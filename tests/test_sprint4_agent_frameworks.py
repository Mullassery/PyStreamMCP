"""Contract tests for experimental CrewAI/PydanticAI/Haystack helpers.

These modules do not import or construct the real frameworks and are not
third-party integration tests. They are experimental and opt-in guarded.
"""

import pytest
import asyncio
from pystreammcp.adapters import AdapterConfig, FrameworkType, AdapterRegistry
from pystreammcp.experimental import (
    EXPERIMENTAL_ENV_VAR,
    ExperimentalIntegrationError,
)
from pystreammcp.integrations.crewai import CrewAIAdapter, PyStreamMCPTool as CrewAITool
from pystreammcp.integrations.pydantic_ai import PydanticAIAdapter
from pystreammcp.integrations.haystack import HaystackAdapter


@pytest.fixture(autouse=True)
def _experimental_opt_in(monkeypatch):
    monkeypatch.setenv(EXPERIMENTAL_ENV_VAR, "1")


class TestExperimentalGuards:
    """The helpers raise a clear error unless explicitly opted in."""

    @pytest.mark.parametrize(
        "adapter_cls,framework,agent_id",
        [
            (CrewAIAdapter, FrameworkType.CREWAI, "guarded_crewai"),
            (PydanticAIAdapter, FrameworkType.PYDANTIC_AI, "guarded_pydantic"),
            (HaystackAdapter, FrameworkType.HAYSTACK, "guarded_haystack"),
        ],
    )
    def test_adapter_raises_without_opt_in(
        self, monkeypatch, adapter_cls, framework, agent_id
    ):
        monkeypatch.delenv(EXPERIMENTAL_ENV_VAR, raising=False)
        config = AdapterConfig(
            framework=framework,
            agent_id=agent_id,
            name=f"{agent_id} test",
        )
        with pytest.raises(
            ExperimentalIntegrationError, match="experimental and unsupported"
        ):
            adapter_cls(config)

    def test_legacy_tool_raises_without_opt_in(self, monkeypatch):
        monkeypatch.delenv(EXPERIMENTAL_ENV_VAR, raising=False)
        with pytest.raises(
            ExperimentalIntegrationError, match="experimental and unsupported"
        ):
            CrewAITool(agent_id="guarded_legacy_crewai")

    def test_explicit_opt_in_argument(self, monkeypatch):
        monkeypatch.delenv(EXPERIMENTAL_ENV_VAR, raising=False)
        config = AdapterConfig(
            framework=FrameworkType.CREWAI,
            agent_id="explicit_opt_in",
            name="Explicit opt-in",
        )
        adapter = CrewAIAdapter(config, experimental=True)
        assert adapter.query("test").query_id


class TestCrewAIAdapter:
    """Test CrewAI adapter."""

    def test_crewai_adapter_init(self):
        """Test adapter initialization."""
        config = AdapterConfig(
            framework=FrameworkType.CREWAI,
            agent_id="crewai_test",
            name="CrewAI Test",
        )
        adapter = CrewAIAdapter(config)
        assert adapter.framework == FrameworkType.CREWAI

    def test_crewai_query(self):
        """Test query execution."""
        config = AdapterConfig(
            framework=FrameworkType.CREWAI,
            agent_id="crewai_query",
            name="CrewAI Query",
        )
        adapter = CrewAIAdapter(config)
        result = adapter.query("What needs to be done?", intent="aggregate", task_name="analysis")
        assert result.query_id is not None
        assert result.cost_reduction_percent > 0

    def test_crewai_legacy_tool(self):
        """Test legacy PyStreamMCPTool."""
        tool = CrewAITool(agent_id="legacy_crewai")
        result = tool.execute("test query")
        assert "tokens" in result
        assert "Reduction" in result


