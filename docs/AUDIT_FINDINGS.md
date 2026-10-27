# Audit Report: PyStreamMCP

**Audit Date:** 2026-10-26  
**Repository Path:** `/Users/georgimullassery/Desktop/Projects/PyStreamMCP`  
**Audit Type:** Read-only systems design audit  
**Version:** 3.3.5 (published Python package); Cargo workspace 3.3.1; FastAPI default 0.2.0; legacy health response 2.0.0  
**Branch:** `main`  
**Working Tree:** Uncommitted `?? docs/superpowers/`; no repository files were modified  
**Source Size:** ~13,383 Python package LOC, ~13,105 Rust workspace LOC, 405 static Python tests, 321 static Rust tests

## Executive Summary

PyStreamMCP is a pure-Python agent intelligence layer with three real surfaces over shared core objects: `Agent` query/token planning, `SourceRegistry` lexical source discovery, and `Orchestrator` MCP endpoint federation. It also ships HMAC-authenticated webhook ingestion, Flask/FastAPI servers with API-key or loopback-only access, framework adapters, an OKF catalog/planner, and optional DuckDB/SQLGlot federated read-only execution.

The shipped Python package is materially real. The major weaknesses are truth and scope: four different version strings exist; the Rust workspace is unshipped and docs disagree on whether it compiles; token "savings" are heuristic estimates, not measured end-to-end outcomes; source and tool relevance are Jaccard/lexical rather than semantic; several orchestration tools return `not_implemented` or accept parameters they ignore; and the two server factories are minimal in-memory apps. The repository is best treated as a beta MCP orchestration toolkit with honest limitations, not a production MCP gateway.

## Purpose and Positioning

- **What it is:** query planning, token-cost estimation, source discovery, MCP endpoint orchestration, webhook event routing, and optional federated read-only queries.
- **Who it is for:** agent builders who want a Python SDK plus MCP/REST surfaces over multiple data sources and MCP endpoints.
- **What it is not:** an LLM, a semantic search engine, a durable workflow engine, a production API gateway, or a shipped Rust backend.
- **Differentiator:** one shared Python core exposed through SDK, REST/Flask, MCP tools, and framework adapters, with explicit `not_implemented` responses instead of fabricated data.

## Architecture

```text
Surfaces
  Python SDK (Agent, SourceRegistry, Orchestrator)
  FastAPI (api.py) and Flask webhook server (server.py)
  MCP server (mcp_server.py) + orchestration handler (_mcp_tools.py)
  CLI (query/server/version/dashboard)
  Framework adapters (LangChain, LlamaIndex, Semantic Kernel; experimental others)
        |
        v
Core
  Agent: query plan + token estimate + strategy
  SourceRegistry: Jaccard word-overlap discovery
  Orchestrator / EventRouter / ServiceRegistry / FallbackManager
  OKF catalog/discovery/query planner
  FederatedQueryEngine (optional DuckDB + SQLGlot)
  Webhook HMAC verification
        |
        v
State
  In-memory agents, sources, endpoint registry, caches, webhook configs
  Optional SQLite/Parquet/CSV sources via DuckDB (read-only)
```

### Rust workspace

- Root `core/` + `python/src` is a separate performance-backend experiment.
- It is not part of the wheel built by `pyproject.toml` (setuptools, pure Python).
- README says the workspace compiles and tests pass; `docs/ARCHITECTURE.md` still says it is "currently-non-compiling." This contradiction is unresolved.
- Internal roadmap documents 43 historical compile errors and a decision to defer the backend.
- `Cargo.toml` version 3.3.1 does not match the Python package 3.3.5.

## Repository Layout

```text
python/pystreammcp/          shipped pure-Python package
  agent.py, discovery.py, context.py, optimization/
  api.py, server.py, mcp_server.py, _mcp_tools.py
  _mcp_connector.py, federation.py, webhook_router.py
  okf_*.py, integrations/, orchestration/, observability/
core/                        unshipped Rust workspace
python/src/lib.rs            unshipped PyO3 experiment
tests/                       Python suite
docs/                        architecture, roadmap, queue, archived aspirational docs
.github/workflows/ci.yml     Python tests/lint/build
```

