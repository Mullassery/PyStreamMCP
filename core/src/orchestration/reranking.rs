/// Contextual reranking based on query analysis and retrieved content quality

use serde::{Serialize, Deserialize};
use crate::metadata::RankedCandidate;

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct RerankedCandidate {
    pub original: RankedCandidate,
    pub stage1_score: f64,
    pub contextual_adjustment: f64,
    pub final_score: f64,
    pub rerank_reason: String,
}

pub struct ContextualReranker {
    query_context: String,
    user_context: Option<UserContext>,
}

#[derive(Clone, Debug)]
pub struct UserContext {
    pub expertise_level: ExpertiseLevel,
    pub preferred_sources: Vec<String>,
    pub domain_focus: Option<String>,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum ExpertiseLevel {
    Beginner,
    Intermediate,
    Advanced,
    Expert,
}

impl ContextualReranker {
    pub fn new(query_context: String) -> Self {
        Self {
            query_context,
            user_context: None,
        }
    }

    pub fn with_user_context(mut self, context: UserContext) -> Self {
        self.user_context = Some(context);
        self
    }

    pub fn rerank(
        &self,
        candidates: Vec<RankedCandidate>,
    ) -> Vec<RerankedCandidate> {
        candidates
            .into_iter()
            .map(|candidate| {
                let stage1_score = candidate.score;
                let contextual_adjustment = self.calculate_adjustment(&candidate);
                let final_score = (stage1_score * 0.7) + (contextual_adjustment * 0.3);
                let reason = self.generate_reason(&candidate, contextual_adjustment);

                RerankedCandidate {
                    original: candidate,
                    stage1_score,
                    contextual_adjustment,
                    final_score,
                    rerank_reason: reason,
                }
            })
            .collect()
    }

    fn calculate_adjustment(&self, _candidate: &RankedCandidate) -> f64 {
        let mut adjustment = 1.0;

        // User expertise adjustment
        if let Some(context) = &self.user_context {
            adjustment *= match context.expertise_level {
                ExpertiseLevel::Beginner => 0.85,    // Prefer simpler sources
                ExpertiseLevel::Intermediate => 1.0,
                ExpertiseLevel::Advanced => 1.1,     // Prefer technical sources
                ExpertiseLevel::Expert => 1.2,       // Prefer comprehensive sources
            };
        }

        // Query complexity adjustment
        if self.query_context.contains("explain") || self.query_context.contains("how") {
            adjustment *= 1.1; // Prefer tutorial-style content
        }

        adjustment.min(1.5).max(0.5)
    }

    fn generate_reason(&self, candidate: &RankedCandidate, adjustment: f64) -> String {
        if adjustment > 1.1 {
            format!("Boosted for {} - contextual match", candidate.source)
        } else if adjustment < 0.9 {
            format!("Adjusted for {} - expertise level mismatch", candidate.source)
        } else {
            format!("Contextually relevant - {}", candidate.source)
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_reranker_creation() {
        let reranker = ContextualReranker::new("python".to_string());
        assert_eq!(reranker.query_context, "python");
    }

    #[test]
    fn test_reranker_with_user_context() {
        let context = UserContext {
            expertise_level: ExpertiseLevel::Expert,
            preferred_sources: vec!["academic".to_string()],
            domain_focus: Some("machine learning".to_string()),
        };
        let reranker = ContextualReranker::new("python".to_string())
            .with_user_context(context);
        assert!(reranker.user_context.is_some());
    }

    #[test]
    fn test_expertise_adjustment_beginner() {
        let context = UserContext {
            expertise_level: ExpertiseLevel::Beginner,
            preferred_sources: vec![],
            domain_focus: None,
        };
        let reranker = ContextualReranker::new("python".to_string())
            .with_user_context(context);
        let adjustment = reranker.calculate_adjustment(
            &RankedCandidate {
                source: "github".to_string(),
                score: 0.8,
                rank: 1,
            }
        );
        assert!(adjustment < 1.0);
    }

    #[test]
    fn test_expertise_adjustment_expert() {
        let context = UserContext {
            expertise_level: ExpertiseLevel::Expert,
            preferred_sources: vec![],
            domain_focus: None,
        };
        let reranker = ContextualReranker::new("python".to_string())
            .with_user_context(context);
        let adjustment = reranker.calculate_adjustment(
            &RankedCandidate {
                source: "arxiv".to_string(),
                score: 0.8,
                rank: 1,
            }
        );
        assert!(adjustment > 1.0);
    }
}
