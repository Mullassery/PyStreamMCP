# Web Knowledge Acquisition: Executive Summary

**Status:** Revised architecture for v0.5 → v1.0  
**Date:** July 2026  
**Key Decision:** Web knowledge as CORE feature (v1.0), not stretch goal (v1.5)

---

## The Opportunity

Current PyStreamMCP (v0.4):
- Optimizes queries against **internal data only** (warehouses, caches, activated sources)
- Agents are **blind to current web knowledge** (trends, best practices, latest research)
- 60-75% token reduction achieved but on 30% of queries (rest need external context)

With web knowledge (v1.0):
- Optimizes queries against **internal + web data** (10 million+ indexed pages)
- Agents gain **recency, authority, breadth** without loss of efficiency
- 60-75% token reduction applies to **80% of queries** (web-informed paths)
- Competitive positioning: first OSS agent framework with web-aware query optimization

---

## Why v1.0, Not v1.5?

| Constraint | Impact |
|---|---|
| **Competitive gap** | Agents without web knowledge are 50% less useful in 2026 |
| **Effort fit** | 900 hours (v0.5 + v1.0) = 6 months, fits Q4 2026 + Q1 2027 roadmap |
| **Architecture ready** | StatGuardian + OKF catalog already support quality gates + external sources |
| **Integration points** | Discovery (add web sources), optimization (handle web token costs), routing (hybrid decisions) |
| **User impact** | "Latest ML trends" queries shift from web-only to optimized hybrid |

---

## Architecture at a Glance

```
Before (v0.4):
    Agent Query
         ↓
    [Local Discovery] → Optimize → Context
    
After (v1.0):
    Agent Query
         ↓
    [Temporal/Recency Check] → Web Needed?
         ↓                           ↓
    [Local Discovery]    [SearXNG + Crawl4AI]
         ↓                           ↓
    [Merge + Weight] ← StatGuardian Validation
         ↓
    [Route Decision] ← (Local-Only / Hybrid / Web-Primary)
         ↓
    [Optimize] (adjust tokens for web cost)
         ↓
    Context (full audit trail)
```

**Key Addition:** Web Knowledge Detector (heuristic, no API call)
- Detects temporal keywords: "latest", "trends", "current", "best practices"
- Checks local data age: > 90 days = web search triggered
- Confidence threshold: if local relevance < 0.5, try web

---

## OSS-Only Tools (Zero Commercial APIs)

| Layer | Tool | Cost | Latency |
|---|---|---|---|
| Search | SearXNG (self-host) | $0 | 300-500ms |
| Crawl | Crawl4AI | $0 | 50ms per page |
| Extract | Trafilatura | $0 | 50-100ms per page |
| Validate | StatGuardian WebValidator | $0 | 500-1000ms |

**Total deployment:** Docker Compose + Python packages. No vendor lock-in.

**Alternative:** Render/Fly.io ($5/mo) for managed SearXNG (optional, not required).

---

## What Changes in v1.0 vs. v0.4

### Code Changes

**New modules:**
```
core/src/web/
├── mod.rs              # Web knowledge exports
├── detector.rs         # Detect web-needing queries (50 lines)
├── searxng.rs          # SearXNG HTTP client (100 lines)
├── crawl4ai.rs         # Crawl4AI async wrapper (80 lines)
├── merger.rs           # Merge web + local results (120 lines)
└── router.rs           # Route decision logic (80 lines)
```

**Modified modules:**
```
discovery.rs           # Add SourceType::Web
optimization.rs        # Adjust token budgets for web cost
statguardian.rs        # Add WebSourceValidator call
query.rs              # Optional: add web_enabled flag
```

**Python layer:**
```
python/pystreammcp/
├── web_discovery.py    # High-level API
├── web_sources.py      # OKF catalog loader
└── web_validators.py   # Wrap StatGuardian WebValidator
```

### OKF Catalog Expansion

New section: `mcp_catalog/web_sources/`
- 50+ curated web domains (Kubernetes, Python, Rust, AWS, etc.)
- Cost profiles, freshness intervals, trustworthiness scores
- Linked to local data (when web + local = better answer)

### API Changes

