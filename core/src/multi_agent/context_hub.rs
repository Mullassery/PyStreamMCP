use crate::context::Context;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SharedContext {
    pub context_id: String,
    pub original_query: String,
    pub optimized_context: Context,
    pub usage_count: u32,
    pub agents_using: Vec<String>,
    pub created_at: String,
    pub cost_savings: f32,
}

impl SharedContext {
    pub fn new(context_id: &str, query: &str, context: Context) -> Self {
        Self {
            context_id: context_id.to_string(),
            original_query: query.to_string(),
            optimized_context: context,
            usage_count: 1,
            agents_using: Vec::new(),
            created_at: chrono::Utc::now().to_rfc3339(),
            cost_savings: 0.0,
        }
    }

    pub fn add_agent(&mut self, agent_id: &str) {
        if !self.agents_using.contains(&agent_id.to_string()) {
            self.agents_using.push(agent_id.to_string());
        }
        self.usage_count += 1;
    }

    pub fn reuse_factor(&self) -> f32 {
        self.usage_count as f32 / self.agents_using.len().max(1) as f32
    }
}

pub struct ContextHub {
    shared_contexts: HashMap<String, SharedContext>,
    agent_collaborations: HashMap<String, Vec<String>>,
}

impl ContextHub {
    pub fn new() -> Self {
        Self {
            shared_contexts: HashMap::new(),
            agent_collaborations: HashMap::new(),
        }
    }

    pub fn register_context(
        &mut self,
        context: SharedContext,
    ) -> crate::error::Result<String> {
        let id = context.context_id.clone();
        self.shared_contexts.insert(id.clone(), context);
        Ok(id)
    }

    pub fn query_shared_contexts(&self, query: &str, limit: usize) -> Vec<SharedContext> {
        let query_lower = query.to_lowercase();
        let mut results: Vec<_> = self
            .shared_contexts
            .values()
            .filter(|ctx| {
                let ctx_query_lower = ctx.original_query.to_lowercase();
                ctx_query_lower.contains(&query_lower)
                    || levenshtein_distance(&query_lower, &ctx_query_lower) < 3
            })
            .cloned()
            .collect();

        results.sort_by(|a, b| {
            b.usage_count
                .cmp(&a.usage_count)
                .then_with(|| b.cost_savings.partial_cmp(&a.cost_savings).unwrap())
        });

        results.into_iter().take(limit).collect()
    }

    pub fn update_usage(&mut self, context_id: &str, agent_id: &str) -> crate::error::Result<()> {
        if let Some(ctx) = self.shared_contexts.get_mut(context_id) {
            ctx.add_agent(agent_id);

            self.agent_collaborations
                .entry(agent_id.to_string())
                .or_insert_with(Vec::new)
                .push(context_id.to_string());

            Ok(())
        } else {
            Err(crate::error::Error::ValidationGateFailed(
                format!("Context {} not found", context_id),
            ))
        }
    }

    pub fn get_context(&self, context_id: &str) -> Option<SharedContext> {
        self.shared_contexts.get(context_id).cloned()
    }

    pub fn agent_collaboration_score(&self, agent_id: &str) -> f32 {
        if let Some(contexts) = self.agent_collaborations.get(agent_id) {
            let total_reuse: f32 = contexts
                .iter()
                .filter_map(|ctx_id| {
                    self.shared_contexts
                        .get(ctx_id)
                        .map(|ctx| ctx.reuse_factor())
                })
                .sum();
            total_reuse / contexts.len().max(1) as f32
        } else {
            0.0
        }
    }

    pub fn collaboration_savings(&self) -> f32 {
        self.shared_contexts
            .values()
            .map(|ctx| ctx.cost_savings * ctx.usage_count as f32)
            .sum()
    }

    pub fn context_count(&self) -> usize {
        self.shared_contexts.len()
    }

    pub fn agent_count(&self) -> usize {
        self.agent_collaborations.len()
    }
}

impl Default for ContextHub {
    fn default() -> Self {
        Self::new()
    }
}

