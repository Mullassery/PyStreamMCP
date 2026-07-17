"""LangSmith integration for PyStreamMCP.

Enables tracing, cost analytics, and performance monitoring
through LangSmith's platform.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class SpanType(str, Enum):
    """LangSmith span types."""
    QUERY = "query"
    DISCOVER = "discover"
    OPTIMIZE = "optimize"
    AGENT = "agent"
    TOOL = "tool"


@dataclass
class LangSmithSpan:
    """LangSmith trace span."""

    name: str
    span_type: SpanType
    start_time: str
    end_time: Optional[str] = None
    duration_ms: Optional[float] = None
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    status: str = "running"  # running, success, error
    parent_span_id: Optional[str] = None
    span_id: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class CostAnalytics:
    """Cost analytics from traced operations."""

    total_baseline_tokens: int = 0
    total_optimized_tokens: int = 0
    total_cost_reduction_percent: float = 0.0
    total_operations: int = 0
    avg_duration_ms: float = 0.0
    error_rate: float = 0.0
    by_intent: Dict[str, Dict[str, float]] = field(default_factory=dict)
    by_model: Dict[str, Dict[str, float]] = field(default_factory=dict)


class LangSmithTracer:
    """Tracer for LangSmith integration.

    Records all PyStreamMCP operations as LangSmith spans
    for distributed tracing and cost analytics.
    """

    def __init__(self, api_key: Optional[str] = None, project_name: str = "pystreammcp"):
        """Initialize LangSmith tracer.

        Args:
            api_key: LangSmith API key
            project_name: Project name in LangSmith
        """
        self.api_key = api_key
        self.project_name = project_name
        self.spans: List[LangSmithSpan] = []
        self.active_spans: Dict[str, LangSmithSpan] = {}
        self.root_trace_id: Optional[str] = None

    def start_trace(self, trace_name: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Start a new trace.

        Args:
            trace_name: Name of the trace
            metadata: Additional metadata

        Returns:
            Trace ID
        """
        self.root_trace_id = datetime.now().isoformat()
        return self.root_trace_id

    def start_span(
        self,
        name: str,
        span_type: SpanType,
        input_data: Dict[str, Any],
        parent_span_id: Optional[str] = None,
    ) -> str:
        """Start a span.

        Args:
            name: Span name
            span_type: Type of span
            input_data: Input data
            parent_span_id: Parent span ID

        Returns:
            Span ID
        """
        span = LangSmithSpan(
            name=name,
            span_type=span_type,
            start_time=datetime.now().isoformat(),
            input_data=input_data,
            parent_span_id=parent_span_id,
        )

        self.active_spans[span.span_id] = span
        return span.span_id

    def end_span(
        self,
        span_id: str,
        output_data: Dict[str, Any],
        status: str = "success",
        error: Optional[str] = None,
    ) -> None:
        """End a span.

        Args:
            span_id: Span ID
            output_data: Output data
            status: Span status
            error: Error message if failed
        """
        if span_id not in self.active_spans:
            return

        span = self.active_spans.pop(span_id)
        span.end_time = datetime.now().isoformat()
        span.output_data = output_data
        span.status = status
        span.error = error

        # Calculate duration
        try:
            start = datetime.fromisoformat(span.start_time)
            end = datetime.fromisoformat(span.end_time)
            span.duration_ms = (end - start).total_seconds() * 1000
        except:
            pass

        self.spans.append(span)

    def trace_query(
        self,
        query_text: str,
        result: Dict[str, Any],
        agent_id: str,
    ) -> str:
        """Trace a query operation.

        Args:
            query_text: Query text
            result: Query result
            agent_id: Agent ID

        Returns:
            Span ID
        """
        span_id = self.start_span(
            name=f"query:{agent_id}",
            span_type=SpanType.QUERY,
            input_data={"query": query_text, "agent_id": agent_id},
        )

        self.end_span(
            span_id,
            output_data={
                "query_id": result.get("query_id"),
                "baseline_tokens": result.get("baseline_tokens"),
                "optimized_tokens": result.get("optimized_tokens"),
                "cost_reduction": result.get("cost_reduction_percent"),
            },
        )

        return span_id

    def get_cost_analytics(self) -> CostAnalytics:
        """Get cost analytics from traces.

        Returns:
            Cost analytics
        """
        analytics = CostAnalytics()

        if not self.spans:
            return analytics

        analytics.total_operations = len(self.spans)

        for span in self.spans:
            if span.output_data:
                baseline = span.output_data.get("baseline_tokens", 0)
                optimized = span.output_data.get("optimized_tokens", 0)

                analytics.total_baseline_tokens += baseline
                analytics.total_optimized_tokens += optimized

                if span.duration_ms:
                    analytics.avg_duration_ms += span.duration_ms

        # Calculate averages
        if analytics.total_operations > 0:
            analytics.avg_duration_ms /= analytics.total_operations

        if analytics.total_baseline_tokens > 0:
            analytics.total_cost_reduction_percent = (
                100 * (1 - analytics.total_optimized_tokens / analytics.total_baseline_tokens)
            )

        analytics.error_rate = sum(1 for s in self.spans if s.status == "error") / len(self.spans)

        return analytics

    def export_to_langsmith(self) -> Dict[str, Any]:
        """Export traces to LangSmith format.

        Returns:
            LangSmith-compatible trace data
        """
        return {
            "project": self.project_name,
            "traces": [
                {
                    "id": span.span_id,
                    "name": span.name,
                    "type": span.span_type.value,
                    "start_time": span.start_time,
                    "end_time": span.end_time,
                    "duration_ms": span.duration_ms,
                    "inputs": span.input_data,
                    "outputs": span.output_data,
                    "status": span.status,
                    "error": span.error,
                }
                for span in self.spans
            ],
            "analytics": self.get_cost_analytics().__dict__,
        }

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for LangSmith dashboard.

        Returns:
            Dashboard-ready data
        """
        analytics = self.get_cost_analytics()

        return {
            "overview": {
                "total_queries": analytics.total_operations,
                "avg_duration_ms": round(analytics.avg_duration_ms, 2),
                "cost_reduction_percent": round(analytics.total_cost_reduction_percent, 2),
                "error_rate": round(analytics.error_rate * 100, 2),
            },
            "cost_breakdown": {
                "baseline_tokens": analytics.total_baseline_tokens,
                "optimized_tokens": analytics.total_optimized_tokens,
                "total_saved": analytics.total_baseline_tokens - analytics.total_optimized_tokens,
            },
            "performance": {
                "p50": self._calculate_percentile(50),
                "p95": self._calculate_percentile(95),
                "p99": self._calculate_percentile(99),
            },
        }

    def _calculate_percentile(self, percentile: int) -> float:
        """Calculate duration percentile."""
        durations = [s.duration_ms for s in self.spans if s.duration_ms]
        if not durations:
            return 0.0

        durations.sort()
        index = int(len(durations) * percentile / 100)
        return durations[min(index, len(durations) - 1)]
