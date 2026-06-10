---
title: Physical Security & Badge Access
doc_id: itsec-physical-security-badge-access
owner: Facilities & Security
last_updated: 2026-04-09
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Physical Security & Badge Access

## 1. Purpose and Scope

This policy establishes physical security controls for Northwind offices and data centers, including badge access, surveillance, and area restrictions.

## 2. Facilities Overview

### 2.1 Northwind Office Locations

| Location | Type | Access Level | Hours |
|---|---|---|---|
| **Austin, TX HQ** | Corporate office + on-site servers | Full access with badge | 24/7 (secure after hours) |
| **San Francisco, CA** | Engineering office | Badge access, restricted server room | 24/7 |
| **Remote** | Home offices | N/A | N/A |

### 2.2 Restricted Areas

- **Server room** (Austin HQ): Only IT staff with electronic badge access
- **Executive offices**: Badge access; visitor sign-in required for non-employees
- **Security operations center**: Only SOC and IT Security staff
- **Data destruction room**: Controlled access for secure document/device destruction

## 3. Badge Access System

### 3.1 Badge Issuance

All employees issued an RFID badge upon hire (Onboarding Day 1):
- Badge tied to employee ID number
- Card format: Photo ID embedded in RFID badge (physical + electronic identification)
- Card color indicates access level:
  - **Blue**: Standard employee (common areas, office)
  - **Green**: IT/Security staff (server room, SOC, network closet)
  - **Red**: Executive staff (all areas)
  - **Yellow**: Visitor (temporary, time-limited)

### 3.2 Physical Access Controls

| Area | Access | Badging | Video Surveillance |
|---|---|---|---|
| **Main entry** | All employees | RFID badge | Yes |
| **Office (common areas)** | All employees | Badge or greeting at desk | Yes |
| **Server room** | IT staff only (Green/Red badges) | RFID + PIN + biometric | Yes, continuous recording |
| **Executive floor** | Execs + approved visitors | Badge; visitor log | Yes |
| **Loading dock** | Facilities + delivery personnel | Badge; clipboard log | Yes, 24/7 |

### 3.3 After-Hours Access

- **5 PM–6 AM**: Building secured; badge-only access
- **Emergency access**: After-hours access requires VP approval and logged entry
- **Cleaning crew**: External cleaning company; badge readers track in/out times (no unescorted access to server room)
- **Cameras**: Video recording continuous; retention 90 days (searchable by date/time for incident investigation)

## 4. Visitor and Contractor Access

### 4.1 Visitor Badges

Visitors require:
1. Advance notice (email from employee to facilities@northwind.com)
2. Visitor agreement signed (acknowledgement of security policies)
3. Government-issued ID verified (name, address, ID number recorded)
4. Yellow temporary badge issued with expiration time (same day or next business day)
5. Visitor escorted to meeting location; badge only unlocks specified areas
6. Badge collected at visitor exit

### 4.2 Contractor Access

Long-term contractors (>1 week):
- Background check required (via third-party vendor)
- Contractor agreement signed (confidentiality clause, acceptable use policy)
- Green badge issued (similar to IT staff, but audit trail shows contractor status)
- Contractor manager responsible for escorting contractor to restricted areas
- Access removed immediately upon contract end

### 4.3 Third-Party Vendor Access (Data Center, SaaS)

Vendors accessing Northwind's AWS/Azure accounts or handling customer data:
- Security assessment required (see **SaaS Application Approval Process**)
- NDA and data processing agreement (DPA) signed by Legal
- MFA mandatory for all vendor access
- All vendor actions logged and audited
- Access revoked when vendor contract expires

## 5. Badge Lifecycle Management

### 5.1 Lost or Stolen Badge

If employee reports badge lost or stolen:
1. **Immediate**: Badge access disabled in system (within 5 minutes)
2. **Building notification**: Security notified; additional badge scan checks performed
3. **Replacement**: New badge issued within 1 business day
4. **Investigation**: If badge used for unauthorized access after reported lost, escalate as Sev-2 incident
5. **Cost**: First lost badge free; second loss charged to employee ($50 replacement fee)

