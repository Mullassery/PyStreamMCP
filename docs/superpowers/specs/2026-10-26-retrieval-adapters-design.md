# Optional Retrieval Backends: QMD and RAG-Anything

- Date: 2026-10-26
- Status: Proposed
- Target repo: `PyStreamMCP`
- Related code: `python/pystreammcp/mcp_server.py`, `_mcp_tools.py`, `api.py`, `cli.py`
- Upstreams: `tobi/qmd` (MIT), `HKUDS/RAG-Anything` (MIT), `HKUDS/LightRAG` (MIT)

## 1. Intent

PyStreamMCP currently has lexical source discovery (`SourceRegistry`'s
Jaccard word overlap) and token-accounting query planning. It has no
semantic retrieval over local knowledge and no document/multimodal
retrieval.

This change adds two optional retrieval backends behind one normalized
service:

1. **QMD** for local full-text, semantic, and hybrid search over indexed
   markdown collections.
2. **RAG-Anything** for parsing and retrieving evidence from PDFs, text,
   images, tables, and equations, including multimodal content where its
   configured parser, model functions, and optional dependencies support
   it.

The core package must remain installable and fully functional without
either upstream. Adding a backend, enabling ingestion, or building the
project must not install a binary, download a model, or call a remote
model by itself.

The three upstream projects are also mirrored into this repository as
pinned, unmodified source snapshots under `vendor/`. The snapshots are a
local fallback for source checkouts, not a runtime update channel. Update
checks are explicit CLI operations and never download or switch code
during a query.

## 2. Goals

- Add one normalized retrieval interface with stable result identifiers,
  source references, excerpts, optional content, scores with explicit
  score semantics, and bounded metadata.
- Integrate QMD through its documented HTTP interface:
  `GET /health`, `POST /query` (alias `/search`).
- Integrate RAG-Anything lazily through an injectable engine factory and
  an optional explicit OpenAI-compatible provider configuration.
- Support ingestion of a single local file into RAG-Anything only when
  allowed roots, supported extensions, size limits, and model provider
  configuration are present.
- Expose retrieval and RAG ingestion through MCP tools and CLI commands.
- Add deterministic backend selection. No LLM is used to route requests.
- Make failures explicit and typed. A configured-but-unavailable
  backend must not silently fall back to another backend.
- Preserve provenance: QMD line references, LightRAG chunk/reference IDs,
  file references, and page metadata when upstream returns it.
- Keep optional dependencies optional and test the core path without
  installing QMD, RAG-Anything, LightRAG, Node, or any model runtime.
- Preserve the upstream sources in-repo: pin QMD, RAG-Anything, and
  LightRAG source snapshots under `vendor/`, verify their checksums, and
  fall back to the vendored RAG/LightRAG source when the installed
  distributions are absent.
- Provide an explicit, read-only `pystreammcp retrieval deps status`
  check that compares pinned versions with upstream tags. It must not
  update, install, or fetch code as part of a query.
- Document security boundaries, model/network egress, cold-start costs,
  and benchmark methodology.

## 3. Non-goals

- Replacing `Agent`, `SourceRegistry`, MCP orchestration, or federation.
- Modifying QMD collections, indexing files into QMD, or exposing QMD's
  collection-management commands.
- Fusing QMD and RAG scores into one ranking. Scores have different
  semantics and are not comparable.
- Generating a synthesized answer with either backend. RAG-Anything's
  answer-generation APIs are not used by the retrieval tool.
- Remote document ingestion, URL ingestion, directory/batch ingestion, or
  deletion in v1.
- Runtime cloning, updating, building, or installing vendored/upstream
  dependencies; only the reviewed maintainer script mutates `vendor/`.
- Automatic package installation, parser installation, model download,
  collection creation, or service startup.
- Automatic runtime dependency updates, runtime downloads, or a runtime
  switch to an upstream Git repository. Vendored snapshots are updated
  only by an explicit maintainer action.
- Vendoring the complete transitive dependency closure. The snapshots
  preserve the three upstream projects' source; their npm/PyPI
  dependencies remain pinned in the extra and lock data.
- A new mandatory dependency for the core package.
- Rest/REST API endpoints for retrieval in v1. MCP and CLI are the
  selected optional surfaces; the library remains the shared
  implementation.

## 4. Constraints and verified upstream facts

### 4.1 Repository constraints

- Core package requires Python >=3.9; current CI covers 3.10, 3.11, 3.12.
- Core dependencies already include `httpx`, `pydantic`, `click`, and
  `rich`; retrieval should not need another mandatory package.
- The MCP server in `mcp_server.py` is synchronous and validates arguments
  with Pydantic v2 models that also generate the advertised JSON schema.
- `PyStreamMCPHandler` in `_mcp_tools.py` is a separate orchestration
  surface. Retrieval tools belong on the protocol-facing
  `PyStreamMCPServer` surface, alongside `pystreammcp_query` and
  `pystreammcp_crawl`.
- The Flask/FastAPI servers are separate surfaces and are not extended in
  v1.
- Baseline before this change: `421 passed, 13 skipped` with the local
  `.venv` on Python 3.12.13.

### 4.2 QMD constraints

Verified from `tobi/qmd` source and README:

- QMD is TypeScript, MIT, published as npm package `@tobilu/qmd`
  (v2.8.3 at design time). It is not a Python library.
- It supports `lex` (BM25/FTS), `vec` (vector), and `hyde` typed
  sub-queries, with optional reranking. It runs local GGUF models via
  node-llama-cpp; the first use may download models.
- HTTP mode is `qmd mcp --http`, default `localhost:8181`.
- Endpoints: `POST /query` (alias `/search`), `POST /metadata`,
  `POST /mcp`, `GET /health`.
- `POST /query` requires `searches: [{type: "lex"|"vec"|"hyde", query}]`.
  Other fields: `collections` (array only), `limit`, `minScore`,
  `rerank`, `intent`, `candidateLimit`, `filter`.
- Responses are `{"results": [...]}`. Each result has `docid`, `file`
  (`qmd://...`), `title`, `score`, `context`, optional `metadata`,
  `line`, `snippet`.
- The HTTP server is unauthenticated. It binds to loopback by default and
  screens `Origin`/`Host`; non-loopback binding requires the operator to
  provide an auth proxy. Its query score is a blended/reranked relevance
  score, not a cross-engine probability.

### 4.3 RAG-Anything / LightRAG constraints

Verified from `HKUDS/RAG-Anything` and `HKUDS/LightRAG` source/README:

- `raganything` 1.4.3 is MIT and requires Python >=3.10.
- Required dependencies include `huggingface_hub`, `lightrag-hku<1.5`,
  `mineru[core]>=3.4.1`, and `tqdm`.
- Optional extras exist for image, text, office (external LibreOffice),
  PaddleOCR, Markdown, audio, and video. First use may download models.
- `RAGAnything` accepts an optional pre-initialized `LightRAG` instance.
  Creating/initializing `LightRAG` requires an LLM function and embedding
  function; vision is optional.
- Document parsing/ingestion uses
  `process_document_complete(file_path, doc_id=..., file_name=...)`.
  Existing processed documents are skipped; `force_multimodal_reprocess`
  only re-runs multimodal processing, not text reindexing.
