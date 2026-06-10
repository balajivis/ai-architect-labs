---
title: Identity & Access Management Policy
doc_id: identity-access-management-policy
owner: IT Security Team
last_updated: 2026-05-01
status: active
classification: internal
supersedes: identity-access-management-policy-legacy
superseded_by: ""
---

# Identity & Access Management Policy

## 1. Purpose

This policy establishes standards for managing user identities, authentication, and access to Northwind's systems and data. It supersedes the legacy IAM policy (last updated 2024-06-15) with modern, NIST-aligned practices.

## 2. User Provisioning and Deprovisioning

### 2.1 New Employee Onboarding
When a new employee joins Northwind, the HR system automatically triggers creation of:
- Okta SSO account
- Email account
- Cloud storage account (OneDrive)
- VPN profile

The hiring manager must specify required system access (engineering, finance, customer support, etc.). The IAM team approves access and provisions credentials within 4 business hours.

### 2.2 Contractor and Temporary Access
Contractors and vendors require a signed Data Processing Addendum (DPA) and approval from department head and Compliance team. Temporary access is limited to 90 days and must be renewed quarterly.

### 2.3 Offboarding
Upon termination or resignation:
- All access is revoked within 2 hours of offboarding notification
- Okta session is terminated immediately
- Email is placed in retention hold (see **Data Classification & Retention Policy**)
- All company devices are collected, wiped, and recycled
- Contractor/vendor access is deactivated immediately

## 3. Authentication Standards

### 3.1 Password Policy (Current Standards – Replaces Superseded Legacy Policy)

**Current Policy (effective 2026-05-01):**
- Minimum 12 characters
- No forced periodic rotation (per NIST SP 800-63B guidance)
- Must be changed only if compromised
- Account lockout after 5 failed attempts (60-minute lockout period)

**Legacy Policy (superseded; do NOT use):**
- 8 character minimum
- Forced rotation every 90 days
- **Status**: Deprecated as of 2026-05-01; see superseded policy doc

### 3.2 Multi-Factor Authentication (MFA) – Mandatory

MFA is required for:
1. All cloud platform access (AWS, Azure, Google Cloud)
2. VPN access (see **Remote Access / VPN Guide**)
3. All administrative accounts (engineers with sudo, IT staff, security team)
4. Email access from non-corporate network (external IP)

**Approved MFA Methods** (in order of preference):
1. TOTP (Time-based One-Time Password) via authenticator app (Google Authenticator, Microsoft Authenticator, Authy)
2. Hardware security key (Yubikey, Google Titan; mandatory for executives)
3. SMS (fallback only; highest risk)

### 3.3 Single Sign-On (SSO) via Okta

All web applications must use SSO. Local username/password authentication is prohibited unless:
- Application does not support SAML/OIDC (rare; requires VP IT approval)
- Okta is unavailable (fallback credentials pre-authorized by IT Security)

### 3.4 Session Timeout

All Northwind applications must enforce:
- **Idle timeout**: 30 minutes of inactivity
- **Maximum session duration**: 12 hours (re-authentication required)

## 4. Least Privilege and Role-Based Access Control (RBAC)

All access decisions must follow the principle of least privilege. Permissions are granted only for job-required functions.

### 4.1 Access Review Cycle
- **Frequency**: Quarterly (Jan, Apr, Jul, Oct)
- **Process**: Department managers review their team's access, approve or revoke
- **Audit**: IAM team flags dormant accounts (no login in 90 days); managers confirm whether to retain or revoke

### 4.2 Privileged Access Management (PAM)
Administrative access (sudo, database root, cloud API keys) requires:
- Explicit approval from IT Security
- Documented business justification
- Session recording and audit logging
- 6-month re-certification

## 5. Credential Management

### 5.1 API Keys and Tokens
- Must be rotated every 180 days
- Must not be embedded in application code; use environment variables or secrets vaults
- Compromised keys must be revoked immediately
- Database passwords held in AWS Secrets Manager; applications retrieve at runtime

### 5.2 SSH Keys
- RSA 4096-bit or Ed25519 minimum
- Private keys stored locally with passphrase protection
- Public keys managed in Okta Directory
- Compromised keys revoked within 1 hour

### 5.3 Password Managers
- Okta Vault is the standard for team-shared credentials (engineering, database backups)
- 1Password is available for personal password management

## 6. Third-Party Access

Third-party vendors (cloud providers, integrators, consultants) requiring system access must:
- Authenticate via Okta or SSO where possible
- Use separate contractor accounts (prefixed `contractor_`)
- Provide MFA
- Sign a DPA (see **Vendor Procurement & Third-Party Risk Policy**)
- Undergo security clearance (High Risk vendors: annual assessment)

## 7. Breach Response and Credential Revocation

If an account is suspected compromised:
- Immediately revoke all sessions in Okta
- Force password reset on next login
- Require MFA re-enrollment
- Notify employee and manager
- Escalate to Security team if access to Confidential/Restricted data occurred (see **Incident Response Runbook**)

## 8. Compliance and Monitoring

- Okta logs all authentication events and access changes; retained for 1 year
- Unauthorized access attempts are tracked and alerted (3+ failed MFA in 10 minutes triggers incident response)
- Quarterly IAM audit submitted to Compliance and Audit Committee

## 9. Training and Awareness

All new employees complete SSO and MFA setup training before Day 1. Annual refresher training is required for all staff.

---

**Document owner:** Chief Information Security Officer  
**Last approved:** 2026-05-01 by IT Leadership (replaces legacy policy approved 2024-06-15)  
**Legacy policy status:** SUPERSEDED (2024-06-15 → 2026-05-01)  
**Next review:** 2027-05-01
