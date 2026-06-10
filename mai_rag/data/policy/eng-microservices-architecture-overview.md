---
title: Microservices Architecture Overview
doc_id: eng-microservices-architecture-overview
owner: VP Engineering
last_updated: 2026-06-01
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Microservices Architecture Overview

## 1. Architecture Principles

Northwind Cloud is built on a microservices architecture deployed on AWS and Azure. Each service is:

1. **Independently deployable** – Services are deployed via CI/CD pipelines; see **GitHub Actions CI/CD Pipeline Guide** for automation details
2. **Database-per-service** – Each service owns its PostgreSQL schema; no direct database access between services
3. **Synchronous & asynchronous communication** – REST APIs for request-response; RabbitMQ for event-driven workflows
4. **Observable** – All services report to Datadog (see **Observability & Monitoring Standards**)
5. **Containerized** – Docker containers orchestrated via Kubernetes (EKS on AWS, AKS on Azure)

## 2. Core Services (Current Topology)

| Service | Language | Purpose | AWS/Azure | Replicas |
|---------|----------|---------|-----------|----------|
| **api-gateway** | Go | HTTP entry point, routing, auth validation | AWS EKS | 5 |
| **data-connector** | Python | Integrates customer data sources (SQL, Salesforce, etc.) | AWS EKS | 3 |
| **transformation-engine** | Java | Applies ETL rules, transformations, scheduling | AWS EKS | 4 |
| **insight-service** | Node.js | Analytics, dashboards, aggregations | AWS EKS | 2 |
| **notification-service** | Python | Email, Slack, webhook delivery | AWS EKS | 2 |
| **audit-service** | Go | Logs all data changes for compliance | Azure AKS | 2 |

## 3. Service Communication Patterns

### 3.1 Synchronous (REST / gRPC)

- **api-gateway** ↔ **data-connector**: "Fetch available sources" (request-response)
- **insight-service** → **data-connector**: "Get latest data snapshot"
- Timeout: 30 seconds; retry on transient failure (exponential backoff)

### 3.2 Asynchronous (Event-Driven)

- **data-connector** publishes `DataSourceConnected` event → RabbitMQ topic `datasource.events`
- **notification-service** subscribes and sends alert email
- **audit-service** subscribes and logs for compliance (see **Secrets Management Standard** for audit data handling)

### 3.3 Resilience

- **Circuit breaker**: If downstream service is unhealthy, circuit opens after 5 consecutive failures
- **Bulkhead isolation**: Each service has its own thread pool; never blocks other services
- **Graceful degradation**: Notification failures do not block transformation completion

## 4. Data Model & Ownership

Each service owns its PostgreSQL schema:

```
├── api-gateway     → db.northwind.gateway_*
├── data-connector  → db.northwind.connector_*
├── transformation  → db.northwind.transform_*
├── insight-service → db.northwind.analytics_*
├── notification    → db.northwind.notifications_*
└── audit-service   → db.northwind.audit_*
```

**Cross-service data access**: Event-driven only. No direct joins across schemas.

## 5. Deployment Model

Microservices are deployed to Kubernetes clusters with auto-scaling:

- **Horizontal Pod Autoscaling (HPA)**: CPU > 70% → scale up; CPU < 30% for 2 min → scale down
- **Rolling updates**: New version deployed to 1 pod, monitored for 2 minutes, then to remaining pods
- **Resource requests**: Each service declares CPU/memory minimum (enforced by Kubernetes); see **Container & Kubernetes Standards**

## 6. Service Mesh (Istio)

All inter-pod communication is managed by Istio service mesh:

- **Traffic routing**: VirtualServices control canary deployments and traffic splitting
- **Circuit breaking**: Istio enforces configured timeouts and retry policies
- **mTLS**: Pod-to-pod encryption automatically enabled (certificate rotation every 30 days)

For detailed networking policies, see **Container & Kubernetes Standards**.

## 7. External Service Dependencies

- **PostgreSQL** (managed) – Connection pooling via PgBouncer; 100 max connections per service
- **RabbitMQ** (managed) – Multi-region replication; persistent queues
- **Redis** (managed) – Cache for session tokens and transformation results (TTL: 1 hour)
- **Azure Cognitive Services** – Callouts for sentiment analysis (fallback to local ML if API fails)

## 8. Monitoring and Observability

All services emit:
- **Structured logs** (JSON) to stdout; Datadog parses and indexes
- **Prometheus metrics** exposed on `:9090/metrics`
- **Distributed traces** (OpenTelemetry) to Datadog APM for end-to-end request tracing

See **Observability & Monitoring Standards** for alert configuration and dashboard requirements.

## 9. Common Pitfalls and Solutions

| Pitfall | Root Cause | Solution |
|---------|-----------|----------|
| **Cascading failures** | One slow service blocks others | Use bulkhead isolation + circuit breaker (Istio) |
| **Data inconsistency** | Async events delayed/lost | Implement idempotent handlers + retry with exponential backoff |
| **Silent failures** | No monitoring of event subscriptions | Datadog monitors dead-letter queue depth; Sev-3 alert if > 100 messages |

---

**Related policies:**
- See **GitHub Actions CI/CD Pipeline Guide** for how services are deployed
- See **Observability & Monitoring Standards** for metric collection and alerting
- See **Container & Kubernetes Standards** for networking and resource limits
