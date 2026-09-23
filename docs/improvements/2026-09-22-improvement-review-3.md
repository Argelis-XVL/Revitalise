# Improvement Review — 2026-09-22 (3)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 2 `NEW` → 1 cluster
**Trigger:** blocker escalation — one unread `blocker`-severity entry (IMP-0820)
**Gate:** `APPROVE IMPROVEMENTS`

**Scope.** This review processes the unread blocker and the corrective finding this review logged
against it. The ten other unread entries stay out of scope — one unread blocker must not pull a
review of everything around it. Eight of them were already declared out of scope by
[review 1 of today](2026-09-22-improvement-review.md) and carry its `excluded_by` stamp; the two
newest (IMP-0818, IMP-0819, both `friction`) are stamped by this review. §5 names them.

---

## 0. What the reviewer needs to know first

**The flow was never broken by the import. It was broken by the designer, and the cause is a
documented platform rule nobody here knew.**

A Power Automate "Initialize variable" action can declare exactly **one** variable. The file format
stores them in an array and will happily hold seven — the packer, the solution import, the publish
and the activation all accept it — but the designer reads only the first one and silently ignores
the rest. Our round-statistics flow declared all seven trailing-window variables in a single
action. So when you opened it in the designer, six of the seven did not exist as far as the
designer was concerned, every formula that used them was broken, and it would not let you save
until you declared those six yourself. Which is exactly what you had to do.

Microsoft states it in one sentence, on their own documentation page for this action:

> *"Although the Initialize variable action has a `variable` section structured as an array, the
> action can create only one variable at a time. Each new variable requires an individual
> Initialize variable action."*

**Two things follow, and the second one is time-sensitive.**

The finding's original diagnosis — that the import failed to carry the flow's content into the
development environment — is **wrong**, and I disproved it with live measurements rather than
argument (§2). The fix it proposed, a routine comparison of the live environment against source
after every deployment, is **withheld**: that exact comparison had already been run, and it came
back clean.

And your six hand-added actions live only in the development environment. **The next deployment
will delete them and put the broken flow back**, because source has not been fixed yet. §4 says
what to do about that.

---

## 1. Regression check — did the last review's changes work?

Audited: [review 2 of today](2026-09-22-improvement-review-2.md), applied roughly three hours
before this one.

| Prior change | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|
| Check 9 added to the flow-shape gate — a "set variable" action may not read the variable it is setting | designer-only validation, self-reference | NO new instance of that exact shape | Working — and it is the direct precedent for this review's change |
| IMP-0816 deferred with a reviewer-approved reason, clearing the build queue | queue blocked by the finding it remediates | NO | Working — the build ran and packaged at 14:16 |

**A class recurred, and it is the one that matters.** Check 9 fixed *one* shape the designer
rejects while everything below it passes. This review is the **third** instance of that same
underlying property, roughly a day apart:

| | Nested declaration | Self-reference | Multi-variable declaration |
|---|---|---|---|
| Recorded as | IMP-0137 | IMP-0816 | this review |
| Defended by | check 4 | check 9 | **nothing, until now** |
| Symptom | designer refuses to save | designer refuses to save | designer refuses to save |

Each was fixed as its own shape. That is the pattern the altitude rule exists to interrupt — but
the correct response here is still to extend the same gate rather than to build a new one, because
**a general gate for this property already exists and is already wired**. What was missing was one
assertion inside it. I say so explicitly so this is not read as a fourth instance patch.

---

## 2. Why the original diagnosis is wrong — three measurements, not an argument

The finding asserted the import did not carry the flow's content into the development environment,
and offered two candidate mechanisms. All three claims fail against live evidence.

**The package was correct.** The zip that was imported carries the flow file byte-for-byte
identical to source, all seven variables present. Checksum `1e152868…8b476`, matching source
exactly.

**The environment was correct after the import, and before you opened the designer.** A live export
pulled at 13:28 — after the 12:24–12:32 import, before your designer session — held all seven
variables in the single action, across 16 top-level actions, with no hand-added actions present.
The comparison against source that this pull was made for reduces to one trivial difference: a
`templateName: null` key that source carries and the platform does not store.

**The environment changed only when the designer wrote to it.** I pulled a fresh live export during
this review. It now has 22 top-level actions: the original action **truncated to `Trailing1`
alone**, plus your six new ones. The designer is the writer that dropped the other six, and the
first-one-survives pattern is the documented behaviour, not a merge artefact.

So the proposed fix — compare the live environment against source after every deployment — is
**withheld**. It would have cost a live export per deployment and reported this flow as clean,
because at the moment it ran, it *was* clean. Worse, run today it would now report drift against
your repair and ask someone to undo it.

---

## 3. The change

