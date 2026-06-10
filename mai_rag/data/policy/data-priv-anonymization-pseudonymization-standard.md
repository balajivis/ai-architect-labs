---
title: Anonymization & Pseudonymization Standard
doc_id: data-priv-anonymization-pseudonymization-standard
owner: Chief Privacy Officer
last_updated: 2026-04-19
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Anonymization & Pseudonymization Standard

## 1. Overview and Definitions

**Anonymization** and **pseudonymization** are technical techniques that reduce the privacy risk of personal data by removing or replacing identifiers. This standard defines when and how to apply these techniques at Northwind Technologies to comply with GDPR, support data minimization, and enable legitimate data reuse.

### 1.1 Key Definitions

| Term | Definition | GDPR Status | Reversible |
|------|-----------|------------|-----------|
| **Personal Data** | Any information relating to an identified or identifiable natural person | ✅ Regulated by GDPR | N/A |
| **Pseudonymous Data** | Data processed using a pseudonym (e.g., "User_12345") that can only be attributed to the data subject via additional information (held separately) | ❌ Still personal data; GDPR applies | ✅ Yes (with key) |
| **Anonymized Data** | Data that cannot be attributed to an identified or identifiable data subject, even with reasonable effort | ❌ Not personal data; GDPR does not apply | ❌ No (by definition) |

**Critical distinction**: Pseudonymization is **not anonymization**. A hashed email address (e.g., "sha256('user@example.com')") is pseudonymous if Northwind holds the mapping (email → hash). If Northwind deletes the mapping, the hash becomes anonymous.

## 2. When to Pseudonymize vs. Anonymize

### 2.1 Pseudonymization Use Cases

Pseudonymization is appropriate when Northwind needs to:
- Process data **conditionally** based on individual identity (e.g., "show User_12345's usage stats to their manager")
- **Link records across systems** (e.g., customer database + usage logs + support tickets)
- **Comply with GDPR rights**: Re-identify the data subject on request to fulfill access/deletion rights

**Examples**:
- Customer account ID (cust-12345) replaces email; mapping held in secure database
- Employee ID (emp-00456) replaces name in payroll; only HR team holds the key
- API usage logs keyed by SHA-256(API_KEY) instead of customer name; API key mapping held in separate encrypted system

**Advantage**: Reduces risk if logs are leaked (attacker cannot identify individuals without the key).

**Limitation**: Still personal data under GDPR; must comply with GDPR rights, retention schedules, security requirements.

### 2.2 Anonymization Use Cases

Anonymization is appropriate when Northwind needs to:
- **Aggregate analytics** (e.g., "50% of users access reporting feature")
- **Train machine learning models** on historical data
- **Share data with third parties** without re-identifying individuals
- **Permanently disable re-identification** (e.g., deleted customer data must be unable to link back to individual)

**Examples**:
- "In March 2026, Northwind Cloud users ran 5M reports, 30% of which exceeded 10-second latency." (No individual identifiable)
- ML training set: 1M rows of {platform_version, num_users, feature_X_enabled, avg_query_latency}; no customer or user identifiers
- Anonymized dataset: Remove customer_id, email, company name; replace with random ID; delete mapping; provide to researcher under data use agreement

**Advantage**: Exempt from GDPR; no right-of-access, no retention schedule, no deletion obligation. Max data reuse.

**Limitation**: Truly hard to achieve; courts often find "anonymous" data is re-identifiable. Northwind must validate anonymization before claiming exemption.

## 3. Pseudonymization Implementation

### 3.1 Key Management

**Requirement**: The mapping between original identifier and pseudonym must be:
- Held **separately** from the pseudonymized data (not in the same database)
- **Encrypted** (AES-256)
- **Access-restricted** (only authorized personnel can access the key; logged access)
- **Retention-scheduled** (deleted when the original data is deleted)

