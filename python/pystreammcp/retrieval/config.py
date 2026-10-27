from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Optional

from .errors import RetrievalError
from .security import normalize_extensions, resolve_allowed_roots, validate_qmd_url

DEFAULT_RAG_EXTENSIONS = (
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".tif",
    ".tiff",
    ".gif",
    ".webp",
    ".txt",
    ".md",
)


@dataclass(frozen=True)
class QmdConfig:
    enabled: bool = False
    url: str = "http://127.0.0.1:8181"
    collections: tuple[str, ...] = ()
    timeout_s: float = 10.0
    health_timeout_s: float = 1.5
    allow_remote: bool = False
    trust_env: bool = False


@dataclass(frozen=True)
class RagProviderConfig:
    llm_model: Optional[str]
    llm_base_url: Optional[str]
    llm_api_key: Optional[str]
    embedding_model: Optional[str]
    embedding_base_url: Optional[str]
    embedding_api_key: Optional[str]
    embedding_dim: Optional[int]
    embedding_max_tokens: int = 8192
    vision_model: Optional[str] = None
    vision_base_url: Optional[str] = None
    vision_api_key: Optional[str] = None


@dataclass(frozen=True)
class RagConfig:
    enabled: bool = False
    working_dir: Path = Path("./rag_storage")
    parsed_dir: Path = Path("./rag_storage/parsed")
    allowed_roots: tuple[Path, ...] = ()
    allowed_extensions: tuple[str, ...] = DEFAULT_RAG_EXTENSIONS
    parser: str = "mineru"
    parse_method: str = "auto"
    query_mode: str = "mix"
    enable_image_processing: bool = True
    enable_table_processing: bool = True
    enable_equation_processing: bool = True
    max_file_mb: int = 100
    query_timeout_s: float = 60.0
    ingest_timeout_s: float = 600.0
    force_multimodal_reprocess: bool = False
    provider_name: str = "none"
    provider: Optional[RagProviderConfig] = None
    source_mode: str = "auto"


@dataclass(frozen=True)
class RetrievalConfig:
    qmd: QmdConfig
    rag: RagConfig
    qmd_requested: bool
    rag_requested: bool
    qmd_error: Optional[str]
    rag_error: Optional[str]

    @classmethod
    def from_env(
        cls, env: Optional[Mapping[str, str]] = None
    ) -> "RetrievalConfig":
        return _from_env(cls, env)


def _value(env: Mapping[str, str], name: str, default: str = "") -> str:
    value = env.get(name, default)
    return value if value is not None else default


def _split_csv(raw: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in raw.split(",") if item.strip())


def _parse_bool(
    env: Mapping[str, str], name: str, default: bool, errors: list[str]
) -> bool:
    raw = _value(env, name)
    if not raw.strip():
        return default
    normalized = raw.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    errors.append(f"{name} must be a boolean")
    return default


def _parse_int(
    env: Mapping[str, str], name: str, default: int, errors: list[str]
) -> int:
    raw = _value(env, name)
    if not raw.strip():
        return default
    try:
        return int(raw)
    except ValueError:
        errors.append(f"{name} must be an integer")
        return default


def _parse_float(
    env: Mapping[str, str], name: str, default: float, errors: list[str]
) -> float:
    raw = _value(env, name)
    if not raw.strip():
        return default
    try:
        return float(raw)
    except ValueError:
        errors.append(f"{name} must be a number")
        return default


def _optional(raw: str) -> Optional[str]:
    value = raw.strip()
    return value or None


