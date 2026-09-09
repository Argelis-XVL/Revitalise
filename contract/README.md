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

**There will be no v0.6.** The reviewer closed that route on 2026-08-19 — *"WBS 0.6 is not going to
come. The 20 hours for DocuSign selection have been invoiced already."* It is recorded in
`scripts/import-baseline.py` (`WBS_IS_FINAL = True`, `KNOWN_GAP.resolution`) and in
`contract/known-exceptions.json` (`EX-001.superseded_note`, `EX-002.superseded_note`). **Do not park
a correction as "pending v0.6" — nothing will ever pick it up.** This paragraph previously listed two
corrections as outstanding for v0.6 and was stale from 2026-08-19 to 2026-09-09, during which it
invited exactly that mistake.

Anything a re-approval would have carried is carried permanently instead, by shape:

| The correction is… | It goes in |
|---|---|
| a gate that is firing and is knowingly accepted | `contract/known-exceptions.json` — owned, dated, re-reported every run (`C-COM-010`) |
| hours or scope the breakdown omits | `scripts/import-baseline.py` `KNOWN_GAP`, surfaced as `corrected_totals_with_known_gap` |
| build order the `Depends On` column does not carry | `contract/delivery-parameters.json` → `build_order_constraints` — non-contractual, no hours move |
| a task claimed complete on evidence that is not the deliverable | `contract/evidence-map.json`, tightened per its own `_rule_quality_note` |

The two former v0.6 items, as they actually stand:
- the 20-hour DocuSign selection-and-trial task the breakdown omits (`IMP-0064`) — **closed**;
  performed and invoiced, carried as `KNOWN_GAP`. v0.5 understates delivered scope by 20 hours
  permanently
- task `0.4`'s status, which reads `Done` with five of its eight named tables absent
  (`IMP-0030`, exception `EX-001`, expires 2026-11-27) — **open, and clearable only by building the
  five tables**, not by restating the document

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
