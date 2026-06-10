---
title: Open Source Software Use Policy (Legacy)
doc_id: legal-open-source-software-use-policy-legacy
owner: Legal & Risk
last_updated: 2024-03-01
status: superseded
classification: internal
supersedes: ""
superseded_by: legal-open-source-software-use-policy-current
---

# Open Source Software Use Policy (Legacy)

## Status
**SUPERSEDED as of 2026-06-09.** This policy represents Northwind's prior approach to GPL licensing. See **Open Source Software Use Policy (Current)** for the active standard.

## Purpose
This policy established guidelines for using open source software (OSS) in Northwind products. The legacy version permitted broader use of GPL and copyleft licenses with fewer restrictions.

## 1. License Categories (Legacy)

| Category | Status | Examples | Approval |
|---|---|---|---|
| **Permissive** | Approved | MIT, Apache 2.0, BSD | No approval |
| **Weak Copyleft** | Approved | LGPL v2.1+ | VP Engineering sign-off |
| **Strong Copyleft** | Approved | GPL v2/v3, AGPL | VP Engineering sign-off only |
| **Restricted** | Not approved | Commons Clause, Elastic License | CEO approval |

## 2. GPL Handling (Legacy Approach)

Under the legacy policy (in effect 2024-03-01 through 2026-06-08), GPL and AGPL code was permissible in distributed Northwind Cloud products provided that:
- Build scripts and deployment tools clearly separated GPL code from proprietary Northwind code
- Customer documentation disclosed GPL source availability
- Northwind believed architectural separation was sufficient to avoid GPL copyleft propagation

**Issue**: This approach did not account for linking, embedding, or derivative work concerns. The current policy imposes stricter isolation requirements.

## 3. Migration Path

Teams currently relying on GPL dependencies should:
1. Review **Open Source Software Use Policy (Current)** for new requirements
2. Submit architecturally non-compliant GPL uses to the OSS Committee before 2026-12-31
3. Plan migration to permissive alternatives or architectural isolation within 6 months
4. Document any GPL dependencies in `DEPENDENCIES.md` with a transition plan

---

**Status**: SUPERSEDED. Do not use this policy for new decisions. Refer to **Open Source Software Use Policy (Current)** for active guidelines.
