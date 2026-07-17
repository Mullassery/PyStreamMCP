"""
PyStreamMCP - Intelligence layer for AI agents

Query optimization, context discovery, and cost reduction for LLM applications.
Reduces token usage by 60-75% while maintaining quality.

Includes StatGuardian integration for data quality validation.
"""

__version__ = "0.2.1"

from .agent import Agent, QueryResult
from .query import Query, QueryIntent, QueryConstraints
from .context import Context, ContextType, ContextWindow
from .discovery import Discovery, DiscoveredSource, SourceType
from .optimization import OptimizationStrategy, StrategyType, OptimizationTechnique, CostMetrics
from .quality import (
    QualityValidator,
    ValidationGate,
    ValidationResult,
    QualityStatus,
    QualityCheck,
)

__all__ = [
    # Core
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
    # Quality Validation (StatGuardian integration)
    "QualityValidator",
    "ValidationGate",
    "ValidationResult",
    "QualityStatus",
    "QualityCheck",
]