- Text queries through `RAGAnything.aquery()` return an answer/context
  string, not structured evidence.
- Structured retrieval is available on the LightRAG instance via
  `aquery_data(query, QueryParam(...))`, which returns entities,
  relationships, chunks, references, and processing metadata. Chunks carry
  `content`, `file_path`, `chunk_id`, and `reference_id`.
- RAG-Anything annotates text chunks with `page_idx`/`page_idx_end` when
  its parser can map pages. `aquery_data` does not return those fields
  directly, so the adapter will attempt an optional enrichment from the
  LightRAG text-chunk store and omit page data when unavailable.
- Some parse paths have security implications: HTML/Docling can fetch
  remote URLs, and Markdown image references can cause arbitrary local
  image reads. Both require explicit handling.
- Deletion exists in LightRAG (`adelete_by_doc_id`) but RAG-Anything has no
  documented cross-store delete contract. Deletion is therefore not in
  v1.

### 4.4 Vendoring constraints

The in-repo snapshots are pinned as follows at design time:

| Component | Upstream | Tag | Commit | License |
|---|---|---|---|---|
| QMD | `tobi/qmd` | `v2.8.3` | `facd35e01359e59d938bc9418e93fb9318addee3` | MIT |
| RAG-Anything | `HKUDS/RAG-Anything` | `v1.4.3` | `afb67c43d391b1b1008a6fee9f020a232067b9e5` | MIT |
| LightRAG | `HKUDS/LightRAG` | `v1.4.16` | `964f26e9a9239c1316045913328e863ec35492e4` | MIT |

- Snapshots contain the upstream tracked files, including `LICENSE`, but
  no `.git` directory, submodules, symlinks, or generated dependency
  trees.
- LightRAG `v1.4.16` is the newest 1.4.x tag compatible with
  RAG-Anything's `lightrag-hku<1.5` constraint at design time.
- RAG-Anything still requires Python >=3.10 and its transitive packages
  (`mineru`, `huggingface_hub`, etc.) from PyPI. QMD still requires Node
  and its npm dependency tree. Vendoring preserves source availability;
  it does not create a hermetic offline runtime.
- The source snapshots are repository assets. They are not included in
  the built wheel and are not importable from an installed wheel.
- No upstream file is modified in v1. If a patch becomes necessary, it
  must be a separate reviewed patch with an updated tree checksum and an
  entry in `vendor/README.md`.
- The repository stores SHA-256 tree checksums for each snapshot so an
  accidental or malicious local edit is detectable without network
  access.

## 5. Approaches considered

### 5.1 Integration shape

**A. In-process adapters (chosen).** QMD is reached over its local HTTP
API. RAG-Anything is imported lazily and operated on a dedicated worker
thread/event loop. This fits the synchronous MCP server, avoids inventing
a new service, and keeps tests independent of heavy dependencies.

**B. Separate RAG sidecar.** Better isolation for heavy parsers and model
runtimes, but adds a second deployable process, health/lifecycle
management, IPC, auth, packaging, and failure modes not present in the
repo today. Rejected for v1.

**C. QMD first, RAG later.** Lower risk but does not meet the multimodal
document requirement and leaves the normalized abstraction untested
against the harder backend. Rejected.

### 5.2 QMD transport

**HTTP (chosen).** Official structured endpoint; no subprocess, no shell,
no Node argument parsing, and a health endpoint. Requires the operator to
run `qmd mcp --http`.

**CLI subprocess.** Avoids a daemon but requires spawning Node, parsing
CLI output, timeout/process-group handling, and a larger security surface.
Rejected for v1. The adapter interface leaves room for a future CLI
transport without changing callers.

### 5.3 RAG model configuration

**Factory plus explicit OpenAI-compatible config (chosen).** Library
users can inject any prebuilt engine. The built-in factory supports
OpenAI-compatible LLM, embedding, and optional vision endpoints using
documented LightRAG helpers. This makes the feature usable from MCP/CLI
without inventing a provider abstraction, while keeping tests fake-based.

**Injected factory only.** Purest, but MCP/CLI users would have to write
Python to use RAG. Rejected.

**OpenAI-compatible config only.** Simpler but prevents local/custom
stacks and makes deterministic tests less clean. Rejected.

### 5.4 Dependency source

**A. Pinned source snapshots under `vendor/` (chosen).** All three
projects are copied from exact upstream tags and verified by checksum.
Installed Python packages remain the preferred runtime source; the
snapshots provide a consistent fallback if the upstream source or package
is unavailable. Update checks are explicit and read-only.

**B. Git submodules.** Less copying, but submodule checkout depends on
network/access and can silently leave an empty or partial tree. Rejected.

**C. Vendored wheels or npm tarballs.** Better offline installation, but
the wheel/sdist would need platform-specific dependency trees and would
not preserve readable source for emergency QMD rebuilds. Rejected for v1.

## 6. Architecture

### 6.1 New package

```text
python/pystreammcp/retrieval/
├── __init__.py          # public service/models/backends
├── base.py              # backend protocols and shared request types
├── cli.py               # `pystreammcp retrieval ...` Click group
├── config.py            # env-backed dataclass configuration
├── deps.py              # vendored source resolution and update checks
├── errors.py            # RetrievalError, codes, serialization
├── models.py            # normalized dataclasses/enums
├── providers.py         # OpenAI-compatible RAG engine factory
├── qmd.py               # QMD HTTP adapter
├── rag_anything.py      # lazy RAG-Anything adapter + worker loop
├── router.py            # deterministic backend selection
├── security.py          # path/extension/markdown guards, redaction
└── service.py           # orchestration, grouping, time budgets
```

No module in this package may import `raganything`, `lightrag`, or any
model SDK at import time. `httpx` is already a core dependency.

### 6.2 Core types

`models.py` defines JSON-serializable dataclasses/enums. All public
results are converted to plain dictionaries at the MCP/CLI boundary.

```python
class BackendName(str, Enum):
    QMD = "qmd"
    RAG_ANYTHING = "rag_anything"

class RequestedBackend(str, Enum):
    AUTO = "auto"
    QMD = "qmd"
    RAG_ANYTHING = "rag_anything"
    ALL = "all"

@dataclass(frozen=True)
class RetrievalRequest:
    query: str
    backend: RequestedBackend = RequestedBackend.AUTO
    mode: str | None = None
    collections: tuple[str, ...] = ()
    content_type: str | None = None
    limit: int = 5
    include_content: bool = False
    max_content_chars: int = 2000
    time_budget_ms: int = 30000
    intent: str | None = None

@dataclass(frozen=True)
class RetrievalHit:
    backend: BackendName
    rank: int
    document_id: str | None
    title: str | None
    source_uri: str
    locator: dict[str, Any]
    excerpt: str
    content: str | None
    score: float | None
    score_kind: str
    metadata: dict[str, Any]

@dataclass
class BackendGroup:
    backend: BackendName
    status: str              # ok | error | timeout | unavailable
    hits: list[RetrievalHit]
    error: dict[str, Any] | None
    elapsed_ms: int
    truncated: bool

@dataclass
class RetrievalResponse:
    status: str              # success | partial | error
    query: str
    backend_requested: str
    groups: list[BackendGroup]
    diagnostics: dict[str, Any]
```

