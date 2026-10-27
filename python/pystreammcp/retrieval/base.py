from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Protocol, runtime_checkable

from .models import BackendName, RetrievalHit, _to_plain


@dataclass(frozen=True)
class BackendSearchRequest:
    query: str
    mode: Optional[str]
    collections: tuple[str, ...]
    content_type: Optional[str]
    limit: int
    include_content: bool
    max_content_chars: int
    timeout_s: float
    intent: Optional[str]

    def to_dict(self) -> dict[str, Any]:
        return _to_plain(self)


@dataclass
class BackendSearchResult:
    hits: list[RetrievalHit]
    truncated: bool
    diagnostics: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return _to_plain(self)


@dataclass(frozen=True)
class BackendCapabilities:
    backend: BackendName
    enabled: bool
    configured: bool
    available: bool
    modes: tuple[str, ...]
    content_types: tuple[str, ...]
    max_limit: int
    supports_ingestion: bool
    supports_full_content: bool
    score_kind: str
    network_egress: str
    error: Optional[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return _to_plain(self)


@dataclass(frozen=True)
class BackendHealth:
    backend: BackendName
    available: bool
    status: str
    message: Optional[str]
    elapsed_ms: int

    def to_dict(self) -> dict[str, Any]:
        return _to_plain(self)


@dataclass(frozen=True)
class IngestionResult:
    document_id: str
    display_path: str
    status: str
    skipped: bool
    elapsed_ms: int
    content_types: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return _to_plain(self)


@runtime_checkable
class RetrievalBackend(Protocol):
    name: BackendName

    def capabilities(self) -> BackendCapabilities: ...

    def health(self) -> BackendHealth: ...

    def search(self, request: BackendSearchRequest) -> BackendSearchResult: ...

    def close(self) -> None: ...


@runtime_checkable
class IngestingBackend(RetrievalBackend, Protocol):
    def ingest(self, path: str, force_multimodal: bool = False) -> IngestionResult: ...
