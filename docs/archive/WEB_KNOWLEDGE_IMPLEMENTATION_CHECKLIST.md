# Web Knowledge Implementation Checklist

**Purpose:** Week-by-week tasks for v0.5 → v1.0 (18 weeks)  
**Status:** Ready to execute  
**Owner:** PyStreamMCP team

---

## v0.5: Foundation (Weeks 1-8)

### Week 1: Architecture Review & Setup
- [ ] Review PLAN_WEB_KNOWLEDGE_OSS_REVISION.md with team
- [ ] Verify OSS license compatibility (AGPL-3.0, Apache-2.0, MIT)
- [ ] Add searxng, crawl4ai, trafilatura to Cargo.toml + requirements.txt
- [ ] Create core/src/web/mod.rs (empty module)
- [ ] Create Docker Compose with SearXNG service
- [ ] PR: Web architecture approved

**Deliverable:** Foundation structure, SearXNG running locally

---

### Week 2: Web Detection (Detector)
- [ ] Implement WebKnowledgeDetector heuristics
- [ ] Temporal keywords: "latest", "trends", "current", "best practices", "how to"
- [ ] Data freshness check: local data age > 90 days
- [ ] Confidence threshold: local relevance < 0.5
- [ ] Unit tests (8 tests): temporal keywords, age check, confidence logic
- [ ] No API calls (local ML model not needed yet)

**File:** core/src/web/detector.rs (100 lines)  
**Tests:** 8 passing  
**PR:** Web detection without external calls

---

### Week 3: SearXNG HTTP Client
- [ ] Build SearXNG HTTP client (reqwest-based)
- [ ] Parse search results (title, URL, snippet)
- [ ] Error handling: SearXNG unavailable → fallback to DuckDuckGo API
- [ ] Rate limiting: max 10 QPS, backoff on 429
- [ ] Integration test with running SearXNG container
- [ ] Unit tests (6 tests): search, parsing, error handling, rate limit

**File:** core/src/web/searxng.rs (120 lines)  
**Tests:** 6 passing  
**PR:** Live web search working

---

### Week 4: Crawl4AI Integration
- [ ] Wrap Crawl4AI Python library (call via Python FFI or subprocess)
- [ ] Extract: URL, title, content (markdown), metadata
- [ ] Async task pool: crawl up to 4 URLs in parallel
- [ ] Token estimation: chars * 0.3 → tokens
- [ ] Fallback: if crawl fails, use search snippet
- [ ] Unit tests (5 tests): crawl success, parse, async, fallback, token estimation

**File:** core/src/web/crawl4ai.rs (150 lines)  
**Tests:** 5 passing  
**PR:** Multi-URL crawling in parallel

**Note:** Can use Python subprocess or PyO3 for FFI. Subprocess simpler for v0.5.

---

### Week 5: Content Extraction (Trafilatura)
- [ ] Integrate Trafilatura (Python subprocess or PyO3)
- [ ] Extract: text, title, author, date, excerpt
- [ ] Fallback to BeautifulSoup4 if Trafilatura fails
- [ ] Language detection: skip non-English (configurable)
- [ ] Quality score: penalize short content (<500 chars)
- [ ] Unit tests (6 tests): extraction, metadata, language, fallback, quality

**File:** core/src/web/extractor.rs (140 lines)  
**Tests:** 6 passing  
**PR:** High-accuracy content extraction

---

### Week 6: Domain Validation
- [ ] Implement WebSource struct (domain, URL, content, freshness, authority)
- [ ] Basic validators: SSL check (via requests), domain age (Wayback Machine API)
- [ ] Freshness check: HTTP Last-Modified header
- [ ] Authority heuristic: whitelist (K8s, Python, Rust) + domain TLD
- [ ] Unit tests (5 tests): SSL, Wayback, freshness, authority, combined

**File:** core/src/web/validator.rs (120 lines)  
**Tests:** 5 passing  
**PR:** Basic domain quality checks

---

### Week 7: Integration with Discovery
- [ ] Add SourceType::Web enum variant to discovery.rs
- [ ] Modify Discovery to include web sources (merge detection)
- [ ] Update test suite: discovery with web sources
- [ ] Integration test: end-to-end query → web detection → search → crawl → extract
- [ ] Tests (4 tests): SourceType::Web, discovery merge, end-to-end

**Files:** 
- discovery.rs (add SourceType::Web variant)
- core/src/web/mod.rs (re-exports)

**Tests:** 4 passing (integration)  
**PR:** Web sources in discovery pipeline

---

### Week 8: v0.5 Testing & Release Prep
- [ ] Full test suite: 25+ tests passing
- [ ] Integration test with Docker Compose (SearXNG + PyStreamMCP)
- [ ] Benchmark: latency, throughput (goal: <2s for 3 URLs)
- [ ] Documentation: web usage guide, SearXNG setup, environment variables
- [ ] Changelog: v0.5.0 released
- [ ] Docker image: includes web dependencies

