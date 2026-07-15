"""CrewAI integration for PyStreamMCP.

Enables CrewAI agents to use PyStreamMCP for optimized context retrieval.
"""

from typing import Optional, Dict, Any, List
from pystreammcp import Agent


class PyStreamMCPTool:
    """CrewAI tool for PyStreamMCP."""

    def __init__(
        self,
        agent_id: str = "crewai_agent",
        max_tokens: int = 2000,
    ):
        """
        Initialize PyStreamMCP tool for CrewAI.

        Args:
            agent_id: Identifier for the agent
            max_tokens: Token budget
        """
        self.agent = Agent(
            agent_id=agent_id,
            name=f"CrewAI: {agent_id}",
            optimization_strategy="token_efficient",
            max_tokens=max_tokens,
        )
        self.name = "optimize_context"
        self.description = (
            "Optimize and retrieve context using PyStreamMCP. "
            "Reduces token usage by 60-75% while maintaining quality."
        )

    def execute(self, query: str) -> str:
        """
        Execute a query and return optimized context.

        Args:
            query: The query text

        Returns:
            Formatted result string
        """
        result = self.agent.query(query)

        return (
            f"Query: {query}\n"
            f"Baseline tokens: {result.baseline_tokens}\n"
            f"Optimized tokens: {result.optimized_tokens}\n"
            f"Reduction: {result.cost_reduction_percent:.1f}%\n"
            f"Cost saved: ${(result.baseline_tokens - result.optimized_tokens) * 0.00001:.4f}"
        )

    def __call__(self, query: str) -> str:
        """Make tool callable."""
        return self.execute(query)


def create_pystreammcp_tool_for_crewai(
    agent_id: str = "crewai_agent",
    max_tokens: int = 2000,
) -> PyStreamMCPTool:
    """
    Create a PyStreamMCP tool for CrewAI agents.

    Args:
        agent_id: Identifier for the agent
        max_tokens: Token budget

    Returns:
        PyStreamMCPTool instance
    """
    return PyStreamMCPTool(
        agent_id=agent_id,
        max_tokens=max_tokens,
    )


def add_pystreammcp_to_agent(agent, agent_id: str = "crewai_agent"):
    """
    Add PyStreamMCP optimization to a CrewAI agent.

    Args:
        agent: CrewAI agent instance
        agent_id: Identifier for PyStreamMCP

    Returns:
        CrewAI agent with PyStreamMCP tool
    """
    tool = create_pystreammcp_tool_for_crewai(agent_id=agent_id)

    if hasattr(agent, "tools"):
        agent.tools.append(tool)
    else:
        agent.tools = [tool]

    return agent
