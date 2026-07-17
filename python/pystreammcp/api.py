"""FastAPI REST server for PyStreamMCP.

Provides HTTP API for query planning, context discovery, and cost optimization.
Integrates with workflow orchestration tools and LLM frameworks.
"""

from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Query as QueryParam
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
import logging

from .adapters import AdapterRegistry, AdapterConfig, FrameworkType, QueryResult
from .agent import Agent


logger = logging.getLogger(__name__)


# Request/Response Models

class QueryRequest(BaseModel):
    """Query execution request."""
    text: str = Field(..., description="Query text")
    intent: str = Field("retrieve", description="Query intent")
    agent_id: Optional[str] = Field(None, description="Agent ID")
    max_tokens: Optional[int] = Field(None, description="Max tokens for response")


class QueryResponse(BaseModel):
    """Query execution response."""
    status: str
    query_id: str
    text: str
    intent: str
    baseline_tokens: int
    optimized_tokens: int
    cost_reduction_percent: float
    execution_time_ms: float
    context: Dict[str, Any]


class DiscoveryRequest(BaseModel):
    """Data source discovery request."""
    context: str = Field(..., description="Context for discovery")
    agent_id: Optional[str] = Field(None, description="Agent ID")


class DiscoveryResponse(BaseModel):
    """Discovery response with sources."""
    status: str
    sources: List[Dict[str, Any]]
    total_sources: int


class OptimizationRequest(BaseModel):
    """Query optimization request."""
    text: str = Field(..., description="Query text")
    strategy: Optional[str] = Field(None, description="Optimization strategy")
    agent_id: Optional[str] = Field(None, description="Agent ID")


class OptimizationResponse(BaseModel):
    """Optimization response."""
    status: str
    query_id: str
    baseline_tokens: int
    optimized_tokens: int
    cost_reduction_percent: float
    techniques: List[str]


class AgentConfig(BaseModel):
    """Agent configuration."""
    agent_id: str = Field(..., description="Unique agent ID")
    name: str = Field(..., description="Agent name")
    optimization_strategy: str = Field("balanced", description="Optimization strategy")
    max_tokens: int = Field(2000, description="Token budget")
    framework: Optional[str] = Field(None, description="Framework type")


class AgentResponse(BaseModel):
    """Agent creation response."""
    status: str
    agent_id: str
    name: str
    optimization_strategy: str
    max_tokens: int


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    adapters: List[str]


# API Server

