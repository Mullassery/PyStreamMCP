"""REST API server for PyStreamMCP - integrates with workflow tools."""

from typing import Dict, Any, Optional, List
from pystreammcp import Agent


class PyStreamMCPServer:
    """REST API server for workflow integration."""

    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        """Initialize server."""
        self.host = host
        self.port = port
        self.agents: Dict[str, Agent] = {}

    def create_agent(self, agent_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create an agent."""
        agent = Agent(
            agent_id=agent_id,
            name=config.get("name", agent_id),
            optimization_strategy=config.get("optimization_strategy", "balanced"),
            max_tokens=config.get("max_tokens", 2000),
        )
        self.agents[agent_id] = agent

        return {
            "status": "success",
            "agent_id": agent_id,
            "message": f"Agent {agent_id} created",
        }

    def query(self, agent_id: str, text: str, intent: str = "retrieve") -> Dict[str, Any]:
        """Execute a query."""
        if agent_id not in self.agents:
            return {"status": "error", "message": f"Agent {agent_id} not found"}

        agent = self.agents[agent_id]
        result = agent.query(text)

        return {
            "status": "success",
            "query_id": result.query_id,
            "query_text": text,
            "intent": intent,
            "baseline_tokens": result.baseline_tokens,
            "optimized_tokens": result.optimized_tokens,
            "cost_reduction_percent": result.cost_reduction_percent,
            "cost_saved": (result.baseline_tokens - result.optimized_tokens) * 0.00001,
            "execution_time_ms": result.execution_time_ms,
            "meets_target": 60 <= result.cost_reduction_percent <= 75,
        }

    def batch_query(self, agent_id: str, queries: List[str]) -> Dict[str, Any]:
        """Execute multiple queries."""
        if agent_id not in self.agents:
            return {"status": "error", "message": f"Agent {agent_id} not found"}

        agent = self.agents[agent_id]
        results = []
        total_saved = 0.0

        for query_text in queries:
            result = agent.query(query_text)
            results.append({
                "query": query_text,
                "cost_reduction_percent": result.cost_reduction_percent,
                "cost_saved": (result.baseline_tokens - result.optimized_tokens) * 0.00001,
            })
            total_saved += (result.baseline_tokens - result.optimized_tokens) * 0.00001

        return {
            "status": "success",
            "queries_processed": len(queries),
            "results": results,
            "total_cost_saved": total_saved,
        }

    def get_metrics(self, agent_id: str) -> Dict[str, Any]:
        """Get agent metrics."""
        if agent_id not in self.agents:
            return {"status": "error", "message": f"Agent {agent_id} not found"}

        agent = self.agents[agent_id]
        metrics = agent.get_metrics()

        return {
            "status": "success",
            "agent_id": agent_id,
            "metrics": metrics,
        }

    def health_check(self) -> Dict[str, Any]:
        """Health check endpoint."""
        return {
            "status": "healthy",
            "agents_count": len(self.agents),
            "version": "0.1.0",
        }

    def list_agents(self) -> Dict[str, Any]:
        """List all agents."""
        return {
            "status": "success",
            "agents": list(self.agents.keys()),
            "count": len(self.agents),
        }


# Flask integration for REST API
def create_flask_app(server: Optional[PyStreamMCPServer] = None):
    """Create Flask app for REST API."""
    try:
        from flask import Flask, request, jsonify
    except ImportError:
        raise ImportError(
            "Flask is required for REST API. Install with: pip install flask"
        )

    app = Flask(__name__)
    srv = server or PyStreamMCPServer()

    @app.route("/health", methods=["GET"])
    def health():
        """Health check."""
        return jsonify(srv.health_check())

    @app.route("/agents", methods=["GET"])
    def list_agents():
        """List all agents."""
        return jsonify(srv.list_agents())

    @app.route("/agents", methods=["POST"])
    def create_agent():
        """Create agent."""
        data = request.get_json()
        agent_id = data.get("agent_id")
        config = data.get("config", {})

        if not agent_id:
            return jsonify({"status": "error", "message": "agent_id required"}), 400

        return jsonify(srv.create_agent(agent_id, config))

    @app.route("/query", methods=["POST"])
    def query():
        """Execute query."""
        data = request.get_json()
        agent_id = data.get("agent_id")
        text = data.get("text")
        intent = data.get("intent", "retrieve")

        if not agent_id or not text:
            return (
                jsonify({"status": "error", "message": "agent_id and text required"}),
                400,
            )

        return jsonify(srv.query(agent_id, text, intent))

    @app.route("/batch-query", methods=["POST"])
    def batch_query():
        """Execute batch queries."""
        data = request.get_json()
        agent_id = data.get("agent_id")
        queries = data.get("queries", [])

        if not agent_id or not queries:
            return (
                jsonify(
                    {"status": "error", "message": "agent_id and queries required"}
                ),
                400,
            )

        return jsonify(srv.batch_query(agent_id, queries))

    @app.route("/metrics/<agent_id>", methods=["GET"])
    def metrics(agent_id):
        """Get agent metrics."""
        return jsonify(srv.get_metrics(agent_id))

    return app


def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the REST API server."""
    app = create_flask_app()
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    run_server()
