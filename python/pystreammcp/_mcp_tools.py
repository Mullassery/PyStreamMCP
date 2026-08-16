"""MCP 2.0 Tools for PyStreamMCP - Intelligent Cross-Project Orchestration"""

from typing import Any, Dict, List, Optional


class PyStreamMCPTools:
    """12 MCP tools for intelligent multi-project orchestration & optimization"""

    @staticmethod
    def get_tools() -> Dict[str, Any]:
        return {
            "discover_mcp_projects": {
                "name": "discover_mcp_projects",
                "description": "Discover all MCP-enabled projects and their available tools",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "include_metadata": {
                            "type": "boolean",
                            "description": "Include tool descriptions",
                        },
                        "filter_by_capability": {
                            "type": "string",
                            "enum": [
                                "data_quality",
                                "activation",
                                "queries",
                                "segmentation",
                                "weather",
                                "spatial",
                                "datasets",
                                "orchestration",
                            ],
                            "description": "Filter projects by capability",
                        },
                    },
                },
            },
            "plan_query_execution": {
                "name": "plan_query_execution",
                "description": "Plan optimal execution strategy for multi-project queries",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query_description": {
                            "type": "string",
                            "description": "What are you trying to do?",
                        },
                        "projects_involved": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of projects to use",
                        },
                        "optimization_goal": {
                            "type": "string",
                            "enum": ["speed", "cost", "accuracy", "balanced"],
                            "description": "Optimize for speed/cost/accuracy",
                        },
                    },
                    "required": ["query_description"],
                },
            },
            "optimize_cross_project_query": {
                "name": "optimize_cross_project_query",
                "description": "Optimize multi-project query to reduce tokens and latency (60-75% reduction)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "original_query": {"type": "string"},
                        "involved_projects": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "constraints": {
                            "type": "object",
                            "properties": {
                                "max_latency_ms": {"type": "integer"},
                                "max_cost_cents": {"type": "number"},
                            },
                        },
                    },
                    "required": ["original_query"],
                },
            },
            "execute_federated_query": {
                "name": "execute_federated_query",
                "description": "Execute query across multiple MCP projects and aggregate results",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Federated query"},
                        "projects": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Target projects",
                        },
                        "timeout_seconds": {
                            "type": "integer",
                            "description": "Query timeout",
                        },
                        "fallback_strategy": {
                            "type": "string",
                            "enum": ["fail_fast", "partial_results", "use_cache"],
                        },
                    },
                    "required": ["query", "projects"],
                },
            },
            "detect_compatible_projects": {
                "name": "detect_compatible_projects",
                "description": "Find projects that can work together for a given task",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "capability": {
                            "type": "string",
                            "description": "Required capability",
                        },
                        "data_type": {
                            "type": "string",
                            "description": "Input data type",
                        },
                        "output_format": {
                            "type": "string",
                            "description": "Desired output format",
                        },
                    },
                    "required": ["capability"],
                },
            },
            "rank_tools_by_relevance": {
                "name": "rank_tools_by_relevance",
                "description": "Rank available tools by relevance to a task",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "task_description": {"type": "string"},
                        "available_tools": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Pool of tools to rank",
                        },
                        "weight_by_speed": {
                            "type": "number",
                            "description": "0-1 weight for speed",
                        },
                        "weight_by_accuracy": {
                            "type": "number",
                            "description": "0-1 weight for accuracy",
                        },
                    },
                    "required": ["task_description"],
                },
            },
            "handle_cross_database_join": {
                "name": "handle_cross_database_join",
                "description": "Execute join across heterogeneous databases (SQL/NoSQL/Graph)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "left_source": {
                            "type": "string",
                            "description": "Left data source (project.table)",
                        },
                        "right_source": {
                            "type": "string",
                            "description": "Right data source",
                        },
                        "join_key": {
                            "type": "string",
                            "description": "Join key expression",
                        },
                        "join_type": {
                            "type": "string",
                            "enum": ["inner", "left", "right", "full"],
                        },
                    },
                    "required": ["left_source", "right_source", "join_key"],
                },
            },
            "cache_management": {
                "name": "cache_management",
                "description": "Manage intelligent caching for frequently accessed data",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["enable", "disable", "clear", "stats"],
                            "description": "Cache action",
                        },
                        "scope": {
                            "type": "string",
                            "enum": ["global", "project", "query"],
                            "description": "Cache scope",
                        },
                        "ttl_seconds": {
                            "type": "integer",
                            "description": "Cache time-to-live",
                        },
                        "target": {
                            "type": "string",
                            "description": "Project or query ID",
                        },
                    },
                    "required": ["action"],
                },
            },
            "error_recovery_retry": {
                "name": "error_recovery_retry",
                "description": "Handle query errors with intelligent retry strategies",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "failed_query": {"type": "string"},
                        "error_type": {
                            "type": "string",
                            "enum": [
                                "timeout",
                                "not_found",
                                "permission",
                                "rate_limit",
                                "incompatible",
                            ],
                        },
                        "retry_strategy": {
                            "type": "string",
                            "enum": [
                                "exponential_backoff",
                                "immediate",
                                "fallback_project",
                            ],
                        },
                        "max_retries": {"type": "integer"},
                    },
                    "required": ["failed_query", "error_type"],
                },
            },
            "report_performance_metrics": {
                "name": "report_performance_metrics",
                "description": "Get performance metrics for queries and project endpoints",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "metric_type": {
                            "type": "string",
                            "enum": [
                                "latency",
                                "throughput",
                                "accuracy",
                                "cost",
                                "availability",
                            ],
                        },
                        "time_window_hours": {
                            "type": "integer",
                            "description": "Historical window",
                        },
                        "group_by": {
                            "type": "string",
                            "enum": ["project", "tool", "hour", "day"],
                        },
                    },
                    "required": ["metric_type"],
                },
            },
            "estimate_query_cost_multi_project": {
                "name": "estimate_query_cost_multi_project",
                "description": "Estimate cost (tokens, API calls, compute) for multi-project query",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "projects": {"type": "array", "items": {"type": "string"}},
                        "cost_model": {
                            "type": "string",
                            "enum": ["tokens", "api_calls", "compute_seconds", "usd"],
                        },
                    },
                    "required": ["query"],
                },
            },
            "manage_endpoint_federation": {
                "name": "manage_endpoint_federation",
                "description": "Manage federation of remote MCP endpoints (ports 8765-8772)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": [
                                "register",
                                "discover",
                                "health_check",
                                "deregister",
                            ],
                        },
                        "endpoint_url": {
                            "type": "string",
                            "description": "MCP endpoint URL",
                        },
                        "project_name": {
                            "type": "string",
                            "description": "Project name",
                        },
                    },
                    "required": ["action"],
                },
            },
            # Orchestration Webhook Tools
            "register_orchestration_webhook": {
                "name": "register_orchestration_webhook",
                "description": "Register webhook for real-time MCP event notifications (mcp.available, tool.invoked, etc.)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "webhook_id": {
                            "type": "string",
                            "description": "Unique webhook identifier",
                        },
                        "url": {
                            "type": "string",
                            "description": "Webhook endpoint URL",
                        },
                        "events": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": [
                                    "mcp.available",
                                    "mcp.unavailable",
                                    "tool.invoked",
                                    "tool.result",
                                    "mcp.health_update",
                                    "tool.dependency_required",
                                ],
                            },
                            "description": "Events to subscribe to",
                        },
                        "secret_key": {
                            "type": "string",
                            "description": "Secret for HMAC signature validation",
                        },
                    },
                    "required": ["webhook_id", "url", "events"],
                },
            },
            "list_service_endpoints": {
                "name": "list_service_endpoints",
                "description": "List all registered MCP service endpoints and their health status",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "filter_by_status": {
                            "type": "string",
                            "enum": ["healthy", "degraded", "unavailable", "all"],
                            "description": "Filter endpoints by health status",
                        },
                        "include_metrics": {
                            "type": "boolean",
                            "description": "Include health metrics",
                        },
                    },
                },
            },
            "route_tool_invocation": {
                "name": "route_tool_invocation",
                "description": "Route a tool invocation to the appropriate MCP endpoint with fallback support",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "tool_name": {
                            "type": "string",
                            "description": "Tool to invoke",
                        },
                        "params": {"type": "object", "description": "Tool parameters"},
                        "chain_id": {
                            "type": "string",
                            "description": "Chain context for cascading",
                        },
                        "use_fallback": {
                            "type": "boolean",
                            "description": "Enable fallback if primary unavailable",
                        },
                        "timeout_ms": {
                            "type": "integer",
                            "description": "Invocation timeout",
                        },
                    },
                    "required": ["tool_name"],
                },
            },
            "get_tool_routing_info": {
                "name": "get_tool_routing_info",
                "description": "Get routing information for a tool (which MCP provides it, health status, fallbacks)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "tool_name": {
                            "type": "string",
                            "description": "Tool to get routing info for",
                        },
                        "include_fallbacks": {
                            "type": "boolean",
                            "description": "Include fallback options",
                        },
                    },
                    "required": ["tool_name"],
                },
            },
            "monitor_mcp_health": {
                "name": "monitor_mcp_health",
                "description": "Monitor health status of MCP endpoints and trigger alerts on degradation",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_name": {
                            "type": "string",
                            "description": "Project to monitor (or 'all')",
                        },
                        "alert_on_degradation": {
                            "type": "boolean",
                            "description": "Alert if status changes",
                        },
                        "metrics_window_minutes": {
                            "type": "integer",
                            "description": "Historical window for metrics",
                        },
                    },
                },
            },
            "orchestrate_cross_mcp_workflow": {
                "name": "orchestrate_cross_mcp_workflow",
                "description": "Orchestrate a workflow spanning multiple MCPs with automatic tool routing and cascading",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "Unique workflow identifier",
                        },
                        "tool_sequence": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Ordered sequence of tools to execute",
                        },
                        "cascade_on_success": {
                            "type": "boolean",
                            "description": "Continue on success",
                        },
                        "error_handling": {
                            "type": "string",
                            "enum": ["fail_fast", "continue", "use_fallback"],
                            "description": "How to handle errors",
                        },
                    },
                    "required": ["workflow_id", "tool_sequence"],
                },
            },
        }


