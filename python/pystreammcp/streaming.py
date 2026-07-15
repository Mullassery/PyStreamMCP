"""Streaming context windows for progressive retrieval in PyStreamMCP."""

from typing import List, Optional
from dataclasses import dataclass
from .context import Context


@dataclass
class StreamedContext:
    """A chunk of context in a streaming response."""

    chunk_id: int
    content: Context
    priority: float
    tokens_accumulated: int
    is_final: bool


class ContextStream:
    """Stream context progressively with budget awareness."""

    def __init__(self, query_id: str, token_budget: int):
        """Initialize context stream."""
        self.query_id = query_id
        self.chunks: List[StreamedContext] = []
        self.current_chunk = 0
        self.token_budget = token_budget
        self.tokens_used = 0

    def add_chunk(self, chunk_id: int, context: Context, priority: float = 0.5) -> None:
        """Add a chunk to the stream."""
        token_count = context.token_count

        if self.tokens_used + token_count > self.token_budget:
            raise ValueError("Token budget exceeded")

        self.tokens_used += token_count

        self.chunks.append(
            StreamedContext(
                chunk_id=chunk_id,
                content=context,
                priority=priority,
                tokens_accumulated=self.tokens_used,
                is_final=False,
            )
        )

    def next(self) -> Optional[StreamedContext]:
        """Get next chunk (sync version)."""
        if self.current_chunk < len(self.chunks):
            chunk = self.chunks[self.current_chunk]
            self.current_chunk += 1

            if self.current_chunk >= len(self.chunks):
                chunk.is_final = True

            return chunk
        return None

    def take_until_budget(self, budget: int) -> List[StreamedContext]:
        """Get all chunks up to a token budget."""
        results = []
        accumulated = 0

        while True:
            chunk = self.next()
            if not chunk:
                break

            accumulated += chunk.tokens_accumulated
            results.append(chunk)

            if accumulated >= budget:
                break

        return results

    def chunks_ready(self) -> int:
        """Get number of chunks not yet retrieved."""
        return len(self.chunks) - self.current_chunk

    def tokens_remaining(self) -> int:
        """Get tokens still available in budget."""
        return self.token_budget - self.tokens_used

    def completion_percent(self) -> float:
        """Get completion percentage."""
        if not self.chunks:
            return 0.0
        return (self.current_chunk / len(self.chunks)) * 100.0

    def sort_by_priority(self) -> None:
        """Sort chunks by priority (highest first)."""
        self.chunks.sort(key=lambda x: -x.priority)

    def get_summary(self) -> dict:
        """Get stream summary."""
        return {
            "query_id": self.query_id,
            "total_chunks": len(self.chunks),
            "chunks_retrieved": self.current_chunk,
            "chunks_remaining": self.chunks_ready(),
            "token_budget": self.token_budget,
            "tokens_used": self.tokens_used,
            "tokens_remaining": self.tokens_remaining(),
            "completion_percent": self.completion_percent(),
        }
