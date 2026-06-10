---
title: Cross-Border Data Transfer Policy
doc_id: data-priv-cross-border-transfer-policy
owner: Chief Privacy Officer
last_updated: 2026-04-18
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Cross-Border Data Transfer Policy

## 1. Overview and Legal Requirement

Northwind Technologies processes personal data of EU/EEA residents in cloud infrastructure located in the United States (AWS regions: us-east-1, us-west-2) and secondary regions (Azure: US East). Transfers of personal data from the EU/EEA to the US require a **legal mechanism** under GDPR Articles 44–49.

**Current mechanism**: Northwind uses **Standard Contractual Clauses (SCCs)** as approved by the European Commission. This policy defines how SCCs are implemented, documented, and enforced.

## 2. GDPR Transfer Mechanisms

Under GDPR Article 44–49, personal data may be transferred outside the EU/EEA **only if**:

### 2.1 Transfer Mechanisms (in priority order)

1. **Adequacy Decision** (GDPR Article 45): EU Commission has determined the destination country has an adequate level of data protection (e.g., Canada, Israel). **US has no adequacy decision.** Not applicable.

2. **Standard Contractual Clauses (SCC)** (GDPR Article 46(2)(c)): The exporter and importer sign EU-approved contracts ensuring data remains protected. **APPLICABLE TO NORTHWIND.** SCC implementation is mandatory.

3. **Binding Corporate Rules (BCR)** (GDPR Article 46(2)(b)): Multinational groups may use internally-approved binding rules. Northwind has no BCRs (subsidiary-based BCR would require significant legal infrastructure). Not currently applicable.

4. **Approved Codes of Conduct** (GDPR Article 46(2)(e)): Industry groups may develop approved codes. Rarely used for cloud infrastructure. Not applicable.

5. **Derogations** (GDPR Article 49): Temporary transfers without safeguards are permitted **only for narrow cases**:
   - Data subject has explicitly consented (after being informed of risks)
   - Transfer is necessary to fulfill a contract with the data subject
   - Transfer is necessary for important reasons of public interest
   - Transfer is necessary to establish, exercise, or defend legal claims
   - **Derogations are NOT the default.** Northwind must use SCCs.

## 3. Standard Contractual Clauses (SCC) Implementation

### 3.1 SCC Document Structure

Northwind's SCCs are executed as follows:

**Module One: Controller-to-Processor Transfer** (Northwind controls data; cloud provider processes it)
- **Exporter**: Northwind Technologies (EU Data Controller)
- **Importer**: AWS US (Data Processor)
- **Governing law**: EU (Brussels) or UK if post-Brexit applicable

**Module Two: Processor-to-Subprocessor Transfer** (Cloud provider engages other subprocessors)
- **Exporter**: AWS (Processor)
- **Importer**: Third-party subprocessor (e.g., Datadog for monitoring)
- Cloud provider is responsible for SCC compliance with subprocessors

**Module Three: Controller-to-Controller Transfer** (Rare; Northwind and a partner share control of data)
- **Exporter**: Northwind
- **Importer**: Partner company
- Applies only if Northwind has joint-control relationships (see **Data Processing Agreement (DPA) Standard**)

**Module Four: Processor-to-Processor Transfer** (Not applicable; processors do not transfer to other processors without controller approval)

### 3.2 SCC Adoption Process and Timeline

| Step | Timeline | Owner |
|------|----------|-------|
| 1. Vendor/service identified; legal negotiates SCC terms | Week 1–2 | General Counsel + Chief Privacy Officer |
| 2. SCC executed; filed in Vendor Register | Week 3 | Chief Privacy Officer |
| 3. Supplementary measures assessed (see § 3.3) | Week 2–3 | VP Security + Privacy Team |
| 4. Transfer begins only after SCC + measures approved | Week 4+ | All parties |
| 5. Annual audit of SCC compliance | Annual | Compliance Team |

### 3.3 Supplementary Measures (Post-Schrems II)

Following the CJEU's decision in **Schrems II** (Case C-311/18), SCCs alone are insufficient if the destination country's laws allow government access to personal data without due process. The US FISA law (Foreign Intelligence Surveillance Act) allows US government to compel data disclosure.

