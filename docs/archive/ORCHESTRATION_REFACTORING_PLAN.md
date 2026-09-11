# PyStreamMCP Orchestration: Refactoring & Cohesion Plan

**Date:** July 22, 2026  
**Phase:** Code Hardening & Architecture Unification  
**Scope:** Make Layers 1-3 more cohesive, testable, and production-ready

---

## Issues Identified

### 1. Weak Error Handling
**Problem:** Inconsistent error handling across modules. Some use `Result`, others panic or return `Option`.

**Current:**
```rust
// Module A: Uses Result
pub fn classify(&self, query: &str) -> Result<IntentResult>

// Module B: Returns Option
pub fn get(&self, server_id: &str) -> Option<MCPServerProfile>

// Module C: No error type
pub fn rank(&servers: &[MCPServerProfile]) -> Vec<ToolRanking>
```

**Impact:** Callers don't know when/how failures occur. Inconsistent error propagation.

---

### 2. Missing Shared Abstractions
**Problem:** Each layer reinvents scoring, ranking, confidence calculation.

**Current Duplication:**
- `ToolRanker::score_server()` manually calculates score
- `ToolSelector::score_server()` duplicates the same logic
- `CapabilityRegistry::rank_sources()` has similar pattern
- No trait-based reusability

**Impact:** Scoring formula changes require updates in 3+ places. Hard to test scoring in isolation.

---

### 3. Weak Type Safety
**Problem:** Heavy use of `String` and `f32` without semantic meaning.

**Current:**
```rust
pub server_id: String,           // What if empty? What if invalid format?
pub rank_score: f32,             // Is this 0-1? Percent? Unbounded?
pub latency_avg_ms: f32,         // Could be negative
pub confidence: f32,             // Is this normalized?
```

**Impact:** No compiler guarantees. Silent bugs (e.g., negative latency). Hard to distinguish meaningful scores.

---

### 4. Inconsistent API Patterns
**Problem:** Builder patterns, constructors, and configuration vary across modules.

**Current:**
```rust
// Layer 1: Direct new() with fields set later
let classifier = IntentClassifier::new();
let entity = Entity { name, entity_type, relevance };

// Layer 2: Partial builders
let profile = MCPServerProfile::new(...).with_capabilities(...).with_metadata(...);

// Layer 3: Standalone functions + structs
ToolSelector::new(registry)
ToolRanker::rank(servers)
PerformanceTracker::default()
```

**Impact:** Inconsistent, hard to learn, easy to misuse.

---

### 5. No Unified Configuration
**Problem:** Each module has its own settings scattered through code.

**Current:**
```rust
// Hardcoded in CapabilityGraph
let min_weight = 0.7;

// Hardcoded in ToolRanker
// 0.35 * success_rate + 0.25 * ...

// Hardcoded in PerformanceTracker
time_window: Duration::from_secs(86400)

// Hardcoded in ToolSelector
let primary_count = (total as f32 * 0.4)
```

**Impact:** Can't customize behavior. Hard to test with different configs. No single source of truth.

---

### 6. Missing Integration Layer
**Problem:** Layers 1-3 exist independently. No unified orchestration API.

**Current:**
```rust
// User must manually orchestrate:
let intent = classifier.classify(query);
let servers = registry.find_by_intent(intent.primary);
let selection = selector.select_with_constraints(&intent, &constraints);
```

**Impact:** Layers don't compose cleanly. Error handling and context passing is manual. Hard to add cross-cutting concerns (logging, tracing, metrics).

---

### 7. Weak Validation
**Problem:** No input validation. Invalid data can silently corrupt state.

**Current:**
```rust
pub server_id: String,        // No validation
pub rank_score: f32,          // No bounds checking
let result = classifier.classify("");  // Empty string accepted
registry.register(profile);   // No duplicate detection
```

**Impact:** Garbage in, garbage out. Silent failures. Hard to debug.

---

### 8. No Observability Hooks
**Problem:** No way to instrument decisions, trace execution, or collect metrics.

**Current:** No logging, no tracing, no metrics collection. Black box system.

