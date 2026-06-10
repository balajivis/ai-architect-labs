---
title: Disaster Recovery & Backup Runbook
doc_id: eng-disaster-recovery-backup-runbook
owner: DBA Team
last_updated: 2026-06-01
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Disaster Recovery & Backup Runbook

## 1. Overview

This runbook defines how Northwind backs up critical data and recovers from disasters (data loss, corruption, regional outages). All databases and persistent storage follow this procedure.

## 2. Backup Strategy

### 2.1 What Gets Backed Up

| Asset | Backup Type | Frequency | Retention | RTO | RPO |
|-------|-------------|-----------|-----------|-----|-----|
| **PostgreSQL databases** | Automated snapshots + log shipping | Hourly snapshots + continuous WAL | 30 days | 2h | 5 min |
| **Application configs** | Git version control | Per commit | Indefinite | 15 min | 0 (code) |
| **S3 buckets** (document storage) | Cross-region replication | Real-time | 30 days | 1h | < 1 min |
| **Kubernetes state** | etcd snapshots | Daily | 7 days | 4h | 1h |
| **Container images** (ECR) | Automated replication | Per push | 180 days | 30 min | 0 |

### 2.2 Backup Storage Locations

```
Primary (AWS us-east-1):
├─ Database: RDS managed backup to S3 northwind-rds-backups-east
├─ S3 data: Regional replication to us-west-2
├─ Container images: ECR northwind-prod-east (replicated to northwind-prod-west)
└─ Configs: GitHub (replicated via cross-account backup)

Secondary (Azure secondary region):
├─ Database: PostgreSQL Flexible Server geo-redundant backup
├─ Application data: Azure blob storage geo-replication
└─ Configs: Azure DevOps git repo (cross-region)
```

## 3. Backup Verification

### 3.1 Automated Backup Testing

Every Sunday 3 AM PT, automated DR drill runs:

```bash
#!/bin/bash
# scripts/dr-drill.sh (runs via GitHub Actions scheduled)

# 1. Restore production database snapshot to isolated "dr-test" environment
aws rds restore-db-instance-from-db-snapshot \
  --db-snapshot-identifier northwind-db-prod-$(date +%Y%m%d) \
  --db-instance-identifier northwind-db-test-dr-$(date +%Y%m%d)

# 2. Wait for restore to complete
aws rds wait db-instance-available \
  --db-instance-identifier northwind-db-test-dr-$(date +%Y%m%d)

# 3. Run smoke tests against restored database
npm run test:integration \
  DATABASE_URL=postgresql://test@northwind-db-test.rds.amazonaws.com/northwind

# 4. Verify data integrity (row count, checksums)
psql -h northwind-db-test.rds.amazonaws.com -U postgres northwind \
  -c "SELECT COUNT(*) as total_rows FROM customers;" \
  > test-results/row-count-$(date +%Y%m%d).txt

# 5. Clean up test instance
aws rds delete-db-instance \
  --db-instance-identifier northwind-db-test-dr-$(date +%Y%m%d) \
  --skip-final-snapshot

# 6. Report results
echo "DR Drill Complete: $(date)" | mail -s "DR Test Results" sre-team@northwind.com
```

**Verification checklist**:
- [ ] Snapshot restored successfully
- [ ] Smoke tests passed
- [ ] Row count matches production (within 1%)
- [ ] No corruption detected
- [ ] Cleanup completed

### 3.2 Recovery Time Objective (RTO) Validation

Test quarterly that recovery meets RTO target:

```
Scenario: Complete database loss in us-east-1 region
Procedure:
  1. Activate secondary region (Azure or us-west-2)
  2. Restore latest backup to secondary
  3. Update DNS to point to secondary
  4. Validate services operational
  5. Time from incident start to full recovery: <= 2 hours (RTO target)
```

## 4. Disaster Scenarios and Recovery

### 4.1 Data Corruption (Single Table)

