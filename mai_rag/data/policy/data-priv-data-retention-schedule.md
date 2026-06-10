---
title: Detailed Data Retention Schedule
doc_id: data-priv-data-retention-schedule
owner: Chief Compliance Officer
last_updated: 2026-04-20
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Detailed Data Retention Schedule

## 1. Purpose and Scope

This schedule specifies the **retention period** (how long data must be kept) and **destruction method** (how to safely delete it) for all data categories at Northwind Technologies. This schedule is derived from the **Data Classification & Retention Policy** and adds operational detail for each data type, system, and legal/business driver.

**Cross-reference**: See the **Data Classification & Retention Policy** for classification levels (Public, Internal, Confidential, Restricted) and **Records Management Policy** for archival, retrieval, and audit procedures.

## 2. Master Retention Schedule

All dates are measured from the **Last Activity Date** (LAD) unless otherwise noted. "Last Activity" means the last time data was modified, accessed in a business transaction, or reconfirmed as accurate.

### 2.1 Customer and Account Data

| Data Type | Classification | Retention Period | Destruction Method | Legal Driver | Notes |
|-----------|---|---|---|---|---|
| **Customer account profile** (name, email, org) | Confidential | 5 years + LAD, or contract term + 1 year, whichever is longer | Cryptographic wipe | Customer contract; SOX if public customer |  Can be anonymized after 5 years for analytics |
| **Customer contact history** (support tickets, emails) | Confidential | 3 years + LAD | Secure deletion | Customer service SLA; audit trail |  Exclude attachments if classified Restricted |
| **Customer contracts, agreements** | Confidential | 7 years + contract end (statute of limitations) | Secure deletion + physical destruction if printed | Contract law; tax code |  Legal hold extends indefinitely if litigation pending |
| **Customer billing and invoices** | Confidential | 7 years from invoice date | Secure deletion | IRS (US); local tax authority (EU) |  PDF invoices are less sensitive if payment card removed |
| **Customer usage logs** (API calls, feature access) | Internal | 90 days + LAD | Permanent deletion from live systems; backups auto-delete per 90-day cycle | SLA compliance; performance monitoring |  Aggregated/anonymized logs may be retained longer for analytics |
| **Customer API keys and secrets** | Restricted | As long as API key is active; **90 days after revocation** | NIST 800-88 compliant cryptographic wipe | Security; breach prevention |  Rotate API keys annually; invalidate on employee departure |

### 2.2 Employee and HR Data

| Data Type | Classification | Retention Period | Destruction Method | Legal Driver | Notes |
|-----------|---|---|---|---|---|
| **Employee personal file** (SSN, address, emergency contact) | Restricted | 6 years after employment end (or per state law, whichever is longer) | NIST 800-88 wipe | Labor law; tax code; I-9 verification |  Background check data: 3 years |
| **Payroll and tax records** | Confidential | 7 years | Secure deletion | IRS; state payroll authority |  W-2s must be retained per employee for audit |
| **Employee health/medical** (health insurance, wellness) | Restricted | 3 years after employment end | NIST 800-88 wipe; notify employee of destruction | HIPAA (if applicable); privacy law |  PII and health data together = Restricted |
| **Performance reviews** | Confidential | 3 years + LAD | Permanent deletion | Internal HR policy; legal defense if termination litigated |  If litigation filed, legal hold applies indefinitely |
| **Disciplinary records** | Confidential | 1 year (for first offense), 3 years (for final warnings) from incident date | Secure deletion | Employment law; internal policy |  Termination for cause: retain 7 years as legal defense |
| **Training records and certifications** | Internal | Until certification expires + 2 years | Permanent deletion | Compliance (e.g., security awareness pass) | Can be anonymized for aggregate statistics |
| **Recruiting and applicant data** | Confidential | 1 year from rejection or hire date | Permanent deletion | Equal Employment Opportunity (EEO) law; GDPR if EU/EEA applicant |  GDPR applies even to rejected applicants if EU/EEA resident |

### 2.3 Security and Audit Logs

