---
title: Observability & Monitoring Standards (Datadog)
doc_id: eng-observability-monitoring-standards
owner: Platform Engineering
last_updated: 2026-06-01
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Observability & Monitoring Standards (Datadog)

## 1. Overview

Observability is the ability to understand system behavior from external outputs. Northwind uses **Datadog** as the unified platform for logs, metrics, traces, and synthetics monitoring. All services must emit observability signals.

## 2. Core Pillars: Logs, Metrics, Traces

### 2.1 Structured Logging

All services emit structured JSON logs to stdout:

```json
{
  "timestamp": "2026-06-01T14:30:45.123Z",
  "level": "INFO",
  "logger": "data-connector",
  "message": "Customer data sync started",
  "service": "data-connector",
  "environment": "prod",
  "service_version": "1.5.2",
  "context": {
    "customer_id": "42",
    "data_source_type": "salesforce",
    "sync_id": "sync-abc123"
  },
  "duration_ms": null,
  "error": null
}
```

**Log levels**:
- **DEBUG**: Granular diagnostic info (disabled in production)
- **INFO**: Important lifecycle events (service start, sync begin/end, deployment)
- **WARN**: Degraded functionality (retry after transient failure, fallback activated)
- **ERROR**: Service-impacting issues (failed API call, database error, validation failure)

**PII redaction**: No personal data (email, SSN, IP, phone) in logs (see **Secrets Management Standard**).

### 2.2 Metrics (Prometheus)

All services expose Prometheus metrics on port 9090:

```
GET http://service:9090/metrics
```

**Standard metrics** (auto-collected by Datadog agent):

```
# Counter: total requests by service, method, endpoint
http_requests_total{service="data-connector",method="POST",endpoint="/sync",status="200"} 15243

# Histogram: request latency buckets
http_request_duration_seconds_bucket{service="data-connector",le="0.1"} 10000
http_request_duration_seconds_bucket{service="data-connector",le="0.5"} 14500
http_request_duration_seconds_bucket{service="data-connector",le="1"} 15000
http_request_duration_seconds_bucket{service="data-connector",le="5"} 15200
http_request_duration_seconds_bucket{service="data-connector",le="+Inf"} 15243

# Gauge: current value (e.g., active connections)
database_connections_active{service="data-connector",host="northwind-db-prod"} 42
```

**Business metrics** (custom, per service):

```
# data-connector service
data_sync_duration_seconds{customer_id="42",source="salesforce"} 125.4
data_sync_records_processed{customer_id="42",source="salesforce"} 5000
data_sync_errors_total{customer_id="42",source="salesforce",error_type="api_rate_limit"} 3

# notification-service
notifications_sent_total{channel="email",status="delivered"} 45000
notifications_sent_total{channel="email",status="failed"} 123
```

### 2.3 Distributed Traces

All inter-service requests traced via OpenTelemetry:

```
GET /v1/customers/42 (api-gateway)
  ├─ 100ms auth.validate-token
  ├─ 200ms data-connector.get-customer
  │   ├─ 50ms db.query("SELECT * FROM customers WHERE id=?")
  │   ├─ 100ms cache.set(key="customer:42", ttl=3600)
  │   └─ 50ms notification.enqueue(event="customer_fetched")
  ├─ 150ms insight-service.compute-analytics
  │   └─ 150ms db.query("SELECT * FROM analytics WHERE customer_id=?")
  └─ 550ms total
```

Each span includes:
- Service name
- Operation name
- Duration
- Status (success/error)
- Attributes (customer_id, request_id, etc.)
- Logs within span

## 3. Datadog Configuration

### 3.1 Agent Installation

Datadog Agent runs as a DaemonSet in Kubernetes:

```yaml
# kubernetes/daemonset-datadog-agent.yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: datadog-agent
  namespace: datadog
spec:
  template:
    spec:
      containers:
      - name: agent
        image: datadog/agent:7.50.0
        env:
        - name: DD_API_KEY
          valueFrom:
            secretKeyRef:
              name: datadog
              key: api-key
        - name: DD_SITE
          value: datadoghq.com
        - name: DD_ENV
          value: prod
        - name: DD_LOGS_ENABLED
          value: "true"
        - name: DD_APM_ENABLED
          value: "true"
        volumeMounts:
        - name: docker-socket
          mountPath: /var/run/docker.sock
        - name: proc
          mountPath: /host/proc
          readOnly: true
        - name: sys
          mountPath: /host/sys
          readOnly: true
```

### 3.2 Service Tags

All logs, metrics, and traces tagged consistently:

```
env:prod
service:data-connector
version:1.5.2
team:data-platform
cost_center:eng-5000
```

## 4. Required Dashboards

Each service must have a monitoring dashboard in Datadog:

