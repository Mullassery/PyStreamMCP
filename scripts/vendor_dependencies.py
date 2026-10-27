#!/usr/bin/env python3
"""Maintainer-only vendor/update/verify tool for pinned source snapshots."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "vendor"
LOCK_PATH = VENDOR / "deps.lock.json"
COMPONENTS = ("qmd", "rag-anything", "lightrag")
EXCLUDED_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "node_modules",
    "dist",
    "build",
}


class VendorError(Exception):
    pass


def load_lock() -> dict[str, Any]:
    try:
        data = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise VendorError(f"missing lock: {LOCK_PATH}") from exc
    except json.JSONDecodeError as exc:
        raise VendorError(f"invalid lock JSON: {exc}") from exc

    if data.get("schema") != 1:
        raise VendorError("unsupported lock schema")
    dependencies = data.get("dependencies")
    if not isinstance(dependencies, dict):
        raise VendorError("lock dependencies must be an object")
    unknown = sorted(set(dependencies) - set(COMPONENTS))
    missing = sorted(set(COMPONENTS) - set(dependencies))
    if unknown or missing:
        raise VendorError(f"lock components mismatch: unknown={unknown} missing={missing}")
    for name, dep in dependencies.items():
        if not isinstance(dep, dict):
            raise VendorError(f"{name}: dependency entry must be an object")
        for key in ("repo", "tag", "commit", "path", "ecosystem", "license", "tree_sha256"):
            if key not in dep:
                raise VendorError(f"{name}: missing {key}")
        path = Path(dep["path"])
        if path.is_absolute() or ".." in path.parts or path.parts != ("vendor", name):
            raise VendorError(f"{name}: invalid repository-relative path {dep['path']!r}")
        if not isinstance(dep["tree_sha256"], str):
            raise VendorError(f"{name}: tree_sha256 must be a string")
        if dep["tree_sha256"] and len(dep["tree_sha256"]) != 64:
            raise VendorError(f"{name}: tree_sha256 must be empty or 64 characters")
    return data


def _write_lock(lock: dict[str, Any]) -> None:
    payload = json.dumps(lock, indent=2, ensure_ascii=False) + "\n"
    fd, temp_name = tempfile.mkstemp(prefix=".deps.lock.", dir=VENDOR)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
        os.replace(temp_name, LOCK_PATH)
    except BaseException:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def _iter_files(root: Path) -> list[Path]:
    if not root.is_dir():
        raise VendorError(f"missing vendor directory: {root}")
    if root.is_symlink():
        raise VendorError(f"symlink vendor root: {root}")
    files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_symlink():
            raise VendorError(f"symlink in vendor tree: {path.relative_to(root)}")
        if any(part in EXCLUDED_DIRS for part in path.relative_to(root).parts):
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
    canonical = json.dumps(entries, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _component_hash(lock: dict[str, Any], name: str) -> str:
    dep = lock["dependencies"][name]
    return compute_tree_sha256(ROOT / dep["path"])


def _verify_component(lock: dict[str, Any], name: str) -> str:
    dep = lock["dependencies"][name]
    expected = dep["tree_sha256"]
    if not expected:
        raise VendorError(f"{name}: empty tree_sha256")
    actual = _component_hash(lock, name)
    if actual != expected:
        raise VendorError(f"{name}: checksum mismatch (expected {expected}, got {actual})")
    return actual


def verify(lock: dict[str, Any]) -> None:
    failures: list[str] = []
    for name in COMPONENTS:
        try:
            digest = _verify_component(lock, name)
        except VendorError as exc:
            failures.append(str(exc))
            print(f"{name}: FAILED ({exc})")
        else:
            print(f"{name}: ok ({digest})")
    if failures:
        raise VendorError(f"{len(failures)} component(s) failed verification")


def _run_git(args: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise VendorError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def _clone(repo: str, tag: str, commit: str, temp_root: Path) -> Path:
    checkout = temp_root / "checkout"
    _run_git(["clone", "--quiet", "--depth", "1", "--branch", tag, repo, str(checkout)])
    head = _run_git(["rev-parse", "HEAD"], cwd=checkout)
    if head != commit:
        raise VendorError(f"resolved commit {head} does not match lock commit {commit}")
    return checkout


def _export(checkout: Path, target: Path) -> None:
    archive = target.parent / "source.tar"
    _run_git(["archive", "--format=tar", "--output", str(archive), "HEAD"], cwd=checkout)
    with tarfile.open(archive) as tar:
        for member in tar.getmembers():
            member_path = Path(member.name)
            if member_path.is_absolute() or ".." in member_path.parts:
                raise VendorError(f"unsafe archive member: {member.name}")
            if member.issym() or member.islnk():
                raise VendorError(f"symlink in archive: {member.name}")
            if member.isdir():
                (target / member_path).mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                destination = target / member_path
                destination.parent.mkdir(parents=True, exist_ok=True)
                source = tar.extractfile(member)
                if source is None:
                    raise VendorError(f"unreadable archive member: {member.name}")
                destination.write_bytes(source.read())


def _install_component(name: str, tag: str, commit: str, repo: str) -> str:
    target = VENDOR / name
    with tempfile.TemporaryDirectory(prefix=f".{name}.", dir=ROOT) as temp:
        temp_root = Path(temp)
        checkout = _clone(repo, tag, commit, temp_root)
        staged = temp_root / "staged"
        _export(checkout, staged)
        if not (staged / "LICENSE").is_file():
            raise VendorError(f"{name}: exported tree has no LICENSE")
        digest = compute_tree_sha256(staged)
        backup = temp_root / "backup"
        if target.exists():
            shutil.move(str(target), str(backup))
        try:
            shutil.move(str(staged), str(target))
        except BaseException:
            if backup.exists() and not target.exists():
                shutil.move(str(backup), str(target))
            raise
        return digest


def vendor(lock: dict[str, Any], selected: list[str]) -> None:
    pending: dict[str, tuple[str, str, str]] = {}
    for name in selected:
        dep = lock["dependencies"][name]
        digest = _install_component(name, dep["tag"], dep["commit"], dep["repo"])
        pending[name] = (dep["tag"], dep["commit"], digest)
        print(f"{name}: vendored ({digest})")
    for name, (tag, commit, digest) in pending.items():
        dep = lock["dependencies"][name]
        dep["tag"] = tag
        dep["commit"] = commit
        dep["tree_sha256"] = digest
    _write_lock(lock)


def _resolve_tag(repo: str, tag: str) -> str:
    refs = _run_git(["ls-remote", "--tags", repo, f"refs/tags/{tag}", f"refs/tags/{tag}^{{}}"])
    peeled = None
    direct = None
    for line in refs.splitlines():
        commit, ref = line.split("\t", 1)
        if ref == f"refs/tags/{tag}^{{}}":
            peeled = commit
        elif ref == f"refs/tags/{tag}":
            direct = commit
    commit = peeled or direct
    if not commit:
        raise VendorError(f"tag not found: {tag}")
    return commit


def update(lock: dict[str, Any], name: str, tag: str) -> None:
    dep = lock["dependencies"][name]
    commit = _resolve_tag(dep["repo"], tag)
    digest = _install_component(name, tag, commit, dep["repo"])
    dep["tag"] = tag
    dep["commit"] = commit
    dep["tree_sha256"] = digest
    _write_lock(lock)


def _selected(component: str) -> list[str]:
    return list(COMPONENTS) if component == "all" else [component]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("verify", help="verify vendored tree checksums offline")

    vendor_parser = subparsers.add_parser("vendor", help="populate vendored snapshots")
    vendor_parser.add_argument("--component", choices=(*COMPONENTS, "all"), required=True)

    update_parser = subparsers.add_parser("update", help="vendor a new upstream tag")
    update_parser.add_argument("--component", choices=COMPONENTS, required=True)
    update_parser.add_argument("--tag", required=True)

    args = parser.parse_args()
    try:
        lock = load_lock()
        if args.command == "verify":
            verify(lock)
        elif args.command == "vendor":
            vendor(lock, _selected(args.component))
        else:
            update(lock, args.component, args.tag)
    except VendorError as exc:
        print(f"error: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
