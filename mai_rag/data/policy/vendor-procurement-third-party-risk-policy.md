---
title: Vendor Procurement & Third-Party Risk Policy
doc_id: vendor-procurement-third-party-risk-policy
owner: Compliance & Procurement
last_updated: 2026-01-30
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Vendor Procurement & Third-Party Risk Policy

## 1. Purpose

This policy establishes standards for evaluating, selecting, and managing third-party vendors and contractors who access Northwind's systems or process company data.

## 2. Vendor Categories

All vendors are categorized by risk level and data access:

| Category | Risk Level | Examples | Security Review Required |
|----------|-----------|----------|---|
| **Infrastructure** | High | Cloud provider (AWS, Azure), DDoS provider, DNS provider | Comprehensive (SOC 2, penetration test) |
| **Customer-Facing** | High | SaaS platforms used by customers, support tools, analytics | SOC 2 Type II minimum |
| **Data Processing** | High | Email provider, CRM, payment processor | SOC 2 + Data Processing Addendum (DPA) required |
| **Development** | Medium | GitHub, CI/CD tools, code repositories | SOC 2 or equivalent |
| **Operations** | Medium | HR systems, expense reporting, IT ticketing | Security questionnaire + SOC 2 preferred |
| **Low-Impact** | Low | Office supplies, marketing agencies, non-data SaaS | Minimal security review |

## 3. Vendor Evaluation Process

### 3.1 Pre-Selection (Internal Evaluation)

When evaluating a new vendor:

1. **Business case**: Department head documents why this vendor is needed
2. **Cost analysis**: Compare 3+ vendors; justify selection
3. **Compliance check**: Will this vendor comply with our data classification and handling policies?
4. **Feature evaluation**: Does the vendor's solution meet functional requirements?

**Expected timeline**: 2–4 weeks

### 3.2 Security Assessment

Based on vendor category, Northwind requires:

#### High-Risk Vendors
- **SOC 2 Type II audit report** (current within 12 months)
  - Must cover: Security, Confidentiality, Availability
  - Provides evidence of controls over access, encryption, monitoring
- **Penetration test results** (current within 18 months) – optional if SOC 2 is recent
- **Security questionnaire** (Northwind security team provides template)
- **Data Processing Addendum (DPA)** – if vendor processes any PII or Confidential data
- **Interview with vendor security team** – conducted by Northwind's VP Security

#### Medium-Risk Vendors
- **SOC 2 Type II OR security questionnaire** (acceptable alternatives)
- **Data Processing Addendum (DPA)** – if data processing occurs

#### Low-Risk Vendors
- **Security questionnaire** (basic; self-assessed)
- **Attestation**: Vendor confirms no processing of company data beyond what's published

### 3.3 Legal Review

