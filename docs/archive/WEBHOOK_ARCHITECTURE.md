# PyStreamMCP Webhook Event Router Architecture
**Phase 2 Pre-Planning Document**

**Date**: 2026-07-31  
**Status**: Design Complete  
**Effort Estimate**: 2-3 weeks  
**Priority**: CRITICAL

---

## Executive Summary

Webhooks for PyStreamMCP enable **automatic event routing and orchestration** across 19 MCP projects (228 tools). Instead of polling for MCP availability, projects push status events that allow PyStreamMCP to route requests dynamically.

### Current Pain
- PyStreamMCP polls each of 19 projects to check MCP availability (228 endpoints)
- Unknown which tools are actually available/ready
- Default routing may send requests to unavailable endpoints
- Manual discovery refresh (every N minutes)
- Cross-project orchestration requires manual tool mapping

### Webhook Solution
- **Real-time discovery**: Projects announce MCP availability instantly
- **Smart routing**: Automatic routing to available tools
- **Cross-MCP orchestration**: Events cascade through tool chains
- **Fallback management**: Gracefully handle unavailable MCPs
- **Metrics collection**: Track tool usage and performance

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│  19 MCP Projects (228 Tools)                            │
│  ├─ StatGuardian (port 8765, 9 tools)                  │
│  ├─ PyReverseETL (port 8766, 14 tools)                 │
│  ├─ PrismNote (port 8767, 11 tools)                    │
│  └─ ... 16 more projects                               │
└────────────────────┬─────────────────────────────────────┘
                     │ MCP status events
                     ▼
         ┌──────────────────────────┐
         │ Event Publisher          │
         │ (each project)           │
         │                          │
         │ mcp.available            │
         │ mcp.unavailable          │
         │ tool.invoked             │
         │ tool.result              │
         └────────────┬─────────────┘
                      │
      ┌───────────────┼───────────────┐
      │               │               │
      ▼               ▼               ▼
  PyStreamMCP   Lineage System  Monitoring System
  (Event Router) (track deps)    (metrics)
      │
      ├─ Discover available MCPs
      ├─ Update service registry
      ├─ Route tool invocations
      ├─ Aggregate results
      └─ Track cross-project dependencies
```

### Event Flow

```
1. MCP Project Startup/Readiness
   ├─ Project 1 (StatGuardian) ready
   └─ Emit: mcp.available { project: StatGuardian, port: 8765, tools: [...] }

2. PyStreamMCP Receives Event
   ├─ Update service registry
   ├─ Mark 9 StatGuardian tools as available
   └─ Notify interested subscribers

3. Tool Invocation Request Arrives
   ├─ Query: "validate_data for customers"
   ├─ PyStreamMCP looks up routing: validate_data → StatGuardian
   ├─ Emit: tool.invoked { tool: validate_data, project: StatGuardian, params: {...} }
   └─ Route request to StatGuardian:8765/validate_data

4. Tool Execution Complete
   ├─ StatGuardian tool returns result
   ├─ Emit: tool.result { tool: validate_data, status: success, result: {...} }
   └─ Return aggregated result to client

5. Cross-Project Orchestration
   ├─ Tool A (StatGuardian) completes
   ├─ Emit: tool.result event
   ├─ PyStreamMCP routes output to next tool
   ├─ Emit: tool.invoked for dependent tool
   └─ Chain continues until complete
