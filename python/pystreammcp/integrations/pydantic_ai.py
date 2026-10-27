"""Experimental, unsupported PydanticAI-named helper for PyStreamMCP.

This module does not import pydantic-ai and does not implement a PydanticAI
tool, agent, or retriever. Constructing it raises unless explicitly opted in.
It is not an integration.
"""

from typing import Dict, Any, Optional
import asyncio
from pystreammcp import (
    Agent,
    AgentFrameworkAdapter,
    AdapterConfig,
    AdapterRegistry,
    FrameworkType,
)

from pystreammcp.adapters import QueryResult as AdapterQueryResult
from pystreammcp.discovery import SourceRegistry
from pystreammcp.experimental import require_experimental_opt_in


class PydanticAIAdapter(AgentFrameworkAdapter):
    """PydanticAI adapter with native async support."""

    def __init__(
        self,
        config: AdapterConfig,
        *,
        experimental: bool = False,
        registry: Optional[SourceRegistry] = None,
    ):
        """Initialize PydanticAI adapter."""
        require_experimental_opt_in("Pydantic AI", experimental)
        super().__init__(config)
        self.agent = Agent(
            agent_id=config.agent_id,
            name=config.name,
            optimization_strategy=config.optimization_strategy,
            max_tokens=config.max_tokens,
        )
        self.registry = registry if registry is not None else SourceRegistry()

    def query(
        self, text: str, intent: str = "retrieve", **kwargs
    ) -> AdapterQueryResult:
        """Execute a query."""
        result = self.agent.query(text)
        return AdapterQueryResult(
            query_id=result.query_id,
            text=text,
            intent=intent,
            baseline_tokens=result.baseline_tokens,
            optimized_tokens=result.optimized_tokens,
            cost_reduction_percent=result.cost_reduction_percent,
            execution_time_ms=result.execution_time_ms,
            context={"strategy": self.config.optimization_strategy},
        )

    async def query_async(
        self, text: str, intent: str = "retrieve", **kwargs
    ) -> AdapterQueryResult:
        """Execute query asynchronously (Pydantic AI native)."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.query, text, intent)

    def discover(self, context: str, **kwargs) -> Dict[str, Any]:
        """Discover sources registered with this adapter's SourceRegistry."""
        max_results = kwargs.get("max_results", kwargs.get("limit", 10))
        sources = self.registry.discover(context, limit=max_results)
        return {
            "sources": sources,
            "total_sources": len(sources),
            "search_context": context,
        }

    async def discover_async(self, context: str, **kwargs) -> Dict[str, Any]:
        """Discover asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.discover, context)

    def optimize(
        self, query_text: str, strategy: Optional[str] = None, **kwargs
    ) -> AdapterQueryResult:
        """Optimize a query."""
        result = self.agent.query(query_text)
        return AdapterQueryResult(
            query_id=result.query_id,
            text=query_text,
            intent="retrieve",
            baseline_tokens=result.baseline_tokens,
            optimized_tokens=result.optimized_tokens,
            cost_reduction_percent=result.cost_reduction_percent,
            execution_time_ms=result.execution_time_ms,
            context={"strategy": strategy or self.config.optimization_strategy},
        )

    async def optimize_async(
        self, query_text: str, strategy: Optional[str] = None, **kwargs
    ) -> AdapterQueryResult:
        """Optimize asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.optimize, query_text, strategy)


# Legacy support
class PyStreamMCPRetriever:
    """PydanticAI retriever (legacy)."""

    def __init__(
        self,
        agent_id: str = "pydantic_ai",
        max_tokens: int = 2000,
        *,
        experimental: bool = False,
    ):
        """Initialize retriever."""
        config = AdapterConfig(
            framework=FrameworkType.PYDANTIC_AI,
            agent_id=agent_id,
            name=f"PydanticAI: {agent_id}",
            optimization_strategy="token_efficient",
            max_tokens=max_tokens,
        )
        self.adapter = PydanticAIAdapter(config, experimental=experimental)

    async def retrieve(self, query: str) -> Dict[str, Any]:
        """Retrieve optimized context."""
        result = await self.adapter.query_async(query)
        return {
            "query": query,
            "baseline_tokens": result.baseline_tokens,
            "optimized_tokens": result.optimized_tokens,
            "cost_reduction_percent": result.cost_reduction_percent,
            "meets_target": 60 <= result.cost_reduction_percent <= 75,
        }

    async def batch_retrieve(self, queries: list) -> list:
        """Retrieve multiple queries."""
        results = []
        for query in queries:
            result = await self.retrieve(query)
            results.append(result)
        return results


def create_pystreammcp_retriever_for_pydantic(
    agent_id: str = "pydantic_ai",
    max_tokens: int = 2000,
    *,
    experimental: bool = False,
) -> PyStreamMCPRetriever:
    """Create a PyStreamMCP retriever for PydanticAI."""
    return PyStreamMCPRetriever(
        agent_id=agent_id, max_tokens=max_tokens, experimental=experimental
    )


# Register adapter
AdapterRegistry.register(FrameworkType.PYDANTIC_AI, PydanticAIAdapter)
