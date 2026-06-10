---
title: Customer Incident Communication Policy
doc_id: cs-incident-communication
owner: Customer Communications / Support
last_updated: 2026-06-09
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Customer Incident Communication Policy

## 1. Overview
This policy governs how Northwind Cloud communicates with customers during production incidents, data breaches, and critical service disruptions. The policy balances transparency with legal/regulatory requirements (GDPR, HIPAA) and brand protection.

## 2. Communication Escalation Framework

| Severity | Customers Notified | Timeline | Channel | Owner |
|---|---|---|---|---|
| **Sev-1** (outage >4h or data breach) | All affected + public status page | Within 30 min of incident declaration | Email + in-app banner + status page | VP Communications / VP Support |
| **Sev-2** (major feature broken) | All affected customers | Within 2 hours of diagnosis | Email + status page update | Support Manager |
| **Sev-3** (minor bug, workaround available) | Affected customers (email) | Within 8 hours | Status page (if multi-customer) or direct email | CSM |
| **Sev-4** (documentation/enhancement) | Not required | Standard support response timeline | Ticket only | Support agent |

---

## 3. Incident Notification Message

### 3.1 Initial Notification (First 30 Minutes)

**Structure:**
1. **Subject:** [INCIDENT] Northwind Cloud — [Brief description]
2. **Opening:** Acknowledge impact apologetically; state what we know (time, affected services).
3. **What to do:** Immediate action for customer (if any — e.g., "Please pause integrations pending update").
4. **Our response:** Team engaged, estimated resolution time, next update schedule.
5. **Status page link:** Direct to real-time updates (see Status Page Policy).

**Example (Sev-1 outage):**
```
Subject: [INCIDENT] Northwind Cloud — Data Integration Service Unavailable (Started 2026-06-09 14:45 UTC)

We're aware that Northwind Cloud's data integration service became unavailable at 2026-06-09 14:45 UTC affecting [X] customers. We sincerely apologize for the disruption.

WHAT WE KNOW:
- Integrations cannot be executed; pipelines queued but not processing.
- Root cause: Database connection pool exhaustion (investigating).

WHAT TO DO:
- Pause any critical integrations to avoid queue backup.
- Check status.northwindcloud.com for real-time updates.

OUR RESPONSE:
- Engineering team investigating; incident commander assigned.
- Expected update in 30 minutes.
- Will notify again if resolution delayed beyond 2 hours.

— Northwind Cloud Support
```

### 3.2 Status Updates (Every 4 Hours During Incident)

For Sev-1 lasting >4 hours, send status update every 4 hours with:
- Current status (still investigating, workaround identified, rollback in progress, resolved).
- % of traffic affected (if relevant).
- Next update ETA.

**Avoid:** Making false promises; estimated time should be conservative (better to resolve early than miss target).

### 3.3 Resolution Notification (Post-Incident)

**Sent within 1 hour of resolution:**
1. **Status:** Service fully restored.
2. **Root cause summary:** Brief explanation (not overly technical).
3. **What we did:** Steps taken to restore service.
4. **Follow-up:** Post-mortem scheduled; customer invited to participate (if Sev-1).
5. **Apology + compensation:** Offer credit/refund per RMA & Refund Policy, section 7 (if data loss or extended outage).

---

## 4. Data Breach & Security Incident Notification

### 4.1 Breach Confirmation & Legal Review

If a data breach is confirmed (PII, Confidential data exposed):

1. **Within 2 hours:** General Counsel + Chief Privacy Officer assess scope (which customers affected? which data classification?).
2. **Regulatory requirement check:**
   - **GDPR:** If EU customer PII exposed, must notify without undue delay (≤72 hours).
   - **HIPAA:** If health data exposed, notify affected individuals + HHS + media (if >500 records).
   - **State PII laws:** CA, NY, TX have specific timelines (typically 30 days).
   - **Customer DPA:** Some contracts require notification within 24 hours of discovery.

