---
title: Cookie & Tracking Policy
doc_id: data-priv-cookie-tracking-policy
owner: Chief Privacy Officer
last_updated: 2026-04-15
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Cookie & Tracking Policy

## 1. Overview and Legal Basis

Northwind Technologies uses cookies, pixels, and similar tracking technologies on northwindcloud.com and associated properties to deliver functionality, improve the platform, and understand user behavior. This policy discloses all tracking technologies and the legal basis for their use under GDPR, CCPA, and ePrivacy Directive.

**Scope**: This policy applies to:
- First-party cookies set by Northwind domains
- Third-party cookies and pixels from vendors
- Local storage, session storage, and other browser storage mechanisms
- Server-side tracking (analytics, fraud detection, logging)

## 2. Cookie Categories and Legal Basis

### 2.1 Strictly Necessary Cookies (No Consent Required)

These cookies are essential for basic platform functionality and are **not consent-dependent** under ePrivacy Directive.

| Cookie Name | Domain | Purpose | Data Collected | Retention |
|---|---|---|---|---|
| `session_id` | northwindcloud.com | Authenticate logged-in users; maintain session state | User ID, session timestamp | 24 hours after logout |
| `csrf_token` | northwindcloud.com | Prevent Cross-Site Request Forgery attacks | Random token (no PII) | Session duration |
| `lang_preference` | northwindcloud.com | Store user language/locale setting | Language code (e.g., "en_US") | 1 year |
| `cookie_banner_dismissed` | northwindcloud.com | Remember that user has seen cookie consent banner | Boolean flag | 1 year |
| `auth_mfa_temp` | northwindcloud.com | Store temporary MFA challenge state during login | MFA nonce (no PII) | 10 minutes |

**Legal Basis**: GDPR Article 6(1)(b) — **Contract** (necessary to provide the service); ePrivacy Directive — exempt from consent requirement.

### 2.2 Functional Cookies (Require Consent)

These cookies enhance user experience and remember preferences but are not strictly necessary.

| Cookie Name | Domain | Purpose | Data Collected | Consent | Retention |
|---|---|---|---|---|---|
| `user_dashboard_layout` | northwindcloud.com | Remember user's preferred dashboard widget arrangement | JSON layout configuration | Opt-in consent (checkbox in Settings) | 2 years |
| `recent_projects` | northwindcloud.com | Cache recently accessed project IDs for quick navigation | Project IDs (no user data) | Implied consent (necessary UX) | 90 days |
| `dark_mode_preference` | northwindcloud.com | Store dark/light theme choice | Boolean (true/false) | Implied consent (UX preference) | 1 year |

**Legal Basis**: GDPR Article 6(1)(a) — **Explicit Consent** (user must opt in); ePrivacy Directive — consent required.

### 2.3 Analytics Cookies (Require Explicit Consent)

Northwind uses third-party analytics to measure usage, performance, and identify improvement opportunities. These cookies transmit personal data (IP address, user ID, event names) to analytics vendors.

| Vendor | Cookie Names | Data Collected | Legal Basis | Consent | Recipient (Processor) |
|---|---|---|---|---|---|
| **Google Analytics 4** | `_ga`, `_gat`, `_gid` | Anonymous user ID, page views, event names, approximate location (country), device type | GDPR 6(1)(a) — Consent | Explicit opt-in required | Google (US; SCC in place) |
| **Datadog Real User Monitoring** | `_dd_r` | Page load time, errors, session replays (no keystroke logging) | GDPR 6(1)(a) — Consent | Implicit consent (enabled by default; user may opt-out in Settings) | Datadog (US; SCC in place) |
| **Hotjar** | `_hjid`, `_hjpvs` | Heatmaps, click maps, user session recordings (redact PII on forms) | GDPR 6(1)(a) — Consent | Explicit opt-in required; disabled for EU visitors by default | Hotjar (EU; Privacy Shield successor SCC) |

