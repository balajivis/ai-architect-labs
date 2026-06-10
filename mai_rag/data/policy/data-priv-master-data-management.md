---
title: Master Data Management
doc_id: data-priv-master-data-management
owner: Chief Data Officer
last_updated: 2026-04-19
status: active
classification: internal
supersedes: ""
supersedes_by: ""
---

# Master Data Management

## 1. Overview

**Master Data Management (MDM)** is the discipline of creating and maintaining a **single source of truth** for critical business data (customer, employee, vendor, product). MDM ensures data consistency across systems, reduces duplicate work, and enables reliable analytics.

**Scope**: This policy applies to:
- **Customer Master Data**: Accounts, contacts, company information
- **Employee Master Data**: Names, IDs, departments, roles, access levels
- **Product Master Data**: Product catalog, feature flags, pricing
- **Vendor Master Data**: Vendor names, contacts, contract terms

**Privacy relevance**: Master data often contains personal data (customer names, emails, employee IDs). MDM quality directly impacts data subject rights (rectification, access, deletion).

## 2. Master Data Architecture

### 2.1 Systems of Record (SoR)

Each data domain has a **System of Record** — the authoritative source:

| Domain | System of Record | Secondary Systems | Update Frequency |
|---|---|---|---|
| **Customers** | Salesforce CRM | Database, Analytics, Marketing automation | Real-time sync via API |
| **Employees** | BambooHR (HR system) | Okta (SSO), Jira, GitHub, VPN, badge access | Daily sync via API |
| **Products** | Northwind Cloud product DB | Marketing site, API docs, customer portal | Real-time via CI/CD |
| **Vendors** | Vendor management spreadsheet + Contracts DB | Procurement system, access control | Manual + quarterly audit |

**Rule**: The SoR is the **only authoritative source**. Secondary systems pull data from SoR; they never override it.

### 2.2 Master Data Attributes

Each master entity has core attributes that must be synchronized:

**Customer Master Data**:
- customer_id (unique identifier)
- company_name, industry, country
- primary_contact (name, email, phone)
- account_type (freemium, paid, enterprise)
- contract_status (active, paused, churned)
- data_classification (see **Data Classification & Retention Policy**)

**Employee Master Data**:
- employee_id (unique identifier)
- full_name, email, phone
- department, manager, title
- start_date, employment_status
- access_level (see **Identity & Access Management Policy**)

### 2.3 Master Data Governance Structure

| Role | Responsibility |
|------|-----------------|
| **Data Steward** (per domain) | Owns SoR; approves data changes; resolves conflicts |
| **Data Owner** (per attribute) | Defines business rules for attributes; validates accuracy |
| **MDM Team** (IT/Data) | Maintains SoR system; implements sync processes; audits consistency |
| **Chief Data Officer** | Policy owner; escalates unresolved conflicts; approves exceptions |

**Example governance**:
- **Customer data steward** = VP Sales (owns Salesforce CRM)
- **Customer email owner** = Marketing Ops (defines: "email must be validated via double opt-in")
- **Customer classification owner** = Chief Privacy Officer (defines: "Confidential vs. Restricted")

## 3. Master Data Lifecycle

### 3.1 Creation (Onboarding)

New master data is created in the **System of Record**:

**Process**:
1. Data steward (or authorized user) enters core attributes in SoR
2. System validates against business rules (format, uniqueness, required fields)
3. If valid, record is created with a unique ID
4. Data is flagged for sync to secondary systems
5. Secondary systems receive data within 24 hours

**Quality gates**:
- Email must be in valid format (RFC 5322)
- Name must not be empty
- Company name must match business registry (if available)
- Classification must be assigned (Public, Internal, Confidential, Restricted)

### 3.2 Maintenance and Updates

Master data is updated when business conditions change:

**Change process**:
1. User identifies a change (e.g., customer changed companies, employee changed departments)
2. Change is submitted to **data steward** for approval (if outside their own record)
3. Steward validates the change (is it authorized? is the new value accurate?)
4. If approved, record is updated in SoR
5. Change is logged (who, what, when) for audit trail
6. Sync flag is set; secondary systems are updated

**Approval authority**:
- Employees may update their own non-sensitive attributes (phone, city)
- Data steward must approve changes to sensitive attributes (classification, access level)
- Chief Privacy Officer must approve changes to attributes affecting GDPR compliance

### 3.3 Synchronization and Consistency

Master data is synchronized to secondary systems via:

- **API integration** (real-time): Salesforce → Database (webhooks, polling)
- **Batch sync** (nightly): BambooHR → Okta SSO (scheduled job)
- **Manual sync** (on-demand): Vendor data → Procurement system (quarterly audit + update)

**Conflict resolution**: If a record is changed in two systems simultaneously (e.g., customer updated in Salesforce AND in the database):
- Primary system (SoR) wins
- Secondary system is overwritten
- Conflict is logged; steward is notified (may indicate process problem)

**Audit**: Weekly reconciliation of master data between SoR and secondary systems (count of records, hash of key attributes).

### 3.4 Deactivation and Deletion

When a customer churns, an employee leaves, or a vendor relationship ends:

**Deactivation** (soft delete):
- Record is marked inactive (not deleted)
- Secondary systems stop syncing from record (but retain historical data)
- Data is retained per retention schedule (e.g., customer: 5 years post-churn; see **Data Retention Schedule**)

**Deletion** (hard delete):
- Record is physically deleted from SoR
- All secondary systems purge the record
- Deletion is logged; Chief Privacy Officer is notified
- Right of erasure (GDPR) may trigger deletion

