# PyStreamMCP Workflow Integration Guide

PyStreamMCP integrates with popular workflow orchestration tools through:
1. **Bash commands** - CLI interface for shell-based workflows
2. **REST API** - HTTP endpoints for remote calls
3. **Native libraries** - Python-based orchestrators

## Setup

### Start the REST API Server

```bash
# Start server on localhost:8000
python -m pystreammcp.server

# Or with custom host/port
python -c "from pystreammcp.server import run_server; run_server(host='0.0.0.0', port=5000)"
```

### Install CLI

```bash
pip install pystreammcp
# pystreammcp command now available
```

---

## Integration Examples

### 1. Temporal (TypeScript/Go)

Temporal workflow calling PyStreamMCP via REST API:

```typescript
// temporal-workflow.ts
import * as wf from "@temporalio/workflow";
import axios from "axios";

export async function dataActivationWorkflow(
  customerId: string,
  query: string
) {
  // Call PyStreamMCP API for optimized context retrieval
  const response = await axios.post(
    "http://localhost:8000/query",
    {
      agent_id: "temporal_agent",
      text: query,
      intent: "retrieve",
    }
  );

  const optimized = response.data;

  if (optimized.cost_reduction_percent < 60) {
    throw new Error("Optimization target not met");
  }

  // Log cost savings
  wf.log.info(`Saved $${optimized.cost_saved} on query retrieval`);

  // Activate customer with optimized context
  return {
    customerId,
    contextRetrieved: true,
    costSaved: optimized.cost_saved,
  };
}
```

### 2. Apache Airflow (Python)

Airflow DAG using PyStreamMCP:

```python
# airflow_dag.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests
import json

def query_pystreammcp(**context):
    """Query PyStreamMCP for optimized context."""
    queries = [
        "Top 10 customers by LTV",
        "Churn risk indicators",
        "Engagement trends"
    ]
    
    response = requests.post(
        "http://localhost:8000/batch-query",
        json={
            "agent_id": "airflow_agent",
            "queries": queries
        }
    )
    
    result = response.json()
    print(f"Total cost saved: ${result['total_cost_saved']:.4f}")
    context['task_instance'].xcom_push(key='savings', value=result['total_cost_saved'])
    return result

def activate_data(**context):
    """Activate optimized data to destinations."""
    savings = context['task_instance'].xcom_pull(key='savings')
    print(f"Activating with ${savings:.4f} cost savings")

with DAG('data_activation', start_date=datetime(2024, 1, 1), schedule_interval='daily') as dag:
    optimize = PythonOperator(
        task_id='optimize_context',
        python_callable=query_pystreammcp,
        provide_context=True
    )
    
    activate = PythonOperator(
        task_id='activate_data',
        python_callable=activate_data,
        provide_context=True
    )
    
    optimize >> activate
```

### 3. n8n (No-Code Workflow)

n8n workflow using HTTP Request node:

```json
{
  "nodes": [
    {
      "name": "Trigger",
      "type": "n8n-nodes-base.start"
    },
    {
      "name": "Query PyStreamMCP",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://localhost:8000/query",
        "method": "POST",
        "contentType": "application/json",
        "body": {
          "agent_id": "n8n_agent",
          "text": "{{ $env.QUERY_TEXT }}",
          "intent": "retrieve"
        }
      }
    },
    {
      "name": "Check Cost Savings",
      "type": "n8n-nodes-base.if",
      "parameters": {
        "conditions": {
          "number": [
            {
              "value1": "{{ $node['Query PyStreamMCP'].json.cost_reduction_percent }}",
              "operation": "greater",
              "value2": 60
            }
          ]
        }
      }
    },
    {
      "name": "Activate Data",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://destination-api/activate",
        "method": "POST",
        "body": {
          "savings": "{{ $node['Query PyStreamMCP'].json.cost_saved }}"
        }
      }
    }
  ],
  "connections": {
    "Trigger": { "main": [[ { "node": "Query PyStreamMCP" } ]] },
    "Query PyStreamMCP": { "main": [[ { "node": "Check Cost Savings" } ]] },
    "Check Cost Savings": { "main": [[ { "node": "Activate Data" } ]] }
  }
}
```

### 4. Power Automate (Microsoft)

Power Automate cloud flow using HTTP action:

```
Trigger: Automated cloud flow (when a row is added to Excel/SharePoint)
  ↓
Action: HTTP
  Method: POST
  URI: https://your-server/api/query
  Headers:
    Content-Type: application/json
  Body:
    {
      "agent_id": "power_automate",
      "text": @{triggerBody()?['query_text']},
      "intent": "retrieve"
    }
  ↓
Action: Parse JSON
  Content: @body('HTTP')
  ↓
Action: Condition
  If: @outputs('Parse_JSON')['cost_reduction_percent'] > 60
    Then: Write results to database
    Else: Log failure
```

### 5. UiPath (RPA)

UiPath workflow using HTTP Request activity:

```
Sequence: Data Activation Workflow
  ├─ Log Message: "Starting optimization"
  ├─ HTTP Request
  │   URL: http://localhost:8000/query
  │   Method: POST
  │   Body (JSON):
  │     {
  │       "agent_id": "uipath_bot",
  │       "text": "[query_variable]",
  │       "intent": "retrieve"
  │     }
  │   Output variable: response
  │
  ├─ Deserialize JSON Activity
  │   JSON String: response
  │   Deserialized Object: optimization_result
  │
  ├─ If: optimization_result.cost_reduction_percent >= 60
  │   Then:
  │   │ └─ Set Variable: activated = true
  │   Else:
  │   └─ Log Message: "Optimization failed"
  │
  └─ Log Message: "Cost saved: $[optimization_result.cost_saved]"
```

