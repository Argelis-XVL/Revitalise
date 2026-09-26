# Improvement Review — 2026-09-24 (4)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 2 NEW → 1 clusters (1 already-`APPLIED` entry stamped; 1 further `NEW`
entry excluded, named in §5)
**Trigger:** blocker escalation — `IMP-0874`, unread
**Gate:** `APPROVE IMPROVEMENTS`
**Status:** ~~DRAFT — parked at the gate, nothing applied~~ **APPLIED 2026-09-24** — approved as
drafted, including both recommended answers in §5. Five changes landed, two entries closed, one
stamped. See §8.

---

## Summary

A form was corrected in the file, and the thing that ships was packed from the folder. `IMP-0874`
is that gap: `pac solution pack` reads the `FormXml/<foldername>/` path segment and ignores the
file's own `type` attribute, so three Quick View Forms kept shipping the value a live import had
already rejected, while every local gate reported OK.

development-agent has fixed it, and the fix holds — I re-ran the packer and the new gate myself
rather than reading the summary that describes them (§1). Two things remain, and both are small.

**First, the sentence that caused it is still in the repository, twice.** The disproved claim —
*"the folder name is a repository path, not a platform value"* — sits in
`constraints/technology/component-shapes.yml` (which development-agent could not edit) and, missed
by the closure sweep, in the header comment of the very Quick View Form that the other two forms
tell the reader to consult. That second copy is new and is logged as `IMP-0876`.

**Second, the new gate cannot fire before a build.** `component-shape-packed` runs after
`pack-unmanaged`, so it is correctly absent from `run-source-gates.py` — which means no pre-build
dispatch can catch this class recurring. The fix for that is not another script: the folder name
and the attribute are both **values**, so one comparison inside the gate that already reads these
files closes the window. I built it and measured it against a reconstruction of the pre-fix tree:
it catches all three forms, pre-pack, where today's gate reports OK (§3).

Net: **0 new constraints, 0 new scripts, 1 gate extension, 2 prose corrections.**

---

## 1. Regression check — did the last review's changes work?

The last review applied was [review 3 of 2026-09-24](2026-09-24-improvement-review-3.md). It
proposed no gate, deliberately, and made two prose edits to the closure-sweep rules.

| Prior change | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|
| Sweep command in [how-to-promote-a-finding.md](../../skills/how-to-promote-a-finding.md) §2.4 — `--recurse-submodules`, no extension filter | fix-time sweep misses a referrer | **Partly** | Worked as written. The `IMP-0875` dispatch ran it and found `src/tests/` and a sibling source file that the narrower command would have missed |
| Closure rule in [how-to-verify-a-platform-contract.md](../../skills/how-to-verify-a-platform-contract.md) §4 — sweep the *withdrawn literal*, and `src/tests/` as a fifth location | same | **Yes, once** | One survivor: the header comment **inside the file being corrected**. Logged as `IMP-0876` |
| `entity form` shape block + `attribute_values` (review 2) | `platform-contract-guessed-not-groundtruthed` | **Yes** — `IMP-0874` | The gate did what it says; what it says was scoped to source |

**The regression-check table's own rule applies to row 2 and I am following it.** A recurrence
after a *prose* change is evidence of wrong altitude, and the remedy is a gate rather than a third
round of prose. The gate is in §3, and it is a **value** comparison, not a phrase search — review 3
declined the phrase-search form after measuring it at 25% precision, and that judgement stands.

| Question | Answer |
|---|---|
| Did a gate exist and not fire? | **No.** `component-shape` fired correctly on what it reads. Its scope was source; the deployable is the packed zip. Not a `gate-cannot-fail` |
| Did closure evidence match the level the defect was visible at? | Yes for review 3's entries. `IMP-0874` is V2 and is closed here on a V2 re-observation I ran myself (§7), not on a document |
| Was the brief's stated class correct? | **No — see §2.** `IMP-0874`'s `class_instance_of` is `platform-contract-guessed-not-groundtruthed` (×68). `gate-scope-mismatch` (×25) appears only in its `why_it_was_never_caught`, so `IMP-0874` is not a member of the ×25 corpus |

---

## 2. Clusters and promotion decisions

### The premise I was asked to act on, re-measured

The dispatch asked for an altitude call on whether `component-shape-packed` is the right
generalisation for the **`gate-scope-mismatch` class at ×25 recurrence**. Before answering I
classified that corpus one member at a time, because a count that ranks remedies is re-derived and
not transcribed.

