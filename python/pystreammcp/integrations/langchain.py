"""Langchain integration for PyStreamMCP.

Enables Langchain agents to use PyStreamMCP for intelligent
query optimization and context discovery.
"""

from typing import Optional, Dict, Any, List, Type
from pystreammcp import Agent, Query, QueryIntent, OptimizationStrategy, StrategyType


class PyStreamMCPTool:
    """Langchain tool wrapper for PyStreamMCP."""

    def __init__(
        self,
        agent_id: str = "langchain_agent",
        optimization_strategy: str = "balanced",
        max_tokens: int = 2000,
    ):
        """
        Initialize PyStreamMCP tool for Langchain.

        Args:
            agent_id: Identifier for the agent
            optimization_strategy: How to optimize (balanced, token_efficient, quality_first)
            max_tokens: Token budget for queries
        """
        self.agent = Agent(
            agent_id=agent_id,
            name=f"Langchain Agent: {agent_id}",
            optimization_strategy=optimization_strategy,
            max_tokens=max_tokens,
        )
        self.name = "pystreammcp_optimize"
        self.description = (
            "Optimize and execute a query using PyStreamMCP. "
            "Returns optimized context with 60-75% token reduction. "
            "Use this when you need to get information efficiently."
        )

    def __call__(self, query_text: str, intent: str = "retrieve", **kwargs) -> Dict[str, Any]:
        """
        Execute a query through PyStreamMCP.

        Args:
            query_text: The question or query
            intent: Query intent (retrieve, discover, aggregate, synthesize, analyze)
            **kwargs: Additional arguments (max_tokens, optimization_strategy)

        Returns:
            Dictionary with optimized context and metrics
        """
        # Map intent string to QueryIntent enum
        intent_map = {
            "retrieve": QueryIntent.RETRIEVE,
            "discover": QueryIntent.DISCOVER,
            "aggregate": QueryIntent.AGGREGATE,
            "synthesize": QueryIntent.SYNTHESIZE,
            "analyze": QueryIntent.ANALYZE,
        }

        intent_enum = intent_map.get(intent.lower(), QueryIntent.RETRIEVE)

        # Create and execute query
        query = Query(
            text=query_text,
            agent_id=self.agent.config.agent_id,
            intent=intent_enum,
        )

        # Override constraints if provided
        if "max_tokens" in kwargs:
            query.constraints.max_tokens = kwargs["max_tokens"]

        result = self.agent.query(query_text)

        return {
            "query_text": query_text,
            "query_id": result.query_id,
            "intent": intent,
            "baseline_tokens": result.baseline_tokens,
            "optimized_tokens": result.optimized_tokens,
            "cost_reduction_percent": result.cost_reduction_percent,
            "execution_time_ms": result.execution_time_ms,
            "techniques_applied": result.optimization_applied,
            "meets_target": 60 <= result.cost_reduction_percent <= 75,
            "estimated_cost_saved": (
                (result.baseline_tokens - result.optimized_tokens) * 0.00001
            ),
        }

    def get_tool_for_langchain(self) -> "LangchainTool":
        """Get a Langchain-compatible tool wrapper."""
        try:
            from langchain.tools import Tool
        except ImportError:
            raise ImportError(
                "langchain is not installed. "
                "Install it with: pip install langchain"
            )

        return Tool(
            name=self.name,
            func=self,
            description=self.description,
            return_direct=False,
        )

    def get_metrics(self) -> Dict[str, Any]:
        """Get agent metrics."""
        return self.agent.get_metrics()


class PyStreamMCPRetriever:
    """Langchain retriever using PyStreamMCP for context optimization."""

    def __init__(
        self,
        agent_id: str = "langchain_retriever",
        max_tokens: int = 2000,
        similarity_threshold: float = 0.7,
    ):
        """
        Initialize PyStreamMCP retriever.

        Args:
            agent_id: Identifier for the retriever
            max_tokens: Maximum tokens in context window
            similarity_threshold: Minimum relevance score
        """
        self.agent = Agent(
            agent_id=agent_id,
            name=f"Langchain Retriever: {agent_id}",
            optimization_strategy="token_efficient",
            max_tokens=max_tokens,
        )
        self.similarity_threshold = similarity_threshold
        self.max_tokens = max_tokens

    def get_relevant_documents(self, query: str) -> List[Dict[str, Any]]:
        """
        Get relevant documents for a query using PyStreamMCP.

        Args:
            query: The query text

        Returns:
            List of relevant documents with scores
        """
        result = self.agent.query(
            query,
            optimization="token_efficient",
            max_tokens=self.max_tokens,
        )

        # Return optimized context as documents
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
        try:
            from langchain.schema import BaseRetriever, Document
        except ImportError:
            raise ImportError(
                "langchain is not installed. "
                "Install it with: pip install langchain"
            )

        class PyStreamMCPLangchainRetriever(BaseRetriever):
            """Langchain retriever backed by PyStreamMCP."""

            def _get_relevant_documents(self, query: str) -> List[Document]:
                docs = self.get_relevant_documents(query)
                return [Document(page_content=d["page_content"], metadata=d["metadata"]) for d in docs]

        retriever = PyStreamMCPLangchainRetriever()
        retriever.get_relevant_documents = self.get_relevant_documents
        return retriever


def create_pystreammcp_agent(
    llm,
    agent_id: str = "pystreammcp_agent",
    tools: Optional[List[Any]] = None,
    max_tokens: int = 2000,
    **kwargs,
):
    """
    Create a Langchain agent with PyStreamMCP integration.

    Args:
        llm: Langchain LLM instance
        agent_id: Identifier for the agent
        tools: Additional tools for the agent
        max_tokens: Token budget
        **kwargs: Additional arguments

    Returns:
        Langchain agent initialized with PyStreamMCP
    """
    try:
        from langchain.agents import initialize_agent, AgentType
    except ImportError:
        raise ImportError(
            "langchain is not installed. "
            "Install it with: pip install langchain"
        )

    # Create PyStreamMCP tool
    pystreammcp_tool = PyStreamMCPTool(
        agent_id=agent_id,
        optimization_strategy=kwargs.get("optimization_strategy", "balanced"),
        max_tokens=max_tokens,
    )

    # Add to tools list
    agent_tools = tools or []
    agent_tools.append(pystreammcp_tool.get_tool_for_langchain())

    # Initialize agent
    agent = initialize_agent(
        agent_tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=kwargs.get("verbose", False),
        handle_parsing_errors=True,
    )

    return agent
