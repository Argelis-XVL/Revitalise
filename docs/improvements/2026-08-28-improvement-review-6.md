# Improvement Review 36 — 2026-08-28

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 10 `unread` → 7 clusters
**Trigger:** one unread `blocker` — [`IMP-0433`](../../logs/improvement-log.jsonl)
([`agents/WORKFLOW.md` L280](../../agents/WORKFLOW.md#L280), *"immediately — do not batch"*) — **and**
the batch trigger at exactly 10 (`C-TECH-061`,
[technology-constraints.md L131](../../constraints/technology/technology-constraints.md#L131)).
**Gate:** `APPROVE IMPROVEMENTS` — ~~nothing in this document is on disk~~ **APPROVED 2026-08-28 by
Xander Lykopoulos and APPLIED IN FULL. §10 carries the record, the four deviations forced at
application, and the three citations in this document that had rotted before the keyword arrived.**
**Scope:** all 10 `unread` entries. The **72** `reviewer-deferred` entries are untouched per
activation step 2 ([improvement-agent.md L103](../../agents/improvement-agent.md#L103)); 0 sit at
`awaiting-approval`, so no entry here needs a keyword sent against another document.
**Numbering:** this follows the review in
[`2026-08-28-improvement-review-5.md`](2026-08-28-improvement-review-5.md), which titles itself
*"Improvement Review 5"* where the sequence 32 → 33 → 34 puts it at 35. Noted, not corrected —
retitling another review's header is not this review's business.
**Concurrency:** a `development-agent` dispatch fixing
[`IMP-0433`](../../logs/improvement-log.jsonl)'s delivery half **landed while this review was being
measured**, and it changed one of the measurements below from 6 findings to 3. §6 carries it.
**WBS:** the review itself is system work, never billable
([`C-COM-002`](../../constraints/commercial/commercial-constraints.md#L35)). Four of the ten
findings carry no `wbs` field and none is invented here. No contracted figure is restated (D-3).

---

## Summary

**Twelve changes, no new rules — the constraint budget is untouched at 0 of 3.** Every cluster
resolved to a script, an instruction, or a knowledge line, because in each case a mechanism already
existed and stopped one step short of the defect.

**The blocker's delivery half is being fixed by another dispatch, and this review does not touch
it.** Three behavioural test blocks for the three untested provisioning scripts now exist at
`DataverseScripts.Tests.ps1` lines 1091, 1192 and 1294 — cited by line number in the draft as
1091/1190/1292 and **already stale by two lines when the keyword arrived**, which is `IMP-0389`'s
rule demonstrating itself inside the document that applies it. What this review adds is the durable
half: a one-second preflight that answers *"does anything name this script at all?"* before a build
spends several minutes discovering the answer.

**Re-verified at application, and one clause of the draft was wrong:** that dispatch also appended
`IMP-0434` and `IMP-0435`, two further blockers about the same scripts. So the tests landed and then
found real defects — the tests working, not the fix being complete.

**Three of this review's own designs measured wrong and were discarded or withheld before reaching
this document, and the numbers are in §6.** One would have found **0** of the 3 defects it was
proposed to catch. One measured **4 findings, 0 true**. The third is a narrowing this review
**withholds** from a HARD gate, because its mechanism is the same phrase-matching instrument that has
now measured false **five** times in this repository — and because the corpus it would relax is green
today.

---

## 1. Regression check — did the last review's changes work?

Three reviews landed on disk today. Each is audited against the four questions.

| Prior change | Review | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| The string-form `proposed_change` fixture in [`verify-improvement-log.py` L1961](../../scripts/verify-improvement-log.py#L1961) | [35](2026-08-28-improvement-review-5.md) | `gate-cannot-fail` | **NO** | **Working.** Re-measured this dispatch: `--selftest` reports **61 fixtures** green and the log validator reaches a verdict over all 430 entries with no traceback |
| [`verify-design-doc-claims.py`](../../scripts/verify-design-doc-claims.py) — the general gate for `approved-document-internally-inconsistent` | [33](2026-08-28-improvement-review-3.md) | `approved-document-internally-inconsistent` | **NO in that class — YES in a new one** | **Working, and it fires on retractions.** All three true positives are corrected and the gate is green (exit 0). But it went RED on the erratum written to satisfy it — that is [`IMP-0428`](../../logs/improvement-log.jsonl), a new instance of `gate-fires-on-nothing` |
| The measured lesson that a prose-proximity gate cannot read a retraction | [34](2026-08-28-improvement-review-4.md) | `gate-reassures-wrongly` | **YES — twice more** | **The lesson was right and reached no instruction.** It was recorded in the log and in the digest, and the section that mandates the measurement never named the asymmetric test. Changes 1 and 2 close that |
| The build-config comment noting `verify-tad-coverage.py` reads `docs/architecture` only ([build.yml L1103](../../config/revitalise-grant-automation-build.yml#L1103)) | [33](2026-08-28-improvement-review-3.md) | `gate-scope-mismatch` | **YES** | **Diagnosed and not fixed.** The comment names the gap; the argparse default at [L873](../../scripts/verify-tad-coverage.py#L873) is unchanged. Change 4 |

The four audit questions, answered:

- **Has any finding in that class appeared since?** Yes, three times. `gate-fires-on-nothing` reached
  x6 within hours of review 33 wiring the gate; `gate-reassures-wrongly` reached x19; `gate-scope-mismatch`
  reached x8.
- **Was the change prose, or a mechanical gate?** Both kinds recurred, and they recurred differently.
  The **gate** recurrence is mis-scoping, not failure — it fired, on the wrong text. The **prose**
  recurrence is the textbook wrong-altitude case: a measured result that lived only in a log entry.
  Escalated to the instruction that governs the measurement (changes 2 and 3).
- **Did the gate run?** Yes, every time, and this was verified by executing each one rather than reading
  it — which is [`IMP-0426`](../../logs/improvement-log.jsonl)'s own rule, applied to its own review.
- **Did the closure evidence match the level the defect was visible at?** For review 35, yes. For this
  review's own closures: seven entries are `n/a` or `V1` and close on an executed check; the one `V2`
  entry is **not closed** — see §5.

---

## 2. Clusters and promotion decisions

```
CLUSTER A: a prose gate cannot tell an assertion from its own RETRACTION
           (x2 here: IMP-0428, IMP-0422 — and the property is at x5 across two days)
Altitude:  CLASS. Four measured attempts were already on record; this review measured a fifth
           (§6c). The property is established, so no sixth attempt should be designed.
Ladder row: "an agent had the information and still did the wrong thing" -> an agent/skill edit,
           plus "prefer the most mechanical home available" for the authoring half.
Becomes:   (1) verify-design-doc-claims.py's two FINDING MESSAGES carry the two retraction-safe
               authoring forms, so the author is told at the moment the gate fires rather than
               having to remember a convention. This is the most mechanical home a rule that
               cannot be a gate can have.
           (2) agents/improvement-agent.md's "run it against the REAL CORPUS" section names the
               asymmetric test it did not name: measure a prose gate against the CORRECTED file,
               not only the defective one.
Retires:   nothing — see §4.
WITHHELD:  the retraction NARROWING IMP-0428 proposes. Reasons, in order: its mechanism is a
           phrase list, which is the instrument that has measured 48%-100% false five times;
           it would put a phrase-triggered escape hatch into a HARD gate, so any author could
           clear a genuine finding by writing "erratum" near it; and the corpus is green today,
           so nothing is currently blocked. The cost of withholding is that an erratum author
           must state the correction source-first — which change 1 tells them how to do.
Cites:     IMP-0428, IMP-0422
Residual:  The gate stays retraction-BLIND. A future erratum that names a column within 40
           characters before an absence phrase will go red on correct prose, and the only
           remedy is the authoring form. Stated, not solved.
```

```
CLUSTER B: a gate's input SET is narrower than its subject  (x2: IMP-0425, IMP-0430)
Altitude:  CLASS for the scope half (gate-scope-mismatch is at x8); INSTANCE-DISCARDED for one
           of the two proposed extensions, on measurement.
Ladder row: "a tool could catch it mechanically."
Becomes:   (3) verify-tad-coverage.py's --design-docs accepts SEVERAL paths and defaults to
               docs/architecture AND docs/plans. Measured first: 0 findings and 0 claims over
               docs/plans (§6b) — a real scope repair with no measured effect today, which is
               said plainly rather than dressed as a coverage win.
           (4) scripts/verify-doc-line-links.py — an identifier-labelled line-link must land in
               the section that identifier names. Measured over the design-document corpus:
               6 identifier links -> 5 findings, 5 TRUE, 0 false (§6a).
DISCARDED: IMP-0430's proposal (a), extending the absence check to source comments. Measured:
           37 absence-phrase lines under src/, 6 naming a rev_* token, and **0 of the 3 known
           survivors reachable** — they name the TypeScript property, not the column. §6d.
Cites:     IMP-0425, IMP-0430
Residual:  56 further dangling links live in docs/development, docs/tests and docs/improvements
           — approved deliverables and historical review documents nobody is authorised to edit.
           The gate is deliberately NOT pointed at them, because a gate that opens red on work no
           dispatch owns teaches people to route around it. Named, not silently skipped.
           And the PARAPHRASE half of IMP-0430 stays uncovered: "the ethnic-group figure has no
           source data at all" names no column and no gate can read it.
```

```
CLUSTER C: a finding's stated root cause is an assertion about BEHAVIOUR, settled only by
           executing it  (x1 here: IMP-0426 — class finding-diagnosis-unverified at x10)
Altitude:  CLASS. Activation step 8 already requires re-reading any file a proposal ASSERTS
           something about; re-reading is exactly what produced both wrong answers.
Ladder row: "an agent had the information and still did the wrong thing."
Becomes:   (5) agents/improvement-agent.md activation step 8 gains one clause: where the
               assertion is about a script's BEHAVIOUR, EXECUTE the script or the function.
Cites:     IMP-0426
Residual:  It cannot be mechanised — nothing can tell a finding's prose "I ran it" from "I read
           it". This review applied the clause to itself, which is how §6b and §6d were caught.
```

```
CLUSTER D: `corrects` is single-valued, so one disproved cause can be marked once  (IMP-0420)
Altitude:  INSTANCE, and the blocking reason has expired. The finding deliberately proposed no
           edit because both reader scripts were owned by a live dispatch; reviews 33 and 34 are
           now applied, so the files are free.
Ladder row: "a tool could catch it mechanically."
Becomes:   (6)(7) both readers accept `corrects` as a string OR a list, plus (8) the schema note
               in skills/how-to-log-an-improvement.md, which currently says "One id, as a string".
Cites:     IMP-0420
Residual:  Neither reader validates the field's TYPE today, so a list is coerced by str(), fails
           to resolve, and is SILENTLY dropped by the generator. The change fixes the capability;
           the type check that makes a malformed value loud is part of the same edit.
```

```
CLUSTER E: a stale verbatim source QUOTATION cited as evidence  (IMP-0429 — class x3)
Altitude:  CLASS. Third instance after IMP-0305 and IMP-0341, so the ladder forbids another
           instance patch.
Ladder row: "a platform law, or a third instance" -> normally a constraint row. NOT taken: the
           Verify By would not be mechanically executable today (see Residual), and an
           unverifiable constraint is a comment. It goes one rung up as a skill rule instead.
Becomes:   (9) skills/how-to-verify-a-platform-contract.md §4 — a document quoting source
               verbatim as evidence names the FILE and the SYMBOL beside the quote, and any pass
               revising the surrounding claim re-greps the quoted string against that file.
DEVIATION: IMP-0429 asks for `file:line`. That is NARROWED to file-plus-symbol, because
           IMP-0389 established four days ago that a line citation across a document boundary
           cannot be maintained by either side of it — the pass that writes the pointer never
           edits the target. The INTENT (a quotation must be re-checkable) survives; the literal
           wording measured wrong against a rule already on disk. Recorded here, in the entry's
           applied_by, and in the gate output, per activation step 8's third branch.
Cites:     IMP-0429, IMP-0305, IMP-0341
Residual:  No gate. Nothing in the repository marks WHICH quoted strings are source quotations,
           so there is no set to check. The convention has to exist before a gate can read it;
           a mechanical version is the plausible FOURTH-instance change and is named here so the
           next review does not re-derive it.
```

```
CLUSTER F: the blocker — a coverage obligation discharged by a suite naming none of the scripts
           (IMP-0433 — class no-assertion-on-shipped-content at x16)
Altitude:  CLASS, and the instance is already fixed by someone else. IMP-0246 recorded this exact
           discrimination for this exact test container, so this is at least the second instance
           and the altitude rule forbids an instance patch.
Ladder row: "a tool could catch it mechanically" — but only in the form that asserts on VALUES.
Becomes:   (10) scripts/verify-provisioning-test-presence.py — every .ps1 in the DECLARED coverage
               scope is named by some *.Tests.ps1 or carries a coverage exclusion. Measured:
               27 scripts -> 3 findings, 3 TRUE, 0 false (§6e).
           (11) knowledge/technology/coding-standards.md — the line IMP-0433 asks for, beside the
               Test Coverage row that declares the scope.
DISCARDED: the obvious design — read the document's coverage CLAIM and check the suite it cites.
           Measured: 8 candidate lines -> 4 findings, 0 true, 4 false. §6c.
NOT CLOSED: IMP-0433 is observable_at V2 and no build has run. See §5.
Cites:     IMP-0433, IMP-0246, IMP-0244
Residual:  THE IMPORTANT ONE. Being NAMED by a test file is NOT behavioural coverage — a script
           can be named inside a convention loop that executes none of it, which is IMP-0433's own
           defect. verify-coverage-threshold.py (C-TECH-014, HARD) stays the instrument that
           measures lines. This gate answers only the cheaper, earlier question, and its own output
           says so, because a check that reassures beyond its evidence is the class it is filed under.
```

```
CLUSTER G: two findings that are questions, not defects  (IMP-0421, IMP-0432)
Altitude:  NEITHER. IMP-0421 proposes no change ON PURPOSE and puts a question to the reviewer;
           IMP-0432 is a single instance whose own proposal says to wait for a second.
Becomes:   nothing. Both deferred with a reason and a trigger — §5, and the decision is in §7.
Cites:     IMP-0421, IMP-0432
```

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? |
|---|---|---|---|---|---|
| 1 | script | [`scripts/verify-design-doc-claims.py`](../../scripts/verify-design-doc-claims.py) | Append the two retraction-safe authoring forms to the finding messages at [L152](../../scripts/verify-design-doc-claims.py#L152) (check a) and [L228](../../scripts/verify-design-doc-claims.py#L228) (check b): state a correction **source-first** so no column name sits within 40 characters before an absence phrase, and keep a retracted FIGURE out of any markdown table row. Add one selftest fixture asserting the guidance text is present in the emitted finding | IMP-0428, IMP-0422 | YES — `python3 scripts/verify-design-doc-claims.py --selftest` (20 checks, up from 19) and `… docs/architecture docs/plans` still exits 0 |
| 2 | agent | [`agents/improvement-agent.md`](../../agents/improvement-agent.md#L367) | In *"run it against the REAL CORPUS before you wire it"*, one sentence: where a gate reads PROSE, measure it against the **corrected** version of the file as well as the defective one — a correction quotes what it withdraws, so a phrase-presence check scores the fix worse than the bug | IMP-0422, IMP-0428 | N/A — instruction change |
| 3 | agent | [`agents/improvement-agent.md`](../../agents/improvement-agent.md#L127) | Activation step 8, one clause: where a proposal's assertion is about a script's **behaviour** (*"X is not a step"*, *"X does not check Y"*), **execute** the script or the function — re-reading its source is what produced both wrong answers | IMP-0426 | N/A — instruction change |
| 4 | script | [`scripts/verify-tad-coverage.py`](../../scripts/verify-tad-coverage.py#L873) | `--design-docs` accepts several paths (`nargs="+"`) and defaults to `docs/architecture` **and** `docs/plans` | IMP-0425 | YES — `python3 scripts/verify-tad-coverage.py` reports 7 design documents, not 4, and exits 0 |
| 5 | script | `scripts/verify-doc-line-links.py` (**new**) + the `doc-line-links` step in [build.yml](../../config/revitalise-grant-automation-build.yml#L1121) beside `design-doc-claims` | An identifier-labelled `path#Lnnn` link must land on a line, or inside a section heading, carrying that identifier. Two narrowings, each removing named false positives | IMP-0430 | YES — `--selftest`, then the corpus run: 5 findings, all true (§6a) |
| 6 | script | `scripts/verify-provisioning-test-presence.py` (**new**) + a preflight step in [build.yml](../../config/revitalise-grant-automation-build.yml) | Every `.ps1` in the coverage scope **derived from** [coding-standards.md L152](../../knowledge/technology/coding-standards.md#L152) is named by some `*.Tests.ps1` or carries a `config/coverage-exclusions.json` entry. Gitignored paths excluded (IMP-0410) | IMP-0433, IMP-0246 | YES — `--selftest` (4 checks) then the corpus run: 3 findings, all true (§6e) |
| 7 | knowledge | [`knowledge/technology/coding-standards.md`](../../knowledge/technology/coding-standards.md#L152) | Beside the coverage-scope row: `DataverseScripts.Tests.ps1`'s generic container is a **convention** check and never discharges a specific new script's coverage obligation — grep `src/tests/` for the script's own filename, and read the per-file `coverage.xml` counters | IMP-0433, IMP-0246 | YES — the new gate in row 6 is the executable form of this sentence |
| 8 | script | [`scripts/verify-improvement-log.py`](../../scripts/verify-improvement-log.py#L1466) | `corrects` accepts a **string or a list of ids**; a value that is neither is reported by id rather than coerced. One new selftest fixture for the list form | IMP-0420 | YES — `--selftest` (62 fixtures) and `--check` exits 0 |
| 9 | script | [`scripts/generate-known-failure-modes.py`](../../scripts/generate-known-failure-modes.py#L411) | Same, in `corrected_by()` — iterate the list instead of coercing it, so a multi-target correction reaches every entry's lesson on the read path | IMP-0420 | YES — `--check` reports the digest current, and IMP-0010's lesson carries the CORRECTED marker |
| 10 | skill | [`skills/how-to-log-an-improvement.md`](../../skills/how-to-log-an-improvement.md#L128) | Record the list form of `corrects`, and the rule the schema change does not remove: a cause confirmed in N findings needs marking in all N, so grep for the others and say in `what` which you could not mark | IMP-0420 | YES — rows 8 and 9 are the executable half |
| 11 | skill | [`skills/how-to-verify-a-platform-contract.md`](../../skills/how-to-verify-a-platform-contract.md#L281) | §4: a document quoting source verbatim as evidence names the **file and the symbol** beside the quote, and any pass revising the surrounding claim re-greps the quoted string against that file. A quotation that no longer matches is a finding, not something to reflow | IMP-0429, IMP-0305, IMP-0341 | NO — and it is a skill line, not a constraint, for exactly that reason (see cluster E) |
| 12 | agent | [`agents/improvement-agent.md`](../../agents/improvement-agent.md#L332) | The `verify-*.py` count moves 48 → 50, forced by rows 5 and 6. Registered as `improvement-agent-verify-script-count` | IMP-0395 | YES — `ls scripts/verify-*.py \| wc -l` and `python3 scripts/verify-derived-counts.py` |

**Constraint budget: 0 of 3 used.** No cluster produced a rule that needed one. Cluster E is the
only candidate the ladder pointed at a constraint row, and it was declined because its `Verify By`
is not mechanically executable today — which the anti-bloat limits treat as a comment, not a
constraint.

---

## 4. Retirements

> Retirement check performed: **80 live constraint rows** reviewed (`grep -rh '^| C-' constraints/
> --include='*.md' | wc -l`), against **10 already retired**. None is currently redundant, and the
> check was mechanical rather than impressionistic: every live row whose `Verify By` names a
> `scripts/*.py` was tested for that script's existence, and **0 rows name a script that does not
> exist**. Nothing in this review supersedes an existing rule — the two new gates cover ground no
> constraint claimed, and `C-TECH-014` is strengthened by row 6 rather than replaced by it.

---

## 5. Findings left unprocessed

No silent caps.

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| [IMP-0421](../../logs/improvement-log.jsonl) | `learning-substrate-destroyed` | **It proposes no change on purpose.** Stamping `reviewed_in` at draft time would change when *every* future review first writes to the shared append-only log, and two live sessions on this synced path is `IMP-0080`'s hazard — which this dispatch met again (§6f). It is a reviewer decision, put in §7 | the reviewer answers the question in §7 |
| [IMP-0432](../../logs/improvement-log.jsonl) | `gate-scope-mismatch` | One instance, and the finding's own proposal says a single instance with a general mechanism is a knowledge line — which the lesson already is, on the digest's read path. Requiring a UTC offset on `ts` is forward-binding on every future entry and no second instance justifies it yet | *(applied verbatim from the entry)* the next V2-or-higher closure whose `reobserved.ts` is refused, or any new gate that compares two entries' timestamps |
| [IMP-0433](../../logs/improvement-log.jsonl) | `no-assertion-on-shipped-content` | **Processed but NOT CLOSED.** Rows 6, 7 and 10 cite it and its delivery half is fixed by the concurrent dispatch — but `observable_at` is **V2** and the reproduction is a build reaching the coverage-threshold step. No build has run. Closing it on a document saying it was fixed is `IMP-0208`'s defect exactly, and `verify-improvement-log.py` refuses the closure without a `reobserved` record. It gets a `deferred_reason` so it stops re-firing the blocker trigger without a false closure | the next build reaching `coverage-threshold`, which re-observes line coverage against the 80% threshold with the three new test blocks in place. Named owner: `build-agent` |

Seven entries close `APPLIED`: `IMP-0420`, `IMP-0422`, `IMP-0425`, `IMP-0426`, `IMP-0428`,
`IMP-0429`, `IMP-0430`. All are `observable_at` `n/a` or `V1`, and each `V1` closure is on a check
this dispatch **executed**, not read.

**Five new findings will be appended at application time**, with ids allocated from `max()` across
the whole log immediately before writing (`IMP-0080`). They are the measurements in §6b, §6c, §6d,
§6f and §6g — a finding's own diagnosis contradicted by measurement is precisely what the log is
for, and appending them now would re-fire the batch trigger against a review that is still a
proposal.

---

## 6. What was measured, and what the measurements changed

### (a) The dangling-link gate: 6 identifier links → 5 findings, 5 true, 0 false

Raw, over the whole of `docs/`: **1039 line-links, 599 identifier-labelled, 272 findings.** That
first number was a false-positive factory, and two narrowings fixed it, each removing named cases:

- **Path resolution.** 170 of the 272 were *"target file does not exist"* — links written
  repo-root-relative from inside a subdirectory. Resolving against both bases removed all 170. This
  was **my** defect, not the corpus's.
- **Narrowing 1 — the label must be a structured identifier.** `[line 142]`, `[line 9]`,
  `[Revision 5]` are labels that say what they are and claim no section; a bare integer is not an
  identifier. 102 → 58.
- **Narrowing 2 — section scope, not a ±3-line window.** A link may deep-link *into* the body of
  the section it names. This removes
  [`plan.md:348`](../../docs/plans/revitalise-grant-automation-plan.md#L348) `[Architecture §3.1]`
  → `#L317` **by name**: §3.1's heading is at L286 and L317 is a table row inside it, so the reader
  lands in the right place.

Scoped to the design-document corpus `design-doc-claims` already governs: **6 identifier links, 5
dangling, 5 true, 0 false.** Adjudicated one at a time — §3.4 is at L1124 and the links point at
L363; `A-R24` appears at L140/L288/L292 and the links point at L924; and `[§7.1]` points 800 lines
away from the §7.1 heading at L1533. Four of the five are the pair
[`IMP-0430`](../../logs/improvement-log.jsonl) names.

Over the whole tree it is **61**, of which 56 sit in approved deliverables and historical review
documents. That is why the gate is scoped and not pointed at everything.

### (b) Extending `tad-coverage` to `docs/plans`: 0 findings AND 0 claims

Executed, not reasoned about: `verify-tad-coverage.py --design-docs docs/plans` reports **0
deliverable-now items in 0 claims across 3 design documents**, and exits 0.
[`IMP-0425`](../../logs/improvement-log.jsonl)'s premise — that a plan document carries the table
two findings are about — is **true of the document and false of the check**: check (c)'s subject is a
bolded *"deliverable now / ships now"* list, and `docs/plans` contains none. The scope repair is
still correct and still one line; it is reported as a zero-effect repair rather than as a coverage
win. This is a `finding-diagnosis-unverified` instance and will be logged.

### (c) The prose form of the blocker's gate: 4 findings, 0 true, 4 false

The obvious design reads a document's coverage claim and checks the suite it cites. Built and run
over `docs/development`, `docs/tests` and `docs/deployments`: **8 candidate lines → 4 findings, 0
true, 4 false.** Every one is co-occurrence, not a claim — a sentence about which suite two scripts
*rely on*; a test-count row naming the runner and two suites (twice); and a constraint row naming
both. Extracting *"this suite discharges that script's obligation"* needs intent.

**This is the fifth measured instance of the same shape**, after review 33's one and review 34's
three. [`IMP-0422`](../../logs/improvement-log.jsonl) asked that a fifth attempt read its entry
first; it was read, the candidate was measured anyway because measuring is the cheap part, and the
measurement agreed. Discarded — and change 2 is what stops a sixth.

### (d) Extending the absence check to source comments: 0 of 3 targets reachable

[`IMP-0430`](../../logs/improvement-log.jsonl)'s proposal (a) is to run check (a) over source
comments where a `rev_*` column is named literally. Measured over `src/`: **37 absence-phrase lines,
6 naming a `rev_*` token — and none of the 3 survivors the proposal exists to catch.**
[`RoundStatistics.tsx:25`](../../src/code-apps/trustee-review-portal/src/components/RoundStatistics.tsx#L25)
names `ethnicGroupDistribution`, a TypeScript property; the other two say *"the field"* and *"the
ethnic-group figure"*. The 6 that do match are false: a privilege name inside a quoted error
message, two *"no column secured"* statements, and an **environment-scoped** claim
(`rev_roundstatisticsresult` *"does not exist in REV-GrantApplications-DEV yet"*) that is true of the
environment and would be judged against source. Discarded. The finding's cost figure and its lesson
stand; its proposed mechanism does not.

### (e) The value-asserting form of the blocker's gate: 3 findings, 3 true, 0 false

27 scripts in the declared coverage scope → **3 findings, all true**:
`ensure-document-locations.ps1`, `verify-access-test-identity.ps1`, `verify-environment-access.ps1`.
The second is `IMP-0246`'s script — 285 lines that could never run — so the gate surfaces the exact
file whose untested state is already on the record. The `--selftest` proves all four guards fire,
including that a missing scope declaration **aborts** rather than passing over nothing (`IMP-0007`).

### (f) The tree moved under the measurement, mid-review

The first run of (e) returned **6** findings, including all three `seed-round-statistics-*.ps1`
scripts. The re-run returned **3**: between them, the concurrent `development-agent` dispatch landed
[`DataverseScripts.Tests.ps1`](../../src/tests/provisioning/DataverseScripts.Tests.ps1#L1091)'s three
behavioural `Describe` blocks. Two things follow. The gate tracks reality rather than a snapshot —
that is the strongest single piece of evidence it fails on the right things. And activation step 8's
hazard is not hypothetical: a proposal measured at the start of this dispatch would have been wrong
by the end of it. This will be logged.

### (g) Three hand-maintained counts have drifted from source — SOFT, and not this review's

`verify-derived-counts.py` is a **SOFT** step, so its findings are reported and do not block. Run
this dispatch, it reports **3 drifted claims**, all pre-existing and all one off:

| Where | Prose says | Source says |
|---|---|---|
| [`revitalise-grant-automation-dev-summary.md:4611`](../development/revitalise-grant-automation-dev-summary.md#L4611) | 67 (*"(67, not 68 or more)"*) | 68 |
| [`revitalise-grant-automation-dev-summary.md:4768`](../development/revitalise-grant-automation-dev-summary.md#L4768) | 67 (*"source is **67** today"*) | 68 |
| [`REV Trustee.xml:73`](../../src/solutions/RevitaliseGrantAutomation/Roles/REV%20Trustee/REV%20Trustee.xml#L73) | 51 (*"51 secured columns"*) | 52 |

Class `hand-maintained-count-drifts-from-source`, at x21. **Not fixed here** — both targets are
delivery-owned artefacts (a Dev Summary and a solution role file), and editing them is not
improvement-agent's to do (`C-COM-002`). It is recorded rather than swallowed, because a SOFT
finding nobody reads is `IMP-0395`'s defect: that step's findings drifted twice before anyone read
the report. Owner: whoever next touches secured columns on `REV Trustee` — a schema addition landed
the 52nd and the two prose figures were not moved with it.

---

## 7. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 430 | 441 (5 appended by this review; the rest by concurrent dispatches) |
| Distinct lessons | 429 | 440 |
| Recurring classes (x≥2) | 37 | 37 — measured, not predicted |
| Digest lines | 573 | 573 |

The recurring-class figure was deliberately not predicted. A review once predicted a digest delta of
31→26 and measured 31→30, because a lesson renders where its `capability` flag sends it and not where
its class suggests (`IMP-0198`). **Measured after regeneration: 37 recurring classes, unchanged, and
573 digest lines, also unchanged** — the five new lessons all joined classes already recurring and
all landed inside sections already at their display cap, so the digest grew by 11 entries and not by
one visible line. That is worth stating plainly, because "the digest is current" and "the digest
shows the new lessons" are different claims: four of the five are reachable only via
`--subject`, or in the log.

Regenerated with `python3 scripts/generate-known-failure-modes.py`; confirmed current with `--check`
(441 entries). The `§9` gate block below keeps the figures the reviewer approved rather than the
measured ones, so the approval record stays intact.

---

## 8. What you need to decide

**Should a review stamp `reviewed_in` on an entry when the DRAFT names it, rather than when the
keyword arrives?**

Today it does not, so between drafting and approval every entry a review has analysed still reads
`unread`. The queue gate then reports *"nothing records that anyone has looked at these"* about work
under active analysis, and re-fires the batch trigger at it. That has already cost two duplicated
strategic-tier passes over settled work.

The argument for stamping at draft time is that `reviewed_in` records only that a review **read** the
entry, which becomes true the moment the draft names it — so it violates neither *"never apply a
change before the keyword"* nor *"unread means nobody has opened it"*.

The argument against is that it makes every future review write to a shared append-only log earlier,
and two live sessions on this synced SharePoint path is a hazard this repository has met repeatedly —
including inside this dispatch, at §6f.

It would **not** clear a blocker trigger either way: the validator counts `awaiting-approval`
alongside `unread` for blockers, deliberately.

**Recommendation: leave it as it is for now.** The cost is a noisy trigger the activation procedure
already teaches agents to read correctly; the change alters the write behaviour of every future
review to fix a reporting artefact. I would rather take it as a deliberate capability change with its
own design note than as a side effect of this review.

---

## 9. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-28-improvement-review-6.md

Findings processed: 10 NEW  →  7 clusters
Regression check:   4 prior changes audited, 3 classes recurred
Proposed:           0 constraints (cap 3), 6 gates/scripts, 3 skill/knowledge edits,
                    3 agent-file edits, 0 retirements
Altitude calls:     4 generalised from instance to class, 2 left as notes
Digest:             will regenerate — 434 lessons, recurring classes measured at application

Withheld:           1 — IMP-0428's retraction narrowing (phrase-list mechanism, 5th measured
                    instance of the shape; would add an escape hatch to a HARD gate)
Discarded:          2 — IMP-0430(a) source-comment corpus (0 of 3 targets reachable);
                    IMP-0433's prose-claim gate (4 findings, 0 true)
Deviation:          1 — cluster E narrowed from `file:line` to file-plus-symbol, compelled by
                    IMP-0389's measured result on cross-boundary line citations
Not closed:         1 — IMP-0433 stays open with a deferred_reason: observable_at V2, no build
                    has run, and its delivery fix is another dispatch's

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 10. Applied

**All 12 changes are on disk, all 10 in-scope findings are dispositioned (7 `APPLIED`, 3 deferred
with a reason and a trigger), 5 new findings are appended, and the digest is regenerated.** Applied
incrementally — each entry closed as its change landed, the digest regenerated once at the end
(`IMP-0301`).

| # | Change | Verified by | Entries closed |
|---|---|---|---|
| 1 | Retraction-safe authoring guidance in `verify-design-doc-claims.py`'s two finding messages, + 3 selftest fixtures | `--selftest` **22 checks** (up from 19); corpus exits 0 | IMP-0428, IMP-0422 |
| 2 | `agents/improvement-agent.md` — measure a prose gate against the CORRECTED file; assert on values, not phrases | grep | IMP-0422 |
| 3 | `agents/improvement-agent.md` step 8 — EXECUTE a behavioural assertion | grep | IMP-0426 |
| 4 | `verify-tad-coverage.py` `--design-docs` → `nargs="+"`, defaults to both directories | default run reads **7** design documents (up from 4), exits 0 | IMP-0425 |
| 5 | `scripts/verify-doc-line-links.py` + the `doc-line-links` build step | `--selftest` **9 checks**; corpus **5 findings, 5 true** | IMP-0430 |
| 6 | `scripts/verify-provisioning-test-presence.py` + the `provisioning-test-presence` preflight | `--selftest` **4 checks**; corpus **3 findings, 3 true** | — (see below) |
| 7 | `knowledge/technology/coding-standards.md` — a convention suite is not coverage | scope still parses; gate reports 27 scripts | — |
| 8 | `verify-improvement-log.py` — `corrects` accepts a list; schema type-guard; 3 fixtures | `--selftest` **64 fixtures** (up from 61) | IMP-0420 |
| 9 | `generate-known-failure-modes.py` — `corrected_by()` iterates instead of coercing | `IMP-0010`'s lesson now carries the CORRECTED marker | IMP-0420 |
| 10 | `skills/how-to-log-an-improvement.md` — the list form + mark every carrier | grep | IMP-0420 |
| 11 | `skills/how-to-verify-a-platform-contract.md` — a quotation of source is a snapshot | grep | IMP-0429 |
| 12 | `agents/improvement-agent.md` — verify-script count 48 → 50 | `verify-derived-counts.py` no longer reports this claim | — |

### The four deviations forced at application

1. **Change 1 shipped 3 selftest fixtures, not 1** — 22 checks rather than the "20, up from 19" §3
   predicted. Asserting the guidance reaches the author needs one fixture per message plus one for
   the withheld escape hatch.
2. **Change 11 narrowed from `file:line` to file-plus-symbol**, as §2 cluster E specified, because
   `IMP-0389` had already measured cross-boundary line citations as unmaintainable. Recorded in the
   entry's `applied_by`, in cluster E, and in the gate output.
3. **Two of change 5's own selftest fixtures encoded my expectation, not the gate's behaviour** —
   they asserted a finding where narrowing 2 correctly produced none. Caught by running them, which
   is change 2's rule applying to change 5 in the same sitting. Fixture document restructured with
   two sections so the "right section" and "wrong section" cases are actually distinguishable.
4. **My first two `reobserved` records were incomplete** (missing `level` and `rerun`) and the
   validator refused them. Fixed before proceeding — and the lesson is that the validator must run
   after *each* closure, not after the batch.

### What approving this did NOT do

**It did not turn the build green.** `verify-improvement-log.py --check` still exits 1 on two
triggers, and neither is this review's: three unread blockers (`IMP-0434`, `IMP-0435`, `IMP-0439`)
and 11 entries awaiting closure. Six of those are other dispatches' findings — `2026-08-28-improvement-review-7.md`
is processing four of them — and five are this review's own, which is inherent: a review's findings
enter the queue it just drained.

**Two new HARD steps are RED by design**, each on true positives with a named owner, following the
`design-doc-claims` precedent already in the build config:

- `doc-line-links` — 5 dangling links in `docs/plans/revitalise-grant-automation-plan.md`. Owner:
  `plan-agent`, with `architect-agent` for the target sections.
- `provisioning-test-presence` — 3 scripts named by no test. Owner: `development-agent`.

Both step comments say *"That is the finding, not a gate defect. Do not delete the step."*

**And `IMP-0433` is deliberately still open**, with a `deferred_reason` and a trigger naming
`build-agent`: it is `observable_at` V2, the reproduction is a build reaching `coverage-threshold`,
and no build has run.

**Verification after application:** `python3 scripts/verify-improvement-log.py` (bare) exits **0** —
441 entries, schema clean. `--selftest` **64 fixtures**. `generate-known-failure-modes.py --check`
reports the digest **current** (441 entries, 440 distinct lessons, 573 lines, 37 recurring classes).
`verify-build-config.py` passes: **66 steps, 51 gates**, negative-test coverage OK.
`verify-review-document.py` passes on this document. `verify-derived-counts.py` reports **3** drifted
claims, all pre-existing and delivery-owned (§6g), none of them this review's.
**Not verified:** nothing was committed, and no build or Pester run was executed against the changed
gates.
