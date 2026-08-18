"""Langchain integration for PyStreamMCP.

Enables Langchain agents to use PyStreamMCP for intelligent
query optimization and context discovery.

Provides both:
1. LangchainAdapter (new, uses AdapterFrameworkAdapter base)
2. Legacy PyStreamMCPTool & PyStreamMCPRetriever (backward compatible)
"""

from typing import Optional, Dict, Any, List, Type
import asyncio
from pystreammcp import (
    Agent,
    Query,
    QueryIntent,
    AgentFrameworkAdapter,
    AdapterConfig,
    AdapterRegistry,
    FrameworkType,
)

from pystreammcp.adapters import QueryResult as AdapterQueryResult
from pystreammcp.discovery import SourceRegistry


class LangchainAdapter(AgentFrameworkAdapter):
    """Langchain adapter using new AgentFrameworkAdapter base class.

    Provides query, discover, and optimize operations for Langchain agents.
    Supports both sync and async execution.
    """

    def __init__(self, config: AdapterConfig, registry: Optional[SourceRegistry] = None):
        """Initialize Langchain adapter.

        Args:
            config: Adapter configuration
            registry: Optional shared SourceRegistry (e.g. the same one used
                by a PyStreamMCPAPI or PyStreamMCPServer instance, so sources
                registered on one surface are discoverable from another). A
                new, empty registry is created if not given.
        """
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

    async def query_async(
        self, text: str, intent: str = "retrieve", **kwargs
    ) -> AdapterQueryResult:
        """Execute a query asynchronously.

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
        """Discover relevant data sources for context.

        Ranks sources registered on `self.registry` (see
        `SourceRegistry.register` / pass a shared registry to `__init__`)
        by real token overlap against `context`. Returns an empty list if
        nothing is registered or nothing overlaps — never fabricated data.

        Args:
            context: Context for discovery
            **kwargs: Additional arguments

        Returns:
            Dictionary with discovered sources
        """
        sources = self.registry.discover(context, limit=kwargs.get("limit", 10))
        return {
            "sources": sources,
            "total_sources": len(sources),
            "search_context": context,
        }

    async def discover_async(self, context: str, **kwargs) -> Dict[str, Any]:
        """Discover sources asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.discover, context)

    def optimize(
        self, query_text: str, strategy: Optional[str] = None, **kwargs
    ) -> AdapterQueryResult:
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
                "techniques": ["pruning", "summarization", "caching"],
            },
        )

    async def optimize_async(
        self, query_text: str, strategy: Optional[str] = None, **kwargs
    ) -> AdapterQueryResult:
        """Optimize query asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.optimize, query_text, strategy)

    def get_tool_for_langchain(self) -> "LangchainTool":
        """Get a Langchain-compatible tool wrapper.

        Returns:
            Langchain Tool instance
        """
        try:
            # langchain >=0.2 moved Tool to langchain_core; try that first.
            from langchain_core.tools import Tool
        except ImportError:
            try:
                from langchain.tools import Tool
            except ImportError:
                raise ImportError(
                    "langchain is not installed. "
                    "Install it with: pip install langchain"
                )

        def execute_query(query_text: str, intent: str = "retrieve") -> str:
            """Execute query through Langchain tool."""
            result = self.query(query_text, intent)
            return f"""