**Impact:** Can't debug issues. Can't measure performance. Can't audit decisions.

---

### 9. Serialization Issues
**Problem:** Types use derive but don't consider versioning or compatibility.

**Current:**
```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RankingBreakdown { ... }
// What if we add fields? Breaks old data.
```

**Impact:** Can't version API. Can't save/load state. Can't do cross-process communication.

---

### 10. Testing Gaps
**Problem:** Tests exist but don't cover integration or edge cases.

**Current:**
- Unit tests pass in isolation
- No integration tests between layers
- No property-based tests
- No performance regression tests
- Edge cases (empty inputs, boundary values) not tested

**Impact:** Bugs hide at layer boundaries. Performance regressions go unnoticed. Integration breaks silently.

---

## Refactoring Strategy

### Phase 1: Unified Error Handling

Create a comprehensive error type with full context:

```rust
// core/src/orchestration/error.rs

#[derive(Debug)]
pub enum OrchestrationError {
    IntentClassification {
        query: String,
        reason: String,
    },
    NoServersFound {
        intent: String,
        available_intents: Vec<String>,
    },
    InvalidConfiguration {
        component: String,
        issue: String,
    },
    SelectionFailed {
        intent: String,
        constraints_violated: Vec<String>,
    },
    PerformanceTracking {
        server_id: String,
        reason: String,
    },
    ValidationFailed {
        field: String,
        value: String,
        reason: String,
    },
}

pub type Result<T> = std::result::Result<T, OrchestrationError>;
```

**Benefits:**
- Consistent error handling everywhere
- Rich context for debugging
- Type-safe error handling
- Traceable error chains

---

### Phase 2: Shared Abstractions via Traits

Define core traits used across all layers:

```rust
// core/src/orchestration/traits.rs

/// Anything that can be scored
pub trait Scoreable {
    fn score(&self) -> f32;
    fn score_explanation(&self) -> String;
}

/// Anything that can be ranked
pub trait Rankable: Scoreable {
    fn rank_position(&self) -> usize;
}

/// Anything that produces confidence
pub trait Confidence {
    fn confidence(&self) -> f32;
}

/// Anything queryable
pub trait Queryable {
    type Query;
    type Result;
    fn query(&self, q: Self::Query) -> Result<Vec<Self::Result>>;
}

/// Anything that can be validated
pub trait Validatable {
    fn validate(&self) -> Result<()>;
}

/// Anything that tracks performance
pub trait PerformanceMetric {
    fn record_success(&mut self, latency_ms: f32, cost_tokens: usize);
    fn record_failure(&mut self, reason: &str);
    fn success_rate(&self) -> f32;
}
```

**Benefits:**
- Shared semantics across layers
- Composable designs
- Easy to add new implementations
- Type-safe composition

---

### Phase 3: Strong Typing with Newtypes

Replace raw `String` and `f32` with semantic types:

```rust
// core/src/orchestration/types.rs - New types

/// Uniquely identifies an MCP server
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct ServerId(pub &'static str);

impl ServerId {
    pub fn new(id: &str) -> Result<ServerId> {
        if id.is_empty() || id.len() > 256 || !id.chars().all(|c| c.is_alphanumeric() || c == '_' || c == '-') {
            return Err(OrchestrationError::ValidationFailed {
                field: "server_id".to_string(),
                value: id.to_string(),
                reason: "Must be non-empty, ≤256 chars, alphanumeric/underscore/dash only".to_string(),
            });
        }
        Ok(ServerId(Box::leak(id.to_string().into_boxed_str())))
    }
}

/// Normalized score (0.0-1.0)
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd)]
pub struct Score(f32);

impl Score {
    pub fn new(value: f32) -> Result<Score> {
        if value < 0.0 || value > 1.0 {
            return Err(OrchestrationError::ValidationFailed {
                field: "score".to_string(),
                value: value.to_string(),
                reason: "Score must be 0.0-1.0".to_string(),
            });
        }
        Ok(Score(value))
    }
}

impl From<Score> for f32 {
    fn from(score: Score) -> f32 {
        score.0
    }
}

/// Latency in milliseconds
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd)]
pub struct Latency(pub f32);

impl Latency {
    pub fn new(ms: f32) -> Result<Latency> {
        if ms < 0.0 || ms > 1_000_000.0 {  // 1M ms = ~11 days
            return Err(OrchestrationError::ValidationFailed {
                field: "latency".to_string(),
                value: ms.to_string(),
                reason: "Latency must be 0-1M milliseconds".to_string(),
            });
        }
        Ok(Latency(ms))
    }
}

/// Success rate (0.0-1.0)
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd)]
pub struct SuccessRate(f32);

impl SuccessRate {
    pub fn new(rate: f32) -> Result<SuccessRate> {
        if rate < 0.0 || rate > 1.0 {
            return Err(OrchestrationError::ValidationFailed {
                field: "success_rate".to_string(),
                value: rate.to_string(),
                reason: "Success rate must be 0.0-1.0".to_string(),
            });
        }
        Ok(SuccessRate(rate))
    }
}
```

