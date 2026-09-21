# Changelog

All notable changes to PyStreamMCP will be documented in this file.

## [Unreleased]

### Fixed
- **Fabricated discovery data in three orchestration adapters**:
  `orchestration/temporal.py`'s `TemporalDiscoveryActivity`/
  `TemporalWorkflow`, `orchestration/airflow.py`'s
  `PyStreamMCPDiscoveryOperator`, and `orchestration/nocode_rpa.py`'s
  `N8nWebhookTrigger.handle_discovery` no longer synthesize
  `source_0..source_4` with fake relevance scores. Each now takes an
  optional shared `SourceRegistry` (same pattern already used by
  `LangchainAdapter`) and calls its real `discover()`; with nothing
  registered they honestly return zero sources instead of padding in
  fake ones. `tests/test_sprint5_orchestration.py` now asserts on real
  registered-source content (name/relevance), not just response shape,
  so this class of bug can't silently pass CI again.
- **`pystreammcp` CLI was unreachable dead code**: added a
  `[project.scripts]` entry (`pyproject.toml`) so `pip install
  PyStreamMCP` installs a real `pystreammcp` command; fixed `cli.py`'s
  `if __name__ == "__main__":` guard to invoke the actual Click group
  instead of a second, smaller, hand-rolled command set (which has been
  removed as genuinely dead code — no callers, no tests, no docs
  referenced it). `server`'s `pystreammcp.api` import is now lazy so
  `pystreammcp version`/`query`/`dashboard` work without the `api`
  extra installed, and `pystreammcp server` without it prints a clear
  install instruction instead of crashing with `ModuleNotFoundError`.
  Verified by installing into a clean venv and running `pystreammcp
  version`/`--help`/`query --json`/`dashboard --static` and `python -m
  pystreammcp.cli version` for real; added `tests/test_cli.py`.
- **`datetime.utcnow()` → `datetime.now(timezone.utc)`** in the 5
  production files where it was genuinely safe (verified no
  naive/aware comparison would break): `webhook_handlers.py` (29,
  pure `.isoformat()` serialization), `webhook_router.py` (7, including
  the `MCPEndpoint.last_heartbeat` field — checked it's never compared
  elsewhere), `quality.py` (4, `QualityCheck.checked_at` +
  `ValidationResult.last_validated` + the 3 staleness-check
  subtractions — migrated together since they interact; also updated
  `tests/test_statguardian_integration.py`'s `past_time` fixture to stay
  aware-consistent), `server.py` (2), `multi_agent.py` (1, also removed
  an `__import__("datetime")` workaround in favor of a normal import).
  Left two self-contained `datetime.utcnow()` calls in
  `tests/test_integration_phase2.py` untouched — they're internal to a
  test-local duplicate-detection helper, not tied to production code.
  `timezone.utc` used (not `datetime.UTC`) since `pyproject.toml`
  supports Python 3.9+ and the latter needs 3.11+.

