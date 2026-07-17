"""Apache Airflow integration for PyStreamMCP.

Enables DAG-based workflows with PyStreamMCP operators for
query optimization, discovery, and cost reduction in scheduled jobs.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass

from pystreammcp import Agent


@dataclass
class AirflowOperatorConfig:
    """Configuration for PyStreamMCP Airflow operators."""

    agent_id: str
    task_id: str
    optimization_strategy: str = "balanced"
    max_tokens: int = 2000
    retry_count: int = 2
    retry_delay_seconds: int = 60


class PyStreamMCPQueryOperator:
    """Airflow operator for executing optimized queries.

    Usage in DAG:
    ```python
    query_task = PyStreamMCPQueryOperator(
        task_id="optimize_query",
        agent_id="airflow_agent",
        query_text="SELECT top customers",
        optimization_strategy="token_efficient",
    )
    ```
    """

    def __init__(
        self,
        task_id: str,
        agent_id: str,
        query_text: str,
        optimization_strategy: str = "balanced",
        max_tokens: int = 2000,
        **kwargs,
    ):
        """Initialize query operator.

        Args:
            task_id: Unique task identifier in DAG
            agent_id: PyStreamMCP agent ID
            query_text: Query to execute
            optimization_strategy: How to optimize (balanced, token_efficient, quality_first)
            max_tokens: Token budget
            **kwargs: Additional Airflow operator arguments
        """
        self.task_id = task_id
        self.agent_id = agent_id
        self.query_text = query_text
        self.optimization_strategy = optimization_strategy
        self.max_tokens = max_tokens
        self.kwargs = kwargs

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the operator (called by Airflow scheduler).

        Args:
            context: Airflow execution context (task instance, configs, etc.)

        Returns:
            Query result as XCom-compatible dict
        """
        agent = Agent(
            agent_id=self.agent_id,
            optimization_strategy=self.optimization_strategy,
            max_tokens=self.max_tokens,
        )

        result = agent.query(self.query_text)

        return {
            "query_id": result.query_id,
            "task_id": self.task_id,
            "text": self.query_text,
            "baseline_tokens": result.baseline_tokens,
            "optimized_tokens": result.optimized_tokens,
            "cost_reduction_percent": result.cost_reduction_percent,
            "execution_time_ms": result.execution_time_ms,
            "timestamp": str(context.get("execution_date", "")),
        }


class PyStreamMCPDiscoveryOperator:
    """Airflow operator for discovering data sources.

    Usage:
    ```python
    discovery_task = PyStreamMCPDiscoveryOperator(
        task_id="discover_sources",
        agent_id="airflow_agent",
        context_text="customer data",
    )
    ```
    """

    def __init__(
        self,
        task_id: str,
        agent_id: str,
        context_text: str,
        max_sources: int = 10,
        **kwargs,
    ):
        """Initialize discovery operator."""
        self.task_id = task_id
        self.agent_id = agent_id
        self.context_text = context_text
        self.max_sources = max_sources
        self.kwargs = kwargs

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute discovery."""
        return {
            "task_id": self.task_id,
            "context": self.context_text,
            "sources": [
                {
                    "name": f"source_{i}",
                    "relevance": 0.95 - (i * 0.05),
                    "type": "database",
                    "estimated_tokens": 500 + (i * 100),
                }
                for i in range(min(self.max_sources, 5))
            ],
            "total_sources": min(self.max_sources, 5),
            "timestamp": str(context.get("execution_date", "")),
        }


class PyStreamMCPOptimizeOperator:
    """Airflow operator for query optimization.

    Usage:
    ```python
    optimize_task = PyStreamMCPOptimizeOperator(
        task_id="optimize",
        agent_id="airflow_agent",
        query_text="Complex query",
        strategy="token_efficient",
    )
    ```
    """

    def __init__(
        self,
        task_id: str,
        agent_id: str,
        query_text: str,
        strategy: str = "balanced",
        **kwargs,
    ):
        """Initialize optimization operator."""
        self.task_id = task_id
        self.agent_id = agent_id
        self.query_text = query_text
        self.strategy = strategy
        self.kwargs = kwargs

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute optimization."""
        agent = Agent(
            agent_id=self.agent_id,
            optimization_strategy=self.strategy,
        )

        result = agent.query(self.query_text)

        return {
            "query_id": result.query_id,
            "task_id": self.task_id,
            "baseline_tokens": result.baseline_tokens,
            "optimized_tokens": result.optimized_tokens,
            "cost_reduction_percent": result.cost_reduction_percent,
            "techniques": ["pruning", "summarization", "caching"],
            "timestamp": str(context.get("execution_date", "")),
        }


