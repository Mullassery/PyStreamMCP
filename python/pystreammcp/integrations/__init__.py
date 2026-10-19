"""PyStreamMCP integrations with popular agent frameworks.

Only ``langchain``, ``llamaindex``, and ``semantic_kernel`` are supported and
real-tested. The ``crewai``, ``pydantic_ai``, and ``haystack`` modules are
experimental in-process helpers that do not import those frameworks; using
them requires an explicit opt-in.
"""

__all__ = ["langchain", "llamaindex", "semantic_kernel"]