**New query flag:**
```rust
pub struct Query {
    pub text: String,
    pub agent_id: String,
    pub intent: QueryIntent,
    pub constraints: QueryConstraints,
    pub allow_web_search: bool,  // NEW (default: true)
    // ...
}
```

**New discovery source type:**
```rust
pub enum SourceType {
    Table { table_name: String },
    // ...
    Web { domain: String, search_query: String },  // NEW
}
```

**New CLI commands:**
```bash
pystreammcp query "latest trends" --include-web --explain-routing
pystreammcp web-sources list --validated-only
pystreammcp web-sources validate kubernetes.io --force-check
```

### Breaking Changes

**None.** Backward compatible:
- Existing queries work unchanged (web disabled by default in transition)
- Existing discovery code unaffected (web is new source type variant)
- Existing optimization strategies unchanged

---

## Three-Phase Rollout

### Phase 1: v0.5 (8 weeks, Q4 2026)
**Web Foundation**

- SearXNG integration (search)
- Crawl4AI integration (crawl top-3 URLs)
- Trafilatura extraction (clean content)
- Basic domain validation (SSL, freshness)
- 25+ tests
- **Impact:** Agents can search web (not yet optimized)

### Phase 2: v1.0 (10 weeks, Q4 2026 → Q1 2027)
**Web as Core**

- StatGuardian WebSourceValidator (quality gates)
- Routing logic (decide local vs. hybrid vs. web)
- Token budget adjustment (web cost modeling)
- OKF catalog expansion (50+ web domains)
- Parallel discovery (local + web in parallel)
- 40+ new tests (100+ total)
- **Impact:** Optimized hybrid queries (60-75% token reduction with web)**

### Phase 3: v1.1 (12 weeks, Q1 → Q2 2027)
**Web at Scale**

- Scrapy site-specific spiders (K8s, Rust, Python, AWS, etc.)
- Knowledge graph extraction (entities + relationships)
- Weekly crawl + OKF catalog sync automation
- Optional: Elasticsearch local index (semantic search)
- Optional: Vector DB (embeddings + similarity)
- 50+ new tests (150+ total)
- **Impact:** Domain-specific crawlers, knowledge graphs for top 20 sites**

---

## Token Budget Impact

**Without web:**
- Query: "Customer retention best practices" (internal data only)
- Local discovery: 1500 tokens
- Total: 1500 tokens

**With web (v1.0):**
- Query: "Customer retention best practices" (internal + web)
- Local discovery: 1000 tokens
- Web search: 50 tokens
- Crawl 3 URLs: 1200 tokens
- Merge + rank: 100 tokens
- **Total: 2350 tokens** (but higher quality + recency)

**Strategy:**
- Adjust `max_tokens` from 2000 → 3500 when web enabled
- OR: Reduce local data (caching + sampling) to stay within 2000
- Agent decides: speed (stay at 2000, fewer web results) vs. quality (3500, full web context)

---

## Quality Gates (StatGuardian Integration)

Web sources require validation before inclusion:

```yaml
# New StatGuardian config
web_sources:
  require_validation: true
  rules:
    - min_authority: 0.6      # Block low-quality sites
    - max_age_days: 180       # Content > 6 months risky
    - require_ssl: true       # No HTTP
    - blocked_domains:
        - "reddit.com"        # Too noisy
        - "quora.com"         # Low authority
    - whitelist:
        - "kubernetes.io"     # Always trust
        - "python.org"
        - "github.com"
```

**Impact:** Agents get trustworthy web context, not random blog posts.

---

## Deployment

### Minimal Setup (v0.5)
```bash
# 1. Deploy SearXNG
docker run -d -p 8888:8888 searxng/searxng

# 2. Install Python packages
pip install pystreammcp crawl4ai trafilatura langdetect

# 3. Use web-enabled queries
pystreammcp query "latest trends" --include-web
```

