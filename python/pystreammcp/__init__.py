"""
PyStreamMCP - Intelligence layer for AI agents

Query optimization, context discovery, and cost reduction for LLM applications.
Reduces token usage by 60-75% while maintaining quality.
"""

__version__ = "0.1.0"

from .agent import Agent, QueryResult
from .query import Query, QueryIntent, QueryConstraints
from .context import Context, ContextType, ContextWindow
from .discovery import Discovery, DiscoveredSource, SourceType
from .optimization import OptimizationStrategy, StrategyType, OptimizationTechnique, CostMetrics

__all__ = [
    "Agent",
    "QueryResult",
    "Query",
    "QueryIntent",
    "QueryConstraints",
    "Context",
    "ContextType",
    "ContextWindow",
    "Discovery",
    "DiscoveredSource",
    "SourceType",
    "OptimizationStrategy",
    "StrategyType",
    "OptimizationTechnique",
    "CostMetrics",
]
