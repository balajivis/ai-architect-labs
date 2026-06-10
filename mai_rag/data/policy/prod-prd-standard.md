---
title: Product Requirements Doc Standard
doc_id: prod-prd-standard
owner: Product Leadership
last_updated: 2026-06-09
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Product Requirements Doc Standard

## 1. Purpose

A Product Requirements Document (PRD) is the single source of truth for a feature or product initiative. It communicates the problem, solution, success criteria, and constraints to Engineering, Design, and stakeholders. Every major feature (Medium-scope or larger per the Product Development Lifecycle) requires a PRD.

## 2. Required Sections

### 2.1 Header (1 page)

- **Title**: Feature or product name
- **Owner**: Product Manager name and email
- **Status**: Draft | In Review | Approved | Launched
- **Last Updated**: Date in YYYY-MM-DD format
- **Target Launch**: Target date in YYYY-MM-DD format
- **T-shirt Size**: XS / S / M / L / XL
- **Epic Link**: Jira epic URL or GitHub Project link

### 2.2 Executive Summary (1 page)

- **Problem Statement**: What customer problem does this solve? (max 300 words)
- **Solution Summary**: High-level approach (max 200 words)
- **Business Case**: Revenue impact, competitive advantage, or cost savings (max 150 words)
- **Key Success Metric**: One primary metric this initiative optimizes (e.g., "Reduce support tickets for X by 30%")

### 2.3 Target User & Use Case (1 page)

- **User Personas**: Name, role, and 2–3 pain points for each primary persona (max 3 personas)
- **Use Case**: Write a narrative scenario: "As a [user], I want to [action] so that [outcome]" (max 500 words)
- **Competitive Benchmark**: How do 3 competitors solve this? (link to Coda doc or attach comparison table)

### 2.4 Solution & Design (2–3 pages)

- **Feature Overview**: What exactly is being built? List each component (e.g., "New Report Builder widget, Three export formats: PDF / CSV / Excel")
- **User Workflows**: Describe happy path and 2–3 alternate paths (e.g., "User with no data"; "User on mobile"; "User with <1 min to complete task")
- **Mockups or Wireframes**: Embed Figma links or screenshots; must include error states and empty states
- **Out of Scope**: Explicitly list what is NOT included to set expectations (e.g., "Not building real-time collaboration in v1"; "Mobile app support deferred to Q3")

### 2.5 Success Metrics & Acceptance Criteria (1 page)

- **Adoption Metric**: "X% of eligible users activate feature within 30 days of launch"
- **Engagement Metric**: "Users return to feature at least Z times per month"
- **Business Metric**: Revenue impact, support cost reduction, or NPS improvement target
- **Acceptance Criteria**: Numbered list of testable conditions (e.g., "User can export report as PDF"; "Report generation completes in <10 seconds for datasets up to 10K rows"; "All UX states (loading, error, empty) display correctly")

### 2.6 Technical Considerations (1 page)

- **Platform Impact**: Which services/APIs/databases are affected? (e.g., "Modifies user-service API contract; adds new Postgres table `reports_generated`")
- **Performance Budget**: E.g., "Page load must remain <2 seconds; report generation must complete within 60 seconds for 100K-row dataset"
- **Security & Privacy**: Data classification (see *Data Classification & Retention Policy*), PII handling, encryption requirements
- **Accessibility**: Must conform to WCAG 2.1 AA per *Accessibility Standard* (e.g., "Form fields have proper labels"; "Color alone doesn't convey meaning"; "Keyboard navigation supported")
- **Localization**: Which languages/regions in scope? (see *Localization & Internationalization Standard*)
- **Dependencies**: Are other teams' features required? (e.g., "Depends on API v3 launch in Q2")

### 2.7 Rollout & Launch Plan (1 page)

- **Phased Rollout**: Will this be feature-flagged? Which user cohorts receive first? (e.g., "10% internal → 25% beta customers → 50% general → 100%")
- **Support & Documentation**: Release notes, customer communication, internal training required
- **Rollback Plan**: How will we revert if critical issues discovered? (reference *Feature Flagging Standard*)
- **Success Criteria for Go/No-Go**: Explicit decision criteria at each phase (e.g., "At 25% rollout, if error rate >0.5%, pause and investigate")

### 2.8 Risks & Mitigation (1 page)

- **Technical Risks**: E.g., "New database schema requires migration on 100M records; estimated 30-min downtime. Mitigation: Perform migration during maintenance window; feature available after migration."
- **Product Risks**: E.g., "May cannibalize premium tier; adoption <10% risk. Mitigation: A/B test messaging; monitor engagement metrics closely."
- **Operational Risks**: E.g., "Increased support load. Mitigation: Write support playbook before launch; hire contract support."

## 3. Approval Gates

| Gate | Approvers | Timing |
|------|-----------|--------|
| **Strategy Gate** | VP Product, VP Engineering | Before design starts (Week 3 of PDLC) |
| **Design Gate** | Design Lead, VP Product | After design QA (Week 7 of PDLC) |
| **Engineering Gate** | VP Engineering, Engineering Lead | During staging validation (Week 19 of PDLC) |
| **Launch Gate** | VP Product, On-Call Engineer | 24 hours before production rollout |

## 4. Template Checklist

Before submitting for approval:

- [ ] Problem statement grounded in 5+ customer conversations or data
- [ ] Success metrics are measurable and SMART (Specific, Measurable, Achievable, Relevant, Time-bound)
- [ ] Design mockups include all system states and are accessible (WCAG 2.1 AA)
- [ ] Technical review confirms no architectural red flags
- [ ] Acceptance criteria are testable (QA and Engineering sign off)
- [ ] Data classification and PII handling reviewed by VP Security
- [ ] Launch plan includes rollout percentages and go/no-go criteria
- [ ] Risks and mitigations are realistic and have owners

## 5. Living Document

The PRD evolves through the development cycle:
- **Weeks 1–3 (Discovery)**: Sections 1–3 complete, sections 4–5 drafted
- **Weeks 4–6 (Strategy)**: Sections 1–5 complete, sections 6–8 drafted
- **Weeks 7–8 (Design)**: All sections complete; mockups embedded
- **Weeks 19–22 (Launch)**: Rollout plan finalized; actual metrics documented in appendix after launch

Document PRD changes in a **Changelog** section appended to the PRD. Significant changes (e.g., scope expansion >20%) require re-approval from VP Product and VP Engineering.

