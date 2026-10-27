"""MCP (Model Context Protocol) server for PyStreamMCP.

Implements the Model Context Protocol standard to expose
query planning, discovery, and optimization as MCP tools.
"""

import logging
import os
from typing import Any, Dict, List, Literal, Optional, Type
from dataclasses import dataclass

from pydantic import BaseModel, Field, ValidationError

from .agent import Agent
from .discovery import SourceRegistry


logger = logging.getLogger(__name__)


# ── MCP tool argument schemas ────────────────────────────────────────────────
#
# Previously `call_tool`/`_tool_*` only did manual `if not text: return error`
# checks per field -- no type checking (a `max_tokens` of "ten" would pass
# straight through to `int()` arithmetic downstream), no enum validation (an
# `intent`/`strategy` of anything at all was accepted despite the JSON schema
# below advertising a fixed enum), and no consistent required-field handling
# across the four tools. These models are now both the single source of
# truth for `input_schema` (via `model_json_schema()`) and the actual runtime
# validation, so the two can no longer silently drift apart the way a
# hand-duplicated dict schema could.


class QueryToolArgs(BaseModel):
    text: str = Field(..., min_length=1, description="The query text")
    intent: Literal["retrieve", "discover", "aggregate", "synthesize", "analyze"] = Field(
        "retrieve", description="Query intent - what the agent is trying to do"
    )
    max_tokens: Optional[int] = Field(
        None, gt=0, description="Maximum tokens for context (overrides default)"
    )


class DiscoverToolArgs(BaseModel):
    context: str = Field(..., min_length=1, description="Context for discovery")
    limit: int = Field(10, gt=0, le=1000, description="Maximum sources to return")


class RegisterSourceToolArgs(BaseModel):
    name: str = Field(..., min_length=1, description="Unique source name")
    description: str = Field(
        ..., min_length=1, description="What this source contains, in plain text"
    )
    type: str = Field("unknown", description="Source type, e.g. database, api, docs")
    tags: List[str] = Field(default_factory=list, description="Optional keyword tags")


class OptimizeToolArgs(BaseModel):
    text: str = Field(..., min_length=1, description="Query to optimize")
    strategy: Literal["balanced", "token_efficient", "quality_first"] = Field(
        "balanced", description="Optimization strategy"
    )


class CrawlToolArgs(BaseModel):
    url: str = Field(..., min_length=1, description="Seed URL to crawl (http/https)")
    depth: int = Field(1, ge=0, le=5, description="Maximum link-following depth")
    max_urls: int = Field(
        25, gt=0, le=500, description="Stop after fetching this many URLs"
    )
    same_domain: bool = Field(
        True, description="Restrict the crawl to the seed URL's domain"
    )
    render_js: bool = Field(
        False,
        description="Render JS-dependent pages in headless Chrome (slow; needs Chrome)",
    )
    timeout_secs: int = Field(30, gt=0, le=120, description="Per-request timeout")
    max_response_bytes: int = Field(
        5_000_000, gt=0, description="Per-response size cap, in bytes"
    )


class RetrievalSearchToolArgs(BaseModel):
    query: str = Field(..., min_length=1, max_length=8000)
    backend: Literal["auto", "qmd", "rag_anything", "all"] = "auto"
    mode: Optional[str] = Field(None, max_length=32)
    collections: List[str] = Field(default_factory=list, max_length=32)
    content_type: Optional[
        Literal[
            "text",
            "image",
            "table",
            "equation",
            "document",
            "pdf",
            "audio",
            "video",
        ]
    ] = None
    limit: int = Field(5, ge=1, le=50)
    include_content: bool = False
    max_content_chars: int = Field(2000, ge=0, le=20000)
    time_budget_ms: int = Field(30000, ge=1, le=300000)
    intent: Optional[str] = Field(None, max_length=1000)


class RetrievalCapabilitiesToolArgs(BaseModel):
    include_health: bool = True


class RagIngestToolArgs(BaseModel):
    path: str = Field(..., min_length=1)
    force_multimodal: bool = False


_TOOL_ARG_MODELS: Dict[str, Type[BaseModel]] = {
    "pystreammcp_query": QueryToolArgs,
    "pystreammcp_discover": DiscoverToolArgs,
    "pystreammcp_register_source": RegisterSourceToolArgs,
    "pystreammcp_optimize": OptimizeToolArgs,
    "pystreammcp_crawl": CrawlToolArgs,
    "pystreammcp_retrieval_search": RetrievalSearchToolArgs,
    "pystreammcp_retrieval_capabilities": RetrievalCapabilitiesToolArgs,
    "pystreammcp_rag_ingest": RagIngestToolArgs,
}


