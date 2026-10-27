from __future__ import annotations

import math
import time
from typing import Any, Optional

import httpx

from .base import (
    BackendCapabilities,
    BackendHealth,
    BackendSearchRequest,
    BackendSearchResult,
)
from .config import QmdConfig
from .errors import RetrievalError
from .models import BackendName, RetrievalHit
from .security import is_loopback_url, redact_text, validate_qmd_url

_BACKEND = BackendName.QMD
_MODES = (
    "auto",
    "hybrid",
    "keyword",
    "lex",
    "full_text",
    "semantic",
    "vec",
    "vector",
    "hyde",
)
_MODE_TABLE = {
    None: (("lex", "vec"), True),
    "auto": (("lex", "vec"), True),
    "hybrid": (("lex", "vec"), True),
    "keyword": (("lex",), False),
    "lex": (("lex",), False),
    "full_text": (("lex",), False),
    "semantic": (("vec",), False),
    "vec": (("vec",), False),
    "vector": (("vec",), False),
    "hyde": (("hyde",), False),
}
_SECRET_WORDS = ("token", "secret", "password", "credential", "authorization")
_MAX_METADATA_KEYS = 20
_MAX_METADATA_STRING = 200
_MAX_METADATA_LIST = 20


def _bounded_scalar(value: Any) -> Any:
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, str):
        return value[:_MAX_METADATA_STRING]
    return None


def _bounded_metadata(value: Any) -> Any:
    if isinstance(value, (dict, tuple)):
        return None
    if isinstance(value, list):
        return [
            item
            for item in (
                _bounded_scalar(entry) for entry in value[:_MAX_METADATA_LIST]
            )
            if not isinstance(item, (dict, list))
        ]
    scalar = _bounded_scalar(value)
    if scalar is None and value is not None:
        return None
    return scalar


def _metadata_key_allowed(key: str) -> bool:
    lowered = key.lower()
    if lowered.endswith("key"):
        return False
    return not any(word in lowered for word in _SECRET_WORDS)


def _error_body(response: httpx.Response) -> str:
    try:
        text = response.text
    except Exception:
        text = ""
    return redact_text(text[:300])


