---
title: VPN Client Standard
doc_id: itsec-vpn-client-standard
owner: IT Operations
last_updated: 2026-05-01
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# VPN Client Standard

## 1. Purpose and Scope

This standard establishes VPN client requirements and configuration for secure remote access to Northwind corporate network. Effective 2026-05-01, this policy replaces the legacy VPN client standard and introduces full-tunnel (no split tunneling) as mandatory.

## 2. VPN Client Selection and Installation

### 2.1 Approved VPN Clients

| Client | Platform | Supported Versions | Mode | Download |
|---|---|---|---|---|
| **OpenVPN** | Windows, macOS, Linux | 2.6+ | Full-tunnel only | vpn.northwind.com/download |
| **Cisco AnyConnect** | Windows, macOS, Linux | 5.1+ | Full-tunnel only | vpn.northwind.com/download |

**Deprecated**: Juniper Pulse, Fortinet FortiClient (no longer supported; migrate to OpenVPN or AnyConnect)

### 2.2 Client Installation Process

1. Download VPN client from vpn.northwind.com
2. Run installer (admin privileges required)
3. Accept certificate verification prompts (Northwind root CA)
4. Import VPN profile (auto-provisioned via MDM):
   ```
   Profile name: Northwind-Austin-FullTunnel-v5
   Gateway: vpn-primary.northwind.com (primary) or vpn-secondary.northwind.com (fallback)
   Protocol: TLS 1.3 + OpenVPN (or IKEv2 + IPsec for Cisco)
   Tunnel mode: Full tunnel (NO split tunneling)
   ```
5. Test connection (see section 3.1)

## 3. Mandatory Full-Tunnel Configuration

### 3.1 Full-Tunnel Requirements

**All VPN traffic must route through the Northwind tunnel. No split tunneling permitted.**

| Traffic Type | Tunnel | Status |
|---|---|---|
| **Corporate access** (internal IPs, company SaaS) | VPN | Routed through corporate tunnel |
| **Public internet** (web browsing, personal apps) | VPN | Also routed through corporate tunnel |
| **DNS queries** | VPN | Resolved by Northwind DNS; no external DNS leaks |
| **Local network** (home printer, smart home) | **BLOCKED** | Split tunneling disabled; cannot access local network via VPN |

### 3.2 Technical Implementation

**VPN Client Routing** (Northwind side):
```
Client subnet: 10.100.0.0/16 (dynamically assigned per session)
All client traffic → Northwind gateway → DLP inspection → Corporate apps or Internet exit

Client personal traffic (e.g., YouTube) → Northwind Internet exit → Public CDNs
  (traffic leaves Northwind, not direct from client)
```

**Kill Switch Enabled** (automatic):
- If VPN tunnel drops, client network connectivity immediately blocked
- Prevents IP leak (personal traffic does NOT route unencrypted)
- Client must manually reconnect to VPN to restore connectivity

### 3.3 Implications for Users

**What works:**
- Access corporate internal systems (wikis, databases, monitoring dashboards)
- Browse the internet (via Northwind internet gateway; subject to DLP and content filtering)
- Download files from internet (cached by Northwind proxy; logs retained for compliance)

**What doesn't work:**
- Connecting to home WiFi printer from corporate laptop
- Accessing personal cloud storage (Dropbox, OneDrive) on same device simultaneously
- Local network resource access (network shares, home servers)

**Workaround**: Use second personal device for personal internet while VPN active on corporate laptop.

## 4. Authentication and MFA

### 4.1 VPN Login Requirements

**Two-factor authentication mandatory:**

1. **Username**: Corporate email (e.g., john.smith@northwind.com)
2. **Password**: Okta account password (12+ characters; NIST-compliant)
3. **MFA Method** (pick one):
   - TOTP via authenticator app (Google Authenticator, Microsoft Authenticator, Authy) – **PREFERRED**
   - Hardware security key (Yubikey, Google Titan) – **RECOMMENDED**
   - SMS – **FALLBACK ONLY** (if TOTP/key unavailable; not recommended)

**SMS NOT permitted under new policy** (changed from legacy policy where SMS was allowed).

