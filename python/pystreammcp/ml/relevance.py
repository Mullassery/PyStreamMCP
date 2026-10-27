"""Learned Relevance Model for PyStreamMCP.

ML-based relevance scoring that learns from query patterns
to optimize source selection and cost reduction.
"""

from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, field
import json
from datetime import datetime
from pathlib import Path


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
        intent_map = {
            "retrieve": 0,
            "discover": 1,
            "aggregate": 2,
            "synthesize": 3,
            "analyze": 4,
        }
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
        """Fit the heuristic model and evaluate it on a held-out split.

        Args:
            test_size: Fraction of accumulated samples held out for evaluation
                (0 means evaluate on the same samples used to fit).

        Returns:
            Training metrics, including the train/test split sizes.
        """
        if len(self.training_data) < 10:
            return {
                "status": "insufficient_data",
                "samples": len(self.training_data),
                "minimum_required": 10,
            }
        if not 0.0 <= test_size < 1.0:
            raise ValueError("test_size must be >= 0 and < 1")

        total = len(self.training_data)
        test_count = int(total * test_size)
        train_count = total - test_count
        train_data = self.training_data[:train_count]
        test_data = self.training_data[train_count:] if test_count else train_data

        # Refit from scratch so repeated training calls are reproducible.
        self.source_relevance_cache = {}
        self._learn_source_weights(train_data)

        correct = 0
        for result in test_data:
            predicted = self.predict_relevance(result.features, result.sources_used)
            actual = result.cost_reduction_percent
            if abs(predicted - actual) < 10:
                correct += 1

        self.accuracy = correct / len(test_data) if test_data else 0.0

        return {
            "status": "trained",
            "samples": total,
            "train_samples": len(train_data),
            "test_samples": len(test_data),
            "accuracy": self.accuracy,
            "model_version": self.model_version,
            "timestamp": datetime.now().isoformat(),
        }

    def predict_relevance(
        self, features: QueryFeatures, candidate_sources: List[str]
    ) -> float:
        """Predict cost reduction for a query using learned model.

        Args:
            features: Query features
            candidate_sources: Available data sources

        Returns:
            Predicted cost reduction percentage
        """
        if not self.source_relevance_cache:
            return 65.0  # Default before any source weights have been learned

        # Feature-weighted heuristic prediction. This is deliberately a small,
        # dependency-free model rather than a trained neural network.
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
            relevance = self.source_relevance_cache.get(source_name, {}).get(
                "relevance", 0.7
            )

            # Adjust based on query features
            if (
                features.estimated_data_size == "small"
                and source.get("size") == "small"
            ):
                relevance += 0.1
            elif (
                features.estimated_data_size == "large"
                and source.get("size") == "large"
            ):
                relevance += 0.05

            ranked.append(
                {
                    **source,
                    "learned_relevance": min(0.99, relevance),
                    "model_version": self.model_version,
                }
            )

        # Sort by learned relevance
        ranked.sort(key=lambda x: x["learned_relevance"], reverse=True)
        return ranked

    def _learn_source_weights(
        self, training_data: Optional[List[QueryResult]] = None
    ) -> None:
        """Learn source weights from the supplied training samples."""
        source_scores: Dict[str, List[float]] = {}

        for result in training_data if training_data is not None else self.training_data:
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
        """Load training samples from a JSON array or JSONL file.

        Args:
            data_source: Path to a UTF-8 JSON/JSONL file containing query
                results. Each record must include ``query_id``, ``features``,
                ``baseline_tokens``, ``optimized_tokens``,
                ``cost_reduction_percent``, ``execution_time_ms``, and
                ``sources_used``.

        Returns:
            Number of samples loaded.

        Raises:
            FileNotFoundError: If ``data_source`` is not an existing file.
            ValueError: If the file is not valid JSON/JSONL or a record is
                missing required fields.
        """
        path = Path(data_source)
        text = path.read_text(encoding="utf-8")
        stripped = text.lstrip()
        if not stripped:
            return 0

        try:
            if stripped.startswith("["):
                records = json.loads(stripped)
                if not isinstance(records, list):
                    raise ValueError("JSON training file must contain an array")
            else:
                records = [
                    json.loads(line)
                    for line in text.splitlines()
                    if line.strip()
                ]
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in {path}: {exc}") from exc

        parsed: List[QueryResult] = []
        for index, record in enumerate(records):
            if not isinstance(record, dict):
                raise ValueError(f"Training record {index} must be an object")
            try:
                features_data = record["features"]
                if not isinstance(features_data, dict):
                    raise TypeError("features must be an object")
                parsed.append(
                    QueryResult(
                        query_id=str(record["query_id"]),
                        features=QueryFeatures(**features_data),
                        baseline_tokens=int(record["baseline_tokens"]),
                        optimized_tokens=int(record["optimized_tokens"]),
                        cost_reduction_percent=float(
                            record["cost_reduction_percent"]
                        ),
                        execution_time_ms=float(record["execution_time_ms"]),
                        sources_used=list(record["sources_used"]),
                        user_satisfaction=record.get("user_satisfaction"),
                        actual_quality=record.get("actual_quality"),
                        **(
                            {"timestamp": record["timestamp"]}
                            if "timestamp" in record
                            else {}
                        ),
                    )
                )
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(
                    f"Invalid training record {index} in {path}: {exc}"
                ) from exc

        for result in parsed:
            self.model.add_training_sample(result)
        return len(parsed)

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
                (r.get("accuracy", 0.0) for r in self.training_history), default=0.0
            ),
        }

    def get_training_history(self) -> List[Dict[str, Any]]:
        """Get training history.

        Returns:
            List of training results
        """
        return self.training_history
