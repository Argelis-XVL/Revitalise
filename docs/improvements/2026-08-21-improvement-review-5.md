# Improvement Review — 2026-08-21 (fifth review this date)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 9 `NEW` → 3 clusters (4 findings processed, 4 deferred with reasons, 1 appended)
**Trigger:** blocker escalation, re-dispatched. `python3 scripts/verify-improvement-log.py --check` was
still failing on the same two blockers a stalled earlier dispatch was sent to clear.
**Gate:** `APPROVE IMPROVEMENTS`
**WBS:** `system`. The findings block delivery tasks 2.6 and 6.7 (the TST/ACC walkthrough) and
guard 0.5 / 6.1 / 6.5 / 8.2 (roles and column security). No contracted task is claimed here.

**Status:** AWAITING `APPROVE IMPROVEMENTS`. Nothing in section 3 has been applied.
Two things *were* done, because the re-dispatch asked for them and neither edits a rule: the
finding log now records the state each entry is in, and the digest is regenerated.

---

## 1. Regression check — did the last review's changes work?

**The last review was never approved, so none of its changes exist.** That is the whole result, and
it is the reason this dispatch happened at all.

[Review 4](2026-08-21-improvement-review-4.md) reached its gate at 15:25 and stopped there, exactly
as it was designed to. Five hours later the finding log gate was still red on the same two entries.
I checked each of its five proposals against the working tree rather than against its own text:

