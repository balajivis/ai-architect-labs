---
title: Data Processing Agreement (DPA) Standard
doc_id: data-priv-dpa-standard
owner: Chief Privacy Officer
last_updated: 2026-04-15
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Data Processing Agreement (DPA) Standard

## 1. Overview and Legal Requirement

A **Data Processing Agreement (DPA)** is a contract required under GDPR Article 28 whenever Northwind Technologies (the **Data Controller**) engages a **Data Processor** — a third party that processes personal data on Northwind's behalf.

**Scope**: This standard applies to all vendor contracts involving:
- Processing of EU/EEA personal data
- Access to Northwind customer data
- Cloud services (AWS, Azure, SaaS vendors)
- Contractors and consultants accessing personal data

## 2. Data Controller vs. Data Processor

### 2.1 Northwind as Data Controller
Northwind is the controller when it:
- Determines the purpose and means of personal data processing
- Decides what data to collect, how long to keep it, and who can access it
- Makes decisions about retention, deletion, or disclosure

**For customer personal data in Northwind Cloud**: Northwind is the controller; customers may also be controllers for their own data.

### 2.2 Data Processor Role
A processor is a vendor that:
- Processes personal data **only as instructed** by Northwind
- Does not decide the purpose or means
- Is bound by the DPA to follow Northwind's documented processing instructions

**Examples**: AWS (infrastructure), Salesforce (CRM), Datadog (monitoring), contractors building features.

### 2.3 Joint Controllers
If two parties jointly determine processing purposes/means, they are **Joint Controllers** and must execute a **Joint Control Agreement** outlining responsibilities. This is rare but may apply if Northwind partners with another company on a product.

## 3. Required DPA Clauses (GDPR Article 28)

All Northwind DPAs must include the following mandatory clauses:

### 3.1 Subject Matter and Duration
- **What data**: Types of personal data (e.g., customer email, usage logs, billing information)
- **Categories of data subjects**: Customers, end-users, employees
- **Nature and purpose**: Processing scope (e.g., "cloud hosting for Northwind Cloud SaaS platform")
- **Duration**: Contract term or as specified

### 3.2 Processing Instructions
The processor must process personal data **only as documented in writing** by Northwind:
- Initial processing instructions are attached as Exhibit A
- Any new processing requires a written amendment signed by both parties
- The processor **may not** use personal data for any other purpose

### 3.3 Processor Personnel Confidentiality
The processor must ensure employees, contractors, or agents with access to personal data:
- Are bound by confidentiality (in writing)
- Have completed data protection training
- Are subject to disciplinary action for breaches

### 3.4 Security and Incident Management
The processor must implement:
- Technical and organizational measures proportional to the classification level (see **Data Classification & Retention Policy**)
- Encryption of Confidential and Restricted data in transit and at rest
- Security incident notification within **48 hours** of discovery
- Incident investigation and evidence preservation (see **Incident Response Runbook** for severity definitions)

### 3.5 Subprocessors
The processor **may not engage subprocessors** without Northwind's prior written consent. For each subprocessor:
- The processor must provide a list and notify Northwind of any changes
- Northwind may object to a subprocessor within 30 days; if objection is reasonable, Northwind may terminate the contract without penalty
- The processor remains liable for subprocessor performance

### 3.6 Data Subject Rights
The processor must:
- Assist Northwind in responding to data subject access requests (GDPR Articles 12–22) within the response timeline
- Implement technical controls to support rights like data portability and deletion
- Support Data Protection Impact Assessments (DPIA) by providing information about processing activities
- Not directly respond to data subjects; refer all requests to Northwind

### 3.7 Data Return or Deletion
Upon contract termination, the processor must:
- Return all personal data to Northwind (in machine-readable format if requested)
- Delete all copies except as required by law (retention schedule confirmed in writing)
- Provide written certification of deletion within 30 days

### 3.8 Audit and Inspection Rights
Northwind (or a contracted auditor) may:
- Request evidence of security compliance (e.g., SOC 2 report, security assessment)
- Conduct on-site audits of the processor's systems
- Review logs and incident reports
- Audit frequency: minimally annual for High Risk vendors; upon reasonable notice

