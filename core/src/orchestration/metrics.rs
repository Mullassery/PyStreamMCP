use serde::{Deserialize, Serialize};
use super::error::{OrchestrationError, Result};
use super::traits::Validatable;

/// Normalized score (0.0-1.0)
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd, Serialize, Deserialize)]
pub struct Score(f32);

impl Score {
    pub const MIN: f32 = 0.0;
    pub const MAX: f32 = 1.0;

    pub fn new(value: f32) -> Result<Score> {
        if value < Self::MIN || value > Self::MAX {
            return Err(OrchestrationError::ValidationFailed {
                field: "score".to_string(),
                value: value.to_string(),
                reason: format!("Score must be {}-{}", Self::MIN, Self::MAX),
            });
        }
        Ok(Score(value))
    }

    pub fn unchecked(value: f32) -> Score {
        Score(value.max(Self::MIN).min(Self::MAX))
    }

    pub fn as_f32(self) -> f32 {
        self.0
    }

    pub fn as_percent(self) -> f32 {
        self.0 * 100.0
    }
}

impl From<Score> for f32 {
    fn from(score: Score) -> f32 {
        score.0
    }
}

impl Validatable for Score {
    fn validate(&self) -> Result<()> {
        if self.0 < Self::MIN || self.0 > Self::MAX {
            return Err(OrchestrationError::ValidationFailed {
                field: "score".to_string(),
                value: self.0.to_string(),
                reason: "Score out of range".to_string(),
            });
        }
        Ok(())
    }
}

/// Success rate (0.0-1.0)
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd, Serialize, Deserialize)]
pub struct SuccessRate(f32);

impl SuccessRate {
    pub fn new(rate: f32) -> Result<SuccessRate> {
        Score::new(rate)?;
        Ok(SuccessRate(rate))
    }

    pub fn as_f32(self) -> f32 {
        self.0
    }

    pub fn as_percent(self) -> f32 {
        self.0 * 100.0
    }

    pub fn is_high(&self, threshold: f32) -> bool {
        self.0 >= threshold
    }
}

impl Validatable for SuccessRate {
    fn validate(&self) -> Result<()> {
        Score::new(self.0)?;
        Ok(())
    }
}

/// Confidence measurement (0.0-1.0)
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd, Serialize, Deserialize)]
pub struct Confidence(f32);

impl Confidence {
    pub fn new(value: f32) -> Result<Confidence> {
        Score::new(value)?;
        Ok(Confidence(value))
    }

    pub fn as_f32(self) -> f32 {
        self.0
    }

    pub fn is_confident(&self, threshold: f32) -> bool {
        self.0 >= threshold
    }

    pub fn level(&self) -> ConfidenceLevel {
        match self.0 {
            v if v < 0.3 => ConfidenceLevel::Low,
            v if v < 0.6 => ConfidenceLevel::Medium,
            v if v < 0.85 => ConfidenceLevel::High,
            _ => ConfidenceLevel::VeryHigh,
        }
    }
}

impl Validatable for Confidence {
    fn validate(&self) -> Result<()> {
        Score::new(self.0)?;
        Ok(())
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
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
            ConfidenceLevel::VeryHigh => write!(f, "Very High"),
        }
    }
}

/// Latency in milliseconds (non-negative)
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd, Serialize, Deserialize)]
pub struct Latency(f32);

impl Latency {
    const MAX_MS: f32 = 1_000_000.0; // ~11 days

    pub fn new(ms: f32) -> Result<Latency> {
        if ms < 0.0 || ms > Self::MAX_MS {
            return Err(OrchestrationError::ValidationFailed {
                field: "latency".to_string(),
                value: ms.to_string(),
                reason: format!("Latency must be 0-{}", Self::MAX_MS),
            });
        }
        Ok(Latency(ms))
    }

    pub fn unchecked(ms: f32) -> Latency {
        Latency(ms.max(0.0))
    }

    pub fn as_ms(self) -> f32 {
        self.0
    }

    pub fn as_secs(self) -> f32 {
        self.0 / 1000.0
    }

    /// Score for latency (inverted: lower is better)
    pub fn score(&self) -> Score {
        let normalized = (1.0 - (self.0 / 1000.0).min(1.0)).max(0.0);
        Score::unchecked(normalized)
    }

