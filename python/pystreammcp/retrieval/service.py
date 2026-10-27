from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, wait
from dataclasses import replace
from typing import Any, Iterable, Mapping, Optional

from .base import (
    BackendCapabilities,
    BackendHealth,
    BackendSearchRequest,
    IngestionResult,
)
from .config import RetrievalConfig
from .errors import RetrievalError
from .models import (
    BackendGroup,
    BackendName,
    RequestedBackend,
    RetrievalRequest,
    RetrievalResponse,
)
from .router import route

_UNAVAILABLE_CODES = {
    "unavailable",
    "not_configured",
    "missing_dependency",
    "configuration_error",
}
_KNOWN_MODES = {
    "auto",
    "hybrid",
    "keyword",
    "lex",
    "full_text",
    "semantic",
    "vec",
    "vector",
    "hyde",
    "local",
    "global",
    "naive",
    "mix",
}
_KNOWN_CONTENT_TYPES = {
    "text",
    "image",
    "table",
    "equation",
    "document",
    "pdf",
    "audio",
    "video",
}


class UnavailableBackend:
    def __init__(self, name: BackendName, error: RetrievalError) -> None:
        self.name = BackendName(name)
        self.error = error

    def capabilities(self) -> BackendCapabilities:
        return BackendCapabilities(
            backend=self.name,
            enabled=True,
            configured=False,
            available=False,
            modes=(),
            content_types=(),
            max_limit=50,
            supports_ingestion=self.name is BackendName.RAG_ANYTHING,
            supports_full_content=self.name is BackendName.RAG_ANYTHING,
            score_kind="unavailable",
            network_egress="unknown",
            error=self.error.to_dict(),
        )

    def health(self) -> BackendHealth:
        return BackendHealth(
            backend=self.name,
            available=False,
            status="unavailable",
            message=self.error.message,
            elapsed_ms=0,
        )

    def search(self, request: BackendSearchRequest):
        raise self.error

    def ingest(self, path: str, force_multimodal: bool = False) -> IngestionResult:
        raise self.error

    def close(self) -> None:
        return None


