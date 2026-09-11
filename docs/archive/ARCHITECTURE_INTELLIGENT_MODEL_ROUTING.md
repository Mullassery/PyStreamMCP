# PyStreamMCP v0.3 — Intelligent Model Routing via OpenRouter

**Concept:** Route each query to the optimal model (cost vs capability) using OpenRouter.

**Date:** 2026-07-17  
**Status:** ARCHITECTURE DESIGN (LOCKED)  
**Priority:** P0 (Multiplies token savings by 3-5x)  
**Vision:** Not every task needs Opus. Match model to complexity.

---

## The Model Selection Problem

### Current (❌ One-Size-Fits-All)

```
Task 1: "What columns in customers table?"
  → Route to Claude Opus (most expensive)
  → Overkill for simple schema lookup
  → Cost: $0.015 per query

Task 2: "Analyze revenue trends across 5 regions"
  → Route to Claude Opus
  → Appropriate complexity
  → Cost: $0.015 per query

Task 3: "Compare 10 customers, find anomalies"
  → Route to Claude Opus
  → Appropriate complexity
  → Cost: $0.015 per query

Average cost: $0.015 per query
Annual (100K queries): $1,500
```

### Proposed (✅ Intelligent Routing)

```
Task 1: "What columns in customers table?"
  → Complexity: TRIVIAL (schema lookup)
  → Route to Claude Haiku (fastest, cheapest)
  → Cost: $0.0008 per query (47x cheaper!)

Task 2: "Analyze revenue trends across 5 regions"
  → Complexity: MEDIUM (multi-table analysis)
  → Route to Claude Sonnet (balanced)
  → Cost: $0.003 per query (5x cheaper than Opus)

Task 3: "Compare 10 customers, find anomalies"
  → Complexity: HIGH (pattern recognition)
  → Route to Claude Opus (most capable)
  → Cost: $0.015 per query

Average cost: $0.006 per query (60% savings)
Annual (100K queries): $600 (vs $1,500)
Savings: $900/year just from routing
```

---

## Complexity Classification

### Tier 1: TRIVIAL (Use Haiku)

**Characteristics:**
- Schema lookups
- Simple field existence checks
- Table name queries
- Column type lookups
- Metadata retrieval

**Cost:** $0.0008 per query
**Latency:** <100ms
**Context limit:** 8K tokens
**Accuracy:** >99%

**Example:**
```
"What columns does customers have?"
"Is region a field in orders?"
"List all tables in this warehouse"
```

**Model capability needed:** Simple information retrieval
→ Haiku is perfect

### Tier 2: SIMPLE (Use Sonnet)

**Characteristics:**
- Single-table filtering
- Basic joins (2-3 tables)
- Simple aggregations
- Pattern matching
- Basic transformations

**Cost:** $0.003 per query
**Latency:** <500ms
**Context limit:** 32K tokens
**Accuracy:** >95%

**Example:**
```
"Top 10 customers by revenue"
"Average order value by region"
"Find duplicates in user_ids"
```

**Model capability needed:** Basic analytics
→ Sonnet is perfect

### Tier 3: MEDIUM (Use Sonnet-Pro or Opus)

**Characteristics:**
- Multi-step analysis
- 4-8 table joins
- Complex aggregations
- Statistical reasoning
- Trend analysis

**Cost:** $0.010 per query (Sonnet-Pro)
**Latency:** <2000ms
**Context limit:** 200K tokens
**Accuracy:** >90%

**Example:**
```
"Analyze customer segmentation by cohort"
"Revenue trends across regions and products"
"Identify seasonal patterns in orders"
```

**Model capability needed:** Multi-dimensional analysis
→ Sonnet-Pro or Opus

### Tier 4: COMPLEX (Use Opus)

**Characteristics:**
- Whole-warehouse analysis
- 8+ table reasoning
- Anomaly detection
- Root cause analysis
- Predictive reasoning

