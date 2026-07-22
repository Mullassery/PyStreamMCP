use std::collections::HashMap;
use super::types::{Capability, MCPServerProfile, ServerHealth};
use super::super::intent::IntentCategory;

/// Query for finding servers by capabilities
#[derive(Debug, Clone)]
pub struct CapabilityQuery {
    pub intent: IntentCategory,
    pub required_capabilities: Vec<String>,
    pub min_success_rate: f32,
    pub min_domain_expertise: f32,
    pub must_be_available: bool,
}

impl CapabilityQuery {
    pub fn new(intent: IntentCategory) -> Self {
        Self {
            intent,
            required_capabilities: vec![],
            min_success_rate: 0.5,
            min_domain_expertise: 0.3,
            must_be_available: false,
        }
    }

    pub fn with_capabilities(mut self, capabilities: Vec<String>) -> Self {
        self.required_capabilities = capabilities;
        self
    }

    pub fn with_min_success_rate(mut self, rate: f32) -> Self {
        self.min_success_rate = rate;
        self
    }

    pub fn with_min_expertise(mut self, expertise: f32) -> Self {
        self.min_domain_expertise = expertise;
        self
    }

    pub fn available_only(mut self) -> Self {
        self.must_be_available = true;
        self
    }
}

/// Registry of all MCP servers and their capabilities
pub struct CapabilityRegistry {
    servers: HashMap<String, MCPServerProfile>,
    intent_index: HashMap<IntentCategory, Vec<String>>, // Intent -> server_ids
    capability_index: HashMap<String, Vec<String>>,      // Capability name -> server_ids
}

impl CapabilityRegistry {
    pub fn new() -> Self {
        Self {
            servers: HashMap::new(),
            intent_index: HashMap::new(),
            capability_index: HashMap::new(),
        }
    }

    /// Register a new MCP server
    pub fn register(&mut self, profile: MCPServerProfile) {
        let server_id = profile.id.clone();

        // Index by intent
        for capability in &profile.capabilities {
            self.intent_index
                .entry(capability.category)
                .or_insert_with(Vec::new)
                .push(server_id.clone());

            // Index by capability name
            self.capability_index
                .entry(capability.name.clone())
                .or_insert_with(Vec::new)
                .push(server_id.clone());
        }

        self.servers.insert(server_id, profile);
    }

    /// Find servers for an intent
    pub fn find_by_intent(&self, intent: IntentCategory) -> Vec<MCPServerProfile> {
        self.intent_index
            .get(&intent)
            .map(|ids| {
                ids.iter()
                    .filter_map(|id| self.servers.get(id).cloned())
                    .collect()
            })
            .unwrap_or_default()
    }

    /// Find servers with specific capability
    pub fn find_by_capability(&self, capability_name: &str) -> Vec<MCPServerProfile> {
        self.capability_index
            .get(capability_name)
            .map(|ids| {
                ids.iter()
                    .filter_map(|id| self.servers.get(id).cloned())
                    .collect()
            })
            .unwrap_or_default()
    }

    /// Execute a complex query
    pub fn query(&self, query: CapabilityQuery) -> Vec<MCPServerProfile> {
        let mut candidates = self.find_by_intent(query.intent);

        // Filter by required capabilities
        if !query.required_capabilities.is_empty() {
            candidates.retain(|server| {
                query
                    .required_capabilities
                    .iter()
                    .all(|req| server.has_capability(req))
            });
        }

        // Filter by success rate
        candidates.retain(|server| server.metadata.success_rate >= query.min_success_rate);

        // Filter by domain expertise
        candidates.retain(|server| {
            server
                .capabilities
                .iter()
                .any(|c| c.domain_expertise >= query.min_domain_expertise)
        });

        // Filter by availability
        if query.must_be_available {
            candidates.retain(|server| server.is_available());
        }

        candidates
    }

    /// Get a server by ID
    pub fn get(&self, server_id: &str) -> Option<MCPServerProfile> {
        self.servers.get(server_id).cloned()
    }

    /// Update server metadata (health, performance, etc.)
    pub fn update_health(&mut self, server_id: &str, health: ServerHealth) {
        if let Some(server) = self.servers.get_mut(server_id) {
            server.metadata.health = health;
            server.last_updated = std::time::SystemTime::now();
        }
    }

