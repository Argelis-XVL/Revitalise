# Improvement Review — 2026-08-20

**Gate:** `APPROVE IMPROVEMENTS` given by the reviewer, alongside a `HOLD` on the August timesheet.
**Findings processed:** 11 `NEW` → 6 clusters. 8 applied, 3 deferred with a named owner.
**WBS:** `system` — this review changes the development system, not the product. Out of contractual
scope, non-billable (`C-COM-002`).

## Summary

One blocker drove this review: **two gates read the same ledger and disagreed by twenty hours**,
and both exited 0, so CI was green while the repository stated invoiced-to-date as both 64 and 84.
The cause was a rule implemented three times and omitted once.

The durable fix is that the rule now exists once, in `scripts/lib/worklog.py`, and a CI check fails
if any reader disagrees with the others. Two site-map shapes that shipped and did not render are now
mechanically rejected. Three findings are deferred, one of them for the fourth time — that is said
out loud in **What is not fixed**, with the inventory that makes it executable.

## Clusters and decisions

```
CLUSTER: two-invocation-paths-disagree  (x1 NEW: IMP-0093 — class now x5)   ** BLOCKER **
Altitude:  CLASS. The property is not "verify-wbs-chain has a bug", it is "a rule about what the
           ledger MEANS was implemented once per reader". Three readers, two implementations,
           one omission.
Ladder row: "a tool could catch it mechanically" + "second instance -> generalise"
Becomes:   scripts/lib/worklog.py (new — the single definition) + verify-wbs-chain.py,
           verify-worklog.py and compute-invoice.py all call it +
           scripts/ci/verify-pm-gates.sh section 7 (readers must agree) +
           src/tests/fixtures/known-bad/worklog-clean/superseded-seed.jsonl
Retires:   the two independent `corrected = {...}` derivations in verify-worklog.py and
           compute-invoice.py. Deleted, not left alongside.
Cites:     IMP-0093
Residual:  The check compares readers to each other, so three readers agreeing on a WRONG rule
           still passes. The fixture is what pins the rule itself: a corrected 10-hour seed must
           read 0 h, and reads 10 h with the correction line removed.

CLUSTER: platform-contract-guessed-not-groundtruthed  (x2 NEW: IMP-0087, IMP-0091 — class now x11)
Altitude:  CLASS, and escalated. The prior home for this class was PROSE —
           skills/how-to-verify-a-platform-contract.md. Two more instances arrived anyway, which
           the regression check treats as evidence the fix was at the wrong altitude.
Ladder row: "recurrence after a prose change -> escalate to a gate"
Becomes:   scripts/verify-shipped-content.py check 1c — an entitylist SubArea Url must begin with
           '/' and contain '?'; a SubArea may not carry both Entity= and an entitylist Url; every
           pinned viewid must resolve to a savedqueryid of the entity it names.
           Fixture: src/tests/fixtures/known-bad/shipped-content-subarea/ (3 errors, exit 1).
Retires:   nothing. Nothing validated a SubArea Url before; the old check read etn= out of any
           string and passed on all three broken shapes.
Cites:     IMP-0087, IMP-0091
Residual:  The gate proves a viewid EXISTS in source. It cannot prove the platform opens it —
           that is V4, and it is what IMP-0088 records. Three viewid encodings are live in the
           production site map; all resolve, so the gate reports the split rather than failing.

CLUSTER: gate-reassures-wrongly  (x1 NEW: IMP-0094 — class now x2)
Altitude:  CLASS — second instance, so no instance patch.
Ladder row: "a tool could catch it mechanically"
Becomes:   scripts/reconstruct-worklog.py — per-EVENT classification, three states
           (yes / NO / MIXED) with a proportional split hint, plus a re-bill warning when a
           session's tasks fall inside WL-0001's already-invoiced phases.
Retires:   the single cluster-wide regex verdict.
Cites:     IMP-0094
Residual:  More windows now read MIXED, including two that used to read a confident NO. That is
           the point — the script refuses to decide where it cannot — but it moves work to the
           human rather than removing it. The split hint weighs an agent's ten log lines the same
           as two hours of thinking, and says so on the line where it prints.

CLUSTER: output-shape-defeats-the-reader  (x1 NEW: IMP-0095 — class now x3)
Altitude:  CLASS — third instance. The finding proposed fixing one agent's template; that would
           have been the instance patch the altitude rule forbids.
Ladder row: "an agent had the information and still did the wrong thing"
Becomes:   skills/how-to-report-to-the-reviewer.md rule 8 — the headline number in a gate block is
           the number being approved, shown as a ladder that reconciles; no word names two
           different quantities. agents/commercial-agent.md's template rebuilt around it.
Retires:   nothing.
Cites:     IMP-0095
Residual:  Nothing mechanically checks that a gate block's figures add up. This is prose in a
           skill, which is the altitude that has already failed twice for this class.

CLUSTER: agent-instructions-describe-a-topology-that-changed  (x1 NEW: IMP-0092 — class now x2)
Altitude:  CLASS — second instance.
Ladder row: "the system's own memory failed" -> a read-path change
Becomes:   agents/commercial-agent.md + skills/how-to-account-for-billable-time.md corrected;
           'UNAVAILABLE (D-4)' removed from the gate template; scripts/warranty-clock.py's
           docstring no longer opens with "WHY IT CURRENTLY REFUSES TO ANSWER" while answering.
Retires:   nothing.
Cites:     IMP-0092
Residual:  No gate compares an agent's stated capability against the tool that provides it, so
           the next lifted blocker can go stale the same way. Named as a candidate below.

CLUSTER: no change required  (IMP-0086, IMP-0088)
Altitude:  DIGEST. One is a capability (a setting solution source omits is untouched by import,
           so a table audit switch is set once per environment and survives every release); the
           other is C-TECH-053's V4 requirement working exactly as written.
Becomes:   the regenerated digest, which is the read path.
Cites:     IMP-0086, IMP-0088
Residual:  none.
```

