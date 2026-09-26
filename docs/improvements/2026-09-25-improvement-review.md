# Improvement Review — 2026-09-25 (1)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 10 NEW → 6 clusters (1 further unread entry excluded, named in §5; 3 entries appended during drafting folded in, see the note at the end of §2)
**Trigger:** blocker escalation — `IMP-0883`, unread
**Gate:** `APPROVE IMPROVEMENTS`
**Status:** ~~DRAFT — parked at the gate, nothing applied~~ **APPLIED 2026-09-25** — approved by
Anna Southern ("Approved and approve improvements", relayed verbatim by lead-agent). All four
changes landed as drafted; 3 entries closed, 7 deferred with reason. See §8.

---

## Summary

The build was blocked by two faults in the trustee portal's code, and **both are already fixed** by
the development-agent dispatch running alongside this review. I re-ran the test suite myself instead
of reading the fix's description: all 43 test files and all 797 tests pass. That fault needs no rule
change. It was a defect in one app's own test, and the fix belongs in that test, where it now is.

The other six unread findings were cheap to review in the same pass, so I did. Four of them are
worth a small, durable change: **one pipeline-agent instruction, one skill paragraph, one knowledge
line, and one registered number**. The three DocuSign findings stay open, because only a person in
the live flow designer can confirm them.

Net: **0 new constraints, 0 new scripts, 2 skill/knowledge edits, 1 agent-file edit, 1 other.**

---

## 1. Regression check — did the last review's changes work?