### Changed
- Relicensed from Proprietary to Apache License 2.0 (`LICENSE`,
  `pyproject.toml`'s `license` field); `CONTRIBUTING.md` still said "MIT"
  at the bottom from an even earlier state — fixed to say Apache-2.0.
- `pyproject.toml` classifier downgraded from `Development Status :: 5 -
  Production/Stable` to `4 - Beta` — not honest given the known-broken
  CLI, fabricated orchestration-adapter discovery, and non-compiling Rust
  workspace documented in `ROADMAP_HONEST.md`.
- Replaced the broken `Dockerfile` (invalid `"""` comment syntax at the
  top, built the non-compiling Rust workspace via `maturin`, and its
  runtime `CMD` never actually started a server since `pystreammcp.api`
  has no `__main__` guard) with a working single-stage pure-Python image
  matching the real setuptools-based package.
- `.github/workflows/ci.yml`: bumped `actions/checkout` v4→v7 and
  `actions/setup-python` v4→v7 (flagged by `actionlint`); added
  non-blocking `lint` (ruff) and `security-audit` (pip-audit) jobs.
- Archived two actively-misleading docs to `docs/archive/`: root
  `ARCHITECTURE.md` (described the unshipped, non-compiling Rust
  workspace's cross-project integrations as real, closed with a
  fabricated "target met" metrics claim) and `docs/PRODUCT_VISION.md`
  (claimed a nonexistent "MCP 2.0 Platform", fixed port, and "Production
  Ready" status inconsistent with this repo). Replaced the previously
  content-free `docs/ARCHITECTURE.md` template with a real architecture
  doc.

### Added
- `ROADMAP_HONEST.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`,
  `.github/pull_request_template.md`.
- `!ROADMAP_HONEST.md` negation in `.gitignore` — its broad `ROADMAP_*`
  "don't expose internal strategy docs" pattern was silently matching
  this file too.

### Found, not fixed (see `ROADMAP_HONEST.md` for full detail)
- `pip-audit` found 7 known CVEs in transitive dependencies (`werkzeug`
  via the `api` extra's `flask`, `nltk` via `llama-index`), unpinned —
  left unpinned this pass; needs compatibility testing against the
  `flask>=2.3.0` floor before bumping.
- 910 remaining pre-existing `ruff` findings (was 951; the 41-finding
  drop is the `datetime.utcnow()` fixes above), not previously run in
  CI, out of scope for a mechanical quick-fix pass.
- Rust workspace confirmed to fail with 43 compile errors
  (`cargo build --workspace`); two Rust test files
  (`tests/metadata_filtering_tests.rs`, `tests/selective_retrieval_tests.rs`)
  contain zero assertions.

## [3.3.0] - 2026-08-25

### Added
- **Pydantic validation for the MCP tool protocol**: each of the four MCP
  tools (`pystreammcp_query`/`_discover`/`_register_source`/`_optimize`)
  now has a Pydantic arg model (`mcp_server.py`), validated in `call_tool`
  before dispatch. Wrong types, invalid enum values, and missing required
  fields now return a structured `validation_errors` response instead of
  reaching the handler unchecked (previously only `text`/`context`/
  `name`+`description` had manual `if not x` checks; `max_tokens`, `limit`,
  `strategy`, `intent`, `type`, `tags` had none). `MCPTool.input_schema` is
  now generated from those same models via `model_json_schema()`, so the
  advertised schema and the schema actually enforced can't drift apart.
- **Failure isolation in the MCP tool-call path**: `call_tool` and
  `process_message` now catch exceptions raised during tool execution
  (including from a real LLM/framework adapter wired in via the new
  `PyStreamMCPServer(agent=...)` constructor param) and return a
  structured `{"status": "error", "error_type": ..., "message": ...}`
  response instead of propagating uncaught.
- **`pystreammcp.testing`**: exports `MockAdapter` (promoted from the old
  test-local copy in `tests/test_sprint1_foundation.py`),
  `RateLimitError`/`ContextWindowExceededError`/`MalformedModelResponseError`,
  and `FailingAgent`/`FailingAdapter` failure-injection stand-ins, for
  downstream projects' own test suites.
- **`tests/conftest.py`**: centralizes the `sys.path` setup 5 test files
  were each duplicating, and exposes `mock_adapter`/`failing_agent`/
  `failing_adapter`/`llm_failure` pytest fixtures.

Closes the three gaps listed under "Known Issues" in the README as of
3.2.0: no Pydantic validation for the MCP tool protocol, no shipped mock
fixtures, no tests for LLM failure states. On that last one: PyStreamMCP's
own code never calls a model provider directly, so there's no
`except RateLimitError` call site to add here — what's now tested is that
the MCP tool dispatcher stays resilient when whatever it's orchestrating
fails, which is the part of that gap actually within this package's
boundary. See `tests/test_mcp_server_resilience.py`.

## [3.2.0] - 2026-08-16

### Fixed (Correctness & Security)
- **MCP tool handlers wired to the real Orchestrator**: `PyStreamMCPHandler`
  (`pystreammcp._mcp_tools`) previously ignored `self.orchestrator` entirely
  and returned hardcoded fixture data (a fake 7-project list, fixed
  "72% reduction", fake "5432 rows matched" cross-DB join results, etc.)
  for every one of its 17 tools. All handlers now call into the real,
  tested `Orchestrator`/`EventRouter` (federation discovery, lexical tool
  ranking, tool routing, webhook registration, workflow execution). Where
  a capability genuinely isn't implemented yet (federated query execution,
  cross-database joins), the response now says `"status": "not_implemented"`
  instead of fabricating a plausible-looking result.
- **Real HMAC-SHA256 auth on the webhook endpoint**: `POST
  /orchestration/webhooks/events` previously accepted any unsigned request
  despite the README claiming HMAC-SHA256 security. It now verifies an
  `X-PyStreamMCP-Signature: sha256=<hex>` header against a shared secret
  (`PYSTREAMMCP_WEBHOOK_SECRET`), rejects missing/invalid signatures with
  401, and fails closed (503) if no secret is configured at all.
- **CI now runs the real test suite**: the Python test job installed from
  `python/` (which has no `pyproject.toml`/`setup.py`) and looked for tests
  in `python/tests` (which doesn't exist) — every run silently no-op'd.
  Fixed to install from the repo root and run the actual `tests/` suite.
- **Version strings reconciled**: `Cargo.toml` (was 1.1.0), `setup.py`
  (was 1.1.0, MIT), and `python/pystreammcp/__init__.py` (was 3.0.0) now
  all match `pyproject.toml`'s 3.2.0 / Proprietary license.
- **Insecure network defaults removed**: HTTP/CLI servers now bind to
  `127.0.0.1` by default instead of `0.0.0.0`; the local MCP connector's
  generated config no longer defaults to wildcard CORS origins (`["*"]`)
  and wildcard `actions`/`roles` permissions.
- Fixed a name collision in `pystreammcp/__init__.py` where `QueryResult`
  (from `agent.py`) shadowed `adapters.QueryResult`, which every framework
  integration (LangChain, LlamaIndex, CrewAI, PydanticAI, Semantic Kernel,
  Haystack) imported expecting the adapters version — this broke nearly
  every integration test (`TypeError: unexpected keyword argument 'text'`).
- Fixed `Agent` missing `agent_id`/`name`/`optimization_strategy`/
  `max_tokens` properties (`AttributeError` from `api.py`'s `/agents` endpoints).
- Fixed `PromptClassifier._detect_domain` returning the first
  dict-order keyword match instead of the best-scoring domain (e.g.
  "patient treatment costs" incorrectly classified as "finance" instead
  of "healthcare").
- `Agent.query()` no longer returns a fixed 70%/50ms result regardless of
  input: token estimates now derive from the actual query text, the
  reduction target varies by `optimization_strategy`, and execution time
  is actually measured.
- Updated LangChain/LlamaIndex adapter imports to support current major
  versions of those libraries (`langchain_core`, `llama_index.core`) with
  fallback to legacy import paths.
- Fixed `AdapterRegistry` test-session pollution where
  `test_sprint1_foundation.py` permanently overwrote the real
  `LangchainAdapter` registration for the rest of the test run.

### Known limitations (documented, not fixed this release)
- The `core`/`python` Rust workspace does not currently compile and is
  **not part of the published PyPI package** (the wheel is pure Python).
  Its CI job is now non-blocking (`continue-on-error`) rather than
  silently masked.
- Cross-project federated query execution and cross-database joins are
  accepted at the API level but report `"not_implemented"` — there's no
  real execution engine behind them yet.

## [1.1.0] - 2026-07-22

### Added
- **Layer 1: Intent Understanding** - Intelligent query classification and entity extraction
  - IntentClassifier with 13 intent categories
  - EntityExtractor with pattern-based entity recognition
  - Urgency detection for token budget allocation
  - 16 comprehensive tests

- **Layer 2: Capability Registry** - Central registry of MCP servers and capabilities
  - MCPServerProfile with capability tagging and performance metadata
  - CapabilityRegistry with O(1) intent/capability lookups
  - CapabilityGraph for discovering related capabilities
  - 20+ comprehensive tests

- **Layer 3: Tool Selection & Ranking** - Intelligent tool selection and ranking
  - ToolSelector with primary/secondary/fallback categorization
  - ToolRanker with 6-factor scoring formula
  - PerformanceTracker with statistical aggregation
  - 25+ comprehensive tests

- **Foundation Modules** - Cohesive, strong architectural foundation
  - `error.rs`: Unified OrchestrationError with 10 error variants and rich context
  - `traits.rs`: 8 core traits + 3 trait compositions for shared semantics
  - `metrics.rs`: 7 semantic types for type-safe metrics (Score, Latency, Cost, etc.)
  - `validation.rs`: Comprehensive input validation framework
  - 25+ tests for foundation

### Architecture Improvements
- Unified error handling: All errors flow through OrchestrationError + Result<T>
- Shared abstractions: Trait-based design (Scoreable, Rankable, Confidence, etc.)
- Type safety: Semantic types prevent mixing incompatible metrics
- Input validation: All inputs validated at boundaries
- Extensibility: Trait-based composition enables new features

### Statistics
- Total: 3,890 LOC with 86+ tests
- Layers 1-3: 2,990 LOC with 61+ tests
- Foundation: 900 LOC with 25+ tests
- All tests passing

### Breaking Changes
None - fully backward compatible

### Documentation
- INTELLIGENT_RETRIEVAL_IMPLEMENTATION_PLAN.md - Detailed retrieval layer vision (18K words)
- MCP_ORCHESTRATION_HUB_DETAILED_PROMPT.md - Detailed orchestration layer vision (23K words)
- LAYERS_1_2_3_COMPLETE.md - Completion report for Layers 1-3
- ORCHESTRATION_REFACTORING_PLAN.md - Comprehensive refactoring guide
- COHESION_IMPROVEMENTS_SUMMARY.md - Foundation improvements summary
- ORCHESTRATION_IMPLEMENTATION_STATUS.md - Implementation status and examples

---

## [1.0.0] - 2026-07-21

### Added
- Initial stable release with query planning, discovery, and optimization
- Token budget enforcement
- Cost optimization strategies (6 techniques)
- Early termination for efficient context retrieval
- Basic latency/confidence constraints
- 58 unit tests + 65 integration tests
- OKF native support
- StatGuardian integration

[Unreleased]: https://github.com/Mullassery/PyStreamMCP/compare/v3.3.0...HEAD
[3.3.0]: https://github.com/Mullassery/PyStreamMCP/compare/v3.2.0...v3.3.0
[1.1.0]: https://github.com/Mullassery/PyStreamMCP/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Mullassery/PyStreamMCP/releases/tag/v1.0.0
