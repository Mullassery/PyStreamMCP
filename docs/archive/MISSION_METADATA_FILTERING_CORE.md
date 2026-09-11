# PyStreamMCP Core Mission: Selective Intelligence via Metadata Filtering

**Date:** July 2026  
**Status:** Mission Critical — Supersedes all other objectives

---

## The Repositioning

PyStreamMCP is **NOT** a query optimizer. It is **NOT** a cost reducer. It is **NOT** a latency improver.

PyStreamMCP is a **Selective Intelligence Engine.**

**Core Mission:** Retrieve **minimal data** of **highest contextual value** using **metadata-driven filtering** and **intelligent caching**.

---

## The Problem PyStreamMCP Solves

### Status Quo (Naive Retrieval)
```
Agent Query: "Best practices for customer retention"
    ↓
Search: Returns top-10 URLs
Crawl: Fetches all 10 pages (50KB each)
Extract: Keeps all 500KB
LLM: "Here's everything, sort it out"
    ↓
Result: High token usage, slow, noisy context
```

### PyStreamMCP Way (Two-Stage Filtering)
```
Agent Query: "Best practices for customer retention"
    ↓
STAGE 1: Metadata Filtering (Pre-Retrieval)
  "Which source has this? Is it already cached?"
    ↓
Selective Retrieval: Crawl only top-1 URL (2KB)
    ↓
STAGE 2: Contextual Reranking + Token Budget Filtering (Post-Retrieval)
  Extract all sections (10KB)
    ↓
  Rerank by context relevance: "Which 3 sections matter most for retention?"
    ↓
  Apply token budget: "We have 500 tokens for context"
    ↓
  Keep only absolute essentials: 3 key sections (1.5KB = 450 tokens)
    ↓
Result: Minimal context (450 tokens), high signal-to-noise, fast, cheap
```

**Improvement:** 95%+ data reduction + token efficiency, maintained quality, faster, cheaper.

---

## Two-Stage Selective Intelligence

### Core Pattern

```
Traditional System:
  Query → Fetch All Data → Analyze → Optimize

PyStreamMCP:
  Query
    ↓
  STAGE 1: Metadata Filtering (Pre-Retrieval)
    → Analyze METADATA
    → Fetch MINIMAL (top-1/3, necessary columns only)
    ↓
  STAGE 2: Contextual Reranking + Token Budget Filtering (Post-Retrieval)
    → Rerank retrieved data by context relevance
    → Filter by token budget (keep absolute essentials)
    → Result: Focused context within budget
```

This two-stage approach achieves **95%+ data reduction** while maintaining quality:
- Stage 1: 70-85% reduction (selective retrieval)
- Stage 2: Additional 70-80% reduction (contextual filtering)
- Combined: 90-95% total reduction

### What Is "Metadata"?

**For Web Searches:**
- URL, title, domain authority, publish date
- No need to crawl the page yet
- Metadata ranks candidates
- Fetch only if metadata is promising

**For Databases:**
- Table name, row count, update frequency, column types
- Statistics about distribution, cardinality, nulls
- No need to query yet
- Query only if metadata is necessary

**For MCP Tools:**
- Tool name, description, input/output types
- Success rate, cost, latency from history
- No need to invoke yet
- Invoke only if metadata indicates value

**For Cached Results:**
- What query was asked before?
- What context was retrieved?
- Is metadata still fresh?
- Skip retrieval entirely if cached answer applies

### Three Decisions Made at Metadata Level

1. **Do we need external data?**
   - Query + cache metadata answer
   - Skip retrieval if cache hit + fresh

2. **Where should we get it?**
   - Query type + metadata profiles
   - Rank candidates by metadata (not data)

3. **What's the minimal viable set?**
   - Query intent + metadata about sources
   - Select top-1 or top-3 (not all)
   - Query only necessary columns/sections (not all)

---

## Three Retrieval Sources, One Pattern

