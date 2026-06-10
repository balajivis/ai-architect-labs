---
title: Data Quality Standard
doc_id: data-priv-data-quality-standard
owner: Chief Data Officer
last_updated: 2026-04-19
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Data Quality Standard

## 1. Overview

Data quality is essential for privacy, security, and regulatory compliance. Inaccurate or incomplete personal data undermines a data subject's ability to exercise GDPR rights (especially the right of rectification). This standard defines quality criteria for all data at Northwind, particularly personal data.

**Scope**: This policy applies to all operational databases, data warehouses, and data lakes that contain personal data or business-critical information.

## 2. Data Quality Dimensions

All data must be evaluated on these dimensions:

### 2.1 Accuracy

Personal data must be **factually correct** and **up-to-date**.

**Standards**:
- Customer name must match government ID or company records
- Email address must be deliverable and verified (bounce checks)
- Phone number must be valid (E.164 format or regional format)
- Address must be a real physical location (via postal database validation)
- Customer company name must match official business registry

**Audit**: Monthly email bounce audit; quarterly address validation; annual customer record spot-check.

**Remediation**: If inaccuracy is discovered, data subject is notified and correction is made within 5 days (see **Data Subject Rights Procedure** for rectification process).

### 2.2 Completeness

Data should contain **all required fields** for the stated purpose.

**Standards**:
- Customer account: name, email, company, country (mandatory); phone (recommended)
- Employee record: name, email, department, manager, hire date (mandatory)
- Contract record: customer name, value, start date, end date (mandatory); renewal date (recommended)

**Audit**: Quarterly review of NULL/missing field counts per data set.

**Remediation**: If critical fields are missing, data owner is notified; deadline to complete is set (e.g., 30 days for customer phone).

### 2.3 Consistency

Data should be **uniform** across systems and **free of contradictions**.

**Standards**:
- Customer email in CRM should match customer email in usage logs
- Employee title in HR system should match title in access control system
- Contract amount in finance system should match contract management system
- Classification (see **Data Classification & Retention Policy**) should be consistent across all references

**Audit**: Quarterly reconciliation of customer and employee records across systems (CRM, database, analytics, HR).

**Remediation**: Single source of truth identified; secondary systems are updated to match.

### 2.4 Validity

Data should **conform to expected format and business rules**.

**Standards**:
- Email addresses must match RFC 5322 format (user@domain.extension)
- Phone numbers must be in E.164 format (+country-area-number)
- Dates must be ISO 8601 format (YYYY-MM-DD)
- Numeric IDs must be positive integers (no negative customer IDs)
- Enum fields (status, type) must be one of predefined values

**Implementation**: Data validation rules in database schema (constraints, triggers) and application validation (before insert/update).

**Audit**: Quarterly sample of 100+ records per data type; flag records that violate rules.

### 2.5 Timeliness

Data should be **current** and **refreshed appropriately**.

**Standards**:
- Customer company size should be refreshed annually (business data changes)
- Customer contact should be verified at account renewal (contact may have changed jobs)
- Employee department/title should be updated same day as HR change
- Usage metrics should be current (no more than 24 hours old)

**Audit**: Check last-update timestamps; flag stale records.

**Remediation**: Automated refresh where possible (integration with HR system, company database); manual refresh on request.

### 2.6 Uniqueness

**Primary keys and unique identifiers must be unique**; no duplicates.

**Standards**:
- No two customer records with the same email (unless customer has multiple accounts)
- No two employees with the same ID
- No two contracts with the same ID + date combination

**Audit**: Monthly uniqueness check on primary key columns.

**Remediation**: Duplicates are identified; if legitimate (customer has multiple accounts), they are flagged; if erroneous, one record is merged/deleted.

## 3. Data Quality Metrics and Thresholds

| Dimension | Target | Warning Threshold | Failure Threshold |
|---|---|---|---|
| **Accuracy** | ≥99% of fields are correct | 95%–99% | <95% |
| **Completeness** | ≥98% of required fields populated | 95%–98% | <95% |
| **Consistency** | ≥99% of records match across systems | 95%–99% | <95% |
| **Validity** | 100% of records conform to format | 98%–100% | <98% |
| **Timeliness** | 100% of data is current per schedule | 95%–100% | <95% |
| **Uniqueness** | 100% of primary keys are unique | 99%–100% | <99% |

**Action on warning**: Data owner is notified; improvement plan is developed.
**Action on failure**: Escalation to Chief Data Officer; data may be flagged as unreliable until remediated.

## 4. Data Quality Governance

### 4.1 Ownership and Accountability

Each data set has a **Data Owner** responsible for quality:

