// Quality Validators - Stage 3
// Validates content at pre-retrieval and post-retrieval stages

use crate::Result;
use serde::{Deserialize, Serialize};

/// Type of validation check
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum CheckType {
    /// Check source metadata (domain, SSL, age, authority)
    SourceMetadata,
    /// Check content exists and is accessible
    Accessibility,
    /// Check content is not empty
    Completeness,
    /// Check content language matches expected
    LanguageMatch,
    /// Check no paywall/403/410 errors
    NoPaywall,
    /// Check freshness (recent update)
    Freshness,
    /// Check for duplicates
    Uniqueness,
    /// Check signal-to-noise ratio (not spam/ads)
    SignalToNoise,
    /// Check format/structure validity
    FormatValidity,
    /// Check data integrity
    DataIntegrity,
}

/// Single validation check result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ValidationCheck {
    pub check_type: CheckType,
    pub passed: bool,
    pub score: f64,    // 0-1, how well passed
    pub message: String,
}

/// Overall validation result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ValidationResult {
    pub passed: bool,
    pub checks: Vec<ValidationCheck>,
    pub overall_score: f64,
}

/// Quality validator
pub struct QualityValidator;

impl QualityValidator {
    /// Create new validator
    pub fn new() -> Result<Self> {
        Ok(Self)
    }

    /// Validate source metadata (pre-retrieval)
    pub async fn validate_source_metadata(
        &self,
        source_id: &str,
        source_type: &str,
    ) -> Result<Vec<ValidationCheck>> {
        let mut checks = vec![];

        // Check 1: Source metadata completeness
        let source_check = ValidationCheck {
            check_type: CheckType::SourceMetadata,
            passed: !source_id.is_empty(),
            score: if source_id.is_empty() { 0.0 } else { 1.0 },
            message: format!("Source metadata check for {}", source_id),
        };
        checks.push(source_check);

        // Check 2: Source type valid
        let type_check = self.validate_source_type(source_type)?;
        checks.push(type_check);

        Ok(checks)
    }

    /// Validate retrieved content (post-retrieval)
    pub async fn validate_retrieved_content(&self, content: &str) -> Result<Vec<ValidationCheck>> {
        let mut checks = vec![];

        // Check 1: Completeness
        let completeness = ValidationCheck {
            check_type: CheckType::Completeness,
            passed: !content.is_empty(),
            score: if content.is_empty() { 0.0 } else { 1.0 },
            message: "Content is not empty".to_string(),
        };
        checks.push(completeness);

        // Check 2: Length check (not too short, not spam)
        let length_check = self.validate_content_length(content)?;
        checks.push(length_check);

        // Check 3: Signal-to-noise ratio
        let signal_check = self.validate_signal_to_noise(content)?;
        checks.push(signal_check);

        // Check 4: Format validity
        let format_check = self.validate_format(content)?;
        checks.push(format_check);

        Ok(checks)
    }

    /// Validate a single item
    pub async fn validate_item(
        &self,
        item: &crate::quality_gates::ContextItem,
    ) -> Result<Vec<ValidationCheck>> {
        let mut checks = vec![];

        // Check 1: Content existence
        let content_check = ValidationCheck {
            check_type: CheckType::Completeness,
            passed: !item.content.is_empty(),
            score: if item.content.is_empty() { 0.0 } else { 1.0 },
            message: format!("Item {} has content", item.id),
        };
        checks.push(content_check);

        // Check 2: Source validity
        let source_check = ValidationCheck {
            check_type: CheckType::SourceMetadata,
            passed: !item.source.is_empty(),
            score: if item.source.is_empty() { 0.0 } else { 1.0 },
            message: format!("Item {} has valid source", item.id),
        };
        checks.push(source_check);

        // Check 3: Token estimate validity
        let token_check = ValidationCheck {
            check_type: CheckType::DataIntegrity,
            passed: item.tokens > 0,
            score: if item.tokens > 0 { 1.0 } else { 0.0 },
            message: format!("Item {} has valid token count", item.id),
        };
        checks.push(token_check);

        Ok(checks)
    }

