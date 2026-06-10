---
title: Churn & Renewal Process
doc_id: cs-churn-renewal
owner: Customer Success / Sales
last_updated: 2026-06-09
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Churn & Renewal Process

## 1. Overview
The Churn & Renewal Process is the CSM + Sales collaboration framework for securing contract renewals, managing at-risk accounts, and understanding churn patterns to improve product and operations.

## 2. Renewal Timeline & Owner Responsibilities

| Phase | Timing | Owner | Activity |
|---|---|---|---|
| **Renewal planning** | 90 days before expiry | CSM | Review account health; identify risks |
| **Renewal conversation** | 75–90 days before expiry | CSM | Initial renewal discussion with customer contact |
| **Renewal negotiation** | 60 days before expiry | Sales + CSM | Price, terms, add-ons; create quote |
| **Contract signature** | 30 days before expiry | Sales + Legal | MSA execution (see Deal Desk & Approval Process) |
| **Post-renewal onboarding** | Day 1 after renewal | CSM | Confirm billing, access, next quarter plan |

---

## 3. Renewal Readiness Assessment (90 Days Prior)

CSM reviews account health (see Customer Success Plan, section 3) and answers:

1. **Is customer Green?** (Healthy usage, satisfied, no escalations)
   - YES → Proceed to section 3.1 (Standard Renewal).
   - NO (Yellow/Red) → Proceed to section 4 (At-Risk Renewal).

2. **Is contract auto-renewing or manual renewal required?**
   - Auto-renew (default for 1+ year contracts) → Confirm terms remain unchanged unless customer requests modification.
   - Manual renewal → CSM initiates conversation within 90-day window.

3. **Any planned changes?**
   - Seat expansion → Coordinate with Sales for expansion deal (see Customer Success Plan, section 4).
   - Tier upgrade → Confirm expansion rationale; coordinate with Deal Desk.
   - Downgrade → Escalate to VP Customer Success (may indicate churn risk).

---

## 4. Standard Renewal Process (Green Accounts)

### 4.1 CSM Renewal Conversation (75–90 Days)

**Agenda:**
- Recap 12-month impact: ROI, cost savings, key integrations delivered.
- Confirm satisfaction: "What's working well? Any gaps?"
- Discuss renewal terms: Same pricing, or negotiation needed?
- Introduce Sales if expansion opportunity or pricing discussion required.

**Outcome:** Documented renewal intent (verbal or email confirmation).

### 4.2 Sales Quote & Negotiation (60 Days)

**Sales team actions:**
1. **Pull contract from Deal Desk archive** (see Deal Desk & Approval Process, section 5).
2. **Create renewal quote** via Salesforce with:
   - Same tier + pricing (or modified if expansion)
   - Payment terms (standard: net 30; negotiable to net 60 for multi-year)
   - Multi-year lock-in opportunity (3-year renewal = 5% discount per Pricing & Discount Policy, section 3.1)

3. **Send quote to customer** with 60-day SLA for signature.
4. **If customer requests discount:**
   - ≤15% discount → Sales approves (see Pricing & Discount Policy, section 3.2).
   - >15% discount → Escalate to Deal Desk for CFO approval (see Deal Desk & Approval Process, section 2).

### 4.3 Legal Review & Signature (30 Days)

1. **Deal Desk routes renewal MSA to General Counsel** for sign-off (standard renewals typically require only updated dates + signature; no legal hold).
2. **Customer executes renewal MSA.**
3. **Northwind General Counsel counter-signs.**
4. **Deal Desk archives final contract + notifies Accounting & CSM** of renewal.

### 4.4 Post-Renewal (Day 1+)

1. **Accounting confirms billing:** New contract date in billing system; next invoice scheduled correctly.
2. **CSM schedules post-renewal check-in** (within 1 week): confirm any service changes, celebrate partnership continuation.
3. **CSM updates Customer Success Plan** with new success criteria or focus areas for next 12 months.

---

## 5. At-Risk Renewal Process (Yellow/Red Accounts)

### 5.1 Risk Assessment (90 Days)

**CSM + VP Customer Success triage:**
1. **Why is account Yellow/Red?**
   - Product fit issues? (Major feature requests unaddressed; integration complexity)
   - Support issues? (Frequent escalations, SLA misses — see Support SLA & Tiers escalation path)
   - Competitive threat? (Customer mentioned evaluating alternatives)
   - Budget constraint? (Finance tightening; customer seeking discount)
   - Organizational change? (Key champion departed; new CTO skeptical)

