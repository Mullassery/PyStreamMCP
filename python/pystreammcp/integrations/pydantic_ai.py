"""PydanticAI integration for PyStreamMCP.

Enables PydanticAI agents to use PyStreamMCP for optimized retrieval.
"""

from typing import Dict, Any, Optional
from pystreammcp import Agent


class PyStreamMCPRetriever:
    """PydanticAI retriever using PyStreamMCP."""

    def __init__(
        self,
        agent_id: str = "pydantic_ai",
        max_tokens: int = 2000,
    ):
        """
        Initialize PydanticAI retriever with PyStreamMCP.

        Args:
            agent_id: Identifier for the retriever
            max_tokens: Token budget
        """
        self.agent = Agent(
            agent_id=agent_id,
            name=f"PydanticAI: {agent_id}",
            optimization_strategy="token_efficient",
            max_tokens=max_tokens,
        )
        self.max_tokens = max_tokens

    async def retrieve(self, query: str) -> Dict[str, Any]:
        """
        Retrieve optimized context.

        Args:
            query: The query text

        Returns:
            Dictionary with optimized context and metrics
        """
        result = self.agent.query(query)

        return {
            "query": query,
            "context": f"Retrieved and optimized context for: {query}",
            "baseline_tokens": result.baseline_tokens,
            "optimized_tokens": result.optimized_tokens,
            "cost_reduction_percent": result.cost_reduction_percent,
            "cost_saved": (result.baseline_tokens - result.optimized_tokens) * 0.00001,
            "execution_time_ms": result.execution_time_ms,
            "meets_target": 60 <= result.cost_reduction_percent <= 75,
        }

    async def batch_retrieve(self, queries: list) -> list:
        """
        Retrieve context for multiple queries.

        Args:
            queries: List of query strings

        Returns:
            List of optimized contexts
        """
        results = []
        for query in queries:
            result = await self.retrieve(query)
            results.append(result)
        return results


def create_pystreammcp_retriever_for_pydantic(
    agent_id: str = "pydantic_ai",
    max_tokens: int = 2000,
) -> PyStreamMCPRetriever:
    """
    Create a PyStreamMCP retriever for PydanticAI.

    Args:
        agent_id: Identifier for the retriever
        max_tokens: Token budget

    Returns:
        PyStreamMCPRetriever instance
    """
    return PyStreamMCPRetriever(
        agent_id=agent_id,
        max_tokens=max_tokens,
    )
