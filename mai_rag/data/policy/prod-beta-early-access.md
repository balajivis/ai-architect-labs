---
title: Beta & Early Access Program
doc_id: prod-beta-early-access
owner: Product Leadership
last_updated: 2026-06-09
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Beta & Early Access Program

## 1. Purpose

The Beta & Early Access Program allows selected customers to trial new features before general availability. This provides:

- **Customer validation**: Real-world usage patterns inform final design decisions
- **Early feedback**: Identify issues, usability problems, and feature gaps before public launch
- **Competitive advantage**: Early adopter customers gain time-to-value; builds loyalty
- **Marketing**: "Trusted tester" status creates brand advocates

## 2. Program Tracks

### 2.1 Closed Beta (Confidential Releases)

- **Duration**: 2–4 weeks
- **Participants**: 5–15 hand-picked customers
- **Risk Level**: High (feature may be unstable; data structures may change)
- **Typical Use Case**: Complex features requiring significant user training or data migration
- **Confidentiality**: NDA required; no public announcement
- **Feedback Channels**: Weekly video calls + shared Slack channel + feedback form

**Example**: New Report Builder feature requires customers to migrate existing reports to new format; beta users validate migration process.

### 2.2 Open Beta (Public Preview)

- **Duration**: 4–8 weeks
- **Participants**: Self-selected customers who opt-in
- **Risk Level**: Medium (feature mostly stable; minor polish remaining)
- **Typical Use Case**: Features ready for broader testing but not general availability
- **Confidentiality**: Public announcement; link to beta signup form
- **Feedback Channels**: Community forum + feature flag in-app "Send Feedback" button + weekly community calls

**Example**: PDF export feature ready for testing; beta form collects 50 feedback responses to improve UX before rollout.

### 2.3 Limited Availability (Staged Rollout)

- **Duration**: 1–2 weeks per stage
- **Participants**: Automatic percentage-based rollout (see *Feature Flagging Standard*)
- **Risk Level**: Low (feature stable; final polish)
- **Typical Use Case**: Low-risk features; percentage rollout to 10% → 50% → 100%
- **Confidentiality**: Release notes published; no "beta" label
- **Feedback Channels**: Support tickets + in-app feedback + NPS surveys

**Example**: New sidebar navigation; feature flag enables for 10% of users for 48h, then 50%, then 100%.

## 3. Participant Selection

### 3.1 Closed Beta Criteria

Product team selects participants based on:

- **Usage Patterns**: Heavy users of related features (e.g., for Report Builder beta, select customers who export reports daily)
- **Geography**: Mix of US, EU, and APAC timezones for async feedback
- **Plan Level**: Mix of Standard, Professional, and Enterprise customers (avoid only Enterprise bias)
- **Communication**: Customers known for providing detailed, constructive feedback
- **Size**: Avoid "influencers" (brand accounts) to keep feedback unbiased

**Selection Process**:
1. Product Manager drafts list of 5–15 candidates with justification
2. Sales & Success teams verify: no active issues, willingness to participate, realistic for their use case
3. Product Manager sends personalized invitation with detailed description of what to test
4. Target: 70%+ acceptance rate (send 20 invites to get 14 participants)

### 3.2 Open Beta Signup Form

Capture:
- Email & company name
- Current product plan (Standard / Professional / Enterprise)
- Key use case (open text; helps prioritize feedback)
- Availability for weekly calls (optional)

**Acceptance**: Auto-approve all signups; no gatekeeping (goal is broad feedback).

## 4. Beta Lifecycle

### 4.1 Pre-Beta Setup (1 week before launch)

1. **Feature Flag Setup**: Create flag `feature_<product>_<feature>_beta` set to OFF
2. **Documentation**: Draft "Beta Features Guide" explaining:
   - What the feature does
   - Known limitations ("This feature is in beta; data structures may change")
   - How to provide feedback (form, Slack channel, email)
   - No SLA; beta features not covered by support contracts
3. **Support Training**: Brief support team on feature; route beta-related tickets to Product team
4. **Metrics Dashboard**: Set up Datadog dashboard to track beta adoption, error rates, and user engagement
5. **Legal**: Ensure NDA covers beta access (Closed Beta only)

### 4.2 Beta Launch

