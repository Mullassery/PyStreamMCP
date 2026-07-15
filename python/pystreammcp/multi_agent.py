"""Multi-agent context sharing and collaboration for PyStreamMCP."""

from typing import Dict, List, Optional
from dataclasses import dataclass
from .context import Context


@dataclass
class SharedContext:
    """Context shared between multiple agents."""

    context_id: str
    original_query: str
    optimized_context: Context
    usage_count: int
    agents_using: List[str]
    created_at: str
    cost_savings: float

    def add_agent(self, agent_id: str) -> None:
        """Add an agent using this context."""
        if agent_id not in self.agents_using:
            self.agents_using.append(agent_id)
        self.usage_count += 1

    def reuse_factor(self) -> float:
        """Calculate how well this context is being reused."""
        return self.usage_count / max(len(self.agents_using), 1)


class ContextHub:
    """Central hub for multi-agent context sharing."""

    def __init__(self):
        """Initialize context hub."""
        self.shared_contexts: Dict[str, SharedContext] = {}
        self.agent_collaborations: Dict[str, List[str]] = {}

    def register_context(
        self, context_id: str, query: str, context: Context, cost_savings: float = 0.0
    ) -> str:
        """Register a context for sharing."""
        shared = SharedContext(
            context_id=context_id,
            original_query=query,
            optimized_context=context,
            usage_count=1,
            agents_using=[],
            created_at=__import__("datetime").datetime.utcnow().isoformat(),
            cost_savings=cost_savings,
        )
        self.shared_contexts[context_id] = shared
        return context_id

    def query_shared_contexts(self, query: str, limit: int = 10) -> List[SharedContext]:
        """Find shared contexts relevant to a query."""
        query_lower = query.lower()
        results = [
            ctx
            for ctx in self.shared_contexts.values()
            if query_lower in ctx.original_query.lower()
        ]

        results.sort(key=lambda x: (-x.usage_count, -x.cost_savings))
        return results[:limit]

    def update_usage(self, context_id: str, agent_id: str) -> None:
        """Record an agent using a shared context."""
        if context_id in self.shared_contexts:
            ctx = self.shared_contexts[context_id]
            ctx.add_agent(agent_id)

            if agent_id not in self.agent_collaborations:
                self.agent_collaborations[agent_id] = []
            if context_id not in self.agent_collaborations[agent_id]:
                self.agent_collaborations[agent_id].append(context_id)

    def get_context(self, context_id: str) -> Optional[SharedContext]:
        """Get a specific shared context."""
        return self.shared_contexts.get(context_id)

    def agent_collaboration_score(self, agent_id: str) -> float:
        """Score how well an agent collaborates (context reuse)."""
        if agent_id not in self.agent_collaborations:
            return 0.0

        contexts = self.agent_collaborations[agent_id]
        if not contexts:
            return 0.0

        total_reuse = sum(
            self.shared_contexts[ctx_id].reuse_factor()
            for ctx_id in contexts
            if ctx_id in self.shared_contexts
        )
        return total_reuse / len(contexts)

    def collaboration_savings(self) -> float:
        """Calculate total cost savings from multi-agent collaboration."""
        return sum(
            ctx.cost_savings * ctx.usage_count
            for ctx in self.shared_contexts.values()
        )

    def context_count(self) -> int:
        """Get number of shared contexts."""
        return len(self.shared_contexts)

    def agent_count(self) -> int:
        """Get number of collaborating agents."""
        return len(self.agent_collaborations)

    def get_top_agents(self, limit: int = 10) -> List[tuple[str, float]]:
        """Get agents ranked by collaboration score."""
        scores = [
            (agent_id, self.agent_collaboration_score(agent_id))
            for agent_id in self.agent_collaborations.keys()
        ]
        scores.sort(key=lambda x: -x[1])
        return scores[:limit]

    def context_reuse_summary(self) -> Dict[str, float]:
        """Get summary of context reuse patterns."""
        return {
            "total_contexts": self.context_count(),
            "total_agents": self.agent_count(),
            "collaboration_savings": self.collaboration_savings(),
            "avg_reuse_per_context": (
                sum(ctx.reuse_factor() for ctx in self.shared_contexts.values())
                / max(len(self.shared_contexts), 1)
            ),
        }