class QmdBackend:
    name = _BACKEND

    def __init__(
        self,
        config: QmdConfig,
        transport: Optional[httpx.BaseTransport] = None,
    ) -> None:
        self.config = config
        validate_qmd_url(config.url, config.allow_remote)
        self._client = httpx.Client(
            base_url=config.url.rstrip("/"),
            timeout=config.timeout_s,
            trust_env=config.trust_env,
            transport=transport,
        )

    def capabilities(self) -> BackendCapabilities:
        return BackendCapabilities(
            backend=_BACKEND,
            enabled=self.config.enabled,
            configured=True,
            available=self.config.enabled,
            modes=_MODES,
            content_types=("text",),
            max_limit=50,
            supports_ingestion=False,
            supports_full_content=False,
            score_kind="qmd_query_relevance",
            network_egress="local" if is_loopback_url(self.config.url) else "remote",
            error=None,
        )

    def health(self) -> BackendHealth:
        started = time.monotonic()
        try:
            response = self._client.get(
                "/health", timeout=self.config.health_timeout_s
            )
        except httpx.TimeoutException:
            return self._health_result(
                started, "unavailable", "QMD health check timed out"
            )
        except httpx.RequestError as exc:
            return self._health_result(
                started,
                "unavailable",
                f"QMD health check failed: {type(exc).__name__}",
            )
        except Exception as exc:
            return self._health_result(
                started, "error", f"QMD health check error: {type(exc).__name__}"
            )
        if response.status_code == 200:
            return self._health_result(started, "ok", None)
        return self._health_result(
            started,
            "unavailable",
            f"QMD health returned HTTP {response.status_code}",
        )

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

    def _selected_collections(self, request: BackendSearchRequest) -> list[str]:
        configured = list(self.config.collections)
        if not request.collections:
            return configured
        requested = list(request.collections)
        allowed = set(configured)
        for collection in requested:
            if collection not in allowed:
                raise RetrievalError(
                    "collection_not_allowed",
                    f"Collection is not allowed: {collection}",
                    backend=_BACKEND,
                )
        return requested

    def _payload(
        self, request: BackendSearchRequest, collections: list[str]
    ) -> dict[str, Any]:
        mode = request.mode.lower() if isinstance(request.mode, str) else request.mode
        if mode not in _MODE_TABLE:
            raise RetrievalError(
                "unsupported_mode",
                f"Unsupported QMD mode: {request.mode}",
                backend=_BACKEND,
            )
        if request.content_type is not None and request.content_type.lower() != "text":
            raise RetrievalError(
                "unsupported_content_type",
                "QMD only supports text content",
                backend=_BACKEND,
            )
        search_types, rerank = _MODE_TABLE[mode]
        payload: dict[str, Any] = {
            "searches": [
                {"type": search_type, "query": request.query}
                for search_type in search_types
            ],
            "collections": collections,
            "limit": request.limit,
            "rerank": rerank,
        }
        if request.intent is not None:
            payload["intent"] = request.intent
        return payload

    def _map_hit(
        self,
        item: dict[str, Any],
        rank: int,
        collections: list[str],
        request: BackendSearchRequest,
    ) -> tuple[RetrievalHit, bool]:
        docid = item.get("docid")
        document_id = docid if isinstance(docid, str) else None
        file_value = item.get("file")
        file_name = file_value if isinstance(file_value, str) else ""
        collection = collections[0] if collections else ""
        upstream_metadata = item.get("metadata")
        if isinstance(upstream_metadata, dict):
            candidate = upstream_metadata.get("collection")
            if isinstance(candidate, str) and candidate in collections:
                collection = candidate
        if file_name.startswith("qmd://"):
            source_uri = file_name
        else:
            source_uri = f"qmd://{collection}/{file_name.lstrip('/')}"

        line_value = item.get("line")
        line = (
            line_value
            if isinstance(line_value, int) and not isinstance(line_value, bool)
            else None
        )
        locator: dict[str, Any] = {"kind": "line"}
        if line is not None:
            locator["line"] = line

        title_value = item.get("title")
        if isinstance(title_value, str):
            title = title_value
        elif file_name:
            title = file_name.rstrip("/").rsplit("/", 1)[-1]
        else:
            title = document_id

        snippet_value = item.get("snippet")
        snippet = snippet_value if isinstance(snippet_value, str) else ""
        excerpt = snippet
        content: Optional[str] = None
        content_truncated = False
        if request.include_content:
            content = snippet[: request.max_content_chars]
            content_truncated = len(snippet) > request.max_content_chars

        score_value = item.get("score")
        score = (
            float(score_value)
            if isinstance(score_value, (int, float))
            and not isinstance(score_value, bool)
            and math.isfinite(float(score_value))
            else None
        )

        metadata: dict[str, Any] = {}
        if isinstance(upstream_metadata, dict):
            for key, value in list(upstream_metadata.items())[:_MAX_METADATA_KEYS]:
                if not isinstance(key, str) or not _metadata_key_allowed(key):
                    continue
                bounded = _bounded_metadata(value)
                if bounded is not None:
                    metadata[key] = bounded
        if document_id is not None:
            metadata["docid"] = document_id
        context = item.get("context")
        if isinstance(context, str):
            metadata["context"] = context[:_MAX_METADATA_STRING]
        if line is not None:
            metadata["line"] = line

        hit = RetrievalHit(
            backend=_BACKEND,
            rank=rank,
            document_id=document_id,
            title=title,
            source_uri=source_uri,
            locator=locator,
            excerpt=excerpt,
            content=content,
            score=score,
            score_kind="qmd_query_relevance",
            metadata=metadata,
        )
        return hit, content_truncated

    def search(self, request: BackendSearchRequest) -> BackendSearchResult:
        if not request.query.strip():
            raise RetrievalError(
                "invalid_request", "Query must not be empty", backend=_BACKEND
            )
        collections = self._selected_collections(request)
        payload = self._payload(request, collections)
        timeout = min(self.config.timeout_s, request.timeout_s)
        try:
            response = self._client.post("/query", json=payload, timeout=timeout)
        except httpx.TimeoutException as exc:
            raise RetrievalError(
                "timeout", "QMD query timed out", backend=_BACKEND, retryable=True
            ) from exc
        except httpx.RequestError as exc:
            raise RetrievalError(
                "unavailable",
                f"QMD query failed: {type(exc).__name__}",
                backend=_BACKEND,
                retryable=True,
            ) from exc

        if response.status_code == 400:
            raise RetrievalError(
                "http_error",
                f"QMD rejected the query: {_error_body(response)}",
                backend=_BACKEND,
                details={"status_code": 400},
            )
        if response.status_code in {403, 404} or response.status_code >= 500:
            raise RetrievalError(
                "unavailable",
                f"QMD query returned HTTP {response.status_code}",
                backend=_BACKEND,
                retryable=True,
                details={"status_code": response.status_code},
            )
        if response.status_code != 200:
            raise RetrievalError(
                "http_error",
                f"QMD query returned HTTP {response.status_code}",
                backend=_BACKEND,
                details={"status_code": response.status_code},
            )

        try:
            decoded = response.json()
        except ValueError as exc:
            raise RetrievalError(
                "invalid_response",
                "QMD returned invalid JSON",
                backend=_BACKEND,
            ) from exc
        if not isinstance(decoded, dict) or not isinstance(
            decoded.get("results"), list
        ):
            raise RetrievalError(
                "invalid_response",
                "QMD response is missing a results list",
                backend=_BACKEND,
            )
        raw_results = decoded["results"]
        if any(not isinstance(item, dict) for item in raw_results):
            raise RetrievalError(
                "invalid_response",
                "QMD response contains a non-object result",
                backend=_BACKEND,
            )

        selected = raw_results[: request.limit]
        hits: list[RetrievalHit] = []
        truncated = len(raw_results) > len(selected)
        for rank, item in enumerate(selected, start=1):
            hit, content_truncated = self._map_hit(
                item, rank, collections, request
            )
            hits.append(hit)
            truncated = truncated or content_truncated

        return BackendSearchResult(
            hits=hits,
            truncated=truncated,
            diagnostics={
                "result_count": len(hits),
                "upstream_count": len(raw_results),
            },
        )

    def close(self) -> None:
        self._client.close()