| What the ×25 corpus actually contains | Members |
|---|---|
| A gate's **default input path** is narrower than the rule it claims to enforce | `IMP-0382`, `IMP-0425`, `IMP-0862` — **all three the same script**, `verify-tad-coverage.py` |
| A gate's **table/entity filter** excludes rows the rule covers | `IMP-0410`, `IMP-0690`, `IMP-0709`, `IMP-0839` |
| A gate reads **documentation** where the rule is about **source**, or the reverse | `IMP-0427`, `IMP-0430`, `IMP-0455`, `IMP-0503`, `IMP-0505` |
| A gate's corpus excludes **untracked or gitignored** files | `IMP-0003`, `IMP-0591`, `IMP-0847` |
| Environment/config sets out of step | `IMP-0401`, `IMP-0472`, `IMP-0595`, `IMP-0666`, `IMP-0760` |
| Log/bookkeeping scope | `IMP-0432`, `IMP-0437`, `IMP-0445`, `IMP-0516`, `IMP-0607` |
| **Source checked, packed artifact deployed** | **none** |

**So the ×25 recurrence is not evidence for or against this gate.** Not one of the twenty-five is a
source-versus-packed-artifact mismatch; `IMP-0874` would be the first, and it is filed under a
different class. A generalisation drawn from the ×25 figure would have been drawn from a corpus
that does not contain the defect.

What the table *does* show is a genuine ×3 sub-cluster — one script's single-path `--tad` default —
that no review has yet generalised. It is outside a blocker dispatch's scope and I have not widened
into it; it is named in §5 so the next batch review inherits it rather than re-deriving it.

### The cluster this review acts on

```
CLUSTER: a platform value derived from a PATH SEGMENT, corrected only in the file   (x2)
Altitude:  CLASS — IMP-0874 (the packed wrapper kept the folder's value) and IMP-0876
           (the prose claim that the folder is inert survived the closure sweep, in the
           file the other two forms delegate to). One mechanism, two surfaces.
Ladder row: "a tool could catch it mechanically" — and, for the recurrence after review 3's
           prose edit, "the system's own memory failed" escalated to the mechanical home.
Becomes:   one `attribute_from_path_segment` key in component-shapes.yml plus ~12 lines in
           the gate that already reads these files. No new script, no new constraint row.
Retires:   nothing — see §6, including why verify-packed-form-types.py is NOT subsumed.
Cites:     IMP-0874, IMP-0875, IMP-0876
Residual:  The coupling is declared per shape, by hand. A future packer behaviour keyed to a
           different path segment is not covered until someone declares it — this gate
           enforces a coupling, it cannot discover one. The packed comparison is what
           catches an undeclared coupling, which is why both gates stay.
```

---

## 3. The gate extension, and the measurement that decided it

`scripts/verify-packed-form-types.py` (build step `component-shape-packed`) is **correct and stays
wired**. It is a comparison keyed on `formid`, not a restatement of the vocabulary, so it
generalises across every form and every form type without a per-instance patch. It is the right
answer to the question *"does the artifact still say what the source says?"*.

It cannot answer a different question: *"is this source tree going to pack wrong?"* — because it
needs a packed zip, which exists only after `pack-unmanaged`. `run-source-gates.py` correctly lists
it under **NOT covered by this run**, so the step-8 command every delivery dispatch runs is blind to
a recurrence of exactly this defect until a full build has gone.

That window closes with a **value comparison** in the source gate: the root `type` attribute must
equal the containing folder name. Both sides are values, so none of the prose-gate polarity traps
apply.

### Measured against the real corpus, four runs

| Run | Corpus | Result |
|---|---|---|
| **M1** | the real solution, 56 hand-authored files across 3 shapes | **0 findings, exit 0.** 0 is correct *because the folder was renamed today* — M3 is the control that proves the check is not vacuous |
| **M2** | `src/tests/fixtures/known-bad/component-shape/` | **1 additional finding, true positive.** The fixture's attribute (`quickview`) genuinely disagrees with its folder (`quick`). Its existing vocabulary finding still fires, so no current Pester assertion changes meaning |
| **M3** | the **pre-fix tree reconstructed** — folder `FormXml/quickview/`, files declaring `type="quick"` | **3 findings, 3 true positives, 0 false, exit 1.** All three Quick View Forms, named individually, pre-pack |
| **M4** | the *same* pre-fix tree, through **today's unmodified gate** | **`component-shape: OK — 56 component file(s)`, exit 0** |

**M3 against M4 is the whole case.** On byte-identical input, the extended gate names the defect
that cost a build cycle and the current gate reports a clean run.

**Precision: 4 findings across the two defective corpora, 4 true positives, 0 false.** The finding
message names the remedy in the terms the platform actually uses — *"rename the containing folder to
match; editing this file alone changes nothing"* — because the wrong remedy is the one that has now
been attempted twice.

**Level reached, per `C-TECH-053`: V2.** The gate was executed against four corpora, including a
live `pac solution pack` run of the real solution. It has not yet run inside a build.

---

## 4. Proposed changes

