---
title: UX Research Process
doc_id: prod-ux-research
owner: Design Leadership
last_updated: 2026-06-09
status: active
classification: internal
supersedes: ""
supersedes_by: ""
---

# UX Research Process

## 1. Purpose

UX Research informs all product decisions. Rather than guessing what users need, we validate assumptions with real user data. This process ensures features are designed around actual user needs, not internal assumptions.

**Principle**: User insights trump executive opinions. Every major feature decision should be grounded in user research.

## 2. Research Methods

### 2.1 Discovery Research (Exploratory)

**Goal**: Understand user needs, pain points, and mental models before defining solutions.

| Method | Duration | Participants | Best For |
|--------|----------|--------------|----------|
| **Contextual Interview** | 45–60 min | 1 user | Deep understanding of workflow and context |
| **User Diary Study** | 1–2 weeks | 5–10 users | Behavior patterns over time |
| **Card Sorting** | 30 min | 20–40 users | Information architecture and mental models |
| **Survey** | 10–15 min | 50–200 users | Quantifying preferences; market sizing |
| **Focus Group** | 60–90 min | 6–8 users | Exploring reactions to concepts |

**Output**: Persona documentation, journey map, problem statement, design direction (see *Product Development Lifecycle* Phase 1).

### 2.2 Validation Research (Confirmatory)

**Goal**: Confirm solutions address the identified problem before full development.

| Method | Duration | Participants | Best For |
|--------|----------|--------------|----------|
| **Usability Test** | 45–60 min | 6–8 users | Testing wireframes or prototypes |
| **A/B Test** | 1–4 weeks | 1,000+ users | Quantifying feature impact |
| **Concept Testing** | 20–30 min | 30–50 users | Validating messaging or design direction |
| **Tree Test** | 15 min | 50–100 users | Navigation structure |

**Output**: Usability findings, design recommendations, success criteria for launch (see *Product Release Management*).

### 2.3 Post-Launch Research (Evaluative)

**Goal**: Measure if launched feature delivers expected value and identify improvements.

| Method | Duration | Participants | Best For |
|--------|----------|--------------|----------|
| **In-App Survey** | 30 sec | 100+ users | Quick feedback on feature satisfaction |
| **NPS Survey** | 2 min | 500+ users | Overall satisfaction and loyalty tracking |
| **User Interview (Post-Launch)** | 30–45 min | 5–10 users | Understanding adoption barriers; feature improvements |
| **Analytics Review** | Ongoing | N/A | Tracking adoption, engagement, retention |

**Output**: Feature success metrics, iteration backlog, post-launch retrospective (see *Product Development Lifecycle* Phase 6).

## 3. Planning a Research Study

### 3.1 Research Kick-off (Week before study starts)

1. **Define Objective**: What question are we answering? (e.g., "Do users understand how to export a report?" not "Do users like export?")
2. **Success Criteria**: How will we know research succeeded? (e.g., "80%+ users can export report in <2 min without help")
3. **Participant Criteria**: Who are we talking to? (e.g., "Power users (3+ exports/month); mix of US and EU; both Admin and Standard roles")
4. **Method Selection**: Which method best answers the question? (e.g., moderated usability test for new UI; survey for preference validation)
5. **Recruiting**: UX Researcher recruits participants via:
   - In-app notification ("Help shape our product; 1-hour user interview")
   - Email to VIP customers
   - Vendor (e.g., UserTesting.com for quick remote recruiting)
   - **Target**: 70%+ acceptance rate to get desired sample size

### 3.2 Research Execution

**Before**:
- Create discussion guide or test script (questions to ask in consistent order)
- Prepare stimuli (prototype, wireframes, survey questions)
- Brief team on observation rules (note user behavior, not personal opinions)
- Set up recording (video + audio; get consent before recording)

**During**:
- Moderator asks open-ended questions (e.g., "What are you looking for?" not "Did you like the button?")
- Observe behavior (watch what users *do*, not just what they *say*)
- Probe unexpected findings (e.g., "Tell me more about why you clicked there")
- Take notes in real-time

**After**:
- Thank participant; document any follow-up questions
- Assign payment (standard: $50 for 30 min, $100 for 60 min)

### 3.3 Analysis & Synthesis

1. **Affinity Mapping**: Team reviews all notes; group similar findings into themes
2. **Quantify**: Count how many participants mentioned each theme (e.g., "7/8 users struggled with step 3")
3. **Recommendations**: For each finding, draft design recommendation (e.g., "Add help text explaining export formats")
4. **Prioritize**: Focus on findings that affect >50% of users or block core workflow
5. **Document**: Write 1–2 page summary of key findings and design recommendations

**Artifact**: Share findings in Figma comment, Slack thread, or shared document; link to study video recordings.

## 4. Usability Testing (Detailed Process)

Usability testing is the most common research method. Process:

### 4.1 Test Plan (1 page)

