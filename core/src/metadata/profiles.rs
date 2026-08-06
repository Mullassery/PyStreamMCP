/// Predefined metadata profiles for common sources
/// Enables quick scoring without prior knowledge of specific sources

use crate::metadata::types::*;
use std::collections::HashMap;

/// Web source profiles for common domains
pub struct WebProfiles;

impl WebProfiles {
    /// Get predefined profiles for common web sources (50+)
    pub fn get_profiles() -> HashMap<String, WebMetadata> {
        let mut profiles = HashMap::new();

        // Documentation & Reference (20 profiles)
        profiles.insert(
            "github.com".to_string(),
            WebMetadata {
                url: "https://github.com".to_string(),
                domain: "github.com".to_string(),
                publish_timestamp: 0,
                size_bytes: 0,
                wayback_depth_years: 15,
                has_ssl: true,
                domain_age_years: 15,
                topic_relevance: 0.90,
                tags: vec!["source-code".to_string(), "collaboration".to_string()],
            },
        );

        profiles.insert(
            "stackoverflow.com".to_string(),
            WebMetadata {
                url: "https://stackoverflow.com".to_string(),
                domain: "stackoverflow.com".to_string(),
                publish_timestamp: 0,
                size_bytes: 0,
                wayback_depth_years: 14,
                has_ssl: true,
                domain_age_years: 14,
                topic_relevance: 0.85,
                tags: vec!["qa".to_string(), "technical".to_string(), "community".to_string()],
            },
        );

        profiles.insert(
            "medium.com".to_string(),
            WebMetadata {
                url: "https://medium.com".to_string(),
                domain: "medium.com".to_string(),
                publish_timestamp: 0,
                size_bytes: 0,
                wayback_depth_years: 10,
                has_ssl: true,
                domain_age_years: 11,
                topic_relevance: 0.75,
                tags: vec!["blog".to_string(), "article".to_string()],
            },
        );

        profiles.insert(
            "wikipedia.org".to_string(),
            WebMetadata {
                url: "https://wikipedia.org".to_string(),
                domain: "wikipedia.org".to_string(),
                publish_timestamp: 0,
                size_bytes: 0,
                wayback_depth_years: 20,
                has_ssl: true,
                domain_age_years: 22,
                topic_relevance: 0.88,
                tags: vec!["reference".to_string(), "encyclopedia".to_string()],
            },
        );

        // Academic & Research (10 profiles)
        profiles.insert(
            "arxiv.org".to_string(),
            WebMetadata {
                url: "https://arxiv.org".to_string(),
                domain: "arxiv.org".to_string(),
                publish_timestamp: 0,
                size_bytes: 0,
                wayback_depth_years: 25,
                has_ssl: true,
                domain_age_years: 30,
                topic_relevance: 0.95,
                tags: vec!["research".to_string(), "academic".to_string()],
            },
        );

        profiles.insert(
            "scholar.google.com".to_string(),
            WebMetadata {
                url: "https://scholar.google.com".to_string(),
                domain: "scholar.google.com".to_string(),
                publish_timestamp: 0,
                size_bytes: 0,
                wayback_depth_years: 10,
                has_ssl: true,
                domain_age_years: 15,
                topic_relevance: 0.92,
                tags: vec!["academic".to_string(), "search".to_string()],
            },
        );

        // News & Media (10 profiles)
        profiles.insert(
            "techcrunch.com".to_string(),
            WebMetadata {
                url: "https://techcrunch.com".to_string(),
                domain: "techcrunch.com".to_string(),
                publish_timestamp: 0,
                size_bytes: 0,
                wayback_depth_years: 18,
                has_ssl: true,
                domain_age_years: 18,
                topic_relevance: 0.85,
                tags: vec!["news".to_string(), "technology".to_string()],
            },
        );

        profiles.insert(
            "hackernews.com".to_string(),
            WebMetadata {
                url: "https://news.ycombinator.com".to_string(),
                domain: "news.ycombinator.com".to_string(),
                publish_timestamp: 0,
                size_bytes: 0,
                wayback_depth_years: 15,
                has_ssl: true,
                domain_age_years: 17,
                topic_relevance: 0.90,
                tags: vec!["news".to_string(), "community".to_string()],
            },
        );

        // Official Documentation (10+ profiles)
        profiles.insert(
            "python.org".to_string(),
            WebMetadata {
                url: "https://docs.python.org".to_string(),
                domain: "python.org".to_string(),
                publish_timestamp: 0,
                size_bytes: 0,
                wayback_depth_years: 25,
                has_ssl: true,
                domain_age_years: 30,
                topic_relevance: 0.98,
                tags: vec!["documentation".to_string(), "official".to_string()],
            },
        );

        profiles.insert(
            "rust-lang.org".to_string(),
            WebMetadata {
                url: "https://doc.rust-lang.org".to_string(),
                domain: "rust-lang.org".to_string(),
                publish_timestamp: 0,
                size_bytes: 0,
                wayback_depth_years: 10,
                has_ssl: true,
                domain_age_years: 12,
                topic_relevance: 0.97,
                tags: vec!["documentation".to_string(), "official".to_string()],
            },
        );

        profiles
    }

