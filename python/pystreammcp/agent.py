"""
Agent - High-level interface for AI agent integration.

Provides a simple API for agents to query with automatic
optimization, discovery, and cost tracking.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AgentConfig:
    """Configuration for an agent."""
    agent_id: str
    name: str
    optimization_strategy: str = "balanced"
    max_tokens: int = 2000
    enable_caching: bool = True
    enable_discovery: bool = True


class Agent:
    """AI Agent with PyStreamMCP intelligence optimization."""

    def __init__(self, agent_id: str, name: Optional[str] = None, **kwargs):
        """
        Initialize an agent with PyStreamMCP integration.

        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name (defaults to agent_id)
            optimization_strategy: How to optimize (balanced, token_efficient, quality_first)
            max_tokens: Token budget for queries
            enable_caching: Use caching when available
            enable_discovery: Discover relevant context automatically
        """
        self.config = AgentConfig(
            agent_id=agent_id,
            name=name or agent_id,
            optimization_strategy=kwargs.get("optimization_strategy", "balanced"),
            max_tokens=kwargs.get("max_tokens", 2000),
            enable_caching=kwargs.get("enable_caching", True),
            enable_discovery=kwargs.get("enable_discovery", True),
        )
        self.metrics: Dict[str, Any] = {
            "queries_executed": 0,
            "total_baseline_tokens": 0,
            "total_optimized_tokens": 0,
            "total_cost_saved": 0.0,
        }

    def query(
        self,
        text: str,
        optimization: Optional[str] = None,
        max_tokens: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "QueryResult":
        """
        Execute a query with automatic optimization.

        Args:
            text: The query text
            optimization: Override optimization strategy
            max_tokens: Override token budget
            metadata: Additional metadata for the query

        Returns:
            QueryResult with optimized context
        """
        strategy = optimization or self.config.optimization_strategy
        tokens = max_tokens or self.config.max_tokens

        # Placeholder for actual Rust core integration
        result = QueryResult(
            query_id=f"query_{self.config.agent_id}_{datetime.now().timestamp()}",
            query_text=text,
            baseline_tokens=tokens,
            optimized_tokens=max(int(tokens * 0.3), 500),  # Simulate 70% reduction
            cost_reduction_percent=70.0,
            contexts=[],
            optimization_applied=[],
            execution_time_ms=50,
        )

        # Update metrics
        self.metrics["queries_executed"] += 1
        self.metrics["total_baseline_tokens"] += result.baseline_tokens
        self.metrics["total_optimized_tokens"] += result.optimized_tokens
        estimated_cost_saved = (result.baseline_tokens - result.optimized_tokens) * 0.00001
        self.metrics["total_cost_saved"] += estimated_cost_saved

        return result

    def get_metrics(self) -> Dict[str, Any]:
        """Get agent metrics."""
        return {
            **self.metrics,
            "average_cost_reduction": (
                (
                    (
                        self.metrics["total_baseline_tokens"]
                        - self.metrics["total_optimized_tokens"]
                    )
                    / self.metrics["total_baseline_tokens"]
                )
                * 100
            )
            if self.metrics["total_baseline_tokens"] > 0
            else 0,
        }


@dataclass
class QueryResult:
    """Result of a query execution."""
    query_id: str
    query_text: str
    baseline_tokens: int
    optimized_tokens: int
    cost_reduction_percent: float
    contexts: List[Dict[str, Any]]
    optimization_applied: List[str]
    execution_time_ms: int
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def is_effective(self) -> bool:
        """Check if optimization met 60-75% reduction target."""
        return 60.0 <= self.cost_reduction_percent <= 75.0

    def exceeds_target(self) -> bool:
        """Check if optimization exceeded 75% reduction."""
        return self.cost_reduction_percent > 75.0

    def get_context_text(self) -> str:
        """Get concatenated context."""
        return "\n".join(
            [str(ctx.get("content", "")) for ctx in self.contexts]
        )
