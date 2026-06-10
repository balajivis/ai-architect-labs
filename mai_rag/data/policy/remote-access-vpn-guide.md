---
title: Remote Access & VPN Guide
doc_id: remote-access-vpn-guide
owner: IT Operations
last_updated: 2026-02-20
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Remote Access & VPN Guide

## 1. Purpose

This guide covers secure remote access to Northwind's corporate network and internal systems. All remote users must follow these practices.

## 2. VPN Access Requirements

### 2.1 Who Needs VPN?

VPN is required when accessing:
- Internal wiki and intranet systems
- Development databases and servers
- Private code repositories (GitHub Enterprise)
- Internal monitoring dashboards (Grafana, Splunk)
- Employee records or HR systems
- Any data classified as Confidential or Restricted (see **Data Classification & Retention Policy**)

VPN is NOT required for:
- Public cloud resources (AWS, Azure) – use IAM authentication instead
- SaaS tools accessed via SSO (Okta)
- Company email and calendar

### 2.2 VPN Setup

1. Enroll in Okta (SSO) – your employee account is automatically created on Day 1
2. Generate TOTP (Time-based One-Time Password) in authenticator app
3. Request VPN access from IT (vpn-access@northwind.com) with manager approval
4. Download VPN client: Cisco AnyConnect (Windows, macOS, Linux) or OpenVPN (all platforms)
5. Import VPN configuration file; connection is authenticated via Okta + TOTP

### 2.3 Mandatory Multi-Factor Authentication

All VPN sessions require:
1. Username and password (Okta account)
2. TOTP from authenticator app (not SMS)

Hardware security keys (Yubikey, Google Titan) are accepted as MFA alternative; SMS is not permitted for VPN.

## 3. VPN Usage Standards

### 3.1 Connection Requirements
- **Default policy**: Always use VPN when working from non-Northwind network (home, coffee shop, airport, hotel)
- **Office policy**: VPN is optional when on Northwind's corporate WiFi (office is automatically trusted)
- **Personal hotspot**: Use VPN (personal hotspot is untrusted)

### 3.2 Idle Timeout
- VPN session automatically disconnects after 2 hours of inactivity
- Users must re-authenticate to reconnect
- This prevents credential theft if device is left unattended

### 3.3 Device Requirements for VPN

Your device must have:
- Operating system updated within 14 days of vendor release
- Antivirus/antimalware engine active with signatures updated daily
- Full device encryption enabled (BitLocker for Windows; FileVault for macOS)
- Host-based firewall enabled
- No unauthorized software or browser extensions
- Device enrolled in Mobile Device Management (MDM)

Devices not meeting these requirements will be blocked from VPN.

## 4. Traveling with Corporate Data

See **Expense & Travel Policy** for requirements when traveling with laptops containing Confidential data. Key points:
- Only carry encrypted devices with MFA
- Always use VPN when accessing corporate systems from hotel or international networks
- Report lost devices immediately to IT Security

## 5. Split Tunneling Policy

**Split tunneling is disabled.** All traffic from your device routes through the VPN, including:
- Web browsing
- Email
- Streaming

This prevents data exfiltration through unmonitored channels and protects against DNS hijacking or malicious WiFi networks.

## 6. VPN Performance and Troubleshooting

### 6.1 Typical Performance
- Connection establishment: 10–30 seconds
- Latency addition: +10–50ms
- Throughput: Typically no noticeable degradation for normal work (email, web, small file transfers)

If your VPN is slow:
1. Check internet connection speed (https://speedtest.net)
2. Check VPN server load (IT dashboard shows connection count)
3. Contact IT if degradation persists

### 6.2 Connection Issues

| Symptom | Likely Cause | Resolution |
|---------|--------------|-----------|
| "Authentication failed" | Expired Okta password, stale TOTP | Re-generate TOTP in authenticator app; reset password in Okta |
| Drops after 2 hours | Idle timeout | Expected behavior; reconnect with credentials |
| Cannot resolve internal hostnames | DNS not routing correctly | Verify VPN connected; try flushing DNS cache (ipconfig /flushdns on Windows) |
| Intermittent drops | WiFi roaming or interference | Switch to wired connection or different WiFi band; restart VPN client |

Contact IT support: it-support@northwind.com or Slack #it-support-tickets

## 7. VPN Logs and Monitoring

All VPN connections are logged for security and compliance purposes:
- Username, IP address, connection time, duration, data transferred
- Logs retained for 1 year
- May be audited during incident investigation

If you see login activity you don't recognize, notify security@northwind.com immediately.

## 8. Contractor and Third-Party Access

Contractors and vendors can request temporary VPN access via the **Vendor Procurement & Third-Party Risk Policy**. Access is limited to:
- Specific IP ranges and internal hosts
- 8-hour day (9 AM to 5 PM PT, can be extended if needed)
- Auto-revocation at project end

All contractors must complete security training and sign an acceptable use agreement.

## 9. Related Policies

- **Information Security Policy**: General security standards for all remote access
- **Acceptable Use Policy**: Prohibited uses of corporate network
- **Data Classification & Retention Policy**: Data handling rules when working remotely
- **Incident Response Runbook**: Steps if your VPN credentials are compromised

---

**Document owner:** IT Operations Manager  
**Last approved:** 2026-02-20 by IT Leadership  
**Next review:** 2027-02-20