`score_kind` is mandatory and descriptive, for example
`qmd_query_relevance` or `unavailable`. No cross-backend normalization or
fusion is performed. A missing RAG score is `None`, not a fabricated rank
score.

`source_uri` is a stable display reference:

- QMD: the upstream `qmd://collection/path` URI.
- RAG: `rag://<root-relative display path>`; absolute filesystem paths are
  not returned.

`locator` is structured:

- QMD: `{"kind": "line", "line": <int>}`.
- RAG: `{"kind": "chunk", "chunk_id": ..., "reference_id": ...,
  "page": ...}`; page keys appear only when available.

`metadata` is shallow, JSON-safe, size-bounded, and never includes API
keys, parser command lines, or absolute paths outside allowed roots.

### 6.3 Errors

`errors.py` defines `RetrievalError(code, message, backend=None,
retryable=False, details=None)` and stable codes:

`configuration_error`, `not_configured`, `unavailable`,
`missing_dependency`, `invalid_request`, `invalid_backend`, `unsupported_mode`,
`unsupported_content_type`, `collection_not_allowed`,
`collection_required`, `timeout`, `http_error`, `invalid_response`,
`path_outside_allowed_roots`, `symlink_not_allowed`,
`unsupported_extension`, `file_too_large`, `not_a_file`, `ingest_failed`,
`index_not_initialized`, `query_failed`, `upstream_unsupported_version`,
`no_available_backend`, `closed`.

Backend failures are returned as structured data. The MCP dispatcher still
has its existing outer exception isolation. Error text is bounded to
approximately 500 characters and is redacted for URL userinfo and
configured secrets.

Retryability and MCP mapping:

| Code family | Retryable | MCP behavior |
|---|---|---|
| `timeout` | yes | group `timeout`; top-level `partial` if another group succeeded |
| `unavailable` (connection/5xx) | yes | group `unavailable`; explicit backend call returns error |
| `invalid_response`, `http_error` 4xx | no | group `error`; bounded upstream message |
| `invalid_request`, `unsupported_mode`, `unsupported_content_type`, `collection_not_allowed`, `collection_required`, `invalid_backend` | no | top-level error before backend execution |
| `path_outside_allowed_roots`, `symlink_not_allowed`, `unsupported_extension`, `file_too_large`, `not_a_file` | no | top-level error from `pystreammcp_rag_ingest` |
| `index_not_initialized` | no | error with "ingest a document or inject a pre-initialized engine" hint |
| `configuration_error`, `missing_dependency`, `not_configured` | no | unavailable capability and actionable error |
| `no_available_backend` | no | top-level error with skipped-backend diagnostics |
| `ingest_failed`, `query_failed` | no by default | error; caller may retry explicitly |
| `closed` | no | error |

There is no automatic retry or circuit breaker in v1. Existing MCP
resilience behavior is unchanged: expected retrieval failures are typed
results, while unexpected exceptions still fall through the server's
existing outer catch and return a structured `error_type` response.

### 6.4 Configuration

`config.py` uses dataclasses and explicit validation. Invalid individual
backend configuration does not crash the process; the backend is
registered as configured-but-unavailable with a `configuration_error`,
so capabilities can explain it and explicit calls fail clearly.

All settings are environment-based. Prefix: `PYSTREAMMCP_`.

QMD:

```text
PYSTREAMMCP_QMD_ENABLED=false
PYSTREAMMCP_QMD_URL=http://127.0.0.1:8181
PYSTREAMMCP_QMD_COLLECTIONS=notes,docs       # required when enabled
PYSTREAMMCP_QMD_TIMEOUT_S=10
PYSTREAMMCP_QMD_HEALTH_TIMEOUT_S=1.5
PYSTREAMMCP_QMD_ALLOW_REMOTE=false
PYSTREAMMCP_QMD_TRUST_ENV=false
```

- QMD collections are an explicit allowlist. Empty allowlist is a
  configuration error when QMD is enabled.
- A request may select a subset of the allowlist but never a collection
  outside it.
- Non-loopback URLs require `PYSTREAMMCP_QMD_ALLOW_REMOTE=true`; no
  credentials are accepted in the URL.
- `trust_env=false` by default avoids proxy environment variables routing
  localhost traffic unexpectedly.

RAG-Anything:

```text
PYSTREAMMCP_RAG_ENABLED=false
PYSTREAMMCP_RAG_WORKING_DIR=./rag_storage
PYSTREAMMCP_RAG_ALLOWED_ROOTS=                 # os.pathsep-separated; required for ingest
PYSTREAMMCP_RAG_ALLOWED_EXTENSIONS=.pdf,.png,.jpg,.jpeg,.bmp,.tif,.tiff,.gif,.webp,.txt,.md
PYSTREAMMCP_RAG_PARSER=mineru                  # mineru | docling | paddleocr
PYSTREAMMCP_RAG_PARSE_METHOD=auto              # auto | ocr | txt
PYSTREAMMCP_RAG_QUERY_MODE=mix                 # mix | hybrid | local | global | naive
PYSTREAMMCP_RAG_ENABLE_IMAGE_PROCESSING=true
PYSTREAMMCP_RAG_ENABLE_TABLE_PROCESSING=true
PYSTREAMMCP_RAG_ENABLE_EQUATION_PROCESSING=true
PYSTREAMMCP_RAG_MAX_FILE_MB=100
PYSTREAMMCP_RAG_QUERY_TIMEOUT_S=60
PYSTREAMMCP_RAG_INGEST_TIMEOUT_S=600
PYSTREAMMCP_RAG_FORCE_MULTIMODAL_REPROCESS=false
PYSTREAMMCP_RAG_PROVIDER=none                  # none | openai_compatible
PYSTREAMMCP_RAG_SOURCE=auto                    # auto | installed | vendored
PYSTREAMMCP_RAG_LLM_BASE_URL=
PYSTREAMMCP_RAG_LLM_API_KEY=
PYSTREAMMCP_RAG_LLM_MODEL=
PYSTREAMMCP_RAG_EMBED_BASE_URL=
PYSTREAMMCP_RAG_EMBED_API_KEY=
PYSTREAMMCP_RAG_EMBED_MODEL=
PYSTREAMMCP_RAG_EMBED_DIM=
PYSTREAMMCP_RAG_EMBED_MAX_TOKENS=8192
PYSTREAMMCP_RAG_VISION_BASE_URL=
PYSTREAMMCP_RAG_VISION_API_KEY=
PYSTREAMMCP_RAG_VISION_MODEL=
```

Rules:

- RAG is query-unavailable unless an engine factory is injected or
  `PYSTREAMMCP_RAG_PROVIDER=openai_compatible` is fully configured.
- `PYSTREAMMCP_RAG_SOURCE` controls dependency resolution:
  - `auto` (default) uses the installed `raganything` and `lightrag`
    distributions only when both are importable; otherwise it uses both
    vendored snapshots; otherwise RAG is unavailable with
    `missing_dependency`.
  - `installed` requires both installed distributions and never adds the
    vendored paths.
  - `vendored` requires both vendored snapshots and never imports the
    installed distributions.
  - The selected source is reported in RAG diagnostics as
    `dependency_source` (`installed`, `vendored`, or `injected`) and
    `dependency_version` when known.
  - The vendored paths are fixed package-relative paths. No environment
    variable, current directory, or caller-provided path may add an
    arbitrary `sys.path` entry.
