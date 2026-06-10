---
title: Incident Response Runbook
doc_id: incident-response-runbook
owner: Security Team
last_updated: 2026-03-14
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Incident Response Runbook

## 1. Overview

This runbook defines how Northwind responds to security and operational incidents. All employees must report suspected incidents immediately to the Security Team at security@northwind.com or call the 24/7 incident hotline at +1-844-NORTHWIND-SEC.

## 2. Incident Severity Levels

All incidents are classified into one of four severity tiers, each with defined response times:

| Severity | Description | RTO | RPO | Notification Timeline | Examples |
|----------|-------------|-----|-----|----------------------|----------|
| **Sev-1 (Critical)** | Active data breach, ransomware, complete service outage affecting customers | 4 hours | 1 hour | Immediate (within 30 min) to exec team + board + legal + PR; customer notification within 24 hours if PII exposed | Ransomware on production servers, 10K+ customer records exposed, all APIs offline |
| **Sev-2 (High)** | Significant service degradation, suspected compromise, data exfiltration (small scope) | 8 hours | 4 hours | Within 2 hours to exec team + customers affected; PR review before disclosure | One customer's data accessed by unauthorized account, 50% API latency for 2+ hours, malware detected on employee laptop |
| **Sev-3 (Medium)** | Isolated security finding, minor data loss, localized system failure | 24 hours | 8 hours | Within 8 hours to relevant teams (engineering, security); customer notification only if contractually required | Weak password used by one developer, database backup failed, single-user account compromise |
| **Sev-4 (Low)** | Informational security event, vulnerability with no exploitation path, process deviation | No SLA | 24 hours | Logged and reviewed in weekly security meetings | Failed login attempts from non-existent account, outdated SSL cert (not yet expired), misconfigured S3 bucket discovered (no data accessible) |

## 3. Detection and Initial Reporting

### 3.1 How Incidents Are Detected
- **Automated**: SIEM alerts (Splunk), antivirus/EDR alerts, cloud security posture (Azure Security Center)
- **Manual**: Employee reports, customer reports, suspicious activity noticed during code review
- **Third-party**: Vendor vulnerability disclosures, bug bounty reports

### 3.2 Reporting Obligations

**Any employee who discovers or suspects an incident must immediately:**
1. **Stop investigating** – avoid contaminating evidence
2. **Notify Security Team** – email security@northwind.com or call +1-844-NORTHWIND-SEC
3. **Preserve evidence** – do not delete logs, shut down systems, or run recovery tools without security approval
4. **Maintain confidentiality** – do not discuss incident details with colleagues outside immediate team

## 4. Incident Response Process

### 4.1 Detection Phase (0–30 minutes)
- Receive report or alert
- Assign **Incident Commander** (senior security engineer)
- Convene rapid response team (security, IT, engineering, legal as needed)
- Conduct initial assessment; assign Sev-1 to Sev-4

### 4.2 Containment Phase (30 minutes – 4 hours for Sev-1)

**Immediate actions:**
- Isolate affected systems if necessary (revoke access, disconnect from network)
- Preserve logs and evidence (snapshot memory, retain last 30 days of logs)
- Notify affected teams and stakeholders per severity
- Activate runbooks for specific incident types (ransomware response, data breach, etc.)

**For data breaches specifically:**
- Identify scope: which data types, how many records, which customers
- Check data classification (see **Data Classification & Retention Policy**) to determine notification obligations
- Contact Compliance and Legal immediately

### 4.3 Eradication Phase (4 hours – 7 days)

- Root cause analysis: how did this happen?
- Remove malware, patch vulnerabilities, rotate compromised credentials
- Rebuild affected systems from clean backups (see **Production Deployment Runbook**)
- Verify all entry points are closed (e.g., if attacker had SSH key, rotate all SSH keys)

### 4.4 Recovery Phase (parallel with eradication)

- Restore systems and data per Recovery Time Objective (RTO)
- Validate data integrity against backups (Recovery Point Objective – RPO)
- Monitor for re-compromise or recurrence

### 4.5 Post-Incident (24 hours – 30 days)

- Conduct **post-mortem**: document findings, timeline, and lessons learned
- Share post-mortem with leadership and affected teams (within 5 business days)
- Implement preventive improvements identified in post-mortem
- Customer communication (for Sev-1/Sev-2 data breaches): provide free credit monitoring if PII exposed

## 5. Specific Incident Types

### 5.1 Data Breach or Suspected Data Exfiltration

1. Identify which records are at risk (see **Data Classification & Retention Policy**)
2. Notify Legal and Compliance immediately (no delay beyond 30 minutes)
3. Check for GDPR applicability (any EU resident data?) – if yes, escalate to GDPR breach protocol
4. Determine notification timeline:
   - **Confidential data**: Customer notification recommended within 24–48 hours
   - **PII or health data**: Mandatory notification per GDPR (to individuals within 30 days), CCPA (to residents within 45 days)
5. Coordinate with PR and marketing on customer-facing disclosure

### 5.2 Ransomware or Malware

1. **Do not pay ransom** – consult legal and law enforcement
2. Isolate all infected systems from network
3. Engage cybersecurity forensics firm (approved vendors list in Incident Response team's private wiki)
4. Restore from clean backups; do not attempt to decrypt ransom notes
5. Coordinate with law enforcement (FBI cyber division, local police)

### 5.3 Compromised Credentials

1. Revoke compromised account in Okta immediately
2. Force password reset on next login
3. Audit account activity for last 30 days; check for data access, API calls, privilege escalation
4. If Restricted data was accessed: escalate to Sev-2 minimum
5. Enable enhanced logging for that account for 90 days

### 5.4 DDoS or Availability Attack

1. Notify cloud provider (Azure, AWS) to activate DDoS mitigation
2. Route traffic through Cloudflare DDoS protection if not already enabled
3. Contact ISP if attacks persist
4. Log all attack details; preserve logs for 90 days post-attack
5. If customer-facing service is down >30 minutes: escalate to Sev-2

## 6. Communication and Escalation

### 6.1 Notification Matrix

| Severity | Time to Notify | Recipients |
|----------|---|---|
| Sev-1 | Within 30 minutes | CEO, VP Security, VP Engineering, General Counsel, Chief Privacy Officer, Board Chair |
| Sev-2 | Within 2 hours | VP Security, VP Engineering, relevant department head, General Counsel |
| Sev-3 | Within 8 hours | VP Security, relevant team leads, Compliance |
| Sev-4 | By next business day | VP Security; documented in incident log |

### 6.2 Customer Notification (Data Breach Protocol)

- **Sev-1 data breach**: Customers notified within 24 hours
- **Sev-2 data breach**: Customers notified within 48 hours
- **Sev-3 data breach**: Customers notified per contract (typically 5 business days)
- All notifications must be reviewed and approved by Legal before sending

## 7. Compliance and Auditing

- All incidents are logged in the Incident Tracking System (Jira, restricted access)
- Post-mortems are retained for 3 years
- Quarterly incident review with board audit committee
- Annual external incident response tabletop exercise

## 8. Training and Preparation

- Security team: Incident response training annually + monthly drill
- All employees: Incident reporting training during onboarding + annual refresher
- Engineering team: Disaster recovery drills (quarterly)

---

**Document owner:** VP Security  
**Last approved:** 2026-03-14 by Security Leadership  
**Next review:** 2027-03-14

---

**Related policies:**
- See **Data Classification & Retention Policy** for data breach notification requirements
- See **Information Security Policy** for general security standards
- See **Remote Access / VPN Guide** for compromised access escalation