## Technology Stack and Dependencies

- **Python 3.9+ core:** standard library; Pydantic for tool schemas.
- **Extras:** FastAPI/Flask (`api`), MCP client (`mcp`, 3.10+), LangChain, LlamaIndex, Semantic Kernel, DuckDB/SQLGlot (`federation`), all integrations.
- **Entry point:** `pystreammcp` Click CLI.
- **Packaging:** setuptools, pure-Python wheel.
- **Testing:** pytest; Python 3.10–3.12 in CI.
- **Unshipped Rust:** PyO3/Tokio workspace.

## Public Surface

### SDK

- `Agent`: `query`, optimization strategies, token counters, metrics.
- `SourceRegistry`: `register`, `discover`, list/get.
- `Orchestrator`: endpoint discovery/health/tool routing/webhook/cache/retry.
- `FederatedQueryEngine`: read-only SQLite/Parquet/CSV joins.
- OKF: catalog, discovery, query planner.
- Framework adapters.

### HTTP

- FastAPI: `/health`, `/info`, agents CRUD, query, discovery, source registration, optimization.
- Flask: webhook event endpoint + status/reporting routes.
- Non-health routes require `PYSTREAMMCP_API_KEY`; if unset, only loopback is accepted.
- Webhook endpoint additionally requires `PYSTREAMMCP_WEBHOOK_SECRET` and `X-PyStreamMCP-Signature`; fails closed `503` without a secret.

### MCP

- `mcp_server.py`: five tools (`pystreammcp_query`, `_discover`, `_register_source`, `_optimize`, `_crawl`) with Pydantic schemas and optional token enforcement.
- `_mcp_tools.py`: 18 orchestration tools advertised; many delegate to real orchestrator state, while some are explicitly partial.
- `call_tool` authenticates with `PYSTREAMMCP_API_KEY` only if it is set; otherwise unauthenticated.

### CLI

- `pystreammcp query|server|version|dashboard`.

## Design Patterns

- **Shared core across surfaces:** REST, MCP, SDK, and adapters call the same objects.
- **Pydantic schemas as source of truth:** MCP input schemas are generated from arg models.
- **Explicit not-implemented reporting:** federation/join paths return a structured explanation when no engine is configured.
- **Fail-closed webhooks:** HMAC over the raw body, constant-time compare, no unsigned fallback.
- **Loopback-only fallback auth:** if no API key is set, non-loopback clients are rejected.
- **Lexical relevance:** Jaccard word overlap for sources; name/description overlap for tools.
- **In-memory orchestration:** endpoints, sources, agents, caches, and fallbacks are process-local.
- **Experimental gating:** unsupported adapters raise unless explicitly enabled.
- **Optional backend:** DuckDB/SQLGlot loaded only when federation is used.

## Data and Storage

- **Agents/sources/endpoints/webhooks/caches:** in-memory Python structures.
- **No database owned by the package.**
- **Federation:** DuckDB in-memory connection attaches SQLite read-only; Parquet/CSV via views; row limit default 1000.
- **OKF:** markdown/git-trackable catalog files.
- **Webhook configs:** in-memory; deleted on restart.
- **No durable event queue, audit log, or session store.**
- **No multi-process coordination.**

This is appropriate for a local agent toolkit, not for multi-replica deployment.

## Concurrency and Performance

- FastAPI async routes; Flask/WSGI for webhook.
- Orchestrator endpoint probes use network I/O; timeout/retry behavior is not uniform across tools.
- Federated execution is synchronous and bounded by a row limit.
- `Agent.query` token counts are character-based estimates (~4 chars/token), not tokenizer-based.
- No committed benchmark for the advertised "60–75% token reduction."
- In-memory caches are global and not partitioned by `scope`.
- No connection pooling for federated sources beyond DuckDB's internal behavior.
- MCP server tool execution is synchronous inside `call_tool`.
- No multi-server reliability/load test.

## Security and Privacy

### Strengths

