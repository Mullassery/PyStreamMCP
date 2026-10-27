import os

import pytest

pytestmark = pytest.mark.skipif(
    not os.getenv("PYSTREAMMCP_TEST_QMD_URL")
    and os.getenv("PYSTREAMMCP_TEST_RAG") != "1",
    reason="set PYSTREAMMCP_TEST_QMD_URL or PYSTREAMMCP_TEST_RAG=1",
)


@pytest.mark.skipif(not os.getenv("PYSTREAMMCP_TEST_QMD_URL"), reason="no live QMD")
def test_live_qmd_health_and_query():
    from pystreammcp.retrieval.base import BackendSearchRequest
    from pystreammcp.retrieval.config import QmdConfig
    from pystreammcp.retrieval.qmd import QmdBackend

    backend = QmdBackend(
        QmdConfig(
            enabled=True,
            url=os.environ["PYSTREAMMCP_TEST_QMD_URL"],
            collections=(os.environ["PYSTREAMMCP_TEST_QMD_COLLECTION"],),
        )
    )
    try:
        assert backend.health().status == "ok"
        backend.search(
            BackendSearchRequest(
                query="test",
                mode=None,
                collections=(),
                content_type=None,
                limit=1,
                include_content=False,
                max_content_chars=100,
                timeout_s=10.0,
                intent=None,
            )
        )
    finally:
        backend.close()


@pytest.mark.skipif(os.getenv("PYSTREAMMCP_TEST_RAG") != "1", reason="no live RAG")
def test_live_rag_ingest_and_query():
    from pystreammcp.retrieval.models import RequestedBackend, RetrievalRequest
    from pystreammcp.retrieval.service import RetrievalService

    doc = os.environ["PYSTREAMMCP_TEST_RAG_DOC"]
    service = RetrievalService.from_env()
    try:
        result = service.ingest(doc)
        assert result.status in {"processed", "skipped"}
        service.search(
            RetrievalRequest(query="test", backend=RequestedBackend.RAG_ANYTHING)
        )
    finally:
        service.close()
