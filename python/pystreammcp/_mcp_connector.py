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
            return {
                "runtime": {
                    "host": "0.0.0.0",
                    "port": self.port,
                    "cors": {"origins": ["*"]},
                },
                "entities": {
                    k: {
                        "source": k,
                        "permissions": [{"actions": ["*"], "roles": ["*"]}],
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

    def plan_query_execution(self, query: str) -> dict:
        return {"plan": []}

    def optimize_cross_project_query(self, query: str) -> dict:
        return {"optimized": query}

    def execute_federated_query(self, query: str, projects: list) -> dict:
        return {"results": []}

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
        return {"joined": {}}

    def cache_management(self, action: str) -> dict:
        return {"cache": {}}

    def error_recovery_retry(self, query: str, error: str) -> dict:
        return {"status": "retrying"}

    def report_performance_metrics(self, metric_type: str) -> dict:
        return {"metrics": []}

    def estimate_query_cost_multi_project(self, query: str) -> dict:
        return {"cost": 0}

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
