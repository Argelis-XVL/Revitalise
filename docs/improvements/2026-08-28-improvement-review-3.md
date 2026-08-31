# Improvement Review 33 — 2026-08-28

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 43 `unread` → 11 clusters
**Trigger:** the batch trigger — 45 `unread` against a threshold of 10
([`C-TECH-061`](../../constraints/technology/technology-constraints.md#L131),
[`agents/WORKFLOW.md` L254](../../agents/WORKFLOW.md#L254)). Dispatched at
[`logs/routing.log` L323](../../logs/routing.log#L323), with the reviewer's instruction to dispose of
everything disposable and surface only what needs his judgement.
**Gate:** `APPROVE IMPROVEMENTS`
**Status:** ~~DRAFT — nothing in this document is on disk.~~ → **APPLIED IN FULL 2026-08-28.**
Reviewer (Xander Lykopoulos) approved as drafted; all 24 changes are on disk, all 43 in-scope
findings are dispositioned (30 `APPLIED`, 13 deferred with a reason and a trigger), and the digest
is regenerated. §10 carries the record, including the **two deviations forced at application
time** and the **three findings this application appended about itself**.
**Scope note:** 43 of the 45 `unread` entries. `IMP-0398` and `IMP-0401` are **excluded**: they are
[improvement review 32](2026-08-28-improvement-review-2.md)'s two findings, approved at
[`logs/routing.log` L324](../../logs/routing.log#L324) while this review was being written, so a
concurrent session is dispositioning them now. §5 reconciles with its dispositions rather than
re-deriving them. The 51 `reviewer-deferred` entries are untouched, per activation step 2.
**Concurrency:** a second session is applying review 32 to
[`logs/improvement-log.jsonl`](../../logs/improvement-log.jsonl) as this is written, and two design
documents were rewritten by other sessions mid-measurement. Every figure below is measured against a
named state, and activation step 8 re-measures before anything is applied (`IMP-0080`, `IMP-0213`).
**WBS:** system work, not billable
([`C-COM-002`](../../constraints/commercial/commercial-constraints.md#L35)). One finding carries a
commercial consequence belonging to `commercial-agent`; §5 names it. No contracted figure is restated
(D-3, [`C-COM-004`](../../constraints/commercial/commercial-constraints.md#L44)).

---

## Summary

**Twenty-four changes, no new rules.** The constraint budget is untouched — 0 of 3 — because every
cluster resolved to a script, a knowledge line or a step-order fix. One existing rule's verification
method is strengthened instead of a new row being added.

**Five of this review's own designs measured wrong and were rebuilt before reaching this document.**
One gate was pointed in the opposite direction to the defect it was meant to catch; one measured 100%
false positives; one measured 87% false and is not being built at all; one finding's stated root cause
turned out to describe a gate that has been wired for four days; and one knowledge edit is narrowed
because a finding appended mid-review shows the fact it would have written down is unsettled. §6
carries all five, with the numbers.

**Approving this does NOT unblock the build, and that changed while the review was being written.**
Thirteen entries arrived from the ADR-038 delivery dispatch after this one opened — `IMP-0405` to
`IMP-0417`, two of them `blocker` — so
[`C-TECH-061`](../../constraints/technology/technology-constraints.md#L131) stays red on 13 unread
entries after these 43 are dispositioned. §5 names all 13. The blockers route immediately, on their
own, per the trigger; they are not this dispatch's to process and re-deriving them here is
`IMP-0183`'s defect.

---

## 1. Regression check — did the last review's changes work?

Review 31 applied six changes earlier today ([its applied record](2026-08-28-improvement-review.md#L436)).
All six are on disk. Review 32 audited the same six against the six entries then available; this audit
runs over all 43 and reaches a different verdict on two rows.

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| 1 — digest generator runs the structural schema check ([`generate-known-failure-modes.py` L303](../../scripts/generate-known-failure-modes.py#L303)) | 2026-08-28 | `gate-reassures-wrongly` | **YES ×2** — `IMP-0396`, `IMP-0404` | **Working on its own rung.** Neither recurrence is the generator: one is a validator's error text naming a key it does not have, one is a different gate reading prose one physical line at a time. Changes 4 and 5 |
| 2 — [`allocate-improvement-id.py`](../../scripts/allocate-improvement-id.py) | 2026-08-28 | `learning-substrate-destroyed` | NO — 14 entries appended since, no collision | Working |
| 3/3a/3b/3c — validator named before the generator, seven agent files, `CLAUDE.md` | 2026-08-28 | `declared-policy-not-mechanically-enforced` | **YES ×2** — `IMP-0399`, `IMP-0402` | **Working on its own rung**, and neither recurrence is the log-append path. `IMP-0399` is the dispatch boundary, which nothing in `scripts/` can reach; `IMP-0402` is a design claim about a flow trigger. Change 8 takes the first; the second is deferred on measurement grounds |
| 4 — log repair | 2026-08-28 | schema integrity | NO — all 14 new entries validate | Working |
| 5/6 — [`code-apps.md`](../../knowledge/technology/code-apps.md#L214) connector-boot risk and Fluent contrast | 2026-08-28 | `code-apps-new-connector-blocks-boot` | NO | Working — change 10 extends the same section with eleven further lessons |

**The load-bearing recurrence is review 30's, not review 31's.** Review 30 change 13 registered three
prose counts in [`derived-counts-registry.json`](../../scripts/derived-counts-registry.json) for class
`hand-maintained-count-drifts-from-source`. That class recurred twice here (`IMP-0389`, `IMP-0395`) and
now stands at **x20**. The template's rule is that a class recurring after a prose fix escalates to a
gate — and the gate already exists, already runs, and reported the drift on every build for a day while
nobody read it. §6 explains what actually failed, because it is not what the finding says.

**And one class has recurred fifteen times with no gate of any kind.**
`approved-document-internally-inconsistent` has six members in this batch. Every gate in this
repository compares source against source; nothing has ever compared a design document's checkable
factual claims against the source that settles them. That is cluster A.

---

## 2. Clusters and promotion decisions

```
CLUSTER A: approved-document-internally-inconsistent  (x15; x6 here: IMP-0374, IMP-0376, IMP-0379,
           IMP-0380, IMP-0391, IMP-0347)
Altitude:  CLASS — fifteenth instance of a class with NO mechanical check anywhere.
Ladder row: "A tool could catch it mechanically → a script plus a build gate"
           (how-to-promote-a-finding.md L20).
Becomes:   change 7 — scripts/verify-design-doc-claims.py over docs/architecture/ AND docs/plans/,
           two checks. (a) A design document asserting that a rev_* column DOES NOT EXIST or was
           NEVER BUILT, where that column exists in Entity.xml. (b) Every contrast ratio a markdown
           table row states, recomputed from the hex values that row names. Plus change 7a: a
           Verify By strengthening on C-DOM-001, whose current check is a completeness test that a
           populated-but-wrong row passes by construction.
Retires:   nothing. C-DOM-001 is amended in place — see §4.
Cites:     IMP-0379 (check a), IMP-0391, IMP-0385 (check b), IMP-0374, IMP-0376 (both already fixed
           on disk; the durable half is change 15).
Residual:  FOUR, and the first two are why this is not the check the findings asked for.
           (1) IMP-0374 and IMP-0376 asked for the OPPOSITE check — a claim that a column IS
           withheld from trustees, against a schema showing it visible. Built, measured at 7
           findings / 0 true / 7 false, and NOT shipped; §6 carries the numbers. Both instances are
           already corrected on disk, so what those two findings leave behind is change 15's rule,
           not a gate.
           (2) Check (a) reports the same defect twice in one document because the document states
           it twice; and two further statements of it (§3.4's own heading, and a summary line) are
           NOT reported, because no column is named within 40 characters of the phrase. Coverage
           gap, not a false positive, and stated because the gate will read as more complete than
           it is.
           (3) Check (b) reads TABLE ROWS only. Every measured false positive was in prose, where a
           stated figure sits beside colours named three clauses away. Prose is declared out of
           scope rather than silently missed.
           (4) IMP-0380's staleness half and IMP-0347's one-sided-assumption half are WORDING
           properties, not value properties. No gate can read a claim's logic; they get changes 15
           and 17. Two of this cluster's six findings are answered by prose, and that is named
           rather than implied.
```

```
CLUSTER B: platform-contract-guessed-not-groundtruthed, flow-definition half  (x47; x2 here:
           IMP-0345, IMP-0349)
Altitude:  CLASS for IMP-0349 — measured at THREE live instances across three flows, which the
           finding predicted and left to this review to adjudicate. INSTANCE for IMP-0345, already
           fixed on disk, kept as a regression lock.
Ladder row: "A tool could catch it mechanically" (L20), in the gate that already owns flow shape.
Becomes:   change 1 — two checks in scripts/verify-flow-definition-language.py. Check 6: in a flow
           with more than one Response action, no Response may accept `Skipped` in its runAfter.
           Check 7: a failure branch filtering @result('<scope>') where that scope has a container
           child (Scope/Switch/If/Foreach/Until) that no further result() call descends into.
Retires:   nothing.
Cites:     IMP-0345 (check 6), IMP-0349 (check 7).
Residual:  Check 7's three live instances are declared as owned, dated exceptions IN THE SCRIPT, so
           the gate is HARD for a fourth instance from day one without turning the build red over
           three flows this review did not touch. An exception suppresses the failure, never the
           report — the C-DOM-031 pattern. And check 6 finds NOTHING today: its defect was fixed
           before this review opened, so it is a regression lock and §6 reports it as one rather
           than as coverage.
```

```
CLUSTER C: no-assertion-on-shipped-content, code-app half  (x15; x3 here: IMP-0350, IMP-0353,
           IMP-0390)
Altitude:  CLASS — IMP-0390 is the THIRD stylesheet (brand.css, print.css, ds-tokens.css) to carry
           the same exposure, and the fix that landed for it covers only the third.
Ladder row: "second instance → generalise" (L22): replace a hand-maintained list with a derivation.
Becomes:   change 2 — scripts/verify-code-app-composition-root.py. Check A enumerates every
           non-module .css under each code app's src/ and asserts main.tsx side-effect imports it.
           Check B asserts the test harness renders the same THEME object the composition root
           renders. Change 3 takes IMP-0350's manifest field with the manifest gate.
Retires:   the three literal filename regexes at src/styles/ds-tokens.test.ts:490-496 become
           redundant under check A — a hand-typed list of three replaced by an enumeration, which
           is C-TECH-067's own rule. Named as a delivery item, not deleted here: src/ is not this
           agent's to edit.
Cites:     IMP-0390 (check A), IMP-0353 (check B), IMP-0350 (change 3).
Residual:  Check B was DESIGNED DOWN after measurement — §6. As specified it reported PowerProvider,
           which the harness omits correctly, and that was its only finding. The shipped form
           compares theme props only. And check A reports TWO harness divergences today without
           failing on them: brand.css and print.css are imported by main.tsx and not by the
           harness, while both files carry comments asserting that all three are imported in the
           same change. Vitest processes no CSS, so nothing runtime depends on it — the claim is
           wrong, not the code, and that is a delivery item.
```

```
CLUSTER D: platform-fact-groundtruthed + code-app platform contracts  (x25 and x47; x11 here:
           IMP-0355, IMP-0356, IMP-0359, IMP-0360, IMP-0361, IMP-0362, IMP-0370, IMP-0386,
           IMP-0387, IMP-0388, IMP-0394)
Altitude:  KNOWLEDGE — eleven single instances, each with a general cause and no mechanical surface.
Ladder row: "One instance, but the cause is general and a human needs to know it → knowledge/" (L19).
Becomes:   change 10, one consolidated edit to knowledge/technology/code-apps.md, plus a CORRECTION
           MARKER on the "Invalid organization URL null" section. IMP-0360 falsifies IMP-0191's
           escalate-to-support conclusion AND narrows the standing advice that the only fix is a
           different data source TYPE: Microsoft's own DataverseConnector sample resolves
           getContext().app.dataverseOrgUrl once and passes it to the *WithOrganization* variant of
           every operation, and this app's client.ts now does exactly that.
Retires:   nothing retired; one recommendation corrected in place rather than appended around.
Cites:     all eleven.
Residual:  A knowledge file is read by whoever opens it, and logs/known-failure-modes.md renders NO
           Code App lesson at all today — which is cluster H. The two changes are load-bearing for
           each other, and neither is worth much alone.
```

```
CLUSTER E: hand-maintained-count-drifts-from-source  (x20; x2 here: IMP-0389, IMP-0395)
Altitude:  CLASS, and the escalation is NOT the one the finding proposes. IMP-0395 says
           verify-derived-counts.py is unwired; it has been the `derived-counts` build step since
           2026-08-24. §6 carries the disproof.
Ladder row: "The system's own memory failed → a read-path change" (L26).
Becomes:   change 3's second half — the manifest records one finding count per SOFT (--warn-only)
           build step, DERIVED from the config's own step list, so a new drift changes a number in a
           tracked artefact. Today a build records `warnings: {total: 83, untriaged: 0}` and a real
           drift is arithmetically invisible inside it. Change 21 repairs the one registered drift
           this agent's own file carries. Change 16 takes IMP-0389's durable half.
Retires:   nothing.
Cites:     IMP-0395 (changes 3, 21), IMP-0389 (change 16), IMP-0363 (the drift's origin).
Residual:  THREE of the four current drifts are delivery-owned prose and stay red until a delivery
           dispatch clears them; §5 names them with an owner. And a path:line citation in a source
           comment gets a convention line, not a gate: building one needs a registry of citations,
           and the three that exist sit in frozen files nobody is authorised to edit.
```

```
CLUSTER F: dispatch mechanics  (declared-policy-not-mechanically-enforced x17,
           worktree-isolation-base-predates-working-tree x1, incorporated-document-version-mismatch
           x3, dispatched-agent-stalls-silently x3; x4 here: IMP-0399, IMP-0400, IMP-0381, IMP-0357)
Altitude:  CLASS for the first three, which are one property: a dispatch parameter or premise the
           dispatcher got wrong and nothing could see. TOPOLOGY for IMP-0357.
Ladder row: "An agent had the information and still did the wrong thing → an agent-file edit" (L24)
           and "the ORDER of steps was wrong" (L25).
Becomes:   change 8, ONE consolidated edit to agents/lead-agent.md's delegation section carrying
           three rungs — a tier correction is a fresh dispatch and never a SendMessage resume; the
           worktree isolation mode is wrong for any dispatch touching uncommitted state, which here
           is the normal case; a brief stating another document's revision or status quotes the line
           it read. Change 9 adds a fifth case to agents/WORKFLOW.md's dispatch-death section.
Retires:   nothing. This change DISCHARGES the lead-agent.md edit review 32 deferred out of
           IMP-0398 — §5.
Cites:     IMP-0399, IMP-0400, IMP-0381 (change 8), IMP-0357 (change 9).
Residual:  Prose, on a rung where prose has been tried, and honest about why: nothing in scripts/
           sits between an agent and the Task tool, so no gate can read a dispatch parameter. The
           standing control stays the DISPATCHED agent's own tier self-check, which is downstream of
           the mistake and costs a round-trip each time — three were spent on one TAD today. This is
           review 32's residual, unchanged.
```

```
CLUSTER G: gate-reassures-wrongly, review-tooling half  (x17; x3 here: IMP-0396, IMP-0397,
           IMP-0404)
Altitude:  CLASS — three defects in the two scripts that check this system's own learning loop, all
           found by an agent using them for the first time in a new way.
Ladder row: "A tool could catch it mechanically" (L20) for two; a vocabulary fix for the third.
Becomes:   change 4 — scripts/verify-review-document.py: _sentences() becomes paragraph-scoped and
           excludes fenced blocks, and a PROPOSED-COUNT check is added, scoped to documents that
           declare change 4a's closed Type vocabulary. Change 4a — the template declares that
           vocabulary and states that a per-type figure counts ROWS, never files. Change 5 — the
           evidence_grep error text names the key it actually requires.
Retires:   nothing.
Cites:     IMP-0404 (change 4a's motivation is IMP-0397), IMP-0397 (changes 4, 4a), IMP-0396
           (change 5).
Residual:  The PROPOSED-COUNT check is the FOURTH attempt at this assertion in this repository and
           it can fire on no existing document — all 37 predate the vocabulary and are out of scope
           by construction. That is deliberate and it is why the template change comes first: §6
           measures both variants of the naive version at 17 and 15 findings with roughly one true
           positive between them, and the reason is not scoping (review 30's diagnosis) but that the
           Type column is an open vocabulary of 65 values and the claim counts FILES while the table
           counts ROWS. A closed vocabulary is what makes the arithmetic decidable at all.
```

```
CLUSTER H: digest-cap-hides-a-whole-subject-area  (x1: IMP-0383)
Altitude:  READ-PATH — one instance, promoted anyway because the ladder's bottom row is "the
           system's own memory failed → a read-path change" (L26), and this is that row exactly. The
           digest is how every other change in this review reaches an agent.
Ladder row: L26.
Becomes:   change 6 — the capped-lesson note becomes an index GROUPED BY class (fully derived, no
           vocabulary to maintain), and the generator gains a `--subject <term>` verb printing every
           lesson matching a term, rendered or capped.
Retires:   nothing.
Cites:     IMP-0383.
Residual:  This does not raise the cap and does not split any section, which are the two fixes the
           generator's own comment prefers. It makes what is hidden findable rather than visible,
           which is weaker. The honest reason: 105 lessons sit behind caps across five sections, and
           splitting five sections into new workflow moments is a design decision about when agents
           read what — not a defect fix, and not one to take inside a batch review.
```

```
CLUSTER I: input-type-with-no-owning-agent  (x2: IMP-0028, IMP-0384)
Altitude:  CLASS — second instance, so an instance patch is forbidden (L44).
Ladder row: an input type with no owning agent resolves to a declaration in the entry point.
Becomes:   change 20 — CLAUDE.md's Repository Layout declares a supplied-assets input surface with
           an owning agent and an explicit ships / does-not-ship statement, as a RULE for any
           supplied artefact landing outside docs/Import/, not a row for one directory.
Retires:   nothing.
Cites:     IMP-0028, IMP-0384.
Residual:  No gate enumerates top-level directories against the declared layout. Considered and not
           built: the corpus is 14 directories, one of them untracked, and a gate reading a prose
           layout block would be asserting against a markdown code fence. A third instance is what
           would justify it.
```

```
CLUSTER J: supplied-design-asset-assumed-wcag-compliant + three platform facts  (x1, and
           IMP-0373, IMP-0378, IMP-0403)
Altitude:  KNOWLEDGE and SKILL — four single instances, each with a general cause.
Ladder row: L19.
Becomes:   change 14 (accessibility-checklist.md gains an "adopting an externally supplied palette"
           step), change 11 (testing-tools.md — an EntityName-typed metadata column can be SELECTed
           and never FILTERed, generalising a note recorded as a form-specific recipe and reproduced
           on a second table), change 12 (power-automate.md — NARROWED to the open contradiction and
           the safe-under-either pattern, see below), change 13 (dataverse.md — FieldPermission carries CanCreate
           and CanUpdate, so column-level WRITE control exists and is used here, and its
           unavailability for a code-app-readable column follows from this project's own HARD gates,
           never from a platform limit).
Retires:   nothing.
Cites:     IMP-0385, IMP-0373, IMP-0378, IMP-0403.
Residual:  IMP-0385's contrast half becomes mechanical through cluster A's check (b) — which found
           the one arithmetic error in the corpus. Its REMOVED-FOCUS-INDICATOR half (outline:'none'
           with no replacement, a WCAG 2.4.7 failure outright) gets a checklist line and no gate: a
           gate for it would have to read CSS-in-JS props across a component tree, and this project
           has one supplied design system.
           AND change 12 is NARROWED rather than applied as IMP-0378 asks. IMP-0412, appended after
           this draft opened, establishes that IMP-0124's tail claims the OPPOSITE semantics for
           if(), that both are recorded as established, and that neither has been re-tested. Writing
           either as settled is how-to-promote-a-finding.md L153's "an argued mechanism in place of a
           confirmed one" — IMP-0217's defect. So what lands is the contradiction plus the pattern
           that is correct under both, and the deviation is recorded in three places per
           agents/improvement-agent.md L150.
```

```
CLUSTER K: platform-state-divergence + step order  (x9 and x5; x2 here: IMP-0372, IMP-0366)
Altitude:  ORDER for IMP-0366; DEFERRED for IMP-0372.
Ladder row: "the ORDER of steps was wrong" (L25).
Becomes:   change 18 — agents/architect-agent.md gains a step: a TAD or schema change resolving an
           SDD open question that contract/tad-deferrals.json names deletes the matching deferral in
           the SAME dispatch and re-runs verify-tad-coverage.py. IMP-0372 gets a recorded deferral:
           its remedy authenticates to a live environment, which agents/improvement-agent.md L318
           puts outside this agent's authorship entirely.
Retires:   nothing.
Cites:     IMP-0366 (change 18), IMP-0372 (deferral, §5).
Residual:  IMP-0366's instance is already closed on disk — TD-005 deleted, verify-tad-coverage.py
           re-run for this review and green. What is durable is the step order, and the gate that
           caught it belonged to an unrelated dispatch, which is the whole finding. IMP-0372's
           exposure stays LIVE in DEV: rev_ethnicgroup is secured in source with no live field
           permission, so the column fails closed to system administrators only — 52 permissions in
           source against 51 live.
```

---

## 3. Proposed changes

`Type` values come from change 4a's closed vocabulary: `constraint` · `constraint-amendment` ·
`script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? |
|---|---|---|---|---|---|
| 1 | script | [`scripts/verify-flow-definition-language.py`](../../scripts/verify-flow-definition-language.py) | Check 6 (multi-Response `Skipped`) and check 7 (`result(scope)` over an undescended container child), inline `--selftest` fixtures for both, and an owned, dated exception block for check 7's three live instances | IMP-0345, IMP-0349 | **YES** — `--selftest`, then the step at [`build.yml` L888](../../config/revitalise-grant-automation-build.yml#L888) |
| 2 | script | `scripts/verify-code-app-composition-root.py` (new) + a `code-app-composition-root` step | Every non-module stylesheet under a code app's `src/` is side-effect imported by its `main.tsx`; the test harness renders the same theme object the composition root renders; harness stylesheet divergence is reported, not failed | IMP-0353, IMP-0390 | **YES** — `--selftest`, and the preflight recognises any `scripts/verify-*.py` step as a gate |
| 3 | script | [`scripts/verify-build-manifest-note.py`](../../scripts/verify-build-manifest-note.py#L57) | Required-field assertion: `wbs` present and non-empty, every id resolving against `contract/wbs.json` **or** a `contract/change-orders/` covered id; plus one finding count per SOFT build step, derived from the config's own step list | IMP-0350, IMP-0395 | **YES** — `--selftest`, and build-agent already runs it at manifest time |
| 3a | agent | [`agents/build-agent.md` L225](../../agents/build-agent.md#L225) | The documented manifest schema gains `wbs` and `soft_gates` — the field `IMP-0350` calls "a convention held in the authoring agent's head" is written down where the agent reads it | IMP-0350, IMP-0395 | N/A — instruction change |
| 4 | script | [`scripts/verify-review-document.py` L238](../../scripts/verify-review-document.py#L238) | `_sentences()` becomes paragraph-scoped and excludes fenced blocks; at most one `LOST-DEFERRAL` per document and target section; plus a `PROPOSED-COUNT` check scoped to documents declaring change 4a's vocabulary | IMP-0404, IMP-0397 | **YES** — `--selftest` plus §6's corpus figures |
| 4a | template | [`templates/improvement-review-template.md` L46](../../templates/improvement-review-template.md#L46) | §3's `Type` column gets a closed vocabulary, and the gate block's per-type figures are declared to count table ROWS, never files — the two properties that made the naive check undecidable | IMP-0397 | **YES** — it is what makes change 4's second check possible |
| 5 | script | [`scripts/verify-improvement-log.py` L481](../../scripts/verify-improvement-log.py#L481) | The `evidence_grep` error text names `contains`, the key it requires, instead of `needle`, the key it does not | IMP-0396 | **YES** — `--selftest` |
| 6 | script | [`scripts/generate-known-failure-modes.py` L82](../../scripts/generate-known-failure-modes.py#L82) | The capped-lesson note becomes an index grouped by `class_instance_of`; a `--subject <term>` verb prints every matching lesson, rendered or capped | IMP-0383 | **YES** — `--check` plus the digest's own diff |
| 7 | script | `scripts/verify-design-doc-claims.py` (new) + a `design-doc-claims` step | Check (a): a document asserting a `rev_*` column does not exist, where it does. Check (b): every contrast ratio a table row states, recomputed from the hex values that row names. Covers `docs/architecture/` **and** `docs/plans/`, which no gate reads today | IMP-0379, IMP-0391, IMP-0385 | **YES** — `--selftest` plus §6's corpus figures |
| 7a | constraint-amendment | [`C-DOM-001`](../../constraints/domain/domain-constraints.md#L34) | `Verify By` stops being *"the classification column is fully populated"* — a completeness test a wrong row passes by construction — and names change 7's script | IMP-0376, IMP-0374 | **YES** — the amended `Verify By` is executable |
| 8 | agent | [`agents/lead-agent.md` L71](../../agents/lead-agent.md#L71) | Three rungs in one edit: a tier correction needs a fresh dispatch, because a `model:` argument to a resume call is a silent no-op; worktree isolation is wrong for a dispatch touching uncommitted state; a brief describing another document's revision or status quotes the line it read | IMP-0399, IMP-0400, IMP-0381, IMP-0398 | N/A — instruction change |
| 9 | agent | [`agents/WORKFLOW.md` L61](../../agents/WORKFLOW.md#L61) | Fifth dispatch-death case: a dispatch ending `completed` while deferring work to a monitor it created itself has stopped — those notifications reach the dispatching session, never the dispatched one | IMP-0357 | N/A — instruction change |
| 10 | knowledge | [`knowledge/technology/code-apps.md`](../../knowledge/technology/code-apps.md) | Eleven lessons, plus a correction marker on the "Invalid organization URL null" section: the generic connector IS fixable at the call site, via `getContext().app.dataverseOrgUrl` and the `*WithOrganization` operation variant | IMP-0355, IMP-0356, IMP-0359, IMP-0360, IMP-0361, IMP-0362, IMP-0370, IMP-0386, IMP-0387, IMP-0388, IMP-0394 | N/A — reference material |
| 11 | knowledge | [`knowledge/technology/testing-tools.md` L215](../../knowledge/technology/testing-tools.md#L215) | Generalise the `systemform.objecttypecode` recipe into its class: an EntityName-typed metadata column can be SELECTed and never FILTERed as a string. Second confirmed instance. Records the working profile-membership query | IMP-0373 | N/A — reference material |
| 12 | knowledge | [`knowledge/technology/power-automate.md` L97](../../knowledge/technology/power-automate.md#L97) | **NARROWED.** Record that this repository holds two contradicting lessons about whether `if()` short-circuits, that neither has been re-tested, and that `max(divisor,1)` is correct under either semantics — **not** that `if()` evaluates eagerly, which is what the finding asks for and what §6 shows is unsettled | IMP-0378, narrowed by IMP-0412 | N/A — reference material |
| 13 | knowledge | [`knowledge/technology/dataverse.md` L158](../../knowledge/technology/dataverse.md#L158) | `FieldPermission` carries `CanCreate` and `CanUpdate`, authored here for every secured column and reconciled live — so never write "the platform cannot" where "our own HARD gates forbid" is the true statement | IMP-0403 | N/A — reference material |
| 14 | skill | [`skills/accessibility-checklist.md` L27](../../skills/accessibility-checklist.md#L27) | An "adopting an externally supplied palette or design system" step: compute every text and UI-graphic pair before adoption, record each ratio beside the value that ships it, and check specifically for a removed focus indicator | IMP-0385 | Partly — change 7's check (b) covers the stated-ratio half |
| 15 | skill | [`skills/how-to-verify-a-platform-contract.md` L264](../../skills/how-to-verify-a-platform-contract.md#L264) | A fifth rule in §4: closing an assumption or risk is a write to code AND a write to every document citing its id — TAD §11 risks, §12.1 prerequisites, §12.2 verification, Dev Summary §10 | IMP-0380, IMP-0379, IMP-0374, IMP-0376 | N/A — instruction change |
| 16 | skill | [`skills/how-to-report-to-the-reviewer.md` L63](../../skills/how-to-report-to-the-reviewer.md#L63) | Distinguish a REPORT line-link (required, grepped fresh, read once) from a SOURCE-COMMENT citation (name the symbol, never the line) — the rule is stated only for reports and is being generalised into comments, where the cost profile is the opposite | IMP-0389 | N/A — instruction change |
| 17 | template | [`templates/dev-summary-template.md` L47](../../templates/dev-summary-template.md#L47) | An assumption row about a conditional or error branch states its claim and its verification in BOTH directions: fires when it should, and does not fire when it should not | IMP-0347 | N/A — instruction change |
| 18 | agent | [`agents/architect-agent.md` L59](../../agents/architect-agent.md#L59) | A TAD or schema change resolving an SDD open question that `contract/tad-deferrals.json` names deletes the matching deferral in the same dispatch and re-runs `verify-tad-coverage.py` | IMP-0366 | **YES** — the gate already fails a stale deferral; this fixes who runs it and when |
| 19 | agent | [`agents/development-agent.md` L165](../../agents/development-agent.md#L165) | Add `skills/how-to-write-a-test-plan.md` to the inline-skill table for the step that fixes a test-report defect — the regression-test obligation is stated at that skill's line 80 and nothing loads it at that moment | IMP-0346 | N/A — instruction change |
| 20 | agent | [`CLAUDE.md` L164](../../CLAUDE.md#L164) | The Repository Layout block declares a supplied-assets input surface with an owning agent and an explicit ships / does-not-ship statement | IMP-0028, IMP-0384 | N/A — instruction change |
| 21 | agent | [`agents/improvement-agent.md` L314](../../agents/improvement-agent.md#L314) | The registered `verify-*.py` count, derived at application time rather than retyped — one of four drifts `derived-counts` reports today, and the only one this agent owns | IMP-0395 | **YES** — `verify-derived-counts.py` |

**Constraint budget: 0 of 3 used.** Change 7a strengthens
[`C-DOM-001`](../../constraints/domain/domain-constraints.md#L34)'s `Verify By` rather than adding a
row, and that is the substantive choice rather than a budget trick: `C-DOM-001` already requires
personal data to be classified before an entity is designed, and its check — *"TAD §3 data
classification column is fully populated"* — is a completeness test that `IMP-0376`'s wrong row passed
by construction. A new row beside it would leave the weak check running.

---

## 4. Retirements

**No retirements, and the audit ran.** Derived, never typed — **10 retired, 80 live** — via
`grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l` and its live-row twin
([`agents/improvement-agent.md` L278](../../agents/improvement-agent.md#L278)).

**Two candidates considered, both rejected, and the second is the interesting one.**

[`C-DOM-001`](../../constraints/domain/domain-constraints.md#L34) was considered for retirement in
favour of a new mechanical row. Rejected: its subject is a GDPR Art. 30 obligation that predates any
gate, and retiring it to renumber the same rule loses the citation chain for nothing. Amending its
`Verify By` achieves everything the new row would.

The **three literal filename assertions** at `src/styles/ds-tokens.test.ts:490-496` are made redundant
by change 2's check A and are the cleanest retirement candidate in this review — a hand-typed list of
three replaced by an enumeration from disk, which is
[`C-TECH-067`](../../constraints/technology/technology-constraints.md#L137)'s own rule. They are **not
retired here** because they live under `src/`, which this agent does not edit. §5 hands them over.

---

## 5. Findings left unprocessed, and what you need to decide

No silent caps. 43 of 45 `unread` processed; two excluded, three deferred with triggers, and ten
closed only as far as the evidence reaches.

| Finding | Class | Why not processed here | Revisit when |
|---|---|---|---|
| `IMP-0398`, `IMP-0401` | `dispatched-below-required-tier`, `gate-scope-mismatch` | [Review 32](2026-08-28-improvement-review-2.md)'s own two findings, approved at [`routing.log` L324](../../logs/routing.log#L324) and being dispositioned by a concurrent session. A second independent answer for the same findings is the churn the anti-bloat limits exist to prevent | In motion. Change 8 **discharges** the `agents/lead-agent.md` edit review 32 deferred out of `IMP-0398`, exactly as its `revisit_when` scheduled |
| `IMP-0402` | `declared-policy-not-mechanically-enforced` | Its gate's corpus is the flow whose trigger ADR-038 is rewriting now, so a precision figure measured this hour describes a tree that no longer exists. Deliberately consistent with review 32 cluster B rather than re-argued | The ADR-038 dispatch lands and the new trigger is in source; the gate is then measured against both trees, which buys its fixtures free |
| `IMP-0372` | `platform-state-divergence` | Its remedy is a live-vs-source field-permission reconciliation that authenticates to DEV. [`agents/improvement-agent.md` L318](../../agents/improvement-agent.md#L318) puts that outside this agent's authorship: the requirement is handed over, the script is not written here | A delivery agent writes it under `provisioning/` and runs it against DEV |
| `IMP-0382` | `gate-scope-mismatch` | Its own `proposed_change` is `none` — the instance was corrected in the TAD's Revision 4 — and it names the third-instance generalisation as the open item. That third instance is `IMP-0401`, which review 32 deferred on measurement grounds, so the two belong together | With `IMP-0401` |
| Ten findings closed only to their evidence | various | `IMP-0345`, `IMP-0346`, `IMP-0356`, `IMP-0359`, `IMP-0360`, `IMP-0362`, `IMP-0385` are `V4`/`V5` defects whose re-observation needs a signed-in trustee or a live flow run. Their changes land; the entries keep a `deferred_reason` rather than a closure nobody tested (`C-TECH-053`, `IMP-0224`) | A signed-in session performs the original reproduction |
| `IMP-0405` … `IMP-0417` | various | **Thirteen entries appended AFTER this dispatch opened** — twelve from the ADR-038 delivery dispatch at 13:40, one from a peer improvement-agent session at 14:55. Outside the 45 this review was scoped to, and `IMP-0183` is the record of one dispatch pulling settled and unsettled work alike into its pass. Two are `blocker` (`IMP-0406`, `IMP-0410`) and route on their own, immediately | `IMP-0406`/`IMP-0410` now, on the blocker trigger; the remaining eleven at the next batch |
| 53 `reviewer-deferred` | various | Each carries an accepted `deferred_reason`; activation step 2 says leave them. One, `IMP-0274`, still has no `revisit_when` | A review scoped to the deferred queue |

**Handed to delivery with named owners — none needs your decision.** (i) The three `derived-counts`
drifts this agent does not own: `docs/development/revitalise-grant-automation-dev-summary.md` lines
4611 and 4768, and `src/solutions/RevitaliseGrantAutomation/Roles/REV Trustee/REV Trustee.xml` line 73
— owner `development-agent`. (ii) Check 7's three live flow instances — owner `automation-agent`.
(iii) The redundant literal stylesheet assertions, and the two source comments at `src/main.tsx:26-28`
and `src/test/harness.tsx:27-30` claiming a three-file harness parity the tree does not have — owner
`frontend-agent`. (iv) `docs/architecture/trustee-portal-visual-refresh-architecture.md` §3.4 and
`A-R24`, which state that `rev_ethnicgroup` does not exist while a later section of the same document
records that it does — owner `architect-agent`, and change 7's check (a) now reports it on every build.

**One commercial item, and it is `commercial-agent`'s.** `wbs:6.9` is a covered id through
[`CO-001`](../../contract/change-orders/CO-001.md#L30) and is absent from
[`contract/wbs.json`](../../contract/wbs.json)'s 61 baselined tasks. Change 3 therefore resolves
manifest task ids against the baseline **and** the change orders, rather than failing a build over a
legitimately approved id. Flagged, not decided —
[`C-COM-002`](../../constraints/commercial/commercial-constraints.md#L35) is not this agent's to apply.

### What you need to decide

**Nothing blocks this review.** Every finding in scope resolved to a change, a recorded deferral with
a trigger, or a handover with an owner, and every deferral is "the evidence does not exist yet" rather
than "somebody must choose".

Two things are worth your eye rather than your decision.

**Change 1's check 7 finds three real defects in shipped flows and deliberately does not block the
build on them.** They are declared as owned exceptions inside the script and printed on every run, so
a fourth instance fails immediately. If you would rather the build went red until those three flows
are fixed, say so and the exception block comes out — but the build is red already, and stacking a
second red gate on top delays the thing you asked for.

**The queue outran this review, and that is a standing condition rather than an accident.** Delivery
dispatches run in parallel with improvement reviews by design — the two dispatches at
[`routing.log` L320](../../logs/routing.log#L320) and [L321](../../logs/routing.log#L321) are the same
minute — so a batch review of 45 will routinely finish against a queue of 56. Clearing
`C-TECH-061` therefore needs the blocker dispatch and one more batch pass after this one, not a bigger
single review. `IMP-0405`, appended by a peer session at 14:55, is the same observation from the other
side and is the eleven-entry batch's business, not mine to answer here.

---

## 6. Where this review's own premises were measured, and four of them failed

Stated before the verification table, because a review that buries its disproved premises is the
defect it exists to remove ([`agents/improvement-agent.md` L342](../../agents/improvement-agent.md#L342)).

**Cluster A's gate was pointed the wrong way, and the measurement turned it round.** `IMP-0374` and
`IMP-0376` both ask for a check that a prose claim *"this column is withheld from trustees"* matches
the schema. Built and run over all seven design documents: **7 findings, 0 true, 7 false.** Every one
was the old wording surviving inside its own retraction — both documents were corrected on 2026-08-27
and now quote the wrong sentence in order to withdraw it, which a phrase-presence check cannot
distinguish from an assertion. Worse, the same run scored the corpus's one genuinely false sentence —
*"`rev_ethnicgroup` does not exist"* — as CONSISTENT, because it names a column that really is secured.
So the shipped check (a) asserts the opposite direction: a claim of ABSENCE against a schema showing
PRESENCE. Raw matches 20, and two narrowings each remove their false positives by name — the claim's
subject must be an existing `rev_*` column within 40 characters before the phrase (removing *"The
**job itself** is not built"* and a column named after a phrase whose subject was on the previous
line), and a scope qualifier disqualifies it (*"not built in this slice"* is a dated decision record,
not a claim about today's schema). **Measured after narrowing: 2 findings, 2 true, 0 false** — both
`rev_ethnicgroup`, which is `IMP-0379`'s defect exactly.

**Cluster A's check (b) needed one narrowing and now finds the one real error in 27 candidate rows.**
First form: **7 units, 1 true, 6 false**, every false one a stated figure whose second colour is a
design-system token, or a WCAG floor (`4.5`, `3:1`) or a WBS id (`6.1`) read as a measurement.
Narrowed to table rows only, bolded and `n.nn:1` figures only, floors excluded, and the page surface
implied when a row says *"white"*: **1 finding, 1 true, 0 false**, with 13 figures agreeing exactly
and 2 rows declared UNCHECKABLE by name rather than passed over. The one finding is a stated `3.18`
against a recomputed `3.1610` — and the shipped `ds-tokens.css` and `ds-tokens.test.ts` both carry
`3.16`, so the document is the wrong copy. That is `IMP-0391`, reproduced independently.

**`IMP-0395`'s stated root cause is FALSE and the change it proposes is already on disk.** The finding
says *"grep of `config/revitalise-grant-automation-build.yml` confirms it is not a step"*. It is step
`derived-counts` at [line 441](../../config/revitalise-grant-automation-build.yml#L441), added
2026-08-24 by review 24 for `IMP-0269` — the review that existed *because* the gate was unwired. The
proposal is withheld. What replaced it is the mechanism that actually failed: the step is SOFT via
`--warn-only`, prints four drifts on every run, and the last two builds recorded
`warnings: {total: 83, untriaged: 0}` and *"all previously triaged or accepted-by-design"* — an
aggregate a new true positive disappears into. Change 3's second half is the narrowing.

**A delegated measurement reported a hole in the gate-over-the-gates that does not exist.** It read
[`verify-build-config.py`](../../scripts/verify-build-config.py#L368)'s name-pattern list, found the
flow-definition step matching none of it, and concluded the step is never required to prove it can
fail. `is_gate()` has a second clause — anything running a `scripts/verify-*.py` is a gate whatever it
is called — and the step is recognised. Re-derived by executing `is_gate()` directly. Had it gone in,
this review would have proposed a change already on disk, for the second time in one sitting.

**Change 2's check B measured 100% false positives as first specified, and was designed down.** As
written it asserted that the harness renders every provider the composition root renders; its only
finding was a provider the harness omits correctly, because it injects a fake repository and has no
SDK to configure. **1 finding, 0 true, 1 false.** The shipped form compares theme props only — which
is `IMP-0353`'s actual defect — and removes that false positive by name.

**Change 4's second half, as the finding specified it, measured 17 and 15 findings with about one true
positive between them — and the reason is not the one on record.** Review 30 dropped this check at
18 findings / 0 true and diagnosed a scoping defect. Scoping it correctly this time still fails: the
§3 `Type` column is an **open vocabulary of 65 distinct values** across the corpus, 20 of them mapping
to no bucket at all, and the gate block's figures count **files** while the table counts **rows**.
Both are declaration problems, not parsing problems, so change 4a fixes the declaration and change 4's
check applies only where it holds. It can fire on no existing document, and that is stated rather than
dressed up as a clean run.

**Change 1's check 6 measures 0 findings, reported as a regression lock rather than as coverage.** Its
defect — a four-Response flow replying twice on its happy path — was fixed before this review opened.
One raw match exists and the multi-Response guard correctly suppresses it, because that flow has
exactly one Response action. So the guard is load-bearing and is proven by a real corpus case rather
than a fixture.

**Change 4's first half measures 0 findings gained and 0 lost, which is the point.** The naive
paragraph join measured **4 findings, 0 true, 4 false**: a filename split at the `.` in `.md`, and
gate-block key/value lines joined into sentences that exist in no document. Excluding fenced blocks
and reporting at most one lost deferral per document and section removes all four by name and changes
nothing else — corpus output byte-identical to baseline, 14 of 14 fixtures still passing. And it does
fix the defect: a fixture carrying `IMP-0404`'s exact wrapped reference is reported by the current
script and clean under the new one.

**Change 12 is narrowed because the fact it would have recorded is not settled.** `IMP-0378` reports,
from Microsoft's own function reference, that `if()` evaluates all three arguments — and asks for that
to go into the knowledge file. `IMP-0412`, appended at 13:40 while this draft was open, establishes
that `IMP-0124`'s tail records the opposite semantics as proven, that both sit in the repository as
established, and that **neither has been re-tested**. `IMP-0412`'s own analysis is that `IMP-0124`'s
differential observation cannot distinguish the two cases — but it labels that a prediction, not a
finding. So what lands is the contradiction, the note that one live experiment settles it, and the
`max(divisor,1)` pattern that is correct either way. The narrowing removes exactly one thing: a
documentation-derived claim written down as established, which is
[`how-to-promote-a-finding.md` L153](../../skills/how-to-promote-a-finding.md#L153)'s named exclusion
and `IMP-0217`'s defect.

**`IMP-0396`'s second half measured as ALREADY SATISFIED.** It reports that the `reobserved` example
in `skills/how-to-log-an-improvement.md` shows four members against the validator's five. The example
at [line 101](../../skills/how-to-log-an-improvement.md#L101) carries all five and
[line 106](../../skills/how-to-log-an-improvement.md#L106) says *"All five fields are required"*. Only
the error-text half is being changed.

---

## 7. Verification executed for this review

| Check | Command | Result |
|---|---|---|
| Log state read before any finding | `python3 scripts/verify-improvement-log.py --check` | At dispatch: 96 NEW — **45 unread**, 51 reviewer-deferred. FAILED on blocker ×2 (review 32's) and batch ×45 |
| Log state RE-read before this draft closed | same command | **414 entries. 109 NEW — 56 unread, 53 reviewer-deferred.** Review 32 is applied (`IMP-0398`, `IMP-0401` both carry a `deferred_reason` and `reviewed_in`); 13 entries appended mid-review, 2 of them new blockers. The scope stays 43 and §5 names the 13 |
| Digest current before editing | `python3 scripts/generate-known-failure-modes.py --check` | Current — **414 entries**, regenerated by the peer session that appended them |
| Build config preflight | `python3 scripts/verify-build-config.py config/…-build.yml` | **PASS — 61 steps, 46 gates**, negative-test coverage OK |
| `derived-counts`, run bare | `python3 scripts/verify-derived-counts.py` | **4 drifts**, not the 3 `IMP-0395` names — the fourth is this agent's own file |
| Gate classification, re-derived | executed `is_gate()` directly | The flow step **is** recognised. The delegated claim was wrong |
| Every gate suspected of being unrecognised | ran each script's `--selftest` | **20 of 21 exit 0**; the 21st has no `--selftest` and is registered in the Pester suite instead. No hole |
| Condition-profile columns, ground-truthed | parsed `Entity.xml` + `FieldSecurityProfiles.xml` | Both `IsSecured=0` and absent from every profile. The only match in the profile file is a **comment**, so check (a) parses `<AttributeName>` elements and never greps |
| `IMP-0366`'s instance, on disk | `python3 scripts/verify-tad-coverage.py` | **OK** — 174 column specs, 8 deferred, TD-005 deleted. Instance closed |
| `IMP-0372`'s source half | grep `rev_ethnicgroup` in the profile file | Present in source. The live half is **unverified** |
| `wbs:6.9`, against the baseline | parsed `contract/wbs.json` + `contract/change-orders/` | 61 tasks, **no `6.9`**; covered by `CO-001`. Change 3 resolves against both |
| Flow corpus, checks 6 and 7 | prototype over all 5 flow definitions | check 6: **0 findings**, 1 raw match correctly suppressed. check 7: 5 → **3 after one narrowing, 3 true, 0 false** |
| Code app corpus, checks A and B | prototype over `src/code-apps/` | 1 app, 3 global stylesheets, all imported by `main.tsx`. check A: **0 failures, 2 reported divergences**. check B: 1 → **0 after redesign** |
| Design-doc corpus, checks (a) and (b) | prototype over `docs/architecture/` + `docs/plans/` | check (a): 20 raw → **2 findings, 2 true, 0 false**. check (b): 7 → **1 finding, 1 true, 0 false**, 13 figures agreeing, 2 rows declared uncheckable |
| Review-document corpus, change 4 | modified copy over all 38 documents | Naive form **+4 findings, all false**. Shipped form **0 gained, 0 lost**, `--selftest` 14/14, and `IMP-0404`'s fixture flips from reported to clean |
| PROPOSED-COUNT, both naive variants | modified copy over all 37 documents | Variant A **17 findings / 24 documents**; Variant B **15 / 22**. Roughly one true positive between them. Not shipped in that form |
| This document, against the gate it edits | `verify-review-document.py --only …-review-3.md` | **OK.** It failed on its first draft with `IMP-0404`'s exact defect — a `§12.1` reference split at the `.` inside its own section number — and was re-worded, which is the workaround `IMP-0404` records and change 4 removes |
| This document's own §3 tally | counted the table rows by `Type` | **24 rows: 7 script, 7 agent, 4 knowledge, 3 skill, 2 template, 1 constraint-amendment.** The gate block's `Proposed:` line reconciles to the same 24, which is change 4a's rule applied to the document proposing it |
| Whole review corpus | `verify-review-document.py --reviews-dir docs/improvements` | **4 findings across 38 documents, all pre-existing** in documents dated 08-21, 08-22 and 08-25. This review neither introduces nor repairs them; three are amendment artefacts in documents written before the cluster-count check existed |

**Level reached: V1 for everything above** ([`C-TECH-053`](../../constraints/technology/technology-constraints.md#L108)).
Every check reads source, logs, or a script's own execution. **Not verified, and named because it is
the gap that matters:** no live DEV observation was made or attempted — this session holds no
credential for that environment and the two connected MCP servers are unauthenticated. `IMP-0372`'s
live divergence, `IMP-0356`'s real response payload, `IMP-0359`'s post-rollback boot, `IMP-0360`'s Save
Verdict and `IMP-0385`'s rendered contrast are all statements about a running system that nothing here
can make, which is why none of them is closed.

---

## 8. Digest impact

| | Before (re-measured at close) | Predicted after |
|---|---|---|
| Log entries | 414 | 416 — two findings this review will append about itself |
| Distinct lessons | 413 | 415 |
| Recurring classes (x≥2) | 38 raw / 37 after the read-path alias | 38 / 37 — `finding-diagnosis-unverified` goes x6 → x7, crossing no threshold |
| Digest lines | 503 | grows by change 6's capped-lesson index |

The "before" column is **re-measured at the moment this draft closed**, not carried from the figures
read at dispatch. Between those two moments the log went from 401 entries to 414 — which is `IMP-0405`'s
lesson, arriving during the review it is about.

Predicted, not asserted: the generator runs again at application and §10 will carry the measured
figures, per `IMP-0198`. The one non-obvious delta is change 6's, and it is structural rather than
content: 105 lessons sit behind per-section caps today, named by id only.

**Dispositioning 43 entries does not shrink the digest**, and the mechanism is named rather than hoped
for: the generator selects on `status in {NEW, APPLIED}`
([`generate-known-failure-modes.py` L356](../../scripts/generate-known-failure-modes.py#L356)), so a
lesson is published whether its finding is open, deferred or applied. Every lesson in this batch is in
the read path today. What this review changes is enforcement — except for cluster H, which changes
whether the knowledge can be found at all.

**Two findings this review will append about itself**, allocated with
[`allocate-improvement-id.py`](../../scripts/allocate-improvement-id.py) at application time because
another session is writing the log now: (i) `finding-diagnosis-unverified` — a delegated measurement's
confident claim about a gate's behaviour, read from part of that gate's source, nearly put an
already-on-disk change into a review; (ii) `gate-scope-mismatch` — `verify-tad-coverage.py`'s
`--design-docs` defaults to `docs/architecture` only, so the three documents under `docs/plans/`,
including the one carrying the classification table two findings in this batch are about, are read by
no gate at all.

---

## 9. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-28-improvement-review-3.md

Findings processed: 43 NEW  →  11 clusters
Regression check:   6 prior changes audited, 3 classes recurred
Proposed:           0 constraints (cap 3), 7 gates/scripts, 7 skill/knowledge edits,
                    7 agent-file edits, 2 template edits, 1 constraint amendment, 0 retirements
Altitude calls:     6 generalised from instance to class, 5 left as knowledge/skill notes
Digest:             will regenerate — 415 lessons, 37 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

**One change is NARROWED at draft time, not at application, and it is named here as well as in §3 and
§6:** change 12 records the open contradiction about `if()` and the pattern that is safe under either
semantics, rather than the eager-evaluation claim `IMP-0378` asks for. `IMP-0412`, appended mid-review,
shows that `IMP-0124` records the opposite as proven and that neither has been re-tested.

**And this gate does not unblock the build.** Thirteen entries arrived after this dispatch opened, two
of them `blocker`. §5 names all 13.

**The `Proposed:` figures count the numbered rows of §3 by their `Type` column, and reconcile: 7 +
7 + 7 + 2 + 1 = 24 rows.** That is change 4a's own rule, applied to the document proposing it.

---

## 10. Applied

**All 24 changes are on disk, 2026-08-28.** Reviewer approved as drafted, in full. Every entry was
closed as its change landed, not in a batch at the end
([`agents/improvement-agent.md` L205](../../agents/improvement-agent.md#L205)); the digest was
regenerated last, once.

| # | Type | Change | Entries dispositioned |
|---|---|---|---|
| 1 | script | [`verify-flow-definition-language.py`](../../scripts/verify-flow-definition-language.py) checks 6 + 7, docstring count corrected 5 → 7, 3 owned/dated/expiring exceptions | `IMP-0349` APPLIED · `IMP-0345` deferred (V5) |
| 2 | script | [`verify-code-app-composition-root.py`](../../scripts/verify-code-app-composition-root.py) (new) + `code-app-composition-root` step | `IMP-0353`, `IMP-0390` APPLIED |
| 3 | script | [`verify-build-manifest-note.py`](../../scripts/verify-build-manifest-note.py) — `wbs` + `soft_gates` required fields | `IMP-0350`, `IMP-0395` APPLIED |
| 3a | agent | [`build-agent.md`](../../agents/build-agent.md) manifest schema gains both fields | (with 3) |
| 4 | script | [`verify-review-document.py`](../../scripts/verify-review-document.py) — paragraph-scoped `_sentences()`, deduped `LOST-DEFERRAL`, `PROPOSED-COUNT` | `IMP-0404`, `IMP-0397` APPLIED |
| 4a | template | [`improvement-review-template.md`](../../templates/improvement-review-template.md) — closed `Type` vocabulary, rows-not-files | (with 4) |
| 5 | script | [`verify-improvement-log.py`](../../scripts/verify-improvement-log.py) `evidence_grep` error names `contains` | `IMP-0396` APPLIED |
| 6 | script | [`generate-known-failure-modes.py`](../../scripts/generate-known-failure-modes.py) — capped index by class + `--subject` | `IMP-0383` APPLIED |
| 7 | script | [`verify-design-doc-claims.py`](../../scripts/verify-design-doc-claims.py) (new) + `design-doc-claims` step | `IMP-0379`, `IMP-0391` APPLIED |
| 7a | constraint-amendment | [`C-DOM-001`](../../constraints/domain/domain-constraints.md#L34) `Verify By` now executable | `IMP-0374`, `IMP-0376` APPLIED |
| 8 | agent | [`lead-agent.md`](../../agents/lead-agent.md) — three dispatch rungs | `IMP-0399`, `IMP-0400`, `IMP-0381` APPLIED |
| 9 | agent | [`WORKFLOW.md`](../../agents/WORKFLOW.md) fifth dispatch-death case | `IMP-0357` APPLIED |
| 10 | knowledge | [`code-apps.md`](../../knowledge/technology/code-apps.md) — 11 lessons + correction marker | `IMP-0361`, `IMP-0387`, `IMP-0388`, `IMP-0394` APPLIED · `IMP-0355`, `IMP-0356`, `IMP-0359`, `IMP-0360`, `IMP-0362`, `IMP-0370`, `IMP-0386` deferred |
| 11 | knowledge | [`testing-tools.md`](../../knowledge/technology/testing-tools.md) — EntityName rule generalised | `IMP-0373` APPLIED |
| 12 | knowledge | [`power-automate.md`](../../knowledge/technology/power-automate.md) — **NARROWED**, see below | `IMP-0378` APPLIED |
| 13 | knowledge | [`dataverse.md`](../../knowledge/technology/dataverse.md) — `FieldPermission` write control | `IMP-0403` APPLIED |
| 14 | skill | [`accessibility-checklist.md`](../../skills/accessibility-checklist.md) §1.4a supplied palettes | `IMP-0385` deferred (V4) |
| 15 | skill | [`how-to-verify-a-platform-contract.md`](../../skills/how-to-verify-a-platform-contract.md) §4 fifth rule | `IMP-0380` APPLIED |
| 16 | skill | [`how-to-report-to-the-reviewer.md`](../../skills/how-to-report-to-the-reviewer.md) report vs source-comment | `IMP-0389` APPLIED |
| 17 | template | [`dev-summary-template.md`](../../templates/dev-summary-template.md) — both-directions assumption rows | `IMP-0347` APPLIED |
| 18 | agent | [`architect-agent.md`](../../agents/architect-agent.md) — delete a resolved deferral in the same dispatch | `IMP-0366` APPLIED |
| 19 | agent | [`development-agent.md`](../../agents/development-agent.md) — load the test-plan skill at the fix step | `IMP-0346` deferred (V5) |
| 20 | agent | [`CLAUDE.md`](../../CLAUDE.md) — supplied-assets input surface | `IMP-0028`, `IMP-0384` APPLIED |
| 21 | agent | [`improvement-agent.md`](../../agents/improvement-agent.md) — script count 44 → 48, derived | (with 3) |

### Two deviations forced at application time — NARROW-AND-REPORT, not substitution

Both are recorded here, in the entry's `applied_by`, and in the gate output, per
[`agents/improvement-agent.md` L150](../../agents/improvement-agent.md#L150). Each **removes
findings that would have been wrong and names them** — which is the tell that separates a
narrowing from a quiet substitution.

1. **Change 3's `wbs` check accepts `system` and `n/a`.** The approved wording was *"every id
   resolving against `contract/wbs.json` or a `contract/change-orders/` covered id"*. Measured over
   all 22 manifests on disk that produced one `UNKNOWN TASK ID`: `'system'`, in
   `build/artifacts/revitalise-cards-and-forms-20260821-2/manifest.json`. That is not an
   overclaim — `wbs:system, non-billable` is an established repository-wide sentinel, appearing
   nine times in [`logs/routing.log`](../../logs/routing.log), twice as a `wbs` value in the
   improvement log, and in **this document's own header**. Failing a build over the sentinel the
   system uses for its own system work is a gate nobody could satisfy honestly.
   **Re-measured: 0 false positives.**

2. **Change 7's check (b) treats "two hexes AND the word *white*" as UNCHECKABLE.** Against the
   real corpus the approved pairing rule produced **4 findings, 3 true, 1 false**. The false one
   was [`trustee-portal-visual-refresh-architecture.md` L2136](../architecture/trustee-portal-visual-refresh-architecture.md#L2136)
   — a row that is entirely correct, whose second figure is bolded together with trailing prose
   and therefore does not parse, so the one figure that did parse was paired with the wrong two
   colours. **Re-measured: 3 findings, 3 true, 0 false.**

### What was re-measured at application time, because the tree had moved

Activation step 8 is not a formality here: the ADR-038 delivery dispatch changed the flow corpus
between the draft and the keyword, so §7's figures were re-derived rather than trusted.

| Check | Draft | Re-measured at application |
|---|---|---|
| Flow corpus, check 7 | 5 → 3 after one narrowing, 3 true | **unchanged** — 5 raw, 3 true, 0 false; the two false positives are still the two `Fail_if_a_setting_row_is_missing` Terminate-only containers |
| Flow corpus, check 6 | 0 findings, 1 raw match suppressed | **unchanged, and now doubly so** — `REVPortalRoundStatistics` went from four Response actions to **none** under ADR-038, so `IMP-0345`'s instance has left the tree entirely. Check 6 is a pure regression lock |
| Code app, checks A + B | 0 failures, 2 reported divergences; B 0 findings | **unchanged** — 1 app, 3 global stylesheets, all imported by `main.tsx`; `brand.css` and `print.css` absent from the harness; both files render `brandTheme` |
| Design docs, checks (a) + (b) | (a) 2/2/0 · (b) 1/1/0 | **(a) unchanged at 2 true** (21 raw, not 20) · **(b) needed the extra narrowing above** |
| Review corpus, change 4 | 0 gained, 0 lost | **confirmed byte-identical** to the pre-change baseline across 39 documents (38 in the draft) |
| Build preflight | 61 steps, 46 gates | **64 steps, 49 gates** — ADR-038 added one, this review added two |
| `verify-*.py` count | 44 registered vs 47 | **48**, and the drift this agent owns is cleared; 3 delivery-owned drifts remain |

### Four findings appended by this application

- **`IMP-0424`** (`gate-cannot-fail`, APPLIED) — **the validator crashed while being used.**
  `verify-improvement-log.py` raised `AttributeError: 'str' object has no attribute 'get'` the
  moment an entry whose `proposed_change` is a bare **string** rather than an object reached
  `APPLIED`; two entries carry that shape and this review closed both. The traceback replaced the
  whole report **and the exit code was still 0**, so a caller checking only the exit status would
  have read the crash as a clean run. Guarded with `isinstance`. The wider half is open and is the
  real finding: no fixture in the 60-fixture selftest carries the string form, and nothing in
  `scripts/` fails when a check *raises* rather than returns.
- **`IMP-0427`** (`gate-scope-mismatch`, APPLIED) — **change 4's own new check measured wrong on
  its first real run, against this document.** `PROPOSED-COUNT` reported five findings and every
  figure was exactly **double**, because §10's applied record carries its own `Type` column with
  the same eight values and `_row_types()` scanned the whole file. Scoped to §3's body; a fixture
  now carries a second `Type`-columned table so it cannot regress. **Both earlier measurements
  were honest** — the corpus run that covered this document happened while §10 was still the
  template's empty placeholder, and *applying the review* is what gave the document its second
  table. The transferable half: **re-run every gate a review wires AFTER the last edit, not only
  before the first.**
- **`IMP-0425`** (`gate-scope-mismatch`, open) — `verify-tad-coverage.py`'s `--design-docs`
  defaults to `docs/architecture` only ([L873](../../scripts/verify-tad-coverage.py#L873)) and no
  caller overrides it, so the three documents under `docs/plans/` are read by no gate for their
  deliverable-now claims. Change 7 covers both directories, but for two different claim types.
- **`IMP-0426`** (`finding-diagnosis-unverified`, open) — **twice in this one review a stated root
  cause described a gate that had been wired for days.** `IMP-0395` said `verify-derived-counts.py`
  is not a build step (it has been the `derived-counts` step since 2026-08-24); a delegated
  measurement said the flow step is not required to prove it can fail (`is_gate()` has a second
  clause that recognises it). Both were produced by reading part of a script's source and
  reporting the result as a measurement. Activation step 8 requires re-reading a file a change
  *asserts something about*; it does not yet say **execute** when the assertion is about
  behaviour.

### Verification at close

| Check | Result |
|---|---|
| Every touched script's `--selftest` | **7 of 7 exit 0** — flow-definition-language (22 checks), code-app-composition-root (13), build-manifest-note (22), review-document (23 assertions), improvement-log (60 fixtures), design-doc-claims (19), plus the generator's `--check` |
| Build config preflight | **PASS — 64 steps, 49 gates**, negative-test coverage OK |
| Digest regenerated | **424 entries, 423 distinct lessons, 571 lines, 37 recurring classes**; `--check` current |
| `verify-tad-coverage.py` | **OK** — 174 column specs, 8 deferred, `TD-005` gone; 37 trustee-visible columns; 6 deliverable-now items resolve |
| This document, against the gate it edits | **OK** — `PROPOSED-COUNT` reconciles all six buckets, and still reports under a one-figure mutation, so it is live rather than dead |
| Log reconciled | 43 of 43 in scope: **30 APPLIED, 13 deferred** with a reason and a `revisit_when`; 0 left bare `unread` |
| Retirements, derived not typed | **10 retired, 80 live** — unchanged, and §4's audit stands |
| `derived-counts` | 4 drifts → **3**; the one this agent owns is cleared, the other three are delivery-owned and named in §5 |
| Level reached | **V1** for everything ([`C-TECH-053`](../../constraints/technology/technology-constraints.md#L108)). **No live DEV observation was made or attempted** — this session holds no credential, which is why 13 entries are deferred rather than closed |

**The gate did not become green, and it was not going to.** `design-doc-claims` is **RED on three
true positives**, all in one document, owner `architect-agent` — declared in the build config
rather than hidden. `C-TECH-061` also stays red: one `blocker` (`IMP-0423`) and five other entries
arrived from concurrent sessions during this application and are not this dispatch's to process.
