# PyStreamMCP Roadmap (v0.3 → v1.0+)

**The Selective Intelligence Layer for AI Agents**

**PRIMARY MISSION:** Retrieve minimal data of highest contextual value using metadata-driven filtering and intelligent caching.

**Core Principle:** Never retrieve more than necessary. Decide at metadata level (not data level) what to fetch, from where, and whether to fetch at all.

**Applies to:** Web searches, database queries, MCP tool invocations, cached results, and all external sources.

Vision: Become the standard pre-retrieval intelligence layer that filters with metadata, caches decisions, and orchestrates minimal-yet-comprehensive context for agent reasoning.

---

## Integration Architecture

PyStreamMCP orchestrates intelligence across:
- **OpenAnchor** (cost insights) — Cost attribution guides query planning
- **StatGuardian** (quality gates) — Data quality prevents garbage context
- **PyTokenCalc** (token counting) — Accurate token budgets
- **Agent Frameworks** (LangChain, AutoGen, etc.) — Hook into reasoning loops
- **Data Systems** (Postgres, Snowflake, Elasticsearch) — Context discovery

---

## Release Timeline

### ✅ v0.1.0 (February 2026) — FOUNDATION
**Status:** Complete

**Core Features:**
- ✅ Query planning (Retrieve, Discover, Aggregate, Synthesize, Analyze)
- ✅ Token budget enforcement
- ✅ Context discovery (relevance + freshness ranking)
- ✅ Cost optimization (6 strategies: caching, summarization, sampling, pruning, compression, async)
- ✅ Early termination (stop when confident)
- ✅ Basic latency/confidence constraints

**Tests:** 18 unit, 27 integration

---

### ✅ v0.2.0 (April 2026) — DISCOVERY & OPTIMIZATION
**Status:** Complete

**Core Features:**
- ✅ Multi-source discovery (databases, APIs, caches, knowledge bases)
- ✅ Automatic relevance ranking (semantic + statistical)
- ✅ Token budget allocation across sources
- ✅ Async parallel context fetching
- ✅ Quality scoring (completeness, freshness, relevance)
- ✅ Cost estimation per source

**Tests:** 35 unit, 40 integration

---

### ✅ v0.3.0 (June 2026) — STABILIZATION & FIRST INTEGRATIONS
**Status:** Complete

**Features:**

1. **OpenAnchor Bridge** (v0.1 integration)
   - Receive cost/quality insights from openAnchor
   - Query plan adjusts based on observed cost patterns
   - Bidirectional: PyStreamMCP token budgets inform OpenAnchor governance
   - Cost feedback loop: learn which queries are expensive

2. **Query Plan Validation**
   - Pre-flight feasibility checks
   - Latency prediction (data retrieval + LLM response)
   - Cost prediction accuracy
   - Token budget adherence verification

3. **Caching Strategy**
   - Identify repeatable patterns (same queries often asked)
   - Suggest caching layer (Redis, DuckDB)
   - Cost-aware cache eviction
   - TTL optimization (cache staleness vs cost)

4. **Error Recovery**
   - Fallback plans (if primary source unavailable)
   - Partial context assembly (incomplete but useful)
   - Graceful degradation under budget constraints

**Tests:** 45 unit, 52 integration  

---

### ✅ v0.4.0 (July 2026, Released) — QUALITY GATES & OKF NATIVE
**Status:** Complete (Production Ready)

**Features:**

1. **StatGuardian Quality Gates**
   - Validation before retrieval (check schema/format)
   - Validation of retrieved context (ensure quality)
   - Confidence scoring (is this data usable?)
   - Fallback triggers (quality too low, try alternative source)

2. **OKF Native Support** (NEW)
   - System metadata as portable markdown (git-tracked)
   - Agent-native tool discovery
   - Cost transparency in OKF documents
   - Community-driven catalog improvements
   - 39+ OKF tests

3. **Cost + Quality Tradeoff**
   - Pareto frontier: optimal quality at given cost budget
   - User preferences: "prefer quality over cost" vs "prefer speed"
   - Automatic recommendation engine

4. **Agent-Aware Optimization**
   - Per-agent token budgets
   - Tool-call cost tracking (which agents are expensive?)
   - Multi-step reasoning optimization
   - Caching across agent steps

**Tests:** 58 unit, 65 integration, 39 OKF integration

---

### 🔵 v0.5.0 (September-October 2026, 8 weeks) — METADATA FILTERING FOUNDATION
**Status:** Planned (Q4 2026)
**Dependencies:** statguardian 2.3+

