# Improvement Review — 2026-08-31 (review 49)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 7 `NEW` → 3 clusters (4 dispositioned, 3 deferred with reasons in §5)
**Trigger:** unread `blocker` — [`IMP-0526`](../../logs/improvement-log.jsonl), appended 2026-08-31T17:35
**WBS:** 6.9, plus system work that carries no task id
**Gate:** `APPROVE IMPROVEMENTS` — **received 2026-08-31**
**Status:** ✅ **APPLIED. Everything in this document is on disk; §10 is the record and §11 the amendment.**

> **AMENDED AT APPLICATION.** Two `blocker` findings were appended after this draft was parked at
> its gate — `IMP-0527` (18:05) and `IMP-0528` (18:40, *during* the apply pass) — and **both are
> folded in and applied**, as changes 4 and 5. §9's gate block was reconciled to the applied
> figures before this note was written; §11 records what was folded in and what remains. The
> draft's own digest figures (*"521 lessons, 41 recurring classes"*) were transcriptions and are
> **corrected** beneath §9 to the derived **524** and **39** (`IMP-0529`).

---

## Summary

**This is the second time in two days that a stylesheet shipped a defect which is pure arithmetic,
invisible to every test in the repository, and found only by a human looking at a rendered screen —
so the answer is not a second gate, it is one gate that holds the class.** Yesterday it was font
size against line height ([C-TECH-076](../../constraints/technology/technology-constraints.md#L146),
gated). Today it is column count against a grid track floor: a floor stated in pixels sets a
*minimum track width* and can never cap the number of columns, so eight tiles landed 6 + 2 where the
design said 4 + 4.

The delivery fix and its regression test were already on disk from another dispatch. What this review
added is the control that would have caught it: the line-height gate **became** a two-check
CSS-arithmetic gate, and its constraint row broadened to the class rather than the instance.
**Zero new constraints, one constraint amendment, one script, one knowledge line** — plus **two
agent-file edits** for the pair of blockers folded in at application (§11).

---

## 0. Scope, and what I excluded

[`verify-improvement-log.py`](../../scripts/verify-improvement-log.py) `--check` reports **110 NEW:
5 unread, 0 awaiting-approval, 105 reviewer-deferred, 0 already-fixed**.

My scope is the **five unread** entries, per activation step 2
([`improvement-agent.md` L100](../../agents/improvement-agent.md#L100)) — the dispatch named only the
blocker, and reading the rest is what stops the queue misreporting them. **Two are processed here**
(`IMP-0526`, the blocker; and `IMP-0523`, because its defect is in the very file change 1 rewrites).
**Three are deferred with reasons in §5.** Leaving any of them silently would be a silent cap.

**Excluded: the 105 `reviewer-deferred` entries.** Each carries a `deferred_reason` a human accepted;
none is re-derived here. **No entry is `awaiting-approval`**, so no parked document is waiting on a
keyword.

Five pre-existing `corrects` WARNINGs stand (`IMP-0290`, `IMP-0298`, `IMP-0320`, `IMP-0430`,
`IMP-0437`). None names anything this review touches; all five are left alone.

> **This section records the queue as it stood WHEN THE DRAFT WAS WRITTEN, and it moved twice
> afterwards.** `IMP-0527` and `IMP-0528` were appended after the gate opened and are folded in
> (§11); `IMP-0529` was appended by this review itself. The queue at application is **0 unread, 0
> awaiting-approval**, and `verify-improvement-log.py --check` **exits 0** — §10 and §11 are the
> current state, not this section.

---

## 1. Regression check — did the last review's changes work?

Audited against [review 48](2026-08-31-improvement-review-3.md) and against
[review 47](2026-08-31-improvement-review-2.md), which is the review that owns the CSS gate.

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| [`verify-css-line-height.py`](../../scripts/verify-css-line-height.py) + [C-TECH-076](../../constraints/technology/technology-constraints.md#L146) | 2026-08-31 | a CSS defect reducible to arithmetic that jsdom cannot see | **YES — this review's blocker** | **Right instrument, too narrow a scope.** See below |
| [`verify-source-derived-test-counts.py`](../../scripts/verify-source-derived-test-counts.py) tier-2 derive-and-compare | 2026-08-31 | `hand-maintained-count-drifts-from-source` (×19) | **No new member since it landed.** The one open member predates it and was deliberately left for its own cycle | Working — too young to call, say so |
| [`verify-field-length-limits.py`](../../scripts/verify-field-length-limits.py) `--check-fixtures` | 2026-08-31 | a known-bad fixture that stopped being bad | No | Working — leave alone |
| [`agents/WORKFLOW.md`](../../agents/WORKFLOW.md) "the dispatcher's half" | 2026-08-31 | prose fix in a class at ×7 | No | Too young to call. Its own review named the next rung |

**The first row is the finding of this section, and it is the reason for the altitude call in §2.**
The line-height gate is not broken and did not fail — I ran it, it exits 0, and **both of the live
findings it was red on yesterday are now fixed** (`.panelHeading` and `.cardTitle`). What recurred
is not its check; it is its *class*. C-TECH-076's own justification says the mechanism plainly —
*"jsdom computes no layout, so no vitest assertion in this repository could ever have seen it"* — and
that sentence is true of every arithmetic relation in a stylesheet, not only of line height. The
gate was scoped to the one property that had failed, so the next property in the same class shipped
undefended one day later. That is the altitude rule's own textbook case, and it is
[`improvement-agent.md` L356](../../agents/improvement-agent.md#L356)'s third row: a gate that exists
and did not fire is mis-scoped.

---

## 2. Clusters and promotion decisions

```
CLUSTER: css-arithmetic-invisible-to-jsdom  (x2: IMP-0509/IMP-0486 → C-TECH-076; IMP-0526)
Altitude:   CLASS — second instance. The log calls IMP-0526's class
            `unverified-arithmetic-claim-in-css-comment` (x1), but the class that actually
            recurred is the one C-TECH-076 was built for: an authored CSS declaration whose
            correctness is an ARITHMETIC RELATION between declared values, which no vitest
            assertion can see and only a human on a rendered screen catches.
Ladder row: "a tool could catch it mechanically" (script + build gate), plus the altitude
            rule — on the second instance you may not add another instance-level gate.
Becomes:    scripts/verify-css-line-height.py becomes scripts/verify-css-arithmetic.py, a
            two-check harness: check A = line-height vs the ambient body size (unchanged
            logic), check B = an auto-fit/auto-fill minmax floor that is purely absolute
            cannot cap a column count. C-TECH-076 broadens to the property. One knowledge
            line records the CSS law itself.
Retires:    the NAME verify-css-line-height.py, absorbed into the general gate. No constraint
            row is retired — C-TECH-076 is amended in place, not replaced.
Cites:      IMP-0526 (the blocker), IMP-0523 (a crash in the file change 1 rewrites),
            IMP-0509 and IMP-0486 as the first instance of the class.
Residual:   Check B cannot read intent. A grid that is DELIBERATELY uncapped — as many columns
            as fit, no maximum — is a false positive by construction. Measured at zero in this
            corpus (2 declarations, both container-relative), and the escape must be a
            DECLARED VALUE (an explicit `repeat(N,` or a container-relative term), never a
            comment phrase — a comment escape hatch is the instrument this project has
            measured at 48-100% false five times (improvement-agent.md L500).

CLUSTER: gate-reassures-wrongly  (x27: IMP-0527)
Altitude:   NOTE, deliberately. The mechanical half already exists AND ALREADY WORKED —
            verify-improvement-log.py fired correctly, as build.yml's HARD step 3, and
            halted the build. What failed is a human-readable claim written OVER its
            result: a routing note asserted the gate was "not itself a build gate" while
            it was the literal third step of the config being dispatched.
Ladder row: prose, because the thing needing a check is the semantics of a dispatch note,
            and a gate reading a markdown note for semantics is the 48-100%-false
            instrument (improvement-agent.md L204). There is also no artefact: a dispatch
            brief is a Task-tool prompt, never written to a file.
Becomes:    agents/lead-agent.md's pre-dispatch paragraph gains the exit-code rule — read
            $?, not the state breakdown; "already routed to a review" is not a discharge.
Cites:      IMP-0527.

CLUSTER: credential-not-on-the-machine-that-needs-it  (x4: IMP-0048/0061/0105; IMP-0528)
Altitude:   NOTE at instance altitude, and this is NOT the altitude rule being dodged. The
            finding itself states the protocol already routes this correctly and that only
            the round-trip is wasted — there is no defect to gate, and the credential's
            absence from agent sessions is a SECURITY CONTROL working as designed, never a
            thing to route around (improvement-agent.md L15-20).
Becomes:    a briefing rule: name the credential-dependent step in the dispatch and say it
            is expected to stop at REVIEWER ACTION REQUIRED.
Cites:      IMP-0528.
```

**Rejected: the finding's own proposed change.** `IMP-0526` proposes adding a CSS-layout-claim check
to [`skills/accessibility-checklist.md`](../../skills/accessibility-checklist.md). That is the wrong
home twice over. The defect was not an accessibility defect — the 240px floor's WCAG 1.4.10 reflow
guarantee was, and remains, correct — and an author writing a grid has no reason to open the
accessibility checklist, so the line would be read by the wrong person at the wrong moment. It is
also prose where a value check is available, which the ladder puts one rung lower.

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | script | `scripts/verify-css-arithmetic.py` (renamed from [`verify-css-line-height.py`](../../scripts/verify-css-line-height.py)) | Two-check harness. Check A is the existing line-height logic, unchanged. **Check B**: every `grid-template-columns: repeat(auto-fit\|auto-fill, minmax(<floor>, …))` in an authored stylesheet must carry a container-relative term in its floor. Also fixes the `TypeError` crash on the explicit-root path ([L258](../../scripts/verify-css-line-height.py#L258)) | IMP-0526, IMP-0523 | YES — `python3 scripts/verify-css-arithmetic.py`, and `--selftest` | `HARD`, replacing step `css-line-height` at [`build.yml` L1377](../../config/revitalise-grant-automation-build.yml#L1377) |
| 2 | constraint-amendment | [`technology-constraints.md` L146](../../constraints/technology/technology-constraints.md#L146) | C-TECH-076 broadens from "a rule above the ambient size declares its own line-height" to the property — an authored CSS declaration whose correctness is arithmetic against another declared value is checked mechanically — with the two checks named beneath it and the `Verify By` command updated | IMP-0526, IMP-0509 | YES — same command | N/A |
| 3 | knowledge | [`knowledge/technology/code-apps.md`](../../knowledge/technology/code-apps.md) | One line stating the CSS law: an `auto-fit`/`auto-fill` `minmax()` floor in absolute units sets a **minimum track width**, never a maximum column count; capping the count needs a container-relative floor or an explicit track list | IMP-0526 | N/A — reference line | N/A |

**Constraint budget: 0 of 3 used.** Row 2 is an amendment to an existing row, not a new one.

### Measured before wiring, per [`improvement-agent.md` L454](../../agents/improvement-agent.md#L454)

Check B was written as a candidate and run over the real corpus — the five authored stylesheets under
`src/code-apps/trustee-review-portal/src/styles/`, not `node_modules/` or `dist/`:

| Corpus | Declarations found | Findings | True | False |
|---|---|---|---|---|
| HEAD (post-fix) | 2 | **0** | — | — |
| The pre-fix tree (`ba50830^`) | 1 | **1** | **1** | **0** |

**Polarity is proven on a value, not on a phrase.** The one finding against the pre-fix tree is
`minmax(240px, 1fr)` — the exact declaration that produced the reviewer's 6 + 2 screen — and it
stops being reported the moment the fix lands, which is the same proof shape C-TECH-076 used against
`HEAD~1`. **Zero findings against HEAD is the correct result here and not the "0 findings is the
tell" trap**: the instance this corpus contained was fixed by another dispatch four hours ago, and
the git-history run is what demonstrates the gate would have caught it.

**Stated plainly: this gate has no live finding to stand on.** Its evidence is a history replay over
a two-declaration corpus. That is weaker than the line-height gate's two live true positives, and it
is the honest reason to fold it into an existing gate rather than ship it as a script of its own.

---

## 4. Retirements

| ID / file | What it was for | Why retired | Replaced by | Coverage proven? |
|---|---|---|---|---|
| the **name** `scripts/verify-css-line-height.py` | one CSS arithmetic property | the class recurred with a second property one day later | `scripts/verify-css-arithmetic.py` check A, logic byte-for-byte | **To prove at application time** — both existing fixtures must still fail under the renamed gate, and the live tree must still exit 0 |

> Retirement check performed: 82 live constraint rows and 10 already retired reviewed. **None is
> currently redundant.** C-TECH-076 is the only candidate this cluster touches and it is being
> broadened rather than replaced — retiring it would lose the line-height coverage that is working.

A rename obliges the grep-and-classify step in
[`how-to-promote-a-finding.md` L88](../../skills/how-to-promote-a-finding.md#L88). The literal token
`verify-css-line-height` appears in **7 files**: the script itself and the build config (*call
sites*), C-TECH-076's `Verify By` (*instruction* — rewritten by change 2), one improvement-log entry's
`proposed_change` (*instruction* — annotated when `IMP-0523` closes), and a test report plus two prior
reviews (*history* — left exactly as they are).

---

## 5. Findings left unprocessed

**Deferred:** IMP-0522, IMP-0524, IMP-0525

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| IMP-0522 | `hand-maintained-count-drifts-from-source` | Already directed to its own cycle by explicit reviewer instruction during review 48; a `friction` NOTE, not a trigger. Re-deriving it here would be the re-derivation activation step 2 exists to prevent | the next review that is not a blocker escalation |
| IMP-0524 | `stale-claim-contradicting-rechecked-source` | Proposes no rule change by its own account — it corrects a snapshot fact recorded inside another entry. I confirmed the correction: the two rules it names are fixed and the gate now exits 0 | no revisit needed; it is informational, and the state it records is now the current state |
| IMP-0525 | `revision-header-committed-ahead-of-implementation` | Proposes an edit to [`agents/development-agent.md`](../../agents/development-agent.md) about treating a revision header in a working tree as a claim. Sound, and a different cluster from this blocker; folding it in would make a single-blocker dispatch a general pass | the next review that touches development-agent's resume guidance |

---

## 6. Improvement log

`IMPROVEMENT LOG:` 2 findings processed (`IMP-0526`, `IMP-0523`); **0 new findings appended at draft
time.**

All five unread entries are stamped `reviewed_in: docs/improvements/2026-08-31-improvement-review-4.md`
**now, at draft time**, per [`improvement-agent.md` L127](../../agents/improvement-agent.md#L127).
`status` stays `NEW`; `applied_by` does not exist until something is applied.

Dispositions on approval:

| Finding | Disposition | Closure evidence |
|---|---|---|
| `IMP-0526` | **stays `NEW`, with a `deferred_reason` and a `revisit_when`** | `observable_at: V4`. The CSS fix and [`layout.test.ts`](../../src/code-apps/trustee-review-portal/src/styles/layout.test.ts#L50) are on disk, and the test asserts the *declaration*, not a rendered column count — only a signed-in human on a deployed build can observe 4 + 4. Closing it on a green suite would be exactly the false closure `IMP-0224`/`IMP-0225` cost. **A `deferred_reason` and not a bare `revisit_when`**, because a bare one leaves a blocker red on the gate forever ([`improvement-agent.md` L320](../../agents/improvement-agent.md#L320)) |
| `IMP-0523` | `APPLIED` — change 1 | `observable_at: V1`, and I reproduced it: `python3 scripts/verify-css-line-height.py src/code-apps` raised `TypeError` at L258 while the no-argument run passed. `reobserved` records re-running that same command against the renamed gate: exit 1 with a readable ERROR, no traceback |
| `IMP-0527` | `APPLIED` — change 4 (**folded in**, §11) | `observable_at: V2`. `reobserved` records the exact command the finding names, read the way the finding says it must be read: **exit code 0**, 0 unread, 0 awaiting-approval, both blocker TRIGGER lines gone. That is the condition `build-agent`'s step 3 evaluates |
| `IMP-0528` | `APPLIED` — change 5 (**folded in**, §11) | `observable_at: n/a` — no reobservation is required or possible. It is a briefing rule; the finding's own text records that the protocol already handles the case correctly |

**Simulated before parking**, per [`improvement-agent.md` L330](../../agents/improvement-agent.md#L330):
these dispositions applied to a scratch copy of the log take the queue to **0 unread, 0
awaiting-approval**, and **the blocker rung clears**. The real log was restored and confirmed
byte-identical to `HEAD` afterwards.

---

## 7. Work this review ROUTES rather than performs

**Re-measure every row immediately before dispatching it**, per
[`improvement-agent.md` L184](../../agents/improvement-agent.md#L184).

| Routed to | What | State as measured at draft time | Action |
|---|---|---|---|
| architect-agent | **The architecture document still carries the disproved arithmetic.** TAD ADR-041 states the 240px floor lands "typically 4, matching the ui_kit, on the widths this screen is used at today" | **RE-MEASURED AT APPLICATION — still open, and the draft's own state description was already stale.** Corrected below | **Dispatch.** The correction is an erratum on ADR-041 that *retains* the withdrawn sentence, per this repository's own convention |

**The draft measured "the document's header reads Revision 7; the TAD has no Revision 8". It has one now.**
Between the gate opening and the keyword, the TAD advanced to **Revision 8**
([L17–L26](../architecture/trustee-portal-visual-refresh-architecture.md#L17)) — which is exactly the
interval `IMP-0405` and `IMP-0517` exist to make me re-measure, and this row is the third time that
interval has moved something under a review.

**But the substance survives re-measurement, so this is a dispatch and not a withhold.** Revision 8 is
about A-R24 and the `rev_ethnicgroup` release ([§0.11, L656](../architecture/trustee-portal-visual-refresh-architecture.md#L656));
it records no erratum on ADR-041. The disproved sentence is still live at
[L3840–L3860](../architecture/trustee-portal-visual-refresh-architecture.md#L3862), still asserting
*"typically 4, matching the ui_kit, on the widths this screen is used at today"*, while
[`app.module.css` L988](../../src/code-apps/trustee-review-portal/src/styles/app.module.css#L988) now
carries the container-relative floor that actually caps the count. So it is none of the three
withhold conditions — not a closed reviewer decision, not a shipped fix, not a superseded diagnosis.
It matters because the ADR is what the next author reads before touching that grid, and it currently
teaches the arithmetic that failed.

**One scope note for whoever takes it:** `C-TECH-076` now names `architect-agent` in its Applies-To
column, which it did not before. The rule this ADR broke is now binding on the agent that wrote it.

This is not mine to fix: `docs/architecture/` is architect-agent's deliverable. It matters because
the ADR is the document the next author reads before touching that grid, and it currently teaches
the exact arithmetic that failed.

---

## 8. Digest impact

**Every figure below is DERIVED at application time**, from the generator's own stdout and from a
grep of the file it wrote — the draft's were transcribed, and all four were wrong (`IMP-0529`).

| | Draft claimed | Measured before | Measured after |
|---|---|---|---|
| Log entries | 523 | **524** | **526** |
| Distinct lessons | 521 | **522** | **524** |
| Recurring classes (x≥2) | 41 | **39** | **39** |
| Digest lines | 600 | **602** | **602** |

Three entries were appended across this review's life, none of them by the draft: `IMP-0527` and
`IMP-0528` arrived from other sessions and are folded in (§11), and `IMP-0529` is this review's own
finding about the wrong figures above. **No new recurring class**: both folded blockers joined
existing rows (`gate-reassures-wrongly` ×26 → ×27, `credential-not-on-the-machine-that-needs-it`
×3 → ×4).

Derive, never retype:

```bash
python3 scripts/generate-known-failure-modes.py          # prints entries + distinct lessons
grep -c '^| \*\*x' logs/known-failure-modes.md          # recurring classes
python3 scripts/generate-known-failure-modes.py --check  # confirms current
```

---

## 9. Gate

**RECONCILED AT APPLICATION**, after two blockers appended between the draft and the keyword were
folded in (§11). The figures below are the applied ones, not the draft's.

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-31-improvement-review-4.md

Findings processed: 7 NEW  →  3 clusters  (4 dispositioned, 3 deferred with reasons)
                    +1 appended by this review (IMP-0529)
Regression check:   4 prior changes audited, 1 class recurred
Proposed:           0 constraints (cap 3), 1 constraint amendment, 1 gates/scripts,
                    1 skill/knowledge edits, 2 agent-file edits, 1 retirement
Altitude calls:     1 generalised from instance to class, 2 left as notes
Digest:             regenerated — 524 lessons, 39 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

**The draft's own digest figures were wrong and are corrected here, not carried forward.** It
stated *"521 lessons, 41 recurring classes"*; the generator reports **524 distinct teaching
lessons** (523 before this review appended `IMP-0529`) and `grep -c '^| \*\*x' logs/known-failure-modes.md` returns **39**. Both were draft-time
transcriptions rather than derived counts — the defect `IMP-0262` records about this agent's own
reports. Neither folded-in blocker created a new recurring class: `gate-reassures-wrongly` went
×26 → ×27 and `credential-not-on-the-machine-that-needs-it` ×3 → ×4, both already in the table.

---

## 10. Applied

**`APPROVE IMPROVEMENTS` received 2026-08-31. Everything below is on disk.**

| # | Change | Landed | Evidence |
|---|---|---|---|
| 1 | [`scripts/verify-css-line-height.py`](../../scripts/verify-css-line-height.py) → [`scripts/verify-css-arithmetic.py`](../../scripts/verify-css-arithmetic.py), broadened to two checks; `IMP-0523`'s crash fixed | ✅ | `--selftest` **5 fixtures, 0 failures**; live tree exit 0; pre-fix tree exit 1 |
| 2 | [C-TECH-076](../../constraints/technology/technology-constraints.md#L146) broadened from the property to the class; `Verify By` and Applies-To updated | ✅ | `verify-constraint-verifiers.py` PASS — 99 paths across 82 active rows resolve |
| 3 | [`knowledge/technology/code-apps.md`](../../knowledge/technology/code-apps.md#L643) — the CSS law, under Styling | ✅ | present on disk with a worked `max()` example |
| 4 | [`agents/lead-agent.md`](../../agents/lead-agent.md#L231) — read the gate's EXIT CODE, not its narrative (`IMP-0527`, **folded in**) | ✅ | needle `READ ITS EXIT CODE, NOT ITS NARRATIVE` |
| 5 | [`agents/lead-agent.md`](../../agents/lead-agent.md#L171) — briefing rule 4, credential-dependent steps (`IMP-0528`, **folded in**) | ✅ | needle `If a step of the brief needs the DEV provisioning credential` |
| — | [`config/revitalise-grant-automation-build.yml`](../../config/revitalise-grant-automation-build.yml#L1376) step `css-line-height` → `css-arithmetic` | ✅ | `verify-build-config.py` PASS — **70 steps, 55 gates**, negative-test coverage OK |

### Measured at application, not inherited from the draft

**Check B, over the 5 authored stylesheets** — the same corpus, re-run rather than re-quoted:

| Corpus | `auto-fit` declarations | Findings | True | False |
|---|---|---|---|---|
| HEAD | 2, both container-relative | **0** | — | — |
| Real pre-fix tree (`ba50830^`) | 1, `minmax(240px, 1fr)` | **1** | **1** | **0** |

The one finding is the exact declaration that produced the reviewer's 6 + 2 screen. Polarity is
asserted on a **value** — is there a container-relative term in the floor? — never on a phrase.

**Retirement coverage proven rather than assumed**, which §4 listed as "to prove at application
time": run over `19102e4` the renamed gate reports **all three** historical defects —
`.panelHeading` and `.cardTitle` (check A) plus `.statTiles` (check B). Nothing was lost in the
rename. `ls scripts/verify-*.py | wc -l` is **54**, unchanged, because a rename adds no script —
so `improvement-agent-verify-script-count` needed no edit and `verify-derived-counts.py` does not
report it.

### One correction to a finding's own root cause, established by EXECUTING it

`IMP-0523` states the crash is an argument-parsing branch that *"skips whatever sets `base`"*.
**Nothing skips it.** `scan()` sets `base` along one path for every root; what differed is that
`<root>/src/code-apps/*/src/**/*.css` matched **no file** when the root was itself `src/code-apps`,
so `scan()` returned `([], None, 0)` and `main()` fell through to the **PASS** branch and formatted
`None`. The defect is therefore not argument parsing at all — **an empty corpus was on the PASS
path**, which is `gate-cannot-fail` ([`IMP-0007`](../../logs/improvement-log.jsonl)) wearing a
`TypeError`. Fixed at that altitude: an empty corpus now ERRORs and exits 1 for **any** root,
including the default, and selftest case C is the negative control. Reading the source would have
produced the narrower fix; running it produced this one ([`IMP-0426`](../../logs/improvement-log.jsonl)).

### Nothing was withheld, and nothing was narrowed

Every proposed change survived re-verification intact. No `NARROW-AND-REPORT` deviation was needed,
and no premise was disproved between the draft and the keyword.

---

## 11. Amendment — two blockers folded in after the draft was parked

**Both were appended after §9 opened, and both are on disk. Nothing from this amendment remains
outstanding.**

| Finding | Appended | Why folded in rather than held |
|---|---|---|
| `IMP-0527` | 18:05, by build-agent | **It is the blocker sitting on the gate this review's own keyword exists to clear.** Leaving it `NEW` would have kept `C-TECH-061` red and re-halted the `wbs:6.9` build at step 3 for a second time — the outcome the dispatch was sent to prevent |
| `IMP-0528` | 18:40, by identity-agent, **during this apply pass** | Found because step 8 re-reads the log's maximum id before writing ([`IMP-0080`](../../logs/improvement-log.jsonl), `IMP-0312`). Same trigger, same file, same section as change 4 — holding it would have cost a second strategic dispatch to reopen a file this one had open |

Both are `blocker` severity, which is a *"do not batch"* trigger in its own right, so neither could
be deferred to a follow-up batch without leaving the queue red. Neither is a defect in anything
this review proposed: no `corrects` field names any finding here, and no premise moved.

**The routed-work row in §7 was re-measured before being handed on** and its state description was
already stale — the TAD is at Revision 8, not Revision 7. The substance survives, so it is
dispatched with a corrected measurement rather than withheld; §7 carries the detail.

**What remains:** one dispatch to `architect-agent` for the ADR-041 erratum (§7), and three findings
deferred with recorded reasons (§5). `IMP-0526` stays open on its V4 half — only a signed-in human
on a deployed build can confirm 4 + 4.