Nothing below is applied. All of it lands on `APPROVE IMPROVEMENTS`.

| # | Change | File | Cites |
|---|---|---|---|
| 1 | Replace the disproved inert-folder claim; add `attribute_from_path_segment: type` and its note | `constraints/technology/component-shapes.yml` | `IMP-0874` |
| 2 | Assert the named root attribute equals the containing folder name (~12 lines), in **both** copies | `scripts/verify-component-shape.py`, `.engine/scripts/verify-component-shape.py` | `IMP-0874`, `IMP-0876` |
| 3 | One assertion for the new finding; correct the fixture comment that now overstates the independence | `src/tests/build/BuildGates.Tests.ps1` | `IMP-0874` |
| 4 | Correct the surviving header comment the closure sweep missed | `src/solutions/.../FormXml/quick/{7f145e5b-…}.xml` line 27 | `IMP-0876` |
| 5 | Two registered derived counts drifted by other work and by this review's own regeneration | `agents/improvement-agent.md` (64→65), `scripts/generate-known-failure-modes.py` | `IMP-0657` |

### Change 1 — the exact replacement text

The current comment at `component-shapes.yml` lines 79–81 and the `attributes_note` beneath it are
the claim `IMP-0874` disproves. development-agent proposed replacement wording; I have tightened it
rather than transcribing it, because the proposed version described the coupling as a fact about
*packing* and it is better stated as a fact about **where the value is read from**, which is what
makes the remedy obvious.

Replacing the two-line comment:

```yaml
    # TWO INDEPENDENT VALUES, and both are the platform's, not this repository's. The root
    # <forms type> attribute is what Dataverse's import handler validates. The FormXml/<folder>/
    # name is what `pac solution pack` reads to write the packed <forms type> WRAPPER — it does
    # not read this attribute at all. Correcting the file without renaming the folder therefore
    # changes NOTHING in the artifact that ships (IMP-0874, reproduced with a real pack run).
    attribute_from_path_segment: type
    path_segment_note: >
      The containing FormXml/<foldername>/ segment is NOT inert. `pac solution pack` derives the
      packed customizations.xml <forms type> wrapper from it and ignores this file's own attribute,
      so the two must agree here, at source, before a pack exists. Three Quick View Forms declared
      type="quick" inside FormXml/quickview/ and shipped type="quickview" to a live import that had
      already rejected it (IMP-0874). Rename the folder to match the attribute; editing this file
      alone has zero effect. `scripts/verify-packed-form-types.py` (build step
      component-shape-packed) re-checks the same property against the packed artifact, which is
      what catches a coupling nobody has declared here.
```

The existing `attributes_note` and `ground_truth` blocks are **unchanged** — they are accurate, and
the `IMP-0866` incident they narrate is history, not a stale instruction.

---

## 5. Decisions for the reviewer

**Should the ×3 `verify-tad-coverage.py` scope-default sub-cluster (`IMP-0382`, `IMP-0425`,
`IMP-0862`) be picked up by the next batch review, or dispatched now?**
I have not widened into it. It is three instances of one script taking a single hand-picked `--tad`
path while its sibling argument `--design-docs` already scans a directory, so the generalisation is
obvious and cheap — but all three are `friction`, none blocks anything, and a blocker dispatch that
processes the queue around it is the failure `IMP-0183` records. `IMP-0862` stays `NEW` with
`excluded_by` naming this review.

**Is change 4 mine to make?** Line 27 of a shipped solution file is `development-agent`'s territory
by ownership and mine by the repository-fact rule — it is a prose note, settled by the grep I had
already run, with no functional effect. I propose to apply it; say so if you would rather it went
back with the next delivery dispatch.

---

## 6. Retirement

**Checked, and one candidate considered and rejected with a reason.**

`scripts/verify-packed-form-types.py` is the only thing change 2 could plausibly subsume: both
check the same property. **They do not cover the same window.** The source check proves the folder
and the attribute agree *in the tree*; the packed check proves the *artifact* matches the tree. A
stale artifact, a build that packed a different tree, or a future packer that derives the wrapper
some third way defeats the first and is caught by the second — and the third of those is precisely
the residual named in §2. Retiring it would trade a measured defence for tidiness.

Derived at application time: 10 retired constraint rows, 86 live rows,
65 `scripts/verify-*.py` checks. **This review adds none of any of them.**

---

## 7. Dispositions

| Entry | `observable_at` | Disposition | Why |
|---|---|---|---|
| `IMP-0874` (blocker) | **V2** | **CLOSE** | Someone in this session re-ran the original reproduction — see the record below |
| `IMP-0875` | V2 | **stamp + enrich** | Already `APPLIED` by the dispatch that fixed it, carrying no `reviewed_in`. Stamped here, and given the `reobserved` record its level requires |
| `IMP-0876` | V1 | **CLOSE** | `evidence_grep` is sufficient at V1 |
| `IMP-0862` | V1 | **EXCLUDE** | Not a blocker; `excluded_by` appended. §5 puts it to you |

