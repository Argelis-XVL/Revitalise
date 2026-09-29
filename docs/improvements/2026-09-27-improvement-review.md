# Improvement Review — 2026-09-27 (1): a column's type cannot change once it exists

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 1 `NEW` → 1 cluster
**Trigger:** reviewer request (relayed by lead-agent as a blocker escalation; see §0 — the finding is governance-lane, so the blocker rung did not require this dispatch)
**Gate:** `APPROVE IMPROVEMENTS`
**Status:** DRAFT — parked at the gate, nothing applied.
**WBS:** `wbs:4.2,4.3` (the TAD revision this finding blocks). The rule changes themselves are system work and map to no billable task.

---

## Summary

A Dataverse column cannot change its data type once it exists in an environment. This project measured that twice, in August, and wrote it into the knowledge file the architect reads at activation. The architecture document still specified eleven type changes as if they would ship like any other edit. Writing the lesson down a second time would not have helped, so this review proposes a build check that fails when a column's type changes, and a constraint row the architect's own gate checks.

**Waiting on you:** `APPROVE IMPROVEMENTS`, or feedback. No decisions are required first. There is one item to keep in mind when you review the architect's rev 13 (see *What is still open*).

## What this review proposes

1. **A build check that fails when an existing column's type changes** (new script `verify-attribute-type-stability.py`, wired HARD after the [component-shape step](config/revitalise-grant-automation-build.yml#L394)). It compares every column's `<Type>` in `Entity.xml` against a committed record of each column's type, in a new file `config/attribute-type-lock.json`. A change fails the build unless that file declares it as a planned retype, with its route, the environments where the column is live, and who authorised it. The historical record shows this catches the failure on the first build, before any import.

