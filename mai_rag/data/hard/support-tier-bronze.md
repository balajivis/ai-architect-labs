---
title: Northwind Support Plan — Bronze Tier SLA
doc_id: support-tier-bronze
owner: Customer Success
last_updated: 2026-02-10
status: active
classification: public
supersedes: ""
superseded_by: ""
---

## Scope

This document defines the service-level commitments that Northwind Technologies extends to customers enrolled in this plan. It applies to all production environments provisioned under an active entitlement at this level and supersedes any informal commitments made during evaluation, onboarding, or sales conversations. Where a signed enterprise agreement contains negotiated terms, that agreement prevails; otherwise the targets described here are the governing commitments for the account.

Entitlements are tied to the subscribing legal entity and may not be shared, resold, or transferred to affiliates without written approval from Northwind Customer Success. The commitments below describe first-response targets, restoration targets, coverage windows, eligible channels, named-contact limits, and uptime-credit thresholds. Each commitment in this document belongs to the tier named in the title block above and to no other tier; figures quoted for higher or lower plans live in their own documents and must not be read into this one.

## First-Response Targets

Northwind classifies every incoming incident by severity at the time of triage. Severity is assigned by the responding engineer based on observed business impact, not by the reporter's own label, although reporter context is always considered. The first-response target is the elapsed time, measured only during the coverage window, between a properly submitted ticket and the first substantive human acknowledgment from a support engineer. An automated receipt confirmation does not count.

For a critical incident — a complete production outage, a data-integrity failure, or a security event with active customer impact — the acknowledgment target under this plan is eight business hours. For a high incident, characterized by severe degradation with no reasonable workaround, the target is twelve business hours. For a moderate incident, where a workaround exists and impact is contained, the target is two business days. For a low incident covering questions, cosmetic defects, and enhancement intake, the target is three business days. These four figures differ deliberately; quoting the high-severity number for a critical incident, or the reverse, misstates the commitment.

These numbers are targets measured against the coverage window described below, not around-the-clock wall-clock guarantees. A ticket submitted near the end of a business day, or over a weekend, begins accruing elapsed time when the next covered business hour opens. Customers who require shorter acknowledgment windows, weekend coverage, or telephone escalation should review the higher service plans, which carry faster targets and broader coverage.

## Coverage Window

Support under this plan is delivered during standard business hours only. The covered window is Monday through Friday, from nine in the morning to six in the evening in the customer's registered local time zone, excluding Northwind-observed regional holidays — a span that this tier treats as the only billable response time. Time that elapses outside this window — evenings, weekends, and holidays — does not count against any first-response or restoration target.

Because coverage is business-hours only, customers should plan change windows, migrations, and high-risk deployments to begin early in a covered day so that adequate covered time remains should an issue arise. Tickets may be submitted at any hour through the eligible channels, but the clock advances only during covered hours. The registered time zone of record is captured at provisioning and can be updated by a named contact through the support portal; the most recently confirmed time zone governs all calculations.

## Restoration Targets

Restoration is the point at which the affected service is returned to normal operation, whether through a permanent fix or a stable, documented workaround that removes material business impact. Restoration targets are distinct from first-response targets and are likewise measured only within the coverage window.

For a critical incident, the time-to-restore target under this plan is three business days from the moment the incident is confirmed and correctly classified — a figure not to be confused with the eight-business-hour acknowledgment commitment, which concerns only the first reply. For a high incident, the restoration target is five business days. For moderate and low items, restoration is addressed through the standard maintenance and release cycle rather than against a fixed restoration clock, and timing is communicated case by case.

Restoration targets assume the customer provides timely access, diagnostic information, and a reachable named contact for the duration of the incident. Periods during which Northwind is waiting on customer input, credentials, or a maintenance approval are excluded from the elapsed-time calculation. Root-cause analysis for critical incidents is summarized in a written follow-up after restoration, on request.

## Channels and Named Contacts

Under this plan, support is delivered through two channels: email and the customer support portal. Tickets may be opened, updated, and tracked through either channel, and the portal provides the authoritative status of record for every case. Telephone support and live chat are not included at this level; customers requiring real-time voice escalation should consider a higher plan that adds those channels.

Each account at this level may designate up to two individuals as authorized contacts permitted to open and escalate support cases. Those authorized individuals are the people whose tickets count toward the response and restoration targets in this document. Requests arriving from anyone outside that roster may be accepted at Northwind's discretion but are not covered by these commitments. The roster can be rotated by submitting a portal request from an existing authorized individual or an account administrator; changes take effect on confirmation.

## Uptime Credits

Northwind measures monthly availability of the production service and publishes the calculation method in the customer portal. If measured availability for a calendar month dips beneath the floor that applies to this plan, namely ninety-nine and one-half percent, the affected account becomes eligible for a service credit against the following invoice. Availability is computed excluding scheduled maintenance windows announced in advance and excluding downtime attributable to customer-side configuration, third-party dependencies, or force-majeure events.

To claim a credit, an authorized contact must submit a request through the portal within thirty days of the close of the affected month, referencing the relevant incident records. Credits are the sole and exclusive remedy for availability shortfalls under this plan and do not stack with other negotiated remedies. Northwind reviews each claim against its internal availability monitoring and confirms the credit amount before applying it. Customers seeking a higher availability commitment, a lower credit threshold, or financial remedies beyond invoice credits should contact their account manager to discuss an upgraded plan.
