# PyStreamMCP v0.3 — Architectural Boundaries

**Principle:** Each tool owns its domain. No duplication. Clear interfaces.

---

## Domain Ownership

### PyVectorHound — Retrieval Forensics

**Owns:** Understanding and fixing retrieval problems

- ✅ Measure retrieval quality (precision, recall, F1, NDCG, MRR)
- ✅ Debug failures (8-failure taxonomy)
- ✅ Analyze root causes
- ✅ Suggest optimizations
- ✅ Replay failed queries with variants

**PyStreamMCP uses:** Call PyVectorHound APIs when retrieval quality is low

```python
# PyStreamMCP:
if retrieval_precision < 0.7:
    analysis = pyvectorhound.analyze(query, retrieved, ideal)
    optimizations = analysis.suggest_fixes()
    # Apply suggestions
else:
    proceed_with_retrieval()
```

**PyStreamMCP does NOT:** Rebuild forensics, duplicate taxonomy, re-analyze failures

---

### StatGuardian — Schema & Lineage Truth

**Owns:** Data landscape knowledge

- ✅ Schema validation
- ✅ Lineage tracking and versioning
- ✅ Change detection (schema, lineage)
- ✅ Drift detection
- ✅ Quality scoring
- ✅ Impact assessment

**PyStreamMCP uses:** Query StatGuardian APIs for knowledge memory

```python
# PyStreamMCP Knowledge Memory:
schema = statguardian.get_schema("customers_enriched")
lineage = statguardian.get_lineage("customers_enriched")
quality = statguardian.get_quality("customers_enriched")
impact = statguardian.get_impact_chain("customers_enriched")
```

**PyStreamMCP does NOT:** Rebuild schema validation, rebuild lineage tracking, duplicate drift detection

---

### PyStreamMCP — Agent Memory & Orchestration

**Owns:** Intelligent agent execution

- ✅ Working memory (current task state)
- ✅ Episodic memory (query history, patterns, outcomes)
- ✅ Execution history (what did we do?)
- ✅ Loop detection (are we stuck?)
- ✅ Budget tracking (tokens remaining?)
- ✅ Workflow orchestration (multi-step tasks)
- ✅ Learning (improve over time)

**Does NOT own:**
- ❌ Retrieval quality metrics (PyVectorHound)
- ❌ Schema validation (StatGuardian)
- ❌ Lineage graphs (StatGuardian)
- ❌ Drift detection (StatGuardian)

---

## Integration Architecture

### Layer 1: Data Input

```
PyVectorHound    StatGuardian
(Retrieval API)  (Lineage API)
     ↓               ↓
┌─────────────────────────────┐
│ PyStreamMCP Integration     │
│                             │
│ • Call PyVectorHound for    │
│   retrieval forensics       │
│                             │
│ • Call StatGuardian for     │
│   schema + lineage          │
└─────────────────────────────┘
```

### Layer 2: Memory System

```
┌─────────────────────────────────────────┐
│ PyStreamMCP Memory (owns this)          │
│                                         │
│ Working Memory:                         │
│ ├─ Current query state                 │
│ ├─ Active schema subset (from stat)    │
│ ├─ Intermediate results                │
│ └─ Token budget                        │
│                                         │
│ Episodic Memory:                       │
│ ├─ Query history                       │
│ ├─ Execution patterns                  │
│ ├─ Outcome feedback                    │
│ └─ Cost estimates                      │
│                                         │
│ Knowledge Memory (synced from stat):    │
│ ├─ Schemas                             │
│ ├─ Lineage graphs                      │
│ ├─ Quality scores                      │
│ └─ Impact chains                       │
└─────────────────────────────────────────┘
```

### Layer 3: Optimization

```
┌─────────────────────────────────────────┐
│ PyStreamMCP Optimization (owns this)    │
│                                         │
│ Execution History:                      │
│ ├─ Track API calls (never repeat)      │
│ └─ Cache results within session        │
│                                         │
│ Loop Detection:                         │
│ ├─ Detect retry patterns               │
│ ├─ Stop when stuck                     │
│ └─ Escalate (ask for help)            │
│                                         │
│ Reasoning Collapse:                     │
│ ├─ Unified schema analysis             │
│ ├─ Combined transformation planning    │
│ └─ Infer relationships from lineage    │
│                                         │
│ Budget Awareness:                       │
│ ├─ Track tokens used/remaining         │
│ ├─ Predict operation costs             │
│ └─ Adjust strategy (normal/cautious)   │
└─────────────────────────────────────────┘
```