    pub fn is_acceptable(&self, threshold_ms: f32) -> bool {
        self.0 <= threshold_ms
    }
}

impl Validatable for Latency {
    fn validate(&self) -> Result<()> {
        if self.0 < 0.0 || self.0 > Self::MAX_MS {
            return Err(OrchestrationError::ValidationFailed {
                field: "latency".to_string(),
                value: self.0.to_string(),
                reason: "Latency out of range".to_string(),
            });
        }
        Ok(())
    }
}

/// Cost in tokens (non-negative)
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
pub struct Cost(usize);

impl Cost {
    pub fn new(tokens: usize) -> Result<Cost> {
        Ok(Cost(tokens))
    }

    pub fn as_tokens(self) -> usize {
        self.0
    }

    pub fn is_within_budget(&self, budget: usize) -> bool {
        self.0 <= budget
    }

    /// Score for cost (inverted: lower is better)
    pub fn score(&self) -> Score {
        let normalized = (1.0 - (self.0 as f32 / 5000.0).min(1.0)).max(0.02);
        Score::unchecked(normalized)
    }
}

impl Validatable for Cost {
    fn validate(&self) -> Result<()> {
        Ok(())
    }
}

/// Expertise score (0.0-1.0)
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd, Serialize, Deserialize)]
pub struct Expertise(f32);

impl Expertise {
    pub fn new(value: f32) -> Result<Expertise> {
        Score::new(value)?;
        Ok(Expertise(value))
    }

    pub fn as_f32(self) -> f32 {
        self.0
    }

    pub fn is_expert(&self) -> bool {
        self.0 >= 0.8
    }
}

impl Validatable for Expertise {
    fn validate(&self) -> Result<()> {
        Score::new(self.0)?;
        Ok(())
    }
}

/// Freshness score (0.0-1.0, where 1.0 = very fresh)
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd, Serialize, Deserialize)]
pub struct Freshness(f32);

impl Freshness {
    pub fn new(value: f32) -> Result<Freshness> {
        Score::new(value)?;
        Ok(Freshness(value))
    }

    pub fn as_f32(self) -> f32 {
        self.0
    }

    pub fn is_fresh(&self) -> bool {
        self.0 >= 0.7
    }
}

impl Validatable for Freshness {
    fn validate(&self) -> Result<()> {
        Score::new(self.0)?;
        Ok(())
    }
}

/// Availability score (0.0-1.0)
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd, Serialize, Deserialize)]
pub struct Availability(f32);

impl Availability {
    pub fn new(value: f32) -> Result<Availability> {
        Score::new(value)?;
        Ok(Availability(value))
    }

    pub fn as_f32(self) -> f32 {
        self.0
    }

    pub fn is_available(&self) -> bool {
        self.0 >= 0.9
    }
}

impl Validatable for Availability {
    fn validate(&self) -> Result<()> {
        Score::new(self.0)?;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_score_new_valid() {
        assert!(Score::new(0.5).is_ok());
        assert!(Score::new(0.0).is_ok());
        assert!(Score::new(1.0).is_ok());
    }

    #[test]
    fn test_score_new_invalid() {
        assert!(Score::new(-0.1).is_err());
        assert!(Score::new(1.1).is_err());
    }

    #[test]
    fn test_latency_score() {
        let latency = Latency::new(100.0).unwrap();
        let score = latency.score();
        assert!(score.as_f32() > 0.9);

        let latency = Latency::new(1000.0).unwrap();
        let score = latency.score();
        assert!(score.as_f32() < 0.2);
    }

    #[test]
    fn test_cost_score() {
        let cost = Cost::new(100);
        let score = cost.score();
        assert!(score.as_f32() > 0.9);

        let cost = Cost::new(5000);
        let score = cost.score();
        assert!(score.as_f32() < 0.1);
    }

    #[test]
    fn test_confidence_level() {
        assert_eq!(Confidence::new(0.2).unwrap().level(), ConfidenceLevel::Low);
        assert_eq!(Confidence::new(0.5).unwrap().level(), ConfidenceLevel::Medium);
        assert_eq!(Confidence::new(0.75).unwrap().level(), ConfidenceLevel::High);
        assert_eq!(Confidence::new(0.9).unwrap().level(), ConfidenceLevel::VeryHigh);
    }
}
