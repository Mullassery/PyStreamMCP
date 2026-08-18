"""Tests for real source discovery (pystreammcp.discovery.SourceRegistry).

Covers the registry logic directly plus the two surfaces that wrap it
(FastAPI /discover, the MCP pystreammcp_discover tool) to make sure none
of them fall back to the old fabricated placeholder behavior.
"""

from pystreammcp.discovery import SourceRegistry, Discovery, DiscoveredSource, SourceType


def test_discover_with_no_sources_returns_empty():
    registry = SourceRegistry()
    assert registry.discover("customer revenue Q3") == []


def test_discover_with_no_overlap_returns_empty_not_padded():
    registry = SourceRegistry()
    registry.register("weather_db", "hourly temperature and precipitation readings")
    assert registry.discover("customer refund policy") == []


def test_discover_ranks_by_real_token_overlap():
    registry = SourceRegistry()
    registry.register(
        "orders_db",
        "customer order history and revenue by quarter",
        type="database",
        tags=["orders", "revenue"],
    )
    registry.register(
        "support_tickets",
        "customer support ticket history",
        type="database",
        tags=["support"],
    )

    results = registry.discover("customer revenue by quarter")

    assert len(results) == 2
    # orders_db shares more tokens with the query than support_tickets
    assert results[0]["name"] == "orders_db"
    assert results[0]["relevance"] > results[1]["relevance"]
    assert "revenue" in results[0]["matched_terms"]


def test_discover_respects_limit():
    registry = SourceRegistry()
    for i in range(5):
        registry.register(f"source_{i}", "customer revenue data", tags=["revenue"])

    results = registry.discover("customer revenue", limit=2)
    assert len(results) == 2


def test_unregister_removes_source_from_results():
    registry = SourceRegistry()
    registry.register("orders_db", "customer revenue data")
    assert len(registry.discover("customer revenue")) == 1

    assert registry.unregister("orders_db") is True
    assert registry.discover("customer revenue") == []
    assert registry.unregister("orders_db") is False


def test_discover_typed_returns_real_discovered_sources():
    registry = SourceRegistry()
    registry.register("orders_db", "customer revenue data", type="table", estimated_tokens=500)

    result = registry.discover_typed(query_id="q1", context="customer revenue")

    assert isinstance(result, Discovery)
    assert len(result.discovered_sources) == 1
    source = result.discovered_sources[0]
    assert isinstance(source, DiscoveredSource)
    assert source.name == "orders_db"
    assert source.source_type == SourceType.TABLE
    assert source.estimated_tokens == 500
    assert 0.0 < source.relevance_score <= 1.0


def test_mcp_discover_tool_uses_real_registry_not_fake_source_n():
    from pystreammcp.mcp_server import PyStreamMCPServer

    server = PyStreamMCPServer(agent_id="test_agent")

    # Before registering anything, discovery must return nothing --
    # the old stub always returned fake source_0..source_4 regardless.
    empty = server.call_tool("pystreammcp_discover", {"context": "anything"})
    assert empty["sources"] == []

    server.call_tool(
        "pystreammcp_register_source",
        {"name": "orders_db", "description": "customer revenue and order data"},
    )
    result = server.call_tool(
        "pystreammcp_discover", {"context": "customer revenue"}
    )
    assert result["total_sources"] == 1
    assert result["sources"][0]["name"] == "orders_db"


def test_api_discover_endpoint_uses_real_registry():
    from fastapi.testclient import TestClient
    from pystreammcp.api import PyStreamMCPAPI

    api = PyStreamMCPAPI()
    client = TestClient(api.app)

    empty = client.post("/discover", json={"context": "anything"}).json()
    assert empty["sources"] == []

    client.post(
        "/sources",
        json={"name": "orders_db", "description": "customer revenue and order data"},
    )
    result = client.post("/discover", json={"context": "customer revenue"}).json()
    assert result["total_sources"] == 1
    assert result["sources"][0]["name"] == "orders_db"
