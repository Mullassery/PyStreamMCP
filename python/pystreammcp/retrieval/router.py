from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .base import RetrievalBackend
from .errors import RetrievalError
from .models import BackendName, RequestedBackend, RetrievalRequest


@dataclass
class RoutingDecision:
    backends: list[BackendName]
    diagnostics: dict[str, Any]


def _ordered(
    names: tuple[BackendName, ...], priority: tuple[BackendName, ...]
) -> list[BackendName]:
    ordered: list[BackendName] = []
    for name in (*priority, *names):
        if name in names and name not in ordered:
            ordered.append(name)
    return ordered


def _skipped(
    name: BackendName, reason: str, error: dict[str, Any] | None = None
) -> dict[str, Any]:
    item: dict[str, Any] = {"backend": name.value, "reason": reason}
    if error is not None:
        item["error"] = error
    return item


def _decision(
    request: RetrievalRequest,
    selected: list[BackendName],
    skipped: list[dict[str, Any]],
) -> RoutingDecision:
    return RoutingDecision(
        backends=selected,
        diagnostics={
            "requested": request.backend.value
            if isinstance(request.backend, RequestedBackend)
            else str(request.backend),
            "selected": [name.value for name in selected],
            "skipped": skipped,
        },
    )


def _capabilities(backends: Mapping[BackendName, RetrievalBackend], name: BackendName):
    return backends[name].capabilities()


def _enabled_and_available(
    backends: Mapping[BackendName, RetrievalBackend], name: BackendName
) -> bool:
    if name not in backends:
        return False
    caps = _capabilities(backends, name)
    return caps.enabled and caps.available


def route(
    request: RetrievalRequest,
    backends: Mapping[BackendName, RetrievalBackend],
    priority: tuple[BackendName, ...],
) -> RoutingDecision:
    requested = request.backend
    order = _ordered(tuple(backends), priority)

    if requested == RequestedBackend.ALL:
        selected = [
            name for name in order if _capabilities(backends, name).enabled
        ]
        if not selected:
            raise RetrievalError(
                "no_available_backend", "No enabled retrieval backends"
            )
        skipped = [
            _skipped(name, "disabled")
            for name in order
            if name not in selected
        ]
        return _decision(request, selected, skipped)

    if requested in {RequestedBackend.QMD, RequestedBackend.RAG_ANYTHING}:
        name = BackendName(requested.value)
        backend = backends.get(name)
        if backend is None or not backend.capabilities().enabled:
            raise RetrievalError(
                "not_configured", f"{name.value} is not configured"
            )
        caps = backend.capabilities()
        if not caps.available:
            raise RetrievalError(
                "unavailable",
                f"{name.value} is unavailable",
                backend=name,
                details=caps.error,
            )
        return _decision(request, [name], [])

    if requested != RequestedBackend.AUTO:
        raise RetrievalError(
            "invalid_backend", f"Unknown backend: {requested}"
        )

    skipped: list[dict[str, Any]] = []
    for name in order:
        caps = _capabilities(backends, name)
        if not caps.enabled:
            skipped.append(_skipped(name, "disabled"))
        elif not caps.available:
            skipped.append(_skipped(name, "unavailable", caps.error))

    available = [
        name for name in order if _enabled_and_available(backends, name)
    ]

    if request.collections:
        if not _enabled_and_available(backends, BackendName.QMD):
            raise RetrievalError(
                "no_available_backend",
                "QMD is required when collections are selected",
            )
        for name in available:
            if name is not BackendName.QMD:
                skipped.append(_skipped(name, "collections_require_qmd"))
        return _decision(request, [BackendName.QMD], skipped)

    if request.content_type and request.content_type.lower() != "text":
        candidates = [
            name
            for name in available
            if request.content_type.lower()
            in {item.lower() for item in _capabilities(backends, name).content_types}
        ]
        if not candidates:
            raise RetrievalError(
                "no_available_backend",
                f"No backend supports content type: {request.content_type}",
            )
        preferred = [
            name
            for name in (BackendName.RAG_ANYTHING, BackendName.QMD)
            if name in candidates
        ]
        selected = (preferred or candidates)[0]
        for name in available:
            if name is not selected:
                skipped.append(_skipped(name, "content_type"))
        return _decision(request, [selected], skipped)

    if request.mode:
        candidates = [
            name
            for name in available
            if request.mode in _capabilities(backends, name).modes
        ]
        if len(candidates) == 1:
            selected = candidates[0]
            for name in available:
                if name is not selected:
                    skipped.append(_skipped(name, "mode"))
            return _decision(request, [selected], skipped)

    chosen = next(
        (
            name
            for name in order
            if _enabled_and_available(backends, name)
        ),
        None,
    )
    if chosen is None:
        raise RetrievalError(
            "no_available_backend", "No available retrieval backends"
        )
    for name in available:
        if name is not chosen:
            skipped.append(_skipped(name, "priority"))
    return _decision(request, [chosen], skipped)
