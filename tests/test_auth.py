"""Loopback/API-key enforcement tests for Flask and FastAPI apps."""

from __future__ import annotations

import pytest
from pystreammcp.auth import check_request


def test_loopback_allowed_without_key(monkeypatch):
    monkeypatch.delenv("PYSTREAMMCP_API_KEY", raising=False)
    assert check_request("127.0.0.1", None, None)[0] is True


def test_non_loopback_rejected_without_key(monkeypatch):
    monkeypatch.delenv("PYSTREAMMCP_API_KEY", raising=False)
    ok, message = check_request("10.0.0.5", None, None)
    assert ok is False
    assert "PYSTREAMMCP_API_KEY" in message


def test_api_key_required(monkeypatch):
    monkeypatch.setenv("PYSTREAMMCP_API_KEY", "secret")
    assert check_request("10.0.0.5", "wrong", None)[0] is False
    assert check_request("10.0.0.5", "secret", None)[0] is True
    assert check_request("10.0.0.5", None, "Bearer secret")[0] is True


def test_flask_app_enforces_key(monkeypatch):
    pytest.importorskip("flask")
    from pystreammcp.server import create_flask_app

    monkeypatch.setenv("PYSTREAMMCP_API_KEY", "secret")
    app = create_flask_app()
    client = app.test_client()
    assert client.get("/health").status_code == 200
    assert client.get("/agents").status_code == 401
    assert client.get("/agents", headers={"X-API-Key": "secret"}).status_code == 200
