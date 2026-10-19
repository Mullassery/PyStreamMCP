# Cross-repo integration status

PyStreamMCP integrates with sibling projects and third-party frameworks. This
page records what is **wired**, what is **real-tested**, and what is **not
tested**. Fake-module tests are contract tests, not evidence that a real
dependency works.

Verified **2026-10-19**.

## Matrix

| Integration | Wired | Real-tested | Gaps / not tested |
|---|---|---|---|
| **StatGuardian** `/validate` | ✅ `QualityValidator(statguardian_url=...)` | ✅ `tests/test_statguardian_live.py` (real service: pass, block, unreachable) | `enum`/range constraints were not enforced by the single-row endpoint in 2.8.0; the no-URL mode is local heuristics, not a client |
| **MudFish** crawl | ✅ `pystreammcp_crawl` | ✅ `tests/test_mudfish_live.py` (real engine; SSRF skips loopback) | A **successful external fetch is not tested** (network-dependent) |
| **LangChain** | ✅ `[langchain]` extra | ✅ real integration tests (CI installs the extra) | wide version floor; no upper bound |
| **LlamaIndex** | ✅ `[llamaindex]` extra | ✅ real integration tests (CI installs the extra) | wide version floor |
| **Semantic Kernel** | ✅ `[semantic-kernel]` extra | ✅ real integration tests (CI installs the extra) | wide version floor |
| **CrewAI** | ✅ `[crewai]` extra | ❌ **not tested** | no test; mark experimental or remove |
| **Pydantic AI** | ✅ `[pydantic-ai]` extra | ❌ **not tested** | no test |
| **Haystack** | ✅ `[haystack]` extra | ❌ **not tested** | no test |
| **Temporal** | ✅ `[temporal]` extra | ❌ **not tested** | no test |
| **Airflow** | ✅ `[airflow]` extra | ❌ **not tested** | no test |
| **StatGuardian `_mcp_connector` shared base** | ⚠️ import attempted, local fallback | ❌ **not wired** | StatGuardian does not ship `_mcp_connector`; each consumer defines its own fallback |

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

## Running the real tests

```bash
# StatGuardian (needs statguardian[api])
pytest tests/test_statguardian_live.py -q

# MudFish
pip install mudfish
pytest tests/test_mudfish_live.py -q
```

A skipped test means **not tested**, not supported.
