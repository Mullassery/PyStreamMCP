# PyStreamMCP

[![CI](https://github.com/Mullassery/PyStreamMCP/actions/workflows/ci.yml/badge.svg)](https://github.com/Mullassery/PyStreamMCP/actions/workflows/ci.yml)

An AI-agent intelligence layer: query planning, context discovery, and
token-cost optimization, exposed both as a Python SDK and as an MCP
(Model Context Protocol) tool server, plus a small event-driven
orchestration/federation layer for coordinating multiple MCP endpoints.

Pure Python — `pip install` just works, no Rust toolchain or compiler
required.

## Use cases

- **Giving an AI agent a query-planning layer over multiple data
  sources**, exposed as real MCP tools rather than hand-rolled per-agent
  glue code.
- **Coordinating multiple MCP endpoints** through the event-driven
  orchestration/federation layer instead of wiring each one separately.
- **Tracking token-cost optimization** across agent queries.
- **Not yet a good fit for:** anything depending on the Rust workspace —
  see [Rust workspace (not shipped)](#rust-workspace-not-shipped) below;
  the published package is pure Python only.

## Install

```bash
pip install PyStreamMCP
```

Optional extras, install what you actually need:

```bash
pip install "PyStreamMCP[api]"          # FastAPI + Flask HTTP servers
pip install "PyStreamMCP[mcp]"          # MCP protocol client library
pip install "PyStreamMCP[langchain]"    # LangChain adapter
pip install "PyStreamMCP[llamaindex]"   # LlamaIndex adapter
pip install "PyStreamMCP[semantic-kernel]"  # Semantic Kernel adapter
pip install "PyStreamMCP[all-integrations]" # every framework adapter
```

Requires Python 3.9+ for the core SDK (`Agent`, `SourceRegistry`,
`Orchestrator`). The `mcp` and `semantic-kernel` extras require Python
3.10+ — their upstream packages don't publish Python 3.9-compatible
releases, so `pip install` for those extras will fail on 3.9. CI tests
3.10, 3.11, and 3.12 only; 3.9 is not covered by CI.

## Quick start

```python
from pystreammcp import Agent

agent = Agent(
    agent_id="recommendation_engine",
    name="Product Recommendation Engine",
    optimization_strategy="token_efficient",  # or "balanced" / "quality_first"
    max_tokens=1000,
)

result = agent.query("What are the top 10 customers by lifetime value?")

print(f"Baseline tokens:  {result.baseline_tokens}")
print(f"Optimized tokens: {result.optimized_tokens}")
print(f"Reduction:        {result.cost_reduction_percent:.1f}%")
```

Token counts are estimated from the actual query text (a standard
~4-characters-per-token heuristic) and the reduction percentage is
computed from the selected `optimization_strategy` — not a fixed number
returned regardless of input. See [`examples/basic_usage.py`](examples/basic_usage.py)
for a full runnable walkthrough, including framework adapters for
LangChain, LlamaIndex, CrewAI, Semantic Kernel, PydanticAI, and Haystack
under [`pystreammcp.integrations`](python/pystreammcp/integrations/).

## Data source discovery

`SourceRegistry` (`pystreammcp.SourceRegistry`) ranks *registered* data
sources by real word-overlap relevance to a query — not a fabricated or
hardcoded result:

```python
from pystreammcp import SourceRegistry

registry = SourceRegistry()
registry.register(
    "orders_db",
    description="customer order history and revenue by quarter",
    type="database",
    tags=["orders", "revenue"],
)

results = registry.discover("customer revenue by quarter")
# [{"name": "orders_db", "type": "database", "relevance": 0.4444, "matched_terms": [...]}]
```

The same registry backs `POST /discover` (REST), the `pystreammcp_discover`
MCP tool, and `LangchainAdapter.discover()` — register sources once via
`POST /sources` / `pystreammcp_register_source` / `registry.register()`,
then discover against them from any of the three surfaces. This is a
simple Jaccard token-overlap heuristic, not semantic/embedding search.

## MCP orchestration & federation

`Orchestrator` (`pystreammcp.Orchestrator`) discovers and routes across
other MCP-enabled projects you configure in `pystreammcp.toml`:

```toml
[federation]
endpoints = [
    "http://localhost:8765/mcp",
    "http://localhost:8766/mcp",
]
```

```python
from pystreammcp import Orchestrator

orch = Orchestrator()  # reads ./pystreammcp.toml
result = orch.discover_mcp_projects()
# {"projects": [{"project_name": ..., "endpoint": ..., "status": "healthy"|"unavailable", ...}], "total": N}
```

This actually probes each configured endpoint's real `tools/list` MCP
method — with nothing configured, or nothing reachable, it honestly
reports zero/unavailable projects rather than a fixed fixture list.
`Orchestrator` also does lexical tool-relevance ranking
(`rank_tools_by_relevance`) and capability matching
(`detect_compatible_projects`) against whatever it actually discovers.

To expose these (plus tool-routing and webhook-event handling) as MCP
tools, `PyStreamMCPHandler` (`pystreammcp._mcp_tools`) wires the MCP
tool-call surface directly to a live `Orchestrator`/`EventRouter`
instance — every handler call is backed by real, inspectable state, not
a hardcoded response.

**Honest limitations**: a few orchestration capabilities are accepted at
the API level but not fully implemented yet — cross-project federated
query *execution* and cross-database joins currently report
`"status": "not_implemented"` with an explanation, rather than fabricated
result rows, because there's no real query engine behind them yet.

## Webhook event server

`pystreammcp.server.create_flask_app()` exposes a small REST/webhook
surface for orchestration events (agent MCPs reporting `mcp.available`,
`tool.invoked`, health updates, etc. to `POST /orchestration/webhooks/events`).

### Webhook security (HMAC-SHA256)

Inbound events to `/orchestration/webhooks/events` must be signed:

```bash
export PYSTREAMMCP_WEBHOOK_SECRET="a long random shared secret"
```

Senders compute `HMAC-SHA256(secret, raw_request_body)` and send it as:

```
X-PyStreamMCP-Signature: sha256=<hex digest>
```

```python
from pystreammcp.server import compute_webhook_signature
import json, requests

body = json.dumps({"event_type": "mcp.available", "data": {...}}).encode()
signature = compute_webhook_signature(secret, body)

requests.post(
    "http://localhost:8000/orchestration/webhooks/events",
    data=body,
    headers={
        "Content-Type": "application/json",
        "X-PyStreamMCP-Signature": signature,
    },
)
```

Requests with a missing or invalid signature are rejected with `401`. If
`PYSTREAMMCP_WEBHOOK_SECRET` isn't set at all, the endpoint fails closed
and rejects every request with `503` — there is no "accept unsigned
events" fallback.

### Network defaults

The HTTP servers (`PyStreamMCPServer` / `create_flask_app()`,
`PyStreamMCPAPI.run`) bind to `127.0.0.1` (localhost-only) by default.
Pass `host="0.0.0.0"` explicitly if you need the server reachable from
other hosts — e.g. inside a container that already has its own network
boundary.

**The `pystreammcp` CLI**: `pip install PyStreamMCP` now installs a real
`pystreammcp` command (`[project.scripts]` in `pyproject.toml`) backed by
the Click group in `python/pystreammcp/cli.py`:
`query`/`server`/`version`/`dashboard`. `python -m pystreammcp.cli` reaches
the same Click group (the file's old, separate, smaller hand-rolled
command set has been removed). `server` lazy-imports `pystreammcp.api`, so
`pystreammcp version`/`query`/`dashboard` work without installing the
`api` extra; running `pystreammcp server` without it prints a clear
"install `pystreammcp[api]`" error instead of crashing with
`ModuleNotFoundError`. See [`ROADMAP_HONEST.md`](ROADMAP_HONEST.md) §2.2
(now marked fixed) for how this was previously broken.

## Testing

```bash
pip install -e ".[dev,api,mcp,langchain,llamaindex,semantic-kernel]"
pytest tests/ -v
```

Note: this exact command needs Python 3.10+ (see [Install](#install)); on
3.9 the `mcp` and `semantic-kernel` extras fail to resolve, so drop them
from the extras list if you're on 3.9.

## Known Issues

- ~~No end-to-end tests for LLM failure states~~ **Fixed.** PyStreamMCP's
  own code never calls a model provider directly (no code path here to add
  `except RateLimitError`/`APIError` handling *to* — see `AgentFrameworkAdapter`
  below), so what's now tested is the part this repo actually owns: that the
  MCP tool-call path doesn't crash when whatever it's orchestrating fails.
  `pystreammcp.testing` exports `RateLimitError`, `ContextWindowExceededError`,
  `MalformedModelResponseError`, and `FailingAgent`/`FailingAdapter` stand-ins
  that raise them; `mcp_server.py`'s `call_tool`/`process_message` now catch
  exceptions raised during tool execution and return a structured
  `{"status": "error", "error_type": ..., "message": ...}` response instead
  of propagating uncaught. See `tests/test_mcp_server_resilience.py`.
- ~~No Pydantic validation for the MCP tool protocol itself~~ **Fixed.**
  Each of the four MCP tools now has a Pydantic arg model
  (`QueryToolArgs`/`DiscoverToolArgs`/`RegisterSourceToolArgs`/`OptimizeToolArgs`
  in `mcp_server.py`) validated in `call_tool` before dispatch (wrong types,
  invalid enum values, and missing required fields all now return a
  structured `validation_errors` response instead of reaching the handler
  unchecked), and `MCPTool.input_schema` is generated from those same models
  via `model_json_schema()` — the advertised schema and the schema actually
  enforced can no longer drift apart the way a hand-duplicated dict could.
- ~~No shipped mock MCP server / mock LLM fixture~~ **Fixed.** Added
  `tests/conftest.py` (centralizing the `sys.path` setup 5 test files were
  duplicating, plus `mock_adapter`/`failing_agent`/`failing_adapter`/
  `llm_failure` pytest fixtures) and `pystreammcp/testing.py`, exporting
  `MockAdapter` (promoted from the old test-local copy) and the
  failure-injection stand-ins above for downstream projects' own test
  suites to import directly.
- **Per-query context discovery** now has a real implementation
  (`pystreammcp.discovery.SourceRegistry`): register data sources (name,
  description, type, tags), and `/discover` (REST), `pystreammcp_discover`
  (MCP), and `LangchainAdapter.discover()` all rank *registered* sources
  by real Jaccard token-overlap against the query — an empty registry or
  a non-matching context returns an empty list, not fabricated data. This
  is a simple word-overlap heuristic, not semantic/embedding search — if
  you need that, wrap `SourceRegistry` with your own similarity scoring.
- ~~The `pystreammcp` CLI is dead code~~ **Fixed.** `pyproject.toml` now
  has a `[project.scripts]` entry, and the module's `__main__` guard
  invokes the real Click group. See [Network defaults](#network-defaults)
  above and [`ROADMAP_HONEST.md`](ROADMAP_HONEST.md) §2.2.
- ~~Three orchestration-tool discovery adapters return fabricated
  results~~ **Fixed.** `orchestration/temporal.py`'s
  `TemporalDiscoveryActivity`/`TemporalWorkflow`, `airflow.py`'s
  `PyStreamMCPDiscoveryOperator`, and `nocode_rpa.py`'s
  `N8nWebhookTrigger` now take an optional shared `SourceRegistry` and
  call its real `discover()` instead of synthesizing `source_0..
  source_4`. With nothing registered they honestly return zero sources
  (see [`ROADMAP_HONEST.md`](ROADMAP_HONEST.md) §2.1).
- `pip-audit` (run 2026-09-20 against the `dev,api,mcp,langchain,
  llamaindex,semantic-kernel` extras) found 7 known CVEs in transitive
  dependencies (`werkzeug` via `flask`, `nltk` via `llama-index`) — see
  [`ROADMAP_HONEST.md`](ROADMAP_HONEST.md) §4. Not fixed this pass.
- No open GitHub issues as of this pass.

## Documentation

- [`ROADMAP_HONEST.md`](ROADMAP_HONEST.md) — full, unhedged status:
  what's tested, what's fabricated/broken, technical debt, what's
  explicitly not built.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — how the shipped
  package is structured, with a diagram.
- [`OKF_INTEGRATION.md`](OKF_INTEGRATION.md) — the OKF (Open Knowledge
  Format) catalog/discovery/query-planner feature (real, tested, not
  mentioned elsewhere in this README).
- [`CONTRIBUTING.md`](CONTRIBUTING.md), [`SECURITY.md`](SECURITY.md),
  [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md),
  [`CHANGELOG.md`](CHANGELOG.md).

## Rust workspace (not shipped)

`core/` and `python/src/lib.rs` are an in-progress Rust workspace intended
as a future performance backend. **It is not part of the published PyPI
package** — the wheel built from `pyproject.toml` is pure Python — and it
does not currently compile. Don't rely on it; it's tracked separately
from the Python package described in this README.

## License

This project is licensed under the [Apache License 2.0](LICENSE).
