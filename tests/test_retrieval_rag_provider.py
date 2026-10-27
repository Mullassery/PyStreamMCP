import asyncio
import sys
import types

import pytest

from pystreammcp.retrieval.config import RagConfig, RagProviderConfig
from pystreammcp.retrieval.errors import RetrievalError
from pystreammcp.retrieval.providers import (
    build_openai_compatible_engine,
    validate_provider_config,
)


def provider(**kw):
    values = dict(
        llm_model="m",
        llm_base_url="http://127.0.0.1:1234/v1",
        llm_api_key="sk-secret",
        embedding_model="e",
        embedding_base_url="http://127.0.0.1:1234/v1",
        embedding_api_key="sk-secret",
        embedding_dim=8,
        embedding_max_tokens=128,
    )
    values.update(kw)
    return RagProviderConfig(**values)


def cfg(tmp_path, **kw):
    values = dict(
        enabled=True,
        working_dir=tmp_path,
        parsed_dir=tmp_path / "parsed",
        allowed_roots=(tmp_path,),
        provider_name="openai_compatible",
        provider=provider(),
    )
    values.update(kw)
    return RagConfig(**values)


def test_validation_names_missing_field(tmp_path):
    assert validate_provider_config(cfg(tmp_path)) is None
    assert "LLM_MODEL" in validate_provider_config(
        cfg(tmp_path, provider=provider(llm_model=""))
    )
    assert "EMBED_DIM" in validate_provider_config(
        cfg(tmp_path, provider=provider(embedding_dim=None))
    )


def test_missing_dependency(monkeypatch, tmp_path):
    import importlib.util

    real = importlib.util.find_spec
    monkeypatch.setattr(
        importlib.util,
        "find_spec",
        lambda name, *a, **k: None
        if name in {"raganything", "lightrag"}
        else real(name, *a, **k),
    )
    with pytest.raises(RetrievalError) as exc:
        asyncio.run(build_openai_compatible_engine(cfg(tmp_path)))
    assert exc.value.code == "missing_dependency"
    assert "rag-anything" in exc.value.message


def test_factory_wires_upstream(monkeypatch, tmp_path):
    calls = {}

    class LightRAG:
        def __init__(self, **kw):
            calls["lightrag"] = kw

        async def initialize_storages(self):
            calls["storages"] = True

        async def initialize_pipeline_status(self):
            calls["pipeline"] = True

    class RAGAnything:
        def __init__(self, **kw):
            calls["rag"] = kw

    class Config:
        def __init__(self, **kw):
            calls["config"] = kw

    async def complete(*a, **k):
        return "ok"

    async def embed(*a, **k):
        return [[0.0]]

    class EmbeddingFunc:
        def __init__(self, **kw):
            calls["embedding"] = kw

    light = types.ModuleType("lightrag")
    light.LightRAG = LightRAG
    light.__path__ = []
    llm = types.ModuleType("lightrag.llm")
    llm.__path__ = []
    oa = types.ModuleType("lightrag.llm.openai")
    oa.openai_complete_if_cache = complete
    oa.openai_embed = types.SimpleNamespace(func=embed)
    utils = types.ModuleType("lightrag.utils")
    utils.EmbeddingFunc = EmbeddingFunc
    rag = types.ModuleType("raganything")
    rag.RAGAnything = RAGAnything
    rag.RAGAnythingConfig = Config
    for name, mod in [
        ("lightrag", light),
        ("lightrag.llm", llm),
        ("lightrag.llm.openai", oa),
        ("lightrag.utils", utils),
        ("raganything", rag),
    ]:
        monkeypatch.setitem(sys.modules, name, mod)
    monkeypatch.setattr("importlib.util.find_spec", lambda name, *a, **k: object())

    engine = asyncio.run(build_openai_compatible_engine(cfg(tmp_path)))
    assert isinstance(engine, RAGAnything)
    assert calls["storages"] is True and calls["pipeline"] is True
    assert calls["rag"]["lightrag"] is not None
    assert calls["embedding"]["embedding_dim"] == 8
    assert calls["embedding"]["max_token_size"] == 128
    assert calls["config"]["parser"] == "mineru"
    assert calls["config"]["parse_method"] == "auto"
    assert "sk-secret" not in repr(calls)
    assert "vision_model_func" not in calls["rag"]


def test_vision_model_is_wired_when_configured(monkeypatch, tmp_path):
    calls = {}

    class LightRAG:
        def __init__(self, **kw):
            calls["lightrag"] = kw

        async def initialize_storages(self):
            pass

        async def initialize_pipeline_status(self):
            pass

    class RAGAnything:
        def __init__(self, **kw):
            calls["rag"] = kw

    class Config:
        def __init__(self, **kw):
            pass

    async def complete(*a, **k):
        return "ok"

    async def embed(*a, **k):
        return [[0.0]]

    class EmbeddingFunc:
        def __init__(self, **kw):
            pass

    light = types.ModuleType("lightrag")
    light.LightRAG = LightRAG
    light.__path__ = []
    llm = types.ModuleType("lightrag.llm")
    llm.__path__ = []
    oa = types.ModuleType("lightrag.llm.openai")
    oa.openai_complete_if_cache = complete
    oa.openai_embed = types.SimpleNamespace(func=embed)
    utils = types.ModuleType("lightrag.utils")
    utils.EmbeddingFunc = EmbeddingFunc
    rag = types.ModuleType("raganything")
    rag.RAGAnything = RAGAnything
    rag.RAGAnythingConfig = Config
    for name, mod in [
        ("lightrag", light),
        ("lightrag.llm", llm),
        ("lightrag.llm.openai", oa),
        ("lightrag.utils", utils),
        ("raganything", rag),
    ]:
        monkeypatch.setitem(sys.modules, name, mod)
    monkeypatch.setattr("importlib.util.find_spec", lambda name, *a, **k: object())

    config = cfg(
        tmp_path,
        provider=provider(
            vision_model="v", vision_base_url="http://127.0.0.1:1234/v1",
            vision_api_key="sk-vision",
        ),
    )
    asyncio.run(build_openai_compatible_engine(config))
    assert callable(calls["rag"]["vision_model_func"])


def test_missing_provider_is_configuration_error(tmp_path):
    with pytest.raises(RetrievalError) as exc:
        asyncio.run(
            build_openai_compatible_engine(cfg(tmp_path, provider=None))
        )
    assert exc.value.code == "configuration_error"
