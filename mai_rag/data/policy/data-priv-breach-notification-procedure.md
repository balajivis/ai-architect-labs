---
title: Data Breach Notification Procedure
doc_id: data-priv-breach-notification-procedure
owner: Chief Privacy Officer
last_updated: 2026-04-20
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Data Breach Notification Procedure

## 1. Overview

A **data breach** is the unauthorized access, disclosure, or loss of personal data. This procedure defines how Northwind detects, investigates, and notifies affected parties (data subjects, regulators, customers) in compliance with GDPR Article 33, state privacy laws (CCPA, etc.), and contractual obligations.

**Key timeline**: GDPR requires notification to regulators within **72 hours** of discovery and to data subjects **without undue delay** if high risk.

## 2. Breach Definition and Scope

### 2.1 What Constitutes a Breach

A breach occurs when:
- **Unauthorized access**: Someone who should not have access gains it (e.g., attacker compromises password)
- **Unauthorized disclosure**: Data is transferred to an unauthorized recipient (e.g., file shared publicly on the internet)
- **Unauthorized alteration**: Data is modified without consent (e.g., attacker changes salary records)
- **Accidental loss**: Data is deleted, corrupted, or rendered inaccessible by mistake (e.g., hard drive fails without backup)

**Triggering factors**:
- Server is breached; attacker downloads customer database
- AWS S3 bucket is misconfigured; data is publicly readable
- Employee laptop with unencrypted customer data is stolen
- Vendor data center is compromised; Northwind customer data is exposed
- Email with confidential data is sent to wrong recipient
- Database backup is lost during transit

### 2.2 Scope (Personal Data Only)

Breaches of **personal data only** are notifiable. Breaches of non-personal business data (source code, business plans, trade secrets) may be serious but are not GDPR breaches.

**Personal data = any data that identifies or can identify an individual**: name, email, SSN, IP address, customer ID (if linkable to name), etc.

**Non-personal data = cannot identify individual**: anonymized statistics, aggregate metrics, public company information.

## 3. Breach Detection and Initial Reporting

### 3.1 How Breaches Are Detected

**Automated detection**:
- SIEM/intrusion detection system (Splunk) detects suspicious network activity
- Cloud security posture tools (Azure Security Center, AWS GuardDuty) flag misconfigured resources
- Antivirus/EDR alerts on endpoint compromise
- Monitoring alerts (Datadog) flag unusual data access patterns

**Manual detection**:
- Employee reports suspicious activity (e.g., "I received a phishing email claiming to be from IT")
- Customer reports data exposure (e.g., "I found my data on the dark web")
- Vendor notifies Northwind of a breach affecting Northwind (e.g., AWS reports a compromised API key)
- Third-party bug bounty researcher reports vulnerability

**Media/regulatory notification**:
- News article discloses a breach
- Regulator (DPA) forwards a data subject complaint alleging unauthorized access

### 3.2 Initial Reporting Obligation

**Any employee who discovers or suspects a breach must immediately:**

1. **Stop investigating** — do not attempt to access the data, delete evidence, or run recovery tools
2. **Notify the Security Team** — email security@northwind.com or call +1-844-NORTHWIND-SEC (24/7 hotline)
3. **Document the finding** — what was discovered? when? how?
4. **Preserve evidence** — do not shut down systems; keep logs intact
5. **Maintain confidentiality** — do not discuss the breach with colleagues outside the incident response team

**Response SLA**: Security Team acknowledges receipt within 1 hour; incident commander is assigned within 2 hours.

## 4. Breach Investigation and Assessment

### 4.1 Incident Severity Classification

Once a breach is reported, the incident commander conducts a **rapid assessment** to assign severity (per **Incident Response Runbook**):

| Severity | Impact | RTO | Examples | Notify Execs |
|----------|--------|-----|----------|--------------|
| **Sev-1** | 10K+ records of sensitive PII exposed; complete service outage | 4 hours | Database dump posted to internet; ransomware encrypts all customer data | YES (within 30 min) |
| **Sev-2** | 100–10K records exposed; service degradation | 8 hours | Employee laptop stolen with customer contracts; misconfigured S3 bucket | YES (within 2 hours) |
| **Sev-3** | <100 records; isolated incident | 24 hours | Single employee email sent to wrong recipient; weak password used by one dev | YES (within 8 hours) |
| **Sev-4** | Attempted breach but data not accessed; vulnerability with no exploitation path | No SLA | Failed login attempts; outdated SSL cert (not yet expired) | Track in security log |

### 4.2 Breach Scope Assessment

