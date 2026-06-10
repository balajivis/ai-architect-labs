---
title: Records & Document Control Policy
doc_id: ops-records-document-control-policy
owner: General Counsel & Operations
last_updated: 2026-06-09
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Records & Document Control Policy

## 1. Purpose & Scope

This policy establishes standards for creating, managing, archiving, and retaining company records and documents to ensure:
- **Legal compliance**: Retention meets regulatory obligations (SEC, GDPR, HIPAA, state laws)
- **Audit readiness**: Documents available for internal/external audit and litigation discovery
- **Operational continuity**: Critical records preserved during emergencies (see Business Continuity Plan)
- **Confidentiality**: Sensitive documents protected; access controlled
- **Efficiency**: Organized systems reduce time to locate and retrieve documents

**Scope**: All company records—digital and physical—created or received by employees, contractors, and systems.

## 2. Document Classifications & Retention

### 2.1 Record Types & Retention Schedules

| Record Type | Retention Period | Storage | Responsible Party |
|---|---|---|---|
| **Financial** | | | |
| Invoices, receipts, expense reports | 7 years | Cloud archive (encrypted) | Finance |
| Tax records, 1099 forms, W-2s | 7 years | Secure file room + cloud | Finance & HR |
| Bank statements, credit card reconciliations | 7 years | Cloud archive (encrypted) | Finance |
| **Human Resources** | | | |
| Personnel files (employment, performance, discipline) | 3 years post-termination | Locked cabinet (HR office) + cloud | HR |
| Onboarding documents (SSN, I-9, tax forms) | 3 years post-termination | Locked cabinet (HR office) | HR |
| Benefit enrollment, payroll records | 7 years | Cloud archive (encrypted) | HR / Payroll |
| **Legal & Compliance** | | | |
| Contracts, NDAs, purchase agreements | Life of contract + 7 years | Cloud + legal database | General Counsel |
| Board minutes, shareholder records | Indefinite | Secure cloud + paper archive | General Counsel |
| Litigation holds (see Section 6) | Until case resolved + 2 years | Locked storage (litigation sensitive) | General Counsel |
| Compliance audit reports (SOC 2, ISO, GDPR) | 7 years | Cloud archive | VP Security |
| **Intellectual Property** | | | |
| Patents, trademarks, copyright registrations | Indefinite | Cloud + legal database | General Counsel + Engineering |
| **Technical & Operations** | | | |
| Code repositories (git history) | Indefinite | GitHub (private) | Engineering |
| Infrastructure configs, runbooks | Indefinite (or superseded version + 3 years) | GitHub + wiki | IT Ops |
| Incident reports, security logs | 2 years | Cloud (encrypted) | Security & IT Ops |
| **Customer & Commercial** | | | |
| Customer contracts, SOWs, SLAs | Life + 7 years | Cloud database | Sales / Legal |
| Customer support tickets | 2 years | Zendesk or equivalent | Customer Success |
| Customer data (incl. PII) | Per contract + legal hold; min 1 year | Encrypted cloud + local backups | VP Product & Sec. |
| **Marketing & Communications** | | | |
| Campaigns, content, social media archives | 2 years | Cloud storage (Google Drive, Box) | Marketing |
| Customer testimonials, case studies | Indefinite | Cloud database | Marketing |
| **Email** | | | |
| General business email | 3 years | Cloud archive (auto) | All employees |
| Executive email (CEO, Board, Legal) | 7 years (longer if litigation) | Cloud archive + litigation hold if applicable | Office manager, General Counsel |

### 2.2 Data Classification Impact on Retention
- **Public**: 2-year retention minimum (unless operational reason to keep longer)
- **Internal**: 3-year retention minimum
- **Confidential**: 5-year retention minimum (comply with contract confidentiality terms)
- **Restricted** (PII, trade secrets, security-sensitive): 7-year retention minimum (see Data Classification & Retention Policy)

## 3. Document Creation & Naming Standards

### 3.1 Document Naming Convention
Use clear, searchable names:
```
<Team>-<Project>-<Type>-<YYYY-MM-DD>-<Version>
Examples:
  Marketing-Campaign-EmailTemplate-2026-06-09-v2
  Finance-FY2026-BudgetPlan-2025-12-15-final
  Legal-Contract-NDA-Acme-Corp-2026-02-01-signed
```