### 5.2 Badge Deactivation Upon Termination

At employee termination:
1. Badge access disabled immediately upon HR notification
2. Departing employee badge collected before leaving building
3. Access logs reviewed (check for after-hours access in days prior to termination)
4. Badge physically destroyed or recycled

### 5.3 Badge Maintenance

- Badge readers tested monthly
- RFID enrollment updated quarterly (new employees added; terminated employees removed)
- Replacement cards issued every 3 years (wear/tear)

## 6. Area Access Policies

### 6.1 Server Room Access

| Activity | Who | Supervision | Logging |
|---|---|---|---|
| **Maintenance** | IT staff with Green badge | Unsupervised | Electronic access log + video |
| **Physical inspection** | VP Security or IT Director | Any IT staff present | Log + photos for documentation |
| **Audit/inspection** | External auditor (during SOC 2) | IT staff present | Audit trail; video retention extended |

### 6.2 Secure Destruction Area

- **Document shredding**: Facilities staff only (destroy all printed Confidential/Restricted documents)
- **Hard drive destruction**: IT staff only; physical shredding tool used; certificate of destruction obtained
- **Recording**: All destruction events video recorded and logged

## 7. Video Surveillance and Retention

### 7.1 Camera Placement

- **Entry/exit points**: Main doors, loading dock, parking lot
- **Hallways**: Common corridors to server room and executive areas
- **Server room entrance**: Continuous recording of all entries
- **Restricted areas**: Interior server room has continuous recording (tapes) for forensics

**Privacy notice**: Employees informed (signage at entry) that surveillance occurs in common areas. Personal workspaces not monitored.

### 7.2 Video Retention and Access

| Area | Retention | Access | Incident Search SLA |
|---|---|---|---|
| **Entry/exit** | 90 days | IT Security, VP Security | 1 hour |
| **Server room entrance** | 1 year | IT Security, CISO | 30 minutes |
| **Interior server room** | 2 years | IT Security, CISO | 30 minutes |

Incidents requiring investigation (unauthorized entry, breach attempt, theft) trigger immediate video search.

## 8. Environmental and Physical Controls

### 8.1 Server Room Climate Control

- **Temperature**: 64–80°F (strict control; alarms if out of range)
- **Humidity**: 40–60% RH
- **Power**: Redundant UPS systems; generator backup for extended outages
- **Fire suppression**: Gas-based suppression (not water) to protect equipment

### 8.2 Disaster Recovery / Business Continuity

- **Data backup**: Nightly backups to secondary site (RTO <4 hours per **Incident Response Runbook**)
- **Facility**: All-hands evacuation plan posted; emergency contacts listed
- **Insurance**: Property insurance covers equipment loss; business interruption insurance for outages

## 9. Environmental Compliance

- **Fire safety**: Fire exits unlocked and marked; annual fire drills (evacuate and account for all employees)
- **Accessibility**: ADA-compliant ramps, elevators, restrooms
- **OSHA compliance**: Ergonomic workstations; injury reporting (e.g., repetitive strain)

## 10. Incident Response for Physical Security Breaches

If unauthorized physical access detected:
1. **Immediate**: Notify VP Security and on-call engineer
2. **Investigation**: Review video footage (1-hour window before/after incident)
3. **Escalation**: If data center breached, escalate as Sev-1 incident (potential data compromise)
4. **Follow-up**: IT Security audit of system logs (logins, file access) during time of breach to assess data impact
5. **Communication**: If data breach confirmed, follow notification procedures per **Incident Response Runbook**

## 11. Related Policies

- **Information Security Policy**: General security standards
- **Incident Response Runbook**: Incident escalation procedures
- **Data Classification & Retention Policy**: Secure destruction of physical documents

---

**Document owner:** VP Facilities & Security  
**Last approved:** 2026-04-09 by Security Steering Committee  
**Next review:** 2027-04-09
