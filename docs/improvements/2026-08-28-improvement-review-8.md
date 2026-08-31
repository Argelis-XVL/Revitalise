# Improvement Review 38 — 2026-08-28

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 14 `unread` → 9 clusters
**Trigger:** the batch trigger — `python3 scripts/verify-improvement-log.py --check` reported
**13 NEW entries awaiting closure** against a threshold of 10.
**Gate:** `APPROVE IMPROVEMENTS` — ~~nothing in this document is on disk~~ **APPROVED 2026-08-28 by
Xander Lykopoulos and APPLIED in full, with the three decisions resolved and one extra change
authorised. §9 carries the record and the two deviations. `verify-improvement-log.py` is OK, the
digest is current, and the build is clear.**
**Scope:** the 8 entries the dispatch named (`IMP-0447`–`IMP-0454`), **plus 5 that this review
un-parked by correcting a false stamp** (`IMP-0440`–`IMP-0444`), **plus `IMP-0455`, appended by the
concurrent dispatch at 17:20 while this draft was being measured.** See the scope note below; the
five are not scope creep but the removal of a data defect that had made them unprocessable by any
session, and `IMP-0455` is folded in because it names the same gate as `IMP-0451` and asks
explicitly to be coordinated with it — designing that gate twice is the defect `IMP-0443` records.
No `APPLIED` or `REJECTED` entry was read, and the 78 `reviewer-deferred` entries are untouched per
activation step 2 ([`improvement-agent.md` L103](../../agents/improvement-agent.md#L103)).

**The five parked entries were parked by a defect, not by a decision.** All five carry
`reviewed_in: docs/improvements/2026-08-28-improvement-review-6.md`, and **review 6 does not
mention any of them** — `grep -c 'IMP-044[0-4]'` against that document returns **0**. Review 6
*appended* them, which the separate `appended_by` field already records correctly on all five. The
consequence is a closed loop: the stamp makes the gate report them as `awaiting-approval`, whose
instruction to every future review is *"read the document each one names and send the keyword; do
not re-derive"* — and the document names them nowhere, so no keyword can ever dispose of them.
Correcting the stamp is change 8. Three of the five share a class with three of the eight
dispatched entries, so the defect was also hiding cluster members.

**Concurrency — it moved this document's own corpus three times while the measurements ran, and
each move improved the design.** The `architect-agent` dispatch correcting the documentation-honesty
gap ([`trustee-portal-visual-refresh-architecture.md`](../architecture/trustee-portal-visual-refresh-architecture.md),
[`contract/tad-deferrals.json`](../../contract/tad-deferrals.json)) **landed its Appendix A erratum
between two runs of this review's candidate gate** — the same design measured 4 findings and then 0
on the same file, which §6a uses as the polarity proof. It then **created a new
`undelivered_requirements` register** and logged `IMP-0455` asking that a gate be made to read it.
That register replaced the weakest part of this review's design: an acquittal that was a prose
marker is now an owned, dated, expiring entry. Both files are still `M` in `git status`, so that
dispatch may still be working; activation step 8 re-measures before anything here is applied
([`IMP-0405`](../../logs/improvement-log.jsonl)). **Neither file is edited by this review.**

**Numbering:** 37 → 38. **WBS:** the dispatched entries carry `wbs:6.9` where they carry one; the
review itself is `system` work, never billable
([`C-COM-002`](../../constraints/commercial/commercial-constraints.md#L35)). No contracted figure
is restated (D-3).

---

## Summary

**Nine changes as applied — eight proposed, plus the stamp-check gate the reviewer authorised on a
single instance. No new rules: the constraint budget is untouched at 0 of 3.** Every cluster
resolved to a script, a skill line or a data correction, and no change added a 52nd script — both
new gates went inside gates that already existed.

**The most important item is the gate blind spot the dispatch asked about, and it is real.** No
gate in this repository read the traceability matrix that phase acceptance reads, and none read the
new register that now owns the shortfall. The extension built for it scores **4 findings, 4 true
positives** against the state in which the defect actually shipped, and **0** today — because the
gap is now declared in two places, which is the correct outcome rather than a miss.

**The teeth are the expiry, not today's verdict.** The three register entries expire
**2026-09-18**, and the new validation fails on an expired one. So this gate is green now and turns
red in three weeks unless the reviewer's sizing decision lands — which is precisely what a deferral
register is supposed to do, and what nothing was enforcing.

**Two proposals were withheld because measurement disproved them, and one is a repeat.** The
prose-gate asked for by one finding scores **3 findings on the defective text and 3 on the
corrected text** — it cannot tell them apart at all, the sixth measured instance of that shape. The
`--committed-only` flag asked for by another would leave its gate with **0 tracked inputs**, which
review 37 had already measured for the neighbouring gate one review earlier. §6 carries both.

**At draft time the improvement-log gate was FAILED, and its own suggested remedy was wrong.** That
is a HARD build step, so the next build would have halted on it. Change 8 was the unblock and §6f
explains why the printed remedy would have made things worse; change 9 is the gate that stops it
recurring. **As applied, `verify-improvement-log.py` reports OK over 455 entries with 0 unread and
0 awaiting-approval.**

---

## 1. Regression check — did review 37's changes work?

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| [`scripts/verify-superseded-column-writers.py`](../../scripts/verify-superseded-column-writers.py) + the HARD step at [`build.yml` L195](../../config/revitalise-grant-automation-build.yml#L195) — review 37 change 1 | 2026-08-28 | `no-assertion-on-shipped-content` | **YES** — `IMP-0448`, same day | **Working for the half it covers, structurally blind to the other half.** See below |
| [`knowledge/technology/dataverse.md`](../../knowledge/technology/dataverse.md#L294) — change 2 | 2026-08-28 | `platform-contract-guessed-not-groundtruthed` | **NO** | **No evidence either way.** Prose; nothing in this batch touches the class |
| [`scripts/lib/tracked_paths.py`](../../scripts/lib/tracked_paths.py) — change 3 | 2026-08-28 | `gate-scope-mismatch` | **YES, in the property** — `IMP-0447` | **Working where adopted. Adoption is the gap, and review 37 predicted exactly this** |
| [`scripts/verify-forms-and-views-reachable.py`](../../scripts/verify-forms-and-views-reachable.py#L182) scope line + `--committed-only` — change 4 | 2026-08-28 | `gate-scope-mismatch` | Same recurrence | **Working, and its scope line is the shape change 2 copies.** But see §6d: the flag half does **not** port |
| [`scripts/verify-build-config.py`](../../scripts/verify-build-config.py) *"read the exit code"* — change 5 | 2026-08-28 | `IMP-0439`'s class (x1) | **NO** | **Working, and this review obeyed it** — §7's second question exists because the exit code was read before wiring |
| [`scripts/verify-provisioning-test-presence.py`](../../scripts/verify-provisioning-test-presence.py) `CONVENTION_SUITES` — change 6 | 2026-08-28 | `declared-policy-not-mechanically-enforced` | **NO** | **Working.** Exits 0 |
| [`scripts/lib/gate_baseline.py`](../../scripts/lib/gate_baseline.py) + [`config/gate-baselines.json`](../../config/gate-baselines.json) — change 7 | 2026-08-28 | `IMP-0439` | **NO** | **Working, and re-used.** The superseded gate reports *"0 baselined"*, and §7 proposes this instrument again |

The four audit questions, for the two recurrences:

- **`no-assertion-on-shipped-content` — was the change prose or a gate?** A gate. **Did the gate
  run?** Yes, and it passes: *"3 marked column(s) examined across 38 writer candidate(s); 0
  finding(s), 0 baselined."* It did not fire on `IMP-0448` because its subject is **writers** in
  `.ps1` and `Workflows/*.json`, and the three new false statements were in shipped **prose** — an
  entity-level `<Description>`, an option-set `<Description>` and a `notes.md`. **So is this
  `gate-cannot-fail`?** No. It is a correctly-scoped gate meeting a neighbouring defect, and §6b is
  the measurement showing the neighbouring defect has no mechanical home.
- **`gate-scope-mismatch` — was the change prose or a gate?** A shared helper plus one gate's
  adoption. **Did it run?** Yes; the adopting gate reports its scope on every verdict. The
  recurrence is in a gate that never adopted it, which review 37's own residual named:
  *"opt-in, exactly as the ignored direction is."* **Altitude:** this is the second instance, so
  the ladder forbids another instance patch — and §6d records that the general form (force every
  glob-driven gate through `git ls-files`) is measurably wrong. The available generalisation is the
  **scope line**, not the flag, and change 2 adopts it in the gate whose verdict was quoted as a
  finding. A third instance justifies a meta-check.
- **Did the closure evidence match the level each defect was visible at?** Yes, and review 37 is
  clean here. `IMP-0434` (V4) and `IMP-0435` (V5) were **left open** with a `revisit_when` rather
  than closed on a green gate, which is what
  [`C-TECH-053`](../../constraints/technology/technology-constraints.md#L108) requires. No closure
  in review 37 claimed a level above its evidence.

**And the one thing this audit establishes about the system.** Review 37 closed with the argument
that its new gate caught two instances of its own class within forty minutes. That is true, and the
same file produced a third instance nine minutes later that the gate could not see — because the
defect moved from code into prose. A gate narrows the surface; it does not close it. That is why
§6b declines to build the prose half rather than shipping a blind version of it.

---

## 2. Clusters and promotion decisions

```
CLUSTER A: a contract table in the approved TAD disagrees with what source PRODUCES, and no
           gate reads it  (x2: IMP-0451, IMP-0454 — class approved-document-internally-
           inconsistent, now x18)
Altitude:  CLASS. Two instances, one document, one day, and one of them is a real
           requirements-delivery gap that reached a phase-acceptance surface. The dispatch's
           hypothesis is confirmed: verify-tad-coverage.py reads §3.1's column table and the
           design-doc claim set, and NOTHING reads Appendix A's traceability rows or §3.3's
           response enumeration.
Ladder row: "a tool could catch it mechanically" → a script plus a build gate
Becomes:   (1) THREE new assertions inside the EXISTING verify-tad-coverage.py — not a new
           script. (d) every response key the flow composes as a literal null in its OK document
           must be acquitted, EITHER by an undelivered_requirements register entry naming it in
           response_fields (preferred — owned, dated, expiring) OR by the Appendix A REQUIREMENT
           row that names it carrying a not-delivered marker; (e) every status value the flow
           composes or the app synthesises outside test files must appear in §3.3's enumeration;
           (f) every undelivered_requirements entry validates its seven required fields and a
           non-past ISO expiry, and FAILS as a dead promise when the response field it names is
           no longer null. All three trigger on VALUES read from source, which is what makes
           them survivable (agents/improvement-agent.md L419).
Retires:   nothing — this surface was undefended
Cites:     IMP-0451, IMP-0454, IMP-0455, and IMP-0158/IMP-0159 for the older half of the same
           property
Residual:  TWO acquittal paths, and the weaker one is prose. A key acquitted by an Appendix A
           marker rather than by a register entry is owned by nobody and expires never, so an
           author can still silence a true finding by writing "null" into a row. It is kept
           because withdrawing it would fail ethnicGroupDistribution, a shortfall the reviewer
           has already closed (OQ-037, benchmark withdrawn) and which needs no owner. The
           mitigation is that the summary line NAMES the acquitting path for every suppressed
           key on every run, per tad-deferrals.json's own rule that a deferral suppresses the
           FAIL and never the report — so a prose acquittal is visible as a prose acquittal.
           Also: one flow supplies every input today, so assertion (d) has one artefact's worth
           of corpus.
```

```
CLUSTER B: a source-auditing gate's verdict does not say WHICH UNIVERSE it measured
           (IMP-0447 — class finding-diagnosis-unverified, x13; the property is IMP-0445's,
           second instance in one day)
Altitude:  CLASS for the scope line, and the finding's OWN LITERAL PROPOSAL IS WITHHELD.
           It asks for --committed-only on verify-superseded-column-writers.py. Measured: all
           three UNUSED FROM REVISION markers live in ONE UNTRACKED file, git ls-files over both
           round-statistics tables returns 0 tracked files, so the flag would give the gate zero
           marked columns — and that gate's own IMP-0007 rule makes a no-input run FAIL. The flag
           would be a switch that can only break it (§6d).
Ladder row: "second instance of the same class → generalise", applied to the property rather
           than to the wording: a gate whose verdict can be quoted as a finding must state its
           scope. That half needs no tracked inputs and would have prevented the incident on
           its own.
Becomes:   (2) the scope line on every verdict, copying the shape review 37 change 4 already
           established at verify-forms-and-views-reachable.py L182-L198; (3) the observer-side
           half as a skill line — see the altitude correction below.
Retires:   nothing
Cites:     IMP-0447, IMP-0445, IMP-0437
Residual:  a scope line is read by a human or it does nothing. Nothing forces the next gate
           author to print one, and §6d explains why the mechanical version is unavailable for
           84 of 108 glob calls.
Note:      ALTITUDE CORRECTION. IMP-0447 proposes the observer-side rule for
           agents/improvement-agent.md. Declined: the observer that logged the disproved blocker
           was development-agent, and EVERY agent writes findings. The rule goes in
           skills/how-to-log-an-improvement.md, which every agent loads at the moment it logs
           one. Putting it in improvement-agent.md would have addressed the one agent that did
           not make the mistake.
```

```
CLUSTER C: a HARD gate reports OK while silently skipping the one row it cannot parse
           (x2: IMP-0452, IMP-0441 — class gate-reassures-wrongly, now x21)
Altitude:  INSTANCE for the fix, and IMP-0441 needs NOTHING — it is review 36's own record that
           a prose-claim gate measured 8 lines / 4 findings / 0 true and was discarded. Its
           proposed_change is "none" and review 36 change 2 already carries its lesson. It is
           closed here, not re-derived.
Ladder row: "a tool could catch it mechanically"
Becomes:   (4) urllib.parse.unquote the 'Where' path before resolving it, and FAIL when a row
           NAMES a target that does not resolve. Measured narrowing (§6c): the FAIL branch is
           restricted to rows that name a target, because 7 of the 8 unresolvable rows name no
           target at all and failing those would turn a delivery document's open assumptions
           into a red build — review 37 change 5's rule, applied.
Retires:   nothing
Cites:     IMP-0452, IMP-0441
Residual:  a row naming no 'Where' target is still only a NOTE, so an OPEN assumption with no
           source pointer remains unchecked by design. That is a documentation gap owned by the
           document's author, not something this gate can invent a target for.
```

```
CLUSTER D: a count a human reconciles against a document drifts from source
           (x2: IMP-0453, IMP-0444 — class hand-maintained-count-drifts-from-source, now x23)
Altitude:  INSTANCE for the gate's own count; ROUTED for the other, which is not mine.
Ladder row: "a tool could catch it mechanically"
Becomes:   (5) de-duplicate declared_removals() by (role, privilege). Measured: 3 raw tuples,
           2 distinct pairs, and the script's own header at L203 already records 2 as the
           truth — so the gate disagrees with itself in writing.
Retires:   nothing
Cites:     IMP-0453, IMP-0444
Residual:  IMP-0444's three drifted prose figures are NOT fixed here. Two live in an approved
           Dev Summary and one in a solution role file — delivery-owned artefacts, C-COM-002 —
           and verify-derived-counts.py still reports all three today, confirmed this dispatch.
           Routed to development-agent in §5.
```

```
CLUSTER E: a gate's remediation sentence cannot be followed literally
           (IMP-0450 — class output-shape-defeats-the-reader, x9)
Altitude:  INSTANCE. One instance, and the general lesson is already in the finding; the
           mechanical fix is one string and costs nothing.
Ladder row: "a tool could catch it mechanically"
Becomes:   (6) print the marker in the exact bytes the parser accepts, in BOTH places a reader
           looks — the UNCLASSIFIABLE message at L179 and the docstring at L22. Confirmed by
           execution: the parser at L90 requires box-drawing U+2500 and a trailing rule; both
           advisory strings flatten it to two ASCII hyphens.
Retires:   nothing
Cites:     IMP-0450
Residual:  nothing mechanical can compare a gate's advice against its own parser. This is one
           string in one gate; a second instance would justify a check that every remediation
           sentence quoting a token round-trips through the parser that demands it.
```

```
CLUSTER F: the prose half of "written by nothing" — GATE DISCARDED ON MEASUREMENT
           (IMP-0448 — class no-assertion-on-shipped-content, x20)
Altitude:  KNOWLEDGE, and this is a downgrade from what the finding asks for. It proposes
           extending verify-superseded-column-writers.py to <Description> prose. Measured
           against the defective text and the corrected text of the same description: 3 findings
           and 3 findings. The gate CANNOT TELL THEM APART (§6b).
Ladder row: "one instance, but the cause is general and a human needs to know it" → knowledge/
Becomes:   (7) a knowledge line: when an ADR moves columns off a table but RETAINS them, sweep
           the artefacts that describe the TABLE, not only those that read or write the columns.
Retires:   nothing
Cites:     IMP-0448, IMP-0434, IMP-0422
Residual:  no gate reads an entity-level or option-set <Description> for a stale write claim,
           and after this measurement none should. §7's first question offers the reviewer the
           one route that WOULD make a value gate possible, because it is a real trade-off and
           not mine to take.
```

```
CLUSTER G: five findings parked in a state no session can clear
           (IMP-0443 + the stamp defect on IMP-0440-IMP-0444 — class
           learning-substrate-destroyed, x26)
Altitude:  DATA CORRECTION plus a new finding. Not a rule change: the two fields that encode
           this distinction already exist and are documented at verify-improvement-log.py
           L439-L445 — `appended_by` means "a review WROTE this", `reviewed_in` means "a review
           PROCESSED this". All five carry both, pointing at the same document, and only
           `appended_by` is true.
Ladder row: "the system's own memory failed" → a read-path change
Becomes:   (8) drop the false `reviewed_in` from all five. That returns them to `unread`, which
           is what they are, and clears the FAILED verdict blocking the build. IMP-0443 itself
           closes on review 37 change 6, which is the narrowing it asked for.
Retires:   nothing
Cites:     IMP-0443, IMP-0154, IMP-0033
Residual:  nothing prevents the next review from writing the same stamp. A check that
           `reviewed_in` names a document that actually MENTIONS the entry is mechanically
           available and is NOT proposed here on one instance — §6f states the measurement that
           would size it, and §7's third question puts it to the reviewer.
```

```
CLUSTER H: a sanctioned register that NO GATE READS  (IMP-0455 — class gate-scope-mismatch, x10)
Altitude:  CLASS, and it merges into cluster A's change rather than getting its own. The finding
           was logged by the concurrent architect-agent dispatch at 17:20 and says so itself:
           "the two proposals are the same gate seen from the document side and the register
           side." Building a second gate for one property is the duplication the anti-bloat
           limits exist to prevent, and two dispatches designing one gate within the hour is
           exactly IMP-0443.
Ladder row: "a tool could catch it mechanically"
Becomes:   assertion (f) of change 1. The register's own key name declares the gap —
           `_undelivered_requirements_is_read_by_no_gate` — and grep confirms it: NO file under
           scripts/ mentions `undelivered_requirements`. So three owned entries carrying a
           2026-09-18 expiry would have expired in silence.
Retires:   nothing
Cites:     IMP-0455, IMP-0451
Residual:  the register can express a gap that Appendix A does not, and nothing forces the two
           to agree with each other. Assertion (f) checks the register against SOURCE and
           assertion (d) checks source against BOTH; no assertion compares the register against
           Appendix A directly. Stated rather than built: that is a third document-to-document
           comparison, and this review already declines one (§6b).
```

```
CLUSTER I: records only, no change  (x3: IMP-0449, IMP-0440, IMP-0442)
Altitude:  NOTHING, deliberately, and all three say so themselves — every one carries
           proposed_change.type "none".
           IMP-0449: the live DEV request row still holds rev_status = 2 from a create-only
           seeder that no longer writes it; the entry exists so the next session to query that
           table does not read the value as a live writer and reopen a closed finding. No live
           operation is proposed and none should be.
           IMP-0440: a scope repair measured at ZERO coverage gain, recorded so the next review
           does not re-derive the expectation.
           IMP-0442: a proposed narrowing that would have missed all three of its own finding's
           worked examples, discarded on measurement.
Ladder row: "one instance, specific to one feature, no general mechanism" → it stays a log note
Becomes:   nothing. Closed with the record intact.
Cites:     IMP-0449, IMP-0440, IMP-0442
Residual:  IMP-0449 is observable_at V3 and cannot be closed from here — see §5.
```

---

## 3. Changes proposed

| # | Type | Target | What | Cites | Provable? |
|---|---|---|---|---|---|
| 1 | gate extension | [`scripts/verify-tad-coverage.py`](../../scripts/verify-tad-coverage.py#L558) — assertions **(d)**, **(e)** and **(f)**, inside the already-HARD [`tad-coverage` step](../../config/revitalise-grant-automation-build.yml#L616) | (d) a response key composed as literal `null` in the OK document must be acquitted by an [`undelivered_requirements`](../../contract/tad-deferrals.json) entry naming it, or by a not-delivered marker in the Appendix A **requirement** row naming it — and the summary names which path acquitted each; (e) a status value the flow composes or the app synthesises outside test files must appear in §3.3's enumeration; (f) every register entry validates seven fields plus a non-past ISO expiry, and fails as a dead promise once its field is no longer null | IMP-0451, IMP-0454, IMP-0455, IMP-0158, IMP-0159 | **YES** — (d) **4 findings / 4 true / 0 false** against the state the defect shipped in, **0** today with all 5 acquittals named; (e) **2 findings / 2 true / 0 false** after one narrowing, from 5/2/3; (f) 3 entries validate, 0 stale, and **no file under `scripts/` reads the register today**. §6a |
| 2 | script | [`scripts/verify-superseded-column-writers.py`](../../scripts/verify-superseded-column-writers.py#L239) | A scope line on **every** verdict, pass or fail, naming the universe measured and its untracked inputs — the shape at [`verify-forms-and-views-reachable.py` L182](../../scripts/verify-forms-and-views-reachable.py#L182). **`--committed-only` is WITHHELD** (§6d) | IMP-0447, IMP-0445 | **YES** — the verdict currently names no universe while reading an untracked `Entity.xml` for 3 of its 3 markers |
| 3 | skill | [`skills/how-to-log-an-improvement.md`](../../skills/how-to-log-an-improvement.md#L128), beside the existing `corrects` guidance | Before logging a finding whose whole evidence is a working-tree file, **re-read the file**; and never set `corrects` or severity `blocker` on an observation your own `root_cause` calls possibly transient. Mutation-falsifying a provisioning script leaves the real file deliberately broken for the length of a test run | IMP-0447, IMP-0446 | Prose. No gate — nothing can see an edit in flight (§6e) |
| 4 | script | [`scripts/verify-assumption-markers.py`](../../scripts/verify-assumption-markers.py#L163) | `urllib.parse.unquote` the `Where` path before resolving; **FAIL** when a row names a target that does not resolve; keep the NOTE for rows naming no target. Plus a fixture with a percent-encoded path | IMP-0452 | **YES** — the skipped row's file exists and carries its marker (grepped, 1 occurrence); the narrowing removes 7 false positives by name (§6c) |
| 5 | script | [`scripts/verify-role-privilege-ownership.py`](../../scripts/verify-role-privilege-ownership.py#L417) | De-duplicate `declared_removals()` by `(role, privilege)` before counting; keep every occurrence's `file:line` in the detail | IMP-0453 | **YES** — 3 raw tuples → **2** distinct pairs, matching the script's own header at [L203](../../scripts/verify-role-privilege-ownership.py#L203) |
| 6 | script | [`scripts/verify-provisioning-step-convergence.py`](../../scripts/verify-provisioning-step-convergence.py#L179) and its [docstring L22](../../scripts/verify-provisioning-step-convergence.py#L22) | Print the step marker in the exact bytes [the parser at L90](../../scripts/verify-provisioning-step-convergence.py#L90) accepts, and name a file that already carries one | IMP-0450 | **YES** — parser requires U+2500 + trailing rule; both advisory strings show `# -- <n>. ` |
| 7 | knowledge | [`knowledge/technology/dataverse.md`](../../knowledge/technology/dataverse.md#L294) | When an ADR moves columns off a table but retains them, sweep the artefacts that describe the **table** — entity-level `<Description>`, the option set's `<Description>`, the flow's `notes.md` — not only the readers and writers of the columns | IMP-0448, IMP-0434 | Prose, deliberately. The gate for it measured blind (§6b) |
| 8 | data | [`logs/improvement-log.jsonl`](../../logs/improvement-log.jsonl) | Drop the false `reviewed_in` from `IMP-0440`–`IMP-0444`, keeping the true `appended_by`. Returns five findings to `unread` and clears the FAILED verdict | IMP-0443, IMP-0154 | **YES** — `verify-improvement-log.py --check` currently **FAILED, 1 problem**; it reaches OK after the correction (§6f) |

**No new script, so the derived `verify-*.py` count stays at 51** and
[`agents/improvement-agent.md` L356](../../agents/improvement-agent.md#L356) needs no edit. Derived
at draft time, re-derived at application:
`ls scripts/verify-*.py | wc -l` → **51**. Extending an existing gate rather than adding a 52nd
script is the anti-bloat-correct choice here: assertions (d) and (e) share
[`C-TECH-066`](../../constraints/technology/technology-constraints.md#L136)'s subject exactly — *"the
approved TAD's tables are a CHECKED SPECIFICATION, not prose"* — so no new constraint row is needed
either.

---

## 4. Retirement — considered, none found

Checked, and both candidates were rejected for cause:

- **A separate script for cluster A**, retiring nothing but adding a 52nd gate. Rejected in favour
  of extending [`verify-tad-coverage.py`](../../scripts/verify-tad-coverage.py#L558): same
  document, same constraint, same build step, and that gate already carries three assertions of
  this exact shape. A new script would have needed a new constraint row and a new build step to say
  what `C-TECH-066` already says.
- **[`C-TECH-066`](../../constraints/technology/technology-constraints.md#L136)** itself, on the
  argument that assertions (d) and (e) widen it past its stated scope of *"schema and access
  tables"*. Rejected: widening a rule's coverage is not grounds to retire it, and its `Verify By`
  already names the script this review extends. The row's wording is accurate about the two tables
  it names; it under-describes what the gate now checks, which is a documentation nicety rather than
  a retirement.

Derived, not typed: `grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l` → **10** retired rows
against **80** live ones.

---

## 5. Deferrals and routing — what this review does NOT close, and why

- **[`IMP-0449`](../../logs/improvement-log.jsonl) stays open, with a reason.** `observable_at` is
  **V3** and the divergence it records is a live DEV row value. Confirming it cleared — or confirming
  it persists — needs a query against DEV that nothing in this review performs, and
  [`C-TECH-053`](../../constraints/technology/technology-constraints.md#L108) forbids closing it on
  source evidence. `revisit_when`: the next session that queries `rev_roundstatisticsrequest` in DEV
  reports what `rev_status` holds. **No live write is proposed**; the entry's own conclusion is that
  the correct state of a retained, unread column is whatever it happens to hold.
- **[`IMP-0444`](../../logs/improvement-log.jsonl) is ROUTED, not closed.** Three prose figures —
  two in an approved Dev Summary, one in a solution role file — read one below source, and
  `verify-derived-counts.py` still reports all three today (`67` vs `68` twice, `51` vs `52` once).
  Delivery-owned artefacts under [`C-COM-002`](../../constraints/commercial/commercial-constraints.md#L35);
  `development-agent` owns the correction. `revisit_when`: `verify-derived-counts.py` reports 0
  drifted claims.
- **[`IMP-0454`](../../logs/improvement-log.jsonl)'s document half is ROUTED.** §3.3's enumeration
  still names five status values where the system produces seven — confirmed this dispatch at
  [L1124](../architecture/trustee-portal-visual-refresh-architecture.md#L1124), *after* the
  concurrent dispatch's erratum landed, so it was not swept up by that correction. The TAD is
  `architect-agent`'s artefact. Assertion (e) is the durable half and is mine; the wording is not.
- **[`IMP-0447`](../../logs/improvement-log.jsonl), [`IMP-0450`](../../logs/improvement-log.jsonl),
  [`IMP-0451`](../../logs/improvement-log.jsonl), [`IMP-0452`](../../logs/improvement-log.jsonl),
  [`IMP-0453`](../../logs/improvement-log.jsonl) close** on `APPLIED`. All are `observable_at` `n/a`
  or V1 and changes 1–6 are their fixes, with `IMP-0447`'s literal proposal recorded as withheld and
  the measurement that forced it.
- **[`IMP-0448`](../../logs/improvement-log.jsonl) closes** on `APPLIED` against change 7, with its
  proposed gate recorded as **discarded on measurement** in the entry's own `applied_by`.
- **[`IMP-0455`](../../logs/improvement-log.jsonl) closes** on `APPLIED` against change 1's
  assertion (f). Both halves it asks for are built: the register is read and validated, and it is
  coordinated with `IMP-0451` rather than being given a second gate. Its `observable_at` is `n/a`.
  **Its third suggestion — one string added to the *"defers nothing"* failure message — is folded
  in**, because it costs nothing and it is the message an agent in that position actually reads.
- **[`IMP-0451`](../../logs/improvement-log.jsonl) is `observable_at: V2`.** It closes only if the
  re-observation is available: the gate is run and the four metrics are shown to be accounted for.
  That re-observation IS available from here and is recorded in §6a — 4 findings on the
  pre-correction text, 0 on the corrected text. Stated explicitly because a V2 closure needs a
  `reobserved` record and the gate refuses it otherwise.
- **[`IMP-0440`](../../logs/improvement-log.jsonl)–[`IMP-0444`](../../logs/improvement-log.jsonl)
  close** as records, each `applied_by` naming what covers it: review 36 change 2 for `IMP-0441`,
  review 36 changes 3–4 for `IMP-0440`, review 36 change 5 for `IMP-0442`, review 37 change 6 for
  `IMP-0443`. `IMP-0444` routes as above.

**THREE findings were appended at application — one more than this draft promised.** Ids were
allocated at that moment via `python3 scripts/allocate-improvement-id.py`, never from this page,
because the `architect-agent` dispatch was live on this synced path and an id read minutes earlier
is a duplicate ([`IMP-0080`](../../logs/improvement-log.jsonl),
[`IMP-0312`](../../logs/improvement-log.jsonl)):

- **[`IMP-0456`](../../logs/improvement-log.jsonl)** — the `reviewed_in`/`appended_by` stamp defect
  that parked five entries and reddened the build, *and* the more useful half: a gate whose finding
  is real while its printed **remedy** is wrong makes the remedy part of the defect.
- **[`IMP-0457`](../../logs/improvement-log.jsonl)** — the sixth measured instance of the prose-gate
  shape, and the first to measure **blind** rather than inverted, so a seventh is not designed.
- **[`IMP-0458`](../../logs/improvement-log.jsonl)** — not promised by the draft, and the reason it
  exists is §9. Two independent implementations of change 1's null-key extraction reported **0
  against a flow containing 8**, and both exited 0. Recorded for the two reusable Power Automate
  traps: a recursive `actions` walk misses an action nested in a Scope inside a condition, and
  brace-matching must take the **narrowest** enclosing block because the outermost is `properties`
  and always matches.

All three are `APPLIED`, and all three are named here rather than only stamped — which is what
change 9 requires of any review that appends its own findings, this one included. It caught this
document failing that rule on its first run; see §9.

---

## 6. Measurements

Every candidate was run against the real corpus, not only its fixtures, and every finding was
adjudicated one at a time.

### 6a — CLUSTER A: the polarity proof arrived by accident, and it is the best evidence on this page

**Assertion (d), naive design: 9 findings, 4 true, 5 false — 56% wrong.** Redesigned rather than
shipped with an exemption. Three narrowings, each removing named false positives:

| Narrowing | Removes, by name | Principle |
|---|---|---|
| Read only the **OK document**'s composed keys | `metrics`, `staleAfterSeconds` — both nulled **only** inside `Compose_error_document` | This is `IMP-0454`'s own point: a non-ok document carries a subset of the key set |
| Report only a key an Appendix A row **names** | `highHoursCareProportion`, `lowLifeSatisfactionProportion`, `unableToTakeBreakProportion` — FR-062 declares all three collectively (*"the three proportions await OQ-039"*) without naming each | Declared, not inferred |
| Restrict to rows whose first cell is a **requirement id** | `staleAfterSeconds` again, named only in an `OQ-042` row | An open question is not a coverage claim |
| Acquit a row carrying a not-delivered marker | `ethnicGroupDistribution` — FR-061 says *"always `null`"* | **True negative.** The acquittal works, proven by the corpus's own good row |

Re-measured: **4 findings, 4 true, 0 false** — `applicationsPerDay`, `breakTypeProfile`,
`exceptionalCircumstanceMix`, `exceptionalFundingSummary`. Exactly the four metrics the test-agent
found undelivered.

**Then the corpus changed underneath the measurement, which is the polarity test the agent file
demands.** Between two runs of the identical design, the `architect-agent` dispatch landed ERRATUM
5.3 on [FR-058](../architecture/trustee-portal-visual-refresh-architecture.md#L3370),
[FR-059](../architecture/trustee-portal-visual-refresh-architecture.md#L3371) and
[FR-060](../architecture/trustee-portal-visual-refresh-architecture.md#L3372). Same gate, same
flow:

| Document text | Findings |
|---|---|
| `git show HEAD:` — pre-correction | **4** |
| Working tree — after ERRATUM 5.3 | **0** |

**A correction makes it green.** That is measured on real before-and-after prose rather than on a
fixture, which is exactly the failure mode
[`IMP-0422`](../../logs/improvement-log.jsonl) records — five prior candidates in this repository
scored the *corrected* file worse and had inverted polarity. This one does not.

**Then the register arrived, and it silences the gate completely — which is why the can-it-fail
proof cannot come from today's corpus.** Final design, all acquittals reported:

| State measured | Findings | Acquitted, and by what |
|---|---|---|
| **Today** — erratum + register | **0** | `applicationsPerDay` ← UR-001 · `exceptionalCircumstanceMix`, `exceptionalFundingSummary` ← UR-002 · `breakTypeProfile` ← UR-003 · `ethnicGroupDistribution` ← Appendix A marker |
| Fixture: register present, **document at HEAD** | 0 | the register alone acquits all four |
| Fixture: erratum present, **UR-001 deleted** | 0 | the marker alone acquits it |
| Fixture: **no erratum, no register** — the state the defect actually shipped in | **4** | none. `applicationsPerDay`, `breakTypeProfile`, `exceptionalCircumstanceMix`, `exceptionalFundingSummary` |

The last row is the can-it-fail proof and the only one that matters for the altitude call: **the gate
would have caught the exact gap the test-agent found, and nothing else in this repository would
have.** The first row is the honest description of today — green, with five suppressions printed
rather than hidden. **Assertion (f) is what stops that greenness being permanent:** the three
register entries expire 2026-09-18 and (f) fails on an expired entry.

**Assertion (f), measured.** All three entries carry the seven required fields and a valid
non-past ISO expiry, and none is stale — every `response_field` they name is still a literal null
in source. And `grep -rl undelivered_requirements scripts/` returns **nothing**: the register's own
`_undelivered_requirements_is_read_by_no_gate` key is accurate, so without (f) three owned,
dated promises would have expired in silence.

**Assertion (e), naive design: 5 findings, 2 true, 3 false — 60% wrong.** One narrowing: exclude
test files. It removes `flow-error`, `flow-failed` and `some-new-failure-mode` **by name**, all
three from `*.test.ts*` — and `some-new-failure-mode` is the fixture that proves the app tolerates
an unknown status, so the naive gate fired on the test written to demonstrate the tolerance.
Re-measured: **2 findings, 2 true, 0 false** — `error` (composed by the flow) and `pending`
(synthesised in `dataverse/roundStatistics.ts`, non-test source). Both are `IMP-0454`'s two.

### 6b — CLUSTER F: the prose gate is not merely inverted, it is BLIND

`IMP-0448` asks that no `<Description>` assert a marked column is written on the entity carrying
the marker. Measured against the two texts of the same description:

| Text | Naive-gate findings |
|---|---|
| Defective, quoted by `IMP-0448` — *"the flow writes rev_status, rev_resultjson and rev_computedon when it finishes"* | **3** |
| Corrected, on disk now — *"the flow writes rev_status, rev_resultjson and rev_computedon **on rev_roundstatisticsresult, never on the table it triggers on**…"* | **3** |

The correction *retains* the offending clause and appends the negation, which is this repository's
documented correction style. So the gate scores them identically: it cannot distinguish a false
claim from its own retraction. This is the **sixth** measured instance of the shape and the first
to score not inverted but *blind*.

**Is a value available to assert on instead?** No. The subject is prose about prose; there is no
value in the artefact to compare. Per
[`how-to-log-an-improvement`'s](../../skills/how-to-log-an-improvement.md) sibling lesson, the
honest restatement is a question about files, and the file-level question — *does anything write
this column?* — is **already answered** by the gate review 37 built. Discarded, and §7's first
question offers the one route that would create a value to assert on.

### 6c — CLUSTER C: the narrowing, and the 7 false positives it removes

`verify-assumption-markers.py` exits **0** and prints *"PASS — 14 OPEN row(s) checked … 8
unresolvable"*. The 8 split into two different defects:

| Unresolvable branch | Count | Rows | Right answer |
|---|---|---|---|
| Row **names** a `Where` target that does not resolve | **1** | `A-FIN-03` — the path is percent-encoded (`%7B…%7D` for a form GUID's braces) | **FAIL.** The file exists and carries the marker — grepped, 1 occurrence — so unquoting makes it a checked, passing row |
| Row names **no** `Where` target at all | **7** | `A-TR-1`, `A-TR-3`, `A-TR-4`, `A-TR-5`, `A-TR-8`, `A-TR-9`, `A-TR-11` | **NOTE.** Failing these turns a delivery document's open assumptions into a red build over rows with nothing to resolve |

The finding asks for *"an unresolvable target for an OPEN row is a FAILURE"*. Applied literally that
is **8 findings, 1 true, 7 false**. Narrowed to *named-but-unresolvable*, it is **1 finding, 1
true** before the unquote fix and **0** after — the fix converts a silently-skipped row into a
checked one. Review 37 change 5's rule is what forced reading the exit code first.

### 6d — CLUSTER B: why `--committed-only` is withheld, measured twice now

| Probe | Result |
|---|---|
| `git ls-files` over both round-statistics table directories | **0 tracked files** |
| Files carrying `UNUSED FROM REVISION` markers | **1**, and it is **untracked** |

So `--committed-only` on `verify-superseded-column-writers.py` yields zero marked columns, and that
gate fails on no inputs by design (`IMP-0007`'s shape, correctly). The flag would be a switch that
can only break it. **Review 37 §6d measured this same fact for the neighbouring gate one review
earlier** and concluded *"report the split, do not narrow the inputs"* — `IMP-0447` proposed the
narrowing anyway, for the adjacent gate. The scope line half needs no tracked inputs, and it is the
half that would have prevented the incident: the observing session would have read *"scope: WORKING
TREE"* in the verdict it quoted.

### 6e — why change 3 is prose and gets no gate

The check would be *"the file this finding describes was not mid-edit when it was read"*, and
nothing in a repository can see an edit in flight. The window is inherent to mutation-falsification,
which is a practice worth keeping: the mutants killed in the originating dispatch are why that
regression lock is known to be able to fail. **The response is not to mutation-test less.** It is a
second read before logging, which is free, and a scope line on the gate, which is change 2.

### 6f — CLUSTER G: the gate is right that the stamp is wrong, and its remedy would make it worse

`verify-improvement-log.py --check` is **FAILED — 1 problem**, and it is a HARD build step, so the
next build halts. The problem it names:

> `IMP-0443`: state unread, processed by `2026-08-28-improvement-review-7.md` (named in a `Cites`
> position) but `reviewed_in` still names the earlier `2026-08-28-improvement-review-6.md`.

**The detection is correct and the suggested fix is wrong.** Review 37 *cited* `IMP-0443` as
evidence in a cluster block at [L152](2026-08-28-improvement-review-7.md#L152); it did not process
it — its own header says those five *"need a keyword sent against that document, not a second review
here."* Moving the stamp to review 37 would point the reviewer at an already-applied document for a
keyword that can never arrive.

The real defect is one level up and it affects all five:

| Field | Value on all of `IMP-0440`–`IMP-0444` | True? |
|---|---|---|
| `appended_by` | `…improvement-review-6.md` | **Yes** — review 6 wrote them |
| `reviewed_in` | `…improvement-review-6.md` | **No** — `grep -c 'IMP-044[0-4]'` against review 6 returns **0** |

The two fields exist precisely to carry this distinction, documented in the gate itself at
[L439](../../scripts/verify-improvement-log.py#L439): *"`reviewed_in` says 'a review PROCESSED
this'. There was no way to say 'a review WROTE this'."* Dropping the untrue field is change 8.

**A mechanical check is available and is NOT proposed here.** `reviewed_in` could be required to
name a document that actually mentions the entry — the same grep this section ran. One instance, and
the ladder forbids a gate on one instance whose mechanism is not a platform law. §7's third question
asks whether the reviewer wants it anyway, because the cost of *not* having it is five findings
silently unprocessable, which is the expensive direction.

---

## 7. What you need to decide

**Should the stale column names come out of the shipped descriptions altogether?**

The prose gate is discarded because a `<Description>` that says *"the flow writes rev_status … on
rev_roundstatisticsresult, never on the table it triggers on"* is indistinguishable, to any regex,
from the false version it replaced. The words are all still there.

There is one route that would fix this properly: rewrite those descriptions so they **do not name
the superseded columns at all** — *"the answer is written on `rev_roundstatisticsresult`; three
retained columns below are written by nothing and read by nothing"*. Then a value gate becomes
possible, because the column name appearing in a description on its own owning entity would be the
defect.

That is an edit to shipped solution metadata under `wbs:6.9`, so it is `development-agent`'s, not
mine. My recommendation is to leave it: the descriptions are now *true*, and buying a gate by
constraining how documentation may be worded is a poor trade at one instance. Do you want it routed,
or left?

**Assertion (e) is red today. Baseline it, or hand the correction over first?**

Assertions (d) and (f) are **green** — the concurrent dispatch's erratum and register satisfied
both. Assertion (e) is **red**: `error` and `pending` are produced and §3.3 still enumerates five
values, confirmed at
[L1124](../architecture/trustee-portal-visual-refresh-architecture.md#L1124) *after* the erratum
landed, so it was not swept up by that pass.

Wiring all three HARD today halts the build on a document defect this review does not own — exactly
the situation review 37 built [`gate_baseline.py`](../../scripts/lib/gate_baseline.py) for. My
recommendation is **HARD with one baseline entry** covering assertion (e) only, owned by
`lead-agent`, expiring **2026-09-30**, clearing when §3.3 lists all seven values. That keeps every
assertion HARD rather than a warning nobody is blocked by, prints the finding on every run, and puts
a date on it.

The alternative is to hand `architect-agent` the §3.3 correction first and wire (e) after — cleaner,
but it leaves the whole extension unwired while a delivery dispatch is queued, and (d) and (f) are
green and ready now. Baseline (e), or hold the wiring?

**Do you want `reviewed_in` required to name a document that mentions the entry?**

This is the check that would have prevented five findings from being parked where no session could
reach them, and it is one grep. I have not proposed it as a change because the ladder forbids a gate
on a single instance, and I would rather ask than quietly exceed my own rules.

The argument for building it anyway: the failure is silent, self-concealing, and it *disables the
learning loop for every entry it touches* — the queue reads as handled. The argument against: one
instance, and change 8 fixes the data. Build it now, or wait for a second instance?

---

## 8. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-28-improvement-review-8.md

Findings processed: 14 unread  →  9 clusters
Regression check:   7 prior changes audited, 2 classes recurred
Proposed:           0 constraints (cap 3), 5 gates/scripts, 2 skill/knowledge edits,
                    0 agent-file edits, 0 retirements, 1 log data correction
Altitude calls:     3 generalised from instance to class, 3 left as notes, 2 proposals
                    WITHHELD on measurement, 1 altitude corrected downward,
                    1 merged into another cluster's change
Digest:             will regenerate at application — 452 entries today, 39 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 9. Applied — the record

**Approved 2026-08-28 by Xander Lykopoulos, with the three §7 decisions resolved as:** (1) baseline
the red status-value assertion HARD with a dated exception rather than holding the wiring;
(2) leave the stale column names in the shipped descriptions alone — delivery work under `wbs:6.9`,
not this review's; (3) **build the stamp-check gate now despite its single instance**, per the
exception this review flagged against its own two-instance rule.

Decision 3 adds a change the draft did not propose, so this review applied **nine** changes, not
eight. All nine are on disk.

**Re-verified before applying, per activation step 8.** The log held 452 entries and max `IMP-0455`
at draft time and the same at application; no entry carried `corrects` naming anything this review
acts on; §3.3 was still un-widened, so the baseline was still needed; the register was unchanged at
UR-001–UR-003 expiring 2026-09-18. The `verify-*.py` count was re-derived (**51**, unchanged —
change 9 went inside an existing gate rather than adding a 52nd script), so
[`improvement-agent.md` L356](../../agents/improvement-agent.md#L356) needed no edit.

| # | Landed | Proof executed |
|---|---|---|
| 1 | [`scripts/verify-tad-coverage.py`](../../scripts/verify-tad-coverage.py) — assertions **(d)**, **(e)**, **(f)** | Selftest **18 → 29 cases**, all green, 11 of them new. Corpus exit **0**; removing one baseline entry exits **1** |
| 2 | [`scripts/verify-superseded-column-writers.py`](../../scripts/verify-superseded-column-writers.py) — a scope line on every verdict | Exit 0, and the verdict now names **5 untracked inputs**. `--committed-only` withheld, measured |
| 3 | [`skills/how-to-log-an-improvement.md`](../../skills/how-to-log-an-improvement.md) — re-read a working-tree file before logging; no `corrects`/`blocker` on a transient observation | Prose. Altitude corrected downward from the finding's own proposal |
| 4 | [`scripts/verify-assumption-markers.py`](../../scripts/verify-assumption-markers.py) — percent-decode, and FAIL on a **named** unresolvable target | OPEN rows checked **14 → 15**, unresolvable **8 → 7**, exit 0. Selftest **12 → 14** |
| 5 | [`scripts/verify-role-privilege-ownership.py`](../../scripts/verify-role-privilege-ownership.py) — `distinct_removals()` | Reported count **3 → 2**, matching the script's own header. Selftest green |
| 6 | [`scripts/verify-provisioning-step-convergence.py`](../../scripts/verify-provisioning-step-convergence.py) — the marker in real bytes, in both places | The message now prints `# ── <n>. <title> ────` and is copy-pasteable. Selftest 15 green |
| 7 | [`knowledge/technology/dataverse.md`](../../knowledge/technology/dataverse.md) — the four-artefact ADR sweep checklist | Prose, deliberately. Carries the measurement that discarded the gate |
| 8 | [`logs/improvement-log.jsonl`](../../logs/improvement-log.jsonl) — the false `reviewed_in` dropped from **six** entries | `awaiting-approval` **5 → 0**, `unread` **8 → 0**. Validator **OK** |
| 9 | [`scripts/verify-improvement-log.py`](../../scripts/verify-improvement-log.py) — `check_self_stamps()`, an **ERROR** | Fired on **6 findings, 6 true, 0 false**, with 9 true negatives. Unnarrowed it was 31, of which 26 were historical |

**Findings closed incrementally, as each change landed:** `IMP-0440`–`IMP-0443`, `IMP-0447`,
`IMP-0448`, `IMP-0450`–`IMP-0455` are `APPLIED`. `IMP-0451` carries a `reobserved` record at V2.
`IMP-0444` (routed to `development-agent`) and `IMP-0449` (V3, needs a DEV query) stay open with a
re-verified reason and a trigger. Digest regenerated last and once: **455 entries, 454 lessons, 37
recurring classes.**

### Deviation 1 — the draft promised two new findings and three were appended

`IMP-0458` was not planned. Change 1's first implementation reported **0 null response keys against
a flow containing 8**, and its second reported 0 again for a different reason. Both exited 0. The
only thing that caught either is the rule that a gate reporting 0 findings against a corpus known
to contain an instance is the tell — the 8 had been measured with a throwaway probe *before* the
gate was written, which is what gave the 0 something to be wrong against. Recorded because the two
Power Automate traps are reusable: a recursive `actions` walk misses an action nested in a Scope
inside a condition, and brace-matching must take the **narrowest** enclosing block, because the
outermost is `properties` and always matches.

### Deviation 2 — change 9 caught this document, on its first run

Appending `IMP-0456`–`IMP-0458` with both `appended_by` and `reviewed_in` naming this review, while
this document did not yet mention them, is **exactly** the defect change 9 exists to catch. It went
red on all three immediately.

The remedy taken was the *other* one, and the distinction is the point: for the five entries in
change 8 the stamp was false and was dropped, because review 36 never processed them. For these
three the stamp is **true** — this review did process them — so the document was corrected to name
them, in §5. Both routes clear the gate; only one is honest in each case, and the gate cannot tell
you which. It tells you the pair disagrees.

### Deviation 3 — the corpus moved a fourth time, and assertion (f) went red on real ground truth

**A delivery dispatch implemented FR-058, FR-059 and FR-060 while this review was applying.** The
flow now composes `applicationsPerDay`, `exceptionalCircumstanceMix`, `exceptionalFundingSummary`
and `breakTypeProfile` from real actions — `Compose_applications_per_day`,
`Compose_exceptionalcircumstance_categories`, `Compose_exceptional_funding_summary`,
`Compose_breaktype_profile` — read directly, not inferred.

So [`UR-001`–`UR-003`](../../contract/tad-deferrals.json) are now **dead promises**, and
`verify-tad-coverage.py` exits **1** with exactly 4 violations, **all of them assertion (f)**;
(d) and (e) are clean. **That is the assertion working, on live ground truth, within an hour of
existing** — before it, no file under `scripts/` read that register at all, so three satisfied
entries would have sat until their 2026-09-18 expiry and then failed for the wrong reason.

**Not fixed here, and deliberately not baselined.** Deleting a satisfied deferral is the register's
own documented remedy (`_stale_entries_fail`), and a baseline is for debt that needs a date — the
wrong instrument for tidy-up that should happen today. Both files are delivery- and
architecture-owned under [`C-COM-002`](../../constraints/commercial/commercial-constraints.md#L35),
and the flow's `.json`, `.data.xml` and `notes.md` were **all** still `M` in `git status` when this
was written, which by change 3's own new rule is a tree mid-edit and not a settled state. Acting on
another dispatch's uncommitted work is the defect that rule exists to prevent.

**Logged as [`IMP-0459`](../../logs/improvement-log.jsonl)**, left open with a re-verified reason
and a trigger. Appendix A also now overclaims in the **opposite** direction — 2 rows still read
`UNDELIVERED` for fields that have a producer — which is `IMP-0451`'s defect with the sign
reversed, and acceptance reads that table. `IMP-0451`'s `reobserved` record was amended in place
rather than left standing, because its *"declared in two places"* clause would otherwise have
become a misleading statement in the durable record of a closed finding.

**The remaining red is a two-minute fix by the owning agent:** delete three register entries,
correct three Appendix A rows, and the step goes green.

### What this review is evidence of

**Two of the nine changes were narrowed by something other than my own judgement, and both
narrowings removed named false positives.** Change 1's design went from 9 findings / 4 true to 4
findings / 4 true because the measurement forced three narrowings. Change 4's failure branch was
too broad, and the thing that caught it was an **existing fixture** asserting the old behaviour —
`a-Where-column-naming-no-real-file-is-a-note-not-a-failure` — not the real corpus, which reaches
that branch nowhere. Fixtures and corpus answer different questions, and this review needed both to
get either change right.
