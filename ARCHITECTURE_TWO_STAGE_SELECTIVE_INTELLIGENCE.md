# PyStreamMCP v1.0 Architecture: Two-Stage Selective Intelligence

**Date:** July 2026  
**Core Mission:** Retrieve minimal data of highest contextual value within token budgets

---

## Two-Stage Pipeline

### Stage 1: Metadata Filtering (Pre-Retrieval)
**Objective:** Decide what to fetch BEFORE fetching

```
Query
  ↓
Analyze METADATA (no data retrieval)
  ├─ Metadata Discovery: Find candidate sources
  ├─ Metadata Ranking: Score by metadata (authority, freshness, cost, reliability)
  ├─ Candidate Selection: Choose top-1 or top-3 (not all)
  └─ Decision Caching: Remember for reuse
  ↓
Selective Retrieval (fetch ONLY selected candidates)
  ├─ Web: Crawl top-1 URL (not top-10)
  ├─ Database: Query only necessary columns (not *)
  └─ Tools: Invoke best tool only (not all)
```

**Reduction Factor:** 70-85% (fewer sources fetched)

### Stage 2: Contextual Reranking + Tiered Token Filtering (Post-Retrieval)
**Objective:** Keep ONLY what matters, fit within token budget

```
Retrieved Data
  ↓
Extract Content (all segments/sections/fields)
  ↓
Complexity Detection (is this simple/moderate/complex/very-complex query?)
  ↓
Apply Tiered Token Budget
  ├─ Minimal (50-100): Definition + 1 key point
  ├─ Standard (500-1000): Definition + 2-3 key points + examples
  ├─ Large (2000-3000): Full analysis + trade-offs
  └─ Comprehensive (5000+): Everything + alternatives
  ↓
Contextual Reranking (rank by relevance to query intent)
  ├─ Most relevant items first
  ├─ Keep until token budget exhausted
  └─ Maintain zero false negatives
  ↓
Quality Validation (StatGuardian checks both stages)
  ↓
Result: Focused context within budget, highest value
```

**Reduction Factor:** 70-80% (additional tokens removed)
**Combined Reduction:** 90-95% total

---

## Data Flow Example

### Query: "Best practices for customer retention"

**Complexity:** Moderate (understanding + examples)  
**Token Budget:** Standard (500-1000 tokens)

**Stage 1 Execution:**
```
Query metadata: "retention practices + examples + proven strategies"
  ↓
Candidate sources (metadata only):
- hbr.org (authority 0.95, freshness high, topic match high)
- techcrunch.com (authority 0.85, freshness high, topic match medium)
- random-blog.com (authority 0.3, freshness low)
  ↓
Selection: Fetch HBR only (top-1, metadata said best)
Crawl single URL: 8KB raw content
```

**Stage 2 Execution:**
```
Extracted content: 12 sections from HBR article
- Definition of retention (2KB)
- 7 proven strategies (15KB)
- Implementation steps (8KB)
- Metrics to track (3KB)
- Case studies (6KB)
- Conclusion (1KB)
  ↓
Complexity detected: MODERATE
Budget: STANDARD (500-1000 tokens)
Estimated: ~1200 tokens if all included
  ↓
Contextual reranking (by relevance):
1. Definition (100 tokens) ← INCLUDED
2. Top 3 strategies (400 tokens) ← INCLUDED
3. Metrics to track (150 tokens) ← INCLUDED
4. Implementation steps (300 tokens) ← EXCLUDED (would exceed budget)
5. Case studies (400 tokens) ← EXCLUDED
6. Conclusion (50 tokens) ← INCLUDED
  ↓
Final context: 650 tokens (within 500-1000 budget)
```

**Result:** 8KB fetched → 650 tokens final context → 92% reduction maintained quality

---

## Architecture Components

### 1. Complexity Classifier + Intent-Based Allocation (Stage 1 → 2)

Detects query complexity and allocates tokens within tier:

