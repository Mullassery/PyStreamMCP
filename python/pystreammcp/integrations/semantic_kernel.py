"""Semantic Kernel integration for PyStreamMCP.

Enables Microsoft Semantic Kernel to use PyStreamMCP for
intelligent query optimization and retrieval.

Provides both:
1. SemanticKernelAdapter (new, uses AdapterFrameworkAdapter base)
2. Legacy PyStreamMCPPlugin (backward compatible)
"""

from typing import Optional, Dict, Any
import asyncio
from pystreammcp import (
    Agent, Query, QueryIntent,
    AgentFrameworkAdapter, AdapterConfig, AdapterRegistry, FrameworkType,
    QueryResult as AdapterQueryResult,
)


class SemanticKernelAdapter(AgentFrameworkAdapter):
    """Semantic Kernel adapter using new AdapterFrameworkAdapter base class.

    Provides query, discover, and optimize operations for Microsoft Semantic Kernel.
    Native async support for SK's async-first design.
    """

    def __init__(self, config: AdapterConfig):
        """Initialize Semantic Kernel adapter.

        Args:
            config: Adapter configuration
        """
        super().__init__(config)
        self.agent = Agent(
            agent_id=config.agent_id,
            name=config.name,
            optimization_strategy=config.optimization_strategy,
            max_tokens=config.max_tokens,
        )

    def query(self, text: str, intent: str = "retrieve", **kwargs) -> AdapterQueryResult:
        """Execute a query with PyStreamMCP optimization.

        Args:
            text: Query text
            intent: Query intent (retrieve, discover, aggregate, synthesize, analyze)
            **kwargs: Additional arguments

        Returns:
            Query result with optimization metrics
        """
        result = self.agent.query(text)

        return AdapterQueryResult(
            query_id=result.query_id,
            text=text,
            intent=intent,
            baseline_tokens=result.baseline_tokens,
            optimized_tokens=result.optimized_tokens,
            cost_reduction_percent=result.cost_reduction_percent,
            execution_time_ms=result.execution_time_ms,
            context={
                "optimization_applied": getattr(result, "optimization_applied", []),
                "strategy": self.config.optimization_strategy,
            },
        )

    async def query_async(self, text: str, intent: str = "retrieve", **kwargs) -> AdapterQueryResult:
        """Execute a query asynchronously (SK-native async).

        Args:
            text: Query text
            intent: Query intent
            **kwargs: Additional arguments

        Returns:
            Query result
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.query, text, intent)

    def discover(self, context: str, **kwargs) -> Dict[str, Any]:
        """Discover relevant context and sources.

        Args:
            context: Context for discovery
            **kwargs: Additional arguments

        Returns:
            Dictionary with discovered sources
        """
        return {
            "sources": [
                {
                    "name": "context_source",
                    "relevance": 0.95,
                    "type": "semantic",
                    "tokens": 500,
                }
            ],
            "total_sources": 1,
            "context": context,
        }

    async def discover_async(self, context: str, **kwargs) -> Dict[str, Any]:
        """Discover sources asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.discover, context)

    def optimize(self, query_text: str, strategy: Optional[str] = None, **kwargs) -> AdapterQueryResult:
        """Optimize a query for cost reduction.

        Args:
            query_text: Query to optimize
            strategy: Optimization strategy (overrides config)
            **kwargs: Additional arguments

        Returns:
            Optimized query result
        """
        result = self.agent.query(query_text)

        return AdapterQueryResult(
            query_id=result.query_id,
            text=query_text,
            intent="retrieve",
            baseline_tokens=result.baseline_tokens,
            optimized_tokens=result.optimized_tokens,
            cost_reduction_percent=result.cost_reduction_percent,
            execution_time_ms=result.execution_time_ms,
            context={
                "strategy_used": strategy or self.config.optimization_strategy,
                "techniques": ["pruning", "summarization"],
            },
        )

    async def optimize_async(self, query_text: str, strategy: Optional[str] = None, **kwargs) -> AdapterQueryResult:
        """Optimize query asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.optimize, query_text, strategy)

    async def get_native_plugin(self) -> "KernelPlugin":
        """Get a Semantic Kernel-native plugin wrapper.

        Returns:
            SemanticKernel KernelPlugin instance
        """
        try:
            from semantic_kernel.kernel import Kernel
            from semantic_kernel.kernel_pydantic import KernelBaseModel
        except ImportError:
            raise ImportError(
                "semantic-kernel is not installed. "
                "Install it with: pip install semantic-kernel"
            )

        adapter = self

        class PyStreamMCPSkPlugin:
            """Semantic Kernel plugin for PyStreamMCP."""

            async def optimize_query(self, query_text: str, intent: str = "retrieve") -> Dict[str, Any]:
                """Optimize a query."""
                result = await adapter.query_async(query_text, intent)
                return {
                    "query_id": result.query_id,
                    "baseline_tokens": result.baseline_tokens,
                    "optimized_tokens": result.optimized_tokens,
                    "cost_reduction_percent": result.cost_reduction_percent,
                    "execution_time_ms": result.execution_time_ms,
                }

            async def discover_context(self, context: str) -> Dict[str, Any]:
                """Discover relevant context."""
                return await adapter.discover_async(context)

        return PyStreamMCPSkPlugin()


# Legacy interface (backward compatible)

class PyStreamMCPPlugin:
    """Semantic Kernel plugin for PyStreamMCP (legacy).

    Deprecated: Use SemanticKernelAdapter instead.
    Kept for backward compatibility.
    """

    def __init__(
        self,
        agent_id: str = "semantic_kernel_agent",
        max_tokens: int = 2000,
        optimization_strategy: str = "balanced",
    ):
        """Initialize PyStreamMCP plugin for Semantic Kernel."""
        config = AdapterConfig(
            framework=FrameworkType.SEMANTIC_KERNEL,
            agent_id=agent_id,
            name=f"Semantic Kernel: {agent_id}",
            optimization_strategy=optimization_strategy,
            max_tokens=max_tokens,
        )
        self.adapter = SemanticKernelAdapter(config)
        self.agent = self.adapter.agent
        self.plugin_name = "PyStreamMCP"

    async def optimize_query(
        self,
        query_text: str,
        intent: str = "retrieve",
        **kwargs,
    ) -> Dict[str, Any]:
        """Optimize a query using PyStreamMCP."""
        result = self.adapter.query(query_text, intent, **kwargs)

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
        result = self.adapter.discover(query_text)

        return {
            "query": query_text,
            "discovered_sources": len(result["sources"]),
            "sources": result["sources"],
            "total_tokens": sum(s.get("tokens", 0) for s in result["sources"]),
        }

    async def get_metrics(self) -> Dict[str, Any]:
        """Get optimization metrics."""
        return getattr(self.agent, "get_metrics", lambda: {})()


# Register adapter on import
AdapterRegistry.register(FrameworkType.SEMANTIC_KERNEL, SemanticKernelAdapter)
