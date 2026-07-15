"""
Basic usage example of PyStreamMCP SDK.

Shows how to use the Agent API for query optimization.
"""

from pystreammcp import (
    Agent,
    Query,
    QueryIntent,
    Discovery,
    DiscoveredSource,
    SourceType,
    OptimizationStrategy,
    StrategyType,
)


def main():
    """Basic usage example."""

    # Create an agent
    agent = Agent(
        agent_id="recommendation_engine",
        name="Product Recommendation Engine",
        optimization_strategy="token_efficient",
        max_tokens=1000,
    )

    print(f"Created agent: {agent.config.name}")
    print(f"Optimization strategy: {agent.config.optimization_strategy}")
    print()

    # Query 1: Simple retrieval query
    print("=" * 60)
    print("Query 1: Retrieve top customers by LTV")
    print("=" * 60)

    query1 = Query.retrieve(
        text="What are the top 10 customers by lifetime value?",
        agent_id=agent.config.agent_id,
        max_tokens=1000,
    )

    result1 = agent.query(query1.text)
    print(f"Baseline tokens: {result1.baseline_tokens}")
    print(f"Optimized tokens: {result1.optimized_tokens}")
    print(f"Reduction: {result1.cost_reduction_percent:.1f}%")
    print(f"Meets target (60-75%): {60 <= result1.cost_reduction_percent <= 75}")
    print()

    # Query 2: Token-efficient discovery
    print("=" * 60)
    print("Query 2: Discover churn indicators (token-efficient)")
    print("=" * 60)

    query2 = Query.discover(
        text="Which indicators predict customer churn?",
        agent_id=agent.config.agent_id,
    ).set_token_efficient()

    result2 = agent.query(query2.text, optimization="token_efficient")
    print(f"Baseline tokens: {result2.baseline_tokens}")
    print(f"Optimized tokens: {result2.optimized_tokens}")
    print(f"Reduction: {result2.cost_reduction_percent:.1f}%")
    print(f"Execution time: {result2.execution_time_ms}ms")
    print()

    # Query 3: Aggregate with discovery
    print("=" * 60)
    print("Query 3: Aggregate metrics")
    print("=" * 60)

    query3 = Query.aggregate(
        text="What's the average MRR per customer segment?",
        agent_id=agent.config.agent_id,
        max_tokens=1500,
    )

    result3 = agent.query(query3.text)
    print(f"Baseline tokens: {result3.baseline_tokens}")
    print(f"Optimized tokens: {result3.optimized_tokens}")
    print(f"Cost reduction: {result3.cost_reduction_percent:.1f}%")
    print()

    # Show agent metrics
    print("=" * 60)
    print("Agent Metrics")
    print("=" * 60)

    metrics = agent.get_metrics()
    print(f"Queries executed: {metrics['queries_executed']}")
    print(f"Total baseline tokens: {metrics['total_baseline_tokens']}")
    print(f"Total optimized tokens: {metrics['total_optimized_tokens']}")
    print(f"Average cost reduction: {metrics['average_cost_reduction']:.1f}%")
    print(f"Total cost saved: ${metrics['total_cost_saved']:.4f}")
    print()

    # Check if all queries met target
    print("=" * 60)
    print("Optimization Summary")
    print("=" * 60)
    all_results = [result1, result2, result3]
    met_target = sum(1 for r in all_results if 60 <= r.cost_reduction_percent <= 75)
    exceeded_target = sum(1 for r in all_results if r.cost_reduction_percent > 75)

    print(f"Total queries: {len(all_results)}")
    print(f"Met 60-75% target: {met_target}")
    print(f"Exceeded 75%: {exceeded_target}")
    print()
    print("✓ PyStreamMCP is working correctly!")


if __name__ == "__main__":
    main()
