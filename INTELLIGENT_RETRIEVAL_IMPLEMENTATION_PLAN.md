# PyStreamMCP: Intelligent Relevance-Optimized MCP Retrieval
## Implementation Blueprint

**Date:** July 22, 2026  
**Vision:** "Retrieve less. Understand more. Deliver only what matters."  
**Target Release:** v0.5 (Sep-Oct 2026) + v1.0 (Nov-Jan 2027)

---

## Architecture Overview

```
User Request
    ↓
[1] Intent Detection ← Extract what problem we're actually solving
    ↓
[2] Query Expansion ← Enrich with related concepts
    ↓
[3] Metadata Filtering (Stage 1) ← Pre-retrieval ranking (70-85% reduction)
    ├─ Web: Rank by authority/freshness/relevance
    ├─ Database: Select tables by cardinality/recency
    └─ MCP Tools: Rank by success-rate/capability match
    ↓
[4] Selective Retrieval ← Invoke only top-ranked sources
    ├─ Web: Crawl highest-authority URL only
    ├─ Database: Query only necessary columns/rows
    └─ Tool: Invoke best-matched tool
    ↓
[5] Evidence Extraction ← Transform raw data into findings
    ↓
[6] Contextual Reranking (Stage 2) ← Post-retrieval ranking (70-80% reduction)
    ├─ Complexity Detection (Simple/Moderate/Complex/Very Complex)
    ├─ Tier Assignment (Minimal 50-100 / Standard 500-1K / Large 2-3K / Comprehensive 5K+)
    ├─ Intent Allocation (flexible within tier)
    ├─ Token Multiplier (critical keywords expand budget)
    └─ Relevance Ranking (only highest-value items)
    ↓
[7] Context Compression ← Summarize findings with evidence
    ↓
[8] Quality Validation (StatGuardian) ← Verify usability
    ↓
[9] Relevance Scoring ← Attach confidence + reasoning
    ↓
Agent Response ← Minimal, high-value, auditable context
```

---

## Component Breakdown & Implementation Priority

### PHASE 1: Intent & Query Understanding (v0.5, Weeks 1-2)

#### 1.1: Intent Detector
**What:** Extract actual information need from query.

**Implementation:**
```rust
// core/src/retrieval/intent.rs
pub enum QueryIntent {
    RootCauseAnalysis,      // Why did X fail?
    StateInquiry,           // What's current X?
    PredictionRequest,      // Will X happen?
    DecisionSupport,        // How to achieve X?
    HistoricalAnalysis,     // Has X changed over time?
    ComparisonRequest,      // How does X compare to Y?
    ConfigurationRequest,   // How to set up X?
    ValidationRequest,      // Is X correct/valid?
}

pub struct IntentDetector {
    patterns: HashMap<String, QueryIntent>,
    ml_model: Option<RelevanceModel>,  // Optional ML-based detection
}

impl IntentDetector {
    pub fn detect(&self, query: &str) -> QueryIntent { }
    pub fn confidence(&self) -> f32 { }  // 0.0-1.0
    pub fn related_intents(&self) -> Vec<QueryIntent> { }
}
```

**Testing:**
- 15 test cases covering all intent types
- Ambiguous query handling (multiple intents)
- Intent confidence scoring

---

#### 1.2: Query Expansion Engine
**What:** Enrich queries with synonyms, related concepts, alternative phrasings.

**Implementation:**
```rust
// core/src/retrieval/expansion.rs
pub struct QueryExpander {
    semantic_graph: SemanticGraph,  // Concept relationships
    domain_knowledge: DomainKnowledge,  // Robot, networking, etc.
}

pub struct ExpandedQuery {
    original: String,
    expansions: Vec<Expansion>,
    weights: Vec<f32>,  // How important each expansion is
}

pub struct Expansion {
    term: String,
    expansion_type: ExpansionType,  // Synonym, Related, Alternative
    confidence: f32,
}

impl QueryExpander {
    pub fn expand(&self, query: &str) -> ExpandedQuery { }
    pub fn ranked_terms(&self) -> Vec<(String, f32)> { }  // term + weight
}
```

**Testing:**
- Expansion correctness (right concepts identified)
- Weight appropriateness (important terms ranked higher)
- Domain-specific expansions

---

### PHASE 2: Metadata Filtering - Stage 1 (v0.5, Weeks 3-6)

#### 2.1: Metadata Repository
**What:** Maintain profiles of all retrieval sources (web domains, databases, MCP tools).