**Scope:** Build metadata-driven filtering layer. Enable selective retrieval across web, databases, and MCP tools. Core mission: minimal data, maximum value.

**Foundation Layers:**

1. **Metadata Filtering Engine** (CORE)
   - Metadata-first decision tree (decide what to retrieve *before* retrieving)
   - Candidate ranking by metadata (title, structure, freshness, domain authority, schema stats)
   - Filter candidates to top-1 or top-3 (not top-10)
   - Zero false negatives (never miss critical data)

2. **Metadata Caching System** (CORE)
   - Cache metadata about every source (URL, table, tool)
   - Cache filtering decisions ("for this query type, column X is always needed")
   - Cache relationship metadata (which columns link to which)
   - TTL-based invalidation (respect freshness guarantees)
   - Reuse across agents (share metadata learnings)

3. **Web Knowledge Foundation** (enables metadata filtering for web)
   - Web detector (temporal keywords, data freshness, confidence gaps)
   - SearXNG search (OSS, free, aggregates 10+ engines)
   - **Metadata extraction:** title, author, publish date, domain authority, word count, structure
   - **Selective crawling:** Crawl4AI only on highest-value URLs (top 1-3, not top-10)
   - Trafilatura cleaning (95%+ accuracy)
   - Domain reputation metadata in OKF catalog

4. **Database Discovery Foundation** (enables metadata filtering for structured data)
   - Discover databases in environment (connection strings, configs)
   - Extract schema metadata (tables, columns, types, constraints)
   - Compute statistics (row counts, cardinality, update frequency)
   - Build relationship graph (foreign keys, inferred relationships)
   - Classification metadata (operational vs. analytical, domain type)

5. **MCP Tool Metadata** (enables filtering of tool candidates)
   - Tool registry: name, description, input/output types, cost, reliability
   - Tool capability metadata (what does it solve?)
   - Tool freshness metadata (when was it last used successfully?)
   - Filter tool candidates before invocation (not after)

6. **OKF Metadata Catalog** (NEW)
   - 50+ web domains with metadata (authority, freshness patterns)
   - 25+ database schema examples with entity descriptions
   - 20+ MCP tools with cost/reliability profiles
   - Community-driven: PRs to improve metadata quality

**Integration (Metadata-Driven):**
```
Agent Query
    ↓
Metadata Filter (question: "do we need external data?")
    ├→ Check cache (have we solved this before?)
    └→ Check local freshness (is our local data fresh enough?)
    ↓
IF external retrieval needed:
    ├→ Metadata Filter (query type → best source type: web/db/tool?)
    ├→ Source Ranking (metadata only: no data retrieval yet)
    └→ Candidate Selection (top-1 or top-3, not top-10)
    ↓
Selective Retrieval (ONLY what metadata says is valuable)
    ├→ Web: Crawl only top-1 URLs (not top-10)
    ├→ DB: Query only necessary columns (not full table scan)
    └→ Tools: Invoke only highest-confidence tool (not all)
    ↓
Result + Cache Metadata (decisions for reuse)
    ↓
Context (minimal, high-value, audit trail in OKF)
```

**Tests:** 35 unit, 35 integration (total 105+ tests)
**Deliverables:**
- `core/src/metadata/` — Metadata filtering engine + cache
- `core/src/web/` — Web metadata extraction + selective crawling
- `core/src/database/` — Database discovery + schema metadata
- `core/src/mcp/` — MCP tool metadata registry
- `python/pystreammcp/metadata/` — Python bindings
- `mcp_catalog/metadata/` — Metadata profiles for web domains, DB schemas, MCP tools
- Docker: optional SearXNG + metadata sidecar
- Docs: "Metadata Filtering Architecture" guide
- Backward compatible: opt-in via config

**Impact:** Every retrieval (web/db/tool) now decides at metadata level, reducing unnecessary data transfer by 70-85%.

**No Breaking Changes:** Existing queries unaffected. Metadata filtering opt-in.

---

### 🟠 v1.0.0 (November-January 2026-27, 10 weeks) — SELECTIVE INTELLIGENCE CORE
**Status:** Planned (Q4 2026 - Q1 2027)
**Dependencies:** statguardian 2.3+, openanchor 1.0+, PyTokenCalc 1.0+

**Scope:** Production-grade metadata filtering across web, databases, and MCP tools. Core mission: minimal context of maximum value.

**Features:**

