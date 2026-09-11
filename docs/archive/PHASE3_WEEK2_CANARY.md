# Phase 3 Week 2: Canary Deployment (Aug 8-12, 2026)

**Status**: PENDING (Scheduled to begin Aug 8)  
**Timeline**: 5 days  
**Objective**: Deploy to 10% production traffic, monitor, obtain decision for progressive rollout

---

## Overview

Canary deployment is a low-risk way to validate production readiness before full rollout. We deploy Phase 2 code to 10% of production traffic and monitor intensively for 2-4 hours.

**Success Criteria**:
- Error rate < 0.1%
- Latency p95 < 100ms
- Webhook delivery > 99.9%
- No critical incidents
- Zero data loss

**Rollback Triggers**:
- Error rate > 1% for 5+ minutes → automatic rollback
- Latency p95 > 500ms for 5+ minutes → automatic rollback
- Webhook delivery < 99% for 5+ minutes → automatic rollback
- Any critical incident → immediate rollback

---

## Sunday, Aug 8: Canary Deployment (10% Traffic)

### Pre-Deployment (8am-10am)

**Checklist**:
- [ ] Confirm staging validation complete (all tests passing)
- [ ] Verify team sign-off obtained
- [ ] Confirm rollback plan tested
- [ ] Activate on-call team
- [ ] Notify all stakeholders
- [ ] Open war room channel
- [ ] Start metrics dashboards
- [ ] Brief team on procedure

**Communications**:
- Slack: #phase3-deployment - "Canary deployment beginning at 10am"
- Email: Stakeholders notified
- War room: https://zoom.internal/c/warroom (open and recording)

### Deployment Window (10am-11am)

**Step 1: Pre-Deployment Checks** (10:00am - 10:05am)
```bash
# 1. Verify production API health
curl -s https://api.production.com/health | jq .

# 2. Check database connection
python -c "from app import db; db.session.execute('SELECT 1')"

# 3. Verify all services available
curl -s https://statguardian.production.com/health
curl -s https://pyreverseetl.production.com/health

# 4. Snapshot metrics
aws cloudwatch get-metric-statistics --metric-name CPUUtilization \
  --namespace AWS/EC2 --statistics Average
```

**Step 2: Deploy Code** (10:05am - 10:15am)
```bash
# 1. Pull latest code
git pull origin main  # Commit 0b73c06

# 2. Run database migrations (if any)
python -m flask db upgrade --tag canary

# 3. Deploy to 10% of servers
# Use load balancer to route 10% traffic to new deployment
# OR use AWS CodeDeploy with deployment group for 10% traffic
./scripts/deploy.sh --version=0b73c06 --traffic=10% --env=production

# 4. Verify deployment
curl -s https://api.production.com/health | jq .version
# Should return "0b73c06"
```

**Step 3: Enable Enhanced Monitoring** (10:15am - 10:20am)
```bash
# 1. Increase metrics collection frequency (1 second instead of 5)
export METRICS_INTERVAL=1s

# 2. Enable detailed logging
export LOG_LEVEL=DEBUG

# 3. Activate anomaly detection
python scripts/start_anomaly_detection.py

# 4. Open dashboards
# Grafana: https://grafana.production.com (open in separate window)
# Prometheus: https://prometheus.production.com
# Status Page: https://status.example.com (set to "Canary Deployment")
```

**Step 4: Warm Up** (10:20am - 10:30am)
- Verify canary traffic flowing
- Run synthetic tests
- Verify no immediate errors

```bash
# Run synthetic tests
python scripts/synthetic_tests.py --endpoint=api.production.com \
  --duration=10m --rate=10/sec
```

### Monitoring Phase (10:30am - 2:30pm) - 4 hours

**Real-Time Metrics to Watch**:
- Error rate (target: <0.1%)
- Latency p95 (target: <100ms)
- Webhook delivery success (target: >99.9%)
- MCP health status
- Resource usage (CPU, memory)
- Request throughput
- Database connection pool

