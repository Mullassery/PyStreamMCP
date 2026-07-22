# Web Knowledge Acquisition: Document Index

**Status:** Complete revision delivered  
**Total Documentation:** 2000 lines across 4 documents  
**Review Time:** 30 minutes (exec summary) to 2 hours (full detail)

---

## Documents Overview

### 1. PLAN_WEB_KNOWLEDGE_OSS_REVISION.md (489 lines)
**Best For:** Understanding the full architecture and roadmap

**Sections:**
- **OSS Architecture (30%):** SearXNG, Crawl4AI, Trafilatura, StatGuardian WebValidator
  - Tool selection rationale (why OSS, not commercial APIs)
  - Self-hosted vs. SaaS cost comparison ($0 vs. $100+/mo)
  - Quality guarantees without APIs
  
- **Core Integration Strategy (40%):** How web knowledge fits into query planning
  - Query planning flow: detect web-needing queries → parallel discovery → merge + validate → route
  - Token budget impact: +1650 tokens per web query
  - StatGuardian integration: WebSourceValidator checks (SSL, freshness, authority)
  - OKF catalog expansion: 50+ web domains as first-class discovery targets
  - Routing logic: local-only vs. hybrid (weighted) vs. web-primary decisions
  
- **Revised Roadmap (30%):** Phase breakdown
  - **v0.5 (8 weeks):** Web foundation (detection, search, crawl, extract, basic validation)
  - **v1.0 (10 weeks):** Web as core feature (StatGuardian gates, OKF catalog, routing, parallel discovery)
  - **v1.1 (12 weeks):** Web at scale (site-specific Scrapy spiders, knowledge graphs)

- **Architecture Diagram:** Visual flow from agent query → context response
- **Decision Points:** Why SearXNG, why Crawl4AI, why v1.0 not v1.5, why StatGuardian validation
- **Key Differences:** v1.0 vs. v0.4 (sources, discovery, detection, budgets, validation, routing, catalog, tests)

**Reading Time:** 45 minutes  
**Audience:** Architects, tech leads, decision makers

---

### 2. WEB_KNOWLEDGE_OSS_TOOLS_MATRIX.md (784 lines)
**Best For:** Technical tool evaluation and implementation details

**Sections:**
- **Search Layer:** SearXNG (primary), DuckDuckGo (fallback), Searx (legacy), Elasticsearch (local index)
  - API examples (reqwest client code)
  - Metrics: latency, throughput, accuracy, cost
  - Pros/cons for each tool
  - Migration path from SerpAPI

- **Crawling Layer:** Crawl4AI (primary), Scrapy (site mapping), Selenium/Playwright (JS rendering)
  - Deployment examples (Docker, async pools)
  - Performance comparison: 200 sites/sec vs. 50-100 pages/sec
  - When to use each tool

- **Content Extraction:** Trafilatura (primary), BeautifulSoup4 (fallback)
  - API code showing markdown conversion, metadata extraction
  - Accuracy metrics and latency
  - Fallback strategy

- **Validation Layer:** StatGuardian WebSourceValidator (new), langdetect (language filtering)
  - Validation checks: SSL, domain age, freshness, authority, paywall
  - Code examples: Python functions for each check
  - Whitelist/blacklist configuration

- **Comparison Matrix:** Throughput + cost across all components
- **Dependency Tree:** Full OSS package graph
- **Migration Path:** Drop-in replacement for SerpAPI

**Reading Time:** 60 minutes  
**Audience:** Backend engineers, DevOps, infrastructure planners

---

### 3. WEB_KNOWLEDGE_EXECUTIVE_SUMMARY.md (361 lines)
**Best For:** Quick overview and business case

**Sections:**
- **The Opportunity:** Why web knowledge matters (60-75% reduction only on 30% of queries currently)
- **Why v1.0, Not v1.5:** Competitive gap, effort fit, architecture readiness
- **Architecture at a Glance:** Simple before/after flow diagram
- **OSS-Only Tools:** Quick table of tools + costs
- **What Changes in v1.0 vs. v0.4:** Code modules, API changes, breaking changes (none)
- **Three-Phase Rollout:** v0.5 → v1.0 → v1.1
- **Token Budget Impact:** Cost of web retrieval, strategy options
- **Quality Gates:** StatGuardian validation configuration
- **Deployment:** Minimal vs. production setup
- **Success Metrics:** Coverage, accuracy, latency, throughput, test count, catalog size
- **Competitive Positioning:** How v1.0 differentiates from competitors
- **Risks & Mitigations:** SearXNG availability, content quality, crawl latency, false triggers
- **Roadmap Integration:** Fits into existing phases (v0.5 as Phase 4A, v1.0 as Phase 4B+5)
- **Next Steps:** Review → architecture → spike → v0.5 start

**Reading Time:** 15 minutes  
**Audience:** Product managers, executives, stakeholders

---

### 4. WEB_KNOWLEDGE_IMPLEMENTATION_CHECKLIST.md (364 lines)
**Best For:** Week-by-week execution plan and task tracking

