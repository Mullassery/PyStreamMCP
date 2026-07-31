# PyStreamMCP MCP 2.0 Quick Start

> Intelligent multi-project orchestration layer. Ask Claude to discover MCP tools, plan queries, optimize execution, handle cross-database joins, and federate results.

## Installation

```bash
pip install PyStreamMCP>=0.3
```

## Basic Usage

```python
from pystreammcp import Orchestrator

# Create orchestrator
orchestrator = Orchestrator()

# Enable MCP (starts on port 8772, discovers 7 projects)
endpoint = orchestrator.start_mcp_connector()

# Claude can now:
# - "Discover all available MCP tools"
# - "Plan optimal query for data quality + segmentation"
# - "Join data from PrismNote and ClusterAudienceKit"
# - "Check which projects can do weather correlation"
# - "Optimize this query to reduce tokens by 70%"
# - "Execute federated query across all projects"
```

## 12 MCP Tools

1. `discover_mcp_projects` — Discover all 7 projects + 73 tools
2. `plan_query_execution` — Plan optimal multi-project query execution
3. `optimize_cross_project_query` — Reduce tokens by 60-75%
4. `execute_federated_query` — Execute across multiple projects
5. `detect_compatible_projects` — Find projects for capability
6. `rank_tools_by_relevance` — Rank tools by task match
7. `handle_cross_database_join` — Join heterogeneous databases
8. `cache_management` — Intelligent caching strategies
9. `error_recovery_retry` — Handle failures gracefully
10. `report_performance_metrics` — Get performance stats
11. `estimate_query_cost_multi_project` — Cost estimation
12. `manage_endpoint_federation` — Manage remote endpoints

## Connected Projects (Ports 8765-8771)

- **8765:** StatGuardian (9 tools) — Data Quality Validation
- **8766:** PyReverseETL (12 tools) — Data Activation
- **8767:** PrismNote (10 tools) — SQL Queries
- **8768:** ClusterAudienceKit (10 tools) — Customer Segmentation
- **8769:** PyWeatherEnriched (10 tools) — Weather Enrichment
- **8770:** PyTerrainMap (10 tools) — Fleet Terrain Intelligence
- **8771:** PyRoboFrames (11 tools) — ML Dataset Metadata

## Example Workflows

### Workflow 1: Data Pipeline Validation
```
"Validate data quality → Segment customers → Estimate sync volume → Sync to CRM"
Uses: StatGuardian → ClusterAudienceKit → PyReverseETL
Token Reduction: 72% (via PyStreamMCP optimization)
```

### Workflow 2: Revenue Intelligence
```
"Correlate revenue with weather → Find high-value segments → 
 Forecast impact → Calculate CLV"
Uses: PyWeatherEnriched → ClusterAudienceKit
Cost Reduction: 68% (via intelligent caching)
```

### Workflow 3: Fleet Operations
```
"Find unexplored terrain → Suggest optimal path → 
 Analyze sensors → Export dataset manifest"
Uses: PyTerrainMap → PyRoboFrames
Latency: 2.1s (via federated execution)
```

---

For full documentation, see [README.md](README.md)
