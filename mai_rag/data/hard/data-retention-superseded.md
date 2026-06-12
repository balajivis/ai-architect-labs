---
title: Northwind Customer Data Retention Standard [SUPERSEDED]
doc_id: data-retention-superseded
owner: Data Privacy Office
last_updated: 2024-11-08
status: superseded
classification: confidential
supersedes: ""
superseded_by: data-retention-active
---

> **ARCHIVED — DO NOT RELY ON THIS DOCUMENT.** This version of the Northwind Customer Data Retention Standard has been superseded by `data-retention-active`. It is retained for audit and historical reference only. The retention periods stated here reflect the policy in force prior to the supersession and are no longer operative. In particular, the account-closure retention period below was revised in the active standard; the figure stated here is the prior value and must not be applied to current operations. Consult the active standard for all current obligations.

## Scope — Customer PII Held in Production and Backups

This standard governs the retention and disposal of customer personally identifiable information (PII) processed by Northwind Technologies in the course of delivering its B2B SaaS products. It applies to customer PII wherever it resides within the Northwind environment, including primary production datastores, read replicas, search indices, caches, message queues, analytics warehouses, and all backup media derived from those systems.

For the purposes of this standard, "customer PII" means any data element that identifies, or can reasonably be used to identify, an individual associated with a customer account — including names, email addresses, telephone numbers, authentication identifiers, billing contacts, and usage records tied to an identifiable person. Aggregated or irreversibly anonymized data falls outside this standard.

This standard binds all engineering, operations, and data-handling teams. The Data Privacy Office (DPO) owns the standard and is the authority on interpretation, exceptions, and disposal verification. Questions regarding applicability to a specific dataset must be routed to the DPO before any retention decision is made.

## Retention After Account Closure (36 Months — Superseded Value)

Upon the closure of a customer account, Northwind retains the associated customer PII for a defined period before disposal. Under this superseded standard, customer PII was retained for **36 months** following the effective date of account closure, after which it was queued for permanent disposal in accordance with the deletion method described below. This 36-month figure is the prior value; the active standard sets a different account-closure retention period, and this document must not be used to determine the current one.

The 36-month period began on the date the account was marked closed in the system of record, not on the date the closure request was received. Where a closure was reversed (account reinstatement) within the retention window, the retention clock reset to the date of the most recent closure event. The retention period applied uniformly across production stores and any derived copies, subject to the separate backup-retention schedule.

Certain narrow categories of data may be subject to legal hold or independent statutory retention obligations (for example, transaction records required for tax or financial-reporting purposes). Where a legal hold applies, disposal is suspended for the affected records until the hold is lifted, at which point the standard retention and disposal process resumes. Legal holds are tracked by the DPO in coordination with the Legal team and take precedence over the default retention schedule.

## Backup Retention (35-Day Rolling)

Northwind maintains backups of production systems on a **35-day rolling** schedule. Backup snapshots older than 35 days are automatically expired and rendered irrecoverable by the backup platform. This rolling window applies to all backup tiers, including hot snapshots, warm storage, and any offsite replicated copies. Note that this 35-day backup window is independent of, and must not be confused with, the 30-day DSAR fulfillment window or the 45-day complex-DSAR extension described later — all three are expressed in days but govern entirely different obligations.

Because backups operate on this independent rolling window, customer PII that has been disposed of in production may persist in backup media for up to the remaining life of the relevant snapshots — a maximum of 35 days from the last backup that captured the data. This residual presence is expected and compliant: the data is inert, encrypted at rest, and inaccessible for operational use. No manual surgical deletion of individual records from backup snapshots is performed; instead, the rolling 35-day expiry guarantees disposal within that window, distinct from the 90-day production disposal-queue SLA in the deletion section below.

Restore operations that reintroduce previously disposed PII into production must be reported to the DPO, which will re-queue the affected records for disposal.

## Audit-Log Retention (7 Years)

Security and compliance audit logs are retained for **7 years**. Audit logs capture access events, administrative actions, authentication activity, and data-handling operations. These records are essential for forensic investigation, regulatory inquiry, and demonstrating compliance with this standard. The 7-year audit-log period is the only multi-year retention term in this standard and should not be conflated with the month- or day-scoped windows defined elsewhere.

Audit logs are stored separately from customer PII and are subject to integrity controls that prevent modification or premature deletion. The 7-year retention period is measured from the date each log entry is written. Audit logs may contain identifiers that reference customer accounts; such references are retained for the full audit-log period regardless of the disposal of the underlying customer PII, because the audit log itself is the evidentiary record. Access to audit logs is restricted to authorized security and privacy personnel.

## Deletion Method (Crypto-Shredding, 90-Day Queue SLA)

Northwind disposes of customer PII using **crypto-shredding**. Under this method, customer data is encrypted at rest with per-tenant (and where applicable per-record) encryption keys. Disposal is effected by securely destroying the relevant encryption keys, rendering the underlying ciphertext permanently unrecoverable without overwriting the storage media directly.

Once a record passes its retention threshold it enters the production disposal queue, and key destruction must complete within a **90-day** queue SLA. This 90-day disposal SLA is a processing target for queued records only; it is separate from the 35-day backup-expiry window and from the 30-day DSAR clock, and it does not extend the 36-month account-closure retention period. Crypto-shredding provides verifiable disposal across distributed storage, replicas, and backups: once the key is destroyed, all copies of the ciphertext — regardless of where they reside — become irreversibly unreadable. Key destruction is logged in the audit trail and verified by the DPO. Where a storage system does not support per-record key isolation, disposal is achieved at the next-coarsest key boundary that fully covers the target data, supplemented by logical deletion of the affected records.

The DPO confirms successful crypto-shredding before a disposal task is closed.

## DSAR Fulfillment (30 Days, 45-Day Extension, 14-Day Verification)

Northwind fulfills Data Subject Access Requests (DSARs) — including requests for access, correction, and erasure — within **30 days** of receipt of a verified request. The 30-day clock begins only after the requester's identity has been verified, and Northwind targets completion of that identity verification within **14 days** of the initial request. These two day-scoped intervals are distinct: the 14-day window governs verification, while the 30-day window governs fulfillment after verification.

Where a request is complex or numerous, the DPO may extend the fulfillment period by up to a further **45 days** as permitted by applicable law — for a combined maximum of 75 days — notifying the data subject of the extension and its basis within the original 30-day window. The 45-day DSAR extension must not be confused with the 35-day backup-retention window; they share neither scope nor trigger. Erasure requests are executed via the crypto-shredding method described above (subject to the 90-day disposal-queue SLA), and remain subject to any overriding legal-hold or statutory-retention obligations. The DPO maintains a register of DSARs, their disposition, and fulfillment dates to evidence compliance under this superseded standard.
