/// PyStreamMCP v0.5 - Metadata Filtering Stage 1 Tests
/// Unit tests for the metadata profile/scoring foundation.

#[cfg(test)]
mod metadata_unit_tests {
    use pystreammcp_core::metadata::*;

    /// Current unix timestamp (seconds), used for freshness-oriented fixtures.
    fn now_ts() -> i64 {
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs() as i64
    }

    // ============ Web Profile Tests ============

    #[test]
    fn test_web_profiles_count() {
        let profiles = WebProfiles::get_profiles();
        assert!(profiles.len() >= 10, "Should have 10+ web domain profiles");
    }

    #[test]
    fn test_github_profile_exists() {
        let profiles = WebProfiles::get_profiles();
        assert!(profiles.contains_key("github.com"));
        let github = &profiles["github.com"];
        assert_eq!(github.domain, "github.com");
        assert!(github.has_ssl);
    }

    #[test]
    fn test_stackoverflow_profile_exists() {
        let profiles = WebProfiles::get_profiles();
        assert!(profiles.contains_key("stackoverflow.com"));
        let so = &profiles["stackoverflow.com"];
        assert!(so.topic_relevance > 0.8);
    }

    #[test]
    fn test_web_profile_scoring() {
        let meta = WebMetadata {
            url: "https://example.com".to_string(),
            domain: "example.com".to_string(),
            publish_timestamp: 0,
            size_bytes: 1024,
            wayback_depth_years: 10,
            has_ssl: true,
            domain_age_years: 5,
            topic_relevance: 0.85,
            tags: vec!["technical".to_string()],
        };

        let score = WebProfiles::score(&meta);
        assert!(score > 0.0 && score <= 1.0);
    }

    #[test]
    fn test_web_high_quality_scores_high() {
        let meta = WebMetadata {
            url: "https://github.com".to_string(),
            domain: "github.com".to_string(),
            publish_timestamp: 0,
            size_bytes: 10000,
            wayback_depth_years: 15,
            has_ssl: true,
            domain_age_years: 15,
            topic_relevance: 0.95,
            tags: vec!["source-code".to_string()],
        };

        let score = WebProfiles::score(&meta);
        assert!(score > 0.85, "GitHub should score as high-quality");
    }

    #[test]
    fn test_web_no_ssl_penalizes_score() {
        let with_ssl = WebMetadata {
            url: "https://example.com".to_string(),
            domain: "example.com".to_string(),
            publish_timestamp: 0,
            size_bytes: 1024,
            wayback_depth_years: 5,
            has_ssl: true,
            domain_age_years: 5,
            topic_relevance: 0.75,
            tags: vec![],
        };

        let without_ssl = WebMetadata {
            url: "http://example.com".to_string(),
            domain: "example.com".to_string(),
            publish_timestamp: 0,
            size_bytes: 1024,
            wayback_depth_years: 5,
            has_ssl: false,
            domain_age_years: 5,
            topic_relevance: 0.75,
            tags: vec![],
        };

        let score_with = WebProfiles::score(&with_ssl);
        let score_without = WebProfiles::score(&without_ssl);
        assert!(score_with > score_without);
    }

    #[test]
    fn test_web_freshness_scoring() {
        let recent = WebMetadata {
            url: "https://news.example.com".to_string(),
            domain: "news.example.com".to_string(),
            publish_timestamp: now_ts(),
            size_bytes: 1024,
            wayback_depth_years: 1,
            has_ssl: true,
            domain_age_years: 2,
            topic_relevance: 0.75,
            tags: vec!["news".to_string()],
        };

        let score = WebProfiles::score(&recent);
        assert!(score > 0.6, "Recent content should score reasonably");
    }

    #[test]
    fn test_web_profile_tags() {
        let profiles = WebProfiles::get_profiles();
        let github = &profiles["github.com"];
        assert!(!github.tags.is_empty());
        assert!(github.tags.iter().any(|t| t.contains("source")));
    }

    #[test]
    fn test_web_domain_authority_varied() {
        let profiles = WebProfiles::get_profiles();
        let mut scores = profiles.values().map(WebProfiles::score).collect::<Vec<_>>();
        scores.sort_by(|a, b| a.partial_cmp(b).unwrap());

        // Scores should be varied (not all the same)
        let min = scores.first().copied().unwrap_or(0.0);
        let max = scores.last().copied().unwrap_or(1.0);
        assert!(max - min > 0.1, "Should have varied domain quality scores");
    }

