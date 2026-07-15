use serde::{Deserialize, Serialize};

/// Integration with StatGuardian for context quality validation.
///
/// PyStreamMCP validates that discovered context has passed
/// StatGuardian quality gates before including in queries.

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ValidationGate {
    pub dataset_id: String,
    pub block_on_failure: bool,
    pub max_staleness_seconds: Option<u64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ValidationStatus {
    Valid,
    Invalid { reason: String },
    Stale { last_validated: chrono::DateTime<chrono::Utc> },
    Unknown,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ValidationResult {
    pub dataset_id: String,
    pub status: ValidationStatus,
    pub timestamp: chrono::DateTime<chrono::Utc>,
    pub quality_score: Option<f32>,
    pub errors: Vec<String>,
}

impl ValidationGate {
    pub fn new(dataset_id: impl Into<String>) -> Self {
        ValidationGate {
            dataset_id: dataset_id.into(),
            block_on_failure: true,
            max_staleness_seconds: Some(3600),
        }
    }

    pub fn block_on_failure(mut self, block: bool) -> Self {
        self.block_on_failure = block;
        self
    }

    pub fn allow_stale_for(mut self, seconds: u64) -> Self {
        self.max_staleness_seconds = Some(seconds);
        self
    }
}

impl ValidationResult {
    pub fn is_valid(&self) -> bool {
        matches!(self.status, ValidationStatus::Valid)
    }

    pub fn is_usable(&self, max_staleness: Option<u64>) -> bool {
        match &self.status {
            ValidationStatus::Valid => true,
            ValidationStatus::Stale { last_validated } => {
                if let Some(max_stale) = max_staleness {
                    let age = chrono::Utc::now()
                        .signed_duration_since(*last_validated)
                        .num_seconds() as u64;
                    age <= max_stale
                } else {
                    false
                }
            }
            _ => false,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_validation_gate_creation() {
        let gate = ValidationGate::new("dataset_123");
        assert_eq!(gate.dataset_id, "dataset_123");
        assert!(gate.block_on_failure);
    }

    #[test]
    fn test_validation_result_valid() {
        let result = ValidationResult {
            dataset_id: "d1".to_string(),
            status: ValidationStatus::Valid,
            timestamp: chrono::Utc::now(),
            quality_score: Some(0.95),
            errors: Vec::new(),
        };
        assert!(result.is_valid());
    }
}
