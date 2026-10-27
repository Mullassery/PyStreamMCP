from __future__ import annotations

import asyncio
import concurrent.futures
import hashlib
import inspect
import threading
import time
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Optional
from urllib.parse import quote

from .base import (
    BackendCapabilities,
    BackendHealth,
    BackendSearchRequest,
    BackendSearchResult,
    IngestionResult,
)
from .config import RagConfig
from .errors import RetrievalError
from .models import BackendName, RetrievalHit
from .security import (
    check_markdown_image_refs,
    is_loopback_url,
    resolve_ingest_path,
)

_BACKEND = BackendName.RAG_ANYTHING
_RAG_MODES = ("auto", "hybrid", "local", "global", "naive", "mix")
_QMD_ONLY_MODES = {
    "keyword",
    "lex",
    "full_text",
    "semantic",
    "vec",
    "vector",
    "hyde",
}
_PROVIDER_REQUIRED = (
    "llm_model",
    "llm_base_url",
    "llm_api_key",
    "embedding_model",
    "embedding_base_url",
    "embedding_dim",
)


def _as_int(value: Any) -> Optional[int]:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return None


def _display_path(file_path: Any, roots: tuple[Path, ...]) -> str:
    if not isinstance(file_path, str) or not file_path:
        return ""
    raw = file_path.replace("\\", "/")
    if raw.startswith("/"):
        candidate = Path(raw)
        for root in roots:
            try:
                relative = candidate.relative_to(Path(root))
            except ValueError:
                continue
            return PurePosixPath(relative.as_posix()).as_posix()
        raw = raw.lstrip("/")
    while raw.startswith("./"):
        raw = raw[2:]
    parts = [part for part in PurePosixPath(raw).parts if part not in ("", ".")]
    if any(part == ".." for part in parts):
        return ""
    return PurePosixPath(*parts).as_posix()


def _normalized_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.split())


def _status_value(record: Any) -> Optional[str]:
    if isinstance(record, dict):
        status = record.get("status")
    else:
        status = getattr(record, "status", None)
    return status.lower() if isinstance(status, str) else None