- HMAC-SHA256 webhook verification over raw body with constant-time comparison and fail-closed missing-secret behavior.
- API key comparison uses `hmac.compare_digest`.
- No API key -> non-loopback requests rejected (401/403).
- Servers bind `127.0.0.1` by default.
- MCP `call_tool` enforces the API key when set.
- DuckDB federation is read-only for SQLite and bounded by row limit.
- Source aliases are validated; table identifiers are quoted; join expressions are caller-supplied but execution is read-only.
- Experimental integrations are gated.
- SECURITY.md is candid about CVEs and no SLA.

### Gaps

- **Public read/write when no API key is set and behind a loopback-trusting proxy:** `remote_addr` loopback trust can be wrong behind reverse proxies unless deployment preserves peer address.
- **MCP transport is unauthenticated if no API key:** README says put it behind the MCP host's auth.
- **Webhook secret is process env/config only:** no key rotation or replay protection (HMAC authenticates, but no timestamp/nonce).
- **Unverified transitive CVEs:** `werkzeug` via Flask and `nltk` via LlamaIndex, per README/SECURITY/roadmap.
- **No rate limiting** on HTTP/MCP endpoints was verified.
- **No TLS listener:** expects a gateway.
- **Webhook SSRF:** outbound webhook URL registration is caller-controlled; no destination allowlisting was verified.
- **Federated SQL accepts caller join expressions and columns:** read-only but can still be expensive or access any attached source.
- **In-memory state can leak across tenants** if one process serves multiple users.
- **API key and webhook secret in environment** are visible to same-user processes.
- **Experimental vendor-named modules** can be mistaken for real integrations.

## Reliability and Observability

- Structured error responses from MCP tool execution; Pydantic validation errors are returned, not raised.
- Orchestrator records endpoint health and delivery metrics.
- Webhook event router tracks services/tool chains/fallbacks.
- Observability module exists with metrics helpers.
- No durable state or replay.
- No distributed tracing or request IDs across surfaces.
- No backoff/timeout standard across all federation probes.
- No dead-letter for webhook events.
- No readiness dependency checks.
- Some tools accept parameters they ignore (`weight_by_speed`, `weight_by_accuracy`, `time_window_hours`, cache `scope`).
- Tests cover resilience for MCP tool failures.

## Testing, CI, and Quality

- 405 static Python test definitions; 321 static Rust tests.
- Internal architecture says 375 passed; roadmap says 383 passed; 2026-10-19 audit says 27 tests (stale). These are unreconciled.
- CI tests Python 3.10–3.12; README says core supports 3.9, extras require 3.10.
- Tests cover Agent, discovery, webhooks, MCP handler/server, federation, adapters, OKF, CLI, and resilience.
- No benchmark for token savings.
- No multi-server federation/reliability test.
- No live vendor-SDK tests for experimental integrations (by design).
- `ruff` history shows a large finding count; earlier passes reduced it, but lint coverage should be verified in CI.
- No coverage gate.
- No end-to-end test with real MCP hosts or real external endpoints.
- Rust workspace tests are not part of the shipped artifact and may not be run by CI.

## Documentation, Packaging, and Release

- Version drift: package 3.3.5, Cargo 3.3.1, FastAPI 0.2.0, health JSON 2.0.0.
- Architecture doc contradicts README on whether the Rust workspace compiles.
- README correctly retracts old "MCP 2.0 / 18 projects / production ready" claims; archived docs preserve them.
- README candidly documents heuristic token savings, lexical discovery, unsupported integrations, CVEs, and unshipped Rust.
- `Development Status :: 4 - Beta` is appropriate.
- Pure-Python wheel is the shipped artifact.
- No GitHub release/tag verified.
- Docs are extensive but fragmented; `QUEUE_STATUS.md` is the clearest shipped/blocked view.

## Strengths

- Real shared core across SDK/REST/MCP, not duplicated fixtures.
- Strong webhook HMAC design and fail-closed behavior.
- API-key or loopback-only HTTP auth across both server factories.
- Honest `not_implemented` responses and explicit experimental gating.
- Optional read-only DuckDB/SQLGlot federation is a real capability.
- Pydantic-generated MCP schemas and structured validation errors.
- Candid security and roadmap documentation.
- Broad test suite with resilience coverage.

## Risks and Gaps

