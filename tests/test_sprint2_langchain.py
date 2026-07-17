"""Sprint 2 integration tests - Langchain Integration.

Tests for:
- LangchainAdapter implementation
- Tool creation and execution
- Retriever integration
- Multi-step workflows
- Async/sync execution
"""

import pytest
import asyncio
from pystreammcp.adapters import AdapterConfig, FrameworkType
from pystreammcp.integrations.langchain import (
    LangchainAdapter, PyStreamMCPTool, PyStreamMCPRetriever,
    create_pystreammcp_agent, AdapterRegistry,
)


class TestLangchainAdapter:
    """Test LangchainAdapter implementation."""

    def test_adapter_initialization(self):
        """Test adapter creation."""
        config = AdapterConfig(
            framework=FrameworkType.LANGCHAIN,
            agent_id="test_langchain",
            name="Test Langchain",
            optimization_strategy="balanced",
            max_tokens=2000,
        )
        adapter = LangchainAdapter(config)

        assert adapter.agent_id == "test_langchain"
        assert adapter.framework == FrameworkType.LANGCHAIN
        assert adapter.is_async_capable is True

    def test_adapter_query(self):
        """Test query execution through adapter."""
        config = AdapterConfig(
            framework=FrameworkType.LANGCHAIN,
            agent_id="query_test",
            name="Query Test",
        )
        adapter = LangchainAdapter(config)

        result = adapter.query("What is the top product?", intent="retrieve")

        assert result.query_id is not None
        assert result.baseline_tokens > 0
        assert result.optimized_tokens > 0
        assert result.cost_reduction_percent > 0
        assert result.execution_time_ms > 0

    def test_adapter_discover(self):
        """Test discovery through adapter."""
        config = AdapterConfig(
            framework=FrameworkType.LANGCHAIN,
            agent_id="discover_test",
            name="Discovery Test",
        )
        adapter = LangchainAdapter(config)

        result = adapter.discover("high-value customers")

        assert "sources" in result
        assert isinstance(result["sources"], list)
        assert len(result["sources"]) > 0
        assert "relevance" in result["sources"][0]

    def test_adapter_optimize(self):
        """Test query optimization."""
        config = AdapterConfig(
            framework=FrameworkType.LANGCHAIN,
            agent_id="optimize_test",
            name="Optimize Test",
        )
        adapter = LangchainAdapter(config)

        result = adapter.optimize(
            "Show top 100 products by revenue last quarter",
            strategy="token_efficient"
        )

        assert result.query_id is not None
        assert result.baseline_tokens > result.optimized_tokens
        assert result.cost_reduction_percent > 0
        assert "techniques" in result.context

    @pytest.mark.asyncio
    async def test_adapter_async_query(self):
        """Test async query execution."""
        config = AdapterConfig(
            framework=FrameworkType.LANGCHAIN,
            agent_id="async_test",
            name="Async Test",
        )
        adapter = LangchainAdapter(config)

        result = await adapter.query_async("Async query test")

        assert result.query_id is not None
        assert result.baseline_tokens > 0

    @pytest.mark.asyncio
    async def test_adapter_async_discover(self):
        """Test async discovery."""
        config = AdapterConfig(
            framework=FrameworkType.LANGCHAIN,
            agent_id="async_discover_test",
            name="Async Discovery Test",
        )
        adapter = LangchainAdapter(config)

        result = await adapter.discover_async("test context")

        assert "sources" in result
        assert isinstance(result["sources"], list)

    def test_adapter_get_tool_for_langchain(self):
        """Test Langchain tool creation."""
        config = AdapterConfig(
            framework=FrameworkType.LANGCHAIN,
            agent_id="tool_test",
            name="Tool Test",
        )
        adapter = LangchainAdapter(config)

        tool = adapter.get_tool_for_langchain()

        assert tool is not None
        assert tool.name == "pystreammcp_query"
        assert "optimize" in tool.description.lower()

    def test_adapter_get_retriever(self):
        """Test Langchain retriever creation."""
        config = AdapterConfig(
            framework=FrameworkType.LANGCHAIN,
            agent_id="retriever_test",
            name="Retriever Test",
        )
        adapter = LangchainAdapter(config)

        retriever = adapter.get_retriever_for_langchain()

        assert retriever is not None
        # Test retriever can be called
        docs = retriever._get_relevant_documents("test query")
        assert len(docs) > 0


