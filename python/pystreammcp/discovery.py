"""Discovery types for PyStreamMCP."""

from typing import Optional, List
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime


class SourceType(str, Enum):
    """Type of data source."""
    TABLE = "table"
    INDEX = "index"
    CACHE = "cache"
    EXTERNAL = "external"
    COMPUTED = "computed"


@dataclass
class DiscoveredSource:
    """A discovered data source."""
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
            self.discovered_sources,
            key=lambda s: s.quality_score(),
            reverse=True
        )
        return sorted_sources[:limit]

    def high_relevance_sources(self, threshold: float = 0.8) -> List[DiscoveredSource]:
        """Get high-relevance sources."""
        return [s for s in self.discovered_sources if s.relevance_score >= threshold]
