---
title: Data Subject Rights Procedure
doc_id: data-priv-data-subject-rights-procedure
owner: Chief Privacy Officer
last_updated: 2026-04-15
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Data Subject Rights Procedure

## 1. Overview

This procedure defines how Northwind Technologies receives, processes, and fulfills **data subject requests** under GDPR Articles 12–22 and other privacy laws (CCPA, state laws). A **data subject request** is any communication from an individual asking to access, delete, correct, port, restrict, or object to processing of their personal data.

## 2. Request Channels and Intake

### 2.1 How Northwind Receives Requests

Data subject requests may arrive via:
- **Email**: privacy@northwind.com (monitored 24/5, responded to within 24 business hours)
- **In-app portal**: Data Subject Request form at northwindcloud.com/privacy/my-data
- **Phone**: +1-512-NORTHWIND, option 3 (Privacy Team)
- **Third-party intermediary**: A legal representative, family member, or authorized agent acting on behalf of the data subject
- **Regulatory referral**: A data protection authority forwarding a data subject complaint

### 2.2 Request Verification

Upon receipt, the Privacy Team must:
1. **Verify identity**: Confirm the requester is the data subject or a legally authorized representative. If doubt exists, request government-issued ID or power of attorney.
2. **Log the request**: Record in the **Data Subject Request Register** (maintained in a secure, encrypted spreadsheet):
   - Request ID (unique number, e.g., DSR-2026-0001)
   - Requester name and contact
   - Request date and type (access, deletion, rectification, etc.)
   - Data subject identity (if different from requester)
   - Deadline (typically Day 30)
   - Status (received, under review, completed, denied)

## 3. Request Types and Procedures

### 3.1 Right of Access (GDPR Article 15, CCPA § 1798.100)

**Request**: "Give me a copy of all data you have about me."

**Procedure**:
1. Search all systems where personal data is stored (customer databases, CRM, email, support tickets, log files, analytics platforms).
2. Compile a report including:
   - All personal data fields (name, email, usage history, etc.)
   - Source of the data
   - Purpose and legal basis for processing
   - Recipients (which teams, vendors, or third parties have accessed this data)
   - Retention period
3. Deliver in a **structured, commonly used, machine-readable format** (CSV or JSON preferred).
4. **Deadline**: 30 days from receipt.
5. **Cost**: Free (unless the request is manifestly unfounded or excessive; may charge reasonable fees).

**Example response**: A file named "user-data-export-2026-04-20.csv" containing 47 fields of customer usage, contract terms, and communication history.

### 3.2 Right of Rectification (GDPR Article 16)

**Request**: "This information about me is wrong; please correct it."

**Procedure**:
1. Verify the data is inaccurate or incomplete.
2. Correct the record in all systems where it appears.
3. Notify **all recipients** who have received the inaccurate data (e.g., third-party vendors, customers who purchased data integrations). Document notifications.
4. **Deadline**: 30 days.
5. Provide written confirmation to the data subject.

**Note**: If the data subject claims data is inaccurate but it is factually correct (e.g., a legitimate audit finding), Northwind may refuse but must document the reason and offer the data subject the right to append a correction statement.

### 3.3 Right of Erasure (GDPR Article 17)

**Request**: "Delete all data you have about me."

**Procedure**:
1. **Check exceptions**: Erasure may be refused if:
   - Data is necessary to fulfill an active contract (e.g., customer still has an account).
   - Data is required by law (e.g., tax records must be kept 7 years).
   - Data is subject to a legal hold or ongoing litigation.
   - Northwind has a documented **Legitimate Interest Assessment (LIA)** that overrides the request (rare).
   - See the **Data Classification & Retention Policy** for retention rules.
2. If erasure is permitted, delete from all systems (databases, backups, archives, archives of archives).
3. Notify recipients who have received the data.
4. **Deadline**: 30 days.
5. **Special case – Backups**: Deleted personal data in automated backups does **not** need to be individually purged if backups are encrypted and deleted per the retention schedule (e.g., 90-day backup cycle).