**Northwind's supplementary measures**:

1. **Encryption at rest** (AES-256): Personal data is encrypted before upload to US cloud infrastructure. Cloud provider has encryption keys in hardware security modules; US government cannot compel decryption without the key (which is held in EU HSM).

2. **Data minimization**: Northwind collects and transfers only the minimum personal data necessary for the service:
   - Customer usage logs do not include full email addresses; identifiers are hashed
   - Customer contract data is pseudonymized (PII replaced with reference IDs)
   - Employee data is minimized (name, email, org; not SSN or home address unless absolutely required)

3. **Transparency**: Northwind discloses transfers to data subjects in the Privacy Policy and the **Cookie & Tracking Policy** (specifically, Google Analytics and Datadog transfers to US).

4. **Data subject rights**: Northwind provides clear mechanisms for data subjects to exercise GDPR rights (see **Data Subject Rights Procedure**), including deletion and portability.

5. **Regular audits**: AWS and Azure undergo SOC 2 Type II audits annually; Northwind reviews audit reports to confirm encryption, access controls, and no unauthorized government access.

### 3.4 SCC Compliance Record

Northwind maintains a **SCC Register** with entries for:

| Service | Importer | Module | Execution Date | SCC Status | Supplementary Measures | Audit Status |
|---|---|---|---|---|---|---|
| **AWS (cloud infrastructure)** | Amazon Web Services LLC (US) | Module 1 (Controller-Processor) | 2023-06-15 | ✅ Active | Encryption (AES-256), data minimization, SOC 2 audit | ✅ Audited 2026-Q1 |
| **Azure (secondary cloud)** | Microsoft Ireland Operations (EU-based, but data processed in US) | Module 1 | 2024-01-10 | ✅ Active | Encryption, data minimization, SOC 2 audit | ✅ Audited 2026-Q1 |
| **Google Analytics** | Google LLC (US) | Module 2 (Processor-Processor via AWS) | 2023-08-20 | ✅ Active | Data minimization (hash IP), transparent disclosure, user opt-out | ✅ Audited 2025-Q4 |
| **Datadog** | Datadog Inc. (US) | Module 2 | 2023-09-01 | ✅ Active | Encryption in transit (TLS 1.3), data minimization, SOC 2 audit | ✅ Audited 2025-Q4 |

## 4. Data Subject Transparency and Consent

### 4.1 Privacy Policy Disclosure

Northwind's Privacy Policy (northwindcloud.com/privacy) explicitly discloses:

> "Northwind Technologies processes your personal data in cloud infrastructure located in the United States (AWS, Microsoft Azure). Your data is subject to US laws, including the Foreign Intelligence Surveillance Act (FISA), which may allow US government access to data. Northwind uses encryption and data minimization to reduce these risks. You have the right to access, delete, or port your data under GDPR; see northwindcloud.com/privacy/rights."

### 4.2 Consent for Analytics Transfers

For **non-essential tracking** (Google Analytics, Datadog, Hotjar), explicit consent is required. See the **Cookie & Tracking Policy** for consent implementation. Users may opt-out of transfers to the US for analytics; core service functionality remains available.

### 4.3 EU Data Subject Rights During Transfers

Data subjects have **uncompromised rights** even though their data is transferred:
- **Right of access** (Article 15): Data subjects may request a copy of their data; Northwind provides it regardless of where it is stored
- **Right of erasure** (Article 17): Data subjects may request deletion from US cloud; Northwind deletes within 30 days
- **Right to lodge a complaint** with their national DPA, regardless of transfer

## 5. Subprocessor Transfers (Northwind → AWS → Third Parties)

When AWS or Azure engages **subprocessors** (e.g., Datadog for monitoring), those subprocessors are governed by:
- **AWS Data Processing Addendum (DPA)** or **Azure DPA**, which includes SCCs
- **Module Two SCC** (Processor-to-Subprocessor) is executed by AWS/Azure, not directly by Northwind
- Northwind has the right to object to new subprocessors or demand additional safeguards

**Northwind's process**:
1. AWS publishes list of approved subprocessors (updated monthly): https://aws.amazon.com/service-terms/
2. Northwind reviews and confirms all subprocessors have SCC coverage
3. If Northwind objects to a subprocessor, Northwind may terminate the AWS contract without penalty (rare)