### 3.2 Metadata & Tagging
All documents in centralized storage (Google Drive, Box, SharePoint) include:
- **Created date** (auto)
- **Created by** (auto)
- **Last modified** (auto)
- **Owner**: Person responsible for accuracy / updates
- **Classification**: Public, Internal, Confidential, Restricted (per Data Classification & Retention Policy)
- **Retention date**: When document should be purged (or "Indefinite")
- **Sensitive tags**: GDPR, PII, HIPAA, Trade Secret, Attorney-Client Privilege (if applicable)

### 3.3 Versioning & Approval
- **Draft**: Marked "[DRAFT]"; work-in-progress; not final
- **In review**: Marked "[UNDER REVIEW]"; sent to stakeholders; feedback incorporated
- **Final/Active**: No tag; represents current policy/procedure
- **Superseded**: Marked "[SUPERSEDED BY: doc-id]"; archived with date superseded
- **Change tracking**: Use version control (Google Docs suggestion mode, Git diffs) to track edits; final version signed/approved before activation

## 4. Storage & Access Control

### 4.1 Centralized Storage Systems
| System | Purpose | Access Control | Backup |
|--------|---------|-----------------|--------|
| **GitHub** | Code, runbooks, infrastructure configs | RBAC (repo teams); public repos limited | Auto (AWS backup) |
| **Google Drive** (company account) | Shared documents, policies, procedures | Folder-level access; Confidential/Restricted restricted | Auto (Google Workspace) |
| **OneDrive / SharePoint** | Departmental documents, local shared drives | Department folders; sensitive docs encrypted | Auto (Microsoft) |
| **Legal database** (managed service) | Contracts, NDAs, litigation docs | Admin + legal team only; audit log | Daily backup |
| **Cloud archive** (AWS S3 Glacier) | Long-term retention (7+ years); financial, legal, compliance | Encrypted; IT Ops access only | Cross-region replication |
| **Locked file room** (HQ) | Original signed documents, physical records | Keyed cabinet; Facilities manages access | Temperature/humidity controlled |
| **Email archive** (Microsoft Purview or Proofpoint) | Email retention; litigation hold; auto-archive | User can access own email; eDiscovery team can search all | Auto (cloud provider) |

### 4.2 Access Levels
- **Public documents** (marketing, job descriptions, benefits guides): All employees + public internet
- **Internal documents** (policies, strategies, org chart): All Northwind employees + contractors
- **Confidential documents** (contracts, financial, customer data): Department + related stakeholders; approval required for access
- **Restricted documents** (trade secrets, security vulnerabilities, board-level decisions): Executive + directly involved parties only; logged access

### 4.3 Encryption & Security
- **In transit**: All cloud uploads use HTTPS; data encrypted in transit
- **At rest**: Confidential/Restricted data encrypted with AES-256; keys managed by IT Security
- **Shared links**: No-share default; sharing requires approval; expiration date set
- **Mobile**: Accessing Confidential docs on mobile device requires MFA + encryption per Remote Access/VPN Guide

## 5. Audit & Compliance

### 5.1 Internal Audit
- **Quarterly**: Finance audits financial records (invoices, receipts, bank reconciliations)
- **Annually**: General Counsel audits contract portfolio; verifies expiration dates, renewal terms
- **Annually**: HR audits personnel files; verifies compliance with retention policy
- **After breach**: IT Security conducts forensic review of relevant logs; findings reported to VP Security + General Counsel

### 5.2 External Audit & eDiscovery
- **SOC 2 auditors**: Verify backup, archive, and logging controls; audit access logs
- **Tax auditors**: IRS may request 7-year financial records; prepared within 5 business days
- **Litigation/eDiscovery**: If lawsuit filed, General Counsel activates legal hold (Section 6); documents preserved and produced per discovery schedule

