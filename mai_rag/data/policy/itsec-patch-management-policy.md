---
title: Patch Management Policy
doc_id: itsec-patch-management-policy
owner: IT Operations
last_updated: 2026-04-10
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Patch Management Policy

## 1. Purpose and Scope

This policy establishes procedures for deploying security patches and operating system updates across all infrastructure and endpoints at Northwind.

## 2. Patch Classification and SLA

### 2.1 Severity Levels

Patches are classified based on vulnerability CVSS score:

| Patch Type | CVSS Score | Endpoint SLA | Server SLA | Example |
|---|---|---|---|---|
| **Critical** | 9.0–10.0 | 7 days | 24 hours | Remote code execution, critical auth bypass |
| **High** | 7.0–8.9 | 14 days | 7 days | Privilege escalation, information disclosure |
| **Medium** | 4.0–6.9 | 30 days | 30 days | DoS, weak encryption |
| **Low** | 0.1–3.9 | 90 days | 90 days | Minor bug fixes, cosmetic issues |

### 2.2 Patch Categories

- **Operating System patches** (Windows, macOS, Linux kernel)
- **Application patches** (libraries, frameworks, dependencies)
- **Firmware updates** (BIOS, network drivers, storage controller)
- **Database patches** (PostgreSQL, MongoDB, Redis versions)
- **Antivirus/Antimalware signature updates** (deployed daily)

## 3. Patch Sources and Notification

### 3.1 Vendor Notification Channels

| Vendor | Channel | Frequency |
|---|---|---|
| Microsoft | Windows Update / Microsoft Security Update Guide | 2nd Tuesday monthly |
| Apple | Apple Security Updates | Irregular; critical fixes within days |
| Linux (Ubuntu) | Ubuntu Security Notices (USN) | Continuous |
| AWS | AWS Security Bulletins | Continuous |
| Azure | Azure Security and Compliance Blog | Continuous |
| Third-party vendors | Vendor mailing lists / NVD (National Vulnerability Database) | Continuous |

### 3.2 Patch Intake Process

1. **Notification received** from vendor (email, RSS feed, or manual check)
2. **Vulnerability assessment**: CVE lookup; CVSS score determination
3. **Affected systems inventory**: Which servers/endpoints impacted?
4. **SLA calculation**: Due date assigned per patch classification
5. **Testing plan**: Dev/staging deployment; rollback plan prepared
6. **Change request**: Submitted to change management system; approval obtained

## 4. Endpoint Patch Deployment

### 4.1 Automatic Patch Management (Windows/macOS)

- **Windows Update**: Auto-enabled for all Windows endpoints; patches install on next reboot (scheduled via MDM)
- **macOS Software Update**: Auto-enabled; critical patches apply immediately, others at next restart
- **Linux**: Unattended-upgrades daemon auto-installs OS patches monthly (user notified of pending reboot)

### 4.2 Patch Deferral for Compatibility

Users may request patch deferral if update breaks critical business application:
1. Submit patch deferral request to IT Operations within 24 hours of patch release
2. Provide application name, business impact, and proposed remediation timeline
3. IT Security reviews; may approve deferral for up to 14 days (high-severity patches non-deferrable)
4. Application vendor engaged for compatibility fix or application update
5. Deferral expires after 14 days; endpoint must patch or lose network access

### 4.3 Patch Compliance Monitoring

- MDM checks daily for patch status of all endpoints
- Non-compliant endpoints (unpatched for >SLA days) receive escalating notifications:
  - Day 1: Email reminder from IT
  - Day 3: Warning of access restriction
  - Day 7: VPN/network access revoked; user required to remediate at office
- Compliance dashboard public to all team leads (peer pressure encourages compliance)

## 5. Server and Infrastructure Patching

### 5.1 Production Deployment Window

- **Standard window**: Patching occurs 2nd Tuesday monthly, 10 PM–2 AM PT (low-traffic period)
- **Critical patches**: May be deployed outside window with VP Engineering approval
- **Customer notification**: Customers notified 1 week prior of planned maintenance window; RTO 1 hour per system

### 5.2 Staging and Testing

All patches tested before production deployment:
1. **Stage 1 – Dev environment**: Patch applied to non-prod instances; smoke tests run
2. **Stage 2 – Staging environment**: Patch applied to production-identical staging; full regression testing performed; performance baseline verified
3. **Stage 3 – Production**: Approved patches deployed to prod during change window; monitored for errors for 24 hours

