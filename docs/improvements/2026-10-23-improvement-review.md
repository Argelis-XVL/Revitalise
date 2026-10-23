# Improvement Review — 2026-10-23 (1)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 5 `NEW` → 3 clusters (2 unread, plus 3 reviewer-deferred entries whose return condition was met after the last review)
**Trigger:** reviewer request, relayed by lead-agent. It also covers the scoped DEV push of build `trustee-portal-design-2-20261022-4` ([pipeline.log L461](logs/pipeline.log#L461)), which got no batch of its own because review 2026-10-22 (3) was parked at its gate when it landed.
**Status:** APPLIED 2026-10-23 06:50 — `APPROVE IMPROVEMENTS` (reviewer Xander Lykopoulos, relayed by lead-agent). Rows 1–4 applied as drafted; 4 findings closed, 1 re-deferred; one new finding logged (IMP-1242). Not committed. `reviewed_in` is on all five entries (IMP-1241 and IMP-1236 stamped by lead-agent on the reviewer's instruction). Applied record: §8.
**Serves:** `wbs:system`; the two builds behind the findings serve `wbs:6.3` (unbilled)
**Gate:** `APPROVE IMPROVEMENTS`

---

## Summary

The queue held two unread findings, and both are small tool defects with a measured fix. Scoped DEV builds of the trustee portal could not find their own last green build. Deferring a superseded work item did not stop the work-items check from counting its dead evidence. I propose three script changes and one build-agent edit, each tested on a scratch copy. Two older findings can also be closed, because their conditions were met last night and I re-ran both checks this morning. You have one decision: the keyword.

## What has been built

Nothing is applied yet. The draft proposes the following.

1. **A scoped build now finds the last green build of the same build config, whichever feature directory it sits in** — [resolve_last_green](.engine/scripts/run-build.py#L193).
   Today the runner looks for green builds under the build config's own feature name (`revitalise-grant-automation-*`). Portal builds are filed under `trustee-portal-design-2-*`, so it missed them. The real tree shows the gap: the runner today picks build `20261021-3` (commit `495dd5b`), and with the fix it picks last night's green portal build `20261022-4` (commit `ca3797b`). The finding asked for a `--feature` flag instead. I did not use one, because a flag can be left off, and leaving off an argument is how this kind of defect has already happened four times.

2. **The manifest check reads the build config the runner recorded, instead of guessing it from the feature name** — [verify-build-manifest-note.py L292](scripts/verify-build-manifest-note.py#L292).
   This is the same failure a build-agent instruction was meant to prevent in August, and it happened again: the instruction says to pass `--build-config`, and on 2026-10-22 the agent did not. Against last night's real manifest the check goes from `NO BUILD CONFIG` to a pass. A recorded config that does not exist still fails.

3. **A deferred work item's broken evidence becomes a note, as a finished item's already is** — [verify-work-items.py L82](.engine/scripts/verify-work-items.py#L82).
   A deferred item can only come back through a reopen, and a reopen clears its evidence, so that evidence can never count again. Failing on it cost pm-agent a resume and a second defer for each superseded item. I replayed the ledger at the point of the two deferrals. The check today gives 54 failures and the fix gives 49, and the 5 it removes are exactly the 5 the finding names.

4. **build-agent's instructions describe the new behaviour** — [build-agent.md L98](agents/build-agent.md#L98), [L264](agents/build-agent.md#L264), [L412](agents/build-agent.md#L412).
   Three sentences describe the old file pattern and the old default. If they are left as they are, the next agent will work around a fault that no longer exists.

## Elements changed

| File | Repository | Change |
|---|---|---|
| [run-build.py](.engine/scripts/run-build.py#L193) | engine (the instance copy is a wrapper) | §A |
| [verify-build-manifest-note.py](scripts/verify-build-manifest-note.py#L292) + its engine twin | both (byte-identical pair) | §B |
| [verify-work-items.py](.engine/scripts/verify-work-items.py#L82) | engine (the instance copy is a wrapper) | §C |
| [build-agent.md](agents/build-agent.md#L98) | engine | §D |

## What is still open

**Choosing the wrong feature name for the artifact directory is still possible.** An older deferred finding records a build filed under the build config's name instead of the feature's name. Its return condition was "a fifth instance of this class", and the manifest half of tonight's finding is that fifth instance. After this review the wrong name no longer breaks the last-green lookup or the manifest check, so its cost drops to a wrongly named folder. A check on the name itself was measured in September at 41% false alarms, so it stays deferred with a new return condition.

**Changing a built item's acceptance text after a design change is still a separate, open design question.** This review does not touch it, and the deferral fix does not depend on it.

**Review 2026-10-22 (3) wrote "the 8 classic-portal items" when the measurement was 8 rows across 5 items.** The same review had counted 8 rows correctly a few lines earlier. The rule against this landed in that review's own apply, after the draft was written. It needs no further change, and the counts here are given per item and per row.

## What you need to decide

**Approve these 4 changes?**

**Problem** — Scoped DEV builds of the portal fall back to a full 88-step run, and deferring superseded items leaves the work-items check red until someone works around it.
**Suggested fix** — Reply `APPROVE IMPROVEMENTS`. I apply rows 1–4 as drafted in §A–§D, close 4 findings, and re-defer 1 with a new return condition.
**What happens if you don't** — Each scoped portal build needs its base commit passed by hand, or it runs in full. Each superseded item costs two extra ledger events.
[§3, proposed changes](docs/improvements/2026-10-23-improvement-review.md#L158)

---

**After approval: one engine commit, then one pointer bump.** Rows 1–4 change files in `.engine`, and row 2 also changes the instance copy. I will give you the commands in the required order, with the engine push first.

---

Verification: all three scratch selftests pass. Each new test fails against today's code: run-build gives `aaa1` against an expected `bbb2`, and verify-work-items fails with `['EVIDENCE']`. Both are recorded in §2. The corpus measurements are above, and each was run against the real tree and ledger. `EntraScripts.Tests.ps1` run alone: 45 of 45 pass (06:27). The unscoped work-items check: 0 failures, and 0 lines name `trustee-review-portal-cards`. The dispositions were simulated on a scratch copy of the log: 0 unread and 0 awaiting-approval, and the only 2 errors were the needles of rows 1 and 3, which cannot exist until the apply. The real log stayed byte-identical. **Not verified:** a real scoped build with the fix, and a real deferral under the new rule. Both need a build-agent or pm-agent dispatch after the apply. Both findings are V1, so neither closure waits on it.

---

## 1. Regression check — did the last review's changes work?

The last review applied was 2026-10-22 (3), at 21:05. **No finding has been logged since then.** IMP-1240 (20:36) and IMP-1241 (21:04) both predate the apply. The table is therefore about whether each change was exercised, and what that showed.

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| Rows 14–15: `add`/`link` refuse a label no environment declares | 2026-10-22 21:00 | `component-label-declared-nowhere` (IMP-1238) | NO | Exercised by pm-agent's 51 relinks ([routing.log L1750](logs/routing.log#L1750)), all accepted. No deploy has happened since, so IMP-1238's V3 condition is still open |
| Row 12(a): development-agent counts a folder's consumers before a removal | 2026-10-22 | `retirement-or-rename-leaves-consumers` | NO | Not exercised: no removal since. The routed repair it pointed to is complete: the unscoped check went 326 → 49 → 14 → 0 ([routing.log L1759](logs/routing.log#L1759)), and I re-measured 0 at 06:27 |
| Row 12(b): carry the build's standing warnings into a new Dev Summary | 2026-10-22 | `untriaged-tool-warning` | NO | Not exercised: no new feature since |
| Row 13: improvement-agent re-derives counts and causes | 2026-10-22 | `finding-premise-fails-re-measurement` | NO (IMP-1241's item/row slip was written before row 13 landed) | Applied here: IMP-1240's `expected` is overruled by measurement (cluster 1), and IMP-1241's counts are re-derived per row and per item |
| Rows 1–11 (knowledge, skills, agent rules) | 2026-10-22 | various | NO | No finding names them |
| Routed: `EntraScripts.Tests.ps1` dot-source fix | 2026-10-22 21:02 | IMP-1235 | NO | **Working**: 45/45 alone, re-run 2026-10-23 06:27. Closed below |

**Changes whose class recurred after a *prose* fix:** `gate-invocation-omits-required-arg`. build-agent.md has told the agent to pass `--build-config` since review 43 (IMP-0479), and IMP-1240 records the agent not doing it. That is a recurrence after prose, so row 2 moves it to the script.
**Changes whose class recurred after a *gate*:** none.

---

## 2. Clusters and promotion decisions

```
CLUSTER: shared-build-config-feature-name-misderived  (x1 + family: IMP-1240; IMP-0611 re-deferred)
Altitude:   CLASS. Where one build config serves several features, two tools derived one identity
            from the other: run-build.py looked up green results under the CONFIG's feature name,
            and verify-build-manifest-note.py derived the CONFIG from the MANIFEST's feature name.
            Same family as gate-invocation-omits-required-arg x4 (IMP-0470, 0479, 0494, 0611),
            whose prose fixes did not hold.
Ladder row: a tool could catch it mechanically + recurrence after a prose fix -> script
Becomes:    row 1, run-build.py: last-green = newest SUCCESS result whose RECORDED `config` equals
            this run's config, in any build/artifacts/*/ directory (§A).
            row 2, verify-build-manifest-note.py: with no --build-config, read `config` from the
            sibling run-build-result.json before deriving config/<feature>-build.yml (§B).
            row 4, build-agent.md: three sentences rewritten to match (§D).
Retires:    nothing. --build-config stays as the explicit override and the derivation stays as the
            last fallback, which still fails closed
Cites:      IMP-1240, IMP-0611
Residual:   (1) Results written before IMP-1053 sit outside artifact dirs and are invisible; 41 of
            41 in-dir results carry `config`, so nothing current is lost. (2) The manifest check
            gains nothing on the 38 older manifests that have no sibling result. It runs on the
            current artifact only, and every build-agent run since IMP-1053 writes one. (3) The
            wrong --feature for resolve-artifact-dir.py (IMP-0611) is not prevented; it now only
            costs a misnamed directory.
```

**Why config and not feature, contrary to the finding's `expected`.** IMP-1240 asked for "the newest SUCCESS result for the feature named in the dispatch, whatever config it ran under". That key is wrong in principle. The induction that makes skipping safe is over the config's steps, so a green run under a different config proves nothing about this one. Keying on the recorded config is the property itself, and it needs no flag. Only one build config exists today ([build config](config/revitalise-grant-automation-build.yml#L10)), so on the real tree the two keys happen to agree.

**Premises re-measured at draft time.**
- *last-green misses sibling features:* the old resolver returns `495dd5b` from `revitalise-grant-automation-20261021-3`, and the scratch resolver returns `ca3797b` from `trustee-portal-design-2-20261022-4`. `--plan --changed-since last-green` on the real config gives "FULL RUN — config, .engine changed" today, and "FULL RUN — .engine changed" with the fix. The config is no longer a false trigger. The run stays full only because this morning's commit bumped the engine pointer, which is correct.
- *Result files carry `config`:* 41 of 41 under `build/artifacts/*/run-build-result.json`, all `config/revitalise-grant-automation-build.yml`.
- *Manifest gate fails on a shared-config feature:* reproduced on `trustee-portal-design-2-20261022-4/manifest.json`, which gives `NO BUILD CONFIG`, exit 1. The scratch gate gives PASS. Across 99 manifests the old default resolves 57 and fails 42. The fix resolves 4 of the 42 (those with a sibling result), and the other 38 are older builds the gate is never run on again. The manifest's own `build_config` field is present on only 1 of 99, with prose appended to the path, so it was not used.
- *The instruction exists and was not followed:* [build-agent.md L409](agents/build-agent.md#L409) shows the command with `--build-config`.
- *Mutation:* the run-build fixture against today's resolver returns `aaa1` against an expected `bbb2`, so it fails. The manifest fixture's case is exactly the real reproduction above.

```
CLUSTER: work-item-evidence-orphaned-by-folder-rename  (x1: IMP-1241)
Altitude:   CLASS. The property is "evidence that can never be used again is history". `done`
            already had it; `deferred` did not, though a reopen from deferred empties
            evidence_since_reopen (lib/work_items.py, the reopen branch).
Ladder row: a tool could catch it mechanically
Becomes:    row 3, verify-work-items.py: drift on a deferred item is a NOTE naming the item, as on
            a done item; docstring and two selftest cases (§C)
Retires:    nothing. pm-agent's reopen-then-defer workaround is no longer needed, but it was never
            written into a rule, so there is nothing to retire
Cites:      IMP-1241
Residual:   A deferred item's drift no longer fails any build. That is intended: C-TECH-079 already
            treats `deferred` with a reason as a discharge, and the note still names it. Amending a
            built item's acceptance after a design change is IMP-1175's open design, not this.
```

**Premises re-measured.** The fold does not reset the window on `defer`, only on `reopen` ([lib/work_items.py](.engine/scripts/lib/work_items.py#L959)). The drift check fails every state except `done` ([L82](.engine/scripts/verify-work-items.py#L82)). Replaying the ledger truncated at line 1045 (the two deferrals, before the workaround) gives 54 failures today and 49 with the fix. The 5 removed are WI-0005 ×1 and WI-0008 ×4, the rows IMP-1241 names. The other 49 are other items' real drift, and they still fail. On today's ledger the fix changes nothing: 0 failures, 44 notes, both before and after. pm-agent's workaround had already cleared these rows. The alternative proposal, making `defer` empty the window, was not taken. It would erase the record a note keeps visible.

**IMP-1241's second half.** Review 2026-10-22 (3) said "8 name classic-portal code" ([L41](docs/improvements/2026-10-22-improvement-review-3.md#L41)), which is correct as a row count, and then "the 8 classic-portal items" ([L65](docs/improvements/2026-10-22-improvement-review-3.md#L65)), which is wrong: they were 8 rows across 5 items. This is the item-versus-row form of `finding-premise-fails-re-measurement`, written before that review's row 13 landed, so it needs no new rule.

```
CLUSTER: deferred-entries-whose-condition-was-met  (x2: IMP-1235, IMP-1236)
Altitude:   NOTE. Closures, not changes
Ladder row: a deferred entry closes when its revisit_when is observed at its level
Becomes:    CLOSE on apply. IMP-1235 with reobserved V2; IMP-1236 with evidence_grep (V1)
Retires:    nothing
Cites:      IMP-1235, IMP-1236
Residual:   none
```

- **IMP-1235** (V2) — return condition: *"`EntraScripts.Tests.ps1` passes 45 of 45 when run alone with Invoke-Pester"*. Re-run by this review on 2026-10-23 at 06:27, with only that container: `passed=45 failed=0 total=45`. development-agent reported the same result at 21:02.
- **IMP-1236** (V1) — return condition: *"the unscoped `verify-work-items.py --check` reports no [EVIDENCE] failure naming trustee-review-portal-cards"*. Re-run at 06:27: exit 0, 0 failures, and 0 lines name the folder.

**Other reviewer-deferred entries checked against last night's events.** The scoped push at 20:37 and your visual check at 20:48 confirmed the Decision-column buttons only. I matched 39 deferred return conditions that mention the portal, a push, styling or work items. None is met: the stat-tile and round-overview conditions need a different screen, and IMP-1238 needs a deploy. IMP-0986's two-app condition is overtaken by the retirement of the second app. It is named in §5 and not processed here.

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | script | [.engine/scripts/run-build.py L193](.engine/scripts/run-build.py#L193), engine only | `resolve_last_green` keys on the recorded `config`; docstring; fixture `last-green-keys-on-config` (§A) | IMP-1240 | YES — `python3 scripts/run-build.py --selftest`. Scratch: PASS; today's resolver fails the fixture (`aaa1` ≠ `bbb2`). Corpus: base moves `495dd5b` → `ca3797b` | already wired (it is the build runner, build-agent step 5) |
| 2 | script | [scripts/verify-build-manifest-note.py L292](scripts/verify-build-manifest-note.py#L292) + `.engine/scripts/` twin | `config_from_run_result()`; precedence flag → recorded → derived; 2 fixtures; `--help` text (§B) | IMP-1240, IMP-0611 | YES — `--selftest`. Scratch: 24 fixtures OK. Real: `-4` manifest `NO BUILD CONFIG` → PASS | `SUITE_GATE_EXEMPT` + reason already recorded ([verify-build-config.py L745](.engine/scripts/verify-build-config.py#L745): its input is written after every step) |
| 3 | script | [.engine/scripts/verify-work-items.py L82](.engine/scripts/verify-work-items.py#L82), engine only | Drift on a `deferred` item is a note; docstring; 2 selftest cases (§C) | IMP-1241 | YES — `python3 scripts/verify-work-items.py --selftest`. Scratch OK; today's gate fails the new case (`['EVIDENCE']`). Replay at ledger L1045: 54 → 49, the 5 removed named | already wired (SOFT `--warn-only`, [build config L182](config/revitalise-grant-automation-build.yml#L182)) |
| 4 | agent | [build-agent.md L98](agents/build-agent.md#L98), [L264](agents/build-agent.md#L264), [L412](agents/build-agent.md#L412) | Three sentences describe the recorded-config lookups (§D) | IMP-1240 | N/A — instruction change | N/A |

**Constraint budget:** 0 of 3 used.

**Engine altitude (skill §6).** Rows 1–4 land in `.engine`. Their text names no client table, person or environment. The comments cite finding ids only, and the fixtures use the placeholder names `implicit-1`, `sibling-feature-1` and `other-config-1`. `grep -c 'revitalise\|Revitalise'` over the three diffs: 0.

**Dispositions, decided now from `observable_at`:**

| Entry | `observable_at` | Disposition |
|---|---|---|
| IMP-1240 | V1 | **CLOSE** on apply; `evidence_grep` `.engine/scripts/run-build.py` ⊃ `last-green-keys-on-config` |
| IMP-1241 | V1 | **CLOSE** on apply; `evidence_grep` `.engine/scripts/verify-work-items.py` ⊃ `IMP-1241: drifted evidence on a deferred item` |
| IMP-1235 | V2 | **CLOSE** with `reobserved` V2 (improvement-agent, 2026-10-23T06:27, Pester on `EntraScripts.Tests.ps1` alone, 45/45) |
| IMP-1236 | V1 | **CLOSE**; `evidence_grep` `agents/development-agent.md` ⊃ `Before you remove or rename a folder, count its consumers` (row 12, present, count 1) |
| IMP-0611 | V1 | **DEFER again**: its trigger (a fifth instance) is met by IMP-1240. Rows 1–2 remove the two lookups a misnamed directory used to break. The remaining mechanism, an agent passing the wrong `--feature`, still has no precise check. New `revisit_when`: *a dispatch's feature slug reaches build-agent as a recorded value (a routing-line field or a dispatch file) that resolve-artifact-dir.py can compare against, or a misnamed artifact directory costs a failed step after this review* |

### Routed work

None.

---

## 4. Retirements

> Retirement check performed: 10 retired and 88 live constraint rows (`grep -rh '^| ~~C-'` and
> `'^| C-'` over `constraints/`). The live rows these clusters touch are C-TECH-079 (work items)
> and none for the build runner. None is made redundant: row 3 aligns the drift check with
> C-TECH-079's existing treatment of `deferred`, and rows 1–2 add no rule. build-agent.md's
> `--build-config` instruction is kept, rewritten as an override, not retired. The flag stays the
> explicit form. Nothing is retired.

---

## 5. Findings left unprocessed

**Deferred:** IMP-1175, IMP-0986

| Finding | Class | Why not processed | Revisit when |
|---|---|---|---|
| IMP-1175 | `ledger-cannot-record-a-design-change-honestly` | Related to IMP-1241 but a different mechanism: an acceptance amendment on a built item, which needs a supersede-transition design. Row 3 neither needs nor pre-empts it | its own: a design for a work-item supersede transition exists |
| IMP-0986 | `deploy-record-cannot-name-which-app` | Its return condition names two apps, and the second was retired on 2026-10-22. Settling whether it is superseded is a separate disposition and not in this queue | its own; a later batch may close it as superseded |

The 3 fixed-in-flight blockers (IMP-1095, IMP-1098, IMP-1156) wait on a designer save of the scrub flow. Nothing last night observed that, so they were not re-derived. The other 304 reviewer-deferred entries are unchanged.

---

## 6. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 1237 | 1238 (IMP-1242 appended at apply; see §8) |
| Distinct lessons | 1213 | 1214 (measured on apply) |
| Recurring classes (x≥2) | 96 | 96 (measured on apply) |
| Entries closed | — | 4 (IMP-1240, IMP-1241, IMP-1236 V1; IMP-1235 V2); 1 re-deferred |
| Digest lines | 640 | 640 (measured on apply) |

Regenerated on apply with `python3 scripts/generate-known-failure-modes.py`, confirmed with `--check`.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-10-23-improvement-review.md

Findings processed: 5 NEW  →  3 clusters
Regression check:   6 prior changes audited, 0 classes recurred
Proposed:           0 constraints (cap 3), 3 gates/scripts, 0 skill/knowledge edits,
                    1 agent-file edits, 0 retirements
Altitude calls:     2 generalised from instance to class, 1 left as notes
Digest:             will regenerate — 1213 lessons, 96 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. On approval

### Applied 2026-10-23 06:40–06:50 (`APPROVE IMPROVEMENTS`, reviewer Xander Lykopoulos, relayed by lead-agent)

All four rows applied as drafted, with no narrowing and nothing withheld. The four target files still had the sha1s measured at draft, so no merge was needed.

| Row | Landed at | Verified by |
|---|---|---|
| 1 | [resolve_last_green](.engine/scripts/run-build.py#L206) | `run-build.py --selftest` PASS, including `last-green by config`. `--plan --changed-since last-green` on the real config: "FULL RUN — .engine changed", with no config trigger, as the draft predicted |
| 2 | [config_from_run_result](scripts/verify-build-manifest-note.py#L243), engine twin byte-identical (`cmp`) | `--selftest` OK, 24 fixtures, both new cases OK. The `-4` manifest without `--build-config`: PASS, exit 0 (was `NO BUILD CONFIG`) |
| 3 | [drift loop](.engine/scripts/verify-work-items.py#L83) | `--selftest` OK, both new cases OK. Unscoped `--check`: 0 failures, 44 notes, as before |
| 4 | [build-agent.md L98](agents/build-agent.md#L98), [L265](agents/build-agent.md#L265), [L414](agents/build-agent.md#L414) | Text as in §D |

**One addition beyond the §A diff:** the resolver skips a result whose top level is not an object before reading `config`. That is a guard against a malformed file, not a change to what it matches.

**Dispositions, as drafted:** IMP-1240 and IMP-1241 APPLIED with the §3 needles; IMP-1235 APPLIED with `reobserved` V2 and the needle `when this file runs alone (IMP-1235).` in `EntraScripts.Tests.ps1` (the draft named no needle for it, and every closure needs one); IMP-1236 APPLIED with the row-12 needle; IMP-0611 re-deferred with the approved `revisit_when` verbatim and the reason annotated. `verify-improvement-log.py --check` after the dispositions: exit 0, 0 unread, 0 awaiting-approval.

**Closing checks:** `verify-engine-instance-split.py` exit 0. `verify-derived-counts.py` exit 1 (SOFT) on one claim this review did not touch: the parent dev summary still gives the portal bundle as 1205 kB, and the budget file says 858 after the portal swap. Logged as IMP-1242 and not fixed here, because that document belongs to development-agent. The digest regeneration drifted no registered claim.

**Not executed in this session:** a direct call to the new resolver against the real artifact tree was refused by the permission classifier. The `--plan` run above measures the same thing through the CLI. A real scoped build and a real deferral under the new rule still wait on a build-agent or pm-agent dispatch.

**Publishing:** rows 1–4 change `.engine` (four files), and row 2 also changes `scripts/`. Nothing is committed. The engine needs its own commit, a push to the branch that already contains its parent, and then a pointer bump here.

---

Written **after** `APPROVE IMPROVEMENTS`. Apply order: (1) set the status to `APPLYING`. (2) Confirm the targets still have the sha1s measured at draft: `.engine/scripts/run-build.py` `cd7e19ac1e1c…`, both copies of `verify-build-manifest-note.py` `a36c8bc6b520…`, and `.engine/scripts/verify-work-items.py` `538513dbc889…`. Merge if they differ. (3) Apply §A–§D one row at a time and close each entry as its row lands. (4) Run the three selftests, `verify-engine-instance-split.py`, the unscoped work-items check, and the `-4` manifest check without `--build-config`. (5) Regenerate the digest. (6) Run `verify-improvement-log.py --check`, `verify-derived-counts.py` and `verify-review-document.py`.

---

## §A — `.engine/scripts/run-build.py` (proposed)

Measured on a scratch copy: selftest PASS (`… last-green by config, result default path`).

```diff
@@ module docstring
-`build/artifacts/<feature>-*/run-build-result.json`. Correct by induction: a step skipped in
+`build/artifacts/*/run-build-result.json` whose recorded `config` is this run's config, whatever
+feature directory it sits in (IMP-1240). Correct by induction: a step skipped in
@@ def resolve_last_green
-def resolve_last_green(repo_root: Path, feature: str) -> dict | None:
-    """Newest SUCCESS result for this feature that recorded a git_head."""
-    candidates = sorted((repo_root / "build" / "artifacts").glob(f"{feature}-*/run-build-result.json"),
+def _config_key(repo_root: Path, value: str | None) -> str | None:
+    """A recorded or passed config path, normalised to one comparable string."""
+    if not value:
+        return None
+    p = Path(value)
+    p = p if p.is_absolute() else repo_root / p
+    try:
+        return p.resolve().relative_to(repo_root.resolve()).as_posix()
+    except ValueError:
+        return p.resolve().as_posix()
+
+
+def resolve_last_green(repo_root: Path, config_path: Path) -> dict | None:
+    """Newest SUCCESS result that ran THIS build config and recorded a git_head.
+
+    Keyed on the `config` each result records, never on a feature name (IMP-1240). One config
+    serves several features, and build-agent names each artifact directory after the
+    DISPATCHED feature, not after the config's own `feature:` field, so a feature-name glob
+    missed every green run of a sibling feature and fell back to a full run. The induction
+    in the module docstring holds per config: the steps are the config's, so a green run of
+    it under any feature's directory is a valid base."""
+    want = _config_key(repo_root, str(config_path))
+    candidates = sorted((repo_root / "build" / "artifacts").glob("*/run-build-result.json"),
                         key=lambda p: p.stat().st_mtime, reverse=True)
     for path in candidates:
         ...
+        if _config_key(repo_root, doc.get("config")) != want:
+            continue
         if doc.get("status") == "SUCCESS" and doc.get("git_head"):
@@ def resolve_scope
-        green = resolve_last_green(repo_root, feature)
+        green = resolve_last_green(repo_root, config_path)
         if green is None:
             return None, {"scoped": False, "changed_since": changed_since,
-                          "full_run_reason": "no green result with a recorded git_head under "
-                                             f"build/artifacts/{feature}-*/ — this full run "
-                                             "becomes the baseline"}
+                          "full_run_reason": "no green result with a recorded git_head ran "
+                                             f"{config_path} under build/artifacts/*/ — this "
+                                             "full run becomes the baseline"}
@@ selftest, before result-defaults-into-artifact-dir
+        # last-green-keys-on-config (IMP-1240): a green run of the SAME config filed under a
+        # sibling feature's directory is the base; a newer green run of ANOTHER config is not.
+        arts = repo2 / "build" / "artifacts"
+        for name, cfgval, head, age in (("implicit-1", "build.yml", "aaa1", 300),
+                                        ("sibling-feature-1", "build.yml", "bbb2", 200),
+                                        ("other-config-1", "other.yml", "ccc3", 100)):
+            (arts / name).mkdir(parents=True)
+            rp = arts / name / "run-build-result.json"
+            rp.write_text(json.dumps({"status": "SUCCESS", "config": cfgval, "git_head": head}))
+            t = time.time() - age
+            os.utime(rp, (t, t))
+        lg = resolve_last_green(repo2, cfg2)
+        if not lg or lg["ref"] != "bbb2":
+            failures.append(f"last-green-keys-on-config: got {lg and lg['ref']!r}, want 'bbb2' — "
+                            f"the newest green run of this config under ANY feature directory")
+        shutil.rmtree(arts.parent)
@@ selftest PASS line
-              "change scoping, command-named inputs, result default path)")
+              "change scoping, command-named inputs, last-green by config, result default path)")
```

## §B — `verify-build-manifest-note.py`, both copies (proposed)

Measured on a scratch copy: selftest OK, 24 fixtures, both new cases OK.

```diff
@@ before def check_required_fields
+def config_from_run_result(path: Path, repo_root: Path) -> Path | None:
+    """The build config the runner RECORDED for this artifact, if it left a result beside it.
+
+    Precedence is --build-config, then this, then config/<feature>-build.yml. The manifest's
+    `feature` is the DISPATCHED feature, and one config serves several features, so deriving
+    the config from it failed NO BUILD CONFIG on every sibling-feature build; build-agent.md
+    told the agent to pass the flag, and the prose was not enough twice (IMP-0479, IMP-1240).
+    `run-build-result.json` carries `config` as a value. An unreadable or config-less result
+    falls through to the old derivation, which still fails closed."""
+    result = path.parent / "run-build-result.json"
+    try:
+        value = json.loads(result.read_text(encoding="utf-8")).get("config")
+    except (OSError, json.JSONDecodeError, AttributeError):
+        return None
+    if not isinstance(value, str) or not value.strip():
+        return None
+    config = Path(value)
+    return config if config.is_absolute() else repo_root / config
@@ soft_gates block
     config = build_config
     if config is None:
+        config = config_from_run_result(path, repo_root)
+    if config is None:
         if not feature:
@@ selftest, before the _CASES loop
+        # config-from-run-result (IMP-1240): a sibling feature's manifest resolves the config
+        # the runner recorded beside it; a recorded config that does not exist still fails.
+        for n, (label, recorded, expect_fail, want) in enumerate((
+                ("required: a manifest whose feature has no config resolves the one recorded in "
+                 "the sibling run-build-result.json", "config/feat-build.yml", False, ""),
+                ("required: a recorded config that does not exist still fails NO BUILD CONFIG",
+                 "config/gone-build.yml", True, "NO BUILD CONFIG"))):
+            adir = Path(tmp) / f"art-{n}"
+            adir.mkdir()
+            (adir / "run-build-result.json").write_text(json.dumps({"config": recorded}),
+                                                         encoding="utf-8")
+            mpath = adir / "manifest.json"
+            mpath.write_text(json.dumps(dict(cases[0][1], feature="sibling-feature")),
+                             encoding="utf-8")
+            errors = check_manifest(mpath, repo_root=root)
+            rc = 1 if errors else 0
+            ok = ((rc != 0) if expect_fail else (rc == 0)) and (not want or want in "\n".join(errors))
+            print(f"  {'OK' if ok else 'DID NOT BEHAVE':16} {label} → exit {rc}")
+            if not ok:
+                failures.append(label)
+            _required_case_count += 1
@@ --build-config help
-                                         "(default: config/<feature>-build.yml)")
+                                         "(default: the `config` recorded in the sibling "
+                                         "run-build-result.json, else config/<feature>-build.yml)")
```

## §C — `.engine/scripts/verify-work-items.py` (proposed)

Measured on a scratch copy (with the engine `lib/` beside it): selftest OK.

```diff
@@ docstring
-    EVIDENCE  a transition lacks the evidence its state needs, or an item that is NOT done has
-              evidence (since its last reopen) that no longer resolves at HEAD
+    EVIDENCE  a transition lacks the evidence its state needs, or an item that is neither done
+              nor deferred has evidence (since its last reopen) that no longer resolves at HEAD
@@
-NOTES (reported, never failing): evidence drift on a done item (code moves on after closure),
+NOTES (reported, never failing): evidence drift on a done or deferred item (code moves on after
+closure; a deferred item's evidence is emptied by the reopen that resumes it — IMP-1241),
@@ drift loop
-                if it.state == "done":
-                    notes.append(f"{it.id} (done): evidence from line {line} has drifted — {msg}")
+                if it.state in ("done", "deferred"):
+                    # A deferred item's evidence is history, exactly as a done item's is: the only
+                    # way back is a reopen, and a reopen empties evidence_since_reopen, so this
+                    # evidence can never be used again. Failing on it cost a resume plus a second
+                    # defer per superseded item (IMP-1241).
+                    notes.append(f"{it.id} ({it.state}): evidence from line {line} has drifted — {msg}")
@@ selftest, after the done-item drift cases
+        checks, r = run(good + [ev("WI-0001", "defer", reason="superseded")])
+        check("IMP-1241: drifted evidence on a deferred item: no failure", checks, [])
+        check("IMP-1241: drifted evidence on a deferred item: noted",
+              any("(deferred)" in n and "drifted" in n for n in r["notes"]), True)
```

## §D — `agents/build-agent.md` (proposed text)

**D.1, step 5 (L98–L99).** Replace *"finds its base by globbing `build/artifacts/<feature>-*/run-build-result.json`, so a result written anywhere else is invisible to it"* with:

> finds its base by reading every `build/artifacts/*/run-build-result.json` and taking the newest SUCCESS whose recorded `config` is this run's config — in any feature's directory, since one config serves several features (`IMP-1240`) — so a result written anywhere else is invisible to it

**D.2, Change-scoped runs (L263–L264).** Replace *"until a result recording a `git_head` exists at `build/artifacts/<feature>-*/run-build-result.json` (step 5)"* with:

> until a result recording a `git_head` for this build config exists under `build/artifacts/*/run-build-result.json` (step 5)

**D.3, manifest check (L412–L416).** Replace the paragraph beginning *"**Pass `--build-config` explicitly whenever…**"* with:

> **Keep `--build-config` in the command; it is the explicit form, and no longer the only thing between you and a red gate.** Without it the script reads the `config` that `run-build.py` recorded in `$ARTIFACT_DIR/run-build-result.json`, and only when that file is absent does it derive `config/<feature>-build.yml` from the manifest's own `feature` field — which, for a feature sharing a parent's build config, names a file that does not exist and stops with `NO BUILD CONFIG` (`IMP-0479`, `IMP-1240`; history → *`--build-config`*).
