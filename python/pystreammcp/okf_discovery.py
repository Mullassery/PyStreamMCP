"""OKF discovery exporter for PyStreamMCP.

Converts discovered MCP systems and tools into OKF documents.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from .okf_core import OKFCatalog, OKFDocType


class MCPSystemToOKF:
    """Convert an MCP system to OKF document format."""

    @staticmethod
    def render(system_id: str, name: str, description: str,
              tools_count: int, cost_per_query: float = 0.0,
              latency_p99_ms: int = 0, metadata: Optional[Dict[str, Any]] = None) -> tuple[str, Dict[str, Any]]:
        """Render an MCP system as OKF document.

        Args:
            system_id: Unique system identifier
            name: Human-readable system name
            description: Brief description
            tools_count: Number of tools available
            cost_per_query: Average cost per query
            latency_p99_ms: p99 latency in milliseconds
            metadata: Additional metadata

        Returns:
            Tuple of (content, metadata_dict)
        """
        if metadata is None:
            metadata = {}

        content = f"""# {name}

## Overview
{description}

## System Profile
- **Tools Available:** {tools_count}
- **Cost per Query:** ${cost_per_query:.4f}
- **Latency (p99):** {latency_p99_ms}ms

## Usage
Refer to individual tool documentation for API details and parameters.
"""

        okf_metadata = {
            "type": OKFDocType.MCP_SYSTEM,
            "system_id": system_id,
            "tools_count": tools_count,
            "cost_per_query": cost_per_query,
            "latency_p99_ms": latency_p99_ms,
            "tags": metadata.get("tags", []),
            **{k: v for k, v in metadata.items() if k not in ["tags"]},
        }

        return content, okf_metadata


class MCPToolToOKF:
    """Convert an MCP tool to OKF document format."""

    @staticmethod
    def render(tool_id: str, name: str, description: str,
              system_id: str, cost: float = 0.0,
              latency_p95_ms: int = 0,
              parameters: Optional[Dict[str, Any]] = None,
              returns: Optional[Dict[str, Any]] = None,
              metadata: Optional[Dict[str, Any]] = None) -> tuple[str, Dict[str, Any]]:
        """Render an MCP tool as OKF document.

        Args:
            tool_id: Unique tool identifier
            name: Human-readable tool name
            description: Tool description
            system_id: ID of parent MCP system
            cost: Cost per call
            latency_p95_ms: p95 latency in milliseconds
            parameters: Parameter schema
            returns: Return value schema
            metadata: Additional metadata

        Returns:
            Tuple of (content, metadata_dict)
        """
        if metadata is None:
            metadata = {}
        if parameters is None:
            parameters = {}
        if returns is None:
            returns = {}

        # Render parameters section
        params_section = ""
        if parameters:
            params_section = "## Parameters\n```json\n"
            for param_name, param_info in parameters.items():
                param_type = param_info.get("type", "string")
                param_desc = param_info.get("description", "")
                params_section += f'  "{param_name}": {{"type": "{param_type}", "description": "{param_desc}"}},\n'
            params_section += "```\n"

        # Render returns section
        returns_section = ""
        if returns:
            returns_section = "## Returns\n```json\n"
            for field_name, field_info in returns.items():
                field_type = field_info.get("type", "string")
                returns_section += f'  "{field_name}": {{"type": "{field_type}"}},\n'
            returns_section += "```\n"

        content = f"""# {name}

## Description
{description}

## Cost & Performance
- **Cost per call:** ${cost:.4f}
- **Latency (p95):** {latency_p95_ms}ms

