"""Runtime guard for experimental, unsupported integrations."""

from __future__ import annotations

import os

EXPERIMENTAL_ENV_VAR = "PYSTREAMMCP_ENABLE_EXPERIMENTAL"


class ExperimentalIntegrationError(RuntimeError):
    """Raised when an experimental integration is used without explicit opt-in."""


def experimental_opt_in_enabled() -> bool:
    """Return True when the environment opt-in is enabled."""
    value = os.environ.get(EXPERIMENTAL_ENV_VAR, "")
    return value.strip().lower() in {"1", "true", "yes", "on"}


def require_experimental_opt_in(name: str, enabled: bool = False) -> None:
    """Raise unless the caller explicitly opts in to an experimental integration."""
    if enabled or experimental_opt_in_enabled():
        return
    raise ExperimentalIntegrationError(
        f"{name} is experimental and unsupported: PyStreamMCP does not test it "
        f"against the real {name} package and ships no adapter for its SDK. "
        "To use this in-process helper anyway, pass experimental=True or set "
        f"{EXPERIMENTAL_ENV_VAR}=1. Supported integrations are langchain, "
        "llamaindex, and semantic-kernel."
    )
