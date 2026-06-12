---
title: Northwind Remote Access — Approved VPN Client (Standard) [ARCHIVED]
doc_id: vpn-client-standard-superseded
owner: IT Security
last_updated: 2025-09-02
status: superseded
classification: internal
supersedes: ""
superseded_by: vpn-client-standard-active
---

> **NOTICE — ARCHIVED DOCUMENT.** This version of the Standard VPN client policy has been superseded. It is retained for historical and audit reference only and must not be used to configure new endpoints. The current, authoritative policy is `vpn-client-standard-active`. If you are configuring a corporate laptop today, follow the active document, not this one.

## Scope — corporate-issued laptops connecting to Northwind internal network

This policy governs how Northwind Technologies employees use the standard remote-access client on corporate-issued laptops to reach the Northwind internal network. It applies to all full-time and part-time staff, plus approved long-term contractors, who have been provisioned a managed Windows or macOS laptop by IT. Personal devices, mobile phones, and tablets are out of scope and are covered by the separate BYOD and mobile-access standards.

The standard client is intended for routine work: reaching internal web applications, file shares, source control, ticketing systems, and internal-only administrative consoles. Privileged administrative access to production infrastructure follows additional controls described in the privileged-access standard and is not relaxed by anything in this document.

Use of any remote-access client other than the approved one named below — including personal VPN products, browser proxy extensions, or self-hosted tunnels — is prohibited and may result in the device being quarantined by IT Security.

## Approved Client (Cisco AnyConnect 4.10)

The sole approved remote-access client for the standard profile is **Cisco AnyConnect Secure Mobility Client, version 4.10**. This is the build packaged, signed, and distributed by IT through the managed software catalog. Employees must not download AnyConnect from third-party sites; only the catalog build carries the Northwind configuration profile and trust anchors.

The approved client connects to the corporate gateway at `vpn.northwind.example` using the **Standard** connection profile. On first launch the profile is pushed automatically; users should not hand-edit the XML profile or add alternate gateways. If the catalog offers a newer build than the one named here, hold and confirm with IT Security before upgrading, because gateway compatibility is validated per release.

Older or newer AnyConnect builds installed manually are unsupported. If the help desk finds an unmanaged build during a support session, it will be removed and replaced with the catalog version.

## Authentication (Duo MFA, certificate posture)

Authentication to the VPN is **multi-factor and mandatory**. The first factor is the employee's Northwind directory credential. The second factor is **Duo MFA**; push approval is the default method, with one-time passcodes available as a fallback for users in low-connectivity situations. SMS-based codes are not permitted.

In addition to the user factors, the gateway performs a **certificate posture check**. Each managed laptop carries a device certificate issued by the Northwind internal CA. At connection time the gateway validates that this certificate is present, valid, and not revoked before the tunnel is permitted to establish. A device that fails the posture check — for example, one that has been re-imaged without re-enrollment — will be refused and routed to a remediation page.

Lost or stolen devices must be reported immediately so the device certificate can be revoked, which severs that endpoint's ability to authenticate regardless of whether the user's password is still valid.

## Session Timeouts and Limits

Two timers govern every standard VPN session:

- **Idle-disconnect timeout: 15 minutes.** If the tunnel carries no user-initiated traffic for 15 continuous minutes, the gateway tears down the session. The user must reauthenticate, including completing Duo, to reconnect. This protects unattended laptops where the screen lock may not have engaged.
- **Maximum session length: 12 hours.** Regardless of activity, a single VPN session may not exceed 12 hours. At the 12-hour mark the session is forcibly terminated and a fresh authentication is required. This bounds the lifetime of any single authenticated session and forces periodic re-validation of credentials and device posture.

These limits are enforced at the gateway and cannot be extended by the client or by individual users. Requests for long-running automated connections (for example, a build agent that must stay connected) are handled through the service-account exception process, not by relaxing these timers.

## Split Tunneling Policy

Split tunneling is **disabled** on the standard profile. When the VPN is connected, **all** network traffic from the laptop is routed through the Northwind gateway, including general internet browsing. There is no local-LAN or internet bypass for the standard client.

Full-tunnel routing ensures that web filtering, DNS controls, and egress monitoring apply uniformly while a device is connected, and it prevents a compromised endpoint from bridging an untrusted local network into Northwind. Users who experience performance issues with full-tunnel routing should contact the help desk rather than attempting to enable split tunneling themselves; modifying routing to bypass the gateway is a policy violation.

## Legacy Clients (Juniper Pulse Secure 9.1 being phased out)

Prior to standardizing on Cisco AnyConnect, parts of the organization used **Juniper Pulse Secure 9.1**. That client is **being phased out** and is considered legacy. New installations of Pulse Secure are not permitted, and any remaining Pulse Secure endpoints are being migrated to the approved AnyConnect build on a rolling schedule coordinated by IT.

During the transition window, a small number of legacy gateways may continue to accept Pulse Secure connections, but they receive no new feature work and are slated for decommission. Employees still on Pulse Secure should expect a migration ticket; until then they remain subject to the same MFA, posture, timeout, and split-tunnel rules described above.

## Support and Escalation

For connection problems, certificate or posture failures, or Duo enrollment issues, contact the IT Service Desk through the standard channels. Tier-1 handles installation, profile, and authentication issues. Posture-check failures, suspected device compromise, and gateway-side problems escalate to **IT Security**.

Because this document is archived, support staff should resolve current-state questions against `vpn-client-standard-active`. Any conflict between this archived policy and the active policy is resolved in favor of the active policy.