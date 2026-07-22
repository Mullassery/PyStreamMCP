// Confidence Scoring - Stage 3
// Calculates confidence and quality scores from validation checks

use crate::quality_gates::validators::{CheckType, ValidationCheck};
use crate::Result;
use serde::{Deserialize, Serialize};

/// Confidence score (0-1)
#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialOrd, PartialEq)]
pub struct ConfidenceScore(pub f64);

impl ConfidenceScore {
    /// Create new confidence score
    pub fn new(value: f64) -> Self {
        Self(value.max(0.0).min(1.0))
    }

    /// Is this confidence acceptable (> threshold)?
    pub fn is_acceptable(&self, threshold: f64) -> bool {
        self.0 >= threshold
    }

    /// Get confidence level (Low/Medium/High/VeryHigh)
    pub fn level(&self) -> ConfidenceLevel {
        match self.0 {
            0.0..=0.33 => ConfidenceLevel::Low,
            0.34..=0.66 => ConfidenceLevel::Medium,
            0.67..=0.85 => ConfidenceLevel::High,
            _ => ConfidenceLevel::VeryHigh,
        }
    }
}

/// Confidence level categories
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum ConfidenceLevel {
    Low,
    Medium,
    High,
    VeryHigh,
}

impl std::fmt::Display for ConfidenceLevel {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ConfidenceLevel::Low => write!(f, "Low"),
            ConfidenceLevel::Medium => write!(f, "Medium"),
            ConfidenceLevel::High => write!(f, "High"),
            ConfidenceLevel::VeryHigh => write!(f, "VeryHigh"),
        }
    }
}

/// Confidence calculator
pub struct ConfidenceCalculator {
    config: ConfidenceConfig,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConfidenceConfig {
    pub min_confidence: f64,
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

impl ConfidenceCalculator {
    /// Create new confidence calculator
    pub fn new(config: ConfidenceConfig) -> Result<Self> {
        Ok(Self { config })
    }

    /// Calculate confidence from validation checks
    pub fn calculate_source_confidence(&self, checks: &[ValidationCheck]) -> Result<f64> {
        if checks.is_empty() {
            return Ok(0.5); // Unknown
        }

        // Weight checks by type
        let mut total_score = 0.0;
        let mut total_weight = 0.0;

        for check in checks {
            let weight = self.get_weight_for_check_type(check.check_type);
            total_score += check.score * weight;
            total_weight += weight;
        }

        let confidence = if total_weight > 0.0 {
            total_score / total_weight
        } else {
            0.5
        };

        Ok(confidence.max(0.0).min(1.0))
    }

    /// Calculate confidence for content
    pub fn calculate_content_confidence(&self, checks: &[ValidationCheck]) -> Result<f64> {
        if checks.is_empty() {
            return Ok(0.5);
        }

        // For content, weight completeness higher
        let mut total_score = 0.0;
        let mut total_weight = 0.0;

        for check in checks {
            let mut weight = self.get_weight_for_check_type(check.check_type);

            // Boost weight for critical checks
            match check.check_type {
                CheckType::Completeness => weight *= 1.5,
                CheckType::DataIntegrity => weight *= 1.3,
                CheckType::SignalToNoise => weight *= 1.2,
                _ => {}
            }

            total_score += check.score * weight;
            total_weight += weight;
        }

        let confidence = if total_weight > 0.0 {
            total_score / total_weight
        } else {
            0.5
        };

        Ok(confidence.max(0.0).min(1.0))
    }

    /// Calculate quality score from checks
    pub fn calculate_quality_score(&self, checks: &[ValidationCheck]) -> Result<f64> {
        if checks.is_empty() {
            return Ok(0.5);
        }

        let passed_count = checks.iter().filter(|c| c.passed).count();
        let pass_rate = passed_count as f64 / checks.len() as f64;

        // Quality = pass rate + average score weighted
        let avg_score: f64 = checks.iter().map(|c| c.score).sum::<f64>() / checks.len() as f64;

        let quality = (pass_rate * 0.6 + avg_score * 0.4).max(0.0).min(1.0);

        Ok(quality)
    }

    /// Get weight for check type
    fn get_weight_for_check_type(&self, check_type: CheckType) -> f64 {
        match check_type {
            CheckType::SourceMetadata => 0.2,
            CheckType::Accessibility => 0.15,
            CheckType::Completeness => 0.25,
            CheckType::LanguageMatch => 0.1,
            CheckType::NoPaywall => 0.15,
            CheckType::Freshness => 0.15,
            CheckType::Uniqueness => 0.1,
            CheckType::SignalToNoise => 0.15,
            CheckType::FormatValidity => 0.1,
            CheckType::DataIntegrity => 0.2,
        }
    }

    /// Estimate confidence based on context
    pub fn estimate_from_context(
        &self,
        relevance: f64,
        freshness: f64,
        completeness: f64,
    ) -> Result<ConfidenceScore> {
        let confidence = (relevance * self.config.relevance_weight
            + freshness * self.config.freshness_weight
            + completeness * self.config.completeness_weight)
            .max(0.0)
            .min(1.0);

        Ok(ConfidenceScore::new(confidence))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_confidence_score_bounds() {
        let score = ConfidenceScore::new(1.5);
        assert_eq!(score.0, 1.0); // Clamped to 1.0

        let score = ConfidenceScore::new(-0.5);
        assert_eq!(score.0, 0.0); // Clamped to 0.0
    }

    #[test]
    fn test_confidence_level() {
        assert_eq!(ConfidenceScore(0.2).level(), ConfidenceLevel::Low);
        assert_eq!(ConfidenceScore(0.5).level(), ConfidenceLevel::Medium);
        assert_eq!(ConfidenceScore(0.75).level(), ConfidenceLevel::High);
        assert_eq!(ConfidenceScore(0.9).level(), ConfidenceLevel::VeryHigh);
    }

    #[test]
    fn test_is_acceptable() {
        let score = ConfidenceScore(0.75);
        assert!(score.is_acceptable(0.7));
        assert!(!score.is_acceptable(0.8));
    }

    #[test]
    fn test_calculate_quality_score() {
        let config = ConfidenceConfig::default();
        let calc = ConfidenceCalculator::new(config).unwrap();

        let checks = vec![
            ValidationCheck {
                check_type: CheckType::Completeness,
                passed: true,
                score: 1.0,
                message: "test".to_string(),
            },
            ValidationCheck {
                check_type: CheckType::SignalToNoise,
                passed: true,
                score: 0.8,
                message: "test".to_string(),
            },
            ValidationCheck {
                check_type: CheckType::FormatValidity,
                passed: false,
                score: 0.5,
                message: "test".to_string(),
            },
        ];

        let quality = calc.calculate_quality_score(&checks).unwrap();
        assert!(quality > 0.5); // More passed than failed
        assert!(quality < 0.85); // Not perfect due to one failure
    }
}