### 3.4 Right to Restrict Processing (GDPR Article 18)

**Request**: "Don't use my data for marketing anymore, but keep it stored."

**Procedure**:
1. Mark the data subject's record with a **restriction flag** in the database.
2. Implement technical controls to prevent processing (e.g., exclude from email campaigns, pause analytics tracking).
3. Notify recipients who have received unrestricted data.
4. **Deadline**: 30 days.
5. Continue to honor the restriction until the data subject requests it be lifted or a legal exception applies.

### 3.5 Right to Data Portability (GDPR Article 20)

**Request**: "Give me my data in a format I can import into a competitor's tool."

**Procedure**:
1. Compile all personal data in a **machine-readable format** (JSON, CSV, XML).
2. **Include all fields**: Any data the data subject provided or data Northwind collected about them (excluding derived/inferred data, which is ambiguous under GDPR).
3. If the data subject specifies a third-party recipient, **directly transmit** to that recipient if technically feasible.
4. **Deadline**: 30 days.
5. **Cost**: Free.
6. Format must be **structured** (not PDF, not a human-readable report).

**Example format**:
```json
{
  "user_id": "cust-12345",
  "email": "alice@example.com",
  "account_created": "2023-06-01",
  "features_used": ["reporting", "api", "integrations"],
  "data_processed_count": 1_500_000,
  "contracts": [{"id": "contract-789", "start": "2023-06-01"}]
}
```

### 3.6 Right to Object (GDPR Article 21)

**Request**: "Stop processing my data for marketing/profiling/[purpose]."

**Procedure**:
1. Cease processing for the stated purpose within 30 days.
2. If Northwind claims a **compelling legitimate interest** that overrides the objection, document the Legitimate Interest Assessment (LIA) and provide it to the data subject.
3. If no legitimate interest exists, honor the objection.
4. Update the data subject's preference record.
5. **Marketing objections** (GDPR Article 21.3) must be honored immediately; business contact may continue if necessary for contract fulfillment.

## 4. Timelines and Extensions

| Scenario | Timeline |
|----------|----------|
| **Standard request** | 30 days from receipt |
| **Complex request** (100+ fields, multiple systems) | 30 + 60 days (extension must be communicated by Day 30) |
| **Unfounded or excessive request** | May refuse or charge reasonable fees; must explain reason within 30 days |
| **Request for more info** | Data subject has 14 days to provide ID or clarification; clock restarts on Day 1 of receipt |

## 5. Request Register and Tracking

The Privacy Team maintains a **Data Subject Request Register** with entries for:
- Request ID, date, type, deadline, status
- Any exemptions claimed (legal hold, legitimate interest, etc.)
- Resolution and completion date

Register is reviewed monthly; gaps or overdue requests trigger escalation to the Chief Privacy Officer and VP Security.

## 6. Denial and Appeals

If Northwind denies a request (e.g., "Data is subject to active litigation"), the response must include:
- Clear explanation of the reason
- Reference to the applicable law or exemption
- Information on how to appeal to the Data Protection Authority (DPA) of the member state where the data subject resides
- Escalation path within Northwind (contact Chief Privacy Officer at privacy@northwind.com)

## 7. Training and Escalation

All Privacy Team members and designated data owners complete quarterly training on:
- GDPR/CCPA rights
- How to authenticate requester identity
- How to identify personal data across systems
- Deadline tracking and escalation

**Escalation triggers**:
- Request involves legal hold or litigation → escalate to General Counsel immediately
- Request involves health/biometric data → escalate to VP People
- Request is from a regulatory authority → escalate to VP Security and Chief Privacy Officer
- Request deadline at risk → escalate to Chief Privacy Officer

---

**Document owner:** Chief Privacy Officer  
**Last approved:** 2026-04-15 by Privacy Leadership  
**Next review:** 2027-04-15
