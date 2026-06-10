---
title: Encryption Standard
doc_id: itsec-encryption-standard
owner: IT Security Team
last_updated: 2026-04-02
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Encryption Standard

## 1. Purpose and Scope

This standard establishes encryption requirements for all Confidential and Restricted data at Northwind, both in transit and at rest. All teams handling sensitive data must comply.

## 2. Encryption in Transit (Data at Rest)

### 2.1 Network Communication Standards

All network traffic carrying Confidential or Restricted data must use:
- **TLS 1.3** minimum (no TLS 1.2 or earlier)
- **Strong cipher suites** (ECDHE or DHE for key exchange; AES-GCM or ChaCha20-Poly1305 for symmetric encryption)
- **Certificate validation** enforced (no self-signed certificates in production)
- **Perfect forward secrecy** (PFS) required

### 2.2 Certificate Management

- SSL/TLS certificates issued by trusted Certificate Authority (DigiCert or Let's Encrypt)
- Certificates auto-renewed 30 days before expiration
- Certificate chain validated (no expired intermediate CAs)
- Private keys stored in Hardware Security Module (HSM) with access logged
- Key rotation annually; compromise triggers immediate 72-hour rotation

### 2.3 VPN Encryption

- VPN tunnels use IPsec or TLS 1.3
- IKE Phase 1: DH Group 14 (2048-bit) minimum; AES-256-CBC
- IKE Phase 2: ESP with AES-256-GCM
- Pre-shared keys (PSK) for site-to-site VPN rotated quarterly
- All VPN keys stored in HSM

## 3. Encryption at Rest

### 3.1 Database Encryption

All databases storing Confidential or Restricted data must have encryption at rest:
- **Algorithm**: AES-256 (no weaker algorithms)
- **Implementation**: Native database encryption (PostgreSQL pgcrypto, MySQL TDE, or AWS RDS KMS)
- **Key management**: Keys held in Hardware Security Module (HSM) or AWS KMS; application never sees plaintext key

| Database Type | Encryption Method | Key Manager |
|---|---|---|
| Azure PostgreSQL Flexible Server | TDE with CMK (Customer Managed Key) | Azure Key Vault |
| AWS RDS | AWS KMS with customer-managed key | AWS KMS |
| MongoDB | Native WiredTiger encryption | AWS KMS or Azure Key Vault |
| DynamoDB | AWS KMS server-side encryption | AWS KMS |

### 3.2 Block Storage Encryption

All cloud storage (EBS, Blob Storage) and NAS systems must use:
- **Algorithm**: AES-256
- **Implementation**: Cloud-native encryption (EBS KMS, Azure Storage encryption)
- **Backups**: All backups encrypted with same key as primary data
- **Snapshots**: Encrypted snapshots only; plaintext snapshots prohibited

### 3.3 File-Level Encryption

For files stored in object storage (S3, Blob Storage):
- **Algorithm**: AES-256-GCM
- **Implementation**: S3 KMS encryption or Azure Blob client-side encryption
- **Bucket policy**: Default deny; explicit allow for service accounts only
- **Object versioning**: Enabled; encryption applies to all versions

## 4. Key Management

### 4.1 Key Hierarchy

```
Master Key (in HSM)
  ├── Database Encryption Key (DEK)
  │    └── Encrypts customer data at rest
  ├── Backup Key
  │    └── Encrypts backup files
  └── Application Key
       └── Encrypts sensitive fields in logs
```

### 4.2 Key Rotation

| Key Type | Rotation Frequency | Trigger Event |
|---|---|---|
| Database DEK | Annually (Jan) | Scheduled; no downtime required |
| Backup Key | Annually | Scheduled with backup window |
| Application Key | Semi-annually | Scheduled; old key retained for decryption |
| TLS Certificate | Annually (before expiration) | Automated 30 days prior |
| Incident-triggered | Immediately (within 2h) | Key compromise, data breach |

### 4.3 Key Storage and Access

- All master keys stored in Hardware Security Module (HSM)
- HSM access requires MFA (smart card + PIN)
- Only 3 people have HSM access: CISO, VP Infrastructure, and senior DBA
- HSM backup key split into 3 shares; each held by separate person (Shamir secret sharing)
- All HSM access logged and retained for 7 years

### 4.4 Key Decommissioning

When a key is retired:
- Key marked as "retired" in HSM; new data uses new key
- Old key retained for decryption of existing data (indefinitely)
- If key is compromised, retired key is destroyed after re-encryption of all data with new key

## 5. Encryption for Endpoint Devices

### 5.1 Full Disk Encryption

All company-issued endpoints must have full disk encryption:
- **Windows**: BitLocker with XTS-AES 128-bit
- **macOS**: FileVault with AES-XTS 128-bit
- **Linux**: LUKS with AES-256-CBC

Recovery keys backed up to a secure vault (Azure AD for Windows/macOS; Okta for Linux). Users cannot disable encryption.

### 5.2 Personal Device Encryption

Personal devices used for work must have full disk encryption or file-level encryption for work files.

## 6. Encryption for Data in Transit (End-to-End)

### 6.1 Email Encryption

Confidential or Restricted data sent via email requires:
- **Office 365 Message Encryption** (OME)
- Recipient receives unique password to decrypt message
- Message expires after 28 days (cannot be read after expiration)
- No metadata encryption; email subject visible to email provider

### 6.2 Application-to-Application Communication

All inter-service communication in Kapi and Brahmasumm must use:
- **mTLS (mutual TLS)** with certificate pinning
- **JWTs** signed with RS256 (RSA 2048-bit minimum) and HMAC-SHA256
- **Message-level encryption**: Sensitive fields encrypted with AES-256-GCM before transport

## 7. Encryption in Logs and Monitoring

### 7.1 Sensitive Data Masking

Logs must NOT contain:
- Plaintext passwords, API keys, or tokens
- Unencrypted PII (SSN, credit card numbers, home addresses)
- Encryption keys

**Remediation**: If sensitive data appears in logs:
1. Immediately quarantine log file
2. Scrub plaintext value from Splunk/Datadog
3. Rotate affected credentials within 1 hour
4. Escalate as Sev-2 per **Incident Response Runbook**

### 7.2 Log Retention Encryption

All logs containing Confidential data retained in archive (>6 months) must be encrypted at rest using AES-256.

## 8. Encryption Testing and Validation

### 8.1 Encryption Verification

- Annual penetration testing includes encryption verification (attempt to decrypt data without key)
- Encryption strength validated against NIST SP 800-175B standards
- Third-party auditors (during SOC 2 audit) verify encryption implementation

### 8.2 Key Recovery Testing

- Annually, a backup key is recovered from offline storage and tested
- Database is restored from encrypted backup using recovered key
- If recovery fails, incident escalation within 1 hour

## 9. Compliance Standards

This standard aligns with:
- **NIST SP 800-175B** (encryption standards)
- **GDPR Article 32** (encryption of personal data)
- **CCPA** (encryption of consumer personal information)
- **PCI DSS 3.4** (encryption of cardholder data)
- **SOC 2 Trust Services Criteria** (encryption and key management)

## 10. Related Policies

- **Information Security Policy**: Data classification and protection standards
- **Data Classification & Retention Policy**: Encryption requirements per data class
- **Endpoint Security Standard**: Device encryption requirements
- **Security Logging & SIEM**: Log protection and encryption

---

**Document owner:** Chief Information Security Officer  
**Last approved:** 2026-04-02 by Security Steering Committee  
**Next review:** 2027-04-02
