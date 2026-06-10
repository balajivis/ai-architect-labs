---
title: Experimentation & A/B Testing Policy
doc_id: prod-experimentation-ab-testing
owner: Product Leadership & Analytics
last_updated: 2026-06-09
status: active
classification: internal
supersedes: ""
supersposed_by: ""
---

# Experimentation & A/B Testing Policy

## 1. Purpose

A/B Testing (also called multivariate testing) allows us to measure the impact of product changes on user behavior and business metrics. Rather than debating which version is "better," we run controlled experiments and let data decide.

**Philosophy**: Hypothesis-driven, data-validated decisions reduce risk and improve product outcomes.

## 2. Experimentation Framework

### 2.1 When to Run an Experiment

**MUST run experiment** for:
- New features where we're uncertain about impact (e.g., "Will users notice this feature?")
- Changes to monetization or conversion flows (e.g., new pricing tier, new checkout flow)
- Messaging or positioning changes (e.g., "Does this help text improve task completion?")
- High-traffic pages (sample sizes sufficient for statistical significance in 1–2 weeks)

**MAY run experiment** for:
- Minor UX improvements (if confidence is low)
- Copywriting changes (subject lines, button text)
- Visual polish (button colors, spacing)

**NO experiment needed** for:
- Bug fixes (just deploy; monitor metrics)
- Low-traffic features (insufficient traffic for statistical significance)
- Internal-only changes (admin panels, internal tools)

### 2.2 Hypothesis Formulation

Every experiment starts with a **hypothesis statement**:

**Format**: "If we [change X], then [metric Y] will [improve/decrease] by Z%, because [reason]."

**Examples**:

