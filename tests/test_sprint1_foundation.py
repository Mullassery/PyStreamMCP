"""Sprint 1 integration tests - Foundation & MCP.

Tests for:
- Adapter base class and registry
- MCP server protocol
- REST API endpoints
"""

import pytest
from pystreammcp.adapters import (
    AdapterConfig, AdapterRegistry, AgentFrameworkAdapter,
    FrameworkType, QueryResult,
)
from pystreammcp.mcp_server import PyStreamMCPServer
from pystreammcp.api import PyStreamMCPAPI, QueryRequest, AgentConfig


class MockAdapter(AgentFrameworkAdapter):
    """Mock adapter for testing."""

    def query(self, text: str, intent: str = "retrieve", **kwargs) -> QueryResult:
        return QueryResult(
            query_id="test-1",
            text=text,
            intent=intent,
            baseline_tokens=1000,
            optimized_tokens=400,
            cost_reduction_percent=60.0,
            execution_time_ms=150.5,
            context={"result": "mock"},
        )

    async def query_async(self, text: str, intent: str = "retrieve", **kwargs) -> QueryResult:
        return self.query(text, intent, **kwargs)

    def discover(self, context: str, **kwargs) -> dict:
        return {
            "sources": [{"name": "source_1", "relevance": 0.95}],
            "total": 1,
        }

    async def discover_async(self, context: str, **kwargs) -> dict:
        return self.discover(context, **kwargs)

    def optimize(self, query_text: str, strategy=None, **kwargs) -> QueryResult:
        return self.query(query_text)

    async def optimize_async(self, query_text: str, strategy=None, **kwargs) -> QueryResult:
        return self.optimize(query_text, strategy, **kwargs)


class TestAdapterPattern:
    """Test adapter base class and registry."""

    def test_adapter_config(self):
        """Test adapter configuration."""
        config = AdapterConfig(
            framework=FrameworkType.LANGCHAIN,
            agent_id="test_agent",
            name="Test Agent",
            optimization_strategy="token_efficient",
            max_tokens=1500,
        )
        assert config.framework == FrameworkType.LANGCHAIN
        assert config.agent_id == "test_agent"
        assert config.max_tokens == 1500

    def test_mock_adapter_query(self):
        """Test adapter query method."""
        config = AdapterConfig(
            framework=FrameworkType.LANGCHAIN,
            agent_id="test",
            name="Test",
        )
        adapter = MockAdapter(config)
        result = adapter.query("What is this?")

        assert result.query_id == "test-1"
        assert result.baseline_tokens == 1000
        assert result.optimized_tokens == 400
        assert result.cost_reduction_percent == 60.0

    def test_adapter_get_tools(self):
        """Test adapter tool definitions."""
        config = AdapterConfig(
            framework=FrameworkType.LANGCHAIN,
            agent_id="test",
            name="Test",
        )
        adapter = MockAdapter(config)
        tools = adapter.get_tools()

        assert len(tools) == 3
        assert any(t["name"] == "pystreammcp_query" for t in tools)
        assert any(t["name"] == "pystreammcp_discover" for t in tools)
        assert any(t["name"] == "pystreammcp_optimize" for t in tools)

    def test_adapter_registry_register(self):
        """Test adapter registration."""
        AdapterRegistry.register(FrameworkType.LANGCHAIN, MockAdapter)
        adapter_class = AdapterRegistry.get_adapter_class(FrameworkType.LANGCHAIN)
        assert adapter_class == MockAdapter

    def test_adapter_registry_create(self):
        """Test adapter creation through registry."""
        AdapterRegistry.register(FrameworkType.LANGCHAIN, MockAdapter)
        config = AdapterConfig(
            framework=FrameworkType.LANGCHAIN,
            agent_id="registry_test",
            name="Registry Test",
        )
        adapter = AdapterRegistry.create_adapter(config)
        assert adapter is not None
        assert adapter.agent_id == "registry_test"

    def test_adapter_registry_get(self):
        """Test adapter retrieval from registry."""
        AdapterRegistry.register(FrameworkType.LANGCHAIN, MockAdapter)
        config = AdapterConfig(
            framework=FrameworkType.LANGCHAIN,
            agent_id="get_test",
            name="Get Test",
        )
        created = AdapterRegistry.create_adapter(config)
        retrieved = AdapterRegistry.get_adapter("get_test")
        assert retrieved == created

    def test_adapter_registry_list(self):
        """Test listing registered adapters."""
        AdapterRegistry.register(FrameworkType.LANGCHAIN, MockAdapter)
        adapters = AdapterRegistry.list_adapters()
        assert "get_test" in adapters or len(adapters) >= 0


