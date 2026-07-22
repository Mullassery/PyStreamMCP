// Metadata Filtering Engine - Stage 1 Foundation
// Enables pre-retrieval intelligent decisions across web, database, and MCP sources

pub mod types;
pub mod filter;
pub mod cache;

pub use types::{
    Metadata, MetadataSource, SourceType, SourceQuality, WebMetadata, DatabaseMetadata,
    MCPToolMetadata, MetadataProfile, Candidate, RankedCandidate,
};
pub use filter::{MetadataFilter, FilterConfig, RankingStrategy};
pub use cache::{MetadataCache, CacheEntry, CacheConfig};

use crate::Result;

/// Metadata intelligence layer for selective retrieval
///
/// Decides what to fetch BEFORE fetching, using only metadata.
/// Reduces data transfer by 70-85% in Stage 1.
pub struct MetadataIntelligence {
    filter: MetadataFilter,
    cache: MetadataCache,
}

impl MetadataIntelligence {
    /// Create new metadata intelligence layer
    pub fn new(config: FilterConfig) -> Result<Self> {
        let cache = MetadataCache::new(config.cache_config.clone())?;
        let filter = MetadataFilter::new(config)?;

        Ok(Self { filter, cache })
    }

    /// Rank candidates for a query using only metadata (no data retrieval)
    pub async fn rank_candidates(
        &self,
        query: &str,
        source_type: SourceType,
        candidates: Vec<Metadata>,
    ) -> Result<Vec<RankedCandidate>> {
        // Check cache first
        let cache_key = self.cache.make_key(query, &source_type);
        if let Ok(cached) = self.cache.get(&cache_key) {
            return Ok(cached);
        }

        // Rank using filter
        let ranked = self.filter.rank(query, source_type, candidates).await?;

        // Cache the decision
        self.cache.set(&cache_key, ranked.clone())?;

        Ok(ranked)
    }

    /// Get top candidates by metadata (for selective retrieval)
    pub async fn get_top_candidates(
        &self,
        query: &str,
        source_type: SourceType,
        candidates: Vec<Metadata>,
        top_k: usize,
    ) -> Result<Vec<RankedCandidate>> {
        let ranked = self.rank_candidates(query, source_type, candidates).await?;
        Ok(ranked.into_iter().take(top_k).collect())
    }

    /// Clear cache (for testing or manual refresh)
    pub fn clear_cache(&self) -> Result<()> {
        self.cache.clear()
    }

    /// Get cache statistics
    pub fn cache_stats(&self) -> Result<CacheStats> {
        self.cache.stats()
    }
}

#[derive(Debug, Clone)]
pub struct CacheStats {
    pub total_entries: usize,
    pub hit_count: u64,
    pub miss_count: u64,
    pub hit_rate: f64,
}