**Monitoring Commands**:
```bash
# Terminal 1: Error rate monitoring
watch -n 1 'curl -s https://prometheus.production.com/api/v1/query \
  --data-urlencode "query=rate(errors_total[1m])" | jq'

# Terminal 2: Latency monitoring
watch -n 1 'curl -s https://prometheus.production.com/api/v1/query \
  --data-urlencode "query=histogram_quantile(0.95, rate(request_duration_seconds_bucket[1m]))" | jq'

# Terminal 3: Log monitoring
tail -f /var/log/pystreammcp/production.log | grep -E "ERROR|CRITICAL"

# Terminal 4: Grafana dashboard
# Open in browser: https://grafana.production.com/d/canary

# Terminal 5: War room monitoring
# Keep zoom open with screen share of metrics
```

**Hourly Checks** (10:30am, 11:30am, 12:30pm, 1:30pm, 2:30pm):

```
Checkpoint:
├─ Error rate: ___% (threshold: <0.1%)
├─ Latency p95: ___ms (threshold: <100ms)
├─ Webhook success: ___% (threshold: >99.9%)
├─ Memory usage: ___% (looking for leaks)
├─ Database health: OK/DEGRADED
├─ Anomalies detected: YES/NO
├─ Incidents: NONE/[list]
├─ Team assessment: GO/HOLD/ABORT
└─ Next action: Continue/Investigate/Rollback
```

**Action Triggers**:

| Metric | Threshold | Action |
|--------|-----------|--------|
| Error rate > 1% (5+ min) | CRITICAL | Automatic rollback |
| Latency p95 > 500ms (5+ min) | CRITICAL | Automatic rollback |
| Webhook delivery < 99% (5+ min) | CRITICAL | Automatic rollback |
| Memory growing > 5%/min | HIGH | Investigate memory leak |
| Database connection pool > 90% | HIGH | Investigate connection usage |
| MCP unavailable | HIGH | Check MCP health, investigate |
| Unusual error pattern | MEDIUM | Investigate root cause |

### Decision Point (2:30pm-3:00pm)

**Decision Tree**:

```
Is error rate < 0.1%?
├─ NO → ROLLBACK (automatic already triggered)
└─ YES (continue)
    ├─ Is latency p95 < 100ms?
    │  ├─ NO → INVESTIGATE (likely capacity issue)
    │  └─ YES (continue)
    │      ├─ Is webhook delivery > 99.9%?
    │      │  ├─ NO → ROLLBACK
    │      │  └─ YES (continue)
    │      │      ├─ Are there critical incidents?
    │      │      │  ├─ YES → ROLLBACK or PAUSE
    │      │      │  └─ NO (continue)
    │      │      │      ├─ Is memory stable?
    │      │      │      │  ├─ NO (leaking) → ROLLBACK
    │      │      │      │  └─ YES → SUCCESS
    │      │      │      │
    │      │      │      └─ PROCEED TO PROGRESSIVE ROLLOUT
```

**Sign-Off for Progressive Rollout**:

```
Canary Deployment Sign-Off

Date: Aug 8, 2026
Time: [2:30pm-3:00pm]
Canary Version: 0b73c06
Traffic: 10%

Metrics (4-hour window):
├─ Error rate: [%]
├─ Latency p50: [ms]
├─ Latency p95: [ms]
├─ Latency p99: [ms]
├─ Webhook delivery: [%]
├─ Uptime: [%]
└─ Memory: [stable/leaked]

Incidents: [list or none]

Decision: [✅ GO / ⏸ HOLD / ❌ ROLLBACK]

Approved By:
├─ [x] Engineering Lead (signature)
├─ [x] Operations Lead (signature)
└─ [x] On-Call Primary (signature)

Next Action: [Progressive Rollout Aug 12 / Investigate / Rollback]
```

---

## Monday-Wednesday, Aug 9-11: Investigation & Holdover

### If Canary Goes Well

**Aug 9-11: Wait Period**
- Monitor canary metrics continuously
- Ensure stability maintained
- Run additional validation tests
- Prepare for progressive rollout

**Aug 12: Decision for 25% Rollout**
```
✅ Metrics stable for 72+ hours?
├─ YES → Proceed to 25% deployment
└─ NO → Continue canary monitoring
```

### If Issues Detected

**Investigation Steps**:
1. Identify root cause
2. Determine if fix needed or investigation only
3. If fix needed:
   - Implement fix in code
   - Re-test in staging
   - Re-deploy canary
   - Monitor for 2-4 hours
   - Re-evaluate

4. If investigation only:
   - Document finding
   - Plan mitigation for production
   - Proceed with knowledge

---

## Tuesday, Aug 12: Progressive Rollout Decision

