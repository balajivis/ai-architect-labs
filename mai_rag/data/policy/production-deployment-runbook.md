---
title: Production Deployment Runbook
doc_id: production-deployment-runbook
owner: Engineering Leadership
last_updated: 2026-02-28
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Production Deployment Runbook

## 1. Overview

This runbook defines the process for deploying code and infrastructure changes to Northwind's production environment. All deployments must follow this process to ensure stability, traceability, and safety.

## 2. Deployment Philosophy

**Northwind prioritizes stability and customer uptime.** Our production SLA is 99.9% uptime (4.38 hours downtime per year). All deployments must be:
- Traceable (commit linked to change request)
- Reviewable (code review completed before merge)
- Reversible (rollback procedure defined before deploy)
- Testable (changes tested in staging environment first)

## 3. Pre-Deployment Checklist

### 3.1 Code Review and Approval

Before any deployment:

1. **Feature branch**: Code is developed on a feature branch (`feature/name` or `bugfix/name`)
2. **Pull request**: PR is opened against `main` branch with description of changes
3. **Code review**: At least 2 approvals required from team members
   - For security changes: VP Security or Security Team must approve
   - For infrastructure changes: DevOps lead must approve
4. **Automated tests pass**: CI pipeline must pass (unit tests, integration tests, linting)
5. **Merge**: PR is merged to `main` by PR author (not auto-merged)

### 3.2 Staging Validation

1. **Deploy to staging**: Merged code is automatically deployed to staging environment
2. **Smoke tests**: Automated smoke test suite must pass (customer login, API health, core workflows)
3. **Manual testing**: QA team performs functional testing per test plan (duration: 2–8 hours depending on scope)
4. **Performance check**: No significant latency increase vs. previous version

**Definition of success**: All tests pass AND no customer-reported issues during 8-hour staging window.

### 3.3 Deployment Window Planning

1. **Schedule**: Deployments must be scheduled during **normal business hours (9 AM–5 PM PT, Monday–Friday)**
   - Exception: Critical fixes to resolve customer-impacting incidents may deploy outside business hours (see Incident Response Runbook)

2. **Stakeholder notification**: Announce planned deployment in #deployments Slack channel at least 2 hours before deploy
   - Include: What's changing, deployment start time, expected duration (typically 15–30 minutes)

3. **On-call readiness**: Confirm on-call engineer is available to monitor deployment and respond to issues

## 4. Deployment Execution

### 4.1 Pre-Deployment Verification (10 minutes before)

**Deployment lead verifies:**
- [ ] All code reviews approved
- [ ] CI pipeline passed
- [ ] Staging tests passed
- [ ] On-call engineer is available and monitoring
- [ ] Database migrations are backward-compatible (if applicable)
- [ ] Rollback plan is documented and ready

### 4.2 Deployment Process

1. **Trigger deploy**: Execute deployment command (CI/CD pipeline automated)
   ```
   # Example (tool varies by product)
   npm run deploy:production
   ```

2. **Monitoring**: Deployment typically takes 15–30 minutes
   - New code is deployed in a rolling fashion (3–5 servers at a time)
   - Old servers continue serving traffic during rollout
   - No customer-facing downtime expected

3. **Health checks**: Automated health checks verify each deployed server is healthy
   - API endpoints respond (HTTP 200)
   - Database connections succeed
   - Critical workflows execute (simulated customer action)

4. **Rollout complete**: Once all servers are deployed, deployment is complete

### 4.3 Post-Deployment Validation (30 minutes after)

**On-call engineer monitors:**
- [ ] Error rates normal (< 0.1% 5xx errors)
- [ ] Latency acceptable (p99 < 500ms)
- [ ] Customer reports: No critical issues in support queue
- [ ] Business metrics: Revenue, conversion, API usage trending normal

**If issues detected**: Execute rollback (see Rollback section)

**If all clear**: Document deployment in #deployments and close change request

### 4.4 Rollback Procedure

If a deployment introduces a critical issue:

1. **Assess severity** (see Incident Response Runbook):
   - **Sev-1** (complete outage, customer data exposed): Immediate rollback
   - **Sev-2** (significant degradation): Rollback within 30 minutes
   - **Sev-3** (minor feature broken): May fix forward if fix is ready; otherwise rollback

2. **Execute rollback**:
   ```
   npm run rollback:production
   ```

3. **Verify rollback**: Confirm that previous stable version is running
   - Re-run health checks
   - Verify error rates return to normal

