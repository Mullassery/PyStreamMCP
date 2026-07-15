"""Complex query decomposition for multi-step reasoning in PyStreamMCP."""

from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class QueryStep:
    """A single step in a decomposed query."""

    step_id: int
    sub_query: str
    required_sources: List[str]
    optimization_strategy: str
    estimated_tokens: int


@dataclass
class DecomposedQuery:
    """A complex query decomposed into steps."""

    query_id: str
    original_query: str
    steps: List[QueryStep]
    dependencies: List[Tuple[int, int]]
    parallelizable_steps: List[int]
    estimated_total_tokens: int
    complexity_score: float

    def step_count(self) -> int:
        """Get number of steps."""
        return len(self.steps)

    def is_complex(self) -> bool:
        """Check if this is a complex multi-step query."""
        return self.step_count() > 1

    def can_parallelize(self) -> bool:
        """Check if any steps can run in parallel."""
        return len(self.parallelizable_steps) > 0


@dataclass
class ExecutionPlan:
    """Optimized execution plan for a decomposed query."""

    plan_id: str
    stages: List[List[int]]
    sequential_order: List[int]
    estimated_latency_ms: int
    optimized: bool

    def stage_count(self) -> int:
        """Get number of execution stages."""
        return len(self.stages)

    def is_parallelizable(self) -> bool:
        """Check if execution can be parallelized."""
        return any(len(stage) > 1 for stage in self.stages)


class QueryDecomposer:
    """Decomposes complex queries into executable steps."""

    @staticmethod
    def decompose(query: str) -> DecomposedQuery:
        """Decompose a query into steps."""
        # Detect multi-step queries by keywords
        keywords = ["then", "after", "next", "combine", "also", "which"]
        query_lower = query.lower()

        keyword_count = sum(1 for kw in keywords if kw in query_lower)
        step_count = 1 if keyword_count == 0 else keyword_count + 1

        steps = []

        if step_count == 1:
            # Single-step query
            steps.append(
                QueryStep(
                    step_id=0,
                    sub_query=query,
                    required_sources=QueryDecomposer._extract_sources(query),
                    optimization_strategy="balanced",
                    estimated_tokens=QueryDecomposer._estimate_tokens(query),
                )
            )
        else:
            # Multi-step query decomposition
            parts = QueryDecomposer._split_query(query, step_count)
            for i, part in enumerate(parts):
                steps.append(
                    QueryStep(
                        step_id=i,
                        sub_query=part,
                        required_sources=QueryDecomposer._extract_sources(part),
                        optimization_strategy=QueryDecomposer._choose_strategy(part),
                        estimated_tokens=QueryDecomposer._estimate_tokens(part),
                    )
                )

        # Find parallelizable steps
        parallelizable = [
            i for i in range(len(steps))
            if not any(dep_to == i or dep_from == i for dep_from, dep_to in [])
        ]

        total_tokens = sum(step.estimated_tokens for step in steps)
        complexity = QueryDecomposer._calculate_complexity(step_count)

        return DecomposedQuery(
            query_id=f"dq_{__import__('uuid').uuid4()}",
            original_query=query,
            steps=steps,
            dependencies=[],
            parallelizable_steps=parallelizable,
            estimated_total_tokens=total_tokens,
            complexity_score=complexity,
        )

    @staticmethod
    def optimize_execution_plan(decomposed: DecomposedQuery) -> ExecutionPlan:
        """Create an optimized execution plan."""
        stages = [[i] for i in range(len(decomposed.steps))]

        # Merge parallelizable steps into same stage
        if len(decomposed.parallelizable_steps) > 1:
            stages = [decomposed.parallelizable_steps] + [
                [i] for i in range(len(decomposed.steps))
                if i not in decomposed.parallelizable_steps
            ]

        sequential_order = list(range(len(decomposed.steps)))
        estimated_latency = len(stages) * 50 + decomposed.estimated_total_tokens // 100

        return ExecutionPlan(
            plan_id=f"ep_{__import__('uuid').uuid4()}",
            stages=stages,
            sequential_order=sequential_order,
            estimated_latency_ms=estimated_latency,
            optimized=len(decomposed.steps) > 1,
        )

    @staticmethod
    def _split_query(query: str, count: int) -> List[str]:
        """Split a query into parts."""
        keywords = ["then", "after", "next", "combine", "also"]
        query_lower = query.lower()

        parts = []
        last_pos = 0

        for keyword in keywords:
            if keyword in query_lower:
                pos = query_lower.find(keyword)
                if last_pos < pos:
                    parts.append(query[last_pos:pos].strip())
                last_pos = pos + len(keyword)

        if last_pos < len(query):
            parts.append(query[last_pos:].strip())

        while len(parts) < count:
            parts.append(query)

        return parts[:count]

    @staticmethod
    def _extract_sources(query: str) -> List[str]:
        """Extract data sources from query."""
        keywords = ["customer", "order", "product", "revenue", "segment", "metric", "data"]
        return [kw for kw in keywords if kw in query.lower()]

    @staticmethod
    def _choose_strategy(query: str) -> str:
        """Choose optimization strategy for a query step."""
        query_lower = query.lower()
        if "top" in query_lower or "rank" in query_lower:
            return "quality_first"
        elif "aggregate" in query_lower or "sum" in query_lower:
            return "token_efficient"
        else:
            return "balanced"

    @staticmethod
    def _estimate_tokens(query: str) -> int:
        """Estimate tokens needed for a query."""
        base = len(query) // 4
        multiplier = 2 if "detailed" in query.lower() else 1
        return max(base * multiplier, 100)

    @staticmethod
    def _calculate_complexity(step_count: int) -> float:
        """Calculate query complexity score."""
        return step_count / 5.0
