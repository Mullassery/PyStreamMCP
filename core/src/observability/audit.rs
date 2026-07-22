// Audit Trail - Stage 4
// Complete audit trail recording for compliance and debugging

use crate::Result;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::{Arc, Mutex};

/// Decision audit trail
pub struct DecisionAuditTrail {
    config: AuditConfig,
    decisions: Arc<Mutex<Vec<DecisionRecord>>>,
}

#[derive(Debug, Clone)]
pub struct AuditConfig {
    pub enabled: bool,
    pub retention_days: u32,
    pub include_decisions: bool,
    pub include_performance: bool,
}

/// Single decision record
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DecisionRecord {
    pub trace_id: String,
    pub stage: String,
    pub decision_type: String,
    pub subject: String,
    pub score: f64,
    pub reason: String,
    pub timestamp: i64,
}

impl DecisionAuditTrail {
    /// Create new audit trail
    pub fn new(config: AuditConfig) -> Result<Self> {
        Ok(Self {
            config,
            decisions: Arc::new(Mutex::new(Vec::new())),
        })
    }

    /// Record a decision
    pub fn record_decision(&self, decision: DecisionRecord) -> Result<()> {
        if !self.config.enabled {
            return Ok(());
        }

        let mut decisions = self.decisions.lock().unwrap();
        decisions.push(decision);

        // Keep only recent decisions (based on retention)
        let cutoff_timestamp = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs() as i64
            - (self.config.retention_days as i64 * 86400);

        decisions.retain(|d| d.timestamp > cutoff_timestamp);

        Ok(())
    }

    /// Get all decisions for a trace
    pub fn get_decisions_for_trace(&self, trace_id: &str) -> Result<Vec<DecisionRecord>> {
        let decisions = self.decisions.lock().unwrap();
        let trace_decisions: Vec<DecisionRecord> = decisions
            .iter()
            .filter(|d| d.trace_id == trace_id)
            .cloned()
            .collect();

        Ok(trace_decisions)
    }

    /// Get decisions by stage
    pub fn get_decisions_by_stage(&self, stage: &str) -> Result<Vec<DecisionRecord>> {
        let decisions = self.decisions.lock().unwrap();
        let stage_decisions: Vec<DecisionRecord> = decisions
            .iter()
            .filter(|d| d.stage == stage)
            .cloned()
            .collect();

        Ok(stage_decisions)
    }

    /// Generate audit report
    pub fn generate_report(&self, trace_id: &str) -> Result<AuditReport> {
        let decisions = self.get_decisions_for_trace(trace_id)?;

        let mut stage_counts: HashMap<String, usize> = HashMap::new();
        let mut avg_scores: HashMap<String, f64> = HashMap::new();

        for decision in &decisions {
            *stage_counts.entry(decision.stage.clone()).or_insert(0) += 1;
            let entry = avg_scores.entry(decision.stage.clone()).or_insert(0.0);
            *entry += decision.score;
        }

        // Calculate averages
        for (stage, total) in &stage_counts {
            if let Some(sum) = avg_scores.get_mut(stage) {
                *sum /= *total as f64;
            }
        }

        Ok(AuditReport {
            trace_id: trace_id.to_string(),
            total_decisions: decisions.len(),
            decisions_by_stage: stage_counts,
            avg_scores_by_stage: avg_scores,
            decisions,
        })
    }

    /// Get total decision count
    pub fn get_total_decisions(&self) -> Result<usize> {
        let decisions = self.decisions.lock().unwrap();
        Ok(decisions.len())
    }
}

/// Audit report for a query
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuditReport {
    pub trace_id: String,
    pub total_decisions: usize,
    pub decisions_by_stage: HashMap<String, usize>,
    pub avg_scores_by_stage: HashMap<String, f64>,
    pub decisions: Vec<DecisionRecord>,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_record_decision() {
        let config = AuditConfig {
            enabled: true,
            retention_days: 90,
            include_decisions: true,
            include_performance: true,
        };
        let trail = DecisionAuditTrail::new(config).unwrap();

        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs() as i64;

        trail.record_decision(DecisionRecord {
            trace_id: "trace-123".to_string(),
            stage: "Stage1".to_string(),
            decision_type: "source_selection".to_string(),
            subject: "example.com".to_string(),
            score: 0.95,
            reason: "High authority".to_string(),
            timestamp: now,
        })
        .unwrap();

        let decisions = trail.get_decisions_for_trace("trace-123").unwrap();
        assert_eq!(decisions.len(), 1);
    }

    #[test]
    fn test_generate_report() {
        let config = AuditConfig {
            enabled: true,
            retention_days: 90,
            include_decisions: true,
            include_performance: true,
        };
        let trail = DecisionAuditTrail::new(config).unwrap();

        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs() as i64;

        trail.record_decision(DecisionRecord {
            trace_id: "trace-123".to_string(),
            stage: "Stage1".to_string(),
            decision_type: "source_selection".to_string(),
            subject: "example.com".to_string(),
            score: 0.95,
            reason: "High authority".to_string(),
            timestamp: now,
        })
        .unwrap();

        let report = trail.generate_report("trace-123").unwrap();
        assert_eq!(report.total_decisions, 1);
        assert!(report.decisions_by_stage.contains_key("Stage1"));
    }
}
