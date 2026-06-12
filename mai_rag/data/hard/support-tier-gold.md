---
title: Northwind Support Plan — Gold Tier SLA
doc_id: support-tier-gold
owner: Customer Success
last_updated: 2026-02-10
status: active
classification: public
supersedes: ""
superseded_by: ""
---

## Scope — this plan tier (Gold)

This document defines the service-level commitments for accounts subscribed to the Gold support plan at Northwind Technologies. It applies to all production environments covered under an active Gold subscription and to the contacts designated by the customer in their account profile. The commitments described here govern response timing, coverage hours, restoration objectives, communication channels, and service credits.

This plan is one of several support tiers Northwind offers. Customers should confirm which plan their organization holds before relying on any specific commitment, because the targets in each tier document use the same structure and differ only in their numeric values. Where this document refers to "the plan," "this plan," or "your plan," it means the tier named in the title and in this Scope line. Nothing in this document modifies the master services agreement; in the event of a conflict, the executed contract controls.

The commitments below are stated as targets and apply during the defined coverage window unless explicitly noted otherwise. All times are measured from the moment a qualifying ticket is received through an approved channel and acknowledged by the Northwind support intake system. Throughout this document a single severity scale is used: Priority 1 through Priority 4 (P1–P4). "Severity" and "priority" refer to the same scale, and a "Severity-1" incident means a P1 incident.

## First-Response Targets

First response means the first substantive human acknowledgment of a reported issue, including assignment to an engineer and confirmation that investigation has begun. Automated receipt confirmations do not count as first response.

For a Priority 1 (P1) incident — defined as a complete loss of production service, a critical security exposure, or a total outage affecting all users with no available workaround — the first-response target is **1 business hour** from the time the ticket is received within the coverage window. If a P1 is submitted outside the coverage window, the response clock begins at the start of the next covered period.

Lower-priority issues carry longer first-response targets: P2 (major degradation with a partial workaround) targets 4 business hours, P3 (minor issue) targets 1 business day, and P4 (informational or cosmetic) targets 2 business days. These lower-priority targets are consistent across Northwind support plans; the differentiating commitment for this plan is the P1 first-response number stated above. Customers escalating an issue should select the severity accurately, as the first-response clock is keyed to the severity assigned at intake. Northwind reserves the right to reclassify severity after triage, with notice to the named contacts.

## Coverage Window

Support under this plan is delivered on a **24x5** basis: around-the-clock coverage Monday through Friday, in the customer's primary contracted time zone as recorded in the account profile. Coverage runs continuously from 00:00 Monday to 23:59 Friday, including overnight hours on covered days. Weekends and Northwind-observed regional holidays fall outside the coverage window.

"Business hour" and "business day," as used throughout this document, are measured only within the coverage window. A business hour is one elapsed clock hour during covered time. A business day is one full covered service day. Time accrued outside the coverage window does not count toward any target. For example, a P1 received late Friday with unresolved time remaining will have its remaining clock resume at the start of the next covered day. Customers requiring continuous weekend and holiday coverage should review the higher tiers, which extend the coverage window accordingly.

## Restoration Targets

Restoration means returning the affected production service to a working state, which may include a stable workaround that removes the customer-facing impact while permanent remediation continues. Restoration is distinct from first response and from permanent root-cause resolution.

For a P1 incident under this plan, the restoration target is **1 business day** from the time the incident is confirmed as P1 by Northwind triage. This target reflects the priority handling, escalation paths, and engineering resources assigned to accounts on this plan. Restoration targets for lower priorities are longer and are communicated during triage based on impact and scope.

Restoration targets are objectives pursued in good faith and are not guarantees of a specific outcome by a specific instant. Factors outside Northwind's reasonable control — including customer-side configuration, third-party provider outages, or force-majeure events — may extend restoration and pause the applicable clock for the duration of the external dependency. Northwind will document any such pause and notify the named contacts. Throughout an active P1 incident, Northwind provides status updates to the named contacts at regular intervals until the service is restored or a workaround is in place.

## Channels and Named Contacts

Customers on this plan may open and manage support requests through the following channels: **email, the support portal, telephone, and Slack Connect**. All four channels feed the same intake queue and are eligible to start the first-response clock. For fastest handling of a P1, Northwind recommends opening the ticket through the portal or by phone and confirming the priority at the time of submission.

Each account on this plan may designate up to **10 named contacts** who are authorized to file requests, receive status updates, and approve priority classifications. Named contacts are managed in the account profile and may be updated by the customer's administrator at any time. Requests originating from individuals who are not named contacts may be accepted at Northwind's discretion but do not carry the response commitments described here until validated against the named-contact list. Customers needing additional named contacts should contact their Customer Success representative to discuss available options.

## Uptime Credits

Northwind targets high availability for production services under this plan. When measured monthly availability for a covered production service falls **below 99.9%**, the affected account becomes eligible to request service credits in accordance with the credit schedule in the master services agreement.

Credit eligibility is assessed per calendar month and per covered service. Availability is calculated by Northwind using its standard monitoring methodology, excluding scheduled maintenance windows announced in advance, customer-caused outages, and downtime attributable to factors outside Northwind's reasonable control. To claim a credit, a named contact must submit a request through an approved channel within 30 days of the end of the affected month, including the relevant incident references. Credits are applied to future invoices, are the customer's sole and exclusive remedy for availability shortfalls, and do not accrue as cash refunds. The credit threshold and schedule are specific to this plan tier; other tiers publish their own thresholds.
