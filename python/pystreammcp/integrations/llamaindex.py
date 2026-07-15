"""Llamaindex integration for PyStreamMCP.

Enables Llamaindex (formerly LlamaIndex) to use PyStreamMCP for
intelligent retrieval and context optimization.
"""

from typing import Any, List, Optional, Dict
from pystreammcp import Agent, Query, QueryIntent


class StreamMCPRetriever:
    """Llamaindex retriever using PyStreamMCP."""

    def __init__(
        self,
        agent_id: str = "llamaindex_retriever",
        max_tokens: int = 2000,
        optimization_strategy: str = "token_efficient",
    ):
        """
        Initialize PyStreamMCP retriever for Llamaindex.

        Args:
            agent_id: Identifier for the retriever
            max_tokens: Maximum tokens in context window
            optimization_strategy: How to optimize (balanced, token_efficient, quality_first)
        """
        self.agent = Agent(
            agent_id=agent_id,
            name=f"Llamaindex Retriever: {agent_id}",
            optimization_strategy=optimization_strategy,
            max_tokens=max_tokens,
        )
        self.max_tokens = max_tokens
        self.optimization_strategy = optimization_strategy

    def retrieve(self, query_str: str) -> List[Any]:
        """
        Retrieve documents for a query using PyStreamMCP.

        Args:
            query_str: The query text

        Returns:
            List of NodeWithScore objects compatible with Llamaindex
        """
        result = self.agent.query(
            query_str,
            optimization=self.optimization_strategy,
            max_tokens=self.max_tokens,
        )

        # Create Llamaindex-compatible NodeWithScore objects
        nodes = []
        try:
            from llama_index.schema import NodeWithScore, TextNode
        except ImportError:
            # Fallback if llama_index not available
            class TextNode:
                def __init__(self, text: str, metadata: Dict[str, Any]):
                    self.text = text
                    self.metadata = metadata

            class NodeWithScore:
                def __init__(self, node: Any, score: float):
                    self.node = node
                    self.score = score

        # Create a node with the optimized context
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
                "techniques_applied": result.optimization_applied,
            },
        )

        # Score based on cost reduction effectiveness
        score = min(result.cost_reduction_percent / 100.0, 1.0)
        nodes.append(NodeWithScore(node=node, score=score))

        return nodes

    def get_retriever_for_llamaindex(self):
        """Get a Llamaindex-compatible retriever."""
        try:
            from llama_index.schema import BaseRetriever
        except ImportError:
            raise ImportError(
                "llama-index is not installed. "
                "Install it with: pip install llama-index"
            )

        class PyStreamMCPRetriever(BaseRetriever):
            """Llamaindex retriever backed by PyStreamMCP."""

            def __init__(self, pystreammcp_retriever: "StreamMCPRetriever"):
                super().__init__()
                self.pystreammcp_retriever = pystreammcp_retriever

            def _retrieve(self, query_bundle: Any) -> List[Any]:
                """Retrieve documents for query."""
                return self.pystreammcp_retriever.retrieve(query_bundle.query_str)

        return PyStreamMCPRetriever(self)


class StreamMCPQueryEngine:
    """Llamaindex query engine using PyStreamMCP."""

    def __init__(
        self,
        retriever: StreamMCPRetriever,
        llm: Optional[Any] = None,
    ):
        """
        Initialize PyStreamMCP query engine for Llamaindex.

        Args:
            retriever: StreamMCPRetriever instance
            llm: Llamaindex LLM instance (optional)
        """
        self.retriever = retriever
        self.llm = llm

    def query(self, query_str: str) -> Dict[str, Any]:
        """
        Execute a query with PyStreamMCP optimization.

        Args:
            query_str: The query text

        Returns:
            Dictionary with response and metadata
        """
        # Get optimized context
        nodes = self.retriever.retrieve(query_str)

        # Build response
        context_metadata = (
            nodes[0].node.metadata if nodes else {}
        )

        return {
            "response": f"Retrieved optimized context for: {query_str}",
            "source_nodes": nodes,
            "metadata": {
                "cost_reduction_percent": context_metadata.get(
                    "cost_reduction_percent", 0
                ),
                "baseline_tokens": context_metadata.get("baseline_tokens", 0),
                "optimized_tokens": context_metadata.get("optimized_tokens", 0),
                "estimated_cost_saved": context_metadata.get(
                    "estimated_cost_saved", 0
                ),
                "execution_time_ms": context_metadata.get("execution_time_ms", 0),
            },
        }


def create_pystreammcp_index(
    documents: Optional[List[Any]] = None,
    agent_id: str = "llamaindex_index",
    max_tokens: int = 2000,
    **kwargs,
):
    """
    Create a Llamaindex index with PyStreamMCP optimization.

    Args:
        documents: List of documents (optional)
        agent_id: Identifier for the index
        max_tokens: Token budget
        **kwargs: Additional arguments

    Returns:
        Llamaindex index with PyStreamMCP retriever
    """
    try:
        from llama_index import VectorStoreIndex, Document
    except ImportError:
        raise ImportError(
            "llama-index is not installed. "
            "Install it with: pip install llama-index"
        )

    # Create retriever
    retriever = StreamMCPRetriever(
        agent_id=agent_id,
        max_tokens=max_tokens,
        optimization_strategy=kwargs.get("optimization_strategy", "token_efficient"),
    )

    # If documents provided, create index
    if documents:
        # Create standard vector store index
        index = VectorStoreIndex.from_documents(documents)

        # Create query engine with PyStreamMCP
        query_engine = StreamMCPQueryEngine(retriever=retriever)
        index.query_engine = query_engine

        return index

    # Return retriever if no documents
    return retriever
