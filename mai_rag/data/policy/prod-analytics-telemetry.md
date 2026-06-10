---
title: Product Analytics & Telemetry Standard
doc_id: prod-analytics-telemetry
owner: Analytics & Engineering
last_updated: 2026-06-09
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Product Analytics & Telemetry Standard

## 1. Purpose

Product Analytics captures how users interact with Northwind Cloud. These insights inform roadmap decisions, identify feature adoption issues, and detect technical problems. All events must follow this standard to ensure data quality and consistent interpretation.

**Scope**: Customer-facing product telemetry (web app, mobile app, API). Internal admin panels excluded.

## 2. Event Taxonomy

### 2.1 Event Categories

All events fall into one of four categories:

| Category | Purpose | Examples | Owner |
|----------|---------|----------|-------|
| **Page View** | Track navigation | `page_dashboard_viewed`, `page_settings_viewed` | Product team |
| **User Action** | Track feature usage | `button_export_clicked`, `form_saved` | Product team |
| **System Event** | Track errors / performance | `api_error_occurred`, `page_load_slow` | Engineering team |
| **Business Event** | Track revenue impact | `subscription_purchased`, `trial_ended` | Product + Finance teams |

### 2.2 Event Naming Convention

Event names follow pattern: `[category]_[feature]_[action]` in snake_case.

**Examples**:
- ✅ `page_reports_viewed`
- ✅ `button_export_pdf_clicked`
- ✅ `form_credentials_submitted`
- ✅ `api_request_timeout`
- ✅ `subscription_annual_purchased`

**Naming Rules**:
- Lowercase with underscores; no hyphens or CamelCase
- Max 50 characters
- Verb last (action-oriented): "clicked", "viewed", "submitted", "failed"
- Avoid acronyms; use full words
- Never use internal database IDs in event name (e.g., ❌ `user_123_clicked` → ✅ `button_export_clicked`)

## 3. Event Properties (Attributes)

Every event includes standard properties plus optional context-specific properties:

### 3.1 Standard Properties (Required)

```json
{
  "event_id": "evt_550e8400-e29b-41d4-a716-446655440000",
  "event_name": "button_export_clicked",
  "timestamp": "2026-06-09T14:23:45.123Z",
  "user_id": "user_abc123",
  "org_id": "org_xyz789",
  "session_id": "session_def456",
  "app_version": "24.06.0"
}
```

### 3.2 Context Properties (Varies by Event)

For `button_export_clicked`:

```json
{
  "feature": "reports",
  "export_format": "pdf",
  "report_size_rows": 1500,
  "is_custom_report": true,
  "user_plan": "Professional"
}
```

