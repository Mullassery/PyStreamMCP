# Competitive intelligence in roadmap and upgrade work

**Policy date:** 2026-10-19

Competitive findings are an input to product decisions, not a one-off report.
Every pending roadmap item, new feature, and routine dependency upgrade should
check the repository's [`AUDIT_FINDINGS.md`](AUDIT_FINDINGS.md) before work
starts, and record the decision in the PR or changelog.

## Required check before building

1. **Read `AUDIT_FINDINGS.md`.** Find the relevant competitor row and the
   ranked next actions. If the finding is stale, update it with a dated source.
2. **Name the competitor and the user problem.** A feature is not justified by
   "competitor has it". State the workflow it unlocks, who needs it, and how
   often. Mark unverified demand as a hypothesis.
3. **Prefer reuse over new code.** Check whether an existing Mullassery repo
   already provides the capability (see `BUNDLES.md` in the profile repo and
   the bundle role file in this repo, when present). Typical reuse:
   - crawling/fetching/robots/SSRF → **MudFish**
   - architecture maps / PR diffs → **CodeAtlas**
   - data-quality contracts / validation → **StatGuardian**
   - token counting / cost tables → **PyTokenCalc**
   - dependency graph / advisories / SBOM → **PyDeepMesh**
   - segmentation / CLV / churn → **ClusterAudienceKit**
   - activation / lineage / PII → **PyReverseETL**
   - fleet state sync → **SyncFleet** (only after conflict resolution)
4. **Choose one disposition:** build, integrate, defer, or reject. Write it
   down. A rejection with a reason is a successful outcome.
5. **For routine upgrades**, check whether the upgrade closes a known
   competitor gap or breaks a differentiated capability. Run the tests that
   cover the affected path; do not merge a green build that silently changes a
   user-visible contract.

## PR / changelog checklist

- [ ] Competitor and source URL/date recorded (or "no direct competitor").
- [ ] User impact and frequency stated; unverified demand labelled.
- [ ] Reuse check done against sibling repos/bundles.
- [ ] Failure mode and rollback considered (especially auth, PII, cost).
- [ ] Docs/roadmap status updated honestly.
- [ ] Tests or a manual verification command included.

## Review cadence

- Refresh the competitor row when a release changes the capability.
- Re-check the full `AUDIT_FINDINGS.md` at least quarterly and before a major
  release.
- If a finding is wrong or stale, correct it in the same PR that relies on it.

## Non-goals

- Copying features for parity.
- Adding a dependency just because a competitor uses it.
- Treating star counts or download counts as proof of user need.

## OSS gap analysis — 2026-10-24

**What matters most here:** be an actual MCP server, and measure token savings. A bespoke envelope with no stdio/SSE/HTTP binding cannot be used by Claude Desktop or Cursor, and `len//4` arithmetic is not context optimization; fix the protocol and benchmark real assembly.

Scope: Compared PyStreamMCP's shipped pure-Python SDK/MCP tool surface against four actively maintained MCP frameworks and gateways, focusing on wire compatibility, transport/auth, federation, and token-cost handling.

### Comparable OSS projects
| Project | GitHub | License | Last activity | Why it is the comparison |
| --- | --- | --- | --- | --- |
| FastMCP | https://github.com/PrefectHQ/fastmcp | Apache-2.0 | v4.1.3, 2026-10-20 | Reference Python MCP server framework; same job as our MCP tool server |
| mcp-use | https://github.com/mcp-use/mcp-use | MIT | client v2.4.4, 2026-10-17 | Multi-server MCP client + agent layer; competes with our orchestration |
| Context7 | https://github.com/upstash/context7 | MIT | ctx7@0.8.2 / mcp 4.4.4, 2026-10-23 | Doc-retrieval MCP server with query resolution; competes with discovery/planning |
| mcp-proxy | https://github.com/TBXark/mcp-proxy | MIT | v1.1.0, 2026-09-15 | Aggregates many MCP servers behind one HTTP endpoint; competes with federation |

### Capability comparison
| Capability | Ours | FastMCP | mcp-use | Context7 | mcp-proxy | Gap |
| --- | --- | --- | --- | --- | --- | --- |
| MCP spec wire protocol (JSON-RPC) | No | Yes | Yes | Yes | Yes | Critical |
| stdio / SSE / streamable HTTP server | No | Yes | Yes | Yes | Yes | Critical |
| MCP client across many servers | Partial | Partial | Yes | No | Yes | Moderate |
| OAuth / scoped auth | Partial | Yes | Yes | Yes | Yes | Moderate |
| Tool discovery and ranking | Yes | Partial | Partial | Partial | No | Ahead |
| Semantic retrieval | No | No | No | Partial | No | Moderate |
| Token-budget optimization | Partial | No | No | Partial | No | Narrow lead |
| Cross-source SQL federation | Partial | No | No | No | No | Ahead |
| Framework adapters | Yes | Partial | Yes | No | No | Ahead |
| Published releases/benchmarks | Partial | Yes | Yes | Yes | Yes | Moderate |