| Risk | Severity | Evidence | Impact |
|---|---|---|---|
| Version drift across four values | Medium | package/Cargo/FastAPI/health | Wrong diagnostics, support confusion. |
| Rust workspace status contradiction | Medium | README vs ARCHITECTURE vs roadmap | Users may try an unshipped/non-working backend. |
| Token-savings claim unbenchmarked | High credibility | README heuristic; no benchmark | Users may expect real 60–75% savings. |
| Discovery is lexical, not semantic | Medium | `SourceRegistry` Jaccard; tool overlap | Poor results on paraphrased queries. |
| MCP auth optional if key unset | Medium/High | `call_tool` conditional | Unauthenticated tool access if exposed. |
| Webhook no replay protection | Medium | HMAC only | Captured signed requests can be replayed. |
| Outbound webhook SSRF/allowlist absent | Medium | caller-controlled URL | Server-side requests to internal targets. |
| In-memory state/no durable queue | Medium | Orchestrator/EventRouter | Restart loses endpoints, webhooks, agents, events. |
| Ignored parameters | Low/Medium | weights, time window, cache scope | API suggests behavior that does not exist. |
| Transitive CVEs | Medium | werkzeug/nltk via extras | Known vulnerable dependencies. |
| No rate limiting/TLS | Medium | server code | Resource abuse if exposed; needs gateway. |
| Four-way test-count drift | Medium | 27/375/383/405 | Release confidence unclear. |

## Prioritized Recommendations

### P0 - exposure safety

1. Require `PYSTREAMMCP_API_KEY` for non-loopback binds at startup.
2. Add webhook timestamp/nonce replay protection and an outbound destination allowlist.
3. Pin or upgrade `werkzeug`/`nltk` and run `pip-audit` in CI.
4. Add rate limiting to HTTP and MCP surfaces.

### P1 - truth and correctness

5. Unify versions and decide the Rust workspace's fate: ship, archive, or delete.
6. Reconcile test counts into one verified result.
7. Replace heuristic token-savings claims with a committed benchmark or label them "estimated."
8. Implement or remove ignored parameters; keep `not_implemented` explicit.
9. Add semantic/embedding discovery as an opt-in backend.

### P2 - operations

10. Add durable state or document single-process, ephemeral behavior.
11. Add tracing/request IDs across SDK/REST/MCP/federation.
12. Add multi-server federation and load tests.
13. Add TLS or document a mandatory reverse proxy.
14. Clarify that experimental vendor-named modules are not real integrations.

## Evidence Appendix

- `README.md` - 3.3.5, pure-Python wheel, lexical discovery, HMAC webhooks, auth model, CVEs, unshipped Rust.
- `SECURITY.md` - webhook fail-closed, loopback default, transitive CVEs.
- `docs/ARCHITECTURE.md` - shipped package design; says Rust workspace currently non-compiling.
- `docs/internal/ROADMAP_HONEST.md` - 383 passing tests, 951 ruff findings, Rust 43 errors, historical fixes.
- `docs/internal/QUEUE_STATUS.md` - federation and auth shipped; semantic retrieval blocked; Rust rejected/deferred.
- `docs/internal/AUDIT_FINDINGS.md` - stale 27-test claim; lexical discovery; no benchmark.
- `python/pystreammcp/auth.py` - API key/loopback logic.
- `python/pystreammcp/api.py` - FastAPI auth middleware, 0.2.0, endpoints.
- `python/pystreammcp/server.py` - Flask webhook HMAC, 2.0.0 health, loopback default.
- `python/pystreammcp/mcp_server.py` - five MCP tools, Pydantic validation, auth, resilience.
- `python/pystreammcp/_mcp_tools.py` - 18 orchestration tools, explicit partials.
- `python/pystreammcp/federation.py` - read-only DuckDB/SQLGlot joins, row limit.
- `pyproject.toml`, `Cargo.toml`, `__init__.py` - version drift.
- 405 Python / 321 Rust static test definitions.

## Audit Limitations

- Static audit only; no server, MCP host, webhook, federation, or adapter was executed.
- Test counts are static; pass/fail claims were not rerun.
- Rust workspace build status could not be reconciled from docs; it was not built due the no-modification constraint.
- No dynamic security, load, fuzz, or multi-server testing.
- PyPI and CI state were not independently verified.
- `docs/superpowers/` was left untouched.
