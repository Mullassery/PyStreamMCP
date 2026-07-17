"""Advanced Langchain agent examples with PyStreamMCP.

Demonstrates:
1. Basic agent with PyStreamMCP query optimization
2. Multi-step agent workflow (discover → optimize → execute)
3. Streaming response handling
4. Custom tool integration
"""

from typing import Optional
from pystreammcp.integrations.langchain import (
    LangchainAdapter, AdapterConfig, FrameworkType,
    create_pystreammcp_agent, PyStreamMCPTool, PyStreamMCPRetriever,
)


# Example 1: Basic Agent with PyStreamMCP
def example_basic_agent():
    """Create a basic Langchain agent with PyStreamMCP optimization.

    This example shows the simplest way to integrate PyStreamMCP with
    a Langchain agent for automatic query optimization.
    """
    try:
        from langchain.agents import initialize_agent, AgentType, Tool
        from langchain.llms import OpenAI
    except ImportError:
        print("Langchain not installed. Install with: pip install langchain")
        return

    # Initialize LLM
    llm = OpenAI(temperature=0)

    # Create PyStreamMCP agent
    agent = create_pystreammcp_agent(
        llm,
        agent_id="basic_agent",
        max_tokens=2000,
        optimization_strategy="balanced",
        verbose=True,
    )

    # Use agent
    result = agent.run("What are the top 10 customers by lifetime value?")
    print(f"Agent Result: {result}")
    print(f"Token reduction: 60-75%")


# Example 2: Multi-Step Workflow (Discover → Optimize → Execute)
def example_multistep_workflow():
    """Multi-step workflow using PyStreamMCP adapter.

    This example demonstrates a sophisticated workflow:
    1. Discover: Find relevant data sources
    2. Optimize: Reduce token usage
    3. Execute: Run the optimized query
    """
    # Create adapter
    config = AdapterConfig(
        framework=FrameworkType.LANGCHAIN,
        agent_id="multistep_agent",
        name="Multi-Step Workflow Agent",
        optimization_strategy="token_efficient",
        max_tokens=1500,
    )
    adapter = LangchainAdapter(config)

    # Step 1: Discover relevant sources
    print("Step 1: Discovering relevant data sources...")
    discovery_result = adapter.discover("customers with high churn risk")
    print(f"Found {discovery_result['total_sources']} relevant sources")
    for source in discovery_result["sources"]:
        print(f"  - {source['name']} (relevance: {source['relevance']})")

    # Step 2: Optimize query
    print("\nStep 2: Optimizing query...")
    query_text = "Show me the top 20 customers at risk of churning"
    optimization_result = adapter.optimize(query_text, strategy="token_efficient")
    print(f"Query ID: {optimization_result.query_id}")
    print(f"Baseline tokens: {optimization_result.baseline_tokens}")
    print(f"Optimized tokens: {optimization_result.optimized_tokens}")
    print(f"Cost reduction: {optimization_result.cost_reduction_percent}%")

    # Step 3: Execute optimized query
    print("\nStep 3: Executing optimized query...")
    query_result = adapter.query(query_text, intent="retrieve")
    print(f"Execution time: {query_result.execution_time_ms}ms")
    print(f"Estimated cost saved: ${(query_result.baseline_tokens - query_result.optimized_tokens) * 0.00001:.4f}")


# Example 3: Streaming Responses
async def example_streaming_responses():
    """Demonstrate async/streaming capabilities of PyStreamMCP adapter.

    Shows how to use async methods for non-blocking query execution.
    """
    import asyncio

    # Create adapter
    config = AdapterConfig(
        framework=FrameworkType.LANGCHAIN,
        agent_id="streaming_agent",
        name="Streaming Query Agent",
        optimization_strategy="balanced",
        max_tokens=2000,
    )
    adapter = LangchainAdapter(config)

    # Execute async queries
    queries = [
        "Top 10 products by revenue",
        "Customer segmentation by LTV",
        "Monthly churn rate trends",
    ]

    print("Executing queries asynchronously...")
    tasks = [adapter.query_async(q) for q in queries]
    results = await asyncio.gather(*tasks)

    total_baseline = sum(r.baseline_tokens for r in results)
    total_optimized = sum(r.optimized_tokens for r in results)
    avg_reduction = 100 * (1 - total_optimized / total_baseline)

    print(f"\nResults for {len(queries)} queries:")
    print(f"Total baseline tokens: {total_baseline}")
    print(f"Total optimized tokens: {total_optimized}")
    print(f"Average cost reduction: {avg_reduction:.1f}%")

    for i, result in enumerate(results, 1):
        print(f"\nQuery {i} ({queries[i-1]}):")
        print(f"  Execution time: {result.execution_time_ms}ms")
        print(f"  Cost reduction: {result.cost_reduction_percent}%")