**Benefits:**
- Compiler catches invalid values
- Self-documenting
- Can't accidentally compare score to latency
- Validation at construction time

---

### Phase 4: Unified Configuration System

Create a centralized config that all layers respect:

```rust
// core/src/orchestration/config.rs

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OrchestrationConfig {
    pub scoring: ScoringConfig,
    pub selection: SelectionConfig,
    pub performance: PerformanceConfig,
    pub validation: ValidationConfig,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScoringConfig {
    pub weights: ScoringWeights,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScoringWeights {
    pub success_rate: f32,      // 0.35
    pub domain_expertise: f32,  // 0.25
    pub latency: f32,           // 0.15
    pub cost_efficiency: f32,   // 0.10
    pub data_freshness: f32,    // 0.10
    pub availability: f32,      // 0.05
}

impl Default for ScoringWeights {
    fn default() -> Self {
        Self {
            success_rate: 0.35,
            domain_expertise: 0.25,
            latency: 0.15,
            cost_efficiency: 0.10,
            data_freshness: 0.10,
            availability: 0.05,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SelectionConfig {
    pub primary_tier_ratio: f32,      // 0.40
    pub secondary_tier_ratio: f32,    // 0.35
    pub max_tools_per_tier: Option<usize>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PerformanceConfig {
    pub time_window: Duration,  // 24h
    pub min_samples_for_stats: usize,  // Don't trust stats with <5 samples
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ValidationConfig {
    pub strict_mode: bool,  // Fail on any validation error
    pub max_string_length: usize,
    pub require_server_health_check: bool,
}

impl Default for OrchestrationConfig {
    fn default() -> Self {
        Self {
            scoring: ScoringConfig { weights: ScoringWeights::default() },
            selection: SelectionConfig {
                primary_tier_ratio: 0.40,
                secondary_tier_ratio: 0.35,
                max_tools_per_tier: None,
            },
            performance: PerformanceConfig {
                time_window: Duration::from_secs(86400),
                min_samples_for_stats: 5,
            },
            validation: ValidationConfig {
                strict_mode: true,
                max_string_length: 256,
                require_server_health_check: true,
            },
        }
    }
}
```

**Benefits:**
- Single source of truth for behavior
- Easy to customize
- Supports different deployment scenarios
- Testable with different configs

---

### Phase 5: Integration Layer

Create a unified orchestration API:

```rust
// core/src/orchestration/engine.rs

pub struct OrchestrationEngine {
    config: OrchestrationConfig,
    classifier: IntentClassifier,
    registry: CapabilityRegistry,
    selector: ToolSelector,
    tracker: PerformanceTracker,
    validator: InputValidator,
}

impl OrchestrationEngine {
    pub fn new(config: OrchestrationConfig) -> Result<Self> {
        // Validate config
        config.validate()?;
        
        Ok(Self {
            classifier: IntentClassifier::new(),
            registry: CapabilityRegistry::new(),
            selector: ToolSelector::new(CapabilityRegistry::new()),
            tracker: PerformanceTracker::with_config(&config.performance),
            validator: InputValidator::with_config(&config.validation),
            config,
        })
    }

    pub fn orchestrate(
        &self,
        query: &str,
    ) -> Result<OrchestratedResponse> {
        // Validate input
        self.validator.validate_query(query)?;

        // Step 1: Understand intent
        let intent_result = self.classifier.classify(query)?;

        // Step 2: Find capability matches
        let servers = self.registry.find_by_intent(intent_result.primary)?;
        if servers.is_empty() {
            return Err(OrchestrationError::NoServersFound { ... });
        }

        // Step 3: Select and rank tools
        let selection = self.selector.select_with_constraints(&intent_result, &constraints)?;

        Ok(OrchestratedResponse {
            intent: intent_result,
            selection,
            trace: execution_trace,
        })
    }

    pub fn record_result(&mut self, server_id: &str, result: QueryResult) -> Result<()> {
        self.tracker.record(result)?;
        Ok(())
    }
}

pub struct OrchestratedResponse {
    pub intent: IntentResult,
    pub selection: ToolSelection,
    pub trace: ExecutionTrace,
}

pub struct ExecutionTrace {
    pub steps: Vec<TraceStep>,
    pub total_time_ms: f32,
    pub decisions: Vec<Decision>,
}

pub struct TraceStep {
    pub layer: String,
    pub action: String,
    pub duration_ms: f32,
    pub result: String,
}

pub struct Decision {
    pub what: String,
    pub why: String,
    pub alternatives: Vec<String>,
}
```

**Benefits:**
- Single entry point for orchestration
- Consistent error handling
- Built-in tracing/observability
- Easy to add cross-cutting concerns
- Testable end-to-end

---

### Phase 6: Input Validation

Add validation everywhere:

```rust
// core/src/orchestration/validation.rs

pub struct InputValidator {
    config: ValidationConfig,
}

impl InputValidator {
    pub fn validate_query(&self, query: &str) -> Result<()> {
        if query.is_empty() {
            return Err(OrchestrationError::ValidationFailed {
                field: "query".to_string(),
                value: "".to_string(),
                reason: "Query cannot be empty".to_string(),
            });
        }
        if query.len() > self.config.max_string_length {
            return Err(OrchestrationError::ValidationFailed {
                field: "query".to_string(),
                value: query.to_string(),
                reason: format!("Query exceeds max length ({})", self.config.max_string_length),
            });
        }
        Ok(())
    }

    pub fn validate_server_profile(&self, profile: &MCPServerProfile) -> Result<()> {
        // Validate ID format
        if profile.id.is_empty() || profile.id.len() > 256 {
            return Err(OrchestrationError::ValidationFailed {
                field: "server_id".to_string(),
                value: profile.id.clone(),
                reason: "Server ID must be non-empty and ≤256 chars".to_string(),
            });
        }

        // Validate capabilities
        if profile.capabilities.is_empty() && self.config.strict_mode {
            return Err(OrchestrationError::ValidationFailed {
                field: "capabilities".to_string(),
                value: "".to_string(),
                reason: "Server must have at least one capability".to_string(),
            });
        }

        // Validate metrics
        if profile.metadata.success_rate < 0.0 || profile.metadata.success_rate > 1.0 {
            return Err(OrchestrationError::ValidationFailed {
                field: "success_rate".to_string(),
                value: profile.metadata.success_rate.to_string(),
                reason: "Success rate must be 0.0-1.0".to_string(),
            });
        }

        Ok(())
    }
}
```

**Benefits:**
- Fail fast on invalid inputs
- Clear error messages
- Prevents silent corruption
- Configurable strictness

---

### Phase 7: Observability

Add comprehensive logging/tracing:

