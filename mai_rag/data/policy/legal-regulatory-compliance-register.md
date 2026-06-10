---
title: Regulatory Compliance Register
doc_id: legal-regulatory-compliance-register
owner: Legal & Risk
last_updated: 2026-06-09
status: active
classification: confidential
supersedes: ""
superseded_by: ""
---

# Regulatory Compliance Register

## Purpose
This register tracks Northwind Technologies' regulatory obligations, audit schedules, compliance status, and remediation efforts across all applicable jurisdictions and frameworks. It serves as the single source of truth for compliance risk assessment.

## 1. Applicable Regulatory Frameworks

| Framework | Jurisdiction | Applicability | Owner |
|---|---|---|---|
| **GDPR** | EU + UK | Northwind processes EU customer data | Chief Privacy Officer |
| **CCPA/CPRA** | California | Northwind processes California resident data | Chief Privacy Officer |
| **HIPAA** | U.S. Federal | If handling health data (currently no) | Chief Privacy Officer |
| **SOC 2 Type II** | Auditing standard | Requested by enterprise customers | VP Security + Audit firm |
| **ISO 27001** | International | Optional certification (target: 2027) | VP Security |
| **FTC Safeguards Rule** | U.S. Federal | Northwind is service provider; must comply | VP Security + General Counsel |
| **Export Control (EAR)** | U.S. Federal | Software encryption + foreign nationals | General Counsel |
| **Anti-Corruption (FCPA/UK Bribery)** | U.S./UK | Northwind operates internationally | General Counsel |
| **Tax Compliance** | State + Federal | Sales tax, employment tax, income tax | CFO |
| **Labor Law** | Federal + State | Texas primary, plus multi-state remote | VP People |

## 2. Compliance Status Dashboard

### Data Privacy
**GDPR Compliance**
- Status: ✅ **Compliant** (last audit: 2025-11-15)
- DPA in place with all customer vendors
- Privacy by Design implemented in new features
- Data Subject Rights process (access, deletion) in place
- Next audit: 2026-11-15

**CCPA/CPRA Compliance**
- Status: ✅ **Compliant** (last audit: 2025-09-30)
- California resident data inventory maintained
- Opt-out/opt-in mechanisms in place for marketing
- Privacy notice updated 2026-01-01
- Next audit: 2026-09-30

### Security & Audit
**SOC 2 Type II**
- Status: ✅ **In progress** (engagement with Big4 audit firm)
- Scope: Security, availability, integrity, confidentiality
- Testing period: 2026-01-01 to 2026-06-30
- Expected completion: 2026-09-30
- Cost: $150K; approved in 2026 budget

**ISO 27001**
- Status: ⏳ **Planned** (target: 2027)
- Prerequisite: Complete SOC 2 Type II
- Gap analysis scheduled for Q1 2027

### Vendor Risk Management
**Third-Party Risk (Vendor Procurement & Third-Party Risk Policy)**
- Status: ✅ **Compliant** (updated 2026-05-01)
- All vendors screened for OFAC/sanctions compliance
- Data processor agreements signed by 100+ vendors
- Vendor audit calendar maintained (5-year cycle)
- Next high-risk vendor audits: Q3 2026

### Anti-Corruption & FCPA
**FCPA/UK Bribery Compliance**
- Status: ✅ **Compliant** (training updated 2026-01-15)
- All employees trained on FCPA; 95% compliance rate
- Customer/partner due diligence process in place
- Sanctions screening (OFAC) for new vendors
- No investigations or violations to date

### Export Control
**Export Administration Regulations (EAR)**
- Status: ✅ **Compliant** (last review: 2025-12-01)
- Encryption in Northwind Cloud classified as non-EAR (standard SSL/TLS)
- Foreign national hiring screened for technology access restrictions
- No violations to date

### Tax Compliance
**Income Tax (Federal + Texas)**
- Status: ✅ **Compliant** (returns filed on time)
- Annual filing deadline: 2026-04-15 (extended)
- Estimated quarterly payments maintained
- Multi-state nexus analysis completed annually

**Sales Tax (Multi-state)**
- Status: ✅ **Compliant**
- SaaS sales are exempt from sales tax in most states
- Nexus analysis confirms no additional filing obligations
- Quarterly review of nexus changes