**Implementation:**
```rust
// core/src/retrieval/metadata/repository.rs
pub struct SourceMetadata {
    id: String,
    source_type: SourceType,  // Web, Database, MCPTool, Cache
    authority: f32,  // 0.0-1.0 (domain trustworthiness)
    freshness: f32,  // 0.0-1.0 (how current is data?)
    latency: Duration,  // How long to retrieve?
    coverage: f32,  // 0.0-1.0 (topic coverage breadth)
    accuracy: f32,  // 0.0-1.0 (reliability based on validation)
    success_rate: f32,  // Fraction of successful queries
    cost_per_query: TokenCount,
    last_updated: Timestamp,
}

pub struct MetadataRepository {
    sources: HashMap<String, SourceMetadata>,
    version: Timestamp,  // Allows time-travel queries
}

impl MetadataRepository {
    pub fn rank_sources(&self, intent: &QueryIntent) -> Vec<(String, f32)> { }
    pub fn get_metadata(&self, source_id: &str) -> SourceMetadata { }
    pub fn update_accuracy(&mut self, source_id: &str, result: &ValidationResult) { }
}
```

**Seed Data (v0.5):**
- 50+ web domains (HBR, MIT, arxiv, etc.)
- 25+ database systems (PostgreSQL, MongoDB, BigQuery)
- 20+ MCP tool profiles

---

#### 2.2: Metadata Filter Engine
**What:** Rank sources by metadata before any retrieval happens.

**Implementation:**
```rust
// core/src/retrieval/metadata/filter.rs
pub struct MetadataFilter {
    repository: MetadataRepository,
    query_matcher: QueryMatcher,  // Maps queries to topics
}

pub struct FilterResult {
    source_id: String,
    metadata: SourceMetadata,
    relevance_score: f32,  // How well does this source match?
    ranking_reason: String,  // "High authority (0.95), Good coverage (0.88)"
}

impl MetadataFilter {
    pub fn filter(&self, intent: &QueryIntent, expanded_query: &ExpandedQuery) 
        -> Vec<FilterResult> { }  // Top-3 or top-1 based on strategy
    
    pub fn filter_with_constraints(&self, 
        intent: &QueryIntent, 
        expanded_query: &ExpandedQuery,
        max_latency: Duration,
        max_cost: TokenCount,
    ) -> Vec<FilterResult> { }
}
```

**Scoring Formula:**
```
RelevanceScore = 0.35 * authority 
               + 0.25 * freshness 
               + 0.20 * coverage
               + 0.15 * query_relevance
               + 0.05 * success_rate
```

---

#### 2.3: Metadata Caching
**What:** Cache metadata decisions to avoid recomputing rankings.

**Implementation:**
```rust
// core/src/retrieval/metadata/cache.rs
pub struct MetadataCache {
    cache: LRU<String, CachedDecision>,
    ttl: Duration,
}

pub struct CachedDecision {
    intent: QueryIntent,
    expanded_terms: Vec<String>,
    filtered_sources: Vec<FilterResult>,
    timestamp: Timestamp,
    hit_count: u32,
}

impl MetadataCache {
    pub fn get_or_compute(&mut self, 
        intent: &QueryIntent, 
        query: &str,
        compute_fn: impl Fn() -> Vec<FilterResult>
    ) -> Vec<FilterResult> { }
    
    pub fn invalidate_source(&mut self, source_id: &str) { }  // When source updates
}
```

---

### PHASE 3: Selective Retrieval (v1.0, Weeks 7-10)

#### 3.1: Web Retrieval
**What:** Crawl only the highest-ranked URL.

**Implementation:**
```rust
// core/src/retrieval/web/crawler.rs
pub struct WebCrawler {
    client: HttpClient,
    extractor: ContentExtractor,
}

pub struct CrawledContent {
    url: String,
    title: String,
    sections: Vec<Section>,  // Hierarchical content
    structured_data: Option<StructuredData>,  // Tables, lists, etc.
    timestamp: Timestamp,
}

pub struct Section {
    heading: String,
    content: String,
    depth: u32,  // h1, h2, h3, etc.
    relevance_keywords: Vec<String>,
}

impl WebCrawler {
    pub fn crawl(&self, url: &str) -> Result<CrawledContent> { }
    pub fn crawl_with_intent(&self, url: &str, intent: &QueryIntent) 
        -> Result<CrawledContent> { }  // Extract only intent-relevant sections
}
```

**Tools:** Crawl4AI + Trafilatura (OSS, no vendor lock-in)

---

#### 3.2: Database Selective Query
**What:** Query only necessary columns/rows.

