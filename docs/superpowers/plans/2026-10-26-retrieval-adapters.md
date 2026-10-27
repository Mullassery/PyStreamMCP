# Retrieval Adapters Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add optional QMD and RAG-Anything retrieval adapters with deterministic grouped routing, guarded ingestion, in-repo pinned dependency snapshots, explicit update checks, MCP tools, CLI commands, tests, benchmarks, and documentation.

**Architecture:** A framework-free `pystreammcp.retrieval` package normalizes search and ingestion. QMD is a loopback-first HTTP adapter. RAG-Anything is lazy, runs on a managed worker thread, and uses either an injected engine or an explicitly configured OpenAI-compatible provider. Pinned QMD, RAG-Anything, and LightRAG source snapshots live under `vendor/`; RAG resolution prefers a consistent installed pair and falls back to the vendored pair. A read-only `deps status` command checks upstream tags. A service owns routing, time budgets, serialization, and cleanup; MCP and Click are thin surfaces.

**Tech Stack:** Python 3.9+ core, `httpx`, dataclasses, `concurrent.futures`, `threading`, `asyncio`, `click`, Pydantic v2, `pytest`, `httpx.MockTransport`.

**Spec:** `docs/superpowers/specs/2026-10-26-retrieval-adapters-design.md`

## Global Constraints

- Do not make QMD, RAG-Anything, LightRAG, MinerU, or OpenAI mandatory. QMD is HTTP-only; RAG goes in the optional `rag-anything` extra.
- Vendor the upstream sources before adapter code: `tobi/qmd` v2.8.3 (`facd35e01359e59d938bc9418e93fb9318addee3`), `HKUDS/RAG-Anything` v1.4.3 (`afb67c43d391b1b1008a6fee9f020a232067b9e5`), and `HKUDS/LightRAG` v1.4.16 (`964f26e9a9239c1316045913328e863ec35492e4`) under `vendor/` with licenses, tree checksums, and no nested `.git`.
- `PYSTREAMMCP_RAG_SOURCE=auto` uses installed `raganything`/`lightrag` only when both are present; otherwise it uses both vendored snapshots. `installed` and `vendored` are strict. Never mix pairs. `auto` must not import heavy modules during capabilities.
- `pystreammcp retrieval deps status` is read-only. It verifies vendored checksums offline and, unless `--offline`, checks upstream GitHub tags. It never downloads, installs, updates, or switches code. A maintainer script is the only thing that mutates `vendor/`.
- Extra entries must be gated with `python_version >= '3.10'`; core `requires-python` stays `>=3.9`. Pin `lightrag-hku==1.4.16` in the RAG extra.
- No auto-install, model download, or telemetry. No remote model call without explicit provider config. No `shell=True`.
- QMD defaults to loopback; remote URLs require `PYSTREAMMCP_QMD_ALLOW_REMOTE=true`. QMD collections are an explicit allowlist.
- Ingestion requires `PYSTREAMMCP_RAG_ALLOWED_ROOTS`; reject traversal, symlinks, HTML, unsupported extensions, oversize files, and Markdown images outside roots.
- Do not log API keys, bearer tokens, `GITHUB_TOKEN`, document content, query text, or URL userinfo.
- Preserve existing MCP tools, auth, validation, and outer exception handling. Do not modify `python/pystreammcp/_mcp_tools.py`.
- No REST, deletion, batch ingestion, QMD CLI transport, RAG answer generation, cross-engine score fusion, automatic retry, or circuit breaker.
- `vendor/` is source-repository-only; exclude it from built packages. Live tests are opt-in via the spec's environment variables.
- Do not commit unless the user explicitly asks. End each task with `git status --short` and a checkpoint.

## Review Focus

- **Vendored tree modified:** `vendor_dependencies.py verify` and the offline vendor test fail before any adapter test can mask it; Task 0.
- **Installed/vendored mixing:** `auto` must choose a consistent pair, and `vendored` must not silently import an installed package; Task 2 and Task 6.
- **Update check mutates state or leaks a token:** `deps status` is read-only and redacts `GITHUB_TOKEN`; Task 10.
- **Timed-out RAG query:** returns `timeout` promptly and `close()` does not hang; test in Task 6.
- **Symlink inside an allowed root:** rejected before hashing/engine work; tests in Tasks 2 and 7.
- **Unreachable QMD during text auto-routing:** QMD is selected by priority and its failure is returned; no silent RAG retry; test in Task 4.
- **Broken backend config:** does not crash service construction; that backend is unavailable and the other still works; test in Task 4.
- **Markdown image outside roots:** rejected before the engine is called; test in Task 7.

---

### Task 0: Pin and Vendor Upstream Dependencies

**Files:**
- Create: `vendor/README.md`
- Create: `vendor/deps.lock.json`
- Create: `vendor/qmd/`
- Create: `vendor/rag-anything/`
- Create: `vendor/lightrag/`
- Create: `scripts/vendor_dependencies.py`
- Test: `tests/test_vendor_dependencies.py`

**Interfaces:**
- Produces: `vendor/deps.lock.json` schema with `repo`, `tag`, `commit`, `path`, `ecosystem`, `license`, `tree_sha256`
- Produces: `scripts/vendor_dependencies.py verify` and `scripts/vendor_dependencies.py vendor --component all`
- Produces: offline tree-check verification used by Task 2b and Task 10

- [ ] **Step 1: Write the failing vendor tests**

Create `tests/test_vendor_dependencies.py`:

```python
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "vendor" / "deps.lock.json"
EXPECTED = {
    "qmd": ("v2.8.3", "facd35e01359e59d938bc9418e93fb9318addee3", "vendor/qmd"),
    "rag-anything": ("v1.4.3", "afb67c43d391b1b1008a6fee9f020a232067b9e5", "vendor/rag-anything"),
    "lightrag": ("v1.4.16", "964f26e9a9239c1316045913328e863ec35492e4", "vendor/lightrag"),
}

def test_lock_pins_and_paths():
    data = json.loads(LOCK.read_text(encoding="utf-8"))
    assert data["schema"] == 1
    assert set(data["dependencies"]) == set(EXPECTED)
    for name, (tag, commit, path) in EXPECTED.items():
        dep = data["dependencies"][name]
        assert (dep["tag"], dep["commit"], dep["path"]) == (tag, commit, path)
        assert dep["license"] == "MIT"
        assert dep["ecosystem"] == ("npm" if name == "qmd" else "python")
        assert dep["repo"].startswith("https://github.com/")
        assert (ROOT / path / "LICENSE").is_file()
        assert not (ROOT / path / ".git").exists()
        assert not (ROOT / path / "node_modules").exists()
        assert "tree_sha256" in dep and len(dep["tree_sha256"]) == 64

def test_no_symlinks_in_vendor_tree():
    for path in (ROOT / "vendor").rglob("*"):
        assert not path.is_symlink(), f"symlink in vendor: {path}"

def test_verifier_passes_and_rejects_modification(tmp_path):
    ok = subprocess.run([sys.executable, "scripts/vendor_dependencies.py", "verify"],
                        cwd=ROOT, capture_output=True, text=True, timeout=60)
    assert ok.returncode == 0, ok.stderr
    target = ROOT / "vendor" / "lightrag" / "README.md"
    original = target.read_bytes()
    try:
        target.write_bytes(original + b"\nlocal edit\n")
        bad = subprocess.run([sys.executable, "scripts/vendor_dependencies.py", "verify"],
                             cwd=ROOT, capture_output=True, text=True, timeout=60)
        assert bad.returncode != 0
    finally:
        target.write_bytes(original)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_vendor_dependencies.py -v`

Expected: FAIL because `vendor/deps.lock.json` and the script are missing.

- [ ] **Step 3: Create the lock and vendor README**

Create `vendor/README.md` with the upstream URLs, exact tags/commits, MIT attribution, the tree-hash algorithm, the no-modification rule, the source-fallback semantics, the maintainer update procedure, and these limitations:

- The snapshots contain upstream tracked files only; `.git` and generated dependency trees are excluded.
- RAG-Anything/LightRAG still need their PyPI dependencies; QMD still needs Node/npm dependencies.
- The adapter never updates, downloads, or starts vendored code automatically.
- Updates are reviewed source changes, never runtime operations.

Create `vendor/deps.lock.json` with the exact shape in §6.13 and the three pins above. Leave `tree_sha256` empty until Step 5.

- [ ] **Step 4: Implement the maintainer script**

`scripts/vendor_dependencies.py` uses `argparse` and subprocess argument lists only:

- `verify`: load the lock, reject unknown/missing paths, reject symlinks, recompute each tree hash, compare, print one line per component, exit 1 on mismatch. No network.
- `vendor --component qmd|rag-anything|lightrag|all`: read the lock, shallow-clone each exact tag into a temporary directory, check out the pinned commit, export tracked files (no `.git`), copy into a temporary sibling, reject symlinks, replace the vendor directory, recompute the hash, and update the lock atomically. An empty `tree_sha256` is allowed only for this initial/fill path; `verify` rejects it. No shell.
- `update --component NAME --tag TAG`: resolve `TAG` with `git ls-remote` to a commit (prefer the peeled `^{}` commit for annotated tags), then vendor that tag and update `tag`/`commit`/`tree_sha256`. This is the only mutation path and is maintainer-only.
- Never add a `deps update` Click command. The runtime package must not mutate `vendor/`.

- [ ] **Step 5: Vendor the pinned sources**

Run the script for all three components, then verify:

```bash
.venv/bin/python scripts/vendor_dependencies.py vendor --component all
.venv/bin/python scripts/vendor_dependencies.py verify
```

Expected: `vendor/qmd/`, `vendor/rag-anything/`, `vendor/lightrag/` contain tracked upstream files plus `LICENSE`; no `.git`; lock hashes populated.

- [ ] **Step 6: Run the vendor tests**

Run: `.venv/bin/python -m pytest tests/test_vendor_dependencies.py -v`

Expected: PASS.

- [ ] **Step 7: Checkpoint**

Run: `git status --short`. Do not commit. Confirm the vendor trees are present before implementing adapter code.

---

### Task 1: Normalized Models, Errors, and Backend Contracts

**Files:**
- Create: `python/pystreammcp/retrieval/__init__.py`
- Create: `python/pystreammcp/retrieval/models.py`
- Create: `python/pystreammcp/retrieval/errors.py`
- Create: `python/pystreammcp/retrieval/base.py`
- Test: `tests/test_retrieval_models.py`
- Test helper: `tests/retrieval_helpers.py`

**Interfaces:**
- Produces: `BackendName`, `RequestedBackend`
- Produces: `RetrievalRequest`, `RetrievalHit`, `BackendGroup`, `RetrievalResponse`
- Produces: `RetrievalError(code, message, backend=None, retryable=False, details=None)` with `to_dict()`
- Produces: `BackendSearchRequest`, `BackendSearchResult`, `BackendCapabilities`, `BackendHealth`, `IngestionResult`
- Produces: `RetrievalBackend` and `IngestingBackend` protocols
- Produces test helper `FakeBackend`

- [ ] **Step 1: Write the failing model tests**

Create `tests/test_retrieval_models.py` with these exact assertions:

```python
from pystreammcp.retrieval.base import BackendCapabilities
from pystreammcp.retrieval.errors import RetrievalError
from pystreammcp.retrieval.models import (
    BackendGroup, BackendName, RequestedBackend, RetrievalHit,
    RetrievalRequest, RetrievalResponse,
)

def test_request_defaults_match_spec():
    request = RetrievalRequest(query="alpha")
    assert request.backend is RequestedBackend.AUTO
    assert request.mode is None
    assert request.content_type is None
    assert request.limit == 5
    assert request.max_content_chars == 2000
    assert request.time_budget_ms == 30000

def test_response_keeps_engines_separate_and_serializes_enums():
    hit = RetrievalHit(
        backend=BackendName.QMD, rank=1, document_id="d1", title="Doc",
        source_uri="qmd://docs/a.md", locator={"kind": "line", "line": 3},
        excerpt="alpha", content=None, score=1.5,
        score_kind="qmd_query_relevance", metadata={"docid": "d1"},
    )
    response = RetrievalResponse(
        status="success", query="alpha", backend_requested="auto",
        groups=[BackendGroup(
            backend=BackendName.QMD, status="ok", hits=[hit], error=None,
            elapsed_ms=4, truncated=False,
        )],
        diagnostics={"selected": ["qmd"]},
    )
    data = response.to_dict()
    assert data["status"] == "success"
    assert data["groups"][0]["backend"] == "qmd"
    assert data["groups"][0]["hits"][0]["locator"]["line"] == 3
    assert "content" not in data["groups"][0]["hits"][0]

def test_error_to_dict_is_bounded():
    data = RetrievalError(
        "http_error", "x" * 900, backend=BackendName.QMD,
        retryable=False, details={"status_code": 400},
    ).to_dict()
    assert data["code"] == "http_error"
    assert len(data["message"]) <= 500
    assert data["backend"] == "qmd"
    assert data["details"] == {"status_code": 400}

def test_capabilities_shape():
    caps = BackendCapabilities(
        backend=BackendName.QMD, enabled=True, configured=True, available=True,
        modes=("auto",), content_types=("text",), max_limit=50,
        supports_ingestion=False, supports_full_content=False,
        score_kind="qmd_query_relevance", network_egress="local", error=None,
    )
    assert caps.to_dict()["network_egress"] == "local"
    assert caps.to_dict()["supports_full_content"] is False
```

Create `tests/retrieval_helpers.py`:

