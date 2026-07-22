# PyStreamMCP Complete Implementation Roadmap 2026

**Date:** July 2026  
**Status:** Architecture finalized, roadmap approved, ready for v0.5 development  
**Mission:** Selective Intelligence via Metadata Filtering + Contextual Reranking

---

## Executive Summary

PyStreamMCP is transforming from a query optimizer into a **Selective Intelligence Engine** that achieves **90-95% data reduction** while maintaining quality.

**Two-Stage Pipeline:**
1. **Stage 1 (Pre-Retrieval):** Metadata filtering (70-85% reduction)
2. **Stage 2 (Post-Retrieval):** Contextual reranking + tiered token filtering (70-80% reduction)

**Flexibility:**
- Tiered token budgets (Minimal/Standard/Large/Comprehensive)
- Intent-based allocation within tiers
- Developer-configurable token multipliers for critical scenarios

**Result:** Every query gets focused context at the right detail level, within strict budgets, fully auditable.

---

## Complete Architecture

### Three Retrieval Sources, One Pattern

```
Query
  ↓
STAGE 1: Metadata Filtering (Pre-Retrieval)
├─ Web Search: Rank by authority (no crawl yet)
├─ Database: Select tables by cardinality (no query yet)
└─ MCP Tools: Rank by capability + success rate (no invoke yet)
  ↓
Selective Retrieval (top-1 or top-3 only)
├─ Web: Crawl highest-ranked URL
├─ Database: Query only necessary columns
└─ Tool: Invoke best-ranked tool
  ↓
STAGE 2: Contextual Reranking + Tiered Token Filtering (Post-Retrieval)
├─ Complexity Detection: Simple / Moderate / Complex / Very Complex
├─ Tier Assignment: Minimal (50-100) / Standard (500-1000) / Large (2000-3000) / Comprehensive (5000+)
├─ Intent Allocation: Flexible within tier bounds
├─ Multiplier Check: Expand budget for critical keywords
├─ Rerank Content: By relevance to query intent
└─ Filter to Budget: Keep only highest-value items within tier
  ↓
Quality Validation (StatGuardian)
  ↓
Result: Minimal, high-value context within budget
```

### Detailed Component Breakdown

#### 1. Complexity Classifier
Detects query complexity and calculates tier:

```
Input: "Design a customer retention system with budget constraints"
↓
Features:
- Entities: 3 (customer, retention, system) ← Complex
- Relationships: 2 (design → system, system → constraints) ← Complex
- Keywords: "design", "system", "constraints" ← Complex
- Word count: 9 words ← Moderate
↓
Result: Complex tier (Large: 2000-3000 tokens)
```

#### 2. Intent Detector
Determines how to allocate tokens within tier:

```
Input: "Design a customer retention system with budget constraints"
Query Intent: Detailed analysis (implementation-focused)
↓
Tier: Large (2000-3000)
Intent Score: 0.8 (high detail needed)
↓
Allocation: 2800 tokens (high end of tier)
```

#### 3. Token Multiplier Engine
Expands budget for critical scenarios:

```
Query: "CRITICAL: Production customer retention bug - analyze root cause"
↓
Keywords: "CRITICAL", "Production", "bug" → Multiplier: 2.0x
↓
Base Allocation: 2800 tokens (from intent)
Expanded: 2800 × 2.0 = 5600 tokens
↓
Result: 5600 tokens (capped at Comprehensive ceiling of 8000)
```

#### 4. Metadata Filter (Stage 1)
Selects sources before retrieval:

```
Query: "Retention strategies"
↓
Web Search Candidates (metadata ranking):
- HBR (authority 0.95, freshness 0.9, topic 0.95) → Score: 0.93
- TechCrunch (authority 0.85, freshness 0.9, topic 0.7) → Score: 0.82
- RandomBlog (authority 0.3, freshness 0.5, topic 0.6) → Score: 0.43
↓
Selection: HBR (top-1 by metadata)
Retrieval: Crawl only HBR URL (8KB)
```

#### 5. Contextual Reranker (Stage 2)
Ranks retrieved content by relevance:

```
Retrieved Content: 12 sections from HBR article
↓
Ranking by Relevance:
1. Definition (relevance 1.0, tokens 80) ← Most relevant
2. Top 3 strategies (relevance 0.95, tokens 320)
3. Implementation metrics (relevance 0.90, tokens 150)
4. Case studies (relevance 0.75, tokens 400)
5. Advanced techniques (relevance 0.60, tokens 200)
↓
Selection (within 2800 token budget):
- Definition: 80 tokens (cumulative: 80)
- Top 3 strategies: 320 tokens (cumulative: 400)
- Implementation metrics: 150 tokens (cumulative: 550)
- Case studies: 400 tokens (cumulative: 950)
- Advanced techniques: 200 tokens (would exceed at 1150)
- Stop: Budget respected, highest-value items selected
↓
Result: 950 tokens of 2800 allocated (lots of room, but stops at relevance cliff)
```