**Architecture example**:
```
┌──────────────────────────────────────────────────────────────┐
│ Separated Keying                                             │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ System A: Pseudonymized Data (Production Logs)             │
│ ┌────────────────────────────────┐                          │
│ │ timestamp  | user_id | event   │                          │
│ │ 2026-04-19 | U_12345 | login   │  (no reversal possible) │
│ │ 2026-04-19 | U_12346 | query   │                          │
│ └────────────────────────────────┘                          │
│                                                              │
│ System B: Key (Encryption Safe / Separate Server)          │
│ ┌─────────────────────────────────┐                         │
│ │ pseudonym | original_id | hash  │  (encrypted, access    │
│ │ U_12345   | cust_98765  | ***   │   logged, limited to   │
│ │ U_12346   | cust_99999  | ***   │   privacy team)        │
│ └─────────────────────────────────┘                         │
│                                                              │
│ Only the Chief Privacy Officer can re-identify.             │
└──────────────────────────────────────────────────────────────┘
```

### 3.2 Pseudonymization Techniques

| Technique | How It Works | Reversibility | Strength | Use Case |
|-----------|------------|---|---|---|
| **Hashing (SHA-256)** | Hash(email) = "a7f4a2b9c3d1..." | No (not reversible) | Medium (if input is long/complex) | User ID replacement; analytics aggregation |
| **Encryption (AES-256)** | Encrypt(email, key) = "xyz123" | Yes (requires key) | High (requires key and HSM) | Sensitive fields in logs; medical data |
| **Replacement (Lookup)** | email → U_12345 (via mapping table) | Yes (requires mapping) | High (depends on mapping security) | Account IDs; customer names |
| **Generalization (Aggregation)** | "user_age" → "30-40" (band) | No (data loss) | Low (still possibly identifiable) | Demographics in analytics |
| **Suppression (Deletion)** | Remove identifiers entirely | No | High (cannot re-identify) | Public datasets; research data |

**Northwind's standard**: Use **hashing for logs/analytics** (irreversible); **encryption with HSM-held keys for sensitive data** (reversible if needed); **lookup tables for account identifiers** (reversible with access control).

### 3.3 Pseudonymization Audit

Pseudonymized data must be audited annually to confirm:
- Mapping is held separately and securely
- Mapping access is logged (who accessed it, when, why)
- Mapping is deleted when the original data is deleted (retention schedule compliance)
- No re-identification has occurred without authorization

**Audit checklist**:
- [ ] Mapping location and encryption status documented
- [ ] Access logs for mapping reviewed (no suspicious access)
- [ ] Reconciliation: all pseudonymized records have a corresponding mapping entry
- [ ] Retention: no orphaned mappings (data deleted but mapping remains)

## 4. Anonymization Validation

### 4.1 Legal Standard for Anonymization

Under GDPR Recital 26, data is anonymous if:
> "It is not possible to identify the data subject or to attribute the data to an identified individual...taking account of all means reasonably likely to be used."

**Key phrase**: "reasonably likely to be used" — attackers with moderate resources, time, and technical skills cannot re-identify.

Northwind must apply this standard before claiming data is anonymous.

### 4.2 Anonymization Risk Assessment

Before declaring data anonymous, conduct a **Risk Assessment**:

1. **Uniqueness test**: Is the combination of remaining attributes unique or near-unique?
   - Example: "Female, age 45, CEO, healthcare industry" may uniquely identify 1–2 people nationally (risky)
   - Example: "Age 30-40, London, software engineer" matches 10,000+ people (safer)

2. **Linkability test**: Can this data be linked to another dataset to re-identify?
   - Example: Anonymized usage data + customer database (even if separately held) could be cross-matched by timestamp
   - Example: Anonymized support tickets + public tweets (timing and subject) could reveal customer name

3. **Inference test**: Can a motivated attacker infer identity from patterns?
   - Example: A researcher analyzes "anonymous" company data and infers which competitor is the largest customer (economic inference attack)
   - Example: ML model trained on "anonymous" genomic data can be reverse-engineered to extract individual DNA profiles

### 4.3 Anonymization Techniques

