// Metadata type definitions for Stage 1 filtering

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Source type for metadata ranking
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum SourceType {
    Web,
    Database,
    MCPTool,
}

/// Quality indicators for metadata scoring
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SourceQuality {
    /// Authority/reputation score (0-1)
    pub authority: f64,
    /// Freshness score (0-1, higher = more recent)
    pub freshness: f64,
    /// Accessibility score (0-1, can we access it?)
    pub accessibility: f64,
    /// Cost score (0-1, lower cost = higher score)
    pub cost_efficiency: f64,
    /// Reliability score (0-1, based on history)
    pub reliability: f64,
}

impl SourceQuality {
    /// Compute weighted overall quality score (0-1)
    pub fn overall_score(&self, weights: &QualityWeights) -> f64 {
        (self.authority * weights.authority
            + self.freshness * weights.freshness
            + self.accessibility * weights.accessibility
            + self.cost_efficiency * weights.cost_efficiency
            + self.reliability * weights.reliability)
            / (weights.authority
                + weights.freshness
                + weights.accessibility
                + weights.cost_efficiency
                + weights.reliability)
    }
}

/// Weights for quality score calculation (customizable per query)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QualityWeights {
    pub authority: f64,
    pub freshness: f64,
    pub accessibility: f64,
    pub cost_efficiency: f64,
    pub reliability: f64,
}

impl Default for QualityWeights {
    fn default() -> Self {
        Self {
            authority: 1.0,
            freshness: 1.0,
            accessibility: 1.0,
            cost_efficiency: 0.5,
            reliability: 1.0,
        }
    }
}

/// Web source metadata
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WebMetadata {
    pub url: String,
    pub domain: String,
    /// Last publish date (unix timestamp, 0 if unknown)
    pub publish_timestamp: i64,
    /// Document size in bytes
    pub size_bytes: u64,
    /// Wayback Machine availability (years of history)
    pub wayback_depth_years: u16,
    /// HTTPS/SSL availability
    pub has_ssl: bool,
    /// Domain registration age (years)
    pub domain_age_years: u16,
    /// Topic match score (0-1, based on query keywords)
    pub topic_relevance: f64,
    /// Custom tags (e.g., "documentation", "tutorial", "news")
    pub tags: Vec<String>,
}

/// Database source metadata
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DatabaseMetadata {
    pub name: String,
    pub db_type: String, // "postgres", "mongodb", "bigquery", etc.
    /// Table/collection names
    pub tables: Vec<String>,
    /// Row count estimate (0 if unknown)
    pub row_count: u64,
    /// Last update timestamp (unix, 0 if unknown)
    pub last_update: i64,
    /// Access cost (relative score 0-1)
    pub access_cost: f64,
    /// Column information
    pub columns: Vec<ColumnMetadata>,
    /// Update frequency (hours between updates, 0 if unknown)
    pub update_frequency_hours: u16,
    /// Data quality score (0-1)
    pub quality_score: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ColumnMetadata {
    pub name: String,
    pub col_type: String,
    pub nullable: bool,
    pub cardinality: Option<u64>,
    pub is_indexed: bool,
}

/// MCP Tool metadata
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MCPToolMetadata {
    pub name: String,
    pub description: String,
    /// Input types (e.g., ["text", "url"])
    pub input_types: Vec<String>,
    /// Output types (e.g., ["json", "text"])
    pub output_types: Vec<String>,
    /// Average latency (milliseconds)
    pub avg_latency_ms: u32,
    /// Cost per invocation (relative score 0-1)
    pub cost_per_call: f64,
    /// Success rate from history (0-1)
    pub success_rate: f64,
    /// Capability categories (e.g., "search", "analysis", "transform")
    pub capabilities: Vec<String>,
    /// Required authentication ("none", "api_key", "oauth", etc.)
    pub auth_type: String,
}

/// Generic metadata container
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Metadata {
    Web(WebMetadata),
    Database(DatabaseMetadata),
    MCPTool(MCPToolMetadata),
}

impl Metadata {
    /// Get source type
    pub fn source_type(&self) -> SourceType {
        match self {
            Metadata::Web(_) => SourceType::Web,
            Metadata::Database(_) => SourceType::Database,
            Metadata::MCPTool(_) => SourceType::MCPTool,
        }
    }

    /// Get unique identifier
    pub fn id(&self) -> String {
        match self {
            Metadata::Web(w) => w.url.clone(),
            Metadata::Database(d) => d.name.clone(),
            Metadata::MCPTool(t) => t.name.clone(),
        }
    }

    /// Get quality indicators
    pub fn quality(&self) -> SourceQuality {
        match self {
            Metadata::Web(w) => web_quality(w),
            Metadata::Database(d) => database_quality(d),
            Metadata::MCPTool(t) => tool_quality(t),
        }
    }

    /// Estimate tokens if retrieved
    pub fn estimated_tokens(&self) -> u32 {
        match self {
            // Web: ~0.3 tokens per character
            Metadata::Web(w) => ((w.size_bytes as f64) * 0.3) as u32,
            // Database: varies, estimate 100-1000 per row
            Metadata::Database(d) => {
                std::cmp::min(d.row_count as u32 * 100, 100_000)
            }
            // MCP Tool: typically 500-2000 tokens output
            Metadata::MCPTool(_) => 1000,
        }
    }
}

/// Ranked candidate for retrieval
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RankedCandidate {
    pub metadata: Metadata,
    pub rank: usize,
    /// Score (0-1, higher is better)
    pub score: f64,
    /// Why this candidate was ranked (for explainability)
    pub justification: String,
}

/// OKF-compatible metadata profile (for cataloging)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetadataProfile {
    pub name: String,
    pub description: String,
    pub source_type: SourceType,
    pub metadata: Metadata,
    /// When this profile was last updated
    pub updated_at: i64,
    /// Reliability score based on accuracy
    pub profile_reliability: f64,
    /// Community contributions/reviews
    pub reviews: u32,
}

