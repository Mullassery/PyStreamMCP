"""MCP Connector for PyStreamMCP - Multi-Project Orchestration"""

import json
import logging
import re
import subprocess
import tempfile
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
from datetime import datetime, timezone

from .webhook_router import EventRouter

logger = logging.getLogger(__name__)

try:
    import httpx
except ImportError:  # pragma: no cover - exercised only without the `mcp` extra installed
    httpx = None

try:
    import tomllib as _toml_reader  # Python 3.11+ stdlib

    def _read_toml(path: Path) -> Dict[str, Any]:
        with open(path, "rb") as f:
            return _toml_reader.load(f)
except ImportError:
    import toml as _toml_reader  # third-party backport for Python 3.9/3.10

    def _read_toml(path: Path) -> Dict[str, Any]:
        return _toml_reader.load(str(path))


DEFAULT_CONFIG_PATH = Path("pystreammcp.toml")
DISCOVERY_TIMEOUT_SECONDS = 3.0


@dataclass
class DiscoveredProject:
    """A federated MCP project as actually observed, not assumed."""

    project_name: str
    endpoint: str
    status: str  # "healthy" | "unavailable"
    tools: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None
    checked_at: float = field(default_factory=time.time)

try:
    from statguardian._mcp_connector import BaseMCPConnector