{params_section}{returns_section}
## Related
- System: [[{system_id}.md]]
"""

        okf_metadata = {
            "type": OKFDocType.MCP_TOOL,
            "tool_id": tool_id,
            "system": system_id,
            "cost": cost,
            "latency_p95_ms": latency_p95_ms,
            "parameter_count": len(parameters),
            "tags": metadata.get("tags", []),
            **{k: v for k, v in metadata.items() if k not in ["tags"]},
        }

        return content, okf_metadata


class DiscoveryOKFExporter:
    """Export discovered MCP systems and tools as OKF documents."""

    def __init__(self, catalog: OKFCatalog):
        """Initialize exporter with target catalog.

        Args:
            catalog: OKFCatalog instance to export to
        """
        self.catalog = catalog

    def export_system(self, system_id: str, name: str, description: str,
                     tools_count: int, cost_per_query: float = 0.0,
                     latency_p99_ms: int = 0,
                     metadata: Optional[Dict[str, Any]] = None) -> str:
        """Export an MCP system as OKF document.

        Args:
            system_id: Unique system identifier
            name: Human-readable system name
            description: Brief description
            tools_count: Number of tools available
            cost_per_query: Average cost per query
            latency_p99_ms: p99 latency in milliseconds
            metadata: Additional metadata

        Returns:
            Path to saved document
        """
        content, okf_metadata = MCPSystemToOKF.render(
            system_id, name, description, tools_count,
            cost_per_query, latency_p99_ms, metadata
        )

        path = self.catalog.save_document(
            OKFDocType.MCP_SYSTEM,
            name,
            content,
            okf_metadata
        )

        return str(path)

    def export_tool(self, tool_id: str, name: str, description: str,
                   system_id: str, cost: float = 0.0,
                   latency_p95_ms: int = 0,
                   parameters: Optional[Dict[str, Any]] = None,
                   returns: Optional[Dict[str, Any]] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """Export an MCP tool as OKF document.

        Args:
            tool_id: Unique tool identifier
            name: Human-readable tool name
            description: Tool description
            system_id: ID of parent MCP system
            cost: Cost per call
            latency_p95_ms: p95 latency in milliseconds
            parameters: Parameter schema
            returns: Return value schema
            metadata: Additional metadata

        Returns:
            Path to saved document
        """
        content, okf_metadata = MCPToolToOKF.render(
            tool_id, name, description, system_id,
            cost, latency_p95_ms, parameters, returns, metadata
        )

        path = self.catalog.save_document(
            OKFDocType.MCP_TOOL,
            name,
            content,
            okf_metadata
        )

        return str(path)

    def export_query_plan(self, plan_id: str, objective: str,
                         steps: List[Dict[str, Any]],
                         estimated_token_savings: float = 0.0,
                         estimated_cost_savings: float = 0.0,
                         metadata: Optional[Dict[str, Any]] = None) -> str:
        """Export a query optimization plan as OKF document.

        Args:
            plan_id: Unique plan identifier
            objective: What the plan aims to achieve
            steps: List of query steps with costs
            estimated_token_savings: Expected token reduction (%)
            estimated_cost_savings: Expected cost reduction ($)
            metadata: Additional metadata

        Returns:
            Path to saved document
        """
        if metadata is None:
            metadata = {}

        steps_section = "## Steps\n"
        for i, step in enumerate(steps, 1):
            steps_section += f"""### Step {i}: {step.get('description', 'Query step')}
- Cost: ${step.get('cost', 0):.4f}
- Latency: {step.get('latency_ms', 0)}ms
- Token Cost: {step.get('token_cost', 0)}

"""

        content = f"""# {objective}

## Optimization Plan

**Token Savings:** {estimated_token_savings:.1f}%
**Cost Savings:** ${estimated_cost_savings:.2f}

{steps_section}
"""

        okf_metadata = {
            "type": OKFDocType.QUERY_PLAN,
            "plan_id": plan_id,
            "estimated_token_savings": estimated_token_savings,
            "estimated_cost_savings": estimated_cost_savings,
            "step_count": len(steps),
            "tags": metadata.get("tags", []),
            **{k: v for k, v in metadata.items() if k not in ["tags"]},
        }

        path = self.catalog.save_document(
            OKFDocType.QUERY_PLAN,
            objective,
            content,
            okf_metadata
        )

        return str(path)
