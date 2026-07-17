"""Learned Relevance Model for PyStreamMCP.

ML-based relevance scoring that learns from query patterns
to optimize source selection and cost reduction.
"""

from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, field
import json
from datetime import datetime


@dataclass
class QueryFeatures:
    """Features extracted from a query for ML model."""

    query_text: str
    query_length: int
    intent: str  # retrieve, discover, aggregate, synthesize, analyze
    has_filters: bool
    has_joins: bool
    has_aggregates: bool
    estimated_data_size: str  # small, medium, large
    time_sensitivity: str  # realtime, hourly, daily
    custom_features: Dict[str, float] = field(default_factory=dict)

    def to_vector(self) -> List[float]:
        """Convert features to vector for ML model."""
        intent_map = {"retrieve": 0, "discover": 1, "aggregate": 2, "synthesize": 3, "analyze": 4}
        size_map = {"small": 0, "medium": 1, "large": 2}
        time_map = {"realtime": 0, "hourly": 1, "daily": 2}

        return [
            self.query_length,
            intent_map.get(self.intent, 0),
            float(self.has_filters),
            float(self.has_joins),
            float(self.has_aggregates),
            size_map.get(self.estimated_data_size, 1),
            time_map.get(self.time_sensitivity, 2),
        ] + list(self.custom_features.values())


