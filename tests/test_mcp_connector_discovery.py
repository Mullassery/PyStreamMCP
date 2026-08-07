"""Tests for real MCP federation discovery in Orchestrator (_mcp_connector.py).

Before this fix, every discovery-related Orchestrator method
(`discover_mcp_projects`, `rank_tools_by_relevance`, `manage_endpoint_federation`,
`detect_compatible_projects`) was a one-line stub returning an empty/fake
result unconditionally, regardless of what was actually configured in
pystreammcp.toml's [federation] section or reachable over the network.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

import httpx
import pytest

from pystreammcp._mcp_connector import Orchestrator


def write_config(tmp_path: Path, endpoints) -> Path:
    config_path = tmp_path / "pystreammcp.toml"
    lines = ["[federation]", "endpoints = ["]
    lines += [f'    "{e}",' for e in endpoints]
    lines.append("]")
    config_path.write_text("\n".join(lines))
    return config_path


def mock_transport(handlers):
    """handlers: dict of url -> (status_code, json_body) or Exception."""

    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        result = handlers.get(url)
        if result is None:
            return httpx.Response(404, json={"error": "not mocked"})
        if isinstance(result, Exception):
            raise result
        status_code, body = result
        return httpx.Response(status_code, json=body)

    return httpx.MockTransport(handler)


class TestDiscoverMcpProjects:
    def test_no_config_file_returns_real_empty_result(self, tmp_path):
        orch = Orchestrator(config_path=str(tmp_path / "does_not_exist.toml"))
        result = orch.discover_mcp_projects()
        assert result == {"projects": [], "total": 0}

    def test_healthy_endpoint_returns_its_real_tools(self, tmp_path):
        config_path = write_config(tmp_path, ["http://fake-statguardian:8765/mcp"])
        transport = mock_transport(
            {
                "http://fake-statguardian:8765/mcp": (
                    200,
                    {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "result": {
                            "serverInfo": {"name": "StatGuardian"},
                            "tools": [
                                {"name": "validate_schema", "description": "Validate a data schema"},
                                {"name": "check_lineage", "description": "Check data lineage"},
                            ],
                        },
                    },
                )
            }
        )
        orch = Orchestrator(config_path=str(config_path), transport=transport)

        result = orch.discover_mcp_projects()

        assert result["total"] == 1
        project = result["projects"][0]
        assert project["project_name"] == "StatGuardian"
        assert project["status"] == "healthy"
        assert project["tool_count"] == 2

    def test_unreachable_endpoint_is_reported_unavailable_not_faked(self, tmp_path):
        config_path = write_config(tmp_path, ["http://fake-down-project:9999/mcp"])
        transport = mock_transport(
            {"http://fake-down-project:9999/mcp": httpx.ConnectError("connection refused")}
        )
        orch = Orchestrator(config_path=str(config_path), transport=transport)

        result = orch.discover_mcp_projects()

        assert result["total"] == 1
        project = result["projects"][0]
        assert project["status"] == "unavailable"
        assert project["tool_count"] == 0
        assert project["error"] is not None

    def test_mixed_healthy_and_unreachable_endpoints(self, tmp_path):
        config_path = write_config(
            tmp_path, ["http://fake-up:8765/mcp", "http://fake-down:8766/mcp"]
        )
        transport = mock_transport(
            {
                "http://fake-up:8765/mcp": (
                    200,
                    {
                        "result": {
                            "serverInfo": {"name": "UpProject"},
                            "tools": [{"name": "do_thing", "description": "Does a thing"}],
                        }
                    },
                ),
                "http://fake-down:8766/mcp": httpx.ConnectError("refused"),
            }
        )
        orch = Orchestrator(config_path=str(config_path), transport=transport)

        result = orch.discover_mcp_projects()

        statuses = {p["project_name"]: p["status"] for p in result["projects"]}
        assert statuses["UpProject"] == "healthy"
        assert statuses["fake-down"] == "unavailable"

    def test_refresh_false_reuses_cached_results(self, tmp_path):
        config_path = write_config(tmp_path, ["http://fake:8765/mcp"])
        call_count = {"n": 0}

        def handler(request):
            call_count["n"] += 1
            return httpx.Response(200, json={"result": {"tools": []}})

        orch = Orchestrator(config_path=str(config_path), transport=httpx.MockTransport(handler))

        orch.discover_mcp_projects(refresh=True)
        orch.discover_mcp_projects(refresh=False)

        assert call_count["n"] == 1


class TestRankToolsByRelevance:
    def _orchestrator_with_tools(self, tmp_path):
        config_path = write_config(tmp_path, ["http://fake:8765/mcp"])
        transport = mock_transport(
            {
                "http://fake:8765/mcp": (
                    200,
                    {
                        "result": {
                            "serverInfo": {"name": "DataProject"},
                            "tools": [
                                {
                                    "name": "validate_schema",
                                    "description": "Validate a JSON schema against data",
                                },
                                {
                                    "name": "compute_lineage",
                                    "description": "Trace data lineage across pipelines",
                                },
                                {
                                    "name": "unrelated_tool",
                                    "description": "Does something else entirely",
                                },
                            ],
                        }
                    },
                )
            }
        )
        return Orchestrator(config_path=str(config_path), transport=transport)

    def test_ranks_matching_tools_above_unrelated_ones(self, tmp_path):
        orch = self._orchestrator_with_tools(tmp_path)

        result = orch.rank_tools_by_relevance("validate the schema for incoming json input")

        names = [r["tool_name"] for r in result["ranked"]]
        # Zero-relevance tools (no term overlap at all) are excluded outright.
        assert names == ["validate_schema"]

    def test_sorts_by_descending_relevance_when_multiple_tools_match(self, tmp_path):
        orch = self._orchestrator_with_tools(tmp_path)

        # Mentions both "schema" and "lineage" plus "validate_schema" by name directly.
        result = orch.rank_tools_by_relevance("validate_schema and lineage tracing across data")

        names = [r["tool_name"] for r in result["ranked"]]
        assert names[0] == "validate_schema"  # exact name match scores highest
        scores = [r["relevance"] for r in result["ranked"]]
        assert scores == sorted(scores, reverse=True)

    def test_no_task_terms_yields_no_matches(self, tmp_path):
        orch = self._orchestrator_with_tools(tmp_path)
        result = orch.rank_tools_by_relevance("")
        assert result["ranked"] == []

    def test_relevance_scores_are_bounded(self, tmp_path):
        orch = self._orchestrator_with_tools(tmp_path)
        result = orch.rank_tools_by_relevance("validate schema data lineage")
        for r in result["ranked"]:
            assert 0.0 < r["relevance"] <= 1.0


class TestManageEndpointFederation:
    def test_list_does_not_reprobe(self, tmp_path):
        config_path = write_config(tmp_path, ["http://fake:8765/mcp"])
        call_count = {"n": 0}

        def handler(request):
            call_count["n"] += 1
            return httpx.Response(200, json={"result": {"tools": []}})

        orch = Orchestrator(config_path=str(config_path), transport=httpx.MockTransport(handler))
        orch.discover_mcp_projects(refresh=True)

        result = orch.manage_endpoint_federation("list")

        assert call_count["n"] == 1  # unchanged by "list"
        assert result["status"] == "listed"
        assert len(result["endpoints"]) == 1

    def test_refresh_reprobes(self, tmp_path):
        config_path = write_config(tmp_path, ["http://fake:8765/mcp"])
        call_count = {"n": 0}

        def handler(request):
            call_count["n"] += 1
            return httpx.Response(200, json={"result": {"tools": []}})

        orch = Orchestrator(config_path=str(config_path), transport=httpx.MockTransport(handler))
        orch.discover_mcp_projects(refresh=True)

        result = orch.manage_endpoint_federation("refresh")

        assert call_count["n"] == 2
        assert result["status"] == "refreshed"

    def test_unknown_action_is_a_real_error(self, tmp_path):
        orch = Orchestrator(config_path=str(tmp_path / "none.toml"))
        result = orch.manage_endpoint_federation("bogus")
        assert result["status"] == "error"


class TestDetectCompatibleProjects:
    def test_finds_projects_with_matching_capability(self, tmp_path):
        config_path = write_config(tmp_path, ["http://fake:8765/mcp"])
        transport = mock_transport(
            {
                "http://fake:8765/mcp": (
                    200,
                    {
                        "result": {
                            "serverInfo": {"name": "SchemaProject"},
                            "tools": [
                                {"name": "validate_schema", "description": "Validate schemas"}
                            ],
                        }
                    },
                )
            }
        )
        orch = Orchestrator(config_path=str(config_path), transport=transport)

        result = orch.detect_compatible_projects("schema validation")

        assert len(result["compatible"]) == 1
        assert result["compatible"][0]["project_name"] == "SchemaProject"
        assert "validate_schema" in result["compatible"][0]["matching_tools"]

    def test_no_matching_capability_returns_empty(self, tmp_path):
        config_path = write_config(tmp_path, ["http://fake:8765/mcp"])
        transport = mock_transport(
            {
                "http://fake:8765/mcp": (
                    200,
                    {"result": {"tools": [{"name": "foo", "description": "bar"}]}},
                )
            }
        )
        orch = Orchestrator(config_path=str(config_path), transport=transport)

        result = orch.detect_compatible_projects("completely unrelated capability xyz123")

        assert result["compatible"] == []