**Symptom**: Application reports incorrect data in one table (e.g., customer records)

**Recovery**:
```bash
# Step 1: Identify corruption scope
SELECT COUNT(*) as corrupted_rows FROM customers WHERE status NOT IN ('active', 'inactive', 'suspended');
# Result: 1,247 corrupted rows

# Step 2: Stop writes to table (lock application briefly)
pm2 restart api-gateway transformation-engine  # Graceful restart to clear connection pool

# Step 3: Restore table from point-in-time backup (last good known time)
pg_restore -d northwind --data-only \
  --table customers \
  northwind-backup-$(date +%Y%m%d_%H%M%S_before_corruption).sql

# Step 4: Verify restore
SELECT COUNT(*) as total FROM customers;
SELECT COUNT(*) as valid FROM customers WHERE status IN ('active', 'inactive', 'suspended');

# Step 5: Re-enable writes and restart services
pm2 restart all
psql -h northwind-db-prod -U postgres northwind -c "VACUUM ANALYZE customers;"

# Step 6: Post-incident: Determine corruption cause (corrupted input, application bug)
```

**RTO**: 30 minutes (if corruption detected quickly)  
**RPO**: Up to 1 hour (last PITR checkpoint)

### 4.2 Entire Database Loss (Ransomware)

**Symptom**: All data deleted/encrypted; application fails with "database does not exist"

**Recovery**:
```bash
# Step 1: Incident declared — Sev-1
# Notify: CEO, VP Security, VP Engineering, CTO, General Counsel (see INCIDENT_RESPONSE_RUNBOOK)

# Step 2: Isolate (prevent spread)
# - Revoke all database credentials (immediately)
# - Disconnect application servers from network (AWS Security Groups)
# - Preserve evidence (snapshots of all EBS volumes)

# Step 3: Restore from offline backup (kept in separate account)
# Use backup from < 24 hours ago (unaffected by ransomware)
aws rds restore-db-instance-from-db-snapshot \
  --db-snapshot-identifier northwind-db-prod-$(date -d yesterday +%Y%m%d) \
  --db-instance-identifier northwind-db-prod-restored \
  --db-subnet-group-name northwind-prod-db-subnet \
  --vpc-security-group-ids sg-prod-db

# Step 4: Update database endpoint in application config
kubectl set env deployment/api-gateway \
  DATABASE_URL=postgresql://northwind@northwind-db-prod-restored.rds.amazonaws.com/northwind \
  -n northwind-prod

# Step 5: Deploy latest application code to fresh instances
kubectl set image deployment/api-gateway \
  api-gateway=northwind-prod-east.dkr.ecr.us-east-1.amazonaws.com/api-gateway:latest \
  -n northwind-prod

# Step 6: Verify service health
kubectl rollout status deployment/api-gateway -n northwind-prod
curl https://api.northwind.com/health

# Step 7: Validate data integrity
psql -h northwind-db-prod-restored.rds.amazonaws.com -U postgres northwind \
  -c "SELECT COUNT(*) as customers FROM customers; SELECT COUNT(*) as orders FROM orders;"
```

**RTO**: 2 hours (restore database, restart services, validate)  
**RPO**: 24 hours (one-day-old backup)  
**Customer impact**: Announce SLA breach immediately (see **Incident Response Runbook**)

### 4.3 Regional Outage (AWS us-east-1 down)

**Symptom**: All services in us-east-1 unavailable; CloudWatch metrics unavailable