**Deliverable:** v0.5.0 release (web foundation, backward compatible)

**Tests:** 25 passing  
**Coverage:** core/src/web/* fully tested  
**Benchmark:** SearXNG 400ms + Crawl4AI 150ms + Trafilatura 300ms = 850ms (goal: <2s ✓)

---

## v1.0: Core (Weeks 9-18)

### Week 9: StatGuardian WebSourceValidator
- [ ] Design WebSourceValidator type (impl Validator trait)
- [ ] Checks: SSL, domain age, content freshness, authority, language, paywall
- [ ] Integration with existing StatGuardian module
- [ ] Config: min_authority, max_age_days, blocked_domains, whitelist
- [ ] Unit tests (7 tests): each check + combined

**File:** statguardian.rs extension (150 lines)  
**Tests:** 7 passing  
**PR:** Quality gates for web sources

---

### Week 10: OKF Catalog Expansion
- [ ] Create mcp_catalog/web_sources/ directory structure
- [ ] Define 50+ web domains (K8s, Python, Rust, AWS, ML, etc.)
- [ ] YAML format: domain, freshness, authority, covered_topics, quality_notes
- [ ] Link to local data: when web + local = better answer
- [ ] Load OKF web catalog in discovery
- [ ] Unit tests (3 tests): catalog load, parse, linking

**Files:**
- mcp_catalog/web_sources/*.yaml (50 files)
- okf_discovery.py extension (load web sources)

**Tests:** 3 passing  
**PR:** Web sources documented in OKF

---

### Week 11: Routing Logic
- [ ] Implement ContextRouter: local-only, hybrid, web-primary, web-only decisions
- [ ] Score local vs. web relevance
- [ ] Weight merging: default 70% local, 30% web (configurable)
- [ ] Edge cases: sensitive queries (block web), no local data (web-only)
- [ ] Unit tests (8 tests): routing decisions, scoring, merging, edge cases

**File:** core/src/web/router.rs (200 lines)  
**Tests:** 8 passing  
**PR:** Intelligent routing decisions

---

### Week 12: Token Budget for Web
- [ ] Adjust optimization.rs: detect web sources, add web cost
- [ ] Default web cost model: search 50 + crawl 1200 + merge 100 = 1350 tokens
- [ ] Dynamic adjustment: if web enabled, max_tokens → max_tokens + 1350
- [ ] Strategy options: (1) increase budget, (2) reduce local data, (3) fewer web URLs
- [ ] Unit tests (5 tests): cost estimation, budget adjustment, strategies

**Files:** optimization.rs extension (100 lines)  
**Tests:** 5 passing  
**PR:** Web cost modeling

---

### Week 13: Parallel Discovery
- [ ] Modify discovery to run local + web in parallel (tokio tasks)
- [ ] Merge results after both complete (or timeout)
- [ ] Timeout: web has 1s budget (fail gracefully if SearXNG slow)
- [ ] Unit tests (4 tests): parallel execution, merge, timeout handling

**Files:** discovery.rs extension (80 lines)  
**Tests:** 4 passing  
**PR:** Parallel local + web discovery

---

### Week 14: Quality Gates & Validation
- [ ] Wire StatGuardian WebSourceValidator into discovery
- [ ] Block sources that fail validation (low authority, no SSL, stale)
- [ ] Log validation results (audit trail)
- [ ] Configuration: set min_authority, blocked_domains via env/config
- [ ] Unit tests (6 tests): gate enforcement, logging, config override

**Files:**
- discovery.rs integration
- Config schema update

**Tests:** 6 passing  
**PR:** Quality gates enforced

---

### Week 15: CLI & API Updates
- [ ] Add --include-web flag to query CLI
- [ ] Add --explain-routing flag (show why local vs. web)
- [ ] New CLI commands: web-sources list, web-sources validate
- [ ] REST API: new web_enabled parameter in /query endpoint
- [ ] Unit tests (5 tests): CLI parsing, API parameters

**Files:** cli.rs, api.rs, mcp_server.py  
**Tests:** 5 passing  
**PR:** User-facing web control

---

### Week 16: Integration Tests (v1.0 End-to-End)
- [ ] Full pipeline test: query → web detection → parallel discovery → validation → routing → optimize → response
- [ ] 5 end-to-end scenarios:
  1. Local-only (web not triggered)
  2. Hybrid (web + local)
  3. Web-primary (local low relevance)
  4. Validation gate (block low-quality source)
  5. Error handling (SearXNG down, fallback to DuckDuckGo)
- [ ] Unit tests (10 tests): scenarios + error paths

**Files:** tests/test_web_integration.rs  
**Tests:** 10 passing  
**Total tests:** 100+ passing

---

### Week 17: Performance & Benchmark
- [ ] Benchmark: latency for local-only, hybrid, web-only queries
- [ ] Goal: web latency <1.5s p95 (acceptable for agent context)
- [ ] Throughput: 10+ QPS for web queries
- [ ] Memory: baseline + web overhead
- [ ] Optimize: parallel crawling, caching, early termination
- [ ] Document results

**Deliverable:** Performance report (latency, throughput, memory)

---

### Week 18: v1.0 Release & Documentation
- [ ] All 100+ tests passing
- [ ] Full test coverage: core/src/web/* + modified modules
- [ ] User documentation: web queries, configuration, limitations
- [ ] Architecture docs: design decisions, routing logic, token costs
- [ ] Migration guide: from v0.4 (backward compatible)
- [ ] Examples: web-enabled queries in Langchain, Llamaindex
- [ ] Changelog: v1.0.0 released
- [ ] Update README with web capability

**Deliverable:** v1.0.0 release (web as core feature)

**Tests:** 100+ passing  
**Coverage:** All web modules + integration  
**Documentation:** Complete

---

## v1.1: Scale (Weeks 19-30, Q1-Q2 2027)

### Weeks 19-24: Scrapy Site Spiders
- [ ] Define 10+ domain-specific spiders (K8s, Python, Rust, AWS, etc.)
- [ ] Crawl strategy: weekly, cache results, update OKF
- [ ] Knowledge graph extraction: entities, relationships
- [ ] Quality checks: deduplication, freshness validation
- [ ] Tests (20 tests)

### Weeks 25-30: Knowledge Graphs & Semantic Search
- [ ] Build knowledge graph storage (Postgres or DuckDB)
- [ ] Extract entities (classes, functions, types)
- [ ] Extract relationships (inherits, implements, depends)
- [ ] Vector embeddings (optional): semantic search over web content
- [ ] Tests (30 tests)

**Total v1.1:** 600 hours, 12 weeks

---

## Deliverable Summary

| Phase | Version | Hours | Weeks | Tests | Status |
|---|---|---|---|---|---|
| Foundation | v0.5 | 400 | 8 | 25+ | Ready |
| Core | v1.0 | 500 | 10 | 40+ | Ready |
| Scale | v1.1 | 600 | 12 | 50+ | Planned |
| **Total** | **v1.1** | **1500** | **30** | **115+** | **Roadmap** |

---

## Critical Path

**Blocking dependencies:**
1. ✅ Week 1: Architecture review → Weeks 2-7 (foundation)
2. ✅ Weeks 2-5: Core modules (detector, search, crawl, extract) → Week 6-7 (integration)
3. ✅ Week 7: Discovery integration → Week 9-14 (validation + routing)
4. ✅ Weeks 9-14: Core features → Week 15-16 (API + tests)

**No blocking dependencies between v0.5 and v1.0.** Can run in parallel (weeks 1-18 sequential).

---

## Risk Mitigation

| Risk | Week | Mitigation |
|---|---|---|
| SearXNG deployment issues | Week 1 | Docker Compose tested locally before Week 3 |
| Crawl4AI library stability | Week 4 | Use subprocess (safer than PyO3) |
| Trafilatura accuracy | Week 5 | BeautifulSoup4 fallback (100% reliability) |
| StatGuardian integration complexity | Week 9 | Design with StatGuardian team early (Week 1) |
| Performance regressions | Week 16 | Baseline benchmarks established Week 1 |

---

## Approval Gates

| Gate | Week | Owner | Pass Condition |
|---|---|---|---|
| Architecture review | 1 | Team | Sign-off on OSS choices + roadmap |
| Web foundation PoC | 8 | Lead | v0.5 tests passing + SearXNG working |
| v1.0 core feature complete | 18 | Lead | 100+ tests passing + docs complete |
| v1.0 release | 18 | Lead | All deliverables met, no P0 bugs |

---

## Success Criteria (v1.0)

- ✅ 100+ tests passing (25+ in v0.5, 40+ new in v1.0)
- ✅ Web detection accuracy >90% (manual verification)
- ✅ Validation gate precision >95% (block/allow correctness)
- ✅ Latency p95 <1.5s (web path)
- ✅ Throughput 10+ QPS (web queries)
- ✅ 50+ OKF web domains documented
- ✅ Backward compatible (existing queries unchanged)
- ✅ Zero commercial APIs (OSS-only)
- ✅ Full documentation (usage, architecture, examples)
- ✅ Production Docker Compose setup

---

## Team Capacity

**Estimated team size: 2-3 developers**

- **Developer 1:** Weeks 1-8 (foundation), Weeks 11-13 (routing + optimization)
- **Developer 2:** Weeks 2-5 (modules), Weeks 9-10 (StatGuardian + OKF), Weeks 14-18 (integration + release)
- **Developer 3 (optional):** Weeks 15-18 (performance, docs, examples)

**Total: 1500 person-hours = 750 person-weeks with 2 developers**

---

**Ready to start Week 1. Architecture approved? → Begin implementation.**
