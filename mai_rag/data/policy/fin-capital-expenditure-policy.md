---
title: Capital Expenditure Policy
doc_id: fin-capital-expenditure-policy
owner: Finance Operations
last_updated: 2026-06-01
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Capital Expenditure Policy

## 1. Purpose and Scope

This policy governs the approval, procurement, and accounting of capital expenditures (CapEx) at Northwind Technologies. Capital assets are long-lived items (useful life >1 year) that are capitalized on the balance sheet and depreciated over time, as opposed to operating expenses (OpEx) that are expensed in the current period.

## 2. Capital vs. Operating Expense Classification

### 2.1 Capital Expenditure (CapEx)

**CapEx** are purchases of items that:
- Have **useful life > 1 year**
- Cost >**$5,000** (single item or project)
- Provide ongoing benefit to the company (equipment, infrastructure, leasehold improvements)
- Are capitalized on the balance sheet and depreciated

**Examples**:
- Server hardware, storage arrays, networking equipment
- Office furniture and fixtures
- Leasehold improvements (renovations, buildouts)
- Software licenses (multi-year, site licenses)
- Company vehicles and transportation equipment
- Research and development equipment

### 2.2 Operating Expense (OpEx)

**OpEx** are purchases that:
- Have **useful life ≤ 1 year** (consumable, recurring)
- Cost <**$5,000** (standard threshold)
- Are expensed in the current period (not capitalized)

**Examples**:
- Office supplies (pens, paper, desk accessories)
- Monthly/annual SaaS subscriptions (renewed yearly)
- Repairs and maintenance (routine)
- Travel and entertainment
- Professional services (legal, consulting)
- Utilities and facilities (rent, electricity)

### 2.3 Gray Area and Capitalization Policy

**Items borderline $5K threshold:**
- If item costs $4,800 but expected to last 3+ years → Likely CapEx; capitalize
- If item costs $5,200 but replaced annually → Likely OpEx; expense
- **Decision rule**: Economic substance (will this benefit >1 year?) overrides amount threshold

**Bundled purchases**: If multiple items are purchased as one project:
- Total project cost determines classification (e.g., office renovation with furniture, painting, fixtures bundled as one project for CapEx review)
- Not itemizing to avoid CapEx threshold (e.g., buying 10x $490 keyboards = $4,900 to stay under $5K) is prohibited

## 3. CapEx Approval Authority

### 3.1 Approval Matrix by Amount

| CapEx Amount | Approver(s) | Documentation |
|---|---|---|
| $5,000 – $49,999 | Department Manager + Finance | Project justification + cost estimate |
| $50,000 – $99,999 | VP (Department) + CFO | Business case + ROI analysis + vendor quotes |
| $100,000 – $250,000 | CFO + CEO | Full business case + ROI + Board agenda item |
| Over $250,000 | Board of Directors | Strategic review + full due diligence + Board vote |

**Sequential approval**: Each level must approve before escalation (no skipping).

### 3.2 CapEx Request Process

1. **Requestor submits CapEx proposal** to Finance with:
   - **Business justification**: Why is this CapEx needed? What problem does it solve?
   - **Cost estimate**: Equipment cost, installation, training, ongoing support (3+ year horizon)
   - **Vendor analysis**: 2–3 vendor quotes (see **Procurement Thresholds & Competitive Bidding** for multi-vendor rules)
   - **ROI or payback analysis** (if >$50K):
     - Cost savings or revenue impact
     - Payback period (how long to recover cost)
     - Example: Server upgrade costs $80K, reduces cloud spend by $30K/year → Payback in 2.7 years
   - **Useful life estimate**: Expected years of operation (3, 5, 7, 10 years?)
   - **Depreciation calculation**: Annual depreciation = cost ÷ useful life

2. **Finance reviews** for:
   - Capitalization vs. expensing (is this really CapEx?)
   - Useful life estimate (reasonable?)
   - Vendor assessment (approved vendors only for high-risk categories)
   - Impact on annual budget (does this fit in CapEx plan from Annual Budget Planning Process?)

3. **Approvers approve** in sequence (Department Manager → VP → CFO → CEO/Board as needed)

4. **Approved CapEx** is added to capital asset register; Finance tracks depreciation

## 4. CapEx vs. Lease (Finance Lease Decision)

If acquiring long-life assets, Finance must decide: **Buy (CapEx) or Lease?**

### 4.1 Build vs. Buy Decision

For infrastructure or facilities:

| Decision | Use Case | Approval |
|---|---|---|
| **Buy (CapEx)** | Long-term stable need; know we'll use >3 years | CapEx approval per matrix |
| **Lease (OpEx)** | Flexible, short-term, or uncertain need | Operating lease; lower approval threshold |
| **Cloud (OpEx subscription)** | Scalable, consumption-based; e.g., AWS | Monthly OpEx; department budget authority |

**Example 1**: Building permanent office HQ → Buy/lease building (both capitalized or lease obligation)
**Example 2**: Temporary 6-month office space for project team → Lease month-to-month (operating expense)
**Example 3**: Need compute infrastructure → Cloud (AWS/Azure) usually OpEx; buy only if long-term and economical