Rollback plan prepared for all patches; rollback executed if error rate increases >1% within 30 minutes of deployment.

### 5.3 Database Patching

- **PostgreSQL**: Minor patches (e.g., 13.2 → 13.3) auto-applied to test/staging; production updates scheduled per SLA
- **Major version upgrades** (e.g., 13 → 14): Require engineering review; full testing in staging; customer notification 2 weeks prior
- **Backup before patching**: Full backup taken 1 hour before database patching; restoration tested if patching fails
- **Zero-downtime patching**: Logical replication used to migrate data to patched instance; RTO <5 minutes

### 5.4 Firmware Updates

- **Server BIOS/Firmware**: Firmware updates deployed quarterly (non-critical); critical firmware updates deployed within 7 days
- **Network devices**: Firmware updates staggered across devices to avoid all equipment restarting simultaneously
- **Impact assessment**: Firmware update impact (restart required, service interruption) evaluated before deployment

## 6. Patch Rollback

### 6.1 Rollback Triggers

Automatic rollback if:
- Error rate increases >2% post-deployment
- System becomes unavailable within 5 minutes of patch
- Critical service fails health checks within 15 minutes

Manual rollback if:
- VP Engineering requests rollback
- Unexpected data corruption or corruption detected
- Customer-reported critical issue traced to new patch

### 6.2 Rollback Execution

1. **Notification**: VP Engineering, on-call engineer, and change manager notified
2. **Rollback command**: Executed within 5 minutes of trigger; system reverts to prior version
3. **Verification**: Health checks confirm rollback successful; error rate returns to baseline
4. **Investigation**: Root cause analysis; patch sent to vendor if issue is product bug
5. **Rescheduling**: Patch redeployed after fix confirmed (or deferred indefinitely if unfixable)

## 7. Antivirus and Threat Intelligence Updates

### 7.1 Daily Signature Updates

- All antivirus engines auto-update signatures daily (no user action required)
- Failed updates (e.g., network connectivity issue) flagged in MDM; IT reaches out to user
- Signature verification: All downloaded signatures cryptographically verified before installation

### 7.2 Threat Intelligence Feeds

- Firewall threat prevention feeds updated daily
- DNS blocklists updated hourly
- Malware sample repositories updated continuously (real-time threat detection)

## 8. Patch Metrics and Compliance Reporting

### 8.1 Key Metrics

- **Patch deployment time**: Target 50% of endpoints within 3 days of release
- **Compliance rate**: Target 95% of endpoints patched within SLA
- **Critical patch time to deployment**: Target 24 hours for servers, 7 days for endpoints
- **Rollback frequency**: <2% of deployments require rollback

### 8.2 Monthly Patch Report

Security and IT Operations publish monthly report:
- Patches deployed; CVEs addressed
- Compliance by team (endpoints patching on schedule vs. lagging)
- Rollback incidents; root causes
- Patch deferral requests; status
- Forward-looking: Major patches arriving next month; vendor notifications

## 9. Special Circumstances

### 9.1 Legacy System Patches

Systems nearing end-of-life may not receive patches:
- **Risk acceptance**: VP Security and system owner jointly approve acceptance
- **Compensating controls**: Increased monitoring, network isolation, access restrictions
- **Sunset date**: Documented in IT asset inventory; decommissioning planned

### 9.2 Third-Party Patch Dependencies

Some patches depend on other vendors' patches (e.g., OS patch depends on firmware update):
- Dependency identified in patch testing phase
- Dependent patches grouped; deployed together in single change window
- Vendor coordination required if patches from different vendors

## 10. Patch Management Tools

- **Windows**: Windows Update, WSUS (Windows Server Update Services)
- **macOS**: Apple Software Update, Jamf Pro MDM
- **Linux**: Unattended-upgrades, apt/yum
- **Antivirus signatures**: Automatic daily updates (no manual intervention)

## 11. Related Policies

- **Vulnerability Management**: Patch prioritization per vulnerability assessment
- **Change Management** (in **Firewall Change Management Policy**): Change request and approval procedures
- **Endpoint Security Standard**: Endpoint compliance and monitoring
- **Incident Response Runbook**: Escalation if patch causes critical issue

---

**Document owner:** VP IT Operations  
**Last approved:** 2026-04-10 by IT Leadership  
**Next review:** 2027-04-10
