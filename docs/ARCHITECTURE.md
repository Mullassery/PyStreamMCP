# PyStreamMCP Architecture & Ecosystem Boundaries

## Mission

**Optimize Intelligence for AI Agents**

Core Question: What is the minimum context an agent needs to make a quality decision?

## Core Responsibility

PyStreamMCP is **exclusively responsible** for:

- **Query Planning** — Understanding what agents need
- **Context Discovery** — Finding relevant information
- **Cost Optimization** — Reducing tokens 60-75% without losing quality
- **Agent Intelligence** — Making agents smarter with less

## What We Do NOT Own

These belong to other products:

### ❌ Data Validation & Quality (StatGuardian)
- Data contracts
- Drift detection
- Schema profiling
- Freshness monitoring

**Our role:** Consume validated context. Trust StatGuardian's gates.

### ❌ Audience Creation (ClusterAudienceKit)
- Segmentation
- Clustering
- RFM analysis

**Our role:** Discover and optimize for audience context.

### ❌ Data Activation (PyReverseETL)
- Moving data to operational systems
- Entity synchronization
- Destination management

**Our role:** Discover and optimize data from activated sources.

### ❌ Journey Orchestration (PyCustomerJourney)
- Customer journeys
- Multi-step workflows
- Communications

**Our role:** Provide context for journey decisions.

## Architectural Principles

### 1. Agent-Centric Design

```
What does this agent need?
        ↓
Query planning (constraints)
        ↓
Discovery (what exists?)
        ↓
Optimization (60-75% reduction)
        ↓
Context window (optimal)
```

### 2. Validation Gates

PyStreamMCP can require StatGuardian validation before including context:

```rust
Query {
    text: "top customers",
    validation_gates: vec![
        ValidationGate::new("customers_dataset"),
    ],
}
```

### 3. No Embedded Validation

```rust
// ❌ NOT OUR JOB
fn validate_context(context: &Context) -> Result<()> {
    // Check for nulls
    // Check for anomalies
    // Check freshness
}

// ✅ OUR JOB
fn discover_context(query: &Query) -> Result<Vec<Context>> {
    // Find relevant data
    // Rank by relevance
    // Estimate token costs
}
```

## Boundary Examples

### Scenario: Agent asks "Who's churning?"

**Who owns what:**

1. **Agent asks question** — "Which customers are at churn risk?"
2. **PyStreamMCP plans** — Query type: Discover, Budget: 2000 tokens
3. **PyStreamMCP discovers** — Found: churn_model scores, recent interactions, cohort data
4. **StatGuardian validates** — Churn scores are fresh, interactions are recent ✓
5. **PyStreamMCP optimizes** — Reduce to top 20 at-risk + key traits (70% reduction)
6. **Agent responds** — With 30% of the cost, same quality

### Scenario: Agent needs customer context

**Who owns what:**

1. **PyReverseETL activated** — Customer LTV synced to journey system
2. **PyStreamMCP discovers** — LTV available, historical trends, segment info
3. **Agent asks** — "Tell me about customer #123"
4. **PyStreamMCP optimizes** — Return LTV + trend + peer comparison (60% reduction)
5. **Agent decides** — Whether to trigger upsell journey

## Integration Points

### With StatGuardian

Every context can require validation:

```rust
Context {
    content: customer_data,
    validation_gate: Some(ValidationGate::new("customer_dataset")),
}
```

### With PyReverseETL

Context sources come from activated data:

```rust
DiscoveredSource {
    name: "activated_customer_traits",
    source_type: SourceType::External { api: "pyreverseetl" },
}
```

### With Agent Frameworks

Query intent maps to agent needs:

```python
query = Query("top 5 similar customers", agent_id="rec_engine")
discovery = Discovery(query.id)
# Returns optimized context for recommendation
```

## Module Structure

```
core/src/
├── lib.rs                 # Public exports
├── error.rs               # Error types (NO validation errors)
├── query.rs               # Query planning (intent, constraints)
├── context.rs             # Context representation
├── discovery.rs           # Source discovery & ranking
├── optimization.rs        # Cost reduction strategies
├── statguardian.rs        # Quality validation gates
└── storage/              # Persistence
    ├── mod.rs
    ├── schema.rs
    └── repository.rs
```

## What's NOT Here

### Validation Engine

```rust
// ❌ NOT IN PyStreamMCP
mod validation {
    fn validate_schema() { }
    fn detect_drift() { }
    fn check_freshness() { }
}
```

### Audience Engine

```rust
// ❌ NOT IN PyStreamMCP
mod audience {
    fn cluster() { }
    fn rfm_score() { }
    fn define_segment() { }
}
```

### Activation Engine

```rust
// ❌ NOT IN PyStreamMCP
mod activation {
    fn sync_to_salesforce() { }
    fn sync_to_hubspot() { }
    fn propagate_audience() { }
}
```

### Journey Engine

```rust
// ❌ NOT IN PyStreamMCP
mod journey {
    fn execute_step() { }
    fn branch() { }
    fn send_email() { }
}
```

## Testability

Each boundary is enforced through:

1. **Module privacy** — Validation/audience/activation/journey modules don't exist
2. **Type system** — Can't express validation rules in our types
3. **Integration tests** — Test against mocked StatGuardian/PyReverseETL APIs
4. **Documentation** — Explicit "out of scope" statements

## Philosophy

PyStreamMCP is to agent intelligence what dbt is to transformation:

- dbt owns **transformation logic**, not data quality
- PyStreamMCP owns **query optimization**, not data validation

Each product is best in class precisely because it has a singular focus.

## Success Metrics

✅ 60-75% token reduction (target met)
✅ Quality maintained (validation gates pass)
✅ Speed maintained (latency < constraints)
✅ Agent satisfaction (better decisions)
✅ Cost reduction (30-40% cheaper queries)

## Future Evolution

### Phase 2: Agent Integrations
- MCP (Model Context Protocol) native support
- Langchain/Llamaindex adapters
- Agent framework plugins

### Phase 3: Learning
- Learned relevance models
- Agent-specific optimizations
- Multi-agent knowledge sharing

### Phase 4: Enterprise
- Cost governance and budgets
- Team-level optimization
- SLA enforcement
- Custom optimization rules
