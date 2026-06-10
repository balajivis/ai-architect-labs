---
title: Open Source Software Use Policy (Current)
doc_id: legal-open-source-software-use-policy-current
owner: Legal & Risk
last_updated: 2026-06-09
status: active
classification: internal
supersedes: legal-open-source-software-use-policy-legacy
superseded_by: ""
---

# Open Source Software Use Policy (Current)

## Purpose
This policy establishes Northwind Technologies' guidelines for evaluating, integrating, and maintaining open source software (OSS) in Northwind products and infrastructure. This policy supersedes the legacy version (effective 2024-03-01) to align with evolved practices around GPL and copyleft compliance.

## 1. License Classification & Approval

All open source licenses are classified as:

| Category | Status | Examples | Approval Required |
|---|---|---|---|
| **Permissive (Approved)** | Pre-approved | MIT, Apache 2.0, BSD-2/3, ISC, Unlicense | No; standard intake via SBOM |
| **Weak Copyleft** | Approval required | LGPL v2.1+ | VP Engineering + General Counsel |
| **Strong Copyleft (distributed)** | Approval required | GPL v2/v3, AGPL | VP Engineering + General Counsel + OSS Committee |
| **Strong Copyleft (SaaS only)** | Approved conditionally | AGPL (for internal tools only, not customer-facing) | VP Engineering approval only |
| **Restricted/Proprietary** | Not approved | Commons Clause, Elastic License, Prosperity Public License | CEO + Board approval required |

## 2. Key Change: GPL Handling (Recency Note)

**Effective 2026-06-09**, Northwind's GPL policy has evolved:

**Previous guidance (2024-03-01):** GPL libraries and tools were permitted for internal use with minimal restriction, assuming separation from distributed customer code.

**Current guidance (2026-06-09):** GPL v2/v3 **may not be integrated into Northwind Cloud distributed customer-facing code** without explicit architectural isolation. GPL remains acceptable for:
- **Internal tools** (CI/CD, build systems, admin utilities) where no GPL code is distributed to customers
- **Development dependencies** if they do not link or embed GPL code into the final product binary
- **Isolated services** if GPL code runs in a separate containerized service not distributed as part of Northwind Cloud

**Copyleft compliance strategy**: If GPL dependencies are essential, Northwind must:
1. Prove the GPL code is not linked/embedded into customer distribution
2. Document the architectural boundary in an ADR (Architecture Decision Record)
3. Obtain General Counsel approval before release
4. Include GPL source code and license notice in customer documentation if source is distributed

## 3. Approval Workflow

**Step 1: Discovery** — Developer identifies OSS dependency (new library, framework, tool).

**Step 2: License Scan** — VP Engineering or OSS Committee runs automated SBOM scan (`licensecheck`, FOSSA, or Black Duck) to identify license type and any GPL/copyleft flags.

**Step 3: Permissive Path** — If MIT, Apache 2.0, or BSD → record in `DEPENDENCIES.md` with version and source URL. No further approval.

**Step 4: Copyleft Path** — If GPL, LGPL, AGPL → submit to OSS Committee with:
- Justification (no suitable permissive alternative)
- Architectural diagram showing isolation from distributed code
- License compliance plan (source code distribution, attribution)

**Step 5: Approval** — OSS Committee (VP Engineering + General Counsel + Tech Lead) votes within 5 business days. GPL for **internal tools only** is typically fast-tracked (2 business days).

**Step 6: Integration & Documentation** — Developer records license, version, and compliance obligations in `DEPENDENCIES.md`. General Counsel adds to IP registry.

## 4. DEPENDENCIES.md Standard

All projects must maintain a `DEPENDENCIES.md` file in the repo root listing:

```markdown
## Direct Dependencies

| Name | Version | License | Justification | Compliance Notes |
|---|---|---|---|---|
| express | 4.18.2 | MIT | Web framework | None |
| lodash | 4.17.21 | MIT | Utility library | None |
| gnu-tar | 1.34 | GPL-3.0 | Build system only | Internal tool; source available in repo |
| openssl | 3.0.5 | Apache 2.0 | Crypto | None |

## Transitive Dependencies
[List any notable transitive GPL/copyleft dependencies]

## Compliance Plan
- Source code for GPL dependencies provided in `/licenses/sources/`
- GPL attribution in product THIRD-PARTY-LICENSES.txt
- No GPL code in distributed customer binaries
```

## 5. Vulnerability & Security Management

Northwind scans all OSS dependencies for security vulnerabilities:
- **Quarterly scan** — All dependencies checked against CVE databases
- **Sev-1 vulnerabilities** — Patch within 48 hours or disable the dependency
- **Sev-2 vulnerabilities** — Patch within 7 days
- **Maintenance burden** — If an OSS package is unmaintained (no updates for 2+ years) and contains Sev-2+ vulnerabilities, migrate to an actively maintained alternative

## 6. Transitive Dependencies & Supply Chain Risk

Developers must be aware that OSS dependencies bring their own dependencies. If a transitive dependency introduces a strong copyleft license (GPL, AGPL) that was not explicitly chosen, the project must:
1. Verify no redistribution occurs
2. Document the transitive dependency in `DEPENDENCIES.md`
3. Escalate to OSS Committee if the path to distribution is ambiguous

## 7. Proprietary Code + OSS Licensing

When Northwind distributes customer products that include both Northwind proprietary code and OSS:
- Permissive-licensed OSS may be freely combined
- GPL/AGPL code must be architecturally isolated (no linking to proprietary code) or relicensed agreements must be negotiated with the GPL copyright holder
- Northwind will not dual-license Northwind proprietary code under GPL; GPL code is either isolated or not used

## 8. License Exceptions & Waivers

A waiver to use non-compliant OSS (e.g., GPL in distributed code without isolation) requires:
- Documented business justification
- Written approval from CEO + General Counsel
- A remediation plan with a sunset date
- Quarterly review until resolved

## 9. Community Contributions & Attribution

Employees who contribute to open source projects (GitHub, Linux Foundation, etc.) on company time:
- Must ensure Northwind IP is not disclosed (see **Intellectual Property Policy**)
- Should use a company email for public contributions (allows Northwind to claim credit)
- Do not require prior approval for patches to non-strategic projects; notify VP Engineering for strategic contributions
- Understand that contributions become part of the OSS license (typically permissive)

---

**Related Policies:** Intellectual Property Policy; Open Source Software Use Policy (Legacy); Data Classification & Retention Policy; Vendor Procurement & Third-Party Risk Policy.

**Supersedes:** legal-open-source-software-use-policy-legacy (2024-03-01)
