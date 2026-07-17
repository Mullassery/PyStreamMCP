"""OpenTelemetry metrics for PyStreamMCP.

Collects and exports metrics to Grafana, Datadog, and other OTEL backends.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict


@dataclass
class MetricPoint:
    """Single metric data point."""

    timestamp: str
    value: float
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class Metric:
    """OpenTelemetry metric."""

    name: str
    description: str
    unit: str
    type: str  # counter, gauge, histogram
    points: List[MetricPoint] = field(default_factory=list)


class MetricsCollector:
    """Collects and manages PyStreamMCP metrics.

    Tracks:
    - Query execution time
    - Token usage (baseline vs optimized)
    - Cost reduction percentage
    - Error rates
    - Source usage
    - Model accuracy
    """

    def __init__(self, service_name: str = "pystreammcp"):
        """Initialize metrics collector.

        Args:
            service_name: Service name for metrics
        """
        self.service_name = service_name
        self.metrics: Dict[str, Metric] = {}
        self._initialize_metrics()
        self.buffer: List[Dict[str, Any]] = []

    def _initialize_metrics(self) -> None:
        """Initialize default metrics."""
        self.metrics["query_duration_ms"] = Metric(
            name="pystreammcp_query_duration_ms",
            description="Query execution duration in milliseconds",
            unit="ms",
            type="histogram",
        )

        self.metrics["baseline_tokens"] = Metric(
            name="pystreammcp_baseline_tokens",
            description="Baseline token count before optimization",
            unit="tokens",
            type="counter",
        )

        self.metrics["optimized_tokens"] = Metric(
            name="pystreammcp_optimized_tokens",
            description="Optimized token count after optimization",
            unit="tokens",
            type="counter",
        )

        self.metrics["cost_reduction_percent"] = Metric(
            name="pystreammcp_cost_reduction_percent",
            description="Cost reduction percentage",
            unit="%",
            type="gauge",
        )

        self.metrics["query_count"] = Metric(
            name="pystreammcp_query_count",
            description="Total number of queries",
            unit="queries",
            type="counter",
        )

        self.metrics["model_accuracy"] = Metric(
            name="pystreammcp_model_accuracy",
            description="ML model prediction accuracy",
            unit="%",
            type="gauge",
        )

        self.metrics["errors"] = Metric(
            name="pystreammcp_errors",
            description="Number of errors",
            unit="errors",
            type="counter",
        )

    def record_query(
        self,
        duration_ms: float,
        baseline_tokens: int,
        optimized_tokens: int,
        cost_reduction: float,
        agent_id: str,
        intent: str,
    ) -> None:
        """Record a query execution.

        Args:
            duration_ms: Query execution time
            baseline_tokens: Baseline token count
            optimized_tokens: Optimized token count
            cost_reduction: Cost reduction percentage
            agent_id: Agent ID
            intent: Query intent
        """
        timestamp = datetime.now().isoformat()
        labels = {
            "agent_id": agent_id,
            "intent": intent,
            "service": self.service_name,
        }

        # Record metrics
        self.metrics["query_duration_ms"].points.append(MetricPoint(timestamp, duration_ms, labels))
        self.metrics["baseline_tokens"].points.append(MetricPoint(timestamp, baseline_tokens, labels))
        self.metrics["optimized_tokens"].points.append(MetricPoint(timestamp, optimized_tokens, labels))
        self.metrics["cost_reduction_percent"].points.append(MetricPoint(timestamp, cost_reduction, labels))

        # Increment counters
        query_metric = self.metrics["query_count"]
        query_metric.points.append(MetricPoint(timestamp, len(query_metric.points) + 1, labels))

        self.buffer.append({
            "type": "query",
            "timestamp": timestamp,
            "duration_ms": duration_ms,
            "baseline_tokens": baseline_tokens,
            "optimized_tokens": optimized_tokens,
            "cost_reduction": cost_reduction,
            "agent_id": agent_id,
            "intent": intent,
        })

    def record_model_accuracy(self, accuracy: float, model_version: str) -> None:
        """Record model accuracy.

        Args:
            accuracy: Accuracy percentage (0-100)
            model_version: Model version
        """
        timestamp = datetime.now().isoformat()
        labels = {
            "model_version": model_version,
            "service": self.service_name,
        }

        self.metrics["model_accuracy"].points.append(MetricPoint(timestamp, accuracy, labels))

    def record_error(self, error_type: str, agent_id: str) -> None:
        """Record an error.

        Args:
            error_type: Type of error
            agent_id: Agent ID
        """
        timestamp = datetime.now().isoformat()
        labels = {
            "error_type": error_type,
            "agent_id": agent_id,
            "service": self.service_name,
        }

        self.metrics["errors"].points.append(MetricPoint(timestamp, 1, labels))

    def get_metrics(self) -> Dict[str, Metric]:
        """Get all collected metrics.

        Returns:
            Metrics dictionary
        """
        return self.metrics

    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format.

        Returns:
            Prometheus-formatted metrics
        """
        lines = []

        for metric_name, metric in self.metrics.items():
            lines.append(f"# HELP {metric.name} {metric.description}")
            lines.append(f"# TYPE {metric.name} {metric.type}")

            for point in metric.points[-10:]:  # Last 10 points
                labels_str = ",".join(f'{k}="{v}"' for k, v in point.labels.items())
                line = f'{metric.name}{{{labels_str}}} {point.value}'
                lines.append(line)

        return "\n".join(lines)

    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary.

        Returns:
            Summary statistics
        """
        queries = self.metrics["query_count"].points
        durations = [p.value for p in self.metrics["query_duration_ms"].points]
        reductions = [p.value for p in self.metrics["cost_reduction_percent"].points]

        return {
            "total_queries": len(queries),
            "avg_duration_ms": sum(durations) / len(durations) if durations else 0,
            "avg_cost_reduction": sum(reductions) / len(reductions) if reductions else 0,
            "total_baseline_tokens": sum(p.value for p in self.metrics["baseline_tokens"].points),
            "total_optimized_tokens": sum(p.value for p in self.metrics["optimized_tokens"].points),
            "total_errors": len(self.metrics["errors"].points),
        }

    def flush_buffer(self) -> List[Dict[str, Any]]:
        """Flush metrics buffer for export.

        Returns:
            Buffered metrics
        """
        result = self.buffer.copy()
        self.buffer.clear()
        return result
