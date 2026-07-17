"""Phase 3 tests - Advanced Optimization & Enterprise Features.

Tests for:
- Learned relevance models
- ML-based optimization
- OpenTelemetry metrics
- Observability
"""

import pytest
from pystreammcp.ml.relevance import (
    RelevanceModel, QueryFeatures, QueryResult, ModelTrainer,
)
from pystreammcp.observability.metrics import MetricsCollector


class TestRelevanceModel:
    """Test learned relevance model."""

    def test_model_initialization(self):
        """Test model initialization."""
        model = RelevanceModel()
        assert model.model_version is not None
        assert model.accuracy == 0.0

    def test_query_features(self):
        """Test query feature extraction."""
        features = QueryFeatures(
            query_text="SELECT * FROM users WHERE age > 18",
            query_length=40,
            intent="retrieve",
            has_filters=True,
            has_joins=False,
            has_aggregates=False,
            estimated_data_size="large",
            time_sensitivity="hourly",
        )

        vector = features.to_vector()
        assert len(vector) > 0
        assert vector[0] == 40  # query_length

    def test_add_training_sample(self):
        """Test adding training samples."""
        model = RelevanceModel()
        features = QueryFeatures(
            query_text="test",
            query_length=10,
            intent="retrieve",
            has_filters=False,
            has_joins=False,
            has_aggregates=False,
            estimated_data_size="small",
            time_sensitivity="daily",
        )
        result = QueryResult(
            query_id="test_1",
            features=features,
            baseline_tokens=1000,
            optimized_tokens=400,
            cost_reduction_percent=60.0,
            execution_time_ms=100.0,
            sources_used=["source_1"],
        )

        model.add_training_sample(result)
        assert len(model.training_data) == 1

    def test_model_training(self):
        """Test model training."""
        model = RelevanceModel()

        # Add samples
        for i in range(20):
            features = QueryFeatures(
                query_text=f"query {i}",
                query_length=50 + i,
                intent=["retrieve", "discover"][i % 2],
                has_filters=i % 2 == 0,
                has_joins=False,
                has_aggregates=False,
                estimated_data_size="medium",
                time_sensitivity="daily",
            )
            result = QueryResult(
                query_id=f"test_{i}",
                features=features,
                baseline_tokens=1000 + i * 100,
                optimized_tokens=400 + i * 50,
                cost_reduction_percent=60.0 + (i % 15),
                execution_time_ms=100.0 + i * 5,
                sources_used=[f"source_{j}" for j in range(i % 3 + 1)],
            )
            model.add_training_sample(result)

        # Train
        result = model.train()
        assert result["status"] == "trained"
        assert result["samples"] == 20
        assert model.accuracy > 0.0

    def test_predict_relevance(self):
        """Test relevance prediction."""
        model = RelevanceModel()
        features = QueryFeatures(
            query_text="test query",
            query_length=50,
            intent="retrieve",
            has_filters=True,
            has_joins=False,
            has_aggregates=False,
            estimated_data_size="medium",
            time_sensitivity="daily",
        )

        prediction = model.predict_relevance(features, ["source_1", "source_2"])
        assert 50 <= prediction <= 75

    def test_rank_sources(self):
        """Test source ranking."""
        model = RelevanceModel()
        features = QueryFeatures(
            query_text="test",
            query_length=30,
            intent="retrieve",
            has_filters=False,
            has_joins=False,
            has_aggregates=False,
            estimated_data_size="small",
            time_sensitivity="daily",
        )

        sources = [
            {"name": "source_1", "type": "database", "size": "small"},
            {"name": "source_2", "type": "cache", "size": "medium"},
            {"name": "source_3", "type": "database", "size": "large"},
        ]

        ranked = model.rank_sources(features, sources)
        assert len(ranked) == 3
        assert all("learned_relevance" in s for s in ranked)

    def test_export_import_model(self):
        """Test model export and import."""
        model1 = RelevanceModel("v1.0")

        # Train model
        for i in range(15):
            features = QueryFeatures(
                query_text=f"q{i}",
                query_length=30,
                intent="retrieve",
                has_filters=False,
                has_joins=False,
                has_aggregates=False,
                estimated_data_size="small",
                time_sensitivity="daily",
            )
            result = QueryResult(
                query_id=f"id_{i}",
                features=features,
                baseline_tokens=1000,
                optimized_tokens=400,
                cost_reduction_percent=60.0,
                execution_time_ms=100.0,
                sources_used=["source_1"],
            )
            model1.add_training_sample(result)

        model1.train()

        # Export
        checkpoint = model1.export_model()
        assert checkpoint["model_version"] == "v1.0"

        # Import to new model
        model2 = RelevanceModel()
        model2.import_model(checkpoint)
        assert model2.accuracy == model1.accuracy


