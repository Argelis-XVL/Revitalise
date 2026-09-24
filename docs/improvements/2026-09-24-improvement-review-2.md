# Improvement Review — 2026-09-24 (2)

**Status:** APPLIED 2026-09-24, on `APPROVE IMPROVEMENTS` with both section 5 decisions answered.
Previously recorded DRAFT. Everything in section 6 is on disk; the apply-time record, including the
one deviation, is section 8.

**Trigger:** one unread critical finding, routed immediately rather than batched. A second
finding arrived from the fixing dispatch while this was being drafted and is folded in, and this
review logged a third of its own — three findings, two clusters.

---

## Summary

A form file was hand-written with a made-up label in it, and the label was the one thing nobody
checked against the platform. It packaged cleanly, then the live import threw it out. The label
had been properly flagged as a guess, but the register row pointed at the packaging step as the
thing that would settle it — and packaging cannot settle it, so the guess was marked closed on
evidence that never touched the question.

The source is already fixed, correctly, by a separate dispatch. That dispatch also added a new
build check — and this is where the review turns. **This project already has a general check for
exactly this kind of problem**, built in August, wired, and green. It missed the form files only
because its reference table had never been told about forms. So the repository now has two checks
for one rule, and the new one passes when pointed at a directory that does not exist.

What this review proposes is therefore consolidation, not addition: teach the existing check about
forms, and retire the new one. That is what the rule on second instances requires, and the new
check's own known-bad test file still fails under the general one, which is the proof that
retiring it loses nothing.

One thing needs your decision, in section 5: the finding cannot honestly be *closed* by anyone
sitting here, because closing it means watching a live import succeed.

---

## 1. Regression check — did the last review's changes work?

