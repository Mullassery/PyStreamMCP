// Contextual Reranking Engine - Stage 2
// Reranks retrieved content by relevance to query intent

use crate::selective_retrieval::types::*;
use crate::{Error, Result};
use serde::{Deserialize, Serialize};
use std::collections::HashSet;

/// Contextual reranker for post-retrieval filtering
pub struct ContextualReranker {
    config: RerankerConfig,
}

/// Reranker configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RerankerConfig {
    /// Weight for semantic relevance (0-1)
    pub relevance_weight: f64,
    /// Weight for informativeness (0-1)
    pub informativeness_weight: f64,
    /// Weight for uniqueness (0-1)
    pub uniqueness_weight: f64,
    /// Weight for recency (0-1)
    pub recency_weight: f64,
}

impl Default for RerankerConfig {
    fn default() -> Self {
        Self {
            relevance_weight: 0.4,
            informativeness_weight: 0.3,
            uniqueness_weight: 0.2,
            recency_weight: 0.1,
        }
    }
}

/// Ranking criteria (can be customized per query)
#[derive(Debug, Clone)]
pub struct RankingCriteria {
    pub relevance_weight: f64,
    pub informativeness_weight: f64,
    pub uniqueness_weight: f64,
    pub recency_weight: f64,
}

impl RankingCriteria {
    /// Create criteria for query intent
    pub fn for_intent(intent: &QueryIntent) -> Self {
        match intent {
            QueryIntent::Factual => Self {
                relevance_weight: 0.6,    // Exact relevance critical
                informativeness_weight: 0.2,
                uniqueness_weight: 0.1,
                recency_weight: 0.1,
            },
            QueryIntent::Conceptual => Self {
                relevance_weight: 0.4,
                informativeness_weight: 0.4,  // More detail needed
                uniqueness_weight: 0.1,
                recency_weight: 0.1,
            },
            QueryIntent::Detailed => Self {
                relevance_weight: 0.35,
                informativeness_weight: 0.35, // Full analysis
                uniqueness_weight: 0.2,
                recency_weight: 0.1,
            },
            QueryIntent::Complex => Self {
                relevance_weight: 0.3,
                informativeness_weight: 0.3,
                uniqueness_weight: 0.25,
                recency_weight: 0.15,         // Multiple perspectives
            },
        }
    }
}

impl ContextualReranker {
    /// Create new contextual reranker
    pub fn new(config: RerankerConfig) -> Result<Self> {
        // Validate weights sum approximately to 1.0
        let total = config.relevance_weight
            + config.informativeness_weight
            + config.uniqueness_weight
            + config.recency_weight;

        if (total - 1.0).abs() > 0.1 {
            return Err(Error::Generic(
                "Reranker weights should sum to ~1.0".to_string(),
            ));
        }

        Ok(Self { config })
    }

    /// Rerank content items by contextual relevance
    pub async fn rerank(
        &self,
        query: &str,
        intent: &QueryIntent,
        items: Vec<ContentItem>,
    ) -> Result<Vec<ContentItem>> {
        if items.is_empty() {
            return Ok(vec![]);
        }

        // Get criteria for this intent
        let criteria = RankingCriteria::for_intent(intent);

        // Calculate relevance keywords from query
        let keywords = self.extract_keywords(query);

        // Score each item
        let mut scored: Vec<(ContentItem, RerankingScore)> = items
            .into_iter()
            .map(|item| {
                let score = self.score_item(&item, &keywords, &criteria, intent);
                (item, score)
            })
            .collect();

        // Sort by combined score (highest first)
        scored.sort_by(|a, b| {
            b.1.combined_score
                .partial_cmp(&a.1.combined_score)
                .unwrap_or(std::cmp::Ordering::Equal)
        });

        // Return scored items (keep score for later filtering)
        Ok(scored.into_iter().map(|(item, _)| item).collect())
    }

