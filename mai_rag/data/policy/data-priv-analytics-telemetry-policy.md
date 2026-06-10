---
title: Analytics & Telemetry Policy
doc_id: data-priv-analytics-telemetry-policy
owner: Chief Privacy Officer
last_updated: 2026-04-17
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Analytics & Telemetry Policy

## 1. Overview

Northwind Technologies collects **analytics and telemetry data** to:
- Measure product usage and feature adoption
- Identify performance bottlenecks (latency, errors)
- Understand user behavior and pain points
- Improve product design and customer experience

This policy establishes privacy guardrails for all analytics and telemetry collection to ensure GDPR compliance, transparency, and data minimization.

**Scope**: This applies to:
- In-app analytics (feature usage, event tracking)
- Performance monitoring (error rates, latency, CPU usage)
- User behavior tracking (session duration, click heatmaps)
- Log aggregation and analysis
- Third-party analytics tools (Google Analytics, Datadog, Hotjar)

## 2. Categories of Analytics Data

### 2.1 Usage Analytics (Aggregated)

**What**: Feature usage patterns, event counts, user sessions.
**Data collected**: User ID (hashed or anonymized), feature name, timestamp, event type.
**Retention**: 26 months (per Google Analytics retention standard).
**Personal data?** No (if properly anonymized) or maybe (if hashed user ID can be reversed).

**Legal basis**: GDPR Article 6(1)(a) — Consent (analytics requires opt-in in some jurisdictions).

**Examples**:
- "User_12345 clicked the 'Export' button on 2026-04-19 at 14:32 UTC"
- "50% of users access the reporting feature daily"
- "Average session duration: 18 minutes"

### 2.2 Performance Monitoring (Real-time)

**What**: Error rates, latency, resource usage, infrastructure health.
**Data collected**: Request ID, endpoint, response time, error status, IP address (masked), user agent.
**Retention**: 90 days (live); 2 years (archived for root cause analysis if incident occurred).
**Personal data?** Maybe (IP address may identify individual in small networks).

**Legal basis**: GDPR Article 6(1)(b) — Necessary to provide the service (performance monitoring is essential).

**Examples**:
- API error rate: 0.5% (200 errors of 40K requests)
- Database query latency: 95th percentile = 250ms
- Customer support portal down for 2 hours (Sev-2 incident)

### 2.3 Behavioral Analytics (Session-based)

**What**: User session recordings, click heatmaps, form abandonment, navigation flows.
**Data collected**: Session ID, user ID (hashed), interactions (clicks, scrolls, form entries), browser/device info.
**Retention**: 12 months.
**Personal data?** Maybe (session recordings may include form data, email addresses, sensitive fields).

**Legal basis**: GDPR Article 6(1)(a) — Explicit Consent (behavioral recording requires opt-in).

**Caveat**: **Form data redaction** is mandatory — email addresses, passwords, credit card numbers, SSNs must be masked before recording.

**Examples**:
- Session video: User scrolls dashboard, clicks "Reports" button, fills "date range" form (form inputs redacted)
- Heatmap: Most users click CTA button (85% click rate) vs. secondary button (10% click rate)
- Funnel: 1K users start onboarding; 800 reach step 2; 500 complete step 3 (30% abandonment)

## 3. Data Collection Standards

### 3.1 Minimization and Necessity

Analytics should collect **only the minimum data** necessary to answer business questions:

| Question | Data Needed | Data NOT Needed |
|----------|-------------|-----------------|
| "Which features do users adopt?" | Feature name, user_id (hashed), timestamp | User's email, department, salary |
| "Where do users abandon onboarding?" | Step number, event timestamp | User's name, company, contact info |
| "Which regions have highest latency?" | Country (inferred from IP), latency | User's exact IP, address, device ID |

