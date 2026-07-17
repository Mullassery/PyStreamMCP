"""No-code and RPA tool integrations for PyStreamMCP.

Enables n8n, Power Automate, UiPath, and Automation Anywhere
to integrate PyStreamMCP for intelligent workflow automation.
"""

from typing import Dict, Any, Optional
import json

from pystreammcp import Agent


class N8nWebhookTrigger:
    """n8n webhook trigger for PyStreamMCP operations.

    n8n integrates via webhook nodes that call HTTP endpoints.
    This class represents the PyStreamMCP endpoint.

    Usage in n8n:
    1. Add HTTP Request node
    2. Set URL to: http://localhost:8000/n8n/query
    3. Add query in body: {"text": "your query", "agent_id": "agent_1"}
    """

    def __init__(self, agent_id: str = "n8n_agent"):
        """Initialize webhook trigger.

        Args:
            agent_id: PyStreamMCP agent ID
        """
        self.agent_id = agent_id

    def handle_query(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming webhook request.

        Args:
            body: Request body from n8n

        Returns:
            Response for n8n workflow
        """
        query_text = body.get("text", "")
        intent = body.get("intent", "retrieve")

        if not query_text:
            return {"error": "Missing 'text' parameter"}

        agent = Agent(agent_id=self.agent_id)
        result = agent.query(query_text)

        return {
            "query_id": result.query_id,
            "text": query_text,
            "intent": intent,
            "baseline_tokens": result.baseline_tokens,
            "optimized_tokens": result.optimized_tokens,
            "cost_reduction": result.cost_reduction_percent,
            "cost_saved": (result.baseline_tokens - result.optimized_tokens) * 0.00001,
            "execution_time_ms": result.execution_time_ms,
            "success": True,
        }

    def handle_discovery(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """Handle discovery webhook."""
        context = body.get("context", "")

        if not context:
            return {"error": "Missing 'context' parameter"}

        return {
            "context": context,
            "sources": [
                {
                    "name": f"source_{i}",
                    "relevance": 0.95 - (i * 0.05),
                    "type": "data_source",
                }
                for i in range(5)
            ],
            "total_sources": 5,
            "success": True,
        }

    def get_webhook_spec(self) -> Dict[str, Any]:
        """Get OpenAPI spec for n8n webhook registration."""
        return {
            "name": "PyStreamMCP",
            "version": "1.0.0",
            "endpoints": [
                {
                    "name": "query",
                    "url": "/n8n/query",
                    "method": "POST",
                    "description": "Execute optimized query",
                    "parameters": {
                        "text": {"type": "string", "required": True},
                        "intent": {"type": "string", "enum": ["retrieve", "discover", "optimize"]},
                    },
                },
                {
                    "name": "discover",
                    "url": "/n8n/discover",
                    "method": "POST",
                    "description": "Discover data sources",
                    "parameters": {
                        "context": {"type": "string", "required": True},
                    },
                },
            ],
        }


class PowerAutomateConnector:
    """Microsoft Power Automate connector for PyStreamMCP.

    Power Automate integrates via HTTP connector + custom connectors.
    This class provides the connector interface.

    Usage in Power Automate:
    1. Add HTTP action (or create custom connector)
    2. Set endpoint: https://api.example.com/power-automate/query
    3. Add headers: {"Content-Type": "application/json"}
    4. Pass body: {"text": "query", "agent_id": "agent_1"}
    """

    def __init__(self, api_base: str = "https://api.example.com"):
        """Initialize Power Automate connector.

        Args:
            api_base: API base URL
        """
        self.api_base = api_base

    def query(self, text: str, agent_id: str) -> Dict[str, Any]:
        """Execute query via Power Automate.

        Args:
            text: Query text
            agent_id: Agent ID

        Returns:
            Query result
        """
        agent = Agent(agent_id=agent_id)
        result = agent.query(text)

        return {
            "status": "success",
            "queryId": result.query_id,
            "text": text,
            "baselineTokens": result.baseline_tokens,
            "optimizedTokens": result.optimized_tokens,
            "costReduction": result.cost_reduction_percent,
            "executionTimeMs": result.execution_time_ms,
        }

    def get_custom_connector_spec(self) -> Dict[str, Any]:
        """Get OpenAPI spec for Power Automate custom connector."""
        return {
            "swagger": "2.0",
            "info": {
                "title": "PyStreamMCP",
                "version": "1.0.0",
                "description": "Intelligent query optimization and cost reduction",
            },
            "host": "api.example.com",
            "basePath": "/power-automate",
            "schemes": ["https"],
            "consumes": ["application/json"],
            "produces": ["application/json"],
            "paths": {
                "/query": {
                    "post": {
                        "summary": "Execute optimized query",
                        "parameters": [
                            {
                                "name": "body",
                                "in": "body",
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "text": {"type": "string"},
                                        "agentId": {"type": "string"},
                                    },
                                },
                            }
                        ],
                        "responses": {
                            "200": {"description": "Query executed successfully"}
                        },
                    }
                }
            },
        }


class RoboticProcessAdapter:
    """Adapter for RPA platforms (UiPath, Automation Anywhere).

    RPA platforms execute PyStreamMCP operations as part of
    robotic process automation workflows.

    Supports:
    - UiPath: Invoke HTTP Request activity
    - Automation Anywhere: HTTP Request command
    """

    def __init__(self, agent_id: str = "rpa_agent"):
        """Initialize RPA adapter.

        Args:
            agent_id: PyStreamMCP agent ID
        """
        self.agent_id = agent_id

    def execute_query_activity(self, query_text: str) -> Dict[str, Any]:
        """Execute query as RPA activity.

        UiPath Usage:
        ```
        HttpClient.Post(
            url="http://localhost:8000/rpa/query",
            body={"text": query_text},
            headers={"Content-Type": "application/json"}
        )
        ```

        Automation Anywhere Usage:
        ```
        WebService.Execute HTTP Request
            Method: POST
            URL: http://localhost:8000/rpa/query
            Body: {"text": query_text}
        ```
        """
        agent = Agent(agent_id=self.agent_id)
        result = agent.query(query_text)

        return {
            "query_id": result.query_id,
            "text": query_text,
            "baseline_tokens": result.baseline_tokens,
            "optimized_tokens": result.optimized_tokens,
            "cost_reduction_percent": result.cost_reduction_percent,
            "execution_time_ms": result.execution_time_ms,
            "success": True,
            "message": f"Query optimized: {result.cost_reduction_percent:.1f}% reduction",
        }

    def execute_batch_activity(self, queries: list) -> Dict[str, Any]:
        """Execute multiple queries in a batch RPA process.

        Args:
            queries: List of query strings

        Returns:
            Batch execution results
        """
        results = []
        total_baseline = 0
        total_optimized = 0

        for query in queries:
            agent = Agent(agent_id=self.agent_id)
            result = agent.query(query)

            results.append({
                "query": query,
                "query_id": result.query_id,
                "reduction": result.cost_reduction_percent,
            })

            total_baseline += result.baseline_tokens
            total_optimized += result.optimized_tokens

        avg_reduction = 100 * (1 - total_optimized / total_baseline) if total_baseline > 0 else 0

        return {
            "batch_size": len(queries),
            "queries": results,
            "total_baseline_tokens": total_baseline,
            "total_optimized_tokens": total_optimized,
            "average_reduction_percent": avg_reduction,
            "total_cost_saved": (total_baseline - total_optimized) * 0.00001,
            "success": True,
        }

    def get_uipath_activity_spec(self) -> Dict[str, Any]:
        """Get UiPath activity specification."""
        return {
            "name": "PyStreamMCP Query",
            "category": "Data Extraction",
            "inputs": {
                "query_text": {"type": "string", "required": True},
                "agent_id": {"type": "string", "default": self.agent_id},
            },
            "outputs": {
                "query_id": {"type": "string"},
                "cost_reduction": {"type": "number"},
                "success": {"type": "boolean"},
            },
        }

    def get_automation_anywhere_spec(self) -> Dict[str, Any]:
        """Get Automation Anywhere command specification."""
        return {
            "name": "PyStreamMCP Query",
            "type": "HTTP",
            "endpoint": "http://localhost:8000/rpa/query",
            "method": "POST",
            "inputs": {
                "query_text": "string",
                "agent_id": "string",
            },
            "outputs": {
                "query_id": "string",
                "cost_reduction_percent": "number",
                "success": "boolean",
            },
        }
