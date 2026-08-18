"""Discovery types and logic for PyStreamMCP.

`SourceRegistry` is real discovery logic: register data sources (name,
description, type, tags), then find the ones most relevant to a query
context using word-overlap relevance scoring. This is deliberately a
simple, honest heuristic — Jaccard token overlap between the query context
and each source's registered description/tags/name — not a semantic or
embedding-based search. Sources with zero token overlap are excluded from
results rather than padded in with a fabricated score, so an empty
registry or a context that matches nothing returns no sources, not
placeholder data.

`Discovery` / `DiscoveredSource` / `SourceType` are the result types
`SourceRegistry.discover()` returns results as, so callers get real,
structured discovery results rather than a bare dict.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

_WORD_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> Set[str]:
    return set(_WORD_RE.findall(text.lower()))


class SourceType(str, Enum):
    """Type of data source."""

    TABLE = "table"
    INDEX = "index"
    CACHE = "cache"
    EXTERNAL = "external"
    COMPUTED = "computed"
    UNKNOWN = "unknown"


@dataclass
class DiscoveredSource:
    """A discovered data source, returned by SourceRegistry.discover()."""

    name: str
    source_type: SourceType
    relevance_score: float
    estimated_tokens: int
    freshness_score: float = 1.0
    source_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not self.source_id:
            import uuid

            self.source_id = str(uuid.uuid4())
        self.relevance_score = max(0.0, min(1.0, self.relevance_score))
        self.freshness_score = max(0.0, min(1.0, self.freshness_score))

    def quality_score(self) -> float:
        """Combined relevance and freshness score."""
        return self.relevance_score * self.freshness_score

    def with_freshness(self, score: float) -> "DiscoveredSource":
        """Set freshness score."""
        self.freshness_score = max(0.0, min(1.0, score))
        return self


@dataclass
class Discovery:
    """Discovery result for a query."""

    query_id: str
    discovered_sources: List[DiscoveredSource] = field(default_factory=list)
    discovery_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not self.discovery_id:
            import uuid

            self.discovery_id = str(uuid.uuid4())

    def add_source(self, source: DiscoveredSource) -> "Discovery":
        """Add a discovered source."""
        self.discovered_sources.append(source)
        return self

    def total_available_tokens(self) -> int:
        """Total tokens across all sources."""
        return sum(s.estimated_tokens for s in self.discovered_sources)

    def top_sources(self, limit: int = 5) -> List[DiscoveredSource]:
        """Get top sources by quality score."""
        sorted_sources = sorted(
            self.discovered_sources, key=lambda s: s.quality_score(), reverse=True
        )
        return sorted_sources[:limit]

    def high_relevance_sources(self, threshold: float = 0.8) -> List[DiscoveredSource]:
        """Get high-relevance sources."""
        return [s for s in self.discovered_sources if s.relevance_score >= threshold]


@dataclass
class DataSource:
    """A data source registered with a SourceRegistry."""

    name: str
    description: str
    type: str = "unknown"
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    estimated_tokens: int = 0

    def _text(self) -> str:
        return " ".join([self.name, self.description, *self.tags])


class SourceRegistry:
    """In-memory registry of data sources, with real relevance scoring."""

    def __init__(self) -> None:
        self._sources: Dict[str, DataSource] = {}

    def register(
        self,
        name: str,
        description: str,
        type: str = "unknown",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        estimated_tokens: int = 0,
    ) -> DataSource:
        """Register (or replace) a data source by name."""
        source = DataSource(
            name=name,
            description=description,
            type=type,
            tags=list(tags) if tags else [],
            metadata=dict(metadata) if metadata else {},
            estimated_tokens=estimated_tokens,
        )
        self._sources[name] = source
        return source

    def unregister(self, name: str) -> bool:
        """Remove a registered source. Returns True if it existed."""
        return self._sources.pop(name, None) is not None

    def list_sources(self) -> List[DataSource]:
        return list(self._sources.values())

    def discover(self, context: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Return registered sources ranked by real relevance to `context`.

        Relevance is Jaccard token overlap: |context tokens ∩ source
        tokens| / |context tokens ∪ source tokens|. Sources that share no
        tokens with `context` are excluded, not returned with a made-up
        low score. Returns plain dicts (the wire-format shape used by the
        REST/MCP surfaces) — use `discover_typed` for `DiscoveredSource`
        objects.
        """
        return [
            {
                "name": s.name,
                "type": s.type,
                "relevance": round(score, 4),
                "matched_terms": matched,
            }
            for score, matched, s in self._score(context, limit)
        ]

    def discover_typed(self, query_id: str, context: str, limit: int = 10) -> Discovery:
        """Same ranking as `discover`, returned as a `Discovery` result of
        real `DiscoveredSource` objects instead of plain dicts."""
        result = Discovery(query_id=query_id)
        for score, _matched, s in self._score(context, limit):
            try:
                source_type = SourceType(s.type)
            except ValueError:
                source_type = SourceType.UNKNOWN
            result.add_source(
                DiscoveredSource(
                    name=s.name,
                    source_type=source_type,
                    relevance_score=score,
                    estimated_tokens=s.estimated_tokens,
                )
            )
        return result

    def _score(self, context: str, limit: int):
        context_tokens = _tokenize(context)
        if not context_tokens or not self._sources:
            return []

        scored = []
        for source in self._sources.values():
            source_tokens = _tokenize(source._text())
            if not source_tokens:
                continue
            overlap = context_tokens & source_tokens
            if not overlap:
                continue
            union = context_tokens | source_tokens
            relevance = len(overlap) / len(union)
            scored.append((relevance, sorted(overlap), source))

        scored.sort(key=lambda item: item[0], reverse=True)
        return scored[:limit]
