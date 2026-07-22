// Metadata Cache - Stage 1 Learning Layer
// Caches filtering decisions for reuse across queries and agents

use crate::metadata::types::*;
use crate::{Error, Result};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;

/// Configuration for metadata cache
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

/// Single cache entry
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CacheEntry {
    /// Cached ranked candidates
    pub ranked_candidates: Vec<RankedCandidate>,
    /// When entry was created (unix timestamp)
    pub created_at: i64,
    /// Number of times this entry was accessed
    pub access_count: u64,
}

impl CacheEntry {
    /// Check if entry is expired
    pub fn is_expired(&self, ttl_seconds: u64) -> bool {
        if ttl_seconds == 0 {
            return false; // No expiry
        }
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs() as i64;
        now - self.created_at > ttl_seconds as i64
    }
}

/// Metadata cache for filtering decisions
pub struct MetadataCache {
    config: CacheConfig,
    entries: Arc<RwLock<HashMap<String, CacheEntry>>>,
    stats: Arc<RwLock<CacheStatistics>>,
}

#[derive(Debug, Clone, Default)]
struct CacheStatistics {
    hits: u64,
    misses: u64,
    evictions: u64,
}

impl MetadataCache {
    /// Create new cache
    pub fn new(config: CacheConfig) -> Result<Self> {
        Ok(Self {
            config,
            entries: Arc::new(RwLock::new(HashMap::new())),
            stats: Arc::new(RwLock::new(CacheStatistics::default())),
        })
    }

    /// Make cache key from query and source type
    pub fn make_key(&self, query: &str, source_type: &SourceType) -> String {
        format!("{}::{:?}", query.to_lowercase(), source_type)
    }

    /// Get cached ranked candidates
    pub async fn get(&self, key: &str) -> Result<Vec<RankedCandidate>> {
        let mut entries = self.entries.write().await;

        if let Some(entry) = entries.get_mut(key) {
            // Check expiry
            if entry.is_expired(self.config.ttl_seconds) {
                entries.remove(key);
                let mut stats = self.stats.write().await;
                stats.misses += 1;
                return Err(Error::Generic("Cache entry expired".to_string()));
            }

            // Update access count and stats
            entry.access_count += 1;
            let mut stats = self.stats.write().await;
            stats.hits += 1;

            return Ok(entry.ranked_candidates.clone());
        }

        let mut stats = self.stats.write().await;
        stats.misses += 1;
        Err(Error::Generic("Cache miss".to_string()))
    }

    /// Set cache entry
    pub async fn set(&self, key: &str, ranked_candidates: Vec<RankedCandidate>) -> Result<()> {
        let mut entries = self.entries.write().await;

        // Check if we need to evict
        if entries.len() >= self.config.max_entries {
            // Simple eviction: remove entry with lowest access count
            if let Some((evict_key, _)) = entries.iter().min_by_key(|(_, v)| v.access_count) {
                entries.remove(evict_key);
                let mut stats = self.stats.write().await;
                stats.evictions += 1;
            }
        }

        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs() as i64;

        entries.insert(
            key.to_string(),
            CacheEntry {
                ranked_candidates,
                created_at: now,
                access_count: 0,
            },
        );

        Ok(())
    }

    /// Clear all cache entries
    pub async fn clear(&self) -> Result<()> {
        self.entries.write().await.clear();
        Ok(())
    }

    /// Get cache statistics
    pub async fn stats(&self) -> Result<CacheStats> {
        let entries = self.entries.read().await;
        let stats = self.stats.read().await;

        let total = stats.hits + stats.misses;
        let hit_rate = if total > 0 {
            (stats.hits as f64) / (total as f64)
        } else {
            0.0
        };

        Ok(CacheStats {
            total_entries: entries.len(),
            hit_count: stats.hits,
            miss_count: stats.misses,
            hit_rate,
        })
    }

    /// Get cache size (number of entries)
    pub async fn size(&self) -> Result<usize> {
        Ok(self.entries.read().await.len())
    }

    /// Get cache memory usage estimate (bytes)
    pub async fn memory_usage(&self) -> Result<usize> {
        let entries = self.entries.read().await;
        let mut usage = 0;

        for (key, entry) in entries.iter() {
            usage += key.len();
            usage += entry.ranked_candidates.len() * 1000; // Estimate per ranked candidate
            usage += 16; // struct overhead
        }

        Ok(usage)
    }
}

/// Cache statistics
#[derive(Debug, Clone)]
pub struct CacheStats {
    pub total_entries: usize,
    pub hit_count: u64,
    pub miss_count: u64,
    pub hit_rate: f64,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_cache_set_get() {
        let config = CacheConfig {
            ttl_seconds: 3600,
            max_entries: 100,
        };
        let cache = MetadataCache::new(config).unwrap();

        let key = "test_query::Web";
        let ranked = vec![RankedCandidate {
            metadata: Metadata::Web(WebMetadata {
                url: "https://example.com".to_string(),
                domain: "example.com".to_string(),
                publish_timestamp: 0,
                size_bytes: 1000,
                wayback_depth_years: 1,
                has_ssl: true,
                domain_age_years: 5,
                topic_relevance: 0.8,
                tags: vec![],
            }),
            rank: 1,
            score: 0.85,
            justification: "test".to_string(),
        }];

        // Set and get
        cache.set(key, ranked.clone()).await.unwrap();
        let retrieved = cache.get(key).await.unwrap();

        assert_eq!(retrieved.len(), 1);
        assert_eq!(retrieved[0].rank, 1);

        // Check stats
        let stats = cache.stats().await.unwrap();
        assert_eq!(stats.hit_count, 1);
        assert_eq!(stats.miss_count, 0);
        assert!(stats.hit_rate > 0.99);
    }

    #[tokio::test]
    async fn test_cache_clear() {
        let config = CacheConfig::default();
        let cache = MetadataCache::new(config).unwrap();

        let key = "test::Web";
        let ranked = vec![];
        cache.set(key, ranked).await.unwrap();
        assert_eq!(cache.size().await.unwrap(), 1);

        cache.clear().await.unwrap();
        assert_eq!(cache.size().await.unwrap(), 0);
    }

    #[tokio::test]
    async fn test_cache_eviction() {
        let config = CacheConfig {
            ttl_seconds: 3600,
            max_entries: 2, // Small cache
        };
        let cache = MetadataCache::new(config).unwrap();

        // Fill cache
        for i in 0..3 {
            let key = format!("query{}::Web", i);
            cache.set(&key, vec![]).await.unwrap();
        }

        // Should have evicted one entry
        let size = cache.size().await.unwrap();
        assert!(size <= 2);

        let stats = cache.stats().await.unwrap();
        assert!(stats.evictions > 0);
    }
}