| Data Type | Classification | Retention Period | Destruction Method | Legal Driver | Notes |
|-----------|---|---|---|---|---|
| **VPN access logs** | Internal | 90 days | Permanent deletion | Security monitoring; incident investigation |  Real-time logs: purge; archival: 30-day cycle |
| **AWS/Azure cloud logs** (CloudTrail, Activity Log) | Internal | 90 days (live), archived to S3/blob for 2 years | Permanent deletion from archive after 2 years | SOC 2; audit trail; incident forensics |  Sev-1/Sev-2 incidents: extend to legal hold duration |
| **Antivirus/EDR logs** | Internal | 90 days | Auto-purge per tool settings | Malware detection; breach investigation |  Quarantined files: retain until verified clean or legal hold |
| **Email audit logs** (sent/received metadata) | Internal | 7 years | Archival deletion per email retention | eDiscovery; SEC/SOX if public company |  Content is separate from metadata; see Email Data below |
| **Network intrusion detection (IDS) logs** | Internal | 30 days | Permanent deletion | Real-time incident response; forensics |  Extend if Sev-2+ incident detected |
| **Physical access logs** (badge swipes, door locks) | Internal | 90 days | Permanent deletion | Access control; incident investigation |  Extend if theft or unauthorized access suspected |
| **Change management logs** (code deployments, config changes) | Internal | 2 years | Permanent deletion | Audit trail; incident root cause analysis |  Production changes: retained via git history indefinitely |
| **Incident investigation reports** | Confidential | Duration of investigation + 3 years (or per legal hold) | Secure deletion | Legal defense; regulatory compliance |  During active investigation: **Restricted** classification; downgrade to Confidential post-close |

### 2.4 Email and Communications

| Data Type | Classification | Retention Period | Destruction Method | Legal Driver | Notes |
|-----------|---|---|---|---|---|
| **Employee email (live inbox)** | Internal/Confidential | Indefinite (user manages deletion) | Depends on content classification | User retention choice; legal hold if litigation |  Corporate email may be reviewed during investigations |
| **Email archive** (auto-archived after 7 years inactive) | Internal/Confidential | Total 10 years from date sent | Permanent deletion from archive | eDiscovery; SEC/SOX if public |  Active email stays in mailbox; auto-archive preserves for 3 additional years |
| **Slack and instant messages** (if used) | Internal | 90 days | Permanent deletion per workspace retention settings | Real-time collaboration; not formal record |  Retain longer if discussion involves compliance/contracts |
| **Meeting recordings** | Internal | 1 year from recording date | Secure deletion | Internal use; training; knowledge preservation |  Extend if training content is reused |

### 2.5 Financial and Tax Data

| Data Type | Classification | Retention Period | Destruction Method | Legal Driver | Notes |
|-----------|---|---|---|---|---|
| **General ledger, accounts payable/receivable** | Confidential | 7 years + end of fiscal year | Secure deletion | IRS; state tax code; accounting standards |  Balancing/closing entry in year 8 confirms completeness |
| **Bank reconciliations, statements** | Confidential | 7 years | Secure deletion | IRS audit trail; fraud prevention |  Archived statements: same retention |
| **Tax returns (corporate, state, local)** | Confidential | 7 years + indefinite if tax extended or disputed | Secure deletion (final closure) | IRS; state authority; statute of limitations |  Maintain master copy indefinitely until tax authority closes |
| **Expense reports** | Confidential | 7 years | Secure deletion | Audit trail; tax deduction substantiation |  Requires itemized receipts; see Acceptable Use Policy |

### 2.6 Vendor and Third-Party Data

| Data Type | Classification | Retention Period | Destruction Method | Legal Driver | Notes |
|-----------|---|---|---|---|---|
| **Vendor contracts and SOWs** | Confidential | 5 years post-termination or contract end + 3 years | Secure deletion | Contract law; audit trail |  Retain longer if vendor lawsuit is pending |
| **Vendor assessments, audit reports** | Confidential | 3 years from assessment date | Permanent deletion | Vendor risk management; compliance |  High Risk vendor: extend to 5 years |
| **Vendor incident reports** | Confidential | Per **Incident Response Runbook** severity: Sev-1 = 7 years; Sev-2+ = 3 years | Secure deletion | Incident history; breach patterns |  If vendor caused data breach, legal hold applies |
| **Vendor security questionnaires** | Confidential | 2 years from vendor onboarding | Permanent deletion | Vendor onboarding; risk baseline | Re-assess annually for active vendors |

### 2.7 Backup and Disaster Recovery

| Data Type | Classification | Retention Period | Destruction Method | Legal Driver | Notes |
|-----------|---|---|---|---|---|
| **Full database backups** | Classified per source data | 90 days (3-month rotation) | Cryptographic wipe of backup media | Recovery Point Objective (RPO); storage cost |  Extended backups (6+ months) require Chief Privacy Officer approval; audit trail required |
| **Incremental/differential backups** | Classified per source data | 30 days | Cryptographic wipe | Backup chaining; storage efficiency |  Cascading deletion per standard backup cycle |
| **Disaster recovery copies** (off-site, cloud-to-cloud) | Classified per source data | Matches primary backup cycle (90 days) | Cryptographic wipe of secondary media | RTO/RPO; geographic redundancy |  Geo-replicated to EU if EU/EEA data present; see Cross-Border Data Transfer Policy |
| **Test/dev copies of production data** | Classified per source data | 30 days from creation; dev copies must be anonymized after 7 days | Permanent deletion | Data minimization; prevent unauthorized exposure | Mask PII in dev/test; log all data provisioning |

