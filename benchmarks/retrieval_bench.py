#!/usr/bin/env python3
"""Offline-first retrieval benchmark.

The default fake mode measures routing, service dispatch, and response
serialization without touching a network or loading a model. QMD and RAG
modes are explicit opt-ins.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from pystreammcp.retrieval.base import (  # noqa: E402
    BackendCapabilities,
    BackendHealth,
    BackendSearchRequest,
    BackendSearchResult,
)
from pystreammcp.retrieval.config import QmdConfig  # noqa: E402
from pystreammcp.retrieval.errors import RetrievalError  # noqa: E402
from pystreammcp.retrieval.models import (  # noqa: E402
    BackendName,
    RetrievalHit,
    RetrievalRequest,
)
from pystreammcp.retrieval.qmd import QmdBackend  # noqa: E402
from pystreammcp.retrieval.service import RetrievalService  # noqa: E402

_DEFAULT_QUERIES = tuple(
    f"retrieval benchmark query {index}" for index in range(1, 11)
)


class FakeBackend:
    name = BackendName.QMD

    def capabilities(self) -> BackendCapabilities:
        return BackendCapabilities(
            backend=self.name,
            enabled=True,
            configured=True,
            available=True,
            modes=("auto",),
            content_types=("text",),
            max_limit=50,
            supports_ingestion=False,
            supports_full_content=True,
            score_kind="score",
            network_egress="none",
            error=None,
        )

    def health(self) -> BackendHealth:
        return BackendHealth(
            backend=self.name,
            available=True,
            status="ok",
            message=None,
            elapsed_ms=0,
        )

    def search(self, request: BackendSearchRequest) -> BackendSearchResult:
        hit = RetrievalHit(
            backend=self.name,
            rank=1,
            document_id="fake-1",
            title="Fake hit",
            source_uri="fake://benchmark/1",
            locator={"chunk": 0},
            excerpt="offline benchmark fixture",
            content=None,
            score=1.0,
            score_kind="score",
            metadata={},
        )
        return BackendSearchResult(hits=[hit], truncated=False, diagnostics={})

    def close(self) -> None:
        pass


def _positive_int(raw: str) -> int:
    value = int(raw)
    if value <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return value


def _non_negative_int(raw: str) -> int:
    value = int(raw)
    if value < 0:
        raise argparse.ArgumentTypeError("must be a non-negative integer")
    return value


def _percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, math.ceil(fraction * len(ordered)) - 1)
    return round(ordered[index], 3)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Benchmark retrieval routing and backend latency offline."
    )
    parser.add_argument(
        "--queries",
        type=_positive_int,
        default=10,
        help="Number of measured queries (default: 10).",
    )
    parser.add_argument(
        "--query",
        action="append",
        default=None,
        help="Query text to cycle through; may be repeated.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON metrics.")
    parser.add_argument(
        "--warmup",
        type=_non_negative_int,
        default=1,
        help="Unmeasured warmup requests (default: 1).",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--qmd-url",
        default=None,
        help="Benchmark a real QMD service at this URL.",
    )
    mode.add_argument(
        "--rag",
        action="store_true",
        help="Benchmark RAG-Anything configured from the environment.",
    )
    return parser


def _queries(count: int, supplied: Optional[list[str]]) -> list[str]:
    source = tuple(item for item in (supplied or ()) if item)
    if not source:
        source = _DEFAULT_QUERIES
    return [source[index % len(source)] for index in range(count)]


def _service(args: argparse.Namespace) -> tuple[RetrievalService, str]:
    if args.qmd_url:
        collections = tuple(
            item.strip()
            for item in os.environ.get("PYSTREAMMCP_QMD_COLLECTIONS", "").split(",")
            if item.strip()
        )
        config = QmdConfig(
            enabled=True,
            url=args.qmd_url,
            collections=collections,
        )
        return RetrievalService([QmdBackend(config)]), "qmd"
    if args.rag:
        return RetrievalService.from_env(), "rag"
    return RetrievalService([FakeBackend()]), "fake"


def _measure(
    service: RetrievalService, queries: list[str], warmup: int
) -> dict[str, Any]:
    for index in range(warmup):
        try:
            service.search(RetrievalRequest(query=queries[index % len(queries)]))
        except RetrievalError:
            pass

    durations: list[float] = []
    hit_count = 0
    empty_count = 0
    error_count = 0
    timeout_count = 0
    for query in queries:
        started = time.perf_counter()
        try:
            response = service.search(RetrievalRequest(query=query))
            response.to_dict()
        except RetrievalError as error:
            error_count += 1
            if error.code == "timeout":
                timeout_count += 1
        except Exception:
            error_count += 1
        else:
            hits = sum(len(group.hits) for group in response.groups)
            hit_count += hits
            if hits == 0:
                empty_count += 1
            for group in response.groups:
                error = group.error or {}
                if error:
                    error_count += 1
                    if error.get("code") == "timeout":
                        timeout_count += 1
        finally:
            durations.append((time.perf_counter() - started) * 1000.0)

    total_ms = sum(durations)
    return {
        "sample_count": len(queries),
        "hit_count": hit_count,
        "empty_count": empty_count,
        "error_count": error_count,
        "timeout_count": timeout_count,
        "p50_ms": _percentile(durations, 0.50),
        "p95_ms": _percentile(durations, 0.95),
        "p99_ms": _percentile(durations, 0.99),
        "mean_ms": round(statistics.mean(durations), 3) if durations else 0.0,
        "throughput_qps": (
            round(len(queries) / (total_ms / 1000.0), 3) if total_ms else 0.0
        ),
    }


def main(argv: Optional[list[str]] = None) -> int:
    args = _build_parser().parse_args(argv)
    service, mode = _service(args)
    try:
        metrics = _measure(service, _queries(args.queries, args.query), args.warmup)
    finally:
        service.close()
    metrics["mode"] = mode

    if args.json:
        print(json.dumps(metrics, indent=2, sort_keys=True))
    else:
        print(f"mode: {metrics['mode']}")
        for key in (
            "sample_count",
            "hit_count",
            "empty_count",
            "error_count",
            "timeout_count",
            "p50_ms",
            "p95_ms",
            "p99_ms",
            "mean_ms",
            "throughput_qps",
        ):
            print(f"{key}: {metrics[key]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
