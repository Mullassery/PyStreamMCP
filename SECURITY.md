# Security Policy

## Supported versions

PyStreamMCP is a single-maintainer project. Only the latest release on
PyPI is supported; there is no backport policy for older versions.

## Reporting a vulnerability

Please report security issues privately rather than opening a public
GitHub issue. Email **mullassery@gmail.com** with:

- A description of the vulnerability and its potential impact
- Steps to reproduce (a minimal example, if possible)
- Which version/commit you tested against

This is a single-maintainer, part-time project — there is no guaranteed
response SLA. You should get an acknowledgment within a few days.

## Known security-relevant behavior (see README/ROADMAP_HONEST.md for detail)

- The webhook endpoint (`POST /orchestration/webhooks/events`) requires
  `PYSTREAMMCP_WEBHOOK_SECRET` to be set and fails closed (503) if it
  isn't — there is no "accept unsigned events" fallback. Verified by
  `tests/test_webhook_hmac_auth.py`.
- HTTP/CLI servers bind to `127.0.0.1` by default; you must explicitly
  pass `--host 0.0.0.0` / `host="0.0.0.0"` to expose them.
- As of the 2026-09 audit, `pip-audit` found known CVEs in transitive
  dependencies (`werkzeug` via the `api` extra's `flask`, and `nltk` via
  `llama-index`) that are not yet pinned/patched — see
  [`docs/internal/ROADMAP_HONEST.md`](docs/internal/ROADMAP_HONEST.md) §4 for exact versions and CVE
  IDs. If you depend on this package's `api`/`llamaindex` extras in a
  security-sensitive context, check `pip-audit` yourself before deploying.

## Retrieval adapters

- QMD defaults to a loopback URL. Non-loopback QMD URLs require
  `PYSTREAMMCP_QMD_ALLOW_REMOTE=true`, and credentials embedded in the URL
  are rejected. QMD collections are an explicit allowlist; requests may
  select a subset but never a collection outside it.
- RAG ingestion is limited to `PYSTREAMMCP_RAG_ALLOWED_ROOTS` (an
  `os.pathsep`-separated list). Path traversal, symlinks, extensions outside
  the allowlist, and files over `PYSTREAMMCP_RAG_MAX_FILE_MB` are rejected.
  HTML is not ingested. Markdown local-image references are checked before
  ingestion. The adapter has no deletion API and does not remove source files.
- Remote model egress is opt-in: when an OpenAI-compatible provider is
  configured, document text or images are sent to the configured LLM,
  embedding, or vision endpoints. With no provider and no injected engine,
  RAG retrieval/ingestion is unavailable.
- Vendored QMD, RAG-Anything, and LightRAG snapshots are pinned by tag,
  commit, and tree checksum in `vendor/deps.lock.json`. Trees are verified
  offline; missing, corrupted, or symlinked trees are rejected. Installed and
  vendored RAG pairs are never mixed.
- There is no runtime dependency update, download, install, or automatic QMD
  start. `pystreammcp retrieval deps status` is read-only and never mutates
  the lock file. Upstream checks may use `GITHUB_TOKEN`; token and API-key
  values are redacted from errors and are not printed.

See [`docs/retrieval.md`](docs/retrieval.md) for the complete environment and
routing contract.
