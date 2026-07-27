# OKF Integration Guide for PyStreamMCP

**Status:** Phase 1-3 Complete  
**Version:** v0.1  
**Date:** 2026-07-20

---

## Overview

PyStreamMCP now natively supports Google's Open Knowledge Format (OKF) for storing and querying MCP system metadata, tool definitions, and query optimization plans.

OKF enables:
- **Portable metadata** — MCP systems defined as git-trackable markdown
- **Agent-native discovery** — Agents navigate OKF documents directly
- **Zero vendor lock-in** — Metadata not trapped in PyStreamMCP
- **Community contribution** — Teams share and improve tool definitions

---

## Quick Start

### 1. Initialize OKF Catalog

```python
from pathlib import Path
from pystreammcp.okf_core import OKFCatalog

# Create catalog (auto-creates directory structure)
catalog = OKFCatalog(Path("./mcp_catalog"))
```

### 2. Export Discovered Systems

```python
from pystreammcp.okf_discovery import DiscoveryOKFExporter

exporter = DiscoveryOKFExporter(catalog)

# Export PostgreSQL system
exporter.export_system(
    system_id="postgres-prod",
    name="PostgreSQL Production",
    description="Primary OLTP database",
    tools_count=45,
    cost_per_query=0.02,
    latency_p99_ms=150,
    metadata={"tags": ["database", "sql", "production"]}
)

# Export tools
exporter.export_tool(
    tool_id="search_customers",
    name="Search Customers",
    description="Full-text search on customers",
    system_id="postgres-prod",
    cost=0.01,
    latency_p95_ms=50,
    parameters={
        "query": {"type": "string", "description": "Search term"},
        "limit": {"type": "integer", "description": "Result limit"}
    }
)
```

### 3. Generate Query Plans from OKF

```python
from pystreammcp.okf_query_planner import OKFQueryPlanner

planner = OKFQueryPlanner(catalog)

# Generate cheapest plan
plan = planner.find_cheapest_path("get customer profile")

# Print results
for step in plan.steps:
    print(f"System: {step.system_name}, Tool: {step.tool_name}, Cost: ${step.cost}")

print(f"Total cost: ${plan.total_cost}")
print(f"Total latency: {plan.total_latency_ms}ms")
print(f"Token cost: {plan.total_token_cost}")
```

---

## Directory Structure

```
mcp_catalog/
├── systems/              # MCP system profiles
│   ├── postgres.md
│   ├── elasticsearch.md
│   └── bigquery.md
├── tools/                # MCP tool definitions
│   ├── search_customers.md
│   ├── analyze_trends.md
│   └── query_data.md
├── query_plans/          # Optimized query plans
│   ├── customer_360.md
│   └── sales_analytics.md
├── schemas/              # Data schema definitions
├── interconnections/     # System relationships
├── playbooks/            # Best practice guides
└── case_studies/         # Real-world examples
```

---

## OKF Document Example

### System Document (`systems/postgres.md`)
```yaml
---
type: mcp-system
title: PostgreSQL Production
system_id: postgres-prod
tools_count: 45
cost_per_query: 0.02
latency_p99_ms: 150
tags: [database, sql, production]
timestamp: 2026-07-20T12:30:00
---

# PostgreSQL Production

## Overview
Primary OLTP database for customer data and transactions.

## Tools (45 total)
- 15 customer queries
- 20 order operations
- 10 analytics queries

## Cost Profile
- $0.02 per query
- p99 latency: 150ms

## Related
- [[elasticsearch.md]] — Analytics copy
- [[bigquery.md]] — Historical warehouse
```

### Tool Document (`tools/search_customers.md`)
```yaml
---
type: mcp-tool
title: Search Customers
tool_id: search_customers
system: postgres-prod
cost: 0.01
latency_p95_ms: 50
parameter_count: 2
tags: [customer, search]
timestamp: 2026-07-20T12:30:00
---

# Search Customers

## Description
Full-text search across customer names and metadata.

## Parameters
```json
{
  "query": {"type": "string", "description": "Customer name or email"},
  "limit": {"type": "integer", "default": 10}
}
```

## Performance
- Latency (p95): 50ms
- Cost per call: $0.01
- Cache hit rate: 60%
```

---

## API Reference

### OKFCatalog