```python
import time

from pystreammcp.retrieval.base import (
    BackendCapabilities, BackendHealth, BackendSearchResult, IngestionResult,
)
from pystreammcp.retrieval.models import BackendName, RetrievalRequest

def make_request(**overrides):
    values = {"query": "alpha"}
    values.update(overrides)
    return RetrievalRequest(**values)

class FakeBackend:
    def __init__(self, name, caps=None, hits=None, error=None, delay=0.0):
        self.name = BackendName(name)
        self.caps = caps or BackendCapabilities(
            backend=self.name, enabled=True, configured=True, available=True,
            modes=("auto", "hybrid", "local", "global", "naive", "mix"),
            content_types=("text",), max_limit=50, supports_ingestion=True,
            supports_full_content=True, score_kind="unavailable",
            network_egress="local", error=None,
        )
        self.hits = list(hits or [])
        self.error = error
        self.delay = delay
        self.requests = []
        self.closed = False
        self.ingest_calls = []

    def capabilities(self):
        return self.caps

    def health(self):
        return BackendHealth(
            backend=self.name, available=True, status="ok",
            message="ok", elapsed_ms=0,
        )

    def search(self, request):
        self.requests.append(request)
        if self.delay:
            time.sleep(self.delay)
        if self.error:
            raise self.error
        return BackendSearchResult(hits=list(self.hits), truncated=False, diagnostics={})

    def ingest(self, path, force_multimodal=False):
        self.ingest_calls.append((path, force_multimodal))
        return IngestionResult(
            document_id="doc-1", display_path=path, status="processed",
            skipped=False, elapsed_ms=1, content_types=("text",),
        )

    def close(self):
        self.closed = True
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_retrieval_models.py -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'pystreammcp.retrieval'`.

- [ ] **Step 3: Implement the exact spec types**

`models.py`:

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
    mode: Optional[str] = None
    collections: tuple[str, ...] = ()
    content_type: Optional[str] = None
    limit: int = 5
    include_content: bool = False
    max_content_chars: int = 2000
    time_budget_ms: int = 30000
    intent: Optional[str] = None

@dataclass(frozen=True)
class RetrievalHit:
    backend: BackendName
    rank: int
    document_id: Optional[str]
    title: Optional[str]
    source_uri: str
    locator: dict[str, Any]
    excerpt: str
    content: Optional[str]
    score: Optional[float]
    score_kind: str
    metadata: dict[str, Any]

@dataclass
class BackendGroup:
    backend: BackendName
    status: str
    hits: list[RetrievalHit]
    error: Optional[dict[str, Any]]
    elapsed_ms: int
    truncated: bool

@dataclass
class RetrievalResponse:
    status: str
    query: str
    backend_requested: str
    groups: list[BackendGroup]
    diagnostics: dict[str, Any]
```

Add `to_dict()` to every public dataclass. Recursively serialize enums and dataclasses. Omit `content` only when `None`. Do not fabricate scores.

`errors.py`:

```python
class RetrievalError(Exception):
    def __init__(self, code, message, backend=None, retryable=False, details=None): ...
    def to_dict(self) -> dict[str, Any]: ...
```

Stable codes exactly: `configuration_error`, `not_configured`, `unavailable`, `missing_dependency`, `invalid_request`, `invalid_backend`, `unsupported_mode`, `unsupported_content_type`, `collection_not_allowed`, `collection_required`, `timeout`, `http_error`, `invalid_response`, `path_outside_allowed_roots`, `symlink_not_allowed`, `unsupported_extension`, `file_too_large`, `not_a_file`, `ingest_failed`, `index_not_initialized`, `query_failed`, `upstream_unsupported_version`, `no_available_backend`, `closed`. Bound messages to 500 chars.

`base.py`:

```python
@dataclass(frozen=True)
class BackendSearchRequest:
    query: str
    mode: Optional[str]
    collections: tuple[str, ...]
    content_type: Optional[str]
    limit: int
    include_content: bool
    max_content_chars: int
    timeout_s: float
    intent: Optional[str]

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
    available: bool
    modes: tuple[str, ...]
    content_types: tuple[str, ...]
    max_limit: int
    supports_ingestion: bool
    supports_full_content: bool
    score_kind: str
    network_egress: str
    error: Optional[dict[str, Any]]

@dataclass(frozen=True)
class BackendHealth:
    backend: BackendName
    available: bool
    status: str
    message: Optional[str]
    elapsed_ms: int

@dataclass(frozen=True)
class IngestionResult:
    document_id: str
    display_path: str
    status: str
    skipped: bool
    elapsed_ms: int
    content_types: tuple[str, ...]

@runtime_checkable
class RetrievalBackend(Protocol):
    name: BackendName
    def capabilities(self) -> BackendCapabilities: ...
    def health(self) -> BackendHealth: ...
    def search(self, request: BackendSearchRequest) -> BackendSearchResult: ...
    def close(self) -> None: ...

@runtime_checkable
class IngestingBackend(RetrievalBackend, Protocol):
    def ingest(self, path: str, force_multimodal: bool = False) -> IngestionResult: ...
```

`retrieval/__init__.py` exports only these models/errors/base types for now.

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_retrieval_models.py -v`

Expected: PASS.

- [ ] **Step 5: Checkpoint**

Run: `git status --short`. Do not commit.

---

### Task 2: Configuration and Ingestion Security

**Files:**
- Create: `python/pystreammcp/retrieval/config.py`
- Create: `python/pystreammcp/retrieval/security.py`
- Test: `tests/test_retrieval_config.py`
- Test: `tests/test_retrieval_security.py`

**Interfaces:**
- Produces: `QmdConfig`, `RagProviderConfig`, `RagConfig`, `RetrievalConfig.from_env(env=None)`
- Produces: `normalize_extensions`, `resolve_allowed_roots`, `resolve_ingest_path`, `make_display_path`, `check_markdown_image_refs`, `is_loopback_url`, `validate_qmd_url`, `redact_text`, `redact_url_userinfo`

- [ ] **Step 1: Write failing config tests**

Create `tests/test_retrieval_config.py`:

```python
from pystreammcp.retrieval.config import RetrievalConfig

def test_defaults_are_disabled():
    c = RetrievalConfig.from_env({})
    assert (c.qmd_requested, c.rag_requested) == (False, False)
    assert c.qmd_error is None and c.rag_error is None

def test_qmd_env_and_collection_allowlist():
    c = RetrievalConfig.from_env({
        "PYSTREAMMCP_QMD_ENABLED": "true",
        "PYSTREAMMCP_QMD_URL": "http://127.0.0.1:8181",
        "PYSTREAMMCP_QMD_COLLECTIONS": "notes, docs",
        "PYSTREAMMCP_QMD_TIMEOUT_S": "9.5",
        "PYSTREAMMCP_QMD_TRUST_ENV": "true",
    })
    assert c.qmd.collections == ("notes", "docs")
    assert c.qmd.timeout_s == 9.5
    assert c.qmd.trust_env is True
    assert c.qmd_error is None

def test_qmd_requires_collections_when_enabled():
    c = RetrievalConfig.from_env({"PYSTREAMMCP_QMD_ENABLED": "true"})
    assert c.qmd_requested is True
    assert "QMD_COLLECTIONS" in c.qmd_error

def test_qmd_remote_requires_opt_in():
    c = RetrievalConfig.from_env({
        "PYSTREAMMCP_QMD_ENABLED": "true",
        "PYSTREAMMCP_QMD_COLLECTIONS": "docs",
        "PYSTREAMMCP_QMD_URL": "https://qmd.example.com",
    })
    assert "loopback" in c.qmd_error

def test_rag_missing_roots_is_not_ingestion_ready():
    c = RetrievalConfig.from_env({"PYSTREAMMCP_RAG_ENABLED": "true"})
    assert c.rag.allowed_roots == ()
    assert c.rag_error is None

def test_rag_provider_parsing_and_embed_key_fallback():
    c = RetrievalConfig.from_env({
        "PYSTREAMMCP_RAG_ENABLED": "true",
        "PYSTREAMMCP_RAG_ALLOWED_ROOTS": "/tmp/docs",
        "PYSTREAMMCP_RAG_PROVIDER": "openai_compatible",
        "PYSTREAMMCP_RAG_LLM_MODEL": "gpt-4.1",
        "PYSTREAMMCP_RAG_LLM_BASE_URL": "https://llm.example.com/v1",
        "PYSTREAMMCP_RAG_LLM_API_KEY": "sk-llm",
        "PYSTREAMMCP_RAG_EMBED_MODEL": "embed",
        "PYSTREAMMCP_RAG_EMBED_BASE_URL": "https://embed.example.com/v1",
        "PYSTREAMMCP_RAG_EMBED_DIM": "1024",
    })
    assert c.rag_error is None
    assert c.rag.provider.embedding_api_key == "sk-llm"
    assert c.rag.provider.embedding_max_tokens == 8192

def test_invalid_integer_is_config_error_not_exception():
    c = RetrievalConfig.from_env({
        "PYSTREAMMCP_RAG_ENABLED": "true",
        "PYSTREAMMCP_RAG_MAX_FILE_MB": "lots",
    })
    assert "MAX_FILE_MB" in c.rag_error
```

- [ ] **Step 2: Run config tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_retrieval_config.py -v`

Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement config**

`QmdConfig`: `enabled`, `url="http://127.0.0.1:8181"`, `collections=()`, `timeout_s=10.0`, `health_timeout_s=1.5`, `allow_remote=False`, `trust_env=False`.

`RagProviderConfig`: `llm_model`, `llm_base_url`, `llm_api_key`, `embedding_model`, `embedding_base_url`, `embedding_api_key`, `embedding_dim`, `embedding_max_tokens=8192`, optional `vision_model`, `vision_base_url`, `vision_api_key`.

`RagConfig`: `enabled=False`, `working_dir=Path("./rag_storage")`, `parsed_dir=Path("./rag_storage/parsed")`, `allowed_roots=()`, `allowed_extensions` default exactly `.pdf,.png,.jpg,.jpeg,.bmp,.tif,.tiff,.gif,.webp,.txt,.md`, `parser="mineru"`, `parse_method="auto"`, `query_mode="mix"`, `enable_image_processing=True`, `enable_table_processing=True`, `enable_equation_processing=True`, `max_file_mb=100`, `query_timeout_s=60.0`, `ingest_timeout_s=600.0`, `force_multimodal_reprocess=False`, `provider_name="none"`, `provider=None`, `source_mode="auto"`.

`RetrievalConfig`: `qmd`, `rag`, `qmd_requested`, `rag_requested`, `qmd_error`, `rag_error`.

Environment names are exactly:

`PYSTREAMMCP_QMD_ENABLED`, `PYSTREAMMCP_QMD_URL`, `PYSTREAMMCP_QMD_COLLECTIONS`, `PYSTREAMMCP_QMD_TIMEOUT_S`, `PYSTREAMMCP_QMD_HEALTH_TIMEOUT_S`, `PYSTREAMMCP_QMD_ALLOW_REMOTE`, `PYSTREAMMCP_QMD_TRUST_ENV`.

`PYSTREAMMCP_RAG_ENABLED`, `PYSTREAMMCP_RAG_WORKING_DIR`, `PYSTREAMMCP_RAG_ALLOWED_ROOTS`, `PYSTREAMMCP_RAG_ALLOWED_EXTENSIONS`, `PYSTREAMMCP_RAG_PARSER`, `PYSTREAMMCP_RAG_PARSE_METHOD`, `PYSTREAMMCP_RAG_QUERY_MODE`, `PYSTREAMMCP_RAG_ENABLE_IMAGE_PROCESSING`, `PYSTREAMMCP_RAG_ENABLE_TABLE_PROCESSING`, `PYSTREAMMCP_RAG_ENABLE_EQUATION_PROCESSING`, `PYSTREAMMCP_RAG_MAX_FILE_MB`, `PYSTREAMMCP_RAG_QUERY_TIMEOUT_S`, `PYSTREAMMCP_RAG_INGEST_TIMEOUT_S`, `PYSTREAMMCP_RAG_FORCE_MULTIMODAL_REPROCESS`, `PYSTREAMMCP_RAG_PROVIDER`, `PYSTREAMMCP_RAG_SOURCE`, `PYSTREAMMCP_RAG_LLM_BASE_URL`, `PYSTREAMMCP_RAG_LLM_API_KEY`, `PYSTREAMMCP_RAG_LLM_MODEL`, `PYSTREAMMCP_RAG_EMBED_BASE_URL`, `PYSTREAMMCP_RAG_EMBED_API_KEY`, `PYSTREAMMCP_RAG_EMBED_MODEL`, `PYSTREAMMCP_RAG_EMBED_DIM`, `PYSTREAMMCP_RAG_EMBED_MAX_TOKENS`, `PYSTREAMMCP_RAG_VISION_BASE_URL`, `PYSTREAMMCP_RAG_VISION_API_KEY`, `PYSTREAMMCP_RAG_VISION_MODEL`.

Rules: roots split on `os.pathsep`; lists comma-split and trimmed; invalid section values set `qmd_error`/`rag_error` instead of raising; QMD enabled requires non-empty collections; QMD URL must be loopback unless remote opt-in and must not contain userinfo; RAG `provider_name` must be `none` or `openai_compatible`; `openai_compatible` requires all LLM/embed fields and sets `rag_error` otherwise; RAG `source_mode` must be `auto`, `installed`, or `vendored`; missing roots is not a config error (query may still work, ingestion will fail); `parsed_dir` is derived from `working_dir` unless a library caller overrides it.

- [ ] **Step 4: Run config tests**

Run: `.venv/bin/python -m pytest tests/test_retrieval_config.py -v`

Expected: PASS.

- [ ] **Step 5: Write failing security tests**

Create `tests/test_retrieval_security.py` with these assertions:

```python
import pytest
from pystreammcp.retrieval.errors import RetrievalError
from pystreammcp.retrieval.security import (
    check_markdown_image_refs, make_display_path, resolve_ingest_path, validate_qmd_url,
)

