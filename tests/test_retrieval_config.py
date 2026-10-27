from pystreammcp.retrieval.config import RetrievalConfig


def test_defaults_are_disabled():
    c = RetrievalConfig.from_env({})
    assert (c.qmd_requested, c.rag_requested) == (False, False)
    assert c.qmd_error is None and c.rag_error is None


def test_qmd_env_and_collection_allowlist():
    c = RetrievalConfig.from_env(
        {
            "PYSTREAMMCP_QMD_ENABLED": "true",
            "PYSTREAMMCP_QMD_URL": "http://127.0.0.1:8181",
            "PYSTREAMMCP_QMD_COLLECTIONS": "notes, docs",
            "PYSTREAMMCP_QMD_TIMEOUT_S": "9.5",
            "PYSTREAMMCP_QMD_TRUST_ENV": "true",
        }
    )
    assert c.qmd.collections == ("notes", "docs")
    assert c.qmd.timeout_s == 9.5
    assert c.qmd.trust_env is True
    assert c.qmd_error is None


def test_qmd_requires_collections_when_enabled():
    c = RetrievalConfig.from_env({"PYSTREAMMCP_QMD_ENABLED": "true"})
    assert c.qmd_requested is True
    assert "QMD_COLLECTIONS" in c.qmd_error


def test_qmd_remote_requires_opt_in():
    c = RetrievalConfig.from_env(
        {
            "PYSTREAMMCP_QMD_ENABLED": "true",
            "PYSTREAMMCP_QMD_COLLECTIONS": "docs",
            "PYSTREAMMCP_QMD_URL": "https://qmd.example.com",
        }
    )
    assert "loopback" in c.qmd_error


def test_rag_missing_roots_is_not_ingestion_ready():
    c = RetrievalConfig.from_env({"PYSTREAMMCP_RAG_ENABLED": "true"})
    assert c.rag.allowed_roots == ()
    assert c.rag_error is None


def test_rag_provider_parsing_and_embed_key_fallback():
    c = RetrievalConfig.from_env(
        {
            "PYSTREAMMCP_RAG_ENABLED": "true",
            "PYSTREAMMCP_RAG_ALLOWED_ROOTS": "/tmp/docs",
            "PYSTREAMMCP_RAG_PROVIDER": "openai_compatible",
            "PYSTREAMMCP_RAG_LLM_MODEL": "gpt-4.1",
            "PYSTREAMMCP_RAG_LLM_BASE_URL": "https://llm.example.com/v1",
            "PYSTREAMMCP_RAG_LLM_API_KEY": "sk-llm",
            "PYSTREAMMCP_RAG_EMBED_MODEL": "embed",
            "PYSTREAMMCP_RAG_EMBED_BASE_URL": "https://embed.example.com/v1",
            "PYSTREAMMCP_RAG_EMBED_DIM": "1024",
        }
    )
    assert c.rag_error is None
    assert c.rag.provider.embedding_api_key == "sk-llm"
    assert c.rag.provider.embedding_max_tokens == 8192


def test_invalid_integer_is_config_error_not_exception():
    c = RetrievalConfig.from_env(
        {
            "PYSTREAMMCP_RAG_ENABLED": "true",
            "PYSTREAMMCP_RAG_MAX_FILE_MB": "lots",
        }
    )
    assert "MAX_FILE_MB" in c.rag_error


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
