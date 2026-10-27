from __future__ import annotations

from typing import Any, Optional

from .models import _to_plain

ERROR_CODES = (
    "configuration_error",
    "not_configured",
    "unavailable",
    "missing_dependency",
    "invalid_request",
    "invalid_backend",
    "unsupported_mode",
    "unsupported_content_type",
    "collection_not_allowed",
    "collection_required",
    "timeout",
    "http_error",
    "invalid_response",
    "path_outside_allowed_roots",
    "symlink_not_allowed",
    "unsupported_extension",
    "file_too_large",
    "not_a_file",
    "ingest_failed",
    "index_not_initialized",
    "query_failed",
    "upstream_unsupported_version",
    "no_available_backend",
    "closed",
)


class RetrievalError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        backend: Any = None,
        retryable: bool = False,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        self.code = code
        self.message = str(message)[:500]
        self.backend = backend
        self.retryable = bool(retryable)
        self.details = details if details is not None else {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "backend": _to_plain(self.backend),
            "retryable": self.retryable,
            "details": _to_plain(self.details),
        }
