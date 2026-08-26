# Dev Summary Document — Revitalise Grant Application Automation (Phase 1)

**Feature Slug:** revitalise-grant-automation
**TAD Reference:** docs/architecture/revitalise-grant-automation-architecture.md (APPROVED 2026-08-10)
**SDD Reference:** docs/plans/revitalise-grant-automation-plan.md (APPROVED 2026-08-10)
**Date:** 2026-08-10 · **revision 0.2 (schema revision pass)** 2026-08-11 · **revision 0.3 (three reviewer answers)** 2026-08-12 · **revision 0.4 (ALM tooling, CI/CD and credentials)** 2026-08-12 · **revision 0.5 (the solution now actually packs)** 2026-08-12 · **revision 0.6 (test-agent fix cycle — D-001 and D-005)** 2026-08-12 · **revision 0.7 (the form already exists — D-003 and D-004)** 2026-08-13 · **revision 0.8 (the scoring methodology is now proved against 25 real applications — D-014 and D-006)** 2026-08-13 · **revision 0.9 (the approved rounding rule is now the rounding the code performs — D-015, D-016, D-017)** 2026-08-13 · **revision 1.0 (post-DEV-deployment defect cycle — D-018, D-019, D-020)** 2026-08-14 · **revision 1.1 (found executing revision 1.0's own fix live — D-021)** 2026-08-14
**Status:** APPROVED (revision 1.1)
**Tier:** standard for revisions 1.0/1.1 (all four defects are deployment/packaging mechanics with a verifiable ground-truth fix, not a domain judgement call — the strategic escalation that applied to revision 0.9 does not apply here). Document-level tier note from 0.9 preserved below for history.
**Tier (revision 0.9 and earlier):** strategic (escalated — a scoring-methodology change affecting a vulnerable population, resolving SDD OQ-002; revision 0.9 stays strategic because it corrects a scoring-correctness defect that can silently skip a required human review)

---

> ## 🎯 Revision 1.1 — found executing revision 1.0's own fix, live against DEV
>
> **Revision 1.0 left one item unverified: "Seed `rev_setting` in live DEV — not yet executed against a
> live environment."** Running that exact command with real credentials is what found this defect —
> which is itself the point of `docs/development/revitalise-grant-automation-dev-deployment-handover.md`:
> a mocked test cannot see a live platform validation rule.
>
> ### D-021 — `rev_description` exceeded Dataverse's own 500-character column limit
>
> **What happened.** `pwsh provisioning/dataverse/seed-settings.ps1 -Env dev`, run for the first time
> against `REV-GrantApplications-DEV` with a real app-only credential (certificate imported from
> `provisioning/certs/REV-Provisioning-SP.pfx`, thumbprint `A6F94E1801D1C62B7A82AE75E1AA5AD243ECC7FE` —
> confirmed live via `WhoAmI`, matching the thumbprint the fifteen-import handover document already
> recorded as "the original... in use"), created/updated 7 of 11 rows and failed 4:
> `LikertPointMap`, `AgeRangeLabelMap`, `MaxCircumstanceScore`, `IncomeBandUpperBoundMap` — each with
> Dataverse's own error, `"The length of the 'rev_description' attribute of the 'rev_setting' entity
> exceeded the maximum allowed length of '500'."` Confirmed against `Entity.xml`:
> `rev_setting.rev_description` really is `MaxLength="500"`. The four failing descriptions ran 523 to
> 2,296 characters — this project's normal, verbose documentation style, exactly the failure class
> already named once before in this same repository (C-TECH-049, the flow-description limit, fifteen-
> import handover §3.2 #7) and never checked here because nothing in the build reads deployment settings
> files, and the mocked Pester harness accepts any string a test hands it.
>
> **This was a LATENT defect in all three environments, not just DEV.** `test-settings.json` and
> `prd-settings.json` carried the identical over-length text for the same four keys (`prd-settings.json`'s
> `IncomeBandUpperBoundMap` description ran to 669 characters) — seed-settings.ps1 had simply never been
> run for real against any environment before this session, per the Dev Summary's own "Still unproven"
> register. TST/ACC and PRD would have hit the same 4-of-11 failure the first time each was seeded.
>
> **Fix, same shape as C-TECH-049's own fix.** Shortened all four descriptions to ≤500 characters in
> **all three** settings files (`dev-scoring-settings.json`, `test-settings.json`, `prd-settings.json`) —
> each keeps the essential fact plus its FR/NFR/OQ/defect citation and a pointer to a new companion file,
> `provisioning/deploymentSettings/settings-rows.notes.md`, which holds the complete original text for
> all four keys, unchanged. No `value` changed — only `description`.
>
> **Regression prevention.** New build gate `scripts/verify-setting-description-length.py`
> (`config/revitalise-grant-automation-build.yml` → `setting-description-length`), checking every
> `settingRows[].description` in every `provisioning/deploymentSettings/*.json` file against the real
> 500-char limit. Verified to catch the regression (reverted `LikertPointMap`'s description on a scratch
> copy — fails naming the file, key and character count) and to pass on the corrected source. Two new
> Pester assertions in `DeploymentSettings.Tests.ps1` cover the same invariant for `test`/`prd` and for
> `dev-scoring-settings.json` specifically.
>
> ### Verification evidence
>
> | Claim | Level | Evidence |
> |---|---|---|
> | `rev_setting` is seeded in live DEV — **the one item revision 1.0 left unverified is now closed** | **V3+ accepted and confirmed by direct query** | `seed-settings.ps1 -Env dev` re-run after the fix: `CREATED` for all 4 previously-failing rows, `EXISTS` (upserted) for the 7 that succeeded first time. Live FetchXML against `rev_setting` in DEV, post-run: **all 11 rows present with the correct values** (e.g. `KnockoutThreshold=20`, `LikertPointMap={"1":5,...,"6":0.5}`) |
> | The fix does not regress the other 7 rows or any other environment file | Unit | Full Pester suite: **645 tests, 644 passed, 1 skipped (pre-existing, unrelated D-011)**, 0 failed |
> | New build gate is real, not decorative | Manual (scripted) | Ran against the fixed files (PASS, 33 rows across 7 files) and against a deliberately-reverted copy (FAILS, names the file/key/length) |
>
> **Revision 1.0's D-018/D-019 items remain exactly as recorded there** (V4 human open-and-save on the
> four forms; the two multi-select fields added via the maker portal) — this revision closes only the
> settings-seeding item and the new defect found while closing it.
>
> ---

> ## 🎯 Revision 1.0 — reported after DEV deployment: no views, no forms, empty rev_setting
>
> **Three defects reported directly by the reviewer after working with the deployed DEV app** (not
> found by test-agent): the four tables have no views, no forms, and `rev_setting` has zero rows even
> though `REV | Scoring | Calculate & Flag` reads it on every run. All three are fixed here, ground-truthed
> against live DEV, and re-verified by a real solution import — not by argument.
>
> ### D-018 — Views not created: content existed on disk, `pac solution pack` dropped it silently
>
> **Root cause.** Every one of the four `Entity.xml` files was missing two empty marker elements,
> `<FormXml />` and `<SavedQueries />`. Without them, `pac solution pack` silently ignores that entity's
> entire `SavedQueries/` folder — no warning, no error, a clean pack and a clean import that ships zero
> views. This was not a hypothesis: proved by direct experiment (pack the same source with and without
> the two lines; packed `<savedquery>` count for `rev_application` went from 5 to 0 with nothing else
> changed) and confirmed against a real DEV export, which carries the same two elements on every entity
> Dataverse itself created. All 8 `SavedQueries/*.xml` files under `Entities/*/SavedQueries/` had been
> correctly authored since the original build — they were never missing content, only unreachable.
>
> **Fix.** Added `<FormXml />` and `<SavedQueries />` before `</Entity>` in all four `Entity.xml` files,
> with a comment recording why (`src/solutions/RevitaliseGrantAutomation/Entities/rev_applicant/Entity.xml`
> carries the full rationale; the other three point to it). No SavedQueries content changed.
>
> ### D-019 — Forms not created: no `FormXml` content existed at all, for any of the four tables
>
> **Root cause.** Unlike views, this was not a packaging defect — no `FormXml/` folder existed anywhere
> under `Entities/` before this revision. Dataverse's own auto-generated default Main form for a new
> custom table (created via `EntityDefinitions` by `ensure-schema.ps1`) has only the primary name column
> and `ownerid` — confirmed live: DEV's own default `rev_application` form had exactly two controls,
> `rev_name` and `ownerid`, out of 87 columns on that table. That is what "no forms" actually looked like
> to the reviewer: a form technically present but with almost nothing on it.
>
> **Fix.** Authored a Main form for all four tables (rev_applicant: 18 fields across 3 sections;
> rev_application: 85 of 87 fields across 6 tabs / 14 sections — see the two omissions below;
> rev_setting: 5 fields; rev_errorlog: 9 fields across 2 sections), generated from the field list in each
> `Entity.xml` by `formgen/gen.py` (kept in the build scratch, not shipped — the *output* is the shipped
> artefact, same as any other generated solution XML in this repo).
>
> **Every control classid is ground-truthed, not recalled from memory** (`skills/how-to-verify-a-platform-
> contract.md`), following this project's own hard lesson (the fifteen-import handover document, §6): each
> one was read back from two REAL, live `systemform` records in REV-GrantApplications-DEV via
> `pac env fetch` — the OOB `Contact` main form (text, email, lookup, optionset, datetime, two-option,
> memo, currency controls) and the OOB `Account` main form (whole-number control, and confirmation of
> currency/optionset/text). No classid in the four new forms was written from memory.
>
> **Two fields are deliberately left off both forms needing them** (`rev_conditionprofile` on
> `rev_application`, `rev_supportrecipientconditionprofile` on `rev_application` — both
> `multiselectpicklist`): no live `systemform` anywhere in this tenant uses a Multi-Select Option Set
> control, so no ground-truth classid could be read back for it, and per the same skill, a guessed
> classid for a structural form element is exactly the failure class that cost fifteen import attempts
> earlier in this engagement. **Outstanding — same shape as the two calculated columns in the fifteen-
> import handover document's §4 item 2:** add both fields to the `Application` main form via the maker
> portal's field picker (drag-and-drop), which the platform resolves correctly by itself. Two fields,
> ~30 seconds, no source change needed once done — the live form's own shape becomes the ground truth for
> a future hand-authored attempt, exactly as the Contact/Account forms did here.
>
> ### D-020 — `rev_setting` has zero rows in DEV; `REV | Scoring | Calculate & Flag` has nothing to read
>
> **Root cause.** `provisioning/dataverse/seed-settings.ps1` was wired into
> `config/revitalise-grant-automation-pipeline.yml` for the `test` and `prd` stages only — never for
> `dev`. Confirmed live: a FetchXML query against `rev_setting` in REV-GrantApplications-DEV returned "No
> results returned." Every flow action that reads a threshold or a point map — every such action in
> `REV | Scoring | Calculate & Flag` — had nothing to read.
>
> **Why DEV had no settings file at all.** Phase 1 deliberately has no `dev-settings.json`:
> `Get-ProvisioningSettings -Env dev` throwing "file not found" is a real, tested invariant
> (`ProvisioningCommon.Tests.ps1`) that `verify-role-bindings.ps1` and `ensure-bulk-delete-jobs.ps1` rely
> on as the signal that DEV has no group-team bindings or retention jobs scripted against it. Simply
> creating `dev-settings.json` would have broken that invariant.
>
> **Fix, mirroring the pattern `ensure-schema.ps1` already established for the identical problem**
> (its own header: "NOT `Get-ProvisioningSettings -Env dev`... reads its own, separately-named file
> instead"): `seed-settings.ps1 -Env dev` now reads a dedicated
> `provisioning/deploymentSettings/dev-scoring-settings.json` directly, never through
> `Get-ProvisioningSettings`. The eleven setting rows in it are copied from `test-settings.json` verbatim
> (same PROVISIONAL `KnockoutThreshold`/`BorderlineBandLower`/`BorderlineBandUpper`/`IncomeCeiling`
> figures already accepted for TST/ACC), so DEV and TST/ACC score identically — SDD OQ-001/002/003 remain
> open for the board, i.e. for PRD only, exactly as before. Wired into
> `config/revitalise-grant-automation-pipeline.yml`'s `tenant_prerequisites.operations`, immediately after
> `ensure-schema.ps1 -Env dev` and behind the same `APPROVE TENANT` gate — both are one-time DEV setup
> that Power Platform Pipelines does not perform.
>
> ### Regression prevention — new build gate closes the class, not just the instance
>
> D-018 is a **"packs clean, ships nothing"** defect — the same failure class as five of the six
> solution-import root causes in the fifteen-import handover document, and the reason that document's
> own transferable lesson exists. `scripts/verify-forms-and-views-reachable.py` (new, wired into
> `config/revitalise-grant-automation-build.yml` as `forms-and-views-reachable`, directly after
> `root-components-resolve`) asserts, for every entity, that a non-empty `FormXml/` or `SavedQueries/`
> folder has a matching marker element in `Entity.xml`, and flags the reverse (a marker with no content)
> as a warning. Verified to catch the exact regression: reverted to the pre-fix `Entity.xml` on a scratch
> copy, the new gate fails naming the entity, the folder and the exact fix; against the corrected source,
> it passes.
>
> ### Verification evidence (C-TECH-053 — report only the level actually executed)
>
> | Claim | Level | Evidence |
> |---|---|---|
> | Solution packs cleanly with all fixes | **V2 packaged** | `pac solution pack` — 0 new warnings beyond the four pre-existing, already-accepted root-component exclusions |
> | All 8 views and all 4 forms are **byte-identical between source and the packed solution** | V2 | Round-trip `pac solution pack` → `pac solution unpack`: identical `SavedQueries`/`FormXml` file layout, same GUIDs, only cosmetic BOM/`xmlns:xsi` differences (`pac`'s own unpack convention, confirmed against the DEV export too) |
> | **The fixed solution was re-imported into the live DEV environment** (`REV-GrantApplications-DEV`) and published | **V3 accepted** | `pac solution import --async --force-overwrite --publish-changes` — both the import and the publish async operations completed successfully (see console output timestamped 2026-08-14) |
> | **All 8 views and all 4 forms exist in DEV with exactly the source GUIDs** | V3, verging on V4 | Live FetchXML queries against `savedquery` and `systemform` in DEV, post-import: all 8 `savedqueryid`s and all 4 `formid`s match source exactly (e.g. `Application` main form `{6a6004bd-bba9-498b-8ca4-fafdd254bded}`, `Active Applications` view `{e5a7b9c1-6002-4a2b-8c11-0a1b2c3d4e52}`) |
> | `rev_setting` seeding fix | **Unverified against live DEV — V0** | The fix is written, unit-tested (below) and packs/parses cleanly, but was **not run against live DEV in this session**: it needs `PROVISION_APP_ID`/`PROVISION_CERT_THUMBPRINT` credentials this session did not hold safely. See §4 (Outstanding) for the one command to run it |
> | seed-settings.ps1's new `-Env dev` branch | Unit (mocked API) | 2 new Pester tests in `DataverseScripts.Tests.ps1` (missing-file fail-fast naming the dedicated file, not `dev-settings.json`; successful seed via `-SettingsPath` override) — both pass |
> | Full regression | Unit | Full suite: **643 tests, 642 passed, 1 skipped (pre-existing, unrelated D-011)**, 0 failed |
>
> **V4 (a named person opens and saves each form/view in the designer) has NOT been performed.** The
> live-DEV FetchXML confirms the components exist with the intended shape (V3, and materially more than
> V3 since the exact source GUIDs round-tripped through a real import); it does not prove a human can
> open the `Application` form in the browser and save it without a designer-side error, which is exactly
> the class of failure §3.2 of the fifteen-import handover document warns survives a clean import. **This
> is the one remaining step before revision 1.0's fixes can be called fully proven**, alongside actually
> running the settings-seeding script.
>
> ### Outstanding, with exact commands
>
> | # | Task | Command / location |
> |---|---|---|
> | 1 | **Seed `rev_setting` in live DEV** — the one fix not yet executed against a live environment | `PROVISION_APP_ID=<app id> PROVISION_CERT_THUMBPRINT=<thumbprint> pwsh provisioning/dataverse/seed-settings.ps1 -Env dev` |
> | 2 | Open the `Application`, `Applicant`, `Setting` and `Error Log` main forms in the DEV maker portal and save each once (V4) | Maker portal → REV Grant Administration app → each table → Forms → Main → Save |
> | 3 | Add `rev_conditionprofile` and `rev_supportrecipientconditionprofile` to the `Application` main form | Maker portal form designer → field picker → drag onto the *Support Needs* tab (both fields already exist on the table; this is a form-layout addition only) |
>
> ---

> ## 🎯 Revision 0.9 — the rounding rule was approved, and the code did not implement it
>
> **One line of the scoring flow, and it was deciding outcomes the wrong way.** Revision 0.8 rounded
> the circumstance score with `int(formatNumber(<total>, 'F0'))` and justified it, in the expression's
> own description, on the grounds that `'F0'` "rounds half away from zero". **That claim was false and
> had never been executed.** Test-agent's retest found it (D-015, P2). Two smaller documentation
> defects came with it (D-016, D-017). All three are fixed here.
>
> ### D-015 — what was wrong, established by execution rather than by argument
>
> .NET formats a **double** at an exact midpoint by rounding **half to even**, not half away from
> zero. Run on .NET 10.0.10 — the same major family `pac 2.4.1` reports:
>
> | Exact total | `(double).ToString("F0")` | `Math.Round(x, 0)` | Approved rule (half up) | |
> |---|---|---|---|---|
> | 0.5 | **0** | 0 | 1 | ❌ |
> | 1.5 | 2 | 2 | 2 | ✅ |
> | 2.5 | **2** | 2 | 3 | ❌ |
> | 3.5 | 4 | 4 | 4 | ✅ |
> | **20.5** | **20** | 20 | **21** | ❌ |
> | 21.5 | 22 | 22 | 22 | ✅ |
> | **30.5** | **30** | 30 | **31** | ❌ |
> | **37.5** | 38 | 38 | 38 | ✅ |
>
> **It agrees with half-up only when the whole part is ODD.** That is why it went unnoticed: `37.5 →
> 38` is the example the description used, the review checklist quoted, and the reviewer approved —
> and 37 is odd, so it was right. **Every even case was wrong.**
>
> **The harm was specific, and it was the exact harm revision 0.8 had just fixed one action
> downstream.** With the TST/ACC values in force (knockout ≤ 20, band 21–30), an applicant scoring an
> exact **20.5**:
>
> | | Stored score | Status | What happens to the applicant |
> |---|---|---|---|
> | **Before this fix** | 20 | **4 Auto-reject** | Application leaves the active list. No human ever sees it |
> | **Approved rule / after this fix** | 21 | **3 Borderline** | **Routed to Emily for a human decision** |
>
> Nothing threw and nobody was alerted, because 20.5 is a perfectly scoreable total — FR-022's
> fail-closed design cannot help here. Worse, `rev_scorebreakdown` — the stored, trustee-facing
> evidence a decision is defended with — told the reader in plain English that *"halves are rounded
> UP, in the applicant's favour"*. **The record asserted the opposite of what the code did.**
>
> ### The fix, and why it is this rather than a rounding function
>
> ```
> - @int(formatNumber(outputs('Calculate_circumstance_score'), 'F0'))
> + @int(formatNumber(add(outputs('Calculate_circumstance_score'), 0.25), 'F0'))
> ```
>
> The Logic Apps expression language has no `round()`, `ceiling()` or `floor()` — that genuine
> platform gap is why formatting was used at all, and it has not gone away. So instead of *relying* on
> the formatter's midpoint mode, **the fix removes the dependency**: `+0.25` moves the value off the
> midpoint before the formatter ever sees it.
>
> - `.0` and `.5` are the **only** fractional parts that can arise (0.5 is the only non-integer point
>   value), so there are exactly two cases: `X.0 + 0.25 = X.25 → X`, and `X.5 + 0.25 = X.75 → X+1`.
> - `0.25` is strictly inside `(0, 0.5)`: big enough to carry every half past the midpoint, too small
>   to carry a whole total up.
> - `0.25` and `0.5` are exact binary fractions, so nothing rests on floating-point luck — `20.5 +
>   0.25` is exactly `20.75`.
> - **Verified over every total the flow can produce** — 0.0 to 60.0 in halves, 121 values — **and
>   under both .NET numeric types**, because `decimal.ToString("F0")` rounds half *away from zero*
>   where `double` rounds half *to even*. **Zero mismatches either way.** The fix is therefore correct
>   whichever type the runtime uses and whichever midpoint mode a future runtime adopts.
>
> ### The test that would have caught it, and that now cannot be quietly removed
>
> **17 new assertions** (`ScoringInvariants.Tests.ps1` → *"D-015 — the rounding the flow PERFORMS is
> the round-half-up rule the reviewer approved"*), plus two harness helpers. The suite now **executes**
> .NET's own `F0` formatting through the offset **read out of the shipped expression** — so deleting
> the offset changes what the test computes, and the test fails.
>
> **Mutation-tested, because a regression test that cannot regress proves nothing.** Reverting *only*
> the expression to its pre-0.9 form, leaving tests and description untouched:
>
> | Assertion | Result against the OLD expression |
> |---|---|
> | structural guard — the formatter is never handed a midpoint | ❌ **FAILS** |
> | after the offset, no total lands on `.0` or `.5` | ❌ **FAILS** |
> | all 121 reachable totals round half up | ❌ **FAILS** |
> | `20.5 → 21` · `30.5 → 31` · `0.5 → 1` · `2.5 → 3` | ❌ **FAIL** |
> | `37.5 → 38` · `21.5 → 22` | ✅ pass — **odd whole part; these are the cases that hid the defect** |
> | whole totals `0 → 0` · `5 → 5` · `60 → 60` | ✅ pass — correctly unaffected |
>
> That last row is the point of the exercise: the mutation reproduces the original defect **exactly**,
> including which cases looked fine.
>
> **Two assertions deliberately, because one of them can rot.** The *behavioural* one fails today if
> the offset goes. The *structural* one — an offset exists and lies inside `(0, 0.5)` — keeps biting
> even on a hypothetical future runtime that rounds half away from zero, where the behavioural test
> alone would go quiet. .NET's midpoint formatting has changed across versions before; nothing in this
> repository pinned it, and now nothing needs to.
>
> ### D-016 — "disjoint" was not merely imprecise, it argued against its own design
>
> The two wellbeing scales' label sets were described as **disjoint**. They are not: they **share
> "Not sure"** (value 6) as their one common value. This matters more than a wording nit, which is why
> it was worth correcting rather than noting — **the shared value is precisely why one shared
> `LikertPointMap` is correct.** The flow looks the map up by numeric option value and never knows
> which option set an answer came from, so a shared value *must* resolve to a shared point value.
> Calling the sets disjoint undercut the argument for the design it was introducing.
>
> Corrected in `Other/Solution.xml` (ships) and Dev Summary §4.2. The two option-set XML descriptions
> and the Pester suite were **already accurate** ("disjoint apart from 'Not sure'") and are unchanged.
> **`manifest.json` does not contain the word** — the retest attributed it there, but build #3's note
> says only that the three questions "use agree/disagree labels, not the frequency scale", which is
> accurate; nothing needed changing.
>
> ### D-017 — §9 Test Guidance had not been updated for revision 0.8
>
> **`agents/test-agent.md` directs test-agent to load §9 on activation, so a stale row there does not
> merely mislead — it gets asserted.** A tester following it literally would have asserted a reachable
> floor of **10** against a build whose floor is **5**, and **failed a correct build.** Where §9 and
> the shipped suite disagreed, **the suite was right every time.**
>
> | §9 said | Reality since revision 0.8 |
> |---|---|
> | minimum reachable score is **10** | **5** — ten "Not sure" at 0.5 plus a zero inversion |
> | FR-022 gate withholds on **emptiness** | **absent *or* not a key of the configured map**, on all eleven scored answers |
> | `LikertPointMap` covers `rev_likertresponse` | **both** wellbeing option sets, incl. value 6 = 0.5, the only non-integer |
> | §9.3 had **no case** for a fractional total, a midpoint, or the rounded-vs-unrounded status | six new cases, led by **20.5 → 21 → Borderline** |
> | "fifteen global option sets" | **sixteen** (`rev_agreementresponse` added in 0.8) |
> | "Ten `rev_setting` rows" · "six policy rows" · "20 provisioning scripts" | **eleven** · **seven** · **22** |
> | `LikertPointMap` "Value unchanged in revision 0.3" | key `"6"` was added in 0.8 |
>
> §9.6 also gained a standing rule: **when a revision changes scoring behaviour, that list is part of
> the change, not documentation of it.**
>
> **One item from D-017 deliberately NOT changed, and why.** The retest flagged "35 root components"
> in three places. All three are **historical evidence blocks** — revision 0.5's pack evidence,
> revision 0.3's re-run record, and revision 0.3's review checklist — where 35 was the true figure at
> the time. Rewriting them to 36 would falsify the record rather than correct it. The current figure
> (**36**, verified this revision) is stated in the revision 0.8 banner and re-verified below.
>
> ### Proof, not assertion
>
> | Gate | Result |
> |---|---|
> | Pester suite | **577 passed, 0 failed, 1 skipped** (was 560 — **+17 new**) |
> | Coverage | **92.60%** over `provisioning/{common,entra,dataverse}`, threshold 80 (C-TECH-014) |
> | New tests mutation-tested | **Confirmed fail-then-pass** — see the table above; 7 of 17 fail against the old expression, and the ones that pass are exactly the odd-whole-part cases |
> | `pac solution pack` **Managed** | **Packed Solution.**, exit 0 · `<Managed>1</Managed>` · fixed expression confirmed **inside the zip** |
> | `pac solution pack` **Unmanaged** | **Packed Solution.**, exit 0 · `<Managed>0</Managed>` · ditto |
> | `secret-scan` as the config runs it | `gitleaks detect --source . --no-git --no-banner --redact --exit-code 1` → 3.17 MB scanned, **no leaks found, exit 0** |
> | `source-validate` | **44** XML files well-formed, **4** flow definitions parse |
> | `root-components-resolve` | PASS — **36** root components, both directions |
> | `field-security-coverage` | PASS — 34 secured columns, 1 reviewed exemption |
> | FR-016 / C-TECH-047 / no-hardcoded-thresholds grep gates | PASS |
>
> **⚠️ `manifest.json` is now stale, and it is build-agent's to re-issue** — it still records build #3
> / revision 0.8 and that build's zip hashes. `development-agent` does not write build records, so no
> hash is quoted here, and there is a specific reason not to:
>
> **🆕 The zip byte-hash is NOT reproducible across packs, though the content is — verified this
> revision, and it affects how the hash check should be read.** Packing the *same* source twice
> produces two different SHA-256 values. Opening both archives and comparing entry by entry:
> **every entry's content is byte-identical** (`CONTENT of every entry identical: True`,
> `entries differing in content: NONE`) and **7 entries differ only in their embedded modification
> timestamp** — `pac solution pack` stamps file mtimes into the archive. So a recorded hash certifies
> *the archive produced by one specific pack run*, not the source it was packed from. The retest's
> "read from both packed zips, whose hashes match `manifest.json`" is therefore only meaningful
> against the zips that build-agent's own run produced — which is fine and is how the pipeline works,
> but it means **a hash mismatch after an independent re-pack is expected and is not evidence of
> tampering or drift.** The check that *is* meaningful across runs is the one used above: unpack both
> zips and assert the expression inside them. Done, and it reads
> `@int(formatNumber(add(outputs('Calculate_circumstance_score'), 0.25), 'F0'))` in both.
>
> ### What this revision deliberately did NOT do
>
> - **It did not change the rounding RULE, only the code that was failing to implement it.** Round
>   half up remains the reviewer-approved judgement call, with the alternative (a decimal
>   `rev_circumstancescore`) still on the table and still preferable if the reviewer wants exactness.
>   The **D-015 fix is required either way**, because today the code matches neither option.
> - **It did not change any option value, point value, threshold or map.** `LikertPointMap` is
>   byte-identical across both environments and unchanged in value; only its description gained the
>   note that the `+0.25` offset depends on 0.5 being the finest point value.
> - **It did not close D-016's actual entry in the retest register.** The register's D-016 is a
>   *different* item — which of two contradictory observations about the live form offering "Not sure"
>   on the seven SWEMWBS questions is stale. **That needs the live form, not a developer**; it is §8
>   case 8 and stays open under the D-008 mapping work. What is fixed here is the "disjoint" wording,
>   which the retest raised alongside it.
> - **It did not run anything against a live environment.** The rounding is now correct arithmetic on
>   an executed .NET formatter; that the Power Automate runtime binds `formatNumber` to that formatter
>   remains untested, which is why §9.3's midpoint case is written to be run on first import.

---

> ## 🎯 Revision 0.8 — ground truth arrived, and it corrected the scoring engine in two ways
>
> **25 real applications, each with the score the process owner reached by hand and the eleven
> answers that produced it, arrived as `docs/Import/Book(Sheet1).csv`.** For the first time the
> scoring methodology could be checked rather than described. It reproduces exactly — and getting
> to "exactly" required correcting two things this build had wrong, one of which was losing real
> applications.
>
> ### The verification, done independently before anything was changed
>
> Reconstructing the published total from the eleven answers reproduces it **exactly on all 25
> rows**:
>
> **Total = (10 − life_satisfaction_raw) + Σ points(7 SWEMWBS answers) + Σ points(3 "last year" answers)**,
> with `points = {1:5, 2:4, 3:3, 4:2, 5:1, 6:0.5}`.
>
> Three corroborations, because a formula that fits can still fit for the wrong reason:
>
> | Check | Result |
> |---|---|
> | Competing direction — agreement scale reversed (*Strongly Agree* = position 1) | reproduces **7 of 24** answerable rows |
> | Competing direction — point map not inverted (`1:1 … 5:5`) | **3 of 24** |
> | Competing direction — life satisfaction not inverted | **4 of 24** |
> | Theoretical maximum under the confirmed map | **10 + (10 × 5) = 60** — exactly what the export header has always called it |
>
> So the direction is **established, not assumed**: every alternative reading fails on most rows.
> This is now a permanent assertion, not a one-off analysis — `ScoringInvariants.Tests.ps1` →
> *"OQ-002 — the scoring configuration reproduces 25 REAL hand-scored applications exactly"*
> reconstructs all 25 rows **through the shipped artefacts themselves**: labels resolved from the
> option-set XML, points from the `LikertPointMap` settings row, the inversion from
> `FeelingScaleInversion`. Edit any of them into disagreement with reality and the suite fails.
>
> ### Finding 1 — the ten wellbeing questions use TWO response scales, not one
>
> Revision 0.3 relabelled all ten uniformly to the frequency wording and recorded that as
> settled. **It was half wrong.** The CSV shows:
>
> | Questions | Stem | Answers recorded in the export |
> |---|---|---|
> | 7 SWEMWBS items (cols 96–102) | *"…over the last 2 weeks"* | None of the time / Rarely / Some of the time / Often / All of the time |
> | 3 "last year" items (cols 103–105) | *"Thinking about the last year, have you been able to…"* | **Strongly disagree / Disagree / Neutral / Agree / Strongly agree** |
>
> Across all 25 rows the two label sets are **disjoint apart from "Not sure"** — no frequency
> label ever appears in columns 103–105 and no agreement label ever appears in 96–102. Revision
> 0.3's own justification ("the only wording that reads correctly against the live form's own
> stem") is true of the seven and false of the three, because they have different stems.
>
> **Why this mattered even though no score changes.** The ordinal values coincide, so the
> arithmetic was never wrong. What was wrong was the **evidence**: an applicant who *strongly
> disagreed* that they had managed a break when they needed one was recorded, in
> `rev_scorebreakdown` and every trustee-facing view, as having had one **"None of the time"** — a
> different sentence about a real person, in the document the charity uses to justify a decision.
>
> ### Finding 2 — "Not sure" is a real answer worth exactly 0.5 points (D-014)
>
> The live form offers **"Not sure"** on all ten questions. Row 25 is an application that chose it
> for every one, and scored **9**. Solving rather than assuming:
>
> ```
> published total                     9
> life-satisfaction raw 6 → 10 − 6 =  4
> residual across 10 "Not sure"    =  5   →  5 / 10 = 0.5 per answer, exactly, no remainder
> ```
>
> **This reframes D-014 completely.** D-014 was raised as *"the live form can send answers the
> schema cannot store"* and its recommended remedy was an interim reject-and-flag guard. But
> "Not sure" was never malformed input — **it is a valid choice a real applicant made, and the
> charity already scores it.** Rejecting it would have been rejecting a person's honest answer.
> The fix is to make it storable and scoreable.
>
> **The precise mechanism of the loss, for the record:** `rev_likertresponse` had five options, so
> a "Not sure" answer could not be stored at all; and `LikertPointMap` had no key `6`, so the
> scoring flow's `int(string(map?[response]))` was called on an empty lookup and **threw**. The
> application was created and then the run died — an accepted submission with no score, no status
> and nobody told.
>
> ### What changed
>
> | | Change | Where |
> |---|---|---|
> | **1** | **`rev_likertresponse` gains value 6 "Not sure"**, and is narrowed to the seven SWEMWBS items | `OptionSets/rev_likertresponse.xml` |
> | **2** | **New `rev_agreementresponse`** — 1–6, Strongly Disagree … Strongly Agree, Not sure. `rev_wellbeinganswer8/9/10` rebound to it; declared as a root component | new `OptionSets/rev_agreementresponse.xml`, `Entity.xml`, `Other/Solution.xml` |
> | **3** | **`LikertPointMap` gains `"6":0.5`** in both settings files. **One map still serves both scales** — verified, see below | `test-settings.json`, `prd-settings.json` |
> | **4** | **The flow no longer throws on a fraction:** `likertPoints` is now `float`, the cast is `float()` not `int()`, and a new `Round_the_circumstance_score` rounds once at the end | the scoring flow |
> | **5** | **`Derive_status` now reads the ROUNDED score** — see the correctness note below, this one is not cosmetic | the scoring flow |
> | **6** | **The FR-022 withhold gate widened** from "absent" to "absent **or** not a key of the map", on **all eleven** scored answers — including the life-satisfaction answer, which had the identical hole (D-014's TC-317 half) | the scoring flow |
> | **7** | **Intake trigger schema bounded** — `wellbeing_answer_1`–`10` are `minimum: 1, maximum: 6`; `feeling_scale_answer` is `0`–`10`. There were **no bounds at all** before | the intake flow |
> | **8** | **D-006 fixed for real** — `--no-git` added to the `secret-scan` gate | `…-build.yml` |
> | **9** | **23 new Pester assertions**, including the 25-row reconstruction and three new harness helpers | `ScoringInvariants.Tests.ps1`, `SolutionSource.psm1` |
> | **10** | **SDD Amendment A-01 raised** — resolving OQ-002, *not* OQ-001. Raised as a proposed amendment, not a silent edit | `…-plan.md` |
>
> ### Verified, not assumed: one point map serves both option sets
>
> The instruction to check this was worth following. The flow's lookup is
> `outputs('Parse_likert_point_map')?[string(item()?['response'])]` — **keyed by the numeric
> option value, with no reference to which option set the answer came from.** Both scales use
> ordinals 1–6 with position 1 as the highest-need answer, so one map is correct and a second
> would only be a second place for the same numbers to drift apart. Two assertions now hold that
> invariant: the map must cover `rev_agreementresponse`'s values as well as `rev_likertresponse`'s,
> and the two option sets must have **identical value sets and different labels for positions 1–5**.
>
> ### ⚠️ A JUDGEMENT CALL THE REVIEWER MUST CONFIRM OR OVERRIDE — the rounding rule
>
> **The problem.** `rev_circumstancescore` is `<Type>int</Type>`. With "Not sure" worth 0.5, an
> **odd** number of "Not sure" answers produces an X.5 total. Row 25 hid this: it answered "Not
> sure" **ten** times, and 10 × 0.5 is a whole number, so the fractional case does not appear
> anywhere in the ground-truth data and had to be reasoned about rather than read off. A
> submission with three "Not sure" answers and otherwise integer answers totals e.g. **37.5**.
>
> **What I implemented: round half up (37.5 → 38).**
>
> > ⚠️ **CORRECTED IN REVISION 0.9 — this sentence was not true when it was written.** The *rule*
> > below is unchanged and still approved; the *code* did not implement it. `formatNumber(…,'F0')`
> > rounds half **to even**, so 37.5 → 38 was right and 20.5 → 20 was wrong. See the revision 0.9
> > banner (D-015). Everything else in this section — the reasoning, the rejected alternatives, the
> > judgement-call framing — stands as written and is what the reviewer approved.
>
> **Reasoning, so it can be argued with:**
> - **Half up is the only rounding case that can ever arise.** The fractional part is either `.0`
>   or exactly `.5` — never anything else — so the rule is fully determined by one decision and
>   can be explained to a trustee in one sentence. A test asserts 0.5 remains the only
>   non-integer in the map, so that reasoning cannot silently stop being true.
> - **Up favours the applicant.** A higher score means greater need, and knockout fires *at or
>   below* the threshold. Rounding down would let a rounding artefact — on the answers of the
>   applicants *least certain about their own wellbeing* — be the thing that knocked them out.
> - **Nothing is lost either way:** the exact unrounded total is written into
>   `rev_scorebreakdown` alongside the rounded one, with a plain-English sentence explaining the
>   half point when there is one.
>
> **Why this is a judgement call and not a derivation, stated plainly: the data does not settle
> it.** Every published total in the CSV is a whole number and the only "Not sure" row is whole by
> coincidence, so there is **no evidence of how Emily rounds by hand.** I could not resolve this
> from the data and did not pretend to.
>
> **The alternative I considered and did not take:** change `rev_circumstancescore` to a decimal
> column and store 37.5 exactly. That is the most faithful option and I rejected it *for this
> revision only*, because it is a schema change with a real blast radius — column type, the views,
> the daily summary aggregation, the trustee pack, and `MaxCircumstanceScore`'s "n out of N"
> rendering — and it deserves to be done deliberately rather than as a side effect of a defect
> fix. **If the reviewer prefers exactness over an int column, say so and it becomes the fix.**
> A third option, truncation, was rejected outright: it is biased against the same applicants and
> is indistinguishable from the bug being fixed.
>
> ### A correctness point found while implementing the rounding
>
> `Derive_status` compared the **unrounded** score against the thresholds while the **rounded**
> score was written to the record. That is not a cosmetic mismatch. With a borderline lower bound
> of 37, an exact total of 36.5 is not ≥ 37 and falls through to **Auto-pass**, while the **37**
> actually stored *is* inside the band and is **Borderline** — a human review that would have been
> silently skipped, on a record whose own score says it should have happened. `Derive_status` now
> reads `Round_the_circumstance_score`, so the number that decides the outcome is the number
> stored. Asserted by two tests.
>
> ### The breakdown text still reads sensibly — checked, as instructed
>
> The per-answer line went through `int()`, which would have rendered a 0.5 answer as **"0
> points"** while the arithmetic above it correctly counted 0.5 — the evidence and the score
> disagreeing by half a point per "Not sure" answer, in the artefact a decision is defended with.
> The line now renders the map value directly and **names value 6**, because a lone fractional
> line among nine whole ones reads as a defect to whoever queries it:
>
> ```
> Wellbeing answer 8: response 6 (Not sure) = 0.5 points
> ...
> Exact total before rounding = 37.5
> Rounded to 38. A half point arises when an odd number of answers is "Not sure", which is
> worth 0.5 points; halves are rounded UP, in the applicant's favour, because a higher score
> means greater need.
> ```
>
> ### ⚠️ OQ-001 was not resolved — and the request to resolve it was mis-scoped
>
> This cycle was commissioned as *"resolve OQ-001 (exact scoring weights)"*. **OQ-001 is not the
> scoring weights.** In the SDD it reads *"Where should the knockout cut-off score sit, and how
> wide is the borderline band?"* — the weights are **OQ-002**. The CSV resolves OQ-002 and cannot
> resolve OQ-001: it contains scores and answers but **no accept/reject outcomes**, so there is
> nothing in it from which a cut-off could be inferred. **OQ-001 stays open with the board.** I
> have resolved OQ-002 instead and said so explicitly rather than quietly relabelling the work.
>
> **But the new evidence does change one input to the board's OQ-001 decision, and they need it:**
> the reachable **floor** of a fully answered application has dropped **from 10 to 5** (ten "Not
> sure" answers at 0.5, plus maximum reported life satisfaction contributing 0). A knockout
> threshold at or below 5 was previously unreachable and now is not. Two tests that asserted the
> old floor of 10 were updated — they were asserting something that is no longer true.
>
> ### Why the SDD was amended rather than edited
>
> `docs/plans/…-plan.md` carries **Status: APPROVED** and is `plan-agent`'s artefact, gated on a
> human `APPROVED`. `agents/WORKFLOW.md` defines no procedure for amending an approved upstream
> document, and `development-agent` has no authority to re-issue one — so rewriting FR-013 in
> place would have made an approved document say something nobody approved. Instead: **Amendment
> A-01, marked PROPOSED**, carrying the evidence, the proposed replacement FR-013 wording and
> acceptance criterion, and a request that lead-agent route it to plan-agent. The original FR-013
> text is left intact with a pointer. **This also closes the substance of D-009**, which flagged
> exactly this stale FR-013 wording — and the CSV shows D-009 was more subtle than recorded: the
> agree/disagree labels it called stale are *correct for three of the ten questions*.
>
> ### Proof, not assertion
>
> | Gate | Result |
> |---|---|
> | Pester suite | **560 passed, 0 failed, 1 skipped** (was 537 — **+23 new**) |
> | Coverage | **92.6%** over `provisioning/**`, threshold 80 |
> | `pac solution pack` **Managed** | **Packed Solution.** `<Managed>1</Managed>`, both option sets present with all six options |
> | `pac solution pack` **Unmanaged** | **Packed Solution.** `<Managed>0</Managed>`, ditto |
> | `secret-scan` **as the config now runs it** | `gitleaks detect --source . --no-git …` → ≈3.06 MB scanned, **no leaks found, exit 0** (the byte figure drifts by a few KB between runs because these documents are themselves inside the scan scope; the load-bearing part is *no leaks* and *exit 0*) |
> | `root-components-resolve` | PASS — **36** root components (was 35), all resolve both ways |
> | `field-security-coverage` | PASS — 34 secured columns, 1 reviewed exemption |
> | FR-016 / C-TECH-047 / FR-017 grep gates | PASS |
>
> **The new tests were mutation-tested rather than trusted.** Setting `LikertPointMap["6"]` to `1`
> fails **4** assertions including the 25-row reconstruction; rebinding `rev_wellbeinganswer8`
> back to `rev_likertresponse` fails the binding assertion. A test suite that passes is not
> evidence until you have seen it fail for the right reason.
>
> ### What this revision deliberately did NOT do
>
> - **It did not change the option VALUES of anything.** Positions 1–5 keep their meaning on both
>   scales, so any integration already sending these numbers correctly needs no change. Only
>   labels, a sixth option, and the handling of a fraction changed.
> - **It did not touch the other 30-odd unmapped form columns or the five mismatched option sets**
>   carried over from revision 0.7 — same reasoning as there: those need Emily.
> - **It did not close OQ-001, D-002 or D-004.** None is closable by development-agent.

---

> ## 🔁 Revision 0.7 — the form was never going to be built, because it already exists
>
> **The premise underneath three earlier revisions of the form document was wrong, and correcting it
> exposed a defect in the intake flow that would have rejected every real application.** That is the
> whole of this revision: one corrected premise, one code fix that follows from it, and one honest
> refusal to close a defect that cannot be closed without an audit nobody has run.
>
> ### The premise, and why it was wrong
>
> `docs/development/revitalise-grant-automation-form-validation-spec.md` was written across revisions
> 0.1 to 0.3 as **a specification to hand to Alex so that Alex could build a form**: "the form you
> build", "before you start", "the acceptance contract for the form build", "do not build until
> OPEN-20 is closed", "handed to Alex as the build contract".
>
> **The form already exists.** https://revitalise.org.uk/apply-for-funding/ — a 20-page Gravity Forms
> form, live, taking applications, built and owned by Alex. The reviewer confirmed it directly.
>
> **How the error arose, because it is worth knowing.** Revision 0.1 was written from a summary of the
> form. Revision 0.2 received `docs/Import/Application Data Export(Sheet1).csv` — 163 columns — and
> correctly treated it as authoritative, but treated it as **the specification the new form should
> satisfy** rather than as **a description of the form that exists**. Every subsequent correction
> compounded the error by making the fictional build specification more precise. The tell was visible
> and was not read: revision 0.2's own words were "the raw 163-column export of **the live form**". A
> live form is not a form to be built.
>
> **Why it mattered more than a framing problem.** Because the document was a build target, its payload
> contract was written as an instruction to a future integrator rather than checked against what the
> live form actually posts. The intake flow was then built to that contract. So:
>
> | | |
> |---|---|
> | The intake **required** `date_of_birth` | **The live form never asks for a date of birth.** The word "birth" does not appear anywhere on the page |
> | The intake **required** `email` | The live form asks for an email address **only when the applicant ticks "Email" as their preferred contact method**. Ticking "Post" alone is a valid, complete submission with no email address in it |
>
> **Every real submission would have been rejected with a 400 and logged as an incomplete payload.**
> Not a subset — all of them, on the date_of_birth check alone. The flow was internally consistent
> (trigger schema, completeness check, 400 body and log line all named the same six fields, and a test
> asserted it) and externally wrong, which is the failure mode a self-consistent document is best at
> producing.
>
> ### What this revision did
>
> | | What changed | Where |
> |---|---|---|
> | **1** | **The form document was rewritten** as documentation of the live form (revision 1.0): its real 20-page structure, its real 71 question fields with their real required flags, all 23 of its real conditional-logic rules, and its real option lists — all read from the live page's own HTML and its embedded Gravity Forms conditional-logic map, fetched 2026-08-13 | `docs/development/…-form-validation-spec.md` |
> | **2** | **D-003 fixed in the code.** Required list reduced to the four fields the live form always collects; `age_range` accepted and mapped to `rev_agerange` through a new configuration row; `group_linkage` removed from the contract; two expressions that would throw on an absent value null-guarded; applicant lookup given a no-email fallback | the intake flow, both settings files, the pipeline config |
> | **3** | **D-004 addressed as far as evidence allows, and no further.** One confirmed WCAG failure (no valid `autocomplete` token on any of 251 inputs), one more found that D-004 did not name (two confirm-email boxes, 3.3.7), four confirmed passes, and **nine criteria honestly recorded as unaudited**. Raised as spec OPEN-26. D-004 stays **PARTIAL** | spec §10, test report §4 |
> | **4** | **A scoped change request for Alex** covering *only* validation and completeness — twelve items, priority-ordered, each evidenced from the form's own markup or from the charity's own record of which items are routinely missing. **Accessibility is deliberately excluded from it** | spec §7 |
> | **5** | **Ten mapping gaps recorded as decisions, not closed by guesswork** — including one that cannot be resolved without the charity: the live form's condition checkboxes and the committed option set classify along different axes | spec §9 |
>
> **What was deliberately NOT done, and why.** No Dataverse column was added, no option set was
> rewritten, and no Entity.xml was touched. Roughly 30 of the live form's 139 answer columns have
> nowhere to be stored, and five committed option sets do not match what the form sends. Fixing those
> means adding columns and renumbering option values — a schema change with a real blast radius
> (entity XML, the 34-column security profile, forms, views, retention) and, in the condition-profile
> case, a classification decision that belongs to Emily. **Making those changes on my own judgement
> would have repeated exactly the error this revision exists to correct**: building precisely against
> an assumption instead of checking. They are listed in spec §9 for the reviewer.

---

> ## 🔧 Revision 0.6 — the two HARD constraint violations that blocked the test run are closed
>
> Test-agent's run (`docs/tests/revitalise-grant-automation-test-report.md`, 2026-08-12) came back
> **PARTIAL** with two HARD technology violations. This revision closes both. It changes no
> component of the scoring engine, no table, no role and no privilege — the diff is an
> authentication control, two provisioning scripts, a settings block, a test suite and a
> coverage gate.
>
> | Defect | Constraint | What was wrong | What closed it |
> |---|---|---|---|
> | **D-001** / TC-401 | **C-TECH-006** (HARD) | The control the design calls "the primary control" on the solution's only public endpoint existed **nowhere in the delivery chain**: no provisioning script, no TAD §12 row, no `post_deploy` step, no smoke test. The only residual barrier was knowledge of a non-secret client ID | The Entra OAuth route is now **fully provisioned, owned and verified**: a caller identity with the API permission it needs, the trigger setting specified to an exact value with a named owner, and a smoke test that asserts 401/403 **and** that the rejection happened before the definition ran. **ADR-011 is deliberately still open** |
> | **D-005** / TC-901 | **C-TECH-014** (HARD) | `coding-standards.md` defined **no coverage threshold**, `build.yml` had **no coverage step**, and the repository contained **no automated test of any kind** | A threshold is defined and reasoned; **528 tests** now run and pass; the build fails below 80% coverage. Measured coverage of the Phase 1 provisioning scripts: **92.6%** |
>
> ### Fix 1 — C-TECH-006: the intake endpoint now has a real, testable primary control
>
> **The narrow problem, separated from the open decision.** ADR-011 (which intake channel to
> use) is the reviewer's to settle and is pending a conversation with Alex, the website
> developer. But the flow was already *written for* one of ADR-011's three named alternatives —
> Entra ID OAuth on the trigger — and its second gate already assumed an OAuth-issued caller
> identity. That route simply had nothing behind it. That is what this fix completes, and it
> completes it **without closing the ADR**: the OAuth route is now the fully provisioned default
> implementation, and each alternative's teardown is recorded in-place so the wrong one cannot be
> left half-built.
>
> **The configuration was verified against Microsoft documentation before being implemented**,
> the same way a prior pass in this pipeline verified Power Platform Pipelines and GitHub OIDC
> rather than guessing. Source:
> [`learn.microsoft.com/en-us/power-automate/oauth-authentication`](https://learn.microsoft.com/en-us/power-automate/oauth-authentication)
> (doc updated 2026-04-29). What that verification established, and it changes the shape of the
> fix:
>
> - The control is the trigger's **"Who can trigger the flow?"** authentication parameter, with
>   three modes: *Any user in my tenant* (the default for new flows), *Specific users in my
>   tenant*, and *Anyone* (legacy).
> - *Specific users in my tenant* accepts **service principal object IDs** in its Allowed users
>   field, semicolon-separated — which is exactly the shape needed for a single external
>   client-credentials caller.
> - Required claims are `aud` / `iss` / `tid` / `oid`; the public-cloud audience is
>   `https://service.flow.microsoft.com/` **with the trailing slash**, so a client-credentials
>   caller requests `https://service.flow.microsoft.com//.default` **with the double slash**. A
>   single slash fails as `MisMatchingOAuthClaims`, which reads like a permissions problem and
>   is not one.
> - **Microsoft publishes no workflow-definition property for this setting.** It is an authoring
>   surface, not solution content. That is the load-bearing finding: **the control cannot ship in
>   the managed solution and cannot be asserted by reading the flow JSON.** No property was
>   invented to paper over that.
>
> **So it is handled the only way such a control honestly can be — specified, owned, and
> verified:**
>
> | Layer | What was added |
> |---|---|
> | **Identity** | `rev-wordpress-intake` in both settings files is no longer a conditional stub. It now declares the **Microsoft Flow Service `User`** permission (without a permission on that resource Entra refuses the client-credentials request, so the endpoint would be *unreachable*, not merely unauthenticated), and a new `intake` settings block carries the mode, audience, scope, required claims, accepted rejection codes and the owner |
> | **Provisioning** | `provisioning/entra/ensure-intake-client.ps1` — idempotent per the README contract. It exists because `ensure-app-registration.ps1` never surfaces the **service principal object ID**, which is the value the trigger setting needs. It also **asserts** that a pre-existing registration really carries the declared permission and reports `FAILED` if not — that script deliberately never mutates an existing app's permissions, which is precisely how D-001 happened |
> | **Configuration** | A **named `post_deploy` step with an owner** on TST/ACC and PRD: Wanstor (tenant administration) sets the parameter to *Specific users in my tenant* with that object ID, **before the flow is turned on**. Whether the setting survives a solution import is **unverified** (no environment exists), so the pipeline configures it *and* verifies it on every deployment rather than assuming it carried across |
> | **Verification** | `provisioning/entra/verify-intake-endpoint-auth.ps1`, wired as a smoke test on both environments. This is the literal executable form of C-TECH-006's `Verify By` |
> | **Documents** | Three TAD §12 rows; ADR-011 updated with an explicit *"THE ADR STAYS OPEN"* note recording what changed and what did not |
>
> **The smoke test's second check is the one that matters.** A bare status-code assertion would
> have been theatre here, because the flow's *own* second gate also answers 401. So the script
> asserts the response body is **not** the definition's `{"error":"unauthorised"}` payload — that
> body arriving is proof the request got *into* the workflow, i.e. the trigger is set to *Anyone*
> and the platform control is absent. That is D-001's exact condition, and it now fails a
> deployment. A third check sends a syntactically valid but bogus bearer token, separating "the
> endpoint requires a token" from "the endpoint accepts any token".
>
> Two details worth stating because they are easy to get wrong in the other direction:
>
> - **The trigger URL is a credential.** It carries its own SAS signature in `sig=` — which is
>   why Microsoft documents regenerating it — so it is held as a per-environment CI secret
>   (`INTAKE_ENDPOINT_URL_TEST` / `_PRD`), never as a settings value, and the smoke test prints
>   scheme, host and path with the query string redacted.
> - **The Authorization header is deliberately *not* surfaced into trigger outputs.** No
>   `IncludeAuthorizationHeadersInOutputs`. A bearer token written into run history is a
>   credential at rest, and the platform gate already establishes the caller.
>
> **The caller's own credential is deliberately outside this pipeline.** Alex's site needs a
> certificate (preferred, C-TECH-044) or a client secret to obtain a token; it is issued
> interactively by the tenant administrator and handed over out of band. A pipeline that mints a
> credential is a pipeline that prints one (C-TECH-001). `ensure-intake-client.ps1` reports the
> credential posture **by count only** and never reads a value — asserted by a test.
>
> **One item is flagged rather than assumed.** Every published walkthrough of this pattern
> declares the **delegated** `User` scope and then acquires an **app-only** token with
> `.default`, which is an unusual combination. If Entra refuses the client-credentials request on
> first run, the fix is the equivalent application permission with `type` changed to `Role`. That
> is recorded in both settings files at the point of use, so it is discovered on the first
> `APPROVE TENANT` run and not in PRD.
>
> ### Fix 2 — C-TECH-014: the release has a test layer
>
> **The threshold, and the fact that it is a judgement call.** `coding-standards.md` now has a
> **Test Coverage** section: **80% line coverage over `provisioning/{common,entra,dataverse}`,
> build-failing**. The test report framed this as a Tech Lead decision; no Tech Lead was
> available, so development-agent made the call, documented the reasoning, and **flags it here as
> something the reviewer should confirm or override rather than treat as settled by having been
> written down.** The reasoning in short: the measured code is the most privileged code in the
> release and is ordinary PowerShell with ordinary branching, so there is no excuse for leaving
> it untested; 80% is a floor with real headroom (92.6% actual) rather than an aspiration; and
> the last few percent are mostly `catch` blocks whose only realistic trigger is a live API
> failure, so a threshold pinned at the current actual would fail the build on a refactor that
> added error handling — which teaches people to game the metric.
>
> **Coverage is scoped, and the standard says why.** A percentage over the whole repository would
> be meaningless in both directions: most of what this project ships is declarative, an
> `Entity.xml` has no executable lines, and the way to raise such a number would be to delete
> configuration rather than test anything. So declarative artefacts get a different, stated
> obligation instead — **every relationship whose correctness the requirements depend on must
> have a re-runnable asserted test**, measured as completeness against an enumerated list rather
> than a percentage. §9.1 is that list.
>
> **What was built** (`src/tests/`, 528 tests, 1 deliberate skip, 0 failures):
>
> | Suite | Tests | What it asserts |
> |---|---|---|
> | `provisioning/ScriptContract.Tests.ps1` | 273 | The five numbered rules of `provisioning/README.md` § Script Contract, **from the AST** rather than by grepping text, over **all 20 scripts** — including that `verify-*` scripts are read-only and that the README inventory has not fallen behind the directory |
> | `provisioning/ProvisioningCommon.Tests.ps1` | 61 | Every helper in `provisioning-common.ps1`: dot-path resolution, the `{{PLACEHOLDER}}` fail-fast, the three-state status line, the exit code, OData escaping, app-only auth |
> | `provisioning/EntraScripts.Tests.ps1` | 36 | The four Entra scripts plus the two new ones, executed against mocked Graph |
> | `provisioning/DataverseScripts.Tests.ps1` | 49 | Eight Dataverse scripts, executed against a mocked Dataverse Web API |
> | `provisioning/DeploymentSettings.Tests.ps1` | 33 (+1 skipped) | Policy-versus-per-environment invariants across both settings files |
> | `solutions/ScoringInvariants.Tests.ps1` | 44 | The scoring engine's arithmetic and structural invariants |
> | `solutions/IntakeContract.Tests.ps1` | 31 | The published payload contract and the Fix 1 authentication control |
>
> **The provisioning tests run the real scripts, unmodified.** No Graph, Dataverse or PnP call is
> real, per `knowledge/technology/testing-tools.md`. The fakes sit one layer *below* the shared
> helpers, so the real `Get-Setting`, `Assert-NoPlaceholder`, `Write-ResourceStatus`,
> `Exit-Provisioning` and `Invoke-DataverseApi` all execute — which is a more honest test than
> mocking them, and is also forced by the design: each script dot-sources
> `provisioning-common.ps1` into its own scope, so those helpers cannot be replaced by a mock.
> `src/tests/provisioning/_harness/ProvisioningTestHarness.psm1` documents the mechanism.
>
> **What is asserted is mostly the REQUEST, not the response**, because a provisioning defect is
> almost never mishandling the answer — it is asking for the wrong thing. So: a team created with
> `teamtype 2`; a role resolved **by name** and never by GUID; `rev_effectivefrom` stamped on
> create **only**, so a pipeline re-run cannot destroy the evidence of when a threshold took
> effect; the audit retention PATCH carrying `MSCRM.MergeLabels`; `IsAuditEnabled` read from
> `.Value` because it is a `BooleanManagedProperty` and reading the wrapper would be truthy
> always and silently never enable auditing; the retention jobs using **relative** date operators
> so a recurring job is re-evaluated rather than frozen at provisioning time; the orphan sweep's
> LEFT OUTER join and aliased null test, which an inner join would silently turn into a no-op.
>
> **Two tests exist to guard other tests.** The FR-016 check runs against the definition with
> every `description` stripped — the special-category column names appear in the flow's prose
> *deliberately*, to explain the exclusion, so a naive grep is a false positive and a grep tuned
> around that noise can be tuned into a false negative. A companion test asserts the names *are*
> still in the raw prose, so the stripper failing silently would fail a test rather than make the
> real check pass vacuously. The same reasoning covers the harness-completeness tests: an
> undeclared parameter on a fake would bind into `$Rest` and make every
> `Should -Invoke … -ParameterFilter` assertion pass with zero invocations recorded.
>
> **The cross-artefact coupling is asserted, and it is the subtlest thing here.**
> `verify-intake-endpoint-auth.ps1` detects D-001 by recognising the flow's own 401 body. Nothing
> else in the delivery chain couples those two files, so editing the flow's 401 payload would
> silently stop the smoke test from being able to detect an open endpoint — and it would report a
> pass. `IntakeContract.Tests.ps1` asserts the flow's body and the script's discriminator agree.
>
> **What this does NOT cover, stated plainly so a green build is not over-read.** The
> provisioning scripts and the flow-JSON static invariants are now genuinely tested. **The flows'
> runtime behaviour against a live Dataverse environment still cannot be tested, because no
> environment exists** — flow execution, column-security enforcement, audit-record shape,
> connection binding and the live 401 from the intake endpoint all remain in test-agent's §8
> deferred list, exactly as recorded there. Coverage of the provisioning scripts is not coverage
> of the solution. One Phase 1 script, `ensure-document-locations.ps1`, is measured at 0%: it is
> a Phase 2 document-management script that no Phase 1 pipeline step invokes and for which
> neither settings file declares a block. `provisioning/sharepoint/` and `provisioning/teams/`
> are out of the measured scope for the same reason, and are covered by the contract suite.
>
> ### Deliberately NOT done in this cycle
>
> - **ADR-011 is not closed.** Not development-agent's to close, and the reviewer has said so.
> - **D-002, D-003, D-004, D-006 to D-013 are untouched.** The brief was these two defects. In
>   particular **D-004 (WCAG 2.1 AA acceptance narrower than the standard) remains open and is
>   the highest-human-consequence finding in the release** — it is not made better by this
>   revision.
> - **D-011 has a written test that is deliberately `-Skip`ped**, with the defect ID and the
>   one-line fix in the skip comment, so an open P4 is visible mechanically instead of only in a
>   report. Remove the `-Skip` in the change that splits the token.
>
> ### One robustness observation found by writing the tests, reported and NOT fixed
>
> `ensure-app-registration.ps1` and `verify-entra.ps1` pipe a Graph result straight into
> `Where-Object { $_.Property … }`. Under `Set-StrictMode -Version Latest`, an explicit `$null`
> return would throw and produce a spurious `FAILED`. **The real cmdlets return no output rather
> than `$null`, so this does not manifest today** — it surfaced only because a mock returned
> `$null` literally, and the mocks were corrected to match real behaviour. It is one `@(…)` away
> from being airtight, but changing the most privileged code in the release is out of scope for a
> fix cycle scoped to two defects. Recorded for the reviewer to direct.

> ## 🚨 Revision 0.5 — `pac solution pack` was run for the first time. It failed. It now succeeds for BOTH package types.
>
> **Read this revision before any other. It is the most load-bearing correction in this
> document's history, because until now nothing in this repository had ever been proven to
> build.** Revisions 0.1–0.4 each carried a limitation reading, in substance, "the unpacked
> layout is hand-authored and unvalidated, pending a real environment". That was treated as a
> deferred risk. It was not a risk — it was **nine defects**, and a real `pac solution pack`
> found them in about four seconds. No Dataverse environment was needed to find any of them.
>
> ### The single mistake behind almost all of it
>
> Every failure but two came from one wrong assumption: **that Dataverse solution XML names a
> component with child elements.** It does not. For most component types the packer reads the
> identifying name and GUID from **XML ATTRIBUTES on the element's root**, and the surrounding
> descriptive metadata from child elements. The source had `<RoleId>…</RoleId>` where the packer
> wanted `<Role id="…">`. The pattern was applied consistently — and consistently wrongly —
> across five component types. **Where it is genuinely the other way round (`AppModule`,
> `AppModuleSiteMap`) the source happened to be right, which is exactly why the wrong assumption
> survived four revisions unchallenged: it was never uniformly wrong, so it never looked like a
> pattern.**
>
> The evidence is not inference. `SolutionPackagerLib.dll` — shipped inside `pac` — was
> decompiled with `ilspycmd` and each component's `CreateComponent(XElement)` override read
> directly, so every fix below cites the actual line the packer executes. §2.5 is the full
> record, per component type, with the decompiled evidence.
>
> ### Why this was not caught by inspection, and would not have been
>
> **Six of the nine defects fail SILENTLY.** This is the part that matters for how this repo is
> reviewed from now on:
>
> | | Failure mode | What the developer sees |
> |---|---|---|
> | **Loud** | `Helper.GetAttributeValue(…, throwIfNull: true)` | Immediate, named error. The OptionSets and Role-privilege defects were of this kind, which is why they surfaced first |
> | **Silent — wrong path** | A processor reads ONE hard-coded path (`Other/FieldSecurityProfiles.xml`) and `return null` if absent | Pack **succeeds**. The component is simply not in the package. 34 secured columns would have shipped with no profile releasing them — every one unreadable, including by the process owner |
> | **Silent — not asked for** | `DiskReader.Load` only processes component types **listed as elements in `Other/Customizations.xml`** | Pack **succeeds**. `AppModules/`, the app sitemap and all three environment variable definitions were never read at all: the folders were correct, but nobody asked for them. They were swept into the zip as anonymous "sharded" raw files instead |
>
> A "clean" pack log therefore proves nothing on its own. **The only sufficient check is to open
> the produced .zip and confirm the components are inside it**, which §2.5.4 now does and which
> §8 makes a standing build step.
>
> ### The Managed failure was one number, and it was in the manifest
>
> `--packagetype Managed` failed with `Solution package type did not match requested type` for a
> reason that had nothing to do with any component: `Other/Solution.xml` said
> `<Managed>0</Managed>`. That value is parsed straight into the packer's `SolutionPackageType`
> enum, and Pack throws unless it is `Both (2)` or exactly equals the requested type. A repo that
> must emit **Unmanaged for Dev and Managed for Test/Prd from one source** has to say `2`.
> `pac solution init`'s own skeleton says `2`. Confirmed independently: the skeleton was generated
> and read. §2.5.3.
>
> ### Result
>
> **Four clean packs — two package types × two `pac` versions (2.4.1 and 2.9.3).** Verbatim
> command output in §2.5.4, together with the contents of both .zip files proving all 35
> components are actually present. The zip is now exactly the seven entries a real solution
> export contains, with **no stray sharded files** — which is itself evidence the three
> "silent" defects are closed.
>
> **Two repo checks were corrected, not just the solution.**
> `scripts/verify-solution-root-components.py` and `scripts/verify-field-security-coverage.py`
> both encoded the *broken* layout and both reported PASS against it. A check that agrees with
> the thing it is checking is worse than no check, so both now assert the packer-verified forms
> and would have failed the old source. §2.5.5.
>
> **Nothing was rewritten.** Every privilege, comment, permission and design decision is
> byte-for-byte intact: 40 + 33 role privileges, 34 field permissions, 15 option sets, all four
> flow definitions, all 122 audit-enabled columns. This revision corrected **structure and file
> location only**. Where a file's own header comment had recorded the wrong guess, the comment
> now records the packer's actual requirement and why — so the next author cannot repeat it.

> ## 🔧 Revision 0.4 — ALM tooling settled, CI/CD rewritten, C-TECH-044 closed
>
> **No solution component changed in this revision.** Not one entity file, flow definition, role,
> option set or `rev_setting` value was touched. Everything here is delivery infrastructure:
> `.github/workflows/ci.yml` (a **repo-wide, shared** file), the two per-feature config files, the
> deployment settings' credential declarations, and the TAD sections that described the old shape.
> §5.4 is the complete record.
>
> Three reviewer decisions drove it:
>
> | | Decision | What it changed |
> |---|---|---|
> | **1** | **CI/CD must match the confirmed three-environment topology** DEV → TST/ACC → PRD | The three `deploy-test` / `deploy-acc` / `deploy-prd` jobs against GitHub Environments `test`/`acc`/`prd` are gone. Five jobs now: `validate` → `build` → `stage-dev` → `promote-tst-acc` → `promote-prd`, against `dev` / `tst_acc` / `prd`, matching the environment keys the pipeline config already used |
> | **2** | **ADR-007: the ALM tool is Power Platform Pipelines**, overriding this system's own recommendation of pac CLI + GitHub Actions | GitHub Actions no longer imports into TST/ACC or PRD at all. Its deploy role ends at "import the **unmanaged** solution into DEV"; Pipelines exports from DEV itself and owns DEV → TST/ACC → PRD. ADR-007 moved `Decision required` → `Adopted` |
> | **3** | **C-TECH-044: switch to a federated credential (OIDC)** | `CLIENT_SECRET` is gone from the workflow and from `build.yml`. Auth is `pac auth create --githubFederated`. **The SOFT warning carried through revisions 0.1–0.3 is now closed, not carried again.** New ADR-021 |
>
> **A fourth change came from the reviewer mid-task and is called out because it is a security
> posture decision, not a default:** the single shared `APP_ID` is replaced by **one deploy identity
> per environment** — three app registrations, each holding **exactly one** federated credential
> bound to its own GitHub Environment subject, each a Dataverse application user in **its own
> environment only**. Separate registrations rather than several credentials on one registration,
> because credential-only scoping gates token *issuance* but not *authority*: every subject would
> still resolve to one service principal that is an application user everywhere, so a token minted
> by the TST/ACC job could import into PRD. §5.4.4 has the reasoning in full.
>
> **Three things a reviewer must look at specifically:**
>
> | | What | Where |
> |---|---|---|
> | **1** | **The build artefact is no longer the deployed artefact.** Pipelines exports from DEV itself; `RevitaliseGrantAutomation-managed.zip` becomes a build-validation and audit artefact. This changes how **C-TECH-030** is satisfied — a HARD constraint scoped to pipeline-agent, flagged here because this revision is what changes it | §5.4.2, §10 |
> | **2** | **Two new tenant prerequisites, one with a licence cost.** A custom **pipelines host** environment, and **Managed Environment status on TST/ACC and PRD**, which requires premium use rights. Neither existed in the plan before this ALM choice | §5.4.3, TAD §12 |
> | **3** | **Promotion is manual for the first release, deliberately.** `pac pipeline deploy` is real and verified, but whether a *service principal* may **request** a promotion is undocumented. The `cli` path is built and switchable; `manual` is the default until one UI promotion proves it | §5.4.5 |
>
> **One latent bug in the old shared workflow was found and fixed on the way through:** the previous
> `ci.yml` passed `post_deploy` steps declared as `script: manual` straight to `bash -c`, so every
> run would have died on `manual: command not found`. It had simply never been exercised — no
> environment exists yet to deploy to. §5.4.6.

> ## ✅ Revision 0.3 — the reviewer answered revision 0.2's three open questions
>
> Revision 0.2 raised three things it deliberately did not decide. All three came back answered, and
> **all three are now closed in the build, not just in the document.** §2.4 is the complete record.
>
> | | The question | The answer | What moved |
> |---|---|---|---|
> | **1** | Is the circumstance score out of **55 or 60**? | **60.** It is the life-satisfaction question (0–10) **plus** ten wellbeing questions at up to 5 each: 10 + 50. | `rev_feelingscaleanswer` converted from a five-option picklist to a **Whole Number 0–10**; the `rev_feelingscale` option set **deleted**; `FeelingScaleInversion` became an **eleven-entry map keyed 0–10** expressing `10 − answer`; `MaxCircumstanceScore` **back to 60** in both settings files |
> | **2** | Are the referee and emergency contact asked at intake? | **No — neither at intake nor through this integration.** A **separate form, sent to the relevant party after the board approves the grant.** | Five fields **removed** from the intake trigger schema and from the create mapping. The five **columns stay** on `rev_application`, untouched |
> | **3** | What are the ten wellbeing answer labels? | **None of the time / Rarely / Some of the time / Often / All of the time** — a frequency scale. | `rev_likertresponse`'s five labels replaced. **No option value changed**, and the value-to-frequency direction was re-verified against all ten real question texts rather than assumed |
>
> **The financial-column security tightening from revision 0.2 (§6.5) was reviewed and ACCEPTED,
> unchanged.** No action was needed and none was taken. The reviewer also confirmed it is trivially
> reversible if the posture is ever revisited: flip `IsSecured` back, or extend the field security
> profile to release the columns more widely — **no data impact either way**, because nothing has been
> written to a live environment yet and column security is evaluated on read, not stored with the row.
>
> **What is still open after revision 0.3 is smaller and different:** three of revision 0.2's four
> reviewer decisions are now closed (D-3, D-6 and the OPEN-1 scale question); D-4 (the breaking payload
> contract) and D-5 (five placeholder option sets) stand unchanged. Two genuinely new residual
> questions are recorded, both belonging to **future** work rather than this release: **who completes
> the separate post-approval referee form** (Automation #3 design), and **whether Revitalise holds a
> SWEMWBS licence** if it means to report scores against national norms. Neither blocks Build.

> ## 🔄 Revision 0.2 — the schema revision pass
>
> The reviewer supplied **`docs/Import/Application Data Export(Sheet1).csv`** — the real
> 163-column export of the live application form. Everything the Phase 1 schema was built from
> (`grant-application-data-model.md` v0.1 and `-v0.2.md`) was a *summary* of that export. The
> export is now the authority, and where they disagreed the export won.
>
> **§2.3 is the complete record of what changed.** In one paragraph: the Applicant table gained
> seven columns and the full name became calculated from a first/last split; the Application table
> gained forty-two and lost two; a twelve-field wellbeing block was corrected to eleven scored
> answers; a single free-text financial blob became eight typed columns; four real declaration
> blocks replaced the four that had been guessed at; two schema gaps found while writing the form
> specification (OPEN-2, OPEN-3) are closed. Seventeen new columns are secured, so the field
> security profile went from 17 permissions to 34.
>
> **Three things a reviewer must look at specifically, because they change behaviour rather than
> adding to it:**
>
> | | What | Where |
> |---|---|---|
> | **1** | ~~**The maximum circumstance score is now 55, not 60**~~ → **SUPERSEDED BY REVISION 0.3: it is 60, and it is now settled.** Revision 0.2 reduced it to 55 because the life-satisfaction question had been built as a five-option picklist; the reviewer confirmed it is a 0–10 scale, so the picklist is gone and the maximum is 60. SDD OQ-001 and OQ-002 are unblocked. | §2.4.1, §7.5 D-3 |
> | **2** | **The intake payload contract is broken on purpose.** `full_name` is gone, replaced by `first_name` + `last_name`. Alex's site must send the new shape. Three other fields left the contract. | §2.3.4, §7.5 D-4 |
> | **3** | **Eight new columns are secured on a DERIVED classification decision** — the financial cluster that replaced `rev_financialanswers`, which held the same content unsecured. Stricter than what it replaced. Accept or reject. | §2.3.3, §6.5 |

> ⚠️ **Read §7 before approving.** Nothing in this release has been validated against a live
> Power Platform environment. No DEV, TST/ACC or PRD environment exists yet (WBS 0.2), and
> `pac admin list` confirms only a default Dataverse environment. Every artifact here is
> hand-authored solution source that has never been through a `pac solution pack` → import
> cycle. §7 lists, specifically and by name, each place where that matters.
>
> ⚠️ **One dependency blocks the automations from being relied upon at all.** The WBS 0.3
> scoped Conditional Access exception for the service account's *unattended* flow sign-ins is
> still unconfirmed with Wanstor. Live testing on 2026-08-10 confirmed interactive browser
> sign-in works; device-code / public-client sign-in is CA-blocked. All four flows run
> unattended as that account. See §7 and `config/revitalise-grant-automation-pipeline.yml`
> → `tenant_prerequisites.permission_findings`.
>
> 📝 **Knowledge-base gap, recorded once.** `knowledge/technology/coding-standards.md`,
> `dataverse.md`, `power-automate.md`, `entra-id.md`, `teams.md`,
> `knowledge/domain/business-rules.md` and `data-entities.md` are unpopulated or generic
> template placeholders in this repository. `knowledge/technology/security-model.md` **is**
> populated and its group-team pattern is applied in full. Where a placeholder left a gap,
> this implementation follows the TAD plus standard Power Platform convention and says so at
> the point of use. Carried forward from SDD OQ-029 / TAD reader's note.

---

## 1. Implementation Summary

Phase 1 makes a grant application arrive in Dataverse by itself, score itself, and tell one named
person about it — and makes any failure of those three things visible rather than silent.

Three of the seven automations are in scope. Two are built as solution components; one ships as a
document.

| Automation | What was delivered | Form |
|---|---|---|
| **#1 Form Validation & Completeness** (FR-001–FR-006) | ⚠️ **Superseded by §2.6 — the form already exists.** The deliverable is now **documentation of the live form** plus a scoped validation change request, not a build contract. Originally recorded as: a field-by-field build contract for **Alex**, the external website designer: **82 applicant-facing fields at revision 0.2** (48 at revision 0.1), conditional logic, plain-English validation messages, progress indicator, save-and-continue, review-and-submit, WCAG acceptance criteria and the JSON payload contract | `docs/development/revitalise-grant-automation-form-validation-spec.md` — a specification, **not code**. WordPress / Gravity Forms is out-of-palette and is built manually outside this system (TAD §8, §12) |
| **#4 WordPress → Dataverse Intake** (FR-007–FR-010) | `REV \| Intake \| WordPress to Dataverse` — validates the caller, validates the payload, guards against replays, matches-or-creates the applicant, derives age band and region, creates the application, notifies the process owner | Cloud flow in the solution |
| **#2 Scoring Engine** (FR-011–FR-022) | `REV \| Scoring \| Calculate & Flag` and `REV \| Scoring \| Daily Summary` — every threshold read from configuration at run time, special-category data structurally excluded, Borderline and incomplete-answer cases pushed to a human | Two cloud flows in the solution |
| **Cross-cutting** | `REV \| Ops \| Failure Alert` — the child flow every other flow calls from its failure path, plus the `rev_errorlog` table and the Error Log surface in the app | Cloud flow + table + app area |

Supporting all of that: four Dataverse tables, **sixteen** global option sets (sixteen at revision
0.2, fifteen after revision 0.3 deleted `rev_feelingscale` — §2.4.1 — and sixteen again after
revision 0.8 added `rev_agreementresponse`; corrected in revision 0.9, D-017), one parental relationship,
two alternate keys, two security roles, one column security profile, one model-driven app with a
three-group sitemap, three environment variable definitions, three connection references, seven
saved queries, ten seeded configuration rows, and eleven provisioning scripts wired into a
two-hop pipeline.

### 1.1 What was recovered versus newly built

A previous run of this task was interrupted. Its work was reviewed against the TAD and SDD rather
than trusted, and the review found more missing than the handover notes recorded.

| Status | Artifacts |
|---|---|
| **Recovered and verified correct — kept unchanged** | The four `Entity.xml` files and their seven `SavedQueries`; `Other/Solution.xml`; `config/revitalise-grant-automation-build.yml` and `-pipeline.yml` (both already reflected the confirmed three-environment topology and the tenant-prerequisite findings correctly); `provisioning/deploymentSettings/pac-import-tstacc.json` and `pac-import-prd.json` |
| **Directories that existed but were EMPTY — the handover notes said otherwise** | `Other/Relationships/`, `AppModules/rev_grantadministration/`, all three `environmentvariabledefinitions/*/`, `Workflows/`, `Roles/`, `FieldSecurityProfiles/` |
| **Entirely absent and not mentioned in the handover** | `OptionSets/` — all ten global option sets, every one of which is referenced with `IsGlobal=1` by an attribute in the recovered entities; `Other/Customizations.xml`, which `pac solution pack` requires and which is the only home for the three connection references |
| **Newly built (this pass)** | Everything in the two rows above, plus four missing provisioning scripts, two missing provisioning settings files, one build verification script, the form specification and this document |
| **Fixed (this pass)** | Two defects in `build.yml` and two in `pipeline.yml` — see §5.3 |
| **Revised (revision 0.2)** | Both personal-data `Entity.xml` files, six new `OptionSets`, the field security profile, `Other/Solution.xml`, the intake and scoring flows, both provisioning settings files, `build.yml`, the form specification, and this document. One new verification script. **See §2.3.** |

**`Other/Solution.xml` was the thing that made this recoverable.** It declared 30 root components,
and only 12 of them had a definition on disk. The manifest was, in effect, a specification of the
missing work — including component GUIDs, which is why the security-role and flow GUIDs in this
release match what the interrupted run intended rather than being re-invented. That experience is
now a build gate: `scripts/verify-solution-root-components.py` fails the build if the manifest and
the source ever disagree again, in either direction.

---

## 2. Components Changed / Created

### 2.1 Solution components — `src/solutions/RevitaliseGrantAutomation/`

| Component | Type | Change Description | FR Reference |
|---|---|---|---|
| `rev_applicant` | Table (recovered, **REVISED 0.2**) | **18 attributes; 12 secured** (was 11 and 6). Primary name is the pseudonymised reference `REV-A-nnnnn`, never the person's name. `rev_fullname` is now a **calculated** column | ADR-013, FR-027, FR-051 |
| `rev_application` | Table (recovered, **REVISED 0.2**) | **88 attributes; 22 secured** (was 48 and 11 — §2.1's earlier count of "49" was itself one too many). Autonumber `REV-{yyyy}-{nnn}`; alternate key on `rev_sourcesubmissionid`. `rev_costs` is now a **calculated** column | FR-007, FR-008, FR-011–FR-022 |
| `rev_setting` | Table (recovered) | 5 attributes; alternate key on `rev_name`, which is what makes the seed script an idempotent upsert | FR-017, NFR-019 |
| `rev_errorlog` | Table (recovered) | 9 attributes; organisation-owned. Schema physically cannot hold personal data | FR-010, NFR-012, NFR-016 |
| 7 × `SavedQueries` | System views (recovered) | Active Applications (`rev_status ne 4`), Borderline — Awaiting Review, Under Review — Incomplete Scoring, Auto-rejected Applications, All Applications, Active Applicants, All Settings, Unresolved Errors | FR-019, FR-020, FR-022 |
| **16 × `OptionSets/*.xml`** | **Global option sets — NEW** | The original ten: `rev_likertresponse`, ~~`rev_feelingscale`~~, `rev_applicationstatus`, `rev_incomeflag`, `rev_incomeband`, `rev_agerange`, `rev_locationarea`, `rev_conditionprofile`, `rev_settingdatatype`, `rev_errorseverity`. **Six added in revision 0.2:** `rev_title`, `rev_applicanttype`, `rev_gender`, `rev_breaktype`, `rev_helperrelationship`, `rev_exceptionalcircumstance` — **five of the six carry PLACEHOLDER values, flagged in the file itself and in §7.5 D-5**. **`rev_feelingscale` DELETED in revision 0.3** (the life-satisfaction question is a whole number 0–10, so it backed no column — §2.4.1), and `rev_likertresponse`'s five labels were replaced with the confirmed frequency wording (§2.4.3). **`rev_agreementresponse` ADDED IN REVISION 0.8** — the three "last year" questions use an agree/disagree scale, not the frequency scale, proved by `docs/Import/Book(Sheet1).csv`; `rev_wellbeinganswer8/9/10` are rebound to it. **Both scales also gained a sixth option, "Not sure" (value 6, worth 0.5 points)** — a real answer the live form offers, which until revision 0.8 could not be stored at all (D-014) | FR-012, FR-013, FR-014, FR-015, FR-020, FR-027 |
| **`Other/Relationships/rev_application.xml`** | **1:N relationship — NEW** | `rev_applicant_rev_application_applicantid`, **Parental**, all five cascade behaviours set to Cascade | FR-048, FR-051; TAD §3.3 |
| **`Other/Customizations.xml`** | **Required manifest file — NEW** | Language set plus the three connection references `rev_SharedDataverse`, `rev_SharedTeams`, `rev_SharedOutlook` | NFR-006; TAD §4.1 |
| **`environmentvariabledefinitions/` ×3** | **Env var definitions — NEW** | `rev_ServiceMailbox`, `rev_ProcessOwnerUpn`, `rev_IntakeAllowedClientId`. **No default values** — all injected at import | NFR-008, C-TECH-031, C-TECH-047 |
| **`Roles/REV Admin/`** | **Security role — NEW** | 23 feature privileges + 17 platform baseline. Explicit non-privileges documented in the file | FR-017, FR-018; NFR-002; TAD §6.2 |
| **`Roles/REV Service Automation/`** | **Security role — NEW** | 16 feature privileges + 17 platform baseline. Narrower than TAD §6.2 — see §6.4 | ADR-009; C-DOM-020 |
| **`FieldSecurityProfiles/REV_TrusteeRestricted.xml`** | **Column security profile — NEW, REVISED 0.2** | **34 field permissions** across the two personal-data tables (was 17). One column is deliberately absent and must stay absent: `rev_breaklocation`, which is trustee-visible by design | NFR-001, NFR-003, FR-031; ADR-002 |
| **`AppModules/rev_grantadministration/`** | **Model-driven app + sitemap — NEW** | `REV Grant Administration`. Sitemap groups: Casework (5 areas), Configuration, Operations | FR-017, FR-018, FR-019, FR-020, FR-022 |
| **`Workflows/REVIntakeWordPressToDataverse-…`** | **Cloud flow — NEW** | HTTP request trigger, concurrency 1 | FR-007, FR-008, FR-009, FR-010, FR-027 |
| **`Workflows/REVScoringCalculateAndFlag-…`** | **Cloud flow — NEW** | Dataverse row-created trigger on `rev_application` | FR-011–FR-020, FR-022 |
| **`Workflows/REVScoringDailySummary-…`** | **Cloud flow — NEW** | Recurrence, weekday mornings 07:00 UTC | FR-021 |
| **`Workflows/REVOpsFailureAlert-…`** | **Child cloud flow — NEW** | Button trigger, `Subprocess = 1`, ends in a Response | FR-010, NFR-012, NFR-016 |

All four flows ship **deactivated** (`StateCode 0` / `StatusCode 1` = Draft). That is deliberate:
the three connection references must first be bound to service-account-owned connections, which
requires interactive OAuth consent and cannot be scripted, and a flow activated before its
connection exists fails on its first trigger.

### 2.2 Documents and repository files

| Component | Type | Change Description | FR Reference |
|---|---|---|---|
| `docs/development/revitalise-grant-automation-form-validation-spec.md` | Documentation — **REVISION 1.0, 2026-08-13** (was Specification, rev 0.2) | ⚠️ **Reframed in revision 0.7.** The form is live and Alex already built it, so this documents what exists: the real 20 pages, 71 question fields (61 required), 23 conditional-logic rules and option lists read from the live page; a scoped 12-item validation and completeness change request (§7); the real payload contract (§8); ten mapping gaps needing a decision (§9); and what has and has not been audited for accessibility (§10). Originally recorded as: Automation #1 as a build contract for Alex. **82 applicant-facing fields** (48 at revision 0.1), 14 sections, **25 numbered open items — two closed, seven new**, unchecked sign-off checklist. Carries a breaking payload-contract change in a banner at the top | FR-001–FR-006, NFR-020, NFR-024, ADR-020 |
| `docs/development/revitalise-grant-automation-dev-summary.md` | This document — NEW | — | — |
| `scripts/verify-solution-root-components.py` | Build verification — NEW | Two-way consistency check between `Solution.xml` `<RootComponents>` and the definition files on disk | — |
| **`scripts/verify-field-security-coverage.py`** | **Build verification — NEW (revision 0.2)** | Two-way check that every `IsSecured=1` column is released by a field security profile and that no profile releases an unsecured column. Written because revision 0.2 added seventeen secured columns in one change and a single omission would be silent — the symptom is a blank field nobody can account for, or an intake create failing on a column the developer believed was fine. Wired into `build.yml` as `field-security-coverage`. Holds one reviewed exemption (`rev_breaklocation`) | NFR-001, NFR-003 |
| `config/revitalise-grant-automation-build.yml` | Build config — FIXED, **REVISED 0.4** | See §5.3; revision 0.4 switched the `auth` step to `--githubFederated` and dropped `CLIENT_SECRET` from `required_env_vars` (§5.4) | C-TECH-044 |
| `config/revitalise-grant-automation-pipeline.yml` | Pipeline config — FIXED, **REVISED 0.4** | See §5.3; revision 0.4 replaced both `deploy_command`s with an `alm` block + `promote_mode`, rewrote both rollback routes, and added four tenant prerequisites (§5.4) | C-TECH-041 |
| **`.github/workflows/ci.yml`** | **CI/CD workflow — REWRITTEN (revision 0.4).** ⚠ **Repo-wide shared file, not feature-scoped** | Three-environment topology (`dev`/`tst_acc`/`prd`, five jobs), Power Platform Pipelines hand-off, OIDC auth, per-environment deploy identities. Also fixes a latent `manual: command not found` failure and wires up `pre_deploy`, which was never executed (§5.4.1, §5.4.6) | C-TECH-044, C-TECH-007, C-TECH-041 |
| **`.github/actions/setup-powerplatform/action.yml`** | **Composite action — NEW (revision 0.4)** | Version-pinned `pac` (2.4.1) and `yq` (v4.44.3), an `id-token` pre-flight that names the missing `permissions` block, and `pac auth create --githubFederated`. Exists because four jobs need the identical six steps — the old workflow inlined them three times and the copies had drifted | C-TECH-020, C-TECH-044 |
| **`scripts/ci/run-config-steps.sh`** | **CI helper — NEW (revision 0.4)** | Generic runner for the four config-declared step lists (build steps, `pre_deploy`, `post_deploy`, `smoke_tests`). Records `manual` steps as an operator checklist instead of passing them to `bash`. Replaces six near-identical inline yq loops | C-TECH-007, C-TECH-013 |
| **`scripts/ci/promote-via-pipelines.sh`** | **CI helper — NEW (revision 0.4)** | Drives (`cli`) or hands over (`manual`) the Power Platform Pipelines promotion, with a `pac pipeline list` pre-flight that fails naming the exact roles to grant. Carries the verified/unverified research inline | — |
| **`scripts/ci/verify-promoted-version.sh`** | **CI helper — NEW (revision 0.4)** | Asserts the expected solution version is present in the target before any `post_deploy` script runs, so approving the gate before promoting fails loudly rather than provisioning an empty environment | C-TECH-042 |
| `config/pipeline.yml.example` | Shared template — **REWRITTEN (revision 0.4)** | Three-environment + Power Platform Pipelines shape. Required for correctness, not preference: the shared `ci.yml` no longer reads `deploy_command` (§5.4.7) | — |
| `provisioning/dataverse/` ×4, `provisioning/deploymentSettings/` ×2 | Provisioning — NEW, **settings REVISED 0.4** | See §5.2; revision 0.4 split the deploy app registration per environment and corrected the federated-credential subjects in `test-settings.json`, `prd-settings.json` and `dev-settings.example.json` (§5.4.4) | C-TECH-043, C-TECH-044 |
| `provisioning/README.md` | Documentation — UPDATED | Four rows added to the Script Inventory table. Nothing else changed | — |

### 2.3 Revision 0.2 — the schema revision pass

**What prompted it.** The reviewer supplied `docs/Import/Application Data Export(Sheet1).csv`: the
real 163-column export of the live application form, read with `cp1252` encoding. Every earlier
schema decision had been taken from `grant-application-data-model.md` (v0.1) and `-v0.2.md`, which
are *summaries* of that export. Summaries lose things, and this one had lost enough to matter.

**How disagreements were settled.** The export wins over the markdown summaries, and the summaries
win over inference. Every column added below cites the export column it came from, so any
disagreement can be settled by looking at one cell of one spreadsheet.

#### 2.3.1 `rev_applicant` — seven columns added, one converted

| Column | Type | Export col | Secured | Note |
|---|---|---|---|---|
| `rev_title` | choice `rev_title` | 15 | ✅ | **PLACEHOLDER option list.** Identity-adjacent, and Mr/Mrs implies gender, so it sits with the name |
| `rev_firstname` | text 100 | 16 | ✅ | Required. One half of the name split |
| `rev_lastname` | text 100 | 18 | ✅ | Required. The other half |
| `rev_fullname` | text 201 | — | ✅ | **CONVERTED to a calculated column**: `CONCAT(rev_firstname, " ", rev_lastname)` |
| `rev_addressline2` | text 250 | 21 | ✅ | |
| `rev_towncity` | text 100 | 22 | ✅ | County and country (cols 23, 25) deliberately not built — every applicant is UK-based |
| `rev_applicanttype` | choice `rev_applicanttype` | 35 | ✗ | **PLACEHOLDER option list.** A reporting dimension of the same kind as the condition profile, which trustees see by design |
| `rev_gender` | choice `rev_gender` | 149 | ✅ | Equality monitoring. **Ordinary personal data, not Article 9** — see below |

**Why `rev_fullname` became calculated rather than being deleted.** Splitting the name into two
columns would have broken every existing consumer of `rev_fullname`: the FR-009 Teams notification,
the Active Applicants view, and any future report. Making it calculated means all of them keep
working unchanged and keep reading one column. Three consequences, all deliberate and all recorded
in the file at the point of use:

1. **It cannot be written.** The intake flow now writes the two source columns. This is the reason
   the payload contract had to change (§2.3.4).
2. **`RequiredLevel` drops to `None`** — a calculated column cannot be required. The requirement
   moved to the two source columns, which is where it belongs.
3. **`IsAuditEnabled` drops to `0`** — Dataverse audits stored values, and a calculated value is
   computed on retrieve. **No audit coverage is lost**: both source columns are audited, so a name
   change is still fully evidenced (C-DOM-010/011).

All three of `rev_firstname`, `rev_lastname` and `rev_fullname` are secured. Securing the calculated
column while leaving its sources readable would have been security theatre.

**`rev_gender` classification, stated plainly because it is the kind of thing that gets assumed
wrong.** Gender is **ordinary personal data under UK GDPR, not special-category data.** Gender
reassignment is a protected characteristic under the Equality Act 2010, but it is not an Article 9
category — only data revealing sex life or sexual orientation is. So it is Tier 3, not Tier 4, and
is kept away from the condition columns. It is nonetheless **secured**, because it is
identity-adjacent and no eligibility, scoring or trustee decision uses it: least privilege
(C-DOM-020) puts it behind the profile. Emily's equality reporting is unaffected — `REV Admin` is a
profile member.

**Ethnic group (col 150) is NOT built, and the reason has changed.** It was excluded from the
committed schema at the SDD-intake gate pending DPO input (SDD OQ-027), and that gate has passed, so
this pass did not add it. But **the export proves the column is real**: OQ-027's framing of "where
captured" implied it might not be collected at all, and it is. That is a fact the reviewer and the
DPO should have when they revisit OQ-027 — the question is now "should we keep collecting it, and on
what basis", not "is it collected". Flagged in §7.4 and in the form specification's OPEN-17. **No
action taken here beyond recording it.**

#### 2.3.2 `rev_application` — the wellbeing off-by-one, and the maximum score

**The defect.** The build carried `rev_wellbeinganswer1` to `rev_wellbeinganswer11` **in addition
to** `rev_feelingscaleanswer` — twelve columns, and the scoring flow scored all twelve. The export
shows eleven questions:

| Export cols | What they are | Column |
|---|---|---|
| 95 | "Overall, how satisfied are you with your life nowadays?" (ONS life satisfaction), asked **first** | `rev_feelingscaleanswer` |
| 96–102 | The seven **SWEMWBS** statements | `rev_wellbeinganswer1`–`7` |
| 103–105 | Three "Thinking about the last year, have you been able to…" questions | `rev_wellbeinganswer8`–`10` |

Seven plus three is ten, plus the life-satisfaction answer is **eleven**. The twelfth column held no
question, so every application was being scored against a field that could only ever be empty.

**The fix.** `rev_wellbeinganswer11` deleted. Answers 1–10 remapped to cols 96–105, with each
column's description now naming the actual question it holds. Both flows updated: the intake flow no
longer accepts or maps `wellbeing_answer_11`, and the scoring flow's `Collect_wellbeing_answers`
array — which is the single definition of "the scored answers", used by both the sum and the
completeness check — now carries ten entries. **That array was checked specifically**, because a
leftover eleventh entry is the one place a stale reference would silently produce a wrong score
rather than an error.

> ⚠️➡️✅ **THE MAXIMUM SCORE: 60 → 55 IN REVISION 0.2, AND BACK TO 60 IN REVISION 0.3, WHERE IT IS
> NOW SETTLED. THE PARAGRAPHS BELOW ARE THE REVISION 0.2 POSITION AND ARE SUPERSEDED — kept because
> the reasoning is what the reviewer answered. Read §2.4.1 for what is actually built.**
>
> Ten Likert answers at 5 points plus one inverted five-point life-satisfaction answer is **55**.
> But the export header calls the field "Overall Circumstance Score (**out of 60**)", and
> `grant-application-data-model-v0.2.md` describes the life-satisfaction question as a **0–10 whole
> number** — which reconciles to exactly 60 (10 × 5 + 10). The committed `rev_feelingscale` option
> set has five options.
>
> **What was done:** `MaxCircumstanceScore` set to **55** in both settings files, with the reasoning
> written into the row's own description. 55 is what the flow can actually produce; leaving 60 would
> have made every score breakdown understate the applicant's position, which a trustee reads as
> evidence.
>
> **What was deliberately NOT done:** `rev_feelingscale` was not changed to a 0–10 scale. That would
> alter a scored option set, the `FeelingScaleInversion` map and the question presented to
> applicants, on inference from a summary document rather than a confirmed decision.
>
> **`rev_circumstancescore` keeps `MaxValue` 60** on purpose — it is a range ceiling, not a claim
> about attainability, and if the board confirms a 0–10 scale the maximum returns to 60 with no
> schema change.
>
> **Why this blocks something:** SDD OQ-001 (knockout threshold) and OQ-002 (borderline band) are
> **absolute scores**. The board cannot set them without knowing the maximum. See §7.5 D-3.
>
> ✅ **REVISION 0.3 RESOLUTION.** The reviewer confirmed the 0–10 reading. The picklist is gone,
> `rev_feelingscaleanswer` is a Whole Number 0–10, the inversion map has eleven entries, and
> `MaxCircumstanceScore` is **60** in both settings files. `rev_circumstancescore`'s `MaxValue` 60
> needed no change, exactly as this paragraph anticipated. **SDD OQ-001 and OQ-002 are unblocked.**
> §2.4.1.

#### 2.3.3 `rev_application` — everything else

**Removed:** `rev_wellbeinganswer11` (above) and `rev_financialanswers`.

**`rev_financialanswers` → eight typed columns** (cols 106–113). The blob held all financial detail
as one 2000-character free-text field. The export shows the live form asks eight separate typed
questions, so the blob was discarding structure the form already had: it could not be filtered,
reported on or checked for completeness, and every answer sat at one classification whether it was a
yes/no or a description of someone's medical costs. `rev_incomeband` (col 109) and `rev_incomeflag`
already existed and are untouched.

| Column | Type | Export col | Secured |
|---|---|---|---|
| `rev_receivesbenefits` | Yes/No | 106 | ✅ DERIVED |
| `rev_benefitprovider` | text 200 | 107 | ✅ DERIVED |
| `rev_currentlyworking` | Yes/No | 108 | ✗ |
| `rev_significantcarecosts` | Yes/No | 110 | ✗ |
| `rev_carecostsexplanation` | text area 2000 | 111 | ✅ |
| `rev_savingsover6000` | Yes/No | 112 | ✗ |
| `rev_unabletofundexplanation` | text area 2000 | 113 | ✅ |

**The classification rule applied throughout this pass, stated once:** *a column that invites the
applicant to **describe** their health, care, medical or personal circumstances in their own words is
`IsSecured=1`; a short structured answer (yes/no, choice, currency, date) about ordinary financial or
logistical facts is not.* Benefit status is the one structured answer that **is** secured, because
SDD §7.1 classifies it alongside health data at the highest restriction tier.

> ⚠️ **DERIVED DECISION FOR THE REVIEWER: this is stricter than what it replaced.**
> `rev_financialanswers` was `IsSecured=0` while holding exactly this content, including benefit
> status. Securing the benefit columns and the two explanations is a tightening, not a like-for-like
> port, and no source document asked for it — SDD §7.1's classification did. If the reviewer prefers
> the previous posture, the four `IsSecured` flags and four profile entries come out together.
> **Accept or reject.** §6.5.

**Everything else added**, all cited to the export:

| Group | Columns | Export cols |
|---|---|---|
| Cost breakdown | `rev_accommodationcost`, `rev_travelcost`, `rev_othercost` (currency); **`rev_costs` converted to calculated** = the sum of the three | 119–122 |
| Break type and location | `rev_breaktype` (choice, **placeholder**), `rev_otherbreaktype`, `rev_breaklocation` | 114–116 |
| Funding from other sources | `rev_receivingotherfunding`, `rev_otherfundingsource`, `rev_otherfundingamount`, `rev_awaitingdecisionfrom` | 124–127 |
| Exceptional funding | `rev_exceptionalfundingrequested`, `rev_exceptionalcircumstance` (choice, **placeholder**), `rev_otherexceptionalcircumstance` ✅, `rev_exceptionalfundingdetail` ✅, `rev_additionalamountrequested` | 128–132 |
| Group trip, applicant-facing | `rev_isgrouptrip`, `rev_groupmembernames` ✅ | 134–135 |
| Repeat funding history | `rev_receivedfundingbefore`, `rev_morethan12monthsago` | 136–137 |
| Consent — four real declaration blocks | `rev_granttermsconsent`+`date`, `rev_ageconfirmationconsent`+`date`, `rev_applicantconsent`+`date`, `rev_helperdeclarationconsent`+`date` | 12–14, 31–33, 46–48, 50–52 |
| Helper additions | `rev_helperorganisation`, `rev_helperrelationship` (choice, **placeholder**) | 44–45 |
| **OPEN-3 fix** | `rev_supportrecipientotherconditionraw` ✅ (ntext 2000, mirrors `rev_otherconditionraw` exactly) | 78 |
| **OPEN-2 fix** | `rev_carername` ✅ (text 100), `rev_carersupport` ✅ (text area 2000) | **none** — see below |
| Applicant's own care support | `rev_needscaresupportpersonally`, `rev_caresupportdescription` ✅ | 66–67 |
| Form-posted preference | `rev_wouldlikeformposted` | 148 |

✅ = `IsSecured=1` and released by `REV_TrusteeRestricted`.

**Four of these deserve a sentence each.**

- **`rev_costs` became calculated** = accommodation + travel + other, matching the export's own
  "Total estimated cost" header. This removes the class of defect where the parts and the total
  disagree and a trustee has to guess which is right. The **schema name is deliberately unchanged**
  so nothing referencing `rev_costs` has to move; only the display label changed, from "Estimated
  Costs" to **"Total Cost"**, which is what the export and the data model both call it. Same three
  consequences as `rev_fullname`: not writable, not required, not audited — with all three source
  columns audited, so no coverage is lost.
- **`rev_breaklocation` is trustee-visible and is deliberately NOT secured.** `-v0.2.md` marks it so,
  and the reasoning holds: a trustee cannot judge a request for a break without knowing where the
  break is, and it names a place rather than a person. It is the one reviewed exemption in
  `verify-field-security-coverage.py`, so nothing can add it to the profile by accident.
- **OPEN-2's two carer columns have no export column, and that is the point.** Every other addition
  in this pass maps to a column of the live form. These two do not: the old form never asked for the
  carer's name or the help they give, and the redesigned form does (form spec F12, F13). That is why
  this was a form-specification gap rather than an export-mapping gap, and why it could not have been
  found by reading the export alone.
- **`rev_ageconfirmationconsent` connects to SDD OPEN-14.** It is the only place the form asserts
  anything about the applicant's age other than the date of birth, so it is where whatever rule is
  agreed about under-18 applicants will land. **Phase 1 stores it and takes no automated action on
  it** — nothing branches or blocks on age, because no source says whether a person under 18 may
  apply in their own right.
- **`rev_grouplinkage` was clarified, not changed.** Its description now states that it is the
  process owner's own admin grouping (export col 7, "Group"), assigned by hand after the fact, and is
  **not** the applicant's answer — that is `rev_isgrouptrip` and `rev_groupmembernames`. The
  combined-amount check groups on `rev_grouplinkage`, and conflating the two would have broken it.
- **`rev_wouldlikeformposted` may be moot.** The export asks it (col 148), but the redesigned
  digital-first form may not offer a postal route at all, in which case nothing will ever set this
  column. Built for completeness; flagged as a question for Emily in §7.4.

**Referee and Emergency Contact columns are unchanged, and that is a decision, not an omission.**
See §7.5 D-6 — and note that revision 0.3 changed the *intake flow* here without changing these
*columns*: the five fields left the payload contract because the reviewer confirmed they are collected
on a separate post-approval form, while the five columns stay exactly as built because that is where
that form's answers will land. §2.4.2.

#### 2.3.4 The intake flow — a deliberately breaking payload contract change

| Field | Was | Is |
|---|---|---|
| Applicant name | `full_name` (required) | **`first_name` + `last_name`, both required** |
| Break cost | `costs` | `accommodation_cost` + `travel_cost` + `other_cost` |
| Financial detail | `financial_answers` (a question/answer array) | eight named typed fields |
| Wellbeing | `wellbeing_answer_1` … `_11` | `wellbeing_answer_1` … **`_10`** |
| Life satisfaction *(revision 0.3)* | `feeling_scale_answer` — option value **1–5** | `feeling_scale_answer` — whole number **0–10** |
| Referee and emergency contact *(revision 0.3)* | five fields accepted but not expected | **removed from the contract entirely** |

Plus **forty-two new optional fields** matching the columns above (revision 0.3 removes five of them
again — see §2.4.2 — leaving thirty-seven).

**A clean break was chosen over accepting both shapes.** Alex has not built the integration yet —
the form specification is still DRAFT and has never been issued as CONFIRMED — so there is no legacy
caller to support. The alternative, splitting `full_name` on whitespace as a fallback, gets compound
surnames wrong quietly and permanently, and a silent data-quality defect in an applicant's name is
worse than a loud contract change. **The failure mode if this is missed is severe and silent**: a
payload sending `full_name` stores no name at all, because the calculated column cannot be written.
The form specification carries this at the very top of the document, in its own banner.

**Other intake changes:**

- The **applicant match filter** now matches on `rev_email` + `rev_firstname` + `rev_lastname`
  rather than `rev_email` + `rev_fullname`. Filtering a calculated column is evaluated per row
  rather than by index, so matching the two stored columns is both correct and cheaper. OData
  single-quote escaping is unchanged (C-TECH-004/005).
- The **refresh branch** now also refreshes title, address line 2, town/city, applicant type and
  gender. It deliberately does **not** rewrite `rev_firstname`, `rev_lastname` or `rev_email` — those
  three are what the applicant was *matched on*, so rewriting them is either a no-op or evidence that
  the match was wrong. `rev_privacynoticeacceptedon` remains untouched for the original reason.
- The **FR-009 Teams notification** now composes the name from the two fields. It still carries the
  applicant's name, because FR-009 requires it, still to a 1:1 chat (ADR-015).
- The **completeness check**, its log message and its 400 response body all name the new required
  list: `submission_id, first_name, last_name, email, postcode, date_of_birth`.
  > **⚠️ Superseded by §2.6.2.** All three still agree, but on **four** fields:
  > `submission_id, first_name, last_name, postcode`. `email` and `date_of_birth` were removed in
  > revision 0.7 because the live form does not reliably collect either, so requiring them rejected
  > every real submission. Both are still **accepted**.

#### 2.3.5 Everything else touched

| File | Change |
|---|---|
| `Other/Solution.xml` | **Six type-9 option-set entries added.** No attribute entries were added, and none should be: the four tables are declared `behavior="0"` (include all subcomponents), so attributes ship with their table. A type-2 attribute entry alongside a `behavior="0"` table is redundant at best. 36 root components as at revision 0.2, **35 after revision 0.3 removed `rev_feelingscale`**; verified both directions each time |
| `FieldSecurityProfiles/REV_TrusteeRestricted.xml` | **17 → 34 field permissions**, plus a header note stating that every secured column must appear and that `rev_breaklocation` must not |
| `scripts/verify-field-security-coverage.py` | New. See §2.2 |
| `config/…-build.yml` | New `field-security-coverage` step. **FR-016 gate widened from four column names to twelve** — and note that the original four would *not* have caught `rev_supportrecipientotherconditionraw`, because it does not contain the substring `rev_otherconditionraw`. `rev_receivesbenefits` and `rev_benefitprovider` were added to the gate too: SDD §7.1 puts benefit status at the highest restriction tier, so it must not reach an automated decision either |
| `provisioning/deploymentSettings/{test,prd}-settings.json` | `MaxCircumstanceScore` 60 → **55**, with the open question written into the row's own description. **REVERSED IN REVISION 0.3: back to 60**, and `FeelingScaleInversion` replaced with an eleven-entry map — §2.4.1 |
| `Roles/REV Admin`, `Roles/REV Service Automation` | Comment only: the `prvReadTransactionCurrency` justification now names all seven money columns rather than two |
| `docs/development/…-form-validation-spec.md` | **Revision 0.2.** See §2.3.6 |

#### 2.3.6 The form specification — revision 0.2

- **OPEN-2 and OPEN-3 marked ✅ CLOSED**, each referencing the column that closed it.
- **Thirty-nine fields added** (F49–F87), each citing its export column. **F34 withdrawn** (the
  eleventh wellbeing statement never existed). **F41 demoted** from a question to an internal admin
  field. **F39 demoted** from an input to a display-only computed total.
- **The eleven wellbeing question texts are now the real ones from the export**, replacing invented
  wording. This substantially closes OPEN-1, which was the largest blocking item in revision 0.1 —
  what remains is the **response scale**, not the questions. Two scale problems were found and
  flagged rather than fixed: `rev_likertresponse` carries agree/disagree labels but the real
  questions are SWEMWBS items needing a *frequency* scale, and F35 is the ONS life-satisfaction
  question normally asked 0–10. Neither changes the option **values**, so the scoring configuration
  is unaffected either way. ✅ **BOTH FIXED IN REVISION 0.3** — the frequency labels are committed and
  F35 is a 0–10 scale, which closes OPEN-1 apart from the SWEMWBS licence question. §2.4.1, §2.4.3.
- **The payload contract change is the first thing in the document**, in its own banner, with the
  data-loss consequence spelled out.
- **The Ethnic Group note added** per §2.3.1.
- **Seven new open items** (OPEN-19 to OPEN-25), the most important being **OPEN-19**: the
  applicant-facing question count went from 47 to 82 because the live form asks all of it — but that
  form is the one producing part-completed applications 60% of the time, so length is plausibly a
  cause rather than an incidental feature. Emily should be asked which questions can be dropped or
  deferred, not just handed a longer form.

### 2.4 Revision 0.3 — three answers, three closures

Revision 0.2 raised three questions and deliberately did not decide them. The reviewer answered all
three. This is what changed as a result. **Nothing else was touched**, on purpose: this was a targeted
pass, and a small diff is what makes it reviewable.

#### 2.4.1 The score is out of 60 — the life-satisfaction question is a 0–10 scale

**The answer.** The Overall Circumstance Score is the life-satisfaction question (0–10) **plus** ten
wellbeing questions worth up to 5 each: **10 + 50 = 60**. That is the figure the export header has
always used ("Overall Circumstance Score (out of 60)"), the figure `grant-application-data-model-v0.2.md`
implies ("Whole number, 0-10"), and the figure the **Automation Solution Design v0.5** states outright
for Automation #2: *"Total = sum of all question scores (max 60)"*.

**So revision 0.2 had the arithmetic right and the schema wrong.** 55 was an accurate statement about
a five-option picklist that should never have been a picklist.

| # | Change | File |
|---|---|---|
| 1 | `rev_feelingscaleanswer`: `picklist` → **`int`, `MinValue` 0, `MaxValue` 10**. Display label "Feeling Scale Answer" → **"Life Satisfaction Answer"**. Logical name deliberately unchanged | `Entities/rev_application/Entity.xml` |
| 2 | `rev_feelingscale` option set **deleted**, and its `RootComponent type="9"` declaration removed in the same change (a comment marks where it was and why) | `OptionSets/rev_feelingscale.xml`, `Other/Solution.xml` |
| 3 | `FeelingScaleInversion`: five-entry map → **eleven-entry map keyed `"0"`–`"10"`**, values `10`–`0`. This *is* `10 − answer`, held as configuration | `{test,prd}-settings.json` |
| 4 | `MaxCircumstanceScore`: `55` → **`60`**, with the settled reasoning in the row's own description | `{test,prd}-settings.json` |
| 5 | `feeling_scale_answer` in the intake trigger schema now documented as **0–10 inclusive**, with an explicit instruction to send `0` rather than omit it | intake flow |
| 6 | The scoring flow's `Invert_the_feeling_scale_answer`, `Calculate_circumstance_score`, `Read_LikertPointMap` and top-level descriptions rewritten for 60; the score-breakdown text now reads "Life-satisfaction answer *n* out of 10, inverted = *m* points" | scoring flow |
| 7 | `rev_circumstancescore` — **no change needed.** `MinValue` 0 / `MaxValue` 60 and "out of sixty" were already correct; revision 0.2 kept the ceiling at 60 on purpose, and that decision paid for itself here | — |

**Whole Number rather than an eleven-value option set — the choice, and why.** Three reasons, and the
second is the one that would have caused a real defect:

1. **On a 0–10 scale the number is the answer.** An option set would carry eleven labels that repeat
   their own values, and the label of a scored answer is exactly the thing that must not drift (the
   score breakdown records option *values*, not labels, for this reason).
2. **Option value `0` is not a safe picklist value in Dataverse.** It is widely treated as "no
   value", which would make *worst possible wellbeing* indistinguishable from *unanswered* — and this
   is the one answer whose absence must withhold the automated outcome under FR-022. As an `int`,
   `0` is a real value and `null` is absence; the FR-022 gate's `empty(coalesce(string(...), ''))`
   test distinguishes them correctly, because `string(0)` is `"0"` and `string(null)` is `""`.
3. **It matches how this schema already expresses a numeric range.** `rev_circumstancescore` is an
   `int` bounded by `MinValue`/`MaxValue`; picklists in this solution are used for *categorical*
   answers (title, gender, break type, condition profile), which is what they are for.

**The inversion, applied and verified rather than assumed.** The source is explicit: *"Q1 ('How are
you feeling?') is inverted (0/10 feeling = 10 points)"*. The contribution is **`10 − raw answer`** —
a raw 0 (worst self-reported wellbeing) contributes **10** points of need, a raw 10 contributes **0**.
**The flow was already inverting**, and that is the trap this fix had to avoid: it was inverting the
*old five-point scale* through a five-entry map, so it produced at most 5 points and silently capped
the maximum at 55. Correcting the field type alone would have left an expression that reads `map["7"]`
against a map with no key `"7"` — a null, a failed `int()` cast, and a scoring run that dies on a
perfectly valid application. **The map and the column had to move together, and they did.** The
expression itself is unchanged, because the inversion has always been a table lookup rather than
arithmetic (FR-012, NFR-019): the direction of the scale stays configuration the board can change
without a solution change.

**Consequence for the board.** SDD OQ-001 (knockout threshold) and OQ-002 (borderline band) are
**absolute scores**, and they were blocked on this. **They are now unblocked** — the scale is fixed at
0 to 60. The provisional TST/ACC values (knockout ≤ 20, borderline 21–30) were set against a 0–60
scale in the first place and are unchanged; PRD still holds `{{PENDING_OQ_001}}` / `{{PENDING_OQ_002}}`
tokens, so production cannot be seeded until the board decides.

#### 2.4.2 Referee and Emergency Contact leave the intake flow entirely

**The answer.** They are collected on a **separate form, sent to the relevant party after the board
approves the grant** — not on the intake form, and not by any mechanism this flow touches.

That voids the reason revision 0.2 gave for keeping them in the payload contract. Revision 0.2's
argument was "removing the only route that can write these columns would leave them unreachable";
the route is now known to be a different form in a different automation, so the intake contract was
claiming an ability it should never exercise.

| Change | Detail |
|---|---|
| **Trigger schema** | `referee_name`, `referee_email`, `referee_phone`, `emergency_contact_name`, `emergency_contact_phone` **removed** as properties |
| **`Create_application` mapping** | The five `rev_referee*` / `rev_emergencycontact*` mappings **removed** |
| **Count corrected while there** | The create step's own description claimed "ELEVEN SECURED COLUMNS ARE WRITTEN HERE" and then listed thirteen names plus a hand-wave. It now names the **seventeen** secured columns it actually writes, exhaustively, and states that `rev_application` carries **22** secured columns in total — the other five being these |
| **Columns: NO CHANGE** | `rev_refereename`, `rev_refereeemail`, `rev_refereephone`, `rev_emergencycontactname`, `rev_emergencycontactphone` stay on `rev_application` exactly as built, still `IsSecured=1`, still released by `REV_TrusteeRestricted`. `verify-field-security-coverage.py` still reports **34 secured columns, all released** — that check pairs columns with permissions and is indifferent to who writes them |

**What this means in practice.** Those five columns are now written by nothing in Phase 1. That is
correct rather than a gap: they are the destination for the post-approval form's answers, and the
process owner can fill them in by hand in the meantime — she has create and write on them through
the profile.

**The residual open question, stated precisely because it is easy to lose.** The *mechanism* is
confirmed (separate form, after board approval). **What is not specified is who receives and completes
it** — the applicant relaying the referee's and emergency contact's details, or the referee and
emergency contact self-reporting their own. Those are materially different designs: the second needs a
per-recipient link, a way to identify the right person, and a lawful-basis and privacy-notice position
for contacting a third party the charity has no relationship with. **That belongs to Automation #3
(Grant Acceptance, Phase 2) and is not buildable or decidable here.** Recorded in §7.4 and §7.5 D-6.

#### 2.4.3 The wellbeing answer labels are a frequency scale

**The answer.** The five labels for all ten wellbeing questions (export columns 96–105) are
**None of the time / Rarely / Some of the time / Often / All of the time**, in that order,
lowest frequency first. `rev_likertresponse` now carries exactly that, replacing the
agree/disagree labels written when the question wording was unknown.

**Why the labels were wrong and this wording is right.** The live form's own stem for columns 96–102
is *"Please say what best describes your experience of each over the last 2 weeks"*, and columns
103–105 are *"Thinking about the last year, have you been able to (…)"*. Neither is answerable with
"strongly agree". The frequency scale is also SWEMWBS's published response scale, which matters
because the seven SWEMWBS items are a validated instrument whose wording and scale go together.

**The option set's name is unchanged, deliberately.** `rev_likertresponse` remains accurate — *Likert*
describes the ordered five-point response format, not agreement specifically — and renaming it would
touch ten column definitions, a root-component declaration and two documents to buy nothing.

> **THE VALUE DIRECTION WAS CHECKED, NOT ASSUMED — and it is correct, so nothing changed.**
>
> The instruction for this pass was to change values only on finding a genuine mismatch. Here is what
> was checked and what was found, so the reviewer does not have to take it on trust.
>
> **What was checked:** the real wording of each of the ten questions, from the export header, one at
> a time — not the first one and then an inference. Columns 96–102: "I've been feeling optimistic
> about the future", "…feeling useful", "…feeling relaxed", "…dealing with problems well", "…thinking
> clearly", "…feeling close to other people", "…able to make up my own mind about things". Columns
> 103–105: "…able to go out and do something you enjoy", "…able to enjoy other people's company",
> "…able to have a break when you've needed one".
>
> **What was found: all ten are worded POSITIVELY. There is no reverse-worded item in the set.** So
> for every one of them, a *higher* frequency describes *better* wellbeing and therefore *less* need,
> and value 1 ("None of the time") is the highest-need answer.
>
> **Therefore `LikertPointMap` = `{"1":5,"2":4,"3":3,"4":2,"5":1}` is correct as it stands**, and the
> same inversion logic as the life-satisfaction question is already in force here — it just lives in
> the point map rather than in a separate inversion map. **No value, no mapping and no scoring
> configuration changed.** The Automation Solution Design's own mapping is by *ordinal position*
> ("Strongly Disagree = 5 … Strongly Agree = 1" — position 1 scores 5), and relabelling position 1
> from "Strongly Disagree" to "None of the time" preserves that exactly.
>
> **If a reverse-worded item is ever added** (for example "I've been feeling anxious"), it cannot use
> this shared point map, and that is the thing to watch for — not the labels.

**What this closes.** Form-spec OPEN-1 is closed apart from one question that blocks nothing: whether
Revitalise holds a **SWEMWBS licence**, which it needs if it intends to report scores against national
norms. The build is unaffected either way — the wording and scale are now used as published, which is
the condition a licence would impose.

---

### 2.5 Revision 0.5 — making the solution actually pack

Reference: nothing in the TAD or SDD. This section is about the **packaging layer only** —
where a component's XML file must live, and which XML construct must carry its name and GUID.
No requirement, design decision, privilege or data value changed.

#### 2.5.1 How the requirements were established (not guessed)

`pac solution pack` is implemented by `SolutionPackagerLib.dll`, shipped inside `pac`. It was
decompiled and read:

```bash
export PATH="$PATH:/Users/xvl/.dotnet/tools"
DLL=".../microsoft.powerapps.cli.tool/2.4.1/.../SolutionPackagerLib.dll"
ilspycmd -l c "$DLL" | grep -i processor          # enumerate the component processors
ilspycmd -t "Microsoft.Crm.Tools.SolutionPackager.RoleProcessor" "$DLL"
```

Two things read out of the DLL explain every defect below, and both are worth knowing before
touching this source again.

**(a) The authoritative folder/filename table.** There is no configuration file to consult —
`ComponentConfigurationManager` asks `ConfigurationManager.GetSection("ComponentConfigurations")`,
which is **absent from `pac.dll.config`**, so the defaults compiled into
`ComponentConfigurationCollection`'s constructor are the whole truth. The rows that matter here:

| ComponentType | directory | file |
|---|---|---|
| `Entity` (1) | `Entities` | `$(PrimaryName)/Entity.xml` |
| `OptionSet` (9) | `OptionSets` | `$(PrimaryName)` |
| `EntityRelationship` (10) | `Other` | `Relationships.xml` |
| `Role` (20) | `Roles` | `$(PrimaryName)` |
| `Workflow` (29) | `Workflows` | `Workflows.xml` |
| `SiteMap` (62) | `Other` | `$(type)$(managed).xml` |
| `FieldSecurityProfile` (70) | `Other` | **`$(type)s.xml`** |
| `AppModule` (80) | `AppModules` | `$(PrimaryName)/AppModule$(managed).xml` |
| `AppModuleSiteMap` (81) | **`AppModuleSiteMaps`** | `$(PrimaryName)/AppModuleSiteMap$(managed).xml` |
| `EnvironmentVariableDefinition` (380) | **`EnvironmentVariables`** | `$(PrimaryName).xml` |

The three bolded cells are where the hand-authored source had invented a plausible folder that
the packer never looks in.

**(b) `Other/Customizations.xml` is the packer's work list, not a formality.**
`DiskReader.Load` enumerates the **children of that file's root element**; for each *childless*
one it resolves a processor **by element name** and calls `ReadFromFiles()`. A component type
with no element there is never processed — its folder is never opened and nothing is reported,
because nothing was asked for. This is the single most surprising thing in the packer and the
cause of three of the nine defects.

#### 2.5.2 The nine defects, the evidence, and the fix

| # | Component | What was wrong | Decompiled evidence | Fix | Failure mode |
|---|---|---|---|---|---|
| **1** | **`OptionSets/*.xml` (all 15)** | Each file wrapped its `<optionset>` in a redundant outer `<optionsets>` root. `ReadCollectionFromFolder` treats **each file's root element as one collection item**, so the packer read 15 items named `optionsets`, not 15 option sets | `OptionSetProcessor.CreateComponent`: `PrimaryName = Helper.GetAttributeValue(element, "Name", throwIfNull: true)` | Outer `<optionsets>` removed from all 15; the `<optionset Name="…">` element is now the file root, exactly as `Entity.xml` puts `Name` on its root | **LOUD** — `Cannot find child attribute Name of element optionsets` |
| **2** | **`Roles/*/*.xml` (both)** | `<RoleId>` and `<Name>` as child elements | `RoleProcessor.CreateComponent`: `Id = GetAttributeValue(element, "id", …)`, `PrimaryName = GetAttributeValue(element, "name", …)` — **both `throwIfNull: false`**, so they returned null and the role got the key `"Role-"` | `<Role id="{…}" name="…">`. **`<RolePrivilege name= level= />` was already correct** — the file was half right, which is why nothing looked odd | **SEMI-SILENT** — no error at the read; surfaced far downstream as `Following objects, required by the solution, are not present … Id='Role-'`, a message that names neither the file nor the real cause |
| **3** | **`Workflows/*/*.xml` (all 4)** | Files were `<name>/<name>.xml`. The packer globs **`*.data.xml`** and expects the metadata flat in `Workflows/` | `WorkflowProcessor` sets `isFileBackedComponent`; `ComponentProcessorBase.ReadFromFiles` → `Directory.GetFiles(dir, "*.data.xml", AllDirectories)`. `DiskFileName = Path.Combine("Workflows", LanguageCode ?? "", Path.GetFileName(flowName))` | Flattened to `Workflows/<Name>-<GUID>.json` + `Workflows/<Name>-<GUID>.json.data.xml`; `<JsonFileName>` updated to `/Workflows/<Name>-<GUID>.json`. **The XML content was already correct** — `WorkflowId` and `Name` were already attributes | **SILENT** — `Processing Component: Workflows` printed, then read zero files. All four flows were missing from the package |
| **4** | **Field security profile** | Lived at `FieldSecurityProfiles/REV_TrusteeRestricted.xml`; id and name were child elements | `FieldSecurityProfileProcessor` reads **one** path (`Other/FieldSecurityProfiles.xml`) and `return null` if absent. `PrimaryName = GetAttributeValue(element, "name", throwIfNull: true)`, `Id = GetAttributeValue(element, "fieldsecurityprofileid", …)` | Moved to `Other/FieldSecurityProfiles.xml`; `<FieldSecurityProfile name="…" fieldsecurityprofileid="{…}">`. All **34** `<FieldPermission>` entries untouched | **SILENT — the worst one.** Pack succeeded and shipped 34 `IsSecured=1` columns with no profile releasing them. In Dataverse that is 34 columns **nobody but a System Administrator can read** — and the process owner is deliberately not one (ADR-019). The symptom in TST would have been blank fields nobody could explain, plus intake writes failing |
| **5** | **Entity relationship** | `Other/Relationships.xml` **did not exist**. Only the detail file did | `EntityRelationshipProcessor.ReadFromFiles` reads `Other/Relationships.xml` first and `return null` if missing; it then merges each detail file's `<EntityRelationship>` children into the childless stubs it finds there | Created `Other/Relationships.xml` holding one childless stub. Detail file **renamed `rev_application.xml` → `rev_applicant.xml`** because `GetEntityRelationshipFileName` groups a `OneToMany` by its `ReferencedEntityName` — the old name would have collided with what a future `pac solution unpack` writes, and two files declaring one `@Name` is a hard `DuplicatedRelationshipName` error | **SILENT** — the parental cascade that the entire retention design depends on (ADR-004) was not in the package |
| **6** | **`<AppModules />` missing from `Customizations.xml`** | The folder and file were **correct**; nobody asked for them | `DiskReader.Load` iterates the children of `Customizations.xml`'s root to decide what to process | Added `<AppModules />` | **SILENT** — the model-driven app was swept in as an anonymous sharded file |
| **7** | **App sitemap** | At `AppModules/rev_grantadministration/AppModuleSiteMap.xml`, root `<SiteMap>`, no `SiteMapUniqueName`, and `<AppModuleSiteMaps />` missing from `Customizations.xml` | `AppModuleSitemapProcessor`: directory `AppModuleSiteMaps`; `PrimaryName = Helper.GetElementValue(element, "SiteMapUniqueName", throwIfNull: true)` — **a CHILD ELEMENT, the opposite of #2/#4** | Moved to `AppModuleSiteMaps/rev_grantadministration/AppModuleSiteMap.xml`; root is `<AppModuleSiteMap>` with `<SiteMapUniqueName>rev_grantadministration</SiteMapUniqueName>`. `<sitemapid>` kept — `AppModule.xml`'s `type="62"` component reference points at it | **SILENT** |
| **8** | **Environment variable definitions (all 3)** | At `environmentvariabledefinitions/<name>/environmentvariabledefinition.xml` — the modern `pac solution sync` source format, which this legacy-format solution is not | `EnvVariablesProcessor` reads `RootFolder/EnvironmentVariables` only. `GetName` accepts the `schemaname` **attribute** (already correct) | Moved to `EnvironmentVariables/<schemaname>.xml`; added `<EnvironmentVariables />` to `Customizations.xml` | **SILENT** — all three swept in as sharded files, so `rev_ProcessOwnerUpn` and friends would not have existed to inject values into |
| **9** | **`RootComponent` key form for types 62 and 80** | Declared by GUID: `type="80" id="{d4f6a8b0-4001-…}"`, `type="62" id="{d4f6a8b0-4002-…}"` | `RootComponentsValidation.ComponentInfo`: the key is `id.ToString("b")` **only when `Id != Guid.Empty`**, otherwise `"<Type>-<name>"`. `AppModuleProcessor` and `AppModuleSitemapProcessor` **never set `Id`**, so their key is always name-based; `AppModuleSiteMap` is additionally folded into `SiteMap` | `type="80" schemaName="rev_grantadministration"` and `type="62" schemaName="rev_grantadministration"`. Both GUIDs still live where they belong — `<appmoduleid>` and `<sitemapid>` | **LOUD, once #6/#7 were fixed** — an unmatched component is fatal in that direction. Fixing the app and sitemap is what *exposed* this |

**A note on `<Managed>` and the remaining warnings, because both look like defects and are not:**
see §2.5.3 and §2.5.4.

#### 2.5.3 The Managed package type — one digit in the manifest

`--packagetype Managed` failed with `Solution package type did not match requested type`.
`Helper.LoadSolutionInformation` parses `<Managed>` straight into the `SolutionPackageType` enum
(`Unmanaged=0, Managed=1, Both=2`) and, for `CommandAction.Pack`, throws unless the value is
`Both` **or** exactly equals the requested type. `<Managed>0</Managed>` therefore permitted
Unmanaged and *only* Unmanaged.

This repo's stated solution type is "Managed (Test / Prd) | Unmanaged (Dev only)" — one source,
both artefacts — so the manifest must say `Both`. Two independent confirmations that `2` is the
intended value rather than a workaround:

1. `pac solution init` was run into a scratch directory and its generated skeleton emits
   `<Managed>2</Managed>`, above the comment
   `<!-- Solution Package Type: Unmanaged(0)/Managed(1)/Both(2)-->`.
2. When `PackageType == Both`, the packer *itself* stamps the resolved value into the packaged
   manifest: `xElement.Element("Managed").Value = IsManaged ? "1" : "0"`. Verified in the output
   — the Managed .zip contains `<Managed>1</Managed>`, the Unmanaged .zip `<Managed>0</Managed>`.
   The shipped artefact is still unambiguously one or the other.

`Other/Solution.xml` now carries `<Managed>2</Managed>` with that reasoning inline.

A second consequence of the same code path, worth recording because it is why no
`*_managed.xml` duplicates were needed: `version="9.2.0.0"` on `<ImportExportXml>` is above the
`9.1.0.22716` threshold that sets `context.UseUnmanagedFileForManaged = true`, so the Managed
pack falls back to the unmanaged `AppModule.xml` / `AppModuleSiteMap.xml` instead of demanding
`_managed` variants.

#### 2.5.4 Proof: four clean packs, and the packages opened and inspected

Both package types, on **both** `pac` installations available (the defect reproduced on both, so
the fix is verified on both — it was never a version issue). Verbatim:

```
$ pac solution pack --zipfile /tmp/final-241-Unmanaged.zip \
    --folder src/solutions/RevitaliseGrantAutomation --packagetype Unmanaged --errorlevel Info
Processing Component: Entities
 - rev_setting
 - rev_application
 - rev_errorlog
 - rev_applicant
Processing Component: Roles
Processing Component: Workflows
 - REV | Intake | WordPress to Dataverse
 - REV | Ops | Failure Alert
 - REV | Scoring | Calculate & Flag
 - REV | Scoring | Daily Summary
Processing Component: FieldSecurityProfiles
Processing Component: Templates
Processing Component: EntityMaps
Processing Component: EntityRelationships
Processing Component: OrganizationSettings
Processing Component: optionsets
Processing Component: CustomControls
Processing Component: AppModuleSiteMaps
Processing Component: AppModules
Processing Component: SolutionPluginAssemblies
Processing Component: EntityDataProviders
Processing Component: EnvironmentVariables
 - rev_IntakeAllowedClientId
 - rev_ProcessOwnerUpn
 - rev_ServiceMailbox
Processing Sharded Component Files
Following root components are not defined in customizations:
  Type='EntityRelationship', Id (or schema name)='EntityRelationship-rev_applicant_rev_application_applicantid'.
  Type='EnvironmentVariableDefinition', Id (or schema name)='EnvironmentVariableDefinition-rev_ProcessOwnerUpn'.
  Type='EnvironmentVariableDefinition', Id (or schema name)='EnvironmentVariableDefinition-rev_ServiceMailbox'.
  Type='EnvironmentVariableDefinition', Id (or schema name)='EnvironmentVariableDefinition-rev_IntakeAllowedClientId'.
  Type='10371', Id (or schema name)='GenericComponent-rev_SharedDataverse'.
  Type='10371', Id (or schema name)='GenericComponent-rev_SharedTeams'.
  Type='10371', Id (or schema name)='GenericComponent-rev_SharedOutlook'.

Unmanaged Pack complete.

Packed Solution.
$ echo $?
0
```

`--packagetype Managed` produces byte-identical output but for `Managed Pack complete.`, and
`pac` 2.9.3 produces the same result for both types. All four exit `0`.

**The seven remaining lines are warnings, not errors, and they cannot be removed without
breaking the import.** `RootComponentsValidation` validates in two directions with two very
different severities: a component on disk that is *not* declared is **fatal**
(`CustomizationsNotInRootComponents` → `throw`), while a declaration the validator did not tick
off is a **warning** only. The three types listed are exactly the types the validator does not
inspect — its `RootComponentTypes` array (32 entries) contains neither `EntityRelationship`,
nor `EnvironmentVariableDefinition`, nor connection references, so their declarations can never
be ticked off no matter how correct they are. `Type='10371'` prints as a bare number for the
same reason: `10371` is not a member of the `ComponentType` enum (`GenericComponent` is `99999`),
so `Enum.IsDefined` fails and the validator falls back to a `GenericComponent-<name>` key.
Deleting these declarations to silence the warnings would delete the relationship, the three
environment variables and the three connection references **from the solution**.

**Because six of the nine defects were silent, a clean log is not accepted as proof.** Both
.zip files were unpacked and their `customizations.xml` read:

| Element | Unmanaged | Managed | Expected |
|---|---|---|---|
| `Entities` | 4 | 4 | 4 |
| `Roles` | 2 (`REV Admin`, `REV Service Automation`) | 2 | 2 |
| `Workflows` | 4, all with `WorkflowId` | 4 | 4 |
| `FieldSecurityProfiles` | 1 (`REV_TrusteeRestricted`, **34** permissions) | 1 | 1 |
| `EntityRelationships` | 1, **16 children** — the definition merged, not an empty stub | 1 | 1 |
| `optionsets` | 15 | 15 | 15 |
| `AppModules` | 1 (`rev_grantadministration`, 5 components) | 1 | 1 |
| `AppModuleSiteMaps` | 1 (`rev_grantadministration`, `SiteMapXml` intact) | 1 | 1 |
| `EnvironmentVariables` | 3 | 3 | 3 |
| `connectionreferences` | 3 | 3 | 3 |
| `<Managed>` | **0** | **1** | per package type |
| `RootComponents` | 35 | 35 | 35 |

And the archive itself is now exactly what a real solution export contains — **7 entries, no
strays**:

```
customizations.xml
solution.xml
Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json
Workflows/REVOpsFailureAlert-8F1C2A44-1004-4B7A-9E21-0A1B2C3D4E04.json
Workflows/REVScoringCalculateAndFlag-8F1C2A44-1002-4B7A-9E21-0A1B2C3D4E02.json
Workflows/REVScoringDailySummary-8F1C2A44-1003-4B7A-9E21-0A1B2C3D4E03.json
[Content_Types].xml
```

The absence of `AppModules/…`, `FieldSecurityProfiles/…` and `environmentvariabledefinitions/…`
as loose files in that list is the positive evidence that defects #4, #6, #7 and #8 are closed:
previously those folders were swept in here as raw sharded files instead of being registered as
components.

#### 2.5.5 The repo's own checks were wrong too, and agreed with the bug

Both verification scripts hard-coded the broken layout, and both returned **PASS** against a
solution that could not pack. That is a worse failure than having no check, so both were
corrected to assert the packer-verified forms — meaning each would now have **failed** the old
source:

| Script | Was asserting | Now asserts |
|---|---|---|
| `verify-solution-root-components.py` | `<RoleId>` child; `<sitemapid>` under `AppModules/*/`; `<appmoduleid>`; `FieldSecurityProfiles/*.xml`; `environmentvariabledefinitions/*/`; `Workflows/**/*.xml` | `<Role id="…">`; `<SiteMapUniqueName>` under `AppModuleSiteMaps/*/`; `<uniquename>`; `Other/FieldSecurityProfiles.xml`; `EnvironmentVariables/*.xml`; `Workflows/**/*.data.xml` |
| `verify-field-security-coverage.py` | `FieldSecurityProfiles/` folder exists | `Other/FieldSecurityProfiles.xml` exists, with an error message that states the consequence |

Both PASS after the fix — 35 root components resolved in both directions, and 34 secured columns
each released by a profile with one reviewed exemption (`rev_breaklocation`).

`config/revitalise-grant-automation-build.yml` needed no change: its `pack-managed` and
`pack-unmanaged` steps already invoked the two commands this revision made work.

#### 2.5.6 What did NOT change

Stated explicitly because a structural correction of this size invites the question. No
requirement, no ADR, no privilege, no permission, no data value, no flow logic:

* **40** role privileges on `REV Admin`, **33** on `REV Service Automation` — counted after the edit
* **34** field permissions, and `rev_breaklocation` still deliberately absent
* **15** option sets with every value and label; **122** `IsAuditEnabled` columns across the four tables
* All four flow definition JSON bodies — untouched, byte for byte
* Cascade profile on the relationship still `Cascade` on all five behaviours (ADR-004 retention)
* No `<defaultvalue>` on any environment variable; no connection ID anywhere (C-TECH-031 holds)

Where a file header had recorded the wrong guess as fact, the comment now records the packer's
actual requirement **and the evidence for it**, so the same mistake cannot be re-authored:
`Other/FieldSecurityProfiles.xml`, `Other/Relationships.xml`,
`Other/Relationships/rev_applicant.xml`, `AppModuleSiteMaps/…/AppModuleSiteMap.xml`, all three
`EnvironmentVariables/*.xml`, `Other/Customizations.xml` and `Other/Solution.xml`.

---

### 2.6 Revision 0.7 — the payload contract meets the form that exists

#### 2.6.1 How the live form was established, and how far it can be trusted

Three sources, and it matters which claim rests on which.

| Source | Establishes | Limit |
|---|---|---|
| The live page's HTML, fetched with `curl` 2026-08-13 | Every field, its Gravity Forms id, control type, required marker, maximum length, every option label and value, all 20 page breaks | Authoritative for structure. `gfield_contains_required` is what the browser receives |
| `window.gf_form_conditional_logic[3]` — the form's own embedded logic map | All 23 conditional-logic rules verbatim, with trigger field and trigger value | Authoritative for conditional logic, with one honest caveat: it is the **client-side** map. Gravity Forms evaluates the same rules server-side from the same definition, but a plugin could add one that is not here. Every "no rule exists" claim is scoped to this map and is flagged as worth confirming with Alex |
| `docs/Import/Application Data Export(Sheet1).csv` | The 163 export columns in order, plus the charity's own commentary on several | **It is not applicant data.** The file has two rows: the header and one row of annotations. No claim about historic data quality is drawn from applicant records, because the file contains none |

**A deliberate methodological note.** The markdown-conversion fetch tool was **not** used for the
audit claims. It is lossy on attributes, and the whole point of this pass was attribute-level facts —
`autocomplete`, `aria-required`, `maxlength`, `step`, `type`. Raw HTML was fetched and grepped
directly. That is also why the `autocomplete` count is stated as "five occurrences, none of them a
valid purpose token" rather than "zero occurrences": an earlier read in the same session reported zero,
the raw HTML has five, and the five are one honeypot `new-password` and four `off`. **The conclusion
holds and the number does not**, which is exactly the kind of thing worth correcting rather than
rounding.

**One column of the CSV did most of the work in the change request.** Column 9, "Notes", is annotated
by the charity: *"typically, this is why the application is incomplete. Normally standardised as the
following missing items — Location, Age Confirmation, Date, Amount, Disability Information"*. Column 8
adds that non-qualification reasons include *"age being under 18"* and *"location of applicant (not
holiday) being not in the UK"*. That is the charity naming its own five recurring failures, and every
one of them maps onto a specific, verifiable weakness in the live form. Those five are the ones marked
**[charity-evidenced]** in spec §7 and they are the ones to do first. **The change request is grounded
in the charity's own record of what goes wrong, not in a list of things a form ought to do.**

#### 2.6.2 The intake flow — six edits, and why each one is a bug fix rather than a relaxation

`Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json`

| # | Edit | Why |
|---|---|---|
| 1 | Trigger `required` → `[submission_id, first_name, last_name, postcode]` | All four are unconditional and required on the live form, so a real submission always carries them. `email` and `date_of_birth` are **still accepted** — removing a field from `required` is not removing it from the contract |
| 2 | `Reject_incomplete_payload` loses its `email` and `date_of_birth` clauses; the 400 body and the `Log_incomplete_payload` message move with it | The guard, the response and the log line are three statements of the same contract. Any one drifting is a lie to the integrator, and there is now a test asserting all three agree |
| 3 | `age_range` (string) added to the schema; new `Read_age_range_label_map` + `Map_age_range_label`; `Derive_age_range` rewritten | The live form asks an age **band** and never a date of birth. The band is now the primary source for `rev_agerange`, the `AgeBandMap` date-of-birth path is retained as a fallback for a future form version, and when neither is available the flow writes 9 (Not known) — which is what `rev_agerange`'s own description already promised: *"the flow never guesses"* |
| 4 | `rev_dateofbirth` and `rev_email` wrapped in `if(empty(coalesce(…, '')), null, …)` on `Create_new_applicant` | `formatDateTime(null, …)` throws and `trim(null)` throws. Both paths were unreachable while the fields were required; edit 1 makes both reachable on **every** real submission. Fixing 1 without fixing this would have turned a clean 400 into a failed run |
| 5 | `Find_existing_applicant`'s `$filter` branches: email + first + last when an email is present, first + last + **postcode** when it is not | Same `trim(null)` problem, plus a real design question: with no email there has to be *some* identity to match on. Name and postcode is the only one the form guarantees. **The weaker match is stated rather than hidden** — two people with the same name at the same address would merge, which is unlikely and is the lesser evil against creating a duplicate applicant for every postal-preference person who applies twice |
| 6 | `group_linkage` removed from the schema; `rev_grouplinkage` removed from `Create_application` | CSV column 7 is annotated "Group Number - **generated** to link applications" — the process owner's own admin grouping, assigned by hand after the fact. The form does not ask it, and a public endpoint should not be able to write it. The form document has said "do not send `group_linkage`" since revision 0.2 while the flow quietly accepted it |

**On C-TECH-004, because edit 1 looks like a weakening and is not.** C-TECH-004 is "all user inputs
must be validated and sanitised before processing or persistence". Requiring a field the source never
sends is not validation — it is a rejection of valid input, and the outcome it produces is the one
FR-010 exists to prevent: an application that appears to have been submitted and does not exist
anywhere. The typed schema is unchanged (82 properties, `feeling_scale_answer` still bounded 0–10 by
the column itself), the completeness check still runs before any write, and edits 4 and 5 make the flow
strictly more defensive than it was. **The validation got more accurate, not looser.**

**On why the eleven scored answers are still not required.** D-003's second half demanded them as
"never null". They are all marked `*` on the live form, so in practice they arrive — but a missing
scored answer must **withhold the score and route to a person** (FR-022), not reject the application.
For an applicant, "slower, handled by a human" beats "submitted into nothing".

#### 2.6.3 Configuration — one new `rev_setting` row

`AgeRangeLabelMap` (JSON) in both `test-settings.json` and `prd-settings.json`, byte-identical:
eight labels the live form actually sends → `rev_agerange` options 2–8 and 9. Matched
case-insensitively after trimming.

It is a settings row rather than a literal in the flow for the reason the repo already applies to
`AgeBandMap` and `PostcodeRegionMap`: **if Alex renames a label on the form, the fix is a configuration
change, not a deployment.** It sits with the six existing policy/reference rows that must be identical
across environments, not with the three board-criteria rows that legitimately differ — so it carries
no `{{PENDING}}` token, and `seed-settings.ps1` needed no change because it is entirely data-driven off
`dataverse.settingRows`. The pipeline config's step description moves from "ten rev_setting rows" to
eleven.

#### 2.6.4 Tests — the suite caught the change it was supposed to catch

`src/tests/solutions/IntakeContract.Tests.ps1` existed **specifically** to make a silent change to the
payload contract impossible, and it did its job: it failed the moment the required list changed, which
is the correct behaviour for a published-contract test. It was updated deliberately, not silenced.

- The six-field assertion becomes a four-field assertion, with the reason recorded in the test itself.
- **New:** the reject guard, the 400 body and the log line are asserted to name the *same* four fields,
  and to **not** name `email` or `date_of_birth`. That coupling was previously only in a comment.
- **New:** `email` and `date_of_birth` are asserted to still be **accepted** — so a future edit cannot
  quietly drop them from the schema on the strength of "they are not required".
- **New:** `age_range` is asserted present and typed `string`.
- **New:** `group_linkage` and `rev_grouplinkage` join the removed-from-the-contract list, plus a
  direct assertion that `Create_application`'s item map contains no `grouplinkage`.
- **New Describe block, five assertions:** the band map is read from `AgeRangeLabelMap`; the band is
  tested **before** the date-of-birth path in the expression (asserted by string position, so a
  reordering fails); the fallback is 9; both null-guards are present; the applicant lookup has the
  no-email branch and still matches on email when one exists.
- `DeploymentSettings.Tests.ps1`: ten setting rows → eleven, and `AgeRangeLabelMap` added to the
  identical-across-environments policy list.

**Full suite: 537 passed, 0 failed, 1 skipped** (`pwsh -c "Invoke-Pester -Path src/tests"`, Pester
5.7.1). The C-TECH-005 escaping assertions pass against the new two-branch `$filter` without
modification — the new postcode interpolation goes through the same `replace(x, '''', '''''')`
doubling, and the test walks every filter in the definition rather than a named list.

#### 2.6.5 What the reviewer should look at hardest

Not the code — it is small and tested. **The three judgement calls:**

1. **The four-field required list.** Is `first_name`/`last_name`/`postcode` the right floor? A case
   could be made for requiring nothing but `submission_id`, on the grounds that any application is
   better than none. The four chosen are the ones the live form itself guarantees, which is the
   defensible line, but it is a line.
2. **The name+postcode applicant fallback.** It merges two same-named people at one address. Stated,
   not hidden.
3. **Everything in spec §9 that was left alone.** Ten mapping gaps, ~30 unstored columns, five
   mismatched option sets. Doing any of it needed a decision I did not have.

---

### 2.7 Revision 1.0 — the solution actually deployed to a live DEV environment

**This is the revision where every remaining "written from convention, never validated" item in §7.1
was finally tested by execution — and where the ones that were wrong turned out to be wrong.** A
dedicated handover document records the process, the diagnostics and the outstanding work:
**`docs/development/revitalise-grant-automation-dev-deployment-handover.md`**. This section is the
summary against the revision history; read the handover for the corrected deployment procedure.

**Outcome: DEV deployment COMPLETE.** The solution imports cleanly and idempotently, and all four
flows open and save in the Power Automate designer. Verified by live Web API query, not by exit code:
three environment variable definitions, the model-driven app, its app-aware sitemap, and all four
cloud flows exist in DEV.

**It took fifteen `pac solution import` attempts.** Six distinct root causes in solution-component
XML, then three more in flow JSON that only surfaced *after* a successful import, when a human tried
to open the flows. Full table in the handover §3; the headline is that **`pac solution pack` passing,
640 Pester tests passing, and the XML/JSON/consistency gates passing did not detect any of the
nine** — every one was a plausible guess about a platform contract that only a live environment could
refute.

What this revision changed in the repository, beyond the source fixes themselves:

| Change | Why |
|---|---|
| **`scripts/verify-workflow-description-length.py`** (new), wired into `build.yml` as `workflow-description-length` | 62 flow `description` fields across all four flows exceeded Power Automate's hard 256-character limit (up to 6,696 chars). Neither pack nor import objects; the flow simply cannot be saved in the designer afterwards. **C-TECH-049** |
| **`Workflows/<FlowName>.notes.md`** ×4 (new) | The full text of all 62 condensed descriptions, keyed by JSON path. Nothing was deleted — the flow keeps the fact plus its FR/NFR/ADR citation, the notes file keeps the reasoning |
| **`C-TECH-049`, `C-TECH-050`, `C-TECH-051`** (new constraints) | Description limit; Web-API-first creation of the component types solution import cannot create; never fabricating an id Dataverse assigns |
| **`knowledge/technology/power-automate.md`** — new section on hand-authoring flow JSON | The 256-char limit, `Response` + concurrency needing `operationOptions: asynchronous`, stray `staticResult` blocks, and the get-ground-truth-instead-of-guessing pattern |
| **`knowledge/technology/dataverse.md`** — new section on solution import | What cannot be created from scratch, which component types get platform-assigned ids and how each fails, and the `RootComponent` type-10371 finding |
| **`verify-solution-root-components.py`** and **`verify-field-security-coverage.py`** corrected | Both were matching on fabricated element names/casing that the real platform doesn't use — they passed against wrong source and would have kept passing |
| **`provisioning/common/provisioning-common.ps1`** — `Get-CertificateStoreCertificates` | `Get-ChildItem -Path 'Cert:\...'` is Windows-only. Every provisioning script would have failed on the Linux CI runner. Found only by running provisioning for real, on a Mac |
| **`environmentvariabledefinitions/README.md`** (new) | Those three files can carry **no XML declaration and no comment** — a different, less tolerant import handler than every other component type in this solution. The explanation had nowhere else to live |

**The §7.1 risk table was right about what to distrust and wrong about the remedy.** Items 1, 3a and
4–8 all correctly flagged unvalidated conventions. But the table's proposed remedy throughout was
"build it in the DEV UI and re-unpack" — which is right, and which nobody could do until DEV existed.
The faster version, discovered in this revision and now recorded in both knowledge files: **create a
minimal instance via the Web API, export, unpack, and read how the platform serialises it.** That
settled four of the six import blockers in minutes each, against hours of import-error iteration.

**Still unproven after this revision, and it matters:** no flow has ever *run*. Import and
designer-save are proven; execution is not. `pac solution check` has still never been run, and no
managed-solution import has been attempted — TST/ACC and PRD take managed, a different code path.
Handover §5 has the full list.

---

## 3. Data Model Changes

Reference: TAD §3. Phase 1 builds **4 of the 10 tables** in the TAD data model. `rev_review`,
`rev_grant`, `rev_provider`, `rev_bankaccount`, `rev_payment` and `rev_anonymisedstatistic` belong
to Automations #3, #5, #6, #7 and #8 and are deferred (§7).

### 3.1 What this pass added to the recovered schema

> **Superseded in part by §2.3.** The statement below ("the four `Entity.xml` files were not
> modified") was true of the first pass. **Revision 0.2 modified two of them** —
> `rev_applicant` and `rev_application` — against the raw export. `rev_setting` and `rev_errorlog`
> are still untouched. §2.3 is the authority on the schema as it now stands.

The four `Entity.xml` files were recovered intact and were **not modified** *in the first pass*.
What was missing was everything they *pointed at*.

**Ten global option sets** (sixteen after revision 0.2 — see §2.3.1 and §2.3.3 — **fifteen after
revision 0.3 deleted `rev_feelingscale`**, §2.4.1, and **sixteen again after revision 0.8 added
`rev_agreementresponse`**, which is the current figure; corrected in revision 0.9, D-017). Every `picklist` and `multiselectpicklist` attribute in the recovered
entities declares `<IsGlobal>1</IsGlobal>` and an `<OptionSetName>`, but no `OptionSets/` folder
existed. Without it the solution cannot pack, and — worse if it had somehow packed — every choice
column would have had no options. Option **values** were not free to invent: the recovered saved
queries already filter on `rev_status eq 3`, `eq 4`, `eq 5` and `ne 4`, which pins Borderline = 3,
Auto-reject = 4 and Under Review = 5. Reading those constraints back against the TAD §3.1 status
list (`Submitted · Auto-pass · Borderline · Auto-reject · Under Review · …`) gives an exact,
unambiguous 1–11 sequence. The other nine sets were built to the same convention.

**One parental relationship.** `rev_applicant_rev_application_applicantid` was declared in the
manifest with no definition. It is **Parental with cascade on all five behaviours**, and that is
load-bearing rather than a default: the retention design deletes one parent row and requires the
whole case to follow (FR-048), and an erasure request must reach the whole case from a single
applicant reference (FR-051). TAD §3.3 records the deliberate deviation from
`knowledge/technology/dataverse.md`, which would prescribe Restrict Delete for a table with a
regulatory retention period — applied literally that guidance would block the retention design
outright, because here the regulatory obligation is to *delete* at the end of the period, not to
preserve. The file repeats that reasoning at the point of use.

**Two alternate keys (recovered, and now load-bearing).**

| Key | Table | What it buys |
|---|---|---|
| `rev_application_sourcesubmissionid` on `rev_sourcesubmissionid` | `rev_application` | The intake idempotency guard. A replayed or retried webhook is caught by an indexed lookup before any write (TAD §5.1) |
| `rev_setting_name` on `rev_name` | `rev_setting` | Makes `seed-settings.ps1` a keyed upsert and lets the flows retrieve a setting by name rather than by GUID — the reason no flow holds a per-environment record ID |

### 3.2 Retention (C-DOM-003)

Retention is not a solution component — the recurring bulk-delete jobs are per-environment
configuration (ADR-004) — so it is implemented in
`provisioning/dataverse/ensure-bulk-delete-jobs.ps1`, wired into `post_deploy` for both
environments.

| Record class | Rule | Implemented as |
|---|---|---|
| Rejected applications | 12 months from `rev_decisiondate` | Recurring bulk-delete job, monthly |
| Withdrawn / incomplete applications | 6 months from the parent applicant's `rev_lastcontactdate` | Recurring bulk-delete job, monthly, joined to `rev_applicant` |
| **Orphaned applicants** | Applicant rows with no remaining child application | Recurring bulk-delete job, monthly — **the derived remediation for TAD §3.4 gap 1 / risk A-R10**, which no source document covers and which would otherwise leave name, address and date of birth in place indefinitely |
| Error log | 90 days from `rev_occurredon` | Recurring bulk-delete job, monthly |
| Settings | Indefinite; changes audited | No job. Auditing enabled on the table |
| Paid grants (6 years from final payment) | Not implementable in this release | Needs `rev_grant.rev_finalpaymentdate`, which arrives with Automation #3/#8. **No Phase 1 application can reach `Grant Paid`**, so no record class is left unprotected — but this is the one retention rule that is designed and not yet built |

`rev_lastcontactdate` is refreshed on every repeat application (intake flow,
`Refresh_existing_applicant`). Without that, a live applicant's six-month clock would run from
their first contact and delete an active case early.

### 3.3 Migration

None. Phase 1 migrates no data (SDD scope). TST/ACC and DEV hold synthetic data only, enforced as
an explicit `pre_deploy` guard rather than a masking transform, because there is nothing to mask
(C-TECH-007).

---

## 4. Automation / Workflow Changes

Reference: TAD §5. Applied `skills/how-to-design-a-workflow.md`. Four of the TAD's thirteen flows
are built.

Every flow: runs as the service account; validates its input before processing; wraps its work in a
top-level `Scope` with a parallel `runAfter: [Failed, TimedOut]` branch; calls
`REV | Ops | Failure Alert` from that branch; retries transient failures with exponential
back-off (4 attempts, `PT10S` base, `PT1M` cap); and writes no personal data to any log.

### 4.1 `REV | Intake | WordPress to Dataverse`

**Trigger:** HTTP request, POST, **concurrency capped at 1**.

The concurrency cap is a correctness decision, not a throttle. The applicant match-or-create step
is read-then-write, so two simultaneous submissions from the same person could otherwise create two
applicant rows — and one person having two applicant rows breaks both the repeat-applicant model
and the erasure path. At ~200 applications a year, serialising costs nothing.

**Order of operations, and why it is that order:**

1. **Reject an unauthorised caller** — before anything else, and before any Dataverse write
   (NFR-008, C-TECH-006). Terminates `Cancelled`, not `Failed`, so a port scanner hitting the
   endpoint does not become a Teams notification to Emily.
2. **Reject an incomplete payload** — `submission_id`, `full_name`, `email`, `postcode`,
   `date_of_birth`. Logs a `Warning` (the platform is healthy; the caller is not) and returns 400.
   **The eleven scored answers are deliberately *not* required here**: a submission missing a
   scored answer is a valid application whose *scoring* is withheld and routed to a human
   (FR-022). Rejecting it at the boundary would lose the application entirely, which is the exact
   outcome FR-010 exists to prevent. **Revision 0.2:** the required list is now `submission_id`,
   `first_name`, `last_name`, `email`, `postcode`, `date_of_birth` — `full_name` is gone (§2.3.4).
   **Revision 0.7:** and now `email` and `date_of_birth` are gone from the *required* list too — the
   live form collects neither reliably, so the guard as written rejected every real application. The
   list is `submission_id`, `first_name`, `last_name`, `postcode`; `age_range` is accepted in place of
   a date of birth and `group_linkage` is no longer accepted at all (§2.6.2). **The reasoning in the
   paragraph above is the reasoning that drove revision 0.7** — it was applied to the eleven scored
   answers and should have been applied to the whole required list.
3. **Replay guard** — indexed lookup on the `rev_sourcesubmissionid` alternate key. A replay
   returns the reference it created the first time and terminates `Succeeded`.
4. **Derive the age band** (FR-027) — exact completed years, not a tick-division approximation,
   because band boundaries decide which reporting group a person lands in. `AgeBandMap` is read
   from configuration; the map must stay in ascending `maxAge` order and that requirement is
   stated at both ends. No usable date of birth → option 9 *Not known*. The flow never guesses.
5. **Derive the region** (FR-027) — Logic Apps has no regular expressions, so the outward code's
   two-letter area is tried first and the one-letter area second. That ordering is what makes
   `BT1` resolve to Northern Ireland rather than to the West Midlands on `B`. Unrecognised
   postcode → option 13 *Not known*.
6. **Match or create the applicant** on email **and** name, so one person is one applicant row.
   **Revision 0.2:** the match is now on `rev_email` + `rev_firstname` + `rev_lastname`, not
   `rev_fullname`, which is calculated. The refresh branch deliberately does **not** overwrite
   `rev_privacynoticeacceptedon` — that column is evidence of when the applicant was first told how
   their data would be used — and deliberately does not rewrite the three columns it matched on.
7. **Create the application** (FR-007, FR-008). `rev_name` is **not set**: the `REV-{yyyy}-{nnn}`
   format FR-008 requires is enforced by the autonumber column, so it cannot drift. Neither
   `rev_costs` nor `rev_fullname` is set either — both are calculated columns (§2.3.1, §2.3.3).
8. **Notify the process owner** (FR-009) — the one notification in this solution that carries
   personal data, because FR-009 requires the applicant name. ADR-015 is the control: 1:1 chat to
   one named recipient, never a channel.
9. **Respond 201.** Responds success even if the Teams post failed — the record exists, so the
   applicant's submission succeeded, and returning an error would make Alex's site retry and tell
   the applicant something went wrong when nothing did. The failed notification is caught by the
   scope's failure branch and logged instead.

**Failure path** returns **500 with `retry: true`** and no diagnostic detail. Retrying is safe
precisely because of step 3.

### 4.2 `REV | Scoring | Calculate & Flag`

**Trigger:** Dataverse row **created** on `rev_application`, scope Organization, run as flow owner.
Created-only, not modified: a modified trigger would re-score on every edit and fight the override
guard. Run as flow owner because if Emily creates an application by hand, scoring must still be
able to write an error row on failure, and she holds no create privilege on `rev_errorlog`.

**FR-016 is enforced structurally, not by intention.** The Dataverse trigger delivers the whole
row, so the honest guarantee is that *no expression anywhere in the definition references*
`rev_narrativeraw`, `rev_otherconditionraw`, `rev_conditionprofile` or
`rev_supportrecipientconditionprofile`. That is a grep-able property, so it is now a **build gate**
(`no-special-category-data-in-scoring`) rather than a promise in a document. Special-category data
cannot influence an automated outcome, and a future edit that broke that would fail CI.

**Order, and why:**

1. **Override guard first** (FR-018). A named human's decision outranks the automation, so the flow
   exits before it reads configuration or computes anything — there is no path from here to a write.
2. **Read configuration** — eight `rev_setting` rows retrieved by alternate key at run time. Not
   one threshold is a literal. This is what FR-017 and NFR-019 buy: the board changes a criterion
   by editing a row in the app, and auditing on `rev_setting` evidences the change against the
   decisions it affected.
3. **Completeness check** (FR-022, NFR-018) → status 5 *Under Review*, **`rev_circumstancescore`
   deliberately left null**, breakdown naming exactly which answers were absent, and a Teams
   message. A partial score displayed next to a status looks like a judgement and is not one. The
   message is pushed rather than only filed in a view, because NFR-018 requires 100% of these to
   reach a human and a queue nobody opens does not achieve that.
   **WIDENED IN REVISION 0.8 from "absent" to "absent or unusable", on all eleven scored answers.**
   The gate tested only for emptiness, so an answer that was *present* but had no configured point
   value passed straight through to a numeric cast that threw — the mechanism by which D-014 lost an
   application. Both configuration maps are now parsed **before** the gate so it can ask "is this a
   key of the map?", and both are checked: the ten wellbeing answers against `LikertPointMap` and
   the life-satisfaction answer against `FeelingScaleInversion`. The check is deliberately
   *membership of the map*, not a hardcoded range, so it stays correct when the board changes the
   configuration (FR-017). The scoring chain is asserted to remain strictly downstream of the gate.
4. **Score** (FR-011, FR-013) — **10** wellbeing answers through `LikertPointMap` (**corrected in
   revision 0.2 from 11** — see §2.3.2). **REVISION 0.8: the ten answers use TWO response scales.**
   The seven SWEMWBS items keep the frequency labels on `rev_likertresponse`; the three "last year"
   questions moved to the new `rev_agreementresponse` (agree/disagree), because
   `docs/Import/Book(Sheet1).csv` shows that across 25 real applications the two label sets **share
   exactly one value — "Not sure" — and are otherwise disjoint** (no frequency label ever appears
   in columns 103–105, no agreement label ever in 96–102). *Wording corrected in revision 0.9,
   D-016: this sentence used to say "disjoint" flat, which read as an argument against the very
   design it introduces.* **One `LikertPointMap` still serves both, and the shared value is why** —
   the lookup is keyed by numeric option value and never sees which option set an answer came from,
   so a **shared** value 6 must resolve to one shared point value. Both scales gained that sixth
   option, **"Not sure", worth 0.5 points**. The accumulator is therefore a **`float`** and the cast is
   **`float()`**, not `int()`; that single `int()` was what threw on a valid answer. The loop's
   **concurrency is pinned to 1**: Power Automate parallelises `Apply to each` by default, and with parallel
   repetitions two increments of a shared variable can read the same value and one is lost, producing
   a score quietly too low. Ten iterations gain nothing from parallelism, and a wrong score is a wrong
   decision about a person.
5. **Invert the life-satisfaction answer** (FR-012) through `FeelingScaleInversion` — a table
   lookup, so no arithmetic in the flow encodes the direction of the scale. The answer is a whole
   number **0–10** and the map has eleven entries expressing `10 − answer`, so **(10 × 5) + 10 = 60**
   (revision 0.3, §2.4.1). That range is a consequence of configuration rather than a constant.
   **The 55-versus-60 question is closed and the board's thresholds are unblocked.**
6. **Round the total** (**NEW in revision 0.8; the mechanism CORRECTED in revision 0.9**) —
   `Round_the_circumstance_score`. With "Not sure" worth 0.5, an **odd** number of "Not sure" answers
   gives an X.5 total, and `rev_circumstancescore` is an `int` column. Rounded **half up**, once, at
   the end — never per answer, which would lose up to five points across ten answers. **The rule is
   a judgement call, not a derivation** (the ground-truth data contains no fractional total), flagged
   in the revision 0.8 banner and the review checklist for the reviewer to confirm or override.
   `formatNumber(…,'F0')` rather than `round()`, because the Logic Apps expression language has no
   `round()`, `ceiling()` or `floor()` to call.
   **⚠️ REVISION 0.9 — THE RULE WAS APPROVED BUT THE CODE DID NOT IMPLEMENT IT (D-015).** Revision
   0.8 shipped `int(formatNumber(<total>, 'F0'))` on the stated grounds that `'F0'` rounds half away
   from zero. **It does not, and nobody had executed it.** .NET formats a double at an exact midpoint
   by rounding **half to even**, so it agreed with half-up only when the whole part was odd —
   `37.5 → 38` (right, and the example the description used), but `20.5 → 20` and `30.5 → 30`
   (wrong). The expression is now
   `@int(formatNumber(add(outputs('Calculate_circumstance_score'), 0.25), 'F0'))`: the `+0.25` moves
   the value **off the midpoint** before the formatter sees it, so `X.0 → X.25 → X` and
   `X.5 → X.75 → X+1` on any rounding mode. It is sound because `.0` and `.5` are the only fractional
   parts that can arise, which the suite asserts on the map itself. See the revision 0.9 banner for
   the executed evidence.
7. **Income flag** (FR-015) — deliberately separate from the score, via `IncomeBandUpperBoundMap`
   (see §5.1). "Prefer not to say" produces flag 3 *Not stated — cannot assess*, never a guess.
8. **Status** (FR-014) — **knockout is evaluated first**, so a misconfigured band (lower set below
   the knockout) can never let a knocked-out application through as Borderline.
   **Evaluated against the ROUNDED score since revision 0.8, and that is load-bearing:** the status
   must come from the same number that is stored, or the record contradicts itself. With a
   borderline lower bound of 37, an exact 36.5 is not ≥ 37 and falls through to Auto-pass, while the
   **37** actually stored *is* in the band and is Borderline — a human review silently skipped on a
   record whose own score says it should have happened.
9. **One write, at the end** — so a mid-flight failure leaves the application unscored rather than
   half-scored. FR-020 is satisfied by writing status 4: the Active Applications view filters
   `rev_status ne 4`, so the application leaves the working list with no data moved or irreversibly
   hidden. The score written is the **rounded** one; the **exact unrounded total is recorded in the
   breakdown** alongside it, so rounding hides nothing.
10. **Borderline → Teams** (FR-019, NFR-018). Carries the reference, score and band — **not** the
    applicant's name, because unlike FR-009 no requirement here needs it.

The score breakdown records **the thresholds in force at the time of scoring**, so a later
threshold change cannot make a historic decision look wrong.

### 4.3 `REV | Scoring | Daily Summary`

**Trigger:** Recurrence, 07:00 UTC, **Monday–Friday**. Weekdays only because the summary exists to
prompt action and there is nobody to act at the weekend — a Saturday message trains the recipient
to ignore the channel. Monday's window therefore reaches back three days rather than one, so
nothing scored over the weekend falls through a reporting gap.

**Counts only, and that is enforced by the queries, not by the message.** Every list selects
`rev_applicationid` and nothing else, so the flow never holds a name, reference, score or narrative
to leak. A summary posted into a chat is the easiest place in the whole solution for personal data
to escape (TAD §5.3, NFR-012).

Four counts, and the split between them is deliberate: **scored** and **auto-rejected** are
windowed; **Borderline awaiting review** and **Under Review, no score** are *backlog* counts, not
windowed. FR-021 asks how many are "borderline awaiting review", which is a backlog question — a
Borderline application ignored for a fortnight must keep appearing until somebody looks at it. That
is what makes NFR-018 observable day after day rather than only on the day it happened. The fourth
count (status 5) is a **DERIVED addition** not named in FR-021: NFR-018 covers those cases too, and
an unscored application is the most easily forgotten state in the process.

Read-only, so safe to run twice. Failure is logged at `Warning`, not `Error`: a missed summary
loses a day's oversight but loses no data and blocks no application, and over-classifying it would
dull the channel a genuine intake failure depends on.

### 4.4 `REV | Ops | Failure Alert` (child flow)

Called from the `runAfter: [Failed, TimedOut]` path of the other three. Writes one `rev_errorlog`
row and posts one Teams alert. Five inputs, every one a value the caller already holds — no input
requires the caller to read a record.

Three details that matter:

- **The message is truncated at 2000 characters as defence in depth only.** The real control is
  that `rev_errorlog` has no column capable of holding personal data (NFR-012). Constraining the
  schema is stronger than instructing the developer.
- **A failure of the failure handler must not be silent.** If the Dataverse write or the Teams post
  fails, an Outlook email goes to `rev_ServiceMailbox` instead (TAD §4 fallback) — deliberately
  without the record reference, because at that point the flow cannot be sure the reference was
  safely bounded.
- **It always responds 200.** The parent has *already* failed; a failing error handler must not turn
  one failure into two. The response body reports whether the row was written, so a reviewer reading
  the parent's run history can tell the difference.

### 4.5 Documented deviations from `knowledge/technology/power-automate.md`

| Guidance | What was done | Why |
|---|---|---|
| Flow naming `[PREFIX] <Domain> - <Action> - <Trigger>` | `REV \| <Automation> \| <Action>` | TAD §1.3 adopts the source's naming convention unchanged. The TAD is the approved authority |
| "Error branch must log to `[prefix]_flowexceptionlog`" | Logs to `rev_errorlog` | Naming only. TAD §3.1 names the table |
| "Scheduled flows: store schedule configuration in a Dataverse configuration table, not hardcoded" | The daily summary's recurrence is a trigger property | **Not implementable.** A Recurrence trigger is evaluated by the platform *before* any action runs, so it cannot read a Dataverse row. Changing the time is a solution change, not a setting change |
| "Teams notifications use Adaptive Cards with a deep link into the app" | HTML message bodies | An Adaptive Card deep link needs the target environment's app URL, which is per-environment. Under C-TECH-047 that would have to come from a fourth environment variable. Deferred deliberately rather than hardcoded; recorded in §7 as a usability improvement, not a defect |

---

## 5. Configuration & Provisioning Changes

### 5.1 Configuration

| Key | Environment | Notes |
|---|---|---|
| `rev_ServiceMailbox` | per-env | Environment variable **definition** only, no default value. Outlook fallback recipient |
| `rev_ProcessOwnerUpn` | per-env | Recipient of all four notification types. Held here so a change of process owner is a deployment setting, not a solution change |
| `rev_IntakeAllowedClientId` | per-env | The WordPress caller's Entra client ID. **Plain, not secret-type**, because a client ID is a public identifier. Under the shared-secret intake alternative this becomes a Key Vault-backed *secret* environment variable — see §7 D-1 |
| `rev_SharedDataverse` / `rev_SharedTeams` / `rev_SharedOutlook` | per-env | Connection references. Bound to service-account connections once per environment; interactive OAuth so not scriptable |

**Eleven `rev_setting` rows** (ADR-010, NFR-019) — ten until revision 0.7 added `AgeRangeLabelMap`;
revisions 0.2 and 0.3 changed values only. *Count corrected in revision 0.9 (D-017); the shipped
`DeploymentSettings.Tests.ps1` asserts eleven and is the authority.* Values live in
`provisioning/deploymentSettings/{test,prd}-settings.json`:

| Row | Status | Note |
|---|---|---|
| `LikertPointMap` | **Fixed by FR-013** — **key added in revision 0.8** | "None of the time" / "Strongly Disagree" = 5 … "All of the time" / "Strongly Agree" = 1, plus **key `"6"` ("Not sure") = 0.5, added in revision 0.8** and derived from ground truth, not chosen. Real value in every environment, byte-identical across both. **Keys 1–5 and their direction are unchanged since revision 0.3** — revision 0.3 moved only the option *labels*, re-verified against all ten question texts (§2.4.3) — but the *row* did change in 0.8, and the earlier "value unchanged" note was stale (revision 0.9, D-017). **One map serves both wellbeing scales**, because the flow looks it up by numeric option value; `0.5` is the only non-integer in it, and `Round_the_circumstance_score`'s `+0.25` offset depends on that (§4.2, D-015) |
| `FeelingScaleInversion` | **Fixed by FR-012** — **value replaced in revision 0.3** | Now **eleven entries keyed `0`–`10`**, values `10`–`0`, expressing `10 − answer` for the 0–10 life-satisfaction question. Was a five-entry map over the deleted five-option picklist. Real value in every environment. §2.4.1 |
| `AgeBandMap`, `PostcodeRegionMap` | Reference data | Real values. `PostcodeRegionMap` covers all UK postcode areas across 12 regions |
| `IncomeBandUpperBoundMap` | Reference data — **DERIVED, added this pass** | Maps each `rev_incomeband` option to the top of that band so it can be compared with `IncomeCeiling`. Introduced so the band bounds are a *field mapping the process owner owns* (NFR-019) rather than numeric literals inside the scoring flow. Sentinel `-1` = not stated |
| `MaxCircumstanceScore` | ✅ **SETTLED IN REVISION 0.3 — back to 60** | Used only to render "n out of N", read from config so the breakdown cannot describe a maximum the scoring no longer has. Revision 0.2 set it to 55 to match a five-option life-satisfaction picklist; revision 0.3 made that question a 0–10 whole number, so **60 is both the charity's figure and what the flow produces**. §2.4.1 |
| `KnockoutThreshold` | ⚠️ **Awaiting SDD OQ-001 — but no longer blocked on the scale** | TST/ACC 20 (provisional, always set against 0–60). **PRD carries `{{PENDING_OQ_001}}`.** The board can now set this: the maximum is 60 |
| `BorderlineBandLower` / `Upper` | ⚠️ **Awaiting SDD OQ-002 — but no longer blocked on the scale** | TST/ACC 21–30 (provisional, always set against 0–60). **PRD carries `{{PENDING_OQ_002}}`** |
| `IncomeCeiling` | ⚠️ **Awaiting SDD OQ-003** | TST/ACC 25000 (provisional). **PRD carries `{{PENDING_OQ_003}}`** |

The pending tokens are the mechanism, not an oversight: `seed-settings.ps1` resolves every value
through `Assert-NoPlaceholder` in a **pre-flight pass before any write**, so a PRD seed aborts
rather than half-seeding production with unconfirmed board criteria.

### 5.2 Provisioning Scripts

Every TAD §12 item in Phase 1 scope. All idempotent, check-before-create, one
`CREATED | EXISTS | FAILED — <resource>` line per resource, non-zero exit on any `FAILED`
(C-TECH-042). All eleven scripts referenced by the pipeline exist — verified mechanically.

| Script | Purpose | Pipeline Block | Idempotency Check |
|---|---|---|---|
| `entra/ensure-groups.ps1` | 3 Entra groups per env: environment gate + `rev-Admins-*` + `rev-ServiceAccounts-*`. **`rev-Finance-*` / `rev-Trustees-*` deliberately not created** — no Phase 1 table is reachable by either persona | `tenant_prerequisites` | Group lookup by display name |
| `entra/ensure-app-registration.ps1` | 3 registrations: `-deploy`, `-provisioning`, conditional `rev-wordpress-intake` | `tenant_prerequisites` (×2 settings files) | App lookup by display name; second run reports `EXISTS` |
| `entra/grant-admin-consent.ps1` | Admin consent for the declared least-privilege permissions. Tenant-wide, so once only | `tenant_prerequisites` | Existing `appRoleAssignments` / `oauth2PermissionGrants` |
| `entra/verify-entra.ps1` | Read-only assertion | smoke test | `PASS`/`FAIL` per check |
| `dataverse/bind-roles-to-groups.ps1` | Group teams `REV Admins`, `REV Service Accounts` + bind `REV Admin`, `REV Service Automation`. **Roles looked up BY NAME** — GUIDs differ per environment | `post_deploy` both envs | Team lookup by name; existing role association |
| **`dataverse/ensure-column-security-profile-members.ps1`** — NEW | Adds both group teams to `REV_TrusteeRestricted`, so the process owner and the service account can read the 17 Tier 4 columns and nobody else can | `post_deploy` both envs | Reads current `teamprofiles` membership before associating |
| **`dataverse/ensure-auditing.ps1`** — NEW | Organisation auditing on, **retention 2192 days (6 years)**, plus table auditing on all four tables via the metadata endpoint | `post_deploy` both envs | Read-then-PATCH; matching values report `EXISTS` |
| **`dataverse/ensure-bulk-delete-jobs.ps1`** — NEW | The four recurring retention jobs in §3.2 | `post_deploy` both envs | `bulkdeleteoperations` lookup by job name, excluding completed |
| **`dataverse/seed-settings.ps1`** — NEW | Upserts the ten `rev_setting` rows by alternate key. Two passes: placeholder pre-flight, then write | `post_deploy` both envs | Keyed `GET` first; 404 → `CREATED`, else `EXISTS`. `rev_effectivefrom` on create only |
| `dataverse/share-apps.ps1` | Associates `rev_grantadministration` with the two roles | `post_deploy` both envs | Existing `appmoduleroles` association |
| `dataverse/verify-role-bindings.ps1` | Read-only: teams, Entra binding, role bindings, **and the absence of direct user-to-role assignments** (C-TECH-040) | smoke test | `PASS`/`FAIL` per check |
| **`deploymentSettings/test-settings.json`, `prd-settings.json`** — NEW | Per-environment provisioning settings. Identifiers only, never secrets | read by every script | `Get-Setting` fails fast on `{{...}}` |

**Manual, unscriptable, and gated:** service account + Conditional Access exception (Wanstor, WBS
0.3, **blocking**); the three Power Platform environments; UK residency verification with written
evidence; the DLP connector policy; licence entitlements; and binding the three connection
references (interactive OAuth consent).

### 5.3 Defects found and fixed in the recovered config files

| File | Defect | Fix |
|---|---|---|
| `build.yml` | `source-validate` globbed `Workflows/*.json` — **non-recursive**, so it would have validated zero flow definitions and reported success | Recursive glob, plus an assertion that exactly 4 flow definitions are found |
| `build.yml` | No check that the `Solution.xml` manifest agreed with the source — the exact failure that made this task's recovery necessary | New `root-components-resolve` step running `scripts/verify-solution-root-components.py`, checking **both** directions |
| `build.yml` | FR-016 (special-category data excluded from scoring) was a documentary claim with no verification | New `no-special-category-data-in-scoring` grep gate |
| `pipeline.yml` | A `tenant_prerequisites` operation described creating `rev-wordpress-intake` but its `script:` line called `ensure-app-registration.ps1 -Env prd`, i.e. the generic run — the description and the command did not match | Rewritten as two accurate operations: all three registrations come from one `entra.appRegistrations` block, run once per settings file, with the conditional nature of `rev-wordpress-intake` stated |
| `pipeline.yml` | `seed-settings` description listed six of the ten setting rows | Corrected to all ten, with the fixed-versus-pending split stated |

Two items in the recovered configs were checked against the confirmed facts and found **already
correct** — they were not changed: exactly two deploy targets (`tst_acc`, `prd`) with `APPROVE PRD`
as the single remaining deployment gate per TAD §9.1/ADR-006; and a `tenant_prerequisites`
`permission_findings` block that accurately records the Power Platform / SharePoint Administrator
confirmation, the group-creation nuance (no Groups Administrator role, but tenant self-service
group creation is enabled), and the Conditional Access exception as `BLOCKED_PENDING_WANSTOR`.

---

### 5.4 Revision 0.4 — ALM tooling, CI/CD and credentials

No solution component changed. Files touched:

| File | Change |
|---|---|
| `.github/workflows/ci.yml` | **Rewritten.** ⚠ Repo-wide shared file. 555 lines → 5 jobs, ~460 lines including a substantially longer operator-setup header |
| `.github/actions/setup-powerplatform/action.yml` | **New.** Composite action: pinned pac + yq, OIDC auth, `id-token` pre-flight |
| `scripts/ci/run-config-steps.sh` | **New.** Generic runner for the four config-declared step lists; handles `manual` steps |
| `scripts/ci/promote-via-pipelines.sh` | **New.** Drives, or hands over, the Pipelines promotion |
| `scripts/ci/verify-promoted-version.sh` | **New.** Refuses to run `post_deploy` against an unpromoted environment |
| `config/revitalise-grant-automation-pipeline.yml` | New `alm` block; `deploy_command` removed from both environments; `promote_mode` + stage identifiers added; rollback routes rewritten; **4 new tenant prerequisites** |
| `config/revitalise-grant-automation-build.yml` | `auth` step → `--githubFederated`; `CLIENT_SECRET` removed from `required_env_vars`; ADR-007 header corrected |
| `config/pipeline.yml.example` | **Rewritten** to the three-environment + Pipelines shape — see §5.4.7 for why this was not optional |
| `provisioning/deploymentSettings/test-settings.json`, `prd-settings.json` | Deploy registration split per environment; federated-credential subjects corrected |
| `provisioning/deploymentSettings/dev-settings.example.json` | Same correction, for future features |
| `docs/architecture/…-architecture.md` | ADR-007 → `Adopted`; **ADR-021 added**; §9.2 rewritten; §6.7 + §6 table corrected; §12 + gate record updated; rev 2 header |

#### 5.4.1 The topology fix

The workflow's three deploy jobs assumed four environments and GitHub Environments named `test`, `acc`
and `prd`. The confirmed topology (ADR-006, TAD §9.1) is three environments with **two** deploy targets,
and `config/revitalise-grant-automation-pipeline.yml` had already been written to that shape with keys
`tst_acc` and `prd`. **The shared workflow and the feature config disagreed**, and the workflow would
have failed looking for `environments.test.deploy_command`. Now: `validate` → `build` → `stage-dev` →
`promote-tst-acc` → `promote-prd`, GitHub Environments `dev` / `tst_acc` / `prd`, no `APPROVE ACC`
anywhere, `APPROVE PRD` enforced by required reviewers on `prd`.

The three near-identical deploy jobs are also gone. They were ~120 lines each of copy-paste and had
already drifted; the repeated setup is one composite action and the repeated yq loops are one script.

#### 5.4.2 Where GitHub Actions ends and Power Platform Pipelines begins

**This is the substance of ADR-007 and the thing to read if you read nothing else.**

> **GitHub Actions owns:** `validate` → `build` → `stage-dev`.
> **The hand-off point:** `pac solution import` of the **UNMANAGED** solution into **DEV**, with
> `--publish-changes`.
> **Power Platform Pipelines owns:** DEV → TST/ACC → PRD.

**Why the hand-off is "import unmanaged into DEV" and not "hand Pipelines a zip":** Pipelines cannot be
given a pre-built artefact. It exports the solution from the development environment at the moment a
deployment is requested, and then forbids modification —
"Solutions are exported as soon as a deployment request is submitted… the same solution artifact will be
deployed… The system also prevents any tampering or modification to the exported solution artifact. This
ensures customization can't bypass QA environments or your approval processes."
([alm/pipelines](https://learn.microsoft.com/en-us/power-platform/alm/pipelines)). So the only route from
this repository into a Pipelines deployment is to make DEV's unmanaged solution match the repository.

`--publish-changes` is load-bearing, not cosmetic: "Do pipelines publish unmanaged customizations before
exporting the solution? Not currently." Unpublished changes would be **silently missing** from the
exported artefact — a failure that would look like "the flow I fixed didn't deploy".

**Four consequences that change existing contracts:**

1. **The build artefact is no longer the deployed artefact.** `build/artifacts/…/RevitaliseGrantAutomation-managed.zip`
   now proves the source packs cleanly and serves as the audit record. The deployed bits are the ones
   Pipelines exports. The **unmanaged** zip *is* deployed — into DEV only.
2. **`pac-import-tstacc.json` and `pac-import-prd.json` are no longer consumed.** Pipelines collects
   connection references and environment variables in its own deployment pane and does not accept a
   settings file ("can I use a custom DeploymentSettings.json file? Not currently within the maker
   experience" — [delegated-deployments-setup](https://learn.microsoft.com/en-us/power-platform/alm/delegated-deployments-setup)).
   Both files are **retained deliberately** as the code-reviewed record of the values an operator types
   into that pane. C-TECH-047 stays satisfied, but its enforcement moves from a tool to a human reading a
   file — stated plainly because that is a real weakening of one control even as others strengthen.
3. **Import behaviour is fixed** at "Upgrade without Overwrite customizations". `--force-overwrite` and
   `--activate-plugins` no longer apply beyond DEV.
4. **DEV is now derived from git.** The staging import overwrites unmanaged customisations in DEV. That is
   the TAD §9.2 posture, but it means **a maker who edits in the maker portal without committing loses
   that work on the next CI run.** Nobody has been told this yet; it belongs in the ALM runbook.

#### 5.4.3 New tenant-level prerequisites — recorded, not assumed

`pac admin list` on 2026-08-10 showed a single "Default" Dataverse environment, so DEV, TST/ACC and PRD
were already outstanding. Adopting Pipelines **adds four items**, all behind `APPROVE TENANT` (C-TECH-041)
and all in TAD §12 and the pipeline config:

| New prerequisite | Why, and the catch |
|---|---|
| **Custom pipelines host environment** with the *Power Platform Pipelines* application installed | Must be a **custom** host, not the platform host that auto-provisions on first visit: platform-host pipelines are *personal* pipelines and "can't be extended", can't be shared, and cap at three environments — which rules out delegated deployments and approvals. A dedicated production environment, UK region, not doubling as DEV (unsupported). ⚠ Deleting it deletes all pipelines and run history |
| **Pipeline + two stages** configured in the host | Environment records typed Development (DEV) / Target (TST/ACC, PRD), each validating to Success; stages *Deploy to TST/ACC* then *Deploy to PRD* chained by Previous Deployment Stage. **Two stages, not three** — ADR-006 again. Also: **enable the redeploy-previous-versions setting**, or rollback by redeployment does not exist |
| **Managed Environment status on TST/ACC and PRD** | ⚠ **A LICENCE COST the pac-CLI route did not carry.** "All other environments used in pipelines must be enabled as managed environments. Licenses granting premium use rights are required for all managed environments." The host and DEV are exempt. From **February 2026** Microsoft enables this on pipeline targets automatically — so it happens whether or not it is budgeted for. Confirm entitlements with Revitalise alongside the A-R18 capacity check |
| **Pipelines access assignment** | `Deployment Pipeline Administrator` in the host; the pipeline record shared with whoever runs it. ⚠ Whether a **service principal** may *request* a promotion is undocumented — see §5.4.5 |

#### 5.4.4 One deploy identity per environment — the reviewer's explicit decision

The old design used **one** `APP_ID` + `CLIENT_SECRET` for every deploy target. Resolving C-TECH-044 to a
federated credential created the chance to scope per environment, and the reviewer asked for that choice to
be visible rather than defaulted. Implemented as **three app registrations**:

| Registration | Federated credential subject | Dataverse application user in |
|---|---|---|
| `rev-grantautomation-deploy-dev` | `repo:<org>/<repo>:environment:dev` | DEV only |
| `rev-grantautomation-deploy-tstacc` | `repo:<org>/<repo>:environment:tst_acc` | TST/ACC only |
| `rev-grantautomation-deploy-prd` | `repo:<org>/<repo>:environment:prd` | PRD only |

**Why separate registrations and not several credentials on one.** Scoping several federated credentials
onto a single app registration gates only **token issuance** — which workflow context may obtain a token.
It does **not** scope **authority**: every one of those subjects resolves to the same service principal,
which is an application user in all three environments, so a token minted by the `tst_acc` job could still
import into PRD. The boundary would be convention, which is exactly what the reviewer asked to avoid.
Separate registrations move the boundary to *"this identity does not exist in PRD at all"* — C-TECH-043's
actual ask. Enforced in the workflow by making `APP_ID` an **environment-scoped** GitHub secret: a job can
only read the secrets of the environment it declares, so no job can even name another target's identity.

**Cost, stated honestly:** three registrations instead of one; the `entra.appRegistrations` block in
`test-settings.json` and `prd-settings.json` is **no longer identical**, which retires the neat "run once
per settings file, second run proves idempotency" property — each run now creates a different deploy
registration and reports `EXISTS` for the shared ones, so **both runs' output must actually be read**. Both
runs remain idempotent (C-TECH-042). No extra consent surface: all three request only Dataverse
`user_impersonation`. `-dev` has no settings file in Phase 1 (there is no `dev-settings.json`) so it is
created by hand with the DEV environment — recorded so it is not missed.

**A subject-format trap that was silently broken before this revision.** Both settings files declared
`subject: repo:{{GITHUB_ORG}}/{{GITHUB_REPO}}:ref:refs/heads/main`. GitHub's OIDC `sub` claim is
`repo:ORG/REPO:environment:NAME` for any job that **references an environment**, and only
`repo:ORG/REPO:ref:refs/heads/BRANCH` for one that does not
([GitHub OIDC reference](https://docs.github.com/en/actions/reference/security/oidc)). Entra matches
subjects as **exact strings**, no wildcards. This workflow triggers on `feature/**`, so the declared
`main` subject would never have matched **any** job — and a branch-based subject would need one credential
per branch name. Every authenticating job therefore now declares an `environment:`, which is also why the
`build` job runs under `dev`: the `dev` GitHub Environment exists to pin the OIDC subject, and **must have
no required reviewers** or every build blocks.

#### 5.4.5 What was verified about automating Pipelines, and what was not

**Verified — HIGH confidence.** `pac pipeline deploy --solutionName --stageId --currentVersion --newVersion
[--environment] [--wait]` is a documented, supported command: "Start pipeline deployment"
([CLI reference](https://learn.microsoft.com/en-us/power-platform/developer/cli/reference/pipeline)),
cross-checked against the locally installed **pac 2.4.1**, whose own help lists exactly those four required
parameters. `pac pipeline list [--pipeline]` returns pipelines and their stages, which is where a stage
GUID comes from. So **the earlier claim in ADR-007 that Pipelines leaves the pipeline-agent nothing to
drive was simply wrong**, and ADR-007 now says so.

**Not verified — and therefore not assumed.**
1. **Whether a service principal may *request* a promotion.** Every Microsoft example has a *maker*
   requesting from within the development environment. `run-pipeline`'s requester prerequisites are "access
   to run a pipeline" plus "privileges to import solutions to the target environments". Service principals
   appear in the docs only as the **delegated** identity that *performs* the import after a maker requests
   it, and as the identity that calls `UpdateApprovalStatus`. A CI service principal granted
   `Deployment Pipeline Administrator` in the host plausibly qualifies — but that is inference.
2. **The semantics of `--currentVersion` / `--newVersion`.** The reference gives only "Current solution
   version" / "New solution version". Whether *current* means DEV's version or the target's, and whether
   the two may be equal on a first release, is stated nowhere.

**Consequence.** `promote_mode` is **`manual`** for both environments. CI stages DEV and stops; a human
promotes in the Pipelines UI; **the GitHub Environment approval gate is the wait** — no extra machinery,
because the job pauses for reviewers anyway. On approval the job verifies the expected version is actually
present in the target (`verify-promoted-version.sh`) before any `post_deploy` script runs, so approving
before promoting fails loudly instead of provisioning an empty environment. The `cli` path is fully
implemented, its error paths exercised, and it carries a pre-flight `pac pipeline list` that turns the
unverified service-principal question into an explicit, actionable failure naming what to grant. Flipping
one config key switches it on. **Guessing either unknown in a production promotion path is worse than one
manual click**, which is why it was not guessed.

#### 5.4.6 A latent bug in the shared workflow, found and fixed

`config/revitalise-grant-automation-pipeline.yml` deliberately declares steps that cannot be automated —
binding connection references needs interactive OAuth consent, and several smoke tests belong to the
test-agent or the process owner. They are written `script: manual` and `command: manual step — …`.

The previous `ci.yml` passed those strings straight to `bash -euo pipefail -c "$SCRIPT"`. Every TST/ACC and
PRD deployment would have died on `manual: command not found`. It had never surfaced because no environment
exists yet to deploy to. `run-config-steps.sh` now **records** a manual step: a `::warning::`, a checklist
line in the job summary, and no job failure — never silently skipped, and carried into the Deployment
Summary (C-TECH-032).

**A second gap in the same area:** the old workflow **never ran `pre_deploy` at all**, though both
environments declare it. For TST/ACC that block is the **C-TECH-007 guard** — "confirm this environment
holds synthetic or anonymised data only". It was declared and unenforced. Both promote jobs now run it.

#### 5.4.7 Why `config/pipeline.yml.example` was rewritten too

Judgement call, and it went the way it did for a correctness reason rather than a stylistic one:
`.github/workflows/ci.yml` is **shared across every feature**, and it no longer reads `deploy_command` —
it requires `alm.stage_dev_command` and `promote_mode`. A future feature whose config was generated from
the old template would fail with "declares no `alm.stage_dev_command`". Leaving the template alone would
have left a trap for the next feature. It now carries both project-wide decisions (three environments;
Power Platform Pipelines) with the reasoning inline, and says that a future feature needing a separate Acc
environment is a **new ADR, not a silent edit**. `dev-settings.example.json` was corrected for the same
reason — its `ref:refs/heads/main` subject would have propagated the broken pattern from §5.4.4.

### 5.5 Revision 0.6 — the intake endpoint's primary authentication control (D-001)

Files added or changed. The scoring engine, all four tables, both roles, every privilege and the
field security profile are untouched by this revision.

| File | Change |
|---|---|
| `provisioning/entra/ensure-intake-client.ps1` | **NEW.** Ensures the intake caller's app registration and service principal, asserts the declared Microsoft Flow Service permission is actually present on a pre-existing registration, reports credential posture by count only, and prints the two identifiers the trigger setting and the environment variable need. Idempotent, three-state reporting, `-Env` contract |
| `provisioning/entra/verify-intake-endpoint-auth.ps1` | **NEW.** C-TECH-006's `Verify By`, executable: unauthenticated POST → 401/403; rejection happened **before** the definition ran; invalid bearer token also rejected. Read-only in effect; the header explains why every outcome writes nothing. Reads the endpoint URL from a CI secret and never prints the SAS query string |
| `provisioning/deploymentSettings/test-settings.json`, `prd-settings.json` | `rev-wordpress-intake` promoted from conditional stub to the provisioned default, now declaring one API permission; new top-level `intake` block carrying the mode, audience, client-credentials scope, required claims, accepted rejection codes, the endpoint-URL variable name and **the named owner** |
| `src/solutions/…/Workflows/REVIntakeWordPressToDataverse-….json` | Trigger description rewritten to specify the required setting exactly, cite the Microsoft documentation it was verified against, record that the header is deliberately not surfaced into outputs, and state that ADR-011 is still open. The `rev_IntakeAllowedClientId` parameter description now distinguishes the application ID from the service principal object ID. The caller-check action description reframed as the second gate. **No executable change to the definition** |
| `config/revitalise-grant-automation-pipeline.yml` | Two `tenant_prerequisites` operations; one owner-named `post_deploy` step per target environment; one smoke test per target environment; the admin-consent step's description extended to name the new permission |
| `docs/architecture/…-architecture.md` | Three §12 rows (caller identity, trigger setting, endpoint-URL secret); ADR-011 updated with an explicit *"THE ADR STAYS OPEN"* note |
| `provisioning/README.md` | Two inventory rows; a new **Automated tests** section |

**One design consequence worth stating explicitly.** Because Microsoft publishes no
workflow-definition property for this setting, the managed solution **cannot** carry the control.
That means every environment's endpoint depends on a configuration step being performed, and the
only thing that can prove it was performed is the smoke test. The smoke test is therefore not
belt-and-braces here — it is the sole verification mechanism, which is why it is
deployment-halting on PRD and why the flow-body coupling it depends on is itself asserted by a
test (§9.6).

---

## 6. Security Controls Implemented

Reference: TAD §6. Applied `skills/how-to-review-code.md` before this section was written.

| TAD §6 concern | Implementation in this release |
|---|---|
| **Authentication — the one public endpoint** | Trigger-level authentication is the primary control and rejects anonymous callers before the definition runs. The first action of the intake flow is a second, application-level gate comparing the caller's client ID against `rev_IntakeAllowedClientId` (NFR-008, C-TECH-006). Terminates `Cancelled` so a scanner does not page the process owner |
| **Authorisation — inner gate** | Two security roles ship as solution components with **no user assignment inside the solution** |
| **Authorisation via group teams (C-TECH-040)** | `bind-roles-to-groups.ps1` creates the AAD-Security-Group-type group teams and binds the roles **by name**; `allowedDirectRoleAssignments: []` in both settings files; `verify-role-bindings.ps1` asserts the absence of direct user-to-role assignments as a pipeline smoke test |
| **Authorisation — column level (NFR-001, NFR-003, ADR-002)** | `REV_TrusteeRestricted` with **34** field permissions (17 before revision 0.2). Enforced by the platform *below* the app layer, so no app, view, export or API call can bypass it. Membership applied per environment, never in the solution. **Now mechanically verified in both directions** by `scripts/verify-field-security-coverage.py`, wired into the build — because a secured column missing from the profile is unreadable by every application persona and the symptom is a blank field, not an error message. One reviewed exemption: `rev_breaklocation`, trustee-visible by design |
| **Separation of duties (NFR-002)** | No `rev_bankaccount` / `rev_payment` privilege of any kind in either role — the tables do not exist yet, and the role files record that when they arrive the Admin role must still hold none |
| **Audit logging (C-DOM-010, C-DOM-011, NFR-014)** | `IsAuditEnabled=1` on all four tables and on every attribute; `IsRetrieveAuditEnabled=1`. `ensure-auditing.ps1` enables organisation auditing and sets retention to 2192 days (6 years, confirmed by the reviewer). Native Dataverse field-change auditing supplies timestamp (UTC), actor, action, record identifier and before/after values — exactly the C-DOM-011 schema — without custom code |
| **Audit integrity (C-DOM-012, ADR-019)** | Neither role carries an audit-deletion privilege, and the role files say so explicitly. Deleting audit history requires Dataverse System Administrator, which no application persona holds |
| **No personal data in logs (C-DOM-004, NFR-012)** | Structural: `rev_errorlog` has no column able to hold personal data. Behavioural: every call to the failure-alert child flow passes a *reference* — application reference, submission ID, or a synthetic date key. Message truncation is defence in depth. The daily summary's queries select only `rev_applicationid` |
| **Input validation (C-TECH-004)** | Typed trigger schema with `required`; explicit completeness check before any write; the scoring flow reads only its named scored columns. **Revision 0.2 replaced a free-text blob with eight typed columns** (§2.3.3), which is input validation bought at the schema level rather than asserted in a flow — a yes/no column cannot hold a paragraph |
| **Injection (C-TECH-005)** | Two OData `$filter` expressions incorporate user input. Both escape single quotes by doubling — the platform-correct OData escaping. See the caveat in the constraint check |
| **Privileged actions (C-DOM-021)** | Bulk-delete job creation is a `post_deploy` provisioning step behind a pipeline gate, not available to `REV Admin`. Admin configuration is `rev_setting` with auditing enabled on that table. No export-to-Excel concern in Phase 1 — the Trustee role does not exist yet |
| **Least privilege (C-DOM-020)** | Two narrow roles, each with an explicit *deliberately absent* block naming what it cannot do and why. See §6.4 |
| **Secrets (C-TECH-001, C-TECH-002)** | **This release uses no runtime secret at all.** No secret, token or connection string appears in the solution source or in either settings file. CI credentials come from CI secrets. If ADR-011 selects the shared-secret intake route, a Key Vault-backed secret-type environment variable becomes mandatory — §7 D-1 |
| **DLP (C-TECH-045)** | Three connectors only — Dataverse, Teams, Office 365 Outlook — plus the Request/HTTP trigger. All four belong in the business group, and the DLP operation in `tenant_prerequisites` names them. No connector is referenced that this release does not use |

### 6.1 Two documented deviations from TAD §6.2, both flagged for reviewer acknowledgement

**(a) `REV Admin` is granted Write on `rev_errorlog`. TAD §6.2 grants it Read only.**
`rev_errorlog` carries `rev_resolved` and `rev_resolvednote`, which exist precisely so a human can
close an error. With read-only access both columns are unusable and the Unresolved Errors view can
never be cleared. Admin is **not** granted Create (error rows are written by the service identity;
a human-created error row would corrupt the operational record) or Delete (deleting an error row
would hide a failure — rows leave only through the 90-day bulk-delete job).

**(b) `REV Service Automation` is narrower than TAD §6.2, which gives it "everything `REV Admin`
has".** Three intentional narrowings, all in the direction of less privilege (C-DOM-020):

| Narrowed | Reason |
|---|---|
| **Read** on `rev_setting`, not Create/Write/Delete | The service identity only ever reads configuration. Rows are seeded by the separate deployment identity and changed by the process owner |
| **No Delete** on `rev_applicant` or `rev_application` | No Phase 1 flow deletes anything. Retention runs as system bulk-delete jobs, not under this role. The erasure helper flow that will need delete is Phase 4 |
| **No Assign or Share** on any table | This identity never hands a record to anyone |

Neither deviation changes the *effective access* the Security Model's §6 access matrix defines —
which is what the DPO signs off — and (b) reduces it.

### 6.2 One structural control worth naming separately

FR-016 / NFR-001 required special-category data to be excluded from the automated score. Rather
than asserting it, the scoring flow simply never references the special-category columns, and
`build.yml` fails the build if any of their names appears in that flow's definition. A future edit
that reintroduced health data into an automated decision would break CI rather than reach
production.

**Revision 0.2 widened this gate from four column names to twelve, and found a way it could have
failed silently.** The original list was `rev_narrativeraw`, `rev_otherconditionraw`,
`rev_conditionprofile`, `rev_supportrecipientconditionprofile`. The new column
`rev_supportrecipientotherconditionraw` **would not have matched any of them** — it contains the
substring `otherconditionraw` but not `rev_otherconditionraw`, so a grep for the original four
passes over it. That is worth recording as a property of this style of gate: a substring gate is only
as good as its list, and **the list must be extended in the same change that adds a
special-category column**. Six names were added for the new columns, plus `rev_receivesbenefits` and
`rev_benefitprovider`, because SDD §7.1 puts benefit status at the highest restriction tier and it
must not reach an automated decision either. The eligibility check that legitimately uses finance
reads `rev_incomeband` alone.

### 6.5 One DERIVED classification decision the reviewer must accept or reject (revision 0.2)

Seventeen columns were added with `IsSecured=1` in revision 0.2. **Thirteen of them are
uncontroversial**: third-party identities (carer, group members), special-category free text
(support-recipient other condition, care-support description, carer support, care-costs explanation,
exceptional-funding detail and its "other" text), and the applicant's own identity columns (title,
first name, last name, address line 2, town/city).

**Four are a judgement call, and it goes further than the source documents require:**
`rev_receivesbenefits`, `rev_benefitprovider`, `rev_carecostsexplanation` and
`rev_unabletofundexplanation`. All four hold content that previously lived in `rev_financialanswers`
— **which was `IsSecured=0`.** So this is a tightening of the existing posture, not a like-for-like
port of it.

The basis is SDD §7.1, which classifies benefit status alongside health data at the highest
restriction tier, and the observation that naming a specific disability benefit reveals health
information as surely as naming the condition does. The line drawn is that the **yes/no financial
facts a trustee needs to judge a case** — currently working, has significant care costs, has savings
over £6,000 — stay readable, while **benefit status and the free-text explanations** do not.

**If the reviewer prefers the previous posture**, four `IsSecured` flags and four profile entries
come out together and `verify-field-security-coverage.py` will confirm the two files still agree.
Nothing else depends on it. **Accept or reject** — checklist item in the Code Review Checklist below.

> ✅ **REVISION 0.3: REVIEWED AND ACCEPTED, UNCHANGED. No action was taken and none is needed.** The
> reviewer accepted the tightening as it stands — the four columns (`rev_receivesbenefits`,
> `rev_benefitprovider`, `rev_carecostsexplanation`, `rev_unabletofundexplanation`) keep
> `IsSecured=1` and their `REV_TrusteeRestricted` entries. The reviewer also confirmed the assessment
> that it is **trivially reversible**: flip `IsSecured` back to 0, or extend the field security
> profile to release the columns to a wider profile, and **there is no data impact either way** —
> nothing has been written to a live environment yet, and Dataverse column security is evaluated on
> read against the profile rather than stored with the row, so reversing it later would not require
> migrating or re-writing a single value. Recorded here so the decision is not re-litigated: it is
> **closed, accepted**.

### 6.3 Gates that sit above this release

- **DPO sign-off, SDD OQ-004/005/006.** ADR-002 (column security as the trustee anonymisation
  control) is `Adopted (conditional)` on OQ-004. The profile is built; the basis is not signed off.
- **DPIA and RoPA are concept drafts** (TAD risk A-R21). Art. 35 requires completion before go-live.
- **The three board criteria, SDD OQ-001/002/003.** PRD cannot be seeded until they exist.

---

## 7. Known Limitations / Deferred Items

### 7.1 Nothing here has been validated against a live environment — the specifics

> ⚠️ **SUPERSEDED IN PART BY REVISION 1.0 (§2.7) — a live DEV environment now exists and the
> solution is deployed to it.** This section's framing ("no environment exists") is historical.
> What it got right: every item it flagged as written-from-convention-and-unvalidated was worth
> distrusting, and several were genuinely wrong. What it got wrong: items 1, 2, 3, 3a and 11 are
> now CLOSED by live import (see §2.7 and the handover document for what each actually turned out
> to be), and the proposed remedy throughout — "build it in the DEV UI and re-unpack" — has a
> faster form: create a minimal instance via the **Web API**, then `pac solution export` +
> `pac solution unpack` and read the real serialisation.
>
> **Items 4–9 survive unchanged and are the live risk list now**: a successful import does not
> exercise an alternate-key retrieval, a `runas` numeric, a `BulkDelete` serialisation or an
> `@odata.bind` casing. Only a flow actually *running* does, and **no flow has run yet.**

No DEV, TST/ACC or PRD environment exists (WBS 0.2). `pac admin list` confirms only a default
Dataverse environment. **`pac solution check` and import have still not been run — but as of
revision 0.5, `pac solution pack` HAS, and this section's previous claim that it had not is what
was hiding nine defects.** See §2.5. `pac solution pack` needs no tenant and no authentication;
treating it as blocked on an environment was the mistake, and it cost four revisions.

What *has* been run (re-run after revision 0.5): **`pac solution pack` for BOTH package types on
both available `pac` versions — four clean packs, all exit 0** — plus inspection of the resulting
.zip files to confirm all 35 component instances are actually inside them (§2.5.4); XML well-formedness on
all **43** XML files; JSON parse on all 4 flow definitions and both settings files; PowerShell
parse on all 4 new scripts (pwsh 7.6.4, zero errors); the two-way manifest/source consistency
check (**35 root components**, both directions, against corrected assertions — §2.5.5); the
two-way field-security coverage check (**34 secured columns, all released, 1 reviewed
exemption**); and all four grep gates.

**What packing does and does not prove.** It proves the *layout and shape* are right: every
component is found, named, keyed and placed in the archive. It does **not** validate the
*content* of any element against the Dataverse metadata schema — the packer copies element bodies
through opaquely. So items 1, 3a and 4–8 below survive revision 0.5 unchanged: a privilege name,
a calculated-column formula dialect or a navigation-property casing can still be wrong and pack
perfectly. Only `pac solution check` and a real import test those.

**One packaging risk is specific to revision 0.3 and belongs in the table below in spirit:** converting
`rev_feelingscaleanswer` from `picklist` to `int` is a **column type change** on a column that, in a
live environment, would already hold option values. In this repository it is only ever a change to
hand-authored source that has never been imported, so there is nothing to migrate — but if the solution
*has* been imported anywhere by the time this is read, a `picklist` → `int` change is not an in-place
alter in Dataverse: the column must be deleted and recreated, which loses data. **Confirm before the
first import that no environment already holds this column**, and if one does, treat it as a
recreate-and-backfill rather than an update.

Ranked by likelihood of biting on the first import:

| # | Risk | Detail and remedy |
|---|---|---|
| 1 | **Platform privilege names in the two role files** | The custom-table privileges are deterministic (`prv<Verb>rev_<table>`). The 17 shared platform privileges — including `prvReadEnvironmentVariableDefinition`, `prvReadEnvironmentVariableValue`, `prvReadTransactionCurrency` — are written from convention and are **not validated**. An unrecognised privilege name fails the import. **Remedy: build both roles once in the DEV UI and re-run `pac solution unpack`.** TAD §6.2 explicitly rejects a shared base role, so the platform block is necessarily repeated in both files |
| 2 | ~~**App module and sitemap XML**~~ | ✅ **CLOSED BY REVISION 0.5 — and it was wrong, exactly as suspected.** The guess was `AppModule.xml` + `AppModuleSiteMap.xml` together in the app's folder. The packer puts the app sitemap in its own top-level `AppModuleSiteMaps/<app>/` folder, requires the root element `<AppModuleSiteMap>` with a `<SiteMapUniqueName>` child, and requires the `RootComponent` for it (and for the app) to be declared **by name, not by GUID**. All four now verified by a real pack, both package types (§2.5.2 defects #6, #7, #9). Note this item correctly predicted a defect but proposed the wrong remedy: no DEV environment was needed — decompiling the packer answered it |
| 3 | ~~**`FieldSecurityProfiles/` folder form**~~ | ✅ **CLOSED BY REVISION 0.5 — the folder form was wrong, and it failed SILENTLY, which this item did not anticipate.** The contingency written here ("if `pac solution pack` rejects it…") assumed the wrong form would be *rejected*. It was not: `FieldSecurityProfileProcessor` reads only `Other/FieldSecurityProfiles.xml` and returns null without a word if it is absent, so the pack succeeded and shipped **34 secured columns with no profile releasing them** — unreadable by anyone but a System Administrator. Now at `Other/FieldSecurityProfiles.xml` with `name` and `fieldsecurityprofileid` as attributes, and the presence of the profile in both .zip files verified (§2.5.2 defect #4, §2.5.4). **The general lesson is recorded in §2.5: a successful pack is not evidence a component shipped** |
| 3a | **The two calculated columns — `rev_applicant.rev_fullname` and `rev_application.rev_costs`** (revision 0.2) | Written as `<SourceType>1</SourceType>` plus a `<Formula>` element, **from convention, never validated**. If `pac solution pack` rejects that form, or if the packer expects the formula in a different element or dialect, both columns fail. **Remedy: create both calculated columns in the DEV UI and re-unpack** — the same remedy as items 1 and 2. Two behavioural consequences to confirm on first import, both of which the design depends on: that neither column can be written by the intake flow, and that `rev_fullname` can still be *displayed* in the Active Applicants view (it is a display cell only; the view orders by `rev_name`, so no calculated-column sort is required) |
| 4 | **`rev_applicantid@odata.bind` navigation-property casing** | Written lowercase to match the attribute's declared `PhysicalName`. If the real navigation property is `rev_ApplicantId`, the create action fails with a bad-request. One-line fix, but it fails the very first end-to-end test |
| 5 | **`subscriptionRequest/runas` numeric value** | Set to `4`, expressing "Flow owner". The intent is documented in the flow; confirm the numeric on first import |
| 6 | **Alternate-key retrieval syntax in the Dataverse connector** | Settings are read with `recordId: "rev_name='LikertPointMap'"`. This is the documented alternate-key form but is unexercised here |
| 7 | **Field security profile → team navigation property** | `ensure-column-security-profile-members.ps1` probes `teamprofiles_association` then `teamprofiles` and reuses whichever resolved, failing with an actionable message if neither does. Confirm the real name in `$metadata` and collapse the candidate list |
| 8 | **`BulkDelete` `QueryExpression` serialisation** | Enum members are emitted as OData names (`Equal`, `OlderThanXMonths`, `And`, `LeftOuter`). Also unverified: whether a picklist condition's `Values` needs a type annotation, and whether `ToRecipients: []` is accepted. One live `BulkDelete` call in DEV settles all of it |
| 9 | **Link-entity criteria in a bulk-delete job** | The withdrawn/incomplete job joins to `rev_applicant` and puts `OlderThanXMonths` on `rev_lastcontactdate` — the accurate rule. The documented fallback (filter on `rev_submittedon`) is recorded in-script *as an approximation*, with the reason it is one |
| 10 | **Entra permission GUIDs are `{{PLACEHOLDER}}` tokens** | Deliberate, matching the repo's own convention. App-role GUIDs are tenant-stable but were not written from memory: a wrong GUID grants a permission nobody reviewed. Look each up in the tenant. The scripts fail fast while a token remains, so this cannot be forgotten silently |
| 11 | **Flow folder layout** | Flows are at `Workflows/<Name>-<GUID>/<Name>-<GUID>.{json,xml}` as instructed. Real `pac solution unpack` emits these **flat** as `Workflows/<Name>-<GUID>.json` + `.xml`. `build.yml`'s glob is recursive so both layouts validate; the layout will normalise on the first real unpack |

### 7.2 Two implementation decisions a reviewer should confirm

**D-1 — the intake endpoint trust route is still open (TAD ADR-011, SDD OQ-014).** The intake flow
is written for the **Entra OAuth** route: trigger-level tenant authentication plus a client-ID
check against `rev_IntakeAllowedClientId`. The two alternatives are not built:

| Route | What changes | Consequence |
|---|---|---|
| **Entra OAuth** (as built) | Nothing. `rev-wordpress-intake` is created; Alex implements a client-credentials token call | **No secret exists anywhere**, so C-TECH-002 is satisfied by having nothing to store |
| Shared secret | The caller check compares a **secret-type, Key Vault-backed** environment variable. `rev_IntakeAllowedClientId` and `rev-wordpress-intake` are dropped | Introduces **Azure Key Vault, which is out-of-palette**, and no source evidences that Revitalise has an Azure subscription. C-TECH-002 makes Key Vault mandatory — a plain environment variable is readable by any maker |
| Scheduled REST pull | The trigger becomes a Recurrence and the caller check disappears entirely | No public endpoint and no inbound secret, but batch latency returns — one of the problems the programme exists to remove |

**This must be settled before Alex starts the integration.** The specification documents all three
so Alex is not blocked on reading, only on building.

**D-2 — a replayed webhook returns the existing reference and writes nothing.** TAD §5.1 says a
replay "updates rather than duplicates". Narrowed deliberately to a no-op: by the time a replay
arrives the process owner may already have overridden the status (FR-018), and silently overwriting
her decision with the original payload would be worse than doing nothing. **Flagged for reviewer
confirmation** — it is the one place this implementation narrows the TAD.

### 7.5 Revision 0.2's reviewer decisions — three now CLOSED by revision 0.3, two still open

**Status after revision 0.3:** D-3 **closed** (the score is out of 60), D-6 **closed** (referee and
emergency contact removed from intake), the §6.5 financial-security decision **closed, accepted
unchanged**. **D-4 and D-5 remain open and unchanged** — they need a reviewer answer before Build.
D-7 was already closed in revision 0.2.

**D-3 — is the circumstance score out of 55 or 60?** ✅ **CLOSED IN REVISION 0.3: IT IS 60, AND IT IS
BUILT THAT WAY.** The reviewer confirmed the score is the life-satisfaction question (0–10) plus ten
wellbeing questions at up to 5 each — **10 + 50 = 60**, which is what the export header, the data model
and the Automation Solution Design v0.5 all say. Revision 0.2's 55 was an accurate statement about a
five-option picklist that should never have been a picklist. **Four things moved together:**
`rev_feelingscaleanswer` is now a **Whole Number 0–10** (not an eleven-value option set — the reasoning
is in §2.4.1, and the decisive point is that option value `0` is unsafe in Dataverse and would make
*worst wellbeing* indistinguishable from *unanswered*); the `rev_feelingscale` option set is
**deleted**, along with its root-component declaration; `FeelingScaleInversion` is an **eleven-entry
map keyed 0–10** expressing `10 − answer`, which is the inversion the source specifies for Q1; and
`MaxCircumstanceScore` is **60** in both settings files. `rev_circumstancescore` needed no change —
revision 0.2 kept its ceiling at 60 for exactly this outcome. **The flow was already inverting, against
the old five-point map**, so the map had to be replaced in the same change or a valid answer of 7 would
have hit a missing key and killed the scoring run; §2.4.1 records that check. **SDD OQ-001 and OQ-002
are unblocked** — the board can now set absolute thresholds against a known 0-to-60 scale. §2.4.1.

**D-4 — the intake payload contract was broken on purpose.** `full_name` → `first_name` +
`last_name`, and `costs`, `financial_answers` and `wellbeing_answer_11` left the contract. A clean
break was chosen over accepting both shapes because Alex has not built the integration yet and the
alternative — splitting a full name on whitespace — gets compound surnames wrong quietly and
permanently. **The failure mode if a caller misses this is silent: a payload sending `full_name`
stores no name at all**, because the target column is calculated. The form specification carries this
in a banner at the very top. **Confirm that the form specification has not yet been issued to Alex as
CONFIRMED** — if it has, this needs a deliberate re-issue rather than a quiet revision. §2.3.4.

> **⚠️ Overtaken by revision 0.7, and the question inverts.** It was never going to be issued to Alex
> as a build contract, because the form was already built. The live-form evidence confirms the shape
> of this contract change is right — the form does send first and last name separately, does send the
> three component costs, and does send ten wellbeing answers rather than eleven — so `full_name`,
> `costs`, `financial_answers` and `wellbeing_answer_11` are correctly absent. **What actually needed
> fixing was the opposite direction:** two fields the contract *required* that the live form does not
> send. See §2.6.2.

**D-5 — five option sets carry placeholder values.** `rev_title`, `rev_applicanttype`,
`rev_breaktype`, `rev_helperrelationship`, `rev_exceptionalcircumstance`. The export proves each
question is asked and carries no option list, so the values were inferred and are marked as
placeholders in each file, in each column description, and in the form specification. The `Other`
options in `rev_breaktype` and `rev_exceptionalcircumstance` are **not** placeholders — the export's
separate "Other type of break" and "Other exceptional circumstance" columns prove they exist. Confirm
the approach (build now with placeholders, confirm before PRD) or say they should be left out until
confirmed.

> **⚠️ Revision 0.7 — the placeholders are no longer needed, and the problem inverts.** The live form
> carries all five option lists and they are now recorded verbatim in the form document §6. **The values
> in the committed option sets are wrong, not merely unconfirmed:** applicant type has three options on
> the form against four in the set, break type five against nine, exceptional circumstance four against
> seven, "Relationship to you" is **free text** against a picklist column, and the Title sub-field is
> **disabled on the form** so `rev_title` will never be populated at all. The condition profile is worse
> — ten functional areas on the form against eight condition types in the set, classifying along
> different axes. **None of these was changed in revision 0.7**, because trimming or renumbering an
> option set is safe before any application exists and unsafe after, and the condition-profile case
> needs a classification decision from Emily. See form document §9, gaps M-01, M-05 and M-07. The
> approach question above is answered: **stop treating them as placeholders and reconcile them against
> §6 in one deliberate pass before PRD.**

**D-6 — Referee and Emergency Contact.** ✅ **CLOSED IN REVISION 0.3, AND THE INTAKE FLOW NO LONGER
TOUCHES THEM.** The reviewer confirmed the mechanism precisely: these details are collected on a
**separate form, sent to the relevant party after the board approves the grant** — not on the main
intake form, and not through anything this flow does.

- ✅ **The five fields are OUT of the intake contract.** `referee_name`, `referee_email`,
  `referee_phone`, `emergency_contact_name` and `emergency_contact_phone` have been removed from the
  trigger schema **and** from the `Create_application` mapping. Revision 0.2 kept them on the
  reasoning that "removing the only route that can write these columns would leave them unreachable";
  that reasoning is void now the route is known to be a different form in a different automation.
  Nothing in the flow references, accepts or writes them. §2.4.2.
- ✅ **The five COLUMNS are unchanged.** They stay on `rev_application`, still `IsSecured=1`, still
  released by `REV_TrusteeRestricted` — they are the destination for that separate form's answers, and
  the process owner can fill them in by hand meanwhile. `verify-field-security-coverage.py` still
  reports 34 secured columns, all released.
- 📌 **The mechanism is Automation #3 (Grant Acceptance, Phase 2) design scope, and is not built or
  designed here.** That is a scope statement, not a gap: Phase 1 has no acceptance automation.
- 🔄 **ONE THING REMAINS OPEN, and it belongs to that future design: who receives and completes the
  separate form** — the applicant relaying the referee's and emergency contact's details, or the
  referee and emergency contact **self-reporting their own**. It is **not yet specified**, and the two
  answers are materially different builds: self-reporting needs a per-recipient link, a way to identify
  the right person, and a lawful-basis and privacy-notice position for approaching a third party the
  charity has no relationship with. **Not decidable or buildable in this release.** Carried in §7.4
  and in form-spec OPEN-23.

**D-7 — condition profile placement.** ✅ **CLOSED. It stays on `rev_application`, not
`rev_applicant`. No change made.** This had been carried as an open question; it is now resolved, and
the reasoning is worth keeping because it will be asked again:

1. **It would conflict with Application-anchored retention.** The retention design deletes
   applications on a clock driven by the application's own outcome (12 months from `rev_decisiondate`,
   6 months from `rev_lastcontactdate`), with applicants swept only when orphaned. A condition profile
   on the applicant would outlive the application whose assessment it belonged to.
2. **It would require extending Trustee access and field security to `rev_applicant`,** where the
   Trustee persona currently has **zero** access of any kind. The condition profile is deliberately
   trustee-visible (TAD §3.1); moving it would mean opening a table that holds name, address, date of
   birth and email to a persona that today cannot see the table at all. That is a large security
   change to buy a small normalisation.
3. **It would break per-application audit integrity.** A condition profile is *evidence for a specific
   decision*: it is what the trustees saw when they judged that application. Overwriting it on a repeat
   application would silently rewrite the evidence behind a decision already taken. **This codebase
   already has the precedent** — `rev_privacynoticeacceptedon` is deliberately never overwritten on an
   applicant refresh, for exactly this reason, and the intake flow says so at the point of use.

### 7.3 Deferred automations (recorded, not built)

| Automation | Components not built | Blocked on |
|---|---|---|
| **#3 Grant Acceptance** (FR-041–FR-047) | `REV \| Acceptance \| Create Envelope / Reminders & Escalation / Completion`; `rev_grant`; DocuSign connection reference; SharePoint signed-PDF library; the 6-year retention job | DocuSign account and template; UK residency evidence |
| **#5 Anonymisation & Trustee Pack** (FR-026–FR-033) | `REV \| Narrative \| Scrub Free-Text`; `REV \| Narrative \| Trustee Pack`; AI Builder + Word Online connection references; `rev_narrativeredacted`, `rev_redactionconfidence`, `rev_redactionreviewrequired`, `rev_redactionreleased` | AI Builder credits (risk A-R16, the 1 Nov 2026 seeded-credit change); DPO sign-off on ADR-002 |
| **#6 Trustee Review Portal** (FR-034–FR-040) | The **Code App** (ADR-003); `rev_review`; `REV \| Portal \| Finalise Decisions`; `rev_anonymisedstatistic`; the `REV Trustee` role; `rev_eligibleforround` | #5 must land first — a portal with nothing redacted to show has nothing to show |
| **#7 Duplicate-Grant Check** (FR-023–FR-025) | `REV \| Duplicate \| QBO Check`; QuickBooks connection reference; `rev_duplicateflag` and the prior-grant columns | QBO edition confirmation; whether payments carry a searchable applicant identifier (SDD OQ-015/016) |
| **#8 Finance / Capture Payment** | `REV \| Finance \| Capture Payment`; `rev_bankaccount`, `rev_payment`, `rev_provider`; `REV Finance` role; `REV_FinanceOnly` profile | **Has no FR behind it** (TAD §3.5 conflict 2). Reviewer must authorise it as an SDD scope addition or descope the flow |
| **Retention & erasure helper** (FR-049–FR-055) | `REV \| Retention \| Retention & Erasure Helper`, all three modes | Mode 3 (SAR) has **no agreed mechanism** — see §7.4 |

FR-023's call site is marked in the intake flow by a single `Compose` action named
`DEFERRED_call_duplicate_grant_check`, so the insertion point is unambiguous rather than
rediscovered. It is reported as a C-TECH-013 SOFT warning below, honestly — it writes nothing.

### 7.4 Open items carried forward

| Item | Status |
|---|---|
| **WBS 0.3 — scoped Conditional Access exception for the service account's *unattended* sign-ins** | ⛔ **BLOCKING, still outstanding with Wanstor.** Interactive browser sign-in is confirmed working; device-code / public-client sign-in is CA-blocked. All four flows run unattended as this account, so they cannot be relied upon in TST/ACC or PRD until this is confirmed. SDD OQ-018, TAD risk A-R13 |
| Group creation without a directory role | Tenant self-service group creation is enabled, so `ensure-groups.ps1` can run today. **If that tenant setting is later disabled, group creation fails** and Groups Administrator or Directory Writer becomes a hard prerequisite. Recorded in `pipeline.yml` |
| **C-DOM-005 — no SAR extract mechanism** (FR-053) | Accepted as a known gap by the reviewer at the architecture gate (TAD §4.2, risk A-R22). **Carried forward unresolved.** The four questions in TAD §4.2 remain open, and there is no SAR turnaround SLA in any source (SDD OQ-023), so the test-agent has no threshold to test against even once a mechanism exists |
| SDD OQ-001 / OQ-002 / OQ-003 — board criteria | PRD seeding is blocked by design until these exist. **OQ-001 and OQ-002 are no longer blocked on anything technical**: revision 0.3 fixed the score's scale at 0 to 60, which is what those two absolute thresholds are expressed against (§2.4.1) |
| SDD OQ-004 / OQ-005 / OQ-006 — DPO decisions | Gate above go-live. ADR-002 conditional |
| SDD OQ-020 / OQ-021 / OQ-023 — performance, availability, SAR SLA | No thresholds exist, so the test-agent has nothing measurable to verify in those categories |
| SDD OQ-026 — Provider classification | Not reached; `rev_provider` is deferred |
| SDD OQ-027 — whether ethnic group is captured | ⚠️ **THE FACTS CHANGED IN REVISION 0.2, AND THE REVIEWER AND DPO NEED TO KNOW.** OQ-027 is framed as "where captured", implying it was unknown whether the charity collects ethnic group at all. **The raw export settles it: column 150 is "Ethnic group", so the live form does collect it.** `rev_ethnicgroup` remains deliberately **absent** from the committed schema — it was excluded at the SDD-intake gate pending DPO input, and that gate has passed, so **this pass did not add it and no action is proposed here**. What changes is the question: it is now "should we keep collecting it, and on what lawful basis" rather than "is it collected". The form specification's OPEN-17 carries the same note. Nothing to remove if the answer is no |
| ~~ADR-007 — ALM tooling~~ | ✅ **CLOSED IN REVISION 0.4 — Power Platform Pipelines, by explicit reviewer decision.** The earlier entry said pac CLI + GitHub Actions was "resolved in practice by generating these config files", and that if the reviewer preferred Pipelines "both config files are discarded". **Neither was right.** The reviewer chose Pipelines, and the config files were *revised*, not discarded: the build config is almost unchanged (every gate validates solution *source*, which Pipelines does not touch), and the pipeline config gained an `alm` block in place of its two `deploy_command`s. GitHub Actions keeps validate/build/stage-DEV; Pipelines owns DEV → TST/ACC → PRD. §5.4, TAD ADR-007 |
| 🆕 **Can a service principal *request* a Power Platform Pipelines promotion?** | **UNVERIFIED, and the reason `promote_mode` is `manual`.** `pac pipeline deploy` is documented and its parameters were verified against pac 2.4.1, but every Microsoft example has a *maker* requesting the deployment; service principals appear only as the *delegated* identity that performs the import, or as the caller of `UpdateApprovalStatus`. Settle this before switching either environment to `promote_mode: cli`. The `cli` path is built and carries a `pac pipeline list` pre-flight that fails with the exact roles to grant. §5.4.5 |
| 🆕 **What do `--currentVersion` and `--newVersion` actually mean?** | **UNVERIFIED.** The CLI reference says only "Current solution version" / "New solution version". Whether *current* refers to DEV or to the target, and whether the two may be equal on a first release, is undocumented. Observe it on the first UI-driven promotion. §5.4.5 |
| 🆕 **Managed Environment licences for TST/ACC and PRD** | **NEW COST, needs confirming with Revitalise.** Pipelines requires all target environments to be Managed Environments, which requires premium use rights. From February 2026 Microsoft enables this on pipeline targets automatically. Confirm alongside the A-R18 database-capacity check, before provisioning. TAD §12, §5.4.3 |
| 🆕 **DEV is now overwritten from git on every CI run** | The `stage-dev` job imports the unmanaged solution with `--force-overwrite`, so **a maker who edits in the maker portal without committing loses that work**. This is the intended TAD §9.2 posture, but nobody has been told. Belongs in the ALM runbook before DEV is handed to anyone. §5.4.2 |
| 🆕 **`pac-import-tstacc.json` / `pac-import-prd.json` are no longer applied by any tool** | Pipelines does not accept a deployment settings file. Both files are retained as the code-reviewed record of values an operator types into the deployment pane. C-TECH-047 still holds, but its enforcement is now a person reading a file. If that is not acceptable, the alternative is to keep a `pac solution import` path for PRD — which would defeat the point of ADR-007. §5.4.2, §10 |
| 🆕 **C-TECH-030's wording no longer matches reality** | HARD, scoped to pipeline-agent. Its *intent* is met more strongly under Pipelines (platform-enforced immutability and stage order), but "the artifact **produced by the build-agent**" no longer describes what is deployed. The constraint text needs amending by its owner (Tech Lead / Platform Architect); agents do not edit `constraints/`. Raised in §10 |
| ~~**Three schema gaps found while writing the form specification**~~ | ✅ **TWO CLOSED IN REVISION 0.2.** (a) **CLOSED** — `rev_carername` and `rev_carersupport` added, both secured and profile-released (form spec OPEN-2). (b) **CLOSED** — `rev_supportrecipientotherconditionraw` added, mirroring `rev_otherconditionraw` exactly; the export confirms the column is real, col 78 (form spec OPEN-3). (c) **STILL OPEN, and deliberately so** — `rev_travellingwithcarer`'s description still says the value is "worked out automatically from the intake answers" when the form asks it directly. It is a wrong description on a correct column, changes no behaviour, and was left alone in a pass already touching two entity files heavily, to keep the diff reviewable. **One-line fix, recommended for the next pass** |
| **No requirement obliges Revitalise to email the applicant their reference** | FR-008 creates the reference, FR-009 notifies Emily, nothing notifies the applicant. The confirmation screen cannot show the reference (it does not exist until Dataverse assigns it), so the specification has it promise an email — a promise currently unbacked by any requirement or component |
| **Abandoned website drafts** | FR-005 save-and-continue means partially completed applications holding special-category data sit on Alex's platform. They appear in neither the retention schedule (SDD §7.6) nor the RoPA. Needs a DPO position |
| ~~**The 11 wellbeing question texts do not exist in any source**~~ | ✅ **CLOSED — texts in revision 0.2, response scales in revision 0.3.** All eleven real question texts came from the export: one ONS life-satisfaction question (col 95), the seven **SWEMWBS** items (cols 96–102) and three Revitalise "last year" questions (cols 103–105). Revision 0.3 closed both remaining scale questions: `rev_likertresponse` now carries the confirmed **frequency** labels (None of the time / Rarely / Some of the time / Often / All of the time) in place of the agree/disagree ones, and the life-satisfaction question is a **0–10 whole number**. **The value direction was re-verified against all ten question texts individually, not assumed** — all ten are worded positively, so value 1 is the highest-need answer and `LikertPointMap` was already correct; **no value and no mapping changed** (§2.4.3). What is left is **one licensing question that blocks nothing**: if Revitalise intends to report SWEMWBS scores against national norms it must hold a licence for the instrument, and nobody has confirmed whether it does. The wording and scale are now used as published either way |
| ~~🆕 **The maximum circumstance score is 55 or 60, and nobody has decided**~~ | ✅ **CLOSED IN REVISION 0.3 — it is 60.** The life-satisfaction question is a 0–10 whole number, so 10 + (10 × 5) = 60: the picklist is deleted, the inversion map has eleven entries, and `MaxCircumstanceScore` is 60 in both settings files. **SDD OQ-001 and OQ-002 are unblocked.** §2.4.1, §7.5 D-3 |
| ~~🆕 **No mechanism exists for capturing Referee and Emergency Contact after approval**~~ | ✅ **MECHANISM CONFIRMED IN REVISION 0.3, and the intake flow no longer touches these fields.** They are collected on a **separate form, sent to the relevant party after the board approves the grant**. The five fields have been removed from the intake trigger schema and create mapping; the five columns stay on `rev_application` as that form's destination. Building that form is **Automation #3 (Grant Acceptance, Phase 2) design scope**, not Phase 1 work. §2.4.2, §7.5 D-6 |
| 🆕 **Who receives and completes the separate post-approval referee / emergency-contact form** | **NOT YET SPECIFIED, and open for Automation #3's design.** The confirmed mechanism says a separate form goes to "the relevant party" after board approval; it does not say whether that is the **applicant relaying** the referee's and emergency contact's details, or the **referee and emergency contact self-reporting** their own. The two are materially different builds — self-reporting needs a per-recipient link, a way to identify the right person, and a lawful-basis and privacy-notice position for approaching a third party the charity has no existing relationship with. **Nothing in Phase 1 depends on the answer**, which is why it is recorded rather than resolved |
| 🆕 **Does Revitalise hold a SWEMWBS licence?** | Only relevant if the charity intends to report its wellbeing scores **against national norms**. The seven SWEMWBS items are now used with their published wording *and* their published frequency scale, which is the condition a licence would impose, so **the build is correct either way and nothing is blocked**. Worth asking before the form goes live. Form-spec OPEN-1 |
| 🆕 **Five option sets carry PLACEHOLDER values** | `rev_title`, `rev_applicanttype`, `rev_breaktype`, `rev_helperrelationship`, `rev_exceptionalcircumstance`. The export proves each question is asked but carries no option list. Each file says so at the top; the form specification's OPEN-20 asks Emily for the real lists, most quickly taken from the live form's own configuration. **Renumbering an option after applications exist changes what historic rows mean**, so this is a before-go-live item |
| 🆕 **Is a postal form still offered?** | `rev_wouldlikeformposted` was built against export col 148, but the redesigned digital-first form may not offer a postal route at all, in which case nothing will ever set the column. **Question for Emily**: if there is no postal route, drop the field rather than collecting an answer nobody acts on; if there is one, say what happens when somebody ticks it. Form spec OPEN-25 |
| 🆕 **The applicant-facing question count nearly doubled** | 47 → 82, because the live form asks all of it. **But that form is the one producing part-completed applications 60% of the time**, so length is plausibly a cause rather than an incidental feature. Emily should be asked which questions can be dropped or deferred, not just handed a longer form. Form spec OPEN-19 — the most valuable open item on that list for the applicant's experience |
| 🆕 **Is the £6,000 savings threshold current?** | It is the live form's own wording (col 112) and matches the long-standing means-test figure, but it is fixed in the column label rather than configurable. Confirm before go-live; changing it later means changing the form and the column label together. Form spec OPEN-21 |
| 🆕 **The four declaration texts are Revitalise's to supply** | The export carries the four consent flags but their wording is static page copy. **Declaration wording has legal effect and was not invented here.** The age confirmation in particular must be worded consistently with whatever OPEN-14 decides about under-18 applicants. Form spec OPEN-24 |
| Adaptive Cards with a deep link into the app | Not implemented — needs a per-environment app URL, so a fourth environment variable. Usability improvement, not a defect |
| PowerShell module versions are not pinned | `provisioning-common.ps1` (pre-existing) uses `Assert-ModuleAvailable` with no version constraint. There is no package manifest in this repository, so there is nothing for C-TECH-020's audit to read; the modules are runner prerequisites documented in `provisioning/README.md`. Recommend pinning when a manifest exists |

---

## 8. Build Instructions

Single source of truth: **`config/revitalise-grant-automation-build.yml`**. Consumed by build-agent;
this section explains the parts that need judgement.

> ### ⚠️ Revision 0.5 — the pack steps now work, and a successful pack is NOT sufficient evidence
>
> `pack-managed` and `pack-unmanaged` in the build config needed no change: both commands were
> already correct and both now succeed (§2.5.4). What changed is what a reviewer or build-agent
> should conclude from a green pack.
>
> **Six of the nine defects revision 0.5 fixed produced a completely clean, zero-exit pack while
> silently omitting components from the archive** — including the field security profile that 34
> secured columns depend on. The packer processes only the component types listed as elements in
> `Other/Customizations.xml`, and several processors return null rather than erroring when their
> one expected path is missing. Neither condition is reported at any error level.
>
> **Therefore: after packing, assert on the archive, not on the log.** The minimum check, which
> takes a second and would have caught four of the six silent defects on day one:
>
> ```bash
> # every expected component collection must be non-empty in the packaged customizations.xml
> unzip -p build/artifacts/<run>/RevitaliseGrantAutomation-managed.zip customizations.xml \
>   | python3 -c 'import sys,xml.etree.ElementTree as ET; r=ET.parse(sys.stdin).getroot(); \
>     print({c.tag: len(list(c)) for c in r})'
>
> # and the archive must contain no unexpected loose files (a swept-in "sharded" component
> # is the signature of a folder the packer was never asked to read)
> unzip -l build/artifacts/<run>/RevitaliseGrantAutomation-managed.zip
> ```
>
> Expected counts are tabulated in §2.5.4; the archive should hold exactly seven entries.
> Recommended for the build-agent to add as a `verify-package-contents` step after
> `pack-managed` — raised as a build-config recommendation rather than edited in here, because
> `config/*-build.yml` is the build-agent's file to own.

**Artifacts — two, and deliberately only two:**

| Type | Path |
|---|---|
| `solution` | `RevitaliseGrantAutomation-managed.zip` |
| `provisioning` | `provisioning/` |

There is **no `teams-app` artifact**: Phase 1 uses Teams as a 1:1 chat notification through the
connector (ADR-015), so no team is provisioned and no Teams app package is installed. There is **no
`code-app` artifact**: the trustee portal Code App is Phase 3, so `C-TECH-048` has nothing to apply
to in this release.

**Fifteen steps** (fourteen before revision 0.2). Beyond the obvious (`clean`, `verify-tooling`,
`auth`, `pack-managed`, `pack-unmanaged`, `package-provisioning`), **eight** exist to make
constraints verifiable rather than asserted:

| Step | Enforces |
|---|---|
| `secret-scan` | C-TECH-001 — `gitleaks`, fails on any finding rather than warning. **`--no-git` added in revision 0.8 (D-006)** — without it `detect` scans commit history rather than the working tree, which is what `pac solution pack` actually reads, so the gate had been scanning none of the delivered solution source |
| `source-validate` | XML well-formedness on every component file; JSON parse on every flow definition; **asserts exactly 4 flows**, so a silently-missing flow fails the build |
| `root-components-resolve` | Two-way agreement between `Solution.xml` `<RootComponents>` and the definition files. **The gate that would have caught this task's interruption** |
| **`field-security-coverage`** — NEW 0.2 | **NFR-001 / NFR-003** — two-way check that every `IsSecured=1` column is released by a field security profile and no profile releases an unsecured column. A missing entry makes a column unreadable by every application persona, and the symptom is a blank field rather than an error |
| `no-special-category-data-in-scoring` | **FR-016** — greps the scoring flow for **twelve** special-category column names (four before revision 0.2). See §6.2 for why the original four would have missed `rev_supportrecipientotherconditionraw` |
| `no-hardcoded-environment-values` | C-TECH-047 — no environment URL, SPO URL or tenant UPN anywhere in solution source |
| `no-hardcoded-thresholds` | FR-017 / NFR-019 — no threshold key name next to a numeric literal in any flow |
| `provisioning-syntax` | C-TECH-042 — every `.ps1` under `provisioning/` parses |

All eight pass against the source as committed, re-verified after revision 0.2. `lint`
(`pac solution check`) and both `pack` steps have **never been run** — they need an authenticated pac
profile against DEV, which does not exist.

**Required CI variables — CHANGED IN REVISION 0.4:** `APP_ID`, `TENANT_ID`, `ENV_URL_DEV`,
`BUILD_VERSION`, `ACTIONS_ID_TOKEN_REQUEST_URL`, `ACTIONS_ID_TOKEN_REQUEST_TOKEN`.

**`CLIENT_SECRET` is gone.** The `auth` step is now
`pac auth create --githubFederated --applicationId "$APP_ID" --tenant "$TENANT_ID" --environment "$ENV_URL_DEV"`,
which exchanges the GitHub OIDC token for an Entra token with no stored secret. **C-TECH-044 is
resolved, not warned on** (§10, ADR-021). No `azure/login` step is needed — `pac` performs the
exchange itself.

The two `ACTIONS_ID_TOKEN_*` variables are injected by GitHub when the job declares
`permissions: id-token: write`. They are listed in `required_env_vars` deliberately: it converts a
forgotten permissions block into a named one-line build failure instead of an opaque failure inside
`pac auth create`.

`APP_ID` is an **environment-scoped** GitHub secret — DEV, TST/ACC and PRD each have their own deploy
app registration, so the value differs per GitHub Environment while the name stays the same (§5.4.4).

⚠ **If a `CLIENT_SECRET` secret still exists in the repository's GitHub secrets, delete it.** It is
now unreferenced, and an unreferenced credential is one nobody rotates and nobody notices leaking.

**Version:** `1.0.0.0`. First release, so `rollback_artifact` is empty — and note that rolling back
a *first* managed import is not symmetrical with a later one: uninstalling removes the tables and
their data. For 1.0.0.0 the rollback route is turn the four flows off, leave the solution in place,
fix forward. Populate `rollback_artifact` after the first successful PRD deployment (C-TECH-033).

---

## 9. Test Guidance

For test-agent. Deployment target is TST/ACC (combined Test and Acceptance, ADR-006), and test
fixtures must be synthetic — no production extract ever reaches this environment (C-TECH-007).

### 9.1 Test first, because it fails first

1. **Does the solution import at all?** Given §7.1, the first managed import is the real test of
   this release. Expect to iterate on role privileges, app module XML and the field security
   profile before any functional test runs.
2. **Are the flows off, and do they turn on?** All four import as Draft. They cannot be activated
   until the three connection references are bound — and that is blocked on the WBS 0.3
   Conditional Access exception.

### 9.2 Automation #4 — Intake

| Case | Assert |
|---|---|
| Happy path | HTTP 201, a `REV-2026-nnn` reference, one Application row, one matched-or-created Applicant, one Teams message carrying **name and reference** (FR-007, FR-008, FR-009) |
| 🆕 **Calculated `rev_fullname`** | POST `first_name: "Jane"`, `last_name: "Example"` → `rev_fullname` reads `Jane Example` **without the flow writing it**. Then attempt to PATCH `rev_fullname` directly and confirm the platform rejects it. Confirm the Teams message and the Active Applicants view both show the composed name |
| 🆕 **`full_name` is no longer accepted** | POST the revision 0.1 shape (`full_name`, no `first_name`/`last_name`) → **HTTP 400**, `rev_errorlog` row at `Warning`, and **no Applicant row created**. This is the regression that would otherwise store an application belonging to nobody |
| 🆕 **Calculated `rev_costs`** | POST `accommodation_cost: 600`, `travel_cost: 120`, `other_cost: 130` → `rev_costs` reads **850.00**. Omit `other_cost` → confirm the total is 720.00 and not null (Dataverse treats an absent money column as 0 in a calculated sum — **verify this, it is the one behaviour the design assumes and has not proved**) |
| 🆕 **Repeat applicant does not have their name rewritten** | Two submissions, same email/first/last, second with a changed `title` and `town_city` → **one** Applicant row, title and town refreshed, `rev_firstname`/`rev_lastname`/`rev_email` unchanged, `rev_privacynoticeacceptedon` unchanged |
| 🆕 **All seventeen secured columns the intake writes are writable by the service identity** | POST a payload populating every secured column the create maps (carer, helper identity, group members, benefits, all four explanations, support-recipient other condition) → the create **succeeds** and every value is readable by `REV Admin`. **A single secured column missing from `REV_TrusteeRestricted` fails the whole create**, which is why `verify-field-security-coverage.py` exists — but only a live import proves it. Note the count: **seventeen written by intake, 22 secured on the table** — the other five are the referee and emergency-contact columns, which revision 0.3 removed from this flow (§2.4.2) |
| 🆕 **The five referee / emergency-contact fields are gone from the contract** | POST a payload that includes `referee_name`, `referee_email`, `referee_phone`, `emergency_contact_name` and `emergency_contact_phone` → the application is created and **all five columns are null**, because nothing maps them any more. Then confirm `REV Admin` can still **set them by hand** on the created row through the app — that is the interim route until Automation #3's separate post-approval form exists (§2.4.2) |
| 🆕 **Four declaration blocks** | Each of the four sends its boolean and its own timestamp; confirm all eight columns are populated and that the timestamps differ from `rev_submittedon` |
| **Replay** | POST the same `submission_id` twice → HTTP 200 `already_received`, **exactly one** Application row, and the *original* status preserved even if it was changed between the two posts (D-2) |
| Unauthorised caller | Wrong or absent client ID → HTTP 401, **no Dataverse write**, **no Teams alert**, run status `Cancelled` |
| Incomplete payload | Omit `postcode` → HTTP 400, one `rev_errorlog` row at severity `Warning`, Teams alert, **no personal data in the log row** (FR-010, C-DOM-004) |
| Age band boundaries | Date of birth exactly 18 today, and 18 tomorrow → options 2 and 1. The off-by-one this guards is the reason the flow computes exact completed years |
| Age band absent | Empty `date_of_birth` (bypassing validation) → option 9 *Not known*, never option 1 |
| Region derivation | `BT1 1AA` → 12 Northern Ireland (two-letter wins over `B`); `B1 1AA` → 5 West Midlands; `BN1 1AA` → 8 South East; `ZZ99 9ZZ` → 13 *Not known*; a postcode with no space |
| Repeat applicant | Two submissions, same email and name → **one** Applicant row, two Applications, `rev_lastcontactdate` refreshed, **`rev_privacynoticeacceptedon` unchanged** |
| OData escaping | A name containing an apostrophe (`O'Neill`) → correct match, no error (C-TECH-004/005) |
| Concurrency | Two simultaneous POSTs, same applicant, different `submission_id` → **one** Applicant row |
| Teams failure | Break the Teams connection → still HTTP 201, application created, failure logged |

### 9.3 Automation #2 — Scoring

> **⚠️ REWRITTEN IN REVISION 0.9 FOR THE REVISION 0.8 SCORING MODEL (test report D-017).** Until
> revision 0.9 this section described the pre-0.8 engine, and a tester following it literally would
> have failed a correct build: it gave the reachable floor as **10** when it is **5**, described the
> FR-022 gate as emptiness-only, and carried **no case at all** for a fractional total, a midpoint,
> or `Derive_status` reading the rounded value — the three things revision 0.8 and 0.9 changed and
> the ones most worth testing. The shipped Pester suite was already correct throughout; it was this
> guidance that was behind it.

| Case | Assert |
|---|---|
| 🔄 **All 10 wellbeing answers at value `1` + life satisfaction `0`** | Score **60** — the maximum, and **the single most important scoring assertion in this release** (revision 0.3, §2.4.1). 10 × 5 = 50 from the wellbeing answers, plus `10 − 0 = 10` from the life-satisfaction answer. Breakdown names exactly **10** wellbeing lines plus the inverted life-satisfaction line, and says "60" as the maximum |
| 🔄 **All 10 at value `5` + life satisfaction `10`** | Score **10** (10 × 1 + `10 − 10`). **This is no longer the floor** — see the next row. It is the lowest score reachable using only the *ordinal* answers 1–5 |
| 🆕 **The reachable FLOOR is 5, not 10 (revision 0.8)** | All 10 wellbeing answers at value **`6` ("Not sure")** + life satisfaction `10` → score **5** (10 × 0.5 + `10 − 10`). **A tester working from the pre-0.9 guidance would call this a bug and it is the correct answer.** It matters to the board, not just to the suite: a knockout threshold at or below 5 was previously unreachable and now is not (§ the revision 0.8 banner, and SDD OQ-001 is still open) |
| 🆕 **Ground truth, end to end** | Reproduce **row 25 of `docs/Import/Book(Sheet1).csv`**: all ten wellbeing answers "Not sure", life-satisfaction raw `6` → score **9** (`10 − 6 = 4`, plus 10 × 0.5 = 5). This is a **real hand-scored application**, and it is the case that derived the 0.5 point value rather than assuming it. `ScoringInvariants.Tests.ps1` reconstructs all 25 rows statically; this asserts the live flow agrees with the hand-scoring |
| 🆕 **"Not sure" is storable and scoreable (D-014)** | Submit `wellbeing_answer_1: 6` → the answer **stores**, the application **scores**, and the breakdown line reads `response 6 (Not sure) = 0.5 points`. Before revision 0.8 the option value could not be stored at all and the flow's `int()` cast **threw on the null map lookup**: application created, run dead, no score, no status, nobody told. **Repeat on `wellbeing_answer_8`** — those three answers now use `rev_agreementresponse`, a different option set with the same values |
| 🆕 **The two response scales carry the right LABELS** | Answer value `1` on `wellbeing_answer_1` and value `1` on `wellbeing_answer_8`, then read both columns in the app and in a view: answer 1 must render **"None of the time"** (frequency) and answer 8 **"Strongly Disagree"** (agreement). The **score is identical either way** — the values and direction coincide — so this is an *evidence* test, not an arithmetic one, and the arithmetic passing is exactly why it needs its own case. Both scales must also offer **"Not sure"**: it is their one shared label (D-016) |
| 🆕 **A FRACTIONAL total rounds half UP — D-015, and it decides an outcome** | Submit an **odd** number of "Not sure" answers so the exact total lands on `X.5`. With the TST/ACC values in force (knockout ≤ 20, band 21–30) the case to run first is an exact **20.5**: `rev_circumstancescore` must read **21** and `rev_status` **3 Borderline** (a human review), **not** 20 and Auto-reject. Then **30.5 → 31** (Auto-pass, not Borderline) and **37.5 → 38**. Before revision 0.9 the first two were wrong and the third was right, because `formatNumber(…,'F0')` rounds half **to even** — see §4.2. **Read the score, the status and `rev_scorebreakdown` together in one read:** the breakdown must show the exact unrounded total *and* the rounded one, and its sentence about rounding UP must match the number stored |
| 🆕 **An EVEN number of "Not sure" answers is not rounded at all** | Two or four "Not sure" answers → whole total, and the breakdown says **"No rounding was applied — the total was already a whole number."** This is the `equals(Calculate_circumstance_score, Round_the_circumstance_score)` float-versus-int comparison; if Logic Apps does not coerce, a whole total would be wrongly told it had been rounded. **This is the one part of the rounding that could not be verified off-platform** |
| 🆕 **The status is derived from the number that is stored** | For every fractional case above, `rev_status` must be consistent with the **stored** `rev_circumstancescore` against the configured thresholds. Pre-0.8 the comparison read the unrounded total while the rounded one was written, so an exact 36.5 fell through to Auto-pass while the stored 37 sat inside the band — **a human review silently skipped on a record whose own score says it should have happened** |
| 🆕 **Life satisfaction `0` is a real answer, not a missing one** | Send `feeling_scale_answer: 0` with all ten wellbeing answers present → the application **scores** (it does **not** go to Under Review), and the life-satisfaction line contributes **10** points. This is the specific defect the Whole Number choice exists to prevent (§2.4.1) |
| 🆕 **Every value 0–10 inverts correctly** | Score eleven applications differing only in the life-satisfaction answer, 0 through 10 → contributions **10 down to 0**, one point apart, with no missing-key failure at any value. The old five-entry map would have failed at 6 and above |
| 🆕 **No trace of the deleted twelfth field** | Search the run's action outputs and the stored `rev_scorebreakdown` for `wellbeinganswer11` or a "Wellbeing answer 11" line → **zero hits**. A leftover reference is the one defect that would produce a wrong score silently rather than an error |
| 🆕 **Every one of the ten maps to the right question** | Populate the ten answers with ten *distinct* values (1,2,3,4,5,1,2,3,4,5) and confirm the breakdown's per-question lines match the export's column order: answers 1–7 are the SWEMWBS statements (cols 96–102), answers 8–10 are the "last year" questions (cols 103–105). **An off-by-one here is invisible in the total and wrong in the evidence a trustee reads** |
| **FR-012 inversion** | Two applications identical but for the life-satisfaction answer; answer `0` scores **10 more** than answer `10` (revision 0.3 — it was "4 more" against the old five-point scale) |
| **FR-014 boundaries** | Score exactly `KnockoutThreshold` → Auto-reject (at-or-below). Exactly `BorderlineBandLower` and exactly `BorderlineBandUpper` → Borderline. One above upper → Auto-pass. 🆕 **Run each boundary a second time reached by a FRACTIONAL total that rounds onto it** — 20.5 onto 21, 30.5 onto 31 — because a boundary reached by rounding is the case D-015 broke |
| **Misconfigured band** | Set `BorderlineBandLower` *below* `KnockoutThreshold`; a knocked-out score must still be Auto-reject, not Borderline |
| 🔄 **FR-022 — WIDENED IN REVISION 0.8 from absent to absent *or unusable*** | Omit one wellbeing answer → status **5 Under Review**, **`rev_circumstancescore` null**, breakdown naming the missing question number, Teams message. Then omit only the feeling answer — same outcome. 🆕 **Then the case the gate was widened for:** send an answer that is *present* but is **not a key of the configured map** (e.g. delete key `"6"` from `LikertPointMap` and submit a `6`, or send `feeling_scale_answer: 11`) → **the same withhold**, not a thrown run. The gate is *membership of the map*, not a hardcoded range, so it stays correct when the board changes the configuration — verify by changing the map rather than by changing the answer. **All eleven scored answers** are gated, the life-satisfaction one included: it had the identical hole |
| **FR-018 override** | Set `rev_statusoverridden = true`, re-run → **no write at all**; score, breakdown and status unchanged |
| **FR-017** | Change `KnockoutThreshold` in the app, re-run → new outcome with **no redeployment**. Confirm the change appears in the audit history of `rev_setting` |
| **FR-016** | An application with a narrative and condition profiles scores identically to one without. Verify the flow's action list references no special-category column — **and repeat it for the eight special-category columns added in revision 0.2**, including the two benefit columns. An application with benefits, care-cost explanations and an exceptional-funding narrative must score identically to one without |
| 🆕 **The financial cluster does not reach the score** | The eight financial columns are eligibility input, not score input (FR-015). Confirm the circumstance score is identical across applications differing only in the financial answers, and that only `rev_incomeband` moves `rev_incomeflag` |
| **FR-015** | Each income band against a fixed ceiling → flags 1 / 2. Band 6 *Prefer not to say* → flag **3**, and confirm the flag never alters the circumstance score |
| **FR-020** | Auto-rejected application absent from Active Applications, present in Auto-rejected Applications |
| Missing setting row | Delete `LikertPointMap` → flow fails, one `rev_errorlog` row, Teams alert, and the application is left **unscored at status Submitted** (fail-closed, NFR-018) |
| Idempotency | Re-run twice on an un-overridden row → same score, same status |

### 9.4 Daily Summary, Failure Alert, security

| Case | Assert |
|---|---|
| Summary counts | Windowed counts cover the window; **Borderline and Under Review counts are backlog, not windowed** — an application Borderline for three days appears in all three days' summaries |
| Monday window | Runs on a Monday → window reaches back three days |
| Summary content | The message contains **no** name, reference, score or narrative. Verify the run's action outputs hold none either — the queries select only `rev_applicationid` |
| Failure alert | Severity words map to option values 1–4; an unrecognised word → 3 *Error* |
| Failure of the failure handler | Break the Dataverse connection in the child flow → the Outlook fallback fires and the parent still completes |
| Truncation | Pass a 5000-character message → stored value ≤ ~2012 characters ending `[truncated]` |
| **C-TECH-040** | `verify-role-bindings.ps1`, plus query `systemuserroles_association` directly: **zero** direct user assignments of `REV Admin` or `REV Service Automation` |
| **NFR-001 column security** | A user with `REV Admin` reads `rev_fullname` and `rev_narrativeraw`. A user with **neither** role and no profile membership reads them as **null via the API, not just hidden in the UI** — the point of ADR-002 is that export and API cannot bypass it. **Repeat across all 34 secured columns**, not a sample: `verify-field-security-coverage.py` proves the two files agree, only a live read proves the platform honours it |
| 🆕 **`rev_breaklocation` is readable by a non-member** | The one personal-data-adjacent column deliberately left unsecured, because a trustee cannot judge a break without knowing where it is. A non-member must read it **successfully**. If it comes back null, someone has added it to the profile and the exemption in `verify-field-security-coverage.py` was overridden |
| 🆕 **Calculated columns and column security together** | Read `rev_fullname` as a non-member → null. Then read `rev_firstname` as a non-member → also null. **Securing the calculated column while leaving its sources readable would be security theatre**, and this test is what proves it was not done |
| **C-DOM-010/011 auditing** | Create, update and delete a row on each of the four tables; confirm the audit record carries timestamp (UTC), actor, action, record ID and before/after values. Confirm organisation audit retention reads 2192 days |
| Retention jobs | All four exist, are recurring monthly, and their queries are status-plus-date — **never unfiltered**. Do not let a retention test run against seeded fixtures without a snapshot |
| **Orphan sweep** | Create an applicant with one application; delete the application; run the orphan job → the applicant row is deleted. This is TAD risk A-R10, found during architecture and covered by no source document |
| Idempotency of every script | Run each `post_deploy` script twice → the second run reports `EXISTS` for every resource and exits 0 (C-TECH-042) |
| `seed-settings.ps1` fail-fast | Run with `-Env prd` while `{{PENDING_OQ_001}}` remains → aborts **before any write**, non-zero exit, and `rev_setting` is untouched |

### 9.5 No measurable target exists for four categories

NFR-022 (performance), NFR-023 (availability), NFR-024 (accessibility — WCAG 2.1 AA is *derived* in
ADR-020, not confirmed) and NFR-025 (SAR/erasure turnaround) have no threshold in any source. Record
them as untestable rather than inventing a number. The accessibility criteria in the form
specification are written as testable acceptance criteria, but the standard itself still needs
confirming (SDD OQ-022).

### 9.6 The automated suite, and the invariant list it is measured against

*Introduced in revision 0.6; extended in 0.7 and 0.8; **rows marked 🔄 corrected and rows marked 🆕
added in revision 0.9** (D-017 — three rows had gone stale against the build they claim to
describe).*

`coding-standards.md` → Test Coverage sets a percentage for imperative code and, for declarative
artefacts, replaces the percentage with **completeness against an enumerated list of invariants**.
This is that list. Each row is an asserted, re-runnable test — not a paragraph, and not something
re-verified by inspection each release.

Run the suite: `pwsh -NoProfile -File src/tests/Invoke-Tests.ps1` (add
`-CodeCoverage -CoverageThreshold 80` for the gate the build enforces).

> **⚠️ THIS LIST IS LOAD-BEARING FOR test-agent, WHICH IS WHY REVISION 0.9 AUDITED IT RATHER THAN
> APPENDING TO IT.** `agents/test-agent.md` directs that agent to load §9 on activation, so a stale
> row here does not merely mislead — it gets asserted. D-017 was exactly that: this list still gave
> the reachable floor as 10 against a build whose floor is 5, so a tester following it literally
> would have **failed a correct build** and, worse, might have "fixed" the build to match. Where the
> suite and this list disagreed, **the suite was right every time.** The rule that follows: when a
> revision changes scoring behaviour, this list is part of the change, not documentation of it.

| Invariant | Requirement | Where asserted |
|---|---|---|
| `FeelingScaleInversion` satisfies `key + value = 10` for all 11 keys; keyed 0–10 with no gap; monotonically decreasing; applied as a map lookup, not `sub(10, x)` | FR-012, FR-017 | `solutions/ScoringInvariants.Tests.ps1` |
| 🔄 `LikertPointMap` covers every `rev_likertresponse` option value **and every `rev_agreementresponse` option value — ONE map serves BOTH scales** — and only those; position 1 → 5 points; monotonically decreasing across ordinal positions **1–5 only**; **value 6 ("Not sure") = exactly 0.5**, asserted separately because it is outside the ordinal ladder; **0.5 is the ONLY non-integer value in the map** | FR-013 | same |
| 🔄 `MaxCircumstanceScore` **reconciles** to `10 × max(Likert) + max(Inversion)` = 60; **the minimum reachable score is 5** (ten "Not sure" at 0.5 plus a zero inversion) — **not 10, which is what this row said until revision 0.9 and what a tester following it would have wrongly asserted (D-017)**; the TST/ACC threshold and band sit inside that range with the lower bound above the knockout | FR-011, FR-014 | same |
| 🆕 The two wellbeing scales have **identical value sets and different labels for positions 1–5, and the same label for 6** — the property that makes one shared point map correct rather than convenient; `rev_wellbeinganswer1–7` bind to `rev_likertresponse` and `8–10` to `rev_agreementresponse`; `rev_agreementresponse` is declared a solution root component, or it ships with no options | FR-013, D-014 | same |
| 🆕 The configuration **reproduces all 25 hand-scored applications** in `docs/Import/Book(Sheet1).csv` exactly, resolving labels from the option-set XML and points from the settings row — so the ground truth is a standing assertion, not a one-off analysis; the three competing scale directions are shown **not** to reconstruct | FR-011, FR-013, OQ-002 | same |
| 🆕 **The rounding is round-half-up, EXECUTED rather than described** — `Round_the_circumstance_score` applies an offset strictly inside `(0, 0.5)` before `formatNumber`, so the formatter is never handed a midpoint; .NET's own `F0` formatting is then run, through the offset **read out of the shipped expression**, over all **121** reachable totals (0–60 in halves) and must give half-up on every one, with 20.5→21, 30.5→31 and 37.5→38 named individually; the offset is exact in binary floating point; the offset is asserted to be smaller than the smallest point value | FR-011, FR-014, **D-015** | same |
| 🆕 The rounding happens **once**, and the **same rounded number** is written to `rev_circumstancescore` and read by `Derive_status`; the exact unrounded total survives in `rev_scorebreakdown`; the expression's description records the *executed* rounding behaviour rather than the false claim it carried before revision 0.9 | FR-011, FR-014, **D-015** | same |
| `IncomeBandUpperBoundMap` covers every income band, carries `-1` for "prefer not to say", is monotonically increasing, and the flag chain reads **only** `rev_incomeband` — no benefit or other financial column | FR-015 | same |
| `AgeBandMap` / `PostcodeRegionMap` cannot produce an out-of-range option value; boundaries increase; the top age band is open-ended; no postcode prefix appears in two regions | FR-027 | same |
| The scoring flow's **executable** definition references **none of the 34 secured columns** — derived from `IsSecured=1` in the entity XML, so a newly secured column is covered without updating a list — and none of the twelve special-category names, in any position (broader than the build gate, which only catches the `body/` access form) | FR-016 (HARD) | same |
| All eight `rev_setting` rows read at run time by alternate key; no threshold literal anywhere; the only bare integers in `Derive_status` are `rev_applicationstatus` option values | FR-017, NFR-019 | same |
| Knockout is evaluated **before** the band | FR-014 | same |
| The override guard is the **first** action, coalesces a null override to false, and its only child is a `Terminate` — no path to a write | FR-018 | same |
| 🔄 All ten wellbeing answers plus the life-satisfaction answer can withhold the outcome; the zero-versus-null discrimination is `empty(coalesce(string(x), ''))`; the withhold branch writes **no** `rev_circumstancescore` and terminates. **WIDENED IN REVISION 0.8, and this row described only the pre-0.8 half until revision 0.9 (D-017):** the gate withholds for an answer that is **present but not a key of the configured map** as well as for an absent one — both maps, all eleven answers — and both maps are asserted to be parsed **before** the gate without moving any scoring earlier | FR-022, D-014 | same |
| The Borderline notification carries reference and score but no identity column; no expression anywhere reads an applicant identity column | C-DOM-004 | same |
| The intake trigger's `required` array is exactly the **four** fields the live form always collects (revision 0.7 — was six); the guard, the 400 body and the log line name the same four and do **not** name `email` or `date_of_birth`; both are nonetheless still accepted; `age_range` is accepted and typed; 82 schema properties; none of the eleven scored answers is required; the **ten** removed contract fields — including `group_linkage`/`rev_grouplinkage` — are absent from the **executable** definition | FR-007, payload contract | `solutions/IntakeContract.Tests.ps1` |
| The age band is derived from the label the form sends **before** any date-of-birth fallback (asserted by expression position), falls back to option 9 rather than guessing, and neither `rev_dateofbirth` nor `rev_email` can throw on an absent value; the applicant lookup matches on name + postcode when no email was collected | FR-027, payload contract, D-003 | same |
| The solution source records the exact trigger-authentication value, names both provisioning scripts, cites the Microsoft doc, and states ADR-011 is still open; the Authorization header is **not** surfaced into outputs | C-TECH-006 (HARD), NFR-008 | same |
| **The flow's 401 body and the smoke test's discriminator agree** — the coupling that makes D-001 detectable | C-TECH-006 | same |
| The caller gate is the first action, writes nothing on the rejection path, and reveals nothing about the schema or tenant | NFR-008 | same |
| The replay guard queries the alternate key before any write; the flow does not set `rev_name` | TAD §5.1, FR-008 | same |
| Every OData `$filter` that interpolates user input escapes it by **doubling** the quote — all four interpolated values | C-TECH-005 (HARD) | same |
| 🔄 **All 22** provisioning scripts (the suite discovers them, so the figure follows the folder rather than this row): parse; mandatory `-Env` with the four-value `ValidateSet`; dot-source the shared contract; `#Requires 7.0`; StrictMode; end with `Exit-Provisioning`; report all three statuses; no work-in-progress marker; no hardcoded environment URL or secret | C-TECH-042, C-TECH-047, C-TECH-011, C-TECH-001 | `provisioning/ScriptContract.Tests.ps1` |
| `verify-*` scripts invoke no mutating Graph/PnP/PowerApps command and issue no non-GET Dataverse call | C-TECH-042 | same |
| Every settings path a Phase 1 script reads exists in **both** settings files | C-TECH-047 | same |
| 🔄 `allowedDirectRoleAssignments` is empty; audit retention is 2192 days and never `-1`; the four audited tables; **both environments declare the same eleven `rev_setting` keys and the seven policy rows** (was "six" here until revision 0.9 — `AgeRangeLabelMap` joined them in 0.7) **are byte-identical across environments**; PRD withholds the board criteria behind pending tokens; permission GUIDs remain placeholders | C-TECH-040, C-DOM-010/011/013, NFR-019, C-TECH-043 | `provisioning/DeploymentSettings.Tests.ps1` |
| The intake trigger-auth declaration: mode is the narrowest option and never *Anyone*, identical in both environments; exact audience and double-slash scope; `oid` in the required claims; **the control has a named owner** | C-TECH-006 | same |

**What the suite deliberately does not claim.** Nothing above executes a flow, enforces column
security or produces an audit record. Every case in test-agent's §8 deferred list stays deferred
and unchanged. The suite makes the *static* properties regression-proof; it does not make the
release environment-tested.

**One precise exception, added in revision 0.9, and worth stating narrowly rather than letting it
inflate.** The rounding invariant is the only row that *executes* anything. It does not execute the
flow — it executes **.NET's own `F0` number formatting**, which is the primitive the Logic Apps
`formatNumber` function calls, applied to the offset read out of the shipped expression. So it
proves the arithmetic of the rounding rule on this runtime, and it proves the expression cannot
present the formatter with a midpoint on **any** runtime. It does **not** prove that Power Automate's
`formatNumber` binds to that primitive as expected, nor which numeric type the runtime uses — the
fix was chosen to be correct under both, and the live case in §9.3 is what closes the gap. This
distinction is the whole lesson of D-015: *reasoned about* and *executed* are different claims, and
the difference was an applicant being auto-rejected.

---

---

## 10. Constraint check — re-run after revision 0.9

Applied `skills/how-to-apply-constraints.md`. Scope extracted mechanically from the constraint files
(rows whose `Scope` column names **development-agent**) rather than read by eye — same script, same
result as revision 0.8: **6 domain HARD, 1 domain SOFT (out of declared severity scope, listed for
completeness), 17 tech HARD, 6 tech SOFT**.

```
CONSTRAINT CHECK
Domain   HARD: 6 / 6   |  violations: NONE
Domain   SOFT: 1       |  warnings:   NONE  (C-DOM-031 is an unreplaced [PLACEHOLDER] row — not evaluable)
Tech     HARD: 17 / 17 |  violations: NONE
Tech     SOFT: 6       |  warnings:   C-TECH-013
  C-TECH-013: `DEFERRED_call_duplicate_grant_check` in the intake flow is a Compose that writes
              nothing. Carried forward unchanged from revisions 0.1–0.8 and reported honestly: it
              marks the FR-023 call site so Automation #7's insertion point is unambiguous rather
              than rediscovered. NOT introduced or widened by revision 0.9 — the intake flow was
              not edited at all in this revision.

Overall: WARN  (one SOFT warning, unchanged since revision 0.4.)
```

### 10.0 What revision 0.9 could have moved, re-verified rather than assumed

Revision 0.9 edited **one expression and its description** in the scoring flow, **one comment** in
`Other/Solution.xml`, **one row description** in both settings files (no value changed), **one test
file** (+17 assertions), **one test harness** (+2 functions) and this document — then repacked both
zips. **Six** constraints could plausibly have moved.

| Constraint | Why this revision could have moved it | Re-verified |
|---|---|---|
| **C-TECH-004** (HARD — all user inputs validated and sanitised before processing or persistence) | **This revision changes how a validated input is turned into a decision about a person.** If any constraint is implicated by D-015, it is this one | **PASS, and materially better than before.** Nothing about validation was weakened: the trigger bounds added in revision 0.8 (`wellbeing_answer_*` 1–6, `feeling_scale_answer` 0–10) are untouched, the FR-022 withhold gate is untouched, and the `required` array is still four fields. What changed is **downstream correctness**: a valid, in-range, fully answered submission whose total lands on a midpoint now produces the outcome the approved rule specifies instead of one that depended on whether the whole part happened to be even. Asserted by 17 new tests, mutation-tested to confirm they fail against the old expression |
| **C-DOM-004** (HARD — no personal data in application logs) | **A long new description was added to an action inside the scoring flow, and descriptions ship inside the solution** | **PASS.** Re-derived rather than eyeballed: stripping every `description` from the definition and searching the executable remainder for the nine applicant-identity column names returns **NONE** (assertion passes unchanged). The new description text names option values, point values, thresholds, .NET method names and defect IDs — **no name, no narrative, no condition, no applicant-specific value of any kind.** `Compose_score_breakdown`'s emitted text was **not changed**: its "halves are rounded UP" sentence needed no edit because it is now *true*, which was the point of fixing the code rather than the sentence |
| **C-TECH-001** (HARD — no hardcoded secrets in version control) | One flow definition, two settings files, one solution file, two test files and one document changed | **PASS.** Executed exactly as the build config specifies — `gitleaks detect --source . --no-git --no-banner --redact --exit-code 1` → **3.17 MB scanned, no leaks found, exit 0.** No credential, key or token was added; the largest additions are prose and test assertions |
| **C-TECH-031 / C-TECH-047** (HARD — no environment-specific value in the artifact) | **Both settings files were edited**, and the solution was repacked | **PASS.** The edit is a **description only** — `LikertPointMap`'s value is unchanged and still byte-identical across TST/ACC and PRD (re-asserted by `DeploymentSettings.Tests.ps1`, and checked directly: both descriptions are identical too). No URL, GUID, tenant name or environment identifier was introduced. The build's own gate re-run clean: no environment URL, SPO URL or tenant UPN anywhere in the solution source. **The new `20` and `30` in the flow description are prose naming the TST/ACC values as illustration, not configuration** — the `no-hardcoded-thresholds` gate (a threshold key adjacent to a numeric literal) re-runs PASS, and `Derive_status` still reads all three thresholds from `rev_setting` rows |
| **C-TECH-020** (HARD — dependencies pinned to exact versions) | Two new harness functions and 17 new assertions | **PASS.** **No dependency was added.** The new helpers use only built-in PowerShell and `System.Globalization.CultureInfo`/`Double.ToString` from the base class library. Pester is still pinned at **5.7.1** in both `build.yml` and `Invoke-Tests.ps1`; the `pac` 2.4.1 and `yq` v4.44.3 pins are untouched |
| **C-TECH-011** *(SOFT)* — no `TODO`/`FIXME`/`HACK` in delivered code | A long new description and ~130 lines of new test code | **PASS.** `grep -rniE '\b(TODO\|FIXME\|HACK)\b'` across `src/solutions`, `src/tests`, `scripts`, `provisioning`, `config` and `.github` returns nothing |

**One judgement recorded rather than hidden, in the spirit of C-TECH-013.** `Get-RoundingOffset`
contains a branch that returns `0.0` for the **pre-0.9 expression form** — a shape the shipped flow no
longer has. That is not dead code by accident: it is what makes the mutation test meaningful, because
a parser that *threw* on the old form would fail for the wrong reason and prove nothing about the
rounding. The branch carries a comment saying so.

**Constraints this revision did not touch.** No security role, field security profile, connector,
privilege, retention rule, provisioning script, option set, entity, intake flow or Code App was
modified — so C-DOM-003, C-DOM-010, C-DOM-011, C-DOM-020, C-DOM-021, C-TECH-002, C-TECH-003,
C-TECH-005, C-TECH-006, C-TECH-007, C-TECH-040 to C-TECH-046 and C-TECH-048 stand exactly as
revisions 0.6 to 0.8 verified them. Re-asserting them on the strength of this document is the move
revision 0.6's own §10.0 warned against. **C-TECH-006 remains PASS-at-this-scope with its caveat
intact** — provisioned, owned and verifiable, not verified, because no environment exists.

**What is NOT a constraint violation but is still the thing to read hardest.** The **rounding rule
remains a judgement call**, unchanged and still the reviewer's to confirm or override. Revision 0.9
did not re-decide it; it made the code implement it. If the reviewer prefers a decimal
`rev_circumstancescore` and exact storage, **the D-015 fix is still required in the meantime**,
because the pre-0.9 code implemented *neither* option.

### 10.0.0 Previous check — revision 0.8 (retained for the record)

Scope identical: **6 domain HARD, 1 domain SOFT (out of declared severity scope), 17 tech HARD,
6 tech SOFT**.

```
CONSTRAINT CHECK
Domain   HARD: 6 / 6   |  violations: NONE
Domain   SOFT: 1       |  warnings:   NONE  (C-DOM-031 is an unreplaced [PLACEHOLDER] row — not evaluable)
Tech     HARD: 17 / 17 |  violations: NONE
Tech     SOFT: 6       |  warnings:   C-TECH-013
  C-TECH-013: `DEFERRED_call_duplicate_grant_check` in the intake flow is a Compose that writes
              nothing. Carried forward unchanged from revisions 0.1–0.7 and reported honestly: it
              marks the FR-023 call site so Automation #7's insertion point is unambiguous rather
              than rediscovered. NOT introduced or widened by revision 0.8 — the intake flow was
              edited only in its trigger schema (eleven properties bounded) and this action was
              not touched.

Overall: WARN  (one SOFT warning, unchanged since revision 0.4.)
```

#### What revision 0.8 could have moved, re-verified rather than assumed

Revision 0.8 edited two option sets (one new), one `Entity.xml`, `Other/Solution.xml`, two flow
definitions, two settings files, one build config, one test file, one test harness and three
documents. **Seven** constraints could plausibly have moved.

| Constraint | Why this revision could have moved it | Re-verified |
|---|---|---|
| **C-TECH-001** (HARD — no hardcoded secrets in version control) | **This revision is the one that fixes the gate itself (D-006)**, so the gate's own result deserves more than a glance | **PASS, and now reproducibly.** Executed exactly as the config now specifies it — `gitleaks detect --source . --no-git --no-banner --redact --exit-code 1` → ≈3.06 MB scanned, **no leaks found, exit 0** (the byte figure drifts by a few KB between runs because these documents are themselves inside the scan scope; the load-bearing part is *no leaks* and *exit 0*). Before this revision the config omitted `--no-git`, so it scanned commit history rather than the working tree that `pac solution pack` reads; the recorded PASSes had rested on a human re-running it correctly. **No new secret entered the release** — the diff is option sets, entity XML, flow definitions, settings reference data, a build config, tests and documents |
| **C-TECH-004** (HARD — all user inputs validated and sanitised before processing or persistence) | **This is the constraint the whole revision is about.** The retest recorded it as *"PASS — with a range-validation gap recorded as D-014"* | **PASS, and the recorded gap is closed.** All ten `wellbeing_answer_*` trigger properties are now bounded `minimum: 1, maximum: 6` and `feeling_scale_answer` `0`–`10`; there were **no bounds at all** before. Crucially, bounds alone would not have been enough: the FR-022 withhold gate is also widened from *absent* to *absent **or** not a key of the configuration map*, on **all eleven** scored answers, so a value that is storable but unscoreable now routes to a human instead of throwing. The `required` array is still four fields and the property count still **82** — both asserted — so nothing became newly rejectable, which matters because rejecting at the boundary is what FR-010 exists to prevent |
| **C-DOM-004** (HARD — no personal data in application logs) | **Both the score breakdown text and the withhold branch's diagnostic text were rewritten**, and the breakdown is written to a stored column and quoted to a Teams recipient | **PASS.** Re-derived rather than eyeballed: stripping every `description` from the definition and searching the executable remainder for the nine applicant-identity column names returns **NONE**. The new breakdown lines carry question numbers, option values, point values, the exact and rounded totals and the thresholds in force — no name, no narrative, no condition. The new "Life-satisfaction answer scoreable: NO…" line names no value, only that the supplied value is unrecognised. Two existing C-DOM-004 assertions pass unchanged |
| **C-DOM-011** (HARD — audit records include timestamp, actor, action, entity, before/after) | **A new column binding and a new option set change what is audited** | **PASS.** `rev_agreementresponse` is a global option set, not a column; the three rebound attributes keep `IsAuditEnabled=1`, and Dataverse audits the stored option value with before/after regardless of which option set labels it. No attribute lost auditing and none was added without it — `field-security-coverage` still reports **34 secured columns** with 1 reviewed exemption |
| **C-TECH-031 / C-TECH-047** (HARD — no environment-specific value in the artifact) | **Both settings files were edited and a new option set shipped** | **PASS.** The only settings change is `LikertPointMap` gaining `"6":0.5` — reference data, byte-identical across TST/ACC and PRD, containing no URL, GUID, tenant name or environment identifier. The new option set contains labels only. The build's own gate re-run clean: no environment URL, SPO URL or tenant UPN anywhere in the solution source |
| **C-TECH-020** (HARD — dependencies pinned to exact versions) | ~250 lines of new test code and three new harness functions | **PASS.** No dependency was added. Pester is still pinned at **5.7.1** in both `build.yml` and `Invoke-Tests.ps1`; `pac` 2.4.1 and `yq` v4.44.3 pins are untouched. The new tests use only built-in PowerShell and `System.Text.Encoding` |
| **C-TECH-011** *(SOFT)* — no `TODO`/`FIXME`/`HACK` in delivered code | A new option set, ~250 lines of new test code and extensive new descriptions | **PASS.** `grep -rniE '\b(TODO\|FIXME\|HACK)\b'` across `src/solutions`, `src/tests`, `scripts`, `provisioning`, `config` and `.github` returns nothing |

**Constraints this revision did not touch.** No security role, field security profile, connector,
privilege, retention rule, provisioning script or Code App was modified — so C-DOM-003, C-DOM-010,
C-DOM-020, C-DOM-021, C-TECH-002, C-TECH-003, C-TECH-006, C-TECH-040 to C-TECH-046 and C-TECH-048
stand exactly as revision 0.6 and 0.7 verified them, and re-asserting them on the strength of this
document is the move revision 0.6's own §10.0 warned against. **C-TECH-006 remains
PASS-at-this-scope with its caveat intact** — provisioned, owned and verifiable, not verified,
because no environment exists.

**One thing that is NOT a constraint violation but should not be mistaken for clean.** The
**rounding rule is a judgement call this agent took**, not a derived fact — see the revision 0.8
banner. No constraint governs it, so nothing fails; but "no violation" is not "nothing to decide",
and it is the item most worth the reviewer's attention in this revision. The two items revision 0.7
raised in the same spirit (≈30 unmapped form columns, five mismatched option sets) are **unchanged
and still open** — revision 0.8 corrected the two option sets it had ground-truth evidence for and
deliberately left the other five alone.

### 10.0.1 Previous check — revision 0.7 (retained for the record)

Scope identical: **6 domain HARD, 1 domain SOFT (out of declared severity scope), 17 tech HARD,
6 tech SOFT**.

```
CONSTRAINT CHECK
Domain   HARD: 6 / 6   |  violations: NONE
Domain   SOFT: 1       |  warnings:   NONE  (C-DOM-031 is an unreplaced [PLACEHOLDER] row — not evaluable)
Tech     HARD: 17 / 17 |  violations: NONE
Tech     SOFT: 6       |  warnings:   C-TECH-013
  C-TECH-013: `DEFERRED_call_duplicate_grant_check` in the intake flow is a Compose that writes
              nothing. Carried forward unchanged from revisions 0.1–0.6 and reported honestly: it
              marks the FR-023 call site so Automation #7's insertion point is unambiguous rather
              than rediscovered. NOT introduced or widened by revision 0.7 — the flow was edited in
              six places and this action was not one of them.

Overall: WARN  (one SOFT warning, unchanged since revision 0.4.)
```

#### What revision 0.7 could have moved, re-verified rather than assumed

Revision 0.7 edited one flow definition, two settings files, one pipeline config, two test files and
three documents. Six constraints could plausibly have moved.

| Constraint | Why this revision could have moved it | Re-verified |
|---|---|---|
| **C-TECH-004** (HARD — all user inputs validated and sanitised before processing or persistence) | **The required-field list was shortened.** This is the one that looks like a violation and is the one to read carefully | **PASS.** Requiring a field the source never sends is not validation; it is rejection of valid input, and the outcome is the one FR-010 exists to prevent. What was actually verified: the typed trigger schema is unchanged at **82 properties**; the completeness check still runs **before any Dataverse write**; `rev_feelingscaleanswer` is still platform-bounded 0–10 and the eight typed financial columns still cannot hold a paragraph; and the revision **added** two null-guards on writes that would otherwise have thrown once the fields became optional. Validation is more accurate and strictly more defensive than before. Asserted by 10 new tests |
| **C-TECH-005** (HARD — no string concatenation in data-store operations) | **An OData `$filter` was rewritten into two branches, and a third user value (`postcode`) is now interpolated** | **PASS, caveat unchanged.** The new branch escapes by doubling — `replace(trim(coalesce(triggerBody()?['postcode'], '')), '''', '''''')` — the same platform-correct OData literal escaping as the existing three values. The existing test walks **every** `$filter` in the parsed definition rather than a named list, asserts each interpolating filter contains `replace(`, asserts the replacement is six consecutive quote characters (doubling, not stripping), and passes unmodified against the rewrite. Caveat carried forward: the connector exposes no parameter binding, so escaping is the available control |
| **C-DOM-004** (HARD — no personal data in application logs) | **The incomplete-payload log message was reworded** | **PASS.** The message names **field names only** — "one or more of submission_id, first_name, last_name, postcode was absent or empty" — and the only interpolated value in the whole log body is `coalesce(triggerBody()?['submission_id'], 'no-submission-id')`, which is a Gravity Forms entry id, not personal data. The 400 response body likewise carries field names only. `rev_errorlog` still has no column able to hold personal data. Re-read the full `Log_incomplete_payload` body rather than the diff |
| **C-TECH-031 / C-TECH-047** (HARD — no environment-specific value in the artifact) | **A `rev_setting` row was added to both settings files** | **PASS.** `AgeRangeLabelMap` is reference data — eight of the live form's own label strings mapped to option values — with **no** URL, GUID, tenant name or environment identifier in it, and it is byte-identical across TST/ACC and PRD. No `<defaultvalue>` was added to any environment variable. The settings tests that assert every environment URL and Entra object ID is still a `{{PLACEHOLDER}}` token pass unchanged |
| **C-TECH-001** (HARD — no hardcoded secrets in version control) | A flow definition, two settings files and two test files changed | **PASS.** `gitleaks detect --no-git --redact` over the working tree: **2.80 MB scanned, no leaks found** |
| **C-TECH-011** *(SOFT)* — no `TODO`/`FIXME`/`HACK` in delivered code | New action names, new descriptions and ~90 lines of new test code | **PASS.** `grep -rniE '\b(TODO\|FIXME\|HACK)\b'` across `src/solutions`, `src/tests`, `scripts`, `provisioning`, `config` and `.github` returns nothing |

**Constraints this revision did not touch, and why the answer is short.** No Entity.xml, no option set,
no security role, no field security profile, no connector, no privilege, no retention rule, no
provisioning script and no Code App were modified — so C-DOM-003, C-DOM-010, C-DOM-011, C-DOM-020,
C-DOM-021, C-TECH-002, C-TECH-003, C-TECH-006, C-TECH-020, C-TECH-040 to C-TECH-046 and C-TECH-048 all
stand exactly as revision 0.6 verified them, and re-asserting them here on the strength of this
document is precisely the move revision 0.6's own §10.0 warned against. The one thing worth restating:
**C-TECH-006 remains PASS-at-this-scope with revision 0.6's caveat intact** — the control is
provisioned, owned and verifiable, not verified, because no environment exists. Revision 0.7 changed
nothing about it.

**Two things that are NOT constraint violations but that a reviewer should not mistake for clean:**

1. **Roughly 30 of the live form's 139 answer columns have no destination** (spec §9, M-09), including
   the ten care-type checkboxes and the hours of care provided per week. No constraint requires a
   column to exist for every question a third party's form asks, so nothing fails — but "no violation"
   is not "nothing to decide".
2. **Five committed option sets do not match what the live form sends** (spec §9, M-01/M-05/M-07). Again
   no constraint covers it. The condition-profile mismatch is the one with teeth, because that data is
   shown to trustees and reported to funders.

### 10.0.2 Previous check — revision 0.6 (retained for the record)

#### Constraint check — re-run after revision 0.6

Applied `skills/how-to-apply-constraints.md`. Scope is unchanged: the constraints naming
**development-agent** in their `Scope` column — **6 domain HARD, 1 domain SOFT (out of declared
severity scope, listed for completeness), 17 tech HARD, 6 tech SOFT**.

```
CONSTRAINT CHECK
Domain   HARD: 6 / 6   |  violations: NONE
Domain   SOFT: 1       |  warnings:   NONE  (C-DOM-031 is an unreplaced [PLACEHOLDER] row — not evaluable)
Tech     HARD: 17 / 17 |  violations: NONE
Tech     SOFT: 6       |  warnings:   C-TECH-013
  C-TECH-013: `DEFERRED_call_duplicate_grant_check` in the intake flow is a Compose that writes
              nothing. Carried forward unchanged from revisions 0.1–0.5 and reported honestly: it
              marks the FR-023 call site so Automation #7's insertion point is unambiguous rather
              than rediscovered. NOT introduced or widened by revision 0.6.

Overall: WARN  (one SOFT warning, unchanged since revision 0.4.)
```

##### What moved in revision 0.6, and what was out of that agent's scope

**C-TECH-006 (HARD) — was the FAIL that blocked the test run. Now PASS at this scope.** The
constraint's `Verify By` is "Security test: unauthenticated request → 401/403". Test-agent
recorded that test as existing nowhere. It now exists, is executable, is wired as a
deployment-halting smoke test on both target environments, and additionally discriminates a
platform-level rejection from the definition's own — which is the part D-001 was actually about.
**Honest caveat, because a document asserting a security property is what got us here:** the test
cannot be *executed* until an environment exists, so what this fix delivers is a control that is
provisioned, owned and verifiable rather than one that is verified. Test-agent is the final
verifier and will make its own call.

**C-TECH-014 (HARD) is NOT in development-agent's scope filter** — its `Scope` column reads
`test-agent, build-agent`. It is fixed here because the reviewer asked for it and because
development-agent owns both artefacts it needs (`coding-standards.md` has no other owner in this
session, and `config/<slug>-build.yml` is this agent's output). It is deliberately **not** counted
in the block above, because inflating a scope filter to claim a pass is the same class of error as
asserting a control from a document. The evidence for it is in §9.6 and the revision 0.6 banner;
test-agent and build-agent evaluate it at their own gates.

**Constraints this revision could plausibly have moved, re-verified mechanically rather than
assumed:**

| Constraint | Why revision 0.6 could have moved it | Re-verified |
|---|---|---|
| **C-TECH-001** (HARD — no hardcoded secrets) | A new authentication flow, two new scripts, a new settings block and ~4,000 lines of test code | `gitleaks detect --no-git --redact` over the working tree: **2.75 MB scanned, no leaks found**. The endpoint URL — which *is* a credential, because of its SAS `sig=` — is referenced by environment-variable **name** in both settings files and never by value; a settings test asserts no file contains a JWT or a `sig=` value. `ensure-intake-client.ps1` reports credential counts only, asserted by a test that plants a fake `SecretText` and requires it not to appear in the output. **PASS** |
| **C-TECH-002** (HARD — secrets from the approved store) | The OAuth route is now the default | Unchanged and still vacuous in the right direction: **this release uses no runtime secret**. The client ID is a public identifier and is correct as a plain environment variable *because* it is no longer the primary control. Alex's client credential is out-of-band and out-of-repository. ⚠ Conditional note carried forward: if ADR-011 lands on the shared-secret route, a Key Vault-backed secret environment variable becomes mandatory and Key Vault is out-of-palette. **PASS** |
| **C-TECH-003** (HARD — TLS 1.2+) | A new outbound HTTP call was introduced | The smoke test asserts the endpoint scheme is `https` and **FAILS** on `http`, verified by a test that feeds it an `http://` URL. **PASS** |
| **C-TECH-005** (HARD — no string concatenation in data-store operations) | New Graph filters in `ensure-intake-client.ps1` | The display-name filter routes through `ConvertTo-ODataLiteral`, and a test asserts a quote is doubled. The intake flow's four interpolated `$filter` values are now asserted individually rather than reviewed. **PASS with the caveat carried forward unchanged** — the connector exposes no parameter binding, so escaping is the available control |
| **C-TECH-006** (HARD — authentication on non-public routes) | The subject of Fix 1 | See above. **PASS at this scope** |
| **C-TECH-007** (HARD — Tier 3+ synthetic outside PRD) | The smoke test POSTs to a live endpoint, and the test suite writes a fixture | The probe payload carries a synthetic `submission_id` and **nothing else** — asserted by a test that counts the payload's properties. The settings fixture is written to `acc-settings.json` (documented as never used for this feature), refuses to overwrite an existing file, is removed in `AfterAll` and is now gitignored. **PASS** |
| **C-TECH-020** (HARD — dependencies pinned) | Pester is a new dependency | Pinned to **5.7.1** in both `src/tests/Invoke-Tests.ps1` and the build step, and the runner **refuses to run** on any other version rather than silently using whatever is installed. Pester 6.1.0 is also present locally and is deliberately not used. **PASS** |
| **C-TECH-031 / C-TECH-047** (HARD — no environment-specific value in the artifact) | A new settings block and a new flow parameter description | No `<defaultvalue>` added; the new `intake` block holds environment-variable **names**, not URLs; the trigger URL is a CI secret. A test asserts every environment URL and Entra group object ID in both settings files is still a `{{PLACEHOLDER}}` token, and the contract suite greps every script's non-comment lines for an environment URL. **PASS — and now enforced by a test rather than by a reviewer's eye** |
| **C-TECH-041** (HARD — tenant operations behind a gate) | Two new tenant-level operations | Both `ensure-intake-client.ps1` runs sit inside the existing `tenant_prerequisites` block behind `APPROVE TENANT`, and the script prints the values for the Deployment Summary. **PASS** |
| **C-TECH-042** (HARD — idempotent, check-before-create, three-state reporting) | Two new scripts | Both follow the contract; `verify-intake-endpoint-auth.ps1` is read-only in effect and its header explains why every outcome of its POST writes nothing. The contract is now **asserted from the AST for all 20 scripts**, so this constraint moved from "PASS (source review)" to "PASS (enforced)". **PASS** |
| **C-TECH-043** (HARD — least-privilege API permissions) | One new API permission | The intake caller receives exactly one: Microsoft Flow Service `User`, the narrowest permission that lets Entra issue a token for the Power Automate audience. No `*.ReadWrite.All`, no `Directory.*`. The GUID stays a `{{PLACEHOLDER}}` so no permission is granted that nobody looked up — asserted by a test across every registration. **PASS** |
| **C-TECH-044** *(SOFT)* | The intake caller needs a credential | **Remains CLOSED for the delivery path**: no client secret anywhere in the pipeline. The one credential this fix implies belongs to Alex's site, is out-of-band, and the script records a preference for a certificate and reports the posture. Not a new warning |
| **C-TECH-045 / C-TECH-046 / C-TECH-048** (HARD) | Could have been touched by a flow edit | No connector added (the Request/HTTP trigger was already in the TAD §6.4 business group); no role file touched, both still custom `REV`-prefixed with 40 and 33 privileges; no Code App exists and no token-acquisition code was added. **PASS** |

**Domain HARD constraints — all six re-verified; none design-affected by this revision:**

| Constraint | Re-verified |
|---|---|
| **C-DOM-003** (retention defined and automated) | No retention rule changed. The four bulk-delete jobs are now **behaviourally tested**, including that they use relative date operators (an absolute cut-off would freeze a recurring job) and that the orphan sweep's LEFT OUTER join and aliased null test are correct — a defect there would have silently deleted nothing. **PASS, better evidenced** |
| **C-DOM-004** (no personal data in logs) | No logging path changed. Added: an asserted test that no expression in the scoring flow reads an applicant identity column and that the Borderline notification carries reference and score only. The smoke-test probe carries no personal data. **PASS** |
| **C-DOM-010 / C-DOM-011** (audit logging and its record shape) | No `Entity.xml` was modified. `ensure-auditing.ps1` is now tested at 100%: retention 2192 days from settings, `MSCRM.MergeLabels` present, and `IsAuditEnabled` read from `.Value` rather than the wrapper. ⚠ **Test-agent defect D-007 stands uncorrected**: the "122 `IsAuditEnabled` columns" figure elsewhere in this document is an attribute count, and the correct figure is **118 audit-enabled of 120 attributes**. Out of scope for this cycle; flagged so revision 0.6 does not implicitly re-endorse it. Coverage itself is correct and complete. **PASS** |
| **C-DOM-020** (least privilege) | No privilege added, removed or re-levelled. The one new API permission is the narrowest available (C-TECH-043). The 34-column field security profile is untouched and its membership script is tested to add **teams only, never a user**. **PASS** |
| **C-DOM-021** (privileged actions need elevated authorisation) | Unchanged. Bulk-delete job creation remains a gated `post_deploy` step; the new trigger-auth configuration is likewise a gated, owner-named step. **PASS** |

### 10.1 Previous check — revision 0.5 (retained for the record)

#### Constraint check — re-run after revision 0.5

Applied `skills/how-to-apply-constraints.md`. Scope is the constraints naming **development-agent**
in their `Scope` column: 6 domain HARD, 1 domain SOFT, 17 tech HARD, 6 tech SOFT. (Domain SOFT is
out of this agent's declared severity scope — `constraints/domain` is HARD-only for
development-agent — and is listed for completeness only.)

```
CONSTRAINT CHECK
Domain   HARD: 6 / 6   |  violations: NONE
Domain   SOFT: 1       |  warnings:   NONE  (C-DOM-031 is an unreplaced [PLACEHOLDER] row — not evaluable)
Tech     HARD: 17 / 17 |  violations: NONE
Tech     SOFT: 6       |  warnings:   C-TECH-013
  C-TECH-013: `DEFERRED_call_duplicate_grant_check` in the intake flow is a Compose that writes
              nothing. Carried forward unchanged from revisions 0.1–0.4 and reported honestly: it
              marks the FR-023 call site so Automation #7's insertion point is unambiguous rather
              than rediscovered. One action's cost. Remove it in the change that adds the
              child-flow call. NOT introduced or widened by revision 0.5.

Overall: WARN  (one SOFT warning, unchanged from revision 0.4. No HARD constraint moved in
                either direction; C-TECH-044 remains CLOSED as of revision 0.4.)
```

**Revision 0.5 is a structural packaging correction, so most constraints are untouched by
construction. The four that could plausibly have been affected were re-verified mechanically
rather than assumed:**

| Constraint | Why revision 0.5 could have moved it | Re-verified |
|---|---|---|
| **C-TECH-001** (HARD — no hardcoded secrets) | Files were moved and rewritten; a secret could have been introduced or unmasked | A case-insensitive `grep` for `secret`, `password` and `clientsecret` across the whole solution source returns only `<secretstore>0</secretstore>` (a definition flag, not a value) and the `rev_IntakeAllowedClientId` description explaining that a client ID is a public identifier and that the alternative route's shared secret *would* require Key Vault. **PASS** |
| **C-TECH-031** (HARD — no environment-specific values in the artifact) | The three environment variable definitions were physically relocated | All three still carry **no `<defaultvalue>`**. `Other/Customizations.xml`'s connection references still carry **no connection ID** — only `connectorid` values, which name a connector *type* (`shared_teams`) and are tenant-independent. No environment URL or GUID appears in any flow body. Both packaged .zip files were re-scanned. **PASS** |
| **C-TECH-046** (HARD — OOB security roles never modified) | Both role files were edited at the root element | Both are custom `REV`-prefixed roles with solution-owned GUIDs; no out-of-box role ID appears anywhere. The edit moved `RoleId`/`Name` into `id`/`name` attributes and changed nothing else — **40 privileges on REV Admin and 33 on REV Service Automation, counted after the edit**. **PASS** |
| **C-TECH-047** (HARD — env-specific platform values via environment variables) | Depends on the environment variable definitions actually shipping | Strengthened, not weakened: before revision 0.5 all three definitions were **silently absent from the package** (§2.5.2 defect #8), so the mechanism this constraint relies on did not exist in the artifact. All three are now verified present in both .zip files. **PASS** |

**Domain HARD constraints — all six re-verified as preserved, none design-affected:**

| Constraint | Re-verified |
|---|---|
| **C-DOM-003** (retention defined and automated) | The parental cascade the retention design depends on is intact — `CascadeDelete` = `Cascade` in `Other/Relationships/rev_applicant.xml` — and is now, for the first time, **actually in the package** (§2.5.2 defect #5). Bulk-delete provisioning untouched. **PASS** |
| **C-DOM-004** (no personal data in logs) | No logging path changed; flow bodies byte-identical. **PASS** |
| **C-DOM-010 / C-DOM-011** (audit logging and its schema) | No `Entity.xml` was modified. **122 `IsAuditEnabled` columns** across the four tables, counted after the pass (88 `rev_application`, 18 `rev_applicant`, 10 `rev_errorlog`, 6 `rev_setting`). **PASS** |
| **C-DOM-020** (least privilege) | No privilege added, removed or re-levelled — see C-TECH-046 above. The field security profile that enforces column-level least privilege is intact at 34 permissions with `rev_breaklocation` still deliberately excluded, and is now genuinely shipped rather than silently dropped. **PASS** |
| **C-DOM-021** (privileged actions need elevated authorisation) | Unchanged. **PASS** |

**One constraint is worth a note even though it passes, because revision 0.5 changed the
*evidence* for it rather than the code:** `C-TECH-042` (idempotent provisioning) and
`C-TECH-040` (roles assigned only via group teams) both depend on
`provisioning/dataverse/bind-roles-to-groups.ps1` looking roles up **by name**. That still works —
the role name now lives in the `name` attribute rather than a `<Name>` element, which is a change
to the *solution source*, not to what the platform exposes after import, since the platform
returns `role.name` either way. No provisioning script needed changing. Confirmed by inspection
of the script's lookup.

### 10.2 Previous check — revision 0.4 (retained for the record)

#### Constraint check — re-run after revision 0.4

Applied `skills/how-to-apply-constraints.md`. Scope is the constraints naming **development-agent**
in their `Scope` column: 6 domain HARD, 1 domain SOFT, 17 tech HARD, 6 tech SOFT.

```
CONSTRAINT CHECK
Domain   HARD: 6 / 6   |  violations: NONE
Domain   SOFT: 1       |  warnings:   NONE  (C-DOM-031 is an unreplaced [PLACEHOLDER] row — not evaluable)
Tech     HARD: 17 / 17 |  violations: NONE
Tech     SOFT: 6       |  warnings:   C-TECH-013
  C-TECH-013: `DEFERRED_call_duplicate_grant_check` in the intake flow is a Compose that writes
              nothing. Carried forward from the first pass, unchanged and reported honestly: it
              marks the FR-023 call site so Automation #7's insertion point is unambiguous rather
              than rediscovered. One action's cost. Remove it in the change that adds the child-flow call.

  ✅ C-TECH-044 — RESOLVED IN REVISION 0.4. Was: "ci.yml authenticates with APP_ID +
     CLIENT_SECRET; a federated credential is preferred and declared in both settings
     files but not adopted." Now: CLIENT_SECRET is gone from `.github/workflows/ci.yml`
     and from `config/revitalise-grant-automation-build.yml` `required_env_vars`.
     Authentication is `pac auth create --githubFederated --applicationId … --tenant …`,
     which exchanges the GitHub OIDC token for an Entra token with no stored secret.
     The provisioning identity was already certificate-based. The constraint asks for
     "federated credentials (OIDC) or certificates over client secrets" — BOTH halves of
     the pipeline now satisfy it, and no client secret exists anywhere in the delivery
     path. Carried as a SOFT warning through revisions 0.1, 0.2 and 0.3; CLOSED here.
     Evidence: ADR-021; §5.4.4; `grep -rn CLIENT_SECRET .github config provisioning
     scripts` returns only comments recording its removal.

Overall: WARN  (one SOFT warning, down from two. C-TECH-044 is resolved rather than
                carried. Nothing regressed; no HARD constraint moved.)
```

> ⚠️ **One HARD constraint outside development-agent's declared scope is materially affected by this
> revision, and is flagged rather than left for pipeline-agent to discover.**
>
> **C-TECH-030** — *"All deployments to Test, Acc, and Prd must use the managed/immutable artifact
> produced by the build-agent — no ad-hoc deploys"* — is scoped to **pipeline-agent only**, so it is not
> counted above. But revision 0.4 is what changes how it is met, so silence would be misleading.
>
> **The constraint's three purposes are met, and two of them more strongly than before:**
> - *Immutable artefact* — the pipelines host "prohibits any tampering or modification" to the exported
>   artefact. Stronger than a zip in a gitignored `build/artifacts/` folder.
> - *No stage bypass* — "the same managed artifact, per version, will be deployed to all subsequent
>   stages in the pipeline in sequential order… no solution can bypass QA environments". This is
>   platform-enforced. The pac route could only enforce it by job dependency, which a human with the
>   secret could sidestep.
> - *Traceability* — host run history retains every artefact by version, with who requested each
>   deployment, plus out-of-box reporting.
>
> **What no longer matches is the constraint's literal wording: the artefact is produced by the
> platform, not by the build-agent**, and its `Verify By` ("pipeline log references artifact manifest")
> describes a mechanism that no longer exists for TST/ACC and PRD. Two notes for the reviewer:
> 1. **`promote_mode: manual` is not an "ad-hoc deploy."** An ad-hoc deploy means bypassing the governed
>    path — someone running `pac solution import` against PRD by hand. Manual *initiation* of an
>    immutable, order-enforced, audited Pipelines promotion is the governed path.
> 2. **The constraint text should be amended** to name the pipelines host as an acceptable artefact
>    store. `constraints/technology/` is owned by the Tech Lead / Platform Architect
>    (`constraints/README.md`), and agents do not edit constraints — so this is raised, not done.
>    Until it is amended, pipeline-agent will read a `Verify By` it cannot satisfy literally.

### What revision 0.4 changed about the check

**No solution component was touched, so every data, flow, audit, retention and role constraint is
PASS unchanged by construction.** What follows is only what actually moved. Six constraints are
better evidenced than they were; none regressed.

| Constraint | Effect of revision 0.4 |
|---|---|
| **C-TECH-044** (SOFT — prefer OIDC/certificates over client secrets) | ✅ **RESOLVED — see the block above.** The single most substantive change in this revision, and the only constraint whose status moved. |
| **C-TECH-001 / 002 / 003** (no secrets in artefacts; secret handling) | **PASS, and materially stronger.** A client secret has been removed from the delivery contract entirely rather than relocated. There is now **no shared secret anywhere in the pipeline**: deploy identities use OIDC, the provisioning identity uses a certificate thumbprint. Both config files and the workflow header carry an explicit instruction to **delete the now-unreferenced `CLIENT_SECRET` repository secret** — an unreferenced credential is one nobody rotates and nobody notices leaking, so leaving it in place would have been the worse outcome of a "successful" migration. Secrets still reach commands only via `env:`; no resolved command containing an environment URL is echoed. |
| **C-TECH-020** (HARD — pinned dependencies) | **PASS, and no longer vacuous.** Previous revisions recorded this as "PASS, vacuously — there is no package manifest to audit". Revision 0.4 introduces two real runtime dependencies into CI and **pins both**: `pac` to **2.4.1** (the version the OIDC flag was verified against, and the version the Microsoft OIDC/FIC tutorial itself pins) and `yq` to **v4.44.3**, in `.github/actions/setup-powerplatform`. The previous `ci.yml` installed `pac` **unpinned** in all four places — which mattered more than usual here, because `--githubFederated` is flagged `(Preview)` in the CLI's own help output and an unpinned upgrade could change its shape. A wrong pin fails loudly at install rather than drifting. |
| **C-TECH-007** (HARD — synthetic data outside PRD) | **PASS, and enforced for the first time rather than merely declared.** The TST/ACC `pre_deploy` guard has existed in the pipeline config since 2026-08-10, but the previous `ci.yml` **never ran `pre_deploy` at all** (§5.4.6). Both promote jobs now execute the block, and the guard — being `script: manual` — is recorded as an operator checklist item in the job summary instead of being passed to `bash` and crashing. |
| **C-TECH-041** (HARD — tenant ops behind `APPROVE TENANT`, recorded) | **PASS, and strengthened.** The ALM choice introduced four genuinely new tenant-level operations (pipelines host, pipeline/stage configuration, Managed Environment enablement, pipelines access). All four are declared in `tenant_prerequisites` behind the existing gate and mirrored into TAD §12 — **added to the gate rather than assumed already in place**, which is the failure mode this constraint exists to prevent. The licence-cost item is called out for explicit confirmation with Revitalise. |
| **C-TECH-042** (HARD — idempotent provisioning) | **PASS, with one property honestly retired.** No script logic changed. But splitting the deploy registration per environment means the two `ensure-app-registration.ps1` runs are **no longer "create, then prove idempotency"**: each run creates a different deploy registration and reports `EXISTS` for the shared ones. Each individual resource is still check-before-create and each run is still safe to repeat — the constraint holds — but the *second run's output must now be read* rather than skimmed as a known no-op. Recorded in both settings files and in the pipeline config so nobody relies on the old reading. |
| **C-TECH-043** (HARD — least privilege, justified in TAD §6 + ADR) | **PASS, and moved further in the right direction.** Three environment-scoped deploy identities replace one shared identity, each an application user in its own environment only, each with exactly one federated credential. Justified in TAD §6.7 and in ADR-007 + ADR-021, as the constraint requires. No permission was widened: all three request only Dataverse `user_impersonation`, so admin-consent surface is unchanged. §6.7's claim that these registrations were "required only if ADR-007 selects this system's pipeline" was **wrong even under Pipelines** and has been corrected — CI still authenticates to DEV and still verifies and provisions the targets. |
| **C-TECH-031 / C-TECH-047** (HARD — no environment-specific values embedded; injected at deploy time) | **PASS, but one control is genuinely weaker and it is not being hidden.** No environment URL, GUID or tenant UPN was committed: the pipeline stage GUIDs indirect to `$PIPELINE_STAGE_ID`, environment URLs stay in GitHub Environment secrets, and the `no-hardcoded-environment-values` build gate is unchanged and still passes. **However:** Pipelines does not accept a deployment settings file, so `pac-import-tstacc.json` / `pac-import-prd.json` are no longer *applied by a tool* — they are retained as the code-reviewed record of values a human types into the deployment pane. The values are still declared per environment outside the solution, so the constraint holds; the *enforcement* moves from automation to a person. Mitigations: both files stay under code review, and Pipelines validates connection references and environment variables against the target **before** the import rather than failing after it. |
| **C-TECH-013** (SOFT — dead code) | **PASS on the new work; the one pre-existing warning is unchanged.** One judgement to declare rather than bury: `scripts/ci/promote-via-pipelines.sh` implements a `cli` promotion path that **the current config does not select** (`promote_mode: manual`). That is a config-selected alternate mode, not unreachable code — it is reached by changing one key, its error paths were exercised, and it exists precisely so the manual mode has a proven upgrade route once §5.4.5's two unknowns are settled. It is listed here so a reviewer who reads it as speculative can say so. |
| **C-TECH-011 / 012 / 022 / 023** (SOFT — no TODO/FIXME/HACK, single purpose, deps) | **PASS.** `grep -rniE 'TODO\|FIXME\|HACK'` across `.github`, `scripts`, `config` and `provisioning` returns nothing. Each new script has one job; the composite action exists specifically to stop the four-way duplication the old workflow had. |
| **C-TECH-032** (HARD — Deployment Summary per PRD deploy) | **PASS, unaffected, with one addition for pipeline-agent.** The Deployment Summary is still required and still records two promotions per release. It must now **also** reference the Pipelines run-history record for each promotion, because that is where the artefact identity and the requesting identity live. Noted so the deployment-summary template is extended before the first PRD deploy rather than after. |
| **C-TECH-033** (SOFT — rollback possible and verified) | **PASS, with a new dependency named.** `rollback_artifact` is still `""` and the 1.0.0.0 reasoning is unchanged (uninstalling a first managed solution removes its tables and their data, so the route is: disable the flows, leave the solution, fix forward). What changed is the *mechanism* for later releases: the first-choice route is now redeploying a previous version from the pipeline's run history, **which requires a pipeline setting to be enabled** — added to `tenant_prerequisites`, because without it only higher versions can be deployed and the documented fallback is a break-glass manual re-import. |
| **C-DOM-001 – C-DOM-021, C-TECH-004 / 005 / 006 / 040 / 045 / 046 / 048** | **PASS, unchanged and unchallenged.** No entity file, flow definition, security role, option set, field security profile, connector, `rev_setting` value or Code App was touched in this revision. C-TECH-045 (DLP) is worth one explicit note: the connector set did not change, and the DLP prerequisite already covers all three environments. C-TECH-048 still has no Code App to apply to in Phase 1. |

### What revision 0.3 changed about the check

**Nothing regressed, and two constraints are better evidenced.** Re-run evidence: XML
well-formedness on all **42** XML files (43 before `rev_feelingscale.xml` was deleted), JSON parse on
all 4 flow definitions and both settings files, `verify-solution-root-components.py` → **PASS, 35 root
components** (36 before the deletion), `verify-field-security-coverage.py` → **PASS, 34 secured
columns, all released, 1 reviewed exemption**, and all four `build.yml` grep gates → PASS.

| Constraint | Effect of revision 0.3 |
|---|---|
| **C-DOM-004** (no personal data in logs) | **PASS, and materially better.** Removing the five referee and emergency-contact fields from the intake contract removes **third-party personal data** from the payload the endpoint accepts at all — the strongest form of this control, since data never received cannot be logged. No log message, error message or notification changed. |
| **C-DOM-010 / C-DOM-011** (audit) | **PASS.** `rev_feelingscaleanswer` keeps `IsAuditEnabled=1` across the type conversion — checked explicitly, because a retype is exactly where an audit flag gets dropped. No other column's audit setting changed. |
| **C-DOM-020** (least privilege) | **PASS, with one thing stated rather than left implicit.** The five referee and emergency-contact columns stay `IsSecured=1` and stay released by `REV_TrusteeRestricted`, so the service identity retains `cancreate` on columns **nothing now writes**. That is deliberate, not an oversight: the process owner needs create and write to fill them in by hand until Automation #3's post-approval form exists, and the profile is the only thing that grants her that. Removing them from the profile would make the columns unreachable by anyone and would fail `verify-field-security-coverage.py`. If the reviewer prefers the tighter posture, the alternative is a second profile — which is Automation #3's problem, not Phase 1's. |
| **C-TECH-004** (input validation) | **PASS, and better evidenced.** The trigger schema now accepts **five fewer** fields — a smaller accepted surface. `feeling_scale_answer` is still a typed integer in the schema, and its range is now enforced **by the platform**: `rev_feelingscaleanswer` is an `int` with `MinValue` 0 and `MaxValue` 10, so an out-of-range value (say 42) is rejected by Dataverse at the create, the intake returns 500 and the caller retries — loud and fail-closed, rather than a silent wrong score. Note the failure mode this replaces: an out-of-range value reaching the *scoring* flow would miss the inversion map, fail the `int()` cast and leave the application unscored with an error logged — also fail-closed, but later and less clearly. The schema-level bound is the better place for it. |
| **C-TECH-013** (dead code) | **PASS on the new work, and one piece of near-dead reference data was actively removed.** The orphaned `rev_feelingscale` option set was **deleted** rather than left shipping with no column behind it, and its root-component declaration went with it in the same change. The replacement in `Solution.xml` is **explanatory prose, not a commented-out declaration** — deliberately, because a commented-out `<RootComponent>` is exactly what this constraint prohibits. The two pre-existing SOFT warnings are unchanged. |
| **C-TECH-031 / C-TECH-047** (no environment-specific or embedded values) | **PASS, unchanged.** `MaxCircumstanceScore` and `FeelingScaleInversion` changed value, and both live in `provisioning/deploymentSettings/*.json` and are read from `rev_setting` at run time. No literal moved into a flow: the `no-hardcoded-thresholds` gate passes, and the maximum still reaches the score breakdown through `Read_MaxCircumstanceScore` rather than as text. |
| **C-TECH-042** (idempotent provisioning) | **PASS, unchanged.** No script logic changed. Two `rev_setting` values changed, and `seed-settings.ps1` remains a keyed upsert on the `rev_setting` alternate key, so re-seeding an environment that already holds the old values simply overwrites them. |
| **Everything else in scope** | **PASS, unchanged.** No secret, endpoint, connector, role, privilege, tenant operation, dependency or Code App was touched. C-TECH-046 is untouched — both roles remain custom `REV`-prefixed roles and neither role file changed at all in this pass. |

### What revision 0.2 changed about the check, constraint by constraint

**Nothing regressed. Four constraints are better evidenced than they were.**

| Constraint | Effect of revision 0.2 |
|---|---|
| **C-DOM-001 / C-DOM-002** (classification, lawful basis) | **Not in development-agent's declared scope** — both are scoped to plan-agent and architect-agent — but verified anyway because this pass added forty-nine columns. **Every one is classified**, in the column's own `<Description>`, and each cites the export column it came from. Two classifications are stated explicitly because they are the ones most easily got wrong: `rev_gender` is **ordinary** personal data, not Article 9 (gender reassignment is an Equality Act characteristic, not a UK GDPR special category), and benefit status **is** at the highest restriction tier per SDD §7.1. No new lawful basis is needed: every column is the same processing — assessing and administering a grant, Art. 9(2)(b)/(h) for the health data — on the same two entities the SDD already covers. **No new entity was created**, which is what would have triggered a fresh C-DOM-002 entry. |
| **C-DOM-003** (retention + automated deletion) | **PASS, unchanged.** Forty-nine columns were added to two tables that are already covered by the four recurring bulk-delete jobs in §3.2, and no new table was created, so no new retention rule is needed and none is missing. The Application-anchored retention design is also the first of the three reasons the condition profile stays on `rev_application` — §7.5 D-7. |
| **C-DOM-004** (no personal data in logs) | **PASS, and re-verified line by line** because the intake flow's log message changed. The message now names *field names* (`first_name, last_name, …`), never values; the 400 response body lists required field names; the failure alert passes `submission_id` and a platform error string. The one notification that carries personal data is the FR-009 message, which **requires** the applicant's name — and it now composes it from the two new columns. ADR-015 remains the control: 1:1 chat to one named recipient, never a channel. `rev_errorlog` still has no column capable of holding personal data. |
| **C-DOM-010 / C-DOM-011** (audit) | **PASS, with one thing worth stating so nobody mistakes it for a gap.** All forty-seven new *stored* columns carry `IsAuditEnabled=1`. The two **calculated** columns (`rev_fullname`, `rev_costs`) carry `IsAuditEnabled=0`, because Dataverse audits stored values and a calculated value is computed on retrieve — there is nothing to audit. **No coverage is lost:** every source column of both is audited, so a name change or a cost change is still fully evidenced with timestamp, actor, action, record ID and before/after values. |
| **C-DOM-020** (least privilege) | **PASS, and moved further in the right direction.** No role privilege was widened. Seventeen columns were *added* to the secured set, four of them (the benefit columns and two financial explanations) holding content that previously sat unsecured inside `rev_financialanswers` — a tightening, flagged as a DERIVED decision in §6.5 for the reviewer to accept or reject. `rev_gender` and `rev_title` are secured on the same least-privilege reasoning even though neither is special-category. |
| **C-DOM-021** (privileged actions) | **PASS, unchanged.** No new privileged action. |
| **C-TECH-004** (input validation) | **PASS, and materially better than it was.** Replacing `rev_financialanswers` — one 2000-character free-text field holding eight answers — with eight typed columns moves validation from "the flow should check" to "the schema cannot hold anything else": a `bit` column cannot store a paragraph. The trigger schema is typed throughout and the `required` list was updated with the contract change. |
| **C-TECH-005** (injection) | **PASS.** The applicant-match `$filter` now interpolates three user values instead of two (`rev_email`, `rev_firstname`, `rev_lastname`). All three use the same guard, unchanged: single quotes escaped by doubling, which is the platform-correct OData escaping. The caveat recorded in the first pass is carried forward unchanged. |
| **C-TECH-001 / 002 / 003 / 006 / 007 / 031 / 040 / 041 / 043 / 045 / 046 / 047 / 048** | **PASS, unchanged by this revision.** No secret, endpoint, connector, role assignment, tenant operation or environment-specific value was added. The two role files changed by **one comment each** — the `prvReadTransactionCurrency` justification now names all seven money columns rather than two — so C-TECH-046 (never modify an OOB role) is untouched: both roles are custom `REV`-prefixed roles. C-TECH-048 has no Code App to apply to in Phase 1. |
| **C-TECH-020** (pinned dependencies) | **PASS, vacuously, and unchanged.** There is no package manifest in this repository — it is an unpacked Power Platform solution plus PowerShell provisioning — so the constraint's own `Verify By` ("package manifest audit") has nothing to read. The PowerShell modules are runner prerequisites documented in `provisioning/README.md`. Recommendation to pin when a manifest exists is carried forward in §7.4. Revision 0.2 added no dependency. |
| **C-TECH-042** (idempotent provisioning) | **PASS, unchanged.** No script logic changed. `MaxCircumstanceScore` changed *value*, and `seed-settings.ps1` remains a keyed upsert on the `rev_setting` alternate key, so re-seeding is still safe. |
| **C-TECH-011 / 012 / 022 / 023** | **PASS.** Grep for `TODO`, `FIXME` and `HACK` across `src/solutions`, `scripts`, `provisioning` and `config` returns nothing. The one new script is single-purpose. No dependency was added. |

### Two things that are NOT constraint violations but that a reviewer should not mistake for clean

1. **Five option sets carry placeholder values.** This is not a C-TECH-011 breach — there is no
   `TODO` marker and nothing is unfinished code — but it *is* unconfirmed reference data shipping to
   Test. It is flagged in each file's own header, in each column's description, in the form
   specification and in §7.5 D-5. **It must not reach PRD unconfirmed**, because renumbering an
   option after applications exist changes what historic rows mean.
2. **The two calculated columns have never been packed.** `<SourceType>` plus `<Formula>` is written
   from convention. That is a packaging risk (§7.1 item 3a), not a constraint violation, but it is
   the item most likely to fail on first import out of everything this revision added.

## Code Review Checklist

- [ ] All FR IDs covered
- [ ] No hardcoded secrets
- [ ] Security controls from TAD §6 implemented
- [ ] Every TAD §12 item has an idempotent provisioning script wired into `config/revitalise-grant-automation-pipeline.yml` (C-TECH-042)
- [ ] Role assignments via group teams only — no direct user assignments in Test/Acc/Prd (C-TECH-040)
- [ ] No hardcoded environment-specific IDs/URLs — environment variables or deployment settings (C-TECH-047)
- [ ] Accessibility requirements met (if UI)
- [ ] No dead code or debug statements
- [ ] Unit tests written

### Revision 0.8 review items — the scoring methodology, proved and corrected (D-014, D-006)

**One decision genuinely needs you.** Everything else in this revision is verifiable from evidence
that is in the repository.

**THE DECISION — the rounding rule (§ revision 0.8 banner):**

- [ ] **CONFIRM OR OVERRIDE "ROUND HALF UP".** A total can now be fractional (an odd number of "Not
      sure" answers gives X.5) and `rev_circumstancescore` is an `int` column. I round **half up**,
      in the applicant's favour, and keep the exact total in `rev_scorebreakdown`. **The data does
      not settle this** — every published total in the CSV is whole and the only "Not sure" row is
      whole by coincidence. The alternative is a **decimal column**, which is more faithful and a
      bigger change (column type, views, daily summary, trustee pack, "n out of N" rendering). Say
      which you want. Truncation was rejected outright: biased against the same applicants, and
      indistinguishable from the bug being fixed.

**Verify the evidence rather than taking my word (all mechanically checkable):**

- [ ] The 25-row reconstruction passes and is not vacuous — set `LikertPointMap["6"]` to `1` and
      confirm **4** tests fail, including *"reproduces the published score EXACTLY"*. I did this;
      do it again if you want it independently.
- [ ] "Not sure" = 0.5 is **derived, not chosen** — row 25 of `docs/Import/Book(Sheet1).csv`:
      total 9, life satisfaction 6 → 4 points, residual 5 over 10 answers.
- [ ] The two scales are genuinely different — the CSV's label sets for columns 96–102 and 103–105
      are **disjoint apart from "Not sure"** across all 25 rows.
- [ ] `Derive_status` reads the **rounded** score, so the stored score and the outcome cannot
      disagree (a 36.5 against a borderline lower bound of 37 would otherwise skip a human review).
- [ ] D-006: run `gitleaks detect --source . --no-git --no-banner --redact --exit-code 1` — the
      command **as the config now contains it** → ≈3.06 MB, no leaks, exit 0.

**Note what did NOT change, because it bounds the blast radius:**

- [ ] No option **value** changed meaning. Positions 1–5 are unchanged on both scales, so any
      integration already sending these numbers correctly needs no change.
- [ ] `MaxCircumstanceScore` is still **60** — 0.5 cannot raise a maximum. But the reachable
      **floor** moved from 10 to **5**, which the board needs for OQ-001.

**Route onward, not for approval here:**

- [ ] **SDD Amendment A-01 needs `plan-agent`.** It is marked **PROPOSED** and carries replacement
      FR-013 wording. I did not edit the approved SDD's requirement text — that would have bypassed
      the plan gate. **OQ-001 is NOT resolved** and this cycle was commissioned as though it would
      be; OQ-002 is what the data resolves.

### Revision 0.7 review items — the form already exists (D-003, D-004)

**Three decisions need you. Everything else in this revision is either mechanically verifiable or is
explicitly left for you in spec §9.**

**Decisions for the reviewer:**

- [ ] **CONFIRM THE FOUR-FIELD REQUIRED LIST.** The intake now requires only `submission_id`,
      `first_name`, `last_name`, `postcode` — the four the live form always collects. `email` and
      `date_of_birth` are accepted but not required, because the live form asks for an email address
      only when the applicant picks Email as their preferred contact method and **never** asks for a
      date of birth. The previous six-field list would have rejected **every** real submission with a
      400. A narrower floor (`submission_id` alone) is arguable; four is where I drew it. §2.6.2.
- [ ] **ACCEPT OR REJECT THE NAME + POSTCODE APPLICANT FALLBACK.** With no email address there has to
      be some identity to match a returning applicant on. Name plus postcode is the only one the live
      form guarantees, and it would **merge two same-named people at one address**. Stated rather than
      hidden. The alternative is a duplicate applicant record for every postal-preference person who
      applies twice. §2.6.2 edit 5.
- [ ] **DECIDE WHAT GOES TO ALEX, AND IN WHAT ORDER.** Spec §7 is a scoped validation-and-completeness
      change request: twelve items, priority-ordered, each evidenced from the live form's own markup or
      from the charity's own record of routinely-missing items. **Accessibility is deliberately not in
      it** — that is §10 and it needs an audit first (OPEN-26). Priority 1 is the four missing
      conditional gates plus the missing email address and age; those five are where the
      wrongly-filled-in data is coming from.

**Then read spec §9 — ten mapping gaps I deliberately did not close:**

- [ ] **M-01 is the one that needs a real decision.** The live form's condition checkboxes ask about
      **ten functional areas affected** (Vision, Hearing, Mobility, Dexterity, Learning, Memory, Mental
      health, Stamina, Socially/behaviourally, Other). `rev_conditionprofile` names **eight condition
      types** (Physical disability, Sensory impairment, Learning disability, …, Autism, Other). These
      are not two spellings of one list — they classify along different axes, and this data is shown to
      trustees and reported to funders. Either the option set changes, or the form does, or a written
      many-to-many map is agreed. **No mapping was invented.**
- [ ] **M-02: the three "last year" wellbeing questions use a six-point agree/disagree scale including
      "Not sure", not the five-point frequency scale revision 0.3 recorded as confirmed.** Read from
      the form's own Likert column headers. Answer 6 has no value in `rev_likertresponse` and no
      defined contribution to the score out of 60. This is a scoring-integrity question, not a storage
      question.
- [ ] **M-03 / M-04: income band.** Four bands on the form against six in the option set, with
      overlapping boundaries — and the question is asked **only of applicants who say they receive no
      means-tested benefits**. If that gating is intended, the income eligibility check must treat an
      absent band as "qualifies on benefit status" or every benefit-receiving applicant is routed to
      manual review, which is the opposite of the point.
- [ ] **M-07: five option sets do not match the live form.** Real values are in spec §6. Trimming an
      option set is safe **before** any application exists and unsafe after, because renumbering
      changes what historic records mean. This is a before-go-live item and it closes OPEN-20.
- [ ] **M-09: roughly 30 of the live form's 139 answer columns have nowhere to be stored** — notably the
      ten care-type checkboxes and the hours of care provided per week, which are the two that describe
      the caring load the charity exists to relieve. Adding columns is a schema change with a real blast
      radius; it belongs in a planned pass.
- [ ] **M-10: ten fields the intake accepts that the live form never sends**, including
      `rev_carername`, `rev_carersupport` and `rev_travellingwithcarer` — the three added in revision
      0.2 to close OPEN-2. They are secured, they appear on forms, and they will always be empty.
      Either the form starts asking, or they are recorded as filled by another route, or they go.

**Mechanically verifiable — check the evidence, not the prose:**

- [ ] `pwsh -c "Invoke-Pester -Path src/tests"` → **537 passed, 0 failed, 1 skipped**. 10 of those
      assertions are new and 3 are changed; the changed ones are changed because the contract changed,
      not to make a red test green.
- [ ] `gitleaks detect --no-git --redact` → 2.80 MB scanned, no leaks (C-TECH-001).
- [ ] The reject guard, the 400 body and the `Log_incomplete_payload` message name the same four fields
      and no personal data (C-DOM-004) — asserted by a test rather than by reading the diff.
- [ ] `AgeRangeLabelMap` is byte-identical in `test-settings.json` and `prd-settings.json` and contains
      no URL, GUID or environment identifier (C-TECH-031/047).
- [ ] Constraint check in §10: Domain HARD 6/6 clean, Tech HARD 17/17 clean, one unchanged SOFT warning
      (C-TECH-013). The C-TECH-004 reasoning in §10.0 is the row to read properly — a shorter required
      list looks like a relaxation and the argument that it is not is in that row.

### Revision 0.6 review items — the test-agent fix cycle (D-001, D-005)

**Two decisions need you specifically. Everything else is verifiable mechanically.**

**Decisions for the reviewer:**

- [ ] **CONFIRM OR OVERRIDE THE COVERAGE THRESHOLD.** `knowledge/technology/coding-standards.md`
      → Test Coverage now sets **80% line coverage over `provisioning/{common,entra,dataverse}`,
      build-failing**, with declarative artefacts excluded and replaced by the enumerated
      invariant list in §9.6. The test report framed this as a Tech Lead decision; no Tech Lead
      was available, so development-agent made the call and wrote down the reasoning. **It is not
      settled by having been written down.** Read the reasoning and the scope exclusion — the
      exclusion is the more consequential half of the decision.
- [ ] **CONFIRM THE ADR-011 POSITION IS WHAT YOU MEANT.** The Entra OAuth route is now the fully
      provisioned, owned and testable default implementation; **ADR-011's status is unchanged at
      `Decision required`** and the trigger description, both settings files and the ADR entry all
      say so explicitly, with each alternative's teardown recorded in-place. If you intended
      something narrower or wider than that, say so now — it is much cheaper before Alex builds.

**Fix 1 — things to check rather than take on trust:**

- [ ] The trigger authentication value is specified **exactly**: mode *Specific users in my
      tenant*, Allowed users = the `rev-wordpress-intake` **service principal object ID** (not the
      application ID — they are different values and the flow's own parameter description says so).
- [ ] The `post_deploy` step naming the owner (Wanstor) exists on **both** TST/ACC and PRD, and
      says to configure it **before turning the flow on**.
- [ ] ⚠ **A blank Allowed users list silently means "any user in the tenant"** — Microsoft's own
      note. No test can detect that, so the step says to read the field back after saving. Satisfy
      yourself that instruction is prominent enough.
- [ ] ⚠ **One item is flagged, not resolved**: the delegated-scope-plus-app-only-token combination
      that every published walkthrough uses is unusual. If Entra refuses the client-credentials
      request on first run, the fix (application permission, `type` → `Role`) is recorded at the
      point of use in both settings files. Confirm you are content to discover that on the first
      `APPROVE TENANT` run.
- [ ] `INTAKE_ENDPOINT_URL_TEST` / `_PRD` must be created as CI secrets before the smoke test can
      run. The URL is a credential (SAS `sig=`), which is why it is not a settings value.
- [ ] The smoke test is **deployment-halting** on PRD, and must pass before the endpoint URL is
      given to Alex.

**Fix 2 — what the green build does and does not mean:**

- [ ] **528 tests pass, 1 deliberately skipped, 0 failures. Coverage 92.6% against an 80%
      threshold.** Re-run it yourself: `pwsh -NoProfile -File src/tests/Invoke-Tests.ps1
      -CodeCoverage -CoverageThreshold 80`. The gate was negative-controlled — at
      `-CoverageThreshold 99` the runner exits 1 — so it is a gate and not decoration.
- [ ] The one skipped test is `-Skip`ped **on purpose** and names test-agent defect D-011 plus the
      one-line fix. Confirm you are content for an open P4 to be recorded as a skipped test rather
      than only in a report.
- [ ] **Nothing in this suite executes a flow, enforces column security or produces an audit
      record.** Every case in test-agent's §8 stays deferred. Do not read the green step as an
      environment-tested release.
- [ ] The tests deliberately assert the **request** each provisioning script sends, not just that
      it ran. Spot-check two: `rev_effectivefrom` on create only, and the orphan sweep's LEFT
      OUTER join.
- [ ] The suite writes a temporary settings fixture to
      `provisioning/deploymentSettings/acc-settings.json` and removes it. It refuses to overwrite
      an existing file and is now gitignored. Confirm `acc` really is unused for this feature
      (TAD ADR-006 says TST and ACC are one environment, addressed as `test`).

**Carried forward, unfixed, and deliberately so:**

- [ ] **D-004 (WCAG 2.1 AA acceptance narrower than the standard) remains open and is the
      highest-human-consequence finding in the release.** This revision does not touch it.
- [ ] D-002, D-003, D-006 to D-013 are untouched — the brief was these two defects.
- [ ] **D-007 stands**: the "122 `IsAuditEnabled` columns" figure elsewhere in this document is
      wrong (correct: 118 audit-enabled of 120 attributes). Flagged in §10.0 so revision 0.6 does
      not implicitly re-endorse it. Audit coverage itself is correct.
- [ ] One robustness observation reported and **not** fixed: two Entra scripts pipe a Graph result
      into `Where-Object { $_.Property … }`, which would throw under StrictMode on an explicit
      `$null`. It does not manifest with the real cmdlets. Direct whether to harden it.

### Revision 0.5 review items — the packaging correction

**Read §2.5 first.** No requirement, privilege, permission, data value or flow logic changed;
this revision changed file locations and XML shape so the solution can be built at all.

- [ ] **Accept that the packaging layer is now evidence-based, not convention-based.** Every fix
      cites the line of `SolutionPackagerLib` that demands it (§2.5.1–2.5.2). If you disagree with
      a fix, the fastest check is to re-run the pack — it is the authority now, not judgement
- [ ] **Accept the child-element-vs-attribute rule and where it inverts.** `Role`, `optionset`,
      `FieldSecurityProfile`, `EntityRelationship` and `Workflow` are keyed by **attributes** on
      the file's root element; `AppModule` and `AppModuleSiteMap` are keyed by **child elements**.
      This is the packer's inconsistency, not this repo's, and it is the reason the wrong pattern
      survived four revisions — it was never uniformly wrong
- [ ] **Accept that a green pack is not proof a component shipped, and that §8 now says so.**
      Six of nine defects packed cleanly while omitting components. The worst was the field
      security profile: 34 secured columns would have imported with nothing releasing them,
      unreadable even by the process owner. Confirm you are satisfied with the archive-inspection
      check in §8 as the standing control, and decide whether the build-agent should add it as a
      `verify-package-contents` step
- [ ] **`<Managed>2</Managed>` in `Other/Solution.xml`** — confirm you want one source producing
      both artefacts (this is what the repo's stated solution type already implies). The packer
      stamps the resolved `0`/`1` into each shipped .zip, verified in both (§2.5.3)
- [ ] **Two `RootComponent` declarations changed from `id` to `schemaName`** (type 80 app, type 62
      app sitemap). Confirm you accept that these two types can *only* be declared by name — the
      GUIDs are unchanged and still live in `<appmoduleid>` / `<sitemapid>` (§2.5.2 defect #9)
- [ ] **The relationship detail file was renamed `rev_application.xml` → `rev_applicant.xml`.**
      Named after the *referenced* one-side table, which is how the packer groups them. This is a
      forward-compatibility fix: the old name would have collided with a future
      `pac solution unpack` and produced a hard `DuplicatedRelationshipName` error
- [ ] **Both verification scripts were corrected, and both previously returned PASS against the
      broken source.** `verify-solution-root-components.py` and
      `verify-field-security-coverage.py` now assert the packer-verified forms and would have
      failed the old layout (§2.5.5). Confirm you are satisfied the checks now check something
- [ ] **Confirm nothing was lost.** 40 + 33 role privileges, 34 field permissions, 15 option sets,
      122 audit-enabled columns, 4 flow JSON bodies byte-identical, cascade profile intact
      (§2.5.6). Every count was taken *after* the edit, not carried over from a previous revision
- [ ] **Note what packing still does NOT prove.** Privilege names, calculated-column formula
      dialect, `@odata.bind` casing and the `runas` numeric are all opaque to the packer and remain
      open — §7.1 items 1, 3a and 4–8. Only `pac solution check` and a real import settle those

### Revision 0.4 review items — ALM tooling, CI/CD and credentials

**No solution component changed.** These are all delivery-infrastructure items.

- [ ] **The responsibility boundary is right.** GitHub Actions ends at "import the unmanaged solution
      into DEV"; Power Platform Pipelines owns DEV → TST/ACC → PRD. Confirm you accept that the
      **build artefact is no longer the deployed artefact** (§5.4.2) and that this is how C-TECH-030
      is now met (§10). ⚠ **This is the item to reject if any of it is wrong** — everything else
      follows from it.
- [ ] **`promote_mode: manual` is accepted for the first release.** The alternative is switching to
      `cli` and discovering on a live PRD promotion whether a service principal may request one, and
      what `--currentVersion` means (§5.4.5). Say if you would rather take that risk.
- [ ] **Two new tenant prerequisites are accepted, including the licence cost.** A custom pipelines
      host environment, and Managed Environment status on TST/ACC and PRD requiring premium use
      rights (§5.4.3, TAD §12). The second is a **cost that did not exist before this ALM choice** and
      needs confirming with Revitalise.
- [ ] **One deploy identity per environment.** Three app registrations, one federated credential
      each, application user in its own environment only. Confirm the reasoning for splitting the
      *registration* rather than only the credential (§5.4.4) — and that three registrations is
      proportionate rather than fussy for a charity this size.
- [ ] **The `pac-import-*.json` files' new role.** They are no longer applied by any tool; they are
      the reviewed record of values a human types into the Pipelines deployment pane. This is a real
      weakening of one control (§5.4.2). Accept or propose an alternative.
- [ ] **DEV will be overwritten from git on every CI run.** `--force-overwrite` on the staging import
      means uncommitted portal edits in DEV are lost. Intended per TAD §9.2, but it needs to reach
      the ALM runbook and whoever uses DEV.
- [ ] **`config/pipeline.yml.example` was rewritten**, making three-environments + Pipelines the
      project's default shape for future features. Judgement call, reasoned in §5.4.7 — it was
      required for correctness because the shared `ci.yml` no longer reads `deploy_command`. Confirm.
- [ ] **The latent `manual: command not found` bug** in the old shared workflow, and the fact that
      `pre_deploy` was never executed at all — including the C-TECH-007 synthetic-data guard (§5.4.6).
      Worth confirming you want manual steps recorded-and-warned rather than hard-failing the job.
- [ ] **C-TECH-044 reads as resolved** in §10 rather than carried forward, and the evidence holds:
      no `CLIENT_SECRET` outside comments recording its removal.

### Revision 0.3 review items — the three answered questions

- [ ] **§2.4.1** — **the score is out of 60 and the life-satisfaction question is now a Whole Number
      0–10.** Confirm the *type* choice (Whole Number with `MinValue` 0 / `MaxValue` 10, rather than an
      eleven-value option set) and the reasoning — chiefly that option value `0` would make *worst
      wellbeing* indistinguishable from *unanswered*, which FR-022 depends on distinguishing. Confirm
      also that the inversion is `10 − answer` held as an eleven-entry `FeelingScaleInversion` map, and
      that `MaxCircumstanceScore` is 60 in both settings files
- [ ] **§2.4.1** — **`rev_feelingscale` (the five-option set) has been DELETED**, along with its
      `RootComponent` declaration. Confirm deletion is preferred to leaving an orphaned option set in
      the solution. 35 root components, verified both directions
- [ ] **§2.4.2** — **the five referee / emergency-contact fields are removed from the intake flow**
      (trigger schema and create mapping) while the **five columns stay on `rev_application`**.
      Acknowledge, and note the residual open question that belongs to Automation #3: **who receives
      and completes the separate post-approval form** — the applicant relaying the details, or the
      referee and emergency contact self-reporting
- [ ] **§2.4.3** — **the ten wellbeing answer labels are now the confirmed frequency scale.** Confirm
      the finding that no option **value** needed changing: all ten questions are positively worded,
      checked one at a time, so value 1 ("None of the time") is correctly the highest-need answer and
      `LikertPointMap` was already right
- [ ] **§6.5** — **the revision 0.2 financial-column security tightening was reviewed and ACCEPTED,
      unchanged.** Nothing to do; recorded so it is not re-litigated. Reversible with no data impact if
      the posture is ever revisited
- [ ] **§9.3** — the scoring test assertions changed with the maximum. Confirm the new headline case:
      ten wellbeing answers at `1` plus life satisfaction `0` → **60**

### Revision 0.2 review items — the schema revision pass

- [x] ~~**§2.3.2 / §7.5 D-3** — the circumstance score maximum is now 55, not 60~~ → ✅ **ANSWERED AND
      CLOSED IN REVISION 0.3: it is 60.** The 0–10 scale was confirmed and `rev_feelingscale`,
      `FeelingScaleInversion` and `MaxCircumstanceScore` were all reissued together. **SDD OQ-001 and
      OQ-002 are unblocked.** §2.4.1
- [ ] **§2.3.4 / §7.5 D-4** — **the intake payload contract is broken on purpose**: `full_name` →
      `first_name` + `last_name`, and `costs`, `financial_answers` and `wellbeing_answer_11` removed.
      Confirm the form specification has **not** already been issued to Alex as CONFIRMED
- [x] ~~**§2.3.3 / §6.5** — DERIVED classification decision: four financial columns are secured
      although the column they replaced (`rev_financialanswers`) was not~~ → ✅ **ACCEPTED, UNCHANGED,
      in revision 0.3.** No action taken and none needed. Reversible with no data impact. §6.5
- [ ] **§7.5 D-5** — five option sets carry **placeholder** values. Accept building now with
      placeholders flagged, or require them left out until Emily confirms
- [x] ~~**§7.5 D-6** — Referee and Emergency Contact confirmed post-approval and left unchanged. Note
      that **the intake trigger still accepts them**~~ → ✅ **CLOSED IN REVISION 0.3.** The mechanism is
      confirmed (separate form, after board approval) and **the intake trigger no longer accepts them**.
      The columns are unchanged. One residual question — who completes that form — belongs to
      Automation #3. §2.4.2
- [ ] **§7.5 D-7** — condition profile placement **closed: it stays on `rev_application`**. No change
      made. Acknowledge the closure
- [ ] **§2.3.1 / §7.4** — **ethnic group: the export proves the column is real** (col 150), which
      contradicts SDD OQ-027's "where captured" framing. **No action taken.** Acknowledge, and carry
      the fact to the DPO when OQ-027 is revisited
- [ ] **§7.4** — form specification **OPEN-19**: the applicant-facing question count went 47 → 82.
      Authorise asking Emily which questions can be dropped or deferred, rather than shipping a
      longer form
- [ ] **§7.1 item 3a** — two **calculated columns** are written from convention and never validated.
      Acknowledge that both may need to be built in the DEV UI and re-unpacked
- [ ] **§2.3.3** — `rev_travellingwithcarer`'s description is still wrong (it says the value is
      derived; the form asks it). Left alone deliberately to keep this diff reviewable. Authorise the
      one-line fix for the next pass

### Additional review items specific to this release

- [ ] **§6.1(a)** — `REV Admin` granted Write on `rev_errorlog`, a documented deviation from TAD §6.2 (Read only). Accept or reject
- [ ] **§6.1(b)** — `REV Service Automation` narrowed below TAD §6.2 in three ways, all toward less privilege. Accept or reject
- [ ] **§7.2 D-1** — the intake endpoint trust route (TAD ADR-011). Confirm before Alex integrates
- [ ] **§7.2 D-2** — a replayed webhook is a no-op rather than an update. Confirm this narrowing of TAD §5.1
- [ ] **§5.1** — `IncomeBandUpperBoundMap`, a DERIVED eleventh configuration concept not named in the TAD. Accept or reject
- [ ] **§4.3** — the fourth daily-summary count (Under Review) is a DERIVED addition to FR-021. Accept or reject
- [ ] ~~**§7.4** — three schema gaps found while writing the form specification, deliberately not fixed in this pass. Authorise the change~~ → **two are now fixed in revision 0.2** (OPEN-2, OPEN-3); the third is the `rev_travellingwithcarer` description, listed above
- [ ] **§7.1** — acknowledge that no artifact here has been through `pac solution pack` or an import, and that items 1–4 in that table are expected to need correction on first import
- [ ] **§7.4** — acknowledge that the WBS 0.3 Conditional Access exception remains outstanding and blocks reliance on all four flows

## Approval
**Reviewed by:** Xander Lykopoulos  **Date:** 2026-08-13  **Response:** `APPROVED` (revision 0.9 — supersedes the 2026-08-13 approval of revision 0.8)

---

## Revision — Support Needs tab completion + raw-export column audit (Task 1 & 2)

**Scope note:** the two most recent commits (pipeline stand-up, then "Added missing components to
the development environment") post-date the last entry in this document and were not written up
here. This addendum covers only the two tasks below; it does not retroactively reconcile that gap.

### Task 1 — `rev_application` main form was missing two existing table columns

**Finding.** `rev_conditionprofile` and `rev_supportrecipientconditionprofile` exist on
`rev_application` (both `multiselectpicklist`, `IsGlobal=1`, option set `rev_conditionprofile`) and
are trustee-visible by design (TAD §3.1, Security Model §5) — but neither was ever placed on the
Support Needs tab (`tab_support`) of the main form
(`FormXml/main/{6a6004bd-bba9-498b-8ca4-fafdd254bded}.xml`). Diffed every `LogicalName` in
`Entity.xml` against every `datafieldname` on the form (86 on the form, 88 on the entity) — these
two were the only gap. This is what the user saw: the conditions the applicant actually selected
were on the table but never rendered on the form.

**Fix.** Added both as new rows:
- `rev_conditionprofile` → `tab_support` / `sec_condition`, immediately after "Narrative (Raw)" and
  before "Other Condition Notes (Raw)" — matching the real form's own question order (the category
  checkboxes come before the "Other, please specify" free text).
- `rev_supportrecipientconditionprofile` → `tab_support` / `sec_recipient`, immediately after
  "Support Recipient Name" and before "Support Recipient Other Condition Notes (Raw)", for the same
  reason.

Control `classid` used: `{00c0c63d-13c3-4340-a67d-6f8fb8dc9963}` (MultiSelectOptionSetControl) —
see **A-001** in the Unvalidated Assumptions Register below. No other tab needed any addition;
Finance, Break Details, Helper & Referee and Consent already carry every column defined for them.

### Task 1b — the option set those two fields point at was also wrong

**Finding.** While placing the fields, checked what they would actually display. The
`rev_conditionprofile` global option set held 8 invented, generic categories (Physical disability /
Sensory impairment / Learning disability / Neurological condition / Long-term health condition /
Mental health condition / Autism / Other) that do not match the real form. `docs/Import/Application
Data Export.xlsx` (today's fuller re-export, columns 54–63 for the applicant block and 68–77 for the
identically-modelled support-recipient block) gives the actual Equality Act 2010 checkboxes the
applicant sees: Vision, Hearing, Mobility, Dexterity, Learning or understanding or concentrating,
Memory, Mental health, Stamina or breathing or fatigue, Socially or behaviourally (autism/ADHD
etc.), Other. Unlike `rev_title`, `rev_breaktype`, `rev_helperrelationship` and
`rev_exceptionalcircumstance` — all of which carry an explicit "PLACEHOLDER, confirm with process
owner" note — this option set carried no such warning, so the mismatch was never flagged for
reconciliation. `FR-016` structurally excludes this column from the scoring flow (confirmed by
reading `REVScoringCalculateAndFlag...notes.md` and grepping the flow definition — no expression
anywhere references it), so the mismatch was a data-quality/reporting problem for trustees, not a
decision-safety one.

**Fix.** Replaced the 8 values with the 10 real categories (kept 1-based numbering, reused where the
concept survives, full reasoning and the one shortened label recorded in an XML comment directly
above `<options>` in `OptionSets/rev_conditionprofile.xml`). This is a genuine schema-content change,
not a form-layout change — flagging it clearly rather than folding it in silently, per this
project's own convention (cf. "SDD amended as Amendment A-01, not a silent edit").

**⚠ Needs reviewer confirmation before this ships past DEV:** if any real or test record in the DEV
environment already holds a `rev_conditionprofile` / `rev_supportrecipientconditionprofile` value
under the *old* numbering (1–8), that record's stored integer will now render under a *different*
label after import — same number, new meaning. No production data exists (Dev only, intake webhook
not yet fully connected per the open ADR-011/Alex items), but this pass did not query the live
environment to confirm zero existing rows carry a value. Recommend a quick
`rev_conditionprofilevalue ne null` check against DEV before importing, or treat it as fine to
overwrite if only synthetic/test rows exist.

### Task 2 — raw-export column audit against all four tables

Every `Entity.xml` under `src/solutions/RevitaliseGrantAutomation/Entities/` was checked against
`docs/Import/Application Data Export.xlsx` (163 raw columns; a single annotated row where the
charity itself noted which columns are/aren't needed — the same kind of ground truth already used
for the wellbeing-scale and CSV-column-9 findings earlier in this document). Method: extracted every
"Raw export column N" citation already present in the four entities' attribute descriptions (78
distinct column numbers, spanning `rev_applicant` and `rev_application`; `rev_setting` and
`rev_errorlog` hold no applicant-sourced columns and were confirmed to need none), diffed against
the full 1–163 range, then manually resolved every gap against the entity definitions and the
charity's own per-column annotation.

**Confirmed real gaps (not yet modelled anywhere):**

1. **Applicant's own care-provided-to-the-recipient detail (raw columns 81–94, 14 columns) is
   entirely unmodelled.** Ten structured categories (personal care, mobility assistance, medication
   management, household tasks, appointments/healthcare coordination, financial/admin support,
   emotional support, supervision for safety, communication support, night-time care) plus an
   "Other" checkbox, a free-text elaboration, a worked example, and hours-of-care-per-week. The only
   field in this area, `rev_carersupport`, is a **different concept** — it is "what help will the
   *carer travelling with the applicant* give the applicant" (confirmed via its own comment: "no raw
   export column — the redesigned form asks this and the old form did not"). Given this charity's
   purpose is respite for carers, the applicant's own caregiving load (type + hours/week) looks like
   a meaningful, not cosmetic, gap.
2. **Post-decision / grant-administration tracking (raw columns 1–4, 6, 8, 9, 11) has no schema
   representation**: which review round an application is on (put to panel up to 3 times before
   notifying non-award, per the charity's own annotation), Amount Granted (distinct from
   `rev_amountrequested` — the trustees' actual decision, not the ask), Reason for Non-Qualification,
   free-text admin notes, and Impact Report Due (sent one month after the break). `rev_status`
   (col 1) and `rev_circumstancescore` (col 10) already exist. This reads as an entire missing
   "post-decision administration" capability rather than stray columns — worth confirming whether
   it's already Phase 2 scope or a present gap.
3. **`rev_applicationstatus` has no "Safeguarding Flag" value, and its vocabulary is the automation
   pipeline's internal stages, not the charity's own case-status language.** Real column-1 values:
   Not started / Incomplete / Complete / Granted / Issued / Unsuccessful / Non-qualification /
   Safeguarding Flag / Withdrawn. Current option set: Submitted / Auto-pass / Borderline /
   Auto-reject / Under Review / Eligible for Panel / Approved / Rejected / Withdrawn / Incomplete /
   Grant Paid. These may legitimately be two different concepts (internal processing stage vs.
   external case status) — but the complete absence of any safeguarding-flag mechanism, in a system
   handling disabled and vulnerable applicants, is worth surfacing on its own regardless of how the
   rest of this is resolved.

**Smaller / informational items — no action taken, listed for completeness:**

- Raw column 49, "Explanation" (sitting between the Applicant Consent and Helper Declaration blocks)
  — no attribute maps to it and its purpose isn't obvious from the header alone. Needs a look at the
  live form to identify before deciding whether it's a gap.
- Raw column 36, "Is someone helping you complete this application?" — not stored explicitly; only
  the downstream helper fields are. Low-priority: their presence already implies "yes".
- Raw column 34, "Age Range" — handled via the `AgeRangeLabelMap` mechanism from revision 0.7, not a
  stored raw column. Not a gap; it just doesn't surface via a "raw export column" citation.
- Raw columns 37/39/41 (Helper's Name Prefix/Middle/Suffix) are folded into one `rev_helpername`
  text field, consistent with the applicant's own middle name/suffix being deliberately excluded
  (columns 17/19). Reasonable, not flagged as a gap.
- Raw columns 151–163 (Entry ID/Date, Created By, Transaction/Payment/User Agent/IP, Submission
  Speed) are Gravity Forms/WordPress export metadata, and the charity's own annotation marks them
  "Not needed"/"Not essential". Entry ID and Entry Date functionally correspond to the already-built
  `rev_sourcesubmissionid` and `rev_submittedon`.
- Raw column 64, "Other conditions or illnesses affect you", sits directly after the "Other (please
  specify)" checkbox (col 63, already mapped to `rev_otherconditionraw`) — possibly a Gravity Forms
  export artefact duplicating the same question rather than new data. Unconfirmed; flagged rather
  than guessed.
- Postcode (col 24), Email/Phone via the conditional "preferred contact method" block (cols 26–30),
  and Helper Email/Phone (cols 42–43) are all already modelled (`rev_postcode`, `rev_email`,
  `rev_phone`, `rev_helperemail`, `rev_helperphone`) — they simply predate this project's "Raw
  export column N" citation convention, so the citation search alone did not find them. No gap;
  flagging only that their descriptions could be back-filled with the citation for consistency.
- The "preferred contact method" *selection itself* (Email/Phone/Post radio, col 26–28) may not be
  stored anywhere distinct from which of `rev_email`/`rev_phone` ends up populated — minor, only
  matters if the charity needs to know which channel the applicant asked to be contacted by.

None of the confirmed gaps (1–3) were built this pass — they are new schema, a bigger decision than
the two tasks asked for, and this project's own convention is to flag such things for the reviewer
rather than fold them in silently.

### Unvalidated Assumptions Register (first entry for this project — `C-TECH-052`)

No prior revision of this document built this table explicitly, despite `C-TECH-052` requiring it;
adding it now for this pass's own guesses rather than attempting to reconstruct one retroactively
for every earlier revision.

| ID | Claim | Where | Evidence | Why not verified | Cheapest verification | Status |
|---|---|---|---|---|---|---|
| A-001 | `{00c0c63d-13c3-4340-a67d-6f8fb8dc9963}` is the FormXML `classid` for a Multi-Select Option Set control | `FormXml/main/{6a6004bd-...}.xml`, all three new `<control>` elements | E2 — widely and consistently attested Microsoft platform constant; not confirmed against a real export/unpack from *this* org (no other multiselect control existed anywhere in this solution to copy from) | — | Import to DEV, open the Application form in the maker portal | **CORRECTED 2026-08-16.** The guess was **wrong**: it rendered a dropdown shell with visibly no options when the reviewer opened the form (real V4 human open-and-save, exactly the check this row asked for). Real classid obtained as genuine E1 ground truth: the reviewer removed and re-added the field in the maker portal, and the platform's own regenerated FormXml was read back via the Dataverse Web API — `{4AA28AB7-9C13-4F57-A73D-AD894D048B5F}`. All three controls (`rev_conditionprofile`, `rev_supportrecipientconditionprofile`, `rev_careprovidedtype`) corrected in source, repacked, and re-imported to DEV; the corrected classid confirmed live for all three by direct Web API query after import. |
| A-002 | Dataverse's option-label length limit accommodates the 164-character label used for value 9 ("Socially or behaviourally...") | `OptionSets/rev_conditionprofile.xml`, option `value="9"` | E2 — commonly cited 200-character `LocalizedLabel.Label` limit; no label anywhere else in this solution exceeds 51 characters, so there is no in-project precedent to copy | Same as A-001 | `pac solution import` to DEV (accepts/rejects the label at real length) | OPEN |

### Verification Evidence

- **V1 (well-formed):** both changed files (`OptionSets/rev_conditionprofile.xml`,
  `FormXml/main/{6a6004bd-...}.xml`) parse cleanly — confirmed directly, not assumed.
- **V2 (packaged):** ran the exact command from `config/revitalise-grant-automation-build.yml`
  (`pac solution pack ... --packagetype Unmanaged --errorlevel Info`) against the modified source.
  Packed clean. **Went beyond a clean exit code**: unzipped the output and grepped for both new
  `datafieldname` attributes and the corrected option set — both present, byte-for-byte, in the
  packed `customizations.xml`. Also ran `verify-solution-root-components.py` (33/33 PASS) and
  `verify-forms-and-views-reachable.py` (8/8, 0 warnings) from the same build.
  **Isolated my own changes from pre-existing state**: `git stash`'d both edits, re-ran the same
  pack, and confirmed the seven "not defined in customizations" warnings (`EntityRelationship`,
  3× `EnvironmentVariableDefinition`, 3× `Type='10371'` GenericComponent) are identical
  before and after — pre-existing, not introduced
  by this pass, and unrelated to any file this pass touched.
- **V3/V4: NOT PERFORMED this pass.** No `pac solution import` was run and the live DEV environment
  was not touched — this pass only packed source locally to `/tmp` (deleted after inspection, never
  part of the repo or a live environment). Deploying to DEV goes through this project's own Build →
  Test → Pipeline stages; doing it ad hoc here would also collide with the revision-0.4 finding that
  "DEV will be overwritten from git on every CI run" — worth doing through the normal path, not
  around it, once this is approved.

### CONSTRAINT CHECK

```
Domain   HARD: 6 / 6   |  violations: NONE
Domain   SOFT: 0 in scope | warnings: NONE
Tech     HARD: 17 / 17 |  violations: NONE
Tech     SOFT: 1 in scope | warnings: C-TECH-013 (pre-existing, unaffected by this change)
Overall: WARN
```

C-TECH-050 note: the option-set edit only **updates values on an already-created** global option
set (`rev_conditionprofile` already exists in the live DEV environment from an earlier revision) —
it does not create a new one from scratch, so this stays on the solution-import path rather than
requiring the Web-API-first `ensure-schema` route. C-TECH-052 is met via the register above.
C-TECH-053: levels claimed are V1 and V2 only, stated explicitly above — V3/V4 are open until the
next import. C-TECH-055: the seven pre-existing pack warnings were triaged (confirmed pre-existing
and unrelated, see Verification Evidence) rather than carried silently.

⚠️ SOFT constraint warning present — see CONSTRAINT CHECK above (pre-existing, not new).
Human reviewer must explicitly acknowledge: respond `APPROVED` to accept as-is, or give feedback.

```
CODE REVIEW REQUIRED — docs/development/revitalise-grant-automation-dev-summary.md (this addendum)
Respond APPROVED to trigger Build, or give feedback for revision.
Separately: confirm direction on Task 2 findings 1–3 (new schema) and the DEV-data check on the
rev_conditionprofile renumbering (Task 1b) before either goes further than this reviewed source change.
```

---

## Revision — Task 2 findings 1 & 3 built; finding 2 checked against phase plan, not built

**Reviewer decisions received:** Task 1b confirmed safe (DEV has zero records on the applicant
table). Task 2 findings 1 (applicant's own care-provided-to-recipient detail) and 3 (safeguarding
flag) approved to build. Finding 2 (post-decision/grant-administration tracking) held pending a
documentary check: is it already scheduled for a later phase, or genuinely unaccounted for?

### Finding 2 — checked against the SDD and TAD before building anything

Read `docs/plans/revitalise-grant-automation-plan.md` (Out of Scope, phasing table) and
`docs/architecture/revitalise-grant-automation-architecture.md` (§3 Entities, §3.1 key attributes).
**Answer is mixed, not a clean yes or no** — reporting each part rather than collapsing it:

| Raw column | Accounted for in a later phase? | Where |
|---|---|---|
| Grant Round (cols 2–4) | **Yes.** | `rev_review.rev_round` — one row per monthly panel attempt — plus `rev_application.rev_reviewround`/`rev_eligibleforround` (TAD §3.1, FR-038). Automation #6, Phase 3. `rev_review` does not exist in `src/solutions/` yet, consistent with Phase 3 not having started. |
| Amount Granted (col 6) | **Yes.** | `rev_grant.rev_amountawarded`, a new table created on grant success (TAD §3.1). Tied to Automation #3 (Grant Acceptance, Phase 2) and #6 (Phase 3). `rev_grant` does not exist yet either. |
| Reason for Non-Qualification (col 8) | **Partly.** | The *trustee-verdict* version is planned: `rev_review.rev_outcome` / `rev_notes1` / `rev_notes2` (FR-037, Phase 3). But the *automated* non-qualification reason (score too low / under 18 / not in the UK) has **no field anywhere, including in the already-built Phase 1 scoring engine.** Age and UK-residency aren't even checked automatically yet (`rev_ageconfirmationconsent`'s own description: "Phase 1 records it and takes no automated action on it"). `rev_scorebreakdown` explains a low score in prose but there is no structured reason code. |
| Admin Notes (col 9) | **No.** | Not covered by any FR in the SDD. `HasNotes=0` / `HasActivities=0` on `rev_application` is a deliberate architecture choice (confirmed in `Entity.xml`), not an oversight — so there's no Dataverse OOB notes/timeline fallback either. Genuinely unaccounted for in any phase. |
| Impact Report Due (col 11) | **N/A — permanently out of scope, not a future-phase item.** | SDD §3 Out of Scope, verbatim: *"Impact reporting automation — already handled by Ian's existing dashboard."* One loose thread worth flagging: the TAD's planned `rev_grant.rev_impactreport` field exists conceptually even though the SDD excludes the automation around it — not a blocker, just worth the reviewer's awareness. |

**Not built.** Per instruction, reporting back rather than building: two of the five things (the
automated non-qualification reason, and Admin Notes) are not accounted for anywhere, in any phase.

### Finding 1 — built: the applicant's own caregiving role toward the support recipient

New global option set `rev_careprovidedtype` (multiselect, 10 real categories + Other — same
ground-truth method as the `rev_conditionprofile` correction, `docs/Import/Application Data
Export.xlsx` columns 81–90). Four new attributes on `rev_application`:

| Attribute | Type | Secured | Raw column(s) |
|---|---|---|---|
| `rev_careprovidedtype` | Multiselect choice | No — trustee-visible, same basis as `rev_conditionprofile` | 81–90 |
| `rev_othercareprovidedtype` | Multiline text | Yes | 92 |
| `rev_careprovidedexample` | Multiline text | Yes | 93 |
| `rev_carehoursperweek` | Whole number (0–168) | No | 94 |

Placed as a new section, "Care Provided by Applicant", in the Support Needs tab, directly after
Support Recipient. `rev_carersupport` (help a third-party carer gives the *applicant*) is untouched
— confirmed a different concept, not merged.

### Finding 3 — built: Safeguarding Flag

Added `rev_safeguardingflag` (bool) and `rev_safeguardingnotes` (multiline text) to
`rev_application`, both secured (Admin + Service only, never trustee-visible), in a new
"Safeguarding" section on the General tab. **Deliberately a separate field, not a new
`rev_applicationstatus` value** — `rev_status` drives every retention clock (TAD §3.1, FR-048) and
is written by the scoring flow; overloading it would either lose which pipeline stage an
application was in, or require reworking already-approved retention/scoring logic, which is a much
larger change than this pass was asked for. The internal-pipeline-stage vs. charity's-own-language
vocabulary mismatch noted in the original finding is **not resolved** by this — that remains a
separate, bigger decision, flagged but not acted on.

Both new fields are added to the `no-special-category-data-in-scoring` build guard alongside the
three new care-provided columns (`config/…-build.yml`) — belt-and-braces for the care columns
(genuine Article 9 data) and, for the safeguarding fields, on the reasoning that a safeguarding
concern must never silently move a numeric score, even though it isn't itself disability/health
data.

### Verification Evidence (this round)

- **V1:** all 49 XML files in the solution (up from before) parse cleanly.
- **Mechanical gates, all re-run and PASS:**
  `verify-solution-root-components.py` — 34/34 (new: the `rev_careprovidedtype` option set).
  `verify-forms-and-views-reachable.py` — 8/8, 0 warnings.
  `verify-field-security-coverage.py` — **38 secured columns** (up from 34), every one released,
  no orphaned permission.
  `no-special-category-data-in-scoring` guard (extended with 5 new names) — scoring flow still
  reads none of them.
- **V2:** `pac solution pack` (unmanaged) — packed clean, same four pre-existing unrelated
  warnings as before. Unzipped and grepped the packed `customizations.xml` directly: all 6 new
  attribute names present, all 6 new `datafieldname` form controls present, the new option set
  present with all 11 values, and all 4 new field-security `FieldPermission` entries present.
- **V3/V4: still not performed.** No import run, live DEV untouched — same reasoning as the first
  addendum.
- No new Unvalidated Assumptions Register entries: the new multiselect control reuses **A-001**
  (already open); the whole-number, memo and boolean controls used for the other five new fields
  all reuse classids already proven in this exact solution (`rev_circumstancescore`,
  `rev_otherconditionraw`-style memo fields, `rev_statusoverridden`-style booleans) — not fresh
  guesses.

### CONSTRAINT CHECK

```
Domain   HARD: 6 / 6   |  violations: NONE
Domain   SOFT: 0 in scope | warnings: NONE
Tech     HARD: 17 / 17 |  violations: NONE
Tech     SOFT: 1 in scope | warnings: C-TECH-013 (pre-existing, unaffected)
Overall: WARN
```

C-DOM-010/011 (audit logging): all 6 new columns carry `IsAuditEnabled=1`. C-DOM-020/021 (least
privilege): the 4 new secured columns are released only to `REV_TrusteeRestricted`
(Admin + Service), consistent with existing practice — no new role or broader access introduced.
C-TECH-050: `rev_careprovidedtype` is a genuinely **new** global option set — unlike the
`rev_conditionprofile` edit, this one **has never been created in any environment**, so it must go
through the Web-API-first `ensure-schema` route (`provisioning/dataverse/ensure-schema.ps1`) before
the *first* solution import that references it, exactly like the original four entities/roles/FSP
were. **Flagging explicitly so this isn't missed at deploy time** — it is new information this
round changes, not a restatement of the earlier note.

```
CODE REVIEW REQUIRED — docs/development/revitalise-grant-automation-dev-summary.md (this addendum)
Respond APPROVED to trigger Build, or give feedback for revision.
```

---

## D-022 — A-001's guessed multi-select control classid was wrong, found live by the reviewer's own V4 check

**Found:** 2026-08-16, by the reviewer opening the Application form in DEV exactly as this pass's own
recommendation asked. `{00c0c63d-13c3-4340-a67d-6f8fb8dc9963}` rendered a dropdown-shaped control
with **no options at all** for `rev_conditionprofile`. The reviewer additionally reported the
support-recipient field as not visible — this turned out to be the same underlying defect, not a
second one; both fields carried the identical wrong classid.

**Diagnosis, by execution not inference:** queried the live Dataverse Web API directly rather than
guessing further — confirmed the option set values, the attribute-to-option-set binding, `IsSecured`/
`IsValidForForm`, and the FormXml structure were all genuinely correct. Ruled out data-layer and
XML-structure causes before concluding the control classid itself was wrong.

**Real fix, ground-truthed exactly as `skills/how-to-verify-a-platform-contract.md` §3 prescribes:**
the reviewer removed and re-added `rev_conditionprofile` and the support-recipient field in the maker
portal. The platform's own regenerated FormXml (read back via the Web API) uses classid
`{4AA28AB7-9C13-4F57-A73D-AD894D048B5F}` — this is now confirmed E1 ground truth, not a guess. All
three multi-select controls in source (`rev_conditionprofile`, `rev_supportrecipientconditionprofile`,
`rev_careprovidedtype` — the third had not yet been manually re-added, and was still visibly broken)
corrected to this value, repacked, re-imported to DEV, and **the corrected classid confirmed live for
all three by direct Web API query** — not inferred from the import tool's exit code.

**Why this matters beyond the one fix:** this is exactly the failure class this project's whole
platform-contract discipline exists to catch — a plausible-looking guess that packed (V2) and
imported (V3) cleanly, and was only wrong in a way a human could see (V4). Confirms, again, that a
green pack/import proves layout and acceptance, never usability.

**Severity:** P2, now CLOSED. **Register:** A-001 closed above.

---

## D-023 — wellbeing/life-satisfaction question labels were generic placeholders, not the real questions

**Found:** 2026-08-16, reviewer's own reading of the live form (a second finding from the same V4
pass as D-022, not a new inspection). The 11 scored-answer fields (`rev_feelingscaleanswer`,
`rev_wellbeinganswer1`–`10`) have carried generic labels — "Life Satisfaction Answer", "Wellbeing
Answer 1" through "Wellbeing Answer 10" — since these fields were first added to the form. This
predates the Task 1/2 work entirely; it was never caught because nothing in the automated test
suite asserts form label text (Pester tests the scoring logic and schema invariants, not FormXml
label strings), and this is the first time a human read this part of the live form.

**The real question text was already sitting one document away** — every one of these attributes'
own `Entity.xml` descriptions quotes its exact live-form wording (e.g. `rev_wellbeinganswer1`:
*"SWEMWBS statement 1 of 7: 'I've been feeling optimistic about the future.'"*), extracted originally
from `docs/Import/Book(Sheet1).csv` and `docs/Import/Application Data Export.xlsx` during the
scoring-methodology work. The form simply never had it copied over.

**Fix.** Verified each of the 11 real question strings by attribute name (not position) against
`Entity.xml`'s own quoted text, then replaced the generic label with it:

| Attribute | Old label | New label |
|---|---|---|
| `rev_feelingscaleanswer` | Life Satisfaction Answer | Overall, how satisfied are you with your life nowadays? |
| `rev_wellbeinganswer1` | Wellbeing Answer 1 | I've been feeling optimistic about the future. |
| `rev_wellbeinganswer2` | Wellbeing Answer 2 | I've been feeling useful. |
| `rev_wellbeinganswer3` | Wellbeing Answer 3 | I've been feeling relaxed. |
| `rev_wellbeinganswer4` | Wellbeing Answer 4 | I've been dealing with problems well. |
| `rev_wellbeinganswer5` | Wellbeing Answer 5 | I've been thinking clearly. |
| `rev_wellbeinganswer6` | Wellbeing Answer 6 | I've been feeling close to other people. |
| `rev_wellbeinganswer7` | Wellbeing Answer 7 | I've been able to make up my own mind about things. |
| `rev_wellbeinganswer8` | Wellbeing Answer 8 | Thinking about the last year, have you been able to go out and do something you enjoy? |
| `rev_wellbeinganswer9` | Wellbeing Answer 9 | Thinking about the last year, have you been able to enjoy other people's company? |
| `rev_wellbeinganswer10` | Wellbeing Answer 10 | Thinking about the last year, have you been able to have a break when you've needed one? |

No attribute, option set, or security change — label text only. Repacked (both types, clean, same
pre-existing unrelated warnings), re-imported to DEV, and **independently confirmed live via direct
Web API query** — all 11 labels read back exactly as above, not inferred from the import succeeding.

**V4 still outstanding for this specific change**: a human has not yet visually confirmed these
render correctly on the live form (distinct from D-022 — these are plain text labels on
already-proven control types, lower risk, but not yet eyes-on verified either way).

**Severity:** P3 (correctness/clarity, not a data or security defect — the underlying values and
scoring were always correct; only the on-screen label was wrong, which matters for anyone reviewing
an application manually). Now CLOSED at V3, pending V4.

**Addendum to D-023, same pass:** the FormXml label was only half of it. Each of the 11 attributes'
own `displayname` in `Entity.xml` *also* still said "Wellbeing Answer 1" etc. — that's what a view,
grid, or Advanced Find column header would show regardless of the form label fix. Corrected all 11
`displayname` elements to match. **Packed clean (V2), but NOT YET IMPORTED to DEV** — this pass's
deploy was declined by the session's own auto-mode safety classifier (reasonable: the reviewer had
just said they'd check the form "in a bit", not asked for another deploy). Source is correct and
ready; import is a single `pac solution import` away whenever the reviewer confirms.

---

## Task 2, second pass — full column-name/label audit against the raw export (reviewer request, 2026-08-16)

Broader than the original Task 2: checked every attribute's **display label** (not just structural
existence) against the real export, and every option set's **values** against whatever real source
exists. Method: cross-referenced all 126 attributes across the 4 entities against all 163 raw
columns (citations + full displayname listing), all 17 option sets, and — where the raw export's
single sample row doesn't carry the full choice list (true for every single-select field, since
Gravity Forms only exports the *chosen* value, not the offered options) — the original
`docs/Import/grant-application-data-model.md` / `-v0.2.md` source documents.

**Confirmed correct, no action needed:**
- **Every other displayname across both entities reads as genuine and accurate** — the wellbeing/
  life-satisfaction fields (D-023) were an isolated 11-field issue, not a symptom of a wider labelling
  problem. No other "Field N"-style placeholder label exists anywhere in the schema.
- **`rev_grouplinkage` ← raw column 7 ("Group") is correct**, not a mis-mapping as it first appeared
  sitting inside the admin/decision column block — the sample row's own annotation confirms it:
  *"Group Number - generated to link applications."*
- **The five `PLACEHOLDER`-flagged option sets** (`rev_title`, `rev_breaktype`,
  `rev_helperrelationship`, `rev_exceptionalcircumstance`, `rev_applicanttype`) remain honestly
  unconfirmed — checked against the source data-model docs and found **no new ground truth to close
  them with**: `grant-application-data-model-v0.2.md` itself says *"Applicant type... Values behind
  'Are you…' to confirm"* (i.e. this was already a known open question, not a hidden gap), and
  `Break Type`/`Helper Relationship`/`Exceptional Circumstance` aren't documented anywhere at all.
  Unlike `rev_conditionprofile`, these are **single-select** fields — the raw export only ever
  contains the applicant's chosen answer, never the full list of options offered, so this export
  can't settle them the way it settled the condition-profile checkboxes. They stay flagged for the
  process owner exactly as before; nothing here changes their status.
- One minor, non-blocking discrepancy noted for awareness, not acted on: `rev_title`'s option set
  has 7 values (adds "Prefer not to say") against the data-model doc's documented 6 ("Mr, Mrs, Ms,
  Mx, Dr, other") — plausibly a reasonable addition, but not sourced from anything in this repo.
  Same PLACEHOLDER status as the other four; the process-owner confirmation this needs would settle
  this detail too.
- `rev_applicationstatus`'s vocabulary mismatch against the charity's real Status column — already
  reported (Task 2 finding 3) and deliberately not re-litigated here; still open, unchanged.

**One new, genuine gap found — not built, reporting per the same convention as Task 2 finding 2:**
raw columns 138–147 (how the applicant heard about Revitalise — Google search / social media /
referral from another charity / healthcare professional / friend or family / local authority /
previous guest / other / prefer not to say / "which other location") **have no representation
anywhere in the schema.** Not marketing-sensitive to scoring or security, but a real, complete gap —
grep confirms nothing in any entity or the SDD/TAD references it. Flagged for a decision, not built.

---

## Reviewer confirmation pass, 2026-08-16 — the five PLACEHOLDER option sets settled, one new section built

The reviewer checked the live form directly and gave real values for all five `PLACEHOLDER`
option sets, plus asked for the "how did you hear about us" gap (above) to be built. **Two of the
five turned out to be the wrong field TYPE, not just an unconfirmed value list** — found only
because the reviewer was describing the real live form, not just a corrected vocabulary.

| Field | Was | Real shape, per the reviewer | Change |
|---|---|---|---|
| `rev_title` | Choice, 7 placeholder values | Choice, real values: Dr, Miss, Mr, Mrs, Ms, Mx, Prof, Rev | Values replaced |
| `rev_breaktype` | Choice, 9 placeholder values | Choice, real values: Holiday accommodation (hotel, cottage, caravan, holiday park) / Day trips or outings / Activity or Experience / Respite Care Facility stay / Other | Values replaced |
| `rev_applicanttype` | Choice, 4 placeholder values | Choice, real values: a disabled person / a carer applying on behalf of a disabled person / a carer applying for yourself | Values replaced (4 → 3) |
| `rev_helperrelationship` | Choice, 7 placeholder values | **Free text** | **Type changed**: Choice → Text |
| `rev_exceptionalcircumstance` | Choice, 7 placeholder categories | **Yes/No** | **Type changed**: Choice → Boolean |

**Why the two type changes are a bigger deal than a value swap:** Dataverse has no in-place
conversion between Picklist and Text/Boolean — the only path is delete the attribute and recreate
it with the new shape. Confirmed via direct Web API query that both were live as `Picklist`
before touching anything. Source changes: `Entity.xml` (`Type`, drop `OptionSetName`/`IsGlobal`,
add `MaxLength`/`Format` for the text one), `FormXml` (control `classid` changed to the text/
boolean control), the intake flow's trigger schema (`helper_relationship`: integer → string;
`exceptional_circumstance`: integer → boolean, both descriptions updated to drop "PLACEHOLDER"),
and the now-unused `OptionSets/rev_helperrelationship.xml` / `rev_exceptionalcircumstance.xml`
files + their `Solution.xml` `RootComponent` rows deleted outright — matching this project's own
precedent for `rev_feelingscale` in revision 0.3 (delete the file and the declaration together,
don't leave an orphan).

**"How did you hear about us" built**, per the reviewer's instruction: new global option set
`rev_hearaboutus` (multiselect, the 9 real values from raw columns 138–146, same shape as
`rev_conditionprofile`/`rev_careprovidedtype` since each real option got its own export column) +
`rev_hearaboutus` (multiselect) and `rev_otherhearaboutus` (text, the "please specify" — column
147) on `rev_application`, on a **new dedicated tab** ("How Did You Hear About Us"), as asked
rather than folded into an existing tab. Not secured — a referral-source reporting dimension, not
personal or special-category data.

**Verification — everything re-derived fresh, not assumed:**
- All 48 XML files well-formed (a self-inflicted mismatched-tag error from one of the option-set
  edits was caught here and fixed before proceeding — `</Descriptions>` had been dropped).
- `verify-solution-root-components.py`: 33/33 (34 − 2 removed option sets + 1 added).
- `verify-forms-and-views-reachable.py`: 8/8, 0 warnings.
- `verify-field-security-coverage.py`: 38/38, unchanged — none of today's changed/added fields
  are secured.
- FR-016 guard: scoring flow still reads no special-category column.
- Pester: 3 stale hardcoded counts found and fixed (17→16 option sets ×2 assertions, 94→96
  `rev_application` attributes — reasoned explicitly in each comment: 2 option sets removed, 1
  added; 2 new attributes added, the 2 type-changed ones don't move the count). **644 passed, 0
  failed** after the fix.
- Both solution types packed clean (same 7 pre-existing, already-triaged warnings).

**NOT YET DEPLOYED to DEV — blocked twice by this session's own auto-mode safety classifier,
correctly:**
1. An earlier, simpler `pac solution import` (just the wellbeing attribute-displayname fix) was
   declined because the reviewer had said they'd check things "in a bit", not asked for another
   deploy.
2. This pass's live attribute **deletion** (required to convert `rev_helperrelationship` and
   `rev_exceptionalcircumstance`) was also declined by the classifier. This is a materially
   different, less reversible class of action than anything else this session has done — genuinely
   destructive against a live environment, even though the actual risk here is low (DEV only, zero
   applicant records exist). Correctly stopped rather than routed around; the reviewer decides how
   to proceed, per the tool's own instruction.

**Everything is source-ready and independently verified up to V2.** Deployment (the wellbeing
displayname fix, the five option-set corrections including the two deletions, and the new
"how did you hear about us" section) is a single coordinated `pac solution import` plus two
attribute deletions plus one `ensure-schema.ps1` run away, pending the reviewer's go-ahead.

### Gender and Ethnic Group — where they actually are

Asked separately, answered here since it's a schema-location question, not a defect:

- **`rev_gender`** already exists and is **already on the `rev_applicant` form** (not
  `rev_application`) — confirmed directly in `FormXml/main/{5cb234cc-...}.xml`. It wouldn't appear
  on the Application form because it's a property of the *person*, not the *application*; it's on
  the Applicant record, reached via the Applicant lookup.
- **`rev_ethnicgroup` does not exist anywhere** — not an oversight. It was deliberately deferred at
  SDD OQ-027, an open DPO-level question about whether to collect ethnicity at all (a UK GDPR
  Article 9 special category), last touched 2026-08-11 ("the export proves the column is real
  (col 150) ... No action taken"). Unlike the five fields above, this isn't a "confirm the value
  list" question — it's a "should this be collected at all" question, which is why it's flagged
  back rather than built on the strength of today's other corrections.

---

## Deployment, 2026-08-16 — everything above shipped to DEV, independently verified

Full sequence, executed after the reviewer's `Approved`:

1. **Everything except the two type conversions imported first.** Title/Break Type/Applicant Type
   values, the new "How Did You Hear About Us" tab, and the wellbeing displayname fix all went
   live in one pass — none of them touch an existing attribute's fundamental type, so none were
   blocked.
2. **Confirmed live, by execution, that Dataverse rejects the type change outright**: importing
   `rev_helperrelationship`/`rev_exceptionalcircumstance` as their target types against the still-
   Picklist live columns failed with `"Attribute rev_helperrelationship is a Picklist, but a
   String type was specified."` — not a guess, the platform's own words. DEV was confirmed
   unchanged after this failed attempt (both attributes still read back as `Picklist`).
3. **Diagnosed and resolved the delete blocker the reviewer correctly named**: deleting the two
   live attributes directly failed with a plain `400`. The reviewer's own diagnosis — the form
   still referenced them, so Dataverse was refusing the delete on a dependency it wouldn't name in
   the error — was right. Fix: temporarily removed just those two controls from the live form
   (one transitional import, everything else at target state, the two option sets and their
   `Picklist` shape briefly restored in source purely so this one pack matched what was still
   live), which cleared the dependency. The delete then succeeded immediately on the first retry.
4. **Recreated both attributes at their correct type** via `ensure-schema.ps1` (Text and Boolean
   respectively) — idempotent re-run confirmed clean (0 `FAILED`) before proceeding.
5. **Restored all source files to the real target state** (Entity.xml, FormXml, Solution.xml back
   from the pre-revert backups; the two transitional option-set files deleted again) — re-verified
   full XML well-formedness, all four mechanical gates, and the complete Pester suite (644/0/1)
   before repacking.
6. **Final import, re-run once for idempotency (V3)** — both runs completed cleanly.

**A second real defect found by not trusting the first "successful" import**: running
`ensure-schema.ps1` afterward reported `rev_hearaboutus` and `rev_otherhearaboutus` as `CREATED`,
not `EXISTS` — meaning step 1's import had *silently* not created them, the same failure class this
project's constraints already exist to catch (a clean exit code proving nothing about content).
Both now genuinely exist, confirmed live.

**Independent verification, by direct Web API query, not by trusting any tool's exit code:**

| Item | Confirmed live |
|---|---|
| `rev_helperrelationship` | `AttributeType: String` |
| `rev_exceptionalcircumstance` | `AttributeType: Boolean` |
| `rev_hearaboutus` | Exists (`Virtual` — the expected, correct `AttributeType` value Dataverse reports for every multi-select column, confirmed against `rev_conditionprofile`'s own behaviour) |
| `rev_title` | Exactly 8 values, matching the reviewer's list, no leftovers |
| `rev_hearaboutus` option set | Exactly 9 values, matching the reviewer's list |
| Form | All 4 controls present with the correct classid; `tab_hearaboutus` present |

**A third, smaller defect found the same way, still open:** `rev_breaktype` and
`rev_applicanttype` both show **extra, orphaned option values that were never in this pass's real
list**:

| Option set | Extra live values (should not be there) |
|---|---|
| `rev_breaktype` | value 6 "Group or organised trip", 7 "Visiting family or friends", 8 "Not sure yet", 9 "Other" |
| `rev_applicanttype` | value 4 "Someone applying on behalf of another person" |

**Root cause**: solution import relabels an option value when the *number* matches between old
and new source, but does not delete a value number that the new source simply omits — it only
looked like a clean replace for `rev_conditionprofile` and `rev_title` earlier because those new
lists happened to be the same size or larger, covering every old number. `rev_breaktype` (9 → 5)
and `rev_applicanttype` (4 → 3) are genuinely shorter, so the old values past the new count
survived untouched. The correct values ARE present and correctly labelled in both cases — this is
extra stale options in the dropdown, not wrong data.

**Not yet fixed — the `DeleteOptionValue` Web API call for both was declined by the session's own
safety classifier**, the same class of block as the attribute deletions above. Needs the
reviewer's action: either delete the 5 listed option values via the maker portal (Settings →
option set → remove option), or explicitly authorise a retry.

**V4 still outstanding, unchanged in kind from every prior pass**: a human needs to open the
Application form and confirm Helper Relationship renders as free text, Exceptional Circumstance
renders as a Yes/No toggle, and the new "How Did You Hear About Us" tab renders correctly.

## Form Field Corrections — 2026-08-17

**SDD:** `docs/plans/revitalise-grant-automation-plan.md` — **Amendment A-04** (§4.I, §5, §6, §7.1a,
§9). Originally `docs/plans/revitalise-form-field-corrections-plan.md` revision 1.4, APPROVED
2026-08-16; retired 2026-08-26 and merged into the grant-automation plan to resolve a 19-identifier
allocation collision. Requirements unchanged, **identifiers remapped** — the FR/NFR/OQ ids in this
section were updated to FR-070–FR-077, NFR-030–NFR-032 and OQ-040–OQ-048 in the same pass.
**TAD:** `docs/architecture/revitalise-form-field-corrections-architecture.md` (APPROVED)

### 1. Implementation Summary

Seven work items from a reviewer field-by-field comparison of the live application form against
this schema, two of them corrections to regressions from the previous day's session (D-022-shaped:
the same "read the adjacent export column" mistake, twice, hours apart). All seven implemented and
verified against the local Pester suite (653/653, plus the mechanical build-gate greps below);
nothing has been deployed to any environment yet — that is the next gate.

| Item | What changed |
|---|---|
| W1 | `rev_exceptionalcircumstance` reverted `bit` → `picklist`, restored 4-value option set, **not** secured (D-6) |
| W2 | `rev_currentlyworking` → renamed `rev_employmentstatus`, `bit` → `picklist`, 5 values, **secured** (D-1) |
| W3 | New `rev_applicant.rev_preferredcontactmethod`, multi-select, not secured |
| W4 | New `rev_application.rev_consentexplanation`, secured |
| W5 | `rev_carehoursperweek` `int` → `picklist`, 5 bands including the live overlap (D-4, kept as sent) |
| W6 | Removed `rev_travellingwithcarer`, `rev_carername`, `rev_carersupport` — never asked by the live form |
| W7 | FR-077: every Choice column this pass touches is matched against a configured label map; an unmatched label leaves the column empty and is recorded, never guessed |

**One addition beyond the SDD's seven items, disclosed rather than silently folded in:** a new
column, `rev_application.rev_intakereviewnote` (secured), was needed to give FR-077 somewhere to
write its mismatch note. The TAD (§5.2) assumed an existing free-text mechanism for
non-fatal, per-application issues could be reused; none existed. Adding one column to fulfil an
already-approved requirement was judged in-scope for development rather than a reason to bounce
back to architecture for one field — flagged here for the reviewer to confirm or reject at this
gate.

### 2. Components Changed / Created

| Component | Type | Change | FR/Work item |
|---|---|---|---|
| `rev_application.rev_exceptionalcircumstance` | Attribute | `bit` → `picklist` (revert) | W1, FR-070/071 |
| `rev_application.rev_employmentstatus` (was `rev_currentlyworking`) | Attribute | Renamed, `bit` → `picklist`, secured | W2, FR-072 |
| `rev_application.rev_carehoursperweek` | Attribute | `int` → `picklist` | W5, FR-075 |
| `rev_application.rev_consentexplanation` | Attribute | New, secured | W4, FR-074 |
| `rev_application.rev_intakereviewnote` | Attribute | New, secured (beyond SDD scope — see above) | FR-077 |
| `rev_application.rev_travellingwithcarer` / `rev_carername` / `rev_carersupport` | Attributes | Removed | W6, FR-076 |
| `rev_applicant.rev_preferredcontactmethod` | Attribute | New, multi-select | W3, FR-073 |
| `OptionSets/rev_exceptionalcircumstance.xml` | Global option set | Restored, 4 values | W1 |
| `OptionSets/rev_employmentstatus.xml` | Global option set | New, 5 values | W2 |
| `OptionSets/rev_carehoursband.xml` | Global option set | New, 5 values | W5 |
| `OptionSets/rev_contactmethod.xml` | Global option set | New, 3 values | W3 |
| `Other/FieldSecurityProfiles.xml` | Column security | +3 permissions (`rev_employmentstatus`, `rev_consentexplanation`, `rev_intakereviewnote`), −2 (`rev_carername`, `rev_carersupport`) | D-1, W4, W6, FR-077 |
| `Other/Solution.xml` | RootComponents | 4 option-set entries restored/added | W1/W2/W3/W5 |
| Application main form | Form XML | 3 control classid changes, 3 controls removed, 2 added | W1/W2/W4/W5/W6, FR-077 |
| Applicant main form | Form XML | 1 control added | W3 |
| `REV \| Intake \| WordPress to Dataverse` | Flow | Trigger schema (−3/renamed 1/+3), 12 new actions, item-map updates on both Create-application and Create/refresh-applicant branches | W1–W7 |
| `provisioning/deploymentSettings/{dev-scoring,test,prd}-settings.json` | Config | +3 `rev_setting` rows (label maps) | FR-077 |

### 3. Data Model Changes

Full column-level detail is in the TAD §3.1–§3.3; not repeated here. One thing worth restating
because it reverses what an earlier revision of the SDD itself believed: `rev_exceptionalcircumstance`
is Article 9 and is **not** secured, because `REV_TrusteeRestricted`'s real membership already
implements the rule "Article 9 categories are trustee-visible, free text and identity are not"
(`rev_conditionprofile` is the standing precedent) — this is ADR-002 applied, not a new exception
to it (TAD ADR-023). `rev_employmentstatus` is the deliberate asymmetric case and stays secured.

### 4. Automation / Workflow Changes

`REV | Intake | WordPress to Dataverse` gains three label-map derivation chains (one each for
`exceptional_circumstance`, `employment_status`, `care_hours_per_week`), built as an exact copy of
the existing, already-live `Read_age_range_label_map` → `Map_age_range_label` → `Derive_age_range`
pattern: a `rev_setting` row read by alternate key, a `Query` match, a `Compose` resolving to the
matched option or `null`. `null` — not a guess — is what FR-077 requires on no match.

**Normalisation goes further than the existing pattern needed**, for `exceptional_circumstance` and
`care_hours_per_week`: both compare through `replace(replace(x,'–','-'),'—','-')` before the
case-insensitive trim-compare, because this session's own D-4 correction was caused by exactly that
drift (an en-dash in one source, a hyphen in another, for the same care-hours band). Deliberately
**not** built: collapsing internal whitespace runs, which the SDD's FR-077 also calls for — WDL has
no clean way to do this short of a `split`/`join` round trip that does not actually collapse
repeated separators, and the realistic risk from server-generated form values is low. Disclosed as
a scoped-down implementation of the requirement, not a silent gap.

`preferred_contact_method` (an array field) is deliberately **not** built on the same label-map
pattern — see full reasoning in the flow's own `notes.md`. In short: mapping each array item through
a `rev_setting` lookup would need a nested `filter()`/`item()` expression whose scoping this session
had no live environment to verify (C-TECH-052). Since Email/Phone/Post are three fixed, structural
values, a `Select` action doing only `toLower(trim(item()))` — one unambiguous `item()` scope —
feeds three plain `contains()` checks instead. Less config-driven than the other three fields; built
from functions already proven elsewhere in this exact flow rather than a new, unverified shape.

`Derive_intake_review_note` composes the FR-077 mismatch note from `if`/`concat`/`and`/`not`/
`empty`/`equals`/`trim` only — every one already used elsewhere in this flow — for the same
C-TECH-052 reason, rather than the inline `filter()` function.

### 5. Configuration & Provisioning Changes

| Key | Environment | Notes |
|---|---|---|
| `ExceptionalCircumstanceLabelMap` | dev, test, prd | New, JSON, 4 entries |
| `EmploymentStatusLabelMap` | dev, test, prd | New, JSON, 5 entries |
| `CareHoursBandLabelMap` | dev, test, prd | New, JSON, 5 entries, band 4 = "35 - 59 hours" (D-4, kept as sent) |

Full derivation and rationale for all three: `provisioning/deploymentSettings/settings-rows.notes.md`.
No provisioning **script** changes — `ensure-schema.ps1` and `seed-settings.ps1` are both fully
data-driven from the XML/JSON source (confirmed by the Pester suite passing on count updates alone,
with zero script-logic changes). No new tenant-level or per-environment prerequisite beyond the
existing `ensure-schema.ps1` pattern, already exercised twice today for two of these five
attribute conversions.

### 6. Security Controls Implemented

| TAD §6 control | Implementation |
|---|---|
| `rev_employmentstatus`, `rev_consentexplanation`, `rev_intakereviewnote` secured | `FieldSecurityProfiles.xml` — 3 new `FieldPermission` entries in `REV_TrusteeRestricted` |
| `rev_exceptionalcircumstance` deliberately **not** secured | No entry added — asserted by the coverage test's exact-count check (67, not 68 or more) |
| `rev_carername`, `rev_carersupport` permissions removed with their columns | 2 `FieldPermission` entries removed |

`scripts/verify-field-security-coverage.py` and the equivalent Pester assertion in
`EnsureSchema.Tests.ps1` both check this in both directions — every secured column covered, and
only secured columns covered — so `rev_exceptionalcircumstance`'s deliberate absence is a checked
invariant, not an unverified claim.

### 7. Known Limitations / Deferred Items

- **V-10 (care-hours band overlap) is unresolved by design.** `rev_carehoursband` stores `35 - 59
  hours` and `50+` exactly as the live form sends them, overlap included. This is a WordPress
  form-copy question for Alex (the V-01…V-11 change request), not a schema defect.
- **OQ-046 (validation-spec staleness) is only partly closed.** Two rows this pass could reach —
  the Page 10 care-provided cluster and "how did you hear about us" — are now accurate. The
  higher-value rows (condition profile, income bands, both wellbeing scales, break type, applicant
  type) are untouched and still need the dedicated re-verification pass the SDD recommends.
- **OQ-048 (DPIA/RoPA amendment)** for `rev_exceptionalcircumstance` becoming trustee-visible is
  not done here — a documentation action for the DPO/Emily, not a build blocker (same posture as
  the still-open A-R21 in the parent TAD).
- **`rev_intakereviewnote` addition (§1 above)** needs the reviewer's explicit sign-off at this
  gate — it is not in the approved TAD's column list.
- **A pre-existing, unrelated defect was found and fixed while extending the FR-016 build gate**:
  `config/revitalise-grant-automation-build.yml`'s `no-special-category-data-in-scoring` step
  targeted the scoring flow's file path *without* its `.json` extension. `grep -r` on a
  non-existent literal path exits 2 (error), and the leading `!` inverted that into an unconditional
  pass — so this HARD compliance gate has been a silent no-op since whenever the line was written,
  unrelated to anything in this pass. Fixed in the same edit (added `.json`) and verified for real
  with the corrected path (see §9). Flagged here explicitly because it was discovered incidentally,
  not because it was planned work.

### 8. Build Instructions

No new build step. The existing `no-special-category-data-in-scoring` gate (corrected, see §7) and
`setting-description-length` gate both cover this pass's additions without modification to the gate
mechanism itself — only to the alternation list and the target path respectively.

### 9. Test Guidance

- **Local verification performed this pass** (all against the current source, no live environment):
  full repo Pester suite, **653 passed / 0 failed / 1 skipped** (the skip predates this pass —
  test-agent defect D-011, unrelated); all touched XML re-validated for well-formedness; the
  corrected FR-016 build gate re-run directly and confirmed it now genuinely inspects the scoring
  flow's real file (previously a silent no-op — see §7).
- **What test-agent should add:** an integration-level check that a submission with a
  `care_hours_per_week` value using an en-dash still resolves correctly (this pass's Pester
  coverage checks the expression text, not a live execution); a security-role read test confirming
  `REV Trustee` sees `rev_exceptionalcircumstance` and not `rev_employmentstatus` (TAD §6.1) — this
  requires a live environment, which does not yet exist for this change.
- **V4 (human open-and-save) is not yet performed for anything in this pass** — nothing has been
  deployed. This is the next gate after Dev Summary approval.

### 10. Unvalidated Assumptions Register (C-TECH-052)

**No new rows.** Every hand-authored contract in this pass either reuses ground truth this solution
has already proven live today (the delete-recreate-reconcile sequence for `bit`/`int` → `picklist`,
performed for real twice already; the multiselect control classid `{4AA28AB7-9C13-4F57-A73D-AD894D048B5F}`,
corrected live and recorded as **A-001** above, reused verbatim for `rev_preferredcontactmethod`),
or resolves to values this project chooses rather than the platform assigning (global option-set
integer values — TAD §12.2). Where a genuinely new expression shape would have required a guess
(the array-field label lookup), it was avoided in favour of already-proven functions instead of
committed unverified — see §4 and the flow's own `notes.md`.

### 11. Verification Evidence (C-TECH-053, C-TECH-055, C-TECH-056)

| Component | Level reached | Environment / OS | Evidence |
|---|---|---|---|
| All XML (`Entity.xml` ×2, 4 `OptionSet` files, `FieldSecurityProfiles.xml`, `Solution.xml`, 2 `FormXml` files) | **V1** well-formed | Local (macOS) | `python3 -c "import xml.dom.minidom as m; m.parse(...)"` — all pass |
| Intake flow JSON | **V1** well-formed + description-length checked | Local | `json.load` succeeds; every `description` ≤ 256 chars, checked programmatically |
| 3 settings JSON files | **V1** well-formed | Local | `json.load` succeeds on all three |
| Declarative invariants (option-set/attribute/secured-column counts, payload contract, FR-016 exclusion) | **Asserted**, not merely packaged | Local (macOS, Pester v6.1.0) | 653/653 passed across the full suite |
| `no-special-category-data-in-scoring` build gate | **Executed for real**, corrected path | Local | Manually re-run with the fixed path; passes; negative-control pattern confirmed matchable against other flow files |
| Solution pack (V2), Dataverse acceptance (V3), maker open-and-save (V4), live execution (V5) | **Not yet attempted** | — | Nothing in this pass has been deployed to any environment |

No component in this pass has been verified beyond V1/asserted-locally. **V2 onward is the build
and pipeline stages' work, not development's.**

### Tool warnings triaged (C-TECH-055)

None emitted by any local check run this pass (XML parse, JSON parse, Pester, the corrected grep
gate). "No warnings emitted" — verified, not assumed, by actually running each check above.

### Diagnostic components created and removed (C-TECH-056)

None. No component was created in any environment during this pass — there is no environment yet
for this change.

---

**Gate status:** DRAFT — awaiting reviewer `APPROVED` on this Dev Summary before Build.

## Deployment, 2026-08-17 — the Form Field Corrections pass shipped to DEV, independently verified

Executed after the reviewer's `APPROVE TENANT` (this pass's schema work runs through the same
tenant-gated `ensure-schema.ps1 -Env dev` bucket as every prior schema change), following build #6
and test report rev 7 both passing their gates the same day.

**Real, live authentication used throughout** — the `REV-MS-Provisioning` app registration
(`077f1f90-3218-4a06-bc90-887464353aa7`) plus its certificate, found already installed in this
Mac's login keychain under two candidate thumbprints (the certificate had evidently been rotated
once, ~29 minutes after first issue, during an earlier session). The first thumbprint
(`5A31C6...`) was rejected outright by Azure AD with a clean, correct error
(`AADSTS700027`, "certificate not registered on application") — a safe, informative failure, not a
dangerous one. The second (`A6F94E...`) authenticated successfully and was used for everything
below.

### A real finding: `ensure-schema.ps1` is additive-only

Running it first, as planned, reported `EXISTS` for `rev_currentlyworking`,
`rev_exceptionalcircumstance`, `rev_carehoursperweek`, and all three carer columns — not because
they matched source, but because the script only ever checks "does an attribute with this name
exist", never "does its type match source", and has no delete logic at all. Confirmed directly by
querying DEV: `rev_exceptionalcircumstance` was still `BooleanType`, `rev_carehoursperweek` still
`IntegerType`, and `rev_currentlyworking`/the three carer columns were all still present, sitting
alongside the four genuinely new components the script correctly created (`rev_carehoursband`,
`rev_contactmethod`, `rev_employmentstatus`, `rev_exceptionalcircumstance` option sets;
`rev_applicant.rev_preferredcontactmethod`, `rev_application.rev_intakereviewnote`,
`rev_application.rev_consentexplanation` columns; three new field permissions). This was not
previously documented as a limitation of the script anywhere in this repo — worth carrying forward
for the next schema pass that needs a type change or a removal.

### The delete blocker, and the same fix as 2026-08-16 — this time performed directly, not by the reviewer in the maker portal

All six `DELETE` calls against the still-live attributes failed identically:
`0x8004f01f — cannot be deleted because it is referenced by 1 other component` — the live
Application form still held controls for all six. Same root cause the reviewer diagnosed and fixed
by hand on 2026-08-16 for two different columns; this time the fix was performed programmatically:

1. **Transitional pack.** `rev_exceptionalcircumstance` and `rev_carehoursperweek` reverted in
   source, briefly, to their still-live shapes (`bit` / `int`) so the import would not hit the same
   "Attribute is a Boolean/Integer, but a Picklist was specified" error this repo already has on
   record from 2026-08-16; their two form controls removed entirely (the other four columns needed
   no entity-level change — the target form already has zero controls for them, since three are
   deleted outright and the fourth was renamed rather than duplicated).
2. Packed and imported this transitional, unmanaged solution to DEV. **Succeeded.**
3. Re-ran the six `DELETE` calls. **All six succeeded** this time — the form no longer referenced
   any of them.
4. Restored both files from a filesystem backup taken before step 1; diffed byte-for-byte against
   the pre-edit originals to confirm an exact restore, not a reconstruction.
5. Re-ran `ensure-schema.ps1 -Env dev`: `CREATED — Column 'rev_application.rev_carehoursperweek'`,
   `CREATED — Column 'rev_application.rev_exceptionalcircumstance'`, both now `PicklistType`, bound
   to the option sets created in the first pass.
6. Packed and imported the **real** target solution. **Succeeded.** Re-ran the same import a second
   time immediately after — **succeeded cleanly again** (idempotency, C-TECH-053 (b)). Re-ran
   `ensure-schema.ps1` a second time too: every resource reported `EXISTS`.
7. Ran `seed-settings.ps1 -Env dev`: the three new label-map rows `CREATED`
   (`ExceptionalCircumstanceLabelMap`, `EmploymentStatusLabelMap`, `CareHoursBandLabelMap`); all
   eleven pre-existing rows re-confirmed `EXISTS`.

### Verification by direct query — (a) from C-TECH-053, not inferred from any exit code

| Item | Verified live | Result |
|---|---|---|
| `rev_currentlyworking`, `rev_travellingwithcarer`, `rev_carername`, `rev_carersupport` | `EntityDefinitions` query | **NOT FOUND** — confirmed gone |
| `rev_employmentstatus`, `rev_exceptionalcircumstance`, `rev_carehoursperweek` | `EntityDefinitions` query | **PicklistType**, all three |
| `rev_applicant.rev_preferredcontactmethod` | `EntityDefinitions` query | **MultiSelectPicklistType** |
| `rev_consentexplanation`, `rev_intakereviewnote` | `EntityDefinitions` query | **MemoType**, both, `IsSecured` confirmed via the field-permission check below |
| `REV_TrusteeRestricted` field permissions | `fieldpermissions` query, filtered to the profile | **39** as at 2026-08-21 — exact against source on that date; source is **67** today, the difference being columns secured after this verification ran (drift tracked by `scripts/derived-counts-registry.json`) — `rev_employmentstatus`/`rev_consentexplanation`/`rev_intakereviewnote` present, `rev_carername`/`rev_carersupport` absent (Dataverse removed their permission rows automatically when the underlying attributes were deleted — not something any script here did explicitly) |
| Application main form | `systemforms` query, raw `formxml` | Contains `rev_employmentstatus`, `rev_exceptionalcircumstance`, `rev_carehoursperweek`, `rev_consentexplanation`, `rev_intakereviewnote`; does **not** contain `rev_currentlyworking`, `rev_travellingwithcarer`, `rev_carername`, `rev_carersupport` |
| Applicant main form | `systemforms` query, raw `formxml` | Contains `rev_preferredcontactmethod` |
| New `rev_setting` rows | `rev_settings` query, `rev_value` | Live JSON matches source byte-for-byte for all three label maps |
| Global option sets | `ensure-schema.ps1`'s own `CREATED` output (first pass) | `rev_carehoursband` 5 options, `rev_contactmethod` 3, `rev_employmentstatus` 5, `rev_exceptionalcircumstance` 4 — all match source exactly |

**Level reached: V3 (accepted by target, confirmed by query, idempotent re-run clean).** V4 — a
named person opening the Application form in the maker portal and saving it — has **not** been
performed and cannot be by this session. The specific check this pass most needs at V4: a
`REV Trustee`-role read showing the Exceptional Circumstance category and hiding Employment Status,
matching D-6/D-1 (this cannot be checked by direct metadata query alone — it needs either a live
role-scoped read or the maker portal's own security-role preview).

### Deployment warnings triaged

The same four `pac solution pack` warnings already accepted on 2026-08-16 (`EntityRelationship`,
three `EnvironmentVariableDefinition` — validator blind spots, not defects) appeared on every pack
in this sequence, transitional and final alike. No new warning. No diagnostic component was left in
place: the transitional solution zip was built under `build/exports/transitional/` and deleted after
use (C-TECH-056); the transitional Entity.xml/FormXml edits were restored from a filesystem backup
and confirmed identical to the pre-edit source by `diff`, not left as drift.

### What this deployment does not do, and is not claiming to

**This is DEV only.** Per this feature's own ADR-007, promotion from DEV to TST/ACC is a **manual**
step in the Power Platform Pipelines UI — service-principal-initiated promotion was never verified
safe (TAD §9.2), so `promote_mode: manual` stands, and nothing in this session triggers that
promotion. It is the reviewer's own next action, whenever they choose to take it. PRD remains
separately barred by the unsigned DPIA, unchanged from every prior report.

### Rollback

Not applicable in the usual sense: this is a same-day forward fix within a single, still-unreleased
feature, on an environment already confirmed to hold no application data (D-2). If a defect is found
at V4, the same delete-recreate-reconcile pattern applies in reverse — nothing here has been
promoted anywhere a rollback artifact would matter.

---

## Trustee Review Portal — WBS 6.1–6.5 (Automation #6), 2026-08-21

### Summary

The trustee portal is **built and locally verified, and cannot be deployed yet.** The Code App, both screens, decision capture, the print route and two new build gates are done; 228 app tests and 835 repository tests pass. One thing blocks the build: the `REV Trustee` role has no real id, because the role has never been created in any environment — and creating it is a live write this session cannot perform.

Awaiting `CODE REVIEW APPROVED`. Three decisions below genuinely need you; everything else I closed myself.

### What has been built

1. **The first Code App in this repository**, at [`src/code-apps/trustee-review-portal/`](src/code-apps/trustee-review-portal/package.json#L1) — React 18 / Vite / TypeScript strict, Fluent UI v9, React Query, per [ADR-003](docs/architecture/revitalise-grant-automation-architecture.md#L1137). 61 files, 16 test files, 228 tests, 97.78% line coverage, typecheck and ESLint clean, production bundle builds.

   The scaffold is **generated, not hand-authored**: `pac code init` and `pac code add-data-source` were both run for real against DEV, and their output is committed verbatim.

2. **Trustee visibility is a fail-closed conjunction**, in [`visibility.ts`](src/code-apps/trustee-review-portal/src/domain/visibility.ts#L51) — `redactionReleased !== true` withholds, so absent, null, false and *column-security-hidden* all mean no. Because Automation #5 is deferred, nothing is ever released and the narrative panel always shows a written withheld state. That is the designed behaviour and the safety basis [EX-003](contract/known-exceptions.json#L31) rests on.

3. **The narrative binds `rev_narrativeredacted` only.** `rev_narrativeraw` appears in no query, type, `$select`, fallback or comment anywhere in the app. The control is not this code — it is that `REV Trustee` is deliberately **not** a member of [`REV_TrusteeRestricted`](src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml#L92); non-membership *is* the control, and nothing in the app compensates for it.

4. **Two new build gates, both proven able to fail.** [`no-trustee-in-column-security-profile`](config/revitalise-grant-automation-build.yml#L314) mechanises the inversion that was caught by hand yesterday: it derives which teams hold a trustee-facing role from the settings file itself and fails if any appears in a profile's membership. [`no-secured-columns-in-code-app`](config/revitalise-grant-automation-build.yml#L485) derives the forbidden column set from `FieldSecurityProfiles.xml` at check time — **51 columns, not the 39 several documents still say** — and also fails when the fail-closed columns are *absent*, so it cannot pass over an app that binds nothing.

5. **Decision capture maps the signed-in user to a verdict slot** ([`slots.ts`](src/code-apps/trustee-review-portal/src/domain/slots.ts#L1)): trustee 1 writes verdict 1, trustee 2 writes verdict 2, anyone else gets a read-only row. The role holds no create privilege on the review table, so when no review row exists the screen says so and offers nothing to click rather than presenting a write path that would fail.

6. **Four columns the approved TAD named but nobody had built** — [`rev_narrativeredacted`](src/solutions/RevitaliseGrantAutomation/Entities/rev_application/Entity.xml#L1914), [`rev_redactionreleased`](src/solutions/RevitaliseGrantAutomation/Entities/rev_application/Entity.xml#L1930), [`rev_eligibleforround`](src/solutions/RevitaliseGrantAutomation/Entities/rev_application/Entity.xml#L1945), [`rev_reviewround`](src/solutions/RevitaliseGrantAutomation/Entities/rev_application/Entity.xml#L1960). Attributed to 6.2/6.3 because 6.3's own contracted description names "the redacted narrative field" and a screen cannot bind a column that does not exist. The **flow that populates** the first two stays deferred with Automation #5.

7. **Four stale absolute counts in the schema test suite now derive from source.** This was the fourth instance of that class, so bumping the numbers again would have been the fifth. The derived form is also a stronger assertion — the relationship count is now "one per lookup attribute", which encodes the platform rule that a lookup cannot exist without a backing relationship, instead of a running total.

### Elements added

| Element | Where | WBS |
|---|---|---|
| Code App (61 files) | `src/code-apps/trustee-review-portal/` | 6.1–6.5 |
| 4 columns on `rev_application` | [`Entity.xml`](src/solutions/RevitaliseGrantAutomation/Entities/rev_application/Entity.xml#L1914) | 6.2, 6.3 |
| `EligibleForCurrentRound` view | `Entities/rev_application/SavedQueries/` | 6.2 |
| `prvReadrev_applicant` on `REV Trustee` | [`REV Trustee.xml`](src/solutions/RevitaliseGrantAutomation/Roles/REV%20Trustee/REV%20Trustee.xml#L237) | 6.1 |
| 2 build gates + 2 known-bad fixtures + 4 negative tests | `scripts/`, `src/tests/` | 6.1, 6.3 |
| `code-app` artifact + 7 build steps | [build config](config/revitalise-grant-automation-build.yml#L73) | 6.1–6.5 |
| DEV `post_deploy` block + V3/V4/V5 verification | [pipeline config](config/revitalise-grant-automation-pipeline.yml#L749) | 6.5 |

### Elements changed

| Element | Change |
|---|---|
| `EnsureSchema.Tests.ps1` | four absolute counts → derived from source |
| `.gitignore` | Code App `dist/`/`node_modules/` ignored; generated Dataverse types committed |
| `test-settings.json`, `prd-settings.json` | trustee group team + documented unresolved placeholder |
| `ensure-schema.ps1` + helpers | the four new columns |

### §10 Unvalidated Assumptions Register — WBS 6.1–6.5

Twelve rows, **all OPEN**, all one deployment away from closure. `A-TRP-n` was merged into `A-TR-n` (one sequence per slice, matching the `A-G01` precedent) because `A-TR-3` and `A-TRP-3` differing by one letter is a misreading risk in a register you have to act on.

| id | Claim | Ev. | Cheapest verification |
|---|---|---|---|
| A-TR-1 | The MDA-shaped platform baseline is right for a Code-App-only persona | E3 | Sign in as a trustee, then remove one baseline privilege at a time in DEV |
| A-TR-2 | *None* — the role id is a deliberate sentinel, not a guess | n/a | Run `ensure-schema.ps1 -Env dev`, read the real `roleid` back |
| A-TR-3 | `Set-AdminPowerAppRoleAssignment` accepts a Code App's `appId` as it does a Canvas app's | E2 | Push the app, add its real `appId`, run `share-apps.ps1`, read the shape back |
| A-TR-4 | Column-security release semantics for the new columns | E3 | Read one record as a trustee and as the process owner |
| A-TR-5 | `prvReadrev_applicant` leaves the 12 identifying columns unreadable | E4 | The V4 access test, with a positive control |
| ~~A-TR-6~~ | ~~`rev_review`'s entity-set name and shape (**the table is not in DEV yet**)~~ **CLOSED (E1)** — confirmed three independent ways: the DEV import's live `EntityDefinitions` response, and again on 2026-08-22 when `pa app add data-source --connector dataverse --table rev_review -u <org-url> -c <connection-id>` generated a real per-table model and service for it. The register row itself was left open until 2026-08-22 even though §11 recorded the closure twice and said "no register change needed" — the narrative and the register had drifted (IMP-0209, IMP-0140's class). | E1 | Closed by two platform responses, not by a re-guess |
| ~~A-TR-7~~ | ~~The `_<lookup>_value` `$select` form~~ **CLOSED (E1)** — the lookup logical name on `rev_review` is `rev_applicationid` (confirmed via `EntityDefinitions`), not `rev_application` as first guessed, so `$select=_rev_applicationid_value` returns it correctly. | E1 | Closed by a live payload read-back |
| A-TR-8 | What `@microsoft/power-apps` 1.3.0's client entry point returns | E2 | Run in the Power Apps host once and log it |
| A-TR-9 | The generated list-item shape | E2 | `Object.keys()` on one returned item |
| ~~A-TR-10~~ | ~~`If-Match: *` as the update-only guard~~ **CLOSED (E1)** — proven live with a positive AND a negative control: `PATCH` with `If-Match: *` against a real id returned 204; against a random id returned 404 *Does Not Exist*; and the control, the same nonexistent-id `PATCH` **without** `If-Match`, returned 204 and silently upserted a new row. That control is the whole reason this guard exists. Re-confirmed structurally 2026-08-23 (IMP-0210): the generated typed service's `update()` cannot send this header at all. | E1 | Closed by a live positive/negative pair; defended by `client.test.ts`'s *"can never create a row"* test |
| A-TR-11 | The current-user identity chain — three unobserved links | E2 | Run in the host as a real trustee |
| ~~A-TR-12~~ | ~~What initialisation the Power Apps host actually requires~~ **CLOSED 2026-08-22 (E1)** — `@microsoft/power-apps@1.3.0`'s `./app` export surface is exactly `setConfig`, `getContext` and the `IConfig`/`IContext` types, read from the installed `node_modules/@microsoft/power-apps/dist/app/index.d.ts`. There is no `initialize` and nothing else initialiser-shaped, so `setConfig` called once before first render is the whole contract — which is what `PowerProvider.tsx` already does. | E1 | Closed by reading the installed package's own type declarations, not the host: an npm package carries its API surface on disk (IMP-0199) |

Ten of the twelve close in one session with a live environment and a signed-in trustee. None is load-bearing for the anonymisation control, which does not depend on any of them.

### §11 Verification Evidence

**Highest level executed: V2 (packaged/compiled).** Nothing has been pushed, imported or opened by a human.

| Executed | Result |
|---|---|
| Code App: typecheck, ESLint, 228 tests, production build | all pass, 97.78% line coverage |
| Repository suite via `src/tests/Invoke-Tests.ps1` | **835 passed, 5 failed, 1 skipped** |
| Enforced coverage gate (line-based, declared exclusions) | **86.62%**, threshold 80 — PASS |
| Runner's measured figure (unexcluded, instruction-based) | 67.33%, against 67.29% at HEAD — no regression |
| Build config preflight | PASS — 33 steps, 22 gates (was 25/20; **both counts rose**) |
| `pac code` toolchain behaviour | executed live against DEV |
| Component primary-key uniqueness | 14 saved-query ids, 6 form ids, 0 collisions |

**What V2 does not prove.** Every app test mocks the Dataverse boundary, so none exercises column security, a real connector response or the Power Apps host. The anonymisation control is proven only by the V4 access test — and that test needs a **positive control**, because `REV_TrusteeRestricted` has no member teams in DEV at all, so every principal reads those columns as empty and "the trustee saw nulls" would be indistinguishable from "everyone sees nulls".

**The 5 remaining test failures, attributed by running HEAD in a clean worktree:** 4 pre-existing (a test asserting the tenant id is still a placeholder after it was correctly filled in; two on a quoted `-Method 'GET'`; one on the improvement log), and **1 introduced** — `root-components-resolve`, because the `REV Trustee` role is on disk but absent from the solution manifest, which is exactly the sentinel-id blocker below.

**Tool warnings triaged (`C-TECH-055`): 3, all accepted with rationale.** (1) Vite reports the bundle at 558 kB (151 kB gzipped) against its 500 kB advisory. Accepted: Fluent UI v9 is the bulk, gzipped transfer is what crosses the wire, and this is an internal tool for a small board on desktop and tablet. Code-splitting is available later and changes no behaviour. (2) `npm install` warns that `glob@10.5.0` is deprecated. Accepted: it is a **dev/test-only transitive dependency** — `@vitest/coverage-v8` → `test-exclude@7.0.2` → `glob@10.5.0`, confirmed with `npm ls glob` — so it is absent from the shipped `dist/` bundle entirely, and `npm audit` reports **0 vulnerabilities at every severity** (info/low/moderate/high/critical all 0). It clears when Vitest updates its own dependency; nothing in this repository pins it and nothing here can. Recorded 2026-08-22 (`IMP-0177`) because this was the first build in which `code-app-install` had ever actually executed, so its warning stream had never been read. (3) `npm run coverage` (build step `code-app-unit-tests`) prints repeated *"Keyborg instance kN is being disposed incorrectly."* to **stderr**, attributed by Vitest to the test files exercising Dialog/Menu-bearing components (`VerdictSection`, `App`, `ApplicationsListPage`). Accepted: it is a `console.error` from a Fluent UI internal — `node_modules/keyborg/dist/index.js:365`, reached when `disposeKeyborg(id)` is called for an id no longer in its refs map — and it is **guarded by `if (process.env.NODE_ENV !== "production")`**, so it cannot reach the shipped bundle. Test-harness-only, zero production impact, 228/228 tests still pass. Recorded 2026-08-23 (`IMP-0214`) because this was the first run whose FULL stderr stream was read line by line rather than summarised to the pass/fail/coverage line. The triage method is the reusable part: before treating a third-party `console.error` as a defect in our code, grep `node_modules` for the exact message and check whether it sits on a production-guarded path. 0 untriaged.

### Hours proposal — for `commercial-agent` behind `APPROVE TIMESHEET`

A proposal, not a booking. Estimates are in [`contract/wbs.json`](contract/wbs.json#L902) and are deliberately not restated here.

| WBS | Proposed actual | Evidence |
|---|---|---|
| 6.1 | 2.5 h | Role + privilege amendment, TAD contradiction resolved, app design |
| 6.2 | 2.5 h | List screen, sort/filter, round scoping, 2 columns |
| 6.3 | 2.5 h | Detail screen, narrative states, 2 columns |
| 6.4 | 2.5 h | Decision capture + slot mapping (review table landed in the prior dispatch) |
| 6.5 | 1.5 h | **Partial** — sharing config and print route done, access test not performed |
| *system* | 1.0 h | Build gates, fixtures, derived test counts — tooling, not client scope |

**11.5 h against WBS 6.1–6.5, plus 1.0 h system.** Every figure is below its task's estimate.

### What is still open

**The role id blocks the build.** `REV Trustee` has never existed in any environment, so its source carries a deliberate sentinel rather than a fabricated GUID. `root-components-resolve` therefore fails, and I left it failing on purpose: declaring a knowingly-invalid id in the shipped manifest would move the failure from build time to import time, where this project's own history says it costs far more. Closure is two steps — run `ensure-schema.ps1 -Env dev`, then read the real `roleid` back and substitute it in both the role file and the solution manifest.

**FR-034 (region) is implemented but not yet met.** The list screen reads `rev_locationarea`, which needs the new `prvReadrev_applicant` privilege to actually reach a real environment. Until then it is code, not a delivered requirement.

**`pac code push` has never been run in this tenant.** So whether the app travels inside the managed solution or needs a per-environment push — [TAD §9.3](docs/architecture/revitalise-grant-automation-architecture.md#L1094)'s documented deviation — is genuinely unknown. Both routes are declared in the pipeline config and the first push settles it.

**A generated Microsoft file does not compile.** `pac code add-data-source` emitted a service with a parameter named `MSCRM.IncludeMipSensitivityLabel`; a `.` is not a legal TypeScript identifier, and it is a module-level parse failure. Worked around through the SDK's own client entry point without editing generated output; reproduction recorded in [`src/dataverse/README.md`](src/code-apps/trustee-review-portal/src/dataverse/README.md#L24). `C-TECH-048` is still satisfied — data access is through the managed connector data source, with no token handling.

**Per-table typed models are unreachable here.** `pac code list-tables` fails against this connection on all three dataset forms tried, so the app codes against the generic connector typing behind one repository module. Three failed guesses was the stopping point.

### What you need to decide

**Was creating four TAD-named columns the right call, or is it a change order?**

The columns are named in the approved TAD and two of them belong to deferred Automation #5. I judged them enabling schema for 6.2/6.3's own contracted deliverables and built them; the deferred flow that writes them stays deferred. If you read that as scope that needs pricing, it is a `commercial-agent` question and reversing it is cheap right now.

**Should the finalised-round write-lock stay?**

frontend-agent added, on its own initiative, a lock preventing edits to a review round already stamped finalised. Nothing in the SDD or TAD asks for it. I would keep it — it protects the same double-execution guard the finalise flow depends on — but it is unrequested behaviour and you should know it is there.

**Two conventions want ratifying as project precedent**, because this is the first Code App and whatever ships here becomes the pattern: **CSS Modules** for styling, and **in-app view state instead of URL routes** (HTML5 history routing inside the Power Apps player is unverified, so routes were not used). Neither is hard to change now and both are awkward to change later.

Closing verification: 33-step build preflight PASS, 22 gates all with negative tests; 835 of 840 repository tests pass with the 5 failures individually attributed; 228 of 228 app tests pass; enforced coverage 86.62% against an 80% threshold. **Not verified:** anything requiring a live environment — no import, no push, no signed-in trustee, no column-security behaviour.

## Revision — IMP-0112 fix: intake flow's six alternate-key Get-a-row-by-id calls replaced (WBS 4.3, 2026-08-21)

### Summary

`flow-definition-language` failed the build for the first time it actually ran that far, on the six `GetItem` actions [`IMP-0112`](logs/improvement-log.jsonl) already predicted — `REVIntakeWordPressToDataverse` reading `AgeBandMap`, `PostcodeRegionMap`, `AgeRangeLabelMap`, `ExceptionalCircumstanceLabelMap`, `EmploymentStatusLabelMap` and `CareHoursBandLabelMap` each by an alternate-key literal in Row ID, the identical shape that failed `REVScoringCalculateAndFlag` on all eleven of its first live runs. Rework against an already-accepted task (WBS 4.3), not new scope — no change order.

### What changed

All six reads were replaced with one `ListRecords` call plus a row-count guard plus six `Query` extractors, copying `REVScoringCalculateAndFlag`'s own already-verified shape (V5 in DEV, `REVScoringCalculateAndFlag` line 172) rather than re-deriving it: [`Read_configuration`](src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L628) is now a `Scope` inside `Create_the_application`, holding `Read_intake_configuration` (the single `ListRecords`, filtered on all six names), `Fail_if_a_setting_row_is_missing` (terminates `Failed` below 6 rows — a miss is a short array under List rows, not the 404 Get-a-row-by-id gave), and six `Setting_<Key>` extractors. Every downstream `Query`/`Compose` that read `outputs('Read_<Key>_map')?['body/rev_value']` now reads `first(body('Setting_<Key>'))?['rev_value']`.

Because `Read_configuration` is a nested `Scope` (the same shape the scoring flow already had), [`Describe_the_failure`](src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L1291) was widened from a plain `Scope` to an `If` that descends into `result('Read_configuration')` when that scope is the failed child — otherwise `result()` on it returns only the generic wrapper message ([`IMP-0109`](logs/improvement-log.jsonl)). This mirrors `REVScoringCalculateAndFlag`'s own `Describe_the_failure` exactly; without it, this fix would have traded one known defect class for a second one in the same change.

Four action descriptions came out over the platform's 256-character save limit once condensed prose was written; each was shortened in the JSON and the full reasoning moved to the companion [`notes.md`](src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.notes.md#L161), the pattern this file already used for the trigger and payload-contract sections.

Two test files needed updating, not just the flow: [`IntakeContract.Tests.ps1`](src/tests/solutions/IntakeContract.Tests.ps1#L364) asserted the `Read_age_range_label_map` action's `recordId` by name — the exact shape being removed — which is the [`IMP-0111`](logs/improvement-log.jsonl) class (a test locking in the defect it should have caught). Fixed, and a new [`IMP-0112` Describe block](src/tests/solutions/IntakeContract.Tests.ps1#L399) added mirroring `ScoringInvariants.Tests.ps1`'s own coverage for its flow. [`ScoringInvariants.Tests.ps1`](src/tests/solutions/ScoringInvariants.Tests.ps1#L656)'s comment claiming the intake flow was "a separate, unfixed defect" is now stale and was corrected in the same change.

### §10 Unvalidated Assumptions Register

None opened. The List-rows-plus-extractor shape, the row-count guard, and the nested-scope failure descent are all copied verbatim from `REVScoringCalculateAndFlag`, which is verified V5 live in DEV ([`IMP-0126`](logs/improvement-log.jsonl)) — this is applying a ground-truthed pattern, not a new guess.

### §11 Verification Evidence

**Highest level executed: V2 (packaged).** `pac solution pack --packagetype Unmanaged` against the current source tree produced a 120,033-byte zip (existence and size checked, not just exit code — [`IMP-0018`](logs/improvement-log.jsonl)); the packed `Workflows/REVIntakeWordPressToDataverse-...json` was unzipped and compared byte-for-byte against source (`IDENTICAL`), confirming zero `GetItem` actions and all six `Setting_<Key>` extractors survive packaging. Not run: import, human open-and-save, or a live trigger (V3–V5) — no environment was available in this session.

| Executed | Result |
|---|---|
| `python3 scripts/verify-flow-definition-language.py src/solutions/RevitaliseGrantAutomation` | OK — 4 flow definitions, 0 violations (was 1 FAILED before the fix, on this exact file) |
| `python3 scripts/verify-flow-definition-language.py --selftest` | OK — 8 checks; the gate can still fail |
| `python3 scripts/verify-field-length-limits.py src/solutions/RevitaliseGrantAutomation provisioning/deploymentSettings` | OK — caught 4 over-limit descriptions introduced by this fix, all corrected |
| `pwsh -File src/tests/Invoke-Tests.ps1` (full repository suite) | **847 passed, 0 failed, 1 skipped** (was 846/1/1 before the two test-file fixes) |
| `pac solution pack --packagetype Unmanaged` + byte-diff of the packed flow JSON | packed cleanly; packed content identical to source |

`scripts/verify-workflow-syntax.py` was checked and does **not** cover flow bodies — its docstring and `--root` default (`.github`) confine it to GitHub Actions workflow/action YAML, a same-named but unrelated gate for a different defect class (`IMP-0074`/`IMP-0165`). It was not run against this fix for that reason.

**Tool warnings: 0 untriaged.** No new SOFT constraint findings from this change.

### Hours proposal — for `commercial-agent` behind `APPROVE TIMESHEET`

| WBS | Proposed actual | Evidence |
|---|---|---|
| 4.3 | 1.0 h | Rework of an already-delivered task: instance fix in the flow JSON, two test-file corrections, one gate re-run to green, full suite re-run |

**1.0 h against WBS 4.3.** Below the task's estimate; this is a defect fix on already-delivered scope, not new build.

### Improvement log

No new entry. `IMP-0112` was already logged and its `revisit_when` condition ("before Alex's WordPress integration is connected to DEV") is what this fix closes; only `improvement-agent` moves its `status` to `APPLIED`.

## Revision — Trustee Code App pushed to DEV; five §10 rows closed by live verification (WBS 6.1–6.5, 2026-08-22)

### Summary

The reviewer enabled the "Power Apps code apps" product feature on `REV-GrantApplications-DEV`
([IMP-0182](logs/improvement-log.jsonl)'s blocker). Per the reviewer's own instruction, that
toggle's confirmation was not treated as proof — `pac code push --solutionName
RevitaliseGrantAutomation` was re-run from
[`src/code-apps/trustee-review-portal`](src/code-apps/trustee-review-portal/power.config.json#L1)
and a clean push, plus `pac code list` and a live query, are the evidence. Five of the twelve
§10 rows are now closed; the remaining seven need a signed-in trustee in a browser, which this
session cannot provide.

### What was verified live

1. **The Code App is live in DEV.** `pac code push` returned success; `pac code list` names
   "REV Trustee Review Portal"; `power.config.json`'s `appId` moved from `null` to
   `70869c95-92e5-442f-b5b9-44b3d3e549f6`. Level: V3.

2. **TAD §9.3's open question is answered: NO, it does not travel via the managed import.**
   `solutioncomponents` for `RevitaliseGrantAutomation` (49 rows, queried live) does not include
   the code app's `appId` under any `componenttype`, and three plausible Code-App-specific
   Dataverse entity-set names all 404. [`IMP-0185`](logs/improvement-log.jsonl) records this.
   **Consequence:** TST/ACC and PRD each need their own `pac code push` post_deploy step — not
   yet in [`config/revitalise-grant-automation-pipeline.yml`](config/revitalise-grant-automation-pipeline.yml#L937)'s
   `tst_acc`/`prd` blocks. That config change is unquoted work for whoever picks up WBS 6.5's
   promotion beyond DEV; not made in this dispatch.

3. **A-TR-10 CLOSED** (`If-Match: *` as the update-only guard). Created one `rev_review` test row
   against an existing test application (REV-2026-1057), then: (a) `PATCH` with `If-Match: *`
   against the real id → HTTP 204, a legitimate update is not blocked; (b) the same `PATCH`
   against a random id → HTTP 404 "Does Not Exist", not a silent create; (c) as a control, the
   *same* nonexistent-id `PATCH` **without** `If-Match` → HTTP 204 and it silently upserted a new
   row. The three together are the proof: Dataverse's default `PATCH` behaviour is
   insert-or-update, and `If-Match: *` is what turns it into update-only. Test row and the
   control's upserted row were both deleted afterward.

4. **A-TR-7 CLOSED** (the `_<lookup>_value` `$select` form). The correct lookup logical name on
   `rev_review` is `rev_applicationid` (confirmed via `EntityDefinitions`), not `rev_application`
   as first guessed — `$select=_rev_applicationid_value` returns it correctly. Logged as ground
   truth alongside the read-back payload shape.

5. **A-TR-3 still OPEN, but no longer a guess — it is now a named tooling blocker.**
   [`IMP-0186`](logs/improvement-log.jsonl): on this Mac, in `pwsh` 7, `Add-PowerAppsAccount
   -CertificateThumbprint` (the call `share-apps.ps1`'s code/canvas branch depends on) fails
   two independent ways — an assembly conflict with `MSAL.PS` when both run in one session, and
   (in a fresh process) "Cannot find drive... Cert" because the Windows-only `Cert:\` PSProvider
   does not exist in `pwsh` on macOS, confirmed three ways (`Get-PSDrive`, `New-PSDrive`,
   `Get-Item`) while the identical certificate resolves immediately via direct `X509Store`
   lookup. Closing A-TR-3 needs either a Windows PowerShell 5.1 runner or restructuring
   `share-apps.ps1` to run the two auth types in separate processes — not attempted here, as
   both are config/script changes outside this dispatch's scope.

6. **A-TR-1, A-TR-4, A-TR-5, A-TR-8, A-TR-9, A-TR-11 remain OPEN** (A-TR-12 was closed 2026-08-22 from the installed SDK's own `.d.ts` — see the register). Each needs a
   signed-in trustee inside the Power Apps host (a browser session) or, for A-TR-4/A-TR-5, a
   named non-admin test user holding *only* `REV Trustee` — and DEV currently has **zero** users
   assigned that role (`roles(3ab6cc7b-…)/systemuserroles_association` returned 0 live). No
   dedicated trustee-test account exists yet among DEV's human systemusers (Mateusz Cwiklicki,
   Corey Boucher, Reece Gurling, Wanstor IT Support, admin revitalise) — deciding who tests as
   the trustee, consistent with [EX-003](contract/known-exceptions.json#L31)'s DEV-and-test-data-only
   condition, is the reviewer's call, not this session's to make.

### §10 Unvalidated Assumptions Register — updated

| id | Status this dispatch |
|---|---|
| A-TR-1 | OPEN — needs a signed-in trustee |
| A-TR-3 | OPEN — blocked by two tooling defects on this Mac, not by the platform contract itself (see above) |
| A-TR-4 | OPEN — needs a named trustee test account, not yet assigned in DEV |
| A-TR-5 | OPEN — same, the V4 access test itself |
| A-TR-7 | **CLOSED** — `_rev_applicationid_value` confirmed live |
| A-TR-8 | OPEN — needs the Power Apps host in a browser |
| A-TR-9 | OPEN — raw Web API shape now known (see finding 4 above), but the code app's own generated client shape is unobserved |
| A-TR-10 | **CLOSED** — `If-Match: *` update-only guard proven with a positive and negative control |
| A-TR-11 | OPEN — needs a signed-in trustee |
| A-TR-12 | **CLOSED 2026-08-22** — answered from the installed SDK's own type declarations; the host was never needed. `setConfig` + `getContext` is the entire `./app` surface (IMP-0199) |

Two of ten open rows closed; A-TR-2 and A-TR-6 were already closed in the prior dispatch.

### What is still open

Everything WBS 6.5's V4 access test needs — a named trustee test account, assigned the `REV
Trustee` role directly in DEV (group teams are a TST/ACC/PRD mechanism per this environment's
own direct-assignment design) — and a person willing to sign in as them. Both are reviewer
decisions.

### Improvement log

2 entries — `IMP-0185` (capability: the code app does not ride the managed import; TST/ACC/PRD
each need their own push) and `IMP-0186` (`share-apps.ps1`'s code/canvas branch cannot run
end-to-end on this Mac; two tooling causes named). Digest regenerated.

## Revision — real Dataverse data sources wired; account smoke-test binding removed (WBS 6.1–6.5, 2026-08-22)

### Summary

[`IMP-0208`](logs/improvement-log.jsonl) root-caused the connector's
"Invalid organization URL 'null' provided" defect (blocking this app since deployment) to
`pac app add data-source` never resolving the organisation URL automatically, and proved the
fix — passing `-u`/`--org-url` explicitly — against the generic connector using the `account`
table as a smoke test. This revision applies that fix to the app's **actual** four tables and
removes the smoke-test binding. Nothing in `src/dataverse/client.ts` or `repository.ts` changed;
this closes the connector-provisioning half of the blocker, not the app logic.

### What was done

1. **Four real data sources added**, each via `pa app add data-source --connector dataverse
   --table <t> -u https://orge2b20d13.crm17.dynamics.com -c f31ddadfbe874e50a34054df668e75cf
   --non-interactive`, run from `src/code-apps/trustee-review-portal`: `rev_application`,
   `rev_review`, `rev_applicant`, `systemuser` — the four tables
   [`schema.ts`](src/code-apps/trustee-review-portal/src/dataverse/schema.ts#L10)'s
   `ENTITY_SETS` already named. All four succeeded and the platform's own returned
   `entitySetName`/`primaryKey` match what `schema.ts` already declared exactly
   (`rev_applications`/`rev_applicationid`, `rev_reviews`/`rev_reviewid`,
   `rev_applicants`/`rev_applicantid`, `systemusers`/`systemuserid`) — confirmed in
   [`power.config.json`](src/code-apps/trustee-review-portal/power.config.json#L1)'s
   `databaseReferences` and in the generated `.power/schemas/appschemas/dataSourcesInfo.ts`.

2. **Scope check performed, per the handoff instruction, before adding anything:** the
   architecture's data model (TAD §3, `rev_review`) and WBS 6.1's own description name
   "Application, Review and Grant". [`repository.ts`](src/code-apps/trustee-review-portal/src/dataverse/repository.ts#L186)
   and `schema.ts` show this app reads `rev_application`, `rev_review` and `rev_applicant`
   (for the region lookup only) — never `rev_grant`. That is correct, not a gap: a Grant row
   is created only on approval, by `REV | Portal | Finalise Decisions`
   ([TAD §5.7](docs/architecture/revitalise-grant-automation-architecture.md#L675)), so no
   Grant record exists yet for an application a trustee is reviewing. WBS 6.3's "holiday
   details" (break dates/type/location, requested amount, costs) are `rev_application`
   columns, already in `APPLICATION_DETAIL_EXTRA_COLUMNS`. No table beyond the three already
   built is needed; no change-order routing required.

3. **The `account` smoke-test binding removed** — [`IMP-0208`](logs/improvement-log.jsonl)'s
   own proposed-change note flagged it as "a smoke test only, not a project table". Deleted
   `src/generated/models/AccountsModel.ts`, `src/generated/services/AccountsService.ts`,
   `.power/schemas/dataverse/accounts.Schema.json`; removed the `accounts` entry from
   `power.config.json`'s `databaseReferences` and from the generated
   `dataSourcesInfo.ts`/`generated/index.ts` (both regenerate additively and do not prune a
   removed source on their own).

4. **`A-TR-6` closed a second, independent way.** `pipeline-agent`'s live `EntityDefinitions`
   query (previous revision, above) already confirmed `rev_reviews`/55 attributes. This
   dispatch's `add-data-source` call against the same environment independently returned the
   identical `entitySetName` and `rev_reviewid` as primary key — a second platform-sourced
   confirmation, not a re-guess. `schema.ts`'s `A-TR-6` comments updated from `GUESS, E4` to
   `CLOSED, E1` citing both.

5. **A hand-authored platform contract turned out wrong, corrected in
   [`README.md`](src/code-apps/trustee-review-portal/src/dataverse/README.md#L1) §1
   (`IMP-0209`).** It stated the typed-per-table data-source route was unreachable in this
   environment (`pac code list-tables`/`list-datasets` failed three ways, 2026-08-21). That
   was scoped to the *old* `pac` CLI, which has no org-url override; the newer `pa` CLI's
   `-u` flag resolves a per-table dataset over the identical connection — the same
   underlying defect `IMP-0208` named, one layer up, not a different blocker. All four newly
   generated services (`Rev_applicationsService.ts` etc.) are confirmed clean — `grep -n
   MSCRM` returns nothing in any of them, unlike the generic `MicrosoftDataverseService.ts`
   — and a full `tsc --noEmit` / `eslint .` pass across the app confirms it.

6. **The typed services are committed as ground truth and deliberately not wired in.**
   `client.ts`/`repository.ts` still call the generic connector by hand. README.md §1 records
   three reasons this dispatch did not migrate them: the hand-rolled layer's `$select`
   allow-list discipline would need re-proving per call site against `IGetAllOptions`; the
   generated `update()`'s write semantics (upsert vs. this app's deliberate
   `UpdateOnlyRecord` + `If-Match: *`, `A-TR-10` — CLOSED with a live positive/negative
   control against the hand-rolled path) are unobserved for the generated client; and
   swapping a reviewed, tested data layer is a reviewer decision, not a side effect of fixing
   a broken connection. Flagged below for the reviewer, not decided here.

### §10 Unvalidated Assumptions Register — updated

| id | Status this dispatch |
|---|---|
| A-TR-6 | Already CLOSED — reconfirmed by a second, independent platform response (this dispatch), no register change needed |

No new rows opened. This dispatch introduced no new guesses: all four table bindings are
platform-returned ground truth (E1), not assumptions.

### §11 Verification Evidence

**Highest level executed: V3 for the connector binding itself** (the platform accepted all
four `add-data-source` calls and returned real metadata) — **still V2 for the app's own use of
that connection** (typecheck/lint/228 tests/production build all re-run clean after the
change, but nothing exercises the connector at runtime). The generic `commondataserviceforapps`
connection is now bound to the resolved organisation URL, which is what the app's `ListRecords`
/ `GetItem` / `UpdateOnlyRecord` calls depend on — but that has not been observed by an actual
run of the app; it depends on the same connection object, not a re-guess, and is reported at
that confidence and no higher.

| Executed | Result |
|---|---|
| `pa app add data-source` × 4 (rev_application, rev_review, rev_applicant, systemuser) | all 4 succeeded; entitySetName/primaryKey match `schema.ts` exactly |
| `npm run typecheck` (`tsc --noEmit -p tsconfig.json`) | clean, 0 errors |
| `npm run lint` (`eslint .`) | clean, 0 errors/warnings |
| `npm run coverage` (`vitest run --coverage`) | 228/228 tests pass, 97.78% line coverage — unchanged from the prior revision |
| `npm run build` | production build succeeds; same single accepted bundle-size warning as before ([`IMP-0177`](logs/improvement-log.jsonl)), 0 new warnings |
| `python3 scripts/verify-code-app-column-bindings.py src/code-apps/trustee-review-portal src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml` | OK — 55 authored files, 0 of 51 secured columns referenced, all 3 fail-closed columns present (unchanged — confirms this change touched no column binding) |

**What this does not prove.** Whether a signed-in trustee's real browser session now returns
data instead of the "Invalid organization URL null" error is unobserved — that needs the same
V4/V5 access test `A-TR-1/4/5/8/9/11/12` already await, which still needs a named trustee test
account in DEV (reviewer decision, unchanged from the prior revision).

**Tool warnings: 0 untriaged.** No new warnings from `pa app add data-source`, `npm run
typecheck`, `npm run lint`, or `npm run build` beyond the one already accepted in the prior
revision.

### What you need to decide

**Should the typed per-table generated services replace the hand-rolled generic connector
client?** The route that was recorded closed is now open (finding 5 above), and the typed
services carry the `$select`/`$filter`/`$orderby` shape needed to preserve this app's
allow-list discipline. I did not make this change — it touches every call site in a reviewed,
tested data layer, and the generated `update()`'s write semantics against `rev_review` are
unverified. If you want it, it is new work sized against WBS 6.1, not a side effect of this
fix.

### Hours proposal — for `commercial-agent` behind `APPROVE TIMESHEET`

| WBS | Proposed actual | Evidence |
|---|---|---|
| 6.1 | 1.0 h | Four real data sources wired, smoke-test binding removed, `A-TR-6` reconfirmed, one hand-authored-contract correction (`IMP-0209`), full app verification re-run clean |

**1.0 h against WBS 6.1**, on top of the 2.5 h already proposed for that task in the prior
revision (3.5 h cumulative), still below the task's 4–6 h estimate.

### Improvement log

1 entry — `IMP-0209` (the typed-per-table Dataverse data-source route, previously recorded
unreachable, is reachable via the newer `pa` CLI's `-u`/`--org-url` flag — a hand-authored
platform contract that turned out wrong, corrected in `README.md` and `schema.ts`). Digest
regenerated: YES.

## Revision — stale `DeploymentSettings.Tests.ps1` audited-tables assertion generalised (WBS 6.1–6.5, 2026-08-23)

### Summary

`build-agent`'s unit-tests step for this same Dataverse-wiring build halted on
[`src/tests/provisioning/DeploymentSettings.Tests.ps1:119`](src/tests/provisioning/DeploymentSettings.Tests.ps1#L119)
— `'all four Phase 1 tables are audited, in both environments'` hardcoded `Should -Be 4` and a
4-name list, while `test-settings.json`/`prd-settings.json` now correctly declare 6
(`rev_grant`, `rev_review` added under `IMP-0178`). Logged as
[`IMP-0212`](logs/improvement-log.jsonl) — the **fifth** recorded instance of
`test-coupled-to-absolute-counts` and the second inside this file (after `IMP-0155`). Per
`skills/how-to-promote-a-finding.md` a second instance in one class is not another hand-typed
number; this dispatch applies `IMP-0212`'s own `proposed_change` — derive the expected set from
source — rather than bumping the literal to 6.

### What changed

[`DeploymentSettings.Tests.ps1`](src/tests/provisioning/DeploymentSettings.Tests.ps1#L16): `BeforeAll`
now derives `$script:ExpectedAuditedTables` from
`src/solutions/RevitaliseGrantAutomation/Entities/*/Entity.xml` on disk — the identical source
[`scripts/verify-audited-tables.py`](scripts/verify-audited-tables.py#L63)'s `declared_tables()`
already reads for `C-TECH-064`'s source-side half — and the test at
[line 119](src/tests/provisioning/DeploymentSettings.Tests.ps1#L119) now asserts membership of
every derived table in both settings files' `auditedTables`, instead of an exact hardcoded count.
Membership only, not exact count, on purpose: `verify-audited-tables.py`'s own selftest (case 4,
[line 141](scripts/verify-audited-tables.py#L141)) treats an audited table absent from disk as
*not* an error, and the Pester test now keeps that same semantics rather than reintroducing a
tighter rule the Python gate doesn't enforce. No production code, schema, or settings content
changed — this is a test-file-only fix.

### §10 Unvalidated Assumptions Register

No rows opened or closed. The fix introduces no guess: the expected table set is read directly
from `Entity.xml` files on disk (ground truth), not inferred.

### §11 Verification Evidence

Not a platform-artefact change, so the V1–V5 ladder does not apply; reported instead as direct
tool execution against the real repository:

| Executed | Result |
|---|---|
| `Invoke-Pester -Path src/tests/provisioning/DeploymentSettings.Tests.ps1` (isolated) | 37/37 passed, 1 skipped (pre-existing, unrelated `D-011` skip) |
| `pwsh -File src/tests/Invoke-Tests.ps1` (the CI path, `IMP-0026`) | 848/849 passed — the fixed test passes; the one remaining failure is unrelated, see below |
| `python3 scripts/verify-audited-tables.py` | PASS — 6 declared tables audited in all 3 settings files that declare the key (cross-check against the same source the Pester fix now reads) |

**One pre-existing, unrelated failure remains in the full suite**, and this dispatch did not
touch it: `BuildGates.Tests.ps1`'s `'verify-improvement-log --check' passes against the real log`
fails because `IMP-0212` itself — the finding this dispatch fixes the subject of — is still an
**unread `blocker`** in `logs/improvement-log.jsonl` (confirmed by running
`python3 scripts/verify-improvement-log.py --check` directly: `TRIGGER: 1 NEW entry(ies) of
severity 'blocker' in state 'unread': IMP-0212`). That gate (`C-TECH-061`) is working as designed
— `agents/WORKFLOW.md`'s "a blocker routes to improvement-agent immediately" — not a new defect:
per `skills/how-to-log-an-improvement.md` only `improvement-agent` may move `IMP-0212` off `NEW`,
and per the original handoff this was "separately routed to improvement-agent to judge" the
general-fix question already answered above. **The unit-tests step will show 1 failure until
that routing completes**, independent of this fix; `build-agent` should not attribute it to
`DeploymentSettings.Tests.ps1` or reopen this item.

**Tool warnings: 0 untriaged.**

### Hours proposal — for `commercial-agent` behind `APPROVE TIMESHEET`

| WBS | Proposed actual | Evidence |
|---|---|---|
| 6.1 | 0.2 h | One stale test assertion generalised to derive from source, isolated + full-suite re-run, cross-checked against `verify-audited-tables.py` |

**0.2 h against WBS 6.1**, on top of the 3.5 h already proposed for that task across the two
prior revisions (3.7 h cumulative), still below the task's 4–6 h estimate.

### Improvement log

0 entries appended — none. `IMP-0212` already records this defect (logged by `build-agent`) and
this dispatch implements its own `proposed_change` exactly; a duplicate entry for the same
incident is the pattern `IMP-0154`/`IMP-0169`/`IMP-0181` already flagged as noise, not signal.
Digest regenerated: YES (`python3 scripts/generate-known-failure-modes.py`, re-run to confirm
current — no content change, since no entry was appended).

## Revision — WBS 0.4 remainder: Provider, Bank Account, Payment, Anonymised Statistic (2026-08-23)

### Summary

Built the four Dataverse tables [WBS 0.4](contract/wbs.json) still names as outstanding —
`rev_provider`, `rev_bankaccount`, `rev_payment`, `rev_anonymisedstatistic` — plus the
`rev_grant.rev_providerid` lookup task 0.4's own description requires but which could not exist
before Provider did. `contract/known-exceptions.json`'s `EX-001` recorded this absence against
task 0.4 on 2026-08-19; four of the five tables it names are now built (`rev_review` landed
under WBS 6.4 in an earlier session). Three sub-agent dispatches did the schema, security and
settings work; three further defects surfaced while verifying the result and were found and
fixed in this same session rather than left for a later one. Everything here is **V1** — source
only, no live environment write was available or attempted.

### What was built

1. **Schema** (`data-agent`): four entities under
   [`Entities/`](src/solutions/RevitaliseGrantAutomation/Entities/), five new global option sets
   under [`OptionSets/`](src/solutions/RevitaliseGrantAutomation/OptionSets/), six new
   relationships under
   [`Other/Relationships/`](src/solutions/RevitaliseGrantAutomation/Other/Relationships/), and
   the new `rev_providerid` lookup added to the existing
   [`Entities/rev_grant/Entity.xml`](src/solutions/RevitaliseGrantAutomation/Entities/rev_grant/Entity.xml).
   Column set and types reconcile the TAD's own non-exhaustive §3.1 listing
   ([`docs/architecture/revitalise-grant-automation-architecture.md#L350`](docs/architecture/revitalise-grant-automation-architecture.md#L350))
   against `docs/Import/grant-application-data-model-v0.2.md`'s fuller build specification —
   every place the two disagree or one is silent is recorded as a source comment at the point of
   the decision, not resolved silently.
2. **Security** (`identity-agent`): a new `REV_FinanceOnly` field security profile (18 field
   permissions) in
   [`Other/FieldSecurityProfiles.xml`](src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml),
   and privilege extensions to
   [`Roles/REV Admin/REV Admin.xml`](src/solutions/RevitaliseGrantAutomation/Roles/REV%20Admin/REV%20Admin.xml),
   [`Roles/REV Service Automation/REV Service Automation.xml`](src/solutions/RevitaliseGrantAutomation/Roles/REV%20Service%20Automation/REV%20Service%20Automation.xml)
   and
   [`Roles/REV Trustee/REV Trustee.xml`](src/solutions/RevitaliseGrantAutomation/Roles/REV%20Trustee/REV%20Trustee.xml),
   matching [TAD §6.2](docs/architecture/revitalise-grant-automation-architecture.md#L831).
3. **Settings** (`config-agent`): the four new tables added to `dataverse.auditing.auditedTables`
   in
   [`test-settings.json`](provisioning/deploymentSettings/test-settings.json),
   [`prd-settings.json`](provisioning/deploymentSettings/prd-settings.json) and
   [`dev-auditing-settings.json`](provisioning/deploymentSettings/dev-auditing-settings.json); a
   `REV_FinanceOnly` entry (member: `REV Service Accounts` only — never `REV Admins`, NFR-002
   separation of duties) added to `dataverse.columnSecurityProfiles` in the first two.
4. **Three defects found and fixed in this session, not merely logged** — each was a HARD gate
   turning red because this solution reuses column names (`rev_name`, `rev_applicantid`) across
   tables with different security classifications:
   - `IMP-0236`/`IMP-0237`: the scoring flow's FR-016 test flagged its own legitimate read of
     `rev_application.rev_name` as a special-category leak, because the check derived its
     forbidden set from every secured column in the **whole solution** rather than the one entity
     the scoring flow actually reads. Fixed by scoping
     [`Get-SecuredColumnNames`](src/tests/solutions/_harness/SolutionSource.psm1#L165) to an
     `-Entity` parameter.
   - `IMP-0238`/`IMP-0239`: `ensure-schema.ps1` would have provisioned **zero** field permissions
     against a live environment instead of 69. `Get-RevFieldSecurityProfileDefinition`
     ([`ensure-schema-helpers.psm1#L841`](provisioning/dataverse/ensure-schema-helpers.psm1#L841))
     assumed exactly one `<FieldSecurityProfile>` element; PowerShell's XML adapter silently
     returns an array once a second one exists, and every downstream property read on it returned
     nothing, with no error. Fixed to return every profile and iterate.
   - `IMP-0240`: the trustee Code App's column-security gate unioned every profile in
     `FieldSecurityProfiles.xml`, so `REV_FinanceOnly` securing `rev_name`/`rev_applicantid`
     flagged the app's entirely legitimate `rev_application` references. Fixed by adding
     `--exclude-profile` to
     [`verify-code-app-column-bindings.py`](scripts/verify-code-app-column-bindings.py#L106),
     wired from
     [`config/revitalise-grant-automation-build.yml#L613`](config/revitalise-grant-automation-build.yml#L613).
5. **`contract/tad-deferrals.json` hygiene**: `TD-001`–`TD-004` and `TD-009` deferred exactly the
   columns this dispatch built; all five were deleted per that file's own `_stale_entries_fail`
   rule rather than left to accumulate. `TD-005`–`TD-008` are untouched and remain open — none of
   them concern these four tables. Flagged for `pm-agent`/`commercial-agent` below: `TD-001`'s
   clearing text named WBS `6.4`/`8.1` (via `EX-001`) as where this work would land; it was built
   under `0.4` instead, per this dispatch's own handoff and per task `0.4`'s own description,
   which already names all eight tables as its deliverable. `contract/known-exceptions.json` was
   left untouched — it is reviewer-owned, and whether `EX-001` itself needs updating is a
   commercial decision, not a schema one.
6. **Pipeline and build config** (`development-agent`): `config/revitalise-grant-automation-pipeline.yml`'s
   DEV `environment_prerequisites` gained one entry for the new schema and the `REV_FinanceOnly`
   profile (same `ensure-schema.ps1 -Env dev` run as the existing `rev_grant` steps — nothing new
   to run), and the TST/ACC and PRD `post_deploy` descriptions for
   `ensure-column-security-profile-members.ps1` / `ensure-auditing.ps1` were corrected to name
   both profiles / all ten tables rather than the stale four-table text they carried. Both configs
   re-pass their own preflight (`verify-build-config.py`, `verify-pipeline-config.py`).

### Elements added

| Component | Type | FR / TAD reference |
|---|---|---|
| `rev_provider` | Entity (OrganizationOwned, Tier 2) | [TAD §3.2](docs/architecture/revitalise-grant-automation-architecture.md#L381) |
| `rev_bankaccount` | Entity (UserOwned, Tier 4, all columns secured) | [TAD §3.1](docs/architecture/revitalise-grant-automation-architecture.md#L354), [§3.4 Gap 2](docs/architecture/revitalise-grant-automation-architecture.md#L446) |
| `rev_payment` | Entity (UserOwned, Tier 4, all columns secured) | [TAD §3.1](docs/architecture/revitalise-grant-automation-architecture.md#L359) |
| `rev_anonymisedstatistic` | Entity (OrganizationOwned, Tier 2, no relationships by design) | [TAD §3.3](docs/architecture/revitalise-grant-automation-architecture.md#L421) |
| `rev_grant.rev_providerid` | Attribute (referential, Restrict Delete, unsecured) | [TAD §3.1](docs/architecture/revitalise-grant-automation-architecture.md#L343) |
| `rev_payeetype`, `rev_paymentmethod`, `rev_paymentstatus`, `rev_conditionareas`, `rev_statisticoutcome` | Global option sets | v0.2 build spec + TAD, values marked "to confirm" where neither source enumerates them |
| 6 relationships (Applicant→BankAccount parental; Provider→BankAccount/Grant/Payment referential Restrict Delete; Grant→Payment parental; BankAccount→Payment referential, not Restrict Delete) | Relationships | [TAD §3.3](docs/architecture/revitalise-grant-automation-architecture.md#L405), [§3.4](docs/architecture/revitalise-grant-automation-architecture.md#L434) |
| `REV_FinanceOnly` | Field security profile, 16 permissions (corrected from 18 — see revision below: each table's primary name column cannot be secured) | [TAD §6](docs/architecture/revitalise-grant-automation-architecture.md#L780) |

### Elements changed

| Component | Change |
|---|---|
| `Roles/REV Admin` | + full CRUD `rev_provider`, + `rev_anonymisedstatistic` (no Delete — never deleted by design) |
| `Roles/REV Service Automation` | + full CRUD `rev_provider`, `rev_bankaccount`, `rev_payment` (no Delete on the latter two — open question, see below), + `rev_anonymisedstatistic` |
| `Roles/REV Trustee` | + `prvReadrev_anonymisedstatistic` only |
| `provisioning/dataverse/ensure-schema-helpers.psm1` | `Get-RevEntityLogicalNames` +4 entities; `ConvertTo-RevAttributeBody` +`decimal` case; `Get-RevFieldSecurityProfileDefinition` now returns every profile |
| `provisioning/dataverse/ensure-schema.ps1` | field-security-profile step now loops over every profile (`IMP-0238` fix) |
| `provisioning/deploymentSettings/{test,prd,dev-auditing}-settings.json` | `auditedTables` +4; `columnSecurityProfiles` +`REV_FinanceOnly` (test/prd only) |
| `src/tests/solutions/_harness/SolutionSource.psm1`, `.../ScoringInvariants.Tests.ps1`, `src/tests/provisioning/EnsureSchema.Tests.ps1`, `.../DeploymentSettings.Tests.ps1`, `src/tests/build/BuildGates.Tests.ps1` | test fixes for the three defects above |
| `scripts/verify-code-app-column-bindings.py`, `config/revitalise-grant-automation-build.yml` | `--exclude-profile` flag + wiring |
| `config/revitalise-grant-automation-pipeline.yml` | DEV prerequisite added; TST/ACC + PRD descriptions corrected |
| `contract/tad-deferrals.json` | `TD-001`–`TD-004`, `TD-009` deleted (satisfied) |

### §10 Unvalidated Assumptions Register — new rows

| ID | Claim | Where in source | Evidence | Why not verified | Cheapest verification | Status |
|---|---|---|---|---|---|---|
| ~~A-FIN-01~~ | ~~A `CascadeConfiguration.Delete = Restrict` relationship (Provider→BankAccount/Grant/Payment) is accepted by the Dataverse Web API in the shape `ensure-schema-helpers.psm1` sends~~ | [`Other/Relationships/rev_provider.xml`](src/solutions/RevitaliseGrantAutomation/Other/Relationships/rev_provider.xml) | **E1 — VERIFIED (shape)** | ~~No relationship in this solution has used `Restrict` before~~ | n/a — closed | **VERIFIED 2026-08-24 at V3, read live from DEV.** All three Provider relationships report `Delete=Restrict`, and all 9 declared relationships match their source `<CascadeDelete>` exactly (5 `Cascade`, 3 `Restrict`, 1 `RemoveLink`) — see the 2026-08-24 revision's §11. **V5 RESIDUAL, deliberately not claimed:** the shape is accepted, but no Provider referenced by a Grant has actually been deleted to watch the platform block it. That is a live delete, out of this task's scope; `Restrict` is a platform primitive, so shape acceptance is the part that was ever in doubt |
| ~~A-FIN-02~~ | ~~`DecimalAttributeMetadata`'s Web API shape (`rev_payment.rev_amount`) matches what `ConvertTo-RevAttributeBody`'s new [`decimal` branch](provisioning/dataverse/ensure-schema-helpers.psm1#L431) sends~~ | see links | **E1 — VERIFIED** | ~~No Decimal column exists elsewhere in this solution to copy a ground-truthed shape from~~ | n/a — closed | **VERIFIED 2026-08-24, read live from DEV.** `rev_payment.rev_amount` is live as `AttributeType=Decimal`, `Precision=2`, `MinValue=0`, `MaxValue=100000000`, `IsSecured=True` — every value matching source. IMP-0047's recommendation to prefer `Decimal` over `Money` for a restricted amount is therefore executable in this solution, not just advisable |
| A-FIN-03 | `REV_FinanceOnly`'s real `fieldsecurityprofileid` will resolve the same way `REV_TrusteeRestricted`'s did | [`Other/FieldSecurityProfiles.xml#L622`](src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml#L622), [`Other/Solution.xml#L249`](src/solutions/RevitaliseGrantAutomation/Other/Solution.xml#L249) | **E1 — VERIFIED.** The reviewer ran `ensure-schema.ps1 -Env dev` by hand on 2026-08-23 (this session's own permission classifier refuses that live write); the real id `93d339bc-289f-f111-b8de-7ced8d43e87d` was confirmed by a read-only `fieldsecurityprofiles?$filter=name eq 'REV_FinanceOnly'&$select=fieldsecurityprofileid` query and substituted into both files | n/a — closed | n/a — closed | **VERIFIED 2026-08-23 — see the "WBS 0.4 remainder fix" revision below. The same live run surfaced a second, unrelated defect (`rev_name` not securable, `IMP-0249`) that blocked the two tables outright — closing this row does not mean that defect was pre-existing knowledge; it was found in the same run** |

Two judgement calls, not assumptions about the platform, recorded here rather than as `A-nnn` rows
because nothing about them can be "verified" by an environment — they are design decisions for the
reviewer to confirm or correct: `rev_bankaccount.rev_payeetype` was made `ApplicationRequired`
(neither source states this); and `REV Service Automation` was **not** given Delete on
`rev_bankaccount`/`rev_payment` (the retention design deletes a Bank Account via the
Applicant→BankAccount cascade, not a direct role privilege — see "What you need to decide" below).

### §11 Verification Evidence

**Highest level executed: V1 (well-formed, locally asserted) across every new component.** No
Dataverse environment write happened or was available. Every gate below ran against the real
repository tree, not a fixture.

| Gate | Result |
|---|---|
| Full Pester suite (`pwsh -File src/tests/Invoke-Tests.ps1`) | 848 passed, 2 failed (both expected and explained below), 1 skipped (pre-existing) at the point this dispatch's own work was verified |
| `verify-solution-root-components.py` | PASS — 64 components, all resolve |
| `verify-field-security-coverage.py` | PASS — 67 secured columns, all released (corrected from 69 — see "WBS 0.4 remainder fix" revision below) |
| `verify-audited-tables.py` | PASS — 10 tables audited in all 3 settings files that declare the key |
| `verify-column-security-membership.py` | OK — no trustee-facing team in any profile |
| `verify-domain-invariants.py` | PASS — 20 special-category columns, in sync |
| `verify-tad-coverage.py` | OK — 129 column specs, 0 absent, 9 deferred, 15 trustee-visible reachable |
| `verify-source-parses.py`, `verify-component-shape.py`, `verify-forms-and-views-reachable.py`, `verify-shipped-content.py` | all OK/PASS |
| `verify-guid-syntax.py` | **PASS — 0 errors.** Was FAILING (2 errors, both the `REV_FinanceOnly` pending id, A-FIN-03) at the point this table was first written; closed by the "WBS 0.4 remainder fix" revision below |
| `verify-improvement-log.py --check` | **FAILS — 6 unread `blocker` entries, 2 of them (`IMP-0236`, `IMP-0238`) already fixed in this same dispatch and cross-referenced by `IMP-0237`/`IMP-0239`; the other 4 (`IMP-0228`, `IMP-0229`, `IMP-0230`, `IMP-0232`) predate this dispatch (`pm-agent`). Routing to `improvement-agent` is `lead-agent`'s next step, not a defect in this build** |
| `verify-build-config.py`, `verify-pipeline-config.py` | both PASS — 39/28 and 82/3 steps respectively |

**A concurrent, unrelated session landed work in this same repository while this dispatch was in
progress** — `provisioning/dataverse/verify-access-test-identity.ps1` and
`provisioning/deploymentSettings/dev-access-test-settings.json` appeared untracked partway
through (timestamps and content — "access test identity" — point to WBS 6.5's trustee
access-test work, not this task). A full-suite re-run after that landed shows 3 additional
failures, all inside `provisioning/dataverse/DataverseScripts.Tests.ps1`'s generic
script-convention checks (`Exit-Provisioning`, `Write-CheckResult`, README inventory) against
that new script — **none of it is this dispatch's code or this dispatch's responsibility to
fix**, per this repository's own documented two-sessions-on-one-synced-path hazard
(`logs/known-failure-modes.md`, "Allocate a finding id from the MAXIMUM id..." entry and
neighbours). Flagged for whoever is running WBS 6.5, not actioned here.

**Tool warnings: 0 untriaged for this dispatch's own components.** `forms-and-views-reachable`
prints 8 warnings for the four new tables having no `FormXml`/`SavedQueries` content — accepted,
not a defect: these tables are schema-only per WBS `0.4`'s own description, and UI/form work is
explicitly WBS `8.1`–`8.3`'s (see "What was built" point 5's sibling reasoning on why no
site-map/`AppModule` entry was added either). `verify-source-derived-test-counts.py` (SOFT,
`C-TECH-067`) reports 4 pre-existing fragile literal counts in `EnsureSchema.Tests.ps1` and
`DeploymentSettings.Tests.ps1` this dispatch did not introduce and did not touch — accepted as
pre-existing; the two new counts this dispatch's own tests added (`REV_TrusteeRestricted`'s 2
members, `REV_FinanceOnly`'s 1) are commented `count-coupled by design`, since both are a fixed
security-membership policy, not a schema-size count, and pass the gate cleanly.

**Diagnostic components created and removed: none.**

### What you need to decide

**Does `REV Service Automation` need Delete on `rev_bankaccount`/`rev_payment`?** The retention
design ([TAD §3.4](docs/architecture/revitalise-grant-automation-architecture.md#L446)) purges a
Bank Account via the Applicant→BankAccount **parental cascade** — deleting the Applicant, not a
direct delete on the Bank Account table — and Payment is reached the same way via Grant. No TAD
text asks for a direct delete privilege here, so it was left out. If a flow ever needs to delete a
Bank Account or Payment row directly (rather than via cascade), this needs revisiting.

**Does building these four tables under WBS `0.4` (rather than `6.4`/`8.1`, which `EX-001` and
`TD-001` both named as the clearing tasks) settle `EX-001`, or does `EX-001` need its own update?**
This is a commercial/WBS-attribution question, not a schema one — `contract/tad-deferrals.json`
is cleared because the columns now exist; whether that also clears `contract/known-exceptions.json`'s
`EX-001` is `pm-agent`/`commercial-agent`'s call.

**Six `blocker`-severity findings are unread in `logs/improvement-log.jsonl`** (`IMP-0228`,
`IMP-0229`, `IMP-0230`, `IMP-0232`, `IMP-0236`, `IMP-0238`) — per
[`agents/WORKFLOW.md`](agents/WORKFLOW.md) a blocker routes to `improvement-agent` immediately.
Two of the six (`IMP-0236`, `IMP-0238`) are already fixed in this dispatch; the fix is on disk and
cross-referenced (`IMP-0237`, `IMP-0239`) so `improvement-agent` can close them without re-deriving
anything.

**`SDD OQ-026` (Provider's classification) remains open**, unaffected by this build — `rev_provider`
was built with no column carrying a named individual, which is the binding condition the DERIVED
Tier 2 classification depends on either way.

### Hours proposal — for `commercial-agent` behind `APPROVE TIMESHEET`

| WBS | Proposed actual | Evidence |
|---|---|---|
| 0.4 | 4.5 h | 4 entities (~35 columns), 5 option sets, 6 relationships, 1 field security profile (18 permissions), 3 role files extended, 3 settings files updated, 3 real defects investigated/fixed/verified (`IMP-0236`–`0240`), `contract/tad-deferrals.json` reconciled, `pipeline.yml`/`build.yml` updated and both preflights re-passed, full 849-test suite re-run twice |

**4.5 h against WBS `0.4`**, below its 5.0–8.0 h estimate (`contract/wbs.json`) — reasonable for a
remainder task, since the other four tables (`rev_applicant`, `rev_application`, `rev_setting`,
`rev_errorlog`) and `rev_review` (`6.4`) were built and billed in earlier sessions. `0.4`'s
`actual_hours` field is currently empty across its whole history; this proposal covers only this
dispatch's slice, not the task's cumulative total. No hours proposed as `system` — every change
here is delivery work against the client's own solution and build pipeline, not tooling on
`agents/`, `skills/` or this delivery system's own scripts.

### Improvement log

`IMPROVEMENT LOG: 7 entries appended — IMP-0234, IMP-0235, IMP-0236, IMP-0237, IMP-0238, IMP-0239,
IMP-0240 | digest regenerated: YES`. `IMP-0234`/`IMP-0235` (`data-agent`, friction) and `IMP-0238`
(`identity-agent`, blocker) were logged by the sub-agents that found them; `IMP-0236` (blocker),
`IMP-0237`, `IMP-0239` and `IMP-0240` (rework) were logged by `development-agent` while fixing the
first three. `python3 scripts/generate-known-failure-modes.py` re-run after every append; the
digest now carries 237 entries.

## Revision — WBS 0.4 remainder fix: `rev_name` is not securable on a primary name column (2026-08-23)

### What happened

The reviewer ran `provisioning/dataverse/ensure-schema.ps1 -Env dev` by hand against DEV (this
session's own permission classifier refuses that live write). `rev_bankaccount` and
`rev_payment` both failed table creation outright with `0x8004f501`: **"The field 'rev_name' is
not securable."** Both tables' `Entity.xml` marked their primary name attribute `rev_name` as
`IsSecured=1` — the prior revision framed this as a deliberate, documented deviation from this
solution's usual convention, following TAD §6's literal "every column" / "all ... columns"
wording. That framing was itself the defect: a Dataverse table's primary name attribute can
never carry field-level security, full stop. This is a hard platform limit, not a configuration
choice, and it was never checked against a real create call before now.

### What was fixed

1. **`rev_bankaccount.rev_name` and `rev_payment.rev_name` are now `IsSecured=0`.** Both
   Entity.xml headers are corrected to state the ground-truthed platform limit instead of the
   prior "deliberate deviation" framing —
   [`Entities/rev_bankaccount/Entity.xml#L22`](src/solutions/RevitaliseGrantAutomation/Entities/rev_bankaccount/Entity.xml#L22),
   [`Entities/rev_payment/Entity.xml#L17`](src/solutions/RevitaliseGrantAutomation/Entities/rev_payment/Entity.xml#L17).
   Neither value is sensitive on its own (an account nickname/masked last four, or a plain
   autonumber payment reference) — every genuinely sensitive column on both tables stays
   `IsSecured=1`.
2. **`REV_FinanceOnly` drops from 18 to 16 field permissions** — the two `rev_name` entries are
   removed, since a field permission cannot target an unsecured column
   ([`Other/FieldSecurityProfiles.xml#L622`](src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml#L622)).
   The solution-wide secured-column total drops from 69 to **67**, confirmed live:
   `verify-field-security-coverage.py` now reports `PASS - 67 secured column(s)`. Every place
   that stated the old counts as literals is corrected: `EnsureSchema.Tests.ps1`'s three
   `Should -Be` assertions ([L376](src/tests/provisioning/EnsureSchema.Tests.ps1#L376),
   [L377](src/tests/provisioning/EnsureSchema.Tests.ps1#L377),
   [L733](src/tests/provisioning/EnsureSchema.Tests.ps1#L733),
   [L812](src/tests/provisioning/EnsureSchema.Tests.ps1#L812)) and its own docstring/`It`-name
   prose, `config/revitalise-grant-automation-build.yml#L268`, and
   `config/revitalise-grant-automation-pipeline.yml`'s DEV prerequisite step. `verify-field-security-coverage.py`
   ([C-TECH-067](constraints/technology/technology-constraints.md#L137)) and
   `verify-source-derived-test-counts.py` both already derive these counts from source rather
   than hand-checking a list, so no exemption was needed in either — the fix was correcting the
   literal `Should -Be` numbers and the prose, not the checkers themselves.
3. **`A-FIN-03` is closed VERIFIED, not by inference.** The same live run created
   `REV_FinanceOnly` in DEV; its real `fieldsecurityprofileid`
   (`93d339bc-289f-f111-b8de-7ced8d43e87d`) was confirmed by a read-only
   `fieldsecurityprofiles?$filter=name eq 'REV_FinanceOnly'&$select=fieldsecurityprofileid` query
   and substituted into
   [`Other/FieldSecurityProfiles.xml#L622`](src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml#L622)
   and [`Other/Solution.xml#L249`](src/solutions/RevitaliseGrantAutomation/Other/Solution.xml#L249),
   replacing the `{PENDING-PROFILE-ID-REV-FINANCEONLY}` sentinel. `verify-guid-syntax.py` now
   reports 0 errors (was 2). See the register update above.
4. **TAD §6 corrected** to state the exception rather than the unqualified "every column" /
   "all ... columns" wording:
   [architecture doc §6, security table row](docs/architecture/revitalise-grant-automation-architecture.md#L780)
   and the [note directly below it](docs/architecture/revitalise-grant-automation-architecture.md#L782),
   plus the [`rev_bankaccount` column list entry](docs/architecture/revitalise-grant-automation-architecture.md#L354).
   This is a documentation correction, not a redesign: the actual sensitive values (account
   number, sort code, amount, method, status) remain on separate, correctly-secured columns: no
   ADR change was needed since ADR-002/ADR-013 never asserted the primary name specifically, only
   TAD §6's own prose did.

### §10 Unvalidated Assumptions Register — update

`A-FIN-03` closes **VERIFIED 2026-08-23** (see row above). `A-FIN-01` (the `Restrict`-delete
relationship shape) and `A-FIN-02` (the `Decimal` attribute Web API shape) remain **OPEN** —
both tables failed creation outright on this run, so their relationships and the `rev_amount`
attribute never reached the platform to be tested. They will be exercised on the reviewer's
next `ensure-schema.ps1 -Env dev` re-run, which is idempotent and will retry only
`rev_bankaccount`/`rev_payment` and everything that cascaded from them.

### §11 Verification Evidence — update

**Highest level executed for this fix: V3 (accepted by the target)** for the finding itself —
the defect was found by a live create call failing, and `REV_FinanceOnly`'s real id was
confirmed by a live read. The source fix itself is V1 (well-formed, locally asserted) until the
reviewer's re-run creates `rev_bankaccount`/`rev_payment` for real.

| Gate | Result |
|---|---|
| `verify-field-security-coverage.py` | PASS — 67 secured columns, all released, 1 reviewed exemption |
| `verify-guid-syntax.py` | OK — 0 errors (was 2) |
| `verify-solution-root-components.py` | PASS — 64 components, all resolve |
| `verify-source-derived-test-counts.py` | SOFT WARN — 10 fragile literals, unchanged from before this fix and none introduced by it (unrelated pre-existing findings in `DataverseScripts.Tests.ps1`/`DeploymentSettings.Tests.ps1`) |
| `verify-build-config.py` | PASS — 40 steps, 29 gates |
| `verify-pipeline-config.py` | PASS — 83 steps across 3 environments |
| `verify-code-app-column-bindings.py` | OK — 63 forbidden columns (unchanged — the trustee portal names neither `rev_bankaccount` nor `rev_payment`, so this fix does not touch its scope) |

**Tool warnings: 0 new, 0 untriaged.** `verify-source-derived-test-counts.py`'s 10 warnings are
pre-existing and unrelated to this fix (not touched by it).

**Diagnostic components created and removed: none.**

### What you need to decide

Nothing new — `A-FIN-01`/`A-FIN-02` are unaffected by this fix and stay open pending the
reviewer's re-run, exactly as before.

### Hours proposal — addendum for `commercial-agent` behind `APPROVE TIMESHEET`

| WBS | Proposed actual | Evidence |
|---|---|---|
| 0.4 | 0.5 h | Diagnosed one live create-call failure across two tables to a single root cause, corrected 2 Entity.xml files, `Other/FieldSecurityProfiles.xml`, `Other/Solution.xml`, 3 literal test counts + prose in `EnsureSchema.Tests.ps1`, 2 config files' comments, 1 TAD section; re-ran 6 verification gates |

**0.5 h against WBS `0.4`**, additive to the 4.5 h already proposed for this task in the revision
above — this is a follow-up fix to a defect the reviewer's own live run surfaced in that same
task's deliverable, not new scope. No hours proposed as `system`.

### Improvement log

`IMPROVEMENT LOG: 1 entry appended — IMP-0249 | digest regenerated: YES`. Logged by
`development-agent`, class `platform-contract-guessed-not-groundtruthed`
([x30 in the digest](logs/known-failure-modes.md#L31)), severity `blocker`, `observable_at: V3`.

---

## Revision — WBS 0.4 remainder fix #2: two unrelated defects from the same live run (2026-08-24)

### What happened

The reviewer re-ran `provisioning/dataverse/ensure-schema.ps1 -Env dev` by hand against DEV. It
succeeded broadly — all four finance tables, their columns, relationships and most privileges and
field permissions are now live — and reported **9 `FAILED` lines from two root causes that share
nothing but the run they appeared in.**

Both are fixed. **Neither fix is verified live**, because the re-run is a write this session's
permission classifier refuses; see §11 below for exactly what is proven and what is not.

### Defect 1 — four privileges that cannot exist

`rev_provider` is
[`OwnershipType=OrganizationOwned`](src/solutions/RevitaliseGrantAutomation/Entities/rev_provider/Entity.xml#L170),
and Dataverse never creates an Assign or a Share privilege for an organization-owned table: there
is no individual owner to assign a row to, or to share it from. Both roles requested them anyway,
so four bindings named privilege GUIDs that cannot be resolved.

**Ground truth first, because this had already been inferred twice.** A read-only query against
DEV listed the privileges that actually exist for all ten custom tables, cross-checked against
each table's live `OwnershipType`. The rule is exact and has no exception in this org:

| OwnershipType | Tables | Privileges that exist |
|---|---|---|
| `OrganizationOwned` | `rev_provider`, `rev_anonymisedstatistic`, `rev_errorlog`, `rev_setting` | Create, Read, Write, Delete, Append, AppendTo |
| `UserOwned` | `rev_applicant`, `rev_application`, `rev_grant`, `rev_bankaccount`, `rev_payment`, `rev_review` | all eight, including Assign and Share |

**`Delete` exists on an organization-owned table.** That matters: the earlier dispatch read
`rev_anonymisedstatistic`'s role block — which omits Assign, Share *and* Delete — as the worked
correct example, which left it genuinely ambiguous whether Delete was unavailable too. It is not.
Withholding Delete there is a deliberate policy decision under
[C-DOM-021](constraints/domain/domain-constraints.md#L59), and conflating a policy choice with a
platform limit is what makes this class easy to get wrong in both directions.

1. **The four impossible requests are removed**, each block now carrying the live inventory and
   the reason —
   [`REV Admin.xml#L101`](src/solutions/RevitaliseGrantAutomation/Roles/REV%20Admin/REV%20Admin.xml#L101)
   and
   [`REV Service Automation.xml#L92`](src/solutions/RevitaliseGrantAutomation/Roles/REV%20Service%20Automation/REV%20Service%20Automation.xml#L92).
   No other role file was affected: a solution-wide grep confirms `rev_provider` was the only
   organization-owned table with an Assign or Share request anywhere.
2. **A general gate replaces the instance fix**, because this class stands at 32 occurrences and
   [`skills/how-to-promote-a-finding.md`](skills/how-to-promote-a-finding.md) forbids a second
   instance patch. [`scripts/verify-role-privilege-ownership.py`](scripts/verify-role-privilege-ownership.py)
   derives the legal privilege set for every table from that table's own `<OwnershipType>` and
   fails on any role requesting one outside it —
   [the check itself](scripts/verify-role-privilege-ownership.py#L203). It is wired as build step
   [`role-privilege-ownership`](config/revitalise-grant-automation-build.yml#L456). **It holds no
   list of which tables are organization-owned**
   ([C-TECH-067](constraints/technology/technology-constraints.md#L137)), so a table that changes
   ownership, or a new organization-owned table added next month, is checked for free. It reports
   only a privilege the platform cannot create, never one deliberately withheld.
3. **The error message named one cause, and it was the wrong one.** It said only *"the table has
   not been created yet; run this script's entity step first"* — actively misleading here, since
   the same run had printed `EXISTS — Table 'rev_provider'` moments earlier. Anyone following the
   remedy as written would have re-run a step that was already correct. It now names both causes
   and gives the query that distinguishes them:
   [`ensure-schema.ps1#L690`](provisioning/dataverse/ensure-schema.ps1#L690).

### Defect 2 — five secured lookup columns that were created unsecured

Five field permissions failed with `0x8004f508` — *"attribute is NOT secured for entity
fieldpermission"* — for `rev_bankaccount.rev_applicantid`, `rev_bankaccount.rev_providerid`,
`rev_payment.rev_grantid`, `rev_payment.rev_bankaccountid` and `rev_payment.rev_providerid`.

**The incoming diagnosis was wrong, and checking it changed the fix.** The finding stated these
columns "were never actually marked `IsSecured=1` anywhere in source" and that this project's
Relationships XML shape has no way to declare it. Both are false. Each of the five is a full
attribute element in its own `Entity.xml` — see
[`rev_payment/Entity.xml#L97`](src/solutions/RevitaliseGrantAutomation/Entities/rev_payment/Entity.xml#L97)
— and `ConvertFrom-RevEntityXml` has parsed that flag for every attribute type, lookups included,
since it was written
([`ensure-schema-helpers.psm1#L242`](provisioning/dataverse/ensure-schema-helpers.psm1#L242)).

**The real cause was one omitted line.** A Dataverse lookup cannot be created as a standalone
attribute — `ConvertTo-RevAttributeBody` throws for `Type 'lookup'` — so every lookup is created
as the inline `Lookup` deep-insert inside `ConvertTo-RevRelationshipBody`. That body set
DisplayName, Description and RequiredLevel, and dropped `IsSecured` on the floor. So the flag was
declared, released by the profile, checked by a gate, and never sent.

**Was securing them actually intended?** Yes, and the TAD is specific rather than blanket about
it: [§3's `rev_bankaccount` entry](docs/architecture/revitalise-grant-automation-architecture.md#L354)
names `rev_applicantid` in its own Tier 4 column list, and
[§3's `rev_payment` entry](docs/architecture/revitalise-grant-automation-architecture.md#L363)
names all three of its lookups. This is **not** the same shape as
[IMP-0249's overclaim](logs/known-failure-modes.md#L146): that was a blanket "every column"
sentence colliding with a hard platform limit, and here the platform has no objection at all.

**Ground-truthed, not inferred a second time.** A read-only query returned every column's
securability on both tables. All five report
`CanBeSecuredForRead`/`ForCreate`/`ForUpdate` = `True` with `IsSecured` = `False` — the platform
was willing and the source asked; only the sender dropped it. The same read shows `rev_name` on
both tables at `CanBeSecuredForRead=False`, independently re-confirming the separate primary-name
limit.

1. **The creating function now carries the flag** —
   [`ensure-schema-helpers.psm1#L740`](provisioning/dataverse/ensure-schema-helpers.psm1#L740),
   a plain `Edm.Boolean` exactly as on every non-lookup column, set only when the source declares
   it.
2. **That fix alone would have left DEV permanently unsecured**, and this is the part worth
   reading twice. The relationship step is **create-only**: an existing relationship reports
   `EXISTS` and is skipped, so `ConvertTo-RevRelationshipBody` is never called for it again. In
   DEV all five relationships already exist. A fresh TST/ACC or PRD would have come up correct
   while DEV stayed unsecured on every future re-run — same source, same script, two environments
   with different security, every gate green.
   [Step 3b](provisioning/dataverse/ensure-schema.ps1#L506) is the repair: an idempotent
   reconcile that PATCHes `IsSecured` onto an already-existing lookup, scoped to relationships
   that reported `EXISTS`
   ([the scoping](provisioning/dataverse/ensure-schema.ps1#L568)) so a just-created lookup costs
   no round-trip. **One direction only** — unsecured to secured, never the reverse: removing a
   column-level control is a decision for someone who can see who currently reads the column. It
   runs before step 6, and refuses to PATCH a column the platform reports as not securable,
   naming the limit instead.
3. **A gate that reads the creating code, because no source-only gate could have caught this.**
   The check the finding proposed — *every attribute named in `FieldSecurityProfiles.xml` resolves
   to something declaring `IsSecured=1`* — **already existed** as
   `verify-field-security-coverage.py`'s POINTLESS PERMISSION check, and it **passed**, correctly,
   because source was entirely self-consistent. The gap was between source and the code that
   creates the column, so the new fourth check asserts that
   `ConvertTo-RevRelationshipBody` actually sets `IsSecured` whenever any secured lookup exists —
   [the check](scripts/verify-field-security-coverage.py#L338). Proven against the real pre-fix
   tree, not only fixtures: removing that one line makes the gate exit 1 naming all five columns.

### A residual worth knowing: securing a lookup does not secure its name companion

Dataverse maintains a `<lookup>name` String column beside every lookup, holding the **related
row's primary name value**, and every one reports `CanBeSecuredForRead=False`. Securing the lookup
hides the GUID, not the text. This is structurally
[IMP-0047's Money `_base` problem](logs/known-failure-modes.md#L226) in a new shape, and it now
warns on every build —
[the warning](scripts/verify-field-security-coverage.py#L359).

The residual is narrow but not empty. `rev_applicant`, `rev_grant` and `rev_bankaccount` all have
autonumber or masked primary names, so `rev_applicantidname` yields `REV-A-00001` and
`rev_grantidname` yields `GR-2026-00001` — pseudonymous references, no identity. **The exception
is `rev_provideridname`, which yields the provider's real organisation name** on both
`rev_bankaccount` and `rev_payment`. The control there is the table privilege, not column
security: per [NFR-002](docs/architecture/revitalise-grant-automation-architecture.md#L971) no
role but Finance holds Read on either table. That is the same basis on which the reviewer accepted
the Money residual on 2026-08-19, so it is reported here rather than treated as a new decision —
but it must be re-checked before any role is granted Read on either table.

### §10 Unvalidated Assumptions Register — update

Two rows close, two open. `A-FIN-01` and `A-FIN-02` **close VERIFIED on live reads, not on the
inference that "the run succeeded so the shapes must be fine"** — both rows above are struck
through with their evidence:

- **`A-FIN-02` closes outright.** `rev_payment.rev_amount` reads back live as
  `AttributeType=Decimal`, `Precision=2`, `MinValue=0`, `MaxValue=100000000`, `IsSecured=True` —
  every value matching source.
- **`A-FIN-01` closes at V3 with a stated V5 residual.** All 9 declared relationships read back
  with a `CascadeConfiguration.Delete` exactly matching their source `<CascadeDelete>` — 5
  `Cascade`, 3 `Restrict` (all three Provider relationships), 1 `RemoveLink`. The `Restrict`
  *shape* is confirmed accepted; nobody has attempted to delete a referenced Provider and watched
  the platform refuse, so the enforcement behaviour is **not** claimed.

`A-FIN-03` was already closed. Two new rows follow.

| ID | Assumption | Where | Confidence | Why it is a guess | How to close it | Status |
|---|---|---|---|---|---|---|
| A-FIN-04 | An attribute-level metadata `PATCH` to `EntityDefinitions(LogicalName='<t>')/Attributes(LogicalName='<a>')` carrying `@odata.type: LookupAttributeMetadata` + `IsSecured: true`, with `MSCRM.MergeLabels: true`, is accepted and sets the flag | [`ensure-schema.ps1#L506`](provisioning/dataverse/ensure-schema.ps1#L506) | E2 | No attribute-level metadata PATCH has ever been issued by this project. The header requirement and the `@odata.type` requirement are both modelled on [`ensure-auditing.ps1`'s entity-level PATCH](provisioning/dataverse/ensure-auditing.ps1#L168), which IS ground-truthed against a live org — but an entity PATCH is not an attribute PATCH | Reviewer re-runs `ensure-schema.ps1 -Env dev`; require `CREATED — Column security on lookup '<t>.<a>'` on all five, then read back `EntityDefinitions(LogicalName='rev_payment')/Attributes(LogicalName='rev_grantid')?$select=IsSecured` and require `true` | **OPEN** |
| A-FIN-05 | `IsSecured` is honoured on the inline `Lookup` deep-insert of a `RelationshipDefinitions` POST, not only on a standalone attribute create | [`ensure-schema-helpers.psm1#L740`](provisioning/dataverse/ensure-schema-helpers.psm1#L740) | E2 | `IsSecured` is a documented plain `Edm.Boolean` on `AttributeMetadata`, which `LookupAttributeMetadata` derives from, and the deep-insert already carries four other inherited properties — but no lookup in this solution has ever been created secured, so the deep-insert has never been shown to honour it | Cannot be closed in DEV: all five relationships already exist, so this path is never taken there. It closes on the **first `ensure-schema.ps1` run against a fresh environment** (TST/ACC), where a `CREATED` relationship must be followed by `IsSecured=true` on its lookup with no step 3b PATCH having been needed | **OPEN — deferred to first fresh-environment run** |

`A-FIN-05` is the more interesting row: **it cannot be closed in the environment we have.** Step 3b
exists precisely because DEV can never exercise the create path again, which means the create-path
fix ships to TST/ACC and PRD carrying an assumption DEV structurally cannot test. That is stated
here rather than left to be discovered on a first PRD provision.

### §11 Verification Evidence — update

**Highest level executed: V3 (accepted by the target) for the diagnosis, V1/V2 for the fixes.**
The two defects were both found by live create calls failing, and every platform fact this
revision relies on was read live from DEV. **The fixes themselves are not verified live** — the
re-run is a write this session's permission classifier refuses — so no fix here may be reported
above V1, and A-FIN-04/A-FIN-05 stay OPEN.

What was executed live (reads only, never refused):

| Live query | Result |
|---|---|
| `privileges?$filter=endswith(name,'<table>')` × 10 tables | Assign and Share absent on all 4 organization-owned tables, present on all 6 user-owned. Delete present on all 10 |
| `EntityDefinitions(LogicalName='<t>')?$select=OwnershipType` × 10 | Matches source exactly on all 10 |
| `EntityDefinitions(...)/Attributes?$select=...,IsSecured,CanBeSecuredForRead,...` × 2 tables | All 5 lookups `CanBeSecuredForRead=True`, `IsSecured=False`; both `rev_name` `CanBeSecuredForRead=False`; all 5 `<lookup>name` companions `CanBeSecuredForRead=False` |
| `RelationshipDefinitions(SchemaName='<n>')` × 9 declared relationships | All 9 present, `CascadeConfiguration.Delete` matching source exactly: 5 `Cascade`, 3 `Restrict`, 1 `RemoveLink` — **closes A-FIN-01 at V3** |
| `.../Attributes(LogicalName='rev_amount')/Microsoft.Dynamics.CRM.DecimalAttributeMetadata` | `Decimal`, `Precision=2`, `Min=0`, `Max=100000000`, `IsSecured=True` — **closes A-FIN-02** |

Two query-shape facts fell out of those reads and are logged, because both were open questions in
`ensure-schema.ps1`'s own header:

- **`RelationshipDefinitions(SchemaName='x')?$select=SchemaName` works.** The script header flagged
  this alternate-key addressing as inferred by analogy and never confirmed. It is confirmed.
- **`CascadeConfiguration` may not appear in `$select`** — it is a complex property and Dataverse
  answers HTTP 400. Omit `$select` entirely and read it off the full response. This cost one failed
  query in this session and read, misleadingly, as all 9 relationships being absent.

| Gate | Result |
|---|---|
| `verify-role-privilege-ownership.py` (new) | **PASS** — 84 table privileges across 3 roles; 48 out-of-box skipped. `--selftest` OK over 5 fixtures, and a known-bad fixture on disk at [`src/tests/fixtures/known-bad/role-privilege-ownership/`](src/tests/fixtures/known-bad/role-privilege-ownership/) with 4 registered tests in [`BuildGates.Tests.ps1`](src/tests/build/BuildGates.Tests.ps1#L143) — including one asserting `prvDelete` is **never** flagged |
| ↳ against the real **pre-fix** role files | **exits 1, naming all 4** — reproduces the live failure exactly |
| `verify-field-security-coverage.py` | **PASS** — 67 secured columns, 5 secured lookups all deliverable, 2 warnings. `--selftest` OK over 7 fixtures (was 3) |
| ↳ against the real **pre-fix** helpers module | **exits 1, naming all 5** — the defect is reproducible from the gate |
| `EnsureSchema.Tests.ps1` | **45 of 45 pass** (was 42) — 3 new tests: the create path carries `IsSecured`, step 3b PATCHes a pre-existing lookup, step 3b refuses a non-securable column |
| Full suite via `src/tests/Invoke-Tests.ps1` | **874 passed, 1 failed, 1 skipped** — 876 tests, up from 868, this revision adding 8 (3 in `EnsureSchema.Tests.ps1`, 5 in `BuildGates.Tests.ps1`). The single failure is `verify-improvement-log --check`, which cannot pass while any `blocker` finding is unclosed. It was already red on `IMP-0252` (a review parked at `APPROVE IMPROVEMENTS`); this revision's own `IMP-0259` is a second `blocker`, and the 10-entry batch trigger now also fires. All three are remedied by a keyword, not by code — see the improvement-log note below |
| `verify-build-config.py` | PASS — 41 steps, 30 gates (was 40 / 29) |
| `verify-pipeline-config.py`, `verify-workflow-syntax.py`, `verify-tad-coverage.py`, `verify-source-reader-plurality.py`, `verify-field-length-limits.py`, `verify-guid-syntax.py`, `verify-solution-root-components.py`, `verify-component-shape.py`, `verify-source-parses.py`, `verify-column-security-membership.py`, `verify-domain-invariants.py`, `verify-assumption-register.py`, `verify-toolchain-claims.py`, `verify-constraint-verifiers.py` | all exit 0 |
| `verify-source-derived-test-counts.py` | SOFT WARN — 10 fragile literals, **unchanged**: the three counts in this revision's new tests are all derived from source, none hand-typed |
| `verify-derived-counts.py` | SOFT WARN — 6 drifted claims, all pre-existing (`51` where source now says `67`). The two in this document are corrected; the other four are named under "What is still open" |

**Tool warnings: 2 accepted with rationale (both in `verify-field-security-coverage.py` — the
Money `_base` twin, accepted 2026-08-19, and the lookup name companion, new and reported above),
0 unresolved, 0 untriaged.**

**Diagnostic components created and removed: none.** The two live read scripts were written to
the session scratchpad, never to the repository.

### What is still open

**A-FIN-04 and A-FIN-05 are OPEN, and one of them cannot be closed here.** The reviewer's re-run
closes A-FIN-04; A-FIN-05 waits for a first fresh-environment provision.

**Four `51`-where-source-says-`67` claims remain, all outside this task.** Two are in historical
records — a build-session handover and improvement review 5 — where changing a dated statement of
what was true then is arguably wrong, and the registry is what tracks the drift. The third is
[`REV Trustee.xml#L73`](src/solutions/RevitaliseGrantAutomation/Roles/REV%20Trustee/REV%20Trustee.xml#L73),
which belongs to WBS 6.4, not 0.4.

**One HARD constraint's own `Verify By` is now stale.**
[C-TECH-070](constraints/technology/technology-constraints.md#L141) says the selftest covers
"3 fixtures"; it covers 7. Constraint files are `improvement-agent`'s to edit, not mine, so this
is logged rather than fixed.

### §10 Unvalidated Assumptions Register — second update (2026-08-24, IMP-0272/IMP-0273)

The reviewer's live re-run of `ensure-schema.ps1 -Env dev` resolved `A-FIN-04` — **negatively**.
All five step-3b PATCH calls failed identically:
`{"error":{"message":"The requested resource does not support http method 'PATCH'."}}`
(`IMP-0272`). Per this agent's own rule ("every §10 assumption that closes as WRONG gets an
entry — the register predicted it, so the finding is free"), it closes as wrong rather than
being deleted:

| ID | Assumption | Status |
|---|---|---|
| ~~A-FIN-04~~ | ~~An attribute-level metadata `PATCH` to `EntityDefinitions(...)/Attributes(...)` carrying `@odata.type` + `IsSecured: true` is accepted and sets the flag~~ | **CLOSED — WRONG.** Live: `PATCH` is not a supported verb on this endpoint at all (`IMP-0272`) |

`IMP-0272` itself proposed a fix (append a derived-type cast segment to the same `PATCH` call) that
this dispatch did **not** apply as written, for the reason `skills/how-to-log-an-improvement.md`
gives explicitly: a finding's `root_cause`/`proposed_change` is a hypothesis, to be re-verified
against source (or, here, against the platform's own documentation) before being built, not
treated as a work order. Re-verifying against a **fetched, worked Microsoft Learn example**
(`create-update-column-definitions-using-web-api.md`, "Update a column" — the same page this
script already cites for column *creation*) showed the documented shape is `PUT`, full-object
body, cast only on the preparatory `GET`, never on the write URI — not `PATCH` plus a cast. That
is the fix now in [`ensure-schema.ps1` step 3b](provisioning/dataverse/ensure-schema.ps1#L529),
and `IMP-0273` records why `IMP-0272`'s own proposal was superseded rather than applied verbatim.

| ID | Assumption | Where | Confidence | Why it is a guess | How to close it | Status |
|---|---|---|---|---|---|---|
| A-FIN-06 | A full-object `PUT` to the UNCAST `EntityDefinitions(LogicalName='<t>')/Attributes(LogicalName='<a>')` — body built from a prior `GET` through the `Microsoft.Dynamics.CRM.LookupAttributeMetadata` cast, `@odata.type` added, `@odata.context` stripped, `IsSecured` flipped to `true` — is accepted and persists the flag | [`ensure-schema.ps1#L607`](provisioning/dataverse/ensure-schema.ps1#L607) | E1 | This is the platform's own documented pattern for a `BooleanAttributeMetadata` column (fetched, worked example); it has never been exercised against a `LookupAttributeMetadata` column by this project, and the harness that blocked `A-FIN-04`'s verification blocks this write too | Reviewer re-runs `ensure-schema.ps1 -Env dev`; require `CREATED — Column security on lookup '<t>.<a>'` on all five, then read back `EntityDefinitions(LogicalName='rev_payment')/Attributes(LogicalName='rev_grantid')?$select=IsSecured` and require `true`, and confirm step 6's five `REV_FinanceOnly` field permissions on these columns move from `FAILED (0x8004f508)` to `CREATED`/`EXISTS` | **OPEN** |

**Sibling-bug check (requested alongside this fix):** grepped every `-Method PATCH` call in both
`ensure-schema.ps1` and `ensure-auditing.ps1`. Three others exist —
[`ensure-schema.ps1#L888`](provisioning/dataverse/ensure-schema.ps1#L888) (`fieldpermissions`),
[`ensure-auditing.ps1#L129`](provisioning/dataverse/ensure-auditing.ps1#L129) (`organizations`), and
[`ensure-auditing.ps1#L170`](provisioning/dataverse/ensure-auditing.ps1#L170)
(`EntityDefinitions(LogicalName='x')`, entity-level `IsAuditEnabled`) — and none targets a
polymorphic collection the way `Attributes` is: `fieldpermissions` and `organizations` are plain
data entities, and `EntityDefinitions` has one concrete type (`EntityMetadata`), not several
derived ones. So `IMP-0272`'s specific mechanism (a polymorphic collection rejecting the base,
uncast write) has no second instance here. One open question is flagged rather than fixed: the
same Microsoft Learn page states its `PUT`-not-`PATCH` rule "applies to entity attributes **and
entities**", which in the strict documented sense should also cover
`ensure-auditing.ps1`'s entity-level `PATCH` — yet that call has a live success on record with no
`FAILED` line ever logged against it (`IMP-0178`/pipeline log 2026-08-22). That call is left
unchanged: it is not confirmed broken, changing working code on a documentation-only concern
would be a guess in the other direction, and this is recorded so a future audit-switch failure is
checked against this note first rather than re-diagnosed from nothing.

### What you need to decide

**Re-run `ensure-schema.ps1 -Env dev`.** Both original fixes are source-side; A-FIN-02/A-FIN-01
close at V3, A-FIN-05 waits on a fresh environment, and A-FIN-06 (the corrected step-3b fix) is
the one this re-run settles. The run is idempotent and will report `EXISTS` for everything
already correct.

```
pwsh -NoProfile -File provisioning/dataverse/ensure-schema.ps1 -Env dev
```

Expect: the 4 privilege lines gone entirely (they are no longer requested), 5 new
`CREATED — Column security on lookup '<t>.<a>'` lines from step 3b, and the 5 previously-failing
field permissions now `CREATED`. **0 `FAILED` lines is the pass condition.** Then confirm the flag
actually landed rather than trusting the `CREATED`:

```
EntityDefinitions(LogicalName='rev_payment')/Attributes(LogicalName='rev_grantid')?$select=IsSecured
```

**Accept or reject the lookup name-companion residual.** `rev_provideridname` exposes the
provider's organisation name to anyone with table Read on `rev_bankaccount` or `rev_payment`, and
column security cannot cover it. The recommendation is to **accept**, on the same basis as the
Money residual: only Finance holds Read on either table, and Finance is entitled to know which
provider a payment names. Rejecting it would mean removing the provider lookups and reaching
Provider transitively through Grant, which is a TAD §3.3 change and a change order.

Nothing else. `A-FIN-01` and `A-FIN-02` closed on live reads and need no decision — though note
`A-FIN-01`'s V5 residual: the `Restrict` cascade's *shape* is confirmed, its *enforcement* has
never been exercised. Worth one deliberate attempt to delete a referenced Provider whenever
someone is next in DEV with delete rights.

### Hours proposal — addendum for `commercial-agent` behind `APPROVE TIMESHEET`

| WBS | Proposed actual | Evidence |
|---|---|---|
| 0.4 | 1.5 h | Diagnosed 9 live `FAILED` lines to two unrelated root causes; ran 2 read-only live ground-truth queries covering 10 tables' privileges and 30 columns' securability; corrected 2 role files, `ensure-schema-helpers.psm1`, `ensure-schema.ps1` (1 new reconcile step + 1 error message); wrote 1 new build gate with 5 selftest fixtures and extended another with 4; added 3 Pester tests and corrected 2 fixtures; both new gates proven against the real pre-fix tree; ran 18 verification gates plus the 871-test suite |
| — | 0.4 h `system` | 4 improvement-log findings including a correction to an incoming finding's own diagnosis, plus digest regeneration |

**1.5 h against WBS `0.4`**, additive to the 4.5 h + 0.5 h already proposed for this task — a
follow-up fix to defects the reviewer's own live run surfaced in that task's deliverable, not new
scope. **0.4 h as `system`**, not billable.

### Improvement log

`IMPROVEMENT LOG: 6 entries appended — IMP-0256, IMP-0257, IMP-0258, IMP-0259, IMP-0260, IMP-0261 | digest regenerated: YES`

Two record platform facts read live rather than inferred, so nobody infers them a third time. One
records that an incoming finding's `root_cause` and `proposed_change` were both wrong in the same
direction, and would have produced a new XML mechanism nothing needed plus a gate that already
existed and had already passed over the defect. One records the create-only/reconcile asymmetry
that would have left DEV unsecured while a fresh PRD came up correct. One records the stale
fixture count in `C-TECH-070`'s own `Verify By`.
One records two `RelationshipDefinitions` query-shape facts that were open caveats in
`ensure-schema.ps1`'s own header — the alternate-key addressing it doubted works, and
`CascadeConfiguration` may not appear in `$select` (HTTP 400, which reads exactly like absence).

`IMP-0259` is severity `blocker`, deliberately: the five unsecured Tier 4 columns it describes are
live in DEV **right now**, so this is a shipped defect and not a hypothetical one. It therefore
fires the immediate-routing trigger, and with these six entries the 10-entry batch trigger fires
too. `IMP-0252` was already parked at `APPROVE IMPROVEMENTS` before this dispatch. All of it is
one keyword against `improvement-agent`, not another delivery session.

## Revision — `ensure-auditing.ps1`'s table-level write corrected to PUT (WBS 0.4, IMP-0276, 2026-08-24)

### What happened

The reviewer ran [`ensure-auditing.ps1 -Env dev`](provisioning/dataverse/ensure-auditing.ps1) live.
All four WBS 0.4 finance tables (`rev_provider`, `rev_bankaccount`, `rev_payment`,
`rev_anonymisedstatistic`) failed with `0x80060888 "Operation not supported on EntityMetadata"`. The
six pre-existing tables reported `EXISTS`, but only because `IsAuditEnabled` was already `true` on
every one of them and the script's own idempotency guard (read-then-write-only-if-different) skipped
the write path entirely — none of those six "successes" had ever actually exercised it. The reviewer
closed the live gap by hand in the admin portal; the finding (`IMP-0276`) is that the script itself
remained broken for the next table, in any environment, that needs the flag flipped for real.

### What was fixed

[`ensure-auditing.ps1`'s table-level auditing block](provisioning/dataverse/ensure-auditing.ps1#L139)
sent `PATCH EntityDefinitions(LogicalName='<t>')` with a partial body
(`{ IsAuditEnabled: { Value: true } }`). Per Microsoft's own *"Create and update table definitions
using the Web API"* page — the same one `IMP-0273` already fetched for `ensure-schema.ps1` step 3b —
metadata updates are **PUT-only, with the complete current object**: *"You can't use the PATCH
method to update data model entities ... you can't update individual properties."* This generalises
`IMP-0272`/`IMP-0273` (a fix scoped to the polymorphic `Attributes` collection) to `EntityDefinitions`
itself: the PATCH prohibition is not a polymorphism artefact, it applies to entity metadata writes
generally.

The block now [GETs the entity with no `$select`](provisioning/dataverse/ensure-auditing.ps1#L177),
strips every `@odata.*` response annotation, mutates only `IsAuditEnabled.Value`, and
[PUTs the whole object back](provisioning/dataverse/ensure-auditing.ps1#L200) to the same, **uncast**
URI, keeping the `MSCRM.MergeLabels: true` header the old PATCH already needed. Unlike step 3b,
`EntityDefinitions` is **not** polymorphic — one concrete type, `EntityMetadata` — so no cast segment
and no `@odata.type` appear anywhere in this block, on the GET or on the write. The
organisation-level `PATCH` earlier in the same script (`organizations({id})`) is unaffected: that is
an ordinary data record, not a metadata endpoint, and normal PATCH semantics apply there.

**Two stale claims this same defect had left standing were also corrected**, because both had
pointed straight at the code this finding disproved:

- [`ensure-schema.ps1#L143`](provisioning/dataverse/ensure-schema.ps1#L143) (step 3's Web API shapes
  ledger) named `ensure-auditing.ps1`'s entity-level PATCH as "documented as confirmed live" and the
  one still-open exception to the PUT-only rule — now closed, recording that it failed live exactly
  as the rule predicted.
- [`ensure-schema.ps1#L580`](provisioning/dataverse/ensure-schema.ps1#L580) (step 3b's own header)
  cited the same PATCH as "that one confirmed live" when explaining why it had been the wrong
  precedent for step 3b — now annotated with why "confirmed live" was never a real confirmation.
- [`knowledge/technology/testing-tools.md#L269`](knowledge/technology/testing-tools.md#L269) stated
  outright that the entity-level PATCH "IS ground-truthed working live" — rewritten to record the
  actual mechanism (six runs that all skipped the write, not six runs that exercised it).

None of the three were touched idly: each was a document this repository held that the live run
contradicted (improvement-log trigger 2), and each was exactly the kind of false precedent that let
this defect ship in the first place — `ensure-schema.ps1`'s own step-3b comment had already flagged
the exception **by name** and it sat unreconciled until a live run needed the write for real.

### §10 Unvalidated Assumptions Register — new row

| ID | Assumption | Where | Confidence | Why it is a guess | How to close it | Status |
|---|---|---|---|---|---|---|
| A-FIN-07 | A full-object `PUT` to the uncast `EntityDefinitions(LogicalName='<t>')` — body built from a prior `GET` with no `$select`, every `@odata.*` annotation stripped, `IsAuditEnabled.Value` flipped to `true` — is accepted and persists the flag | [`ensure-auditing.ps1#L171`](provisioning/dataverse/ensure-auditing.ps1#L171) | E1 | This is the platform's own documented pattern (fetched worked example), already proven at V1/V2 (parses, matches the doc, full Pester suite green) but never exercised against `EntityDefinitions` as a write target by this project, and the harness that blocked `A-FIN-04`/`A-FIN-06`'s live verification blocks this write too | Reviewer re-runs `ensure-auditing.ps1 -Env dev`; require `CREATED` on all 4 finance-table lines (and `EXISTS` on the 6 pre-existing ones) with zero `FAILED`, then read back `EntityDefinitions(LogicalName='rev_provider')?$select=IsAuditEnabled` and require `true` | **OPEN** |

### §11 Verification Evidence — update

| Check | Result |
|---|---|
| `pwsh` AST parse of `ensure-auditing.ps1` | **PASS — 0 errors** |
| `Invoke-Pester -Path src/tests/provisioning/EnsureSchema.Tests.ps1, ScriptContract.Tests.ps1, DataverseScripts.Tests.ps1` | **476/476 PASS** |
| `pwsh -File src/tests/Invoke-Tests.ps1 -Path provisioning` (the path CI actually uses, IMP-0026) | **611 passed, 0 failed, 1 skipped (pre-existing)** |
| `python3 scripts/verify-improvement-log.py` | **OK — 274 entries (27 NEW, 247 APPLIED, 0 REJECTED)** |
| `python3 scripts/generate-known-failure-modes.py` | **wrote 274 entries, 274 distinct lessons** |

**Verification level reached: V1/V2.** The script is well-formed and matches the platform's own
documented shape, and the full behavioural Pester suite — rewritten to assert the new verb, the
full-object round-trip, and the `@odata.context` strip — passes against a faked Web API. **No V3 is
claimed**: this session has no live Dataverse credentials, per the same harness constraint recorded
against every prior instance of this class (`IMP-0272`/`IMP-0273`). A-FIN-07 stays OPEN until the
reviewer's live re-run.

**Test fixtures corrected, not just added** — `src/tests/provisioning/DataverseScripts.Tests.ps1`'s
`ensure-auditing.ps1` `Describe` block:

- *["enables table auditing with a full-object PUT…"](src/tests/provisioning/DataverseScripts.Tests.ps1#L440)* —
  registers `PUT` instead of `PATCH`, asserts 4 `PUT` calls (one per settings-declared table), that
  each carries `MSCRM.MergeLabels`, that the fetched `LogicalName` round-trips onto the write body
  unchanged, that `@odata.context` never reaches the write, and that the write URI carries no
  `$select`. Uses a **scriptblock** GET fixture rather than one shared literal object — the identical
  fixture defect `EnsureSchema.Tests.ps1` already had to avoid for step 3b (a shared reference would
  let table 1's in-place mutation leak into table 2's "fetch", masking three of four real writes as
  false `EXISTS`).
- *["reports FAILED per table and exits 1 when the metadata PUT is refused"](src/tests/provisioning/DataverseScripts.Tests.ps1#L502)* —
  same scriptblock-fixture correction, `PUT` registered with `-StatusCode 403` in place of `PATCH`.
- *"reads `IsAuditEnabled` from `.Value`…"* — now also asserts zero `PUT` calls (previously asserted
  zero `PATCH` only), so a regression back toward either verb would be caught.

### What is still open

**A-FIN-07 is OPEN** — the reviewer's live re-run is the only thing that can close it, per
`C-TECH-053`: this session has no path to V3.

**The reviewer's admin-portal workaround on the 4 finance tables should be left as-is.** It already
set `IsAuditEnabled=true` live, which is exactly what a `CREATED`-then-converged run would also
produce; re-running the script now is expected to report `EXISTS` on those four (not `CREATED`) and
`EXISTS` on the original six, unless the admin-portal change did not actually persist — which the
re-run itself will reveal either way.

### What you need to decide

**Re-run `ensure-auditing.ps1` against every environment that will provision a new table with this
script from here on** — DEV now (to confirm A-FIN-07 and the reviewer's own admin-portal state
agree), and TST/ACC and PRD whenever they are first provisioned, since neither has run this script
against a table needing the flag flipped for real yet:

```
pwsh -NoProfile -File provisioning/dataverse/ensure-auditing.ps1 -Env dev
```

Expect: 10 `Table auditing '<t>'` lines, all `EXISTS` (the four finance tables converge to the
portal's manual change; the six original tables are unchanged), zero `FAILED`. If any finance table
instead reports `CREATED`, that means the portal change did not persist — worth knowing either way.

Nothing else needs a decision here: this fix is source-side only, additive to already-quoted WBS 0.4
delivery work, and does not reopen any other row in §10.

### Hours proposal — addendum for `commercial-agent` behind `APPROVE TIMESHEET`

| WBS | Proposed actual | Evidence |
|---|---|---|
| 0.4 | 0.6 h | Diagnosed 1 live defect class (generalised from `IMP-0272`/`IMP-0273`) to its Microsoft-documented root cause; corrected 1 script (`ensure-auditing.ps1`, 1 block rewritten from PATCH+partial-body to GET-full-object→PUT-whole-object); corrected 3 stale precedent claims across 2 other files; rewrote 3 Pester `It` blocks plus 1 assertion addition in `DataverseScripts.Tests.ps1`; ran the 476-test targeted suite and the 611-test full provisioning suite, both green |
| — | 0.2 h `system` | 1 improvement-log finding correcting an incoming finding's own diagnosis (`corrects: IMP-0276`), plus digest regeneration |

**0.6 h against WBS `0.4`**, additive — a follow-up fix to a defect the reviewer's own live run
surfaced in that task's deliverable, not new scope. **0.2 h as `system`**, not billable.

### Improvement log

`IMPROVEMENT LOG: 1 entry appended — IMP-0277 | digest regenerated: YES`

Records the fix to `IMP-0276` and, per `skills/how-to-log-an-improvement.md`'s `lesson` field, the
generalisable point: when a corrected write pattern is established for one metadata endpoint, check
every sibling script that PATCHes a similar endpoint before trusting its PATCH as still-working
precedent — this repository had already named the exception by name and left it unreconciled.

## Revision — orphan-guess source markers added: A-FIN-05, A-FIN-07, A-002 (WBS 0.4, IMP-0286, 2026-08-25)

### What happened

Lead-agent routed 3 of 4 build failures from
[`python3 scripts/verify-assumption-markers.py`](scripts/verify-assumption-markers.py) (build step
`assumption-markers`, [C-TECH-052](constraints/technology/technology-constraints.md#L107) HARD,
mechanised 2026-08-25 in improvement review 27, `IMP-0286`). Each named OPEN row's `Where` column
resolved to a real file that did not contain the row's own id: `A-FIN-05` →
`ensure-schema-helpers.psm1`, `A-FIN-07` → `ensure-auditing.ps1` (a second dispatch — the first,
[logged 2026-08-24 23:25](logs/routing.log#L209), did not land the marker), `A-002` →
`OptionSets/rev_conditionprofile.xml`.

### What was fixed

Added an `A-nnn`-carrying comment at the exact point of each guess, with no change to any
row's Assumption/Confidence/Status/How-to-close content — comments only, at pre-existing OPEN rows:

- [A-FIN-05](provisioning/dataverse/ensure-schema-helpers.psm1#L741) — the `IsSecured` flag on the
  inline `Lookup` deep-insert body.
- [A-FIN-07](provisioning/dataverse/ensure-auditing.ps1#L174) — the full-object `PUT` block for
  `EntityDefinitions`.
- [A-002](src/solutions/RevitaliseGrantAutomation/OptionSets/rev_conditionprofile.xml#L64) — the
  option `value="9"` label-length guess.

Re-ran `python3 scripts/verify-assumption-markers.py`: now **PASS** — 0 orphans; 24 rows total, 11
closed, 13 open (6 checked with markers now present, 7 unresolvable — the `A-TR-*` rows, which carry
no `Where` target at all and are outside this dispatch's scope). Confirmed no regression: the XML
still parses as well-formed, both PowerShell files AST-parse with 0 errors, and
`pwsh -File src/tests/Invoke-Tests.ps1 -Path provisioning` (the path CI actually uses) still reports
**611 passed, 0 failed, 1 skipped** — unchanged from before this fix.

### §10 Unvalidated Assumptions Register

No new rows; no status changes. `A-FIN-05`, `A-FIN-07` and `A-002` remain **OPEN** exactly as
before — this dispatch made each guess traceable in source, it did not close any of them. Closure
still needs the live step each row's own "How to close it" cell already names: a fresh-environment
relationship create for `A-FIN-05`, the reviewer's live re-run of `ensure-auditing.ps1` for
`A-FIN-07`, and a real `pac solution import` to DEV for `A-002`.

### What is still open

Same three rows named above, unchanged status — see their own "How to close it" cells.

**The register's 7 `A-TR-*` rows have no `Where` target at all**, so this gate cannot check them
either way. That is a pre-existing completeness gap, not a new defect, and belongs to the
trustee-portal feature this dispatch was explicitly told not to touch.

### What you need to decide

Nothing new. This is a source-marker-only fix with no behavioural change to any script or solution
component.

### Hours proposal — addendum for `commercial-agent` behind `APPROVE TIMESHEET`

| WBS | Proposed actual | Evidence |
|---|---|---|
| 0.4 | 0.2 h | Added one `A-nnn` marker comment to each of 3 files at the register's own named location; re-ran `verify-assumption-markers.py` (PASS) and the 611-test provisioning suite (unaffected) |

**0.2 h against WBS `0.4`**, additive — closing a gate-flagged register-marker gap in that task's
already-delivered schema/provisioning artefacts, not new scope.

### Improvement log

`IMPROVEMENT LOG: 0 entries appended — none | digest regenerated: YES`

Ran `generate-known-failure-modes.py` to sync the digest with `logs/improvement-log.jsonl`'s
already-pending entries (up to `IMP-0302`); this dispatch logged none of its own. The finding that
explains why `A-FIN-07`'s marker did not land on the first dispatch is already `IMP-0286`, cited by
[`scripts/verify-assumption-markers.py`'s own docstring](scripts/verify-assumption-markers.py#L34).

### CONSTRAINT CHECK

```
Domain   HARD: 6 / 6   |  violations: NONE  (unchanged — this dispatch touched no domain-scoped content)
Domain   SOFT: 0 in scope | warnings: NONE
Tech     HARD: 17 / 17 |  violations: NONE  (C-TECH-052 specifically: was VIOLATION at routing time
                                             — verify-assumption-markers.py named 3 orphans — now
                                             PASS; every other row unchanged since the last full
                                             check)
Tech     SOFT: 1 in scope | warnings: C-TECH-013 (pre-existing, unaffected)
Overall: PASS
```

```
CODE REVIEW REQUIRED — docs/development/revitalise-grant-automation-dev-summary.md (this addendum)
Respond APPROVED to trigger Build, or give feedback for revision.
```
