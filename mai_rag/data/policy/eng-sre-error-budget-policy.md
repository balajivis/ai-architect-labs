---
title: SRE Error Budget Policy
doc_id: eng-sre-error-budget-policy
owner: Platform Engineering
last_updated: 2026-06-01
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# SRE Error Budget Policy

## 1. Overview

An error budget is the amount of downtime or failures a service is allowed per month while still meeting its SLO (Service Level Objective). This policy defines how Northwind calculates, tracks, and manages error budgets across all services.

## 2. SLO and Error Budget Relationship

### 2.1 SLO Definitions

Each service has a target uptime % (SLO):

| Service | SLO | RTO | RPO | Error Budget (monthly) |
|---------|-----|-----|-----|----------------------|
| api-gateway | 99.9% | 4h | 1h | 43.2 minutes |
| data-connector | 99.5% | 8h | 4h | 3.6 hours |
| transformation-engine | 99.0% | 8h | 8h | 7.2 hours |
| insight-service | 99.5% | 8h | 4h | 3.6 hours |
| notification-service | 98% | 24h | 24h | 14.4 hours |
| audit-service | 99.99% | 1h | 15 min | 4.3 minutes |

**Formula**: Error Budget = (1 - SLO%) × minutes in month

Example: api-gateway with 99.9% SLO:
- (1 - 0.999) × 43,200 minutes/month = 43.2 minutes/month

### 2.2 SLI (Service Level Indicator)

SLI is the measured metric that tracks SLO compliance:

```
api-gateway SLI = successful_requests / total_requests
  where successful = status 2xx or 3xx (not 5xx)
  measured: 99.91% this month ✓ (meets 99.9% SLO)

data-connector SLI = completed_syncs / total_syncs
  where completed = sync finished without timeout (> 5 min)
  measured: 99.42% this month ✗ (misses 99.5% SLO)
```

## 3. Error Budget Tracking

### 3.1 Real-Time Dashboard

Datadog dashboard tracks error budget consumption:

```
api-gateway Error Budget Monitor
├─ SLO: 99.9% uptime
├─ Error budget: 43.2 minutes
├─ Consumed this month: 15.3 minutes (35% used)
├─ Remaining: 27.9 minutes
├─ Days until depleted: ~4 days (if current failure rate continues)
└─ Status: HEALTHY (plenty of buffer)

notification-service Error Budget Monitor
├─ SLO: 98% uptime
├─ Error budget: 14.4 hours
├─ Consumed this month: 12.8 hours (89% used)
├─ Remaining: 1.6 hours
├─ Days until depleted: < 1 day (critical state)
└─ Status: ALERT — Freeze new deployments until error budget recovered
```

### 3.2 Calculation

SLI is measured every minute and aggregated by Datadog:

```
Current hour SLI = successful_requests_this_hour / total_requests_this_hour
Monthly SLI = sum(successful_requests) / sum(total_requests) for all minutes in month
Error budget consumed = (1 - monthly_SLI) × minutes_in_month
```

## 4. Error Budget Policy and Actions

### 4.1 Green Zone (Error Budget > 30%)

**Status**: Healthy. Service is meeting SLO with comfortable margin.

**Actions**:
- ✅ Deploy features normally (see **Production Deployment Runbook**)
- ✅ Conduct experiments (canary deployments, A/B tests)
- ✅ Schedule non-critical maintenance

### 4.2 Yellow Zone (10% < Error Budget ≤ 30%)

**Status**: Caution. Approaching SLO violation.

**Actions**:
- 🟡 Reduce deployment frequency to critical bugfixes only
- 🟡 Cancel non-critical experiments
- 🟡 Increase monitoring and alert sensitivity
- 🟡 Schedule incident review: What caused the budget burn?

**Trigger**: Automatic Slack alert in `#deployments`:
```
⚠️ ALERT: notification-service error budget at 20%
Remaining: 2.8 hours
Projected depletion: 2026-06-15 18:00 PT
Action: Feature freeze activated until recovery
```

### 4.3 Red Zone (Error Budget ≤ 10%)

**Status**: Critical. Risk of SLO violation.

**Actions**:
- 🔴 **Feature freeze**: No deployments except critical hotfixes
- 🔴 **Incident review**: Mandatory meeting within 4 hours (see **Incident Response Runbook**)
- 🔴 **Escalate**: VP Engineering notified; on-call team in standby
- 🔴 **Increase monitoring**: Alert on every error; no alert suppression
- 🔴 **Rollback risky changes**: Any deployment in past 24h considered for rollback

**Trigger**: Page to on-call team:
```
🔴 CRITICAL: audit-service error budget at 8% (3 minutes remaining)
Projected depletion: 2026-06-15 16:30 PT
Action: Page on-call team immediately
```

### 4.4 Exceeded (Error Budget ≤ 0%)

**Status**: SLO violated.

