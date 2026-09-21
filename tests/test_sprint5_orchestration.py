"""Sprint 5 integration tests - Workflow Orchestration Tools.

Tests for Temporal, Airflow, n8n, Power Automate, UiPath, Automation Anywhere.
"""

import pytest
from pystreammcp.orchestration.temporal import (
    TemporalQueryActivity, TemporalDiscoveryActivity,
    TemporalWorkflow, TemporalClient,
)
from pystreammcp.orchestration.airflow import (
    PyStreamMCPQueryOperator, PyStreamMCPDiscoveryOperator,
    PyStreamMCPOptimizeOperator, PyStreamMCPDAGFactory,
)
from pystreammcp.orchestration.nocode_rpa import (
    N8nWebhookTrigger, PowerAutomateConnector, RoboticProcessAdapter,
)
from pystreammcp.discovery import SourceRegistry


class TestTemporalIntegration:
    """Test Temporal workflow integration."""

    def test_temporal_query_activity(self):
        """Test query activity execution."""
        activity = TemporalQueryActivity(
            agent_id="temporal_test",
            query_text="Test query",
            intent="retrieve",
        )
        result = activity.execute()

        assert result["status"] == "completed"
        assert result["query_id"] is not None
        assert result["cost_reduction_percent"] > 0
        assert result["baseline_tokens"] > result["optimized_tokens"]

    def test_temporal_discovery_activity_returns_nothing_without_registration(self):
        """An untouched registry must not fabricate source_0..source_4."""
        activity = TemporalDiscoveryActivity(
            agent_id="temporal_test",
            context="test context",
        )
        result = activity.execute()

        assert result["status"] == "completed"
        assert result["sources"] == []
        assert result["total_sources"] == 0

    def test_temporal_discovery_activity_finds_real_registered_source(self):
        """Discovery must return the actual registered source, not a fake one."""
        registry = SourceRegistry()
        registry.register("orders_db", "customer revenue and order data")

        activity = TemporalDiscoveryActivity(
            agent_id="temporal_test",
            context="customer revenue",
            registry=registry,
        )
        result = activity.execute()

        assert result["status"] == "completed"
        assert result["total_sources"] == 1
        assert result["sources"][0]["name"] == "orders_db"
        assert 0.0 < result["sources"][0]["relevance"] <= 1.0
        assert not any(s["name"].startswith("source_") for s in result["sources"])

    def test_temporal_workflow_definition(self):
        """Test workflow definition."""
        workflow = TemporalWorkflow("workflow_1", "agent_1")
        definition = workflow.workflow_definition()

        assert definition["workflow_id"] == "workflow_1"
        assert len(definition["activities"]) == 3
        assert definition["timeout_seconds"] == 300

    def test_temporal_workflow_execution(self):
        """Test workflow execution."""
        workflow = TemporalWorkflow("test_workflow", "test_agent")
        result = workflow.optimize_query("Test query")

        assert result["query_id"] is not None
        assert result["execution_time_ms"] > 0

    def test_temporal_client(self):
        """Test Temporal client."""
        client = TemporalClient()
        workflow = TemporalWorkflow("client_test", "agent_1")

        result = client.start_workflow(workflow, "Test query")

        assert result["status"] == "started"
        assert result["result"]["query_id"] is not None

    def test_temporal_workflow_status(self):
        """Test getting workflow status."""
        client = TemporalClient()
        workflow = TemporalWorkflow("status_test", "agent_1")

        client.start_workflow(workflow, "Test query")
        status = client.get_workflow_status("status_test")

        assert status["status"] == "completed"


