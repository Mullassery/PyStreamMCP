import sys
from pathlib import Path


def test_public_exports():
    from pystreammcp import (
        BackendName,
        RequestedBackend,
        RetrievalError,
        RetrievalRequest,
        RetrievalResponse,
        RetrievalService,
    )

    assert BackendName.QMD.value == "qmd"
    assert RequestedBackend.AUTO.value == "auto"
    assert RetrievalRequest(query="x").limit == 5
    assert RetrievalService and RetrievalResponse and RetrievalError


def test_retrieval_package_exports():
    from pystreammcp.retrieval import (
        QmdBackend,
        RAGAnythingBackend,
        RetrievalConfig,
        RetrievalService,
    )

    assert QmdBackend and RAGAnythingBackend and RetrievalService
    assert RetrievalConfig.from_env({}).qmd.enabled is False


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
    assert "all-integrations" in text


def test_vendor_is_source_only():
    from setuptools import find_packages

    assert (Path("vendor") / "deps.lock.json").is_file()
    assert all(not p.startswith("vendor") for p in find_packages(where="python"))
    assert "prune vendor" in Path("MANIFEST.in").read_text(encoding="utf-8")
