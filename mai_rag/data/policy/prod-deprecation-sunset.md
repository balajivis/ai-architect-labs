---
title: Feature Deprecation & Sunset Policy
doc_id: prod-deprecation-sunset
owner: Product Leadership
last_updated: 2026-06-09
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Feature Deprecation & Sunset Policy

## 1. Purpose

As Northwind evolves, older features are replaced with newer, better solutions. Rather than abruptly removing features, we follow a structured deprecation timeline that gives customers time to migrate while managing our technical debt.

**Goal**: Minimize customer impact while keeping codebase clean and maintainable.

## 2. Deprecation Levels

### 2.1 Level 1: Maintenance (No Deprecation)

Feature is still fully supported; all bugs fixed, documentation maintained.

- **Timeline**: Indefinite
- **Examples**: Core features like dashboard, reporting, user management

### 2.2 Level 2: Deprecated (Feature Still Works)

Feature works but will be removed. Customers must migrate to replacement.

- **Timeline**: 90–180 days
- **Support**: Bug fixes only; no new features
- **Communication**: Clear messaging on timeline and replacement

### 2.3 Level 3: Archived (Read-Only or Disabled)

Feature no longer accepts new operations; existing data readable only.

- **Timeline**: Final 30 days before removal
- **Use Case**: Data export or read-only access for historical reference
- **Support**: No support; not recommended for use

### 2.4 Level 4: Removed (Completely Gone)

Feature deleted entirely; no data access; code removed from product.

- **Timeline**: ≥180 days after initial deprecation announcement
- **Notification**: Proactive support outreach; data export windows provided
- **Support**: None; historical data available via support request if needed

## 3. Deprecation Timeline & Process

### 3.1 Announcement Phase (Day 1)

**Product Manager Actions**:

1. **Write Deprecation Notice** (1 page):
   - Feature name and what's changing
   - Why it's being deprecated (e.g., "Replaced by more powerful Report Builder"; "Low adoption, high maintenance cost")
   - **Migration Path**: Exact steps to switch to replacement feature (with screenshots/video if complex)
   - **Timeline**: Specific dates for each phase
   - **Support Resources**: Migration guide, webinar, documentation links

2. **Customer Communication** (Multi-channel):
   - **Email**: To all users with deprecation notice and migration guide
   - **In-App**: Banner on affected feature: "This feature will be removed on [DATE]. [Link: Migrate to Report Builder]"
   - **Blog**: "We're retiring X feature on [DATE]"
   - **Support**: Brief support team on migration steps; prepare canned responses

3. **Internal Communication**:
   - Update roadmap (mark old feature Level 2: Deprecated)
   - Notify Engineering (code maintenance limits)
   - Notify Sales (for customers asking why feature removed)

### 3.2 Support Phase (Days 2–150)

**Duration**: 90–150 days depending on complexity (see section 3.3).

**Product Team**:
- Monitor adoption of replacement feature
- Collect migration feedback; improve guide if needed
- Create FAQ: "Common migration questions"

**Support Team**:
- Answer migration questions
- Assist customers with migration (1:1 calls if needed)
- Escalate to Product if customers ask for feature to be retained

**Engineering**:
- No new features for deprecated feature
- Fix critical bugs only (P0/P1)
- Ignore enhancement requests

### 3.3 Deprecation Periods by Complexity

| Feature Type | Duration | Rationale |
|---|---|---|
| **Cosmetic only** (button color, layout) | 30–60 days | Low impact; easy migration |
| **Minor feature** (export format, display option) | 60–90 days | Some user workflows affected |
| **Core feature** (authentication method, API endpoint, data storage format) | 120–180 days | Major migration effort; high disruption risk |
| **Data Migration Required** | 180+ days | Allow time for data export, transformation, re-import |

### 3.4 Read-Only Phase (Days 151–180)

**For complex features, transition to read-only access**:

1. **Turn Off Write Operations**: Feature still loads; button to export data; cannot edit or add new records
2. **Clear Messaging**: "This feature is no longer accepting new data. To continue, migrate to [Replacement Feature]."
3. **Data Export**: One-click export of all data (CSV, JSON, or native format)
4. **Support**: Intensive support period; offer migration assistance calls

### 3.5 Removal Phase (Day 181+)

1. **Turn Off Feature**: Remove from UI; return 404 if accessed directly
2. **Code Cleanup**: Remove feature flag, backend code, database tables (in separate PR after confirmed customer data exported)
3. **Archive History**: Keep git history and deployment notes in case of recovery request
4. **Monitor Support**: Handle data recovery requests; document lessons learned

## 4. Replacement Feature Requirements

**Before deprecating a feature, replacement must be in place**:

- ✅ **Replacement functional**: New feature is stable and feature-complete relative to old feature
- ✅ **Migration documented**: Step-by-step migration guide with screenshots
- ✅ **Data migration tested**: If old feature has data, confirm data can be exported/imported to new feature
- ✅ **Performance equal or better**: New feature not slower than old feature
- ✅ **Accessibility equal or better**: New feature meets WCAG 2.1 AA (see *Accessibility Standard*)