class TestPydanticAIAdapter:
    """Test PydanticAI adapter."""

    def test_pydantic_ai_adapter_init(self):
        """Test adapter initialization."""
        config = AdapterConfig(
            framework=FrameworkType.PYDANTIC_AI,
            agent_id="pydantic_test",
            name="Pydantic AI Test",
        )
        adapter = PydanticAIAdapter(config)
        assert adapter.framework == FrameworkType.PYDANTIC_AI

    def test_pydantic_ai_query(self):
        """Test query execution."""
        config = AdapterConfig(
            framework=FrameworkType.PYDANTIC_AI,
            agent_id="pydantic_query",
            name="Pydantic Query",
        )
        adapter = PydanticAIAdapter(config)
        result = adapter.query("Validate this data", intent="analyze")
        assert result.baseline_tokens > result.optimized_tokens

    @pytest.mark.asyncio
    async def test_pydantic_ai_async(self):
        """Test async execution (Pydantic AI native)."""
        config = AdapterConfig(
            framework=FrameworkType.PYDANTIC_AI,
            agent_id="pydantic_async",
            name="Pydantic Async",
        )
        adapter = PydanticAIAdapter(config)
        result = await adapter.query_async("Async validation")
        assert result.query_id is not None


class TestHaystackAdapter:
    """Test Haystack adapter."""

    def test_haystack_adapter_init(self):
        """Test adapter initialization."""
        config = AdapterConfig(
            framework=FrameworkType.HAYSTACK,
            agent_id="haystack_test",
            name="Haystack Test",
        )
        adapter = HaystackAdapter(config)
        assert adapter.framework == FrameworkType.HAYSTACK

    def test_haystack_query(self):
        """Test query execution."""
        config = AdapterConfig(
            framework=FrameworkType.HAYSTACK,
            agent_id="haystack_query",
            name="Haystack Query",
        )
        adapter = HaystackAdapter(config)
        result = adapter.query("Search the documents", intent="discover")
        assert result.baseline_tokens > 0
        assert result.cost_reduction_percent > 0

    def test_haystack_discover(self):
        """Test document discovery."""
        config = AdapterConfig(
            framework=FrameworkType.HAYSTACK,
            agent_id="haystack_discover",
            name="Haystack Discover",
        )
        adapter = HaystackAdapter(config)
        sources = adapter.discover("relevant documents")
        assert "sources" in sources
        assert len(sources["sources"]) > 0


class TestMultiAgentWorkflows:
    """Test workflows across agent frameworks."""

    def test_crewai_multi_agent_coordination(self):
        """Test multi-agent task coordination."""
        config = AdapterConfig(
            framework=FrameworkType.CREWAI,
            agent_id="coordinator",
            name="Coordinator",
            optimization_strategy="balanced",
        )
        adapter = CrewAIAdapter(config)

        # Simulate multi-agent task
        result = adapter.query(
            "Analyze market, competitive, and regulatory risks",
            intent="aggregate",
            task_name="risk_analysis",
        )
        assert result.intent == "retrieve" or "aggregate" in str(result.intent)

    @pytest.mark.asyncio
    async def test_concurrent_agent_execution(self):
        """Test concurrent execution across agents."""
        crewai_config = AdapterConfig(
            framework=FrameworkType.CREWAI,
            agent_id="concurrent_crewai",
            name="Concurrent CrewAI",
        )
        crewai = CrewAIAdapter(crewai_config)

        pydantic_config = AdapterConfig(
            framework=FrameworkType.PYDANTIC_AI,
            agent_id="concurrent_pydantic",
            name="Concurrent Pydantic",
        )
        pydantic = PydanticAIAdapter(pydantic_config)

        haystack_config = AdapterConfig(
            framework=FrameworkType.HAYSTACK,
            agent_id="concurrent_haystack",
            name="Concurrent Haystack",
        )
        haystack = HaystackAdapter(haystack_config)

        # Execute concurrently
        tasks = [
            crewai.query_async("Task 1"),
            pydantic.query_async("Task 2"),
            haystack.query_async("Task 3"),
        ]
        results = await asyncio.gather(*tasks)

        assert len(results) == 3
        assert all(r.query_id is not None for r in results)


class TestRegistryIntegration:
    """Test adapter registration."""

    def test_all_adapters_registered(self):
        """Test all adapters are properly registered."""
        crewai_class = AdapterRegistry.get_adapter_class(FrameworkType.CREWAI)
        assert crewai_class == CrewAIAdapter

        pydantic_class = AdapterRegistry.get_adapter_class(FrameworkType.PYDANTIC_AI)
        assert pydantic_class == PydanticAIAdapter

        haystack_class = AdapterRegistry.get_adapter_class(FrameworkType.HAYSTACK)
        assert haystack_class == HaystackAdapter


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