Investigate:
- **Which data types were exposed?** (names, emails, SSNs, contracts, etc.)
- **How many data subjects affected?** (exact count if possible; range if not)
- **What classifications were affected?** (Public, Internal, Confidential, Restricted — per **Data Classification & Retention Policy**)
- **Was data encrypted?** (If yes, encryption likely prevents access; re-assess risk)
- **How long was data exposed?** (Minutes, hours, days?)
- **Who had access?** (Legitimate users? Attackers? Public?)

**Risk assessment**:
- **High risk** → data subject has high probability of identity theft, financial loss, or harm
- **Low risk** → data exposure is temporary, data is encrypted, or harm is unlikely

**Example risk assessments**:

| Scenario | Data | Risk Level | Reason |
|----------|------|-----------|--------|
| AWS S3 bucket misconfigured; customer names, emails, usage logs visible for 2 hours; discovered via scanner; access logs show no unauthorized downloads | Names, emails, usage logs | Low | Data was encrypted; access logs show no theft; exposure was brief |
| Employee laptop stolen; customer contracts (PDFs) on unencrypted drive | Contracts (names, pricing, dates) | High | Unencrypted; attacker has physical device; customer PII is in contract text |
| Email sent to wrong recipient (wrong email address); contained one customer's SSN | SSN (Restricted PII) | High | SSN is sensitive; recipient is unknown; impossible to recall email |

## 5. Notifications and Escalation

### 5.1 Internal Escalation

**Immediately notify** (within 2 hours):
- **CEO**: Sev-1 and Sev-2 breaches only
- **VP Security**: All breaches
- **Chief Privacy Officer**: All breaches (GDPR compliance lead)
- **General Counsel**: Sev-1, Sev-2, and any breach involving contracts or litigation
- **Board of Directors**: Sev-1 breaches only (within 24 hours)

**Notification format**: Secure conference call or in-person meeting (not email; email is not secure for sensitive breach info). Conference bridge: TBD (established during incident).

**Information to provide**:
- What happened (high-level summary)?
- When was it discovered? When did it occur?
- How many data subjects affected?
- What data was exposed?
- Is the breach ongoing? (Is it still happening, or has it been contained?)
- What actions have been taken so far?
- What is the timeline for resolution?
- What is the risk to Northwind (financial, reputational, regulatory)?

### 5.2 Customer Notification

**Rule**: Customers must be notified if:
1. A Sev-1 or Sev-2 breach occurs (high risk to customer data)
2. The customer's data or data of their employees was exposed
3. The risk assessment indicates notification is necessary

**Notification timeline**: Without undue delay; ideally within 24–48 hours of discovery.

**Notification method**: Email from Chief Privacy Officer; subject = "Security Incident Notification – [Customer Name]"

