from pystreammcp.retrieval.base import BackendCapabilities
from pystreammcp.retrieval.errors import RetrievalError
from pystreammcp.retrieval.models import (
    BackendGroup,
    BackendName,
    RequestedBackend,
    RetrievalHit,
    RetrievalRequest,
    RetrievalResponse,
)


def test_request_defaults_match_spec():
    request = RetrievalRequest(query="alpha")
    assert request.backend is RequestedBackend.AUTO
    assert request.mode is None
    assert request.content_type is None
    assert request.limit == 5
    assert request.max_content_chars == 2000
    assert request.time_budget_ms == 30000


def test_response_keeps_engines_separate_and_serializes_enums():
    hit = RetrievalHit(
        backend=BackendName.QMD,
        rank=1,
        document_id="d1",
        title="Doc",
        source_uri="qmd://docs/a.md",
        locator={"kind": "line", "line": 3},
        excerpt="alpha",
        content=None,
        score=1.5,
        score_kind="qmd_query_relevance",
        metadata={"docid": "d1"},
    )
    response = RetrievalResponse(
        status="success",
        query="alpha",
        backend_requested="auto",
        groups=[
            BackendGroup(
                backend=BackendName.QMD,
                status="ok",
                hits=[hit],
                error=None,
                elapsed_ms=4,
                truncated=False,
            )
        ],
        diagnostics={"selected": ["qmd"]},
    )
    data = response.to_dict()
    assert data["status"] == "success"
    assert data["groups"][0]["backend"] == "qmd"
    assert data["groups"][0]["hits"][0]["locator"]["line"] == 3
    assert "content" not in data["groups"][0]["hits"][0]


def test_error_to_dict_is_bounded():
    data = RetrievalError(
        "http_error",
        "x" * 900,
        backend=BackendName.QMD,
        retryable=False,
        details={"status_code": 400},
    ).to_dict()
    assert data["code"] == "http_error"
    assert len(data["message"]) <= 500
    assert data["backend"] == "qmd"
    assert data["details"] == {"status_code": 400}


def test_capabilities_shape():
    caps = BackendCapabilities(
        backend=BackendName.QMD,
        enabled=True,
        configured=True,
        available=True,
        modes=("auto",),
        content_types=("text",),
        max_limit=50,
        supports_ingestion=False,
        supports_full_content=False,
        score_kind="qmd_query_relevance",
        network_egress="local",
        error=None,
    )
    assert caps.to_dict()["network_egress"] == "local"
    assert caps.to_dict()["supports_full_content"] is False