## 6. Special Cases: Third-Party Integrations

### 6.1 Customer Data Integrations

If a **customer** requests Northwind to integrate with a third-party tool (e.g., Salesforce, Slack), and that integration involves transferring customer data outside the EU/EEA:

1. **Northwind acts as Data Controller** (decides what data to transfer)
2. **SCC or similar mechanism** must be in place with the third party
3. **Customer consent** must be obtained (customer is informed that data will be transferred; customer approves)
4. **Data Processing Agreement** with the third party is required

**Example**: Customer uses Northwind Cloud + Salesforce integration. Customer's Salesforce data (contacts, deals) may be transferred to Salesforce's US servers. Northwind discloses this in the integration configuration screen; customer must explicitly enable the integration.

### 6.2 SCC Chain of Custody

```
┌─────────────────────────────────────────────┐
│ Northwind (EU Data Controller)              │
│ ↓ (SCC Module 1)                            │
│ AWS (US Data Processor)                     │
│ ↓ (SCC Module 2 via AWS DPA)                │
│ Datadog (US Subprocessor)                   │
│                                             │
│ Each link has SCC + supplementary measures │
└─────────────────────────────────────────────┘
```

## 7. Non-US Transfers (EU to UK, APAC, etc.)

### 7.1 Transfers to the UK

The UK is not part of the EU but has **UK Adequacy Decision** (valid post-Brexit). Transfers to UK are treated as internal EU transfers if the UK maintains adequacy. If UK loses adequacy:
- UK transfers require SCC
- SCC is negotiated with importer in UK

### 7.2 Transfers to APAC (Australia, Singapore, Japan)

These countries have varying data protection laws:
- **Australia**: Privacy Act (weaker than GDPR); SCC required
- **Singapore**: Personal Data Protection Act (moderate); SCC recommended
- **Japan**: Act on Protection of Personal Information (APPI, strengthening); SCC required for sensitive data

**Current state**: Northwind does not operate production systems in APAC. If APAC expansion occurs, SCC negotiation will be required.

## 8. Annual Review and Audit

### 8.1 SCC Compliance Audit

The Chief Privacy Officer audits SCC compliance annually:
- Review SCC Register for expired or superseded agreements
- Confirm all cloud vendors and subprocessors have SCCs in place
- Audit supplementary measures (encryption, data minimization, access logs)
- Verify no unauthorized government requests were received (or if received, were documented and challenged)

### 8.2 Response to Legal Challenges

If a **data subject or DPA challenges** Northwind's transfer mechanism:

1. **Immediate escalation** to General Counsel and Chief Privacy Officer
2. **Documentation** of the challenge and Northwind's response
3. **Assessment** of whether supplementary measures are sufficient
4. **Potential actions**:
   - Strengthen encryption or data minimization
   - Seek updated EU Commission guidance on transfers
   - Relocate processing to EU infrastructure if necessary (cost/feasibility assessment)
   - Obtain individual data subject consent for the transfer

### 8.3 Post-Schrems II Monitoring

Northwind monitors ongoing EU/US data adequacy discussions:
- **US reforms**: FISA court transparency, European Data Governance Act
- **EU guidance**: EDPB opinions on transfer mechanisms
- **Regulatory changes**: New regulations that might affect SCCs

If SCCs become invalid or inadequate, Northwind will:
1. Notify affected data subjects within 30 days
2. Implement alternative safeguards (e.g., migrate to EU cloud infrastructure)
3. Update Privacy Policy and this policy

## 9. Cross-Reference to Related Policies

- **GDPR Compliance Policy**: Data subject rights, legal bases, article references
- **Data Processing Agreement (DPA) Standard**: SCC clauses, subprocessor approval
- **Data Classification & Retention Policy**: Data types being transferred (what data is sent abroad)
- **Cookie & Tracking Policy**: Analytics transfers (Google, Datadog to US)
- **Privacy Impact Assessment Process**: DPIA must assess transfer risks; supplementary measures must be documented

---

**Document owner:** Chief Privacy Officer  
**Last approved:** 2026-04-18 by Privacy Leadership  
**Next review:** 2027-04-18
