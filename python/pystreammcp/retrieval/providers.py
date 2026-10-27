from __future__ import annotations

import importlib.util
from typing import Any, Optional

from .config import RagConfig
from .errors import RetrievalError

_REQUIRED_FIELDS = (
    ("llm_model", "LLM_MODEL"),
    ("llm_base_url", "LLM_BASE_URL"),
    ("llm_api_key", "LLM_API_KEY"),
    ("embedding_model", "EMBED_MODEL"),
    ("embedding_base_url", "EMBED_BASE_URL"),
    ("embedding_dim", "EMBED_DIM"),
)


def validate_provider_config(config: RagConfig) -> Optional[str]:
    if config.provider_name != "openai_compatible":
        return "RAG_PROVIDER"
    provider = config.provider
    if provider is None:
        return "LLM_MODEL"
    for field_name, env_name in _REQUIRED_FIELDS:
        value = getattr(provider, field_name, None)
        if value is None or value == "":
            return env_name
        if field_name == "embedding_dim" and (
            not isinstance(value, int) or isinstance(value, bool) or value <= 0
        ):
            return env_name
    return None


async def build_openai_compatible_engine(config: RagConfig) -> Any:
    missing = validate_provider_config(config)
    if missing is not None:
        raise RetrievalError(
            "configuration_error", f"{missing} must be configured"
        )
    provider = config.provider
    assert provider is not None

    from . import deps

    source = deps.ensure_rag_import_path(config.source_mode)
    if (
        importlib.util.find_spec("raganything") is None
        or importlib.util.find_spec("lightrag") is None
    ):
        raise RetrievalError(
            "missing_dependency",
            "Install rag-anything and lightrag "
            f"(selected source: {source.source})",
        )

    try:
        from lightrag import LightRAG
        from lightrag.llm.openai import openai_complete_if_cache, openai_embed
        from lightrag.utils import EmbeddingFunc
        from raganything import RAGAnything, RAGAnythingConfig
    except ImportError as exc:
        raise RetrievalError(
            "missing_dependency",
            "RAG-Anything or LightRAG could not be imported "
            f"(selected source: {source.source})",
        ) from exc

    llm_model = provider.llm_model
    llm_base_url = provider.llm_base_url
    llm_api_key = provider.llm_api_key
    embed_model = provider.embedding_model
    embed_base_url = provider.embedding_base_url
    embed_api_key = provider.embedding_api_key
    embedding_dim = provider.embedding_dim

    async def llm_model_func(
        prompt: str,
        system_prompt: Optional[str] = None,
        history_messages: Optional[list[Any]] = None,
        **kwargs: Any,
    ) -> Any:
        kwargs.setdefault("api_key", llm_api_key)
        kwargs.setdefault("base_url", llm_base_url)
        return await openai_complete_if_cache(
            llm_model,
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages or [],
            **kwargs,
        )

    embed_func = getattr(openai_embed, "func", openai_embed)

    async def embedding_func(texts: Any) -> Any:
        return await embed_func(
            texts,
            model=embed_model,
            api_key=embed_api_key,
            base_url=embed_base_url,
            embedding_dim=embedding_dim,
        )

    embedding = EmbeddingFunc(
        embedding_dim=embedding_dim,
        max_token_size=provider.embedding_max_tokens,
        func=embedding_func,
    )

    lightrag = LightRAG(
        working_dir=str(config.working_dir),
        llm_model_func=llm_model_func,
        embedding_func=embedding,
    )
    await lightrag.initialize_storages()
    await lightrag.initialize_pipeline_status()

    rag_config = RAGAnythingConfig(
        working_dir=str(config.working_dir),
        parser=config.parser,
        parse_method=config.parse_method,
        enable_image_processing=config.enable_image_processing,
        enable_table_processing=config.enable_table_processing,
        enable_equation_processing=config.enable_equation_processing,
    )
    rag_kwargs: dict[str, Any] = {
        "config": rag_config,
        "lightrag": lightrag,
    }

    if provider.vision_model:
        vision_model = provider.vision_model
        vision_base_url = provider.vision_base_url
        vision_api_key = provider.vision_api_key

        async def vision_model_func(
            prompt: str,
            system_prompt: Optional[str] = None,
            history_messages: Optional[list[Any]] = None,
            image_data: Any = None,
            **kwargs: Any,
        ) -> Any:
            if vision_api_key is not None:
                kwargs.setdefault("api_key", vision_api_key)
            if vision_base_url is not None:
                kwargs.setdefault("base_url", vision_base_url)
            if image_data is not None:
                kwargs.setdefault("image_data", image_data)
            return await openai_complete_if_cache(
                vision_model,
                prompt,
                system_prompt=system_prompt,
                history_messages=history_messages or [],
                **kwargs,
            )

        rag_kwargs["vision_model_func"] = vision_model_func

    return RAGAnything(**rag_kwargs)