### Layer 4: Agent Interface

```
┌──────────────────────────────┐
│ Agent (uses PyStreamMCP)      │
│                              │
│ Doesn't know about:          │
│ ├─ Memory internals          │
│ ├─ Optimization layers       │
│ ├─ Integration plumbing      │
│                              │
│ Calls:                       │
│ └─ query(task)               │
│    → Get answer (optimized)  │
└──────────────────────────────┘
```

---

## No Duplication Rules

### Rule 1: Retrieval Quality

**If PyVectorHound already measures precision/recall/F1/NDCG:**
- ❌ PyStreamMCP should NOT reimplement these
- ✅ PyStreamMCP should CALL PyVectorHound for metrics
- ✅ PyStreamMCP should STORE these metrics in episodic memory

```python
# PyStreamMCP Correct:
from pyvectorhound import RetrievalForensics

forensics = RetrievalForensics()
metrics = forensics.measure_precision_recall(query, retrieved, ideal)

episodic_memory.save_metrics(metrics)
```

**Not:**
```python
# PyStreamMCP Incorrect (duplication):
def compute_precision_myself(retrieved, ideal):
    return len(retrieved & ideal) / len(retrieved)

# Don't do this - PyVectorHound already does it
```

---

### Rule 2: Lineage Tracking

**If StatGuardian already tracks lineage:**
- ❌ PyStreamMCP should NOT track its own lineage
- ✅ PyStreamMCP should QUERY StatGuardian's lineage
- ✅ PyStreamMCP should CACHE StatGuardian's lineage in working memory

```python
# PyStreamMCP Correct:
from statguardian import get_lineage_graph

graph = get_lineage_graph(warehouse_config)
working_memory.load_lineage(graph)

# Use it for optimization
for table in query_tables:
    upstream = graph.get_upstream(table)
    downstream = graph.get_downstream(table)
```

**Not:**
```python
# PyStreamMCP Incorrect (duplication):
class LineageTracker:
    def build_lineage_myself():
        # Don't do this - StatGuardian already does it
        pass
```

---

### Rule 3: Schema Validation

**If StatGuardian already validates schemas:**
- ❌ PyStreamMCP should NOT validate schemas itself
- ✅ PyStreamMCP should CALL StatGuardian for validation
- ✅ PyStreamMCP should STORE validation results

```python
# PyStreamMCP Correct:
from statguardian import validate_schema

validation = validate_schema(schema, contract)
working_memory.schema_status = validation.status
```

**Not:**
```python
# PyStreamMCP Incorrect (duplication):
def validate_schema_myself(schema):
    # Don't do this - StatGuardian already does it
    pass
```

---

### Rule 4: Drift Detection

**If StatGuardian already detects drift:**
- ❌ PyStreamMCP should NOT detect drift
- ✅ PyStreamMCP should QUERY StatGuardian for drift status
- ✅ PyStreamMCP should USE drift info to invalidate cache

```python
# PyStreamMCP Correct:
from statguardian import detect_drift

drift = detect_drift(table, baseline_stats, current_stats)

if drift.severity == "HIGH":
    working_memory.invalidate_schema_cache(table)
```

**Not:**
```python
# PyStreamMCP Incorrect (duplication):
def detect_drift_myself(table, stats1, stats2):
    # Don't do this - StatGuardian already does it
    pass
```

---

## API Boundaries

### PyVectorHound API (PyStreamMCP calls)

```python
from pyvectorhound import RetrievalForensics

forensics = RetrievalForensics()

# Measurement
precision = forensics.measure_precision(retrieved, ideal)
recall = forensics.measure_recall(retrieved, ideal)
f1 = forensics.measure_f1(precision, recall)
ndcg = forensics.measure_ndcg(retrieved, ideal)
mrr = forensics.measure_mrr(retrieved, ideal)

# Debugging
analysis = forensics.analyze(query, retrieved, ideal)
root_causes = analysis.root_causes  # 8-failure taxonomy
suggestions = analysis.suggestions  # Fixes to try

# Replay
variants = [
    {"query_rewrite": "with_synonyms"},
    {"ranking_boost": "business_tables"},
]
results = forensics.replay(failed_query, variants)
best = results.max_by_precision()
```

