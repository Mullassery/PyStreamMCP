"""Tests for Phase 3 items 1-2: Auto Tagging & Advanced Optimization."""

import pytest
from pystreammcp.ml.tagging import (
    PromptClassifier, PromptIntent, PromptComplexity,
)
from pystreammcp.optimization.advanced import (
    StreamingContextWindow, MultiAgentContextSharing, CostOptimizationEngine,
)


class TestAutoPromptTagging:
    """Test auto prompt tagging."""

    def test_classifier_init(self):
        """Test classifier creation."""
        classifier = PromptClassifier()
        assert classifier is not None

    def test_intent_detection_retrieve(self):
        """Test detecting retrieve intent."""
        classifier = PromptClassifier()
        analysis = classifier.analyze("Get all users from database")
        assert analysis.intent == PromptIntent.RETRIEVE

    def test_intent_detection_analyze(self):
        """Test detecting analyze intent."""
        classifier = PromptClassifier()
        analysis = classifier.analyze("Analyze the total revenue by region")
        assert analysis.intent == PromptIntent.ANALYZE

    def test_complexity_simple(self):
        """Test detecting simple complexity."""
        classifier = PromptClassifier()
        analysis = classifier.analyze("Get user by ID")
        assert analysis.complexity == PromptComplexity.SIMPLE

    def test_complexity_moderate(self):
        """Test detecting moderate complexity."""
        classifier = PromptClassifier()
        analysis = classifier.analyze("Get users where status = active and region = US")
        assert analysis.complexity == PromptComplexity.MODERATE

    def test_domain_detection(self):
        """Test domain detection."""
        classifier = PromptClassifier()
        analysis = classifier.analyze("Calculate total patient treatment costs")
        assert analysis.domain == "healthcare"

    def test_tag_generation(self):
        """Test tag generation."""
        classifier = PromptClassifier()
        analysis = classifier.analyze("Retrieve all customers from finance database")
        assert len(analysis.tags) > 0
        assert any(tag.name == "intent" for tag in analysis.tags)

    def test_quality_score(self):
        """Test quality score calculation."""
        classifier = PromptClassifier()
        analysis = classifier.analyze("Get specific customer data for ID 12345")
        assert 0 <= analysis.quality_score <= 1

    def test_routing_strategy(self):
        """Test routing strategy generation."""
        classifier = PromptClassifier()
        analysis = classifier.analyze("Get user")
        strategy = classifier.get_routing_strategy(analysis)
        assert "parallelizable" in strategy
        assert "cache_friendly" in strategy

    def test_batch_analyze(self):
        """Test batch analysis."""
        classifier = PromptClassifier()
        prompts = ["Get users", "Analyze revenue", "Find customers"]
        results = classifier.batch_analyze(prompts)
        assert len(results) == 3

    def test_training(self):
        """Test classifier training."""
        classifier = PromptClassifier()

        # Add training samples
        for i in range(10):
            analysis = classifier.analyze(f"Sample prompt {i}")
            classifier.add_training_sample(analysis)

        result = classifier.train()
        assert result["status"] == "trained"
        assert result["samples"] == 10


class TestStreamingContextWindow:
    """Test streaming context windows."""

    def test_streaming_init(self):
        """Test streaming creation."""
        streaming = StreamingContextWindow()
        assert streaming is not None

    def test_create_stream(self):
        """Test creating a stream."""
        streaming = StreamingContextWindow()
        stream_id = streaming.create_stream("ctx1", "agent1", "test query")
        assert stream_id == "ctx1"

    def test_stream_chunk(self):
        """Test streaming a chunk."""
        streaming = StreamingContextWindow()
        streaming.create_stream("ctx1", "agent1", "test query")
        streaming.stream_chunk("ctx1", {"data": "chunk1", "tokens": 50})

        stats = streaming.get_stream_stats("ctx1")
        assert stats["chunk_count"] == 1
        assert stats["streamed_tokens"] == 50

    def test_multiple_chunks(self):
        """Test streaming multiple chunks."""
        streaming = StreamingContextWindow()
        streaming.create_stream("ctx1", "agent1", "test query")

        for i in range(5):
            streaming.stream_chunk("ctx1", {"data": f"chunk{i}", "tokens": 100})

        stats = streaming.get_stream_stats("ctx1")
        assert stats["chunk_count"] == 5
        assert stats["streamed_tokens"] == 500

    def test_close_stream(self):
        """Test closing a stream."""
        streaming = StreamingContextWindow()
        streaming.create_stream("ctx1", "agent1", "test query")
        streaming.stream_chunk("ctx1", {"data": "test", "tokens": 100})

        result = streaming.close_stream("ctx1")
        assert result["total_chunks"] == 1
        assert result["total_tokens"] == 100


