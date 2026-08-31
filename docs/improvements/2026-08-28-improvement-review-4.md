# Improvement Review 34 — 2026-08-28

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 16 `unread` → 8 clusters
**Trigger:** two unread `blocker` entries — `IMP-0406` and `IMP-0410`
([`agents/WORKFLOW.md` L254](../../agents/WORKFLOW.md#L254), *"immediately — do not batch"*), inside a
dispatch scoped to the remainder after review 33. Dispatched at
[`logs/routing.log` L329](../../logs/routing.log#L329).
**Gate:** `APPROVE IMPROVEMENTS`
**Status:** **APPLIED 2026-08-28** — reviewer approved as drafted in full; all 16 changes are on
disk. §10 carries the applied record, the six deviations forced at application, and the one thing
this dispatch could **not** confirm.
**Scope note:** 16 of the 58 `unread` entries, and the boundary is mechanical rather than chosen.
[Review 33](2026-08-28-improvement-review-3.md) processed 43 of them and is parked at its own gate; its
own §5 excluded exactly this set. `IMP-0382` is **also excluded** — review 33 gives it a recorded
deferral and a `revisit_when` pairing it with `IMP-0401`, so a second answer here is the churn the
anti-bloat limits exist to prevent. The 53 `reviewer-deferred` entries are untouched, per activation
step 2.
**Concurrency:** the `architect-agent` erratum dispatch at
[`logs/routing.log` L328](../../logs/routing.log#L328) **completed while this review was being
written**. It changed two of this review's dispositions and appended two further findings —
`IMP-0418` and `IMP-0419` — which are folded in here rather than left for a fifth review, because
they are about the very document this review was measuring. The log went from 414 to 416 entries
mid-draft. §6 carries every re-measurement, and activation step 8 re-measures again before anything is
applied (`IMP-0080`, `IMP-0405`).
**WBS:** fourteen of the sixteen findings carry `wbs:6.9`. The review itself is system work, not
billable ([`C-COM-002`](../../constraints/commercial/commercial-constraints.md#L35)). No contracted
figure is restated (D-3, [`C-COM-004`](../../constraints/commercial/commercial-constraints.md#L37)).

---

## Summary

**Sixteen changes, no new rules.** The constraint budget is untouched — 0 of 3 — because every cluster
resolved to a script, a knowledge line, or one amendment to an existing rule whose current wording
already carries the mechanism and stops one step short of it.

**Both blockers are disposed of, and neither needed a rule I had to invent.** The gate blocker
(`IMP-0410`) becomes a shared helper plus a regression lock, proven by materialising the real defect
rather than a fixture. The document blocker (`IMP-0406`) was **resolved by delivery while this review
was open**, so what remains is the knowledge line.

**Five of this review's own designs measured wrong and were rebuilt or discarded before reaching this
document.** One gate scored a *corrected* file worse than the *defective* one. One measured 71% false
because it inferred across a 47-member class bucket. Two measured 100% false. The fifth measured 24 raw
findings and at best one true. §6 carries all five with the numbers — and together they establish a
result worth more than any single change here: **a prose-proximity gate cannot tell an assertion from
its own retraction in this repository's documentation style, and four measured attempts across two
reviews now say so.**

**Approving this does not unblock the build.** 43 entries stay `unread` until review 33 is approved, so
[`C-TECH-061`](../../constraints/technology/technology-constraints.md#L131) stays red on the batch
trigger regardless of what happens here. §5 says so plainly.

---

## 1. Regression check — did the last review's changes work?

**Review 32 is the last review actually on disk** ([its applied record](2026-08-28-improvement-review-2.md#L436)),
and it proposed **no rule changes at all** — two recorded deferrals, a digest regeneration, and one
appended finding. So there is no rule of its making that can have failed, and the audit below is of its
*dispositions*. Review 33's audit of review 31's six changes is not re-derived here; it is parked at its
gate and re-deriving it is `IMP-0183`'s defect.

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| 1 — `IMP-0398` deferred, approved wording applied verbatim | 2026-08-28 | `dispatched-below-required-tier` | **NO** — no new instance in these 16 | Holding. The generated self-check clause at [`generate-subagents.py` L214](../../scripts/generate-subagents.py#L214) caught the original; nothing new occurred for it to catch |
| 2 — `IMP-0401` deferred, **one clause corrected** at application | 2026-08-28 | `gate-scope-mismatch` | **YES — `IMP-0410`** | **Working, and on a different rung.** `IMP-0401` is a document describing a gate's reach; `IMP-0410` is a gate's own input glob. Nothing review 32 wrote could reach the second. Cluster A takes it |
| 3 — digest regenerated | 2026-08-28 | read path | n/a | Current, and regenerated **again** by the erratum session mid-draft — 416 entries |
| 4 — `IMP-0405` appended about review 32 itself | 2026-08-28 | `declared-policy-not-mechanically-enforced` | **it IS the recurrence** | Cluster G takes it. The finding records that the control fired as designed and that its *framing* is narrow — a proposal, not a failure |

**The load-bearing row is row 2, and the reason matters.** `gate-scope-mismatch` now stands at **x4**
([digest L55](../../logs/known-failure-modes.md#L55)) and every prior instance was *a document
describing a gate wrongly*. `IMP-0410` is the first where **the gate itself selects the wrong inputs**,
and its verdict is inverted between this Mac and CI. Same class name, different property — which is why
cluster A builds a mechanism instead of correcting a sentence.

**And `IMP-0405`'s own lesson came true against this review, twice.** Its point is that a review's
evidence goes stale in the interval between drafting and approval. Between my first measurement pass and
this draft closing, the erratum landed and two entries were appended. Both are handled in-line rather
than described in a scope note that would have been false by the time it was read.

**One residual of review 32 is cleared here rather than left standing.** Its closing note records six
citations left unstamped on instruction, `IMP-0405` among them. This review processes and stamps it.

---

## 2. Clusters and promotion decisions

```
CLUSTER A: gate-scope-mismatch — a HARD gate's verdict depends on a file the repository IGNORES
           (x4; x1 here: IMP-0410, blocker)
Altitude:  CLASS. Fourth instance of the class, and the FIRST in which the gate's own input
           selection is the defect rather than a document's description of it. An instance patch
           is forbidden (how-to-promote-a-finding.md L44).
Ladder row: "A tool could catch it mechanically -> a script plus a build gate" (L20), plus
           "second instance -> generalise: replace a hand-maintained list with a derivation" (L22).
Becomes:   change 1 — scripts/lib/tracked_paths.py, one helper that globs and then EXCLUDES
           whatever `git check-ignore` claims, REPORTING each exclusion by name rather than
           silently narrowing the input set. change 2 — verify-audited-tables.py calls it, keeping
           its own empty-input-set failure intact. change 3 —
           scripts/verify-gate-input-tracking.py, a meta-gate that AST-extracts every glob literal
           under scripts/ (module constants resolved), expands the anchored ones, and fails if any
           result is ignored.
Retires:   nothing, and the one candidate is declared and REJECTED in section 4 —
           verify-toolchain-claims.py L190's hardcoded `node_modules` filter is the hand-typed
           form of exactly this derivation, and replacing it would add a subprocess call over 625
           paths for no behavioural change.
Cites:     IMP-0410.
Residual:  THREE, and the first limits the gate most.
           (1) The AST parse resolves module-level string constants and inline literals only, so
           26 UNANCHORED patterns (a bare `*` applied to a base computed at runtime) are skipped
           as unresolvable. The meta-gate covers ANCHORED patterns. A coverage gap, not a false
           positive, stated because the gate will read as more complete than it is.
           (2) Once change 2 lands, verify-audited-tables.py declares its own handling and the
           meta-gate SKIPS it — so the lock protects FUTURE gates and no longer its own founding
           instance. Reported as a regression lock in section 6, never as coverage.
           (3) Two gates legitimately read ignored paths — verify-build-manifest-note.py over
           build/artifacts (931 files, 909 ignored, by design) and verify-toolchain-claims.py.
           A blanket exclusion everywhere would EMPTY the first one's input set and, under its own
           no-inputs rule, fail it. The helper is therefore opt-in, which is a real weakness:
           nothing forces a new gate to call it.
```

```
CLUSTER B: gate-reassures-wrongly — a build config asserts its OWN step is expected to fail
           (x19; x1 here: IMP-0414)
Altitude:  CLASS for the mechanism, INSTANCE for the sentence (already corrected on disk).
Ladder row: "A tool could catch it mechanically" (L20).
Becomes:   change 4 — verify-build-config.py rejects a step whose comment block asserts the step
           currently fails, unless that block is a retraction, and points the author at
           contract/known-exceptions.json, where a deliberately-red gate carries an owner, a
           clearing action and a dated expiry that verify-wbs-chain.py already enforces.
Retires:   nothing.
Cites:     IMP-0414.
Residual:  The retraction guard is a phrase list. A future correction worded outside it is a false
           positive; an assertion avoiding the red phrases is a false negative. Both declared,
           because the NAIVE form of this check scored the CORRECTED file WORSE than the defective
           one (section 6) — a polarity inversion, the most dangerous shape a gate can have, and
           only the measurement found it.
```

```
CLUSTER C: platform-state-divergence — a source-versus-live reconciliation that ran in ONE
           direction (x11; x2 here: IMP-0407, IMP-0408)
Altitude:  CLASS. Two findings, one property: the diff that was owed was never run both ways.
           IMP-0407 is a removal nobody diffed for; IMP-0408 is a diff whose direction a document
           predicted wrongly.
Ladder row: "A platform law, or a third instance -> a constraint row" (L23) for IMP-0407, amending
           in place rather than adding a row; L19 for IMP-0408.
Becomes:   change 5 — C-TECH-042's convergence clause is AMENDED, not duplicated: a privilege
           REMOVED from a role's source obliges a named per-environment revoke step plus a live
           read-back asserting ABSENCE, because the create-only provisioning path cannot converge
           on a removal. Its rationale carries IMP-0418's safety fact, because that is where a
           future revoke gets designed. change 6 gives it a mechanically executable Verify By.
           change 7 — how-to-verify-a-platform-contract.md gains a "reconciling a hand-edited live
           artefact" step: export + unpack, flatten both action graphs to a path-keyed map, strip
           the three designer-only keys observed here, and report only-in-live, only-in-source AND
           changed-in-both separately.
Retires:   nothing. C-TECH-042 already carries the create-only-cannot-converge reasoning for
           ATTRIBUTES (IMP-0259); this extends the same clause to ROLE PRIVILEGES. A new row
           beside it would leave the narrower wording running, which is review 33's C-DOM-001
           reasoning applied to a second rule.
Cites:     IMP-0407, IMP-0418 (changes 5, 6), IMP-0408 (change 7).
Residual:  TWO. (1) The read-back half authenticates to a live environment, which
           agents/improvement-agent.md L318 puts outside this agent's authorship entirely — the
           requirement is handed over, the script is not written here. So change 6 checks the
           SOURCE-side obligation (a declared removal has a sequenced revoke) and can never prove
           the environment converged. (2) IMP-0407's own INSTANCE is closed by delivery, not by
           this review — section 6.
```

```
CLUSTER D: platform contracts and capabilities, ground-truthed
           (platform-contract-guessed-not-groundtruthed x48, platform-fact-groundtruthed x27;
           x5 here: IMP-0406 (blocker), IMP-0409, IMP-0417, IMP-0354, IMP-0411)
Altitude:  KNOWLEDGE — five single instances, each with a general cause and no mechanical surface
           that does not require live access.
Ladder row: "One instance, but the cause is general and a human needs to know it" (L19), and
           "a capability was established and could be lost again" (L21) for IMP-0409/IMP-0417.
Becomes:   change 8 — power-automate.md records the FULL callbackregistration.message enumeration
           with its live provenance, placed beside the existing runas 3-not-4 note, because they
           are the same defect shape: a trigger parameter whose wrong value packs, imports and
           reports Activated while registering nothing that fires. It also records the
           export+unpack recipe for capturing a live flow definition and the stringmap recipe for
           reading any picklist's real enumeration. change 9 — code-apps.md records the
           entity-set/table/binding ordering constraint and the sanctioned --allow escape, naming
           both forbidden shortcuts. change 10 — accessibility-checklist.md gains a brand-asset
           licence step. change 11 — provisioning/README.md pins Pester 5.7.1 and names all three
           affected files rather than leaving the set open.
Retires:   nothing.
Cites:     all five.
Residual:  IMP-0406's TAD half is RESOLVED BY DELIVERY and is NOT re-proposed here — section 6.
           And a knowledge file is read by whoever opens it: the digest renders these lessons
           behind per-section caps (29 hidden in the platform-authoring section alone,
           digest L170), which is review 33's cluster H and not mine to fix twice.
```

```
CLUSTER E: finding-diagnosis-unverified — a recorded conclusion that nothing ever VARIED
           (x8; x3 here: IMP-0412, IMP-0413, IMP-0415)
Altitude:  KNOWLEDGE for IMP-0413, SKILL for IMP-0415, DEFERRED for IMP-0412.
Ladder row: L19, and "an argued mechanism in place of a confirmed one" is the named exclusion at
           L153 that governs all three.
Becomes:   change 12 — build-and-deploy.md and the build config comment stop attributing
           `pac solution check --outputDirectory` writing nothing to this repository's spaces in
           its path. IMP-0413 tested it on a path with NO spaces and the behaviour is
           unconditional. The OPERATIVE rule is unchanged and still right — read the result from
           stdout — so only the CAUSE is corrected. change 13 — how-to-review-code.md gains two
           lines, one of them cluster F's.
Retires:   nothing, but one LESSON is corrected in place: change 15 sets `corrects` on IMP-0010,
           which carries the identical wrong cause and which IMP-0413 names without pointing at.
Cites:     IMP-0413 (changes 12, 15), IMP-0415 (change 13), IMP-0412 (deferral, section 5).
Residual:  THREE. (1) IMP-0413's proposed target was knowledge/technology/platform.md, which does
           not contain the claim at all; the claim lives in two other files, and change 12
           corrects the finding's own target. (2) IMP-0412 is NOT duplicated: review 33's change
           12 already writes the if() contradiction into power-automate.md, and settling it needs
           one live designer run nobody here can make. (3) The mechanical form of this cluster —
           inferring from a `corrects` field which SIBLING lessons are also wrong — measured 7
           findings, 1 true, 5 false and is NOT BUILT (section 6).
```

```
CLUSTER F: test-coupled-to-absolute-counts — a count assertion structurally blind to ADDITIONS
           (x21; x1 here: IMP-0416)
Altitude:  SKILL. Twenty-first instance of the class and, as the finding establishes, the FIRST
           that fails by staying GREEN — every prior instance announced itself by going red on a
           legitimate change, which is how all twenty were found.
Ladder row: L19, on the finding's own reasoning that a 21st per-file correction is the wrong
           altitude.
Becomes:   change 13's second line — for every count assertion, the review asks which DIRECTION of
           change it can detect. A count taken from the test's own enumeration detects removals
           only, which is the weaker half and usually not the half anyone wanted.
Retires:   nothing.
Cites:     IMP-0416.
Residual:  Static detection was built and measured at 4 findings, 0 true, 4 false, and the one
           real instance was INVISIBLE because delivery had already corrected it (five -> seven).
           Not built; section 6 carries the numbers. So this class keeps a checklist question and
           no gate, on measurement grounds rather than on principle.
```

```
CLUSTER G: declared-policy-not-mechanically-enforced — a review proposing NO changes still carries
           perishable evidence (x18; x1 here: IMP-0405)
Altitude:  AGENT-FILE, and it is this agent's own file.
Ladder row: "An agent had the information and still did the wrong thing" (L24). The control DID
           fire; what is narrow is the wording it fired against.
Becomes:   change 14 — activation step 8 gains one clause: a review proposing no changes
           re-verifies the factual clauses of every deferred_reason it is about to write, and
           applies the approved revisit_when VERBATIM even when part of it has become satisfied,
           annotating the state in deferred_reason instead.
Retires:   nothing.
Cites:     IMP-0405.
Residual:  Prose, and deliberately so: nothing can diff a sentence against a tree. IMP-0405's own
           proposal says the same and rules out a script. The standing control remains a human
           reading the draft, which is what caught it this time — and this review is the second
           consecutive one to hit the same hazard, which is the evidence the clause is worth
           having.
```

```
CLUSTER H: a fact RESTATED instead of CITED cannot follow a change made where it was decided
           (baseline-restated-not-cited x5, approved-document-internally-inconsistent x16;
           x2 here: IMP-0418, IMP-0419)
Altitude:  CLASS. Two findings appended by the erratum dispatch, and they are one property seen
           from two sides: IMP-0418 is a dispatch BRIEF that restated a privilege+role fact and
           swapped the role; IMP-0419 is a DOCUMENT whose executable sections restated a privilege
           set as a literal list, so they did not follow the withdrawal decided upstream. Both are
           the mechanism C-COM-008 already forbids for baseline figures.
Ladder row: "An agent had the information and still did the wrong thing -> an agent-file or skill
           edit" (L24). NOT a constraint: nothing can read a dispatch brief, and the
           document-internal gate IMP-0419 proposes measured 23 of 24 findings false (section 6),
           so a constraint here would fail anti-bloat limit 4 — an unverifiable Verify By is a
           comment.
Becomes:   change 16 — how-to-document-architecture.md: an EXECUTABLE section (prerequisites,
           rollout steps) CITES the section that decides rather than restating it; withdrawing an
           identifier is a whole-document grep, checking the sections that EXECUTE separately from
           the sections that ARGUE; and a privilege named anywhere carries its ROLE and its source
           line, because the role is the half compression swaps.
Retires:   nothing.
Cites:     IMP-0418, IMP-0419.
Residual:  TWO, and the first is a dependency. (1) Review 33's change 8 adds a closely related
           rung to agents/lead-agent.md — "a brief stating another document's revision or status
           quotes the line it read" — and IMP-0418 is a second instance of exactly that property
           with a different subject. If review 33 is approved first, change 16 should be read
           beside it rather than duplicating it; nothing here edits lead-agent.md, deliberately.
           (2) The class approved-document-internally-inconsistent reaches x16 with NO gate of any
           kind, and this review adds none. That is now the second consecutive review to measure a
           gate for it and decline to ship one, and the reason is the same both times.
```

---

## 3. Proposed changes

| # | Type | Target | Change | Cites | Mechanically verifiable? |
|---|---|---|---|---|---|
| 1 | script | `scripts/lib/tracked_paths.py` (new) | One helper: glob, then exclude every result `git check-ignore` claims, **reporting each exclusion by name** rather than silently narrowing. Callers keep their own empty-input-set failure | IMP-0410 | **YES** — `--selftest`, plus section 7's corpus figures |
| 2 | script | [`scripts/verify-audited-tables.py` L55](../../scripts/verify-audited-tables.py#L55) | `SETTINGS_GLOB` resolves through change 1, so the HARD `audited-tables` step stops depending on whether a crashed Pester run left a fixture behind. The [L203](../../scripts/verify-audited-tables.py#L203) no-inputs failure is untouched | IMP-0410 | **YES** — proven by materialising the real fixture, section 6 |
| 3 | script | `scripts/verify-gate-input-tracking.py` (new) + a `gate-input-tracking` step | AST-extracts every glob literal under `scripts/` (module constants resolved), expands the anchored ones, and FAILS if any result is gitignored. Scripts declaring their own ignore handling are skipped **and named** | IMP-0410 | **YES** — `--selftest`, and the preflight recognises any `scripts/verify-*.py` step as a gate ([`is_gate()` L368](../../scripts/verify-build-config.py#L368)) |
| 4 | script | [`scripts/verify-build-config.py` L368](../../scripts/verify-build-config.py#L368) | Reject a step whose comment block asserts the step currently fails, unless that block is a retraction; point the author at `contract/known-exceptions.json` instead | IMP-0414 | **YES** — `--selftest`, plus the real pre-correction version in git, section 6 |
| 5 | constraint-amendment | [`C-TECH-042`](../../constraints/technology/technology-constraints.md#L84) | The convergence clause extends from attributes to **role privileges**: a privilege removed from role source obliges a named per-environment revoke plus a live read-back asserting ABSENCE. `ensure-schema.ps1` declares the gap in its own [L748](../../provisioning/dataverse/ensure-schema.ps1#L748) convergence line. Rationale records **which** privilege is deliberately live on **which** role, because revoking the wrong one breaks Refresh Figures for every trustee | IMP-0407, IMP-0418 | **YES** — change 6 is the executable half |
| 6 | script | [`scripts/verify-role-privilege-ownership.py` L135](../../scripts/verify-role-privilege-ownership.py#L135) | Every privilege a role file declares REMOVED in its own source must have a sequenced revoke step. Parses `<RolePrivilege>` elements, never greps — a privilege named inside a comment is `IMP-0020`'s trap and this one file carries four such comments | IMP-0407 | **YES** — measured 1 finding, 1 true, 0 false, section 7 |
| 7 | skill | [`skills/how-to-verify-a-platform-contract.md` L205](../../skills/how-to-verify-a-platform-contract.md#L205) | A "reconciling a hand-edited live artefact" step in the ground-truth section: `pac solution export` + `unpack`, flatten both action graphs to a path-keyed map, strip the three designer-only keys, report **all three** difference directions. A document's account of a designer session is evidence about one direction only | IMP-0408 | N/A — instruction change |
| 8 | knowledge | [`knowledge/technology/power-automate.md` L199](../../knowledge/technology/power-automate.md#L199) | The full `callbackregistration.message` / `subscriptionRequest/message` enumeration with live provenance, beside the existing `runas` 3-not-4 note; plus the export+unpack recipe for a live flow definition and the `stringmap` recipe for any picklist's real mapping, with the `pac env fetch` truncation trap named as the thing not to try | IMP-0406, IMP-0409 | N/A — reference material |
| 9 | knowledge | [`knowledge/technology/code-apps.md` L146](../../knowledge/technology/code-apps.md#L146) | Registering an entity set, creating the table, and binding the app are three steps in a fixed order, and the middle one is a live action no build can perform. The sanctioned response is `--allow ENTITY=REASON`; both forbidden shortcuts are named, because both look like the obvious fix | IMP-0417 | N/A — reference material |
| 10 | skill | [`skills/accessibility-checklist.md` L27](../../skills/accessibility-checklist.md#L27) | Before shipping a font file, confirm a **web-embedding** licence exists for it — an Office/Microsoft 365 bundled font is licensed for device install and document embedding, not for a site to serve. Name-only in the stack with a system fallback chain is the default, and the substitution is recorded rather than made silently | IMP-0354 | N/A — instruction change |
| 11 | knowledge | [`provisioning/README.md` L109](../../provisioning/README.md#L109) | The Automated tests section states `Import-Module Pester -RequiredVersion 5.7.1` before `Invoke-Pester`, and names all **three** affected files — including `EnsureSchema.Tests.ps1`, the one the TAD's own rollout sequence depends on | IMP-0411 | N/A — reference material |
| 12 | knowledge | [`knowledge/technology/build-and-deploy.md` L257](../../knowledge/technology/build-and-deploy.md#L257) | Stop attributing `--outputDirectory` writing nothing to this repository's spaces in its path — tested 2026-08-28 on a path with none, the behaviour is unconditional. Corrects [L403](../../knowledge/technology/build-and-deploy.md#L403) and the build config comment at [L1231](../../config/revitalise-grant-automation-build.yml#L1231) too. The operative rule is unchanged | IMP-0413 | **Partly** — no gate reads prose; the claim is checkable by re-running the test the finding ran |
| 13 | skill | [`skills/how-to-review-code.md` L60](../../skills/how-to-review-code.md#L60) | Two lines. (a) Where a TAD or Dev Summary claims a defect class is structurally **inexpressible**, that claim is a testable assertion and gets one mutation proving the suite catches it. (b) For every count assertion, ask which DIRECTION of change it can detect | IMP-0415, IMP-0416 | N/A — instruction change |
| 14 | agent | [`agents/improvement-agent.md` L128](../../agents/improvement-agent.md#L128) | Activation step 8 gains one clause: a review proposing **no** changes still re-verifies the factual clauses of every `deferred_reason` it is about to write, and applies an approved `revisit_when` verbatim even when part of it has come true | IMP-0405 | N/A — instruction change |
| 15 | other | [`logs/improvement-log.jsonl`](../../logs/improvement-log.jsonl) | One-line repair: `corrects` is set on `IMP-0010` as well as `IMP-0079`, so the digest's correction marker reaches **both** entries carrying the disproved space-in-path cause | IMP-0413 | **YES** — `verify-improvement-log.py --check`, and the marker renders as it already does at [digest L290](../../logs/known-failure-modes.md#L290) |
| 16 | skill | [`skills/how-to-document-architecture.md` L89](../../skills/how-to-document-architecture.md#L89) | An **executable** section (prerequisites, rollout steps) CITES the section that decides rather than restating it. Withdrawing an identifier is a whole-document grep, checking sections that EXECUTE separately from sections that ARGUE. A privilege named anywhere carries its ROLE and its source line | IMP-0418, IMP-0419 | N/A — instruction change |

**Constraint budget: 0 of 3 used.** Change 5 amends
[`C-TECH-042`](../../constraints/technology/technology-constraints.md#L84) rather than adding a row, and
that is substantive rather than a budget trick: the row already carries the create-only-cannot-converge
reasoning for attributes, and its own rationale records that applying it found the founding blocker's
premise too narrow. A sibling row for role privileges would leave the narrower clause running beside it,
which is the duplicate-coverage outcome
[`constraints/README.md` L139](../../constraints/README.md#L139) forbids. Cluster H's constraint
proposal is **declined on measurement**, not on budget — see section 6.

---

## 4. Retirements

**No retirements, and the audit ran.** Derived, never typed — **10 retired, 80 live** — via
`grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l` and its live-row twin
([`agents/improvement-agent.md` L278](../../agents/improvement-agent.md#L278)).

> Retirement check performed: 90 constraint rows reviewed, none currently redundant, because this
> review adds no general gate that supersedes an existing row — change 5 *strengthens* a row rather
> than replacing one, and changes 1–4 and 6 create coverage where there was none.

**One non-constraint candidate was considered and rejected, and it is the interesting one.**
[`verify-toolchain-claims.py` L190](../../scripts/verify-toolchain-claims.py#L190) filters
`node_modules` by a hardcoded string — the hand-typed form of exactly the derivation change 1
introduces, which is
[`C-TECH-067`](../../constraints/technology/technology-constraints.md#L137)'s own rule. **Not retired.**
It is correct today, it is a list of one, and routing 625 paths through `git check-ignore` on every run
would buy no behavioural change. Naming it matters anyway: if a second hardcoded exclusion appears in
that file, the derivation becomes the cheaper option and this paragraph is the record of why it was
deferred.

---

## 5. Findings left unprocessed, and what you need to decide

No silent caps. 16 of 58 `unread` processed; 44 excluded by a mechanical boundary, 2 deferred with
triggers, and 5 closed only as far as the evidence reaches.

| Finding | Class | Why not processed here | Revisit when |
|---|---|---|---|
| The 43 entries `IMP-0345`…`IMP-0404` | various | [Review 33](2026-08-28-improvement-review-3.md) processed all 43 and is parked at its own gate. They read `unread` only because a review cannot stamp before its own approval — see the decision below. Re-deriving them is `IMP-0183`'s defect exactly | Review 33 receives `APPROVE IMPROVEMENTS` |
| `IMP-0382` | `gate-scope-mismatch` | Review 33 already gives it a recorded deferral and a `revisit_when` pairing it with `IMP-0401`. Its own `proposed_change` is `none` | With `IMP-0401`, per review 33 |
| `IMP-0412` | `finding-diagnosis-unverified` | Review 33's change 12 **already writes** the `if()` contradiction and the safe-under-either pattern into `power-automate.md`. A second independent knowledge edit for the same fact is duplicate coverage; settling which semantics is right needs one live designer run | A flow is next opened in the designer and the one-line experiment is run — an `if()` whose untaken branch divides by zero |
| Five findings closed only to their evidence | various | `IMP-0406` (V5), `IMP-0407` (V3), `IMP-0411`, `IMP-0415` (V4) and `IMP-0419` (V3) carry defects whose re-observation needs a live environment or a signed-in user. Their changes land; the entries keep a `deferred_reason` rather than a closure nobody tested ([`C-TECH-053`](../../constraints/technology/technology-constraints.md#L108), `IMP-0224`) | Section 6 names what is already re-observed and by whom; the rest needs a live session |
| 53 `reviewer-deferred` | various | Each carries an accepted `deferred_reason`; activation step 2 says leave them. One, `IMP-0274`, still has no `revisit_when` | A review scoped to the deferred queue |

**Handed to delivery with named owners — none needs your decision.** (i) The two gates that read
gitignored paths **by design** — `verify-build-manifest-note.py` over `build/artifacts`, and
`verify-toolchain-claims.py` — must NOT adopt change 1's helper; owner `build-agent`, and change 3 skips
both by construction. (ii) `src/code-apps/trustee-review-portal/src/dataverse/client.test.ts` still
hand-types its entity-set count (now seven) because it cannot derive without importing a private map;
the comment now records the hazard, and deriving it properly is owner `frontend-agent`. (iii) The two
`post_deploy` `$ref` deletes and their absence read-backs that Erratum 5.1 sequenced are owner
`pipeline-agent`, and they are **expected to fail on first run** — that is the design.

**One commercial note, and it is `commercial-agent`'s.** Fourteen of these sixteen findings carry
`wbs:6.9`, a change-order-covered id absent from the 61 baselined tasks — the same observation review 33
flagged. Nothing here restates a figure
([`C-COM-002`](../../constraints/commercial/commercial-constraints.md#L35) is not this agent's to apply).

### What you need to decide

**Nothing blocks this review.** Every finding in scope resolved to a change, a recorded deferral with a
trigger, or a handover with an owner.

**One genuine judgment call: a parked review leaves 43 entries reading "nobody has looked at these".**
The log gate says exactly that about 43 entries a full strategic-tier pass has already analysed, and the
batch trigger re-fires against them on every check. The `awaiting-approval` state exists for this and is
set by `reviewed_in`, but by convention a review writes nothing to the log until its keyword arrives —
so the state is reachable in principle and unused in practice.

Stamping `reviewed_in` at **draft** time would fix it, because that field records only that a review
*read* the entry, which is true the moment the draft names it. The trade-off is real: it makes every
future review write to a shared append-only log earlier, and two live sessions on this synced path is
the `IMP-0080` hazard — a hazard this very session met twice. It would **not** clear either blocker
trigger; [`verify-improvement-log.py` L123](../../scripts/verify-improvement-log.py#L123) counts
`awaiting-approval` alongside `unread` for blockers, deliberately.

I have **not** proposed it as a change, because it alters when every future review touches the log and
no finding in my sixteen asked for it. **Do you want it drafted as its own review?** The finding
recording the observation is one of the two this review appends about itself.

**Two things worth your eye rather than your decision.** Change 3's meta-gate finds nothing today, and
is reported as a lock rather than as coverage — its founding instance was deleted before this dispatch
opened, so I proved it can fail by recreating the real fixture rather than trusting one I wrote. And
neither blocker's live exposure is closed by approving this: `IMP-0407`'s stale privilege is still bound
Global in DEV, and a human with the right credential has to run the revocation the TAD now sequences.

---

## 6. Where this review's own premises were measured, and five of them failed

Stated before the verification table, because a review that buries its disproved premises is the defect
it exists to remove ([`agents/improvement-agent.md` L342](../../agents/improvement-agent.md#L342)).

**The result that outlives every change here: four measured attempts now say a prose-proximity gate
cannot tell an assertion from its own retraction.** Review 33 measured one at 7 findings, 0 true, 7
false. This review measured three more — cluster B's naive form, cluster E's sibling inference, and
cluster H's privilege-pair check at 24 raw findings — and every false positive had the same shape: the
old wording surviving inside the correction that withdraws it, or a negation the pattern could not read.
This repository's documentation style makes it worse, because a delta TAD deliberately *retains*
superseded text with a supersession note rather than deleting it. A future review proposing a fifth
attempt should read this paragraph first: assert on **values**, not on phrases.

**The erratum landed mid-review and resolved both halves of one blocker, so nothing is proposed for
it.** When this dispatch opened, the TAD carried `subscriptionRequest/message: 2` at three places and
`A-R49` named one stale privilege. Re-measured at close: the value is **3** at
[L1458](../../docs/architecture/trustee-portal-visual-refresh-architecture.md#L1458),
[L246](../../docs/architecture/trustee-portal-visual-refresh-architecture.md#L246) and
[L3172](../../docs/architecture/trustee-portal-visual-refresh-architecture.md#L3172); `A-R49` names
**two** privileges at
[L2991](../../docs/architecture/trustee-portal-visual-refresh-architecture.md#L2991) with an absence
read-back row at
[L3123](../../docs/architecture/trustee-portal-visual-refresh-architecture.md#L3123); and the flow
source itself carries `"subscriptionRequest/message": 3` at
[L39](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json#L39).
The only surviving `message: 2` is the erratum's own record of what was wrong. So `IMP-0406` and
`IMP-0407` are **resolved-by-delivery on their document halves**, exactly as the dispatch instruction
anticipated, and this review proposes only their durable knowledge and constraint halves.

**Cluster B's gate scored the CORRECTED file worse than the DEFECTIVE one.** The naive phrase match
returned **2 findings on the working tree and 1 on `git show HEAD:`** — a polarity inversion, because
the correction at [`build.yml` L888](../../config/revitalise-grant-automation-build.yml#L888) quotes the
old sentence in order to withdraw it, and quotes it twice. Total naive: **3 findings, 1 true, 2 false.**
One narrowing — skip a comment block containing a retraction marker — removes both false positives **by
name** (L888's quoted sentence; L891's *"whose config says it is EXPECTED to be red"*) and leaves the
true positive standing at HEAD's L886. **Re-measured: 1 finding, 1 true, 0 false**, with the can-it-fail
proof being the real pre-correction file rather than a fixture.

**Cluster E's mechanical form measured 71% false and is NOT BUILT.** The idea: when an entry carries
`corrects: X`, warn that X's *siblings* may state the same disproved thing. Over all 416 entries it
returned **7 findings — 1 clearly true (`IMP-0010`, in a class with exactly 2 members), 1 arguable, 5
clearly false.** Every false one came from a broad bucket: `corrects` against a member of
`platform-contract-guessed-not-groundtruthed` implicates **46** unrelated siblings. Narrowing to classes
with two or fewer members leaves 2 findings, 1 true, 1 arguable — still not clean, for one true positive
in the whole corpus that `IMP-0413` had already named in prose. Change 15 fixes that instance with a
one-line log repair instead, which is the honest altitude.

**Cluster F's static detection measured 100% false, and its one real instance was invisible.** A count
assertion beside a literal array, over 48 test files: **4 findings, 0 true, 4 false.** All four take
their count from the subject correctly — a rendered DOM row count, a `Set().size`, two domain values.
The genuine instance, `client.test.ts`'s *"five registered entity sets"*, does not appear, because
delivery corrected it to seven before this dispatch opened. So *"the count came from the test's own
enumeration"* is not decidable by proximity.

**Cluster H's gate measured 24 raw findings and at best one true, so cluster H ships prose.** `IMP-0419`
proposes extending the TAD-versus-source gate with a document-internal privilege check. Built two ways.
A global form (is this `prv*` in **any** role source?) returned **1 finding, 0 true, 1 false** — the one
hit was `prvDeleteAuditPartition`, which the parent architecture document says `REV Admin` **must not**
carry. A per-role pair form (does **this** role's source hold **this** privilege?) returned **24 raw
findings**, and after excluding negated and retracted lines, **3 — of which at best 1 is true** (a
Revision 5 argument superseded three sections later rather than corrected in place). The two remaining
false positives are instructive: one is a negation my pattern missed because the word *no* was wrapped
in markdown emphasis, the other is the stale-privilege table correctly naming the privilege as stale.
So the class reaches x16 with no gate, and this is the second consecutive review to measure one and
decline.

**Cluster A's first two designs were both wrong, in different ways.** A **directory-level** check (does
this gate's glob root contain ignored files?) measured **5 findings, 1 true, 4 false**: `scripts` is
"mixed" only because of `__pycache__/*.pyc`, which `scripts/*.py` never returns, and `docs/Import` only
because of a `.DS_Store` that `*.doc*` never matches. A **glob-result** check with a naive AST parse
measured **4 findings, 0 true, 4 false** — three were my own extractor expanding a bare `*` from the
wrong base, the fourth was `verify-toolchain-claims.py`, already correct at L190. Two narrowings —
anchored patterns only, and skip a script declaring its own handling — remove all four **by name**.
**Re-measured: 0 findings at rest; 1 finding, 1 true, 0 false with the real fixture materialised.**

**`IMP-0413`'s proposed target does not contain the claim it asks to correct.** It names
`knowledge/technology/platform.md`; that file has no occurrence of `outputDirectory` or of a
space-in-path claim. The claim lives at
[`build-and-deploy.md` L257](../../knowledge/technology/build-and-deploy.md#L257) and
[L403](../../knowledge/technology/build-and-deploy.md#L403), and in the build config comment at
[L1231](../../config/revitalise-grant-automation-build.yml#L1231). Change 12 corrects the finding's own
target rather than editing the file it named.

---

## 7. Verification executed for this review

| Check | Command | Result |
|---|---|---|
| Log state read before any finding | `python3 scripts/verify-improvement-log.py --check` | At dispatch: **414 entries, 109 NEW — 56 unread, 0 awaiting-approval, 53 reviewer-deferred.** FAILED on 2 triggers |
| Log state RE-read before this draft closed | same command | **416 entries, 111 NEW — 58 unread.** `IMP-0418` and `IMP-0419` appended by the erratum session mid-draft; both folded into cluster H rather than deferred |
| Review 33's exclusion, confirmed before scoping | read its section 5 | Its `IMP-0405`…`IMP-0417` row excludes exactly this set. Scope set from the gate's list, not re-derived |
| Digest current before editing | `python3 scripts/generate-known-failure-modes.py --check` | **Current — 416 entries, 415 lessons, 505 lines, 37 recurring class rows** |
| Glob-based gates, enumerated | AST parse over `scripts/*.py` | **22 of 62 scripts select inputs by glob; 0 are ignore-aware.** 1038 input files enumerated, 624 gitignored — all but one in `node_modules` |
| Glob roots classified | `git check-ignore` over each root | 5 MIXED, and **3 of the 5 are false positives at the glob level** (`.pyc` and `.DS_Store` the actual patterns never match) |
| Cluster A, at rest | prototype over `scripts/` | **0 findings** after two narrowings; 1 script declares its own handling, 26 unanchored patterns skipped |
| Cluster A, can-it-fail | recreated the REAL fixture, ran the HARD gate | `verify-audited-tables.py` **exit 1, 13 undeclared pairs** over a throwaway file; ignore-aware input set globs 10, excludes exactly 1 by name, keeps 9. Fixture removed, **exit 0** confirmed, absence re-checked |
| Cluster B, both forms | modified copy over 4 config files + `git show HEAD:` | Naive **3 findings, 1 true, 2 false**, and INVERTED (2 on the fixed file, 1 on the broken one). Narrowed **1 finding, 1 true, 0 false** |
| Cluster C, removed privileges | XML parse + diff of `Roles/*/*.xml` against HEAD | **1 finding, 1 true, 0 false** — `prvReadWorkflow` gone from `REV Trustee` source, declared at [L237](../../src/solutions/RevitaliseGrantAutomation/Roles/REV%20Trustee/REV%20Trustee.xml#L237), no revoke step. The other two roles legitimately still grant it |
| Cluster E, corrects-siblings | prototype over all 416 entries | **7 findings, 1 true, 5 false, 1 arguable.** Not shipped |
| Cluster F, count assertions | prototype over 48 test files | **4 findings, 0 true, 4 false.** Not shipped |
| Cluster H, both forms | prototype over `docs/architecture/` + role XML | Global form **1 finding, 0 true, 1 false**; per-role form **24 raw, 3 narrowed, at best 1 true.** Not shipped |
| Erratum state, re-measured at close | grep the TAD + parse the flow JSON | `message: 3` in the document **and** in source; `A-R49` names two privileges. Both document halves resolved by delivery |
| `IMP-0413`'s claim, re-derived | grep `knowledge/`, `constraints/`, `skills/`, `agents/`, `config/` | The space-in-path cause appears in **3 places**, none of them the file the finding names |
| `IMP-0410`'s instance, current state | `ls` + `git check-ignore -v` | Fixture **absent**; ignored at [`.gitignore` L58](../../.gitignore#L58). The HARD step is green at rest and the defect is latent |
| `IMP-0416`'s instance, current state | read the file and `git show HEAD:` | Corrected in the working tree from five to **seven**, with the hazard recorded in its own comment |
| This document, against the gate it must pass | `verify-review-document.py --only …-review-4.md` | See the closing line |

**Level reached: V1 for everything above** ([`C-TECH-053`](../../constraints/technology/technology-constraints.md#L108)).
Every check reads source, logs, git, or a script's own execution. **Not verified, and named because it
is the gap that matters:** no live DEV observation was made or attempted — this session holds no
credential for that environment and both connected MCP servers are unauthenticated. `IMP-0407`'s live
privilege binding, `IMP-0406`'s trigger actually firing, `IMP-0411`'s Pester run, `IMP-0415`'s rendered
behaviour, `IMP-0417`'s post-binding state and `IMP-0419`'s per-environment prerequisite exposure are
all statements about a running system that nothing here can make, which is why none of the six is
closed.

---

## 8. Digest impact

| | Before (measured at close) | Predicted after |
|---|---|---|
| Log entries | 416 | 418 — two findings this review appends about itself |
| Distinct lessons | 415 | 417 |
| Recurring classes (x≥2) | 37 rows | 37 — both self-findings join existing classes, crossing no threshold |
| Digest lines | 505 | grows by two lessons and one correction marker |

Predicted, not asserted: the generator runs again at application and section 10 will carry the measured
figures, per `IMP-0198`.

**Dispositioning 16 entries does not shrink the digest**, and the mechanism is named rather than hoped
for: the generator selects on `status in {NEW, APPLIED}`, so a lesson is published whether its finding
is open, deferred or applied. What this review changes is enforcement — plus one **correction marker**,
the only structural delta: change 15 makes `IMP-0010`'s lesson carry the same
`CORRECTED by IMP-0413` marker that `IMP-0079`'s already does at
[digest L290](../../logs/known-failure-modes.md#L290), so the disproved cause stops being taught in the
one place a reader is most likely to meet it.

**Two findings this review will append about itself**, allocated with
[`allocate-improvement-id.py`](../../scripts/allocate-improvement-id.py) at application time because
another session is demonstrably writing the log: (i) `learning-substrate-destroyed` — a review parked at
its gate leaves every entry it processed reading `unread`, so the queue gate reports *"nothing records
that anyone has looked at these"* about 43 entries under active analysis, and the batch trigger re-fires
against work already done; this is the finding behind the judgment call in section 5. (ii)
`gate-reassures-wrongly` — a phrase-presence check over prose scores a corrected file **worse** than the
defective one, because a correction quotes the old wording to withdraw it; fourth measured occurrence in
this repository, so any future such check measures against the corrected file specifically and asserts
on values rather than phrases.

---

## 9. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-28-improvement-review-4.md

Findings processed: 16 NEW  →  8 clusters
Regression check:   4 prior changes audited, 2 classes recurred
Proposed:           0 constraints (cap 3), 5 gates/scripts, 8 skill/knowledge edits,
                    1 agent-file edit, 1 constraint amendment, 1 log repair, 0 retirements
Altitude calls:     4 generalised from instance to class, 4 left as knowledge/skill notes
Digest:             will regenerate — 417 lessons, 37 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

**Both blockers are disposed of.** `IMP-0410` becomes changes 1–3; `IMP-0406`'s document half was
resolved by the concurrent erratum and its durable half becomes change 8. Neither is closed as
`APPLIED` — both are `V5`/`V3` defects whose re-observation needs a live environment, so both keep a
`deferred_reason` rather than a closure nobody tested.

**This gate does not unblock the build.** 43 entries stay `unread` until review 33 receives its own
keyword, so the batch trigger and
[`C-TECH-061`](../../constraints/technology/technology-constraints.md#L131) stay red on them.

**The `Proposed:` figures count the numbered rows of section 3 by their `Type` column, and reconcile:
5 + 8 + 1 + 1 + 1 = 16 rows** (5 `script`, 4 `skill`, 4 `knowledge`, 1 `constraint-amendment`,
1 `agent`, 1 `other`).

---

## 10. Applied

**All 16 changes are on disk.** Re-verification ran first (activation step 8): the log was
unchanged at 416 entries and max id `IMP-0419`, and **no `corrects` field anywhere named any of
this review's sixteen findings** — the gate's two `corrects` warnings concern `IMP-0290`/`IMP-0298`,
which belong to earlier reviews. No proposal was disproved, so nothing was withheld. Six changes
deviated at application and each is named below with the measurement that forced it.

| # | Change | Applied | Entries dispositioned |
|---|---|---|---|
| 1 | [`scripts/lib/tracked_paths.py`](../../scripts/lib/tracked_paths.py) — glob, then exclude what git ignores, naming each exclusion; fails OPEN if `check-ignore` is unavailable; never decides the empty-input question | ✅ `--selftest` 6/6 | `IMP-0410` |
| 2 | [`verify-audited-tables.py`](../../scripts/verify-audited-tables.py#L60) resolves `SETTINGS_GLOB` through it; the no-inputs failure untouched | ✅ 8/8, incl. 2 new | `IMP-0410` |
| 3 | [`scripts/verify-gate-input-tracking.py`](../../scripts/verify-gate-input-tracking.py) + the [`gate-input-tracking`](../../config/revitalise-grant-automation-build.yml#L360) step | ✅ `--selftest` 9/9; preflight sees it as a gate | `IMP-0410` |
| 4 | [`verify-build-config.py`](../../scripts/verify-build-config.py) rejects a step documented as currently failing, unless retracted | ✅ 1 finding, 1 true, 0 false | `IMP-0414` |
| 5 | [`C-TECH-042`](../../constraints/technology/technology-constraints.md#L84) amended — removals, the revoke obligation, and `IMP-0418`'s safety fact | ✅ row integrity 8 fields | `IMP-0407`, `IMP-0418` |
| 6 | [`verify-role-privilege-ownership.py`](../../scripts/verify-role-privilege-ownership.py) — a declared removal needs a sequenced revoke **and** an absence read-back | ✅ 11 fixtures | `IMP-0407` |
| 7 | [`how-to-verify-a-platform-contract.md`](../../skills/how-to-verify-a-platform-contract.md) — reconciling a hand-edited live artefact, all three directions | ✅ | `IMP-0408` |
| 8 | [`power-automate.md`](../../knowledge/technology/power-automate.md) — the full `message` enumeration, export+unpack, `stringmap`, the `pac env fetch` trap | ✅ toolchain-claims PASS | `IMP-0406`, `IMP-0409` |
| 9 | [`code-apps.md`](../../knowledge/technology/code-apps.md) — three steps in a fixed order, `--allow`, both forbidden shortcuts | ✅ | `IMP-0417` |
| 10 | [`accessibility-checklist.md`](../../skills/accessibility-checklist.md) — web-embedding licence step | ✅ | `IMP-0354` |
| 11 | [`provisioning/README.md`](../../provisioning/README.md) — Pester 5.7.1 pinned, all three files named | ✅ | `IMP-0411` |
| 12 | [`build-and-deploy.md`](../../knowledge/technology/build-and-deploy.md) ×2 + the [build config comment](../../config/revitalise-grant-automation-build.yml#L1324) — cause corrected, operative rule untouched | ✅ | `IMP-0413` |
| 13 | [`how-to-review-code.md`](../../skills/how-to-review-code.md) — the mutation line and the count-direction line | ✅ | `IMP-0415`, `IMP-0416` |
| 14 | [`agents/improvement-agent.md`](../../agents/improvement-agent.md#L131) — activation step 8's no-change clause | ✅ | `IMP-0405` |
| 15 | Log repair — **reshaped, see deviation 1** | ✅ both markers render | `IMP-0413`, `IMP-0420` |
| 16 | [`how-to-document-architecture.md`](../../skills/how-to-document-architecture.md) — cite don't restate, grep the whole document, name the residual | ✅ | `IMP-0418`, `IMP-0419` |

**Dispositions: 10 `APPLIED` (every one with a needle that matches — verified, 10/10), 6 deferred
with a `revisit_when`, all 16 stamped `reviewed_in`.** Deferred, because their re-observation needs
a live environment or a signed-in user this session had neither of: `IMP-0406` (V5), `IMP-0407`
(V3), `IMP-0411`, `IMP-0412` (review 33's), `IMP-0415` (V4), `IMP-0419` (V3).

### The six deviations, each with its measurement

1. **Change 15 could not be applied as worded, and was reshaped.** `corrects` is read as a single
   **string** by both consumers — [`verify-improvement-log.py` L1466](../../scripts/verify-improvement-log.py#L1466)
   and [`generate-known-failure-modes.py` L411](../../scripts/generate-known-failure-modes.py#L411)
   — so one entry corrects exactly one target and a list would be coerced, fail to resolve, and be
   **silently dropped** by the generator. Making it multi-valued means editing two scripts that
   review 33 owned at that moment. The intent was achieved instead through the schema as it exists:
   `IMP-0420` records the schema limit and carries `corrects: IMP-0010`. **Both disproved lessons
   now carry a marker** — [digest L296](../../logs/known-failure-modes.md#L296) and
   [L301](../../logs/known-failure-modes.md#L301) — which is exactly what change 15 asked for.
2. **Change 6's first form measured 8 findings, 0 true positives**, and one narrowing then had to
   be **refined because it discarded the founding true positive.** The false positives, by name:
   `prvReadSavedQuery` and `prvReadEnvironmentVariableValue` (`REV Admin.xml:197`/`:223`), whose own
   comments say the privilege *"does not exist as a privilege in this environment"* — never bound,
   so nothing to revoke; `prvAssignrev_provider`/`prvSharerev_provider` (`:93`), `IMP-0254`'s
   impossible verbs; the bare token `prvRead`, scraped from prose and scoring as *sequenced* by
   substring-matching every line naming `prvReadWorkflow` — a false **negative** mechanism; and a
   prose paragraph about a provider **record** that *"can simply be removed"*. Three narrowings
   remove all of them. **The refinement matters:** requiring the privilege to resolve to a
   *solution* table excluded `prvReadWorkflow`, which names the out-of-box `workflow` table, exists
   perfectly well, and **is `IMP-0407`'s founding true positive.** Re-measured: 3 removals examined,
   0 findings, and the can-it-fail proof is the **real TAD** with its `prvReadWorkflow` lines
   stripped, which reproduces the pre-erratum state exactly and fires the gate.
3. **Cluster C's expected count changed, because the erratum landed.** §7 predicted *1 finding, 1
   true* for removed privileges. Post-erratum the correct answer is **0**: the TAD now sequences
   **both** revokes at [its rollout step 8](../../docs/architecture/trustee-portal-visual-refresh-architecture.md#L3179)
   with both absence read-backs in [its prerequisites table](../../docs/architecture/trustee-portal-visual-refresh-architecture.md#L3123).
   Reported as resolved-by-delivery, not as a clean run.
4. **Change 3's one real-corpus finding was adjudicated a FALSE POSITIVE, and two false SKIPS were
   found and fixed.** The finding: [`verify-toolchain-claims.py` L189](../../scripts/verify-toolchain-claims.py#L189)
   selects 624 ignored `node_modules` manifests — and L190 discards every one, while L184 globs
   *into* `node_modules` deliberately, because the **installed** version is the ground truth sought.
   It now carries a `GATE-INPUT-TRACKING:` declaration. The two false skips were worse and only the
   real corpus exposed them: the first draft matched the token `tracked_paths` anywhere in a file
   and skipped `derive-wbs-state.py`, whose own helper is *named* `_git_tracked_paths`; and the gate
   **skipped itself** on the strength of a marker inside its own test fixture. Detection is now
   AST-precise, placeholder reasons beginning `<` are rejected, and both classes are locked by
   fixtures.
5. **Change 14's derived-count fix was superseded by review 33's better one, and left alone.** I
   corrected `44` → `47`; review 33 rewrote the same passage to `48` **plus the derivation command**
   `ls scripts/verify-*.py | wc -l` (`IMP-0395`). 48 is correct — review 33 added two scripts, this
   review added one — and a derivation beats a literal, so their version stands. The change-14
   clause itself is present and intact.
6. **`IMP-0410` is closed `APPLIED`, not deferred — reconciling §9 against §5.** §9's summary says
   *"both blockers … keep a `deferred_reason`"*; §5's enumerated list of findings-closed-only-to-
   their-evidence names five and **does not include `IMP-0410`**. §5 is right: `IMP-0410`'s
   `observable_at` is `n/a`, and its reproduction was re-observed directly during application —
   the real fixture materialised, the naive input set measured at **13 undeclared pairs (HARD step
   RED)**, the ignore-aware set keeping 9 of 10 and excluding 1 by name, gate exit 0, fixture
   removed in a `try/finally`, absence re-checked. That is the reproduction step, so the closure is
   evidenced rather than claimed, and it is `reobserved` on the entry.

### Four findings appended, not the two predicted

`IMP-0420` (the `corrects` schema limit, above) and `IMP-0423` were **not** predicted by §8.
`IMP-0421` and `IMP-0422` are the two §8 promised.

**`IMP-0423` is a `blocker`, and it is the one thing this dispatch could not confirm.**
`python3 scripts/verify-improvement-log.py --check` **terminates with an unhandled
`AttributeError`** instead of a verdict — `'str' object has no attribute 'get'` at
[L1042](../../scripts/verify-improvement-log.py#L1042), a line that executes **only for `APPLIED`
rows**. `IMP-0390` and `IMP-0391` were appended with `proposed_change` as a plain **string**, and
when review 33 moved them to `APPLIED` the line began running over them and the gate died. It is
**not** this review's doing: neither entry is among the sixteen, all sixteen carry well-formed
objects, and the same command validated at dispatch (416 entries, FAILED on 2 real problems, no
crash).

**The blast radius is narrower than it first looks, and this is the part worth knowing:** the crash
is confined to `check_triggers`, so **`verify-improvement-log.py` without `--check` runs clean and
reports `OK (schema) — 420 entries`, exit 0.** Schema and every per-entry rule — including the
`reobserved`, `evidence_grep` and `corrects` rules this review depends on — pass over all 420
entries. What is lost is only the CI/trigger mode, which is exactly the mode `C-TECH-061` and
`CLAUDE.md`'s "validator first" rule invoke.

**Not fixed here, deliberately.** The file and both offending entries were owned by the
concurrently-applying review 33, and editing another live dispatch's files to unblock my own
verification is how two sessions clobber each other. What was verified instead, directly: the
schema pass above; all 16 dispositions correct; all 10 needles matching the tree; and the
generator — the other half of the mandated pair — clean and current.

### Verification at application

| Check | Result |
|---|---|
| Log re-read before applying (step 8) | **416 entries, max `IMP-0419`** — unchanged from the draft |
| `corrects` naming any of the 16 | **none** — the 2 warnings are `IMP-0290`/`IMP-0298`, other reviews' |
| `verify-audited-tables.py --selftest` | **PASS**, 8 cases (2 added, incl. the materialised fixture) |
| `verify-gate-input-tracking.py --selftest` | **PASS**, 9 cases (3 added for the false-skip classes) |
| Meta-gate, real corpus | **PASS** — 11 resolvable inputs, 0 ignored, 3 declared-and-named, **75 unresolvable and reported as a coverage gap** |
| `verify-build-config.py` on the build config | **PASS — 63 steps, 48 gates**, new check line green |
| Change 4, naive vs narrowed | naive **3 findings, 1 true, 2 false, polarity INVERTED** (2 on the corrected file, 1 on the defective) → narrowed **1, 1 true, 0 false** |
| `verify-role-privilege-ownership.py` | **PASS**, 11 fixtures; corpus 3 removals, 0 findings |
| Change 6, first form vs final | **8 findings, 0 true** → 3 narrowings (one refined) → **0 findings**, fires on the real pre-erratum TAD |
| `verify-constraint-verifiers.py` | **PASS** — 86 paths across 80 rows resolve. It **caught a real defect in my own edit**: an ambiguous "11 fixtures" literal beside two named gates, since replaced with a reference to the selftest's own reported total |
| Constraint counts, derived | **10 retired, 80 live** — budget still **0 of 3** |
| `verify-derived-counts.py` | 4 drifts → **3** (mine cleared; the 3 remaining are delivery-side secured-column counts) |
| `verify-toolchain-claims.py` | **PASS** — 54 claims across 13 knowledge files |
| `evidence_grep` needles | **10/10 match** |
| Digest regenerated | **421 entries, 420 lessons, 571 lines, 37 recurring classes** at the last run. The entry total is a moving figure while review 33 is still applying — it went 416 → 420 (this review's four) → 421 (`IMP-0424`, review 33's) during this dispatch. Re-run the generator rather than trusting this number |
| `generate-known-failure-modes.py --check` | **current** |
| `verify-improvement-log.py` (no `--check`) | ✅ **OK (schema) — 420 entries**, exit 0. Schema and every per-entry rule pass |
| `verify-improvement-log.py --check` | ❌ **CRASHES** in `check_triggers` only — `IMP-0423`, not this review's doing, not fixed here |

**Level reached: V1 for everything** ([`C-TECH-053`](../../constraints/technology/technology-constraints.md#L108)).
No live DEV observation was made or attempted — this session holds no credential and both connected
MCP servers are unauthenticated. `IMP-0406`'s trigger firing, `IMP-0407`'s privilege binding,
`IMP-0411`'s Pester run, `IMP-0415`'s rendered figure and `IMP-0419`'s per-environment exposure all
remain statements about a running system that nothing here can make, which is why none is closed.

**Digest actuals against §8's prediction:** 420 lessons at the last run, not 417 — because four
findings were appended rather than two, and review 33 appended a fifth (`IMP-0424`) while this one
closed. 37 recurring classes, exactly as predicted; no threshold crossed.

**One postscript, recorded because it changes what the reader should expect.** `IMP-0423`'s
type-guard half **landed from the concurrent dispatch about twenty minutes after it was logged** —
[`verify-improvement-log.py` L1049](../../scripts/verify-improvement-log.py#L1049) now
`isinstance`-guards the field, and `--check` runs to completion again. The **schema half did not**:
`proposed_change` is still not asserted to be an object anywhere, `IMP-0390` and `IMP-0391` are
still plain strings, and nothing reports them — so that malformation went from **crashing loudly to
being tolerated silently**, which is why `IMP-0423` stays open rather than being closed on the
guard. Its entry carries this update, and its sharpened lesson is the transferable part: guarding
the consumer and validating the schema are two different jobs, and doing only the first converts a
loud failure into a quiet one.
