---
title: Firewall Change Management
doc_id: itsec-firewall-change-management
owner: IT Infrastructure & Security
last_updated: 2026-04-13
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Firewall Change Management

## 1. Purpose and Scope

This policy establishes procedures for proposing, testing, approving, and deploying firewall rule changes across Northwind's network infrastructure. Changes include inbound/outbound rules, access lists, NAT policies, and threat prevention settings.

## 2. Firewall Infrastructure

### 2.1 Production Firewalls

| Firewall | Location | Model | Role | VLANs Protected |
|---|---|---|---|---|
| **Primary FW** | Austin HQ | Palo Alto PA-7060 (HA active-active) | Perimeter defense | Corporate, Development, Production, DMZ |
| **Secondary FW** | Offsite | Palo Alto PA-5220 | Failover / disaster recovery | All (replica of Primary) |
| **Edge FW** | AWS VPC | AWS Security Groups + Firewall Manager | Cloud perimeter | AWS subnets |

### 2.2 Current Baseline Rules

**Inbound (Internet → Northwind):**
- 443 (HTTPS) → Web servers in DMZ (CloudFlare, Akamai bypass)
- 22 (SSH) → Bastion host only (restricted to GitHub Actions IPs)
- All other inbound → Blocked

**Outbound (Northwind → Internet):**
- 443 (HTTPS) → Any (CDNs, SaaS, APIs)
- 25, 587 (SMTP) → Email vendors (SendGrid)
- 53 (DNS) → External resolvers
- All other outbound → Blocked

## 3. Change Request Process

### 3.1 Initiating a Change Request

Employee needing firewall rule change submits via Change Portal (change.northwind.com):

**Required fields:**
- **Business justification**: Why is the rule needed? What will it enable?
- **Source/destination**: IP ranges, ports, protocols (CIDR notation required)
- **Duration**: Permanent or temporary? If temporary, when should rule auto-expire?
- **Owner**: Who is responsible for this rule? (Department + manager approval required)
- **Data sensitivity**: Will this rule carry Public/Internal/Confidential/Restricted data?
- **Estimated impact**: How many users affected? What if rule blocks too much?

**Example:**
```
Title: Allow GitHub Actions to deploy to production
Business justification: Enable CI/CD deployment pipeline for prod releases
Source: 140.82.112.0/20 (GitHub Actions IP range)
Destination: 10.10.50.0/24 (prod web servers, port 443)
Protocol: TCP/443 (HTTPS)
Duration: Permanent
Owner: VP Engineering (john.smith@northwind.com)
Data sensitivity: Production API calls (Internal + Confidential)
Estimated impact: All deployments will route through this rule (~50 pushes/day)
```

### 3.2 Review Workflow

1. **Tier 1 – IT Infrastructure** (2 business days)
   - Technical review: Does rule syntax make sense? Is CIDR notation valid?
   - Redundancy check: Does a similar rule already exist?
   - Scope check: Is rule overly broad (e.g., 0.0.0.0/0 source)?
   - Status: Approved, Needs Details, or Rejected with reason

2. **Tier 2 – IT Security** (2 business days)
   - Security review: Does rule expose critical systems?
   - Data flow check: Does rule carry Confidential/Restricted data securely?
   - Threat assessment: Could rule enable attack (e.g., allow reverse shell outbound)?
   - Status: Approved, Approved with Conditions, or Rejected with reason

3. **Tier 3 – Change Advisory Board (CAB)** (2 business days)
   - CAB members: IT Director, VP Security, VP Engineering, Network Manager
   - CAB decides: Approve, hold for discussion, or reject
   - Emergency override: VP Security can approve critical rules without CAB if incident active

4. **Implementation approval**: After all tiers pass, rule scheduled for deployment

### 3.3 Implementation Window

Standard rule deployment occurs during **monthly change window: 2nd Tuesday, 10 PM–2 AM PT**.

**Emergency rules** may be deployed outside window if:
- Active security incident (e.g., block DDoS source)
- Production outage requiring urgent fix
- VP Security approval obtained

Emergency rules logged as exception; reviewed in monthly governance meeting.

## 4. Testing and Validation

### 4.1 Pre-Deployment Testing

Before deploying to production:

1. **Lab environment** (Palo Alto test appliance)
   - Rule deployed and tested against test traffic
   - Expected behavior verified (traffic allowed, blocked, or logged per rule intent)
   - Unintended side effects checked (e.g., rule doesn't block legitimate traffic)

2. **Staging environment** (Secondary firewall replica)
   - Rule deployed to staging for 24–48 hours
   - Real traffic analyzed (NetFlow logs examined; no unexpected blocks)
   - Performance impact assessed (rule not causing latency or resource exhaustion)

3. **Rollback plan** documented
   - How will rule be reverted if issue discovered?
   - Who will execute rollback and by when?
   - Communication plan (notify stakeholders of rollback)

### 4.2 Deployment Checklist

Before pushing to production:
- [ ] Lab testing passed
- [ ] Staging testing passed (24+ hours no issues)
- [ ] Rollback plan written and tested
- [ ] Stakeholders notified of change window
- [ ] On-call engineer available during deployment
- [ ] CAB approval confirmed in change ticket

## 5. Deployment and Monitoring

### 5.1 Deployment Process

1. **Pre-deployment**: Network manager backs up current firewall config (dated backup file)
2. **Deployment**: New rule(s) deployed to primary firewall
3. **Verify**: Ping test and traffic flow confirmed; logs monitored for anomalies
4. **Replication**: Rule automatically replicates to secondary firewall (HA sync)
5. **Monitoring**: Netflow, firewall logs, and application metrics monitored for 4 hours post-deployment

### 5.2 Post-Deployment Monitoring (4 hours)

| Metric | Watch For | Alert Threshold |
|---|---|---|
| **Blocked traffic** | Legitimate traffic blocked by rule | >10 blocked flows; escalate to rule owner |
| **Firewall CPU** | High CPU from new rule processing | >70% CPU utilization |
| **Latency** | Network latency increase post-rule | >10ms increase vs. baseline |
| **Alerts** | IDS/IPS alerts from new rule interaction | Any critical alert; investigate immediately |

## 6. Rollback Procedures

### 6.1 Automatic Rollback

Rule automatically rolled back if:
- Firewall health check fails (rule crashes firewall process)
- Traffic drop >50% in 15 minutes (rule blocking too much)
- DDoS or abnormal traffic surge (rule ineffective against attack)

Rollback initiated automatically; network manager notified immediately.

### 6.2 Manual Rollback

Network manager executes manual rollback if:
- Operational team requests rollback within 24 hours of deployment
- Security incident requires immediate rule disabling
- Customer-reported issue traced to new rule

Rollback timeline: <5 minutes from decision to revert.

### 6.3 Post-Rollback Analysis

After rollback:
1. Root cause analysis conducted
2. Updated rule designed (adjust CIDR, port range, or logic)
3. Re-tested in lab (addressing root cause)
4. Redeployed in next month's change window

## 7. Rule Lifecycle and Cleanup

### 7.1 Temporary Rules

Rules with expiration dates auto-disabled on expiration:
- **Grace period**: Rule remains in firewall but disabled (not active) for 30 days
- **Cleanup**: After 30 days, rule deleted from configuration (unless renewal requested)
- **Renewal**: Rule owner may request extension before grace period expires

**Example**:
```
Temporary rule: Allow vendor IP 203.0.113.50 for onboarding (expires 2026-06-30)
→ 2026-06-30: Rule disabled (still in config)
→ 2026-07-30: Rule deleted (if no renewal)
→ If renewal needed: Owner submits request by 2026-06-15; new expiration date set
```

### 7.2 Quarterly Rule Audit

Every quarter, IT Infrastructure team:
- Reviews all active rules (>500 rules)
- Identifies rules no longer needed (associated project ended, vendor deprecated)
- Removes obsolete rules (e.g., rule for legacy server that was decommissioned)
- Reports: Removed X rules; consolidated Y overlapping rules
- Goal: Keep firewall rule base clean; <2% obsolete rules at any time

## 8. Documentation and Version Control

### 8.1 Firewall Configuration Backup

- **Daily automated backup**: Firewall config backed up to S3 with timestamp
- **Version control**: Each backup labeled with date, rule count, rule summary
- **Retention**: 1-year retention; older backups archived to Glacier

**Backup naming**: `pa-7060-prod-2026-04-13-v142.xml` (device-environment-date-version)

### 8.2 Rule Change Log

All rule changes logged in change management system:
```
Change ID: CHG-20026-00412
Rule name: GitHub Actions → Production Deploy
Action: Create
Effective date: 2026-04-13
Created by: jsmith@northwind.com
Approver: IT Infrastructure Review
CAB approval: 2026-04-10
Deployment date: 2026-04-14 (during change window)
Status: Active
Expiration: Permanent
```

Rules searchable by: rule name, source IP, destination IP, port, creation date, approval date.

## 9. Emergency Rule Requests

### 9.1 Fast-Track Approval

For active incidents (security breach, DDoS, critical service down):
- **VP Security** may approve rule without full CAB review
- **Justification**: Brief explanation of emergency
- **Approval timeline**: <30 minutes
- **Implementation**: Immediate (outside normal change window)

**Example emergency**:
```
Emergency rule: Block 192.0.2.0/24 (DDoS source)
Justification: 50 Gbps DDoS attack in progress; AWS Shield engaged; block source at FW
Approved by: VP Security (2026-04-13 14:32 UTC)
Deployed: 2026-04-13 14:35 UTC
Post-incident review: 2026-04-14 (CAB retroactively reviews; may approve/reject)
```

### 9.2 Post-Incident Review

Emergency rules reviewed within 24 hours by CAB:
- Does rule address root cause or just symptoms?
- Can rule be made more targeted (reduce collateral damage)?
- Should rule be permanent or temporary?

## 10. Compliance and Auditing

Firewall change management supports:
- **SOC 2 Type II**: Demonstrates change control and segregation of duties (approver ≠ implementer)
- **PCI DSS 1.1**: Firewall rule documentation and configuration standards
- **GDPR / CCPA**: Rule documentation supports data flow mapping

## 11. Related Policies

- **Network Security Architecture**: High-level firewall design and rule strategy
- **Incident Response Runbook**: Emergency rule deployment for active incidents
- **Information Security Policy**: Classification standards applied to firewall rules

---

**Document owner:** VP Infrastructure & IT Operations  
**Last approved:** 2026-04-13 by Infrastructure Steering Committee  
**Next review:** 2027-04-13