All vendor contracts must be reviewed by Legal (Northwind's General Counsel):
- **Data Processing Addendum (DPA)**: Ensures GDPR, CCPA, and data residency compliance
- **Liability and indemnification**: Vendor responsible for breaches of their security
- **Termination and data return**: How is our data deleted if we terminate?
- **Audit rights**: Northwind can request security audits of vendor

**Timeline**: Legal review typically 5–10 business days

### 3.4 Approval and Onboarding

1. **Final approval**: VP Procurement approves cost and terms
2. **Procurement team**: Negotiates discounts and volume licensing
3. **Onboarding**: IT provisions access; vendor is added to "approved vendors" list
4. **Training**: Teams are trained on vendor's tools and data handling requirements

## 4. Data Processing Agreements (DPA)

Any vendor processing Northwind customer data or PII must sign a Data Processing Addendum that includes:

### 4.1 Data Handling Commitments

- **Encryption**: Data encrypted at rest (AES-256) and in transit (TLS 1.3)
- **Access control**: Limited to employees with business need
- **Audit**: Vendor permits Northwind to audit data handling
- **Retention**: Data deleted within 30 days of termination (or as specified by contract)
- **Subprocessors**: Vendor notifies Northwind if they use additional third parties

### 4.2 GDPR / CCPA Compliance

If vendor processes EU resident data (GDPR scope):
- Standard contractual clauses (SCCs) or equivalent transfer mechanism required
- Vendor confirms data residency (e.g., EU servers only)
- Vendor commits to assist with data subject rights (access, deletion, portability)

If vendor processes California resident data (CCPA scope):
- Vendor confirms CCPA compliance
- Vendor does not sell personal information
- Vendor assists with consumer rights requests

### 4.3 Breach Notification

Vendor must notify Northwind within 24 hours if any security incident involves our data.

## 5. Ongoing Vendor Management

### 5.1 Annual Security Reviews

For High-Risk vendors:
- **Annual review**: Security team checks for updated SOC 2, penetration tests, security incidents
- **Questionnaire refresh**: Vendor confirms no material changes to security posture
- **Escalation**: If SOC 2 expires or new vulnerabilities discovered, vendor is placed on probation

### 5.2 Incident Response

If a vendor experiences a security incident:
1. Vendor notifies Northwind immediately (within 24 hours)
2. Northwind security team assesses impact on our data
3. If customer data was exposed: Escalate per **Incident Response Runbook**
4. Vendor provides incident report (timeline, scope, root cause, remediation) within 5 business days

### 5.3 Offboarding

When terminating a vendor relationship:
1. **Data return**: Vendor deletes all Northwind data within 30 days (or as per contract)
2. **Access revocation**: All accounts and API keys are disabled
3. **Migration**: Data is migrated to new vendor or internal system
4. **Exit attestation**: Vendor provides written confirmation that data has been destroyed

## 6. Vendor Access and Credentials

### 6.1 Contractor Account Management

Contractors and vendors accessing Northwind systems must:
- Have separate Okta account (prefixed `contractor_` or `vendor_`)
- Use MFA (TOTP or hardware key)
- Have time-limited access (auto-revoked after engagement ends)
- Sign acceptable use agreement
- Complete security awareness training

### 6.2 Vendor VPN Access

Vendors requiring remote access to internal systems:
- Request VPN access via procurement team
- Access is scoped: specific IP ranges, specific servers, specific hours
- Access limited to business hours (8 AM–6 PM PT) unless emergency approved
- All access is logged and audited

### 6.3 API Keys and Secrets

If vendors require API keys or service accounts:
- Keys issued via AWS Secrets Manager or similar vault
- Keys are rotated every 180 days
- Vendor does not have console/direct access; must use APIs only
- Key usage is logged and monitored

## 7. Vendor Risk Escalation

### 7.1 Red Flags

If a vendor exhibits any of the following, escalate to VP Security:
- Delays in providing SOC 2 audit
- Failure to notify of security incident
- Unauthorized subprocessors
- Data residency outside agreed regions
- Breach of Data Processing Addendum
- Unreliable uptime (SLA breaches > 2 per quarter)

### 7.2 Vendor Probation

High-risk vendors on probation:
- Increased monitoring: Weekly check-ins instead of quarterly
- Escalated review: VP Security involvement in all decisions
- Plan for replacement: Begin evaluating alternative vendors
- Timeline: 30–90 days to resolve issue or terminate

### 7.3 Termination for Cause

Immediate vendor termination if:
- Security breach affecting Northwind or customer data
- Unauthorized data access or exfiltration
- Breach of contract terms (e.g., using data for own purposes)
- Loss of required certifications (SOC 2, compliance certs)

## 8. Vendor Performance Monitoring

### 8.1 Service Level Agreements (SLAs)

Critical vendors must have SLAs covering:
- **Uptime**: 99.9% monthly availability (4.38 hours downtime allowed)
- **Performance**: API response time < 500ms (p99)
- **Support response**: Sev-1 issue response within 1 hour
- **Penalties**: Credits or refunds for SLA breaches

### 8.2 Metrics Tracking

For all vendors, Northwind tracks:
- Monthly uptime (% of successful requests)
- Incident frequency and resolution time
- Customer complaints or support tickets
- Security incidents or vulnerabilities

**Monthly vendor scorecard** reviewed by VP Procurement; underperforming vendors are addressed.

## 9. Vendor List and Register

Northwind maintains a confidential **Approved Vendor Register** including:
- Vendor name, contract dates, data access level
- SOC 2 expiration date, last security review date
- Key contact, escalation contact, procurement owner
- Annual cost, contract renewal date

**Register updated**: Quarterly review; updated within 5 business days of new vendor approval or termination.

## 10. Compliance and Audit

- Vendor evaluations are retained for 3 years
- Audit team reviews vendor file annually
- External audits (SOC 2, ISO 27001) verify vendor compliance with policy

---

**Document owner:** Chief Compliance Officer  
**Last approved:** 2026-01-30 by Compliance Leadership  
**Next review:** 2027-01-30

**Related policies:**
- **Data Classification & Retention Policy**: Data handling rules vendors must follow
- **Information Security Policy**: Security standards vendors must meet
- **Identity & Access Management Policy**: Contractor account provisioning
- **Incident Response Runbook**: Escalation path if vendor data breach occurs
