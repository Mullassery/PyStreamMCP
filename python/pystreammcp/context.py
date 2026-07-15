"""Context types for PyStreamMCP."""

from typing import Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime


class ContextType(str, Enum):
    """Type of context."""
    ENTITY_DATA = "entity_data"
    RELATIONSHIP = "relationship"
    METRIC = "metric"
    HISTORICAL = "historical"
    SIMILAR = "similar"
    CONTEXTUAL = "contextual"


@dataclass
class Context:
    """Context information for queries."""
    context_type: ContextType
    content: Dict[str, Any]
    source: str
    relevance_score: float = 1.0
    token_count: int = 0
    context_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not self.context_id:
            import uuid
            self.context_id = str(uuid.uuid4())
        if self.token_count == 0:
            # Rough estimation: ~1 token per 4 chars
            import json
            serialized = json.dumps(self.content)
            self.token_count = len(serialized) // 4

    def with_relevance(self, score: float) -> "Context":
        """Set relevance score."""
        self.relevance_score = max(0.0, min(1.0, score))
        return self


@dataclass
class ContextWindow:
    """Window of contexts for a query."""
    query_id: str
    contexts: List[Context] = field(default_factory=list)
    token_budget: int = 2000
    total_tokens: int = 0

    def add_context(self, context: Context) -> bool:
        """Try to add context within budget."""
        if self.total_tokens + context.token_count > self.token_budget:
            return False
        self.contexts.append(context)
        self.total_tokens += context.token_count
        return True

    def utilization_percent(self) -> float:
        """Get token utilization percentage."""
        if self.token_budget == 0:
            return 0.0
        return (self.total_tokens / self.token_budget) * 100

    def remaining_tokens(self) -> int:
        """Get remaining token budget."""
        return max(0, self.token_budget - self.total_tokens)

    def is_full(self) -> bool:
        """Check if window is full."""
        return self.total_tokens >= self.token_budget