```python
from pystreammcp.okf_core import OKFCatalog

catalog = OKFCatalog(Path("./mcp_catalog"))

# Search systems
systems = catalog.search_systems("postgres")  # By name/tag
all_systems = catalog.search_systems("*")     # All systems

# Search tools
tools = catalog.search_tools()                # All tools
postgres_tools = catalog.search_tools(system_id="postgres")

# Get metadata
cost_profile = catalog.get_cost_profile("search_customers")

# Find relationships
relationships = catalog.find_relationships("postgres-prod")

# Save new document
catalog.save_document(
    doc_type="mcp-system",
    title="New System",
    content="# New System\nDescription here",
    metadata={"tags": ["new"]}
)

# Reload from disk
catalog.reload()
```

### OKFQueryPlanner

```python
from pystreammcp.okf_query_planner import OKFQueryPlanner

planner = OKFQueryPlanner(catalog)

# Cheapest path
plan = planner.find_cheapest_path("objective")

# Fastest path
plan = planner.find_fastest_path("objective")

# Balanced optimal path
plan = planner.find_optimal_path(
    "objective",
    cost_weight=0.5,
    latency_weight=0.3,
    relevance_weight=0.2
)

# Custom plan generation
plan = planner.generate_plan(
    objective="find data",
    system_constraint="postgres",  # Optional: specific system
    max_cost=0.10                    # Optional: budget
)

# Inspect plan
for step in plan.steps:
    print(step.system_name, step.tool_name, f"${step.cost}")

print(f"Total: ${plan.total_cost}, {plan.total_latency_ms}ms")
```

---

## Advanced Usage

### Integration with Agents

```python
from pystreammcp.okf_core import OKFCatalog
from pystreammcp.okf_query_planner import OKFQueryPlanner

# Agent can navigate OKF directly
catalog = OKFCatalog(Path("./mcp_catalog"))
planner = OKFQueryPlanner(catalog)

# Agent reasons over OKF documents
objective = extract_agent_goal()  # From agent prompt
plan = planner.find_optimal_path(objective)

# Execute plan
execute_query_plan(plan)

# Store results
save_plan_results(plan, results)
```

### Custom System Profiles

```python
exporter = DiscoveryOKFExporter(catalog)

# Export with custom metadata
exporter.export_system(
    system_id="custom-api",
    name="Custom API Service",
    description="Internal service",
    tools_count=10,
    cost_per_query=0.005,
    latency_p99_ms=200,
    metadata={
        "tags": ["api", "internal"],
        "owner": "data-team",
        "sla_uptime": "99.9%",
        "rate_limit": "1000 req/min"
    }
)
```

### Linking Systems

```python
# Create system interconnection
catalog.save_document(
    doc_type="system-linkage",
    title="Postgres to BigQuery",
    content="# Data Pipeline\nSync every 6 hours",
    metadata={
        "source_system": "postgres-prod.md",
        "target_system": "bigquery.md",
        "relationship_type": "one-to-many",
        "sync_frequency": "6 hours",
        "data_freshness": "6-hour lag"
    }
)
```

---

## Testing

Run OKF tests:
```bash
python -m pytest tests/test_okf*.py -v
```

All tests should pass:
- `test_okf_core.py` — 16 tests
- `test_okf_discovery.py` — 8 tests
- `test_okf_query_planner.py` — 15 tests

---

## Migration Guide

### From In-Memory Registry to OKF

**Before:**
```python
# Discovery stored in memory
registry = DiscoveryEngine().discover()
planner.use_registry(registry)  # Transient
```

**After:**
```python
# Discovery exported to persistent OKF
catalog = OKFCatalog(Path("./mcp_catalog"))
exporter = DiscoveryOKFExporter(catalog)
exporter.export_systems(discovered_systems)

# Query planner reads from OKF
planner = OKFQueryPlanner(catalog)
```

---

## Limitations & Future Work

**Current (v0.1):**
- ✅ System and tool metadata
- ✅ Cost profiles
- ✅ Query plan generation
- ✅ Basic linking

**Planned (v0.5+):**
- Semantic versioning for schemas
- Cross-project linking (to PyVectorHound diagnostics)
- Automatic cost calculation from usage patterns
- WebMCP-specific optimizations

---

## Contributing

OKF documents are git-friendly! Submit improvements:

1. Edit system/tool `.md` files
2. Update metadata in frontmatter
3. Commit and push
4. Catalog auto-syncs on `reload()`

Example PR: "Improve PostgreSQL cost estimates based on Q3 usage data"

---

## References

- **Google OKF Spec:** https://github.com/GoogleCloudPlatform/knowledge-catalog
- **PyStreamMCP Docs:** https://github.com/Mullassery/PyStreamMCP
- **OKF Format Guide:** See strategic rationale document