class RetrievalService:
    def __init__(
        self,
        backends: Iterable[Any],
        priority: tuple[BackendName, ...] = (
            BackendName.QMD,
            BackendName.RAG_ANYTHING,
        ),
        max_workers: int = 4,
    ) -> None:
        self._backends = list(backends)
        self._registry: dict[BackendName, Any] = {}
        for backend in self._backends:
            self._registry[BackendName(backend.name)] = backend
        self._priority = tuple(priority)
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers, thread_name_prefix="retrieval"
        )
        self._closed = False

    @classmethod
    def from_env(cls, env: Optional[Mapping[str, str]] = None) -> "RetrievalService":
        config = RetrievalConfig.from_env(env)
        backends: list[Any] = []

        if config.qmd_requested:
            if config.qmd_error:
                backends.append(
                    UnavailableBackend(
                        BackendName.QMD,
                        RetrievalError("configuration_error", config.qmd_error),
                    )
                )
            else:
                try:
                    from .qmd import QmdBackend

                    backends.append(QmdBackend(config.qmd))
                except Exception as exc:
                    backends.append(
                        UnavailableBackend(
                            BackendName.QMD,
                            RetrievalError(
                                "configuration_error",
                                f"QMD backend could not be created: {type(exc).__name__}",
                            ),
                        )
                    )

        if config.rag_requested:
            if config.rag_error:
                backends.append(
                    UnavailableBackend(
                        BackendName.RAG_ANYTHING,
                        RetrievalError("configuration_error", config.rag_error),
                    )
                )
            else:
                try:
                    from .rag_anything import RAGAnythingBackend

                    backends.append(RAGAnythingBackend(config.rag))
                except Exception as exc:
                    backends.append(
                        UnavailableBackend(
                            BackendName.RAG_ANYTHING,
                            RetrievalError(
                                "configuration_error",
                                "RAG backend could not be created: "
                                f"{type(exc).__name__}",
                            ),
                        )
                    )
        return cls(backends)

    def _validate(self, request: RetrievalRequest) -> RetrievalRequest:
        if self._closed:
            raise RetrievalError("closed", "Retrieval service is closed")

        query = request.query if isinstance(request.query, str) else ""
        if not query.strip() or len(query) > 8000:
            raise RetrievalError(
                "invalid_request", "Query must be between 1 and 8000 characters"
            )
        if not isinstance(request.limit, int) or not 1 <= request.limit <= 50:
            raise RetrievalError("invalid_request", "Limit must be between 1 and 50")
        if (
            not isinstance(request.max_content_chars, int)
            or not 0 <= request.max_content_chars <= 20000
        ):
            raise RetrievalError(
                "invalid_request",
                "max_content_chars must be between 0 and 20000",
            )
        if (
            not isinstance(request.time_budget_ms, int)
            or not 1 <= request.time_budget_ms <= 300000
        ):
            raise RetrievalError(
                "invalid_request",
                "time_budget_ms must be between 1 and 300000",
            )
        if len(request.collections) > 32:
            raise RetrievalError(
                "invalid_request", "At most 32 collections may be requested"
            )
        if request.intent is not None and len(request.intent) > 1000:
            raise RetrievalError(
                "invalid_request", "Intent must be at most 1000 characters"
            )

        try:
            backend = RequestedBackend(request.backend)
        except ValueError as exc:
            raise RetrievalError(
                "invalid_backend", f"Unknown backend: {request.backend}"
            ) from exc
        if request.mode is not None and request.mode not in _KNOWN_MODES:
            raise RetrievalError(
                "unsupported_mode", f"Unsupported mode: {request.mode}"
            )
        content_type = (
            request.content_type.lower()
            if isinstance(request.content_type, str)
            else request.content_type
        )
        if content_type is not None and content_type not in _KNOWN_CONTENT_TYPES:
            raise RetrievalError(
                "unsupported_content_type",
                f"Unsupported content type: {request.content_type}",
            )
        return replace(
            request,
            backend=backend,
            content_type=content_type,
            collections=tuple(request.collections),
        )

    def _backend_request(
        self, request: RetrievalRequest
    ) -> BackendSearchRequest:
        return BackendSearchRequest(
            query=request.query,
            mode=request.mode,
            collections=tuple(request.collections),
            content_type=request.content_type,
            limit=request.limit,
            include_content=request.include_content,
            max_content_chars=request.max_content_chars,
            timeout_s=request.time_budget_ms / 1000.0,
            intent=request.intent,
        )

    def _run_backend(
        self,
        name: BackendName,
        backend: Any,
        request: BackendSearchRequest,
    ) -> BackendGroup:
        started = time.monotonic()
        try:
            result = backend.search(request)
        except RetrievalError as exc:
            status = (
                "unavailable" if exc.code in _UNAVAILABLE_CODES else "error"
            )
            return BackendGroup(
                backend=name,
                status=status,
                hits=[],
                error=exc.to_dict(),
                elapsed_ms=int(round((time.monotonic() - started) * 1000)),
                truncated=False,
            )
        except Exception as exc:
            error = RetrievalError(
                "query_failed",
                f"Unexpected backend failure: {type(exc).__name__}",
                backend=name,
            )
            return BackendGroup(
                backend=name,
                status="error",
                hits=[],
                error=error.to_dict(),
                elapsed_ms=int(round((time.monotonic() - started) * 1000)),
                truncated=False,
            )
        return BackendGroup(
            backend=name,
            status="ok",
            hits=result.hits,
            error=None,
            elapsed_ms=int(round((time.monotonic() - started) * 1000)),
            truncated=result.truncated,
        )

    def search(self, request: RetrievalRequest) -> RetrievalResponse:
        request = self._validate(request)
        decision = route(request, self._registry, self._priority)
        backend_request = self._backend_request(request)
        futures = {
            name: self._executor.submit(
                self._run_backend,
                name,
                self._registry[name],
                backend_request,
            )
            for name in decision.backends
        }
        done, pending = wait(
            futures.values(), timeout=request.time_budget_ms / 1000.0
        )
        groups_by_name: dict[BackendName, BackendGroup] = {}
        for name, future in futures.items():
            if future in done:
                try:
                    groups_by_name[name] = future.result()
                except Exception as exc:
                    error = RetrievalError(
                        "query_failed",
                        f"Unexpected backend failure: {type(exc).__name__}",
                        backend=name,
                    )
                    groups_by_name[name] = BackendGroup(
                        backend=name,
                        status="error",
                        hits=[],
                        error=error.to_dict(),
                        elapsed_ms=0,
                        truncated=False,
                    )
            else:
                future.cancel()
                error = RetrievalError(
                    "timeout",
                    "Backend did not finish within the time budget",
                    backend=name,
                )
                groups_by_name[name] = BackendGroup(
                    backend=name,
                    status="timeout",
                    hits=[],
                    error=error.to_dict(),
                    elapsed_ms=request.time_budget_ms,
                    truncated=False,
                )
        groups = [groups_by_name[name] for name in decision.backends]
        if all(group.status == "ok" for group in groups):
            status = "success"
        elif any(group.status == "ok" for group in groups):
            status = "partial"
        else:
            status = "error"
        diagnostics = dict(decision.diagnostics)
        return RetrievalResponse(
            status=status,
            query=request.query,
            backend_requested=request.backend.value,
            groups=groups,
            diagnostics=diagnostics,
        )

    def capabilities(self, include_health: bool = True) -> dict[str, Any]:
        if self._closed:
            raise RetrievalError("closed", "Retrieval service is closed")
        entries = []
        for backend in self._backends:
            try:
                entry = backend.capabilities().to_dict()
            except Exception as exc:
                error = RetrievalError(
                    "configuration_error",
                    f"Capabilities failed: {type(exc).__name__}",
                    backend=getattr(backend, "name", None),
                )
                entry = UnavailableBackend(
                    BackendName(getattr(backend, "name", BackendName.QMD)), error
                ).capabilities().to_dict()
            if include_health:
                try:
                    entry["health"] = backend.health().to_dict()
                except Exception as exc:
                    entry["health"] = BackendHealth(
                        backend=BackendName(getattr(backend, "name", BackendName.QMD)),
                        available=False,
                        status="error",
                        message=f"Health check failed: {type(exc).__name__}",
                        elapsed_ms=0,
                    ).to_dict()
            entries.append(entry)
        return {"backends": entries}

    def health(self) -> dict[str, Any]:
        if self._closed:
            raise RetrievalError("closed", "Retrieval service is closed")
        entries = []
        for backend in self._backends:
            name = BackendName(getattr(backend, "name", BackendName.QMD))
            try:
                entries.append(backend.health().to_dict())
            except Exception as exc:
                entries.append(
                    BackendHealth(
                        backend=name,
                        available=False,
                        status="error",
                        message=f"Health check failed: {type(exc).__name__}",
                        elapsed_ms=0,
                    ).to_dict()
                )
        return {"backends": entries}

    def ingest(
        self, path: str, force_multimodal: bool = False
    ) -> IngestionResult:
        if self._closed:
            raise RetrievalError("closed", "Retrieval service is closed")
        rag_backends = [
            backend
            for backend in self._backends
            if BackendName(backend.name) is BackendName.RAG_ANYTHING
        ]
        if not rag_backends:
            raise RetrievalError(
                "not_configured", "RAG-Anything is not registered"
            )
        if len(rag_backends) > 1:
            raise RetrievalError(
                "configuration_error", "Multiple RAG backends are registered"
            )
        backend = rag_backends[0]
        if not hasattr(backend, "ingest"):
            raise RetrievalError(
                "configuration_error", "RAG backend does not support ingestion"
            )
        return backend.ingest(path, force_multimodal=force_multimodal)

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        for backend in self._backends:
            try:
                backend.close()
            except Exception:
                pass
        self._executor.shutdown(wait=True, cancel_futures=True)
