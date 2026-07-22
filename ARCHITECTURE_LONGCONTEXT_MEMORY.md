# PyStreamMCP v0.3 — Long-Context Intelligence Layer

**Concept:** Persistent memory architecture for data agents that eliminates repeated context feeding.

**Date:** 2026-07-17  
**Status:** ARCHITECTURE DESIGN (LOCKED)  
**Priority:** P0 (Fundamental redesign)  
**Vision:** Agents maintain three persistent memory systems instead of re-processing information

---

## Problem: Context Amnesia

### Current (❌ Inefficient)

```
Query 1: "What columns in customers?"
  → Agent re-reads schema (50K tokens)
  → Embeds query
  → Analyzes result
  → Returns answer

Query 2: "Top customers by revenue" (similar schema questions)
  → Agent re-reads same schema (50K tokens) ← WASTED
  → Re-embeds query
  → Re-analyzes same structure
  → Returns answer

Query 100: Same warehouse, same schema
  → Re-read schema (50K tokens) × 100 ← MASSIVE WASTE
  → 5M tokens total for schema re-reading alone
```

### Proposed (✅ Efficient)

```
Query 1: "What columns in customers?"
  → Working Memory: Load schema once (50K tokens)
  → Episodic Memory: Cache result ("columns: id, name, email, ...")
  → Knowledge Memory: Store lineage (customers_raw → cleaned → enriched)
  → Return answer (50K tokens)

Query 2-100: Same warehouse
  → Working Memory: Reuse schema (0 tokens, already loaded)
  → Episodic Memory: Query similar to Q1? Return cached result (10 tokens embedding check)
  → Knowledge Memory: Lineage already known
  → Return answer (10 tokens per query = 1K total instead of 5M)

Result: 99.8% token reduction through memory persistence
```

---

## Architecture: Three Memory Systems

### 1. WORKING MEMORY (Current Context)

**Purpose:** Active query execution state — what the agent is currently working on

**Stores:**
- Current query intent and embedding
- Active schema subset (only relevant tables)
- Current transformation chain
- Query results cache
- Temporary computation state