    #[test]
    fn test_official_documentation_highest_scores() {
        let profiles = WebProfiles::get_profiles();
        let python_score = profiles
            .get("python.org")
            .map(WebProfiles::score)
            .unwrap_or(0.0);
        let medium_score = profiles
            .get("medium.com")
            .map(WebProfiles::score)
            .unwrap_or(0.0);

        assert!(
            python_score > medium_score,
            "Official docs should score higher than blogs"
        );
    }

    // ============ Database Profile Tests ============

    #[test]
    fn test_database_profiles_count() {
        let profiles = DatabaseProfiles::get_profiles();
        assert!(profiles.len() >= 3, "Should have 3+ database profiles");
    }

    #[test]
    fn test_postgres_profile_exists() {
        let profiles = DatabaseProfiles::get_profiles();
        assert!(profiles.contains_key("public_postgres"));
        let pg = &profiles["public_postgres"];
        assert_eq!(pg.db_type, "postgres");
    }

    #[test]
    fn test_mongodb_profile_exists() {
        let profiles = DatabaseProfiles::get_profiles();
        assert!(profiles.contains_key("mongodb_main"));
        let mongo = &profiles["mongodb_main"];
        assert_eq!(mongo.db_type, "mongodb");
        assert!(mongo.row_count > 0);
    }

    #[test]
    fn test_bigquery_profile_exists() {
        let profiles = DatabaseProfiles::get_profiles();
        assert!(profiles.contains_key("bigquery_analytics"));
        let bq = &profiles["bigquery_analytics"];
        assert_eq!(bq.db_type, "bigquery");
        assert!(bq.quality_score > 0.9);
    }

    #[test]
    fn test_database_scoring() {
        let meta = DatabaseMetadata {
            name: "test_db".to_string(),
            db_type: "postgres".to_string(),
            tables: vec!["users".to_string(), "posts".to_string()],
            row_count: 1_000_000,
            last_update: now_ts(),
            access_cost: 0.01,
            columns: vec![],
            update_frequency_hours: 24,
            quality_score: 0.90,
        };

        let score = DatabaseProfiles::score(&meta);
        assert!(score > 0.0 && score <= 1.0);
    }

    #[test]
    fn test_database_postgres_preferred() {
        let profiles = DatabaseProfiles::get_profiles();
        let pg_score = profiles
            .get("public_postgres")
            .map(DatabaseProfiles::score)
            .unwrap_or(0.0);
        let mongo_score = profiles
            .get("mongodb_main")
            .map(DatabaseProfiles::score)
            .unwrap_or(0.0);

        assert!(pg_score > mongo_score, "PostgreSQL should score higher");
    }

    #[test]
    fn test_database_freshness_matters() {
        let recent = DatabaseMetadata {
            name: "recent".to_string(),
            db_type: "postgres".to_string(),
            tables: vec!["data".to_string()],
            row_count: 100_000,
            last_update: now_ts(),
            access_cost: 0.01,
            columns: vec![],
            update_frequency_hours: 24,
            quality_score: 0.90,
        };

        let old = DatabaseMetadata {
            name: "old".to_string(),
            db_type: "postgres".to_string(),
            tables: vec!["data".to_string()],
            row_count: 100_000,
            last_update: now_ts() - (7 * 24 * 3600), // 7 days ago
            access_cost: 0.01,
            columns: vec![],
            update_frequency_hours: 24,
            quality_score: 0.90,
        };

        let recent_score = DatabaseProfiles::score(&recent);
        let old_score = DatabaseProfiles::score(&old);
        assert!(recent_score > old_score, "Recent data should score higher");
    }

    #[test]
    fn test_database_quality_matters() {
        let high_quality = DatabaseMetadata {
            name: "reliable".to_string(),
            db_type: "postgres".to_string(),
            tables: vec![],
            row_count: 0,
            last_update: 0,
            access_cost: 0.01,
            columns: vec![],
            update_frequency_hours: 24,
            quality_score: 0.95,
        };

        let low_quality = DatabaseMetadata {
            name: "flaky".to_string(),
            db_type: "postgres".to_string(),
            tables: vec![],
            row_count: 0,
            last_update: 0,
            access_cost: 0.01,
            columns: vec![],
            update_frequency_hours: 24,
            quality_score: 0.60,
        };

        let high_score = DatabaseProfiles::score(&high_quality);
        let low_score = DatabaseProfiles::score(&low_quality);
        assert!(high_score > low_score);
    }

