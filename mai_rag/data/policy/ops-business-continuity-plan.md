---
title: Business Continuity Plan (BCP)
doc_id: ops-business-continuity-plan
owner: Operations & IT
last_updated: 2026-06-09
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Business Continuity Plan (BCP)

## 1. Purpose & Scope

This Business Continuity Plan (BCP) ensures Northwind Technologies can sustain or rapidly resume critical operations following any disruption—whether caused by natural disaster, infrastructure failure, cyberattack, pandemic, or supply-chain incident. This plan applies to all employees, contractors, and facilities.

**Scope**: All critical business functions, data, systems, and personnel required to maintain service to customers and internal operations.

## 2. Critical Operations & Recovery Priorities

| Priority Tier | Function | RTO | RPO | Owner |
|---------------|----------|-----|-----|-------|
| **Tier 1** | Northwind Cloud platform availability; customer API access | 4 hours | 1 hour | VP Engineering |
| **Tier 1** | Customer data protection & confidentiality | 4 hours | 1 hour | VP Security |
| **Tier 2** | Billing & customer communication systems | 8 hours | 4 hours | VP Operations |
| **Tier 3** | Office operations, HQ & remote support | 24 hours | 8 hours | VP People & Facilities |

RTO (Recovery Time Objective) is the maximum tolerable downtime; RPO (Recovery Point Objective) is the acceptable data-loss window. Tier-1 functions (matching Sev-1 incident severity per the Incident Response Runbook) require immediate notification of executive leadership, the Board, and potentially customers.

## 3. BCP Governance & Roles

- **BCP Sponsor**: VP Operations; reports quarterly to Board
- **Crisis Management Team**: CEO, VP Security, VP Engineering, CFO, VP People, General Counsel (activated during any Tier-1 disruption)
- **Recovery Teams**: Functional leads for Tier-1 and Tier-2 operations
- **Comms Lead**: VP People or designee; coordinates internal and customer messaging per the Internal Communications Policy

## 4. Continuity Measures

### 4.1 Infrastructure Redundancy
- **Cloud**: AWS (primary) + Azure (secondary) for failover; automated health checks via Datadog
- **Data**: Encrypted backups daily; tested recovery path quarterly; 30-day retention minimum
- **Network**: Secondary ISP for HQ; remote-capable infrastructure for all critical teams
- **Facilities**: Austin HQ + distributed remote workforce; no single point of occupancy failure

### 4.2 Scenario-Specific Responses

**Natural Disaster (Hurricane, Earthquake)**:
1. Activate Crisis Management Team immediately (CEO declares DEFCON level)
2. Assess facility damage; shift to 100% remote work
3. Verify AWS and Azure infrastructure remain operational
4. Resume Tier-1 operations within 4 hours via cloud failover
5. See Emergency Response Plan for facility inspection & personnel safety protocols

**Cyberattack (Ransomware, Data Breach)**:
1. Activate Incident Response Runbook immediately (incident severity classification)
2. Isolate affected systems; preserve forensic evidence
3. Notify VP Security, General Counsel, and executive team; assess customer impact
4. Activate backup data restores only if approved by Incident Commander
5. See Information Security Policy and Crisis Management Plan for containment & disclosure

**Pandemic or Mass Illness**:
1. Shift to 100% remote work; activate continuity for on-site only roles (facilities, badge access)
2. Ensure IT support scaled for remote workload (VPN capacity, MFA availability)
3. Communicate via Internal Communications Policy; HR manages PTO/leave considerations per Leave & Time-Off Policy

### 4.3 Testing & Maintenance
- **Backup Testing**: Monthly restore verification; annual disaster-recovery drill
- **Communication Trees**: Updated semi-annually; tested during Q3 all-hands
- **Documentation**: Review and update this plan quarterly or after any activation

## 5. Recovery Procedures

### 5.1 Pre-Incident Preparation
- All Tier-1/Tier-2 leads maintain 48-hour contact lists (phone + email)
- Critical data extracts kept in encrypted cold storage (AWS S3 Glacier, tested quarterly)
- Runbooks for failover, restore, and service resumption posted in secure wiki

### 5.2 Activation Steps
1. **Detection**: Automated alert (Datadog) or manual report triggers incident classification
2. **Notification**: Incident Commander declares incident severity; Crisis Management Team convened if Sev-1
3. **Assessment**: Evaluate scope, affected systems, estimated recovery time
4. **Communication**: Internal (Slack update, all-hands if needed); External (customer notification per contract SLA)
5. **Recovery**: Activate documented runbook for affected tier; track timeline on war room dashboard
6. **Restoration**: Restore normal operations incrementally; validate each tier before handoff

### 5.3 Post-Incident
- Blameless post-mortem within 5 business days
- Update this plan if process gaps identified
- Report incident summary to Board (Tier-1) or executive team (Tier-2/3)

## 6. Communication During Disruption

All communications follow the Internal Communications Policy:
- **Internal**: Slack #incident-declared channel, then all-hands if >2-hour downtime expected
- **External**: Customer Success + PR coordinate message; General Counsel reviews for regulatory language
- **Frequency**: Updates every 30 minutes during active recovery

## 7. Annual Review & Certification

This plan is reviewed annually by VP Operations and signed off by the CEO. A full disaster-recovery drill (simulated Tier-1 incident) is conducted each October.

**Last Drill**: October 2025 (6-day recovery scenario); all Tier-1 targets met. Next: October 2026.

