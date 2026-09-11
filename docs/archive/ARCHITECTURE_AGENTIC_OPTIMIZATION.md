# PyStreamMCP v0.3 — Agentic Workflow Optimization

**Concept:** Autonomous agents that detect and eliminate redundant work before wasting tokens.

**Date:** 2026-07-17  
**Status:** ARCHITECTURE DESIGN (LOCKED)  
**Priority:** P0 (Blocks autonomous agent scaling)  
**Vision:** Agents maintain execution state to detect loops, stop redundancy, and budget smartly

---

## Problem: Autonomous Agent Inefficiency

### Current (❌ Token Waste)

```
Agent Task: "Find top customers in APAC, segment by revenue, create performance report"

Attempt 1:
  → Call get_schema("customers")        [50K tokens]
  → Analyze response
  → Call get_schema("regions")          [40K tokens]  
  → Analyze response
  → Realize needs another field
  → Call get_schema("customers") AGAIN  [50K tokens] ← REDUNDANT
  → Attempt query
  → Query fails (missing join condition)
  
Attempt 2 (Loop):
  → Re-call get_schema("customers")     [50K tokens] ← LOOP
  → Same analysis
  → Call different API (duplicate work)
  → Query fails differently
  
Attempt 3 (Infinite loop):
  → Agent keeps trying same failing pattern
  → Each attempt re-fetches schemas
  → Each attempt re-analyzes relationships
  → No progress, 500K tokens wasted

Total: 500K tokens on failed attempts
Agent never asked: "Wait, did I already fetch this?"
```

### Proposed (✅ Efficient)

```
Agent Task: "Find top customers in APAC, segment by revenue, create performance report"

Execution 1:
  → BEFORE calling get_schema("customers"):
     Check execution_history: "Already fetched this? ✗"
     Add to pending_calls: [get_schema("customers")]
  → Call get_schema("customers")        [50K tokens]
  → Log result: customers_schema (result_id="schema_1")
  
  → BEFORE calling get_schema("regions"):
     Check execution_history: "Already fetched? ✗"
     Add to pending_calls: [get_schema("regions")]
  → Call get_schema("regions")          [40K tokens]
  → Log result: regions_schema (result_id="schema_2")
  
  → BEFORE attempting query:
     Check pending_calls: Need more fields?
     Collapse reasoning: "I have schemas, I can infer joins"
     → No need for 3rd schema call
  → Attempt query (now has all needed info)
  → Query fails with specific error: "Missing customer_region_id"
  
  → BEFORE retrying:
     Detect loop: "Did I just try this?"
     Check: Last failure was same query pattern ✓
     Budget check: Have I spent 200K tokens? Yes
     → Switch strategy: "Ask for help, don't retry blindly"
  → Agent calls get_column_details("customer_region_id")
  → Query succeeds
  
Total: 95K tokens (50 + 40 + details lookup)
Agent saved: 405K tokens by detecting redundancy
```

---

## Four Optimization Layers

### Layer 1: EXECUTION HISTORY TRACKING

**What:** Remember what we already did in this session

**Tracks:**
```python
execution_history = {
    "api_calls": [
        {
            "call_id": "schema_1",
            "api": "get_schema",
            "arguments": {"table": "customers"},
            "timestamp": t1,
            "result": customers_schema,
            "tokens_used": 50000,
            "success": True,
        },
        {
            "call_id": "schema_2",
            "api": "get_schema",
            "arguments": {"table": "regions"},
            "timestamp": t2,
            "result": regions_schema,
            "tokens_used": 40000,
            "success": True,
        },
    ],
    "failed_attempts": [
        {
            "attempt": 1,
            "operation": "query_customers_by_region",
            "error": "Missing customer_region_id",
            "tokens_used": 15000,
            "timestamp": t3,
        }
    ],
    "total_tokens_used": 105000,
    "total_attempts": 2,
    "start_time": t0,
}
```

**Deduplication Logic:**
```python
def should_repeat_call(api_call):
    """Should we make this API call again?"""
    
    # Check if already executed
    for past_call in execution_history.api_calls:
        if (past_call.api == api_call.api and 
            past_call.arguments == api_call.arguments):
            
            # Already executed
            if time_since(past_call) < 5_minutes:
                # Result still fresh, reuse it
                return False, past_call.result
            elif past_call.success:
                # Still available in context, don't repeat
                return False, past_call.result
    
    # Not executed before, or too old, or failed
    return True, None

# Usage:
should_repeat, cached_result = should_repeat_call(
    get_schema("customers")
)

if not should_repeat:
    result = cached_result  # Reuse (0 tokens)
    log_dedup_save(50000)
else:
    result = get_schema("customers")  # Execute (50K tokens)
    add_to_history(result)
```