The last review to be approved and applied was
[review 6 of 2026-09-23](2026-09-23-improvement-review-6.md). Its change was prose, in
[development-agent's own activation file](../../agents/development-agent.md): tell the agent
authoring a new provisioning script to run three checks that already existed, before handing the
work on.

| Question | Answer |
|---|---|
| Has any finding in that class appeared since? | **No.** The class it addressed has two members, both from the incident that produced the change, and nothing since. |
| Was the change prose, or a mechanical gate? | Prose — deliberately, because the gates involved were correct and had fired. |
| Did the gate run? | Not applicable; no gate was added. |
| Did the closure evidence match the level the defect was visible at? | Yes. Those entries were visible from source alone and were closed on source evidence. |

**The audit that matters for *this* review is a different one**, and it is the reason section 2
proposes no new script. The check that should have caught today's failure —
[`verify-component-shape.py`](../../scripts/verify-component-shape.py), wired as the
[`component-shape` build step](../../config/revitalise-grant-automation-build.yml#L378) — exists,
runs, and is green. It was built in August for exactly this class of problem, deliberately as one
check reading one reference table rather than a script per component type. It did not fire because
that table has no entry for forms, and because the table cannot currently express the kind of rule
this needed.

That is a coverage gap in a working check, not a missing check. It is also the second time in two
months that this distinction has been missed: a finding proposing a new gate for a property an
existing gate already owns is a recurring shape here, and the reason the digest's "Defended by"
column exists. That column is empty for this class, which is part (d) of section 6.

---

## 2. The main cluster

```
CLUSTER: platform-contract-guessed-not-groundtruthed  (x65 overall; 2 new members:
         IMP-0866 the failure, IMP-0867 the fix record, which `corrects` it)
Altitude:  CLASS — and the class ALREADY has a general gate for this exact sub-property
           (a hand-authored component whose element set differs from what the platform
           requires), reading one reference table. The table simply has no entry for forms.
Ladder row: "a tool could catch it mechanically", governed by §2's altitude rule: the second
           instance of a class may NOT get its own instance gate. One arrived anyway,
           between the finding and this review. So the output is CONSOLIDATION.
Becomes:   (a) constraints/technology/component-shapes.yml — a new shape block for entity
               FormXml carrying the four accepted labels and the evidence that proves them
           (b) scripts/verify-component-shape.py + its .engine twin — the table gains the
               ability to express "this root attribute's value must be one of these"
           (c) skills/how-to-verify-a-platform-contract.md — two paragraph-sized edits
           (d) logs/class-defences.json — record the defence, so this class stops showing an
               empty "Defended by" cell in the digest and stops inviting a 66th new script
Retires:   scripts/verify-formxml-type-values.py and its `formxml-type-values` build step.
           Coverage proof in section 3 — its own known-bad fixture still fails under the
           general gate.
Cites:     IMP-0866, IMP-0867
Residual:  The check settles the WRAPPER label only. The body of a form — which controls
           exist, whether a lookup resolves, whether a maker can save it — is untouched and
           still needs a live import and a human in the designer. And the vocabulary is a
           fixed set; if Microsoft adds a fifth form type this gate rejects it as unknown
           until the table is updated. That is the correct failure direction for a
           fail-closed check, but it is a real cost and it is named here rather than
           discovered later.
```

### What actually happened

Three Quick View Forms were hand-written for the applicant table. Each opens with a wrapper element
declaring what kind of form it is. The author wrote `quickview`, which is the wording the maker
portal uses and the name this repository gave the folder. The platform does not accept it. The
accepted label is `quick`.

This was not an unflagged guess. The author flagged it properly, in the assumptions register, as
[row A-QVF-1](../development/revitalise-grant-automation-dev-summary.md#L9569) — naming the exact
string, saying plainly it was invented by symmetry with a neighbouring folder name, and naming what
would settle it. **What it named was the packaging step**, and that is the whole defect. Packaging
validates layout; it never asks the target whether it accepts the content. The package was built,
the three forms were present in it, and
[the test cycle recorded the row as closed on that basis](../tests/revitalise-grant-automation-test-report-20260924-4.md#L98).
The import then failed in one minute twenty-five seconds.

So the evidence was real, the reasoning was careful, and it answered a different question from the
one being asked. A package containing a component proves the component was *included*. It cannot
prove the target *accepts* it. That sentence is part (c) of section 6, because it is the general
lesson and it is currently written down nowhere.

### The ground truth, established independently this session

Microsoft's reference page for model-driven app forms ("Customize forms in model-driven apps",
Form properties) states the vocabulary explicitly: the wrapper's `type` attribute takes **`main`**,
**`mobile`**, **`quick`** or **`quickCreate`**, and nothing else. `quick` is the Quick View Form.
That matches the twelve forms in this solution that already import cleanly, all of which are
`main`, and it matches the import error, which named `quickview` as unsupported. The fixing
dispatch reached the same four values from the same source independently.

### Why this is a value check and not a text search

Worth stating, because the obvious cheap implementation is wrong and this project has been caught
by it five times. A text search for the string `quickview` scores the **corrected** files worse
than the broken ones: the corrected files retain the withdrawn wording in an explanatory comment,
so they contain the offending string two or three times where the broken ones contained it once. A
search-based check would have gone red on the correction. Reading the attribute's actual value out
of the parsed XML is immune to that. Both the proposed change and the gate being retired get this
right — it is not among the reasons for retiring it.

### 2a. The second cluster — why the duplicate gate got written at all

Logged by this review as it drafted, because the answer is not "someone was careless".

```
CLUSTER: declared-policy-not-mechanically-enforced  (1 new member: IMP-0868)
Altitude:  CLASS, but only PARTLY actioned here — see Residual.
Ladder row: "an agent had the information and still did the wrong thing" would point at an
           agent-file edit. It does not apply: the agent did NOT have the information.
Becomes:   change (d) in section 6 — record the existing defence in logs/class-defences.json,
           which is what fills the digest's "Defended by" cell for this class.
Retires:   nothing
Cites:     IMP-0868
Residual:  The finding also proposes a line in agents/development-agent.md telling a delivery
           agent to read that column before authoring a gate. This review does NOT apply it.
           Change (d) removes the misleading signal, which is the cheaper half and may be
           sufficient on its own; adding an activation step to another agent's file on a
           single instance is exactly the speculative rule the anti-bloat limits forbid.
           If a second duplicate gate appears, that edit is the right answer and the finding
           is already written.
```

The rule that forbids a second instance gate lives in a skill **only this agent loads**. It is
named in no delivery agent's activation set, so no delivery agent can obey it. And the one place an
author would look — the "Defended by" column in the generated failure-modes digest — was **empty
for this class**, which is the largest in the digest, because the August gate's coverage was never
recorded. The digest actively signalled "nothing defends this" to the agent reading it before
authoring. That is a read-path defect, and change (d) is its fix.

---

## 3. Retirement — one candidate, and the proof

**Candidate: `scripts/verify-formxml-type-values.py` and its `formxml-type-values` build step, both
added by the fixing dispatch a few hours ago.** (Both are gone as of the apply; the links this
section carried while it was a draft pointed at a script and a config line that no longer exist.)

The governing reason is the altitude rule: a class with a general gate does not also get an
instance gate. Two checks asserting one rule is the duplication the anti-bloat limits exist to
prevent, and it is how this project ended up with two separate field-length scripts in August.

**The coverage proof.** The rule for retiring an instance gate is that its own known-bad fixtures
must still fail under the general one. Run this session against
`src/tests/fixtures/known-bad/formxml-type-values/`, the extended general gate fails it, naming the
same file and the same wrong value. Nothing is lost.

**Three things are gained**, and they are why this is not merely tidiness:

1. **The instance gate passes when pointed at a directory that does not exist.** Measured:
   `verify-formxml-type-values.py /nonexistent/path` prints "nothing to check" and exits 0. The
   general gate on the same path exits non-zero with *"a gate pointed at a missing target does not
   pass"*. A renamed folder or a typo'd build step silently turns the instance gate green forever.
2. **A form with no type label at all passes it.** That case is printed as a warning and skipped.
   Under the general gate a declared attribute that is absent is an error.
3. **It exists only in `scripts/`, not in the engine copy**, so it is one of the two-file changes
   this repository's split requires and currently has one file.

Its `--selftest` is also not implemented — the flag is swallowed as a path and exits 0 — but it
does have real negative coverage through its Pester fixture, so that one is noted rather than
counted against it.

Derived at draft time, not retyped: **10** retired constraint rows, **86** live ones. This review
proposes **no new constraint**, so the cap of three is untouched.

---

## 4. Findings this review did NOT process

**One**, and it is not mine to take.

[`IMP-0862`](../../logs/improvement-log.jsonl) reports that a coverage check only scans the primary
architecture document and misses the second one. It reads as unprocessed in the queue, but it
already carries an `excluded_by` field naming
[the batch review parked since this morning](2026-09-24-improvement-review.md). That review owns
it. A single critical finding must not pull a re-review of everything sitting around it, so it is
named here and left alone.

Thirty-eight further entries are parked awaiting your keyword on their own documents, and 186 carry
reviewer-accepted deferrals. Neither group is in scope for a critical-finding dispatch.

---

## 5. What you need to decide

**Both answered by the reviewer on 2026-09-24, and both applied as suggested.** The two blocks
below are left as written, because they are what was approved.

- **Decision 1 — deferred, not closed.** Both findings carry a `deferred_reason` and the
  `revisit_when` this section named, verbatim: the next DEV import for this feature completing
  successfully with the three forms present.
- **Decision 2 — remove the duplicate build step now.** Done; see section 8.

---

**Should these two findings be recorded as deferred rather than fixed?**

**Problem** — The failure was only ever visible when a live import ran against the DEV environment,
and nobody in this session holds credentials for it. The source is corrected and the consolidated
build check reproduces the failure on the old files and passes on the new ones, but that is
evidence at the level of the file, not the level of the platform.

**Suggested fix** — Record both as deferred with a return condition naming the observation that
would close them: the next DEV import for this feature completing successfully with the three forms
present. Everything else in section 6 applies as normal.

**What happens if you don't** — Marking them closed would put a claim in the log that nobody
verified, which is the exact habit that produced this finding in the first place. Leaving them
neither closed nor deferred keeps the critical-finding trigger lit and halts the next build.

[logs/improvement-log.jsonl](../../logs/improvement-log.jsonl) · both observable at V3

---

**Remove the duplicate build step now, or leave it until the fixing dispatch is confirmed
finished?**

**Problem** — The check being retired was added within the last few hours by development-agent,
which may still be working. Editing its build config underneath it could collide, and the step is
currently green and harmless.

**Suggested fix** — Remove it as part of this change. It is green today only because the source was
just corrected; leaving it means the repository keeps a check that cannot fail on a missing path,
and a second author later has to work out which of the two is authoritative.

**What happens if you don't** — Nothing breaks immediately. The cost is deferred and quiet: two
checks for one rule, one of them unfailable, and the next person to add a form type has to guess
which reference to update.

[config/revitalise-grant-automation-build.yml](../../config/revitalise-grant-automation-build.yml#L411)

---

## 6. The changes, exactly

Nothing below is on disk.

### (a) `constraints/technology/component-shapes.yml` — a third shape block

Appended after the existing option-set block at
[line 60](../../constraints/technology/component-shapes.yml#L60). Declares the glob
`Entities/*/FormXml/*/*.xml`, root element `forms`, and the four accepted values for the `type`
attribute, with the documentation reference and the failed import recorded as the ground truth that
proves them — per the file's own "only from ground truth" rule.

### (b) `scripts/verify-component-shape.py` and `.engine/scripts/verify-component-shape.py`

The two files are byte-identical today and both are edited in the same change; the build runs the
`scripts/` copy. Inserted before the existing required-children check at
[line 158](../../scripts/verify-component-shape.py#L158): for each attribute the shape names, read
its value off the parsed root element and fail if it is absent or outside the declared set. Around
fifteen lines. The docstring's "what it checks" list gains the matching bullet.

### (c) `skills/how-to-verify-a-platform-contract.md` — two edits

**The ground-truth procedure's copy-the-shape step**
([line 333](../../skills/how-to-verify-a-platform-contract.md#L333)) currently says to copy the
shape exactly — element names, casing, attribute-vs-child, ordering, folder path. It gains the
clause this incident needed: the read covers the **wrapper the artefact sits inside**, not only the
artefact. Here the body of the form was ground-truthed properly from a live export, and the element
enclosing it was invented.

**The artefact-scope table** ([line 775](../../skills/how-to-verify-a-platform-contract.md#L775)),
which lists what each kind of artefact can and cannot evidence, gains a row in the form the other
six rows already take: a **packaged solution `.zip`** evidences that a component was *included* in
the package; it can never evidence that the target *accepts* its content. This is the row that
would have stopped the register being closed on a package listing.

### (d) `logs/class-defences.json` — record the defence

This class is the largest in the digest and shows an empty "Defended by" cell, which is exactly
what invited a duplicate gate today. One entry naming the sub-property
`verify-component-shape.py` actually covers — and, equally important, what it does **not** cover —
fixes that. Validated with `verify-class-defences.py`, the gate that checks it, not merely with the
generator that renders it.

### (e) The retirement

`scripts/verify-formxml-type-values.py` deleted, its build step removed, and — per the retirement
rule — every remaining reference swept and rewritten, not just the call site. Nine references exist
outside the script itself: three in the build config, five in the Dev Summary, one in the build
config history. The Dev Summary and history entries are **records of what happened** and stay as
they are; the build config entries go. The known-bad fixture is kept and re-pointed at the general
gate, because it is the coverage proof.

### (f) Two stale counts, corrected at apply time

Not proposals, and nothing to decide — two sentences elsewhere quote numbers that have drifted from
what they count, and the check that watches them is already red on both before this review touches
anything. One is a count of verification scripts quoted in
[improvement-agent's own file](../../agents/improvement-agent.md#L551); the other is a line count of
the digest, quoted inside the generator that produces it — which drifts every time a review
regenerates the digest, as this one is required to. Both are corrected in the same change, and both
figures are re-derived after the retirement changes the script count again.

---

## 7. Verification

Run at draft time, against a patched copy in a scratchpad; nothing was applied.

| What | Result |
|---|---|
| Proposed check against the corrected tree (56 files, 3 shapes) | **0 findings**, exit 0. Zero is correct here: the source fix landed while this was being measured. |
| Proposed check against the pre-fix corpus, rebuilt from `git archive HEAD` (54 files) | **3 findings, 3 true positives, 0 false.** Exactly the three forms that failed the live import; the twelve `main` forms passed untouched. |
| Proposed check against the retiring gate's own known-bad fixture | **Fails it**, naming the same file and value. This is the retirement coverage proof. |
| Retiring gate pointed at a non-existent directory | **Exits 0.** The general gate on the same path exits non-zero. |
| Accepted vocabulary | Confirmed against Microsoft Learn this session, corroborated by the twelve forms in this solution that import cleanly, and independently reached by the fixing dispatch. |
| Review document consistency, document line links | Both green. |
| Disposition simulation on a scratch copy of the log | The critical-finding trigger clears under the deferral in section 5. Real file restored and confirmed byte-identical. |

**Not verified, and by whom it can be.** No live import ran here, and none can from this session.
That is the V3 observation the deferral in section 5 exists to record; pipeline-agent is the one who
will make it. The consolidated gate has also not yet run inside a real build — it has been measured
standalone against four corpora, which is V1 evidence about the gate, not V2 evidence about the
build.

---

## 8. Apply-time record

Applied 2026-09-24 on `APPROVE IMPROVEMENTS`. Everything in section 6 landed. One deviation, stated
first because it is the only thing in here that differs from what was approved.

### The deviation — the reference sweep was larger than section 6(e) enumerated

**What section 6(e) said:** nine references outside the script itself — three in the build config,
five in the Dev Summary, one in the build config history.

**What the sweep actually found** (`git grep -n 'formxml-type-values'`, re-run at apply time):
three in the build config, **ten** in the Dev Summary, one in the build config history, and **eight
lines in [`src/tests/build/BuildGates.Tests.ps1`](../../src/tests/build/BuildGates.Tests.ps1#L218)
— a whole `Describe` block with three assertions, which section 6(e) did not name at all.**

Left alone, the retirement would have deleted a script that a green Pester suite still invokes
three times. The approved instruction is *"every remaining reference swept and rewritten, not just
the call site"*, so the test block is inside what was approved; only the draft's count of where
those references were was wrong. The negative coverage was **moved, not dropped**: the three
assertions became two inside the existing
[`component-shape` Describe block](../../src/tests/build/BuildGates.Tests.ps1#L845), and the
known-bad fixture moved into that block's own fixture tree at
`src/tests/fixtures/known-bad/component-shape/Entities/rev_fixture/FormXml/quickview/`. The third
assertion — "passes against the real solution source" — was dropped as a literal duplicate of an
assertion already in that block.

The two surviving assertions are the ones that would have been wrong to lose: the fixture still
fails, naming the same file and the same value, and a copy with only the attribute corrected stops
being failed while its comment still quotes the withdrawn value. Dev Summary and build-config-history
entries stay as written — they are dated records of what happened, per section 6(e).

### What landed

| Change | Where | Evidence |
|---|---|---|
| (a) `entity form` shape block — glob, root, the four accepted `type` values, ground truth | [component-shapes.yml](../../constraints/technology/component-shapes.yml#L76) | gate green over 56 files, 3 shapes |
| (b) the table gains `attribute_values` | [verify-component-shape.py](../../scripts/verify-component-shape.py#L162) and its `.engine` twin, byte-identical | 3 findings / 3 true positives on the pre-fix corpus |
| (c) the wrapper clause and the packaged-`.zip` row | [how-to-verify-a-platform-contract.md](../../skills/how-to-verify-a-platform-contract.md#L336) and its [artefact-scope table](../../skills/how-to-verify-a-platform-contract.md#L807) | — |
| (d) the defence recorded | [class-defences.json](../../logs/class-defences.json#L46) | `verify-class-defences.py`: OK, 5 defences, 31 references resolved |
| (e) the retirement | script deleted, build step replaced by a do-not-re-add note, fixture moved, test block absorbed | `verify-build-config.py`: PASS, 84 steps, 65 gates |
| (f) both stale counts | [improvement-agent.md](../../agents/improvement-agent.md#L551) (self-corrected by the retirement: 65 → 64) and the generator's own `CURRENT SIZE` line, in both copies | `verify-derived-counts.py`: OK, 10 of 10 |

### The log

| Finding | Disposition |
|---|---|
| The live import failure | **DEFERRED**, not closed — `deferred_reason` + the approved `revisit_when`, verbatim |
| The source fix | **DEFERRED**, same return condition. Its `deferred_reason` also records that the gate it added was retired here and where its fixture went |
| The duplicate-gate finding | **APPLIED**, partially — change (d) only. The proposed activation line in another agent's file is **withheld** and the reason is in `applied_by` |

`verify-improvement-log.py --check` went from FAILED to **OK** — the critical-finding trigger this
review exists to clear is clear. Digest regenerated; this class's
"Defended by" cell is now populated, which was the point of change (d).

One finding was logged by the apply step itself, for the deviation above: a retirement proposal's
reference sweep must be the output of `git grep -l <bare filename>` over the whole tree, because the
referrer that matters most — the gate's own Pester block — invokes the script by bare filename and
breaks rather than rots when it is missed.

### Verified at apply time, not merely at draft time

Gate against the corrected tree (56 files, 0 findings, exit 0); against the pre-fix corpus rebuilt
from `git archive HEAD` (54 files, 3 findings, 3 true positives, 0 false); against the retiring
gate's own fixture (fails, naming the same file and value); the full build-gate suite, **120 of 120
passing**; `verify-build-config.py`, `verify-class-defences.py`, `verify-derived-counts.py` and
`verify-improvement-log.py` all green.

**Still not verified, and by whom.** No live import ran; none can from this session. That is exactly
what the deferral records, and pipeline-agent is who closes it. The consolidated gate has been
measured standalone against four corpora and through the Pester suite — it has not yet run inside a
real `pac` build.