### 1. Web Retrieval (Metadata Filtering)

**Old:** SearXNG → Crawl top-10 URLs → Extract all → LLM

**New (Metadata-Driven):**
```
Query: "Latest GPU pricing trends"
    ↓
Metadata Ranking (no crawl):
- nvidia.com (authority 0.95, freshness high)
- tom's-hardware.com (authority 0.88, freshness high)
- random-blog.com (authority 0.3, freshness low)
    ↓
Filter Decision: Fetch nvidia.com + tom's-hardware (top-2)
    ↓
Selective Crawl: Only these 2 URLs, not 10
    ↓
Extract: Only GPU pricing sections (not entire page)
    ↓
Result: ~5KB final context vs. 500KB naive
```

**Metadata Cached:** "GPU pricing" queries → always check nvidia + tom's-hardware first

### 2. Database Retrieval (Metadata Filtering)

**Old:** SELECT * FROM tables → Analyze → Filter → LLM

**New (Metadata-Driven):**
```
Query: "Top customers by LTV in last quarter"
    ↓
Metadata Analysis (no scan):
- customers table: 500K rows, active/dormant signal
- orders table: 50M rows, linked by customer_id
- payments table: 80M rows, heavy, rarely needed
    ↓
Decision: Query only customers + orders, skip payments
Query only: customer_id, name, ltv, order_count (4 columns, not *)
Limit: 100 rows (high LTV) (not all 500K)
    ↓
Result: 100 rows × 4 columns vs. 500K rows × 50 columns
Reduction: 98%+ less data transferred
```

**Metadata Cached:** "LTV queries" → always prefer customers + orders, skip payments + payments_detail

### 3. MCP Tool Invocation (Metadata Filtering)

**Old:** Invoke all candidate tools → Wait for slowest → Use first response

**New (Metadata-Driven):**
```
Query: "What's the weather in San Francisco?"
    ↓
Tool Metadata Filtering:
- weather_api: cost $0.02, latency 200ms, success 99%
- bing_search: cost $0.01, latency 500ms, success 85%
- weather_tool (slow): cost $0.03, latency 1000ms, success 95%
    ↓
Filter Decision: Invoke only weather_api (highest value/cost ratio)
Skip: bing_search (high latency), weather_tool (high cost)
    ↓
Result: 200ms latency, $0.02 cost
vs. naive "invoke all": 1000ms latency, $0.06 cost
```

**Metadata Cached:** "Weather queries" → always use weather_api first, fall back to bing_search if timeout

---

## The Metadata Cache: Learning Over Time

### Tiered Token Budgets

The token budget filtering is applied in tiers based on query complexity:

```
Simple Query: "What is X?"
  ↓
Token Budget: Minimal (50-100 tokens)
  ↓
Reranking: Keep only definition + 1-2 key points
  ↓
Result: Concise answer (70 tokens)

---

Moderate Query: "How does X relate to Y?"
  ↓
Token Budget: Standard (500-1000 tokens)
  ↓
Reranking: Keep definition + relationships + examples
  ↓
Result: Comprehensive answer (800 tokens)

---

Complex Query: "Compare X and Y across dimensions A, B, C"
  ↓
Token Budget: Large (2000-3000 tokens)
  ↓
Reranking: Keep definitions + comparisons + evidence + tradeoffs
  ↓
Result: Detailed analysis (2400 tokens)

---

Very Complex Query: "Design system using X, Y, Z with constraints A, B, C"
  ↓
Token Budget: Comprehensive (5000+ tokens)
  ↓
Reranking: Keep everything relevant + trade-offs + alternatives + risks
  ↓
Result: Full context for reasoning (4800 tokens)
```

**How Tiering Works:**

