---
title: Data Classification & Retention Policy
doc_id: data-classification-retention-policy
owner: Compliance Team
last_updated: 2026-01-20
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Data Classification & Retention Policy

## 1. Data Classification Levels

All information created, received, or processed by Northwind must be assigned one of four classifications:

### 1.1 Public
- Marketing materials, press releases, public blog posts
- General company announcements
- Non-sensitive product information
- **Access Control**: Unrestricted
- **Encryption**: Not required
- **Retention**: 5 years (or until superseded)
- **Examples**: Company website copy, published whitepapers

### 1.2 Internal
- Internal communications, meeting notes, non-sensitive employee lists
- Internal process documentation
- Aggregate business metrics (not tied to individual customers)
- **Access Control**: Limited to Northwind employees and approved contractors
- **Encryption**: File-level encryption recommended; mandatory for transmission outside corporate network
- **Retention**: 3 years
- **Examples**: Internal memos, departmental process guides, anonymized performance reviews

### 1.3 Confidential
- Customer contracts, pricing agreements, non-public financial data
- Personally Identifiable Information (PII) such as SSN, driver's license, home address
- Proprietary source code, algorithms, architecture diagrams
- Customer data, API keys, database credentials
- Product roadmaps and strategic plans
- **Access Control**: Role-based; limited to those with explicit business need
- **Encryption**: Mandatory AES-256 at rest; TLS 1.3 in transit
- **Retention**: 5 years (or per contract requirements)
- **Examples**: Customer contact lists, salary information, AWS API keys, database backups

### 1.4 Restricted
- Authentication credentials (passwords, private SSH keys, OAuth tokens)
- Encryption keys and key management system access logs
- Incident investigation reports (during active investigation)
- Medical or health information of employees
- Biometric data
- **Access Control**: Explicitly approved by VP Security and data owner; access revoked after 90 days unless renewed
- **Encryption**: Mandatory AES-256 with key held in hardware security module
- **Retention**: As required by law; destroyed within 30 days of retention period end
- **Examples**: Master database encryption keys, employee medical records, payment card data (PCI-DSS scope)

## 2. Data Ownership and Responsibility

Every data set must have a designated **Data Owner** (typically a department head or manager). Data Owners are responsible for:
- Assigning appropriate classification
- Approving access requests
- Ensuring timely deletion at end of retention period
- Responding to data breach notifications

Classification decisions must be documented in the system metadata.

## 3. Special Categories

### 3.1 Personally Identifiable Information (PII)
Any data that can identify an individual (name + email, SSN, home address, phone, government ID, health records) must be classified Confidential or Restricted. Handling is subject to GDPR, CCPA, and state privacy laws.

### 3.2 Payment Card Industry (PCI) Data
Credit card numbers, expiration dates, CVV, and cardholder names must be Restricted and stored only in PCI-compliant systems. Northwind does not store full card data in application databases; card processing is outsourced to Stripe.

### 3.3 Customer Data
All customer-supplied information (including logs, usage data, feature requests) is Confidential minimum. Contracts may specify Restricted handling.

## 4. Data Retention Schedule

| Classification | Default Retention | Destruction Method |
|---|---|---|
| Public | 5 years | Permanent deletion from storage |
| Internal | 3 years | Permanent deletion from storage |
| Confidential | 5 years (or per contract) | Cryptographic wiping or shredding |
| Restricted | As required by law (1–7 years) | Cryptographic wiping to NIST 800-88 standard |

**Exceptions**: Legal holds, ongoing litigation, or explicit contract requirements may extend retention. The Compliance team must approve all exceptions.

## 5. Data Retention Automation

- All cloud storage (OneDrive, Google Drive) is configured to auto-delete files older than retention period
- Database backups are deleted after 90 days (full backup cycle) unless customer contract specifies longer retention
- Email is archived after 7 years; archived email is deleted after 10 years total

## 6. Breach Notification

If unencrypted Confidential or Restricted data is suspected lost, stolen, or exposed, the responsible employee must notify the Security Team within 1 hour. See the **Incident Response Runbook** for escalation and notification timelines.

## 7. Cross-Reference: Travel and Data Mobility

When traveling (see **Expense & Travel Policy**), employees may only carry devices with Confidential or Restricted data if:
- Device is encrypted (BitLocker, FileVault, or Samsung Knox)
- Device has MFA enabled
- Device is lost-and-found covered by company insurance
- Data is synced to cloud storage with encryption in transit

## 8. Compliance and Audit

The Compliance team audits data classification and retention practices annually. Non-compliance may result in disciplinary action and mandatory remedial training.

---

**Document owner:** Chief Compliance Officer  
**Last approved:** 2026-01-20 by Compliance Leadership  
**Next review:** 2027-01-20
