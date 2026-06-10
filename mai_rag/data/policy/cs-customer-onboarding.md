---
title: Customer Onboarding Process
doc_id: cs-customer-onboarding
owner: Customer Success
last_updated: 2026-06-09
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Customer Onboarding Process

## 1. Overview
The Customer Onboarding Process is the first 90 days post-signature. This phase sets the trajectory for customer satisfaction, time-to-value, and expansion revenue. CSM, Sales, and Engineering collaborate to deliver a frictionless experience.

## 2. Pre-Onboarding (Day 0–3)

1. **Deal Desk hands off to CSM** (see Deal Desk & Approval Process, section 5):
   - CSM assigned based on customer segment (Enterprise = dedicated CSM; Mid-Market = shared 1:50; SMB = low-touch digital).
   - Onboarding playbook selected based on use case (single-cloud vs. multi-cloud integration).

2. **CSM conducts kickoff call within 48 hours:**
   - Introduce implementation team (solution architect, integration engineer).
   - Review success criteria: define what "success" looks like by month 3 (e.g., X% data integration complete, Y TB ingested).
   - Establish weekly check-in cadence.
   - Confirm data classification & security requirements (see Data Classification & Retention Policy).

3. **Implementation team provisioning:**
   - Set up customer's Okta SSO integration with Northwind Cloud.
   - Provision AWS/Azure accounts or validate customer's existing cloud credentials.
   - Enable MFA for all customer admin users (mandatory per Information Security Policy).
   - Configure data encryption in transit and at rest per customer's classification policy.

## 3. Phase 1: Discovery & Planning (Weeks 1–2)

1. **Detailed architecture review:**
   - Document customer's current data sources (ERP, CRM, data warehouse, logs).
   - Map data classification levels (Public, Internal, Confidential, Restricted) to each source.
   - Identify integration priority order (critical-path data first).

2. **Success plan creation:**
   - CSM + customer create 90-day success plan with milestones:
     - Week 4: First data pipeline live (pilot).
     - Week 8: Mission-critical integrations complete.
     - Week 12: Full scope deployed, users trained.

3. **Support tier alignment:**
   - Confirm selected support tier (see Support SLA & Tiers) matches operational criticality.
   - Escalate if customer's RTO/RPO expectations exceed contracted SLA.

4. **Training calendar:**
   - Schedule platform training (4 hours), admin training (2 hours), and end-user training (per team).
   - Provide Knowledge Base access (see Knowledge Base Standards).

## 4. Phase 2: Build & Deploy (Weeks 3–8)

1. **Data integration development:**
   - Solution Architect configures pipelines for top-priority data sources.
   - Testing in staging environment; customer validates schema, data completeness.
   - Security review: confirm PII handling complies with customer's data classification (encrypt, tokenize, or mask as required).

2. **Weekly check-ins:**
   - Agenda: progress against milestones, blockers, data quality issues.
   - CSM escalates technical issues to Support (see Support SLA & Tiers, Support Escalation Runbook for escalation criteria).

3. **Pilot production deployment:**
   - First pipeline goes live in production by end of week 4.
   - Monitor performance; customer confirms data quality & latency acceptable.

## 5. Phase 3: Optimization & Closure (Weeks 9–12)

1. **Remaining integrations go live:**
   - All mission-critical pipelines in production.
   - Performance baseline established (latency, data freshness).

2. **User acceptance testing (UAT):**
   - End-user teams validate data in their BI tools, applications, or data warehouses.
   - CSM collects feedback; Engineering addresses critical issues within 48 hours.

3. **Knowledge transfer:**
   - Admin training on operations: monitoring alerts, troubleshooting, user provisioning.
   - Runbook handoff: CSM documents customer-specific runbooks (e.g., "how to add a new data source").

4. **Onboarding closure:**
   - Signed onboarding completion certificate (confirms customer accepted delivery).
   - Transition to CSM steady-state support (monthly or quarterly business reviews).
   - Trigger digital NPS survey (see NPS & Customer Feedback Process, section 2).

## 6. Milestones & Exit Criteria

| Milestone | Week | Criteria | Owner |
|---|---|---|---|
| Kickoff completed | 1 | Success plan signed, team introductions | CSM |
| Pilot live | 4 | First pipeline in prod, data validated | Engineering |
| Critical integrations live | 8 | 80% of planned integrations deployed | Engineering |
| Full scope live & accepted | 12 | UAT passed, runbooks documented, users trained | CSM + Engineering |

## 7. Escalation During Onboarding

1. **Data quality issues:** If data completeness <95% after week 6, escalate to VP Engineering.
2. **SLA violations:** If support response times exceed contracted SLA (see Support SLA & Tiers), CSM escalates to VP Support.
3. **Scope creep:** If customer requests out-of-scope integrations, CSM routes to Sales for change order (new professional services engagement).
4. **Resource constraints:** If implementation team cannot meet timeline, VP Engineering escalates to CSM/customer with revised timeline.

## 8. Success Metrics

- **On-time delivery:** ≥90% of onboardings complete by week 12.
- **Time-to-value:** 50% of integrations live by week 4.
- **Customer satisfaction:** ≥8/10 on onboarding NPS.
- **Zero critical security incidents:** No data breaches or compliance violations during onboarding.
