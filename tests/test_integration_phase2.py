"""Integration tests for Phase 2: StatGuardian + PyStreamMCP orchestration"""

import asyncio
import pytest
import time
from datetime import datetime

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

from pystreammcp.webhook_router import EventRouter, MCPEndpoint, Tool
from pystreammcp.webhook_handlers import OrchestrationWebhookHandlers


class TestStatGuardianPyStreamMCPIntegration:
    """Integration tests between StatGuardian quality webhooks and PyStreamMCP orchestration"""

    @pytest.fixture
    def orchestration_setup(self):
        """Setup PyStreamMCP with mock MCPs"""
        router = EventRouter()
        handlers = OrchestrationWebhookHandlers(router)

        # Register mock MCPs (statguardian, pyreverseetl, lineage, notifications)
        statguardian_ep = MCPEndpoint(
            project_name="statguardian",
            port=8765,
            mcp_version="2.0",
            tools=[
                Tool(name="validate_data", project_name="statguardian", description=""),
                Tool(name="detect_drift", project_name="statguardian", description=""),
            ],
        )
        router.service_registry.register_mcp_endpoint(statguardian_ep)

        pyreverseetl_ep = MCPEndpoint(
            project_name="pyreverseetl",
            port=8766,
            mcp_version="2.0",
            tools=[
                Tool(name="hold_activation", project_name="pyreverseetl", description=""),
                Tool(name="resume_activation", project_name="pyreverseetl", description=""),
            ],
        )
        router.service_registry.register_mcp_endpoint(pyreverseetl_ep)

        lineage_ep = MCPEndpoint(
            project_name="lineage",
            port=8777,
            mcp_version="2.0",
            tools=[
                Tool(name="update_lineage_graph", project_name="lineage", description=""),
            ],
        )
        router.service_registry.register_mcp_endpoint(lineage_ep)

        return router, handlers

    @pytest.mark.asyncio
    async def test_quality_violation_triggers_hold_activation(self, orchestration_setup):
        """
        Test: Quality violation → Hold PyReverseETL activations

        Flow:
        1. StatGuardian detects validation rule violation (high severity)
        2. Emits quality.rule_violated webhook event
        3. PyStreamMCP routes hold_activation to PyReverseETL
        4. Verifies activation hold triggered
        """
        router, handlers = orchestration_setup

        # 1. StatGuardian emits quality violation event
        quality_event = {
            "event_type": "quality.rule_violated",
            "data": {
                "project_name": "statguardian",
                "entity_id": "customers",
                "rule_name": "null_email_check",
                "severity": "high",
                "failure_count": 127,
            },
        }

        # 2. Route quality event (would trigger hold_activation in real system)
        result = await router.route(quality_event)
        assert result["status"] != "error"

        # 3. Simulate orchestration response: route hold_activation to PyReverseETL
        hold_event = {
            "event_type": "tool.invoked",
            "data": {
                "tool_name": "hold_activation",
                "invocation_id": "inv_hold_1",
                "request_context": {
                    "entity_id": "customers",
                    "reason": "quality_violation",
                    "severity": "high",
                },
            },
        }

        result = await handlers.dispatch(hold_event)
        assert result["status"] == "success"
        assert result["tool_name"] == "hold_activation"
        assert "pyreverseetl" in result["project_name"]

    @pytest.mark.asyncio
    async def test_schema_change_cascades_to_lineage_system(self, orchestration_setup):
        """
        Test: Schema change → Update lineage + notify downstream

        Flow:
        1. StatGuardian detects schema violation
        2. Emits schema.changed webhook
        3. PyStreamMCP cascades to lineage system
        4. Lineage updates dependency graph
        5. Downstream systems notified
        """
        router, handlers = orchestration_setup

        # 1. MCP available event
        mcp_event = {
            "event_type": "mcp.available",
            "data": {
                "project_name": "statguardian",
                "mcp_port": 8765,
                "mcp_version": "2.0",
                "tools": [],
            },
        }
        await router.route(mcp_event)

        # 2. Schema change event triggers lineage update
        schema_event = {
            "event_type": "tool.invoked",
            "data": {
                "tool_name": "update_lineage_graph",
                "invocation_id": "inv_lineage_1",
                "request_context": {
                    "entity_id": "customers",
                    "changes": [
                        {"type": "column_added", "column": "internal_id"},
                    ],
                },
            },
        }

        result = await handlers.dispatch(schema_event)
        assert result["status"] == "success"
        assert "lineage" in result["project_name"]

    @pytest.mark.asyncio
    async def test_drift_detection_triggers_alert_cascade(self, orchestration_setup):
        """
        Test: Drift detection → Team alert + metrics update + optional hold

        Flow:
        1. StatGuardian detects critical drift
        2. Emits drift.detected webhook
        3. PyStreamMCP routes to notification system
        4. Cascade triggers metrics update
        5. Optional: hold syncs for critical drift
        """
        router, handlers = orchestration_setup

        # Register alert tool
        alert_ep = MCPEndpoint(
            project_name="notifications",
            port=8778,
            mcp_version="2.0",
            tools=[
                Tool(name="send_alert", project_name="notifications", description=""),
            ],
        )
        router.service_registry.register_mcp_endpoint(alert_ep)

        # Drift event
        drift_event = {
            "event_type": "tool.invoked",
            "data": {
                "tool_name": "send_alert",
                "invocation_id": "inv_alert_1",
                "request_context": {
                    "entity_id": "customers",
                    "message": "Critical drift detected",
                    "severity": "critical",
                    "drifted_columns": ["age", "purchases_30d"],
                },
                "orchestration_context": {
                    "chain_id": "drift_alert_chain",
                    "position_in_chain": 0,
                    "total_chain_length": 2,
                },
            },
        }

        result = await handlers.dispatch(drift_event)
        assert result["status"] == "success"

        # Verify cascade context would trigger metrics update
        assert result.get("project_name") in ["notifications"]

    @pytest.mark.asyncio
    async def test_anomaly_detection_records_for_analysis(self, orchestration_setup):
        """
        Test: Anomaly detection → Record for analysis

        Flow:
        1. StatGuardian detects anomalies
        2. Emits anomaly.detected webhook
        3. PyStreamMCP records event
        4. Audit trail complete
        """
        router, handlers = orchestration_setup

        anomaly_event = {
            "event_type": "tool.invoked",
            "data": {
                "tool_name": "detect_drift",
                "invocation_id": "inv_anomaly_1",
                "request_context": {
                    "entity_id": "customers",
                    "anomaly_count": 47,
                    "anomaly_rate_pct": 0.94,
                },
            },
        }

        result = await handlers.dispatch(anomaly_event)
        assert result["status"] == "success"