def _qmd_config(env: Mapping[str, str], errors: list[str]) -> tuple[QmdConfig, bool]:
    enabled = _parse_bool(env, "PYSTREAMMCP_QMD_ENABLED", False, errors)
    allow_remote = _parse_bool(env, "PYSTREAMMCP_QMD_ALLOW_REMOTE", False, errors)
    config = QmdConfig(
        enabled=enabled,
        url=_value(env, "PYSTREAMMCP_QMD_URL", "http://127.0.0.1:8181").strip(),
        collections=_split_csv(_value(env, "PYSTREAMMCP_QMD_COLLECTIONS")),
        timeout_s=_parse_float(env, "PYSTREAMMCP_QMD_TIMEOUT_S", 10.0, errors),
        health_timeout_s=_parse_float(
            env, "PYSTREAMMCP_QMD_HEALTH_TIMEOUT_S", 1.5, errors
        ),
        allow_remote=allow_remote,
        trust_env=_parse_bool(env, "PYSTREAMMCP_QMD_TRUST_ENV", False, errors),
    )
    if enabled and not config.collections:
        errors.append("PYSTREAMMCP_QMD_COLLECTIONS is required when QMD is enabled")
    try:
        validate_qmd_url(config.url, allow_remote=config.allow_remote)
    except RetrievalError as exc:
        errors.append(f"PYSTREAMMCP_QMD_URL: {exc.message}")
    return config, enabled


def _rag_provider(
    env: Mapping[str, str], errors: list[str]
) -> tuple[str, Optional[RagProviderConfig]]:
    name = _value(env, "PYSTREAMMCP_RAG_PROVIDER", "none").strip().lower() or "none"
    if name not in {"none", "openai_compatible"}:
        errors.append(
            "PYSTREAMMCP_RAG_PROVIDER must be 'none' or 'openai_compatible'"
        )
        return name, None
    if name == "none":
        return name, None

    llm_model = _optional(_value(env, "PYSTREAMMCP_RAG_LLM_MODEL"))
    llm_base_url = _optional(_value(env, "PYSTREAMMCP_RAG_LLM_BASE_URL"))
    llm_api_key = _optional(_value(env, "PYSTREAMMCP_RAG_LLM_API_KEY"))
    embedding_model = _optional(_value(env, "PYSTREAMMCP_RAG_EMBED_MODEL"))
    embedding_base_url = _optional(_value(env, "PYSTREAMMCP_RAG_EMBED_BASE_URL"))
    embedding_api_key = _optional(
        _value(env, "PYSTREAMMCP_RAG_EMBED_API_KEY")
    ) or llm_api_key
    embedding_dim = _parse_int(
        env, "PYSTREAMMCP_RAG_EMBED_DIM", 0, errors
    ) or None
    embedding_max_tokens = _parse_int(
        env, "PYSTREAMMCP_RAG_EMBED_MAX_TOKENS", 8192, errors
    )
    provider = RagProviderConfig(
        llm_model=llm_model,
        llm_base_url=llm_base_url,
        llm_api_key=llm_api_key,
        embedding_model=embedding_model,
        embedding_base_url=embedding_base_url,
        embedding_api_key=embedding_api_key,
        embedding_dim=embedding_dim,
        embedding_max_tokens=embedding_max_tokens,
        vision_model=_optional(_value(env, "PYSTREAMMCP_RAG_VISION_MODEL")),
        vision_base_url=_optional(_value(env, "PYSTREAMMCP_RAG_VISION_BASE_URL")),
        vision_api_key=_optional(_value(env, "PYSTREAMMCP_RAG_VISION_API_KEY")),
    )

    missing = [
        variable
        for variable, value in (
            ("PYSTREAMMCP_RAG_LLM_MODEL", llm_model),
            ("PYSTREAMMCP_RAG_LLM_BASE_URL", llm_base_url),
            ("PYSTREAMMCP_RAG_LLM_API_KEY", llm_api_key),
            ("PYSTREAMMCP_RAG_EMBED_MODEL", embedding_model),
            ("PYSTREAMMCP_RAG_EMBED_BASE_URL", embedding_base_url),
            ("PYSTREAMMCP_RAG_EMBED_API_KEY", embedding_api_key),
            ("PYSTREAMMCP_RAG_EMBED_DIM", embedding_dim),
        )
        if not value
    ]
    if missing:
        errors.append(
            "PYSTREAMMCP_RAG_PROVIDER=openai_compatible requires: "
            + ", ".join(missing)
        )
    return name, provider