### 4.2 Lease vs. Buy Financial Analysis

Finance evaluates:
- **Total cost of ownership** (buy): Purchase price + maintenance + depreciation tax benefits
- **Lease cost** (operating): Monthly/annual lease payments + cancellation penalties
- **Flexibility**: Can we easily exit a lease if business changes?
- **Obsolescence**: Will technology be obsolete before end of useful life? (Accelerates buy decision for equipment)

For equipment >$100K, Finance calculates both scenarios and recommends optimal option.

## 5. Annual CapEx Planning

CapEx is planned as part of **Annual Budget Planning Process**:

- **CapEx budget**: Established in July–August for following year
- **Discretionary vs. mandatory CapEx**:
  - **Mandatory**: Security upgrades, disaster recovery infrastructure, compliance requirements → Must be funded
  - **Discretionary**: Nice-to-have upgrades, expansions, new initiatives → Funded if budget allows
- **Prioritization**: If total requested CapEx exceeds budget, Finance/CEO prioritize by ROI or strategic importance
- **Quarterly reviews**: Finance reviews actual CapEx spending vs. budget; reallocates if needed

## 6. CapEx Procurement and Vendor Management

### 6.1 Procurement Process

CapEx purchases follow **Purchase Approval Matrix** and **Vendor Onboarding (Finance & Procurement)**:

1. **RFQ (Request for Quote)**: ≥2 quotes for items <$100K; ≥3 quotes for >$100K
2. **Vendor evaluation**: Cost, quality, delivery time, support SLA, security (if applicable)
3. **Negotiation**: Finance/Procurement negotiates best price and terms
4. **Order placement**: PO issued once approval is final
5. **Receipt and inspection**: Goods received; inspected for quality/damage
6. **Asset registration**: Finance adds to capital asset register

### 6.2 Asset Tagging and Tracking

All CapEx items >$5K must be tagged with:
- **Asset tag number** (barcode, RFID, or sequential)
- **Description** (model, serial number, key specs)
- **Purchase date and cost**
- **Useful life and depreciation schedule**
- **Location** (office, data center, employee home office)
- **Owner/custodian** (employee responsible for asset)

Annual inventory verification ensures all tagged assets are accounted for (audit requirement).

## 7. Depreciation and Useful Life Estimates

### 7.1 Depreciation Schedule

| Asset Category | Typical Useful Life | Annual Depreciation Method |
|---|---|---|
| **Computer hardware** (servers, desktops) | 3 years | 33% straight-line |
| **Networking equipment** | 5 years | 20% straight-line |
| **Office furniture and fixtures** | 7 years | 14% straight-line |
| **Software licenses** (capitalized multi-year) | 3–5 years | Depends on term |
| **Vehicles** | 5 years | 20% straight-line |
| **Leasehold improvements** | 5 years or lease term | Lesser of lease/useful life |
| **Building and real estate** | 39 years | 2.6% straight-line |

**Straight-line depreciation**: Annual depreciation expense = (Cost − Salvage value) ÷ Useful life

**Example**: Server costs $60K; useful life 5 years; salvage value $5K
- Annual depreciation = ($60K − $5K) ÷ 5 = $11K/year
- Year 1–5: $11K expensed each year

### 7.2 Impairment and Disposal

If a CapEx asset is damaged, obsolete, or no longer useful:
- **Impairment charge**: If book value >fair market value, write down to FMV (one-time loss)
- **Disposal**: Remove from capital asset register; realize gain/loss on sale
- **Salvage**: If sold for scrap, proceeds offset remaining book value

## 8. CapEx Accountability and Controls

### 8.1 Project Tracking

CapEx projects >$50K are tracked in a project management system:
- **Budget vs. actual**: Monthly reporting of spending vs. approved budget
- **Schedule**: Expected completion date; actual completion date
- **Variance analysis**: If budget overrun >10%, Finance investigates

### 8.2 Post-Implementation Review

After project completion, Finance conducts a **post-implementation review (PIR)**:
- Did project stay on budget? (If not, why overrun?)
- Did project stay on schedule?
- Was ROI achieved? (For projects with financial ROI targets)
- Lessons learned for future projects

CapEx projects with significant variances (>20%) are escalated to CFO and Board.

## 9. Tax Implications

Finance considers tax implications of CapEx:
- **Section 179 deduction**: May allow immediate deduction of certain equipment (instead of depreciation)
- **Bonus depreciation**: Allows accelerated depreciation for certain asset types
- **Tax credits**: Research credits for R&D equipment; energy credits for efficient equipment
- **COGS vs. OpEx**: Some CapEx is allocated to cost of goods sold (COGS) for product development

Finance and Tax advisor collaborate on tax-optimal CapEx structure.

---

**Document owner:** VP Finance / CFO  
**Last approved:** 2026-06-01 by Finance Leadership  
**Next review:** 2027-06-01

**Related policies:**
- **Annual Budget Planning Process**: CapEx budget planning and prioritization
- **Purchase Approval Matrix**: Approval authority for CapEx purchases
- **Procurement Thresholds & Competitive Bidding**: Multi-vendor requirements for CapEx
- **Vendor Onboarding (Finance & Procurement)**: Vendor selection and management
