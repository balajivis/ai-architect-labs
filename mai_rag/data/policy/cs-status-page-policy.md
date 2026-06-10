---
title: Status Page Policy
doc_id: cs-status-page-policy
owner: Customer Communications / Operations
last_updated: 2026-06-09
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Status Page Policy

## 1. Overview
Northwind Cloud maintains a public status page (status.northwindcloud.com) showing real-time system health, ongoing incidents, and maintenance windows. This policy governs status page updates, customer communication, and incident transparency.

## 2. Status Page Components

### 2.1 System Status Display

**Service components tracked:**

| Component | Description | Criticality | Monitored By |
|---|---|---|---|
| **Data Integration Service** | Core pipeline execution, transformation logic | Critical | DevOps + Datadog |
| **Auth & SSO** | Okta integration, user login, session management | Critical | DevOps + Datadog |
| **API Gateway** | REST endpoints, customer integrations | Critical | DevOps + Datadog |
| **UI / Dashboard** | Customer-facing web app | High | DevOps + Datadog |
| **Data Storage (AWS)** | S3, RDS, data warehouse | Critical | AWS CloudWatch + DevOps |
| **Observability** | Datadog monitoring, alerting dashboard | High | Datadog SLA |

**Status indicators:**

- **🟢 Operational:** Service running normally; <0.1% error rate.
- **🟡 Degraded Performance:** Latency elevated; requests slower than baseline but not failing.
- **🔴 Partial Outage:** Some users/regions affected; service partially unavailable.
- **🔴 Major Outage:** Service completely unavailable for all users.
- **⚪ Maintenance:** Scheduled maintenance in progress; service temporarily unavailable (announced ≥72h in advance).

### 2.2 Incident Tracking

Each incident published to status page includes:
- **Title:** Brief description (e.g., "Data Integration Delays").
- **Severity:** Sev-1, Sev-2, Sev-3, Sev-4 (aligned with Support SLA & Tiers).
- **Start time:** When incident began.
- **Updates:** Chronological updates every 30–60 minutes during incident.
- **Resolution time:** When incident resolved + root cause summary (once available).

**Example:**
```
🔴 MAJOR OUTAGE: Data Integration Service
Started: 2026-06-09 14:45 UTC

14:45 — Service became unavailable; pipelines not executing.
15:15 — Engineering investigating database connection issues.
15:45 — Identified connection pool exhaustion; rollback in progress.
16:15 — Service restored; monitoring for stability.
16:30 — Incident resolved; post-mortem scheduled.

Root Cause: Query optimization regression in recent deployment.
Resolution: Reverted deployment; fix being re-tested.
Impact: 2.5 hours downtime; 45 customers affected.
```

### 2.3 Maintenance Windows

Scheduled maintenance announced on status page ≥72 hours before:

- **Title:** "Scheduled Maintenance — Database Migration".
- **Planned impact:** Downtime expected 2–3 hours; read-only access available.
- **Start/end time:** Precise UTC times.
- **Why:** Brief explanation (scaling, security patch, infrastructure upgrade).
- **Contact:** Support email if customer questions.

---

## 3. Incident Status Page Updates

### 3.1 Timing & Frequency

| Phase | Frequency | Owner | Content |
|---|---|---|---|
| **Detection** | Immediate (<5 min) | Incident commander | "Investigating [service]" posted |
| **Investigation** | Every 30 min | VP Support / VP Ops | Progress update; estimated resolution time |
| **Resolution** | Upon completion | Incident commander | Service restored; monitoring for stability |
| **Post-incident** | 1–5 business days | VP Engineering | Root cause + post-mortem summary |

### 3.2 Status Page Update Responsibility

1. **Incident commander (on-call)** declares incident and posts initial message to status page.
2. **VP Support** updates status page every 30 minutes during active incident.
3. **VP Engineering** provides technical details for post-mortem update.
4. **VP Communications** reviews all updates for tone and clarity before posting (optional for technical updates; required for public-facing communication if brand risk exists).

### 3.3 Update Language

**Tone:** Professional, empathetic, transparent; avoid jargon customers won't understand.

**What to include:**
- What's affected (specific components, customer count, scope).
- What we know (root cause hypothesis, not confirmed details yet).
- What we're doing (investigation steps, remediation in progress).
- ETA (realistic estimate; better to be conservative).