class TestAirflowIntegration:
    """Test Apache Airflow integration."""

    def test_query_operator(self):
        """Test query operator."""
        operator = PyStreamMCPQueryOperator(
            task_id="query_task",
            agent_id="airflow_agent",
            query_text="Test query",
        )

        context = {"execution_date": "2024-01-01"}
        result = operator.execute(context)

        assert result["task_id"] == "query_task"
        assert result["baseline_tokens"] > 0
        assert result["cost_reduction_percent"] > 0

    def test_discovery_operator_returns_nothing_without_registration(self):
        """An untouched registry must not fabricate source_0..source_4."""
        operator = PyStreamMCPDiscoveryOperator(
            task_id="discover_task",
            agent_id="airflow_agent",
            context_text="test context",
        )

        context = {"execution_date": "2024-01-01"}
        result = operator.execute(context)

        assert result["task_id"] == "discover_task"
        assert result["sources"] == []
        assert result["total_sources"] == 0

    def test_discovery_operator_finds_real_registered_source(self):
        """Discovery must return the actual registered source, not a fake one."""
        registry = SourceRegistry()
        registry.register("orders_db", "customer revenue and order data")

        operator = PyStreamMCPDiscoveryOperator(
            task_id="discover_task",
            agent_id="airflow_agent",
            context_text="customer revenue",
            registry=registry,
        )

        context = {"execution_date": "2024-01-01"}
        result = operator.execute(context)

        assert result["task_id"] == "discover_task"
        assert result["total_sources"] == 1
        assert result["sources"][0]["name"] == "orders_db"
        assert not any(s["name"].startswith("source_") for s in result["sources"])

    def test_optimize_operator(self):
        """Test optimization operator."""
        operator = PyStreamMCPOptimizeOperator(
            task_id="optimize_task",
            agent_id="airflow_agent",
            query_text="Test query",
        )

        context = {"execution_date": "2024-01-01"}
        result = operator.execute(context)

        assert result["task_id"] == "optimize_task"
        assert result["cost_reduction_percent"] > 0

    def test_dag_factory_query_dag(self):
        """Test DAG factory for query DAG."""
        factory = PyStreamMCPDAGFactory()
        dag = factory.create_query_dag(
            dag_id="test_dag",
            agent_id="airflow_agent",
            queries=["Query 1", "Query 2", "Query 3"],
        )

        assert dag["dag_id"] == "test_dag"
        assert len(dag["tasks"]) == 4  # 3 queries + 1 aggregate
        assert dag["tasks"][-1]["task_id"] == "aggregate_results"

    def test_dag_factory_discovery_dag(self):
        """Test DAG factory for discovery DAG."""
        factory = PyStreamMCPDAGFactory()
        dag = factory.create_discovery_dag(
            dag_id="discovery_dag",
            agent_id="airflow_agent",
            contexts=["context_1", "context_2"],
        )

        assert dag["dag_id"] == "discovery_dag"
        assert len(dag["tasks"]) == 2

    def test_dag_factory_pipeline_dag(self):
        """Test complete pipeline DAG."""
        factory = PyStreamMCPDAGFactory()
        dag = factory.create_pipeline_dag(
            dag_id="pipeline_dag",
            agent_id="airflow_agent",
        )

        assert dag["dag_id"] == "pipeline_dag"
        assert len(dag["tasks"]) == 4  # discover → optimize → execute → aggregate
        assert dag["tasks"][0]["task_id"] == "discover_sources"
        assert dag["tasks"][-1]["task_id"] == "aggregate_results"


class TestN8nIntegration:
    """Test n8n webhook integration."""

    def test_n8n_webhook_query(self):
        """Test n8n query webhook."""
        trigger = N8nWebhookTrigger(agent_id="n8n_agent")
        result = trigger.handle_query({"text": "Test query"})

        assert result["success"] is True
        assert result["query_id"] is not None
        assert result["cost_reduction"] > 0

    def test_n8n_webhook_discovery_returns_nothing_without_registration(self):
        """An untouched registry must not fabricate source_0..source_4."""
        trigger = N8nWebhookTrigger()
        result = trigger.handle_discovery({"context": "test"})

        assert result["success"] is True
        assert result["sources"] == []
        assert result["total_sources"] == 0

    def test_n8n_webhook_discovery_finds_real_registered_source(self):
        """Discovery must return the actual registered source, not a fake one."""
        registry = SourceRegistry()
        registry.register("orders_db", "customer revenue and order data")
        trigger = N8nWebhookTrigger(registry=registry)

        result = trigger.handle_discovery({"context": "customer revenue"})

        assert result["success"] is True
        assert result["total_sources"] == 1
        assert result["sources"][0]["name"] == "orders_db"
        assert not any(s["name"].startswith("source_") for s in result["sources"])

    def test_n8n_webhook_missing_params(self):
        """Test n8n webhook error handling."""
        trigger = N8nWebhookTrigger()
        result = trigger.handle_query({})

        assert "error" in result

    def test_n8n_webhook_spec(self):
        """Test n8n webhook specification."""
        trigger = N8nWebhookTrigger()
        spec = trigger.get_webhook_spec()

        assert spec["name"] == "PyStreamMCP"
        assert len(spec["endpoints"]) == 2
        assert any(e["name"] == "query" for e in spec["endpoints"])


