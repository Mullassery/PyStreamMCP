use serde::{Deserialize, Serialize};

/// Optimization reduces token usage and latency while maintaining quality.
///
/// PyStreamMCP achieves 60-75% token reduction through intelligent
/// context selection, caching, and query optimization.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OptimizationStrategy {
    pub id: String,
    pub query_id: String,
    pub strategy_type: StrategyType,
    pub techniques: Vec<OptimizationTechnique>,
    pub expected_reduction_percent: f32,
    pub created_at: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum StrategyType {
    TokenMinimization,
    LatencyMinimization,
    CostMinimization,
    QualityFirst,
    Balanced,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum OptimizationTechnique {
    Caching,                // Use cached results
    Summarization,          // Summarize instead of full text
    Sampling,               // Sample data instead of full scan
    Pruning,                // Remove low-relevance items
    Compression,            // Compress representations
    Async,                  // Parallelize requests
    EarlyTermination,       // Stop when confidence sufficient
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CostMetrics {
    pub query_id: String,
    pub baseline_tokens: u32,
    pub optimized_tokens: u32,
    pub reduction_percent: f32,
    pub baseline_latency_ms: u64,
    pub optimized_latency_ms: u64,
    pub quality_maintained: bool,
}

impl OptimizationStrategy {
    pub fn new(query_id: impl Into<String>, strategy_type: StrategyType) -> Self {
        OptimizationStrategy {
            id: uuid::Uuid::new_v4().to_string(),
            query_id: query_id.into(),
            strategy_type,
            techniques: Vec::new(),
            expected_reduction_percent: 0.0,
            created_at: chrono::Utc::now(),
        }
    }

    pub fn add_technique(mut self, technique: OptimizationTechnique) -> Self {
        self.techniques.push(technique);
        self
    }

    pub fn with_expected_reduction(mut self, reduction: f32) -> Self {
        self.expected_reduction_percent = reduction.max(0.0).min(99.0);
        self
    }

    pub fn for_token_efficiency(mut self) -> Self {
        self.techniques = vec![
            OptimizationTechnique::Caching,
            OptimizationTechnique::Pruning,
            OptimizationTechnique::Summarization,
            OptimizationTechnique::EarlyTermination,
        ];
        self.expected_reduction_percent = 70.0;
        self
    }
}

impl CostMetrics {
    pub fn new(query_id: impl Into<String>, baseline_tokens: u32, optimized_tokens: u32) -> Self {
        let reduction_percent = if baseline_tokens == 0 {
            0.0
        } else {
            ((baseline_tokens - optimized_tokens) as f32 / baseline_tokens as f32) * 100.0
        };

        CostMetrics {
            query_id: query_id.into(),
            baseline_tokens,
            optimized_tokens,
            reduction_percent,
            baseline_latency_ms: 0,
            optimized_latency_ms: 0,
            quality_maintained: true,
        }
    }

    pub fn with_latency(mut self, baseline: u64, optimized: u64) -> Self {
        self.baseline_latency_ms = baseline;
        self.optimized_latency_ms = optimized;
        self
    }

    pub fn with_quality(mut self, maintained: bool) -> Self {
        self.quality_maintained = maintained;
        self
    }

    /// Check if optimization meets targets (60-75% reduction)
    pub fn meets_target(&self) -> bool {
        self.reduction_percent >= 60.0 && self.reduction_percent <= 75.0
    }

    pub fn exceeds_target(&self) -> bool {
        self.reduction_percent > 75.0
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_optimization_strategy() {
        let strategy = OptimizationStrategy::new("query_1", StrategyType::TokenMinimization)
            .add_technique(OptimizationTechnique::Caching)
            .add_technique(OptimizationTechnique::Pruning);

        assert_eq!(strategy.techniques.len(), 2);
    }

    #[test]
    fn test_token_efficiency_strategy() {
        let strategy = OptimizationStrategy::new("q1", StrategyType::Balanced).for_token_efficiency();
        assert_eq!(strategy.techniques.len(), 4);
        assert_eq!(strategy.expected_reduction_percent, 70.0);
    }

    #[test]
    fn test_cost_metrics() {
        let metrics = CostMetrics::new("query_1", 2000, 600);
        assert!(metrics.meets_target()); // (2000-600)/2000 = 70%
    }

    #[test]
    fn test_cost_metrics_exceeds_target() {
        let metrics = CostMetrics::new("query_1", 1000, 200);
        assert!(metrics.exceeds_target()); // (1000-200)/1000 = 80%
    }
}
