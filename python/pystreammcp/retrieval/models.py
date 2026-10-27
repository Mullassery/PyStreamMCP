from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from enum import Enum
from typing import Any, Optional


def _to_plain(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        result: dict[str, Any] = {}
        for field in fields(value):
            field_value = getattr(value, field.name)
            if field.name == "content" and field_value is None:
                continue
            result[field.name] = _to_plain(field_value)
        return result
    if isinstance(value, dict):
        return {key: _to_plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_plain(item) for item in value]
    return value


class BackendName(str, Enum):
    QMD = "qmd"
    RAG_ANYTHING = "rag_anything"


class RequestedBackend(str, Enum):
    AUTO = "auto"
    QMD = "qmd"
    RAG_ANYTHING = "rag_anything"
    ALL = "all"


@dataclass(frozen=True)
class RetrievalRequest:
    query: str
    backend: RequestedBackend = RequestedBackend.AUTO
    mode: Optional[str] = None
    collections: tuple[str, ...] = ()
    content_type: Optional[str] = None
    limit: int = 5
    include_content: bool = False
    max_content_chars: int = 2000
    time_budget_ms: int = 30000
    intent: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return _to_plain(self)


@dataclass(frozen=True)
class RetrievalHit:
    backend: BackendName
    rank: int
    document_id: Optional[str]
    title: Optional[str]
    source_uri: str
    locator: dict[str, Any]
    excerpt: str
    content: Optional[str]
    score: Optional[float]
    score_kind: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return _to_plain(self)


@dataclass
class BackendGroup:
    backend: BackendName
    status: str
    hits: list[RetrievalHit]
    error: Optional[dict[str, Any]]
    elapsed_ms: int
    truncated: bool

    def to_dict(self) -> dict[str, Any]:
        return _to_plain(self)


@dataclass
class RetrievalResponse:
    status: str
    query: str
    backend_requested: str
    groups: list[BackendGroup]
    diagnostics: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return _to_plain(self)