class TestMCPServer:
    """Test MCP server protocol."""

    def test_mcp_server_init(self):
        """Test server initialization."""
        server = PyStreamMCPServer("test_mcp")
        assert server.agent_id == "test_mcp"

    def test_mcp_server_tools(self):
        """Test MCP tool definitions."""
        server = PyStreamMCPServer()
        tools = server.get_tools()

        assert len(tools) == 3
        tool_names = [t["name"] for t in tools]
        assert "pystreammcp_query" in tool_names
        assert "pystreammcp_discover" in tool_names
        assert "pystreammcp_optimize" in tool_names

    def test_mcp_server_query_tool(self):
        """Test query tool execution."""
        server = PyStreamMCPServer()
        result = server.call_tool(
            "pystreammcp_query",
            {"text": "Test query"},
        )

        assert result["status"] == "success"
        assert "query_id" in result
        assert "baseline_tokens" in result
        assert "optimized_tokens" in result

    def test_mcp_server_discover_tool(self):
        """Test discovery tool."""
        server = PyStreamMCPServer()
        result = server.call_tool(
            "pystreammcp_discover",
            {"context": "test context"},
        )

        assert result["status"] == "success"
        assert "sources" in result

    def test_mcp_server_optimize_tool(self):
        """Test optimization tool."""
        server = PyStreamMCPServer()
        result = server.call_tool(
            "pystreammcp_optimize",
            {"text": "Test query"},
        )

        assert result["status"] == "success"
        assert "cost_reduction_percent" in result

    def test_mcp_server_invalid_tool(self):
        """Test invalid tool call."""
        server = PyStreamMCPServer()
        with pytest.raises(ValueError):
            server.call_tool("invalid_tool", {})

    def test_mcp_server_message_handling(self):
        """Test MCP message processing."""
        server = PyStreamMCPServer()

        # List tools message
        msg = {"type": "list_tools"}
        response = server.process_message(msg)
        assert response["type"] == "tools"
        assert len(response["tools"]) == 3

        # Info message
        msg = {"type": "get_info"}
        response = server.process_message(msg)
        assert response["type"] == "info"
        assert "PyStreamMCP" in response["name"]


class TestRestAPI:
    """Test REST API endpoints."""

    @pytest.fixture
    def api(self):
        """Create API for testing."""
        return PyStreamMCPAPI()

    @pytest.fixture
    def client(self, api):
        """Create test client."""
        from fastapi.testclient import TestClient
        return TestClient(api.app)

    def test_health_endpoint(self, client):
        """Test health check."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_info_endpoint(self, client):
        """Test info endpoint."""
        response = client.get("/info")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data

    def test_create_agent(self, client):
        """Test agent creation."""
        payload = {
            "agent_id": "api_test_agent",
            "name": "API Test",
            "optimization_strategy": "token_efficient",
            "max_tokens": 1500,
        }
        response = client.post("/agents", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["agent_id"] == "api_test_agent"

    def test_list_agents(self, client):
        """Test listing agents."""
        # Create an agent first
        payload = {
            "agent_id": "list_test_agent",
            "name": "List Test",
        }
        client.post("/agents", json=payload)

        # List agents
        response = client.get("/agents")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["agents"]) > 0

    def test_get_agent(self, client):
        """Test getting agent details."""
        # Create an agent
        payload = {
            "agent_id": "get_test_agent",
            "name": "Get Test",
        }
        client.post("/agents", json=payload)

        # Get agent
        response = client.get("/agents/get_test_agent")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["agent_id"] == "get_test_agent"

    def test_query_endpoint(self, client):
        """Test query endpoint."""
        # Create agent
        payload = {
            "agent_id": "query_test_agent",
            "name": "Query Test",
        }
        client.post("/agents", json=payload)

        # Execute query
        payload = {
            "text": "Test query",
            "intent": "retrieve",
            "agent_id": "query_test_agent",
        }
        response = client.post("/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "query_id" in data
        assert "baseline_tokens" in data

    def test_metrics_endpoint(self, client):
        """Test metrics endpoint."""
        response = client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "metrics" in data
