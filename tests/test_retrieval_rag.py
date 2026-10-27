import pytest

from pystreammcp.retrieval.base import BackendSearchRequest
from pystreammcp.retrieval.config import RagConfig, RagProviderConfig
from pystreammcp.retrieval.errors import RetrievalError
from pystreammcp.retrieval.rag_anything import RAGAnythingBackend
from retrieval_rag_fakes import FakeLightRAG, FakeRagEngine, install_fake_lightrag


@pytest.fixture(autouse=True)
def _fake_lightrag(monkeypatch):
    install_fake_lightrag(monkeypatch)


def provider():
    return RagProviderConfig(
        llm_model="m",
        llm_base_url="http://127.0.0.1:1234/v1",
        llm_api_key="k",
        embedding_model="e",
        embedding_base_url="http://127.0.0.1:1234/v1",
        embedding_api_key="k",
        embedding_dim=8,
        embedding_max_tokens=128,
    )


def rag_config(tmp_path, **kw):
    values = dict(
        enabled=True,
        working_dir=tmp_path / "rag",
        parsed_dir=tmp_path / "rag" / "parsed",
        allowed_roots=(tmp_path,),
        allowed_extensions=(".md",),
        max_file_mb=1,
        query_timeout_s=2.0,
        ingest_timeout_s=5.0,
        provider_name="openai_compatible",
        provider=provider(),
    )
    values.update(kw)
    return RagConfig(**values)


def req(**kw):
    values = dict(
        query="alpha",
        mode=None,
        collections=(),
        content_type=None,
        limit=5,
        include_content=False,
        max_content_chars=100,
        timeout_s=2.0,
        intent=None,
    )
    values.update(kw)
    return BackendSearchRequest(**values)


def backend(tmp_path, light, **kw):
    engine = FakeRagEngine(light)
    return (
        RAGAnythingBackend(
            rag_config(tmp_path, **kw), engine_factory=lambda: engine
        ),
        engine,
    )


def test_capabilities_does_not_load_engine(tmp_path):
    calls = []
    b = RAGAnythingBackend(
        rag_config(tmp_path),
        engine_factory=lambda: calls.append(1)
        or FakeRagEngine(FakeLightRAG()),
    )
    caps = b.capabilities()
    assert caps.available is True and caps.supports_ingestion is True
    assert caps.supports_full_content is True
    assert caps.score_kind == "unavailable"
    assert calls == [] and b._thread is None
    b.close()


def test_health_does_not_load_engine(tmp_path):
    calls = []
    b = RAGAnythingBackend(
        rag_config(tmp_path),
        engine_factory=lambda: calls.append(1)
        or FakeRagEngine(FakeLightRAG()),
    )
    assert b.health().status == "ok"
    assert calls == []
    b.close()


def test_search_maps_chunks_and_pages(tmp_path):
    light = FakeLightRAG(
        page_records={
            "c1": {"page_idx": 2, "page_idx_end": 3, "full_doc_id": "d1"}
        }
    )
    b, _ = backend(tmp_path, light)
    result = b.search(req())
    hit = result.hits[0]
    assert hit.backend.value == "rag_anything"
    assert hit.document_id == "d1"
    assert hit.title == "a"
    assert hit.source_uri == "rag://docs/a.md"
    assert hit.locator == {
        "kind": "chunk",
        "chunk_id": "c1",
        "reference_id": "r1",
        "page": 2,
    }
    assert hit.metadata["page_end"] == 3
    assert hit.score is None and hit.score_kind == "unavailable"
    assert result.diagnostics["dependency_source"] == "injected"
    assert result.diagnostics["mode"] == "mix"
    assert result.diagnostics["chunk_count"] == 1
    assert result.diagnostics["processing_info"]["total_chunks"] == 1
    b.close()


def test_auto_mode_uses_configured_query_mode(tmp_path):
    light = FakeLightRAG()
    b, _ = backend(tmp_path, light, query_mode="global")
    b.search(req(mode="auto"))
    assert light.query_calls[0][1].kwargs["mode"] == "global"
    assert light.query_calls[0][1].kwargs["top_k"] == 5
    assert light.query_calls[0][1].kwargs["chunk_top_k"] == 5
    b.close()


@pytest.mark.parametrize("mode", ["hybrid", "local", "global", "naive", "mix"])
def test_accepts_rag_modes(tmp_path, mode):
    light = FakeLightRAG()
    b, _ = backend(tmp_path, light)
    b.search(req(mode=mode))
    assert light.query_calls[0][1].kwargs["mode"] == mode
    b.close()


def test_qmd_only_mode_is_unsupported(tmp_path):
    b, _ = backend(tmp_path, FakeLightRAG())
    with pytest.raises(RetrievalError) as exc:
        b.search(req(mode="lex"))
    assert exc.value.code == "unsupported_mode"
    b.close()


def test_capabilities_reports_missing_dependency(monkeypatch, tmp_path):
    from pystreammcp.retrieval import deps

    def fail(mode, injected=False):
        raise RetrievalError("missing_dependency", "install rag-anything")

    monkeypatch.setattr(deps, "resolve_rag_source", fail)
    b = RAGAnythingBackend(rag_config(tmp_path))
    caps = b.capabilities()
    assert caps.available is False
    assert caps.error["code"] == "missing_dependency"
    b.close()


