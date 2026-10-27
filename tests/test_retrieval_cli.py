import json

from click.testing import CliRunner

from pystreammcp.cli import cli
from pystreammcp.retrieval.base import IngestionResult
from pystreammcp.retrieval.errors import RetrievalError
from pystreammcp.retrieval.models import BackendGroup, RetrievalResponse


class FakeService:
    def __init__(self):
        self.search_calls = []
        self.ingest_calls = []
        self.closed = 0

    def search(self, request):
        self.search_calls.append(request)
        return RetrievalResponse(
            status="success",
            query=request.query,
            backend_requested=request.backend.value,
            groups=[
                BackendGroup(
                    backend="qmd",
                    status="ok",
                    hits=[],
                    error=None,
                    elapsed_ms=1,
                    truncated=False,
                )
            ],
            diagnostics={},
        )

    def capabilities(self, include_health=True):
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


def test_group_mounted_and_search_json(monkeypatch):
    fake = FakeService()
    monkeypatch.setattr("pystreammcp.retrieval.cli._build_service", lambda: fake)
    assert "retrieval" in CliRunner().invoke(cli, ["--help"]).output
    out = CliRunner().invoke(
        cli, ["retrieval", "search", "alpha", "--json", "--limit", "3"]
    )
    assert out.exit_code == 0
    assert json.loads(out.output)["status"] == "success"
    assert fake.search_calls[0].limit == 3
    assert fake.closed == 1


def test_search_options_map_to_request(monkeypatch):
    fake = FakeService()
    monkeypatch.setattr("pystreammcp.retrieval.cli._build_service", lambda: fake)
    out = CliRunner().invoke(
        cli,
        [
            "retrieval",
            "search",
            "alpha",
            "--backend",
            "qmd",
            "--mode",
            "fast",
            "--collection",
            "notes",
            "--collection",
            "docs",
            "--content-type",
            "text",
            "--limit",
            "2",
            "--include-content",
            "--max-content-chars",
            "10",
            "--time-budget-ms",
            "500",
            "--intent",
            "find",
            "--json",
        ],
    )
    assert out.exit_code == 0
    request = fake.search_calls[0]
    assert request.backend.value == "qmd"
    assert request.mode == "fast"
    assert request.collections == ("notes", "docs")
    assert request.content_type == "text"
    assert request.limit == 2
    assert request.include_content is True
    assert request.max_content_chars == 10
    assert request.time_budget_ms == 500
    assert request.intent == "find"


def test_human_partial_and_error(monkeypatch):
    class Partial(FakeService):
        def search(self, request):
            return RetrievalResponse(
                status="partial",
                query=request.query,
                backend_requested=request.backend.value,
                groups=[],
                diagnostics={},
            )

    monkeypatch.setattr("pystreammcp.retrieval.cli._build_service", Partial)
    out = CliRunner().invoke(cli, ["retrieval", "search", "x"])
    assert out.exit_code == 1
    assert "0 hit(s)" in out.output

    class Failing(FakeService):
        def search(self, request):
            raise RetrievalError("unsupported_mode", "no", backend="qmd")

    monkeypatch.setattr("pystreammcp.retrieval.cli._build_service", Failing)
    out = CliRunner().invoke(cli, ["retrieval", "search", "x"])
    assert out.exit_code == 1 and "unsupported_mode" in out.output


def test_capabilities_health_ingest(monkeypatch):
    fake = FakeService()
    monkeypatch.setattr("pystreammcp.retrieval.cli._build_service", lambda: fake)
    assert (
        json.loads(
            CliRunner()
            .invoke(cli, ["retrieval", "capabilities", "--json"])
            .output
        )
        == {"backends": []}
    )
    out = CliRunner().invoke(
        cli, ["retrieval", "capabilities", "--no-health", "--json"]
    )
    assert json.loads(out.output) == {"backends": []}
    assert (
        json.loads(
            CliRunner().invoke(cli, ["retrieval", "health", "--json"]).output
        )
        == {"backends": []}
    )
    out = CliRunner().invoke(
        cli,
        [
            "retrieval",
            "ingest",
            "docs/a.md",
            "--force-multimodal",
            "--json",
        ],
    )
    assert json.loads(out.output)["status"] == "processed"
    assert fake.ingest_calls == [("docs/a.md", True)]
    assert fake.closed == 4


def test_deps_status_exit_codes(monkeypatch):
    from pystreammcp.retrieval import cli as retrieval_cli

    def status(offline=False):
        return {
            "schema": 1,
            "offline": offline,
            "dependencies": [
                {
                    "name": "qmd",
                    "pinned": "v2.8.3",
                    "latest": "v2.8.3",
                    "state": "current",
                    "vendored": "verified",
                    "error": None,
                },
            ],
        }

    monkeypatch.setattr(retrieval_cli.deps, "dependency_status", status)
    monkeypatch.setattr(retrieval_cli.deps, "upstream_exit_code", lambda data: 0)
    out = CliRunner().invoke(
        cli, ["retrieval", "deps", "status", "--offline", "--json"]
    )
    assert out.exit_code == 0
    assert json.loads(out.output)["offline"] is True
    monkeypatch.setattr(retrieval_cli.deps, "upstream_exit_code", lambda data: 1)
    out = CliRunner().invoke(cli, ["retrieval", "deps", "status", "--offline"])
    assert out.exit_code == 1
    assert "qmd" in out.output


def test_deps_status_never_builds_service(monkeypatch):
    from pystreammcp.retrieval import cli as retrieval_cli

    def fail():
        raise AssertionError("service must not be built")

    monkeypatch.setattr(retrieval_cli, "_build_service", fail)
    monkeypatch.setattr(
        retrieval_cli.deps,
        "dependency_status",
        lambda offline=False: {"schema": 1, "dependencies": []},
    )
    monkeypatch.setattr(retrieval_cli.deps, "upstream_exit_code", lambda data: 0)
    out = CliRunner().invoke(cli, ["retrieval", "deps", "status", "--offline"])
    assert out.exit_code == 0
