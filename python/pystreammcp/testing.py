"""Reusable test doubles for PyStreamMCP, exported for downstream use.

Previously the only mock (`MockAdapter` in `tests/test_sprint1_foundation.py`)
was test-local -- not importable by a downstream project's own test suite,
and not usable for simulating real LLM/framework failure states (rate
limits, context-window overruns, malformed model responses) at all, since it
only ever returned a fixed happy-path result.

This module provides:
  - `MockAdapter`: the same happy-path mock, promoted here so it's a real,
    importable, reusable fixture instead of copy-pasted per test file.
  - `RateLimitError`, `ContextWindowExceededError`,
    `MalformedModelResponseError`: the three LLM-failure classes named in
    the "no end-to-end tests for LLM failure states" gap. PyStreamMCP's own
    code never calls a model provider directly (see README "Known Issues"),
    so these aren't wrapping any provider-specific SDK exception -- they
    exist to let tests exercise how PyStreamMCP's *own* code (the MCP tool
    dispatcher, adapter query paths) behaves when something it's
    orchestrating (a real `Agent`/`AgentFrameworkAdapter` a caller plugs in)
    fails in one of these ways, without needing network access or a real
    API key.
  - `FailingAgent` / `FailingAdapter`: drop-in stand-ins for `Agent` /
    `AgentFrameworkAdapter` that raise a configured failure on `query()`
    instead of computing a result.
"""

from typing import Any, Dict, Optional

from .adapters import AdapterConfig, AgentFrameworkAdapter, QueryResult


class RateLimitError(Exception):
    """Raised by a test double to simulate a model provider rate limit."""


class ContextWindowExceededError(Exception):
    """Raised by a test double to simulate exceeding the model's context window."""


class MalformedModelResponseError(Exception):
    """Raised by a test double to simulate a model returning invalid/unparseable JSON."""


class MockAdapter(AgentFrameworkAdapter):
    """Happy-path mock adapter: always returns a fixed, valid result.

    Useful for tests that need *an* adapter wired in but don't care about
    its output -- for failure-injection tests, use `FailingAdapter` instead.
    """

    def query(self, text: str, intent: str = "retrieve", **kwargs) -> QueryResult:
        return QueryResult(
            query_id="mock-query-1",
            text=text,
            intent=intent,
            baseline_tokens=1000,
            optimized_tokens=400,
            cost_reduction_percent=60.0,
            execution_time_ms=150.5,
            context={"result": "mock"},
        )

    async def query_async(self, text: str, intent: str = "retrieve", **kwargs) -> QueryResult:
        return self.query(text, intent, **kwargs)

    def discover(self, context: str, **kwargs) -> Dict[str, Any]:
        return {
            "sources": [{"name": "source_1", "relevance": 0.95}],
            "total": 1,
        }

    async def discover_async(self, context: str, **kwargs) -> Dict[str, Any]:
        return self.discover(context, **kwargs)

    def optimize(self, query_text: str, strategy: Optional[str] = None, **kwargs) -> QueryResult:
        return self.query(query_text)

    async def optimize_async(
        self, query_text: str, strategy: Optional[str] = None, **kwargs
    ) -> QueryResult:
        return self.optimize(query_text, strategy, **kwargs)


class FailingAgent:
    """Drop-in stand-in for `pystreammcp.agent.Agent`: raises `failure` from
    `query()` instead of computing a result. Pass to
    `PyStreamMCPServer(agent=FailingAgent(RateLimitError(...)))` to test how
    the MCP tool-call path handles a failure during execution."""

    def __init__(self, failure: Exception):
        self.failure = failure

    def query(self, text: str, *args, **kwargs):
        raise self.failure


class FailingAdapter(AgentFrameworkAdapter):
    """Drop-in `AgentFrameworkAdapter` that raises `failure` from every
    operation, for framework-integration failure-path tests."""

    def __init__(self, config: AdapterConfig, failure: Exception):
        super().__init__(config)
        self.failure = failure

    def query(self, text: str, intent: str = "retrieve", **kwargs) -> QueryResult:
        raise self.failure

    async def query_async(self, text: str, intent: str = "retrieve", **kwargs) -> QueryResult:
        raise self.failure

    def discover(self, context: str, **kwargs) -> Dict[str, Any]:
        raise self.failure

    async def discover_async(self, context: str, **kwargs) -> Dict[str, Any]:
        raise self.failure

    def optimize(self, query_text: str, strategy: Optional[str] = None, **kwargs) -> QueryResult:
        raise self.failure

    async def optimize_async(
        self, query_text: str, strategy: Optional[str] = None, **kwargs
    ) -> QueryResult:
        raise self.failure
