"""Shared pytest configuration and fixtures.

Puts `python/` on `sys.path` once, centrally, instead of every test file
repeating its own `sys.path.insert` (previously duplicated across 5 files
independently). Also exposes the reusable mock/failure-injection fixtures
from `pystreammcp.testing` as pytest fixtures, so downstream test suites --
and this repo's own -- get "mock server fixtures out-of-the-box" rather
than each writing (or copy-pasting) their own.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

import pytest

from pystreammcp.testing import (
    ContextWindowExceededError,
    FailingAdapter,
    FailingAgent,
    MalformedModelResponseError,
    MockAdapter,
    RateLimitError,
)
from pystreammcp.adapters import AdapterConfig, FrameworkType


@pytest.fixture
def mock_adapter() -> MockAdapter:
    """A happy-path AgentFrameworkAdapter that always succeeds."""
    config = AdapterConfig(
        framework=FrameworkType.LANGCHAIN,
        agent_id="mock_agent",
        name="Mock Agent",
    )
    return MockAdapter(config)


@pytest.fixture(params=[RateLimitError, ContextWindowExceededError, MalformedModelResponseError])
def llm_failure(request) -> Exception:
    """Parametrized over all three simulated LLM failure states -- a test
    using this fixture runs once per failure type."""
    return request.param("simulated failure")


@pytest.fixture
def failing_agent(llm_failure) -> FailingAgent:
    """An Agent-compatible stand-in whose query() raises `llm_failure`."""
    return FailingAgent(llm_failure)


@pytest.fixture
def failing_adapter(llm_failure) -> FailingAdapter:
    """An AgentFrameworkAdapter whose every method raises `llm_failure`."""
    config = AdapterConfig(
        framework=FrameworkType.LANGCHAIN,
        agent_id="failing_agent",
        name="Failing Agent",
    )
    return FailingAdapter(config, llm_failure)