**Rule**: Before adding a new event or attribute to analytics, the data owner must document:
- What business question does this answer?
- Is this the minimum data necessary?
- Is personal data being collected? (If yes, what's the legal basis?)
- How long will it be retained?

### 3.2 Consent and Transparency

**Analytics cookie tracking**: See **Cookie & Tracking Policy** for cookie consent and opt-out mechanisms.

**In-app analytics**: Northwind collects in-app usage analytics for **all users** (no opt-out option) as necessary for service improvement. Users are informed in the Privacy Policy that usage is tracked.

**Behavioral recording** (Hotjar, session replays): Requires explicit opt-in. Users see a banner: "We use session recordings to improve UX. [Accept] [Decline]"

### 3.3 Sensitive Data and Analytics

**Never include in analytics**:
- Passwords, API keys, authentication tokens
- Credit card numbers (PCI-DSS scope)
- Government ID numbers (SSN, passport)
- Health/medical information
- Biometric data
- Email addresses or phone numbers (unless specifically needed and hashed)

**If sensitive data appears in logs** (e.g., a user accidentally submitted their SSN in a form field):
1. Redact from all analytics and logs (see **Anonymization & Pseudonymization Standard**)
2. Notify the user
3. Investigate how the sensitive data entered the system

## 4. Analytics Tools and Vendor Management

### 4.1 First-Party Analytics (Northwind-owned)

**Tools**: Custom event tracking in Northwind Cloud (PostgreSQL, Datadog, custom dashboards).

**Data flow**:
1. In-app event is triggered (user clicks button, loads page, completes action)
2. Event is logged to Northwind's backend (event name, user_id, timestamp)
3. Events are aggregated in data warehouse (daily/hourly batches)
4. Dashboards and reports query aggregated data

**Retention**: Events retained for 90 days; aggregates retained indefinitely (no personal data).

**Access**: Product, engineering, and data teams (access controlled via Okta RBAC).

### 4.2 Third-Party Analytics Tools

See **Cookie & Tracking Policy** for detailed management of third-party vendors.

| Tool | Purpose | Data Shared | Consent | DPA | SCC |
|---|---|---|---|---|---|
| **Google Analytics** | Usage analytics, user funnels | Anonymous user ID, events, device | Opt-in | ✅ | ✅ (SCC) |
| **Datadog** | Performance monitoring, error tracking | Request details, latency, errors | Implied (necessary) | ✅ | ✅ (SCC) |
| **Hotjar** | Behavioral recording, heatmaps | Session video (redacted), interactions | Explicit opt-in | ✅ | ✅ (SCC) |

### 4.3 Vendor Data Processing Agreements

All third-party analytics vendors must have a **Data Processing Agreement (DPA)** in place (see **Data Processing Agreement (DPA) Standard**).

**Key requirements**:
- Vendor must encrypt data in transit (TLS 1.3)
- Vendor must comply with data retention (auto-delete after period)
- Vendor must not use data for own purposes (e.g., marketing)
- Vendor must notify Northwind of data breaches within 48 hours
- Northwind has the right to audit vendor compliance (SOC 2 required)

## 5. Data Subject Rights and Analytics

### 5.1 Right of Access and Analytics Data

Data subjects may request a copy of analytics data collected about them:

**Process**:
1. Data subject submits request via privacy@northwind.com
2. Privacy Team identifies analytics records for the user (user_id, user_email, hashed_user_id)
3. Analytics team exports events associated with the user ID
4. Data is compiled in CSV format and delivered to data subject
5. **Retention exception**: While GDPR access request is pending, analytics data for that user is retained (not auto-purged)

**Example deliverable**: CSV with columns {timestamp, event_name, event_data, user_agent}; redacted of other users' data

### 5.2 Right of Erasure and Analytics Data

Data subjects may request deletion of analytics data:

**Policy**:
- **Hashed user IDs**: Are irreversibly anonymized (cannot be reversed). If properly anonymized, they are not "personal data" and do not need to be deleted. However, if user_id is reversible (e.g., user_001 can be linked back via a mapping), it must be deleted per request.
- **Raw events**: If events contain personal data (email, address), they are deleted within 30 days.
- **Aggregates**: Already anonymized; cannot be reverted to personal data; no deletion needed.

**Consequence of deletion**: Historical analytics for that user become unavailable; may slightly impact trend analysis if user was a major power user.

### 5.3 Right to Object and Analytics

Data subjects may object to analytics collection:

**If user opts out of analytics**:
- All future events are not collected
- Existing analytics data is retained per retention schedule (but user can request deletion via GDPR right of erasure)
- User remains fully functional in the platform (analytics is not required for core features)

**How to opt-out**: Settings → Privacy → Disable Usage Analytics (checkbox)

## 6. Analytics Data Governance and Security

### 6.1 Access Controls

Analytics data is classified per **Data Classification & Retention Policy**:

- **Raw event logs** (contains hashed user IDs): Internal / Confidential
- **Aggregated analytics** (no user IDs): Internal / Public
- **Performance logs** (may contain IP addresses): Internal / Confidential

**Access**:
- Product team: Full access to dashboards
- Engineering team: Full access to performance logs
- Data science team: Full access to aggregates and anonymized data
- Finance: Limited access (only aggregate metrics)
- Executives: Dashboards only (no raw data)

**Enforcement**: Okta RBAC + database row-level security (RLS).

### 6.2 Data Retention

| Data Type | Retention | Reason |
|---|---|---|
| **Raw event logs** | 90 days | Cost; privacy minimization |
| **Performance logs** | 90 days (live); 2 years (archive) | Root cause analysis; incident investigation |
| **Aggregated analytics** | Indefinite (no personal data) | Historical trend analysis |
| **Session recordings** (Hotjar) | 13 months | GDPR compliance; cost |
| **Google Analytics** | 26 months | GA default; GDPR compliance |
| **Datadog monitoring** | Per SLA (typically 30–90 days) | Real-time monitoring; cost |

Retention is enforced via automated deletion policies in cloud storage and log aggregation tools.

### 6.3 Incident Response

If an analytics data breach is discovered (e.g., raw event logs exposed with user IDs):

1. **Classification**: Determine if personal data was exposed (hashed IDs alone are low risk; email addresses are high risk)
2. **Scope**: How many users affected? Which data types exposed?
3. **Notification**: Per **Incident Response Runbook** severity:
   - Sev-2 (email addresses exposed): Notify users within 48 hours
   - Sev-1 (large-scale PII exposure): Notify within 24 hours; notify regulators within 72 hours
4. **Root cause**: How did data get exposed? (access control failure? vendor breach? misconfigured permissions?)
5. **Remediation**: Fix the vulnerability; review retention policies; strengthen encryption

## 7. Analytics and Machine Learning

Analytics data is often used to train ML models (e.g., predict churn, recommend features):

**Privacy controls**:
- Raw user data is anonymized or pseudonymized before training (see **Anonymization & Pseudonymization Standard**)
- Model does not retain user IDs or identifiable information
- Model audit is conducted before deployment (check for bias, discriminatory outcomes)
- Users have right to object to automated decision-making (see **GDPR Compliance Policy**)

**Example**: ML model trained on {num_logins_per_month, features_used, account_age, churn_probability}; no user IDs, emails, or company names.

## 8. Transparency and Privacy Policy

Northwind's Privacy Policy (northwindcloud.com/privacy) discloses:

> "We collect analytics to understand how you use Northwind Cloud, improve features, and identify performance issues. Analytics include your usage events (feature clicks, page views), session information, and device details. Analytics data is retained for 26 months and may be shared with vendors (Google Analytics, Datadog) who are bound by data processing agreements. You can disable analytics in Settings → Privacy. If you are in the EU, you can opt-in to behavioral recording (Hotjar); it is disabled by default. We also use cookies to track analytics; see our Cookie Policy for details."

---

**Document owner:** Chief Privacy Officer  
**Last approved:** 2026-04-17 by Privacy Leadership  
**Next review:** 2027-04-17