@dataclass
class QueryResult:
    """Result of a query with relevance feedback."""

    query_id: str
    features: QueryFeatures
    baseline_tokens: int
    optimized_tokens: int
    cost_reduction_percent: float
    execution_time_ms: float
    sources_used: List[str]
    user_satisfaction: Optional[float] = None  # 0-1 rating
    actual_quality: Optional[float] = None  # Measured quality metric
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class RelevanceModel:
    """Learned relevance model using historical query data.

    Learns which sources are most relevant for different query types,
    enabling better source selection and cost optimization.
    """

    def __init__(self, model_version: str = "v1.0"):
        """Initialize relevance model.

        Args:
            model_version: Model version identifier
        """
        self.model_version = model_version
        self.training_data: List[QueryResult] = []
        self.learned_weights: Dict[str, float] = {}
        self.source_relevance_cache: Dict[str, Dict[str, float]] = {}
        self.accuracy: float = 0.0

    def add_training_sample(self, result: QueryResult) -> None:
        """Add a query result to training data.

        Args:
            result: Query result with feedback
        """
        self.training_data.append(result)

    def train(self, test_size: float = 0.2) -> Dict[str, Any]:
        """Train the model on accumulated data.

        Args:
            test_size: Fraction of data to use for testing

        Returns:
            Training metrics
        """
        if len(self.training_data) < 10:
            return {
                "status": "insufficient_data",
                "samples": len(self.training_data),
                "minimum_required": 10,
            }

        # Simulate ML training
        # In production, use scikit-learn, TensorFlow, etc.
        correct = 0
        total = len(self.training_data)

        for result in self.training_data:
            predicted = self.predict_relevance(result.features, result.sources_used)
            actual = result.cost_reduction_percent

            if abs(predicted - actual) < 10:  # Within 10% is "correct"
                correct += 1

        self.accuracy = correct / total if total > 0 else 0.0

        # Learn source weights
        self._learn_source_weights()

        return {
            "status": "trained",
            "samples": total,
            "accuracy": self.accuracy,
            "model_version": self.model_version,
            "timestamp": datetime.now().isoformat(),
        }

    def predict_relevance(self, features: QueryFeatures, candidate_sources: List[str]) -> float:
        """Predict cost reduction for a query using learned model.

        Args:
            features: Query features
            candidate_sources: Available data sources

        Returns:
            Predicted cost reduction percentage
        """
        if not self.learned_weights:
            return 65.0  # Default if model not trained

        # Simulate prediction
        # In production, use trained model to score
        base_score = 60.0

        # Adjust based on features
        if features.intent == "retrieve":
            base_score += 5.0
        elif features.intent == "discover":
            base_score += 3.0

        if features.has_filters:
            base_score += 2.0
        if features.has_aggregates:
            base_score += 3.0

        # Adjust based on sources
        if len(candidate_sources) > 0:
            source_bonus = sum(
                self.source_relevance_cache.get(source, {}).get("weight", 0)
                for source in candidate_sources
            ) / len(candidate_sources)
            base_score += source_bonus

        return min(75.0, max(50.0, base_score))

    def rank_sources(
        self, features: QueryFeatures, available_sources: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Rank available sources by relevance using learned model.

        Args:
            features: Query features
            available_sources: List of available sources

        Returns:
            Ranked sources with relevance scores
        """
        ranked = []

        for source in available_sources:
            source_name = source.get("name", "unknown")
            relevance = self.source_relevance_cache.get(source_name, {}).get("relevance", 0.7)

            # Adjust based on query features
            if features.estimated_data_size == "small" and source.get("size") == "small":
                relevance += 0.1
            elif features.estimated_data_size == "large" and source.get("size") == "large":
                relevance += 0.05

            ranked.append({
                **source,
                "learned_relevance": min(0.99, relevance),
                "model_version": self.model_version,
            })

        # Sort by learned relevance
        ranked.sort(key=lambda x: x["learned_relevance"], reverse=True)
        return ranked

    def _learn_source_weights(self) -> None:
        """Learn source weights from training data."""
        source_scores: Dict[str, List[float]] = {}

        for result in self.training_data:
            for source in result.sources_used:
                if source not in source_scores:
                    source_scores[source] = []
                source_scores[source].append(result.cost_reduction_percent)

        # Calculate source weights
        for source, scores in source_scores.items():
            avg_score = sum(scores) / len(scores) if scores else 0.5
            self.source_relevance_cache[source] = {
                "weight": (avg_score - 50) / 25,  # Normalize to -1 to 1
                "relevance": avg_score / 100,  # Normalize to 0 to 1
                "samples": len(scores),
            }

    def export_model(self) -> Dict[str, Any]:
        """Export model for deployment.

        Returns:
            Model checkpoint
        """
        return {
            "model_version": self.model_version,
            "accuracy": self.accuracy,
            "source_weights": self.source_relevance_cache,
            "samples_trained": len(self.training_data),
            "timestamp": datetime.now().isoformat(),
        }

    def import_model(self, checkpoint: Dict[str, Any]) -> None:
        """Import model from checkpoint.

        Args:
            checkpoint: Model checkpoint
        """
        self.model_version = checkpoint.get("model_version", "unknown")
        self.accuracy = checkpoint.get("accuracy", 0.0)
        self.source_relevance_cache = checkpoint.get("source_weights", {})


class ModelTrainer:
    """Trainer for relevance models using production query data."""

    def __init__(self, model: RelevanceModel):
        """Initialize trainer.

        Args:
            model: Model to train
        """
        self.model = model
        self.training_history = []

    def load_production_data(self, data_source: str) -> int:
        """Load training data from production queries.

        Args:
            data_source: Path to data (file, database, API endpoint)

        Returns:
            Number of samples loaded
        """
        # In production, load from actual data source
        # For now, simulate
        sample_results = [
            QueryResult(
                query_id=f"prod_query_{i}",
                features=QueryFeatures(
                    query_text=f"Sample query {i}",
                    query_length=100 + (i * 10),
                    intent=["retrieve", "discover", "aggregate"][i % 3],
                    has_filters=i % 2 == 0,
                    has_joins=i % 3 == 0,
                    has_aggregates=i % 4 == 0,
                    estimated_data_size=["small", "medium", "large"][i % 3],
                    time_sensitivity=["realtime", "hourly", "daily"][i % 3],
                ),
                baseline_tokens=1000 + (i * 100),
                optimized_tokens=400 + (i * 50),
                cost_reduction_percent=60.0 + (i % 15),
                execution_time_ms=100.0 + (i * 10),
                sources_used=[f"source_{j}" for j in range(i % 5 + 1)],
                user_satisfaction=0.7 + (0.3 * (i % 10) / 10),
            )
            for i in range(50)
        ]

        for result in sample_results:
            self.model.add_training_sample(result)

        return len(sample_results)

    def train_and_validate(self) -> Dict[str, Any]:
        """Train model and validate performance.

        Returns:
            Training results
        """
        results = self.model.train()
        self.training_history.append(results)

        return {
            **results,
            "history_length": len(self.training_history),
            "best_accuracy": max(
                (r.get("accuracy", 0.0) for r in self.training_history),
                default=0.0
            ),
        }

    def get_training_history(self) -> List[Dict[str, Any]]:
        """Get training history.

        Returns:
            List of training results
        """
        return self.training_history