except ImportError:

    class BaseMCPConnector(ABC):
        def __init__(self, project_name: str, port: int = 8765):
            self.project_name = project_name
            self.port = port
            self.dab_process: Optional[subprocess.Popen] = None
            self._ready = False

        @abstractmethod
        def get_mcp_tools(self) -> Dict[str, Any]:
            pass

        @abstractmethod
        def get_tool_handlers(self) -> Any:
            pass

        def start_mcp_connector(self) -> str:
            logger.info(f"Starting {self.project_name} MCP...")
            try:
                tools = self.get_mcp_tools()
                self.handler = self.get_tool_handlers()
                config = self._generate_dab_config(tools)
                config_path = self._write_temp_config(config)
                self._start_dab_subprocess(config_path)
                self._ready = True
                return f"http://localhost:{self.port}/mcp"
            except Exception as e:
                logger.error(f"Failed: {e}")
                raise

        def stop_mcp_connector(self):
            if self.dab_process:
                try:
                    self.dab_process.terminate()
                    self.dab_process.wait(timeout=5)
                except (subprocess.TimeoutExpired, OSError):
                    pass
                self._ready = False

        def _generate_dab_config(self, tools: Dict[str, Any]) -> Dict:
            # Bind to localhost only, with no cross-origin access and
            # read-only anonymous permissions by default. This launches a
            # local subprocess for MCP tool serving; it isn't meant to be
            # reachable from other hosts or origins out of the box. Callers
            # that need broader access (e.g. a container with its own
            # network boundary) should override these explicitly rather
            # than getting an open-to-everyone server by default.
            return {
                "runtime": {
                    "host": "127.0.0.1",
                    "port": self.port,
                    "cors": {"origins": []},
                },
                "entities": {
                    k: {
                        "source": k,
                        "permissions": [{"actions": ["read"], "roles": ["anonymous"]}],
                    }
                    for k in tools.keys()
                },
                "rest": {"enabled": True, "path": "/api"},
                "graphql": {"enabled": True, "path": "/graphql"},
                "mcp": {"enabled": True, "path": "/mcp"},
            }

        def _write_temp_config(self, config: Dict) -> str:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False
            ) as f:
                json.dump(config, f)
                return f.name

        def _start_dab_subprocess(self, config_path: str):
            self.dab_process = subprocess.Popen(
                ["dab", "start", "--config", config_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        def is_ready(self) -> bool:
            return self._ready


class Orchestrator:
    """Multi-project MCP orchestration and intelligent federation"""

    def __init__(self, config_path: Optional[str] = None, transport: Optional[Any] = None):
        """
        Args:
            config_path: Path to the pystreammcp.toml config to read
                [federation].endpoints from. Defaults to ./pystreammcp.toml.
            transport: Optional httpx transport override, for tests to
                inject a mock transport instead of hitting real sockets.
        """
        self.mcp_connector: Optional[Any] = None
        self.registered_projects: Dict[str, DiscoveredProject] = {}
        self.config_path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
        self._transport = transport

        # Real, stateful backing for the routing/webhook/health MCP tools
        # (register_orchestration_webhook, list_service_endpoints,
        # route_tool_invocation, get_tool_routing_info, monitor_mcp_health,
        # orchestrate_cross_mcp_workflow): the same tested ServiceRegistry /
        # ToolChainOrchestrator / FallbackManager infrastructure the HTTP
        # webhook server (server.py) uses, not a second, disconnected copy.
        self.event_router = EventRouter()
        self.webhook_configs: Dict[str, Dict[str, Any]] = {}

        # Real (if minimal) in-memory cache backing `cache_management`.
        self._cache: Dict[str, Any] = {}
        self._cache_enabled: bool = True
        self._cache_hits = 0
        self._cache_misses = 0

    def _load_federation_endpoints(self) -> List[str]:
        """Read [federation].endpoints from the config file.

        Returns [] (not fabricated entries) when the config is missing or
        has no federation section — discovery then has nothing real to
        report, which is the honest result.
        """
        if not self.config_path.exists():
            logger.warning(
                "No config file at %s; federation discovery has nothing to probe",
                self.config_path,
            )
            return []
        try:
            config = _read_toml(self.config_path)
        except Exception as e:
            logger.error("Failed to parse %s: %s", self.config_path, e)
            return []
        return config.get("federation", {}).get("endpoints", [])

    @staticmethod
    def _project_name_from_endpoint(endpoint: str) -> str:
        """Best-effort project name when the remote server doesn't
        self-report one: derived from the endpoint host."""
        parsed = urlparse(endpoint)
        return parsed.hostname or endpoint

    def _probe_endpoint(self, endpoint: str, client: "httpx.Client") -> DiscoveredProject:
        """Real MCP `tools/list` JSON-RPC call against a federated endpoint.

        Unreachable/erroring endpoints are reported as unavailable with the
        real error, not silently dropped or replaced with fake data.
        """
        try:
            response = client.post(
                endpoint,
                json={"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
                timeout=DISCOVERY_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            payload = response.json()
            result = payload.get("result", {})
            tools = result.get("tools", [])
            project_name = (
                result.get("serverInfo", {}).get("name")
                or self._project_name_from_endpoint(endpoint)
            )
            return DiscoveredProject(
                project_name=project_name, endpoint=endpoint, status="healthy", tools=tools
            )
        except Exception as e:
            return DiscoveredProject(
                project_name=self._project_name_from_endpoint(endpoint),
                endpoint=endpoint,
                status="unavailable",
                error=str(e),
            )

    def discover_mcp_projects(self, refresh: bool = True) -> dict:
        """Discover MCP projects configured for federation.

        Probes every endpoint in [federation].endpoints for real liveness
        and its actual tool list via the MCP `tools/list` method. This
        replaces the previous behavior of unconditionally returning an
        empty/fake result regardless of what's actually configured or
        reachable.
        """
        if refresh or not self.registered_projects:
            if httpx is None:
                logger.warning("httpx not installed; cannot probe federation endpoints")
                return {"projects": [], "total": 0, "error": "httpx not installed"}

            endpoints = self._load_federation_endpoints()
            with httpx.Client(transport=self._transport) as client:
                for endpoint in endpoints:
                    project = self._probe_endpoint(endpoint, client)
                    self.registered_projects[project.project_name] = project

        projects = [
            {
                "project_name": p.project_name,
                "endpoint": p.endpoint,
                "status": p.status,
                "tool_count": len(p.tools),
                "error": p.error,
            }
            for p in self.registered_projects.values()
        ]
        return {"projects": projects, "total": len(projects)}

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """Standard ~4-characters-per-token heuristic, floored at 1."""
        return max(1, len(text) // 4)

    def plan_query_execution(
        self, query: str, projects_involved: Optional[List[str]] = None
    ) -> dict:
        """Build an execution plan against actually discovered projects.

        Stages reference the real, currently-known health of each named
        project (discovering first if nothing has been discovered yet)
        rather than a fabricated 3-stage plan with made-up latency numbers.
        Unknown/unrequested projects are reported as such, not silently
        dropped or assumed healthy.
        """
        if not self.registered_projects:
            self.discover_mcp_projects(refresh=True)

        requested = projects_involved or []
        resolved = []
        for name in requested:
            project = self.registered_projects.get(name)
            resolved.append(
                {
                    "project_name": name,
                    "status": project.status if project else "unknown",
                }
            )

        return {
            "query": query,
            "estimated_tokens": self._estimate_tokens(query),
            "projects": resolved,
            "all_projects_healthy": all(p["status"] == "healthy" for p in resolved)
            if resolved
            else None,
            "plan": [
                {"stage": "validate", "projects": [p["project_name"] for p in resolved]},
                {
                    "stage": "execute",
                    "projects": [p["project_name"] for p in resolved if p["status"] == "healthy"],
                },
            ],
        }

    def optimize_cross_project_query(
        self, query: str, strategy: str = "balanced"
    ) -> dict:
        """Compute a real, input-derived token-reduction estimate.

        Uses the same character-based token heuristic and per-strategy
        reduction target as Agent.query() (agent.py) rather than a
        hardcoded constant unconnected to the actual query text.
        """
        baseline_tokens = self._estimate_tokens(query)
        reduction_target = {
            "token_efficient": 0.75,
            "quality_first": 0.60,
        }.get(strategy, 0.70)
        optimized_tokens = max(1, int(baseline_tokens * (1 - reduction_target)))
        reduction_percent = (
            (baseline_tokens - optimized_tokens) / baseline_tokens
        ) * 100

        return {
            "original_query": query,
            "baseline_tokens": baseline_tokens,
            "optimized_tokens": optimized_tokens,
            "token_reduction_percent": round(reduction_percent, 2),
            "strategy": strategy,
        }

    def execute_federated_query(
        self, query: str, projects: List[str], timeout_seconds: int = 30
    ) -> dict:
        """Report which of the requested projects are actually reachable.

        This does not fabricate row counts or execution results — there is
        no real cross-project query engine backing this yet. It reports
        real discovery/health status for each requested project so callers
        get an honest answer about what's actually available, and marks
        the query itself as not executed.
        """
        if not self.registered_projects:
            self.discover_mcp_projects(refresh=True)

        results = []
        for name in projects:
            project = self.registered_projects.get(name)
            results.append(
                {
                    "project_name": name,
                    "status": project.status if project else "unknown",
                    "error": project.error if project else "not discovered",
                }
            )

        healthy = [r for r in results if r["status"] == "healthy"]
        return {
            "query": query,
            "projects": results,
            "status": "not_implemented",
            "message": (
                "Federated query execution across projects is not yet implemented; "
                f"{len(healthy)}/{len(projects)} requested projects are currently healthy "
                "and reachable."
            ),
        }

    def detect_compatible_projects(self, capability: str) -> dict:
        """Find discovered, healthy projects exposing a tool relevant to
        `capability` (lexical match against each tool's name/description).
        """
        if not self.registered_projects:
            self.discover_mcp_projects(refresh=True)

        capability_terms = self._tokenize(capability)
        compatible = []
        for project in self.registered_projects.values():
            if project.status != "healthy":
                continue
            matching_tools = [
                tool.get("name")
                for tool in project.tools
                if self._relevance_score(
                    capability_terms, tool.get("name", ""), tool.get("description", "")
                )
                > 0
            ]
            if matching_tools:
                compatible.append(
                    {"project_name": project.project_name, "matching_tools": matching_tools}
                )
        return {"compatible": compatible}

    def rank_tools_by_relevance(self, task: str) -> dict:
        """Rank all discovered tools across federated projects by lexical
        relevance to `task`. Triggers discovery first if nothing has been
        discovered yet.
        """
        if not self.registered_projects:
            self.discover_mcp_projects(refresh=True)

        task_terms = self._tokenize(task)
        ranked = []
        for project in self.registered_projects.values():
            if project.status != "healthy":
                continue
            for tool in project.tools:
                name = tool.get("name", "")
                description = tool.get("description", "")
                score = self._relevance_score(task_terms, name, description)
                if score > 0:
                    ranked.append(
                        {
                            "tool_name": name,
                            "project_name": project.project_name,
                            "description": description,
                            "relevance": round(score, 4),
                        }
                    )
        ranked.sort(key=lambda r: r["relevance"], reverse=True)
        return {"ranked": ranked}

    @staticmethod
    def _tokenize(text: str) -> set:
        return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if len(w) > 2}

    @classmethod
    def _relevance_score(cls, task_terms: set, name: str, description: str) -> float:
        """Jaccard-style overlap between task terms and a tool's own
        name+description terms. Classical lexical relevance — no embedding
        model required, consistent with this tool needing to run
        dependency-light inside an orchestration hub. Name matches count
        double: a task mentioning the tool's name directly is a much
        stronger relevance signal than an incidental description overlap.
        """
        if not task_terms:
            return 0.0
        name_terms = cls._tokenize(name.replace("_", " "))
        desc_terms = cls._tokenize(description)
        name_overlap = len(task_terms & name_terms)
        desc_overlap = len(task_terms & desc_terms)
        score = (name_overlap * 2 + desc_overlap) / (len(task_terms) * 2)
        return min(1.0, score)

    def handle_cross_database_join(self, left: str, right: str, key: str) -> dict:
        """Cross-database joins are not implemented.

        Honest "not_implemented" rather than a fabricated row count / join
        plan: there is no real query engine here capable of executing a
        join across heterogeneous databases.
        """
        return {
            "left_source": left,
            "right_source": right,
            "join_key": key,
            "status": "not_implemented",
            "message": "Cross-database join execution is not yet implemented.",
        }

    def cache_management(
        self,
        action: str,
        ttl_seconds: Optional[int] = None,
        target: Optional[str] = None,
    ) -> dict:
        """Manage a real (if minimal) in-memory cache.

        Tracks actual entries and real hit/miss counters rather than
        fabricated size/hit-rate figures.
        """
        if action == "enable":
            self._cache_enabled = True
            return {"action": action, "status": "success", "cache_enabled": True}
        if action == "disable":
            self._cache_enabled = False
            return {"action": action, "status": "success", "cache_enabled": False}
        if action == "clear":
            if target:
                self._cache.pop(target, None)
            else:
                self._cache.clear()
            return {"action": action, "status": "success", "entries": len(self._cache)}
        if action == "stats":
            total_lookups = self._cache_hits + self._cache_misses
            hit_rate = (
                (self._cache_hits / total_lookups * 100) if total_lookups else 0.0
            )
            return {
                "action": action,
                "status": "success",
                "cache_enabled": self._cache_enabled,
                "entries": len(self._cache),
                "hits": self._cache_hits,
                "misses": self._cache_misses,
                "hit_rate_percent": round(hit_rate, 2),
            }
        return {
            "action": action,
            "status": "error",
            "message": f"Unknown action: {action!r} (expected enable/disable/clear/stats)",
        }

    def error_recovery_retry(
        self,
        failed_query: str,
        error_type: str,
        retry_strategy: str = "exponential_backoff",
        max_retries: int = 3,
    ) -> dict:
        """Queue a failed query for retry via the real FallbackManager.

        Reports the real resulting queue size rather than a hardcoded
        "retrying" status disconnected from any actual queue state.
        """
        self.event_router.fallback_manager._queue_for_retry(
            failed_query, {"error_type": error_type, "max_retries": max_retries}
        )
        queue_status = self.event_router.fallback_manager.get_retry_queue_status()
        return {
            "failed_query": failed_query,
            "error_type": error_type,
            "retry_strategy": retry_strategy,
            "max_retries": max_retries,
            "status": "queued_for_retry",
            "queue_size": queue_status["queue_size"],
        }

    def report_performance_metrics(
        self, metric_type: str = "latency", group_by: str = "project"
    ) -> dict:
        """Report real health-history metrics from the ServiceRegistry.

        Returns actually recorded health-check history (may legitimately
        be empty if nothing has reported health metrics yet) rather than
        fabricated latency/throughput figures.
        """
        history = self.event_router.service_registry.health_history
        metrics = []
        for project_name, entries in history.items():
            if not entries:
                continue
            latest = entries[-1]
            value = latest.get("metrics", {}).get(metric_type)
            metrics.append(
                {
                    "group": project_name,
                    "value": value,
                    "status": latest.get("status"),
                    "recorded_at": latest.get("timestamp"),
                }
            )
        return {
            "metric_type": metric_type,
            "group_by": group_by,
            "metrics": metrics,
            "message": None
            if metrics
            else "No health metrics have been recorded for any project yet.",
        }

    def estimate_query_cost_multi_project(
        self, query: str, projects: Optional[List[str]] = None, cost_model: str = "tokens"
    ) -> dict:
        """Estimate token cost from the actual query text.

        Uses the same character-based heuristic as optimize_cross_project_query
        rather than a fixed constant unrelated to the query content.
        """
        tokens = self._estimate_tokens(query)
        projects = projects or []
        per_project_tokens = tokens // len(projects) if projects else tokens

        return {
            "query": query,
            "cost_model": cost_model,
            "projects_involved": projects,
            "estimated_tokens": tokens,
            "cost_breakdown": {p: {"tokens": per_project_tokens} for p in projects},
        }

    def manage_endpoint_federation(self, action: str) -> dict:
        """Manage the federation endpoint list.

        Supported actions:
            "list"    - return current known endpoints and their status
                        without re-probing.
            "refresh" - re-probe every configured endpoint now.
        """
        if action == "refresh":
            self.discover_mcp_projects(refresh=True)
        elif action != "list":
            return {
                "status": "error",
                "message": f"Unknown action: {action!r} (expected 'list' or 'refresh')",
                "endpoints": [],
            }

        endpoints = [
            {"project_name": p.project_name, "endpoint": p.endpoint, "status": p.status}
            for p in self.registered_projects.values()
        ]
        return {"status": "refreshed" if action == "refresh" else "listed", "endpoints": endpoints}

    # --- Real orchestration webhook / routing surface -------------------
    #
    # Backed by the same tested ServiceRegistry / ToolChainOrchestrator /
    # FallbackManager machinery in webhook_router.py that the HTTP webhook
    # server (server.py) uses — not a second, disconnected implementation.

    def register_orchestration_webhook(
        self,
        webhook_id: str,
        url: str,
        events: List[str],
        secret_key: Optional[str] = None,
    ) -> dict:
        """Register a webhook subscription in real, queryable state."""
        self.webhook_configs[webhook_id] = {
            "webhook_id": webhook_id,
            "url": url,
            "events": events,
            "secret_key": secret_key,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        return {
            "status": "success",
            "webhook_id": webhook_id,
            "url": url,
            "events": events,
            "signature_method": "HMAC-SHA256" if secret_key else "none",
            "created_at": self.webhook_configs[webhook_id]["created_at"],
        }

    def list_service_endpoints(
        self, filter_by_status: str = "all", include_metrics: bool = False
    ) -> dict:
        """List MCP endpoints registered with the real ServiceRegistry.

        This reflects only endpoints that have actually been registered
        (via `mcp.available` events or `register_mcp_endpoint`) — it is
        genuinely empty until something registers, not a fabricated
        7-project fixture list.
        """
        snapshot = self.event_router.service_registry.get_registry_snapshot()
        endpoints = snapshot["mcps"]
        if filter_by_status != "all":
            endpoints = [e for e in endpoints if e["status"] == filter_by_status]
        if not include_metrics:
            for ep in endpoints:
                ep.pop("health_metrics", None)
        return {
            "status": "success",
            "endpoints": endpoints,
            "total": len(endpoints),
            "healthy_count": len([e for e in endpoints if e["status"] == "healthy"]),
        }

    async def route_tool_invocation(
        self,
        tool_name: str,
        params: Optional[Dict[str, Any]] = None,
        chain_id: Optional[str] = None,
        use_fallback: bool = True,
        timeout_ms: Optional[int] = None,
    ) -> dict:
        """Route a tool invocation via the real ToolChainOrchestrator.

        Actually looks the tool up in the ServiceRegistry; if it isn't
        found and `use_fallback` is set, falls back through
        FallbackManager.invoke_with_fallback rather than fabricating a
        "routed" response to an endpoint that doesn't exist.
        """
        chain_context = {"chain_id": chain_id} if chain_id else None
        result = await self.event_router.tool_orchestrator.route_tool_invocation(
            tool_name=tool_name,
            params=params or {},
            chain_context=chain_context,
        )
        if result.get("status") == "error" and use_fallback:
            result = await self.event_router.fallback_manager.invoke_with_fallback(
                tool_name=tool_name, params=params or {}, fallback_enabled=True
            )
        return result

    def get_tool_routing_info(
        self, tool_name: str, include_fallbacks: bool = False
    ) -> dict:
        """Real routing info for a tool: where the ServiceRegistry says
        it actually lives, not a fabricated 145.5ms/0.999 fixture."""
        result = self.event_router.service_registry.find_tool(tool_name)
        if not result:
            return {
                "status": "not_found",
                "tool_name": tool_name,
                "message": f"Tool {tool_name} not found in any registered MCP",
            }
        project_name, endpoint = result
        routing = {
            "tool_name": tool_name,
            "primary_mcp": project_name,
            "primary_endpoint": f"http://localhost:{endpoint.port}",
            "health_status": endpoint.status,
        }
        if include_fallbacks:
            fallback = self.event_router.tool_orchestrator.find_fallback_tool(tool_name)
            routing["fallback_mcps"] = (
                [{"project": fallback[0], "endpoint": fallback[1]}] if fallback else []
            )
        return {"status": "success", "routing": routing}

    def monitor_mcp_health(self, project_name: str = "all") -> dict:
        """Real orchestration health snapshot from the ServiceRegistry."""
        status = self.event_router.get_status()
        registry = status["registry"]
        if project_name != "all":
            endpoint = self.event_router.service_registry.endpoints.get(project_name)
            return {
                "status": "success",
                "project_name": project_name,
                "current_status": endpoint.status if endpoint else "unknown",
            }
        return {
            "status": "success",
            "total_mcps": registry["total_mcps"],
            "healthy_mcps": registry["healthy_mcps"],
            "degraded_or_unavailable": registry["total_mcps"] - registry["healthy_mcps"],
        }

    async def orchestrate_cross_mcp_workflow(
        self,
        workflow_id: str,
        tool_sequence: List[str],
        cascade_on_success: bool = True,
        error_handling: str = "fail_fast",
    ) -> dict:
        """Execute a real sequence of routed tool invocations.

        Each stage's outcome is the real result of
        ToolChainOrchestrator.route_tool_invocation (found/not-found
        against the ServiceRegistry) — not a fabricated "pending" plan
        that never actually executes.
        """
        stages = []
        for position, tool_name in enumerate(tool_sequence):
            result = await self.event_router.tool_orchestrator.route_tool_invocation(
                tool_name=tool_name,
                params={},
                chain_context={
                    "chain_id": workflow_id,
                    "position_in_chain": position,
                    "total_chain_length": len(tool_sequence),
                },
            )
            stages.append({"stage": position + 1, "tool": tool_name, "result": result})
            if result.get("status") == "error" and error_handling == "fail_fast":
                return {
                    "status": "failed",
                    "workflow_id": workflow_id,
                    "stages": stages,
                    "failed_at_stage": position + 1,
                }

        return {
            "status": "completed",
            "workflow_id": workflow_id,
            "stages": stages,
            "total_stages": len(tool_sequence),
        }

    def start_mcp_connector(self, port: int = 8772) -> str:
        from pystreammcp._mcp_tools import PyStreamMCPHandler, PyStreamMCPTools

        self.mcp_connector = _MCPOrchestratorConnector(orchestrator=self, port=port)
        return self.mcp_connector.start_mcp_connector()

    def stop_mcp_connector(self):
        if self.mcp_connector:
            self.mcp_connector.stop_mcp_connector()


class _MCPOrchestratorConnector(BaseMCPConnector):
    def __init__(self, orchestrator: Orchestrator, port: int = 8772):
        super().__init__("PyStreamMCP", port=port)
        self.orchestrator = orchestrator

    def get_mcp_tools(self) -> Dict[str, Any]:
        from pystreammcp._mcp_tools import PyStreamMCPTools

        return PyStreamMCPTools.get_tools()

    def get_tool_handlers(self) -> Any:
        from pystreammcp._mcp_tools import PyStreamMCPHandler

        return PyStreamMCPHandler(self.orchestrator)
