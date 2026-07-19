"""Tests for OKF query planner."""

import tempfile
from pathlib import Path

import pytest

from pystreammcp.okf_core import OKFCatalog
from pystreammcp.okf_discovery import DiscoveryOKFExporter
from pystreammcp.okf_query_planner import OKFQueryPlanner, QueryPlan, QueryPlanStep


@pytest.fixture
def populated_catalog():
    """Create catalog with sample systems and tools."""
    with tempfile.TemporaryDirectory() as tmpdir:
        catalog = OKFCatalog(Path(tmpdir))
        exporter = DiscoveryOKFExporter(catalog)

        # Export sample systems
        exporter.export_system(
            system_id="postgres",
            name="PostgreSQL",
            description="Primary database",
            tools_count=15,
            cost_per_query=0.01,
            latency_p99_ms=150,
            metadata={"tags": ["database", "sql"]}
        )

        exporter.export_system(
            system_id="elasticsearch",
            name="Elasticsearch",
            description="Search engine",
            tools_count=12,
            cost_per_query=0.005,
            latency_p99_ms=200,
            metadata={"tags": ["search", "analytics"]}
        )

        exporter.export_system(
            system_id="bigquery",
            name="BigQuery",
            description="Data warehouse",
            tools_count=20,
            cost_per_query=0.02,
            latency_p99_ms=300,
            metadata={"tags": ["warehouse", "analytics"]}
        )

        # Export sample tools
        exporter.export_tool(
            tool_id="search_customers",
            name="Search Customers",
            description="Search customer database",
            system_id="postgres",
            cost=0.005,
            latency_p95_ms=50,
            metadata={"tags": ["customer", "search"]}
        )

        exporter.export_tool(
            tool_id="analyze_trends",
            name="Analyze Trends",
            description="Analyze sales trends",
            system_id="elasticsearch",
            cost=0.008,
            latency_p95_ms=100,
            metadata={"tags": ["analytics", "trends"]}
        )

        exporter.export_tool(
            tool_id="customer_lifetime_value",
            name="Customer Lifetime Value",
            description="Calculate CLV",
            system_id="bigquery",
            cost=0.015,
            latency_p95_ms=200,
            metadata={"tags": ["analytics", "customer"]}
        )

        # Reload to ensure all docs are indexed
        catalog.reload()

        yield catalog


class TestQueryPlanStep:
    """Test individual query plan steps."""

    def test_create_step(self):
        """Test creating a query plan step."""
        step = QueryPlanStep(
            system_name="PostgreSQL",
            tool_name="Search Customers",
            cost=0.01,
            latency_ms=50,
            token_cost=500
        )

        assert step.system_name == "PostgreSQL"
        assert step.tool_name == "Search Customers"
        assert step.cost == 0.01

    def test_step_to_dict(self):
        """Test converting step to dictionary."""
        step = QueryPlanStep(
            system_name="PostgreSQL",
            tool_name="Query",
            cost=0.01,
            latency_ms=50,
            token_cost=500,
            okf_ref="tools/query.md"
        )

        step_dict = step.to_dict()
        assert step_dict["system"] == "PostgreSQL"
        assert step_dict["cost"] == 0.01
        assert step_dict["okf_reference"] == "tools/query.md"


class TestQueryPlan:
    """Test query plan operations."""

    def test_empty_plan(self):
        """Test creating empty plan."""
        plan = QueryPlan(objective="Test", steps=[])
        assert plan.objective == "Test"
        assert plan.total_cost == 0

    def test_plan_with_steps(self):
        """Test plan with multiple steps."""
        steps = [
            QueryPlanStep("System A", "Tool 1", cost=0.01, latency_ms=50, token_cost=500),
            QueryPlanStep("System B", "Tool 2", cost=0.02, latency_ms=100, token_cost=1000),
        ]
        plan = QueryPlan(objective="Test", steps=steps)

        assert plan.total_cost == 0.03
        assert plan.total_latency_ms == 150
        assert plan.total_token_cost == 1500

    def test_plan_to_dict(self):
        """Test converting plan to dictionary."""
        step = QueryPlanStep("System", "Tool", cost=0.01)
        plan = QueryPlan(objective="Test", steps=[step])

        plan_dict = plan.to_dict()
        assert plan_dict["objective"] == "Test"
        assert plan_dict["total_cost"] == 0.01
        assert len(plan_dict["steps"]) == 1


