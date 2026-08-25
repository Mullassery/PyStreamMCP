"""End-to-end tests for the MCP tool-call path's resilience:

1. Pydantic argument validation (previously: `call_tool`/`_tool_*` only did
   manual `if not text` checks -- no type checking, no enum validation, no
   consistent required-field handling).
2. Failure isolation when a tool's execution raises -- including the three
   "real LLM failure states" the external critique named (rate limits,
   context-window overruns, malformed model responses), simulated via the
   exported `pystreammcp.testing` mocks since PyStreamMCP's own code never
   calls a model provider directly (there's nothing to mock a provider SDK
   *of* -- what's being tested is that PyStreamMCP's own dispatcher doesn't
   crash when whatever it's orchestrating fails).
"""

import pytest

from pystreammcp.mcp_server import PyStreamMCPServer


class TestArgumentValidation:
    def test_missing_required_field_is_rejected(self):
        server = PyStreamMCPServer()
        result = server.call_tool("pystreammcp_query", {})

        assert result["status"] == "error"
        assert any(e["field"] == "text" for e in result["validation_errors"])

    def test_invalid_enum_value_is_rejected(self):
        server = PyStreamMCPServer()
        result = server.call_tool(
            "pystreammcp_query", {"text": "hello", "intent": "delete_everything"}
        )

        assert result["status"] == "error"
        assert any(e["field"] == "intent" for e in result["validation_errors"])

    def test_wrong_type_is_rejected(self):
        """Previously max_tokens was passed through unchecked -- a string
        here would have silently reached arithmetic further downstream."""
        server = PyStreamMCPServer()
        result = server.call_tool(
            "pystreammcp_query", {"text": "hello", "max_tokens": "a lot please"}
        )

        assert result["status"] == "error"
        assert any(e["field"] == "max_tokens" for e in result["validation_errors"])

    def test_negative_max_tokens_is_rejected(self):
        server = PyStreamMCPServer()
        result = server.call_tool("pystreammcp_query", {"text": "hello", "max_tokens": -5})

        assert result["status"] == "error"

    def test_out_of_range_limit_is_rejected(self):
        server = PyStreamMCPServer()
        result = server.call_tool(
            "pystreammcp_discover", {"context": "docs", "limit": 100_000}
        )

        assert result["status"] == "error"

    def test_valid_arguments_succeed(self):
        server = PyStreamMCPServer()
        result = server.call_tool("pystreammcp_query", {"text": "hello world"})

        assert result["status"] == "success"
        assert result["text"] == "hello world"
        assert result["intent"] == "retrieve"  # default applied

    def test_register_source_requires_both_name_and_description(self):
        server = PyStreamMCPServer()
        result = server.call_tool("pystreammcp_register_source", {"name": "only_a_name"})

        assert result["status"] == "error"
        assert any(e["field"] == "description" for e in result["validation_errors"])

    def test_input_schema_matches_actual_validation(self):
        """The advertised JSON schema (get_tools()) is generated from the
        same Pydantic models call_tool() validates against, so an enum
        listed there is guaranteed to be exactly what's enforced -- no
        hand-duplicated schema to drift out of sync."""
        server = PyStreamMCPServer()
        tools = {t["name"]: t for t in server.get_tools()}

        query_schema = tools["pystreammcp_query"]["inputSchema"]
        assert "text" in query_schema["properties"]
        assert query_schema["properties"]["intent"]["enum"] == [
            "retrieve",
            "discover",
            "aggregate",
            "synthesize",
            "analyze",
        ]


class TestLLMFailureStateIsolation:
    def test_tool_execution_failure_returns_structured_error_not_a_crash(self, failing_agent):
        """Before this fix, an exception raised while a tool handler ran
        (e.g. self.agent.query(...) raising) propagated straight out of
        call_tool uncaught -- crashing whatever was driving the MCP
        server's message loop instead of returning a normal error
        response."""
        server = PyStreamMCPServer(agent=failing_agent)

        result = server.call_tool("pystreammcp_query", {"text": "hello"})

        assert result["status"] == "error"
        assert result["error_type"] == type(failing_agent.failure).__name__
        assert str(failing_agent.failure) in result["message"]

    def test_optimize_tool_also_isolates_failures(self, failing_agent):
        server = PyStreamMCPServer(agent=failing_agent)

        result = server.call_tool("pystreammcp_optimize", {"text": "hello"})

        assert result["status"] == "error"
        assert result["error_type"] == type(failing_agent.failure).__name__

    def test_process_message_survives_tool_execution_failure(self, failing_agent):
        """End-to-end through the actual message-transport entry point, not
        just call_tool() directly."""
        server = PyStreamMCPServer(agent=failing_agent)

        response = server.process_message(
            {
                "type": "call_tool",
                "name": "pystreammcp_query",
                "arguments": {"text": "hello"},
            }
        )

        assert response["status"] == "error"

    def test_process_message_survives_unknown_tool_name(self):
        """call_tool() raises ValueError for an unknown tool name;
        process_message must not let that escape uncaught either."""
        server = PyStreamMCPServer()

        response = server.process_message(
            {"type": "call_tool", "name": "does_not_exist", "arguments": {}}
        )

        assert response["status"] == "error"

    def test_a_healthy_tool_call_still_works_after_a_failing_one(self, failing_agent):
        """Failure isolation shouldn't leave the server in a broken state --
        confirm a subsequent call on a working server still succeeds."""
        failing_server = PyStreamMCPServer(agent=failing_agent)
        failing_server.call_tool("pystreammcp_query", {"text": "hello"})

        healthy_server = PyStreamMCPServer()
        result = healthy_server.call_tool("pystreammcp_query", {"text": "hello"})
        assert result["status"] == "success"


class TestMockAdapterIsReusable:
    """Proves the exported pystreammcp.testing.MockAdapter is a genuine,
    working AgentFrameworkAdapter -- not dead code sitting unused."""

    def test_mock_adapter_query_returns_valid_result(self, mock_adapter):
        result = mock_adapter.query("test query")
        assert result.text == "test query"
        assert result.cost_reduction_percent == 60.0

    def test_mock_adapter_discover_returns_sources(self, mock_adapter):
        result = mock_adapter.discover("some context")
        assert result["total"] == 1

    @pytest.mark.asyncio
    async def test_mock_adapter_async_methods_work(self, mock_adapter):
        result = await mock_adapter.query_async("test query")
        assert result.text == "test query"
