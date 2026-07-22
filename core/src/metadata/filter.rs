// Metadata Filtering Engine - Stage 1
// Ranks candidates by metadata (no data retrieval needed)

use crate::metadata::types::*;
use crate::{Error, Result};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Configuration for metadata filtering
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FilterConfig {
    pub ranking_strategy: RankingStrategy,
    pub quality_weights: QualityWeights,
    pub cache_config: CacheConfig,
}

impl Default for FilterConfig {
    fn default() -> Self {
        Self {
            ranking_strategy: RankingStrategy::Quality,
            quality_weights: QualityWeights::default(),
            cache_config: CacheConfig::default(),
        }
    }
}

/// Strategy for ranking candidates
#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
pub enum RankingStrategy {
    /// Rank by overall quality score
    Quality,
    /// Rank by cost-efficiency
    CostOptimized,
    /// Rank by freshness
    Freshness,
    /// Balanced approach (default)
    Balanced,
}

/// Cache configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CacheConfig {
    /// TTL for cache entries (seconds, 0 = no expiry)
    pub ttl_seconds: u64,
    /// Maximum cache size (entries)
    pub max_entries: usize,
}

impl Default for CacheConfig {
    fn default() -> Self {
        Self {
            ttl_seconds: 3600, // 1 hour
            max_entries: 1000,
        }
    }
}

/// Metadata filtering engine
pub struct MetadataFilter {
    config: FilterConfig,
}

impl MetadataFilter {
    /// Create new filter
    pub fn new(config: FilterConfig) -> Result<Self> {
        Ok(Self { config })
    }

    /// Rank candidates by metadata
    pub async fn rank(
        &self,
        query: &str,
        _source_type: SourceType,
        candidates: Vec<Metadata>,
    ) -> Result<Vec<RankedCandidate>> {
        if candidates.is_empty() {
            return Err(Error::Generic("No candidates to rank".to_string()));
        }

        // Extract query features for scoring
        let query_features = self.extract_query_features(query);

        // Score each candidate
        let mut scored: Vec<(Metadata, f64, String)> = candidates
            .into_iter()
            .map(|c| {
                let score = self.score_candidate(&c, &query_features);
                let justification = self.create_justification(&c, &query_features, score);
                (c, score, justification)
            })
            .collect();

        // Sort by score (highest first)
        scored.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));

        // Return ranked candidates
        Ok(scored
            .into_iter()
            .enumerate()
            .map(|(rank, (metadata, score, justification))| RankedCandidate {
                metadata,
                rank: rank + 1,
                score,
                justification,
            })
            .collect())
    }

    /// Score a single candidate
    fn score_candidate(&self, metadata: &Metadata, query_features: &QueryFeatures) -> f64 {
        let quality = metadata.quality();

        // Base quality score
        let base_score = quality.overall_score(&self.config.quality_weights);

        // Adjust based on query features
        let (topical_boost, domain_boost, freshness_factor) =
            self.calculate_adjustments(metadata, query_features);

        let score = (base_score * 0.4 + topical_boost * 0.3 + domain_boost * 0.2)
            * (1.0 + freshness_factor * 0.1);

        score.min(1.0).max(0.0)
    }

    /// Calculate score adjustments based on query
    fn calculate_adjustments(
        &self,
        metadata: &Metadata,
        query_features: &QueryFeatures,
    ) -> (f64, f64, f64) {
        let topical_boost = match metadata {
            Metadata::Web(w) => {
                // Boost if topic relevance is high
                w.topic_relevance * query_features.topic_weight
            }
            Metadata::Database(d) => {
                // Boost if we have matching columns
                self.column_match_score(&d.columns, query_features) * query_features.topic_weight
            }
            Metadata::MCPTool(t) => {
                // Boost if capabilities match
                self.capability_match_score(&t.capabilities, query_features) * query_features.topic_weight
            }
        };

        let domain_boost = match metadata {
            Metadata::Web(w) => {
                // Boost if domain tags match
                if w.tags.iter().any(|tag| query_features.domain_tags.contains(tag)) {
                    0.2
                } else {
                    0.0
                }
            }
            Metadata::Database(_) => 0.0,
            Metadata::MCPTool(t) => {
                // Boost if tool auth matches requirements
                if query_features.auth_available.contains(&t.auth_type.as_str()) {
                    0.2
                } else {
                    0.0
                }
            }
        };

        let freshness_factor = match self.config.ranking_strategy {
            RankingStrategy::Quality => 0.0,
            RankingStrategy::CostOptimized => 0.0,
            RankingStrategy::Freshness => 1.0,
            RankingStrategy::Balanced => 0.5,
        };

        (topical_boost, domain_boost, freshness_factor)
    }

    /// Match columns to query features
    fn column_match_score(&self, columns: &[ColumnMetadata], query: &QueryFeatures) -> f64 {
        if columns.is_empty() || query.required_fields.is_empty() {
            return 0.5;
        }

        let matched = columns
            .iter()
            .filter(|col| query.required_fields.iter().any(|f| col.name.contains(f)))
            .count();

        (matched as f64) / (query.required_fields.len() as f64)
    }

    /// Match tool capabilities to query
    fn capability_match_score(&self, capabilities: &[String], query: &QueryFeatures) -> f64 {
        if capabilities.is_empty() || query.required_capabilities.is_empty() {
            return 0.5;
        }

        let matched = capabilities
            .iter()
            .filter(|cap| query.required_capabilities.iter().any(|r| cap.contains(r)))
            .count();

        (matched as f64) / (query.required_capabilities.len() as f64)
    }

    /// Create human-readable justification for ranking
    fn create_justification(
        &self,
        metadata: &Metadata,
        _query_features: &QueryFeatures,
        score: f64,
    ) -> String {
        let id = metadata.id();
        let quality = metadata.quality();
        let tokens = metadata.estimated_tokens();

        format!(
            "{}: score={:.2} (auth={:.2} fresh={:.2} cost={:.2} tokens={})",
            id, score, quality.authority, quality.freshness, quality.cost_efficiency, tokens
        )
    }

    /// Extract features from query for scoring
    fn extract_query_features(&self, query: &str) -> QueryFeatures {
        let words: Vec<&str> = query.split_whitespace().collect();

        // Detect domain keywords
        let domain_tags = self.detect_domain_tags(query);
        let required_capabilities = self.detect_capabilities(query);
        let required_fields = self.detect_fields(query);
        let auth_available = vec!["none", "api_key", "oauth"];

        // Topic weight increases with query length and specificity
        let topic_weight = (words.len() as f64 / 10.0).min(1.0).max(0.5);

        QueryFeatures {
            domain_tags,
            required_capabilities,
            required_fields,
            auth_available,
            topic_weight,
        }
    }

    /// Detect domain tags from query (e.g., "documentation", "tutorial")
    fn detect_domain_tags(&self, query: &str) -> Vec<String> {
        let mut tags = vec![];
        let query_lower = query.to_lowercase();

        if query_lower.contains("document") || query_lower.contains("guide") {
            tags.push("documentation".to_string());
        }
        if query_lower.contains("tutorial") || query_lower.contains("example") {
            tags.push("tutorial".to_string());
        }
        if query_lower.contains("api") || query_lower.contains("endpoint") {
            tags.push("api_reference".to_string());
        }
        if query_lower.contains("news") || query_lower.contains("latest") {
            tags.push("news".to_string());
        }

        tags
    }

    /// Detect required capabilities from query
    fn detect_capabilities(&self, query: &str) -> Vec<String> {
        let mut caps = vec![];
        let query_lower = query.to_lowercase();

        if query_lower.contains("search") {
            caps.push("search".to_string());
        }
        if query_lower.contains("analy") {
            caps.push("analysis".to_string());
        }
        if query_lower.contains("transform") {
            caps.push("transform".to_string());
        }
        if query_lower.contains("generate") {
            caps.push("generation".to_string());
        }

        caps
    }

    /// Detect required fields from query
    fn detect_fields(&self, query: &str) -> Vec<String> {
        let mut fields = vec![];
        let words: Vec<&str> = query.split_whitespace().collect();

        // Look for field-like words (all lowercase, short)
        for word in words {
            if word.len() > 2 && word.len() < 20 && word.chars().all(|c| c.is_alphanumeric() || c == '_') {
                fields.push(word.to_lowercase());
            }
        }

        // Keep only unique fields, limit to 5
        fields.sort();
        fields.dedup();
        fields.truncate(5);

        fields
    }
}

