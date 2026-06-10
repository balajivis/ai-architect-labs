---
title: Secrets Management Standard
doc_id: eng-secrets-management-standard
owner: VP Security
last_updated: 2026-06-01
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Secrets Management Standard

## 1. Overview

Secrets (database passwords, API keys, TLS certificates, JWT signing keys) are the highest-risk asset in any system. Northwind enforces centralized, audited secrets management with automatic rotation.

## 2. What Is a Secret

| Asset | Classification | Example | Rotation |
|-------|-----------------|---------|----------|
| **Database password** | Restricted | `postgres_user:CorrectHorseBatteryStaple!23` | 90 days |
| **API key (external)** | Restricted | `sk_prod_9f8d7c6b5a4e3f2g1h0i9j8k` (Stripe) | 180 days |
| **JWT signing key** | Restricted | `-----BEGIN EC PRIVATE KEY-----` | 365 days |
| **TLS certificate** | Confidential | `/etc/ssl/certs/northwind.pem` | 30 days before expiry |
| **OAuth client secret** | Restricted | `cs_prod_... ` (Google, GitHub, Okta) | Per provider policy |
| **Webhook signing secret** | Restricted | `whsk_prod_...` | 90 days |

## 3. Secrets Storage

### 3.1 Storage Hierarchy

| Secret Type | Storage | Access | Audit |
|-------------|---------|--------|-------|
| **Deployed app secrets** | Kubernetes Secrets + Sealed Secrets (encrypted at-rest) | Pod identity via RBAC; mounted as env vars | Audit log of access |
| **CI/CD pipeline secrets** | GitHub Actions Secrets | Only in workflows; encrypted in transit/rest | GitHub audit log |
| **Local development** | `.env.local` (git-ignored) | Developer machine only | None (local) |
| **Infrastructure secrets** | AWS Secrets Manager + Azure Key Vault | Terraform, application runtime | CloudTrail / Azure audit |
| **Certificates (TLS)** | AWS Certificate Manager + Azure Key Vault | Auto-renewal; used by load balancers | CloudTrail audit |

### 3.2 Never Store Secrets In:

```
❌ Source code (git)
❌ Environment files committed to repo (even .env.example with real values)
❌ Configuration files (Docker, Kubernetes, Terraform) with plaintext values
❌ Logs, error messages, or debug output
❌ Documentation or wiki pages
❌ Pull requests or code review comments
❌ Slack messages, email, or chat (use secrets manager instead)
```

## 4. Secrets in Applications

### 4.1 Environment Variables (Kubernetes)

Production applications read secrets from environment variables populated by Kubernetes Secrets:

```yaml
# kubernetes/deployment-data-connector.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: data-connector
spec:
  template:
    spec:
      containers:
      - name: data-connector
        image: northwind-prod-east.dkr.ecr.us-east-1.amazonaws.com/data-connector:latest
        env:
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: northwind-db-secrets
              key: postgres-password
        - name: SALESFORCE_API_KEY
          valueFrom:
            secretKeyRef:
              name: external-api-secrets
              key: salesforce-api-key
```

**Sealed Secrets**: In git, secrets are encrypted using `kubeseal`:

```bash
# Encrypt a secret before committing
echo -n 'my-secret-password' | kubeseal -o yaml > sealed-secret.yaml

# Result (committed to git):
---
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: northwind-db-secrets
spec:
  encryptedData:
    postgres-password: AgBv...ENCRYPTED_VALUE...
```

### 4.2 Application Code: Reading Secrets

**Go example**:
```go
package main

import "os"

func init() {
    dbPassword := os.Getenv("DATABASE_PASSWORD")
    if dbPassword == "" {
        log.Fatal("DATABASE_PASSWORD env var not set")
    }
    // Use password to connect to database
    db, err := sql.Open("postgres", fmt.Sprintf(
        "postgres://northwind:%s@northwind-db-prod.rds.amazonaws.com/northwind",
        dbPassword,
    ))
}
```

