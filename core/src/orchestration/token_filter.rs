/// Token budget and relevance-based filtering for intelligent content selection

use serde::{Serialize, Deserialize};
use crate::metadata::RankedCandidate;

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct TokenBudget {
    pub total_tokens: u32,
    pub allocated_tokens: u32,
    pub used_tokens: u32,
    pub critical_keywords: Vec<String>,
    pub keyword_multiplier: f64,
}

impl TokenBudget {
    pub fn new(total_tokens: u32) -> Self {
        Self {
            total_tokens,
            allocated_tokens: 0,
            used_tokens: 0,
            critical_keywords: Vec::new(),
            keyword_multiplier: 2.0,
        }
    }

    pub fn remaining(&self) -> u32 {
        self.total_tokens.saturating_sub(self.used_tokens)
    }

    pub fn allocate(&mut self, tokens: u32) -> bool {
        if self.used_tokens + tokens <= self.total_tokens {
            self.used_tokens += tokens;
            true
        } else {
            false
        }
    }

    pub fn add_critical_keywords(&mut self, keywords: Vec<String>) {
        self.critical_keywords = keywords;
    }

    pub fn get_adjusted_budget(&self) -> u32 {
        let base = self.total_tokens.saturating_sub(self.used_tokens);
        (base as f64 * self.keyword_multiplier) as u32
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct TokenFilterResult {
    pub selected_content: Vec<ContentSegment>,
    pub total_tokens_used: u32,
    pub relevance_score: f64,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ContentSegment {
    pub text: String,
    pub relevance: f64,
    pub tokens_estimated: u32,
    pub has_critical_keywords: bool,
}

pub struct TokenFilter;

impl TokenFilter {
    /// Filter content to fit within token budget
    pub fn filter_to_budget(
        content: Vec<ContentSegment>,
        budget: &mut TokenBudget,
    ) -> TokenFilterResult {
        let mut selected = Vec::new();
        let mut total_tokens = 0;

        // First pass: add critical keyword content
        for segment in &content {
            if segment.has_critical_keywords
                && total_tokens + segment.tokens_estimated <= budget.total_tokens
            {
                selected.push(segment.clone());
                total_tokens += segment.tokens_estimated;
            }
        }

        // Second pass: add high-relevance content
        let remaining_budget = budget.total_tokens.saturating_sub(total_tokens);
        for segment in &content {
            if !segment.has_critical_keywords
                && segment.relevance > 0.7
                && total_tokens + segment.tokens_estimated <= budget.total_tokens
            {
                selected.push(segment.clone());
                total_tokens += segment.tokens_estimated;
            }
        }

        // Third pass: fill remaining budget with other content
        for segment in &content {
            if !selected.contains(segment)
                && total_tokens + segment.tokens_estimated <= budget.total_tokens
            {
                selected.push(segment.clone());
                total_tokens += segment.tokens_estimated;
            }
        }

        let _ = budget.allocate(total_tokens);
        let relevance_score = if selected.is_empty() {
            0.0
        } else {
            selected.iter().map(|s| s.relevance).sum::<f64>() / selected.len() as f64
        };

        TokenFilterResult {
            selected_content: selected,
            total_tokens_used: total_tokens,
            relevance_score,
        }
    }
}

#[derive(Clone, Debug)]
pub struct RelevanceRanker {
    query_keywords: Vec<String>,
    critical_weight: f64,
    contextual_weight: f64,
}

impl RelevanceRanker {
    pub fn new(query: &str) -> Self {
        Self {
            query_keywords: query.split_whitespace().map(|s| s.to_lowercase()).collect(),
            critical_weight: 2.0,
            contextual_weight: 1.0,
        }
    }

    pub fn rank_content(&self, candidates: &[RankedCandidate]) -> Vec<RankedContent> {
        candidates
            .iter()
            .map(|c| {
                let relevance = self.calculate_relevance(c);
                RankedContent {
                    original: c.clone(),
                    relevance_score: relevance,
                }
            })
            .collect()
    }

    fn calculate_relevance(&self, candidate: &RankedCandidate) -> f64 {
        let base_score = candidate.score;
        let keyword_match = self.keyword_match_ratio(candidate);
        (base_score * 0.6) + (keyword_match * 0.4)
    }

    fn keyword_match_ratio(&self, _candidate: &RankedCandidate) -> f64 {
        // Simplified: real implementation would analyze candidate content
        0.8
    }
}

#[derive(Clone, Debug)]
pub struct RankedContent {
    pub original: RankedCandidate,
    pub relevance_score: f64,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_token_budget_creation() {
        let budget = TokenBudget::new(1000);
        assert_eq!(budget.total_tokens, 1000);
        assert_eq!(budget.remaining(), 1000);
    }

    #[test]
    fn test_token_allocation() {
        let mut budget = TokenBudget::new(1000);
        assert!(budget.allocate(500));
        assert_eq!(budget.remaining(), 500);
    }

    #[test]
    fn test_token_overallocation() {
        let mut budget = TokenBudget::new(1000);
        assert!(budget.allocate(800));
        assert!(!budget.allocate(300)); // Should fail
        assert_eq!(budget.remaining(), 200);
    }

    #[test]
    fn test_content_segment_creation() {
        let segment = ContentSegment {
            text: "Sample content".to_string(),
            relevance: 0.85,
            tokens_estimated: 50,
            has_critical_keywords: false,
        };
        assert_eq!(segment.relevance, 0.85);
    }

    #[test]
    fn test_relevance_ranker_creation() {
        let ranker = RelevanceRanker::new("python machine learning");
        assert_eq!(ranker.query_keywords.len(), 3);
    }
}
