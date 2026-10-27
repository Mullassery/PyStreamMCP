"""Observability module for PyStreamMCP.

In-process metrics collection and summaries. This is not an OpenTelemetry
exporter; the collector stores samples locally for inspection.
"""

from .metrics import Metric, MetricPoint, MetricsCollector

__all__ = [
    "Metric",
    "MetricPoint",
    "MetricsCollector",
]
