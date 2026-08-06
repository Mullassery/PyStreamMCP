/// Multi-modal reranking combining multiple ranking strategies for enhanced accuracy

use serde::{Serialize, Deserialize};
use crate::metadata::RankedCandidate;

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct RankingMode {
    pub name: String,
    pub strategy: RankingStrategy,
    pub weight: f64,
    pub enabled: bool,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum RankingStrategy {
    ContentBased,      // Score based on content characteristics
    CollaborativeFiltering, // Similar user preferences
    HybridSemantic,    // Semantic similarity analysis
    TemporalTrending,  // Time-based relevance decay
    ExpertiseAdapted,  // User skill level alignment
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct MultiModalRanker {
    pub modes: Vec<RankingMode>,
    pub fusion_method: FusionMethod,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum FusionMethod {
    WeightedAverage,   // Simple weighted average
    RRF,               // Reciprocal Rank Fusion
    Borda,             // Borda count
    ConductorBased,    // Multi-criteria decision
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct MultiModalScore {
    pub original_score: f64,
    pub content_score: f64,
    pub collaborative_score: f64,
    pub semantic_score: f64,
    pub temporal_score: f64,
    pub expertise_score: f64,
    pub final_score: f64,
    pub scoring_breakdown: Vec<(String, f64)>,
}

impl Default for MultiModalRanker {
    fn default() -> Self {
        Self {
            modes: vec![
                RankingMode {
                    name: "Content".to_string(),
                    strategy: RankingStrategy::ContentBased,
                    weight: 0.30,
                    enabled: true,
                },
                RankingMode {
                    name: "Collaborative".to_string(),
                    strategy: RankingStrategy::CollaborativeFiltering,
                    weight: 0.25,
                    enabled: true,
                },
                RankingMode {
                    name: "Semantic".to_string(),
                    strategy: RankingStrategy::HybridSemantic,
                    weight: 0.25,
                    enabled: true,
                },
                RankingMode {
                    name: "Temporal".to_string(),
                    strategy: RankingStrategy::TemporalTrending,
                    weight: 0.10,
                    enabled: true,
                },
                RankingMode {
                    name: "Expertise".to_string(),
                    strategy: RankingStrategy::ExpertiseAdapted,
                    weight: 0.10,
                    enabled: true,
                },
            ],
            fusion_method: FusionMethod::WeightedAverage,
        }
    }
}

impl MultiModalRanker {
    pub fn new(fusion_method: FusionMethod) -> Self {
        Self {
            fusion_method,
            ..Default::default()
        }
    }

    pub fn rerank(&self, candidates: &[RankedCandidate]) -> Vec<(RankedCandidate, MultiModalScore)> {
        candidates
            .iter()
            .map(|candidate| {
                let content_score = self.calculate_content_score(candidate);
                let collaborative_score = self.calculate_collaborative_score(candidate);
                let semantic_score = self.calculate_semantic_score(candidate);
                let temporal_score = self.calculate_temporal_score(candidate);
                let expertise_score = self.calculate_expertise_score(candidate);

                let final_score = self.fuse_scores(
                    candidate.score,
                    content_score,
                    collaborative_score,
                    semantic_score,
                    temporal_score,
                    expertise_score,
                );

                let breakdown = vec![
                    ("content".to_string(), content_score),
                    ("collaborative".to_string(), collaborative_score),
                    ("semantic".to_string(), semantic_score),
                    ("temporal".to_string(), temporal_score),
                    ("expertise".to_string(), expertise_score),
                ];

                let score = MultiModalScore {
                    original_score: candidate.score,
                    content_score,
                    collaborative_score,
                    semantic_score,
                    temporal_score,
                    expertise_score,
                    final_score,
                    scoring_breakdown: breakdown,
                };

                (candidate.clone(), score)
            })
            .collect()
    }

    fn calculate_content_score(&self, _candidate: &RankedCandidate) -> f64 {
        // Simplified: would analyze content depth, structure, completeness
        0.82
    }

    fn calculate_collaborative_score(&self, _candidate: &RankedCandidate) -> f64 {
        // Simplified: would use user preference patterns
        0.78
    }

    fn calculate_semantic_score(&self, _candidate: &RankedCandidate) -> f64 {
        // Simplified: would use semantic similarity
        0.85
    }

    fn calculate_temporal_score(&self, _candidate: &RankedCandidate) -> f64 {
        // Simplified: would check freshness/trending
        0.80
    }

    fn calculate_expertise_score(&self, _candidate: &RankedCandidate) -> f64 {
        // Simplified: would match user expertise level
        0.75
    }

    fn fuse_scores(
        &self,
        original: f64,
        content: f64,
        collab: f64,
        semantic: f64,
        temporal: f64,
        expertise: f64,
    ) -> f64 {
        match self.fusion_method {
            FusionMethod::WeightedAverage => {
                (original * 0.20)
                    + (content * 0.30)
                    + (collab * 0.25)
                    + (semantic * 0.25)
                    + (temporal * 0.10)
                    + (expertise * 0.10)
            }
            FusionMethod::RRF => self.reciprocal_rank_fusion(&[original, content, collab, semantic]),
            FusionMethod::Borda => self.borda_count(&[original, content, collab, semantic, temporal]),
            FusionMethod::ConductorBased => self.conductor_based(&[original, content, collab, semantic, expertise]),
        }
    }

    fn reciprocal_rank_fusion(&self, scores: &[f64]) -> f64 {
        let k = 60.0;
        scores
            .iter()
            .map(|score| 1.0 / (k + (1.0 - score) * 100.0))
            .sum::<f64>()
            / scores.len() as f64
    }

    fn borda_count(&self, scores: &[f64]) -> f64 {
        let mut sorted = scores.to_vec();
        sorted.sort_by(|a, b| b.partial_cmp(a).unwrap_or(std::cmp::Ordering::Equal));

        scores
            .iter()
            .map(|score| {
                let rank = sorted.iter().position(|s| (s - score).abs() < 0.01).unwrap_or(0);
                (scores.len() - rank) as f64 / scores.len() as f64
            })
            .sum::<f64>()
            / scores.len() as f64
    }

    fn conductor_based(&self, scores: &[f64]) -> f64 {
        let max_score = scores
            .iter()
            .copied()
            .fold(f64::NEG_INFINITY, f64::max);

        // Amplify best performers
        scores
            .iter()
            .map(|score| {
                if score == &max_score {
                    score * 1.15
                } else if score > &0.7 {
                    score * 1.05
                } else {
                    *score
                }
            })
            .sum::<f64>()
            / (scores.len() as f64 * 1.05)
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct FeedbackLoop {
    pub query: String,
    pub selected_source: String,
    pub user_rating: f64,
    pub time_spent_ms: u32,
    pub useful: bool,
}

pub struct FeedbackAggregator {
    feedbacks: Vec<FeedbackLoop>,
    max_history: usize,
}

impl Default for FeedbackAggregator {
    fn default() -> Self {
        Self {
            feedbacks: Vec::new(),
            max_history: 10000,
        }
    }
}

impl FeedbackAggregator {
    pub fn new(max_history: usize) -> Self {
        Self {
            feedbacks: Vec::new(),
            max_history,
        }
    }

    pub fn record_feedback(&mut self, feedback: FeedbackLoop) {
        self.feedbacks.push(feedback);
        if self.feedbacks.len() > self.max_history {
            self.feedbacks.remove(0);
        }
    }

    pub fn get_source_reliability(&self, source: &str) -> f64 {
        let relevant: Vec<_> = self
            .feedbacks
            .iter()
            .filter(|f| f.selected_source == source)
            .collect();

        if relevant.is_empty() {
            return 0.5; // Default neutral score
        }

        let useful_count = relevant.iter().filter(|f| f.useful).count();
        useful_count as f64 / relevant.len() as f64
    }

    pub fn get_query_patterns(&self) -> Vec<(String, usize)> {
        let mut patterns = std::collections::HashMap::new();
        for feedback in &self.feedbacks {
            *patterns.entry(feedback.query.clone()).or_insert(0) += 1;
        }
        let mut result: Vec<_> = patterns.into_iter().collect();
        result.sort_by(|a, b| b.1.cmp(&a.1));
        result.into_iter().take(20).collect()
    }

    pub fn count_feedbacks(&self) -> usize {
        self.feedbacks.len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_multimodal_ranker_default() {
        let ranker = MultiModalRanker::default();
        assert_eq!(ranker.modes.len(), 5);
        assert!(ranker.modes.iter().all(|m| m.enabled));
    }

    #[test]
    fn test_fusion_methods() {
        let ranker = MultiModalRanker::new(FusionMethod::WeightedAverage);
        assert_eq!(ranker.fusion_method, FusionMethod::WeightedAverage);

        let ranker = MultiModalRanker::new(FusionMethod::RRF);
        assert_eq!(ranker.fusion_method, FusionMethod::RRF);
    }

    #[test]
    fn test_feedback_recording() {
        let mut aggregator = FeedbackAggregator::default();
        let feedback = FeedbackLoop {
            query: "python".to_string(),
            selected_source: "github".to_string(),
            user_rating: 0.9,
            time_spent_ms: 45000,
            useful: true,
        };
        aggregator.record_feedback(feedback);
        assert_eq!(aggregator.count_feedbacks(), 1);
    }

    #[test]
    fn test_source_reliability() {
        let mut aggregator = FeedbackAggregator::default();
        for i in 0..10 {
            let feedback = FeedbackLoop {
                query: "test".to_string(),
                selected_source: "github".to_string(),
                user_rating: 0.8,
                time_spent_ms: 30000,
                useful: i < 8,
            };
            aggregator.record_feedback(feedback);
        }
        let reliability = aggregator.get_source_reliability("github");
        assert!(reliability > 0.7 && reliability < 0.9);
    }

    #[test]
    fn test_query_patterns() {
        let mut aggregator = FeedbackAggregator::default();
        for _ in 0..5 {
            let feedback = FeedbackLoop {
                query: "python".to_string(),
                selected_source: "github".to_string(),
                user_rating: 0.8,
                time_spent_ms: 30000,
                useful: true,
            };
            aggregator.record_feedback(feedback);
        }
        let patterns = aggregator.get_query_patterns();
        assert!(!patterns.is_empty());
    }

    #[test]
    fn test_feedback_aggregator_max_history() {
        let mut aggregator = FeedbackAggregator::new(5);
        for i in 0..10 {
            let feedback = FeedbackLoop {
                query: format!("query{}", i),
                selected_source: "github".to_string(),
                user_rating: 0.8,
                time_spent_ms: 30000,
                useful: true,
            };
            aggregator.record_feedback(feedback);
        }
        assert_eq!(aggregator.count_feedbacks(), 5);
    }
}
