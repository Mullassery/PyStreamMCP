/// Query complexity detection for adaptive resource allocation
/// Classifies queries as Simple/Moderate/Complex/Very Complex

use serde::{Serialize, Deserialize};

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
pub enum ComplexityTier {
    Simple,
    Moderate,
    Complex,
    VeryComplex,
}

impl ComplexityTier {
    /// Get token budget multiplier (how many tokens to allocate)
    pub fn token_multiplier(&self) -> f64 {
        match self {
            Self::Simple => 1.0,      // Minimal: ~500 tokens
            Self::Moderate => 2.0,    // Standard: ~1000 tokens
            Self::Complex => 4.0,     // Large: ~2000 tokens
            Self::VeryComplex => 8.0, // Comprehensive: ~4000 tokens
        }
    }

    /// Get source selection strategy
    pub fn source_strategy(&self) -> SourceStrategy {
        match self {
            Self::Simple => SourceStrategy::TopOne,         // Use best source only
            Self::Moderate => SourceStrategy::TopTwo,       // Compare 2 sources
            Self::Complex => SourceStrategy::TopThree,      // Triangulate 3 sources
            Self::VeryComplex => SourceStrategy::TopFive,   // Comprehensive coverage
        }
    }
}

#[derive(Clone, Copy, Debug)]
pub enum SourceStrategy {
    TopOne,    // Select only best source
    TopTwo,    // Fetch from 2 sources, merge
    TopThree,  // Fetch from 3 sources, aggregate
    TopFive,   // Fetch from 5 sources, comprehensive
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct QueryComplexity {
    pub tier: ComplexityTier,
    pub word_count: usize,
    pub has_filters: bool,
    pub has_aggregations: bool,
    pub requires_temporal: bool,
    pub requires_spatial: bool,
    pub confidence: f64,
}

pub struct ComplexityDetector;

impl ComplexityDetector {
    /// Detect query complexity from query text
    pub fn detect(query: &str) -> QueryComplexity {
        let word_count = query.split_whitespace().count();
        let has_filters = Self::has_filters(query);
        let has_aggregations = Self::has_aggregations(query);
        let requires_temporal = Self::requires_temporal(query);
        let requires_spatial = Self::requires_spatial(query);

        let tier = Self::classify(
            word_count,
            has_filters,
            has_aggregations,
            requires_temporal,
            requires_spatial,
        );

        let confidence = Self::confidence(word_count, &tier);

        QueryComplexity {
            tier,
            word_count,
            has_filters,
            has_aggregations,
            requires_temporal,
            requires_spatial,
            confidence,
        }
    }

    fn has_filters(query: &str) -> bool {
        let keywords = ["where", "filter", "between", "from", "to", "range"];
        keywords.iter().any(|k| query.to_lowercase().contains(k))
    }

    fn has_aggregations(query: &str) -> bool {
        let keywords = ["sum", "count", "average", "avg", "min", "max", "group"];
        keywords.iter().any(|k| query.to_lowercase().contains(k))
    }

    fn requires_temporal(query: &str) -> bool {
        let keywords = ["when", "date", "time", "year", "month", "day", "hour", "historical", "trend"];
        keywords.iter().any(|k| query.to_lowercase().contains(k))
    }

    fn requires_spatial(query: &str) -> bool {
        let keywords = ["where", "location", "region", "near", "distance", "area", "zone"];
        keywords.iter().any(|k| query.to_lowercase().contains(k))
    }

    fn classify(
        word_count: usize,
        has_filters: bool,
        has_aggregations: bool,
        temporal: bool,
        spatial: bool,
    ) -> ComplexityTier {
        let mut score = 0;

        // Word count
        if word_count > 50 {
            score += 3;
        } else if word_count > 20 {
            score += 2;
        } else if word_count > 5 {
            score += 1;
        }

        // Features
        if has_filters { score += 1; }
        if has_aggregations { score += 2; }
        if temporal { score += 1; }
        if spatial { score += 1; }

        match score {
            0..=1 => ComplexityTier::Simple,
            2..=3 => ComplexityTier::Moderate,
            4..=5 => ComplexityTier::Complex,
            _ => ComplexityTier::VeryComplex,
        }
    }

    fn confidence(word_count: usize, tier: &ComplexityTier) -> f64 {
        let base = match word_count {
            0..=5 => 0.6,    // Very short: low confidence
            6..=20 => 0.85,  // Medium: good confidence
            21..=50 => 0.9,  // Long: very good
            _ => 0.95,       // Very long: excellent
        };

        match tier {
            ComplexityTier::Simple => base * 0.95,
            ComplexityTier::Moderate => base,
            ComplexityTier::Complex => base * 0.95,
            ComplexityTier::VeryComplex => base * 0.9,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_simple_query_detection() {
        let complexity = ComplexityDetector::detect("What is Python?");
        assert_eq!(complexity.tier, ComplexityTier::Simple);
        assert!(complexity.word_count <= 5);
    }

    #[test]
    fn test_complex_query_detection() {
        let complexity = ComplexityDetector::detect(
            "Show me historical temperature trends in the New York area between January 2020 and December 2023 aggregated by month with average values"
        );
        assert_eq!(complexity.tier, ComplexityTier::Complex);
        assert!(complexity.requires_temporal);
        assert!(complexity.requires_spatial);
        assert!(complexity.has_aggregations);
    }

    #[test]
    fn test_very_complex_query_detection() {
        let query = "Calculate the seasonal patterns and anomalies in precipitation data across multiple geographic regions with temporal cross-correlation analysis comparing historical data from the past decade";
        let complexity = ComplexityDetector::detect(query);
        assert_eq!(complexity.tier, ComplexityTier::VeryComplex);
        assert!(complexity.word_count > 20);
    }

    #[test]
    fn test_token_multipliers() {
        assert_eq!(ComplexityTier::Simple.token_multiplier(), 1.0);
        assert_eq!(ComplexityTier::Moderate.token_multiplier(), 2.0);
        assert_eq!(ComplexityTier::Complex.token_multiplier(), 4.0);
        assert_eq!(ComplexityTier::VeryComplex.token_multiplier(), 8.0);
    }

    #[test]
    fn test_source_strategies() {
        match ComplexityTier::Simple.source_strategy() {
            SourceStrategy::TopOne => {},
            _ => panic!("Expected TopOne"),
        }
        match ComplexityTier::VeryComplex.source_strategy() {
            SourceStrategy::TopFive => {},
            _ => panic!("Expected TopFive"),
        }
    }
}
