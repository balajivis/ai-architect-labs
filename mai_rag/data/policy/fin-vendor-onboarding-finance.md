---
title: Vendor Onboarding (Finance & Procurement)
doc_id: fin-vendor-onboarding-finance
owner: Finance Operations
last_updated: 2026-06-01
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Vendor Onboarding (Finance & Procurement)

## 1. Overview

This policy outlines the financial and procurement process for onboarding new vendors at Northwind Technologies. Vendor onboarding includes security vetting (see **Vendor Procurement & Third-Party Risk Policy**), contract negotiation, and integration into accounts payable.

## 2. Vendor Onboarding Workflow

### 2.1 Pre-Onboarding (Evaluation Phase)

1. **Identify need**: Department head identifies vendor and submits procurement request
2. **Cost-benefit analysis**: Finance validates budget allocation and cost reasonableness
3. **Vendor selection**: 2–3 vendors evaluated per **Procurement Thresholds & Competitive Bidding**
4. **Security assessment**: If vendor processes customer data, VP Security completes assessment (see **Vendor Procurement & Third-Party Risk Policy**)
5. **Contract negotiation**: Legal and Finance negotiate terms (payment terms, liability, data handling, exit clause)

**Timeline**: 2–4 weeks

### 2.2 Approval Phase

1. **VP Procurement**: Recommends vendor based on cost, quality, and risk assessment
2. **Finance approval**: CFO or Finance Manager approves cost and contract terms
3. **Execution**: General Counsel (or authorized signatory) signs contract on behalf of Northwind

### 2.3 Activation Phase

1. **Procurement team**: Provides signed contract to vendor; requests:
   - W-9 form (for 1099 vendors/contractors)
   - ACH or payment details
   - Invoice submission instructions
   - Support contact information

2. **Finance team**: Sets up vendor in accounting system (Netsuite or equivalent):
   - Vendor name and ID
   - Payment method (ACH, check, credit card)
   - Payment terms (Net 30, Net 60, etc.)
   - Tax ID and W-9 on file
   - Approval authority for invoice payment
   - Cost center allocation

3. **Department owner**: Onboards vendor's tool/service:
   - User provisioning (access, licenses, seats)
   - Team training on tool usage
   - Integration with existing systems (if applicable)

## 3. Vendor Information and Compliance

### 3.1 Required Vendor Documentation

**For all vendors:**
- Company name, address, phone, email
- Primary contact and backup contact
- Tax identification number (EIN for US; VAT ID for international)
- W-9 form (1099 contractors) or W-8BEN (foreign persons)

**For data processing vendors:**
- Data Processing Addendum (DPA) signed
- SOC 2 Type II audit report (if applicable)
- Insurance certificate (cyber liability, E&O)
- Security questionnaire responses

**For SaaS vendors:**
- Service Level Agreement (SLA) with uptime/availability guarantees
- Pricing and licensing terms
- Renewal/cancellation terms
- Data backup and disaster recovery policy

### 3.2 Vendor Master File
Finance maintains a Vendor Master File in the accounting system with:
- Vendor ID and classification (SaaS, Contractor, Infrastructure, etc.)
- Payment terms and approved amount (single invoice limit)
- Budget code for cost allocation
- Tax documents (W-9, W-8BEN, EIN)
- Contract signed date and expiration
- Contact person and escalation path

## 4. Payment Terms and Conditions

### 4.1 Standard Payment Terms

| Vendor Type | Standard Terms | Notes |
|---|---|---|
| SaaS (monthly) | Net 30 | Monthly invoices; auto-renewal unless canceled |
| SaaS (annual) | Net 30 | Paid upfront at contract start |
| Infrastructure (AWS, Azure) | Net 30 | Auto-billed to corporate credit card |
| Professional Services | Net 30–60 | Depends on contract (hourly or fixed-price) |
| Contractors (1099) | Net 30 | Bi-weekly or monthly, per engagement |
| Office Supplies | Net 30 | Blanket PO with vendor; invoices submitted monthly |

**Negotiate favorable terms**: Procurement should negotiate discounts for:
- Annual upfront payment (typically 10% discount)
- Multi-year commitment (10–20% discount)
- Volume discounts (if applicable)
- Early payment discounts (2% 10 Net 30)

### 4.2 Payment Approval
All invoices are routed through accounts payable and must match:
- **PO amount**: Invoice amount matches approved PO
- **Invoice receipt**: Goods/services received or verified
- **Budget availability**: Cost center has remaining budget

See **Invoice Processing & Accounts Payable** for invoice approval workflow.

## 5. Annual Vendor Reviews

### 5.1 Annual Vendor Assessment

At least once per year (or on contract renewal), Finance and the department head review:

1. **Cost assessment**: Are we getting value for the price? Any discounts available?
2. **Usage assessment**: Is the tool/service being fully utilized?
3. **Performance**: Has vendor met SLA/support requirements?
4. **Security**: If data-processing vendor, has security posture changed? Any incidents?
5. **Renewal decision**: Continue, terminate, or renegotiate?

### 5.2 Termination and Offboarding
If a vendor is terminated:
1. **Notice**: Provide contract-required notice (typically 30–90 days)
2. **Data retrieval**: Request export of any company data per contract
3. **Access removal**: Disable user accounts and licenses
4. **Final invoice**: Reconcile and pay final invoice
5. **Contract closure**: Mark contract as "Closed" in vendor master file; archive documents

## 6. Vendor Performance Tracking

### 6.1 KPIs by Vendor Type

**SaaS vendors:**
- **Uptime**: Measured against SLA (typically 99.9%)
- **Support response time**: First response within agreed window (typically 4–24 hours)
- **Feature development**: Regular updates and security patches
- **Cost per user**: Track if seats increase/decrease

**Infrastructure providers (AWS, Azure):**
- **Availability**: Measured against SLA (typically 99.99%)
- **Cost per service**: Compare month-to-month; identify cost optimization opportunities
- **Support escalation time**: Critical issues resolved within RTO window
- **Security posture**: Regular penetration tests and vulnerability scans

**Professional services (legal, audit, consultants):**
- **Budget adherence**: Invoice costs match estimates
- **Delivery timeline**: Deliverables on schedule
- **Quality**: Stakeholder satisfaction and rework required
- **Billing accuracy**: No duplicate invoices or overages

### 6.2 Vendor Scorecards
Finance maintains quarterly vendor scorecards summarizing performance. Underperforming vendors (score <70%) are escalated to VP Procurement for renegotiation or termination.

## 7. Vendor Lock-In and Alternative Analysis

To reduce vendor lock-in, Finance should:

- **Document business case** for sole-vendor selections
- **Negotiate exit clauses**: Data export, transition services, API access
- **Explore alternatives annually**: Is there a better, cheaper option?
- **Standardize tools**: Avoid multiple tools performing the same function

Example: If using Salesforce as CRM, vet its export capabilities and ensure we can migrate data to a competing system within 90 days if needed.

---

**Document owner:** VP Finance / Procurement  
**Last approved:** 2026-06-01 by Finance Leadership  
**Next review:** 2027-06-01

**Related policies:**
- **Vendor Procurement & Third-Party Risk Policy**: Security assessment and DPA requirements
- **Procurement Thresholds & Competitive Bidding**: Multi-vendor evaluation
- **Invoice Processing & Accounts Payable**: Invoice approval workflow
- **Contractor & Consultant Payment Policy**: Contractor-specific onboarding