**Guidelines**:
- Include only data relevant to the event (don't bloat with irrelevant context)
- Classify PII: Do NOT include `email`, `phone`, or `home_address` in event properties
- Use enums for categorical properties (e.g., `user_plan`: "Free" | "Professional" | "Enterprise", not free text)
- Round large numbers (e.g., `report_size_rows`: round to nearest 100 for privacy)

## 4. Implementation: Tracking Code

### 4.1 Web App (React)

```typescript
// hooks/useAnalytics.ts
import { analytics } from '@northwind/analytics-sdk';

export function useAnalytics() {
  return {
    track: (eventName: string, properties?: Record<string, unknown>) => {
      analytics.track(eventName, properties);
    },
  };
}

// components/ExportButton.tsx
export function ExportButton({ report }) {
  const { track } = useAnalytics();

  const handleExportClick = (format: 'pdf' | 'csv') => {
    track('button_export_clicked', {
      feature: 'reports',
      export_format: format,
      report_size_rows: report.rows.length,
      user_plan: currentUser.plan,
    });
    // Trigger export logic...
  };

  return <button onClick={() => handleExportClick('pdf')}>Export as PDF</button>;
}
```

### 4.2 Backend Events (Node.js)

```typescript
// services/reportService.ts
import { analytics } from '@northwind/analytics-sdk';

export async function generateReport(userId: string, reportId: string) {
  const startTime = Date.now();
  
  try {
    const report = await db.reports.findById(reportId);
    const result = await computeReport(report);
    
    const duration = Date.now() - startTime;
    
    analytics.track('api_report_generated', {
      feature: 'reports',
      report_type: report.type,
      duration_ms: duration,
      row_count: result.rows.length,
      user_id: userId,
    });
    
    return result;
  } catch (error) {
    analytics.track('api_report_failed', {
      feature: 'reports',
      error_code: error.code,
      error_message: error.message.substring(0, 100), // Truncate for privacy
      duration_ms: Date.now() - startTime,
      user_id: userId,
    });
    throw error;
  }
}
```

### 4.3 Feature Flag Events

When a feature flag is toggled, automatically log:

```json
{
  "event_name": "feature_flag_toggled",
  "feature_flag": "feature_reports_export_pdf",
  "flag_enabled": true,
  "rollout_percentage": 50,
  "timestamp": "2026-06-09T14:23:45.123Z"
}
```

## 5. Data Quality Standards

### 5.1 Event Validation

Before shipping code with analytics:

- ✅ Event name follows naming convention
- ✅ All required properties present (event_id, timestamp, user_id, org_id)
- ✅ No PII (email, phone, SSN, home address) in event properties
- ✅ Categorical properties use enums (not free text)
- ✅ Sampling strategy defined for high-volume events (see 5.2 below)
- ✅ Privacy review completed (see *Data Classification & Retention Policy*)

### 5.2 Sampling for High-Volume Events

High-volume events (>100K/day) may cause cost or performance issues. Implement sampling:

```typescript
// Example: Sample 10% of page_view events
function shouldTrackEvent(eventName: string): boolean {
  if (eventName === 'page_view') {
    return Math.random() < 0.10; // Track 10%
  }
  return true; // Track 100% of other events
}
```

**Sampling Rules**:
- Document sample rate in event definition (e.g., "10% sampling")
- Use consistent user-based sampling (same user always sampled or never sampled)
- Never sample business-critical events (purchases, errors, conversions)

## 6. Event Instrumentation Checklist

Before launching a new feature:

| Event Type | Events Required | Examples |
|-----------|-----------------|----------|
| **Feature** | Activation + completion | `page_X_viewed`, `form_X_submitted` |
| **Form** | Submit + error | `form_export_submitted`, `form_export_failed` |
| **Button** | Click + success/failure | `button_export_clicked`, `export_failed` |
| **API** | Request + response | `api_report_requested`, `api_report_timeout` |
| **Navigation** | Page views | `page_reports_viewed` |

## 7. Accessing Analytics Data

### 7.1 Tools & Dashboards

| Tool | Access | Use Case |
|------|--------|----------|
| **Datadog Events** | All employees | Real-time raw events; debugging |
| **Amplitude** (future) | Product + Analytics | User cohorts, retention, funnel analysis |
| **Looker Studio** (future) | Executive dashboard | KPI dashboards, executive reporting |
| **Mixpanel** (legacy) | Deprecated 2026-05 | Do not use; migrate queries to Datadog |

### 7.2 Creating Dashboards

For each new feature, create a dashboard tracking:

- **Adoption**: % of eligible users activating feature
- **Engagement**: % returning 2+ times; avg events/user/week
- **Conversion**: % completing intended workflow
- **Error Rate**: % of attempts resulting in error
- **Performance**: P95 latency, timeout rate

**Lifecycle**:
- Week 1 (launch): Update daily
- Weeks 2–4: Update 2x/week
- Month 2+: Update weekly; archive if metric stabilizes

## 8. Privacy & Data Retention

See *Data Classification & Retention Policy* for full details. Summary:

- **PII**: Never track email, phone, SSN, home address in analytics
- **Sensitive**: User behavior data is Confidential; access limited to product/analytics teams
- **Retention**: Keep raw events for 90 days; aggregate (cohorts, funnels) for 2 years
- **Deletion**: User can request "right to be forgotten"; delete all their events

## 9. Coordination with Experimentation

Feature flag + experiment setup includes automatic event logging:

```yaml
experiment_id: "exp-export-redesign-001"
flag_name: feature_reports_export_pdf
assigned_group: "control" | "treatment"

# Automatic event logged on assignment
{
  "event_name": "experiment_assigned",
  "experiment_id": "exp-export-redesign-001",
  "assigned_group": "treatment",
  "timestamp": "2026-06-01T10:00:00.000Z"
}
```

This allows analytics to automatically segment metrics by experiment cohort (see *Experimentation & A/B Testing Policy*).

## 10. Product Analytics Metrics (Quarterly)

Track data quality:

| Metric | Target |
|--------|--------|
| **Event Coverage** | All customer-facing features instrumented (100%) |
| **Data Quality Score** | % events with all required properties (target: ≥98%) |
| **Dashboard Freshness** | All dashboards updated in last 7 days (100%) |
| **PII Incidents** | Zero events containing PII (0/quarter) |
| **Latency** | Event tracking <100ms added to page load time |

## 11. Distractor: Product Analytics vs. Data Team Telemetry

⚠️ **Careful**: "Product Analytics" (this doc) and "Data Team Infrastructure Telemetry" (*Data Classification & Retention Policy*) are different systems:

| Aspect | Product Analytics | Data Telemetry |
|--------|------------------|-----------------|
| **What** | User interaction events | System health, infrastructure metrics |
| **Who owns** | Product team | Data/Engineering team |
| **Tools** | Datadog, Amplitude | Datadog, Prometheus |
| **Data lifetime** | 90 days raw, 2 years aggregated | Varies by metric type |
| **PII** | Forbidden | Should not collect |
| **Typical events** | `button_clicked`, `page_viewed` | `cpu_usage`, `disk_free`, `api_latency` |

**Don't confuse the two.** If you're tracking "how many API calls did the user make," that's Product Analytics. If you're tracking "what is the API gateway's latency," that's Data Telemetry.