---

### Layer 2: LOOP DETECTION

**What:** Detect when agent is repeating failed patterns

**Detects:**
```python
class LoopDetector:
    """Identify when agent is stuck in a pattern"""
    
    def detect_retry_loop(self):
        """Is agent retrying same failed operation?"""
        
        # Pattern: Same operation attempted multiple times
        if len(execution_history.failed_attempts) >= 3:
            last_3 = execution_history.failed_attempts[-3:]
            
            # All same operation?
            if all(a.operation == last_3[0].operation for a in last_3):
                return True, {
                    "operation": last_3[0].operation,
                    "attempts": len(last_3),
                    "error_patterns": [a.error for a in last_3],
                    "total_tokens_wasted": sum(a.tokens_used for a in last_3),
                }
        
        return False, None
    
    def detect_circular_reasoning(self):
        """Is agent reasoning in circles?"""
        
        # Pattern: Agent asked same question multiple times
        # (Same embedding, different phrasing)
        recent_thoughts = execution_history.reasoning[-10:]
        
        embeddings = [embed(t) for t in recent_thoughts]
        
        # High cosine similarity between distant thoughts?
        for i in range(len(embeddings)):
            for j in range(i+3, len(embeddings)):  # Skip nearby
                if cosine_similarity(embeddings[i], embeddings[j]) > 0.92:
                    # Thinking about same thing again
                    return True, {
                        "thought_1": recent_thoughts[i],
                        "thought_2": recent_thoughts[j],
                        "similarity": cosine_similarity(embeddings[i], embeddings[j]),
                    }
        
        return False, None
    
    def detect_tool_call_loop(self):
        """Is agent making same tool call repeatedly?"""
        
        last_10_calls = execution_history.api_calls[-10:]
        call_signatures = [(c.api, str(c.arguments)) for c in last_10_calls]
        
        # More than 50% of last calls identical?
        call_counts = Counter(call_signatures)
        dominant_call_count = call_counts.most_common(1)[0][1]
        
        if dominant_call_count / len(last_10_calls) > 0.5:
            return True, {
                "repeated_call": call_signatures[0],
                "occurrences": dominant_call_count,
                "out_of": len(last_10_calls),
            }
        
        return False, None
```

**Response:**
```python
if loop_detected := detector.detect_retry_loop():
    # STOP and escalate
    log_alert(f"Loop detected: {loop_detected}")
    
    # Don't retry blindly
    agent_state = "AWAITING_GUIDANCE"
    
    # Suggest alternative approach
    alternatives = generate_alternatives(
        failed_operation=loop_detected["operation"],
        error_patterns=loop_detected["error_patterns"],
    )
    
    return AlternativeStrategy(alternatives)
```

---

### Layer 3: REDUNDANCY COLLAPSING

**What:** Recognize duplicate reasoning and use cached reasoning

**Collapses:**
```python
class ReasoningOptimizer:
    """Collapse duplicate analytical work"""
    
    def collapse_schema_analysis(self, schemas_fetched):
        """
        If agent fetched multiple schemas in sequence,
        don't re-analyze each one separately.
        
        Instead: Unified analysis of all relationships.
        """
        
        # Before (naive):
        # - Analyze customers schema (5K tokens)
        # - Analyze orders schema (5K tokens)
        # - Analyze payments schema (5K tokens)
        # - Think about joins (5K tokens)
        # Total: 20K tokens of separate analysis
        
        # After (optimized):
        # - Unified schema analysis with pre-known relationships
        # - Leverage StatGuardian lineage
        # - Infer joins from lineage
        # Total: 8K tokens in single pass
        
        unified_schema = {
            "tables": schemas_fetched,
            "relationships": knowledge_memory.get_relationships(schemas_fetched),
            "transformations": knowledge_memory.get_lineage(schemas_fetched),
        }
        
        reasoning = agent.analyze_unified_schema(unified_schema)
        
        tokens_saved = 12000  # 20K - 8K
        log_optimization("Schema analysis collapsed", tokens_saved)
        
        return reasoning, tokens_saved
    
    def collapse_transformation_planning(self, goal):
        """
        If agent is planning multiple transformations,
        don't plan each one separately.
        
        Use lineage to pre-build transformation chain.
        """
        
        # Get pre-computed lineage
        lineage = knowledge_memory.get_transformation_chain(goal.tables)
        
        # Use lineage as template (instead of planning from scratch)
        plan = agent.refine_plan(lineage)  # Light, not heavy
        
        tokens_saved = 15000
        return plan, tokens_saved
```

---

### Layer 4: BUDGET-AWARE PLANNING

