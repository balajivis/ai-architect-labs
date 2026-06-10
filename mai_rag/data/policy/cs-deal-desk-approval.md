---
title: Deal Desk & Approval Process
doc_id: cs-deal-desk-approval
owner: Sales / Legal / Finance
last_updated: 2026-06-09
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Deal Desk & Approval Process

## 1. Purpose
The Deal Desk function gates contract review and approval to ensure legal compliance, margin protection, and CFO visibility. This process is the mandatory handoff point between Sales (see Sales Playbook, section 6) and Legal/Finance.

## 2. Approval Thresholds

| Contract Value | Discount % | Approval Path | Reviewer(s) | Timeline |
|---|---|---|---|---|
| <$50K | ≤15% | Self-service (Sales) | None required | Immediate |
| <$50K | >15% | Deal Desk review | CFO (discount) | 2 business days |
| $50K–$100K | Any | Deal Desk + Legal review | Deal Desk, General Counsel | 3 business days |
| >$100K | Any | CFO, General Counsel, VP Sales alignment | CFO + General Counsel + VP Sales | 5 business days |
| Strategic partnership / custom terms | Any | Executive sign-off | CEO, General Counsel | 7 business days |

## 3. Submission Process

1. **Sales submits to Deal Desk via Salesforce** with:
   - Opportunity name, customer, estimated ARR
   - Proposed discount (if any) and business justification
   - Payment terms, multi-year flag, add-ons (professional services, support tier)
   - Customer's DPA if modified from standard template
   - Any non-standard contract terms flagged

2. **Deal Desk conducts 48-hour triage:**
   - Confirm margin (target: 70% gross margin minimum; escalate if <65%)
   - Verify compliance with Pricing & Discount Policy (section 4)
   - Route to General Counsel if DPA amendments or custom liability caps detected
   - Route to VP Sales if deal conflicts with strategic goals (e.g., selling to a competitor's subsidiary)

3. **Legal review** (if required):
   - Examines MSA, DPA, liability and indemnity clauses, IP provisions
   - Approves or requests redline
   - Confirms customer's insurance requirements align with SLA (see Support SLA & Tiers)
   - Timeline: 3–5 business days depending on complexity

4. **CFO approval** (if required):
   - Reviews margin impact, payment terms, multi-year commitment
   - Approves or declines
   - Timeline: 2 business days

5. **Sales communicates final approval to customer** and executes MSA.

## 4. Discount Policy Integration

- **Discounts ≤15%:** Sales authority; no escalation needed.
- **Discounts 16–25%:** Requires Deal Desk approval and CFO sign-off; justification must cite competitive threat or strategic value (e.g., logo acquisition, multi-year lock-in).
- **Discounts >25%:** Requires CFO + VP Sales approval; rare exception path.
- **Volume discounts (multi-year, 3+ instances):** Structured by Deal Desk; apply across all customers to prevent margin cannibalization.

## 5. Contract Execution & Closeout

1. Deal Desk confirms all reviewers have signed off (electronic approval in Salesforce suffices).
2. General Counsel executes MSA on Northwind's behalf.
3. Customer executes and returns signed MSA.
4. **Deal Desk archives final contract** in centralized folder (Salesforce / ShareFile).
5. **Deal Desk notifies Customer Success & Accounting:**
   - CSM assigned
   - Expected go-live date
   - Billing contact, payment method, PO number
   - Support tier and onboarding timeline (see Customer Onboarding Process)

## 6. Non-Standard Terms & Escalation

1. **Custom liability caps or indemnity clauses** → General Counsel escalates to VP Security if data-handling implications arise.
2. **Custom data residency requests** (e.g., "data must stay in Germany only")** → General Counsel + Engineering assess feasibility; may require product configuration (Northwind Cloud's multi-region deployment).
3. **Customer requires custom SLA** beyond standard Support SLA & Tiers → Sales Engineering + VP Engineering assess technical feasibility; CFO approves pricing premium if infrastructure investment required.

## 7. Renewal & Amendment Process

1. Renewals follow the same approval path if discount or terms change.
2. Amendments (contract modifications, additional users/seats) require Deal Desk triage if they alter margin >5%.
3. Minor amendments (e.g., billing contact change) require only signed amendment and General Counsel counter-signature.

## 8. Monthly Reporting
Deal Desk publishes monthly dashboard to CFO and VP Sales:
- Number of deals reviewed
- Total ARR closed
- Average discount % by segment
- Deals in "Legal hold" (awaiting review)
