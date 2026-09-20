## What does this change do?

<!-- One or two sentences. -->

## Why?

<!-- What problem does this solve, or what does it enable? -->

## How was this tested?

<!-- e.g. `pytest tests/ -v`, manual steps, or "not tested" — be honest. -->

## Checklist

- [ ] `pytest tests/ -v` passes locally
- [ ] `ruff check python/ tests/` doesn't add new findings (the repo has
      pre-existing debt tracked in `ROADMAP_HONEST.md` — no need to fix
      unrelated ones, just don't add more)
- [ ] Updated `CHANGELOG.md` under `[Unreleased]` if this is a
      user-visible change
- [ ] Updated `README.md` / `ROADMAP_HONEST.md` if this changes what's
      built vs. not built (no hedge language — state plainly what works
      and what doesn't)
