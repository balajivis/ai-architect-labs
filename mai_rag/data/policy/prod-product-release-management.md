---
title: Product Release Management
doc_id: prod-product-release-management
owner: Product Leadership & Engineering
last_updated: 2026-06-09
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Product Release Management

## 1. Purpose

Product Release Management defines how features transition from development to production and how we communicate changes to customers. This process ensures coordinated deployment, clear messaging, and measurable impact tracking.

## 2. Release Types

### 2.1 Standard Release

- **Frequency**: Bi-weekly (every 2 weeks on Wednesday at 10 AM PT)
- **Content**: Accumulated features, bug fixes, and improvements from the prior 2-week sprint
- **Duration**: 2–4 weeks of development + 1 week validation
- **Risk Level**: Medium (multiple features, but tested together in staging)
- **Example**: "v24.06 Release: PDF Export, Improved Search, Bug Fixes"

### 2.2 Hotfix Release

- **Frequency**: As-needed
- **Content**: Critical bug fix or security patch
- **Duration**: 1–2 days (code → staging → production)
- **Risk Level**: Low (single fix, narrow scope)
- **Requires**: VP Engineering approval before production deployment
- **Example**: "Hotfix: Security patch for customer export API"

### 2.3 Major Release

- **Frequency**: Quarterly (e.g., v24.Q1, v24.Q2)
- **Content**: Significant new capabilities, architectural changes, or visual redesigns
- **Duration**: 8+ weeks of development + 2 weeks validation
- **Risk Level**: High (customers may need migration time or new training)
- **Requires**: CEO & VP Product approval; customer communication plan
- **Example**: "v24.Q2: New Report Builder, Dashboard Redesign, API v3"

## 3. Release Workflow

### 3.1 Planning Phase (Weeks 1–2 before release)

| Responsibility | Task | Deadline |
|---|---|---|
| **Product Manager** | Finalize feature list; identify breaking changes or data migrations | Week -2, Tuesday |
| **Engineering Lead** | Validate all features complete staging validation per *Production Deployment Runbook*; confirm no known blockers | Week -2, Wednesday |
| **Design Lead** | Confirm all design work complete; no design debt carried into release | Week -2, Wednesday |
| **Marketing** | Draft release announcement, customer communication, and help articles | Week -1, Friday |
| **VP Product** | Approve final feature list and go/no-go criteria | Week -1, Friday |

### 3.2 Release Preparation (Week before release)

1. **Release Notes**: Product Manager compiles final release notes with:
   - Feature summaries (2–3 sentences each, customer-friendly language)
   - Bug fixes (list and link to customer-impacting issues)
   - Breaking changes or deprecations (prominent warning)
   - Known limitations or deferred items
   - Thank you to customers who requested top features

2. **Customer Communication**:
   - Email announcement to all users (72 hours before release)
   - In-app notification (24 hours before release, if applicable)
   - Support playbook for common questions
   - Help articles or video walkthroughs for major features

3. **Deployment Plan**:
   - Schedule deployment window (e.g., "Wednesday 10 AM – 1 PM PT")
   - Identify rollback procedure (see *Feature Flagging Standard*)
   - Assign deployment lead and on-call engineer
   - Plan gradual rollout: Phase 0 (10%) → Phase 1 (50%) → Phase 2 (100%)

4. **Feature Flag Verification**:
   - All new features are behind feature flags set to OFF in production
   - Rollout percentages determined for each feature (see *Feature Flagging Standard*)
   - Flags named consistently (see *Feature Flagging Standard* naming convention)

5. **Success Criteria**:
   - All automated tests pass in CI/CD
   - No P0 or P1 bugs in staging
   - Zero customer data migrations required (or migration tested and approved)
   - Support team briefed on new features
   - Monitoring dashboards in Datadog ready (see *Product Analytics & Telemetry Standard*)

### 3.3 Release Day (Wednesday, 10 AM PT)

1. **Pre-Release (30 min before)**:
   - Deployment lead confirms: all code merged, no hot fixes in flight, team ready
   - On-call engineer confirms: Datadog dashboards active, PagerDuty ready, communication channels open

