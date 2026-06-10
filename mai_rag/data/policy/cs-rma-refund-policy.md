---
title: RMA / Refund Policy
doc_id: cs-rma-refund-policy
owner: Finance / Customer Success
last_updated: 2026-06-09
status: active
classification: confidential
supersedes: ""
superseded_by: ""
---

# RMA / Refund Policy

## 1. Overview
RMA (Return Merchandise Authorization) and refund policy governs Northwind Cloud refund requests for unsatisfactory service, failed implementations, or customer-initiated cancellations. Policy balances customer protection with revenue and operational impact.

## 2. Refund Eligibility & Windows

### 2.1 30-Day Satisfaction Guarantee (All Customers)

**Eligibility:**
- Customer initiated contract within 30 days of signature.
- Customer demonstrates good-faith implementation attempt (documented onboarding sessions, integration attempts).
- Customer requests refund in writing before day 30 of contract.

**Refund amount:** 100% of one-month subscription fee (pro-rated if partial month); no professional services refunded unless customer can demonstrate delivery failure (see section 3).

**Rationale:** Eliminates risk from customer buyer's remorse; protects customers from poor fit discovered during ramp-up.

### 2.2 Post-30-Day Refunds (Escalated Cases)

After 30 days, refund requests evaluated per section 3 (SLA Breach / Operational Failure).

---

## 3. Refund Criteria & Approval Path

### 3.1 Refund Justification Matrix

| Reason | Refund Eligibility | Approval Authority | Amount | Notes |
|---|---|---|---|---|
| **SLA breach (Sev-1 unresolved >8h)** | Eligible if documented | VP Support + CFO | 10–20% monthly fee | Customer must provide incident tickets; Support Manager validates |
| **Data loss incident** | Eligible if confirmed | VP Support + VP Eng + CFO | Full month + investigation costs | Requires post-mortem; customer bears some responsibility for backups |
| **Implementation failure** | Eligible if Northwind-caused | VP Engineer + CSM + CFO | Pro-rated pro services; 5–10% monthly fee | Cannot attribute to customer's incomplete data delivery |
| **Product fit (poor adoption)** | Not eligible post-30-day window | CSM escalation | 0% (offer expansion plan instead) | If customer unwilling to optimize, escalate to retention playbook |
| **Competitive displacement** | Not eligible | Sales VP | 0% (discount offered for continued contract) | Competitor won deal; refund doesn't recover customer |
| **Budget constraint / cost-cutting** | Not eligible | Finance | 0% (offer payment plan or discount) | Customer financial issue, not Northwind failure |
| **Organizational churn (M&A, layoff)** | Not eligible (customer situation) | CFO | 0% | Resume contract when customer stabilizes, or churn gracefully |

### 3.2 Approval Workflow

**Customer submits refund request to CSM or support@northwindcloud.com with:**
1. Reason for refund request (SLA breach, product fit, data incident, other).
2. Supporting evidence (tickets, incident report, usage logs, etc.).
3. Requested refund amount (if not obvious).

**CSM / Support Manager triage (2 business days):**
1. Confirm refund reason maps to one of section 3.1 categories.
2. Validate claim (e.g., check support tickets, confirm SLA miss, assess incident severity).
3. Route to appropriate approver:
   - **SLA breach / data loss:** VP Support + VP Engineering + CFO (all three must concur).
   - **Implementation failure:** VP Engineering + CSM + CFO.
   - **Other:** CSM escalates to VP Customer Success + CFO.

**Approval decision (3–5 business days):**
- **Approved:** CFO issues credit/refund authorization; Accounting processes within 5 business days.
- **Denied:** CSM communicates reason to customer with retention offer (discount, extended payment terms, additional support hours).

---

## 4. Refund Processing & Amounts

### 4.1 Refund Methods

