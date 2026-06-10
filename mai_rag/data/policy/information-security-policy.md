---
title: Information Security Policy
doc_id: information-security-policy
owner: Security Team
last_updated: 2026-03-14
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Information Security Policy

## 1. Purpose and Scope

This policy establishes the minimum security standards for all Northwind Technologies employees, contractors, and third parties with access to company systems and data. This policy applies to all employees in all locations and all remote workers.

## 2. Information Classification

All company information must be classified according to the **Data Classification & Retention Policy**. Security controls must be proportional to classification level:
- **Public**: No encryption required; unrestricted distribution
- **Internal**: File-level encryption; limited distribution within Northwind
- **Confidential**: Full encryption at rest and in transit; restricted access via role-based controls
- **Restricted**: Maximum encryption; access requires explicit approval from VP Security and data owner

## 3. Access Control Principles

All access must follow the principle of least privilege. Users may only access systems and data required for their job function. Access reviews must be conducted quarterly by department heads and approved by the Identity & Access Management (IAM) team.

### 3.1 Multi-Factor Authentication (MFA)

MFA is mandatory for:
- All cloud platform logins (AWS, Azure)
- All VPN access
- Administrative accounts
- Email access from non-corporate devices

MFA methods: TOTP (authenticator apps), hardware security keys (preferred), or SMS as fallback.

### 3.2 Single Sign-On (SSO)

SSO via corporate identity provider (Okta) is required for all SaaS applications. Individual user IDs and passwords for web applications are prohibited unless explicitly approved by the IAM team.

## 4. Data Protection Standards

### 4.1 Encryption

- **At rest**: AES-256 for databases and file storage; applied to all Confidential and Restricted data
- **In transit**: TLS 1.3 minimum for all network communication
- **Key management**: All encryption keys held in HSM (Hardware Security Module) managed by Northwind's cloud provider

### 4.2 Endpoint Security

All company-issued laptops and workstations must have:
- Operating system updated within 14 days of vendor release
- Antivirus/antimalware engine active with signatures updated daily
- Device encryption enabled (BitLocker for Windows; FileVault for macOS)
- Host-based firewall enabled

Personal devices used for work must be enrolled in Mobile Device Management (MDM) and comply with the same standards.

## 5. Incident Response

Upon discovery of a suspected security incident, employees must report to the Security Team at security@northwind.com within 1 hour. Do NOT investigate or disclose details beyond the immediate IT and Security teams. See the **Incident Response Runbook** for escalation paths and timelines.

## 6. Third-Party and Vendor Risk

All vendors processing company data must sign a Data Processing Addendum (DPA) and comply with the **Vendor Procurement & Third-Party Risk Policy**. Annual security assessments are mandatory for vendors classified as "High Risk" (see Vendor Policy for criteria).

## 7. Compliance and Auditing

Northwind complies with SOC 2 Type II, ISO 27001 (in progress), and GDPR standards. The Compliance team conducts annual audits. All employees must complete security awareness training annually and pass a knowledge assessment (minimum 80%).

## 8. Enforcement

Violations may result in:
- First offense: Written warning and mandatory remedial training
- Second offense: Suspension of system access for 7 days
- Third offense: Termination of employment

Executives and security staff are subject to the same standards.

## 9. Policy Review

This policy is reviewed annually. Any updates require approval from the VP Security and Chief Technology Officer. Employees will be notified of policy changes via email and internal wiki.

---

**Document owner:** VP Security  
**Last approved:** 2026-03-14 by Security Steering Committee  
**Next review:** 2027-03-14
