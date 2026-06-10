---
title: Purchase Approval Matrix
doc_id: fin-purchase-approval-matrix
owner: Finance Operations
last_updated: 2026-06-01
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Purchase Approval Matrix

## 1. Overview

This policy establishes approval authority for purchases by amount and category. All purchase requests must follow the approval matrix; unauthorized or improperly approved purchases may be reversed and the approver held accountable.

**Related policies**: **Procurement Thresholds & Competitive Bidding** policy defines multi-vendor requirements; **Purchase Approval Matrix** defines who approves.

## 2. Approval Authority by Amount

### 2.1 Purchase Approval Matrix

| Amount Range | Approver | Documentation Required | Competitive Bids |
|---|---|---|---|
| $0 – $999 | Department Manager | Receipt/invoice | No |
| $1,000 – $4,999 | Department Manager + Finance | Procurement request + invoice | No |
| $5,000 – $24,999 | VP (Department) + Finance | Procurement request + quotes | 2 quotes required |
| $25,000 – $99,999 | CFO + VP Procurement | Vendor evaluation + quotes | 3 quotes required |
| $100,000 – $250,000 | CFO + CEO + Board Approval | Full business case + vendor SOC 2 | 3 quotes + vendor security review |
| Over $250,000 | Board of Directors | Strategic review + ROI analysis | Competitive RFP process |

**Multi-level approval**: Each level must approve before proceeding to the next. Approvals must be obtained in sequence (no skipping levels).

### 2.2 Category-Specific Approvals

Certain categories have additional review requirements, regardless of amount:

#### Infrastructure and Cloud Services
- **AWS/Azure spending**: IT Security reviews cloud architecture; Finance approves cost
- **DDoS or security services**: VP Security approves; must demonstrate ROI
- **Data center colocation or new infrastructure**: CTO/VP Engineering + CFO + Board (if >$50K)

#### Customer Data and PII Processing
- **Any vendor accessing customer data**: Must complete vendor security assessment (see **Vendor Procurement & Third-Party Risk Policy**)
- **Data processing agreements required**: Legal reviews DPA; Finance approves cost
- **Annual spend > $100K**: Board approval required if vendor handles PII

#### Professional Services and Consultants
- **Legal services**: General Counsel approves hourly rate and engagement scope
- **Auditors and tax advisors**: CFO approves; must be approved audit firms
- **Executive recruiters**: VP People approves; must be retained firms
- **Contractors under $50K**: Department Manager + Finance approve
- See also **Contractor & Consultant Payment Policy**

#### Equipment and CapEx
- **Single item over $50K**: CapEx approval (see **Capital Expenditure Policy**)
- **Office equipment, furniture**: Department Manager + Facilities; Finance if >$5K
- **IT hardware (laptops, servers, network)**: IT + Finance; CapEx review if >$50K

#### Travel and Conference Registration
- See **Expense & Travel Policy** and **Travel Booking Policy**
- Conference registration >$3,000: VP approval required
- Travel estimated cost >$2,500: VP approval required

#### SaaS and Software Licenses
- **New SaaS tool**: IT or department lead + Finance approval
- **Renewal or multi-year licensing**: Finance reviews cost-per-user and ROI
- **Seats over 50**: VP + CFO approval (multi-department impact)

## 3. Procurement Request Process

All purchases over $1,000 must be submitted via the Procurement portal (Ariba or equivalent):

1. **Requestor** (department manager) submits procurement request:
   - Business justification (why do we need this?)
   - Preferred vendor(s)
   - Estimated cost and budget code (department, cost center)
   - Requested delivery date

2. **Department Manager** approves within 1 business day

3. **Finance** reviews:
   - Budget availability (no overspend)
   - Prior vendor relationship (has Finance negotiated a discount?)
   - Policy compliance (see **Procurement Thresholds & Competitive Bidding**)

4. **VP (if required)** approves within 2 business days

5. **Procurement team** (if required):
   - Gathers competitive quotes
   - Negotiates best price
   - Evaluates vendor (risk, delivery, support)
   - Recommends vendor selection

6. **CFO or Board** approves final vendor and amount (if required by matrix)

7. **Purchase Order (PO)** issued by Procurement; Vendor fulfills

**Total cycle time**: $0–$5K (3–5 days); $5K–$100K (5–10 business days); >$100K (2–4 weeks, Board meeting cycle dependent)

## 4. Exceptions and Emergency Purchases

### 4.1 Business Continuity Emergency
If systems are down and purchasing a service/equipment is critical to restore operations:

1. **Verbal or email approval** from CFO (or VP if CFO unavailable)
2. **Document in Procurement**: Explain emergency, approver name, time
3. **Purchase immediately** to restore service
4. **Formal PO and approval** retroactively within 1 business day

Examples: Server failure requiring emergency hardware, security incident requiring incident response services.

### 4.2 Sole-Vendor Purchases
If only one vendor can fulfill the requirement (e.g., specific software license, patented service):

1. **Requestor documents** in Procurement request why sole-vendor is necessary
2. **VP Procurement** approves sole-vendor waiver
3. **Approval authority** proceeds as normal (Finance, VP, CFO as per matrix)

Sole-vendor approvals are tracked; Finance reviews annually to reduce vendor lock-in.

## 5. Approval Violations

### 5.1 Unauthorized Purchases
A purchase is **unauthorized** if:
- Obtained without required approval from the matrix
- Approver exceeded their authority (e.g., manager approved $50K without VP)
- Vendor is not on approved vendor list (for categories requiring vendor vetting)
- Budget is overspent in that cost center

### 5.2 Handling Unauthorized Purchases
1. **Finance identifies** in monthly reconciliation
2. **Finance notifies** requestor and manager
3. **Options**:
   - If possible, cancel or return (vendor reversal)
   - If already consumed, escalate to CFO for retroactive approval (rare)
   - Employee may be liable if personal benefit (e.g., expensing personal item as business purchase)

### 5.3 Repeated Violations
- **First**: Manager given verbal warning; approval authority reviewed
- **Second**: Manager written warning; approval authority suspended for 30 days
- **Third**: Escalated to HR; may result in termination for cause if egregious

## 6. Record Retention

All approval records, quotes, and POs are maintained in Procurement system for 7 years (IRS requirement). Finance Controller audits approval matrix compliance quarterly.

---

**Document owner:** VP Finance / Procurement  
**Last approved:** 2026-06-01 by Finance Leadership  
**Next review:** 2027-06-01

**Related policies:**
- **Procurement Thresholds & Competitive Bidding**: Multi-vendor requirements (defines WHAT to compare)
- **Capital Expenditure Policy**: Equipment and infrastructure purchases >$50K
- **Vendor Procurement & Third-Party Risk Policy**: Vendor security evaluation
- **Contractor & Consultant Payment Policy**: Approval for external personnel
