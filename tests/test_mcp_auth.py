"""MCP call_tool auth tests."""

from __future__ import annotations

from pystreammcp.mcp_server import PyStreamMCPServer


def test_call_tool_requires_token_when_configured(monkeypatch):
    monkeypatch.setenv("PYSTREAMMCP_API_KEY", "secret")
    server = PyStreamMCPServer()
    result = server.call_tool("pystreammcp_discover", {"context": "x"})
    assert result["status"] == "error"
    assert result["error_type"] == "AuthenticationError"
    ok = server.call_tool("pystreammcp_discover", {"context": "x"}, auth_token="secret")
    assert ok.get("error_type") != "AuthenticationError"


def test_call_tool_open_without_key(monkeypatch):
    monkeypatch.delenv("PYSTREAMMCP_API_KEY", raising=False)
    server = PyStreamMCPServer()
    result = server.call_tool("pystreammcp_discover", {"context": "x"})
    assert result.get("error_type") != "AuthenticationError"