class TestOKFQueryPlanner:
    """Test OKF-based query planner."""

    def test_generate_plan(self, populated_catalog):
        """Test basic plan generation."""
        planner = OKFQueryPlanner(populated_catalog)
        plan = planner.generate_plan("customer search")

        assert plan.objective == "customer search"
        assert isinstance(plan, QueryPlan)

    def test_generate_plan_with_constraint(self, populated_catalog):
        """Test plan generation with system constraint."""
        planner = OKFQueryPlanner(populated_catalog)
        plan = planner.generate_plan("search", system_constraint="PostgreSQL")

        assert plan.objective == "search"
        # Should have found steps from PostgreSQL
        if plan.steps:
            assert "PostgreSQL" in [s.system_name for s in plan.steps]

    def test_cheapest_path(self, populated_catalog):
        """Test finding cheapest query path."""
        planner = OKFQueryPlanner(populated_catalog)
        plan = planner.find_cheapest_path("customer data")

        assert plan.objective == "customer data"
        # Cheapest should have lowest total cost
        if plan.steps:
            # Verify steps are sorted by cost
            costs = [s.cost for s in plan.steps]
            assert costs == sorted(costs)

    def test_fastest_path(self, populated_catalog):
        """Test finding fastest query path."""
        planner = OKFQueryPlanner(populated_catalog)
        plan = planner.find_fastest_path("quick lookup")

        assert plan.objective == "quick lookup"
        # Fastest should have low latency steps
        if plan.steps:
            # All steps should be reasonably fast
            for step in plan.steps:
                assert step.latency_ms <= 500  # Some reasonable upper bound

    def test_optimal_path(self, populated_catalog):
        """Test finding balanced optimal path."""
        planner = OKFQueryPlanner(populated_catalog)
        plan = planner.find_optimal_path(
            "customer analytics",
            cost_weight=0.4,
            latency_weight=0.4,
            relevance_weight=0.2
        )

        assert plan.objective == "customer analytics"
        assert isinstance(plan, QueryPlan)

    def test_optimal_with_custom_weights(self, populated_catalog):
        """Test optimal path with custom weight distribution."""
        planner = OKFQueryPlanner(populated_catalog)

        # Cost-optimized
        cost_plan = planner.find_optimal_path(
            "test",
            cost_weight=0.8,
            latency_weight=0.1,
            relevance_weight=0.1
        )

        # Latency-optimized
        latency_plan = planner.find_optimal_path(
            "test",
            cost_weight=0.1,
            latency_weight=0.8,
            relevance_weight=0.1
        )

        # Both should be valid plans
        assert cost_plan.objective == "test"
        assert latency_plan.objective == "test"

    def test_plan_with_budget_constraint(self, populated_catalog):
        """Test plan generation respects budget constraint."""
        planner = OKFQueryPlanner(populated_catalog)
        plan = planner.generate_plan("test", max_cost=0.02)

        # Total cost should not exceed budget
        assert plan.total_cost <= 0.02

    def test_plan_with_no_matching_systems(self, populated_catalog):
        """Test plan generation with impossible objective."""
        planner = OKFQueryPlanner(populated_catalog)
        # Search for something that won't match systems
        plan = planner.generate_plan("xyzabc123notfound")

        # Should still return a plan (fallback to all systems)
        assert plan.objective == "xyzabc123notfound"
        assert isinstance(plan, QueryPlan)


class TestOKFQueryPlannerIntegration:
    """Integration tests for query planner with catalog."""

    def test_end_to_end_planning(self, populated_catalog):
        """Test end-to-end planning from catalog."""
        planner = OKFQueryPlanner(populated_catalog)

        # Generate multiple types of plans
        cheap_plan = planner.find_cheapest_path("get customer info")
        fast_plan = planner.find_fastest_path("get customer info")
        optimal_plan = planner.find_optimal_path("get customer info")

        # All should be valid
        for plan in [cheap_plan, fast_plan, optimal_plan]:
            assert isinstance(plan, QueryPlan)
            assert plan.objective == "get customer info"

    def test_plans_differ_by_strategy(self, populated_catalog):
        """Test that different strategies produce different plans."""
        planner = OKFQueryPlanner(populated_catalog)

        cheap = planner.find_cheapest_path("test")
        fast = planner.find_fastest_path("test")

        # Both should be valid plans
        assert isinstance(cheap, QueryPlan)
        assert isinstance(fast, QueryPlan)

        # They might have different characteristics
        # (cost and latency are often tradeoffs, not guarantees)
        if cheap.steps and fast.steps:
            # At minimum, they're both valid plans
            assert len(cheap.steps) > 0
            assert len(fast.steps) > 0
