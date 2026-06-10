---
title: Mobile Device Management (MDM)
doc_id: itsec-mobile-device-management
owner: IT Operations
last_updated: 2026-04-11
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Mobile Device Management (MDM)

## 1. Purpose and Scope

This policy establishes Mobile Device Management (MDM) requirements for all devices (laptops, desktops, tablets, smartphones) used to access Northwind's network or data.

## 2. Devices Covered

### 2.1 Enrollment Mandatory

The following devices MUST be enrolled in MDM before any corporate access:
- Company-issued laptops (Windows, macOS)
- Company-issued desktops (Windows, macOS)
- Company-issued tablets (iPad, Android)
- Personal devices used for work (BYOD)
- Mobile devices used for email or Slack access

### 2.2 Devices Exempt

Exemptions (no MDM required):
- Desktop terminals with no network connectivity
- Test/lab devices in isolated network (documented in IT inventory)
- Print servers, IoT devices (managed via separate IoT policy)

## 3. MDM Platform and Capabilities

### 3.1 Platform Selection

| Device Type | MDM Solution | Vendor |
|---|---|---|
| Windows | Intune (Microsoft) | Microsoft Endpoint Manager |
| macOS | Jamf Pro | Jamf |
| iOS/iPadOS | Apple Business Manager + Jamf | Jamf |
| Android | Google Workspace MDM | Google |
| Linux | Landscape (Canonical) | Canonical |

### 3.2 Core MDM Capabilities

All MDM solutions provide:
- **Device inventory**: Asset tracking, serial numbers, OS versions
- **Compliance monitoring**: Configuration verification (encryption, firewall, antivirus status)
- **Configuration management**: Deploy settings (WiFi profiles, VPN configs, security policies)
- **Application management**: Deploy corporate apps; prevent sideloading of unapproved apps
- **Remote actions**: Lock device, wipe data, force password reset
- **Logging**: Device actions, policy compliance, application installations

## 4. MDM Enrollment Process

### 4.1 Company-Issued Devices

1. Device shipped with MDM enrollment URL pre-loaded
2. Employee boots device; MDM enrollment wizard launches
3. Employee authenticates with Okta credentials
4. Device automatically configures:
   - VPN profile (OpenVPN for Linux/macOS; Cisco AnyConnect for Windows)
   - WiFi network settings
   - Email and calendar (Exchange Online)
   - Okta SSO for cloud apps
   - Security baselines (encryption, firewall, antivirus)
5. Device checked for compliance; if non-compliant, remediation applied automatically
6. Employee receives device ready for work; enrollment complete in <30 minutes

### 4.2 Personal Device Enrollment (BYOD)

1. Employee requests BYOD registration via HR portal
2. Employee downloads MDM agent for their device (Jamf or Intune)
3. MDM agent requests permissions to manage device
4. Device compliance verified (OS version, encryption, passcode)
5. If non-compliant, employee prompted to enable security settings
6. Once compliant, corporate apps and VPN access provisioned
7. Employee can unenroll device at any time; corporate apps removed

**Note**: Personal device enrollment grants IT access to device settings only, not personal data (e.g., photos, messages, private apps).

## 5. Compliance Policies

### 5.1 Baseline Security Requirements

All enrolled devices must maintain:

| Setting | Windows | macOS | iOS | Android |
|---|---|---|---|---|
| **Encryption** | BitLocker enabled | FileVault enabled | Enabled (default) | Enabled |
| **Passcode** | 12+ characters | 12+ characters | 6+ digits | 6+ characters |
| **Screen lock timeout** | 15 minutes | 15 minutes | 10 minutes | 10 minutes |
| **OS updates** | Within 14 days | Within 14 days | Within 7 days | Within 14 days |
| **Antivirus** | CrowdStrike or Windows Defender | CrowdStrike | N/A (native) | CrowdStrike |
| **VPN** | Mandatory when remote | Mandatory when remote | Via Okta Verify app | Via Okta Verify app |

### 5.2 Compliance Monitoring

- **Daily check-in**: Device reports compliance status every 24 hours
- **Policy enforcement**: Non-compliant devices blocked from corporate resources within 24 hours
- **Remediation**: Automated scripts attempt to fix non-compliance (e.g., update OS, enable encryption)
- **Escalation**: If device remains non-compliant >7 days, IT reaches out to user for manual remediation

## 6. Application Management

### 6.1 Approved Applications

| Category | Windows/macOS | iOS/Android |
|---|---|---|
| **Email** | Outlook (corporate) | Outlook mobile |
| **Collaboration** | Slack, Teams | Slack, Teams |
| **Productivity** | Office 365 | Office 365 mobile |
| **Dev tools** | VS Code, GitHub Desktop, Docker Desktop | N/A |
| **VPN** | OpenVPN, Cisco AnyConnect | Okta Verify (built-in MFA) |
| **Browser** | Chrome, Safari, Edge | Chrome, Safari |

