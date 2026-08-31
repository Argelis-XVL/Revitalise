# Improvement Review 31 — 2026-08-28

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 11 `unread` ids across 13 log lines → 4 clusters
**Trigger:** unread `blocker` — six of them, per
[`agents/WORKFLOW.md` L254](../../agents/WORKFLOW.md#L254) *"immediately — do not batch"*. The
dispatch also names the gate's own integrity errors, which overlap the same lines.
**Gate:** `APPROVE IMPROVEMENTS`
**Status:** ~~DRAFT — nothing in this document is on disk~~ — **APPLIED 2026-08-28.** The reviewer
sent `APPROVE IMPROVEMENTS`; all six changes of §3 are on disk, all 13 processed log lines are
dispositioned, and §10 records what landed, the three corrections made at application, and the one
thing this review does **not** achieve — `verify-improvement-log.py --check` is down from 13
problems to 1, and that 1 is the batch trigger, which needs the batch review.
**Scope note:** this is the narrow blocker-plus-integrity scope, **not** a pass over the whole
queue. 36 further `unread` entries and 41 `reviewer-deferred` entries are untouched and §5 names
them.
**WBS:** system work, not billable
([C-COM-002](../../constraints/commercial/commercial-constraints.md#L35)). Two findings in scope
carry a commercial consequence belonging to another agent; §5 names both.

---

## Summary

**The blocker that halted your build is one mechanism, and it is mechanically fixable today.**
[`generate-known-failure-modes.py`](../../scripts/generate-known-failure-modes.py#L244) parses the
log with a bare `json.loads` and validates nothing, so the one command every agent *is* instructed
to run reports success over a file the authoritative validator rejects. Three agents appended, saw
exit 0, and moved on. Eleven of the gate's thirteen problems are that single gap.

**Of the six blockers, two are already resolved on disk, three are open and need delivery
dispatches, and one is fixed by this review.** [`IMP-0371`](../../logs/improvement-log.jsonl#L369)
was answered by the architect's own [ADR-032](../../docs/architecture/trustee-portal-visual-refresh-architecture.md#L1918)
within the hour — I re-ran its build gate and it exits 0.
[`IMP-0352`](../../logs/improvement-log.jsonl#L349)'s contrast defect is fixed and covered by 26
passing assertions. The three that remain are all one story, below.

**`IMP-0377` is confirmed live, and worse than it reads.** ADR-030's mechanism is dead — the
connector crashed the app's boot twice — yet the flow in solution source still carries
`"kind": "PowerApp"`, ADR-030 still reads `Derived`, and Revision 4 explicitly declines to re-open
it. Meanwhile `power.config.json` has **already dropped** `shared_logicflows`, so the app cannot
invoke that flow at all, and [`IMP-0392`](../../logs/improvement-log.jsonl#L374) records the reviewer
hand-changing the live DEV flow in the designer. **Source and DEV now disagree, and the next
solution import reverts DEV to the shape that crashes.** This needs `architect-agent`, then
`development-agent` — it is not a rule change and I am not applying it.

**The measurement changed the design, twice.** The obvious version of change 1 — have the generator
call `check_schema` and refuse — measured **4 firing commits across 27, 1 true positive, 3 false**.
Narrowed to the entry's *own shape* and excluding claims about the tree, it measures **1 of 27, 1
true, 0 false**, and the one commit it refuses is `6158243` — the commit that carried `IMP-0074`'s
duplicate id, which CI never caught because the workflow was dead that day.

**What needs you:** **no new constraints** against a cap of three, two new/edited scripts, one skill
edit, seven agent-file edits, one `CLAUDE.md` edit, two knowledge lines, no retirements, and **three
decisions — one of which gates a delivery dispatch and should be answered before the held build
resumes.**

---

## 1. Regression check — did review 30's changes work?

Review 30 applied 13 changes on 2026-08-26 ([its applied record](2026-08-26-improvement-review.md#L594)).
Every change was re-run against the tree just now, not read.

| Prior change | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|
| 9 — `--warn-only` on [`verify-improvement-log.py`](../../scripts/verify-improvement-log.py#L1993) | `gate-reassures-wrongly` | **YES, once — the blocker that summoned me** | **Wrong altitude.** See below |
| 10 — [`build-agent.md` step 7b](../../agents/build-agent.md#L78) manifest re-check | `gate-reassures-wrongly` | **YES, same instance** | **Wrong altitude.** Prose, and the appending agents never reach it |
| 1 — `CLUSTER-COUNT` in [`verify-review-document.py`](../../scripts/verify-review-document.py#L38) | `approved-document-internally-inconsistent` | **YES, seven times** | **Gate working, correctly scoped, and RED right now.** See below |
| 2 — [`verify-document-status-consistency.py`](../../scripts/verify-document-status-consistency.py#L1) | `approved-document-internally-inconsistent` | as above | **Working.** 15 citations across 68 documents, all agreeing — its one true positive got fixed |
| 3 — `requirement-id-uniqueness` → HARD | `identifier-namespace-collision-across-documents` | NO | **Working.** 3 documents, 170 identifiers, 0 allocated twice |
| 6 — [`dump-entity-attributes.py`](../../scripts/dump-entity-attributes.py#L1) | negative schema claims | NO new negative-claim instance | Working — leave alone |
| 13 — one lesson count | `hand-maintained-count-drifts-from-source` | **YES, three times** — but in delivery prose, not here | **Working.** `--check` reports the digest current at 390 entries |
| 4, 5, 7, 8, 11, 12 | various | NO | Working — leave alone |

**Changes 9 and 10 are the regression rule firing exactly as written.** Review 30 read `IMP-0343`
as *"the validator is awkward to run"* and answered with a flag plus an instruction in one agent
file. [`IMP-0369`](../../logs/improvement-log.jsonl#L367) shows the real mechanism one day later:
the problem was never ergonomics, it is that **two scripts disagree about validity and only the one
nobody is instructed to run is authoritative.** A recurrence after a prose fix escalates to a gate
— [`how-to-promote-a-finding.md` L22](../../skills/how-to-promote-a-finding.md#L22) — and cluster A
does that.

**Change 1's gate is red on three documents and that is the gate working, not failing.**
`2026-08-21-improvement-review.md:5` claims 17 clusters against 7 blocks; `2026-08-22-improvement-review.md`
claims 4 against 3, at lines 4 and 214. Review 30 measured exactly these three as its true
positives and shipped the gate; nobody has since corrected the three documents. A fourth error,
`LOST-DEFERRAL` on `2026-08-25-improvement-review.md:39`, is in the same population. **These are
`improvement-agent`'s own documents and therefore mine to fix — §7 decision 3 asks whether you want
that done now or in the batch review.**

**Change 13's class recurred three times, and all three are one delivery act.**
[`verify-derived-counts.py`](../../scripts/verify-derived-counts.py) is red (SOFT): the secured-column
count moved 67→68 and the REV Trustee role header 51→52 when `rev_ethnicgroup` landed.
[`IMP-0363`](../../logs/improvement-log.jsonl#L360) — in this review's scope — updated the *test*
counts and not these three *prose* counts. That is why §3 does not close it.

---

## 2. Clusters and promotion decisions

```
CLUSTER A: gate-reassures-wrongly + learning-substrate-destroyed
           (x9 log lines, 8 ids: IMP-0369(L367) reports it; IMP-0363, IMP-0364, IMP-0365,
            IMP-0367, IMP-0368(L366), IMP-0368(L374), IMP-0369(L375), IMP-0375 are the damage)
Altitude:  CLASS. gate-reassures-wrongly is x15 and was answered one day ago with a flag plus
           one agent-file line (review 30, changes 9+10). The duplicate-id half is worse: SIX
           recorded instances of one prose rule -- IMP-0080 (08-19), IMP-0301, IMP-0312,
           IMP-0339, IMP-0369, IMP-0375 -- over eight days, plus two live duplicates in the
           tree right now. The altitude rule forbids a seventh instance patch.
Ladder row: "a tool could catch it mechanically" + "second instance -> generalise"
Becomes:   change 1 makes the command agents ALREADY run authoritative (the highest-leverage
           fix, because it needs nobody to remember anything); change 2 gives id allocation a
           command instead of a paragraph; change 3 repairs the read path that misled them;
           change 4 repairs the eight damaged entries and reallocates the two duplicate ids.
Retires:   nothing. Change 1 does not make the validator's own build step redundant -- that step
           also checks triggers, citation stamps and corrections, none of which change 1 reads.
Cites:     IMP-0369(L367), IMP-0080, IMP-0301, IMP-0312, IMP-0339, IMP-0375
Residual:  THREE, and the second is the honest limit.
           (a) Change 2 NARROWS the two-live-sessions race from minutes to one write; it cannot
               eliminate it on a synced SharePoint path. Change 1 is the backstop that makes a
               collision visible at the next digest run instead of at the next commit.
           (b) Change 1 refuses on the entry's OWN SHAPE only. An entry that is well-formed and
               wrong -- a fabricated root cause, a mis-stated class -- passes it, as it must.
           (c) Change 3 is prose and prose is what just failed. It is proposed only because
               change 1 makes it cheap to obey, not as the mechanism.
```

```
CLUSTER B: approved-document-internally-inconsistent + code-apps-new-connector-blocks-boot
           (x4: IMP-0377 (blocker), IMP-0358 (blocker), IMP-0365 (blocker), IMP-0368(L374))
Altitude:  INSTANCE for the documents, CLASS for the knowledge. The document half is one
           feature's architecture decision and belongs to architect-agent -- promoting it into
           a rule would be writing a constraint about one ADR. The platform half is a real
           class: THREE instances of "a new connector type blocks a Code App's boot", and the
           digest undercounts it as x2 because IMP-0358 recorded the class in `class` and a
           different value in `class_instance_of` (IMP-0330's defect, in a new place).
Ladder row: "one instance, but the cause is general and a human needs to know it" -> knowledge/
Becomes:   change 5, one knowledge entry in knowledge/technology/code-apps.md carrying the
           boot-risk rule, the working write-then-poll alternative, and the private-window
           verification rule. The ADR itself is a DISPATCH, named in §7 decision 1, NOT a
           change in this review.
Retires:   nothing.
Cites:     IMP-0358, IMP-0365, IMP-0368(L374)
Residual:  TWO. (a) No gate compares a flow's trigger kind against what the Code App's client
           expects to call. Both single-sided gates exist -- verify-flow-definition-language.py
           and verify-code-app-data-sources.py -- and a cross-check is buildable, but the
           corpus is ONE app and ONE flow, so it cannot be measured, and review 29's cluster C
           measured an unmeasurable pairing design at 48% wrong. Deliberately not built; §7
           decision 2 asks whether to build it after the ADR lands and the corpus is real.
           (b) The root cause of the boot crash is still unknown. This knowledge line records
           what was eliminated and what works around it, not why.
```

```
CLUSTER C: requirement-names-data-the-solution-cannot-supply  (x1 in scope: IMP-0371)
Altitude:  NONE -- already resolved on disk, and the entry's status is stale (IMP-0169).
Ladder row: none. The finding's own architectural answer was written the same hour by the same
           agent, as ADR-032 (Revision 3, 2026-08-27), which keeps the HARD gate unmodified and
           renders FR-078's restricted state from a build-derived catalogue instead.
Becomes:   a disposition, not a change. Reobserved at V2 per C-TECH-053: the gate IMP-0371 said
           would fail the next build, verify-code-app-column-bindings.py, exits 0 today, and
           generate-trustee-field-catalogue.py --check reports 11 validated entries across 2
           groups -- exactly the eleven columns A-05 named.
Retires:   nothing.
Cites:     IMP-0371
Residual:  ONE, and it is a finding about the class NAME. This is the FIFTH member of
           `requirement-names-data-the-solution-cannot-supply` and the second in a row that is
           not about data the solution cannot supply -- review 30 already established that for
           the first four. Here the column exists, is secured, and a gate forbids binding it.
           The class name is misleading a third review running. Renaming a class rewrites the
           digest's join key for 5 entries and is NOT in this narrow scope; it is §7 decision 3's
           companion and belongs to the batch review.
```

```
CLUSTER D: platform-contract-guessed-not-groundtruthed  (x1 in scope: IMP-0352)
Altitude:  INSTANCE. The defect is fixed and the instance is DEFENDED by a wired build step --
           code-app-coverage (build.yml L1064) runs the app's vitest suite, which includes
           theme.test.ts's 26 contrast assertions. Reobserved at V2: 26 passed.
Ladder row: "one instance, but the cause is general and a human needs to know it" -> knowledge/
Becomes:   change 6, one knowledge line. IMP-0352's own proposal asks for a repo-wide
           scripts/verify-brand-contrast.py, and I am NOT proposing it: the gap it closes is
           "the NEXT code app has no such requirement", there is exactly one code app, and a
           gate whose corpus is one file cannot be measured against a corpus.
Retires:   nothing.
Cites:     IMP-0352
Residual:  TWO. (a) The class DID recur -- IMP-0385, supplied-design-asset-assumed-wcag-
           compliant, appended 22:40 the same day. It is unread, out of this narrow scope, and
           §5 names it; the second instance is what would justify the gate IMP-0352 asked for,
           and the batch review will have both. (b) theme.test.ts asserts the pairs it was
           written to assert. A token pair nobody thought of is still unchecked.
```

---

## 3. Proposed changes

| # | Type | Target | Change | Cites | Mechanically verifiable? |
|---|---|---|---|---|---|
| 1 | script | [`generate-known-failure-modes.py` L244](../../scripts/generate-known-failure-modes.py#L244) | `load()` runs the **structural** subset of [`check_schema`](../../scripts/verify-improvement-log.py#L703) and exits non-zero naming each bad entry, so the one command every agent is told to run is authoritative. Structural = the entry's own shape (id, `severity`, `observable_at`, `status`, required fields, `refusal_context`); **excludes** `evidence_grep` outcomes, which are claims about the tree | IMP-0369 | **YES, measured — current tree 11 findings / 11 true / 0 false; history sweep 1 of 27 commits / 1 true / 0 false** |
| 2 | script | `scripts/allocate-improvement-id.py` | Prints `max(id)+1` across the whole file; `--append <entry.json>` re-reads the maximum and writes the line in one `O_APPEND` write, then runs the validator | IMP-0080, IMP-0301, IMP-0312, IMP-0339, IMP-0369, IMP-0375 | **YES** — `--selftest`, plus a two-process concurrent-append fixture |
| 3 | skill | [`how-to-log-an-improvement.md` §3 L242](../../skills/how-to-log-an-improvement.md#L242) | "After appending" names the **validator first**, then the generator, and states plainly that the generator exiting 0 is not evidence the log is valid. Change 1 is what makes this true rather than hopeful | IMP-0369 | Enforced by change 1 |
| 3a | agent files | `architect-agent.md`, `development-agent.md`, `plan-agent.md`, `pm-agent.md`, `test-agent.md` | Improvement Capture block names the validator alongside the generator | IMP-0369 | **YES, measured — 5 files name the generator and not the validator; all 5 true positives** |
| 3b | agent files | `acceptance-agent.md`, `commercial-agent.md` | Both name **neither** script. Add the same two-command block | IMP-0369 | **YES, measured — 2 of 12 agent files, both true** |
| 3c | entry point | [`CLAUDE.md` L139](../../CLAUDE.md#L139) | Learning Rules rule 2 names only the generator; name both, validator first | IMP-0369 | Enforced by change 1 |
| 4 | log repair | [`logs/improvement-log.jsonl`](../../logs/improvement-log.jsonl) | Six `observable_at` values reduced to bare tokens with the caveats moved into `cost`/`what` **per IMP-0369's own lesson**; `IMP-0368`(L374) `severity: capability` → `rework` plus `capability: true`, the flag the schema actually provides ([skill L275](../../skills/how-to-log-an-improvement.md#L275)); `refusal_context` added to `IMP-0363`; the two duplicate ids reallocated | IMP-0369 | **YES** — the gate goes green or it does not |
| 5 | knowledge | `knowledge/technology/code-apps.md` | Adding a **new connector type** to `power.config.json` is a boot-risk change, not an additive one; `shared_logicflows` has failed twice under independent private-session reproduction; the working alternative is the Dataverse-row-trigger write-then-poll pattern, including the `isFresh` trap ([`roundStatistics.ts` L357](../../src/code-apps/trustee-review-portal/src/dataverse/roundStatistics.ts#L357)); verify every Code App push in a private window | IMP-0358, IMP-0365, IMP-0368(L374) | N/A — reference material |
| 6 | knowledge | `knowledge/technology/code-apps.md` | Fluent v9's `createLightTheme` does not guarantee AA: `colorBrandBackground` is `brand[80]` behind a hard-coded white, so a ramp whose shade 80 is under 4.5:1 ships a failing primary button. Compute every pair, including pairs a human said were fine | IMP-0352 | N/A — reference material; the instance is covered by [`build.yml` L1064](../../config/revitalise-grant-automation-build.yml#L1064) |

**Constraint budget: 0 of 3 used.**
[`C-TECH-061`](../../constraints/technology/technology-constraints.md#L131) already requires the log
to conform to the schema and already names the validator as its `Verify By`. The rule was never
missing; the **read path** was, and that is a script gap. Writing a new constraint row here would
be the fourth restatement of a rule that is already HARD.

### Which duplicate keeps its id, and why

The project has already settled this once. [`IMP-0375`](../../logs/improvement-log.jsonl#L368) records
its own reallocation from `IMP-0366` on the rule *"this entry collided with development-agent's
IMP-0366, which is cited by name in the dev summary and therefore kept its id."* **Neither of
today's pairs is cited by content anywhere** — the only mention is one dev-summary line describing
the collision itself. So the tiebreaker falls to append order, and to one decisive fact: `IMP-0369`
at line 367 is the blocker **this document cites throughout**, so renumbering it would break every
link above.

| Line | Currently | Becomes | Reason |
|---|---|---|---|
| 366 | `IMP-0368` (plan-agent, `rework`) | unchanged | Appended first |
| 367 | `IMP-0369` (plan-agent, `blocker`) | unchanged | Appended first, and cited by this review |
| 374 | `IMP-0368` (lead-agent, `capability`) | **`IMP-0392`** | Appended second, uncited |
| 375 | `IMP-0369` (lead-agent, `friction`) | **`IMP-0393`** | Appended second, uncited |

Ids are taken from `max()` **at application time**, not from the 391 read while drafting — that is
`IMP-0080`'s rule and `IMP-0312`'s cost, and two sessions have already been live on this path today.

### The measurement that forced change 1's design

**Dropped — "the generator calls `check_schema` and refuses on any error." Measured: 4 firing
commits across 27, 1 true, 3 false.** Named false positives, all three of which would have blocked
a digest regeneration over a correct file:

- `388291b` — `IMP-0161: status NEW, but <needle> ALREADY contains ...`. That is the `already-fixed`
  signal, which the gate itself reports as a **NOTE**, not an error. Refusing to regenerate because
  a finding's fix already shipped is precisely backwards.
- `fc5fb1d` and `a072849` — `IMP-0204: status APPLIED, but <file> does not contain <needle>`. A stale
  closure needle on a long-settled entry. Real information, and not a reason the digest cannot be
  built.

**Kept — the structural subset.** Re-measured: **1 firing commit of 27, 1 true, 0 false.** The one
it refuses is `6158243`, which carried `IMP-0074`'s duplicate id — the founding incident of
`IMP-0080`, which CI never reported because `ci.yml` was invalid that day. A gate that fires exactly
once across the log's whole history, on the one commit history records as broken, is the strongest
evidence this corpus can give.

---

## 4. Retirements

**No retirements, and the audit was run.** Derived, not typed — **10 retired, 80 live** — via
`grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l`. All ten retired rows were checked for a
fired reinstatement condition; none has one.

**Nothing this review adds makes a live row redundant.** Change 1 was checked for overlap against
`C-TECH-061`'s own `Verify By`: that row names the validator and two enforcement paths, and change 1
adds a **third** reader of the same schema rather than replacing either. The two named paths stay.

**The two standing candidates are named for the fourth review running, so they do not go quiet.**
[`C-TECH-011`](../../constraints/technology/technology-constraints.md#L155) still has no
verification and [`C-TECH-012`](../../constraints/technology/technology-constraints.md#L156) still
has neither a threshold nor a tool. Both are already retired; what is outstanding is your decision
whether either is reinstated with a real check or left retired permanently. **Unchanged from review
30 — this review does not re-ask it.**

---

## 5. Findings left unprocessed, and what this dispatch could not fix

**This is the narrow blocker scope, and the caps are stated rather than silent.**
Per [`improvement-agent.md` L101](../../agents/improvement-agent.md#L101) and `IMP-0183`, an unread
blocker summons a review of **the unread blockers**, not of everything around them.

| State | Count | What I did |
|---|---|---|
| `unread`, in scope | 11 ids / 13 lines | Processed here |
| `unread`, deferred | **36** | Not read. They belong to the batch review — the batch trigger is already firing at 47 |
| `awaiting-approval` | 0 | Nothing is parked at another review's gate |
| `reviewer-deferred` | 41 | Left alone, per activation step 2. One of them, `IMP-0274`, still names no `revisit_when` |
| `already-fixed` | 0 | — |

**The 36 deferred unread entries include five classes this review touches**, and I am naming them
so the batch review does not have to rediscover the link: `supplied-design-asset-assumed-wcag-compliant`
(`IMP-0385` — cluster D's second instance, which is what would justify the contrast gate),
`approved-document-internally-inconsistent` (`IMP-0374`, `IMP-0376`, `IMP-0379`, `IMP-0380`,
`IMP-0391` — cluster B's document half), `platform-state-divergence` (`IMP-0372`),
`gate-cannot-fail` (`IMP-0390`), and `requirement-names-data-the-solution-cannot-supply`
(cluster C's class-rename question). **The `gate-cannot-fail` altitude call that cluster C's
residual raises is deferred to the batch review, and this paragraph is where it is recorded.**

**`IMP-0347` still raises a citation-stamp warning** — unread, cited by review 30, carrying no
`reviewed_in`. Review 30 explains why it left the warning standing, and stamping it now would claim
*this* review processed it. Left as the honest state; it is a warning, not an error.

**Three things this dispatch found and cannot fix:**

1. **`verify-derived-counts.py` is red (SOFT) on three delivery-prose counts** — 67 against 68 twice
   in the dev summary, 51 against 52 in `REV Trustee.xml`. All three are `rev_ethnicgroup`'s
   consequence. They are `development-agent`'s files and one token each. **This is why `IMP-0363`
   is not closed** — its author fixed the test counts and not these.
2. **`verify-review-document.py` is red on four items in three of `improvement-agent`'s own past
   documents.** Mine to fix; §7 decision 3 asks when.
3. **The live DEV flow and solution source disagree**, on `IMP-0392`'s own account. I have no live
   environment reach to confirm it, so it is recorded as that entry's claim, not as a fact I
   verified. Either way, source is wrong and an import reverts DEV.

**Two commercial consequences belonging to other agents.** `IMP-0363` records `rev_ethnicgroup` as
unquoted scope resolving SDD OQ-027 and routes itself to `commercial-agent` for a change-order
decision — that routing is correct and I am not pricing it
([C-COM-002](../../constraints/commercial/commercial-constraints.md#L35)). `IMP-0377`'s ADR work is
warranty rework on `wbs:6.9`, not new scope.

**Two findings I would append at application, not now.** The log's id space is the exact thing under
repair, and adding a third live session's allocation into a duplicate-id incident is how `IMP-0312`
happened. Both are recorded here so they cannot be lost:

- **`two-invocation-paths-disagree`:** `theme.test.ts` **fails** with
  `SyntaxError: 'tabster' does not provide an export named 'createTabster'` when vitest is invoked
  as `npm --prefix <app> exec -- vitest run <path>` from the repo root, and **passes 26/26** via
  `npm --prefix <app> run test -- <path>`. The app's `vitest.config.ts` is not picked up on the
  first path. This is `IMP-0026`'s lesson — verify through the path CI actually uses — in a new
  place, and it cost me one wrong reading of a reobservation.
- **`hand-maintained-count-drifts-from-source`:** item 1 above, as the fourth instance since review
  30's change 13.

---

## 6. Verification executed for this review

Everything in §1 and §2 was **run**, not read. Per
[`C-TECH-053`](../../constraints/technology/technology-constraints.md#L108) the level reached is
stated per item.

| What | Command | Result | Level |
|---|---|---|---|
| The blocker's root cause | read [`generate-known-failure-modes.py` L244](../../scripts/generate-known-failure-modes.py#L244) | `json.loads` with no schema call — confirmed | V1 |
| Change 1, current tree | structural subset over 390 entries | 11 findings, **11 true, 0 false** | V1 |
| Change 1, real corpus | structural subset over 27 historical revisions | **1 firing commit, 1 true, 0 false** (`6158243`) | V1 |
| Change 1, naive design | full `check_schema` over the same 27 | **4 firing, 1 true, 3 false** → redesigned | V1 |
| Log green at HEAD? | `check_schema` over `HEAD:logs/improvement-log.jsonl` | **0 errors at 348 entries** — confirms `IMP-0369`'s claim | V1 |
| Changes 3a/3b scope | generator-vs-validator grep across 12 agent files | 5 name only the generator, 2 name neither | V1 |
| Duplicate-id class size | pattern sweep over all 390 entries | **6 recorded instances** | V1 |
| `IMP-0371` reobservation | `verify-code-app-column-bindings.py` + `generate-trustee-field-catalogue.py --check` | **exit 0**, 11 entries / 2 groups | **V2** |
| `IMP-0352` reobservation | `npm --prefix … run test -- src/theme.test.ts` | **26/26 passed** | **V2** |
| `IMP-0377` ground truth | flow JSON trigger, ADR-030 status, `power.config.json` | `"kind": "PowerApp"` at [L31](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json#L31); ADR-030 `Derived`; `shared_logicflows` **absent** | V1 |
| Redesign reach | grep `rev_roundstatisticsrequest` across the tree | 25 files — app, schema, roles, provisioning. **Zero flow JSON** | V1 |
| Regression, all 13 | each script re-run | 4 red items, all attributable; §1 | V1 |
| Constraint counts | `grep -rh '^| ~~C-'` / `'^| C-'` | 10 retired, 80 live | V1 |

**Nothing here reaches V3 or above, and nothing in this review claims to.** The Code App boot
question and the live-vs-source flow divergence are both V4 facts that need a signed-in human in a
private window; §7 decision 1 names the owner.

---

## 7. What you need to decide

**None of these blocks approving this review.** Decision 1 blocks the *delivery* work the halted
build was for.

1. **`IMP-0377` — who supersedes ADR-030, and does the flow get rebuilt before or after?**
   My recommendation: dispatch `architect-agent` to write the superseding ADR (the redesign is
   already built and observable in 25 files, so the ADR is recording a decision, not making one),
   **then** `development-agent` to bring the flow JSON into line with it and with the live DEV flow.
   Doing the flow first means hand-authoring a trigger shape no approved document names — which is
   exactly what `IMP-0377` was logged to prevent. **This is `wbs:6.9` warranty rework, not new
   scope.**

2. **Do you want the flow-trigger-vs-client cross-check gate?** Cluster B's residual (a). It is
   buildable and it is currently unmeasurable — one app, one flow. My recommendation: **not yet.**
   Revisit once the ADR lands and there is a second flow to measure against, so it can be held to
   the corpus obligation every other gate here was.

3. **Should I fix `improvement-agent`'s four red `verify-review-document.py` items now, or in the
   batch review?** Three cluster-count mismatches and one lost deferral, in documents from 08-21,
   08-22 and 08-25. They are one token each and they are mine. My recommendation: **the batch
   review**, alongside the class-rename question cluster C raises, so the digest's join key is
   rewritten once rather than twice.

---

## 8. Digest impact

**Stated as structural deltas, not as a predicted number** — `IMP-0198` is what happens when a
review predicts 31→26 and measures 31→30. The figure is derived by `--check` at application.

- **Entry count is unchanged at 390** by change 4. Renumbering is not appending.
- **Two double-counted ids resolve.** `IMP-0369` currently renders under *both*
  `gate-reassures-wrongly` (x15) and `untriaged-tool-warning` (x4); `IMP-0368` under both
  `approved-document-internally-inconsistent` (x14) and `code-apps-new-connector-blocks-boot` (x2).
  After change 4 each class names a distinct id. **Counts do not move — the ids become correct.**
  The `Unrouted` overflow list, which today literally reads `IMP-0368, IMP-0368, IMP-0369`, stops
  repeating itself.
- **`code-apps-new-connector-blocks-boot` is truly x3, not x2.** `IMP-0358` recorded that class in
  `class` and `platform-contract-guessed-not-groundtruthed` in `class_instance_of`, and the digest
  keys on the latter. That is `IMP-0330`'s defect in a new place; **change 4 does not fix it**,
  because rewriting a finding's `class_instance_of` changes what the altitude rule sees, and that
  is a judgement for the batch review with all three instances in hand.
- **Three closures** (`IMP-0369`, `IMP-0371`, `IMP-0352`) move from `NEW` to `APPLIED` and keep
  teaching — an `APPLIED` entry still renders.
- **`capability: true` on `IMP-0392`** routes its lesson to `Capabilities`, where its author
  evidently intended it when they typed `capability` into `severity`.

---

## 9. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-28-improvement-review.md

Findings processed: 11 NEW (unread, 13 log lines)  →  4 clusters
Regression check:   13 prior changes audited, 3 classes recurred
Proposed:           0 constraints (cap 3), 2 gates/scripts, 1 skill/knowledge edits,
                    7 agent-file edits, 0 retirements
Altitude calls:     2 generalised from instance to class, 2 left as notes
Digest:             will regenerate — 390 entries, 3 recurring classes touched

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

**Deferred, and named rather than capped silently:** 36 unread non-blocker entries, 41
reviewer-deferred entries, the class-rename question, and `improvement-agent`'s own four red
review-document items. §5 and §7 carry all four.

---

## 10. Applied

**`APPROVE IMPROVEMENTS` received 2026-08-28. All six changes are on disk; all 13 processed log
lines are dispositioned — 3 `APPLIED`, 10 left `NEW` with an explicit `deferred_reason` and a
`revisit_when`.**

**Re-verification ran first, per activation step 8, and nothing was disproved.** The log was
unchanged at 390 entries with `max(id)` still `IMP-0391`, and **no entry carries `corrects` against
anything this review processed**. Nothing was withheld.

**The one thing this review did NOT achieve is stated first: `verify-improvement-log.py --check`
does not exit 0.** It reports **1 problem**, down from 13, and that problem is the **batch
trigger** — 38 entries still `unread` against a threshold of 10. Clearing it means processing or
deferring the 38, which is the batch review this review's approved scope explicitly excluded and
which `IMP-0183` is the record of doing wrongly. **The halted build is still blocked by
`improvement-log-check`, and a batch review is what unblocks it.**

### What landed

| # | Change | Landed as | Measured at application |
|---|---|---|---|
| 1 | generator validates structurally | [`generate-known-failure-modes.py`](../../scripts/generate-known-failure-modes.py#L60) + `structural_only` on [`check_schema`](../../scripts/verify-improvement-log.py#L703) | **11 findings / 11 true / 0 false** on the broken tree; **1 of 27 commits / 1 true / 0 false** on the history sweep. Validator's own 60 fixtures still green |
| 2 | id allocator | [`allocate-improvement-id.py`](../../scripts/allocate-improvement-id.py#L1) | `--selftest` **11 fixtures OK**, including an **8-way concurrent append producing 0 duplicate ids**. Then used for real: `IMP-0394`–`IMP-0397`, no collision |
| 3 | validator-first, in the skill | [`how-to-log-an-improvement.md` §3](../../skills/how-to-log-an-improvement.md#L242) | N/A — enforced by change 1 |
| 3a/3b | seven agent files | architect, development, plan, pm, test (named generator only); acceptance, commercial (named neither) | **Re-measured: 0 agent files still missing the validator**, from 5 and 2 |
| 3c | entry point | [`CLAUDE.md`](../../CLAUDE.md#L137) Learning Rules rule 2 | N/A |
| 4 | log repair | [`logs/improvement-log.jsonl`](../../logs/improvement-log.jsonl) | **13 problems → 1.** 6 `observable_at` reduced to bare tokens, caveats moved to `cost`; `refusal_context` added to `IMP-0363`; `IMP-0368`→`IMP-0392` with `severity: rework` + `capability: true`; `IMP-0369`→`IMP-0393` |
| 5 | connector boot-risk | [`code-apps.md`](../../knowledge/technology/code-apps.md#L214) — new subsection, **plus a correction marker on the paragraph that still called the synchronous flow route "the correct default"** | N/A — reference material |
| 6 | Fluent ramp contrast | [`code-apps.md`](../../knowledge/technology/code-apps.md#L627) under Accessibility | N/A — reference material |

**Change 5 turned out to be load-bearing rather than decorative.** The section it landed in
recommended the synchronous instant-flow route as "the correct default" for live figures — the
mechanism that has now crashed this app's boot twice. That recommendation is corrected in place, not
appended around.

### Deviations and corrections, per activation step 8's third branch

**No narrowing was needed at application** — change 1's narrowing happened at draft time, against
the measurement, and the approved §3 wording already said "structural". Two corrections and one
error of my own:

1. **`evidence_grep` takes `contains`, not `needle`.** I wrote `needle` on all three closures and
   the gate rejected them — using the word "needle" in the sentence that rejects the key called
   `needle`. Corrected. **Logged as `IMP-0396`**, because the error message's own vocabulary is what
   misled me.
2. **`reobserved` requires five members, not four.** I copied the shape from `IMP-0198` and the
   skill's worked example, both of which predate `result`. Corrected on both closures; same finding.
3. **My §9 gate block's per-type counts disagreed with my own §3 table** — it said "1
   skill/knowledge edits" against three rows (3, 5, 6), and accounted for neither the `CLAUDE.md`
   edit nor the log repair. The reviewer's approval quoted the wrong figure back. The **substance**
   was itemised correctly in §3 and approved "as drafted"; only the summary arithmetic was wrong.
   **Logged as `IMP-0397`** — and it is the same class as this review's own §1 audit, in a document
   that passed `verify-review-document.py` cleanly, because that gate checks the cluster count and
   not the per-type line. Review 30 dropped exactly that check on an implementation defect.

### Findings dispositioned

| Finding | Status | By |
|---|---|---|
| `IMP-0369` (L367) | `APPLIED` | changes 1 + 2 + 3, needle `structural_only=True` |
| `IMP-0371` | `APPLIED` | already resolved on disk by ADR-032; **reobserved V2** — gate exits 0, catalogue validates 11/2 |
| `IMP-0352` | `APPLIED` | change 6; **reobserved V2** — 26/26 contrast assertions pass |
| `IMP-0358` | `NEW`, deferred | change 5 landed the knowledge half; **V4 unobservable from any agent session** |
| `IMP-0365` | `NEW`, deferred | as above — and its own lesson forbids a third binding attempt |
| `IMP-0377` | `NEW`, deferred | **confirmed live**; needs `architect-agent` then `development-agent`, per §7 decision 1 |
| `IMP-0392` (was `IMP-0368` L374) | `NEW`, deferred | change 5 landed its proposed change **in full**; not closed because `observable_at` is V3 and the entry itself says V4 was not performed |
| `IMP-0363` | `NEW`, deferred | schema damage repaired; **not closed** — `verify-derived-counts.py` is red on three prose counts that are this entry's own consequence |
| `IMP-0364`, `IMP-0367`, `IMP-0375`, `IMP-0368` (L366), `IMP-0393` | `NEW`, deferred | schema damage repaired; substance outside the approved scope → batch review |

**`IMP-0366`, `IMP-0385` and `IMP-0347` were deliberately NOT stamped.** They are named in §5 as
deferred but were not processed, and stamping `reviewed_in` would claim otherwise — review 30's
precedent on `IMP-0347`, kept. Their citation warnings stand as the honest state.

**Three of the six blockers stayed open, and that is the point.** Each carries a `deferred_reason`
and a `revisit_when` naming who can make the observation. `C-TECH-053` closes a V3+ finding only on
evidence at its own level, and no agent session here can open a browser as a signed-in trustee. An
honest open entry beats a closed one nobody tested (`IMP-0224`, `IMP-0225`).

### Findings appended by this review

Four, all via change 2's allocator: **`IMP-0394`** (vitest `exec` vs `run` invocation paths
disagree — found while reobserving `IMP-0352`), **`IMP-0395`** (`rev_ethnicgroup` drifted three
registered prose counts; `verify-derived-counts.py` red and unwired), **`IMP-0396`** (the two
closure-field defects above), **`IMP-0397`** (this document's own gate-block arithmetic).

### Queue state after this application

| | Before | After |
|---|---|---|
| `verify-improvement-log.py --check` | **FAILED — 13 problems** | **FAILED — 1 problem** (batch trigger only) |
| Structural errors | **11** | **0** |
| Unread `blocker` trigger | **6 blockers firing** | **0 — cleared** |
| Duplicate ids | **2 pairs** | **0** |
| unread | 47 | **38** — 13 dispositioned out of `unread`, 4 appended |
| `reviewer-deferred` | 41 | **51** |
| Digest | 390 entries, 389 lessons | **394 entries, 393 teaching lessons, 502 lines**, `--check` current |
| Retired / live constraints | 10 / 80 | **10 / 80** — no retirements, as proposed |

**Both pre-existing red gates are unchanged by this work, and neither is mine to fix here:**
`verify-review-document.py` reports the same 3 cluster-count and 1 lost-deferral items in documents
from 08-21/08-22/08-25 (§7 decision 3 — **this document is clean**, and it is the 36th in the
corpus), and `verify-derived-counts.py` reports the same 3 `rev_ethnicgroup` drifts, now recorded as
`IMP-0395`.
