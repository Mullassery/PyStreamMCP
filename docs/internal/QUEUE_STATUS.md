# Queue status — 2026-10-19

This file records what was shipped, what is blocked/failed, and what is rejected for this repository. It complements `AUDIT_FINDINGS.md`.

## Shipped
- Federated DuckDB/SQLGlot read-only execution (`pystreammcp[federation]`).
- API-key/Bearer HTTP auth for Flask/FastAPI plus MCP `call_tool` token enforcement.

## Blocked / failed
- Semantic retrieval/Graphify integration.

## Rejected / deferred
- The Rust backend; not shipped.

## Policy

Any future feature or upgrade must check `AUDIT_FINDINGS.md` and this file before implementation. A blocked item is retried only when its external dependency is available; a rejected item needs new user evidence or a design change to reopen.
