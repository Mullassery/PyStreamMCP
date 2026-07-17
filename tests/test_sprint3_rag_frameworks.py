"""Sprint 3 integration tests - LlamaIndex and Semantic Kernel.

Tests for:
- LlamaIndexAdapter implementation
- SemanticKernelAdapter implementation
- Retriever/plugin creation
- Legacy interface compatibility
"""

import pytest
import asyncio
from pystreammcp.adapters import AdapterConfig, FrameworkType, AdapterRegistry
from pystreammcp.integrations.llamaindex import (
    LlamaIndexAdapter, StreamMCPRetriever,
)
from pystreammcp.integrations.semantic_kernel import (
    SemanticKernelAdapter, PyStreamMCPPlugin,
)


class TestLlamaIndexAdapter:
    """Test LlamaIndex adapter implementation."""

    def test_adapter_initialization(self):
        """Test LlamaIndex adapter creation."""
        config = AdapterConfig(
            framework=FrameworkType.LLAMAINDEX,
            agent_id="test_llamaindex",
            name="Test LlamaIndex",
            optimization_strategy="token_efficient",
            max_tokens=2000,
        )
        adapter = LlamaIndexAdapter(config)

        assert adapter.agent_id == "test_llamaindex"
        assert adapter.framework == FrameworkType.LLAMAINDEX
        assert adapter.is_async_capable is True

    def test_adapter_query(self):
        """Test query execution."""
        config = AdapterConfig(
            framework=FrameworkType.LLAMAINDEX,
            agent_id="llamaindex_query_test",
            name="Query Test",
        )
        adapter = LlamaIndexAdapter(config)

        result = adapter.query("What are the key findings?", intent="retrieve")

        assert result.query_id is not None
        assert result.baseline_tokens > 0
        assert result.optimized_tokens > 0
        assert result.cost_reduction_percent > 0

    def test_adapter_discover(self):
        """Test source discovery."""
        config = AdapterConfig(
            framework=FrameworkType.LLAMAINDEX,
            agent_id="llamaindex_discover_test",
            name="Discovery Test",
        )
        adapter = LlamaIndexAdapter(config)

        result = adapter.discover("research documents", max_results=5)

        assert "sources" in result
        assert result["total_sources"] > 0
        assert all("relevance" in s for s in result["sources"])

    def test_adapter_optimize(self):
        """Test query optimization."""
        config = AdapterConfig(
            framework=FrameworkType.LLAMAINDEX,
            agent_id="llamaindex_optimize_test",
            name="Optimize Test",
        )
        adapter = LlamaIndexAdapter(config)

        result = adapter.optimize("Find all research papers from 2024")

        assert result.baseline_tokens > result.optimized_tokens
        assert result.cost_reduction_percent > 0
        assert "techniques" in result.context

    @pytest.mark.asyncio
    async def test_adapter_async_query(self):
        """Test async query execution."""
        config = AdapterConfig(
            framework=FrameworkType.LLAMAINDEX,
            agent_id="llamaindex_async_test",
            name="Async Test",
        )
        adapter = LlamaIndexAdapter(config)

        result = await adapter.query_async("Async test query")

        assert result.query_id is not None
        assert result.baseline_tokens > 0

    @pytest.mark.asyncio
    async def test_adapter_async_discover(self):
        """Test async discovery."""
        config = AdapterConfig(
            framework=FrameworkType.LLAMAINDEX,
            agent_id="llamaindex_async_discover_test",
            name="Async Discovery Test",
        )
        adapter = LlamaIndexAdapter(config)

        result = await adapter.discover_async("test context")

        assert "sources" in result
        assert isinstance(result["sources"], list)

    def test_adapter_get_retriever(self):
        """Test LlamaIndex retriever creation."""
        config = AdapterConfig(
            framework=FrameworkType.LLAMAINDEX,
            agent_id="llamaindex_retriever_test",
            name="Retriever Test",
        )
        adapter = LlamaIndexAdapter(config)

        retriever = adapter.get_retriever_for_llamaindex()
        assert retriever is not None

    def test_adapter_registry(self):
        """Test adapter in registry."""
        adapter_class = AdapterRegistry.get_adapter_class(FrameworkType.LLAMAINDEX)
        assert adapter_class == LlamaIndexAdapter

    def test_legacy_retriever(self):
        """Test legacy StreamMCPRetriever."""
        retriever = StreamMCPRetriever(
            agent_id="legacy_llamaindex_test",
            max_tokens=2000,
        )

        result = retriever.retrieve("test query")

        assert isinstance(result, list)
        assert len(result) > 0


