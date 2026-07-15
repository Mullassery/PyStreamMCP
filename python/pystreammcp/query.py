"""Query types and utilities for PyStreamMCP."""

from typing import Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime


class QueryIntent(str, Enum):
    """Type of query intent."""
    RETRIEVE = "retrieve"      # Get specific information
    DISCOVER = "discover"      # Explore available data
    AGGREGATE = "aggregate"    # Summarize multiple sources
    SYNTHESIZE = "synthesize"  # Combine information
    ANALYZE = "analyze"        # Statistical analysis


@dataclass
class QueryConstraints:
    """Constraints for query execution."""
    max_tokens: Optional[int] = 2000
    max_latency_ms: Optional[int] = 5000
    min_confidence: Optional[float] = None
    max_staleness_seconds: Optional[int] = 3600

    def token_efficient(self) -> "QueryConstraints":
        """Set token-efficient constraints."""
        self.max_tokens = 500
        self.min_confidence = 0.85
        return self


@dataclass
class Query:
    """A query for PyStreamMCP."""
    text: str
    agent_id: str
    intent: QueryIntent = QueryIntent.RETRIEVE
    constraints: QueryConstraints = field(default_factory=QueryConstraints)
    metadata: Dict[str, Any] = field(default_factory=dict)
    query_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not self.query_id:
            import uuid
            self.query_id = str(uuid.uuid4())

    @staticmethod
    def retrieve(text: str, agent_id: str, max_tokens: Optional[int] = None) -> "Query":
        """Create a retrieval query."""
        constraints = QueryConstraints(max_tokens=max_tokens) if max_tokens else QueryConstraints()
        return Query(text=text, agent_id=agent_id, intent=QueryIntent.RETRIEVE, constraints=constraints)

    @staticmethod
    def discover(text: str, agent_id: str, max_tokens: Optional[int] = None) -> "Query":
        """Create a discovery query."""
        constraints = QueryConstraints(max_tokens=max_tokens) if max_tokens else QueryConstraints()
        return Query(text=text, agent_id=agent_id, intent=QueryIntent.DISCOVER, constraints=constraints)

    @staticmethod
    def aggregate(text: str, agent_id: str, max_tokens: Optional[int] = None) -> "Query":
        """Create an aggregation query."""
        constraints = QueryConstraints(max_tokens=max_tokens) if max_tokens else QueryConstraints()
        return Query(text=text, agent_id=agent_id, intent=QueryIntent.AGGREGATE, constraints=constraints)

    def set_token_efficient(self) -> "Query":
        """Make this query token-efficient."""
        self.constraints.token_efficient()
        return self

    def with_intent(self, intent: QueryIntent) -> "Query":
        """Set query intent."""
        self.intent = intent
        return self

    def with_max_tokens(self, tokens: int) -> "Query":
        """Set max token budget."""
        self.constraints.max_tokens = tokens
        return self

    def with_metadata(self, key: str, value: Any) -> "Query":
        """Add metadata."""
        self.metadata[key] = value
        return self