### StatGuardian API (PyStreamMCP calls)

```python
from statguardian import (
    get_lineage_graph,
    get_lineage_version,
    detect_lineage_changes,
    get_schema,
    validate_schema,
    detect_drift,
    get_quality_score,
)

# Lineage
graph = get_lineage_graph(warehouse_config)
upstream = graph.get_upstream("customers_enriched")
downstream = graph.get_downstream("customers_enriched")
impact = graph.get_impact_chain("customers_raw")

# Schema
schema = get_schema("customers_enriched")
validation = validate_schema(schema, contract)

# Quality
quality = get_quality_score("customers_enriched")
propagated_quality = get_quality_through_lineage("customer_metrics")

# Changes
changes = detect_lineage_changes(v1=5, v2=6)
drift = detect_drift(table, baseline, current)
```

### PyStreamMCP API (Agents call)

```python
from pystreammcp import MemoryAwareAgent

agent = MemoryAwareAgent(
    warehouse_config=config,
    token_budget=100_000,
)

# Agent doesn't know about internal optimization
result = agent.query("Top customers by revenue in APAC")

# Result comes optimized:
# ✓ Retrieved with high precision (via PyVectorHound)
# ✓ Cached from episodic memory if available (via PyStreamMCP)
# ✓ No loops or redundancy (via PyStreamMCP)
# ✓ Within budget (via PyStreamMCP)
```

---

## Data Flow (No Duplication)

```
Query: "Top customers by revenue"
  ↓
PyStreamMCP Agent Interface
  │
  ├─→ Check execution history: "Already done?" 
  │   (PyStreamMCP ownership)
  │
  ├─→ Need retrieval? Call PyVectorHound
  │   quality.measure_precision(retrieved)
  │   (PyVectorHound ownership)
  │
  ├─→ Need schema? Query StatGuardian
  │   get_schema("customers")
  │   get_lineage("customers")
  │   (StatGuardian ownership)
  │
  ├─→ Cache in working memory
  │   (PyStreamMCP ownership)
  │
  ├─→ Execute query with optimized context
  │   (Agent responsibility)
  │
  ├─→ Save to episodic memory
  │   (PyStreamMCP ownership)
  │
  └─→ Return optimized result
```

---

## Forbidden Patterns (Duplication)

| Task | Tool | PyStreamMCP | Why Not |
|------|------|-------------|---------|
| Measure retrieval quality | PyVectorHound | ❌ Don't rebuild | Already exists |
| Debug retrieval failures | PyVectorHound | ❌ Don't rebuild | Already exists |
| Track lineage | StatGuardian | ❌ Don't rebuild | Already exists |
| Validate schemas | StatGuardian | ❌ Don't rebuild | Already exists |
| Detect drift | StatGuardian | ❌ Don't rebuild | Already exists |
| Manage memory | PyStreamMCP | ✅ Own it | Unique to agents |
| Detect loops | PyStreamMCP | ✅ Own it | Unique to execution |
| Budget tracking | PyStreamMCP | ✅ Own it | Unique to orchestration |

---

## Benefits of Clear Boundaries

1. **No Duplication**
   - Each tool excels at its domain
   - No competing implementations
   - Easier to maintain

2. **Composability**
   - PyStreamMCP works with ANY retrieval backend (as long as PyVectorHound debugs it)
   - PyStreamMCP works with ANY data source (as long as StatGuardian validates it)
   - Tools combine seamlessly

3. **Upgradability**
   - If PyVectorHound improves retrieval measurement, PyStreamMCP benefits automatically
   - If StatGuardian improves lineage tracking, PyStreamMCP benefits automatically
   - No need to update PyStreamMCP code

4. **Testability**
   - PyVectorHound tested independently
   - StatGuardian tested independently
   - PyStreamMCP only tested for orchestration

5. **Reusability**
   - PyVectorHound usable by other tools
   - StatGuardian usable by other tools
   - PyStreamMCP usable for other agents

---

## Summary

**PyStreamMCP is the orchestration layer that combines:**
- PyVectorHound (retrieval quality)
- StatGuardian (lineage knowledge)
- Custom memory (agent state)
- Custom optimization (autonomous execution)

**It does NOT rebuild any of their functionality.**

**Result:** Modular, maintainable, composable, upgradable architecture.