### 6. Automation Anywhere (RPA)

Automation Anywhere bot using REST Web Service:

```
Bot Configuration:
├─ Start
├─ REST Web Service
│   URL: http://localhost:8000/query
│   Method: POST
│   Content Type: application/json
│   Body:
│     {
│       "agent_id": "automation_anywhere",
│       "text": "$queryText",
│       "intent": "retrieve"
│     }
│   Response Variable: response
│
├─ JSON Extract
│   JSON String: $response
│   Path: cost_reduction_percent
│   Variable: savings_percent
│
├─ Condition
│   If $savings_percent >= 60
│     Message Box: "Optimization successful: $savings_percent%"
│     Activate data in destination
│   Else
│     Message Box: "Optimization did not meet target"
│
└─ End
```

---

## Bash Command Integration

### Direct Command Usage

```bash
# Create agent
pystreammcp create-agent workflow_agent token_efficient 1500

# Execute query
pystreammcp query "Top customers by LTV" retrieve workflow_agent

# Get metrics
pystreammcp metrics | jq '.metrics'

# Parse JSON output in shell scripts
RESULT=$(pystreammcp query "Find segments")
COST_SAVED=$(echo $RESULT | jq '.cost_saved')
echo "Saved: $COST_SAVED"
```

### Shell Script Example

```bash
#!/bin/bash
# activate_data.sh

QUERY="${1:-Top customers by LTV}"
AGENT_ID="${2:-shell_agent}"
DEST_URL="${3:-http://localhost:9000/activate}"

echo "Querying PyStreamMCP for: $QUERY"

# Execute query
RESULT=$(pystreammcp query "$QUERY" retrieve "$AGENT_ID")

# Extract metrics
COST_SAVED=$(echo "$RESULT" | jq '.cost_saved')
REDUCTION=$(echo "$RESULT" | jq '.cost_reduction_percent')

echo "Cost reduction: $REDUCTION%"
echo "Cost saved: $COST_SAVED"

# Check if optimization met target
if (( $(echo "$REDUCTION >= 60" | bc -l) )); then
    echo "Optimization successful, activating data..."
    curl -X POST "$DEST_URL" \
      -H "Content-Type: application/json" \
      -d "$RESULT"
else
    echo "Optimization did not meet target"
    exit 1
fi
```

### Cron Job Example

```bash
# Run optimization every hour
0 * * * * /usr/local/bin/activate_data.sh "Customer metrics" etl_agent >> /var/log/pystreammcp.log 2>&1

# Run multiple queries daily
0 2 * * * /usr/local/bin/activate_data.sh "Churn indicators" daily_job http://crm-api/update
0 14 * * * /usr/local/bin/activate_data.sh "Engagement scores" daily_job http://marketing-api/update
```

---

## Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN pip install pystreammcp flask

COPY . .

EXPOSE 8000

CMD ["python", "-m", "pystreammcp.server"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  pystreammcp:
    build: .
    ports:
      - "8000:8000"
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
```

---

## Configuration Management

### Environment Variables

```bash
# .env
PYSTREAMMCP_HOST=0.0.0.0
PYSTREAMMCP_PORT=8000
PYSTREAMMCP_DEFAULT_STRATEGY=token_efficient
PYSTREAMMCP_DEFAULT_MAX_TOKENS=2000
```

### Agent Configuration File

```yaml
# agents.yaml
agents:
  temporal_agent:
    strategy: balanced
    max_tokens: 2000
    
  airflow_agent:
    strategy: token_efficient
    max_tokens: 1500
    
  n8n_agent:
    strategy: quality_first
    max_tokens: 3000
```

---

## Monitoring & Alerts

### Prometheus Metrics (Coming in Phase 3)

```
# metrics endpoint
GET /metrics

# Metrics exposed:
pystreammcp_queries_total
pystreammcp_tokens_saved_total
pystreammcp_cost_saved_total
pystreammcp_query_latency_seconds
pystreammcp_optimization_ratio_percent
```

### Health Checks

```bash
# Check server health
curl http://localhost:8000/health

# Response
{
  "status": "healthy",
  "agents_count": 5,
  "version": "0.1.0"
}
```

---

## Security Best Practices

1. **Authentication** (Phase 3+)
   ```bash
   # Use API keys
   curl -H "X-API-Key: your-api-key" http://localhost:8000/query
   ```

2. **Rate Limiting** (Phase 3+)
   ```bash
   # Limit requests per agent
   PYSTREAMMCP_RATE_LIMIT=100  # requests per minute
   ```

3. **TLS/HTTPS**
   ```bash
   # Use reverse proxy (nginx)
   proxy_pass http://pystreammcp:8000;
   proxy_ssl_protocols TLSv1.2 TLSv1.3;
   ```

4. **Network Security**
   - Run PyStreamMCP in isolated network
   - Use firewall rules to restrict access
   - Enable VPC/security group controls

---

## Summary

PyStreamMCP integrates seamlessly with any workflow tool via:
- **CLI**: Direct shell command invocation
- **REST API**: HTTP endpoints for remote tools
- **Native Python**: Direct library integration
- **Docker**: Container-based deployment

All methods support the same core features: query optimization, cost tracking, batch processing, and metrics.
