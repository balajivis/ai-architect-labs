---
title: Identity & Access Management Policy (Legacy)
doc_id: identity-access-management-policy-legacy
owner: IT Security Team
last_updated: 2024-06-15
status: superseded
classification: internal
supersedes: ""
superseded_by: identity-access-management-policy
---

# Identity & Access Management Policy (Legacy – SUPERSEDED)

**ATTENTION: This policy is superseded as of 2026-05-01. See the current Identity & Access Management Policy for updated guidance.**

## 1. Authentication Standards (Superseded)

### 1.1 Password Policy (OUTDATED – DO NOT USE)

**This policy was in effect 2024-06-15 to 2026-04-30.**

- Minimum 8 characters
- Must contain uppercase, lowercase, numbers, and special characters
- Forced rotation every 90 days
- Account lockout after 3 failed attempts (30-minute lockout)

**Rationale**: This policy followed older NIST guidance (SP 800-63-3). NIST SP 800-63B (released 2017) now recommends against forced rotation, as it encourages weak passwords and post-its. Northwind aligned to current standards effective 2026-05-01.

### 1.2 Multi-Factor Authentication (Legacy)
MFA was required only for:
- VPN access
- AWS console access

This scope was insufficient. The current policy extends MFA to all cloud platforms, admin accounts, and email from external networks.

## 2. What Changed and Why

| Aspect | Legacy (until 2026-04-30) | Current (from 2026-05-01) | Reason |
|--------|---------------------------|--------------------------|--------|
| Password rotation | Every 90 days | No forced rotation | NIST guidance update; reduces weak-password risk |
| Min password length | 8 characters | 12 characters | Entropy-based approach; longer passwords more resilient |
| MFA scope | VPN + AWS only | All cloud + admin + email from non-corp | Comprehensive coverage of high-risk access |
| MFA methods | SMS only | TOTP (primary), hardware keys, SMS (fallback) | Hardware keys eliminate SIM-swap attacks |

## 3. Migration Guidance

**All users must comply with the current policy by 2026-06-15.**

If your password was set before 2026-05-01:
- You are NOT required to change it immediately
- You MUST change it within 30 days of this document (by 2026-06-15)
- Use the new 12-character standard; do not reuse old passwords

If you do not have MFA enabled:
- Enroll immediately using the current policy's approved methods
- All administrators must enroll by 2026-05-15

## 4. Sunset of Old Systems

The legacy password-rotation reminder system (automated emails every 60 days after password change) was discontinued 2026-05-02. Passwords no longer expire.

---

**Document owner:** Chief Information Security Officer  
**Original approval date:** 2024-06-15  
**Superseded date:** 2026-05-01  
**For current guidance:** See **Identity & Access Management Policy**
