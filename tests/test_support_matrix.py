"""Assert the documented integration support matrix matches code and packaging.

Supported extras must have a real-framework test that skips only when the
optional dependency is absent. Experimental helpers must raise a clear error
unless explicitly opted in, and must not be advertised as extras.
"""

import asyncio
import importlib.util
import re
from pathlib import Path

import pytest
from pystreammcp.adapters import AdapterConfig, FrameworkType
from pystreammcp.experimental import (
    EXPERIMENTAL_ENV_VAR,
    ExperimentalIntegrationError,
)

ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = ROOT / "pyproject.toml"
README = ROOT / "README.md"
INTEGRATIONS_DOC = ROOT / "docs" / "INTEGRATIONS.md"

SUPPORTED_EXTRAS = {"langchain", "llamaindex", "semantic-kernel"}
NON_INTEGRATION_EXTRAS = {
    "dev",
    "federation",
    "api",
    "mcp",
    "crawl",
    "all-integrations",
}
EXPERIMENTAL_EXTRAS = {"crewai", "pydantic-ai", "haystack", "temporal", "airflow"}


def _load_pyproject():
    text = PYPROJECT.read_text()
    try:
        import tomllib

        return tomllib.loads(text)
    except ModuleNotFoundError:
        import toml

        return toml.loads(text)


def _distribution_name(requirement: str) -> str:
    return re.split(r"[<>=!~\[]", requirement, maxsplit=1)[0].strip().lower()


def _experimental_factories():
    from pystreammcp.integrations.crewai import CrewAIAdapter
    from pystreammcp.integrations.haystack import HaystackAdapter
    from pystreammcp.integrations.pydantic_ai import PydanticAIAdapter
    from pystreammcp.orchestration.airflow import (
        PyStreamMCPDAGFactory,
        PyStreamMCPDiscoveryOperator,
        PyStreamMCPOptimizeOperator,
        PyStreamMCPQueryOperator,
    )
    from pystreammcp.orchestration.temporal import (
        TemporalClient,
        TemporalDiscoveryActivity,
        TemporalQueryActivity,
        TemporalWorkflow,
    )

    return [
        lambda: CrewAIAdapter(
            AdapterConfig(
                framework=FrameworkType.CREWAI, agent_id="crewai", name="CrewAI"
            )
        ),
        lambda: PydanticAIAdapter(
            AdapterConfig(
                framework=FrameworkType.PYDANTIC_AI,
                agent_id="pydantic",
                name="Pydantic AI",
            )
        ),
        lambda: HaystackAdapter(
            AdapterConfig(
                framework=FrameworkType.HAYSTACK, agent_id="haystack", name="Haystack"
            )
        ),
        lambda: TemporalQueryActivity(agent_id="a", query_text="q"),
        lambda: TemporalDiscoveryActivity(agent_id="a", context="c"),
        lambda: TemporalWorkflow("w", "a"),
        lambda: TemporalClient(),
        lambda: PyStreamMCPQueryOperator("t", "a", "q"),
        lambda: PyStreamMCPDiscoveryOperator("t", "a", "c"),
        lambda: PyStreamMCPOptimizeOperator("t", "a", "q"),
        lambda: PyStreamMCPDAGFactory(),
    ]


def test_packaging_advertises_only_supported_extras():
    extras = _load_pyproject()["project"]["optional-dependencies"]

    integration_extras = set(extras) - NON_INTEGRATION_EXTRAS
    assert integration_extras == SUPPORTED_EXTRAS
    assert not (EXPERIMENTAL_EXTRAS & set(extras))

    all_integrations = {
        _distribution_name(requirement) for requirement in extras["all-integrations"]
    }
    assert all_integrations == {"langchain", "llama-index", "semantic-kernel"}


@pytest.mark.parametrize(
    "module,adapter_import,adapter_name,factory_name",
    [
        (
            "langchain_core",
            "pystreammcp.integrations.langchain",
            "LangchainAdapter",
            "get_tool_for_langchain",
        ),
        (
            "llama_index.core",
            "pystreammcp.integrations.llamaindex",
            "LlamaIndexAdapter",
            "get_retriever_for_llamaindex",
        ),
        (
            "semantic_kernel",
            "pystreammcp.integrations.semantic_kernel",
            "SemanticKernelAdapter",
            "get_native_plugin",
        ),
    ],
)
def test_supported_adapters_skip_only_on_missing_dependency(
    module, adapter_import, adapter_name, factory_name
):
    try:
        module_spec = importlib.util.find_spec(module)
    except ModuleNotFoundError:
        module_spec = None
    if module_spec is None:
        pytest.skip(f"{module} is an optional dependency and is not installed")

    adapter_module = importlib.import_module(adapter_import)
    adapter_cls = getattr(adapter_module, adapter_name)
    framework = {
        "LangchainAdapter": FrameworkType.LANGCHAIN,
        "LlamaIndexAdapter": FrameworkType.LLAMAINDEX,
        "SemanticKernelAdapter": FrameworkType.SEMANTIC_KERNEL,
    }[adapter_name]
    adapter = adapter_cls(
        AdapterConfig(
            framework=framework,
            agent_id=f"matrix_{framework.value}",
            name=f"Matrix {framework.value}",
        )
    )

    native = getattr(adapter, factory_name)()
    if asyncio.iscoroutine(native):
        native = asyncio.run(native)
    assert native is not None


@pytest.mark.parametrize("factory", _experimental_factories())
def test_experimental_helpers_raise_without_opt_in(monkeypatch, factory):
    monkeypatch.delenv(EXPERIMENTAL_ENV_VAR, raising=False)
    with pytest.raises(
        ExperimentalIntegrationError, match="experimental and unsupported"
    ):
        factory()


def test_experimental_helpers_allow_explicit_opt_in(monkeypatch):
    monkeypatch.delenv(EXPERIMENTAL_ENV_VAR, raising=False)
    from pystreammcp.orchestration.temporal import TemporalQueryActivity

    result = TemporalQueryActivity(
        agent_id="opt_in", query_text="q", experimental=True
    ).execute()
    assert result["status"] == "completed"


def test_docs_mark_every_experimental_integration_unsupported():
    matrix = INTEGRATIONS_DOC.read_text()
    display_names = {
        "CrewAI",
        "Pydantic AI",
        "Haystack",
        "Temporal",
        "Airflow",
    }
    for name in display_names:
        rows = [
            line
            for line in matrix.splitlines()
            if line.startswith(f"| **{name}**")
        ]
        assert rows, f"{name} is missing from docs/INTEGRATIONS.md"
        assert any(
            "experimental" in row.lower() and "unsupported" in row.lower()
            for row in rows
        ), f"{name} must be marked experimental/unsupported"
    assert EXPERIMENTAL_ENV_VAR in matrix


def test_readme_does_not_advertise_experimental_extras():
    readme = README.read_text()
    for extra in EXPERIMENTAL_EXTRAS:
        assert f"PyStreamMCP[{extra}]" not in readme
    assert "Experimental / unsupported integrations" in readme
    assert "PyStreamMCP[all-integrations]" in readme
