"""Comprehensive tests for PyStreamMCP webhook router and orchestration"""

import asyncio
import pytest
from datetime import datetime

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

from pystreammcp.webhook_router import (
    EventRouter,
    ServiceRegistry,
    ToolChainOrchestrator,
    FallbackManager,
    Tool,
    MCPEndpoint,
    ToolInvocation,
)
from pystreammcp.webhook_handlers import OrchestrationWebhookHandlers


class TestServiceRegistry:
    """Test MCP service registry and discovery"""

    def test_register_mcp_endpoint(self):
        """Test registering MCP endpoint"""
        registry = ServiceRegistry()

        endpoint = MCPEndpoint(
            project_name="statguardian",
            port=8765,
            mcp_version="2.0",
            tools=[
                Tool(
                    name="validate_data",
                    project_name="statguardian",
                    description="Validate data quality",
                ),
                Tool(
                    name="detect_drift",
                    project_name="statguardian",
                    description="Detect data drift",
                ),
            ],
        )

        registry.register_mcp_endpoint(endpoint)

        assert "statguardian" in registry.endpoints
        assert len(registry.tools_by_project["statguardian"]) == 2

    def test_find_tool(self):
        """Test finding tool in registry"""
        registry = ServiceRegistry()

        endpoint = MCPEndpoint(
            project_name="statguardian",
            port=8765,
            mcp_version="2.0",
            tools=[
                Tool(
                    name="validate_data",
                    project_name="statguardian",
                    description="Validate data",
                ),
            ],
        )

        registry.register_mcp_endpoint(endpoint)

        result = registry.find_tool("validate_data")
        assert result is not None
        project_name, found_endpoint = result
        assert project_name == "statguardian"
        assert found_endpoint.port == 8765

    def test_tool_not_found(self):
        """Test tool not found"""
        registry = ServiceRegistry()
        result = registry.find_tool("nonexistent_tool")
        assert result is None

    def test_mark_mcp_unavailable(self):
        """Test marking MCP unavailable"""
        registry = ServiceRegistry()

        endpoint = MCPEndpoint(
            project_name="statguardian",
            port=8765,
            mcp_version="2.0",
        )

        registry.register_mcp_endpoint(endpoint)
        registry.mark_mcp_unavailable("statguardian", "connection timeout")

        assert registry.endpoints["statguardian"].status == "unavailable"

    def test_update_health_metrics(self):
        """Test updating health metrics"""
        registry = ServiceRegistry()

        endpoint = MCPEndpoint(
            project_name="statguardian",
            port=8765,
            mcp_version="2.0",
        )

        registry.register_mcp_endpoint(endpoint)

        metrics = {"latency_p99_ms": 145.5, "error_rate": 0.001}
        registry.update_health_metrics("statguardian", metrics)

        assert registry.endpoints["statguardian"].health_metrics == metrics
        assert len(registry.health_history["statguardian"]) == 1

    def test_get_available_mcps(self):
        """Test getting available MCPs"""
        registry = ServiceRegistry()

        # Register healthy MCP
        healthy = MCPEndpoint(
            project_name="statguardian",
            port=8765,
            mcp_version="2.0",
            status="healthy",
        )
        registry.register_mcp_endpoint(healthy)

        # Register unavailable MCP
        unavailable = MCPEndpoint(
            project_name="pyreverseetl",
            port=8766,
            mcp_version="2.0",
            status="unavailable",
        )
        registry.register_mcp_endpoint(unavailable)

        available = registry.get_available_mcps()
        assert len(available) == 1
        assert available[0].project_name == "statguardian"