def test_outside_root_rejected(tmp_path):
    root = tmp_path / "docs"; root.mkdir()
    outside = tmp_path / "x.md"; outside.write_text("x")
    with pytest.raises(RetrievalError, match="outside") as exc:
        resolve_ingest_path(str(outside), (root.resolve(),), (".md",), 1024)
    assert exc.value.code == "path_outside_allowed_roots"

def test_symlink_rejected_even_inside_root(tmp_path):
    root = tmp_path / "docs"; root.mkdir()
    real = root / "a.md"; real.write_text("x")
    link = root / "b.md"; link.symlink_to(real)
    with pytest.raises(RetrievalError) as exc:
        resolve_ingest_path(str(link), (root.resolve(),), (".md",), 1024)
    assert exc.value.code == "symlink_not_allowed"

def test_html_rejected_unconditionally(tmp_path):
    root = tmp_path / "docs"; root.mkdir()
    html = root / "a.html"; html.write_text("<p>x</p>")
    with pytest.raises(RetrievalError) as exc:
        resolve_ingest_path(str(html), (root.resolve(),), (".html",), 1024)
    assert exc.value.code == "unsupported_extension"

def test_extension_and_size(tmp_path):
    root = tmp_path / "docs"; root.mkdir()
    exe = root / "a.exe"; exe.write_text("x")
    big = root / "b.md"; big.write_bytes(b"x" * 2048)
    with pytest.raises(RetrievalError) as e1:
        resolve_ingest_path(str(exe), (root.resolve(),), (".md",), 4096)
    assert e1.value.code == "unsupported_extension"
    with pytest.raises(RetrievalError) as e2:
        resolve_ingest_path(str(big), (root.resolve(),), (".md",), 1024)
    assert e2.value.code == "file_too_large"

def test_markdown_image_outside_root_rejected_and_remote_ignored(tmp_path):
    root = tmp_path / "docs"; root.mkdir()
    (tmp_path / "outside.png").write_bytes(b"png")
    doc = root / "a.md"
    doc.write_text("![x](../outside.png)\n![r](https://example.com/a.png)\n")
    with pytest.raises(RetrievalError) as exc:
        check_markdown_image_refs(doc.resolve(), (root.resolve(),))
    assert exc.value.code == "path_outside_allowed_roots"

def test_display_path_is_root_qualified(tmp_path):
    root = tmp_path / "docs"; root.mkdir()
    f = root / "a" / "b.md"; f.parent.mkdir(); f.write_text("x")
    assert make_display_path(f.resolve(), (root.resolve(),)) == "docs/a/b.md"

def test_remote_qmd_url_requires_opt_in():
    with pytest.raises(RetrievalError, match="loopback"):
        validate_qmd_url("https://qmd.example.com", allow_remote=False)
    validate_qmd_url("http://127.0.0.1:8181", allow_remote=False)
    validate_qmd_url("https://qmd.example.com", allow_remote=True)
```

- [ ] **Step 6: Run security tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_retrieval_security.py -v`

Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 7: Implement security helpers**

Signatures:

```python
def normalize_extensions(values: Iterable[str]) -> tuple[str, ...]: ...
def resolve_allowed_roots(raw: str | Iterable[str]) -> tuple[Path, ...]: ...
def resolve_ingest_path(
    path: str, roots: tuple[Path, ...], allowed_extensions: tuple[str, ...], max_bytes: int,
) -> tuple[Path, Path, str]: ...
def make_display_path(resolved: Path, roots: tuple[Path, ...]) -> str: ...
def check_markdown_image_refs(resolved: Path, roots: tuple[Path, ...]) -> None: ...
def is_loopback_url(url: str) -> bool: ...
def validate_qmd_url(url: str, allow_remote: bool) -> None: ...
def redact_text(text: str, secrets: Iterable[str] = ()) -> str: ...
def redact_url_userinfo(url: str) -> str: ...
```

`resolve_ingest_path`: expanduser, resolve strict, require regular file, reject HTML extensions always (`.html`, `.htm`, `.xhtml`) regardless of allowlist, match a root, reject any symlink component between root and file, check extension, check size. `make_display_path` prefixes with the root name and handles duplicate root names with an index. `check_markdown_image_refs` handles Markdown and HTML `<img>`, ignores remote/data/fragment refs, resolves local refs and rejects outside/missing. `redact_text` replaces secrets and URL userinfo with `[REDACTED]`.

- [ ] **Step 8: Run security tests**

Run: `.venv/bin/python -m pytest tests/test_retrieval_security.py -v`

Expected: PASS.

- [ ] **Step 9: Checkpoint**

Run: `git status --short`. Do not commit.

---

### Task 2b: Vendored Source Resolution and Update Checks

**Files:**
- Create: `python/pystreammcp/retrieval/deps.py`
- Test: `tests/test_retrieval_deps.py`
- Modify: `python/pystreammcp/retrieval/config.py` (`RagConfig.source_mode`)
- Test: `tests/test_retrieval_config.py`

**Interfaces:**
- Produces: `RagSource(mode, source, rag_path, lightrag_path, version)`
- Produces: `resolve_rag_source(mode, injected=False) -> RagSource`
- Produces: `ensure_rag_import_path(mode) -> RagSource`
- Produces: `vendor_root()`, `load_vendor_lock()`, `compute_tree_sha256(path)`, `verify_vendored_tree(name)`
- Produces: `dependency_status(offline=False, client=None, token=None) -> dict`
- Produces: `check_upstream_updates(...)` and `upstream_exit_code(status)`

- [ ] **Step 1: Write failing dependency-resolution tests**

Create `tests/test_retrieval_deps.py`. Use `importlib.util.find_spec` monkeypatching and the real vendored tree from Task 0; do not import `raganything` or `lightrag`.

```python
import json, sys
import httpx
import pytest
from pystreammcp.retrieval import deps
from pystreammcp.retrieval.errors import RetrievalError

def fake_specs(monkeypatch, present):
    real = __import__("importlib.util", fromlist=["find_spec"]).find_spec
    def find_spec(name, *args, **kwargs):
        if name in {"raganything", "lightrag"}:
            return object() if name in present else None
        return real(name, *args, **kwargs)
    monkeypatch.setattr("importlib.util.find_spec", find_spec)

def test_auto_prefers_consistent_installed_pair(monkeypatch):
    fake_specs(monkeypatch, {"raganything", "lightrag"})
    source = deps.resolve_rag_source("auto")
    assert source.source == "installed" and source.rag_path is None

def test_auto_uses_vendored_pair_when_either_installed_is_missing(monkeypatch):
    fake_specs(monkeypatch, {"raganything"})
    source = deps.resolve_rag_source("auto")
    assert source.source == "vendored"
    assert source.rag_path == deps.vendor_root() / "rag-anything"
    assert source.lightrag_path == deps.vendor_root() / "lightrag"

def test_strict_modes_do_not_mix(monkeypatch):
    fake_specs(monkeypatch, {"raganything", "lightrag"})
    assert deps.resolve_rag_source("vendored").source == "vendored"
    fake_specs(monkeypatch, set())
    with pytest.raises(RetrievalError) as exc:
        deps.resolve_rag_source("installed")
    assert exc.value.code == "missing_dependency"

def test_ensure_import_path_is_idempotent_and_fixed(monkeypatch):
    fake_specs(monkeypatch, set())
    before = list(sys.path)
    try:
        first = deps.ensure_rag_import_path("vendored")
        second = deps.ensure_rag_import_path("vendored")
        assert first == second
        assert sys.path.count(str(first.rag_path)) == 1
        assert sys.path.count(str(first.lightrag_path)) == 1
    finally:
        sys.path[:] = before

def test_injected_bypasses_source_resolution(monkeypatch):
    fake_specs(monkeypatch, set())
    source = deps.resolve_rag_source("vendored", injected=True)
    assert source.source == "injected" and source.rag_path is None

def test_resolution_does_not_import_heavy_packages(monkeypatch):
    fake_specs(monkeypatch, set())
    deps.resolve_rag_source("vendored")
    assert "raganything" not in sys.modules
    assert "lightrag" not in sys.modules

def test_invalid_mode_is_configuration_error():
    with pytest.raises(RetrievalError) as exc:
        deps.resolve_rag_source("network")
    assert exc.value.code == "configuration_error"

def test_tree_verification_detects_edit(tmp_path):
    root = tmp_path / "pkg"; root.mkdir()
    (root / "a.txt").write_text("alpha", encoding="utf-8")
    digest = deps.compute_tree_sha256(root)
    (root / "a.txt").write_text("beta", encoding="utf-8")
    assert deps.compute_tree_sha256(root) != digest

def test_offline_status_reports_corruption(tmp_path, monkeypatch):
    root = tmp_path / "vendor"; root.mkdir()
    names = ("qmd", "rag-anything", "lightrag")
    lock = {"schema": 1, "dependencies": {}}
    for name in names:
        component = root / name; component.mkdir()
        (component / "LICENSE").write_text("MIT", encoding="utf-8")
        (component / "README.md").write_text(name, encoding="utf-8")
        lock["dependencies"][name] = {
            "repo": "https://github.com/example/repo.git",
            "tag": "v1.2.3", "commit": "a" * 40,
            "path": f"vendor/{name}", "ecosystem": "npm" if name == "qmd" else "python",
            "license": "MIT", "tree_sha256": deps.compute_tree_sha256(component),
        }
    (root / "deps.lock.json").write_text(json.dumps(lock), encoding="utf-8")
    monkeypatch.setattr(deps, "vendor_root", lambda: root)
    (root / "qmd" / "README.md").write_text("changed", encoding="utf-8")
    data = deps.dependency_status(offline=True)
    qmd = next(d for d in data["dependencies"] if d["name"] == "qmd")
    assert qmd["state"] == "corrupt"

def test_update_check_parses_stable_tags_and_redacts_token(monkeypatch):
    def handler(request):
        assert request.headers["Authorization"] == "Bearer secret-token"
        return httpx.Response(200, json=[{"name": "v9.9.9-rc1"}, {"name": "v2.9.0"}])
    client = httpx.Client(transport=httpx.MockTransport(handler))
    data = deps.check_upstream_updates(client=client, token="secret-token", components=["qmd"])
    assert data["dependencies"][0]["state"] == "update_available"
    assert data["dependencies"][0]["latest"] == "v2.9.0"
    assert "secret-token" not in json.dumps(data)

def test_update_check_http_failure_is_bounded():
    client = httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(403)))
    data = deps.check_upstream_updates(client=client, components=["qmd"])
    assert data["dependencies"][0]["state"] == "check_failed"
    assert len(data["dependencies"][0]["error"]) <= 500

@pytest.mark.parametrize("status", [404, 500])
def test_update_check_bad_response_is_bounded(status):
    client = httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(status)))
    data = deps.check_upstream_updates(client=client, components=["qmd"])
    assert data["dependencies"][0]["state"] == "check_failed"

def test_update_check_timeout_is_bounded():
    def handler(request):
        raise httpx.ConnectTimeout("timeout")
    client = httpx.Client(transport=httpx.MockTransport(handler))
    data = deps.check_upstream_updates(client=client, components=["qmd"])
    assert data["dependencies"][0]["state"] == "check_failed"
    assert "timeout" in data["dependencies"][0]["error"].lower()

def test_offline_status_verifies_real_vendor_tree():
    data = deps.dependency_status(offline=True)
    assert {d["name"] for d in data["dependencies"]} == {"qmd", "rag-anything", "lightrag"}
    assert all(d["vendored"] == "verified" for d in data["dependencies"])
    assert all(d["latest"] is None for d in data["dependencies"])
```

Add to `tests/test_retrieval_config.py`:

```python
def test_rag_source_mode_validation():
    ok = RetrievalConfig.from_env({
        "PYSTREAMMCP_RAG_ENABLED": "true",
        "PYSTREAMMCP_RAG_SOURCE": "vendored",
    })
    assert ok.rag.source_mode == "vendored" and ok.rag_error is None
    bad = RetrievalConfig.from_env({
        "PYSTREAMMCP_RAG_ENABLED": "true",
        "PYSTREAMMCP_RAG_SOURCE": "network",
    })
    assert "RAG_SOURCE" in bad.rag_error
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_retrieval_deps.py tests/test_retrieval_config.py -v`

Expected: `ModuleNotFoundError` / missing `source_mode`.

- [ ] **Step 3: Add config source mode**

Add `source_mode: str = "auto"` to `RagConfig` and parse `PYSTREAMMCP_RAG_SOURCE`. Only `auto`, `installed`, `vendored` are valid; any other value sets `rag_error` containing `RAG_SOURCE`. Do not validate the selected source at config time beyond the mode string.

- [ ] **Step 4: Implement `deps.py`**

- `vendor_root()` resolves `Path(__file__).resolve().parents[3] / "vendor"`; it never reads the current directory or an environment path.
- `load_vendor_lock()` reads `vendor/deps.lock.json` and validates `schema == 1`, known component names, repository-relative `path` equal to `vendor/<name>`, and 64-character hashes. Missing/invalid lock is `missing_dependency` for RAG resolution. `dependency_status` converts a missing/invalid lock into a bounded status object with `missing` states and exit 2 instead of a traceback.
- `compute_tree_sha256(path)` implements the exact canonical hash from §6.13, rejects symlinks, and excludes `.git`, `__pycache__`, `.pytest_cache`, `.ruff_cache`, `node_modules`, `dist`, `build`, and `*.pyc`.
- `verify_vendored_tree(name)` compares the computed hash with the lock. Cache successful verification by `(resolved_path, expected_hash)`; a mismatch is never cached and raises `RetrievalError("configuration_error", ...)`.
- `resolve_rag_source(mode, injected=False)`:
  - injected -> `RagSource(mode, "injected", None, None, None)`
  - invalid mode -> `configuration_error`
  - installed pair via `importlib.util.find_spec` (import the module, not the function, so tests can patch it) and `find_spec("raganything")`/`find_spec("lightrag")`
  - vendored pair only when both directories exist and `verify_vendored_tree` succeeds
  - `auto`: installed pair, else vendored pair, else `missing_dependency`
  - `installed`: installed pair or `missing_dependency`
  - `vendored`: vendored pair or `missing_dependency`
  - version: installed `importlib.metadata.version` without importing the package; vendored lock tag.
