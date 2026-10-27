# Vendored dependency sources

This directory contains pinned source snapshots of optional upstream
dependencies. The snapshots are repository assets: they are not included in
the built wheel or sdist and are never imported from an installed wheel.

## Pins

| Component | Upstream | Tag | Commit | License |
|---|---|---|---|---|
| qmd | https://github.com/tobi/qmd | `v2.8.3` | `facd35e01359e59d938bc9418e93fb9318addee3` | MIT |
| rag-anything | https://github.com/HKUDS/RAG-Anything | `v1.4.3` | `afb67c43d391b1b1008a6fee9f020a232067b9e5` | MIT |
| lightrag | https://github.com/HKUDS/LightRAG | `v1.4.16` | `964f26e9a9239c1316045913328e863ec35492e4` | MIT |

The machine-readable pins and tree checksums live in
[`deps.lock.json`](deps.lock.json).

## Tree checksums

`tree_sha256` is SHA-256 over a canonical UTF-8 JSON array of
`[relative_posix_path, sha256_of_file_bytes]` pairs, sorted by path, with no
extra whitespace. It excludes `.git`, `__pycache__`, `.pytest_cache`,
`.ruff_cache`, `node_modules`, `dist`, `build`, and compiled Python files.
Symlinks are rejected rather than hashed.

## Source fallback

RAG-Anything and LightRAG resolve dependencies in this order:

- `PYSTREAMMCP_RAG_SOURCE=auto`: use an installed `raganything` and
  `lightrag` pair only when both are importable; otherwise use both vendored
  snapshots.
- `PYSTREAMMCP_RAG_SOURCE=installed`: require the installed pair.
- `PYSTREAMMCP_RAG_SOURCE=vendored`: require the vendored pair.

Installed and vendored packages are never mixed. QMD is reached over HTTP;
its vendored source is an emergency rebuild input and is never started or
built automatically.

## Limitations

- The snapshots contain upstream tracked files only. `.git`, submodules,
  symlinks, and generated dependency trees are excluded.
- RAG-Anything and LightRAG still need their PyPI dependencies. QMD still
  needs Node and its npm dependencies.
- The adapter never updates, downloads, installs, or starts vendored code
  automatically.
- Updates are reviewed source changes, never runtime operations.

## Maintainer updates

Only `scripts/vendor_dependencies.py` may mutate this directory:

```bash
.venv/bin/python scripts/vendor_dependencies.py verify
.venv/bin/python scripts/vendor_dependencies.py vendor --component all
.venv/bin/python scripts/vendor_dependencies.py update --component lightrag --tag v1.4.16
```

`verify` is offline. `vendor` and `update` need network access. Updates must
pass the vendor tests and the retrieval test suite before being committed.