### 4.1 Service Health Dashboard

```
Title: Data Connector — Service Health

Widgets:
1. Request Rate: http_requests_total by status (count)
2. Error Rate: % of requests with status 5xx (< 0.1% SLO)
3. Latency: p50, p95, p99 of http_request_duration_seconds (< 1s p99 SLO)
4. Database Connections: database_connections_active gauge (< 80 of 100 limit)
5. Cache Hit Rate: cache_hits / (cache_hits + cache_misses) (target > 80%)
6. Event Processing: data_sync_duration_seconds histogram (5 min, 1 hour, 24 hour windows)
```

### 4.2 Business Metrics Dashboard

```
Title: Data Connector — Business Impact

Widgets:
1. Records Synced: data_sync_records_processed (daily total)
2. Sync Success Rate: successful / (successful + failed) syncs
3. Average Sync Duration: data_sync_duration_seconds (p50, p95)
4. Customer Churn: New sources added vs. removed (daily delta)
5. Revenue Impact: ARR from active data sources
```

## 5. Alerting

### 5.1 Alert Thresholds

| Alert | Threshold | Severity | Action |
|-------|-----------|----------|--------|
| **Error rate spike** | 5x baseline for 5 min | Sev-2 | Page on-call engineer |
| **Latency degradation** | p99 > 2s for 10 min | Sev-2 | Page on-call engineer |
| **Database connections** | > 90 of 100 | Sev-3 | Slack alert; investigate |
| **API rate limit** | > 80% of quota | Sev-3 | Slack alert; plan scaling |
| **Service replica down** | < desired count for 5 min | Sev-2 | Page + auto-remediate (scale up) |
| **Disk usage** | > 85% on any node | Sev-3 | Slack alert; schedule cleanup |

### 5.2 Alert Configuration (Datadog UI or YAML)

```yaml
# monitoring/data-connector-alerts.yaml
monitors:
  - name: "Data Connector — Error Rate Spike"
    type: threshold
    query: "avg:trace.web.request.errors{service:data-connector} > 0.05"  # 5% error rate
    thresholds:
      critical: 0.05
      warning: 0.01
    evaluation_delay: 300  # Wait 5 min to reduce noise
    notify_list:
      - "@pagerduty-data-platform"
      - "@slack-#data-platform"
    tags: ["service:data-connector", "severity:sev-2"]

  - name: "Data Connector — Database Connection Pool"
    type: threshold
    query: "avg:postgresql.connections{service:data-connector}"
    thresholds:
      critical: 90  # 90% of 100
      warning: 75   # 75% of 100
    evaluation_delay: 60
    notify_list: ["@slack-#data-platform"]
    tags: ["service:data-connector"]
```

## 6. Observability Checklist for New Services

Before deploying a new service to production (see **Production Deployment Runbook**):

- [ ] **Structured logging** configured (JSON format, PII redacted)
- [ ] **Prometheus metrics** exposed on `:9090/metrics` (at least HTTP request metrics)
- [ ] **OpenTelemetry SDK** integrated (spans exported to Datadog APM)
- [ ] **Service dashboard** created in Datadog (at least 5 widgets showing health)
- [ ] **Alerts configured** for critical failures (error rate, latency, availability)
- [ ] **Sample requests** traced end-to-end (verified in Datadog APM)
- [ ] **SLOs documented** (RTO, RPO, uptime % target — see **SRE Error Budget Policy**)

## 7. Trace Sampling

To reduce costs while maintaining visibility:

```
# Sample 100% of errors, 10% of successful requests
if (span.error) then sample_rate = 1.0 else sample_rate = 0.1
```

Datadog's intelligent tail sampling helps identify issues in low-traffic services.

## 8. Runbook Integration

Datadog monitors link to runbooks for quick remediation:

```
Alert: "Data Connector — Sync Failures Elevated"
→ Runbook: https://wiki.northwind.com/runbooks/data-connector-sync-failures
  1. Check recent deployments (last 30 min)
  2. Verify external API health (Salesforce status page)
  3. Check database replication lag
  4. If lag > 1s, escalate to DBA team
```

## 9. Compliance and Data Retention

- **Logs**: Retained for 7 days (free tier); 30 days (enterprise)
- **Metrics**: Retained for 15 months
- **Traces**: Retained for 30 days (with tail sampling)
- **Restricted data**: Never stored in Datadog (see **Information Security Policy**); redact before sending

---

**Related policies:**
- See **SRE Error Budget Policy** for SLO/SLI definitions and incident response
- See **Production Deployment Runbook** for using dashboards during deployment validation
- See **Incident Response Runbook** for alert escalation and on-call procedures
- See **Secrets Management Standard** for credential handling in logs