- ✅ "If we add a help tooltip to the export button, then task completion time will decrease by 10%, because users are missing the button location."
- ✅ "If we change checkout button color from gray to green, then conversion rate will increase by 5%, because green signals success and action."
- ❌ "People will like the new design better" (too vague; not measurable)
- ❌ "The new feature is better" (doesn't predict metric impact)

### 2.3 Experimental Design

Before launching experiment:

1. **Control Group**: Existing behavior (status quo)
2. **Treatment Group**: New behavior (variant being tested)
3. **Sample Size**: Calculate using power analysis (90% power, 5% significance level)
4. **Duration**: Run until sample size reached or 2 weeks elapsed, whichever comes first
5. **Success Metric**: Primary metric measuring hypothesis (e.g., conversion rate, task completion, engagement)
6. **Secondary Metrics**: Guard rails to catch negative effects (e.g., error rate, support tickets)

**Example**:

```
Hypothesis: Adding a confirmation dialog before account deletion will 
reduce accidental deletions and decrease support tickets.

Control Group:        Existing "Delete Account" button (no confirmation)
Treatment Group:      New "Delete Account" button + confirmation dialog
Sample Size:          1,000 users per group (2,000 total)
Duration:             2 weeks or until target reached
Success Metric:       % of users clicking "Delete Account" button
Secondary Metrics:    Support tickets, cancellation rate, NPS (no negative regression)
```

## 3. Experimentation Workflow

### 3.1 Planning Phase (Before Experiment Launch)

| Responsibility | Task | Deadline |
|---|---|---|
| **Product Manager** | Write hypothesis and experimental design; identify success metrics | Week -1, Monday |
| **Analytics Engineer** | Validate sample size calculation; confirm metric instrumentation ready | Week -1, Tuesday |
| **Engineering Lead** | Estimate implementation effort; confirm feature flag setup (see *Feature Flagging Standard*) | Week -1, Tuesday |
| **Data Analyst** | Create experiment dashboard in Datadog showing control vs. treatment metrics | Week -1, Friday |

### 3.2 Execution Phase (During Experiment)

**Launch**:
1. Deploy treatment via feature flag set to OFF
2. Enable treatment for 50% of users (randomized, consistent per user)
3. Leave control group at 50% (serve old behavior)
4. Confirm both groups have equal traffic (balanced)

**Monitoring** (Daily for first 5 days, then every 2 days):
- Success metric trending toward hypothesis (e.g., conversion rate higher in treatment)?
- Secondary metrics stable (error rate, support tickets)?
- Sample size accumulating normally (no traffic anomalies)?
- Any technical issues in treatment group?

**Early Stopping Rules**:
- If treatment shows **3+ sigma improvement** in success metric after 1 week, stop early and declare winner (statistically significant)
- If treatment shows **3+ sigma degradation** in secondary metric, stop immediately and disable treatment group

### 3.3 Analysis & Decision Phase (After Experiment Completes)

1. **Calculate Results**:
   - Primary metric: Control = 12%, Treatment = 14.1%, Difference = +2.1%
   - Statistical significance: p-value = 0.032 (< 0.05, statistically significant)
   - Confidence interval: Treatment conversion is 12.8% – 15.4% with 95% confidence
   - Secondary metrics: No regression (error rate, support tickets unchanged)

2. **Decision**:
   - **Winner**: Treatment outperforms control with p < 0.05; implement globally
   - **Inconclusive**: No significant difference; declare a tie (no change required)
   - **Loser**: Treatment underperforms control; discard treatment

3. **Recommendation**:
   - ✅ **Implement**: Roll out treatment to 100% of users (see *Feature Flagging Standard*)
   - ❌ **Discard**: Keep control; explore different hypothesis for next experiment
   - ⚠️ **Iterate**: Treatment showed promise (p = 0.08) but not significant; run again with larger sample size

### 3.4 Post-Experiment (Rollout & Documentation)

1. **Rollout**: If treatment wins, gradually increase feature flag to 100% (see *Product Release Management*)
2. **Documentation**: Write 1-page summary:
   - Hypothesis
   - Results (primary + secondary metrics, p-value)
   - Business impact (e.g., "+2.1% conversion = +$50K/year revenue")
   - Key learnings (e.g., "Users prefer confirmation dialogs for destructive actions")
3. **Sharing**: Present findings in weekly product sync; add to "Experiment Archive" wiki
4. **Archive**: Store experiment setup, results, and code in shared repo for future reference

## 4. Common Experiments & Metrics

### 4.1 Feature Adoption Experiments

| Hypothesis | Success Metric | Sample Size | Duration |
|-----------|---|---|---|
| "Larger button will increase feature discovery" | % activating feature | 2,000–5,000 | 1–2 weeks |
| "Help tooltip will improve task completion" | % completing task without error | 1,000–2,000 | 1–2 weeks |
| "New onboarding flow will reduce churn" | % retained after 7 days | 500–1,000 | 2–4 weeks |

### 4.2 Conversion Experiments

| Hypothesis | Success Metric | Sample Size | Duration |
|-----------|---|---|---|
| "Reducing checkout steps will increase conversion" | % completing purchase | 5,000–10,000 | 2–4 weeks |
| "Clearer pricing will reduce cart abandonment" | Revenue per user | 2,000–5,000 | 2–3 weeks |
| "Urgency messaging will lift trial signups" | % signing up for trial | 5,000+ | 1–2 weeks |

### 4.3 Engagement Experiments

| Hypothesis | Success Metric | Sample Size | Duration |
|-----------|---|---|---|
| "Weekly digest email will increase engagement" | % DAU (daily active users) | 1,000–2,000 | 2–4 weeks |
| "Gamification badges will increase feature usage" | Feature usage frequency | 500–1,000 | 2–4 weeks |
| "Personalized recommendations will increase session time" | Avg session duration | 2,000–5,000 | 1–2 weeks |

## 5. Statistical Concepts (Non-Technical Summary)

### 5.1 P-Value & Significance

- **p-value < 0.05**: Result is statistically significant (95% confident difference is real, not random chance)
- **p-value ≥ 0.05**: Not statistically significant; insufficient evidence to declare winner

**Example**: Treatment conversion = 14.1%, Control = 12%, p = 0.032 → **Significant** (confident treatment is truly better)

### 5.2 Sample Size

- Larger sample size = more confidence in small differences
- Small sample size = only large differences are detectable

**Rule of thumb**: Plan for 1,000–5,000 users per experiment (adjust based on metric variance).

### 5.3 False Positives & False Negatives

- **False Positive**: Declare winner when actually no real difference (Probability ≤ 5% if p < 0.05)
- **False Negative**: Declare tie when actually a true difference exists (Probability ≤ 10% with 90% power)

## 6. Coordination with Feature Flagging & Release Management

### 6.1 Multi-Stage Rollout with Experiments

Feature can proceed through stages:

1. **Stage 1 (Beta)**: Feature flag OFF for 99% of users; ON for 1% (beta users)
2. **Stage 2 (A/B Test)**: Feature flag enabled for 50% of users (control = old, treatment = new)
3. **Stage 3 (Winner)**: Feature flag enabled for 100% of users if test shows success

### 6.2 Experiment Documentation in Feature Flagging

In feature flag config, document:

```yaml
flag_name: feature_cloud_new_export
status: active
rollout_stages:
  - stage: beta
    enabled_percentage: 1
    duration: "2026-05-15 to 2026-05-20"
  - stage: a_b_test
    enabled_percentage: 50
    duration: "2026-05-20 to 2026-06-03"
    experiment_id: "exp-export-redesign-001"
  - stage: global_rollout
    enabled_percentage: 100
    duration: "2026-06-03 onwards"
```

## 7. Limitations & Caveats

- **Short-term Bias**: 2-week experiment may not capture long-term behavior (e.g., novelty effect wears off). Plan follow-up studies after 30+ days.
- **External Validity**: Result may not generalize to all user segments (e.g., US result may differ in EU). Consider running segment-specific analyses.
- **Multiple Testing Problem**: Running many experiments increases false positive risk. Set Bonferroni correction if running >5 concurrent experiments.
- **Cannibalization**: New feature may boost primary metric but hurt secondary product lines. Monitor broadly.

## 8. Ethics & Guardrails

- ✅ **Transparency**: Users are not deceived; if testing payment changes, disclose to Finance/Legal
- ✅ **Data Privacy**: Experiment assignments not stored indefinitely; deleted after rollout
- ✅ **Fairness**: Control group receiving inferior experience only acceptable if truly "beta" quality and short-lived
- ✅ **Approval**: Revenue or policy-impacting experiments require VP Product + VP Engineering sign-off before launch

## 9. Experimentation Metrics (Quarterly)

Track:

- **Experiments Launched**: # of hypothesis tests run (target: ≥4 per quarter)
- **Win Rate**: % of experiments showing positive results (typical: 20–30%)
- **Time to Statistical Significance**: Avg days to reach 95% confidence (target: <14 days)
- **Revenue Impact**: Total revenue lifted from winning experiments (cumulative)

