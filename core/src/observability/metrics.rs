// Metrics Collection - Stage 4
// Performance and efficiency metrics collection

use crate::Result;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::{Arc, Mutex};

/// Metrics collector
pub struct MetricsCollector {
    config: MetricsConfig,
    stage_metrics: Arc<Mutex<HashMap<String, StageMetrics>>>,
    reduction_metrics: Arc<Mutex<ReductionMetrics>>,
}

#[derive(Debug, Clone)]
pub struct MetricsConfig {
    pub enabled: bool,
    pub export_format: String,
}

/// Metrics for a single stage
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StageMetrics {
    pub stage: String,
    pub total_queries: u64,
    pub total_latency_ms: u64,
    pub avg_latency_ms: u32,
    pub min_latency_ms: u32,
    pub max_latency_ms: u32,
    pub total_data_before: u64,
    pub total_data_after: u64,
    pub avg_reduction_percent: u32,
}

/// Overall performance metrics
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PerformanceMetrics {
    pub stage1: StageMetrics,
    pub stage2: StageMetrics,
    pub stage3: StageMetrics,
    pub combined_latency_ms: u32,
    pub combined_reduction_percent: u32,
    pub total_queries: u64,
}

/// Data reduction metrics
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ReductionMetrics {
    pub stage1_reductions: Vec<u32>,
    pub stage2_reductions: Vec<u32>,
    pub stage3_reductions: Vec<u32>,
    pub cache_hits: u64,
    pub cache_misses: u64,
    pub fallback_invocations: u64,
}

impl MetricsCollector {
    /// Create new metrics collector
    pub fn new(config: MetricsConfig) -> Result<Self> {
        Ok(Self {
            config,
            stage_metrics: Arc::new(Mutex::new(HashMap::new())),
            reduction_metrics: Arc::new(Mutex::new(ReductionMetrics {
                stage1_reductions: vec![],
                stage2_reductions: vec![],
                stage3_reductions: vec![],
                cache_hits: 0,
                cache_misses: 0,
                fallback_invocations: 0,
            })),
        })
    }

    /// Record stage performance
    pub fn record_stage_performance(
        &self,
        stage: &str,
        latency_ms: u32,
        data_before: usize,
        data_after: usize,
        reduction_percent: u32,
    ) -> Result<()> {
        let mut metrics = self.stage_metrics.lock().unwrap();

        let stage_metric = metrics
            .entry(stage.to_string())
            .or_insert_with(|| StageMetrics {
                stage: stage.to_string(),
                total_queries: 0,
                total_latency_ms: 0,
                avg_latency_ms: 0,
                min_latency_ms: u32::MAX,
                max_latency_ms: 0,
                total_data_before: 0,
                total_data_after: 0,
                avg_reduction_percent: 0,
            });

        stage_metric.total_queries += 1;
        stage_metric.total_latency_ms += latency_ms as u64;
        stage_metric.avg_latency_ms = (stage_metric.total_latency_ms / stage_metric.total_queries) as u32;
        stage_metric.min_latency_ms = stage_metric.min_latency_ms.min(latency_ms);
        stage_metric.max_latency_ms = stage_metric.max_latency_ms.max(latency_ms);
        stage_metric.total_data_before += data_before as u64;
        stage_metric.total_data_after += data_after as u64;
        stage_metric.avg_reduction_percent = reduction_percent;

        // Update reduction metrics
        let mut reduction = self.reduction_metrics.lock().unwrap();
        match stage {
            "Stage1" => reduction.stage1_reductions.push(reduction_percent),
            "Stage2" => reduction.stage2_reductions.push(reduction_percent),
            "Stage3" => reduction.stage3_reductions.push(reduction_percent),
            _ => {}
        }

        Ok(())
    }

    /// Record cache hit
    pub fn record_cache_hit(&self) -> Result<()> {
        let mut reduction = self.reduction_metrics.lock().unwrap();
        reduction.cache_hits += 1;
        Ok(())
    }

    /// Record cache miss
    pub fn record_cache_miss(&self) -> Result<()> {
        let mut reduction = self.reduction_metrics.lock().unwrap();
        reduction.cache_misses += 1;
        Ok(())
    }

    /// Record fallback invocation
    pub fn record_fallback(&self) -> Result<()> {
        let mut reduction = self.reduction_metrics.lock().unwrap();
        reduction.fallback_invocations += 1;
        Ok(())
    }

    /// Get cache hit rate
    pub fn get_cache_hit_rate(&self) -> Result<f64> {
        let reduction = self.reduction_metrics.lock().unwrap();
        let total = reduction.cache_hits + reduction.cache_misses;

        let rate = if total > 0 {
            reduction.cache_hits as f64 / total as f64
        } else {
            0.0
        };

        Ok(rate)
    }

