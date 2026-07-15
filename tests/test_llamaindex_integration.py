"""Tests for Llamaindex integration."""

import pytest
from pystreammcp.integrations.llamaindex import (
    StreamMCPRetriever,
    StreamMCPQueryEngine,
    create_pystreammcp_index,
)


class TestStreamMCPRetriever:
    """Tests for StreamMCPRetriever."""

    def test_retriever_creation(self):
        """Test creating a StreamMCPRetriever."""
        retriever = StreamMCPRetriever(
            agent_id="test_retriever",
            max_tokens=1500,
            optimization_strategy="token_efficient",
        )

        assert retriever.agent is not None
        assert retriever.max_tokens == 1500
        assert retriever.optimization_strategy == "token_efficient"

    def test_retrieve_documents(self):
        """Test retrieving documents."""
        retriever = StreamMCPRetriever()

        nodes = retriever.retrieve("What are customer segments?")

        assert isinstance(nodes, list)
        assert len(nodes) > 0

    def test_retrieved_nodes_have_metadata(self):
        """Test that retrieved nodes include cost metrics."""
        retriever = StreamMCPRetriever()

        nodes = retriever.retrieve("Test query")
        assert len(nodes) > 0

        node = nodes[0]
        metadata = node.node.metadata

        assert "query_id" in metadata
        assert "cost_reduction_percent" in metadata
        assert "baseline_tokens" in metadata
        assert "optimized_tokens" in metadata
        assert "estimated_cost_saved" in metadata
        assert "execution_time_ms" in metadata

    def test_node_score_based_on_cost_reduction(self):
        """Test that node score reflects cost reduction."""
        retriever = StreamMCPRetriever()

        nodes = retriever.retrieve("Query text")

        if nodes:
            # Score should be between 0 and 1
            assert 0.0 <= nodes[0].score <= 1.0

    def test_retriever_with_different_strategies(self):
        """Test retriever with different optimization strategies."""
        strategies = ["balanced", "token_efficient", "quality_first"]

        for strategy in strategies:
            retriever = StreamMCPRetriever(
                optimization_strategy=strategy,
            )

            nodes = retriever.retrieve("Test query")
            assert len(nodes) > 0


class TestStreamMCPQueryEngine:
    """Tests for StreamMCPQueryEngine."""

    def test_query_engine_creation(self):
        """Test creating a StreamMCPQueryEngine."""
        retriever = StreamMCPRetriever()
        engine = StreamMCPQueryEngine(retriever=retriever)

        assert engine.retriever is not None

    def test_query_execution(self):
        """Test executing a query through the engine."""
        retriever = StreamMCPRetriever()
        engine = StreamMCPQueryEngine(retriever=retriever)

        result = engine.query("What are the top products?")

        assert isinstance(result, dict)
        assert "response" in result
        assert "source_nodes" in result
        assert "metadata" in result

    def test_query_result_metadata(self):
        """Test that query results include optimization metrics."""
        retriever = StreamMCPRetriever()
        engine = StreamMCPQueryEngine(retriever=retriever)

        result = engine.query("Test query")
        metadata = result["metadata"]

        assert "cost_reduction_percent" in metadata
        assert "baseline_tokens" in metadata
        assert "optimized_tokens" in metadata
        assert "estimated_cost_saved" in metadata

    def test_cost_reduction_validation(self):
        """Test that cost reduction is positive."""
        retriever = StreamMCPRetriever()
        engine = StreamMCPQueryEngine(retriever=retriever)

        result = engine.query("Test query")
        reduction = result["metadata"]["cost_reduction_percent"]

        assert reduction >= 60.0


class TestIndexCreation:
    """Tests for create_pystreammcp_index function."""

    def test_index_creation_without_documents(self):
        """Test creating an index without documents."""
        retriever = create_pystreammcp_index(
            agent_id="test_index",
            max_tokens=2000,
        )

        assert retriever is not None
        assert hasattr(retriever, "retrieve")

    def test_index_creation_with_optional_args(self):
        """Test creating index with optional arguments."""
        retriever = create_pystreammcp_index(
            agent_id="test_index",
            max_tokens=1500,
            optimization_strategy="token_efficient",
        )

        assert retriever.max_tokens == 1500
        assert retriever.optimization_strategy == "token_efficient"

    def test_index_retrieval(self):
        """Test using created index for retrieval."""
        retriever = create_pystreammcp_index()

        nodes = retriever.retrieve("Test query")

        assert isinstance(nodes, list)
        assert len(nodes) > 0


class TestIntegrationFlow:
    """Tests for end-to-end Llamaindex integration flow."""

    def test_retriever_workflow(self):
        """Test complete retriever workflow."""
        retriever = StreamMCPRetriever()

        queries = [
            "What are customer segments?",
            "Find retention strategies",
            "List performance metrics",
        ]

        results = []
        for query in queries:
            nodes = retriever.retrieve(query)
            results.append(nodes)

        assert len(results) == 3
        assert all(len(r) > 0 for r in results)

    def test_query_engine_workflow(self):
        """Test complete query engine workflow."""
        retriever = StreamMCPRetriever()
        engine = StreamMCPQueryEngine(retriever=retriever)

        queries = [
            "What are top customers?",
            "Show engagement trends",
            "List feature adoption",
        ]

        results = []
        for query in queries:
            result = engine.query(query)
            results.append(result)

        assert len(results) == 3

        # All should have positive cost reduction
        for result in results:
            reduction = result["metadata"]["cost_reduction_percent"]
            assert reduction > 0

    def test_cost_accumulation(self):
        """Test that costs accumulate correctly."""
        retriever = StreamMCPRetriever()

        total_savings = 0.0
        for i in range(3):
            nodes = retriever.retrieve(f"Query {i+1}")
            if nodes:
                savings = nodes[0].node.metadata["estimated_cost_saved"]
                total_savings += savings

        assert total_savings > 0

    def test_optimization_target_met(self):
        """Test that optimization targets are met."""
        retriever = StreamMCPRetriever(
            optimization_strategy="token_efficient",
        )

        nodes = retriever.retrieve("Test query")

        if nodes:
            metadata = nodes[0].node.metadata
            reduction = metadata["cost_reduction_percent"]

            # Should meet 60-75% target
            assert reduction >= 60.0