/// Extracted query features for scoring
#[derive(Debug)]
struct QueryFeatures {
    domain_tags: Vec<String>,
    required_capabilities: Vec<String>,
    required_fields: Vec<String>,
    auth_available: Vec<&'static str>,
    topic_weight: f64,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_rank_web_candidates() {
        let config = FilterConfig::default();
        let filter = MetadataFilter::new(config).unwrap();

        let candidates = vec![
            Metadata::Web(WebMetadata {
                url: "https://example.com/doc".to_string(),
                domain: "example.com".to_string(),
                publish_timestamp: 0,
                size_bytes: 10000,
                wayback_depth_years: 5,
                has_ssl: true,
                domain_age_years: 10,
                topic_relevance: 0.9,
                tags: vec!["documentation".to_string()],
            }),
            Metadata::Web(WebMetadata {
                url: "https://other.com/guide".to_string(),
                domain: "other.com".to_string(),
                publish_timestamp: 0,
                size_bytes: 5000,
                wayback_depth_years: 2,
                has_ssl: false,
                domain_age_years: 2,
                topic_relevance: 0.5,
                tags: vec![],
            }),
        ];

        let ranked = filter.rank("test query", SourceType::Web, candidates).await.unwrap();
        assert_eq!(ranked.len(), 2);
        // Higher score should rank first
        assert!(ranked[0].score > ranked[1].score);
    }

    #[test]
    fn test_extract_query_features() {
        let config = FilterConfig::default();
        let filter = MetadataFilter::new(config).unwrap();

        let features = filter.extract_query_features("API documentation tutorial");
        assert!(features.domain_tags.contains(&"documentation".to_string()));
        assert!(features.domain_tags.contains(&"tutorial".to_string()));
    }
}