class RAGAnythingBackend:
    name = _BACKEND

    def __init__(
        self,
        config: RagConfig,
        engine_factory: Optional[Callable[[], Any]] = None,
    ) -> None:
        self.config = config
        self._engine_factory = engine_factory
        self._engine: Any = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._closed = False
        self._dependency_source: Optional[str] = (
            "injected" if engine_factory is not None else None
        )
        self._dependency_version: Optional[str] = None

    def _provider_configured(self) -> bool:
        provider = self.config.provider
        if provider is None:
            return False
        for field_name in _PROVIDER_REQUIRED:
            value = getattr(provider, field_name, None)
            if value is None or value == "":
                return False
        return True

    def _is_configured(self) -> bool:
        return self._engine_factory is not None or self._provider_configured()

    def _content_types(self) -> tuple[str, ...]:
        content_types = ["text"]
        provider = self.config.provider
        if (
            provider is not None
            and provider.vision_model
            and self.config.enable_image_processing
        ):
            content_types.append("image")
        if self.config.enable_table_processing:
            content_types.append("table")
        if self.config.enable_equation_processing:
            content_types.append("equation")
        return tuple(content_types)

    def _network_egress(self) -> str:
        if self._engine_factory is not None:
            return "unknown"
        provider = self.config.provider
        if provider is None:
            return "unknown"
        urls = [provider.llm_base_url, provider.embedding_base_url]
        if provider.vision_model:
            urls.append(provider.vision_base_url)
        if any(not isinstance(url, str) or not url for url in urls):
            return "unknown"
        if all(is_loopback_url(url) for url in urls):
            return "local"
        return "remote"

    def _unavailable_capabilities(
        self, error: RetrievalError
    ) -> BackendCapabilities:
        return BackendCapabilities(
            backend=_BACKEND,
            enabled=self.config.enabled,
            configured=False,
            available=False,
            modes=_RAG_MODES,
            content_types=self._content_types(),
            max_limit=50,
            supports_ingestion=True,
            supports_full_content=True,
            score_kind="unavailable",
            network_egress=self._network_egress(),
            error=error.to_dict(),
        )

    def capabilities(self) -> BackendCapabilities:
        if self._engine_factory is None:
            try:
                from . import deps

                source = deps.resolve_rag_source(self.config.source_mode)
            except RetrievalError as exc:
                return self._unavailable_capabilities(exc)
            except Exception as exc:
                return self._unavailable_capabilities(
                    RetrievalError(
                        "configuration_error",
                        f"RAG dependency resolution failed: {type(exc).__name__}",
                    )
                )
            self._dependency_source = source.source
            self._dependency_version = source.version
        if not self.config.enabled:
            return self._unavailable_capabilities(
                RetrievalError("not_configured", "RAG-Anything is disabled")
            )
        if not self._is_configured():
            return self._unavailable_capabilities(
                RetrievalError(
                    "not_configured",
                    "Set PYSTREAMMCP_RAG_PROVIDER or inject an engine factory",
                )
            )
        return BackendCapabilities(
            backend=_BACKEND,
            enabled=True,
            configured=True,
            available=True,
            modes=_RAG_MODES,
            content_types=self._content_types(),
            max_limit=50,
            supports_ingestion=True,
            supports_full_content=True,
            score_kind="unavailable",
            network_egress=self._network_egress(),
            error=None,
        )

    def health(self) -> BackendHealth:
        started = time.monotonic()
        if self._closed:
            raise RetrievalError("closed", "RAG backend is closed")
        if self._engine_factory is None:
            try:
                from . import deps

                source = deps.resolve_rag_source(self.config.source_mode)
            except RetrievalError as exc:
                return self._health_result(
                    started, "unavailable", exc.message
                )
            except Exception as exc:
                return self._health_result(
                    started,
                    "unavailable",
                    f"RAG dependency resolution failed: {type(exc).__name__}",
                )
            self._dependency_source = source.source
            self._dependency_version = source.version
        if not self.config.enabled or not self._is_configured():
            return self._health_result(
                started, "unavailable", "RAG-Anything is not configured"
            )
        message = (
            "RAG engine is configured and initialized"
            if self._engine is not None
            else "RAG engine is configured but not initialized"
        )
        return self._health_result(started, "ok", message)

    def _health_result(
        self, started: float, status: str, message: Optional[str]
    ) -> BackendHealth:
        return BackendHealth(
            backend=_BACKEND,
            available=status == "ok",
            status=status,
            message=message,
            elapsed_ms=int(round((time.monotonic() - started) * 1000)),
        )

    def _normalized_mode(self, mode: Optional[str]) -> str:
        if mode is None:
            return self.config.query_mode
        lowered = str(mode).lower()
        if lowered == "auto":
            return self.config.query_mode
        if lowered in _RAG_MODES:
            return lowered
        if lowered in _QMD_ONLY_MODES:
            raise RetrievalError(
                "unsupported_mode",
                f"RAG-Anything does not support mode: {mode}",
                backend=_BACKEND,
            )
        raise RetrievalError(
            "unsupported_mode", f"Unsupported mode: {mode}", backend=_BACKEND
        )

    def _loop_worker(self, loop: asyncio.AbstractEventLoop) -> None:
        asyncio.set_event_loop(loop)
        try:
            loop.run_forever()
        finally:
            pending = asyncio.all_tasks(loop)
            for task in pending:
                task.cancel()
            if pending:
                loop.run_until_complete(
                    asyncio.gather(*pending, return_exceptions=True)
                )
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()

    def _ensure_worker(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        loop = asyncio.new_event_loop()
        thread = threading.Thread(
            target=self._loop_worker,
            args=(loop,),
            name="pystreammcp-rag",
            daemon=True,
        )
        self._loop = loop
        self._thread = thread
        thread.start()

    async def _ensure_engine(self) -> Any:
        if self._engine is not None:
            return self._engine
        if self._engine_factory is not None:
            engine = self._engine_factory()
            if inspect.isawaitable(engine):
                engine = await engine
            self._dependency_source = "injected"
            self._dependency_version = None
        else:
            from . import deps

            source = deps.ensure_rag_import_path(self.config.source_mode)
            self._dependency_source = source.source
            self._dependency_version = source.version
            try:
                from .providers import build_openai_compatible_engine
            except ImportError as exc:
                raise RetrievalError(
                    "missing_dependency",
                    "The RAG provider factory is unavailable",
                ) from exc
            try:
                engine = await build_openai_compatible_engine(self.config)
            except RetrievalError:
                raise
            except ImportError as exc:
                raise RetrievalError(
                    "missing_dependency",
                    "RAG-Anything or LightRAG could not be imported",
                ) from exc
            except Exception as exc:
                raise RetrievalError(
                    "configuration_error",
                    f"RAG engine construction failed: {type(exc).__name__}",
                ) from exc
        self._engine = engine
        return engine

    async def _page_records(
        self, lightrag: Any, chunk_ids: list[str]
    ) -> tuple[dict[str, dict[str, Any]], bool]:
        text_chunks = getattr(lightrag, "text_chunks", None)
        getter = getattr(text_chunks, "get_by_ids", None)
        if not chunk_ids or not callable(getter):
            return {}, False
        try:
            records = getter(chunk_ids)
            if inspect.isawaitable(records):
                records = await records
        except Exception:
            return {}, False
        if isinstance(records, dict):
            return {
                key: value
                for key, value in records.items()
                if isinstance(key, str) and isinstance(value, dict)
            }, True
        if not isinstance(records, list):
            return {}, True
        mapped: dict[str, dict[str, Any]] = {}
        for index, record in enumerate(records):
            if not isinstance(record, dict):
                continue
            key = record.get("chunk_id")
            if not isinstance(key, str) and index < len(chunk_ids):
                key = chunk_ids[index]
            if isinstance(key, str):
                mapped[key] = record
        return mapped, True

    def _map_chunk(
        self,
        chunk: dict[str, Any],
        record: dict[str, Any],
        rank: int,
        request: BackendSearchRequest,
    ) -> tuple[RetrievalHit, bool]:
        display_path = _display_path(chunk.get("file_path"), self.config.allowed_roots)
        source_uri = "rag://" + quote(display_path, safe="/")
        title = (
            PurePosixPath(display_path).stem if display_path else None
        )

        chunk_id = chunk.get("chunk_id")
        reference_id = chunk.get("reference_id")
        page = _as_int(record.get("page_idx"))
        page_end = _as_int(record.get("page_idx_end"))

        document_id = record.get("full_doc_id")
        if not isinstance(document_id, str):
            document_id = chunk.get("full_doc_id")
        if not isinstance(document_id, str):
            document_id = chunk.get("doc_id")
        if not isinstance(document_id, str):
            document_id = None

        locator: dict[str, Any] = {"kind": "chunk"}
        if isinstance(chunk_id, str):
            locator["chunk_id"] = chunk_id
        if isinstance(reference_id, str):
            locator["reference_id"] = reference_id
        if page is not None:
            locator["page"] = page

        metadata: dict[str, Any] = {}
        if isinstance(reference_id, str):
            metadata["reference_id"] = reference_id
        if isinstance(chunk_id, str):
            metadata["chunk_id"] = chunk_id
        if page is not None:
            metadata["page"] = page
        if page_end is not None:
            metadata["page_end"] = page_end

        content_value = chunk.get("content")
        content_text = content_value if isinstance(content_value, str) else ""
        excerpt = _normalized_text(content_text)[:500]
        content: Optional[str] = None
        content_truncated = False
        if request.include_content:
            content = content_text[: request.max_content_chars]
            content_truncated = len(content_text) > request.max_content_chars

        hit = RetrievalHit(
            backend=_BACKEND,
            rank=rank,
            document_id=document_id,
            title=title,
            source_uri=source_uri,
            locator=locator,
            excerpt=excerpt,
            content=content,
            score=None,
            score_kind="unavailable",
            metadata=metadata,
        )
        return hit, content_truncated

    async def _search_async(
        self, request: BackendSearchRequest, mode: str
    ) -> BackendSearchResult:
        engine = await self._ensure_engine()
        lightrag = getattr(engine, "lightrag", None)
        if lightrag is None:
            raise RetrievalError(
                "index_not_initialized",
                "RAG index is not initialized; ingest a document first",
                backend=_BACKEND,
            )
        query_fn = getattr(lightrag, "aquery_data", None)
        if not callable(query_fn):
            raise RetrievalError(
                "upstream_unsupported_version",
                "LightRAG does not expose aquery_data",
                backend=_BACKEND,
            )
        try:
            from lightrag import QueryParam
        except ImportError as exc:
            raise RetrievalError(
                "missing_dependency",
                "LightRAG QueryParam could not be imported",
                backend=_BACKEND,
            ) from exc

        param = QueryParam(
            mode=mode,
            top_k=request.limit,
            chunk_top_k=request.limit,
        )
        try:
            payload = await query_fn(request.query, param)
        except RetrievalError:
            raise
        except Exception as exc:
            raise RetrievalError(
                "query_failed",
                f"RAG query failed: {type(exc).__name__}",
                backend=_BACKEND,
            ) from exc

        if not isinstance(payload, dict) or payload.get("status") != "success":
            raise RetrievalError(
                "invalid_response",
                "LightRAG query did not return a successful response",
                backend=_BACKEND,
            )
        data = payload.get("data")
        if not isinstance(data, dict) or not isinstance(data.get("chunks"), list):
            raise RetrievalError(
                "invalid_response",
                "LightRAG response is missing a chunks list",
                backend=_BACKEND,
            )
        raw_chunks = data["chunks"]
        if any(not isinstance(chunk, dict) for chunk in raw_chunks):
            raise RetrievalError(
                "invalid_response",
                "LightRAG response contains a non-object chunk",
                backend=_BACKEND,
            )

        selected_chunks = raw_chunks[: request.limit]
        chunk_ids = [
            chunk["chunk_id"]
            for chunk in selected_chunks
            if isinstance(chunk.get("chunk_id"), str)
        ]
        records, page_enrichment = await self._page_records(lightrag, chunk_ids)

        hits: list[RetrievalHit] = []
        truncated = len(raw_chunks) > len(selected_chunks)
        for rank, chunk in enumerate(selected_chunks, start=1):
            chunk_id = chunk.get("chunk_id")
            record = records.get(chunk_id, {}) if isinstance(chunk_id, str) else {}
            hit, content_truncated = self._map_chunk(
                chunk, record, rank, request
            )
            hits.append(hit)
            truncated = truncated or content_truncated

        diagnostics: dict[str, Any] = {
            "dependency_source": self._dependency_source,
            "mode": mode,
            "chunk_count": len(raw_chunks),
            "page_enrichment": page_enrichment,
        }
        if self._dependency_version:
            diagnostics["dependency_version"] = self._dependency_version
        metadata = data.get("metadata")
        processing_info = (
            metadata.get("processing_info") if isinstance(metadata, dict) else None
        )
        if isinstance(processing_info, dict):
            numeric = {
                key: value
                for key, value in processing_info.items()
                if isinstance(value, (int, float))
                and not isinstance(value, bool)
            }
            if numeric:
                diagnostics["processing_info"] = numeric

        return BackendSearchResult(
            hits=hits, truncated=truncated, diagnostics=diagnostics
        )

    def _run(
        self,
        factory: Callable[[], Any],
        timeout: float,
        timeout_message: str,
    ) -> Any:
        with self._lock:
            if self._closed:
                raise RetrievalError("closed", "RAG backend is closed")
            self._ensure_worker()
            assert self._loop is not None
            future = asyncio.run_coroutine_threadsafe(
                asyncio.wait_for(factory(), timeout), self._loop
            )
            try:
                return future.result(timeout=timeout + 0.5)
            except (asyncio.TimeoutError, concurrent.futures.TimeoutError) as exc:
                future.cancel()
                raise RetrievalError(
                    "timeout",
                    timeout_message,
                    backend=_BACKEND,
                    retryable=True,
                ) from exc

    def search(self, request: BackendSearchRequest) -> BackendSearchResult:
        if self._closed:
            raise RetrievalError("closed", "RAG backend is closed")
        mode = self._normalized_mode(request.mode)
        timeout = self.config.query_timeout_s
        if request.timeout_s and request.timeout_s > 0:
            timeout = min(timeout, request.timeout_s)
        timeout = max(timeout, 0.001)
        return self._run(
            lambda: self._search_async(request, mode),
            timeout,
            "RAG query exceeded the time budget",
        )

    async def _ingest_async(
        self,
        resolved: Path,
        display_path: str,
        document_id: str,
        force_multimodal: bool,
    ) -> IngestionResult:
        started = time.monotonic()
        engine = await self._ensure_engine()
        lightrag = getattr(engine, "lightrag", None)
        if lightrag is None:
            raise RetrievalError(
                "index_not_initialized",
                "RAG index is not initialized; ingest a document first",
                backend=_BACKEND,
            )
        status_store = getattr(lightrag, "doc_status", None)
        getter = getattr(status_store, "get_by_id", None)

        async def current_status() -> Optional[str]:
            if not callable(getter):
                return None
            try:
                record = getter(document_id)
                if inspect.isawaitable(record):
                    record = await record
            except Exception:
                return None
            return _status_value(record)

        if not force_multimodal:
            status = await current_status()
            if status == "processed":
                return IngestionResult(
                    document_id=document_id,
                    display_path=display_path,
                    status="processed",
                    skipped=True,
                    elapsed_ms=int(
                        round((time.monotonic() - started) * 1000)
                    ),
                    content_types=self._content_types(),
                )

        processor = getattr(engine, "process_document_complete", None)
        if not callable(processor):
            raise RetrievalError(
                "upstream_unsupported_version",
                "RAG engine does not expose process_document_complete",
                backend=_BACKEND,
            )
        try:
            result = processor(
                file_path=str(resolved),
                file_name=display_path,
                doc_id=document_id,
                output_dir=str(self.config.parsed_dir),
                force_multimodal_reprocess=force_multimodal,
                parse_method=self.config.parse_method,
            )
            if inspect.isawaitable(result):
                await result
        except RetrievalError:
            raise
        except Exception as exc:
            raise RetrievalError(
                "ingest_failed",
                f"RAG ingestion failed: {type(exc).__name__}",
                backend=_BACKEND,
            ) from exc

        status = await current_status()
        if status not in {"processed", "partial", "failed"}:
            status = "processed"
        return IngestionResult(
            document_id=document_id,
            display_path=display_path,
            status=status,
            skipped=False,
            elapsed_ms=int(round((time.monotonic() - started) * 1000)),
            content_types=self._content_types(),
        )

    def ingest(
        self, path: str, force_multimodal: bool = False
    ) -> IngestionResult:
        if self._closed:
            raise RetrievalError("closed", "RAG backend is closed")
        if not self.config.enabled:
            raise RetrievalError("not_configured", "RAG-Anything is disabled")
        roots = tuple(self.config.allowed_roots)
        if not roots:
            raise RetrievalError(
                "configuration_error",
                "At least one RAG allowed root is required for ingestion",
            )
        max_bytes = max(0, int(self.config.max_file_mb)) * 1024 * 1024
        resolved, _root, display_path = resolve_ingest_path(
            path,
            roots,
            self.config.allowed_extensions,
            max_bytes,
        )
        if resolved.suffix.lower() in {".md", ".markdown"}:
            check_markdown_image_refs(resolved, roots)
        try:
            payload = resolved.read_bytes()
        except OSError as exc:
            raise RetrievalError("not_a_file", "File cannot be read") from exc
        document_id = "pystreammcp-" + hashlib.sha256(payload).hexdigest()[:32]

        try:
            Path(self.config.working_dir).mkdir(parents=True, exist_ok=True)
            Path(self.config.parsed_dir).mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise RetrievalError(
                "configuration_error",
                "RAG working directories could not be created",
            ) from exc

        timeout = max(self.config.ingest_timeout_s, 0.001)
        return self._run(
            lambda: self._ingest_async(
                resolved, display_path, document_id, force_multimodal
            ),
            timeout,
            "RAG ingestion timed out; upstream may still be running",
        )

    async def _finalize(self) -> None:
        engine = self._engine
        if engine is None:
            return
        lightrag = getattr(engine, "lightrag", None)
        finalizer = getattr(lightrag, "finalize_storages", None)
        if callable(finalizer):
            result = finalizer()
            if inspect.isawaitable(result):
                await result

    def close(self) -> None:
        with self._lock:
            if self._closed:
                return
            self._closed = True
            loop = self._loop
            thread = self._thread
            if loop is not None and loop.is_running():
                try:
                    future = asyncio.run_coroutine_threadsafe(
                        self._finalize(), loop
                    )
                    future.result(timeout=2.0)
                except Exception:
                    pass
                loop.call_soon_threadsafe(loop.stop)
            if thread is not None:
                thread.join(timeout=2.0)
            self._loop = None
            self._thread = None
            self._engine = None
