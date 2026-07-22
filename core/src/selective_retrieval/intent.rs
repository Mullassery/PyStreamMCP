// Intent Classifier - Stage 2
// Classifies query intent and complexity for tier/budget assignment

use crate::selective_retrieval::types::*;
use crate::Result;

/// Intent classifier for understanding query needs
pub struct IntentClassifier;

impl IntentClassifier {
    /// Create new intent classifier
    pub fn new() -> Result<Self> {
        Ok(Self)
    }

    /// Classify query intent
    pub async fn classify(&self, query: &str) -> Result<QueryIntent> {
        let keywords = query.to_lowercase();

        // Factual intent: "What is", "Define", "What does"
        if keywords.contains("what is")
            || keywords.contains("define")
            || keywords.contains("meaning")
            || keywords.contains("definition")
        {
            return Ok(QueryIntent::Factual);
        }

        // Conceptual intent: "How does", "How does", "Explain"
        if keywords.contains("how does")
            || keywords.contains("how can")
            || keywords.contains("explain")
            || keywords.contains("understanding")
        {
            return Ok(QueryIntent::Conceptual);
        }

        // Detailed intent: "Compare", "Analyze", "Difference"
        if keywords.contains("compare")
            || keywords.contains("versus")
            || keywords.contains("vs")
            || keywords.contains("analyze")
            || keywords.contains("difference")
        {
            return Ok(QueryIntent::Detailed);
        }

        // Complex intent: "Design", "Build", "System"
        if keywords.contains("design")
            || keywords.contains("build")
            || keywords.contains("architecture")
            || keywords.contains("system")
            || keywords.contains("implement")
        {
            return Ok(QueryIntent::Complex);
        }

        // Default based on length and punctuation
        if query.len() > 50 {
            Ok(QueryIntent::Detailed)
        } else if query.len() > 30 {
            Ok(QueryIntent::Conceptual)
        } else {
            Ok(QueryIntent::Factual)
        }
    }

    /// Detect query complexity (Simple/Moderate/Complex/VeryComplex)
    pub fn detect_complexity(&self, query: &str) -> Result<QueryComplexity> {
        let words: Vec<&str> = query.split_whitespace().collect();
        let word_count = words.len();

        // Count complexity signals
        let mut complexity_score = 0u32;

        // Word count signal
        if word_count > 50 {
            complexity_score += 3;
        } else if word_count > 30 {
            complexity_score += 2;
        } else if word_count > 10 {
            complexity_score += 1;
        }

        // Entity count signal (words with capitals)
        let entity_count = words.iter().filter(|w| w.chars().next().map_or(false, |c| c.is_uppercase())).count();
        if entity_count > 3 {
            complexity_score += 2;
        } else if entity_count > 1 {
            complexity_score += 1;
        }

        // Relationship signals
        let query_lower = query.to_lowercase();
        if query_lower.contains("relate") || query_lower.contains("compare") {
            complexity_score += 1;
        }
        if query_lower.contains("design") || query_lower.contains("implement") {
            complexity_score += 2;
        }
        if query_lower.contains("constraint") || query_lower.contains("trade-off") {
            complexity_score += 1;
        }

        // Punctuation signals
        let has_semicolon = query.contains(';');
        let has_colon = query.contains(':');
        let question_count = query.matches('?').count();

        if has_semicolon || has_colon || question_count > 1 {
            complexity_score += 1;
        }

        // Map score to complexity
        Ok(match complexity_score {
            0..=1 => QueryComplexity::Simple,
            2..=4 => QueryComplexity::Moderate,
            5..=7 => QueryComplexity::Complex,
            _ => QueryComplexity::VeryComplex,
        })
    }
}

impl Default for IntentClassifier {
    fn default() -> Self {
        Self
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_intent_classification() {
        let classifier = IntentClassifier::new().unwrap();

        // Test factual
        let intent = classifier.classify("What is machine learning?").await.unwrap();
        assert_eq!(intent, QueryIntent::Factual);

        // Test conceptual
        let intent = classifier
            .classify("How does neural networks work?")
            .await
            .unwrap();
        assert_eq!(intent, QueryIntent::Conceptual);

        // Test detailed
        let intent = classifier
            .classify("Compare supervised vs unsupervised learning")
            .await
            .unwrap();
        assert_eq!(intent, QueryIntent::Detailed);

        // Test complex
        let intent = classifier
            .classify("Design a recommendation system for e-commerce")
            .await
            .unwrap();
        assert_eq!(intent, QueryIntent::Complex);
    }

    #[test]
    fn test_complexity_detection() {
        let classifier = IntentClassifier::new().unwrap();

        // Simple
        let complexity = classifier.detect_complexity("What is X?").unwrap();
        assert_eq!(complexity, QueryComplexity::Simple);

        // Moderate
        let complexity = classifier.detect_complexity("How does X relate to Y?").unwrap();
        assert_eq!(complexity, QueryComplexity::Moderate);

        // Complex
        let complexity = classifier
            .detect_complexity("Compare X and Y across dimensions A, B, and C")
            .unwrap();
        assert_eq!(complexity, QueryComplexity::Complex);

        // Very Complex
        let complexity = classifier.detect_complexity(
            "Design a system with constraints X; handle edge cases: Y, Z; optimize for A, B, C?",
        )
        .unwrap();
        assert_eq!(complexity, QueryComplexity::VeryComplex);
    }

    #[test]
    fn test_entity_detection() {
        let classifier = IntentClassifier::new().unwrap();

        // Multiple entities increase complexity
        let simple = classifier.detect_complexity("What is X?").unwrap();
        let complex = classifier.detect_complexity("What is X, Y, and Z?").unwrap();

        assert!(complex as u32 > simple as u32);
    }
}