fn levenshtein_distance(s1: &str, s2: &str) -> usize {
    let len1 = s1.len();
    let len2 = s2.len();

    if len1 == 0 {
        return len2;
    }
    if len2 == 0 {
        return len1;
    }

    let mut matrix = vec![vec![0; len2 + 1]; len1 + 1];

    for i in 0..=len1 {
        matrix[i][0] = i;
    }
    for j in 0..=len2 {
        matrix[0][j] = j;
    }

    let s1_chars: Vec<char> = s1.chars().collect();
    let s2_chars: Vec<char> = s2.chars().collect();

    for i in 1..=len1 {
        for j in 1..=len2 {
            let cost = if s1_chars[i - 1] == s2_chars[j - 1] { 0 } else { 1 };
            matrix[i][j] = (*[
                matrix[i - 1][j] + 1,
                matrix[i][j - 1] + 1,
                matrix[i - 1][j - 1] + cost,
            ]
            .iter()
            .min()
            .unwrap());
        }
    }

    matrix[len1][len2]
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn test_shared_context_creation() {
        let ctx = Context::new(
            "query_1",
            crate::context::ContextType::EntityData {
                entity_type: "customer".to_string(),
            },
            json!({"id": "123"}),
            "warehouse",
        );
        let shared = SharedContext::new("sc_1", "test query", ctx);
        assert_eq!(shared.context_id, "sc_1");
        assert_eq!(shared.usage_count, 1);
    }

    #[test]
    fn test_context_hub_register() {
        let mut hub = ContextHub::new();
        let ctx = Context::new(
            "q1",
            crate::context::ContextType::EntityData {
                entity_type: "c".to_string(),
            },
            json!({}),
            "db",
        );
        let shared = SharedContext::new("sc_1", "customers", ctx);
        assert!(hub.register_context(shared).is_ok());
        assert_eq!(hub.context_count(), 1);
    }

    #[test]
    fn test_query_shared_contexts() {
        let mut hub = ContextHub::new();
        let ctx1 = Context::new(
            "q1",
            crate::context::ContextType::EntityData {
                entity_type: "customer".to_string(),
            },
            json!({}),
            "db",
        );
        let ctx2 = Context::new(
            "q2",
            crate::context::ContextType::Metric {
                name: "revenue".to_string(),
            },
            json!({}),
            "metrics",
        );

        let sc1 = SharedContext::new("sc_1", "customer data", ctx1);
        let sc2 = SharedContext::new("sc_2", "revenue metrics", ctx2);

        hub.register_context(sc1).ok();
        hub.register_context(sc2).ok();

        let results = hub.query_shared_contexts("customer", 10);
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].context_id, "sc_1");
    }

    #[test]
    fn test_update_usage() {
        let mut hub = ContextHub::new();
        let ctx = Context::new(
            "q1",
            crate::context::ContextType::EntityData {
                entity_type: "c".to_string(),
            },
            json!({}),
            "db",
        );
        let shared = SharedContext::new("sc_1", "test", ctx);
        hub.register_context(shared).ok();

        assert!(hub.update_usage("sc_1", "agent_1").is_ok());
        assert!(hub.update_usage("sc_1", "agent_2").is_ok());

        let ctx = hub.get_context("sc_1").unwrap();
        assert_eq!(ctx.agents_using.len(), 2);
        assert!(ctx.usage_count >= 3);
    }

    #[test]
    fn test_collaboration_score() {
        let mut hub = ContextHub::new();
        let ctx = Context::new(
            "q1",
            crate::context::ContextType::EntityData {
                entity_type: "c".to_string(),
            },
            json!({}),
            "db",
        );
        let shared = SharedContext::new("sc_1", "test", ctx);
        hub.register_context(shared).ok();

        hub.update_usage("sc_1", "agent_1").ok();
        hub.update_usage("sc_1", "agent_2").ok();

        let score = hub.agent_collaboration_score("agent_1");
        assert!(score >= 1.0);
    }
}