**Actions**:
- 🛑 **Incident declared**: Sev-2 minimum (see **Incident Response Runbook**)
- 🛑 **War room**: VP Engineering, affected team leads, on-call engineer
- 🛑 **Root cause analysis**: Why did we miss SLO?
- 🛑 **Corrective actions**: Prevent recurrence (improve monitoring, add capacity, architectural change)
- 🛑 **Customer notification**: If SLA breach (see **Incident Response Runbook**)
- 🛑 **Post-mortem**: Within 3 business days, published to leadership

## 5. Budget Burn Rate Analysis

Fast burn rate (high error rate) vs. slow burn rate (low uptime degradation):

### 5.1 Burn Rate Alert

Alert when error budget depletes too fast:

```
api-gateway Burn Rate Alert:
├─ Fast burn (> 5x): Error rate > 5% for 10 minutes
│  Trigger: Page immediately (SLO violated in < 9 hours)
│
├─ Medium burn (2–5x): Error rate 1–5% for 1 hour
│  Trigger: Slack alert to on-call team
│
└─ Slow burn (< 2x): Error rate < 1% sustained
   Trigger: No alert (service handling gracefully)
```

## 6. Error Budget Recovery

### 6.1 Planned Downtime (Does NOT count against error budget)

If scheduled maintenance is required:

1. **Announce** in advance (48 hours notice via email + Slack)
2. **Schedule** outside peak hours (off-peak window for that region)
3. **Exclude from SLI**: Mark period as "maintenance" in Datadog
4. **Communicate**: SLO still valid because downtime was planned

Example:
```
Scheduled maintenance window: 2026-06-20 02:00–02:30 AM PT
Service: data-connector (database upgrade)
SLI exclusion: Mark in Datadog; SLO unaffected
Customer notification: Sent 48 hours and 4 hours before
```

### 6.2 Incident Recovery

After an incident that consumed error budget:

1. **Measure impact**: How many minutes of SLI lost?
2. **Implement fix**: Prevent recurrence (code change, monitoring improvement)
3. **Monitor**: Enhanced alerting for 7 days post-incident
4. **Post-mortem**: Document lessons learned (see **Incident Response Runbook**)

## 7. SLO Review and Adjustment

### 7.1 Quarterly SLO Review

Each quarter, platform team reviews SLOs:

| Service | Current SLO | Actual (Last 90d) | Recommendation | Status |
|---------|------------|------------------|-----------------|--------|
| api-gateway | 99.9% | 99.93% | Keep at 99.9% | ✓ |
| data-connector | 99.5% | 99.8% | Consider raising to 99.7% | Review |
| notification | 98% | 96.5% | Lower to 95% (unsustainable) | Discuss with PO |

### 7.2 SLO Adjustment Criteria

Increase SLO if:
- Service maintains higher uptime for 6+ months
- Infrastructure upgraded (more replicas, better hardware)
- Monitoring improved (fewer blind spots)

Decrease SLO if:
- Consistently missing target for 2+ months
- Infrastructure constraints prevent higher uptime
- New dependencies add risk (external API calls, database migrations)

**Approval**: VP Engineering + Product Lead sign-off.

## 8. Error Budget During On-Call

On-call engineers use error budget status to prioritize work:

```
Monday morning:
├─ Check error budget status for all services
├─ If any service in yellow/red zone:
│  ├─ High priority: Fix incidents, stabilize
│  └─ Low priority: Defer non-critical alerts
└─ If all green: Can work on feature improvements
```

## 9. Reporting and Communication

### 9.1 Weekly Report

Every Monday, platform team reports error budget status:

```
Slack #engineering:
📊 Error Budget Status (Week of 2026-06-01)

🟢 api-gateway: 42% budget remaining ✓
🟡 data-connector: 18% budget remaining (watch closely)
🟢 transformation-engine: 65% budget remaining ✓
🟢 insight-service: 55% budget remaining ✓
🔴 notification-service: EXCEEDED (SLO missed) ⚠️
🟢 audit-service: 88% budget remaining ✓

Action: Feature freeze on notification-service; incident review scheduled
```

### 9.2 Monthly SLO Report

Executive summary to leadership:

```
SLO Compliance — June 2026

Service          | Target | Actual | Status
---|---|---|---
api-gateway      | 99.9%  | 99.91% | ✓ Met
data-connector   | 99.5%  | 99.42% | ✗ Missed (4 minutes)
transformation   | 99.0%  | 99.15% | ✓ Met
insight-service  | 99.5%  | 99.68% | ✓ Met
notification     | 98%    | 96.5%  | ✗ Missed (1.8 hours)
audit-service    | 99.99% | 99.995%| ✓ Met

Average SLO attainment: 99.2% (target: 99.3%) — Missed by 0.1%
```

---

**Related policies:**
- See **Observability & Monitoring Standards** for SLI collection and dashboard setup
- See **Incident Response Runbook** for incident severity and escalation
- See **Production Deployment Runbook** for feature freeze procedures during red zone
- See **On-Call & Escalation Policy** for on-call responsibilities during error budget crisis
