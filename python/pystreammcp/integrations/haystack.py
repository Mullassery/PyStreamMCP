"""Haystack integration for PyStreamMCP.

Enables Haystack pipelines to use PyStreamMCP for optimized retrieval.
"""

from typing import List, Dict, Any, Optional
from pystreammcp import Agent


class PyStreamMCPRetriever:
    """Haystack component for PyStreamMCP."""

    def __init__(
        self,
        agent_id: str = "haystack_retriever",
        max_tokens: int = 2000,
    ):
        """
        Initialize PyStreamMCP for Haystack pipelines.

        Args:
            agent_id: Identifier for the retriever
            max_tokens: Token budget
        """
        self.agent = Agent(
            agent_id=agent_id,
            name=f"Haystack: {agent_id}",
            optimization_strategy="token_efficient",
            max_tokens=max_tokens,
        )
        self.max_tokens = max_tokens

    def run(self, query: str) -> Dict[str, Any]:
        """
        Retrieve documents with optimization (Haystack component interface).

        Args:
            query: Query string

        Returns:
            Dictionary with documents and metrics
        """
        result = self.agent.query(query)

        return {
            "documents": [
                {
                    "content": f"Optimized context for: {query}",
                    "meta": {
                        "baseline_tokens": result.baseline_tokens,
                        "optimized_tokens": result.optimized_tokens,
                        "cost_reduction_percent": result.cost_reduction_percent,
                    },
                }
            ],
            "metadata": {
                "cost_reduction_percent": result.cost_reduction_percent,
                "cost_saved": (result.baseline_tokens - result.optimized_tokens) * 0.00001,
                "execution_time_ms": result.execution_time_ms,
            },
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict for Haystack."""
        return {
            "class_name": "PyStreamMCPRetriever",
            "init_parameters": {
                "agent_id": self.agent.config.agent_id,
                "max_tokens": self.max_tokens,
            },
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PyStreamMCPRetriever":
        """Deserialize from dict for Haystack."""
        init_params = data.get("init_parameters", {})
        return cls(
            agent_id=init_params.get("agent_id", "haystack_retriever"),
            max_tokens=init_params.get("max_tokens", 2000),
        )


class PyStreamMCPDocumentStore:
    """Haystack document store backed by PyStreamMCP."""

    def __init__(
        self,
        agent_id: str = "haystack_docstore",
        max_tokens: int = 2000,
    ):
        """
        Initialize PyStreamMCP document store.

        Args:
            agent_id: Identifier
            max_tokens: Token budget
        """
        self.retriever = PyStreamMCPRetriever(
            agent_id=agent_id,
            max_tokens=max_tokens,
        )

    def retrieve_documents(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve documents (document store interface).

        Args:
            query: Query string
            limit: Maximum number of documents

        Returns:
            List of documents
        """
        result = self.retriever.run(query)
        return result["documents"][:limit]

    def query(self, query: str) -> Dict[str, Any]:
        """Execute query and return results with metrics."""
        return self.retriever.run(query)


def create_pystreammcp_retriever_for_haystack(
    agent_id: str = "haystack_retriever",
    max_tokens: int = 2000,
) -> PyStreamMCPRetriever:
    """
    Create a PyStreamMCP retriever for Haystack.

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