Nuance: "Ours" is the pure-Python package only. `mcp_server.py` dispatches a custom `{"type": "call_tool"}` message, not JSON-RPC 2.0, so a stock MCP client cannot connect without an adapter. Tool *semantics* (list/call, Pydantic schemas) are real; the *transport* is not. `Orchestrator` does issue real JSON-RPC `tools/list` probes, so we are a client of the protocol but not a compliant server. Context7's semantic retrieval runs in a private backend, not this repo, hence "Partial". Cross-source federation is real but limited to SQLite/Parquet/CSV via DuckDB + SQLGlot.

### Gaps that matter (ranked)
1. **Not a spec-compliant MCP server** — `mcp_server.py` uses a bespoke message envelope and ships no stdio/SSE/streamable-HTTP binding; users cannot point Claude Desktop, Cursor, or Inspector at it. This is the difference between "an SDK" and "an MCP server", and it blocks the primary distribution path every comparable has. Effort M.
2. **Token optimization is arithmetic, not context assembly** — `Agent.query()` computes `baseline_tokens` from `len(text)//4` and a per-strategy reduction constant; no chunking, reranking, eviction, or measured output. The 60–75% claim is therefore a formula, not an observed saving, and an evaluator comparing against Context7 will notice immediately. Effort M/L.
3. **Federation discovers but barely executes** — discovery probes `tools/list`, yet cross-server query execution, retry/circuit-breaking per endpoint, and non-SQL source routing are absent; joins cover only SQLite/Parquet/CSV. mcp-proxy already does aggregation with OAuth token custody. Effort M.
4. **Auth is one shared static key** — `PYSTREAMMCP_API_KEY` plus HMAC webhooks, no OAuth resource metadata, no per-tool scopes, no token refresh. Every listed competitor ships OAuth in 2026. Effort M.
5. **Discovery is Jaccard only** — `SourceRegistry` cannot use embeddings or hybrid scoring, so it degrades on paraphrase and multilingual queries where Context7-style resolution works. Effort M.
6. **No published benchmark or release artifact** — no reproducible token-savings benchmark and no GitHub release; competitors publish versioned releases and changelogs weekly. Effort S.

### Where we are differentiated
- Federated read-only SQL joins across SQLite/Parquet/CSV with SQLGlot transpilation and row bounds — none of the four comparables plans or executes cross-source queries.
- Query planning + token accounting + source discovery in one importable SDK, not just a server; usable inside an existing agent loop.
- Shipped, tested LangChain/LlamaIndex/Semantic Kernel adapters, which FastMCP and mcp-proxy do not provide.
- Fail-closed HMAC webhooks and explicit `not_implemented` responses instead of fabricated rows — a trust advantage for data teams.

### Disposition
- **Build:** a spec-compliant server transport (prefer mounting the official `mcp` SDK or FastMCP) and replace the arithmetic savings estimate with measured before/after context assembly.
- **Integrate/reuse:** FastMCP for server transport/auth; mcp-use or mcp-proxy for multi-server aggregation and OAuth token custody rather than reimplementing.
- **Defer/reject:** semantic/embedding retrieval and the Rust backend; keep federation execution scoped to SQL sources.

### Sources
- https://github.com/PrefectHQ/fastmcp (accessed 2026-10-24)
- https://github.com/PrefectHQ/fastmcp/releases/tag/v4.1.0 (accessed 2026-10-24)
- https://github.com/mcp-use/mcp-use (accessed 2026-10-24)
- https://github.com/upstash/context7 (accessed 2026-10-24)
- https://github.com/TBXark/mcp-proxy (accessed 2026-10-24)
- Repo files inspected: `README.md`, `COMPETITIVE_INTELLIGENCE.md`, `AUDIT_FINDINGS.md`, `docs/ARCHITECTURE.md`, `pyproject.toml`, `Cargo.toml`, `python/pystreammcp/mcp_server.py`, `python/pystreammcp/agent.py`, `python/pystreammcp/_mcp_connector.py`
