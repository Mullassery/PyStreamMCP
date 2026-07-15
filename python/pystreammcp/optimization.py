"""Optimization types for PyStreamMCP."""

from typing import List, Optional
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime


class StrategyType(str, Enum):
    """Type of optimization strategy."""
    TOKEN_MINIMIZATION = "token_minimization"
    LATENCY_MINIMIZATION = "latency_minimization"
    COST_MINIMIZATION = "cost_minimization"
    QUALITY_FIRST = "quality_first"
    BALANCED = "balanced"


class OptimizationTechnique(str, Enum):
    """Optimization technique."""
    CACHING = "caching"
    SUMMARIZATION = "summarization"
    SAMPLING = "sampling"
    PRUNING = "pruning"
    COMPRESSION = "compression"
    ASYNC = "async"
    EARLY_TERMINATION = "early_termination"


@dataclass
class OptimizationStrategy:
    """Strategy for query optimization."""
    query_id: str
    strategy_type: StrategyType
    techniques: List[OptimizationTechnique] = field(default_factory=list)
    expected_reduction_percent: float = 0.0
    strategy_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not self.strategy_id:
            import uuid
            self.strategy_id = str(uuid.uuid4())

    def add_technique(self, technique: OptimizationTechnique) -> "OptimizationStrategy":
        """Add optimization technique."""
        if technique not in self.techniques:
            self.techniques.append(technique)
        return self

    def for_token_efficiency(self) -> "OptimizationStrategy":
        """Configure for token efficiency (60-75% reduction target)."""
        self.techniques = [
            OptimizationTechnique.CACHING,
            OptimizationTechnique.PRUNING,
            OptimizationTechnique.SUMMARIZATION,
            OptimizationTechnique.EARLY_TERMINATION,
        ]
        self.expected_reduction_percent = 70.0
        return self

    def for_latency(self) -> "OptimizationStrategy":
        """Configure for low latency."""
        self.techniques = [
            OptimizationTechnique.CACHING,
            OptimizationTechnique.ASYNC,
        ]
        return self

    def for_quality(self) -> "OptimizationStrategy":
        """Configure for quality-first (no aggressive pruning)."""
        self.techniques = [OptimizationTechnique.CACHING]
        return self


@dataclass
class CostMetrics:
    """Cost metrics for a query."""
    query_id: str
    baseline_tokens: int
    optimized_tokens: int
    baseline_latency_ms: int = 0
    optimized_latency_ms: int = 0
    quality_maintained: bool = True
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def reduction_percent(self) -> float:
        """Token reduction percentage."""
        if self.baseline_tokens == 0:
            return 0.0
        return ((self.baseline_tokens - self.optimized_tokens) / self.baseline_tokens) * 100

    @property
    def meets_target(self) -> bool:
        """Check if optimization meets 60-75% target."""
        return 60.0 <= self.reduction_percent <= 75.0

    @property
    def exceeds_target(self) -> bool:
        """Check if optimization exceeds 75% reduction."""
        return self.reduction_percent > 75.0

    @property
    def estimated_cost_saved(self) -> float:
        """Estimated cost saved (assuming $0.00001 per token)."""
        return (self.baseline_tokens - self.optimized_tokens) * 0.00001

    def __str__(self) -> str:
        """Format metrics as string."""
        return (
            f"Tokens: {self.baseline_tokens} → {self.optimized_tokens} "
            f"({self.reduction_percent:.1f}% reduction) | "
            f"Cost saved: ${self.estimated_cost_saved:.4f}"
        )
