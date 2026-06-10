---
title: Knowledge Base Standards
doc_id: cs-knowledge-base-standards
owner: Customer Support / Documentation
last_updated: 2026-06-09
status: active
classification: internal
supersedes: ""
supersewed_by: ""
---

# Knowledge Base Standards

## 1. Overview
The Northwind Cloud Knowledge Base (KB) is the self-service resource customers use to resolve issues, learn platform features, and troubleshoot integrations. This policy establishes content standards, ownership, and quality gates to ensure KB articles remain accurate, discoverable, and helpful.

## 2. Knowledge Base Platform & Access

**Platform:** Confluence (internal wiki) + Zendesk Help Center (customer-facing).

**Internal structure (Confluence):**
- `/KB/Getting Started` — Onboarding guides, platform overview, glossary.
- `/KB/Features` — Feature documentation, use cases, tutorials.
- `/KB/Troubleshooting` — Common issues, error codes, resolution steps.
- `/KB/API Reference` — API documentation, code samples, SDKs.
- `/KB/Compliance` — GDPR, HIPAA, SOC 2, security certifications.

**Customer-facing KB (Zendesk Help Center):**
- Public portal (no login required) for frequently asked questions.
- Category structure mirrors Confluence organization.
- Article search available; auto-suggested on support portal.

---

## 3. Article Standards & Templates

### 3.1 Mandatory Article Metadata

Every KB article must include:

```yaml
Title:             [Specific, searchable]
Doc ID:            kb-[kebab-slug]
Author:            [Team / Person]
Last Updated:      YYYY-MM-DD
Status:            active | deprecated | archived
Audience:          [Customer / Admin / Developer]
Search Keywords:   [5–10 tags for discoverability]
Related Articles:  [List of related KB IDs]
Reviewed By:       [Approver: Support Manager / VP Support]
```

### 3.2 Article Structure (Template)

**Standard format for how-to and troubleshooting articles:**

```markdown
# [Article Title]

## Overview
[1–2 sentences describing what this article covers and who should read it]

## Prerequisites
[Requirements before following steps: role permissions, data format, etc.]

## Step-by-Step Guide
1. [First step]
2. [Second step, with screenshot if visual]
...

## Troubleshooting
[Common errors + solutions during this process]

### Error: "Connection Timeout"
**Cause:** Network timeout between Northwind Cloud and customer's data source.
**Solution:** [Steps to resolve]

## FAQ
**Q: Can I ...?**
A: [Answer with reference to related articles]

## Related Articles
- [Article 1]
- [Article 2]

---
Last updated: YYYY-MM-DD
Reviewed by: [Name, Title]
```

### 3.3 Writing Standards

**Clarity & tone:**
- Avoid jargon; define technical terms on first use.
- Use active voice ("Click the button" not "The button should be clicked").
- Address reader as "you"; use second person.
- Keep sentences short; aim for 8th-grade reading level.

**Screenshots & visuals:**
- Include screenshots for UI-based steps (hide sensitive data: blur API keys, customer names).
- Use numbered overlays (1️⃣, 2️⃣) to highlight click targets.
- Maintain consistent visual style (same font, size, color for annotations).

**Code samples:**
- Include complete, runnable examples when possible.
- Use syntax highlighting (Markdown code blocks with language identifier: ```python, ```bash).
- Test code samples before publishing (run them against staging environment).

**Completeness:**
- Article should answer 90% of reader questions without requiring support contact.
- Include "Next steps" or "What to do if this doesn't work" (escalation to support).

---

## 4. Content Ownership & Approval Process

### 4.1 Content Owner by Topic

| Topic | Owner | Approver |
|---|---|---|
| **Getting Started, onboarding** | CSM + Customer Success Manager | VP Customer Success |
| **Feature documentation** | Product Manager + Engineering | VP Product + VP Engineering |
| **Troubleshooting, error codes** | Support Manager | Support Manager |
| **API & developer docs** | Engineering | VP Engineering |
| **Compliance, security** | Chief Privacy Officer + VP Security | VP Security |

### 4.2 Article Creation & Approval Workflow

1. **Author drafts article** (Content Owner writes in Confluence).
2. **Internal review** (72-hour SLA): Approver checks for accuracy, clarity, completeness.
3. **Feedback rounds** (max 2): Author incorporates feedback; resubmits.
4. **Approval & publication:**
   - Approver marks "Reviewed"; article moved to "/KB/" in Confluence.
   - Article published to Zendesk Help Center within 1 business day.
5. **Scheduled review** (quarterly): Approver re-reads; updates "Last Updated" date if no changes needed, or schedules refresh.

### 4.3 Deprecation & Archival

**Deprecated articles** (feature removed, outdated process):
1. Update article header: `Status: deprecated; see [New Article] instead`.
2. Keep article in Zendesk for 6 months (SEO + customer references).
3. After 6 months: Move to "Archived" status in Confluence; remove from Zendesk public KB.
4. Link from new article to deprecated one (for customers on old versions).

**Archived articles:** Retained in Confluence for audit trail; not searchable in Help Center.

---

## 5. Discoverability & Search Optimization

### 5.1 Keyword Strategy

