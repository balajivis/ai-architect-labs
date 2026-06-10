---
title: Invoice Processing & Accounts Payable
doc_id: fin-invoice-processing-accounts-payable
owner: Finance Operations
last_updated: 2026-06-01
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Invoice Processing & Accounts Payable

## 1. Purpose and Scope

This policy governs the receipt, validation, approval, and payment of vendor invoices at Northwind Technologies. All invoices must be properly documented, match purchase orders, and comply with payment terms before payment is authorized.

## 2. Invoice Receipt and Entry

### 2.1 Invoice Submission Methods

Vendors submit invoices via:
- **Email**: vendor-invoices@northwind.com
- **Portal**: AP portal in accounting system (Netsuite)
- **Paper mail**: Finance office (slower; not recommended)

**Best practice**: Request vendors submit invoices electronically and in PDF format.

### 2.2 Invoice Entry Process

1. **Accounts Payable (AP) team** receives invoice and creates record in accounting system:
   - Invoice number and date
   - Vendor name and ID
   - Invoice amount and currency
   - Description of goods/services
   - PO number (if applicable)

2. **Three-Way Match** verification:
   - **PO match**: Invoice amount and description match approved purchase order
   - **Receipt match**: Goods received or services delivered per receipt (PO acknowledgment)
   - **Invoice match**: Invoice accurately reflects PO terms (price, quantity, payment terms)

3. **If exceptions exist**: AP team holds invoice and notifies requestor/manager for resolution

### 2.3 Escalation Process for Three-Way Match Exceptions

| Exception | Owner | Resolution |
|---|---|---|
| **Amount variance** (invoice ≠ PO by >5%) | AP Manager | Confirm with vendor; issue debit memo or credit memo if error |
| **Quantity variance** (goods short-shipped) | Department Lead + Vendor | Reconcile shipment; receive balance or issue return |
| **Description mismatch** | Department Lead | Confirm goods match PO description; approve if acceptable |
| **PO missing** (invoice has no PO) | Requestor | Confirm expense is valid; create PO retroactively if needed |
| **Unauthorized vendor** | Finance Manager | Review; reject if vendor not approved; escalate if disputed |

**Resolution timeline**: 3–5 business days; invoices held in "On Hold" status pending resolution.

## 3. Invoice Approval Workflow

### 3.1 Approval Authority by Amount

| Invoice Amount | Approver(s) | Time to Approve |
|---|---|---|
| $0 – $999 | Department Manager only | 1 business day |
| $1,000 – $4,999 | Department Manager + Finance | 2 business days |
| $5,000 – $24,999 | VP (Department) + Finance | 2 business days |
| $25,000 – $99,999 | CFO + VP Procurement | 3 business days |
| $100,000 + | CFO + CEO or Board approval | 5 business days |

**Sequential approval**: Each level must approve before the invoice moves to the next (no skipping).

### 3.2 Approval Process in Accounting System

1. **AP team** routes invoice to department manager for approval
2. **Department manager** verifies in system:
   - Goods received or service delivered
   - Invoice amount is reasonable
   - Expense is legitimate (not personal or duplicate)
3. **Manager approves** with comment (if needed); invoice routes to Finance
4. **Finance reviewer** (Finance Manager or Controller) verifies:
   - Budget available in cost center
   - Vendor is approved (security vetted if needed)
   - Payment terms match contract
5. **Finance approves** or escalates to CFO if unusual
6. **CFO or VP** (if required by amount) approves

### 3.3 Approval Criteria

Approver must confirm:
- [ ] Goods/services were received or performed
- [ ] Invoice matches PO (amount, description, quantity)
- [ ] Business purpose is clear and legitimate
- [ ] No duplicate invoices have been submitted
- [ ] Vendor is authorized and properly vetted
- [ ] Budget is available

**Rejecting an invoice**: If approver rejects, they must provide reason and route back to vendor or requestor for correction.

## 4. Payment Processing and Timing

### 4.1 Payment Methods

Northwind uses the following payment methods:
- **ACH transfer** (preferred): Bank-to-bank electronic transfer; fastest processing
- **Check**: Mailed payment; slower; used if vendor cannot accept ACH
- **Credit card**: Corporate card (auto-billed to Finance); used for small recurring expenses
- **Wire transfer**: International vendors; higher fees; used only if ACH unavailable

### 4.2 Payment Timing

All invoices are paid according to contract terms:

| Terms | Example | Payment Date |
|---|---|---|
| **Net 30** | Invoice 6/1, approved 6/2 | Payment by 7/1 |
| **Net 60** | Invoice 6/1, approved 6/2 | Payment by 8/1 |
| **2/10 Net 30** | Invoice 6/1, approved 6/2 | Pay by 6/11 (2% discount) or 7/1 (full) |

