---
title: Feature Flagging Standard
doc_id: prod-feature-flagging
owner: Engineering Leadership
last_updated: 2026-06-09
status: active
classification: internal
supersedes: ""
supersedes_by: ""
---

# Feature Flagging Standard

## 1. Purpose

Feature flags enable safe, gradual rollout of code changes to production without redeployment. All Production deployments risk introducing bugs or performance regressions. Feature flags decouple code deployment from feature activation, allowing us to:

- Deploy code to production while feature is OFF (safe testing)
- Enable feature for internal employees first (dogfooding)
- Gradually roll out to customers (10% → 25% → 50% → 100%)
- Disable feature instantly if issues discovered (no rollback needed)
- A/B test feature variants (see *Experimentation & A/B Testing Policy*)

## 2. Mandatory Scenarios

Feature flags are REQUIRED for:

1. **All user-facing features** (web UI, API responses affecting customers)
2. **Changes to critical APIs** (authentication, payments, data export)
3. **Database schema changes** (new tables, columns, indexes)
4. **Third-party service integrations** (new API, new SaaS tool)
5. **Performance-sensitive code** (caching, indexing, batch processing)
6. **A/B tests and experiments** (see *Experimentation & A/B Testing Policy*)

Feature flags are OPTIONAL for:

- Internal tooling or admin panels (lower risk)
- Bug fixes that do not change API contracts
- Cosmetic UI improvements
- Documentation or comment changes

## 3. Naming Convention

Feature flag names follow the pattern: `feature_<product>_<feature_name>_<variant>` in kebab-case.

**Examples**:
- `feature_reports_export_pdf` — Enable PDF export in reports feature
- `feature_reports_export_pdf_v2` — V2 variant (use for A/B testing)
- `feature_api_customer_lookup_enhanced` — Enhanced customer lookup in API

**Naming Rules**:
- Lowercase with underscores
- Max 50 characters
- Avoid acronyms; use full words
- Always start with `feature_` for consistency
- Append `_v2`, `_v3` for variants, never `_old` or `_new`

## 4. Implementation Pattern

### 4.1 Backend Feature Flags (Node.js / Python example)

```javascript
// lib/flags.ts
import { featureFlag } from '@northwind/feature-flagging-sdk';

export async function isFeatureEnabled(
  flagName: string,
  userId: string,
  context?: { orgId?: string; plan?: string }
): Promise<boolean> {
  return featureFlag.isEnabled(flagName, { userId, ...context });
}

// Inside handler/service
const pdfExportEnabled = await isFeatureEnabled(
  'feature_reports_export_pdf',
  userId,
  { orgId, plan: user.plan }
);

if (pdfExportEnabled) {
  // New PDF export logic
  return generatePDFReport(report);
} else {
  // Fallback to existing behavior
  return generateCSVReport(report);
}
```

### 4.2 Frontend Feature Flags (React example)

```typescript
// hooks/useFeatureFlag.ts
import { useFeatureFlag } from '@northwind/feature-flagging-sdk';

export function ExportButton({ reportId }) {
  const pdfExportEnabled = useFeatureFlag('feature_reports_export_pdf');

  return (
    <>
      <button onClick={() => exportAsCSV(reportId)}>Export CSV</button>
      {pdfExportEnabled && (
        <button onClick={() => exportAsPDF(reportId)}>Export PDF</button>
      )}
    </>
  );
}
```

### 4.3 Database Migrations with Flags

When adding a new table or column:

