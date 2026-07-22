# PyStreamMCP: Web Knowledge Acquisition — OSS-Only Architecture Revision

**Scope:** Integrate web knowledge as a CORE feature (v1.0), not optional stretch goal. OSS-only tools, embedded in query planning, quality gated.

**Document Status:** Architecture revision for v0.5 → v1.0 roadmap  
**Date:** July 2026

---

## 1. OSS Architecture (30%)

### Search Layer
| Tool | Role | Cost Model | Quality |
|------|------|-----------|---------|
| **SearXNG** (primary) | Meta-search aggregator | Self-hosted (free) | Aggregates 10+ engines (Google, Bing, DuckDuckGo, Searx) |
| **DuckDuckGo API** (fallback) | Search + bangs | Free tier: 100/day | Instant answers, no tracking |
| **Elasticsearch** (optional) | Local document index | Self-hosted (free) | Full-text search over crawled docs |

**Decision:** SearXNG + DuckDuckGo hybrid. SearXNG deployed on Render/Fly (free tier: ~$5/mo actual cost). No API key dependency. Fallback to DuckDuckGo when SearXNG unavailable.

### Crawling Layer
| Tool | Role | Cost Model | Quality |
|------|------|-----------|---------|
| **Crawl4AI** (primary) | Async web crawler + LLM extraction | Free OSS (pip install) | Fast (200+ domains/sec), JS-aware, built-in LLM extraction |
| **Scrapy** (secondary) | Scalable spider framework | Free OSS (pip install) | Production-grade for site mapping (v1.1+) |
| **Playwright** (JS rendering) | Dynamic content handler | Free OSS (pip install) | Headless browser for JS-heavy sites (fallback) |

**Decision:** Crawl4AI as primary (minimal setup, LLM-native). Scrapy for site-specific mapping in v1.1. Playwright only when needed (10% of queries).

### Content Extraction Layer
| Tool | Role | Cost Model | Quality |
|------|------|-----------|---------|
| **Trafilatura** (primary) | Extract article text + metadata | Free OSS (pip install) | 95%+ extraction accuracy, minimal junk |
| **BeautifulSoup4** (fallback) | HTML parsing | Free OSS (pip install) | Lower accuracy but works everywhere |
| **URLextract** | Link discovery | Free OSS | For site mapping |

**Decision:** Trafilatura first (specialized for content). BeautifulSoup4 fallback (100% reliability).

### Validation Layer
| Tool | Role | Integration |
|------|------|-----------|
| **StatGuardian** | Quality gates for web content | NEW: WebSourceValidator (domain reputation, SSL, age, update frequency) |
| **Langdetect** | Language detection (free OSS) | Skip non-English sources by default |
| **URLextract + ssl.SSLContext** | Domain reputation + SSL verification | Built-in Python |

**Decision:** Web sources require StatGuardian validation (new validator type). Blocks outdated, low-quality, or untrusted domains.

### Self-Hosted vs. SaaS Tradeoffs

| Component | Self-Hosted | SaaS |
|---|---|---|
| **SearXNG** | $5/mo (Render), 500ms latency, full control | API quota $0-100/mo, commercial vendor risk |
| **Crawl4AI** | $0, 5s crawl latency per domain | Cloud service (~$0.01/crawl) = $1-10/mo for scale |
| **Trafilatura + DB** | $0, local, instant | Cloud indexing ($50+/mo) |
| **StatGuardian validation** | Local checks + external API (shared fleet) | Inline quality gates (existing) |

**Recommendation:** Self-hosted SearXNG + local Crawl4AI for v0.5-v1.0. Containerize as optional sidecar. v1.1+ offers cloud deployment option (Render/Fly) for teams.

---

## 2. Core Integration Strategy (40%)

### Query Planning: Web as First-Class Source

**Current (v0.4):** Query → Discover (local data) → Optimize → Context  
**New (v1.0):** Query → Analyze Web-Needing → Discover (local + web) → Optimize → Context