```

---

## Webhook Event Types

### 1. mcp.available
**Triggered**: MCP project/tool becomes available  
**Publisher**: Each MCP project (on startup/readiness)

```json
{
  "event_type": "mcp.available",
  "timestamp": "2026-07-31T12:30:00Z",
  "entity_id": "statguardian_8765",
  "entity_type": "mcp_endpoint",
  "action": "available",
  "source_system": "statguardian",
  "data": {
    "project_name": "StatGuardian",
    "mcp_port": 8765,
    "mcp_version": "2.0",
    "tools": [
      {
        "name": "validate_data",
        "description": "Validate data against quality contract",
        "input_schema": {...},
        "output_schema": {...}
      },
      {
        "name": "detect_drift",
        "description": "Detect statistical drift"
      }
    ],
    "tool_count": 9,
    "health_status": "healthy",
    "performance_metrics": {
      "avg_latency_ms": 45,
      "success_rate_pct": 99.8,
      "throughput_rps": 150
    }
  },
  "metadata": {
    "startup_time_ms": 2340,
    "version": "2.0.0",
    "environment": "production"
  }
}
```

### 2. mcp.unavailable
**Triggered**: MCP project becomes unavailable  
**Publisher**: Health monitor or project shutdown

```json
{
  "event_type": "mcp.unavailable",
  "timestamp": "2026-07-31T12:35:00Z",
  "entity_id": "statguardian_8765",
  "entity_type": "mcp_endpoint",
  "action": "unavailable",
  "source_system": "statguardian",
  "data": {
    "project_name": "StatGuardian",
    "mcp_port": 8765,
    "reason": "health_check_failed",
    "last_healthy_check": "2026-07-31T12:34:55Z",
    "affected_tools": 9,
    "recommended_action": "retry_with_fallback"
  }
}
```

### 3. tool.invoked
**Triggered**: Tool invocation request initiated  
**Publisher**: PyStreamMCP orchestration layer

```json
{
  "event_type": "tool.invoked",
  "timestamp": "2026-07-31T12:30:05Z",
  "entity_id": "tool_invocation_123",
  "entity_type": "tool_execution",
  "action": "invoked",
  "source_system": "pystreammcp",
  "data": {
    "tool_name": "validate_data",
    "project_name": "StatGuardian",
    "mcp_port": 8765,
    "invocation_id": "inv_123",
    "user_id": "user_abc",
    "request_context": {
      "contract_id": "cust_v2",
      "data_source": "s3://data/customers.parquet"
    },
    "orchestration_context": {
      "chain_id": "chain_456",
      "position_in_chain": 1,
      "total_chain_length": 3,
      "upstream_results": []
    }
  }
}
```

### 4. tool.result
**Triggered**: Tool execution completes  
**Publisher**: Each MCP project

```json
{
  "event_type": "tool.result",
  "timestamp": "2026-07-31T12:30:08Z",
  "entity_id": "tool_invocation_123",
  "entity_type": "tool_execution",
  "action": "completed",
  "source_system": "statguardian",
  "data": {
    "tool_name": "validate_data",
    "project_name": "StatGuardian",
    "invocation_id": "inv_123",
    "status": "success",
    "execution_time_ms": 245,
    "result": {
      "passed": true,
      "failed_checks": [],
      "affected_rows": 0,
      "recommendations": []
    },
    "cascade_triggers": [
      {
        "tool_name": "detect_drift",
        "project_name": "StatGuardian",
        "trigger_condition": "validation_passed",
        "priority": "high"
      }
    ]
  }
}
```

### 5. mcp.health_update
**Triggered**: Periodic health check results  
**Publisher**: Each MCP project (heartbeat)

```json
{
  "event_type": "mcp.health_update",
  "timestamp": "2026-07-31T12:31:00Z",
  "entity_id": "statguardian_8765",
  "entity_type": "mcp_endpoint",
  "action": "health_check",
  "source_system": "statguardian",
  "data": {
    "project_name": "StatGuardian",
    "mcp_port": 8765,
    "health_status": "healthy",
    "metrics": {
      "cpu_usage_pct": 35,
      "memory_usage_mb": 156,
      "active_requests": 12,
      "avg_latency_ms": 42,
      "success_rate_pct": 99.9,
      "throughput_rps": 145,
      "request_queue_length": 2
    },
    "alerts": []
  }
}
```

### 6. tool.dependency_required
**Triggered**: Tool needs output from another tool  
**Publisher**: MCP projects during tool execution

```json
{
  "event_type": "tool.dependency_required",
  "timestamp": "2026-07-31T12:30:06Z",
  "entity_id": "tool_invocation_123",
  "entity_type": "tool_execution",
  "action": "waiting",
  "source_system": "statguardian",
  "data": {
    "current_tool": "detect_drift",
    "current_project": "StatGuardian",
    "dependency_tool": "establish_baseline",
    "dependency_project": "StatGuardian",
    "waiting_reason": "baseline_not_established",
    "timeout_ms": 5000,
    "fallback_strategy": "skip_drift_check"
  }
}
```

---

## Integration Points

### 1. PyStreamMCP Router Integration
**Current**: Polls each MCP for tool availability  
**Webhook**: Receives mcp.available/unavailable events

```
Event Receiver:
├─ Receive: mcp.available event
├─ Parse: Tool list + metadata
├─ Update: Service registry
├─ Notify: Routing engine
└─ Enable: Dynamic routing to project
```

### 2. Cross-Project Tool Chaining
**Current**: Manual tool dependency mapping  
**Webhook**: Automatic cascade on tool.result

```
Tool Chain Handler:
├─ Receive: tool.result event
├─ Check: Cascade triggers
├─ Route: Output to next tool
├─ Invoke: Dependent tool
└─ Track: Chain execution progress
```

### 3. Fallback Management
**Current**: Failed tool invocations return errors  
**Webhook**: Automatic fallback on mcp.unavailable

```
Fallback Handler:
├─ Receive: mcp.unavailable event
├─ Mark: Tools as unavailable
├─ Route: To fallback MCPs
├─ Notify: Client of degradation
└─ Queue: Retry when available
```

### 4. Performance Metrics
**Current**: Post-execution metrics only  
**Webhook**: Real-time performance tracking

```
Metrics Collector:
├─ Receive: tool.invoked event
├─ Track: Start time
├─ Receive: tool.result event
├─ Calculate: Latency + throughput
└─ Update: Performance dashboard
```

---

## Implementation Design

### File Structure

```
PyStreamMCP/
├── python/pystreammcp/
│   ├── webhooks.py (NEW - 400 lines)
│   │   ├─ EventWebhookManager (register, deliver, track)
│   │   ├─ EventWebhookEvent (standardized payload)
│   │   └─ EventWebhookDelivery (tracking)
│   │
│   ├── webhook_router.py (NEW - 350 lines)
│   │   ├─ EventRouter (route events to handlers)
│   │   ├─ ServiceRegistry (MCP availability tracking)
│   │   ├─ ToolChainOrchestrator (cross-project tool routing)
│   │   └─ FallbackManager (handle unavailable MCPs)
│   │
│   ├── webhook_handlers.py (NEW - 300 lines)
│   │   ├─ MCPAvailabilityHandler
│   │   ├─ ToolInvocationHandler
│   │   ├─ ToolResultHandler
│   │   ├─ CrossProjectHandler
│   │   └─ HealthUpdateHandler
│   │
│   ├── discovery.py (MODIFIED +100 lines)
│   │   └─ Integrate EventRouter for dynamic discovery
│   │
│   ├── server.py (MODIFIED +150 lines)
│   │   ├─ Add WebhookManager initialization
│   │   ├─ Add webhook endpoints (11 endpoints)
│   │   └─ Add event routing endpoints
│   │
│   ├── _mcp_tools.py (MODIFIED +120 lines)
│   │   ├─ Add webhook management tools (MCP 2.0)
│   │   └─ Add orchestration tools
│   │
│   └── agent.py (MODIFIED +80 lines)
│       └─ Use EventRouter for dynamic tool discovery
│
├── tests/
│   └── test_webhook_router.py (NEW - 450 lines)
│       ├─ Test MCP availability/discovery
│       ├─ Test tool routing
│       ├─ Test tool chaining
│       ├─ Test fallback logic
│       └─ Test cross-project orchestration
│
└── docs/
    ├── WEBHOOK_INTEGRATION.md (NEW - 400 lines)
    │   ├─ Complete API reference
    │   ├─ Event type definitions
    │   ├─ Routing strategies
    │   └─ Orchestration examples
    │
    └── WEBHOOK_ARCHITECTURE.md (this file)
