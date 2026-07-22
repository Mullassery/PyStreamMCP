// Distributed Tracing - Stage 4
// OpenTelemetry integration for decision transparency

use crate::Result;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Decision tracer for OpenTelemetry
pub struct DecisionTracer {
    config: TraceConfig,
    trace_counter: std::sync::atomic::AtomicU64,
}

#[derive(Debug, Clone)]
pub struct TraceConfig {
    pub enabled: bool,
    pub sample_rate: f64,
}

/// Trace context for a complete decision
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TraceContext {
    pub trace_id: String,
    pub parent_span_id: Option<String>,
    pub span_id: String,
    pub timestamp: i64,
    pub metadata: HashMap<String, String>,
}

/// Individual trace span (decision point)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TraceSpan {
    pub trace_id: String,
    pub span_id: String,
    pub parent_span_id: Option<String>,
    pub operation: String,      // "select_source", "rerank_item", "validate_content", etc.
    pub start_time: i64,
    pub end_time: i64,
    pub duration_ms: u32,
    pub status: SpanStatus,
    pub attributes: HashMap<String, String>,
    pub events: Vec<SpanEvent>,
}

/// Span status
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum SpanStatus {
    OK,
    Error,
    Cancelled,
}

/// Span event (checkpoint within span)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SpanEvent {
    pub name: String,
    pub timestamp: i64,
    pub attributes: HashMap<String, String>,
}

impl DecisionTracer {
    /// Create new tracer
    pub fn new(config: TraceConfig) -> Result<Self> {
        Ok(Self {
            config,
            trace_counter: std::sync::atomic::AtomicU64::new(0),
        })
    }

    /// Generate unique trace ID
    pub fn generate_trace_id(&self) -> String {
        let counter = self
            .trace_counter
            .fetch_add(1, std::sync::atomic::Ordering::SeqCst);
        format!("trace-{:016x}", counter)
    }

    /// Generate unique span ID
    pub fn generate_span_id(&self) -> String {
        let counter = self
            .trace_counter
            .fetch_add(1, std::sync::atomic::Ordering::SeqCst);
        format!("span-{:016x}", counter)
    }

    /// Create new trace context
    pub fn create_context(&self, trace_id: String) -> TraceContext {
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_millis() as i64;

        TraceContext {
            trace_id,
            parent_span_id: None,
            span_id: self.generate_span_id(),
            timestamp: now,
            metadata: HashMap::new(),
        }
    }

    /// Create child span (nested decision)
    pub fn create_child_span(
        &self,
        parent_context: &TraceContext,
        operation: &str,
    ) -> TraceSpan {
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_millis() as i64;

        TraceSpan {
            trace_id: parent_context.trace_id.clone(),
            span_id: self.generate_span_id(),
            parent_span_id: Some(parent_context.span_id.clone()),
            operation: operation.to_string(),
            start_time: now,
            end_time: now,
            duration_ms: 0,
            status: SpanStatus::OK,
            attributes: HashMap::new(),
            events: vec![],
        }
    }

    /// Add attribute to span
    pub fn add_span_attribute(
        &self,
        span: &mut TraceSpan,
        key: &str,
        value: &str,
    ) {
        span.attributes.insert(key.to_string(), value.to_string());
    }

    /// Add event to span (checkpoint)
    pub fn add_span_event(&self, span: &mut TraceSpan, event_name: &str) {
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_millis() as i64;

        span.events.push(SpanEvent {
            name: event_name.to_string(),
            timestamp: now,
            attributes: HashMap::new(),
        });
    }

    /// Mark span as complete
    pub fn complete_span(&self, span: &mut TraceSpan) {
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_millis() as i64;

        span.end_time = now;
        span.duration_ms = ((now - span.start_time) as u32).max(1);
    }

    /// Export span to OpenTelemetry format
    pub fn export_span(&self, span: &TraceSpan) -> Result<String> {
        let json = serde_json::to_string(span)?;
        Ok(json)
    }

    /// Create root span for complete query
    pub fn create_root_span(&self, trace_id: String, query: &str) -> TraceSpan {
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_millis() as i64;

        let mut span = TraceSpan {
            trace_id,
            span_id: self.generate_span_id(),
            parent_span_id: None,
            operation: "query_processing".to_string(),
            start_time: now,
            end_time: now,
            duration_ms: 0,
            status: SpanStatus::OK,
            attributes: HashMap::new(),
            events: vec![],
        };

        span.attributes.insert("query".to_string(), query.to_string());
        span
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_trace_id_generation() {
        let config = TraceConfig {
            enabled: true,
            sample_rate: 1.0,
        };
        let tracer = DecisionTracer::new(config).unwrap();

        let id1 = tracer.generate_trace_id();
        let id2 = tracer.generate_trace_id();

        assert_ne!(id1, id2);
        assert!(id1.starts_with("trace-"));
    }

    #[test]
    fn test_create_context() {
        let config = TraceConfig {
            enabled: true,
            sample_rate: 1.0,
        };
        let tracer = DecisionTracer::new(config).unwrap();

        let context = tracer.create_context("trace-123".to_string());
        assert_eq!(context.trace_id, "trace-123");
        assert!(context.span_id.starts_with("span-"));
    }

    #[test]
    fn test_create_child_span() {
        let config = TraceConfig {
            enabled: true,
            sample_rate: 1.0,
        };
        let tracer = DecisionTracer::new(config).unwrap();

        let parent = tracer.create_context("trace-123".to_string());
        let child = tracer.create_child_span(&parent, "select_source");

        assert_eq!(child.trace_id, parent.trace_id);
        assert_eq!(child.parent_span_id, Some(parent.span_id.clone()));
        assert_eq!(child.operation, "select_source");
    }

    #[test]
    fn test_span_lifecycle() {
        let config = TraceConfig {
            enabled: true,
            sample_rate: 1.0,
        };
        let tracer = DecisionTracer::new(config).unwrap();

        let mut span = tracer.create_root_span("trace-123".to_string(), "test query");

        tracer.add_span_attribute(&mut span, "source", "example.com");
        tracer.add_span_event(&mut span, "source_selected");
        tracer.add_span_event(&mut span, "validation_passed");

        tracer.complete_span(&mut span);

        assert!(span.duration_ms > 0);
        assert_eq!(span.events.len(), 2);
        assert_eq!(span.attributes.get("source").unwrap(), "example.com");
    }
}
