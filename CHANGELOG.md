# Changelog

All notable changes to PyStreamMCP will be documented in this file.

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

[Unreleased]: https://github.com/Mullassery/PyStreamMCP/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/Mullassery/PyStreamMCP/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Mullassery/PyStreamMCP/releases/tag/v1.0.0
