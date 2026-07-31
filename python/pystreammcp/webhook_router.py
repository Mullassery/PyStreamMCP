"""Event-driven MCP orchestration router for cross-project tool discovery and routing"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class Tool:
    """MCP tool metadata"""
    name: str
    project_name: str
    description: str
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MCPEndpoint:
    """MCP project endpoint"""
    project_name: str
    port: int
    mcp_version: str
    tools: List[Tool] = field(default_factory=list)
    status: str = "healthy"  # healthy, degraded, unavailable
    health_metrics: Dict[str, Any] = field(default_factory=dict)
    last_heartbeat: datetime = field(default_factory=datetime.utcnow)
    fallback_endpoints: List[str] = field(default_factory=list)


@dataclass
class ToolInvocation:
    """Tool invocation request and metadata"""
    tool_name: str
    project_name: str
    invocation_id: str
    params: Dict[str, Any]
    chain_id: Optional[str] = None
    position_in_chain: int = 0
    total_chain_length: int = 1
    upstream_results: List[Dict[str, Any]] = field(default_factory=list)
    user_id: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class ServiceRegistry:
    """Track availability of all MCPs and tools across 19 projects"""

    def __init__(self):
        self.endpoints: Dict[str, MCPEndpoint] = {}
        self.tools_by_name: Dict[str, List[Tuple[str, MCPEndpoint]]] = {}  # tool_name -> [(project, endpoint)]
        self.tools_by_project: Dict[str, List[Tool]] = {}  # project_name -> [tools]
        self.health_history: Dict[str, List[Dict[str, Any]]] = {}  # project_name -> [health_checks]
        self.max_history_size = 100

    def register_mcp_endpoint(self, endpoint: MCPEndpoint) -> None:
        """Register MCP endpoint for a project"""
        self.endpoints[endpoint.project_name] = endpoint
        self.tools_by_project[endpoint.project_name] = endpoint.tools

        # Index tools by name for quick lookup
        for tool in endpoint.tools:
            if tool.name not in self.tools_by_name:
                self.tools_by_name[tool.name] = []
            self.tools_by_name[tool.name].append((endpoint.project_name, endpoint))

        logger.info(
            f"MCP endpoint registered: {endpoint.project_name} "
            f"(port {endpoint.port}, {len(endpoint.tools)} tools)"
        )

    def unregister_mcp_endpoint(self, project_name: str) -> None:
        """Unregister MCP endpoint"""
        if project_name in self.endpoints:
            endpoint = self.endpoints[project_name]
            del self.endpoints[project_name]
            del self.tools_by_project[project_name]

            # Remove from tools_by_name index
            for tool in endpoint.tools:
                if tool.name in self.tools_by_name:
                    self.tools_by_name[tool.name] = [
                        (p, e) for p, e in self.tools_by_name[tool.name]
                        if p != project_name
                    ]
                    if not self.tools_by_name[tool.name]:
                        del self.tools_by_name[tool.name]

            logger.info(f"MCP endpoint unregistered: {project_name}")

    def get_available_mcps(self) -> List[MCPEndpoint]:
        """Get all available MCPs"""
        return [e for e in self.endpoints.values() if e.status == "healthy"]

    def find_tool(self, tool_name: str) -> Optional[Tuple[str, MCPEndpoint]]:
        """Find a tool in any available MCP"""
        if tool_name not in self.tools_by_name:
            return None

        # Return first available endpoint with this tool
        for project_name, endpoint in self.tools_by_name[tool_name]:
            if endpoint.status == "healthy":
                return (project_name, endpoint)

        return None

    def find_tool_fallback(self, tool_name: str) -> Optional[Tuple[str, MCPEndpoint]]:
        """Find fallback for tool (includes degraded MCPs)"""
        if tool_name not in self.tools_by_name:
            return None

        # Return first available endpoint (even if degraded)
        for project_name, endpoint in self.tools_by_name[tool_name]:
            if endpoint.status in ["healthy", "degraded"]:
                return (project_name, endpoint)

        return None

    def get_tools_by_project(self, project_name: str) -> List[Tool]:
        """Get all tools in a project"""
        return self.tools_by_project.get(project_name, [])

    def mark_mcp_available(self, project_name: str, metrics: Optional[Dict[str, Any]] = None) -> None:
        """Mark MCP as available"""
        if project_name in self.endpoints:
            self.endpoints[project_name].status = "healthy"
            if metrics:
                self.endpoints[project_name].health_metrics = metrics
            self.endpoints[project_name].last_heartbeat = datetime.utcnow()
            logger.info(f"MCP marked available: {project_name}")

    def mark_mcp_unavailable(self, project_name: str, reason: Optional[str] = None) -> None:
        """Mark MCP as unavailable"""
        if project_name in self.endpoints:
            self.endpoints[project_name].status = "unavailable"
            logger.warning(f"MCP marked unavailable: {project_name} ({reason or 'unknown'})")

    def mark_mcp_degraded(self, project_name: str) -> None:
        """Mark MCP as degraded but operational"""
        if project_name in self.endpoints:
            self.endpoints[project_name].status = "degraded"
            logger.warning(f"MCP marked degraded: {project_name}")

    def update_health_metrics(self, project_name: str, metrics: Dict[str, Any]) -> None:
        """Update health metrics for MCP"""
        if project_name in self.endpoints:
            self.endpoints[project_name].health_metrics = metrics
            self.endpoints[project_name].last_heartbeat = datetime.utcnow()

            # Track history
            if project_name not in self.health_history:
                self.health_history[project_name] = []

            history_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": metrics,
                "status": self.endpoints[project_name].status,
            }
            self.health_history[project_name].append(history_entry)

            # Trim history
            if len(self.health_history[project_name]) > self.max_history_size:
                self.health_history[project_name] = self.health_history[project_name][-self.max_history_size:]

    def get_registry_snapshot(self) -> Dict[str, Any]:
        """Get current registry state"""
        return {
            "total_mcps": len(self.endpoints),
            "healthy_mcps": len(self.get_available_mcps()),
            "total_tools": len(self.tools_by_name),
            "mcps": [
                {
                    "project": name,
                    "port": ep.port,
                    "status": ep.status,
                    "tool_count": len(ep.tools),
                    "health_metrics": ep.health_metrics,
                }
                for name, ep in self.endpoints.items()
            ],
        }


class ToolChainOrchestrator:
    """Orchestrate cross-project tool chains and cascading executions"""

    def __init__(self, service_registry: ServiceRegistry):
        self.registry = service_registry
        self.invocation_history: Dict[str, Dict[str, Any]] = {}
        self.max_history_size = 1000

    async def route_tool_invocation(
        self,
        tool_name: str,
        params: Dict[str, Any],
        chain_context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Route tool invocation to appropriate MCP"""
        chain_id = chain_context.get("chain_id") if chain_context else None
        position = chain_context.get("position_in_chain", 0) if chain_context else 0
        total_length = chain_context.get("total_chain_length", 1) if chain_context else 1
        upstream_results = chain_context.get("upstream_results", []) if chain_context else []

        # Find tool location
        result = self.registry.find_tool(tool_name)
        if not result:
            return {
                "status": "error",
                "message": f"Tool {tool_name} not found in any available MCP",
                "tool_name": tool_name,
            }

        project_name, endpoint = result

        # Create invocation record
        invocation_id = f"inv_{chain_id or 'standalone'}_{position}"
        invocation = ToolInvocation(
            tool_name=tool_name,
            project_name=project_name,
            invocation_id=invocation_id,
            params=params,
            chain_id=chain_id,
            position_in_chain=position,
            total_chain_length=total_length,
            upstream_results=upstream_results,
            user_id=user_id,
        )

        # Record invocation
        self.invocation_history[invocation_id] = {
            "invocation": invocation,
            "routed_to": f"{project_name}:{endpoint.port}",
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Trim history
        if len(self.invocation_history) > self.max_history_size:
            oldest_keys = list(self.invocation_history.keys())[:100]
            for key in oldest_keys:
                del self.invocation_history[key]

        logger.info(
            f"Tool routed: {tool_name} → {project_name}:{endpoint.port} "
            f"(chain {chain_id}, position {position}/{total_length})"
        )

        return {
            "status": "routed",
            "invocation_id": invocation_id,
            "tool_name": tool_name,
            "project_name": project_name,
            "endpoint": f"http://localhost:{endpoint.port}",
            "chain_id": chain_id,
            "position_in_chain": position,
        }

    async def cascade_on_result(
        self,
        tool_result: Dict[str, Any],
        cascade_triggers: List[Dict[str, Any]],
        invocation_id: str,
    ) -> List[Dict[str, Any]]:
        """Cascade tool result to dependent tools"""
        cascaded_results = []

        for trigger in cascade_triggers:
            trigger_tool = trigger.get("tool_name")
            trigger_condition = trigger.get("trigger_condition")
            priority = trigger.get("priority", "normal")

            # Check if cascade condition is met
            should_cascade = self._check_cascade_condition(tool_result, trigger_condition)

            if should_cascade:
                logger.info(
                    f"Cascading from {invocation_id}: "
                    f"{trigger_tool} (condition: {trigger_condition}, priority: {priority})"
                )

                # Route cascaded tool invocation
                cascade_params = trigger.get("params", {})
                cascade_context = {
                    "chain_id": tool_result.get("chain_id", f"cascade_{invocation_id}"),
                    "position_in_chain": tool_result.get("position_in_chain", 0) + 1,
                    "total_chain_length": tool_result.get("total_chain_length", 2),
                    "upstream_results": [tool_result],
                }

                cascade_result = await self.route_tool_invocation(
                    tool_name=trigger_tool,
                    params=cascade_params,
                    chain_context=cascade_context,
                )
                cascaded_results.append(cascade_result)

        return cascaded_results

    def find_fallback_tool(self, tool_name: str) -> Optional[Tuple[str, str]]:
        """Find fallback for tool"""
        result = self.registry.find_tool_fallback(tool_name)
        if result:
            project_name, endpoint = result
            return (project_name, f"http://localhost:{endpoint.port}")
        return None

    def _check_cascade_condition(self, result: Dict[str, Any], condition: str) -> bool:
        """Check if cascade condition is met"""
        if condition == "always":
            return True
        if condition == "on_success":
            return result.get("status") == "success"
        if condition == "on_error":
            return result.get("status") == "error"
        return False

    def get_invocation_status(self, invocation_id: str) -> Optional[Dict[str, Any]]:
        """Get status of specific invocation"""
        return self.invocation_history.get(invocation_id)


class FallbackManager:
    """Handle MCP failures with graceful fallbacks"""

    def __init__(self, service_registry: ServiceRegistry):
        self.registry = service_registry
        self.fallback_mappings: Dict[str, List[str]] = {}  # tool_name -> [fallback_tools]
        self.retry_queue: List[Dict[str, Any]] = []
        self.max_queue_size = 10000

    def register_fallback(
        self,
        primary_tool: str,
        fallback_tools: List[str],
    ) -> None:
        """Register fallback tools for a primary tool"""
        self.fallback_mappings[primary_tool] = fallback_tools
        logger.info(
            f"Fallback registered for {primary_tool}: {', '.join(fallback_tools)}"
        )

    async def invoke_with_fallback(
        self,
        tool_name: str,
        params: Dict[str, Any],
        fallback_enabled: bool = True,
    ) -> Dict[str, Any]:
        """Invoke tool with fallback support"""
        result = self.registry.find_tool(tool_name)

        if result:
            project_name, endpoint = result
            return {
                "status": "success",
                "tool_name": tool_name,
                "project_name": project_name,
                "endpoint": f"http://localhost:{endpoint.port}",
            }

        # Primary tool not available, try fallback
        if fallback_enabled and tool_name in self.fallback_mappings:
            for fallback_tool in self.fallback_mappings[tool_name]:
                fallback_result = self.registry.find_tool(fallback_tool)
                if fallback_result:
                    project_name, endpoint = fallback_result
                    logger.warning(
                        f"Using fallback: {fallback_tool} for {tool_name}"
                    )
                    return {
                        "status": "fallback",
                        "primary_tool": tool_name,
                        "fallback_tool": fallback_tool,
                        "project_name": project_name,
                        "endpoint": f"http://localhost:{endpoint.port}",
                    }

        # Queue for retry
        self._queue_for_retry(tool_name, params)

        return {
            "status": "unavailable",
            "tool_name": tool_name,
            "message": f"Tool {tool_name} and fallbacks unavailable",
            "queued_for_retry": True,
        }

    async def retry_queue_processor(self) -> Dict[str, int]:
        """Process retry queue"""
        processed = {"retried": 0, "succeeded": 0, "failed": 0}

        while self.retry_queue:
            item = self.retry_queue.pop(0)
            tool_name = item["tool_name"]

            result = self.registry.find_tool(tool_name)
            if result:
                processed["succeeded"] += 1
                logger.info(f"Retry succeeded for {tool_name}")
            else:
                processed["failed"] += 1
                # Re-queue for next retry
                self._queue_for_retry(tool_name, item["params"])

            processed["retried"] += 1

        return processed

    def _queue_for_retry(self, tool_name: str, params: Dict[str, Any]) -> None:
        """Queue tool for retry"""
        if len(self.retry_queue) < self.max_queue_size:
            self.retry_queue.append({
                "tool_name": tool_name,
                "params": params,
                "queued_at": datetime.utcnow().isoformat(),
            })
            logger.info(f"Tool queued for retry: {tool_name}")

    def get_retry_queue_status(self) -> Dict[str, Any]:
        """Get retry queue status"""
        return {
            "queue_size": len(self.retry_queue),
            "max_size": self.max_queue_size,
            "queued_tools": [item["tool_name"] for item in self.retry_queue],
        }


class EventRouter:
    """Main orchestration event router for MCP 2.0"""

    def __init__(self):
        self.service_registry = ServiceRegistry()
        self.tool_orchestrator = ToolChainOrchestrator(self.service_registry)
        self.fallback_manager = FallbackManager(self.service_registry)

    async def route(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Route orchestration event"""
        event_type = event.get("event_type")

        if event_type == "mcp.available":
            return self._handle_mcp_available(event)
        elif event_type == "mcp.unavailable":
            return self._handle_mcp_unavailable(event)
        elif event_type == "tool.invoked":
            return await self._handle_tool_invoked(event)
        elif event_type == "tool.result":
            return await self._handle_tool_result(event)
        elif event_type == "mcp.health_update":
            return self._handle_health_update(event)
        else:
            logger.warning(f"Unknown event type: {event_type}")
            return {"status": "unhandled", "event_type": event_type}

    def _handle_mcp_available(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP availability event"""
        data = event.get("data", {})
        endpoint = MCPEndpoint(
            project_name=data.get("project_name"),
            port=data.get("mcp_port"),
            mcp_version=data.get("mcp_version", "2.0"),
            tools=[
                Tool(
                    name=t.get("name"),
                    project_name=data.get("project_name"),
                    description=t.get("description"),
                )
                for t in data.get("tools", [])
            ],
        )
        self.service_registry.register_mcp_endpoint(endpoint)
        return {"status": "registered", "project_name": endpoint.project_name}

    def _handle_mcp_unavailable(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP unavailability event"""
        data = event.get("data", {})
        project_name = data.get("project_name")
        reason = data.get("reason", "unknown")
        self.service_registry.mark_mcp_unavailable(project_name, reason)
        return {"status": "unavailable", "project_name": project_name}

    async def _handle_tool_invoked(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool invocation event"""
        data = event.get("data", {})
        return await self.tool_orchestrator.route_tool_invocation(
            tool_name=data.get("tool_name"),
            params=data.get("request_context", {}),
            chain_context=data.get("orchestration_context"),
            user_id=data.get("user_id"),
        )

    async def _handle_tool_result(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool result event"""
        data = event.get("data", {})
        cascades = await self.tool_orchestrator.cascade_on_result(
            tool_result=data.get("result", {}),
            cascade_triggers=data.get("cascade_triggers", []),
            invocation_id=data.get("invocation_id", "unknown"),
        )
        return {"status": "result_processed", "cascades": cascades}

    def _handle_health_update(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle health update event"""
        data = event.get("data", {})
        self.service_registry.update_health_metrics(
            project_name=data.get("project_name"),
            metrics=data.get("metrics", {}),
        )
        return {"status": "health_updated", "project_name": data.get("project_name")}

    def get_status(self) -> Dict[str, Any]:
        """Get router status"""
        return {
            "status": "healthy",
            "registry": self.service_registry.get_registry_snapshot(),
            "retry_queue": self.fallback_manager.get_retry_queue_status(),
        }
