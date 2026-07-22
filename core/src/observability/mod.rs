// Stage 4: Observability & Tracing
// OpenTelemetry integration for decision transparency and performance monitoring

pub mod tracing;
pub mod metrics;
pub mod logging;
pub mod audit;

pub use tracing::{DecisionTracer, TraceSpan, TraceContext};
pub use metrics::{MetricsCollector, PerformanceMetrics, ReductionMetrics};
pub use logging::{StructuredLogger, LogLevel, AuditLog};
pub use audit::{DecisionAuditTrail, DecisionRecord};

use crate::Result;
use serde::{Deserialize, Serialize};
use std::time::Instant;

/// Observability Engine - Stage 4
///
/// Provides complete traceability for all decisions:
/// 1. Distributed tracing (OpenTelemetry)
/// 2. Metrics collection and export
/// 3. Structured logging
/// 4. Audit trail recording
///
/// Enables:
/// - Full decision transparency (why this choice?)
/// - Performance monitoring (latency per stage)
/// - Data reduction tracking (efficiency metrics)
/// - Compliance reporting (audit trail)
/// - Multi-agent tracking (fairness monitoring)
pub struct ObservabilityEngine {
    tracer: DecisionTracer,
    metrics: MetricsCollector,
    logger: StructuredLogger,
    audit_trail: DecisionAuditTrail,
}

impl ObservabilityEngine {
    /// Create new observability engine
    pub fn new(config: ObservabilityConfig) -> Result<Self> {
        let tracer = DecisionTracer::new(config.trace_config)?;
        let metrics = MetricsCollector::new(config.metrics_config)?;
        let logger = StructuredLogger::new(config.log_config)?;
        let audit_trail = DecisionAuditTrail::new(config.audit_config)?;

        Ok(Self {
            tracer,
            metrics,
            logger,
            audit_trail,
        })
    }

    /// Start tracing a complete query
    pub async fn start_query_trace(&self, query: &str, agent_id: Option<&str>) -> Result<QueryTrace> {
        let trace_id = self.tracer.generate_trace_id();
        let start_time = Instant::now();

        let trace = QueryTrace {
            trace_id,
            query: query.to_string(),
            agent_id: agent_id.map(|s| s.to_string()),
            start_time,
            stages: vec![],
        };

        Ok(trace)
    }

    /// Record Stage 1 decision (metadata filtering)
    pub fn record_stage1_decision(
        &self,
        trace_id: &str,
        source_id: &str,
        rank: usize,
        score: f64,
        reason: &str,
    ) -> Result<()> {
        let decision = DecisionRecord {
            trace_id: trace_id.to_string(),
            stage: "Stage1_MetadataFiltering".to_string(),
            decision_type: "source_selection".to_string(),
            subject: source_id.to_string(),
            score,
            reason: reason.to_string(),
            timestamp: std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap_or_default()
                .as_secs() as i64,
        };

        self.audit_trail.record_decision(decision)?;
        Ok(())
    }

    /// Record Stage 2 decision (selective retrieval)
    pub fn record_stage2_decision(
        &self,
        trace_id: &str,
        item_id: &str,
        action: &str,    // "keep" or "filter"
        reason: &str,
        score: f64,
    ) -> Result<()> {
        let decision = DecisionRecord {
            trace_id: trace_id.to_string(),
            stage: "Stage2_SelectiveRetrieval".to_string(),
            decision_type: action.to_string(),
            subject: item_id.to_string(),
            score,
            reason: reason.to_string(),
            timestamp: std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap_or_default()
                .as_secs() as i64,
        };

        self.audit_trail.record_decision(decision)?;
        Ok(())
    }

    /// Record Stage 3 decision (validation)
    pub fn record_stage3_decision(
        &self,
        trace_id: &str,
        check_type: &str,
        passed: bool,
        score: f64,
        message: &str,
    ) -> Result<()> {
        let decision = DecisionRecord {
            trace_id: trace_id.to_string(),
            stage: "Stage3_QualityValidation".to_string(),
            decision_type: check_type.to_string(),
            subject: format!("validation_{}", if passed { "pass" } else { "fail" }),
            score,
            reason: message.to_string(),
            timestamp: std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap_or_default()
                .as_secs() as i64,
        };

        self.audit_trail.record_decision(decision)?;
        Ok(())
    }

    /// Record performance metrics
    pub fn record_performance(
        &self,
        trace_id: &str,
        stage: &str,
        latency_ms: u32,
        data_before: usize,
        data_after: usize,
    ) -> Result<()> {
        let reduction_percent = if data_before > 0 {
            ((data_before - data_after) as f64 / data_before as f64 * 100.0) as u32
        } else {
            0
        };

        self.metrics.record_stage_performance(
            stage,
            latency_ms,
            data_before,
            data_after,
            reduction_percent,
        )?;

        Ok(())
    }

