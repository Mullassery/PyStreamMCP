import asyncio
import hashlib

import pytest

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


def backend(tmp_path, light, **kw):
    engine = FakeRagEngine(light)
    return (
        RAGAnythingBackend(
            rag_config(tmp_path, **kw), engine_factory=lambda: engine
        ),
        engine,
    )


def write_doc(root, name="doc.md", text="# alpha\n"):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_ingest_hash_status_and_force(tmp_path):
    doc = write_doc(tmp_path)
    b, engine = backend(tmp_path, FakeLightRAG())
    first = b.ingest(str(doc))
    expected = (
        "pystreammcp-" + hashlib.sha256(doc.read_bytes()).hexdigest()[:32]
    )
    assert first.document_id == expected
    assert first.display_path == f"{tmp_path.name}/doc.md"
    assert first.status == "processed" and first.skipped is False
    assert engine.calls[0]["doc_id"] == expected
    assert engine.calls[0]["force_multimodal_reprocess"] is False
    second = b.ingest(str(doc))
    assert second.status == "processed" and second.skipped is True
    assert len(engine.calls) == 1
    third = b.ingest(str(doc), force_multimodal=True)
    assert third.skipped is False
    assert len(engine.calls) == 2
    assert engine.calls[1]["force_multimodal_reprocess"] is True
    b.close()


def test_policy_failures_happen_before_engine(tmp_path):
    b, engine = backend(tmp_path, FakeLightRAG())
    outside = tmp_path.parent / "outside.md"
    outside.write_text("x")
    with pytest.raises(RetrievalError) as exc:
        b.ingest(str(outside))
    assert exc.value.code == "path_outside_allowed_roots"
    link = tmp_path / "link.md"
    link.symlink_to(write_doc(tmp_path, "real.md"))
    with pytest.raises(RetrievalError) as exc:
        b.ingest(str(link))
    assert exc.value.code == "symlink_not_allowed"
    html = tmp_path / "a.html"
    html.write_text("<p>x</p>")
    with pytest.raises(RetrievalError) as exc:
        b.ingest(str(html))
    assert exc.value.code == "unsupported_extension"
    assert engine.calls == []
    b.close()


def test_markdown_image_and_oversize_rejected(tmp_path):
    root = tmp_path / "docs"
    root.mkdir()
    (tmp_path / "outside.png").write_bytes(b"png")
    doc = root / "a.md"
    doc.write_text("![x](../outside.png)\n")
    b, engine = backend(
        tmp_path,
        FakeLightRAG(),
        allowed_roots=(root,),
        allowed_extensions=(".md", ".png"),
    )
    with pytest.raises(RetrievalError) as exc:
        b.ingest(str(doc))
    assert exc.value.code == "path_outside_allowed_roots"
    assert engine.calls == []
    b.close()

    big = root / "big.md"
    big.write_bytes(b"x" * 2048)
    b2, engine2 = backend(
        tmp_path,
        FakeLightRAG(),
        allowed_roots=(root,),
        allowed_extensions=(".md",),
        max_file_mb=0,
    )
    with pytest.raises(RetrievalError) as exc:
        b2.ingest(str(big))
    assert exc.value.code == "file_too_large"
    assert engine2.calls == []
    b2.close()


def test_missing_roots_is_configuration_error(tmp_path):
    b, engine = backend(tmp_path, FakeLightRAG(), allowed_roots=())
    with pytest.raises(RetrievalError) as exc:
        b.ingest(str(write_doc(tmp_path)))
    assert exc.value.code == "configuration_error"
    assert engine.calls == []
    b.close()


def test_content_types_and_output_params(tmp_path):
    doc = write_doc(tmp_path)
    b, engine = backend(tmp_path, FakeLightRAG())
    result = b.ingest(str(doc))
    assert result.content_types == ("text", "table", "equation")
    call = engine.calls[0]
    assert call["file_name"] == f"{tmp_path.name}/doc.md"
    assert call["output_dir"] == str(tmp_path / "rag" / "parsed")
    assert call["parse_method"] == "auto"
    assert (tmp_path / "rag").is_dir()
    assert (tmp_path / "rag" / "parsed").is_dir()
    b.close()


def test_disabled_ingest_does_not_load_engine(tmp_path):
    engine_holder = []

    def factory():
        engine_holder.append(1)
        return FakeRagEngine(FakeLightRAG())

    b = RAGAnythingBackend(
        rag_config(tmp_path, enabled=False), engine_factory=factory
    )
    with pytest.raises(RetrievalError) as exc:
        b.ingest(str(write_doc(tmp_path)))
    assert exc.value.code == "not_configured"
    assert engine_holder == []
    b.close()


def test_failed_status_is_reported(tmp_path):
    class FailingEngine(FakeRagEngine):
        async def process_document_complete(self, **kwargs):
            self.calls.append(kwargs)
            self.lightrag.doc_status.records[kwargs["doc_id"]] = {
                "status": "failed"
            }

    engine = FailingEngine(FakeLightRAG())
    b = RAGAnythingBackend(
        rag_config(tmp_path), engine_factory=lambda: engine
    )
    result = b.ingest(str(write_doc(tmp_path)))
    assert result.status == "failed" and result.skipped is False
    b.close()


def test_ingest_timeout_is_bounded(tmp_path):
    class SlowEngine(FakeRagEngine):
        async def process_document_complete(self, **kwargs):
            self.calls.append(kwargs)
            await asyncio.sleep(0.5)

    engine = SlowEngine(FakeLightRAG())
    b = RAGAnythingBackend(
        rag_config(tmp_path, ingest_timeout_s=0.05),
        engine_factory=lambda: engine,
    )
    with pytest.raises(RetrievalError) as exc:
        b.ingest(str(write_doc(tmp_path)))
    assert exc.value.code == "timeout"
    assert "may still be running" in exc.value.message
    b.close()
    assert b._thread is None
