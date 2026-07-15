use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Query represents an agent's information need.
///
/// PyStreamMCP takes incoming queries and optimizes them for:
/// - Minimal token usage
/// - Maximum relevance
/// - Fastest execution
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Query {
    pub id: String,
    pub text: String,
    pub agent_id: String,
    pub intent: QueryIntent,
    pub constraints: QueryConstraints,
    pub metadata: HashMap<String, serde_json::Value>,
    pub created_at: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub enum QueryIntent {
    #[default]
    Retrieve,           // Get specific information
    Discover,          // Explore available data
    Aggregate,         // Summarize multiple sources
    Synthesize,        // Combine information
    Analyze,           // Statistical analysis
    Custom(String),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QueryConstraints {
    /// Maximum tokens to retrieve
    pub max_tokens: Option<u32>,
    /// Maximum latency in milliseconds
    pub max_latency_ms: Option<u64>,
    /// Minimum confidence/quality score (0.0 - 1.0)
    pub min_confidence: Option<f32>,
    /// Required data freshness (seconds)
    pub max_staleness_seconds: Option<u64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QueryPlan {
    pub query_id: String,
    pub steps: Vec<QueryStep>,
    pub estimated_tokens: u32,
    pub estimated_latency_ms: u64,
    pub cost_reduction_percent: f32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QueryStep {
    pub id: String,
    pub action: QueryAction,
    pub token_budget: u32,
    pub dependencies: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum QueryAction {
    Lookup { key: String },
    Search { query: String, limit: u32 },
    Filter { condition: String },
    Aggregate { function: String },
    LLMCall { prompt: String, model: String },
}

impl Query {
    pub fn new(text: impl Into<String>, agent_id: impl Into<String>) -> Self {
        let now = chrono::Utc::now();
        Query {
            id: uuid::Uuid::new_v4().to_string(),
            text: text.into(),
            agent_id: agent_id.into(),
            intent: QueryIntent::Retrieve,
            constraints: QueryConstraints::default(),
            metadata: HashMap::new(),
            created_at: now,
        }
    }

    pub fn with_intent(mut self, intent: QueryIntent) -> Self {
        self.intent = intent;
        self
    }

    pub fn with_constraints(mut self, constraints: QueryConstraints) -> Self {
        self.constraints = constraints;
        self
    }

    pub fn with_max_tokens(mut self, tokens: u32) -> Self {
        self.constraints.max_tokens = Some(tokens);
        self
    }

    pub fn token_efficient(mut self) -> Self {
        self.constraints.max_tokens = Some(500);
        self.constraints.min_confidence = Some(0.85);
        self
    }
}

impl Default for QueryConstraints {
    fn default() -> Self {
        QueryConstraints {
            max_tokens: Some(2000),
            max_latency_ms: Some(5000),
            min_confidence: None,
            max_staleness_seconds: Some(3600),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_query_creation() {
        let query = Query::new("What are top customers by LTV?", "agent_123");
        assert_eq!(query.agent_id, "agent_123");
        assert!(query.constraints.max_tokens.is_some());
    }

    #[test]
    fn test_query_token_efficient() {
        let query = Query::new("List customers", "agent_1").token_efficient();
        assert_eq!(query.constraints.max_tokens, Some(500));
        assert_eq!(query.constraints.min_confidence, Some(0.85));
    }

    #[test]
    fn test_query_intent() {
        let query = Query::new("Test", "agent_1").with_intent(QueryIntent::Discover);
        match query.intent {
            QueryIntent::Discover => {}
            _ => panic!("Wrong intent"),
        }
    }
}
