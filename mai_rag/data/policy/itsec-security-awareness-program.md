---
title: Security Awareness Program
doc_id: itsec-security-awareness-program
owner: IT Security & HR
last_updated: 2026-04-06
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Security Awareness Program

## 1. Purpose and Scope

This policy establishes mandatory security awareness training for all Northwind employees, contractors, and third parties with system access. The program aims to reduce human-caused security incidents (phishing, credential compromise, accidental data exposure).

## 2. Training Requirements by Role

### 2.1 Onboarding Day 1 (All Employees)

All new hires complete 3 hours of security training before VPN/email access granted:

| Training Module | Duration | Content | Pass Requirement |
|---|---|---|---|
| **Security Fundamentals** | 1 hour | Data classification, encryption, secure password practices | 80% |
| **Acceptable Use & Code of Conduct** | 0.75 hours | Prohibited uses, harassment, discrimination | 100% (signed agreement) |
| **Okta MFA Setup** | 0.5 hours | TOTP configuration, password manager usage, MFA recovery codes | Hands-on test |
| **Phishing & Social Engineering** | 0.75 hours | Phishing indicators, reporting procedures, don't-click demos | 80% |

**Failure consequence**: If employee fails any module, retrain within 2 days. If fail again, access delayed until 3rd attempt passes.

### 2.2 Annual Security Awareness Training (All Employees)

Every employee completes 45 minutes of refresher training annually:
- Module randomization: 3 topics randomly selected from 8 available (prevents "same training every year" fatigue)
- Topics: Phishing, data handling, incident response, password safety, device security, remote work, social engineering, compliance
- Passing score: 80%
- Due date: Anniversary of employment (or 2026 calendar year for legacy employees)
- Tracking: Training completion tracked in Workday; managers notified of non-completion

### 2.3 Role-Based Training

**IT/Security staff** (quarterly):
- 1-hour "threat landscape" briefing (new attack patterns discovered each quarter)
- Topics: Zero-days, ransomware trends, supply chain attacks, incident case studies
- Audience: IT Operations, Security team, architecture reviews

**Developers** (semi-annually):
- 1-hour "secure coding" training (OWASP Top 10, API security, secrets management)
- Topics: SQL injection, XSS, authentication bypass, privilege escalation
- Audience: Engineering teams, contractor developers

**Managers** (annually):
- 45-minute "managing security incidents" (when employee reports phishing/breach, what to do)
- Topics: Incident reporting chain, notifying IT Security, employee support during breach
- Audience: All team leads, VPs

**Data stewards** (semi-annually):
- 1-hour "data governance and retention" (classification, deletion, disposal)
- Topics: Data classification levels, retention periods, secure deletion
- Audience: HR, Finance, Compliance, Legal, Senior engineers with data access

## 3. Phishing Simulations

### 3.1 Quarterly Simulations

All employees receive simulated phishing emails 4x/year (one per quarter):
- **Q1**: CEO impersonation ("CEO exec approval needed on wire transfer")
- **Q2**: Urgent IT request ("Reset your password immediately due to security breach")
- **Q3**: External threat / invoice fraud ("New expense reimbursement tool")
- **Q4**: Holiday-themed ("Holiday gift card, click here to claim")

### 3.2 Simulation Mechanics

- Email designed to mimic real phishing (looks professional; creates urgency)
- Link or attachment leads to training page (not actual download or credential capture)
- Clicking link/downloading = "failed" the test
- Email header analysis challenge: "What's wrong with this email?" (teaches credential headers)
- Simulation results captured; individual and team scores reported

### 3.3 Performance and Intervention

| Simulation Result | Next Steps |
|---|---|
| Passed (did NOT click) | Email delivered as "passed"; recognized phishing |
| Failed (clicked/downloaded) | Immediately redirected to 15-minute "you failed" training module; re-takes phishing awareness test |
| Second failure in 12 months | Escalated to HR; additional 30-minute training with manager; performance plan if third failure |

**Target**: 85% pass rate organization-wide; departments tracking <70% face retraining mandate.

## 4. Training Content and Modules

### 4.1 Core Modules

**Phishing Recognition** (15 min):
- Real vs. fake email headers
- URL spoofing techniques (bit.ly shorteners hiding true URL)
- Attachment risks (macro-enabled Office docs, .exe files)
- Reporting procedures (Report as Phishing button in Outlook)

**Data Handling** (20 min):
- Data classification levels (Public, Internal, Confidential, Restricted)
- Allowed sharing destinations (Internal staff only for Confidential; executive approval for Restricted)
- Secure deletion requirements (overwrite, shredding, incinerator)
- PII identification (SSN, home address, government ID)

**Incident Response** (15 min):
- How to recognize a breach or suspicious activity
- Immediate steps (disconnect from network, notify security@northwind.com)
- Do NOT investigate alone; preserve evidence
- Escalation procedures per **Incident Response Runbook**

**Password Safety** (10 min):
- Minimum 12 characters; no forced rotation
- Use password manager (Azure Vault, 1Password)
- Don't share passwords; unique per account
- MFA as second layer of protection

**Device Security** (10 min):
- Full disk encryption (BitLocker, FileVault) mandatory
- Antivirus engine enabled and updated
- VPN for remote work
- Lock device when away from desk (Windows + L or screen lock)