4. **Notification**: Announce rollback in #deployments and notify executive team (for Sev-1)

5. **Root cause analysis**: Team holds blameless post-mortem within 24 hours (see Incident Response Runbook)

## 5. Database Migrations

### 5.1 Safe Migration Practices

All database schema changes must be backward-compatible:

- **Add column**: Safe; can add with default value or nullable
- **Remove column**: Unsafe (old code expects column); must remove in separate deployment after old code is removed
- **Rename column**: Unsafe; create new column, migrate data, remove old column in later deploy
- **Add index**: Safe; non-blocking on production (async)
- **Add foreign key constraint**: Safe if data is already valid; test in staging first

### 5.2 Migration Testing

1. **Test on staging database**: Run migration script on staging (prod-like data snapshot)
2. **Verify data integrity**: Post-migration queries confirm correct data state
3. **Test rollback**: Verify migration can be reversed if needed

### 5.3 Large Table Migrations

For tables with 10M+ rows, migrations may take hours. Coordinate with ops:
- Run during low-traffic window
- Use online migration tools (pt-online-schema-change) if available
- Plan for reduced performance during migration

## 6. Infrastructure Changes

### 6.1 Changes Requiring Deployment Review

- Database configuration changes (pool size, timeout, encryption)
- Load balancer rules or SSL certificates
- Container orchestration changes (Kubernetes configs)
- Security group/firewall rule changes
- Cloud resource changes (VM sizing, storage, backups)

### 6.2 Approval Process for Infrastructure

1. **Document change**: File describes what is changing and why
2. **Staging test**: Change is applied to staging environment first; verify no impact
3. **Risk assessment**: Is this change reversible? Can we roll back in < 5 minutes?
4. **Approvals**: VP Engineering + VP Operations approve
5. **Change control**: Create change ticket (ServiceNow or similar) for audit trail

## 7. Feature Flags and Gradual Rollout

For high-risk features, use feature flags to roll out to a subset of users:

1. **Feature flag enabled in code**: `if (FEATURE_FLAG_NEW_DASHBOARD) { ... }`
2. **Deploy with flag OFF**: No users see new feature initially
3. **Gradually enable**: Enable for 5% → 25% → 100% of users over hours/days
4. **Monitor**: Error rates and customer feedback at each step
5. **Rollback if needed**: Disable flag to instantly hide feature; fix code; re-deploy

## 8. Deployment Logs and Auditing

- All deployments are logged with: timestamp, user, code version (git commit hash), change description
- Logs retained for 1 year (audit compliance)
- Deployment metrics (success rate, rollback rate, lead time) tracked monthly

## 9. Emergency Hotfixes

**Definition**: Critical customer-impacting bug discovered in production that must be fixed immediately.

1. **Assess severity** per Incident Response Runbook (likely Sev-1 or Sev-2)
2. **Create emergency branch** from `main`: `hotfix/description`
3. **Code fix and minimal review**: Pair programming or single review acceptable
4. **Skip staging** if downtime risk is greater: deploy directly to production (with on-call standing by for rollback)
5. **Notification**: Announce emergency deploy in #deployments and notify CEO/COO (for Sev-1)
6. **Post-mortem**: Conduct root cause analysis within 24 hours to prevent recurrence

## 10. Deployment Frequency and Targets

**Northwind deployment targets** (measured monthly):

- **Deployment frequency**: 20+ production deployments per month (multiple per day)
- **Lead time**: < 4 hours from code commit to production (measured median)
- **Failure rate**: < 10% of deployments require rollback
- **MTTR** (Mean Time To Recover): < 30 minutes (time from issue detection to rollback complete)

These metrics drive continuous improvement in deployment safety.

## 11. Documentation and Change Control

Every deployment must have:
- [ ] Git commit(s) linking to code changes
- [ ] GitHub PR with description of changes
- [ ] Deployment ticket (change request) with approval dates
- [ ] Rollback procedure documented (if not standard rollback)

Change requests are archived for 3 years for audit and compliance.

## 12. Escalation and Support

**Deployment questions**: #deployments Slack channel or devops@northwind.com  
**Deployment emergency**: On-call engineer (pager) + #deployments + VP Engineering

---

**Document owner:** VP Engineering  
**Last approved:** 2026-02-28 by Engineering Leadership  
**Next review:** 2027-02-28

**Related policies:**
- **Incident Response Runbook**: Severity escalation and post-mortem process
- **Information Security Policy**: Security review for deployment changes
- **On-Call & Escalation Policy**: On-call engineer responsibilities during deployment