| Prior change | Applied | Class it targeted | Present on disk? | Verdict |
|---|---|---|---|---|
| `provisioning/dataverse/verify-flow-trigger.ps1` — the canary probe | never | `exit-zero-does-not-mean-created` | **No** | Proposal only. Carried forward unchanged as item 1 below |
| Probe wired into `smoke_tests` — [pipeline.yml#L909](../../config/revitalise-grant-automation-pipeline.yml#L909), [#L1074](../../config/revitalise-grant-automation-pipeline.yml#L1074) | never | same | **No** | Carried forward as item 2 |
| Probe row in [seed-test-data.ps1](../../provisioning/dataverse/seed-test-data.ps1) | never | same | **No** | Carried forward as item 3 |
| [C-TECH-064](../../constraints/technology/technology-constraints.md#L134) `Verify By` amendment | never | same | **No** | Carried forward as item 4, now covering two properties instead of one |
| Ladder table in `knowledge/technology/testing-tools.md` | never | same | **No** | Carried forward as item 10 |
| Retire [C-TECH-023](../../constraints/technology/technology-constraints.md#L63) | never | non-mechanical `Verify By` | **No** — still active | Carried forward as section 4 |

The review before it did land, and two of its gates have now produced results worth keeping:

| Prior change | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|
| [verify-environment-access.ps1](../../provisioning/dataverse/verify-environment-access.ps1) + [C-TECH-065](../../constraints/technology/technology-constraints.md#L135) | identity not onboarded to the target environment | No | **Working, and it changes today's diagnosis.** It returns PASS against TST/ACC, so the dead trigger is not an access problem |
| The blocker trigger in [verify-improvement-log.py#L237](../../scripts/verify-improvement-log.py#L237) | an unprocessed finding queue | No | **Working, and it is the only reason this dispatch exists.** It stayed red through a stalled review and forced a re-dispatch |

**The one that misfired is the same one that worked.** It kept the pressure on correctly, and it
could not tell the reviewer that the analysis it was demanding had already been written. A second
strategic-tier session re-derived a six-rung cluster analysis that was sitting in a file. That is
logged as its own finding and fixed as item 7.

---

## 2. Clusters and promotion decisions

### CLUSTER A — proving a Dataverse trigger is alive

```
CLUSTER:    a Dataverse-triggered flow reports every correct state and does not fire, and a
            "successful re-run" cannot tell you otherwise
            (IMP-0148 blocker, IMP-0151; prior rungs IMP-0100, IMP-0104, IMP-0106, IMP-0113,
             IMP-0114, IMP-0136, IMP-0139)
Class:      exit-zero-does-not-mean-created (x13) + gate-reassures-wrongly (x7)
Altitude:   CLASS, and a change of EVIDENCE KIND rather than another field to read
Ladder row: "second instance -> generalise. Instance patches are forbidden here."
Becomes:    a behavioural probe (item 1), wired into every environment's smoke tests (item 2),
            a single probe row before the other eleven (item 3), and a Verify By that refuses
            metadata as evidence (item 4)
Retires:    no constraint. It retires a HABIT: the metadata checklist may no longer be recorded
            as evidence that a trigger works, and a Resubmit may no longer be reported as a run
Cites:      IMP-0148, IMP-0151, IMP-0104, IMP-0106, IMP-0113, IMP-0114
Residual:   the probe writes a real row to a real environment, so it is refused wherever writes
            are refused and must clean up after itself in a finally block. It detects and cannot
            fix. It also cannot separate "the trigger is dead" from "the flow ran and failed
            before writing", so it reports the three observable effects separately rather than
            one boolean.
```

Read the history in order. Every rung was a real fix that added one more thing to read, and each
was defeated by the next incident.

| Finding | What was added to the checklist | How the next one defeated it |
|---|---|---|
| `IMP-0100` | `statecode` must be 1, not 0 | statecode 1 with no registration at all |
| `IMP-0104` | so also assert a `callbackregistration` row exists | a row existed but predated the import |
| `IMP-0114` | so also compare its `createdon` against the flow's `modifiedon` | a designer save silently changed the trigger's scope |
| `IMP-0106` | so also re-read `subscriptionRequest/scope` from `workflow.clientdata` | — |
| `IMP-0148` | **all of the above pass and the flow still does not fire** | — |
| `IMP-0151` | — | and the reassurance that it *had* been fixed was a Resubmit, which never touches the trigger path |

`IMP-0148` is the terminal proof that the checklist is the wrong *kind* of evidence: registration
not stale, scope 4, `runas` 3, message Create, entity `rev_application`, and twelve rows sat
unscored for nine minutes with no async operation and no error-log row. The platform never
attempted the call. A seventh field to read is the instance patch the altitude rule forbids, and on
this evidence it would not have helped.

`IMP-0151` is why this cluster has two members instead of one. After the missing settings rows were
seeded, the flows were reported as re-run and succeeding — by Resubmit from run history, which
replays the original trigger payload and never goes near the subscription path. One clarifying
question is all that stood between that report and a blocker being closed on it. The probe answers
this structurally: a canary row is a create, so it cannot be a replay.

**The property, independent of the instance:** *a trigger is proven by causing it to fire, not by
reading the state that is supposed to mean it will.* In [C-TECH-053](../../constraints/technology/technology-constraints.md#L108)'s
own vocabulary, the entire metadata checklist is V3 — accepted by the target — recorded as though it
were V5.

**What this does not do.** It does not make the flow fire. The remedy for a dead registration is a
human opening the flow in the Power Automate designer and saving it, never a `statecode` PATCH, and
no identity this project holds has maker access to TST/ACC. The probe's value is that it turns a
nine-minute silent non-event into one FAIL line naming the person and the click.

### CLUSTER B — a guess inside an instruction

```
CLUSTER:    a platform mechanism's direction inferred from a name, and asserted in a DISPATCH
            INSTRUCTION rather than in an artefact
            (IMP-0153 blocker; class x19)
Class:      platform-contract-guessed-not-groundtruthed
Altitude:   CLASS on the read path, plus a mechanical guard on the artefact the instruction
            would have edited
Ladder row: "the system's own memory failed -> a read-path change", and above it "a tool could
            catch it mechanically"
Becomes:    an allow-list check over the profile's member list (item 5), the read-path fix that
            actually caused it (items 8 and 9), and profile membership added to the live-read
            list in C-TECH-064 (item 4c)
Retires:    nothing. This class has never had a defence that pointed at an instruction
Cites:      IMP-0153, and the eighteen prior members of the class
Residual:   the allow-list can only see membership DECLARED in a settings file. A member added
            by hand in the maker portal is invisible to every source-side gate, which is why
            item 4c puts profile membership into the live-read list too. And no gate reads a
            dispatch instruction before it is sent — items 8 and 9 change what the dispatching
            agent knows, not what a script can check.
```

The instruction said *bind the trustee role to the restricted-columns profile*. That is backwards.
Membership in that profile is what **grants** read on all 39 secured columns, raw applicant
narratives included; the control is that nobody is a member. Executing the instruction would have
handed trustees the precise disclosure that FR-036, NFR-003 and ADR-002 exist to prevent.

Three facts decide the altitude, and the third is the one that matters:

1. **The instance is already closed, in source.** The receiving agent refused the instruction and
   ground-truthed the profile itself. The trustee team is absent from the member list in both
   [test-settings.json#L243](../../provisioning/deploymentSettings/test-settings.json#L243) and
   [prd-settings.json#L278](../../provisioning/deploymentSettings/prd-settings.json#L278), and the
   role file states the absence is the mechanism at
   [REV Trustee.xml#L68](../../src/solutions/RevitaliseGrantAutomation/Roles/REV%20Trustee/REV%20Trustee.xml#L68).
   Nothing was disclosed and there is no rework.
2. **Nothing checks it.** Membership is not in the solution at all — the profile XML says so in its
   own header at [FieldSecurityProfiles.xml#L18](../../src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml#L18)
   — it is applied by [ensure-column-security-profile-members.ps1#L126](../../provisioning/dataverse/ensure-column-security-profile-members.ps1#L126)
   from a settings array. So the only thing standing between the trustee role and 39 secured columns
   today is a comment in a JSON file. An allow-list over that array is cheap, mechanical, and fails
   HARD in CI the moment anyone adds a persona.
3. **The dispatching agent had no instruction to ground-truth anything.**
   [how-to-verify-a-platform-contract.md#L3](../../skills/how-to-verify-a-platform-contract.md#L3)
   lists five agents in its *Used by* line and lead-agent is not one of them, and
   [lead-agent.md#L161](../../agents/lead-agent.md#L161) does not load it. Eighteen prior members of
   this class were all *artefacts* — solution XML, flow JSON, settings files — and every defence
   built for them points at an artefact. An instruction that asserts how a platform mechanism
   behaves is the same claim with no gate anywhere near it.

That third fact is the promotion. The rule stops being *"verify an artefact before you commit it"*
and becomes *"verify a platform claim before you assert it, wherever you assert it"* — and the
agent that writes dispatch instructions has to be told, because today it is not.

### CLUSTER C — a HARD gate that fails a correct step

```
CLUSTER:    a false FAIL in a CI-wired gate, from an off-by-one (IMP-0149)
Class:      gate-reassures-wrongly (x7)
Altitude:   INSTANCE. One entry, one function, one character, and its own revisit_when named
            "the next improvement review" — which is this one
Ladder row: "a tool could catch it mechanically"
Becomes:    item 6 — the slice takes its closing parenthesis, plus a fixture that proves the case
Retires:    nothing
Cites:      IMP-0149
Residual:   the fixture proves the single-line form. Any other layout the regex cannot see stays
            unknown, and the failure direction remains a false FAIL, which blocks a correct deploy
            step rather than passing a broken one.
```

[powershell_params#L118](../../scripts/verify-pipeline-config.py#L118) slices the parameter block up
to but not including its closing parenthesis at
[line 143](../../scripts/verify-pipeline-config.py#L143), while the name pattern needs a terminator
*inside* the slice. For a single-line `param()` block the last parameter's only terminator is that
excluded parenthesis, so the gate reports the parameter as missing and fails a step that is
correct. Nothing in the repository is affected today because every provisioning script declares its
parameters across multiple lines. It is here because its own deferral said to come back at the next
review, and because a HARD gate that can fail a correct step is the expensive direction.

---

## 3. Proposed changes

Items 1–4 and 10 are review 4's proposals, carried forward unchanged except where noted. Items 5–9
are new.

| # | Type | Target | Change | Cites | Mechanically verifiable? |
|---|---|---|---|---|---|
| 1 | script (new) | `provisioning/dataverse/verify-flow-trigger.ps1` | The canary probe. Creates ONE minimal `rev_application` row, polls a bounded timeout for any of the three observable effects (`rev_scoredon` set, an async operation, an error-log row), deletes the canary in a `finally`, and reports PASS/FAIL per the provisioning script contract. The FAIL detail names the remedy exactly: open the flow in the Power Automate designer and save it; never PATCH `statecode` | IMP-0148, IMP-0151, IMP-0104, IMP-0114 | YES — Pester tests in `src/tests/provisioning/DataverseScripts.Tests.ps1`, mocked for both outcomes and for the cleanup path |
| 2 | config | [pipeline.yml](../../config/revitalise-grant-automation-pipeline.yml#L909) | Add the probe as the FIRST `smoke_tests` entry for `tst_acc` ([L909](../../config/revitalise-grant-automation-pipeline.yml#L909)) and `prd` ([L1074](../../config/revitalise-grant-automation-pipeline.yml#L1074)), and to `dev`. A deploy that leaves a dead trigger currently reports success | IMP-0148 | YES — `python3 scripts/verify-pipeline-config.py` |
| 3 | script | [seed-test-data.ps1](../../provisioning/dataverse/seed-test-data.ps1) | The test-agent's own proposal: after the six-precondition preflight passes, seed ONE probe row and assert the effect before loading the remaining eleven. Twelve wasted rows and a nine-minute wait become one row and a bounded wait, reported as its own FAILED line distinct from a wrong-answer defect | IMP-0148 | YES — extends the existing precondition block, asserted in `DataverseScripts.Tests.ps1` |
| 4 | constraint | [C-TECH-064](../../constraints/technology/technology-constraints.md#L134) — **amend, no new row** | Three additions to `Verify By`. (a) For a Dataverse-triggered flow, a metadata assertion — `statecode`, `callbackregistration`, `subscriptionRequest` — may NOT be recorded as evidence that the trigger works; the evidence is an observed effect from a row created after the last change to the flow. (b) A run reached by Resubmit is not such evidence. (c) Column-security profile MEMBERSHIP joins the live-read list, beside `fieldpermissions` | IMP-0148, IMP-0151, IMP-0153, plus the five prior rungs | YES — item 1 is the command for (a) and (b); an `Associate`d-teams query for (c) |
| 5 | script | [verify-pipeline-config.py](../../scripts/verify-pipeline-config.py#L240) | New check 13, HARD: an allow-list over `dataverse.columnSecurityProfiles[].memberTeams` in every deployment settings file that declares one. Only the two service group teams are permitted; any persona, role or trustee team added fails the gate and names the disclosure it would cause | IMP-0153 | YES — `python3 scripts/verify-pipeline-config.py`, with a known-bad fixture in `src/tests/build/BuildGates.Tests.ps1` |
| 6 | script | [verify-pipeline-config.py#L143](../../scripts/verify-pipeline-config.py#L143) | Slice the parameter block inclusive of its closing parenthesis so the final parameter has a terminator, and add a single-line `param()` fixture to the known-bad tree | IMP-0149 | YES — the fixture is the proof |
| 7 | script | [verify-improvement-log.py#L237](../../scripts/verify-improvement-log.py#L237) | Give the blocker trigger three states instead of two. Unread stays a FAIL saying "run a review". **Processed-awaiting-approval** (`reviewed_in` names an existing review document) stays a FAIL — a stalled review must not go quiet — but says "read that document and send the keyword; do not re-derive". Reviewer-deferred stays the accepted note. Plus a check that every finding a review document cites carries `reviewed_in` naming it | IMP-0154, IMP-0033 | YES — `python3 scripts/verify-improvement-log.py`, with fixtures for all three states |
| 8 | skill | [how-to-verify-a-platform-contract.md](../../skills/how-to-verify-a-platform-contract.md#L3) | Add `lead-agent` to *Used by*. Add a section: **an instruction is an artefact** — a claim about how a platform mechanism behaves is a platform contract wherever it is written, including in a dispatch to another agent, and a membership list is who a control grants access TO, not who it withholds from. Add one line to the verification-level table at [L124](../../skills/how-to-verify-a-platform-contract.md#L124): a run reached by Resubmit is a replay, not a V5 | IMP-0153, IMP-0151, IMP-0139 | N/A — instruction |
| 9 | agent | [lead-agent.md#L161](../../agents/lead-agent.md#L161) | Load `how-to-verify-a-platform-contract.md` before writing a dispatch instruction that asserts how a platform mechanism behaves. This is the read-path half: the skill's own *Used by* line naming lead-agent changes nothing if lead-agent never opens it | IMP-0153 | N/A — instruction, but its absence is greppable |
| 10 | knowledge | `knowledge/technology/testing-tools.md` | The six-rung ladder table from section 2, so the next agent does not add a seventh field to read | IMP-0148 | N/A — instruction |

**Constraint budget: 0 of 3 used.** One existing row is amended. Cluster A's home is a row whose
subject is already *environment state that solution source cannot express, verified live*; what was
wrong is that its `Verify By` enumerated only metadata queries, which is exactly what these findings
defeat. Cluster B's mechanical half fits an existing HARD gate as one more check, so it needs no row
either.

---

## 4. Retirements

| ID / file | What it was for | Why retired | Replaced by | Coverage proven? |
|---|---|---|---|---|
| [C-TECH-023](../../constraints/technology/technology-constraints.md#L63) | SOFT — new dependencies must come from approved sources | Fourth member of a family whose other three were retired on 2026-08-19, and simply missed in that sweep. This repository has no `package.json`, no `requirements.txt` and no project package reference, so there is nothing to audit. Its `Verify By` is *"Architecture review; code review"*, which `constraints/README.md` rule 5 forbids | Nothing, for the same reason the other three needed no replacement: there are no third-party dependencies to check | YES, vacuously — there is no fixture because there was never a gate. Nothing regresses, because nothing was executing |

Reinstate it with a new id alongside its retired siblings when the Phase 3 Code App introduces a
real dependency manifest. Carried forward from review 4 unchanged; the row is still active on disk.

---

## 5. Findings left unprocessed

No silent caps. Each is now recorded on the entry itself, with an owner and a return condition.

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| IMP-0148 | `exit-zero-does-not-mean-created` | The detection is proposed here in full. The **remedy** is a human opening the flow in the Power Automate designer in the acceptance environment — no identity this project holds has maker access | That person has done it, and a freshly created row scores unprompted. A Resubmit does not close it |
| IMP-0153 | `platform-contract-guessed-not-groundtruthed` | The instance is closed in source. The class fix edits a gate and an agent file, which cannot be self-applied | On approval of items 5, 8 and 9 |
| IMP-0085 | `no-assertion-on-shipped-content` | Table auditing has no representation in solution source and the live verifier needs environment credentials. Unchanged from four prior reviews | The next Dataverse table is built (Phase 3, tasks 6.4 / 8.1) |
| IMP-0112 | `platform-contract-guessed-not-groundtruthed` | The gate is applied and naming all six occurrences on every build. The instance fix restructures a flow that has never run live, so there is nothing to regression-test it against | Before the WordPress integration is connected to DEV |
| IMP-0150 | `hand-maintained-count-drifts-from-source` | Friction, logged today, clusters with neither blocker. Its check also lands in the pipeline preflight, which this review already changes twice — a third edit widens the blast radius of one keyword for no gain in urgency | The next review, or the next time a settings row is added |
| IMP-0152 | `gate-cannot-fail` | Deliberately not bundled behind a blocker's approval. Adding a named-membership evidence rule flips task 0.5 from complete to partial, which changes derived task state and what the PM and commercial agents report — that wants pm-agent in the room | The next review with pm-agent, or immediately if task 0.5 is about to be claimed for acceptance or an invoice |

`IMP-0151` and `IMP-0149` are processed, not deferred: they are folded into clusters A and C and
carry `reviewed_in` pointing at this document. `IMP-0154` was appended by this review and is
answered by item 7.

---

## 6. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 150 | 151 |
| Distinct lessons | 150 | 151 |
| `NEW` entries | 8 (2 blockers with no reason — the gate was red) | 9 (0 blockers without a reason — the gate is green) |
| Recurring classes (x≥2) | 19 | 19 — `learning-substrate-destroyed` moves x12 → x13 |
| Digest lines | 404 | 405 |
| Technology constraints, active | 46 | 45 after the retirement; no new row |

Regenerated with `python3 scripts/generate-known-failure-modes.py` and confirmed current with
`--check`. `python3 scripts/verify-improvement-log.py --check` now exits 0.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-21-improvement-review-5.md

Findings processed: 9 NEW  →  3 clusters (4 processed, 4 deferred with owners, 1 appended)
Regression check:   6 prior changes audited, 0 classes recurred, 5 changes NEVER APPLIED
                    (review 4 stalled at its gate — all five proposals carried forward)
Proposed:           0 constraints (cap 3) — 1 amended, 5 gates/scripts, 2 skill/knowledge edits,
                    1 agent-file edit, 1 config edit, 1 retirement
Altitude calls:     2 generalised from instance to class, 1 left at instance
Digest:             regenerated — 151 lessons, 19 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

### What needs your decision

**The probe writes one row to the environment it checks. Is that acceptable in production?**

It creates one clearly marked application row, waits a bounded time, and deletes it in a `finally`.
The alternative — never proving a production trigger fires — is how this defect reached the
acceptance environment in the first place.

My recommendation is yes, with the delete path covered by its own test. A write to production is
your call, not mine.

**Who opens the scoring flow in the designer in the acceptance environment?**

Nothing in this review makes that flow fire. It needs a person with Power Automate maker access to
REV-GrantApplications-ACC to open `REV | Scoring | Calculate & Flag` and save it. Until that
happens, the trustee walkthrough stays blocked and the probe will report the block rather than
remove it. This question was asked five hours ago in review 4 and has not been answered; it is the
only item here that no amount of engineering closes.

**One thing I did without the keyword, and you should know it.**

The finding log now carries a deferral reason on each blocker, which is what turns the log gate from
red to green. That is bookkeeping — it records the state each finding is in, it applies no proposed
change, and every reason names an owner and a return condition. It is also, honestly, a field
written by the agent the gate summoned, which is the ambiguity item 7 exists to remove: after it,
"a review has processed this and is waiting for you" is a state the gate can say out loud instead of
being indistinguishable from "nobody has looked".

---

## 8. Applied

**`APPROVE IMPROVEMENTS` received 2026-08-21. PARTIALLY APPLIED, 2026-08-21** — 4 of 10 items
plus the retirement are on disk. Two of the four landed in a **different and more mechanical
home** than this review proposed, which is recorded per row rather than smoothed over. Every row
was verified by reading the target file (`IMP-0140`).

| # | Change | State | Evidence |
|---|---|---|---|
| 1 | `verify-flow-trigger.ps1` — the canary probe | **NOT APPLIED** | File absent; carried on `IMP-0148` with an `evidence_grep` asserting the absence |
| 2 | Probe in `smoke_tests` | **NOT APPLIED** | Depends on item 1 |
| 3 | Probe row in `seed-test-data.ps1` | **NOT APPLIED** | Depends on item 1 |
| 4 | [C-TECH-064](../../constraints/technology/technology-constraints.md#L134) — three `Verify By` additions | **APPLIED** | All three clauses present: metadata-is-not-evidence, Resubmit-is-a-replay, column-security MEMBERSHIP. Closes `IMP-0151` |
| 5 | Check 13 in `verify-pipeline-config.py` — `memberTeams` allow-list | **APPLIED ELSEWHERE** | Landed as its own HARD gate, [verify-column-security-membership.py](../../scripts/verify-column-security-membership.py), not as a check inside the preflight. 4 tests green, including the `IMP-0153` negative case. Closes `IMP-0153`'s mechanical half |
| 6 | [verify-pipeline-config.py](../../scripts/verify-pipeline-config.py#L143) — parameter slice inclusive of `)` | **APPLIED** | The slice is `text[start:end + 1]` with the finding cited in place. Closes `IMP-0149` |
| 7 | [verify-improvement-log.py](../../scripts/verify-improvement-log.py) — three states on the blocker trigger | **APPLIED, EXTENDED TO FOUR** | Review 6 item 6 added `already-fixed`. Closes `IMP-0154` |
| 8 | [how-to-verify-a-platform-contract.md](../../skills/how-to-verify-a-platform-contract.md) — "an instruction is an artefact" | **NOT APPLIED** | The skill file carries neither the section nor `lead-agent` in *Used by*. Both findings it served (`IMP-0151`, `IMP-0153`) are closed on the constraint and the gate instead, so this is a **read-path residual**, not an open defect |
| 9 | [lead-agent.md](../../agents/lead-agent.md) — load that skill before a dispatch asserting platform behaviour | **NOT APPLIED** | Pairs with item 8; greppable by its absence |
| 10 | Ladder table in `knowledge/technology/testing-tools.md` | **NOT APPLIED** | Carried on `IMP-0148` |
| — | Retire [C-TECH-023](../../constraints/technology/technology-constraints.md#L63) | **APPLIED** | Struck through with a `retired_reason` + Retired Constraints row |

**Items 8 and 9 are the honest weak spot.** Both findings are marked `APPLIED` on the strength of
a HARD constraint clause and a HARD gate, which is a stronger home than a skill paragraph — but
the *instruction* that produced the backwards role-to-profile binding was written by an agent
reading that skill, and that read path is unchanged. Re-propose it at the next review rather than
treating it as covered.

**This review's open question was already answered when it was asked.** The scoring flow had been
opened and saved; the reviewer confirmed it on 2026-08-21. See `IMP-0171`.
