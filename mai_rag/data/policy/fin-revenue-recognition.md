---
title: Revenue Recognition Summary
doc_id: fin-revenue-recognition
owner: Finance Operations
last_updated: 2026-06-01
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Revenue Recognition Summary

## 1. Purpose and Overview

This policy establishes Northwind Technologies' revenue recognition practices in compliance with ASC 606 (the Financial Accounting Standards Board's revenue recognition standard). The policy ensures consistent, transparent reporting of revenue and related deferred revenue (liabilities).

This is a **summary for finance operations**; detailed accounting guidance is maintained by the Controller and external auditors.

## 2. Revenue Model and Contracts

### 2.1 Northwind's Revenue Streams

Northwind Technologies generates revenue from:

| Product | Revenue Type | Recognition Timing |
|---|---|---|
| **Northwind Cloud** (SaaS platform) | Subscription (monthly/annual) | Ratably over subscription period |
| **Professional Services** | Fixed-price projects or T&M (time & materials) | Milestone-based or T&M completion |
| **Support and Maintenance** | Subscription | Monthly, ratably |
| **Training and Onboarding** | Fixed-price services | Upon completion of deliverables |
| **Licenses** (perpetual or term) | Upfront or term-based | At license activation or over term |
| **Consulting** | T&M or fixed-price | Upon invoice or milestone completion |

### 2.2 Subscription Revenue (SaaS Model)

**Northwind Cloud** is the primary revenue driver (subscription SaaS):

- **Monthly subscriptions**: Customer pays $XXX/month for platform access; revenue recognized monthly
- **Annual subscriptions**: Customer pays $XXXX upfront for 12 months; revenue recognized ratably ($XXXX ÷ 12) each month
- **Multi-year contracts**: Customer pays upfront for 3 years; revenue recognized ratably over 36 months
- **Ancillary services** (add-ons, premium support): Separate performance obligations; recognized upon delivery

**Example**:
- Customer signs 12-month contract: $12,000 upfront (due immediately)
- Cash received: $12,000 (accounts receivable on invoice date)
- Initial liability (deferred revenue): $12,000
- Monthly revenue: $1,000/month
- After month 1: Deferred revenue = $11,000; month 2: $10,000; etc.

## 3. ASC 606 Revenue Recognition Framework

### 3.1 Five-Step Model

1. **Identify the contract** with customer (signed agreement, identified terms, collectible)
2. **Identify performance obligations** (distinct goods/services promised)
3. **Determine transaction price** (consideration customer will pay)
4. **Allocate transaction price** to performance obligations (if multiple, allocate using standalone selling prices)
5. **Recognize revenue** when (or as) performance obligation is satisfied

**Northwind application**:
- Most contracts are signed SaaS agreements (clear deliverable: platform access)
- Single or multiple performance obligations (e.g., platform + premium support)
- Transaction price is agreed contract amount (some contracts include variable consideration, e.g., usage-based pricing)
- Revenue recognized ratably (subscription) or at milestone completion (professional services)

### 3.2 Performance Obligations

**Performance obligation**: A promise to deliver a distinct good or service.

**Examples**:
- **SaaS platform access** = One performance obligation (recognized monthly over subscription term)
- **SaaS platform + professional services** = Two performance obligations:
  - Platform access (monthly, ratably)
  - Services (upon completion of deliverables or T&M performed)
- **Perpetual license + annual support** = Two performance obligations:
  - License (upfront, when activated)
  - Support (monthly, ratably over year)

Finance and Sales must document performance obligations clearly in contracts to ensure accurate revenue recognition.

## 4. Contract Review and Approval

### 4.1 New Contracts and Revenue Streams

New customer contracts (especially non-standard terms) must be reviewed by Finance:

1. **Sales team** submits contract to Finance before signature
2. **Finance/Controller** reviews:
   - Performance obligations (identify clearly)
   - Transaction price (fixed, variable, or contingent?)
   - Payment terms (upfront, Net 30, milestone-based?)
   - Refund/return rights (affects revenue recognition timing)
   - Multi-year or renewal terms
3. **Approval**: Controller approves revenue model; Legal approves contract terms
4. **Documentation**: Finance maintains contract copy and revenue recognition summary (in accounting system)

### 4.2 Variable Consideration and Constraints

**Variable consideration**: Revenue that depends on future events (e.g., usage-based pricing, performance bonuses, refunds).

- **Usage-based pricing**: Revenue recognized when usage occurs (may be estimated until final billing)
- **Performance bonuses or rebates**: Recognized only if probable and estimable; otherwise constrained (excluded until achievement certain)
- **Refunds and return rights**: Reduce revenue (liability); recognized as returned

**Constraint principle**: Variable consideration is included in transaction price only if it is probable that a significant reversal will not occur.

**Example**: Customer pays base fee $10K/year + $X per additional user (usage variable). Revenue recognized as:
- Base: $833/month (ratably)
- Usage: Estimated each month; trued up at year-end invoice

## 5. Deferred Revenue (Contract Liabilities)

### 5.1 Accounting for Deferred Revenue