- Image processing is advertised only when a vision model is configured.
- Ingestion is unavailable unless at least one allowed root is configured.
- `.html`, `.htm`, and `.xhtml` are rejected unconditionally in v1 because
  the upstream Docling path can fetch remote URLs.
- Allowed roots are resolved once at configuration time. A candidate is
  also resolved and checked again before use.
- `working_dir` is state, not an allowed document root. It is created only
  when RAG is configured.
- Secrets are never included in capabilities, errors, or logs.

#### Configuration precedence and sources

There is no retrieval config file and no dynamic plugin/entry-point
discovery in v1.

1. Library callers may pass explicit config dataclasses or a prebuilt
   `RetrievalService`. Injected objects win completely; no environment
   values are merged into them.
2. Otherwise, `RetrievalService.from_env()` reads the environment once.
   MCP lazy construction uses this path; CLI commands call it per
   invocation.
3. Defaults apply only to omitted environment values.
4. CLI flags are request options only (`--backend`, `--mode`, etc.).
   There are intentionally no CLI flags for provider API keys or allowed
   roots; secrets and security boundaries come from the environment or an
   injected service.
5. Only the two built-in backends are registered. Third-party backends may
   be passed directly to `RetrievalService(backends=[...])` for embedding
   or tests, but there are no Python entry points, namespace scanning, or
   dynamic imports for adapters.

### 6.5 Backend protocol

`base.py` defines concrete, synchronous protocol types. Backends do not
return MCP envelopes; they raise `RetrievalError` for expected failures
and the service converts those into result groups.

```python
@dataclass(frozen=True)
class BackendSearchRequest:
    query: str
    mode: str | None
    collections: tuple[str, ...]
    content_type: str | None
    limit: int
    include_content: bool
    max_content_chars: int
    timeout_s: float
    intent: str | None

@dataclass
class BackendSearchResult:
    hits: list[RetrievalHit]
    truncated: bool
    diagnostics: dict[str, Any]

@dataclass(frozen=True)
class BackendCapabilities:
    backend: BackendName
    enabled: bool
    configured: bool
    available: bool              # structural/config availability, no model load
    modes: tuple[str, ...]
    content_types: tuple[str, ...]
    max_limit: int
    supports_ingestion: bool
    supports_full_content: bool
    score_kind: str
    network_egress: str          # local | remote | unknown
    error: dict[str, Any] | None

@dataclass(frozen=True)
class BackendHealth:
    backend: BackendName
    available: bool
    status: str                  # ok | unavailable | error
    message: str | None
    elapsed_ms: int

@dataclass(frozen=True)
class IngestionResult:
    document_id: str
    display_path: str
    status: str
    skipped: bool
    elapsed_ms: int
    content_types: tuple[str, ...]

class RetrievalBackend(Protocol):
    name: BackendName
    def capabilities(self) -> BackendCapabilities: ...
    def health(self) -> BackendHealth: ...
    def search(self, request: BackendSearchRequest) -> BackendSearchResult: ...
    def close(self) -> None: ...

class IngestingBackend(RetrievalBackend, Protocol):
    def ingest(self, path: str, force_multimodal: bool = False) -> IngestionResult: ...
```

- All backend methods are synchronous from the service's perspective.
  RAG-Anything performs async work on its private worker loop.
- `capabilities()` performs no network I/O and loads no models. QMD
  availability there is structural/config-level; `health()` performs the
  `GET /health` check.
- `search()` and `ingest()` may raise `RetrievalError`; the service catches
  those into groups/results. Unexpected exceptions are caught at the
  service and MCP boundaries.
- `timeout_s` is computed by the service per backend from its configured
  timeout and the request's remaining budget.
- `BackendSearchRequest` carries only backend-relevant normalized fields.
  The service is responsible for routing and grouping.

### 6.6 Deterministic router

`router.py` is pure and independently testable. Inputs: request, backend
registry, configured priority. Output: selected backend names plus
diagnostics. No network calls.

Rules:

1. Explicit `qmd` or `rag_anything` selects exactly that backend. If it is
   disabled or unavailable, return a typed error; never substitute another
   backend.
2. `all` selects every enabled backend, including configured-but-
   unavailable ones so their status is visible in the grouped response.
3. `auto` chooses one backend:
   - If `collections` is non-empty, QMD is required.
   - If `content_type` is non-text (`image`, `table`, `equation`,
     `document`, `pdf`, `audio`, `video`), choose a backend that advertises
     that capability; prefer RAG-Anything.
   - If `mode` is supported by exactly one available backend, choose it.
   - Otherwise choose the first available backend in configured priority
     (`qmd`, then `rag_anything` by default).
4. If no backend is available, return `no_available_backend`.
5. Unavailable backends skipped by `auto` are listed in diagnostics with
   their reasons. This is explicit, not a silent fallback.

### 6.7 Service

`service.py` owns backend instances, router, and a bounded thread pool for
cross-backend fan-out.

- `RetrievalService.from_env()` constructs configured backends. Individual
  configuration errors become unavailable backends.
- `search(request)` validates request-level limits, routes, and runs one
  or more backends. Multiple backends run concurrently.
- Each group has its own backend timeout. The service waits up to the
  request's `time_budget_ms`; unfinished groups become `timeout`.
- Backend exceptions are caught and converted to group errors. One failed
  backend does not prevent other groups from returning.
- Top-level status: `success` if all selected groups are `ok`;
  `partial` if at least one is `ok` and another is not; `error` if none is
  `ok`.
- No merging or re-ranking across groups.
- `capabilities()` returns configured, enabled, available, modes, content
  types, limits, ingestion support, score semantics, and network-egress
  disclosure. QMD availability may be checked via `/health`; RAG
  availability is based on dependency/config/engine state without loading
  model weights.
- `ingest(path, force_multimodal)` requires exactly one RAG backend and
  delegates to its guarded ingestion path.
- `close()` closes backends and the thread pool. The service is safe to
  use after a failed search.

### 6.8 QMD adapter

`qmd.py` implements `RetrievalBackend` over `httpx.Client`.

Modes:

| Normalized mode | QMD request |
|---|---|
| `auto` (default) / `hybrid` | `searches=[lex, vec]`, `rerank=true` |
| `keyword` / `lex` / `full_text` | `searches=[lex]`, `rerank=false` |
| `semantic` / `vec` / `vector` | `searches=[vec]`, `rerank=false` |
| `hyde` | `searches=[hyde]`, `rerank=false` |

- `auto` deliberately uses typed `lex` + `vec` rather than QMD's plain
  `query` auto-expansion, so the request is deterministic and does not
  introduce an extra undocumented expansion step.
- Search always sends the configured allowlist or a validated subset.
- `limit` is clamped by the service to 1..50.
- `intent` is passed through when supplied.
- Response parsing validates `results` is a list and each item is an
  object. `snippet` is the excerpt. `content` is the same bounded snippet:
  QMD's REST surface does not expose full document content, so capability
  metadata says `full_content=false`.
