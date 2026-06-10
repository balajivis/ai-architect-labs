---
title: CI/CD Pipeline Guide (GitHub Actions)
doc_id: eng-github-actions-ci-cd-pipeline
owner: Platform Engineering
last_updated: 2026-06-01
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# CI/CD Pipeline Guide (GitHub Actions)

## 1. Overview

Northwind's CI/CD pipelines are implemented via GitHub Actions. All code changes automatically flow through testing, security scanning, staging, and production deployment stages. See **Git Branching & Release Strategy** for branch workflows.

## 2. Pipeline Architecture

```
┌─────────────────┐
│ Feature branch  │
│ push to GitHub  │
└────────┬────────┘
         │
    ┌────▼───────────────────────────────────────┐
    │    PULL REQUEST: Run Tests & Linting       │
    │  ✓ Unit tests (Jest/pytest)                │
    │  ✓ Linting (ESLint/Pylint)                │
    │  ✓ Security scan (Snyk)                    │
    │  ✓ Type check (TypeScript)                 │
    └────┬───────────────────────────────────────┘
         │
    ┌────▼──────────────────────────────────────────┐
    │ Code Review & Approval (2 required)           │
    │ See CODE_REVIEW_STANDARDS for requirements    │
    └────┬──────────────────────────────────────────┘
         │
    ┌────▼────────────────────────────────────┐
    │ Merge to main                           │
    │ ✓ Tests run again (full suite)         │
    │ ✓ Build Docker image                   │
    │ ✓ Push to ECR (AWS)                    │
    └────┬────────────────────────────────────┘
         │
         ├─────────────────┬─────────────────────┐
         │                 │                     │
    ┌────▼──────┐  ┌──────▼─────┐  ┌───────▼────┐
    │Deploy to  │  │Auto-tag    │  │Create      │
    │Staging    │  │Release     │  │Artifact    │
    │(1-hr delay)  │          │  │          │
    └──────────────┘  └──────────┘  └───────────┘
         │
    ┌────▼─────────────────────────────────┐
    │ Smoke Tests in Staging (8 hours)    │
    │ ✓ Customer login                    │
    │ ✓ API health checks                 │
    │ ✓ Core workflows                    │
    └────┬────────────────────────────────┘
         │
    ┌────▼──────────────────────────────────────┐
    │ Manual Deploy to Production               │
    │ (Requires on-call engineer approval)      │
    │ See PRODUCTION_DEPLOYMENT_RUNBOOK         │
    └────┬──────────────────────────────────────┘
         │
    ┌────▼────────────────────────────────────┐
    │ Post-Deploy Health Checks (30 min)      │
    │ ✓ Error rates < 0.1%                   │
    │ ✓ Latency p99 acceptable               │
    │ ✓ Business metrics normal              │
    └─────────────────────────────────────────┘
```

## 3. PR Pipeline (Feature Branch)

When a feature branch is pushed to GitHub, the PR pipeline runs automatically:

### 3.1 Job: Test

```yaml
test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-node@v3
      with:
        node-version: '20'
    - run: npm ci
    - run: npm run test:unit
      env:
        CI: true
    - run: npm run test:integration
```

**SLA**: Tests must complete within 10 minutes. Failure blocks merge.

### 3.2 Job: Lint

```yaml
lint:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3
    - run: npm ci
    - run: npm run lint
    - run: npm run type-check
```

**Checks**: ESLint (code style), Prettier (formatting), TypeScript strict mode

### 3.3 Job: Security Scan

```yaml
security:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3
    - run: npm install -g snyk
    - run: snyk test --severity-threshold=high
    - run: npm audit --audit-level=high
    - uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
```

**Failure condition**: Any HIGH or CRITICAL vulnerability blocks merge. LOW/MEDIUM may be acknowledged as risk acceptance (see **Information Security Policy** for risk acceptance process).

### 3.4 PR Status Check Summary

| Job | Status | SLA | Failure Action |
|-----|--------|-----|---|
| test | Required | 10 min | Block merge |
| lint | Required | 3 min | Block merge |
| security (Snyk) | Required | 5 min | Block merge (unless risk-accepted) |
| security (npm audit) | Advisory | 5 min | Warn only |
| type-check | Required | 5 min | Block merge |

## 4. Main Branch Pipeline (Post-Merge)

After a PR is merged to `main`, a comprehensive pipeline runs:

### 4.1 Build & Push

```yaml
build:
  runs-on: ubuntu-latest
  if: github.ref == 'refs/heads/main'
  steps:
    - uses: actions/checkout@v3
    - run: npm ci && npm run build
    - uses: aws-actions/configure-aws-credentials@v2
    - run: aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_REGISTRY
    - run: docker build -t $ECR_REGISTRY/$SERVICE:${{ github.sha }} .
    - run: docker push $ECR_REGISTRY/$SERVICE:${{ github.sha }}
    - run: docker tag $ECR_REGISTRY/$SERVICE:${{ github.sha }} $ECR_REGISTRY/$SERVICE:latest
    - run: docker push $ECR_REGISTRY/$SERVICE:latest
```

