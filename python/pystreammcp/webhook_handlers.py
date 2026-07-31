"""Orchestration event handlers for PyStreamMCP - handles real-time MCP routing and health coordination"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from .webhook_router import EventRouter, Tool, MCPEndpoint

logger = logging.getLogger(__name__)


class OrchestrationWebhookHandlers:
    """Handle orchestration webhook events and trigger real-time coordination"""

    def __init__(self, event_router: EventRouter, server: Optional[Any] = None):
        """
        Initialize orchestration webhook handlers

        Args:
            event_router: EventRouter instance for MCP orchestration
            server: PyStreamMCP server instance for triggering actions
        """
        self.event_router = event_router
        self.server = server
        self.handlers = {
            "mcp.available": self.handle_mcp_available,
            "mcp.unavailable": self.handle_mcp_unavailable,
            "tool.invoked": self.handle_tool_invoked,
            "tool.result": self.handle_tool_result,
            "mcp.health_update": self.handle_health_update,
            "tool.dependency_required": self.handle_tool_dependency,
        }
        self.active_invocations: Dict[str, Dict[str, Any]] = {}
        self.cascade_history: List[Dict[str, Any]] = []

    async def dispatch(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch orchestration event to appropriate handler"""
        event_type = event.get("event_type")
        handler = self.handlers.get(event_type)

        if not handler:
            logger.warning(f"No handler found for orchestration event: {event_type}")
            return {"status": "unhandled", "event_type": event_type}

        try:
            result = await handler(event)
            return result
        except Exception as e:
            logger.error(f"Error handling orchestration event {event_type}: {e}")
            return {"status": "error", "event_type": event_type, "error": str(e)}

    async def handle_mcp_available(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP availability event

        When an MCP endpoint comes online, register it, discover tools,
        update routing tables, and process any queued tools.
        """
        logger.info(f"Handling MCP availability event")

        data = event.get("data", {})
        project_name = data.get("project_name")
        port = data.get("mcp_port")
        mcp_version = data.get("mcp_version", "2.0")
        tools = data.get("tools", [])
        metrics = data.get("health_metrics", {})

        actions = []

        # Action 1: Register MCP endpoint
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
                for t in tools
            ],
        )
        self.event_router.service_registry.register_mcp_endpoint(endpoint)
        registration = self._register_mcp_endpoint(project_name, port, len(tools), mcp_version)
        actions.append(registration)

        # Action 2: Update health metrics
        health_update = self._update_mcp_health(project_name, "healthy", metrics)
        actions.append(health_update)

        # Action 3: Process retry queue for this MCP's tools
        retry_result = await self._process_retry_queue_for_mcp(project_name, tools)
        if retry_result["processed_count"] > 0:
            actions.append(retry_result)

        # Action 4: Notify dependent systems
        notification = self._notify_mcp_available(project_name, len(tools))
        actions.append(notification)

        return {
            "status": "success",
            "event_type": event.event_type,
            "project_name": project_name,
            "tools_registered": len(tools),
            "actions_triggered": actions,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def handle_mcp_unavailable(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP unavailability event

        When an MCP endpoint goes offline, mark it unavailable,
        queue affected tools for retry, and activate fallbacks.
        """
        logger.info(f"Handling MCP unavailability event")

        data = event.get("data", {})
        project_name = data.get("project_name")
        reason = data.get("reason", "unknown")
        affected_tools = data.get("affected_tools", [])
        is_temporary = data.get("is_temporary", False)

        actions = []

        # Action 1: Mark MCP unavailable
        self.event_router.service_registry.mark_mcp_unavailable(project_name, reason)
        unavailable_action = self._mark_mcp_unavailable(project_name, reason, is_temporary)
        actions.append(unavailable_action)

        # Action 2: Queue affected tools for retry
        if affected_tools:
            retry_result = self._queue_tools_for_retry(affected_tools, project_name)
            actions.append(retry_result)

        # Action 3: Activate fallbacks for high-priority tools
        fallback_result = await self._activate_fallbacks(affected_tools)
        if fallback_result["fallbacks_activated"]:
            actions.append(fallback_result)

        # Action 4: Alert dependent systems and users
        alert = self._alert_mcp_unavailable(
            project_name=project_name,
            affected_count=len(affected_tools),
            reason=reason,
            is_temporary=is_temporary,
        )
        actions.append(alert)

        return {
            "status": "success",
            "event_type": event.event_type,
            "project_name": project_name,
            "affected_tools": len(affected_tools),
            "actions_triggered": actions,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def handle_tool_invoked(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle tool invocation event

        When a tool is invoked, route it to appropriate MCP,
        track invocation context, and monitor for timeouts.
        """
        logger.info(f"Handling tool invocation event")

        data = event.get("data", {})
        tool_name = data.get("tool_name")
        invocation_id = data.get("invocation_id")
        user_id = data.get("user_id")
        chain_context = data.get("orchestration_context", {})
        params = data.get("request_context", {})

        # Record active invocation
        self.active_invocations[invocation_id] = {
            "tool_name": tool_name,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "chain_context": chain_context,
        }

        actions = []

        # Action 1: Route tool invocation
        route_result = await self.event_router.tool_orchestrator.route_tool_invocation(
            tool_name=tool_name,
            params=params,
            chain_context=chain_context,
            user_id=user_id,
        )
        actions.append({
            "action": "route_tool_invocation",
            "tool_name": tool_name,
            "routed_to": route_result.get("project_name"),
            "invocation_id": invocation_id,
            "status": route_result.get("status"),
        })

        # Action 2: Track invocation in orchestration
        tracking = self._track_invocation(
            invocation_id=invocation_id,
            tool_name=tool_name,
            user_id=user_id,
            chain_id=chain_context.get("chain_id"),
        )
        actions.append(tracking)

        # Action 3: Monitor for timeout (if timeout specified)
        if chain_context.get("timeout_ms"):
            timeout_monitor = self._monitor_invocation_timeout(
                invocation_id=invocation_id,
                timeout_ms=chain_context.get("timeout_ms"),
            )
            actions.append(timeout_monitor)

        # Action 4: Log invocation for audit trail
        audit = self._audit_invocation(
            invocation_id=invocation_id,
            tool_name=tool_name,
            user_id=user_id,
            severity="high" if chain_context.get("chain_id") else "normal",
        )
        actions.append(audit)

        return {
            "status": "success",
            "event_type": event.event_type,
            "invocation_id": invocation_id,
            "tool_name": tool_name,
            "project_name": route_result.get("project_name"),
            "actions_triggered": actions,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def handle_tool_result(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle tool result event

        When a tool completes, cascade result to dependent tools,
        update chain context, and clean up invocation tracking.
        """
        logger.info(f"Handling tool result event")

        data = event.get("data", {})
        invocation_id = data.get("invocation_id")
        tool_name = data.get("tool_name")
        result = data.get("result", {})
        cascade_triggers = data.get("cascade_triggers", [])

        actions = []

        # Action 1: Process tool result
        result_action = self._process_tool_result(
            invocation_id=invocation_id,
            tool_name=tool_name,
            result=result,
        )
        actions.append(result_action)

        # Action 2: Cascade to dependent tools
        cascaded_results = await self.event_router.tool_orchestrator.cascade_on_result(
            tool_result=result,
            cascade_triggers=cascade_triggers,
            invocation_id=invocation_id,
        )
        if cascaded_results:
            cascade_action = {
                "action": "cascade_execution",
                "cascaded_count": len(cascaded_results),
                "cascaded_tools": [c.get("tool_name") for c in cascaded_results],
                "status": "initiated",
            }
            actions.append(cascade_action)

            # Track cascade history
            self.cascade_history.append({
                "invocation_id": invocation_id,
                "source_tool": tool_name,
                "cascaded_tools": cascaded_results,
                "timestamp": datetime.utcnow().isoformat(),
            })

        # Action 3: Update chain metrics
        chain_context = self.active_invocations.get(invocation_id, {}).get("chain_context", {})
        if chain_context.get("chain_id"):
            metrics_update = self._update_chain_metrics(
                chain_id=chain_context.get("chain_id"),
                position=chain_context.get("position_in_chain", 0),
                total_length=chain_context.get("total_chain_length", 1),
                result_status=result.get("status"),
            )
            actions.append(metrics_update)

        # Action 4: Clean up invocation tracking
        if invocation_id in self.active_invocations:
            del self.active_invocations[invocation_id]
            cleanup = {"action": "cleanup_invocation", "invocation_id": invocation_id, "status": "cleaned"}
            actions.append(cleanup)

        return {
            "status": "success",
            "event_type": event.event_type,
            "invocation_id": invocation_id,
            "tool_name": tool_name,
            "cascaded_count": len(cascaded_results),
            "actions_triggered": actions,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def handle_health_update(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle health update event

        When MCP health metrics are updated, assess system health,
        adjust routing priorities, and trigger alerts if degraded.
        """
        logger.info(f"Handling health update event")

        data = event.get("data", {})
        project_name = data.get("project_name")
        metrics = data.get("metrics", {})
        previous_status = data.get("previous_status", "unknown")

        actions = []

        # Action 1: Update health metrics in registry
        self.event_router.service_registry.update_health_metrics(
            project_name=project_name,
            metrics=metrics,
        )
        metrics_update = self._update_registry_health(project_name, metrics)
        actions.append(metrics_update)

        # Action 2: Assess health status
        endpoint = self.event_router.service_registry.endpoints.get(project_name)
        current_status = endpoint.status if endpoint else "unknown"

        # Action 3: Handle status transitions
        status_action = self._handle_health_status_transition(
            project_name=project_name,
            previous_status=previous_status,
            current_status=current_status,
        )
        actions.append(status_action)

        # Action 4: Adjust routing if degraded
        if current_status == "degraded":
            degradation = self._handle_mcp_degradation(
                project_name=project_name,
                metrics=metrics,
            )
            actions.append(degradation)

        # Action 5: Alert if critical metrics
        if self._has_critical_metrics(metrics):
            alert = self._alert_critical_health(
                project_name=project_name,
                critical_metrics=self._extract_critical_metrics(metrics),
            )
            actions.append(alert)

        return {
            "status": "success",
            "event_type": event.event_type,
            "project_name": project_name,
            "current_status": current_status,
            "actions_triggered": actions,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def handle_tool_dependency(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle tool dependency event

        When a tool requires another tool's result, establish
        dependency chain and coordinate cross-MCP execution.
        """
        logger.info(f"Handling tool dependency event")

        data = event.get("data", {})
        dependent_tool = data.get("dependent_tool")
        required_tool = data.get("required_tool")
        dependency_type = data.get("dependency_type", "result")  # result, state, trigger
        invocation_id = data.get("invocation_id")

        actions = []

        # Action 1: Establish dependency relationship
        dependency_action = self._establish_dependency(
            dependent_tool=dependent_tool,
            required_tool=required_tool,
            dependency_type=dependency_type,
        )
        actions.append(dependency_action)

        # Action 2: Determine execution order
        exec_order = self._determine_execution_order(
            dependent_tool=dependent_tool,
            required_tool=required_tool,
        )
        actions.append(exec_order)

        # Action 3: Verify both tools available
        availability_check = self._check_tools_available([dependent_tool, required_tool])
        actions.append(availability_check)

        # Action 4: If cross-MCP, plan cross-project execution
        if availability_check.get("status") == "available":
            result = self.event_router.service_registry.find_tool(required_tool)
            if result:
                required_project, _ = result
                dep_result = self.event_router.service_registry.find_tool(dependent_tool)
                if dep_result:
                    dependent_project, _ = dep_result
                    if required_project != dependent_project:
                        cross_mcp = self._plan_cross_mcp_execution(
                            dependent_project=dependent_project,
                            required_project=required_project,
                            dependent_tool=dependent_tool,
                            required_tool=required_tool,
                        )
                        actions.append(cross_mcp)

        return {
            "status": "success",
            "event_type": event.event_type,
            "dependent_tool": dependent_tool,
            "required_tool": required_tool,
            "dependency_type": dependency_type,
            "actions_triggered": actions,
            "timestamp": datetime.utcnow().isoformat(),
        }

    # Private action methods
    def _register_mcp_endpoint(
        self, project_name: str, port: int, tool_count: int, mcp_version: str
    ) -> Dict[str, Any]:
        """Register MCP endpoint action"""
        return {
            "action": "register_mcp_endpoint",
            "project_name": project_name,
            "port": port,
            "tool_count": tool_count,
            "mcp_version": mcp_version,
            "status": "registered",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _update_mcp_health(
        self, project_name: str, status: str, metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update MCP health action"""
        return {
            "action": "update_mcp_health",
            "project_name": project_name,
            "health_status": status,
            "metrics": metrics,
            "status": "updated",
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def _process_retry_queue_for_mcp(
        self, project_name: str, tools: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process retry queue for newly available MCP"""
        result = await self.event_router.fallback_manager.retry_queue_processor()
        return {
            "action": "process_retry_queue",
            "project_name": project_name,
            "processed_count": result.get("retried", 0),
            "succeeded_count": result.get("succeeded", 0),
            "status": "processed",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _notify_mcp_available(self, project_name: str, tool_count: int) -> Dict[str, Any]:
        """Notify dependent systems MCP available"""
        return {
            "action": "notify_mcp_available",
            "project_name": project_name,
            "tool_count": tool_count,
            "status": "notified",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _mark_mcp_unavailable(
        self, project_name: str, reason: str, is_temporary: bool
    ) -> Dict[str, Any]:
        """Mark MCP unavailable action"""
        return {
            "action": "mark_mcp_unavailable",
            "project_name": project_name,
            "reason": reason,
            "is_temporary": is_temporary,
            "status": "unavailable",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _queue_tools_for_retry(
        self, tools: List[str], failed_mcp: str
    ) -> Dict[str, Any]:
        """Queue tools for retry"""
        for tool in tools:
            # Tools are already queued by FallbackManager
            pass
        return {
            "action": "queue_tools_for_retry",
            "tool_count": len(tools),
            "failed_mcp": failed_mcp,
            "status": "queued",
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def _activate_fallbacks(self, tools: List[str]) -> Dict[str, Any]:
        """Activate fallbacks for tools"""
        activated = 0
        for tool in tools:
            if self.event_router.fallback_manager.registry.find_tool_fallback(tool):
                activated += 1
        return {
            "action": "activate_fallbacks",
            "tool_count": len(tools),
            "fallbacks_activated": activated,
            "status": "fallbacks_ready",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _alert_mcp_unavailable(
        self,
        project_name: str,
        affected_count: int,
        reason: str,
        is_temporary: bool,
    ) -> Dict[str, Any]:
        """Alert MCP unavailable"""
        return {
            "action": "alert_mcp_unavailable",
            "project_name": project_name,
            "affected_count": affected_count,
            "reason": reason,
            "is_temporary": is_temporary,
            "severity": "warning" if is_temporary else "critical",
            "status": "alerted",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _track_invocation(
        self,
        invocation_id: str,
        tool_name: str,
        user_id: Optional[str],
        chain_id: Optional[str],
    ) -> Dict[str, Any]:
        """Track tool invocation"""
        return {
            "action": "track_invocation",
            "invocation_id": invocation_id,
            "tool_name": tool_name,
            "user_id": user_id,
            "chain_id": chain_id,
            "status": "tracked",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _monitor_invocation_timeout(
        self, invocation_id: str, timeout_ms: int
    ) -> Dict[str, Any]:
        """Monitor invocation timeout"""
        return {
            "action": "monitor_timeout",
            "invocation_id": invocation_id,
            "timeout_ms": timeout_ms,
            "status": "monitoring",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _audit_invocation(
        self,
        invocation_id: str,
        tool_name: str,
        user_id: Optional[str],
        severity: str,
    ) -> Dict[str, Any]:
        """Audit invocation"""
        return {
            "action": "audit_invocation",
            "invocation_id": invocation_id,
            "tool_name": tool_name,
            "user_id": user_id,
            "severity": severity,
            "status": "audited",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _process_tool_result(
        self,
        invocation_id: str,
        tool_name: str,
        result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Process tool result"""
        return {
            "action": "process_result",
            "invocation_id": invocation_id,
            "tool_name": tool_name,
            "result_status": result.get("status"),
            "status": "processed",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _update_chain_metrics(
        self,
        chain_id: str,
        position: int,
        total_length: int,
        result_status: str,
    ) -> Dict[str, Any]:
        """Update chain metrics"""
        return {
            "action": "update_chain_metrics",
            "chain_id": chain_id,
            "position": position,
            "total_length": total_length,
            "result_status": result_status,
            "status": "updated",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _update_registry_health(
        self, project_name: str, metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update registry health"""
        return {
            "action": "update_registry_health",
            "project_name": project_name,
            "metrics_keys": list(metrics.keys()),
            "status": "updated",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _handle_health_status_transition(
        self, project_name: str, previous_status: str, current_status: str
    ) -> Dict[str, Any]:
        """Handle health status transition"""
        return {
            "action": "health_status_transition",
            "project_name": project_name,
            "previous_status": previous_status,
            "current_status": current_status,
            "status": "handled",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _handle_mcp_degradation(
        self, project_name: str, metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle MCP degradation"""
        return {
            "action": "handle_degradation",
            "project_name": project_name,
            "priority_adjustment": "reduce_load",
            "status": "degradation_handled",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _has_critical_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Check if metrics indicate critical state"""
        if metrics.get("error_rate", 0) > 0.5:
            return True
        if metrics.get("latency_p99_ms", 0) > 5000:
            return True
        if metrics.get("tool_availability", 1.0) < 0.5:
            return True
        return False

    def _extract_critical_metrics(
        self, metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract critical metrics from health metrics"""
        critical = {}
        if metrics.get("error_rate", 0) > 0.1:
            critical["error_rate"] = metrics["error_rate"]
        if metrics.get("latency_p99_ms", 0) > 1000:
            critical["latency_p99_ms"] = metrics["latency_p99_ms"]
        if metrics.get("tool_availability", 1.0) < 0.9:
            critical["tool_availability"] = metrics["tool_availability"]
        return critical

    def _alert_critical_health(
        self, project_name: str, critical_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Alert critical health"""
        return {
            "action": "alert_critical_health",
            "project_name": project_name,
            "critical_metrics": critical_metrics,
            "severity": "critical",
            "status": "alerted",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _establish_dependency(
        self,
        dependent_tool: str,
        required_tool: str,
        dependency_type: str,
    ) -> Dict[str, Any]:
        """Establish tool dependency"""
        return {
            "action": "establish_dependency",
            "dependent_tool": dependent_tool,
            "required_tool": required_tool,
            "dependency_type": dependency_type,
            "status": "established",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _determine_execution_order(
        self, dependent_tool: str, required_tool: str
    ) -> Dict[str, Any]:
        """Determine execution order"""
        return {
            "action": "determine_execution_order",
            "execution_order": [required_tool, dependent_tool],
            "status": "determined",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _check_tools_available(self, tools: List[str]) -> Dict[str, Any]:
        """Check if tools are available"""
        available_count = 0
        for tool in tools:
            if self.event_router.service_registry.find_tool(tool):
                available_count += 1
        return {
            "action": "check_tools_available",
            "total_tools": len(tools),
            "available_tools": available_count,
            "status": "available" if available_count == len(tools) else "partial",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _plan_cross_mcp_execution(
        self,
        dependent_project: str,
        required_project: str,
        dependent_tool: str,
        required_tool: str,
    ) -> Dict[str, Any]:
        """Plan cross-MCP execution"""
        return {
            "action": "plan_cross_mcp_execution",
            "dependent_project": dependent_project,
            "required_project": required_project,
            "dependent_tool": dependent_tool,
            "required_tool": required_tool,
            "cross_mcp": True,
            "status": "planned",
            "timestamp": datetime.utcnow().isoformat(),
        }
