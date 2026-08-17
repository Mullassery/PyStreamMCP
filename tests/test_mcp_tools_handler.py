"""Tests proving PyStreamMCPHandler (the MCP-exposed tool surface in
_mcp_tools.py) actually calls into the real Orchestrator, instead of
returning hardcoded fixture data disconnected from it.

Before this fix, every PyStreamMCPHandler method ignored
`self.orchestrator` entirely and returned a fixed dict (e.g. a 7-project
fixture list for discover_mcp_projects regardless of what was actually
configured or reachable). These tests exercise the handler through a real
Orchestrator/EventRouter and assert the response reflects real state,
including the "nothing is configured/discovered yet" case, which a
fixture-backed handler could never represent.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

import pytest

from pystreammcp._mcp_connector import Orchestrator
from pystreammcp._mcp_tools import PyStreamMCPHandler
from pystreammcp.webhook_router import MCPEndpoint, Tool


@pytest.fixture
def orchestrator(tmp_path):
    return Orchestrator(config_path=str(tmp_path / "does_not_exist.toml"))


@pytest.fixture
def handler(orchestrator):
    return PyStreamMCPHandler(orchestrator)


class TestDiscoverMcpProjects:
    @pytest.mark.asyncio
    async def test_no_config_returns_real_empty_result_not_fixture(self, handler):
        """A fixture-backed handler always claimed 7 projects; the real
        Orchestrator has nothing to report when nothing is configured."""
        result = await handler.discover_mcp_projects()
        assert result == {"projects": [], "total": 0}

    @pytest.mark.asyncio
    async def test_filter_by_capability_uses_real_detection(self, handler, orchestrator):
        endpoint = MCPEndpoint(
            project_name="demo",
            port=9001,
            mcp_version="2.0",
            tools=[Tool(name="validate_schema", project_name="demo", description="Validate a schema")],
        )
        orchestrator.event_router.service_registry.register_mcp_endpoint(endpoint)
        # detect_compatible_projects operates on orchestrator.registered_projects
        # (federation discovery), not the event_router registry, so seed that too.
        from pystreammcp._mcp_connector import DiscoveredProject

        orchestrator.registered_projects["demo"] = DiscoveredProject(
            project_name="demo",
            endpoint="http://localhost:9001/mcp",
            status="healthy",
            tools=[{"name": "validate_schema", "description": "Validate a schema"}],
        )

        result = await handler.discover_mcp_projects(filter_by_capability="schema validation")
        assert result["total"] == 1
        assert result["filtered_by_capability"] == "schema validation"


class TestRouteToolInvocation:
    @pytest.mark.asyncio
    async def test_unknown_tool_reports_real_failure_not_fake_success(self, handler):
        """The old fixture handler claimed every tool routed successfully
        to a hardcoded "statguardian" endpoint that may not even exist.
        With no fallback registered either, the real FallbackManager
        correctly reports "unavailable" rather than a fabricated route."""
        result = await handler.route_tool_invocation(tool_name="does_not_exist")
        assert result["status"] in ("error", "unavailable")

    @pytest.mark.asyncio
    async def test_registered_tool_routes_to_its_real_project(self, handler, orchestrator):
        endpoint = MCPEndpoint(
            project_name="demo",
            port=9002,
            mcp_version="2.0",
            tools=[Tool(name="do_thing", project_name="demo", description="does a thing")],
        )
        orchestrator.event_router.service_registry.register_mcp_endpoint(endpoint)

        result = await handler.route_tool_invocation(tool_name="do_thing")
        assert result["status"] == "routed"
        assert result["project_name"] == "demo"
        assert result["endpoint"] == "http://localhost:9002"


class TestListServiceEndpoints:
    @pytest.mark.asyncio
    async def test_empty_registry_is_genuinely_empty(self, handler):
        result = await handler.list_service_endpoints()
        assert result == {"status": "success", "endpoints": [], "total": 0, "healthy_count": 0}

    @pytest.mark.asyncio
    async def test_reflects_real_registered_endpoint(self, handler, orchestrator):
        endpoint = MCPEndpoint(project_name="demo", port=9003, mcp_version="2.0", tools=[])
        orchestrator.event_router.service_registry.register_mcp_endpoint(endpoint)

        result = await handler.list_service_endpoints()
        assert result["total"] == 1
        assert result["endpoints"][0]["project"] == "demo"
        assert result["endpoints"][0]["port"] == 9003


class TestOrchestrateCrossMcpWorkflow:
    @pytest.mark.asyncio
    async def test_actually_executes_not_just_plans(self, handler, orchestrator):
        """The old fixture handler returned status="orchestrating" with
        every stage hardcoded to "pending" — it never actually ran
        anything. This asserts real per-stage execution results."""
        endpoint = MCPEndpoint(
            project_name="demo",
            port=9004,
            mcp_version="2.0",
            tools=[Tool(name="step_one", project_name="demo", description="")],
        )
        orchestrator.event_router.service_registry.register_mcp_endpoint(endpoint)

        result = await handler.orchestrate_cross_mcp_workflow(
            workflow_id="wf_test", tool_sequence=["step_one"]
        )
        assert result["status"] == "completed"
        assert result["stages"][0]["result"]["status"] == "routed"

    @pytest.mark.asyncio
    async def test_fail_fast_stops_on_first_missing_tool(self, handler):
        result = await handler.orchestrate_cross_mcp_workflow(
            workflow_id="wf_fail",
            tool_sequence=["missing_a", "missing_b"],
            error_handling="fail_fast",
        )
        assert result["status"] == "failed"
        assert result["failed_at_stage"] == 1
        assert len(result["stages"]) == 1  # never attempted the second tool


class TestHandleCrossDatabaseJoin:
    @pytest.mark.asyncio
    async def test_reports_not_implemented_not_fabricated_row_count(self, handler):
        """The old fixture handler always claimed 5432 rows matched in
        850ms for a join that never actually ran."""
        result = await handler.handle_cross_database_join("proj_a.customers", "proj_b.orders", "customer_id")
        assert result["status"] == "not_implemented"
        assert "rows_matched" not in result


class TestOptimizeCrossProjectQuery:
    @pytest.mark.asyncio
    async def test_reduction_derives_from_actual_query_text(self, handler):
        """The old fixture handler returned exactly 72.0%/68.0% regardless
        of query content. This should vary with real input."""
        short = await handler.optimize_cross_project_query(
            original_query="find recent customer orders"
        )
        long = await handler.optimize_cross_project_query(
            original_query="find all customer orders placed in the last 90 days across regions"
        )
        assert short["baseline_tokens"] < long["baseline_tokens"]
        assert short["optimized_tokens"] < short["baseline_tokens"]
        assert long["optimized_tokens"] < long["baseline_tokens"]


class TestCacheManagement:
    @pytest.mark.asyncio
    async def test_stats_reflect_real_empty_cache_not_fabricated_numbers(self, handler):
        """The old fixture handler always claimed 2540.0MB / 1250 entries
        / 72.3% hit rate for a cache that was never actually implemented."""
        result = await handler.cache_management(action="stats")
        assert result["entries"] == 0
        assert result["hits"] == 0
        assert result["misses"] == 0
        assert "cache_size_mb" not in result  # no fabricated figure

    @pytest.mark.asyncio
    async def test_unknown_action_is_a_real_error(self, handler):
        result = await handler.cache_management(action="bogus")
        assert result["status"] == "error"
