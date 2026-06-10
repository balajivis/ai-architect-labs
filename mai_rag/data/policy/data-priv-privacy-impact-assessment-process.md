---
title: Privacy Impact Assessment Process
doc_id: data-priv-privacy-impact-assessment-process
owner: Chief Privacy Officer
last_updated: 2026-04-18
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Privacy Impact Assessment Process

## 1. Overview

A **Data Protection Impact Assessment (DPIA)**, also called a **Privacy Impact Assessment (PIA)**, is a structured evaluation of a proposed data processing activity to identify and mitigate privacy risks before the activity launches. DPIAs are required under GDPR Article 35 for high-risk processing.

**Requirement**: All teams proposing new data processing (features, integrations, analytics, etc.) must complete a DPIA form and submit it to the Chief Privacy Officer **at least 30 days before launch**. Failure to complete a DPIA may result in project delay or suspension.

## 2. When a DPIA is Required

A DPIA is **mandatory** for processing activities that are:

### 2.1 High-Risk Automatic Triggers

- **Large-scale processing of special categories of data**: EU/EEA personal data combined with health, race, religion, sexual orientation, criminal records, or union membership data
- **Automated decision-making that produces legal or similarly significant effects**: AI/ML algorithms that determine eligibility, pricing, service denial, or hiring
- **Systematic monitoring of a public area**: Cameras, sensor data, continuous tracking of user behavior
- **Processing of children's data at scale**: Under GDPR 8, children (under 16) require parental consent; large-scale children's data triggers DPIA
- **High-risk data categories + high-risk recipients**: Confidential/Restricted data + third-party sharing (especially cross-border)
- **New use of existing data in a way not disclosed to data subjects**: Repurposing customer data for AI training without re-consent

### 2.2 Discretionary Assessment (Recommended)

Even if not an automatic trigger, a DPIA is **recommended** for:
- New data collection or integration
- Changes to data retention or access controls
- Third-party sharing of customer data
- Any data processing that was previously manual and is now automated

**When in doubt, request a DPIA.** The cost of a DPIA (~4 hours) is far less than the cost of a privacy breach or GDPR fine.

## 3. DPIA Form and Submission Process

### 3.1 Who Completes the DPIA

**Responsibility**: The **feature owner or project lead** completing the work is responsible for completing the DPIA. They work with:
- **Privacy Team** (Chief Privacy Officer or Privacy Analyst) for guidance
- **Security Team** (VP Security) for risk assessment
- **Legal Team** (General Counsel) if data sharing with third parties or regulated data

### 3.2 DPIA Template and Content

Submit the DPIA form (template: `privacy.dpia-template@northwind.com`) with the following sections:

**1. Overview**
- Project/feature name
- Team and project lead
- Proposed launch date
- Link to product requirements or design doc

**2. Data Processing Activity**
- What personal data is being collected or used? (list specific fields: name, email, SSN, etc.)
- Which categories of data subjects? (customers, employees, prospects, children, etc.)
- Is this data EU/EEA personal data? (yes/no; if yes, triggers GDPR Articles 12–22 obligations)
- Processing purpose(s) (e.g., "customer analytics", "fraud detection", "personalized recommendations")
- Processing duration (temporary, indefinite, tied to contract, etc.)
- Who will have access? (internal teams, third parties, business partners, public?)
- Will data be combined with other data sets? (e.g., customer purchase history + demographic data = higher risk)
- Will data be transferred outside EU/EEA? (if yes, see **Cross-Border Data Transfer Policy**)

**3. Legal Basis**
Identify which GDPR lawful basis (from **GDPR Compliance Policy**) applies:
- [ ] Consent – data subject explicitly opted in
- [ ] Contract – processing is necessary to fulfill a service agreement
- [ ] Legal Obligation – required by law
- [ ] Vital Interests – emergency/life-saving (rare)
- [ ] Public Task – (not applicable for B2B SaaS)
- [ ] Legitimate Interest – Northwind has a documented business need

If **Legitimate Interest** is claimed, complete a **Legitimate Interest Assessment (LIA)**:
- What is Northwind's business purpose?
- How necessary is this processing to that purpose?
- Could the purpose be achieved with less personal data?
- What are the data subject's reasonable expectations?
- Does Northwind's interest override the data subject's privacy rights? (assessment: yes/no)

**4. Privacy Risks and Safeguards**

| Risk | Likelihood | Severity | Mitigation | Residual Risk |
|------|------------|----------|-----------|---------------|
| Unauthorized access to personal data | Medium | High | Encrypt Confidential data; limit access to 5 authorized engineers | Low |
| Data subject cannot exercise GDPR rights (access, deletion) | Low | High | Design system with data export API; retention schedule supports right of erasure | Low |
| Profiling or automated decision-making creates disparate impact | Medium | Medium | Audit algorithm for bias every 90 days; maintain human-review process for decisions | Low |
| Cross-border transfer violates GDPR Article 44 | Low | Critical | Use Standard Contractual Clauses; encrypt data in transit | Low |
| Data retention exceeds necessity | Low | Medium | Set automatic deletion at 3 years; flag for Chief Privacy Officer if retention extends beyond contract | Low |

**5. Data Subject Rights Support**