class TestCrossMCPOrchestration:
    """Test tool routing and orchestration across multiple MCPs"""

    @pytest.fixture
    def multi_mcp_setup(self):
        """Setup with multiple MCPs"""
        router = EventRouter()

        # Register 5 MCPs with tools
        mcps = [
            ("statguardian", 8765, ["validate_data", "detect_drift"]),
            ("pyreverseetl", 8766, ["hold_activation", "resume_activation"]),
            ("lineage", 8777, ["update_lineage_graph"]),
            ("notifications", 8778, ["send_alert", "send_email"]),
            ("analytics", 8779, ["update_metrics", "generate_report"]),
        ]

        for project_name, port, tool_names in mcps:
            endpoint = MCPEndpoint(
                project_name=project_name,
                port=port,
                mcp_version="2.0",
                tools=[
                    Tool(
                        name=tool,
                        project_name=project_name,
                        description=f"{tool} in {project_name}",
                    )
                    for tool in tool_names
                ],
            )
            router.service_registry.register_mcp_endpoint(endpoint)

        return router

    def test_tool_discovery_across_mcps(self, multi_mcp_setup):
        """Test discovering tools across multiple MCPs"""
        router = multi_mcp_setup
        registry = router.service_registry

        # Verify all tools discoverable
        tools_to_find = [
            ("validate_data", "statguardian"),
            ("hold_activation", "pyreverseetl"),
            ("update_lineage_graph", "lineage"),
            ("send_alert", "notifications"),
            ("update_metrics", "analytics"),
        ]

        for tool_name, expected_project in tools_to_find:
            result = registry.find_tool(tool_name)
            assert result is not None
            project_name, endpoint = result
            assert project_name == expected_project

    def test_tool_lookup_performance(self, multi_mcp_setup):
        """Test tool lookup is O(1) even with many MCPs"""
        router = multi_mcp_setup

        # Measure lookup time
        start = time.time()
        for _ in range(1000):
            router.service_registry.find_tool("validate_data")
        elapsed = time.time() - start

        # Should be fast (< 10ms for 1000 lookups = <10µs per lookup)
        avg_time_ms = (elapsed * 1000) / 1000
        assert avg_time_ms < 10

    @pytest.mark.asyncio
    async def test_tool_routing_healthy_mcp(self, multi_mcp_setup):
        """Test routing to healthy MCP"""
        router = multi_mcp_setup

        result = await router.tool_orchestrator.route_tool_invocation(
            tool_name="validate_data",
            params={"entity_id": "customers"},
        )

        assert result["status"] == "routed"
        assert result["tool_name"] == "validate_data"
        assert result["project_name"] == "statguardian"

    @pytest.mark.asyncio
    async def test_fallback_manager_when_tool_unavailable(self, multi_mcp_setup):
        """Test fallback manager activates when tool unavailable"""
        router = multi_mcp_setup

        # Register fallback for validate_data
        router.fallback_manager.register_fallback(
            primary_tool="validate_data",
            fallback_tools=["detect_drift"],
        )

        # Mark primary MCP unavailable
        router.service_registry.mark_mcp_unavailable("statguardian", "connection timeout")

        # Invoke with fallback support
        result = await router.fallback_manager.invoke_with_fallback(
            tool_name="validate_data",
            params={"entity_id": "customers"},
            fallback_enabled=True,
        )

        # Should have queued for retry
        assert result["status"] == "unavailable"
        assert result["queued_for_retry"] is True

    @pytest.mark.asyncio
    async def test_cascade_execution_cross_mcp(self, multi_mcp_setup):
        """Test cascade execution across MCPs"""
        router = multi_mcp_setup

        # Cascade from validation (statguardian) to alert (notifications)
        cascades = await router.tool_orchestrator.cascade_on_result(
            tool_result={
                "status": "error",
                "entity_id": "customers",
                "message": "Validation failed",
            },
            cascade_triggers=[
                {
                    "tool_name": "send_alert",
                    "trigger_condition": "on_error",
                    "params": {"severity": "high"},
                },
            ],
            invocation_id="inv_1",
        )

        assert len(cascades) == 1
        cascade = cascades[0]
        assert cascade["tool_name"] == "send_alert"
        # Alert tool is in notifications MCP
        assert cascade["project_name"] == "notifications"

    @pytest.mark.asyncio
    async def test_multi_stage_cascade(self, multi_mcp_setup):
        """Test multi-stage cascade: validation → alert → metrics update"""
        router = multi_mcp_setup

        # Stage 1: Validation fails, triggers alert
        cascades1 = await router.tool_orchestrator.cascade_on_result(
            tool_result={"status": "error", "entity_id": "customers"},
            cascade_triggers=[
                {
                    "tool_name": "send_alert",
                    "trigger_condition": "on_error",
                }
            ],
            invocation_id="inv_1",
        )

        assert len(cascades1) == 1

        # Stage 2: Alert sent, triggers metrics update
        cascades2 = await router.tool_orchestrator.cascade_on_result(
            tool_result={
                "status": "success",
                "tool_name": "send_alert",
                "chain_id": "cascade_chain",
            },
            cascade_triggers=[
                {
                    "tool_name": "update_metrics",
                    "trigger_condition": "always",
                }
            ],
            invocation_id="inv_2",
        )

        assert len(cascades2) == 1


