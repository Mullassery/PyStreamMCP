# PyStreamMCP

[![PyPI](https://img.shields.io/pypi/v/pystreammcp)](https://pypi.org/project/pystreammcp/)
[![CI](https://github.com/Mullassery/PyStreamMCP/actions/workflows/ci.yml/badge.svg)](https://github.com/Mullassery/PyStreamMCP/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](./LICENSE)

Context and token optimization for AI agents — query planning, source discovery, and MCP orchestration.

## What it is

PyStreamMCP is an AI-agent intelligence layer: query planning, context discovery, and
token-cost optimization, exposed both as a Python SDK and as an MCP (Model Context
Protocol) tool server. It also includes a small event-driven orchestration/federation
layer for coordinating multiple MCP endpoints. The published package is **pure Python** —
`pip install` works with no Rust toolchain or compiler.

## Features / Highlights

- **Agent query planning** — `pystreammcp.Agent` with selectable optimization strategies
  (`token_efficient`, `balanced`, `quality_first`) and token accounting.
- **Source discovery** — `SourceRegistry` ranks registered data sources by real
  word-overlap relevance (Jaccard) to a query; backs REST `/discover`, the
  `pystreammcp_discover` MCP tool, and `LangchainAdapter.discover()`.
- **MCP tool server** — `PyStreamMCPHandler` wires the MCP tool-call surface directly to a
  live `Orchestrator`/`EventRouter`; MCP tool args are validated with Pydantic and the
  advertised schema is generated from the same models.
- **MCP orchestration & federation** — `Orchestrator` probes each configured endpoint's
  real `tools/list` MCP method, with lexical tool-relevance ranking and capability
  matching.
- **Webhook event server** — `pystreammcp.server.create_flask_app()` exposes an
  HMAC-SHA256-signed event endpoint; unsigned or invalid events are rejected, and the
  endpoint fails closed (`503`) if no secret is configured.
- **Framework adapters** — LangChain, LlamaIndex, CrewAI, Semantic Kernel, PydanticAI,
  and Haystack under `pystreammcp.integrations`.
- **CLI** — `pystreammcp` with `query` / `server` / `version` / `dashboard`.
- **OKF integration** — an Open Knowledge Format catalog/discovery/query-planner feature
  (see [`OKF_INTEGRATION.md`](OKF_INTEGRATION.md)).

## Who it's for / Use cases

- **Giving an AI agent a query-planning layer over multiple data sources**, exposed as
  real MCP tools rather than hand-rolled per-agent glue code.
- **Coordinating multiple MCP endpoints** through the event-driven
  orchestration/federation layer instead of wiring each one separately.
- **Tracking token-cost optimization** across agent queries.
- **Adding MCP support to an existing agent framework** through the shipped adapters.

## What it is not

- **The Rust backend is not shipped.** `core/` and `python/src/lib.rs` are an in-progress
  Rust workspace intended as a future performance backend; the wheel built from
  `pyproject.toml` is pure Python. The workspace compiles and its tests pass, but it is
  tracked separately and not part of the published package.
- **Some orchestration capabilities are not fully implemented.** Cross-project federated
  query *execution* and cross-database joins currently report
  `"status": "not_implemented"` with an explanation, rather than fabricated result rows.
- **Source discovery is a word-overlap heuristic, not semantic search.**
  `SourceRegistry` uses Jaccard token overlap; wrap it with your own similarity scoring if
  you need embeddings.
- **Optional concurrency/framework packages have Python constraints.** The core SDK
  (`Agent`, `SourceRegistry`, `Orchestrator`) supports Python 3.9+, but the `mcp` and
  `semantic-kernel` extras require Python 3.10+ (their upstream packages don't publish
  3.9-compatible releases). CI tests 3.10, 3.11, and 3.12 only.
- **Known dependency CVEs.** `pip-audit` (run 2026-09-20) found 7 known CVEs in
  transitive dependencies (`werkzeug` via `flask`, `nltk` via `llama-index`). See
  [`ROADMAP_HONEST.md`](ROADMAP_HONEST.md) §4.
- **The HTTP servers have no auth layer of their own.** They bind to `127.0.0.1`
  (localhost-only) by default; pass `host="0.0.0.0"` explicitly only inside a network
  boundary you control. The event endpoint requires HMAC-SHA256 signatures. See
  [SECURITY.md](SECURITY.md).

## Project status

**Beta.** Current version **3.3.1** (`Development Status :: 4 - Beta`). The pure-Python
package is the shipped artifact and is under active hardening; the Rust workspace compiles
and passes its tests but is not shipped. The most recent pass fixed the Rust build,
Python `ruff` findings, and a stale integration test — see
[`ROADMAP_HONEST.md`](ROADMAP_HONEST.md) for the unhedged status.

## Installation

```bash
pip install PyStreamMCP
```

Optional extras — install only what you need:

```bash
pip install "PyStreamMCP[api]"              # FastAPI + Flask HTTP servers
pip install "PyStreamMCP[mcp]"              # MCP protocol client library
pip install "PyStreamMCP[langchain]"        # LangChain adapter
pip install "PyStreamMCP[llamaindex]"       # LlamaIndex adapter
pip install "PyStreamMCP[semantic-kernel]"  # Semantic Kernel adapter
pip install "PyStreamMCP[all-integrations]" # every framework adapter
```

Requires Python 3.9+ for the core SDK; the `mcp` and `semantic-kernel` extras require
Python 3.10+.

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

Token counts are estimated from the actual query text (a ~4-characters-per-token
heuristic) and the reduction is computed from the selected strategy — not a fixed number.
See [`examples/basic_usage.py`](examples/basic_usage.py) for a full walkthrough.

## Usage

**Data source discovery:**

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

**MCP orchestration & federation** (`pystreammcp.toml`):

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
```

**Webhook event server (HMAC-SHA256):**

```bash
export PYSTREAMMCP_WEBHOOK_SECRET="a long random shared secret"
```

Senders compute `HMAC-SHA256(secret, raw_request_body)` and send it as
`X-PyStreamMCP-Signature: sha256=<hex digest>`. Requests with a missing or invalid
signature are rejected with `401`; with no secret configured, the endpoint rejects every
request with `503`.

**Testing:**

```bash
pip install -e ".[dev,api,mcp,langchain,llamaindex,semantic-kernel]"
pytest tests/ -v
```

## Documentation

- [`ROADMAP_HONEST.md`](ROADMAP_HONEST.md) — full, unhedged status: what's tested, what's fabricated/broken, technical debt, what's explicitly not built
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — how the shipped package is structured, with a diagram
- [`OKF_INTEGRATION.md`](OKF_INTEGRATION.md) — the OKF catalog/discovery/query-planner feature
- [`CHANGELOG.md`](CHANGELOG.md) — release history
- [`examples/`](examples/) — runnable examples, including framework integrations and the MCP orchestrator

## Known issues and deferred work

**Blocked / failed:**
- Semantic retrieval/Graphify integration and MCP hardening.

**Rejected / deferred:**
- The Rust backend; not shipped.

Full shipped/blocked/rejected detail: [`QUEUE_STATUS.md`](QUEUE_STATUS.md).

## Queue status

Shipped, blocked/failed, and rejected work for this repository is documented in
[`QUEUE_STATUS.md`](QUEUE_STATUS.md).

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) and
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Report security issues per
[SECURITY.md](SECURITY.md).

## Related projects

- [PyStreamXL](https://github.com/Mullassery/PyStreamXL) — stream large Excel workbooks with constant memory
- [PyStreamPDF](https://github.com/Mullassery/PyStreamPDF) — token-efficient PDF extraction for RAG
- [PyStreamMCP](https://github.com/Mullassery/PyStreamMCP) — context and token optimization for AI agents
- [PyStreamAI](https://github.com/Mullassery/PyStreamAI) — ML deployment toolkit (canary/A-B, cost tracking, ONNX)
- [PyTokenCalc](https://github.com/Mullassery/PyTokenCalc) — LLM token counting and cost estimation
- [Browse all projects](https://github.com/Mullassery?tab=repositories)

## License

This project is licensed under the [Apache License 2.0](LICENSE).