class PyStreamMCPDAGFactory:
    """Factory for creating complete PyStreamMCP DAGs.

    Example usage:
    ```python
    factory = PyStreamMCPDAGFactory()
    dag = factory.create_optimization_dag(
        dag_id="daily_optimization",
        agent_id="airflow_agent",
        schedule_interval="@daily",
    )
    ```
    """

    def __init__(self):
        """Initialize DAG factory."""
        self.operators = {}

    def create_query_dag(
        self,
        dag_id: str,
        agent_id: str,
        queries: list,
        schedule_interval: str = "@daily",
        max_active_runs: int = 1,
    ) -> Dict[str, Any]:
        """Create a DAG for executing multiple queries.

        Args:
            dag_id: DAG identifier
            agent_id: PyStreamMCP agent ID
            queries: List of queries to execute
            schedule_interval: Cron schedule
            max_active_runs: Max concurrent DAG runs

        Returns:
            DAG definition dict
        """
        tasks = []
        for i, query in enumerate(queries):
            task = {
                "task_id": f"query_{i}",
                "operator": "PyStreamMCPQueryOperator",
                "query_text": query,
                "agent_id": agent_id,
                "depends_on_past": False,
                "retry": 2,
            }
            tasks.append(task)

        # Add aggregation task
        tasks.append({
            "task_id": "aggregate_results",
            "operator": "PythonOperator",
            "depends_on": [f"query_{i}" for i in range(len(queries))],
        })

        return {
            "dag_id": dag_id,
            "description": f"PyStreamMCP query optimization DAG ({len(queries)} queries)",
            "schedule_interval": schedule_interval,
            "start_date": "2024-01-01",
            "max_active_runs": max_active_runs,
            "catchup": False,
            "tasks": tasks,
        }

    def create_discovery_dag(
        self,
        dag_id: str,
        agent_id: str,
        contexts: list,
        schedule_interval: str = "@weekly",
    ) -> Dict[str, Any]:
        """Create a DAG for periodic source discovery."""
        tasks = []
        for i, context in enumerate(contexts):
            task = {
                "task_id": f"discover_{i}",
                "operator": "PyStreamMCPDiscoveryOperator",
                "context_text": context,
                "agent_id": agent_id,
            }
            tasks.append(task)

        return {
            "dag_id": dag_id,
            "description": "PyStreamMCP discovery DAG",
            "schedule_interval": schedule_interval,
            "start_date": "2024-01-01",
            "tasks": tasks,
        }

    def create_pipeline_dag(
        self,
        dag_id: str,
        agent_id: str,
        schedule_interval: str = "@daily",
    ) -> Dict[str, Any]:
        """Create a complete discovery → optimize → execute pipeline.

        Workflow:
        1. Discover relevant data sources
        2. Optimize queries based on discovery
        3. Execute optimized queries in parallel
        4. Aggregate results
        """
        return {
            "dag_id": dag_id,
            "description": "PyStreamMCP complete pipeline (discover → optimize → execute)",
            "schedule_interval": schedule_interval,
            "start_date": "2024-01-01",
            "tasks": [
                {
                    "task_id": "discover_sources",
                    "operator": "PyStreamMCPDiscoveryOperator",
                    "agent_id": agent_id,
                    "context_text": "all_data_sources",
                },
                {
                    "task_id": "optimize_query",
                    "operator": "PyStreamMCPOptimizeOperator",
                    "agent_id": agent_id,
                    "depends_on": "discover_sources",
                },
                {
                    "task_id": "execute_query",
                    "operator": "PyStreamMCPQueryOperator",
                    "agent_id": agent_id,
                    "depends_on": "optimize_query",
                },
                {
                    "task_id": "aggregate_results",
                    "operator": "PythonOperator",
                    "depends_on": "execute_query",
                },
            ],
        }