The last review applied was [review 4 of 2026-09-24](2026-09-24-improvement-review-4.md).

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| Path-segment comparison in `verify-component-shape.py` (`component-shape` + `component-shape-packed`, [build config L378](../../config/revitalise-grant-automation-build.yml#L378), [L923](../../config/revitalise-grant-automation-build.yml#L923)) | 2026-09-24 | `platform-contract-guessed-not-groundtruthed` | **Yes, but not where the gate looks** (the DocuSign designer finding, cluster C) | **Working.** The recurrence is a connector parameter inside a flow's JSON, resolved live against a DocuSign template. That surface has no source of truth this repository can read, as the skill's [dynamic-connector section](../../skills/how-to-verify-a-platform-contract.md#L68) already states. It is not a gate that failed to fire |
| Disproved inert-folder claim replaced in `component-shapes.yml` | 2026-09-24 | same | No | Working |
| Surviving header comment corrected in the Quick View Form | 2026-09-24 | `declared-policy-not-mechanically-enforced` | No | Working |

**Changes whose class recurred after a *prose* fix:** none.
**Changes whose class recurred after a *gate*:** none within the gate's scope. The build of
2026-09-24 19:51 ran both `component-shape` steps green, and the 2026-09-25 13:12 build failed at
step 74 of 74, after both had passed.

| Closure-level audit | Answer |
|---|---|
| Did the closure evidence match the level the defect was visible at? | Yes. Review 4 closed its critical finding on a V2 re-run it performed itself |

---

## 2. Clusters and promotion decisions

### Cluster A — the build blocker

```
CLUSTER: build-blocked-by-incomplete-code-app-work  (x2: IMP-0883, IMP-0884)
Altitude:   INSTANCE — one app's own test file, one missing page; no general mechanism
Ladder row: "One instance, specific to one feature, no general mechanism" → stays a log note
Becomes:    nothing in agents/, constraints/, skills/ or knowledge/. The finding's own
            proposed_change targeted src/…/print.test.ts, which is product source, and it has
            already landed there (comment-stripping before the scan, citing this finding by id)
Retires:    nothing
Cites:      IMP-0883, IMP-0884
Residual:   a comment-blind text scan can still exist in some OTHER test file. One instance does
            not justify a rule about how product tests scan source; a second would.
```

**The measurement.** When the dispatch was written, both root causes were live. At draft time,
neither was:

| Root cause | State at draft time | Evidence |
|---|---|---|
| `App.tsx` imports a page that does not exist | **Fixed.** `pages/GroupsListPage.tsx` and its test now exist (untracked, created by the parallel dispatch) | `export function GroupsListPage` at [GroupsListPage.tsx L54](../../src/code-apps/trustee-review-portal/src/pages/GroupsListPage.tsx#L54) |
| The print test's export-library regex matches the `.xlsx` extension in a citation comment | **Fixed.** Comments are stripped before scanning | [print.test.ts L118](../../src/code-apps/trustee-review-portal/src/styles/print.test.ts#L118) |
| The failing reproduction | **Re-run by me:** `npm --prefix src/code-apps/trustee-review-portal run test -- --run` | 43 of 43 files, 797 of 797 tests, 0 failures |

**Why this is not promoted, on the merits.** The lesson the finding proposes, *"narrow the regex to
code, not comments"*, is a property of one test in one app. This repository already has the general
rule it would fall under. The rule is *"assert on values, not on phrases"*, in
[improvement-agent.md](../../agents/improvement-agent.md#L748), and it has been measured five times
across three reviews. That rule governs gates this agent writes. Extending it to every product test
on the strength of one collision would be the speculative rule that the promotion skill's
[§4](../../skills/how-to-promote-a-finding.md#L247) excludes.

**Disposition: CLOSE both.** Both findings are V2 and I re-ran the reproduction, so each closure carries a
`reobserved` record. The second finding is development-agent's confirmation of the fix, and it names
the first as the one it corrects. Its own count of 797 passing tests matches mine.

**One caution, because this touches another agent's live work.** The fix is on disk but
**uncommitted and untracked**, and development-agent's dispatch may still be running. So the
closure's `reobserved` record names the working tree I ran against, not a commit. The build that
re-runs `code-app-unit-tests` is still the owner of V2-on-a-committed-tree.

### Cluster B — a pipeline stage reported done with a declared step unrun

```
CLUSTER: pipeline-dispatch-stops-before-declared-post-deploy  (x1: IMP-0879, three occurrences)
Altitude:   CLASS — the omission is independent of the Code App; any post_deploy entry a
            narrowly-worded brief does not name is exposed to it
Ladder row: "An agent had the information and still did the wrong thing" → agent-file edit
Becomes:    agents/pipeline-agent.md — step 4 of "Executing an Environment Block" binds every
            declared post_deploy entry regardless of the brief's scope; the success report and
            the stage log line name each entry and its outcome (change 1)
Retires:    nothing
Cites:      IMP-0879
Residual:   prose only. No gate reads a dispatch's report. The new report line gives a fixed
            token a later gate could anchor on, so the escalation is cheap if this recurs.
```

**Why prose and not the finding's proposed script.** Its first option, a check that reads
`pipeline.log` and infers which solution imports should have triggered a push, reads a log for
meaning. This project has measured that kind of check at 48–100% false. Its second option, making
the omission visible in the report itself, is the one I took. A recurrence after this change is the
regression-check trigger to escalate it to a gate. That gate would be a presence check for the new
report line, a value check that does not have the precision problem.

**Premise re-measured.** The dev block does declare a `post_deploy` entry
([pipeline config L1072](../../config/revitalise-grant-automation-pipeline.yml#L1072)). Step 4 does
say *"Each `post_deploy` step in order"* ([pipeline-agent.md L423](../../agents/pipeline-agent.md#L423)),
and the success report block has no line for it
([L469](../../agents/pipeline-agent.md#L469)). The three `SUCCESS`/`FAILED` stage lines between the
2026-09-20 push and the 2026-09-25 push do not mention the Code App.

**Disposition: DEFER from the start.** The defect is V3: it shows only when a pipeline dispatch
runs, and no one in this session can run one. The change lands, and the entry stays open until the
next DEV dispatch's success report is seen to list its post-deploy steps.

### Cluster C — DocuSign flows that the live designer refused to save

```
CLUSTER: connector parameter shape wrong at the live designer
         (x3: IMP-0880 platform-contract-guessed-not-groundtruthed,
              IMP-0882 connector-property-renamed-not-removed,
              IMP-0881 malformed-connector-collection-renders-as-loop-symptom-in-designer)
Altitude:   CLASS for one lesson (IMP-0882's); the other two stay notes
Ladder row: "An agent had the information and still did the wrong thing" → skill edit
Becomes:    skills/how-to-verify-a-platform-contract.md, dynamic-connector subsection — the
            mandatory pre-activation designer step covers the operation's WHOLE parameters
            block, not only the property registered as dynamic (change 2)
Retires:    nothing
Cites:      IMP-0882, IMP-0880
Residual:   still no static route to a dynamic connector schema, and none is possible. The skill
            changes the scope of the human session, not what a machine can see.
```

I grouped these by mechanism rather than by class label, because they came from the same two flows,
the same designer session and the same reviewer. The labels differ only because three agents
wrote them.

| Finding | What it adds | Already covered? | Decision |
|---|---|---|---|
| Envelope action: `tabs` and array-shaped `signers` rejected | The register flagged both as open guesses, and the designer confirmed both wrong | **Yes.** The skill already makes the designer step a blocking pre-activation action ([L68](../../skills/how-to-verify-a-platform-contract.md#L68)). The finding itself proposes no change | Note only |
| Trigger: `name` rejected, and a separate *"Connect configuration name is missing"* | **One operation drifted on a property nobody flagged as dynamic.** Only `events` was registered | **No.** The skill's table treats the static half as *"E2 at best — commit it"*, and nothing extends the designer session to it | **Promote** (change 2) |
| Designer showed a loop where the source has none | A hypothesis about how the designer renders a malformed collection | Not a confirmed mechanism, and the finding says so | Note only. The promotion skill excludes an argued mechanism ([§4](../../skills/how-to-promote-a-finding.md#L255)) |

**Engine vs client (skill §6).** Change 2 names DocuSign and a DocuSign operation, which are vendor
facts. It names no table, environment or client. I grepped the drafted paragraph for `rev_`,
`Revitalise` and the environment names, and none are present. So it can go into the engine skill.

**Disposition: DEFER all three from the start.** Two are V4, and one is an unconfirmed designer
behaviour. The closing observation for all three is the same: the reviewer reopens both flows in
the DEV designer after development-agent's correction, saves them, and reports what the designer
shows.

### Cluster D — this checkout's installed packages cannot be trusted

```
CLUSTER: stale-local-install-produces-spurious-typecheck-failure  (x1: IMP-0878; sibling IMP-0857)
Altitude:   CLASS — two different symptoms (missing binary; stale type packages) with one
            cause and one remedy
Ladder row: "cause is general and a human needs to know it" → knowledge line
Becomes:    knowledge/technology/build-and-deploy.md, "Operating Facts of This Repository and
            Machine" — one line: run npm ci before any npm script in an interactive session
            (change 3)
Retires:    nothing
Cites:      IMP-0878, IMP-0857
Residual:   no gate can see what an interactive session did before running a script. The build
            is already safe: its code-app-install step runs npm ci (build config L705).
```

**Premise re-measured.** The Operating Facts section
([build-and-deploy.md L473](../../knowledge/technology/build-and-deploy.md#L473)) says nothing about
`node_modules` or `npm ci`. The only `npm ci` in the file is the generic build recipe at L14. The
sibling finding about the missing binary stays in its own reviewer-deferred state. This line
generalises its remedy but does not change its disposition.

**Disposition: CLOSE** (V1, on the needle).

### Cluster E — a dev summary citing a bundle size that is half the real one

```
CLUSTER: stale-claim-contradicting-rechecked-source  (x2 in scope: IMP-0877, IMP-0885; x20 in the log)
Altitude:   CLASS — a hand-typed figure with a machine-readable source beside it; the neighbouring
            class hand-maintained-count-drifts-from-source (x35) already has a working answer
Ladder row: "A tool could catch it mechanically" → use the existing gate
Becomes:    one row in scripts/derived-counts-registry.json, derived from bundle-budget.json's
            measured_bytes, and the dev summary's figure corrected to match (change 4)
Retires:    nothing
Cites:      IMP-0877, IMP-0885
Residual:   derived-counts is SOFT (--warn-only), so drift reports but does not block. And
            measured_bytes itself is hand-updated; the code-app-bundle-budget step checks only
            max_bytes. Both are the existing design, not something this change weakens.
```

**Premise re-measured.** The dev summary says *"558 kB (151 kB gzipped)"*
([dev summary L4893](../../docs/development/revitalise-grant-automation-dev-summary.md#L4893)), and
`bundle-budget.json` records `measured_bytes: 1204716`, measured on 2026-09-01
([bundle-budget.json](../../src/code-apps/trustee-review-portal/bundle-budget.json)). The planned
derivation prints `1205`, and the claim phrase occurs exactly once in the file. The verifier's
number parser accepts bare digits only ([verify-derived-counts.py L132](../../scripts/verify-derived-counts.py#L132)),
so the corrected sentence uses `1205 kB`, without a thousands separator.

**Whose file.** The dev summary belongs to development-agent. This is a repository fact settled by a
command, and the fix adds a discharge condition that names that command: the registry row. That is
the case improvement-agent.md permits me to correct in another agent's file. The `558 kB` figure is
kept in the sentence as history.

**Disposition: CLOSE** (`n/a`, on the needle).

**The second member stays a note.** A comment header in `ApplicationDetailPage.tsx` said the
summary pack's panel order was delivered. The reviewer found the opposite on the live DEV screen,
and the panel-order test agreed with the comment, because it had been written to match the fix and
not the requirement. There is no value to register, since the source of truth is a PDF.
development-agent has already rewritten the test against the PDF's order. **DEFER from the start:**
the finding is V4, and it closes when the reviewer confirms the panel order on the live screen.

### Cluster F — a finding timestamped later than the clock

```
CLUSTER: finding-timestamp-ahead-of-clock  (x1: IMP-0886, logged by this review)
Altitude:   INSTANCE — one occurrence; the altitude rule holds a gate for the second
Ladder row: "One instance… no general mechanism yet" → stays a log note
Becomes:    nothing now. The proposed guard (allocate-improvement-id.py --append refusing a
            future ts) is recorded on the entry for the second instance
Retires:    nothing
Cites:      IMP-0886
Residual:   until the guard exists, a composed ts can block an honest closure for hours
```

**What happened.** The fix-confirmation finding in cluster A carries a time of 14:20, but this
machine's clock read 13:40 CEST when I measured it. The log validator correctly refuses a
re-observation dated before the finding it re-observes. So **cluster A's second finding can only be
closed after 14:20.** If the keyword arrives before then, I will close the blocker, leave its
confirmation entry open with that reason, and say so in the applied record. That does not hold the
blocker trigger. The simulation below showed the trigger clears on the blocker's closure alone.

**Disposition: DEFER** (single instance; revisit on a second).

### Amendment note — written last

Three findings were appended while this draft was being written: two by development-agent, and one
by this review, after the disposition simulation surfaced the timestamp problem. All three are now
folded in. The fix confirmation joins cluster A, the panel-order finding joins cluster E as a note,
and the timestamp finding is cluster F. The gate block, §2, §6 and the `reviewed_in` stamps all carry
them. Nothing is outstanding from the amendment.

### Disposition simulation (run before parking)

I applied the proposed statuses and fields to a scratch copy of the log and ran
`verify-improvement-log.py --check --log <copy>`. **The blocker trigger clears.** The only error was
the future timestamp that cluster F records. The two entries that close on needles the changes will
create (clusters D and E) could not be simulated as closed, because their needles are not on disk
until the changes are applied. I checked that the real log was byte-identical after the simulation.

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | agent | `agents/pipeline-agent.md` | Step 4 binds every declared `post_deploy` entry whatever the brief names; the success report and stage log line list each entry DONE/SKIPPED | IMP-0879 | N/A — instruction change | N/A |
| 2 | skill | `skills/how-to-verify-a-platform-contract.md` | The pre-activation designer step resolves the operation's whole parameters block, not only the registered dynamic property | IMP-0882, IMP-0880 | N/A — instruction change | N/A |
| 3 | knowledge | `knowledge/technology/build-and-deploy.md` | Operating fact: run `npm ci` before any npm script in an interactive session on this checkout | IMP-0878, IMP-0857 | N/A — knowledge line | N/A |
| 4 | other | `scripts/derived-counts-registry.json` + dev summary L4893 | Register the dev summary's bundle figure against `bundle-budget.json`; correct 558 → 1205 kB | IMP-0877 | YES — `python3 scripts/verify-derived-counts.py` | already wired (`derived-counts`, SOFT) |

**Constraint budget:** 0 of 3 used.

### Exact wording

**Change 1:** [pipeline-agent.md L423](../../agents/pipeline-agent.md#L423), step 4 becomes:

> 4. **Every** `post_deploy` step the config declares for this environment, in order (idempotent
>    scripts; record per-resource results) — **whether or not the dispatch brief names it.** A brief
>    scoped by WBS id to a solution-side fix does not narrow this list. Three consecutive DEV
>    dispatches reported SUCCESS without running a declared Code App push, and the live app ran
>    five days behind the solution (`IMP-0879`).

The success report block ([L469](../../agents/pipeline-agent.md#L469)) gains, after `Prerequisites:`:

> `Post-deploy steps: <n> declared / <n> DONE / <n> SKIPPED — <each entry by name: DONE | SKIPPED (reason, owner)>`

The Logging section gains one sentence: *"A `SUCCESS` stage line names each declared `post_deploy`
entry and its outcome; an entry absent from the line is read as not run."*

`agents/` is in the `.engine` submodule, so this change is published in the order that section of
my instructions requires: push the submodule first, then bump the pointer.

**Change 2:** inserted after the dynamic-connector table in
[how-to-verify-a-platform-contract.md](../../skills/how-to-verify-a-platform-contract.md#L68):

> **The pre-activation V4 step covers the operation's WHOLE parameters block, not only the rows
> registered as dynamic.** Added 2026-09-25 (`IMP-0882`). E2 evidence for the static half is a
> claim about the documentation on the day it was read, not about the live operation. DocuSign's
> `CreateHookEnvelopeV4` trigger rejected a `name` parameter the connector reference still showed,
> and separately reported a missing *Connect configuration name*. Neither property was in the
> register, because only `events` had been flagged dynamic. So the designer session that opens an
> action to resolve one dynamic property resolves and saves **every** parameter of that action,
> and the register gets one row per property it had to change. A designer error about a property
> nobody flagged is evidence that the static half has drifted as well.

**Change 3:** appended to Operating Facts in
[build-and-deploy.md L473](../../knowledge/technology/build-and-deploy.md#L473):

> **In an interactive session, run `npm ci` before any `npm` script in a code app, because this
> checkout's `node_modules/` cannot be trusted.** The repository sits on a synced OneDrive path,
> and the installed packages can differ from `package-lock.json` with no source change. That has
> shown up twice: once as a missing binary (`vite: command not found`, `IMP-0857`), and once as
> stale type packages that failed `tsc --noEmit` with 47 errors, all in test files (`IMP-0878`).
> Both cleared on `npm ci` with the source unchanged. The build's `code-app-install` step already
> runs `npm ci`; this is for every other session. A typecheck failure seen before `npm ci` has
> run in this session is not yet evidence of a source defect.

**Change 4:** the dev summary's item (1) opens:

> (1) Vite reports the bundle at 1205 kB (about 472 kB gzipped) against its 500 kB advisory —
> derived from `bundle-budget.json`'s `measured_bytes` and registered in
> `scripts/derived-counts-registry.json`, so this figure is checked rather than retyped.
> Previously recorded as 558 kB (151 kB gzipped) on 2026-08-22, before recharts@3.10.1 was added
> (wbs:6.9). Accepted: recharts and Fluent UI v9 are the bulk, …

The registry row: `id: dev-summary-code-app-bundle-kb`,
`claim_pattern: "Vite reports the bundle at (?P<number>[0-9]+) kB"`, derived by a shell command
that reads the `.js` asset's `measured_bytes` from `bundle-budget.json` and divides by 1000
(rounded, which gives 1205 today).

---

## 4. Retirements

> Retirement check performed: 86 live constraint rows, 10 retired (both counts derived with the
> grep in improvement-agent.md). None is currently redundant. No change in this review touches a
> constraint row, and the two constraints adjacent to this batch are `C-TECH-055` (bundle triage),
> which this review strengthens, and `C-TECH-053` (verification levels), which decided three of the
> dispositions above. Both are live and doing their job.

---

## 5. Findings left unprocessed

**Deferred:** IMP-0862

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| IMP-0862 | `gate-scope-mismatch` | **The reviewer already decided this one.** Review 4's §8 records that the `verify-tad-coverage.py` sub-cluster was *"parked for the next batch review"*. This review was triggered by a blocker and is not that batch. Widening `--tad` also needs a precision measurement over every architecture document before it is wired, which is batch-review work. The gap is already documented in the script's own header (`verify-tad-coverage.py` L322) | the next batch review, per the reviewer's 2026-09-24 decision |

Excluded by state, not read: 1 `awaiting-approval` entry, which waits on its own document, and 206
`reviewer-deferred` entries.

---

## 6. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 881 | 882 (1 finding logged by this review, cluster F) |
| Entries closed | — | 4 (`IMP-0883`, `IMP-0884`, `IMP-0878`, `IMP-0877`) |
| Entries deferred with a recorded reason | 206 | 212 (`IMP-0879`, `IMP-0880`, `IMP-0881`, `IMP-0882`, `IMP-0885`, `IMP-0886`) |

To be regenerated with `python3 scripts/generate-known-failure-modes.py` at apply time and confirmed
with `--check`, followed by `verify-derived-counts.py`.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-25-improvement-review.md

Findings processed: 10 NEW  →  6 clusters
Regression check:   3 prior changes audited, 1 class recurred (outside the gate's reach)
Proposed:           0 constraints (cap 3), 0 gates/scripts, 2 skill/knowledge edits,
                    1 agent-file edits, 0 retirements, 1 other
Altitude calls:     4 generalised from instance to class, 4 left as notes
Digest:             will regenerate — 4 closed, 6 deferred with reason, 1 excluded

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Applied

**Authorisation.** `APPROVE IMPROVEMENTS`, sent by Anna Southern in her own conversation turn
(*"Approved and approve improvements"*) and relayed verbatim by lead-agent. The relay meets all four
conditions of WORKFLOW.md's channel rule. It was recorded in `logs/routing.log` at 13:44, before
any change.

**Re-verified before applying (step 8).** Every premise was re-measured at 13:44 against the tree.
The fix is still on disk and `GroupsListPage.tsx` still exists. The dev summary still said 558 kB,
`bundle-budget.json` still derives to 1205, and neither agent file had changed. The reproduction
was re-run: 43/43 files and 797/797 tests passed, exit 0. **Nothing was withheld, and nothing was
narrowed.**

| # | Type | Change | Landed at | Verified by |
|---|---|---|---|---|
| 1 | agent | Step 4 binds every declared post-deploy step; report line and log-line rule added | `agents/pipeline-agent.md` (engine submodule) | needle grep: 1 match |
| 2 | skill | Whole-parameters-block paragraph after the dynamic-connector table | `skills/how-to-verify-a-platform-contract.md` (engine submodule) | needle grep: 1 match |
| 3 | knowledge | `npm ci` operating fact | `knowledge/technology/build-and-deploy.md` | needle grep: 1 match |
| 4 | other | Figure corrected 558 → 1205 kB; `dev-summary-code-app-bundle-kb` registered | dev summary L4893, `scripts/derived-counts-registry.json` | `verify-derived-counts.py`: 11 of 11 claims match. The registry diff is 13 insertions and 0 other changes |

**Entries.**

| Entry | Outcome |
|---|---|
| `IMP-0883` (the blocker) | **APPLIED**, with a V2 `reobserved` record from the 13:44 re-run |
| `IMP-0877`, `IMP-0878` | **APPLIED** at their levels (`n/a`, V1), on needles |
| `IMP-0879`, `IMP-0880`, `IMP-0881`, `IMP-0882`, `IMP-0885`, `IMP-0886` | **Deferred with reason**, as drafted |
| `IMP-0884` | **Deferred.** This is the case §2's cluster F said might happen: the keyword arrived at 13:44, before the entry's own timestamp of 14:20, so no honest re-observation can be recorded yet. It closes after 14:20 with a fresh re-run |

**Housekeeping that compliance caused.** Regenerating the digest drifted the registered line-count
sentence in `generate-known-failure-modes.py`. Both copies (instance and `.engine`) were corrected
from 772 to 779 lines, and they are byte-identical.

**Gates run after applying:**

| Gate | Result |
|---|---|
| `verify-improvement-log.py --check` | exit 0, **no trigger** |
| `generate-known-failure-modes.py --check` | current, 883 entries |
| `verify-derived-counts.py` | exit 0 |
| `verify-class-defences.py` | exit 0 |
| `verify-engine-instance-split.py` | exit 0 |
| `verify-doc-line-links.py` | exit 0 |

**Arrived during application, not processed.** A second improvement-agent dispatch ran at the same
time. It correctly declined to redraft, stopping at BLOCKED, and logged `IMP-0887`, a friction
finding that proposes no change. It is unread and non-blocking. It was appended after the keyword,
so it is outside what was approved, and it goes to the next review. I checked that the concurrent
dispatch made no duplicate edits to any file this review changed.

**Not yet published.** Changes 1 and 2 live in the `.engine` submodule, which already had other
uncommitted edits in it before this review. Nothing has been committed or pushed. Publishing needs a
commit in `.engine`, `git -C .engine push origin HEAD:main`, a check with
`branch -r --contains HEAD`, and only then the instance commit with the pointer bump.