```
Agent Query: "Best practices for customer retention"
                    ↓
        Detect: Needs current web knowledge
        (Keywords: "best", "latest", "trends", "practices")
                    ↓
        Route Decision:
        - Local knowledge sufficient? → Local-only path
        - Web knowledge valuable? → Hybrid path (local + web)
        - Web-only domain? → Web-primary path
                    ↓
        Parallel Execution:
        [Local Discovery] + [Web Search] + [Crawl Top-5 URLs]
                    ↓
        StatGuardian Validation (BEFORE merging)
        - Domain reputation (SSL, Wayback Machine age)
        - Content freshness (HTTP headers, DOM timestamps)
        - Authority score (page rank heuristic)
                    ↓
        Merge Results:
        - Weight local data 70% (fresh, trusted)
        - Weight web data 30% (recency, breadth)
                    ↓
        Optimize & Stream to Agent
```

### Web Detection Heuristics

Detect when web knowledge is needed (no API call, local ML model):

```python
class WebKnowledgeDetector:
    def needs_web_search(query: str, age_hours: int) -> bool:
        # Trigger on:
        # 1. Temporal keywords: "latest", "current", "2026", "trend", "how to"
        # 2. Knowledge domains: "practices", "standards", "benchmarks"
        # 3. Data age > 90 days (local data freshness)
        # 4. Confidence gap: local data relevance < 0.5
        
        # Don't trigger on:
        # - Retrieval-only queries ("customer ID #123")
        # - Predictive queries (use local model)
        # - Sensitive data (PII, financial)
```

### Token Budget Impact

**Web retrieval costs (added to budget):**
- Search query: 50 tokens
- Crawl extraction (top-3 URLs): 1500 tokens (4-5K chars per URL @ ~0.3 tokens/char)
- Merging + ranking: 100 tokens
- **Total per web query: ~1650 tokens**

**Strategy:** Adjust `max_tokens` constraint when web enabled:
- Without web: 2000 token budget
- With web: 3500 token budget (1650 + 1850 local)
- OR: Reduce local data (caching + sampling) if web needed

### StatGuardian Integration for Web

NEW validator type in StatGuardian:

```python
@dataclass
class WebSourceValidator(Validator):
    """Validates web sources before inclusion in context."""
    
    def validate(source: WebSource) -> ValidationResult:
        checks = [
            check_domain_reputation(source.url),      # SSL, Wayback Machine
            check_content_freshness(source.headers),   # Last-Modified
            check_authority(source.title, source.url), # Domain + PageRank est.
            check_language(source.content),            # langdetect
            check_no_paywall(source.status_code),      # Not 403/410
        ]
        
        return ValidationResult(
            passed=all(checks),
            confidence=mean(check_scores),
            issues=failing_checks
        )
```

StatGuardian config:
```yaml
web_sources:
  require_validation: true
  rules:
    - min_authority: 0.6  # Block low-authority sites
    - max_age_days: 180   # Content > 6 months is risky
    - require_ssl: true
    - blocked_domains: ["quora.com", "reddit.com"]  # Optional noisiness filter
```

### OKF Catalog Expansion

NEW catalog section: `mcp_catalog/web_sources/`

```yaml
mcp_catalog/
├── systems/
├── tools/
├── web_sources/          # NEW: Public web knowledge domains
│   ├── technical_docs/
│   │   ├── kubernetes.yaml     # K8s official docs
│   │   ├── rust_book.yaml
│   │   └── python_docs.yaml
│   ├── industry_benchmarks/
│   │   ├── ai_trends_2026.yaml
│   │   └── e_commerce_best_practices.yaml
│   └── research_papers.yaml    # arXiv, papers.dev
└── interconnections/
    └── web_to_local_mapping.yaml  # When web + local = better answer
```