| Technique | Risk Reduction | Effort | Reversibility |
|-----------|---|---|---|
| **Aggregation** (age band, region band) | Low-Medium | Low | No |
| **Suppression** (remove identifier columns entirely) | High | Low | No |
| **Perturbation** (add noise to numeric values) | Medium | Medium | No |
| **Generalization** (replace specific with general; e.g., "John Smith" → "Name removed") | Low | Low | No |
| **Sub-sampling** (retain only 10% of records) | Low | Medium | No |
| **k-anonymity** (ensure each record is indistinguishable from k–1 others) | Medium-High | High | No |
| **Differential Privacy** (mathematical guarantee that queries reveal only aggregate patterns) | High | Very High | No |

**Northwind's standard for anonymization**:
1. **Remove all direct identifiers** (name, email, customer_id, account_id)
2. **Aggregate or generalize quasi-identifiers** (age → band; company → industry)
3. **Validate with k-anonymity** (k ≥ 5; each aggregate represents ≥5 individuals)
4. **Delete the mapping** irreversibly (no reversal possible)

**Example - Anonymizing Customer Usage Data**:

**Before (Personal Data)**:
```
customer_id | email             | company        | num_users | api_calls
1004        | alice@acme.com    | Acme Corp      | 50        | 100K
1005        | bob@widgets.com   | Widget Inc.    | 20        | 50K
```

**After (Anonymized)**:
```
company_size | industry  | api_calls_bucket
50-100       | Tech      | 100K+
50-100       | Tech      | 50K-100K
```

(Each row represents ≥5 customers; no reversal to individual possible; mappings deleted.)

## 5. Restricted Data Handling (No Anonymization Allowed)

**Certain data MUST NOT be anonymized** — it must be deleted per retention schedule:

- **Restricted classification** (passwords, encryption keys, authentication tokens): NIST 800-88 wipe; no anonymization possible
- **Medical/health data**: May be anonymized only under strict regulatory guidance (e.g., HIPAA de-identification standard); Northwind does not handle health data
- **Biometric data**: Must be deleted (GDPR Article 9); anonymization prohibited in practice

These data types are **deleted, not anonymized, at end of retention period**.

## 6. Pseudonymization vs. Records Management

**Common confusion**: Pseudonymization is different from **Records Management** (retention schedules, archival).

| Aspect | Pseudonymization | Records Management |
|--------|---|---|
| **Purpose** | Reduce privacy risk during processing | Manage lifecycle (retention, archival, deletion) |
| **GDPR Status** | Still personal data (GDPR applies) | Applies to all records (personal + non-personal) |
| **Reversibility** | May be reversible (pseudonym) or irreversible (anonymized) | Deletion is permanent |
| **Retention Period** | May extend if re-identification rights must be honored | Follows retention schedule from **Data Retention Schedule** |
| **Example** | Hash(email) in logs; original email deleted but hash retained | Email deleted after 3 years per retention policy |

See **Records Management Policy** for archival and disposal procedures.

## 7. Training and Compliance

All engineers and data scientists working with customer data must:
- Complete **Privacy Training** (annual; 1 hour) covering anonymization, pseudonymization, and data handling
- Obtain **Chief Privacy Officer approval** before claiming data is anonymized (simple form: `privacy-approval@northwind.com`)
- Document pseudonymization/anonymization in code comments and architecture docs

**Compliance check**: Quarterly audit of code repositories to identify where customer data is processed; validate that pseudonymization/anonymization are correctly applied.

## 8. Cross-Reference to Related Policies

- **Data Classification & Retention Policy**: Classification determines risk level and informs pseudonymization strategy
- **Records Management Policy**: Deletion of mappings must align with data retention schedules
- **Privacy Impact Assessment Process**: DPIA must assess whether anonymization or pseudonymization is feasible for the proposed processing
- **Data Subject Rights Procedure**: Pseudonymization may limit ability to fulfill right of access; must be designed to preserve reversibility if GDPR rights are needed

---

**Document owner:** Chief Privacy Officer  
**Last approved:** 2026-04-19 by Privacy Leadership  
**Next review:** 2027-04-19
