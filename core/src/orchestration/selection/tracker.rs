use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::time::{SystemTime, Duration};

/// Performance data for a single query
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QueryPerformance {
    pub query_id: String,
    pub server_id: String,
    pub query: String,
    pub success: bool,
    pub latency_ms: f32,
    pub cost_tokens: usize,
    pub relevance_score: Option<f32>,
    pub timestamp: SystemTime,
}

impl QueryPerformance {
    pub fn new(query_id: String, server_id: String, query: String) -> Self {
        Self {
            query_id,
            server_id,
            query,
            success: false,
            latency_ms: 0.0,
            cost_tokens: 0,
            relevance_score: None,
            timestamp: SystemTime::now(),
        }
    }

    pub fn with_result(
        mut self,
        success: bool,
        latency_ms: f32,
        cost_tokens: usize,
        relevance: Option<f32>,
    ) -> Self {
        self.success = success;
        self.latency_ms = latency_ms;
        self.cost_tokens = cost_tokens;
        self.relevance_score = relevance;
        self.timestamp = SystemTime::now();
        self
    }
}

/// Aggregated performance statistics
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PerformanceStats {
    pub total_queries: u32,
    pub successful_queries: u32,
    pub failed_queries: u32,
    pub avg_latency_ms: f32,
    pub p50_latency_ms: f32,
    pub p95_latency_ms: f32,
    pub p99_latency_ms: f32,
    pub avg_cost_tokens: f32,
    pub avg_relevance: Option<f32>,
    pub success_rate: f32,
}

impl PerformanceStats {
    pub fn from_queries(queries: &[QueryPerformance]) -> Self {
        if queries.is_empty() {
            return Self::default();
        }

        let total = queries.len() as u32;
        let successful = queries.iter().filter(|q| q.success).count() as u32;
        let failed = total - successful;

        let mut latencies: Vec<f32> = queries.iter().map(|q| q.latency_ms).collect();
        latencies.sort_by(|a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal));

        let avg_latency = latencies.iter().sum::<f32>() / latencies.len() as f32;
        let p50_idx = (latencies.len() / 2).saturating_sub(1);
        let p95_idx = ((latencies.len() * 95) / 100).saturating_sub(1);
        let p99_idx = ((latencies.len() * 99) / 100).saturating_sub(1);

        let p50 = latencies[p50_idx];
        let p95 = latencies[p95_idx];
        let p99 = latencies[p99_idx];

        let avg_cost = queries.iter().map(|q| q.cost_tokens as f32).sum::<f32>() / queries.len() as f32;
        let avg_relevance = if queries.iter().all(|q| q.relevance_score.is_some()) {
            Some(
                queries
                    .iter()
                    .filter_map(|q| q.relevance_score)
                    .sum::<f32>() / queries.len() as f32,
            )
        } else {
            None
        };

        let success_rate = successful as f32 / total as f32;

        Self {
            total_queries: total,
            successful_queries: successful,
            failed_queries: failed,
            avg_latency_ms: avg_latency,
            p50_latency_ms: p50,
            p95_latency_ms: p95,
            p99_latency_ms: p99,
            avg_cost_tokens: avg_cost,
            avg_relevance,
            success_rate,
        }
    }
}

impl Default for PerformanceStats {
    fn default() -> Self {
        Self {
            total_queries: 0,
            successful_queries: 0,
            failed_queries: 0,
            avg_latency_ms: 0.0,
            p50_latency_ms: 0.0,
            p95_latency_ms: 0.0,
            p99_latency_ms: 0.0,
            avg_cost_tokens: 0.0,
            avg_relevance: None,
            success_rate: 0.0,
        }
    }
}

/// Tracks performance of MCP servers over time
pub struct PerformanceTracker {
    queries: HashMap<String, Vec<QueryPerformance>>, // server_id -> queries
    time_window: Duration,
}

impl PerformanceTracker {
    pub fn new() -> Self {
        Self {
            queries: HashMap::new(),
            time_window: Duration::from_secs(86400), // 24 hours
        }
    }

    pub fn with_time_window(mut self, window: Duration) -> Self {
        self.time_window = window;
        self
    }

    /// Record a query performance
    pub fn record(&mut self, performance: QueryPerformance) {
        self.queries
            .entry(performance.server_id.clone())
            .or_insert_with(Vec::new)
            .push(performance);
    }

    /// Get performance for a server
    pub fn get_stats(&self, server_id: &str) -> PerformanceStats {
        let queries = self.get_recent_queries(server_id);
        PerformanceStats::from_queries(&queries)
    }

    /// Get recent queries (within time window)
    fn get_recent_queries(&self, server_id: &str) -> Vec<QueryPerformance> {
        let now = SystemTime::now();
        self.queries
            .get(server_id)
            .map(|queries| {
                queries
                    .iter()
                    .filter(|q| {
                        now.duration_since(q.timestamp)
                            .unwrap_or(Duration::from_secs(0))
                            < self.time_window
                    })
                    .cloned()
                    .collect()
            })
            .unwrap_or_default()
    }