def test_injected_factory_reports_unknown_egress(tmp_path):
    b = RAGAnythingBackend(
        rag_config(tmp_path),
        engine_factory=lambda: FakeRagEngine(FakeLightRAG()),
    )
    assert b.capabilities().network_egress == "unknown"
    b.close()


def test_query_exception_is_query_failed(tmp_path):
    light = FakeLightRAG()

    async def fail(*args, **kwargs):
        raise RuntimeError("upstream boom")

    light.aquery_data = fail
    b, _ = backend(tmp_path, light)
    with pytest.raises(RetrievalError) as exc:
        b.search(req())
    assert exc.value.code == "query_failed"
    b.close()


def test_timeout_and_close_are_bounded(tmp_path):
    b, _ = backend(tmp_path, FakeLightRAG(delay=0.5), query_timeout_s=0.05)
    with pytest.raises(RetrievalError) as exc:
        b.search(req(timeout_s=0.05))
    assert exc.value.code == "timeout"
    b.close()
    assert b._thread is None


def test_missing_lightrag_and_missing_aquery_are_specific(tmp_path):
    engine = FakeRagEngine(FakeLightRAG())
    engine.lightrag = None
    b = RAGAnythingBackend(rag_config(tmp_path), engine_factory=lambda: engine)
    with pytest.raises(RetrievalError) as exc:
        b.search(req())
    assert exc.value.code == "index_not_initialized"
    b.close()

    class NoQuery:
        def __init__(self):
            self.lightrag = object()

        async def process_document_complete(self, **kw):
            pass

    b2 = RAGAnythingBackend(rag_config(tmp_path), engine_factory=NoQuery)
    with pytest.raises(RetrievalError) as exc:
        b2.search(req())
    assert exc.value.code == "upstream_unsupported_version"
    b2.close()


def test_include_content_and_empty_results(tmp_path):
    b, _ = backend(tmp_path, FakeLightRAG())
    hit = b.search(req(include_content=True, max_content_chars=5)).hits[0]
    assert hit.content == "alpha"
    b.close()
    empty = FakeLightRAG(payload={"status": "success", "data": {"chunks": []}})
    b2, _ = backend(tmp_path, empty)
    result = b2.search(req())
    assert result.hits == [] and result.diagnostics["chunk_count"] == 0
    b2.close()


def test_invalid_payloads_are_reported(tmp_path):
    bad_status = FakeLightRAG(
        payload={"status": "failure", "data": {"chunks": []}}
    )
    b, _ = backend(tmp_path, bad_status)
    with pytest.raises(RetrievalError) as exc:
        b.search(req())
    assert exc.value.code == "invalid_response"
    b.close()

    bad_chunks = FakeLightRAG(payload={"status": "success", "data": {}})
    b2, _ = backend(tmp_path, bad_chunks)
    with pytest.raises(RetrievalError) as exc:
        b2.search(req())
    assert exc.value.code == "invalid_response"
    b2.close()


def test_page_enrichment_failure_is_nonfatal(tmp_path):
    light = FakeLightRAG()

    async def fail(ids):
        raise RuntimeError("store unavailable")

    light.text_chunks.get_by_ids = fail
    b, _ = backend(tmp_path, light)
    result = b.search(req())
    assert len(result.hits) == 1
    assert result.diagnostics["page_enrichment"] is False
    assert result.hits[0].document_id is None
    b.close()


def test_close_is_idempotent_and_closed_errors(tmp_path):
    b, _ = backend(tmp_path, FakeLightRAG())
    b.close()
    b.close()
    with pytest.raises(RetrievalError) as exc:
        b.search(req())
    assert exc.value.code == "closed"


def test_installed_and_vendored_source_diagnostics(monkeypatch, tmp_path):
    import sys
    import types

    async def build(config):
        return FakeRagEngine(FakeLightRAG())

    providers = types.ModuleType("pystreammcp.retrieval.providers")
    providers.build_openai_compatible_engine = build
    monkeypatch.setitem(sys.modules, "pystreammcp.retrieval.providers", providers)

    installed = RAGAnythingBackend(
        rag_config(tmp_path, source_mode="installed")
    )
    result = installed.search(req())
    assert result.diagnostics["dependency_source"] == "installed"
    installed.close()

    vendored = RAGAnythingBackend(
        rag_config(tmp_path, source_mode="vendored")
    )
    result = vendored.search(req())
    assert result.diagnostics["dependency_source"] == "vendored"
    assert result.diagnostics["dependency_version"]
    vendored.close()


def test_strict_installed_mode_reports_missing_dependency(monkeypatch, tmp_path):
    import importlib.util

    real = importlib.util.find_spec
    monkeypatch.setattr(
        importlib.util,
        "find_spec",
        lambda name, *a, **k: None
        if name in {"raganything", "lightrag"}
        else real(name, *a, **k),
    )
    b = RAGAnythingBackend(rag_config(tmp_path, source_mode="installed"))
    caps = b.capabilities()
    assert caps.available is False
    assert caps.error["code"] == "missing_dependency"
    b.close()


def test_builtin_without_provider_is_not_configured(tmp_path):
    b = RAGAnythingBackend(rag_config(tmp_path, provider=None))
    caps = b.capabilities()
    assert caps.available is False
    assert caps.error["code"] == "not_configured"
    assert b.health().status == "unavailable"
    b.close()