**Cost:** $0.015 per query
**Latency:** <5000ms
**Context limit:** 200K tokens
**Accuracy:** >95%

**Example:**
```
"Identify revenue anomalies and root causes"
"Predict customer churn risk"
"Cross-warehouse data quality assessment"
```

**Model capability needed:** Advanced reasoning
→ Opus is necessary

---

## Intelligent Routing Algorithm

### Step 1: Analyze Query

```python
class ComplexityClassifier:
    """Determine task complexity without running it"""
    
    def classify(self, query: str, context_size: int) -> Tier:
        """Classify query complexity"""
        
        score = 0
        
        # Factor 1: Query length (longer = more complex?)
        score += min(len(query) / 500, 1.0) * 0.1
        
        # Factor 2: Keywords indicating complexity
        complexity_keywords = {
            "trivial": ["columns", "fields", "schema", "exists", "list"],
            "simple": ["top", "average", "sum", "group", "filter"],
            "medium": ["join", "trend", "segment", "coalesce", "pivot"],
            "complex": ["anomaly", "pattern", "predict", "correlate", "cascade"],
        }
        
        for tier, keywords in complexity_keywords.items():
            if any(kw in query.lower() for kw in keywords):
                score += tier_scores[tier]
        
        # Factor 3: Number of tables needed (inferred from query)
        table_count = estimate_table_count(query)
        score += (table_count / 20) * 0.3
        
        # Factor 4: Context size
        if context_size < 8_000:
            score += 0.0  # Trivial
        elif context_size < 32_000:
            score += 0.25  # Simple
        elif context_size < 100_000:
            score += 0.5  # Medium
        else:
            score += 0.75  # Complex
        
        # Classify by score
        if score < 0.25:
            return Tier.TRIVIAL
        elif score < 0.5:
            return Tier.SIMPLE
        elif score < 0.75:
            return Tier.MEDIUM
        else:
            return Tier.COMPLEX
    
    def estimate_table_count(self, query: str) -> int:
        """Estimate how many tables this query will need"""
        
        tables_mentioned = extract_table_names(query)
        return len(tables_mentioned)
```

### Step 2: Select Model via OpenRouter

```python
class ModelRouter:
    """Route to optimal model via OpenRouter"""
    
    MODELS = {
        Tier.TRIVIAL: {
            "model": "openrouter/claude-3-haiku-20250301",
            "cost_per_1k_input": 0.80,
            "cost_per_1k_output": 4.00,
            "max_context": 8_000,
        },
        Tier.SIMPLE: {
            "model": "openrouter/claude-3-5-sonnet-20241022",
            "cost_per_1k_input": 3.00,
            "cost_per_1k_output": 15.00,
            "max_context": 200_000,
        },
        Tier.MEDIUM: {
            "model": "openrouter/claude-3-5-sonnet-20241022",  # Or Opus if needed
            "cost_per_1k_input": 3.00,
            "cost_per_1k_output": 15.00,
            "max_context": 200_000,
        },
        Tier.COMPLEX: {
            "model": "openrouter/claude-opus-4-1-20250805",
            "cost_per_1k_input": 15.00,
            "cost_per_1k_output": 60.00,
            "max_context": 200_000,
        },
    }
    
    def select_model(self, tier: Tier, context_size: int) -> ModelConfig:
        """Select best model for this task"""
        
        config = self.MODELS[tier]
        
        # Verify context fits
        if context_size > config["max_context"]:
            # Escalate to more capable model
            return self.escalate_model(tier, context_size)
        
        return config
    
    def escalate_model(self, tier: Tier, context_size: int) -> ModelConfig:
        """Escalate to more capable model if needed"""
        
        escalation_path = {
            Tier.TRIVIAL: Tier.SIMPLE,
            Tier.SIMPLE: Tier.MEDIUM,
            Tier.MEDIUM: Tier.COMPLEX,
            Tier.COMPLEX: Tier.COMPLEX,  # Already max
        }
        
        new_tier = escalation_path[tier]
        
        if new_tier == tier:
            # Already at max, context too large
            raise ContextTooLargeError(
                f"Context {context_size} exceeds {Tier.COMPLEX} max"
            )
        
        return self.select_model(new_tier, context_size)
    
    def estimate_cost(self, model: ModelConfig, 
                     input_tokens: int, output_tokens: int) -> float:
        """Estimate cost before executing"""
        
        input_cost = (input_tokens / 1000) * model["cost_per_1k_input"]
        output_cost = (output_tokens / 1000) * model["cost_per_1k_output"]
        
        return input_cost + output_cost
```