**Early payment discount**: If vendor offers 2% discount for payment within 10 days, Finance evaluates:
- Cash flow impact (can we afford to pay early?)
- Discount value (2% on $100K = $2K savings, worth it)
- AP processing time (can we approve and pay within 10 days?)

Finance may pre-approve early payment for qualified vendors.

### 4.3 Payment Batch Processing

Approved invoices are batched and paid:
- **Frequency**: 2x per week (Tuesdays and Thursdays, standard)
- **Batch deadline**: Invoices must be fully approved by 2pm day before payment batch
- **Notification**: Requestor receives email confirmation once payment is submitted

**Payment reconciliation**: AP team reconciles bank statements weekly; resolves discrepancies within 3 business days.

## 5. Disputed Invoices and Debit Memos

### 5.1 Dispute Process

If an invoice is challenged:

1. **Requestor notifies** AP team with reason (e.g., duplicate, overcharge, goods defective)
2. **AP places hold** on invoice; escalates to vendor
3. **Vendor response**: Within 5 business days, vendor provides explanation or corrected invoice
4. **Resolution**:
   - **Agree on correction**: Vendor issues credit memo or corrected invoice; AP processes
   - **Dispute**: If unresolved, escalate to Finance Manager or department VP
   - **Legal review**: If amount is significant (>$10K), General Counsel may review

### 5.2 Debit and Credit Memos

- **Credit memo**: Issued by vendor if they overcharged or goods were defective; reduces future invoices or generates refund
- **Debit memo**: Issued by Northwind if vendor undercharged; requests additional payment (rare)

Both must be matched to original invoice and processed through AP.

## 6. 1099 and W-9 Contractor Invoices

For contractors and consultants paid via 1099 (Form 1099-NEC):

- **W-9 on file**: Must have valid W-9 signed before first payment
- **Invoice template**: Contractor submits invoice (contractor's own invoice template acceptable)
- **Approval**: Department manager and Finance approve as normal
- **1099 tracking**: Finance maintains 1099 records; contractors >$600/year are reported to IRS
- **Tax withholding**: None (contractor responsible for self-employment tax)

See **Contractor & Consultant Payment Policy** for detailed contractor guidelines.

## 7. Recurring Invoices and Subscriptions

For monthly or annual SaaS subscriptions:

- **Setup recurring invoice**: Vendor submits first invoice; AP sets up recurring payment schedule
- **Monthly auto-payment**: Recurring invoices are auto-approved if:
  - Invoice matches prior month amount (within 2% variance)
  - Vendor is active and current
  - PO is current and not yet expensed
- **Annual renewal**: If invoice includes renewal, department manager must re-approve (confirm continued need)
- **Cancellation**: Department notifies Finance ≥30 days before renewal; AP cancels auto-payment

## 8. Month-End Close and Accruals

### 8.1 Accrual Process

At month-end, Finance accrues (records) invoices that are expected but not yet received:

- **Recurring invoices** (e.g., cloud services): Estimated based on prior months
- **Waiting invoices**: If goods received but vendor hasn't yet invoiced, AP estimates and accrues

Accruals are reversed when actual invoice is received.

### 8.2 Invoice Aging Report

Monthly, AP produces an aging report:
- **Current**: Invoices 0–30 days old
- **30–60 days**: Past due invoices (likely vendor hasn't invoiced yet or missing docs)
- **60+ days**: Very overdue (escalate to Finance Manager)

Overdue invoices are investigated; Finance may contact vendor to resubmit.

## 9. Record Retention and Audit

All invoices, supporting documents (PO, receipt), and payment records are retained for 7 years per IRS and audit requirements. Finance maintains:
- Scanned invoice images (PDF)
- Payment confirmation (bank statement, ACH receipt)
- Approval audit trail (system log of approvers and dates)

Quarterly, internal audit reviews invoice processing for:
- Approval compliance (all invoices properly approved)
- Three-way match exceptions (authorized exceptions only)
- Duplicate payments (none detected)
- Policy violations (e.g., payment outside terms)

---

**Document owner:** VP Finance / Controller  
**Last approved:** 2026-06-01 by Finance Leadership  
**Next review:** 2027-06-01

**Related policies:**
- **Purchase Approval Matrix**: Approval authority by amount
- **Contractor & Consultant Payment Policy**: 1099 vendor invoices
- **Vendor Onboarding (Finance & Procurement)**: Vendor setup and payment terms
