import json

import httpx
import pytest

from pystreammcp.retrieval.base import BackendSearchRequest
from pystreammcp.retrieval.config import QmdConfig
from pystreammcp.retrieval.errors import RetrievalError
from pystreammcp.retrieval.qmd import QmdBackend


def cfg(**kw):
    values = dict(
        enabled=True,
        url="http://127.0.0.1:8181",
        collections=("docs",),
        timeout_s=2.0,
        health_timeout_s=0.2,
    )
    values.update(kw)
    return QmdConfig(**values)


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
        intent="find",
    )
    values.update(kw)
    return BackendSearchRequest(**values)


def test_auto_payload_and_mapping():
    seen = {}

    def handler(request):
        seen["url"] = str(request.url)
        seen["json"] = json.loads(request.content)
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "docid": "d1",
                        "file": "a.md",
                        "title": "A",
                        "score": 1.5,
                        "context": "ctx",
                        "line": 3,
                        "snippet": "alpha beta",
                        "metadata": {"tag": "x"},
                    }
                ]
            },
        )

    b = QmdBackend(cfg(), transport=httpx.MockTransport(handler))
    result = b.search(req(include_content=True))
    assert seen["url"].endswith("/query")
    assert seen["json"] == {
        "searches": [
            {"type": "lex", "query": "alpha"},
            {"type": "vec", "query": "alpha"},
        ],
        "collections": ["docs"],
        "limit": 5,
        "intent": "find",
        "rerank": True,
    }
    hit = result.hits[0]
    assert hit.document_id == "d1"
    assert hit.source_uri == "qmd://docs/a.md"
    assert hit.locator == {"kind": "line", "line": 3}
    assert hit.content == "alpha beta"
    assert hit.score_kind == "qmd_query_relevance"
    assert hit.metadata["docid"] == "d1"
    assert hit.metadata["context"] == "ctx"
    assert hit.metadata["line"] == 3
    assert hit.metadata["tag"] == "x"
    b.close()


def test_mode_matrix():
    def payload_for(mode):
        seen = {}

        def handler(request):
            seen.update(json.loads(request.content))
            return httpx.Response(200, json={"results": []})

        b = QmdBackend(cfg(), transport=httpx.MockTransport(handler))
        b.search(req(mode=mode))
        b.close()
        return seen

    assert payload_for("hybrid")["rerank"] is True
    assert payload_for("lex")["searches"] == [{"type": "lex", "query": "alpha"}]
    assert payload_for("vector")["searches"] == [
        {"type": "vec", "query": "alpha"}
    ]
    assert payload_for("hyde")["searches"] == [
        {"type": "hyde", "query": "alpha"}
    ]


def test_collection_subset_enforced():
    b = QmdBackend(
        cfg(),
        transport=httpx.MockTransport(
            lambda r: httpx.Response(200, json={"results": []})
        ),
    )
    b.search(req(collections=("docs",)))
    with pytest.raises(RetrievalError) as exc:
        b.search(req(collections=("other",)))
    assert exc.value.code == "collection_not_allowed"
    b.close()


def test_error_mapping_and_health():
    b = QmdBackend(
        cfg(), transport=httpx.MockTransport(lambda r: httpx.Response(503, text="down"))
    )
    with pytest.raises(RetrievalError) as exc:
        b.search(req())
    assert exc.value.code == "unavailable" and exc.value.retryable is True
    b.close()
    b2 = QmdBackend(
        cfg(),
        transport=httpx.MockTransport(
            lambda r: (_ for _ in ()).throw(httpx.TimeoutException("slow"))
        ),
    )
    assert b2.health().status == "unavailable"
    b2.close()


def test_capabilities_egress():
    local = QmdBackend(
        cfg(),
        transport=httpx.MockTransport(lambda r: httpx.Response(200, json={})),
    )
    remote = QmdBackend(
        cfg(url="https://qmd.example.com", allow_remote=True),
        transport=httpx.MockTransport(lambda r: httpx.Response(200, json={})),
    )
    assert local.capabilities().network_egress == "local"
    assert remote.capabilities().network_egress == "remote"
    assert local.capabilities().supports_full_content is False
    local.close()
    remote.close()


def test_http_400_404_and_invalid_payload():
    for status, code in ((400, "http_error"), (404, "unavailable")):
        b = QmdBackend(
            cfg(),
            transport=httpx.MockTransport(
                lambda r, status=status: httpx.Response(status, text="nope")
            ),
        )
        with pytest.raises(RetrievalError) as exc:
            b.search(req())
        assert exc.value.code == code
        b.close()

    invalid = QmdBackend(
        cfg(),
        transport=httpx.MockTransport(
            lambda r: httpx.Response(200, text="not-json")
        ),
    )
    with pytest.raises(RetrievalError) as exc:
        invalid.search(req())
    assert exc.value.code == "invalid_response"
    invalid.close()


def test_truncation_content_and_metadata_bounds():
    def handler(request):
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "docid": f"d{i}",
                        "file": f"a{i}.md",
                        "line": i,
                        "snippet": "x" * 100,
                        "metadata": {
                            "nested": {"not": "allowed"},
                            "tags": ["a", 1],
                            "long": "y" * 1000,
                            "api_key": "must-not-leak",
                        },
                    }
                    for i in range(1, 8)
                ]
            },
        )

    b = QmdBackend(cfg(), transport=httpx.MockTransport(handler))
    result = b.search(req(limit=5, include_content=True, max_content_chars=10))
    assert result.truncated is True
    assert len(result.hits) == 5
    hit = result.hits[0]
    assert hit.content == "x" * 10
    assert "nested" not in hit.metadata
    assert "api_key" not in hit.metadata
    assert hit.metadata["tags"] == ["a", 1]
    assert len(hit.metadata["long"]) <= 200
    b.close()


def test_health_ok_and_invalid_requests():
    calls = []

    def handler(request):
        calls.append(str(request.url))
        return httpx.Response(200, json={"status": "ok"})

    b = QmdBackend(cfg(), transport=httpx.MockTransport(handler))
    health = b.health()
    assert health.status == "ok" and health.available is True
    assert calls == ["http://127.0.0.1:8181/health"]

    with pytest.raises(RetrievalError) as exc:
        b.search(req(mode="global"))
    assert exc.value.code == "unsupported_mode"
    with pytest.raises(RetrievalError) as exc:
        b.search(req(content_type="image"))
    assert exc.value.code == "unsupported_content_type"
    b.close()