**Deferred revenue** (liability) arises when:
- Cash is received before performance obligation is satisfied
- Common in subscription SaaS (annual contracts paid upfront)

**Accounting**:
- **Journal entry on cash receipt**: Debit Cash, Credit Deferred Revenue
- **Monthly revenue recognition**: Debit Deferred Revenue, Credit Revenue (as performance obligation is satisfied)

**Example**:
- January 1: Customer pays $12,000 for 12-month subscription
  - **Entry**: Debit Cash $12K, Credit Deferred Revenue $12K
- January 31: Month 1 revenue recognized
  - **Entry**: Debit Deferred Revenue $1K, Credit Revenue $1K
- (Repeat monthly through December)

### 5.2 Balance Sheet Reporting

**Deferred revenue** is reported as a current liability (short-term) if expected to be recognized within 12 months; long-term liability if >12 months.

**Monthly reporting**: Finance publishes deferred revenue balance; Finance Controller reviews for accuracy (aging, appropriate reclassification to revenue).

## 6. Revenue Adjustments and Corrections

### 6.1 Contract Modifications

If a customer contract is modified (added services, price change, extended term):

1. **Identify the modification** (amendment or change order)
2. **Determine accounting treatment**:
   - **Separate contract?** If the modification adds distinct goods/services at standalone price, treat as new contract
   - **Modification to existing contract?** If it's a change to existing terms, reassess performance obligations and transaction price
3. **Update revenue recognition** if needed

**Example**: Customer adds premium support ($2K/year) to existing $12K/year platform contract. This is a separate performance obligation; create new revenue stream for support (recognized ratably over new year).

### 6.2 Chargebacks and Credits

**Chargeback** (customer disputes invoice):
- Finance investigates; reconciles with customer
- If valid, issue credit memo (reduces revenue)
- If invalid, confirm billing and collect

**Refunds and credits**:
- Reduce revenue (via return/allowance or credit memo)
- Reduce customer receivable or deferred revenue

## 7. Accounts Receivable and Collectibility

### 7.1 Revenue Recognition and Collectibility

**ASC 606 requires**:
- Contract is probable of collection (customer can and will pay)
- If collectibility is not probable, defer revenue recognition until payment is received or collectibility becomes probable

**Northwind practice**:
- Most customer contracts are with creditworthy companies (creditworthiness assessed during contract negotiation)
- Credit limits may be imposed (e.g., don't exceed $1M outstanding invoice)
- Contracts with high-risk customers (startups, distressed companies) are scrutinized; may require prepayment

### 7.2 Allowance for Doubtful Accounts

Finance maintains an **allowance for doubtful accounts** (estimated uncollectible receivables):

- **Methodology**: Historical write-off rates by customer segment; forward-looking estimate of current/future credit risk
- **Monthly review**: Finance assesses accounts >60 days past due; may increase allowance or pursue collection

**Journal entry**:
- Debit Bad Debt Expense
- Credit Allowance for Doubtful Accounts

Uncollectible accounts are written off against the allowance.

## 8. Intercompany Revenue (Not Applicable Currently)

If Northwind acquires subsidiaries or creates business units, intercompany transactions must be eliminated in consolidated financial statements. This section is a placeholder for future multi-entity structure.

## 9. Segment Revenue Reporting

### 9.1 Revenue by Product and Geography

Finance reports revenue by:
- **Product/Service**: Northwind Cloud, Professional Services, Support, Training
- **Customer geography**: US, International
- **Customer segment**: Enterprise, Mid-market, SMB

This segmentation is used in:
- Monthly financial reports (CFO dashboard)
- Quarterly investor reports (Board and investors)
- Annual audit workpapers

## 10. Compliance and Audit

### 10.1 Revenue Documentation

Finance maintains supporting documentation for all revenue:
- Signed customer contracts
- Purchase orders (if applicable)
- Invoices and delivery proof (for services)
- Revenue recognition summary (transaction price, performance obligations, timing)
- Deferred revenue roll-forward (shows monthly revenue recognition)

These are reviewed during quarterly financial close and annual audit.

### 10.2 Auditor Review

External auditors (Big 4 or mid-tier) review revenue recognition during the annual audit:
- **Test revenue transactions**: Sample contracts; verify revenue is accurately recognized
- **Review contracts for unusual terms**: Look for performance obligations that might be misjudged
- **Verify deferred revenue**: Trace to underlying contracts; ensure roll-forward is accurate
- **Assess estimates**: Challenge variable consideration estimates and allowance for doubtful accounts

Finance must provide auditors with:
- Contract repository (database of all material contracts)
- Revenue recognition summary workpaper
- Deferred revenue analysis (aging, by customer, by contract)
- Accounts receivable aging
- Allowance for doubtful accounts calculation

---

**Document owner:** VP Finance / Controller  
**Last approved:** 2026-06-01 by Finance Leadership  
**Next review:** 2027-06-01

**Related policies:**
- **Invoice Processing & Accounts Payable**: Customer invoice and receivable management
- **Annual Budget Planning Process**: Revenue forecasting and planning
- **Expense Reimbursement Policy (Detailed)**: Related to expense allocation (internal) vs. revenue (external)