### 3.9 International Transfers
If the processor stores/transfers personal data outside the EU/EEA, the DPA must include:
- **Standard Contractual Clauses (SCCs)** as the legal mechanism
- Supplementary technical measures (encryption, access controls)
- Reference to the **Cross-Border Data Transfer Policy**

### 3.10 Liability and Indemnification
The processor:
- Remains liable for GDPR fines and damages caused by its breach
- Indemnifies Northwind against regulatory fines and lawsuits arising from the processor's failure to comply
- Maintains cyber liability and errors & omissions insurance (minimally EUR 2 million coverage for processors handling Confidential/Restricted data)

## 4. Northwind DPA Template

All vendor contracts must incorporate (or reference) the **Northwind DPA Template** maintained by the Chief Privacy Officer. Standard sections:

```
EXHIBIT A: PROCESSING INSTRUCTIONS
- Data types: [list]
- Categories of data subjects: [list]
- Processing purpose: [e.g., "cloud hosting", "email delivery", "analytics"]
- Processor personnel with access: [roles/teams]
- Data location: [e.g., "US-East-1, US-West-2"]
- Retention period: [align with Data Classification & Retention Policy]

EXHIBIT B: SECURITY REQUIREMENTS
- Encryption standard: [AES-256 at rest; TLS 1.3 in transit for Confidential/Restricted]
- Access controls: [RBAC, MFA where applicable]
- Audit rights: [annual SOC 2, incident notification within 48 hours]
- Incident escalation: [contact security@northwind.com]

EXHIBIT C: SUBPROCESSORS
- Existing subprocessors: [list with processing purposes]
- Change notification: [30 days' notice; Northwind may object]

EXHIBIT D: STANDARD CONTRACTUAL CLAUSES (SCC)
- [Incorporated by reference if non-EU processing]
```

## 5. Vendor Onboarding and DPA Lifecycle

### 5.1 Pre-Engagement
1. Vendor screening questionnaire (privacy.questionnaire@northwind.com) covers:
   - Scope of personal data access
   - Processing locations
   - Subprocessors
   - Security certifications
2. Risk classification: Low (limited data), Medium (customer usage data), or High (payment info, health data, large-scale EU personal data)
3. Chief Privacy Officer approves DPA terms before contract signature

### 5.2 Post-Engagement
- DPA and security certifications filed in Vendor Register (maintained by Compliance Team)
- Annual audit of High Risk vendors (SOC 2 Type II, ISO 27001, or equivalent)
- Quarterly review of subprocessor changes

### 5.3 DPA Renewal and Amendment
- DPA is reviewed annually; material changes (new processing purpose, subprocessor, location) require written amendment
- If vendor refuses to sign amended DPA with new requirements, escalate to VP Security for risk acceptance decision

## 6. Vendor Categories and Heightened Due Diligence

| Vendor Type | Data Access | DPA Requirement | Audit Frequency |
|-------------|------------|-----------------|-----------------|
| **Infrastructure** (AWS, Azure) | Confidential/Restricted | Mandatory SCC; SOC 2 Type II required | Annual |
| **SaaS (CRM, HR, Finance)** | Internal/Confidential | Mandatory with standard clauses | Annual if High Risk |
| **Consultants/Contractors** | Variable | Mandatory if any personal data access | Upon engagement |
| **Payment Processors** | Restricted (PCI) | Mandatory SCC; PCI-DSS compliance required | Quarterly |
| **Analytics/Monitoring** | Minimal (aggregated logs only) | May use vendor-provided DPA; minimum audit annually | Annual |

## 7. Escalation and Disputes

If a vendor:
- Refuses to sign a required DPA clause
- Fails a security audit
- Experiences a data breach involving personal data

**Action**: Escalate to VP Security and Chief Privacy Officer. Options include:
1. Negotiate amended terms
2. Implement compensating controls (e.g., encryption, access restrictions)
3. Terminate engagement if risk is unacceptable

---

**Document owner:** Chief Privacy Officer  
**Last approved:** 2026-04-15 by Privacy Leadership  
**Next review:** 2027-04-15