## Regression check — did the 2026-08-19 reviews work?

| Prior change | Class | Recurred? | Verdict |
|---|---|---|---|
| `C-TECH-064` + `verify-pipeline-config.py` check 10 | `exit-zero-does-not-mean-created` | No new instances | Held. |
| `agents/pipeline-agent.md` Reviewer-Executed Operations | `harness-blocks-destructive-call` | No new instances | Held. |
| `knowledge/technology/testing-tools.md` live verification | `live-verification-capability` | No new instances | Held. |
| `skills/how-to-verify-a-platform-contract.md` (prose) | `platform-contract-guessed-not-groundtruthed` | **Twice** | **Wrong altitude.** Escalated to a gate this review. |
| `skills/how-to-report-to-the-reviewer.md` (prose) | `output-shape-defeats-the-reader` | **Once** | Prose again, knowingly — see that cluster's residual. |

`C-TECH-064` deserves its own line. It did not recur, but it also **has never run**: it is declared
in the pipeline config as `script: manual` with a `blocked_on`, exactly as the prior review recorded.
`IMP-0085` is the consequence that review predicted. A constraint with no executable implementation
is not a gate that held; it is a gate that has not been tested.

## New constraints

**None.** The cap is three and this review used zero. Every cluster found a more mechanical home —
four scripts, one library, one CI check, two fixtures and two skill/agent edits. `C-COM-003` and
`C-TECH-064` already say what needed saying; what they lacked was execution.

## Retirement

Two implementations retired rather than deprecated: the independent `corrected = {...}` derivations
in `verify-worklog.py` and `compute-invoice.py`, replaced by `scripts/lib/worklog.py`. No constraint
row was retired. One candidate for the next review: nothing yet compares an agent's stated tool
capability against the tool, which is what `IMP-0092` needed and what would make a prose correction
unnecessary next time.

## What is not fixed

**The count-coupled assertions — deferred a fourth time, to development-agent.** `IMP-0005` and
`IMP-0039` describe 14 assertions broken by correct schema additions. The fix is a `src/tests/`
refactor, which is not this agent's to make. What was missing from the previous three deferrals is
the discrimination rule and the inventory, so here they are.

The rule: **a count that tracks a total derived from source is fragile; a count that asserts a
fixture's own cardinality is not.** `$securedColumns.Count | Should -Be 51` breaks whenever a
column is secured. `@(Get-FakeDataverseCalls -Method POST).Count | Should -Be 0` is a behavioural
assertion and must be left alone.

There are **45** sites matching `.Count | Should -Be <n>` with n ≥ 2. Roughly 13 track a
source-derived total and are the actual defect:

| File | Lines | Asserts |
|---|---|---|
| `src/tests/provisioning/EnsureSchema.Tests.ps1` | 196, 572 | 21 global option sets |
| | 200 | 9 options on one set |
| | 305, 306, 602, 674 | 51 secured / profiled / permission / patched columns |
| | 498, 500 | 43 and 36 role privileges |
| | 585 | 3 relationship calls |
| | 594 | 79 AddPrivilegesRole calls (38 + 31, already annotated with its own history) |
| `src/tests/solutions/ScoringInvariants.Tests.ps1` | 549 | 51 secured columns |
| | 49 | 11 inversion keys |
| `src/tests/solutions/IntakeContract.Tests.ps1` | 234, 316 | 82 trigger schema properties |

The other ~32 are fixture cardinalities. **A blanket gate over all 45 would be wrong about most of
them**, which is why this is judgement work by whoever owns those tests and not a regex this review
could have written.

**The `C-TECH-064` live verifier — deferred with an owner.** `IMP-0085`: table auditing is an
environment setting with no representation in solution source, five more tables are still to be
built, and each will ship unaudited unless someone remembers. The executable form needs environment
credentials, so it is out of reach from here as well as out of scope. What was done in scope:
`verify-shipped-content.py`'s NAVIGABILITY message said *"adding a table is TWO changes"* while the
check 20 lines below it said four. It now names all four, including the environment audit switch,
and states which three it can see.

## Verification

Executed: `verify-improvement-log.py` (92 entries, schema OK) · `scripts/ci/verify-pm-gates.sh`
(all PM gates pass, every known-bad fixture rejected, section 7 added and green) ·
`verify-shipped-content.py` green on real source and **exit 1 with all three errors** on the new
fixture · `verify-worklog.py`, `compute-invoice.py` and `verify-wbs-chain.py` now all report 64 h ·
`report-baseline-drift.py` — 0 fee/rate figures (D-3).

Not verified: the Pester suite (`src/tests/**/*.Tests.ps1`) was not run — PowerShell tests are
development-agent's and no `.Tests.ps1` was touched by this review, so the new gate check 1c has a
fixture but no permanent negative test. The coverage proof above is a run, not a regression test.
Nothing in this review was verified against a live environment.
