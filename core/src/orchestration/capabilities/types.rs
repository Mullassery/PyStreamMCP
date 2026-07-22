use serde::{Deserialize, Serialize};
use std::time::SystemTime;
use super::super::intent::IntentCategory;

/// A capability that an MCP server provides
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct Capability {
    pub name: String,
    pub category: IntentCategory,
    pub keywords: Vec<String>,
    pub domain_expertise: f32, // 0.0-1.0: how expert is this server?
    pub supported_entities: Vec<String>, // robot, database, api, etc.
}

impl Capability {
    pub fn new(
        name: String,
        category: IntentCategory,
        keywords: Vec<String>,
        domain_expertise: f32,
    ) -> Self {
        Self {
            name,
            category,
            keywords,
            domain_expertise,
            supported_entities: vec![],
        }
    }

    pub fn with_entities(mut self, entities: Vec<String>) -> Self {
        self.supported_entities = entities;
        self
    }

    /// Calculate relevance of this capability to a query
    pub fn relevance_to_keywords(&self, query_keywords: &[String]) -> f32 {
        let mut matches = 0;
        for keyword in query_keywords {
            if self.keywords.iter().any(|k| k.contains(keyword)) {
                matches += 1;
            }
        }
        if matches == 0 {
            return 0.0;
        }
        (matches as f32) / (self.keywords.len() as f32)
    }
}

/// Health status of an MCP server
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum ServerHealth {
    Healthy,
    Degraded,
    Unhealthy,
    Unknown,
}

impl ServerHealth {
    pub fn score(&self) -> f32 {
        match self {
            ServerHealth::Healthy => 1.0,
            ServerHealth::Degraded => 0.6,
            ServerHealth::Unhealthy => 0.0,
            ServerHealth::Unknown => 0.5,
        }
    }
}

/// Metadata about server performance
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ServerMetadata {
    pub hostname: String,
    pub port: u16,
    pub latency_avg_ms: f32,
    pub success_rate: f32,  // 0.0-1.0
    pub data_freshness: f32, // 0.0-1.0
    pub cost_per_query_tokens: usize,
    pub max_concurrent_queries: usize,
    pub authentication_required: bool,
    pub ssl_required: bool,
    pub last_health_check: SystemTime,
    pub health: ServerHealth,
    pub uptime_percentage: f32, // 0.0-1.0
}

impl ServerMetadata {
    pub fn new(hostname: String, port: u16) -> Self {
        Self {
            hostname,
            port,
            latency_avg_ms: 0.0,
            success_rate: 0.5,
            data_freshness: 0.5,
            cost_per_query_tokens: 1000,
            max_concurrent_queries: 10,
            authentication_required: false,
            ssl_required: true,
            last_health_check: SystemTime::now(),
            health: ServerHealth::Unknown,
            uptime_percentage: 0.95,
        }
    }

    pub fn latency_score(&self) -> f32 {
        // Prefer lower latency: 100ms = 1.0, 1000ms = 0.1
        (1.0 - (self.latency_avg_ms / 1000.0).min(1.0)).max(0.0)
    }

    pub fn cost_score(&self) -> f32 {
        // Prefer lower cost: 100 tokens = 1.0, 5000 tokens = 0.02
        (1.0 - (self.cost_per_query_tokens as f32 / 5000.0).min(1.0)).max(0.02)
    }
}

impl Default for ServerMetadata {
    fn default() -> Self {
        Self::new("localhost".to_string(), 8080)
    }
}

/// Profile of an MCP server
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MCPServerProfile {
    pub id: String,
    pub name: String,
    pub version: String,
    pub description: String,
    pub capabilities: Vec<Capability>,
    pub metadata: ServerMetadata,
    pub created_at: SystemTime,
    pub last_updated: SystemTime,
}

impl MCPServerProfile {
    pub fn new(
        id: String,
        name: String,
        version: String,
        description: String,
    ) -> Self {
        Self {
            id,
            name,
            version,
            description,
            capabilities: vec![],
            metadata: ServerMetadata::default(),
            created_at: SystemTime::now(),
            last_updated: SystemTime::now(),
        }
    }

    pub fn with_capabilities(mut self, capabilities: Vec<Capability>) -> Self {
        self.capabilities = capabilities;
        self
    }

    pub fn with_metadata(mut self, metadata: ServerMetadata) -> Self {
        self.metadata = metadata;
        self
    }

    pub fn has_capability(&self, name: &str) -> bool {
        self.capabilities.iter().any(|c| c.name == name)
    }

    pub fn capabilities_for_intent(&self, intent: IntentCategory) -> Vec<&Capability> {
        self.capabilities
            .iter()
            .filter(|c| c.category == intent)
            .collect()
    }

    pub fn is_available(&self) -> bool {
        self.metadata.health == ServerHealth::Healthy
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_capability_new() {
        let cap = Capability::new(
            "research".to_string(),
            IntentCategory::Research,
            vec!["papers".to_string(), "academic".to_string()],
            0.9,
        );
        assert_eq!(cap.name, "research");
        assert_eq!(cap.domain_expertise, 0.9);
    }

    #[test]
    fn test_capability_relevance() {
        let cap = Capability::new(
            "research".to_string(),
            IntentCategory::Research,
            vec!["papers".to_string(), "academic".to_string(), "robotics".to_string()],
            0.9,
        );
        let relevance = cap.relevance_to_keywords(&["papers".to_string(), "robotics".to_string()]);
        assert!(relevance > 0.0);
    }

    #[test]
    fn test_server_health_score() {
        assert_eq!(ServerHealth::Healthy.score(), 1.0);
        assert_eq!(ServerHealth::Degraded.score(), 0.6);
        assert_eq!(ServerHealth::Unhealthy.score(), 0.0);
    }

    #[test]
    fn test_server_metadata_latency_score() {
        let mut metadata = ServerMetadata::new("localhost".to_string(), 8080);
        metadata.latency_avg_ms = 100.0;
        assert!(metadata.latency_score() > 0.9);

        metadata.latency_avg_ms = 1000.0;
        assert!(metadata.latency_score() < 0.2);
    }

    #[test]
    fn test_server_profile_has_capability() {
        let profile = MCPServerProfile::new(
            "arxiv".to_string(),
            "Arxiv MCP".to_string(),
            "1.0.0".to_string(),
            "Access Arxiv papers".to_string(),
        ).with_capabilities(vec![
            Capability::new(
                "research".to_string(),
                IntentCategory::Research,
                vec!["papers".to_string()],
                0.9,
            ),
        ]);

        assert!(profile.has_capability("research"));
        assert!(!profile.has_capability("web-search"));
    }

    #[test]
    fn test_server_profile_is_available() {
        let mut profile = MCPServerProfile::new(
            "arxiv".to_string(),
            "Arxiv MCP".to_string(),
            "1.0.0".to_string(),
            "Access Arxiv papers".to_string(),
        );
        profile.metadata.health = ServerHealth::Healthy;
        assert!(profile.is_available());

        profile.metadata.health = ServerHealth::Unhealthy;
        assert!(!profile.is_available());
    }
}