**Implementation:**
```rust
// core/src/retrieval/database/selector.rs
pub struct DatabaseSelector {
    schema_analyzer: SchemaAnalyzer,
}

pub struct SelectiveQuery {
    table: String,
    columns: Vec<String>,  // Only needed columns
    filter: Option<String>,  // WHERE clause restricting rows
    limit: usize,  // How many rows?
    order_by: Option<String>,
}

impl DatabaseSelector {
    pub fn select_columns(&self, table: &str, intent: &QueryIntent) 
        -> Vec<String> { }
    
    pub fn select_rows(&self, table: &str, query: &str, max_rows: usize) 
        -> String { }  // WHERE clause
    
    pub fn build_selective_query(&self, 
        table: &str, 
        intent: &QueryIntent,
        limit: usize
    ) -> SelectiveQuery { }
}
```

**Example:**
```
Query: "Why did robot stop?"

Without selector:
SELECT * FROM logs;  ← 1M rows, 20 columns, 50MB

With selector:
SELECT timestamp, subsystem, severity, message 
FROM logs 
WHERE subsystem IN ('navigation', 'motor', 'power')
  AND severity >= 'ERROR'
  AND timestamp > NOW() - INTERVAL '2 hours'
LIMIT 50;  ← 50 rows, 4 columns, 2KB
```

---

#### 3.3: MCP Tool Selector
**What:** Invoke only the best-ranked tool.

**Implementation:**
```rust
// core/src/retrieval/mcp/tool_selector.rs
pub struct MCPToolSelector {
    registry: MCPRegistry,
    success_tracker: SuccessTracker,
}

pub struct ToolSelection {
    tool_id: String,
    relevance_score: f32,
    capability_match: f32,  // Does this tool solve this problem?
    estimated_cost: TokenCount,
    reason: String,
}

impl MCPToolSelector {
    pub fn select_tool(&self, intent: &QueryIntent) -> Option<ToolSelection> { }
    pub fn select_top_k(&self, intent: &QueryIntent, k: usize) 
        -> Vec<ToolSelection> { }
}
```

---

### PHASE 4: Evidence Extraction & Compression (v1.0, Weeks 8-9)

#### 4.1: Evidence Extractor
**What:** Transform raw data into findings with evidence.

**Implementation:**
```rust
// core/src/retrieval/evidence.rs
pub struct Finding {
    claim: String,  // "Robot drifted left"
    confidence: f32,  // 0.0-1.0
    evidence: Vec<Evidence>,  // Supporting data points
}

pub struct Evidence {
    source: String,  // "Wheel encoder", "IMU", "Camera"
    data: String,  // Actual measurement/observation
    relevance: f32,  // How directly does this support the claim?
}

pub struct EvidenceExtractor {
    llm_client: LLMClient,  // For intelligent extraction
    rules: Vec<ExtractionRule>,  // Domain-specific rules
}

impl EvidenceExtractor {
    pub fn extract(&self, content: &Content, intent: &QueryIntent) 
        -> Vec<Finding> { }
    
    pub fn extract_with_evidence(&self, content: &Content, intent: &QueryIntent)
        -> Vec<(Finding, Vec<Evidence>)> { }
}
```

---

#### 4.2: Context Compressor
**What:** Summarize content into actionable context.

**Implementation:**
```rust
// core/src/retrieval/compression.rs
pub struct CompressedContext {
    summary: String,  // High-level takeaway
    key_findings: Vec<Finding>,  // Top 3-5 findings
    anomalies: Vec<Anomaly>,  // Unexpected patterns
    recommended_actions: Vec<String>,  // Next steps
    token_budget_used: usize,
    compression_ratio: f32,  // Original / compressed tokens
}

pub struct Compressor {
    summarizer: Summarizer,
    anomaly_detector: AnomalyDetector,
}

impl Compressor {
    pub fn compress(&self, content: &Content, budget: TokenCount)
        -> CompressedContext { }
    
    pub fn compress_hierarchical(&self, 
        content: &Content, 
        budgets: &[TokenCount]
    ) -> Vec<CompressedContext> { }  // Multiple detail levels
}
```

---

### PHASE 5: Contextual Reranking - Stage 2 (v1.0, Weeks 10-14)

#### 5.1: Complexity Classifier
**What:** Detect query complexity to assign appropriate detail level.