- `ensure_rag_import_path(mode)` resolves first, prepends the two vendored paths only for `vendored`, under a module lock, and is idempotent. It never adds an arbitrary path.
- `check_upstream_updates(client=None, token=None, components=None)` uses `httpx` with a 10-second timeout, no retries, and `Authorization: Bearer <GITHUB_TOKEN>` only when the standard `GITHUB_TOKEN` is present or explicitly passed. It parses `vMAJOR.MINOR.PATCH`, ignores pre-releases, and returns bounded per-component dictionaries. A 403/404/5xx/timeout/network failure is `check_failed` with a bounded `error` (timeouts include the word `timeout`); it never raises into the CLI.
- `dependency_status(offline=False)` verifies local trees first. `offline=True` sets `latest=None`, `state="pinned"`. Online mode calls the update check for verified components only. It always returns `{"schema": 1, "offline": bool, "dependencies": [...]}`.
- `upstream_exit_code(status)` returns 2 for any `corrupt`/`missing`/`check_failed`, 1 for any `update_available`, else 0.
- No module-level import of `raganything`, `lightrag`, or `openai`; no network at import.

- [ ] **Step 5: Run dependency tests**

Run: `.venv/bin/python -m pytest tests/test_retrieval_deps.py tests/test_retrieval_config.py -v`

Expected: PASS.

- [ ] **Step 6: Checkpoint**

Run: `git status --short`. Do not commit.

---

### Task 3: Deterministic Router

**Files:**
- Create: `python/pystreammcp/retrieval/router.py`
- Test: `tests/test_retrieval_router.py`

**Interfaces:**
- Produces: `RoutingDecision(backends: list[BackendName], diagnostics: dict[str, Any])`
- Produces: `route(request, backends: Mapping[BackendName, RetrievalBackend], priority: tuple[BackendName, ...]) -> RoutingDecision`

- [ ] **Step 1: Write failing router tests**

Create `tests/test_retrieval_router.py` using `FakeBackend` and `make_request`:

```python
import pytest
from pystreammcp.retrieval.base import BackendCapabilities
from pystreammcp.retrieval.errors import RetrievalError
from pystreammcp.retrieval.models import BackendName, RequestedBackend
from pystreammcp.retrieval.router import route
from retrieval_helpers import FakeBackend, make_request

QMD, RAG = BackendName.QMD, BackendName.RAG_ANYTHING

def caps(name, modes, content_types, available=True, collection_scoped=False):
    return BackendCapabilities(
        backend=name, enabled=True, configured=True, available=available,
        modes=modes, content_types=content_types, max_limit=50,
        supports_ingestion=name is RAG, supports_full_content=name is RAG,
        score_kind="unavailable", network_egress="local", error=None,
    )

def test_auto_text_uses_priority():
    qmd = FakeBackend("qmd", caps(QMD, ("auto", "hybrid"), ("text",)))
    rag = FakeBackend("rag_anything", caps(RAG, ("auto", "local"), ("text",)))
    d = route(make_request(), {QMD: qmd, RAG: rag}, (QMD, RAG))
    assert d.backends == [QMD]

def test_auto_image_prefers_rag():
    qmd = FakeBackend("qmd", caps(QMD, ("auto",), ("text",)))
    rag = FakeBackend("rag_anything", caps(RAG, ("auto",), ("image",)))
    d = route(make_request(content_type="image"), {QMD: qmd, RAG: rag}, (QMD, RAG))
    assert d.backends == [RAG]

def test_auto_mode_supported_by_one():
    qmd = FakeBackend("qmd", caps(QMD, ("auto",), ("text",)))
    rag = FakeBackend("rag_anything", caps(RAG, ("global",), ("text",)))
    d = route(make_request(mode="global"), {QMD: qmd, RAG: rag}, (QMD, RAG))
    assert d.backends == [RAG]

def test_collections_require_qmd():
    qmd = FakeBackend("qmd", caps(QMD, ("auto",), ("text",), collection_scoped=True))
    d = route(make_request(collections=("docs",)), {QMD: qmd}, (QMD,))
    assert d.backends == [QMD]
    with pytest.raises(RetrievalError) as exc:
        route(make_request(collections=("docs",)), {}, (QMD,))
    assert exc.value.code == "no_available_backend"

def test_explicit_disabled_is_not_configured():
    with pytest.raises(RetrievalError) as exc:
        route(make_request(backend=RequestedBackend.QMD), {}, (QMD,))
    assert exc.value.code == "not_configured"

def test_all_includes_unavailable_for_visibility():
    qmd = FakeBackend("qmd", caps(QMD, ("auto",), ("text",), available=False))
    rag = FakeBackend("rag_anything", caps(RAG, ("auto",), ("text",)))
    d = route(make_request(backend=RequestedBackend.ALL), {QMD: qmd, RAG: rag}, (QMD, RAG))
    assert d.backends == [QMD, RAG]

def test_no_available_backend():
    qmd = FakeBackend("qmd", caps(QMD, ("auto",), ("text",), available=False))
    with pytest.raises(RetrievalError) as exc:
        route(make_request(), {QMD: qmd}, (QMD,))
    assert exc.value.code == "no_available_backend"

def test_explicit_unavailable_is_unavailable():
    qmd = FakeBackend("qmd", caps(QMD, ("auto",), ("text",), available=False))
    with pytest.raises(RetrievalError) as exc:
        route(make_request(backend=RequestedBackend.QMD), {QMD: qmd}, (QMD,))
    assert exc.value.code == "unavailable"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_retrieval_router.py -v`

Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement the router**

Rules from spec §6.6:

1. Explicit backend selects exactly it; registered-but-unavailable raises `unavailable`; unregistered/disabled raises `not_configured`.
2. `all` selects every registered enabled backend, including unavailable ones, so group status is visible.
3. `auto`:
   - non-empty `collections` requires QMD; if QMD missing/unavailable -> `no_available_backend`.
   - non-text content type picks an available backend advertising it, preferring RAG.
   - mode supported by exactly one available backend chooses it.
   - otherwise first available in priority.
4. No available backend -> `no_available_backend`.
5. Diagnostics list skipped backends and reasons.
6. No network calls.

- [ ] **Step 4: Run tests**

Run: `.venv/bin/python -m pytest tests/test_retrieval_router.py -v`

Expected: PASS.

- [ ] **Step 5: Checkpoint**

Run: `git status --short`. Do not commit.

---

### Task 4: Service Orchestration, Time Budgets, and Cleanup

**Files:**
- Create: `python/pystreammcp/retrieval/service.py`
- Modify: `python/pystreammcp/retrieval/__init__.py`
- Test: `tests/test_retrieval_service.py`

**Interfaces:**
- Produces: `UnavailableBackend(name, error)`
- Produces: `RetrievalService(backends, priority=(QMD, RAG), max_workers=4)`
- Produces: `.from_env(env=None)`, `.search(request)`, `.capabilities(include_health=True)`, `.health()`, `.ingest(path, force_multimodal=False)`, `.close()`

- [ ] **Step 1: Write failing service tests**

Create `tests/test_retrieval_service.py`:

```python
import pytest
from pystreammcp.retrieval.errors import RetrievalError
from pystreammcp.retrieval.models import BackendName, RetrievalHit
from pystreammcp.retrieval.service import RetrievalService, UnavailableBackend
from retrieval_helpers import FakeBackend, make_request

QMD, RAG = BackendName.QMD, BackendName.RAG_ANYTHING

def hit(backend=QMD):
    return RetrievalHit(
        backend=backend, rank=1, document_id="d1", title="T",
        source_uri=f"{backend.value}://d1", locator={"kind": "line", "line": 1},
        excerpt="alpha", content=None, score=1.0,
        score_kind="qmd_query_relevance", metadata={},
    )

def test_success_grouping():
    service = RetrievalService([FakeBackend("qmd", hits=[hit()])])
    r = service.search(make_request())
    assert r.status == "success"
    assert r.groups[0].backend is QMD
    assert r.groups[0].hits[0].excerpt == "alpha"
    service.close()

def test_partial_when_one_group_fails():
    qmd = FakeBackend("qmd", hits=[hit()])
    rag = FakeBackend("rag_anything", error=RetrievalError("query_failed", "boom", backend=RAG))
    service = RetrievalService([qmd, rag])
    r = service.search(make_request(backend="all"))
    assert r.status == "partial"
    assert [g.status for g in r.groups] == ["ok", "error"]
    service.close()

def test_no_fallback_after_qmd_failure():
    qmd = FakeBackend("qmd", error=RetrievalError("unavailable", "down", backend=QMD, retryable=True))
    rag = FakeBackend("rag_anything", hits=[hit(RAG)])
    service = RetrievalService([qmd, rag])
    r = service.search(make_request())
    assert r.status == "error"
    assert [g.backend for g in r.groups] == [QMD]
    assert r.groups[0].status == "unavailable"
    service.close()

def test_timeout_group():
    service = RetrievalService([FakeBackend("qmd", delay=0.25, hits=[hit()])])
    r = service.search(make_request(time_budget_ms=100))
    assert r.groups[0].status == "timeout"
    assert r.status == "error"
    service.close()

def test_invalid_request_does_not_dispatch():
    b = FakeBackend("qmd")
    service = RetrievalService([b])
    for kwargs in ({"query": ""}, {"limit": 0}, {"limit": 51},
                   {"max_content_chars": -1}, {"time_budget_ms": 0},
                   {"collections": tuple(f"c{i}" for i in range(33))}):
        with pytest.raises(RetrievalError) as exc:
            service.search(make_request(**kwargs))
        assert exc.value.code == "invalid_request"
    assert b.requests == []
    service.close()

def test_empty_registry_is_no_available_backend():
    service = RetrievalService([])
    with pytest.raises(RetrievalError) as exc:
        service.search(make_request())
    assert exc.value.code == "no_available_backend"
    service.close()

def test_broken_backend_does_not_crash_and_other_works():
    bad = UnavailableBackend(QMD, RetrievalError("configuration_error", "bad config"))
    good = FakeBackend("rag_anything", hits=[hit(RAG)])
    service = RetrievalService([bad, good])
    caps = service.capabilities(include_health=False)
    assert caps["backends"][0]["available"] is False
    assert service.search(make_request()).groups[0].backend is RAG
    service.close()

def test_ingest_requires_rag_and_delegates():
    rag = FakeBackend("rag_anything")
    service = RetrievalService([rag])
    result = service.ingest("/tmp/a.md", force_multimodal=True)
    assert result.status == "processed"
    assert rag.ingest_calls == [("/tmp/a.md", True)]
    service.close()
    with pytest.raises(RetrievalError) as exc:
        RetrievalService([]).ingest("/tmp/a.md")
    assert exc.value.code == "not_configured"

def test_close_is_idempotent():
    b = FakeBackend("qmd")
    service = RetrievalService([b])
    service.close(); service.close()
    assert b.closed is True
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_retrieval_service.py -v`

Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement service**

`UnavailableBackend` returns `BackendCapabilities(enabled=True, configured=False, available=False, error=error.to_dict(), ...)`; `health` returns `BackendHealth(available=False, status="unavailable", message=error.message, elapsed_ms=0)`; search/ingest raise the stored error.

`RetrievalService`:

- Validate query 1..8000; limit 1..50; content 0..20000; budget 1..300000 ms; collections <=32; intent <=1000; known backend/mode/content type. Invalid bounds -> `invalid_request`; unknown backend -> `invalid_backend`; unknown mode -> `unsupported_mode`; unknown content type -> `unsupported_content_type`.
- Route with Task 3. If no backends, `no_available_backend`.
- Submit selected backends to a persistent `ThreadPoolExecutor`; wait at most `time_budget_ms/1000`. Wrapper records elapsed ms. Paths: group `timeout` if unfinished; `unavailable` for `unavailable`/`not_configured`/`missing_dependency`/`configuration_error`; `error` otherwise.
- Request `timeout_s = time_budget_ms / 1000.0`; backend clamps to its configured timeout.
- Top status: `success` if all groups `ok`; `partial` if at least one `ok` and one not; `error` if none `ok`.
- `capabilities(include_health=True)` returns `{"backends": [caps.to_dict() + optional "health"]}`. `health()` returns backend healths. No model load.
- `from_env`: build QMD/RAG only when requested. If section error, register `UnavailableBackend`. For RAG with no provider/factory, still construct backend (it reports unavailable) so capabilities explain it. If a constructor raises, register `UnavailableBackend`.
- `ingest(path, force_multimodal=False)` requires exactly one registered `rag_anything`; delegate. Missing -> `not_configured`; more than one -> `configuration_error`.
- `close()` closes backends and executor once, `cancel_futures=True`.

- [ ] **Step 4: Run tests**

Run: `.venv/bin/python -m pytest tests/test_retrieval_service.py -v`

Expected: PASS.

- [ ] **Step 5: Checkpoint**

Run: `git status --short`. Do not commit.

---

### Task 5: QMD HTTP Adapter

