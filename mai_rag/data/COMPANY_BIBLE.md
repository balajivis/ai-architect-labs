# Northwind Technologies — Canonical Company Bible

**This file is the single source of truth.** Every corpus document must stay
consistent with the facts, names, and acronyms below. Do not contradict an
anchor fact; you may *add* detail around it.

## Identity
- **Northwind Technologies** — B2B SaaS company, ~1,200 employees, HQ in Austin TX, remote-friendly. Founded 2016. Flagship product: "Northwind Cloud" (a data-integration platform).
- Cloud stack: **AWS** (primary) + **Azure** (secondary). Identity via **Okta SSO**. Code on **GitHub**; CI/CD via **GitHub Actions**; observability via **Datadog**; on-call via **PagerDuty**. Corporate VPN for remote access.
- Leadership roles referenced across docs: **CEO**, **VP Security**, **VP Engineering**, **General Counsel**, **Chief Privacy Officer**, **CFO**, **VP People**, **Board of Directors**.

## Anchor facts (NEVER contradict — golden cases depend on these)
- **MFA is mandatory for all VPN access.** Approved methods: TOTP authenticator app (preferred), hardware security key, SMS (fallback only).
- **Data classification** has four levels: **Public · Internal · Confidential · Restricted.** PII (SSN, government ID, home address) is **Confidential or Restricted** and requires encryption at rest and in transit.
- **Password policy (CURRENT, effective 2026-05-01):** no forced rotation; change only if compromised; **minimum 12 characters**; NIST-aligned. *(The legacy policy — 90-day rotation, 8-char minimum — is SUPERSEDED, dated 2024-06-15.)*
- **Travel with Confidential data:** device must be encrypted (BitLocker or FileVault); corporate access from external/hotel networks requires VPN + MFA.
- **Incident severities:** **Sev-1** → RTO 4h, RPO 1h, notify the executive team (CEO, VP Security, VP Engineering, General Counsel, Chief Privacy Officer, Board) ; **Sev-2** → RTO 8h, notify VP Security, affected customers notified within 48h ; Sev-3/Sev-4 lower.
- **Admin access** to cloud consoles (AWS/Azure) requires explicit **IT Security approval** with documented business justification.
- **PTO** accrues at **1.5 days/month** (0.75 for a mid-month start); there is a maximum accrual cap.
- **Onboarding Day 1:** 3 hours mandatory security training (Information Security Awareness — 1h, 80% pass required; Acceptable Use; Data Handling), plus MFA enrollment, which gates VPN access.
- **Expenses over $75 require an itemized receipt.**
- **Production deploys:** a customer-impacting error-rate spike (e.g. 5%) is a **Sev-2**; deployment lead assesses and may roll back within 30 minutes.

## Acronym glossary (use consistently)
MFA · SSO · TOTP · RTO (recovery time objective) · RPO (recovery point objective) · PII · DLP (data loss prevention) · BCP (business continuity plan) · SLA · SLO · PTO · ADR (architecture decision record) · DPA (data processing agreement) · GDPR · RBAC · SoD (segregation of duties).

## Document style contract
Each document is a separate markdown file with YAML frontmatter, then body:
```
---
title: <Human Title>
doc_id: <kebab-case, matches filename without .md>
owner: <Team>
last_updated: 2026-0X-XX
status: active            # active | superseded
classification: internal  # public | internal | confidential | restricted
supersedes: ""            # doc_id or ""
superseded_by: ""         # doc_id or ""
---

# <Human Title>
... 350–800 words, numbered clauses, 1–2 tables where natural ...
```

## Design requirements baked into every cluster
- **Cross-reference** other documents by title ("see the Data Classification & Retention Policy").
- **Multi-hop**: some answers must require combining two documents.
- **Distractors**: near-duplicate topics so a naive retriever can grab the wrong chunk.
- **Surface variety**: acronyms, synonyms, and at least one table per few docs.