**Implementation:**
```rust
// core/src/retrieval/complexity.rs
pub enum ComplexityLevel {
    Simple,      // Direct facts, single step
    Moderate,    // Multi-step reasoning, some context
    Complex,     // Multiple entities, intricate relationships
    VeryComplex, // Novel problem, requires deep analysis
}

pub struct ComplexityClassifier {
    feature_extractor: FeatureExtractor,
    model: Option<ClassificationModel>,
}

pub struct ComplexityScore {
    level: ComplexityLevel,
    confidence: f32,
    explanation: String,  // "3 entities + 2 relationships = Complex"
}

impl ComplexityClassifier {
    pub fn classify(&self, query: &str, intent: &QueryIntent) 
        -> ComplexityScore { }
}

pub struct TokenTierAssignment {
    level: ComplexityLevel,
    min_tokens: usize,
    max_tokens: usize,
    suggested_tokens: usize,  // Based on intent
}

// Tier Mapping:
// Simple: 50-100 tokens
// Moderate: 500-1000 tokens
// Complex: 2000-3000 tokens
// VeryComplex: 5000-8000 tokens
```

---

#### 5.2: Intent-Based Allocation
**What:** Allocate tokens within tier based on how much detail is needed.

**Implementation:**
```rust
// core/src/retrieval/allocation.rs
pub struct IntentAllocator {
    tier_map: HashMap<ComplexityLevel, TokenBudget>,
}

pub struct TokenAllocation {
    base_tier: TokenBudget,
    intent_multiplier: f32,  // 0.5 - 2.0
    allocated_tokens: usize,
    rationale: String,
}

impl IntentAllocator {
    pub fn allocate(&self, 
        complexity: &ComplexityScore,
        intent: &QueryIntent
    ) -> TokenAllocation { }
    
    pub fn apply_multiplier(&mut self, 
        keywords: &[String],  // CRITICAL, URGENT, PRODUCTION
        multiplier: f32
    ) -> TokenAllocation { }
}

// Example Multipliers:
// "CRITICAL": 2.0x
// "PRODUCTION": 1.8x
// "URGENT": 1.5x
// "debug": 0.8x (less detail needed)
```

---

#### 5.3: Relevance Ranker
**What:** Rank retrieved content by relevance to query intent.

**Implementation:**
```rust
// core/src/retrieval/ranking.rs
pub struct RankedContent {
    item: String,  // Section, finding, log line
    relevance_score: f32,  // 0.0-1.0
    scoring_breakdown: ScoringBreakdown,
    token_count: usize,
}

pub struct ScoringBreakdown {
    semantic_match: f32,      // 0.40 weight
    keyword_match: f32,       // 0.25 weight
    temporal_relevance: f32,  // 0.15 weight (recent > old)
    evidence_strength: f32,   // 0.10 weight (direct > indirect)
    user_intent_match: f32,   // 0.10 weight
}

pub struct ContentRanker {
    semantic_model: SemanticModel,
    keyword_matcher: KeywordMatcher,
    temporal_scorer: TemporalScorer,
}

impl ContentRanker {
    pub fn rank(&self, 
        content_items: &[ContentItem],
        query: &str,
        intent: &QueryIntent
    ) -> Vec<RankedContent> { }
    
    pub fn select_within_budget(&self,
        ranked: Vec<RankedContent>,
        budget: TokenCount
    ) -> Vec<RankedContent> { }  // Include items until budget exhausted
}
```

---

#### 5.4: Quality Validation (StatGuardian)
**What:** Verify context is usable before sending to agent.

**Implementation:**
```rust
// core/src/retrieval/quality.rs
pub struct QualityCheck {
    is_valid: bool,
    confidence: f32,
    issues: Vec<QualityIssue>,
}

pub enum QualityIssue {
    OutdatedInformation,
    ConflictingData,
    IncompleteContext,
    AmbiguousFindings,
    LowSourceReliability,
}

pub struct QualityValidator {
    statguardian_client: StatGuardianClient,
}

impl QualityValidator {
    pub fn validate(&self, context: &CompressedContext) 
        -> QualityCheck { }
    
    pub fn suggest_alternatives(&self, 
        context: &CompressedContext,
        quality_issues: &[QualityIssue]
    ) -> Vec<AlternativeSource> { }  // Fallback sources
}
```

---

### PHASE 6: Relevance Scoring & Response (v1.0, Weeks 14-18)

#### 6.1: Relevance Scorer
**What:** Attach confidence + reasoning to every response.

**Implementation:**
```rust
// core/src/retrieval/scoring.rs
pub struct ScoredResponse {
    content: CompressedContext,
    relevance: RelevanceScore,
    audit_trail: AuditTrail,
}

pub struct RelevanceScore {
    overall: f32,  // 0.0-1.0
    reasoning: String,  // "High semantic match (0.95) + direct evidence (0.9)"
    components: HashMap<String, f32>,  // Breakdown by scoring factor
    confidence_level: ConfidenceLevel,  // Low, Medium, High, Very High
}

pub enum ConfidenceLevel {
    Low,      // < 0.6
    Medium,   // 0.6-0.75
    High,     // 0.75-0.9
    VeryHigh, // > 0.9
}

pub struct AuditTrail {
    intent_detected: QueryIntent,
    sources_considered: Vec<String>,
    sources_selected: Vec<String>,
    complexity_level: ComplexityLevel,
    tokens_allocated: usize,
    tokens_used: usize,
    compression_ratio: f32,
}

impl ScoredResponse {
    pub fn explain(&self) -> String { }  // Human-readable explanation
}
```