    #[test]
    fn test_database_cost_consideration() {
        let cheap = DatabaseMetadata {
            name: "cheap".to_string(),
            db_type: "postgres".to_string(),
            tables: vec![],
            row_count: 0,
            last_update: 0,
            access_cost: 0.001,
            columns: vec![],
            update_frequency_hours: 24,
            quality_score: 0.90,
        };

        let expensive = DatabaseMetadata {
            name: "expensive".to_string(),
            db_type: "postgres".to_string(),
            tables: vec![],
            row_count: 0,
            last_update: 0,
            access_cost: 1.0,
            columns: vec![],
            update_frequency_hours: 24,
            quality_score: 0.90,
        };

        let cheap_score = DatabaseProfiles::score(&cheap);
        let expensive_score = DatabaseProfiles::score(&expensive);
        assert!(cheap_score > expensive_score, "Cheaper should score higher");
    }

    // ============ MCP Tool Profile Tests ============

    #[test]
    fn test_mcp_tool_profiles_count() {
        let profiles = MCPToolProfiles::get_profiles();
        assert!(profiles.len() >= 3, "Should have 3+ MCP tool profiles");
    }

    #[test]
    fn test_search_tool_profile_exists() {
        let profiles = MCPToolProfiles::get_profiles();
        assert!(profiles.contains_key("search_tool"));
        let search = &profiles["search_tool"];
        assert_eq!(search.capabilities.first().map(|s| s.as_str()), Some("search"));
    }

    #[test]
    fn test_database_query_tool_exists() {
        let profiles = MCPToolProfiles::get_profiles();
        assert!(profiles.contains_key("database_query"));
        let db = &profiles["database_query"];
        assert_ne!(db.auth_type, "none");
        assert!(db.cost_per_call > 0.0);
    }

    #[test]
    fn test_mcp_tool_scoring() {
        let meta = MCPToolMetadata {
            name: "test_tool".to_string(),
            description: "A test tool".to_string(),
            input_types: vec!["text".to_string()],
            output_types: vec!["json".to_string()],
            avg_latency_ms: 500,
            cost_per_call: 0.01,
            success_rate: 0.95,
            capabilities: vec!["search".to_string()],
            auth_type: "none".to_string(),
        };

        let score = MCPToolProfiles::score(&meta);
        assert!(score > 0.0 && score <= 1.0);
    }

    #[test]
    fn test_mcp_tool_reliability_matters() {
        let reliable = MCPToolMetadata {
            name: "reliable".to_string(),
            description: "Reliable tool".to_string(),
            input_types: vec!["text".to_string()],
            output_types: vec!["json".to_string()],
            avg_latency_ms: 500,
            cost_per_call: 0.01,
            success_rate: 0.99,
            capabilities: vec!["search".to_string()],
            auth_type: "none".to_string(),
        };

        let unreliable = MCPToolMetadata {
            name: "unreliable".to_string(),
            description: "Unreliable tool".to_string(),
            input_types: vec!["text".to_string()],
            output_types: vec!["json".to_string()],
            avg_latency_ms: 500,
            cost_per_call: 0.01,
            success_rate: 0.70,
            capabilities: vec!["search".to_string()],
            auth_type: "none".to_string(),
        };

        let reliable_score = MCPToolProfiles::score(&reliable);
        let unreliable_score = MCPToolProfiles::score(&unreliable);
        assert!(reliable_score > unreliable_score);
    }

    #[test]
    fn test_mcp_tool_capability_matters() {
        let high_value = MCPToolMetadata {
            name: "query".to_string(),
            description: "Query tool".to_string(),
            input_types: vec!["sql".to_string()],
            output_types: vec!["json".to_string()],
            avg_latency_ms: 500,
            cost_per_call: 0.05,
            success_rate: 0.95,
            capabilities: vec!["query".to_string()],
            auth_type: "api_key".to_string(),
        };

        let lower_value = MCPToolMetadata {
            name: "classify".to_string(),
            description: "Classification tool".to_string(),
            input_types: vec!["text".to_string()],
            output_types: vec!["json".to_string()],
            avg_latency_ms: 500,
            cost_per_call: 0.05,
            success_rate: 0.95,
            capabilities: vec!["classification".to_string()],
            auth_type: "api_key".to_string(),
        };

        let high_score = MCPToolProfiles::score(&high_value);
        let lower_score = MCPToolProfiles::score(&lower_value);
        assert!(high_score > lower_score);
    }

