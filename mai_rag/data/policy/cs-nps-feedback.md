---
title: NPS & Customer Feedback Process
doc_id: cs-nps-feedback
owner: Customer Success / Product
last_updated: 2026-06-09
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# NPS & Customer Feedback Process

## 1. Overview
NPS (Net Promoter Score) is Northwind Cloud's primary measure of customer satisfaction and satisfaction trajectory. This policy defines how NPS surveys are conducted, analyzed, and acted upon to drive product improvements and identify at-risk accounts (see Customer Success Plan, section 3).

## 2. NPS Survey Program

### 2.1 Survey Timing & Frequency

| Trigger | Timing | Audience | Recipient |
|---|---|---|---|
| **Onboarding completion** | Day 90 after signature | All new customers | CSM |
| **Quarterly check-in** | End of every quarter | All active customers | CSM |
| **Post-support interaction** | 24 hours after Sev-1 / Sev-2 closure | Affected customers | Support team |
| **Annual customer review** | 1 week before renewal | Renewing customers | CSM |
| **Churn feedback** | Upon non-renewal decision | Churned customers | VP Customer Success |

### 2.2 NPS Survey Format

**Core question:**
"How likely are you to recommend Northwind Cloud to a colleague on a scale of 0–10?"

**Follow-up questions (conditional):**
- **If 9–10 (Promoter):** "What's your primary reason for recommending us?"
- **If 7–8 (Passive):** "What could we improve to move you to a 9?"
- **If 0–6 (Detractor):** "What's holding you back from recommending us?" + "Would you be open to a conversation with our leadership?"

**Open comment field:**
"Any other feedback for Northwind Cloud?"

---

## 3. NPS Calculation & Segments

### 3.1 Net Promoter Score Formula

```
NPS = % Promoters (9–10) − % Detractors (0–6)
```

**Example:** If 60% Promoters, 20% Detractors, 20% Passive → NPS = 60% − 20% = +40.

### 3.2 NPS Benchmarking

| Segment | Northwind Target | Industry Average | Interpretation |
|---|---|---|---|
| **Enterprise** | ≥70 | 50–60 | Market-leading satisfaction |
| **Mid-Market** | ≥60 | 40–50 | Strong satisfaction |
| **SMB** | ≥50 | 30–40 | Acceptable; room for growth |
| **Overall** | ≥60 | 40–50 | Target: Top quartile |

### 3.3 Segment Analysis

VP Customer Success tracks NPS by:
- **Customer segment:** Enterprise, Mid-Market, SMB (see Sales Playbook, section 2).
- **Use case:** Single-cloud vs. multi-cloud; cost optimization vs. compliance.
- **Tenure:** New (0–6 months), established (6–24 months), mature (24+ months).
- **Support tier:** Level 1/2 vs. Level 3/4 (see Support SLA & Tiers).

**Monthly trending:** Plot NPS by segment; identify declines for root cause analysis.

---

## 4. Detractor Management & Escalation

### 4.1 Detractor Outreach (Within 48 Hours)

When a Detractor (0–6 score) responds to NPS survey:

1. **VP Customer Success routes to CSM immediately** with survey response.
2. **CSM schedules call within 48 hours** to understand root cause.
3. **Conversation goal:** Identify what could move account from "would not recommend" to "passive" or "promoter".

**Common root causes:**
- **Support SLA miss:** Recent ticket went unresolved >SLA (see Support SLA & Tiers; escalate to Support Manager).
- **Feature gap:** Customer's critical use case unsupported (escalate to VP Product).
- **Integration issue:** Data quality or latency problems (escalate to Support Escalation Runbook).
- **Pricing objection:** Customer feels over-charged; wants discount (escalate to Sales for renewal negotiation).
- **Competitive evaluation:** Customer actively evaluating alternatives (escalate to VP Sales for win-back strategy).

### 4.2 Detractor Resolution & Follow-Up

**CSM documents action plan:**
1. Root cause identified.
2. Remediation steps (support escalation, product roadmap commitment, discount offer, implementation plan).
3. Timeline for resolution.
4. Follow-up NPS survey scheduled (30–60 days) to confirm improvement.

**Escalation if unresolved:**
- If Detractor remains at-risk after 30 days, escalate to VP Customer Success.
- VP Customer Success assesses churn probability (see Churn & Renewal Process, section 5).
- If high churn risk, VP Customer Success + VP Sales develop retention strategy.

---

## 5. Passive Optimization

