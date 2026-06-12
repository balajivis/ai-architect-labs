---
title: Northwind Security Incident Response Runbook
doc_id: incident-response-runbook
owner: IT Security
last_updated: 2026-04-12
status: active
classification: confidential
supersedes: ""
superseded_by: ""
---

# Northwind Security Incident Response Runbook

This runbook defines the authoritative method by which Northwind Technologies responds to security incidents. It applies to all systems, networks, and data processed by Northwind, including customer-facing SaaS environments, internal corporate systems, and infrastructure operated on our behalf by third parties. The runbook is owned by IT Security and is reviewed at least annually.

## Scope — confirmed and suspected security incidents

This runbook covers both **confirmed** and **suspected** security incidents. A security incident is any event that compromises, or could reasonably compromise, the confidentiality, integrity, or availability of Northwind systems or data. Examples include unauthorized access to systems, malware infection, credential compromise, data exfiltration, denial-of-service conditions, and the loss or theft of devices holding company or customer data.

A *suspected* incident is treated with the same urgency as a confirmed one until triage concludes otherwise. Anyone at Northwind who observes a potential incident must report it to IT Security immediately through the on-call channel. Do not attempt independent investigation or remediation before reporting; uncoordinated action can destroy forensic evidence and complicate later legal assessment.

## Severity Classification

Every incident is assigned a severity level during triage. Severity drives escalation, staffing, and communication cadence.

- **SEV-1 (Critical):** Confirmed compromise of customer data, production outage affecting multiple customers, or active attacker presence in production. Executive and Legal notification is immediate.
- **SEV-2 (High):** Likely compromise of a single system or customer tenant, or a contained breach with no confirmed data loss. Legal is engaged at triage.
- **SEV-3 (Moderate):** Limited-scope events such as a single compromised internal account with no customer-data exposure.
- **SEV-4 (Low):** Policy violations, isolated malware on a managed endpoint, or near-miss events with no exposure.

Severity may be revised in either direction as facts emerge. A SEV-3 that later reveals customer-data exposure is reclassified to SEV-1 and the full notification process is reassessed.

## Response Phases (detect / triage / contain / eradicate / notify / post-mortem)

Northwind follows a fixed six-phase method. Phases may overlap, but none may be skipped.

1. **Detect.** An incident enters the process via monitoring alerts, customer reports, employee reports, or third-party notification. The on-call responder opens an incident record and assigns an Incident Commander.
2. **Triage.** The Incident Commander confirms whether an incident is real, assigns severity, and identifies affected systems and data categories. Legal is engaged at this point for any incident with potential customer-data impact.
3. **Contain.** Responders isolate affected systems to stop ongoing harm — revoking credentials, segmenting networks, disabling accounts, or quarantining hosts. Containment prioritizes stopping spread over preserving uptime.
4. **Eradicate.** The root cause is removed: malware deleted, vulnerabilities patched, attacker footholds closed, and compromised credentials rotated. Systems are validated as clean before restoration.
5. **Notify.** Internal and external notifications proceed per the Regulatory Notification section below. Notification only begins once Legal has assessed obligations.
6. **Post-mortem.** A structured review captures timeline, impact, root cause, and corrective actions.

## Regulatory Notification (process only)

When an incident involves personal or customer data, Northwind may have an obligation to notify regulators, affected customers, and other parties. **Notification timing and content are determined by the Legal team based on the nature of the data, the jurisdictions involved, and applicable regulation.**

The process is as follows. First, IT Security provides Legal with a factual assessment: what data was involved, how many records, which customers and jurisdictions, and the confirmed or estimated exposure window. Second, Legal evaluates which regulatory and contractual notification obligations apply. Third, Legal directs the notification — to whom, in what form, and **within the timeframe determined by Legal and applicable regulation**. IT Security and Communications execute notifications under Legal's direction.

Northwind does not maintain a single fixed notification deadline in this runbook, because obligations vary by regulation, contract, and jurisdiction. Responders must not assume or quote a deadline; the controlling timeframe for any given incident is the one Legal identifies for that incident. Premature or inaccurate external notification can itself create legal and reputational harm, so no external notice goes out without Legal sign-off.

## Scope of Retained Customer Data (see data-retention-active)

Determining the scope of a breach requires knowing what customer data Northwind holds and for how long. **All customer data retained by Northwind under the Data Retention Standard is in-scope for breach notification.** Responders must consult the active Data Retention Standard (doc_id: `data-retention-active`) to establish the retention window that defines how far back potentially exposed records may extend.

Because retained customer records remain in-scope for the full retention period defined in that standard, the breach assessment must account for the entire window — not merely data created during the incident timeframe. When scoping affected records, pull the controlling retention period from `data-retention-active` and apply it to the affected data stores. Do not rely on memory or this runbook for the figure; the retention period is owned and maintained by the Data Privacy team in that document.

## Third-Party / Vendor Incidents

Some incidents originate with a third party — a subprocessor, hosting provider, or SaaS vendor that handles Northwind or customer data. These are handled under this runbook with two additions.

First, the Incident Commander identifies the vendor relationship and pulls the vendor's security posture from the vendor onboarding security review on file. That review establishes what data the vendor holds, contractual notification commitments, and the security controls assessed at onboarding. A vendor without a current security review is escalated to Procurement and Legal immediately.

Second, contractual notification timelines owed *by* the vendor *to* Northwind, and *by* Northwind *to* its customers, are reconciled by Legal as part of the Notify phase. Northwind's own notification obligations are not waived because the root cause sat with a vendor.

## Post-Incident Review

Within ten business days of closing a SEV-1 or SEV-2 incident, the Incident Commander convenes a post-incident review. The review is blameless and produces a written record: detection-to-containment timeline, root cause, customer and data impact, regulatory actions taken under Legal's direction, and a prioritized list of corrective actions with owners and due dates. Corrective actions are tracked to completion by IT Security, and recurring themes are fed back into this runbook at the annual review.