**Recovery** (failover to secondary region):
```bash
# Step 1: Determine outage scope
# Check AWS status page: https://status.aws.amazon.com/

# Step 2: Activate secondary region (us-west-2)
# Update Route53 DNS to point to us-west-2 endpoints (TTL: 60 seconds)
aws route53 change-resource-record-sets \
  --hosted-zone-id Z2FDTNDATAQYW2 \
  --change-batch '{
    "Changes": [{
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "api.northwind.com",
        "Type": "CNAME",
        "TTL": 60,
        "ResourceRecords": [{"Value": "api-west.northwind.com"}]
      }
    }]
  }'

# Step 3: Restore database to us-west-2 from backup
aws rds restore-db-instance-from-db-snapshot \
  --db-snapshot-identifier northwind-db-prod-latest \
  --db-instance-identifier northwind-db-prod-west \
  --region us-west-2

# Step 4: Verify application in secondary region
curl https://api-west.northwind.com/health

# Step 5: Monitor for region recovery
# Once us-east-1 recovered: sync databases, switch DNS back to primary

# Step 6: Post-incident: Implement hot standby (reduce RTO from 2h to 30min)
```

**RTO**: 1–2 hours (failover to secondary, DNS propagation)  
**RPO**: < 1 hour (continuous replication)

## 5. Backup Compliance and Auditing

### 5.1 Backup Audit Checklist

Monthly, DBA team verifies:

- [ ] All databases have automated backups enabled
- [ ] Backup retention policies match compliance requirements (30 days minimum)
- [ ] Backup encryption enabled (KMS keys rotated per **Secrets Management Standard**)
- [ ] Cross-region replication enabled for production
- [ ] Backup access restricted to DBA team only
- [ ] DR drill completed successfully (latest results documented)

### 5.2 Backup Logs

All backup operations logged in Datadog:

```json
{
  "timestamp": "2026-06-01T03:00:00Z",
  "event": "backup_completed",
  "database": "northwind-db-prod",
  "backup_id": "rds:northwind-db-prod-2026-06-01-0300",
  "size_gb": 87.5,
  "duration_minutes": 15,
  "status": "success",
  "encryption": "AES256-KMS",
  "region": "us-east-1",
  "retention_days": 30
}
```

## 6. Backup Restore Procedure (Non-Emergency)

To restore a specific backup in non-emergency scenarios:

```bash
# 1. List available backups
aws rds describe-db-snapshots \
  --db-instance-identifier northwind-db-prod \
  --query 'DBSnapshots[*].[DBSnapshotIdentifier,SnapshotCreateTime]' \
  --output table

# 2. Restore to temporary instance (non-prod)
aws rds restore-db-instance-from-db-snapshot \
  --db-snapshot-identifier northwind-db-prod-2026-05-15-0300 \
  --db-instance-identifier northwind-db-temp-restore

# 3. Validate restored data
psql -h northwind-db-temp-restore.rds.amazonaws.com -U postgres northwind \
  -c "SELECT COUNT(*) as total FROM customers;"

# 4. If valid, migrate data to production
# Option A (if minor corruption): Restore single table
pg_restore -d northwind --data-only --table customers northwind-snapshot.sql

# Option B (if major issues): Swap database endpoints
# Update application config to point to restored instance

# 5. Clean up temporary instance
aws rds delete-db-instance \
  --db-instance-identifier northwind-db-temp-restore
```

## 7. Disaster Recovery Drill (Quarterly)

Every Q (March, June, September, December), DBA team runs full DR drill:

**Agenda**: 4-hour exercise
1. **Kickoff** (30 min): Scenario briefing (e.g., "ransomware attack; entire database lost")
2. **Execution** (2 hours): Follow recovery procedure; time critical operations
3. **Validation** (1 hour): Verify system operational; data integrity checks
4. **Debrief** (30 min): Lessons learned; update runbook if needed

**Participants**: DBA team, DevOps lead, on-call engineer, VP Engineering

**Success criteria**:
- Database restored within RTO target
- Services operational within 30 minutes
- Data integrity verified
- No critical findings blocking production
- Post-drill report published to leadership

---

**Related policies:**
- See **Database Change Management** for backup impact of schema changes
- See **Incident Response Runbook** for incident declaration and escalation
- See **Information Security Policy** for backup encryption and access control
- See **Secrets Management Standard** for KMS key rotation
