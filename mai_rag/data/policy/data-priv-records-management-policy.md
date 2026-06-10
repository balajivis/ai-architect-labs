---
title: Records Management Policy
doc_id: data-priv-records-management-policy
owner: Chief Compliance Officer
last_updated: 2026-04-20
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Records Management Policy

## 1. Overview

This policy establishes how Northwind Technologies **manages the lifecycle** of all business records — creation, classification, retention, archival, and destruction. "Records" include email, documents, databases, log files, and any information with business, legal, or regulatory value.

**Scope**: This policy applies to:
- All employees, contractors, and authorized third parties
- All Northwind systems (cloud storage, email, databases, file servers)
- Both personal data (GDPR-regulated) and non-personal business records

**Distinction from Anonymization**: See the **Anonymization & Pseudonymization Standard** for how to reduce privacy risk of personal data *before* retention/deletion. This policy addresses how to manage records *after* classification and retention periods are set.

## 2. Records Classification and Lifecycle

All records at Northwind follow this lifecycle:

```
CREATE → CLASSIFY → RETAIN → ARCHIVE → DELETE
  ↓         ↓          ↓         ↓         ↓
Define  Assign risk   Store   Transfer  Destroy
purpose  level &       in live  to       per
         retention     systems  cold     schedule
                                storage
```

### 2.1 Creation and Classification

When a record is created (email, document, database entry), the owner must:
1. **Classify** it using the **Data Classification & Retention Policy** (Public, Internal, Confidential, Restricted)
2. **Assign retention period** based on the **Detailed Data Retention Schedule** (3 years, 5 years, 7 years, etc.)
3. **Document the reason**: Why is this record being kept? (contract requirement, legal hold, audit trail, etc.)

**Responsibility**: Data owner (typically the creator or their manager).

### 2.2 Active Retention Phase (Live Storage)

Records are kept in **live storage** (on-access, indexed, searchable) for their **active retention period**:

- **Email**: Indefinite in live inbox; auto-archived after 7 years inactivity
- **Contracts**: Retained in contract management system (live) for contract duration + 1 year
- **Payroll records**: Retained in payroll system (live) for 2 years; then archived
- **Backup copies**: Retained for 90-day backup cycle; older backups deleted per schedule
- **Database records**: Retained in production database until retention period ends

**Access during active retention**: Full search, edit, and retrieval.

### 2.3 Archival Phase (Cold Storage)

When a record **exceeds active retention** but must still be kept (per legal hold, audit requirement, or extended retention):