class TestPowerAutomateIntegration:
    """Test Power Automate integration."""

    def test_power_automate_query(self):
        """Test Power Automate query execution."""
        connector = PowerAutomateConnector()
        result = connector.query("Test query", "agent_1")

        assert result["status"] == "success"
        assert result["queryId"] is not None
        assert result["costReduction"] > 0

    def test_power_automate_connector_spec(self):
        """Test Power Automate connector specification."""
        connector = PowerAutomateConnector()
        spec = connector.get_custom_connector_spec()

        assert spec["info"]["title"] == "PyStreamMCP"
        assert "/query" in spec["paths"]


class TestRPAIntegration:
    """Test RPA platform integration."""

    def test_uipath_query_activity(self):
        """Test UiPath query activity."""
        adapter = RoboticProcessAdapter(agent_id="uipath_agent")
        result = adapter.execute_query_activity("Test query")

        assert result["success"] is True
        assert result["query_id"] is not None
        assert result["cost_reduction_percent"] > 0

    def test_automation_anywhere_batch(self):
        """Test Automation Anywhere batch processing."""
        adapter = RoboticProcessAdapter()
        result = adapter.execute_batch_activity(["Query 1", "Query 2"])

        assert result["success"] is True
        assert result["batch_size"] == 2
        assert result["average_reduction_percent"] > 0
        assert result["total_cost_saved"] > 0

    def test_uipath_activity_spec(self):
        """Test UiPath activity specification."""
        adapter = RoboticProcessAdapter()
        spec = adapter.get_uipath_activity_spec()

        assert spec["name"] == "PyStreamMCP Query"
        assert "query_text" in spec["inputs"]
        assert "cost_reduction" in spec["outputs"]

    def test_automation_anywhere_spec(self):
        """Test Automation Anywhere specification."""
        adapter = RoboticProcessAdapter()
        spec = adapter.get_automation_anywhere_spec()

        assert spec["name"] == "PyStreamMCP Query"
        assert spec["method"] == "POST"


class TestOrchestrationWorkflows:
    """Test end-to-end orchestration workflows."""

    def test_temporal_multi_step_workflow(self):
        """Test multi-step Temporal workflow."""
        registry = SourceRegistry()
        registry.register("data_lake", "raw data context for analytics")
        workflow = TemporalWorkflow("multistep", "agent_1", registry=registry)

        # Step 1: Discover -- must find the real registered source, not
        # a fabricated one.
        sources = workflow.discover_sources("data context")
        assert sources["total_sources"] == 1
        assert sources["sources"][0]["name"] == "data_lake"

        # Step 2: Optimize
        optimized = workflow.optimize_query("Complex query")
        assert optimized["cost_reduction_percent"] > 0

        # Step 3: Execute parallel
        results = workflow.execute_parallel_queries(["Q1", "Q2"])
        assert len(results) == 2

    def test_airflow_pipeline_execution(self):
        """Test Airflow pipeline execution."""
        factory = PyStreamMCPDAGFactory()
        dag = factory.create_pipeline_dag("test_pipeline", "agent_1")

        # Simulate task execution
        context = {"execution_date": "2024-01-01"}

        # Discovery phase -- must find the real registered source, not a
        # fabricated one.
        registry = SourceRegistry()
        registry.register("test_source", "test data for the pipeline")
        discover_op = PyStreamMCPDiscoveryOperator(
            "discover", "agent_1", "test", registry=registry
        )
        discover_result = discover_op.execute(context)
        assert discover_result["total_sources"] == 1
        assert discover_result["sources"][0]["name"] == "test_source"

        # Optimization phase
        optimize_op = PyStreamMCPOptimizeOperator(
            "optimize", "agent_1", "Test query"
        )
        optimize_result = optimize_op.execute(context)
        assert optimize_result["cost_reduction_percent"] > 0

        # Execution phase
        query_op = PyStreamMCPQueryOperator(
            "execute", "agent_1", "Test query"
        )
        query_result = query_op.execute(context)
        assert query_result["baseline_tokens"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