```python
class ComplexityClassifier:
    def classify(query: str) -> (Tier, TokenAllocation):
        """
        Step 1: Classify tier (hard boundary)
        - Simple: "What is X?" → Minimal (50-100)
        - Moderate: "How does X relate to Y?" → Standard (500-1000)
        - Complex: "Compare X vs Y across A, B, C" → Large (2000-3000)
        - VeryComplex: "Design system X with constraints" → Comprehensive (5000+)
        
        Step 2: Detect intent (flexible within tier)
        - Factual: Less detail needed (lower end of tier)
        - Conceptual: More explanation needed (mid-tier)
        - Detailed: Full analysis needed (high end of tier)
        - Comprehensive: Everything + alternatives (max tier)
        
        Result: Tier (hard limit) + Intent (allocation within tier)
        """
        
        # Tier detection (hard boundaries)
        features_tier = [
            word_count,              # >50 words = higher tier
            entity_count,            # >3 entities = higher tier
            relationship_count,      # >2 relationships = higher tier
            constraint_keywords,     # "compare", "trade-off", "optimize"
        ]
        tier = classify_tier(features_tier)  # Hard boundary
        
        # Intent detection (flexible allocation within tier)
        features_intent = [
            intent_keywords,         # "why", "how", "explain", "example"
            pronoun_usage,          # "our" = domain-specific, needs detail
            temporal_scope,         # "now", "next quarter" = recency focus
        ]
        intent = detect_intent(features_intent)  # Allocation flexibility
        
        # Combine: Tier is hard limit, intent adjusts within tier
        tier_budget = tier.token_range  # e.g., (500, 1000) for Standard
        intent_allocation = intent.adjust(tier_budget)  # e.g., 750 for balanced
        
        return (tier, intent_allocation)
```

**Key Design:**
- **Tier = Hard Boundary:** Standard tier always 500-1000, never exceeded
- **Intent = Flexible Allocation:** Within tier, intent guides token distribution
- **Example:**
  - Query: "Explain customer retention best practices" (Moderate tier)
  - Tier: Standard (500-1000 tokens, hard limit)
  - Intent: Explain (needs examples and detail)
  - Allocation: 750 tokens (lower-mid range, respects hard limit)

### 2. Tiered Token Budget System (Hard Limits, Intent-Based Allocation)

```python
class TokenBudgetTier:
    # Hard limits: Never exceeded
    # Intent allocation: Flexible within tier
    
    MINIMAL = {
        "tokens": (50, 100),                    # HARD LIMIT
        "use_cases": ["factual lookup", "definition"],
        "intent_allocation": {
            "factual": 50,                      # Definition only
            "conceptual": 75,                   # Definition + concept
            "detailed": 100,                    # Definition + examples
        }
    }
    
    STANDARD = {
        "tokens": (500, 1000),                  # HARD LIMIT
        "use_cases": ["understanding", "comparison"],
        "intent_allocation": {
            "factual": 500,                     # Key points only
            "conceptual": 750,                  # Key points + explanation
            "detailed": 1000,                   # Full with examples
        }
    }
    
    LARGE = {
        "tokens": (2000, 3000),                 # HARD LIMIT
        "use_cases": ["analysis", "design", "complex reasoning"],
        "intent_allocation": {
            "factual": 2000,                    # Analysis only
            "conceptual": 2500,                 # Analysis + alternatives
            "detailed": 3000,                   # Full analysis + trade-offs
        }
    }
    
    COMPREHENSIVE = {
        "tokens": (5000, 8000),                 # HARD LIMIT
        "use_cases": ["multi-agent reasoning", "full context"],
        "intent_allocation": {
            "factual": 5000,                    # Everything essential
            "conceptual": 6500,                 # Everything + risks
            "detailed": 8000,                   # Everything + future
        }
    }

    @staticmethod
    def allocate(tier: str, intent: str) -> int:
        """Returns token allocation within tier bounds."""
        tier_obj = TokenBudgetTier[tier]
        token_limit = tier_obj["tokens"]
        allocation = tier_obj["intent_allocation"].get(intent)
        assert token_limit[0] <= allocation <= token_limit[1], "Intent allocation must respect tier hard limits"
        return allocation
```

**Key Design:**
- **Tier is Hard Limit (with multiplier exception):** STANDARD tier caps at 1000, but can expand to 1500 with multipliers
- **Intent is Flexible:** Within tier, intent can allocate 500 (minimal) to 1000 (comprehensive)
- **Multipliers are Configurable:** Developers specify keywords that expand budget
- **Guarantee:** Every query respects its tier's token limit (or multiplier-adjusted ceiling)

### 3. Token Multiplier System (Developer-Configurable Keywords)

Developers can specify keywords that trigger token budget expansion:

```python
class TokenMultiplier:
    """
    Developers define keywords and multipliers.
    When query contains keywords, token budget expands accordingly.
    """
    
    def __init__(self):
        self.rules = {
            # Critical scenarios: 2x expansion
            "critical": 2.0,
            "emergency": 2.0,
            "urgent": 2.0,
            "production_incident": 2.0,
            "data_loss": 2.0,
            
            # Domain-specific needs: 1.5x expansion
            "financial": 1.5,
            "compliance": 1.5,
            "legal": 1.5,
            "security": 1.5,
            "medical": 1.5,
            
            # Debug/Analysis needs: 1.2x expansion
            "debug": 1.2,
            "troubleshoot": 1.2,
            "analyze": 1.2,
            "investigate": 1.2,
            "root_cause": 1.2,
        }
    
    def calculate_multiplier(self, query: str) -> float:
        """
        Scan query for multiplier keywords.
        Return highest multiplier found (max once per category).
        
        Example:
        "Emergency financial incident analysis"
        → Matches: emergency (2.0), financial (1.5), analyze (1.2)
        → Returns: 2.0 (take highest)
        """
        found_multipliers = []
        for keyword, multiplier in self.rules.items():
            if keyword.lower() in query.lower():
                found_multipliers.append(multiplier)
        
        return max(found_multipliers) if found_multipliers else 1.0

def allocate_with_multiplier(tier: str, intent: str, query: str) -> int:
    """
    Final allocation: tier × intent × multiplier
    Respects hard ceiling per tier.
    """
    base_allocation = TokenBudgetTier.allocate(tier, intent)  # e.g., 750
    multiplier = TokenMultiplier().calculate_multiplier(query)  # e.g., 2.0
    
    # Calculate expanded allocation
    expanded = base_allocation * multiplier  # e.g., 750 × 2.0 = 1500
    
    # Respect tier ceiling (with multiplier buffer)
    tier_max = TokenBudgetTier[tier]["tokens"][1]  # e.g., 1000 for STANDARD
    ceiling = tier_max * 2.0  # Allow up to 2x tier max for multipliers
    
    final_allocation = min(expanded, ceiling)
    
    return final_allocation

# Examples:
# Query: "Explain retention best practices"
#   → Tier: STANDARD, Intent: conceptual, Multiplier: 1.0
#   → Allocation: 750 tokens

# Query: "Emergency: Fix critical production customer retention bug"
#   → Tier: STANDARD, Intent: conceptual, Multiplier: 2.0 (critical)
#   → Allocation: 1500 tokens (expanded within ceiling)

# Query: "Analyze financial compliance impact of retention policy"
#   → Tier: STANDARD, Intent: detailed, Multiplier: 1.5 (financial)
#   → Allocation: 1500 tokens (1000 × 1.5)
```

