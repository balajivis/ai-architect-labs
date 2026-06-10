---
title: Security Logging & SIEM
doc_id: itsec-security-logging-siem
owner: IT Security Team
last_updated: 2026-04-12
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Security Logging & SIEM

## 1. Purpose and Scope

This policy establishes logging and monitoring requirements for all IT systems at Northwind. Centralized logging enables incident detection, forensics, and compliance audits.

## 2. SIEM Architecture

### 2.1 Centralized Log Aggregation

**Primary SIEM**: Splunk Enterprise (self-hosted on Northwind infrastructure)
- Ingestion rate: 10GB/day (scalable to 50GB/day)
- Index retention: 1 year hot/warm storage; 7 years cold storage (S3 archive)
- Log parsing via 500+ custom regex rules; CIM-compliant data models

**Secondary SIEM** (Real-Time Alerts): Datadog
- Ingestion rate: Real-time streaming from VMs and Kubernetes
- Retention: 30 days; used for live incident response
- Alerts sent to PagerDuty for on-call escalation

### 2.2 Log Sources and Collection

| Source | Log Type | Collection Method | Retention |
|---|---|---|---|
| VPN gateway | Auth, connection metadata | Syslog to Splunk | 1 year |
| Firewalls (Palo Alto) | Blocked connections, threats | Syslog over TLS | 1 year |
| DNS server | Query logs, malicious domains | syslog-ng | 90 days |
| Web servers (Apache, nginx) | Access logs, error logs | Fluentd to Splunk | 6 months |
| SSH bastion servers | SSH login attempts, commands | auditd to Splunk | 1 year |
| Active Directory (Okta) | User login, group changes, account lockout | OIDC log export | 1 year |
| AWS CloudTrail | API calls, IAM actions, resource changes | S3 → Lambda → Splunk | 2 years |
| Azure Activity Log | Azure API calls, resource changes | Event Hub → Splunk | 2 years |
| GitHub Actions | Workflow runs, secrets access | GitHub API → Splunk | 1 year |
| Database audit logs | Logins, DDL/DML, superuser actions | Native DB logging to Splunk | 1 year |
| Endpoint logs (EDR) | Process execution, file changes, network connections | CrowdStrike to Splunk via API | 1 year |
| Application logs | Errors, warnings, access patterns | Syslog or stdout to Splunk | 6 months |

## 3. Logging Standards

### 3.1 Mandatory Log Fields

All logs must include (minimum):
- **Timestamp** (ISO 8601 format, UTC)
- **Source** (hostname, IP address, service name)
- **Event type** (authentication, file access, network connection, etc.)
- **User/Principal** (account name or service principal)
- **Action** (login, logout, access granted/denied, create, delete, modify)
- **Result** (success, failure, error code)
- **Resource** (file path, database name, API endpoint, etc.)

### 3.2 Sensitive Data Masking

Logs must NOT contain plaintext:
- Passwords or passphrases
- API keys or tokens
- Encryption keys
- PII (SSN, credit card numbers, home addresses)
- Customer data (classified as Confidential/Restricted)

**Masking approach**: Sensitive fields replaced with [REDACTED] before logging. If sensitive data appears, log source is escalated to VP Security.

### 3.3 Log Sampling

High-volume logs may be sampled to control ingestion costs:
- **Critical**: No sampling (e.g., authentication failures, malware alerts)
- **High**: 100% sampling (e.g., SSH login success, firewall allowed connections)
- **Medium**: 50% sampling (e.g., DNS queries to known-good domains)
- **Low**: 10% sampling (e.g., routine application debug logs)

Sampling ratios reviewed quarterly and adjusted based on incident history.

## 4. Detection and Alerting

### 4.1 SIEM Detections (High Priority)

| Alert | Trigger | Response |
|---|---|---|
| **Brute force login** | >10 failed logins in 10min from single source IP | Auto-block IP; alert SOC; review for credential compromise |
| **Privilege escalation** | Non-admin user runs sudo/administrative command | Alert SOC; require VP Security approval for escalation |
| **Data exfiltration attempt** | DLP blocks >10 Confidential files in 1 hour | Block user's network access; escalate to VP Security as Sev-2 |
| **Malware signature match** | Antivirus detects malware on endpoint | Auto-isolate endpoint; alert on-call engineer |
| **Suspicious API calls** | API key used from unusual country or VPN | Rate-limit API key; notify key owner; investigate for compromise |
| **Account lockout** | Okta account locked after 10 failed MFA attempts | Send SMS to user; require password reset before unlock |
| **Unauthorized SSH access** | SSH login to production server from non-approved bastion | Deny login; alert on-call DBA; review SSH key logs |