1. **Intelligent Metadata Filtering** (CORE)
   - Pre-retrieval filtering: decide what to fetch before fetching
   - Source selection via metadata: choose 1 DB table instead of 10
   - Column selection via metadata: query only necessary columns
   - Tool selection via metadata: invoke best tool instead of all tools
   - Cache metadata decisions: reuse across agents + query sessions

2. **Web Selective Retrieval** (Production)
   - Metadata ranking: filter candidates by title/domain/freshness (no crawling)
   - Selective crawling: Crawl4AI only top-1 or top-3 URLs (not top-10)
   - StatGuardian WebSourceValidator (pre-flight + post-retrieval)
   - Confidence scoring per source (0-1)
   - Fallback chains: if primary source fails, try ranked alternatives
   - Smart caching: cache crawled pages + metadata decisions (70% cache hit)

3. **Database Selective Retrieval** (NEW)
   - Metadata-only source selection: use statistics, no table scan
   - Column selection: query only high-value columns (not `SELECT *`)
   - Row sampling: use cardinality + relevance to limit rows
   - Relationship awareness: follow only necessary foreign keys
   - StatGuardian validation: pre-flight schema checks, post-retrieval quality
   - Freshness metadata: track which tables are stale

4. **MCP Tool Selective Invocation** (NEW)
   - Tool metadata registry: capabilities, cost, reliability, freshness
   - Pre-filtering: eliminate low-confidence candidates before invocation
   - Parallel invocation: call top-2 candidates, use first-to-respond
   - Cost tracking: associate tool invocation costs with source metadata
   - Fallback chains: if primary tool fails, invoke ranked backup
   - StatGuardian validation: pre-flight tool capability checks

5. **Knowledge Merging & Weighting** (Metadata-Aware)
   - Merge local + web + database results with confidence scores
   - Metadata-driven weighting: newer sources, higher authority get priority
   - Deduplication: consolidate same-entity results (customer_id matches)
   - Temporal scoring: combine recency signals from all sources
   - Audit trail: why each source was chosen (metadata justification)

6. **Cost Optimization (Metadata-Level)**
   - Track retrieval costs per metadata decision (in OpenAnchor)
   - Identify expensive metadata patterns ("queries needing web always cost $0.15")
   - Learn: "for this query type, always check cache first" (metadata caching ROI)
   - Selective caching: cache high-value metadata + decision histories
   - Predict: estimate cost at metadata level (before retrieval)

7. **Multi-Source Context Sharing** (Metadata-Driven)
   - Shared metadata cache: all agents benefit from learned patterns
   - TTL-based metadata invalidation (respect freshness guarantees)
   - Cross-agent learning: "Agent A's query pattern helps Agent B's filtering"
   - Fair allocation: metadata-driven quota enforcement (no single agent monopolizes)

8. **Enterprise Observability (OTel)**
   - Trace every metadata decision: why filter this candidate? why skip this column?
   - Lineage: which metadata decisions led to this context?
   - Cost breakdown: metadata queries vs. actual data retrieval costs
   - Latency: metadata filtering overhead vs. retrieval savings
   - Audit: full decision history for compliance + debugging

**Integration with Ecosystem (Metadata-Driven):**
```
Multi-Agent System with Queries
    ↓
PyStreamMCP (v1.0) — Selective Intelligence Layer
    ├→ Metadata Filter (CORE): "What data do we need? Where is it best? Cache decision.")
    ├→ Query Planning (via metadata, not data)
    ├→ Selective Retrieval (web/database/tools guided by metadata)
    ├→ OpenAnchor (v1.0): metadata-level cost tracking + learning
    ├→ StatGuardian (v2.3): metadata + quality validation (pre + post)
    ├→ PyTokenCalc (v1.0): accurate token estimates from metadata
    ├→ PyVectorHound (debugging: "why this source? what metadata guided the choice?")
    ├→ PyStreamDocuments (metadata-driven ingestion strategy)
    └→ Web + Databases + MCP Tools (metadata-first selection)
    ↓
Shared Metadata Cache (across all agents + sessions)
    ↓
Observability: OTel traces (metadata decisions → retrieval → validation → context)
    ↓
Minimal + High-Value Context Window
    ↓
LLM Response (70-85% data reduction via metadata filtering, maintained quality)
```

**Key Innovation:** Metadata is now first-class, shared, cached, and learned-from. Every retrieval decision is justified by metadata, auditable, and reusable.