### Step 3: Execute with Model

```python
class OpenRouterExecutor:
    """Execute query on OpenRouter with selected model"""
    
    def __init__(self, api_key: str):
        self.client = OpenRouter(api_key=api_key)
        self.router = ModelRouter()
    
    def execute(self, query: str, context: Dict, tier: Tier) -> Result:
        """Execute query on optimal model"""
        
        # Select model
        model_config = self.router.select_model(tier, len(context))
        
        # Estimate cost
        estimated_cost = self.router.estimate_cost(
            model_config,
            input_tokens=estimate_tokens(query + str(context)),
            output_tokens=500  # Rough estimate
        )
        
        # Check budget
        if estimated_cost > self.budget_remaining:
            # Degrade to cheaper model?
            model_config = self.degrade_if_possible(tier)
        
        # Execute
        result = self.client.create(
            model=model_config["model"],
            messages=[
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuery: {query}"
                }
            ]
        )
        
        # Track cost
        self.actual_cost = calculate_actual_cost(result)
        self.budget_remaining -= self.actual_cost
        
        return result
```

---

## Cost Savings Breakdown

### By Tier Distribution

```
Typical query distribution in data analytics:

Tier 1 (Trivial):  30% of queries
  ├─ Cost per query: $0.0008
  ├─ Annual (30K queries): $24

Tier 2 (Simple):   50% of queries
  ├─ Cost per query: $0.003
  ├─ Annual (50K queries): $150

Tier 3 (Medium):   15% of queries
  ├─ Cost per query: $0.010
  ├─ Annual (15K queries): $150

Tier 4 (Complex):   5% of queries
  ├─ Cost per query: $0.015
  ├─ Annual (5K queries): $75

TOTAL ANNUAL: $399 (vs $1,500 with all Opus)
SAVINGS: 73% reduction
```

### Compound Savings

With other optimizations:

```
Retrieval quality:  50-75% savings
Memory + caching:   70-85% hit rate
Agentic optimization: 80-95% efficiency
Model routing:      60-73% cost reduction

Combined: 90-95% overall savings
```

---

## Integration with Memory System

### Episodic Memory Learns Model Performance

```python
episodic_memory.save_query_execution({
    "query": query,
    "tier_classified": Tier.SIMPLE,
    "model_used": "claude-3-5-sonnet",
    "cost_actual": 0.003,
    "cost_estimated": 0.0035,
    "cost_accuracy": 92%,  # Estimate vs actual
    
    "result_quality": 0.95,  # User satisfaction
    "latency_ms": 234,
    "tokens_input": 1200,
    "tokens_output": 150,
})

# Over time, learn:
# - Tier classification accuracy
# - Model performance vs cost
# - Latency characteristics
# - Quality tradeoffs
```

### Budget Awareness Respects Model Costs

```python
budget_manager = BudgetManager(token_budget=100_000)

for query in pending_queries:
    tier = complexity_classifier.classify(query)
    model = model_router.select_model(tier)
    cost = model_router.estimate_cost(model, tokens)
    
    if cost > budget_manager.remaining:
        # Can't afford this model
        
        if can_degrade_tier(tier):
            # Use cheaper model
            tier = degrade_tier(tier)
            model = model_router.select_model(tier)
        else:
            # Can't execute this query
            break
    
    budget_manager.charge(cost)
    result = execute_on_router(model, query)
```

