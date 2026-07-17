"""Tests for Phase 3 items 3-5: LangSmith, Decomposition, QA Framework."""

import pytest
from pystreammcp.integrations.langsmith import (
    LangSmithTracer, LangSmithSpan, CostAnalytics, SpanType,
)
from pystreammcp.optimization.decomposition import (
    QueryDecomposer, DecompositionPlan, QueryType, SubQuery,
)
from pystreammcp.qa.validator import (
    QualityValidator, ValidationRule, SLAChecker, AuditLogger, ValidationStatus,
)


class TestLangSmithIntegration:
    """Test LangSmith integration."""

    def test_tracer_initialization(self):
        """Test tracer creation."""
        tracer = LangSmithTracer(project_name="test_project")
        assert tracer.project_name == "test_project"

    def test_start_trace(self):
        """Test starting a trace."""
        tracer = LangSmithTracer()
        trace_id = tracer.start_trace("test_trace")
        assert trace_id is not None

    def test_start_end_span(self):
        """Test span lifecycle."""
        tracer = LangSmithTracer()

        span_id = tracer.start_span(
            "test_span",
            SpanType.QUERY,
            {"input": "test"},
        )

        tracer.end_span(
            span_id,
            {"output": "result"},
            status="success",
        )

        assert len(tracer.spans) == 1
        span = tracer.spans[0]
        assert span.status == "success"
        assert span.output_data["output"] == "result"

    def test_trace_query(self):
        """Test tracing a query."""
        tracer = LangSmithTracer()

        result = {
            "query_id": "q1",
            "baseline_tokens": 1000,
            "optimized_tokens": 400,
            "cost_reduction_percent": 60.0,
        }

        span_id = tracer.trace_query("SELECT * FROM users", result, "agent_1")
        assert span_id is not None

    def test_cost_analytics(self):
        """Test cost analytics."""
        tracer = LangSmithTracer()

        for i in range(3):
            tracer.trace_query(
                f"Query {i}",
                {
                    "query_id": f"q{i}",
                    "baseline_tokens": 1000 + i * 100,
                    "optimized_tokens": 400 + i * 50,
                    "cost_reduction_percent": 60.0 + i * 5,
                },
                "agent_1",
            )

        analytics = tracer.get_cost_analytics()
        assert analytics.total_operations == 3
        assert analytics.total_baseline_tokens > 0

    def test_export_to_langsmith(self):
        """Test exporting to LangSmith format."""
        tracer = LangSmithTracer()
        tracer.trace_query("test", {"baseline_tokens": 1000, "optimized_tokens": 400}, "agent_1")

        export = tracer.export_to_langsmith()
        assert "project" in export
        assert "traces" in export
        assert "analytics" in export

    def test_dashboard_data(self):
        """Test dashboard data generation."""
        tracer = LangSmithTracer()

        tracer.trace_query("q1", {"baseline_tokens": 1000, "optimized_tokens": 400}, "a1")
        tracer.trace_query("q2", {"baseline_tokens": 1200, "optimized_tokens": 500}, "a1")

        dashboard = tracer.get_dashboard_data()
        assert "overview" in dashboard
        assert "cost_breakdown" in dashboard
        assert "performance" in dashboard


class TestQueryDecomposition:
    """Test query decomposition."""

    def test_decomposer_initialization(self):
        """Test decomposer creation."""
        decomposer = QueryDecomposer()
        assert decomposer is not None

    def test_analyze_simple_query(self):
        """Test analyzing a simple query."""
        decomposer = QueryDecomposer()
        qtype = decomposer.analyze_query("SELECT * FROM users WHERE id = 1")
        assert qtype == QueryType.SIMPLE

    def test_analyze_joined_query(self):
        """Test analyzing a joined query."""
        decomposer = QueryDecomposer()
        qtype = decomposer.analyze_query("SELECT * FROM users JOIN orders ON users.id = orders.user_id")
        assert qtype == QueryType.JOINED

    def test_analyze_aggregated_query(self):
        """Test analyzing aggregated query."""
        decomposer = QueryDecomposer()
        qtype = decomposer.analyze_query("SELECT user_id, COUNT(*) FROM orders GROUP BY user_id")
        assert qtype == QueryType.AGGREGATED

    def test_decompose_simple(self):
        """Test decomposing simple query."""
        decomposer = QueryDecomposer()
        plan = decomposer.decompose("SELECT * FROM users")

        assert plan.query_type == QueryType.SIMPLE
        assert len(plan.sub_queries) == 1
        assert plan.estimated_reduction >= 60.0

    def test_decompose_joined(self):
        """Test decomposing joined query."""
        decomposer = QueryDecomposer()
        plan = decomposer.decompose("SELECT * FROM users JOIN orders ON users.id = orders.user_id")

        assert plan.query_type == QueryType.JOINED
        assert len(plan.sub_queries) == 3
        assert any(sq.parallelizable for sq in plan.sub_queries)

    def test_execution_order(self):
        """Test execution order generation."""
        decomposer = QueryDecomposer()
        plan = decomposer.decompose("SELECT * FROM users JOIN orders ON users.id = orders.user_id")

        order = decomposer.get_execution_order(plan)
        assert len(order) == len(plan.sub_queries)

        # Verify dependencies are respected
        executed = set()
        for sq_id in order:
            sq = next(sq for sq in plan.sub_queries if sq.id == sq_id)
            assert all(d in executed for d in sq.depends_on)
            executed.add(sq_id)

    def test_estimate_speedup(self):
        """Test speedup estimation."""
        decomposer = QueryDecomposer()
        plan = decomposer.decompose("SELECT * FROM users JOIN orders ON users.id = orders.user_id")

        speedup = decomposer.estimate_speedup(plan)
        assert speedup > 1.0
        assert speedup <= 3.5


