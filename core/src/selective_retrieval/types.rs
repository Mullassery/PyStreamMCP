// Stage 2 Type Definitions

use serde::{Deserialize, Serialize};

/// Content item retrieved from a source (to be filtered)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ContentItem {
    pub id: String,
    pub item_type: ItemType,
    pub content: String,
    pub tokens: u32,
    /// Metadata about item (publish date, source, etc.)
    pub metadata: ItemMetadata,
}

/// Type of content item
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum ItemType {
    /// Web: paragraph, section, subsection
    WebParagraph,
    WebSection,
    WebSubsection,
    /// Database: row or record
    DatabaseRow,
    /// Tool: output segment
    ToolOutput,
}

/// Metadata about a content item
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ItemMetadata {
    /// Source URL/table/tool
    pub source: String,
    /// Item relevance to query (0-1, estimated)
    pub relevance_hint: f64,
    /// When was this created/updated
    pub timestamp: i64,
    /// Informativeness score (0-1, high = more information)
    pub informativeness: f64,
    /// Custom tags (e.g., "code", "example", "warning")
    pub tags: Vec<String>,
}

/// Retrieved content from Stage 1 (selective) retrieval
#[derive(Debug, Clone)]
pub struct RetrievedContent {
    pub items: Vec<ContentItem>,
    pub total_tokens: u32,
    pub source_type: String,
}

/// Reranked content item with contextual score
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RerankingScore {
    pub item_id: String,
    /// Contextual relevance score (0-1)
    pub relevance: f64,
    /// Informativeness score (0-1)
    pub informativeness: f64,
    /// Uniqueness score (0-1, 1.0 if unique, decreases for duplicates)
    pub uniqueness: f64,
    /// Recency score (0-1, based on timestamp)
    pub recency: f64,
    /// Combined score (weighted average)
    pub combined_score: f64,
    /// Why this item was ranked (explainability)
    pub justification: String,
}

/// Query intent classification
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum QueryIntent {
    /// Factual lookup ("What is X?")
    Factual,
    /// Understanding ("How does X work?")
    Conceptual,
    /// Detailed analysis ("Compare X and Y")
    Detailed,
    /// Complex reasoning ("Design X system")
    Complex,
}

/// Intent scoring with confidence
#[derive(Debug, Clone)]
pub struct IntentScore {
    pub intent: QueryIntent,
    /// Confidence (0-1)
    pub confidence: f64,
}

/// Query complexity level
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum QueryComplexity {
    Simple,
    Moderate,
    Complex,
    VeryComplex,
}

impl std::fmt::Display for QueryComplexity {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            QueryComplexity::Simple => write!(f, "Simple"),
            QueryComplexity::Moderate => write!(f, "Moderate"),
            QueryComplexity::Complex => write!(f, "Complex"),
            QueryComplexity::VeryComplex => write!(f, "VeryComplex"),
        }
    }
}

/// Ranking criteria for reranking
#[derive(Debug, Clone)]
pub struct RankingCriteria {
    /// How well does this match query intent?
    pub relevance_weight: f64,
    /// How much value does this add?
    pub informativeness_weight: f64,
    /// Is this info in other items already?
    pub uniqueness_weight: f64,
    /// Is this current/recent?
    pub recency_weight: f64,
}

impl Default for RankingCriteria {
    fn default() -> Self {
        Self {
            relevance_weight: 0.4,
            informativeness_weight: 0.3,
            uniqueness_weight: 0.2,
            recency_weight: 0.1,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_content_item_creation() {
        let item = ContentItem {
            id: "test_1".to_string(),
            item_type: ItemType::WebSection,
            content: "Test content".to_string(),
            tokens: 100,
            metadata: ItemMetadata {
                source: "example.com".to_string(),
                relevance_hint: 0.8,
                timestamp: 0,
                informativeness: 0.7,
                tags: vec!["important".to_string()],
            },
        };

        assert_eq!(item.tokens, 100);
        assert_eq!(item.item_type, ItemType::WebSection);
    }

    #[test]
    fn test_query_intent_classification() {
        let intents = vec![
            QueryIntent::Factual,
            QueryIntent::Conceptual,
            QueryIntent::Detailed,
            QueryIntent::Complex,
        ];

        assert_eq!(intents.len(), 4);
    }

    #[test]
    fn test_complexity_levels() {
        let levels = vec![
            QueryComplexity::Simple,
            QueryComplexity::Moderate,
            QueryComplexity::Complex,
            QueryComplexity::VeryComplex,
        ];

        assert_eq!(levels.len(), 4);
    }
}
