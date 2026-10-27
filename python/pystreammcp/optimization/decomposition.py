"""Query Decomposition for Advanced Optimization.

Breaks down complex queries into simpler sub-queries
for better optimization and parallel execution.
"""

import re
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum


class QueryType(str, Enum):
    """Query type classification."""

    SIMPLE = "simple"  # Single table, basic filters
    JOINED = "joined"  # Multiple tables with joins
    AGGREGATED = "aggregated"  # GROUP BY, aggregations
    COMPLEX = "complex"  # Subqueries, CTEs
    HYBRID = "hybrid"  # Mix of above


@dataclass
class SubQuery:
    """Decomposed sub-query."""

    id: str
    query_text: str
    depends_on: List[str]  # Sub-query IDs this depends on
    estimated_tokens: int
    parallelizable: bool
    priority: int = 0  # Execution priority


@dataclass
class DecompositionPlan:
    """Plan for query decomposition."""

    original_query: str
    query_type: QueryType
    sub_queries: List[SubQuery]
    execution_graph: Dict[str, List[str]]  # ID -> dependencies
    estimated_total_tokens: int
    estimated_reduction: float  # Percentage


class QueryDecomposer:
    """Decomposes complex queries for optimization.

    Breaks large queries into smaller, optimizable pieces
    that can be executed in parallel and cached independently.
    """

    def __init__(self):
        """Initialize query decomposer."""
        self.cache: Dict[str, DecompositionPlan] = {}

    def analyze_query(self, query_text: str) -> QueryType:
        """Analyze query to determine type.

        Args:
            query_text: SQL query text

        Returns:
            Query type
        """
        query_lower = query_text.lower()

        # Simple heuristics (in production, use SQL parser)
        if "join" in query_lower:
            return QueryType.JOINED
        elif "group by" in query_lower or "count(" in query_lower:
            return QueryType.AGGREGATED
        elif (
            "with " in query_lower
            or "select" in query_lower
            and query_lower.count("select") > 1
        ):
            return QueryType.COMPLEX
        else:
            return QueryType.SIMPLE

    def decompose(self, query_text: str) -> DecompositionPlan:
        """Decompose a query into sub-queries.

        Args:
            query_text: Query to decompose

        Returns:
            Decomposition plan
        """
        query_type = self.analyze_query(query_text)

        if query_type == QueryType.SIMPLE:
            return self._decompose_simple(query_text)
        elif query_type == QueryType.JOINED:
            return self._decompose_joined(query_text)
        elif query_type == QueryType.AGGREGATED:
            return self._decompose_aggregated(query_text)
        else:
            return self._decompose_complex(query_text)

    @staticmethod
    def _estimate_tokens(query_text: str) -> int:
        """Character-based token estimate, floored at one."""
        return max(1, len(query_text) // 4)

    @classmethod
    def _extract_tables(cls, query_text: str) -> List[str]:
        """Extract physical table names following FROM/JOIN.

        This is intentionally a small lexical helper, not a SQL parser. It
        ignores subqueries (``FROM (``) and returns each table once.
        """
        pattern = re.compile(
            r"\b(?:from|join)\s+([`\"\[]?[A-Za-z_][\w.]*[`\"\]]?)",
            re.IGNORECASE,
        )
        tables: List[str] = []
        for match in pattern.finditer(query_text):
            table = match.group(1).strip("`\"[]")
            if table and table not in tables:
                tables.append(table)
        return tables

    def _single_query_plan(
        self, query_text: str, query_type: QueryType
    ) -> DecompositionPlan:
        """Return an honest one-step plan (no measurable reduction claimed)."""
        sub_query = SubQuery(
            id="q1",
            query_text=query_text,
            depends_on=[],
            estimated_tokens=self._estimate_tokens(query_text),
            parallelizable=False,
        )
        return DecompositionPlan(
            original_query=query_text,
            query_type=query_type,
            sub_queries=[sub_query],
            execution_graph={"q1": []},
            estimated_total_tokens=sub_query.estimated_tokens,
            estimated_reduction=0.0,
        )

    def _decompose_simple(self, query_text: str) -> DecompositionPlan:
        """Simple queries are already a single step."""
        return self._single_query_plan(query_text, QueryType.SIMPLE)

    def _decompose_joined(self, query_text: str) -> DecompositionPlan:
        """Split a join into real table fetches plus the original join query."""
        tables = self._extract_tables(query_text)
        if len(tables) < 2:
            return self._single_query_plan(query_text, QueryType.JOINED)

        fetch_queries = []
        for index, table in enumerate(tables, start=1):
            fetch_text = f"SELECT * FROM {table}"
            fetch_queries.append(
                SubQuery(
                    id=f"q{index}_fetch",
                    query_text=fetch_text,
                    depends_on=[],
                    estimated_tokens=self._estimate_tokens(fetch_text),
                    parallelizable=True,
                    priority=1,
                )
            )

        fetch_ids = [sub.id for sub in fetch_queries]
        join_query = SubQuery(
            id=f"q{len(fetch_queries) + 1}_join",
            query_text=query_text,
            depends_on=fetch_ids,
            estimated_tokens=self._estimate_tokens(query_text),
            parallelizable=False,
            priority=2,
        )
        sub_queries = [*fetch_queries, join_query]

        return DecompositionPlan(
            original_query=query_text,
            query_type=QueryType.JOINED,
            sub_queries=sub_queries,
            execution_graph={sub.id: list(sub.depends_on) for sub in sub_queries},
            estimated_total_tokens=sum(
                sub.estimated_tokens for sub in sub_queries
            ),
            estimated_reduction=0.0,
        )

    def _decompose_aggregated(self, query_text: str) -> DecompositionPlan:
        """Aggregations cannot be safely split without a SQL parser."""
        return self._single_query_plan(query_text, QueryType.AGGREGATED)

    def _decompose_complex(self, query_text: str) -> DecompositionPlan:
        """CTE/subquery rewrites require a real SQL parser; stay one-step."""
        return self._single_query_plan(query_text, QueryType.COMPLEX)

    def get_execution_order(self, plan: DecompositionPlan) -> List[str]:
        """Get optimal execution order for sub-queries.

        Args:
            plan: Decomposition plan

        Returns:
            Ordered list of sub-query IDs
        """
        executed = set()
        order = []

        while len(executed) < len(plan.sub_queries):
            for sq in plan.sub_queries:
                if sq.id not in executed and all(d in executed for d in sq.depends_on):
                    order.append(sq.id)
                    executed.add(sq.id)

        return order

    def estimate_speedup(self, plan: DecompositionPlan) -> float:
        """Estimate speedup from parallelization.

        Args:
            plan: Decomposition plan

        Returns:
            Estimated speedup factor
        """
        parallelizable = [sq for sq in plan.sub_queries if sq.parallelizable]
        speedup = 1.0 + (len(parallelizable) * 0.3)  # 30% per parallelizable query
        return min(3.5, speedup)  # Cap at 3.5x
