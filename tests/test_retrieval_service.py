import pytest

from pystreammcp.retrieval.errors import RetrievalError
from pystreammcp.retrieval.models import BackendName, RetrievalHit
from pystreammcp.retrieval.service import RetrievalService, UnavailableBackend
from retrieval_helpers import FakeBackend, make_request

QMD, RAG = BackendName.QMD, BackendName.RAG_ANYTHING


def hit(backend=QMD):
    return RetrievalHit(
        backend=backend,
        rank=1,
        document_id="d1",
        title="T",
        source_uri=f"{backend.value}://d1",
        locator={"kind": "line", "line": 1},
        excerpt="alpha",
        content=None,
        score=1.0,
        score_kind="qmd_query_relevance",
        metadata={},
    )


def test_success_grouping():
    service = RetrievalService([FakeBackend("qmd", hits=[hit()])])
    r = service.search(make_request())
    assert r.status == "success"
    assert r.groups[0].backend is QMD
    assert r.groups[0].hits[0].excerpt == "alpha"
    service.close()


def test_partial_when_one_group_fails():
    qmd = FakeBackend("qmd", hits=[hit()])
    rag = FakeBackend(
        "rag_anything", error=RetrievalError("query_failed", "boom", backend=RAG)
    )
    service = RetrievalService([qmd, rag])
    r = service.search(make_request(backend="all"))
    assert r.status == "partial"
    assert [g.status for g in r.groups] == ["ok", "error"]
    service.close()


def test_no_fallback_after_qmd_failure():
    qmd = FakeBackend(
        "qmd",
        error=RetrievalError("unavailable", "down", backend=QMD, retryable=True),
    )
    rag = FakeBackend("rag_anything", hits=[hit(RAG)])
    service = RetrievalService([qmd, rag])
    r = service.search(make_request())
    assert r.status == "error"
    assert [g.backend for g in r.groups] == [QMD]
    assert r.groups[0].status == "unavailable"
    service.close()


def test_timeout_group():
    service = RetrievalService([FakeBackend("qmd", delay=0.25, hits=[hit()])])
    r = service.search(make_request(time_budget_ms=100))
    assert r.groups[0].status == "timeout"
    assert r.status == "error"
    service.close()


def test_invalid_request_does_not_dispatch():
    b = FakeBackend("qmd")
    service = RetrievalService([b])
    for kwargs in (
        {"query": ""},
        {"limit": 0},
        {"limit": 51},
        {"max_content_chars": -1},
        {"time_budget_ms": 0},
        {"collections": tuple(f"c{i}" for i in range(33))},
    ):
        with pytest.raises(RetrievalError) as exc:
            service.search(make_request(**kwargs))
        assert exc.value.code == "invalid_request"
    assert b.requests == []
    service.close()


def test_empty_registry_is_no_available_backend():
    service = RetrievalService([])
    with pytest.raises(RetrievalError) as exc:
        service.search(make_request())
    assert exc.value.code == "no_available_backend"
    service.close()


def test_broken_backend_does_not_crash_and_other_works():
    bad = UnavailableBackend(
        QMD, RetrievalError("configuration_error", "bad config")
    )
    good = FakeBackend("rag_anything", hits=[hit(RAG)])
    service = RetrievalService([bad, good])
    caps = service.capabilities(include_health=False)
    assert caps["backends"][0]["available"] is False
    assert service.search(make_request()).groups[0].backend is RAG
    service.close()


def test_ingest_requires_rag_and_delegates():
    rag = FakeBackend("rag_anything")
    service = RetrievalService([rag])
    result = service.ingest("/tmp/a.md", force_multimodal=True)
    assert result.status == "processed"
    assert rag.ingest_calls == [("/tmp/a.md", True)]
    service.close()
    with pytest.raises(RetrievalError) as exc:
        RetrievalService([]).ingest("/tmp/a.md")
    assert exc.value.code == "not_configured"


def test_close_is_idempotent():
    b = FakeBackend("qmd")
    service = RetrievalService([b])
    service.close()
    service.close()
    assert b.closed is True