1. **Query Complexity Detection** (heuristic)
   - Simple: "What is X?" (1-2 entities, no relationships)
   - Moderate: "How does X relate to Y?" (2-3 entities, 1-2 relationships)
   - Complex: "Compare X vs Y" (3+ entities, multiple comparisons)
   - Very Complex: "Design system" (5+ constraints, trade-offs)

2. **Token Tier Assignment**
   - Minimal (50-100): Definition queries, factual lookups
   - Standard (500-1000): Understanding, relationships, examples
   - Large (2000-3000): Analysis, comparisons, design decisions
   - Comprehensive (5000+): Multi-agent reasoning, complex workflows

3. **Contextual Reranking Within Tier**
   - Extract all relevant information
   - Rank by relevance to query intent
   - Keep items until token budget exhausted
   - Maintain highest-value items (never exclude critical info)

### Session 1
```
Query: "Best practices for customer retention" (Moderate Complexity)
Token Budget: Standard (500-1000)
    ↓
Metadata filtering: "Check web sources"
Result: Crawl TechCrunch (authority 0.9)
    ↓
Rerank: "Key practices, proven outcomes, implementation tips" (850 tokens)
```

### Session 2 (Same Agent, Different Query)
```
Query: "Retention strategies in SaaS" (Complex - comparing strategies)
Token Budget: Large (2000-3000)
    ↓
Metadata cache: "SaaS queries → TechCrunch + Stanford case studies"
Result: Reuse prior metadata + expand context window
    ↓
Rerank: "Strategies, why they work, trade-offs, metrics" (2600 tokens)
```

### Session 3 (Different Agent)
```
Query: "Design retention engine for our platform" (Very Complex)
Token Budget: Comprehensive (5000+)
    ↓
Metadata cache (shared): Benefits from Sessions 1 + 2 + other agents
Result: Reuse learned patterns + full context
    ↓
Rerank: "Requirements, strategies, implementation, risks, alternatives" (4800 tokens)
```

**Outcome:** Every query gets focused context at the right detail level, efficiently using token budget.

---

## Architecture: Two-Stage Intelligence

### v0.5 Foundation (Pre-Retrieval Only)

```
STAGE 1: Metadata Filtering Engine (Pre-Retrieval)
├── Metadata Discovery (find candidate sources)
├── Metadata Ranking (score by metadata)
├── Candidate Selection (top-1 or top-3)
└── Decision Caching (remember for next time)

Metadata Sources
├── Web Domains (50+ catalogs with authority, freshness)
├── Database Schemas (25+ with statistics, lineage)
└── MCP Tools (20+ with cost, reliability, success rate)
```

### v1.0 Production (Both Stages)

```
STAGE 1: Metadata Filtering Engine (Pre-Retrieval)
├── Metadata Discovery (find candidate sources)
├── Metadata Ranking (score by metadata)
├── Candidate Selection (top-1 or top-3)
└── Decision Caching (remember for next time)
    ↓
Selective Retrieval (fetch minimal)
    ↓
STAGE 2: Contextual Reranking + Token Budget Filtering (Post-Retrieval)
├── Content Extraction (segments, sections, fields)
├── Contextual Ranking (relevance to query intent)
├── Token Estimation (actual tokens per item)
├── Budget Enforcement (fit within token limit)
└── Essential Filtering (keep only highest-value items)
    ↓
Quality Validation (StatGuardian checks both stages)
    ↓
Shared Intelligence Cache (decisions + filtered context)
    ↓
OTel Tracing (audit both filtering stages)

Integrated Retrieval (all sources use both stages)
├── Web (SearXNG + Crawl4AI + Trafilatura)
├── Databases (PostgreSQL, MongoDB, BigQuery, etc.)
└── MCP Tools (any MCP-compatible service)
```

---

## Success Metrics (v1.0)

**NOT token reduction. NOT cost reduction. NOT latency.**

**YES: Data Minimization + Contextual Value Preservation + Budget Adherence**