- `metadata` contains only selected scalar fields: `docid`, `context`,
  `line`, and any upstream metadata values that are JSON scalars/flat
  arrays. Values are size-bounded.
- HTTP 400 -> `invalid_response`/`http_error` with a bounded message;
  403 -> `unavailable` with origin/host hint; 404 -> `unavailable`; 5xx ->
  `unavailable`; timeout -> `timeout`; connection failure -> `unavailable`.
- Health uses `GET /health` with a short timeout and no secret leakage.
- The adapter never creates collections, indexes files, or shells out.

### 6.9 RAG-Anything adapter

`rag_anything.py` implements `RetrievalBackend` and `IngestingBackend`.

#### Lazy engine and worker loop

- The adapter resolves `raganything` and `lightrag` through
  `deps.resolve_rag_source()` according to
  `PYSTREAMMCP_RAG_SOURCE`. Resolution uses `importlib.util.find_spec`
  and the fixed vendored paths; it does not import either package at
  module import time.
- `auto` prefers a consistent installed pair. If either distribution is
  absent, it prepends both vendored source roots so a consistent vendored
  pair is used instead of a mixed-version pair. `installed` and
  `vendored` are strict.
- If the selected source's transitive dependencies are missing, the
  import failure becomes `missing_dependency` with an install hint; there
  is no auto-install.
- Engine construction happens inside a dedicated daemon worker thread with
  its own asyncio event loop. All RAG operations are serialized with a
  lock. This prevents a synchronous MCP caller from creating per-call
  event loops and prevents concurrent ingestion/query on shared stores.
- `engine_factory` is optional and may be sync or async. It returns an
  object implementing the used RAG-Anything surface. An injected factory
  bypasses dependency resolution and reports
  `dependency_source="injected"`.
- If no factory is provided, `providers.py` builds the
  OpenAI-compatible engine. It calls
  `deps.ensure_rag_import_path()` before importing upstream modules.
- `close()` finalizes storages when the engine supports it, stops the
  loop, and joins the thread with a timeout. It is idempotent.
- A closed adapter returns `closed` errors.

#### Built-in OpenAI-compatible factory

`providers.py` uses documented LightRAG helpers:

- `lightrag.llm.openai.openai_complete_if_cache` for text completion.
- `lightrag.utils.EmbeddingFunc` with `openai_embed.func` and the required
  explicit embedding dimension.
- A vision function following the upstream RAG-Anything pattern, using
  `raganything.image_signature.image_mime_type` for the data URI media type.
- A pre-initialized `LightRAG(working_dir=..., llm_model_func=...,
  embedding_func=...)`, followed by `initialize_storages()` and
  `initialize_pipeline_status()`, then `RAGAnything(config=...,
  lightrag=lightrag, vision_model_func=...)`.
- The `rag-anything` extra installs `raganything>=1.4.3,<1.5` and
  `openai>=2.0,<4.0`, gated to Python >=3.10. Operators may install
  `raganything[text]` or other extras separately for additional formats.
- No provider call is made during configuration, health, or capabilities.
  Only explicit query/ingestion triggers network calls.
- Egress disclosure: capabilities mark `network_egress` as `local` when
  configured hosts are loopback, otherwise `remote`. Document content is
  sent only when the operator explicitly ingests or queries.

#### Ingestion

`ingest(path, force_multimodal=False)`:

1. Require RAG enabled and an engine/provider configured.
2. Resolve the configured roots and candidate path with `strict=True`.
3. Reject non-files, symlinks, symlinked path components, files outside
   every allowed root, unsupported extensions, HTML, and files over the
   configured size limit.
4. For Markdown, scan local image references. Any existing local image
   that resolves outside allowed roots causes rejection. Remote URLs are
   left to upstream as plain text; no fetch is performed by this adapter.
5. Compute a content hash and a stable `doc_id`:
   `pystreammcp-<first 32 hex chars of sha256(file bytes)>`.