    #[test]
    fn test_mcp_tool_latency_preference() {
        let fast = MCPToolMetadata {
            name: "fast".to_string(),
            description: "Fast tool".to_string(),
            input_types: vec!["json".to_string()],
            output_types: vec!["json".to_string()],
            avg_latency_ms: 50,
            cost_per_call: 0.001,
            success_rate: 0.99,
            capabilities: vec!["parse".to_string()],
            auth_type: "none".to_string(),
        };

        let slow = MCPToolMetadata {
            name: "slow".to_string(),
            description: "Slow tool".to_string(),
            input_types: vec!["json".to_string()],
            output_types: vec!["json".to_string()],
            avg_latency_ms: 5000,
            cost_per_call: 0.001,
            success_rate: 0.99,
            capabilities: vec!["parse".to_string()],
            auth_type: "none".to_string(),
        };

        let fast_score = MCPToolProfiles::score(&fast);
        let slow_score = MCPToolProfiles::score(&slow);
        assert!(fast_score > slow_score, "Faster tools should score higher");
    }

    #[test]
    fn test_mcp_tool_cost_preference() {
        let cheap = MCPToolMetadata {
            name: "cheap".to_string(),
            description: "Cheap tool".to_string(),
            input_types: vec!["text".to_string()],
            output_types: vec!["json".to_string()],
            avg_latency_ms: 500,
            cost_per_call: 0.001,
            success_rate: 0.95,
            capabilities: vec!["search".to_string()],
            auth_type: "none".to_string(),
        };

        let expensive = MCPToolMetadata {
            name: "expensive".to_string(),
            description: "Expensive tool".to_string(),
            input_types: vec!["text".to_string()],
            output_types: vec!["json".to_string()],
            avg_latency_ms: 500,
            cost_per_call: 0.50,
            success_rate: 0.95,
            capabilities: vec!["search".to_string()],
            auth_type: "none".to_string(),
        };

        let cheap_score = MCPToolProfiles::score(&cheap);
        let expensive_score = MCPToolProfiles::score(&expensive);
        assert!(cheap_score > expensive_score);
    }

    #[test]
    fn test_mcp_database_tool_preferred() {
        let profiles = MCPToolProfiles::get_profiles();
        let db_score = profiles
            .get("database_query")
            .map(MCPToolProfiles::score)
            .unwrap_or(0.0);
        let search_score = profiles
            .get("search_tool")
            .map(MCPToolProfiles::score)
            .unwrap_or(0.0);

        assert!(db_score > search_score, "Database tools should score higher");
    }

    // ============ Cross-profile Comparison Tests ============

    #[test]
    fn test_profile_scoring_consistency() {
        let web = WebMetadata {
            url: "https://example.com".to_string(),
            domain: "example.com".to_string(),
            publish_timestamp: 0,
            size_bytes: 1024,
            wayback_depth_years: 10,
            has_ssl: true,
            domain_age_years: 5,
            topic_relevance: 0.85,
            tags: vec![],
        };

        let db = DatabaseMetadata {
            name: "test".to_string(),
            db_type: "postgres".to_string(),
            tables: vec![],
            row_count: 100_000,
            last_update: 0,
            access_cost: 0.01,
            columns: vec![],
            update_frequency_hours: 24,
            quality_score: 0.90,
        };

        let tool = MCPToolMetadata {
            name: "test".to_string(),
            description: "Database tool".to_string(),
            input_types: vec!["sql".to_string()],
            output_types: vec!["json".to_string()],
            avg_latency_ms: 200,
            cost_per_call: 0.05,
            success_rate: 0.98,
            capabilities: vec!["query".to_string()],
            auth_type: "api_key".to_string(),
        };

        let web_score = WebProfiles::score(&web);
        let db_score = DatabaseProfiles::score(&db);
        let tool_score = MCPToolProfiles::score(&tool);

        assert!(web_score > 0.0);
        assert!(db_score > 0.0);
        assert!(tool_score > 0.0);
    }
}