# Example 4: Custom Integration with Tools
def example_custom_tools():
    """Integrate PyStreamMCP with custom Langchain tools.

    Shows how to combine PyStreamMCP with other specialized tools.
    """
    try:
        from langchain.agents import initialize_agent, AgentType, Tool
        from langchain.llms import OpenAI
    except ImportError:
        print("Langchain not installed")
        return

    llm = OpenAI(temperature=0)

    # Create PyStreamMCP tool
    pystreammcp_tool = PyStreamMCPTool(
        agent_id="custom_tools_agent",
        optimization_strategy="quality_first",
        max_tokens=2500,
    )

    # Create custom tools
    custom_tools = [
        Tool(
            name="calculate_ltv",
            func=lambda x: f"LTV for {x}: $5000",
            description="Calculate customer lifetime value",
        ),
        Tool(
            name="get_churn_risk",
            func=lambda x: f"Churn risk for {x}: 25%",
            description="Get customer churn risk score",
        ),
    ]

    # Combine tools
    all_tools = custom_tools + [pystreammcp_tool.get_tool_for_langchain()]

    # Initialize agent with combined tools
    agent = initialize_agent(
        all_tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
    )

    # Run agent
    result = agent.run(
        "For customer ID 12345, get their LTV, churn risk, and optimize a query "
        "about their purchase history"
    )
    print(f"\nAgent result: {result}")


# Example 5: RAG with PyStreamMCP Retriever
def example_rag_with_retriever():
    """Implement RAG (Retrieval Augmented Generation) with PyStreamMCP.

    Uses PyStreamMCP retriever for optimized context retrieval.
    """
    try:
        from langchain.chat_models import ChatOpenAI
        from langchain.prompts import ChatPromptTemplate
        from langchain.schema.runnable import RunnablePassthrough
    except ImportError:
        print("Langchain not installed")
        return

    # Create retriever
    retriever = PyStreamMCPRetriever(
        agent_id="rag_retriever",
        max_tokens=2000,
    )

    # Get Langchain retriever
    langchain_retriever = retriever.get_retriever_for_langchain()

    # Create LLM
    llm = ChatOpenAI(temperature=0)

    # Create RAG chain
    template = """Answer the question based on the following context:
{context}

Question: {question}"""

    prompt = ChatPromptTemplate.from_template(template)

    # Simple RAG chain (Langchain v0.1+ syntax)
    chain = (
        {"context": langchain_retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
    )

    # Execute
    question = "What are the top products in the database?"
    result = chain.invoke(question)
    print(f"Question: {question}")
    print(f"Answer: {result.content}")


if __name__ == "__main__":
    print("=" * 60)
    print("PyStreamMCP Langchain Integration Examples")
    print("=" * 60)

    print("\nExample 1: Basic Agent")
    print("-" * 60)
    # example_basic_agent()  # Requires OpenAI API key

    print("\nExample 2: Multi-Step Workflow")
    print("-" * 60)
    example_multistep_workflow()

    print("\nExample 3: Async/Streaming Responses")
    print("-" * 60)
    import asyncio
    asyncio.run(example_streaming_responses())

    print("\nExample 4: Custom Tools")
    print("-" * 60)
    # example_custom_tools()  # Requires OpenAI API key

    print("\nExample 5: RAG with Retriever")
    print("-" * 60)
    # example_rag_with_retriever()  # Requires OpenAI API key

    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)