```

### Core Classes

**EventWebhookManager** (Reuse from PyReverseETL)
```python
class EventWebhookManager(WebhookManager):
    """Webhook manager for orchestration events"""
    
    def register_event_webhook(
        self,
        webhook_id: str,
        url: str,
        events: List[str],  # mcp.available, tool.invoked, etc.
        filters: Optional[Dict[str, Any]] = None  # Filter by project, tool, etc.
    ) -> EventWebhookConfig
```

**ServiceRegistry** (New)
```python
class ServiceRegistry:
    """Track availability of all 19 MCPs and 228 tools"""
    
    def get_available_mcps(self) -> List[MCPEndpoint]
    
    def find_tool(self, tool_name: str) -> Optional[MCPEndpoint]
    
    def get_tools_by_project(self, project_name: str) -> List[Tool]
    
    def mark_mcp_available(self, event: EventWebhookEvent)
    
    def mark_mcp_unavailable(self, event: EventWebhookEvent)
    
    def update_health_metrics(self, event: EventWebhookEvent)
```

**ToolChainOrchestrator** (New)
```python
class ToolChainOrchestrator:
    """Orchestrate cross-project tool chains"""
    
    async def route_tool_invocation(
        self,
        tool_name: str,
        params: Dict[str, Any],
        chain_context: Optional[Dict] = None
    ) -> ToolResult
    
    async def cascade_on_result(
        self,
        tool_result: ToolResult,
        cascade_triggers: List[Dict]
    ) -> List[ToolResult]
    
    def find_fallback_tool(self, tool_name: str) -> Optional[str]
