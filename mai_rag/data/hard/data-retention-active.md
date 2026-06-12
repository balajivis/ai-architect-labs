---
title: Northwind Customer Data Retention Standard
doc_id: data-retention-active
owner: Data Privacy Office
last_updated: 2026-03-22
status: active
classification: confidential
supersedes: data-retention-superseded
superseded_by: ""
---

# Northwind Customer Data Retention Standard

This Standard defines how Northwind Technologies retains and disposes of customer data across its production estate and backup systems. It is the authoritative source for retention periods, deletion methods, and data-subject request handling. All engineering, infrastructure, and customer-success teams that store or process customer data must conform to this Standard. Exceptions require written approval from the Data Privacy Office and are logged in the exceptions register.

## Scope — customer PII held in production and backups

This Standard applies to all customer personally identifiable information (PII) that Northwind processes on behalf of its B2B SaaS tenants. In scope are: account identifiers, contact records, authentication material, usage telemetry tied to an identifiable person, support correspondence, and any uploaded customer content that contains PII. The Standard covers data wherever it physically resides — primary production databases, read replicas, object storage, search indices, message queues, and all backup tiers.

Out of scope are aggregated or fully anonymized datasets from which no individual can be re-identified, and Northwind's own employee records, which are governed separately by the HR records policy. Tenant-configured retention overrides may shorten — but never lengthen — the periods defined here. Where a contractual Data Processing Addendum specifies a shorter period, the contract prevails and the shorter period is applied.

## Retention After Account Closure (24 months)

When a customer account is closed — whether through voluntary cancellation, non-renewal, or termination for cause — Northwind retains the associated customer PII for **24 months** from the effective closure date. During this window the data is moved to a restricted, closed-account partition that is inaccessible to standard application paths and is reachable only by the Data Privacy Office and a small set of break-glass operators.

The 24-month window exists to support reactivation requests, billing disputes, tax reconciliation, and legitimate legal hold. At the expiry of 24 months, the data is rendered irreversibly unrecoverable through the deletion method described below. No customer PII tied to a closed account is retained in production beyond 24 months. Reactivation within the window restores the account to active status and resets retention to the active-account lifecycle.

Where a legal hold is in force, deletion is suspended for the affected records only, and the hold is documented in the exceptions register with an owner and review date. Release of the hold restarts the deletion clock from the release date.

## Backup Retention (35-day rolling)

Production data is captured in encrypted backups on a **35-day rolling** schedule. Backups older than 35 days are automatically expired and overwritten. This means that once a record has been deleted from production, any residual copy in backup media is purged within at most 35 days as the rolling window advances past the last backup that contained it.

Backups are stored encrypted at rest with per-tenant key separation, so that expiry of a tenant's keys (see deletion method) renders backup copies cryptographically inaccessible even before physical overwrite completes. The 35-day window is fixed and is not configurable per tenant. Restore operations from backup are permitted only for disaster recovery and are logged; a restore must never reintroduce data whose retention period has lawfully expired, and the restore runbook includes a post-restore reconciliation step to re-apply pending deletions.

## Audit-Log Retention (7 years)

Audit logs — records of who accessed what, administrative actions, authentication events, and deletion confirmations — are retained for **7 years** to satisfy compliance, regulatory, and contractual obligations. Audit logs are deliberately excluded from the customer-PII retention windows above because they are evidentiary records of processing rather than the customer data itself.

Audit logs are minimized so they reference subjects by stable internal identifiers rather than storing raw PII. They are held in append-only storage with integrity protection and are themselves subject to access controls and review. The 7-year period is the floor; logs may be retained longer only where a specific legal hold or regulatory directive requires it, and any such extension is recorded.

## Deletion Method (crypto-shredding)

Irreversible deletion at Northwind is achieved through **crypto-shredding of per-tenant encryption keys**. All customer PII is encrypted with tenant-scoped keys held in the key-management service. To delete data irreversibly, Northwind destroys the relevant per-tenant key material; without the key, the ciphertext in production, replicas, indices, and backups is permanently unrecoverable.

Crypto-shredding is preferred over physical erasure because it acts atomically across distributed and replicated storage, including backup media that cannot be selectively overwritten on demand. Key destruction is a privileged, dual-authorized operation, and each shred event is recorded in the audit log with the tenant, scope, timestamp, and authorizing operators. After a shred, a verification job confirms that no live key can decrypt the affected ciphertext.

## DSAR Fulfillment (30 days)

Northwind fulfills verified Data Subject Access Requests (DSARs) — including access, rectification, and erasure requests — within a **30 calendar day** SLA from the date the request is verified. The Data Privacy Office triages incoming requests, verifies the requester's identity, and coordinates with engineering to assemble or erase the relevant records.

For erasure requests, fulfillment uses the irreversible deletion method defined in this Standard where the request scope aligns to tenant key boundaries, or targeted record deletion followed by backup expiry on the rolling backup schedule otherwise. Complex requests may be extended once, with notice to the data subject, where permitted by applicable law. Every DSAR and its disposition is logged.

## Cross-Reference: Incident Response

When a security incident affects retained customer data, the Incident Response Plan governs breach assessment and notification. Incident responders scope the population of potentially exposed records by reference to the retention periods defined in this Standard. In particular, when a breach touches data belonging to closed accounts, responders must determine how far back retained PII may extend by applying the closed-account retention window defined in the "Retention After Account Closure" section above — the incident plan deliberately does not restate that figure, so that the single authoritative period governs. Responders must consult this Standard's current figures when sizing affected populations; the Data Privacy Office is the point of contact for retention questions during any incident.