1. **Move to archive system** (separate from live systems; lower cost)
2. **Encrypt** (if Confidential/Restricted classification)
3. **Document archive location** (where it's stored; metadata in indexing system)
4. **Restrict access** (only compliance/legal teams; audit all access)

**Archival storage**:
- **Email**: Move to email archive (separate tier in Microsoft 365, Google Workspace)
- **Documents**: Move to cold storage (AWS Glacier, Azure Archive tier, on-premise tape)
- **Databases**: Create read-only snapshots; store on archive media; encrypt with retention policy
- **Logs and backups**: Compress and move to storage designed for long-term retention

**Duration**: Typically 1–10 years depending on the record type and legal driver.

### 2.4 Deletion Phase

When the **retention period expires**, records must be **destroyed** per the method in **Detailed Data Retention Schedule**:

- **Public/Internal data**: Permanent deletion (OS-level delete, overwrite if repurposing media)
- **Confidential data**: Cryptographic wipe (NIST 800-88 standard)
- **Restricted data**: NIST 800-88 wipe + certificate of destruction + Chief Privacy Officer attestation
- **Physical records**: Shredding by certified vendor (Chain of Custody documented)

**Verification**: After deletion, IT must provide evidence (log entry, certificate, hash verification) to the Compliance Team.

## 3. Specific Record Types and Retention

### 3.1 Email Management

| Record Type | Retention | Location | Access |
|---|---|---|---|
| **Active mailbox** (live emails) | Indefinite (user managed) | Microsoft 365 / Google Workspace | Sender/recipient + IT |
| **Auto-archived email** (>7 yrs inactivity) | 3 additional years (total 10 yrs from send date) | Email archive tier | Compliance/Legal only |
| **Deleted emails** (user-deleted) | 60 days (retention hold) | Deleted items folder | User (recovery window) |
| **Permanently deleted emails** | Deleted per tenant recycling (30 days) | Purged from all systems | N/A (gone) |

**Email hold for litigation**: If litigation is filed, all employee emails in scope are placed on a **Legal Hold**; auto-deletion is disabled; retention extends indefinitely until Chief Counsel releases the hold.

### 3.2 Database Records

| Record Type | Retention | Storage | Action at End |
|---|---|---|---|
| **Customer account data** (name, email) | 5 years + LAD | Active database (live) | Right of erasure may apply (GDPR) |
| **Customer usage logs** (API calls) | 90 days | Active database; older purged | Permanent deletion from live; backups auto-cycle |
| **Backup copies** (snapshots) | 90 days (3-month rotation) | S3/Blob cold storage | Cryptographic wipe of media |
| **Transactional audit logs** (who changed what) | 2 years | Active database; then archive | Archive at 2-year mark; delete at 5 years |

**Deletion method**: See **Detailed Data Retention Schedule** for specific database record types and methods.

### 3.3 Document Management

| Record Type | Retention | Storage | At End of Retention |
|---|---|---|---|
| **Contracts** | 7 years from end | OneDrive/SharePoint (live) | Secure deletion (checked by Compliance) |
| **Financial records** (invoices, expenses) | 7 years from date | OneDrive/SharePoint (live) | Secure deletion |
| **Meeting notes & agendas** | 1 year | OneDrive/SharePoint (live) | Permanent deletion (user choice) |
| **Design docs & specs** | 5 years | GitHub/Confluence (live); archive to cold storage at 2 yrs | Permanent deletion from archive |

**Cloud storage auto-deletion**: Microsoft OneDrive and Google Drive can be configured to auto-delete files older than retention period. Northwind enables auto-delete for Confidential/Restricted data; users manage Internal/Public data.

### 3.4 Access Logs and Monitoring Data

| Record Type | Retention | Storage | Destruction Method |
|---|---|---|---|
| **VPN access logs** | 90 days | SIEM (Splunk) | Automatic purge after 90 days |
| **Cloud audit logs** (AWS CloudTrail, Azure Activity) | 90 days (live); 2 years (archive) | CloudTrail S3 / Activity Log archive | Automatic deletion from archive at 2-year mark |
| **Application logs** (error, debug) | 30 days | Log aggregation (Datadog) | Automatic expiration per Datadog SLA |
| **Network IDS logs** | 30 days | Splunk (SIEM) | Automatic purge |
| **Security incident logs** | Per **Incident Response Runbook** severity (Sev-1 = 7 yrs; Sev-2+ = 3 yrs) | Archive (encrypted) | Secure deletion at end of retention |

**Audit logs during investigation**: Logs related to an active incident are **held** (not auto-purged) until the incident is resolved + 30 days.

## 4. Legal Holds

### 4.1 Legal Hold Initiation

If litigation is anticipated or pending, the **General Counsel** issues a **Legal Hold Notice** in writing:

**Elements**:
- Case name or legal matter description
- Records affected (data sets, systems, email accounts, document folders)
- Hold duration (until Chief Counsel issues release notice)
- Responsible teams (IT, engineering, finance, etc.)

**Example**: "All emails from Alice Smith (alice@northwind.com) and the Finance team for the period Jan 2024–Mar 2024 are held. Do not delete or purge. IT will place a retention lock on these email accounts."

### 4.2 Effect of Legal Hold

When a legal hold is in effect:
- **Retention periods are suspended** (the record cannot be deleted until hold is released)
- **Auto-deletion is disabled** (email auto-archive, database record auto-purge stopped)
- **Backup cycles are extended** (backup copies retained longer for potential recovery)
- **Access restrictions may be tightened** (only authorized legal team; audit all access)

### 4.3 Hold Release and Removal

Once the legal matter is resolved, Chief Counsel issues a **Hold Release Notice**:
- **Effective date**: Usually 30 days after notice (grace period for any remaining legal needs)
- **Records released**: Normal retention/deletion resumes for affected records
- **Verification**: IT confirms hold is removed from all systems

## 5. Third-Party and Vendor Records

### 5.1 Vendor Records and Data Processor Records

Records created by or on behalf of **Data Processors** (vendors like AWS, Salesforce) follow vendor retention policies:

**Northwind as Controller**:
- Northwind specifies retention requirements in the **Data Processing Agreement (DPA)**
- Vendor must honor Northwind's retention schedule (e.g., "retain customer data for 5 years, then delete")
- Vendor must provide evidence of deletion (certificate, log entry)

**Example**: AWS processes Northwind customer data. DPA specifies: "Delete backups after 90 days." AWS complies and provides deletion certificate.

### 5.2 Vendor Records Held by Northwind

Records from vendors (e.g., vendor security assessment, contract, SOC 2 report) are retained per **Detailed Data Retention Schedule**:

- **Vendor contract**: 5 years post-termination
- **Vendor security assessment**: 2 years (refresh annually for active vendors)
- **Vendor incident report**: 3–7 years (per severity; see **Incident Response Runbook**)

## 6. Records Management System and Tools

### 6.1 Tools Used

| System | Records Stored | Retention Management |
|---|---|---|
| **Microsoft 365** (OneDrive, SharePoint, Teams) | Documents, presentations, spreadsheets | Auto-delete files after 3+ years inactivity (configurable per classification) |
| **Google Workspace** (Drive, Docs, Sheets) | Documents | Auto-delete after 3+ years inactivity (configurable) |
| **Email (Microsoft 365 / Google)** | Email messages | Auto-archive after 7 years; auto-delete archived after 10 years total |
| **GitHub** (code repositories) | Source code, ADRs, change logs | Indefinite (code is living record); merge branches deleted after 30 days |
| **Confluence/Wiki** (documentation) | Internal docs, runbooks | Indefinite (living docs); archive old spaces after 1 year inactivity |
| **Jira/Issue Tracking** | Engineering issues, tickets | Closed issues auto-archived after 2 years; kept indefinitely if contract-dependent |
| **Splunk / SIEM** | Security/audit logs | Auto-purge after retention period (30–90 days; configurable) |
| **S3 / Azure Blob (backups)** | Database backups, file archives | Lifecycle policies: delete after 90 days; archive to Glacier after 30 days |
| **PagerDuty** (on-call events) | Incident logs | Retain for 2 years (searchable); auto-purge after 5 years |

### 6.2 Automating Deletion and Retention

Northwind uses **automated lifecycle policies** to reduce manual deletion work:

- **Cloud storage**: S3 Lifecycle Policies, Azure Blob retention policies, OneDrive/Google auto-delete
- **Databases**: Scheduled SQL jobs (run nightly) to mark records as deleted, then purge after grace period
- **Email**: Exchange Online Retention Policies, Gmail automatic purge
- **Logs**: SIEM and log aggregation tools configured with auto-purge schedules

**Manual verification**: Compliance Team audits automated deletion logs quarterly to confirm records were deleted per schedule.

## 7. Roles and Responsibilities

| Role | Responsibility |
|------|-----------------|
| **Data Owner** (department head) | Classify records; set retention period; approve legal holds for records in their domain |
| **Records Manager** (Chief Compliance Officer) | Policy owner; audit compliance; coordinate legal holds; approve retention exceptions |
| **IT/Systems Admin** | Configure retention policies in systems; execute deletion per schedule; maintain deletion evidence |
| **Chief Counsel** | Issue legal holds; release holds; advise on litigation-related record holds |
| **Chief Privacy Officer** | Ensure GDPR compliance; oversee right-of-erasure requests; validate deletion of sensitive data |
| **All Employees** | Mark records with appropriate retention period; do not delete records manually (use system retention) |

## 8. Annual Audit and Compliance

The **Compliance Team** audits records management annually:

- **Sample 50+ records** across systems; verify retention period is correct per **Data Retention Schedule**
- **Validate deletion logs** (confirm records were deleted at end of retention)
- **Check for orphaned holds** (legal holds that remain in place after litigation ends)
- **Test compliance** with data subject rights (access, deletion requests honored per timelines)
- **Report findings** to Chief Compliance Officer and Board

**Non-compliance** (records not deleted, retention period not set, legal hold not released) triggers:
- Written notice to data owner
- 30-day remediation period
- Escalation to CEO if not remediated

---

**Document owner:** Chief Compliance Officer  
**Last approved:** 2026-04-20 by Compliance Leadership  
**Next review:** 2027-04-20
