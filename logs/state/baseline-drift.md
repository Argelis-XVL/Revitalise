# Baseline drift

**GENERATED — do not hand-edit.** `python3 scripts/report-baseline-drift.py`

Build Terms B1 makes the Solution Design, the Solution Architecture, the WBS and the phase acceptance record jointly the Agreed Specification, and the most recently accepted version prevails. A disagreement between them is an open question about scope.

## 1. Total reconciliation

| | Hours |
|---|---|
| Agreement (read from the signed PDF, verified two ways) | **292** |
| WBS v0.5 as accepted | 177–277 |
| WBS corrected for the known gap | 197–297 |
| Verdict | **RECONCILED — the agreement total falls inside the corrected WBS band** |

The agreement groups WBS work many-to-one by design (D-1/D-2), so a per-phase comparison is meaningless and is deliberately not made here.

## 2. The known WBS gap

- **20 h — Selecting and trialling the DocuSign platform** (automation #3, phase_1, `IMP-0064`)
- Action: Issue WBS v0.6 carrying this task; do not edit v0.5.
- WBS v0.6 present in `docs/Import/`: **NO — still outstanding**

## 3. Hour figures restated in documents

A document that restates a baseline figure goes stale silently and is inherited downstream (`IMP-0029`). These disagree with the baseline:

| Where | Says |
|---|---|
| `docs/plans/revitalise-grant-automation-plan.md:873` | 106–160 hours |
| `docs/plans/revitalise-grant-automation-plan.md:905` | 133–208 hours |
| `docs/plans/revitalise-grant-automation-plan.md:930` | 106–160 hours |

## 4. D-3 compliance — fee and rate figures

Clean. No fee or rate figure appears in the checked paths.

## 5. Claimed status against evidence

- **1 overclaim(s)** — a task marked complete whose deliverable is partly or wholly absent
- **5 underclaim(s)** — a deliverable that exists against a blank status
- 0 task(s) with no evidence rule

  - **OVERCLAIM `0.4`** Dataverse solution & table schema build — missing: entity rev_review: ABSENT; entity rev_provider: ABSENT; entity rev_bankaccount: ABSENT; entity rev_payment: ABSENT; entity rev_anonymisedstatistic: ABSENT
  - UNDERCLAIM `1.2` Write form specification
  - UNDERCLAIM `1.6` Document save-and-continue workflow
  - UNDERCLAIM `2.8` Test with real data + sign-off
  - UNDERCLAIM `6.5` Share app to trustee role + access test
  - UNDERCLAIM `8.2` Build finance security role

## 6. Computations blocked by missing inputs

- **Warranty / hypercare / liability caps: UNAVAILABLE** — D-4: the Build & Implementation Terms clause text is not in this repository, only its URL and version. No gate may compute a warranty window, an exclusion or a liability cap until the text is present.

