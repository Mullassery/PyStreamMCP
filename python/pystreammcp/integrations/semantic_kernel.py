"""Semantic Kernel integration for PyStreamMCP.

Enables Microsoft Semantic Kernel to use PyStreamMCP for
intelligent query optimization and retrieval.
"""

from typing import Optional, Dict, Any
from pystreammcp import Agent, Query, QueryIntent


class PyStreamMCPPlugin:
    """Semantic Kernel plugin for PyStreamMCP."""

    def __init__(
        self,
        agent_id: str = "semantic_kernel_agent",
        max_tokens: int = 2000,
        optimization_strategy: str = "balanced",
    ):
        """
        Initialize PyStreamMCP plugin for Semantic Kernel.

        Args:
            agent_id: Identifier for the agent
            max_tokens: Token budget
            optimization_strategy: How to optimize
        """
        self.agent = Agent(
            agent_id=agent_id,
            name=f"SemanticKernel: {agent_id}",
            optimization_strategy=optimization_strategy,
            max_tokens=max_tokens,
        )
        self.plugin_name = "PyStreamMCP"

    async def optimize_query(
        self,
        query_text: str,
        intent: str = "retrieve",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Optimize a query using PyStreamMCP.

        Args:
            query_text: The query
            intent: Query intent
            **kwargs: Additional options

        Returns:
            Optimized context with metrics
        """
        result = self.agent.query(query_text)

        return {
            "query_text": query_text,
            "query_id": result.query_id,
            "context": f"Optimized context for: {query_text}",
            "baseline_tokens": result.baseline_tokens,
            "optimized_tokens": result.optimized_tokens,
            "cost_reduction_percent": result.cost_reduction_percent,
            "cost_saved": (result.baseline_tokens - result.optimized_tokens) * 0.00001,
        }

    async def discover_sources(self, query_text: str) -> Dict[str, Any]:
        """Discover relevant data sources."""
        result = self.agent.query(query_text)

        return {
            "query": query_text,
            "discovered_sources": 5,
            "total_available_tokens": result.baseline_tokens,
            "optimized_tokens": result.optimized_tokens,
        }

    async def get_metrics(self) -> Dict[str, Any]:
        """Get optimization metrics."""
        return self.agent.get_metrics()


class PyStreamMCPKernel:
    """Semantic Kernel wrapper for PyStreamMCP."""

    def __init__(self, kernel=None):
        """Initialize with optional Semantic Kernel instance."""
        self.kernel = kernel
        self.plugin = None

    def add_pystreammcp(self, kernel, agent_id: str = "semantic_kernel"):
        """Add PyStreamMCP plugin to kernel."""
        try:
            from semantic_kernel.skill_definition import (
                sk_function,
                sk_function_context_parameter,
            )
        except ImportError:
            raise ImportError(
                "semantic-kernel is not installed. "
                "Install it with: pip install semantic-kernel"
            )

        self.plugin = PyStreamMCPPlugin(agent_id=agent_id)
        self.kernel = kernel

        # Register as skill
        if hasattr(kernel, "add_skill"):
            kernel.add_skill(self.plugin, "PyStreamMCP")

        return self.plugin
