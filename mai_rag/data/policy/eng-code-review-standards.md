---
title: Code Review Standards
doc_id: eng-code-review-standards
owner: VP Engineering
last_updated: 2026-06-01
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Code Review Standards

## 1. Purpose

Code review is the primary mechanism for maintaining code quality, security, and architectural consistency. Every change to production code must pass code review before merging to the main branch.

## 2. Review Requirements

### 2.1 Approval Thresholds

| Change Type | Minimum Approvals | Approver Role | Time to Review |
|-------------|-------------------|---------------|---|
| Feature (non-security) | 2 | Engineers | 24 hours |
| Bugfix (production-impacting) | 2 | Engineers | 12 hours |
| Security change | 1 | VP Security + 1 Engineer | 4 hours |
| Infrastructure change | 1 | DevOps Lead + 1 Engineer | 12 hours |
| Database migration | 1 | DBA + 1 Engineer | 12 hours |
| Secrets / credentials handling | 1 | VP Security (must verify no plaintext) | 2 hours |

### 2.2 Who Can Approve

- **Engineers**: Any engineer with 6+ months at Northwind and `write` access to the repository
- **Senior Engineers**: Can approve any change in their domain
- **Specialists**: VP Security (security), DBA (database), DevOps Lead (infrastructure), VP Engineering (architectural decisions)

**New contributors**: First 3 PRs require 1 additional approval from team lead, even if >= 2 engineer approvals received.

## 3. PR Checklist for Authors

Before requesting review, author must verify:

- [ ] **PR description** is clear: What changed, why, and any side effects
- [ ] **Tests written**: Unit tests for new code, integration tests for APIs (minimum 70% coverage for new code)
- [ ] **No hardcoded secrets**: Credentials, API keys, database passwords never in code (see **Secrets Management Standard**)
- [ ] **Backward compatibility**: Database migrations are backward-compatible or have rollback plan
- [ ] **Documentation**: README, ADR, or inline comments for non-obvious logic
- [ ] **Linting passes**: `npm run lint` or equivalent (enforced by CI; see **GitHub Actions CI/CD Pipeline Guide**)
- [ ] **Security scan passes**: SAST tool (Snyk) reports no critical/high vulnerabilities
- [ ] **No credential leaks**: Credential scanner (Truffles, git-secrets) passes

## 4. Reviewer Checklist

Reviewers must assess:

1. **Correctness**: Does the code do what the PR claims?
   - Verify test cases cover edge cases
   - Check for off-by-one errors, null pointer dereferences, race conditions
   - Validate error handling (don't silently swallow errors)

2. **Security**: Does this introduce a vulnerability?
   - No hardcoded secrets (see **Secrets Management Standard**)
   - No SQL injection vectors (use parameterized queries)
   - No XSS vulnerabilities (escape user input)
   - No insecure deserialization
   - Check authorization: Does the code verify user has permission?
   - See **Information Security Policy** for security checklist

3. **Performance**: Will this degrade system performance?
   - No new O(n²) algorithms without justification
   - No new database N+1 queries
   - New external API calls? Check timeout and retry policy

4. **Architecture**: Does this follow our patterns?
   - Aligns with **Microservices Architecture Overview**
   - Uses circuit breaker, bulkhead isolation where needed
   - Database queries follow schema ownership rules (see **Service Catalog**)
   - Follows **API Design Guidelines**

5. **Observability**: Can we debug this in production?
   - Structured logging present for important decisions
   - Prometheus metrics for business-critical paths
   - No sensitive data in logs (see **Secrets Management Standard**)

6. **Testing**: Is test coverage adequate?
   - Unit tests for business logic (minimum 70%)
   - Integration tests for cross-service APIs
   - E2E tests for critical workflows (deployed weekly to staging)

## 5. Common Review Comments and Standards

### 5.1 "Add Error Handling"

All external API calls must handle errors:
```go
// BAD: Silent failure
data, _ := fetchData(ctx)  // ignores error

// GOOD: Explicit error handling
data, err := fetchData(ctx)
if err != nil {
    return fmt.Errorf("failed to fetch: %w", err)  // wrap and propagate
}
```

### 5.2 "Use Parameterized Queries"

Never interpolate user input into SQL:
```python
# BAD: SQL injection vulnerability
query = f"SELECT * FROM users WHERE email = '{email}'"  # DANGEROUS

# GOOD: Parameterized query
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
```

### 5.3 "Add Observability"

Log important decisions; emit metrics for business workflows:
```go
// GOOD: Structured logging
log.Info("transformation_started", "service_id", serviceID, "record_count", count)
metrics.Increment("transformations.started", []string{fmt.Sprintf("service:%s", serviceID)})
```

### 5.4 "Request Denied: Insufficient Justification"

If a reviewer rejects a PR, they must provide:
1. **Specific issue**: Quote the problematic code
2. **Why it's a problem**: Security risk? Performance? Architecture violation?
3. **How to fix it**: Proposed solution or link to policy

Rejections without explanation are not valid; author can escalate to team lead.

## 6. Review Timeline and Escalation

| Scenario | Action |
|----------|--------|
| PR pending > 24 hours (non-security) | Assignee sends Slack reminder to reviewers |
| PR pending > 4 hours (security) | Assignee escalates to VP Security |
| Reviewer unavailable | Author reassigns to another qualified reviewer |
| Reviewers disagree | Team lead breaks tie |
| Author disagrees with rejection | Escalate to VP Engineering for final decision |

## 7. Special Cases

### 7.1 Hotfixes to Production

If a customer-impacting incident requires immediate fix:

1. **Expedited review** (1 approval, 15-minute window) allowed only for **Sev-1/Sev-2 incidents** (see **Incident Response Runbook**)
2. **Post-incident**: Full review completed within 24 hours
3. **Audit trail**: Expedited hotfixes logged in GitHub with incident ticket reference

Example: "Hotfix for Sev-2 incident #INC-12345 (customer API degradation)"

### 7.2 Database Migrations

All database changes must have DBA approval:

- **Forward compatibility**: New columns are nullable; drop columns only after 2 release cycles
- **Rollback plan**: Documented and tested before merge
- **See**: **Database Change Management** for full migration checklist

### 7.3 Infrastructure / DevOps Changes

Infrastructure PRs (Terraform, Helm, CI/CD) require:

1. **DevOps Lead** approval
2. **Staged rollout**: Changes deployed to staging first (see **Infrastructure as Code Standards**)
3. **Post-deploy validation**: Smoke tests automated (see **Production Deployment Runbook**)

## 8. Continuous Improvement

- **Monthly review metrics**: VP Engineering reports approval time and rejection rate to leadership
- **Quarterly calibration meeting**: Engineering team reviews common rejection patterns and refines standards
- **Annual audit**: Spot-check 20% of merged PRs to verify quality standards maintained

---

**Related policies:**
- See **GitHub Actions CI/CD Pipeline Guide** for automated checks that run before review
- See **Secrets Management Standard** for credential handling
- See **Information Security Policy** for security checklist
- See **Architecture Decision Record (ADR) Process** for documenting architectural decisions in code reviews