**Files:**
- Create: `python/pystreammcp/retrieval/qmd.py`
- Modify: `python/pystreammcp/retrieval/__init__.py`
- Test: `tests/test_retrieval_qmd.py`

**Interfaces:**
- Produces: `QmdBackend(config: QmdConfig, transport: httpx.BaseTransport | None = None)`

- [ ] **Step 1: Write failing QMD tests**

Create `tests/test_retrieval_qmd.py`:

```python
import json
import httpx
import pytest
from pystreammcp.retrieval.base import BackendSearchRequest
from pystreammcp.retrieval.config import QmdConfig
from pystreammcp.retrieval.errors import RetrievalError
from pystreammcp.retrieval.qmd import QmdBackend

def cfg(**kw):
    values = dict(enabled=True, url="http://127.0.0.1:8181",
                  collections=("docs",), timeout_s=2.0, health_timeout_s=0.2)
    values.update(kw)
    return QmdConfig(**values)

def req(**kw):
    values = dict(query="alpha", mode=None, collections=(), content_type=None,
                  limit=5, include_content=False, max_content_chars=100,
                  timeout_s=2.0, intent="find")
    values.update(kw)
    return BackendSearchRequest(**values)

def test_auto_payload_and_mapping():
    seen = {}
    def handler(request):
        seen["url"] = str(request.url)
        seen["json"] = json.loads(request.content)
        return httpx.Response(200, json={"results": [{
            "docid": "d1", "file": "a.md", "title": "A", "score": 1.5,
            "context": "ctx", "line": 3, "snippet": "alpha beta",
            "metadata": {"tag": "x"},
        }]})
    b = QmdBackend(cfg(), transport=httpx.MockTransport(handler))
    result = b.search(req(include_content=True))
    assert seen["url"].endswith("/query")
    assert seen["json"] == {
        "searches": [{"type": "lex", "query": "alpha"}, {"type": "vec", "query": "alpha"}],
        "collections": ["docs"], "limit": 5, "intent": "find", "rerank": True,
    }
    hit = result.hits[0]
    assert hit.document_id == "d1"
    assert hit.source_uri == "qmd://docs/a.md"
    assert hit.locator == {"kind": "line", "line": 3}
    assert hit.content == "alpha beta"
    assert hit.score_kind == "qmd_query_relevance"
    b.close()

def test_mode_matrix():
    def payload_for(mode):
        seen = {}
        def handler(request):
            seen.update(json.loads(request.content))
            return httpx.Response(200, json={"results": []})
        b = QmdBackend(cfg(), transport=httpx.MockTransport(handler))
        b.search(req(mode=mode))
        b.close()
        return seen
    assert payload_for("hybrid")["rerank"] is True
    assert payload_for("lex")["searches"] == [{"type": "lex", "query": "alpha"}]
    assert payload_for("vector")["searches"] == [{"type": "vec", "query": "alpha"}]
    assert payload_for("hyde")["searches"] == [{"type": "hyde", "query": "alpha"}]

def test_collection_subset_enforced():
    b = QmdBackend(cfg(), transport=httpx.MockTransport(lambda r: httpx.Response(200, json={"results": []})))
    b.search(req(collections=("docs",)))
    with pytest.raises(RetrievalError) as exc:
        b.search(req(collections=("other",)))
    assert exc.value.code == "collection_not_allowed"
    b.close()

def test_error_mapping_and_health():
    b = QmdBackend(cfg(), transport=httpx.MockTransport(lambda r: httpx.Response(503, text="down")))
    with pytest.raises(RetrievalError) as exc:
        b.search(req())
    assert exc.value.code == "unavailable" and exc.value.retryable is True
    b.close()
    b2 = QmdBackend(cfg(), transport=httpx.MockTransport(lambda r: (_ for _ in ()).throw(httpx.TimeoutException("slow"))))
    assert b2.health().status == "unavailable"
    b2.close()

def test_capabilities_egress():
    local = QmdBackend(cfg(), transport=httpx.MockTransport(lambda r: httpx.Response(200, json={})))
    remote = QmdBackend(cfg(url="https://qmd.example.com", allow_remote=True),
                        transport=httpx.MockTransport(lambda r: httpx.Response(200, json={})))
    assert local.capabilities().network_egress == "local"
    assert remote.capabilities().network_egress == "remote"
    assert local.capabilities().supports_full_content is False
    local.close(); remote.close()
```

Also add tests for 400 (`http_error`), 404/5xx (`unavailable`), invalid JSON (`invalid_response`), result truncation when upstream returns more than `limit`, and metadata bounds.

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_retrieval_qmd.py -v`

Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `QmdBackend`**

- One `httpx.Client` with base URL, timeout, `trust_env`, injected transport.
- `POST /query`; `GET /health` with health timeout.
- Mode table exactly: `auto`/`hybrid` -> `[lex, vec]`, rerank true; `keyword`/`lex`/`full_text` -> `[lex]`, rerank false; `semantic`/`vec`/`vector` -> `[vec]`, rerank false; `hyde` -> `[hyde]`, rerank false.
- Use configured collections or a request subset; reject outside allowlist with `collection_not_allowed`.
- Payload keys: `searches`, `collections`, `limit`, `intent` when supplied, `rerank`.
- Map `docid` -> `document_id`; `file` + collection -> `qmd://<collection>/<file>` (or pass through an upstream `qmd://` URI); `snippet` -> excerpt/content; `locator={"kind":"line","line":...}`; metadata only `docid`, `context`, `line`, and flat scalar/list upstream metadata, bounded.
- Errors: 400 -> `http_error`; 403/404/5xx -> `unavailable`; timeout -> `timeout`; connection -> `unavailable`; invalid payload -> `invalid_response`.
- Capabilities: modes tuple above, `content_types=("text",)`, `max_limit=50`, `supports_ingestion=False`, `supports_full_content=False`, `score_kind="qmd_query_relevance"`, `network_egress` local/remote, `error=None`.
- Health: `status` `ok|unavailable|error`, `elapsed_ms`.

- [ ] **Step 4: Run tests**

Run: `.venv/bin/python -m pytest tests/test_retrieval_qmd.py -v`

Expected: PASS.

- [ ] **Step 5: Checkpoint**

Run: `git status --short`. Do not commit.

---

### Task 6: RAG-Anything Worker Loop and Query

**Files:**
- Create: `python/pystreammcp/retrieval/rag_anything.py`
- Create: `tests/retrieval_rag_fakes.py`
- Test: `tests/test_retrieval_rag.py`

**Interfaces:**
- Produces: `RAGAnythingBackend(config: RagConfig, engine_factory: Callable[[], Any] | None = None)`
- Consumes: `deps.resolve_rag_source`, `deps.ensure_rag_import_path`
- Produces `.search`, `.capabilities`, `.health`, `.close`; ingestion in Task 7

- [ ] **Step 1: Write fake engine and failing query tests**

Create `tests/retrieval_rag_fakes.py`:

```python
import asyncio
import importlib.util
import sys
import types

class FakeQueryParam:
    def __init__(self, **kwargs): self.kwargs = kwargs

def install_fake_lightrag(monkeypatch):
    mod = types.ModuleType("lightrag")
    mod.__path__ = []
    mod.QueryParam = FakeQueryParam
    monkeypatch.setitem(sys.modules, "lightrag", mod)
    real = importlib.util.find_spec
    monkeypatch.setattr(
        "importlib.util.find_spec",
        lambda name, *a, **k: object() if name in {"raganything", "lightrag"} else real(name, *a, **k),
    )
    return mod

class FakeDocStatus:
    def __init__(self, records=None): self.records = records or {}
    async def get_by_id(self, doc_id): return self.records.get(doc_id)

class FakeTextChunks:
    def __init__(self, records=None): self.records = records or {}; self.calls = []
    async def get_by_ids(self, ids):
        self.calls.append(list(ids))
        return [self.records[i] for i in ids if i in self.records]

class FakeLightRAG:
    def __init__(self, payload=None, delay=0.0, page_records=None):
        self.payload = payload or {
            "status": "success", "message": "ok",
            "data": {
                "chunks": [{"content": "alpha beta", "file_path": "/docs/a.md",
                            "chunk_id": "c1", "reference_id": "r1"}],
                "entities": [], "relationships": [],
                "metadata": {"processing_info": {"total_chunks": 1}},
            },
        }
        self.delay = delay
        self.query_calls = []
        self.text_chunks = FakeTextChunks(page_records or {})
        self.doc_status = FakeDocStatus()
    async def aquery_data(self, query, param):
        self.query_calls.append((query, param))
        if self.delay: await asyncio.sleep(self.delay)
        return self.payload

class FakeRagEngine:
    def __init__(self, lightrag): self.lightrag = lightrag; self.calls = []
    async def process_document_complete(self, **kwargs):
        self.calls.append(kwargs)
        self.lightrag.doc_status.records[kwargs["doc_id"]] = {"status": "processed"}
```

Create `tests/test_retrieval_rag.py` with a helper:

```python
import pytest
from pystreammcp.retrieval.base import BackendSearchRequest
from pystreammcp.retrieval.config import RagConfig, RagProviderConfig
from pystreammcp.retrieval.errors import RetrievalError
from pystreammcp.retrieval.rag_anything import RAGAnythingBackend
from retrieval_rag_fakes import FakeLightRAG, FakeRagEngine, install_fake_lightrag

@pytest.fixture(autouse=True)
def _fake_lightrag(monkeypatch):
    install_fake_lightrag(monkeypatch)

def provider():
    return RagProviderConfig(
        llm_model="m", llm_base_url="http://127.0.0.1:1234/v1", llm_api_key="k",
        embedding_model="e", embedding_base_url="http://127.0.0.1:1234/v1",
        embedding_api_key="k", embedding_dim=8, embedding_max_tokens=128,
    )

def rag_config(tmp_path, **kw):
    values = dict(enabled=True, working_dir=tmp_path / "rag",
                  parsed_dir=tmp_path / "rag" / "parsed",
                  allowed_roots=(tmp_path,), allowed_extensions=(".md",),
                  max_file_mb=1, query_timeout_s=2.0, ingest_timeout_s=5.0,
                  provider_name="openai_compatible", provider=provider())
    values.update(kw)
    return RagConfig(**values)

def req(**kw):
    values = dict(query="alpha", mode=None, collections=(), content_type=None,
                  limit=5, include_content=False, max_content_chars=100,
                  timeout_s=2.0, intent=None)
    values.update(kw)
    return BackendSearchRequest(**values)

def backend(tmp_path, light, **kw):
    engine = FakeRagEngine(light)
    return RAGAnythingBackend(rag_config(tmp_path, **kw), engine_factory=lambda: engine), engine

def test_capabilities_does_not_load_engine(tmp_path):
    calls = []
    b = RAGAnythingBackend(rag_config(tmp_path), engine_factory=lambda: calls.append(1) or FakeRagEngine(FakeLightRAG()))
    caps = b.capabilities()
    assert caps.available is True and caps.supports_ingestion is True
    assert caps.supports_full_content is True
    assert caps.score_kind == "unavailable"
    assert calls == [] and b._thread is None
    b.close()

def test_health_does_not_load_engine(tmp_path):
    calls = []
    b = RAGAnythingBackend(rag_config(tmp_path), engine_factory=lambda: calls.append(1) or FakeRagEngine(FakeLightRAG()))
    assert b.health().status == "ok"
    assert calls == []
    b.close()

def test_search_maps_chunks_and_pages(tmp_path):
    light = FakeLightRAG(page_records={"c1": {"page_idx": 2, "page_idx_end": 3, "full_doc_id": "d1"}})
    b, _ = backend(tmp_path, light)
    result = b.search(req())
    hit = result.hits[0]
    assert hit.backend.value == "rag_anything"
    assert hit.document_id == "d1"
    assert hit.title == "a"
    assert hit.source_uri == "rag://docs/a.md"
    assert hit.locator == {"kind": "chunk", "chunk_id": "c1", "reference_id": "r1", "page": 2}
    assert hit.metadata["page_end"] == 3
    assert hit.score is None and hit.score_kind == "unavailable"
    assert result.diagnostics["dependency_source"] == "injected"
    b.close()

def test_auto_mode_uses_configured_query_mode(tmp_path):
    light = FakeLightRAG()
    b, _ = backend(tmp_path, light, query_mode="global")
    b.search(req(mode="auto"))
    assert light.query_calls[0][1].kwargs["mode"] == "global"
    assert light.query_calls[0][1].kwargs["top_k"] == 5
    assert light.query_calls[0][1].kwargs["chunk_top_k"] == 5
    b.close()

def test_qmd_only_mode_is_unsupported(tmp_path):
    b, _ = backend(tmp_path, FakeLightRAG())
    with pytest.raises(RetrievalError) as exc:
        b.search(req(mode="lex"))
    assert exc.value.code == "unsupported_mode"
    b.close()

def test_capabilities_reports_missing_dependency(monkeypatch, tmp_path):
    from pystreammcp.retrieval import deps
    def fail(mode, injected=False):
        raise RetrievalError("missing_dependency", "install rag-anything")
    monkeypatch.setattr(deps, "resolve_rag_source", fail)
    b = RAGAnythingBackend(rag_config(tmp_path))
    caps = b.capabilities()
    assert caps.available is False
    assert caps.error["code"] == "missing_dependency"
    b.close()

def test_injected_factory_reports_unknown_egress(tmp_path):
    b = RAGAnythingBackend(rag_config(tmp_path), engine_factory=lambda: FakeRagEngine(FakeLightRAG()))
    assert b.capabilities().network_egress == "unknown"
    b.close()

def test_query_exception_is_query_failed(tmp_path):
    light = FakeLightRAG()
    async def fail(*args, **kwargs):
        raise RuntimeError("upstream boom")
    light.aquery_data = fail
    b, _ = backend(tmp_path, light)
    with pytest.raises(RetrievalError) as exc:
        b.search(req())
    assert exc.value.code == "query_failed"
    b.close()

def test_timeout_and_close_are_bounded(tmp_path):
    b, _ = backend(tmp_path, FakeLightRAG(delay=0.5), query_timeout_s=0.05)
    with pytest.raises(RetrievalError) as exc:
        b.search(req(timeout_s=0.05))
    assert exc.value.code == "timeout"
    b.close()
    assert b._thread is None

def test_missing_lightrag_and_missing_aquery_are_specific(tmp_path):
    engine = FakeRagEngine(FakeLightRAG())
    engine.lightrag = None
    b = RAGAnythingBackend(rag_config(tmp_path), engine_factory=lambda: engine)
    with pytest.raises(RetrievalError) as exc:
        b.search(req())
    assert exc.value.code == "index_not_initialized"
    b.close()
    class NoQuery:
        def __init__(self): self.lightrag = object()
        async def process_document_complete(self, **kw): pass
    b2 = RAGAnythingBackend(rag_config(tmp_path), engine_factory=NoQuery)
    with pytest.raises(RetrievalError) as exc:
        b2.search(req())
    assert exc.value.code == "upstream_unsupported_version"
    b2.close()

def test_include_content_and_empty_results(tmp_path):
    b, _ = backend(tmp_path, FakeLightRAG())
    hit = b.search(req(include_content=True, max_content_chars=5)).hits[0]
    assert hit.content == "alpha"
    b.close()
    empty = FakeLightRAG(payload={"status": "success", "data": {"chunks": []}})
    b2, _ = backend(tmp_path, empty)
    result = b2.search(req())
    assert result.hits == [] and result.diagnostics["chunk_count"] == 0
    b2.close()
```

