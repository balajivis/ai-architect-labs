---
title: Northwind Support Plan — Platinum Tier SLA
doc_id: support-tier-platinum
owner: Customer Success
last_updated: 2026-02-10
status: active
classification: public
supersedes: ""
superseded_by: ""
---

# Northwind Support Plan — Platinum Tier SLA

This document defines the service commitments Northwind Technologies extends to customers enrolled in this support plan. It describes response targets, coverage hours, restoration objectives, communication channels, and the conditions under which uptime credits apply. All commitments below are measured against Northwind's incident-management system of record and reconciled monthly during the account review.

## Scope of this plan

This document governs one support plan only. The commitments stated here apply exclusively to accounts that hold the matching active entitlement on their order form. Customers whose order form carries a different entitlement should refer to the document that matches it, as targets differ at each level and are not interchangeable. Where a customer holds multiple subscriptions, the plan attached to the affected subscription determines which targets apply to a given incident.

The remainder of this document states each commitment as a plain sentence so that it can be quoted directly into account communications without further interpretation. Numbers are authoritative as written.

## First-response targets

A first response is the first substantive human acknowledgement of a logged incident — not an automated receipt. The clock starts when the incident is created through any approved channel and stops when an engineer posts an initial assessment or request for information.

The first-response target for a Severity-1 (P1) incident under this plan is 15 minutes. This is the headline commitment and is measured around the clock, every day of the year, with no exclusion for weekends or holidays.

Lower-severity incidents carry longer first-response targets. The first-response target for a Severity-2 (P2) incident is 1 hour. The first-response target for a Severity-3 (P3) incident is 4 business hours. The first-response target for a Severity-4 (P4) request is 1 business day. Severity is assigned at intake by Northwind in consultation with the customer's named contact and reflects business impact, not the volume of affected users alone.

## Coverage window

Coverage under this plan is continuous: 24 hours a day, 7 days a week, every day of the year. First-response targets for P1 and P2 incidents are honored continuously, including nights, weekends, and public holidays in every region where the customer operates. P3 and P4 targets are measured in business hours, defined as 09:00–18:00 in the customer's primary registered time zone, Monday through Friday, excluding Northwind-observed holidays.

Continuous coverage is delivered through a follow-the-sun roster so that an incident opened at any hour reaches an engineer who is on shift rather than on call. Customers do not need to flag an incident as urgent outside business hours; the severity assigned at intake determines which coverage clock applies.

## Restoration targets

Restoration means the affected service is returned to normal operation or a workaround is in place that removes the customer-facing impact. Restoration is distinct from root-cause resolution, which may follow later through a problem record and a post-incident review.

The Severity-1 restoration target under this plan is 4 hours. Northwind commits to restoring service or providing an effective workaround within 4 hours of a P1 incident being confirmed. The Severity-2 restoration target is 8 hours. The Severity-3 restoration target is 3 business days. Severity-4 requests are addressed on a scheduled basis and do not carry a fixed restoration target.

Restoration targets are objectives measured across the trailing calendar quarter. Where a restoration target is missed because the customer was unable to provide access, diagnostic data, or a decision needed to proceed, the elapsed waiting time is excluded from the measurement. Each excluded interval is recorded in the incident timeline so that the customer can review it during the account review.

## Channels and named contacts

This plan includes access through all support channels: the support portal, email, in-product chat, a dedicated Technical Account Manager (TAM), and a 24x7 phone bridge for live incident coordination. The TAM is the standing point of contact for escalations, roadmap alignment, and quarterly service reviews, and convenes the phone bridge for any active P1.

The number of named contacts permitted under this plan is unlimited. Customers may register as many individuals as they wish to open incidents, receive notifications, and join the phone bridge, and may revise the roster at any time through the portal. For P1 incidents, Northwind recommends designating a single decision-maker on the bridge to keep restoration moving, even though the roster itself is not capped.

All channels feed the same incident queue, so the first-response and restoration clocks behave identically regardless of how an incident is raised. Phone-bridge and TAM access do not change the stated targets; they exist to accelerate coordination within them.

## Uptime credits

Northwind measures availability of the covered production service each calendar month. The availability commitment under this plan is 99.95%. If measured monthly availability falls below 99.95%, the customer becomes eligible for a service credit against the affected subscription.

Credits are calculated on a sliding scale tied to the shortfall, applied to the monthly fee for the affected service, and are the exclusive remedy for availability shortfalls under this plan. To claim a credit, a named contact must submit a request through the portal within 30 days of the end of the month in which the shortfall occurred, referencing the relevant incident numbers.

Availability excludes scheduled maintenance announced at least 72 hours in advance, force-majeure events, and outages caused by customer configuration changes outside Northwind's control. The monthly availability figure and any applicable credit are confirmed during the account review and reflected on the following invoice.