**Example**: Customer cancels subscription on 2026-04-01. Record is marked inactive. Data is retained until 2031-04-01 (5 years post-churn). At 2031-04-01, record is deleted if no legal hold exists.

## 4. Master Data Quality and Privacy

Master data quality directly impacts:
- **GDPR compliance**: Inaccurate customer email → right of rectification delayed
- **Data minimization**: Unnecessary attributes → larger footprint
- **Data subject rights**: Cannot fulfill data access request if master record is incomplete

### 4.1 Data Quality Standards for Master Data

Master data must meet higher quality standards than transactional data:

| Attribute | Standard |
|-----------|----------|
| **Uniqueness** | 100% (no duplicate customer IDs, employee IDs) |
| **Completeness** | 100% for required fields; 80%+ for optional |
| **Accuracy** | 99%+ (must be verified against source) |
| **Validity** | 100% (format, enum values, constraints) |
| **Timeliness** | Updated within 24 hours of change |

See **Data Quality Standard** for audit methods.

### 4.2 Data Minimization

Master data should include **only attributes necessary for business operations**. Unnecessary attributes increase risk:

**Good practice**: Customer master includes {id, company, contact_email, country, contract_status}
**Bad practice**: Customer master includes {id, company, contact_email, address, ssn, credit_score, religion, ethnicity}

**Rule**: Before adding a new attribute to master data, data steward must document:
- Business purpose (why do we need this?)
- Legal basis (consent, contract, legitimate interest?)
- Retention period (how long do we keep it?)
- Classification (what risk level?)

If purpose cannot be articulated, the attribute is not added.

## 5. Personal Data in Master Data

Master data often includes personal data (customer names, emails, employee IDs). Special rules apply:

### 5.1 Restricted Personal Data

**Cannot be included in master data** (or must be encrypted separately):
- Authentication credentials (passwords, API keys)
- Encryption keys
- SSN or government ID numbers
- Health/medical information
- Biometric data

**If needed**, these are stored in a separate, highly-secured system with different access controls.

### 5.2 Confidential Personal Data (Name, Email, Address)

**May be in master data** if:
- Business purpose is clear (e.g., customer contact info needed for billing)
- Access is controlled via RBAC (only authorized teams see it)
- Retention schedule is clear (see **Data Retention Schedule**)
- Data quality is maintained (see **Data Quality Standard**)

**Sensitivity**: Marked as Confidential classification; encryption in transit and at rest.

### 5.3 GDPR Rights in Master Data

Master data enables GDPR rights:
- **Right of access** (Article 15): Data subject requests copy of their master record
- **Right of rectification** (Article 16): Data subject corrects inaccurate master data
- **Right of erasure** (Article 17): Data subject requests deletion (with exceptions for legal hold, contract)

**Process**: See **Data Subject Rights Procedure** for how to fulfill rights from master data.

## 6. Master Data Governance and Compliance

### 6.1 Master Data Register

MDM team maintains a **Master Data Register**:

| Domain | System | Owner | Attributes | Sync Frequency | Last Audit |
|---|---|---|---|---|---|
| **Customers** | Salesforce | VP Sales | 15 attributes | Real-time | 2026-04-15 |
| **Employees** | BambooHR | VP People | 12 attributes | Daily | 2026-04-10 |
| **Products** | Northwind Cloud DB | VP Product | 25 attributes | Real-time | 2026-04-18 |
| **Vendors** | Vendor DB | Procurement | 10 attributes | Quarterly | 2026-03-30 |

### 6.2 Annual MDM Audit

The Chief Data Officer audits master data annually:

1. **Completeness**: Are required attributes present in 100% of records?
2. **Accuracy**: Sample 50+ records; verify against source (e.g., customer email matches company records)
3. **Consistency**: Do secondary systems match SoR (within 24-hour sync window)?
4. **Uniqueness**: No duplicate IDs or emails?
5. **Timeliness**: Are records updated promptly when business changes occur?
6. **Quality**: Do data quality scores meet thresholds per **Data Quality Standard**?

**Report**: Findings reported to VP Engineering and Board quarterly.

### 6.3 Exception Handling

If master data violates a standard (e.g., incomplete record, sync delay, duplicate found):

1. **Issue is logged** in MDM tracking system
2. **Steward is notified** with 5-day remediation deadline
3. **Root cause** is investigated (process gap? system error? manual error?)
4. **Remediation** is implemented (fix record; improve process)
5. **Verification**: Record is fixed; process is improved to prevent recurrence

**Escalation**: If not resolved in 30 days → escalate to Chief Data Officer → CEO.

### 6.4 Data Lineage and Audit Trail

Master data changes are logged:

- **Who**: User ID that made the change
- **What**: Original value → new value (before/after)
- **When**: Timestamp
- **Why**: Change reason (if provided)
- **Where**: Which system originated the change

**Retention**: Audit trail is retained for 7 years (per audit requirements and **Data Retention Schedule**).

## 7. Cross-Reference to Related Policies

- **Data Classification & Retention Policy**: Master data classification and retention periods
- **Data Quality Standard**: Quality standards for master data (accuracy, completeness, uniqueness)
- **Records Management Policy**: Archival and deletion of master data records
- **Data Subject Rights Procedure**: How to fulfill GDPR rights from master data
- **Data Processing Agreement (DPA) Standard**: If master data is shared with processors

---

**Document owner:** Chief Data Officer  
**Last approved:** 2026-04-19 by Data Leadership  
**Next review:** 2027-04-19
