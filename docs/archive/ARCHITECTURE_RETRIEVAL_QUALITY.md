# PyStreamMCP v0.3 — Retrieval Quality Platform

**Concept:** Integrated retrieval debugger (via PyVectorHound) to measure and improve retrieval precision.

**Date:** 2026-07-17  
**Status:** ARCHITECTURE DESIGN (LOCKED)  
**Priority:** P0 CRITICAL (foundation for all other improvements)  
**Vision:** Retrieval precision drives everything else — 20% to 80% = massive cost savings

---

## The Retrieval Quality Problem

### Current (❌ Inefficient)

```
Agent query: "Top 5 customers by lifetime revenue in APAC region"

Poor retrieval (20% precision):
  Retrieved context:
  ├─ customers schema ✓ (relevant)
  ├─ products schema ✗ (irrelevant)
  ├─ suppliers schema ✗ (irrelevant)
  ├─ orders schema ✓ (relevant)
  ├─ vendor pricing ✗ (irrelevant)
  ├─ payments schema ✓ (relevant)
  ├─ inventory ✗ (irrelevant)
  ├─ logistics ✗ (irrelevant)
  ├─ regions schema ✓ (relevant)
  └─ marketing ✗ (irrelevant)
  
  Result: 8K tokens of irrelevant context out of 10K total
  Model wastes effort filtering noise
  Answer quality: 60%
  Confidence: Low
  Cost: High (long context window)
```

### Proposed (✅ Efficient)

```
Same query with quality retrieval (80% precision):
  Retrieved context:
  ├─ customers schema ✓ (relevant)
  ├─ orders schema ✓ (relevant)
  ├─ payments schema ✓ (relevant)
  ├─ regions schema ✓ (relevant)
  └─ revenue_metrics table ✓ (relevant)
  
  Result: 5K tokens of relevant context only
  Model focus on signal (no filtering noise)
  Answer quality: 95%
  Confidence: High
  Cost: 50% lower (shorter context + better reasoning)
```

### The Math

```
Scenario: 100 daily analytics queries

With 20% retrieval precision:
  ├─ Context tokens per query: 10K (mostly noise)
  ├─ Model re-reading noise: 8K of wasted tokens
  ├─ Query tokens: 100 queries × 10K = 1M tokens/day
  └─ Cost: $5/day = $1,825/year

With 80% retrieval precision:
  ├─ Context tokens per query: 5K (mostly signal)
  ├─ Model focus on relevant: 4K useful tokens
  ├─ Query tokens: 100 queries × 5K = 500K tokens/day
  └─ Cost: $2.50/day = $912.50/year

Result:
  ├─ Token reduction: 50% (1M → 500K)
  ├─ Cost savings: $912.50/year
  ├─ Answer quality: 60% → 95%
  └─ Confidence: Low → High
```

**Key insight:** Retrieval precision is more impactful than caching.

A 60% precision improvement saves **more tokens** and **improves quality** better than any cache.

---

## Retrieval Quality Platform Architecture

### Layer 1: RETRIEVAL MEASUREMENT

Measure what we're actually retrieving:

```python
class RetrievalQualityMeter:
    """Measure retrieval precision, recall, MRR, NDCG"""
    
    def measure_retrieval(self, query, retrieved_context, ideal_context):
        """
        Compare what we retrieved vs. what was needed
        """
        
        metrics = {
            # Precision: Of what we retrieved, how much was relevant?
            "precision": len(retrieved & ideal) / len(retrieved),
            # Recall: Of what should have been retrieved, did we get it?
            "recall": len(retrieved & ideal) / len(ideal),
            # F1: Harmonic mean of precision and recall
            "f1": 2 * (precision * recall) / (precision + recall),
            # MRR: Mean Reciprocal Rank (how soon did we get first relevant?)
            "mrr": 1 / (rank_of_first_relevant + 1),
            # NDCG: Normalized Discounted Cumulative Gain (ranking quality)
            "ndcg": compute_ndcg(retrieved, ideal),
        }
        
        return metrics
    
    def categorize_retrieval_failure(self, failure_type):
        """What went wrong?"""
        
        failures = {
            "MISSING_RELEVANT": "Required table not retrieved",
            "RANK_TOO_LOW": "Relevant table ranked too far down",
            "IRRELEVANT_NOISE": "Non-relevant tables polluting context",
            "TYPE_MISMATCH": "Retrieved wrong type of entity",
            "CONTEXT_TOO_SMALL": "Retrieved too few relevant items",
            "EMBEDDING_MISMATCH": "Query embedding didn't match relevant tables",
        }
        
        return failures[failure_type]
```

---

### Layer 2: RETRIEVAL DEBUGGING (PyVectorHound Integration)

