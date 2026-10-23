# Improvement Review — 2026-10-22 (3)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 35 `NEW` → 11 clusters (31 unread, 1 logged by this review, 3 reviewer-deferred entries whose return condition this deploy met)
**Trigger:** post-deploy batch — pipeline-agent's DEV PARTIAL (V3) of build `trustee-portal-design-2-20261022-3` ([pipeline.log L457](logs/pipeline.log#L457))
**Status:** APPLIED 2026-10-22 21:05, all 15 rows, on the reviewer's "Approve Improvements" + "Option A please." (Xander Lykopoulos, relayed verbatim by lead-agent). 30 entries closed, 5 deferred, none rejected. Rows 7–15 sit in the `.engine` working tree, uncommitted: the engine commit, push and pointer bump are the reviewer's. See the [applied record](#applied-record--2026-10-22).
**Serves:** `wbs:system`; the deploy it follows serves `wbs:6.3` (unbilled)
**Gate:** `APPROVE IMPROVEMENTS`

---

## Summary

Today's portal deploy reached DEV at V3, and three earlier fixes were confirmed working by it. The 31 new findings become 15 changes: six knowledge corrections, three skill lines, four agent-file rules and one engine script fix. The fix makes the work-item tool refuse a deploy label no environment declares when an item is linked, not one stage later at deploy. Nothing is applied. You have two things to decide: the keyword, and how the 55 work items orphaned by today's folder rename get their evidence back.

## What has been built

1. **The work-item tool now refuses a deploy label that no environment declares, when the item is linked** — [component_label_problems](.engine/scripts/lib/work_items.py#L167), [the link check](.engine/scripts/work-items.py#L104).
   Until now it checked only the label's shape. `script:ensure-schema.ps1` has a valid shape, but nothing in the pipeline config declares it, so WI-0146 could not be marked deployed until pm-agent relinked it. The new check reads the declared labels from the pipeline config. Two new selftest cases pass with the fix, and the first one fails on today's library (link accepted, exit 0), so the test can fail.

2. **The knowledge files now match the design you approved today** — [overview.md L105](knowledge/domain/overview.md#L105), [business-rules.md L91](knowledge/domain/business-rules.md#L91), [regulations.md L29](knowledge/domain/regulations.md#L29), [dataverse.md L240](knowledge/technology/dataverse.md#L240).
   They said three things that are no longer true: that no special-category answer reaches a trustee, that no trustee team may sit in any column-security profile, and that erasure deletes from QuickBooks. Each now states the current rule and cites the approved decision.

3. **Four platform facts measured live today are written where the next agent looks** — [testing-tools.md L157](knowledge/technology/testing-tools.md#L157), [dataverse.md](knowledge/technology/dataverse.md#L507).
   These are: pac's FetchXML quoting, the typed values a Web API bulk delete needs, the header that stops synthetic rows from firing live flows, and the fact that a new field security profile cannot be packed until DEV has given it an id.

4. **Four rules for the agents whose drafts you corrected today** — [lead-agent L335](agents/lead-agent.md#L335), [architect-agent L202](agents/architect-agent.md#L202), [development-agent L337](agents/development-agent.md#L337), [improvement-agent L169](agents/improvement-agent.md#L169).
   Lead-agent quotes your approval together with the proposal you approved, and does not restate it as a mechanism. Architect-agent offers the one-person option when a design needs more people per request, writes a delete guard in your own "final" status, and rechecks old diagram-only steps. Development-agent checks the work-item ledger before it renames a folder. It also copies the last build's warnings into a new feature's Dev Summary. I measure a failure count's cause before I state it.

## Elements changed

| File | Repository | Change |
|---|---|---|
| [lib/work_items.py](.engine/scripts/lib/work_items.py#L167) | engine | `undeclared_component_labels()` (§A) |
| [work-items.py](.engine/scripts/work-items.py#L104) | engine | refusal at `add`/`link`, 2 selftest cases (§B) |
| 6 knowledge files | instance | rows 1–6 (§C) |
| 3 skills, 4 agent files | engine | rows 7–13 (§C) |

## What is still open

**55 work items carry evidence that no longer resolves, because of today's folder rename.** The SOFT `work-items` step went from 1 failure in build `20261021-3` to 326 in this build. All 326 trace to the rename and the variant retirement: 306 name the deleted `-cards` folder, 8 name classic-portal code replaced by the card app, and 12 name `-cards` build or pipeline entries the retirement removed. A plain path substitution re-points 313 of the 322 distinct `-cards` evidence rows; 9 needles are gone. Separately, 51 items still carry the label `operation:code-app-push@trustee-review-portal-cards`, which the renamed config no longer declares. This is ledger work for pm-agent, and how it is done is decision 2.

**The previous review called those 326 "older drift in other items". That was wrong**, and it is logged against this agent (IMP-1239, row 13).

**One test file passes only when an earlier file has run first.** `EntraScripts.Tests.ps1` mocks a function it never loads. Run alone today it fails 25 of its 45 tests (the finding said 45 of 45). In build attempt 1 all 45 failed because the run order was different. It is routed to development-agent; the fix is one dot-source line in its `BeforeAll`.

**The bulk-delete script fix is in the working tree, not yet run live.** development-agent corrected `ensure-bulk-delete-jobs.ps1` and its fakes for the two rejections test-agent measured. Only a session with the provisioning credential can prove it, so that finding stays open.

**I did not build a "soft gate count jumped" warning, because measured on the record it would cry wolf.** Across 76 build manifests, a SOFT count rose against the previous green build 94 times, 20 of them by 10 or more. Most are `routing-reconciliation` swinging between scoped and full builds (9 ↔ 133). A warning on every rise would fire on most builds.

## What you need to decide

**Approve these 15 changes?**

**Problem** — 31 findings since yesterday's batch, including five corrections you made to agent drafts today, are not yet in the rules.
**Suggested fix** — Reply `APPROVE IMPROVEMENTS`; I apply rows 1–15, close 25 entries, defer 5 with their return conditions, and close 3 earlier entries this deploy confirmed.
**What happens if you don't** — Nothing is applied. The knowledge files keep stating three rules that your approved designs have overtaken, and the next agent to read them will argue from them.
[§3, proposed changes](docs/improvements/2026-10-22-improvement-review-3.md#L234)

---

**How should the 55 orphaned work items get their evidence back?**

**Problem** — 55 items (mostly `verified:dev`) cite files and labels the rename removed, so the work-items check reports 326 failures and will hide the next real one.
**Suggested fix** — (a) pm-agent re-points each item with the existing `reopen --retrace`, and lead-agent re-cites your existing DEV verdict to return it to `verified:dev`; the 8 classic-portal items are deferred as superseded by your card-layout choice. Or (b) commission a bulk "move" action for the ledger as a design extension first. Recommended: (a), because it uses the tools that exist and the scope is measured.
**What happens if you don't** — Delivery is not blocked (the step is warn-only), but a build that breaks a real item's evidence will show 327 instead of 326, and nobody will notice.
[verify-work-items step, build config L182](config/revitalise-grant-automation-build.yml#L182)

---

**After approval: one engine commit, then one pointer bump.** Rows 7–15 change files in `.engine` (on branch `deploy-first-learning-and-item-closure`, published). Rows 1–6 are instance files. I will hand over the exact commands with the applied record, in the order `agents/improvement-agent.md` requires (engine push first).

---

Verification: both engine selftests pass with the drafted fix applied to a scratch copy (0 FAIL lines), and the new link case fails on today's library. The 326 failures were classified one line at a time, and the 313-of-322 re-point figure comes from checking each needle at its new path. The 25-of-45 Pester figure is from running that one container alone. **Not verified:** the full build with the fix, and anything above V3 for this deploy (nothing V4 was observed).

---

## 1. Regression check — did the last review's changes work?

The last review applied was 2026-10-22 (2). This deploy also exercises four rows of 2026-10-21's batch, so those are audited too.

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| 10-22 (2) rows 1–2, `fold()` checks the current `source_ref` only | 2026-10-22 | `work-item-source-ref-dangling-after-rename` | NO — the scoped check on WI-0146..0148 is still 0 failures (re-run 18:10) | Working. **But its prose was wrong**: it called the 326 residual failures "older drift"; they are today's rename (IMP-1239) |
| 10-22 (1) rows 1–2, register `trustee_release` rows + `--released-profile` | 2026-10-22 | ADR-085 capability | NO | Working: build `-3` green, engine commit `5fc81e8` published on `origin/deploy-first-learning-and-item-closure` |
| 10-21 row 2, `verify-live-flow-definitions.py` skips a data file with no `JsonFileName` | 2026-10-22 | `gate-defect` (IMP-1178) | NO | Working: this deploy ran it on the default directory, 13/13 ([L456](logs/pipeline.log#L456)) |
| 10-21 row 3, `log-line.py` refuses two entries in one call | 2026-10-22 | IMP-1165 | NO | Working: 0 joined lines among this deploy's 10 (instrument checked: 8 such lines exist earlier in the log) |
| 10-21 row 13, Code App marker form | 2026-10-22 | IMP-1181 | NO | Working: the push marker resolved and WI-0147/0148 reached `deployed:dev` ([L454](logs/pipeline.log#L454)) |
| 10-21 row 5, `add`/`link` refuse a free-text component label | 2026-10-22 | `declared-policy-not-mechanically-enforced` (IMP-1160) | **YES — IMP-1238** | **Gate ran and was mis-scoped**: it checks a label's SHAPE; the property is that some environment DECLARES it. Generalised by rows 14–15. IMP-1238 is itself the gate-cannot-fail record, so no duplicate is logged |

**Changes whose class recurred after a *prose* fix:** `finding-premise-fails-re-measurement` (step 6 already says "re-measure premises"; IMP-1206 and IMP-1239 are this agent's own). Row 13 tightens it; no mechanical home exists for "was this measured", and that is said in its Residual.
**Changes whose class recurred after a *gate*:** row 5 of 2026-10-21, above.

---

## 2. Clusters and promotion decisions

```
CLUSTER: retirement-or-rename-leaves-consumers  (x2: IMP-1212, IMP-1236)
Altitude:   CLASS — one property: removing or renaming a path leaves its consumers (gates, generators,
            register rows, ledger evidence) pointing at nothing; 10-22 (2)'s IMP-1227 was the third
Ladder row: an agent had the information and still did the wrong thing; every gate that caught it
            fired only AFTER the removal
Becomes:    row 12(a): development-agent runs `git grep -n <folder>` and the unscoped work-items check
            before and after a removal and reports both counts; routed ledger repair (decision 2)
Retires:    nothing
Cites:      IMP-1212, IMP-1236
Residual:   no gate compares the work-items count with the last green build; measured at 94 rises over
            76 manifests, a delta gate would cry wolf, so it is deliberately not built
```

```
CLUSTER: component-label-declared-nowhere  (x2: IMP-1238; WI-0129's undeclared label at creation)
Altitude:   CLASS — the 2026-10-21 shape check is the instance gate; the property is membership
Ladder row: a tool could catch it mechanically + second instance -> generalise
Becomes:    rows 14-15: add/link refuse a label no environment of the pipeline config declares
Retires:    nothing — the shape check stays as the first rung, for when no config is readable
Cites:      IMP-1238
Residual:   write path only. 53 of the 55 undeclared labels on today's ledger were declared when
            written (the rename removed them); those are the ledger repair, not this check
```

```
CLUSTER: relayed-word-acted-on-without-its-source  (x3: IMP-1221, IMP-1216, IMP-1233)
Altitude:   CLASS — a reviewer statement passed through a relay was acted on without re-reading what
            it answered (the approved proposal) or running the one query that settles it (the team)
Ladder row: an agent had the information and still did the wrong thing
Becomes:    row 10 (lead-agent: quote + name the proposal answered) and row 7 (skill: an existence
            or identity claim is settled by its read-only query, whoever stated it)
Retires:    nothing
Cites:      IMP-1221, IMP-1216, IMP-1233
Residual:   prose; nothing reads a dispatch brief. A relay that quotes and still misreads is not
            prevented, only made checkable
```

```
CLUSTER: design-trade-off-resolved-unasked  (x5: IMP-1228, IMP-1234, IMP-1230, IMP-1213, IMP-1214)
Altitude:   CLASS for the architect three; the two plan-agent entries stay notes
Ladder row: an agent had the information and still did the wrong thing
Becomes:    row 11: architect-agent items 6 and 7 (people per occurrence; a delete guard in the
            owner's own final status; an ADR overlapping a diagram-only flow re-reads its steps)
Retires:    nothing
Cites:      IMP-1228, IMP-1234, IMP-1230, IMP-1213, IMP-1214
Residual:   IMP-1213 (default from the cited artefact) and IMP-1214 (a batch action inherits the
            single action's rules) are single plan-agent instances, both caught at the gate; lessons
            carried by the digest
```

```
CLUSTER: knowledge-stale-against-approved-design  (x4: IMP-1211, IMP-1215, IMP-1217, IMP-1218)
Altitude:   INSTANCE edits of the files only improvement-agent may change
Ladder row: one instance, general cause, a human needs to know it -> knowledge line
Becomes:    rows 1, 2, 3 (knowledge) and row 8 (compliance-checklist: the upstream intake source is a
            store)
Retires:    nothing
Cites:      IMP-1211, IMP-1215, IMP-1217, IMP-1218, IMP-1221
Residual:   no gate compares knowledge prose with SDD/TAD; each corrected line now names the SDD/TAD
            section that governs it, so the next reader is pointed at the source
```

```
CLUSTER: platform-fact-measured-live  (x6: IMP-1219, IMP-1220, IMP-1222, IMP-1231, IMP-1232, IMP-1225)
Altitude:   INSTANCE facts, recorded where they are read
Ladder row: one instance, general cause -> knowledge line (row 7 for the identity rule, a skill)
Becomes:    rows 4, 5, 6, 7
Retires:    nothing
Cites:      IMP-1219, IMP-1220, IMP-1222, IMP-1231, IMP-1232, IMP-1225
Residual:   IMP-1220's cause (pac re-escaping quotes) is inferred, and the line says so
```

```
CLUSTER: own-claim-not-measured  (x2: IMP-1206, IMP-1239)
Altitude:   CLASS — finding-premise-fails-re-measurement, now x9
Ladder row: an agent had the information and still did the wrong thing (this agent)
Becomes:    row 13: step 6 — a corpus cell for an unwritten check comes from a scratch run; a planned
            closure dumps the entry first; a stated cause of a residual count is classified line by line
Retires:    nothing
Cites:      IMP-1206, IMP-1239
Residual:   prose recurring after prose. No gate can tell a measured cell from a reasoned one; this
            review applied the rule to itself (the scratch selftests and the 94-rise measurement)
```

```
CLUSTER: shared-working-tree-between-sessions  (x2: IMP-1207, IMP-1224)
Altitude:   INSTANCE — IMP-1207 is covered by lead-agent rung 5; IMP-1224 is a new reading rule
Ladder row: one instance, general cause -> skill line
Becomes:    row 9: a gate whose inputs another session is drafting is reported against HEAD too
Retires:    nothing
Cites:      IMP-1207, IMP-1224
Residual:   no gate tells an applied file from a drafted one; this makes the provisional result visible
```

```
CLUSTER: build-and-test-hygiene  (x2: IMP-1237, IMP-1235)
Altitude:   INSTANCE — IMP-1237 is untriaged-tool-warning (x26) in its new-feature form
Ladder row: an agent had the information and still did the wrong thing
Becomes:    row 12(b): development-agent copies every warnings_detail entry of the last SUCCESS
            manifest whose triaged_in names another document; IMP-1235 routed to development-agent
Retires:    nothing
Cites:      IMP-1237, IMP-1235
Residual:   the mechanical form is held by IMP-0500 / IMP-1006's design (37 of 261 as first built);
            warnings_detail.triaged_in is a value, so a later gate can use it
```

```
CLUSTER: notes-no-rule-change  (x5: IMP-1208, IMP-1209, IMP-1210, IMP-1223, IMP-1229)
Altitude:   NOTE — each was caught by the defence that exists, or is already discharged
Ladder row: one instance -> nothing; the digest carries the lesson
Becomes:    nothing
Retires:    nothing
Cites:      IMP-1208, IMP-1209, IMP-1210, IMP-1223, IMP-1229
Residual:   IMP-1208 is the third tier-tag miss (IMP-0398, IMP-1112); each time the subagent's own
            check stopped it within one dispatch, which is the defence working
```

```
CLUSTER: deferred-entries-reobserved-by-this-deploy  (x3: IMP-1165, IMP-1181, IMP-1178)
Altitude:   NOTE — closures, not changes
Ladder row: a fixed-in-flight/deferred entry closes when the deploy re-observes it at its level
Becomes:    CLOSE with reobserved V3 (pipeline-agent, 2026-10-22 18:01-18:02)
Retires:    nothing
Cites:      IMP-1165, IMP-1181, IMP-1178
Residual:   IMP-1178's line says "(read-only, scratch dir)". The command carries no --workflows-dir, so
            the default directory was read; the scratch directory is the script's own temp folder
```

**Premises re-measured at draft time.** IMP-1236's 326 classified one line at a time (above). IMP-1235's "fails 45 of 45 alone" re-run: 25 of 45. IMP-1238's precedent: on today's ledger 55 events carry a label the current config does not declare; against HEAD's config only 2 do (WI-0129, WI-0146). IMP-1215: the gate docstring and the build-config comment were already rewritten by development-agent (G1), so row 2 is the knowledge half only. IMP-1216: the portal TAD's §6.1 sentence ("DEV: the team the first app is shared with") is right after all, given IMP-1233's live read, so nothing is routed to architect-agent. IMP-1219's routing half is done: A-NS-45 (c) was accepted as risk A-R109. IMP-1209: the clause was restored and the export refreshed (narrative-scrubbing dev summary L2596). IMP-1217 and IMP-1215 waited on approvals: rev 33 and portal Revision 4 are both approved.

**Reviewer-deferred entries checked against this deploy.** 33 name a portal, a push or an import in their return condition. 3 are met (above). The rest need a signed-in human opening the app or a designer (V4/V5), or a build, and this deploy recorded nothing V4. The three fixed-in-flight blockers (IMP-1095, IMP-1098, IMP-1156) wait on a designer save of the scrub flow and are not in scope.

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | knowledge | [overview.md L105](knowledge/domain/overview.md#L105), [compliance-requirements.md L17](knowledge/domain/compliance-requirements.md#L17) | Non-negotiable 1 and CR-01 restated as the §7.1a rule (§C.1) | IMP-1211 | N/A — prose | N/A |
| 2 | knowledge | [dataverse.md L240](knowledge/technology/dataverse.md#L240) | Point 1 stated as the property, with `REV_TrusteeFinancialEligibility` as the named exception (§C.2) | IMP-1215 | N/A | N/A |
| 3 | knowledge | [business-rules.md L91](knowledge/domain/business-rules.md#L91), [regulations.md L29](knowledge/domain/regulations.md#L29), [compliance-requirements.md L25](knowledge/domain/compliance-requirements.md#L25) | Locate vs delete; QuickBooks never erased by the solution; SAR = helper mode 3 (§C.3) | IMP-1217, IMP-1221 | N/A | N/A |
| 4 | knowledge | [dataverse.md](knowledge/technology/dataverse.md#L507), new last section | A new field security profile cannot be packed until it has a live id (§C.4) | IMP-1222 | N/A | N/A |
| 5 | knowledge | [testing-tools.md](knowledge/technology/testing-tools.md#L157), new last section | FetchXML quoting; typed QueryExpression values; the callback-suppression header (§C.5) | IMP-1220, IMP-1231, IMP-1232 | N/A | N/A |
| 6 | knowledge | [code-apps.md L762](knowledge/technology/code-apps.md#L762) | The portal has no axe dependency; assert roles and names (§C.6) | IMP-1225 | N/A | N/A |
| 7 | skill | [how-to-verify-a-platform-contract.md L327](skills/how-to-verify-a-platform-contract.md#L327) | Shape 3: an identity-type or existence claim is settled by its read-only query, whoever made it (§C.7) | IMP-1219, IMP-1216, IMP-1233 | N/A | N/A |
| 8 | skill | [compliance-checklist.md L21](skills/compliance-checklist.md#L21) | The store inventory includes the upstream intake source (§C.8) | IMP-1218 | N/A | N/A |
| 9 | skill | [how-to-apply-constraints.md L36](skills/how-to-apply-constraints.md#L36) | A gate whose inputs another session is drafting is reported against HEAD too (§C.9) | IMP-1224, IMP-1207 | N/A | N/A |
| 10 | agent | [lead-agent.md L335](agents/lead-agent.md#L335) | Relay an approval with the words AND the proposal it answers (§C.10) | IMP-1221 | N/A | N/A |
| 11 | agent | [architect-agent.md L202](agents/architect-agent.md#L202) | Items 6–7 (§C.11) | IMP-1228, IMP-1234, IMP-1230 | N/A | N/A |
| 12 | agent | [development-agent.md L337](agents/development-agent.md#L337) | Two subsections: before a removal; carry the build's standing warnings (§C.12) | IMP-1212, IMP-1236, IMP-1237 | N/A | N/A |
| 13 | agent | [improvement-agent.md L169](agents/improvement-agent.md#L169) | Step 6: scratch-run corpus cells, dump before closing, classify a residual count's cause (§C.13) | IMP-1206, IMP-1239 | N/A | N/A |
| 14 | script | [.engine/scripts/lib/work_items.py L167](.engine/scripts/lib/work_items.py#L167), engine only | `undeclared_component_labels()` (§A) | IMP-1238 | YES — `python3 scripts/work-items.py --selftest`; corpus: 55 of 163 component-carrying events undeclared today, 2 against HEAD's config | already wired (`work-items` selftest and SOFT step, [build config L182](config/revitalise-grant-automation-build.yml#L182)) |
| 15 | script | [.engine/scripts/work-items.py L104](.engine/scripts/work-items.py#L104), engine only | refuse at `add`/`link`; 2 selftest cases, one failing on today's library (§B) | IMP-1238 | YES — the same selftest: scratch 0 FAIL; unpatched library `got (0, False), want (1, True)` | already wired |

**Constraint budget:** 0 of 3 used. `scripts/work-items.py` and `scripts/verify-work-items.py` are 46- and 47-line wrappers and `scripts/lib/` holds no `work_items.py`, so rows 14–15 have no instance copy.

**Engine altitude (skill §6).** Rows 7–15 land in `.engine`. Their text names no client table, person or environment except where a row cites this client's own finding id; rows 10–13 cite finding ids only. Row 2's profile name and row 3's QuickBooks/Finance facts are client facts and stay in this instance's `knowledge/`.

**Dispositions, decided now from `observable_at`:**

| Entry | `observable_at` | Disposition |
|---|---|---|
| IMP-1206, 1211, 1212, 1213, 1214, 1215, 1216, 1217, 1218, 1219, 1220, 1221, 1224, 1225, 1228, 1230, 1233, 1234, 1239 | n/a or V1 | **CLOSE** on apply, `evidence_grep` on the row's text |
| IMP-1207, 1208, 1209, 1210, 1223, 1229 | n/a or V1 | **CLOSE** as a note, `evidence_grep` on this document's applied record |
| IMP-1222 | V2 | **CLOSE** with `reobserved` V2: build-agent's pack of `-3` at 17:48 succeeded once the id existed ([build.log L194](logs/build.log#L194)) |
| IMP-1237 | V2 | **CLOSE** with `reobserved` V2: build `-3` C-TECH-055 PASS with the row at [dev summary L400](docs/development/trustee-portal-design-2-dev-summary.md#L400) |
| IMP-1165, 1181, 1178 | V3 | **CLOSE** with `reobserved` V3 (pipeline-agent, [L454](logs/pipeline.log#L454)–[L457](logs/pipeline.log#L457)) |
| IMP-1231, 1232 | V3 | **DEFER**: knowledge lands; closes when a live run of the fixed script creates the jobs (1231) / the next synthetic-write session shows an unchanged `flowrun` count (1232) |
| IMP-1235 | V2 | **DEFER**: routed; closes when `EntraScripts.Tests.ps1` passes run alone |
| IMP-1236 | V1 | **DEFER**: row 12 lands; closes when the unscoped check names no `trustee-review-portal-cards` evidence |
| IMP-1238 | V3 | **DEFER**: rows 14–15 land; closes when a deploy transition of an item linked after the fix needs no relink |

### Routed work

| To | What | Re-measured |
|---|---|---|
| pm-agent (+ lead-agent for verdicts) | Ledger repair for 55 items per decision 2: re-point 313 `-cards` evidence rows, settle the 9 whose needle is gone, defer the 8 classic-portal items as superseded, relink the 51 stale `-cards` labels | 2026-10-22 18:10, ledger at 948 events |
| development-agent | `EntraScripts.Tests.ps1`: dot-source `provisioning/common/provisioning-common.ps1` in `BeforeAll`, as `CitySettlementRegister.Tests.ps1` does | 25 of 45 fail alone, 18:12 |
| reviewer | Run `ensure-bulk-delete-jobs.ps1 -Env dev` once the fix is committed (credential-gated) | no `pipeline.log` line names it |

---

## 4. Retirements

> Retirement check performed: 10 retired constraint rows (`grep -rh '^| ~~C-' constraints/`) and the
> live rows these clusters touch (C-TECH-051, C-TECH-055, C-TECH-074) were reviewed. None is made
> redundant: rows 14–15 add membership above the shape check, which stays as the fallback when no
> pipeline config is readable. Nothing is retired.

---

## 5. Findings left unprocessed

**Deferred:** none

Every unread entry is in scope. The 3 fixed-in-flight blockers named in §2 are reviewer-deferred under their own return condition and were not re-derived.

---

## 6. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 1234 | 1235 (+ IMP-1239) |
| Distinct lessons | 1210 | 1211 |
| Recurring classes (x≥2) | 96 | 96 |
| Entries closed | — | 30 (25 + 2 V2 + 3 V3); 5 deferred |

Regenerated with `python3 scripts/generate-known-failure-modes.py` on apply; confirmed with `--check`.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-10-22-improvement-review-3.md

Findings processed: 35 NEW  →  11 clusters
Regression check:   6 prior changes audited, 2 classes recurred
Proposed:           0 constraints (cap 3), 2 gates/scripts, 9 skill/knowledge edits,
                    4 agent-file edits, 0 retirements
Altitude calls:     4 generalised from instance to class, 8 left as notes
Digest:             will regenerate — 1211 lessons, 96 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. On approval

Written **after** `APPROVE IMPROVEMENTS`. Apply order: (1) set the status to `APPLYING`; (2) confirm `.engine/scripts/lib/work_items.py` is still sha1 `6f9c8e79ff7f…` and `work-items.py` `9a1b1f2e56b1…`, and merge if not; (3) apply §A, §B, §C one row at a time, closing each entry as its row lands; (4) run both engine selftests, `verify-engine-instance-split.py`, the scoped and unscoped work-items checks; (5) regenerate the digest; (6) `verify-improvement-log.py --check`, `verify-derived-counts.py`, `verify-review-document.py`.

---

### Applied record — 2026-10-22

**Approval:** *"Approve Improvements"* followed by *"Option A please."*, typed by Xander Lykopoulos after lead-agent showed him this draft, relayed verbatim (logs/routing.log, 2026-10-22 20:50). "Option A" answers decision 2: pm-agent re-points the 55 items with `reopen --retrace`, lead-agent re-cites the existing DEV verdicts, and the 8 classic-portal items are deferred as superseded. Lead-agent routes that work; this apply did not dispatch it.

**Re-verified before applying (20:51):** the Status line still read DRAFT; both engine files still had sha1 `6f9c8e79ff7f…` and `9a1b1f2e56b1…`; no `corrects` warning named any entry here. One entry arrived after the draft, IMP-1240 (build-agent, shared-config last-green glob). It is outside this approval and stays unread for the next batch. The ledger was unchanged (948 events), so every routed row still stands. Nothing was withheld or narrowed.

| # | Change | Applied at | Status | Entries moved |
|---|---|---|---|---|
| 1 | §C.1 overview.md item 1, CR-01 lead | working tree 2026-10-22 20:53 | APPLIED 2026-10-22 | IMP-1211 |
| 2 | §C.2 dataverse.md point 1 | working tree | APPLIED 2026-10-22 | IMP-1215 |
| 3 | §C.3 BR-D04, regulations Art. 15/17, CR-09, SAR row | working tree | APPLIED 2026-10-22 | IMP-1217, IMP-1221 (also row 10) |
| 4 | §C.4 dataverse.md new section | working tree | APPLIED 2026-10-22 | IMP-1222 (reobserved V2) |
| 5 | §C.5 testing-tools.md new section | working tree | APPLIED 2026-10-22 | IMP-1220; IMP-1231, IMP-1232 deferred |
| 6 | §C.6 code-apps.md bullet | working tree | APPLIED 2026-10-22 | IMP-1225 |
| 7 | §C.7 verify-a-platform-contract shape 3 | `.engine` working tree, **not committed** | APPLIED 2026-10-22 | IMP-1216, IMP-1219, IMP-1233 |
| 8 | §C.8 compliance-checklist line | `.engine`, not committed | APPLIED 2026-10-22 | IMP-1218 |
| 9 | §C.9 apply-constraints paragraph | `.engine`, not committed | APPLIED 2026-10-22 | IMP-1224 |
| 10 | §C.10 lead-agent relay rule | `.engine`, not committed | APPLIED 2026-10-22 | IMP-1221 |
| 11 | §C.11 architect-agent items 6–7 | `.engine`, not committed | APPLIED 2026-10-22 | IMP-1228, IMP-1230, IMP-1234 |
| 12 | §C.12 development-agent two subsections | `.engine`, not committed | APPLIED 2026-10-22 | IMP-1212, IMP-1237 (reobserved V2); IMP-1236 deferred |
| 13 | §C.13 improvement-agent step 6 bullets | `.engine`, not committed | APPLIED 2026-10-22 | IMP-1206, IMP-1239 |
| 14 | §A `lib/work_items.py`, byte-identical to the scratch copy measured at draft | `.engine`, not committed | — | IMP-1238 deferred (V3) |
| 15 | §B `work-items.py` | `.engine`, not committed | — | — |

Closed as notes (no rule change): APPLIED 2026-10-22 | IMP-1207 · APPLIED 2026-10-22 | IMP-1208 · APPLIED 2026-10-22 | IMP-1209 · APPLIED 2026-10-22 | IMP-1210 · APPLIED 2026-10-22 | IMP-1213 · APPLIED 2026-10-22 | IMP-1214 · APPLIED 2026-10-22 | IMP-1223 · APPLIED 2026-10-22 | IMP-1229

Closed on this deploy's re-observation (V3, pipeline-agent 18:01–18:02): IMP-1165, IMP-1181, IMP-1178.

Deferred with a recorded reason: IMP-1231, IMP-1232, IMP-1235, IMP-1236, IMP-1238. No entry rejected. IMP-1240 carries `excluded_by` naming this document; it waits for the next batch.

**Two registered counts corrected because this apply drifted them:** the digest line count in `generate-known-failure-modes.py` (638 → 640, both copies), and the `verify-*.py` count in `agents/improvement-agent.md` (71 → 70, after the other session deleted `verify-code-app-variant-parity.py`). The one remaining drift, the bundle size in the grant-automation dev summary (1205 → 858 kB), belongs to development-agent and is not changed here.

**Checks after applying:**

| Check | Exit | Result |
|---|---|---|
| `python3 scripts/work-items.py --selftest` | 0 | 0 FAIL lines, both IMP-1238 cases OK |
| `python3 scripts/verify-work-items.py --selftest` | 0 | |
| `verify-work-items.py --check --scope WI-0146,WI-0147,WI-0148 --at-least built` | 0 | 0 failures |
| `verify-work-items.py --check` (unscoped, warn-only) | 1 | 326, unchanged: the fix is write-path only, and the repair is routed (Option A) |
| `verify-engine-instance-split.py` | 0 | |
| `verify-improvement-log.py --check` | 0 | 0 awaiting-approval, 0 blockers open; 1 unread (IMP-1240, out of scope) |
| `generate-known-failure-modes.py --check` | 0 | current, 1236 entries, 1212 lessons |
| `verify-derived-counts.py` (SOFT) | WARN | 1 drift, not from this review (above) |
| `verify-review-document.py --only` this document | 0 | |

## §A — `.engine/scripts/lib/work_items.py` (proposed)

Applied to a scratch copy and run; the diff below is that copy against today's file.

```diff
--- a/scripts/lib/work_items.py
+++ b/scripts/lib/work_items.py
@@ -167,6 +167,26 @@
 def component_label_problems(labels: list[str]) -> list[str]:
     """Labels that are not `deploy`, `operation:<x>` or `script:<x>`."""
     return [c for c in labels if not COMPONENT_LABEL_RE.match(c)]
+
+
+def undeclared_component_labels(labels: list[str], ctx: "Context") -> tuple[list[str], list[str], str]:
+    """(labels no environment of the pipeline config declares, the declared set, the config path).
+
+    `add` and `link` call this AFTER component_label_problems(): a label can have the right SHAPE
+    and still be one no deploy could ever discharge, because no environment declares it
+    (`script:ensure-schema.ps1` is an environment_prerequisites entry, which carries no label).
+    Until 2026-10-22 that was found only at `deployed:<env>`, a stage later and in another agent
+    (IMP-1238). Write path only: a label the config stopped declaring AFTER the event was written
+    is a fact about the config now, and owed_components() reports it at the transition. An absent
+    or unreadable config returns nothing here, for the same reason."""
+    config, where = ctx.pipeline()
+    if config is None or not labels:
+        return [], [], where
+    try:
+        known = dm.all_labels(config)
+    except dm.ConfigError:
+        return [], [], where
+    return sorted(c for c in labels if c not in known), sorted(known), where
 
 
 def _dated(ev: dict) -> bool:
```

## §B — `.engine/scripts/work-items.py` (proposed)

```diff
--- a/scripts/work-items.py
+++ b/scripts/work-items.py
@@ -106,6 +106,13 @@
             print(f"work-items: REFUSED [components] {bad} — a component label is `deploy`, "
                   f"`operation:<x>` or `script:<x>` (IMP-1160)", file=sys.stderr)
             return 1
+        undeclared, known, where = wi.undeclared_component_labels(
+            _csv(getattr(args, "components", None)), ctx)
+        if undeclared:
+            print(f"work-items: REFUSED [components] {undeclared} are declared by no environment in "
+                  f"{where}, so no deploy could discharge them; declared labels: {known} (IMP-1238)",
+                  file=sys.stderr)
+            return 1
 
     def build(items, allocate):
         if args.cmd == "add":
@@ -355,6 +362,14 @@
                                    "--by", "pm-agent")
         check("free-text component label refused at link (IMP-1160)",
               (rc_free, "REFUSED [components]" in err_free), (1, True))
+        rc_und, _, err_und = run(root, "link", "WI-0001", "--components", "script:not-declared.ps1",
+                                 "--by", "pm-agent")
+        check("well-formed but undeclared component label refused at link (IMP-1238)",
+              (rc_und, "declared by no environment" in err_und), (1, True))
+        check("only the undeclared label is named (IMP-1238)",
+              wi.undeclared_component_labels(["deploy", "operation:code-app-push",
+                                              "script:not-declared.ps1"], wi.load_context(root))[0],
+              ["script:not-declared.ps1"])
         check("the three label forms pass the vocabulary",
               wi.component_label_problems(["deploy", "operation:x", "script:y.ps1", "REV | Portal | Flow"]),
               ["REV | Portal | Flow"])
```

## §C — text changes (proposed)

**C.1 — `knowledge/domain/overview.md` L105–106**, replace item 1 with:

> 1. **Identity and raw free text never reach a trustee.** Column security hides identity, and the
>    narrative is redacted before trustee review. Categorical Art. 9 answers (condition profiles,
>    exceptional circumstance, the Equality Act answers, and since SDD Amendment A-14 benefit and
>    employment status) are trustee-visible by design, each released only under NFR-031 with its
>    necessity recorded (SDD §7.1a, §7.1b). The SDD, not this line, holds the current set (`IMP-1211`).

`knowledge/domain/compliance-requirements.md` L17, CR-01's bold lead becomes **Identity and raw free text never reach a trustee; a categorical Art. 9 answer reaches one only under NFR-031 (SDD §7.1a).** The rest of the row is unchanged.

**C.2 — `knowledge/technology/dataverse.md` L240–242**, replace point 1 with:

> 1. `CanUpdate` governs only `IsSecured=1` columns, and releasing a secured column to a trustee
>    requires the trustee team **inside a field security profile**. The property
>    `no-trustee-in-column-security-profile` protects is *no trustee team in a profile that releases
>    identity or grants write* (`ADR-002`). Since portal TAD trustee-portal-design-2 Revision 4
>    (`ADR-084`, `ADR-085`, SDD A-14) one profile is the named exception, `REV_TrusteeFinancialEligibility`:
>    read only, three columns, and the gate REQUIRES every trustee team to be its member (`IMP-1215`).

**C.3 — erasure and SAR.**
`business-rules.md` L91, BR-D04 becomes: *Erasure **locates** data across Applicant, Application, Review, Grant, Payment, the signed-PDF library, DocuSign and QuickBooks — **including** referees, helpers, group members and emergency contacts. It **deletes** from Dataverse, the signed-PDF library and DocuSign only. **QuickBooks is never erased by this solution**: the connection is read only (`ADR-017`), the record is kept under the finance policy, and Finance deletes it after six years outside this solution (TAD `ADR-088`); the requester is told (`IMP-1217`).*
`regulations.md` L29–31 (Art. 15): the ⚠️ sentence becomes *Designed in TAD rev 33 (`ADR-088`): helper mode 3, started by the process owner, produces one extract covering every store, payments, bank details and QuickBooks included. Not built yet (CO-011, `wbs:0.13`). ⚠️ No response-time SLA is recorded anywhere (SDD OQ-023).*
`regulations.md` L32–33 (Art. 17): *…across the Dataverse tables, the signed-PDF library and DocuSign envelopes. QuickBooks is located and disclosed, never erased by this solution; Finance deletes the record after six years (`ADR-088`).*
`compliance-requirements.md` L25, CR-09's lead becomes **Erasure reaches every copy it may delete** — Dataverse, signed-PDF library, DocuSign; QuickBooks is located and reported, and Finance deletes it after six years outside this solution (`ADR-088`). L51's row becomes *| **SAR extract designed, not built** (FR-053) | TAD rev 33 `ADR-088`, helper mode 3; CO-011 (`wbs:0.13`) | Until built, an Article 15 request is answered by hand. Statutory default is one month and **no internal SLA exists**, so test-agent has no threshold to test |*. IMP-1217's "manual SAR procedure" wording is superseded by IMP-1221 and is not used.

**C.4 — `knowledge/technology/dataverse.md`, new last section:**

> ## A New Field Security Profile Cannot Be Packed Until the Platform Has Given It an Id
>
> *Recorded 2026-10-22 (`IMP-1222`), measured with a local `pac solution pack`.*
>
> `pac solution pack` fails with *"RootComponent validation failed"* when
> `Other/FieldSecurityProfiles.xml` declares a `<FieldSecurityProfile>` with no
> `fieldsecurityprofileid`: the packer keys the profile's root component by that id, and
> `C-TECH-051` forbids inventing one. So for a NEW profile the order is fixed — create it live
> (`ensure-schema.ps1 -Env dev`), read the id back, write it into source, then build. **No build
> can run between authoring the element and the read-back**; plan the live step as the first
> build prerequisite, not as an import prerequisite.

**C.5 — `knowledge/technology/testing-tools.md`, new last section:**

> ## Querying and writing a live DEV from a test session
>
> *Recorded 2026-10-22 (`IMP-1220`, `IMP-1231`, `IMP-1232`), each measured against DEV.*
>
> - **`pac env fetch --xml` takes single-quoted attributes.** With double quotes pac 2.4.1 on macOS
>   failed every query with *XmlException "'\' is an unexpected token"*; single quotes ran. The
>   cause (the shim re-escaping quotes) is inferred, not proven; `--xmlFile` avoids it.
>   `olderthan-x-days` refuses 0.
> - **A hand-built Web API `QueryExpression` types every condition value.** `BulkDelete` dropped bare
>   JSON numbers (*"requires 1 value/s, not 0"*) and accepted
>   `{"@odata.type": "Microsoft.Dynamics.CRM.Object", "Type": "System.Int32", "Value": "30"}`.
>   `bulkdeleteoperation` has no `recurrencepattern` (0x80060888); read it through
>   `$expand=asyncoperationid`. A fake that accepts any body pinned both defects for two months:
>   send a hand-built body to a live org once before trusting the fake.
> - **Synthetic rows fire live flows unless the callback header is sent.**
>   `MSCRM.BypassBusinessLogicExecution: CustomSync,CustomAsync` did not stop Dataverse-connector
>   triggers; `MSCRM.SuppressCallbackRegistrationExpanderJob: true` on every create, update and
>   delete did. Mark each synthetic row by name, count `flowrun` rows before and after, and delete
>   by the marker.

**C.6 — `knowledge/technology/code-apps.md` L762, `## Testing`**, add a bullet: *- **Accessibility**: the trustee portal has no axe dependency (no axe-core, jest-axe or vitest-axe in `package.json`). A test contract asserts roles, accessible names and visible text directly; adding axe-core is a lockfile change under `C-TECH-074` and needs a reviewer decision (`IMP-1225`).*

**C.7 — `skills/how-to-verify-a-platform-contract.md`, after shape 2 (L352):**

> **3. A claim about what EXISTS or WHO an identity is gets its one read-only query, whoever made the
> claim.** "There is no such team in this environment" and "these rows belong to a non-interactive
> identity" are settled by one fetch each: the team table with its roles, and the owning user's
> `accessmode` and `applicationid`. A statement relayed from the reviewer is still a statement, not
> a measurement. Run the query before a design or a test depends on it, and record the result
> (`IMP-1216`, `IMP-1233`, `IMP-1219`).

**C.8 — `skills/compliance-checklist.md` §1.1, after the retention line (L26):**

> - [ ] The store inventory behind retention, erasure and access requests covers both directions:
>   every copy made FROM the system of record, and the upstream source it was copied from (a web
>   form's own entries are a store), each with its retention owner (`IMP-1218`)

**C.9 — `skills/how-to-apply-constraints.md` Step 3, after item 3 (L42):**

> **When another session is drafting files a gate reads, report the gate twice.** A draft behind a
> gate keyword is indistinguishable on disk from an applied change. Measure against the working
> tree and against `HEAD` (`git show HEAD:<file>` into your scratch directory, never `git stash`),
> and mark the working-tree result provisional (`IMP-1224`).

**C.10 — `agents/lead-agent.md`, after L335:**

> **An approval of a proposal is relayed with the proposal named beside the words** — the document,
> section and item the reviewer was shown — and never restated as a mechanism. "Manual" in a reply
> about a flow mode names the trigger unless the reviewer says there is no flow. The receiving agent
> re-reads the named proposal before authoring from it (`IMP-1221`).

**C.11 — `agents/architect-agent.md`, after item 5 (L224):**

> 6. **State how many people a manual path needs per occurrence.** Where a protected property forces
>    more than one, offer the single-handler option and its residual risk as a lettered gate
>    decision; do not resolve it in favour of the split. And a guard on a destructive action is
>    written in the status the process owner already treats as final, with any intermediate-state
>    trigger offered only as an alternative (`IMP-1228`, `IMP-1234`).
> 7. **An ADR that adds a job, column or rule on a table that an unbuilt, diagram-only flow also
>    touches lists that flow's steps as kept, moved or impossible**, in the same revision (`IMP-1230`).

**C.12 — `agents/development-agent.md`, before `## Constraints to Check` (L337):**

> ### Before you remove or rename a folder, count its consumers
>
> Run `git grep -n <folder>` (the ledger, `logs/work-items.jsonl`, included) and
> `python3 scripts/verify-work-items.py --check` before and after, and report both failure counts in
> the Dev Summary. A rise is evidence and labels you have orphaned; re-point or defer them through
> pm-agent in the same change. The build gates that catch a dangling consumer fire only after the
> removal, and the ledger's is warn-only (`IMP-1212`, `IMP-1236`: 1 → 326).
>
> ### Carry the build's standing warnings into a new feature's Dev Summary
>
> At handoff, read the last SUCCESS manifest of the same build config. For each `warnings_detail`
> entry whose `triaged_in` names another document, add a citing row to this feature's
> tool-warnings table (`C-TECH-055`). Steps that need a network or a credential, such as `lint`,
> are the ones you cannot reproduce locally, so their warnings exist only there (`IMP-1237`).

**C.13 — `agents/improvement-agent.md` step 6, after the third premise bullet (L191):**

> - **A corpus cell for a check not yet written comes from a scratch implementation run at draft
>   time**, never from reasoning about the corpus; a planned closure dumps the entry's existing
>   closure fields first; a status-word test strips `~~…~~` before reading the word (`IMP-1206`).
> - **A stated cause of a residual failure count is classified line by line, and the count is set
>   beside the last green build's `soft_gates` figure.** "Older drift" is a cause and needs the same
>   measurement as any other (`IMP-1239`: 326 called drift, 326 of 326 from that day's rename).
