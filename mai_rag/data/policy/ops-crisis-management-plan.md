---
title: Crisis Management Plan
doc_id: ops-crisis-management-plan
owner: Executive Leadership & Security
last_updated: 2026-06-09
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Crisis Management Plan

## 1. Purpose & Scope

The Crisis Management Plan (CMP) defines how Northwind Technologies identifies, escalates, and manages crises—events that pose significant risk to company reputation, customer trust, financial stability, or regulatory compliance. This plan complements the Business Continuity Plan (BCP) by adding governance, decision-making authority, and stakeholder communication layers.

**Scope**: All employees; particularly applicable to customer-facing incidents, executive decisions, and external stakeholder notifications.

## 2. Crisis Definitions & Escalation

A **Crisis** is any event meeting one or more of:
- **Business Impact**: Revenue loss >$100K/day, breach of SLA by >4 hours (Tier-1 functions)
- **Reputation Risk**: Public social media/press reporting; customer attrition risk >5% annual
- **Regulatory Risk**: Suspected GDPR violation, data breach affecting >1,000 customers, inquiry from tax/banking regulators
- **Safety or Well-being**: Employee or customer injury, threat to workplace safety

| Event Type | Incident Severity | Crisis Level | Authority | Timeline |
|------------|-------------------|--------------|-----------|----------|
| Production API outage 4+ hours | Sev-1 | **Level 1** | CEO + VP Engineering | Immediate CEO brief |
| Customer data breach (10+ records) | Sev-2 | **Level 2** | VP Security + General Counsel | Within 1 hour |
| Social media/press coverage (reputational) | N/A | **Level 2** | CEO + VP People | Within 30 min |
| Multi-day facility disruption | Sev-3 | **Level 3** | VP Operations + VP People | Within 4 hours |

## 3. Crisis Management Team & Decision Authority

### 3.1 Core Team (Level 1 & 2)
- **CEO** – ultimate decision maker; activates Board notification and external PR
- **VP Security** – incident assessment, containment, compliance advice
- **VP Engineering** – technical recovery timeline, root cause analysis
- **General Counsel** – regulatory obligations, customer notification legal review, external counsel coordination
- **Chief Privacy Officer** – GDPR/data-subject-rights implications (see Data Privacy & GDPR Compliance Policy)
- **VP People** – employee safety, internal comms, HR impacts
- **CFO** – financial impact, insurance/claims, investor communication (if Board directed)

### 3.2 Convening Protocol
- **CEO or VP Security** calls meeting within 30 minutes of Level-1 classification
- **Attendees**: Core team + incident owner (functional VP); legal counsel; PR advisor (external, on-call 24/7)
- **Frequency**: Hourly updates minimum until incident downgraded; then daily until resolved

### 3.3 Board Notification (Level 1 only)
- CEO briefs Board within 2 hours of Level-1 classification
- Follow-up brief within 24 hours with root cause assessment and mitigation plan
- Quarterly reporting on all Level-2+ incidents to Audit Committee

## 4. Communication Strategy by Audience

### 4.1 Internal Communication
**Timing**: Before external announcement

1. **All-hands announcement** (Slack + email) within 30 minutes of Level 1/2 activation
   - Clear statement: what happened, what we're doing, next update ETA
   - No speculation; approved talking points only
2. **Department briefings**: Functional VPs brief their teams, approved message
3. **Ongoing updates**: Every 2 hours via Slack #incident-declared; daily once stabilized
4. **See Internal Communications Policy** for channel/format standards

### 4.2 Customer Communication
**Responsibility**: Customer Success (tactical), CEO/PR (strategic)

1. **Initial notification** (within 1 hour of Level 1): "We are aware of an issue. Technical team is investigating. More info within 30 minutes."
2. **Detailed update** (within 2 hours): Root cause, scope (affected customers), impact, ETA for resolution
3. **Resolution notice**: When service fully restored, brief post-mortem link offered
4. **SLA credit**: Finance/billing applies per service agreement; VP Operations approves

### 4.3 External Stakeholder Communication
- **Press/Media**: CEO + PR advisor; statement drafted and approved by General Counsel before release
- **Investors/Board**: CEO; detailed narrative (impact, timeline, response) within 24 hours if material
- **Regulators**: General Counsel; GDPR authority notification per Data Privacy & GDPR Compliance Policy (timing depends on data-breach severity)

## 5. Crisis Containment & Decision-Making

### 5.1 Initial Assessment (0–60 minutes)
1. Fact gather: What, when, scope, impact, root cause hypothesis
2. Classify event: Crisis level (1, 2, or 3)
3. Activate decision-making team and declare incident commander (usually VP of functional area)
4. Notify all Core Team members and convene within 30 minutes

### 5.2 Response Phase (1–4 hours)
1. **Technical/Operational**: Execute remediation per Incident Response Runbook (isolation, restore, failover)
2. **Legal/Compliance**: General Counsel assesses regulatory disclosure obligations
3. **Communication**: Prepare internal and external messaging; CEO approves strategy
4. **Escalation**: If technical recovery >4 hours and no solution in sight, escalate to BCP activation

### 5.3 Recovery & Stabilization (4–48 hours)
1. Restore normal operations; reduce crisis team frequency to daily check-ins
2. Assign post-mortem lead; schedule blameless review within 5 business days
3. Prepare final customer/investor communication
4. Brief Board if Level 1; document lessons-learned

## 6. Specific Crisis Scenarios

### 6.1 Data Breach (10+ customers affected)
- **Trigger**: VP Security confirms unauthorized access to customer data
- **Immediate**: Isolate systems; preserve forensic evidence; convene Core Team
- **Legal**: General Counsel determines GDPR notification timeline (per Data Priv & GDPR Compliance Policy); assess regulatory fine risk
- **Customer**: Customer Success prepares breach notification; offer free credit monitoring for affected individuals
- **Post-incident**: Mandatory security training for all employees (per Information Security Policy)

### 6.2 Service Outage (>4 hours, affecting customers)
- **Trigger**: API availability <95% for 4+ consecutive hours; SLA breach imminent
- **Technical**: VP Engineering leads war room; assess rollback vs. forward fix
- **Communication**: CEO updates customers every 60 minutes; transparency builds trust
- **Escalation**: Activate BCP if RTO cannot be met within 4 hours; failover to Azure
- **Post-incident**: Change advisory board reviews deployment process per Production Deployment Runbook

### 6.3 Public Relations Crisis (social media, negative press)
- **Trigger**: >100 mentions of Northwind in negative context within 24 hours; media inquiry received
- **Response**: CEO + PR advisor draft statement within 4 hours
- **Amplification**: Internal comms brief employees before external release
- **Engagement**: Customer Success proactively reaches out to at-risk accounts
- **Learning**: After stabilization, conduct reputation risk review with Board

## 7. Crisis Plan Testing & Updates

- **Tabletop drill**: Annually (Q2); simulates Level-2 crisis (data breach scenario)
- **Stakeholder interviews**: Bi-annually; Core Team members review this plan
- **Updates**: After any crisis activation or annual review; CEO sign-off required

**Last Drill**: May 2026 (data-breach scenario); response time met targets. **Next**: May 2027.

