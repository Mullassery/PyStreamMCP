use serde::{Deserialize, Serialize};
use serde_json::json;

/// Context represents relevant information for an agent's decision-making.
///
/// PyStreamMCP discovers and optimizes which context to include in each query.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Context {
    pub id: String,
    pub query_id: String,
    pub context_type: ContextType,
    pub content: serde_json::Value,
    pub relevance_score: f32,
    pub token_count: u32,
    pub source: String,
    pub created_at: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ContextType {
    EntityData { entity_type: String },
    Relationship { from: String, to: String },
    Metric { name: String },
    Historical { period: String },
    Similar { similarity_type: String },
    Contextual { category: String },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ContextWindow {
    pub query_id: String,
    pub contexts: Vec<Context>,
    pub total_tokens: u32,
    pub token_budget: u32,
    pub utilization_percent: f32,
}

impl Context {
    pub fn new(
        query_id: impl Into<String>,
        context_type: ContextType,
        content: serde_json::Value,
        source: impl Into<String>,
    ) -> Self {
        let now = chrono::Utc::now();
        let token_count = estimate_tokens(&content);

        Context {
            id: uuid::Uuid::new_v4().to_string(),
            query_id: query_id.into(),
            context_type,
            content,
            relevance_score: 1.0,
            token_count,
            source: source.into(),
            created_at: now,
        }
    }

    pub fn with_relevance(mut self, score: f32) -> Self {
        self.relevance_score = score.max(0.0).min(1.0);
        self
    }
}

impl ContextWindow {
    pub fn new(query_id: impl Into<String>, token_budget: u32) -> Self {
        ContextWindow {
            query_id: query_id.into(),
            contexts: Vec::new(),
            total_tokens: 0,
            token_budget,
            utilization_percent: 0.0,
        }
    }

    pub fn add_context(&mut self, context: Context) -> Result<(), String> {
        if self.total_tokens + context.token_count > self.token_budget {
            return Err(format!(
                "Token budget exceeded: {} + {} > {}",
                self.total_tokens, context.token_count, self.token_budget
            ));
        }
        self.total_tokens += context.token_count;
        self.utilization_percent = (self.total_tokens as f32 / self.token_budget as f32) * 100.0;
        self.contexts.push(context);
        Ok(())
    }

    pub fn is_full(&self) -> bool {
        self.total_tokens >= self.token_budget
    }

    pub fn remaining_tokens(&self) -> u32 {
        self.token_budget.saturating_sub(self.total_tokens)
    }
}

/// Rough token count estimation (approx. 1 token per 4 characters)
fn estimate_tokens(value: &serde_json::Value) -> u32 {
    let serialized = serde_json::to_string(value).unwrap_or_default();
    ((serialized.len() as f32) / 4.0).ceil() as u32
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_context_creation() {
        let context = Context::new(
            "query_1",
            ContextType::EntityData {
                entity_type: "customer".to_string(),
            },
            json!({"id": "cust_123", "ltv": 5000}),
            "warehouse",
        );
        assert_eq!(context.query_id, "query_1");
        assert!(context.token_count > 0);
    }

    #[test]
    fn test_context_relevance() {
        let context = Context::new(
            "q1",
            ContextType::Metric {
                name: "MRR".to_string(),
            },
            json!({"value": 50000}),
            "metrics",
        )
        .with_relevance(0.95);

        assert_eq!(context.relevance_score, 0.95);
    }

    #[test]
    fn test_context_window() {
        let mut window = ContextWindow::new("query_1", 1000);
        let context1 = Context::new("query_1", ContextType::Metric { name: "test".into() }, json!({}), "s1");
        let context2 = Context::new("query_1", ContextType::Metric { name: "test2".into() }, json!({}), "s2");

        assert!(window.add_context(context1).is_ok());
        assert!(window.add_context(context2).is_ok());
        assert!(window.total_tokens > 0);
    }
}
