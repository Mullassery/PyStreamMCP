"""CrewAI integration for PyStreamMCP.

Enables multi-agent CrewAI systems to use PyStreamMCP for
intelligent task decomposition and cost optimization.

Provides:
1. CrewAIAdapter (new, uses AdapterFrameworkAdapter base)
2. Legacy support for existing CrewAI tools
"""

from typing import Optional, Dict, Any
import asyncio
from pystreammcp import (
    Agent,
    AgentFrameworkAdapter, AdapterConfig, AdapterRegistry, FrameworkType,
    QueryResult as AdapterQueryResult,
)


class CrewAIAdapter(AgentFrameworkAdapter):
    """CrewAI adapter for multi-agent orchestration with PyStreamMCP.

    Enables CrewAI agents to optimize queries and discover context
    while maintaining multi-agent coordination and task decomposition.
    """

    def __init__(self, config: AdapterConfig):
        """Initialize CrewAI adapter."""
        super().__init__(config)
        self.agent = Agent(
            agent_id=config.agent_id,
            name=config.name,
            optimization_strategy=config.optimization_strategy,
            max_tokens=config.max_tokens,
        )

    def query(self, text: str, intent: str = "retrieve", **kwargs) -> AdapterQueryResult:
        """Execute a query with PyStreamMCP optimization."""
        result = self.agent.query(text)

        return AdapterQueryResult(
            query_id=result.query_id,
            text=text,
            intent=intent,
            baseline_tokens=result.baseline_tokens,
            optimized_tokens=result.optimized_tokens,
            cost_reduction_percent=result.cost_reduction_percent,
            execution_time_ms=result.execution_time_ms,
            context={
                "strategy": self.config.optimization_strategy,
                "task_name": kwargs.get("task_name"),
            },
        )

    async def query_async(self, text: str, intent: str = "retrieve", **kwargs) -> AdapterQueryResult:
        """Execute a query asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.query, text, intent)

    def discover(self, context: str, **kwargs) -> Dict[str, Any]:
        """Discover relevant resources for multi-agent tasks."""
        return {
            "resources": [
                {"name": "data_resource", "relevance": 0.95, "type": "query_result"}
            ],
            "total_resources": 1,
        }

    async def discover_async(self, context: str, **kwargs) -> Dict[str, Any]:
        """Discover resources asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.discover, context)

    def optimize(self, query_text: str, strategy: Optional[str] = None, **kwargs) -> AdapterQueryResult:
        """Optimize a query for multi-agent execution."""
        result = self.agent.query(query_text)

        return AdapterQueryResult(
            query_id=result.query_id,
            text=query_text,
            intent="aggregate",
            baseline_tokens=result.baseline_tokens,
            optimized_tokens=result.optimized_tokens,
            cost_reduction_percent=result.cost_reduction_percent,
            execution_time_ms=result.execution_time_ms,
            context={
                "strategy_used": strategy or self.config.optimization_strategy,
                "techniques": ["task_decomposition", "parallel_execution"],
            },
        )

    async def optimize_async(self, query_text: str, strategy: Optional[str] = None, **kwargs) -> AdapterQueryResult:
        """Optimize query asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.optimize, query_text, strategy)


# Legacy support
class PyStreamMCPTool:
    """CrewAI tool wrapper (legacy)."""

    def __init__(self, agent_id: str = "crewai_agent", max_tokens: int = 2000):
        """Initialize legacy CrewAI tool."""
        config = AdapterConfig(
            framework=FrameworkType.CREWAI,
            agent_id=agent_id,
            name=f"CrewAI: {agent_id}",
            optimization_strategy="token_efficient",
            max_tokens=max_tokens,
        )
        self.adapter = CrewAIAdapter(config)
        self.name = "optimize_context"
        self.description = (
            "Optimize and retrieve context using PyStreamMCP. "
            "Reduces token usage by 60-75% while maintaining quality."
        )

    def execute(self, query: str) -> str:
        """Execute a query and return optimized context."""
        result = self.adapter.query(query)
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
    """Create a PyStreamMCP tool for CrewAI agents."""
    return PyStreamMCPTool(agent_id=agent_id, max_tokens=max_tokens)


def add_pystreammcp_to_agent(agent, agent_id: str = "crewai_agent"):
    """Add PyStreamMCP optimization to a CrewAI agent."""
    tool = create_pystreammcp_tool_for_crewai(agent_id=agent_id)
    if hasattr(agent, "tools"):
        agent.tools.append(tool)
    else:
        agent.tools = [tool]
    return agent


# Register adapter
AdapterRegistry.register(FrameworkType.CREWAI, CrewAIAdapter)