**The V2 re-observation, run in this session, not read from a summary:**

```
pac solution pack --zipfile <scratch>/imprev-verify.zip \
  --folder src/solutions/RevitaliseGrantAutomation --packagetype Unmanaged --errorlevel Info
# Unmanaged Pack complete. Packed Solution.

# The original reproduction — unzip, match each formid to its enclosing <forms type> wrapper:
#   type="quick"  -> 3 form(s): ['7f145e5b', '8df85b1f', 'eed29b6a']
#   type="main"   -> 12 single-form wrappers

python3 scripts/verify-packed-form-types.py src/solutions/RevitaliseGrantAutomation <scratch>/imprev-verify.zip
# packed-form-types: OK — 15 form(s) … match their own source-declared type.   (exit 0)

# Negative control, the stale build-6 artifact IMP-0874 was filed against:
python3 scripts/verify-packed-form-types.py src/solutions/RevitaliseGrantAutomation \
  build/artifacts/revitalise-grant-automation-20260924-6/RevitaliseGrantAutomation.zip
# packed-form-types: FAILED — 3 form(s) … packed … type="quickview" (IMP-0874)   (exit 1)
```

The symptom `IMP-0874` records is gone from a fresh pack of the current tree, and still present in
the artifact the fix had not reached — which is the discrimination a closure needs.

**What this closure does not claim.** No build has run since, and no DEV import has been attempted.
`IMP-0866` and `IMP-0867` remain correctly open at V3 on their own `revisit_when`; nothing here
touches them.

---

## 8. What has landed

Approved as drafted on 2026-09-24, including both §5 answers: the header comment was corrected by
this review, and the `verify-tad-coverage.py` sub-cluster was parked for the next batch review.

**Applied in full. No change was withheld and no change was narrowed** — every premise re-verified
before application, and the disproved-claim greps in §4 were re-run against the tree at apply time
rather than trusted from draft time.

| # | Change | Landed at | Verified by |
|---|---|---|---|
| 1 | Disproved inert-folder claim replaced; coupling declared as data | `component-shapes.yml`, the `entity form` block | `component-shape` green over 56 files |
| 2 | Path-segment comparison, **both** script copies (instance and `.engine`, confirmed byte-identical) | `verify-component-shape.py` | 4 corpora, below |
| 3 | Two new assertions — one negative on the fixture, one positive control on the real solution | `BuildGates.Tests.ps1` | Pester 15/15 green across both `component-shape` blocks |
| 4 | Surviving header comment corrected, withdrawn wording retained as a quoted retraction | the `{7f145e5b-…}` Quick View Form | `git grep` — no live instance of the claim remains |
| 5 | Two registered derived counts re-derived | `agents/improvement-agent.md`, `generate-known-failure-modes.py` | `verify-derived-counts.py` clean |

**Corpus measurement, re-run against the applied files rather than the prototype:** the known-bad
fixture now yields 4 findings (3 pre-existing, 1 new — the fixture's attribute genuinely disagrees
with its folder), and the reconstructed pre-fix tree yields 3, one per Quick View Form, before any
packing. The real solution yields 0, and the pre-fix control is what proves that 0 is a measurement
rather than a vacuous pass. **4 true positives, 0 false.**

**Entries.** The critical finding is closed with a V2 `reobserved` record — a live `pac solution
pack`, the packed `customizations.xml` read directly, and the new packed gate run against both the
fresh artifact and the stale one. The fix entry, already `APPLIED` by the dispatch that made it,
was stamped with this review and given the same record, which its level required and it lacked.
The new finding is closed at V1 on its needle.

**Deviation from the letter of activation step 6, recorded because it was deliberate.** That step
stamps `reviewed_in` on every processed entry at draft time. Doing so on the already-`APPLIED` fix
entry made the log validator report that this review's keyword had already been given and that the
critical finding had been "left behind" — a false signal caused by the stamp itself. That one stamp
was therefore deferred to apply time; the two `NEW` entries were stamped at draft time as the step
requires.

**Level reached, per `C-TECH-053`: V2.** Every gate and test named above was executed. Nothing here
has run inside a build, and no environment import has been attempted.

---

## 9. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-24-improvement-review-4.md

Findings processed: 2 NEW  →  1 clusters
Regression check:   3 prior changes audited, 2 classes recurred
Proposed:           0 constraints (cap 3), 1 gates/scripts, 0 skill/knowledge edits,
                    1 agent-file edits, 0 retirements
Altitude calls:     1 generalised from instance to class, 1 left as notes
Digest:             will regenerate — 1 lessons, 1 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```
