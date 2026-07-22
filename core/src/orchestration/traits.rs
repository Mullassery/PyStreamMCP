use super::error::Result;

/// Anything that can be scored (0.0-1.0)
pub trait Scoreable {
    /// Calculate score
    fn score(&self) -> f32;

    /// Explain why this score
    fn score_explanation(&self) -> String;

    /// Validate score is in valid range
    fn validate_score(&self) -> Result<()> {
        let score = self.score();
        if score < 0.0 || score > 1.0 {
            return Err(super::error::OrchestrationError::ConstraintViolation {
                constraint: "score_range".to_string(),
                actual: score.to_string(),
                expected: "0.0-1.0".to_string(),
            });
        }
        Ok(())
    }
}

/// Anything that can be ranked
pub trait Rankable: Scoreable {
    /// Position in ranking (1-based)
    fn rank_position(&self) -> Option<usize>;

    /// Set rank position
    fn set_rank_position(&mut self, position: usize);
}

/// Anything that produces confidence measurements
pub trait Confidence {
    /// Confidence 0.0-1.0
    fn confidence(&self) -> f32;

    /// Why are we confident/not confident?
    fn confidence_explanation(&self) -> String {
        format!("Confidence: {:.1}%", self.confidence() * 100.0)
    }

    /// Confidence is high enough to trust?
    fn is_confident(&self, threshold: f32) -> bool {
        self.confidence() >= threshold
    }
}

/// Anything that can track performance
pub trait PerformanceMetric {
    /// Record successful operation
    fn record_success(&mut self, latency_ms: f32, cost_tokens: usize) -> Result<()>;

    /// Record failed operation
    fn record_failure(&mut self, reason: &str) -> Result<()>;

    /// Success rate 0.0-1.0
    fn success_rate(&self) -> f32;

    /// Average latency in milliseconds
    fn avg_latency_ms(&self) -> f32;

    /// Total queries recorded
    fn total_queries(&self) -> usize;
}

/// Anything that can be validated
pub trait Validatable {
    /// Validate this item
    fn validate(&self) -> Result<()>;

    /// Human-readable validation result
    fn validation_error_message(&self) -> Option<String> {
        self.validate().err().map(|e| e.to_string())
    }

    /// Is this item valid?
    fn is_valid(&self) -> bool {
        self.validate().is_ok()
    }
}

/// Anything queryable
pub trait Queryable<Q, R> {
    /// Execute a query
    fn query(&self, q: Q) -> Result<Vec<R>>;

    /// Execute a query with a limit
    fn query_limited(&self, q: Q, limit: usize) -> Result<Vec<R>> {
        let results = self.query(q)?;
        Ok(results.into_iter().take(limit).collect())
    }
}

/// Anything that can explain decisions
pub trait Explainable {
    /// Explain this decision/result in human-readable form
    fn explain(&self) -> String;

    /// Explain concisely
    fn explain_brief(&self) -> String {
        self.explain()
    }
}

/// Anything that can provide alternatives
pub trait HasAlternatives {
    type Alternative;

    /// Get alternative options
    fn alternatives(&self) -> Vec<Self::Alternative>;

    /// Number of alternatives available
    fn alternative_count(&self) -> usize {
        self.alternatives().len()
    }
}

/// Composition: Scoreable + Rankable
pub trait RankedScore: Scoreable + Rankable {}
impl<T: Scoreable + Rankable> RankedScore for T {}

/// Composition: Scoreable + Confidence
pub trait ConfidentScore: Scoreable + Confidence {}
impl<T: Scoreable + Confidence> ConfidentScore for T {}

/// Composition: Explainable + HasAlternatives
pub trait ExplainedChoice: Explainable + HasAlternatives {}
impl<T: Explainable + HasAlternatives> ExplainedChoice for T {}

/// Composition: All observable traits
pub trait FullyObservable: Scoreable + Confidence + Explainable {}
impl<T: Scoreable + Confidence + Explainable> FullyObservable for T {}

#[cfg(test)]
mod tests {
    use super::*;

    struct MockScore(f32);

    impl Scoreable for MockScore {
        fn score(&self) -> f32 {
            self.0
        }

        fn score_explanation(&self) -> String {
            format!("Score is {}", self.0)
        }
    }

    #[test]
    fn test_scoreable_validate_score() {
        let valid = MockScore(0.5);
        assert!(valid.validate_score().is_ok());

        let invalid = MockScore(1.5);
        assert!(invalid.validate_score().is_err());
    }

    #[test]
    fn test_confidence() {
        struct MockConfidence(f32);

        impl Confidence for MockConfidence {
            fn confidence(&self) -> f32 {
                self.0
            }
        }

        let conf = MockConfidence(0.8);
        assert!(conf.is_confident(0.7));
        assert!(!conf.is_confident(0.9));
    }
}
