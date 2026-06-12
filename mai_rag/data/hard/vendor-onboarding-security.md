---
title: Northwind Vendor Onboarding & Third-Party Security Review
doc_id: vendor-onboarding-security
owner: IT Security
last_updated: 2026-01-28
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Northwind Vendor Onboarding & Third-Party Security Review

This policy defines how Northwind Technologies evaluates, onboards, and renews third-party vendors. It is maintained by IT Security and applies to every team that procures software, services, or infrastructure on behalf of the company. The goal is to ensure that vendors who touch Northwind systems, customer data, or production environments meet a consistent security bar before any contract is signed.

## Scope — all new third-party vendors and renewals

This policy covers all new third-party vendors and all renewals of existing vendor agreements, regardless of department. "Vendor" includes SaaS providers, contractors, managed-service partners, payment processors, analytics tools, and any external party that stores, processes, or transmits Northwind data. Renewals are treated as fresh reviews: a vendor approved two years ago must re-clear the current bar, because evidence expires and risk posture drifts.

The review applies whether the vendor is paid annually, monthly, or per-seat, and whether procurement is centralized or initiated directly by an engineering, HR, finance, or customer success team. No team may sign or auto-renew a vendor agreement outside this process. Free-tier tools that nonetheless ingest customer data are in scope even when no money changes hands, because data exposure — not spend — is the controlling risk for the PII track.

## Spend Threshold Trigger ($25,000 — see expense-approval-thresholds)

A full Security review is triggered for any new vendor whose annual spend is **greater than or equal to $25,000**. This $25,000 band intentionally mirrors the procurement sign-off tier documented in `expense-approval-thresholds`; the two policies are meant to fire together so that a purchase requiring senior finance approval also requires a completed security review before the contract is countersigned.

Vendors below the $25,000 threshold follow a lightweight self-attestation path unless they fall into one of the mandatory tracks (PII processing or production-data access), which override the spend trigger entirely. In other words, spend is one of three independent triggers: cross the $25,000 line, touch customer PII, or touch production data, and the full review applies. When a vendor crosses the $25,000 line mid-contract through expansion or added seats, the next renewal — or the expansion order, whichever comes first — must go through the full review rather than waiting for the original term to lapse.

## Security Evidence Required (SOC 2 Type II, pen-test)

Vendors subject to a full review must provide current **SOC 2 Type II** evidence. We require the Type II report specifically — covering an audit period, not a point-in-time Type I attestation — so that we can evaluate operating effectiveness of the vendor's controls over time. The report must be no more than twelve months old and must cover the security trust principle at minimum; availability and confidentiality are evaluated where relevant to the engagement.

Separately, **penetration-test evidence is required for any vendor handling production data**. A SOC 2 report alone does not satisfy this requirement. Acceptable evidence is a summary or attestation from an independent third-party penetration test conducted within the last twelve months, including remediation status for any high or critical findings. Vendors that cannot produce pen-test evidence may not be granted access to production environments regardless of their SOC 2 status or contract value. IT Security maintains the evidence library and is the sole approver for exceptions, which require a documented compensating control and a defined expiry.

## Data Processing Agreements and PII (Vendgistics Risk Assessment v3)

Any vendor that processes customer **PII** must sign the standard **DPA** (Data Processing Agreement) before onboarding completes. The DPA establishes Northwind as the data controller and the vendor as the processor, sets out permitted processing purposes, breach-notification timelines, sub-processor disclosure obligations, and data-deletion commitments at contract end. No PII-processing vendor may begin handling data on a handshake or an unsigned order form.

In addition to the DPA, every PII-processing vendor must complete the **Vendgistics Risk Assessment v3** questionnaire. This is our standardized third-party risk instrument; version 3 is the only accepted revision as of this policy's last update, and earlier completed questionnaires (v1 or v2) do not carry forward. The Vendgistics Risk Assessment v3 covers data-flow mapping, encryption at rest and in transit, retention schedules, sub-processor inventory, and incident-handling maturity. IT Security scores the completed assessment and assigns a risk rating that gates final approval. A high-risk rating requires executive sign-off and a remediation plan with committed dates before the vendor is cleared.

## Access and SSO (Okta, SAML 2.0)

All vendor portals and administrative consoles used by Northwind employees must integrate with our identity provider. **SSO is enforced via Okta**, and vendor portals **must support SAML 2.0** for federation. A vendor whose application cannot support SAML 2.0 cannot be granted employee access on the standard path; local username-and-password accounts on vendor systems are prohibited for any tool in scope.

During onboarding, IT Security provisions the Okta application, configures SAML 2.0 assertions, and validates that just-in-time provisioning and deprovisioning work end to end. Deprovisioning is critical: when an employee leaves or changes roles, removing them from the Okta group must immediately revoke their vendor access. Vendors that support SCIM in addition to SAML 2.0 are preferred, because automated user lifecycle management closes the gap between an Okta change and the vendor's user directory. Multi-factor authentication is enforced at the Okta layer and may not be disabled per-vendor.

## Cross-Reference: Incident Response for Third-Party Breaches

A security review does not end at onboarding. If a vendor suffers a breach, or if Northwind data is exposed through a vendor's systems, the third-party breach path in the `incident-response-runbook` governs the response. That runbook defines notification timelines, the cross-functional response team, customer-communication obligations, and the post-incident review that may result in a vendor's suspension or termination.

The DPA breach-notification clause and the Vendgistics Risk Assessment v3 incident-handling section are designed to feed directly into that runbook: contractual notification windows must be at least as fast as the runbook requires. Vendor owners are responsible for ensuring contact details on file are current so that the incident-response team can reach the vendor's security contact without delay during an active third-party incident.