/// Main orchestration engine combining Stage 1 and Stage 2 for intelligent retrieval

use serde::{Serialize, Deserialize};
use crate::metadata::{RankedCandidate, SourceType};
use crate::Result;

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct OrchestrationConfig {
    pub enable_stage1: bool,
    pub enable_stage2: bool,
    pub min_candidate_score: f64,
    pub top_k_sources: usize,
    pub enable_quality_validation: bool,
}

impl Default for OrchestrationConfig {
    fn default() -> Self {
        Self {
            enable_stage1: true,
            enable_stage2: true,
            min_candidate_score: 0.5,
            top_k_sources: 3,
            enable_quality_validation: true,
        }
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct OrchestrationResult {
    pub selected_sources: Vec<RankedCandidate>,
    pub stage1_decisions: Stage1Decision,
    pub stage2_decisions: Option<Stage2Decision>,
    pub total_candidates: usize,
    pub total_processing_time_ms: f64,
    pub recommendations: Vec<String>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Stage1Decision {
    pub candidates_evaluated: usize,
    pub candidates_filtered: usize,
    pub pass_through_rate: f64,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Stage2Decision {
    pub complexity_tier: String,
    pub token_budget: u32,
    pub source_strategy: String,
    pub relevance_adjustments: Vec<(String, f64)>,
}

pub struct RetrievalOrchestrator {
    config: OrchestrationConfig,
}

impl RetrievalOrchestrator {
    pub fn new(config: OrchestrationConfig) -> Self {
        Self { config }
    }

    /// Orchestrate end-to-end retrieval (Stage 1 + Stage 2)
    pub async fn orchestrate(
        &self,
        query: &str,
        source_type: SourceType,
        candidates: Vec<RankedCandidate>,
    ) -> Result<OrchestrationResult> {
        let start_time = std::time::Instant::now();

        // Stage 1: Metadata filtering
        let (stage1_selected, stage1_decision) =
            self.stage1_filtering(&candidates)?;

        let mut recommendations = Vec::new();

        // Stage 2: Contextual reranking (optional)
        let (final_selected, stage2_decision) = if self.config.enable_stage2 && !stage1_selected.is_empty() {
            let (reranked, decision) = self.stage2_reranking(query, stage1_selected)?;
            (reranked, Some(decision))
        } else {
            (stage1_selected, None)
        };

        // Quality validation (optional)
        if self.config.enable_quality_validation && !final_selected.is_empty() {
            recommendations.push("Quality validation enabled - use top 1-2 sources only".to_string());
        }

        let total_time = start_time.elapsed().as_secs_f64() * 1000.0;

        Ok(OrchestrationResult {
            selected_sources: final_selected,
            stage1_decisions: stage1_decision,
            stage2_decisions,
            total_candidates: candidates.len(),
            total_processing_time_ms: total_time,
            recommendations,
        })
    }

    fn stage1_filtering(
        &self,
        candidates: &[RankedCandidate],
    ) -> Result<(Vec<RankedCandidate>, Stage1Decision)> {
        let filtered: Vec<_> = candidates
            .iter()
            .filter(|c| c.score >= self.config.min_candidate_score)
            .take(self.config.top_k_sources)
            .cloned()
            .collect();

        let decision = Stage1Decision {
            candidates_evaluated: candidates.len(),
            candidates_filtered: candidates.len() - filtered.len(),
            pass_through_rate: filtered.len() as f64 / candidates.len() as f64,
        };

        Ok((filtered, decision))
    }

    fn stage2_reranking(
        &self,
        query: &str,
        candidates: Vec<RankedCandidate>,
    ) -> Result<(Vec<RankedCandidate>, Stage2Decision)> {
        // Simplified Stage 2: would call complexity detector and reranker
        let complexity_score = self.estimate_complexity(query);
        let token_budget = self.calculate_token_budget(complexity_score);

        let decision = Stage2Decision {
            complexity_tier: self.complexity_tier_name(complexity_score),
            token_budget,
            source_strategy: self.source_strategy_name(complexity_score),
            relevance_adjustments: self.calculate_adjustments(&candidates),
        };

        Ok((candidates, decision))
    }

    fn estimate_complexity(&self, query: &str) -> f64 {
        let word_count = query.split_whitespace().count();
        let has_keywords = [
            "aggregate", "average", "sum", "count", "group",
            "historical", "trend", "seasonal", "pattern",
        ]
        .iter()
        .any(|kw| query.to_lowercase().contains(kw));

        let mut score = (word_count as f64 / 10.0).min(1.0);
        if has_keywords {
            score += 0.3;
        }
        score.min(1.0)
    }

    fn calculate_token_budget(&self, complexity: f64) -> u32 {
        let base_tokens = 1000u32;
        ((base_tokens as f64) * (1.0 + complexity * 3.0)) as u32
    }

    fn complexity_tier_name(&self, score: f64) -> String {
        match score {
            0.0..=0.25 => "Simple".to_string(),
            0.26..=0.50 => "Moderate".to_string(),
            0.51..=0.75 => "Complex".to_string(),
            _ => "VeryComplex".to_string(),
        }
    }

    fn source_strategy_name(&self, score: f64) -> String {
        match score {
            0.0..=0.25 => "TopOne".to_string(),
            0.26..=0.50 => "TopTwo".to_string(),
            0.51..=0.75 => "TopThree".to_string(),
            _ => "TopFive".to_string(),
        }
    }

    fn calculate_adjustments(
        &self,
        candidates: &[RankedCandidate],
    ) -> Vec<(String, f64)> {
        candidates
            .iter()
            .map(|c| (c.source.clone(), 1.0 + (c.score * 0.5)))
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_orchestration_config_default() {
        let config = OrchestrationConfig::default();
        assert!(config.enable_stage1);
        assert!(config.enable_stage2);
    }

    #[test]
    fn test_orchestrator_creation() {
        let orchestrator = RetrievalOrchestrator::new(OrchestrationConfig::default());
        let config = orchestrator.config.clone();
        assert!(config.enable_stage1);
    }

    #[test]
    fn test_complexity_estimation_simple() {
        let orchestrator = RetrievalOrchestrator::new(OrchestrationConfig::default());
        let complexity = orchestrator.estimate_complexity("What is Python?");
        assert!(complexity < 0.5);
    }

    #[test]
    fn test_complexity_estimation_complex() {
        let orchestrator = RetrievalOrchestrator::new(OrchestrationConfig::default());
        let query = "Calculate seasonal aggregate trends with historical pattern analysis";
        let complexity = orchestrator.estimate_complexity(query);
        assert!(complexity > 0.5);
    }

    #[test]
    fn test_token_budget_calculation() {
        let orchestrator = RetrievalOrchestrator::new(OrchestrationConfig::default());
        let simple_budget = orchestrator.calculate_token_budget(0.2);
        let complex_budget = orchestrator.calculate_token_budget(0.8);
        assert!(complex_budget > simple_budget);
    }

    #[test]
    fn test_complexity_tier_names() {
        let orchestrator = RetrievalOrchestrator::new(OrchestrationConfig::default());
        assert_eq!(orchestrator.complexity_tier_name(0.1), "Simple");
        assert_eq!(orchestrator.complexity_tier_name(0.4), "Moderate");
        assert_eq!(orchestrator.complexity_tier_name(0.6), "Complex");
        assert_eq!(orchestrator.complexity_tier_name(0.9), "VeryComplex");
    }
}