**Tests:** 85+ unit, 95+ integration (total 200+ tests)
**Deliverables:**
- Full API reference (metadata filtering + retrieval APIs)
- Integration examples (Langchain, AutoGen, Pydantic AI)
- Kubernetes deployment guide + YAML
- Performance benchmarks: data reduction (70-85% fewer rows/columns)
- Metadata filtering tuning guide
- Cost analysis: metadata decision vs. data retrieval ROI

**Stability:** Production-ready, stable API contract. Metadata filtering is core capability.

**Success Metrics (v1.0) — Focus on Data Minimization:**
- 70-85% reduction in retrieved data size (vs. naive retrieval)
- Metadata filtering accuracy >95% (no loss of critical information)
- Metadata cache hit rate >70% (queries benefit from prior decisions)
- Pre-retrieval metadata latency <50ms (decisions fast, before data transfer)
- Confidence scoring >0.8 correlation with manual assessment
- Zero false negatives (never miss critical data due to filtering)
- Latency improvement: 40-60% faster (due to selective retrieval)
- Cost improvement: 50-70% lower (fewer APIs, fewer data transfers)
- 200+ metadata profiles (web domains, DB schemas, MCP tools)
- 0 breaking changes (backward compatible)

---

### 📋 v1.1.0 (Q4 2026+) — ADVANCED INTELLIGENCE
**Stretch Goals** (contingent on adoption):

1. **Multi-Agent Orchestration**
   - Coordinate token budgets across multiple agents
   - Fair-share allocation (no single agent hogs budget)
   - Dependency tracking (agent A's output feeds agent B)

2. **Causal Query Analysis**
   - Which sources actually influenced the final answer?
   - Trace information flow through reasoning steps
   - Remove irrelevant context (shorten windows)

3. **Knowledge Graph Reasoning**
   - Query patterns learnable from KG structure
   - Suggest optimal retrieval paths
   - Avoid redundant hops

4. **Predictive Sampling**
   - Estimate sufficiency (do we have enough context?)
   - Stop querying early if confidence high enough
   - Improve latency + cost simultaneously

---

## Cross-Project Dependencies & Data Flows

### v0.3 (Current)
```
PyStreamMCP (v0.3)
    ↓
OpenAnchor (v0.1): "GPT-4 cost is $0.30 per query"
    ↓
PyStreamMCP learns: adjust retrieval cost estimates
```

### v0.4 (August)
```
Agent Query
    ↓
PyStreamMCP (v0.4) query planner
    ├→ OpenAnchor: "cost/quality tradeoff"
    ├→ StatGuardian: "pre-flight validation"
    └→ PyTokenCalc: "token budget available"
    ↓
Optimized Query Plan
    ├→ Retrieve context (cost-aware)
    ├→ StatGuardian: validate retrieved data
    └→ Assemble window (quality + cost optimized)
    ↓
LLM (with budget enforcement from OpenAnchor)
```

### v1.0 (October)
```
Multi-Agent System
    ↓
PyStreamMCP (v1.0) orchestrator
    ├→ OpenAnchor (v1.0): enterprise cost governance
    ├→ StatGuardian (v2.3): OTEL quality metrics
    ├→ PyTokenCalc (v1.0): unified token counting
    └→ Agent Framework: hooks + tracing
    ↓
Observability: OTEL traces show query→retrieve→LLM→response flow
```

---

## Success Metrics

| Milestone | Metric | Target |
|-----------|--------|--------|
| v0.3 | OpenAnchor integration tests | 8+ |
| v0.4 | StatGuardian bridge tests | 10+ |
| v1.0 | Production deployments | 2+ |
| v1.0 | Token reduction (avg) | 50-70% |
| v1.0 | Latency improvement | 30-50% |

---

## Critical Path Items

1. **v0.3 → v0.4 transition:** StatGuardian 2.2 must be stable before PyStreamMCP v0.4 starts. Currently on track.

2. **v0.4 → v1.0 transition:** OpenAnchor 1.0 must have enterprise features before PyStreamMCP v1.0. Target dates align.

3. **v1.0 dependency chain:** All three projects reach v1.0 ~October 2026. Synchronized release is critical.

---

## Notes

- **v0.3 is stabilization month** — Once OpenAnchor integration works, v0.4 can proceed confidently.
- **v0.4 unlocks the "quality + cost" dual optimization** — This is the unique differentiation vs generic RAG tools.
- **v1.0 requires all three projects (OpenAnchor, PyStreamMCP, StatGuardian) at maturity** — Schedule them together.
- **Beyond v1.0:** Multi-agent orchestration (v1.1) is the next frontier, requiring all three at v1.0+ stability.
