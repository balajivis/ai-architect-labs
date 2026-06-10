---
title: Support SLA & Tiers
doc_id: cs-support-sla-tiers
owner: Customer Support
last_updated: 2026-06-09
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Support SLA & Tiers

## 1. Overview
Northwind Cloud offers four support tiers (Level 4, 3, 2, 1) with increasing response times, availability, and access to engineering. All SLAs are measured from ticket submission to first response; resolution time depends on issue severity and complexity.

## 2. Support Tier Matrix

| Tier | Segment | Monthly Cost | Business Hours | Initial Response | Escalation | Phone Support |
|---|---|---|---|---|---|---|
| **Level 4 (Email)** | SMB/Starter | Included | 9a–5p US Central | 24 hours | N/A | No |
| **Level 3 (Standard)** | Mid-Market/Prof | +$500 | 8a–6p US Central | 8 hours | Support Manager | No |
| **Level 2 (Priority)** | Enterprise/Prof | +$2K | 24/7 | 4 hours (bus. hrs), 2h (off-hrs) | VP Support | Limited (queue) |
| **Level 1 (Premium)** | Enterprise | +$5K | 24/7/365 | 1 hour (all times), Sev-1 = 30 min | VP Support + VP Eng | Dedicated escalation hotline |

## 3. Severity Definitions & Response Targets

| Severity | Definition | Level 4 | Level 3 | Level 2 | Level 1 |
|---|---|---|---|---|---|
| **Sev-1** | Production outage; data loss; security breach | N/A | N/A | 1 hour | 30 min |
| **Sev-2** | Major feature broken; data not syncing; significant performance degradation | N/A | 4 hours | 2 hours | 1 hour |
| **Sev-3** | Minor feature issue; workaround exists; cosmetic bugs | 24 hours | 8 hours | 4 hours | 2 hours |
| **Sev-4** | Documentation requests; enhancement suggestions | 48 hours | 24 hours | 12 hours | 4 hours |

## 4. SLA Uptime Commitments

| Tier | Monthly Uptime % | Downtime Budget | Service Credit |
|---|---|---|---|
| Level 4–3 | 99.5% | 3.6 hours | 5% monthly fee (if <99.5%) |
| Level 2 | 99.9% | 43 minutes | 10% monthly fee (if <99.9%) |
| Level 1 | 99.95% | 22 minutes | 15% monthly fee (if <99.95%) |

## 5. Escalation & Support Runbook Integration

1. **Support Escalation Runbook** (see Support Escalation Runbook, section 2) defines when Level 4/3 escalate to Level 2/1.
2. **When a Sev-1 occurs**, customer's assigned tier determines escalation depth:
   - Level 4 customer with Sev-1 → Escalated to VP Support automatically.
   - Level 1 customer with Sev-1 → Escalated to VP Support + VP Engineering + On-Call incident commander (per On-Call & Escalation Policy).

3. **Support Manager reviews SLA performance weekly** for all tier accounts.

## 6. Exclusions & Limitations

1. **Excluded from SLA:**
   - Issues caused by customer's misconfiguration (CSM may assist at no cost if Level 1/2).
   - Third-party service outages (AWS, Azure, Okta) unless Northwind Cloud integration impacted.
   - Feature requests and enhancements (Sev-4 issues).
   - Scheduled maintenance windows (announced ≥72 hours in advance).

2. **Hours of support:**
   - Level 4/3 "Business Hours" = Mon–Fri 9a–5p US Central (Austin, TX timezone).
   - Level 2/1 available 24/7 including holidays.

3. **SLA suspension:**
   - If customer fails to provide required information within 2 business days, SLA timer pauses until customer responds.

## 7. Escalation to Engineering

1. **Level 2/1 customers** may request escalation to Engineering for Sev-1 or Sev-2 issues.
2. VP Support evaluates if issue is product defect vs. operational misconfiguration.
3. If defect confirmed, VP Engineering assigns developer within 2 hours (Level 1) or 4 hours (Level 2).
4. Engineering provides status updates every 4 hours for Sev-1, daily for Sev-2.

## 8. Support Channel & Ticketing

- **All tiers:** Email support via support@northwindcloud.com.
- **Level 2/1:** In-app chat support available 24/7 (monitors queue every 15 minutes).
- **Level 1:** Dedicated phone escalation hotline +1-512-NORTHWIN ext. 1 (24/7).
- **All tickets tracked in Zendesk** with SLA countdown displayed to support team.

## 9. Customer Success Integration

CSM monitors account health via support ticket volume and tone (see Customer Success Plan). If a customer exceeds 10 Sev-2 tickets in a month, CSM proactively schedules health check to identify root causes (missing training, product fit issue, infrastructure gap).

## 10. Tier Changes

- Customers may upgrade tier at any time; applied retroactively to active tickets.
- Downgrades effective on next billing cycle.
- VP Support approves downgrades for Level 1 accounts to prevent revenue leakage.