- How will Northwind support data subjects exercising rights under GDPR Articles 15–22?
  - [ ] Access: Yes (export API; CSV download)
  - [ ] Rectification: Yes (self-service profile edit)
  - [ ] Erasure: Yes (with exceptions for contract/legal hold)
  - [ ] Restriction: Yes (opt-out flag; cease processing)
  - [ ] Portability: Yes (machine-readable export)
  - [ ] Object: Yes (unsubscribe; pause analytics)
  - [ ] Automated decision: Yes (human review available)

**6. Vendor and Subprocessor Assessment**

- Will any third parties process personal data? (vendors, contractors, cloud providers)
- For each third party, confirm:
  - [ ] Data Processing Agreement (DPA) is in place
  - [ ] Vendor has SOC 2 or ISO 27001 certification
  - [ ] Sub-processors are listed and approved

See the **Data Processing Agreement (DPA) Standard** for requirements.

**7. Data Breach Scenario and Incident Response**

- If this data were breached, how many data subjects would be affected? (low: <100; medium: 100–10K; high: 10K+)
- Would the breach pose high risk to rights/freedoms of data subjects?
- How would Northwind notify affected data subjects and regulators?
- Cross-reference: **Incident Response Runbook** and **Data Breach Notification Procedure**

**8. Conclusion and Sign-Off**

- Overall privacy risk: Low / Medium / High / Critical
- Recommended action:
  - [ ] Proceed as planned
  - [ ] Proceed with mitigations (list them)
  - [ ] Redesign to reduce risk (specify what must change)
  - [ ] Halt until risks are addressed

**Sign-offs**:
- [ ] Feature owner (project lead)
- [ ] Chief Privacy Officer (or Privacy Analyst delegated)
- [ ] VP Security (for security assessment)
- [ ] General Counsel (if data sharing or regulated data)
- [ ] VP Engineering (if major architectural change)

## 4. Risk Assessment Framework

### 4.1 Likelihood and Severity Matrix

| Likelihood | Severity | Overall Risk |
|-----------|----------|--------------|
| Low + Low | **Low** | Minimal risk; proceed |
| Low + High | **Medium** | Mitigate; proceed with controls |
| Medium + Medium | **Medium** | Mitigate; proceed with controls |
| Medium + High | **High** | Re-design or seek approval from Chief Privacy Officer |
| High + High | **Critical** | Halt; re-design; Chief Privacy Officer approval required |

### 4.2 Typical Risk Mitigations

| Risk | Mitigation Example |
|------|-------------------|
| Unauthorized data access | Encrypt at rest (AES-256); apply least-privilege access; enable audit logging; monitor access |
| Data breach / exfiltration | Minimize data collection (collect only necessary fields); implement DLP rules; background-check contractors with access |
| Lack of GDPR rights support | Design system with data export capability; implement auto-delete after retention period; honor opt-out requests within 30 days |
| Cross-border transfer | Use Standard Contractual Clauses (SCC); encrypt data at rest and in transit; transfer only to countries with data protection laws |
| Profiling or discrimination | Exclude sensitive fields from ML models (race, gender, age); audit model outputs monthly for disparate impact; maintain human appeal |

## 5. DPIA Approval and Documentation

### 5.1 Submission and Review Timeline

| Step | Timeline | Owner |
|------|----------|-------|
| Project lead completes DPIA form | 30 days before launch | Feature owner |
| Privacy Team reviews | Within 5 business days | Chief Privacy Officer |
| VP Security security assessment | Within 5 business days | VP Security |
| General Counsel review (if needed) | Within 5 business days | General Counsel |
| Sign-off and approval | Day 25 | Chief Privacy Officer |
| **No approval = no launch** | Day 30 | Escalate to CEO |

### 5.2 Filing and Retention

All completed DPIAs are retained in a **DPIA Register** maintained by the Chief Privacy Officer:
- Archive: `/compliance/dpia-register/` (encrypted, access restricted to privacy/legal/security teams)
- Fields: DPIA ID, project name, date submitted, overall risk, approval status, review team members
- Retention: 3 years after project end or legal hold, whichever is longer

### 5.3 Re-Assessment Triggers

A DPIA must be re-assessed (new DPIA or amendment) if:
- The processing purpose materially changes
- New personal data categories are added
- Data retention extends beyond original approval
- A third party gains access to data
- A data breach or incident occurs involving the processing activity
- A regulator raises concerns about the processing

## 6. Escalation and Appeals

If the Privacy Team recommends halting or significantly redesigning a project due to privacy risks:

1. **Feature owner discusses findings** with Chief Privacy Officer and VP Security
2. **Risk mitigation options** are explored (may take 5–10 days)
3. If mitigations are insufficient and **project is blocked**, escalate to:
   - VP Engineering (if architectural redesign is needed)
   - CEO (if business case overrides privacy risk; rare; requires documented Board approval)

**Precedent**: Northwind has never approved a project blocked on privacy grounds without redesign. Risk mitigation is always preferred over risk acceptance.

## 7. Cross-Reference to Related Policies

- **GDPR Compliance Policy**: Legal basis, data subject rights, transfer mechanisms
- **Data Classification & Retention Policy**: Risk classification informs DPIA severity
- **Information Security Policy**: Security controls support privacy safeguards
- **Incident Response Runbook**: Breach notification and Sev levels
- **Data Breach Notification Procedure**: Post-breach DPIA analysis and lessons learned

---

**Document owner:** Chief Privacy Officer  
**Last approved:** 2026-04-18 by Privacy Leadership  
**Next review:** 2027-04-18
