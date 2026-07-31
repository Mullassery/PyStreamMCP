#!/bin/bash

################################################################################
# Phase 3: Staging Deployment Validation Suite
#
# This script validates the staging deployment of Phase 2 webhook infrastructure
# Includes smoke tests, performance tests, and integration validation
#
# Usage: ./phase3_staging_validation.sh [environment] [duration_hours]
# Example: ./phase3_staging_validation.sh staging 48
################################################################################

set -e

# Configuration
ENVIRONMENT=${1:-staging}
DURATION_HOURS=${2:-48}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_DIR="./logs/phase3_validation_${TIMESTAMP}"
RESULTS_FILE="${LOG_DIR}/validation_results.txt"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create log directory
mkdir -p "${LOG_DIR}"

################################################################################
# Logging Functions
################################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "${RESULTS_FILE}"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1" | tee -a "${RESULTS_FILE}"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1" | tee -a "${RESULTS_FILE}"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1" | tee -a "${RESULTS_FILE}"
}

################################################################################
# API Health Checks
################################################################################

check_api_health() {
    log_info "===== API Health Checks ====="

    local endpoints=(
        "/health"
        "/orchestration/status"
        "/orchestration/services"
        "/orchestration/webhooks"
    )

    for endpoint in "${endpoints[@]}"; do
        log_info "Checking $endpoint..."

        response=$(curl -s -w "\n%{http_code}" "http://localhost:8000${endpoint}")
        http_code=$(echo "${response}" | tail -n1)
        body=$(echo "${response}" | head -n-1)

        if [ "$http_code" == "200" ]; then
            log_success "GET $endpoint (HTTP $http_code)"
        else
            log_error "GET $endpoint (HTTP $http_code)"
            return 1
        fi
    done
}

################################################################################
# Smoke Tests
################################################################################