**Scope:** Per-query or per-agent-session
**Lifetime:** Duration of query execution (seconds to minutes)
**Size limit:** ~8K tokens (agent's available context window)

**Example:**
```python
working_memory = {
    "current_query": "Top customers by revenue in 2024",
    "query_embedding": [0.1, 0.2, ...],
    "active_tables": ["customers", "orders", "payments"],
    "active_lineage": {
        "customers_raw": → "customers_cleaned" → "customers_enriched",
        "orders_raw": → "orders_cleaned",
    },
    "intermediate_results": {
        "revenue_per_customer": [("cust_1", $100K), ...]
    },
    "token_budget_remaining": 6000
}
```

**Managed by:** Agent execution engine
**Populated from:** Episodic + Knowledge memory
**Updated:** Real-time during query

---

### 2. EPISODIC MEMORY (Experience History)

**Purpose:** Record what happened — queries, results, execution traces, and outcomes

**Stores:**
- Query history (what was asked, when, by whom)
- Query results with confidence scores
- Execution traces (which schemas used, which transformations ran, performance)
- Outcome evaluations (was the result correct? useful?)
- Temporal patterns (time-of-day, frequency, trends)

**Scope:** Per-agent or per-warehouse
**Lifetime:** Persistent (survives sessions, weeks/months of data)
**Size limit:** Queryable database (scales to millions of records)

**Schema:**
```sql
CREATE TABLE episodic_queries (
    query_id TEXT PRIMARY KEY,
    query_text TEXT,
    query_embedding VECTOR(1536),
    timestamp DATETIME,
    agent_id TEXT,
    warehouse_id TEXT,
    
    -- Result
    result_text TEXT,
    result_confidence FLOAT,
    execution_time_ms FLOAT,
    tokens_used INT,
    
    -- Outcomes
    was_useful BOOLEAN,
    user_feedback TEXT,
    similar_queries COUNT,
    
    -- Lineage
    tables_used JSON,
    transformations_applied JSON
);

CREATE INDEX idx_embedding ON episodic_queries(query_embedding);
CREATE INDEX idx_timestamp ON episodic_queries(warehouse_id, timestamp DESC);
CREATE INDEX idx_similarity ON episodic_queries(agent_id, query_embedding);
```

**Retrieval:**
```python
# Find similar past queries (semantic search)
similar = episodic.find_similar_queries(
    query_embedding=current_query_embedding,
    warehouse_id="snowflake_prod",
    time_window="last_7_days",
    min_confidence=0.85,
    limit=5
)
# Returns: [
#   (query="Top 10 customers", result="[(...)]", confidence=0.92),
#   (query="Revenue by customer segment", result="[(...)]", confidence=0.88),
#   ...
# ]
```

**Benefits:**
- Avoid re-computing similar queries
- Learn from past execution patterns
- Provide query suggestions
- Optimize future queries

**Temporal Dimension:**
- Same query at different times may have different results (data changed)
- Patterns: "queries about revenue peak on Fridays"
- Decay: older results less useful

---

### 3. KNOWLEDGE MEMORY (Semantic Understanding)

**Purpose:** Facts about the data landscape — what exists, how it relates, why it matters

**Stores:**
- Schema information (tables, columns, types, constraints)
- Table lineage and transformations (via StatGuardian)
- Data quality scores and drift history
- Business metadata (ownership, purpose, SLA)
- Relationships (which tables join, foreign keys)
- Data dictionary (column meanings, valid values)
- Cost information (query cost, table size, update frequency)

**Scope:** Per-warehouse (shared across all agents/queries)
**Lifetime:** Persistent (updated when schema changes)
**Size limit:** Complete warehouse knowledge graph

**Source of Truth:** StatGuardian v2.2 Lineage APIs
- get_lineage_graph() → full warehouse DAG
- get_impact_chain() → what breaks if this changes
- detect_lineage_changes() → what's new/removed
- get_quality_through_lineage() → quality propagation

**Schema:**
```sql
-- Synced from StatGuardian
CREATE TABLE knowledge_tables (
    table_id TEXT PRIMARY KEY,
    warehouse_id TEXT,
    database TEXT,
    schema_name TEXT,
    table_name TEXT,
    
    -- Metadata
    description TEXT,
    owner TEXT,
    sla_freshness_hours INT,
    
    -- Quality
    quality_score FLOAT,
    last_updated DATETIME,
    row_count INT,
    
    -- Cost
    monthly_query_cost FLOAT,
    avg_query_time_ms FLOAT
);

CREATE TABLE knowledge_lineage (
    source_table_id TEXT,
    target_table_id TEXT,
    transformation_name TEXT,
    transformation_sql TEXT,
    
    PRIMARY KEY (source_table_id, target_table_id)
);

CREATE TABLE knowledge_columns (
    table_id TEXT,
    column_name TEXT,
    column_type TEXT,
    description TEXT,
    is_key BOOLEAN,
    
    PRIMARY KEY (table_id, column_name)
);
```

**Agent Access:**
```python
# Query knowledge memory
schema = knowledge.get_table_schema("customers_enriched")
# → TableSchema(columns=[...], quality_score=0.95, owner="analytics-team")

lineage = knowledge.get_transformation_chain("customers_enriched")
# → [customers_raw, customers_cleaned, customers_enriched]

impact = knowledge.get_impact_chain("customers_raw")
# → [customers_cleaned, customers_enriched, customer_metrics]

quality = knowledge.get_quality_through_lineage("customer_metrics")
# → 0.92 (minimum of: raw=0.98, cleaned=0.95, enriched=0.94, agg=0.92)
```

**Updates:**
- Synced daily from StatGuardian
- Triggered on schema changes (lineage changes)
- Agent query feedback updates quality estimates

---

## Memory Interactions

### Working ← Episodic (Query Suggestion)

```python
# Agent formulating new query
working_memory.current_query = "Customer revenue trends Q1-Q4"

# Check episodic: have we answered similar?
suggestions = episodic.find_similar_queries(
    embedding=working_memory.current_query_embedding,
    limit=3
)

if suggestions[0].confidence > 0.90:
    # Use past result (might need re-execution if data changed)
    working_memory.suggested_result = suggestions[0].result
    working_memory.re_execute_needed = time_since(suggestions[0]) > 24h
```

### Working ← Knowledge (Context Loading)

```python
# Agent needs to work with "customers" table
working_memory.load_schema("customers_enriched")

# Knowledge memory provides:
schema = knowledge.get_table_schema("customers_enriched")
lineage = knowledge.get_upstream_tables("customers_enriched")
quality = knowledge.get_table_quality("customers_enriched")

working_memory.active_tables = [
    "customers_enriched",
    "customers_cleaned",  # Parent (upstream)
    "customer_metrics"     # Child (downstream)
]
working_memory.schema_context = {
    "tables": [schema for each table],
    "lineage": lineage,
    "quality_scores": [0.95, 0.98, 0.92],
}
```

### Episodic → Knowledge (Learning)

```python
# After query execution
episodic.save_query(
    query="Top 100 customers by lifetime value",
    result=result,
    tables_used=["customers_enriched", "orders_cleaned", "payments"],
    execution_time=1230,  # ms
    tokens_used=50000,
)

# If user says "that was useful"
episodic.add_feedback(query_id, was_useful=True)

# Knowledge memory learns:
# "This transformation chain is frequently useful"
# "Quality of this chain should be tracked more carefully"
```

### Episodic → Working (Optimization)

```python
# Agent sees pattern in episodic memory
patterns = episodic.extract_patterns(
    agent_id="analytics_agent_1",
    time_window="last_7_days"
)

# "Similar queries about customer revenue get asked ~20x/day"
# "Best result format: [customer_id, revenue, growth_rate]"
# "Optimal query time: early morning (before 9am) = 500ms"
# "Peak query time: 11am = 2000ms"

working_memory.optimize_execution(patterns)
```

---

## Token Economics Through Memory

### Without Memory (Current)

```
100 daily queries on Snowflake warehouse with 50K-token schema

Query 1: Schema (50K) + embed (5K) + analysis (20K) = 75K tokens
Query 2: Schema (50K) + embed (5K) + analysis (18K) = 73K tokens
Query 3-100: Same pattern

Total: 100 × 73K = 7,300K tokens/day
Cost: $36.50/day = $1,095/month = $13,140/year
```

### With Memory (Proposed)

```
Day 1:
  Query 1: Schema (50K) + embed (5K) + analysis (20K) = 75K tokens
           → Save to episodic (5K) + update knowledge (2K) = 7K

Queries 2-100 (same warehouse, similar patterns):
  Query 2: Working load (5K) + episodic search (8K) + similar-enough result
           → Return with re-execution check = 13K tokens
  Query 3: Similar (13K)
  ...
  Query 100: Similar (13K)

Day 1 Total: 75K + (99 × 13K) = 75K + 1,287K = 1,362K tokens
Cost Day 1: $6.81

Days 2-7 (episodic memory fully populated):
  Schema already in working/episodic (0K)
  Episodic hit rate: 80-90%
  
  Query 1: 10K (episodic hit + validation)
  Query 2-100: 8-10K each (cached + re-validate if needed)
  
Daily total: 100 × 9K = 900K tokens
Cost: $4.50/day

Weekly: $56.50 (vs $255.50 without memory)
Monthly: $226/month (vs $1,095)
Annual: $2,712 (vs $13,140)

Savings: 80% reduction in token cost
Result: Re-execution happens only when data actually changed
```

---

## Implementation Architecture

### Layer Stack

```
┌─────────────────────────────────────────────────────────┐
│ AGENT LAYER (User queries, prompt engineering)          │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│ WORKING MEMORY (Current execution state, 8K tokens)    │
│ ├─ Current query + embedding                            │
│ ├─ Active schema subset                                 │
│ ├─ Intermediate results                                 │
│ └─ Token budget tracking                                │
└────────────────┬────────────────────────────────────────┘
                 │
     ┌───────────┴───────────┬───────────┐
     │                       │           │
     ▼                       ▼           ▼
┌─────────────┐      ┌──────────────┐  ┌─────────────────┐
│ EPISODIC    │      │ KNOWLEDGE    │  │ OPTIMIZATION    │
│ MEMORY      │      │ MEMORY       │  │ ENGINE          │
│             │      │              │  │                 │
│ • Queries   │      │ • Lineage    │  │ • Pattern learn │
│ • Results   │      │ • Schemas    │  │ • Cost optimize │
│ • Traces    │      │ • Quality    │  │ • Predict perf  │
│ • Feedback  │      │ • Metadata   │  │                 │
└──────┬──────┘      └──────┬───────┘  └────────┬────────┘
       │                    │                   │
       └────────────────────┼───────────────────┘
                            │
        ┌───────────────────┴──────────────────┐
        │                                      │
        ▼                                      ▼
   ┌─────────────────────┐        ┌──────────────────────┐
   │ EPISODIC DATABASE   │        │ STATGUARDIAN v2.2    │
   │ (SQLite/PostgreSQL) │        │ (Knowledge Source)   │
   │                     │        │                      │
   │ • Query history     │        │ • Lineage graph      │
   │ • Similarity index  │        │ • Schema versions    │
   │ • Temporal patterns │        │ • Quality scores     │
   │ • User feedback     │        │ • Change detection   │
   └─────────────────────┘        └──────────────────────┘
```

### Component Breakdown

**Working Memory Manager:**
- Loads schema subsets on demand
- Manages token budget
- Tracks intermediate results
- Formats output

**Episodic Memory Manager:**
- Saves queries with embeddings
- Semantic search (similarity)
- Temporal queries (time-window)
- Pattern extraction
- Feedback collection

**Knowledge Memory Manager:**
- Syncs from StatGuardian lineage
- Updates on schema changes
- Provides lineage queries
- Quality propagation
- Impact analysis

**Optimization Engine:**
- Learns from episodic patterns
- Predicts query performance
- Suggests optimizations
- Cost tracking

---

## Memory Lifecycle: Example Query

### Query: "Top 10 customers by lifetime revenue"

**Step 1: Working Memory - Initialize**
```
working_memory = {
    current_query: "Top 10 customers by lifetime revenue",
    query_embedding: embed(query),  # 5K tokens
    token_budget: 8000,
}
```

**Step 2: Episodic Memory - Check History**
```
similar = episodic.find_similar_queries(
    query_embedding,
    time_window="last_7_days",
    min_confidence=0.88
)

if similar and not data_changed():
    # Use past result + light re-validation
    working_memory.result = similar[0].result
    working_memory.re_execute = False
    tokens_used: 8K (embedding + check)
    → Done, return answer
```

**Step 3: Knowledge Memory - Load Context**
```
If episodic miss or re-execution needed:

tables_needed = ["customers_enriched", "orders_cleaned", "payments"]

for table in tables_needed:
    schema = knowledge.get_schema(table)
    lineage = knowledge.get_lineage(table)
    quality = knowledge.get_quality(table)
    
working_memory.context = {
    schemas: [3 schemas],
    lineage: [transformation chains],
    quality_scores: [0.95, 0.92, 0.98],
}

tokens_used: 35K (schemas + lineage)
```

**Step 4: Query Execution**
```
Agent executes query against Snowflake with schema context

Discovers result: [("cust_1", $2.5M), ...]

Execution time: 1230ms
Tokens used in execution: 20K
```

**Step 5: Update Episodic Memory**
```
episodic.save_query(
    query_text: "Top 10 customers by lifetime revenue",
    query_embedding: embed(query),
    result: result,
    tables_used: ["customers_enriched", "orders_cleaned", "payments"],
    execution_time: 1230,
    tokens_used: 55K,  # 5K embed + 35K context + 15K execution
    confidence: 0.95,  # Based on data freshness
    timestamp: now()
)
```

**Step 6: Optimization Learning**
```
patterns = episodic.extract_patterns()

Learning:
- "Revenue queries have 0.85 cache hit rate"
- "Best executed at 2am (1000ms) vs peak time 11am (2500ms)"
- "90% of users want top-10 format"

→ Suggest to agent: "Cache revenue queries, batch at off-peak"
```

**Total Cost This Query:**
- Initial execution: 55K tokens
- Next similar query: 8K tokens (episodic hit)
- Savings: 85% reduction for cache hits

---

## Why This Matters for PyStreamMCP

### Before: Caching System
```
"Cache schemas to avoid re-reading"
→ Helps with Token reduction
→ But still re-processes similar patterns
```

### After: Memory System
```
"Agent maintains persistent memory of:
  - What it just did (working)
  - What it learned (episodic)
  - What it knows (knowledge)
→ Becomes smarter over time
→ Compounds token savings
→ Learns query patterns
→ Optimizes execution"
```

This is the difference between:
- **Caching:** Static token reduction (same hit rate)
- **Memory:** Dynamic intelligence (improving hit rate + learning optimizations)

---

## Success Metrics

### Token Reduction
- Working memory: 50-70% reduction (context reuse)
- Episodic memory: 70-90% reduction (cache hits)
- Knowledge memory: 60-80% reduction (selective loading)
- **Combined: 80-95% token reduction**

### Query Performance
- Episodic hits: <100ms (cached + validation)
- Knowledge lookups: <50ms (graph traversal)
- Working memory setup: <500ms (schema loading)
- Total latency: <1000ms for cache hits

### Learning
- Episodic hit rate: 70-85% after 100 queries
- Pattern accuracy: 80%+ after 1 week
- Cost prediction: ±10% after 1 month
- Query optimization suggestions: 5-10 per day

### Business Impact
- 80% token cost reduction
- Faster query execution (cached)
- Better query suggestions (episodic learning)
- Automatic optimization (pattern learning)