### 4.2 MFA Recovery

If you lose MFA device:
1. Authenticate via SMS (backup method; logged as security event)
2. Contact IT immediately (it-support@northwind.com or #it-support on Slack)
3. IT resets MFA enrollment (within 2 hours)
4. Complete TOTP re-enrollment (https://idp.northwind.com/settings)

## 5. Device Posture Requirements

### 5.1 Mandatory Device Checks

Before VPN access granted, device must pass ALL posture checks. **No overrides permitted** (changed from legacy policy where overrides were allowed).

| Check | Requirement | Failure Action |
|---|---|---|
| **Firewall** | Host-based firewall enabled (Windows Defender, pf, iptables) | VPN connection denied; error message displayed |
| **Antivirus** | Antivirus engine active; signatures current (within 7 days) | VPN connection denied; error message displayed |
| **OS patches** | OS updated within 14 days of vendor release | VPN connection denied; prompts for patch installation |
| **Disk encryption** | BitLocker (Windows) or FileVault (macOS) or LUKS (Linux) | VPN connection denied; encryption setup required |
| **VPN client version** | Client version 5.1+ (Cisco) or 2.6+ (OpenVPN) | VPN update prompt; old client auto-disconnected 2026-06-01 |

### 5.2 Posture Check Bypass

**No bypass permitted.** If device fails posture check:
- VPN connection denied with specific error message
- Remediation instructions provided (e.g., "Update Windows to latest patch: go to Settings > Update & Security")
- Retry connection after remediation
- If unsure, contact IT support (it-support@northwind.com)

## 6. VPN Session Management

### 6.1 Idle Timeout

VPN sessions automatically disconnect after **2 hours of inactivity** (changed from 3 hours in legacy policy).

- **Inactivity definition**: No VPN tunnel traffic for 120 consecutive minutes
- **Pre-disconnect warning**: User receives pop-up notification at 110-minute mark
- **Reconnection**: Click "Reconnect" button or manually restart VPN client
- **Session log**: All disconnects logged for audit

### 6.2 Maximum Session Duration

VPN session automatically expires and requires re-authentication after **12 hours of continuous connection**.

- **Rationale**: Prevents credential hijacking if session token stolen
- **User action**: Reconnect (2-minute process) every 12 hours for extended remote work days

### 6.3 Concurrent Session Limit

**Maximum 2 concurrent VPN sessions per user** (e.g., laptop + mobile device).

- If user attempts 3rd connection, oldest session is terminated
- Example: Connect on work laptop at 8 AM; connect on mobile at 9 AM; reconnect on home laptop at 11 AM (first connection on work laptop auto-terminated)

## 7. VPN Performance Baseline

### 7.1 Expected Performance

| Metric | Baseline | Acceptable Range |
|---|---|---|
| **Connection time** | 15–30 seconds | <60 seconds |
| **Latency addition** | +5–10ms | <50ms |
| **Throughput** | No degradation for typical work | <10% degradation acceptable |
| **DNS resolution** | 100–200ms | <500ms acceptable |
| **Packet loss** | <0.1% | <1% acceptable |

Users experiencing performance outside acceptable range should contact IT support with:
- Device type (Windows/macOS/Linux)
- VPN client version
- ISP speed test results (speedtest.net)
- Traceroute output to corporate gateway

### 7.2 Performance Issues

**Troubleshooting steps** (in order):

1. **Check internet connection**: speedtest.net (should be normal speed)
2. **Restart VPN client**: Disconnect, wait 10 seconds, reconnect
3. **Check firewall/antivirus**: Temporarily disable third-party firewall (Windows Defender fine); retry VPN
4. **Check VPN client version**: Must be 5.1+ (Cisco) or 2.6+ (OpenVPN)
5. **Contact IT**: it-support@northwind.com with step results

## 8. VPN for External Networks

### 8.1 Where VPN Is Required

VPN **mandatory** when accessing from:
- Home or apartment (residential networks)
- Coffee shops, hotels, airports
- Mobile hotspot (cellular data)
- Public WiFi networks
- Any non-Northwind network

### 8.2 Office Network (No VPN Required)

VPN is **optional** when on Northwind corporate WiFi (office environment):
- Corporate WiFi is trusted network (WPA3 encryption, 802.1X authentication)
- Employees may work without VPN in office
- Remote employees working from home MUST use VPN

## 9. VPN and DLP (Data Loss Prevention)

All traffic through VPN tunnel is subject to DLP inspection:

**DLP blocks**:
- Uploading >10 Confidential files to personal cloud storage (Dropbox)
- Exfiltrating customer database credentials
- Accessing tor.onion or VPN-within-VPN (double-tunneling)

**DLP allows**:
- Normal web browsing, email, collaboration tools
- Downloading work-related files from approved SaaS (GitHub, Google Drive)
- Internal tool access (Datadog, GitHub, internal wikis)

If DLP blocks your access:
1. Note the blocked URL or file
2. Contact IT Security (security@northwind.com) with business justification
3. IT Security evaluates and approves (or denies) exception

## 10. Mobile VPN (iOS, Android)

### 10.1 Mobile VPN Setup

Mobile devices accessing corporate email (Outlook) or Slack must use Okta Verify app for MFA:

1. Install Okta Verify (iOS App Store or Google Play)
2. Authenticate with corporate credentials
3. Scan QR code from Okta enrollment screen
4. TOTP codes generated in Okta Verify app
5. Login to corporate apps; Okta Verify handles MFA automatically

### 10.2 VPN on Mobile

Mobile devices do NOT require a separate VPN client app:
- **iOS**: Okta Verify handles secure authentication; traffic encrypted via TLS
- **Android**: Same as iOS (no standalone VPN client needed)
- Mobile devices still benefit from full-tunnel protection (all traffic via Okta / TLS)

## 11. Contractor and Vendor VPN Access

### 11.1 Contractor VPN Setup

Contractors require:
- Separate contractor VPN account (contractor@northwind.com)
- MFA setup (TOTP required; SMS fallback available)
- Device posture checks same as employees
- Access limited to specific systems (firewall rules restrict contractor traffic)
- Session logging and audit trail

### 11.2 Automatic Access Revocation

Contractor VPN accounts auto-disable:
- At contract end date (IT notified by HR)
- After 90 days of inactivity (auto-warn at 60 days)
- Manually by IT Security if compromise suspected

## 12. VPN Logs and Audit

### 12.1 Logging

All VPN sessions logged to Splunk (see **Security Logging & SIEM**):
- Username, device hostname, connection time, duration, IP address
- Data transferred (bytes in/out, aggregate; not per-packet)
- Disconnect reason (timeout, user logout, device removed, etc.)

### 12.2 Log Retention

- **Active logs** (searchable): 1 year in Splunk
- **Archive logs**: 7 years in cold storage (S3)
- Logs used for: Incident investigation, compliance audits, legal eDiscovery

## 13. Migration from Legacy Policy

### 13.1 Legacy Policy End-of-Life

- **Legacy policy**: itsec-vpn-client-standard-legacy.md (status: superseded)
- **Enforcement date**: 2026-05-01
- **Grace period**: 2026-05-01 to 2026-05-14 (users update clients)
- **Hard cutoff**: 2026-05-15 (non-compliant clients disconnected)

### 13.2 Key Changes from Legacy

| Aspect | Legacy | Current |
|---|---|---|
| **Tunnel mode** | Split tunnel allowed | Full tunnel mandatory |
| **SMS MFA** | Allowed | Fallback only |
| **Idle timeout** | 3 hours | 2 hours |
| **Device posture overrides** | Allowed with password | No overrides permitted |

## 14. Related Policies

- **Remote Access & VPN Guide**: General VPN usage and setup
- **Endpoint Security Standard**: Device encryption and antivirus requirements
- **Security Logging & SIEM**: VPN log retention and audit
- **Information Security Policy**: Data protection and classification standards
- **Incident Response Runbook**: VPN credential compromise response

---

**Document owner:** VP IT Operations  
**Last approved:** 2026-05-01 by IT Leadership  
**Policy effective:** 2026-05-01 (supersedes legacy policy)  
**Next review:** 2027-05-01
