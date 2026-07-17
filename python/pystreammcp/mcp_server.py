"""MCP (Model Context Protocol) server for PyStreamMCP.

Implements the Model Context Protocol standard to expose
query planning, discovery, and optimization as MCP tools.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from .agent import Agent


logger = logging.getLogger(__name__)


@dataclass
class MCPTool:
    """MCP tool definition."""
    name: str
    description: str
    input_schema: Dict[str, Any]


class PyStreamMCPServer:
    """MCP server implementing PyStreamMCP protocol."""

    def __init__(self, agent_id: str = "mcp_agent"):
        """Initialize MCP server.

        Args:
            agent_id: Agent ID for this server
        """
        self.agent_id = agent_id
        self.agent = Agent(
            agent_id=agent_id,
            name=f"MCP Agent: {agent_id}",
            optimization_strategy="balanced",
            max_tokens=2000,
        )
        self.tools = self._define_tools()

    def _define_tools(self) -> Dict[str, MCPTool]:
        """Define MCP tools."""
        return {
            "query": MCPTool(
                name="pystreammcp_query",
                description="Execute a query with PyStreamMCP optimization and discover relevant context",
                input_schema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The query text",
                        },
                        "intent": {
                            "type": "string",
                            "enum": ["retrieve", "discover", "aggregate", "synthesize", "analyze"],
                            "description": "Query intent - what the agent is trying to do",
                        },
                        "max_tokens": {
                            "type": "integer",
                            "description": "Maximum tokens for context (overrides default)",
                        },
                    },
                    "required": ["text"],
                },
            ),
            "discover": MCPTool(
                name="pystreammcp_discover",
                description="Discover relevant data sources and context for a query",
                input_schema={
                    "type": "object",
                    "properties": {
                        "context": {
                            "type": "string",
                            "description": "Context for discovery",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum sources to return",
                        },
                    },
                    "required": ["context"],
                },
            ),
            "optimize": MCPTool(
                name="pystreammcp_optimize",
                description="Optimize a query for cost reduction while maintaining quality",
                input_schema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Query to optimize",
                        },
                        "strategy": {
                            "type": "string",
                            "enum": ["balanced", "token_efficient", "quality_first"],
                            "description": "Optimization strategy",
                        },
                    },
                    "required": ["text"],
                },
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

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool result

        Raises:
            ValueError: If tool not found
        """
        if name == "pystreammcp_query":
            return self._tool_query(arguments)
        elif name == "pystreammcp_discover":
            return self._tool_discover(arguments)
        elif name == "pystreammcp_optimize":
            return self._tool_optimize(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")

    def _tool_query(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute query tool."""
        text = args.get("text")
        intent = args.get("intent", "retrieve")
        max_tokens = args.get("max_tokens")

        if not text:
            return {
                "status": "error",
                "message": "text parameter required",
            }

        result = self.agent.query(text)

        return {
            "status": "success",
            "query_id": result.query_id,
            "text": text,
            "intent": intent,
            "baseline_tokens": result.baseline_tokens,
            "optimized_tokens": result.optimized_tokens,
            "cost_reduction_percent": result.cost_reduction_percent,
            "execution_time_ms": result.execution_time_ms,
            "context": {
                "description": "Context optimized for the query",
                "recommendation": f"Use this context for {intent} queries",
            },
        }

    def _tool_discover(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute discovery tool."""
        context = args.get("context")
        limit = args.get("limit", 10)

        if not context:
            return {
                "status": "error",
                "message": "context parameter required",
            }

        # TODO: Implement actual discovery logic
        sources = [
            {
                "name": f"source_{i}",
                "relevance": 0.95 - (i * 0.05),
                "type": "database",
            }
            for i in range(min(limit, 5))
        ]

        return {
            "status": "success",
            "sources": sources,
            "total_sources": len(sources),
        }

    def _tool_optimize(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute optimization tool."""
        text = args.get("text")
        strategy = args.get("strategy", "balanced")

        if not text:
            return {
                "status": "error",
                "message": "text parameter required",
            }

        result = self.agent.query(text)

        return {
            "status": "success",
            "query_id": result.query_id,
            "baseline_tokens": result.baseline_tokens,
            "optimized_tokens": result.optimized_tokens,
            "cost_reduction_percent": result.cost_reduction_percent,
            "strategy_used": strategy,
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
            return self.call_tool(tool_name, tool_args)

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
