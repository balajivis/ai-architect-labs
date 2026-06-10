---
title: SaaS Application Approval Process
doc_id: itsec-saas-approval-process
owner: IT Operations & Security
last_updated: 2026-04-05
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# SaaS Application Approval Process

## 1. Purpose and Scope

This process describes how employees request approval to use Software-as-a-Service (SaaS) applications at Northwind. Approval is required for all cloud applications that store, process, or access company data.

## 2. Application Risk Assessment Framework

### 2.1 Risk Categories

All SaaS applications are assessed on the following criteria:

| Category | Low Risk | Medium Risk | High Risk |
|---|---|---|---|
| **Data Sensitivity** | Public only | Internal + limited Confidential | Confidential, Restricted, or PII |
| **User Count** | <5 users | 5–50 users | >50 users |
| **Authentication** | Okta SSO required | Okta SSO preferred; password OK | Okta SSO mandatory |
| **Compliance** | SOC 2 not required | SOC 2 recommended | SOC 2 Type II mandatory |
| **Examples** | Google Analytics, Figma | Slack, Notion, Datadog | Salesforce, GitHub Enterprise, Okta |

### 2.2 Security Questionnaire

All applications classified as "Medium Risk" or higher must complete a security questionnaire covering:
- Data encryption (at rest and in transit)
- Authentication and MFA capabilities
- Compliance certifications (SOC 2, ISO 27001, GDPR, HIPAA)
- Incident response procedures and SLA
- Subprocessor list (third-party vendors accessing data)
- Data retention and deletion policies
- Right to audit and security assessments

## 3. Approval Workflow

### 3.1 Request Process

1. **Employee initiates request** via SaaS Portal (saas-requests.northwind.com)
   - Application name, vendor, business justification
   - Number of expected users
   - Type of data (Public/Internal/Confidential/Restricted)
   - Cost and contract term

2. **Department head approval** (within 3 business days)
   - Reviews business need; approves or rejects
   - If approved, forwards to IT Security

3. **IT Security review** (within 5 business days)
   - For Low Risk: Automatic approval if vendor SOC 2 certified
   - For Medium/High Risk: Full security questionnaire; may request vendor remediation
   - Security review includes: privacy policy analysis, DPA review, compliance assessment

4. **Vendor Agreement** (before procurement)
   - If Confidential/Restricted data involved: Vendor must sign Data Processing Addendum (DPA)
   - DPA must include: data protection standards, incident notification, right to audit, GDPR clauses
   - Legal review required if procurement >$50K/year

5. **Procurement and Licensing**
   - Finance approves contract and cost
   - CFO signature required for contracts >$100K/year
   - IT Operations sets up account and configures SSO (if available)

6. **User Access and Training**
   - IT Operations provisions accounts and applies access controls
   - Requester provides user training (vendor documentation + Northwind security expectations)
   - Users must complete SaaS security training (15 minutes) before access granted

### 3.2 Approval Timeline

| Risk Level | Total Timeline |
|---|---|
| Low Risk (Public data, <5 users) | 3 days |
| Medium Risk (Internal data, 5-50 users) | 10 days |
| High Risk (Confidential/Restricted, >50 users) | 21 days |

Expedited approvals available for business-critical applications (e.g., production outage remediation) with VP approval.

## 4. SaaS Integration Requirements

### 4.1 SSO Integration

All applications processing company data must integrate with Okta SSO:
- User provisioning via SCIM (System for Cross-Domain Identity Management)
- Automatic user de-provisioning when employee is offboarded
- JIT (Just-In-Time) provisioning to reduce manual overhead
- No local passwords; users log in via Okta

Exception: Applications that do not support SCIM must implement manual user provisioning with documented procedures and monthly audits of active accounts.

### 4.2 Data Protection in Transit

- All data must be transmitted via HTTPS (TLS 1.3 minimum)
- Certificate pinning recommended for sensitive applications
- VPN tunnel required for applications handling Restricted data (may require vendor whitelist of IP ranges)

### 4.3 Data Encryption at Rest

- Confidential and Restricted data must be encrypted at rest in the SaaS application
- Vendor must use AES-256 or equivalent
- If vendor does not support encryption at rest, encryption must occur client-side before upload

## 5. Vendor Management and Monitoring

### 5.1 Annual Security Reassessment

- All approved vendors undergo security reassessment annually
- Updated SOC 2 reports requested and reviewed
- Changes to vendor's subprocessors notified to IT Security
- If vendor SOC 2 expires, access may be suspended pending renewal

### 5.2 Breach Notification SLA

Vendors must notify Northwind of data breaches within **24 hours**. Failure to notify is grounds for immediate account suspension and vendor escalation.

### 5.3 SaaS Spending Oversight

- All subscriptions tracked in the SaaS portal (including seat count, expiration, cost)
- Quarterly spend reviews by IT Director and Finance
- Unused licenses identified and cancelled to control costs
- Shadow IT (unapproved SaaS) discovered via network monitoring; users contacted and required to migrate to approved alternative

## 6. Data Security in SaaS Applications

### 6.1 Acceptable Data Types

| Data Classification | Approved for SaaS? | Controls Required |
|---|---|---|
| Public | Yes | Standard security questionnaire |
| Internal | Yes | SSO + encryption at rest |
| Confidential | Conditional | DPA signed + encryption at rest + limited user access |
| Restricted | Rarely | VP Security + Chief Privacy Officer approval; DPA with audit rights |

### 6.2 Prohibited Activities

- Uploading unencrypted PII (SSN, home address, government IDs) to SaaS applications
- Sharing Restricted data with vendors not under DPA
- Storing production database credentials or API keys in SaaS tools (use secrets manager instead)

### 6.3 Data Deletion Upon Contract Termination

At contract end or account suspension:
- SaaS vendor must delete all company data within 30 days
- Vendor provides deletion certificate signed by authorized officer
- If deletion not confirmed, escalate to Legal for contract enforcement

## 7. Incident Response for SaaS Breaches

If a SaaS vendor suffers a data breach involving Northwind data:
1. IT Security notifies VP Security and Chief Privacy Officer within 1 hour
2. Classify incident (Sev-1, Sev-2, Sev-3) per **Incident Response Runbook**
3. If Sev-1 (confirmed PII exposure): Executive notification within 30 minutes
4. If Sev-2+: Customer notification, root cause analysis, audit of vendor's controls

## 8. Related Policies

- **Information Security Policy**: General data classification and protection standards
- **Identity & Access Management Policy**: SSO and access control requirements
- **Vendor Procurement & Third-Party Risk Policy**: Detailed vendor risk assessment
- **Data Classification & Retention Policy**: Data types and retention timelines
- **Incident Response Runbook**: Breach escalation and notification procedures

---

**Document owner:** VP IT Operations  
**Last approved:** 2026-04-05 by IT Leadership  
**Next review:** 2027-04-05