3. **In-house decision:** Notify all customers or only affected subset?
   - **All customers:** If breach involves fundamental platform security (e.g., encryption key compromised).
   - **Affected subset:** If breach limited to specific account(s) (e.g., one customer's data exposed).

### 4.2 Breach Notification Message

**Prepared by VP Communications + General Counsel; approved by CEO:**

```
Subject: IMPORTANT SECURITY NOTICE — Northwind Cloud Data Incident

Dear [Customer Name],

We are writing to inform you of a security incident that may have affected your data stored with Northwind Cloud. We take this matter very seriously and are committed to transparency and swift resolution.

WHAT HAPPENED:
On [date], our security team identified unauthorized access to [specific data category: e.g., "customer metadata" or "integration logs"]. We immediately isolated the affected systems and launched an investigation.

YOUR DATA:
- Data affected: [List specific data types, if applicable]
- Time exposed: Approximately [X hours/days]
- Exposure scope: [Your account / multiple accounts / all accounts]

IMMEDIATE ACTIONS WE'VE TAKEN:
- Revoked unauthorized access.
- Patched the vulnerability.
- Completed forensic investigation (details in attached report).
- Notified law enforcement [if applicable].

WHAT YOU SHOULD DO:
- Review the attached post-mortem for technical details.
- Rotate any credentials (API keys, database passwords) if applicable.
- Monitor your own systems for unauthorized activity.
- Contact us if you have questions: security@northwindcloud.com.

YOUR RIGHTS:
- If your personal information was exposed, you have the right to [credit monitoring / identity protection] at Northwind's expense.
- You may request a detailed breach report: [contact details].
- We're offering [credit / refund] as detailed below.

REGULATORY COMPLIANCE:
- This incident has been reported to relevant regulators as required.
- Notified: [List agencies, e.g., "GDPR – Irish DPA", "HIPAA – HHS" if applicable].

COMPENSATION:
- [3 months free service / $X credit / refund decision].
- We're committed to regaining your trust.

— Northwind Cloud Security Team
```

### 4.3 Customer Notification Timeline

| Trigger | Timeline | Audience | Method |
|---|---|---|---|
| Data breach confirmed (PII exposed) | ≤24 hours (internal law/security review) | All affected customers | Email + phone call for Top 10 accounts |
| Regulatory notification due | Per GDPR (≤72h), HIPAA (30 days), state law | Relevant authorities + customers | Email + formal notification letter |
| Customer requests copies | ≤30 days after request | Individual customer | Encrypted email or secure portal |

---

## 5. Communication Channels

1. **Email:** Primary channel for all incident notifications; use security@northwindcloud.com or specific CSM.
2. **In-app banner:** Northwind Cloud UI displays incident notice for all logged-in users.
3. **Status page:** (See Status Page Policy) Real-time incident tracking; customers can subscribe for updates.
4. **Phone:** VP Communications calls Top 10 affected customers for Sev-1 (optional; VP Support decides).
5. **Twitter / public channels:** VP Communications posts brief status updates only for widespread outages (Sev-1 lasting >4h); avoids detailed technical discussion.

---

## 6. Post-Incident Communication

### 6.1 Post-Mortem Report (Within 5 Business Days)

For Sev-1 incidents, VP Engineering publishes post-mortem:
- **Root cause:** What failed?
- **Timeline:** When did it start? Detected? Resolved?
- **Impact:** How many customers affected? How long? Data loss?
- **Why it happened:** Architecture gap? Operational oversight? Code bug?
- **Preventive measures:** What we're changing to prevent recurrence.
- **Timeline for changes:** When will they be deployed?

**Customer invitation:** Offer to present post-mortem in a webinar or 1-on-1 call (especially for Enterprise tier).

### 6.2 Refund / Credit Decision (Within 10 Business Days)

CSM + VP Customer Success determine compensation per RMA & Refund Policy, section 7:
- **Data loss incident:** Full month refund + 3 months credit.
- **Extended outage (>8h):** 10–20% monthly fee credit.
- **Minor incident:** No credit or 5% courtesy credit.

**Customer receives notification** with credit confirmation + expected application date.

---

## 7. Legal & Compliance Guardrails

1. **Do not speculate** on root cause before engineering confirms.
2. **Do not disclose security details** (vulnerability name, code paths, exploit method) publicly; save for post-mortem.
3. **Do not offer unlimited compensation** without CFO + General Counsel approval (see section 4.2 template for pre-approved language).
4. **Do not delay breach notification** to finish investigation; notify by legal deadline, then provide updates as details emerge.
5. **Document all communications:** Archive email/status page posts; log in incident record for audit trail (GDPR, HIPAA, SOC 2).

---

## 8. Training & Escalation

**VP Communications + VP Support own this policy.** All Support Managers and CSMs receive annual training:
- Identifying seriousness of incidents (when to escalate to Communications).
- Drafting professional incident messages (templates provided).
- Regulatory timelines (GDPR, HIPAA, state laws) for common scenarios.
- Escalation: If Support Manager unsure whether to notify customers, escalate to VP Support immediately (better to over-communicate than under-communicate).

---

## 9. Integration with Other Policies

- **Status Page Policy:** See Status Page Policy for real-time incident tracking and customer subscriptions.
- **Support SLA & Tiers:** Sev-1 RTO is 4 hours per company bible; customer notification within 30 minutes of incident declaration.
- **Incident Response Runbook:** See On-Call & Escalation Policy for incident declaration, escalation, and command structure.
