---
title: ADR (Architecture Decision Record) Process
doc_id: eng-adr-architecture-decision-record-process
owner: VP Engineering
last_updated: 2026-06-01
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# ADR (Architecture Decision Record) Process

## 1. Overview

An Architecture Decision Record (ADR) documents significant architectural or technical decisions made at Northwind. ADRs are living documents that explain the "why" behind design choices, providing future developers context for understanding how the system works.

## 2. When to Write an ADR

Write an ADR for **any architectural decision** that affects:

- **Multiple services** (see **Service Catalog**)
- **System behavior or performance** (latency, scaling, reliability)
- **Long-term maintenance burden** (language choice, framework upgrade, library selection)
- **Security or compliance** (authentication method, encryption strategy, data storage)
- **Development velocity** (tooling, build process, deployment pipeline)

**Examples**:
- ✅ "Use async message queue (RabbitMQ) for event-driven workflow"
- ✅ "Adopt TypeScript for all new services (stricter typing, IDE support)"
- ✅ "Switch from MySQL to PostgreSQL for relational features"
- ✅ "Implement service mesh (Istio) for observability"
- ❌ "Add npm package X to dependencies" (use package.json comment instead)

## 3. ADR Format

All ADRs follow the Nygard template:

```markdown
# ADR-001: Use PostgreSQL for Primary Datastore

## Status
Accepted (as of 2026-01-15)

## Context
Northwind's current data model has many relational queries across customers,
orders, and products. MySQL limitations on complex joins and transactions
have caused performance issues in the transformation-engine service.

## Decision
We will migrate from MySQL 5.7 to PostgreSQL 15 as our primary relational
datastore.

## Rationale
1. **Superior JSON support**: PostgreSQL's JSONB type allows semi-structured data
   without additional key-value store
2. **Better transaction model**: MVCC provides better concurrency than MySQL's
   locking strategy
3. **Team expertise**: Our DBA has 8 years PostgreSQL experience
4. **Ecosystem**: Excellent integration with Node.js and Go via standard libraries

## Consequences
### Positive
- ✅ Eliminates N+1 query problems (better join optimization)
- ✅ Reduces infrastructure complexity (one database instead of MySQL + Redis)
- ✅ Improves compliance (better audit logging via WAL)

### Negative
- ❌ Requires database migration (40 GB; 8-hour downtime estimated)
- ❌ MySQL-specific syntax in 200 queries must be rewritten
- ❌ DBA team needs PostgreSQL tools training (2-day course)

## Alternatives Considered
1. **Keep MySQL**: Rejected due to JSON limitations
2. **Use MongoDB**: Rejected; our data is relational, not document-oriented
3. **Use multi-database approach** (PostgreSQL + MongoDB): Rejected due to
   operational complexity; maintain one source of truth

## Implementation Plan
1. Provision PostgreSQL 15 cluster in staging (January 2026)
2. Migrate schema and data (February 2026)
3. Rewrite 200 MySQL-specific queries (March 2026)
4. Run parallel-write testing (April 2026) — write to both MySQL + PostgreSQL
5. Production cutover (May 2026)
6. Decommission MySQL (June 2026)

## Related ADRs
- ADR-003: Use Kubernetes for orchestration
- ADR-008: Service mesh strategy

## Decision Made By
VP Engineering (approval from CEO, CTO)

## Date Accepted
2026-01-15

## Last Updated
2026-01-15
```

## 4. ADR Lifecycle

### 4.1 States

| State | Meaning | Action |
|-------|---------|--------|
| **Proposed** | Under discussion; not yet decided | Share draft in PR for comments |
| **Accepted** | Decision made; approved by leadership | Implement or in progress |
| **Superseded** | Replaced by newer ADR | Link to superseding ADR |
| **Deprecated** | No longer recommended but still used | Flag for future cleanup |
| **Rejected** | Decision made not to do something | Document why rejected |

### 4.2 Approval Process

1. **Author drafts**: Engineer writes ADR in markdown
2. **Spike/Investigation**: If uncertain, conduct brief technical investigation (1–2 days)
3. **Informal review**: Share in #engineering Slack; get feedback from team
4. **Formal review**: Open PR against `adr/` folder in `infrastructure` repo
5. **VP Engineering approval**: ADR merged only after VP signs off
6. **Implementation**: Team executes; references ADR in pull requests
7. **Follow-up**: Update ADR if implementation reveals new info

## 5. ADR Repository

All ADRs stored in `github.com/northwind/infrastructure/docs/adr/`:

```
docs/adr/
├── README.md (index of all ADRs)
├── adr-001-postgresql-datastore.md
├── adr-002-istio-service-mesh.md
├── adr-003-typescript-standards.md
├── adr-004-kubernetes-orchestration.md
├── adr-005-event-driven-asyncapi.md
├── adr-006-microservices-no-monolith.md
├── adr-007-api-versioning-path-based.md
├── adr-008-datadog-observability.md
├── adr-009-kubernetes-secrets-sealed.md
└── adr-010-cicd-github-actions.md
```

