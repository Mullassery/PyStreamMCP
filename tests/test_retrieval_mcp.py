import json

import pytest

from pystreammcp.mcp_server import PyStreamMCPServer
from pystreammcp.retrieval.base import IngestionResult
from pystreammcp.retrieval.errors import RetrievalError
from pystreammcp.retrieval.models import RetrievalResponse


class FakeService:
    def __init__(self):
        self.search_calls = []
        self.ingest_calls = []
        self.capability_calls = []
        self.closed = 0

    def search(self, request):
        self.search_calls.append(request)
        return RetrievalResponse(
            status="success",
            query=request.query,
            backend_requested=request.backend.value,
            groups=[],
            diagnostics={},
        )

    def capabilities(self, include_health=True):
        self.capability_calls.append(include_health)
        return {"backends": []}

    def health(self):
        return {"backends": []}

    def ingest(self, path, force_multimodal=False):
        self.ingest_calls.append((path, force_multimodal))
        return IngestionResult(
            document_id="d1",
            display_path="docs/a.md",
            status="processed",
            skipped=False,
            elapsed_ms=1,
            content_types=("text",),
        )

    def close(self):
        self.closed += 1


def test_tools_advertised_and_search_roundtrip():
    s = FakeService()
    server = PyStreamMCPServer(retrieval_service=s)
    names = {t["name"] for t in server.get_tools()}
    assert {
        "pystreammcp_retrieval_search",
        "pystreammcp_retrieval_capabilities",
        "pystreammcp_rag_ingest",
    } <= names
    out = server.call_tool("pystreammcp_retrieval_search", {"query": "alpha"})
    assert out["status"] == "success" and out["groups"] == []
    assert s.search_calls[0].limit == 5
    assert s.search_calls[0].max_content_chars == 2000
    assert s.search_calls[0].backend.value == "auto"


def test_error_shape_and_auth(monkeypatch):
    class Failing(FakeService):
        def search(self, request):
            raise RetrievalError("unsupported_mode", "no", backend="qmd")

    server = PyStreamMCPServer(retrieval_service=Failing())
    out = server.call_tool(
        "pystreammcp_retrieval_search", {"query": "x", "mode": "global"}
    )
    assert out == {
        "status": "error",
        "error_type": "RetrievalError",
        "code": "unsupported_mode",
        "message": "no",
        "backend": "qmd",
        "retryable": False,
    }
    monkeypatch.setenv("PYSTREAMMCP_API_KEY", "secret")
    assert (
        server.call_tool("pystreammcp_retrieval_search", {"query": "x"})[
            "error_type"
        ]
        == "AuthenticationError"
    )


def test_ingest_and_capabilities_and_close():
    s = FakeService()
    server = PyStreamMCPServer(retrieval_service=s)
    out = server.call_tool(
        "pystreammcp_rag_ingest",
        {"path": "docs/a.md", "force_multimodal": True},
    )
    assert out["status"] == "processed"
    assert s.ingest_calls == [("docs/a.md", True)]
    assert json.dumps(server.call_tool("pystreammcp_retrieval_capabilities", {}))
    assert s.capability_calls == [True]
    server.close()
    server.close()
    assert s.closed == 1


@pytest.mark.parametrize(
    "args",
    [
        {"query": ""},
        {"query": "x", "limit": 0},
        {"query": "x", "limit": 51},
        {"query": "x", "max_content_chars": -1},
        {"query": "x", "time_budget_ms": 0},
        {"query": "x", "collections": [f"c{i}" for i in range(33)]},
        {"query": "x", "backend": "nope"},
        {"query": "x", "content_type": "nope"},
    ],
)
def test_search_validation_bounds(args):
    s = FakeService()
    server = PyStreamMCPServer(retrieval_service=s)
    out = server.call_tool("pystreammcp_retrieval_search", args)
    assert out["status"] == "error"
    assert out["validation_errors"]
    assert s.search_calls == []
    server.close()


def test_capabilities_without_health_and_ingest_errors():
    class Failing(FakeService):
        def ingest(self, path, force_multimodal=False):
            raise RetrievalError("configuration_error", "no roots")

    server = PyStreamMCPServer(retrieval_service=Failing())
    assert (
        server.call_tool(
            "pystreammcp_retrieval_capabilities", {"include_health": False}
        )
        == {"backends": []}
    )
    out = server.call_tool("pystreammcp_rag_ingest", {"path": "a.md"})
    assert out["error_type"] == "RetrievalError"
    assert out["code"] == "configuration_error"
    server.close()


def test_get_info_retrieval_capability_is_config_gated(monkeypatch):
    for name in ("PYSTREAMMCP_QMD_ENABLED", "PYSTREAMMCP_RAG_ENABLED"):
        monkeypatch.delenv(name, raising=False)
    server = PyStreamMCPServer()
    info = server.process_message({"type": "get_info"})
    assert "retrieval" not in info["capabilities"]
    monkeypatch.setenv("PYSTREAMMCP_QMD_ENABLED", "true")
    assert "retrieval" in server.process_message({"type": "get_info"})[
        "capabilities"
    ]

    injected = PyStreamMCPServer(retrieval_service=FakeService())
    assert "retrieval" in injected.process_message({"type": "get_info"})[
        "capabilities"
    ]
    injected.close()


def test_lazy_service_construction(monkeypatch):
    from pystreammcp.retrieval.service import RetrievalService

    created = []

    def fake_from_env(cls, env=None):
        service = FakeService()
        created.append(service)
        return service

    monkeypatch.setattr(
        RetrievalService, "from_env", classmethod(fake_from_env)
    )
    server = PyStreamMCPServer()
    assert created == []
    server.process_message({"type": "get_info"})
    assert created == []
    out = server.call_tool("pystreammcp_retrieval_search", {"query": "x"})
    assert out["status"] == "success"
    assert len(created) == 1
    server.close()
    assert created[0].closed == 1
