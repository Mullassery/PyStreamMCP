# PyStreamMCP documentation

## Start here

| Document | What it covers |
|---|---|
| [README](../README.md) | Overview, install, quick start, usage |
| [Architecture](ARCHITECTURE.md) | Shipped package structure |
| [Cross-repo integrations](INTEGRATIONS.md) | What is wired, real-tested, and not tested |
| [Honest roadmap](internal/ROADMAP_HONEST.md) | Implemented/partial/missing |
| [Known issues / queue](internal/QUEUE_STATUS.md) | Shipped/blocked/rejected |

## Reference

| Document | What it covers |
|---|---|
| [OKF integration](../OKF_INTEGRATION.md) | Open Knowledge Format |
| [Security policy](../SECURITY.md) | Reporting and scope |
| [Contributing](../CONTRIBUTING.md) | Development setup |
| [ADRs](adr/) | Architecture decisions |
| [`archive/`](archive/) | Historical plans and reports |

## Status discipline

- Fake-module tests are contract tests; they are not integration evidence.
- Real cross-repo tests live in `tests/test_statguardian_live.py` and
  `tests/test_mudfish_live.py`.
- `tests/test_support_matrix.py` asserts that the documented support matrix,
  `pyproject.toml` extras, and runtime guards stay in sync.
- A skipped test is documented as **not tested**.
