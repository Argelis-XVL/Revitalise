# contract/ — the commercial spine

Everything here is **generated or gated**. Nothing in this directory is hand-typed prose about money.

| Path | What | Written by |
|---|---|---|
| `wbs.json` | the 61 accepted tasks: hours, dependencies, deliverables, phases | `scripts/import-baseline.py` |
| `service-agreement.json` | phase hours and milestone dates, read from the signed PDF | `scripts/import-baseline.py` |
| `source-lock.json` | sha256 of every contractual source, so a silent edit is detected | `scripts/import-baseline.py` |
| `evidence-map.json` | WBS task → the repository evidence that proves its deliverable | hand-authored, gated by its own quality rule |
| `external-dependencies.json` | each precondition's state, owner and age | hand-authored from cited evidence |
| `delivery-parameters.json` | capacity and the estimating rule (not contractual) | hand-authored from D-6 |
| `declared-complete.json` | tasks no repository evidence can ever prove, declared by a human | `acceptance-agent` / reviewer |
| `known-exceptions.json` | accepted gate violations, each owned and dated | reviewer |
| `acceptance/PA-*.md` | phase acceptance records — part of the Agreed Specification (B1) | `acceptance-agent`, behind `CLIENT ACCEPTED` |
| `invoices/INV-*.md` | monthly invoices, immutable once issued | `commercial-agent`, behind `ISSUE INVOICE` |
| `change-orders/CO-*.md` | scope the accepted baseline does not cover | `commercial-agent`, behind `APPROVE CHANGE ORDER` |
| `handover/` | handover packs | `acceptance-agent`, behind `APPROVE HANDOVER` |

## The two rules that govern this directory

**1. Hours only.** D-3, the reviewer's decision: *"Hours for the baseline is perfect."* No fee figure,
hourly rate, currency amount or bank detail appears in any tracked file in this repository. The rate
lives outside it; the money is applied outside it. `scripts/verify-worklog.py` and
`scripts/report-baseline-drift.py` both scan for violations, and `C-COM-004` makes it HARD.

Why it matters here specifically: this repository lives in a SharePoint library named after the
client, and a rate in git history cannot be withdrawn.

**2. A source is never edited.** `docs/Import/` holds the contractual sources. WBS v0.5 is
customer-accepted (D-5), so correcting it means issuing v0.6 and having it re-approved behind
`APPROVE BASELINE` — not editing a cell (`C-COM-009`).

Two corrections are outstanding for v0.6:
- the 20-hour DocuSign selection-and-trial task the breakdown omits (`IMP-0064`)
- task `0.4`'s status, which reads `Done` with five of its eight named tables absent
  (`IMP-0030`, exception `EX-001`, expires 2026-09-30)

## What is deliberately NOT here

- **the hourly rate** — `contract/rate.local.yml`, gitignored, and it does not exist yet
- **the incorporated terms' clause text** — D-4. Only their URL and version are recorded, in
  `docs/Import/incorporated-terms.md`. `scripts/warranty-clock.py` **refuses to compute** a warranty
  window until the text is present, because a window computed from the agreement's paraphrase would
  be indistinguishable from one computed from the clause
- **the reviewer's answers to D-1…D-8** — those live in `docs/Import/baseline-lock.yml`, where the
  previous session recorded them. Read that before asking a question it already answers

## Regenerating

```bash
python3 scripts/import-baseline.py            # regenerate from the sources
python3 scripts/import-baseline.py --check    # CI: fail if stale
python3 scripts/derive-wbs-state.py           # task state from evidence
python3 scripts/report-baseline-drift.py      # what disagrees with what
bash scripts/ci/verify-pm-gates.sh            # every gate + proof it can fail
```