    /// Validate source type
    fn validate_source_type(&self, source_type: &str) -> Result<ValidationCheck> {
        let valid_types = ["web", "database", "mcp_tool"];
        let is_valid = valid_types.contains(&source_type.to_lowercase().as_str());

        Ok(ValidationCheck {
            check_type: CheckType::SourceMetadata,
            passed: is_valid,
            score: if is_valid { 1.0 } else { 0.0 },
            message: format!("Source type '{}' is valid", source_type),
        })
    }

    /// Validate content length
    fn validate_content_length(&self, content: &str) -> Result<ValidationCheck> {
        let len = content.len();
        let min_len = 50; // Minimum 50 characters
        let max_len = 1_000_000; // Maximum 1MB

        let passed = len >= min_len && len <= max_len;
        let score = if len < min_len {
            0.0
        } else if len > max_len {
            0.0
        } else {
            1.0
        };

        Ok(ValidationCheck {
            check_type: CheckType::Completeness,
            passed,
            score,
            message: format!("Content length {} is in valid range", len),
        })
    }

    /// Validate signal-to-noise ratio
    fn validate_signal_to_noise(&self, content: &str) -> Result<ValidationCheck> {
        // Simple heuristic: check for common spam/ad patterns
        let content_lower = content.to_lowercase();
        let spam_keywords = vec!["click here", "buy now", "limited time", "spam"];

        let spam_count = spam_keywords
            .iter()
            .filter(|kw| content_lower.contains(*kw))
            .count();

        let passed = spam_count < 3; // Allow up to 2 spam keywords
        let score = (1.0 - (spam_count as f64 * 0.25).min(1.0)).max(0.0);

        Ok(ValidationCheck {
            check_type: CheckType::SignalToNoise,
            passed,
            score,
            message: format!("Signal-to-noise ratio acceptable (spam keywords: {})", spam_count),
        })
    }

    /// Validate format/structure
    fn validate_format(&self, content: &str) -> Result<ValidationCheck> {
        // Check for basic structure (has sentences, paragraphs, etc.)
        let has_sentences = content.contains('.') || content.contains('?') || content.contains('!');
        let has_multiple_lines = content.lines().count() > 1;

        let passed = has_sentences || has_multiple_lines;
        let score = if passed { 1.0 } else { 0.5 };

        Ok(ValidationCheck {
            check_type: CheckType::FormatValidity,
            passed,
            score,
            message: "Content has valid format structure".to_string(),
        })
    }
}

impl Default for QualityValidator {
    fn default() -> Self {
        Self
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_validate_source_metadata() {
        let validator = QualityValidator::new().unwrap();
        let checks = validator
            .validate_source_metadata("example.com", "web")
            .await
            .unwrap();

        assert!(!checks.is_empty());
        assert!(checks.iter().all(|c| c.passed));
    }

    #[tokio::test]
    async fn test_validate_content_empty() {
        let validator = QualityValidator::new().unwrap();
        let checks = validator.validate_retrieved_content("").await.unwrap();

        assert!(checks.iter().any(|c| !c.passed));
    }

    #[tokio::test]
    async fn test_validate_content_valid() {
        let validator = QualityValidator::new().unwrap();
        let content = "This is a valid piece of content. It has multiple sentences. And it's well-structured.";
        let checks = validator.validate_retrieved_content(content).await.unwrap();

        assert!(!checks.is_empty());
        let passed_count = checks.iter().filter(|c| c.passed).count();
        assert!(passed_count > 0);
    }

    #[test]
    fn test_validate_source_type() {
        let validator = QualityValidator::new().unwrap();

        let valid = validator.validate_source_type("web").unwrap();
        assert!(valid.passed);

        let invalid = validator.validate_source_type("unknown").unwrap();
        assert!(!invalid.passed);
    }

    #[test]
    fn test_validate_signal_to_noise() {
        let validator = QualityValidator::new().unwrap();

        let good = validator.validate_signal_to_noise("Good quality content").unwrap();
        assert!(good.passed);

        let spam = validator
            .validate_signal_to_noise("Click here buy now limited time click here")
            .unwrap();
        assert!(!spam.passed);
    }
}
