"""
PyStreamMCP - Intelligence layer for AI agents

Query optimization, context discovery, and cost reduction for LLM applications.
Reduces token usage by 60-75% while maintaining quality.

Includes StatGuardian integration for data quality validation.
"""

__version__ = "3.3.6"

from .agent import Agent, QueryResult
from .query import Query, QueryIntent, QueryConstraints
from .context import Context, ContextType, ContextWindow
from .discovery import Discovery, DiscoveredSource, SourceType, SourceRegistry, DataSource
from .retrieval import (
    BackendName,
    RequestedBackend,
    RetrievalError,
    RetrievalRequest,
    RetrievalResponse,
    RetrievalService,
)

# Optimization types
from .optimization import (
    OptimizationStrategy,
    StrategyType,
    OptimizationTechnique,
    CostMetrics,
)
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

# MCP 2.0 Support (v0.3+) — Multi-project orchestration & federation
from ._mcp_connector import Orchestrator
from .federation import (
    FederatedQueryEngine,
    FederatedResult,
    FederationUnavailable,
    execute_federated,
)
from .experimental import ExperimentalIntegrationError

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
    "SourceRegistry",
    "DataSource",
    # Retrieval adapters
    "BackendName",
    "RequestedBackend",
    "RetrievalError",
    "RetrievalRequest",
    "RetrievalResponse",
    "RetrievalService",
    # Optimization types
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
    # Sprint 1: Adapters & Servers
    "AgentFrameworkAdapter",
    "AdapterConfig",
    "AdapterRegistry",
    "FrameworkType",
    *((["PyStreamMCPServer"]) if PyStreamMCPServer else []),
    *((["PyStreamMCPAPI"]) if PyStreamMCPAPI else []),
    *((["create_app"]) if create_app else []),
    # MCP 2.0 (v0.3+)
    "Orchestrator",
    "FederatedQueryEngine",
    "FederatedResult",
    "FederationUnavailable",
    "execute_federated",
    "ExperimentalIntegrationError",
]