class PyStreamMCPAPI:
    """PyStreamMCP REST API server."""

    def __init__(self, title: str = "PyStreamMCP", version: str = "0.2.0"):
        """Initialize API server."""
        self.title = title
        self.version = version
        self.agents: Dict[str, Agent] = {}
        self.app = self._create_app()

    def _create_app(self) -> FastAPI:
        """Create FastAPI application."""

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            logger.info(f"Starting {self.title} v{self.version}")
            yield
            logger.info(f"Stopping {self.title}")

        app = FastAPI(
            title=self.title,
            version=self.version,
            description="Intelligence layer for AI agents - query planning, discovery, cost optimization",
            lifespan=lifespan,
        )

        # Health & Info Endpoints
        @app.get("/health", response_model=HealthResponse)
        async def health():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "version": self.version,
                "adapters": AdapterRegistry.list_supported_frameworks(),
            }

        @app.get("/info")
        async def info():
            """Server information."""
            return {
                "name": self.title,
                "version": self.version,
                "agents": list(self.agents.keys()),
                "adapters": {
                    "available": AdapterRegistry.list_supported_frameworks(),
                    "registered": AdapterRegistry.list_adapters(),
                },
            }

        # Agent Management Endpoints
        @app.post("/agents", response_model=AgentResponse)
        async def create_agent(config: AgentConfig):
            """Create a new agent."""
            if config.agent_id in self.agents:
                raise HTTPException(status_code=400, detail=f"Agent {config.agent_id} already exists")

            agent = Agent(
                agent_id=config.agent_id,
                name=config.name,
                optimization_strategy=config.optimization_strategy,
                max_tokens=config.max_tokens,
            )
            self.agents[config.agent_id] = agent

            return {
                "status": "success",
                "agent_id": config.agent_id,
                "name": config.name,
                "optimization_strategy": config.optimization_strategy,
                "max_tokens": config.max_tokens,
            }

        @app.get("/agents")
        async def list_agents():
            """List all agents."""
            return {
                "status": "success",
                "agents": [
                    {
                        "agent_id": agent.agent_id,
                        "name": agent.name,
                        "optimization_strategy": getattr(agent, "optimization_strategy", "unknown"),
                    }
                    for agent in self.agents.values()
                ],
            }

        @app.get("/agents/{agent_id}")
        async def get_agent(agent_id: str):
            """Get agent details."""
            if agent_id not in self.agents:
                raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

            agent = self.agents[agent_id]
            return {
                "status": "success",
                "agent_id": agent.agent_id,
                "name": agent.name,
            }

        # Query Endpoints
        @app.post("/query", response_model=QueryResponse)
        async def query(request: QueryRequest):
            """Execute a query with optimization."""
            agent = self._get_agent(request.agent_id)

            result = agent.query(request.text)

            return {
                "status": "success",
                "query_id": result.query_id,
                "text": request.text,
                "intent": request.intent,
                "baseline_tokens": result.baseline_tokens,
                "optimized_tokens": result.optimized_tokens,
                "cost_reduction_percent": result.cost_reduction_percent,
                "execution_time_ms": result.execution_time_ms,
                "context": {},
            }

        @app.post("/query/batch")
        async def batch_query(agent_id: Optional[str] = None, texts: List[str] = []):
            """Execute multiple queries."""
            agent = self._get_agent(agent_id)

            results = []
            for text in texts:
                result = agent.query(text)
                results.append({
                    "query_id": result.query_id,
                    "text": text,
                    "baseline_tokens": result.baseline_tokens,
                    "optimized_tokens": result.optimized_tokens,
                    "cost_reduction_percent": result.cost_reduction_percent,
                })

            return {
                "status": "success",
                "results": results,
                "total_queries": len(results),
            }

        # Discovery Endpoints
        @app.post("/discover", response_model=DiscoveryResponse)
        async def discover(request: DiscoveryRequest):
            """Discover relevant data sources."""
            agent = self._get_agent(request.agent_id)

            # TODO: Implement discovery logic
            sources = []

            return {
                "status": "success",
                "sources": sources,
                "total_sources": len(sources),
            }

        # Optimization Endpoints
        @app.post("/optimize", response_model=OptimizationResponse)
        async def optimize(request: OptimizationRequest):
            """Optimize a query for cost reduction."""
            agent = self._get_agent(request.agent_id)

            result = agent.query(request.text)

            return {
                "status": "success",
                "query_id": result.query_id,
                "baseline_tokens": result.baseline_tokens,
                "optimized_tokens": result.optimized_tokens,
                "cost_reduction_percent": result.cost_reduction_percent,
                "techniques": ["pruning", "summarization", "caching"],
            }

        # Metrics Endpoints
        @app.get("/metrics")
        async def metrics(agent_id: Optional[str] = QueryParam(None)):
            """Get performance metrics."""
            if agent_id and agent_id not in self.agents:
                raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

            return {
                "status": "success",
                "agents": len(self.agents),
                "metrics": {
                    "total_queries": 0,
                    "avg_reduction_percent": 0.0,
                    "total_tokens_saved": 0,
                },
            }

        return app

    def _get_agent(self, agent_id: Optional[str] = None) -> Agent:
        """Get agent, using first available if not specified."""
        if not agent_id:
            if not self.agents:
                raise HTTPException(status_code=400, detail="No agents configured")
            agent_id = next(iter(self.agents))

        if agent_id not in self.agents:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

        return self.agents[agent_id]

    def run(self, host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
        """Run the API server.

        Args:
            host: Server host
            port: Server port
            reload: Enable auto-reload on file changes
        """
        import uvicorn
        uvicorn.run(self.app, host=host, port=port, reload=reload)


def create_app() -> FastAPI:
    """Factory function to create FastAPI app."""
    api = PyStreamMCPAPI()
    return api.app
