---
title: Financial Controls & Segregation of Duties (SoD)
doc_id: fin-financial-controls-segregation-of-duties
owner: Finance Operations
last_updated: 2026-06-01
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Financial Controls & Segregation of Duties (SoD)

## 1. Purpose and Overview

This policy establishes financial controls and segregation of duties (SoD) at Northwind Technologies to prevent fraud, errors, and unauthorized transactions. No single person should have the ability to initiate, approve, and record a financial transaction without oversight or review.

## 2. Core Principles of Segregation of Duties

### 2.1 Four-Part Control Framework

Effective SoD separates responsibilities into four functions:

| Function | Role | Examples | Restriction |
|---|---|---|---|
| **Initiate** | Request/create transaction | Employee requests purchase, submits expense | Requestor cannot approve own request |
| **Approve** | Authorize transaction | Manager approves expense, VP approves purchase | Approver cannot be same as initiator |
| **Execute** | Process transaction | Finance pays invoice, vendor ships goods | Executor cannot be approver |
| **Record** | Document in accounting system | Controller records expense, accountant journals entry | Recorder cannot initiate, approve, or execute |

**Example**: Purchase order flow
- **Initiate**: Employee creates procurement request (need supplies)
- **Approve**: Manager approves request (budget available)
- **Execute**: Procurement team issues PO and receives goods
- **Record**: Finance accountant records invoice and payment in general ledger

**No one person does all four functions.**

### 2.2 SoD Exceptions (Unavoidable Overlap)

In small organizations, some SoD overlap is unavoidable. **Exceptions are documented and compensated by:**

