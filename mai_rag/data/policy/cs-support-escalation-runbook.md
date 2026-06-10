---
title: Support Escalation Runbook
doc_id: cs-support-escalation-runbook
owner: Customer Support
last_updated: 2026-06-09
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Support Escalation Runbook

## 1. Overview
This runbook complements Support SLA & Tiers by defining the escalation path for complex or high-impact issues. Support team uses this runbook when initial diagnosis fails or issue severity is unclear.

## 2. Escalation Decision Tree

### 2.1 Severity Triage (First 15 Minutes)

**Support agent receives ticket → Assess severity using criteria below:**

1. **Is production down for customer's end-users?**
   - YES → **Sev-1** → Go to section 3.1
   - NO → Continue to 2.2

2. **Is customer's data missing, corrupted, or at risk of loss?**
   - YES → **Sev-1** → Go to section 3.1
   - NO → Continue to 2.2

3. **Is customer reporting a security or data breach?**
   - YES → **Sev-1** → Go to section 3.2 (Security escalation)
   - NO → Continue to 2.2

### 2.2 Feature/Functionality Triage

1. **Is a core feature (data integration, pipeline execution, user auth) broken or unusable?**
   - YES (impacts multiple customers or revenue-critical) → **Sev-2** → Go to section 3.3
   - YES (single customer, has workaround) → **Sev-3** → Go to section 3.4
   - NO → Continue to 2.3

2. **Is performance degradation >50% vs. baseline?**
   - YES → **Sev-2** → Go to section 3.3
   - NO → Likely Sev-3 or Sev-4

### 2.3 Documentation & Enhancement Triage

1. **Does ticket contain a feature request or "how-to" question?**
   - YES → **Sev-4** → Respond within SLA; reference Knowledge Base (see Knowledge Base Standards)
   - NO → Sev-3 (minor bug, workaround, low-impact issue)

---

## 3. Escalation Paths by Severity

### 3.1 Sev-1 Escalation (Outage/Data Loss)

**Immediate Actions (0–5 min):**
1. **Page on-call incident commander** via PagerDuty (see On-Call & Escalation Policy).
2. **Notify VP Support** via Slack @VP Support.
3. **Assign ticket to VP Support** (not support agent).
4. **Confirm customer's support tier:**
   - Level 4/3 customer reporting Sev-1? → Escalate to VP Support automatically (tier does not limit Sev-1 response).
   - Level 1 customer → Also notify VP Engineering & incident commander immediately.

**VP Support Actions (5–10 min):**
1. Call customer directly (phone) to confirm impact and get additional context.
2. Open war room (Slack #incident-sev1 or Teams channel).
3. Assess if issue requires engineering or is operational:
   - **Engineering defect** (e.g., data pipeline crashed) → Jump to section 3.2 Engineering Escalation.
   - **Infrastructure issue** (e.g., AWS API throttling, database performance) → Notify VP Engineering + on-call DevOps engineer.
   - **Customer misconfiguration** (rare for Sev-1) → Offer free 1-on-1 remediation; escalate CSM to relationship review.

4. **Update incident status page** (see Status Page Policy, section 2) within 15 minutes if outage affects multiple customers.

**Resolution Target:** See Incident Response Runbook for RTO and RPO targets (Sev-1: RTO 4h, RPO 1h per company bible).

---

### 3.2 Security Breach Escalation

**Immediate Actions (0–10 min):**
1. **Do NOT share breach details in customer Slack or email initially.** Page on-call incident commander + VP Security.
2. **Place ticket in confidential mode** (restricted visibility to support team only).
3. **VP Security conducts rapid triage:**
   - Was data accessed? Exfiltrated? Which data classification (PII/Confidential/Restricted)?
   - Customer requires breach notification? (See Customer Incident Communication Policy, section 4.)

4. **Escalate to VP Security + General Counsel + Chief Privacy Officer** if:
   - PII (SSN, government ID, home address) confirmed exposed.
   - Regulatory notification required (GDPR, HIPAA, state PII laws).
   - Media risk or customer public disclosure likely.

5. Route through Customer Incident Communication Policy (section 4) for legal/PR coordination.

---

### 3.3 Sev-2 Escalation (Major Feature Broken)

**Support Agent Actions (0–30 min):**
1. **Reproduce issue** in test environment with provided details.
2. **Check Knowledge Base & internal wiki:** Is there a known workaround or recent fix?
3. **If reproducible & no workaround → Escalate to VP Support.**

**VP Support Actions (30–60 min):**
1. **Determine if engineering defect or environment issue:**
   - Defect → Escalate to VP Engineering with full repro steps, customer impact (how many users affected?), revenue impact if known.
   - Environment → Coordinate with DevOps; may require AWS/Azure access or customer's Okta SSO debugging.

2. **Assign support tier escalation priority** (see Support SLA & Tiers, section 2):
   - Level 1 customer with Sev-2 → 1-hour response; VP Engineering engaged immediately.
   - Level 2 customer with Sev-2 → 2-hour response; VP Engineering engaged within 4 hours unless critical.

3. **Provide interim workaround or ETA** to customer within SLA window.

---

### 3.4 Sev-3 Escalation (Minor Bug / Cosmetic Issue)

**Support Agent Actions:**
1. **Document issue with repro steps** and customer environment details.
2. **Check for known issues or recent patches.**
3. **If simple fix available:** Apply within 4–8 hours; notify customer.
4. **If engineering required:** Create internal bug ticket; prioritize for next sprint (target: 2-week resolution).
5. **Keep customer updated weekly** until resolved.

---

## 4. Escalation Criteria by Tier

| Tier | Sev-1 | Sev-2 | Sev-3 | Sev-4 |
|---|---|---|---|---|
| Level 4 | VP Support → VP Eng | N/A (escalate to L3) | Support agent | Support agent |
| Level 3 | VP Support → VP Eng | VP Support + VP Eng | VP Support | Support agent |
| Level 2 | VP Support + VP Eng | VP Eng (within 4h) | VP Support | Support agent |
| Level 1 | VP Support + VP Eng (incident commander) | VP Eng (within 1h) | VP Support | Support agent |

---

## 5. Escalation Communication

1. **Always notify customer of escalation** within 1 hour; provide ticket number and assigned owner.
2. **Escalation message template:** "Your issue has been escalated to [VP Support/VP Engineering] for priority investigation. I've assigned [Name], who will contact you within [timeframe] with an update."
3. **Weekly updates for Sev-2/3** if unresolved; Sev-1 updates every 4 hours.

---

## 6. Escalation Documentation

All escalations logged in Zendesk with:
- Reason for escalation
- Assigned escalation owner
- Expected resolution timeline
- Any dependencies (customer action required, third-party vendors, etc.)

Support Manager reviews escalation patterns monthly to identify training gaps or systemic product issues.