```

**FallbackManager** (New)
```python
class FallbackManager:
    """Handle MCP failures with graceful fallbacks"""
    
    def register_fallback(
        self,
        primary_tool: str,
        fallback_tool: str
    )
    
    async def invoke_with_fallback(
        self,
        tool_name: str,
        params: Dict,
        fallback_enabled: bool = True
    ) -> ToolResult
    
    async def retry_queue_processor(self)
```

### Event Router Architecture

```python
class EventRouter:
    """Main orchestration event router"""
    
    def __init__(self):
        self.service_registry = ServiceRegistry()
        self.tool_orchestrator = ToolChainOrchestrator()
        self.fallback_manager = FallbackManager()
        self.handlers = {
            "mcp.available": MCPAvailabilityHandler(),
            "mcp.unavailable": MCPUnavailabilityHandler(),
            "tool.invoked": ToolInvocationHandler(),
            "tool.result": ToolResultHandler(),
            "mcp.health_update": HealthUpdateHandler(),
            "tool.dependency_required": DependencyHandler(),
        }
    
    async def route(self, event: EventWebhookEvent) -> Any:
        """Route event to appropriate handler"""
        handler = self.handlers.get(event.event_type)
        if handler:
            return await handler.handle(event)
        return None
```

### Flask REST Endpoints (in server.py)

```python
# Webhook management (11 endpoints similar to PyReverseETL)
POST   /orchestration/webhooks              # Register
GET    /orchestration/webhooks              # List
DELETE /orchestration/webhooks/{id}         # Unregister
POST   /orchestration/webhooks/{id}/enable  # Enable
POST   /orchestration/webhooks/{id}/disable # Disable

# Event handling
POST   /orchestration/webhooks/events       # Receive event
GET    /orchestration/webhooks/deliveries   # View history
POST   /orchestration/webhooks/deliveries/retry

# Orchestration-specific
GET    /orchestration/services              # List available MCPs
GET    /orchestration/services/{project}    # Tools in project
GET    /orchestration/tools/{tool_name}     # Tool location
POST   /orchestration/invoke/{tool_name}    # Invoke with routing
```

### MCP Tools (in _mcp_tools.py)

```python
# Orchestration webhook management tools (6 new tools)
- register_event_webhook
- list_event_webhooks
- unregister_event_webhook
- get_orchestration_metrics
- discover_available_tools
- invoke_tool_with_routing
```

---

## Service Registry Design

### MCP Endpoint Tracking

```python
@dataclass
class MCPEndpoint:
    project_name: str        # "StatGuardian"
    port: int                # 8765
    status: str              # "healthy" | "degraded" | "unavailable"
    tools: List[Tool]        # Available tools
    health_metrics: Dict     # CPU, memory, latency, etc.
    last_heartbeat: datetime
    fallback_endpoints: List[MCPEndpoint]  # Backup MCPs