- **Objective**: What are we testing? (e.g., "Test new report export UI")
- **Participant Criteria**: Who? (e.g., "8 power users, US + EU, both Admin and Standard roles")
- **Method**: Moderated remote usability test (90 min: 30 min setup + 45 min test + 15 min debrief)
- **Stimuli**: Link to prototype in Figma or UserTesting.com
- **Tasks**: 3–5 realistic tasks (e.g., "Export a dashboard as PDF"; "Find where to download past exports")
- **Success Criteria**: Benchmark (e.g., "User completes task in <2 min without help" = success)

### 4.2 Moderated Test Flow

**Setup (30 min)**:
1. Icebreaker: "Tell me about your role and how you use reports"
2. Explain process: "I'll ask you to complete a few tasks; think aloud as you go"
3. Tech check: Confirm screen sharing, audio, recording working

**Test (45 min)**:
1. **Task 1**: "Export this dashboard as PDF" → Observe and take notes
2. **Probe**: "What were you looking for when you clicked there?" → Listen for mental model
3. **Task 2**: "Find where to download past exports" → Observe
4. **Probe**: "Was that where you expected it to be?" → Identify mental model gaps
5. **Task 3**: Alternative scenario (e.g., "Export to Excel instead")
6. **General**: "What was the most confusing part?"

**Debrief (15 min)**:
- "How likely would you use this feature?" (0–10 scale)
- "What would make it better?"
- Thank participant; send payment

### 4.3 Analysis Template

After all 8 sessions complete:

| Task | Success Rate | Difficulty | Key Insights | Design Recommendation |
|------|--------------|-----------|--------------|----------------------|
| **Export as PDF** | 7/8 (88%) | Easy | 1 user missed export button initially | Add tooltip on button |
| **Find past exports** | 6/8 (75%) | Medium | Users expected "Downloads" not "Export History" | Rename section to "Downloads" |
| **Export to Excel** | 5/8 (63%) | Hard | Users didn't see Excel option was available | Promote Excel in menu; show alongside PDF |

**Recommendation**: Address "Hard" tasks before launch; iterate on "Medium" tasks post-launch.

## 5. Survey Research

### 5.1 Survey Design

- **Length**: Keep to <3 min (aim for <10 questions)
- **Question Types**: Mix multiple-choice, Likert scale, and open-ended
- **Avoid Leading Questions**: ❌ "Don't you think this is great?" ✅ "How would you rate this?"
- **Sample Size**: 50 responses minimum (web/app research); 100+ for statistically significant results

### 5.2 Survey Question Examples

**Preference**:
- "Which format do you prefer for exporting reports?" (PDF / Excel / CSV / No preference)

**Satisfaction (Net Promoter Score)**:
- "How likely are you to recommend Northwind to a colleague?" (0–10 scale)
- Net Promoter Score = (% Promoters 9–10) – (% Detractors 0–6)

**Behavior**:
- "How often do you export reports?" (Daily / Weekly / Monthly / Never)

**Open-Ended**:
- "What's the most frustrating part of exporting reports?" (text field)

## 6. Research Timeline & Roadmap Integration

### 6.1 When to Research

| PDLC Phase | Research Method | Timeline |
|-----------|-----------------|----------|
| **Phase 1 (Discovery)** | Contextual interviews, survey | Week 1–3 |
| **Phase 2 (Strategy)** | Survey validation, competitive analysis | Week 3–6 |
| **Phase 3 (Design)** | Usability test (wireframes) | Week 4–8 |
| **Phase 4 (Engineering)** | Beta research, internal dogfooding | Week 7–20 |
| **Phase 5 (Launch)** | A/B testing | Week 19–22 |
| **Phase 6 (Post-Launch)** | Post-launch survey, interview, analytics | Week 23–26 |

### 6.2 Timing Constraints

- **Discovery Research**: Must complete before PRD is finalized (can't build without understanding the problem)
- **Validation Research**: Must complete before full engineering begins (defer to beta if tight timeline)
- **Post-Launch Research**: Schedule 2–3 weeks after launch (sufficient adoption data)

## 7. Research Ethics

All research must be ethical and user-centric:

- ✅ **Informed Consent**: Users know they're being researched and can opt out
- ✅ **Privacy**: No PII collected without explicit consent; data deleted after analysis
- ✅ **Transparency**: Be honest about how we'll use findings (e.g., "To improve the product, not for marketing")
- ✅ **Inclusivity**: Recruit diverse participants; don't over-sample only power users
- ✅ **Fair Compensation**: Pay research participants fairly ($50–100/hr standard)

## 8. Research Repository

All research findings stored in:

- **Figma**: Comments and prototype links
- **Shared Drive**: `Research/[Product]/[Year-Quarter]/` folder with study documents, recordings, transcripts
- **Team Wiki**: Summary of learnings linked from relevant PRD or feature doc

**Retention**: Keep for 2 years; delete personal data after 1 year.

## 9. Research Metrics

Track quarterly:

| Metric | Target | How |
|--------|--------|-----|
| **Launched Features with Research** | 100% | All Medium+ features have usability test feedback before launch |
| **Usability Test Participants** | 50+ per quarter | Count all research studies (discovery + validation + post-launch) |
| **Research Insights Applied** | ≥80% | % of major usability findings implemented in design |

