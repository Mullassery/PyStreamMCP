# Cross-repo integration status

PyStreamMCP integrates with sibling projects and third-party frameworks. This
page records what is **wired**, what is **real-tested**, and what is **not
tested**. Fake-module tests are contract tests, not evidence that a real
dependency works.

Verified **2026-10-20**.

## Support levels

- **Supported** — has an extra, imports the real third-party package, and has a
  test that runs against it (skipping only when the optional dependency is not
  installed). CI installs the supported extras.
- **Experimental / unsupported** — in-process helper code exists, but it does
  not import or construct the vendor SDK, has no real-framework test, and has no
  extra. Constructing it raises `ExperimentalIntegrationError` unless you opt in
  with `experimental=True` or `PYSTREAMMCP_ENABLE_EXPERIMENTAL=1`. Do not treat
  it as an integration.
- **Not tested** — no real test; a skipped test means not tested, not supported.

## Matrix

| Integration | Level | Wired | Real-tested | Gaps / notes |
|---|---|---|---|---|
| **StatGuardian** `/validate` | Supported | ✅ `QualityValidator(statguardian_url=...)` | ✅ `tests/test_statguardian_live.py` (real service: pass, block, unreachable) | `enum`/range constraints were not enforced by the single-row endpoint in 2.8.0; the no-URL mode is local heuristics, not a client |
| **MudFish** crawl | Supported | ✅ `pystreammcp_crawl` | ✅ `tests/test_mudfish_live.py` (real engine; SSRF skips loopback) | A **successful external fetch is not tested** (network-dependent) |
| **LangChain** | Supported | ✅ `[langchain]` extra, real `langchain_core` objects | ✅ `tests/test_langchain_integration.py`, `tests/test_sprint2_langchain.py` (CI installs the extra) | wide version floor; no upper bound |
| **LlamaIndex** | Supported | ✅ `[llamaindex]` extra, real `llama_index.core` objects | ✅ `tests/test_llamaindex_integration.py`, `tests/test_sprint3_rag_frameworks.py` (CI installs the extra) | wide version floor |
| **Semantic Kernel** | Supported | ✅ `[semantic-kernel]` extra, real `semantic_kernel` import | ✅ `tests/test_sprint3_rag_frameworks.py` (CI installs the extra) | wide version floor |
| **CrewAI** | Experimental / unsupported | ⚠️ `pystreammcp.integrations.crewai` helper only; no `crewai` extra | ❌ no real CrewAI test; module never imports CrewAI | Guard raises `ExperimentalIntegrationError`; removed from `all-integrations` |
| **Pydantic AI** | Experimental / unsupported | ⚠️ `pystreammcp.integrations.pydantic_ai` helper only; no `pydantic-ai` extra | ❌ no real Pydantic AI test; module never imports `pydantic_ai` | Guard raises `ExperimentalIntegrationError`; removed from `all-integrations` |
| **Haystack** | Experimental / unsupported | ⚠️ `pystreammcp.integrations.haystack` helper only; no `haystack` extra | ❌ no real Haystack test; module never imports `haystack` | Guard raises `ExperimentalIntegrationError`; removed from `all-integrations` |
| **Temporal** | Experimental / unsupported | ⚠️ `pystreammcp.orchestration.temporal` helper only; no `temporalio` extra | ❌ no Temporal server/workflow test; module never imports `temporalio` | `TemporalClient` is not a real Temporal client; guard raises `ExperimentalIntegrationError` |
| **Airflow** | Experimental / unsupported | ⚠️ `pystreammcp.orchestration.airflow` helper only; no `apache-airflow` extra | ❌ no Airflow DAG test; module never imports `airflow` | Operators are not `BaseOperator` subclasses; guard raises `ExperimentalIntegrationError` |
| **StatGuardian `_mcp_connector` shared base** | Supported | ✅ imports the shared base when StatGuardian is installed; local fallback retained | ✅ `tests/test_shared_mcp_base.py` (asserts the shared class is the one in use and its secure config) | Older StatGuardian installs still use the embedded fallback |

`all-integrations` installs **only** the supported extras: `langchain`,
`llama-index`, and `semantic-kernel`. The experimental extras (`crewai`,
`pydantic-ai`, `haystack`, `temporal`, `airflow`) were removed from
`pyproject.toml`; install those vendor packages yourself only if you are
experimenting with the unsupported helper modules.

## StatGuardian modes

```python
from pystreammcp.quality import QualityValidator, ValidationGate

# Real service (recommended when available)
validator = QualityValidator(statguardian_url="http://127.0.0.1:8000")
validator.register_gate(ValidationGate(dataset_id="orders", min_quality_score=0.8))

# Local heuristics (no service) — clearly not a StatGuardian client
local = QualityValidator()
```

The service mode posts `source_data` as `{"entity": {"attributes": ...}}` to
`/validate` and fails closed (`QualityStatus.UNKNOWN`) when the service is
unreachable.

## Experimental opt-in

```python
from pystreammcp.integrations.crewai import CrewAIAdapter
from pystreammcp.adapters import AdapterConfig, FrameworkType

config = AdapterConfig(
    framework=FrameworkType.CREWAI,
    agent_id="experiment",
    name="Experiment",
)
adapter = CrewAIAdapter(config, experimental=True)
```

The same environment opt-in works for every experimental module:

```bash
export PYSTREAMMCP_ENABLE_EXPERIMENTAL=1
```

Opting in changes only the guard; it does not make the helper a real vendor
integration or a supported feature.

## Running the real tests

```bash
# StatGuardian (needs statguardian[api])
pytest tests/test_statguardian_live.py -q

# MudFish
pip install mudfish
pytest tests/test_mudfish_live.py -q

# Supported framework extras
pip install -e ".[langchain,llamaindex,semantic-kernel]"
pytest tests/test_support_matrix.py -q
```

A skipped test means **not tested**, not supported.