| Metric | Target | Why |
|--------|--------|-----|
| **Data Reduction (Stage 1)** | 70-85% | Selective retrieval reduces data transferred |
| **Token Reduction (Stage 2)** | 70-80% | Contextual reranking + tier filtering |
| **Combined Reduction** | 90-95% | Two stages compound the reduction |
| **Tier Accuracy** | >90% | Correct complexity classification |
| **Budget Adherence** | 98%+ | Context fits within tier limit |
| **Filtering Accuracy** | >95% | No false negatives (never miss critical data) |
| **Metadata Cache Hit** | >70% | Decisions reused across queries |
| **Decision Latency** | <50ms | Metadata filtering fast |
| **Confidence Score** | >0.8 correlation | Filtering aligned with human judgment |
| **False Negative Rate** | <0.5% | Nearly impossible to filter away critical info |

---

## Implementation Roadmap

### v0.5 (Sep-Oct 2026, 8 weeks) — Metadata Foundation
- Metadata filtering engine
- Metadata caching system
- Web domain metadata (50+ profiles)
- Database schema metadata (25+ profiles)
- MCP tool metadata (20+ profiles)
- 35 unit + 35 integration tests

### v1.0 (Nov-Jan 2027, 10 weeks) — Selective Intelligence Core
- Selective web retrieval (top-1/3, not top-10)
- Selective database retrieval (only necessary columns + rows)
- Selective tool invocation (highest-value tool, not all)
- StatGuardian validation of metadata decisions
- Shared metadata cache (across agents)
- OTel tracing of decisions
- 85+ unit + 95+ integration tests

### v1.1+ (Beyond) — Advanced Patterns
- Learn optimal filtering from history
- Predict metadata changes
- Multi-step reasoning with metadata awareness
- Intelligent prefetching based on query patterns

---

## Why This Matters

### For Users/Agents
- Focused context (not drowning in data)
- Faster responses (metadata filtering + selective retrieval)
- Lower costs (no unnecessary API calls)
- Better quality (signal-to-noise is higher)

### For PyStreamMCP
- Unique positioning: "Selective Intelligence" vs. generic optimizers
- Strategic foundation for v1.1+ multi-agent coordination
- Integration point for web + databases + MCP tools
- OKF-exportable metadata enables community contribution

### For the Platform
- All downstream systems (StatGuardian, OpenAnchor, agents) get higher-quality inputs
- Metadata sharing enables cross-project optimization
- Foundation for enterprise governance (what metadata drove this decision?)

---

## Constraints & Commitments

1. **Zero false negatives:** Never filter away critical information
2. **Metadata-first:** Decide at metadata level, not after data retrieval
3. **Universally applicable:** Works uniformly for web, databases, MCP tools
4. **Cached and reused:** Every decision captured for future reuse
5. **Auditable:** Every retrieval justified by metadata (OTel traces show why)
6. **No breaking changes:** v0.5 → v1.0 fully backward compatible

---

## Strategic Value

PyStreamMCP with metadata filtering becomes the **intelligent acquisition layer** that:

- **Discovers** what data exists (web, databases, tools)
- **Understands** what it means (semantic inference)
- **Filters** to minimal viable set (metadata decisions)
- **Retrieves** only what's necessary (selective retrieval)
- **Caches** decisions for reuse (metadata learning)
- **Explains** every choice (audit trail)

This is different from:
- Query optimizers (optimize after fetching)
- RAG systems (retrieve everything, hope relevance ranking helps)
- Database tools (schema crawling, not semantic understanding)

This is **pre-retrieval intelligence**: understanding what to fetch before fetching.

---

## Next Steps

1. **Review** this mission statement
2. **Confirm** metadata filtering is the primary objective
3. **Allocate** v0.5 resources (metadata filtering engine + caching)
4. **Build** v0.5 foundation (Sep-Oct 2026)
5. **Integrate** v1.0 (Nov-Jan 2027)
6. **Measure** success by data minimization metrics (not token reduction)