**Remote Work** (10 min):
- VPN + MFA required for all remote access
- Home WiFi security (WPA3 encryption preferred)
- Confidential data never printed at home
- Video call privacy (webcam covers; no background visibility of data)

**Social Engineering** (10 min):
- Pretexting: Attacker calls and claims to be IT support
- Verification before sharing credentials (call back IT directly; use known phone number)
- Tailgating: Don't let strangers follow you through secure doors
- Dumpster diving: Dispose of printed Confidential data in shredding bin, not trash

**Compliance and Privacy** (10 min):
- GDPR: Right to be forgotten; respond to data access requests within 30 days
- CCPA: California resident data rights
- Email retention: Don't delete emails without business justification
- Third-party vendor DPA: Ensure all vendors sign data agreements

### 4.2 Interactive Elements

- **Quizzes**: 5-10 questions per module; randomized answers
- **Videos**: 2-3 minute attack scenario videos (dramatized; real-world examples)
- **Simulations**: Fake email interface; practice identifying phishing cues
- **Scenario-based**: "What would you do?" interactive decision trees

## 5. Training Delivery and Accessibility

### 5.1 Platform

- **LMS (Learning Management System)**: Northwind uses Docebo (cloud-based)
- **Mobile-friendly**: All training responsive; completable on phone/tablet
- **Languages**: English, Spanish, Mandarin (hire language options available)
- **Accommodations**: Captions for hearing-impaired; text-to-speech for visual impairment

### 5.2 Scheduling

- **Flexible deadlines**: Annual training due by employee's hire anniversary date
- **Completion reminders**: Automated reminders at 30/14/7 days before deadline
- **Time allocation**: Employees may complete during work hours (manager discretion; no personal time required)
- **Group training**: All-hands "Security Awareness Day" optional presentation (1 hr) on security trends

## 6. Metrics and Effectiveness

### 6.1 Training Metrics

- **Completion rate**: Target 95% of employees complete annual training
- **Phishing pass rate**: Target 85% of employees don't fall for simulations
- **Post-training**: Security incidents tracked; target <5% decrease in phishing clicks, credential reuse, accidental data exposure year-over-year
- **ROI**: Cost of training vs. cost of prevented incidents (e.g., ransomware attack prevented)

### 6.2 Quarterly Metrics Report

| Metric | Target | Current (Q1 2026) | Status |
|---|---|---|---|
| Training completion | 95% | 92% | At risk; reminders sent |
| Phishing pass rate | 85% | 78% | Below target; Q2 retraining planned |
| Incident reduction | >5% YoY | -3% (increase) | Worsening; correlates with new employee onboarding |

Metrics reviewed by VP Security and HR quarterly. If completion <90%, department heads held accountable.

## 7. Enforcement and Consequences

### 7.1 Non-Compliance

| Violation | Consequence |
|---|---|
| Fail onboarding training Day 1 | Delay system access until retrain passes |
| Miss annual training deadline | Suspend system/email access until completion |
| Fail annual training (score <80%) | Must retake within 5 business days; if fail again, escalate to HR |
| Fail phishing simulation (2nd time in 12mo) | Mandatory 30-min retraining with manager present; placed on performance plan |
| Repeated phishing failures or security violations | Disciplinary action per **Information Security Policy** enforcement section (warning → suspension → termination) |

### 7.2 Executive Accountability

Executives and IT staff held to SAME standards (no exemptions). If VP fails phishing simulation:
- VP Security reviews with executive personally (not delegated to HR)
- Enhanced threat briefing provided
- Executive sponsors team-wide security initiative (to model commitment)

## 8. Guest and Contractor Training

### 8.1 Contractor Onboarding

All contractors with system access complete abbreviated training (30 min):
- Data classification and handling (10 min)
- Incident reporting (5 min)
- Acceptable use (10 min)
- MFA and password safety (5 min)

Training required **before** contractor system access granted.

### 8.2 Guest/Temporary Access

Guests with temporary email or VPN access:
- Receive simplified email guide (don't fall for phishing targeting contractors)
- Notified of building security policies (badge, visitor log, escorts in restricted areas)

## 9. Training Effectiveness Evaluation

### 9.1 Annual Program Review

Each year, IT Security evaluates:
- Completion rates by department (identify lagging teams)
- Phishing pass rates by department (prioritize additional training for low-performers)
- Incident data: Did employees report suspicious emails? Did click-through rates decrease?
- Employee feedback: Survey on training relevance and engagement
- Content updates: Are new attack vectors (e.g., AI-generated deepfakes) covered?

### 9.2 Continuous Improvement

- New modules added annually (e.g., "Deepfake Detection" module added 2026)
- Phishing simulation scenarios updated quarterly (use real attacks from threat intelligence)
- Case studies: Real Northwind incidents (anonymized) featured in training to increase relevance

## 10. Related Policies

- **Information Security Policy**: General security standards; enforcement procedures
- **Acceptable Use Policy**: Acceptable and prohibited uses of corporate systems
- **Incident Response Runbook**: How to report and escalate security incidents
- **Email & Phishing Defense**: Email security controls and phishing indicators

---

**Document owner:** VP Security & Chief People Officer  
**Last approved:** 2026-04-06 by Security Steering Committee  
**Next review:** 2027-04-06
