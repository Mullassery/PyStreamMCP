# Archive

64 historical planning/phase/stage/research docs (spanning v0.3 through
early v3.x development), kept for reference only, none referenced by the
current README. For current status see [`../../README.md`](../../README.md).

Two more were added in the 2026-09 OSS-standardization pass, for being
actively misleading rather than merely stale:

- `ARCHITECTURE_RUST_CORE_ASPIRATIONAL.md` (was root `ARCHITECTURE.md`) —
  describes the `core/`/`python` Rust workspace as if its cross-project
  integration points (StatGuardian, PyReverseETL, ClusterAudienceKit,
  PyCustomerJourney) are real, working boundaries, and closes with
  "✅ 60-75% token reduction (target met)" as a stated fact. In reality
  that workspace does not compile (verified: `cargo build --workspace`
  fails with 43 errors as of this pass) and is not part of the published
  package — see the README's "Rust workspace (not shipped)" section.
- `PRODUCT_VISION_MCP2.0_FABRICATED.md` (was `docs/PRODUCT_VISION.md`) —
  describes a "unified MCP 2.0 Platform (228 tools across 19 projects)"
  with this project "Depends on: All 18 projects", a fixed port
  assignment, and "Status: Production Ready (v2.0.0)" — none of which
  matches this repo (currently v3.3.0, no such platform/port/dependency
  exists in the actual manifest or code).
