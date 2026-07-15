use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QueryStep {
    pub step_id: usize,
    pub sub_query: String,
    pub required_sources: Vec<String>,
    pub optimization_strategy: String,
    pub estimated_tokens: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DecomposedQuery {
    pub query_id: String,
    pub original_query: String,
    pub steps: Vec<QueryStep>,
    pub dependencies: Vec<(usize, usize)>,
    pub parallelizable_steps: Vec<usize>,
    pub estimated_total_tokens: u32,
    pub complexity_score: f32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExecutionPlan {
    pub plan_id: String,
    pub stages: Vec<Vec<usize>>,
    pub sequential_order: Vec<usize>,
    pub estimated_latency_ms: u32,
    pub optimized: bool,
}

pub struct QueryDecomposer;

impl QueryDecomposer {
    pub fn decompose(complex_query: &str) -> crate::error::Result<DecomposedQuery> {
        let query_id = format!("dq_{}", uuid::Uuid::new_v4());

        // Detect multi-step queries by keywords
        let keywords = ["then", "after", "next", "combine", "also", "which"];
        let query_lower = complex_query.to_lowercase();

        let keyword_count = keywords.iter().filter(|kw| query_lower.contains(*kw)).count();
        let step_count = if keyword_count == 0 { 1 } else { keyword_count + 1 };

        let mut steps = Vec::new();
        let mut dependencies = Vec::new();

        if step_count == 1 {
            // Single-step query
            steps.push(QueryStep {
                step_id: 0,
                sub_query: complex_query.to_string(),
                required_sources: Self::extract_sources(complex_query),
                optimization_strategy: "balanced".to_string(),
                estimated_tokens: Self::estimate_tokens(complex_query),
            });
        } else {
            // Multi-step query decomposition
            let parts = Self::split_query(complex_query, step_count);

            for (i, part) in parts.iter().enumerate() {
                steps.push(QueryStep {
                    step_id: i,
                    sub_query: part.clone(),
                    required_sources: Self::extract_sources(part),
                    optimization_strategy: Self::choose_strategy(part),
                    estimated_tokens: Self::estimate_tokens(part),
                });

                // Each step depends on the previous one for aggregation queries
                if i > 0 && complex_query.to_lowercase().contains("combine") {
                    dependencies.push((i, i - 1));
                }
            }
        }

        let total_tokens: u32 = steps.iter().map(|s| s.estimated_tokens).sum();
        let parallelizable = Self::find_parallelizable_steps(&steps, &dependencies);
        let complexity = Self::calculate_complexity(step_count, &dependencies);

        Ok(DecomposedQuery {
            query_id,
            original_query: complex_query.to_string(),
            steps,
            dependencies,
            parallelizable_steps: parallelizable,
            estimated_total_tokens: total_tokens,
            complexity_score: complexity,
        })
    }

    pub fn optimize_execution_plan(
        decomposed: &DecomposedQuery,
    ) -> crate::error::Result<ExecutionPlan> {
        let plan_id = format!("ep_{}", uuid::Uuid::new_v4());

        // Create execution stages
        let mut stages = Vec::new();
        let mut scheduled = vec![false; decomposed.steps.len()];

        while scheduled.iter().any(|s| !s) {
            let mut stage_steps = Vec::new();

            for i in 0..decomposed.steps.len() {
                if scheduled[i] {
                    continue;
                }

                // Check if all dependencies are scheduled
                let can_run = decomposed
                    .dependencies
                    .iter()
                    .filter(|(_, dep)| *dep == i)
                    .all(|(step, _)| scheduled[*step]);

                if can_run {
                    stage_steps.push(i);
                    scheduled[i] = true;
                }
            }

            if !stage_steps.is_empty() {
                stages.push(stage_steps);
            } else if scheduled.iter().any(|s| !s) {
                return Err(crate::error::Error::ValidationGateFailed(
                    "Circular dependency detected".to_string(),
                ));
            }
        }

        let sequential_order: Vec<usize> = (0..decomposed.steps.len()).collect();
        let estimated_latency = (stages.len() as u32) * 50 + decomposed.estimated_total_tokens / 100;

        Ok(ExecutionPlan {
            plan_id,
            stages,
            sequential_order,
            estimated_latency_ms: estimated_latency,
            optimized: decomposed.steps.len() > 1,
        })
    }

    fn split_query(query: &str, count: usize) -> Vec<String> {
        let keywords = ["then", "after", "next", "combine", "also"];
        let query_lower = query.to_lowercase();

        let mut parts = Vec::new();
        let mut last_pos = 0;

        for keyword in &keywords {
            if let Some(pos) = query_lower.find(keyword) {
                if last_pos < pos {
                    parts.push(query[last_pos..pos].trim().to_string());
                }
                last_pos = pos + keyword.len();
            }
        }

        if last_pos < query.len() {
            parts.push(query[last_pos..].trim().to_string());
        }

        // Ensure we have at least 'count' parts
        while parts.len() < count {
            parts.push(query.to_string());
        }

        parts.into_iter().take(count).collect()
    }

    fn extract_sources(query: &str) -> Vec<String> {
        let keywords = [
            "customer", "order", "product", "revenue", "segment", "metric", "data",
        ];
        keywords
            .iter()
            .filter(|kw| query.to_lowercase().contains(*kw))
            .map(|s| s.to_string())
            .collect()
    }

    fn choose_strategy(query: &str) -> String {
        let query_lower = query.to_lowercase();
        if query_lower.contains("top") || query_lower.contains("rank") {
            "quality_first".to_string()
        } else if query_lower.contains("aggregate") || query_lower.contains("sum") {
            "token_efficient".to_string()
        } else {
            "balanced".to_string()
        }
    }

    fn estimate_tokens(query: &str) -> u32 {
        let base = (query.len() as u32) / 4;
        let multiplier = if query.contains("detailed") { 2 } else { 1 };
        (base * multiplier).max(100)
    }

    fn find_parallelizable_steps(
        steps: &[QueryStep],
        dependencies: &[(usize, usize)],
    ) -> Vec<usize> {
        steps
            .iter()
            .enumerate()
            .filter(|(i, _)| {
                !dependencies.iter().any(|(_, dep)| dep == i)
                    && !dependencies.iter().any(|(step, _)| step == i)
            })
            .map(|(i, _)| i)
            .collect()
    }

    fn calculate_complexity(step_count: usize, dependencies: &[(usize, usize)]) -> f32 {
        let step_complexity = step_count as f32 / 5.0;
        let dependency_complexity = dependencies.len() as f32 / 2.0;
        (step_complexity + dependency_complexity) / 2.0
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_single_step_query() {
        let query = "Find all customers with revenue > 1000";
        let decomposed = QueryDecomposer::decompose(query).unwrap();
        assert_eq!(decomposed.steps.len(), 1);
        assert_eq!(decomposed.steps[0].step_id, 0);
    }

    #[test]
    fn test_multi_step_query() {
        let query = "Find customers then calculate their lifetime value then rank by importance";
        let decomposed = QueryDecomposer::decompose(query).unwrap();
        assert!(decomposed.steps.len() > 1);
    }

    #[test]
    fn test_execution_plan_generation() {
        let query = "Get customers then find their orders";
        let decomposed = QueryDecomposer::decompose(query).unwrap();
        let plan = QueryDecomposer::optimize_execution_plan(&decomposed).unwrap();
        assert!(!plan.stages.is_empty());
        assert!(plan.estimated_latency_ms > 0);
    }

    #[test]
    fn test_source_extraction() {
        let query = "Find top customers by order value";
        let sources = QueryDecomposer::extract_sources(query);
        assert!(sources.contains(&"customer".to_string()));
        assert!(sources.contains(&"order".to_string()));
    }

    #[test]
    fn test_token_estimation() {
        let short_query = "Find customers";
        let long_query = "Find all detailed customer information with complete purchase history and interactions";
        let short_tokens = QueryDecomposer::estimate_tokens(short_query);
        let long_tokens = QueryDecomposer::estimate_tokens(long_query);
        assert!(long_tokens >= short_tokens);
    }

    #[test]
    fn test_complexity_score() {
        let simple = QueryDecomposer::decompose("Find customers").unwrap();
        let complex = QueryDecomposer::decompose("Find customers then rank then segment then analyze")
            .unwrap();
        assert!(complex.complexity_score > simple.complexity_score);
    }
}
