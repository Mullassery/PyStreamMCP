"""Tests for OKF discovery exporter."""

import tempfile
from pathlib import Path

import pytest

from pystreammcp.okf_core import OKFCatalog, OKFDocType
from pystreammcp.okf_discovery import (
    DiscoveryOKFExporter,
    MCPSystemToOKF,
    MCPToolToOKF,
)


@pytest.fixture
def temp_catalog():
    """Create temporary catalog for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield OKFCatalog(Path(tmpdir))


class TestMCPSystemToOKF:
    """Test MCP system to OKF conversion."""

    def test_render_system(self):
        """Test rendering system to OKF."""
        content, metadata = MCPSystemToOKF.render(
            system_id="postgres-prod",
            name="PostgreSQL Production",
            description="Production database",
            tools_count=45,
            cost_per_query=0.02,
            latency_p99_ms=150
        )

        assert "PostgreSQL Production" in content
        assert "45" in content
        assert "0.0200" in content
        assert metadata["system_id"] == "postgres-prod"
        assert metadata["tools_count"] == 45

    def test_render_system_with_tags(self):
        """Test rendering system with custom tags."""
        content, metadata = MCPSystemToOKF.render(
            system_id="elastic",
            name="Elasticsearch",
            description="Search engine",
            tools_count=30,
            metadata={"tags": ["search", "analytics"]}
        )

        assert "search" in metadata["tags"]
        assert "analytics" in metadata["tags"]


class TestMCPToolToOKF:
    """Test MCP tool to OKF conversion."""

    def test_render_tool(self):
        """Test rendering tool to OKF."""
        content, metadata = MCPToolToOKF.render(
            tool_id="search_customers",
            name="Search Customers",
            description="Search by name",
            system_id="postgres-prod",
            cost=0.01,
            latency_p95_ms=50,
            parameters={
                "query": {"type": "string", "description": "Search term"},
                "limit": {"type": "integer", "description": "Result limit"}
            },
            returns={
                "customer_id": {"type": "string"},
                "name": {"type": "string"}
            }
        )

        assert "Search Customers" in content
        assert "postgres-prod" in content
        assert "0.0100" in content
        assert metadata["tool_id"] == "search_customers"
        assert metadata["parameter_count"] == 2

    def test_render_tool_minimal(self):
        """Test rendering tool with minimal params."""
        content, metadata = MCPToolToOKF.render(
            tool_id="test_tool",
            name="Test Tool",
            description="A test",
            system_id="test_sys"
        )

        assert "Test Tool" in content
        assert metadata["tool_id"] == "test_tool"


class TestDiscoveryOKFExporter:
    """Test discovery exporter integration."""

    def test_export_system(self, temp_catalog):
        """Test exporting system to catalog."""
        exporter = DiscoveryOKFExporter(temp_catalog)

        path = exporter.export_system(
            system_id="postgres-prod",
            name="PostgreSQL Production",
            description="Production database",
            tools_count=45,
            cost_per_query=0.02
        )

        assert Path(path).exists()
        assert "systems" in path

        # Verify in catalog
        systems = temp_catalog.search_systems("PostgreSQL")
        assert len(systems) == 1

    def test_export_tool(self, temp_catalog):
        """Test exporting tool to catalog."""
        exporter = DiscoveryOKFExporter(temp_catalog)

        path = exporter.export_tool(
            tool_id="search_customers",
            name="Search Customers",
            description="Search customer database",
            system_id="postgres-prod",
            cost=0.01,
            latency_p95_ms=50
        )

        assert Path(path).exists()
        assert "tools" in path

        # Verify in catalog
        tools = temp_catalog.search_tools()
        assert len(tools) == 1

    def test_export_query_plan(self, temp_catalog):
        """Test exporting query plan to catalog."""
        exporter = DiscoveryOKFExporter(temp_catalog)

        steps = [
            {"description": "Search metadata", "cost": 0.005, "latency_ms": 50, "token_cost": 500},
            {"description": "Fetch data", "cost": 0.01, "latency_ms": 100, "token_cost": 1200},
        ]

        path = exporter.export_query_plan(
            plan_id="customer_360",
            objective="Retrieve full customer profile",
            steps=steps,
            estimated_token_savings=65.0,
            estimated_cost_savings=0.50
        )

        assert Path(path).exists()
        assert "query_plans" in path

        # Verify in catalog
        plans = temp_catalog.find_by_type(OKFDocType.QUERY_PLAN)
        assert len(plans) == 1

    def test_full_export_workflow(self, temp_catalog):
        """Test full discovery export workflow."""
        exporter = DiscoveryOKFExporter(temp_catalog)

        # Export system
        sys_path = exporter.export_system(
            system_id="postgres",
            name="PostgreSQL",
            description="Primary database",
            tools_count=20,
            cost_per_query=0.01
        )

        # Export tool under that system
        tool_path = exporter.export_tool(
            tool_id="query_users",
            name="Query Users",
            description="Get user data",
            system_id="postgres",
            cost=0.01
        )

        # Export optimization plan
        plan_path = exporter.export_query_plan(
            plan_id="user_profile",
            objective="Get user profile",
            steps=[{"description": "Query", "cost": 0.01, "latency_ms": 50}],
            estimated_token_savings=40.0
        )

        # Verify all exported
        assert Path(sys_path).exists()
        assert Path(tool_path).exists()
        assert Path(plan_path).exists()

        # Verify searchable
        systems = temp_catalog.search_systems()
        assert len(systems) >= 1

        tools = temp_catalog.search_tools()
        assert len(tools) >= 1

        plans = temp_catalog.find_by_type(OKFDocType.QUERY_PLAN)
        assert len(plans) >= 1