2. **Deployment (Phase 0: 10% internal)**:
   - Deploy code to production (see *Production Deployment Runbook* Phase 5)
   - Enable feature flags for internal employees (Northwind staff + QA)
   - Monitor for 30 minutes: error rate, latency, critical logs
   - If issues, deployment lead decides: continue to Phase 1 or rollback

3. **Phase 1 (50% of users)**:
   - Enable feature flags for 50% of general users (via percentage rollout)
   - Monitor for 2–4 hours: error rate, adoption, support tickets
   - If critical issue: rollback immediately (toggle feature flag OFF)
   - Otherwise, proceed to Phase 2

4. **Phase 2 (100% of users)**:
   - Enable feature flags for remaining 50% of users
   - Monitor for 24 hours: all metrics
   - If stable, leave flags ON; schedule flag cleanup for 30 days later (see *Feature Flagging Standard*)

5. **Customer Communication**:
   - Send release announcement email (if not sent pre-release)
   - Publish release notes on website
   - Share announcement in community forums or Slack

### 3.4 Post-Release (Days 1–7)

1. **Metric Tracking**:
   - Product team monitors success metrics (adoption, engagement, support tickets)
   - Daily standup for first 3 days to discuss any issues
   - Weekly review of feature adoption and user feedback

2. **Issue Response**:
   - P1 bugs: Fixed and deployed same day (hotfix)
   - P2 bugs: Prioritized for next release
   - Feature requests: Logged and reviewed in next roadmap planning cycle

3. **Documentation & Training**:
   - Publish "Getting Started" guide for major features
   - Record short video tutorials (2–5 min each)
   - Update help center and FAQs

## 4. Release Versioning

Northwind uses **calendar versioning**: `YYYY.MM.Minor`

- `24.06.0` — June 2024 major release
- `24.06.1` — June 2024 hotfix #1
- `24.06.2` — June 2024 hotfix #2

**Deployment Events**: Each version is tagged in GitHub; deployment timestamp recorded in Datadog. Customer can always see their current version in account settings.

## 5. Breaking Changes & Deprecations

Breaking changes (changes requiring customer action or migration) must be:

1. **Announced** 90 days before removal via email + in-app notification
2. **Documented** in release notes with migration instructions
3. **Supported** by help articles and optional support calls
4. **Deprecated** per *Feature Deprecation & Sunset Policy* 60 days before removal
5. **Removed** only after 90-day notification period

**Example Timeline** for removing legacy API endpoint:
- **Day 0**: Announce sunset in release notes; email customers
- **Day 60**: Mark API as "deprecated" in documentation; return HTTP 200 + deprecation warning header
- **Day 75**: Final support calls and migration assistance
- **Day 90**: Remove endpoint; return HTTP 404; log incident with details for support team

## 6. Release Governance

| Release Type | Approval Required | Approval SLA |
|---|---|---|
| **Standard Release** | VP Product + VP Engineering | 24h before scheduled release |
| **Hotfix** | VP Engineering | 1h before deployment |
| **Major Release** | CEO + VP Product + VP Engineering | 1 week before scheduled release |

## 7. Rollback Criteria

Immediate rollback if:

- Error rate spikes >1% for >5 minutes
- Core customer workflows are broken (login, payments, data export)
- Database migrations partially completed and breaking production
- Security vulnerability discovered in new code

Rollback procedure:
1. Deployment lead toggles feature flags OFF for problematic features
2. If flag toggle doesn't resolve, execute code rollback (previous stable commit) via *Production Deployment Runbook*
3. Alert VP Product, VP Engineering, VP Security; begin incident response per *Incident Response Runbook*

## 8. Release Documentation

For each release, maintain:

- **Release Notes**: Customer-friendly summary (public, shared via email + website)
- **Deployment Ticket**: Jira/GitHub issue tracking deployment tasks and status
- **Changelog**: Machine-readable list in YAML or JSON format (for API documentation)
- **Post-Launch Retrospective**: Document what went well, what to improve (captured 5 days post-release)

