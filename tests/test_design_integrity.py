"""Design-integrity regressions for public package surfaces.

These tests exist because several parallel/legacy modules had drifted out of
sync with the package-level API: shadowed modules, stale ``__all__`` entries,
fabricated discovery data, and simulated training/decomposition output.
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest

import pystreammcp
from pystreammcp.adapters import AdapterConfig, FrameworkType
from pystreammcp.discovery import SourceRegistry
from pystreammcp.ml.relevance import (
    ModelTrainer,
    QueryFeatures,
    QueryResult as MLQueryResult,
    RelevanceModel,
)
from pystreammcp.optimization.decomposition import QueryDecomposer, QueryType


def _adapter_cases():
    cases = []

    from pystreammcp.integrations.llamaindex import LlamaIndexAdapter
    from pystreammcp.integrations.semantic_kernel import SemanticKernelAdapter

    cases.extend(
        [
            (LlamaIndexAdapter, FrameworkType.LLAMAINDEX, {}),
            (SemanticKernelAdapter, FrameworkType.SEMANTIC_KERNEL, {}),
        ]
    )

    from pystreammcp.integrations.crewai import CrewAIAdapter
    from pystreammcp.integrations.haystack import HaystackAdapter
    from pystreammcp.integrations.pydantic_ai import PydanticAIAdapter

    cases.extend(
        [
            (CrewAIAdapter, FrameworkType.CREWAI, {"experimental": True}),
            (PydanticAIAdapter, FrameworkType.PYDANTIC_AI, {"experimental": True}),
            (HaystackAdapter, FrameworkType.HAYSTACK, {"experimental": True}),
        ]
    )
    return cases


@pytest.mark.parametrize("adapter_cls,framework,extra", _adapter_cases())
def test_adapter_discovery_uses_shared_source_registry(adapter_cls, framework, extra):
    registry = SourceRegistry()
    config = AdapterConfig(
        framework=framework,
        agent_id=f"{framework.value}_design_test",
        name=f"{framework.value} design test",
    )
    adapter = adapter_cls(config, registry=registry, **extra)

    assert adapter.discover("anything at all")["sources"] == []

    registry.register(
        "customer_revenue",
        "Quarterly customer revenue and renewal data",
        type="table",
    )
    result = adapter.discover("customer revenue")

    assert [source["name"] for source in result["sources"]] == ["customer_revenue"]
    assert result["total_sources"] == 1
    assert result["sources"][0]["relevance"] > 0


def test_top_level_optimization_types_are_real_exports():
    for name in (
        "OptimizationStrategy",
        "StrategyType",
        "OptimizationTechnique",
        "CostMetrics",
    ):
        value = getattr(pystreammcp, name)
        assert value is not None, f"pystreammcp.{name} is not exported"
        assert name in pystreammcp.__all__


def test_ml_package_exports_only_real_symbols():
    ml = importlib.import_module("pystreammcp.ml")

    for name in (
        "PromptClassifier",
        "PromptIntent",
        "PromptComplexity",
        "PromptAnalysis",
        "PromptTag",
        "QueryFeatures",
        "QueryResult",
        "RelevanceModel",
        "ModelTrainer",
    ):
        assert hasattr(ml, name), f"pystreammcp.ml.{name} is missing"
        assert name in ml.__all__

    assert "IntentDetector" not in ml.__all__
    assert "QueryClassifier" not in ml.__all__


def test_observability_and_qa_export_real_symbols():
    observability = importlib.import_module("pystreammcp.observability")
    qa = importlib.import_module("pystreammcp.qa")

    assert hasattr(observability, "MetricsCollector")
    assert "MetricsCollector" in observability.__all__
    assert "TracingExporter" not in observability.__all__

    for name in ("QualityValidator", "SLAChecker", "AuditLogger"):
        assert hasattr(qa, name)
        assert name in qa.__all__


def test_integrations_package_exports_supported_modules():
    integrations = importlib.import_module("pystreammcp.integrations")

    for name in ("langchain", "llamaindex", "semantic_kernel"):
        assert hasattr(integrations, name)
        assert name in integrations.__all__


def test_no_shadowed_module_files():
    package_dir = Path(pystreammcp.__file__).parent
    assert not (package_dir / "ml.py").exists()
    assert not (package_dir / "optimization.py").exists()
    assert not (package_dir / "optimization" / "__init__.py.bak").exists()


def _training_record(index: int) -> dict:
    return {
        "query_id": f"prod_{index}",
        "features": {
            "query_text": f"real query {index}",
            "query_length": 40 + index,
            "intent": ["retrieve", "discover", "aggregate"][index % 3],
            "has_filters": index % 2 == 0,
            "has_joins": index % 3 == 0,
            "has_aggregates": index % 4 == 0,
            "estimated_data_size": ["small", "medium", "large"][index % 3],
            "time_sensitivity": ["realtime", "hourly", "daily"][index % 3],
        },
        "baseline_tokens": 1000 + index * 10,
        "optimized_tokens": 400 + index * 3,
        "cost_reduction_percent": 60.0 + (index % 10),
        "execution_time_ms": 100.0 + index,
        "sources_used": [f"source_{index % 4}"],
        "user_satisfaction": 0.8,
    }


def test_model_trainer_loads_real_jsonl_file(tmp_path):
    path = tmp_path / "training.jsonl"
    records = [_training_record(i) for i in range(12)]
    path.write_text("\n".join(json.dumps(record) for record in records), encoding="utf-8")

    model = RelevanceModel()
    trainer = ModelTrainer(model)
    loaded = trainer.load_production_data(str(path))

    assert loaded == len(records)
    assert [sample.query_id for sample in model.training_data] == [
        record["query_id"] for record in records
    ]
    assert model.training_data[0].features.query_text == "real query 0"


def test_model_trainer_missing_file_is_an_error(tmp_path):
    trainer = ModelTrainer(RelevanceModel())

    with pytest.raises(FileNotFoundError):
        trainer.load_production_data(str(tmp_path / "missing.jsonl"))


def test_model_train_uses_requested_holdout_split():
    model = RelevanceModel()
    for index in range(20):
        model.add_training_sample(
            MLQueryResult(
                query_id=f"q_{index}",
                features=QueryFeatures(
                    query_text=f"query {index}",
                    query_length=50,
                    intent="retrieve",
                    has_filters=index % 2 == 0,
                    has_joins=False,
                    has_aggregates=False,
                    estimated_data_size="medium",
                    time_sensitivity="daily",
                ),
                baseline_tokens=1000,
                optimized_tokens=400,
                cost_reduction_percent=65.0,
                execution_time_ms=100.0,
                sources_used=["source_1"],
            )
        )

    result = model.train(test_size=0.25)

    assert result["status"] == "trained"
    assert result["samples"] == 20
    assert result["train_samples"] == 15
    assert result["test_samples"] == 5


def test_joined_decomposition_uses_query_tables_not_placeholders():
    query = "SELECT * FROM users JOIN orders ON users.id = orders.user_id"
    plan = QueryDecomposer().decompose(query)

    assert plan.query_type == QueryType.JOINED
    texts = [sub.query_text for sub in plan.sub_queries]
    assert any("users" in text for text in texts)
    assert any("orders" in text for text in texts)
    assert all("table1" not in text and "table2" not in text for text in texts)
    assert texts[-1] == query
    assert plan.estimated_reduction == 0.0
    assert plan.estimated_total_tokens == sum(
        sub.estimated_tokens for sub in plan.sub_queries
    )


def test_simple_decomposition_does_not_claim_an_unmeasured_reduction():
    plan = QueryDecomposer().decompose("SELECT * FROM users WHERE id = 1")

    assert plan.estimated_reduction == 0.0
    assert len(plan.sub_queries) == 1
    assert plan.sub_queries[0].query_text == plan.original_query


def test_api_reports_package_version_and_real_metrics():
    from fastapi.testclient import TestClient

    from pystreammcp.api import PyStreamMCPAPI

    api = PyStreamMCPAPI()
    client = TestClient(api.app)

    assert client.get("/health").json()["version"] == pystreammcp.__version__

    assert (
        client.post(
            "/agents", json={"agent_id": "metrics_agent", "name": "Metrics Agent"}
        ).status_code
        == 200
    )
    assert (
        client.post(
            "/query",
            json={"text": "a real query to measure", "agent_id": "metrics_agent"},
        ).status_code
        == 200
    )

    metrics = client.get("/metrics").json()["metrics"]
    assert metrics["total_queries"] == 1
    assert metrics["total_tokens_saved"] > 0
    assert metrics["avg_reduction_percent"] > 0


def test_api_optimize_does_not_fabricate_applied_techniques():
    from fastapi.testclient import TestClient

    from pystreammcp.api import PyStreamMCPAPI

    api = PyStreamMCPAPI()
    client = TestClient(api.app)
    client.post("/agents", json={"agent_id": "optimize_agent", "name": "Optimize"})

    result = client.post(
        "/optimize", json={"text": "optimize this", "agent_id": "optimize_agent"}
    ).json()

    assert result["techniques"] == []
