"""REST API server for PyStreamMCP - integrates with workflow tools and orchestration webhooks."""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from pystreammcp import Agent
from .webhook_router import EventRouter, MCPEndpoint, Tool
from .webhook_handlers import OrchestrationWebhookHandlers


class PyStreamMCPServer:
    """REST API server for workflow integration and MCP orchestration."""

    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        """Initialize server."""
        self.host = host
        self.port = port
        self.agents: Dict[str, Agent] = {}

        # Initialize orchestration system
        self.event_router = EventRouter()
        self.webhook_handlers = OrchestrationWebhookHandlers(self.event_router, self)
        self.webhook_configs: Dict[str, Dict[str, Any]] = {}  # webhook_id -> config

    def create_agent(self, agent_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create an agent."""
        agent = Agent(
            agent_id=agent_id,
            name=config.get("name", agent_id),
            optimization_strategy=config.get("optimization_strategy", "balanced"),
            max_tokens=config.get("max_tokens", 2000),
        )
        self.agents[agent_id] = agent

        return {
            "status": "success",
            "agent_id": agent_id,
            "message": f"Agent {agent_id} created",
        }

    def query(
        self, agent_id: str, text: str, intent: str = "retrieve"
    ) -> Dict[str, Any]:
        """Execute a query."""
        if agent_id not in self.agents:
            return {"status": "error", "message": f"Agent {agent_id} not found"}

        agent = self.agents[agent_id]
        result = agent.query(text)

        return {
            "status": "success",
            "query_id": result.query_id,
            "query_text": text,
            "intent": intent,
            "baseline_tokens": result.baseline_tokens,
            "optimized_tokens": result.optimized_tokens,
            "cost_reduction_percent": result.cost_reduction_percent,
            "cost_saved": (result.baseline_tokens - result.optimized_tokens) * 0.00001,
            "execution_time_ms": result.execution_time_ms,
            "meets_target": 60 <= result.cost_reduction_percent <= 75,
        }

    def batch_query(self, agent_id: str, queries: List[str]) -> Dict[str, Any]:
        """Execute multiple queries."""
        if agent_id not in self.agents:
            return {"status": "error", "message": f"Agent {agent_id} not found"}

        agent = self.agents[agent_id]
        results = []
        total_saved = 0.0

        for query_text in queries:
            result = agent.query(query_text)
            results.append(
                {
                    "query": query_text,
                    "cost_reduction_percent": result.cost_reduction_percent,
                    "cost_saved": (result.baseline_tokens - result.optimized_tokens)
                    * 0.00001,
                }
            )
            total_saved += (result.baseline_tokens - result.optimized_tokens) * 0.00001

        return {
            "status": "success",
            "queries_processed": len(queries),
            "results": results,
            "total_cost_saved": total_saved,
        }

    def get_metrics(self, agent_id: str) -> Dict[str, Any]:
        """Get agent metrics."""
        if agent_id not in self.agents:
            return {"status": "error", "message": f"Agent {agent_id} not found"}

        agent = self.agents[agent_id]
        metrics = agent.get_metrics()

        return {
            "status": "success",
            "agent_id": agent_id,
            "metrics": metrics,
        }

    def health_check(self) -> Dict[str, Any]:
        """Health check endpoint."""
        registry = self.event_router.get_status()
        return {
            "status": "healthy",
            "agents_count": len(self.agents),
            "version": "2.0.0",
            "webhooks_count": len(self.webhook_configs),
            "registered_mcps": registry.get("registry", {}).get("total_mcps", 0),
            "healthy_mcps": registry.get("registry", {}).get("healthy_mcps", 0),
        }

    def list_agents(self) -> Dict[str, Any]:
        """List all agents."""
        return {
            "status": "success",
            "agents": list(self.agents.keys()),
            "count": len(self.agents),
        }

    # Orchestration and webhook methods
    def register_orchestration_webhook(
        self,
        webhook_id: str,
        url: str,
        events: List[str],
        secret_key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Register orchestration webhook"""
        self.webhook_configs[webhook_id] = {
            "webhook_id": webhook_id,
            "url": url,
            "events": events,
            "secret_key": secret_key,
            "headers": headers or {},
            "active": True,
            "created_at": datetime.utcnow().isoformat(),
        }
        return {
            "status": "success",
            "webhook_id": webhook_id,
            "message": f"Orchestration webhook registered for events: {', '.join(events)}",
            "created_at": self.webhook_configs[webhook_id]["created_at"],
        }

    def unregister_orchestration_webhook(self, webhook_id: str) -> Dict[str, Any]:
        """Unregister orchestration webhook"""
        if webhook_id in self.webhook_configs:
            del self.webhook_configs[webhook_id]
            return {
                "status": "success",
                "webhook_id": webhook_id,
                "message": "Orchestration webhook unregistered",
            }
        return {
            "status": "error",
            "webhook_id": webhook_id,
            "message": "Webhook not found",
        }

    def list_orchestration_webhooks(self) -> Dict[str, Any]:
        """List registered orchestration webhooks"""
        return {
            "status": "success",
            "webhooks": list(self.webhook_configs.values()),
            "count": len(self.webhook_configs),
        }

    def emit_orchestration_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Emit orchestration webhook event"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(self.event_router.route(event_data))
            finally:
                loop.close()

            if result.get("status") != "unhandled":
                # Dispatch to handlers
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    handler_result = loop.run_until_complete(
                        self.webhook_handlers.dispatch(event_data)
                    )
                finally:
                    loop.close()

                return {
                    "status": "success",
                    "event_type": event_data.get("event_type"),
                    "router_result": result,
                    "handler_result": handler_result,
                }

            return {
                "status": "skipped",
                "event_type": event_data.get("event_type"),
                "message": "Unhandled event type",
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def register_mcp_endpoint(
        self,
        project_name: str,
        port: int,
        mcp_version: str = "2.0",
        tools: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Register MCP endpoint"""
        endpoint = MCPEndpoint(
            project_name=project_name,
            port=port,
            mcp_version=mcp_version,
            tools=[
                Tool(
                    name=t.get("name"),
                    project_name=project_name,
                    description=t.get("description", ""),
                    input_schema=t.get("input_schema", {}),
                    output_schema=t.get("output_schema", {}),
                )
                for t in (tools or [])
            ],
        )
        self.event_router.service_registry.register_mcp_endpoint(endpoint)
        return {
            "status": "success",
            "project_name": project_name,
            "port": port,
            "tools_registered": len(tools or []),
        }

    def list_mcp_services(self) -> Dict[str, Any]:
        """List all MCP services"""
        registry = self.event_router.get_status()
        return {
            "status": "success",
            "registry": registry.get("registry", {}),
        }

    def get_tool_routing(self, tool_name: str) -> Dict[str, Any]:
        """Get tool routing information"""
        result = self.event_router.service_registry.find_tool(tool_name)
        if result:
            project_name, endpoint = result
            return {
                "status": "success",
                "tool_name": tool_name,
                "project_name": project_name,
                "endpoint": f"http://localhost:{endpoint.port}",
                "health_status": endpoint.status,
            }
        return {
            "status": "not_found",
            "tool_name": tool_name,
            "message": f"Tool {tool_name} not found in any available MCP",
        }

    def register_fallback_tool(
        self, primary_tool: str, fallback_tools: List[str]
    ) -> Dict[str, Any]:
        """Register fallback tools for primary tool"""
        self.event_router.fallback_manager.register_fallback(
            primary_tool=primary_tool,
            fallback_tools=fallback_tools,
        )
        return {
            "status": "success",
            "primary_tool": primary_tool,
            "fallback_tools": fallback_tools,
            "message": f"Fallbacks registered for {primary_tool}",
        }

    def get_orchestration_status(self) -> Dict[str, Any]:
        """Get orchestration system status"""
        status = self.event_router.get_status()
        return {
            "status": "success",
            "orchestration": status,
            "webhooks": len(self.webhook_configs),
            "timestamp": datetime.utcnow().isoformat(),
        }


# Flask integration for REST API
def create_flask_app(server: Optional[PyStreamMCPServer] = None):
    """Create Flask app for REST API."""
    try:
        from flask import Flask, request, jsonify
    except ImportError:
        raise ImportError(
            "Flask is required for REST API. Install with: pip install flask"
        )

    app = Flask(__name__)
    srv = server or PyStreamMCPServer()

    @app.route("/health", methods=["GET"])
    def health():
        """Health check."""
        return jsonify(srv.health_check())

    @app.route("/agents", methods=["GET"])
    def list_agents():
        """List all agents."""
        return jsonify(srv.list_agents())

    @app.route("/agents", methods=["POST"])
    def create_agent():
        """Create agent."""
        data = request.get_json()
        agent_id = data.get("agent_id")
        config = data.get("config", {})

        if not agent_id:
            return jsonify({"status": "error", "message": "agent_id required"}), 400

        return jsonify(srv.create_agent(agent_id, config))

    @app.route("/query", methods=["POST"])
    def query():
        """Execute query."""
        data = request.get_json()
        agent_id = data.get("agent_id")
        text = data.get("text")
        intent = data.get("intent", "retrieve")

        if not agent_id or not text:
            return (
                jsonify({"status": "error", "message": "agent_id and text required"}),
                400,
            )

        return jsonify(srv.query(agent_id, text, intent))

    @app.route("/batch-query", methods=["POST"])
    def batch_query():
        """Execute batch queries."""
        data = request.get_json()
        agent_id = data.get("agent_id")
        queries = data.get("queries", [])

        if not agent_id or not queries:
            return (
                jsonify(
                    {"status": "error", "message": "agent_id and queries required"}
                ),
                400,
            )

        return jsonify(srv.batch_query(agent_id, queries))

    @app.route("/metrics/<agent_id>", methods=["GET"])
    def metrics(agent_id):
        """Get agent metrics."""
        return jsonify(srv.get_metrics(agent_id))

    # Orchestration webhook endpoints
    @app.route("/orchestration/webhooks", methods=["GET"])
    def list_webhooks():
        """List registered orchestration webhooks."""
        return jsonify(srv.list_orchestration_webhooks())

    @app.route("/orchestration/webhooks", methods=["POST"])
    def register_webhook():
        """Register orchestration webhook."""
        data = request.get_json() or {}
        webhook_id = data.get("webhook_id")
        url = data.get("url")
        events = data.get("events", [])

        if not webhook_id or not url or not events:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "webhook_id, url, and events required",
                    }
                ),
                400,
            )

        return jsonify(
            srv.register_orchestration_webhook(
                webhook_id=webhook_id,
                url=url,
                events=events,
                secret_key=data.get("secret_key"),
                headers=data.get("headers"),
            )
        )

    @app.route("/orchestration/webhooks/<webhook_id>", methods=["DELETE"])
    def unregister_webhook(webhook_id):
        """Unregister orchestration webhook."""
        return jsonify(srv.unregister_orchestration_webhook(webhook_id))

    @app.route("/orchestration/webhooks/events", methods=["POST"])
    def receive_orchestration_event():
        """Receive and process orchestration webhook event."""
        data = request.get_json() or {}
        return jsonify(srv.emit_orchestration_event(data))

    # MCP service endpoints
    @app.route("/orchestration/services", methods=["GET"])
    def list_mcp_services():
        """List registered MCP services."""
        return jsonify(srv.list_mcp_services())

    @app.route("/orchestration/services", methods=["POST"])
    def register_mcp_service():
        """Register MCP endpoint."""
        data = request.get_json() or {}
        project_name = data.get("project_name")
        port = data.get("port")

        if not project_name or not port:
            return (
                jsonify(
                    {"status": "error", "message": "project_name and port required"}
                ),
                400,
            )

        return jsonify(
            srv.register_mcp_endpoint(
                project_name=project_name,
                port=port,
                mcp_version=data.get("mcp_version", "2.0"),
                tools=data.get("tools", []),
            )
        )

    @app.route("/orchestration/tools/<tool_name>", methods=["GET"])
    def get_tool_routing(tool_name):
        """Get tool routing information."""
        return jsonify(srv.get_tool_routing(tool_name))

    # Fallback management endpoints
    @app.route("/orchestration/fallbacks", methods=["POST"])
    def register_fallback():
        """Register fallback tools."""
        data = request.get_json() or {}
        primary_tool = data.get("primary_tool")
        fallback_tools = data.get("fallback_tools", [])

        if not primary_tool or not fallback_tools:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "primary_tool and fallback_tools required",
                    }
                ),
                400,
            )

        return jsonify(
            srv.register_fallback_tool(
                primary_tool=primary_tool,
                fallback_tools=fallback_tools,
            )
        )

    # Status endpoints
    @app.route("/orchestration/status", methods=["GET"])
    def orchestration_status():
        """Get orchestration system status."""
        return jsonify(srv.get_orchestration_status())

    return app


def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the REST API server."""
    app = create_flask_app()
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    run_server()
