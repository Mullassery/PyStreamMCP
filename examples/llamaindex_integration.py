"""
Llamaindex integration example with PyStreamMCP.

Shows how to use PyStreamMCP with Llamaindex for
optimized retrieval and context management.
"""

from pystreammcp.integrations.llamaindex import (
    StreamMCPRetriever,
    StreamMCPQueryEngine,
    create_pystreammcp_index,
)


def example_retriever():
    """Example using StreamMCPRetriever directly."""
    print("=" * 60)
    print("Example 1: Direct StreamMCPRetriever Usage")
    print("=" * 60)

    # Create retriever
    retriever = StreamMCPRetriever(
        agent_id="document_analyzer",
        max_tokens=2000,
        optimization_strategy="token_efficient",
    )

    # Simulate queries
    queries = [
        "What are the key features of the product?",
        "How does customer segmentation work?",
        "What are the performance benchmarks?",
    ]

    print("\nExecuting retrieval queries:")
    results = []
    for query in queries:
        print(f"\nQuery: {query}")
        result = retriever.retrieve(query)

        if result:
            node = result[0]
            metadata = node.node.metadata
            print(f"  Relevance score: {node.score:.2f}")
            print(f"  Cost reduction: {metadata['cost_reduction_percent']:.1f}%")
            print(f"  Baseline tokens: {metadata['baseline_tokens']}")
            print(f"  Optimized tokens: {metadata['optimized_tokens']}")
            print(f"  Cost saved: ${metadata['estimated_cost_saved']:.4f}")
            results.append(metadata)

    return results


def example_query_engine():
    """Example using StreamMCPQueryEngine."""
    print("\n" + "=" * 60)
    print("Example 2: StreamMCPQueryEngine Usage")
    print("=" * 60)

    # Create retriever and query engine
    retriever = StreamMCPRetriever(
        agent_id="query_engine",
        max_tokens=1500,
        optimization_strategy="balanced",
    )

    engine = StreamMCPQueryEngine(retriever=retriever)

    # Execute queries
    queries = [
        "Compare our performance to industry benchmarks",
        "What is the customer satisfaction trend?",
        "Which features have the highest adoption?",
    ]

    print("\nExecuting query engine queries:")
    for query in queries:
        print(f"\nQuery: {query}")
        result = engine.query(query)

        metadata = result["metadata"]
        print(f"  Response: {result['response']}")
        print(f"  Cost reduction: {metadata['cost_reduction_percent']:.1f}%")
        print(f"  Execution time: {metadata['execution_time_ms']}ms")
        print(f"  Cost saved: ${metadata['estimated_cost_saved']:.4f}")


def example_index_creation():
    """Example of creating an index with PyStreamMCP optimization."""
    print("\n" + "=" * 60)
    print("Example 3: Creating Optimized Index")
    print("=" * 60)

    # Create index (without documents for this example)
    retriever = create_pystreammcp_index(
        agent_id="document_index",
        max_tokens=2000,
        optimization_strategy="token_efficient",
    )

    print("Created PyStreamMCP-optimized index")
    print(f"Max tokens: {retriever.max_tokens}")
    print(f"Optimization strategy: {retriever.optimization_strategy}")

    # Simulate index usage
    test_queries = [
        "Find all customer complaints from Q4",
        "Search for enterprise pricing information",
        "Locate technical documentation for API",
    ]

    print("\nSimulating index queries:")
    metrics = {"total_queries": 0, "total_savings": 0.0}

    for query in test_queries:
        print(f"\nQuery: {query}")
        nodes = retriever.retrieve(query)

        if nodes:
            metadata = nodes[0].node.metadata
            print(f"  Found {len(nodes)} results")
            print(f"  Reduction: {metadata['cost_reduction_percent']:.1f}%")
            print(f"  Savings: ${metadata['estimated_cost_saved']:.4f}")
            metrics["total_queries"] += 1
            metrics["total_savings"] += metadata["estimated_cost_saved"]

    print(f"\nTotal cost saved: ${metrics['total_savings']:.4f}")


def example_with_documents():
    """Example with actual documents (requires llama-index)."""
    print("\n" + "=" * 60)
    print("Example 4: Index with Documents")
    print("=" * 60)

    try:
        from llama_index import Document

        # Create sample documents
        documents = [
            Document(text="Customer retention strategies focus on engagement"),
            Document(text="Premium tier customers have 95% retention rate"),
            Document(text="Churn prediction models use behavioral signals"),
        ]

        # Create index with PyStreamMCP
        index = create_pystreammcp_index(
            documents=documents,
            agent_id="document_index",
            max_tokens=1500,
            optimization_strategy="token_efficient",
        )

        print(f"Created index with {len(documents)} documents")
        print("Index has PyStreamMCP query engine for optimized retrieval")

        # Query the index
        if hasattr(index, "query_engine"):
            result = index.query_engine.query("What are retention strategies?")
            print(f"\nQuery result:")
            print(f"  Response: {result['response']}")
            print(f"  Cost reduction: {result['metadata']['cost_reduction_percent']:.1f}%")

    except ImportError:
        print(
            "llama-index not installed. "
            "Install with: pip install llama-index"
        )


def example_comparison():
    """Show cost savings with vs without optimization."""
    print("\n" + "=" * 60)
    print("Example 5: Cost Comparison")
    print("=" * 60)

    retriever = StreamMCPRetriever(
        agent_id="cost_analyzer",
        optimization_strategy="token_efficient",
    )

    query = "Analyze customer behavior patterns and predict churn risk"

    print(f"\nQuery: {query}")
    print("\nWithout PyStreamMCP optimization:")
    print("  Estimated tokens: 5000")
    print("  Estimated cost: $0.05")

    result = retriever.retrieve(query)
    if result:
        metadata = result[0].node.metadata
        print(f"\nWith PyStreamMCP optimization:")
        print(f"  Baseline tokens: {metadata['baseline_tokens']}")
        print(f"  Optimized tokens: {metadata['optimized_tokens']}")
        print(f"  Cost reduction: {metadata['cost_reduction_percent']:.1f}%")
        print(f"  Estimated cost: ${metadata['estimated_cost_saved']:.4f}")
        print(f"\nSavings: ${metadata['estimated_cost_saved']:.4f} "
              f"({metadata['cost_reduction_percent']:.1f}%)")


if __name__ == "__main__":
    # Run examples
    example_retriever()
    example_query_engine()
    example_index_creation()
    example_with_documents()
    example_comparison()

    print("\n" + "=" * 60)
    print("✓ Llamaindex integration examples complete!")
    print("=" * 60)