---

#### 6.2: Agent-Optimized Response
**What:** Format response for maximum agent utility.

**Implementation:**
```rust
// core/src/retrieval/response.rs
pub struct AgentResponse {
    context: String,  // Actual context to use
    metadata: ResponseMetadata,
    layers: Vec<DetailLayer>,  // For progressive disclosure
}

pub struct ResponseMetadata {
    source: String,
    relevance: RelevanceScore,
    quality: QualityCheck,
    freshness: Timestamp,
    next_steps: Vec<String>,  // Recommended agent actions
    confidence: f32,
    audit_trail: AuditTrail,
}

pub struct DetailLayer {
    level: u32,  // 0=summary, 1=findings, 2=evidence, 3=raw
    content: String,
    tokens: usize,
}

impl AgentResponse {
    pub fn to_llm_context(&self) -> String { }  // Format for LLM
    pub fn to_human_summary(&self) -> String { }  // Format for human review
}
```

---

## Success Metrics

### Data Reduction
- **Stage 1 (Metadata Filtering):** 70-85% candidate reduction (before retrieval)
- **Stage 2 (Contextual Reranking):** 70-80% data reduction (after retrieval)
- **Combined:** 90-95% total data reduction vs. baseline

### Quality Metrics
- **Relevance@5:** Fraction of top-5 items relevant to query (target: >90%)
- **Precision:** Only high-value context retrieved (target: >95%)
- **Recall:** Necessary context not missed (target: >80%)
- **Token Efficiency:** Tokens used / tokens in full context (target: <10%)

### Agent Metrics
- **Reasoning Steps Reduction:** Steps to root cause analysis (baseline → 40% reduction)
- **Debugging Time:** Hours to resolve issues (baseline → 50% reduction)
- **Root Cause Discovery Rate:** % of queries where cause is found (target: >85%)

### System Metrics
- **Latency:** Metadata filtering + selective retrieval (target: <500ms)
- **Cost:** Token consumption per query (target: <10% of unoptimized)
- **Consistency:** Same query → same top-3 results (target: >99%)

---

## Testing Strategy

### Unit Tests (70 tests for v0.5, 180+ for v1.0)
- Intent detection: 15 tests
- Query expansion: 12 tests
- Metadata filtering: 18 tests
- Selective retrieval: 20 tests
- Complexity classification: 12 tests
- Ranking: 25 tests
- Quality validation: 15 tests
- Scoring: 12 tests
- Integration: 50+ tests

### Integration Tests
- End-to-end retrieval (query → response)
- Multi-source correlation
- Fallback chain handling
- Budget constraint adherence
- Audit trail correctness

### Performance Tests
- Latency under load
- Metadata filter scaling (1K+ sources)
- Token counting accuracy
- Memory usage (cache sizing)

---

## Rollout Plan

### v0.5.0 (Sep-Oct 2026)
**Foundation for Selective Intelligence**
- Phases 1-2 complete (Intent + Metadata Filtering)
- Backward compatible, no breaking changes
- Docs + examples for all new modules
- 70 tests (35 unit + 35 integration)

### v1.0.0 (Nov-Jan 2027)
**Production Selective Intelligence**
- Phases 3-6 complete (Selective Retrieval + Reranking + Scoring)
- Stable API, production-ready
- Observability (OTel traces for all decisions)
- 180+ tests (85+ unit + 95+ integration)

---

## Next Steps

1. **This Week:** Review architecture, identify blockers
2. **Week 1:** Implement IntentDetector + QueryExpander (Phase 1)
3. **Week 2-6:** Build MetadataRepository + MetadataFilter + Cache (Phase 2)
4. **Week 7-18:** Implement Retrieval, Reranking, Scoring (Phases 3-6)

---

## References

- **Roadmap:** IMPLEMENTATION_ROADMAP_COMPLETE_2026.md
- **Two-Stage Architecture:** ARCHITECTURE_TWO_STAGE_SELECTIVE_INTELLIGENCE.md
- **Integration:** ROADMAP_INTEGRATED.md
- **Web Knowledge:** WEB_KNOWLEDGE_OSS_TOOLS_MATRIX.md