**Python example**:
```python
import os
from urllib.parse import quote

db_password = os.getenv("DATABASE_PASSWORD")
if not db_password:
    raise RuntimeError("DATABASE_PASSWORD not set")

# URL-encode password in case it contains special chars
db_url = f"postgresql://northwind:{quote(db_password)}@northwind-db-prod.rds.amazonaws.com/northwind"
```

**What NOT to do**:
```python
# ❌ NEVER hardcode
password = "hardcoded_password_123"

# ❌ NEVER log
print(f"Connecting with password: {password}")
log.info(f"API key: {api_key}")

# ❌ NEVER return in error messages
raise Exception(f"Failed to connect to {db_user}:{password}@{db_host}")
```

## 5. Secrets in CI/CD (GitHub Actions)

### 5.1 GitHub Actions Secrets

Store all CI/CD secrets as GitHub repository secrets:

```bash
# From GitHub UI or CLI:
gh secret set DATABASE_PASSWORD --body "CorrectHorseBatteryStaple!23"
gh secret set NPM_TOKEN --body "npm_AbCdEfGhIjKlMnOpQrStUv"
gh secret set DOCKER_REGISTRY_PASSWORD --body "..."
```

**In workflows** (accessed as `${{ secrets.SECRET_NAME }}`):

```yaml
# .github/workflows/deploy.yaml
name: Deploy to Staging
on: [push: {branches: [main]}]

env:
  REGISTRY: northwind-prod-east.dkr.ecr.us-east-1.amazonaws.com

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm ci
      - run: npm run build
      
      # ✓ CORRECT: Use secret
      - run: npm run test:integration
        env:
          DATABASE_PASSWORD: ${{ secrets.DATABASE_PASSWORD }}
      
      # ❌ WRONG: Never echo secrets
      - run: echo "Password is ${{ secrets.DATABASE_PASSWORD }}"
        # GitHub masks output, but visible in logs if script captures
```

**Access control**: Only repository maintainers can read/manage secrets.

### 5.2 Secrets in Logs

GitHub Actions automatically masks secret values in logs:

```
# Workflow log (GitHub Actions output):
Run npm run test:integration
  DATABASE_PASSWORD=***
  ✓ 145 tests passed
```

But be careful:
```bash
# ❌ If script captures secret in variable:
PASSWORD="$DATABASE_PASSWORD"
echo "$PASSWORD" > /tmp/debug.log  # Secret now in log file and artifact!

# ✓ Better: Never capture in variables; use directly
npm run test -- --db-password="$DATABASE_PASSWORD"
```

## 6. Local Development

### 6.1 .env.local Setup

Create `.env.local` (git-ignored):

```bash
# .env.local (never commit)
DATABASE_PASSWORD=local_dev_password_123
SALESFORCE_API_KEY=sk_test_xyz789
DATABASE_URL=postgresql://northwind:local_dev_password_123@localhost:5432/northwind_dev
```

**Git ignore configuration**:
```
# .gitignore
.env.local
.env.*.local
```

### 6.2 Development Database

For local development, use a non-production database:

```bash
# docker-compose.yml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: northwind
      POSTGRES_PASSWORD: dev_password_temporary  # Not a real secret
      POSTGRES_DB: northwind_dev
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

## 7. Secrets Rotation

### 7.1 Rotation Schedule

| Secret Type | Rotation Interval | Procedure |
|-------------|-----------------|-----------|
| **Database password** | 90 days | 1. Generate new password; 2. Update Kubernetes secret; 3. Update database; 4. Verify application; 5. Archive old password |
| **API key** | 180 days | 1. Generate new key from provider (e.g., Stripe); 2. Update GitHub Actions secret; 3. Test in staging; 4. Update prod secret; 5. Revoke old key |
| **JWT signing key** | 365 days | 1. Generate new ECDSA key; 2. Support both old + new (dual-signing window); 3. Gradually migrate; 4. Deprecate old |
| **TLS certificate** | 30 days before expiry | ACM auto-renews; verify renewal succeeded in CloudTrail |

### 7.2 Rotation Procedure (Database Password Example)

```bash
#!/bin/bash
# scripts/rotate-db-password.sh