### Production Setup (v1.0)
```yaml
# Docker Compose
version: '3.8'
services:
  pystreammcp:
    build: .
    environment:
      SEARXNG_URL: "http://searxng:8888"
      STATGUARDIAN_URL: "http://statguardian:8001"
      WEB_ENABLED: "true"
      WEB_CRAWLERS: "4"
    ports: ["8000:8000"]
  
  searxng:
    image: searxng/searxng:latest
    ports: ["8888:8888"]
    volumes:
      - ./searxng-settings.yml:/etc/searxng/settings.yml
  
  statguardian:
    build: ../StatGuardian
    ports: ["8001:8001"]
```

---

## Success Metrics (v1.0)

| Metric | Target | How Measured |
|---|---|---|
| **Web detection accuracy** | >90% | Manual classification of 100 test queries |
| **Validation gate precision** | >95% | Block/allow accuracy vs. manual review |
| **Latency (web path)** | <1.5s | p95 end-to-end |
| **Throughput** | 10+ QPS | Concurrent requests |
| **Test coverage** | 100+ tests | Unit + integration |
| **OKF catalog** | 50+ domains | Indexed web sources |
| **Token reduction (hybrid)** | 60-75% | Same targets as local-only |

---

## Competitive Positioning

| Capability | PyStreamMCP v0.4 | PyStreamMCP v1.0 | Competitors |
|---|---|---|---|
| **Web-aware queries** | No | Yes | LangChain (via tools) |
| **OSS-only** | Yes | Yes | Unique in market |
| **Quality gates** | StatGuardian | StatGuardian + Web | Unique |
| **OKF catalog** | 100+ internal | 150+ (internal + web) | Unique |
| **Token reduction** | 60-75% | 60-75% (now on 80% queries) | 40-50% (web-aware) |
| **Latency** | <100ms | <1.5s (web) | 2-5s (web path) |

**Differentiator:** OSS-only web knowledge layer with quality gates. No vendor APIs. Full transparency.

---

## Risks & Mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| **SearXNG availability** | Medium | Fallback to DuckDuckGo API (free, no setup) |
| **Web content quality** | High | StatGuardian validation gates (whitelist/blacklist) |
| **Crawl latency** | Medium | Parallel crawling (3x concurrent), caching |
| **False web triggers** | Medium | Heuristic refinement (v0.5 feedback), local model (v1.1) |
| **Licensing compliance** | Low | All AGPL-3.0/Apache-2.0/MIT verified |
| **Rate limiting** | Medium | Configure SearXNG backend limits, backoff strategy |

---

## Roadmap Integration

**Existing roadmap (phases 1-5):**
- v0.1 (Phase 1): ✅ Foundation
- v0.2 (Phase 2): ✅ Integration
- v0.3 (Phase 3): ✅ Advanced
- v0.4 (Phase 4): 🚧 Enterprise (pushed to v1.0 phase)
- v1.0 (Phase 5): 🔮 Vision

**New roadmap (web-aware):**
- v0.5 (Phase 4A): 🚧 Web Foundation (8 weeks)
- v1.0 (Phase 4B + 5): 🚧 Web Core + Autonomy (10 weeks)
- v1.1 (Phase 6): 🔮 Web Scale (12 weeks)

**Effort:** 1600 hours total (v0.1-v1.1), 900 hours incremental (v0.5-v1.1)

---

## Next Steps

1. **Review & Approve:** Sign off on web knowledge as v1.0 core feature
2. **Architecture review:** Validate design with team (week 1)
3. **Dependency audit:** Verify OSS licenses (week 1)
4. **Spike:** Build minimal v0.5 PoC (SearXNG + Crawl4AI integration) (week 2)
5. **Roadmap update:** Publish revised timeline (week 2)
6. **Begin v0.5:** Start web foundation work (week 3)

---

## Documents

- **[PLAN_WEB_KNOWLEDGE_OSS_REVISION.md](PLAN_WEB_KNOWLEDGE_OSS_REVISION.md)** — Full architecture, 1000 words
- **[WEB_KNOWLEDGE_OSS_TOOLS_MATRIX.md](WEB_KNOWLEDGE_OSS_TOOLS_MATRIX.md)** — Tool evaluation + code examples

---

**TL;DR:** Web knowledge is fundamental to agent intelligence in 2026. PyStreamMCP v1.0 will be the first OSS query optimizer with quality-gated web integration. Zero commercial APIs. 900 hours to ship. Ready to start.
