# Improvement Review 9 — 2026-08-22

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 17 `NEW` → 4 clusters, of which **3 entries were genuinely unread**
**Trigger:** blocker escalation. `IMP-0182` (DEV rejects `pac code push` — the environment's *Power Apps code apps* feature is off) was appended by pipeline-agent from today's DEV deploy of the Trustee Portal.
**Gate:** `APPROVE IMPROVEMENTS`
**WBS:** `system`. The findings guard delivery tasks 6.1–6.5. No contracted task is claimed here.

**Status:** AWAITING `APPROVE IMPROVEMENTS`. Nothing in section 3 has been applied. Three things *were* done, because none of them edits a rule: two new findings were appended, `reviewed_in` was stamped on the three entries whose disposition this review changes, and the digest was regenerated.

---

## The headline

**This review is deliberately small, because the bottleneck is not analysis.** Of the 15 `NEW` entries in the queue when I was dispatched, **one** was unread. Eleven are parked at review 8's gate waiting for a keyword, and three carry standing deferrals whose reasons still hold. I did not re-derive any of the fourteen.

Then I checked what a day of reviewing has actually produced on disk, against the working tree rather than against any document's prose:

| | Items | On disk | Outstanding |
|---|---|---|---|
| Reviews 5 and 6 — approved, tracked by a needle | 4 | **0** | 4 |
| Review 8 — proposed 2026-08-21, never approved | 10 | **0** | 10 |
| **Total awaiting application** | **14** | **0** | **14** |

Review 8's headline was *"this system does not have a proposal problem. It has an application problem."* One review later that diagnosis is measurably worse: the outstanding count went from 6 to 14 in 26 hours, and every one of review 8's ten items is still a proposal. **So this review proposes five items, not ten, and two of them are the new blocker.** Adding an eleventh unapplied proposal to a pile of fourteen is not progress.

The four needles from review 8's own headline table are still absent — I re-ran them rather than trusting the table:

| Finding | Approved in | Artefact that still does not exist |
|---|---|---|
| `IMP-0148` | review 5, items 1–3 | `provisioning/dataverse/verify-flow-trigger.ps1` |
| `IMP-0161` | review 6, item 9 | the `getClient(dataSourcesInfo)` ground truth in [code-apps.md](../../knowledge/technology/code-apps.md#L29) |
| `IMP-0162` | review 6, item 7 | escalation conditions in [models.yml](../../config/models.yml#L249) |
| `IMP-0166` | review 6, item 12 | `EX-004` in [known-exceptions.json](../../contract/known-exceptions.json#L2) |

**And the first of those four has now caused a second, worse defect, which is this review's most important finding.** [C-TECH-064](../../constraints/technology/technology-constraints.md#L134) — a HARD rule — was amended by review 5 to name `verify-flow-trigger.ps1` as the *only* admissible evidence that a Dataverse-triggered flow works, while explicitly ruling out every alternative anyone can produce. The amendment shipped and was committed. The script never existed. A HARD constraint that gates every Dataverse-triggered flow deploy currently admits exactly one form of proof, and that proof cannot be produced by anyone.

---

## 1. Regression check — did review 8's changes work?

**They were never applied, so the honest answer is that they could not have worked.** Review 8's own status header is accurate — unlike review 6's, which review 8 had to correct. Verified by grepping each target:

| Review 8 item | Target | On disk? |
|---|---|---|
| 1 — fifth log state | [verify-improvement-log.py](../../scripts/verify-improvement-log.py#L40) | No — `approved-not-applied` appears nowhere |
| 2 — audited-tables gate | `scripts/verify-audited-tables.py` | No — file absent |
| 3 — `auditedTables` membership | [test-settings.json](../../provisioning/deploymentSettings/test-settings.json), [prd-settings.json](../../provisioning/deploymentSettings/prd-settings.json) | No — both still list four tables; `rev_grant` and `rev_review` absent; no DEV file declares the key |
| 4 — schema script names the audit step | [ensure-schema.ps1](../../provisioning/dataverse/ensure-schema.ps1) | No — no `ACTION REQUIRED` line |
| 5 — reviewer action, `rev_review` auditing | live DEV | Outstanding |
| 6 — chain gate regenerates its cache | [verify-wbs-chain.py](../../scripts/verify-wbs-chain.py#L78) | No — still only advises running the generator when the file is missing |
| 7 — evidence rules repointed | [evidence-map.json](../../contract/evidence-map.json) | No — four `rev_trusteereview` rules remain, zero mention the Code App path |
| 8 — pack-warning registry row | `scripts/derived-counts-registry.json` | No |
| 9 — foreground-retry step | [pipeline-agent.md](../../agents/pipeline-agent.md) | No — no occurrence of "foreground" |
| 10 — triaged npm warning | [dev-summary](../../docs/development/revitalise-grant-automation-dev-summary.md) | No |

### The gate that fired correctly, and the instruction that overrode it

**The one mechanism that is working is the log gate, and this dispatch demonstrates both halves of it.** [verify-improvement-log.py](../../scripts/verify-improvement-log.py#L26) correctly separated 1 unread entry from 11 awaiting-approval and 3 reviewer-deferred, and printed, about the eleven: *"DO NOT run another review and DO NOT re-derive the analysis … the remedy is a keyword, not a session."* That is exactly right and it is `IMP-0154`'s lesson made mechanical.

It was then overridden, because [improvement-agent.md](../../agents/improvement-agent.md#L80) activation step 2 says *"Read every `NEW` entry"* with no carve-out, and my dispatch instruction repeated it. That step was written when `NEW` meant unread; reviews 5 and 6 gave the gate a four-state model and neither updated the activation step that reads the same field. Appended as `IMP-0183` — a gate reporting the right thing and being talked over is a finding, not a nuisance.

---

## 2. Clusters and promotion decisions

### CLUSTER A — an environment refuses an operation the identity is authorised for

```
CLUSTER:    pac code push fails 403 CodeAppOperationNotAllowedInEnvironment until a human
            enables a per-environment product feature (IMP-0182 blocker)
Class:      environment-feature-flag-undeclared (x1)
Altitude:   CLASS, taken early. Ladder §4 permits skipping ahead on a first instance when the
            severity is blocker AND the mechanism is a platform law — both hold: the 403 is
            enforced per environment by the platform, and the finding ground-truthed that there
            is no CLI verb and no organization-entity attribute for it
Ladder row: "a tool could catch it mechanically"
Becomes:    items 1, 2, 3 — knowledge, a declared prerequisite, and check 13
Retires:    nothing
Cites:      IMP-0182, IMP-0161, IMP-0146, IMP-0105
Residual:   the gate proves the prerequisite is DECLARED in the pipeline config. It cannot prove
            the toggle is ON, and unlike the identity probe there is no read to prove it with —
            the finding looked and found none. That half stays a human act with a recorded
            outcome, and the first push is its own evidence
```

The mechanism this belongs to already exists and the category was simply unrecognised. [C-TECH-065](../../constraints/technology/technology-constraints.md#L135) says *"a credential that authenticates is not an identity that is authorised"* and requires the pipeline config to declare an identity probe before the first step that depends on it. This is the same ladder one rung further out: **an authorised identity is not a permitted operation.** Same failure direction, same `environment_prerequisites` block, same enforcement script — so this is an amendment to that row, not a new one.

Two facts make the case concrete. The [DEV prerequisites block](../../config/revitalise-grant-automation-pipeline.yml#L560) declares eight items and none is the code-apps toggle. And the [push step's own `blocked_on`](../../config/revitalise-grant-automation-pipeline.yml#L677) names two causes — a harness refusal and a null `appId` — and *neither is what stopped the run*. A config that explains why a step is blocked, in two paragraphs, without naming the actual blocker, is worse than one that says nothing.

### CLUSTER B — a HARD constraint whose only admissible evidence cannot be produced

```
CLUSTER:    C-TECH-064 names provisioning/dataverse/verify-flow-trigger.ps1 as the sole
            admissible proof that a Dataverse-triggered flow fires, and that script has never
            existed (IMP-0184 new; instance IMP-0148)
Class:      declared-policy-not-mechanically-enforced (x4)
Altitude:   CLASS — fourth instance. No instance patch permitted
Ladder row: "second instance -> generalise" + "a tool could catch it mechanically"
Becomes:    item 4 — scripts/verify-constraint-verifiers.py
Retires:    nothing
Cites:      IMP-0184, IMP-0148, IMP-0174, IMP-0165
Residual:   the gate proves a path a Verify By names EXISTS. It does not prove the script is
            wired into a build config and runs — that is IMP-0174's rung and it is a separate
            check. Together they cover "named but absent" and "present but never executed";
            neither covers "runs and asserts the wrong property"
```

This is the expensive shape, not merely an untidy one. The row rules out, by name, every form of evidence a person can actually generate — `statecode`, a `callbackregistration`'s existence and `createdon`, `subscriptionRequest/scope`, `runas`, and any run reached by Resubmit — and then names one command as the replacement. The command is untracked in git. So the constraint cannot be satisfied, cannot be honestly reported as PASS, and has been in that state in the committed tree since review 5.

**The coverage measurement is what settles the altitude.** I extracted every repository path from every `Verify By` cell across all three constraint files: **22 distinct paths, 21 of which exist.** One gate, one currently-failing fixture on the live tree, and 21 passing cases proving it does not over-fire. That is the cheapest useful gate available in this repository right now.

### CLUSTER C — the activation step and the gate disagree about the same field

```
CLUSTER:    improvement-agent activation step 2 says "read every NEW entry" while the log gate
            says a settled entry needs a keyword, not a review (IMP-0183 new)
Class:      agent-instructions-describe-a-topology-that-changed (x4)
Altitude:   CLASS on the read path — an activation order, not another paragraph
Ladder row: "the system's own memory failed -> a read-path change"
Becomes:    item 5
Retires:    nothing
Cites:      IMP-0183, IMP-0154, IMP-0169, IMP-0181
Residual:   it fixes the order this agent reads in. It does not stop a DISPATCHER from widening
            the scope in the prompt, which is what happened here — that needs the blocker
            trigger in agents/WORKFLOW.md to say "the unread blocker", and item 5 changes only
            the trigger row this agent owns
```

### CLUSTER D — the standing queue, carried without re-derivation

Fourteen entries, no analysis performed, by design. Eleven are review 8's and review 6's business and need a keyword against the documents they already name; three are standing deferrals whose reasons review 8 re-checked yesterday and which still hold. Section 5 lists them.

---

## 3. Proposed changes

Five items. **Two finish the new blocker, one is the cheapest gate in the repo, one is a config correction, and one stops this review costing what it cost.**

| # | Type | Target | Change | Cites | Mechanically verifiable? |
|---|---|---|---|---|---|
| 1 | knowledge | [code-apps.md](../../knowledge/technology/code-apps.md#L29) | Record the *Power Apps code apps* per-environment product toggle as a ground-truthed prerequisite: admin centre → Environments → &lt;env&gt; → Settings → Product → Features, no CLI verb and no organization attribute, a human System/Environment Administrator once per environment before the first push. **Fold this into review 6 item 9's already-approved rewrite of the same file** — one edit discharges both, and the file's [ALM section](../../knowledge/technology/code-apps.md#L103) currently says a push simply publishes. Also add both new classes to the [digest routing table](../../scripts/generate-known-failure-modes.py#L114) so these lessons reach pipeline-agent at the moment they apply instead of landing in *Unrouted* | IMP-0182, IMP-0161 | YES — the digest's Unrouted section must lose both classes |
| 2 | config | [pipeline.yml DEV prerequisites](../../config/revitalise-grant-automation-pipeline.yml#L560), [push step](../../config/revitalise-grant-automation-pipeline.yml#L677) | Declare the toggle as a DEV `environment_prerequisites` entry with `script: manual` and a named owner, and add it to the TST/ACC and PRD blocks against the day promotion is permitted. Correct the push step's `blocked_on`, which names two causes and not the one that actually stopped the run | IMP-0182 | YES — item 3 goes green |
| 3 | script | [verify-pipeline-config.py](../../scripts/verify-pipeline-config.py#L315) | **Check 13**, mirroring `check_environment_access`: an environment whose steps include a `pac code push` must declare the code-apps feature prerequisite *before* that step. Amend [C-TECH-065](../../constraints/technology/technology-constraints.md#L135) one rung — *"and an authorised identity is not a permitted operation"* — naming check 13 in its `Verify By` | IMP-0182, IMP-0146 | YES — **currently RED**: the push step exists and no environment declares the prerequisite, so the known-bad fixture is the live tree |
| 4 | script (new) | `scripts/verify-constraint-verifiers.py` | HARD. Extract every repository-path token from every constraint row's `Verify By` cell and assert it exists on disk. Fails when it resolves zero paths (the `IMP-0007` shape). Then either build the canary probe or correct C-TECH-064's clause to name evidence that can be produced — **the constraint must not keep pointing at a script nobody has written** | IMP-0184, IMP-0148, IMP-0174 | YES — **currently RED** on exactly one row, with 21 resolving paths as the over-fire control |
| 5 | agent | [improvement-agent.md](../../agents/improvement-agent.md#L80) activation step 2, [blocker trigger](../../agents/improvement-agent.md#L50) | Run `verify-improvement-log.py --check` first and scope the full read to the unread subset it names; entries in awaiting-approval are reported by the document they name, never re-derived. Make the blocker row read *"process the unread blocker"* so one blocker does not summon a review of the whole queue | IMP-0183, IMP-0154 | N/A — an instruction, but its absence is greppable and the state names come from the gate |

**Constraint budget: 0 of 3 used.** One row is amended ([C-TECH-065](../../constraints/technology/technology-constraints.md#L135), item 3). Item 4 also obliges a correction to [C-TECH-064](../../constraints/technology/technology-constraints.md#L134)'s flow-trigger clause, which is a repair of an existing row rather than a new rule.

---

## 4. Retirements

**No fresh sweep, and I am saying so rather than implying one.** Review 8 reviewed all 47 active technology constraints 26 hours ago and found no clean candidate; nothing has been retired or superseded since, so a second full pass today would produce the same answer at strategic-tier cost.

**The standing consolidation candidate is unchanged and I am again not taking it.** [C-TECH-001](../../constraints/technology/technology-constraints.md#L34), [C-TECH-002](../../constraints/technology/technology-constraints.md#L35) and [C-TECH-044](../../constraints/technology/technology-constraints.md#L86) govern one subject and are now backed by a real gate. Collapsing them would replace three unenforceable rows with one enforced row. The reason for holding is the same reason this review proposes five items instead of ten: fourteen approved or proposed changes are unapplied, and opening a front on three HARD credential rules while that is true is how the pile grows.

**One retirement-shaped observation worth recording.** C-TECH-064's flow-trigger clause is the first case in this repository of a constraint that is not merely unenforced but *unsatisfiable*. If the canary probe is not going to be built, the honest action is to narrow that clause rather than leave a HARD rule nobody can comply with — that is a question for the reviewer in section 6, not a retirement I should take unilaterally.

---

## 5. Findings left unprocessed

No silent caps. Fourteen, in two groups, none re-derived.

**Eleven parked at a gate, not deferred.** These need a keyword sent against the document each already names, per the log gate's own instruction and `IMP-0154`'s rule. Re-analysing them here would be the fourth review in a row to do it.

| Findings | Document | What they need |
|---|---|---|
| `IMP-0148`, `IMP-0178` (both blocker), `IMP-0161`, `IMP-0162`, `IMP-0166`, `IMP-0173`, `IMP-0176`, `IMP-0177`, `IMP-0179`, `IMP-0180`, `IMP-0181` | [review 8](2026-08-21-improvement-review-8.md) | `APPROVE IMPROVEMENTS` against that document, or feedback on it |

**Three standing deferrals, reasons unchanged.** Review 8 re-checked all three yesterday; I am not re-stamping them, because their disposition has not changed and review 6's and review 8's reasoning stands.

| Finding | Class | Revisit when |
|---|---|---|
| `IMP-0085` | `no-assertion-on-shipped-content` | Review 8 item 2 is applied; the residue is then a live query only |
| `IMP-0112` | `platform-contract-guessed-not-groundtruthed` | Before the WordPress integration is connected to DEV |
| `IMP-0152` | `gate-cannot-fail` | A review with pm-agent present, or immediately if task 0.5 is claimed for acceptance or an invoice |

---

## 6. What you need to decide

**Approve this review, or approve review 8 first.** These are independent documents and both are waiting. Review 8 carries the `rev_review` audit blocker and nine other items; this one carries the code-app blocker and the unsatisfiable-constraint repair. Nothing in either conflicts with the other, so `APPROVE IMPROVEMENTS` on both is the shortest path — but if you want one at a time, review 8 is the older debt and the larger one.

**Who turns the code-apps feature on in DEV, and when.** This is an admin-centre act by a System or Environment Administrator, once per environment, and no script in this repository can do it or even read whether it is done. Until it happens the Trustee Portal cannot be pushed to DEV at all, so WBS 6.1–6.5 is blocked on it in the same way review 8's item 5 blocks the test cycle. Item 2 records it as a named prerequisite with an owner; naming you as that owner is my assumption unless you would rather route it to Wanstor with the other tenant-level acts.

**Whether the flow-trigger canary probe is still going to be built.** [C-TECH-064](../../constraints/technology/technology-constraints.md#L134) currently forbids every producible form of evidence that a Dataverse-triggered flow fires and mandates one script that does not exist. There are two honest exits: build the probe (approved in review 5, item 4 of this review would then go green on its own), or narrow the clause to admit an observed effect recorded by hand. I recommend building it — the row's reasoning is sound and six successive findings earned it — but leaving a HARD rule unsatisfiable is not one of the options.

---

## 7. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 179 | 181 |
| Distinct lessons | 179 | 181 |
| `NEW` entries | 15 (1 unread, 11 awaiting-approval, 3 reviewer-deferred) | 17 (0 unread once stamped, 14 awaiting-approval, 3 reviewer-deferred) |
| Recurring classes (x≥2) | 23 | 24 — `declared-policy-not-mechanically-enforced` reaches x4, `agent-instructions-describe-a-topology-that-changed` x4 |
| Largest class | `gate-cannot-fail` x24 | `gate-cannot-fail` x24 |
| Technology constraints, active | 47 | 47 — 0 proposed, 0 retired, 1 `Verify By` amended, 1 clause to repair |

Regenerated with `python3 scripts/generate-known-failure-modes.py` and confirmed current with `--check` (exit 0).

`python3 scripts/verify-improvement-log.py --check` **stays red on purpose** until the keyword arrives: `IMP-0148` and `IMP-0178` are blockers in the `awaiting-approval` state, which review 5 item 7 deliberately kept as a FAIL so a stalled review cannot go quiet. That behaviour is working exactly as designed, and it is the reason the fourteen outstanding items in section 1 are visible at all.

---

## 8. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-22-improvement-review.md

Findings processed: 17 NEW  →  4 clusters
                    3 unread and processed here (IMP-0182 blocker; IMP-0183, IMP-0184 appended)
                    14 carried untouched — 11 parked at review 8's gate, 3 standing deferrals
Regression check:   10 prior proposals audited (review 8) — 0 on disk, 10 outstanding.
                    Plus 4 approved needles from reviews 5-6 re-tested: 0 on disk.
                    14 items now awaiting application, up from 6 in 26 hours.
                    1 class recurred after a gate fix: the log gate reported the queue
                    state correctly and the activation step overrode it (IMP-0183).
Proposed:           0 constraints (cap 3), 2 gates/scripts, 1 config, 1 knowledge edit,
                    1 agent-file edit, 0 retirements
                    (1 Verify By amended; 1 HARD clause to repair; 1 consolidation
                     candidate named, not taken)
Altitude calls:     3 generalised from instance to class, 0 left as notes
Blocker:            IMP-0182 (DEV rejects pac code push — the environment's code-apps
                    feature is off) — items 1-3. The toggle is an admin-centre act no
                    script here can perform or read; WBS 6.1-6.5 stays blocked until
                    a human does it.
Digest:             regenerated — 181 lessons, 24 recurring classes

IMPROVEMENT LOG: 2 entries appended — IMP-0183, IMP-0184  |  digest regenerated: YES

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```
