# PyStreamMCP

**Intelligence Layer for AI Agents**

PyStreamMCP is a Rust-powered, Python-extensible platform that optimizes queries and discovers context for AI agents. It delivers 60-75% token reduction while maintaining quality and speed.

## Philosophy

Rather than agents asking for everything and parsing the response, PyStreamMCP asks: **What does this agent actually need?**

```
Agent Query
        ↓
Query Planning (token budget)
        ↓
Context Discovery (what's relevant?)
        ↓
Optimization (60-75% reduction)
        ↓
Optimal Context Window
        ↓
Agent Response
```

The platform sits between agent frameworks and data systems, dramatically reducing token usage without sacrificing quality.

## Core Capabilities

### Query Planning
- Understand agent intent (Retrieve, Discover, Aggregate, Synthesize, Analyze)
- Enforce token budgets per query
- Set latency and confidence constraints
- Token-efficient mode (500 token cap, 0.85 confidence floor)

### Context Discovery
- Identify relevant data sources automatically
- Rank by relevance + freshness scores
- Estimate token cost per source
- Discover across warehouses, caches, APIs

### Cost Optimization
- **Caching** — Reuse computed results
- **Summarization** — Summarize instead of full text
- **Sampling** — Sample data instead of full scan
- **Pruning** — Remove low-relevance items
- **Compression** — Compress representations
- **Async** — Parallelize requests
- **Early Termination** — Stop when confident

### Validation Gates
- Integrate StatGuardian for data quality
- Validate context before including in responses
- Configurable freshness requirements
- Block bad data automatically

## Getting Started

### Installation

```bash
pip install pystreammcp
```

### Quick Example

```python
from pystreammcp import Query, Discovery, Optimization

# Agent asks a question
query = Query("Which customers are at churn risk?", agent_id="agent_123")
query = query.token_efficient()  # Max 500 tokens, 0.85 confidence

# Discover relevant context
discovery = Discovery.new(query.id)
# ... sources discovered and ranked ...

# Optimize for cost
strategy = Optimization.for_token_efficiency(query.id)
# Caching + Pruning + Summarization + Early Termination

# Result: 70% token reduction
# Cost: $0.10 instead of $0.33
```

## Core Concepts

### Queries
What agents need to know:
- **Retrieve** — Get specific information
- **Discover** — Explore available data  
- **Aggregate** — Summarize multiple sources
- **Synthesize** — Combine information
- **Analyze** — Statistical analysis

### Context
Relevant information discovered automatically:
- Entity data (customers, accounts, products)
- Relationships (who knows whom, what links where)
- Metrics (MRR, churn rate, engagement)
- Historical context (trends, patterns)
- Similar items (recommendations, benchmarks)
- Contextual information (categories, tags)

### Discovery
Find what matters:
- Scan available data sources
- Rank by relevance + freshness
- Estimate token costs
- Identify caching opportunities
- Discover relationships and dependencies

### Optimization
Reduce without losing quality:
- 60-75% token reduction target
- Multiple techniques combined
- Quality validation throughout
- Cost metrics tracked

## Features

### ✅ Phase 1: Intelligence Foundation
- Query planning with constraints
- Context discovery and ranking
- Cost optimization strategies
- SQLite persistence
- StatGuardian validation
- 18+ unit tests

### ✅ Phase 2: Agent Integration
- MCP (Model Context Protocol) support
- 6 LLM framework integrations (Langchain, Llamaindex, Semantic Kernel, CrewAI, PydanticAI, Haystack)
- 6 workflow orchestration tools (Temporal, Airflow, n8n, Power Automate, UiPath, Automation Anywhere)
- REST API server + CLI interface
- Docker deployment support
- 27+ integration tests

### 🚧 Phase 3: Advanced Optimization (In Progress)
- **Week 1-3:** Learned relevance models (accuracy > 80%)
- **Week 4-6:** Multi-agent context sharing (+20% collective savings)
- **Week 7-8:** Complex query decomposition
- **Week 9-10:** Streaming context windows (< 50ms latency)
- **Week 11-12:** Cost governance and budgets

### 🔮 Phase 4: Enterprise (Planned)
- Team-level cost governance
- Agent performance analytics
- Custom optimization rules
- Advanced audit logging

## Architecture

### Rust Core
- Query parsing and planning
- Context discovery
- Optimization engine
- Token estimation
- SQLite persistence

### Python Layer
- SDK and bindings
- Agent integrations
- Custom optimizers
- Langchain/Llamaindex adapters

### Persistence
- SQLite (local)
- PostgreSQL (enterprise)

## Token Reduction Targets

PyStreamMCP aims for 60-75% token reduction:

**Before:**
- Query: "Which customers are at churn risk?" (10 tokens)
- Full customer data: 2,000 rows × 50 tokens = 100,000 tokens
- Full interaction history: 500 interactions × 20 tokens = 10,000 tokens
- Similar customers: 100 rows × 50 tokens = 5,000 tokens
- **Total: 115,010 tokens**

**After (with PyStreamMCP):**
- Query: "Which customers are at churn risk?" (10 tokens)
- Top 10 at-risk customers + key traits: 500 tokens
- Recent interactions (last 30 days): 1,000 tokens
- Cohort comparison: 500 tokens
- **Total: 2,010 tokens**
- **Reduction: 98.3% (exceeds 60-75% target)** ✅

## Ecosystem

PyStreamMCP is part of the data intelligence platform:

- **StatGuardian** — Ensures data is trustworthy (validation, contracts, drift)
- **ClusterAudienceKit** — Identifies who matters (segmentation, clustering)
- **PyReverseETL** — Activates intelligence in operational systems
- **PyCustomerJourney** — Drives engagement through journeys
- **PyStreamMCP** — Optimizes intelligence for AI agents (this project)

## Architectural Boundaries

PyStreamMCP focuses exclusively on:

✓ Query planning and optimization
✓ Context discovery
✓ Cost optimization (token reduction)
✓ Agent intelligence

PyStreamMCP does NOT:

✗ Validate data (StatGuardian)
✗ Create audiences (ClusterAudienceKit)
✗ Activate data (PyReverseETL)
✗ Manage journeys (PyCustomerJourney)

## Development

### Building

```bash
# Build Rust core
cargo build -p pystreammcp-core

# Build Python bindings
maturin develop

# Run tests
cargo test
pytest tests/
```

### Contributing

See CONTRIBUTING.md for guidelines.

## License

MIT License. See LICENSE for details.

## Support

- GitHub Issues: [PyStreamMCP/issues](https://github.com/Mullassery/PyStreamMCP/issues)
- Discussions: [PyStreamMCP/discussions](https://github.com/Mullassery/PyStreamMCP/discussions)

---

**PyStreamMCP: Intelligent Context for Smarter Agents**
