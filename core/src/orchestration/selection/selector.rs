use serde::{Deserialize, Serialize};
use std::time::Duration;
use super::super::intent::{IntentResult, IntentCategory};
use super::super::capabilities::{CapabilityRegistry, MCPServerProfile};

/// A selected tool for retrieval
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SelectedTool {
    pub server_id: String,
    pub server_name: String,
    pub rank_score: f32,
    pub selection_reason: String,
}

impl SelectedTool {
    pub fn new(server_id: String, server_name: String, rank_score: f32) -> Self {
        Self {
            server_id,
            server_name,
            rank_score,
            selection_reason: String::new(),
        }
    }

    pub fn with_reason(mut self, reason: String) -> Self {
        self.selection_reason = reason;
        self
    }
}

/// Tool selection strategy results
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ToolSelection {
    pub primary: Vec<SelectedTool>,
    pub secondary: Vec<SelectedTool>,
    pub fallback: Vec<SelectedTool>,
    pub selection_explanation: String,
}

impl ToolSelection {
    pub fn new() -> Self {
        Self {
            primary: vec![],
            secondary: vec![],
            fallback: vec![],
            selection_explanation: String::new(),
        }
    }

    /// Get all tools in priority order
    pub fn all_tools(&self) -> Vec<&SelectedTool> {
        let mut all: Vec<&SelectedTool> = vec![];
        all.extend(&self.primary);
        all.extend(&self.secondary);
        all.extend(&self.fallback);
        all
    }

    /// Get tools up to a certain tier
    pub fn tools_up_to(&self, tier: SelectionTier) -> Vec<&SelectedTool> {
        match tier {
            SelectionTier::PrimaryOnly => self.primary.iter().collect(),
            SelectionTier::WithSecondary => {
                let mut tools: Vec<&SelectedTool> = vec![];
                tools.extend(&self.primary);
                tools.extend(&self.secondary);
                tools
            }
            SelectionTier::WithFallback => {
                let mut tools: Vec<&SelectedTool> = vec![];
                tools.extend(&self.primary);
                tools.extend(&self.secondary);
                tools.extend(&self.fallback);
                tools
            }
        }
    }

    pub fn count(&self) -> usize {
        self.primary.len() + self.secondary.len() + self.fallback.len()
    }
}

impl Default for ToolSelection {
    fn default() -> Self {
        Self::new()
    }
}

/// Selection tier for retrieval
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SelectionTier {
    PrimaryOnly,
    WithSecondary,
    WithFallback,
}

/// Constraints for tool selection
#[derive(Debug, Clone)]
pub struct SelectionConstraints {
    pub max_latency: Option<Duration>,
    pub max_cost_tokens: Option<usize>,
    pub max_tools: Option<usize>,
    pub require_availability: bool,
    pub min_success_rate: f32,
}

impl SelectionConstraints {
    pub fn new() -> Self {
        Self {
            max_latency: None,
            max_cost_tokens: None,
            max_tools: None,
            require_availability: false,
            min_success_rate: 0.0,
        }
    }

    pub fn with_max_latency(mut self, latency: Duration) -> Self {
        self.max_latency = Some(latency);
        self
    }

    pub fn with_max_cost(mut self, tokens: usize) -> Self {
        self.max_cost_tokens = Some(tokens);
        self
    }

    pub fn with_max_tools(mut self, count: usize) -> Self {
        self.max_tools = Some(count);
        self
    }

    pub fn available_only(mut self) -> Self {
        self.require_availability = true;
        self
    }

    pub fn with_min_success_rate(mut self, rate: f32) -> Self {
        self.min_success_rate = rate;
        self
    }
}

impl Default for SelectionConstraints {
    fn default() -> Self {
        Self::new()
    }
}

/// Intelligent tool selector
pub struct ToolSelector {
    registry: CapabilityRegistry,
}

impl ToolSelector {
    pub fn new(registry: CapabilityRegistry) -> Self {
        Self { registry }
    }

    /// Select tools for an intent result
    pub fn select(&self, intent_result: &IntentResult) -> ToolSelection {
        self.select_with_constraints(intent_result, &SelectionConstraints::default())
    }

    /// Select tools with constraints
    pub fn select_with_constraints(
        &self,
        intent_result: &IntentResult,
        constraints: &SelectionConstraints,
    ) -> ToolSelection {
        let candidates = self.registry.find_by_intent(intent_result.primary);

        if candidates.is_empty() {
            return ToolSelection {
                primary: vec![],
                secondary: vec![],
                fallback: vec![],
                selection_explanation: format!(
                    "No servers found for intent: {:?}",
                    intent_result.primary
                ),
            };
        }

        // Filter candidates
        let mut filtered = candidates;

        if constraints.require_availability {
            filtered.retain(|s| s.is_available());
        }

        if constraints.min_success_rate > 0.0 {
            filtered
                .retain(|s| s.metadata.success_rate >= constraints.min_success_rate);
        }

        if let Some(max_latency) = constraints.max_latency {
            filtered.retain(|s| {
                Duration::from_millis(s.metadata.latency_avg_ms as u64) <= max_latency
            });
        }

        if let Some(max_cost) = constraints.max_cost_tokens {
            filtered.retain(|s| s.metadata.cost_per_query_tokens <= max_cost);
        }

        // Rank and categorize
        self.categorize_by_tier(filtered, constraints)
    }