2. **Renewal likelihood: High / Medium / Low.**
   - **High:** Account is Red but solvable (e.g., budget concern, single unmet feature).
   - **Medium:** Account has structural issues but retains value (e.g., new CTO needs convincing; willing to pilot expanded use case).
   - **Low:** Account openly evaluating exit; unless major intervention likely will churn.

### 5.2 Retention Strategy (75 Days)

**VP Customer Success + Sales develop win-back plan:**

1. **Executive engagement:** VP Sales or VP Customer Success schedules call with customer's economic buyer (CFO/COO).
   - Present 12-month value delivered (reduce to metrics if not obvious).
   - Address specific pain point (scope/support/pricing).
   - Offer retention incentive (if approved by VP Sales + CFO):
     - Extended discount (5–10%) for 2–3 year commitment.
     - Additional professional services hours (free training, custom integration scoping).
     - Access to product roadmap; customer feature prioritization.

2. **Product engagement:** If feature gap identified, VP Engineering evaluates feasibility + timeline; communicate realistic roadmap to customer.

3. **Support engagement:** If escalations frequent (see Support Escalation Runbook), VP Support + CSM conduct support health review; identify training gaps or product configuration issues.

### 5.3 Negotiation & Re-engagement (60 Days)

1. **Sales + CSM co-present renewal proposal:**
   - Revised pricing (if discount approved).
   - Enhanced support tier or add-on (see Support SLA & Tiers for add-on costs).
   - Commitment to resolving pain point(s) with timeline.

2. **Customer commits or escalates concern** (e.g., needs board approval for budget exception).

3. **If customer declines renewal → Jump to section 6 (Churn Analysis).**

### 5.4 Successful Retention

1. Renewal MSA executed (with modified terms approved by Deal Desk + CFO).
2. CSM schedules intensive onboarding for upcoming quarter: focus on pain-point resolution, adoption of under-utilized features.
3. VP Customer Success monitors for regression; escalates if account slides back to Red.

---

## 6. Churn Analysis & Root Cause Investigation

### 6.1 Churn Confirmation

When customer confirms non-renewal:

1. **CSM documents reason for churn** (verbatim, from customer).
   - Competitive loss → Which competitor? What was their differentiator?
   - Budget/cost → Org-wide contraction or Northwind Cloud cost-specific?
   - Product fit → Feature gap? Performance issue?
   - Support dissatisfaction → See Support SLA & Tiers; identify SLA miss or escalation mishandling.
   - Other (org restructure, M&A, project cancellation).

2. **CSM records in Salesforce** with Opportunity stage = Closed Lost; Loss Reason = category above.

3. **VP Customer Success reviews churn entry** for pattern analysis (see section 7).

### 6.2 Exit Conversation (Optional)

CSM or Sales may offer final conversation:
- "Is there anything we could have done differently?"
- "Would you consider us for [related use case] in future?"
- "Can we stay in touch as your needs evolve?"

**Do not pressure customer.** Goal is feedback, not salvage.

---

## 7. Churn Metrics & Trending

**VP Customer Success publishes monthly churn report:**

| Metric | Calculation | Target |
|---|---|---|
| **Churn Rate (ARR)** | (Churned ARR / Beginning ARR) × 100 | <5% monthly |
| **Logo Churn** | (Churned customers / total customers) × 100 | <2% monthly |
| **Net Revenue Retention (NRR)** | (Beginning ARR + Expansion − Churn) / Beginning ARR | ≥110% |
| **Voluntary vs. Involuntary** | Churn categorized by reason | Track separately |

**Quarterly analysis:**
- Top churn reasons (e.g., 40% product fit, 30% cost, 20% competitive loss, 10% support).
- Segment analysis: Which segments churn more? (e.g., SMB higher churn; Enterprise sticky).
- Product engineering input: If feature gaps are #1 churn driver, VP Product prioritizes roadmap.

---

## 8. Integration with Customer Success Plan & Pricing Policy

- **Renewal expansion:** If customer adds seats/integrations during renewal, CSM routes to Sales for expansion deal (see Customer Success Plan, section 4).
- **Renewal discount policy:** See Pricing & Discount Policy, section 3.2 for expansion discount guardrails (existing customers eligible for 5–10% renewal discount if multi-year commitment).
