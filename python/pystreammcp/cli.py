"""CLI for PyStreamMCP - command-line interface for workflow tools."""

import json
import sys
from typing import Optional
from pystreammcp import Agent, Query, QueryIntent, OptimizationStrategy, StrategyType


class CLIInterface:
    """Command-line interface for PyStreamMCP."""

    def __init__(self):
        self.agent = None

    def create_agent(self, agent_id: str, strategy: str = "balanced", max_tokens: int = 2000):
        """Create an agent."""
        self.agent = Agent(
            agent_id=agent_id,
            optimization_strategy=strategy,
            max_tokens=max_tokens,
        )
        return {"status": "success", "agent_id": agent_id}

    def query(self, text: str, intent: str = "retrieve", agent_id: Optional[str] = None) -> dict:
        """Execute a query."""
        if agent_id:
            self.create_agent(agent_id)

        if not self.agent:
            return {"status": "error", "message": "No agent created"}

        result = self.agent.query(text)

        return {
            "status": "success",
            "query_id": result.query_id,
            "query_text": text,
            "baseline_tokens": result.baseline_tokens,
            "optimized_tokens": result.optimized_tokens,
            "cost_reduction_percent": result.cost_reduction_percent,
            "cost_saved": (result.baseline_tokens - result.optimized_tokens) * 0.00001,
            "execution_time_ms": result.execution_time_ms,
            "meets_target": 60 <= result.cost_reduction_percent <= 75,
        }

    def get_metrics(self) -> dict:
        """Get agent metrics."""
        if not self.agent:
            return {"status": "error", "message": "No agent created"}

        metrics = self.agent.get_metrics()
        return {
            "status": "success",
            "metrics": metrics,
        }


def main():
    """Main CLI entry point."""
    cli = CLIInterface()

    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)

    command = sys.argv[1]

    try:
        if command == "query":
            if len(sys.argv) < 3:
                print(json.dumps({"error": "Missing query text"}))
                sys.exit(1)

            text = sys.argv[2]
            intent = sys.argv[3] if len(sys.argv) > 3 else "retrieve"
            agent_id = sys.argv[4] if len(sys.argv) > 4 else "cli_agent"

            result = cli.query(text, intent=intent, agent_id=agent_id)
            print(json.dumps(result))

        elif command == "create-agent":
            if len(sys.argv) < 3:
                print(json.dumps({"error": "Missing agent_id"}))
                sys.exit(1)

            agent_id = sys.argv[2]
            strategy = sys.argv[3] if len(sys.argv) > 3 else "balanced"
            max_tokens = int(sys.argv[4]) if len(sys.argv) > 4 else 2000

            result = cli.create_agent(agent_id, strategy, max_tokens)
            print(json.dumps(result))

        elif command == "metrics":
            result = cli.get_metrics()
            print(json.dumps(result))

        elif command == "help":
            print_help()

        else:
            print(json.dumps({"error": f"Unknown command: {command}"}))
            sys.exit(1)

    except Exception as e:
        print(json.dumps({"error": str(e), "status": "error"}))
        sys.exit(1)


def print_help():
    """Print help message."""
    help_text = """
PyStreamMCP CLI - Intelligence Layer for Workflows

USAGE:
    pystreammcp <command> [options]

COMMANDS:
    query <text> [intent] [agent_id]
        Execute a query with optimization
        - text: The query text (required)
        - intent: Query type (retrieve|discover|aggregate) (default: retrieve)
        - agent_id: Agent identifier (default: cli_agent)

        Example:
            pystreammcp query "Top 10 customers by LTV" retrieve my_agent

    create-agent <agent_id> [strategy] [max_tokens]
        Create an agent with specific configuration
        - agent_id: Agent identifier (required)
        - strategy: Optimization strategy (balanced|token_efficient|quality_first) (default: balanced)
        - max_tokens: Token budget (default: 2000)

        Example:
            pystreammcp create-agent workflow_agent token_efficient 1500

    metrics
        Get current agent metrics

        Example:
            pystreammcp metrics

    help
        Show this help message

OUTPUT FORMAT:
    All commands return JSON output for easy parsing in workflows

EXAMPLES:
    # Query with cost tracking
    pystreammcp query "Find churn risk customers"

    # Efficient query for token-constrained environments
    pystreammcp query "List segments" discover automation_agent

    # Get metrics for reporting
    pystreammcp metrics | jq '.metrics.total_cost_saved'
"""
    print(help_text)


if __name__ == "__main__":
    main()
