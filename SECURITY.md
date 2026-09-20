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
  [`ROADMAP_HONEST.md`](ROADMAP_HONEST.md) §4 for exact versions and CVE
  IDs. If you depend on this package's `api`/`llamaindex` extras in a
  security-sensitive context, check `pip-audit` yourself before deploying.
