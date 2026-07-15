use serde::{Deserialize, Serialize};

/// Discovery identifies relevant data sources and context for queries.
///
/// PyStreamMCP's discovery engine finds and ranks available information
/// based on relevance, freshness, and cost.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Discovery {
    pub id: String,
    pub query_id: String,
    pub discovered_sources: Vec<DiscoveredSource>,
    pub total_available_tokens: u32,
    pub created_at: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DiscoveredSource {
    pub id: String,
    pub name: String,
    pub source_type: SourceType,
    pub relevance_score: f32,
    pub estimated_tokens: u32,
    pub freshness_score: f32,
    pub availability: Availability,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum SourceType {
    Table { table_name: String },
    Index { index_name: String },
    Cache { cache_key: String },
    External { api: String },
    Computed { function: String },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Availability {
    Available,
    CachedAndFresh,
    StaleButAvailable { staleness_seconds: u64 },
    Unavailable { reason: String },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DiscoveryRanking {
    pub query_id: String,
    pub ranked_sources: Vec<RankedSource>,
    pub optimal_selection: Vec<String>, // source IDs
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RankedSource {
    pub source_id: String,
    pub rank: u32,
    pub score: f32,
    pub reason: String,
}

impl Discovery {
    pub fn new(query_id: impl Into<String>) -> Self {
        Discovery {
            id: uuid::Uuid::new_v4().to_string(),
            query_id: query_id.into(),
            discovered_sources: Vec::new(),
            total_available_tokens: 0,
            created_at: chrono::Utc::now(),
        }
    }

    pub fn add_source(mut self, source: DiscoveredSource) -> Self {
        self.total_available_tokens += source.estimated_tokens;
        self.discovered_sources.push(source);
        self
    }

    pub fn source_count(&self) -> usize {
        self.discovered_sources.len()
    }
}

impl DiscoveredSource {
    pub fn new(
        name: impl Into<String>,
        source_type: SourceType,
        relevance: f32,
        estimated_tokens: u32,
    ) -> Self {
        DiscoveredSource {
            id: uuid::Uuid::new_v4().to_string(),
            name: name.into(),
            source_type,
            relevance_score: relevance.max(0.0).min(1.0),
            estimated_tokens,
            freshness_score: 1.0,
            availability: Availability::Available,
        }
    }

    pub fn with_freshness(mut self, score: f32) -> Self {
        self.freshness_score = score.max(0.0).min(1.0);
        self
    }

    pub fn with_availability(mut self, availability: Availability) -> Self {
        self.availability = availability;
        self
    }

    /// Combined score: relevance * freshness
    pub fn quality_score(&self) -> f32 {
        self.relevance_score * self.freshness_score
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_discovery_creation() {
        let discovery = Discovery::new("query_1");
        assert_eq!(discovery.query_id, "query_1");
        assert_eq!(discovery.source_count(), 0);
    }

    #[test]
    fn test_add_sources() {
        let source = DiscoveredSource::new(
            "customers",
            SourceType::Table {
                table_name: "customers".to_string(),
            },
            0.95,
            500,
        );

        let discovery = Discovery::new("q1").add_source(source);
        assert_eq!(discovery.source_count(), 1);
        assert_eq!(discovery.total_available_tokens, 500);
    }

    #[test]
    fn test_source_quality_score() {
        let source = DiscoveredSource::new("test", SourceType::Cache { cache_key: "k".into() }, 0.8, 100)
            .with_freshness(0.9);

        let score = source.quality_score();
        assert!((score - 0.72).abs() < 0.001); // 0.8 * 0.9
    }
}