2. **One new HARD constraint, `C-TECH-080`**, next to [C-TECH-050](constraints/technology/technology-constraints.md#L92). It states the platform rule and names the build check as its verification. The architect runs a check against every technology constraint at its own gate ([constraints/README.md](constraints/README.md#L75)). So this row reaches the next design that proposes a retype while it is being written, which the knowledge section did not.

3. **The existing knowledge section is extended, not duplicated** ([dataverse.md, "Changing a Column's Data Type After It Has Shipped"](knowledge/technology/dataverse.md#L327)). It covers only Picklist to Text today. It gains the general rule, which Microsoft documents: *"you can't change the Name and Data type if you saved changes to the table to add the column"* ([Microsoft Learn](https://learn.microsoft.com/power-apps/maker/data-platform/create-edit-field-portal#edit-a-column)). It also gains what the second retype on 2026-08-21 measured ([Dev Summary](docs/development/revitalise-grant-automation-dev-summary.md#L4717)), the two routes to choose between, and a pointer to the new check.

### Elements added

| Element | What it is |
|---|---|
| `scripts/verify-attribute-type-stability.py` (+ its engine copy) | The build check, with `--selftest` and `--update` |
| `config/attribute-type-lock.json` | The committed type record, seeded from the current committed `Entity.xml` files, plus an empty `planned_retypes` list |
| `C-TECH-080` | The constraint row |

### Elements changed

| Element | Change |
|---|---|
| `config/revitalise-grant-automation-build.yml` | One HARD step, `attribute-type-stability`, after `component-shape` |
| `knowledge/technology/dataverse.md` | The retype section generalised and extended |

## What is still open

**The architect's rev 13 is being written now, and one of its claims should be checked when it reaches you.** When this review read it (20:11, mid-write), rev 13 point 2 said that field permissions on the five secured columns *"survive the delete-and-recreate because the profile's RootComponent and the attribute's own IsSecured flag are re-applied by the same Entity.xml/FieldSecurityProfiles.xml pack"* ([TAD rev 13](docs/architecture/revitalise-grant-automation-architecture.md#L196)). Two records disagree with that. When columns were deleted on 2026-08-21, Dataverse removed their permission rows automatically ([Dev Summary](docs/development/revitalise-grant-automation-dev-summary.md#L4768)). And [C-TECH-050](constraints/technology/technology-constraints.md#L92) records that adding a field permission through import has failed live, so permissions go through the Web API. Rev 13 also says the permissions are verified live per column before the final import, which would catch the problem. The text may change before the architect's gate returns, so this is a note for your review of rev 13, not a finding against it.

**The TAD defect itself is not closed by this review.** lead-agent routed it to architect-agent at 20:04, and that work is running. This review's changes stop the same mistake reaching a build. They do not correct rev 12. The finding stays open until you approve the revised design (§5 of this document, and the disposition in §8).

**The build check sees source, not the live environment.** A column whose type was changed by hand in the maker portal would not be noticed. `ensure-schema.ps1` reports `EXISTS` for a column whose live type differs from source ([Dev Summary](docs/development/revitalise-grant-automation-dev-summary.md#L4717)), so nothing compares live types at deploy time either. Fixing that means the script has to authenticate to an environment, so it is delivery work and is handed on in §3.1. This review does not build it.

## What you need to decide

Nothing blocks the keyword.

Closing line: premises re-measured by command at draft time, listed in §2. The new check has not been written, so it has no selftest or corpus run of its own yet. The corpus figures in §2 come from a scratch script over the real git history, and the check must reproduce them at apply time before it is wired.

---

## 0. Where this review departs from the finding and the brief, and why

**The finding's premise that the lesson "lives only in Dev Summary prose" is false.** `knowledge/technology/dataverse.md` has carried the section since 2026-08-18 ([L327](knowledge/technology/dataverse.md#L327), applied from the first retype finding). `architect-agent` loads that file at activation ([architect-agent.md](agents/architect-agent.md#L385)). The first finding's lesson is in the digest, although its section cap renders it only in the appendix. A knowledge line was the proposed remedy, and a knowledge line was already in place when the defect happened. That is the ladder row *"an agent had the information and still did the wrong thing"*, and it rules out a knowledge edit as the primary change. Logged as a new finding (listed in §5).

**The finding's proposed gate baseline, "the last shipped build manifest's Type", cannot be built as written.** Build manifests do not record attribute types. They record a `source_commit`, but 57 of the 68 tracked manifests were built from a dirty tree (`source_tree_dirty_paths` non-empty), so that commit is not what shipped. The next candidate, git history, also fails: CI checks out with `actions/checkout@v4` at the default depth of 1 ([ci.yml](.github/workflows/ci.yml#L300)), so a history-based check would compare nothing in CI. That would be the gate-cannot-fail class, which has 51 recorded instances. A committed lock file is the design that works for both.

**The brief framed this as a blocker that must be processed immediately. It is governance-lane.** `defect_in` names only the TAD. `verify-improvement-log.py --check` reports *"1 governance-lane blocker(s) open, NOT halting the build"*. [WORKFLOW.md](agents/WORKFLOW.md#L409) and [lead-agent.md](agents/lead-agent.md#L354) both say that kind of blocker is never routed immediately. The routing line quotes the rule's wording from before blockers were split by lane. Processing it now does no harm, and the draft is useful, but the dispatch was not required. Logged as a new finding (listed in §5).

---

## 1. Regression check — did the last review's changes work?

The last review applied is [2026-09-26-improvement-review-6](docs/improvements/2026-09-26-improvement-review-6.md#L150) (applied 2026-09-27).

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| Shared deploy-marker grammar, `lib/deploy_markers.py` | 2026-09-27 | `two-invocation-paths-disagree` | Class tag YES, property NO. The one later entry is a Pester test that passes on its own and fails under the full runner. It is a different mechanism from two parsers reading one log line | Working — leave alone |
| Resolver requires the component's own command | 2026-09-27 | `wrong-artefact-cited-as-evidence` | NO | Working |
| Scoped `verify-work-items.py` notes out-of-scope drift | 2026-09-27 | `hard-gate-red-on-pre-existing-debt` | NO | Working |
| build-agent stages the manifest (step 8a) | 2026-09-27 | `gate-scope-mismatch` | NO | Working |
| Close-out loop, `C-TECH-079` | 2026-09-27 | capability (WS-W2) | NO finding against it | Too early to judge — no build has run the loop end to end yet |
| Item ids through every handoff | 2026-09-27 | capability (WS-W3) | NO | Too early to judge |

**Changes whose class recurred after a *prose* fix:** none from review 6. The prose fix that did fail belongs to this cluster's own history: the 2026-08-18 knowledge section, which is why §2 escalates it.
**Changes whose class recurred after a *gate*:** none.

---

## 2. Clusters and promotion decisions

**The instance count comes from measurement, not from the log's class counter.** The logged instances of this property carry three different `class_instance_of` tags (`platform-contract-guessed-not-groundtruthed` ×2, `approved-document-internally-inconsistent` ×1). So the digest's recurrence table never showed them as one class. Re-derived by a scratch script that walks every commit touching `Entities/` and compares each attribute's `<Type>` with its previous committed value:

| Date | Commit | Column | From → to | What happened | Logged? |
|---|---|---|---|---|---|
| 2026-08-16 | `1faf2b47` | `rev_application.rev_helperrelationship` | picklist → nvarchar | Import rejected it with the named error; column deleted and recreated | yes |
| 2026-08-16 | `1faf2b47` | `rev_application.rev_exceptionalcircumstance` | picklist → bit | same sequence | yes (same entry) |
| 2026-08-17 | `35521fb2` | `rev_application.rev_carehoursperweek` | int → picklist | Transitional pack, six live deletes, recreate ([Dev Summary](docs/development/revitalise-grant-automation-dev-summary.md#L4732)) | **no** — recorded only in the Dev Summary |
| 2026-08-17 | `35521fb2` | `rev_application.rev_exceptionalcircumstance` | bit → picklist | same | **no** |
| 2026-08-21 | — | four `nvarchar` prose columns | planned nvarchar → ntext | Stopped by you before it was written; format change used instead | yes |
| 2026-09-27 | — | eleven `rev_application` columns | planned nvarchar → ntext (TAD rev 12) | Stopped by development-agent before any edit | yes (this finding) |

Four executed type changes in two commits, all on columns that were live, and all four needed the delete-and-recreate sequence. Two more were planned and stopped before anyone edited source. The working tree today holds 9 new `<Type>` lines and no changed ones, all nine on new attributes, so the check's expected result on the current tree is 0 findings.

```
CLUSTER: attribute-type-change-on-a-live-column  (x1 NEW: IMP-0934; property measured x4 executed + x2 planned, across 3 class tags)
Altitude:   LAW — a platform rule measured at import (V3) twice and documented by Microsoft; ENGINE
            for the mechanism (any Dataverse solution), CLIENT-SPECIFIC for the lock file and the
            knowledge text, which name this client's columns
Ladder row: "a tool could catch it mechanically" + "a platform law, or a third instance → a
            constraint row" + "an agent had the information and still did the wrong thing". The
            knowledge-file row already sat below this and did not hold
Becomes:    scripts/verify-attribute-type-stability.py + config/attribute-type-lock.json (HARD
            build step); C-TECH-080; the knowledge/technology/dataverse.md section extended
Retires:    nothing — no instance gate exists for this property; component-shape checks one file's
            structure and cannot compare against an earlier state, so this is not a block in
            constraints/technology/component-shapes.yml
Cites:      IMP-0934
Residual:   (1) the check sees committed source, not live metadata, so a maker-portal type change is
            invisible to it (handed on, §3.1); (2) a column added but never recorded with --update
            is unprotected. The check prints the count of unrecorded columns on every run, so the
            gap stays visible; (3) at design time the check cannot read a TAD. C-TECH-080 reaches
            the architect through its constraint check, which is judgement, not mechanism. The
            mechanism fires at the first build after the source edit, which is V1 and before any
            import
```

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | script | `scripts/verify-attribute-type-stability.py` (+ `.engine/scripts/` copy) and `config/attribute-type-lock.json` | Fail when a recorded attribute's `<Type>` differs from the lock and no `planned_retypes` entry declares it; `--update` records new attributes only and refuses to change a recorded type | IMP-0934 | YES — `python3 scripts/verify-attribute-type-stability.py src/solutions/RevitaliseGrantAutomation --lock config/attribute-type-lock.json` | `HARD` at `config/revitalise-grant-automation-build.yml`, new step `attribute-type-stability` directly after `component-shape` (L394) |
| 2 | constraint | `constraints/technology/technology-constraints.md` | `C-TECH-080`, wording in §3.2 | IMP-0934 | YES — the row 1 command | N/A |
| 3 | knowledge | `knowledge/technology/dataverse.md` → *Changing a Column's Data Type After It Has Shipped* | Generalise and extend, content in §3.3 | IMP-0934 | N/A — reference text | N/A |

**Constraint budget:** 1 of 3 used.

### 3.1 The check, in detail

- **Input:** every `Entities/*/Entity.xml` under the solution path, parsed as XML. `<Type>` is read per `<attribute>` by `LogicalName`. This checks a value, not a phrase.
- **Lock shape:** `{"attributes": {"<entity>.<logicalname>": "<type>"}, "planned_retypes": [{"attribute", "from", "to", "route": "new-column" | "delete-and-recreate" | "pre-ship", "live_in": [...], "authorised_by", "date", "procedure": "knowledge/technology/dataverse.md"}]}`. `route` and `live_in` are values, so a declaration without a plan cannot pass.
- **Outcomes:** type differs and nothing declared → **FAIL**, and the message names the knowledge section and both routes. Type differs and a matching declaration exists → **WARN**, printing the declared route. Attribute not in the lock → **NOTE**, with a count and the `--update` command. A declaration whose `from` no longer matches the lock → **FAIL**, because a stale plan is not a plan.
- **Seeding:** from the committed `Entity.xml` files at HEAD, so the nine uncommitted new attributes start unrecorded, which is correct because none has shipped.
- **Proof before wiring:** `--selftest` with known-bad fixtures. Then a replay of the two historical commits: a lock seeded from `1faf2b47^` and checked against `1faf2b47` must fail on exactly 2 attributes, and likewise for `35521fb2`. Then the current tree must give 0 findings. The review records "N findings, K true positives" for each run.
- **Handed on, not built here:** `ensure-schema.ps1` should report `TYPE-MISMATCH` rather than `EXISTS` when a live attribute's type differs from source. That is the live half this check proxies for. It authenticates, so it belongs to development-agent. Requirement: one new outcome word; verification: a Pester case with a mocked `AttributeType` mismatch. Route it with the next data-layer dispatch; it does not need its own.

### 3.2 `C-TECH-080`, exact wording

| ID | Constraint | Severity | Scope | Rationale | Verify By |
|---|---|---|---|---|---|
| C-TECH-080 | **An attribute's data type never changes once the attribute exists in any environment.** A design or source edit that changes an existing attribute's `<Type>` must choose a route and declare it in `config/attribute-type-lock.json` → `planned_retypes`: a **new column under a new logical name** (additive, import-safe), or the measured **delete-and-recreate** sequence, run as a reviewer-authorised live operation in each environment where the column is live, with its field permissions re-created through the Web API (`C-TECH-050`) and the loss of its data and audit history stated | HARD | architect-agent, development-agent, build-agent | Solution import rejects a type change (*"Attribute rev_helperrelationship is a Picklist, but a String type was specified"*, 2026-08-16), and Microsoft documents that a column's data type cannot change after the column is saved. Four executed retypes on 2026-08-16/17 each needed a transitional import, a live delete and a recreate. A TAD then specified eleven more as ordinary import edits (`IMP-0934`) while the knowledge file said otherwise | `python3 scripts/verify-attribute-type-stability.py src/solutions/RevitaliseGrantAutomation --lock config/attribute-type-lock.json` |

### 3.3 Knowledge section — what it gains

1. **The general rule**, with the Microsoft Learn quotation and link, replacing *"Picklist → String/Boolean"* as the headline. Measured instances then cover picklist→nvarchar, picklist→bit, int→picklist and bit→picklist, and the documented rule covers nvarchar→ntext.
2. **The second measured sequence (2026-08-21):** revert the live shape in a transitional pack, remove form controls, import, delete, recreate through `ensure-schema.ps1`, import the real target. It also gains the two facts that sequence found. `ensure-schema.ps1` reports `EXISTS` on a type mismatch. Deleting a secured attribute removes its field-permission rows, so they must be re-created.
3. **The environment rule:** a retype is only needed where the column is live. In an environment with no import yet, fix the source before its first import and nothing is deleted.
4. **What a delete costs:** the column's data and its audit history are gone. The delete is irreversible, and the harness refuses it until you authorise it.
5. **The two routes and the check:** new column under a new name, or delete-and-recreate, declared in the lock file; `C-TECH-080` and the check named.

---

## 4. Retirements

> Retirement check performed: 87 live constraint rows (10 already retired, derived by `grep -rh '^| ~~C-' constraints/`). None is redundant with this change. `C-TECH-050` covers how attributes and field permissions are **created**; `C-TECH-080` covers what may never **change**. They cite each other and neither replaces the other. `C-TECH-060`'s field-length gate reads the same `Entity.xml` files for a different property and stays.

---

## 5. Findings left unprocessed

**Deferred:** IMP-0935, IMP-0936, IMP-0933

| Finding | Class | Why not processed here | Revisit when |
|---|---|---|---|
| IMP-0935 | `finding-premise-fails-re-measurement` | Logged by this review about the finding it processes. It proposes no change on one instance | the next batch review |
| IMP-0936 | `dispatch-brief-asserts-unverified-fact` | Logged by this review about its own dispatch. It proposes no change on one instance | the next batch review |
| IMP-0933 | `dataverse-row-size-ceiling-blocks-blanket-column-widen` | Unread, from the same TAD revision, but out of scope: one unread blocker must not pull in the entries around it. It overlaps: its lesson says a String column cannot become Memo in place, which §3.3 will state. The batch that processes it should not add that sentence a second time | the next batch review |

The 30 other unread entries are outside this dispatch's scope for the same reason. They are listed by `python3 scripts/verify-improvement-log.py --check` and are below the batch threshold.

---

## 6. Digest impact

| | Before this review | After apply |
|---|---|---|
| Log entries | 930 | 932 (this review appended two; applying adds none) |
| Distinct lessons | 921 | 923 |
| Recurring classes (x≥2) | 72 | 72 |
| Digest lines | 607 | 606 |

**Apply-time obligation:** `verify-derived-counts.py` reports the digest's registered size sentence as drifted. It says 603 lines; the measured count is 606. That drift predates this review, which only moved it from 607 to 606. It is corrected at apply, in both copies of `generate-known-failure-modes.py`. The other five drifts that check reports are counts in delivery-owned files (pipeline config, Dev Summary, the Trustee role header), and this review does not touch them.

Regenerated after the two appends with `python3 scripts/generate-known-failure-modes.py`. Apply-time regeneration is expected to leave these figures unchanged, because applying moves statuses and adds no lessons.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-27-improvement-review.md

Findings processed: 1 NEW  →  1 clusters
Regression check:   6 prior changes audited, 0 classes recurred
Proposed:           1 constraints (cap 3), 1 gates/scripts, 1 skill/knowledge edits,
                    0 agent-file edits, 0 retirements
Altitude calls:     1 generalised from instance to class, 0 left as notes
Digest:             will regenerate — 923 lessons, 72 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Planned disposition of the processed entry

Nothing has been done yet. This section records what happens on `APPROVE IMPROVEMENTS`, so that the decision is visible before approval. The record of what was actually done is added below it afterwards.

**IMP-0934 — DEFER, not CLOSE.** Its `observable_at` is V3 and its defect is in the TAD. The three changes above stop a recurrence at build time, but they do not correct rev 12, and nobody in this session can observe the corrected design shipping. On approval it gets a `deferred_reason` recording what landed. It also gets a `revisit_when`: *"the reviewer approves the TAD revision replacing ADR-053 point 3, and, if the delete-and-recreate route is taken, a live DEV `EntityDefinitions` query shows the eleven columns as MemoType with their field permissions present"*. A later review closes it with an `evidence_grep` on the approved TAD and a `reobserved` record from that query.