---

## Model Selection Decision Tree

```
Query: "What columns in customers?"

1. Classify complexity
   └─ Keywords: ["columns", "schema"]
   └─ Tables: 1
   └─ Context: <8K tokens
   └─ Score: 0.15
   └─ Tier: TRIVIAL ✓

2. Select model
   └─ Tier.TRIVIAL → Claude Haiku
   └─ Cost: $0.0008
   └─ Latency: <100ms
   └─ Context: 8K (adequate)

3. Execute
   └─ Send to OpenRouter
   └─ Receive result in <100ms
   └─ Cost: $0.0008

---

Query: "Identify revenue anomalies and predict customer churn"

1. Classify complexity
   └─ Keywords: ["anomaly", "predict", "churn"]
   └─ Tables: 5+
   └─ Context: >100K tokens
   └─ Score: 0.85
   └─ Tier: COMPLEX ✓

2. Select model
   └─ Tier.COMPLEX → Claude Opus
   └─ Cost: $0.015
   └─ Latency: <5s
   └─ Context: 200K (adequate)

3. Execute
   └─ Send to OpenRouter
   └─ Receive result in <5s
   └─ Cost: $0.015
```

---

## OpenRouter Integration Points

### 1. Model Selection

```python
import openrouter

router = openrouter.AsyncOpenRouter(api_key=os.getenv("OPENROUTER_API_KEY"))

# List available models
models = await router.models.list()
# → Get pricing, context limits, capabilities

# Select based on tier
model_id = tier_to_model_map[tier]
```

### 2. Cost Tracking

```python
# OpenRouter provides cost info
response = await router.chat.completions.create(
    model=model_id,
    messages=messages,
)

# Track actual costs
cost = {
    "input_tokens": response.usage.prompt_tokens,
    "output_tokens": response.usage.completion_tokens,
    "cost_usd": calculate_cost(
        response.usage.prompt_tokens,
        response.usage.completion_tokens,
        model_id
    ),
}

episodic_memory.save_cost(cost)
budget_manager.charge(cost["cost_usd"])
```

### 3. Fallback Handling

```python
try:
    result = await router.chat.completions.create(
        model=model_id,
        messages=messages,
    )
except openrouter.RateLimitError:
    # Fallback to cheaper model or queue
    tier = degrade_tier(tier)
    model_id = tier_to_model_map[tier]
    result = await router.chat.completions.create(
        model=model_id,
        messages=messages,
    )
except openrouter.ContextLengthError:
    # Need to escalate or split query
    tier = escalate_tier(tier)
    ...
```

---

## Success Metrics

✓ Tier classification accuracy: 90%+  
✓ Cost estimation accuracy: ±5%  
✓ Model selection effectiveness: Results improve 5-10% with Opus selection  
✓ Budget adherence: Queries stay within budget  
✓ Latency: Respects model SLAs  
✓ Cost reduction: 60-73% vs all-Opus baseline  

---

## Combined Impact: All Optimizations

```
100 queries/day baseline:

1. Retrieval quality:        -50% to -75% tokens
2. Memory + caching:         -70% to -85% (cache hits)
3. Agentic optimization:     -80% to -95% efficiency
4. Model routing:            -60% to -73% cost

Combined: 90-95% reduction in both tokens AND cost

Before: 1M tokens/day = $1,825/year
After:  100K tokens/day = $182.50/year
Final (with model routing): $30-50/year per agent

Total savings: 97-98% cost reduction + 35% quality improvement
```

---

## Why This Matters

**Not every query is equally complex.**

Using Opus for "What columns exist?" is like using a supercomputer to turn on a light.

Intelligent routing means:
- Simple queries get fast, cheap answers (Haiku)
- Medium queries get balanced answers (Sonnet)
- Complex queries get best-quality answers (Opus)
- Budget goes 3-5x further

This is the final multiplier on top of all other optimizations.
