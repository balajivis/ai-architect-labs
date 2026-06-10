---
title: Sales Playbook
doc_id: cs-sales-playbook
owner: Sales
last_updated: 2026-06-09
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Sales Playbook

## 1. Overview
The Sales Playbook defines Northwind Cloud's go-to-market strategy, customer segmentation, and closing tactics. All sales team members must follow this playbook during prospecting, qualification, and negotiation phases. This playbook is integrated with the Deal Desk & Approval Process for all contracts requiring legal or finance review.

## 2. Customer Segmentation & ICP

| Segment | Company Size | Use Case | Contract Value | Sales Cycle |
|---------|--------------|----------|-----------------|------------|
| **Enterprise** | 1000+ empl | Multi-cloud data integration, compliance mandate | $100K–$500K+ | 6–12 months |
| **Mid-Market** | 100–1000 empl | Hybrid cloud, cost optimization | $25K–$100K | 3–6 months |
| **SMB** | <100 empl | Cloud migration, single-source integration | $5K–$25K | 1–3 months |

## 3. Discovery Phase

1. Identify the buyer committee (CTO, Finance, Operations, sometimes Chief Privacy Officer if data governance is a concern).
2. Qualify the opportunity using MEDDIC framework: **Metrics, Economic Buyer, Decision Criteria, Decision Process, Identify Pain, Champion**.
3. Conduct discovery call: map current architecture, cloud footprint (AWS vs. Azure primary), pain points, and compliance requirements (e.g., GDPR, industry-specific).
4. Reference Pricing & Discount Policy (section 4) to understand margin-preserving discount guardrails before committing.

## 4. Technical Deep Dive

1. Request architecture review: validate Northwind Cloud fit against customer's data classification standards (see Data Classification & Retention Policy).
2. Discuss security posture: MFA requirements, SSO integration, and encryption standards.
3. Highlight our compliance certifications (SOC 2, GDPR, HIPAA) and data residency options (AWS us-east-1, eu-west-1, or Azure eu-north-1).
4. Confirm support SLA expectations early—see Support SLA & Tiers for baseline options and add-ons.

## 5. Pricing & Proposal

1. **Never quote without Deal Desk approval** if discount exceeds 15% from list price (see Deal Desk & Approval Process, section 3).
2. Bundle support tier with contract: standard = Support SLA & Tiers Level 2; enterprise = Level 1 (4-hour RTO SLA).
3. Include onboarding commitment (see Customer Onboarding Process).
4. Define payment terms: net 30 standard; net 60 negotiable for multi-year contracts.

## 6. Legal & Finance Gating

1. All contracts >$50K require **Deal Desk review** before sending to customer.
2. Contracts >$100K require **CFO sign-off** and **General Counsel review**.
3. Non-standard terms (e.g., liability caps below our standard, custom data processing agreements) require **General Counsel approval**.
4. DPA (Data Processing Agreement) templates are centralized; customer-specific amendments go through Legal.

## 7. Negotiation Tactics

1. **Anchor on value, not price.** Highlight 20% average cost savings vs. competitors on the Metrics dashboard.
2. **Bundle & upsell.** Multi-year contracts (3+ years) get 10% discount; adding professional services (implementation, custom integration) increases LTV.
3. **Objection handling:**
   - *"Competitor is cheaper"* → Show ROI calculation; offer proof-of-concept.
   - *"We need to evaluate open-source alternatives"* → Highlight operational overhead; reference case studies.
   - *"Our CISO needs a SLA guarantee"* → Confirm your support tier covers RTO/RPO expectations; escalate to Sales Engineering if custom SLA requested.

## 8. Closing

1. Obtain signed MSA from customer legal and route to our General Counsel for final sign-off.
2. Confirm contract is recorded in Salesforce with estimated ARR, segments, and expected implementation start date.
3. **Hand off to Customer Success** (see Customer Success Plan) immediately upon signature. Customer Success owns onboarding timeline.
4. Schedule kickoff meeting with customer, CSM, and implementation team within 48 hours.

## 9. Escalation Path
- **Sales Engineer escalation:** Technical objections, RFP responses → escalate to VP Engineering (looped in by Sales Ops).
- **Legal escalation:** Non-standard terms → escalate through Deal Desk to General Counsel.
- **Executive escalation:** Accounts >$250K or strategic partnerships → VP Sales & CFO alignment required.

## 10. Success Metrics
- Average Sales Cycle: <4 months (target).
- Average Contract Value (ACV): $45K (target).
- Win Rate: 30% (target).
- Pipeline Health: 3x quarterly quota.