**README.md** (index):
```markdown
# Architecture Decision Records (ADRs)

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| 001 | Use PostgreSQL for Primary Datastore | Accepted | 2026-01-15 |
| 002 | Adopt Istio Service Mesh | Accepted | 2026-02-01 |
| 003 | TypeScript Strict Mode for New Services | Accepted | 2026-02-15 |
| 004 | Kubernetes as Orchestration Platform | Accepted | 2025-06-01 |
| ... | | | |
```

## 6. ADR in Code Review

When reviewing PRs, reference relevant ADRs:

```
PR #456: Add new validation library

Reviewer comment:
"This library adds JSON schema validation. Great choice!
Note: Per ADR-005 (Event-Driven Architecture), validation
should happen at message boundary, not in consumer.
See section 'Validation Pattern' for example.
✓ LGTM"
```

See **Code Review Standards** for full code review process.

## 7. ADR Examples

### Example 1: Service Mesh Decision

```markdown
# ADR-002: Adopt Istio for Service-to-Service Communication

## Status
Accepted (2026-02-01)

## Context
Currently, microservices communicate via REST with retry logic in client code.
Different services implement circuit breakers, timeouts, and retries differently,
leading to inconsistent behavior. Debugging cross-service failures is difficult.

## Decision
Adopt Istio as the service mesh. All inter-pod traffic (except to external APIs)
routed through Istio sidecar proxies.

## Rationale
- **Centralized observability**: All RPC metrics in Datadog without code changes
- **Consistent timeouts/retries**: Configured via VirtualService, not code
- **Traffic splitting**: Canary deployments and A/B testing via mesh, not application
- **mTLS by default**: Pod-to-pod encryption automatic

## Consequences
### Positive
- ✅ Reduced code complexity (no retry loops in application code)
- ✅ Better observability (Datadog shows all microservice dependencies)
- ✅ Easier troubleshooting (sidecar logs show where latency occurs)

### Negative
- ❌ Learning curve for team (Istio has steep learning curve)
- ❌ Extra latency (sidecar proxy adds ~5ms per RPC)
- ❌ Resource overhead (sidecar per pod; extra CPU/memory)

## Alternatives Considered
1. **Keep existing approach**: Rejected; inconsistency grows with more services
2. **Use Linkerd**: Smaller footprint; rejected because Datadog integration better with Istio
3. **Implement in client libraries**: Rejected; code duplication across services

## Implementation Plan
1. Deploy Istio to staging cluster (February 2026)
2. Configure first service (api-gateway) with Istio (March 2026)
3. Migrate other services one-by-one (April–June 2026)
4. Remove client-side retry logic once all services on mesh (July 2026)

## Related ADRs
- ADR-001: Use PostgreSQL (separate concern; but Istio improves observability of DB calls)
- ADR-004: Kubernetes Orchestration (Istio runs on K8s)

## Decision Made By
VP Engineering + Platform Engineering Lead
```

### Example 2: Rejected Decision

```markdown
# ADR-999: Add GraphQL Gateway (REJECTED)

## Status
Rejected (2026-03-01)

## Context
Some customers request GraphQL API for flexibility in queries.
Currently REST API forces N+1 queries for related data.

## Decision (Not Made)
We rejected adding GraphQL layer for now.

## Rationale for Rejection
1. **REST API sufficient**: Current REST API supports all use cases; N+1 avoided via query parameters
2. **Operational complexity**: GraphQL requires new validation layer, performance tuning
3. **Team unfamiliar**: No team experience with GraphQL; would require hiring/training
4. **API versioning complexity**: GraphQL makes versioning harder (vs. path-based /v1/, /v2/)

## Revisit Condition
Revisit if:
- Customer demand increases (> 3 requests/year)
- Team hires GraphQL expert
- Query complexity genuinely prevents REST from working

## Related ADRs
- ADR-007: API Versioning (REST path-based; GraphQL would complicate this)
```

## 8. Superseding an ADR

If an ADR is superseded by a newer decision:

```markdown
# ADR-003: TypeScript Strict Mode (SUPERSEDED)

## Status
Superseded by ADR-011 (2026-05-01)

...
[original content]

## Superseded By
ADR-011: Adopt TypeScript 5.0 with Strict+ Type Checking

Rationale: TypeScript 5.0's improved type inference makes strict mode
less burdensome; recommend strict+ for new services.
```

## 9. Decision Log

Track decisions by team in Slack:

```
#engineering:
📋 New ADR Proposed

ADR-012: Switch logging from Pino to structured console
Status: Proposed
PR: github.com/northwind/infrastructure/pull/456
Discussion: [Slack thread link]
Decision deadline: 2026-06-15

Please review and comment! 👇
```

## 10. ADR Metrics

Monthly, VP Engineering reports ADR health:

| Metric | Healthy | Current |
|--------|---------|---------|
| ADRs written per quarter | ≥ 4 | 5 ✓ |
| ADRs superseded per year | < 3 | 2 ✓ |
| Time from proposal to acceptance | < 2 weeks | 10 days ✓ |
| Team familiarity with ADRs | > 80% | 75% |

---

**Related policies:**
- See **Code Review Standards** for referencing ADRs in PR comments
- See **Microservices Architecture Overview** for architectural decisions already made
- See **Git Branching & Release Strategy** for ADR versioning alongside product releases