**Legal Basis**: GDPR Article 6(1)(a) — **Explicit Consent** required (not implied); ePrivacy Directive — explicit consent required for non-essential cookies.

### 2.4 Marketing and Retargeting Cookies (Require Explicit Consent)

Northwind uses retargeting pixels to display ads to visitors who have left the site without converting.

| Vendor | Cookie Names | Data Collected | Legal Basis | Consent |
|---|---|---|---|---|
| **Facebook Pixel** | `_fbp` | User ID (hashed), page visits, purchase events (for retargeting) | GDPR 6(1)(a) — Consent | Explicit opt-in required |
| **Google Ads / Conversion Tracking** | `_gac`, `_gat` | Conversion events (form submitted, demo booked) | GDPR 6(1)(a) — Consent | Explicit opt-in required |
| **LinkedIn Insight Tag** | `li_buid`, `lang` | LinkedIn member ID, page visits (for B2B retargeting) | GDPR 6(1)(a) — Consent | Explicit opt-in required |

**Legal Basis**: GDPR Article 6(1)(a) — **Explicit Consent** required; ePrivacy Directive — consent required.

## 3. Cookie Consent Banner and Management

### 3.1 Consent Implementation

Northwind deploys a **cookie consent banner** on the first visit to northwindcloud.com:

```
┌─────────────────────────────────────────────────────────────────┐
│ COOKIE CONSENT                                                  │
│                                                                 │
│ We use cookies to improve your experience. We use three types:  │
│ • Essential (always on)                                        │
│ • Functional & Analytics (you choose)                          │
│ • Marketing (you choose)                                       │
│                                                                 │
│ [ Accept All ]  [ Customize ]  [ Reject All ]                 │
│                                                                 │
│ Learn more: northwindcloud.com/privacy/cookies                 │
└─────────────────────────────────────────────────────────────────┘
```

**User choices**:
- **Accept All**: Essential + Functional + Analytics + Marketing cookies enabled
- **Customize**: User selects which non-essential categories to enable (default: all off)
- **Reject All**: Essential only; non-essential cookies disabled

**Default behavior**:
- **US/non-EU visitors**: Non-essential cookies are enabled by default; user may opt-out
- **EU/EEA visitors**: Non-essential cookies are disabled by default; user must explicitly opt-in

### 3.2 Consent Storage and Verification

- Consent choice is stored in `consent_preferences` cookie (1 year expiry)
- Consent choice is also logged in Northwind's database for audit purposes
- Users can change consent settings anytime in Settings → Privacy → Cookie Preferences

### 3.3 Granular Consent Options

Users can independently opt in/out of each category:

```
Settings > Privacy > Cookie Preferences

✓ Essential Cookies (always enabled)
  └ Authentication, security, CSRF protection

□ Functional Cookies (user may disable)
  └ Dashboard layout, dark mode, language

□ Analytics Cookies (user may disable)
  └ Google Analytics, Datadog RUM, Hotjar

□ Marketing Cookies (user may disable)
  └ Facebook, Google Ads, LinkedIn pixels
```

## 4. Data Retention and Deletion

| Cookie Type | Retention | Deletion Method | Legal Driver |
|---|---|---|---|
| **Strictly Necessary** | 24 hours (session) | Auto-delete on logout | Contract requirement |
| **Functional** | 2 years | User delete via Settings; auto-delete on cookie expiry | User choice |
| **Analytics** | 26 months (aggregated) | Google Analytics auto-deletes after 26 months; Datadog per customer SLA | GDPR data minimization |
| **Marketing** | 13 months | User opt-out; vendor purges on user request | GDPR Article 17 (erasure) |

**Analytics aggregation**: Google Analytics and Datadog aggregate user-level data after 3 months and delete raw session logs. Retained aggregate data (e.g., "10% of users access feature X") is no longer identifiable as personal data.

## 5. Third-Party Vendor Management

All third-party cookies are subject to:
- **Data Processing Agreement (DPA)** in place (see **Data Processing Agreement (DPA) Standard**)
- **Annual security audit** (SOC 2 or equivalent)
- **Data transfer assessment**: If vendor is non-EU, Standard Contractual Clauses (SCC) must be in place