    /// Score a single item
    fn score_item(
        &self,
        item: &ContentItem,
        keywords: &[String],
        criteria: &RankingCriteria,
        intent: &QueryIntent,
    ) -> RerankingScore {
        // Relevance: keyword match + metadata hint
        let keyword_matches = keywords
            .iter()
            .filter(|kw| item.content.to_lowercase().contains(&kw.to_lowercase()))
            .count() as f64;
        let keyword_score = (keyword_matches / keywords.len() as f64).min(1.0);
        let relevance = keyword_score * 0.6 + item.metadata.relevance_hint * 0.4;

        // Informativeness: from metadata
        let informativeness = item.metadata.informativeness;

        // Uniqueness: based on content length and uniqueness
        let uniqueness = (item.tokens as f64 / 1000.0).min(1.0); // Longer = more unique

        // Recency: based on timestamp
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs() as i64;
        let days_old = if item.metadata.timestamp > 0 {
            (now - item.metadata.timestamp) / 86400
        } else {
            0 // Unknown = neutral
        };
        let recency = (1.0 - (days_old as f64 / 365.0).min(1.0)).max(0.0);

        // Combined score (weighted average)
        let combined_score = (relevance * criteria.relevance_weight
            + informativeness * criteria.informativeness_weight
            + uniqueness * criteria.uniqueness_weight
            + recency * criteria.recency_weight)
            .min(1.0)
            .max(0.0);

        // Justification
        let justification = format!(
            "{}: relevance={:.2} info={:.2} unique={:.2} recency={:.2} (intent={:?})",
            item.id, relevance, informativeness, uniqueness, recency, intent
        );

        RerankingScore {
            item_id: item.id.clone(),
            relevance,
            informativeness,
            uniqueness,
            recency,
            combined_score,
            justification,
        }
    }

    /// Extract keywords from query
    fn extract_keywords(&self, query: &str) -> Vec<String> {
        let words: Vec<&str> = query
            .split_whitespace()
            .filter(|w| w.len() > 2 && !self.is_stopword(w))
            .collect();

        // Keep meaningful words, limit to 10
        let keywords: Vec<String> = words
            .iter()
            .map(|w| w.to_lowercase())
            .collect::<HashSet<_>>()
            .into_iter()
            .take(10)
            .collect();

        keywords
    }

    /// Check if word is a stopword
    fn is_stopword(&self, word: &str) -> bool {
        matches!(
            word.to_lowercase().as_str(),
            "a" | "an" | "and" | "are" | "as" | "at" | "be" | "but" | "by" | "for"
                | "from" | "if" | "in" | "into" | "is" | "it" | "no" | "not" | "of"
                | "on" | "or" | "such" | "that" | "the" | "their" | "then" | "these"
                | "they" | "this" | "to" | "was" | "will" | "with"
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_rerank_items() {
        let config = RerankerConfig::default();
        let reranker = ContextualReranker::new(config).unwrap();

        let items = vec![
            ContentItem {
                id: "1".to_string(),
                item_type: ItemType::WebSection,
                content: "Highly relevant information about the topic".to_string(),
                tokens: 500,
                metadata: ItemMetadata {
                    source: "example.com".to_string(),
                    relevance_hint: 0.9,
                    timestamp: 0,
                    informativeness: 0.8,
                    tags: vec![],
                },
            },
            ContentItem {
                id: "2".to_string(),
                item_type: ItemType::WebSection,
                content: "Barely related information".to_string(),
                tokens: 100,
                metadata: ItemMetadata {
                    source: "other.com".to_string(),
                    relevance_hint: 0.3,
                    timestamp: 0,
                    informativeness: 0.2,
                    tags: vec![],
                },
            },
        ];

        let reranked = reranker
            .rerank("relevant information", &QueryIntent::Conceptual, items)
            .await
            .unwrap();

        assert_eq!(reranked.len(), 2);
        // Item 1 should be first (more relevant)
        assert_eq!(reranked[0].id, "1");
    }

    #[test]
    fn test_ranking_criteria_for_intent() {
        let factual = RankingCriteria::for_intent(&QueryIntent::Factual);
        assert!(factual.relevance_weight > 0.5); // Relevance critical

        let complex = RankingCriteria::for_intent(&QueryIntent::Complex);
        assert!(complex.uniqueness_weight > factual.uniqueness_weight); // More diverse
    }

    #[test]
    fn test_extract_keywords() {
        let config = RerankerConfig::default();
        let reranker = ContextualReranker::new(config).unwrap();

        let keywords = reranker.extract_keywords("the quick brown fox jumps");
        assert!(keywords.contains(&"quick".to_string()));
        assert!(keywords.contains(&"brown".to_string()));
        assert!(!keywords.contains(&"the".to_string())); // stopword
    }
}