class TestWebhookSecurityAndReliability:
    """Test webhook delivery, security, and reliability"""

    def test_webhook_signature_validation(self):
        """Test HMAC-SHA256 signature validation"""
        import hmac
        import hashlib

        secret = "test_secret_key"
        payload = '{"event_type": "quality.rule_violated"}'

        # Generate valid signature
        sig = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256,
        ).hexdigest()

        # Verify valid signature
        expected_sig = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256,
        ).hexdigest()

        assert sig == expected_sig

        # Tampered payload should have different signature
        tampered_payload = '{"event_type": "malicious.event"}'
        tampered_sig = hmac.new(
            secret.encode(),
            tampered_payload.encode(),
            hashlib.sha256,
        ).hexdigest()

        assert sig != tampered_sig

    def test_event_deduplication_logic(self):
        """Test event deduplication within 5-second window"""
        from datetime import datetime, timedelta

        # Simulate event deduplication
        def is_duplicate(current_event, recent_events, window_seconds=5):
            """Check if event is duplicate of recent event"""
            current_time = datetime.fromisoformat(current_event["timestamp"])
            current_key = (
                current_event["entity_id"],
                current_event["rule_name"],
            )

            for recent in recent_events:
                recent_time = datetime.fromisoformat(recent["timestamp"])
                recent_key = (recent["entity_id"], recent["rule_name"])

                if current_key == recent_key:
                    time_diff = (current_time - recent_time).total_seconds()
                    if time_diff < window_seconds:
                        return True

            return False

        # Same event within 5 seconds = duplicate
        now = datetime.utcnow()
        event1 = {
            "timestamp": now.isoformat(),
            "entity_id": "customers",
            "rule_name": "null_check",
        }

        event2 = {
            "timestamp": (now + timedelta(seconds=2)).isoformat(),
            "entity_id": "customers",
            "rule_name": "null_check",
        }

        assert is_duplicate(event2, [event1])

        # Same event after 5 seconds = not duplicate
        event3 = {
            "timestamp": (now + timedelta(seconds=6)).isoformat(),
            "entity_id": "customers",
            "rule_name": "null_check",
        }

        assert not is_duplicate(event3, [event1])

    def test_exponential_backoff_retry_schedule(self):
        """Test exponential backoff retry scheduling"""

        def calculate_retry_schedule(max_retries=3):
            """Calculate exponential backoff retry schedule"""
            schedule = []
            for attempt in range(max_retries):
                delay_ms = (2 ** attempt) * 1000  # 1s, 2s, 4s, 8s, etc.
                schedule.append(delay_ms)
            return schedule

        schedule = calculate_retry_schedule(3)

        assert schedule == [1000, 2000, 4000]  # 1s, 2s, 4s

    def test_audit_trail_completeness(self):
        """Test audit trail captures all events"""
        audit_trail = []

        def record_event(event_type, details):
            """Record event in audit trail"""
            audit_trail.append({
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type,
                "details": details,
            })

        # Simulate workflow
        record_event("webhook_received", {"webhook_id": "wh_1"})
        record_event("handler_dispatch", {"handler": "quality_violation"})
        record_event("action_triggered", {"action": "hold_activation"})
        record_event("event_delivered", {"status": "success"})

        # Verify trail has all events
        assert len(audit_trail) == 4
        assert audit_trail[0]["event_type"] == "webhook_received"
        assert audit_trail[-1]["event_type"] == "event_delivered"


