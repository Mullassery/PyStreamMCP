import json
import sys

import httpx
import pytest

from pystreammcp.retrieval import deps
from pystreammcp.retrieval.errors import RetrievalError


def fake_specs(monkeypatch, present):
    real = __import__("importlib.util", fromlist=["find_spec"]).find_spec

    def find_spec(name, *args, **kwargs):
        if name in {"raganything", "lightrag"}:
            return object() if name in present else None
        return real(name, *args, **kwargs)

    monkeypatch.setattr("importlib.util.find_spec", find_spec)


def test_auto_prefers_consistent_installed_pair(monkeypatch):
    fake_specs(monkeypatch, {"raganything", "lightrag"})
    source = deps.resolve_rag_source("auto")
    assert source.source == "installed" and source.rag_path is None


def test_auto_uses_vendored_pair_when_either_installed_is_missing(monkeypatch):
    fake_specs(monkeypatch, {"raganything"})
    source = deps.resolve_rag_source("auto")
    assert source.source == "vendored"
    assert source.rag_path == deps.vendor_root() / "rag-anything"
    assert source.lightrag_path == deps.vendor_root() / "lightrag"


def test_strict_modes_do_not_mix(monkeypatch):
    fake_specs(monkeypatch, {"raganything", "lightrag"})
    assert deps.resolve_rag_source("vendored").source == "vendored"
    fake_specs(monkeypatch, set())
    with pytest.raises(RetrievalError) as exc:
        deps.resolve_rag_source("installed")
    assert exc.value.code == "missing_dependency"


def test_ensure_import_path_is_idempotent_and_fixed(monkeypatch):
    fake_specs(monkeypatch, set())
    before = list(sys.path)
    try:
        first = deps.ensure_rag_import_path("vendored")
        second = deps.ensure_rag_import_path("vendored")
        assert first == second
        assert sys.path.count(str(first.rag_path)) == 1
        assert sys.path.count(str(first.lightrag_path)) == 1
    finally:
        sys.path[:] = before


def test_injected_bypasses_source_resolution(monkeypatch):
    fake_specs(monkeypatch, set())
    source = deps.resolve_rag_source("vendored", injected=True)
    assert source.source == "injected" and source.rag_path is None


def test_resolution_does_not_import_heavy_packages(monkeypatch):
    fake_specs(monkeypatch, set())
    deps.resolve_rag_source("vendored")
    assert "raganything" not in sys.modules
    assert "lightrag" not in sys.modules


def test_invalid_mode_is_configuration_error():
    with pytest.raises(RetrievalError) as exc:
        deps.resolve_rag_source("network")
    assert exc.value.code == "configuration_error"


def test_tree_verification_detects_edit(tmp_path):
    root = tmp_path / "pkg"
    root.mkdir()
    (root / "a.txt").write_text("alpha", encoding="utf-8")
    digest = deps.compute_tree_sha256(root)
    (root / "a.txt").write_text("beta", encoding="utf-8")
    assert deps.compute_tree_sha256(root) != digest


def test_offline_status_reports_corruption(tmp_path, monkeypatch):
    root = tmp_path / "vendor"
    root.mkdir()
    names = ("qmd", "rag-anything", "lightrag")
    lock = {"schema": 1, "dependencies": {}}
    for name in names:
        component = root / name
        component.mkdir()
        (component / "LICENSE").write_text("MIT", encoding="utf-8")
        (component / "README.md").write_text(name, encoding="utf-8")
        lock["dependencies"][name] = {
            "repo": "https://github.com/example/repo.git",
            "tag": "v1.2.3",
            "commit": "a" * 40,
            "path": f"vendor/{name}",
            "ecosystem": "npm" if name == "qmd" else "python",
            "license": "MIT",
            "tree_sha256": deps.compute_tree_sha256(component),
        }
    (root / "deps.lock.json").write_text(json.dumps(lock), encoding="utf-8")
    monkeypatch.setattr(deps, "vendor_root", lambda: root)
    (root / "qmd" / "README.md").write_text("changed", encoding="utf-8")
    data = deps.dependency_status(offline=True)
    qmd = next(d for d in data["dependencies"] if d["name"] == "qmd")
    assert qmd["state"] == "corrupt"


def test_update_check_parses_stable_tags_and_redacts_token(monkeypatch):
    def handler(request):
        assert request.headers["Authorization"] == "Bearer secret-token"
        return httpx.Response(
            200, json=[{"name": "v9.9.9-rc1"}, {"name": "v2.9.0"}]
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    data = deps.check_upstream_updates(
        client=client, token="secret-token", components=["qmd"]
    )
    assert data["dependencies"][0]["state"] == "update_available"
    assert data["dependencies"][0]["latest"] == "v2.9.0"
    assert "secret-token" not in json.dumps(data)


def test_update_check_http_failure_is_bounded():
    client = httpx.Client(
        transport=httpx.MockTransport(lambda request: httpx.Response(403))
    )
    data = deps.check_upstream_updates(client=client, components=["qmd"])
    assert data["dependencies"][0]["state"] == "check_failed"
    assert len(data["dependencies"][0]["error"]) <= 500


@pytest.mark.parametrize("status", [404, 500])
def test_update_check_bad_response_is_bounded(status):
    client = httpx.Client(
        transport=httpx.MockTransport(lambda request: httpx.Response(status))
    )
    data = deps.check_upstream_updates(client=client, components=["qmd"])
    assert data["dependencies"][0]["state"] == "check_failed"


def test_update_check_timeout_is_bounded():
    def handler(request):
        raise httpx.ConnectTimeout("timeout")

    client = httpx.Client(transport=httpx.MockTransport(handler))
    data = deps.check_upstream_updates(client=client, components=["qmd"])
    assert data["dependencies"][0]["state"] == "check_failed"
    assert "timeout" in data["dependencies"][0]["error"].lower()


def test_offline_status_verifies_real_vendor_tree():
    data = deps.dependency_status(offline=True)
    assert {d["name"] for d in data["dependencies"]} == {
        "qmd",
        "rag-anything",
        "lightrag",
    }
    assert all(d["vendored"] == "verified" for d in data["dependencies"])
    assert all(d["latest"] is None for d in data["dependencies"])
