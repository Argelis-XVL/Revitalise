# Improvement Review — 2026-09-26 (4)

**Agent:** improvement-agent (tier `strategic`)
**Mode:** capability mode, Group 1 only: WS-S (blocker lanes), WS-T (fixed-in-flight discharge), WS-Y (hand-typed batch threshold)
**Authorising artefact:** [`docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md`](docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L87). The reviewer's settled rows S-1 to S-5 are taken as given
**Findings processed:** 2 NEW → 2 clusters (both logged by this review; 14 unread entries outside the capability scope are named in section 5)
**Trigger:** reviewer request (capability mode)
**Gate:** `APPROVE IMPROVEMENTS`. Not sent with this dispatch, by design
**Status:** ~~DRAFT~~ **APPLIED 2026-09-26 in the working tree, NOT committed** (reviewer: one commit after the whole plan). The authorisation record, the changes and the executed results are in section 8
**WBS:** `wbs:n/a`. System work on the rules, outside the contracted WBS, not billable (`C-COM-002`)

---

## Summary

Group 1 is buildable, but not exactly as the design wrote it. Four of its mechanism premises fail when executed, and each has a narrow fix that keeps the design's intent. The biggest result is from replaying all 14 historical build halts caused by the finding queue. The lane split (WS-S) clears only 2 of them, and none of the 3 in the design's own window. The fixed-in-flight discharge (WS-T) clears 7 to 9. So **D-1 is the change that actually unblocks deploys, and I recommend yes.**

Four decisions are waiting on you (D-1, D-3, and two new ones this review raises). Nothing has been applied.

## What this review proposes