- **Supervisory review**: Supervisor reviews transactions (e.g., controller reviews accountant's journal entries)
- **Audit trail**: All transactions logged; changes tracked (who, when, what)
- **Periodic reconciliation**: Management reconciles transactions (bank rec, vendor reconciliation)
- **Approval authority**: Clear limits (e.g., staff can execute <$1K transactions; VP approves >$5K)

## 3. Purchasing Cycle SoD

### 3.1 Purchase Authorization Controls

| Step | Owner | Control |
|---|---|---|
| **1. Requisition** | Department Manager | Prepares purchase request; includes business justification |
| **2. Approval** | Manager (and VP if >threshold) | Reviews and approves per **Purchase Approval Matrix** |
| **3. PO Generation** | Procurement Specialist | Issues PO to vendor; matches approved requisition |
| **4. Receipt** | Receiving/Warehouse | Confirms goods received; matches PO quantity/description |
| **5. Invoice Verification** | Finance (3-way match) | Invoice matches PO and receipt; no duplicates |
| **6. Payment Approval** | Finance Manager (and VP if >threshold) | Approves payment per invoice approval matrix |
| **7. Payment Processing** | AP Clerk (different from approver) | Processes ACH/check; executes payment |
| **8. Reconciliation** | Controller (separate from AP) | Monthly reconciliation of POs, invoices, payments |

**Key controls**:
- Requisitioner cannot approve >$1K
- Approver cannot also process payment
- Finance accountant cannot approve; only record/process

### 3.2 Vendor Master File Controls

| Action | Owner | Approval |
|---|---|---|
| **Add vendor** | Procurement | Finance Manager approves (no duplicates, no test accounts) |
| **Change payment method** | Finance | Manager approval required (prevent fraud) |
| **Change vendor address** | Finance | AP Manager approval required (detect address-swap fraud) |
| **Approve payment** | Finance Manager | Cannot be same person who entered vendor |
| **Process payment** | AP Clerk (different) | Cannot approve; only execute payment |

**Fraud prevention**: Two people must touch vendor master: someone adds/approves, someone else processes payment.

## 4. Expense and Travel Cycle SoD

### 4.1 Expense Submission Controls

| Step | Owner | Control |
|---|---|---|
| **1. Submit** | Employee | Uploads receipts; identifies business purpose |
| **2. Manager Review** | Manager | Reviews for policy compliance; approves |
| **3. Finance Audit** | Finance Specialist | Verifies receipt requirement, budget, three-way match |
| **4. Finance Approval** | Finance Manager (if >threshold) | Approves reimbursement |
| **5. Reimbursement Processing** | Payroll (different from approver) | Processes to paycheck or direct deposit |

**Key controls**:
- Employee cannot approve own expense
- Finance cannot both audit and approve (separate eyes)
- Payroll processing is separate from approval

### 4.2 Travel Approval Controls

| Step | Owner | Approval |
|---|---|---|
| **1. Travel Request** | Employee | Submits in Expensify |
| **2. Manager Approval** | Manager | Approves travel dates and budget |
| **3. VP Approval** | VP (if >$2,000) | Reviews and approves for policy compliance |
| **4. Finance Approval** | Finance | Verifies budget; approves booking |
| **5. Booking** | Employee (or travel agent) | Books after all approvals |
| **6. Reimbursement** | Finance | Processes expense and reimbursement |

**Key control**: Employee cannot book until all approvals are received (prevents unauthorized travel).

## 5. Payroll and HR Cycle SoD

### 5.1 Payroll Processing Controls

| Step | Owner | Control |
|---|---|---|
| **1. Employee data changes** | HR | Updates salary, deductions, tax withholding |
| **2. Approval** | HR Manager | Reviews changes for accuracy |
| **3. Payroll data entry** | Payroll Administrator | Inputs approved changes into payroll system |
| **4. Payroll calculation** | Payroll System (automated) | Calculates gross, taxes, deductions, net pay |
| **5. Review and approval** | Finance Manager (or VP) | Reviews payroll report for anomalies |
| **6. Payment processing** | Finance (different from reviewer) | Submits to bank for ACH deposits |
| **7. Reconciliation** | Controller (independent) | Monthly reconciliation of payroll to GL |

**Key controls**:
- HR cannot directly run payroll (separation)
- Payroll approver cannot process payment (separation)
- Finance reconciles (independent verification)
- Audit trail: All changes logged (who, when, what)

### 5.2 Termination Controls

When an employee is terminated:
- **HR** notifies Payroll, Finance, IT, and Security simultaneously
- **Payroll** removes from payroll; no final paycheck processed without HR certification
- **Finance** processes final expense reimbursement (separate from regular payroll)
- **IT** disables access within 1 business day
- **Security** escalates if departing employee had sensitive access

## 6. Journal Entry and General Ledger SoD

### 6.1 Journal Entry Controls

| Type | Approval Required |
|---|---|
| **Routine entries** (<$10K, normal accounts) | Department Manager or Finance Supervisor |
| **Large entries** ($10K–$100K) | Finance Manager or VP |
| **Material adjustments** (>$100K, unusual accounts) | CFO |
| **Period-end close entries** (accruals, reversals) | Controller |

**Restriction**: Staff accountant cannot:
- Approve own entries
- Override automated controls
- Create entries to discretionary accounts (reserve, contingency) without approval

### 6.2 General Ledger Access Controls

| Role | Access Level | Restrictions |
|---|---|---|
| **Staff Accountant** | Create, review (own work only) | Cannot approve; cannot delete |
| **Finance Manager** | Create, approve, delete (non-sensitive accounts) | Cannot approve >$100K without CFO |
| **Finance Controller** | Full access (all accounts, all users) | Reviews monthly for anomalies |
| **VP Finance / CFO** | Full access (audit trail, override logs) | Reviews irregular transactions |

**Audit trail**: All GL changes logged; reports generated monthly for management review.

## 7. Cash and Bank Controls

### 7.1 Bank Reconciliation (Independent Control)

**Monthly bank reconciliation is critical; assigned to person with NO prior involvement:**

| Role | Action | Restriction |
|---|---|---|
| **AP Clerk** | Processes payments (ACH, checks) | Cannot reconcile |
| **Controller or Senior Accountant** | Performs bank reconciliation | Does not approve payments |
| **Finance Manager** | Reviews reconciliation | Reviews for completeness and accuracy |

**Reconciliation procedure**:
1. Obtain bank statement from bank (not from company system)
2. Match clearing transactions in bank to company GL
3. Identify uncleared items (in-transit checks, pending ACH)
4. Investigate differences >$100 (possible errors or fraud)
5. Document and approve when reconciled

**Key control**: If AP clerk processes payments, they cannot reconcile (would hide their own errors/fraud).

### 7.2 Check Signing Controls

| Control | Details |
|---|---|
| **Check signatories** | Designated signatories only (typically VP Finance, CFO, CEO); limited to 2 signatures |
| **Blank check security** | Locked in safe; access restricted |
| **Check stock control** | Serial number tracking; spoiled checks marked VOID |
| **Check log** | Record of all checks issued; matched to GL |
| **Dual signature** | Checks >$25K require two signatures (VP Finance + CFO) |
| **Positive pay** | Company submits check list to bank; bank verifies checks before cashing |

## 8. Approval Authorities (By Amount)

### 8.1 Purchase Orders and Expenses

| Amount | Authority | Notes |
|---|---|---|
| $0 – $1K | Department Manager | Receipt/invoice only |
| $1K – $5K | Manager + Finance | Procurement request + quote |
| $5K – $25K | VP + Finance | 2 quotes required |
| $25K – $100K | CFO + VP Procurement | 3 quotes + vendor evaluation |
| >$100K | CFO + CEO or Board | Full due diligence |

No person may unilaterally approve any purchase (two-person rule).

### 8.2 Journal Entries and Accruals

| Amount | Approver |
|---|---|
| $0 – $10K | Finance Manager or Supervisor |
| $10K – $100K | Finance Manager or VP |
| >$100K | CFO or Board approval (if policy-sensitive) |

## 9. Reconciliation and Monitoring Controls

### 9.1 Monthly Reconciliations

| Reconciliation | Owner | Frequency |
|---|---|---|
| **Bank reconciliation** | Controller or Senior Accountant | Monthly (before close) |
| **Credit card reconciliation** | Finance Manager | Monthly (with department managers for approval) |
| **Accounts receivable aging** | AR Specialist | Monthly |
| **Accounts payable aging** | AP Manager | Monthly |
| **Inventory reconciliation** | Warehouse Manager | Monthly or quarterly |
| **GL trial balance review** | Finance Manager | Monthly (before closing) |

### 9.2 Variance Analysis

Finance performs **variance analysis** monthly:
- **Budget vs. actual**: Each department compares spending to budget
- **Prior year comparison**: Current month vs. same month last year
- **Trend analysis**: 3-month rolling average (detect changes)

Variances >10% are investigated; explained by department managers. Large variances (>20%) escalated to VP Finance.

## 10. Audit Trail and System Controls

### 10.1 User Access Controls

| Control | Description |
|---|---|
| **Unique user IDs** | Each employee has unique login; no shared accounts |
| **Password policy** | 12-character minimum; no forced rotation; change only if compromised |
| **Multi-factor authentication (MFA)** | Required for VPN access; TOTP or hardware key preferred |
| **Role-based access (RBAC)** | Users granted permissions matching their role (manager can approve ≤$5K; CFO can approve all) |
| **Inactive account deactivation** | Accounts disabled after 60 days of inactivity |
| **Termination access removal** | Deactivated within 1 business day of departure |

### 10.2 Audit Trail and Logging

System logs all financial transactions:
- **Who**: User ID and name
- **What**: Transaction type, amount, account
- **When**: Date and time
- **Why**: Note or description
- **Changes**: If edited, log shows original and revised values

**Retention**: Audit trails retained for 7 years per IRS and audit requirements.

### 10.3 System Exceptions and Overrides

**Critical control**: Any override of automated approvals or exceptions is:
- **Logged** (who, when, what, why)
- **Reviewed** monthly by Finance Manager
- **Escalated** if excessive (e.g., >5 overrides/month)
- **Explained** (documented business justification)

Examples of overrides:
- Approving expense after 90-day deadline
- Paying invoice that doesn't match PO (3-way match exception)
- Manually adjusting GL entry after posting (should not happen; indicates control gap)

## 11. Fraud Detection and Investigation

### 11.1 Fraud Risk Indicators

Finance monitors for suspicious patterns:
- **Vendor red flags**: New vendors with highest spend; vendors added/edited right before large payments
- **Employee red flags**: Expenses submitted after hours; frequent exceptions; unusual patterns
- **System red flags**: Failed logins; access outside normal hours; data exports

Monthly, Finance Manager reviews exception logs and escalates concerns to VP Finance and General Counsel.

### 11.2 Investigation Process

If fraud is suspected:
1. **Preserve evidence**: Secure transaction records; do not alert suspect
2. **Notify Legal and HR**: General Counsel and HR Director are informed
3. **Investigate**: Finance and Internal Audit (if available) investigate
4. **Document findings**: Evidence collected; findings documented
5. **Escalate**: If substantiated, escalate to CEO and Board; involve law enforcement if criminal

**No retaliation**: Employees who report suspected fraud are protected from retaliation.

## 12. Annual SoD Assessment

Finance conducts annual assessment of SoD effectiveness:
- **Gaps**: Are there any functions not segregated (due to size, system limitations)?
- **Mitigating controls**: If segregation impossible, are compensating controls adequate?
- **Recommendations**: Improvements to reduce risk

Results presented to Audit Committee (Board) annually.

---

**Document owner:** VP Finance / Controller  
**Last approved:** 2026-06-01 by Finance Leadership  
**Next review:** 2027-06-01

**Related policies:**
- **Purchase Approval Matrix**: Approval authorities (who approves)
- **Invoice Processing & Accounts Payable**: Invoice processing controls
- **Expense Reimbursement Policy (Detailed)**: Expense approval controls
- **Information Security Policy**: User access and authentication controls