class TestQAFramework:
    """Test QA framework."""

    def test_validator_initialization(self):
        """Test validator creation."""
        validator = QualityValidator()
        assert len(validator.rules) > 0

    def test_add_custom_rule(self):
        """Test adding custom rule."""
        validator = QualityValidator()
        rule = ValidationRule(
            name="custom_rule",
            description="Custom test rule",
            metric="custom_metric",
            operator=">=",
            threshold=50.0,
            severity="warning",
        )

        validator.add_rule(rule)
        assert "custom_rule" in validator.rules

    def test_validate_passing(self):
        """Test validation with passing results."""
        validator = QualityValidator()

        result = {
            "cost_reduction": 65.0,
            "latency_ms": 100.0,
            "model_accuracy": 85.0,
        }

        results = validator.validate(result)
        assert len(results) > 0
        assert any(r.status == ValidationStatus.PASS for r in results)

    def test_validate_failing(self):
        """Test validation with failing results."""
        validator = QualityValidator()

        result = {
            "cost_reduction": 50.0,  # Below 60% threshold
            "latency_ms": 100.0,
            "model_accuracy": 85.0,
        }

        results = validator.validate(result)
        assert any(r.status == ValidationStatus.FAIL for r in results)

    def test_validation_summary(self):
        """Test validation summary."""
        validator = QualityValidator()

        for i in range(5):
            result = {
                "cost_reduction": 60.0 + i * 5,
                "latency_ms": 100.0,
                "model_accuracy": 85.0,
            }
            validator.validate(result)

        summary = validator.get_validation_summary()
        assert summary["total"] > 0
        assert summary["pass_rate"] > 0

    def test_sla_checker(self):
        """Test SLA checking."""
        checker = SLAChecker()

        metrics = {
            "latency_ms": 80.0,
            "cost_reduction_percent": 65.0,
            "model_accuracy": 85.0,
        }

        report = checker.check_sla(metrics)
        assert report["compliant"] is True

    def test_sla_violation(self):
        """Test SLA violation detection."""
        checker = SLAChecker()

        metrics = {
            "latency_ms": 200.0,  # Exceeds 100ms threshold
            "cost_reduction_percent": 50.0,  # Below 60% threshold
            "model_accuracy": 85.0,
        }

        report = checker.check_sla(metrics)
        assert report["compliant"] is False
        assert len(report["violations"]) > 0

    def test_audit_logger(self):
        """Test audit logging."""
        logger = AuditLogger()

        entry_id = logger.log_operation(
            operation="query",
            agent_id="agent_1",
            input_data={"query": "test"},
            output_data={"result": "success"},
            cost_reduction=60.0,
            duration_ms=150.0,
            validation_status=ValidationStatus.PASS,
            user_id="user_1",
        )

        assert entry_id is not None
        assert len(logger.audit_log) == 1

    def test_audit_trail_filtering(self):
        """Test audit trail filtering."""
        logger = AuditLogger()

        for i in range(3):
            logger.log_operation(
                operation="query",
                agent_id=f"agent_{i}",
                input_data={},
                output_data={},
                cost_reduction=60.0,
                duration_ms=100.0,
                validation_status=ValidationStatus.PASS,
                session_id="session_1" if i < 2 else "session_2",
            )

        trail = logger.get_audit_trail(session_id="session_1")
        assert len(trail) == 2

    def test_compliance_report(self):
        """Test compliance reporting."""
        logger = AuditLogger()

        for i in range(5):
            logger.log_operation(
                operation="query",
                agent_id="agent_1",
                input_data={},
                output_data={},
                cost_reduction=60.0 + i * 5,
                duration_ms=100.0 + i * 10,
                validation_status=ValidationStatus.PASS if i % 2 == 0 else ValidationStatus.FAIL,
            )

        report = logger.get_compliance_report()
        assert report["total_operations"] == 5
        assert report["compliance_rate"] > 0


class TestPhase3Integration:
    """Test Phase 3 integration scenarios."""

    def test_langsmith_with_decomposition(self):
        """Test LangSmith tracing with decomposed queries."""
        decomposer = QueryDecomposer()
        tracer = LangSmithTracer()

        # Decompose
        plan = decomposer.decompose("SELECT * FROM users JOIN orders")

        # Trace each sub-query
        for sq in plan.sub_queries:
            tracer.trace_query(
                sq.query_text,
                {
                    "query_id": sq.id,
                    "baseline_tokens": int(sq.estimated_tokens * 1.5),
                    "optimized_tokens": int(sq.estimated_tokens * 0.6),
                    "cost_reduction_percent": 60.0,
                },
                "agent_1",
            )

        analytics = tracer.get_cost_analytics()
        assert analytics.total_operations == len(plan.sub_queries)

    def test_decomposition_with_qa(self):
        """Test decomposition output validation."""
        decomposer = QueryDecomposer()
        validator = QualityValidator()

        plan = decomposer.decompose("SELECT * FROM users JOIN orders")

        # Validate the decomposition estimate
        result = {
            "cost_reduction": plan.estimated_reduction,
            "latency_ms": 150.0,
            "model_accuracy": 85.0,
        }

        validation = validator.validate(result)
        assert len(validation) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
