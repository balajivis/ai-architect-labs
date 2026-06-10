---
title: On-Call & Escalation Policy
doc_id: on-call-escalation-policy
owner: Engineering Leadership
last_updated: 2026-03-01
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# On-Call & Escalation Policy

## 1. On-Call Program Overview

Northwind operates a 24/7 on-call rotation to respond to production incidents, customer emergencies, and critical security events. On-call engineers are responsible for rapid response and escalation per the Incident Response Runbook.

## 2. On-Call Roles and Responsibilities

### 2.1 On-Call Engineer

**Availability**: 24 hours on-call (primary rotation)

**Responsibilities:**
- **Response time**: Answer page within 5 minutes
- **Triage**: Assess incident severity (Sev-1 to Sev-4)
- **Communication**: Activate incident response team per severity
- **Remediation**: Work on fix or escalate to specialist
- **Documentation**: Log incident in tracking system before end of shift

**Tools provided:**
- Pager (PagerDuty): Receives alerts and incident pages
- Laptop with full VPN/system access
- 24/7 support from on-call manager (escalation contact)

### 2.2 On-Call Manager (Escalation Contact)

**Availability**: 24 hours (secondary escalation)

**Responsibilities:**
- **Sev-1 incidents only**: Activated for critical outages or data breaches
- **Executive notification**: Ensures leadership is informed per Incident Response Runbook timelines
- **Resource allocation**: Can call in additional engineers, contractors, or vendors if needed
- **Customer communication**: Coordinates messaging with VP Customer Success

**Contact**: Phone tree in PagerDuty; primary manager listed on every on-call shift

### 2.3 On-Call Manager (Coverage)

If on-call engineer cannot reach primary escalation manager, contact backup manager (listed in PagerDuty). All managers are trained to handle Sev-1 incidents.

## 3. On-Call Rotation Schedule

### 3.1 Rotation Assignment

- **Teams with on-call duty**: Engineering (backend), Engineering (infrastructure), Customer Support
- **Rotation frequency**: 1 week per person (Monday 9 AM PT – Sunday 9 AM PT)
- **Coverage**: 2 primary engineers on rotation at all times (to handle simultaneous incidents)
- **Handoff**: On-call transfer happens at 9 AM PT every Monday (outgoing engineer briefs incoming engineer on active issues)

### 3.2 Who Participates

- **Required**: All senior engineers (2+ years experience), all ops engineers, all support leads
- **Optional**: Junior engineers and interns (only if trained and approved by manager)
- **Exempt**: HR, Finance, Sales, Marketing (non-critical incident response)

**New employees** participate in on-call after successful 90-day probation completion.

### 3.3 Rotation Exclusions

Employees cannot be scheduled for on-call during:
- Approved PTO (vacation, sick leave, parental leave)
- Medical leave or disability
- Recent deployments (on-call engineer who deployed code that week participates but is given priority recovery time)

If on-call falls during your approved PTO, swap with another on-call engineer (coordinate in Slack). **Do not ignore pages during vacation.**

## 4. Incident Response Escalation

### 4.1 Severity-Based Escalation

Upon receiving a page, the on-call engineer performs initial triage and escalates per severity:

| Severity | On-Call Action | Escalation Timeline | Escalation Path |
|---|---|---|---|
| **Sev-1** | Immediately activate incident response team | Within 5 min | On-call engineer → On-call manager → VP Engineering → CEO |
| **Sev-2** | Assess; escalate if outside scope | Within 15 min | On-call engineer → VP Engineering + Engineering team lead |
| **Sev-3** | Assess; escalate if blocker | Within 1 hour | On-call engineer → Team lead (no VP page) |
| **Sev-4** | Log and monitor; escalate if escalates to Sev-3 | Within 24 hours | On-call engineer → Daily standup review |

### 4.2 Escalation Decision Tree

