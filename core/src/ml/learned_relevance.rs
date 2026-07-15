use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum FeedbackType {
    Useful,
    Irrelevant,
    Partial,
    Unknown,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TrainingSample {
    pub query: String,
    pub source: String,
    pub relevance_score: f32,
    pub user_feedback: Option<FeedbackType>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UserFeedback {
    pub query: String,
    pub source: String,
    pub feedback: FeedbackType,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LearnedRelevanceModel {
    pub model_id: String,
    pub training_samples: Vec<TrainingSample>,
    pub accuracy: f32,
    pub weights: HashMap<String, f32>,
    pub is_trained: bool,
}

impl LearnedRelevanceModel {
    pub fn new(model_id: &str) -> Self {
        Self {
            model_id: model_id.to_string(),
            training_samples: Vec::new(),
            accuracy: 0.0,
            weights: HashMap::new(),
            is_trained: false,
        }
    }

    pub fn add_sample(&mut self, sample: TrainingSample) {
        self.training_samples.push(sample);
    }

    pub fn train(&mut self) -> crate::error::Result<()> {
        if self.training_samples.is_empty() {
            return Err(crate::error::Error::ValidationGateFailed(
                "No training samples available".to_string(),
            ));
        }

        let total_samples = self.training_samples.len();

        // Build source-based weights
        let mut source_scores: HashMap<String, Vec<f32>> = HashMap::new();
        for sample in &self.training_samples {
            source_scores
                .entry(sample.source.clone())
                .or_insert_with(Vec::new)
                .push(sample.relevance_score);
        }

        // Average scores per source
        for (source, scores) in source_scores {
            let avg_score = scores.iter().sum::<f32>() / scores.len() as f32;
            self.weights.insert(format!("{}_relevance", source), avg_score);
        }

        // Evaluate accuracy using feedback signals
        let mut correct_predictions = 0;
        for sample in &self.training_samples {
            if let Some(feedback) = &sample.user_feedback {
                match feedback {
                    FeedbackType::Useful if sample.relevance_score > 0.7 => correct_predictions += 1,
                    FeedbackType::Irrelevant if sample.relevance_score <= 0.3 => correct_predictions += 1,
                    FeedbackType::Partial if 0.4 <= sample.relevance_score && sample.relevance_score <= 0.7 => {
                        correct_predictions += 1
                    }
                    FeedbackType::Unknown => correct_predictions += 1,
                    _ => {}
                }
            } else {
                correct_predictions += 1;
            }
        }

        self.accuracy = correct_predictions as f32 / total_samples as f32;
        self.is_trained = true;

        Ok(())
    }

    pub fn predict_relevance(&self, query: &str, source: &str) -> f32 {
        let key = format!("{}_relevance", source);
        let base_weight = self.weights.get(&key).copied().unwrap_or(0.5);

        let query_score = self.score_query_source_match(query, source);
        (base_weight + query_score) / 2.0
    }

    pub fn update_with_feedback(&mut self, feedback: UserFeedback) {
        let score = self.feedback_to_score(&Some(feedback.feedback.clone()));
        let sample = TrainingSample {
            query: feedback.query.clone(),
            source: feedback.source.clone(),
            relevance_score: score,
            user_feedback: Some(feedback.feedback),
        };
        self.add_sample(sample);
    }

    pub fn accuracy_percent(&self) -> f32 {
        self.accuracy * 100.0
    }

    fn feedback_to_score(&self, feedback: &Option<FeedbackType>) -> f32 {
        match feedback {
            Some(FeedbackType::Useful) => 0.9,
            Some(FeedbackType::Partial) => 0.6,
            Some(FeedbackType::Irrelevant) => 0.1,
            Some(FeedbackType::Unknown) => 0.5,
            None => 0.5,
        }
    }

    fn score_query_source_match(&self, query: &str, source: &str) -> f32 {
        let query_lower = query.to_lowercase();
        let source_lower = source.to_lowercase();

        if source_lower.contains(&query_lower) {
            0.8
        } else if query_lower.contains(&source_lower) {
            0.7
        } else {
            let query_words: Vec<&str> = query_lower.split_whitespace().collect();
            let matching_words = query_words
                .iter()
                .filter(|w| source_lower.contains(*w))
                .count();

            0.3 + (matching_words as f32 / query_words.len().max(1) as f32) * 0.4
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_new_model() {
        let model = LearnedRelevanceModel::new("test_model");
        assert_eq!(model.model_id, "test_model");
        assert_eq!(model.training_samples.len(), 0);
        assert!(!model.is_trained);
    }

    #[test]
    fn test_add_sample() {
        let mut model = LearnedRelevanceModel::new("test");
        let sample = TrainingSample {
            query: "customers".to_string(),
            source: "customer_db".to_string(),
            relevance_score: 0.9,
            user_feedback: Some(FeedbackType::Useful),
        };
        model.add_sample(sample);
        assert_eq!(model.training_samples.len(), 1);
    }

    #[test]
    fn test_train_model() {
        let mut model = LearnedRelevanceModel::new("test");
        model.add_sample(TrainingSample {
            query: "customer data".to_string(),
            source: "customer_db".to_string(),
            relevance_score: 0.9,
            user_feedback: Some(FeedbackType::Useful),
        });
        model.add_sample(TrainingSample {
            query: "product data".to_string(),
            source: "customer_db".to_string(),
            relevance_score: 0.2,
            user_feedback: Some(FeedbackType::Irrelevant),
        });

        assert!(model.train().is_ok());
        assert!(model.is_trained);
        assert!(model.accuracy > 0.0);
    }

    #[test]
    fn test_predict_relevance() {
        let mut model = LearnedRelevanceModel::new("test");
        model.add_sample(TrainingSample {
            query: "customer revenue".to_string(),
            source: "revenue_db".to_string(),
            relevance_score: 0.85,
            user_feedback: Some(FeedbackType::Useful),
        });
        model.train().ok();

        let score = model.predict_relevance("customer revenue", "revenue_db");
        assert!(score > 0.5);
    }

    #[test]
    fn test_update_with_feedback() {
        let mut model = LearnedRelevanceModel::new("test");
        model.add_sample(TrainingSample {
            query: "test".to_string(),
            source: "test_db".to_string(),
            relevance_score: 0.5,
            user_feedback: None,
        });
        model.train().ok();

        let feedback = UserFeedback {
            query: "customer segment".to_string(),
            source: "segment_db".to_string(),
            feedback: FeedbackType::Useful,
        };
        model.update_with_feedback(feedback);
        assert_eq!(model.training_samples.len(), 2);
    }

    #[test]
    fn test_feedback_to_score() {
        let model = LearnedRelevanceModel::new("test");
        assert_eq!(model.feedback_to_score(&Some(FeedbackType::Useful)), 0.9);
        assert_eq!(model.feedback_to_score(&Some(FeedbackType::Partial)), 0.6);
        assert_eq!(model.feedback_to_score(&Some(FeedbackType::Irrelevant)), 0.1);
    }
}