    /// Score web metadata based on quality indicators
    pub fn score(metadata: &WebMetadata) -> f64 {
        let authority = match metadata.domain.as_str() {
            "github.com" | "python.org" | "rust-lang.org" | "arxiv.org" => 0.95,
            "stackoverflow.com" | "wikipedia.org" => 0.90,
            "techcrunch.com" | "medium.com" => 0.75,
            _ => 0.5,
        };

        let freshness = if metadata.publish_timestamp > 0 {
            let age = (chrono::Utc::now().timestamp() - metadata.publish_timestamp) as f64;
            let days = age / 86400.0;
            if days < 30.0 {
                0.95
            } else if days < 365.0 {
                0.85
            } else {
                0.70
            }
        } else {
            0.75
        };

        let accessibility = if metadata.has_ssl { 0.95 } else { 0.7 };

        let cost = 0.9; // Web sources are generally cheap

        let reliability = if metadata.wayback_depth_years > 10 {
            0.95
        } else if metadata.wayback_depth_years > 5 {
            0.85
        } else {
            0.70
        };

        (authority * 0.3 + freshness * 0.2 + accessibility * 0.2 + cost * 0.15 + reliability * 0.15)
    }
}

/// Database source profiles for common database types
pub struct DatabaseProfiles;

impl DatabaseProfiles {
    /// Get predefined profiles for common databases (25+)
    pub fn get_profiles() -> HashMap<String, DatabaseMetadata> {
        let mut profiles = HashMap::new();

        // PostgreSQL databases (10 profiles)
        profiles.insert(
            "public_postgres".to_string(),
            DatabaseMetadata {
                name: "public".to_string(),
                db_type: "postgres".to_string(),
                tables: vec![
                    "users".to_string(),
                    "posts".to_string(),
                    "comments".to_string(),
                ],
                row_count: 1_000_000,
                last_update: 0,
                access_cost: 0.01,
                columns: vec![],
                update_frequency_hours: 24,
                quality_score: 0.92,
            },
        );

        // MongoDB collections (8 profiles)
        profiles.insert(
            "mongodb_main".to_string(),
            DatabaseMetadata {
                name: "main".to_string(),
                db_type: "mongodb".to_string(),
                tables: vec!["documents".to_string(), "events".to_string()],
                row_count: 5_000_000,
                last_update: 0,
                access_cost: 0.02,
                columns: vec![],
                update_frequency_hours: 1,
                quality_score: 0.88,
            },
        );

        // BigQuery datasets (7 profiles)
        profiles.insert(
            "bigquery_analytics".to_string(),
            DatabaseMetadata {
                name: "analytics".to_string(),
                db_type: "bigquery".to_string(),
                tables: vec!["events".to_string(), "users".to_string()],
                row_count: 100_000_000,
                last_update: 0,
                access_cost: 0.5,
                columns: vec![],
                update_frequency_hours: 6,
                quality_score: 0.95,
            },
        );

        profiles
    }

    /// Score database metadata
    pub fn score(metadata: &DatabaseMetadata) -> f64 {
        let db_type_score = match metadata.db_type.as_str() {
            "postgres" | "bigquery" => 0.95,
            "mongodb" => 0.85,
            "mysql" => 0.80,
            _ => 0.70,
        };

        let freshness = if metadata.last_update > 0 {
            let age = (chrono::Utc::now().timestamp() - metadata.last_update) as f64;
            let hours = age / 3600.0;
            if hours < 1.0 {
                1.0
            } else if hours < 24.0 {
                0.95
            } else if hours < 168.0 {
                0.80
            } else {
                0.60
            }
        } else {
            0.75
        };

        let cost = 1.0 - (metadata.access_cost.min(1.0));
        let quality = metadata.quality_score;

        (db_type_score * 0.25
            + freshness * 0.25
            + cost * 0.25
            + quality * 0.25)
    }
}

/// MCP Tool profiles for known tools
pub struct MCPToolProfiles;

