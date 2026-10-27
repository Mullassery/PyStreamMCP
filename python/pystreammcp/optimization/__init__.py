"""Optimization module for PyStreamMCP.

Advanced query optimization techniques:
- Query decomposition
- Parallel execution planning
- Cost-quality tradeoffs
- Streaming context windows
- Multi-agent context sharing
- Legacy strategy and cost-metric types
"""

from .decomposition import QueryDecomposer, DecompositionPlan, QueryType
from .advanced import (
    StreamingContextWindow,
    MultiAgentContextSharing,
    CostOptimizationEngine,
)
from .types import (
    OptimizationStrategy,
    StrategyType,
    OptimizationTechnique,
    CostMetrics,
)

__all__ = [
    "QueryDecomposer",
    "DecompositionPlan",
    "QueryType",
    "StreamingContextWindow",
    "MultiAgentContextSharing",
    "CostOptimizationEngine",
    "OptimizationStrategy",
    "StrategyType",
    "OptimizationTechnique",
    "CostMetrics",
]