Articles tagged with 5–10 searchable keywords:
- **Primary keyword:** Main topic (e.g., "AWS data source setup").
- **Secondary keywords:** Variations (e.g., "AWS integration", "connect AWS account").
- **Problem keywords:** Common errors (e.g., "permission denied", "connection failed").
- **Alias keywords:** Synonyms (e.g., "integration" vs. "connector", "pipeline" vs. "job").

### 5.2 Search & Recommendations

**Zendesk Help Center:**
- Auto-suggest articles when customer searches or opens ticket.
- Relevance ranking based on keyword match + views + helpfulness rating.
- Analytics tracked: searches performed, articles clicked, CSAT on article (helpful/not helpful).

**Internal Confluence:**
- Search accessible to support team + CSMs.
- Confluence macro embeds KB articles in support ticket responses (e.g., agent pastes link + article excerpt).

---

## 6. Technical Accuracy & Testing

### 6.1 Product Integration Testing

Before publishing, articles must be validated against:
1. **Staging environment:** Reproduce steps in staging to ensure accuracy.
2. **Multiple customer environments:** Test with different AWS regions, data source types (if applicable).
3. **Permission levels:** Test both admin and end-user access scenarios.
4. **Version compatibility:** Note if article applies only to specific Northwind Cloud versions (e.g., "Available in version 2.5+").

### 6.2 Error Code Documentation

**Every error code** referenced in KB must have:
1. **Error message (verbatim):** Exact text customer sees.
2. **Root causes:** Why does this error occur? (3–5 common causes listed).
3. **Resolution steps:** How to fix it? (In priority order: most likely cause first).
4. **Escalation criteria:** When to contact support (e.g., "If error persists after step 4, open a support ticket").

**Example:**

```markdown
### Error Code: NC-5042

**Error Message:** "Authentication Failed: Invalid API Key"

**Root Causes:**
1. API key has been revoked or expired.
2. API key is for a different Northwind Cloud account.
3. API key is missing from request header.

**Resolution:**
1. [Step to verify API key in account settings]
2. [Step to generate new API key if expired]
3. [Step to confirm correct account]
4. [Step to add API key to request header]

**Escalation:** If error persists, open ticket with: [Info customer should provide]
```

---

## 7. Quality Metrics & Review Cycle

### 7.1 Health Metrics (Tracked Monthly)

| Metric | Target | Owner | Action if Miss |
|---|---|---|---|
| **Article freshness** | ≥95% updated in last 12 months | Support Manager | Review + update articles >12 months old |
| **Article helpfulness** | ≥80% "Helpful" rating in Help Center | Content Owner | Revise low-rated articles |
| **Search coverage** | ≥90% of support issues have related KB article | Support Manager + PM | Create articles for high-volume issue categories |
| **Broken links** | <1% of internal/external links broken | Documentation team | Monthly link audit; fix broken links |
| **Completeness** | ≥90% of articles have screenshots/examples | Content Owner | Add visuals to text-only articles |

### 7.2 Quarterly Content Audit

**Support Manager reviews:**
1. **Top 10 most-viewed articles:** Are they still accurate? Updated recently?
2. **Low-traffic articles:** Are they discoverable? Delete if obsolete?
3. **Common support issues:** Do corresponding KB articles exist? If not, create.
4. **Outdated references:** Remove links to deprecated features.

**Output:** Roadmap for new/refresh articles; assigned to Content Owners.

---

## 8. Integration with Support Workflow

### 8.1 Support Agent Best Practices

Support agents use KB articles to:
1. **Resolve tickets faster:** Paste KB link + excerpt in first response.
2. **Escalate efficiently:** If KB article doesn't cover customer's issue, escalate to CSM or Engineering (not just ignore KB gap).
3. **Report gaps:** If common issue lacks KB article, notify Support Manager (logged in Slack #kb-gaps for priority).

### 8.2 Ticket Automation

Zendesk rules auto-insert KB article links based on ticket content:
- **Keywords matched:** If ticket contains "AWS connection", auto-suggest KB article on "AWS data source setup".
- **Issue categorization:** Support agent marks issue as Sev-4 (FAQ-style) → Zendesk auto-suggests FAQ articles before agent responds.

---

## 9. Compliance & Security

### 9.1 PII & Sensitive Data

KB articles **must never include:**
- Real customer names, account IDs, API keys, or credentials (use placeholders).
- Internal URLs, IP addresses, or infrastructure details.
- Examples of customer data (if demo needed, use synthetic/fake data).

**Approval:** Chief Privacy Officer reviews articles mentioning data handling, encryption, or compliance.

### 9.2 Version Control & Audit Trail

All KB articles tracked in Confluence version history:
- Author tracked for every edit.
- Change summary logged (e.g., "Updated screenshots for v2.5 UI").
- Approval comments visible; changes require Approver sign-off.

---

## 10. Knowledge Base Expansion Roadmap

**Annually, Support Manager + Product Manager plan KB growth:**
- Identify high-volume issue categories needing articles.
- Plan coverage for new features (launched in previous 12 months).
- Prioritize articles by: (support ticket volume + customer request + feature importance).

**Target:** 200+ customer-facing KB articles by 2027 (currently ~120).
