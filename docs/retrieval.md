# Retrieval adapters

PyStreamMCP can search two optional local-knowledge backends behind one
normalized interface:

- **QMD** — an external TypeScript service reached over HTTP.
- **RAG-Anything + LightRAG** — in-process document and multimodal retrieval.

Both are opt-in. With no retrieval environment variables set, the core package
loads no RAG-Anything, LightRAG, or OpenAI modules and retrieval tools report a
clear `not_configured` error instead of falling back silently.

## Install

The core package has no retrieval service dependency:

```bash
pip install PyStreamMCP
```

RAG-Anything retrieval and ingestion require Python 3.10+ and the optional
extra:

```bash
pip install "PyStreamMCP[rag-anything]"
```

The extra pins `raganything>=1.4.3,<1.5` and `lightrag-hku==1.4.16` so the
installed pair stays aligned with the vendored LightRAG snapshot.

QMD is **not bundled**. It needs Node.js and the npm package `@tobilu/qmd`.
Start its HTTP MCP mode separately:

```bash
npm install -g @tobilu/qmd
qmd mcp --http
```

The default QMD endpoint is `http://127.0.0.1:8181`. PyStreamMCP never starts,
builds, updates, or installs QMD automatically.

## Vendored sources

Pinned source snapshots live under [`vendor/`](../vendor/README.md), with
machine-readable pins and tree checksums in
[`vendor/deps.lock.json`](../vendor/deps.lock.json):

| Component | Tag | Commit |
|---|---|---|
| QMD | `v2.8.3` | `facd35e01359e59d938bc9418e93fb9318addee3` |
| RAG-Anything | `v1.4.3` | `afb67c43d391b1b1008a6fee9f020a232067b9e5` |
| LightRAG | `v1.4.16` | `964f26e9a9239c1316045913328e863ec35492e4` |

`PYSTREAMMCP_RAG_SOURCE` controls resolution:

- `auto` (default): use installed `raganything` and `lightrag` only when both
  imports are available; otherwise use both vendored snapshots.
- `installed`: require installed distributions and never add vendored paths.
- `vendored`: require both vendored snapshots and never import installed
  distributions.

Installed and vendored packages are never mixed. Vendored trees are verified
offline by checksum before use. The snapshots are repository assets only: they
are not included in wheels or sdists and are never imported from an installed
wheel.

RAG-Anything and LightRAG still need their own transitive PyPI dependencies.
Vendoring the source does not vendor those packages. QMD remains an HTTP
service whose vendored source is an emergency rebuild input, not a runtime
fallback.

Check dependency state read-only:

```bash
pystreammcp retrieval deps status --offline --json
pystreammcp retrieval deps status
```

Exit codes are `0` when pins are current, `1` when an update is available, and
`2` for missing/corrupt trees or a failed upstream check. `--offline` skips
GitHub entirely and still verifies vendored checksums. The command never
downloads, installs, updates, or mutates the lock file. Upstream checks may use
`GITHUB_TOKEN`; token values are redacted from errors.

## Library API

```python
from pystreammcp import RetrievalRequest, RetrievalService

service = RetrievalService.from_env()
try:
    response = service.search(
        RetrievalRequest(query="deployment notes", limit=5)
    )
    for group in response.groups:
        print(group.backend, group.status, len(group.hits))
finally:
    service.close()
```

`RetrievalService.from_env()` reads the environment, registers only configured
backends, and keeps unconfigured backends out of calls. Tests and embedders can
inject service or backend objects directly; injected engines bypass environment
source resolution.

Responses are grouped per backend:

```json
{
  "status": "success",
  "query": "deployment notes",
  "backend_requested": "auto",
  "groups": [
    {
      "backend": "qmd",
      "status": "ok",
      "hits": [],
      "error": null,
      "elapsed_ms": 4,
      "truncated": false
    }
  ],
  "diagnostics": {}
}
```

There is **no cross-backend fusion or re-ranking**. Hits keep their backend,
rank, source URI, locator, excerpt, optional content, score, and metadata.
Group order and backend status make partial failures visible.

## MCP tools

The server advertises these tools alongside the existing tools:

- `pystreammcp_retrieval_search` — normalized grouped search.
- `pystreammcp_retrieval_capabilities` — backend capabilities, optionally with
  health.