**One assertion added to the existing flow-shape gate**
([check 4, `.engine/scripts/verify-flow-definition-language.py#L173`](../../.engine/scripts/verify-flow-definition-language.py#L173)).

Check 4 already walks every "initialize variable" action in every flow and already reads the array
of variables inside it — to collect the declared names and to assert the action sits at the top
level. It simply never looked at how many were in the array. The addition asserts exactly one, names
the offending action and every variable after the first, and states the legal shape in the failure
message so an author who has just been stopped is told what to write instead.

```
CLUSTER: platform-contract-guessed-not-groundtruthed  (IMP-0820, IMP-0821)
Altitude:  CLASS — third instance of "the designer's save validation is stricter than the file
           format, and everything below the designer passes"
Ladder row: "a tool could catch it mechanically" — and the tool already exists and is wired
Becomes:   one assertion inside check 4 of verify-flow-definition-language.py
Retires:   nothing — see §6
Cites:     IMP-0820, IMP-0821 (and IMP-0137, IMP-0816 as the prior instances of the property)
Residual:  The gate reads SOURCE. It cannot see a flow edited directly in the designer, and it
           cannot see the reverse of this defect — an environment whose flow has drifted from
           source, which is the state the development environment is in right now (§4). No gate
           proposed for that: the one measurement we have of that instrument returned clean on a
           genuinely defective flow.
```

**Corpus measurement, taken before proposing this** — 8 flow definitions, 11 "initialize variable"
actions, **1 finding, which is the true positive, 0 false positives**. The single finding is the
round-statistics action this incident is about. Zero findings elsewhere is the correct answer
rather than a clean run: this is the only multi-variable declaration in the solution.

**No new constraint** (cap is 3; this review proposes 0). **No new script**, so the
[count of verification scripts](../../scripts/derived-counts-registry.json) is unchanged at 64.
**No new wiring** — the gate is already build step
[`flow-definition-language`](../../config/revitalise-grant-automation-build.yml#L615).

---

## 4. What is still open

**Source still has the defect, and the next deployment reinstates it.** The seven-in-one action is
unchanged in
[the flow definition](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json#L89).
Splitting it into seven actions is delivery work and belongs to development-agent, not to this
agent. Once the gate below lands, the build will stop on it, which is the intended behaviour.

**Your six hand-added actions are unprotected.** Deployments here use force-overwrite, which
replaces the flow wholesale. Until source is fixed and redeployed, any import undoes your repair.

**Neither finding can be closed by this review, and I am not going to claim otherwise.** Both are
only observable when a human opens the designer and saves. Proving the fix needs a corrected source
tree, a fresh build, an import, and you saving the flow with nothing to hand-add. Nobody in this
session can make that observation, so both entries stay open with a recorded reason and a return
condition naming exactly that.

---

## 5. Entries excluded from this review

Ten unread entries are out of scope. None is a blocker, so none is holding anything up.

| Entries | Severity | Why excluded |
|---|---|---|
| IMP-0798 … IMP-0803, IMP-0811, IMP-0812 | friction / rework | Already declared out of scope by [review 1 of today](2026-09-22-improvement-review.md); carry its `excluded_by` stamp |
| IMP-0818, IMP-0819 | friction | Logged after that review; stamped `excluded_by` this review |

---

## 6. Retirement

**Checked; no candidate.** This review adds no constraint and no script, and it retires nothing.
The change is one assertion inside a gate that already exists, is already wired, and already covers
two neighbouring shapes of the same property — so there is no instance-level gate standing in for
what is being generalised. Recording the check as a deliberate negative, not as an omission.

---

## 7. Applied record

**Applied 2026-09-23** on `APPROVE IMPROVEMENTS`, as part of a batch applying six parked reviews.

| # | Change | Landed in | Entries |
|---|---|---|---|
| 1 | Check 4 gains the one-variable-per-`InitializeVariable` assertion, naming the action, the count, and every variable after the first | `.engine/scripts/verify-flow-definition-language.py` | IMP-0820, IMP-0821 — both **deferred**, not closed |

**Corpus re-measured at apply time, not carried forward from the draft:** 9 flow definitions (the
draft measured 8; one was added since), **1 finding, 1 true positive, 0 false positives** — the
`Initialise_trailing_variables` action in `REVPortalRoundStatistics`, declaring 7 variables. The
gate now names `Trailing2`…`TrailingFilledCount` as the six the designer will silently drop.

The instance `scripts/verify-flow-definition-language.py` is a **wrapper**, not an unsplit
duplicate, so check 4 exists in one place only and no twin edit was required.

### One consequential repair the approved change forced, recorded rather than made silently

Applying the assertion turned the real corpus red — which is §4's stated intent — and that
**falsified a sibling assertion in the wrapper's own selftest**. That assertion was labelled *"the
two declared exceptions suppress the FAILURE today"* but tested `rc == 0`, which asserts the entire
corpus is green across all nine checks. An unrelated true positive must not be able to falsify
check 7's selftest, and fixing source is delivery work this review explicitly does not own (§4).

Both assertions were narrowed to read **check 7's own findings** rather than the process exit code,
which is what their labels always claimed. The deviation is recorded here, in each entry's
`deferred_reason` chain, and in the gate output.

**A false PASS was caught in the middle of that repair and is worth recording**: the first version
redirected `stdout`, while the engine prints `ERROR:` lines to `stderr`. The buffer came back empty,
the count was 0, and today's check reported PASS while asserting nothing at all. It was visible only
because the *expired* assertion — the one expected to be non-zero — failed at the same time. This is
`IMP-0542`'s shape (a count expected to be zero, arriving as an absence) in a new instrument.

---

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-22-improvement-review-3.md

Findings processed: 2 NEW  →  1 cluster
Regression check:   2 prior changes audited, 1 class recurred (third instance, same property)
Proposed:           0 constraints (cap 3), 1 gate extension, 0 skill/knowledge edits,
                    0 agent-file edits, 0 retirements
Altitude calls:     1 generalised from instance to class, 0 left as notes
Digest:             will regenerate — 809 lessons, 2 findings disposed

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```
