---
title: Endpoint Security Standard
doc_id: itsec-endpoint-security-standard
owner: IT Security Team
last_updated: 2026-04-10
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Endpoint Security Standard

## 1. Purpose and Scope

This standard defines minimum security requirements for all endpoints (laptops, desktops, workstations) at Northwind Technologies. This applies to company-issued devices and personal devices used for work.

## 2. Device Enrollment and Inventory

### 2.1 Mandatory Enrollment

All endpoints must be enrolled in Mobile Device Management (MDM) prior to network access. Enrollment includes:
- Inventory tracking (asset tag, serial number, owner, location)
- Configuration compliance verification
- Automatic remediation of non-compliant settings
- Remote wipe capability for lost or stolen devices

Users unable to enroll may request exemption from the IT Security team with business justification and written approval from their VP.

### 2.2 Device Classification

| Device Type | Ownership | MDM Required | Encryption Required | VPN Required |
|---|---|---|---|---|
| Company laptop | Northwind | Yes | Yes (BitLocker/FileVault) | Yes, when remote |
| Company desktop | Northwind | Yes | Yes (OS-level) | N/A (office-only) |
| Personal computer (work) | Employee | Yes | Yes | Yes, always |
| Mobile device (work use) | Varies | Yes | Yes | Yes, unless on corporate WiFi |

## 3. Operating System Hardening

### 3.1 Patch Management

- Windows and macOS security patches must be installed within **14 days** of vendor release
- Critical updates (severity 9.0+) must be installed within **7 days**
- Exceptions require written approval from IT Security
- See **Patch Management Policy** for detailed procedures

### 3.2 Password and Authentication

- Local administrator passwords must be unique per device
- All user passwords must meet NIST standards (minimum 12 characters, no forced rotation)
- See **Identity & Access Management Policy** for company-wide password requirements
- Biometric authentication (fingerprint, Windows Hello) is encouraged on endpoints where available

### 3.3 Firewall Configuration

- Host-based firewall (Windows Defender Firewall, macOS pf) must be enabled
- Inbound connections are blocked by default; outbound allowed
- Firewall logs are forwarded to the Security Logging system (see **Security Logging & SIEM** policy)
- Users cannot disable the firewall

## 4. Malware Protection

### 4.1 Antivirus Engine

All endpoints must run an approved antivirus engine with:
- Real-time file monitoring enabled
- Daily signature updates (automatic)
- Quarantine of detected threats without user intervention
- Approved vendors: Windows Defender (built-in for Windows), CrowdStrike Falcon, or Rapid7

### 4.2 Detection and Response

If malware is detected:
1. Antivirus engine quarantines the file
2. User receives notification in the MDM portal
3. IT Security team is alerted automatically
4. For high-severity detections, the device may be remotely isolated from the network pending review
5. User must remediate within 24 hours or device access is revoked

## 5. Data Loss Prevention (DLP)

### 5.1 Endpoint DLP Agent

All company-issued endpoints run an endpoint DLP agent that:
- Monitors file transfers (USB, email, cloud uploads)
- Prevents exfiltration of Confidential and Restricted data
- Logs all DLP events for audit
- Cannot be disabled by users

### 5.2 USB Device Management

- USB storage devices are disabled by default
- Employees may request USB access from IT Security with business justification
- When enabled, USB writes are logged and monitored

## 6. Encryption Standards

### 6.1 Full Disk Encryption

- **Windows**: BitLocker must be enabled; recovery key backed up to Azure
- **macOS**: FileVault must be enabled; recovery key stored in Okta vault
- **Linux**: LUKS encryption required for /home partition
- Encryption keys are NOT stored locally

### 6.2 File-Level Encryption

For non-encrypted devices (rare exceptions), sensitive files must use file-level encryption:
- Confidential and Restricted files encrypted with AES-256 using 7-Zip or similar
- Encryption password managed via password manager

## 7. Browser Security

### 7.1 Approved Browsers

- Chrome (with security extensions) – recommended
- Safari – acceptable for macOS
- Edge – acceptable for Windows
- Firefox – acceptable

Internet Explorer is prohibited.

### 7.2 Browser Configuration

- Automatic updates enabled
- Pop-up blocker enabled
- JavaScript restricted on untrusted sites
- Extensions limited to approved list (managed via MDM)
- Cookies cleared daily on shutdown

## 8. Incident Response for Compromised Endpoints

If an endpoint is suspected compromised:
1. Isolate from network immediately (disconnect WiFi, unplug ethernet)
2. Notify IT Security at security@northwind.com
3. Do NOT power off the device
4. Preserve logs for forensic analysis
5. Follow escalation in **Incident Response Runbook**

For Sev-1 compromises (confirmed malware on customer-facing system), notify VP Security within 30 minutes.

## 9. Enforcement and Non-Compliance

- Devices non-compliant for >7 days are blocked from VPN and internal network
- Users have 3 business days to remediate before IT takes enforcement action
- Repeated non-compliance may result in device revocation or disciplinary action

---

**Document owner:** Chief Information Security Officer  
**Last approved:** 2026-04-10 by Security Steering Committee  
**Next review:** 2027-04-10
