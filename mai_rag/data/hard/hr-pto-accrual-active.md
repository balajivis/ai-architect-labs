---
title: Northwind PTO Accrual Schedule
doc_id: hr-pto-accrual-active
owner: People Operations
last_updated: 2026-03-05
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Northwind PTO Accrual Schedule

This document defines how paid time off (PTO) is earned, banked, and carried over for Northwind Technologies employees. It is maintained by People Operations and is the authoritative reference for accrual rates, monthly mechanics, carryover limits, and the interaction between PTO and parental leave. Managers, payroll, and the HRIS configuration team should treat the figures here as canonical when reconciling balances.

## Scope — all full-time employees

This schedule applies to all full-time employees of Northwind Technologies, regardless of department or geography, who are classified as regular salaried or regular hourly staff. Part-time employees, contractors, interns, and fixed-term agency workers accrue under separate arrangements documented in their offer letters and are out of scope here. "Full-time" means a standard 40-hour week or the local equivalent. Tenure, for all calculations in this document, is measured in completed years of continuous service from the employee's most recent hire date. Approved leaves of absence generally preserve continuous service for tenure purposes, with the parental-leave exception described below.

## Accrual Bands by Tenure

PTO is granted on a tiered schedule that increases with tenure. The annual entitlement is determined by which tenure band an employee falls into at the start of each accrual month:

- **0–2 years of tenure:** 15 days per year
- **3–5 years of tenure:** 20 days per year
- **6–9 years of tenure:** 25 days per year
- **10+ years of tenure:** 28 days per year

Band boundaries are inclusive and resolve by completed years. An employee with exactly 5 completed years of service remains in the 3–5 band and accrues at **20 days per year**; they do not move to the higher rate until they complete their 6th year, at which point they jump to **25 days per year**. The boundary between bands is therefore a step, not a gradual increase — there is no interpolation between 20 and 25 days. Likewise, an employee with 2 completed years is still in the 0–2 band at 15 days; the increase to 20 days takes effect once the 3rd year of service begins. People Operations recalculates an employee's band on the first of the month following each service anniversary, so a mid-month anniversary does not change the rate until the next monthly accrual run.

## Monthly Accrual Mechanics

PTO accrues monthly and is pro-rated. Northwind does not front-load the full annual entitlement on January 1; instead, employees earn a twelfth of their annual band each month. For example, an employee in the 3–5 year band (20 days/year) earns approximately 1.667 days per month, while an employee in the 6–9 year band (25 days/year) earns approximately 2.083 days per month. Accrual posts on the last calendar day of each month based on the band in effect for that month.

New hires and mid-month starters accrue a pro-rated fraction of their first month based on the number of calendar days worked. Employees who change bands mid-year accrue at the old rate for months completed in the old band and at the new rate thereafter — balances are not retroactively recalculated. Unpaid leave days do not accrue PTO; see the parental-leave interaction below for the specific handling of unpaid extensions.

## Carryover Limit (5 days)

PTO does not roll over without limit. At the close of each calendar year, employees may carry a **maximum of 5 days** of unused PTO into the next year. Any balance above 5 days as of December 31 is forfeited and does not convert to cash, except where local statute requires payout, in which case payroll applies the statutory rule. Carried-over days are consumed first in the new year, before newly accrued days, so that the oldest balance is always used before it can expire. People Operations sends balance reminders in October and November so employees can schedule time before the cap takes effect. The 5-day cap is a hard limit and is not extended for unused parental leave, sabbaticals, or pending PTO requests that were submitted but not yet approved.

## Interaction with Parental Leave (see hr-parental-leave-active)

Parental leave and PTO are tracked as separate entitlements. Time spent on approved parental leave does **not** count against an employee's PTO accrual — that is, an employee does not "spend" PTO days while on parental leave, and PTO continues to accrue at their normal band rate for the duration of the standard, paid parental-leave entitlement. The one exception is **unpaid extensions**: if an employee extends parental leave beyond the standard entitlement into an unpaid period, PTO accrual is **paused** for the unpaid portion and resumes when the employee returns to active, paid status.

To compute the full picture for a specific employee, you must combine this schedule with the parental-leave policy. The two required numbers live in two different documents: the **annual PTO band rate is determined here**, and the **length of the standard paid leave entitlement is defined only in `hr-parental-leave-active`**. For example, an employee with **4 years of tenure** taking parental leave accrues PTO at the **20 days/year** band specified in this document (the 3–5 year band); the number of weeks that paid leave lasts is not stated anywhere in this document and must be read from `hr-parental-leave-active`. Conversely, the parental-leave policy does not restate the 20-day accrual rate. Neither figure can be derived from a single document, so a complete answer to "how does PTO accrue for this employee while on parental leave, and for how long?" always requires cross-referencing both.

## Requesting and Tracking PTO

PTO is requested through the Northwind HRIS self-service portal. Employees submit a request, their manager approves or declines, and approved time is deducted from the available balance at the start of the absence. The portal displays current accrued balance, pending requests, projected year-end balance, and the carryover that will be retained or forfeited under the 5-day cap. Employees are encouraged to review their projected year-end figure each quarter. Discrepancies between the portal balance and an employee's own records should be raised with People Operations within 30 days of the close of the affected month, after which posted accruals are considered final.