    /// Get success rate for a server
    pub fn success_rate(&self, server_id: &str) -> f32 {
        let stats = self.get_stats(server_id);
        stats.success_rate
    }

    /// Get average latency
    pub fn avg_latency(&self, server_id: &str) -> f32 {
        let stats = self.get_stats(server_id);
        stats.avg_latency_ms
    }

    /// Get percentile latency
    pub fn percentile_latency(&self, server_id: &str, percentile: u32) -> Option<f32> {
        let stats = self.get_stats(server_id);
        match percentile {
            50 => Some(stats.p50_latency_ms),
            95 => Some(stats.p95_latency_ms),
            99 => Some(stats.p99_latency_ms),
            _ => None,
        }
    }

    /// Get all tracked servers
    pub fn tracked_servers(&self) -> Vec<String> {
        self.queries.keys().cloned().collect()
    }

    /// Clear old data
    pub fn cleanup(&mut self) {
        for queries in self.queries.values_mut() {
            let now = SystemTime::now();
            queries.retain(|q| {
                now.duration_since(q.timestamp)
                    .unwrap_or(Duration::from_secs(0))
                    < self.time_window
            });
        }
    }

    /// Get all queries for a server
    pub fn all_queries(&self, server_id: &str) -> Vec<QueryPerformance> {
        self.queries
            .get(server_id)
            .cloned()
            .unwrap_or_default()
    }

    /// Get query count
    pub fn query_count(&self, server_id: &str) -> usize {
        self.get_recent_queries(server_id).len()
    }
}

impl Default for PerformanceTracker {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_query_performance_new() {
        let perf = QueryPerformance::new(
            "q1".to_string(),
            "arxiv".to_string(),
            "find papers".to_string(),
        );

        assert_eq!(perf.query_id, "q1");
        assert!(!perf.success);
    }

    #[test]
    fn test_query_performance_with_result() {
        let perf = QueryPerformance::new(
            "q1".to_string(),
            "arxiv".to_string(),
            "find papers".to_string(),
        )
        .with_result(true, 150.0, 2000, Some(0.95));

        assert!(perf.success);
        assert_eq!(perf.latency_ms, 150.0);
        assert_eq!(perf.cost_tokens, 2000);
        assert_eq!(perf.relevance_score, Some(0.95));
    }

    #[test]
    fn test_performance_stats_from_queries() {
        let queries = vec![
            QueryPerformance::new("q1".to_string(), "arxiv".to_string(), "q".to_string())
                .with_result(true, 100.0, 1000, None),
            QueryPerformance::new("q2".to_string(), "arxiv".to_string(), "q".to_string())
                .with_result(true, 200.0, 1500, None),
            QueryPerformance::new("q3".to_string(), "arxiv".to_string(), "q".to_string())
                .with_result(false, 500.0, 2000, None),
        ];

        let stats = PerformanceStats::from_queries(&queries);
        assert_eq!(stats.total_queries, 3);
        assert_eq!(stats.successful_queries, 2);
        assert_eq!(stats.failed_queries, 1);
        assert!(stats.success_rate > 0.6);
    }

    #[test]
    fn test_performance_tracker_record() {
        let mut tracker = PerformanceTracker::new();
        let perf = QueryPerformance::new(
            "q1".to_string(),
            "arxiv".to_string(),
            "find papers".to_string(),
        )
        .with_result(true, 150.0, 2000, Some(0.95));

        tracker.record(perf);
        assert_eq!(tracker.tracked_servers().len(), 1);
    }

    #[test]
    fn test_performance_tracker_success_rate() {
        let mut tracker = PerformanceTracker::new();
        tracker.record(
            QueryPerformance::new("q1".to_string(), "arxiv".to_string(), "q".to_string())
                .with_result(true, 100.0, 1000, None),
        );
        tracker.record(
            QueryPerformance::new("q2".to_string(), "arxiv".to_string(), "q".to_string())
                .with_result(false, 500.0, 2000, None),
        );

        let rate = tracker.success_rate("arxiv");
        assert_eq!(rate, 0.5);
    }

    #[test]
    fn test_performance_tracker_avg_latency() {
        let mut tracker = PerformanceTracker::new();
        tracker.record(
            QueryPerformance::new("q1".to_string(), "arxiv".to_string(), "q".to_string())
                .with_result(true, 100.0, 1000, None),
        );
        tracker.record(
            QueryPerformance::new("q2".to_string(), "arxiv".to_string(), "q".to_string())
                .with_result(true, 200.0, 1500, None),
        );

        let latency = tracker.avg_latency("arxiv");
        assert_eq!(latency, 150.0);
    }
}