def _rag_config(env: Mapping[str, str], errors: list[str]) -> tuple[RagConfig, bool]:
    enabled = _parse_bool(env, "PYSTREAMMCP_RAG_ENABLED", False, errors)
    working_dir = Path(
        _value(env, "PYSTREAMMCP_RAG_WORKING_DIR", "./rag_storage").strip()
        or "./rag_storage"
    ).expanduser()
    extensions_raw = _value(
        env, "PYSTREAMMCP_RAG_ALLOWED_EXTENSIONS", ",".join(DEFAULT_RAG_EXTENSIONS)
    )
    provider_name, provider = _rag_provider(env, errors)
    source_mode = _value(env, "PYSTREAMMCP_RAG_SOURCE", "auto").strip().lower()
    if not source_mode:
        source_mode = "auto"
    if source_mode not in {"auto", "installed", "vendored"}:
        errors.append(
            "PYSTREAMMCP_RAG_SOURCE must be 'auto', 'installed', or 'vendored'"
        )
    config = RagConfig(
        enabled=enabled,
        working_dir=working_dir,
        parsed_dir=working_dir / "parsed",
        allowed_roots=resolve_allowed_roots(
            _value(env, "PYSTREAMMCP_RAG_ALLOWED_ROOTS")
        ),
        allowed_extensions=normalize_extensions(_split_csv(extensions_raw))
        or DEFAULT_RAG_EXTENSIONS,
        parser=_value(env, "PYSTREAMMCP_RAG_PARSER", "mineru").strip() or "mineru",
        parse_method=_value(env, "PYSTREAMMCP_RAG_PARSE_METHOD", "auto").strip()
        or "auto",
        query_mode=_value(env, "PYSTREAMMCP_RAG_QUERY_MODE", "mix").strip() or "mix",
        enable_image_processing=_parse_bool(
            env, "PYSTREAMMCP_RAG_ENABLE_IMAGE_PROCESSING", True, errors
        ),
        enable_table_processing=_parse_bool(
            env, "PYSTREAMMCP_RAG_ENABLE_TABLE_PROCESSING", True, errors
        ),
        enable_equation_processing=_parse_bool(
            env, "PYSTREAMMCP_RAG_ENABLE_EQUATION_PROCESSING", True, errors
        ),
        max_file_mb=_parse_int(
            env, "PYSTREAMMCP_RAG_MAX_FILE_MB", 100, errors
        ),
        query_timeout_s=_parse_float(
            env, "PYSTREAMMCP_RAG_QUERY_TIMEOUT_S", 60.0, errors
        ),
        ingest_timeout_s=_parse_float(
            env, "PYSTREAMMCP_RAG_INGEST_TIMEOUT_S", 600.0, errors
        ),
        force_multimodal_reprocess=_parse_bool(
            env, "PYSTREAMMCP_RAG_FORCE_MULTIMODAL_REPROCESS", False, errors
        ),
        provider_name=provider_name,
        provider=provider,
        source_mode=source_mode,
    )
    return config, enabled


def _from_env(
    cls: type[RetrievalConfig], env: Optional[Mapping[str, str]] = None
) -> RetrievalConfig:
    values = os.environ if env is None else env
    qmd_errors: list[str] = []
    rag_errors: list[str] = []
    qmd, qmd_requested = _qmd_config(values, qmd_errors)
    rag, rag_requested = _rag_config(values, rag_errors)
    return cls(
        qmd=qmd,
        rag=rag,
        qmd_requested=qmd_requested,
        rag_requested=rag_requested,
        qmd_error="; ".join(qmd_errors) or None,
        rag_error="; ".join(rag_errors) or None,
    )