**Output**: Docker image pushed to AWS ECR (`northwind-prod-east` registry)

### 4.2 Auto-Release Tagging (Optional)

If commit message contains `RELEASE=patch|minor|major`, auto-tag:

```yaml
release:
  runs-on: ubuntu-latest
  if: github.ref == 'refs/heads/main'
  steps:
    - uses: actions/checkout@v3
    - run: |
        RELEASE_TYPE=$(git log -1 --format=%b | grep "RELEASE=" | cut -d= -f2)
        if [ -n "$RELEASE_TYPE" ]; then
          npm run version:$RELEASE_TYPE
          git tag $(jq .version package.json)
          git push origin --tags
        fi
```

See **Git Branching & Release Strategy** for version numbering.

### 4.3 Deploy to Staging (1-hour delay)

```yaml
deploy-staging:
  runs-on: ubuntu-latest
  if: github.ref == 'refs/heads/main'
  # Runs 1 hour after merge (scheduled to avoid weekend deploys)
  steps:
    - uses: actions/checkout@v3
    - run: ./scripts/deploy.sh staging
```

**Inputs**: Latest image from ECR
**Outputs**: Service running in staging cluster (EKS `northwind-staging-east`)
**Manual validation**: 8-hour test window before production deploy

## 5. Manual Production Deployment

Production deployments are not automatic. Deployment lead triggers manually via GitHub:

```bash
# Via GitHub Actions UI:
# 1. Go to Actions → "Deploy to Production"
# 2. Click "Run workflow"
# 3. Select branch (main)
# 4. Type "production" in confirmation field
# 5. Click "Run"
```

**Approval flow**:
- On-call engineer must be available (see **On-Call & Escalation Policy**)
- Staging validation window (8 hours) must complete
- No production deploys Friday after 3 PM PT (weekend incident risk)

See **Production Deployment Runbook** for full deployment procedure and monitoring.

## 6. Failure Handling

### 6.1 PR Pipeline Failures

If a PR fails any automated check:

1. **Author investigates** (GitHub shows failure details)
2. **Fix and push** new commit to same branch
3. **CI re-runs** automatically
4. **Merge once all checks pass**

Example: If Snyk finds a vulnerable dependency:
```bash
npm update vulnerable-package@^1.2.3
git commit -am "security: update vulnerable dependency"
git push origin feature/my-feature
# CI runs again; Snyk should pass this time
```

### 6.2 Main Branch Failures

If build/push to ECR fails after merge to main:

1. **Slack alert** sent to `#deployments` channel
2. **On-call engineer** investigates (Docker build error, registry permission, etc.)
3. **Fix committed** and merged to main (e.g., `fix: update Dockerfile`)
4. **Staging/production deploy** retried with new image

**Prevention**: Always test `npm run build && docker build` locally before pushing.

### 6.3 Staging Validation Failures

If automated smoke tests fail in staging (8-hour window):

1. **QA team** notifies engineering
2. **Root cause** identified (database schema, environment variable, etc.)
3. **Hotfix** created and merged to main (new image built)
4. **Re-deploy to staging** and re-run smoke tests
5. Only after staging passes: Approve for production

## 7. Secrets and Environment Variables

All sensitive configuration is managed via GitHub Secrets and Kubernetes Secrets:

| Level | Storage | Usage |
|-------|---------|-------|
| **GitHub Actions** | GitHub Secrets | NPM_TOKEN, AWS credentials, ECR login |
| **Staging/Prod** | Kubernetes Secret | Database passwords, API keys, TLS certs |
| **Local development** | `.env.local` (git-ignored) | Local overrides |

See **Secrets Management Standard** for full credential handling policy.

## 8. Observability and Monitoring

All pipeline runs are logged and viewable:

- **GitHub Actions UI**: `github.com/northwind/<repo>/actions` → click workflow run
- **Datadog integration**: Pipeline events logged to Datadog; custom dashboards track build times
- **Slack notifications**: `#deployments` channel receives alerts (merge, deploy, failure)

### 8.1 Metrics Tracked

| Metric | Alert Threshold | Owner |
|--------|---|---|
| PR test time | > 15 min | Platform Eng |
| Build time | > 20 min | Platform Eng |
| Deploy time | > 45 min | DevOps Lead |
| Pipeline success rate | < 95% | VP Engineering |

## 9. Adding New Pipeline Steps

To add a new automated check (e.g., a new linter, security tool):

1. **Define in** `.github/workflows/` YAML file
2. **Set to advisory** initially (warning, no block)
3. **Test on feature branches** for 2 weeks
4. **Promote to required** (block merge) if stable
5. **Document** in this file and notify team via **Code Review Standards** update

---

**Related policies:**
- See **Code Review Standards** for PR approval workflow
- See **Git Branching & Release Strategy** for branch naming and versioning
- See **Production Deployment Runbook** for manual production deployment trigger
- See **Secrets Management Standard** for credential handling in CI/CD
