# Improvement Review — 2026-09-07 (6)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 1 `NEW` → 1 cluster
**Trigger:** blocker escalation — [IMP-0658](../../logs/improvement-log.jsonl#L655), `blocker`/`unread`, halting the [`no-hardcoded-environment-values`](../../config/revitalise-grant-automation-build.yml#L423) step and now the [`improvement-log-check`](../../config/revitalise-grant-automation-build.yml#L62) step
**WBS:** 3.2, 3.4
**Gate:** `APPROVE IMPROVEMENTS`

---

## 0. The one thing to read first

**The source defect is already fixed and verified; what still blocks the build is the finding's own queue entry, and only the keyword moves it.** I simulated both states against a scratch copy of the log: with the entry merely stamped as reviewed, [`verify-improvement-log.py`](../../scripts/verify-improvement-log.py) still exits **1** — the blocker rung fires on `awaiting-approval` exactly as it does on `unread`. With the entry `APPLIED`, it exits **0**.

**But the change this review proposes is not the one the finding asked for.** [IMP-0658](../../logs/improvement-log.jsonl#L655) proposed a line in a knowledge file teaching authors not to put an environment URL in solution source. That exact lesson was already learned, and recorded, on 2026-08-20 by [IMP-0119](../../logs/improvement-log.jsonl#L116) — *"Do not put an example URL in ANY file under `src/solutions/` … not in a comment"* — which proposed no rule change at all and let the digest carry it. Eighteen days later the identical mistake arrived from a different direction and cost a blocker instead of friction. Repeating the sentence louder is the one response the record already disproves.

**The mechanical gap underneath it is real, and I found it by execution.** The gate that halted the build is a one-second grep over solution source that needs no packaging, no authentication and no environment — yet it runs at build step 46 of 73, and it is **not** in the set that [`run-source-gates.py`](../../scripts/run-source-gates.py) runs before handoff. The authoring dispatch ran its mandatory pre-handoff commands, got 13 of 13 green, and handed off source that a 0.03-second grep would have rejected.

---

## 1. Regression check — did the last reviews' changes work?

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| [IMP-0119](../../logs/improvement-log.jsonl#L116)'s disposition — `proposed_change: none`, lesson left to the digest | 2026-08-21 | an environment URL written into solution source | **YES — [IMP-0658](../../logs/improvement-log.jsonl#L655)**, 18 days later | **The central finding of this review.** A digest-only disposition did not hold. Not disobedience: the digest carries it as a single-member class at [line 614](../../logs/known-failure-modes.md#L614), which is the weakest shelf it has |
| Review 5 change 3 — the fourth mandatory command at [agents/development-agent.md#L41](../../agents/development-agent.md#L41) | 2026-09-07 | defects surviving to build time | **YES — [IMP-0658](../../logs/improvement-log.jsonl#L655)**, within hours | **A coverage gap, not disobedience** — and the second one. §2 executes it: the gate that halted this build is not in the derived set either, for a *different* reason than the one review 5 patched |
| Review 5 change 1 — [`closure_claims()`](../../scripts/verify-assumption-register.py#L97) made to see every claim | 2026-09-07 | `approved-document-internally-inconsistent` | **No** — no new member since | Too early to credit; not contradicted. [`verify-assumption-register.py`](../../scripts/verify-assumption-register.py) exits 0 on the current tree |
| The [`no-hardcoded-environment-values`](../../config/revitalise-grant-automation-build.yml#L423) HARD step itself | 2026-08-21 | `C-TECH-047` breaches | n/a — this IS the gate | **Fired correctly, both times.** Detection was never the gap. It caught [IMP-0119](../../logs/improvement-log.jsonl#L116) twice in one dispatch and [IMP-0658](../../logs/improvement-log.jsonl#L655) once. Its own known-bad fixture still fails under it |

**Classes recurring after a prose-or-digest disposition: two, and they are the same shape.** A lesson with no mechanical home ([IMP-0119](../../logs/improvement-log.jsonl#L116)), and a mechanical home whose coverage was patched one escapee at a time (review 5 change 3). The ladder's answer to both is the same: stop naming escapees, and make the gap itself visible.

**Closure-level audit.** [IMP-0658](../../logs/improvement-log.jsonl#L655) carries `observable_at: V2`, so its closure needs a `reobserved` record and cannot rest on a document. The original reproduction — the C-TECH-047 grep over the solution root — was re-run in this session and finds nothing; the literal URL survives only in the gate's own known-bad fixture at [`EnvUrlHardcoded.xml`](../../src/tests/fixtures/known-bad/no-hardcoded-environment-values/EnvUrlHardcoded.xml#L4), where it belongs.

---

## 2. The cluster, and the altitude call

```
CLUSTER: live-environment-value-in-evidence-comment  (x2: IMP-0658, and IMP-0659 which is its fix)
         + the mechanism it shares with IMP-0119 (2026-08-20) and IMP-0654 (2026-09-07)
Altitude:  CLASS — second instance of "a HARD source-only gate sits outside the pre-handoff
           derived set, so that set reports complete coverage while missing it"
Ladder row: "a tool could catch it mechanically" + "second instance -> generalise.
            Instance patches are forbidden here"
Becomes:   scripts/run-source-gates.py — widened selection (change 1a) AND an explicit report of
           what it did NOT select (change 1b), plus the two prose corrections that follow from it
Retires:   nothing — see §4; the obvious candidate is NOT retirable and the reason matters
Cites:     IMP-0658
Residual:  change 1b REPORTS the uncovered gates; it does not run them. A gate taking no path at
           all (verify-assumption-register.py) stays outside the runner and stays statically named.
```

### The behavioural assertion, executed rather than read

The claim *"this gate is not in the pre-handoff set"* is a statement about a script's behaviour, so I ran it rather than reading its selection regex:

```
run-source-gates: 13 source gate(s) from config/revitalise-grant-automation-build.yml
  PASS source-validate … PASS no-secured-columns-in-code-app
run-source-gates: OK — 13 source gate(s) pass.
```

`no-hardcoded-environment-values` is absent. The [selection rule](../../scripts/run-source-gates.py#L20) requires a command that invokes `scripts/verify-*.py` **and** names a solution root; this step names the solution root but is an inline inverted `grep`, so [`GATE_RE`](../../scripts/run-source-gates.py#L73) rejects it.

### Why this is the orthogonal axis to the widening review 5 rejected

**Review 5 measured a widening and rejected it, and I nearly duplicated that decision before reading it.** Its rejected candidate was *"every `verify-*.py` step naming no path"* — relaxing the **path** requirement — which swept in 22 further steps including [`improvement-log-check`](../../config/revitalise-grant-automation-build.yml#L62), a step that is red by design whenever any blocker is open. That rejection was correct and stands.

**This review relaxes the other half — the gate *shape* — while keeping the path requirement.** Measured against the real config, adjudicating every candidate by hand:

| Rule | Steps selected | Adjudication |
|---|---|---|
| Today: invokes `verify-*.py` **and** names a solution root | **13** | 13 relevant, 0 false positives — unchanged |
| Rejected by review 5: any `verify-*.py`, no path required | 13 + **22** | **Still rejected.** Not revisited here |
| **This review:** names a solution root **and** runs only `grep` or `verify-*.py` | 13 + **3** | **3 relevant, 0 false positives.** The 3 are [`no-special-category-data-in-scoring`](../../config/revitalise-grant-automation-build.yml#L414), [`no-hardcoded-environment-values`](../../config/revitalise-grant-automation-build.yml#L423) and [`no-hardcoded-thresholds`](../../config/revitalise-grant-automation-build.yml#L438) — all HARD, all pure inverted greps over solution source, all green on the current tree, **0.03 seconds for all three** |

The two `pac solution pack` steps are the false positives this keeps out, and the allowlist is **fail-closed** by design: a step qualifies only if its command runs `grep` or a `verify-*.py`, so a step invoking any tool nobody has enumerated is excluded rather than swept in. The corpus here is five steps and I enumerated all five before choosing the set.

### The prose that is now measurably false

[agents/development-agent.md#L41](../../agents/development-agent.md#L41) annotates the command as *"every HARD gate over the source you just wrote"*. It runs **13 of the 16** HARD gates that read only solution source. That sentence is what let this dispatch believe it was covered, and it is a claim about a value, so change 2 replaces it with what the tool itself will now print.

### And the instruction that actively invited the defect

The author did not put a live URL in source out of carelessness. [skills/how-to-verify-a-platform-contract.md#L363](../../skills/how-to-verify-a-platform-contract.md#L363) instructs — correctly, and this review does not weaken it — *"**Mark the guess where it lives, too.** A comment carrying the `A-nnn` id at the point in source where the guess was made."* The register's own `Where` column is defined as *"File and element/path in source"*. So the skill tells an author to annotate the assumption in source, and says nothing about what may not appear in that annotation. Change 3 adds that one clause at the point of the instruction, not in a knowledge file the author had no reason to open.

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | script | [`scripts/run-source-gates.py`](../../scripts/run-source-gates.py) | (a) select solution-root-scoped inline `grep` checks via a fail-closed tool allowlist — 13 → 16 gates; (b) print every HARD step the rule did **not** select under a `NOT covered by this run` heading, so the runner can never again read as complete coverage | IMP-0658 | YES — `python3 scripts/run-source-gates.py config/revitalise-grant-automation-build.yml` must list 16 and name the uncovered set; `--selftest` must pass | **already wired** — deliberately not a build step (it invokes gates the build already invokes; wiring it would run all 16 twice) and deliberately named outside the `verify-*` convention, so [`verify-build-config.py`](../../scripts/verify-build-config.py)'s suite-gate rung does not require a step for it |
| 2 | agent | [`agents/development-agent.md`](../../agents/development-agent.md#L41) | Replace *"every HARD gate over the source you just wrote"* with the true scope, and require the dispatch to read the `NOT covered by this run` list rather than treating a green run as full coverage | IMP-0658 | YES — `grep -c 'every HARD gate over the source you just wrote' agents/development-agent.md` must return 0 | N/A |
| 3 | skill | [`skills/how-to-verify-a-platform-contract.md`](../../skills/how-to-verify-a-platform-contract.md#L363) | Extend the *"Mark the guess where it lives"* rule: the in-source marker carries the `A-nnn` id and a pointer to where the evidence lives — never the evidence itself, because `C-TECH-047` scans comments | IMP-0658 | N/A — instruction change | N/A |

**Constraint budget: 0 of 3 used.** No new constraint is proposed. [C-TECH-047](../../constraints/technology/technology-constraints.md#L89) already covers this exactly, is HARD, has a real gate and a known-bad fixture, and fired correctly on both instances. A second row saying the same thing about comments would be a comment about a constraint.

**No new `verify-*.py` script is added**, so the registered count stays at **57** and [`verify-derived-counts.py`](../../scripts/verify-derived-counts.py) needs no update from this review.

---

## 4. Retirements

> Retirement check performed: the live constraint rows were reviewed against this cluster, and **none is currently redundant**, because the only constraint in scope ([C-TECH-047](../../constraints/technology/technology-constraints.md#L89)) is the one doing the work. **10** rows stand retired, derived with `grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l`.

**One candidate was considered and explicitly rejected, because the reasoning is the interesting part.** Review 5 patched the previous coverage gap by *statically naming* [`verify-assumption-register.py`](../../scripts/verify-assumption-register.py) in the mandatory command block at [agents/development-agent.md#L44](../../agents/development-agent.md#L44) — the exact instance patch the altitude rule forbids on a second occurrence. It would be tidy to retire it now that change 1 generalises the selection.

**It must stay, and change 1 is why.** Change 1b makes the gap *visible*; it does not make the runner *run* a gate that takes no path at all, which is precisely why that script escaped the derived rule in the first place. Retiring the static mention would trade a working instance patch for a report nobody is obliged to act on. That is a coverage regression, not a promotion.

---

## 5. Findings left unprocessed

**Deferred:** none

**Scope, stated because the no-silent-caps rule applies to the queue itself.** This is a blocker dispatch, and the blocker trigger scopes it to the **unread blocker alone** — one unread finding must not pull a review of everything around it. I excluded, by state:

- **18 other `unread` entries**, none of them `blocker`. They are enumerated by [`verify-improvement-log.py`](../../scripts/verify-improvement-log.py)'s own state breakdown, which is the authoritative list; I have deliberately not re-listed the ids here, because naming them in this document would mint 18 fresh citation warnings against entries this review did not process. None is stamped by this review.
- **4 `awaiting-approval` entries**, which already have documents and need a keyword, not a session: [IMP-0608](../../logs/improvement-log.jsonl#L605) is parked at [review 2026-09-05 (2)](2026-09-05-improvement-review-2.md); [IMP-0644](../../logs/improvement-log.jsonl#L641) and [IMP-0645](../../logs/improvement-log.jsonl#L642) at [review 2026-09-07 (2)](2026-09-07-improvement-review-2.md); [IMP-0652](../../logs/improvement-log.jsonl#L649) at [review 2026-09-07 (3)](2026-09-07-improvement-review-3.md).
- **139 `reviewer-deferred` entries**, each carrying a reason a human accepted. One of them, [IMP-0274](../../logs/improvement-log.jsonl#L271), still names no `revisit_when` — a deferral with no trigger to come back. Reported, not fixed; it is not this dispatch's scope.

**[IMP-0659](../../logs/improvement-log.jsonl#L656) is not "left unprocessed" — it is already `APPLIED`.** It is [IMP-0658](../../logs/improvement-log.jsonl#L655)'s fix, carries `corrects: IMP-0658`, and I verified its claim against the tree rather than taking it on report: the literal DEV org URL is gone from [`Customizations.xml`](../../src/solutions/RevitaliseGrantAutomation/Other/Customizations.xml#L90), both comments now cite the Dev Summary, and the C-TECH-047 grep exits 0.

---

## 6. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 656 | **657** — [IMP-0660](../../logs/improvement-log.jsonl#L657) was appended at apply time; see §8 |
| Distinct classes | 131 | **132** |
| Recurring classes (x≥2) | 54 | 54 |
| Digest lines | 660 | **661**, re-registered in the generator's `CURRENT SIZE` line |

No entry is appended by this review, so the counts are unchanged; the digest regenerates because [IMP-0658](../../logs/improvement-log.jsonl#L655)'s status moves. The digest line count is registered in [`derived-counts-registry.json`](../../scripts/derived-counts-registry.json) and drifts whenever it regenerates, so it is re-measured and re-registered at apply time rather than predicted here.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-07-improvement-review-6.md

Findings processed: 1 NEW  →  1 cluster
Regression check:   4 prior changes audited, 2 classes recurred
Proposed:           0 constraints (cap 3), 1 gates/scripts, 1 skill/knowledge edits,
                    1 agent-file edits, 0 retirements
Altitude calls:     1 generalised from instance to class, 0 left as notes
Digest:             will regenerate — 131 lessons, 54 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Applied

**`APPROVE IMPROVEMENTS` — Anna Southern, 2026-09-08.** All three proposed changes applied; one of
them **narrowed**, and the narrowing is recorded here, in [IMP-0658](../../logs/improvement-log.jsonl#L655)'s `applied_by`, and in the gate output.

| # | Change | Applied at | Entries moved to APPLIED |
|---|---|---|---|
| 1a | [`select()`](../../scripts/run-source-gates.py#L169) now requires *names a solution root* **and** [`is_cheap_local_check()`](../../scripts/run-source-gates.py#L133) — a fail-closed [tool allowlist](../../scripts/run-source-gates.py#L90) of `grep`/`echo`/`scripts/verify-*.py`, with a quote-aware segment splitter so `grep -rnE 'a\|b'` is not read as a pipeline. **13 → 16 gates.** Docstring measurement block re-measured and re-dated | 2026-09-08 | [IMP-0658](../../logs/improvement-log.jsonl#L655) |
| 1b | [`report_uncovered()`](../../scripts/run-source-gates.py#L179) prints a `NOT covered by this run` list after every run and every `--list` — **NARROWED**, see below | 2026-09-08 | (same entry) |
| 2 | [agents/development-agent.md#L41](../../agents/development-agent.md#L41) — *"every HARD gate over the source you just wrote"* replaced with the true scope, plus a paragraph requiring the dispatch to read the uncovered list. The stale *"13 gates, ~20 seconds"* at [#L67](../../agents/development-agent.md#L67) re-measured to 16 gates, under 10 seconds, in the same change | 2026-09-08 | (same entry) |
| 3 | [skills/how-to-verify-a-platform-contract.md#L366](../../skills/how-to-verify-a-platform-contract.md#L366) — the in-source marker carries the `A-nnn` id and a pointer, never the evidence, because `C-TECH-047` scans comments | 2026-09-08 | (same entry) |

### The one narrowing, and what compelled it

Change 1b was approved as *"print every **HARD** step the rule did not select"*. **This build config
carries no machine-readable severity field.** Its 73 steps expose exactly three keys — `name`,
`command`, `when` — and SOFT is expressed only in YAML comments and by a step's own `--warn-only`
flag. So the list is printed **unfiltered**: 57 of 73 steps, with no severity claimed.

The false claims this removes are nameable, which is the test that separates a narrowing from a
substitution: a severity-labelled list would have printed the SOFT-by-design steps
[`document-status-consistency`](../../config/revitalise-grant-automation-build.yml#L120),
[`models-yml-comments`](../../config/revitalise-grant-automation-build.yml#L132) and
[`constraint-verifiers`](../../config/revitalise-grant-automation-build.yml#L375) as HARD, along
with `npm ci`, `install-pester` and the Playwright install. The intent — *the runner can never
again read as complete coverage* — is fully preserved and is stated in the printed line itself.

### Verification, at V2

| Check | Result |
|---|---|
| `python3 scripts/run-source-gates.py --selftest` | OK — 10 cases, including the negative case proving a red gate propagates |
| `python3 scripts/run-source-gates.py config/revitalise-grant-automation-build.yml` | **16 of 16 PASS**, 6.5s wall, then `NOT covered by this run — 57 of 73 build step(s)` |
| Corpus adjudication | 18 of 73 steps name a solution root; 16 selected, **0 false positives**; the 2 excluded are the [`pac solution pack`](../../config/revitalise-grant-automation-build.yml#L719) steps (network, auth, minutes) |
| **Reproduction of [IMP-0658](../../logs/improvement-log.jsonl#L655) itself (V2)** | The literal DEV org URL was injected into a temporary file under the solution root in an `A-DS-1` evidence comment. The widened runner **exits 1** and names [`no-hardcoded-environment-values`](../../config/revitalise-grant-automation-build.yml#L423) among the red gates — the 13-gate selection reported 13 of 13 PASS on this same shape. File removed; `git status` clean of it |
| [`verify-improvement-log.py --check`](../../scripts/verify-improvement-log.py) | **exit 0** — 656 entries, 161 NEW, 489 APPLIED, 6 REJECTED, zero `TRIGGER` lines. §9's prediction held exactly |
| [`verify-build-config.py`](../../scripts/verify-build-config.py) | exit 0 — the suite-gate rung still requires no step for this tool |
| Digest | regenerated; [`--check`](../../scripts/generate-known-failure-modes.py) current at 656 entries. **660 lines**, re-registered in the generator's `CURRENT SIZE` line, clearing the `known-failure-modes-digest-line-count` drift |
| `ls scripts/verify-*.py \| wc -l` | **57**, unchanged — no new gate script was added |

Three pre-existing drifts in [`verify-derived-counts.py`](../../scripts/verify-derived-counts.py)
(two secured-column counts in the Dev Summary, one in `REV Trustee.xml`) are untouched by this
review and remain open; that step is SOFT. [`verify-review-document.py`](../../scripts/verify-review-document.py)
exits 1 on 5 findings, **all of them in August documents** — none in this one.

### One finding appended

[IMP-0660](../../logs/improvement-log.jsonl#L657), `friction`, `unread` — the narrowing above, logged
as its own class: *a proposed change whose wording filters a corpus by an attribute that corpus does
not carry as data*. It proposes **no** rule change. The NARROW-AND-REPORT branch in
[agents/improvement-agent.md#L199](../../agents/improvement-agent.md#L199) already covers it exactly
and worked as written; a first instance of a drafting habit does not justify a new rung. Its
`revisit_when` names the second instance as the trigger. It carries **no** `deferred_reason`,
deliberately — that field records a decision a human accepted, and this agent may not write one for
its own finding.

**Nothing else in this document was rewritten.** §0–§7 stand as the reviewer approved them,
including §2's execution trace showing the pre-change tool selecting 13 gates.

---

## 9. What the simulation predicts, so it can be checked against reality

Run on a scratch copy of the log, then restored and confirmed byte-identical with `diff`:

| State | [`verify-improvement-log.py --check`](../../scripts/verify-improvement-log.py) |
|---|---|
| Today | **exit 1** — `TRIGGER: 1 NEW blocker in state 'unread'` |
| After this draft stamps `reviewed_in` (no keyword) | **exit 1** — the same trigger, reworded to `awaiting-approval`. **The build stays blocked** |
| After `APPROVE IMPROVEMENTS` and change 1 lands | **exit 0** — 656 entries, 161 NEW, 489 APPLIED, 6 REJECTED, zero `TRIGGER` lines |

The middle row is the one worth noticing: stamping the entry as reviewed does **not** unblock the build, and it is not meant to. Only the keyword does.