**What:** Dynamically adjust strategy based on token budget

**Budget Tracking:**
```python
class BudgetAwareAgent:
    """Operate within token budget and optimize allocation"""
    
    def __init__(self, token_budget: int = 100_000):
        self.token_budget = token_budget
        self.tokens_used = 0
        self.tokens_available = token_budget
        
    def adjust_strategy(self):
        """Change strategy based on remaining budget"""
        
        percent_used = self.tokens_used / self.token_budget
        
        if percent_used > 0.9:
            # 90%+ budget spent
            log.warning(f"Budget at 90%, {self.tokens_available} left")
            
            strategy = ReducedStrategy(
                skip_exploratory_queries=True,
                use_cached_results_only=True,
                skip_validation=True,
            )
            
            return strategy, "MINIMAL_MODE"
        
        elif percent_used > 0.7:
            # 70-90% spent
            strategy = CautiousStrategy(
                prefer_cached_results=True,
                validate_before_calling_apis=True,
                estimate_cost_before_calling=True,
            )
            
            return strategy, "CAUTIOUS_MODE"
        
        else:
            # < 70% spent, normal operation
            strategy = NormalStrategy(
                call_apis_as_needed=True,
                explore_alternatives=True,
                validate_thoroughly=True,
            )
            
            return strategy, "NORMAL_MODE"
    
    def predict_token_cost(self, planned_operation):
        """Estimate cost before executing"""
        
        # Use episodic memory to estimate
        similar_ops = episodic_memory.find_similar(
            operation=planned_operation
        )
        
        avg_cost = mean([op.tokens_used for op in similar_ops])
        
        # Check if we can afford it
        if avg_cost > self.tokens_available:
            return None, "OUT_OF_BUDGET"
        
        return avg_cost, "OK"
    
    def prioritize_operations(self, pending_operations):
        """Sort operations by value/cost ratio"""
        
        # Value: How much does this help the goal?
        # Cost: How many tokens?
        
        scored = [
            {
                "op": op,
                "value": estimate_value(op, goal),
                "cost": predict_token_cost(op),
                "ratio": estimate_value(op, goal) / predict_token_cost(op),
            }
            for op in pending_operations
        ]
        
        # Sort by value/cost (highest first)
        scored.sort(key=lambda x: x["ratio"], reverse=True)
        
        return [s["op"] for s in scored]
```

**Planning Example:**
```python
# Agent planning task with 100K token budget
agent = BudgetAwareAgent(token_budget=100_000)

pending_operations = [
    "fetch_schema(customers)",           # Est: 50K tokens, Value: High
    "fetch_schema(orders)",              # Est: 40K tokens, Value: High
    "validate_with_sample_query",        # Est: 20K tokens, Value: Medium
    "generate_visualization_code",       # Est: 10K tokens, Value: Low
]

# Prioritized by value/cost:
# 1. fetch_schema(customers)    - 50K tokens, Value=High (ratio=High/50)
# 2. fetch_schema(orders)       - 40K tokens, Value=High (ratio=High/40)
# 3. validate_with_sample_query - 20K tokens, Value=Med (ratio=Med/20)
# 4. generate_visualization_code - 10K tokens, Value=Low (ratio=Low/10)

# Budget tracking:
executed = []
for op in prioritized_operations:
    cost = predict_token_cost(op)
    
    if cost > agent.tokens_available:
        log.warning(f"Cannot afford {op}: costs {cost}, have {agent.tokens_available}")
        break  # Stop, out of budget
    
    result = execute(op)
    agent.tokens_used += cost
    agent.tokens_available -= cost
    executed.append(op)
    
    # Adjust strategy mid-execution
    strategy, mode = agent.adjust_strategy()
    if mode == "CAUTIOUS_MODE":
        # Skip expensive operations now
        pending_operations = [
            op for op in pending_operations
            if predict_token_cost(op) < 15_000  # Only cheap ops
        ]

# Result: Accomplished main goal (fetch schemas) within budget
# Did NOT waste budget on low-value visualization code
```

---

## Integration with Memory System

### Execution Tracking Feed