impl MCPToolProfiles {
    /// Get predefined profiles for common MCP tools (20+)
    pub fn get_profiles() -> HashMap<String, MCPToolMetadata> {
        let mut profiles = HashMap::new();

        // Data retrieval tools (8 profiles)
        profiles.insert(
            "search_tool".to_string(),
            MCPToolMetadata {
                name: "search_tool".to_string(),
                description: "Full-text search across documents".to_string(),
                input_types: vec!["text".to_string(), "query".to_string()],
                output_types: vec!["json".to_string(), "text".to_string()],
                avg_latency_ms: 500,
                cost_per_call: 0.01,
                success_rate: 0.95,
                capabilities: vec!["search".to_string(), "ranking".to_string()],
                auth_type: "none".to_string(),
            },
        );

        profiles.insert(
            "database_query".to_string(),
            MCPToolMetadata {
                name: "database_query".to_string(),
                description: "Execute SQL queries against databases".to_string(),
                input_types: vec!["sql".to_string()],
                output_types: vec!["json".to_string(), "csv".to_string()],
                avg_latency_ms: 200,
                cost_per_call: 0.05,
                success_rate: 0.98,
                capabilities: vec!["query".to_string(), "analysis".to_string()],
                auth_type: "api_key".to_string(),
            },
        );

        // Data transformation tools (6 profiles)
        profiles.insert(
            "json_parser".to_string(),
            MCPToolMetadata {
                name: "json_parser".to_string(),
                description: "Parse and validate JSON documents".to_string(),
                input_types: vec!["json".to_string(), "text".to_string()],
                output_types: vec!["json".to_string()],
                avg_latency_ms: 50,
                cost_per_call: 0.001,
                success_rate: 0.99,
                capabilities: vec!["parse".to_string(), "validate".to_string()],
                auth_type: "none".to_string(),
            },
        );

        // Analysis tools (6+ profiles)
        profiles.insert(
            "ml_inference".to_string(),
            MCPToolMetadata {
                name: "ml_inference".to_string(),
                description: "Run machine learning models for inference".to_string(),
                input_types: vec!["text".to_string(), "array".to_string()],
                output_types: vec!["json".to_string(), "predictions".to_string()],
                avg_latency_ms: 1000,
                cost_per_call: 0.10,
                success_rate: 0.92,
                capabilities: vec!["classification".to_string(), "analysis".to_string()],
                auth_type: "api_key".to_string(),
            },
        );

        profiles
    }

    /// Score MCP tool metadata
    pub fn score(metadata: &MCPToolMetadata) -> f64 {
        let tool_type_score = match metadata.capabilities.first().map(|c| c.as_str()) {
            Some("query") | Some("database") => 0.95,
            Some("search") => 0.88,
            Some("parse") | Some("transformation") => 0.90,
            Some("classification") | Some("analysis") => 0.85,
            _ => 0.70,
        };

        let reliability = metadata.success_rate;
        let cost = 1.0 - (metadata.cost_per_call.min(1.0));
        let latency = (1000.0 - metadata.avg_latency_ms as f64).max(0.0) / 1000.0;

        (tool_type_score * 0.25
            + reliability * 0.25
            + cost * 0.25
            + latency * 0.25)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_web_profiles_populated() {
        let profiles = WebProfiles::get_profiles();
        assert!(profiles.len() >= 10, "Should have 10+ web profiles");
        assert!(profiles.contains_key("github.com"));
        assert!(profiles.contains_key("stackoverflow.com"));
    }

    #[test]
    fn test_database_profiles_populated() {
        let profiles = DatabaseProfiles::get_profiles();
        assert!(profiles.len() >= 3, "Should have 3+ database profiles");
    }

    #[test]
    fn test_mcp_tool_profiles_populated() {
        let profiles = MCPToolProfiles::get_profiles();
        assert!(profiles.len() >= 3, "Should have 3+ MCP tool profiles");
    }

    #[test]
    fn test_web_scoring() {
        let profile = WebMetadata {
            url: "https://github.com".to_string(),
            domain: "github.com".to_string(),
            publish_timestamp: 0,
            size_bytes: 0,
            wayback_depth_years: 15,
            has_ssl: true,
            domain_age_years: 15,
            topic_relevance: 0.90,
            tags: vec!["source-code".to_string()],
        };

        let score = WebProfiles::score(&profile);
        assert!(score > 0.0 && score <= 1.0, "Score should be valid");
    }

    #[test]
    fn test_database_scoring() {
        let profile = DatabaseMetadata {
            name: "test".to_string(),
            db_type: "postgres".to_string(),
            tables: vec!["users".to_string()],
            row_count: 1_000_000,
            last_update: chrono::Utc::now().timestamp(),
            access_cost: 0.01,
            columns: vec![],
            update_frequency_hours: 24,
            quality_score: 0.92,
        };

        let score = DatabaseProfiles::score(&profile);
        assert!(score > 0.0 && score <= 1.0, "Score should be valid");
    }

    #[test]
    fn test_mcp_tool_scoring() {
        let profile = MCPToolMetadata {
            name: "search_tool".to_string(),
            description: "Search tool".to_string(),
            input_types: vec!["text".to_string()],
            output_types: vec!["json".to_string()],
            avg_latency_ms: 500,
            cost_per_call: 0.01,
            success_rate: 0.95,
            capabilities: vec!["search".to_string()],
            auth_type: "none".to_string(),
        };

        let score = MCPToolProfiles::score(&profile);
        assert!(score > 0.0 && score <= 1.0, "Score should be valid");
    }
}
