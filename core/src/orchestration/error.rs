use std::fmt;
use serde::{Deserialize, Serialize};

/// Comprehensive error type for orchestration layer
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum OrchestrationError {
    /// Intent classification failed
    IntentClassification {
        query: String,
        reason: String,
    },
    /// No servers found for intent
    NoServersFound {
        intent: String,
        available_intents: Vec<String>,
    },
    /// Server registration failed
    ServerRegistrationFailed {
        server_id: String,
        reason: String,
    },
    /// Configuration is invalid
    InvalidConfiguration {
        component: String,
        issue: String,
    },
    /// Tool selection failed
    SelectionFailed {
        intent: String,
        constraints_violated: Vec<String>,
    },
    /// Performance tracking error
    PerformanceTracking {
        server_id: String,
        reason: String,
    },
    /// Validation failed
    ValidationFailed {
        field: String,
        value: String,
        reason: String,
    },
    /// Input constraints violated
    ConstraintViolation {
        constraint: String,
        actual: String,
        expected: String,
    },
    /// Internal state corruption
    InternalError {
        component: String,
        message: String,
    },
    /// Capability not found
    CapabilityNotFound {
        capability: String,
        available: Vec<String>,
    },
    /// Entity not found
    EntityNotFound {
        entity_type: String,
        entity_id: String,
    },
}

impl fmt::Display for OrchestrationError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            OrchestrationError::IntentClassification { query, reason } => {
                write!(f, "Failed to classify intent for query '{}': {}", query, reason)
            }
            OrchestrationError::NoServersFound { intent, available_intents } => {
                write!(f, "No servers found for intent '{}'. Available: {:?}", intent, available_intents)
            }
            OrchestrationError::ServerRegistrationFailed { server_id, reason } => {
                write!(f, "Failed to register server '{}': {}", server_id, reason)
            }
            OrchestrationError::InvalidConfiguration { component, issue } => {
                write!(f, "Invalid configuration for {}: {}", component, issue)
            }
            OrchestrationError::SelectionFailed { intent, constraints_violated } => {
                write!(f, "Tool selection failed for intent '{}'. Constraints violated: {:?}", intent, constraints_violated)
            }
            OrchestrationError::PerformanceTracking { server_id, reason } => {
                write!(f, "Failed to track performance for server '{}': {}", server_id, reason)
            }
            OrchestrationError::ValidationFailed { field, value, reason } => {
                write!(f, "Validation failed for field '{}' with value '{}': {}", field, value, reason)
            }
            OrchestrationError::ConstraintViolation { constraint, actual, expected } => {
                write!(f, "Constraint '{}' violated. Expected: {}, got: {}", constraint, expected, actual)
            }
            OrchestrationError::InternalError { component, message } => {
                write!(f, "Internal error in {}: {}", component, message)
            }
            OrchestrationError::CapabilityNotFound { capability, available } => {
                write!(f, "Capability '{}' not found. Available: {:?}", capability, available)
            }
            OrchestrationError::EntityNotFound { entity_type, entity_id } => {
                write!(f, "{} entity not found: {}", entity_type, entity_id)
            }
        }
    }
}

impl std::error::Error for OrchestrationError {}

/// Result type for orchestration operations
pub type Result<T> = std::result::Result<T, OrchestrationError>;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_error_display() {
        let err = OrchestrationError::NoServersFound {
            intent: "Research".to_string(),
            available_intents: vec!["Database".to_string()],
        };
        let msg = err.to_string();
        assert!(msg.contains("Research"));
        assert!(msg.contains("Database"));
    }

    #[test]
    fn test_error_serialization() {
        let err = OrchestrationError::ValidationFailed {
            field: "score".to_string(),
            value: "1.5".to_string(),
            reason: "Score must be 0.0-1.0".to_string(),
        };
        let json = serde_json::to_string(&err).unwrap();
        assert!(json.contains("score"));
    }
}