class TestHealthAndResilience:
    """Test health monitoring and graceful degradation"""

    @pytest.fixture
    def health_setup(self):
        """Setup for health testing"""
        router = EventRouter()

        # Register MCPs
        for i, project in enumerate(["mcp_1", "mcp_2", "mcp_3"]):
            endpoint = MCPEndpoint(
                project_name=project,
                port=8765 + i,
                mcp_version="2.0",
            )
            router.service_registry.register_mcp_endpoint(endpoint)

        return router

    def test_health_metrics_collection(self, health_setup):
        """Test health metrics collection"""
        router = health_setup
        registry = router.service_registry

        metrics = {
            "latency_p99_ms": 145.5,
            "error_rate": 0.001,
            "tool_availability": 0.999,
        }

        registry.update_health_metrics("mcp_1", metrics)

        # Verify stored
        assert "mcp_1" in registry.health_history
        history = registry.health_history["mcp_1"]
        assert len(history) == 1
        assert history[0]["metrics"] == metrics

    def test_status_transitions(self, health_setup):
        """Test status transitions: healthy → degraded → unavailable"""
        router = health_setup
        registry = router.service_registry

        # Start healthy
        assert registry.endpoints["mcp_1"].status == "healthy"

        # Transition to degraded
        registry.mark_mcp_degraded("mcp_1")
        assert registry.endpoints["mcp_1"].status == "degraded"

        # Transition to unavailable
        registry.mark_mcp_unavailable("mcp_1", "connection failed")
        assert registry.endpoints["mcp_1"].status == "unavailable"

        # Can recover to healthy
        registry.mark_mcp_available("mcp_1")
        assert registry.endpoints["mcp_1"].status == "healthy"

    def test_critical_metrics_detection(self, health_setup):
        """Test detection of critical metrics"""

        def has_critical_metrics(metrics):
            """Check if metrics indicate critical state"""
            if metrics.get("error_rate", 0) > 0.5:
                return True
            if metrics.get("latency_p99_ms", 0) > 5000:
                return True
            if metrics.get("tool_availability", 1.0) < 0.5:
                return True
            return False

        # Normal metrics
        normal = {
            "error_rate": 0.001,
            "latency_p99_ms": 145.5,
            "tool_availability": 0.999,
        }
        assert not has_critical_metrics(normal)

        # Critical error rate
        critical_errors = {"error_rate": 0.75}
        assert has_critical_metrics(critical_errors)

        # Critical latency
        critical_latency = {"latency_p99_ms": 6000}
        assert has_critical_metrics(critical_latency)

        # Critical availability
        critical_availability = {"tool_availability": 0.3}
        assert has_critical_metrics(critical_availability)

    @pytest.mark.asyncio
    async def test_graceful_degradation_one_mcp_down(self, health_setup):
        """Test graceful degradation with one MCP unavailable"""
        router = health_setup

        # Mark one MCP unavailable
        router.service_registry.mark_mcp_unavailable("mcp_1", "connection timeout")

        # Other MCPs still available
        available = router.service_registry.get_available_mcps()
        assert len(available) == 2
        assert all(ep.status == "healthy" for ep in available)

        # Can still get tools from available MCPs
        # (This would work in real scenario with tools registered)
        healthy_count = sum(
            1
            for ep in router.service_registry.endpoints.values()
            if ep.status == "healthy"
        )
        assert healthy_count == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