**Sections:**
- **v0.5 Foundation (Weeks 1-8):**
  - Week 1: Setup, SearXNG Docker
  - Week 2: Web detection (temporal keywords, freshness, confidence)
  - Week 3: SearXNG HTTP client + DuckDuckGo fallback
  - Week 4: Crawl4AI parallel integration (4 concurrent crawls)
  - Week 5: Trafilatura + BeautifulSoup4 extraction
  - Week 6: Domain validation (SSL, Wayback Machine, freshness, authority)
  - Week 7: Integration with discovery (add SourceType::Web)
  - Week 8: v0.5 release (25+ tests, benchmarks, docs)

- **v1.0 Core (Weeks 9-18):**
  - Week 9: StatGuardian WebSourceValidator
  - Week 10: OKF catalog expansion (50+ web domains)
  - Week 11: Routing logic (local-only, hybrid, web-primary)
  - Week 12: Token budget modeling for web cost
  - Week 13: Parallel discovery (local + web)
  - Week 14: Quality gates enforcement
  - Week 15: CLI + API updates (--include-web, --explain-routing)
  - Week 16: End-to-end integration tests (10 scenarios)
  - Week 17: Performance benchmark (<1.5s latency goal)
  - Week 18: v1.0 release (100+ tests, full docs)

- **v1.1 Scale (Weeks 19-30):**
  - Weeks 19-24: Scrapy site-specific spiders (10+ domains)
  - Weeks 25-30: Knowledge graphs + optional vector DB

- **Deliverable Summary:** Hours, weeks, tests per phase
- **Critical Path:** Dependencies, parallel vs. sequential tasks
- **Risk Mitigation:** Deployment, library stability, performance issues
- **Approval Gates:** Architecture review, PoC, core features, release
- **Success Criteria:** Tests, accuracy, latency, throughput, OKF catalog, backward compatibility
- **Team Capacity:** 2-3 developers, 750 person-weeks total

**Reading Time:** 30 minutes  
**Audience:** Project managers, team leads, engineers

---

## Quick Navigation

**I need to understand...**

| Question | Read This |
|----------|-----------|
| "Why web knowledge in v1.0?" | Executive Summary → Roadmap section |
| "Which OSS tools should we use?" | OSS Tools Matrix → Search/Crawl/Extract sections |
| "How does web integrate with query planning?" | Plan Revision → Core Integration section + architecture diagram |
| "What's the week-by-week plan?" | Implementation Checklist → v0.5 + v1.0 sections |
| "How much will it cost?" | OSS Tools Matrix → cost comparison tables + Executive Summary → deployment |
| "What are the risks?" | Executive Summary → risks + mitigations |
| "What are the changes from v0.4?" | Executive Summary → What Changes section |
| "How do I deploy this?" | Executive Summary → deployment + Plan Revision → production deployment |
| "What will we deliver?" | Implementation Checklist → deliverable summary |
| "How do we validate quality?" | Plan Revision → StatGuardian integration + OSS Tools Matrix → validation layer |

---

## Key Numbers

| Metric | Value |
|---|---|
| **OSS Tools** | 6 core (SearXNG, Crawl4AI, Trafilatura, BeautifulSoup4, langdetect, urlextract) |
| **Cost (self-hosted)** | $0 (or $5/mo cloud SearXNG) |
| **Cost (vs. commercial)** | $0 vs. $100-1000/mo (SerpAPI + Brave) |
| **Implementation time** | 900 hours (v0.5 + v1.0) = 6 months with 2-3 developers |
| **Test coverage** | 25+ (v0.5) + 40+ (v1.0) = 100+ total |
| **Web sources in OKF** | 50+ documented domains |
| **Latency (web path)** | 1.5s target (SearXNG 400ms + Crawl4AI 50ms + extraction 100ms + validation 800ms) |
| **Throughput** | 10+ QPS (web queries) |
| **Token reduction** | 60-75% (same as local-only, now on 80% of queries) |
| **Breaking changes** | 0 (fully backward compatible) |

---

## Document Relationships

```
Executive Summary (quick read)
    ↓ (for details)
    ├─ Plan Revision (full architecture)
    │   ├─ OSS Tools Matrix (implementation details)
    │   └─ Implementation Checklist (week-by-week execution)
    └─ Quick Reference → Use above matrix for decision lookup
```

---

## Review Checklist

- [ ] Executive Summary: Understand opportunity + roadmap (15 min)
- [ ] Plan Revision: Architecture + integration strategy (45 min)
- [ ] OSS Tools Matrix: Verify tool choices + code examples (60 min)
- [ ] Implementation Checklist: Timeline + milestones (30 min)
- [ ] **Total: ~2.5 hours for complete understanding**

---

## Approval Required

**Sign-off needed from:**
1. ✅ **Architecture:** Web knowledge as v1.0 core feature (not v1.5)
2. ✅ **Engineering:** OSS-only approach (no commercial APIs)
3. ✅ **Product:** Roadmap change (v0.5 + v1.0 as sequential phases)
4. ✅ **Timeline:** 900 hours (6 months), fits Q4 2026 + Q1 2027

**Decision:** Proceed with v0.5 implementation (Week 1)?

---

## Version History

| Date | Change | Document |
|---|---|---|
| 2026-07-22 | Initial revision | All 4 documents created |

---

**Generated by:** Claude Code  
**For:** PyStreamMCP web knowledge integration  
**Status:** Ready for implementation

Next step: Review executive summary, approve v1.0 timeline, begin Week 1 planning.