class TestSemanticKernelAdapter:
    """Test Semantic Kernel adapter implementation."""

    def test_adapter_initialization(self):
        """Test Semantic Kernel adapter creation."""
        config = AdapterConfig(
            framework=FrameworkType.SEMANTIC_KERNEL,
            agent_id="test_sk",
            name="Test Semantic Kernel",
            optimization_strategy="balanced",
            max_tokens=2000,
        )
        adapter = SemanticKernelAdapter(config)

        assert adapter.agent_id == "test_sk"
        assert adapter.framework == FrameworkType.SEMANTIC_KERNEL
        assert adapter.is_async_capable is True

    def test_adapter_query(self):
        """Test query execution."""
        config = AdapterConfig(
            framework=FrameworkType.SEMANTIC_KERNEL,
            agent_id="sk_query_test",
            name="Query Test",
        )
        adapter = SemanticKernelAdapter(config)

        result = adapter.query("Summarize this document", intent="synthesize")

        assert result.query_id is not None
        assert result.baseline_tokens > 0
        assert result.optimized_tokens > 0

    def test_adapter_discover(self):
        """Test context discovery."""
        config = AdapterConfig(
            framework=FrameworkType.SEMANTIC_KERNEL,
            agent_id="sk_discover_test",
            name="Discovery Test",
        )
        adapter = SemanticKernelAdapter(config)

        result = adapter.discover("business documents")

        assert "sources" in result
        assert len(result["sources"]) > 0

    def test_adapter_optimize(self):
        """Test query optimization."""
        config = AdapterConfig(
            framework=FrameworkType.SEMANTIC_KERNEL,
            agent_id="sk_optimize_test",
            name="Optimize Test",
            optimization_strategy="quality_first",
        )
        adapter = SemanticKernelAdapter(config)

        result = adapter.optimize("Analyze market trends and opportunities")

        assert result.baseline_tokens > result.optimized_tokens
        assert result.cost_reduction_percent > 0

    @pytest.mark.asyncio
    async def test_adapter_async_query(self):
        """Test async query (SK-native)."""
        config = AdapterConfig(
            framework=FrameworkType.SEMANTIC_KERNEL,
            agent_id="sk_async_test",
            name="Async Test",
        )
        adapter = SemanticKernelAdapter(config)

        result = await adapter.query_async("Async query test")

        assert result.query_id is not None

    @pytest.mark.asyncio
    async def test_adapter_async_discover(self):
        """Test async discovery."""
        config = AdapterConfig(
            framework=FrameworkType.SEMANTIC_KERNEL,
            agent_id="sk_async_discover_test",
            name="Async Discovery Test",
        )
        adapter = SemanticKernelAdapter(config)

        result = await adapter.discover_async("test context")

        assert "sources" in result

    @pytest.mark.asyncio
    async def test_adapter_get_native_plugin(self):
        """Test SK native plugin creation."""
        config = AdapterConfig(
            framework=FrameworkType.SEMANTIC_KERNEL,
            agent_id="sk_plugin_test",
            name="Plugin Test",
        )
        adapter = SemanticKernelAdapter(config)

        plugin = await adapter.get_native_plugin()
        assert plugin is not None

    def test_adapter_registry(self):
        """Test adapter in registry."""
        adapter_class = AdapterRegistry.get_adapter_class(FrameworkType.SEMANTIC_KERNEL)
        assert adapter_class == SemanticKernelAdapter

    def test_legacy_plugin(self):
        """Test legacy PyStreamMCPPlugin."""
        plugin = PyStreamMCPPlugin(
            agent_id="legacy_sk_test",
            optimization_strategy="balanced",
        )

        assert plugin.plugin_name == "PyStreamMCP"


class TestMultiAdapterWorkflows:
    """Test workflows using multiple adapters."""

    def test_llamaindex_to_semantic_kernel_pipeline(self):
        """Test using LlamaIndex for retrieval, then Semantic Kernel for synthesis."""
        # LlamaIndex for retrieval
        llamaindex_config = AdapterConfig(
            framework=FrameworkType.LLAMAINDEX,
            agent_id="rag_pipeline_retriever",
            name="RAG Retriever",
            optimization_strategy="token_efficient",
        )
        retriever = LlamaIndexAdapter(llamaindex_config)

        # Retrieve documents
        retrieval_result = retriever.query("Find customer feedback documents")
        assert retrieval_result.cost_reduction_percent > 0

        # Semantic Kernel for synthesis
        sk_config = AdapterConfig(
            framework=FrameworkType.SEMANTIC_KERNEL,
            agent_id="rag_pipeline_synthesizer",
            name="RAG Synthesizer",
            optimization_strategy="quality_first",
        )
        synthesizer = SemanticKernelAdapter(sk_config)

        # Synthesize findings
        synthesis_result = synthesizer.query(
            f"Synthesize insights from: {retrieval_result.text}",
            intent="synthesize"
        )
        assert synthesis_result.query_id is not None

    @pytest.mark.asyncio
    async def test_concurrent_adapter_execution(self):
        """Test concurrent execution across adapters."""
        llamaindex_config = AdapterConfig(
            framework=FrameworkType.LLAMAINDEX,
            agent_id="concurrent_llamaindex",
            name="Concurrent LlamaIndex",
        )
        llamaindex = LlamaIndexAdapter(llamaindex_config)

        sk_config = AdapterConfig(
            framework=FrameworkType.SEMANTIC_KERNEL,
            agent_id="concurrent_sk",
            name="Concurrent SK",
        )
        sk = SemanticKernelAdapter(sk_config)

        # Execute queries concurrently
        tasks = [
            llamaindex.query_async("Query 1"),
            llamaindex.query_async("Query 2"),
            sk.query_async("Query 3"),
            sk.query_async("Query 4"),
        ]
        results = await asyncio.gather(*tasks)

        assert len(results) == 4
        assert all(r.query_id is not None for r in results)


class TestCostMetrics:
    """Test cost tracking across adapters."""

    def test_llamaindex_cost_reduction(self):
        """Test LlamaIndex cost reduction metrics."""
        config = AdapterConfig(
            framework=FrameworkType.LLAMAINDEX,
            agent_id="metrics_llamaindex",
            name="Metrics LlamaIndex",
        )
        adapter = LlamaIndexAdapter(config)

        result = adapter.query("Complex query")

        assert result.cost_reduction_percent > 50
        assert result.baseline_tokens > result.optimized_tokens

    def test_semantic_kernel_cost_reduction(self):
        """Test Semantic Kernel cost reduction metrics."""
        config = AdapterConfig(
            framework=FrameworkType.SEMANTIC_KERNEL,
            agent_id="metrics_sk",
            name="Metrics SK",
        )
        adapter = SemanticKernelAdapter(config)

        result = adapter.query("Complex query")

        assert result.cost_reduction_percent > 50
        assert result.execution_time_ms > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