1. **Pro-rated refund to original payment method** (credit card, ACH).
2. **Service credit** (applied against next month's invoice) — preferred if customer willing to continue.
3. **No refund, but discount applied to renewal** — negotiated with customer if refund not justified.

**Processing timeline:** Upon CFO approval, Accounting processes refund within 5 business days. Customer receives notification with refund authorization number.

### 4.2 Refund Amount Calculation

**30-day guarantee:**
- Refund = (Monthly subscription fee) × (Days used / 30)
- Example: $3,000/month contract, customer requests on day 15 → Refund = $1,500.

**SLA breach (partial month):**
- Refund = (Monthly fee) × (% of month SLA was breached)
- Example: Sev-1 unresolved for 8 hours in 30-day month → 10% refund = $300.

**Data loss or major incident (full month):**
- Refund = Full monthly fee if incident caused >4-hour outage or unrecoverable data loss.

**Professional services (if applicable):**
- Non-refundable unless Northwind failed to deliver contracted scope (e.g., integration not implemented, training not conducted).
- If failure confirmed, customer receives credit for hours not delivered: (Undelivered hours / Total hours) × Service cost.

---

## 5. Excluded from Refund

The following scenarios are **not** eligible for refund:

1. **Customer-caused misconfiguration** (unless CSM failed to document proper setup).
2. **Third-party outages** (AWS, Azure, Okta downtime) — Northwind notifies customer; not our responsibility.
3. **Insufficient training or adoption** (customer didn't use product; CSM offered training).
4. **Feature requests or enhancements** not yet released (customer expected future roadmap item).
5. **Scheduled maintenance** (announced ≥72 hours in advance per Support SLA & Tiers, section 6).
6. **Customer-initiated suspension** (customer violated contract terms; see Acceptable Use Policy).

---

## 6. Pricing & Discount Policy Integration

1. **Refunds post-signature are isolated from original discount.** If customer received 15% discount at signature and requests refund, refund applies to discounted rate.
2. **Service credits (not cash refunds) count toward Pricing & Discount Policy compliance** — CFO pre-approves credit amount to ensure margin impact acceptable.

---

## 7. Data Loss & Incident Refunds

If a data loss incident occurs (see Customer Incident Communication Policy, section 4):

1. **VP Engineering + VP Support investigate** (24–48 hours).
2. **Incident report generated** with root cause and Northwind responsibility assessment.
3. **CFO + General Counsel decide refund amount:**
   - If Northwind 100% at fault (infrastructure failure, backup gap) → Full month refund + 3 months credit.
   - If shared fault (customer backup lapse, policy violation) → 50% month refund + 1 month credit.
   - If customer 100% at fault (deleted own data, ignored warnings) → No refund; credit offered as goodwill.

4. **Customer notified** with incident summary, refund decision, and restoration timeline (if applicable).

---

## 8. Dispute Resolution & Appeals

If customer disagrees with refund denial:

1. **CSM escalates to VP Customer Success** within 2 business days of customer appeal.
2. **VP Customer Success conducts independent review** of claim + approver decision.
3. **Final decision issued** within 5 business days; documented in customer file.
4. **No further appeal** after VP Customer Success decision (unless new evidence emerges).

---

## 9. Churn Prevention vs. Refund

**CSM and VP Customer Success prioritize retention over refund:**
- If customer expresses dissatisfaction early (day 5–20), CSM offers support intensive, additional training, or temporary discount **before** refund becomes request.
- Refunds should be rare; goal is customer success, not refund processing.

---

## 10. Reporting & Metrics

**Finance tracks monthly:**
- Number of refund requests by reason.
- Refunds approved vs. denied (ratio).
- Average refund amount.
- Churn correlation (did refund lead to churn or prevent it?).

**VP Customer Success reviews quarterly:**
- Refund trends; identify if specific cohort or segment has higher refund rate.
- Root causes: Is it onboarding failure? Product fit? Support SLA miss?
- Corrective actions: CSM training? Product roadmap shift? Support tier adjustment?
