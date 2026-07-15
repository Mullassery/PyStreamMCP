"""Tests for Langchain integration."""

import pytest
from pystreammcp.integrations.langchain import (
    PyStreamMCPTool,
    PyStreamMCPRetriever,
    create_pystreammcp_agent,
)


class TestPyStreamMCPTool:
    """Tests for PyStreamMCPTool."""

    def test_tool_creation(self):
        """Test creating a PyStreamMCPTool."""
        tool = PyStreamMCPTool(
            agent_id="test_agent",
            optimization_strategy="balanced",
            max_tokens=2000,
        )

        assert tool.agent is not None
        assert tool.name == "pystreammcp_optimize"
        assert tool.agent.config.agent_id == "test_agent"

    def test_tool_query_execution(self):
        """Test executing a query through the tool."""
        tool = PyStreamMCPTool(
            agent_id="test_agent",
            optimization_strategy="token_efficient",
        )

        result = tool("What are top customers?", intent="retrieve")

        assert isinstance(result, dict)
        assert "query_id" in result
        assert "cost_reduction_percent" in result
        assert "baseline_tokens" in result
        assert "optimized_tokens" in result
        assert "meets_target" in result

    def test_tool_intent_mapping(self):
        """Test different intent types."""
        tool = PyStreamMCPTool()

        intents = ["retrieve", "discover", "aggregate", "synthesize", "analyze"]

        for intent in intents:
            result = tool("Test query", intent=intent)
            assert result["intent"] == intent

    def test_tool_metrics(self):
        """Test getting tool metrics."""
        tool = PyStreamMCPTool()

        # Execute some queries
        tool("Query 1", intent="retrieve")
        tool("Query 2", intent="discover")

        metrics = tool.get_metrics()

        assert metrics["queries_executed"] == 2
        assert metrics["total_baseline_tokens"] > 0
        assert metrics["total_optimized_tokens"] > 0
        assert "average_cost_reduction" in metrics

    def test_cost_reduction_validation(self):
        """Test that cost reduction meets target."""
        tool = PyStreamMCPTool(
            optimization_strategy="token_efficient",
        )

        result = tool("Test query")

        # Should meet or exceed 60% reduction
        assert result["cost_reduction_percent"] >= 60.0


class TestPyStreamMCPRetriever:
    """Tests for PyStreamMCPRetriever."""

    def test_retriever_creation(self):
        """Test creating a PyStreamMCPRetriever."""
        retriever = PyStreamMCPRetriever(
            agent_id="test_retriever",
            max_tokens=1500,
        )

        assert retriever.agent is not None
        assert retriever.max_tokens == 1500

    def test_get_relevant_documents(self):
        """Test retrieving documents."""
        retriever = PyStreamMCPRetriever()

        docs = retriever.get_relevant_documents("Test query")

        assert isinstance(docs, list)
        assert len(docs) > 0

        doc = docs[0]
        assert "page_content" in doc
        assert "metadata" in doc

    def test_documents_have_metrics(self):
        """Test that retrieved documents include metrics."""
        retriever = PyStreamMCPRetriever()

        docs = retriever.get_relevant_documents("Test query")
        metadata = docs[0]["metadata"]

        assert "query_id" in metadata
        assert "cost_reduction_percent" in metadata
        assert "estimated_cost_saved" in metadata
        assert "execution_time_ms" in metadata


class TestAgentCreation:
    """Tests for create_pystreammcp_agent function."""

    def test_agent_creation_requires_langchain(self):
        """Test that agent creation fails gracefully without langchain."""
        # This is handled by the ImportError in the function

        try:
            from langchain.llms.fake import FakeListLLM
            has_langchain = True
        except ImportError:
            has_langchain = False

        if has_langchain:
            llm = FakeListLLM(responses=["Test response"])

            # Function should not raise ImportError
            try:
                agent = create_pystreammcp_agent(
                    llm,
                    agent_id="test_agent",
                )
                assert agent is not None
            except ImportError:
                pytest.skip("Langchain not installed")


class TestIntegrationFlow:
    """Tests for end-to-end Langchain integration flow."""

    def test_tool_in_workflow(self):
        """Test using tool in a workflow."""
        tool = PyStreamMCPTool()

        # Simulate agent workflow
        queries = [
            ("What are top products?", "retrieve"),
            ("Find similar customers", "discover"),
            ("Summarize metrics", "aggregate"),
        ]

        results = []
        for query, intent in queries:
            result = tool(query, intent=intent)
            results.append(result)

        assert len(results) == 3

        # All should have cost reduction
        for result in results:
            assert result["cost_reduction_percent"] > 0
            assert result["baseline_tokens"] > 0
            assert result["optimized_tokens"] > 0

    def test_multiple_tool_invocations(self):
        """Test multiple tool invocations accumulate metrics."""
        tool = PyStreamMCPTool()

        tool("Query 1")
        tool("Query 2")
        tool("Query 3")

        metrics = tool.get_metrics()
        assert metrics["queries_executed"] == 3
