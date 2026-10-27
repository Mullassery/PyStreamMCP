from __future__ import annotations

import hashlib
import importlib.metadata
import importlib.util
import json
import os
import re
import sys
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Optional
from urllib.parse import urlsplit

import httpx

from .errors import RetrievalError
from .security import redact_text

COMPONENTS = ("qmd", "rag-anything", "lightrag")
_EXCLUDED_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "node_modules",
    "dist",
    "build",
}
_STABLE_TAG = re.compile(r"v?(\d+)\.(\d+)\.(\d+)")
_PATH_LOCK = threading.Lock()
_VERIFIED_TREES: set[tuple[Path, str]] = set()


@dataclass(frozen=True)
class RagSource:
    mode: str
    source: str
    rag_path: Optional[Path]
    lightrag_path: Optional[Path]
    version: Optional[str]


def vendor_root() -> Path:
    return (Path(__file__).resolve().parents[3] / "vendor").resolve()


def load_vendor_lock() -> dict[str, Any]:
    lock_path = vendor_root() / "deps.lock.json"
    try:
        data = json.loads(lock_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RetrievalError(
            "missing_dependency", f"Missing vendor lock: {lock_path}"
        ) from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise RetrievalError(
            "missing_dependency", "Invalid vendor lock JSON"
        ) from exc

    if not isinstance(data, dict) or data.get("schema") != 1:
        raise RetrievalError("missing_dependency", "Unsupported vendor lock schema")
    dependencies = data.get("dependencies")
    if not isinstance(dependencies, dict):
        raise RetrievalError(
            "missing_dependency", "Vendor lock dependencies must be an object"
        )
    if set(dependencies) != set(COMPONENTS):
        raise RetrievalError(
            "missing_dependency", "Vendor lock component list is invalid"
        )

    for name in COMPONENTS:
        dependency = dependencies[name]
        if not isinstance(dependency, dict):
            raise RetrievalError(
                "missing_dependency", f"Invalid vendor lock entry: {name}"
            )
        for key in (
            "repo",
            "tag",
            "commit",
            "path",
            "ecosystem",
            "license",
            "tree_sha256",
        ):
            if key not in dependency:
                raise RetrievalError(
                    "missing_dependency", f"Vendor lock entry {name} is missing {key}"
                )
        path = Path(dependency["path"])
        if path.is_absolute() or ".." in path.parts or path.parts != ("vendor", name):
            raise RetrievalError(
                "missing_dependency", f"Invalid vendor lock path for {name}"
            )
        digest = dependency["tree_sha256"]
        if not isinstance(digest, str) or len(digest) != 64:
            raise RetrievalError(
                "missing_dependency", f"Invalid tree hash for {name}"
            )
        try:
            int(digest, 16)
        except ValueError as exc:
            raise RetrievalError(
                "missing_dependency", f"Invalid tree hash for {name}"
            ) from exc
    return data


def _iter_files(root: Path) -> list[Path]:
    if root.is_symlink():
        raise RetrievalError(
            "configuration_error", f"Symlinked vendor tree: {root.name}"
        )
    if not root.is_dir():
        raise RetrievalError(
            "missing_dependency", f"Missing vendor tree: {root.name}"
        )
    files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_symlink():
            raise RetrievalError(
                "configuration_error",
                f"Symlink in vendor tree: {path.relative_to(root)}",
            )
        relative = path.relative_to(root)
        if any(part in _EXCLUDED_DIRS for part in relative.parts):
            continue
        if path.suffix == ".pyc":
            continue
        if path.is_file():
            files.append(path)
    return sorted(files, key=lambda path: path.relative_to(root).as_posix())


def compute_tree_sha256(path: Path) -> str:
    entries: list[list[str]] = []
    for file_path in _iter_files(path):
        digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
        entries.append([file_path.relative_to(path).as_posix(), digest])
    canonical = json.dumps(
        entries, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def verify_vendored_tree(name: str) -> str:
    if name not in COMPONENTS:
        raise RetrievalError(
            "configuration_error", f"Unknown vendored component: {name}"
        )
    lock = load_vendor_lock()
    expected = lock["dependencies"][name]["tree_sha256"]
    root = vendor_root() / name
    cache_key = (root.resolve(), expected)
    if cache_key in _VERIFIED_TREES:
        return expected
    actual = compute_tree_sha256(root)
    if actual != expected:
        raise RetrievalError(
            "configuration_error", f"{name}: vendored tree checksum mismatch"
        )
    _VERIFIED_TREES.add(cache_key)
    return actual


def _installed_pair() -> bool:
    return (
        importlib.util.find_spec("raganything") is not None
        and importlib.util.find_spec("lightrag") is not None
    )


def _installed_version() -> Optional[str]:
    try:
        return importlib.metadata.version("raganything")
    except importlib.metadata.PackageNotFoundError:
        return None
    except Exception:
        return None


def _vendored_source(mode: str) -> RagSource:
    rag_path = vendor_root() / "rag-anything"
    lightrag_path = vendor_root() / "lightrag"
    if not rag_path.is_dir() or not lightrag_path.is_dir():
        raise RetrievalError(
            "missing_dependency", "Both vendored RAG snapshots are required"
        )
    verify_vendored_tree("rag-anything")
    verify_vendored_tree("lightrag")
    lock = load_vendor_lock()
    return RagSource(
        mode=mode,
        source="vendored",
        rag_path=rag_path,
        lightrag_path=lightrag_path,
        version=lock["dependencies"]["rag-anything"]["tag"],
    )


def resolve_rag_source(mode: str, injected: bool = False) -> RagSource:
    if injected:
        return RagSource(mode, "injected", None, None, None)
    if mode not in {"auto", "installed", "vendored"}:
        raise RetrievalError(
            "configuration_error",
            "RAG source must be 'auto', 'installed', or 'vendored'",
        )

    if mode in {"auto", "installed"} and _installed_pair():
        return RagSource(
            mode=mode,
            source="installed",
            rag_path=None,
            lightrag_path=None,
            version=_installed_version(),
        )
    if mode == "installed":
        raise RetrievalError(
            "missing_dependency",
            "Both raganything and lightrag must be installed",
        )

    try:
        return _vendored_source(mode)
    except RetrievalError:
        if mode == "vendored":
            raise
    raise RetrievalError(
        "missing_dependency",
        "No consistent RAG dependency pair is available",
    )


def ensure_rag_import_path(mode: str) -> RagSource:
    source = resolve_rag_source(mode)
    if source.source != "vendored":
        return source
    with _PATH_LOCK:
        additions = [str(source.rag_path), str(source.lightrag_path)]
        for path in additions:
            if path not in sys.path:
                sys.path.insert(0, path)
    return source


def _component_entry(
    name: str,
    pinned: Optional[str],
    state: str,
    vendored: str,
    latest: Optional[str] = None,
    error: Optional[str] = None,
) -> dict[str, Any]:
    return {
        "name": name,
        "pinned": pinned,
        "latest": latest,
        "state": state,
        "vendored": vendored,
        "error": error,
    }


def _missing_status(error: str) -> dict[str, Any]:
    bounded = error[:500]
    return {
        "schema": 1,
        "dependencies": [
            _component_entry(name, None, "missing", "missing", error=bounded)
            for name in COMPONENTS
        ],
    }


def _tags_url(repo: str) -> str:
    parsed = urlsplit(repo)
    if parsed.netloc.lower() != "github.com":
        raise ValueError("Only GitHub repositories are supported")
    path = parsed.path.strip("/")
    if path.endswith(".git"):
        path = path[:-4]
    owner, project = path.split("/", 1)
    return f"https://api.github.com/repos/{owner}/{project}/tags?per_page=100"


def _stable_version(tag: Any) -> Optional[tuple[int, int, int]]:
    if not isinstance(tag, str):
        return None
    match = _STABLE_TAG.fullmatch(tag)
    if match is None:
        return None
    return tuple(int(part) for part in match.groups())


def _update_entry(
    name: str,
    pinned: Optional[str],
    latest: Optional[str],
    state: str,
    error: Optional[str] = None,
) -> dict[str, Any]:
    return _component_entry(name, pinned, state, "unknown", latest, error)


def check_upstream_updates(
    client: Optional[httpx.Client] = None,
    token: Optional[str] = None,
    components: Optional[Iterable[str]] = None,
) -> dict[str, Any]:
    requested = list(COMPONENTS if components is None else components)
    try:
        lock = load_vendor_lock()
    except RetrievalError as exc:
        entries = [
            _update_entry(name, None, None, "check_failed", exc.message)
            for name in requested
        ]
        return {"schema": 1, "dependencies": entries}

    secret = token or os.environ.get("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "pystreammcp"}
    if secret:
        headers["Authorization"] = f"Bearer {secret}"
    owns_client = client is None
    http_client = client or httpx.Client(timeout=10.0)
    entries: list[dict[str, Any]] = []
    try:
        for name in requested:
            dependency = lock["dependencies"].get(name)
            if dependency is None:
                entries.append(
                    _update_entry(
                        name, None, None, "check_failed", "Unknown component"
                    )
                )
                continue
            pinned = dependency.get("tag")
            try:
                response = http_client.get(
                    _tags_url(dependency["repo"]),
                    headers=headers,
                    timeout=10.0,
                )
                if response.status_code >= 400:
                    raise RetrievalError(
                        "http_error",
                        f"GitHub returned HTTP {response.status_code}",
                    )
                payload = response.json()
                if not isinstance(payload, list):
                    raise RetrievalError(
                        "invalid_response", "GitHub tags response is invalid"
                    )
                tags = [
                    item.get("name")
                    for item in payload
                    if isinstance(item, dict)
                ]
                stable = [
                    (version, tag)
                    for tag in tags
                    for version in [_stable_version(tag)]
                    if version is not None
                ]
                if not stable:
                    raise RetrievalError(
                        "invalid_response", "No stable tags found"
                    )
                latest_version, latest = max(stable, key=lambda item: item[0])
                pinned_version = _stable_version(pinned)
                state = (
                    "update_available"
                    if pinned_version is not None and latest_version > pinned_version
                    else "current"
                )
                entries.append(
                    _update_entry(name, pinned, latest, state)
                )
            except httpx.TimeoutException as exc:
                message = redact_text(f"timeout: {type(exc).__name__}", [secret or ""])
                entries.append(
                    _update_entry(name, pinned, None, "check_failed", message[:500])
                )
            except RetrievalError as exc:
                message = redact_text(exc.message, [secret or ""])[:500]
                entries.append(
                    _update_entry(name, pinned, None, "check_failed", message)
                )
            except (httpx.HTTPError, ValueError, TypeError, KeyError) as exc:
                message = redact_text(
                    f"{type(exc).__name__}: {exc}", [secret or ""]
                )[:500]
                entries.append(
                    _update_entry(name, pinned, None, "check_failed", message)
                )
    finally:
        if owns_client:
            http_client.close()
    return {"schema": 1, "dependencies": entries}


def dependency_status(
    offline: bool = False,
    client: Optional[httpx.Client] = None,
    token: Optional[str] = None,
) -> dict[str, Any]:
    try:
        lock = load_vendor_lock()
    except RetrievalError as exc:
        response = _missing_status(exc.message)
        response["offline"] = bool(offline)
        return response

    entries: list[dict[str, Any]] = []
    verified: list[str] = []
    for name in COMPONENTS:
        pinned = lock["dependencies"][name].get("tag")
        try:
            verify_vendored_tree(name)
        except RetrievalError as exc:
            state = (
                "missing"
                if exc.code == "missing_dependency"
                else "corrupt"
            )
            vendored = "missing" if state == "missing" else "corrupt"
            entries.append(
                _component_entry(
                    name,
                    pinned,
                    state,
                    vendored,
                    latest=None,
                    error=exc.message[:500],
                )
            )
        else:
            verified.append(name)
            entries.append(
                _component_entry(
                    name,
                    pinned,
                    "pinned" if offline else "current",
                    "verified",
                    latest=None,
                )
            )

    if not offline and verified:
        updates = check_upstream_updates(
            client=client, token=token, components=verified
        )
        by_name = {
            item["name"]: item for item in updates.get("dependencies", [])
        }
        for entry in entries:
            if entry["name"] not in verified:
                continue
            update = by_name.get(entry["name"])
            if update is None:
                entry["state"] = "check_failed"
                entry["error"] = "No update result"
                continue
            entry["latest"] = update.get("latest")
            entry["state"] = update.get("state", "check_failed")
            entry["error"] = update.get("error")

    return {"schema": 1, "offline": bool(offline), "dependencies": entries}


def upstream_exit_code(status: dict[str, Any]) -> int:
    states = {
        dependency.get("state")
        for dependency in status.get("dependencies", [])
        if isinstance(dependency, dict)
    }
    if states & {"corrupt", "missing", "check_failed"}:
        return 2
    if "update_available" in states:
        return 1
    return 0