def _validation_error_response(name: str, error: ValidationError) -> Dict[str, Any]:
    return {
        "status": "error",
        "message": f"Invalid arguments for tool '{name}'",
        "validation_errors": [
            {
                "field": ".".join(str(p) for p in e["loc"]),
                "issue": e["msg"],
                "type": e["type"],
            }
            for e in error.errors()
        ],
    }


def _retrieval_error_response(error: Any) -> Dict[str, Any]:
    backend = getattr(error, "backend", None)
    return {
        "status": "error",
        "error_type": "RetrievalError",
        "code": error.code,
        "message": error.message,
        "backend": getattr(backend, "value", backend),
        "retryable": error.retryable,
    }


@dataclass
class MCPTool:
    """MCP tool definition."""

    name: str
    description: str
    input_schema: Dict[str, Any]


class PyStreamMCPServer:
    """MCP server implementing PyStreamMCP protocol."""

    def __init__(
        self,
        agent_id: str = "mcp_agent",
        agent: Optional[Agent] = None,
        retrieval_service: Optional[Any] = None,
    ):
        """Initialize MCP server.

        Args:
            agent_id: Agent ID for this server (ignored if `agent` is given)
            agent: Optional pre-built `Agent` (or any object exposing a
                compatible `.query(text)` method) to use instead of
                constructing a default one. Mainly for tests that need to
                inject controlled failure behavior (rate limits, malformed
                responses, etc.) into the tool-execution path.
            retrieval_service: Optional pre-built `RetrievalService` (or
                compatible object) to use instead of constructing one from
                the environment on first retrieval call.
        """
        self.agent_id = agent_id
        self.agent = agent or Agent(
            agent_id=agent_id,
            name=f"MCP Agent: {agent_id}",
            optimization_strategy="balanced",
            max_tokens=2000,
        )
        self.registry = SourceRegistry()
        self._retrieval_service = retrieval_service
        self._retrieval_closed = False
        self.tools = self._define_tools()

    def _define_tools(self) -> Dict[str, MCPTool]:
        """Define MCP tools. `input_schema` is generated from the Pydantic
        arg models above, so the advertised schema and the schema actually
        enforced at call time can't drift apart."""
        return {
            "query": MCPTool(
                name="pystreammcp_query",
                description="Execute a query with PyStreamMCP optimization and discover relevant context",
                input_schema=QueryToolArgs.model_json_schema(),
            ),
            "discover": MCPTool(
                name="pystreammcp_discover",
                description="Discover relevant data sources and context for a query",
                input_schema=DiscoverToolArgs.model_json_schema(),
            ),
            "register_source": MCPTool(
                name="pystreammcp_register_source",
                description="Register a data source (name, description, tags) so pystreammcp_discover can find it",
                input_schema=RegisterSourceToolArgs.model_json_schema(),
            ),
            "optimize": MCPTool(
                name="pystreammcp_optimize",
                description="Optimize a query for cost reduction while maintaining quality",
                input_schema=OptimizeToolArgs.model_json_schema(),
            ),
            "crawl": MCPTool(
                name="pystreammcp_crawl",
                description=(
                    "Fetch and crawl a website (SSRF-safe, budget-bounded) and return its "
                    "pages and links. Optional headless-Chrome rendering for JS pages."
                ),
                input_schema=CrawlToolArgs.model_json_schema(),
            ),
            "retrieval_search": MCPTool(
                name="pystreammcp_retrieval_search",
                description=(
                    "Search the configured QMD and RAG-Anything retrieval backends "
                    "with normalized provenance."
                ),
                input_schema=RetrievalSearchToolArgs.model_json_schema(),
            ),
            "retrieval_capabilities": MCPTool(
                name="pystreammcp_retrieval_capabilities",
                description=(
                    "Report retrieval backend capabilities and optionally health "
                    "without loading models."
                ),
                input_schema=RetrievalCapabilitiesToolArgs.model_json_schema(),
            ),
            "rag_ingest": MCPTool(
                name="pystreammcp_rag_ingest",
                description="Ingest an allowed local document into the RAG-Anything index.",
                input_schema=RagIngestToolArgs.model_json_schema(),
            ),
        }

    def get_tools(self) -> List[Dict[str, Any]]:
        """Get available tools in MCP format.

        Returns:
            List of tool definitions
        """
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.input_schema,
            }
            for tool in self.tools.values()
        ]

    def call_tool(
        self,
        name: str,
        arguments: Dict[str, Any],
        auth_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Call a tool by name.

        Validates `arguments` against the tool's Pydantic arg model before
        dispatch (returning a structured `validation_errors` response on
        failure, rather than letting a wrong type or invalid enum value
        flow through to the handler unchecked), and isolates the handler
        call in a try/except so a failure during execution -- a bug, or a
        downstream dependency (e.g. a real LLM/framework adapter wired in
        via `agent=`) hitting a rate limit, context-window overrun, or
        returning malformed data -- produces a structured error response
        instead of propagating out of `call_tool` uncaught.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool result

        Raises:
            ValueError: If tool not found
        """
        import hmac
        import os

        expected = os.environ.get("PYSTREAMMCP_API_KEY")
        if expected and (not auth_token or not hmac.compare_digest(auth_token, expected)):
            return {
                "status": "error",
                "message": "invalid or missing MCP auth token",
                "error_type": "AuthenticationError",
            }

        model = _TOOL_ARG_MODELS.get(name)
        if model is None:
            raise ValueError(f"Unknown tool: {name}")

        try:
            validated = model(**arguments)
        except ValidationError as e:
            return _validation_error_response(name, e)

        handler = {
            "pystreammcp_query": self._tool_query,
            "pystreammcp_discover": self._tool_discover,
            "pystreammcp_register_source": self._tool_register_source,
            "pystreammcp_optimize": self._tool_optimize,
            "pystreammcp_crawl": self._tool_crawl,
            "pystreammcp_retrieval_search": self._tool_retrieval_search,
            "pystreammcp_retrieval_capabilities": self._tool_retrieval_capabilities,
            "pystreammcp_rag_ingest": self._tool_rag_ingest,
        }[name]

        try:
            return handler(validated)
        except Exception as e:
            logger.exception(f"Tool '{name}' failed during execution")
            return {
                "status": "error",
                "message": f"Tool '{name}' failed during execution: {e}",
                "error_type": type(e).__name__,
            }

    def _tool_query(self, args: QueryToolArgs) -> Dict[str, Any]:
        """Execute query tool."""
        result = self.agent.query(args.text)

        return {
            "status": "success",
            "query_id": result.query_id,
            "text": args.text,
            "intent": args.intent,
            "baseline_tokens": result.baseline_tokens,
            "optimized_tokens": result.optimized_tokens,
            "cost_reduction_percent": result.cost_reduction_percent,
            "execution_time_ms": result.execution_time_ms,
            "context": {
                "description": "Context optimized for the query",
                "recommendation": f"Use this context for {args.intent} queries",
            },
        }

    def _tool_discover(self, args: DiscoverToolArgs) -> Dict[str, Any]:
        """Execute discovery tool.

        Ranks *registered* sources (see pystreammcp_register_source) by
        real token overlap against `context`. Returns an empty list if
        nothing is registered or nothing overlaps — never fabricated data.
        """
        sources = self.registry.discover(args.context, limit=args.limit)

        return {
            "status": "success",
            "sources": sources,
            "total_sources": len(sources),
        }

    def _tool_register_source(self, args: RegisterSourceToolArgs) -> Dict[str, Any]:
        """Register a data source for discovery."""
        self.registry.register(
            name=args.name,
            description=args.description,
            type=args.type,
            tags=args.tags,
        )

        return {"status": "success", "name": args.name}

    def _tool_optimize(self, args: OptimizeToolArgs) -> Dict[str, Any]:
        """Execute optimization tool."""
        result = self.agent.query(args.text)

        return {
            "status": "success",
            "query_id": result.query_id,
            "baseline_tokens": result.baseline_tokens,
            "optimized_tokens": result.optimized_tokens,
            "cost_reduction_percent": result.cost_reduction_percent,
            "strategy_used": args.strategy,
            "techniques": [
                "pruning",
                "summarization",
                "caching",
                "early_termination",
            ],
        }

    def _tool_crawl(self, args: CrawlToolArgs) -> Dict[str, Any]:
        """Fetch and crawl a website with MudFish and return its pages.

        `mudfish` (the Rust engine's native Python binding) is an optional
        dependency -- install it with `pip install mudfish` or
        `pip install PyStreamMCP[crawl]`. When it isn't installed this returns
        a structured error naming the fix instead of a bare ImportError. The
        crawl itself is SSRF-safe (resolved-address filtering) and
        budget-bounded (`max_urls`), so it is safe to hand arbitrary
        user/agent-supplied URLs.
        """
        try:
            import mudfish
        except ImportError:
            return {
                "status": "error",
                "error_type": "MissingDependency",
                "message": (
                    "Web crawling requires the optional 'mudfish' package. "
                    "Install it with `pip install mudfish` (or "
                    "`pip install PyStreamMCP[crawl]`)."
                ),
            }

        result = mudfish.crawl(
            args.url,
            depth=args.depth,
            same_domain=args.same_domain,
            max_urls=args.max_urls,
            timeout_secs=args.timeout_secs,
            max_response_bytes=args.max_response_bytes,
            render_js=args.render_js,
        )

        pages = [
            {
                "url": page.url,
                "status_code": page.status_code,
                "title": page.title,
                "links": len(page.links) if page.links is not None else 0,
            }
            for page in result
        ]
        stats = result.stats

        return {
            "status": "success",
            "url": args.url,
            "pages": pages,
            "total_pages": len(pages),
            "stats": {
                "urls_discovered": stats.urls_discovered,
                "urls_fetched": stats.urls_fetched,
                "urls_skipped": stats.urls_skipped,
                "bytes_downloaded": stats.bytes_downloaded,
                "duration_secs": stats.duration_secs,
            },
        }

    def _get_retrieval_service(self) -> Any:
        if self._retrieval_service is None:
            from .retrieval.service import RetrievalService

            self._retrieval_service = RetrievalService.from_env()
        return self._retrieval_service

    def _retrieval_capability_configured(self) -> bool:
        if self._retrieval_service is not None:
            return True
        truthy = {"1", "true", "yes", "on"}
        return any(
            os.environ.get(name, "").strip().lower() in truthy
            for name in (
                "PYSTREAMMCP_QMD_ENABLED",
                "PYSTREAMMCP_RAG_ENABLED",
            )
        )

    def _tool_retrieval_search(self, args: RetrievalSearchToolArgs) -> Dict[str, Any]:
        from .retrieval.errors import RetrievalError
        from .retrieval.models import RequestedBackend, RetrievalRequest

        request = RetrievalRequest(
            query=args.query,
            backend=RequestedBackend(args.backend),
            mode=args.mode,
            collections=tuple(args.collections),
            content_type=args.content_type,
            limit=args.limit,
            include_content=args.include_content,
            max_content_chars=args.max_content_chars,
            time_budget_ms=args.time_budget_ms,
            intent=args.intent,
        )
        try:
            return self._get_retrieval_service().search(request).to_dict()
        except RetrievalError as error:
            return _retrieval_error_response(error)

    def _tool_retrieval_capabilities(
        self, args: RetrievalCapabilitiesToolArgs
    ) -> Dict[str, Any]:
        from .retrieval.errors import RetrievalError

        try:
            return self._get_retrieval_service().capabilities(
                include_health=args.include_health
            )
        except RetrievalError as error:
            return _retrieval_error_response(error)

    def _tool_rag_ingest(self, args: RagIngestToolArgs) -> Dict[str, Any]:
        from .retrieval.errors import RetrievalError

        try:
            return self._get_retrieval_service().ingest(
                args.path, force_multimodal=args.force_multimodal
            ).to_dict()
        except RetrievalError as error:
            return _retrieval_error_response(error)

    def close(self) -> None:
        if self._retrieval_service is not None and not self._retrieval_closed:
            self._retrieval_closed = True
            self._retrieval_service.close()

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process an MCP message.

        Args:
            message: MCP message

        Returns:
            MCP response
        """
        message_type = message.get("type")

        if message_type == "call_tool":
            tool_name = message.get("name")
            tool_args = message.get("arguments", {})
            try:
                return self.call_tool(tool_name, tool_args)
            except ValueError as e:
                # Unknown tool name -- call_tool's own validation/execution
                # error paths already return structured dicts; this is the
                # one case it still raises (see its docstring), and
                # process_message is the actual message-transport entry
                # point, so an unrecognized tool name shouldn't crash the
                # whole call.
                return {"status": "error", "message": str(e)}

        elif message_type == "list_tools":
            return {
                "type": "tools",
                "tools": self.get_tools(),
            }

        elif message_type == "get_info":
            capabilities = ["query", "discover", "optimize", "crawl"]
            if self._retrieval_capability_configured():
                capabilities.append("retrieval")
            return {
                "type": "info",
                "name": "PyStreamMCP",
                "version": "0.2.0",
                "capabilities": capabilities,
            }

        else:
            return {
                "status": "error",
                "message": f"Unknown message type: {message_type}",
            }


async def create_mcp_server(agent_id: str = "mcp_agent") -> PyStreamMCPServer:
    """Factory function to create MCP server.

    Args:
        agent_id: Agent ID

    Returns:
        MCP server instance
    """
    return PyStreamMCPServer(agent_id)
