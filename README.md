# PyStreamMCP

[![CI](https://github.com/Mullassery/PyStreamMCP/actions/workflows/ci.yml/badge.svg)](https://github.com/Mullassery/PyStreamMCP/actions/workflows/ci.yml)

An AI-agent intelligence layer: query planning, context discovery, and
token-cost optimization, exposed both as a Python SDK and as an MCP
(Model Context Protocol) tool server, plus a small event-driven
orchestration/federation layer for coordinating multiple MCP endpoints.

Pure Python — `pip install` just works, no Rust toolchain or compiler
required.

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

The HTTP/CLI servers (`pystreammcp server`, `PyStreamMCPServer`,
`PyStreamMCPAPI.run`) bind to `127.0.0.1` (localhost-only) by default.
Pass `--host 0.0.0.0` (CLI) or `host="0.0.0.0"` explicitly if you need the
server reachable from other hosts — e.g. inside a container that already
has its own network boundary.

## Testing

```bash
pip install -e ".[dev,api,mcp,langchain,llamaindex,semantic-kernel]"
pytest tests/ -v
```

Note: this exact command needs Python 3.10+ (see [Install](#install)); on
3.9 the `mcp` and `semantic-kernel` extras fail to resolve, so drop them
from the extras list if you're on 3.9.

## Known Issues

- **No end-to-end tests for LLM failure states** (rate limits, context-window overruns, malformed model JSON) — no fixtures or tests simulate these; only happy-path unit tests exist, and there's no `except RateLimitError`/`APIError` handling anywhere in `python/pystreammcp/*.py`.
- **No Pydantic validation for the MCP tool protocol itself** — `mcp_server.py`'s `MCPTool.input_schema` is a raw `Dict[str, Any]`, and `call_tool`/`_tool_query` only do manual `if not text` checks, no schema validation. (Pydantic *is* used for the separate REST layer in `api.py` — this gap is specific to the MCP tool-call path.)
- **No shipped mock MCP server / mock LLM fixture** for downstream testing — no `conftest.py` exists; the only mock (`MockAdapter` in `tests/test_sprint1_foundation.py`) is test-local, not exported or reusable.
- **Per-query context discovery** now has a real implementation
  (`pystreammcp.discovery.SourceRegistry`): register data sources (name,
  description, type, tags), and `/discover` (REST), `pystreammcp_discover`
  (MCP), and `LangchainAdapter.discover()` all rank *registered* sources
  by real Jaccard token-overlap against the query — an empty registry or
  a non-matching context returns an empty list, not fabricated data. This
  is a simple word-overlap heuristic, not semantic/embedding search — if
  you need that, wrap `SourceRegistry` with your own similarity scoring.
- No open GitHub issues as of this pass.

## Rust workspace (not shipped)

`core/` and `python/src/lib.rs` are an in-progress Rust workspace intended
as a future performance backend. **It is not part of the published PyPI
package** — the wheel built from `pyproject.toml` is pure Python — and it
does not currently compile. Don't rely on it; it's tracked separately
from the Python package described in this README.

## License

Proprietary License — Free to use with explicit attribution. See
[LICENSE](LICENSE).