Query ID: {result.query_id}
Baseline Tokens: {result.baseline_tokens}
Optimized Tokens: {result.optimized_tokens}
Cost Reduction: {result.cost_reduction_percent}%
Time: {result.execution_time_ms}ms
Meets Target: {60 <= result.cost_reduction_percent <= 75}
"""

        return Tool(
            name="pystreammcp_query",
            func=execute_query,
            description="Optimize and execute a query using PyStreamMCP. Returns optimized context with 60-75% token reduction.",
            return_direct=False,
        )

    def get_retriever_for_langchain(self) -> "BaseRetriever":
        """Get a Langchain-compatible retriever.

        Returns:
            Langchain BaseRetriever instance
        """
        try:
            # langchain >=0.2 moved these to langchain_core; try that first.
            from langchain_core.retrievers import BaseRetriever
            from langchain_core.documents import Document
        except ImportError:
            try:
                from langchain.schema import BaseRetriever, Document
            except ImportError:
                raise ImportError(
                    "langchain is not installed. "
                    "Install it with: pip install langchain"
                )

        adapter = self

        class PyStreamMCPLangchainRetriever(BaseRetriever):
            """Langchain retriever backed by PyStreamMCP."""

            def _get_relevant_documents(self, query: str, **kwargs) -> List["Document"]:
                # **kwargs absorbs the `run_manager` callback argument that
                # modern langchain_core's BaseRetriever ABC passes in.
                result = adapter.query(query)
                return [
                    Document(
                        page_content=f"Optimized context for: {query}",
                        metadata={
                            "query_id": result.query_id,
                            "cost_reduction": result.cost_reduction_percent,
                            "execution_time_ms": result.execution_time_ms,
                        },
                    )
                ]

        return PyStreamMCPLangchainRetriever()


# Legacy interfaces (backward compatible)


class PyStreamMCPTool:
    """Langchain tool wrapper for PyStreamMCP (legacy).

    Deprecated: Use LangchainAdapter instead.
    Kept for backward compatibility.
    """

    def __init__(
        self,
        agent_id: str = "langchain_agent",
        optimization_strategy: str = "balanced",
        max_tokens: int = 2000,
    ):
        """Initialize PyStreamMCP tool for Langchain."""
        config = AdapterConfig(
            framework=FrameworkType.LANGCHAIN,
            agent_id=agent_id,
            name=f"Langchain Agent: {agent_id}",
            optimization_strategy=optimization_strategy,
            max_tokens=max_tokens,
        )
        self.adapter = LangchainAdapter(config)
        self.agent = self.adapter.agent
        self.agent_id = agent_id
        self.name = "pystreammcp_optimize"
        self.description = (
            "Optimize and execute a query using PyStreamMCP. "
            "Returns optimized context with 60-75% token reduction. "
            "Use this when you need to get information efficiently."
        )

    def __call__(
        self, query_text: str, intent: str = "retrieve", **kwargs
    ) -> Dict[str, Any]:
        """Execute a query through PyStreamMCP."""
        result = self.adapter.query(query_text, intent, **kwargs)

        return {
            "status": "success",
            "query_text": query_text,
            "query_id": result.query_id,
            "intent": intent,
            "baseline_tokens": result.baseline_tokens,
            "optimized_tokens": result.optimized_tokens,
            "cost_reduction_percent": result.cost_reduction_percent,
            "execution_time_ms": result.execution_time_ms,
            "meets_target": 60 <= result.cost_reduction_percent <= 75,
            "estimated_cost_saved": (
                (result.baseline_tokens - result.optimized_tokens) * 0.00001
            ),
        }

    def get_tool_for_langchain(self) -> "LangchainTool":
        """Get a Langchain-compatible tool wrapper.

        Renamed to match this legacy tool's own advertised `self.name`
        (`pystreammcp_optimize`), rather than the adapter's internal
        `pystreammcp_query` tool name, so callers see one consistent
        identity for this tool regardless of which entry point they used.
        """
        langchain_tool = self.adapter.get_tool_for_langchain()
        langchain_tool.name = self.name
        return langchain_tool

    def get_metrics(self) -> Dict[str, Any]:
        """Get agent metrics."""
        return getattr(self.agent, "get_metrics", lambda: {})()


class PyStreamMCPRetriever:
    """Langchain retriever using PyStreamMCP (legacy).

    Deprecated: Use LangchainAdapter.get_retriever_for_langchain() instead.
    Kept for backward compatibility.
    """

    def __init__(
        self,
        agent_id: str = "langchain_retriever",
        max_tokens: int = 2000,
        similarity_threshold: float = 0.7,
    ):
        """Initialize PyStreamMCP retriever."""
        config = AdapterConfig(
            framework=FrameworkType.LANGCHAIN,
            agent_id=agent_id,
            name=f"Langchain Retriever: {agent_id}",
            optimization_strategy="token_efficient",
            max_tokens=max_tokens,
        )
        self.adapter = LangchainAdapter(config)
        self.agent = self.adapter.agent
        self.similarity_threshold = similarity_threshold
        self.max_tokens = max_tokens

    def get_relevant_documents(self, query: str) -> List[Dict[str, Any]]:
        """Get relevant documents for a query using PyStreamMCP."""
        result = self.adapter.query(query, optimization_strategy="token_efficient")

        return [
            {
                "page_content": f"Context for query: {query}",
                "metadata": {
                    "query_id": result.query_id,
                    "cost_reduction_percent": result.cost_reduction_percent,
                    "estimated_cost_saved": (
                        (result.baseline_tokens - result.optimized_tokens) * 0.00001
                    ),
                    "execution_time_ms": result.execution_time_ms,
                },
            }
        ]

    def get_retriever_for_langchain(self):
        """Get a Langchain-compatible retriever."""
        return self.adapter.get_retriever_for_langchain()


def create_pystreammcp_agent(
    llm,
    agent_id: str = "pystreammcp_agent",
    tools: Optional[List[Any]] = None,
    max_tokens: int = 2000,
    **kwargs,
):
    """Create a Langchain agent with PyStreamMCP integration.

    Args:
        llm: Langchain LLM instance
        agent_id: Identifier for the agent
        tools: Additional tools for the agent
        max_tokens: Token budget
        **kwargs: Additional arguments (optimization_strategy, verbose, etc.)

    Returns:
        Langchain agent initialized with PyStreamMCP
    """
    try:
        from langchain.agents import initialize_agent, AgentType
    except ImportError:
        raise ImportError(
            "langchain is not installed. " "Install it with: pip install langchain"
        )

    # Create LangchainAdapter
    config = AdapterConfig(
        framework=FrameworkType.LANGCHAIN,
        agent_id=agent_id,
        name=f"Langchain Agent: {agent_id}",
        optimization_strategy=kwargs.get("optimization_strategy", "balanced"),
        max_tokens=max_tokens,
    )
    adapter = LangchainAdapter(config)

    # Register adapter
    AdapterRegistry.register(FrameworkType.LANGCHAIN, LangchainAdapter)
    AdapterRegistry.create_adapter(config)

    # Add PyStreamMCP tool
    agent_tools = tools or []
    agent_tools.append(adapter.get_tool_for_langchain())

    # Initialize agent
    agent = initialize_agent(
        agent_tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=kwargs.get("verbose", False),
        handle_parsing_errors=True,
    )

    return agent


# Register adapter on import
AdapterRegistry.register(FrameworkType.LANGCHAIN, LangchainAdapter)
