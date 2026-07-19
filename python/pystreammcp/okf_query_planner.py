"""OKF-native query planner for PyStreamMCP.

Generates optimized query plans by reading system metadata from OKF catalog.
"""

from typing import Any, Dict, List, Optional

from .okf_core import OKFCatalog, OKFDocType


class QueryPlanStep:
    """Represents a single step in a query plan."""

    def __init__(self, system_name: str, tool_name: str, cost: float,
                 latency_ms: int = 0, token_cost: int = 0,
                 okf_ref: Optional[str] = None):
        """Initialize query plan step.

        Args:
            system_name: Name of the MCP system
            tool_name: Name of the tool to call
            cost: Cost of this operation
            latency_ms: Expected latency in milliseconds
            token_cost: Estimated token cost
            okf_ref: Reference to OKF document
        """
        self.system_name = system_name
        self.tool_name = tool_name
        self.cost = cost
        self.latency_ms = latency_ms
        self.token_cost = token_cost
        self.okf_ref = okf_ref

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "system": self.system_name,
            "tool": self.tool_name,
            "cost": self.cost,
            "latency_ms": self.latency_ms,
            "token_cost": self.token_cost,
            "okf_reference": self.okf_ref,
        }


class QueryPlan:
    """Optimized query plan generated from OKF catalog."""

    def __init__(self, objective: str, steps: List[QueryPlanStep]):
        """Initialize query plan.

        Args:
            objective: What this plan aims to achieve
            steps: List of query plan steps
        """
        self.objective = objective
        self.steps = steps

    @property
    def total_cost(self) -> float:
        """Calculate total cost of plan."""
        return sum(step.cost for step in self.steps)

    @property
    def total_latency_ms(self) -> int:
        """Calculate total latency of plan."""
        return sum(step.latency_ms for step in self.steps)

    @property
    def total_token_cost(self) -> int:
        """Calculate total token cost of plan."""
        return sum(step.token_cost for step in self.steps)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "objective": self.objective,
            "total_cost": self.total_cost,
            "total_latency_ms": self.total_latency_ms,
            "total_token_cost": self.total_token_cost,
            "steps": [step.to_dict() for step in self.steps],
        }


class OKFQueryPlanner:
    """Query planner that reads OKF catalog to optimize plans."""

    def __init__(self, catalog: OKFCatalog):
        """Initialize planner with OKF catalog.

        Args:
            catalog: OKFCatalog instance
        """
        self.catalog = catalog

    def generate_plan(self, objective: str, system_constraint: Optional[str] = None,
                     max_cost: Optional[float] = None) -> QueryPlan:
        """Generate optimized query plan from OKF catalog.

        Args:
            objective: What the agent wants to achieve
            system_constraint: Optional specific system to use
            max_cost: Optional maximum budget

        Returns:
            Optimized QueryPlan
        """
        # Find relevant systems
        if system_constraint:
            systems = self.catalog.search_systems(system_constraint)
        else:
            # Search for systems matching objective keywords
            systems = self.catalog.search_systems(objective)

        if not systems:
            # Fall back to all systems
            systems = self.catalog.search_systems("*")

        steps = []

        # For each relevant system, find tools and build steps
        for system_doc in systems[:3]:  # Limit to first 3 systems for complexity
            tools = self._find_tools_for_system(system_doc)

            for tool_doc in tools[:5]:  # Limit to first 5 tools per system
                cost = tool_doc.get_metadata("cost", 0.01)
                latency = tool_doc.get_metadata("latency_p95_ms", 100)
                token_cost = tool_doc.get_metadata("token_cost", 1000)

                step = QueryPlanStep(
                    system_name=system_doc.title,
                    tool_name=tool_doc.title,
                    cost=cost,
                    latency_ms=latency,
                    token_cost=token_cost,
                    okf_ref=str(tool_doc.path)
                )

                # Only add if within budget
                if max_cost is None or (sum(s.cost for s in steps) + cost) <= max_cost:
                    steps.append(step)

        # Sort by cost efficiency
        steps.sort(key=lambda s: s.cost)

        return QueryPlan(objective=objective, steps=steps)

    def _find_tools_for_system(self, system_doc) -> list:
        """Find tools available in a system.

        Args:
            system_doc: OKFDocument representing an MCP system

        Returns:
            List of tool OKFDocuments
        """
        # Search tools that reference this system
        all_tools = self.catalog.search_tools()
        system_name = system_doc.title

        matching_tools = []
        for tool in all_tools:
            # Check if tool references this system
            if system_name.lower() in tool.content.lower():
                matching_tools.append(tool)

        return matching_tools

    def find_cheapest_path(self, objective: str) -> QueryPlan:
        """Find lowest-cost query path to achieve objective.

        Args:
            objective: What to achieve

        Returns:
            Minimum-cost QueryPlan
        """
        plan = self.generate_plan(objective)

        # Sort by cost, keep only essential steps
        essential_steps = []
        total_cost = 0

        for step in sorted(plan.steps, key=lambda s: s.cost):
            essential_steps.append(step)
            total_cost += step.cost

            # Stop at reasonable cost threshold
            if total_cost > 0.10:  # $0.10 max
                break

        return QueryPlan(objective=objective, steps=essential_steps)

    def find_fastest_path(self, objective: str) -> QueryPlan:
        """Find lowest-latency query path to achieve objective.

        Args:
            objective: What to achieve

        Returns:
            Minimum-latency QueryPlan
        """
        plan = self.generate_plan(objective)

        # Sort by latency
        sorted_steps = sorted(plan.steps, key=lambda s: s.latency_ms)

        # Keep only fast steps
        fast_steps = [s for s in sorted_steps if s.latency_ms < 200]

        if not fast_steps:
            # If no fast steps available, use the fastest available
            fast_steps = sorted_steps[:3]

        return QueryPlan(objective=objective, steps=fast_steps)

    def find_optimal_path(self, objective: str, cost_weight: float = 0.5,
                         latency_weight: float = 0.3,
                         relevance_weight: float = 0.2) -> QueryPlan:
        """Find balanced optimal path considering multiple factors.

        Args:
            objective: What to achieve
            cost_weight: Weight for cost optimization (0-1)
            latency_weight: Weight for latency optimization (0-1)
            relevance_weight: Weight for relevance to objective (0-1)

        Returns:
            Balanced-optimized QueryPlan
        """
        plan = self.generate_plan(objective)

        # Normalize steps by metrics
        if not plan.steps:
            return plan

        max_cost = max(s.cost for s in plan.steps) if plan.steps else 1
        max_latency = max(s.latency_ms for s in plan.steps) if plan.steps else 1

        # Calculate scores
        scored_steps = []
        for step in plan.steps:
            cost_score = 1 - (step.cost / max_cost) if max_cost > 0 else 1
            latency_score = 1 - (step.latency_ms / max_latency) if max_latency > 0 else 1
            relevance_score = 0.8  # Default relevance

            combined_score = (
                cost_score * cost_weight +
                latency_score * latency_weight +
                relevance_score * relevance_weight
            )

            scored_steps.append((step, combined_score))

        # Sort by combined score
        scored_steps.sort(key=lambda x: x[1], reverse=True)

        # Keep top 5 steps
        optimized_steps = [step for step, _ in scored_steps[:5]]

        return QueryPlan(objective=objective, steps=optimized_steps)
