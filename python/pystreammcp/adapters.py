"""Base adapter pattern for LLM framework integrations.

Provides a common interface for all supported frameworks
(Langchain, Llamaindex, Semantic Kernel, CrewAI, PydanticAI, Haystack).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class FrameworkType(str, Enum):
    """Supported LLM frameworks."""
    LANGCHAIN = "langchain"
    LLAMAINDEX = "llamaindex"
    SEMANTIC_KERNEL = "semantic_kernel"
    CREWAI = "crewai"
    PYDANTIC_AI = "pydantic_ai"
    HAYSTACK = "haystack"


@dataclass
class AdapterConfig:
    """Configuration for framework adapters."""
    framework: FrameworkType
    agent_id: str
    name: str
    optimization_strategy: str = "balanced"
    max_tokens: int = 2000
    custom_config: Optional[Dict[str, Any]] = None


@dataclass
class QueryResult:
    """Result from executing a query through an adapter."""
    query_id: str
    text: str
    intent: str
    baseline_tokens: int
    optimized_tokens: int
    cost_reduction_percent: float
    execution_time_ms: float
    context: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


class AgentFrameworkAdapter(ABC):
    """Base class for all LLM framework adapters.

    Adapters wrap framework-specific agent/tool implementations
    to provide a uniform interface to PyStreamMCP functionality.
    """

    def __init__(self, config: AdapterConfig):
        """Initialize adapter.

        Args:
            config: Adapter configuration
        """
        self.config = config
        self.framework = config.framework
        self.agent_id = config.agent_id
        self.name = config.name

    @abstractmethod
    def query(self, text: str, intent: str = "retrieve", **kwargs) -> QueryResult:
        """Execute a query through the framework.

        Args:
            text: The query text
            intent: Query intent (retrieve, discover, aggregate, synthesize, analyze)
            **kwargs: Framework-specific arguments

        Returns:
            QueryResult with optimized context and metrics
        """
        pass

    @abstractmethod
    async def query_async(self, text: str, intent: str = "retrieve", **kwargs) -> QueryResult:
        """Execute a query asynchronously.

        Args:
            text: The query text
            intent: Query intent
            **kwargs: Framework-specific arguments

        Returns:
            QueryResult with optimized context and metrics
        """
        pass

    @abstractmethod
    def discover(self, context: str, **kwargs) -> Dict[str, Any]:
        """Discover relevant data sources.

        Args:
            context: Context for discovery
            **kwargs: Framework-specific arguments

        Returns:
            Discovered sources with relevance scores
        """
        pass

    @abstractmethod
    async def discover_async(self, context: str, **kwargs) -> Dict[str, Any]:
        """Discover sources asynchronously."""
        pass

    @abstractmethod
    def optimize(self, query_text: str, strategy: Optional[str] = None, **kwargs) -> QueryResult:
        """Optimize a query for cost reduction.

        Args:
            query_text: Query to optimize
            strategy: Optimization strategy (if different from config)
            **kwargs: Framework-specific arguments

        Returns:
            Optimized query result
        """
        pass

    @abstractmethod
    async def optimize_async(self, query_text: str, strategy: Optional[str] = None, **kwargs) -> QueryResult:
        """Optimize query asynchronously."""
        pass

    @property
    def is_async_capable(self) -> bool:
        """Whether this adapter supports async operations."""
        return True

    def get_tools(self) -> List[Dict[str, Any]]:
        """Get available tools for the framework.

        Returns:
            List of tool definitions (query, discover, optimize)
        """
        return [
            {
                "name": "pystreammcp_query",
                "description": "Execute a query with PyStreamMCP optimization",
                "framework": self.framework.value,
            },
            {
                "name": "pystreammcp_discover",
                "description": "Discover relevant data sources with PyStreamMCP",
                "framework": self.framework.value,
            },
            {
                "name": "pystreammcp_optimize",
                "description": "Optimize query for cost reduction",
                "framework": self.framework.value,
            },
        ]


class AdapterRegistry:
    """Registry for managing framework adapters."""

    _adapters: Dict[FrameworkType, type[AgentFrameworkAdapter]] = {}
    _instances: Dict[str, AgentFrameworkAdapter] = {}

    @classmethod
    def register(cls, framework: FrameworkType, adapter_class: type[AgentFrameworkAdapter]) -> None:
        """Register an adapter implementation.

        Args:
            framework: Framework type
            adapter_class: Adapter class to register
        """
        cls._adapters[framework] = adapter_class

    @classmethod
    def get_adapter_class(cls, framework: FrameworkType) -> Optional[type[AgentFrameworkAdapter]]:
        """Get registered adapter class.

        Args:
            framework: Framework type

        Returns:
            Adapter class or None if not registered
        """
        return cls._adapters.get(framework)

    @classmethod
    def create_adapter(cls, config: AdapterConfig) -> AgentFrameworkAdapter:
        """Create and register an adapter instance.

        Args:
            config: Adapter configuration

        Returns:
            Adapter instance

        Raises:
            ValueError: If framework not supported
        """
        adapter_class = cls.get_adapter_class(config.framework)
        if not adapter_class:
            raise ValueError(f"No adapter registered for {config.framework}")

        adapter = adapter_class(config)
        cls._instances[config.agent_id] = adapter
        return adapter

    @classmethod
    def get_adapter(cls, agent_id: str) -> Optional[AgentFrameworkAdapter]:
        """Get existing adapter instance.

        Args:
            agent_id: Agent ID

        Returns:
            Adapter instance or None if not found
        """
        return cls._instances.get(agent_id)

    @classmethod
    def list_adapters(cls) -> Dict[str, AgentFrameworkAdapter]:
        """List all registered adapter instances."""
        return cls._instances.copy()

    @classmethod
    def list_supported_frameworks(cls) -> List[str]:
        """List supported frameworks."""
        return [f.value for f in cls._adapters.keys()]
