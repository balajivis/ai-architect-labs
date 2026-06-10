---
title: Network Security Architecture
doc_id: itsec-network-security-architecture
owner: IT Infrastructure Team
last_updated: 2026-04-15
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Network Security Architecture

## 1. Purpose and Scope

This document describes Northwind's network security architecture, including firewalls, DMZs, network segmentation, and perimeter defense. It applies to all network infrastructure managed by IT Operations.

## 2. Network Segmentation

### 2.1 Trust Zones

Northwind's network is divided into four trust zones:

| Zone | Purpose | Security Level | Example Resources |
|---|---|---|---|
| **Corporate** | Employee workstations, printers, corporate VPN | Medium | Laptops, office WiFi, internal wikis |
| **Development** | Code repositories, CI/CD pipelines, staging databases | High | GitHub Enterprise, Datadog, non-prod databases |
| **Production** | Customer-facing applications, production databases | Critical | AWS RDS, load balancers, API servers |
| **DMZ** | Public-facing services, web servers, email gateways | Medium-High | Web servers, reverse proxies, email filters |

### 2.2 Inter-Zone Communication

- **Corporate ↔ Development**: VPN required; traffic inspected by firewall; rate-limited to prevent abuse
- **Development ↔ Production**: No direct communication; all data flows through API gateways; logged and monitored
- **Production ↔ Internet**: Whitelist-only model; all inbound filtered by WAF (Web Application Firewall); outbound restricted to known CDNs and vendor APIs
- **DMZ ↔ Internal**: No direct access; DMZ services authenticate to internal systems via read-only credentials

### 2.3 VLAN Isolation

- Each zone operates on separate VLANs
- VLANs are isolated at the L3 firewall; routing between VLANs requires explicit rules
- Guest WiFi is isolated from corporate VLAN

## 3. Perimeter Defense

### 3.1 Firewall Architecture

- **Primary Firewall**: Palo Alto Networks PA-7060 (active-active HA)
- **Secondary Firewall**: Palo Alto Networks PA-5220 (offsite, async replication)
- Both firewalls maintain synchronized security policies
- Failover is automatic; RTO for firewall failure is 15 minutes

### 3.2 Firewall Rules (High-Level)

**Inbound Rules** (from Internet):
- HTTPS (443) → Web servers in DMZ – permitted
- SSH (22) → DMZ bastion only – restricted to specific IP ranges (GitHub Actions, on-call engineers)
- HTTP (80) → Redirects to HTTPS
- All other inbound traffic → Blocked

**Outbound Rules**:
- HTTPS (443) to known CDNs (Akamai, Cloudflare) – permitted
- SMTP (25/587) to email vendors (SendGrid) – permitted with rate limiting
- DNS (53) to external resolvers – permitted
- All other outbound – Blocked

See **Firewall Change Management** for procedure to modify rules.

### 3.3 DDoS Mitigation

- DDoS protection via AWS Shield Advanced (automatic)
- Volumetric attacks (DNS amplification, SYN floods) filtered by AWS edge
- Application-layer attacks (HTTP floods) mitigated by WAF and rate limiting
- Escalation path: Security team paged on >100 Gbps attack

## 4. VPN Gateway Architecture

### 4.1 VPN Concentrators

- **Primary**: Cisco ASA 5516-X (on-premises, Austin)
- **Secondary**: AWS VPN endpoint (failover)
- VPN concentrators terminate all remote user sessions
- Session logs sent to Splunk in real-time (see **Security Logging & SIEM**)

### 4.2 VPN Client Requirements

All VPN clients must support:
- Cisco AnyConnect or OpenVPN protocol (OpenVPN preferred for cost)
- Mandatory TOTP-based MFA (not SMS)
- Device posture checking (full disk encryption, firewall enabled, antivirus current)
- Kill switch (automatic VPN disconnect if tunnel fails, preventing IP leak)

See **VPN Client Standard** for detailed client configuration and support.

## 5. Intrusion Detection and Prevention

### 5.1 IDS/IPS Deployment

- **Inline IPS** at perimeter (Palo Alto Threat Prevention)
- **Network TAP** (passive) in development zone for deep packet inspection
- **Host-based IPS** on critical servers (falconctl agent, part of CrowdStrike Falcon)

### 5.2 Alerting Thresholds

| Alert Type | Threshold | Action |
|---|---|---|
| Port scan | >50 unique ports probed in 5min | Block source IP; alert SOC |
| Malware signature match | Any detection | Auto-block; quarantine flow; notify host |
| Exfiltration attempt (DLP) | Confidential data leaving network | Block; log; escalate to VP Security |
| Brute force (SSH) | >10 failed logins in 5min | Rate-limit source; alert on-call engineer |

## 6. DNS Security

### 6.1 Internal DNS

- Northwind operates authoritative DNS servers for internal zones (*.northwind.local)
- DNS queries cached by internal resolvers; external queries forwarded to AWS Route 53
- No split-horizon DNS; internal and external DNS names are consistent

### 6.2 DNS Filtering

- Malicious domains blocked at DNS layer (using threat feeds from Cloudflare and VirusTotal)
- Phishing domains blocked automatically
- Gambling, adult content filtered (employee requests must go through VP People)
- DNS logs retained for 90 days; available to security team for incident investigation

## 7. Network Monitoring and Telemetry

### 7.1 NetFlow Collection

- All network traffic sampled via NetFlow v9 and exported to Splunk
- Sampling rate: 1-in-100 for normal traffic, 1-in-5 for suspicious flows
- Metadata collected: source IP, destination IP, port, protocol, bytes transferred
- Retention: 1 year in Splunk, 7 years in archive storage

### 7.2 Bandwidth Monitoring

- Utilization monitored per VLAN and egress link
- Alert if any link exceeds 80% capacity for >15 minutes
- DDoS detection if egress exceeds 100 Gbps sustained

## 8. Network Change Management

All changes to network infrastructure (firewall rules, VLAN additions, routing changes) must:
1. Be documented in a change request (see **Firewall Change Management**)
2. Undergo peer review by at least 1 other network engineer
3. Be tested in a non-production lab before deployment
4. Have a rollback plan
5. Be approved by IT Director before implementation

Emergency changes (active incident response) may bypass approval but must be logged and reviewed within 24 hours.

## 9. Related Policies

- **Firewall Change Management Policy**: Detailed procedures for firewall rule changes
- **Security Logging & SIEM Policy**: Network telemetry and log retention
- **Information Security Policy**: General data classification and access controls
- **Incident Response Runbook**: Network incident escalation paths

---

**Document owner:** VP Infrastructure  
**Last approved:** 2026-04-15 by Infrastructure Steering Committee  
**Next review:** 2027-04-15