// Helper functions for quality calculation

fn web_quality(w: &WebMetadata) -> SourceQuality {
    SourceQuality {
        // Authority: SSL, domain age, wayback depth
        authority: (if w.has_ssl { 0.3 } else { 0.0 }
            + (w.domain_age_years as f64 / 20.0).min(0.3)
            + (w.wayback_depth_years as f64 / 10.0).min(0.4))
            .min(1.0),
        // Freshness: based on publish date (recent = higher)
        freshness: if w.publish_timestamp == 0 {
            0.5 // unknown
        } else {
            let now = std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap_or_default()
                .as_secs() as i64;
            let days_old = (now - w.publish_timestamp) / 86400;
            (1.0 - (days_old as f64 / 365.0).min(1.0)).max(0.0)
        },
        // Accessibility: SSL is a proxy
        accessibility: if w.has_ssl { 0.95 } else { 0.7 },
        // Cost efficiency: small documents are efficient
        cost_efficiency: (1.0 - (w.size_bytes as f64 / 1_000_000.0).min(1.0)).max(0.3),
        // Reliability: based on topic relevance
        reliability: w.topic_relevance,
    }
}

fn database_quality(d: &DatabaseMetadata) -> SourceQuality {
    SourceQuality {
        // Authority: data quality score
        authority: d.quality_score,
        // Freshness: based on last update
        freshness: if d.last_update == 0 {
            0.5
        } else {
            let now = std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap_or_default()
                .as_secs() as i64;
            let hours_old = (now - d.last_update) / 3600;
            let max_hours = (d.update_frequency_hours as i64).max(24);
            (1.0 - (hours_old as f64 / max_hours as f64).min(1.0)).max(0.0)
        },
        // Accessibility: always 1.0 if available
        accessibility: 1.0,
        // Cost efficiency: based on access cost
        cost_efficiency: 1.0 - d.access_cost,
        // Reliability: based on quality
        reliability: d.quality_score,
    }
}

fn tool_quality(t: &MCPToolMetadata) -> SourceQuality {
    SourceQuality {
        // Authority: success rate
        authority: t.success_rate,
        // Freshness: assume always current
        freshness: 1.0,
        // Accessibility: based on auth type
        accessibility: match t.auth_type.as_str() {
            "none" => 1.0,
            "api_key" => 0.9,
            "oauth" => 0.8,
            _ => 0.5,
        },
        // Cost efficiency: inverse of cost
        cost_efficiency: 1.0 - t.cost_per_call,
        // Reliability: based on success rate
        reliability: t.success_rate,
    }
}
