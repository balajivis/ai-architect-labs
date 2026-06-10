---
title: Insurance & Liability Overview
doc_id: legal-insurance-liability-overview
owner: Legal & Risk
last_updated: 2026-06-09
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Insurance & Liability Overview

## Purpose
This document provides an overview of Northwind Technologies' insurance portfolio, coverage limits, deductibles, and claims procedures. Insurance protects Northwind against catastrophic risk while enabling compliance with contractual requirements.

## 1. Active Insurance Policies

| Policy | Type | Insurer | Limit | Deductible | Renewal Date |
|---|---|---|---|---|---|
| **General Liability** | CGL | Travelers Insurance | $2,000,000 | $25,000 | 2026-12-31 |
| **Cyber Liability & Data Breach** | Cyber | Chubb | $5,000,000 | $100,000 | 2026-12-31 |
| **Professional Liability (E&O)** | Errors & Omissions | XL Specialty Insurance | $3,000,000 | $50,000 | 2026-12-31 |
| **Directors & Officers** | D&O | Chubb | $10,000,000 | $250,000 | 2026-12-31 |
| **Employment Practices Liability** | EPLI | Chubb | $1,000,000 | $50,000 | 2026-12-31 |
| **Property (Buildings & Equipment)** | Property | Travelers | $20,000,000 | $50,000 | 2026-12-31 |
| **Workers Compensation** | WC | Texas Mutual | Statutory | $0 (WC) | 2026-12-31 |

## 2. Coverage Details

### General Liability (CGL)
**What it covers**: Bodily injury, property damage, and personal injury claims from third parties.

**Examples**:
- Customer slips on Northwind office floor → bodily injury claim
- Northwind employee accidentally damages customer equipment → property damage
- Northwind accused of libel in a press release → personal injury

**Exclusions**: Intellectual property infringement, contractual liability, and professional services (covered by E&O policy).

### Cyber Liability & Data Breach
**What it covers**: Data breach response, regulatory defense, extortion, and business interruption from cyber incidents.

**Includes**:
- Forensic investigation and incident response (up to $500K)
- Legal defense for regulatory investigations (GDPR fines, CCPA penalties)
- Credit monitoring for affected individuals (up to $250K)
- Business interruption if Northwind Cloud is down due to covered cyber incident
- Ransomware extortion defense and negotiation

**Exclusions**: War, terrorism (covered only if also ordinary commercial tort). Prior known vulnerabilities.

**Claims procedure**: Immediate notification to Chubb and General Counsel if data breach is suspected (see **Incident Response Runbook** for escalation).

### Professional Liability (E&O)
**What it covers**: Claims from customers that Northwind's services caused financial loss.

**Examples**:
- Customer claims Northwind Cloud data integration failed, causing business losses
- Customer claims Northwind failed to deliver contracted feature set, resulting in lost revenue
- Regulatory claim that Northwind's advisory service was negligent

**Limits per claim**: $3M per occurrence; $6M aggregate.

**Exclusions**: Intentional fraud, criminal acts, known design defects.

### Directors & Officers (D&O)
**What it covers**: Personal liability of directors and officers for alleged wrongful acts.

**Examples**:
- Shareholder derivative suit claiming mismanagement
- SEC investigation into officer conduct
- Employment-related claims against officers

**Limit**: $10M per claim; $20M aggregate. Protects directors and officers personally as well as the company as indemnitee.

### Employment Practices Liability (EPLI)
**What it covers**: Employment-related claims (wrongful termination, discrimination, harassment, wage disputes).

**Examples**:
- Employee claims illegal termination
- Discrimination claim (race, gender, age, disability, religion)
- Sexual harassment or hostile work environment
- Wage & hour violation (unpaid overtime)

**Limit**: $1M per claim; $2M aggregate.

### Property Insurance
**What it covers**: Northwind's office building, furniture, equipment, and inventory in case of fire, theft, natural disaster, etc.

**Locations covered**: Austin HQ building (owned by Northwind).

**Subrogation**: If Northwind recovers from a third-party tortfeasor, insurer has right to recover deductible + claim amount.

### Workers Compensation
**What it covers**: Medical expenses and lost wages for employees injured on the job.

**Statutory coverage**: Texas requires coverage for all employees. Northwind maintains statutory limits with no cap on medical benefits.

**Exclusions**: Injuries occurring while commuting to/from work (not covered); intentional self-injury.

## 3. Contractual Insurance Requirements

**Vendor insurance** (see **Master Services Agreement (MSA) Standard**):
- General Liability: $1M minimum
- Cyber/Data Breach: $2M minimum (if vendor handles Confidential/Restricted data)
- Workers Compensation: Statutory

**Customer contracts** may require Northwind to maintain insurance. Standard language:
> "Northwind shall maintain general liability ($2M), cyber liability ($5M), and professional liability ($3M) insurance throughout the term. Certificates of insurance available upon request."

## 4. Claims Procedures

### Claim Notification
**Immediate** (within 24 hours):
1. Report incident to General Counsel
2. General Counsel notifies CFO and insurance broker (Marsh USA)
3. Do not admit liability or make settlement offers

**Within 5 business days**:
1. Formal claim submission to insurer with incident description, damage estimate, and witness statements
2. Assign claim adjuster
3. Insurer opens claim file and assigns claim number

### Investigation & Defense
- Insurer appoints defense counsel if litigation anticipated
- Northwind cooperates fully with insurer and defense counsel
- Decisions to settle (above $50K) require insurer + General Counsel approval
- Large claims ($500K+) escalate to CEO + Board Finance Committee

### Subrogation & Recovery
- If Northwind recovers from a third-party tortfeasor, insurer's subrogation rights apply
- Insurer recoups deductible + claim amount from settlement/judgment
- Example: If Northwind recovers $500K from negligent vendor, insurer gets $100K deductible + claim amount; Northwind retains remainder

## 5. Insurance Gaps & Limits

**Gaps identified**:
- Intellectual property infringement: Not covered by standard CGL; would require separate IP infringement liability policy (being evaluated)
- Business interruption (non-cyber): Limited; covers only cyber incidents, not force majeure (earthquake, pandemic)
- Reputational harm: Not insurable; must be managed via crisis communications and legal defense

**Review schedule**: Annual audit (CFO + General Counsel + Risk Management) to ensure limits remain adequate for company size and risk profile.

## 6. Insurance Broker & Administration

**Broker**: Marsh USA (Austin office) — handles all policies, renewals, and claims coordination.

**Renewal Process**:
- October: Broker requests renewal quotes from all insurers
- November: CFO + General Counsel review quotes and approve renewals
- December 1–15: All policies renew; certificates issued to customers/vendors on demand

**Certificate of Insurance**: Available from CFO's office; includes all active policies, limits, and insured parties. Provided to customers/vendors within 48 hours of request.

## 7. Material Change & Coverage Review

If Northwind's business materially changes (acquisition, new product line, geographic expansion, significant customer concentration), CFO notifies Marsh for coverage review:
- New product with higher liability risk → E&O limit increase
- Customer concentration with large single client → customer-specific excess liability consideration
- Acquisition of another company → representation & warranty insurance may be necessary

---

**Related Policies:** Master Services Agreement (MSA) Standard; Incident Response Runbook; Data Classification & Retention Policy.