class TestToolChainOrchestrator:
    """Test tool chain orchestration and routing"""

    @pytest.mark.asyncio
    async def test_route_tool_invocation(self):
        """Test routing tool invocation"""
        registry = ServiceRegistry()
        orchestrator = ToolChainOrchestrator(registry)

        endpoint = MCPEndpoint(
            project_name="statguardian",
            port=8765,
            mcp_version="2.0",
            tools=[
                Tool(
                    name="validate_data",
                    project_name="statguardian",
                    description="Validate data",
                ),
            ],
        )
        registry.register_mcp_endpoint(endpoint)

        result = await orchestrator.route_tool_invocation(
            tool_name="validate_data",
            params={"entity_id": "customers"},
        )

        assert result["status"] == "routed"
        assert result["tool_name"] == "validate_data"
        assert result["project_name"] == "statguardian"

    @pytest.mark.asyncio
    async def test_tool_not_available(self):
        """Test tool not available"""
        registry = ServiceRegistry()
        orchestrator = ToolChainOrchestrator(registry)

        result = await orchestrator.route_tool_invocation(
            tool_name="nonexistent_tool",
            params={},
        )

        assert result["status"] == "error"
        assert "not found" in result["message"]

    @pytest.mark.asyncio
    async def test_cascade_on_result(self):
        """Test cascading results to dependent tools"""
        registry = ServiceRegistry()
        orchestrator = ToolChainOrchestrator(registry)

        # Register two tools
        endpoint = MCPEndpoint(
            project_name="statguardian",
            port=8765,
            mcp_version="2.0",
            tools=[
                Tool(name="validate_data", project_name="statguardian", description=""),
                Tool(name="alert_owners", project_name="statguardian", description=""),
            ],
        )
        registry.register_mcp_endpoint(endpoint)

        # Trigger cascade
        cascades = await orchestrator.cascade_on_result(
            tool_result={"status": "success", "entity_id": "customers"},
            cascade_triggers=[
                {
                    "tool_name": "alert_owners",
                    "trigger_condition": "on_success",
                    "params": {"severity": "high"},
                }
            ],
            invocation_id="inv_1",
        )

        assert len(cascades) == 1
        assert cascades[0]["tool_name"] == "alert_owners"

    def test_invocation_history(self):
        """Test invocation history tracking"""
        registry = ServiceRegistry()
        orchestrator = ToolChainOrchestrator(registry)

        endpoint = MCPEndpoint(
            project_name="statguardian",
            port=8765,
            mcp_version="2.0",
            tools=[
                Tool(name="validate_data", project_name="statguardian", description=""),
            ],
        )
        registry.register_mcp_endpoint(endpoint)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(
                orchestrator.route_tool_invocation(
                    tool_name="validate_data",
                    params={"entity_id": "customers"},
                )
            )
        finally:
            loop.close()

        assert len(orchestrator.invocation_history) > 0


class TestFallbackManager:
    """Test fallback management and retry logic"""

    def test_register_fallback(self):
        """Test registering fallback tools"""
        registry = ServiceRegistry()
        fallback_manager = FallbackManager(registry)

        fallback_manager.register_fallback(
            primary_tool="validate_data",
            fallback_tools=["validate_data_v2", "basic_validation"],
        )

        assert "validate_data" in fallback_manager.fallback_mappings
        assert len(fallback_manager.fallback_mappings["validate_data"]) == 2

    @pytest.mark.asyncio
    async def test_invoke_with_fallback_available(self):
        """Test invocation with fallback available"""
        registry = ServiceRegistry()
        fallback_manager = FallbackManager(registry)

        # Register primary tool
        endpoint = MCPEndpoint(
            project_name="statguardian",
            port=8765,
            mcp_version="2.0",
            tools=[
                Tool(name="validate_data", project_name="statguardian", description=""),
            ],
        )
        registry.register_mcp_endpoint(endpoint)

        result = await fallback_manager.invoke_with_fallback(
            tool_name="validate_data",
            params={},
            fallback_enabled=True,
        )

        assert result["status"] == "success"
        assert result["tool_name"] == "validate_data"

    @pytest.mark.asyncio
    async def test_invoke_with_fallback_unavailable(self):
        """Test invocation with primary unavailable, fallback available"""
        registry = ServiceRegistry()
        fallback_manager = FallbackManager(registry)

        # Register fallback tool
        endpoint = MCPEndpoint(
            project_name="pyreverseetl",
            port=8766,
            mcp_version="2.0",
            tools=[
                Tool(name="validate_data_v2", project_name="pyreverseetl", description=""),
            ],
        )
        registry.register_mcp_endpoint(endpoint)

        # Register fallback
        fallback_manager.register_fallback(
            primary_tool="validate_data",
            fallback_tools=["validate_data_v2"],
        )

        result = await fallback_manager.invoke_with_fallback(
            tool_name="validate_data",
            params={},
            fallback_enabled=True,
        )

        assert result["status"] == "fallback"
        assert result["fallback_tool"] == "validate_data_v2"

    def test_retry_queue(self):
        """Test retry queue management"""
        registry = ServiceRegistry()
        fallback_manager = FallbackManager(registry)

        fallback_manager._queue_for_retry("validate_data", {"entity_id": "customers"})

        status = fallback_manager.get_retry_queue_status()
        assert status["queue_size"] == 1
        assert "validate_data" in status["queued_tools"]