Each web source entry:
```yaml
name: "Kubernetes Official Documentation"
domain: "kubernetes.io"
freshness_check: "Last-Modified header"
typical_content_age: "7-30 days"
average_tokens_per_crawl: 2000
trustworthiness: 0.95
covered_topics:
  - "kubernetes architecture"
  - "deployment best practices"
  - "storage strategies"
linked_local_sources:
  - "internal_k8s_config_repository"
quality_notes: "Official source; update frequently; few errors"
```

### Routing Decision Logic

```python
class ContextRouter:
    def route(query: Query) -> DiscoveryPlan:
        local_score = score_local_relevance(query)
        web_needed = detector.needs_web_search(query)
        
        if local_score > 0.85 and not web_needed:
            return Route.LOCAL_ONLY
        elif local_score > 0.6 and web_needed:
            return Route.HYBRID (70% local, 30% web)
        elif local_score < 0.4:
            return Route.WEB_PRIMARY (30% local, 70% web)
        else:
            return Route.WEB_ONLY  # Rare; only for entirely external topics
```

---

## 3. Revised Roadmap (30%)

### v0.5: Web Knowledge Foundation (8 weeks, 400 hours)

**Goal:** Detect web-needing queries, integrate SearXNG + Crawl4AI

**Changes to v0.4:**
- Add `WebKnowledgeDetector` module (50h)
- Integrate SearXNG in `discovery.rs` (100h)
- Integrate Crawl4AI for top-3 URLs (80h)
- Add `WebSource` type to discovery (40h)
- Basic StatGuardian web validator (50h)
- Tests + docs (80h)

**Deliverables:**
- Query → detects web-needed (no API call, local heuristic)
- SearXNG search integration (HTTP client, result parsing)
- Crawl4AI extraction (async task pool, token estimation)
- Basic validation (SSL, freshness checks)
- 25+ tests
- Backward compatible (no breaking changes)

**Code Structure:**
```
core/src/
├── web/                     # NEW
│   ├── mod.rs
│   ├── detector.rs          # Web-needing heuristics
│   ├── searxng.rs           # SearXNG HTTP client
│   ├── crawl4ai.rs          # Crawl4AI async wrapper
│   └── validator.rs         # Basic domain validation
├── discovery.rs             # Add WebSource variant
└── [rest unchanged]
```

**Breaking Changes:** None. `SourceType::External` now accepts `web` variant.

### v1.0: Web Knowledge as Core (10 weeks, 500 hours)

**Goal:** Production-ready web + local hybrid queries, StatGuardian integration, OKF catalog

**Changes to v0.5:**
- Full StatGuardian WebSourceValidator (80h)
- OKF catalog + web source definitions (100h)
- Routing logic (hybrid decisions) (80h)
- Token budget adjustment for web (60h)
- Parallel discovery (local + web in parallel) (100h)
- Quality gates + SLA enforcement (80h)

**Deliverables:**
- Web + local scoring (merged relevance + freshness)
- StatGuardian gating (block low-quality sources)
- OKF catalog section (50+ web domain definitions)
- Routing: local-only, hybrid (weighted merge), web-primary
- Parallel discovery (50ms overhead vs. sequential)
- 40+ new tests (total: 100+)
- Production deployment guide
- Docker sidecar config for SearXNG

**Code Structure:**
```
core/src/
├── discovery.rs             # Add ranking for merged web+local
├── optimization.rs          # Adjust token budgets for web
├── web/
│   ├── merger.rs            # Merge + weight web + local results
│   ├── router.rs            # Route decision logic
│   └── [rest from v0.5]
└── statguardian.rs          # NEW: WebSourceValidator call
```

**New CLI commands:**
```bash
# Search + crawl in one call
pystreammcp discover "customer retention" --include-web --statguardian-validate

# Show why query routed to web
pystreammcp query "latest ML trends" --explain-routing

# Manage web source quality gates
pystreammcp web-sources list --validated-only
pystreammcp web-sources validate kubernetes.io --force-check
```