Use PyVectorHound to understand **why** retrieval failed:

```python
class RetrievalDebugger:
    """Use PyVectorHound to debug retrieval failures"""
    
    def debug_failed_retrieval(self, query, failed_retrieval_result):
        """
        When retrieval precision is low, forensically analyze why
        """
        
        # Use PyVectorHound to instrument the retrieval
        from pyvectorhound import RetrievalForensics
        
        forensics = RetrievalForensics()
        
        # Failure taxonomy (from PyVectorHound v1.0)
        failure_analysis = forensics.analyze(
            query=query,
            retrieved=failed_retrieval_result,
            debug_level="DEEP"  # Full forensics
        )
        
        # Results breakdown:
        root_causes = failure_analysis.root_causes
        # [
        #   {
        #       "cause": "EMBEDDING_MISMATCH",
        #       "query_embedding_issue": "Query encoded as 'product pricing' not 'revenue'",
        #       "missing_table": "revenue_metrics",
        #       "reason": "Table name doesn't contain query keywords",
        #       "severity": "HIGH"
        #   },
        #   {
        #       "cause": "IRRELEVANT_NOISE",
        #       "noisy_table": "products",
        #       "why_retrieved": "Shares 'revenue' column with relevant tables",
        #       "can_filter": True,
        #       "filter_rule": "NOT table_category='products'"
        #   }
        # ]
        
        return failure_analysis
    
    def extract_retrieval_patterns(self, past_failures):
        """
        Aggregate failures to find patterns
        (from PyVectorHound's 8-failure taxonomy)
        """
        
        patterns = {
            "EMBEDDING_MISMATCH": [],  # Query encoding issues
            "RANK_COLLAPSE": [],       # Relevant but ranked low
            "NOISE_POLLUTION": [],     # Irrelevant items retrieved
            "MISSING_SYNONYM": [],     # Query uses different words
            "CONTEXT_FRAGMENTATION": [], # Info split across tables
            "SCHEMA_AMBIGUITY": [],    # Multiple tables could match
            "TEMPORAL_MISMATCH": [],   # Outdated schema retrieved
            "SEMANTIC_DRIFT": [],      # Context evolved, embeddings didn't
        }
        
        for failure in past_failures:
            for root_cause in failure.root_causes:
                patterns[root_cause.cause].append(failure)
        
        return patterns
```

---

### Layer 3: RETRIEVAL OPTIMIZATION

Once we know **why** retrieval fails, **fix it**:

```python
class RetrievalOptimizer:
    """Improve retrieval precision based on forensics"""
    
    def optimize_retrieval(self, failure_patterns):
        """
        Generate fixes for each failure type
        (Uses PyVectorHound insights)
        """
        
        optimizations = {}
        
        # Pattern 1: Embedding mismatch → Improve query encoding
        if failure_patterns["EMBEDDING_MISMATCH"]:
            optimizations["query_rewriting"] = {
                "action": "Rewrite query with synonyms",
                "example": "Query: 'Top customers' → 'Top clients/accounts by lifetime value'",
                "impact": "Precision: 40% → 65%",
            }
        
        # Pattern 2: Rank collapse → Adjust retrieval ranking
        if failure_patterns["RANK_COLLAPSE"]:
            optimizations["ranking_adjustment"] = {
                "action": "Boost business-critical tables in ranking",
                "example": "revenue_metrics table: +boost factor of 2.0",
                "impact": "Recall: 60% → 90%",
            }
        
        # Pattern 3: Noise pollution → Add filters
        if failure_patterns["NOISE_POLLUTION"]:
            optimizations["context_filtering"] = {
                "action": "Filter out irrelevant table categories",
                "example": "Exclude tables: [products, suppliers, inventory]",
                "impact": "Context size: 10K → 5K tokens",
            }
        
        # Pattern 4: Missing synonyms → Enhance schema metadata
        if failure_patterns["MISSING_SYNONYM"]:
            optimizations["schema_enrichment"] = {
                "action": "Add business synonyms to table names",
                "example": "customers → ['clients', 'accounts', 'users']",
                "impact": "Embedding match rate: 70% → 95%",
            }
        
        # ... (6 more patterns)
        
        return optimizations
```

---

### Layer 4: RETRIEVAL FEEDBACK LOOP

Continuously improve based on real results:

```python
class RetrievalLearningLoop:
    """Learn what works and what doesn't"""
    
    def record_retrieval_outcome(self, query, retrieved, actual_result_quality):
        """
        After query execution, record what retrieval quality correlated with good results
        """
        
        episodic_memory.save_retrieval_event({
            "query": query,
            "retrieved_context": retrieved,
            "retrieval_metrics": {
                "precision": 0.65,
                "recall": 0.72,
                "f1": 0.68,
            },
            "actual_result_quality": actual_result_quality,  # 0-1
            "model_confidence": 0.85,
            "user_feedback": "helpful",  # or "not helpful"
            "timestamp": now(),
        })
    
    def extract_retrieval_patterns(self):
        """
        Find correlation between retrieval quality and result quality
        """
        
        retrieval_events = episodic_memory.query_retrieval_events(
            time_window="last_7_days"
        )
        
        correlations = {
            "precision_vs_quality": pearsonr(
                [e.retrieval_metrics.precision for e in retrieval_events],
                [e.actual_result_quality for e in retrieval_events]
            ),  # Expected: 0.85+ (high correlation)
            
            "context_size_vs_quality": pearsonr(
                [len(e.retrieved_context) for e in retrieval_events],
                [e.actual_result_quality for e in retrieval_events]
            ),  # Expected: low (context size doesn't matter if precise)
            
            "f1_score_threshold": percentile(
                [e.retrieval_metrics.f1 for e in retrieval_events],
                threshold=80  # Top 20% of retrieval quality
            ),  # E.g., 0.78 F1 score guarantees 90%+ result quality
        }
        
        # Use these to set thresholds and optimize
        return correlations
    
    def auto_tune_retrieval(self, correlations):
        """
        Automatically adjust retrieval to maximize result quality
        """
        
        # If correlation shows F1 > 0.78 → 90% quality
        # Then: Target F1 > 0.78 for all queries
        
        if correlations["precision_vs_quality"] > 0.8:
            # Precision is the key metric
            retrieval.set_optimization_target("maximize_precision")
        
        if correlations["context_size_vs_quality"] < 0.2:
            # Context size doesn't matter (precision does)
            retrieval.set_context_limit_based_on("precision", not "size")
```

---

## Integration with PyStreamMCP v0.3

### How Retrieval Quality Enhances Memory System

```
Knowledge Memory (from StatGuardian)
    ↓
    Query: "Top customers by revenue"
    ↓
RETRIEVAL QUALITY CHECK:
├─ Measure: Precision, recall, NDCG
├─ Debug (PyVectorHound): Why did it fail?
├─ Optimize: Adjust query, ranking, filters
└─ Learn: What precision guarantees good results?
    ↓
Working Memory (improved schema subset)
├─ Only relevant tables loaded
├─ High-confidence context
├─ Minimal noise
└─ 80% precision context
    ↓
Agent gets better context
└─ Shorter, more focused
└─ Better reasoning
└─ Higher confidence
```

### Architecture Integration

```
┌─────────────────────────────────────────┐
│ AGENT QUERY                              │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│ KNOWLEDGE MEMORY                        │
│ (Schemas, lineage from StatGuardian)   │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│ RETRIEVAL QUALITY PLATFORM              │
│                                          │
│ 1. Measure:                             │
│    • Precision, Recall, F1, NDCG       │
│    • Context quality metrics            │
│                                          │
│ 2. Debug (PyVectorHound):               │
│    • Root cause analysis                │
│    • 8-failure taxonomy                │
│    • Pattern extraction                 │
│                                          │
│ 3. Optimize:                            │
│    • Query rewriting                    │
│    • Ranking adjustment                 │
│    • Context filtering                  │
│    • Schema enrichment                  │
│                                          │
│ 4. Learn:                               │
│    • Correlation analysis               │
│    • Auto-tuning                        │
│    • Threshold setting                  │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│ WORKING MEMORY (Optimized)              │
│                                          │
│ • Only 80% precision context            │
│ • Short, focused, relevant              │
│ • High confidence                       │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│ AGENT REASONING                         │
│                                          │
│ • Less noise to filter                  │
│ • Faster reasoning                      │
│ • Higher confidence                     │
└─────────────────────────────────────────┘
```

---

## Retrieval Quality Metrics

### Primary Metrics

| Metric | Meaning | Target |
|--------|---------|--------|
| **Precision** | % of retrieved that was relevant | >80% |
| **Recall** | % of relevant that was retrieved | >85% |
| **F1** | Harmonic mean (balance both) | >0.80 |
| **NDCG** | Quality of ranking order | >0.75 |
| **MRR** | Speed to first relevant result | >0.80 |

### Secondary Metrics

| Metric | Meaning | Target |
|--------|---------|--------|
| **Context Length** | Tokens in retrieved context | <6K |
| **Signal/Noise Ratio** | Relevant vs irrelevant tokens | >4:1 |
| **Embedding Quality** | How well query encodes | >0.85 cosine |
| **Ranking Quality** | % of top-K that's relevant | >75% |

### Outcome Metrics

