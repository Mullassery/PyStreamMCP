use crate::orchestration::error::{OrchestrationError, Result};
use crate::orchestration::traits::Validatable;

/// Input validation configuration
#[derive(Debug, Clone)]
pub struct ValidationConfig {
    pub strict_mode: bool,
    pub max_string_length: usize,
    pub max_query_length: usize,
    pub allow_empty_capabilities: bool,
}

impl Default for ValidationConfig {
    fn default() -> Self {
        Self {
            strict_mode: true,
            max_string_length: 256,
            max_query_length: 2048,
            allow_empty_capabilities: false,
        }
    }
}

/// Validates all inputs to orchestration layer
pub struct InputValidator {
    config: ValidationConfig,
}

impl InputValidator {
    pub fn new(config: ValidationConfig) -> Self {
        Self { config }
    }

    /// Validate a query string
    pub fn validate_query(&self, query: &str) -> Result<()> {
        if query.is_empty() {
            return Err(OrchestrationError::ValidationFailed {
                field: "query".to_string(),
                value: "".to_string(),
                reason: "Query cannot be empty".to_string(),
            });
        }

        if query.len() > self.config.max_query_length {
            return Err(OrchestrationError::ValidationFailed {
                field: "query".to_string(),
                value: query.to_string(),
                reason: format!("Query exceeds max length ({})", self.config.max_query_length),
            });
        }

        // Check for invalid characters
        if query.contains('\0') {
            return Err(OrchestrationError::ValidationFailed {
                field: "query".to_string(),
                value: query.to_string(),
                reason: "Query contains null bytes".to_string(),
            });
        }

        Ok(())
    }

    /// Validate a server ID
    pub fn validate_server_id(&self, server_id: &str) -> Result<()> {
        if server_id.is_empty() {
            return Err(OrchestrationError::ValidationFailed {
                field: "server_id".to_string(),
                value: "".to_string(),
                reason: "Server ID cannot be empty".to_string(),
            });
        }

        if server_id.len() > self.config.max_string_length {
            return Err(OrchestrationError::ValidationFailed {
                field: "server_id".to_string(),
                value: server_id.to_string(),
                reason: format!("Server ID exceeds max length ({})", self.config.max_string_length),
            });
        }

        // Only alphanumeric, underscore, dash
        if !server_id.chars().all(|c| c.is_alphanumeric() || c == '_' || c == '-') {
            return Err(OrchestrationError::ValidationFailed {
                field: "server_id".to_string(),
                value: server_id.to_string(),
                reason: "Server ID must contain only alphanumeric characters, underscores, and dashes".to_string(),
            });
        }

        Ok(())
    }

    /// Validate a capability name
    pub fn validate_capability_name(&self, name: &str) -> Result<()> {
        if name.is_empty() {
            return Err(OrchestrationError::ValidationFailed {
                field: "capability_name".to_string(),
                value: "".to_string(),
                reason: "Capability name cannot be empty".to_string(),
            });
        }

        if name.len() > self.config.max_string_length {
            return Err(OrchestrationError::ValidationFailed {
                field: "capability_name".to_string(),
                value: name.to_string(),
                reason: format!("Capability name exceeds max length ({})", self.config.max_string_length),
            });
        }

        Ok(())
    }

    /// Validate a score is in range
    pub fn validate_score(&self, value: f32) -> Result<()> {
        if value < 0.0 || value > 1.0 {
            return Err(OrchestrationError::ValidationFailed {
                field: "score".to_string(),
                value: value.to_string(),
                reason: "Score must be between 0.0 and 1.0".to_string(),
            });
        }
        Ok(())
    }

    /// Validate latency is non-negative
    pub fn validate_latency(&self, ms: f32) -> Result<()> {
        if ms < 0.0 {
            return Err(OrchestrationError::ValidationFailed {
                field: "latency".to_string(),
                value: ms.to_string(),
                reason: "Latency cannot be negative".to_string(),
            });
        }

        if ms > 1_000_000.0 {
            return Err(OrchestrationError::ValidationFailed {
                field: "latency".to_string(),
                value: ms.to_string(),
                reason: "Latency exceeds reasonable maximum (1M ms)".to_string(),
            });
        }

        Ok(())
    }

    /// Validate a collection of items
    pub fn validate_collection<T: Validatable>(&self, items: &[T], name: &str) -> Result<()> {
        if items.is_empty() && !self.config.allow_empty_capabilities && name == "capabilities" {
            return Err(OrchestrationError::ValidationFailed {
                field: name.to_string(),
                value: "".to_string(),
                reason: format!("{} cannot be empty", name),
            });
        }

        for (i, item) in items.iter().enumerate() {
            item.validate().map_err(|e| {
                OrchestrationError::ValidationFailed {
                    field: format!("{}[{}]", name, i),
                    value: "".to_string(),
                    reason: e.to_string(),
                }
            })?;
        }

        Ok(())
    }
}

impl Default for InputValidator {
    fn default() -> Self {
        Self::new(ValidationConfig::default())
    }
}

/// Batch validator for multiple items
pub struct BatchValidator {
    config: ValidationConfig,
    errors: Vec<String>,
}

impl BatchValidator {
    pub fn new(config: ValidationConfig) -> Self {
        Self {
            config,
            errors: Vec::new(),
        }
    }

    pub fn validate_item<T: Validatable>(&mut self, item: &T, name: &str) {
        if let Err(e) = item.validate() {
            self.errors.push(format!("{}: {}", name, e));
        }
    }

    pub fn has_errors(&self) -> bool {
        !self.errors.is_empty()
    }

    pub fn errors(&self) -> &[String] {
        &self.errors
    }

    pub fn finish(self) -> Result<()> {
        if self.has_errors() {
            return Err(OrchestrationError::ValidationFailed {
                field: "batch".to_string(),
                value: format!("{} errors", self.errors.len()),
                reason: format!("Validation errors: {:?}", self.errors),
            });
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_validate_query_valid() {
        let validator = InputValidator::default();
        assert!(validator.validate_query("find papers").is_ok());
    }

    #[test]
    fn test_validate_query_empty() {
        let validator = InputValidator::default();
        assert!(validator.validate_query("").is_err());
    }

    #[test]
    fn test_validate_query_too_long() {
        let validator = InputValidator::default();
        let long_query = "a".repeat(3000);
        assert!(validator.validate_query(&long_query).is_err());
    }

    #[test]
    fn test_validate_server_id_valid() {
        let validator = InputValidator::default();
        assert!(validator.validate_server_id("arxiv-mcp_v1").is_ok());
    }

    #[test]
    fn test_validate_server_id_invalid_chars() {
        let validator = InputValidator::default();
        assert!(validator.validate_server_id("arxiv@mcp").is_err());
    }

    #[test]
    fn test_validate_score_valid() {
        let validator = InputValidator::default();
        assert!(validator.validate_score(0.5).is_ok());
    }

    #[test]
    fn test_validate_score_invalid() {
        let validator = InputValidator::default();
        assert!(validator.validate_score(1.5).is_err());
        assert!(validator.validate_score(-0.1).is_err());
    }

    #[test]
    fn test_batch_validator() {
        let mut batch = BatchValidator::new(ValidationConfig::default());

        // Simulate validating items
        assert!(!batch.has_errors());

        let result = batch.finish();
        assert!(result.is_ok());
    }
}
