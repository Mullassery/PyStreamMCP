"""Advanced Optimization: Streaming Contexts & Multi-Agent Sharing.

Streaming context windows (<50ms latency) and shared context
across multiple agents.
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict


@dataclass
class StreamingContext:
    """Streaming context window for real-time optimization."""

    context_id: str
    agent_id: str
    query_text: str
    chunks: List[Dict[str, Any]] = field(default_factory=list)
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    total_tokens: int = 0
    streamed_tokens: int = 0
    chunk_count: int = 0


@dataclass
class SharedContext:
    """Context shared across multiple agents."""

    context_id: str
    source_agent_id: str
    shared_with: List[str] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    ttl_seconds: int = 300  # 5 minute TTL
    reuse_count: int = 0
    savings: float = 0.0  # tokens saved


class StreamingContextWindow:
    """Manages streaming context windows with <50ms latency target.

    Streams results incrementally to agents instead of waiting
    for complete result set.
    """

    def __init__(self, chunk_size: int = 100, chunk_delay_ms: float = 10.0):
        """Initialize streaming context.

        Args:
            chunk_size: Number of tokens per chunk
            chunk_delay_ms: Delay between chunks (ms)
        """
        self.chunk_size = chunk_size
        self.chunk_delay_ms = chunk_delay_ms
        self.active_streams: Dict[str, StreamingContext] = {}
        self.chunk_callbacks: Dict[str, Callable] = {}

    def create_stream(self, context_id: str, agent_id: str, query_text: str) -> str:
        """Create a streaming context.

        Args:
            context_id: Unique context ID
            agent_id: Agent receiving the stream
            query_text: Original query

        Returns:
            Stream ID
        """
        stream = StreamingContext(
            context_id=context_id,
            agent_id=agent_id,
            query_text=query_text,
        )

        self.active_streams[context_id] = stream
        return context_id

    def stream_chunk(self, context_id: str, chunk_data: Dict[str, Any]) -> None:
        """Stream a chunk of data.

        Args:
            context_id: Context ID
            chunk_data: Data chunk
        """
        if context_id not in self.active_streams:
            return

        stream = self.active_streams[context_id]
        stream.chunks.append(chunk_data)
        stream.chunk_count += 1

        # Update tokens
        tokens = chunk_data.get("tokens", 0)
        stream.streamed_tokens += tokens

        # Invoke callback if registered
        if context_id in self.chunk_callbacks:
            self.chunk_callbacks[context_id](chunk_data)

    def get_stream_stats(self, context_id: str) -> Dict[str, Any]:
        """Get streaming statistics.

        Args:
            context_id: Context ID

        Returns:
            Stream statistics
        """
        if context_id not in self.active_streams:
            return {}

        stream = self.active_streams[context_id]

        return {
            "context_id": context_id,
            "agent_id": stream.agent_id,
            "chunk_count": stream.chunk_count,
            "streamed_tokens": stream.streamed_tokens,
            "chunks_received": len(stream.chunks),
        }

    def close_stream(self, context_id: str) -> Dict[str, Any]:
        """Close a streaming context.

        Args:
            context_id: Context ID

        Returns:
            Final statistics
        """
        if context_id not in self.active_streams:
            return {}

        stream = self.active_streams.pop(context_id)

        # Remove callback
        if context_id in self.chunk_callbacks:
            del self.chunk_callbacks[context_id]

        return {
            "context_id": context_id,
            "total_chunks": stream.chunk_count,
            "total_tokens": stream.streamed_tokens,
        }


class MultiAgentContextSharing:
    """Manages context sharing across multiple agents.

    Allows agents to reuse computed contexts, reducing redundant
    computation and improving collective token efficiency.
    """

    def __init__(self):
        """Initialize multi-agent context manager."""
        self.shared_contexts: Dict[str, SharedContext] = {}
        self.agent_contexts: Dict[str, List[str]] = defaultdict(list)

    def create_shared_context(
        self,
        context_id: str,
        source_agent_id: str,
        data: Dict[str, Any],
        ttl_seconds: int = 300,
    ) -> str:
        """Create a shareable context.

        Args:
            context_id: Unique context ID
            source_agent_id: Agent creating the context
            data: Context data
            ttl_seconds: Time to live

        Returns:
            Shared context ID
        """
        context = SharedContext(
            context_id=context_id,
            source_agent_id=source_agent_id,
            data=data,
            ttl_seconds=ttl_seconds,
        )

        self.shared_contexts[context_id] = context
        self.agent_contexts[source_agent_id].append(context_id)

        return context_id

    def request_context(self, source_context_id: str, requesting_agent_id: str) -> Optional[Dict[str, Any]]:
        """Request a shared context.

        Args:
            source_context_id: Context to request
            requesting_agent_id: Agent requesting

        Returns:
            Context data if available, None otherwise
        """
        if source_context_id not in self.shared_contexts:
            return None

        context = self.shared_contexts[source_context_id]

        # Check TTL
        created = datetime.fromisoformat(context.created_at)
        elapsed = (datetime.now() - created).total_seconds()

        if elapsed > context.ttl_seconds:
            del self.shared_contexts[source_context_id]
            return None

        # Update reuse stats
        context.shared_with.append(requesting_agent_id)
        context.reuse_count += 1

        # Calculate savings (estimated tokens that don't need to be recomputed)
        context.savings += 50.0  # Conservative estimate

        return context.data

    def get_context_reuse_stats(self) -> Dict[str, Any]:
        """Get context reuse statistics.

        Returns:
            Reuse statistics
        """
        total_contexts = len(self.shared_contexts)
        total_reuses = sum(c.reuse_count for c in self.shared_contexts.values())
        total_savings = sum(c.savings for c in self.shared_contexts.values())

        return {
            "total_shared_contexts": total_contexts,
            "total_reuses": total_reuses,
            "total_tokens_saved": total_savings,
            "avg_reuses_per_context": total_reuses / total_contexts if total_contexts > 0 else 0,
            "collective_savings_percent": 20.0 * min(1.0, total_reuses / 10),  # Up to 20% savings
        }

    def cleanup_expired(self) -> int:
        """Clean up expired contexts.

        Returns:
            Number of contexts removed
        """
        now = datetime.now()
        expired = []

        for context_id, context in self.shared_contexts.items():
            created = datetime.fromisoformat(context.created_at)
            elapsed = (now - created).total_seconds()

            if elapsed > context.ttl_seconds:
                expired.append(context_id)

        for context_id in expired:
            del self.shared_contexts[context_id]

        return len(expired)


class CostOptimizationEngine:
    """Optimizes cost through streaming and sharing.

    Combines streaming context windows and multi-agent sharing
    for maximum efficiency.
    """

    def __init__(self):
        """Initialize optimization engine."""
        self.streaming = StreamingContextWindow()
        self.sharing = MultiAgentContextSharing()
        self.optimization_history: List[Dict[str, Any]] = []

    def optimize_multi_agent_query(
        self,
        agents: List[str],
        query_text: str,
    ) -> Dict[str, Any]:
        """Optimize query execution for multiple agents.

        Args:
            agents: List of agent IDs
            query_text: Query to execute

        Returns:
            Optimization plan
        """
        plan = {
            "agents": agents,
            "query": query_text,
            "strategies": [],
            "estimated_savings_percent": 0.0,
        }

        if len(agents) == 1:
            # Single agent: use streaming
            plan["strategies"].append({
                "type": "streaming",
                "target_agents": agents,
                "latency_target_ms": 50,
                "estimated_savings": 5,
            })
            plan["estimated_savings_percent"] = 5.0

        elif len(agents) > 1:
            # Multiple agents: use sharing + streaming
            plan["strategies"].append({
                "type": "shared_context",
                "source_agent": agents[0],
                "target_agents": agents[1:],
                "reuse_count": len(agents) - 1,
                "estimated_savings": 15 * (len(agents) - 1),
            })

            plan["strategies"].append({
                "type": "streaming",
                "target_agents": agents,
                "latency_target_ms": 50,
                "estimated_savings": 5,
            })

            plan["estimated_savings_percent"] = 15.0 + (5.0 * len(agents))

        self.optimization_history.append(plan)
        return plan

    def estimate_speedup(self, agent_count: int, sharing_enabled: bool = True) -> float:
        """Estimate speedup from optimization.

        Args:
            agent_count: Number of agents
            sharing_enabled: Whether sharing is enabled

        Returns:
            Speedup factor
        """
        base_speedup = 1.0

        if sharing_enabled and agent_count > 1:
            base_speedup += 0.3 * (agent_count - 1)  # 30% per additional agent

        # Add streaming benefit
        base_speedup += 0.1

        return min(2.5, base_speedup)  # Cap at 2.5x
