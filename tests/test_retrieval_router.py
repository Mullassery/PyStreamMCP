import pytest

from pystreammcp.retrieval.base import BackendCapabilities
from pystreammcp.retrieval.errors import RetrievalError
from pystreammcp.retrieval.models import BackendName, RequestedBackend
from pystreammcp.retrieval.router import route
from retrieval_helpers import FakeBackend, make_request

QMD, RAG = BackendName.QMD, BackendName.RAG_ANYTHING


def caps(name, modes, content_types, available=True, collection_scoped=False):
    return BackendCapabilities(
        backend=name,
        enabled=True,
        configured=True,
        available=available,
        modes=modes,
        content_types=content_types,
        max_limit=50,
        supports_ingestion=name is RAG,
        supports_full_content=name is RAG,
        score_kind="unavailable",
        network_egress="local",
        error=None,
    )


def test_auto_text_uses_priority():
    qmd = FakeBackend("qmd", caps(QMD, ("auto", "hybrid"), ("text",)))
    rag = FakeBackend("rag_anything", caps(RAG, ("auto", "local"), ("text",)))
    d = route(make_request(), {QMD: qmd, RAG: rag}, (QMD, RAG))
    assert d.backends == [QMD]


def test_auto_image_prefers_rag():
    qmd = FakeBackend("qmd", caps(QMD, ("auto",), ("text",)))
    rag = FakeBackend("rag_anything", caps(RAG, ("auto",), ("image",)))
    d = route(make_request(content_type="image"), {QMD: qmd, RAG: rag}, (QMD, RAG))
    assert d.backends == [RAG]


def test_auto_mode_supported_by_one():
    qmd = FakeBackend("qmd", caps(QMD, ("auto",), ("text",)))
    rag = FakeBackend("rag_anything", caps(RAG, ("global",), ("text",)))
    d = route(make_request(mode="global"), {QMD: qmd, RAG: rag}, (QMD, RAG))
    assert d.backends == [RAG]


def test_collections_require_qmd():
    qmd = FakeBackend("qmd", caps(QMD, ("auto",), ("text",), collection_scoped=True))
    d = route(make_request(collections=("docs",)), {QMD: qmd}, (QMD,))
    assert d.backends == [QMD]
    with pytest.raises(RetrievalError) as exc:
        route(make_request(collections=("docs",)), {}, (QMD,))
    assert exc.value.code == "no_available_backend"


def test_explicit_disabled_is_not_configured():
    with pytest.raises(RetrievalError) as exc:
        route(make_request(backend=RequestedBackend.QMD), {}, (QMD,))
    assert exc.value.code == "not_configured"


def test_all_includes_unavailable_for_visibility():
    qmd = FakeBackend("qmd", caps(QMD, ("auto",), ("text",), available=False))
    rag = FakeBackend("rag_anything", caps(RAG, ("auto",), ("text",)))
    d = route(
        make_request(backend=RequestedBackend.ALL), {QMD: qmd, RAG: rag}, (QMD, RAG)
    )
    assert d.backends == [QMD, RAG]


def test_no_available_backend():
    qmd = FakeBackend("qmd", caps(QMD, ("auto",), ("text",), available=False))
    with pytest.raises(RetrievalError) as exc:
        route(make_request(), {QMD: qmd}, (QMD,))
    assert exc.value.code == "no_available_backend"


def test_explicit_unavailable_is_unavailable():
    qmd = FakeBackend("qmd", caps(QMD, ("auto",), ("text",), available=False))
    with pytest.raises(RetrievalError) as exc:
        route(make_request(backend=RequestedBackend.QMD), {QMD: qmd}, (QMD,))
    assert exc.value.code == "unavailable"