### 2.8 Third-Party and Marketing Data

| Data Type | Classification | Retention Period | Destruction Method | Legal Driver | Notes |
|-----------|---|---|---|---|---|
| **Prospect/lead data** (from webform, trade shows, purchased lists) | Confidential | 2 years from last engagement OR 12 months from collection date, whichever is sooner | Permanent deletion | Consent withdrawal; GDPR/CAN-SPAM opt-out |  Must provide opt-out link; honor unsubscribe within 30 days |
| **Website analytics** (Google Analytics, Mixpanel) | Internal | 26 months | Permanent deletion | Aggregate business metrics; GDPR compliance for EU visitors |  Anonymize IP addresses after 3 months |
| **Marketing email lists and engagement data** | Confidential | 2 years from last engagement | Permanent deletion | CAN-SPAM (US); GDPR (EU); email consent |  Soft bounces: 1 year; hard bounces: immediate removal |
| **Customer testimonials and case studies** | Internal | 5 years or until customer relationship ends, whichever is longer | Permanent deletion (request from customer before use ends) | Customer consent; content licensing |  Obtain explicit consent for use; anonymize if not permitted |

## 3. Retention Exceptions and Legal Holds

### 3.1 When Retention is Extended

Retention periods listed above are **default minimums** and must be extended in the following cases:

1. **Pending Litigation or Regulatory Investigation**
   - Chief Counsel issues a **Legal Hold Notice** in writing
   - All affected data must be preserved exactly as-is; no deletion, no archival moves
   - Legal hold remains in effect until Chief Counsel issues a **Release Notice**
   - Duration: Often 3+ years; may extend indefinitely if appeal is pending

2. **Regulatory Audit or Examination**
   - If a regulator (SEC, IRS, DPA, etc.) requests data, it must be retained until the audit closes
   - Extend retention by 1 year post-closure in case follow-up questions arise

3. **Unresolved Data Subject Rights Request**
   - If a GDPR data subject contests Northwind's handling or files a complaint with a DPA, affected data must be retained until the complaint is resolved

### 3.2 Documenting Exceptions

All exceptions must be documented:
- **Exception ID** (e.g., HOLD-2026-0015)
- **Data set affected** (e.g., "customer-db-backup-2023-Q2, employee-file-alice-smith")
- **Reason** (litigation case name, regulator name, GDPR complaint ID, etc.)
- **Approval** (signed by Chief Counsel or VP Security)
- **Expected release date**

Exceptions are reviewed quarterly; overdue holds are escalated to Chief Counsel.

## 4. Data Destruction Procedures

### 4.1 Destruction Methods by Classification

| Classification | Destruction Method | Standard | Certification |
|---|---|---|---|
| **Public** | Permanent deletion from storage | Standard OS deletion acceptable | Log entry sufficient |
| **Internal** | Permanent deletion from storage + overwrite | DOD 5220.22-M or NIST 800-88 (1-pass overwrite minimum) | Log + attestation by IT |
| **Confidential** | Cryptographic wipe or 3-pass overwrite | NIST 800-88 compliant | Log + IT attestation |
| **Restricted** | Cryptographic wipe (AES-256 or better) | NIST 800-88 (approved wipe tools only) | Log + IT + Chief Privacy Officer attestation |

### 4.2 Backup Media and Hardware Decommissioning

When decommissioning storage media or cloud resources:
- **Cloud resources (S3, Azure Blob)**: Use cloud provider's cryptographic deletion APIs (not trash/recycle bin)
- **Physical hard drives**: Secure wipe using tool certified for enterprise (e.g., Blancco); if wipe fails, physical destruction (degaussing or shredding) with Certificate of Destruction
- **Hardware**: All endpoints and servers must be wiped before reuse or disposal; include in IT asset lifecycle

### 4.3 Retention of Destruction Evidence

IT must retain evidence of destruction:
- **Log entry**: Date, time, data set destroyed, method, person authorized
- **Certificate of Destruction**: For third-party destruction (e.g., hard drive shredding), retain physical or digital certificate for 3 years

Evidence is stored in IT ticketing system and reviewed annually by Compliance Team.

## 5. Delegation and Ownership

| Role | Responsibility |
|------|-----------------|
| **Data Owner** (department head) | Classify data; approve retention exceptions; authorize destruction |
| **IT/Systems Administrator** | Execute destruction; maintain audit logs; preserve evidence |
| **Compliance Team** | Monitor retention exceptions; audit annual destruction compliance; report to leadership |
| **Chief Compliance Officer** | Policy owner; approve exceptions that exceed 10 years; report to Board |

---

**Document owner:** Chief Compliance Officer  
**Last approved:** 2026-04-20 by Compliance Leadership  
**Next review:** 2027-04-20