**Employment Tax**
- Status: ✅ **Compliant**
- Quarterly 941 payroll tax filings
- Annual W-2/1099 reporting
- No back-tax assessments

### Labor & Employment
**Multi-State Compliance**
- Status: ✅ **Compliant** (last audit: 2025-10-01)
- Remote employee classification reviewed annually
- State-specific requirements: California, New York, Massachusetts monitored
- Wage & hour compliance audit scheduled for 2026-Q4

**Title VII / Equal Employment Opportunity**
- Status: ✅ **Compliant**
- No EEOC complaints filed (within 5 years)
- I-9 verification 100% compliant (audited 2025-07-01)

## 3. Audit Schedule & Calendar

| Regulation | Frequency | Last Audit | Next Audit | Owner |
|---|---|---|---|---|
| GDPR | Annual | 2025-11-15 | 2026-11-15 | Chief Privacy Officer |
| CCPA/CPRA | Annual | 2025-09-30 | 2026-09-30 | Chief Privacy Officer |
| SOC 2 Type II | One-time (annual attestation after) | In progress | 2026-09-30 | VP Security |
| Vendor Risk | Rolling (5-year cycle) | Ongoing (10 vendors/yr) | Ongoing | General Counsel |
| FCPA Training | Annual | 2026-01-15 | 2027-01-15 | General Counsel |
| Employment Tax | Quarterly + Annual | 2026-Q1 | 2026-Q2 | CFO |
| Wage & Hour | Biennial | 2025-10-01 | 2026-10-01 | VP People |

## 4. Non-Compliance Events & Remediation

### Past Events (Resolved)
| Event | Date | Issue | Remediation | Status |
|---|---|---|---|---|
| Vendor missing DPA | 2025-08-15 | Vendor started handling customer data without signed DPA | DPA executed retroactively; 30-day probation | ✅ Closed |
| GDPR data subject request delay | 2025-06-01 | Customer took 35 days to fulfill access request (30-day SLA) | Process improved; now <15 days; staff retrained | ✅ Closed |

### Current Issues (Open)
| Issue | Date Found | Impact | Deadline | Owner |
|---|---|---|---|---|
| Export control classification uncertainty | 2026-05-15 | New encryption library; unclear if EAR applies | Legal review by 2026-06-30 | General Counsel |

## 5. Compliance Training & Attestation

**Annual Mandatory Training**:
1. **Information Security Awareness** — All employees; 1 hour; 80% pass required
2. **FCPA/Anti-Corruption** — All employees; 30 min; attestation required
3. **GDPR/Data Privacy** — All employees handling customer data; 1 hour
4. **Employment Law** — Managers + HR staff; 30 min
5. **Acceptable Use Policy** — All employees; 15 min; annual refresh

**Tracking**: HR maintains compliance dashboard. Non-completion triggers escalation to VP People.

**Attestation**: All employees sign annual attestation confirming:
- I have completed required compliance training
- I understand Northwind's policies on data handling, FCPA, harassment, etc.
- I commit to compliance going forward

## 6. External Auditor & Regulator Engagement

| Regulator / Auditor | Contact | Engagement Type | Frequency |
|---|---|---|---|
| **Northwind's External Auditor** (PwC) | PwC Austin | Annual financial audit | Annual (Q1) |
| **SOC 2 Auditor** (Big4 firm TBD) | TBD | Security/compliance audit | One-time (2026) |
| **OFAC Screening Service** | Dun & Bradstreet | Sanctions screening API | Ongoing (per vendor) |
| **State Labor Commissioner** | Texas TWCC | Workers compensation audit | As-needed |

## 7. Escalation & Board Reporting

**Material compliance breaches** (Sev-1) are escalated:
1. → General Counsel and Chief Privacy Officer (immediate)
2. → CEO + VP Security (within 4 hours)
3. → Board Audit Committee (within 24 hours if impact > $100K or regulatory fine risk)
4. → External counsel if litigation risk

**Quarterly compliance report** to Board:
- Status of all frameworks
- Any material non-compliance or remediation efforts
- Upcoming audit schedules
- Regulatory changes affecting Northwind

---

**Related Policies:** Anti-Bribery & Corruption Policy; Data Classification & Retention Policy; Vendor Procurement & Third-Party Risk Policy; Acceptable Use Policy; Incident Response Runbook.
