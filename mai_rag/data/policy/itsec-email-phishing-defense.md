---
title: Email & Phishing Defense
doc_id: itsec-email-phishing-defense
owner: IT Security Team
last_updated: 2026-03-20
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Email & Phishing Defense

## 1. Purpose and Scope

This policy defines Northwind's email security controls and employee responsibilities to prevent phishing, malware, and email-based data exfiltration.

## 2. Email Gateway and Filtering

### 2.1 Email Provider and Filters

- **Email Provider**: Microsoft Exchange Online (Office 365)
- **Advanced Threat Protection (ATP)**: Enabled for all inbound email
- **Spam Filter**: Machine learning–based, configured to block 99% of known spam and phishing

### 2.2 Automated Defenses

**Inbound Filtering:**
- Sender Policy Framework (SPF) verification (reject if fail)
- DomainKeys Identified Mail (DKIM) validation (warn if fail)
- Domain-based Message Authentication, Reporting and Conformance (DMARC) policy enforcement
- URL rewriting: All URLs in email are rewritten and scanned before rendering
- Attachment scanning: All executables, macros, and compressed files analyzed via sandboxing

**Outbound Filtering:**
- Data Loss Prevention (DLP) rules block emails containing:
  - Credit card numbers (PAN, American Express, etc.)
  - Social Security numbers (SSN)
  - API keys and authentication tokens
  - Customer PII when addressed to external domains
- Database credentials and connection strings auto-blocked
- Any Confidential or Restricted data sent to external email domain requires VP Security approval

### 2.3 Email Authentication Records

| Protocol | Record | Status |
|---|---|---|
| SPF | v=spf1 include:outlook.com ~all | Active, no third-party senders |
| DKIM | selector1._domainkey | Active, rotated quarterly |
| DMARC | p=quarantine | Active, reports to security@northwind.com |

## 3. Employee Email Usage Standards

### 3.1 Acceptable Email Use

- Corporate email for business purposes only (see **Acceptable Use Policy**)
- Employees may use email for brief personal messages (e.g., scheduling personal appointments)
- Personal email accounts must not be used to send or receive corporate data

### 3.2 Suspicious Email Reporting

If you receive a suspicious email (phishing attempt, malware, impersonation):
1. **Do NOT click links or download attachments**
2. **Do NOT reply or forward** (may confirm email is active)
3. Click **Report as Phishing** button in Outlook (top of message)
4. Email is submitted to Security team for analysis
5. If flagged as phishing, IT will add sender to blocklist within 1 hour

### 3.3 Email Retention and Archival

- Active emails retained in user mailbox: 90 days
- Mailbox archive retention: 7 years (for compliance and eDiscovery)
- Deleted items permanently purged after 30 days
- See **Data Classification & Retention Policy** for specific data retention rules

## 4. Phishing Simulation and Training

### 4.1 Quarterly Phishing Simulations

- All employees receive simulated phishing emails quarterly
- Simulations mimic real-world attacks (CEO impersonation, urgent requests, COVID-19 themes, etc.)
- Clicking links or downloading attachments counts as "failed" the test
- Reports sent to HR and department heads; targets >85% pass rate

### 4.2 Remedial Training

Employees who fail phishing simulations are required to:
1. Complete 15-minute anti-phishing training (same day)
2. Pass knowledge assessment (≥80%)
3. If second failure within 12 months: escalated to HR for performance discussion

### 4.3 Annual Security Awareness

All employees must complete **Security Awareness Training** annually, which includes email security and phishing awareness modules. See **Security Awareness Program** for details.

## 5. Phishing and Email Fraud Response

### 5.1 Detection and Containment

If phishing emails are detected in the wild:
1. **Immediate**: Email gateway auto-blocks sender domain
2. **Within 30 minutes**: Incident commander notified if >10 employees targeted
3. **Within 2 hours**: Email recalled (if Office 365 recall feature available)
4. **Within 24 hours**: Root cause analysis; malicious domain reported to threat intelligence partners

### 5.2 Domain Spoofing Prevention

- Email impersonating CEO, CFO, or VP Security triggers automatic hold for manual review
- Domains registered similar to Northwind (northwindtechonlogies.com, northwind-tech.com) are purchased and configured to reject all mail
- Brand monitoring service alerts security team of registered lookalike domains weekly

### 5.3 Account Compromise Response

If an employee's email account is compromised (attacker sends email as that user):
1. **Immediate**: Reset password; revoke all OAuth tokens
2. **Within 1 hour**: Review sent folder for exfiltrated data; review forwarding rules
3. **Within 2 hours**: Notify all recipients of emails sent during compromise window
4. **Within 4 hours**: Restore account from last known good backup if data loss suspected
5. Escalate as **Sev-2** incident per **Incident Response Runbook**

## 6. Third-Party Email and External Sharing

### 6.1 External Recipient Warnings

When sending email to external domains:
- First external recipient per day triggers warning dialog: "Are you sure you want to send this email outside Northwind?"
- Users must explicitly confirm

### 6.2 Confidential Data in Email

Confidential or Restricted data must NOT be sent via email unless:
1. Recipient is approved by data owner
2. Email is encrypted (Office 365 Message Encryption)
3. Recipient requires multi-factor authentication to access encrypted message
4. Message expires within 30 days

## 7. Mobile and Client Configuration

### 7.1 Outlook Configuration

- Outlook on Windows and macOS must have ATP enabled
- Mobile Outlook (iOS, Android) synced via Exchange Online; same filtering applies
- Cached credentials on mobile devices automatically cleared if device is not accessed for 90 days (remote wipe)

### 7.2 Third-Party Email Clients

- Gmail, Apple Mail, and other third-party clients accessing Northwind email must use app-specific passwords
- Standard Okta SSO passwords do NOT work with third-party clients
- App-specific passwords are rate-limited and logged

## 8. Email Logging and Forensics

- All email subject lines and metadata (sender, recipient, timestamp, size) logged to Splunk (see **Security Logging & SIEM**)
- Email bodies not logged for privacy
- 1-year retention for security investigation; 7-year archive for compliance
- If email is suspected to contain malware, IT can quarantine and analyze via sandbox

## 9. Enforcement and Violations

- First violation (e.g., sending Confidential data without encryption): Written warning + retraining
- Second violation: Email access suspended for 7 days
- Repeated violations: Escalation per **Information Security Policy** enforcement section

## 10. Related Policies

- **Information Security Policy**: Email classification standards and access controls
- **Data Classification & Retention Policy**: What data can be emailed and for how long
- **Acceptable Use Policy**: Prohibited email uses (harassment, spam, external solicitation)
- **Security Awareness Program**: Annual training covering phishing and email best practices

---

**Document owner:** Chief Information Security Officer  
**Last approved:** 2026-03-20 by Security Steering Committee  
**Next review:** 2027-03-20