    /// Get current metrics
    pub fn get_metrics(&self) -> Result<PerformanceMetrics> {
        let stage_metrics = self.stage_metrics.lock().unwrap();

        let stage1 = stage_metrics
            .get("Stage1")
            .cloned()
            .unwrap_or_else(|| StageMetrics {
                stage: "Stage1".to_string(),
                total_queries: 0,
                total_latency_ms: 0,
                avg_latency_ms: 0,
                min_latency_ms: 0,
                max_latency_ms: 0,
                total_data_before: 0,
                total_data_after: 0,
                avg_reduction_percent: 0,
            });

        let stage2 = stage_metrics
            .get("Stage2")
            .cloned()
            .unwrap_or_else(|| StageMetrics {
                stage: "Stage2".to_string(),
                total_queries: 0,
                total_latency_ms: 0,
                avg_latency_ms: 0,
                min_latency_ms: 0,
                max_latency_ms: 0,
                total_data_before: 0,
                total_data_after: 0,
                avg_reduction_percent: 0,
            });

        let stage3 = stage_metrics
            .get("Stage3")
            .cloned()
            .unwrap_or_else(|| StageMetrics {
                stage: "Stage3".to_string(),
                total_queries: 0,
                total_latency_ms: 0,
                avg_latency_ms: 0,
                min_latency_ms: 0,
                max_latency_ms: 0,
                total_data_before: 0,
                total_data_after: 0,
                avg_reduction_percent: 0,
            });

        let combined_latency = stage1.avg_latency_ms + stage2.avg_latency_ms + stage3.avg_latency_ms;
        let combined_reduction = ((stage1.avg_reduction_percent as f64
            * stage2.avg_reduction_percent as f64
            * stage3.avg_reduction_percent as f64)
            / 1_000_000.0) as u32;

        Ok(PerformanceMetrics {
            stage1,
            stage2,
            stage3,
            combined_latency_ms: combined_latency,
            combined_reduction_percent: combined_reduction,
            total_queries: stage_metrics
                .values()
                .next()
                .map(|m| m.total_queries)
                .unwrap_or(0),
        })
    }

    /// Export metrics as Prometheus format
    pub fn export_prometheus(&self) -> Result<String> {
        let metrics = self.get_metrics()?;

        let mut output = String::new();
        output.push_str("# HELP pystreammcp_stage_latency_ms Stage latency in milliseconds\n");
        output.push_str("# TYPE pystreammcp_stage_latency_ms gauge\n");
        output.push_str(&format!(
            "pystreammcp_stage_latency_ms{{stage=\"stage1\"}} {}\n",
            metrics.stage1.avg_latency_ms
        ));
        output.push_str(&format!(
            "pystreammcp_stage_latency_ms{{stage=\"stage2\"}} {}\n",
            metrics.stage2.avg_latency_ms
        ));
        output.push_str(&format!(
            "pystreammcp_stage_latency_ms{{stage=\"stage3\"}} {}\n",
            metrics.stage3.avg_latency_ms
        ));

        output.push_str("\n# HELP pystreammcp_data_reduction_percent Data reduction percentage\n");
        output.push_str("# TYPE pystreammcp_data_reduction_percent gauge\n");
        output.push_str(&format!(
            "pystreammcp_data_reduction_percent{{stage=\"stage1\"}} {}\n",
            metrics.stage1.avg_reduction_percent
        ));
        output.push_str(&format!(
            "pystreammcp_data_reduction_percent{{stage=\"stage2\"}} {}\n",
            metrics.stage2.avg_reduction_percent
        ));
        output.push_str(&format!(
            "pystreammcp_combined_latency_ms {}\n",
            metrics.combined_latency_ms
        ));

        Ok(output)
    }

    /// Export metrics as JSON
    pub fn export_json(&self) -> Result<String> {
        let metrics = self.get_metrics()?;
        let json = serde_json::to_string(&metrics)?;
        Ok(json)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_metrics_collection() {
        let config = MetricsConfig {
            enabled: true,
            export_format: "prometheus".to_string(),
        };
        let collector = MetricsCollector::new(config).unwrap();

        collector.record_stage_performance("Stage1", 45, 1000, 150, 85).unwrap();
        collector.record_stage_performance("Stage2", 18, 150, 30, 80).unwrap();
        collector.record_stage_performance("Stage3", 25, 30, 25, 17).unwrap();

        let metrics = collector.get_metrics().unwrap();
        assert!(metrics.stage1.total_queries > 0);
        assert!(metrics.combined_latency_ms > 0);
    }

    #[test]
    fn test_cache_metrics() {
        let config = MetricsConfig {
            enabled: true,
            export_format: "json".to_string(),
        };
        let collector = MetricsCollector::new(config).unwrap();

        collector.record_cache_hit().unwrap();
        collector.record_cache_hit().unwrap();
        collector.record_cache_miss().unwrap();

        let hit_rate = collector.get_cache_hit_rate().unwrap();
        assert!(hit_rate > 0.6 && hit_rate < 0.7);
    }
}
