---
title: VPN Client Standard (Legacy)
doc_id: itsec-vpn-client-standard-legacy
owner: IT Operations
last_updated: 2026-04-30
status: superseded
classification: internal
supersedes: ""
superseded_by: "itsec-vpn-client-standard"
---

# VPN Client Standard (Legacy)

**STATUS: SUPERSEDED as of 2026-05-01. See [VPN Client Standard](itsec-vpn-client-standard.md) for current policy.**

## 1. Purpose and Scope

This document describes the legacy VPN client configuration standard in effect until 2026-04-30. All users must upgrade to the new VPN client standard effective 2026-05-01.

## 2. Legacy VPN Client Options

### 2.1 Supported VPN Clients

| Client | Platform | Status | Tunnel Mode | MFA |
|---|---|---|---|---|
| **Cisco AnyConnect** | Windows, macOS, Linux | Supported | Split tunnel | TOTP + hardware key |
| **OpenVPN** | Windows, macOS, Linux | Supported | Split tunnel | TOTP + hardware key |

**Deprecated (no longer supported)**:
- Juniper Pulse: End-of-life 2025-01-01; users migrated to OpenVPN
- Fortinet FortiClient: Performance issues; OpenVPN preferred

### 2.2 Split Tunneling (Allowed Under Legacy Policy)

**Important**: Split tunneling was allowed under this legacy policy. Users could configure their VPN client to route only corporate traffic through the VPN tunnel and allow personal internet traffic (web browsing, personal cloud storage) through the local internet connection.

This was NOT a security best practice and has been eliminated in the new policy.

**Split tunnel configuration example (legacy)**:
```
Routing policies:
- 10.0.0.0/8 (corporate internal) → VPN tunnel
- 192.168.0.0/16 (customer networks) → VPN tunnel
- 0.0.0.0/0 (all other) → Local internet gateway
```

## 3. Legacy Connection Requirements

### 3.1 Authentication

- Username (corporate email)
- Password (Okta account)
- TOTP from authenticator app (preferred) OR SMS fallback

**Important change in new policy**: SMS is NO LONGER PERMITTED under new policy effective 2026-05-01.

### 3.2 Device Posture Checking

Optional under legacy policy; devices not meeting posture requirements could still connect if user provided override password (not recommended, but allowed):

| Check | Requirement | Failure Handling (Legacy) |
|---|---|---|
| Firewall enabled | Windows Defender or 3rd-party firewall | Override allowed; warning displayed |
| Antivirus enabled | Windows Defender, CrowdStrike, or Rapid7 | Override allowed; warning displayed |
| OS patch level | Within 30 days | Override allowed; warning displayed |
| Disk encryption | BitLocker (Windows) or FileVault (macOS) | Required; no override |

**Important change in new policy**: Posture checking now mandatory; no overrides permitted.

## 4. Legacy Idle Timeout

VPN session automatically terminates after **3 hours of inactivity**.

**Changed in new policy**: Idle timeout reduced to 2 hours for higher security.

## 5. Performance and Troubleshooting (Legacy)

### 5.1 Known Issues with Legacy Config

- **Split tunnel misconfiguration**: Users sometimes broke corporate traffic routing; required IT support to troubleshoot
- **DNS leak**: Personal DNS queries sometimes leaked outside VPN tunnel; user personal data exposed
- **Slow connect time**: OpenVPN negotiation took 45–90 seconds
- **Frequent drops**: Long-lived connections (>4 hours) sometimes hung; required manual reconnect

## 6. Compliance Gaps (Legacy Policy)

This legacy policy had compliance gaps that motivated the new mandatory full-tunnel policy:

| Compliance Requirement | Requirement | Legacy Gap |
|---|---|---|
| **NIST 800-46** | VPN should encrypt all traffic | Split tunneling allowed unencrypted traffic |
| **PCI DSS 4.1** | Encrypt all data in transit | Split tunnel allowed unencrypted card data flow |
| **GDPR Article 32** | Encryption of personal data | Split tunnel PII exposure risk |
| **SOC 2 CC6.1** | Logical access controls | Split tunnel weak enforcement |

## 7. Migration Path to New Policy

### 7.1 Timeline for Upgrade

- **2026-05-01**: New VPN client standard effective; split tunneling disabled network-wide
- **2026-05-01 to 2026-05-14**: Grace period (14 days) for user client software updates
- **2026-05-15**: Enforcement begins; non-compliant clients disconnected from VPN

### 7.2 User Actions Required

All users must:
1. Update VPN client to version 5.1+ (Cisco) or 2.6+ (OpenVPN) by 2026-05-14
2. Re-import VPN profile (automatic; pushed via MDM)
3. Test VPN connection (ensure full-tunnel mode active)
4. Notify IT if connection fails (support ticket)

### 7.3 Support During Migration

- **IT Help Desk**: Extended hours (7 AM–11 PM PT) during migration week
- **FAQ document**: https://wiki.northwind.com/vpn-migration-faq
- **Self-service portal**: Download new VPN client and profile

## 8. Configuration Archival

This legacy configuration documented for:
- **Historical reference**: Understand what was allowed and why it changed
- **Audit trail**: Support SOC 2 and compliance audits (prove we upgraded controls)
- **Incident forensics**: If VPN-related breach investigated, legacy vs. new policy distinctions clear

---

**Document owner:** VP IT Operations  
**Status changed to SUPERSEDED:** 2026-05-01  
**Legacy policy in effect:** 2024-06-01 to 2026-04-30  
**New policy effective:** 2026-05-01 (see [VPN Client Standard](itsec-vpn-client-standard.md))