### v1.1: Site Mapping & Knowledge Graphs (12 weeks, 600 hours)

**Goal:** Build domain-specific crawlers, knowledge graphs for common sites

**Features:**
- Scrapy spiders for 10+ high-value domains (K8s, Python docs, Rust, AWS, etc.)
- Knowledge graph extraction (entity + relationships from crawled content)
- Update scheduler (weekly crawl + OKF catalog sync)
- Deduplication (same fact from multiple sources)
- Local vector DB option (embeddings + semantic search over web content)

**Deliverables:**
- `mcp_catalog/web_spiders/` with 10+ domain spiders
- Knowledge graph storage (Postgres or DuckDB)
- Semantic search: "Kubernetes storage solutions" → k8s/storage/yaml
- Vector index: embed web content, enable similarity search
- Update pipeline: daily crawl, quality check, OKF sync
- 50+ tests

---

## Architecture Diagram

```
Agent Query
    │
    ├─ Web Needed? (Detector)
    │  ├─ Yes → WebKnowledgePath
    │  └─ No  → LocalPath
    │
    ├─ WebKnowledgePath:
    │  ├─ SearXNG search (parallel)
    │  ├─ Top-5 URL ranking
    │  ├─ Crawl4AI extraction (parallel)
    │  └─ Trafilatura content extraction
    │
    └─ LocalPath:
       ├─ OKF catalog lookup
       └─ Table scan/cache hit
    
    Merge Results:
       ├─ Web sources → StatGuardian WebValidator
       ├─ Local sources → StatGuardian existing validators
       └─ Weight + combine (70% local, 30% web by default)
    
    Route Decision:
       ├─ Local-only (score > 0.85, no web trigger)
       ├─ Hybrid (score 0.6-0.85 + web trigger)
       ├─ Web-primary (score < 0.6, web high value)
       └─ Web-only (rare)
    
    Optimize:
       ├─ Adjust token budget (+1650 for web)
       ├─ Streaming + compression
       └─ Caching (web results + extracted content)
    
    Response:
       └─ Context with full audit trail
          (which source, why, confidence, freshness)
```

---

## Decision Points & Rationale

### 1. Why SearXNG + DuckDuckGo (not Google/Bing API)?
- **Cost:** $0 (self-hosted) vs. $1-5 per 1000 queries
- **Vendor lock-in:** None (open protocol)
- **Latency:** 300-500ms (SearXNG) vs. 200ms (API), but minimal impact
- **Quality:** Aggregates 10+ engines, often better than single API
- **Privacy:** No data sent to Google/Microsoft
- **Trade-off:** Slight latency increase (~100-200ms), no API key management

### 2. Why Crawl4AI (not just Selenium/Puppeteer)?
- **Design:** Built for LLM extraction (not testing), async-first
- **Speed:** 200+ domains/sec (vs. 5-10 with Selenium)
- **LLM-native:** Extracts structured data + text in one pass
- **Trade-off:** Newer project (v0.3 in 2026), but stable

### 3. Why Trafilatura (not regex/custom parsing)?
- **Accuracy:** 95%+ on news/articles (benchmark: readability, boilerpipe)
- **Metadata:** Extracts author, publish date, title, abstract
- **Speed:** <100ms per page
- **Fallback:** BeautifulSoup4 as backup (100% works, 80% accuracy)

### 4. Why v1.0, not v1.5?
- **Mission shift:** Web knowledge is fundamental to agent intelligence
- **Competitive gap:** Agents without current web knowledge are blind
- **Integration:** StatGuardian + OKF catalog already ready to support
- **Effort:** 500 hours fits in Q4 2026 roadmap (Phase 5 scope)
- **Trade-off:** v0.4 (enterprise auth) delayed by 6 weeks, v1.0 becomes main release