# Step 1: Generate new password (32 random chars)
NEW_PASSWORD=$(openssl rand -base64 32 | tr -d '=+/' | cut -c1-32)
echo "New password generated: [redacted]"

# Step 2: Update database user
psql -h northwind-db-prod.rds.amazonaws.com -U postgres \
  -c "ALTER USER northwind PASSWORD '$NEW_PASSWORD';"

# Step 3: Update Kubernetes secret
kubectl patch secret northwind-db-secrets \
  -p '{"data":{"postgres-password":"'$(echo -n "$NEW_PASSWORD"|base64)'"}}'

# Step 4: Trigger pod restart (pods will pick up new secret)
kubectl rollout restart deployment/data-connector -n northwind-prod
kubectl rollout restart deployment/transformation-engine -n northwind-prod

# Step 5: Verify connectivity
kubectl exec -it deployment/data-connector -- \
  psql -h northwind-db-prod.rds.amazonaws.com -U northwind -d northwind -c "SELECT 1;"

# Step 6: Archive old password securely (for audit)
# Stored in password manager; never in logs
echo "Old password archived in 1Password vault"
```

## 8. Credential Scanning and Auditing

### 8.1 Pre-Commit Scanning

Prevent secrets from being committed using `git-secrets`:

```bash
# Install
brew install git-secrets
git secrets --install ~/.git-templates/git-secrets
git config --global init.templateDir ~/.git-templates/git-secrets

# Configure patterns
git secrets --add 'sk_live_[0-9a-zA-Z]{20,}'  # Stripe live keys
git secrets --add 'ghp_[0-9a-zA-Z]{36}'       # GitHub personal access tokens
git secrets --add 'aws_access_key_id = AKIA[0-9A-Z]{16}'  # AWS keys

# Usage (automatic on every commit)
git commit -m "add feature"
# If secret detected: commit blocked ✓
```

### 8.2 CI/CD Secret Scanning

GitHub Actions automatically scans for secrets in code:

```yaml
# Enabled by default in enterprise repositories
# Found secrets: Alert VP Security; require immediate rotation
```

### 8.3 Audit Logging

All access to secrets logged:

| Event | Logged To | Retention |
|-------|-----------|-----------|
| AWS Secrets Manager access | CloudTrail | 90 days |
| Azure Key Vault access | Azure audit log | 90 days |
| Kubernetes secret read | K8s audit log | 30 days |
| GitHub Actions secret use | GitHub audit log | 90 days |

**Monitoring**: Datadog alerts if secrets accessed from unauthorized source.

## 9. Incident: Suspected Secret Compromise

If a secret is exposed (accidentally committed, email leaked, etc.):

1. **Revoke immediately**: Disable the credential at source (database, API provider, etc.)
2. **Audit access**: Check logs for unauthorized use within past 24 hours
3. **Rotate**: Generate new secret; update all references
4. **Incident report**: Document in Jira; notify VP Security and affected teams
5. **Post-incident**: Prevent recurrence (better scanning, training, etc.)

Example: Secret accidentally committed to GitHub

```bash
# Step 1: Force push to remove from history (destructive; after VP approval)
git filter-branch --tree-filter 'rm -f exposed_file.env' -- --all
git push --force

# Step 2: Immediately rotate all compromised secrets
# Step 3: Notify users if PII in secret (see INCIDENT_RESPONSE_RUNBOOK)
# Step 4: GitHub will notify if secret was detected; follow up
```

---

**Related policies:**
- See **Information Security Policy** for encryption standards and access control
- See **GitHub Actions CI/CD Pipeline Guide** for secrets in workflows
- See **Infrastructure as Code Standards** for Terraform secret handling
- See **Code Review Standards** for code review checklist on secrets
