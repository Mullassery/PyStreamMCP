"""Click commands for retrieval backends and dependency status."""

from __future__ import annotations

import json
from typing import Any, Optional

import click

from pystreammcp.retrieval import deps
from pystreammcp.retrieval.errors import RetrievalError
from pystreammcp.retrieval.models import RequestedBackend, RetrievalRequest
from pystreammcp.retrieval.service import RetrievalService


def _build_service() -> RetrievalService:
    return RetrievalService.from_env()


def _print_json(payload: Any) -> None:
    click.echo(json.dumps(payload, indent=2, sort_keys=True))


def _close(service: Any) -> None:
    if service is not None:
        service.close()


def _print_failure(error: RetrievalError, output_json: bool) -> None:
    if output_json:
        _print_json(
            {
                "status": "error",
                "error_type": "RetrievalError",
                "code": error.code,
                "message": error.message,
                "backend": getattr(error.backend, "value", error.backend),
                "retryable": error.retryable,
            }
        )
    else:
        click.echo(f"{error.code}: {error.message}", err=True)


def _print_search(response: Any) -> None:
    total = 0
    for group in response.groups:
        backend = getattr(group.backend, "value", group.backend)
        click.echo(
            f"{backend}: {group.status} ({len(group.hits)} hit(s), "
            f"{group.elapsed_ms}ms){' [truncated]' if group.truncated else ''}"
        )
        if group.error:
            click.echo(f"  {group.error.get('code')}: {group.error.get('message')}")
        for hit in group.hits:
            title = hit.title or hit.source_uri
            click.echo(f"  {hit.rank}. {title}")
            click.echo(f"     {hit.source_uri}")
            if hit.excerpt:
                click.echo(f"     {hit.excerpt}")
        total += len(group.hits)
    click.echo(f"{total} hit(s)")


def _print_capabilities(payload: dict[str, Any]) -> None:
    for entry in payload.get("backends", []):
        name = entry.get("name") or entry.get("backend") or "backend"
        click.echo(f"{name}: configured={entry.get('configured')}")
        health = entry.get("health")
        if health:
            click.echo(
                f"  health: {health.get('status')} "
                f"available={health.get('available')}"
            )


def _print_health(payload: dict[str, Any]) -> None:
    for entry in payload.get("backends", []):
        name = entry.get("backend") or entry.get("name") or "backend"
        click.echo(
            f"{name}: {entry.get('status')} available={entry.get('available')}"
        )


def _print_ingest(result: Any) -> None:
    click.echo(f"{result.display_path}: {result.status}")
    if result.document_id:
        click.echo(f"document_id: {result.document_id}")
    if result.error:
        click.echo(f"{result.error.code}: {result.error.message}", err=True)


@click.group()
def retrieval() -> None:
    """Search local knowledge and manage retrieval dependencies."""


@retrieval.command("search")
@click.argument("query")
@click.option(
    "--backend",
    type=click.Choice(["auto", "qmd", "rag_anything", "all"]),
    default="auto",
)
@click.option("--mode", default=None)
@click.option("--collection", "collections", multiple=True)
@click.option("--content-type", default=None)
@click.option("--limit", type=int, default=5)
@click.option("--include-content", is_flag=True)
@click.option("--max-content-chars", type=int, default=2000)
@click.option("--time-budget-ms", type=int, default=30000)
@click.option("--intent", default=None)
@click.option("--json", "output_json", is_flag=True)
def search(
    query: str,
    backend: str,
    mode: Optional[str],
    collections: tuple[str, ...],
    content_type: Optional[str],
    limit: int,
    include_content: bool,
    max_content_chars: int,
    time_budget_ms: int,
    intent: Optional[str],
    output_json: bool,
) -> None:
    """Search configured retrieval backends."""
    service = None
    try:
        service = _build_service()
        response = service.search(
            RetrievalRequest(
                query=query,
                backend=RequestedBackend(backend),
                mode=mode,
                collections=tuple(collections),
                content_type=content_type,
                limit=limit,
                include_content=include_content,
                max_content_chars=max_content_chars,
                time_budget_ms=time_budget_ms,
                intent=intent,
            )
        )
    except RetrievalError as error:
        _print_failure(error, output_json)
        raise SystemExit(1)
    except (ValueError, click.BadParameter) as error:
        click.echo(f"configuration_error: {error}", err=True)
        raise SystemExit(1)
    finally:
        _close(service)

    if output_json:
        _print_json(response.to_dict())
    else:
        _print_search(response)
    if response.status in {"partial", "error"}:
        raise SystemExit(1)


@retrieval.command("capabilities")
@click.option("--no-health", is_flag=True)
@click.option("--json", "output_json", is_flag=True)
def capabilities(no_health: bool, output_json: bool) -> None:
    """Report backend capabilities."""
    service = None
    try:
        service = _build_service()
        payload = service.capabilities(include_health=not no_health)
    except RetrievalError as error:
        _print_failure(error, output_json)
        raise SystemExit(1)
    finally:
        _close(service)

    if output_json:
        _print_json(payload)
    else:
        _print_capabilities(payload)


@retrieval.command("health")
@click.option("--json", "output_json", is_flag=True)
def health(output_json: bool) -> None:
    """Report backend health."""
    service = None
    try:
        service = _build_service()
        payload = service.health()
    except RetrievalError as error:
        _print_failure(error, output_json)
        raise SystemExit(1)
    finally:
        _close(service)

    if output_json:
        _print_json(payload)
    else:
        _print_health(payload)


@retrieval.command("ingest")
@click.argument("path")
@click.option("--force-multimodal", is_flag=True)
@click.option("--json", "output_json", is_flag=True)
def ingest(path: str, force_multimodal: bool, output_json: bool) -> None:
    """Ingest an allowed local document into RAG-Anything."""
    service = None
    try:
        service = _build_service()
        result = service.ingest(path, force_multimodal=force_multimodal)
    except RetrievalError as error:
        _print_failure(error, output_json)
        raise SystemExit(1)
    finally:
        _close(service)

    if output_json:
        _print_json(result.to_dict())
    else:
        _print_ingest(result)


@retrieval.group("deps")
def deps_group() -> None:
    """Inspect pinned dependency versions without modifying them."""


@deps_group.command("status")
@click.option("--offline", is_flag=True)
@click.option("--json", "output_json", is_flag=True)
def deps_status(offline: bool, output_json: bool) -> None:
    """Show vendored checksums and upstream tag status."""
    payload = deps.dependency_status(offline=offline)
    if output_json:
        _print_json(payload)
    else:
        for entry in payload.get("dependencies", []):
            line = (
                f"{entry.get('name')}: pinned={entry.get('pinned')} "
                f"latest={entry.get('latest')} state={entry.get('state')} "
                f"vendored={entry.get('vendored')}"
            )
            if entry.get("error"):
                line += f" error={entry['error']}"
            click.echo(line)
    raise SystemExit(deps.upstream_exit_code(payload))
