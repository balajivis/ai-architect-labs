---
title: Service Catalog
doc_id: eng-service-catalog
owner: Platform Engineering
last_updated: 2026-06-01
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Service Catalog

## 1. Purpose and Governance

The Service Catalog is the single source of truth for all backend services, their owners, runtime dependencies, and deployment targets. All services must be registered here. Service changes (new service, owner change, retirement) require PR approval from VP Engineering.

## 2. Service Inventory

### 2.1 Core Platform Services

**api-gateway**
- **Owner**: Platform Engineering
- **Language**: Go 1.21
- **Repository**: `github.com/northwind/api-gateway`
- **Deployment**: AWS EKS cluster `northwind-prod-east`
- **Database**: None (state-free)
- **External dependencies**: Okta SSO, Datadog, Auth0 for token validation
- **SLO**: 99.9% uptime, p99 latency < 100ms
- **Incident response**: See **On-Call & Escalation Policy**

**data-connector**
- **Owner**: Data Platform team
- **Language**: Python 3.11
- **Repository**: `github.com/northwind/data-connector`
- **Deployment**: AWS EKS cluster `northwind-prod-east`
- **Database**: PostgreSQL schema `connector_*` (managed RDS)
- **External dependencies**: Customer data sources (SQL Server, PostgreSQL, Salesforce API, Google Sheets), RabbitMQ
- **SLO**: 99.5% uptime (background job; not customer-blocking)
- **Configuration**: See **Container & Kubernetes Standards** for resource limits

**transformation-engine**
- **Owner**: Data Platform team
- **Language**: Java 17
- **Repository**: `github.com/northwind/transformation-engine`
- **Deployment**: AWS EKS cluster `northwind-prod-east`
- **Database**: PostgreSQL schema `transform_*`
- **External dependencies**: RabbitMQ, Kafka (audit event sink), data-connector
- **SLO**: 99.0% uptime (background processing)
- **Build tool**: Maven 3.8; JAR deployed to ECR

**insight-service**
- **Owner**: Analytics team
- **Language**: Node.js 20 (TypeScript)
- **Repository**: `github.com/northwind/insight-service`
- **Deployment**: AWS EKS cluster `northwind-prod-west`
- **Database**: PostgreSQL schema `analytics_*` + Redis cache
- **External dependencies**: data-connector, Datadog, ClickHouse (time-series analytics)
- **SLO**: 99.5% uptime, p99 latency < 500ms
- **Observability**: See **Observability & Monitoring Standards** for custom dashboard requirements

**notification-service**
- **Owner**: Platform Engineering
- **Language**: Python 3.11
- **Repository**: `github.com/northwind/notification-service`
- **Deployment**: AWS EKS cluster `northwind-prod-east`
- **Database**: PostgreSQL schema `notifications_*`
- **External dependencies**: SendGrid (email), Slack API, RabbitMQ consumer
- **SLO**: 98% uptime (non-critical path; best-effort delivery)
- **Message retention**: RabbitMQ dead-letter queue kept for 7 days for debugging

**audit-service**
- **Owner**: Security & Compliance team
- **Language**: Go 1.21
- **Repository**: `github.com/northwind/audit-service`
- **Deployment**: Azure AKS cluster `northwind-prod-audit`
- **Database**: PostgreSQL schema `audit_*` (immutable append-only table)
- **External dependencies**: Kafka audit topic, Splunk (log sink for compliance)
- **SLO**: 99.99% uptime (critical for SOX/GDPR compliance)
- **Compliance requirement**: All data changes logged per **Information Security Policy**

### 2.2 Supporting Services (Internal Use)

**config-service** (deprecated)
- **Status**: Superseded by environment variables + Kubernetes ConfigMaps
- **Retirement date**: 2026-09-01
- **Migration path**: See **Infrastructure as Code Standards** section on ConfigMap usage

## 3. Service Dependencies and Topology

```
┌─────────────────┐
│  api-gateway    │  (HTTP entry point)
└────────┬────────┘
         │
    ┌────┴────┬──────────────────────┐
    │         │                      │
    ▼         ▼                      ▼
┌─────────────┐  ┌──────────────┐  ┌──────────────┐
│data-connector│  │insight-service│  │notification │
└──────┬──────┘  └────────┬──────┘  └──────────────┘
       │                  │
       └──────────────────┴─────┐
                                │
                        ┌───────▼─────────┐
                        │transformation   │
                        │engine           │
                        └───────┬─────────┘
                                │
                        ┌───────▼──────┐
                        │audit-service │
                        └──────────────┘
```

## 4. Deployment Lifecycle

All services follow the same deployment cycle:

1. **Code commit** → GitHub (branch: `feature/*`, `bugfix/*`)
2. **Pull request** → 2 approvals required (see **Code Review Standards**)
3. **CI pipeline** → GitHub Actions (unit tests, lint, security scan via **Secrets Management Standard**)
4. **Merge to main** → Auto-deploy to staging
5. **Staging validation** → 8-hour manual test window (see **Production Deployment Runbook**)
6. **Production deploy** → Manual trigger; requires on-call engineer monitoring (see **On-Call & Escalation Policy**)

## 5. Shared Infrastructure

All services depend on:

| Component | Endpoint | Managed by | SLA |
|-----------|----------|-----------|-----|
| PostgreSQL | `northwind-db.postgres.database.azure.com` | DBA team (Azure Database) | 99.95% |
| RabbitMQ | `mq.internal.northwind.com:5672` | Platform Engineering | 99.9% |
| Redis | `cache.internal.northwind.com:6379` | Platform Engineering | 99.5% |
| Datadog | `api.datadoghq.com` | Monitoring team | 99.9% |

For access to shared infrastructure, see **Secrets Management Standard**.

## 6. Adding a New Service

To onboard a new microservice:

1. **Create GitHub repository** under `github.com/northwind/`
2. **Set up CI/CD pipeline** (GitHub Actions template in `templates/github-actions.yml`)
3. **Define database schema** and register in `databases.sql` (see **Database Change Management**)
4. **Add to this catalog** via PR (PR template requires VP Engineering approval)
5. **Configure Kubernetes manifests** (Helm chart; see **Container & Kubernetes Standards**)
6. **Deploy to staging** and run smoke tests (see **Production Deployment Runbook**)

Typical onboarding: 2–3 days.

## 7. Service Retirement

To retire a service:

1. Verify **no active dependencies** (check call graph in Datadog APM)
2. **Migrate data** to new service (provide 30-day transition period)
3. **Notify customers** if applicable (via support, with 2-week notice)
4. **Scale down to 1 replica** for 2 weeks, then delete (provides rollback window)
5. **Archive repository** (do not delete; retain for audit trail; see **Incident Response Runbook**)

---

**Related policies:**
- See **Container & Kubernetes Standards** for resource requests and deployment configs
- See **Code Review Standards** for approval requirements
- See **Infrastructure as Code Standards** for Terraform and Helm patterns