| Data Set | Owner | SLA |
|---|---|---|
| **Customer database** | VP Sales | 99% accuracy + completeness |
| **Employee records** | VP People | 100% accuracy + consistency with HR system |
| **Financial records** | CFO | 100% accuracy + consistency with accounting ledger |
| **Usage logs** | VP Engineering | 98% completeness (some events may be lost in edge cases) |

### 4.2 Data Quality Issues and Escalation

**Data quality issue** = A data set falls below target threshold.

**Escalation ladder**:
1. **Data owner is notified** (automated alert from data quality monitoring)
2. **Root cause analysis** (why did quality degrade? system error? process gap? data entry?)
3. **Remediation plan** (how to fix affected records? prevent recurrence?)
4. **Status tracking** (follow-up until quality is restored)
5. **If not resolved in 30 days** → escalate to Chief Data Officer

### 4.3 Data Quality Tools

Northwind uses automated monitoring to detect quality issues:

- **Data validation rules** (database constraints, application validation)
- **ETL validation** (data pipelines check for completeness, format, uniqueness)
- **Duplicate detection** (automated check for similar records; flag for manual review)
- **Reconciliation** (CRM ↔ database, HR ↔ access control, Finance ↔ general ledger)
- **Anomaly detection** (sudden spike in NULL fields, unusual values flagged)

**Tools**: dbt (data transformation), Great Expectations (validation), custom SQL (reconciliation).

## 5. Personal Data Quality and GDPR Rights

### 5.1 Impact on Right of Rectification

Inaccurate personal data violates GDPR Article 5(1)(a) — "Personal data must be accurate and, where necessary, kept up to date."

When a data subject requests rectification:
- Northwind must correct inaccurate data within 30 days (see **Data Subject Rights Procedure**)
- Northwind must notify all recipients who have received the inaccurate data
- Northwind must investigate why the inaccuracy occurred and prevent recurrence

**Example**: Customer Jane Smith's account shows her company as "Acme Corp" but she actually works at "Acme Inc." Data quality alert triggers → customer corrects via self-service → all systems are updated → audit log confirms correction.

### 5.2 Data Quality Audits for Sensitive Data

**Restricted and Confidential personal data** undergo additional quality audits:

- **Quarterly accuracy spot-check**: 10% sample of records reviewed for factual accuracy
- **Annual completeness audit**: All required fields are present
- **Annual consent audit**: Verify that processing consent is still valid (has data subject revoked consent?)

## 6. Data Quality and Analytics/ML

### 6.1 Training Data Quality

Machine learning models are only as good as their training data. If training data has quality issues:
- Model accuracy degrades
- Model may learn biased patterns from bad data
- Risk of discriminatory outcomes

**Standards**:
- Training data must be representative and balanced (e.g., equal gender distribution if gender is feature)
- Training data must be accurate (labeled correctly; validated by human)
- Training data must not contain sensitive fields (e.g., SSN, address; see **Anonymization & Pseudonymization Standard**)

**Audit**: Before training any new model, data scientist must complete a data quality checklist (accuracy, completeness, validity, no sensitive fields).

### 6.2 Analytics Data Quality

Aggregate analytics (reports, dashboards) are based on underlying data quality. If source data is poor:
- Reports are inaccurate or misleading
- Business decisions are based on wrong information

**Standards**: Same accuracy/completeness thresholds as operational data; aggregation should not mask quality issues.

**Audit**: Quarterly reconciliation of key metrics (total customers, revenue, etc.) between operational DB and analytics data warehouse.

## 7. Data Quality Plan for Known Issues

Northwind acknowledges some historical data quality issues:

| Issue | Scope | Remediation | Timeline |
|---|---|---|---|
| **Missing phone numbers** | 30% of customer records | Manual outreach or optional field | Q2 2026 |
| **Duplicate customer accounts** | 2% of base | Automated matching + manual review | Q3 2026 |
| **Outdated company names** | 5% of records | Annual refresh from business database | Ongoing |

## 8. Data Quality and Incident Response

If a **data quality incident** is discovered (massive inaccuracy, data corruption, unauthorized modification):
- Report to Chief Data Officer immediately (within 1 hour)
- Assess impact (how many records? which data subjects affected?)
- Preserve evidence (do not attempt to fix without investigation)
- Follow **Incident Response Runbook** if it's a Sev-2+ incident (e.g., "50,000 customer records corrupted")
- Notify affected data subjects if they have a right to know (e.g., incorrect salary calculation)

---

**Document owner:** Chief Data Officer  
**Last approved:** 2026-04-19 by Data Leadership  
**Next review:** 2027-04-19
