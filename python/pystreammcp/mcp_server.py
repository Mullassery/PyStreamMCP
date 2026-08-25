"""MCP (Model Context Protocol) server for PyStreamMCP.

Implements the Model Context Protocol standard to expose
query planning, discovery, and optimization as MCP tools.
"""

import logging
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


_TOOL_ARG_MODELS: Dict[str, Type[BaseModel]] = {
    "pystreammcp_query": QueryToolArgs,
    "pystreammcp_discover": DiscoverToolArgs,
    "pystreammcp_register_source": RegisterSourceToolArgs,
    "pystreammcp_optimize": OptimizeToolArgs,
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


@dataclass
class MCPTool:
    """MCP tool definition."""

    name: str
    description: str
    input_schema: Dict[str, Any]


class PyStreamMCPServer:
    """MCP server implementing PyStreamMCP protocol."""

    def __init__(self, agent_id: str = "mcp_agent", agent: Optional[Agent] = None):
        """Initialize MCP server.

        Args:
            agent_id: Agent ID for this server (ignored if `agent` is given)
            agent: Optional pre-built `Agent` (or any object exposing a
                compatible `.query(text)` method) to use instead of
                constructing a default one. Mainly for tests that need to
                inject controlled failure behavior (rate limits, malformed
                responses, etc.) into the tool-execution path.
        """
        self.agent_id = agent_id
        self.agent = agent or Agent(
            agent_id=agent_id,
            name=f"MCP Agent: {agent_id}",
            optimization_strategy="balanced",
            max_tokens=2000,
        )
        self.registry = SourceRegistry()
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

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
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
            return {
                "type": "info",
                "name": "PyStreamMCP",
                "version": "0.2.0",
                "capabilities": ["query", "discover", "optimize"],
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
