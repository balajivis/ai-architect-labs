---
title: Product Development Lifecycle
doc_id: prod-product-development-lifecycle
owner: Product Leadership
last_updated: 2026-06-09
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Product Development Lifecycle

## 1. Overview

The Product Development Lifecycle (PDLC) is Northwind's standard process for moving ideas from conception to launch and beyond. This process ensures alignment with company strategy, customer needs, and operational capacity. All major feature development and product initiatives must follow this framework.

## 2. PDLC Phases

### 2.1 Discovery Phase (Weeks 1–3)

1. **Idea Intake**: Product team collects customer feedback, market research, and internal suggestions via HubSpot, Slack, and monthly product review meetings
2. **Problem Definition**: Write a concise problem statement (max 500 words) identifying the customer pain point and business opportunity
3. **Initial Validation**: Conduct 5–10 customer interviews or surveys to confirm problem-market fit
4. **Preliminary Scope**: Estimate T-shirt sizing (XS = 1-2 weeks, S = 2-4 weeks, M = 4-8 weeks, L = 8-16 weeks, XL = 16+ weeks)
5. **Stakeholder Review**: Present findings to Engineering Leadership, VP Product, and VP Design in a sync meeting

**Success Criteria**: Problem statement approved; preliminary scope agreed; funding allocated for next phase

### 2.2 Strategy & Specification Phase (Weeks 3–6)

1. **Create Product Requirements Document (PRD)** per the PRD Standard (see *Product Requirements Doc Standard*)
2. **Market Validation**: Run a survey or Typeform with 50+ target users to validate solution direction
3. **Competitive Analysis**: Audit 3–5 competing solutions and document differentiation opportunities
4. **Success Metrics**: Define 2–3 success metrics (e.g., "reduce mean time to X from 5 min to 2 min"; "increase adoption by 20%") with baseline measurements
5. **Roadmap Slot**: Product & Engineering confirm this initiative fits the current 13-week rolling roadmap

**Success Criteria**: PRD approved by VP Product and VP Engineering; metrics baselined; roadmap slot confirmed

### 2.3 Design Phase (Weeks 4–8 concurrent with Strategy)

1. **User Workflows**: UX team creates 2–3 user journey flows showing the happy path and 2 alternate paths
2. **Design System Alignment**: Verify all components use Northwind Design System (see *Design System Guidelines*)
3. **Accessibility Review**: Initial WCAG 2.1 AA audit of proposed wireframes (see *Accessibility Standard*)
4. **Wireframes**: Low-fidelity wireframes for each user flow (Figma, review every 3 days)
5. **Usability Testing**: Conduct moderated usability test with 6–8 users and iterate based on feedback
6. **High-Fidelity Mockups**: Build interactive prototypes ready for engineering handoff
7. **Design QA**: Verify mockups include all system states (error, loading, empty, success) and follow accessible color contrast ratios

**Success Criteria**: Interactive prototype approved; accessibility audit completed; 80%+ positive feedback from usability testing

### 2.4 Engineering Phase (Weeks 7–20 depending on scope)

1. **Architecture Design**: Engineering lead creates a technical design document (e.g., ADR template)
2. **Feature Flag Setup**: Add feature flags per Feature Flagging Standard (see *Feature Flagging Standard*); default to OFF during dev
3. **Development**: Code is developed on feature branches, reviewed per Northwind GitHub standards (2 approvals required)
4. **Unit & Integration Tests**: Minimum 75% code coverage required for new components
5. **Staging Validation**: Deploy to staging and verify against PRD acceptance criteria (see *Production Deployment Runbook*)
6. **Beta & Early Access**: If complexity warrants, enroll beta customers per Beta & Early Access Program (see *Beta & Early Access Program*)

**Success Criteria**: All acceptance criteria met in staging; zero P0/P1 bugs; feature flag enables gradual rollout

### 2.5 Launch Phase (Weeks 19–22)

1. **Product Release Management**: Schedule release per Product Release Management policy (see *Product Release Management*)
2. **Documentation & Support**: Product & Engineering write release notes, support articles, and customer communication
3. **Monitoring**: Set up Datadog dashboards and alerts to monitor error rate, latency, and adoption metrics (see *Product Analytics & Telemetry Standard*)
4. **Gradual Rollout**: Enable feature flag for 10% of users, then 25%, then 50%, then 100% (over 5–10 days)
5. **Customer Communication**: Email announcement to all users with release date and change summary

**Success Criteria**: Feature flag enabled for 100% of users; zero Sev-1 incidents; metrics trending toward success targets

### 2.6 Post-Launch Monitoring & Iteration (Weeks 23+)

1. **Metric Tracking**: Weekly check-ins on success metrics (adoption, engagement, support tickets)
2. **Customer Feedback**: Collect feedback via in-app surveys and support tickets
3. **Deprecation Decision**: If a new feature displaces older functionality, plan sunset timeline per Feature Deprecation & Sunset Policy (see *Feature Deprecation & Sunset Policy*)
4. **Localization**: If the feature includes user-facing text, coordinate localization per Localization & Internationalization Standard (see *Localization & Internationalization Standard*)
5. **Experimentation**: Run A/B tests on messaging, pricing, or UX variants per Experimentation & A/B Testing Policy (see *Experimentation & A/B Testing Policy*)

## 3. Roles & Responsibilities

| Role | Phase | Responsibility |
|------|-------|-----------------|
| Product Manager | Discovery → Post-Launch | Own PRD, roadmap prioritization, success metrics |
| Design Lead | Strategy → Launch | Wireframes, accessibility, design QA |
| Engineering Lead | Design → Post-Launch | Technical design, feature flag setup, staging validation |
| VP Product | All phases | Roadmap approval, discovery validation, launch decision |
| VP Engineering | Design → Launch | Capacity planning, code review, deployment |

## 4. Governance & Change Control

- **Scope Creep**: Any scope increase >20% requires re-estimation and roadmap re-prioritization approved by VP Product and VP Engineering
- **Timeline Slips**: If estimated delivery will slip >1 week, notify stakeholders within 48 hours with risk mitigation plan
- **Cancellation**: Any feature can be cancelled by VP Product if market conditions change, but only in phases 1–3 without escalation. Phases 4+ cancellation requires CEO sign-off

## 5. Documentation Requirements

All initiatives must document:
- Approved PRD (see *Product Requirements Doc Standard*)
- Roadmap entry with T-shirt sizing
- Success metrics with baseline measurements
- Usability test results (if applicable)
- Final design mockups in Figma
- Feature flag configuration
- Release notes
- Post-launch retrospective (30 days after launch)