**Closed Beta**:
1. Send personalized email to selected customers with login link + feature flag enabled for their accounts
2. Schedule weekly 30-min video sync with all participants
3. Share Slack channel link for async feedback
4. Create feedback form (Google Form or Typeform) for structured input

**Open Beta**:
1. Publish landing page with signup form and feature description
2. Email announcement to existing customers (1-2 paras; link to signup)
3. Share in community forums, social media, or newsletter (3–5 posts over 1 week)
4. Create weekly community call (optional; 30 min, record for async viewing)

### 4.3 Beta Feedback Collection (2–4 weeks)

**Weekly Cadence**:

| Day | Activity |
|-----|----------|
| **Monday** | Sync meeting with participants (Closed) or community call (Open) |
| **Tuesday–Thursday** | Collect feedback from form submissions, Slack, support tickets |
| **Friday** | Product team reviews feedback, prioritizes issues, plans fixes |

**Feedback Categories**:

- **Critical Issues** (data loss, security, inability to use): Fix immediately; notify participants
- **Important Issues** (significant usability problems): Fix before general launch
- **Nice-to-Haves** (polish, new ideas): Consider for post-launch updates
- **Non-Issues** (expected behavior, feature requests unrelated to beta): Log for future roadmap

**Feedback Response**:
- Acknowledge receipt within 24 hours
- Provide status update within 48 hours
- For fixes, include test link or timeline

### 4.4 Decision Criteria (Before General Availability)

**Go Criteria** (launch publicly):
- ✅ Zero P0 (critical) issues
- ✅ <5 P1 (high) issues, all with workarounds or fixes planned
- ✅ ≥70% positive feedback (NPS >40 or satisfaction >4/5)
- ✅ Performance metrics stable (error rate <0.5%, latency <10% above baseline)

**Hold Criteria** (extend beta):
- ⚠️ 5–10 P1 issues requiring additional investigation
- ⚠️ 50–70% positive feedback; usability concerns
- ⚠️ **Action**: Extend beta 2–4 weeks; prioritize top P1 issues; collect follow-up feedback

**No-Go Criteria** (cancel feature):
- ❌ ≥10 P0 or P1 issues that cannot be resolved quickly
- ❌ <50% positive feedback; fundamental design problems
- ❌ **Action**: Halt beta; return feature to design phase; communicate with participants (2–3 week delay, revised timeline)

## 5. Transition to General Availability

### 5.1 Communication (1 week before launch)

- **Internal**: All-hands announcement of launch date and key changes based on beta feedback
- **Beta Participants**: Personalized thank-you email; highlight their feedback impact; invite to launch webinar
- **All Customers**: Release announcement with new feature summary
- **Support**: Publish "What's New" help article; schedule training for support team

### 5.2 Deployment

- **Feature Flag**: `feature_<product>_<feature>_beta` renamed to `feature_<product>_<feature>` and rolled out per *Feature Flagging Standard* and *Product Release Management*
- **Post-Launch**: Keep flag enabled for 30 days; monitor adoption and issues; remove flag after 30 days if stable

### 5.3 Celebration

- **Blog post**: "X months of beta testing resulted in Y improvements; thank you to Z beta customers"
- **Customer testimonials**: Quote 2–3 beta participants on how feature improved their workflow
- **Case study**: (Optional) Deep dive case study with 1 beta customer on their use case and ROI

## 6. Beta Metrics

Track throughout beta period:

| Metric | Target | Definition |
|--------|--------|-----------|
| **Adoption** | ≥60% of beta cohort uses feature ≥1x | % of participants activating feature |
| **Engagement** | ≥40% return 2+ times | % returning within 1 week |
| **Satisfaction** | NPS ≥40 or satisfaction ≥4/5 | Survey score after 1 week |
| **Error Rate** | <0.5% | P99 errors in feature usage |
| **Support Load** | <10 tickets / 100 users | Beta-related support requests |

## 7. Closed Beta NDA

All Closed Beta participants sign a standard NDA covering:

- **Confidentiality**: Cannot discuss feature, roadmap, or timeline with competitors or public
- **Data Handling**: Beta data may be used internally for metrics; will be deleted post-beta
- **Feedback Ownership**: Northwind owns all feedback; may be shared with team
- **No Warranty**: Feature is provided "as-is"; no support SLA; data may be reset between beta builds
- **Liability**: Northwind not liable for issues; beta customers use at own risk

Template: See Legal team; add to all Closed Beta invitation emails.