class TestLegacyInterfaces:
    """Test backward compatibility with legacy interfaces."""

    def test_pystreammcp_tool_initialization(self):
        """Test PyStreamMCPTool creation."""
        tool = PyStreamMCPTool(
            agent_id="legacy_tool",
            optimization_strategy="token_efficient",
            max_tokens=1500,
        )

        assert tool.name == "pystreammcp_optimize"
        assert tool.agent_id == "legacy_tool"

    def test_pystreammcp_tool_call(self):
        """Test PyStreamMCPTool execution."""
        tool = PyStreamMCPTool()

        result = tool("What is this?", intent="retrieve")

        assert result["status"] == "success"
        assert "query_id" in result
        assert result["baseline_tokens"] > 0
        assert result["optimized_tokens"] > 0

    def test_pystreammcp_tool_langchain_wrapper(self):
        """Test legacy tool Langchain wrapper."""
        tool = PyStreamMCPTool()
        langchain_tool = tool.get_tool_for_langchain()

        assert langchain_tool is not None
        assert langchain_tool.name == "pystreammcp_optimize"

    def test_pystreammcp_retriever(self):
        """Test PyStreamMCPRetriever."""
        retriever = PyStreamMCPRetriever(
            agent_id="legacy_retriever",
            max_tokens=2000,
        )

        docs = retriever.get_relevant_documents("test query")

        assert isinstance(docs, list)
        assert len(docs) > 0
        assert "page_content" in docs[0]
        assert "metadata" in docs[0]

    def test_pystreammcp_retriever_langchain_wrapper(self):
        """Test legacy retriever Langchain wrapper."""
        retriever = PyStreamMCPRetriever()
        langchain_retriever = retriever.get_retriever_for_langchain()

        assert langchain_retriever is not None


class TestWorkflows:
    """Test integrated workflows."""

    def test_multistep_workflow(self):
        """Test multi-step discover → optimize → execute workflow."""
        config = AdapterConfig(
            framework=FrameworkType.LANGCHAIN,
            agent_id="workflow_test",
            name="Workflow Test",
            optimization_strategy="token_efficient",
        )
        adapter = LangchainAdapter(config)

        # Step 1: Discover
        discovery = adapter.discover("customers data")
        assert discovery["total_sources"] > 0

        # Step 2: Optimize
        query = "Show top customers by LTV"
        optimize_result = adapter.optimize(query)
        assert optimize_result.cost_reduction_percent > 0

        # Step 3: Execute
        query_result = adapter.query(query)
        assert query_result.query_id is not None

    @pytest.mark.asyncio
    async def test_async_batch_workflow(self):
        """Test batch async query execution."""
        config = AdapterConfig(
            framework=FrameworkType.LANGCHAIN,
            agent_id="batch_test",
            name="Batch Test",
        )
        adapter = LangchainAdapter(config)

        queries = [
            "Top 10 products",
            "Customer segments",
            "Revenue trends",
        ]

        # Execute all queries concurrently
        tasks = [adapter.query_async(q) for q in queries]
        results = await asyncio.gather(*tasks)

        assert len(results) == len(queries)
        for result in results:
            assert result.baseline_tokens > 0
            assert result.optimized_tokens > 0

    def test_adapter_registry_integration(self):
        """Test Langchain adapter in registry."""
        # Adapter should be pre-registered
        adapter_class = AdapterRegistry.get_adapter_class(FrameworkType.LANGCHAIN)
        assert adapter_class == LangchainAdapter

        # Create via registry
        config = AdapterConfig(
            framework=FrameworkType.LANGCHAIN,
            agent_id="registry_test",
            name="Registry Test",
        )
        adapter = AdapterRegistry.create_adapter(config)
        assert isinstance(adapter, LangchainAdapter)

        # Retrieve from registry
        retrieved = AdapterRegistry.get_adapter("registry_test")
        assert retrieved == adapter


class TestCostMetrics:
    """Test cost and performance metrics."""

    def test_cost_reduction_calculation(self):
        """Test cost reduction percentage calculation."""
        config = AdapterConfig(
            framework=FrameworkType.LANGCHAIN,
            agent_id="metrics_test",
            name="Metrics Test",
        )
        adapter = LangchainAdapter(config)

        result = adapter.query("Test query")

        # Verify cost reduction is within expected range (60-75%)
        assert 50 <= result.cost_reduction_percent <= 90  # Allow some variance

        # Verify baseline > optimized
        assert result.baseline_tokens > result.optimized_tokens

    def test_execution_time_tracking(self):
        """Test execution time is measured."""
        config = AdapterConfig(
            framework=FrameworkType.LANGCHAIN,
            agent_id="timing_test",
            name="Timing Test",
        )
        adapter = LangchainAdapter(config)

        result = adapter.query("Test query")

        assert result.execution_time_ms > 0
        assert isinstance(result.execution_time_ms, float)


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_empty_query(self):
        """Test handling of empty query."""
        config = AdapterConfig(
            framework=FrameworkType.LANGCHAIN,
            agent_id="error_test",
            name="Error Test",
        )
        adapter = LangchainAdapter(config)

        # Should handle gracefully (Rust core validation)
        result = adapter.query("")
        assert result.query_id is not None

    def test_very_long_query(self):
        """Test handling of very long queries."""
        config = AdapterConfig(
            framework=FrameworkType.LANGCHAIN,
            agent_id="long_query_test",
            name="Long Query Test",
        )
        adapter = LangchainAdapter(config)

        long_query = "test " * 1000  # Very long query
        result = adapter.query(long_query)

        assert result.query_id is not None
        assert result.baseline_tokens > 0

    def test_special_characters(self):
        """Test handling of special characters."""
        config = AdapterConfig(
            framework=FrameworkType.LANGCHAIN,
            agent_id="special_char_test",
            name="Special Char Test",
        )
        adapter = LangchainAdapter(config)

        special_query = "Test query with special chars: @#$%^&*()_+-=[]{}|;:',.<>?"
        result = adapter.query(special_query)

        assert result.query_id is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