**Contents of notification**:
- What happened (in plain language, non-technical)
- When did it occur?
- What data was exposed?
- Who was affected (which of the customer's employees/users)?
- What is Northwind doing to fix it?
- What can the customer do to protect themselves?
- Escalation contact (Chief Privacy Officer email and phone)
- Link to detailed incident report (if available)

**Example notification**:

> "Dear [Customer]: On [date], Northwind discovered that a subset of customer contracts containing employee names and email addresses were accessible via an misconfigured cloud storage bucket for approximately [duration]. This affected [X] employees in your organization. We immediately secured the bucket and found no evidence of unauthorized access in server logs. We are conducting a full investigation and will provide an update within [X] days. If you have questions, please contact our Chief Privacy Officer at privacy@northwind.com or +1-512-NORTHWIND."

### 5.3 Regulatory Notification (DPA Notification)

**GDPR Article 33 requirement**: Notify the relevant Data Protection Authority (DPA) within **72 hours** of discovery if:
- The breach poses a **risk to rights or freedoms** of data subjects (not every breach requires notification)
- The data is classified Confidential or Restricted
- The exposure is significant (>100 records)

**Process**:
1. **Determine which DPA**: If data subjects are in multiple EU countries, notify each country's DPA. For a multi-country breach, notify the "lead DPA" (e.g., Ireland if EU subsidiary's data).
2. **Complete DPA notification form** (varies by country; example from Ireland DPC at https://www.dataprotection.ie/)
3. **Notification includes**:
   - Nature of the breach
   - Categories and approximate number of data subjects
   - Likely consequences
   - Measures taken or proposed to mitigate risk
   - Contact person for follow-up

**Who notifies**: Chief Privacy Officer in consultation with General Counsel.

**Evidence**: Breach report, notification letter, and DPA correspondence are filed in the Breach Register.

### 5.4 Media and Public Disclosure

If a breach is large (10K+ records) or a news outlet reports it:

**Communications plan**:
- **PR team** prepares a statement (factual, non-defensive, transparent)
- **Statement is approved** by CEO, VP Security, General Counsel, Chief Privacy Officer
- **Statement is published** on northwindcloud.com/news and shared with media

**Example statement**:

> "Northwind Technologies discovered a security incident on [date] affecting approximately [X] customer records. We immediately took action to secure our systems and began a thorough investigation. We have found no evidence that customer payment information was exposed. We are notifying affected customers and regulatory authorities as required by law. Northwind remains committed to protecting customer data. [Link to detailed FAQ]"

## 6. Breach Investigation and Root Cause Analysis

### 6.1 Investigation Timeline

| Phase | Timeline | Activities |
|---|---|---|
| **Containment** | 0–4 hours (Sev-1) | Isolate affected systems; preserve evidence; identify scope |
| **Investigation** | 4 hours–7 days | Root cause analysis; determine how breach occurred |
| **Eradication** | 4 hours–30 days | Patch vulnerability; remove malware; rotate credentials |
| **Recovery** | Parallel with eradication | Restore systems; validate integrity; test security controls |
| **Post-mortem** | 24 hours–30 days after recovery | Document findings; identify lessons; implement preventive measures |

See **Incident Response Runbook** for detailed investigation procedures.

### 6.2 Breach Report Contents

After investigation is complete, the **Breach Report** is prepared for Chief Privacy Officer and Board:

- **Executive summary**: What happened; impact; key findings
- **Timeline**: When was the breach discovered? When did it occur? When was it contained?
- **Scope**: How many data subjects? Which data types? Which systems?
- **Root cause**: How did it happen? (misconfigured security group, weak password, phishing email, etc.)
- **Forensic findings**: Evidence from logs, file systems, memory, etc.
- **Containment actions**: What was done to stop the breach?
- **Notifications sent**: To regulators, customers, media
- **Corrective actions**: What will be done to prevent recurrence?
- **Financial impact**: Cost of investigation, potential fines, reputational impact
- **Lessons learned**: What should Northwind change?

## 7. Breach Register and Audit Trail

### 7.1 Breach Register

The **Breach Register** is a confidential record of all breaches at Northwind, maintained by the Chief Privacy Officer:

| Breach ID | Date Discovered | Data Exposed | Subjects Affected | Severity | Notified Regulators | Notified Customers | Status | Outcome |
|---|---|---|---|---|---|---|---|---|
| BR-2026-0001 | 2026-03-15 | Customer names, emails | 500 | Sev-2 | YES (Ireland DPC) | YES | Closed | No regulatory fine; customer notified within 24h |
| BR-2026-0002 | 2026-04-10 | S3 bucket misconfigured | 100 | Sev-3 | NO | NO | Closed | Bucket secured; no unauthorized access found |

**Register location**: `/compliance/breach-register/` (encrypted, access restricted to Chief Privacy Officer, VP Security, General Counsel).

**Retention**: Breach Register entries are retained indefinitely (for historical reference and audit trail).

### 7.2 Post-Breach Audit

Within **30 days** of breach closure, the Chief Privacy Officer conducts a **post-breach audit**:

- Was the breach detected promptly?
- Was the investigation thorough and timely?
- Were notifications sent according to requirements?
- Were corrective actions effective?
- Were preventive measures implemented?

**Findings** are reported to the Board and VP Security. If process gaps are identified, they are documented and tracked for remediation.

## 8. Cross-Reference to Related Policies

- **Data Classification & Retention Policy**: Classification determines breach risk and notification requirements
- **Incident Response Runbook**: Incident detection, classification, escalation, investigation procedures
- **Information Security Policy**: Security controls to prevent breaches
- **GDPR Compliance Policy**: Data subject rights and regulatory obligations
- **Data Processing Agreement (DPA) Standard**: If breach involves processor data

## 9. Breach Prevention Best Practices

While this procedure is for **responding to breaches**, Northwind prioritizes **prevention**:

- **Encryption**: All Confidential/Restricted data encrypted at rest and in transit
- **Access controls**: Least privilege; MFA mandatory; regular access reviews
- **Security training**: Annual awareness training; phishing simulations
- **Vulnerability management**: Regular scans; penetration testing; bug bounty program
- **Incident response drills**: Quarterly tabletop exercises to test response readiness
- **Backup and recovery**: Regular backups tested; recovery time objective (RTO) defined

---

**Document owner:** Chief Privacy Officer  
**Last approved:** 2026-04-20 by Privacy Leadership  
**Next review:** 2027-04-20
