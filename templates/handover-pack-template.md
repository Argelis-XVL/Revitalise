# Handover Pack — <Phase N | Final>

> **Handover is a commercial boundary, not a courtesy.** The Service Agreement §02 excludes
> *"ongoing operation, monitoring, support or maintenance after handover"* unless agreed separately
> in writing. This document is what fixes where that line falls, so anything missing from it becomes
> an argument later.
>
> **Verified by:** `python3 scripts/verify-handover-pack.py contract/handover/<file>.md`

- Phase: <Phase N | Final>
- Handover date: <YYYY-MM-DD>
- Accepted by: <Client contact>
- Operational runbooks (B10): `docs/Import/Revitalise-Governance-Runbook-v0.1.docx`,
  `docs/Import/Revitalise-ALM-Runbook-v0.1.docx`

## 1. What was built, and where it lives

| WBS | Deliverable | Where | Level reached |
|---|---|---|---|

## 2. Ownership after handover

| Component | Owner | Contact |
|---|---|---|

## 3. Licences and renewals

Licences are the Client's cost under §02. Anything that lapses here stops the solution.

| Product | Seats / plan | Cost owner | Renewal date |
|---|---|---|---|

## 4. Monitoring and alerting

| What | Where | Who receives it |
|---|---|---|
| Error Log table | `rev_errorlog` | |
| Failure Alert flow | `REVOpsFailureAlert` | |
| AI Builder credit alert | | |
| Licence renewal alert | | |

## 5. Credentials, certificates and app registrations

**Every entry needs a holder.** A dependency held only in an individual's personal keystore is a
HARD handover blocker (PM-R22): the Client cannot operate it, and the day it is needed is the day
someone is unreachable.

| What | Identifier | Held by | Transfer action | Done |
|---|---|---|---|---|

`logs/known-failure-modes.md` → *Capabilities established in earlier sessions* records credentials
this project depends on. `verify-handover-pack.py` reads those lines and fails if one is not
accounted for here.

## 6. Escalation

| Situation | First contact | Then |
|---|---|---|

## 7. Open items at handover

| Item | Owner | Warranty cover ends |
|---|---|---|

## 8. What is NOT included after handover

Quoted from the Service Agreement §02, so the boundary is on the record the Client signs:

- Procurement and ongoing cost of third-party licences and services (DocuSign, Power Automate
  Premium, AI Builder credits, Power BI Pro, Microsoft 365).
- Build and configuration of the WordPress application form itself — carried out by the Client's
  website designer; the Consultant provides the specification and testing only.
- Day-to-day administration and processing of individual grant applications.
- **Ongoing operation, monitoring, support or maintenance after handover, unless agreed separately
  in writing.**