6. Derive a safe `display_path` from the root-relative path (prefixed by
   the configured root's name if roots could collide). Pass it as
   `file_name` so LightRAG stores a relative reference rather than an
   absolute filesystem path.
7. If the engine is already initialized and doc status says processed,
   return `skipped=true` with the existing status unless
   `force_multimodal` is set.
8. Call `process_document_complete(file_path=<resolved path>,
   file_name=<display path>, doc_id=<hash id>,
   force_multimodal_reprocess=force_multimodal)` with the configured
   parser/parse method/output directory, bounded by the ingestion timeout.
9. Read and normalize doc status. Return `document_id`, `display_path`,
   `status`, `skipped`, `elapsed_ms`, and supported content flags.
10. Upstream failures are mapped to `ingest_failed` or `timeout`. A timeout
    explicitly says the upstream operation may still be running; no
    rollback or deletion is attempted.
11. No automatic retry. The caller may retry explicitly with the same
    content; the stable doc ID and upstream processing status provide
    idempotency.

#### Query

`search()`:

1. Require an initialized engine. If `rag.lightrag` is absent, return
   `index_not_initialized` with a hint to ingest a document or inject a
   pre-initialized engine. There is no fallback to answer generation.
2. Validate the requested mode against RAG's modes:
   `auto`, `hybrid`, `local`, `global`, `naive`, `mix`. `auto` maps to the
   configured query mode (`mix` by default). QMD-only modes such as
   `keyword`, `lex`, `vec`, `hyde` are unsupported for this backend.
3. Build LightRAG `QueryParam(mode=..., top_k=limit,
   chunk_top_k=limit)`. Pass `enable_rerank` from config only if the
   configured upstream version supports it; otherwise omit it.
4. Call the documented `aquery_data(query, param)` on the LightRAG
   instance. This is structured retrieval without answer generation.
5. Validate `status == "success"` and the `data.chunks` list. If the
   upstream returns no chunks, return an empty successful result with
   counts in diagnostics.
6. Optionally enrich chunks by reading the LightRAG text-chunk store with
   `get_by_ids` and extracting `page_idx`, `page_idx_end`, and
   `full_doc_id`. Enrichment failure is non-fatal and page data is simply
   omitted.
7. Map each chunk to one `RetrievalHit`:
   - `document_id` = `full_doc_id` when available, otherwise `doc_id` from
     the chunk store, otherwise `None`.
   - `source_uri` = `rag://` + URL-quoted relative `file_path`.
   - `title` = final basename of `file_path` without extension.
   - `locator` includes `chunk_id`, `reference_id`, and `page` when
     available.
   - `excerpt` = whitespace-normalized first 500 characters.
   - `content` = full chunk content when `include_content=true`, truncated
     to `max_content_chars`.
   - `score` = `None`; `score_kind = "unavailable"`.
   - `metadata` contains only `reference_id`, `chunk_id`, `page`, and
     `page_end` when available.
8. Errors: missing LightRAG -> `index_not_initialized`; missing
   `aquery_data` -> `upstream_unsupported_version`; upstream exception ->
   `query_failed`; timeout -> `timeout`.
9. Diagnostics include `dependency_source`, `dependency_version` when
   known, mode, chunk count, and page-enrichment status. They never include
   absolute vendored paths or secrets.

#### Capabilities

RAG capabilities report:

- dependency installed/configured/available
- parser and parse method
- query modes
- ingest extensions/roots count (not the roots themselves)
- content types: text always; image only when vision is configured and
  image processing enabled; table/equation based on processing flags
- `full_content=true`
- `score_kind="unavailable"`
- `network_egress="local"|"remote"`
- ingestion support and limits
- actionable error/status text when unavailable

### 6.10 MCP integration

`mcp_server.py` gains three Pydantic v2 argument models and tools:

1. `pystreammcp_retrieval_search`
   - query, backend (`auto|qmd|rag_anything|all`), mode, collections,
     content_type, limit, include_content, max_content_chars,
     time_budget_ms, intent.
   - Bounds: query 1..8000 chars; limit 1..50; content 0..20000 chars;
     budget 1..300000 ms; collections max 32 entries; intent max 1000.
2. `pystreammcp_retrieval_capabilities`
   - optional `include_health` (default true).
   - Returns backend capabilities/health; never loads RAG weights.
3. `pystreammcp_rag_ingest`
   - path, force_multimodal.
   - Only available when RAG ingestion is configured. Enforces all path
     guards. This is a mutating tool and is therefore gated by environment
     configuration, not merely by the presence of the tool.

`PyStreamMCPServer.__init__` accepts an optional `RetrievalService` for
tests and embedding. Without one, it lazily constructs
`RetrievalService.from_env()` on first retrieval call. The service is
cached. Existing tools and message types are unchanged. `get_info`
advertises retrieval capability names only when configured.

Wiring is explicit, matching the existing server style:

- Add the three argument models to `_TOOL_ARG_MODELS`.
- Add three `MCPTool` entries to `_define_tools()`, so `get_tools()` and
  the advertised Pydantic schemas stay in lockstep.
- Add three dispatch entries to `call_tool()` and three handler methods on
  `PyStreamMCPServer`.
- Add `_get_retrieval_service()` for lazy construction and an optional
  `close()` that closes an injected/created service.
- Do not add MCP resources. The current server has no resource
  abstraction; tools are the only surface being extended.
- Do not change `_mcp_tools.py`; that is the separate orchestration
  handler.
- Existing auth (`PYSTREAMMCP_API_KEY` check before dispatch), validation
  error shape, and outer exception handling remain untouched.

MCP responses:

- Success: `{"status": "success", "query": ..., "backend_requested":
  ..., "groups": [...], "diagnostics": ...}`.
- Partial: same shape with top-level `"partial"`.
- Error: `{"status": "error", "error_type": "RetrievalError", "code":
  ..., "message": ..., "backend": ..., "retryable": ...}`.
- Validation errors continue to use the existing structured
  `validation_errors` response.

### 6.11 CLI integration

`cli.py` mounts the retrieval Click group. Commands:

```text
pystreammcp retrieval search QUERY [--backend ...] [--mode ...]
    [--collection NAME ...] [--content-type ...] [--limit N]
    [--include-content] [--max-content-chars N] [--time-budget-ms N]
    [--intent TEXT] [--json]
pystreammcp retrieval capabilities [--no-health] [--json]
pystreammcp retrieval health [--json]
pystreammcp retrieval ingest PATH [--force-multimodal] [--json]
pystreammcp retrieval deps status [--offline] [--json]
```

- JSON mode prints a single JSON object and exits 0 on success, 1 on
  error/partial, so scripts can detect degradations.
- `deps status` verifies the vendored tree checksums offline. Unless
  `--offline` is set, it also compares pinned tags with upstream GitHub
  tags. Exit codes: 0 all pinned/current, 1 update available, 2
  verification or update-check failure. It never updates or downloads
  code.
- Human mode prints a compact per-backend summary and source references.
- CLI errors are actionable but redacted. No stack traces unless
  `PYSTREAMMCP_DEBUG=1`, consistent with existing behavior.

### 6.12 Optional live tests

Live tests are skipped unless explicitly enabled:

- `PYSTREAMMCP_TEST_QMD_URL` and `PYSTREAMMCP_TEST_QMD_COLLECTION` run a
  real QMD query and health check.
- `PYSTREAMMCP_TEST_RAG=1` plus the normal RAG environment runs one real
  ingest/query against a configured engine. This is operator-driven and
  never part of default CI.
- Contract tests use `httpx.MockTransport` with a captured QMD v2.8.x
  response shape and fake RAG engines. They do not install or start
  upstream services.

### 6.13 Vendored dependencies and update checks

The repository vendors the three upstream projects before adapter code
is written. Layout:

```text
vendor/
├── README.md                 # attribution, pins, update procedure, caveats
├── deps.lock.json            # machine-readable pins and tree checksums
├── qmd/                      # tobi/qmd v2.8.3 tracked files, no .git
├── rag-anything/             # HKUDS/RAG-Anything v1.4.3 tracked files
└── lightrag/                 # HKUDS/LightRAG v1.4.16 tracked files
scripts/
└── vendor_dependencies.py    # maintainer-only vendor/update/verify tool
```

`vendor/deps.lock.json` has this shape. The paths are repository-relative
and are never accepted from the environment.

```json
{
  "schema": 1,
  "dependencies": {
    "qmd": {
      "repo": "https://github.com/tobi/qmd.git",
      "tag": "v2.8.3",
      "commit": "facd35e01359e59d938bc9418e93fb9318addee3",
      "path": "vendor/qmd",
      "ecosystem": "npm",
      "license": "MIT",
      "tree_sha256": "<hex>"
    },
    "rag-anything": {
      "repo": "https://github.com/HKUDS/RAG-Anything.git",
      "tag": "v1.4.3",
      "commit": "afb67c43d391b1b1008a6fee9f020a232067b9e5",
      "path": "vendor/rag-anything",
      "ecosystem": "python",
      "license": "MIT",
      "tree_sha256": "<hex>"
    },
    "lightrag": {
      "repo": "https://github.com/HKUDS/LightRAG.git",
      "tag": "v1.4.16",
      "commit": "964f26e9a9239c1316045913328e863ec35492e4",
      "path": "vendor/lightrag",
      "ecosystem": "python",
      "license": "MIT",
      "tree_sha256": "<hex>"
    }
  }
}
```

#### Tree checksums

`tree_sha256` is SHA-256 over a canonical UTF-8 JSON array of
`[relative_posix_path, sha256_of_file_bytes]` pairs, sorted by path, with
no extra whitespace. It excludes `.git`, `__pycache__`, `.pytest_cache`,
`.ruff_cache`, `node_modules`, `dist`, `build`, and compiled Python files;
symlinks are rejected rather than hashed. The maintainer script computes
and verifies this; tests recompute it offline.

#### RAG source resolution

`deps.py` provides a read-only `resolve_rag_source(mode, injected=False)`
and a guarded `ensure_rag_import_path(mode)`. Resolution uses
`importlib.util.find_spec` and checks the two fixed paths
`vendor/rag-anything` and `vendor/lightrag` (located relative to the
repository root). It never consults the current working directory, an
environment path list, or a caller-provided directory.

- `auto`: if both installed `raganything` and `lightrag` are importable,
  use `installed`. Otherwise, if both vendored snapshots exist, prepend
  both vendored roots to `sys.path` and use `vendored`. Otherwise RAG is
  unavailable with `missing_dependency`.
- `installed`: require both installed distributions; never add vendored
  paths.
- `vendored`: require both vendored snapshots; never use installed
  distributions, even if present.
- `injected=True` bypasses all dependency resolution and reports
  `dependency_source="injected"`.
- A vendored import that fails because of a missing transitive package is
  `missing_dependency` with a `pip install 'pystreammcp[rag-anything]'`
  hint. There is no auto-install and no partial mixed pair.
- Path insertion happens under a process-wide lock, is idempotent, and is
  limited to the two resolved roots. Symlinked or missing vendor roots
  are rejected.
- In an installed wheel the vendor directory is absent, so `auto`
  resolves to `installed`; `vendored` is unavailable. Vendoring is a
  source-repository guarantee, not a wheel feature.

#### Update checks

`pystreammcp retrieval deps status` is the only adapter-adjacent update
lookup. It is read-only and explicit:

1. Load the lock and verify every vendored tree checksum locally. A
   mismatch or missing tree is `corrupt`/`missing` and exit code 2.
2. Unless `--offline`, query the GitHub tags API for each repository
   using `httpx` with a 10-second timeout and no retries:
   `GET /repos/{owner}/{repo}/tags?per_page=100`.
3. Accept only stable `vMAJOR.MINOR.PATCH`/`MAJOR.MINOR.PATCH` tags for
   comparison. Ignore pre-release and non-version tags. No new
   dependency is added for version parsing.
4. Report `current`, `update_available`, `pinned`, `check_failed`,
   `corrupt`, or `missing` per component. It never downloads source,
   rewrites the lock, installs packages, or changes the running adapter.
5. An optional standard `GITHUB_TOKEN` raises the API rate limit. It is
   never logged or serialized. A 403/404/5xx/network failure is a bounded
   `check_failed`; the vendored source remains usable.

The adapter never performs an update check during capabilities, health,
search, or ingestion. "Fallback to the original" means the installed
upstream distribution for Python packages, not a runtime GitHub clone.

#### Maintainer updates

`scripts/vendor_dependencies.py` is the only code that mutates `vendor/`.
It uses argument-list `subprocess` calls (no shell), a temporary
directory, and `git archive`/checkout of the exact tag. It verifies the
resolved commit against the lock, exports tracked files only, rejects
symlinks, recomputes the tree checksum, and updates the lock atomically.
The update is reviewed as a normal source change and must pass the vendor
tests plus the retrieval test suite. This script is not exposed as an MCP
tool or a user-facing update command.

#### Limitations

- QMD's vendored source is an emergency rebuild input. The adapter still
  talks to a running QMD HTTP endpoint; it never builds, starts, or
  switches to vendored QMD automatically.
- Vendored source does not include npm/PyPI transitive dependency trees.
  Those remain in the optional extra and lock data.
- A deleted upstream repository makes the update check fail; it does not
  invalidate the vendored snapshot.

## 7. Security and privacy

- No shell commands, `shell=True`, or CLI argument interpolation.
- QMD endpoint is loopback by default. Remote endpoints are opt-in and
  unauthenticated QMD is documented as requiring an operator-provided
  auth proxy.
- QMD collection allowlist is explicit. No default access to all
  collections when enabled.
- RAG ingestion requires explicit allowed roots. Candidate paths are
  resolved, symlinks rejected, and containment checked twice.
- `.html`/`.htm`/`.xhtml` rejected in v1. Markdown local image references
  are restricted to allowed roots.
- File size and result/content sizes are bounded.
- No absolute paths are returned from RAG sources; ingestion passes a
  safe display name.
- Secrets are held only in configuration and are never serialized.
- Remote model egress is surfaced in capabilities and documentation. No
  content is sent until an explicit query or ingestion call.
- Errors do not include document content, full request bodies, API keys,
  or URL credentials. Upstream error bodies are truncated and redacted.
- Logging records backend, duration, counts, error codes, doc IDs, and
  relative display paths only. Query text is not logged by default.
- Deletion is not exposed. Ingestion is the only mutating operation, and
  it is gated by allowed roots and configuration.
- Vendored snapshots are pinned to exact commits and verified by tree
  checksum before use. The adapter never downloads, auto-installs, or
  auto-switches to upstream Git code.
- Update checks run only from the explicit CLI or maintainer script, use
  HTTPS, have a bounded timeout, and redact `GITHUB_TOKEN`.
- Vendored `sys.path` insertion is limited to the two fixed, resolved
  package roots; symlinked or missing roots are rejected.
- Updating a vendored snapshot is a reviewed code change, not a runtime
  operation. The maintainer script uses argument lists, never a shell.

## 8. Packaging and compatibility

`pyproject.toml` gains:

```toml
[project.optional-dependencies]
rag-anything = [
  "raganything>=1.4.3,<1.5; python_version >= '3.10'",
  "lightrag-hku==1.4.16; python_version >= '3.10'",
  "openai>=2.0.0,<4.0.0; python_version >= '3.10'",
]
```

- The exact `lightrag-hku` pin keeps the installed pair aligned with the
  vendored `v1.4.16` snapshot. RAG-Anything's `<1.5` constraint remains
  satisfied.
- QMD has no Python extra; document the npm/Node prerequisite and
  `qmd mcp --http`.
- Core imports and tests must work on Python 3.9 without either optional
  package. Default unit tests use fakes and do not import upstream; live
  RAG tests require Python >=3.10 and the extra.
- Do not add `raganything` to `all-integrations`.
- `vendor/` is excluded from wheel and sdist contents. It remains in the
  source repository for reproducibility. Packaging tests assert that
  package discovery still comes only from `python/`.
- README installation lists the new extra and the external QMD
  prerequisite.
- No version bump in this change unless the release process is explicitly
  requested. `__version__` remains 3.3.5.

## 9. Documentation

- New `docs/retrieval.md`: architecture, setup for QMD and RAG-Anything,
  configuration reference, MCP/CLI examples, result schema, routing
  rules, score semantics, security, privacy/egress, model downloads,
  cold-start costs, limitations, and benchmark commands.
- New `vendor/README.md`: upstream attribution, exact pins/commits,
  checksum verification, source fallback behavior, update-check
  procedure, transitive-dependency caveats, and the rule that updates are
  reviewed code changes.
- README: feature bullet, install lines, minimal QMD and RAG examples,
  link to `docs/retrieval.md`, and explicit "no silent fallback / no
  cross-engine fusion / no deletion / no runtime dependency updates"
  notes.
- `docs/ARCHITECTURE.md`: add a retrieval section and update the surface
  diagram.
- `SECURITY.md`: ingestion path rules, HTML/Markdown caveats, QMD remote
  exposure, remote model egress, no deletion, vendored-source checks, and
  the no-runtime-update rule.
- `docs/internal/ROADMAP_HONEST.md`: record what was actually verified,
  which upstream sources are vendored and pinned, what remains
  upstream-dependent, and that live QMD/RAG tests are opt-in.

## 10. Benchmark plan and scripts

Add `benchmarks/retrieval_bench.py`:

- Default fake backends measure normalized service/router overhead and
  output p50/p95/p99 latency, throughput, and allocation-free result
  construction. This is deterministic and CI-safe.
- `--qmd-url` mode runs N queries against a real QMD HTTP server and
  reports per-query latency and result counts, excluding model cold start
  unless explicitly measured.
- `--rag` mode is opt-in and reports separately because RAG latency is
  dominated by parsing, embeddings, graph construction, and LLM reranking.
  Never combine QMD and RAG timings into a single quality score.
- Add `benchmarks/README.md` with:
  - corpus/collection setup requirements
  - commands
  - metrics: p50/p95/p99 latency, sample count, hit count, empty-result
    count, error/timeout counts
  - quality fields for a future labeled fixture: precision@k, recall@k,
    MRR; no fabricated baseline numbers
  - cold-start vs warm-cache separation
  - expected overhead target: normalized routing/serialization overhead
    should remain small relative to upstream latency, measured rather than
    asserted.
- Do not commit benchmark result claims until they are produced by a real
  run in the target environment.

## 11. Testing strategy

All default tests are offline and use no heavy optional dependency.

New tests:

- `tests/test_vendor_dependencies.py`: lock schema, exact pins/commits,
  all three source trees and licenses present, no `.git`/symlinks/
  generated dependency trees, tree checksums verify, and the maintainer
  verifier rejects a modified file.
- `tests/test_retrieval_deps.py`: source resolution matrix
  (`installed`/`vendored`/mixed/missing/injected), fixed-path-only
  insertion, idempotency, no heavy import at resolution, update-check
  parsing/tag comparison, offline mode, 403/404/timeout handling, no
  token leakage, and corrupted-tree reporting.
- `tests/test_retrieval_models.py`: serialization, enums, bounds,
  score semantics, redaction.
- `tests/test_retrieval_router.py`: explicit backend, unavailable explicit
  errors, `all`, `auto` by collections/content type/mode/priority,
  no-backend case.
- `tests/test_retrieval_service.py`: grouping, partial success, parallel
  timeout handling, no score fusion, close/idempotency.
- `tests/test_retrieval_qmd.py`: `httpx.MockTransport` contract fixtures
  for health/lex/vec/hybrid/hyde, allowlist enforcement, malformed/failed
  responses, timeouts, output bounds, snippet/line mapping.
- `tests/test_retrieval_rag.py`: fake async engine and real worker loop;
  mode mapping, chunk mapping, page enrichment, empty results, no
  initialization, missing dependency/version, ingest hash/status/idempotency,
  timeout, close.
- `tests/test_retrieval_security.py`: traversal, symlinks, allowed roots,
  unsupported extensions, HTML rejection, size limits, Markdown image
  references, redaction, no absolute RAG paths.
- `tests/test_retrieval_mcp.py`: schemas/validation, search/capabilities/
  ingest dispatch with a fake service, structured errors, existing tools
  unchanged, auth behavior unchanged.
- `tests/test_retrieval_cli.py`: JSON/human output, exit codes, errors,
  `deps status --offline` verification, and `deps status` update/failure
  exit codes via a mock GitHub response.
- `tests/test_retrieval_packaging.py`: public exports, optional extra and
  exact LightRAG pin, core import isolation, and vendor exclusion from
  package discovery and the sdist manifest.
- `tests/test_retrieval_live.py`: skipped unless the documented env vars
  are set.

Acceptance/verification:

- `pytest tests/` passes; baseline 421 passed/13 skipped remains green.
- New tests pass offline.
- `python scripts/vendor_dependencies.py verify` passes without network.
- `pystreammcp retrieval deps status --offline` exits 0 with all three
  snapshots verified.
- `ruff check` is clean on new/changed files (repo-wide lint is currently
  not clean and is not part of this change).
- `python -m compileall` succeeds for new modules.
- Importing `pystreammcp` with no optional extras does not import
  `raganything`, `lightrag`, or `openai`.
- With no retrieval env configured, capabilities are empty/success and
  search returns `no_available_backend`; existing PT behavior is
  unchanged.
- A QMD contract test proves the request/response mapping.
- A fake RAG engine proves ingestion, query, page enrichment fallback, and
  structured error mapping.
- No test claims live upstream behavior without an opt-in live run.

## 12. Risks and mitigations

- **Upstream API drift.** Pin RAG-Anything `<1.5`, pin LightRAG
  `1.4.16`, feature-detect `aquery_data`, and return
  `upstream_unsupported_version` rather than guessing. QMD contract tests
  target v2.8.x. Explicit `deps status` reports newer upstream tags; it
  never applies them automatically.
- **Vendored-source drift or tampering.** Exact commit pins, offline tree
  checksums, reviewed maintainer updates, fixed `sys.path` roots, and no
  runtime downloads.
- **Incomplete vendoring.** The source snapshots do not include npm/PyPI
  transitive closures. Docs and capabilities distinguish "source is
  preserved" from "runtime is fully offline"; missing transitive packages
  are `missing_dependency`, not auto-installed.
- **Stale vendored fallback.** `auto` prefers a consistent installed pair;
  `deps status` exposes pins and update availability. No silent version
  mixing.
- **Heavy RAG cold start and downloads.** Lazy import, no startup model
  load, explicit capabilities, documented first-use downloads, and
  separate benchmark reporting.
- **RAG scores unavailable.** Return `score=None` and
  `score_kind="unavailable"`; never invent scores.
- **Cross-store inconsistency.** RAG ingestion serializes operations and
  uses stable doc IDs. No deletion in v1 prevents a half-delete path.
- **Remote content exposure.** Explicit provider config, loopback/local
  detection, capabilities, docs, and no calls before explicit use.
- **Path/symlink races.** Resolve roots and candidates, reject symlinks,
  pass the resolved path, and bound file sizes.
- **Python version mismatch.** RAG extra is environment-marked to
  Python >=3.10 and not installed by default; core remains 3.9-compatible.
- **Module surface confusion.** Retrieval is exposed on the protocol MCP
  server, not the separate `_mcp_tools` orchestration handler. Docs make
  this explicit.

## 13. What is left to the builder

No open product decisions. The implementation plan should settle only
internal details that do not change behavior:

- exact private helper names and dataclass field ordering
- fixture file layout and synthetic QMD response contents
- pytest test class organization
- whether to use `ThreadPoolExecutor` per service or a small persistent
  executor (either is acceptable if timeouts and shutdown are correct)
- log message wording

The following are deliberate v1 decisions, not open questions:

- HTTP-only QMD; no CLI transport fallback
- in-process RAG in a worker thread; no sidecar
- structured LightRAG `aquery_data` evidence; no synthesized answers
- no deletion, no batch ingestion, no REST endpoints
- no cross-engine score fusion
- explicit config/allowlists; no auto-discovery of collections or roots
- QMD `v2.8.3`, RAG-Anything `v1.4.3`, LightRAG `v1.4.16` vendored under
  `vendor/`; exact commits and tree checksums in `deps.lock.json`
- installed-first/`auto` source resolution with a consistent vendored
  fallback; no mixed installed/vendored pair
- read-only `deps status` update checks; no runtime update or download;
  mutations only through the reviewed maintainer script

Implementation may choose the internal module names for tree hashing and
the exact maintainer-script subcommand spelling, but it must preserve the
layout, pins, resolution rules, and CLI exit-code contract above.
