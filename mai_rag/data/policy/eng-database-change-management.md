---
title: Database Change Management
doc_id: eng-database-change-management
owner: DBA Team
last_updated: 2026-06-01
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Database Change Management

## 1. Overview

Database changes are high-risk operations affecting data availability, integrity, and compliance. All changes follow a structured process with DBA approval and staged rollout.

## 2. Types of Database Changes

| Change Type | Complexity | Approval | Rollout | Validation |
|-------------|-----------|----------|---------|------------|
| **Add column (nullable)** | Low | DBA | Rolling | Auto (schema validation) |
| **Add index** | Low | DBA | Rolling | Performance test (staging) |
| **Add table** | Medium | DBA | Rolling | Application integration test |
| **Modify column (add constraint)** | Medium | DBA + Engineering | Rolling | Manual verification |
| **Drop column** | Medium | DBA + VP Engineering | Phased (3 releases) | Application regression testing |
| **Alter primary key** | High | DBA + VP Engineering + CEO approval | Manual (off-hours) | Full regression suite |
| **Database migration (replatform)** | Critical | DBA + VP Engineering + VP Operations | Manual (change window) | Complete cutover testing |

## 3. Change Request Process

### 3.1 Pre-Change: Planning Phase

1. **Author creates change request** (Jira ticket or GitHub issue):
   - **Description**: What is changing and why?
   - **Impact analysis**: Which services/queries affected?
   - **Rollback plan**: How to undo if issues occur?
   - **Estimated downtime**: 0 (rolling) or X minutes (maintenance window)?

2. **DBA reviews**:
   - Schema compatibility with all services (see **Service Catalog**)
   - Performance implications (index strategy, query optimization)
   - Replication/backup impact
   - Approves with sign-off comment

3. **Acceptance criteria**:
   - [ ] PR merged to main (see **Code Review Standards**)
   - [ ] Staging validation passed (8-hour window; see **Production Deployment Runbook**)
   - [ ] DBA and engineering approvals documented
   - [ ] Change window scheduled (if required)

### 3.2 Migration Scripts

All database changes are defined as versioned migration scripts:

```
migrations/
├── 2026_06_001_add_audit_table.sql
├── 2026_06_002_add_salesforce_connector_index.sql
├── 2026_06_003_backfill_customer_segment_column.sql
└── 2026_06_004_drop_legacy_cache_table.sql
```

**Script format** (PostgreSQL):
```sql
-- 2026_06_001_add_audit_table.sql
-- Author: dba-team@northwind.com
-- Purpose: New audit event logging for compliance
-- Rollback: DROP TABLE IF EXISTS audit_events CASCADE;

BEGIN TRANSACTION;

-- Create table with NOT NULL constraints on key columns
CREATE TABLE IF NOT EXISTS audit_events (
  id BIGSERIAL PRIMARY KEY,
  event_type VARCHAR(50) NOT NULL,
  actor_id INTEGER NOT NULL,
  resource_id VARCHAR(255) NOT NULL,
  action VARCHAR(20) NOT NULL,
  old_value JSONB,
  new_value JSONB,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ip_address INET,
  user_agent VARCHAR(500),
  
  CHECK (action IN ('CREATE', 'UPDATE', 'DELETE'))
);

-- Create indexes for common queries
CREATE INDEX idx_audit_actor_id ON audit_events(actor_id);
CREATE INDEX idx_audit_resource_id ON audit_events(resource_id);
CREATE INDEX idx_audit_created_at ON audit_events(created_at DESC);

-- Grant permissions
GRANT SELECT ON audit_events TO app_readonly;
GRANT SELECT, INSERT ON audit_events TO app_readwrite;

COMMIT;
```

### 3.3 Staging Validation

1. **Deploy to staging** (automatic with main branch; see **Production Deployment Runbook**)
2. **DBA validates**:
   - Schema correct: `\d+ audit_events` (psql command)
   - Indexes present: `SELECT * FROM pg_indexes WHERE tablename='audit_events'`
   - Constraints working: Attempt invalid insert (should fail)
3. **Application validates**:
   - Run integration tests against new schema
   - Query performance acceptable (compare execution plans before/after)
4. **Sign-off**: DBA approves for production (comment in PR or Jira)

## 4. Production Rollout

### 4.1 Zero-Downtime Changes (Nullable Columns, Indexes, New Tables)

These changes are applied during regular deployment and do not require a maintenance window:

```bash
# During standard deployment (see PRODUCTION_DEPLOYMENT_RUNBOOK)
# 1. Deployment lead runs migration script against production
./scripts/migrate.sh production 2026_06_001_add_audit_table.sql

# 2. Verify schema change applied
psql -h northwind-db.postgres.database.azure.com -U postgres -d northwind \
  -c "SELECT column_name FROM information_schema.columns WHERE table_name='audit_events';"

# 3. Monitor: DBA watches replication lag (should be < 100ms)
# 4. Service restart: Update all microservice replicas with new schema awareness
# 5. Validation: Run smoke tests (see PRODUCTION_DEPLOYMENT_RUNBOOK)
```

