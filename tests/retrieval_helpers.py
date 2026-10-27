import time

from pystreammcp.retrieval.base import (
    BackendCapabilities,
    BackendHealth,
    BackendSearchResult,
    IngestionResult,
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
            backend=self.name,
            enabled=True,
            configured=True,
            available=True,
            modes=("auto", "hybrid", "local", "global", "naive", "mix"),
            content_types=("text",),
            max_limit=50,
            supports_ingestion=True,
            supports_full_content=True,
            score_kind="unavailable",
            network_egress="local",
            error=None,
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
            backend=self.name,
            available=True,
            status="ok",
            message="ok",
            elapsed_ms=0,
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
            document_id="doc-1",
            display_path=path,
            status="processed",
            skipped=False,
            elapsed_ms=1,
            content_types=("text",),
        )

    def close(self):
        self.closed = True
