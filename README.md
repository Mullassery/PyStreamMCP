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

Requires Python 3.9+.

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

## Rust workspace (not shipped)

`core/` and `python/src/lib.rs` are an in-progress Rust workspace intended
as a future performance backend. **It is not part of the published PyPI
package** — the wheel built from `pyproject.toml` is pure Python — and it
does not currently compile. Don't rely on it; it's tracked separately
from the Python package described in this README.

## License

Proprietary License — Free to use with explicit attribution. See
[LICENSE](LICENSE).