class TestEventRouter:
    """Test main event router"""

    def test_handle_mcp_available(self):
        """Test MCP available event"""
        router = EventRouter()

        event = {
            "event_type": "mcp.available",
            "data": {
                "project_name": "statguardian",
                "mcp_port": 8765,
                "mcp_version": "2.0",
                "tools": [
                    {"name": "validate_data", "description": "Validate data"},
                ],
            },
        }

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(router.route(event))
        finally:
            loop.close()

        assert result["status"] == "registered"
        assert "statguardian" in router.service_registry.endpoints

    def test_handle_mcp_unavailable(self):
        """Test MCP unavailable event"""
        router = EventRouter()

        # First register
        register_event = {
            "event_type": "mcp.available",
            "data": {
                "project_name": "statguardian",
                "mcp_port": 8765,
                "mcp_version": "2.0",
                "tools": [],
            },
        }

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(router.route(register_event))
        finally:
            loop.close()

        # Then mark unavailable
        unavailable_event = {
            "event_type": "mcp.unavailable",
            "data": {
                "project_name": "statguardian",
                "reason": "connection timeout",
            },
        }

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(router.route(unavailable_event))
        finally:
            loop.close()

        assert result["status"] == "unavailable"
        assert (
            router.service_registry.endpoints["statguardian"].status
            == "unavailable"
        )

    @pytest.mark.asyncio
    async def test_handle_tool_invoked(self):
        """Test tool invoked event"""
        router = EventRouter()

        # Register tool
        endpoint = MCPEndpoint(
            project_name="statguardian",
            port=8765,
            mcp_version="2.0",
            tools=[
                Tool(name="validate_data", project_name="statguardian", description=""),
            ],
        )
        router.service_registry.register_mcp_endpoint(endpoint)

        event = {
            "event_type": "tool.invoked",
            "data": {
                "tool_name": "validate_data",
                "invocation_id": "inv_1",
                "user_id": "user_1",
                "request_context": {"entity_id": "customers"},
            },
        }

        result = await router.route(event)

        assert result["status"] == "routed"
        assert result["tool_name"] == "validate_data"

    def test_get_router_status(self):
        """Test getting router status"""
        router = EventRouter()

        endpoint = MCPEndpoint(
            project_name="statguardian",
            port=8765,
            mcp_version="2.0",
            tools=[
                Tool(name="validate_data", project_name="statguardian", description=""),
            ],
        )
        router.service_registry.register_mcp_endpoint(endpoint)

        status = router.get_status()

        assert status["status"] == "healthy"
        assert status["registry"]["total_mcps"] == 1
        assert status["registry"]["total_tools"] == 1