**Prohibition**: Never deprecate a feature until replacement exists and is live.

## 5. Special Cases

### 5.1 API Deprecation

API endpoints follow strict deprecation rules:

**Timeline**:
- **Day 1**: Announce endpoint deprecation in API changelog; return HTTP 200 + `Deprecation: true` header
- **Day 91–120**: Return HTTP 200 + `Sunset: [removal-date]` header (RFC 8594)
- **Day 181**: Return HTTP 410 Gone for deprecated endpoint; direct to replacement

**Versioning**:
- Old endpoint stays available during support period (don't break immediately)
- New endpoint released alongside old; customers have 180 days to migrate
- Support both endpoints simultaneously for minimum 90 days

**Example**:

```
GET /api/v2/reports/:id                  (old, deprecated)
GET /api/v3/reports/:id                  (new, replacement)

Timeline:
- 2026-06-01: Announce `/v2` deprecated; `/v3` fully available
- 2026-09-01: Both endpoints work; migrate within 90 days
- 2026-12-01: `/v2` returns 410 Gone; only `/v3` available
```

### 5.2 Pricing/Plan Deprecation

If retiring a pricing tier:

**Timeline**: 180+ days (large financial impact)

**Communication**:
- Clear notice of plan retirement
- Migration path to replacement plan (e.g., "Starter plan → Professional plan at 20% discount for 1 year")
- Do NOT increase prices for customers migrating from deprecated plan

**Support**: Sales team assists with plan migration; offer proactive outreach to affected customers

### 5.3 Data Format Deprecation

If changing how data is stored/formatted:

**Timeline**: 180+ days (requires data migration)

**Process**:
1. **New format** deployed alongside old (dual-write)
2. **Read both**: App can read both old and new formats
3. **Migration window**: 90–180 days for customers to convert
4. **Data Export**: Provide one-click export in old format for customer archiving
5. **Removal**: Delete old format code after migration period

## 6. Documentation & Tracking

### 6.1 Deprecation Registry

Maintain a "Deprecation Registry" (Notion or wiki):

| Feature | Deprecated Date | Removal Date | Status | Migration Path |
|---------|-----------------|--------------|--------|-----------------|
| CSV Export v1 | 2026-06-01 | 2026-09-01 | Active | Use new unified export menu |
| Legacy API v2 | 2026-06-01 | 2026-12-01 | Active | Migrate to v3 (see docs) |
| Starter Plan | 2026-06-01 | 2026-12-01 | Active | Upgrade to Professional |

### 6.2 Deprecation Notice Template

Add to product, docs, and API responses:

```
🔔 DEPRECATION NOTICE

The [Feature Name] feature will be retired on [DATE].

Why? [Brief explanation: "Replaced by Report Builder"; "Low adoption"; "Security update"]

What to do:
1. [Step 1: How to migrate]
2. [Step 2: Verify migration]
3. [Step 3: Questions? Contact support]

Learn more: [Link to migration guide]
Timeline: 90 days to migrate
Questions? Email support@northwind.com
```

## 7. Customer Objections & Escalations

### 7.1 "Don't Remove This Feature; I Need It"

**Response Process**:

1. **Support**: Document customer request; ask why they need old feature
2. **Product**: Review if replacement truly meets their need; if gap exists, consider extending deprecation or enhancing replacement
3. **Decision**:
   - **Gap in replacement**: Extend deprecation 30 days; add gap-filling feature to replacement
   - **Customer is only user**: Extend deprecation 60 days; provide transition assistance
   - **Strategic value**: Reverse deprecation (rare); document decision and communicate to other customers

### 7.2 "This Will Break Our Workflow"

**Response**:

- Offer migration assistance call (1:1 support)
- Provide custom data export/transformation if needed
- Consider temporary "read-only" access if customer needs time
- Offer 1-month extension if legitimate hardship

### 7.3 "You're Removing This to Force Customers to Upgrade"

**Prevention**:

- Communicate deprecation 90+ days in advance
- Ensure replacement feature is better, not just "paid-only"
- Don't hide deprecation in release notes; make it prominent
- Never deprecate old feature before replacement is live and equal or better

## 8. Post-Removal Checklist

After feature fully removed:

- [ ] Code deleted from main branch (in separate cleanup PR)
- [ ] Database tables archived or deleted
- [ ] Feature flags removed (see *Feature Flagging Standard*)
- [ ] Documentation updated (mark as "archived/historical")
- [ ] Support documentation updated
- [ ] Monitoring/analytics removed
- [ ] API/SDK updated to remove endpoints
- [ ] Historical data export provided to customers who request it
- [ ] Lessons learned documented (what went well, what to improve next time)

## 9. Metrics & Success Criteria

Track deprecation success:

| Metric | Target | Owner |
|--------|--------|-------|
| **Migration Rate** | ≥90% of users migrated to replacement by removal date | Product PM |
| **Support Load** | <10 migration-related support tickets (for standard deprecation) | Support team |
| **Customer Satisfaction** | NPS impact <3 points for users affected | VP Product |
| **Code Cleanup** | 100% of old code removed within 30 days of removal date | Engineering |