```

### Smart Routing Strategy

```
Tool Invocation Request:
├─ Query tool location: find_tool("validate_data")
├─ Check primary MCP: StatGuardian available? Yes
├─ Route to StatGuardian:8765/validate_data
│
If StatGuardian unavailable:
├─ Check fallback MCPs (configured)
├─ Route to fallback endpoint
├─ Notify PyStreamMCP of degradation
└─ Retry primary when available
```

---

## Performance & Scalability

### Throughput Target
- **Baseline**: 100 tool invocations/sec
- **Target**: 500+ tool invocations/sec (5x)
- **Achieved via**: Parallel routing, connection pooling, caching

### Latency Target
- **Baseline**: 50ms average tool latency
- **Target**: <30ms average (30% improvement)
- **Achieved via**: Local service registry (no polling), smart routing

### MCP Discovery
- **Baseline**: Polling every 60 seconds (19 projects × polling cost)
- **Webhook**: <1 second event-driven discovery (instant)
- **Savings**: 60× reduction in polling overhead

---

## Testing Strategy

### Unit Tests (100 lines each)
- Test service registry updates
- Test tool routing logic
- Test fallback selection
- Test event routing dispatch
- Test cascade trigger logic
- Test health metric tracking

### Integration Tests (150 lines each)
- Test full tool invocation flow
- Test cross-project tool chaining
- Test fallback on unavailability
- Test service registry sync
- Test tool result cascading

### Load Tests
- 500+ concurrent tool invocations
- Sub-30ms average latency
- 99%+ success rate
- Zero registration/discovery lag

### Chaos Tests
- MCP endpoint failures (test fallback)
- Network partitions (test retry)
- Health check delays (test timeout)
- Event delivery failures (test retry)

---

## Deployment Plan

### Phase 2A: Core Infrastructure (1 week)
- [ ] Implement webhooks.py, webhook_router.py
- [ ] Build ServiceRegistry and ToolChainOrchestrator
- [ ] Add Flask endpoints
- [ ] Write unit tests

### Phase 2B: Integration (1 week)
- [ ] Integrate with discovery.py
- [ ] Add MCP tools for webhook management
- [ ] Integration testing with all 19 projects
- [ ] Load testing

### Phase 2C: Deployment (1 week)
- [ ] Deploy to staging
- [ ] Verify with all 19 MCPs
- [ ] Production deployment
- [ ] Monitor and optimize

---

## Success Metrics (Phase 2)

- ✓ All 19 MCPs discoverable within <1 second of startup
- ✓ Tool invocations routed correctly 100% of the time
- ✓ Sub-30ms average tool invocation latency
- ✓ 99.5%+ webhook delivery success rate
- ✓ Automatic fallback on MCP unavailability
- ✓ Cross-project tool chaining works seamlessly
- ✓ Zero regression in baseline performance

---

## Dependencies & Integration

### Inbound
- PyReverseETL (use webhook events for data movement)
- StatGuardian (use webhook events for quality gates)
- All 19 MCP projects (emit mcp.available/unavailable)

### Outbound
- All 19 MCP projects receive tool.invoked events
- Monitoring systems receive metrics via webhooks
- Lineage system receives cross-project dependency info

### No Blockers
- Webhooks are opt-in (backward compatible)
- Polling still works as fallback
- Can deploy independently

---

## Rollout Timeline

**Week 1**: Design + Code Review (Done with this document)  
**Week 2-2.5**: Implementation + Testing
**Week 2.5-3**: Integration + Deployment

---

## Next Steps

1. ✅ **Architecture Review**: COMPLETE (this document)
2. **Code Implementation**: Start Week 1
   - Adapt PyReverseETL webhook pattern
   - Build ServiceRegistry + ToolChainOrchestrator
   - Add FallbackManager
3. **Testing**: Week 2-2.5
   - Unit tests for routing logic
   - Integration with all 19 projects
   - Load testing (500+ RPS)
4. **Deployment**: Week 3
   - Staging deployment
   - Production deployment
   - Monitor for 48 hours

---

**Document Status**: Ready for Implementation  
**Approval Needed**: Tech lead review  
**Estimated Effort**: 2-3 weeks  
**Risk Level**: LOW (proven pattern from PyReverseETL)