**Backward compatibility requirement**: Application must handle both old and new schema during rollout. Example:
```python
# Python app: Graceful handling of nullable column
def insert_audit_event(event_type, actor_id, resource_id, action):
    # Column 'ip_address' is new; app works even if not provided
    query = """
        INSERT INTO audit_events 
        (event_type, actor_id, resource_id, action, ip_address)
        VALUES (%s, %s, %s, %s, %s)
    """
    # Safely handle if ip_address is None
    cursor.execute(query, (event_type, actor_id, resource_id, action, ip_address or None))
```

### 4.2 Downtime Changes (Alter PK, Replatform, Major Refactoring)

High-risk changes require a scheduled maintenance window:

1. **Maintenance window announced** (see **Production Deployment Runbook**):
   - 48 hours notice to all customers
   - Expected downtime: 30–60 minutes
   - Scheduled for Tuesday 2–4 AM PT (low-traffic window)

2. **Pre-change validation**:
   - [ ] Full backup of production database (separate copy created)
   - [ ] Rollback plan tested on backup
   - [ ] All services scaled up (no background jobs running during change)

3. **Change execution**:
   ```bash
   # Step 1: Announce in Slack #deployments
   # Step 2: Stop all application servers gracefully
   pm2 stop all
   
   # Step 3: Run migration (may take 10–45 minutes depending on table size)
   psql -h northwind-db.postgres.database.azure.com -U postgres -d northwind \
     -f migrations/2026_06_004_alter_customer_primary_key.sql
   
   # Step 4: Verify migration success
   psql -c "SELECT COUNT(*) FROM customers;"
   
   # Step 5: Restart application servers
   pm2 start all
   
   # Step 6: Smoke tests
   curl https://api.northwind.com/health
   ```

4. **Post-change**:
   - Monitor error rates for 30 minutes (< 0.1% 5xx errors)
   - DBA validates replication lag (< 100ms)
   - Customer notification sent (change complete, no impact)

## 5. Rollback Procedure

If issues occur after a production change:

### 5.1 Fast Rollback (Nullable Column, Index, New Table)

Most schema changes are reversible via simple SQL:

```bash
# Immediate rollback (< 5 minutes)
psql -h northwind-db.postgres.database.azure.com -U postgres -d northwind \
  -c "ALTER TABLE audit_events DROP COLUMN ip_address;" # if change reverted quickly
```

**Decision criteria**:
- If issue detected < 30 minutes post-deploy: Rollback immediately
- If issue detected 30+ minutes post-deploy: Investigation required (data may be corrupt; restore from backup instead)

### 5.2 Full Rollback (Data Loss Risk)

For changes with data corruption risk:

1. **Stop application** (no new writes)
2. **Restore from backup** (taken pre-change)
3. **Verify integrity** (compare checksum to pre-change snapshot)
4. **Restart services**
5. **Post-mortem** (what caused the issue? how to prevent?)

**RTO**: 15–45 minutes depending on database size and backup restore speed.

See **Incident Response Runbook** and **Disaster Recovery & Backup Runbook** for incident escalation.

## 6. Impact Analysis and Testing

### 6.1 Cross-Service Impact

Before production, verify all affected services work with new schema:

```bash
# Query dependency map (Datadog)
curl https://api.datadoghq.com/api/v2/apm/services \
  -H "Authorization: apiKey <DATADOG_API_KEY>" | jq '.data[] | select(.type == "db")'

# Which services query the audit_events table?
grep -r "audit_events" kapi-platform/services/ | grep -E "\.(ts|py|go|java):"
```

### 6.2 Query Performance

Before production, validate performance impact:

```bash
-- Compare query plans (EXPLAIN ANALYZE)
-- Before change:
EXPLAIN ANALYZE SELECT * FROM audit_events WHERE actor_id = 42;
-- Expected: Index scan on idx_audit_actor_id

-- After change:
EXPLAIN ANALYZE SELECT * FROM audit_events WHERE actor_id = 42 AND created_at > NOW() - INTERVAL '7 days';
-- Expected: Index scan, filter on created_at (should not degrade)
```

## 7. Phased Column Deprecation (Multi-Release)

To remove a column without breaking existing code:

**Release 1** (this release): Deprecate
```sql
ALTER TABLE customers ADD COLUMN legacy_phone_field_removed_v1_6_0 VARCHAR(20);
ALTER TABLE customers DROP COLUMN phone_field;
```

**Release 2** (2 weeks later): Application stops using old field
- Code review: Search for any reads/writes to phone_field
- If found, update code before merging

**Release 3** (2 weeks later): Clean up
```sql
ALTER TABLE customers DROP COLUMN legacy_phone_field_removed_v1_6_0;
```

This 3-release window ensures backward compatibility if customers delay upgrades.

## 8. Documentation and Compliance

All production changes logged for audit:

- **Change ticket**: Jira issue with approval chain and execution log
- **Git commit**: SQL migration script with explanation
- **Execution log**: Timestamp, duration, executed by, verification results
- **Compliance**: For Confidential/Restricted data changes, compliance team notified (see **Data Classification & Retention Policy**)

---

**Related policies:**
- See **Code Review Standards** for schema change code review
- See **Production Deployment Runbook** for deployment scheduling
- See **Disaster Recovery & Backup Runbook** for backup and recovery procedures
- See **Information Security Policy** for access control to production database
