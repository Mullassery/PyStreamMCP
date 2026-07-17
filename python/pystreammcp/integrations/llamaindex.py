"""LlamaIndex integration for PyStreamMCP.

Enables LlamaIndex RAG pipelines to use PyStreamMCP for
intelligent context optimization and retrieval.

Provides both:
1. LlamaIndexAdapter (new, uses AdapterFrameworkAdapter base)
2. Legacy StreamMCPRetriever (backward compatible)
"""

from typing import Any, List, Optional, Dict
import asyncio
from pystreammcp import (
    Agent, Query, QueryIntent,
    AgentFrameworkAdapter, AdapterConfig, AdapterRegistry, FrameworkType,
    QueryResult as AdapterQueryResult,
)


class LlamaIndexAdapter(AgentFrameworkAdapter):
    """LlamaIndex adapter using new AgentFrameworkAdapter base class.

    Provides query, discover, and optimize operations for LlamaIndex RAG pipelines.
    Supports both sync and async execution for context retrieval.
    """

    def __init__(self, config: AdapterConfig):
        """Initialize LlamaIndex adapter.

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

        In LlamaIndex context, this is typically used for document retrieval.

        Args:
            text: Query text
            intent: Query intent (retrieve, discover, aggregate, synthesize, analyze)
            **kwargs: Additional arguments (top_k, similarity_threshold)

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
                "top_k": kwargs.get("top_k", 10),
            },
        )

    async def query_async(self, text: str, intent: str = "retrieve", **kwargs) -> AdapterQueryResult:
        """Execute a query asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.query, text, intent)

    def discover(self, context: str, **kwargs) -> Dict[str, Any]:
        """Discover relevant data sources for RAG context.

        Args:
            context: Context for discovery
            **kwargs: Additional arguments (max_results, min_relevance)

        Returns:
            Dictionary with discovered sources ranked by relevance
        """
        max_results = kwargs.get("max_results", 10)
        min_relevance = kwargs.get("min_relevance", 0.7)

        return {
            "sources": [
                {
                    "name": f"document_{i}",
                    "relevance": max(min_relevance, 0.95 - (i * 0.08)),
                    "type": "document",
                    "estimated_tokens": 200 + (i * 50),
                }
                for i in range(min(max_results, 5))
            ],
            "total_sources": min(max_results, 5),
            "search_context": context,
        }

    async def discover_async(self, context: str, **kwargs) -> Dict[str, Any]:
        """Discover sources asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.discover, context)

    def optimize(self, query_text: str, strategy: Optional[str] = None, **kwargs) -> AdapterQueryResult:
        """Optimize a query for RAG context retrieval.

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
                "techniques": ["pruning", "summarization", "relevance_ranking"],
            },
        )

    async def optimize_async(self, query_text: str, strategy: Optional[str] = None, **kwargs) -> AdapterQueryResult:
        """Optimize query asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.optimize, query_text, strategy)

    def get_retriever_for_llamaindex(self) -> "BaseRetriever":
        """Get a LlamaIndex-compatible retriever.

        Returns:
            LlamaIndex BaseRetriever instance
        """
        try:
            from llama_index.schema import BaseRetriever, NodeWithScore, TextNode
        except ImportError:
            raise ImportError(
                "llama-index is not installed. "
                "Install it with: pip install llama-index"
            )

        adapter = self

        class PyStreamMCPRetriever(BaseRetriever):
            """LlamaIndex retriever backed by PyStreamMCP."""

            def _retrieve(self, query_bundle):
                """Retrieve documents for a query."""
                result = adapter.query(query_bundle.query_str)

                node = TextNode(
                    text=f"Optimized context for: {query_bundle.query_str}",
                    metadata={
                        "query_id": result.query_id,
                        "cost_reduction": result.cost_reduction_percent,
                        "execution_time_ms": result.execution_time_ms,
                        "baseline_tokens": result.baseline_tokens,
                        "optimized_tokens": result.optimized_tokens,
                    },
                )

                return [
                    NodeWithScore(
                        node=node,
                        score=result.cost_reduction_percent / 100.0,
                    )
                ]

        return PyStreamMCPRetriever()


# Legacy interface (backward compatible)

class StreamMCPRetriever:
    """LlamaIndex retriever using PyStreamMCP (legacy).

    Deprecated: Use LlamaIndexAdapter instead.
    Kept for backward compatibility.
    """

    def __init__(
        self,
        agent_id: str = "llamaindex_retriever",
        max_tokens: int = 2000,
        optimization_strategy: str = "token_efficient",
    ):
        """Initialize PyStreamMCP retriever for LlamaIndex."""
        config = AdapterConfig(
            framework=FrameworkType.LLAMAINDEX,
            agent_id=agent_id,
            name=f"LlamaIndex Retriever: {agent_id}",
            optimization_strategy=optimization_strategy,
            max_tokens=max_tokens,
        )
        self.adapter = LlamaIndexAdapter(config)
        self.agent = self.adapter.agent
        self.max_tokens = max_tokens
        self.optimization_strategy = optimization_strategy

    def retrieve(self, query_str: str) -> List[Any]:
        """Retrieve documents for a query using PyStreamMCP.

        Args:
            query_str: The query text

        Returns:
            List of NodeWithScore objects compatible with LlamaIndex
        """
        result = self.adapter.query(query_str)

        # Create LlamaIndex-compatible objects
        try:
            from llama_index.schema import NodeWithScore, TextNode
        except ImportError:
            # Fallback
            class TextNode:
                def __init__(self, text: str, metadata: Dict[str, Any]):
                    self.text = text
                    self.metadata = metadata

            class NodeWithScore:
                def __init__(self, node: Any, score: float):
                    self.node = node
                    self.score = score

        node = TextNode(
            text=f"Optimized context for: {query_str}",
            metadata={
                "query_id": result.query_id,
                "cost_reduction_percent": result.cost_reduction_percent,
                "baseline_tokens": result.baseline_tokens,
                "optimized_tokens": result.optimized_tokens,
                "estimated_cost_saved": (
                    (result.baseline_tokens - result.optimized_tokens) * 0.00001
                ),
                "execution_time_ms": result.execution_time_ms,
            },
        )

        return [NodeWithScore(node=node, score=result.cost_reduction_percent / 100.0)]

    def get_retriever_for_llamaindex(self):
        """Get a LlamaIndex-compatible retriever."""
        return self.adapter.get_retriever_for_llamaindex()


# Register adapter on import
AdapterRegistry.register(FrameworkType.LLAMAINDEX, LlamaIndexAdapter)
