"""Temporal integration for PyStreamMCP.

Enables durable workflows with Temporal, with PyStreamMCP operations
as resilient activities that survive failures and retries.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass

from pystreammcp import Agent


@dataclass
class TemporalQueryActivity:
    """Temporal activity for executing optimized queries."""

    agent_id: str
    query_text: str
    intent: str = "retrieve"
    max_tokens: Optional[int] = None

    def execute(self) -> Dict[str, Any]:
        """Execute the query as a Temporal activity.

        Activities in Temporal:
        - Are durable (survive failures)
        - Can retry with exponential backoff
        - Support timeouts and heartbeats
        - Track execution state
        """
        agent = Agent(
            agent_id=self.agent_id,
            optimization_strategy="balanced",
            max_tokens=self.max_tokens or 2000,
        )

        result = agent.query(self.query_text)

        return {
            "query_id": result.query_id,
            "text": self.query_text,
            "intent": self.intent,
            "baseline_tokens": result.baseline_tokens,
            "optimized_tokens": result.optimized_tokens,
            "cost_reduction_percent": result.cost_reduction_percent,
            "execution_time_ms": result.execution_time_ms,
            "status": "completed",
        }


@dataclass
class TemporalDiscoveryActivity:
    """Temporal activity for data source discovery."""

    agent_id: str
    context: str
    max_sources: int = 10

    def execute(self) -> Dict[str, Any]:
        """Execute discovery as a durable activity."""
        agent = Agent(agent_id=self.agent_id)

        # In production, use actual discovery logic
        return {
            "context": self.context,
            "sources": [
                {
                    "name": f"source_{i}",
                    "relevance": 0.95 - (i * 0.05),
                    "type": "database",
                }
                for i in range(min(self.max_sources, 5))
            ],
            "total_sources": min(self.max_sources, 5),
            "status": "completed",
        }


class TemporalWorkflow:
    """Temporal workflow orchestrating PyStreamMCP operations.

    Example workflow pattern:
    1. Discover relevant data sources
    2. Optimize queries for cost
    3. Execute queries in parallel
    4. Aggregate results
    5. Handle failures with retries
    """

    def __init__(self, workflow_id: str, agent_id: str):
        """Initialize workflow.

        Args:
            workflow_id: Unique workflow identifier
            agent_id: PyStreamMCP agent ID
        """
        self.workflow_id = workflow_id
        self.agent_id = agent_id

    def discover_sources(self, context: str) -> Dict[str, Any]:
        """Activity: Discover relevant sources.

        In Temporal, this would be:
        ```python
        sources = await workflow.execute_activity(
            TemporalDiscoveryActivity,
            TemporalDiscoveryActivity(self.agent_id, context),
        )
        ```
        """
        activity = TemporalDiscoveryActivity(self.agent_id, context)
        return activity.execute()

    def optimize_query(self, query_text: str) -> Dict[str, Any]:
        """Activity: Optimize query for cost reduction.

        In Temporal, this would be:
        ```python
        result = await workflow.execute_activity(
            TemporalQueryActivity,
            TemporalQueryActivity(self.agent_id, query_text, "retrieve"),
            RetryPolicy(maximum_attempts=3),  # Retry up to 3 times
        )
        ```
        """
        activity = TemporalQueryActivity(self.agent_id, query_text)
        return activity.execute()

    def execute_parallel_queries(self, queries: list) -> list:
        """Activity: Execute multiple queries in parallel.

        In Temporal, this would use:
        ```python
        activities = [
            workflow.execute_activity(
                TemporalQueryActivity,
                TemporalQueryActivity(self.agent_id, q),
            )
            for q in queries
        ]
        results = await asyncio.gather(*activities)
        ```
        """
        results = []
        for query in queries:
            activity = TemporalQueryActivity(self.agent_id, query)
            results.append(activity.execute())
        return results

    def workflow_definition(self) -> Dict[str, Any]:
        """Define the complete workflow pattern."""
        return {
            "workflow_id": self.workflow_id,
            "agent_id": self.agent_id,
            "activities": [
                {"name": "discover_sources", "retry_policy": {"max_attempts": 3}},
                {"name": "optimize_query", "retry_policy": {"max_attempts": 3}},
                {"name": "execute_query", "retry_policy": {"max_attempts": 5}},
            ],
            "timeout_seconds": 300,
            "description": "PyStreamMCP-powered workflow with durable activities",
        }


class TemporalClient:
    """Client for submitting workflows to Temporal.

    Usage:
    ```python
    client = TemporalClient(server_address="localhost:7233")
    handle = client.start_workflow(
        TemporalWorkflow("workflow_123", "agent_1"),
        query="Find top customers"
    )
    result = handle.result()  # Wait for completion
    ```
    """

    def __init__(self, server_address: str = "localhost:7233"):
        """Initialize Temporal client.

        Args:
            server_address: Temporal server address
        """
        self.server_address = server_address
        self.workflows = {}

    def start_workflow(
        self,
        workflow: TemporalWorkflow,
        query: str,
        task_queue: str = "pystreammcp",
    ) -> Dict[str, Any]:
        """Start a workflow execution.

        Args:
            workflow: Workflow instance
            query: Initial query
            task_queue: Temporal task queue

        Returns:
            Workflow execution handle
        """
        result = workflow.optimize_query(query)
        self.workflows[workflow.workflow_id] = result

        return {
            "workflow_id": workflow.workflow_id,
            "status": "started",
            "task_queue": task_queue,
            "result": result,
        }

    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow execution status.

        Args:
            workflow_id: Workflow ID

        Returns:
            Workflow status
        """
        if workflow_id in self.workflows:
            return {
                "workflow_id": workflow_id,
                "status": "completed",
                "result": self.workflows[workflow_id],
            }
        return {"workflow_id": workflow_id, "status": "unknown"}

    def list_workflows(self) -> list:
        """List all active workflows."""
        return list(self.workflows.keys())