class TestOrchestrationWebhookHandlers:
    """Test orchestration webhook event handlers"""

    @pytest.mark.asyncio
    async def test_handle_mcp_available(self):
        """Test MCP available handler"""
        router = EventRouter()
        handlers = OrchestrationWebhookHandlers(router)

        event = {
            "event_type": "mcp.available",
            "data": {
                "project_name": "statguardian",
                "mcp_port": 8765,
                "mcp_version": "2.0",
                "tools": [
                    {"name": "validate_data", "description": "Validate data"},
                ],
                "health_metrics": {"latency_p99_ms": 145.5},
            },
        }

        result = await handlers.handle_mcp_available(event)

        assert result["status"] == "success"
        assert result["project_name"] == "statguardian"
        assert result["tools_registered"] == 1

    @pytest.mark.asyncio
    async def test_handle_mcp_unavailable(self):
        """Test MCP unavailable handler"""
        router = EventRouter()
        handlers = OrchestrationWebhookHandlers(router)

        event = {
            "event_type": "mcp.unavailable",
            "data": {
                "project_name": "statguardian",
                "reason": "connection timeout",
                "affected_tools": ["validate_data", "detect_drift"],
                "is_temporary": False,
            },
        }

        result = await handlers.handle_mcp_unavailable(event)

        assert result["status"] == "success"
        assert result["affected_tools"] == 2

    @pytest.mark.asyncio
    async def test_handle_tool_invoked(self):
        """Test tool invoked handler"""
        router = EventRouter()
        handlers = OrchestrationWebhookHandlers(router)

        # Register tool
        endpoint = MCPEndpoint(
            project_name="statguardian",
            port=8765,
            mcp_version="2.0",
            tools=[
                Tool(name="validate_data", project_name="statguardian", description=""),
            ],
        )
        router.service_registry.register_mcp_endpoint(endpoint)

        event = {
            "event_type": "tool.invoked",
            "data": {
                "tool_name": "validate_data",
                "invocation_id": "inv_1",
                "user_id": "user_1",
                "request_context": {"entity_id": "customers"},
                "orchestration_context": {
                    "chain_id": "chain_1",
                    "position_in_chain": 0,
                    "total_chain_length": 1,
                },
            },
        }

        result = await handlers.handle_tool_invoked(event)

        assert result["status"] == "success"
        assert result["tool_name"] == "validate_data"

    @pytest.mark.asyncio
    async def test_handle_tool_result(self):
        """Test tool result handler"""
        router = EventRouter()
        handlers = OrchestrationWebhookHandlers(router)

        # Register tools
        endpoint = MCPEndpoint(
            project_name="statguardian",
            port=8765,
            mcp_version="2.0",
            tools=[
                Tool(name="validate_data", project_name="statguardian", description=""),
                Tool(name="alert_owners", project_name="statguardian", description=""),
            ],
        )
        router.service_registry.register_mcp_endpoint(endpoint)

        event = {
            "event_type": "tool.result",
            "data": {
                "invocation_id": "inv_1",
                "tool_name": "validate_data",
                "result": {"status": "success", "entity_id": "customers"},
                "cascade_triggers": [
                    {
                        "tool_name": "alert_owners",
                        "trigger_condition": "on_success",
                    }
                ],
            },
        }

        result = await handlers.handle_tool_result(event)

        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_handle_health_update(self):
        """Test health update handler"""
        router = EventRouter()
        handlers = OrchestrationWebhookHandlers(router)

        # Register endpoint
        endpoint = MCPEndpoint(
            project_name="statguardian",
            port=8765,
            mcp_version="2.0",
        )
        router.service_registry.register_mcp_endpoint(endpoint)

        event = {
            "event_type": "mcp.health_update",
            "data": {
                "project_name": "statguardian",
                "previous_status": "healthy",
                "metrics": {
                    "latency_p99_ms": 145.5,
                    "error_rate": 0.001,
                    "tool_availability": 0.999,
                },
            },
        }

        result = await handlers.handle_health_update(event)

        assert result["status"] == "success"
        assert result["project_name"] == "statguardian"

    @pytest.mark.asyncio
    async def test_dispatch_handler(self):
        """Test handler dispatch"""
        router = EventRouter()
        handlers = OrchestrationWebhookHandlers(router)

        endpoint = MCPEndpoint(
            project_name="statguardian",
            port=8765,
            mcp_version="2.0",
            tools=[
                Tool(name="validate_data", project_name="statguardian", description=""),
            ],
        )
        router.service_registry.register_mcp_endpoint(endpoint)

        event = {
            "event_type": "mcp.available",
            "data": {
                "project_name": "statguardian",
                "mcp_port": 8765,
                "mcp_version": "2.0",
                "tools": [
                    {"name": "validate_data", "description": "Validate data"},
                ],
            },
        }

        result = await handlers.dispatch(event)

        assert result["status"] == "success"


class TestIntegration:
    """Integration tests for orchestration system"""

    @pytest.mark.asyncio
    async def test_end_to_end_orchestration(self):
        """Test end-to-end orchestration flow"""
        router = EventRouter()
        handlers = OrchestrationWebhookHandlers(router)

        # 1. Register MCP endpoint
        register_event = {
            "event_type": "mcp.available",
            "data": {
                "project_name": "statguardian",
                "mcp_port": 8765,
                "mcp_version": "2.0",
                "tools": [
                    {"name": "validate_data", "description": "Validate data"},
                    {"name": "alert_owners", "description": "Alert data owners"},
                ],
            },
        }

        result = await handlers.dispatch(register_event)
        assert result["status"] == "success"

        # 2. Invoke tool
        invoke_event = {
            "event_type": "tool.invoked",
            "data": {
                "tool_name": "validate_data",
                "invocation_id": "inv_1",
                "user_id": "user_1",
                "request_context": {"entity_id": "customers"},
            },
        }

        result = await handlers.dispatch(invoke_event)
        assert result["status"] == "success"

        # 3. Process result with cascade
        result_event = {
            "event_type": "tool.result",
            "data": {
                "invocation_id": "inv_1",
                "tool_name": "validate_data",
                "result": {"status": "success", "entity_id": "customers"},
                "cascade_triggers": [
                    {
                        "tool_name": "alert_owners",
                        "trigger_condition": "on_success",
                    }
                ],
            },
        }

        result = await handlers.dispatch(result_event)
        assert result["status"] == "success"

        # 4. Verify registry state
        status = router.get_status()
        assert status["registry"]["total_mcps"] == 1
        assert status["registry"]["total_tools"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
