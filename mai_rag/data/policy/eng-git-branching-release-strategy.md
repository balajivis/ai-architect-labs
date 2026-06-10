---
title: Git Branching & Release Strategy
doc_id: eng-git-branching-release-strategy
owner: VP Engineering
last_updated: 2026-06-01
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Git Branching & Release Strategy

## 1. Overview

Northwind uses a trunk-based development model with feature branches. All code flows through `main` (production-ready) and is deployed via GitHub Actions CI/CD pipelines (see **GitHub Actions CI/CD Pipeline Guide** for details).

## 2. Branch Strategy

### 2.1 Main Branches

**main** (production)
- Always deployable state
- Every commit can go to production
- Tag format: `v<MAJOR>.<MINOR>.<PATCH>` (semantic versioning)
- Deployment: Manual trigger via GitHub Actions (see **Production Deployment Runbook**)

**staging** (pre-production)
- Integration branch for validation before production
- Auto-deploys 1 hour after merge to `main`
- Allows for 8-hour smoke test window (see **Production Deployment Runbook**)
- Deleted and recreated from `main` every Monday 6 AM PT

### 2.2 Feature Branches

**Naming convention:**
- Feature: `feature/brief-description` (e.g., `feature/add-salesforce-connector`)
- Bugfix: `bugfix/issue-number` (e.g., `bugfix/gh-1234`)
- Refactor: `refactor/component-name` (e.g., `refactor/api-gateway-logging`)
- Docs: `docs/what-changed` (e.g., `docs/update-sre-playbook`)

**Lifetime:**
- Created from `main`
- Pushed to GitHub; PR opened immediately (prevents stale branches)
- Code review completed (see **Code Review Standards**)
- Merged to `main` by PR author (do not auto-merge)
- **Deleted after merge** (keep repo clean)

## 3. Release Process

### 3.1 Version Numbers

Semantic versioning: `v<MAJOR>.<MINOR>.<PATCH>`

- **MAJOR** (v2.0.0): Breaking API changes, major features (approved by CEO + VP Product)
- **MINOR** (v1.5.0): New features, backward-compatible (approved by VP Engineering)
- **PATCH** (v1.4.1): Bugfixes, performance improvements (approved by team lead; auto-deploys)

### 3.2 Release Cadence

| Release Type | Frequency | Trigger | Approval |
|--------------|-----------|---------|----------|
| **PATCH** | 2–3 times per week | Bugfixes, hotfixes | Auto (CI passes) |
| **MINOR** | Monthly (first Monday) | Feature releases | VP Engineering sign-off |
| **MAJOR** | Quarterly (or ad-hoc) | Strategic initiatives | CEO + Board approval |

### 3.3 Release Checklist

Before merging a MINOR or MAJOR release:

1. **Changelog**: Update `CHANGELOG.md` with all changes since last release
   ```
   ## [1.5.0] - 2026-06-15
   ### Added
   - Support for Salesforce data connector (#456)
   - New audit dashboard for compliance team

   ### Fixed
   - Memory leak in transformation engine (#445)

   ### Security
   - Upgrade OpenSSL to 3.0.4 (CVE-2023-XXXX)
   ```

2. **Release notes**: Draft customer-facing release notes (send to VP Product for approval)
3. **Migration guide**: If database changes, provide step-by-step customer upgrade path
4. **Rollback plan**: Document how to rollback if production incidents occur
5. **Communication**: Schedule announcements in Slack `#deployments` channel 48 hours before release

### 3.4 Release Tag

Tag all releases in GitHub:
```bash
git tag -a v1.5.0 -m "Release v1.5.0: Salesforce connector + audit dashboard"
git push origin v1.5.0
```

## 4. Hotfix Procedure (Production Incidents)

If a Sev-2 or Sev-1 incident occurs in production (see **Incident Response Runbook**):

1. **Create hotfix branch**: `hotfix/incident-number` (e.g., `hotfix/gh-1234`)
2. **Expedited review**: 1 approval minimum, 15-minute window (see **Code Review Standards** for hotfix exception)
3. **Merge to main**: Bypasses standard staging validation
4. **Tag as patch**: `v1.4.2-hotfix` or `v1.4.3` (next patch version)
5. **Deploy to production**: Manual deploy with on-call engineer monitoring
6. **Post-incident review**: Full code review completed within 24 hours

Example timeline:
- 14:05 – Incident reported (API errors, 5% error rate)
- 14:10 – Hotfix branch created, code written
- 14:20 – Expedited review approved
- 14:25 – Merged to main, deployed to production
- 14:50 – Error rate returns to normal
- Day 2 – Post-mortem and full code review completed

## 5. Commit Message Standards

All commits must follow Conventional Commits format:

```
type(scope): subject (50 chars max)

body (72 chars per line, explain what and why, not how)

footer (issue tracking, breaking changes)
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `security`

**Examples:**
```
feat(data-connector): add Salesforce API integration

Adds support for Salesforce data source connections. Implements OAuth2 flow
for authentication and paginated data fetching. New service includes rate
limiting (100 req/min) and retry logic per API documentation.

Closes #456
```

```
security(secrets): remove hardcoded API key from config

Moves SendGrid API key to environment variable. Updates GitHub Actions
secret configuration and deploys to staging for testing.

See SECRETS_MANAGEMENT_STANDARD for details.
```

## 6. Branch Protection Rules

The following rules are enforced by GitHub:

| Rule | Branch | Enforcement |
|------|--------|-------------|
| Require PR reviews | main | Yes (2 approvals) |
| Dismiss stale reviews | main | Yes (auto-dismiss if new commits pushed) |
| Require status checks | main | Yes (all CI checks must pass) |
| Require up-to-date PR | main | Yes (must rebase before merge) |
| Allow force push | main | No (never allowed; protects against accidental deletion) |
| Allow deletions | main | No |

**Staging branch**: Same rules as main, enforced via branch protection

## 7. Integration with CI/CD

GitHub Actions automatically:

1. **Runs tests** on all PRs (see **GitHub Actions CI/CD Pipeline Guide**)
2. **Blocks merge** if CI fails
3. **Auto-deploys** to staging after merge to main (1-hour delay)
4. **Auto-tags release** if `RELEASE=true` commit message flag set

Example: `git commit -m "fix: memory leak" --message "RELEASE=patch"` → Auto-tags as `v1.4.3`

## 8. Rollback Procedure

If production deployment causes issues:

1. **Incident declared**: On-call engineer calls incident hotline (see **Incident Response Runbook**)
2. **Rollback triggered**: `git revert <commit-hash>` creates new commit
3. **Re-deploy**: New commit deployed via **Production Deployment Runbook**
4. **Post-incident**: Root cause analysis and prevention measures

Rollback typically takes 15–30 minutes; see **Production Deployment Runbook** for deployment lead responsibilities.

---

**Related policies:**
- See **GitHub Actions CI/CD Pipeline Guide** for automated testing and deployment
- See **Code Review Standards** for hotfix expedited review exception
- See **Production Deployment Runbook** for deployment procedures
- See **Incident Response Runbook** for incident severity and escalation