    /// Update server success rate
    pub fn record_success(&mut self, server_id: &str) {
        if let Some(server) = self.servers.get_mut(server_id) {
            let current = server.metadata.success_rate;
            server.metadata.success_rate = (current * 0.99 + 1.0 * 0.01).min(1.0);
            server.last_updated = std::time::SystemTime::now();
        }
    }

    /// Record a failure
    pub fn record_failure(&mut self, server_id: &str) {
        if let Some(server) = self.servers.get_mut(server_id) {
            let current = server.metadata.success_rate;
            server.metadata.success_rate = (current * 0.99).max(0.0);
            server.last_updated = std::time::SystemTime::now();
        }
    }

    /// Get all servers
    pub fn all(&self) -> Vec<MCPServerProfile> {
        self.servers.values().cloned().collect()
    }

    /// Get server count
    pub fn count(&self) -> usize {
        self.servers.len()
    }

    /// List all intents that have registered servers
    pub fn supported_intents(&self) -> Vec<IntentCategory> {
        self.intent_index.keys().cloned().collect()
    }
}

impl Default for CapabilityRegistry {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn create_test_server(id: &str, intent: IntentCategory) -> MCPServerProfile {
        MCPServerProfile::new(
            id.to_string(),
            format!("{} MCP", id),
            "1.0.0".to_string(),
            format!("Test server for {}", id),
        )
        .with_capabilities(vec![Capability::new(
            "test".to_string(),
            intent,
            vec!["test".to_string()],
            0.8,
        )])
    }

    #[test]
    fn test_registry_register() {
        let mut registry = CapabilityRegistry::new();
        let server = create_test_server("arxiv", IntentCategory::Research);
        registry.register(server);

        assert_eq!(registry.count(), 1);
    }

    #[test]
    fn test_registry_find_by_intent() {
        let mut registry = CapabilityRegistry::new();
        registry.register(create_test_server("arxiv", IntentCategory::Research));
        registry.register(create_test_server("scholar", IntentCategory::Research));
        registry.register(create_test_server("postgres", IntentCategory::DatabaseQuery));

        let research_servers = registry.find_by_intent(IntentCategory::Research);
        assert_eq!(research_servers.len(), 2);

        let db_servers = registry.find_by_intent(IntentCategory::DatabaseQuery);
        assert_eq!(db_servers.len(), 1);
    }

    #[test]
    fn test_registry_query() {
        let mut registry = CapabilityRegistry::new();
        registry.register(create_test_server("arxiv", IntentCategory::Research));

        let query = CapabilityQuery::new(IntentCategory::Research);
        let results = registry.query(query);
        assert_eq!(results.len(), 1);
    }

    #[test]
    fn test_registry_get() {
        let mut registry = CapabilityRegistry::new();
        let server = create_test_server("arxiv", IntentCategory::Research);
        registry.register(server);

        let retrieved = registry.get("arxiv");
        assert!(retrieved.is_some());
        assert_eq!(retrieved.unwrap().name, "arxiv MCP");
    }

    #[test]
    fn test_registry_record_success() {
        let mut registry = CapabilityRegistry::new();
        let mut server = create_test_server("arxiv", IntentCategory::Research);
        server.metadata.success_rate = 0.5;
        registry.register(server);

        registry.record_success("arxiv");
        let updated = registry.get("arxiv").unwrap();
        assert!(updated.metadata.success_rate > 0.5);
    }

    #[test]
    fn test_registry_record_failure() {
        let mut registry = CapabilityRegistry::new();
        let mut server = create_test_server("arxiv", IntentCategory::Research);
        server.metadata.success_rate = 0.5;
        registry.register(server);

        registry.record_failure("arxiv");
        let updated = registry.get("arxiv").unwrap();
        assert!(updated.metadata.success_rate < 0.5);
    }

    #[test]
    fn test_capability_query_builder() {
        let query = CapabilityQuery::new(IntentCategory::Research)
            .with_min_success_rate(0.8)
            .available_only();

        assert_eq!(query.min_success_rate, 0.8);
        assert!(query.must_be_available);
    }

    #[test]
    fn test_registry_supported_intents() {
        let mut registry = CapabilityRegistry::new();
        registry.register(create_test_server("arxiv", IntentCategory::Research));
        registry.register(create_test_server("postgres", IntentCategory::DatabaseQuery));

        let intents = registry.supported_intents();
        assert_eq!(intents.len(), 2);
    }
}