### 4.2 Alert Routing

| Severity | Recipient | Response SLA |
|---|---|---|
| **Critical** (Sev-1) | PagerDuty on-call (VP Security + lead engineer) | Acknowledge within 5 minutes |
| **High** (Sev-2) | PagerDuty + SOC team Slack | Within 15 minutes |
| **Medium** | SOC team email + Slack | Within 1 hour |
| **Low** | Weekly SOC report | Review within 5 business days |

### 4.3 Alert Tuning

- Alerts reviewed weekly by SOC team for false positive rate
- Target false positive rate: <5%
- If alert accuracy drops below 95%, alert is disabled pending rule refinement

## 5. Log Retention Policies

### 5.1 Retention by Log Type

| Log Type | Hot/Warm (Online) | Cold/Archive (S3) | Deletion |
|---|---|---|---|
| Authentication (VPN, SSH) | 1 year | 7 years | After 7 years |
| Firewall/Network | 1 year | 5 years | After 5 years |
| Application | 6 months | 2 years | After 2 years |
| Database audit | 1 year | 5 years | After 5 years |
| Endpoint (EDR) | 1 year | 3 years | After 3 years |
| Compliance-critical | 7 years | N/A | After 7 years + external hold |

### 5.2 Legal Hold and eDiscovery

- If litigation or regulatory investigation is pending, affected logs placed on "legal hold"
- Legal hold logs are NOT deleted; retained indefinitely or per court order
- General Counsel notifies IT Security when legal hold is released

## 6. Log Access and Privacy

### 6.1 Who Can Access Logs

| Role | Access Level | Logs Visible |
|---|---|---|
| SOC Analyst | Read | All non-employee-private logs |
| CISO / VP Security | Read/Modify alerts | All logs |
| On-call engineer (SRE) | Read | Application + infrastructure logs (not auth logs) |
| Database Administrator | Read | Database audit logs only |
| Compliance auditor | Read | Compliance-critical logs (during audit windows) |
| Employees (self-service) | Read | Own VPN/SSH login activity via portal |

### 6.2 Access Logging

All access to SIEM is logged:
- User, timestamp, query executed, number of rows returned
- Access logs retained for 2 years
- Unusual queries (e.g., exporting 1M rows, querying for PII patterns) trigger alert to CISO

## 7. Log Search and Incident Investigation

### 7.1 Common Investigative Queries

**SOC team has pre-built searches** for common incident investigations:
- All activity by user (logins, file access, API calls)
- All activity on a host (network connections, process execution, file changes)
- All activity involving a data classification (Confidential data flows)
- Data exfiltration timeline (what data left, where, when)

### 7.2 Forensic Investigation Process

During incident investigation:
1. **Preserve evidence**: Query logs; export to encrypted archive
2. **Timeline reconstruction**: Sort events chronologically; identify sequence of actions
3. **Attribution**: Link actions to user account or service principal
4. **Impact analysis**: Determine what data was accessed/modified
5. **Root cause**: Identify initial compromise vector

See **Incident Response Runbook** for detailed investigation procedures.

## 8. SIEM Maintenance and Resilience

### 8.1 Splunk High Availability

- Primary Splunk cluster (3 indexers) in us-west-2 (AWS)
- Replication factor 3; search factor 2 (ensures 1-indexer failure tolerance)
- Backup Splunk instance (read-only replica) in us-east-1; RTO 4 hours
- Weekly backup of Splunk configuration and user data

### 8.2 Log Parsing Validation

- New log sources tested in non-prod Splunk environment
- Log parsing rules validated against 1000 sample events before production deployment
- Quarterly audit of parsing rules; ~10 rules refined based on new attack patterns

## 9. Compliance and Auditing

This logging infrastructure supports:
- **SOC 2 Type II**: Audit trail for all administrative actions
- **GDPR**: Demonstrates access controls and data protection logging
- **PCI DSS 10.x**: Logging and monitoring of card data environments
- **HIPAA**: Audit logs for access to healthcare data (if applicable)

## 10. Related Policies

- **Information Security Policy**: Access control and classification standards
- **Incident Response Runbook**: Log-based investigation procedures
- **Data Classification & Retention Policy**: Log retention timelines
- **Endpoint Security Standard**: EDR logging requirements

---

**Document owner:** Chief Information Security Officer  
**Last approved:** 2026-04-12 by Security Steering Committee  
**Next review:** 2027-04-12
