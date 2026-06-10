---
title: Customer Success Plan
doc_id: cs-customer-success-plan
owner: Customer Success
last_updated: 2026-06-09
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Customer Success Plan

## 1. Overview
The Customer Success Plan is the CSM's strategic roadmap for each customer account. It bridges customer onboarding (see Customer Onboarding Process) into steady-state engagement and drives retention, expansion, and renewal revenue.

## 2. Plan Structure (Created During Onboarding)

### 2.1 Customer Profile
- **Company name, industry, HQ location**
- **Contact roster:** Economic buyer (CFO/COO), technical champion (CTO/architect), end-user teams
- **Business context:** Primary use case (cost optimization, compliance, multi-cloud strategy), organizational pain points
- **Northwind Cloud deployment:** Products/tiers deployed, data volume, integrations active

### 2.2 Success Criteria
Defined jointly with customer during kickoff (see Customer Onboarding Process, section 2):
- **Metric 1:** Primary KPI (e.g., "reduce data integration time by 40%", "ingest 500TB by month 4")
- **Metric 2:** Secondary KPI (e.g., "achieve 99.9% data accuracy", "enable self-service reporting for 50 analysts")
- **Timeline:** Target achievement date (typically end of Q)

### 2.3 Quarterly Business Reviews (QBRs)

CSM conducts QBR every quarter (or semi-annually for small accounts):

**Agenda:**
1. Review actual performance vs. success criteria; celebrate wins.
2. Identify unmet needs: features used less frequently, missing integrations, performance gaps.
3. Discuss usage trends: adoption rates, team growth, data volume trajectory.
4. Plan next quarter: new integrations, team expansion, professional services engagements.

**Output:** Updated success plan + expansion opportunities identified → Handed to Sales for upsell conversations.

---

## 3. Health Scoring & Engagement Cadence

CSM maintains a health score (Red / Yellow / Green) updated monthly based on:

| Health Signal | Green | Yellow | Red |
|---|---|---|---|
| **Product usage** | Weekly active users; monthly integrations running | Sporadic usage; <50% of planned integrations live | No activity for 2+ weeks; major integrations failing |
| **Support tickets** | ≤5/month, mostly Sev-4 | 6–10/month, includes Sev-3 | >10/month or Sev-2+ unresolved >7 days |
| **Expansion signals** | Customer-initiated feature requests; team growth requests | No new requests in 60 days | Headcount reduction; cost-cutting queries |
| **NPS feedback** | ≥8/10 on recent survey | 6–7/10 | <6/10 or written complaints |
| **Renewal trajectory** | On track for renewal; positive sentiment | Uncertain; customer evaluating alternatives | At risk; explicit non-renewal signals |

### 3.1 Engagement Cadence by Health

| Health | Monthly Touchpoints | CSM Escalation | Sales Involvement |
|---|---|---|---|
| **Green** | 1 (monthly check-in) | None | None unless expansion identified |
| **Yellow** | 2–3 (monthly + follow-ups) | VP Customer Success (if >2 months Yellow) | Sales looped for at-risk renewal |
| **Red** | Weekly | VP Customer Success + VP Sales immediately | Renewal risk mitigation + win-back plan |

---

## 4. Expansion Revenue & Upsell Opportunities

CSM identifies expansion during QBRs and monthly check-ins:

1. **Seat expansion:** New team members needing access (Professional Services → seat count increase).
2. **Data volume growth:** Customer exceeds contracted tier (Professional → Enterprise tier upgrade).
3. **New integrations:** Customer wants to connect additional data sources (professional services engagement).
4. **Support tier upgrade:** Yellow/Red customers requiring higher SLA (see Support SLA & Tiers for margin).
5. **Custom development:** Customer requests out-of-scope feature (VP Engineering scopes; Sales negotiates SOW).

**CSM hand-off:** When expansion opportunity identified, CSM engages Sales & Deal Desk for quote (see Deal Desk & Approval Process, section 2).

---

## 5. Churn Prevention & Renewal Process

CSM initiates renewal process 90 days before contract end (see Churn & Renewal Process for detailed timeline):

**Renewal conversation:**
1. Review 12-month ROI delivered: cost savings, operational improvements, team productivity gains.
2. Confirm contract terms & pricing; address any budget concerns early.
3. If churn risk detected, escalate to VP Sales for retention negotiation (See Churn & Renewal Process, section 5).

---

## 6. Customer Advocacy & Case Studies

CSM identifies customers for:
- **Case studies:** 2–3 success stories published annually (VP Marketing owns design; CSM coordinates customer participation).
- **Testimonials & references:** Customer willing to speak at events or provide written quote for website.
- **Product feedback:** CSM funnels customer feature requests to VP Product; escalates urgent compliance/security needs to VP Engineering.

---

## 7. Escalation & Account At-Risk Protocol

**CSM escalates to VP Customer Success if:**
- **Red health score** for 2+ consecutive months.
- **Explicit non-renewal signal** (customer says "we're moving to [competitor]").
- **Major support incident** causing extended outage or data issue (see Support Escalation Runbook, section 3).
- **Expansion deal falls through** due to scope/budget (may indicate relationship fracture).

**VP Customer Success actions:**
1. Schedule executive business review with customer's CFO/COO.
2. Co-present roadmap or custom value proposition.
3. Coordinate with Sales on retention offer (discount, extended payment terms, added professional services).

---

## 8. CSM Performance Metrics

| Metric | Target | Calculation |
|---|---|---|
| **Net Revenue Retention (NRR)** | ≥110% | (Beginning ARR + Expansion − Churn) / Beginning ARR |
| **Customer Health Score** | ≥85% Green | (# Green accounts / total accounts) |
| **Renewal Rate** | ≥95% | (# Renewed / # eligible) |
| **Time to QBR** | <30 days post-quarter-end | QBR scheduled before month 1 of next quarter |
| **Expansion per account** | $10K avg | Total expansion ARR / total accounts |

---

## 9. Integration with Pricing & Discount Policy

When expansion negotiated (new seat, tier upgrade), CSM + Deal Desk apply expansion discounts per Pricing & Discount Policy, section 3.2 (5–10% discretionary discount allowable for existing customers). Expansion margins must maintain ≥70% gross margin (see Pricing & Discount Policy, section 5).

---

## 10. Documentation & Handoff

All CSM notes (QBR output, health score changes, expansion opportunities, churn signals) logged in **Salesforce** under account record. Sales & Executive team review quarterly for strategic account planning.