```rust
// core/src/orchestration/observability.rs

pub trait OrchestrationObserver {
    fn on_intent_detected(&self, intent: &IntentResult);
    fn on_servers_found(&self, intent: &str, count: usize);
    fn on_tools_selected(&self, selection: &ToolSelection);
    fn on_error(&self, error: &OrchestrationError);
}

pub struct VerboseObserver;

impl OrchestrationObserver for VerboseObserver {
    fn on_intent_detected(&self, intent: &IntentResult) {
        println!("Intent: {:?} (confidence: {:.1}%)", 
            intent.primary, intent.confidence * 100.0);
    }
    // ...
}

// Usage:
impl OrchestrationEngine {
    pub fn with_observer(mut self, observer: Box<dyn OrchestrationObserver>) -> Self {
        self.observer = Some(observer);
        self
    }

    fn notify_intent_detected(&self, intent: &IntentResult) {
        if let Some(observer) = &self.observer {
            observer.on_intent_detected(intent);
        }
    }
}
```

**Benefits:**
- Observable decision-making
- Audit trails
- Performance monitoring
- Debuggable behavior

---

### Phase 8: Comprehensive Testing

Add integration and property-based tests:

```rust
// tests/orchestration_integration.rs

#[test]
fn test_orchestration_end_to_end() {
    let mut engine = OrchestrationEngine::default().unwrap();
    
    // Register servers
    engine.registry.register(create_arxiv_server());
    engine.registry.register(create_postgres_server());

    // Orchestrate
    let response = engine.orchestrate("Find robotics papers").unwrap();

    // Verify
    assert_eq!(response.intent.primary, IntentCategory::Research);
    assert!(!response.selection.primary.is_empty());
    assert!(response.trace.total_time_ms < 1000.0);
}

#[test]
fn test_orchestration_with_missing_servers() {
    let engine = OrchestrationEngine::default().unwrap();
    
    let result = engine.orchestrate("Find robotics papers");
    
    assert!(result.is_err());
    match result {
        Err(OrchestrationError::NoServersFound { .. }) => {},
        _ => panic!("Expected NoServersFound error"),
    }
}

// Property-based tests
proptest! {
    #[test]
    fn prop_valid_scores_always_normalize(score in 0.0f32..=1.0) {
        let _ = Score::new(score).unwrap();
    }

    #[test]
    fn prop_scoring_is_symmetric(s1 in 0.0f32..=1.0, s2 in 0.0f32..=1.0) {
        let score1 = calculate_score_with_weights(s1, s2);
        let score2 = calculate_score_with_weights(s2, s1);
        // Verify some property...
    }
}
```

**Benefits:**
- Confidence in integration
- Catch boundary bugs
- Regression detection
- Property validation

---

## Implementation Roadmap

### Week 1: Foundation
- [ ] Create unified error type
- [ ] Define shared traits
- [ ] Create newtype wrappers for all metrics
- [ ] Add validation framework

### Week 2: Integration
- [ ] Build OrchestrationEngine
- [ ] Add execution tracing
- [ ] Implement observability hooks
- [ ] Create unified config system

### Week 3: Hardening
- [ ] Add comprehensive validation
- [ ] Implement input validators
- [ ] Add integration tests
- [ ] Add property-based tests

### Week 4: Polish
- [ ] Performance profiling
- [ ] Documentation update
- [ ] API stability review
- [ ] Release v0.5.0

---

## Expected Outcomes

### Code Quality
- ✅ 100% of error paths handled
- ✅ No panics in production code
- ✅ All inputs validated
- ✅ Type-safe metrics

### Testability
- ✅ Unit tests for each trait
- ✅ Integration tests for orchestration
- ✅ Property-based tests
- ✅ >90% code coverage

### Observability
- ✅ Execution traces
- ✅ Audit trails
- ✅ Decision logs
- ✅ Performance metrics

### Maintainability
- ✅ Unified configuration
- ✅ Clear responsibilities
- ✅ Shared abstractions
- ✅ Extensible design

---

## Summary

**Before:** 3 independent layers with duplicated logic and inconsistent APIs.

**After:** Cohesive orchestration engine with:
- Unified error handling
- Shared abstractions
- Strong typing
- Comprehensive validation
- Full observability
- Extensible design
- 100% testable

**Effort:** ~80 hours (full-time week + half)  
**Payoff:** Production-quality orchestration layer that scales