1. **Every blocker gets a lane, derived from the artefact that is broken.** A new finding field, `defect_in`, names the broken file or `live:<env>`. The gate derives `deploy` or `governance` from it ([gate trigger code](scripts/verify-improvement-log.py#L1356)). Only an open `deploy`-lane blocker halts a build. Governance blockers become notes that wait for the next batch.

2. **A technical blocker fixed in the dispatch that found it stops halting builds.** The fixing agent stamps `fixed_in_flight` with the re-run it did. The gate checks the fix is in the deployable tree and lets the build proceed. The finding itself still closes only at a review, and a live defect (V3 or V4) still needs someone to re-observe it after the deploy. This is what removes the "build blocked by the finding describing the fix it carries" loop ([pipeline-agent's current remedy](agents/pipeline-agent.md#L112)).

3. **The three corrections the measurements force on WS-T.** Drop the "commit is an ancestor of HEAD" check: it fails in CI and on uncommitted fixes. Rank the new state above `already-fixed`, which otherwise errors first. Require the fix's evidence to sit in a deploy-path file, not in prose.

4. **An unconfigured instance fails safe.** If `instance.yaml` declares no `deploy_paths`, every blocker stays in the `deploy` lane, which is today's behaviour. The design's "empty engine default" would have put every path-tagged blocker in `governance` and stopped the gate halting on anything.

5. **Five hand-typed batch thresholds replaced with a pointer to the function that computes it.** The design named two. There are three in agent files, one (`≥10`) in the review template, and one in the gate's own docstring. The gate's comment claiming the sweep was already done is corrected ([false comment](scripts/verify-improvement-log.py#L217)).

### Elements added

| Element | Where | Purpose |
|---|---|---|
| `defect_in` field | finding schema | names the broken artefact, from which the lane is derived |
| `lane_override: deploy` | finding schema | raise-only; no value can lower a lane |
| `fixed_in_flight` object | finding schema | records a technical fix made in the finding's own dispatch |
| `fixed-in-flight` state | `classify()` | sixth state; does not fail the build, still counts toward the batch |
| `improvement.deploy_paths` | [`instance.yaml`](instance.yaml#L42) | this instance's list of paths that ship |

### Elements changed

| Element | Change |
|---|---|
| [C-TECH-061](constraints/technology/technology-constraints.md#L131) | blocker clause becomes lane-aware; withdrawn wording retained |
| Gate trigger semantics | unread governance blocker: note, not failure; census prints lane counts |
| Six agent files, one skill, one template | lane wording, the fixed-in-flight route, threshold pointers |

## What is still open

**The batch rung still halts builds, and the design's Group 2 relies on the opposite.** WS-U's fifth requirement says WS-I already made the batch count non-fatal at build time ([design](docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L195)). WS-I's requirement 2 was withheld on 2026-08-31 because its premise measured false ([review 8](docs/improvements/2026-08-31-improvement-review-8.md#L188)). I executed the gate over a scratch log with 72 unread non-blockers and it exited 1. Group 1 leaves the batch rung alone. It caused 1 of the 14 historical halts. The Group 2 dispatch needs this fact before it drafts.

**The design's production guard (WS-V, Group 2) covers only governance blockers.** Under the design's own WS-S wording, an awaiting-approval deploy blocker would pass the gate in every environment, production included. The new decision about awaiting-approval blockers below closes that gap in Group 1. If you choose the design's wording instead, WS-V must widen to "any open blocker" before a production deploy.

**One halt type survives everything here: a build blocked by a finding whose fix IS the build.** On 2026-09-02 an artifact with no build record was cited for a deploy, and the rebuild that fixed it was halted by the finding recording it ([build.log L70](logs/build.log#L70)). Nothing is committed before that build to stamp, so fixed-in-flight cannot apply. One instance only, so it goes on the record, not into a rule.

**Three sibling reviews are drafting against the same files.** WS-X edits `pipeline-agent.md`. WS-Z edits `build-agent.md` and `pipeline-agent.md` on other lines. A finding from the WS-W1 review asks to edit [`WORKFLOW.md` L372](agents/WORKFLOW.md#L372) after this group lands. The plan of application below applies them one at a time.

## Measurements

### Premises re-measured

| Design premise (Group 1 relevant) | Design said | Measured 2026-09-26 | Verdict |
|---|---|---|---|
| Blockers in window (from 2026-09-15) | 37 | 37 | holds |
| Lane split of those 37 | 20 deploy / 12 governance / 5 hygiene (by hand) | rule on adjudicated `defect_in`: **25 / 12**; without the observed-at clause **23 / 14**; literal rule on today's data **37 / 0** (no entry has `defect_in`) | hypothesis corrected (table below) |
| Builds halted by the queue | 3 in window | 3 in window; **14 of 67** build halts over the whole log | holds, and wider |
| Distinct blocker classes | 110 of 204 | **102** of 204 | small drift |
| Hand-typed batch threshold sites | 2 | **5** | understated |
| WS-I made the batch rung non-fatal at build time | yes | withheld 2026-08-31; rung exits 1 (executed) | **false** (Group 2 premise) |
| A fix commit can be checked as an ancestor of HEAD | implied | exit **128** in a depth-1 clone, which is what [`actions/checkout@v4`](.github/workflows/ci.yml#L300) gives the job that runs [the gate](.github/workflows/ci.yml#L448); **5 of the 8** latest builds packed from uncommitted trees (1–41 dirty paths) | **false** |
| A fixed blocker can reach a new state | implied | an unread blocker with its fix needle present fails today as `already-fixed`, exit 1 (executed) | needs precedence |
| An empty engine default is safe | implied | under the derivation rule, empty means no path is a deploy path, so the gate fails open | needs a fail-safe |

### The 14 queue halts, replayed

Classified from each FAILED/BLOCKED line of `logs/build.log` whose stated cause is the queue gate. Three lines the first pass matched were other gates (L38, L51, L104) and are excluded.

| Build log line | Blocking entries (state then) | Lane | Design as written | With this review's narrowings |
|---|---|---|---|---|
| [L47](logs/build.log#L47) | IMP-0511 awaiting, plus batch rung | deploy | still halts (batch rung) | still halts (batch rung) |
| [L54](logs/build.log#L54) | IMP-0526 awaiting | deploy | passes (awaiting becomes a note) | passes once the fix is stamped |
| [L59](logs/build.log#L59) | IMP-0535 unread | governance | passes | passes |
| [L61](logs/build.log#L61) | IMP-0536 unread, plus a missing-needle error | governance | still halts (schema error) | still halts (schema error) |
| [L70](logs/build.log#L70) | IMP-0582 unread | deploy | still halts | still halts (the fix is the build) |
| [L78](logs/build.log#L78), [L79](logs/build.log#L79) | IMP-0597 (deploy), IMP-0598 (governance), unread | mixed | passes once IMP-0597 is stamped | same |
| [L83](logs/build.log#L83), [L84](logs/build.log#L84) | IMP-0602 (deploy), IMP-0605 (governance), unread | mixed | passes once IMP-0602 is stamped; its fix was already on disk | same |
| [L96](logs/build.log#L96) | IMP-0638, IMP-0640 unread | governance | passes | passes |
| [L100](logs/build.log#L100) | IMP-0650 (deploy), IMP-0651 (governance), unread | mixed | passes once IMP-0650 is stamped | same |
| [L121](logs/build.log#L121) | IMP-0804 awaiting | deploy | passes (awaiting becomes a note) | passes once stamped |
| [L123](logs/build.log#L123) | IMP-0813 unread | deploy | passes once stamped | same |
| [L125](logs/build.log#L125) | IMP-0816 unread | deploy | passes once stamped | same |

**Totals, 14 lines:** lanes alone clear 2. The design's awaiting-approval rule clears 2 more. Fixed-in-flight clears 7 (9 under the narrowing, which moves L54 and L121 into it). 3 still halt. **In the design's window (L121, L123, L125):** lanes clear 0 and fixed-in-flight clears 2 or 3.

L123 is also a worked example of why V4 closure stays strict. A stamp there would have been wrong: the source fix was incomplete, and the designer check *after* the DEV deploy found it. That is the intended order, since a defect only visible in a live designer cannot be observed before the deploy.

### Lane census, entry by entry

Each `defect_in` below is **my reading of each entry, one at a time**: the artefact that is broken, not the file its proposed rule change would edit. The lane is then the rule applied mechanically (script kept for the apply step). "Rule" uses the design's paths and its observed-at clause.

| Entry | Observed at | Broken artefact (adjudicated `defect_in`) | Hand | Rule |
|---|---|---|---|---|
| IMP-0734 | V3 | `provisioning/deploymentSettings/dev-settings.json`, `live:dev` | deploy | deploy |
| IMP-0737 | V4 | `provisioning/dataverse/` seed data, `live:dev` | deploy | deploy |
| IMP-0738 | n/a | `CLAUDE.md`, `.gitmodules` (session bootstrap) | deploy | **governance** |
| IMP-0745 | V2 | `scripts/verify-improvement-log.py` | governance | governance |
| IMP-0757 | V2 | `.engine` publication | governance | governance |
| IMP-0763 | V2 | `provisioning/deploymentSettings/test-settings.json` | deploy | deploy |
| IMP-0767 | V1 | `docs/plans/` | governance | governance |
| IMP-0769 | V1 | `provisioning/deploymentSettings/dev-settings.json` | deploy | deploy |
| IMP-0772 | V2 | `logs/class-defences.json` | governance | governance |
| IMP-0777 | V2 | `provisioning/deploymentSettings/test-settings.json` | deploy | deploy |
| IMP-0780 | V1 | `contract/tad-deferrals.json` | governance | governance |
| IMP-0781 | V3 | `live:dev` (credential on the machine) | deploy | deploy |
| IMP-0782 | V3 | `provisioning/dataverse/ensure-schema.ps1` | deploy | deploy |
| IMP-0784 | V4 | `scripts/derive-wbs-state.py`, `contract/evidence-map.json` | governance | **deploy** (observed-at clause) |
| IMP-0787 | V4 | `agents/WORKFLOW.md` | governance | **deploy** (observed-at clause) |
| IMP-0791 | V2 | `agents/WORKFLOW.md` | governance | governance |
| IMP-0794 | V1 | `src/tests/provisioning/DeploymentSettings.Tests.ps1` | hygiene | deploy |
| IMP-0804 | V3 | `src/solutions/…/Workflows/` | deploy | deploy |
| IMP-0813 | V4 | `src/solutions/…/Workflows/`, `live:dev` | deploy | deploy |
| IMP-0814 | n/a | `agents/WORKFLOW.md` | governance | governance |
| IMP-0816 | V4 | `src/solutions/…/Workflows/` | deploy | deploy |
| IMP-0820 | V4 | `live:dev` | deploy | deploy |
| IMP-0821 | V4 | `src/solutions/…/Workflows/` | deploy | deploy |
| IMP-0824 | V4 | `src/code-apps/trustee-review-portal/` | deploy | deploy |
| IMP-0831 | V5 | `docs/architecture/postcode-lookup-architecture.md` | deploy | **governance** |
| IMP-0835 | n/a | `config/models.yml` | governance | governance |
| IMP-0838 | V1 | `constraints/domain/special-category-register.yml` | governance | governance |
| IMP-0843 | V1 | `constraints/domain/special-category-register.yml` | governance | governance |
| IMP-0845 | V1 | `provisioning/dataverse/seed-city-settlement-register.ps1` | hygiene | deploy |
| IMP-0850 | V1 | `provisioning/README.md` | hygiene | deploy |
| IMP-0852 | V1 | `src/solutions/…/Other/Solution.xml` | deploy | deploy |
| IMP-0866 | V3 | `src/solutions/…/FormXml/` | deploy | deploy |
| IMP-0871 | V1 | `src/tests/solutions/IntakeContract.Tests.ps1` | deploy | deploy |
| IMP-0874 | V2 | `src/solutions/…/FormXml/` | deploy | deploy |
| IMP-0883 | V2 | `src/code-apps/trustee-review-portal/` | deploy | deploy |
| IMP-0888 | V1 | `src/tests/provisioning/LocalAuthorityRegister.Tests.ps1` | hygiene | deploy |
| IMP-0889 | V1 | `src/tests/provisioning/LocalAuthorityRegister.Tests.ps1` | hygiene | deploy |

**What the table says.** All five "hygiene" entries land in `deploy`: each is a HARD test or provisioning file inside the deployable tree. I think that is right, and it costs little once fixed-in-flight exists. Two hand "deploy" entries land in `governance` (a session-bootstrap file and an unbuilt design document), and neither would have been helped by halting a build. The observed-at clause changes exactly two results, and both are wrong. One is a status-reporting defect: under the commercial loop's rule, a reporting failure never halts a build ([WORKFLOW](agents/WORKFLOW.md#L468)). The other is an agent-policy defect. The clause rescues nothing. A purely textual proxy (the paths each entry's `what` names) gives 29 / 8 and disagrees with the adjudication on 4 entries. That is why `defect_in` has to be written deliberately, not scraped.

## What you need to decide

These are grouped by workstream. D-1 and the new awaiting-approval decision interact: the second is only safe to take once the first is yes.

---

**D-1. Adopt the fixed-in-flight discharge for deploy-lane blockers?**

**Problem** — Most measured queue halts (7 to 9 of 14) were a build blocked by the finding describing the fix it was carrying, and the lane split does not touch them.
**Suggested fix** — Yes, with three measured corrections: no commit-ancestry check; the new state ranks above `already-fixed`; the fix's evidence must sit in a deploy-path file.
**What happens if you don't** — Group 1 clears 2 of 14 historical halts and none of the 3 in the design's window. Every technical fix still waits for your keyword before it can be built.
[design, D-1](docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L474)

---

**D-3. Which paths count as "deploy" for this instance?**

**Problem** — The design's list omits the CI workflow, which carries the DEV and TST/ACC deploy jobs ([stage-dev](.github/workflows/ci.yml#L590), [promote-tst-acc](.github/workflows/ci.yml#L717)). An invalid workflow file once stopped every CI job for a day.
**Suggested fix** — `src/`, `provisioning/`, `config/*-build.yml`, `config/*-pipeline.yml`, `build/`, `.github/workflows/`. Drop the redundant `provisioning/deploymentSettings/` entry, keep `contract/` and `scripts/` out, and make an absent list mean "lanes off, every blocker deploy".
**What happens if you don't** — A broken deploy workflow is filed as governance and never halts a build. And an instance that forgets the key silently stops halting on any tagged blocker.
[design, D-3](docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L482)

---

**D-9 (new). Drop the "observed at V3/V4 means deploy" clause from the lane rule?**

**Problem** — Over the 37 blockers, the clause changed two results, both wrongly (a status-report defect and an agent-policy defect), and rescued none.
**Suggested fix** — Derive the lane from `defect_in` alone. When a governance-lane blocker was observed live, print a note asking the reader to confirm the broken artefact is not deployable.
**What happens if you don't** — Governance findings a human happened to notice on a live screen keep halting builds, which is the complaint this design answers. The design's selftest case (d) stays as written.
[design, WS-S requirement 2](docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L101)

---

**D-10 (new). Should an awaiting-approval deploy blocker keep failing until it is fixed in flight?**

**Problem** — The design lets every awaiting-approval blocker pass. For a deploy-lane one, that means a known, unfixed technical defect ships, in any environment, because its production guard checks only governance blockers.
**Suggested fix** — Governance blockers in any state become notes. A deploy-lane blocker in awaiting-approval still fails unless it carries a valid `fixed_in_flight`, so the fix, not the keyword, clears it.
**What happens if you don't** — The design's wording applies. Then the Group 2 production guard must widen to "any open blocker", or an unfixed technical defect can reach production behind a parked review.
[design, WS-S requirement 4](docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L110)

---

## 1. Regression check — did the last review's changes work?

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| Skill paragraph on sweeping the changed segment of a corrected value (review 2026-09-25 (2)) | 2026-09-25 | `test-asserts-the-defect` | no new instance since it landed | too early to call; leave alone |
| pipeline-agent "Before you dispatch ANOTHER agent to fix what a finding describes" (engine commit 10:02) | 2026-09-22 | `build-blocked-by-the-finding-it-remediates` | **yes, once**: [build.log L125](logs/build.log#L125) at 13:41 the same day. None in the 16 builds since (8 failed on other gates) | **detects, cannot prevent.** The rule worked as written (the queue was checked before the build started), but its remedy is to wait for the keyword, and that wait IS the block. A prose rule cannot remove the class. WS-T is the mechanical change that does |
| Adaptive batch threshold; prose sites to point at `batch_threshold()` | 2026-09-11 | `hand-maintained-count-drifts-from-source` | **yes**: three agent sites never changed, plus the template and the docstring | **wrong closure evidence.** The needle proved the new function exists. A presence needle can never prove an old figure was removed |
| WORKFLOW rule that an agent must not write its own `deferred_reason` | 2026-09-11 | self-granted deferral | not measurable: no field records who wrote a `deferred_reason` | leave; WS-T narrows its scope to deferrals |

**Changes whose class recurred after a prose fix:** two. The pipeline-agent dispatch rule is escalated to a mechanism by WS-T in this review. The threshold sweep cannot be escalated to a gate. `evidence_grep` asserts presence only, and a phrase-matching gate over prose has measured 48–100% false five times. The lesson goes to the digest through the new finding in cluster WS-Y, and WS-Y's closure evidence is the pasted sweep output.
**Changes whose class recurred after a gate:** none.

---

## 2. Clusters and promotion decisions

```
CLUSTER: WS-S — derive a lane for every blocker  (x0 new findings; authorised by the design)
Altitude:   ENGINE mechanism, INSTANCE data. The lane rule and the fail-safe default live in the
            gate (both copies); the path list lives in instance.yaml.
Ladder row: "a tool could catch it mechanically" — the lane is a value derived by the gate, never typed
Becomes:    scripts/verify-improvement-log.py: `defect_in` + `lane_override` schema, derive_lane(),
            unread governance blocker → NOTE, lane census line. instance.yaml improvement.deploy_paths.
            C-TECH-061 amended. WORKFLOW / lead-agent / build-agent / improvement-agent lane wording.
Retires:    nothing — C-TECH-061 is amended, not superseded
Cites:      design WS-S requirements 1–6
Residual:   the lane is only as good as `defect_in`, which the finding's author writes. A mis-tagged
            deploy defect is filed as governance; the backstops are the post-deploy batch and the
            production guard (both Group 2). Entries before the cutover carry no `defect_in` and stay
            deploy lane by the fail-safe, so today's corpus is unaffected: 59 open blockers, all
            reviewer-deferred, 0 unread, 0 awaiting.
```

```
CLUSTER: WS-T — fixed-in-flight discharge  (x1: IMP-0905)
Altitude:   ENGINE. Nothing in it names this client
Ladder row: "a tool could catch it mechanically" + "an agent had the information and still did the
            wrong thing" (pipeline-agent and development-agent remedy text)
Becomes:    scripts/verify-improvement-log.py: sixth state `fixed-in-flight`, evaluated BEFORE
            already-fixed; `fixed_in_flight` = {by, at, feature, rerun, exit: 0, level} with optional
            `commit` (recorded, never ancestry-checked); requires an evidence_grep whose needle resolves
            in a deploy-path file; schema error on a governance blocker or a non-blocker. Counted toward
            the batch. Skill, WORKFLOW named-exception paragraph, pipeline-agent and development-agent
            remedy text.
Retires:    nothing
Cites:      IMP-0905; design WS-T requirements 1–4
Residual:   the gate cannot verify who stamped the entry or that `rerun` really exited 0 — both are
            recorded claims, read at the batch review. The needle check is exactly as strong as the
            existing already-fixed state. A V3+ defect is never closed by the stamp: closure still
            needs `reobserved` at its level. The build-is-the-fix case (build.log L70) is not covered.
```

```
CLUSTER: WS-Y — hand-typed batch threshold  (x1: IMP-0904; class hand-maintained-count-drifts-from-source)
Altitude:   ENGINE (agent files, template, gate docstring)
Ladder row: "an agent had the information and still did the wrong thing" — the function exists; five
            prose sites restate a figure it no longer returns
Becomes:    lead-agent L305, improvement-agent L51, build-agent L124 → pointer to batch_threshold();
            review template L5 → the same; gate docstring L6 → the same; the comment at gate L216–218
            corrected with the withdrawn wording retained
Retires:    nothing
Cites:      IMP-0904; design WS-Y
Residual:   re-typing a figure is not gated and will not be — a removal has no presence needle, and a
            phrase gate over prose has measured 48–100% false. Nothing is registered in
            derived-counts-registry.json because no figure remains to register.
```

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | script | `scripts/verify-improvement-log.py` + `.engine/` copy | Lanes: `defect_in` (required on blockers from the cutover date = apply date; bare paths or `live:<env>` from `environment_chain`), `lane_override` (only `deploy`), derive_lane() with the D-3 and D-9 answers, unread governance blocker → NOTE, D-10 rule for awaiting-approval, lane census line | WS-S.1–4, IMP-0905 | YES — `--selftest` gains the design's cases (a)–(f) as amended by D-9, plus: absent `deploy_paths` → deploy; `.github/workflows/` path → deploy | already wired — HARD [`improvement-log-check`](config/revitalise-grant-automation-build.yml#L80) and CI `validate` |
| 2 | script | `scripts/verify-improvement-log.py` + `.engine/` copy | New state `fixed-in-flight` evaluated before `already-fixed`; `fixed_in_flight` schema; needle must resolve in a deploy-path file; schema error on a governance blocker | WS-T.1–3, IMP-0905 | YES — `--selftest` gains the design's (a), (c), (d), (e), plus: present needle with no stamp → `already-fixed` error unchanged; stamp whose needle sits in `docs/` → error; `commit` optional, never resolved | already wired (same step) |
| 3 | script | `scripts/verify-improvement-log.py` + `.engine/` copy | Module docstring L6 threshold figure → pointer; L216–218 claim that the prose sites were cut → corrected, withdrawn wording retained | WS-Y, IMP-0904 | YES — the WS-Y sweep command below returns nothing | already wired (same step) |
| 4 | constraint-amendment | `constraints/technology/technology-constraints.md` | C-TECH-061: blocker clause becomes lane-aware per D-10's answer; governance blockers reported, not failed; withdrawn wording retained; cites the design and its requirement ids | WS-S.5 | YES — `python3 scripts/verify-improvement-log.py --check` | N/A |
| 5 | skill | `skills/how-to-log-an-improvement.md` | Schema block gains `defect_in`, `lane_override`, `fixed_in_flight`, with one paragraph each (the broken artefact, not the rule file, using IMP-0816 as the example); the "do not stamp a deferred_reason to clear your build" paragraph gains the fixed-in-flight route | WS-S.1, WS-T.3 | N/A — instruction change | N/A |
| 6 | agent | `agents/WORKFLOW.md` | L389–392 "an unclosed blocker halts" → deploy-lane; Processing-triggers blocker row → UNREAD deploy-lane, and governance blockers wait for the existing "feature completes" or reviewer-asks triggers and never pre-empt a delivery dispatch; named-exception section keeps its deferral sentence verbatim and gains one fixed-in-flight paragraph | WS-S.6, WS-T.4 | N/A — instruction change | N/A |
| 7 | agent | `agents/lead-agent.md` | Routing table L305 → threshold pointer; L306 → UNREAD deploy-lane blocker; L328–333 awaiting-approval paragraph rewritten per D-10 | WS-S.6, WS-Y | N/A — instruction change | N/A |
| 8 | agent | `agents/build-agent.md` | Step 7b table: L123 → unread deploy-lane blocker (governance: record and report); L124 threshold → pointer | WS-S.6, WS-Y | N/A — instruction change | N/A |
| 9 | agent | `agents/pipeline-agent.md` | "Before you dispatch ANOTHER agent" remedy: fix, stamp `fixed_in_flight`, re-run the gate, then dispatch; route to improvement-agent only when the defect cannot be fixed in flight | WS-T.4 | N/A — instruction change | N/A |
| 10 | agent | `agents/development-agent.md` | L363 section gains the fixed-in-flight route beside `corrects` | WS-T.4 | N/A — instruction change | N/A |
| 11 | agent | `agents/improvement-agent.md` | L51 threshold → pointer; L52 blocker trigger → UNREAD deploy-lane | WS-Y, WS-S.6 | N/A — instruction change | N/A |
| 12 | template | `templates/improvement-review-template.md` | L5 `≥10 NEW entries` → batch threshold pointer | WS-Y | N/A — template text | N/A |
| 13 | other | `instance.yaml` | Add `improvement.deploy_paths` per D-3 | WS-S.3 | YES — `python3 scripts/validate-instance.py` (the new key was tested on a scratch copy and raised nothing) | N/A |

**Constraint budget:** 0 of 3 used (one amendment, which the cap does not count).

**WS-Y's closing evidence is this command's empty output, pasted into the applied record.** A needle cannot express it:

```bash
grep -rn "≥ *30\b\|≥ *10 NEW\|>= *30 \|(30 since" .engine/agents/ .engine/templates/ .engine/skills/ scripts/verify-improvement-log.py constraints/ CLAUDE.md
```

---

## 4. Retirements

> Retirement check performed: 86 live constraint rows, 10 retired (derived with the struck-id grep). None is currently redundant because Group 1 amends C-TECH-061 rather than replacing it, and no other row speaks to blocker lanes or fix discharge.

The design names two candidates. The "feature completes" trigger row belongs to WS-U (Group 2). The self-deferral sentence is narrowed in scope, not retired, and it is prose in `WORKFLOW.md`, not a constraint row.

---

## 5. Findings left unprocessed

**Deferred:** IMP-0862, IMP-0887, IMP-0891, IMP-0892, IMP-0893, IMP-0894, IMP-0895, IMP-0896, IMP-0897, IMP-0898, IMP-0899, IMP-0900, IMP-0901, IMP-0902

| Finding | Why not processed here | Revisit when |
|---|---|---|
| The 14 unread entries above | Capability mode: this review is authorised by the design document and scoped to Group 1. None is a blocker, and the queue gate exits 0 | the next batch (the batch rung, or the post-deploy batch once Group 2 lands) |
| IMP-0901 specifically | Its author asks for it to follow Group 1, because it edits the same `WORKFLOW.md` section (a one-clause deletion at L372) | it can go in the same apply pass as Group 1 if you say so; otherwise the next batch |

Awaiting-approval entries belonging to sibling reviews (IMP-0855, IMP-0903, IMP-0906, IMP-0907) are left to the documents they name.

---

## 6. Digest impact

| | Before | After (predicted) |
|---|---|---|
| Log entries | 903 | 903 |
| Distinct lessons | 894 | 894 |
| Recurring classes (x≥2) | 70 | 70 |

This review's two findings are already in the digest, regenerated after appending, validator first. Applying the changes moves them to APPLIED, which does not change what renders. Sibling reviews may append in the meantime, so the figures are re-derived at apply time, never retyped.

---

## Plan of application

Written now so the apply step is mechanical. It is re-verified against the tree before anything is edited (activation step 8).

1. **Branches.** Instance changes go on `deploy-first-learning-and-item-closure`, which already exists and tracks origin. Engine changes (agents, skills, templates, `.engine/scripts/`) go on a branch **of the same name in `.engine`**, created from `3cc5b9e`, never on engine `main`. Push the engine branch first. Confirm `git -C .engine branch -r --contains HEAD` lists `origin/deploy-first-learning-and-item-closure`. Only then commit and push the instance pointer bump. Merge the engine branch before deleting it, or every fresh clone's pointer dangles.
2. **Order.** Gate script, both copies, identical. Then `--selftest`. Then run against the real log: it must print "0 deploy-open" and exit 0. Zero is correct because all 59 open blockers carry a reviewer's deferral. Then `instance.yaml`, C-TECH-061, the skill, the six agent files, the template.
3. **Corpus proof before closing.** Replay the 14 historical halts on scratch logs: each blocking entry restored to its halt-time state with the adjudicated `defect_in` above, and the verdict compared with the replay table. A mismatch withholds the change and is reported.
4. **Concurrency.** WS-X, WS-Z and the WS-W1 finding touch `pipeline-agent.md`, `build-agent.md` and `WORKFLOW.md` on other lines. Apply serially and re-read each file immediately before editing it.
5. **Closing checks:** `verify-improvement-log.py --check`, `generate-known-failure-modes.py --check`, `verify-engine-instance-split.py`, `verify-derived-counts.py`, `verify-build-config.py config/revitalise-grant-automation-build.yml`, `verify-doc-line-links.py`, `verify-review-document.py`, `verify-class-defences.py`, `validate-instance.py`, plus the WS-Y sweep above.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-26-improvement-review-4.md

Findings processed: 2 NEW  →  2 clusters
Regression check:   4 prior changes audited, 2 classes recurred
Proposed:           0 constraints (cap 3), 1 constraint amendment, 3 gates/scripts,
                    1 skill/knowledge edits, 6 agent-file edits, 1 template edits, 1 other,
                    0 retirements
Altitude calls:     1 generalised from instance to class, 0 left as notes
Digest:             will regenerate — 894 lessons, 70 recurring classes
Decisions open:     D-1, D-3, D-9 (new), D-10 (new)

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Applied

**Authorisation, recorded before any change** (`agents/WORKFLOW.md` → "What channel a keyword must arrive through"):

| Field | Value |
|---|---|
| `authorised_by` | Xander Lykopoulos (the reviewer) |
| `relayed_by` | lead-agent, quoted verbatim from the reviewer's own conversation turn in the commissioning session; a later turn confirmed "Group 1 was already approved and answers to questions given." |
| Keyword, verbatim | "D-1 agreed / D-3 deploy goes via pac tool to power platform DEV. Pac code push for Code app / D-9 Agreed / D-10 Agreed and fold in the IMP-0901 / Approve improvements" |
| Recorded | 2026-09-26, before the first edit |

**The decisions as applied:**
- **D-1: yes, with the three corrections.**
- **D-3:** deploys run locally through `pac` (solution import to DEV, `pac code push` for the Code App), not through CI. So `.github/workflows/` is **not** added. `deploy_paths` = `src/`, `provisioning/`, `config/*-build.yml`, `config/*-pipeline.yml`, `build/`. The redundant `provisioning/deploymentSettings/` entry is dropped, and an absent key means lanes are off.
- **D-9: the observed-at clause is dropped;** a governance blocker observed live prints a note.
- **D-10: an awaiting-approval deploy blocker keeps failing until it is fixed in flight.**
- **IMP-0901 is folded in:** the stale allocator clause at `agents/WORKFLOW.md` L372 is removed.

**Re-verified before applying (step 8).** Queue gate exit 0. No entry appended since the draft carries `corrects` naming anything this review acts on: IMP-0906 and IMP-0907 are friction entries, and IMP-0907 corrects IMP-0879, which is out of scope. Group 4's engine commit `3d9aa64` (the only one touching `build-agent.md`, `pipeline-agent.md` and `lead-agent.md`) was on the branch and those files were clean before they were edited. WS-W1's `7977bf7` touched `improvement-agent.md` (its verify-script count), so that file was re-read before the edit. Every file was re-read immediately before editing.

**Not committed, per the reviewer's later instruction** ("Wait until group 1 has landed. And all items of the plan are processed. Then we do 1 big commit."). Everything below is in the working tree only. One commit-and-push attempt was made before that instruction arrived, and it never executed: the harness gave no verdict. Engine HEAD is still `7977bf7`, and nothing is staged in either repository.

| # | Change | Applied at (working tree) | Entries moved |
|---|---|---|---|
| 1 | Lanes: `defect_in`, `lane_override`, `derive_lane()` with fail-safe, D-9 (observed-live note), D-10 (awaiting deploy blocker still fails), lane census | `scripts/verify-improvement-log.py` + `.engine/scripts/verify-improvement-log.py`, byte-identical | IMP-0905 → APPLIED |
| 2 | Sixth state `fixed-in-flight`, before `already-fixed`; carve-out in `check_evidence_grep`; needle must be in a shipped file; `commit` recorded, never resolved; counted toward the batch | same two files | (IMP-0905) |
| 3 | Docstring threshold pointer; false "six prose sites" comment corrected, withdrawn wording retained | same two files | IMP-0904 → APPLIED |
| 4 | C-TECH-061 lane-aware, withdrawn wording retained, Verify By updated | `constraints/technology/technology-constraints.md` | — |
| 5 | *Blocker lanes* section, schema example, fixed-in-flight route beside the self-deferral prohibition | `skills/how-to-log-an-improvement.md` | — |
| 6 | Capture-contract "Which id" row names the lock-held allocator (IMP-0901 folded in); lane wording; Processing-triggers rows; fixed-in-flight paragraph in the named exception, deferral sentence kept verbatim | `agents/WORKFLOW.md` | IMP-0901: not moved, see below |
| 7 | Routing table (threshold pointer, deploy-lane row, governance row), census mention, D-10 paragraph with withdrawn wording | `agents/lead-agent.md` | — |
| 8 | Step 7b: deploy-lane / governance / batch rows, threshold pointer | `agents/build-agent.md` | — |
| 9 | Remedy is now "fix, stamp, re-run, then dispatch"; withdrawn wording retained | `agents/pipeline-agent.md` | — |
| 10 | Step 4: stamp `fixed_in_flight`; lane wording | `agents/development-agent.md` | — |
| 11 | Trigger rows: threshold pointer, deploy-lane blocker row | `agents/improvement-agent.md` | — |
| 12 | Trigger line: threshold pointer, no `≥10` | `templates/improvement-review-template.md` | — |
| 13 | `improvement.deploy_paths` per D-3 (no `.github/workflows/`: deploys run locally through `pac`) | `instance.yaml` | — |

**Deviation, and why.** D-3 was answered with a fact rather than a yes. Deploys go via `pac` to DEV, with `pac code push` for the Code App. So the draft's proposed `.github/workflows/` entry was not added. No other wording departs from the draft.

**IMP-0901** was folded in as its author proposed: the clause is removed from `WORKFLOW.md`. The entry itself is left `unread` for its own review, because this review did not process it, and it stays on the `**Deferred:**` line above. Its needle-free proposal is now satisfied on disk; the next batch can close it by grep.

**Bookkeeping triggered by the apply:** IMP-0717's needle matched the Processing-triggers row this review reworded, and the gate went red (exit 1). The needle was re-pointed to the surviving row (`needle_repointed_by` names this review, and `needle_repoint_note` says why). Substance unchanged; one log line changed.

**Executed results:**
- Selftest: **89 of 89** fixtures pass.
- **Mutation proof:** removing each new mechanism in turn, on a scratch copy, fails at least one fixture. The six mutations were the precedence, the carve-out, the fail-safe, the governance lane, D-10 and the prose-needle check.
- Real log: exit 0, census `0 deploy-open, 0 governance, 0 fixed-in-flight`. Zero is correct because all 59 open blockers carry a reviewer's deferral.
- **14-halt replay against the real gate, on scratch logs:** every verdict matches the replay table. L59 and L96 pass on lanes. L54 and L121 fail without a stamp (D-10) and pass with one. L78/79, L83/84, L100, L123 and L125 fail without a stamp and pass with one. L61 (schema error) and L70 (the fix is the build) still halt. L47's blocker half matches; its batch-rung half is not replayable at today's threshold, and that code path is unchanged and covered by the existing batch-trigger fixture.

**WS-Y sweep** (the removal evidence), run with a positive control that returned its hit:

```
grep -rn "≥ *30\b\|≥ *10 NEW\|>= *30 \|(30 since" .engine/agents/ .engine/templates/ .engine/skills/ scripts/verify-improvement-log.py constraints/ CLAUDE.md
scripts/verify-improvement-log.py:238:# `grep -rn "thirty\|≥30\|30 \`NEW\`"`. The seven sites use FOUR different spellings between
```

The one hit is the historical comment that quotes the pattern for future sweeps. It is history, not a statement of the threshold, and it stays.

**Closing checks:**
- Exit 0: `verify-improvement-log.py --check`, `--selftest`, `generate-known-failure-modes.py --check` (903 entries, 894 distinct lessons, 70 recurring classes — as predicted), `verify-engine-instance-split.py`, `verify-build-config.py`, `verify-doc-line-links.py`, `verify-review-document.py`, `verify-class-defences.py`, `validate-instance.py`.
- `verify-derived-counts.py`: **one SOFT drift, not from this review.** The verify-script count in `agents/improvement-agent.md` says 66 and the source says 67, because of WS-X's uncommitted `verify-post-deploy-completeness.py`. WS-X owns that edit, so it is left to avoid a collision.

**Level reached:** V1 — the gate parses, its suite is green, and it has run against the real log and the replay corpus. The first live use of a `fixed_in_flight` stamp by a delivery agent is the first real exercise of WS-T.
