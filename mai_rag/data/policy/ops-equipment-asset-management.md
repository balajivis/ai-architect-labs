---
title: Equipment & Asset Management Policy
doc_id: ops-equipment-asset-management
owner: IT & Facilities
last_updated: 2026-06-09
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Equipment & Asset Management Policy

## 1. Purpose & Scope

This policy governs procurement, allocation, maintenance, and retirement of company-owned equipment and assets, including:
- **Computing**: Laptops, desktops, monitors, keyboards, docking stations, mobile devices
- **Network & Security**: Routers, switches, firewalls, VPN appliances, security cameras
- **Office Equipment**: Printers, copiers, phone systems, video conferencing hardware
- **Furniture & Facilities**: Desks, chairs, whiteboards, emergency equipment
- **Software Licenses**: Operating systems, productivity tools, cloud services (tracked separately in vendor procurement)

**Scope**: All employees, contractors, and IT/Facilities teams responsible for equipment lifecycle.

**Objective**: Maximize asset lifespan, minimize waste, maintain security posture, ensure audit compliance, and optimize capital spending.

## 2. Asset Lifecycle: Procurement to Retirement

### 2.1 Procurement
| Stage | Owner | Process |
|-------|-------|---------|
| **Needs Assessment** | Functional manager | Justification document (business need, cost, expected ROI) submitted to CFO |
| **Vendor Selection** | IT / Procurement | RFP or catalog evaluation; check SLA, warranty, security requirements |
| **Approval** | CFO (>$5K) / Manager (≤$5K) | Approval recorded in asset register before purchase |
| **Purchase Order** | Procurement | PO issued; delivery tracked; receipt verified against packing slip |
| **Tagging & Inventory** | IT (computers) / Facilities (other) | Asset tag affixed; serial number logged; assigned to user; baseline documented |

### 2.2 Allocation & Ownership
- **Employee devices** (laptop, phone): Assigned to individual employee; signed assignment form; employee responsible for physical security and data protection
- **Shared equipment** (printers, video conferencing): Assigned to department; primary contact designated
- **Portable devices** (USB drives, external hard drives): Tracked per Acceptable Use Policy; encryption mandatory if containing Confidential or Restricted data
- **Contractor equipment**: Temporary assignment; returned on contract end date; data wiped by IT

### 2.3 Maintenance & Support
- **Warranty**: All equipment covered by manufacturer or vendor warranty during standard support period (typically 1–3 years)
- **IT Support**: Helpdesk triages issues; hardware problems escalated to vendor if under warranty
- **Preventive maintenance**: Servers and network equipment receive quarterly review; desktop/laptop updates managed via Mobile Device Management (MDM) tools
- **Repair vs. Replace**: IT determines after failure; if repair cost >60% of replacement cost or replacement faster than repair, replace

### 2.4 Decommissioning & Data Wiping

**Critical**: All equipment containing company or customer data must be securely wiped before disposal.

| Equipment Type | Data Wipe Method | Certification | Owner |
|---|---|---|---|
| **Hard drive (HDD)** | DoD 5220.22-M standard (3-pass overwrite); or destruction (shredding) | Certificate of destruction issued | IT Security |
| **Solid-state drive (SSD)** | Secure erase command (NIST SP 800-88 compliant); or physical destruction | Certificate logged in asset registry | IT Security |
| **Mobile device** | Factory reset (Apple, Samsung native tools); verify via audit log | Screenshot of "device reset complete" | IT Security |
| **Printer / scanner** | Internal hard drive removed & wiped per HDD protocol; or device physically destroyed | Certificate of destruction | IT + Facilities |

**Process**:
1. Employee notifies IT of equipment end-of-life
2. IT collects device; backs up user data if needed
3. IT Security wipes per protocol; documents completion
4. Facilities disposes of e-waste via certified e-waste recycler (R2 or e-Stewards certified)
5. Asset registry updated: status = "Retired"; date and method logged

### 2.5 Physical Lifecycle Tracking
- **Check-out**: Employee signs form; device SN, assignment date, expected return date recorded
- **Check-in**: IT physically receives device; verifies condition; logs return date
- **Audit**: Monthly reconciliation of asset register vs. active employee roster; missing items escalated to VP Operations

## 3. Device Management & Security

### 3.1 Mobile Device Management (MDM)
All company-owned mobile devices (laptops, phones, tablets) enrolled in MDM (Intune or MDM service provider):
- **Mandatory enrollment**: Day 1 of employment; part of onboarding (cannot use device for work until enrolled)
- **Remote management**: IT can enforce password policies, wipe device remotely if lost/stolen, push security updates
- **Encryption**: Mandatory; verified by MDM system
- **Compliance monitoring**: Non-compliant devices flagged; user receives notification; 7-day cure period before access suspension