Add tests: QMD-only mode (`lex`) -> `unsupported_mode`; auto maps to `config.query_mode`; query exception -> `query_failed`; missing dependency -> capabilities unavailable with `missing_dependency`; custom factory egress `unknown`; installed/vendored source diagnostics; strict `installed`/`vendored` modes.

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_retrieval_rag.py -v`

Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement worker and query**

- Resolve dependencies with `deps.resolve_rag_source(config.source_mode, injected=engine_factory is not None)`; no import at module import.
- Before creating the built-in provider engine, call `deps.ensure_rag_import_path(config.source_mode)`. An injected factory bypasses source resolution and reports `dependency_source="injected"`.
- One daemon thread + private event loop, started on first search/ingest. All engine creation/calls on that loop. Serialize with `threading.Lock`.
- `_run` uses `asyncio.run_coroutine_threadsafe(asyncio.wait_for(...))`; timeout cancels and raises `timeout`.
- `close()` finalizes storages if supported, stops loop, joins with bounded timeout, idempotent. Closed -> `closed`.
- Capabilities: dependency installed/configured/available; parser, parse method, modes `("auto","hybrid","local","global","naive","mix")`, ingest extensions and roots count, content types text + image only if vision configured and flag; table/equation per flags; `supports_full_content=True`; `score_kind="unavailable"`; egress `local` for loopback provider hosts, `remote` for remote, `unknown` for custom factory. A resolution failure returns unavailable with `missing_dependency`/`configuration_error`, without raising from capabilities.
- Health: configured/initialized message; no engine load; `ok` when configured.
- Query mode: `None`/`auto` -> `config.query_mode`; accept hybrid/local/global/naive/mix; QMD-only modes (`keyword`, `lex`, `full_text`, `semantic`, `vec`, `vector`, `hyde`) -> `unsupported_mode`.
- Import `QueryParam` lazily from `lightrag` after `ensure_rag_import_path`; build `QueryParam(mode=..., top_k=limit, chunk_top_k=limit)` and omit unsupported rerank args.
- `await lightrag.aquery_data(query, param)`; require `status=="success"` and `data.chunks` list. Missing lightrag -> `index_not_initialized`; missing `aquery_data` -> `upstream_unsupported_version`; exception -> `query_failed`.
- Chunk mapping: `document_id` from `full_doc_id` or `doc_id`; title from display path stem; `source_uri=rag://<display_path>`; locator `{"kind":"chunk","chunk_id","reference_id","page"}`; metadata contains only `reference_id`, `chunk_id`, `page`, and `page_end` when available; `score=None`; `score_kind="unavailable"`; excerpt normalized; content bounded.
- Page enrichment via `get_by_ids` (`page_idx`, `page_idx_end`, `full_doc_id`), non-fatal.
- Diagnostics: `dependency_source`, `dependency_version` when known, mode, chunk_count, page_enrichment, numeric processing info. Never absolute vendored paths or secrets.

- [ ] **Step 4: Run tests**

Run: `.venv/bin/python -m pytest tests/test_retrieval_rag.py -v`

Expected: PASS.

- [ ] **Step 5: Checkpoint**

Run: `git status --short`. Do not commit.

---

### Task 7: Guarded RAG Ingestion

**Files:**
- Modify: `python/pystreammcp/retrieval/rag_anything.py`
- Test: extend `tests/test_retrieval_rag.py` or create `tests/test_retrieval_rag_ingest.py`

**Interfaces:**
- Produces: `.ingest(path, force_multimodal=False) -> IngestionResult`

- [ ] **Step 1: Write failing ingestion tests**

```python
import hashlib

def write_doc(root, name="doc.md", text="# alpha\n"):
    path = root / name; path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8"); return path

def test_ingest_hash_status_and_force(tmp_path):
    doc = write_doc(tmp_path)
    b, engine = backend(tmp_path, FakeLightRAG())
    first = b.ingest(str(doc))
    expected = "pystreammcp-" + hashlib.sha256(doc.read_bytes()).hexdigest()[:32]
    assert first.document_id == expected
    assert first.display_path == f"{tmp_path.name}/doc.md"
    assert first.status == "processed" and first.skipped is False
    assert engine.calls[0]["doc_id"] == expected
    assert engine.calls[0]["force_multimodal_reprocess"] is False
    second = b.ingest(str(doc))
    assert second.status == "processed" and second.skipped is True
    assert len(engine.calls) == 1
    third = b.ingest(str(doc), force_multimodal=True)
    assert third.skipped is False
    assert len(engine.calls) == 2
    assert engine.calls[1]["force_multimodal_reprocess"] is True
    b.close()

def test_policy_failures_happen_before_engine(tmp_path):
    b, engine = backend(tmp_path, FakeLightRAG())
    outside = tmp_path.parent / "outside.md"; outside.write_text("x")
    with pytest.raises(RetrievalError) as exc:
        b.ingest(str(outside))
    assert exc.value.code == "path_outside_allowed_roots"
    link = tmp_path / "link.md"; link.symlink_to(write_doc(tmp_path, "real.md"))
    with pytest.raises(RetrievalError) as exc:
        b.ingest(str(link))
    assert exc.value.code == "symlink_not_allowed"
    html = tmp_path / "a.html"; html.write_text("<p>x</p>")
    with pytest.raises(RetrievalError) as exc:
        b.ingest(str(html))
    assert exc.value.code == "unsupported_extension"
    assert engine.calls == []
    b.close()

def test_markdown_image_and_oversize_rejected(tmp_path):
    root = tmp_path / "docs"; root.mkdir()
    (tmp_path / "outside.png").write_bytes(b"png")
    doc = root / "a.md"; doc.write_text("![x](../outside.png)\n")
    b, engine = backend(tmp_path, FakeLightRAG(),
                        allowed_roots=(root,), allowed_extensions=(".md", ".png"))
    with pytest.raises(RetrievalError) as exc:
        b.ingest(str(doc))
    assert exc.value.code == "path_outside_allowed_roots"
    assert engine.calls == []
    b.close()
    big = root / "big.md"; big.write_bytes(b"x" * 2048)
    b2, engine2 = backend(tmp_path, FakeLightRAG(), allowed_roots=(root,),
                          allowed_extensions=(".md",), max_file_mb=0)
    with pytest.raises(RetrievalError) as exc:
        b2.ingest(str(big))
    assert exc.value.code == "file_too_large"
    assert engine2.calls == []
    b2.close()

def test_missing_roots_is_configuration_error(tmp_path):
    b, engine = backend(tmp_path, FakeLightRAG(), allowed_roots=())
    with pytest.raises(RetrievalError) as exc:
        b.ingest(str(write_doc(tmp_path)))
    assert exc.value.code == "configuration_error"
    assert engine.calls == []
    b.close()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_retrieval_rag_ingest.py -v`

Expected: FAIL because `ingest` is missing.

- [ ] **Step 3: Implement ingestion**

Order: closed check; config check; require roots; `resolve_ingest_path`; Markdown image check for `.md`/`.markdown`; compute `document_id = "pystreammcp-" + sha256(file bytes)[:32]`; display path; ensure working/parsed dirs; get engine; check `doc_status.get_by_id` and skip if processed unless `force_multimodal`; call `process_document_complete(file_path=str(resolved), file_name=display_path, doc_id=document_id, output_dir=str(parsed_dir), force_multimodal_reprocess=force_multimodal, parse_method=config.parse_method)`; re-read status; map `processed/partial/failed`; timeout -> `timeout` with "upstream may still be running"; other -> `ingest_failed`.

`content_types`: text always; image only when vision configured and image flag; table/equation per flags. No deletion, no batch, no HTML. Policy failures do no hashing or engine work.

- [ ] **Step 4: Run tests**

Run: `.venv/bin/python -m pytest tests/test_retrieval_rag_ingest.py -v`

Expected: PASS.

- [ ] **Step 5: Checkpoint**

Run: `git status --short`. Do not commit.

---

### Task 8: OpenAI-Compatible Provider Factory

**Files:**
- Create: `python/pystreammcp/retrieval/providers.py`
- Test: `tests/test_retrieval_rag_provider.py`

**Interfaces:**
- Produces: `validate_provider_config(config: RagConfig) -> str | None`
- Produces: `async build_openai_compatible_engine(config: RagConfig) -> Any`
- Consumes: `deps.ensure_rag_import_path(config.source_mode)`

- [ ] **Step 1: Write failing provider tests**

```python
import asyncio, sys, types
import pytest
from pystreammcp.retrieval.config import RagConfig, RagProviderConfig
from pystreammcp.retrieval.errors import RetrievalError
from pystreammcp.retrieval.providers import build_openai_compatible_engine, validate_provider_config

def provider(**kw):
    values = dict(llm_model="m", llm_base_url="http://127.0.0.1:1234/v1",
                  llm_api_key="sk-secret", embedding_model="e",
                  embedding_base_url="http://127.0.0.1:1234/v1",
                  embedding_api_key="sk-secret", embedding_dim=8,
                  embedding_max_tokens=128)
    values.update(kw); return RagProviderConfig(**values)

def cfg(tmp_path, **kw):
    values = dict(enabled=True, working_dir=tmp_path, parsed_dir=tmp_path / "parsed",
                  allowed_roots=(tmp_path,), provider_name="openai_compatible",
                  provider=provider())
    values.update(kw); return RagConfig(**values)

def test_validation_names_missing_field(tmp_path):
    assert validate_provider_config(cfg(tmp_path)) is None
    assert "LLM_MODEL" in validate_provider_config(cfg(tmp_path, provider=provider(llm_model="")))

def test_missing_dependency(monkeypatch, tmp_path):
    import importlib.util
    real = importlib.util.find_spec
    monkeypatch.setattr(importlib.util, "find_spec",
                        lambda name, *a, **k: None if name in {"raganything", "lightrag"} else real(name, *a, **k))
    with pytest.raises(RetrievalError) as exc:
        asyncio.run(build_openai_compatible_engine(cfg(tmp_path)))
    assert exc.value.code == "missing_dependency"
    assert "rag-anything" in exc.value.message

def test_factory_wires_upstream(monkeypatch, tmp_path):
    calls = {}
    class LightRAG:
        def __init__(self, **kw): calls["lightrag"] = kw
        async def initialize_storages(self): calls["storages"] = True
        async def initialize_pipeline_status(self): calls["pipeline"] = True
    class RAGAnything:
        def __init__(self, **kw): calls["rag"] = kw
    class Config:
        def __init__(self, **kw): calls["config"] = kw
    async def complete(*a, **k): return "ok"
    async def embed(*a, **k): return [[0.0]]
    class EmbeddingFunc:
        def __init__(self, **kw): calls["embedding"] = kw
    light = types.ModuleType("lightrag"); light.LightRAG = LightRAG; light.__path__ = []
    llm = types.ModuleType("lightrag.llm"); llm.__path__ = []
    oa = types.ModuleType("lightrag.llm.openai")
    oa.openai_complete_if_cache = complete
    oa.openai_embed = types.SimpleNamespace(func=embed)
    utils = types.ModuleType("lightrag.utils"); utils.EmbeddingFunc = EmbeddingFunc
    rag = types.ModuleType("raganything"); rag.RAGAnything = RAGAnything; rag.RAGAnythingConfig = Config
    for name, mod in [("lightrag", light), ("lightrag.llm", llm),
                      ("lightrag.llm.openai", oa), ("lightrag.utils", utils),
                      ("raganything", rag)]:
        monkeypatch.setitem(sys.modules, name, mod)
    monkeypatch.setattr("importlib.util.find_spec", lambda name, *a, **k: object())
    engine = asyncio.run(build_openai_compatible_engine(cfg(tmp_path)))
    assert isinstance(engine, RAGAnything)
    assert calls["storages"] is True and calls["pipeline"] is True
    assert calls["rag"]["lightrag"] is not None
    assert "sk-secret" not in repr(calls)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_retrieval_rag_provider.py -v`

Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement provider**