    /// Get complete audit trail for query
    pub fn get_query_audit_trail(&self, trace_id: &str) -> Result<Vec<DecisionRecord>> {
        self.audit_trail.get_decisions_for_trace(trace_id)
    }

    /// Get performance metrics
    pub fn get_performance_metrics(&self) -> Result<PerformanceMetrics> {
        self.metrics.get_metrics()
    }

    /// Export metrics to format
    pub async fn export_metrics(&self, format: &str) -> Result<String> {
        match format {
            "prometheus" => self.metrics.export_prometheus(),
            "json" => self.metrics.export_json(),
            _ => Err(crate::Error::Generic(format!("Unknown format: {}", format))),
        }
    }
}

/// Configuration for observability
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ObservabilityConfig {
    pub trace_config: TraceConfig,
    pub metrics_config: MetricsConfig,
    pub log_config: LogConfig,
    pub audit_config: AuditConfig,
}

impl Default for ObservabilityConfig {
    fn default() -> Self {
        Self {
            trace_config: TraceConfig::default(),
            metrics_config: MetricsConfig::default(),
            log_config: LogConfig::default(),
            audit_config: AuditConfig::default(),
        }
    }
}

/// Trace configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TraceConfig {
    pub enabled: bool,
    pub sample_rate: f64,     // 0-1, default 1.0 (trace all)
    pub export_interval_ms: u64,  // How often to export
}

impl Default for TraceConfig {
    fn default() -> Self {
        Self {
            enabled: true,
            sample_rate: 1.0,
            export_interval_ms: 5000,
        }
    }
}

/// Metrics configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetricsConfig {
    pub enabled: bool,
    pub export_format: String,  // "prometheus", "json", etc.
    pub export_interval_ms: u64,
}

impl Default for MetricsConfig {
    fn default() -> Self {
        Self {
            enabled: true,
            export_format: "prometheus".to_string(),
            export_interval_ms: 10000,
        }
    }
}

/// Logging configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LogConfig {
    pub enabled: bool,
    pub level: String,  // "DEBUG", "INFO", "WARN", "ERROR"
    pub format: String, // "json", "text"
}

impl Default for LogConfig {
    fn default() -> Self {
        Self {
            enabled: true,
            level: "INFO".to_string(),
            format: "json".to_string(),
        }
    }
}

/// Audit configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuditConfig {
    pub enabled: bool,
    pub retention_days: u32,  // How long to keep audit logs
    pub include_decisions: bool,
    pub include_performance: bool,
}

impl Default for AuditConfig {
    fn default() -> Self {
        Self {
            enabled: true,
            retention_days: 90,
            include_decisions: true,
            include_performance: true,
        }
    }
}

/// Query trace with stage data
#[derive(Debug, Clone)]
pub struct QueryTrace {
    pub trace_id: String,
    pub query: String,
    pub agent_id: Option<String>,
    pub start_time: Instant,
    pub stages: Vec<StageTrace>,
}

/// Stage trace data
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StageTrace {
    pub stage: String,
    pub latency_ms: u32,
    pub data_before: usize,
    pub data_after: usize,
    pub reduction_percent: u32,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_observability_engine_creation() {
        let config = ObservabilityConfig::default();
        let engine = ObservabilityEngine::new(config).unwrap();

        let trace = engine.start_query_trace("test query", Some("agent1")).await.unwrap();
        assert!(!trace.trace_id.is_empty());
        assert_eq!(trace.query, "test query");
        assert_eq!(trace.agent_id, Some("agent1".to_string()));
    }

    #[test]
    fn test_record_decisions() {
        let config = ObservabilityConfig::default();
        let engine = ObservabilityEngine::new(config).unwrap();

        let trace_id = "test_trace_123";

        // Record Stage 1 decision
        engine
            .record_stage1_decision(trace_id, "example.com", 1, 0.95, "High authority score")
            .unwrap();

        // Record Stage 2 decision
        engine
            .record_stage2_decision(trace_id, "item_1", "keep", "High relevance", 0.85)
            .unwrap();

        // Record Stage 3 decision
        engine
            .record_stage3_decision(trace_id, "completeness", true, 1.0, "Content is complete")
            .unwrap();
    }

    #[test]
    fn test_record_performance() {
        let config = ObservabilityConfig::default();
        let engine = ObservabilityEngine::new(config).unwrap();

        engine
            .record_performance("trace_1", "Stage1", 45, 1000, 150)
            .unwrap();
        engine
            .record_performance("trace_1", "Stage2", 18, 150, 30)
            .unwrap();
        engine
            .record_performance("trace_1", "Stage3", 25, 30, 25)
            .unwrap();
    }
}
