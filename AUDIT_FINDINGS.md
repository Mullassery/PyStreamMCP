# Audit findings — 2026-10-19

This file records the repository-specific findings from the portfolio audit
conducted on 2026-10-19. It is documentation only; no code or release artifacts
were changed in this pass unless explicitly noted under "Implementation status".

Sources: the repository's own README/source/workflows, GitHub metadata and
Actions runs, PyPI metadata, and official competitor documentation. Claims are
marked as verified, inferred, or open questions. "Absent" means not found in the
inspected repository/docs, not proof that it cannot exist.

## What it is

Query planning, context/source discovery, and MCP orchestration for AI agents.

## Verified strengths

- Pure-Python package; MCP tool server; federation probing; HMAC webhook server; LangChain/LlamaIndex/CrewAI/Semantic Kernel/PydanticAI/Haystack adapters; CLI; 27 tests.
- MCP orchestration across servers is the real wedge.

## Verified gaps and user-facing risks

- Source discovery is Jaccard word overlap, not semantic; federated execution/cross-DB joins return `not_implemented`.
- Rust backend is not shipped; '60–75% token reduction' has no committed benchmark.
- No external users; no GitHub release.

## Direct competitors

- Graphify (codebase knowledge graph + MCP, 128k stars), Repomix (29k), Context7, LlamaIndex, MCP gateways.

## Ranked next actions

- P1: semantic retrieval or Graphify integration (M).
- P2: MCP orchestration hardening (timeouts/auth/retries) (S).

## Do not build

- The Rust backend; not shipped and adds maintenance.

## Evidence gaps / validation needed

- No benchmark for the savings claim; no multi-server reliability test.

## Recommended disposition

Maintain; focus on orchestration, not retrieval.

## Implementation status

No code changes in this pass.