- Validate `config.provider` and required fields; return first missing env-style name (`LLM_MODEL`, `LLM_BASE_URL`, `LLM_API_KEY`, `EMBED_MODEL`, `EMBED_BASE_URL`, `EMBED_DIM`).
- Call `deps.ensure_rag_import_path(config.source_mode)` first; it selects installed or vendored consistently.
- Check `find_spec("raganything")` and `find_spec("lightrag")`; raise `missing_dependency` with the selected source and install hint.
- Import upstream inside the function.
- Build text/vision completion closures from `openai_complete_if_cache`; build `EmbeddingFunc` with `openai_embed.func`, explicit `embedding_dim`, `max_token_size`.
- Build `RAGAnythingConfig(working_dir=..., parser=..., parse_method=..., enable_image_processing=..., enable_table_processing=..., enable_equation_processing=...)`.
- Build `LightRAG(working_dir=..., llm_model_func=..., embedding_func=...)`; `await initialize_storages()`; `await initialize_pipeline_status()`.
- Return `RAGAnything(config=..., lightrag=..., vision_model_func=...)`.
- Never log keys, content, or URLs with credentials. No network call during configuration/health/capabilities.

- [ ] **Step 4: Run tests**

Run: `.venv/bin/python -m pytest tests/test_retrieval_rag_provider.py -v`

Expected: PASS.

- [ ] **Step 5: Checkpoint**

Run: `git status --short`. Do not commit.

---

### Task 9: MCP Tools

**Files:**
- Modify: `python/pystreammcp/mcp_server.py`
- Test: `tests/test_retrieval_mcp.py`

**Interfaces:**
- Produces: `PyStreamMCPServer(..., retrieval_service=None)`, `.close()`
- Produces tools: `pystreammcp_retrieval_search`, `pystreammcp_retrieval_capabilities`, `pystreammcp_rag_ingest`
- Produces arg models: `RetrievalSearchToolArgs`, `RetrievalCapabilitiesToolArgs`, `RagIngestToolArgs`

- [ ] **Step 1: Write failing MCP tests**

```python
import json
from pystreammcp.mcp_server import PyStreamMCPServer
from pystreammcp.retrieval.base import IngestionResult
from pystreammcp.retrieval.errors import RetrievalError
from pystreammcp.retrieval.models import RetrievalResponse

class FakeService:
    def __init__(self): self.search_calls=[]; self.ingest_calls=[]; self.closed=0
    def search(self, request):
        self.search_calls.append(request)
        return RetrievalResponse(status="success", query=request.query,
                                 backend_requested=request.backend.value,
                                 groups=[], diagnostics={})
    def capabilities(self, include_health=True): return {"backends": []}
    def health(self): return {"backends": []}
    def ingest(self, path, force_multimodal=False):
        self.ingest_calls.append((path, force_multimodal))
        return IngestionResult(document_id="d1", display_path="docs/a.md",
                               status="processed", skipped=False, elapsed_ms=1,
                               content_types=("text",))
    def close(self): self.closed += 1

def test_tools_advertised_and_search_roundtrip():
    s = FakeService(); server = PyStreamMCPServer(retrieval_service=s)
    names = {t["name"] for t in server.get_tools()}
    assert {"pystreammcp_retrieval_search", "pystreammcp_retrieval_capabilities",
            "pystreammcp_rag_ingest"} <= names
    out = server.call_tool("pystreammcp_retrieval_search", {"query": "alpha"})
    assert out["status"] == "success" and out["groups"] == []
    assert s.search_calls[0].limit == 5
    assert s.search_calls[0].max_content_chars == 2000

def test_error_shape_and_auth(monkeypatch):
    class Failing(FakeService):
        def search(self, request): raise RetrievalError("unsupported_mode", "no", backend="qmd")
    server = PyStreamMCPServer(retrieval_service=Failing())
    out = server.call_tool("pystreammcp_retrieval_search", {"query": "x", "mode": "global"})
    assert out == {"status": "error", "error_type": "RetrievalError",
                   "code": "unsupported_mode", "message": "no",
                   "backend": "qmd", "retryable": False}
    monkeypatch.setenv("PYSTREAMMCP_API_KEY", "secret")
    assert server.call_tool("pystreammcp_retrieval_search", {"query": "x"})["error_type"] == "AuthenticationError"

def test_ingest_and_capabilities_and_close():
    s = FakeService(); server = PyStreamMCPServer(retrieval_service=s)
    out = server.call_tool("pystreammcp_rag_ingest", {"path": "docs/a.md", "force_multimodal": True})
    assert out["status"] == "processed"
    assert s.ingest_calls == [("docs/a.md", True)]
    assert json.dumps(server.call_tool("pystreammcp_retrieval_capabilities", {}))
    server.close(); server.close(); assert s.closed == 1
```

Also assert validation bounds: query `""` -> existing `validation_errors`; limit `0`/`51` -> validation error; `time_budget_ms=0` -> validation error; collections 33 -> validation error.

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_retrieval_mcp.py -v`

Expected: FAIL because tools are missing.

- [ ] **Step 3: Implement MCP wiring**

- Add `retrieval_service: Optional[Any] = None` to `__init__`; store, created flag, closed flag.
- `RetrievalSearchToolArgs`: query `min_length=1,max_length=8000`; backend `Literal["auto","qmd","rag_anything","all"]="auto"`; `mode: Optional[str]=Field(None,max_length=32)`; `collections: List[str]=Field(default_factory=list,max_length=32)`; `content_type: Optional[Literal["text","image","table","equation","document","pdf","audio","video"]]=None`; `limit=Field(5,ge=1,le=50)`; `include_content=False`; `max_content_chars=Field(2000,ge=0,le=20000)`; `time_budget_ms=Field(30000,ge=1,le=300000)`; `intent: Optional[str]=Field(None,max_length=1000)`.
- `RetrievalCapabilitiesToolArgs`: `include_health: bool = True`.
- `RagIngestToolArgs`: `path: str = Field(...,min_length=1)`, `force_multimodal: bool = False`.
- Add all three to `_TOOL_ARG_MODELS`, `_define_tools`, dispatch, handlers.
- Handlers return `.to_dict()` / capabilities dict / ingestion `.to_dict()`. Catch `RetrievalError` and return exactly `{"status":"error","error_type":"RetrievalError","code",...,"message",...,"backend",...,"retryable",...}`. Let unexpected exceptions hit the existing outer catch.
- `_get_retrieval_service()` lazily imports and caches `RetrievalService.from_env()`.
- `get_info` adds `"retrieval"` only when an injected service exists or a retrieval env flag is truthy; no lazy construction.
- `close()` closes service once. Preserve auth, validation, existing tools, message types.

- [ ] **Step 4: Run new and existing MCP tests**

Run: `.venv/bin/python -m pytest tests/test_retrieval_mcp.py tests/test_mcp_server_resilience.py tests/test_mcp_tools_handler.py tests/test_mcp_server_structured_errors.py -v`

Expected: PASS.

- [ ] **Step 5: Checkpoint**

Run: `git status --short`. Do not commit.

---

### Task 10: CLI Commands

**Files:**
- Create: `python/pystreammcp/retrieval/cli.py`
- Modify: `python/pystreammcp/cli.py`
- Test: `tests/test_retrieval_cli.py`

**Interfaces:**
- Produces `retrieval` Click group with `search`, `capabilities`, `health`, `ingest`, `deps status`
- Mounts on `pystreammcp.cli.cli`
- `deps status` uses `deps.dependency_status`/`upstream_exit_code`; no service construction

- [ ] **Step 1: Write failing CLI tests**

```python
import json
from click.testing import CliRunner
from pystreammcp.cli import cli
from pystreammcp.retrieval.base import IngestionResult
from pystreammcp.retrieval.errors import RetrievalError
from pystreammcp.retrieval.models import BackendGroup, RetrievalResponse

class FakeService:
    def __init__(self): self.search_calls=[]; self.ingest_calls=[]
    def search(self, request):
        self.search_calls.append(request)
        return RetrievalResponse(status="success", query=request.query,
                                 backend_requested=request.backend.value,
                                 groups=[BackendGroup(backend="qmd", status="ok",
                                                      hits=[], error=None, elapsed_ms=1,
                                                      truncated=False)],
                                 diagnostics={})
    def capabilities(self, include_health=True): return {"backends": []}
    def health(self): return {"backends": []}
    def ingest(self, path, force_multimodal=False):
        self.ingest_calls.append((path, force_multimodal))
        return IngestionResult(document_id="d1", display_path="docs/a.md",
                               status="processed", skipped=False, elapsed_ms=1,
                               content_types=("text",))
    def close(self): pass

def test_group_mounted_and_search_json(monkeypatch):
    fake = FakeService()
    monkeypatch.setattr("pystreammcp.retrieval.cli._build_service", lambda: fake)
    assert "retrieval" in CliRunner().invoke(cli, ["--help"]).output
    out = CliRunner().invoke(cli, ["retrieval", "search", "alpha", "--json", "--limit", "3"])
    assert out.exit_code == 0
    assert json.loads(out.output)["status"] == "success"
    assert fake.search_calls[0].limit == 3

def test_human_partial_and_error(monkeypatch):
    class Partial(FakeService):
        def search(self, request):
            return RetrievalResponse(status="partial", query=request.query,
                                     backend_requested=request.backend.value,
                                     groups=[], diagnostics={})
    monkeypatch.setattr("pystreammcp.retrieval.cli._build_service", Partial)
    assert CliRunner().invoke(cli, ["retrieval", "search", "x"]).exit_code == 1
    class Failing(FakeService):
        def search(self, request): raise RetrievalError("unsupported_mode", "no", backend="qmd")
    monkeypatch.setattr("pystreammcp.retrieval.cli._build_service", Failing)
    out = CliRunner().invoke(cli, ["retrieval", "search", "x"])
    assert out.exit_code == 1 and "unsupported_mode" in out.output

def test_capabilities_health_ingest(monkeypatch):
    fake = FakeService()
    monkeypatch.setattr("pystreammcp.retrieval.cli._build_service", lambda: fake)
    assert json.loads(CliRunner().invoke(cli, ["retrieval", "capabilities", "--json"]).output) == {"backends": []}
    assert json.loads(CliRunner().invoke(cli, ["retrieval", "health", "--json"]).output) == {"backends": []}
    out = CliRunner().invoke(cli, ["retrieval", "ingest", "docs/a.md", "--force-multimodal", "--json"])
    assert json.loads(out.output)["status"] == "processed"
    assert fake.ingest_calls == [("docs/a.md", True)]

def test_deps_status_exit_codes(monkeypatch):
    from pystreammcp.retrieval import cli as retrieval_cli
    def status(offline=False):
        return {"schema": 1, "offline": offline, "dependencies": [
            {"name": "qmd", "pinned": "v2.8.3", "latest": "v2.8.3",
             "state": "current", "vendored": "verified", "error": None},
        ]}
    monkeypatch.setattr(retrieval_cli.deps, "dependency_status", status)
    monkeypatch.setattr(retrieval_cli.deps, "upstream_exit_code", lambda data: 0)
    out = CliRunner().invoke(cli, ["retrieval", "deps", "status", "--offline", "--json"])
    assert out.exit_code == 0
    assert json.loads(out.output)["offline"] is True
    monkeypatch.setattr(retrieval_cli.deps, "upstream_exit_code", lambda data: 1)
    assert CliRunner().invoke(cli, ["retrieval", "deps", "status", "--offline"]).exit_code == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_retrieval_cli.py -v`

Expected: FAIL because the group is missing.

- [ ] **Step 3: Implement CLI**

`retrieval/cli.py`: `_build_service()` -> `RetrievalService.from_env()`. Import `deps` as a module (`from pystreammcp.retrieval import deps`) so tests can replace its status functions. Commands exactly:

```text
search QUERY [--backend auto|qmd|rag_anything|all] [--mode TEXT]
  [--collection NAME ...] [--content-type TEXT] [--limit N]
  [--include-content] [--max-content-chars N] [--time-budget-ms N]
  [--intent TEXT] [--json]
capabilities [--no-health] [--json]
health [--json]
ingest PATH [--force-multimodal] [--json]
deps status [--offline] [--json]
```

Always close the service in `finally`. JSON prints one object. Human mode prints per-backend status, hits, and `N hit(s)`. Exit 1 for `partial`/`error` and `RetrievalError`; print `code: message` to stderr. No secret/provider/root flags.

`deps status` does not build a `RetrievalService`. It calls `deps.dependency_status(offline=offline)`, prints the read-only JSON or one line per component, and exits with `upstream_exit_code`. `--offline` skips GitHub entirely and still verifies vendor checksums. It never downloads, updates, installs, or mutates the lock. Do not add an update subcommand.

Mount in top-level `cli.py` after group definition:

```python
from pystreammcp.retrieval.cli import retrieval
cli.add_command(retrieval)
```

Do not import RAG-Anything.

- [ ] **Step 4: Run new and existing CLI tests**

Run: `.venv/bin/python -m pytest tests/test_retrieval_cli.py tests/test_cli.py -v`

Expected: PASS.

- [ ] **Step 5: Checkpoint**

Run: `git status --short`. Do not commit.

---

### Task 11: Public Exports and Optional Packaging

**Files:**
- Modify: `python/pystreammcp/retrieval/__init__.py`
- Modify: `python/pystreammcp/__init__.py`
- Modify: `pyproject.toml`
- Modify: `MANIFEST.in`
- Test: `tests/test_retrieval_packaging.py`

**Interfaces:**
- Produces top-level exports: `RetrievalService`, `RetrievalRequest`, `RetrievalResponse`, `RetrievalError`, `BackendName`, `RequestedBackend`
- Produces optional extra `rag-anything`

- [ ] **Step 1: Write failing packaging tests**

```python
import sys
from pathlib import Path

