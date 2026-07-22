// Stage 3: Quality Gates & Validation
// Validates content at pre-retrieval and post-retrieval stages

pub mod validators;
pub mod confidence;
pub mod fallback;
pub mod policies;

pub use validators::{QualityValidator, ValidationCheck, ValidationResult, CheckType};
pub use confidence::{ConfidenceScore, ConfidenceCalculator};
pub use fallback::{FallbackChain, FallbackStrategy, FallbackResult};
pub use policies::{QualityPolicy, PolicyEnforcer, SLAConfig};

use crate::Result;
use serde::{Deserialize, Serialize};

/// Quality Gates Engine - Stage 3
///
/// Validates content at every stage:
/// 1. Pre-retrieval: Validate source metadata
/// 2. Post-retrieval: Validate retrieved content quality
/// 3. Final: Ensure quality SLAs met
///
/// Integrates StatGuardian for data quality contracts.
pub struct QualityGatesEngine {
    validator: QualityValidator,
    confidence_calc: ConfidenceCalculator,
    fallback_chain: FallbackChain,
    policy_enforcer: PolicyEnforcer,
}

impl QualityGatesEngine {
    /// Create new quality gates engine
    pub fn new(config: QualityGatesConfig) -> Result<Self> {
        let validator = QualityValidator::new()?;
        let confidence_calc = ConfidenceCalculator::new(config.confidence_config)?;
        let fallback_chain = FallbackChain::new(config.fallback_strategies)?;
        let policy_enforcer = PolicyEnforcer::new(config.quality_policy)?;

        Ok(Self {
            validator,
            confidence_calc,
            fallback_chain,
            policy_enforcer,
        })
    }

    /// Validate source before retrieval (metadata validation)
    pub async fn validate_source(
        &self,
        source_id: &str,
        source_type: &str,
    ) -> Result<SourceValidationResult> {
        let checks = self
            .validator
            .validate_source_metadata(source_id, source_type)
            .await?;

        let confidence = self.confidence_calc.calculate_source_confidence(&checks)?;
        let passed = checks.iter().all(|c| c.passed);

        Ok(SourceValidationResult {
            source_id: source_id.to_string(),
            passed,
            confidence,
            checks,
        })
    }

    /// Validate content after retrieval (quality validation)
    pub async fn validate_content(
        &self,
        content: &str,
        expected_quality: f64,
    ) -> Result<ContentValidationResult> {
        let checks = self
            .validator
            .validate_retrieved_content(content)
            .await?;

        let confidence = self
            .confidence_calc
            .calculate_content_confidence(&checks)?;
        let quality_score = self
            .confidence_calc
            .calculate_quality_score(&checks)?;
        let passed = quality_score >= expected_quality;

        Ok(ContentValidationResult {
            passed,
            confidence,
            quality_score,
            checks,
        })
    }

    /// Check if content meets SLA
    pub fn check_sla(
        &self,
        quality_score: f64,
        latency_ms: u32,
    ) -> Result<SLACheckResult> {
        let sla_result = self.policy_enforcer.check_sla(quality_score, latency_ms)?;

        Ok(sla_result)
    }

    /// Get fallback recommendation if validation fails
    pub async fn get_fallback_recommendation(
        &self,
        failed_source: &str,
    ) -> Result<FallbackResult> {
        self.fallback_chain.recommend_fallback(failed_source).await
    }

    /// Validate entire context window quality
    pub async fn validate_context_window(
        &self,
        items: Vec<ContextItem>,
        budget: u32,
    ) -> Result<ContextWindowValidation> {
        let mut total_quality = 0.0;
        let mut total_confidence = 0.0;
        let mut passed_items = 0;
        let mut validation_details = vec![];

        for (idx, item) in items.iter().enumerate() {
            let checks = self.validator.validate_item(item).await?;
            let confidence = self.confidence_calc.calculate_content_confidence(&checks)?;
            let quality = self.confidence_calc.calculate_quality_score(&checks)?;

            total_quality += quality;
            total_confidence += confidence;
            if quality > 0.7 {
                passed_items += 1;
            }

            validation_details.push(ItemValidationDetail {
                index: idx,
                quality: quality,
                confidence: confidence,
                passed: quality > 0.7,
            });
        }

        let avg_quality = if !items.is_empty() {
            total_quality / items.len() as f64
        } else {
            0.0
        };

        let avg_confidence = if !items.is_empty() {
            total_confidence / items.len() as f64
        } else {
            0.0
        };

        let passed = avg_quality > 0.75 && passed_items as f64 / items.len() as f64 > 0.8;

        Ok(ContextWindowValidation {
            total_items: items.len(),
            passed_items,
            avg_quality,
            avg_confidence,
            overall_passed: passed,
            validation_details,
        })
    }
}

/// Configuration for quality gates
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QualityGatesConfig {
    pub confidence_config: ConfidenceConfig,
    pub fallback_strategies: Vec<FallbackStrategy>,
    pub quality_policy: QualityPolicy,
}

impl Default for QualityGatesConfig {
    fn default() -> Self {
        Self {
            confidence_config: ConfidenceConfig::default(),
            fallback_strategies: vec![
                FallbackStrategy::RetryWithBackoff { max_retries: 3 },
                FallbackStrategy::UseAlternativeSource,
                FallbackStrategy::DegradeGracefully,
            ],
            quality_policy: QualityPolicy::default(),
        }
    }
}

/// Confidence configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConfidenceConfig {
    /// Minimum confidence threshold (0-1)
    pub min_confidence: f64,
    /// Weights for different factors
    pub relevance_weight: f64,
    pub freshness_weight: f64,
    pub completeness_weight: f64,
}

impl Default for ConfidenceConfig {
    fn default() -> Self {
        Self {
            min_confidence: 0.7,
            relevance_weight: 0.4,
            freshness_weight: 0.3,
            completeness_weight: 0.3,
        }
    }
}

/// Source validation result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SourceValidationResult {
    pub source_id: String,
    pub passed: bool,
    pub confidence: f64,
    pub checks: Vec<ValidationCheck>,
}

/// Content validation result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ContentValidationResult {
    pub passed: bool,
    pub confidence: f64,
    pub quality_score: f64,
    pub checks: Vec<ValidationCheck>,
}

/// Context item for validation
#[derive(Debug, Clone)]
pub struct ContextItem {
    pub id: String,
    pub content: String,
    pub source: String,
    pub tokens: u32,
}

/// Context window validation result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ContextWindowValidation {
    pub total_items: usize,
    pub passed_items: usize,
    pub avg_quality: f64,
    pub avg_confidence: f64,
    pub overall_passed: bool,
    pub validation_details: Vec<ItemValidationDetail>,
}

/// Item validation detail
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ItemValidationDetail {
    pub index: usize,
    pub quality: f64,
    pub confidence: f64,
    pub passed: bool,
}

/// SLA check result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SLACheckResult {
    pub quality_met: bool,
    pub latency_met: bool,
    pub overall_met: bool,
    pub violations: Vec<String>,
}