### 5. Why require StatGuardian validation?
- **Quality gate:** Web is noisier than internal data
- **Trust:** Blocks low-authority, outdated, or paywalled content
- **Compliance:** Audit trail for all web sources
- **Trade-off:** +100ms latency per web result, but prevents bad data inclusion

---

## Key Differences: v1.0 vs. v0.4

| Aspect | v0.4 | v1.0 |
|---|---|---|
| **Knowledge sources** | Local only (OKF catalog) | Local + Web (OKF + SearXNG) |
| **Discovery** | Sequential (local) | Parallel (local + web) |
| **Query detection** | Intent-based | Intent + temporal + freshness checks |
| **Token budget** | Fixed 2000-5000 | Dynamic (base + web cost) |
| **Validation** | StatGuardian existing types | + WebSourceValidator |
| **Routing** | Source selection | Local vs. Web decision + merge strategy |
| **OKF catalog** | 100+ internal systems | 100+ internal + 50+ web domains |
| **Tests** | 60+ | 100+ |
| **Dependencies** | numpy, pydantic, sqlalchemy | +searxng, crawl4ai, trafilatura, langdetect |

---

## Implementation Phases & Hours

| Phase | Focus | Hours | Weeks | Tests | Status |
|-------|-------|-------|-------|-------|--------|
| v0.5 | Foundation (search + crawl) | 400 | 8 | 25+ | Planned Q4 2026 |
| v1.0 | Core (validation + routing + OKF) | 500 | 10 | 40+ | Planned Q4-Q1 2026 |
| v1.1 | Scale (site mapping + KG) | 600 | 12 | 50+ | Planned Q1-Q2 2027 |

**Total v1.0 effort:** 900 hours (v0.5 + v1.0 combined) = ~6 months

---

## OSS Dependency Summary

| Dependency | Version | License | Purpose | Cost |
|---|---|---|---|---|
| searxng | latest | AGPL-3.0 | Meta-search | $0 (self-host) |
| crawl4ai | 0.3+ | Apache-2.0 | Web crawling | $0 |
| trafilatura | 1.6+ | Apache-2.0 | Content extraction | $0 |
| beautifulsoup4 | 4.12+ | MIT | Backup parsing | $0 |
| langdetect | 1.0+ | Apache-2.0 | Language detection | $0 |
| urlextract | 1.8+ | BSD | Link discovery | $0 |
| elasticsearch (optional) | 8.0+ | Elastic License | Local indexing (v1.1) | $0 |

**No commercial APIs required. Total licensing compliance: MIT + Apache-2.0 + AGPL-3.0.**

---

## Production Deployment

### Docker Compose: PyStreamMCP + SearXNG

```yaml
version: '3.8'
services:
  pystreammcp:
    build: .
    environment:
      SEARXNG_URL: "http://searxng:8888"
      STATGUARDIAN_URL: "http://statguardian:8001"
    ports:
      - "8000:8000"
    depends_on:
      - searxng

  searxng:
    image: searxng/searxng:latest
    environment:
      SEARXNG_SETTINGS_PATH: /etc/searxng/settings.yml
    ports:
      - "8888:8888"
    volumes:
      - ./searxng-settings.yml:/etc/searxng/settings.yml
```

**Resources:** SearXNG ~200MB RAM, PyStreamMCP +Crawl4AI ~500MB with 2-4 concurrent crawlers.

---

## Conclusion

Web knowledge is no longer optional for agent intelligence. By integrating OSS tools (SearXNG, Crawl4AI, Trafilatura) into query planning as a **first-class discovery source**, PyStreamMCP gains:

1. **Recency** — Current best practices, latest research, live benchmarks
2. **Breadth** — 10 million+ indexed web pages vs. internal data alone
3. **Authority** — Link to trusted external sources with quality gates
4. **Transparency** — Full audit trail (OKF-tracked) of web decisions
5. **Zero lock-in** — All tools OSS; self-host or SaaS (flexible)

**v1.0 ships in Q1 2027 as the first agent-native web knowledge layer.**
