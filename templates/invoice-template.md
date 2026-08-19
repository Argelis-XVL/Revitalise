# Invoice — hours worked, <YYYY-MM>

> **Hours only.** No fee figure or hourly rate appears in this repository (D-3). The money is
> applied outside it. Every figure below comes from `python3 scripts/compute-invoice.py --month
> <YYYY-MM>` and is re-verified by `scripts/verify-worklog.py` before issue.
>
> Invoiced monthly in arrears for hours worked in the preceding calendar month; payment due within
> 14 days of invoice date (Service Agreement §03).

- Invoice reference: INV-<YYYY-MM>
- Period: <YYYY-MM-01> to <YYYY-MM-31>
- Issued: <YYYY-MM-DD>
- Status: DRAFT | ISSUED
- Total hours: <n>

An issued invoice is **immutable**. A correction is a new invoice that references this one
(C-COM-003).

## 1. Hours by WBS task

| WBS | Task | Phase | Hours |
|---|---|---|---|

## 2. Hours by work type

| Work type | Hours |
|---|---|

## 3. Not charged

Work done and deliberately not billed, shown so the decision is on the record.

| What | Hours | Why not charged |
|---|---|---|

## 4. Progress against the contracted baseline

| | Hours |
|---|---|
| Contracted, whole engagement | <from contract/service-agreement.json> |
| Invoiced to date, including this invoice | <n> |
| Remaining contracted | <n> |

**No per-phase variance is stated for a phase still open.** An invoiced figure below estimate on an
unfinished phase says nothing about efficiency (IMP-0065).

## 5. Evidence

Each session behind these hours carries at least one reference that resolves to a log line, a commit
or a file in the repository, plus a recorded human confirmation (C-COM-001). Session ids:
<WL-nnnn, …>