### 6.2 Application Deployment

- **Computers**: Applications deployed via MDM; automatic updates enabled
- **Mobile devices**: Apps distributed via Apple App Store (iOS) and Google Play (Android); automatic updates allowed
- **Sideloading prevention**: On iOS, only App Store apps allowed; sideloading blocked via MDM policy
- **Android**: Only managed Google Play apps allowed; sideloading blocked

### 6.3 Blocked Applications

The following are prohibited and auto-removed if detected:
- Unauthorized password managers (1Password, LastPass not approved; use Azure Vault)
- File-sharing apps (Dropbox, OneDrive are approved; others like pCloud are not)
- VPN apps (except corporate VPN and Okta Verify)
- Unauthorized SSH clients or terminal emulators
- Gaming consoles or streaming applications

## 7. Mobile Device Security

### 7.1 Email Security on Mobile

- **Outlook Mobile**: All email cached locally; encryption via device encryption (BitLocker/FileVault)
- **Email policy**: Confidential and Restricted emails can only be opened if VPN is active
- **Attachment handling**: Executable files and scripts cannot be opened on mobile; users download to computer instead
- **Email retention**: Older emails (>90 days) not synced to mobile to prevent data accumulation

### 7.2 VPN Enforcement on Mobile

- Mobile access to internal systems (HR systems, Grafana, internal wikis) REQUIRES VPN
- VPN profile auto-deployed to all mobile devices; cannot be removed
- VPN kill switch enabled: If VPN drops, data connectivity is blocked
- All traffic routes through VPN (split tunneling disabled)

### 7.3 Remote Wipe Capability

If a device is lost or employee is terminated:
1. **Alert**: IT learns of device loss/termination
2. **Command issued**: Wipe command sent to device via MDM
3. **Action**: All corporate data and applications removed; device reset to factory state
4. **Confirmation**: Wipe status reported back to MDM; IT confirms success
5. **Timeline**: Wipe completed within 1 hour

Remote wipe does NOT remove personal data on BYOD devices (only corporate apps/data wiped).

## 8. Device Decommissioning

### 8.1 End-of-Life Devices

When a device is decommissioned:
1. **Backup**: All data backed up per **Data Classification & Retention Policy**
2. **Wipe**: Device wiped using certified wipe tool (NIST 800-88 compliant)
3. **Certificate of destruction**: Vendor provides proof of destruction for audit
4. **Inventory update**: Device marked as decommissioned in IT asset database

### 8.2 Employee Offboarding

When an employee is terminated:
1. **Device lock**: Device remotely locked within 1 hour of termination
2. **Access revocation**: All corporate credentials invalidated; remote VPN, email, cloud access revoked
3. **Selective wipe**: Confidential data on device securely deleted; personal data (if BYOD) preserved
4. **Device collection**: Laptop collected from employee; wiped and re-imaged for reuse or recycling

## 9. MDM Monitoring and Reporting

### 9.1 Compliance Dashboard

- **Public dashboard**: All employees see their own device compliance status
- **Manager dashboard**: Managers see team device compliance rates
- **IT dashboard**: IT Security team sees organization-wide compliance; top risks highlighted

### 9.2 Monthly MDM Report

IT Operations publishes monthly report:
- Total enrolled devices by type (Windows, macOS, iOS, Android)
- Compliance rates by policy (encryption, OS updates, antivirus)
- Top non-compliance issues (e.g., 200 devices out of compliance with OS patch SLA)
- Wipe operations performed (lost devices, terminations)
- Malware detections via antivirus integration

## 10. Bring Your Own Device (BYOD) Policy

### 10.1 BYOD Eligibility

Employees may use personal devices to access:
- Email and calendar (Outlook)
- Collaboration tools (Slack, Teams)
- Cloud applications (via Okta SSO)

BYOD NOT permitted for:
- Development or coding work (no laptop required for non-engineers)
- Access to production databases or internal tools
- Storage of Confidential or Restricted data

### 10.2 BYOD Agreement

Before enrollment, employees sign BYOD agreement acknowledging:
- IT can remotely manage device settings (MDM compliance monitoring)
- If device lost/stolen, corporate data is remotely wiped
- Employee responsible for maintaining device security (backup, password recovery)
- Enrollment can be revoked if policies violated

## 11. Related Policies

- **Endpoint Security Standard**: Device encryption, antivirus, and patch requirements
- **Information Security Policy**: Data classification and protection standards
- **Data Classification & Retention Policy**: Data retention and secure deletion standards
- **Remote Access & VPN Guide**: VPN requirements for mobile access

---

**Document owner:** VP IT Operations  
**Last approved:** 2026-04-11 by IT Leadership  
**Next review:** 2027-04-11
