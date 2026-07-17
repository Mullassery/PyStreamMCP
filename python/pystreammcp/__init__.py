"""
PyStreamMCP - Intelligence layer for AI agents

Query optimization, context discovery, and cost reduction for LLM applications.
Reduces token usage by 60-75% while maintaining quality.

Includes StatGuardian integration for data quality validation.
"""

__version__ = "0.3.0"

from .agent import Agent, QueryResult
from .query import Query, QueryIntent, QueryConstraints
from .context import Context, ContextType, ContextWindow
from .discovery import Discovery, DiscoveredSource, SourceType
# Optimization imports
try:
    from .optimization import OptimizationStrategy, StrategyType, OptimizationTechnique, CostMetrics
except (ImportError, AttributeError):
    # Fallback: Phase 3+ uses new optimization module structure
    try:
        from .optimization import StrategyType, OptimizationTechnique
        OptimizationStrategy = None
        CostMetrics = None
    except (ImportError, AttributeError):
        OptimizationStrategy = None
        StrategyType = None
        OptimizationTechnique = None
        CostMetrics = None
from .quality import (
    QualityValidator,
    ValidationGate,
    ValidationResult,
    QualityStatus,
    QualityCheck,
)

# Sprint 1: Framework Integration & Server
from .adapters import (
    AgentFrameworkAdapter,
    AdapterConfig,
    AdapterRegistry,
    FrameworkType,
    QueryResult as AdapterQueryResult,
)
# Optional: MCP and API servers (require additional dependencies)
try:
    from .mcp_server import PyStreamMCPServer
except ImportError:
    PyStreamMCPServer = None

try:
    from .api import PyStreamMCPAPI, create_app
except ImportError:
    PyStreamMCPAPI = None
    create_app = None

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
    # Legacy optimization (optional, phase 1-2)
    *((["OptimizationStrategy"]) if OptimizationStrategy else []),
    *((["StrategyType"]) if StrategyType else []),
    *((["OptimizationTechnique"]) if OptimizationTechnique else []),
    *((["CostMetrics"]) if CostMetrics else []),
    # Quality Validation (StatGuardian integration)
    "QualityValidator",
    "ValidationGate",
    "ValidationResult",
    "QualityStatus",
    "QualityCheck",
    # Sprint 1: Adapters & Servers
    "AgentFrameworkAdapter",
    "AdapterConfig",
    "AdapterRegistry",
    "FrameworkType",
    *((["PyStreamMCPServer"]) if PyStreamMCPServer else []),
    *((["PyStreamMCPAPI"]) if PyStreamMCPAPI else []),
    *((["create_app"]) if create_app else []),
]