class PyStreamMCPHandler:
    """Async handlers for PyStreamMCP orchestration tools.

    Every handler here delegates to `self.orchestrator` (an
    `_mcp_connector.Orchestrator` instance) — the same real,
    tested federation-discovery / routing / webhook logic used
    elsewhere in the package — instead of returning hardcoded
    fixture data disconnected from what's actually configured or
    reachable. Where the underlying capability genuinely isn't
    implemented yet (e.g. cross-database joins), the response says
    so explicitly rather than fabricating a plausible-looking result.
    """

    def __init__(self, orchestrator: Any):
        self.orchestrator = orchestrator

    async def discover_mcp_projects(
        self, include_metadata: bool = False, filter_by_capability: Optional[str] = None
    ) -> Dict[str, Any]:
        """Discover MCP-enabled projects actually configured for federation.

        Probes every endpoint in [federation].endpoints (pystreammcp.toml)
        for real liveness and its real tool list. When `filter_by_capability`
        is given, this narrows to projects with a tool whose name/description
        lexically matches that capability (via Orchestrator.detect_compatible_projects)
        instead of a fixed capability->project fixture map.
        """
        if filter_by_capability:
            compat = self.orchestrator.detect_compatible_projects(filter_by_capability)
            return {
                "projects": compat["compatible"],
                "total": len(compat["compatible"]),
                "filtered_by_capability": filter_by_capability,
            }

        result = self.orchestrator.discover_mcp_projects(refresh=True)
        if not include_metadata:
            return result
        # include_metadata: attach each project's real discovered tool
        # names (not a fixture "tool_1, tool_2, ..." placeholder).
        for project in result.get("projects", []):
            discovered = self.orchestrator.registered_projects.get(
                project["project_name"]
            )
            project["tools_list"] = (
                [t.get("name") for t in discovered.tools] if discovered else []
            )
        return result

    async def plan_query_execution(
        self,
        query_description: str,
        projects_involved: Optional[List[str]] = None,
        optimization_goal: str = "balanced",
    ) -> Dict[str, Any]:
        """Plan query execution against actually discovered/healthy projects."""
        plan = self.orchestrator.plan_query_execution(
            query_description, projects_involved
        )
        plan["optimization_goal"] = optimization_goal
        return plan

    async def optimize_cross_project_query(
        self,
        original_query: str,
        involved_projects: Optional[List[str]] = None,
        constraints: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Optimize query: real, input-derived token-reduction estimate."""
        result = self.orchestrator.optimize_cross_project_query(original_query)
        result["involved_projects"] = involved_projects or []
        result["constraints"] = constraints or {}
        return result

    async def execute_federated_query(
        self,
        query: str,
        projects: List[str],
        timeout_seconds: int = 30,
        fallback_strategy: str = "fail_fast",
    ) -> Dict[str, Any]:
        """Execute federated query across projects.

        Federated query *execution* isn't implemented yet — this honestly
        reports which of the requested projects are actually reachable
        rather than fabricating result rows.
        """
        return self.orchestrator.execute_federated_query(
            query, projects, timeout_seconds
        )

    async def detect_compatible_projects(
        self,
        capability: str,
        data_type: Optional[str] = None,
        output_format: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Detect projects with a tool lexically matching `capability`."""
        result = self.orchestrator.detect_compatible_projects(capability)
        return {
            "capability": capability,
            "compatible_projects": [
                c["project_name"] for c in result["compatible"]
            ],
            "details": result["compatible"],
        }

    async def rank_tools_by_relevance(
        self,
        task_description: str,
        available_tools: Optional[List[str]] = None,
        weight_by_speed: float = 0.5,
        weight_by_accuracy: float = 0.5,
    ) -> Dict[str, Any]:
        """Rank real, discovered tools by lexical relevance to the task.

        `weight_by_speed`/`weight_by_accuracy` are accepted for API
        compatibility but not applied: ranking here is purely lexical
        (name/description term overlap) since there's no real per-tool
        speed/accuracy telemetry to weight against yet.
        """
        result = self.orchestrator.rank_tools_by_relevance(task_description)
        ranked = result["ranked"]
        if available_tools:
            ranked = [r for r in ranked if r["tool_name"] in available_tools]
        return {
            "task": task_description,
            "ranked_tools": [
                {
                    "rank": i + 1,
                    "tool": r["tool_name"],
                    "project": r["project_name"],
                    "relevance_score": r["relevance"],
                }
                for i, r in enumerate(ranked)
            ],
            "scoring_weights": {
                "speed": weight_by_speed,
                "accuracy": weight_by_accuracy,
                "note": "weights accepted but not applied; ranking is lexical",
            },
        }

    async def handle_cross_database_join(
        self,
        left_source: str,
        right_source: str,
        join_key: str,
        join_type: str = "inner",
    ) -> Dict[str, Any]:
        """Cross-database joins are not implemented yet (honest "not_implemented",
        not a fabricated row count)."""
        result = self.orchestrator.handle_cross_database_join(
            left_source, right_source, join_key
        )
        result["join_type"] = join_type
        return result

    async def cache_management(
        self,
        action: str,
        scope: str = "global",
        ttl_seconds: Optional[int] = None,
        target: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Manage a real in-memory cache (single global namespace;
        `scope` is accepted but the cache isn't currently partitioned by it)."""
        result = self.orchestrator.cache_management(action, ttl_seconds, target)
        result["scope"] = scope
        return result

    async def error_recovery_retry(
        self,
        failed_query: str,
        error_type: str,
        retry_strategy: str = "exponential_backoff",
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """Queue a failed query for retry via the real FallbackManager."""
        return self.orchestrator.error_recovery_retry(
            failed_query, error_type, retry_strategy, max_retries
        )

    async def report_performance_metrics(
        self, metric_type: str, time_window_hours: int = 24, group_by: str = "project"
    ) -> Dict[str, Any]:
        """Report real recorded health metrics (may be empty if nothing has
        reported health yet — `time_window_hours` is accepted but not yet
        applied as a filter)."""
        result = self.orchestrator.report_performance_metrics(metric_type, group_by)
        result["time_window_hours"] = time_window_hours
        return result

    async def estimate_query_cost_multi_project(
        self,
        query: str,
        projects: Optional[List[str]] = None,
        cost_model: str = "tokens",
    ) -> Dict[str, Any]:
        """Estimate token cost from the actual query text."""
        return self.orchestrator.estimate_query_cost_multi_project(
            query, projects, cost_model
        )

    async def manage_endpoint_federation(
        self,
        action: str,
        endpoint_url: Optional[str] = None,
        project_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Manage the federation endpoint list configured in pystreammcp.toml.

        "discover" re-probes every configured endpoint (maps to the real
        Orchestrator "refresh" action); "health_check" lists current status
        without re-probing (maps to "list"). "register"/"deregister" of
        individual ad-hoc endpoints isn't supported — federation membership
        is config-file driven, not fabricated as if it succeeded.
        """
        action_map = {"discover": "refresh", "health_check": "list"}
        if action in action_map:
            return self.orchestrator.manage_endpoint_federation(action_map[action])
        return {
            "action": action,
            "status": "not_implemented",
            "message": (
                f"Action {action!r} is not supported: federation endpoints are "
                "configured via pystreammcp.toml's [federation].endpoints, not "
                "registered/deregistered individually at runtime."
            ),
            "endpoint_url": endpoint_url,
            "project_name": project_name,
        }

    # Orchestration Webhook Handlers
    async def register_orchestration_webhook(
        self,
        webhook_id: str,
        url: str,
        events: List[str],
        secret_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Register orchestration webhook in real, queryable state."""
        result = self.orchestrator.register_orchestration_webhook(
            webhook_id, url, events, secret_key
        )
        result["message"] = f"Webhook registered for {len(events)} event types"
        result["event_types"] = events
        return result

    async def list_service_endpoints(
        self, filter_by_status: str = "all", include_metrics: bool = False
    ) -> Dict[str, Any]:
        """List MCP endpoints actually registered with the ServiceRegistry
        (genuinely empty until something registers via an mcp.available event)."""
        return self.orchestrator.list_service_endpoints(
            filter_by_status, include_metrics
        )

    async def route_tool_invocation(
        self,
        tool_name: str,
        params: Optional[Dict] = None,
        chain_id: Optional[str] = None,
        use_fallback: bool = True,
        timeout_ms: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Route tool invocation via the real ToolChainOrchestrator/FallbackManager."""
        result = await self.orchestrator.route_tool_invocation(
            tool_name, params, chain_id, use_fallback, timeout_ms
        )
        result["timeout_ms"] = timeout_ms or 5000
        return result

    async def get_tool_routing_info(
        self, tool_name: str, include_fallbacks: bool = False
    ) -> Dict[str, Any]:
        """Get real routing info for a tool from the ServiceRegistry."""
        return self.orchestrator.get_tool_routing_info(tool_name, include_fallbacks)

    async def monitor_mcp_health(
        self,
        project_name: str = "all",
        alert_on_degradation: bool = True,
        metrics_window_minutes: int = 60,
    ) -> Dict[str, Any]:
        """Real health snapshot from the ServiceRegistry (`alert_on_degradation`
        and `metrics_window_minutes` are accepted but not yet applied)."""
        result = self.orchestrator.monitor_mcp_health(project_name)
        result["alert_on_degradation"] = alert_on_degradation
        result["metrics_window_minutes"] = metrics_window_minutes
        return result

    async def orchestrate_cross_mcp_workflow(
        self,
        workflow_id: str,
        tool_sequence: List[str],
        cascade_on_success: bool = True,
        error_handling: str = "fail_fast",
    ) -> Dict[str, Any]:
        """Actually execute a sequence of routed tool invocations, not just
        return a fabricated "pending" plan."""
        return await self.orchestrator.orchestrate_cross_mcp_workflow(
            workflow_id, tool_sequence, cascade_on_success, error_handling
        )