| Metric | Meaning | Target |
|--------|---------|--------|
| **Result Quality** | User perception of answer | >90% helpful |
| **Model Confidence** | Model's certainty | >85% |
| **Token Efficiency** | Tokens per unit quality | <50 tokens/unit |
| **Cost per Query** | Model + retrieval cost | <$0.02 |

---

## PyVectorHound Integration Points

### 1. Failure Analysis

```python
from pyvectorhound import RetrievalForensics

forensics = RetrievalForensics()
analysis = forensics.analyze(
    query="Top customers by revenue in APAC",
    retrieved_context=schemas_retrieved,
    ideal_context=schemas_needed,
    debug_level="DEEP"
)

# Returns: Root causes from 8-failure taxonomy
# - EMBEDDING_MISMATCH: Query encoded wrong
# - RANK_COLLAPSE: Relevant but ranked low
# - NOISE_POLLUTION: Irrelevant items included
# - MISSING_SYNONYM: Synonym not in schema
# - CONTEXT_FRAGMENTATION: Info split across tables
# - SCHEMA_AMBIGUITY: Multiple matches
# - TEMPORAL_MISMATCH: Outdated schema
# - SEMANTIC_DRIFT: Context evolved
```

### 2. Replay Analysis

```python
# Replay failed queries to understand patterns
replay_results = forensics.replay(
    failed_queries=episodic_memory.get_low_precision_queries(),
    variants=[
        {"query_rewrite": "with_synonyms"},
        {"ranking_boost": "business_tables"},
        {"context_filter": "exclude_products"},
    ]
)

# Measure which variant improved precision
best_variant = replay_results.max_by_precision()
# Apply to production
```

### 3. Cost Attribution

```python
# Understand what retrieval failures cost
cost_impact = forensics.cost_analysis(
    failure_pattern="IRRELEVANT_NOISE",
    daily_queries=100,
    context_cost_per_token=0.0005,
)

# "Irrelevant noise costs $2/day in wasted context tokens"
# "Fixing this saves $730/year"
```

---

## Implementation in v0.3

### New Components

1. **python/pystreammcp/retrieval/quality_meter.py** (250 lines)
   - RetrievalQualityMeter
   - Precision, recall, F1, NDCG, MRR computation
   - Metric tracking

2. **python/pystreammcp/retrieval/debugger.py** (300 lines)
   - RetrievalDebugger (PyVectorHound integration)
   - Forensic analysis
   - Pattern extraction

3. **python/pystreammcp/retrieval/optimizer.py** (350 lines)
   - RetrievalOptimizer
   - Query rewriting
   - Ranking adjustment
   - Context filtering
   - Schema enrichment

4. **python/pystreammcp/retrieval/learning_loop.py** (250 lines)
   - RetrievalLearningLoop
   - Outcome recording
   - Pattern extraction
   - Auto-tuning

### Modified Components

- **knowledge_memory.py** — Add retrieval quality check before returning context
- **working_memory.py** — Use optimized, high-precision context only
- **episodic_memory.py** — Store retrieval quality metrics alongside queries

---

## Impact on Token Economics

### Before: With Poor Retrieval (20% precision)

```
100 queries/day × 10K tokens (80% noise) = 1M tokens/day = $5/day
```

### After: With Quality Retrieval (80% precision)

```
100 queries/day × 5K tokens (80% signal) = 500K tokens/day = $2.50/day

Plus:
- Better model reasoning (no filter noise): -20% tokens
- Shorter context needed: -40% tokens
- Higher confidence (less re-checking): -15% tokens

Total savings: 50-75% token reduction
Cost: $2.50/day → $0.75/day = $274/year (vs $1,825)
```

**Savings: $1,551/year just from retrieval quality**

And:
- Answer quality improves 60% → 95%
- Model confidence increases 50% → 85%
- User satisfaction increases

---

## Success Criteria

✓ Retrieval precision measured accurately (correlation with PyVectorHound ±2%)  
✓ Failure patterns identified (all 8 types detected)  
✓ Optimizations effective (precision improvement 20% → 80% documented)  
✓ Feedback loop working (precision improves 5% per week)  
✓ Cost impact measurable (savings tracked and verified)  
✓ Integration seamless (agent gets better results transparently)  

---

## Summary

**Retrieval quality is the foundation.**

Memory, caching, and optimization all sit on top of retrieval. If retrieval is poor (20% precision), nothing else matters — you're feeding the model noise.

With PyVectorHound integration:
- **Measure** what you're actually retrieving
- **Debug** why it's not working (8-failure taxonomy)
- **Optimize** systematically (query, ranking, filters, schema)
- **Learn** from outcomes (auto-tuning)

Result: **50-75% token reduction + 35% quality improvement + $1,500+/year savings**

This should be **the first layer of PyStreamMCP v0.3**, before memory, caching, or anything else.
