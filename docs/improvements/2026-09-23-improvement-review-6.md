# Improvement Review — 2026-09-23 (6)

**Status:** APPLIED — `APPROVE IMPROVEMENTS` received from Anna Southern on 2026-09-23. All three
changes in section 8 are on disk. See section 10 for the apply-time record, including **one
correction to section 4 of this document**, whose premise measured false at apply time.

**Trigger:** one unread critical finding, routed immediately rather than batched. A second
critical finding and one fix record arrived while the draft was open and are folded in — five
findings, three clusters.

---

## Summary

One new provisioning script needed four things to be delivered alongside it. Three of them were
missed, and each one was discovered by a different build check on a different build attempt, so
one script cost three halted builds in a single day. Every check involved worked correctly — they
are simply spread across the build, at steps 6, 25 and 79, so each retry fixed the one thing that
had just been named and then ran into the next one.

The remedy is not another check. It is that the agent authoring the script is told to run the
three checks that already exist **before** it hands the work on, in the file that agent reads on
activation. Two of the four companion items turn out to be undocumented anywhere an author would
look, one is documented and was ignored, and the fourth is not a real requirement at all.

A second critical finding arrived while this was being written, on unrelated work. It needs no
rule change — the checks caught it correctly — but it needs a decision from you so that it stops
blocking builds once the real fix lands. Both decisions are in section 9.

---

## 1. Regression check — did the last review's changes work?

The previous review ([review 5](docs/improvements/2026-09-23-improvement-review-5.md)) proposed
**no rule changes**. It closed two entries on a delivery fix and deliberately left one open. So
there is no prior rule change from it to audit for recurrence.

The change that *is* being audited here is older, and it is the one that matters for this review:

