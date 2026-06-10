---
title: Litigation Hold Procedure
doc_id: legal-litigation-hold-procedure
owner: Legal & Risk
last_updated: 2026-06-09
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Litigation Hold Procedure

## Purpose
This procedure ensures that Northwind Technologies preserves all electronically stored information (ESI) and documents relevant to legal disputes, regulatory investigations, or threatened litigation. Failure to preserve evidence can result in severe sanctions, including default judgment or adverse inference.

## 1. When a Hold Is Triggered

A litigation hold is initiated when Northwind receives:

1. **Demand letter** or notice of intent to sue
2. **Subpoena** or discovery request from court, regulator, or government agency
3. **Investigation notice** from EEOC, DOJ, OSHA, FTC, state attorney general, or equivalent
4. **Threatened litigation** (email or oral notice of intent to sue)
5. **Board/CEO direction** that legal action is anticipated
6. **Regulatory audit** or investigation that may lead to litigation

**Scope**: The hold applies to all documents, emails, chat messages, files, and ESI that are **or reasonably could be** relevant to the dispute, even if not yet requested.

## 2. Hold Notice & Communication

**Timing**: General Counsel issues a litigation hold notice **within 1 business day** of trigger.

**Parties Notified**:
- All employees likely to possess relevant documents (determined by General Counsel)
- IT Security & Infrastructure team (to suspend auto-deletion policies)
- Finance & HR (for employee, budget, and vendor records)
- VP Engineering (for code repositories and design documentation)
- Data Governance team (to freeze any automated data purging)

**Hold Notice Template**:

```
PRIVILEGED AND CONFIDENTIAL — ATTORNEY-CLIENT COMMUNICATION

RE: LITIGATION HOLD NOTICE — [Case/Matter Name]

A legal matter has arisen involving Northwind Technologies. You may 
possess documents relevant to this matter. You are instructed to:

1. Cease all destruction and deletion of documents, emails, and 
   files related to [brief matter description]
2. Preserve all communications with [parties involved], dated 
   [relevant period]
3. Do not discuss this matter outside of Legal and executive 
   leadership
4. Confirm receipt of this notice within 24 hours
5. Report any document destruction that occurred before this notice 
   to Legal immediately

This is a legal hold. Violation may result in sanctions or 
disciplinary action.

— General Counsel
```

## 3. Scope of Preservation

The hold covers:

| Category | Scope | Retention Method |
|---|---|---|
| **Email** | All emails to/from relevant parties during relevant period | Suspend auto-deletion; preserve in original format |
| **Chat** (Slack, Teams, etc.) | Direct messages, channel messages involving relevant parties | Export and preserve as PST or native format |
| **Documents** | Word, Excel, PowerPoint, PDFs, design files related to the matter | Lock files in shared drives; disable access revocation |
| **Databases** | Customer records, financial records, employee records | Take snapshot/backup; preserve in original format |
| **Source Code & Repos** | Code commits, pull requests, issue trackers (GitHub, JIRA) | Preserve repository state; disable auto-cleanup |
| **Cloud Storage** | OneDrive, Sharepoint, AWS S3 buckets with relevant data | Disable lifecycle policies; preserve bucket versions |
| **Mobile & Personal Devices** | Emails and messages on personal phones if work-related | Employee must preserve via backup or forwarding to work email |
| **Backup Systems** | Existing backups (tape, snapshot) relevant to the period | Preserve and catalog; do not overwrite |

## 4. Reasonable Search Approach

To avoid over-preservation and to target resources, Legal defines the "reasonable search":

1. **Custodians** — Identify individuals (10–30 typical) likely to have relevant documents
2. **Time period** — Define relevant date range (e.g., Jan 1, 2022 – Dec 31, 2024)
3. **Keywords** — Identify 5–10 relevant terms (party names, product names, incident dates)
4. **Systems** — Specify which systems to search (email, shared drives, chat, code repos, databases)

**Example**: "Search email and Slack of [custodians] for messages from Jan 2024 onwards containing 'DataBridge', 'customer complaint', or 'outage'."

## 5. IT & Infrastructure Compliance

**IT Security must**:
- Suspend email auto-deletion policies for affected custodians
- Disable cloud storage lifecycle policies (S3 expiration, OneDrive auto-purge)
- Document the hold with backup system administrators
- Confirm all backups are preserved and not overwritten
- Provide a list of all systems affected to Legal for audit

**Timeline**: IT confirms compliance within 3 business days.

## 6. Custodian Acknowledgment

Each employee named in the hold must:
1. Acknowledge receipt of the hold notice within 24 hours (email reply to Legal)
2. Confirm they understand the scope of preservation
3. Report any documents already destroyed (before the notice) to Legal
4. Comply with the hold until explicitly released by General Counsel

**Failure to comply** may result in disciplinary action, up to and including termination, and may expose Northwind to sanctions for failure to preserve.

## 7. Ongoing Preservation & Release

**During Hold**:
- No destruction, deletion, or purging of documents
- New documents created during hold period are also preserved
- Regular (monthly) audit of custodian compliance
- General Counsel tracks all hold-related costs (IT, archival, legal review)

**Modifying the Hold**:
- If case is dismissed or matter is resolved, General Counsel issues a **release letter** terminating the hold
- Partial releases are possible if a sub-issue is resolved but broader litigation continues
- Hold may be **expanded** if discovery reveals additional relevant data or custodians

**Release Letter**:

```
CONFIDENTIAL — ATTORNEY-CLIENT COMMUNICATION

RE: RELEASE OF LITIGATION HOLD — [Case/Matter Name]

The legal matter referenced in our hold notice of [date] has been 
resolved / is no longer anticipated. Therefore, effective [date]:

1. The litigation hold is RELEASED
2. Normal document retention and destruction policies resume
3. Email auto-deletion, cloud lifecycle policies, and backup 
   purging may resume
4. This release applies to [custodians] and [systems]

Please acknowledge receipt and confirm resumption of normal 
policies within 3 business days.

— General Counsel
```

## 8. Privileged & Confidential Documents

Documents created for the purpose of obtaining legal advice (work product, attorney-client communications) remain privileged even during litigation hold:
- Do not share with non-legal staff
- Do not discuss with business teams outside of need-to-know
- Mark documents "ATTORNEY-CLIENT PRIVILEGE" or "WORK PRODUCT"
- Preserve separately from business documents

## 9. Data Subject Rights & GDPR Considerations

If the litigation hold affects personal data (PII) subject to GDPR or similar regulations:
- Legal coordinates with Chief Privacy Officer
- Data subject requests for deletion may be suspended during hold (see **Data Classification & Retention Policy**)
- Hold period is documented as "legal hold" in data subject rights responses
- Post-hold, any personal data not required by law is deleted

## 10. Third-Party Holds (Subpoenas & Government Requests)

If a government agency or opposing party subpoenas Northwind for documents:
1. Legal reviews the subpoena for scope, validity, and privilege objections
2. Subpoenaed documents are gathered and reviewed for privilege
3. Non-privileged documents are produced by the deadline
4. Privileged documents are logged on a privilege log (document ID, date, author, summary, privilege basis)
5. Objections are filed if subpoena is overly broad or seeks privileged information

---

**Related Policies:** Data Classification & Retention Policy; Intellectual Property Policy; Incident Response Runbook; Anti-Bribery & Corruption Policy.