**Morning (9am-12pm): Final Review**
- Review 4-day canary metrics
- Confirm no degradation
- Verify memory stable
- Check for any slow issues

**Afternoon (1pm-3pm): Decision Meeting**
```
Decision: Should we proceed to 25% rollout?

Analysis:
├─ Canary metrics green? [YES/NO]
├─ Any concerning trends? [list or none]
├─ Team confidence level? [high/medium/low]
├─ Any open issues? [list or none]
└─ Risk assessment? [low/medium/high]

Go/No-Go Vote:
├─ Engineering Lead: [GO/NO-GO]
├─ Operations Lead: [GO/NO-GO]
└─ On-Call Primary: [GO/NO-GO]

Result: [✅ PROCEED / ⏸ HOLD / ❌ ROLLBACK]
```

If GO: Proceed to Week 2, Day 3

---

## Rollback Procedures

### Automatic Rollback (Triggered by Metrics)

When error rate > 1% for 5+ minutes:
```bash
# 1. Immediately triggered (automated)
./scripts/rollback.sh --version=previous --traffic=100% --env=production

# 2. Verify rollback successful
curl -s https://api.production.com/health | jq .version
# Should return previous version hash

# 3. Monitor metrics
# Watch error rate drop back below 0.1%
# Watch latency return to baseline

# 4. Notify team
# Slack: #phase3-deployment - "Automatic rollback triggered. Version: [old] → [new]"
# War room: Post incident details
```

### Manual Rollback (If Issues Detected)

```bash
# 1. Stop canary traffic
./scripts/deploy.sh --stop --version=0b73c06

# 2. Revert to previous version
./scripts/deploy.sh --version=previous --traffic=100%

# 3. Verify rollback
curl -s https://api.production.com/health | jq .

# 4. Investigate issue
# Create incident report
# Root cause analysis
# Plan remediation

# 5. Communicate
# Status update to stakeholders
# Reschedule canary for when issue is fixed
```

### Post-Rollback Actions

1. **Immediate** (first hour)
   - Verify rollback successful
   - Monitor metrics return to baseline
   - Notify stakeholders
   - Stop enhanced monitoring

2. **Short-term** (next day)
   - Root cause analysis
   - Fix identified issue in code
   - Re-test fix in staging
   - Plan new canary attempt

3. **Communication**
   - Send incident summary
   - Document lessons learned
   - Schedule follow-up

---

## Incident Response During Canary

### If Critical Issue Detected

**Escalation**:
```
1. Alert triggered → On-call responds (immediate)
2. Incident severity assessed → Escalate if critical
3. War room opened → Team assembles
4. Root cause identified → Fix or rollback decided
5. Action taken → Rollback or fix deployed
6. Monitoring → Verify resolution
```

**Critical Issue Examples**:
- Data corruption detected
- Security breach found
- Production API down
- Massive performance degradation
- Webhook delivery < 95%
- Complete MCP unavailability
- Database connection exhaustion

**Response**:
1. Page on-call immediately
2. Open war room
3. Assess severity
4. Make rollback decision (usually immediate for critical)
5. Execute rollback
6. Post-incident review

---

## Success Metrics for Week 2

### Canary Success
- ✅ 4-hour monitoring completed
- ✅ Error rate < 0.1% throughout
- ✅ Latency p95 < 100ms throughout
- ✅ Webhook delivery > 99.9% throughout
- ✅ No critical incidents
- ✅ Memory stable (no leaks)
- ✅ Proceed to progressive rollout approved

### Decision Criteria Met
- ✅ Metrics confirm production readiness
- ✅ Team confidence high
- ✅ Zero show-stoppers identified
- ✅ Rollback plan verified working (if needed)
- ✅ Monitoring infrastructure validated

---

## Next Phase: Progressive Rollout (Aug 12-15)

Upon successful canary sign-off:
- Aug 12 (Tue): 25% rollout
- Aug 13 (Wed): 50% rollout
- Aug 13 (Wed): 100% rollout
- Aug 14-15 (Thu-Fri): 24-hour monitoring

---

**Phase 3 Week 2 Status**: PENDING (Aug 8-12)  
**Previous**: Phase 3 Week 1 (Aug 2-7)  
**Next**: Phase 3 Week 2-3 Progressive Rollout (Aug 12-15)
