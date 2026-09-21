# PyStreamMCP — Honest Status & Roadmap

Last verified: 2026-09-22, against commit `7bbda43` + this pass's changes
(quick-fix pass: fabricated orchestration-adapter discovery, dead CLI
entry point, `datetime.utcnow()` migration where safe). Every claim below
was checked against the actual code/tests in this repo, not against what
a doc says. See [`README.md`](README.md) for the user-facing quickstart
and [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for how the shipped
package is structured.

## 1. What works (tested by me, this pass)

- `pytest tests/ -v --tb=short` on Python 3.11 with
  `pip install -e ".[dev,api,mcp,langchain,llamaindex,semantic-kernel]"`:
  **383 passed, 0 failed** (was 375; +8 from this pass's new/updated
  orchestration-discovery and CLI tests), 1 unrelated deprecation warning
  (`anyio.abc.BlockingPortal`, from `starlette`'s test client, not this
  project's code).
- `Agent.query()`, `SourceRegistry.discover()`, `Orchestrator` federation
  discovery/ranking, the HMAC-SHA256 webhook auth, and the Pydantic
  validation on the four MCP tools all match what the README claims —
  verified by reading the implementation, not just the tests (tests here
  are largely honest, e.g. `test_webhook_hmac_auth.py` actually asserts
  tampered-payload/missing-secret/wrong-secret rejection).
- OKF (Open Knowledge Format) catalog/discovery/query-planner
  (`okf_core.py`, `okf_discovery.py`, `okf_query_planner.py`) is real and
  tested (`test_okf_core.py`, `test_okf_discovery.py`,
  `test_okf_query_planner.py` all pass) — not fabricated, not previously
  documented in the README (now cross-linked from
  `docs/ARCHITECTURE.md`).
- `actionlint .github/workflows/ci.yml`: clean after this pass's fixes.
- `ruff check python/ tests/`: runs, does not crash (951 findings — see
  Technical Debt below; not previously wired into CI at all).

## 2. Confirmed bugs / fabrications found this pass (not fixed — documented per the disclosure-first policy)

### 2.1. Fabricated discovery data in three orchestration-tool adapters (FIXED in the quick-fix pass, 2026-09-22)

**Fixed**: turned out to be mechanical, not the non-trivial constructor
redesign originally estimated below — `SourceRegistry.discover()` is a
drop-in replacement for the fake dict shape (`name`/`type`/`relevance`,
plus a `matched_terms` field the fake data never had). All three classes
now accept an optional `registry: Optional[SourceRegistry] = None`
constructor/dataclass field (defaulting to a fresh, empty registry —
same pattern `LangchainAdapter` already used) and call
`registry.discover(context, limit=...)` instead of synthesizing
`source_0..source_4`. `TemporalWorkflow` also got a `registry` param so
`discover_sources()` can pass one through to the activity it creates.
`tests/test_sprint5_orchestration.py` now has paired tests per adapter:
one confirming an untouched registry honestly returns zero sources (not
fake ones), one confirming a real registered source is actually found by
name — content assertions, not just shape, so this can't regress
silently again. Original analysis (now superseded) kept below for
context.

`python/pystreammcp/orchestration/temporal.py`
(`TemporalDiscoveryActivity.execute()`, line 61-76),
`python/pystreammcp/orchestration/airflow.py` (discovery `execute()`,
around line 122-134), and `python/pystreammcp/orchestration/nocode_rpa.py`
(around line 74) each independently return a **hardcoded fake result** —
`{"name": f"source_{i}", "relevance": 0.95 - (i * 0.05), "type":
"database"} for i in range(min(self.max_sources, 5))` — instead of
calling the real `SourceRegistry.discover()` that every other surface
(REST, MCP, LangChain adapter) actually uses. Each is marked with a
`# In production, use actual discovery logic` comment acknowledging it.

This is the exact "fabricated integration" pattern this org has hit
before in sibling repos, and it's real here, not a false positive:
`tests/test_sprint5_orchestration.py::test_temporal_discovery_activity`
(line 37-47) only asserts `status == "completed"`, `len(sources) > 0`,
and that `"relevance"` is a key — it never checks the values are real, so
the fabrication passes CI. The Temporal *query* activity
(`TemporalQueryActivity`, same file, line 14-48) is fine — it correctly
calls `Agent.query()`.

**Fix required**: wire all three discovery adapters to a real
`SourceRegistry` instance instead of synthesizing `source_0..source_4`.
Non-trivial because it changes the constructor signature of all three
classes (need a registry passed in or looked up) — left for a dedicated
follow-up.

### 2.2. `pystreammcp` CLI is dead code — unreachable two independent ways (FIXED in the quick-fix pass, 2026-09-22)

**Fixed**: added `[project.scripts]` (`pystreammcp = "pystreammcp.cli:cli"`)
to `pyproject.toml`, and changed `cli.py`'s `if __name__ == "__main__":`
guard to call the real Click `cli()` group. Decided to keep the Click
implementation (not the legacy one) since `scripts/setup_shortcuts.sh`'s
aliases already assume `pystreammcp dashboard`/`pystreammcp query` exist
on `PATH` — those now actually work. The legacy `CLIInterface`/`main()`/
`print_help()` (had no callers, no tests, no docs referencing it) was
deleted rather than left as unreachable dead code. Fixed the
`ModuleNotFoundError` risk noted below by lazy-importing
`pystreammcp.api` inside the `server` command function; without the
`api` extra, `pystreammcp server` now prints a clear "install
`pystreammcp[api]`" message and exits 1 instead of crashing. Verified for
real: clean venv install, `which pystreammcp`, `pystreammcp version`,
`--help`, `query --json`, `dashboard --static`, `python -m
pystreammcp.cli version` — and separately, a second clean venv without
the `api` extra to confirm `version`/`query`/`dashboard` still work and
`server` fails cleanly. Added `tests/test_cli.py`. Original analysis (now
superseded) kept below for context.

`python/pystreammcp/cli.py` actually contains **two different, conflicting
CLI implementations** in one file:

1. A Click-based `@click.group() def cli()` (top of the file) with
   `query`/`server`/`version`/`dashboard` subcommands (`server` at line
   84, `version` at line 92, `dashboard` at line 103).
2. A second, separate, hand-rolled `sys.argv`-parsing `main()` (line 181)
   with a *different, smaller* command set:
   `query`/`create-agent`/`metrics`/`help` — no `server`, `version`, or
   `dashboard` at all.

Both are unreachable as shipped:

- **No installed command at all**: `pyproject.toml` has no
  `[project.scripts]` entry. Verified: `pip install -e .` into a clean
  venv, then `which pystreammcp` → not found.
- **`python -m pystreammcp.cli` doesn't even reach the Click group**: the
  file's own `if __name__ == "__main__":` guard (line 284) calls the
  *legacy* `main()`, not the Click `cli()` group. Verified directly:
  `python -m pystreammcp.cli version` → `{"error": "Unknown command:
  version"}` (proves it hit the legacy interface, not Click — Click would
  have printed `PyStreamMCP v3.3.0`). `python -m pystreammcp.cli query
  "test query"` does work (hits the legacy interface) and returns a real
  `Agent.query()` result.

Net effect: the entire Click-based `server`/`version`/`dashboard`
implementation (lines ~1-124) is **dead code that nothing in the codebase
ever invokes** — not an installed script, not the module's own
`__main__` guard, not imported and called anywhere else (checked: no
other file imports `cli.cli`). Only `query`/`create-agent`/`metrics`/
`help` via the legacy `main()` actually work, and only when run as
`python -m pystreammcp.cli <command>` from a source checkout.

This matters because the README (pre-this-pass) referenced `pystreammcp
server` as one of three ways to run the HTTP server, implying it's an
installed, working command — it was neither. Fixed in this pass: README
now describes the actual, verified-working entry points.

**Not fixed**: making the Click CLI reachable requires (a) deciding which
of the two implementations to keep (the legacy one has real working
callers in `scripts/setup_shortcuts.sh`'s aliases, which assume a
`pystreammcp dashboard`/`pystreammcp query` command exists on `PATH` and
would currently fail), (b) adding `[project.scripts]`, and (c) — if
keeping the Click version — lazy-importing `pystreammcp.api` inside the
`server` command function instead of at module top, since `cli.py` line 9
unconditionally does `from pystreammcp.api import PyStreamMCPAPI` and
`api.py` line 8 unconditionally does `from fastapi import FastAPI, ...`;
`fastapi` is only in the optional `api` extra, so a naively-wired
entry point would `ModuleNotFoundError` on `pystreammcp version` for
anyone who installed without `[api]`. Left for a dedicated follow-up.

### 2.3. `Dockerfile` was fundamentally broken (fixed this pass)

The old `Dockerfile` started with a Python-style `"""..."""` docstring as
its first lines — not valid Dockerfile comment syntax — and its
multi-stage build compiled the Rust workspace with `cargo build --release
--all-features` + `maturin develop --release`, which (a) uses `maturin`,
a build tool this project's actual `pyproject.toml` doesn't use
(setuptools is the real backend) and (b) cannot succeed because the Rust
workspace has 43 compile errors (verified: `cargo build --workspace`
under `rustup run stable`, see §3). Even ignoring the Rust failure, the
runtime stage's `CMD ["python", "-m", "pystreammcp.api"]` would exit
immediately and do nothing, because `api.py` has no `if __name__ ==
"__main__"` block — no server would actually start, and the healthcheck
would never pass.

Replaced with a single-stage pure-Python `python:3.11-slim` image that
installs `.[api]` and runs `uvicorn pystreammcp.api:create_app --factory`.
**Not fully verified**: `docker build` in this sandbox fails at `pip
install` inside the container with `Network is unreachable` (this
sandbox's container runtime has no outbound network — matches the
documented environment limitation, not a flaw in the new Dockerfile). The
Dockerfile's logic was checked by hand against the real, working
`create_app()` factory and confirmed-passing local `pip install -e
".[api]"`; a real `docker build` should be run in CI or by a maintainer
with network access before relying on it.

### 2.4. Two architecture docs were actively misleading (archived this pass, not fixed-in-place)

- Root `ARCHITECTURE.md` (now
  `docs/archive/ARCHITECTURE_RUST_CORE_ASPIRATIONAL.md`) described
  boundary integrations with StatGuardian/PyReverseETL/ClusterAudienceKit/
  PyCustomerJourney as if real and enforced, and closed with "✅ 60-75%
  token reduction (target met)" stated as fact. The referenced Rust
  module structure (`core/src/statguardian.rs` etc.) does exist as
  *type definitions* (structs/enums for `ValidationGate`,
  `ValidationResult`) but has no actual network call to any real
  StatGuardian service, and the workspace containing it doesn't compile.
  A previous audit pass (commit `9292af4`) explicitly kept this file
  because it had "no staleness markers" — it should have been archived
  then; this pass caught what that one missed.
- `docs/PRODUCT_VISION.md` (now
  `docs/archive/PRODUCT_VISION_MCP2.0_FABRICATED.md`) claimed a "unified
  MCP 2.0 Platform (228 tools across 19 projects)", a fixed MCP port
  (8772), "Depends on: All 18 projects", and "Status: Production Ready
  (v2.0.0)" — none of which exists in this repo (current version 3.3.0;
  no such platform, port config, or 18/19-project dependency anywhere in
  the manifest or code).

`docs/ARCHITECTURE.md` itself was previously a content-free template
("Primary logic and functionality", "External libraries", etc. as literal
placeholder bullet text) that also linked to a non-existent `ROADMAP.md`.
Replaced this pass with a real architecture doc reflecting the actual
shipped package.

### 2.5. `pyproject.toml` classifier overclaimed maturity (fixed this pass)

`Development Status :: 5 - Production/Stable` was the PyPI classifier
before this pass. Given items 2.1-2.3 above, plus the unshipped/broken
Rust workspace and `"not_implemented"` federation/join endpoints, "5 -
Production/Stable" is not honest. Changed to `4 - Beta`.

### 2.6. `CONTRIBUTING.md` claimed the wrong license (fixed this pass)

Said "License: MIT" at the bottom despite the project having relicensed
to Apache-2.0 (commit `9cb380b`, `pyproject.toml`'s `license =
"Apache-2.0"`, and the real `LICENSE` file all agree — only
`CONTRIBUTING.md` had drifted). Fixed to say Apache License 2.0.

### 2.7. `.gitignore`'s `ROADMAP_*` pattern would have silently swallowed this very file

`.gitignore` line 47 (`ROADMAP_*`) is a deliberate "don't expose internal
strategy docs" rule, but it also matches `ROADMAP_HONEST.md` — the
file you're reading, which is meant to be public. Added a `!ROADMAP_HONEST.md`
negation immediately after that block; without it, `git add
ROADMAP_HONEST.md` would have been a silent no-op.

## 3. Rust workspace: confirmed broken, not attempted

`cargo build --workspace` (`rustup run stable`, since the pinned
`rust-toolchain.toml` channel 1.81 can't resolve current registry
dependencies at all — `idna_adapter v1.2.2` requires the `edition2024`
cargo feature) fails with **43 compile errors** in `pystreammcp-core`,
including:

- 12× `E0308` mismatched types
- 6× `E0599` — `error::Error::Generic` variant doesn't exist
- 4× `E0609` — `no field 'source' on RankedCandidate`
- 6× `E0277` — `FusionMethod`/`RankingStrategy`
  (`core/src/orchestration/multimodal.rs`) missing `Serialize`/
  `Deserialize` derives
- 4× `E0533` — `BudgetTier::{Standard,Minimal,Large,Comprehensive}`
  referenced as unit variants but defined as struct variants
- `E0432` unresolved imports `orchestration::{UserContext,
  ExpertiseLevel}`; `E0425` — `stage2_decisions` not in scope; `E0603` —
  `IntentScore`/`QueryIntent` imported but private; `E0252` — `TokenBudget`
  defined twice; `E0502` borrow conflict in `core/src/.../multiplier.rs`
  or similar.

This matches what the README/CHANGELOG already say ("does not currently
compile"), independently reverified this pass rather than taken on faith.
Not fixed — 43 errors across a workspace that isn't shipped is out of
scope for a documentation/disclosure pass; tracked here for whoever picks
up the Rust core next.

### 3.1. Rust "tests" that are empty stubs (no fake stubs policy violation)

`tests/metadata_filtering_tests.rs` (240 lines) and
`tests/selective_retrieval_tests.rs` (333 lines) contain **zero
`assert!`/`assert_eq!` calls between them** — every `#[test]` fn body is
just comments describing what it would test (e.g. "Authority = SSL (30%)
+ domain age (30%) + wayback depth (40%)") with no actual assertion. Even
if the workspace compiled, these would vacuously pass regardless of
correctness. `core/tests/phase_v05_metadata_tests.rs` (530 lines) is real
by contrast — 43 real `assert!`/`assert_eq!` calls. Not fixed (part of
the non-compiling, unshipped workspace); flagged because it's a clean
example of the "no fake stubs" anti-pattern for whoever fixes the Rust
core next.

## 4. Technical debt (concrete, file:line, not fixed this pass)

- **910 ruff findings** across `python/` + `tests/` (was 951; the
  41-finding drop is the `datetime.utcnow()` fixes below — see
  `CHANGELOG.md`) (`ruff check python/ tests/`), never previously run in
  CI (now added as a non-blocking `lint` job in
  `.github/workflows/ci.yml`). Breakdown:
  - 468× `UP006` (`typing.Dict`/`List` instead of `dict`/`list`) + 144×
    `FA100` + 76× `UP035` (deprecated `typing` imports) — cosmetic/
    modernization, safe to bulk-fix with `ruff check --fix`, but 688
    findings is enough churn that it deserves its own PR, not folding
    into a docs pass.
  - 71× `I001` unsorted imports, 55× `F401` unused imports — safe
    autofixes, same reasoning.
  - **2× `DTZ003`** (`datetime.utcnow()`, was 43 — FIXED in the
    quick-fix pass, 2026-09-22, in `webhook_handlers.py` (29),
    `webhook_router.py` (7, incl. the `MCPEndpoint.last_heartbeat`
    field default), `quality.py` (4, incl. `QualityCheck.checked_at`/
    `ValidationResult.last_validated`, migrated together with their 3
    staleness-check subtractions since they interact), `server.py` (2),
    `multi_agent.py` (1); see `CHANGELOG.md`. The 2 remaining are
    self-contained inside a test-local helper in
    `tests/test_integration_phase2.py`, not tied to production code —
    left as-is, not worth touching) + **23× `DTZ005`** (`datetime.now()`
    without `tzinfo` — a different call pattern, not touched this pass;
    real correctness risk, same class of bug as `DTZ003`) — naive
    datetimes break comparisons against aware ones. Not concentrated in
    the files listed in the previous version of this doc — recheck with
    `ruff check --select DTZ005` for current locations.
  - **11× `BLE001`** blind `except Exception` + **1× `E722`/`S110`** bare
    `except: pass` at `python/pystreammcp/integrations/langsmith.py:150`
    (silently swallows any error computing span duration — no logging,
    no re-raise).
  - `B006` mutable default argument: `python/pystreammcp/api.py:250`,
    `async def batch_query(agent_id: Optional[str] = None, texts:
    List[str] = [])` — classic shared-mutable-default bug risk.
  - `RUF013` implicit Optional: `python/pystreammcp/cli_daemon.py:59`,
    `def start_persistent_dashboard(package_name: str, cmd: str = None)`.
  - `F821` undefined names (forward-reference type hints that were never
    imported, so they're just wrong at introspection time, e.g.
    `typing.get_type_hints`):
    `python/pystreammcp/integrations/langchain.py:161,198,295`
    (`"LangchainTool"`, `"BaseRetriever"`),
    `python/pystreammcp/integrations/llamaindex.py:154`
    (`"BaseRetriever"`),
    `python/pystreammcp/integrations/semantic_kernel.py:156`
    (`"KernelPlugin"`).
  - ~~`F841` unused variable `python/pystreammcp/orchestration/temporal.py:61`~~
    FIXED — removed along with the §2.1 fabrication fix; the unused
    `agent = Agent(agent_id=self.agent_id)` was the lint's tell that
    `execute()` never actually used real discovery logic.
  - No `[tool.ruff]` section in `pyproject.toml` at all — the 910 count is
    against ruff's full default rule set, not a set the project has
    actually opted into. Whoever does the lint-cleanup pass should also
    decide which rules to actually enable/ignore intentionally rather
    than leave it un-configured.
- **Dependency vulnerabilities** (real `pip-audit` run this pass, not
  simulated): 7 known CVEs across `nltk==3.10.3` (pulled in transitively
  by `llama-index`/`llama-index-core` — `PYSEC-2026-3740`, no fix version
  listed) and `werkzeug==3.1.1` (pulled in by `flask>=2.3.0` in the `api`
  extra — `PYSEC-2026-2046`/`PYSEC-2026-2044`/`PYSEC-2026-2320`, fixed in
  3.1.4/3.1.5/3.1.6 respectively). Neither is pinned in `pyproject.toml`,
  so a fresh `pip install` can resolve the vulnerable `werkzeug`/`nltk`
  today. Not fixed this pass (requires deciding on/testing a `werkzeug`
  floor bump without breaking Flask compat, and confirming no `nltk`
  functional dependency on the vulnerable code path) — added as a
  non-blocking `security-audit` CI job (`pip-audit`) so this doesn't
  regress silently.
- **`Cargo.lock` is gitignored** (`.gitignore:3`) — the org-wide recurring
  pattern from other Mullassery repos (sdist/reproducibility issues).
  Lower urgency here specifically because the Rust workspace doesn't
  compile and isn't shipped, but if/when someone fixes the Rust core,
  `Cargo.lock` should be committed for the `python/` crate (a `cdylib`,
  effectively an application-like artifact) before it's built in CI or
  distributed.
- **No `RUSTFLAGS` documented** for macOS PyO3 linking
  (`RUSTFLAGS="-C link-args=-undefined -C link-args=dynamic_lookup"`) —
  moot while the workspace doesn't compile, but will bite whoever fixes
  it next on macOS.
- **`docs/archive/` has 66 files** now (64 from the previous pass + the 2
  added this pass) with no per-file staleness date in most of them beyond
  the top-level `docs/archive/README.md` note — fine for now, but will
  get harder to audit as it grows; consider a `docs/archive/INDEX.md`
  with one line per file if it keeps growing.

## 5. Pending / incomplete features (explicit, no hedging)

- **Cross-project federated query execution**: accepted at the API/MCP
  level, returns `{"status": "not_implemented", "message": "Federated
  query execution across projects is not yet implemented; ..."}`
  (`_mcp_connector.py:362-365`). Does not exist. Not partially built —
  fully absent.
- **Cross-database joins**: same — `_mcp_connector.py:448-459`,
  `{"status": "not_implemented", "message": "Cross-database join
  execution is not yet implemented."}`. Does not exist.
- ~~**`SourceRegistry` discovery in Temporal/Airflow/RPA adapters**~~
  FIXED — see §2.1.
- ~~**`pystreammcp` CLI as an installed command**~~ FIXED — see §2.2.
- **Rust performance backend** (`core/`, `python/src/lib.rs`): does not
  compile (§3), not shipped, no timeline. Anyone relying on it should
  not.

## 6. Explicitly out of scope for this pass (and why)

- **Fixing the remaining 910 ruff findings**: mixing a 688-cosmetic-finding
  autofix PR into a quick-fix pass would make the diff unreviewable and
  bury the real findings (`DTZ005`, `BLE001`, `B006`, `F821`) in noise.
  Left as a dedicated follow-up; CI now surfaces the count via the
  non-blocking `lint` job so it can't silently grow further unnoticed.
  (§2.1's fabricated-discovery fix and the `DTZ003` `datetime.utcnow()`
  migration *were* done this pass — see §2.1/§2.2 and `CHANGELOG.md`;
  turned out to be mechanical, not the non-trivial follow-up originally
  estimated.)
- **Pinning `werkzeug`/investigating `nltk`**: needs compatibility testing
  against the `flask>=2.3.0` floor and confirming `llama-index` still
  works with a patched `nltk`; not a same-session change.
- **Rust core compile errors (§3)**: 43 errors across an unshipped
  workspace; substantial, dedicated follow-up if the Rust backend is ever
  revived.
- **CODE_OF_CONDUCT.md / SECURITY.md**: added in this pass (see repo
  root) — not skipped.