```
Page received
  ├─ Assess severity
  │  ├─ Sev-1? → Call on-call manager immediately
  │  ├─ Sev-2? → Assess if you can resolve alone
  │  │          ├─ Yes → Work on fix; escalate if stalled >30 min
  │  │          └─ No → Call team lead
  │  ├─ Sev-3? → Work on fix; escalate if stalled >2 hours
  │  └─ Sev-4? → Log and monitor
  │
  └─ Document in incident tracker
```

### 4.3 Customer Communication During Incidents

- **Sev-1/Sev-2**: VP Customer Success is notified and owns customer communication
- **Sev-3**: Support lead notifies affected customers
- **Sev-4**: Documented in customer support system; no proactive notification

On-call engineer focuses on remediation; customer communication is handled by dedicated team.

## 5. Pager and Alerting

### 5.1 Alert Sources

On-call engineers receive pages from:
- **Automated monitoring**: Splunk, DataDog, Azure Monitor (alert thresholds breached)
- **Customer reports**: Support team escalates to on-call via PagerDuty
- **Security alerts**: Okta login anomalies, CloudFlare DDoS detection
- **Deployment issues**: Failed deployment detected by CI/CD pipeline

### 5.2 Alert Tuning

False alerts are the enemy of on-call. Teams are responsible for:
- Tuning alert thresholds quarterly (too strict = false positives; too loose = missed issues)
- Removing stale alerts (e.g., deprecated service still generating alerts)
- Documenting alert runbooks (what each alert means and how to investigate)

**Excessive false alerts** (> 3 per week) trigger a team retrospective and remediation plan.

## 6. On-Call Compensation and Rest

### 6.1 On-Call Pay

- **Base on-call stipend**: $500 per week for being on-call (regardless of pages received)
- **Page response bonus**: $100 per Sev-1 page, $50 per Sev-2 page
- **Incident response bonus**: Additional pay (10–50 hours) if incident response extends beyond 4 hours

### 6.2 Rest and Recovery

To avoid burnout, employees on on-call have:
- **Flex time policy**: If paged during off-hours, employee may arrive 2 hours late next business day
- **No on-call back-to-back weeks**: Minimum 1 week between on-call assignments
- **Manager check-in**: After high-intensity on-call week (Sev-1 incident), manager checks in on wellbeing

## 7. Training and Readiness

### 7.1 On-Call Certification

Before joining on-call rotation:
1. Complete on-call training (4 hours; incident response runbook walkthrough)
2. Shadow an experienced on-call engineer for 1 full shift
3. Pass knowledge assessment (scenario-based incident response quiz)
4. Manager signs off on readiness

### 7.2 Runbook Maintenance

Every team maintains a runbook for their service:
- How to detect incidents (alert definitions)
- Common failure modes and fixes
- Escalation contacts (who to call for DB, networking, security, etc.)

Runbooks are reviewed quarterly and updated as systems evolve.

## 8. Penalties for On-Call Violations

### 8.1 Late Response

- **Page not answered within 5 minutes**: Investigation into why (was phone off? in meeting? timezone issue?)
- **Pattern of late response** (2+ incidents per month): Mandatory re-training or removal from on-call
- **Critical incident missed entirely**: Required to find coverage swap and attend additional training

### 8.2 Inappropriate Action

- **Ignoring a Sev-1 page**: Disciplinary action (written warning minimum)
- **Making undocumented production changes during incident**: Disciplinary action + mandatory code review retraining
- **Unauthorized disclosure of customer data during investigation**: Immediate termination

## 9. Related Documentation

- **Incident Response Runbook**: Severity definitions, escalation timelines, notification procedures
- **Production Deployment Runbook**: How on-call readiness is confirmed before deployment
- **Identity & Access Management Policy**: VPN and emergency access during incidents
- **Employee Onboarding Guide**: On-call training for new hires in critical roles

---

**Document owner:** VP Engineering  
**Last approved:** 2026-03-01 by Engineering Leadership  
**Next review:** 2027-03-01

**Additional resources:**
- PagerDuty schedule: https://northwind.pagerduty.com/schedules
- On-call runbook wiki: https://wiki.northwind.com/on-call/ (internal)
- Incident tracking: https://jira.northwind.com/projects/INCIDENT