    fn categorize_by_tier(
        &self,
        mut candidates: Vec<MCPServerProfile>,
        constraints: &SelectionConstraints,
    ) -> ToolSelection {
        // Score all candidates
        let mut scored: Vec<(MCPServerProfile, f32)> = candidates
            .into_iter()
            .map(|server| {
                let score = self.score_server(&server);
                (server, score)
            })
            .collect();

        // Sort by score descending
        scored.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));

        // Apply max_tools constraint
        let max_total = constraints.max_tools.unwrap_or(usize::MAX);
        let scored: Vec<(MCPServerProfile, f32)> = scored
            .into_iter()
            .take(max_total * 3) // Allow for distribution across tiers
            .collect();

        let total = scored.len();
        let primary_count = (total as f32 * 0.4).ceil() as usize;
        let secondary_count = (total as f32 * 0.35).ceil() as usize;

        let mut selection = ToolSelection::new();

        // Primary tier (top 40%)
        for (i, (server, score)) in scored
            .iter()
            .take(primary_count.min(total))
            .enumerate()
        {
            let tool = SelectedTool::new(
                server.id.clone(),
                server.name.clone(),
                *score,
            )
            .with_reason(format!("Rank #{}: High success rate ({:.1}%)", i + 1, server.metadata.success_rate * 100.0));
            selection.primary.push(tool);
        }

        // Secondary tier (next 35%)
        for (i, (server, score)) in scored
            .iter()
            .skip(primary_count)
            .take(secondary_count.min(total - primary_count))
            .enumerate()
        {
            let tool = SelectedTool::new(
                server.id.clone(),
                server.name.clone(),
                *score,
            )
            .with_reason(format!("Rank #{}: Good expertise ({:.1})", primary_count + i + 1, server.capabilities[0].domain_expertise));
            selection.secondary.push(tool);
        }

        // Fallback tier (remaining)
        for (i, (server, score)) in scored
            .iter()
            .skip(primary_count + secondary_count)
            .enumerate()
        {
            let tool = SelectedTool::new(
                server.id.clone(),
                server.name.clone(),
                *score,
            )
            .with_reason(format!("Fallback #{}: Available backup", i + 1));
            selection.fallback.push(tool);
        }

        selection.selection_explanation = format!(
            "Selected {} tools: {} primary, {} secondary, {} fallback",
            selection.count(),
            selection.primary.len(),
            selection.secondary.len(),
            selection.fallback.len()
        );

        selection
    }

    fn score_server(&self, server: &MCPServerProfile) -> f32 {
        // Scoring formula:
        // 0.35 * success_rate
        // + 0.25 * domain_expertise
        // + 0.15 * latency_score
        // + 0.10 * cost_efficiency
        // + 0.10 * freshness
        // + 0.05 * availability

        let success_rate = server.metadata.success_rate;
        let domain_expertise = server
            .capabilities
            .iter()
            .map(|c| c.domain_expertise)
            .max_by(|a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal))
            .unwrap_or(0.5);
        let latency_score = server.metadata.latency_score();
        let cost_score = server.metadata.cost_score();
        let freshness_score = server.metadata.data_freshness;
        let availability_score = server.metadata.health.score();

        0.35 * success_rate
            + 0.25 * domain_expertise
            + 0.15 * latency_score
            + 0.10 * cost_score
            + 0.10 * freshness_score
            + 0.05 * availability_score
    }
}

impl Default for ToolSelector {
    fn default() -> Self {
        Self::new(CapabilityRegistry::new())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_selected_tool_new() {
        let tool = SelectedTool::new(
            "arxiv".to_string(),
            "Arxiv MCP".to_string(),
            0.95,
        );
        assert_eq!(tool.server_id, "arxiv");
        assert_eq!(tool.rank_score, 0.95);
    }

    #[test]
    fn test_tool_selection_all_tools() {
        let mut selection = ToolSelection::new();
        selection.primary.push(SelectedTool::new(
            "arxiv".to_string(),
            "Arxiv".to_string(),
            0.95,
        ));
        selection.secondary.push(SelectedTool::new(
            "google".to_string(),
            "Google".to_string(),
            0.80,
        ));

        assert_eq!(selection.all_tools().len(), 2);
        assert_eq!(selection.count(), 2);
    }

    #[test]
    fn test_tool_selection_tier_filtering() {
        let mut selection = ToolSelection::new();
        selection.primary.push(SelectedTool::new(
            "arxiv".to_string(),
            "Arxiv".to_string(),
            0.95,
        ));
        selection.secondary.push(SelectedTool::new(
            "google".to_string(),
            "Google".to_string(),
            0.80,
        ));
        selection.fallback.push(SelectedTool::new(
            "bing".to_string(),
            "Bing".to_string(),
            0.60,
        ));

        let primary_only = selection.tools_up_to(SelectionTier::PrimaryOnly);
        assert_eq!(primary_only.len(), 1);

        let with_secondary = selection.tools_up_to(SelectionTier::WithSecondary);
        assert_eq!(with_secondary.len(), 2);

        let with_fallback = selection.tools_up_to(SelectionTier::WithFallback);
        assert_eq!(with_fallback.len(), 3);
    }

    #[test]
    fn test_selection_constraints() {
        let constraints = SelectionConstraints::new()
            .with_max_latency(Duration::from_millis(500))
            .with_max_cost(5000)
            .available_only();

        assert!(constraints.require_availability);
        assert_eq!(constraints.max_cost_tokens, Some(5000));
    }

    #[test]
    fn test_tool_selector_empty_registry() {
        let selector = ToolSelector::default();
        let intent_result = IntentResult::new(IntentCategory::Research, 0.8);

        let selection = selector.select(&intent_result);
        assert_eq!(selection.primary.len(), 0);
    }
}
