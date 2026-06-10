---
title: Roadmap Planning Process
doc_id: prod-roadmap-planning
owner: Product Leadership
last_updated: 2026-06-09
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Roadmap Planning Process

## 1. Overview

Northwind maintains a **13-week rolling roadmap** that prioritizes features, technical debt, and operational work across all product teams. This process ensures alignment with company strategy and realistic capacity planning.

## 2. Roadmap Tiers

The roadmap is organized into three tiers:

| Tier | Commitment | Review Cadence | Rationale |
|------|-----------|---|---|
| **Q-Tier** (Quarters) | Committed strategic initiatives for the next 12 weeks | Monthly | Visibility for cross-functional planning and customer communication |
| **Sprint-Tier** | Specific features for the next 4 weeks | Weekly (sprint planning) | Concrete team-level commitments |
| **Icebox** | Ideas and backlog items evaluated every quarter | Quarterly | Prospective innovation without false commitment |

## 3. Strategic Alignment

All roadmap items must ladder up to one of four company strategic pillars (example):

1. **Customer Obsession**: Improvements directly addressing top customer pain points
2. **Competitive Differentiation**: Features that set Northwind apart from competitors
3. **Operational Excellence**: Infrastructure, performance, and reliability improvements
4. **Revenue Growth**: Features that enable or increase monetization

Each roadmap item includes:
- **Strategic Pillar**: Which of the four pillars does this serve?
- **Narrative**: 1–2 sentences explaining *why* this matters now (e.g., "Top 3 support tickets in May were about report export; this reduces support load and improves CSAT")
- **Owner**: Product Manager accountable for success

## 4. Planning Cycle

### 4.1 Quarterly Planning (Month 0, Week 1)

**Timing**: First week of each quarter (e.g., Jan 1, Apr 1, Jul 1, Oct 1)

**Process**:

1. **Historical Review**: Analyze what was planned vs. shipped in the prior quarter
   - Shipped on time: What enabled us?
   - Slipped: What was underestimated?
   - Cancelled: Was the decision data-driven or reactive?
2. **Market & Customer Input**: VP Product synthesizes customer interviews, support tickets, competitive analysis, and market research from the prior quarter
3. **Strategic Priorities**: VP Product meets with VP Engineering, VP Design, and CEO (2-hour sync) to align on top 4–6 Q-tier initiatives for next 12 weeks
4. **Capacity Planning**: Engineering lead provides T-shirt sizing for each Q-tier item and flags any known blockers (e.g., "Team will be -1 engineer on parental leave in Q2")
5. **Draft Roadmap**: Product team drafts 13-week rolling roadmap (current Q + first 4 weeks of next Q) in Jira/GitHub Projects
6. **Stakeholder Review**: Share draft with all departments (Finance, Support, Marketing, Sales) for 48-hour async feedback
7. **Final Approval**: VP Product approves final roadmap by end of Week 1; announced in all-hands meeting

### 4.2 Monthly Roadmap Review (Month 0, Week 2)

**Timing**: Every second week of the month

**Process**:

1. **Capacity Reforecasting**: Engineering re-estimates remaining capacity for next 8 weeks given any unplanned absences, incidents, or blockers
2. **Scope Validation**: For items currently in Sprint-Tier (next 4 weeks), verify design and acceptance criteria are locked
3. **New Issues**: Evaluate any urgent bugs or customer escalations; determine if they bump planned roadmap items
4. **Slides Presented**: 30-min sync with VP Product, VP Engineering, VP Design to discuss changes

### 4.3 Sprint Planning (Every 2 weeks)

**Timing**: Start of each 2-week sprint (typical: Mondays)

**Process**:

1. **PRD Review**: For items entering Sprint-Tier, ensure PRD is approved and design is complete (see *Product Development Lifecycle* Phase 2–3)
2. **Epic Breakdown**: Engineering breaks roadmap items into tasks and estimates story points (Fibonacci scale: 1, 2, 3, 5, 8, 13, 21)
3. **Commitment**: Team commits to items they believe they can ship in the 2-week sprint
4. **Stretch Goals**: Identify 1–2 optional "nice-to-have" items if primary goals complete early
5. **Risks & Dependencies**: Flag any blockers that may delay delivery (e.g., "Depends on API v3 from platform team")

## 5. Roadmap Change Management

### 5.1 Adding Items

- **Minor Bug or Small Feature** (<1 week effort): Product Manager can add to sprint directly; notify VP Engineering within 24 hours
- **Medium Feature** (1–4 weeks): Requires removal of equal effort from current sprint (tradeoff discussion with VP Engineering)
- **Large Feature** (4+ weeks): Requires Q-tier planning cycle; cannot be added mid-quarter without CEO approval
- **Security or Data Breach**: Emergency items escalate per *Incident Response Runbook*; normal roadmap paused if Sev-1/Sev-2

### 5.2 Deferring Items

If a roadmap item will not ship on time:

1. **Notification**: Engineering notifies VP Product within 24 hours of discovering delay
2. **Impact Assessment**: Estimate new delivery date and customer impact
3. **Options**: Choose one:
   - **Defer**: Move to next sprint/quarter with revised timeline
   - **Reduce Scope**: Ship minimum viable version and move full feature to next cycle (requires PRD amendment)
   - **Cancel**: Remove entirely if priorities have shifted (requires VP Product + CEO sign-off if committed to customers)
4. **Communication**: VP Product updates stakeholders (Finance, Support, Sales, customers) within 48 hours

## 6. Roadmap Transparency

- **Internal**: Roadmap is visible to all employees via Jira/GitHub Projects; quarterly all-hands discusses top 3 strategic priorities
- **Customer-Facing**: Marketing publishes a public roadmap showing committed delivery windows for next 12 weeks (no specific ship dates); updated quarterly
- **Confidential**: Competitive or revenue-sensitive items marked "Confidential" in roadmap, visible only to leadership team

## 7. Success Metrics for Roadmap Planning

Measured quarterly:

- **On-Time Delivery**: % of Q-tier items shipped by planned date (target: ≥75%)
- **Capacity Forecast Accuracy**: Planned effort vs. actual effort for completed items (target: within ±15%)
- **Scope Stability**: % of items that shipped with planned scope vs. scope reductions (target: ≥85%)
- **Customer Impact**: Did shipped items move key metrics (adoption, CSAT, support load) in right direction?