**Current vendor status**:

| Vendor | Status | DPA | Audit | Transfer Mechanism |
|---|---|---|---|---|
| Google Analytics | ✅ Active | ✅ Yes | ✅ SOC 2 (2025) | SCC (EU Standard Clauses) |
| Datadog | ✅ Active | ✅ Yes | ✅ SOC 2 (2025) | SCC |
| Hotjar | ✅ Active | ✅ Yes | ✅ ISO 27001 (2026) | EU Data Subject; local processing |
| Facebook Pixel | ✅ Active | ✅ Yes | ✅ SOC 2 (2025) | SCC |
| Google Ads | ✅ Active | ✅ Yes | ✅ SOC 2 (2025) | SCC |
| LinkedIn Insight | ✅ Active | ✅ Yes | ✅ SOC 2 (2025) | SCC |

## 6. User Rights and Opt-Out

### 6.1 Opting Out

Users can opt-out of non-essential cookies:
1. **Browser settings**: Most browsers allow users to block third-party cookies via Settings
2. **Northwind's privacy settings**: northwindcloud.com/privacy/cookies (requires login)
3. **Vendor opt-outs**:
   - Google Analytics: https://tools.google.com/dlpage/gaoptout
   - Hotjar: https://www.hotjar.com/opt-out
   - Facebook: https://www.facebook.com/about/ads

### 6.2 Right to Access and Deletion

Under GDPR Article 15 (access) and Article 17 (erasure):
- Users may request a copy of all cookies and tracking data collected about them
- Users may request deletion of all marketing and analytics cookies
- Northwind must comply within 30 days (see **Data Subject Rights Procedure**)

## 7. Special Categories: Sensitive Data and Children

### 7.1 No Sensitive Data in Cookies

Northwind **never stores** the following in cookies:
- Health information
- Biometric data
- Religion, race, sexual orientation
- Government ID numbers (SSN, driver's license)
- Payment card information
- Passwords or authentication credentials

If sensitive data must be stored, it is encrypted and stored in the database, not in cookies.

### 7.2 Children Under 13

Northwind Cloud is a **B2B SaaS platform** and is not directed at children under 13. However:
- If a child under 13 uses Northwind Cloud via a parent/guardian account, analytics tracking is disabled
- Parental consent notice is displayed on company domains if child activity is detected

## 8. Email and Non-Web Tracking

### 8.1 Email Pixels and Tracking Links

Northwind may include **email tracking pixels** in marketing emails to measure open rates and click-through rates. These pixels:
- Collect email open events (time, IP address, device)
- Transmit via third-party email service (Sendgrid, Mailchimp)
- Retain for 1 year

**User consent**: Included in marketing email consent; users may unsubscribe anytime.

### 8.2 Email Unsubscribe and Preferences

Every marketing email includes an unsubscribe link compliant with CAN-SPAM (US) and GDPR (EU):
- Users unsubscribed within 10 days
- Unsubscribe is logged and honored; no further marketing emails sent
- User data is retained for 1 year to prevent re-subscription (CAN-SPAM rule)

## 9. Compliance and Audit

### 9.1 Annual Review

The Chief Privacy Officer audits this policy annually:
- Review vendor list for new/removed cookies
- Audit consent banner for accuracy
- Sample 100+ user consent records; verify correct cookie behavior
- Test opt-in and opt-out flows for EU/US visitors

### 9.2 Incident Response

If a tracking vendor experiences a breach or violates the DPA:
- Incident is escalated to VP Security and Chief Privacy Officer (see **Incident Response Runbook**)
- If data breach involves user personal data, affected users are notified within 72 hours
- Vendor is placed on probation; SLA is tightened; future audit is accelerated

---

**Document owner:** Chief Privacy Officer  
**Last approved:** 2026-04-15 by Privacy Leadership  
**Next review:** 2027-04-15