---

## Roadmap at a Glance

### v0.4.0 (Released July 2026)
✅ **Current Production Release**
- OKF native support
- StatGuardian integration
- 58 unit + 65 integration tests

### v0.5.0 (Sep-Oct 2026, 8 weeks)
🚀 **Foundation for Selective Intelligence**
- Metadata filtering engine (Stage 1)
- Metadata caching system
- Web domain metadata (50+ profiles)
- Database schema metadata (25+ profiles)
- MCP tool metadata (20+ profiles)
- Optional SearXNG sidecar (OSS search)
- Database discovery foundation (PostgreSQL, MongoDB)
- 35 unit + 35 integration tests (70 total)
- Backward compatible

**Deliverable:** Foundation for v1.0 complete intelligence layer

### v1.0.0 (Nov-Jan 2027, 10 weeks)
⚡ **Production Selective Intelligence**
- Contextual reranking engine (Stage 2)
- Tiered token budgets (4 tiers)
- Intent-based allocation (flexible within tiers)
- Token multiplier system (developer-configurable keywords)
- Web selective retrieval (Crawl4AI + Trafilatura)
- Database selective retrieval (column + row filtering)
- MCP tool selective invocation
- StatGuardian validation (both stages)
- Shared metadata cache (all agents learn)
- OTel tracing (audit every decision)
- 85+ unit + 95+ integration tests (180+ total)
- Production-ready, stable API

**Deliverable:** Complete selective intelligence platform

### v1.1+ (Beyond Q1 2027)
🚁 **Advanced Features**
- Learn optimal filtering patterns from history
- Predict metadata changes before retrieval
- Multi-agent coordination (fair-share allocation)
- Knowledge graph reasoning

---

## Key Implementation Files (v0.5 + v1.0)

### v0.5 Files

**Metadata Filtering:**
- `core/src/metadata/filter.rs` — Candidate ranking by metadata
- `core/src/metadata/cache.rs` — Metadata caching + TTL invalidation
- `python/pystreammcp/metadata/` — Python bindings

**Web Foundation:**
- `core/src/web/searxng.rs` — SearXNG HTTP client (ranking only, no crawl)
- `core/src/web/metadata.rs` — Domain authority + freshness scoring
- `mcp_catalog/web_domains/` — 50+ domain metadata profiles

**Database Foundation:**
- `core/src/database/discovery.rs` — Safe schema discovery
- `core/src/database/metadata.rs` — Schema + statistics extraction
- `mcp_catalog/database_schemas/` — 25+ example schemas

**MCP Tools:**
- `core/src/mcp/registry.rs` — Tool metadata registry
- `mcp_catalog/mcp_tools/` — 20+ tool profiles

### v1.0 Files (Additions)

**Contextual Reranking & Budgets:**
- `core/src/reranker/contextual.rs` — Relevance scoring + content ranking
- `core/src/budgets/tier.rs` — Tiered token budgets
- `core/src/budgets/intent.rs` — Intent detection + allocation
- `core/src/budgets/multiplier.rs` — Token multiplier system
- `python/pystreammcp/budgets/` — Python bindings

**Web Production:**
- `core/src/web/crawl4ai.rs` — Selective crawling (top-1/3)
- `core/src/web/trafilatura.rs` — Content extraction
- `core/src/web/validator.rs` — StatGuardian integration

**Database Production:**
- `core/src/database/selective_query.rs` — Column + row selection
- `core/src/database/row_sampling.rs` — Metadata-guided row filtering

**MCP Production:**
- `core/src/mcp/selective_invocation.rs` — Ranked tool selection + fallback

**Quality & Observability:**
- `core/src/quality/statguardian_integration.rs` — Pre + post-retrieval validation
- `core/src/observability/otel_traces.rs` — Complete decision tracing

---

## Success Metrics (v1.0)