def test_public_exports():
    from pystreammcp import (BackendName, RequestedBackend, RetrievalError,
                             RetrievalRequest, RetrievalResponse, RetrievalService)
    assert BackendName.QMD.value == "qmd"
    assert RequestedBackend.AUTO.value == "auto"
    assert RetrievalRequest(query="x").limit == 5
    assert RetrievalService and RetrievalResponse and RetrievalError

def test_core_import_does_not_load_heavy_deps():
    import pystreammcp  # noqa: F401
    assert "raganything" not in sys.modules
    assert "lightrag" not in sys.modules
    assert "openai" not in sys.modules

def test_extra_is_declared_and_python_gated():
    text = Path("pyproject.toml").read_text(encoding="utf-8")
    assert "rag-anything" in text and "raganything" in text
    assert "lightrag-hku==1.4.16" in text
    assert "python_version >= '3.10'" in text or 'python_version >= "3.10"' in text

def test_vendor_is_source_only():
    from setuptools import find_packages
    assert (Path("vendor") / "deps.lock.json").is_file()
    assert all(not p.startswith("vendor") for p in find_packages(where="python"))
    assert "prune vendor" in Path("MANIFEST.in").read_text(encoding="utf-8")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_retrieval_packaging.py -v`

Expected: FAIL for missing exports.

- [ ] **Step 3: Implement exports and extra**

`retrieval/__init__.py` exports models, errors, base types, `RetrievalService`, `RetrievalConfig`, `QmdBackend`, `RAGAnythingBackend`; no RAG/OpenAI imports.

Top-level `pystreammcp/__init__.py` adds imports and `__all__` entries without removing existing fallbacks.

Add:

```toml
rag-anything = [
  "raganything>=1.4.3,<1.5; python_version >= '3.10'",
  "lightrag-hku==1.4.16; python_version >= '3.10'",
  "openai>=2.0.0,<4.0.0; python_version >= '3.10'",
]
```

Add `prune vendor` to `MANIFEST.in`; do not add `vendor` to package discovery or package data. The exact `lightrag-hku` pin keeps the installed pair aligned with the vendored LightRAG snapshot.

Do not add to `all-integrations`; do not bump `__version__` or `requires-python`.

- [ ] **Step 4: Run tests and import check**

Run: `.venv/bin/python -m pytest tests/test_retrieval_packaging.py -v`

Run: `.venv/bin/python -c "import pystreammcp, sys; print('raganything' in sys.modules, 'lightrag' in sys.modules, 'openai' in sys.modules)"`

Expected: PASS; `False False False`.

- [ ] **Step 5: Checkpoint**

Run: `git status --short`. Do not commit.

---

### Task 12: Documentation

**Files:**
- Create: `docs/retrieval.md`
- Modify: `README.md`
- Modify: `docs/ARCHITECTURE.md`
- Modify: `SECURITY.md`
- Modify: `docs/internal/ROADMAP_HONEST.md`
- Modify: `docs/README.md`

- [ ] **Step 1: Write `docs/retrieval.md`**

Include, matching code exactly:

- New `vendor/README.md` is created in Task 0 and must be linked from `docs/retrieval.md`.
- Optional adapters and install: core; `pip install 'pystreammcp[rag-anything]'` for Python 3.10+; QMD npm/Node prerequisite `@tobilu/qmd` and `qmd mcp --http` (not bundled).
- Vendored sources: exact QMD/RAG-Anything/LightRAG pins, `PYSTREAMMCP_RAG_SOURCE=auto|installed|vendored`, installed-first/consistent-pair rules, offline checksum verification, `deps status` exit codes, no runtime updates/downloads, transitive-dependency limits, and QMD's emergency-rebuild-only caveat.
- Library API: `RetrievalService.from_env`, injected service/backends, `RetrievalRequest`, grouped `RetrievalResponse`, no fusion.
- MCP tools and CLI commands, including `--force-multimodal` and `deps status`.
- Full env var table, including QMD allowlist, loopback/remote opt-in, RAG roots `os.pathsep`, parser/query mode, provider config, and `RAG_SOURCE`.
- Security/privacy: no auto-install, no model download, remote model egress disclosure, no secrets in logs, no deletion, no HTML, Markdown local-image guard, path/symlink/size checks.
- Routing: explicit, all, auto; collections require QMD; non-text pref RAG; no silent fallback.
- Score semantics: QMD relevance scores not comparable to RAG order-only.
- Limitations: best-effort RAG page data, cold starts, no live verification in this environment, default tests offline.
- Benchmark commands.

- [ ] **Step 2: Update README, architecture, security, roadmap**

README: feature bullet, install, short QMD/RAG examples, link to `docs/retrieval.md`, and no-silent-fallback/no-fusion/no-deletion/no-runtime-dependency-update note.

ARCHITECTURE: add retrieval flow MCP/CLI → service → router → QMD/RAG → groups.

SECURITY: add QMD loopback/remote, collection allowlist, RAG roots/symlink/HTML/Markdown, egress, no deletion, vendored pin/checksum rules, no runtime updates, and `GITHUB_TOKEN` redaction.

ROADMAP: record implemented adapters, optional extra, vendored pins, offline test coverage, and that live QMD/RAG was not run unless opted in.

docs/README: link `retrieval.md`.

- [ ] **Step 3: Verify exact names and no stale claims**

Run:

```bash
grep -n "pystreammcp_retrieval_search\|pystreammcp_retrieval_capabilities\|pystreammcp_rag_ingest" README.md docs/retrieval.md
grep -n "PYSTREAMMCP_RAG_ALLOWED_ROOTS\|PYSTREAMMCP_QMD_ALLOW_REMOTE\|rag-anything" docs/retrieval.md README.md SECURITY.md
grep -niE "guaranteed|production-ready|fully tested|live-tested" docs/retrieval.md README.md SECURITY.md
```

Expected: public names/env vars present; no unsupported live-tested claim.

- [ ] **Step 4: Checkpoint**

Run: `git status --short`. Do not commit.

---

### Task 13: Offline Benchmark Harness

**Files:**
- Create: `benchmarks/retrieval_bench.py`
- Create: `benchmarks/README.md`
- Test: `tests/test_retrieval_benchmark.py`

- [ ] **Step 1: Write failing benchmark test**

```python
import json, subprocess, sys

def run(*args):
    return subprocess.run([sys.executable, "benchmarks/retrieval_bench.py", *args],
                          capture_output=True, text=True, timeout=30)

def test_fake_benchmark_offline():
    r = run("--queries", "2", "--json")
    assert r.returncode == 0, r.stderr
    data = json.loads(r.stdout)
    assert data["mode"] == "fake"
    assert data["sample_count"] == 2
    assert data["error_count"] == 0
    assert data["p50_ms"] >= 0 and data["p95_ms"] >= data["p50_ms"]

def test_rejects_negative_queries():
    assert run("--queries", "-1", "--json").returncode != 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_retrieval_benchmark.py -v`

Expected: FAIL because script is missing.

- [ ] **Step 3: Implement benchmark**

`argparse`: `--queries` positive default 10; `--query` repeatable; `--json`; `--warmup` default 1; `--qmd-url` optional; `--rag` flag. Default fake in-script backend measures router/service/serialization only. QMD mode builds `QmdConfig` from `--qmd-url` plus `PYSTREAMMCP_QMD_COLLECTIONS`; RAG mode uses `RetrievalService.from_env()` and does not ingest. Metrics: `mode`, `sample_count`, `hit_count`, `empty_count`, `error_count`, `timeout_count`, `p50_ms`, `p95_ms`, `p99_ms`, `mean_ms`, `throughput_qps`. Never combine QMD/RAG quality. No secrets/content printed. `benchmarks/README.md` documents corpus setup, commands, cold vs warm, and that quality metrics are future work with no fabricated baselines.

- [ ] **Step 4: Run tests and manual fake run**

Run: `.venv/bin/python -m pytest tests/test_retrieval_benchmark.py -v`

Run: `.venv/bin/python benchmarks/retrieval_bench.py --queries 20 --json`

Expected: PASS; JSON object.

- [ ] **Step 5: Checkpoint**

Run: `git status --short`. Do not commit.

---

### Task 14: Opt-In Live Tests, Compile Check, and Full Verification

**Files:**
- Create: `tests/test_retrieval_live.py`

- [ ] **Step 1: Add skipped-by-default live tests**

```python
import os, pytest

pytestmark = pytest.mark.skipif(
    not os.getenv("PYSTREAMMCP_TEST_QMD_URL") and os.getenv("PYSTREAMMCP_TEST_RAG") != "1",
    reason="set PYSTREAMMCP_TEST_QMD_URL or PYSTREAMMCP_TEST_RAG=1",
)

@pytest.mark.skipif(not os.getenv("PYSTREAMMCP_TEST_QMD_URL"), reason="no live QMD")
def test_live_qmd_health_and_query():
    from pystreammcp.retrieval.config import QmdConfig
    from pystreammcp.retrieval.qmd import QmdBackend
    from pystreammcp.retrieval.base import BackendSearchRequest
    b = QmdBackend(QmdConfig(enabled=True, url=os.environ["PYSTREAMMCP_TEST_QMD_URL"],
                             collections=(os.environ["PYSTREAMMCP_TEST_QMD_COLLECTION"],)))
    try:
        assert b.health().status == "ok"
        b.search(BackendSearchRequest(query="test", mode=None, collections=(),
                 content_type=None, limit=1, include_content=False,
                 max_content_chars=100, timeout_s=10.0, intent=None))
    finally:
        b.close()

@pytest.mark.skipif(os.getenv("PYSTREAMMCP_TEST_RAG") != "1", reason="no live RAG")
def test_live_rag_ingest_and_query():
    from pystreammcp.retrieval.models import RequestedBackend, RetrievalRequest
    from pystreammcp.retrieval.service import RetrievalService
    doc = os.environ["PYSTREAMMCP_TEST_RAG_DOC"]
    service = RetrievalService.from_env()
    try:
        result = service.ingest(doc)
        assert result.status in {"processed", "skipped"}
        service.search(RetrievalRequest(query="test", backend=RequestedBackend.RAG_ANYTHING))
    finally:
        service.close()
```

The RAG live test requires `PYSTREAMMCP_TEST_RAG_DOC`, normal RAG roots, and a real provider/engine; it may download models. Document that.

- [ ] **Step 2: Verify skip behavior**

Run: `.venv/bin/python -m pytest tests/test_retrieval_live.py -v`

Expected: skipped.

- [ ] **Step 3: Compile-check new modules**

Run: `.venv/bin/python -m compileall -q python/pystreammcp/retrieval scripts/vendor_dependencies.py benchmarks/retrieval_bench.py`

Expected: exit 0.

- [ ] **Step 4: Run full suite**

Run: `.venv/bin/python -m pytest tests/ -q`

Expected: all existing tests still pass; baseline was `421 passed, 13 skipped`. New offline tests add to the count; live tests remain skipped unless opted in.

- [ ] **Step 5: Verify vendored dependencies and offline status**

Run:

```bash
.venv/bin/python scripts/vendor_dependencies.py verify
.venv/bin/pystreammcp retrieval deps status --offline --json
```

Expected: exit 0; all three snapshots verified; no network.

- [ ] **Step 6: Lint changed files**

Run:

```bash
.venv/bin/ruff check python/pystreammcp/retrieval \
  python/pystreammcp/mcp_server.py python/pystreammcp/cli.py \
  python/pystreammcp/__init__.py tests/test_retrieval_*.py \
  tests/test_vendor_dependencies.py tests/test_retrieval_mcp.py \
  tests/test_retrieval_cli.py scripts/vendor_dependencies.py \
  benchmarks/retrieval_bench.py
```

Expected: no new findings. Do not fix the repo-wide pre-existing ruff backlog.

- [ ] **Step 7: Final checks**

Run:

```bash
git diff --check
git status --short
grep -rniE "sk-[a-z0-9]{8,}|api[_-]?key\s*=\s*['\"][^'\"]+" python/pystreammcp/retrieval tests/test_retrieval_*.py scripts/vendor_dependencies.py benchmarks/retrieval_bench.py || true
```

Expected: no whitespace errors, no secrets, only intended files. Do not commit unless explicitly asked. Report exact test counts, lint result, vendor verification, and that live QMD/RAG was not run unless the user supplied the opt-in environment.

---

## Self-Review

- **Spec coverage:** vendor pins/checksums/update checks (§4.4, §6.13), models/errors (§6.2–6.3), protocols (§6.5), router (§6.6), service (§6.7), QMD (§6.8), RAG query/ingestion (§6.9), provider, MCP (§6.10), CLI (§6.11), security (§7), packaging (§8), docs (§9), benchmarks (§10), tests (§11) each have an owning task.
- **Dependency order:** Task 0 pins and vendors the upstream sources before any adapter implementation; Task 2b resolves them; Tasks 6, 8, 10 consume the resolution/status APIs.
- **Type consistency:** `BackendName`, `RequestedBackend`, `RetrievalRequest`, `RetrievalHit`, `BackendGroup`, `RetrievalResponse`, `BackendSearchRequest`, `BackendCapabilities`, `BackendHealth`, and `IngestionResult` match the spec fields. `ingest` consistently uses `force_multimodal`.
- **Status values:** response `success|partial|error`; group `ok|error|timeout|unavailable`; health `ok|unavailable|error`; egress `local|remote|unknown`; dependency status `current|update_available|pinned|check_failed|corrupt|missing`.
- **No update path:** only `scripts/vendor_dependencies.py` mutates `vendor/`; `deps status` is read-only; queries never check GitHub.
- **No commit steps:** user has not authorized commits; checkpoints only.
