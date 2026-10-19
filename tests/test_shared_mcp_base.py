"""Verify PyStreamMCP actually uses StatGuardian's canonical MCP base.

The connector has a local fallback for installs that predate
``statguardian._mcp_connector``. When StatGuardian *is* importable, the shared
base must be the one in use -- otherwise the two implementations silently
diverge.
"""

import pytest
from pystreammcp._mcp_connector import Orchestrator, _MCPOrchestratorConnector


def test_shared_base_is_used_when_statguardian_is_installed():
    shared = pytest.importorskip("statguardian._mcp_connector")

    from pystreammcp import _mcp_connector as pystreammcp_connector

    assert pystreammcp_connector.BaseMCPConnector is shared.BaseMCPConnector


def test_connector_generates_secure_shared_config(tmp_path):
    shared = pytest.importorskip("statguardian._mcp_connector")

    orchestrator = Orchestrator(config_path=str(tmp_path / "missing.toml"))
    connector = _MCPOrchestratorConnector(orchestrator=orchestrator, port=9123)

    assert isinstance(connector, shared.BaseMCPConnector)
    assert connector.host == "127.0.0.1"
    assert connector.cors_origins == []

    config = connector._generate_dab_config({"tool_a": {}})
    assert config["runtime"] == {
        "host": "127.0.0.1",
        "port": 9123,
        "cors": {"origins": []},
    }
    assert config["entities"]["tool_a"]["permissions"] == [
        {"actions": ["read"], "roles": ["local"]}
    ]


def test_connector_rejects_remote_bind_without_opt_in():
    pytest.importorskip("statguardian._mcp_connector")

    from pystreammcp._mcp_connector import BaseMCPConnector

    class _Remote(BaseMCPConnector):
        def get_mcp_tools(self):
            return {}

        def get_tool_handlers(self):
            return object()

    with pytest.raises(ValueError, match="allow_remote=True"):
        _Remote("PyStreamMCP", port=9123, host="0.0.0.0")