| Metric | Target | Why |
|--------|--------|-----|
| **Data Reduction (Stage 1)** | 70-85% | Selective retrieval |
| **Token Reduction (Stage 2)** | 70-80% | Contextual reranking + tier filtering |
| **Combined Reduction** | 90-95% | Two-stage compound effect |
| **Tier Accuracy** | >90% | Correct complexity classification |
| **Intent Accuracy** | >85% | Correct allocation within tier |
| **Multiplier Accuracy** | >95% | Keyword detection + expansion |
| **Budget Adherence** | 99%+ | Context fits within tier/multiplier limits |
| **Quality Preservation** | >95% | No false negatives |
| **Cache Hit Rate** | >70% | Metadata decisions reused |
| **Decision Latency** | <50ms | Fast metadata filtering |
| **Multiplier ROI** | >0.8 correlation | Expanded budgets improve quality |
| **False Negatives** | <0.5% | Critical info never filtered |

---

## Resource Requirements

### v0.5 (8 weeks)
- **Team:** 2-3 engineers
- **Hours:** ~320 total (40-50 hrs/week × 2 engineers, 8 weeks)
- **Scope:** Metadata filtering foundation + source discovery
- **Dependencies:** None (parallel with v0.4 release)

### v1.0 (10 weeks)
- **Team:** 2-3 engineers (same team ideally)
- **Hours:** ~400 total (40-50 hrs/week × 2 engineers, 10 weeks)
- **Scope:** Production-grade selective intelligence + quality gates
- **Dependencies:** v0.5 complete + StatGuardian 2.3+

### Total: 18 weeks, 720 hours, 6 months (Q4 2026 + Q1 2027)

---

## Strategic Positioning

After v1.0, PyStreamMCP will be **unique in the OSS ecosystem:**

✅ **Pre-retrieval Intelligence** (metadata filtering before data transfer)  
✅ **Post-retrieval Intelligence** (contextual reranking + tiered budgets)  
✅ **Flexible Budgets** (intent + multipliers within tier bounds)  
✅ **Cached Learning** (decisions improve over time)  
✅ **Quality Gates** (StatGuardian validation at both stages)  
✅ **Uniform Across Sources** (web, database, MCP tools)  
✅ **Fully Auditable** (OTel tracing of every decision)  
✅ **Developer-Configurable** (token multipliers for custom needs)

---

## Timeline

| Phase | Dates | Status | Focus |
|-------|-------|--------|-------|
| v0.4 | Jul 2026 | ✅ Released | OKF + StatGuardian |
| **v0.5** | **Sep-Oct 2026** | **→ Starting** | **Metadata filtering foundation** |
| **v1.0** | **Nov-Jan 2027** | **→ Planned** | **Complete selective intelligence** |
| v1.1+ | Q2 2027+ | Vision | Learning + prediction |

---

## Approval & Next Steps

### To Proceed:
1. ✅ **Approve** this complete architecture
2. ✅ **Confirm** v0.5 start date (Sep 2026)
3. ✅ **Allocate** team (2-3 engineers)
4. ✅ **Begin** v0.5 development (metadata filtering foundation)

### Key Deliverables:
- **v0.5 (Oct 2026):** Foundation complete, ready for v1.0 integration
- **v1.0 (Jan 2027):** Production-grade selective intelligence live

---

## Why This Matters

### For Agents
- Focused context instead of data overload
- Faster reasoning (less to process)
- Lower costs (fewer API calls + data transfers)
- Better quality (high signal-to-noise)

### For PyStreamMCP
- **Unique positioning:** Only OSS system with true selective intelligence
- **Strategic foundation:** v1.1+ multi-agent coordination depends on this
- **Integration point:** Web + database + MCP tools use same pattern
- **Community value:** Exportable metadata in OKF enables contribution

### For the Platform
- Metadata sharing improves all downstream systems
- Quality gates (StatGuardian) now uniform across all sources
- Cost tracking (OpenAnchor) at metadata + data level
- Foundation for intelligent automation at scale

---

## Key Commitments

1. **90-95% data reduction** ← Primary goal
2. **Zero false negatives** ← Never filter critical info
3. **Metadata-first decisions** ← Before data retrieval
4. **Universally applicable** ← Web, database, MCP tools
5. **Cached and learned** ← Every decision improves future queries
6. **Fully auditable** ← OTel traces explain why
7. **Developer-flexible** ← Multipliers for custom needs
8. **Backward compatible** ← v0.5 → v1.0 non-breaking

---

## Final Vision

PyStreamMCP with selective intelligence becomes the **intelligent acquisition platform** that agents and humans trust because:

- **It's selective:** Minimal data, maximum value
- **It's transparent:** Every decision justified by metadata
- **It's efficient:** 90-95% reduction, maintained quality
- **It's learning:** Metadata cache improves over time
- **It's universal:** Works for web, databases, MCP tools
- **It's controllable:** Developers can override with multipliers

Result: Focused, auditable, efficient intelligence for any agent, any source, any scale.

---

**Ready to build the Selective Intelligence Layer.**
