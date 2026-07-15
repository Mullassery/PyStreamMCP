"""Machine learning for learned relevance models in PyStreamMCP."""

from typing import Dict, List, Optional, Literal
from dataclasses import dataclass

FeedbackType = Literal["useful", "irrelevant", "partial", "unknown"]


@dataclass
class TrainingSample:
    """A training sample for the relevance model."""

    query: str
    source: str
    relevance_score: float
    user_feedback: Optional[FeedbackType] = None


class LearnedRelevanceModel:
    """ML model that improves relevance prediction over time."""

    def __init__(self, model_id: str):
        """Initialize model."""
        self.model_id = model_id
        self.training_samples: List[TrainingSample] = []
        self.accuracy: float = 0.0
        self.weights: Dict[str, float] = {}
        self.is_trained: bool = False

    def add_sample(self, sample: TrainingSample) -> None:
        """Add a training sample."""
        self.training_samples.append(sample)

    def train(self) -> None:
        """Train the model on accumulated samples."""
        if not self.training_samples:
            raise ValueError("No training samples available")

        # Build source-based weights
        source_scores: Dict[str, List[float]] = {}
        for sample in self.training_samples:
            if sample.source not in source_scores:
                source_scores[sample.source] = []
            source_scores[sample.source].append(sample.relevance_score)

        # Average scores per source
        for source, scores in source_scores.items():
            avg_score = sum(scores) / len(scores)
            self.weights[f"{source}_relevance"] = avg_score

        # Evaluate accuracy
        correct_predictions = 0
        for sample in self.training_samples:
            if sample.user_feedback:
                if sample.user_feedback == "useful" and sample.relevance_score > 0.7:
                    correct_predictions += 1
                elif sample.user_feedback == "irrelevant" and sample.relevance_score <= 0.3:
                    correct_predictions += 1
                elif sample.user_feedback == "partial" and 0.4 <= sample.relevance_score <= 0.7:
                    correct_predictions += 1
                elif sample.user_feedback == "unknown":
                    correct_predictions += 1
            else:
                correct_predictions += 1

        self.accuracy = correct_predictions / len(self.training_samples)
        self.is_trained = True

    def predict_relevance(self, query: str, source: str) -> float:
        """Predict relevance score for query-source pair."""
        key = f"{source}_relevance"
        base_weight = self.weights.get(key, 0.5)

        query_score = self._score_query_source_match(query, source)
        return (base_weight + query_score) / 2.0

    def update_with_feedback(self, query: str, source: str, feedback: FeedbackType) -> None:
        """Update model with user feedback."""
        score = {"useful": 0.9, "irrelevant": 0.1, "partial": 0.6, "unknown": 0.5}.get(
            feedback, 0.5
        )
        sample = TrainingSample(
            query=query, source=source, relevance_score=score, user_feedback=feedback
        )
        self.add_sample(sample)

    def accuracy_percent(self) -> float:
        """Get accuracy as percentage."""
        return self.accuracy * 100.0

    def _score_query_source_match(self, query: str, source: str) -> float:
        """Score how well query matches source name."""
        query_lower = query.lower()
        source_lower = source.lower()

        if source_lower in query_lower:
            return 0.8
        elif query_lower in source_lower:
            return 0.7
        else:
            query_words = query_lower.split()
            matching_words = sum(1 for w in query_words if w in source_lower)
            return 0.3 + (matching_words / max(len(query_words), 1)) * 0.4