1. **Deploy code** with feature flag OFF; code path ignores new column
2. **Migrate schema** in non-blocking fashion (run migration, code doesn't read/write yet)
3. **Enable feature flag** for 10% of users after 24h soak
4. **Monitor** for 48h before expanding rollout
5. **After 90 days**: Remove feature flag and old code path

## 5. Rollout Strategy

### 5.1 Standard Phased Rollout (7–10 days)

For medium-risk features:

| Phase | Audience | Duration | Go/No-Go Decision |
|-------|----------|----------|-------------------|
| **Phase 0** | Internal employees + QA | 24–48h | Error rate <0.1%; no P0 bugs |
| **Phase 1** | 10% of general users | 48h | Error rate <0.5%; adoption >5% |
| **Phase 2** | 25% of general users | 48h | Error rate <0.5%; engagement stable |
| **Phase 3** | 50% of general users | 2–3 days | Error rate <0.5%; support tickets <10 |
| **Phase 4** | 100% of general users | — | Feature fully live; remove flag after 30 days |

### 5.2 Rapid Rollout (24–48h)

For low-risk bug fixes or internal tools:

| Phase | Audience | Duration |
|-------|----------|----------|
| **Phase 0** | Internal employees | 2–4h |
| **Phase 1** | 50% of users | 12h |
| **Phase 2** | 100% of users | — |

### 5.3 Canary Rollout (5% initial)

For high-risk features (database changes, payment flows):

| Phase | Audience | Duration | Decision |
|-------|----------|----------|----------|
| **Phase 0** | Internal QA | 48h | Error rate <0.05%; zero financial discrepancies |
| **Phase 1** | 5% (early adopter customers only) | 72h | Error rate <0.1%; <5 support tickets |
| **Phase 2** | 25% | 3–5 days | Error rate <0.5%; engagement/revenue on track |
| **Phase 3** | 100% | — | Feature stable; remove flag after 60 days |

## 6. Targeting Rules

Feature flags support targeting by:

- **User ID** (specific users)
- **Organization / Plan** (e.g., "only Enterprise customers")
- **Geography** (e.g., "only EU users" for GDPR compliance)
- **Percentage rollout** (e.g., "10% of all users, consistently bucketed")
- **Custom attributes** (e.g., `user.created_at < 2024-01-01`)

**Example targeting rule**:
```
feature_reports_export_pdf = enabled
  IF (user.id IN [123, 456, 789])  // Specific users
  OR (org.plan == 'Enterprise')     // All Enterprise orgs
  OR (percentage_rollout == 10%)    // 10% of everyone else
```

## 7. Monitoring During Rollout

For each phase, monitor these metrics via Datadog (see *Product Analytics & Telemetry Standard*):

- **Error Rate**: Track API errors and 5xx responses; trigger rollback if >0.5%
- **Latency**: P95 and P99 request latency; alert if increase >10%
- **Adoption**: % of eligible users activating new feature
- **Engagement**: Users returning to feature; target >50% in first 48h
- **Support Tickets**: Segment by feature flag; alert if spike >5x normal
- **Business Metrics**: Revenue, conversion rate, churn (for revenue-impacting features)

**Automated Rollback**:
If error rate exceeds 1% for >5 minutes, automated monitoring disables the feature flag and creates a P1 incident (see *Incident Response Runbook*).

## 8. Flag Lifecycle & Cleanup

### 8.1 Timeline

- **Days 1–7**: Feature in active rollout
- **Days 8–30**: Feature enabled for 100%; monitor metrics
- **Days 31–60**: Evaluate full shutdown vs. permanent feature
- **Day 61+**: If stable, remove flag and old code path; if unstable, revert feature and begin redesign

### 8.2 Removal Process

1. **Confirm Stable**: No new bugs in 14 days; metrics confirm success
2. **Remove Flag Code**: Delete all conditional paths; keep only new implementation
3. **Deploy & Verify**: Deploy to staging, run full test suite, deploy to production (see *Production Deployment Runbook*)
4. **Document**: Close Jira ticket and add cleanup task to PDLC documentation

**Never**:
- Leave feature flag in code indefinitely (legacy technical debt)
- Rename flags; create new flags instead and deprecate old names
- Share flag configuration across unrelated features

## 9. Coordination with Feature Deprecation

When retiring an old feature in favor of a new one:

1. **Old Feature**: Wrap in feature flag `feature_<product>_<old>_deprecate` set to ON
2. **New Feature**: Wrap in feature flag `feature_<product>_<new>_launch` set to OFF
3. **Rollout**: Gradually disable old feature while enabling new feature in parallel
4. **Sunset**: After 30–90 days (per *Feature Deprecation & Sunset Policy*), remove old code path entirely

