from __future__ import annotations

import ipaddress
import os
import re
from pathlib import Path
from typing import Iterable, Optional, Union
from urllib.parse import unquote, urlsplit

from .errors import RetrievalError

HTML_EXTENSIONS = {".html", ".htm", ".xhtml"}
_REMOTE_SCHEMES = {"http", "https", "ftp", "ftps", "data", "mailto", "cid"}
_MARKDOWN_IMAGE = re.compile(
    r"!\[[^\]]*\]\(\s*(?:<([^>]+)>|([^\s)]+))(?:\s+(?:\"[^\"]*\"|'[^']*'))?\s*\)"
)
_HTML_IMAGE = re.compile(
    r"<img\b[^>]*\bsrc\s*=\s*(?:\"([^\"]*)\"|'([^']*)')", re.IGNORECASE
)
_URL_USERINFO = re.compile(
    r"(?P<scheme>[A-Za-z][A-Za-z0-9+.-]*://)(?P<userinfo>[^/@\s]+)@"
)


def normalize_extensions(values: Iterable[str]) -> tuple[str, ...]:
    if isinstance(values, str):
        values = values.split(",")
    normalized: list[str] = []
    for value in values:
        extension = str(value).strip().lower()
        if not extension:
            continue
        if not extension.startswith("."):
            extension = f".{extension}"
        if extension not in normalized:
            normalized.append(extension)
    return tuple(normalized)


def resolve_allowed_roots(raw: Union[str, Iterable[str]]) -> tuple[Path, ...]:
    if isinstance(raw, str):
        parts = raw.split(os.pathsep)
    else:
        parts = list(raw)
    roots: list[Path] = []
    for part in parts:
        value = str(part).strip()
        if not value:
            continue
        root = Path(value).expanduser().resolve()
        if root not in roots:
            roots.append(root)
    return tuple(roots)


def _is_within(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def _matching_root(path: Path, roots: tuple[Path, ...]) -> Path:
    for root in roots:
        if _is_within(path, root):
            return root
    raise RetrievalError(
        "path_outside_allowed_roots",
        "Path is outside the configured allowed roots",
    )


def _has_symlink_component(candidate: Path, root: Path) -> bool:
    candidate_abs = Path(os.path.abspath(candidate))
    root_abs = Path(os.path.abspath(root))
    try:
        candidate_abs.relative_to(root_abs)
    except ValueError:
        return candidate_abs.is_symlink()
    current = candidate_abs
    while True:
        if current.is_symlink():
            return True
        if current == root_abs or current == current.parent:
            return False
        current = current.parent


def resolve_ingest_path(
    path: str,
    roots: tuple[Path, ...],
    allowed_extensions: tuple[str, ...],
    max_bytes: int,
) -> tuple[Path, Path, str]:
    candidate = Path(path).expanduser()
    if candidate.suffix.lower() in HTML_EXTENSIONS:
        raise RetrievalError(
            "unsupported_extension",
            f"HTML files are not supported: {candidate.suffix}",
        )
    try:
        resolved = candidate.resolve(strict=True)
    except FileNotFoundError as exc:
        raise RetrievalError("not_a_file", "Path does not exist") from exc
    except OSError as exc:
        raise RetrievalError("not_a_file", "Path cannot be resolved") from exc

    if not resolved.is_file():
        raise RetrievalError("not_a_file", "Path is not a regular file")

    root = _matching_root(resolved, roots)
    if candidate.is_symlink() or _has_symlink_component(candidate, root):
        raise RetrievalError(
            "symlink_not_allowed", "Symlinks are not allowed for ingestion"
        )

    extension = resolved.suffix.lower()
    if extension not in allowed_extensions:
        raise RetrievalError(
            "unsupported_extension", f"Extension is not allowed: {extension}"
        )
    if resolved.stat().st_size > max_bytes:
        raise RetrievalError(
            "file_too_large", f"File exceeds the {max_bytes}-byte limit"
        )
    return resolved, root, make_display_path(resolved, roots)


def make_display_path(resolved: Path, roots: tuple[Path, ...]) -> str:
    root = _matching_root(resolved, roots)
    relative = resolved.relative_to(root).as_posix()
    duplicate = sum(item.name == root.name for item in roots) > 1
    occurrence = [item for item in roots if item.name == root.name].index(root) + 1
    prefix = root.name
    if duplicate and occurrence > 1:
        prefix = f"{root.name}-{occurrence}"
    return f"{prefix}/{relative}"


def _local_image_reference(document: Path, reference: str) -> Optional[Path]:
    target = reference.strip()
    if not target or target.startswith("#") or target.startswith("//"):
        return None
    parsed = urlsplit(target)
    if parsed.scheme.lower() in _REMOTE_SCHEMES or parsed.netloc:
        return None
    raw_path = unquote(parsed.path)
    if not raw_path:
        return None
    candidate = Path(raw_path).expanduser()
    if not candidate.is_absolute():
        candidate = document.parent / candidate
    return candidate


def check_markdown_image_refs(resolved: Path, roots: tuple[Path, ...]) -> None:
    try:
        text = resolved.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise RetrievalError("not_a_file", "Markdown file cannot be read") from exc

    references: list[str] = []
    for match in _MARKDOWN_IMAGE.finditer(text):
        references.append(match.group(1) or match.group(2) or "")
    for match in _HTML_IMAGE.finditer(text):
        references.append(match.group(1) or match.group(2) or "")

    for reference in references:
        candidate = _local_image_reference(resolved, reference)
        if candidate is None:
            continue
        try:
            image = candidate.resolve(strict=True)
        except (FileNotFoundError, OSError) as exc:
            raise RetrievalError(
                "not_a_file", "Markdown image does not exist"
            ) from exc
        root = _matching_root(image, roots)
        if candidate.is_symlink() or _has_symlink_component(candidate, root):
            raise RetrievalError(
                "symlink_not_allowed", "Symlinked Markdown images are not allowed"
            )
        if not image.is_file():
            raise RetrievalError("not_a_file", "Markdown image is not a file")


def is_loopback_url(url: str) -> bool:
    try:
        parsed = urlsplit(url)
        host = parsed.hostname
    except ValueError:
        return False
    if not host:
        return False
    if host.lower() == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def validate_qmd_url(url: str, allow_remote: bool) -> None:
    try:
        parsed = urlsplit(url)
        parsed.port
    except ValueError as exc:
        raise RetrievalError(
            "configuration_error", "QMD URL is invalid"
        ) from exc
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise RetrievalError(
            "configuration_error", "QMD URL must be an http(s) URL"
        )
    if parsed.username is not None or parsed.password is not None:
        raise RetrievalError(
            "configuration_error", "QMD URL must not contain credentials"
        )
    if not allow_remote and not is_loopback_url(url):
        raise RetrievalError(
            "configuration_error",
            "QMD URL must use a loopback host unless remote access is enabled",
        )


def redact_url_userinfo(url: str) -> str:
    return _URL_USERINFO.sub(r"\g<scheme>[REDACTED]@", url)


def redact_text(text: str, secrets: Iterable[str] = ()) -> str:
    redacted = text
    for secret in sorted(
        {str(value) for value in secrets if str(value)}, key=len, reverse=True
    ):
        redacted = redacted.replace(secret, "[REDACTED]")
    return redact_url_userinfo(redacted)
