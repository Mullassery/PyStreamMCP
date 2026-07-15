"""
Langchain integration example with PyStreamMCP.

Shows how to use PyStreamMCP with Langchain agents for
optimized query execution.
"""

from pystreammcp.integrations.langchain import (
    PyStreamMCPTool,
    create_pystreammcp_agent,
)


def example_pystreammcp_tool():
    """Example using PyStreamMCPTool directly."""
    print("=" * 60)
    print("Example 1: Direct PyStreamMCPTool Usage")
    print("=" * 60)

    # Create tool
    tool = PyStreamMCPTool(
        agent_id="customer_analyst",
        optimization_strategy="token_efficient",
        max_tokens=1500,
    )

    # Execute queries
    queries = [
        ("What are the top 10 customers by LTV?", "retrieve"),
        ("Which segments have high churn risk?", "discover"),
        ("What's the average MRR per segment?", "aggregate"),
    ]

    for query_text, intent in queries:
        print(f"\nQuery: {query_text}")
        print(f"Intent: {intent}")

        result = tool(query_text, intent=intent)

        print(f"  Baseline tokens: {result['baseline_tokens']}")
        print(f"  Optimized tokens: {result['optimized_tokens']}")
        print(f"  Reduction: {result['cost_reduction_percent']:.1f}%")
        print(f"  Meets target: {result['meets_target']}")
        print(f"  Cost saved: ${result['estimated_cost_saved']:.4f}")

    # Show metrics
    print("\n" + "=" * 60)
    print("Tool Metrics")
    print("=" * 60)
    metrics = tool.get_metrics()
    print(f"Queries executed: {metrics['queries_executed']}")
    print(f"Total cost saved: ${metrics['total_cost_saved']:.4f}")
    print(f"Average reduction: {metrics['average_cost_reduction']:.1f}%")


def example_with_mock_llm():
    """Example with mock LLM (requires langchain to be installed)."""
    print("\n" + "=" * 60)
    print("Example 2: With Langchain Agent (Mocked LLM)")
    print("=" * 60)

    try:
        from langchain.llms.fake import FakeListLLM

        # Create mock LLM
        responses = [
            "The top customers are: Customer A ($50K LTV), Customer B ($45K LTV)",
            "High churn risk segments: Price-sensitive, Low engagement",
            "Average MRR by segment: Premium $5000, Standard $2000",
        ]
        llm = FakeListLLM(responses=responses)

        # Create agent with PyStreamMCP
        agent = create_pystreammcp_agent(
            llm,
            agent_id="recommendation_engine",
            max_tokens=2000,
            optimization_strategy="token_efficient",
            verbose=True,
        )

        print("Agent created successfully!")
        print(f"Agent tools: {[tool.name for tool in agent.tools]}")

        # Note: Actual agent.run() requires real LLM setup
        # This is just to show the structure

    except ImportError:
        print(
            "Langchain not installed. "
            "Install with: pip install langchain"
        )


def example_retrieval_workflow():
    """Example of retrieval workflow."""
    print("\n" + "=" * 60)
    print("Example 3: Retrieval Workflow")
    print("=" * 60)

    tool = PyStreamMCPTool(
        agent_id="retrieval_agent",
        optimization_strategy="balanced",
        max_tokens=1000,
    )

    # Simulate retrieval workflow
    queries = [
        "What data sources contain customer LTV information?",
        "Find the most recent customer segment definitions",
        "Retrieve churn prediction model features",
    ]

    results = []
    for query in queries:
        result = tool(query, intent="discover")
        results.append(result)
        print(f"\nQuery: {query}")
        print(f"  Status: {'✓' if result['meets_target'] else '✗'} "
              f"({result['cost_reduction_percent']:.1f}% reduction)")

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    successful = sum(1 for r in results if r["meets_target"])
    print(f"Successful optimizations: {successful}/{len(results)}")
    total_saved = sum(r["estimated_cost_saved"] for r in results)
    print(f"Total estimated cost saved: ${total_saved:.4f}")


if __name__ == "__main__":
    # Run examples
    example_pystreammcp_tool()
    example_with_mock_llm()
    example_retrieval_workflow()

    print("\n" + "=" * 60)
    print("✓ Langchain integration examples complete!")
    print("=" * 60)