| Question | Answer |
|---|---|
| Has any finding in this class appeared since the change? | **Yes.** The audit-declaration class has now recurred for a third time. |
| Was the change prose, or a mechanical gate? | **A gate** — [`verify-audited-tables.py`](scripts/verify-audited-tables.py#L69), added because the same thing had already happened twice. |
| Did the gate run? | **Yes, and it caught the problem correctly**, before anything reached a live environment. |
| Did the closure evidence match the level the defect was visible at? | Yes — every entry here is visible from source alone, and was closed on source evidence. |

**This is the finding that shapes the whole review.** A recurrence after a gate normally means the
gate is mis-scoped or unwired. Here it is neither. The gate is correct, it fired, and it stopped
the problem. What recurred is not the defect reaching production — it is the *author not knowing
the obligation existed*, and paying for that discovery with a build cycle. That is a different
problem with a different remedy, and proposing a better gate would have been the wrong answer.

---

## 2. Cluster 1 — one new script, three companions, three separate builds

**Three findings, one incident.** A new database-seeding script was added to the provisioning
directory. Alongside it, four other things needed to change. Here is what each one actually cost:

| The companion item | Which check catches it | Where in the build | Cost |
|---|---|---|---|
| A behavioural test naming the script | [`verify-provisioning-test-presence.py`](scripts/verify-provisioning-test-presence.py) | [step 6](config/revitalise-grant-automation-build.yml#L92) | 1 halted build |
| An audit declaration in all three environment settings files | [`verify-audited-tables.py`](scripts/verify-audited-tables.py#L69) | [step 25](config/revitalise-grant-automation-build.yml#L222) | 1 halted build |
| A row in the provisioning directory's script inventory | [`ScriptContract.Tests.ps1`](src/tests/provisioning/ScriptContract.Tests.ps1#L362) | [step 79](config/revitalise-grant-automation-build.yml#L878) | 1 halted build |

Three checks, seventy-three build steps apart. Each retry fixed the one item the previous check
named, then hit the next check naming a different one.

### What I measured before proposing anything

The critical finding proposes a four-item checklist. I checked each item against the file the
authoring agent actually loads on activation,
[`coding-standards.md`](knowledge/technology/coding-standards.md#L197), and against the whole
provisioning directory. The result changed the design:

| Proposed checklist item | Measured state | What follows |
|---|---|---|
| Behavioural test | **Already written down, explicitly, as an authoring obligation** — [coding-standards.md](knowledge/technology/coding-standards.md#L235) says a new create-only script needs its own mocked behavioural test | Restating it a fourth time will not help. It needs to become a command, not a sentence. |
| Audit declaration | **Documented nowhere.** The word `auditedTables` appears in **zero** files under `agents/`, `skills/`, `knowledge/` and `constraints/` | A genuine gap. This is cluster 2's change. |
| Inventory row | **Mentioned once**, at [coding-standards.md](knowledge/technology/coding-standards.md#L223), but only as one of the things a convention suite asserts — never as something an author must do | A genuine gap, in the sense that matters: it is not written where an author would read it as a task. |
| A verification counterpart script | **Not a requirement.** 9 of the 29 scripts in this directory have one. The directory README describes verification counterparts as [a category of script](provisioning/README.md#L104), not as an obligation, and no check enforces it | **Withheld.** See below. |

**The fourth item is withheld, and this is what withholding it prevents.** Applying it as written
would have told every future author that twenty currently-correct scripts are incomplete — among
them the settings seeder, the test-data seeder and remover, the app-sharing script and the role
binder. Each of those would have become a false finding on day one.

### The root-cause sentence, which is in the file an author reads

The provisioning directory's own README says this, [at line 120](provisioning/README.md#L120):

> *"A new script in this directory is covered by the contract tests the moment it is added — if it
> breaches the contract, the suite fails without anyone having to remember to write a test for
> it."*

That sentence is true of the convention tests and false of the behavioural-test check, which is
precisely the check that halted the first build. An author who reads it has been told, in the
directory's own documentation, that the thing they just skipped is handled automatically.

### A late arrival that corroborates the withholding

While this draft was being written, the delivery agent logged the fix for the inventory row. Its
own record of the new row fills the *verify counterpart* column with **"none exists yet"** — the
author of the script, writing the inventory row by hand against the shape of its sibling rows,
recorded that this script has no verification counterpart and shipped it anyway. That is
independent confirmation, from the other direction, that the fourth checklist item is not a
requirement of this directory.

```
CLUSTER: new-provisioning-script-companion-artifact-missed-serially  (x2: the critical finding
           and the delivery record that corrects it)
Altitude:  CLASS — but note that the second member RECORDS A FIX rather than being a second
           defect, so this is one incident, not two. Not a constraint-level promotion.
           Promoted on severity (critical) plus a measured three-build cost in one day.
Ladder row: "An agent had the information and still did the wrong thing" → agent-file edit
Becomes:   a companion-checks block in agents/development-agent.md, giving the three COMMANDS,
           placed directly after the existing "grep for the siblings" section it mirrors;
           plus a correction to the misleading README sentence above
Retires:   nothing — no rule governed provisioning companion artefacts
Cites:     the three findings in this cluster and the two that preceded them today
Residual:  Nothing asserts that the author ran the commands. A dispatch instruction is a prompt,
           never a file, so no check can read one — the same structural limit the neighbouring
           section in that agent file already states about itself. This is a checklist, not a gate.
```

### Why not `how-to-apply-constraints.md`, the file the finding names

That skill is the procedure for **evaluating constraints** and producing a constraint-check block
— [five numbered steps](skills/how-to-apply-constraints.md#L14), none of which is about authoring
anything. An authoring checklist placed there would sit in a document loaded at a different moment
for a different purpose. The finding named a plausible file; the measurement says it is the wrong
one.

---

## 3. Cluster 2 — a new table's audit declaration, for the third time

**Two findings, and the class now stands at sixteen members.** When a new database table is added
to solution source, it must also be named in the audit list in all three environment settings
files. Nothing in the source sets this; it is environment metadata that a solution import neither
writes nor clears.

The gate for this was built after the second occurrence and it works. What is missing is anything
that tells an author about the obligation at the moment they create the table. I confirmed that
absence rather than assuming it: the setting's name appears in **no** agent file, skill, knowledge
file or constraint file in this repository.

The skill that governs creating a table —
[how-to-model-a-data-schema.md](skills/how-to-model-a-data-schema.md#L16) — has an entity design
checklist with eight items and lists *"plan for audit from the start"* among its
[principles](skills/how-to-model-a-data-schema.md#L11), with no step that does it. That is the
landing spot.

```
CLUSTER: platform-state-divergence  (x2 unread here: the two audit-declaration findings)
Altitude:  CLASS — 16 members, third occurrence of this exact sub-shape
Ladder row: "An agent had the information and still did the wrong thing" → skill edit
Becomes:   one step added to the entity design checklist in skills/how-to-model-a-data-schema.md
Retires:   nothing
Cites:     the two findings in this cluster and the earlier one that produced the gate
Residual:  The checklist step covers table CREATION. A table that is renamed, or a fourth
           environment settings file added later, is covered by the build gate and not by this
           step. That is the correct division: the gate is the backstop, this is the leading edge.
```

---

## 3a. A second critical finding arrived mid-draft, and it is not a rule problem

Twenty minutes into this draft a **new critical finding** was logged against a different piece of
work. The solution manifest declares ten cloud flows and only nine exist on disk: the missing one
is a watch flow for the local-authority register, which belongs to a different contracted task
from the one that was being built. Two source checks go red on it, and the build cannot start.

I re-measured this rather than accepting the report — ten declarations, nine definitions, the
named identifier present in the manifest, no matching file in the flow directory, and both checks
confirmed red by running them.

**There is no rule change here.** The checks fired correctly and caught a genuine inconsistency
before packaging. The fix is delivery work — either author the missing flow or withdraw its
declaration — and it belongs to whoever owns that task, not to this review.

**But it cannot simply be left alone either.** An open critical finding blocks the next build
regardless of whether the underlying defect is fixed, so leaving it untouched means the build
stays blocked on a bookkeeping entry after the real fix lands. The honest disposition is a
recorded deferral with a named owner and a return condition — which is a decision for you to
make, not for me to assume, and it is in section 9.

---

## 4. Both edit targets exist twice, and only one copy is read

`agents/development-agent.md` and `skills/how-to-model-a-data-schema.md` are **not** symlinks into
the engine submodule on this branch — they are ordinary files, each byte-identical to a second
copy inside `.engine/`, with nothing keeping the two in step. The split check reports 62 such
unsplit duplicates.

So each of the two edits below is **two file writes, not one**. Editing only the engine copy
leaves the copy that agents actually load unchanged; editing only the instance copy means the next
engine sync silently reverts it. This is recorded here because the paths give no hint of it.

---

## 5. Retirement candidate

Checked, and there is nothing to retire. No constraint row governs provisioning companion
artefacts or audit declarations, so none of the three findings supersedes one. Current counts,
derived rather than typed: **10 retired** rows and **86 live** rows across the constraint files.

The nearest thing to a retirement in this review is the correction in change 3 — a sentence that
tells authors an obligation is handled automatically when it is not. That is a withdrawal of a
misleading instruction, not of a rule.

---

## 6. What this review did NOT process

Twenty-four other unread findings are in the queue and are **not** processed here. A single
critical finding summons a review of itself, not of everything around it — batching it would delay
the thing that halted three builds today behind two dozen unrelated items.

Not processed: IMP-0798, IMP-0799, IMP-0800, IMP-0801, IMP-0802, IMP-0803, IMP-0811, IMP-0812,
IMP-0818, IMP-0819, IMP-0822, IMP-0823, IMP-0825, IMP-0826, IMP-0827, IMP-0828, IMP-0829,
IMP-0832, IMP-0833, IMP-0836, IMP-0837, IMP-0839, IMP-0841, IMP-0842.

Each will be stamped as excluded by this review, so the queue shows them as consciously skipped
rather than unopened.

Also untouched: 185 findings a human has already deferred with a recorded reason, and one from
[review 5](docs/improvements/2026-09-23-improvement-review-5.md) that was deliberately left open
because the evidence that would close it is a file that has not been committed.

---

## 7. Routed work — re-measured at gate time

**Nothing to route.** The two delivery fixes this incident called for have both already landed,
and I re-measured both rather than taking them from the dispatch brief:

- The audit declarations are present — the gate now reports 15 declared tables audited across all
  three settings files.
- The inventory row is present in the provisioning README.

The one item that remains open from earlier today is the uncommitted test file carried by review
5, which is that review's to track, not this one's.

---

## 8. The changes awaiting the keyword

| # | Change | File | Cites |
|---|---|---|---|
| 1 | A companion-checks block giving the three commands to run before reporting a new provisioning script done | `agents/development-agent.md` **and** `.engine/agents/development-agent.md` | the critical finding + the two that preceded it today |
| 2 | One step added to the entity design checklist: declare a new table for auditing in all three environment settings files | `skills/how-to-model-a-data-schema.md` **and** `.engine/skills/how-to-model-a-data-schema.md` | the two audit findings + the earlier one |
| 3 | Correct the README sentence that says a new script is covered without anyone remembering to write a test | `provisioning/README.md` | the critical finding |

**Withheld:** the "verification counterpart" checklist item, on the measurement in section 2.
**Not proposed:** any new constraint (0 of a cap of 3), any new gate, any retirement.

### Dispositions

All five findings are visible from source alone, so a source-level needle is sufficient evidence
and no re-run of a live reproduction is required for any of them.

| Finding | Disposition | Basis |
|---|---|---|
| IMP-0848 | **CLOSE** | source-visible; closed on change 2 |
| IMP-0849 | **CLOSE** | source-visible; closed on change 2 |
| IMP-0850 | **CLOSE** | source-visible; closed on change 1 |
| IMP-0851 | **CLOSE** | source-visible; records the inventory-row fix, which I re-measured as present |
| IMP-0852 | **DEFER** | the evidence that would close it does not exist yet, and creating it is delivery work on another task |

---

## 9. What you need to decide

**Approve the three changes in section 8.**

**Problem** — One new script needed four companion items, three were missed, and each was found by
a different check on a different build attempt, costing three halted builds in one day.
**Suggested fix** — Tell the authoring agent to run the three checks that already exist before it
hands the work on, add the one genuinely undocumented step to the table-creation checklist, and
correct the sentence that tells authors this is all automatic.
**What happens if you don't** — The next new provisioning script repeats the same three-retry
cycle, because nothing an author reads lists what a new script needs.
[section 8](docs/improvements/2026-09-23-improvement-review-6.md)

---

**Accept a recorded deferral on the second critical finding, so the build is not blocked by
bookkeeping.**

**Problem** — A critical finding logged mid-draft names a missing cloud-flow definition on a
different contracted task; it needs no rule change, but while it sits open the next build is
blocked on the finding itself rather than on the defect.
**Suggested fix** — Record it as deferred, owned by whoever holds that task, returning as soon as
the flow is authored or its declaration withdrawn.
**What happens if you don't** — The build stays red on the queue entry even after the real fix
lands, and someone pays another review dispatch to close it.
[section 3a](docs/improvements/2026-09-23-improvement-review-6.md)

---

## 10. Apply-time record

Approved by Anna Southern, 2026-09-23. Re-verified before applying, then applied.

### What landed

| # | Change | Where | State |
|---|---|---|---|
| 1 | Companion-checks block giving the three commands to run before reporting a new provisioning script done | [`agents/development-agent.md`](agents/development-agent.md#L395) | applied |
| 2 | An `auditedTables` step added to the Entity Design Checklist | [`skills/how-to-model-a-data-schema.md`](skills/how-to-model-a-data-schema.md#L28) | applied |
| 3 | Correction to the README sentence that told authors a new script needs no companion work | [`provisioning/README.md`](provisioning/README.md#L120) | applied |

All three commands named in change 1 were executed before being written down, and all three
`evidence_grep` needles were grepped before being stored (each returns exactly 1, on one line).

### Correction: section 4 of this document is wrong

Section 4 states that the two edit targets are **not** symlinks, that each is byte-identical to a
second copy in `.engine/`, and that each edit is therefore "two file writes, not one". **All three
claims are false.** Measured at apply time:

- `agents` and `skills` are **directory symlinks** into `.engine` (`ls -ld`).
- Both paths resolve to **one inode** each — 148368851 and 148369606. `cp` refused the second
  write with *"are identical (not copied)"*.
- [`verify-engine-instance-split.py`](scripts/verify-engine-instance-split.py) does report 62
  unsplit duplicates, but they are **scripts**, and it names neither of these two files.

The draft's instruments could not have found this: `ls -l` and `diff` both *follow* symlinks, so
"one file, two paths" and "two synchronised copies" produce identical output. The correct
instrument is `stat -f %i` on the files, or `ls -ld` on the directory component.

**This changed nothing about what was applied** — each edit was made once and both paths carry it,
because they are the same file. The intent survived; only the stated mechanism was wrong. Logged as
[`IMP-0854`](logs/improvement-log.jsonl).

### IMP-0852 — the deferral, re-measured rather than assumed

The dispatch flagged that a background `development-agent` build of the missing flow (wbs:4.6) might
have closed this finding before the keyword arrived. **It had not.** Re-measured at apply time:

- 10 `RootComponent type="29"` entries declared in `Solution.xml`, **9** flow definitions on disk.
- No untracked file under `Workflows/` (`git status --short` on that directory is empty).
- [`run-source-gates.py`](scripts/run-source-gates.py) re-run: `source-validate` and
  `root-components-resolve` **both still red**.

So the deferral was applied as drafted, and it remains the honest disposition. It is not a claim
that the defect is fixed — it records a reviewer decision so the queue entry stops blocking builds
while the real fix is scheduled against wbs:4.6.

### Dispositions as applied

| Finding | State | Basis |
|---|---|---|
| IMP-0848 | `APPLIED` | closed on change 2 |
| IMP-0849 | `APPLIED` | closed on change 2 |
| IMP-0850 | `APPLIED` | closed on change 1, **narrowed** — see below |
| IMP-0851 | `APPLIED` | closed on change 1; inventory row re-measured as present |
| IMP-0852 | `reviewer-deferred` | `deferred_reason` + `revisit_when`, re-measured above |

### Narrowing recorded against IMP-0850

Applied in the narrowest form preserving the intent, on the measurement in section 2:

- **Four items → three.** The *verification counterpart* item was withheld. It would have made
  false findings against 20 of the 29 scripts in the directory on day one — among them the settings
  seeder, the test-data seeder and remover, the app-sharing script and the role binder. The applied
  block now states explicitly that it is *not* a fourth companion, so the symmetry is not re-derived
  by the next reader.
- **Target file changed** from the proposed `skills/how-to-apply-constraints.md` — the
  constraint-*evaluation* procedure, loaded at a different moment — to the agent file the author
  loads on activation.

### Queue bookkeeping

The 24 unprocessed findings named in section 6, plus `IMP-0853` which arrived after that list was
written, carry `excluded_by` naming this review — consciously skipped, not unopened. `IMP-0853` is
*cited* by change 1 (it is the measurement behind the withheld fourth item) but was not processed
here.

One warning is left standing and belongs to
[review 5](docs/improvements/2026-09-23-improvement-review-5.md), not to this one: `IMP-0800` is
corrected by `IMP-0801` and no review has yet processed it.

### Closing checks

`verify-improvement-log.py --check` exits **0** — both blocker triggers cleared. The disposition was
simulated on a scratch copy and the real file confirmed byte-identical before the real write.