class TestMultiAgentContextSharing:
    """Test multi-agent context sharing."""

    def test_sharing_init(self):
        """Test sharing creation."""
        sharing = MultiAgentContextSharing()
        assert sharing is not None

    def test_create_shared_context(self):
        """Test creating shared context."""
        sharing = MultiAgentContextSharing()
        ctx_id = sharing.create_shared_context(
            "ctx1", "agent1", {"data": "shared"}
        )
        assert ctx_id == "ctx1"

    def test_request_context(self):
        """Test requesting shared context."""
        sharing = MultiAgentContextSharing()
        sharing.create_shared_context("ctx1", "agent1", {"result": "test"})

        data = sharing.request_context("ctx1", "agent2")
        assert data is not None
        assert data["result"] == "test"

    def test_reuse_tracking(self):
        """Test reuse count tracking."""
        sharing = MultiAgentContextSharing()
        sharing.create_shared_context("ctx1", "agent1", {"data": "test"})

        # Request from multiple agents
        for i in range(3):
            sharing.request_context("ctx1", f"agent{i+2}")

        stats = sharing.get_context_reuse_stats()
        assert stats["total_reuses"] == 3

    def test_ttl_expiration(self):
        """Test TTL expiration."""
        sharing = MultiAgentContextSharing()
        sharing.create_shared_context("ctx1", "agent1", {"data": "test"}, ttl_seconds=0)

        # Should be expired
        data = sharing.request_context("ctx1", "agent2")
        assert data is None

    def test_cleanup_expired(self):
        """Test cleanup of expired contexts."""
        sharing = MultiAgentContextSharing()
        sharing.create_shared_context("ctx1", "agent1", {"data": "test"}, ttl_seconds=0)

        removed = sharing.cleanup_expired()
        assert removed == 1


class TestAdvancedOptimization:
    """Test advanced optimization engine."""

    def test_engine_init(self):
        """Test engine creation."""
        engine = CostOptimizationEngine()
        assert engine is not None

    def test_single_agent_optimization(self):
        """Test single agent optimization."""
        engine = CostOptimizationEngine()
        plan = engine.optimize_multi_agent_query(["agent1"], "test query")

        assert len(plan["strategies"]) > 0
        assert any(s["type"] == "streaming" for s in plan["strategies"])

    def test_multi_agent_optimization(self):
        """Test multi-agent optimization."""
        engine = CostOptimizationEngine()
        plan = engine.optimize_multi_agent_query(
            ["agent1", "agent2", "agent3"],
            "test query"
        )

        assert len(plan["strategies"]) >= 2
        assert any(s["type"] == "shared_context" for s in plan["strategies"])

    def test_speedup_estimation_single(self):
        """Test speedup for single agent."""
        engine = CostOptimizationEngine()
        speedup = engine.estimate_speedup(1)
        assert speedup > 1.0

    def test_speedup_estimation_multi(self):
        """Test speedup for multiple agents."""
        engine = CostOptimizationEngine()
        speedup = engine.estimate_speedup(5, sharing_enabled=True)
        assert speedup > 1.5

    def test_optimization_history(self):
        """Test optimization history tracking."""
        engine = CostOptimizationEngine()

        engine.optimize_multi_agent_query(["agent1"], "query1")
        engine.optimize_multi_agent_query(["agent1", "agent2"], "query2")

        assert len(engine.optimization_history) == 2


class TestPhase3Completion:
    """Test Phase 3 complete pipeline."""

    def test_tagging_to_optimization(self):
        """Test prompt tagging driving optimization."""
        classifier = PromptClassifier()
        engine = CostOptimizationEngine()

        # Analyze prompt
        analysis = classifier.analyze("Get user data for agents 1-3")

        # Get routing strategy
        strategy = classifier.get_routing_strategy(analysis)
        assert strategy is not None

        # Optimize for multiple agents
        plan = engine.optimize_multi_agent_query(["agent1", "agent2"], analysis.text)
        assert plan["estimated_savings_percent"] > 0

    def test_streaming_with_sharing(self):
        """Test streaming + sharing together."""
        streaming = StreamingContextWindow()
        sharing = MultiAgentContextSharing()

        # Agent 1 streams and creates shared context
        streaming.create_stream("ctx1", "agent1", "query")

        chunks = []
        for i in range(3):
            chunk = {"data": f"chunk{i}", "tokens": 100}
            streaming.stream_chunk("ctx1", chunk)
            chunks.append(chunk)

        # Agent 1 creates shared context
        shared_data = {"chunks": chunks, "total_tokens": 300}
        sharing.create_shared_context("ctx1", "agent1", shared_data)

        # Agents 2-3 request shared context
        data = sharing.request_context("ctx1", "agent2")
        assert data is not None
        assert len(data["chunks"]) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