Passives (7–8 scores) are high-value targets for conversion to Promoters:

1. **Identify quick wins:** Common feedback from Passives (e.g., "easier reporting", "faster support response").
2. **Targeted initiatives:** CSM offers low-cost improvements (additional training, premium support tier trial, feature roadmap commitment).
3. **Re-survey:** Follow-up NPS after initiative (expect 10–15% uplift to Promoters).

---

## 6. Promoter Advocacy Program

### 6.1 Promoter Identification

Promoters (9–10 scores) with additional signals become advocates:
- **Tenure >12 months:** Stable, long-term satisfaction.
- **Active usage:** Integrations working well; data flowing predictably.
- **Expansion:** Customer recently upgraded tier or added integrations (see Customer Success Plan, section 4).
- **Explicit offer:** Open to reference calls, case studies, or testimonials.

### 6.2 Promoter Engagement

**CSM + Marketing coordinate:**
1. **Customer reference:** Promoter willing to take calls from prospects (paid program: $500–$2,000/year incentive).
2. **Case study:** Deep dive into customer's use case, results, ROI (CSM coordinates interview; Marketing writes article).
3. **Testimonial:** Written quote for website (CSM requests; Marketing incorporates).
4. **Speaking engagement:** Customer willing to present at webinar or conference (referral fee if customer declines, Northwind covers travel).

**Selection criteria:** Segment variety (Enterprise + Mid-Market + SMB); industry diversity; results-oriented use case.

---

## 7. Feedback Integration & Product Roadmap

### 7.1 Feedback Themes

**Quarterly, Product Manager analyzes all feedback (NPS comments, support tickets, feature requests):**

| Feedback Category | Frequency Threshold | Action |
|---|---|---|
| **Feature request** | ≥5 customers mention same feature | Prioritize on product roadmap |
| **Usability issue** | ≥3 customers report difficulty with same workflow | UX review; potential redesign |
| **Integration gap** | ≥3 customers need specific data source connector | Engineering estimates effort; roadmap decision |
| **Support/SLA complaint** | ≥2 recent detractors cite support issues | Support Manager reviews SLA performance; training plan |
| **Pricing concern** | ≥2 detractors mention cost/discount | Sales + CFO assess pricing strategy |

### 7.2 Customer Advisory Board

Annually, VP Customer Success invites 8–12 Promoters (mix of segments/industries) to:
- Review Northwind Cloud roadmap (6–12 month outlook).
- Provide feedback on proposed features.
- Share use cases + expansion opportunities.

**Output:** Customer input incorporated into product strategy; customers feel heard & valued.

---

## 8. NPS Dashboard & Reporting

### 8.1 Internal Dashboard (Updated Monthly)

VP Customer Success publishes NPS dashboard visible to all teams:
- **Current NPS score** (overall + by segment).
- **Trending chart** (3-year history).
- **Promoter/Passive/Detractor breakdown (pie chart)**.
- **Open detractors** (flagged; CSM action required).
- **Recent promoter engagements** (case studies, references, speakers).

### 8.2 Executive Reporting (Quarterly)

CFO, VP Sales, VP Product receive quarterly NPS report:
- **Overall NPS trend:** Up / down / stable?
- **Segment performance:** Which segments improving? Declining?
- **Detractor analysis:** Root causes; remediation actions.
- **Promoter advocacy:** Active references, case studies published, testimonials collected.
- **Product roadmap impact:** Features prioritized based on feedback.
- **Risk indicators:** Significant NPS decline tied to support SLA misses or feature gaps?

---

## 9. NPS Tool & Administration

**Platform:** Delighted.io or Zendesk NPS integration.

**Administration:**
- **VP Customer Success:** Owns NPS program, interprets trends, escalates detractors.
- **CSM:** Conducts follow-up calls with detractors/passives; updates Salesforce with action plans.
- **Marketing:** Manages promoter advocacy program; coordinates case studies + testimonials.
- **Support Manager:** Provides feedback to Support team on SLA/quality trends visible in NPS comments.

---

## 10. Integration with Other Processes

- **Customer Success Plan (section 3):** NPS is primary health score signal; Red accounts often have recent NPS decline.
- **Churn & Renewal Process (section 6.1):** Detractors flagged for renewal at-risk assessment.
- **Support Escalation Runbook:** Support SLA misses surface in NPS feedback; VP Support investigates.
- **RMA & Refund Policy (section 10):** Refund trends correlated with NPS; improving refund resolution impacts NPS positively.