- `pystreammcp_rag_ingest` — guarded local ingestion into RAG-Anything.

Example arguments:

```json
{
  "name": "pystreammcp_retrieval_search",
  "arguments": {
    "query": "deployment notes",
    "backend": "auto",
    "limit": 5,
    "include_content": false,
    "max_content_chars": 2000
  }
}
```

`get_info` advertises the `retrieval` capability only when a retrieval service
is injected or `PYSTREAMMCP_QMD_ENABLED` / `PYSTREAMMCP_RAG_ENABLED` is true.
It does not construct the service.

## CLI

Commands are mounted under `pystreammcp retrieval`:

```bash
pystreammcp retrieval search QUERY [--backend auto|qmd|rag_anything|all]
  [--mode TEXT] [--collection NAME ...] [--content-type TEXT] [--limit N]
  [--include-content] [--max-content-chars N] [--time-budget-ms N]
  [--intent TEXT] [--json]
pystreammcp retrieval capabilities [--no-health] [--json]
pystreammcp retrieval health [--json]
pystreammcp retrieval ingest PATH [--force-multimodal] [--json]
pystreammcp retrieval deps status [--offline] [--json]
```

JSON mode prints one object. Human mode prints per-backend status, hits, and a
hit count. `partial`/`error` search results and `RetrievalError` exit `1`.
There are no secrets, provider, or allowed-root flags on the CLI; security
boundaries come from the environment.

## Routing

Routing is explicit and deterministic:

- `backend=qmd`, `rag_anything`, or `all` selects exactly those backends.
- `backend=auto` selects configured backends based on the request.
- `collections` require QMD and are checked against the configured allowlist.
- A non-text `content_type` preference routes to RAG-Anything.
- An explicit backend that is not configured fails with a typed error.

There is **no silent fallback** from a requested backend to another backend.
RAG query modes are `auto`, `hybrid`, `local`, `global`, `naive`, and `mix`.
QMD-only modes such as `keyword`, `semantic`, `vector`, and `hyde` are rejected
for RAG-Anything rather than translated silently.

## Scores

QMD relevance scores are backend-specific and are **not comparable** to
RAG-Anything results, which expose retrieval order rather than a calibrated
relevance score. Use `score_kind` to distinguish them and do not fuse across
backends by raw score.

## Environment

QMD:

| Variable | Default | Meaning |
|---|---|---|
| `PYSTREAMMCP_QMD_ENABLED` | `false` | Register the QMD backend |
| `PYSTREAMMCP_QMD_URL` | `http://127.0.0.1:8181` | QMD HTTP MCP endpoint |
| `PYSTREAMMCP_QMD_COLLECTIONS` | empty | Comma-separated collection allowlist; required when enabled |
| `PYSTREAMMCP_QMD_TIMEOUT_S` | `10` | Search request timeout |
| `PYSTREAMMCP_QMD_HEALTH_TIMEOUT_S` | `1.5` | Health request timeout |
| `PYSTREAMMCP_QMD_ALLOW_REMOTE` | `false` | Permit non-loopback QMD URLs |
| `PYSTREAMMCP_QMD_TRUST_ENV` | `false` | Allow proxy environment variables for QMD HTTP |

RAG-Anything:

| Variable | Default | Meaning |
|---|---|---|
| `PYSTREAMMCP_RAG_ENABLED` | `false` | Register the RAG backend |
| `PYSTREAMMCP_RAG_WORKING_DIR` | `./rag_storage` | LightRAG storage directory |
| `PYSTREAMMCP_RAG_ALLOWED_ROOTS` | empty | `os.pathsep`-separated ingest roots; required for ingest |
| `PYSTREAMMCP_RAG_ALLOWED_EXTENSIONS` | `.pdf,.png,.jpg,.jpeg,.bmp,.tif,.tiff,.gif,.webp,.txt,.md` | Ingest extension allowlist |
| `PYSTREAMMCP_RAG_PARSER` | `mineru` | `mineru`, `docling`, or `paddleocr` |
| `PYSTREAMMCP_RAG_PARSE_METHOD` | `auto` | `auto`, `ocr`, or `txt` |
| `PYSTREAMMCP_RAG_QUERY_MODE` | `mix` | `mix`, `hybrid`, `local`, `global`, or `naive` |
| `PYSTREAMMCP_RAG_ENABLE_IMAGE_PROCESSING` | `true` | Enable image processing |
| `PYSTREAMMCP_RAG_ENABLE_TABLE_PROCESSING` | `true` | Enable table processing |
| `PYSTREAMMCP_RAG_ENABLE_EQUATION_PROCESSING` | `true` | Enable equation processing |
| `PYSTREAMMCP_RAG_MAX_FILE_MB` | `100` | Per-file size cap |
| `PYSTREAMMCP_RAG_QUERY_TIMEOUT_S` | `60` | Query timeout |
| `PYSTREAMMCP_RAG_INGEST_TIMEOUT_S` | `600` | Ingest timeout |
| `PYSTREAMMCP_RAG_FORCE_MULTIMODAL_REPROCESS` | `false` | Reprocess processed documents |
| `PYSTREAMMCP_RAG_PROVIDER` | `none` | `none` or `openai_compatible` |
| `PYSTREAMMCP_RAG_SOURCE` | `auto` | `auto`, `installed`, or `vendored` |
| `PYSTREAMMCP_RAG_LLM_BASE_URL` | empty | OpenAI-compatible LLM base URL |
| `PYSTREAMMCP_RAG_LLM_API_KEY` | empty | LLM API key |
| `PYSTREAMMCP_RAG_LLM_MODEL` | empty | LLM model |
| `PYSTREAMMCP_RAG_EMBED_BASE_URL` | empty | Embedding base URL |
| `PYSTREAMMCP_RAG_EMBED_API_KEY` | empty | Embedding API key (falls back to LLM key) |
| `PYSTREAMMCP_RAG_EMBED_MODEL` | empty | Embedding model |
| `PYSTREAMMCP_RAG_EMBED_DIM` | empty | Embedding dimension |
| `PYSTREAMMCP_RAG_EMBED_MAX_TOKENS` | `8192` | Embedding token limit |
| `PYSTREAMMCP_RAG_VISION_BASE_URL` | empty | Vision model base URL |
| `PYSTREAMMCP_RAG_VISION_API_KEY` | empty | Vision API key |
| `PYSTREAMMCP_RAG_VISION_MODEL` | empty | Vision model |

`PYSTREAMMCP_RAG_PROVIDER=openai_compatible` requires the LLM model, base URL,
API key, embedding model, embedding base URL, embedding API key, and embedding
dimension; a missing value produces a configuration error. RAG search is
unavailable without a fully configured provider or an injected engine factory.

## Security and privacy

- No auto-install, model download, runtime dependency update, or automatic QMD
  start.
- QMD defaults to loopback; non-loopback URLs require explicit
  `PYSTREAMMCP_QMD_ALLOW_REMOTE=true`. Credentials in URLs are rejected.
- QMD collections are an explicit allowlist. A request may select a subset but
  never a collection outside the allowlist.
- RAG ingestion is limited to configured allowed roots. Path traversal,
  symlinks, unapproved extensions, and oversized files are rejected.
- HTML ingestion is not supported. Markdown with local image references is
  checked before ingestion.
- Remote LLM, embedding, and vision providers receive document text or images
  as part of retrieval/ingestion; this is the only model egress and it is
  opt-in through provider configuration.
- Secrets are not printed in logs or error payloads; upstream-check errors
  redact `GITHUB_TOKEN` and API keys.
- There is no deletion API in this adapter. Ingestion does not remove source
  files.

## Limitations

- RAG page/chunk metadata is best-effort and depends on the parser and
  RAG-Anything version.
- First requests can be slow while an engine or model initializes.
- Default tests are offline and use fake engines/HTTP transports. Live QMD and
  RAG-Anything verification is opt-in and was not run by default in this
  environment.
- QMD is a separate service; this adapter does not supervise or health-manage
  the Node process.
- No cross-backend fusion, calibrated score normalization, or answer
  generation is provided.

## Benchmark

```bash
python benchmarks/retrieval_bench.py --help
python benchmarks/retrieval_bench.py --queries 20 --json
python benchmarks/retrieval_bench.py --qmd-url http://127.0.0.1:8181 --json
```

The benchmark is offline by default and does not modify indexes.