**Key Design:**
- **Developers Configure Keywords:** Add custom multiplier rules per org/domain
- **Query Scan:** Check for keywords during complexity classification
- **Dynamic Expansion:** Token budget expands when keywords match
- **Ceiling Protection:** Max multiplier prevents runaway budgets
- **One Multiplier Per Query:** Take highest matching multiplier (don't stack)

---

### 4. Contextual Reranker

```python
class ContextualReranker:
    def rerank(content_items: List[ContentItem], query: Query, budget: int) -> List[ContentItem]:
        """
        Rerank items by relevance to query intent, respecting token budget.
        
        Scoring:
        - Semantic relevance (0-1): How well does this match query intent?
        - Informativeness (0-1): How much value does this add?
        - Uniqueness (0-1): Is this info in other items already?
        - Recency (0-1): Is this current?
        
        Token estimation: Accurate token count for each item
        
        Selection: Greedy algorithm—keep items until budget exhausted
        
        Guarantee: Never exclude critical information (false negative detection)
        """
```

### 4. Metadata Filtering Engine

```python
class MetadataFilter:
    def rank_candidates(query: Query, source_type: str) -> List[Candidate]:
        """
        STAGE 1: Pre-retrieval filtering using ONLY metadata
        
        For Web:
        - Domain authority (0-1 scale)
        - Content freshness (recency score)
        - Topic match (keyword overlap)
        - SSL/security score
        - Historical success rate (cached)
        
        For Database:
        - Table relevance (column name + cardinality match)
        - Data freshness (update frequency)
        - Access cost (indexed vs. full scan)
        - Data quality (null %, duplicates)
        
        For MCP Tools:
        - Capability match (input/output types)
        - Success rate (from history)
        - Cost (API calls, latency)
        - Reliability (error rate)
        
        Returns: Ranked candidates (top-1/3 selected)
        """
```

### 5. Shared Metadata Cache

```python
class MetadataCache:
    """
    Learn and reuse metadata filtering decisions across:
    - Sessions (same agent, different queries)
    - Agents (different agents, similar queries)
    - Time (patterns learned over days/weeks)
    """
    
    def cache_entry(query_pattern: str, best_source: str, tier_used: str):
        """
        Cache: "retention practices" → HBR always best → standard tier
        Reuse: Next "retention" query uses this cached decision
        Learn: Over time, build patterns (e-commerce queries → these 3 sources)
        """
```

### 6. Quality Validation (StatGuardian Integration)

```python
class StatGuardianValidator:
    """
    Stage 1 validation: Is metadata fresh and trustworthy?
    - Source authority checks (SSL, domain age, Wayback Machine)
    - Metadata consistency (do stats match reality?)
    
    Stage 2 validation: Is retrieved content quality high?
    - Content freshness (Last-Modified headers)
    - No paywall/403/410 (accessible content)
    - Language detection (correct language)
    - Noise detection (ads, boilerplate removed by Trafilatura)
    
    Result: Confidence score (0-1) + issues list
    """
```

---

## Integration Points

### With Web Knowledge Layer

```
Web Query
  ↓
STAGE 1: Metadata Filter
├─ SearXNG: Rank domains (metadata only)
├─ Select top-1 or top-3 URLs
└─ Crawl ONLY selected URLs
  ↓
Trafilatura: Extract content
  ↓
STAGE 2: Contextual Rerank + Token Filter
├─ Rerank sections by relevance
├─ Apply token budget tier
└─ Keep only essentials
  ↓
Quality Validation (StatGuardian)
  ↓
Result: Minimal, high-value web context
```

### With Database Discovery Layer

```
Database Query
  ↓
STAGE 1: Metadata Filter
├─ Schema analysis (no table scan)
├─ Select best tables by metadata
└─ Query only necessary columns
  ↓
Execute selective query
  ↓
STAGE 2: Contextual Rerank + Token Filter
├─ Rerank rows by relevance
├─ Apply token budget tier
└─ Keep only high-value rows
  ↓
Quality Validation (StatGuardian)
  ↓
Result: Minimal, high-value database context
```

### With MCP Tool Layer

```
Tool Needed
  ↓
STAGE 1: Metadata Filter
├─ Tool capability match
├─ Rank by reliability + cost
└─ Invoke only best tool
  ↓
Execute tool (single invocation)
  ↓
STAGE 2: Contextual Rerank + Token Filter
├─ Rerank tool output by relevance
├─ Apply token budget tier
└─ Keep only essentials
  ↓
Quality Validation (StatGuardian)
  ↓
Result: Minimal, high-value tool output
```

---

## Metadata Cache Strategy

### Learning Patterns Over Time

**Day 1:**
```
Query: "GPU pricing trends"
Filter decision: nvidia.com + tom's-hardware (search result #1, #2)
Context: 800 tokens (standard tier)
Result: Successful, high-quality answer
Cache: "gpu_pricing_trends" → [nvidia, tom's-hardware]
```

**Day 2:**
```
Query: "Latest GPU prices"
Metadata cache hit: nvidia.com + tom's-hardware
Decision latency: <10ms (vs. 300ms search)
Result: Same quality, faster, cheaper
```

**Day 5:**
```
Query: "GPU market analysis"
Metadata cache: "GPU queries" pattern learned
Auto-select: nvidia.com + tom's-hardware + anandtech.com
Decision: Automatic via learned pattern
Result: Higher quality (added deep-tech analysis)
```

**Week 2:**
```
New agent asks similar question
Shared cache: Benefits from Week 1 learnings
All agents faster and smarter
```

---

## Success Metrics for Two-Stage Pipeline

| Metric | Target | Measurement |
|--------|--------|------------|
| **Stage 1 Reduction** | 70-85% | Data fetched vs. all candidates |
| **Stage 2 Reduction** | 70-80% | Tokens in context vs. retrieved |
| **Combined Reduction** | 90-95% | Total tokens vs. naive retrieval |
| **Tier Accuracy** | >90% | Correct complexity classification |
| **Intent Detection** | >85% | Correct intent-based allocation within tier |
| **Multiplier Accuracy** | >95% | Correct keyword detection + expansion |
| **Budget Adherence** | 99%+ | Context within tier limit (or multiplier ceiling) |
| **Quality Preservation** | >95% | No loss of critical information |
| **Cache Hit Rate** | >70% | Metadata decisions reused |
| **Decision Latency** | <50ms | Stage 1 (metadata) filtering speed |
| **Multiplier ROI** | >0.8 correlation | Expanded budgets improve answer quality |
| **Confidence Score** | >0.8 | Alignment with manual assessment |
| **False Negatives** | <0.5% | Critical info never filtered away |

---

## Backward Compatibility

- v0.5 introduces Stage 1 (metadata filtering)
- Existing queries unaffected (opt-in via config)
- v1.0 adds Stage 2 (contextual reranking + tiered budgets)
- No breaking API changes
- Default: Both stages enabled for new queries

---

## Competitive Position

PyStreamMCP v1.0 with two-stage selective intelligence will be unique:

✅ **Pre-retrieval intelligence** (metadata filtering) — Most systems do post-retrieval only  
✅ **Post-retrieval intelligence** (contextual reranking) — Most systems dump all data  
✅ **Tiered budgets** — Adaptive to query complexity  
✅ **Cached learning** — Decisions improve over time  
✅ **Quality gates** (StatGuardian) — Validation at both stages  
✅ **Uniform across all sources** — Web, database, MCP tools  
✅ **Auditable** (OTel tracing) — Every decision explained  

---

## Example: End-to-End Flow

**User Query:** "How can we improve customer retention in our SaaS product?"

**Step 1: Complexity Classification**
- Entity count: 3 (SaaS, retention, product)
- Relationship count: 2 (improve → retention, retention → SaaS)
- Complexity: MODERATE → Standard tier (500-1000 tokens)

**Step 2: Source Selection (Metadata)**
- Web search: HBR (0.95) + SaaS blog (0.80) + startup guides (0.60)
- Database: retention metrics table + customer journey table
- Tools: Customer analytics tool + retention engine simulator
- Select: HBR (web) + retention metrics (DB) + analytics tool (MCP)

**Step 3: Selective Retrieval**
- Web: Crawl HBR article only (8KB)
- DB: Query `SELECT customer_id, churn_risk, tenure FROM retention_metrics LIMIT 1000` (not all)
- Tool: Invoke analytics tool (single invocation, not all candidates)

**Step 4: Content Extraction**
- Web: 12 sections extracted (leadership lessons, strategies, case studies, metrics)
- DB: 1000 rows × 3 columns (customer segments, risk scores, tenure distribution)
- Tool: 5 key insights + recommendations

**Step 5: Contextual Reranking (Stage 2)**

Within Standard tier (500-1000 tokens):

| Item | Type | Tokens | Relevance | Decision |
|------|------|--------|-----------|----------|
| Definition (retention strategy) | Web | 80 | 1.0 | INCLUDE |
| Top 3 proven strategies | Web | 320 | 0.95 | INCLUDE |
| Case study (Slack) | Web | 150 | 0.80 | INCLUDE |
| Implementation steps | Web | 200 | 0.85 | EXCLUDE (budget) |
| Metric recommendations | Tool | 80 | 0.95 | INCLUDE |
| Churn risk distribution | DB | 70 | 0.85 | INCLUDE |
| | | **900** | | |

**Step 6: Final Context**
```
900 tokens delivered:
- 3 proven retention strategies from HBR
- Implementation metrics to track
- Current churn risk distribution
- Analytics insights
- Why each item was selected (metadata justification)
```

**Value Delivered:**
- 90%+ data reduction (50KB → 900 tokens)
- 100% quality (no false negatives)
- Full auditability (why each item?)
- Reusable metadata cache (future "retention" queries faster)

---

## Deployment

### v0.5 Deployment
```
PyStreamMCP v0.5 + SearXNG (optional sidecar)
├── Database discovery (read-only connections)
├── Web search metadata ranking
├── Metadata cache (SQLite local)
└── Config: Enable/disable metadata filtering
```

### v1.0 Deployment
```
PyStreamMCP v1.0 (full two-stage)
├── All v0.5 components
├── Contextual reranking engine
├── Tiered token budget system
├── StatGuardian WebValidator
├── OTel tracing export
└── Shared metadata cache (Redis optional)
```

---

## What This Means

PyStreamMCP transforms from:
- **Query optimizer** → **Selective intelligence engine**
- **Post-retrieval only** → **Pre + post-retrieval intelligence**
- **All-or-nothing** → **Tiered + adaptive**
- **Single-stage** → **Two-stage pipeline**

Result: 90-95% data reduction, 100% quality preservation, fully auditable.