**What NOT to include:**
- Blame (don't say "engineer made mistake"; say "configuration error").
- Unconfirmed root causes (wait until engineering confirms).
- Internal details (AWS account IDs, IP addresses, security group names).
- Speculation ("might be" or "probably"—state only what's confirmed).

**Example update:**
```
16:45 UTC — We're seeing continued elevated latency in the Data Integration Service. Our team has identified the root cause as a database query inefficiency introduced in a recent deployment. We're testing a rollback now and expect to have an update in 30 minutes.
```

---

## 4. Customer Notification Integration

**Status page updates feed customer communications** (see Customer Incident Communication Policy, section 3):

1. When status page changes to 🔴 (Major Outage), VP Communications automatically sends email to all affected customers (within 30 minutes).
2. When status page updates every 30 minutes, email subscribers receive notification (optional; customers can control subscription frequency).
3. When incident resolved, status page shows "Resolved" + root cause summary; final email sent to subscribers.

**Customers can subscribe** to status page updates via email or SMS (Statuspage.io features).

---

## 5. Maintenance Window Policy

### 5.1 Scheduling & Announcement

**Maintenance criteria:**
- Must not be during peak hours (7a–7p US Central, Monday–Friday).
- Prefer: Tuesday–Thursday 3a–6a UTC (off-peak for global customers).
- Must announce ≥72 hours in advance on status page.
- Enterprise customers (Level 1/2 support) notified via email + direct CSM call 48 hours before.

**Announcement includes:**
- Expected downtime duration (accurate within 30 minutes).
- What's being done (infrastructure upgrade, data migration, security patch).
- Impact: Is data accessible during maintenance? Can integrations be queued?

### 5.2 Maintenance Execution

1. **2 hours before:** Incident commander posts "Maintenance starting in 2 hours" to status page.
2. **During maintenance:** Status page shows 🟡 (Degraded) or ⚪ (Maintenance); updates every 30 minutes.
3. **At resolution:** Post message "Maintenance complete" + actual downtime duration.
4. **Post-mortem (if issues arose during maintenance):** Published within 2 business days.

### 5.3 Maintenance Cancellation

If maintenance is cancelled or delayed:
1. Update status page within 30 minutes.
2. If email subscription customers were notified, send cancellation notice.
3. Reschedule (if applicable) with same 72-hour advance notice.

---

## 6. Post-Incident Reporting

### 6.1 Post-Mortem Summary (Within 5 Business Days)

Post-mortem includes:
- **Root cause:** Technical explanation of what failed.
- **Timeline:** Detected at [time], resolved at [time] = [duration].
- **Impact:** X customers, Y% of traffic, Z hours downtime.
- **Why it happened:** Architecture gap? Human error? External factor?
- **Preventive measures:** Changes being made to prevent recurrence.
- **Timeline for fixes:** When will changes deploy?

**Posted to status page** under resolved incident; customers invited to webinar or 1-on-1 discussion.

### 6.2 Customer Webinar (Optional, for Sev-1)

VP Engineering hosts optional customer webinar 1–2 weeks post-incident:
- Detailed technical walkthrough.
- Q&A with customers.
- Prevents rumors; shows transparency + competence.

---

## 7. Uptime Metrics & Reporting

### 7.1 SLA Uptime Calculation

Status page tracks monthly uptime % per component:

```
Uptime % = (Total minutes in month - Downtime minutes) / Total minutes in month × 100%
```

**Downtime includes:**
- Unplanned outages (Sev-1, Sev-2).
- Excludes announced maintenance windows.
- Excludes customer misconfiguration or third-party outages (AWS, Okta).

### 7.2 Public Reporting

**Monthly:** VP Operations publishes uptime report on status page (e.g., "May 2026: 99.92% uptime").

**Quarterly:** Finance provides uptime data to CFO for customer communication + pricing adjustments (if uptime <SLA, eligible customers receive credit per Support SLA & Tiers, section 4).

---

## 8. Third-Party Dependency Transparency

If Northwind Cloud depends on third-party services (AWS, Okta, Datadog) and they experience outages:

1. **Assess customer impact:** Does third-party outage directly prevent Northwind Cloud customers from using our service?
   - YES (e.g., Okta down, customers can't log in) → Post to status page; notify customers.
   - NO (e.g., AWS account dashboard is slow, but Northwind Cloud service unaffected) → No customer notification needed.

2. **Provide workaround context:** If Okta is down but Northwind Cloud has internal fallback auth → Communicate this to customers.

3. **Link to third-party status page:** Post link to AWS Status or Okta Status for customer reference.

---

## 9. Integration with Incident Response

- **Incident Response Runbook:** See Incident Response Runbook for escalation + incident commander responsibilities.
- **On-Call & Escalation Policy:** Incident commander (on-call) responsible for declaring incident + initial status page post.
- **Customer Incident Communication Policy:** Status page updates automatically trigger customer email notifications (see section 4).

---

## 10. Tooling & Administration

**Status Page Platform:** Statuspage.io (or self-hosted equivalent).

**Admin team:**
- VP Communications (owns escalation language, brand messaging).
- VP Operations (owns technical updates, incident commander coordination).
- DevOps (owns Datadog integration, automated alerts to status page).

**Escalation:** If status page becomes inaccurate or outdated, VP Support escalates to VP Operations within 30 minutes for correction.