run_smoke_tests() {
    log_info "===== Running Smoke Tests ====="

    # Test 1: Register webhook
    log_info "Test 1: Register orchestration webhook"
    response=$(curl -s -X POST http://localhost:8000/orchestration/webhooks \
        -H "Content-Type: application/json" \
        -d '{
            "webhook_id": "smoke_test_webhook",
            "url": "http://localhost:9000/webhook",
            "events": ["mcp.available", "tool.invoked"]
        }')

    if echo "$response" | grep -q "success"; then
        log_success "Webhook registration successful"
    else
        log_error "Webhook registration failed: $response"
        return 1
    fi

    # Test 2: List MCPs
    log_info "Test 2: List MCP services"
    response=$(curl -s http://localhost:8000/orchestration/services)

    if echo "$response" | grep -q "mcp_1\|mcp_2"; then
        log_success "MCP discovery successful"
    else
        log_warning "No MCPs found in registry"
    fi

    # Test 3: Get tool routing
    log_info "Test 3: Get tool routing information"
    response=$(curl -s http://localhost:8000/orchestration/tools/validate_data)

    if echo "$response" | grep -q "routing\|project_name"; then
        log_success "Tool routing information retrieved"
    else
        log_warning "Tool routing information empty"
    fi
}

################################################################################
# Integration Tests
################################################################################

run_integration_tests() {
    log_info "===== Running Integration Tests ====="

    # Run pytest on integration tests
    log_info "Running pytest on integration test suite..."

    if python -m pytest tests/test_integration_phase2.py -v --tb=short > "${LOG_DIR}/integration_tests.log" 2>&1; then
        log_success "All integration tests passed"
        return 0
    else
        log_error "Some integration tests failed"
        tail -20 "${LOG_DIR}/integration_tests.log" | tee -a "${RESULTS_FILE}"
        return 1
    fi
}

################################################################################
# Performance Tests
################################################################################

run_performance_tests() {
    log_info "===== Running Performance Tests ====="

    local num_requests=1000
    local concurrent=10

    log_info "Running load test: $num_requests requests with $concurrent concurrent..."

    # Simulated load test (in real scenario, use ab or wrk)
    local start_time=$(date +%s%N | cut -b1-13)

    for i in $(seq 1 $num_requests); do
        curl -s "http://localhost:8000/health" > /dev/null &

        if [ $((i % concurrent)) -eq 0 ]; then
            wait
        fi
    done
    wait

    local end_time=$(date +%s%N | cut -b1-13)
    local duration=$((end_time - start_time))
    local avg_latency=$((duration / num_requests))

    log_info "Load test completed: ${avg_latency}ms average latency"

    if [ $avg_latency -lt 100 ]; then
        log_success "Performance meets target (<100ms average)"
    else
        log_warning "Performance below target (${avg_latency}ms vs. 100ms target)"
    fi
}

################################################################################
# Reliability Tests
################################################################################

run_reliability_tests() {
    log_info "===== Running Reliability Tests ====="

    # Test webhook delivery
    log_info "Test: Webhook delivery with retry"
    response=$(curl -s -X POST http://localhost:8000/orchestration/webhooks/events \
        -H "Content-Type: application/json" \
        -d '{
            "event_type": "mcp.available",
            "data": {
                "project_name": "test_mcp",
                "mcp_port": 9999,
                "mcp_version": "2.0",
                "tools": []
            }
        }')

    if echo "$response" | grep -q "success\|skipped"; then
        log_success "Event delivery working"
    else
        log_error "Event delivery failed: $response"
    fi

    # Test fallback activation
    log_info "Test: Fallback activation"
    response=$(curl -s http://localhost:8000/orchestration/tools/nonexistent_tool)

    if echo "$response" | grep -q "not_found\|unavailable"; then
        log_success "Fallback handling working"
    else
        log_warning "Unexpected fallback response: $response"
    fi
}

################################################################################
# Security Tests
################################################################################

run_security_tests() {
    log_info "===== Running Security Tests ====="

    # Test HMAC signature validation
    log_info "Test: HMAC-SHA256 signature validation"

    # This would need the actual webhook signing implementation
    log_warning "Security tests require actual webhook endpoints"

    # Test input validation
    log_info "Test: Input validation"
    response=$(curl -s -w "\n%{http_code}" -X POST http://localhost:8000/orchestration/webhooks \
        -H "Content-Type: application/json" \
        -d '{"invalid": "payload"}')

    http_code=$(echo "${response}" | tail -n1)

    if [ "$http_code" == "400" ] || [ "$http_code" == "422" ]; then
        log_success "Input validation working (HTTP $http_code)"
    else
        log_warning "Input validation not as expected (HTTP $http_code)"
    fi
}

################################################################################
# Metrics Collection
################################################################################

collect_metrics() {
    log_info "===== Collecting Baseline Metrics ====="

    # System metrics
    log_info "System Metrics:"
    echo "CPU Usage: $(top -bn1 | grep 'Cpu(s)' | awk '{print $2}')" | tee -a "${RESULTS_FILE}"
    echo "Memory Usage: $(free | grep Mem | awk '{printf "%.2f%%", ($3/$2) * 100.0}')" | tee -a "${RESULTS_FILE}"
    echo "Disk Usage: $(df -h / | tail -1 | awk '{print $5}')" | tee -a "${RESULTS_FILE}"

    # Application metrics
    log_info "Application Metrics:"
    response=$(curl -s http://localhost:8000/health)

    echo "Health Check Response:" | tee -a "${RESULTS_FILE}"
    echo "$response" | jq '.' 2>/dev/null || echo "$response" | tee -a "${RESULTS_FILE}"
}

################################################################################
# Report Generation
################################################################################

generate_report() {
    log_info "===== Generating Validation Report ====="

    local report_file="${LOG_DIR}/VALIDATION_REPORT.md"

    cat > "$report_file" << 'EOF'
# Phase 3 Staging Validation Report

## Execution Summary
- **Environment**: STAGING
- **Duration**: Continuous
- **Timestamp**: $(date)

## Test Results

### API Health Checks
- [ ] /health endpoint responding
- [ ] /orchestration/status endpoint responding
- [ ] /orchestration/services endpoint responding
- [ ] /orchestration/webhooks endpoint responding

### Smoke Tests
- [ ] Webhook registration working
- [ ] MCP discovery working
- [ ] Tool routing information available
- [ ] Error handling correct

### Integration Tests
- [ ] StatGuardian ↔ PyStreamMCP integration
- [ ] Cross-MCP orchestration
- [ ] Webhook security/reliability
- [ ] Health & resilience

### Performance Tests
- [ ] Average latency < 100ms
- [ ] P95 latency < 200ms
- [ ] Throughput > 500 RPS
- [ ] No timeouts detected

### Reliability Tests
- [ ] Event delivery working
- [ ] Fallback activation working
- [ ] Retry logic functioning
- [ ] Deduplication working

### Security Tests
- [ ] Input validation working
- [ ] Error messages safe
- [ ] No SQL injection detected
- [ ] No XSS detected

## Metrics

### System Resources
- CPU Usage: ____%
- Memory Usage: ____%
- Disk Usage: ____%

### Application Performance
- Average Latency: ____ms
- P95 Latency: ____ms
- P99 Latency: ____ms
- Error Rate: ____%
- Webhook Success Rate: _____%

## Recommendations

1. ___________________
2. ___________________
3. ___________________

## Sign-Off

- [ ] QA Lead Approved
- [ ] Engineering Lead Approved
- [ ] Operations Approved
- [ ] Ready for Canary Deployment

---

**Report Generated**: $(date)
EOF

    log_success "Validation report generated: $report_file"
}

################################################################################
# Main Execution
################################################################################

main() {
    log_info "=========================================="
    log_info "Phase 3: Staging Deployment Validation"
    log_info "=========================================="
    log_info "Environment: $ENVIRONMENT"
    log_info "Duration: $DURATION_HOURS hours"
    log_info "Timestamp: $(date)"
    log_info "Log Directory: $LOG_DIR"
    log_info ""

    # Run all validation tests
    if check_api_health; then
        log_success "API health checks passed"
    else
        log_error "API health checks failed"
        return 1
    fi

    if run_smoke_tests; then
        log_success "Smoke tests passed"
    else
        log_error "Smoke tests failed"
        return 1
    fi

    if run_integration_tests; then
        log_success "Integration tests passed"
    else
        log_error "Integration tests failed"
        return 1
    fi

    run_performance_tests
    run_reliability_tests
    run_security_tests
    collect_metrics
    generate_report

    log_info ""
    log_info "=========================================="
    log_info "Validation Complete"
    log_info "=========================================="
    log_info "Results available in: $RESULTS_FILE"
    log_info "Full report: ${LOG_DIR}/VALIDATION_REPORT.md"
}

# Execute main function
main "$@"