### 5.3 Regulatory Compliance
- **GDPR**: Customer data retention limited to contract term + 30 days (unless legal hold); data subject requests (export, delete) handled per Data Privacy & GDPR Compliance Policy
- **SOX / SEC**: If public, quarterly/annual reports retained 7 years + indefinite for material events
- **HIPAA** (if applicable): PHI retained per contract; 6-year audit logs
- **State privacy laws** (CCPA, etc.): PII retention limits per Data Classification & Retention Policy

## 6. Legal Hold & Litigation

### 6.1 Litigation Hold Notice
If Northwind becomes aware of pending/threatened litigation:
1. **General Counsel** issues hold notice to all employees and IT teams
2. **Scope**: Identifies document types, date ranges, persons involved
3. **Compliance**: Employees must preserve documents (stop deletion); IT disables auto-deletion
4. **Duration**: Hold remains until General Counsel lifts it (case settled, resolved, or statute of limitations passed)

**Example hold notice**:
```
LEGAL HOLD NOTICE — Preserve documents related to Acme Corp. contract dispute.
Dates: Jan 2024 — June 2026
Persons: [names of employees involved]
Document types: Email, contracts, meeting notes, Slack messages
STOP deleting. Contact legal@northwind.com with questions.
```

### 6.2 eDiscovery & Production
- **Within 30 days** of hold notice, IT works with General Counsel to identify and collect relevant data
- **Privilege review**: General Counsel filters out attorney-client privileged docs (not produced)
- **Production**: Documents delivered to opposing counsel or court per discovery schedule (often 3–6 months from hold notice)
- **Chain of custody**: Documented; search log maintained

## 7. Destruction & Purging

### 7.1 Automatic Destruction (End-of-Life Documents)
Once retention period expires:
- **Email**: Auto-archived after 3 years by Outlook/Gmail; not searchable but retained for 7 years if hold-applicable
- **Cloud docs**: System flags for deletion; owner confirms, then document moved to trash (30-day recovery window); permanently deleted after 30 days
- **Physical files**: HR/Finance reviews; legal-hold items exempted; remaining docs shredded (certified certificate of destruction maintained)

### 7.2 Early Destruction (With Approval)
If document reached end-of-life but needs to be destroyed before scheduled purge:
1. Document owner requests destruction from General Counsel (if sensitive/legal/HR) or IT Ops (if operational)
2. **Approval**: Confirmed no pending litigation, regulatory request, or hold
3. **Method**: Digital (encrypted wipe) or physical (shredding); certificate of destruction maintained
4. **Logging**: Date, requester, approver, method recorded in retention tracker

### 7.3 Prohibited Destruction
- **During litigation hold**: Violation of hold notice (federal crime; civil sanctions apply)
- **Without approval**: Unauthorized deletion may constitute evidence tampering
- **Confidential/Restricted data**: Wipe method must be certified (DoD 5220.22-M standard or asset destruction certificate)

## 8. Document Control & Approval Workflows

### 8.1 Critical Documents (Policies, Procedures, Contracts)
1. **Draft**: Author creates document; marks "[DRAFT]"
2. **Review**: Circulated to stakeholders; feedback collected via comments or in-person
3. **Revision**: Author incorporates feedback; updates version number
4. **Approval**: Owner (functional VP or General Counsel) reviews final version; approves in writing (email, signature line in doc)
5. **Activation**: Marked "Final/Active"; effective date noted; superseded documents marked and archived
6. **Communication**: Policy change announced per Internal Communications Policy; training scheduled if behavior change required

### 8.2 Change Log
All critical documents maintain a change log:
```
Version | Date | Author | Changes | Approved By
1.0     | 2024-01-15 | Sarah | Initial draft | John (VP Eng)
1.1     | 2024-02-01 | Sarah | Incorporated feedback re: MFA | John
2.0     | 2024-06-15 | Tom | Major revamp per audit findings | John + Legal
```

## 9. Training & Accountability

- **All employees**: Data handling training during Onboarding Day 1; annual refresher
- **Department leaders**: Responsible for ensuring team follows document retention schedule; spot-checks conducted quarterly by General Counsel
- **IT Ops**: Ensures backup and archive systems functioning; monthly verification
- **Violation consequences**: Destroying records without authorization may result in disciplinary action (up to termination) and legal liability