```
┌─────────────────────────────────────────┐
│ AGENT EXECUTION ENGINE                  │
│                                          │
│ 1. Initialize execution history         │
│ 2. Check budget (Layer 4)                │
│ 3. Plan operations (Layer 4)             │
│ 4. Before each API call:                 │
│    - Deduplicate? (Layer 1)              │
│    - Check loops? (Layer 2)              │
│    - Collapse reasoning? (Layer 3)       │
│ 5. Execute operation                     │
│ 6. Log result to history                 │
│ 7. Update working memory                 │
│ 8. Return to step 4 or exit              │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ WORKING MEMORY                          │
│                                          │
│ • execution_history: tracking           │
│ • loop_detector: state                  │
│ • budget_tracker: tokens used/remaining │
│ • dedup_cache: recent results           │
│ • collapsed_reasoning: saved work       │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ EPISODIC MEMORY                         │
│                                          │
│ Save for future:                        │
│ • What operations succeeded (fast)      │
│ • What loops occurred (avoid)           │
│ • What cost estimates were accurate     │
│ • What reasoning could collapse         │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ OPTIMIZATION ENGINE LEARNING            │
│                                          │
│ Learn patterns:                         │
│ • "Task X always loops at step Y"       │
│ • "Cost estimates within 10%"           │
│ • "These schemas always used together"  │
│ • "Collapse reduces tokens by 40%"      │
└─────────────────────────────────────────┘
```

---

## Token Savings Breakdown

### Without Optimization (Current)

```
Agent attempts complex task: "Analytics report for APAC region"

Attempt 1:
  - Fetch schema (customers)        50K
  - Fetch schema (orders)           40K
  - Fetch schema (regions)          35K
  - Attempt 1 fails
  - Fetch schema (customers) AGAIN  50K ← DUP
  - Attempt 2 fails
  - Analyze why (15K reasoning)
  - Fetch schema (orders) AGAIN     40K ← DUP
  - Attempt 3 succeeds
  - Reasoning and validation        20K

Total: 250K tokens
```

### With Optimization (Proposed)

```
Agent attempts same task with layers enabled:

Execution setup:
  - Initialize execution_history
  - Set budget: 100K tokens
  - Enable layer 1-4

Attempt 1:
  - Fetch schema (customers)        50K  [logged]
  - Fetch schema (orders)           40K  [logged]
  - Collapse reasoning (instead of fetching regions) 
                                    ← Save 35K
  - Attempt query
  - Detect loop (layer 2)           
    → Would fail again, stop       ← Save 40K (no dup fetch)
  - Collapse duplicate reasoning   ← Save 15K
  - Switch strategy (budget aware)
  - Query succeeds with minimal retry

Total: 90K tokens
Savings: 160K tokens (64% reduction)

More important: Task succeeded within budget
Without optimization: Would exceed budget and fail
```

---

## Why This Matters

**Autonomous agents don't have humans to stop them.**

Without these layers:
- Agents retry blindly → exponential token waste
- Agents think in circles → wasted reasoning
- Agents don't know budget status → runs out mid-task
- Agents repeat work → 50% of tokens wasted

With these layers:
- **Self-aware execution** (knows what it did)
- **Loop detection** (stops endless retries)
- **Reasoning optimization** (collapses duplicate work)
- **Budget awareness** (completes within limits)

This is critical for scaling from "one agent, one query" to "autonomous agent workflows with multiple steps, retries, and recovery."

---

## Implementation Layers (Ordered by Impact)

| Layer | Impact | Effort | Priority |
|-------|--------|--------|----------|
| 1: Execution history | 30% reduction | Low | P0 |
| 2: Loop detection | 25% reduction | Medium | P0 |
| 3: Reasoning collapse | 20% reduction | Medium | P1 |
| 4: Budget awareness | 15% reduction | Medium | P1 |

**Combined (All 4):** 80-95% efficiency improvement

---

## Integration with PyStreamMCP v0.3

Working Memory needs these 4 layers:

```python
class WorkingMemory:
    def __init__(self):
        # Layer 1: Execution history
        self.execution_history = ExecutionHistory()
        
        # Layer 2: Loop detection
        self.loop_detector = LoopDetector()
        
        # Layer 3: Reasoning optimization
        self.reasoning_optimizer = ReasoningOptimizer()
        
        # Layer 4: Budget management
        self.budget_manager = BudgetManager(token_budget=100_000)
    
    def execute_safely(self, operation):
        """Execute operation with all optimization layers"""
        
        # Layer 1: Deduplicate
        if should_repeat, cached := self.execution_history.check(operation):
            return cached
        
        # Layer 2: Detect loops before executing
        if loop_detected := self.loop_detector.is_loop_detected():
            raise LoopDetectedError(loop_detected)
        
        # Layer 3: Collapse reasoning if applicable
        operation = self.reasoning_optimizer.optimize(operation)
        
        # Layer 4: Check budget
        cost = self.budget_manager.estimate_cost(operation)
        if cost > self.budget_manager.remaining:
            raise BudgetExceededError(cost)
        
        # Safe to execute
        result = execute(operation)
        
        # Record for learning
        self.execution_history.record(operation, result)
        self.budget_manager.charge(cost)
        
        return result
```

This is how agents become **efficient and self-correcting**.