class TestModelTrainer:
    """Test model trainer."""

    def test_trainer_initialization(self):
        """Test trainer initialization."""
        model = RelevanceModel()
        trainer = ModelTrainer(model)
        assert trainer.model == model

    def test_load_production_data(self):
        """Test loading production data."""
        model = RelevanceModel()
        trainer = ModelTrainer(model)

        samples = trainer.load_production_data("mock_data")
        assert samples > 0
        assert len(model.training_data) == samples

    def test_train_and_validate(self):
        """Test training and validation."""
        model = RelevanceModel()
        trainer = ModelTrainer(model)

        trainer.load_production_data("mock_data")
        result = trainer.train_and_validate()

        assert result["status"] == "trained"
        assert "best_accuracy" in result

    def test_training_history(self):
        """Test training history tracking."""
        model = RelevanceModel()
        trainer = ModelTrainer(model)

        trainer.load_production_data("mock_data")
        trainer.train_and_validate()

        history = trainer.get_training_history()
        assert len(history) > 0


class TestMetricsCollector:
    """Test OpenTelemetry metrics collector."""

    def test_collector_initialization(self):
        """Test collector initialization."""
        collector = MetricsCollector("test_service")
        assert collector.service_name == "test_service"
        assert len(collector.metrics) > 0

    def test_record_query(self):
        """Test recording query metrics."""
        collector = MetricsCollector()

        collector.record_query(
            duration_ms=150.5,
            baseline_tokens=1000,
            optimized_tokens=400,
            cost_reduction=60.0,
            agent_id="test_agent",
            intent="retrieve",
        )

        assert len(collector.metrics["query_duration_ms"].points) > 0
        assert len(collector.metrics["query_count"].points) > 0

    def test_record_error(self):
        """Test recording errors."""
        collector = MetricsCollector()

        collector.record_error("timeout", "agent_1")
        collector.record_error("invalid_query", "agent_2")

        assert len(collector.metrics["errors"].points) == 2

    def test_record_model_accuracy(self):
        """Test recording model accuracy."""
        collector = MetricsCollector()

        collector.record_model_accuracy(85.5, "v1.0")

        assert len(collector.metrics["model_accuracy"].points) > 0

    def test_export_prometheus(self):
        """Test Prometheus format export."""
        collector = MetricsCollector()

        collector.record_query(100.0, 1000, 400, 60.0, "agent_1", "retrieve")
        collector.record_model_accuracy(80.0, "v1.0")

        prometheus = collector.export_prometheus()
        assert "pystreammcp_query_duration_ms" in prometheus
        assert "pystreammcp_model_accuracy" in prometheus

    def test_get_summary(self):
        """Test metrics summary."""
        collector = MetricsCollector()

        for i in range(5):
            collector.record_query(
                duration_ms=100.0 + i * 10,
                baseline_tokens=1000,
                optimized_tokens=400,
                cost_reduction=60.0 + i,
                agent_id="agent_1",
                intent="retrieve",
            )

        summary = collector.get_summary()
        assert summary["total_queries"] == 5
        assert summary["avg_cost_reduction"] > 60.0

    def test_flush_buffer(self):
        """Test buffer flushing."""
        collector = MetricsCollector()

        collector.record_query(100.0, 1000, 400, 60.0, "agent_1", "retrieve")
        collector.record_query(150.0, 1500, 500, 65.0, "agent_2", "discover")

        buffer = collector.flush_buffer()
        assert len(buffer) == 2
        assert len(collector.buffer) == 0


class TestPhase3Integration:
    """Test Phase 3 integration scenarios."""

    def test_ml_observability_pipeline(self):
        """Test ML model training with observability."""
        # Create model and trainer
        model = RelevanceModel("v1.0")
        trainer = ModelTrainer(model)

        # Load data
        samples = trainer.load_production_data("prod")
        assert samples > 0

        # Create metrics collector
        collector = MetricsCollector()

        # Train model
        result = trainer.train_and_validate()
        collector.record_model_accuracy(model.accuracy * 100, "v1.0")

        # Record some queries using the model
        for i in range(3):
            features = QueryFeatures(
                query_text=f"q{i}",
                query_length=50,
                intent="retrieve",
                has_filters=True,
                has_joins=False,
                has_aggregates=False,
                estimated_data_size="medium",
                time_sensitivity="daily",
            )

            prediction = model.predict_relevance(features, ["source_1"])
            collector.record_query(100.0, 1000, 400, prediction, "agent_1", "retrieve")

        # Verify results
        summary = collector.get_summary()
        assert summary["total_queries"] == 3
        assert model.accuracy > 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