### 3.2 User Responsibility for Assigned Equipment
- **Physical security**: Keep device secure when not in use; report theft/loss immediately to IT + Security
- **Password/PIN**: Set strong password (per Identity & Access Management Policy); do not share with others
- **Updates & patches**: Allow automatic updates; do not disable security features or firewalls
- **Acceptable use**: See Acceptable Use Policy; personal use limited; no pirated software or media
- **Travel security**: If traveling with Confidential data, device must be encrypted; access only via VPN from hotel/external networks (per Remote Access/VPN Guide)

### 3.3 Personal Device Usage (BYOD)
- **Allowance**: Limited; only if pre-approved by manager and IT
- **Enrollment**: Personal device must be enrolled in MDM and meet baseline security (encryption, password, antivirus)
- **Access**: May access internal portals, email, and shared drives only via VPN
- **Liability**: Company not responsible for loss, theft, or personal data loss on BYOD devices
- **Winding down**: At termination, personal device un-enrolled; company data removed

## 4. Asset Registers & Audit

### 4.1 Asset Register (Master Inventory)
Centralized registry maintained by IT and Facilities:
- **Fields**: Asset tag, serial number, asset type, manufacturer, purchase date, cost, assigned user, location, status (active/retired), notes
- **System**: Maintained in Asset Manager (Excel macro or cloud tool); backed up daily
- **Access**: IT and Finance only; read-only access for managers to their department's assets

### 4.2 Audit & Reconciliation
- **Monthly**: IT Ops reconciles asset register against MDM enrollment and physical spot-checks
- **Quarterly**: Finance performs financial reconciliation; verifies depreciation calculations
- **Annual**: Full physical audit; IT, Facilities, and Finance walk facilities and verify every asset; discrepancies investigated
- **Board reporting**: CFO reports on total fixed assets, depreciation, and any theft/loss incidents

### 4.3 Missing Equipment Protocol
If physical count does not match register:
1. IT conducts secondary search (storage, archive areas); user interviewed
2. If not found within 48 hours, classified as lost or stolen
3. VP People notified (potential misconduct); incident logged
4. Finance writes off asset (depreciation adjustment); asset registry marked "lost" or "stolen"
5. If stolen, police report filed (General Counsel decision); employee disciplinary action considered

## 5. Software Licensing & Compliance

### 5.1 Approved Software List
IT maintains approved software list (GitHub wiki or shared drive):
- **Approved**: Northwind-licensed tools (Office 365, Adobe Suite, Slack, GitHub, etc.); can be installed freely
- **Requires approval**: Specialized tools, developer libraries, or anything with licensing costs; request via IT ticket
- **Prohibited**: Pirated software, license-sharing outside organization, personal entertainment software

### 5.2 License Tracking
- **Inventory**: Finance tracks all paid software subscriptions; owner, cost, renewal date, and seats/users in Asset Manager
- **Usage**: IT monitors usage monthly; unused licenses reallocated or cancelled
- **Renewals**: Finance owner reminds team 60 days before renewal; VP Operations approves
- **Compliance**: Annually, legal holds IT responsible for verifying no unlicensed software in use

## 6. Depreciation & Financial Treatment

- **Capitalization threshold**: Equipment >$2,500 capitalized; <$2,500 expensed
- **Depreciation schedule**:
  - **Computers (3-year)**: Laptop/desktop, monitors
  - **Network equipment (5-year)**: Routers, switches, firewalls
  - **Furniture (7-year)**: Desks, chairs, cabinets
- **Residual value**: Assumed 10% for computers; depreciated to $0 in most cases
- **Annual write-off**: Finance performs depreciation audit each Dec; adjustments recorded in books

## 7. Equipment Replacement Cycle

- **Standard**: Computers replaced every 4 years; phones every 3 years; monitors every 5 years
- **Accelerated**: If device fails and repair cost >60% of replacement; IT may approve early replacement
- **Budget cycle**: Equipment replacements planned annually per department's headcount growth; CFO approves allocation

## 8. Accountability & Consequences

| Violation | Example | Consequence |
|-----------|---------|-------------|
| **Unauthorized transfer** | Giving your laptop to colleague without IT approval | Verbal warning; IT locks device remotely |
| **Failure to report loss** | Laptop stolen; not reported for 1 week | Formal warning; employee may be liable for replacement cost |
| **Unlicensed software** | Installing pirated software; disabling antivirus | Disciplinary review (Code of Conduct violation); possible termination |
| **Negligent damage** | Liquid spill destroying device due to recklessness | Repair/replacement cost charged to employee's department or personal liability |

