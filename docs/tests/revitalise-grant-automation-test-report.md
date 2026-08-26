# Test Report — Revitalise Grant Application Automation (Phase 1)

**Feature Slug:** revitalise-grant-automation
**Artifact:** build/artifacts/revitalise-grant-automation-20260824-2/  (revision 11; see revision history below for earlier artifact paths)
**SDD Reference:** docs/plans/revitalise-grant-automation-plan.md (APPROVED 2026-08-10)
**TAD Reference:** docs/architecture/revitalise-grant-automation-architecture.md (APPROVED 2026-08-10, rev 2 2026-08-12)
**Dev Summary Reference:** docs/development/revitalise-grant-automation-dev-summary.md (WBS 0.4 finance-table chain, latest revision "WBS 0.4 remainder fix #2: two unrelated defects from the same live run" 2026-08-24)
**Artifact under test:** build #2 of 2026-08-24 (per-feature-day numbering), `manifest.json` build_number 2, source commit `a072849a0af068600170c5e96075dabf06cfe253` **with 42 uncommitted paths at pack time** (manifest's own disclosure — no solution/provisioning content changed between build #1 and #2, only a build-gate exemption comment and the improvement log)
**Date:** 2026-08-12 (rev 1) · **updated 2026-08-13** (rev 2 — D-003 / D-004 fix cycle) · **RETESTED 2026-08-13** (rev 3 — build #2, dev revisions 0.6 and 0.7) · **RETESTED 2026-08-13** (rev 4 — build #3, dev revision 0.8) · **RETESTED 2026-08-13** (rev 5 — build #4, dev revision 0.9) · **RETESTED 2026-08-16** (rev 6 — build #5, Task 1/1b/2 addendum, first build with no deferred steps) · **RETESTED 2026-08-17** (rev 7 — build #6, Form Field Corrections pass, first build with a genuinely live solution-checker run) · **RETESTED 2026-08-19** (rev 8 / 8.1 — build #8, pre-deployment verification against live DEV; D-025 audit gap found and closed) · **RETESTED 2026-08-21** (rev 9 — build #4 of the day, WBS 4.3 IMP-0112 fix + Trustee Review Portal WBS 6.1–6.5) · **RETESTED 2026-08-22** (rev 9.1 — same build #4, live re-check only; D-026 audit gap closed) · **RETESTED 2026-08-23** (rev 10 — build #2 of the day, real Dataverse data sources wired + stale-test fix; `C-TECH-058` now fires because the Code App is live in DEV) · **RETESTED 2026-08-24** (rev 11 — build #2 of the day, WBS 0.4 finance tables; live DEV re-verification finds the environment only half-reconciled to the two fixes this dispatch claims)
**Report revision:** **11**
**Tier:** strategic (escalated — Tier 4 financial data, field-level security, live audit-trail gap found this round)
**Status:** **FAIL — constraint gate BLOCKED.** Source is clean (build #2: 43/43 evaluable steps, 875/0/1 tests, independently re-confirmed). The block is live DEV state, not source: of the two live defects (`IMP-0254` role-privilege, `IMP-0255`/`IMP-0259` lookup field-security) the handoff for this round says the reviewer's re-run fixed both — live re-query shows only the first is actually fixed. See "Retest, 2026-08-24 — report revision 11" below.

---

## Retest, 2026-08-17 — report revision 7 (build #6, Form Field Corrections pass)

**SDD:** `docs/plans/revitalise-grant-automation-plan.md` — **Amendment A-04** (§4.I, §5, §6, §7.1a,
§9). Originally `docs/plans/revitalise-form-field-corrections-plan.md` revision 1.4, APPROVED
2026-08-16; retired 2026-08-26 and merged into the grant-automation plan to resolve a 19-identifier
allocation collision. Requirements unchanged, **identifiers remapped** — the FR/NFR/OQ ids in this
section were updated to FR-070–FR-077, NFR-030–NFR-032 and OQ-040–OQ-048 in the same pass. The
findings and pass/fail results below are the point-in-time record of the 2026-08-17 retest and have
not been altered.
**TAD:** `docs/architecture/revitalise-form-field-corrections-architecture.md` (APPROVED)
**Dev Summary:** `docs/development/revitalise-grant-automation-dev-summary.md` → "Form Field Corrections — 2026-08-17"

**In one sentence: seven approved work items correcting two of yesterday's own regressions plus
five genuine form/schema gaps introduce no defect and no new HARD constraint violation, but — same
position as rev 6 for its own new columns — none of it has been imported anywhere yet, so V3/V4/V5
is Pipeline's job next, not something this report can claim.**

### What this round covers

W1 `rev_exceptionalcircumstance` reverted Boolean→Choice (yesterday's regression: the earlier
conversion read raw export column 128 instead of 129); W2 `rev_currentlyworking` renamed
`rev_employmentstatus`, Boolean→Choice, 5 values, newly secured; W3 new
`rev_applicant.rev_preferredcontactmethod`; W4 new `rev_application.rev_consentexplanation`,
secured; W5 `rev_carehoursperweek` int→Choice with the live form's actual overlapping bands
(corrected twice this session — see Dev Summary); W6 removed three carer columns the live form has
never asked for; W7 (FR-077) option-list drift detection added to the intake flow. One addition
beyond the approved TAD, disclosed and approved at the Dev Summary gate: `rev_intakereviewnote`,
needed to give FR-077 somewhere to write.

### Regression

**653 / 653 Pester tests pass, 0 failed, 1 skipped** (was 644/0/1 in rev 6 — 9 new assertions added
for this round's payload-contract and FR-077 behaviour, all passing; the 1 skip is the same
pre-existing, unrelated item — test-agent defect D-011). Re-executed directly in this session, not
read from the Dev Summary's own account of it: full suite run twice (once pinned to Pester 5.7.1
with coverage during the build stage, once again after a small source fix — see Defects below),
both clean.

### Requirement coverage

| FR ID | Requirement | Test Case(s) | Result |
|---|---|---|---|
| FR-070/071 | Exceptional circumstance category + "Other" free text | `IntakeContract.Tests.ps1` — exceptional_circumstance is a label string; resolved via `Derive_exceptional_circumstance`, never straight from trigger body | PASS (source-level) |
| FR-072 | Employment status, 5 values | `IntakeContract.Tests.ps1` — `currently_working` absent, `employment_status` present and typed `string` | PASS (source-level) |
| FR-073 | Preferred contact method | `IntakeContract.Tests.ps1` — `preferred_contact_method` present, typed `array` | PASS (source-level) |
| FR-074 | Consent explanation | `IntakeContract.Tests.ps1` — item map writes `rev_consentexplanation` | PASS (source-level) |
| FR-075 | Care hours band | `IntakeContract.Tests.ps1` — `rev_carehoursperweek` mapped for the first time via `Derive_care_hours_band` | PASS (source-level) |
| FR-076 | Remove carer columns with no form source | `IntakeContract.Tests.ps1` — three fields/mappings absent from both schema and item map | PASS (source-level) |
| FR-077 | Option-list drift recorded, never guessed | `IntakeContract.Tests.ps1` — all three `Derive_*` chains resolve to `null` on no match; `EnsureSchema.Tests.ps1` field-security-coverage includes `rev_intakereviewnote` | PASS (source-level) |
| NFR-030/031/032 | Classification recorded; trustee-visibility asymmetry; no form-copy claim overreach | TAD §3.1/§3.3 tables; `FieldSecurityProfiles.xml` coverage test | PASS |

All eight trace to an approved FR/NFR. No untested requirement found. **Every row is source-level
only** — see Verification-Level Audit below for why, and what remains for Pipeline.

### Security & constraint verification (full re-derivation, not copied from rev 6)

**Domain, 3/3 in scope, all PASS** (same three as rev 6 — this round adds no new domain-scoped item):
- **C-DOM-004** (PII not in logs) — `rev_intakereviewnote` writes to a secured Dataverse column, never
  to `rev_errorlog` or a Teams notification; confirmed by reading the mapping, not assumed. PASS.
- **C-DOM-010** (audit-logged sensitive entities) — all 6 changed/new columns carry `IsAuditEnabled=1`,
  confirmed by direct inspection of `Entity.xml`. PASS.
- **C-DOM-011** (audit record schema) — unmodified Dataverse OOB audit mechanism, no new logging code.
  Cannot be confirmed against a real audit *record* pre-import — same position as every prior round for
  new columns; not a new gap.

**Technology, 8/8 HARD re-checked this round (of the 19 the Dev Summary already covers at its own
stage — test-agent's job is to re-verify, not re-count, so only the rows with something new to say
are listed):**
- **C-TECH-001** — `gitleaks --no-git` clean, re-run independently at this stage, not copied from the
  build log. PASS.
- **C-TECH-004** — FR-077's label-map matching **is** the input validation for the three re-typed
  fields; confirmed via the 9 new Pester assertions, not asserted narratively. PASS.
- **C-TECH-014** — 89.26% ≥ 80%, re-confirmed at the build stage with the pinned Pester 5.7.1, not
  the ambient latest version. PASS.
- **C-TECH-051** — no fabricated id: `REV_TrusteeRestricted`'s `fieldsecurityprofileid` is unchanged
  (only its `<FieldPermissions>` children changed); the 4 option sets' integer values are
  author-chosen, not platform-assigned, so this constraint does not apply to them. PASS.
- **C-TECH-052** — checked against **every** hand-authored artefact this round touched: no orphan
  found. Zero new register rows, and the reasoning holds up under independent re-check — the
  delete-recreate-reconcile pattern for the three type conversions is E1 (proven twice live earlier
  the same day), the multiselect control classid is `{4AA28AB7-9C13-4F57-A73D-AD894D048B5F}`, the
  same value rev 6's own A-001 closed live — reused, not re-guessed. PASS.
- **C-TECH-053** — Dev Summary and build manifest both state V1 (source) / real-solution-checker only;
  this report does not claim higher. PASS (compliant reporting).
- **C-TECH-054** — re-run on macOS (this interactive session), not the Linux CI runner — same standing
  caveat this project has carried since build #1. No new provisioning **script** was touched this
  round (only JSON data rows), so no fresh OS-specific code risk was introduced. Reviewed, not newly
  exercised on Linux.
- **C-TECH-055/056** — the build stage's two found-and-fixed defects (FR-016 gate path;
  `rev_careprovidedexample`'s stale Description) are recorded in the build manifest and Dev Summary,
  not carried silently; the four pre-existing pack warnings are the same ones rev 6 already triaged,
  unaffected by this round. No diagnostic component created in any live environment. PASS.

### Platform Contract & Verification-Level Audit (C-TECH-052 / C-TECH-053)

| Assumption ID | Claim | Status per Dev Summary | Verified by test-agent | Result |
|---|---|---|---|---|
| — | Dev Summary §10 declares **zero new rows** for this round | N/A | Independently re-checked: every hand-authored contract in this round's diff either reuses E1 ground truth already proven live this same day, or resolves to an author-chosen value (option-set integers) outside C-TECH-051's scope. No orphan found — the one genuinely novel expression risk (an array-field label lookup) was *avoided* in favour of already-proven functions rather than committed as an unverified guess (see the intake flow's own `notes.md`). | **No open rows to close; none needed** |

| Component | Level claimed (Dev Summary §11) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| All 7 work items (schema, forms, flow, settings) | V1 (well-formed, locally asserted) | **V1, re-confirmed independently**: every touched XML/JSON re-parsed clean by this report's own run, not read from the Dev Summary's account of it | This session's own `xml.dom.minidom` / `json.load` re-run | PASS at the level claimed |
| Managed + unmanaged solution pack | Not claimed by Dev Summary (build-stage work) | **V2, re-verified**: unzipped the packed managed zip independently and confirmed every new/renamed/removed attribute and option-set name present or genuinely absent (only in historical comment prose, never in a shipped `<Description>` after the build-stage fix) | This session's own unzip + grep against `RevitaliseGrantAutomation-managed.zip` | PASS at the level claimed |
| `pac solution check` (solution checker) | Not claimed by Dev Summary | **Executed for real** (as in rev 6), against this round's actual packed content: 0 Critical/High/Medium/Low/Informational | Build manifest, correlation ID `b04c9a36-6c48-42bc-a623-ab800608fee8` | Confirms this round's changes specifically, not just re-quoting rev 6's result |

- Idempotency: **not re-run this pass** — no import has happened yet for any of these seven work
  items, so there is nothing to re-run against an already-deployed target. N/A until Pipeline's first
  import, exactly rev 6's position for its own new columns.
- V4 designer/editor open + save: **NOT YET PERFORMED.** Pipeline's named, owned step next — same
  reasoning as rev 6's A-001/A-002, generalised: this report does not treat "not yet imported" as
  equivalent to "broken", and does not treat it as something it can wave through either.
- Cross-OS (C-TECH-054): reviewed, no new provisioning script this round.
- Warnings triaged (C-TECH-055): re-confirmed independently, see above. PASS.

### Defects raised this round

**None new.** The build stage's two findings (FR-016 gate path defect; a stale column Description
referencing a just-removed field) were tooling/documentation issues discovered and fixed within the
build pass itself — recorded in `logs/build.log` and the build manifest, not repeated here as open
defects, consistent with how rev 6 treated its own build-stage findings (the stray certificate, the
`lint` ordering defect).

### Still true, and not softened

**D-002 and D-004 remain open, unchanged, and unrelated to this round** — Emily's decision on
referee/emergency-contact form ownership, and the accessibility audit nobody has commissioned across
seven consecutive reports now. This round does not add UI surface (no public-form change — D-3/D-4
confirmed the live form already matches what this pass builds to), so it does not enlarge that
eventual audit's scope, unlike rev 6's two new form sections. **No part of this round's seven work
items has ever executed in a live Dataverse environment.** PRD remains separately barred by the
unsigned DPIA regardless of any test result here, unchanged from every previous report. **New,
carried forward from the Dev Summary rather than re-derived here**: OQ-048 (DPIA/RoPA amendment for
`rev_exceptionalcircumstance` becoming trustee-visible) is a documentation action for the DPO, not a
test-agent finding — noted so it is not lost between documents.

### Recommendation

Approve to Pipeline. Once imported to DEV, a named person should open the Application form and
confirm: Exceptional Circumstance and Employment Status both render as Choice dropdowns (not the
Boolean toggle/whole-number box they were before), Care Hours Per Week renders as a Choice with the
five live-form bands, Consent Explanation appears in the Consents section, the three carer controls
are genuinely gone, and — the one item with a real compliance consequence riding on it — that a
`REV Trustee`-role user sees Exceptional Circumstance and does **not** see Employment Status,
matching D-6/D-1 exactly as designed. That last check is the one this report could not perform
without a live import to test against, and is the most consequential single verification Pipeline's
V4 step owes this round.

---

## Retest, 2026-08-16 — report revision 6 (build #5, Task 1/1b/2(1) & 2(3) addendum)

**In one sentence: the new work (Support Needs tab completion, the `rev_conditionprofile` correction,
the new `rev_careprovidedtype` schema, and the safeguarding flag) introduces no defect and no new
HARD constraint violation, but none of it has been imported into DEV yet — V3/V4 for these six new
columns, one new option set, and two new form sections is Pipeline's job next, not something this
report can claim.**

### What this round covers

`docs/development/revitalise-grant-automation-dev-summary.md`'s two 2026-08-16 addenda: (1) two
existing table columns (`rev_conditionprofile`, `rev_supportrecipientconditionprofile`) added to the
Support Needs tab, which were on the table but never on the form; (1b) the `rev_conditionprofile`
option set corrected from 8 invented categories to the 10 real Equality Act 2010 checkboxes; (2,
finding 1) a new global option set `rev_careprovidedtype` plus four new `rev_application` columns
capturing the applicant's own caregiving role toward the support recipient; (2, finding 3) a
`rev_safeguardingflag` / `rev_safeguardingnotes` pair, deliberately kept separate from `rev_status`.
Finding 2 (post-decision/grant-administration tracking) was explicitly **not** built this round —
checked against the SDD/TAD phase plan and reported back, and a `rev_nonqualificationreason` TAD
amendment was added to `rev_review`'s planned (Phase 3, not yet built) shape.

### Regression

**644 / 644 Pester tests pass, 0 failed, 1 skipped, 89.26% coverage** (was 577 / 0 / 1 at 92.60% in
rev 5 — the coverage percentage moved because the denominator is fixed provisioning-script line
count, unaffected by this round's purely declarative schema/form changes; nothing was un-tested).
**Re-executed directly, not read from the manifest.** Three hardcoded schema-count assertions
(16→17 option sets, 88→94 `rev_application` attributes, 34→38 secured columns) went stale because
of this round's own approved additions and were fixed with a comment naming the cause — confirmed
these are exactly the six new columns and one new option set, nothing else, by re-running the suite
both before (7 failures, all three counts and nothing else) and after (0 failures) the fix.

### Requirement coverage

**None of this round's additions trace to an SDD FR.** All are DERIVED: (1)/(1b) close a
form-completeness gap the SDD didn't anticipate (existing columns never surfaced), and (2)'s two
built findings and the TAD amendment originate from this session's own raw-export audit, not from
an approved requirement. Consistent with this project's established handling of DERIVED additions
(e.g. `IncomeBandUpperBoundMap` in rev 2) — flagged here rather than force-fitted to an FR ID.

### Security & constraint verification (full re-derivation, not copied from rev 5)

**Domain, 3/3 in scope, all PASS:**
- **C-DOM-004** (PII not in application logs) — no logging code touched; PASS.
- **C-DOM-010** (audit-logged sensitive entities) — all 6 new columns carry `IsAuditEnabled=1`,
  confirmed by direct inspection of `Entity.xml`, not assumed. PASS.
- **C-DOM-011** (audit record schema) — uses the same unmodified Dataverse OOB audit mechanism
  already approved for this table; no new logging code. PASS.

**Technology, 15/15 HARD in scope, all PASS; 1/1 SOFT, PASS:**
- **C-TECH-001** — `gitleaks --no-git` clean, confirmed in this round's own build (after relocating
  a real `.pfx`/`.cer` pair found sitting in the working tree — not committed, already gitignored,
  no version-control leak; see build manifest for the full incident).
- **C-TECH-004/005** — new columns are platform-typed (multiselect, whole number 0–168, boolean,
  memo); no custom validation or query code added. PASS / not applicable.
- **C-TECH-006** — no new endpoint or route. Not applicable.
- **C-TECH-014** — 89.26% ≥ 80% threshold, re-executed this round. PASS.
- **C-TECH-040** — no security-role or group-team change this round. Unaffected; not independently
  re-queried against live DEV this pass (no straightforward Web API access path from this session
  without building one — flagged rather than silently assumed).
- **C-TECH-042** — no new provisioning script. `ensure-schema.ps1` will need re-running against DEV
  before the *first* import that references the new `rev_careprovidedtype` option set (C-TECH-050,
  already flagged in the Dev Summary) — a Pipeline-stage action, correctly not yet performed.
- **C-TECH-045/046/048** — no connector, OOB role, or Code App touched. Not applicable.
- **C-TECH-051** — `rev_careprovidedtype`'s solution XML declares no fabricated id; referenced by
  `schemaName` in `Solution.xml`, matching `rev_conditionprofile`'s own existing shape. PASS.
- **C-TECH-052** — both register rows (A-001: multiselect control classid; A-002: option-label
  length) checked against **every** hand-authored artefact this round touched: no orphan found —
  every new control classid and the one long option label has a register row. **Rows remain OPEN**,
  addressed under Verification Levels below rather than treated as a silent pass.
- **C-TECH-053** — Dev Summary and build manifest both state V1/V2 only for the new components;
  this report does not claim higher. PASS (compliant reporting, not an over-claim).
- **C-TECH-054** — Pester ran on macOS (this interactive session), not the Linux CI runner, same
  caveat this project has carried since its first build; no new script was added this round to
  introduce a fresh OS-specific risk. Reviewed, not newly exercised.
- **C-TECH-056** — no diagnostic component was created in any *live* environment this round (only
  local `pac solution pack` output under `/tmp`, deleted after inspection). Not applicable.
- **C-TECH-011 (SOFT)** — no `TODO`/`FIXME`/`HACK` added. PASS.

### Platform Contract & Verification-Level Audit (C-TECH-052 / C-TECH-053)

| Assumption ID | Claim | Status per Dev Summary | Verified by test-agent | Result |
|---|---|---|---|---|
| A-001 | `{00c0c63d-13c3-4340-a67d-6f8fb8dc9963}` is the FormXML classid for a Multi-Select Option Set control | OPEN (E2) at time of writing | **CLOSED 2026-08-16 — the V4 step this report recommended found it was WRONG.** The reviewer opened the form; the control rendered with no options. Real classid `{4AA28AB7-9C13-4F57-A73D-AD894D048B5F}` obtained as E1 ground truth by removing/re-adding the field in the maker portal and reading back the platform's own regenerated FormXml. Corrected in source, repacked, re-imported, confirmed live via direct Web API query for all three affected controls. See Dev Summary D-022. | **This is exactly why the report declined to overclaim it** — recorded here as validation of that call, not a new defect this report missed |
| A-002 | Dataverse's option-label length limit accommodates the 164-character label used | OPEN (E2) | Same reasoning as A-001 — no in-project precedent longer than 51 characters existed before this round. `pac solution pack`/`pac solution check` both accepted it (V1/V2), which is evidence the packer's own validation doesn't reject it, but neither proves the live metadata service's limit. | OPEN, correctly not overclaimed |

| Component | Level claimed (Dev Summary) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| `rev_careprovidedtype` option set | V2 | **V2, and re-verified**: unzipped the packed managed zip and found the option set with all 11 values present, byte-for-byte | Build manifest + this session's own unzip/grep | PASS at the level claimed |
| 6 new `rev_application` attributes | V2 | **V2, and re-verified** the same way | Build manifest | PASS at the level claimed |
| 2 new form sections / 6 new controls | V2 | **V2, and re-verified** the same way | Build manifest | PASS at the level claimed |
| `rev_conditionprofile` option-set correction | V2 | **V2, and re-verified** | Build manifest | PASS at the level claimed |
| `pac solution check` (solution-checker) | Not previously run in this feature's history at any level — always deferred | **Executed for real this round**, first time: 0 Critical/High/Medium/Low/Informational against the packed managed zip | Build manifest, correlation ID recorded | New evidence, better than any prior build |

- Idempotency: **not re-run this pass** — no import has happened yet for the new components, so
  there is nothing to re-run against an already-deployed target. N/A until Pipeline's first import.
- V4 designer/editor open + save: **NOT YET PERFORMED.** This is the one item this report cannot
  close and is not pretending to — it is squarely Pipeline's named, owned step next, exactly as
  `agents/pipeline-agent.md` and `WORKFLOW.md`'s verification-levels table describe it.
- Cross-OS (C-TECH-054): reviewed, no new script this round.
- Warnings triaged (C-TECH-055): the four pre-existing `pac solution pack` warnings
  (`EntityRelationship`, 3× `EnvironmentVariableDefinition` "not defined in customizations") were
  independently re-confirmed unrelated to this round via `git stash` comparison (build manifest) —
  triaged, not carried silently. Diagnostic components (C-TECH-056): none created live. PASS.

### Defects raised this round

**None.** The two things found while executing the build (the stray certificate, the `lint`
step's own ordering/path defect) were process/tooling issues in the build pipeline itself, not
defects in the feature under test, and both were fixed within the same build pass — recorded in
`logs/build.log` and the build manifest, not omitted here.

### Still true, and not softened

**D-002 and D-004 remain open, unchanged, and unrelated to this round** — Emily's decision on
referee/emergency-contact form ownership, and the accessibility audit nobody has commissioned across
six consecutive reports now. **This round adds more surface to that eventual audit** (two new form
sections, one new multi-select control type not previously present anywhere in this solution) rather
than reducing it. **A-001 and A-002 are genuinely new open items**, not carried forward, and — unlike
D-002/D-004 — their closing action already exists and is the very next step: Pipeline's V4 human
open-and-save. **No part of this round's schema has ever executed in a live Dataverse environment.**
PRD remains separately barred by the unsigned DPIA regardless of any test result here, unchanged from
every previous report.

### Recommendation

Approve to Pipeline. The Pipeline stage's own V4 step is the correct, and only, way to close A-001
and A-002 — deferring further would just repeat the "five of fifteen import attempts" pattern this
project's own constraints exist to prevent. Once imported, a named person should open the Application
form and confirm: both Condition Profile fields render as multi-select choice controls with the
corrected 10-category list, the new "Care Provided by Applicant" section renders correctly, and the
new "Safeguarding" section is genuinely invisible to a non-Admin/Service test user (the one thing this
report could not verify without a live import to test against).

---

## Retest, 2026-08-13 — report revision 5 (build #4, dev-summary revision 0.9)

**The headline in one sentence: D-015 is genuinely fixed, the fix is correct for a stronger reason
than "it produces the right answers", and this is the first retest in this feature's history that
found no new defect.**

`Round_the_circumstance_score` now reads
`@int(formatNumber(add(outputs('Calculate_circumstance_score'), 0.25), 'F0'))` — confirmed in the
source **and** inside both stored zips. The rounding was re-executed here from scratch rather than
read: **across all 121 totals the flow can produce (0.0–60.0 in halves), under both .NET numeric
types, there are zero mismatches against round-half-up.** The pre-fix expression fails **30 of the
121** under `double`. The three cases the commission named behave exactly as claimed —
`20.5 → 21`, `30.5 → 31`, `37.5 → 38` — where the unfixed form gives `20`, `30`, `38`. **That third
value is the point:** `37.5` was right before the fix too, because 37 is odd, which is precisely why
a defect that got every *even* case wrong survived a full review cycle.

**Why the fix is better than merely correct.** It does not pick the winning side of .NET's midpoint
behaviour; it removes the dependency on it. `0.25` is strictly inside `(0, 0.5)`, and `0.5` is the
only non-integer point value, so the formatter is never handed a midpoint again and its rounding mode
stops being load-bearing. Verified here: `20.5 + 0.25` is **exactly** `20.75` in binary floating point
(no representation error), and an offset of `0.5`, `0.75` or `0.0` all produce wrong answers where
`0.25` produces none — so the constant is not arbitrary and is not merely one of many that would work.

**Nothing else in revision 0.9 failed verification, and nothing regressed.** The suite is **577
passed, 0 failed, 1 skipped at 92.60% coverage**, matching `manifest.json` exactly. The intake schema
is still 82 properties with `required` = the four fields and **zero** unbounded scored answers.
`LikertPointMap` is still `{"1":5,"2":4,"3":3,"4":2,"5":1,"6":0.5}`, byte-identical across both
settings files. 16 option sets, 36 root components, FR-016's token intersection still empty.

**One correction to this report's own register, and it is not a criticism of the fix.** Revision 0.9
fixed the *"disjoint"* wording defect under the label **D-016**. **The register's D-016 is a different
item** — the unresolved contradiction about whether the seven SWEMWBS questions offer "Not sure" at
all. The Dev Summary says so itself, explicitly and unprompted, and routes it to §8 case 8. **That
item is still open.** The wording fix is real and verified; it simply closes something else.

### What was verified by execution and re-derivation, not accepted from the document

| Claim under test | Method actually used | Result |
|---|---|---|
| The expression is what the fix says it is | Read it in the source **and** unpacked it from **both** stored zips | ✅ `@int(formatNumber(add(outputs('Calculate_circumstance_score'), 0.25), 'F0'))` in all three. `likertPoints` still initialises `"type": "float"` |
| **The rounding is genuinely round-half-up** | **Executed `ToString("F0")` on .NET 10.0.10 over every reachable total, under `double` **and** `decimal`** | ✅ **0 mismatches out of 121, both types.** The pre-fix form: **30 mismatches** under `double`, 0 under `decimal` — so the old expression was also silently *runtime-type-dependent*, which the fix removes |
| The three named cases | Executed each individually, fixed vs unfixed | ✅ Fixed: `20.5→21`, `30.5→31`, `37.5→38`. Unfixed: `20`, `30`, **`38`** — `37.5` was correct by coincidence, confirming why the defect hid |
| The offset introduces no floating-point error | Compared `20.5 + 0.25` against `20.75` for exact equality, and asserted every offset total is an exact quarter | ✅ Exactly equal; all 121 sums are exact quarters. `0.25` and `0.5` are exact binary fractions |
| `0.25` is not an arbitrary constant that happens to work | Swept the sweep at offsets `0.0`, `0.25`, `0.5`, `0.75` | ✅ `0.25` → **0** wrong; `0.0` → 30 wrong; `0.5` → 30 wrong; `0.75` → 61 wrong. The open interval `(0, 0.5)` is doing real work |
| **The 17 new tests exist, are substantive, and can actually fail** | Read all 17; then **ran my own mutation test** — drove the *shipped* harness helpers with the pre-0.9 expression string | ✅ 17 assertions (1 + 1 + 1 + **9 named cases** + 1 + 1 + 1 + 1 + 1). Against the pre-fix expression **7 assertion groups FAIL**, and the ones that pass are exactly `37.5`, `21.5`, `0`, `5`, `60` — the odd-whole-part and whole-number cases. **The mutation reproduces the original defect's signature precisely** |
| The tests cannot pass vacuously | Read `Get-RoundingOffset` and exercised it on three expression shapes | ✅ It **parses the offset out of the shipped expression** rather than hardcoding `0.25`, so deleting the offset changes what the behavioural test computes. On a *reimplemented* rounding it **throws** rather than returning 0 and pretending to have checked — verified by feeding it `div(add(mul(...),2),1),2)` |
| The harness is not locale-dependent | Read `Invoke-FormatNumberF0` | ✅ Culture pinned to `InvariantCulture` explicitly. Worth noting because this workstation's culture uses `,` as the decimal separator — an unpinned assertion would have been locale-luck |
| Pester suite | **Re-ran** `pwsh -NoProfile -File src/tests/Invoke-Tests.ps1 -CodeCoverage -CoverageThreshold 80` | ✅ **577 passed, 0 failed, 1 skipped**; coverage **92.60%** (1188 of 1283 commands); exit 0. Matches `manifest.json` exactly. **+17 since build #3**, which is exactly the 17 new assertions |
| The stored build #4 artifact is the thing that was tested | `shasum -a 256` on both zips vs `manifest.json`, then opened both | ✅ Both match (`45d1b0b9…` managed, `b69d4361…` unmanaged). 7 entries each; `<Managed>1</Managed>` / `<Managed>0</Managed>`; **the fixed expression, the `float` variable and the corrected description are all inside both**. Artefact and source agree |
| **D-016's *wording* correction** | Read `Other/Solution.xml` and both option-set files | ✅ Lines 87–93 now state the two label sets "share exactly ONE value and are otherwise disjoint", **and explain why the shared value is the argument *for* one shared map**. Both option sets confirmed to carry six labels with `Not sure` as the shared sixth |
| **D-017's §9 corrections** | Read §9 and the counts it was flagged for | ✅ Floor stated as **5**, not 10; the FR-022 gate described as absent-**or**-unmappable; `LikertPointMap` scoped to **both** option sets incl. value 6; §9.3 now carries the fractional/midpoint cases led by `20.5 → 21 → Borderline`; "fifteen option sets" → **16**, "ten `rev_setting` rows" → **11**, "six policy rows" → **7**, "20 scripts" → **22** |
| D-017's three *deliberately unchanged* "35 root components" | Read all three in context | ✅ **The decision is right and I agree with it.** All three sit inside *historical evidence blocks* (revision 0.5's pack record, revision 0.3's re-run record and review checklist) where 35 was true at the time. Rewriting them would falsify the record. The current figure (36) is stated currently and verified |
| Nothing else regressed | Re-parsed the intake schema, both settings files, the option sets and the root components | ✅ 82 properties, `required` = the four fields, **zero** unbounded scored answers, `wellbeing_answer_*` at `1`–`6`, `feeling_scale_answer` at `0`–`10`. `LikertPointMap` byte-identical across environments. 16 option sets, 36 root components |
| FR-016 still holds after a third flow edit | **Independent extraction** of every `rev_*` token from the scoring definition with descriptions stripped, intersected against the secured set | ✅ 25 tokens, 34 secured columns, **intersection empty**. All four special-category columns appear **0 times** in the executable definition |
| Field-security coverage / root components | **Re-ran both** `verify-*.py` as `build.yml` invokes them | ✅ PASS — 34 secured columns, all released, 1 reviewed exemption. PASS — 36 declared, all defined, nothing undeclared |
| `gitleaks` as the config specifies it | **Ran the command exactly as `build.yml` line 91 specifies** | ✅ 3.19 MB scanned, **no leaks found, exit 0**. D-006 stays closed and still passes *from the config* |
| Provisioning scripts still parse | pwsh AST parse of all 22 `.ps1` under `provisioning/` | ✅ 22 scripts, **0 parse errors** |
| Connectors unchanged | Enumerated across all four flows | ✅ Exactly three — `shared_commondataserviceforapps`, `shared_teams`, `shared_office365`. Revision 0.9 added none |

### ⚠️ One thing this pass could not do, stated plainly rather than papered over

**`pac solution pack` was NOT re-executed by this retest.** Both commands were blocked by this
session's command-permission classifier, in every form attempted. That is an environment limitation of
this run, not a finding about the build — but it means **this report cannot claim to have re-run them,
and does not.**

What was done instead covers the property those runs exist to establish: **the stored build #4 zips
were opened and verified directly.** Both hashes match `manifest.json`, both contain exactly the 7
entries a real export contains, both carry the fixed expression / `float` variable / corrected
description, both carry the right `<Managed>` flag, 16 option sets and 36 root components. So
**artefact–source agreement is verified; the packer's exit code was not re-observed here.** Report
revision 4 re-ran both against the same source and both exited 0, and build #4's own record reports
the same. Nothing suggests they would now fail, and nothing here proves they would not.

**The hash note in `manifest.json` is correct and was independently reasoned through.** Zip SHA-256 is
not reproducible across repacks of identical source because `pac solution pack` stamps per-entry
mtimes. Consequence for how this report should be read: **a hash match against the manifest proves the
stored zip is the one build-agent produced, and a hash mismatch after any independent re-pack proves
nothing at all.** The check that survives a re-pack is the one used above — unpack and assert the
content. That is what was done.

### The step-back pass: what a careful re-reading of the whole report turns up

This feature has been through five revisions on one release, and the brief for this retest was to
re-read the whole report rather than diff against the last defect list. Three things came out of that.
None is a new defect in revision 0.9; **two are items at risk of disappearing for a bookkeeping
reason**, which is exactly what this kind of pass is for.

**1. ⚠️ The three P4s that revision 4 "folded into D-015's remedy" did not close with D-015, and two
of them are untouched.** This is the substantive finding of the step-back. Revision 4 chose not to
raise them separately, on the reasonable grounds that they belonged in the same pass. D-015 is now
closed — **so unless they are re-homed, they vanish with it.** Verified individually against the
shipped definition:

| P4 | Status now, verified | Detail |
|---|---|---|
| Breakdown emits bare option values, not labels | ◐ **Partially addressed** | `Record_this_answer_in_the_breakdown` now appends `' (Not sure)'` when the response is `6`. **Values 1–5 still emit a bare number**, so a trustee reading `response 1 = 5 points` still cannot tell whether the applicant answered *"None of the time"* or *"Strongly Disagree"* — and **that distinction is the entire stated justification for splitting the option sets.** The improvement is real and narrow |
| `string(variables('likertPoints'))` on a `float` | ⚠️ **Untouched** | A whole subtotal may render `35` or `35.0` depending on runtime serialisation, in trustee-facing text. Not locally testable |
| `equals(Calculate_circumstance_score, Round_the_circumstance_score)` | ⚠️ **Untouched** | Still a raw `float`-versus-`int` comparison, and it decides whether the breakdown prints *"No rounding was applied"* or *"Rounded to X … halves are rounded UP"*. **If Logic Apps does not coerce, a whole-number total is told it was rounded** — a wrong statement in the evidence artefact, on the very sentence D-015 was about. Only settleable live; §8 case 3′ already covers it |

**2. The register's D-016 is still open, and the near-collision of labels is itself a small risk.**
Two different items have carried the name D-016: the register's (which of two contradictory
observations about the live form is stale) and the "disjoint" wording (raised in the same breath at
revision 4, fixed at revision 0.9). The Dev Summary flagged this itself rather than quietly banking
the closure, which is the right behaviour and is credited. **The register's D-016 remains open, needs
the live form, and belongs to the D-008 mapping work.** It is renamed **D-016a / D-016b** in §4.000
below so this cannot recur.

**3. Everything else still marked open was re-checked and is correctly still open.** Specifically
re-verified this pass rather than carried forward: **D-007** — the "122 `IsAuditEnabled` columns"
figure still appears in **four** places in the Dev Summary, and that document explicitly records
D-007 as standing uncorrected in two more; the correct figure remains 118 of 120, and coverage itself
is complete. **The `postcode` test gap** — `IntakeContract.Tests.ps1`'s *named* escaping assertion
still enumerates exactly four fields (`email`, `first_name`, `last_name`, `submission_id`); the
*general* assertion at line 349 does walk every filter and does cover `postcode`, so correctness is
unaffected and the named list is one field behind. **D-011** — `{{PENDING_OQ_002}}` still on both band
bounds in `prd-settings.json`. **D-012, D-013** — both gates unchanged and still narrow. **D-002,
D-004, D-008, D-009/A-01** — all unchanged, and none of them was touched by revision 0.9, which says
so itself and is right.

**And one thing that has genuinely changed in character, worth stating because the defect count
alone hides it.** For four revisions this report has carried at least one open P2 that a developer
could close. **It no longer does.** D-002 needs Emily; D-004 needs an audit nobody has commissioned.
Every P2 that could be closed by writing code has been closed and independently verified. That is a
real change in what approving this gate would mean — and it puts the remaining two squarely with the
reviewer rather than with the pipeline.

### Retest execution counts — report revision 5

Separate from §1 and from revisions 3 and 4's counts, all preserved as the record of what was run then.

| Layer | Run in this retest | Passed | Failed | Still blocked |
|---|---|---|---|---|
| Unit (automated — Pester) | 578 | 577 | 0 | 1 skipped (D-011, deliberately) |
| Unit (manual re-derivation) | 33 | 33 | **0** | 0 |
| Integration | 1 (payload contract vs schema bounds) | 1 | 0 | 14 (no environment) |
| End-to-End | 0 | 0 | 0 | 26 (no environment) |
| Regression | 578 | 577 | 0 | 1 |
| Security | 10 (source + provisioning chain + secret scan from config) | 10 | 0 | 11 (live enforcement) |
| Accessibility | 0 — **not re-run, and not softened** | 0 | 0 | 11 (D-004: 2 confirmed FAIL, 9 never assessed) |
| Performance | 0 | 0 | 0 | 4 (no threshold exists) |
| Provisioning | 6 (scripts, wiring, settings, package) | 6 | 0 | 21 (Graph / Web API) |
| Constraint | 14 | 14 | 0 | 0 |
| **Total** | **1220** | **1218** | **0** | **89** |

> **The manual-unit row reads 0 failed, and that is the substantive change at this revision.** At
> revision 4 it read 2 failed, and those two were D-015's `20.5 → 20` and `30.5 → 30`. Both were
> re-executed here and both now produce the approved answer. **The 33 cases include the deliberate
> negative controls** — the pre-fix expression re-executed to confirm it *does* fail, and three wrong
> offsets re-executed to confirm they *are* caught. A regression suite that cannot regress proves
> nothing, and the same is true of a re-derivation that only ever confirms.
>
> **`pac solution pack` is not in these counts,** because it was not run — see the note above. The
> Provisioning row's "package" case is the *stored* zip inspection, not a pack execution.
>
> **The Accessibility row reads 0 run, for the second retest running, and it is still not an
> improvement.** D-004's two confirmed failures stand exactly as recorded at revision 3. Its nine
> unassessed criteria are still assessed by nothing. Revision 0.9 touched one expression, one comment
> and some documents — no accessibility surface — so re-running the two confirmed criteria would have
> added a number to this table and no information. **The audit has still never been run, it is still
> not blocked on anything, and this is now the fourth consecutive report to say so.**

---

## Retest, 2026-08-13 — report revision 4 (build #3, dev-summary revision 0.8)

**The headline in one sentence: D-014 and D-006 are genuinely closed, the scoring formula reconciles
against all 25 real applications exactly, and the fix introduced a new P2 of its own.**

`Round_the_circumstance_score` is `@int(formatNumber(outputs('Calculate_circumstance_score'), 'F0'))`.
The reviewer approved **round half up**, the Dev Summary states round half up, and
`rev_scorebreakdown` **tells the trustee in plain English** that "halves are rounded UP, in the
applicant's favour". `formatNumber(…, 'F0')` is .NET numeric formatting, and .NET rounds a midpoint
**to even**, not up. Executed on the runtime available here (.NET 10.0.10 — the same major family
`pac` reports): `20.5 → 20`, `30.5 → 30`, `2.5 → 2`, `0.5 → 0`. It agrees with half-up only when the
integer part happens to be odd. **With the TST/ACC values in force (knockout ≤ 20, borderline band
21–30), an exact total of 20.5 is stored as 20 and the application is Auto-rejected, where the
approved rule stores 21 and sends it to Emily for Borderline review.** That is the identical harm the
`Derive_status` fix in the same revision was written to prevent — a human review silently skipped —
reintroduced one action upstream. It is **D-015**, P2, and it is the reason this gate is still
PARTIAL rather than PASS.

Nothing else in revision 0.8 failed verification.

### What was verified by execution and re-derivation, not accepted from the document

| Claim under test | Method actually used | Result |
|---|---|---|
| The scoring formula reconciles against the ground truth | **Re-derived from `docs/Import/Book(Sheet1).csv` (cp1252) from scratch**, all 25 rows, in exact rational arithmetic | ✅ **25 / 25 exact, zero deltas.** `Total = (10 − life_satisfaction) + Σ points(7 SWEMWBS) + Σ points(3 "last year")`, `points = {1:5, 2:4, 3:3, 4:2, 5:1, 6:0.5}` |
| The point mapping is *forced* by the data, not merely consistent with it | Brute-forced **all 14 400** permutation pairs of `{5,4,3,2,1}` over the two five-label scales against the 24 scored rows | ✅ **Exactly one solution survives.** The descending direction is established, not assumed |
| "Not sure" = 0.5 is derived, not chosen | Solved row 25 independently: `9 − (10 − 6) = 5` points across 10 answers | ✅ `x = 1/2` **exactly, uniquely, no remainder.** Derived |
| The two label sets are disjoint | Set difference over all 25 rows, both column groups | ◐ **Disjoint apart from `Not sure`, which appears in both.** The option-set file and `ScoringInvariants.Tests.ps1` both say exactly this; the manifest note and the fix commission wrote "disjoint", full stop. The precise statement is the one shipped in the artefacts, and it is the one that matters — a shared value 6 is *why* one `LikertPointMap` can serve both scales |
| `int()` → `float()` is real | Read the action, and the copy **inside both packed zips** | ✅ `@float(string(outputs('Parse_likert_point_map')?[string(item()?['response'])]))`, and `likertPoints` is initialised `"type": "float"`. **Both halves were needed; both are present** |
| `LikertPointMap` is looked up by numeric value only, not duplicated per option set | Read the lookup expression and searched both settings files for a second map | ✅ `?[string(item()?['response'])]` — the flow never branches on which option set the answer came from. `{"1":5,"2":4,"3":3,"4":2,"5":1,"6":0.5}`, **byte-identical in both settings files. No `AgreementPointMap` exists.** One map, as claimed |
| `Derive_status` rounding-order fix is real | Read all three comparisons and the write payload | ✅ **All three** threshold comparisons read `outputs('Round_the_circumstance_score')`, and `rev_circumstancescore` is written from the same output. Status and stored score cannot disagree. Arithmetically confirmed that the pre-fix form was harmful: unrounded 20.5 is neither `≤ 20` nor `≥ 21`, so it fell through to **2 (Auto-pass)** |
| The life-satisfaction bounds fix is real | Read the withhold gate's third condition | ✅ A **third** `or` condition withholds when `Parse_feeling_scale_inversion?[answer]` resolves empty, and `Parse_feeling_scale_inversion` runs **before** the gate. The wellbeing filter is likewise `@or(empty(response), empty(map?[response]))` |
| The scoring chain is downstream of the gate | Read `runAfter` chain | ✅ `Initialise_likert_points` runs after the gate, whose true branch `Terminate`s. No score can be computed past a withhold |
| `rev_agreementresponse` exists with the right six values | Read the option-set XML | ✅ `1 Strongly Disagree, 2 Disagree, 3 Neutral, 4 Agree, 5 Strongly Agree, 6 Not sure` |
| `rev_likertresponse` gained value 6 | Read the option-set XML | ✅ Six values; `6 = Not sure`. Labels 1–5 unchanged |
| `rev_wellbeinganswer8/9/10` **actually reference** the new option set | Parsed the `<attribute>` blocks in `Entities/rev_application/Entity.xml` — not merely checked the file exists | ✅ `8`, `9`, `10` → `rev_agreementresponse`; `1`–`7` → `rev_likertresponse`. **The rebind is real, on exactly the three intended columns** |
| The new option set actually ships | Counted inside both fresh zips **and** both stored zips | ✅ `optionsets` **16** (was 15) and `RootComponents` **36** (was 35) in all four. `verify-solution-root-components.py` → PASS, 36 declared, all defined, nothing undeclared |
| Intake bounds | Parsed the trigger schema | ✅ All **ten** `wellbeing_answer_*` carry `minimum 1 / maximum 6`; `feeling_scale_answer` carries `0 / 10`. **Zero unbounded scored answers.** `required` still exactly the four fields; still **82** properties |
| Pester suite | **Re-ran** `pwsh -NoProfile -File src/tests/Invoke-Tests.ps1 -CodeCoverage -CoverageThreshold 80` | ✅ **560 passed, 0 failed, 1 skipped**; coverage **92.60%** (1188 of 1283 commands); exit 0. Matches `manifest.json` exactly. +23 tests since build #2 |
| `pac solution pack`, both types | **Re-ran both** against `src/solutions/RevitaliseGrantAutomation` | ✅ Both exit 0. Both zips are exactly the 7 entries a real export contains; `<Managed>1</Managed>` / `<Managed>0</Managed>`; the two `customizations.xml` are byte-identical (same SHA-256), which is correct |
| The packages are not silently empty | Opened both fresh zips and counted | ✅ Entities 4, Roles 2 (**73** privileges = 40 + 33), Workflows 4, `FieldSecurityProfile REV_TrusteeRestricted` with **34** `FieldPermission` (cancreate/canread/canupdate = 34 each), EntityRelationship 1 with `CascadeDelete = Cascade`, optionsets 16, AppModule 1, AppModuleSiteMap 1, 3 `environmentvariabledefinition`, 3 `connectionreference`, 36 RootComponents, `Version 1.0.0.0` |
| The stored build #3 artifact is the thing that was tested | `shasum -a 256` against `manifest.json`, then opened both | ✅ Both hashes match (`c08cf6b1…` managed, `a3226ec7…` unmanaged). The **stored** zips carry the `float()` cast, the `float` variable, `rev_agreementresponse` and value 6. **Artifact and source agree** |
| `gitleaks --no-git` is genuinely in the config | Read `config/revitalise-grant-automation-build.yml`, then **ran the command exactly as the config specifies it** | ✅ Line 91: `gitleaks detect --source . --no-git --no-banner --redact --exit-code 1`. Executed: **3.07 MB scanned, no leaks found, exit 0.** **D-006 closed for real this time** |
| Field-security coverage | **Re-ran** `verify-field-security-coverage.py` | ✅ PASS — 34 secured columns, all released, 1 reviewed exemption |
| FR-016 still holds after two flow edits | **Independent extraction** of every `rev_*` token from the scoring definition with descriptions stripped, intersected against the secured set | ✅ 25 tokens, 34 secured columns, **intersection empty** |
| Provisioning scripts still parse | pwsh AST parse of all 22 `.ps1` under `provisioning/` | ✅ 22 scripts, **0 parse errors** |
| `MaxCircumstanceScore` did not need re-deriving | Recomputed both ends of the range | ✅ Max = 10 + (10 × 5) = **60**, unchanged. Floor of a fully answered application = 0 + (10 × 0.5) = **5**, down from 10 — as the amendment says, and `rev_circumstancescore`'s `MinValue 0` accommodates it |
| The daily summary email does not assume an integer score | Parsed the Daily Summary definition | ✅ **It never reads `rev_circumstancescore` at all** — `rev_circumstancescore` appears **0 times**; the four queries filter on `rev_status` and `rev_scoredon` only. No integer assumption to break |
| The borderline routing does not assume an integer score | Read `Route_borderline_applications_to_the_person` condition | ✅ It tests `Derive_status` equals `3`, not the score. Correct — and it therefore inherits D-015 rather than adding to it |

### Three findings this pass produced that no document records

**1. `D-015` (NEW, P2) — the rounding function does not implement the approved rounding rule.** Full
entry in §4.2. This is the significant one: it is a decision-affecting arithmetic defect inside the
fix for a decision-affecting arithmetic defect, and the plain-English text the charity would show a
trustee to justify the decision asserts the behaviour that is not implemented.

**2. `D-016` (NEW, P4) — the ground-truth CSV contradicts this report's own revision-3 finding about
which questions offer "Not sure".** Revision 3's verified fact 1 counted the live form's field 132
(the seven SWEMWBS statements) as **7 × 5 = 35 radio inputs — no "Not sure" column** — and field 134
as 3 × 6. But **CSV row 25 answers "Not sure" to all ten questions, including all seven SWEMWBS
ones**, and it is a real scored application. One of the two observations is stale: either the live
form changed, or the CSV predates it, or the input count missed a column. **Revision 0.8's decision
to add value 6 to *both* option sets is correct under either reading**, so nothing is unsafe — but
the discrepancy sits directly under the M-02 / D-008 option-set mapping work and should not be
carried forward silently.

**3. The trustee-facing breakdown does not carry the benefit of the option-set split.**
`rev_agreementresponse` exists because, in the option set's own words, storing an agreement answer
under a frequency label "would corrupt the EVIDENCE: `rev_scorebreakdown` and every trustee-facing
view would describe an applicant who strongly disagreed that they had managed a break as having had
one 'None of the time'". That reasoning is sound for the **Dataverse form and view rendering** of
`rev_wellbeinganswer8/9/10`, which is where it bites. It is **not** true of `rev_scorebreakdown`
itself: `Record_this_answer_in_the_breakdown` emits `'Wellbeing answer 8: response 1 = 5 points'` —
the **numeric option value**, no label, from either scale. So the breakdown text neither had the
problem nor gained the fix, and a trustee reading it still cannot see what the applicant answered.
Folded into D-015's remedy as a **P4**, not raised separately.

### Retest execution counts — report revision 4

Separate from §1 and from revision 3's counts, both preserved as the record of what was run then.

| Layer | Run in this retest | Passed | Failed | Still blocked |
|---|---|---|---|---|
| Unit (automated — Pester) | 561 | 560 | 0 | 1 skipped (D-011, deliberately) |
| Unit (manual re-derivation) | 31 | 29 | 2 | 0 |
| Integration | 1 (payload contract vs schema bounds) | 1 | 0 | 14 (no environment) |
| End-to-End | 0 | 0 | 0 | 26 (no environment) |
| Regression | 561 | 560 | 0 | 1 |
| Security | 10 (source + provisioning chain + secret scan from config) | 10 | 0 | 11 (live enforcement) |
| Accessibility | 0 — **not re-run, and not softened** | 0 | 0 | 11 (D-004: 2 confirmed FAIL, 9 never assessed) |
| Performance | 0 | 0 | 0 | 4 (no threshold exists) |
| Provisioning | 6 (scripts, wiring, settings, package) | 6 | 0 | 21 (Graph / Web API) |
| Constraint | 14 | 14 | 0 | 0 |
| **Total** | **1184** | **1180** | **2** | **89** |

> **The two manual-unit failures are D-015's two instances** — the `20.5 → 20` knockout case and the
> `30.5 → 30` band case, each demonstrated by executing `ToString("F0")` on the .NET runtime available
> here rather than by reading the expression.
>
> **The Accessibility row reads 0 run, and that is not an improvement.** D-004's two confirmed
> failures stand exactly as recorded at revision 3, and its nine unassessed criteria are still
> unassessed by anything. Revision 0.8 touched no accessibility surface, so re-running the two
> confirmed criteria would have added a number to this table and no information. **The audit has
> still never been run, and it is still not blocked on anything.**

---

## Retest, 2026-08-13 — report revision 3

**What changed at the gate: the constraint check is no longer BLOCKED.** Revision 1 of this report
failed two HARD technology constraints, C-TECH-006 and C-TECH-014. Both are now **PASS**, verified
by execution rather than by reading the Dev Summary. That is the single most important change since
revision 2, and it is the only thing that moved the gate.

**What did not change: five of the nine test layers still cannot be executed at all.** No Power
Platform environment exists. Nothing in §0 or §6 has been softened, and §8's deferred work list is
longer after this pass, not shorter.

### What was re-verified by execution, not accepted from the document

Every claim in the Dev Summary's revisions 0.6 and 0.7 that this gate depends on was re-derived from
source or re-run. The method is the standing rule set in §0: this repository has now produced, on
three separate occasions, a confident claim or a clean exit code that was wrong on inspection — six
solution-packaging defects that packed with exit 0 while silently dropping the field security
profile, and the `date_of_birth` / `email` required-field bug that survived two full revisions and a
passing test because the test asserted the document rather than the world.

| Check | Method actually used | Result |
|---|---|---|
| Intake trigger `required` array | Parsed the flow JSON, read the array | ✅ Exactly `[submission_id, first_name, last_name, postcode]` |
| The guard, the 400 body and the log line agree with it | Read all three from the parsed definition | ✅ `Reject_incomplete_payload` tests exactly those four with `empty(coalesce(…, ''))`; 400 body `required` string is the same four; `Log_incomplete_payload` names the same four and **no value** |
| `rev_dateofbirth` write is null-safe | Read the expression, not a comment | ✅ `if(empty(coalesce(triggerBody()?['date_of_birth'], '')), null, formatDateTime(…))` |
| `rev_email` write is null-safe | Read the expression | ✅ `if(empty(coalesce(triggerBody()?['email'], '')), null, toLower(trim(…)))` |
| `Compute_age_in_years` cannot throw on an absent date of birth | Read the expression | ✅ Returns `-1` when absent, so `formatDateTime` is never reached |
| `Derive_age_range` tests the band **before** the date-of-birth path and cannot emit out of range | Read the expression and the option set | ✅ Label map → `Compute_age_in_years < 0 → 9` → band match → `9`. `AgeRangeLabelMap`'s eight target options are 2–8 and 9; `rev_agerange` has 1–9. No route out of range |
| `AgeRangeLabelMap` labels match what the live form actually sends | Extracted the eight `input_26` radio values from the live page's own HTML | ✅ `18-24, 25-34, 35-44, 45-54, 55-64, 65-74, 75 or over, Prefer not to say` — byte-identical to the map, in both settings files, byte-identical between them |
| `group_linkage` is gone from the write path | Token count over the definition **with descriptions stripped** | ✅ `group_linkage` 0, `rev_grouplinkage` 0. 82 schema properties, as claimed |
| The live form really never asks a date of birth | Case-insensitive count of "birth" in the fetched page | ✅ **0 occurrences** |
| Email really is conditional | Read the form's own embedded conditional-logic map | ✅ Field 19 (Email) shown only when field 21 = `Email`; field 21 offers `Email / Phone / Post`, so **Post alone is a valid submission with neither** |
| The four required fields really are unconditional | Checked `gfield_contains_required` and the logic map for fields 14 and 15 | ✅ Name (15) and Address (14) are required **and are not conditional targets**. Age Range (26) is **not** required |
| Pester suite | **Re-ran** `pwsh -NoProfile -File src/tests/Invoke-Tests.ps1 -CodeCoverage -CoverageThreshold 80` | ✅ **537 passed, 0 failed, 1 skipped**; coverage **92.60%** (1188 of 1283 commands) against the 80% threshold; exit 0. Matches the manifest exactly |
| The coverage gate actually fails below threshold | **Re-ran the same command with `-CoverageThreshold 99`** | ✅ Exit code **1**. It is a gate, not a report |
| `pac solution pack`, both package types | **Re-ran both** against `src/solutions/RevitaliseGrantAutomation` | ✅ Both exit 0. Both zips are exactly the 7 entries a real export contains |
| The packages are not silently empty | Opened both fresh zips and counted components | ✅ Entities 4, Roles 2 (**73** role privileges = 40 + 33), Workflows 4, `FieldSecurityProfile REV_TrusteeRestricted` with **34** `FieldPermission` (cancreate/canread/canupdate = 34 each), EntityRelationship 1 with `CascadeDelete = Cascade`, optionsets 15, AppModule 1, AppModuleSiteMap 1, **3** `environmentvariabledefinition`, **3** `connectionreference`, 35 RootComponents, `Version 1.0.0.0` |
| Managed really is managed | Read `solution.xml` in each fresh zip | ✅ `<Managed>1</Managed>` / `<Managed>0</Managed>`; the two `customizations.xml` are byte-identical (same SHA-256), which is correct — only the package type differs |
| The stored build #2 artifact is the thing that was tested | `shasum -a 256` against `manifest.json`, then opened it | ✅ Both hashes match. The **stored** managed zip carries the revision 0.7 intake fix (`required` = the four fields, `age_range` accepted, `group_linkage` absent) — the artifact and the source agree |
| Field-security coverage | **Re-ran** `verify-field-security-coverage.py` | ✅ PASS — 34 secured columns, all released, 1 reviewed exemption |
| Root-component resolution | **Re-ran** `verify-solution-root-components.py` | ✅ PASS — 35 declared, all defined on disk, nothing undeclared |
| The two new provisioning scripts exist and are real | `ls`, then pwsh AST parse of **all 22** `.ps1` under `provisioning/` | ✅ Both exist; **0 parse errors across all 22**. `ensure-intake-client.ps1` is check-before-create (`Get-MgApplication` before `New-MgApplication`), emits CREATED/EXISTS/FAILED, takes `-Env`, and reports credential posture by **count only** (`KeyCredentials`/`PasswordCredentials` `.Count`, never a value) |
| The smoke test is wired in | Read `config/revitalise-grant-automation-pipeline.yml` | ✅ `ensure-intake-client.ps1 -Env test\|prd` in `tenant_prerequisites` (lines 328, 334); `verify-intake-endpoint-auth.ps1 -Env test` in TST/ACC `smoke_tests` (line 515) and `-Env prd` in PRD `smoke_tests` (line 634); a named manual `post_deploy` step on both environments with **Wanstor** as the owner and the exact value to set |
| The smoke test's discriminator still matches the flow | Compared the script's regex to the flow's actual 401 body | ✅ Script matches `"error"\s*:\s*"unauthorised"`; the flow's `Respond_401_unauthorised` body is `{"error": "unauthorised"}`. The coupling holds, and `IntakeContract.Tests.ps1` asserts it |
| The settings keys the smoke test reads exist | Parsed both settings files | ✅ `intake.endpointUrlEnvVar` and `intake.triggerAuthentication.unauthenticatedExpectedStatusCodes` (`[401, 403]`) present in both. The endpoint URL is held as a CI secret, never as a settings value |

### Two findings this retest produced that no document records

**The good news about D-003 and D-005 did not stop the pass.** Two things were found, and the first
is the more serious finding in this retest.

**1. A new P2 — `D-014`. The live form can send three answers the schema cannot store and the score
cannot map, and the fail-closed design does not cover it.** This is not caused by revision 0.7. It
was latent from revision 0.3, and revision 0.7's audit of the live form is what made it visible —
but revision 0.7 deliberately changed no option set, so it is live. It is recorded in the form
document only as a *mapping gap needing Emily's decision* (M-02, V-08, V-10), which understates it:
the Revitalise side has no defence, and the failure mode is a lost application. Full detail in §4.

> 🔧 **development-agent, 2026-08-13 (dev-summary revision 0.8): both findings now have fixes
> delivered, awaiting test-agent verification.** D-014's remedy turned out to be the *opposite* of
> the one recommended below — ground-truth data proved "Not sure" is a **valid answer worth 0.5
> points**, not unusable input, so it was implemented as a real sixth option rather than rejected
> by a guard. See the annotation at the end of §4.1, which also credits verified fact 6 with
> catching a gap in the first version of the fix. D-006's `--no-git` is now genuinely in the
> config, evidenced by a run of the command as the config specifies it.

**2. `D-006` is not fixed, and the manifest and the config disagree about it.** `manifest.json`
records the executed step as `secret-scan (--no-git)`, and re-running `gitleaks detect --no-git` is
indeed clean (2.89 MB, no leaks — up from 1.84 MB because `src/tests/` now exists). But
`config/revitalise-grant-automation-build.yml` line 77 is still
`gitleaks detect --source . --no-banner --redact --exit-code 1` — **the flag was never added to the
config.** So the passing scan is not reproducible from the repository, and a CI run driven by the
config alone reverts to scanning git history, which covers none of the untracked solution source.
D-006 stays **open**, and the manifest's step label overstates what the config will do.

### One packer message that must not be read as a signal

Both `pac solution pack` runs printed *"Following root components are not defined in
customizations"* for seven items — the entity relationship, all three environment variable
definitions and all three connection references. **All seven are demonstrably present in the
packaged `customizations.xml`** (counted above), and `verify-solution-root-components.py` passes. So
the message is a packer reconciliation quirk here, not a dropped component. It is recorded because
it is uninformative in **both** directions: a genuinely missing component would print the same line.
That is precisely why recommendation 8 (a `verify-package-contents` build step) still stands — the
only sufficient check remains opening the zip.

### Retest execution counts

Separate from §1, which is preserved as the record of what was run on 2026-08-12.

| Layer | Run in this retest | Passed | Failed | Still blocked |
|---|---|---|---|---|
| Unit (automated — Pester) | 538 | 537 | 0 | 1 skipped (D-011, deliberately) |
| Unit (manual re-derivation) | 24 | 22 | 2 | 0 |
| Integration | 1 (payload contract vs live form) | 1 | 0 | 14 (no environment) |
| End-to-End | 0 | 0 | 0 | 26 (no environment) |
| Regression | 538 | 537 | 0 | 1 |
| Security | 9 (source + provisioning chain) | 9 | 0 | 11 (live enforcement) |
| Accessibility | 2 (re-confirmed 1.3.5, 3.3.7) | 0 | 2 | 8 (audit never run) |
| Performance | 0 | 0 | 0 | 4 (no threshold exists) |
| Provisioning | 6 (scripts, wiring, settings) | 6 | 0 | 21 (Graph / Web API) |
| Constraint | 14 | 14 | 0 | 0 |
| **Total** | **1132** | **1126** | **4** | **86** |

> The two manual-unit failures are **D-014's two instances**. The two accessibility failures are
> **D-004's two confirmed criteria, re-verified independently** — 251 `<input>` elements carrying
> exactly five `autocomplete` attributes (one honeypot `new-password`, four `off`), and the two
> confirm-email pairs. Re-verification found the same result, so D-004 is not softened.
>
> **Regression is no longer "N/A — no suite exists".** A suite exists, it runs, and it caught the
> revision 0.7 contract change it was written to catch. That is D-005's substantive closure.

---

## Update, 2026-08-13 — D-003 closed, D-004 PARTIAL, and a correction to this report's own basis

Two defects from this run have been worked. **One correction to the report's premise comes first,
because it changes how three of its sections should be read.**

**This report assessed Automation #1 as "a build contract for Alex, the external website designer" —
a specification for a form that had not yet been built.** That was wrong, and the error was inherited
from the document under test rather than introduced here. **The form already exists, is live, and Alex
already built it:** https://revitalise.org.uk/apply-for-funding/, a 20-page Gravity Forms form. The
163-column CSV in `docs/Import/` is a description of *that* form's export layout, not a target.

`docs/development/revitalise-grant-automation-form-validation-spec.md` has been rewritten
(**revision 1.0**) as documentation of the live form, established from the live page's own HTML and its
embedded conditional-logic map. Consequences for this report:

| Section | What changes |
|---|---|
| **§2.1** | The FR-001 to FR-006 results were assessed against acceptance criteria in a specification. They are now re-stated against **what the live form actually does**. Two FRs move to FAIL that previously passed — FR-005 and FR-006 are **not implemented on the live form at all**. That is not a regression; it is the first time they were measured against reality. |
| **§3 / §4** | **D-003 is RESOLVED**, in the code as well as the document. **D-004 is PARTIAL** — one criterion confirmed as a real failure, the rest genuinely unaudited. **D-002 and D-008 change basis** without closing. **D-010 is superseded.** See the revision block at the head of §4. |
| **§8** | The Accessibility row's premise ("once Alex delivers") was wrong — the surface exists and can be scanned today. Rewritten. |
| **§9** | Recommendations 2 and 3 rewritten. |

**The run counts in §1 are left exactly as they were.** They record what was executed on 2026-08-12
and re-writing them would destroy that record. Current defect status is in §4's revision block.

---

## 0. Read this first — what this test run could and could not do

**No Power Platform environment exists.** `pac admin list` confirms only the tenant's "Default"
Dataverse environment. DEV, TST/ACC and PRD (WBS 0.2) have never been provisioned, and neither has
the Power Platform Pipelines host environment (TAD §12, ADR-007). Five of the nine test layers
therefore **cannot be executed at all** — not "were skipped", not "passed", **cannot be executed**.

| Layer | Executable now? | Basis | Change at retest (rev 3) |
|---|---|---|---|
| Unit (declarative logic, configuration arithmetic) | ✅ Executed | Source inspection + configuration reconciliation | **Now also automated** — 537 Pester assertions run and pass |
| Integration | ⛔ **BLOCKED — no environment** | Requires live Dataverse + bound connections | Unchanged |
| End-to-End | ⛔ **BLOCKED — no environment** | Requires live flows; also blocked on WBS 0.3 | Unchanged |
| Regression | ~~⚪ N/A — first release~~ → ✅ **Executed** | A suite now exists (`src/tests/`, 537 tests) and re-ran clean | **Changed — D-005** |
| Security | ◐ **Partially executed** | Source/design layer executed in depth; live enforcement BLOCKED | Provisioning chain for the endpoint control now exists and was verified; **live enforcement still BLOCKED** |
| Accessibility | ◐ **Partially executed** | Two criteria confirmed FAIL from the live page's HTML; the other nine unaudited | Re-confirmed, not softened. **The audit has still never been run** |
| Performance | ⛔ **BLOCKED — and no threshold exists** | NFR-022 / SDD OQ-020 records no measurable target | Unchanged |
| Provisioning | ◐ **Partially executed** | Scripts reviewed and parsed; Graph / Dataverse Web API assertions BLOCKED | 22 scripts parse clean (was 20); wiring verified. **Live assertions still BLOCKED** |
| Constraint Verification | ✅ Executed | 14 in-scope rows, both severities | **BLOCKED → PASS** |

> **Read the Regression row carefully.** The suite that now exists covers the **provisioning
> PowerShell** and **static invariants of the flow JSON**. It does not execute a flow, because no
> environment exists to execute one in. Coverage of the provisioning scripts is not coverage of the
> solution, and the Dev Summary says so itself.

> **⚠️ Unchanged at the second retest (revision 4), and D-015 is the clearest demonstration of it yet.**
> The table above is identical for revision 4 except that the suite is now 560 tests. **Five layers
> still cannot be executed at all.** The Unit row grew again — and D-015 is a defect that *only*
> surfaced because a value was pushed through a real runtime instead of being read off an expression.
> Everything in the scoring flow that has been reasoned about but never executed is in exactly the
> position `Round_the_circumstance_score` was in before this report. That is not an argument for
> confidence in the rest; it is an argument for §8.
>
> The Accessibility row is unchanged and **was not re-run**, because revision 0.8 touched no
> accessibility surface. Two criteria remain confirmed failures, nine remain assessed by nothing, and
> the audit remains the one deferred item that **is not blocked on any environment**.

> **⚠️ Unchanged again at the third retest (revision 5), with one qualification that cuts the other way.**
> The table above is identical for revision 5 except that the suite is now **577** tests. **Five layers
> still cannot be executed at all.**
>
> The qualification: the Unit row is now stronger than a count suggests. At revision 4 this note argued
> that "everything in the scoring flow that has been reasoned about but never executed is in exactly the
> position `Round_the_circumstance_score` was in before this report." **That is now less true of the
> rounding specifically** — it is the first step in the scoring chain whose behaviour the suite
> *executes* rather than inspects, over every input it can receive. **It remains entirely true of the
> rest of the flow.** Nothing else in the scoring engine, and nothing at all in the intake, has ever
> been run by anything. The lesson generalises; the fix does not.
>
> **`pac solution pack` could not be executed at this retest** — blocked by this session's command
> permissions. The stored zips were opened and verified instead. See the note in the revision 5 block.
>
> The Accessibility row is unchanged and **was not re-run**, for the same reason as at revision 4:
> revision 0.9 touched one expression, one comment and some documents. **Two criteria remain confirmed
> failures, nine remain assessed by nothing, the audit has still never been run, and it is still not
> blocked on anything.** It is now the top recommendation in §9.000 because everything above it closed.

**No result in this report is asserted for anything that was not actually run.** Where the Dev
Summary's own §9 test guidance defines a case that needs an environment, that case is carried into
§8 (Deferred Test Execution) verbatim in intent, not marked passed.

**The methodological posture of this run.** Dev Summary revision 0.5 recorded that six of nine
solution-packaging defects produced a clean, exit-0 `pac solution pack` while silently dropping
components — including the field security profile that 34 secured columns depend on. That lesson was
applied here as a standing rule: **no claim in the Dev Summary was accepted on the strength of the
document asserting it.** Every load-bearing statement below was re-derived from the source, the
packaged archive, or a re-run of the check. Three of the thirteen defects in §4 were found precisely
because a stated count or a stated control did not survive that re-derivation.

---

## 1. Test Summary

"Run" counts distinct verification cases actually executed. Cases that cannot be executed are counted
in §8, not here.

| Layer | Run | Passed | Failed | Skipped / Blocked |
|---|---|---|---|---|
| Unit | 21 | 20 | 1 | 0 |
| Integration | 1 (contract review only) | 0 | 1 | 14 (blocked — no environment) |
| End-to-End | 6 (spec acceptance criteria) | 5 | 1 | 26 (blocked — no environment) |
| Regression | 0 | 0 | 0 | 0 (n/a — first release, and no suite exists) |
| Security | 19 | 17 | 2 | 11 (blocked — live enforcement) |
| Accessibility | 12 | 11 | 1 | 3 (blocked — no built surface) |
| Performance | 0 | 0 | 0 | 4 (blocked — and no NFR threshold exists) |
| Provisioning | 9 | 9 | 0 | 21 (blocked — Graph / Web API assertions) |
| Compliance / Constraint | 13 | 11 | 2 | 0 |
| **Total** | **81** | **73** | **8** | **79** |

> **Reading the two "Run" qualifiers.** The Integration and End-to-End rows count reviews of the
> *specification and the payload contract*, not executions against a system — there is no system to
> execute against. Automation #1 ships as a specification, so reviewing its six acceptance criteria is
> the only E2E verification available for FR-001–FR-006.
>
> **Why the failure cells sum to 8 but §3 lists 7 findings.** The Compliance row counts the 13 in-scope
> constraint rows, and one of its two failures (C-TECH-006) is the constraint-layer expression of the
> same finding as Security's TC-401 / defect D-001. **There are 7 distinct findings, counted once each
> in §3 and §4.**

**Environment:** local workstation; `pac` 2.4.1 (+ 2.9.3 available), Python 3.14, pwsh 7.6.4,
gitleaks present. No Dataverse tenant target.

**Test data:** none created — no environment to create it in. All fixtures required for §8 are
specified as synthetic per C-TECH-007; no production extract exists or was used.

### 1.1 Independent re-verification of the build artifact

The Build/Provisioning evidence in `manifest.json` and `logs/build.log` / `logs/routing.log`
(2026-08-12 22:2x) was **not** taken on trust. It was independently reproduced:

| Check | Method | Result |
|---|---|---|
| Artifact integrity | `shasum -a 256` on both zips vs `manifest.json` | ✅ Both match byte-for-byte (`f467ba43…` managed, `baee267e…` unmanaged) |
| Archive is a real solution export, no stray sharded files | `unzip -l` on both | ✅ Exactly 7 entries each — `customizations.xml`, `solution.xml`, 4 flow `.json`, `[Content_Types].xml` |
| Component collections non-empty | Parsed packaged `customizations.xml` | ✅ Entities 4, Roles 2, Workflows 4, FieldSecurityProfiles 1, EntityRelationships 1, optionsets 15, AppModules 1, AppModuleSiteMaps 1, EnvironmentVariables 3, connectionreferences 3 — every count equals Dev Summary §2.5.4 |
| Package type resolves per artifact | Parsed packaged `solution.xml` | ✅ `<Managed>1</Managed>` in managed zip, `<Managed>0</Managed>` in unmanaged; 35 RootComponents and Version 1.0.0.0 in both |
| Field security profile actually shipped (the worst of the nine silent defects) | Counted `FieldPermission` elements **inside the managed zip** | ✅ `REV_TrusteeRestricted`, 34 permissions, `cancreate/canread/canupdate = 4` |
| Retention cascade actually shipped | Read `EntityRelationship` **inside the managed zip** | ✅ `rev_applicant_rev_application_applicantid`, 16 children, `CascadeDelete = Cascade` (+ Assign/Reparent/Share/Unshare) |
| Role privilege counts survived the revision 0.5 edit | Counted `RolePrivilege` inside the managed zip | ✅ `REV Admin` 40, `REV Service Automation` 33 |
| Repo verification scripts | Re-ran both | ✅ `verify-field-security-coverage.py` → PASS, 34 secured columns all released, 1 reviewed exemption. `verify-solution-root-components.py` → PASS, 35 root components, both directions |

**Conclusion:** the Build layer's claim to have been verified by archive inspection rather than exit
code is accurate, and `pac solution pack` was not re-run for this report because there is no reason
to doubt it. This is the strongest-evidenced part of the release.

---

## 2. Requirement Coverage

All **55** SDD functional requirements are traced. **22 are in Phase 1 scope**
(FR-001–FR-006 Automation #1 as a specification, FR-007–FR-010 Automation #4, FR-011–FR-022
Automation #2). **33 are deferred** (FR-023–FR-055) and their absence from `src/solutions/` was
verified, not assumed.

### 2.1 Automation #1 — Form Validation & Completeness (specification deliverable, out-of-palette)

The deliverable is `docs/development/revitalise-grant-automation-form-validation-spec.md`. **The
original assessment below treated it as a build contract for a form that did not yet exist.** The form
exists and is live; revision 1.0 of that document records what it actually does. Both readings are kept
here — the original for the record, the re-assessment because it is the one that is true.

**Re-assessed 2026-08-13 against the live form** (its own HTML and conditional-logic map):

| FR ID | Requirement | Result against the LIVE form | Evidence |
|---|---|---|---|
| FR-001 | Block submission when any mandatory field empty | ◐ **PARTIAL — and wrong in both directions** | 61 of 71 question fields are marked required and per-page validation blocks progress. But the required set does not match the requirement: **no email address is guaranteed** (the Email field is conditional on "Preferred contact method" including Email, so a postal-preference applicant supplies none), **no date of birth is collected at all** and the age-band question is optional, and the break date is one required **free-text** box. Meanwhile six helper fields and three exceptional-funding fields are required of applicants they do not apply to, which manufactures wrong data rather than preventing it. Spec §7 V-01 to V-05 |
| FR-002 | Plain-English field-specific guidance and validation messages | ⚪ **NOT ASSESSED** | Error messages are produced on a failed submission and cannot be read from a read-only fetch. The visible help text *is* plain and appropriately kind. Needs a live pass — spec OPEN-26 |
| FR-003 | Financial detail questions only after income band selected; carer questions only if travelling with a carer | ◐ **PARTIAL, on a different basis than D-002 recorded** | The live form has 23 conditional rules and the delicate ones are right — every "Other (please specify)" box is gated on its own option, and the two condition-detail fields are correctly gated on their own checkbox group rather than crossed. **But the gate is on benefit status, not income band**: employment, income band, care costs and the £6,000 savings test are all shown only when the applicant says they receive **no** means-tested benefits. And four gates are missing entirely (the whole helper page, three of four exceptional-funding fields, the repeat-funding follow-up, and both support-recipient pages). The carer questions FR-003 names are **not asked at all** |
| FR-004 | Completion-progress indicator | ✅ **PASS** | "Step 1 of 20" in words plus a percentage, on every page |
| FR-005 | Save and resume a partial application | ❌ **FAIL — not implemented** | Gravity Forms' save-and-continue is switched off (`gform_save_link` absent). A 20-page form with no way to pause, for a population that often needs another person's help to finish |
| FR-006 | Pre-submission summary with per-section edit | ❌ **FAIL — not implemented** | There is no review screen. The phrase "check your answers" appears nowhere and page 20 leads straight to submit |

**FR-005 and FR-006 are the two the live form does not implement at all**, and both bear directly on
the 60% problem this programme exists to solve. Neither was a regression — this is the first time
either was measured against the running form rather than against a paragraph describing one.

<details>
<summary><b>Original 2026-08-12 assessment, retained for the record</b> — read as an assessment of a document, not of a form</summary>

| FR ID | Requirement | Test Case(s) | Result |
|---|---|---|---|
| FR-001 | Block submission when any mandatory field empty | TC-101 — all six SDD-named categories checked individually against the spec's field tables | **PASS (conditional)** — all six are mandatory: full name (F01+F49), DOB (F06), postcode (F05), financial situation (F20/F21/F23/F60/F62), holiday dates (F36/F37), provider preference (F38). Enforcement is specified as server-side, not browser-side ("Browser-side validation is a convenience. Server-side validation is the control"). **Conditional on D-008**: F53 is mandatory but cannot be built while its option list is a placeholder (OPEN-20) |
| FR-002 | Plain-English field-specific guidance and validation messages | TC-102 — per-field message text + nine binding style rules | **PASS with defect** — verbatim per-field messages throughout, plus explicit prohibitions ("No 'mandatory', 'valid', 'populate', 'criteria', 'submit an entry', 'field'"). **Three messages breach the spec's own rule 1** (F85/F86/F87 all read "Please tick the box to confirm this." and name no field) — **D-010** |
| FR-003 | Financial detail questions only after income band selected; carer questions only if travelling with a carer | TC-103 — conditional-reveal trigger table | ❌ **FAIL** — the carer half is fully specified. **The income-band gate the FR names has been deliberately removed** ("F20 no longer reveals anything… they are all shown together and none is gated behind F20"), the eight financial questions are now asked *before* the band, no SDD change request records the deviation, and a contradictory revision-0.1 instruction survives elsewhere in the same document. **D-002** |
| FR-004 | Completion-progress indicator | TC-104 | **PASS** — "Step 3 of 7" plus step name, `aria-current="step"`, also in `h1` and `<title>`, explicitly "announced, not only drawn", never colour alone, percentages alone prohibited |
| FR-005 | Save and resume a partial application | TC-105 | **PASS** — control on every step; "Saving must never validate"; opaque token ≥128 bits; "no time limit that causes the applicant to lose work (WCAG 2.2.1)". Retention of abandoned drafts is PROPOSED and blocked on OPEN-4 — a genuine compliance gap the spec names itself |
| FR-006 | Pre-submission summary with per-section edit | TC-106 | **PASS** — answers grouped by the seven steps, a per-section "Change" link with an accessible name that says what it changes, return-to-review behaviour, 3.3.4 confirmation wording |

</details>

### 2.2 Automation #4 — Website → System-of-Record Intake (`REV | Intake | WordPress to Dataverse`)

Verified by reading the flow definition JSON directly, not its self-describing comments.

| FR ID | Requirement | Test Case(s) | Result |
|---|---|---|---|
| FR-007 | Create an application record automatically on submission | TC-201 — `Create_application` action present, `entityName: rev_applications`, applicant matched-or-created first, `rev_applicantid@odata.bind` resolved | **PASS (design)** — live create BLOCKED (§8). Casing of the bind navigation property remains unvalidated (Dev Summary §7.1 item 4) |
| FR-008 | Unique `REV-YYYY-NNN` reference + submission timestamp | TC-202 — autonumber `REV-{yyyy}-{nnn}` on `rev_application.rev_name`; flow deliberately does **not** set `rev_name` | **PASS (design)** — format cannot drift because it is platform-enforced rather than flow-composed. TAD §3.5 conflict #1 correctly resolved in the SDD's favour |
| FR-009 | Teams notification with applicant name and reference | TC-203 — `Notify_process_owner_of_new_application` | **PASS (design)** — 1:1 chat to `rev_ProcessOwnerUpn` (ADR-015), body carries `concat(first_name, ' ', last_name)` + `rev_name`. The one notification that legitimately carries personal data |
| FR-010 | Record the failure and alert on intake failure | TC-204 — `Log_incomplete_payload` and `Alert_on_failure` both call child flow `8f1c2a44-1004-…`; 400 and 500 response paths present | **PASS (design)** — no submission path terminates without either a record or a logged, alerted failure. 500 returns `retry: true`, made safe by the replay guard |

**Additional intake findings (not FR-numbered but load-bearing):**

- **Idempotency guard verified** — `Find_application_with_this_submission_id` queries the
  `rev_sourcesubmissionid` alternate key *before* any write, and `Return_the_existing_reference_if_this_is_a_replay`
  responds 200 and terminates. Dev Summary D-2 narrows TAD §5.1 from "update" to "no-op"; the
  narrowing is implemented as described and is the safer behaviour (it cannot overwrite an FR-018 override).
- **Breaking payload contract verified as fully applied.** With description strings stripped, the
  executable definition contains **zero** occurrences of `full_name`, `referee_*`,
  `emergency_contact_*`, `wellbeing_answer_11`, `financial_answers` or `"costs"`. Trigger `required`
  array is exactly `[submission_id, first_name, last_name, email, postcode, date_of_birth]`, matching
  the completeness check, the 400 body and the log message. 82 schema properties.
  > **⚠️ Corrected 2026-08-13.** That required array was internally consistent and **externally
  > wrong**. The live form never collects a date of birth and only collects an email address when the
  > applicant picks Email as their preferred contact method, so **the flow as tested would have
  > rejected every real submission with a 400.** The required array is now
  > `[submission_id, first_name, last_name, postcode]` — the four the live form always collects — the
  > completeness check, the 400 body and the log line move with it, and `group_linkage` has been
  > removed while `age_range` has been added. Still 82 properties. **D-003.**
  >
  > **✅ Re-verified at retest (rev 3), from the JSON and from the live page.** The `required` array
  > reads exactly those four. The reject guard, the 400 body and the `Log_incomplete_payload` message
  > name the same four and no others, and the log line names *field names* only, never a value. With
  > descriptions stripped, `group_linkage` and `rev_grouplinkage` are 0 occurrences; 82 properties.
  > Independently against the live page's own markup: `birth` appears **0 times**; field 19 (Email) is
  > shown only when field 21 = `Email`, and field 21 offers `Email / Phone / Post`, so a postal
  > applicant sends neither an email nor a phone number; fields 14 (Address) and 15 (Name) are
  > required **and are not conditional targets**. **D-003 is genuinely closed, in the code and against
  > reality.**
- **Derivation fallbacks reconcile with the option sets.** `AgeBandMap` has 8 bands and
  `rev_agerange` has 9 values with `9 = Not known`; `PostcodeRegionMap` has 12 regions and
  `rev_locationarea` has 13 with `13 = Not known`. Neither derivation can produce an out-of-range value.
  > **Extended 2026-08-13.** Because there is no date of birth to derive from, `rev_agerange` is now
  > set from the age band the form actually sends, mapped through a new configuration row
  > `AgeRangeLabelMap` (8 labels → options 2–8 and 9). The `AgeBandMap` path is retained as a fallback.
  > Neither route can produce an out-of-range value, and when neither is available the flow writes 9
  > (Not known) rather than guessing. Both new-applicant writes that could throw on an absent value —
  > `rev_dateofbirth` via `formatDateTime(null,…)` and `rev_email` via `trim(null)` — are now
  > null-guarded, and the applicant lookup falls back from email+name to name+postcode.
  >
  > **✅ Re-verified at retest (rev 3), from the expressions themselves and not from a comment.**
  > `rev_dateofbirth` = `if(empty(coalesce(triggerBody()?['date_of_birth'], '')), null,
  > formatDateTime(…))`; `rev_email` = `if(empty(coalesce(triggerBody()?['email'], '')), null,
  > toLower(trim(…)))`. `Compute_age_in_years` returns `-1` when the date of birth is absent, so
  > `formatDateTime` is never reached on that path either. `Derive_age_range` tests the label map
  > **first**, then `Compute_age_in_years < 0 → 9`, then the band match, then `9` — so the
  > `Match_age_bands` query, which matches every band when the age is `-1`, is unreachable in that
  > case. `AgeRangeLabelMap`'s eight labels are byte-identical to the eight `input_26` radio values on
  > the live page, byte-identical between the two settings files, and map only to options 2–8 and 9,
  > all of which exist. **No route can produce an out-of-range age band.** Both `$filter` branches
  > escape every interpolated value, postcode included.
  >
  > ⚠️ **One residual worth naming, and it is not recorded anywhere.** If Alex renames an age-band
  > label on the form, `Map_age_range_label` finds nothing, `Compute_age_in_years` is `-1`, and
  > `rev_agerange` silently becomes 9 (Not known) for **every** subsequent applicant, with no error and
  > no alert. The configuration row's own description anticipates the rename but not the silence.
  > `rev_agerange` feeds reporting and trustee generalisation (FR-027, NFR-013), not the score, so this
  > is **P4** and is folded into D-014's remedy rather than raised separately. Note also that field 26
  > is **optional** on the live form, so "Not known" is already the expected value for most applicants
  > until change-request item **V-02** makes it required.

### 2.3 Automation #2 — Scoring Engine (`REV | Scoring | Calculate & Flag` / `Daily Summary`)

| FR ID | Requirement | Test Case(s) | Result |
|---|---|---|---|
| FR-011 | Circumstance score out of 60 from wellbeing answers | TC-301 — `Calculate_circumstance_score` = `add(likertPoints, Invert_the_feeling_scale_answer)`; reconciled against seeded configuration | **PASS** — arithmetic reconciles exactly: `LikertPointMap` max 5 × 10 answers = 50, `FeelingScaleInversion` max 10 → **60 = `MaxCircumstanceScore`**. ~~Minimum for a fully answered application = (10 × 1) + 0 = **10**~~ → **⚠️ corrected at revision 4: the minimum is now 5**, because "Not sure" is worth 0.5 and is cheaper than "All of the time" at 1. Recomputed, and the shipped Pester suite asserts 5 |
| FR-012 | Invert the reported feeling answer | TC-302 — `Invert_the_feeling_scale_answer` is a map lookup, not arithmetic | **PASS** — `FeelingScaleInversion` = `{"0":10 … "10":0}`, 11 entries; **verified `key + value = 10` for all 11 keys**, i.e. genuinely `10 − answer`. Direction of the scale is configuration, so the board can change it without a solution change |
| FR-013 | Convert each Likert response to its configured point value | TC-303 — `Add_the_configured_points_for_this_answer` reads `LikertPointMap` by response value | **PASS with traceability defect** — ~~`{"1":5,"2":4,"3":3,"4":2,"5":1}`~~ → **⚠️ corrected at revision 4: `{"1":5,"2":4,"3":3,"4":2,"5":1,"6":0.5}`**, one map keyed by numeric option value and shared by both scales. Ordinal position 1 → 5 points, exactly the mapping FR-013 specifies, now proved against 25 real applications. **FR-013's named labels are correct for exactly three of the ten questions** — the build ships frequency labels on the seven SWEMWBS items and agreement labels on the three "last year" items, and the SDD still names only the agreement set. **D-009 — substance closed, SDD text still wrong, A-01 PROPOSED (§4.3)** |
| FR-014 | Set Auto-pass / Borderline / Auto-reject against configured threshold and band | TC-304 — `Derive_status`; TC-305 — misconfigured-band ordering; **TC-318 (new, rev 4) — midpoint rounding** | ~~**PASS**~~ → ❌ **FAIL at revision 4 — D-015.** The ordering is still correct and still verified: `4` at-or-below `KnockoutThreshold`, `3` inside the band, `2` above, **knockout evaluated first**, every boundary a configured value, and since revision 0.8 all three comparisons read the **rounded** score so the outcome cannot disagree with the stored one. **But the rounded number itself is wrong at a midpoint** — `formatNumber(…,'F0')` rounds half to even, so an exact 20.5 becomes 20 and is **Auto-rejected** where the approved round-half-up rule makes it 21 and Borderline. §4.2 · ✅ **PASS again at revision 5 — D-015 closed and verified by execution.** The expression now offsets by `0.25` before formatting; re-executed over all 121 reachable totals under both .NET numeric types with **zero** mismatches against round-half-up. An exact 20.5 now stores **21** and returns **3 Borderline**. The ordering was never the defect and is unchanged; the arithmetic feeding it is now correct. **Live execution of the expression remains unproven** (§8 case 3′) |
| FR-015 | Evaluate finances against the income ceiling as a separate flag | TC-306 — `Derive_income_flag` | **PASS** — `1` within, `2` above, `3` not stated. Reads **only** `rev_incomeband` via `IncomeBandUpperBoundMap`; band 6 "Prefer not to say" → `-1` → flag 3, never a guess. Flag never enters the score expression |
| FR-016 | Exclude disability, health-condition and narrative data from the score | TC-307 — **independent extraction** of every `rev_*` token in the definition with description strings removed | ✅ **PASS — independently verified, not accepted from the comment.** The executable definition references exactly 25 `rev_*` tokens; **not one is a secured or special-category column.** The four special-category names appear once each in *description prose only*. Cross-checked against the full secured set (22 on `rev_application` + 12 on `rev_applicant` = 34): zero intersection |
| FR-017 | Change threshold, band and ceiling without changing automation logic | TC-308 — `Read_configuration` scope | **PASS** — **eight** `rev_setting` rows retrieved by alternate key at run time (`LikertPointMap`, `FeelingScaleInversion`, `KnockoutThreshold`, `BorderlineBandLower`, `BorderlineBandUpper`, `IncomeCeiling`, `IncomeBandUpperBoundMap`, `MaxCircumstanceScore`). Not one threshold is a literal anywhere in the definition |
| FR-018 | Allow the process owner to override, and record that an override was made | TC-309 — `Stop_if_the_process_owner_has_overridden_this_application` | **PASS** — it is the **first** action; `coalesce(rev_statusoverridden, false)` then `Terminate`. There is no path from the guard to a write. Override columns (`rev_statusoverridden`, `rev_overriddenby`, `rev_overriddenon`, `rev_overridereason`) exist and are audited |
| FR-019 | Route Borderline to the process owner before it progresses | TC-310 | **PASS** — `Route_borderline_applications_to_the_process_owner` posts to Teams; `BorderlineAwaitingReview` saved query filters `rev_status eq 3`. Message carries reference, score and band — deliberately **not** the applicant's name |
| FR-020 | Remove Auto-reject from the active working list | TC-311 | **PASS** — verified in the saved queries: `ActiveApplications` filters `statecode eq 0` **and** `rev_status ne 4`; `AutoRejectedApplications` filters `rev_status eq 4`. No data is moved or irreversibly hidden |
| FR-021 | Daily summary of scored / auto-rejected / borderline-awaiting-review | TC-312 — all four queries and the message body | **PASS with a DERIVED addition** — four counts; `Scored` and `Auto-rejected` are windowed, `Borderline` (status 3) and `Under Review, no score` (status 5) are **backlog** counts, which is the correct reading of "awaiting review". The fourth count is a declared DERIVED addition beyond FR-021, justified by NFR-018 |
| FR-022 | Withhold the automated outcome when a scored answer is absent | TC-313 — `Withhold_the_outcome_when_a_scored_answer_is_missing`; TC-314 — zero-vs-null discrimination | ✅ **PASS — and the hardest detail in the release is correct.** The gate fires if any of the ten wellbeing answers is empty **or** the life-satisfaction answer is empty, tested as `empty(coalesce(string(x), ''))`. Because `string(0)` is `"0"` and `string(null)` is `""`, a genuine worst-case answer of **0 scores** while a missing answer **withholds** — the exact defect the Whole Number type choice exists to prevent. The withhold branch writes status 5, a breakdown naming which answers were absent, and **no `rev_circumstancescore` at all** (verified in the action's `item` payload) |

**⚠️ Added at retest, 2026-08-13 — every PASS in §2.3 above is a PASS against the scale the build
assumes, and the live form does not use that scale for three of the ten answers.**

The arithmetic in FR-011, the map lookup in FR-013 and the withhold gate in FR-022 were all verified
correct, and they remain correct. What was never checked until this retest is whether the **inputs**
they are correct about are the inputs the live form actually produces. They are not, for three of the
ten wellbeing answers and for the life-satisfaction answer:

| What the build assumes | What the live form sends | Verified how |
|---|---|---|
| Ten wellbeing answers on one five-point scale; `rev_likertresponse` has values 1–5; `LikertPointMap` has keys `1`–`5` | **Two different scales.** Field 132 is seven statements × **five** columns (the SWEMWBS frequency scale — correct). Field 134 is three "last year" questions × **six** columns, the sixth being **"Not sure"** | Counted the radio inputs in the live page's own HTML: field 132 = 35 (7 × 5), field 134 = **18 (3 × 6)**; read the column header `<th>` labels, the sixth of which is `Not sure` |
| The life-satisfaction answer is a whole number 0–10 | `type=number` `min=0` `max=10` **`step='any'`** — so **7.5 is a valid submission** | Read the `input_133` element attributes |

Those three six-point questions are **`rev_wellbeinganswer8`, `9` and `10`** — confirmed from their
own schema descriptions ("Thinking about the last year, have you been able to go out and do something
you enjoy / enjoy other people's company / have a break when you've needed one?"). All ten are
`picklist` columns bound to `rev_likertresponse`, which has **no sixth option**. This is **D-014**
(§4), and it means FR-011, FR-013 and FR-022 should be read as **PASS (against the assumed scale),
UNSAFE against the live one** until the scale mismatch is resolved. It is not a regression and not a
revision 0.7 defect — it was latent from revision 0.3 — but it is live.

> ### ✅ Re-assessed at the second retest, 2026-08-13 (report revision 4) — the scale mismatch is closed, and one row moves the other way
>
> **The build now assumes what the live form and its own export actually produce, and that is
> established from ground truth rather than from a document.** `docs/Import/Book(Sheet1).csv` was
> re-derived from scratch for this report — cp1252, all 25 rows, exact rational arithmetic — and
> reproduces every published score with **zero deltas**. A brute force over all 14 400 permutation
> pairs of `{5,4,3,2,1}` across the two five-label scales leaves **exactly one** solution, so the
> direction is forced by the data. "Not sure" = **0.5** is pinned uniquely by row 25
> (`9 − (10 − 6) = 5`, across ten answers, no remainder).
>
> | FR | Status at revision 4 | What changed |
> |---|---|---|
> | **FR-011** | ✅ **PASS — and now proved against 25 real applications, not just internally reconciled** | `MaxCircumstanceScore` stays **60** (10 + 10 × 5), correctly not re-derived. **The reachable floor of a fully answered application moves from 10 to 5**, because "Not sure" at 0.5 is cheaper than "All of the time" at 1. `rev_circumstancescore`'s `MinValue 0` accommodates it. The board needs this figure for OQ-001: a knockout threshold at or below 5 was previously unreachable and now is not |
> | **FR-013** | ✅ **PASS — the mapping is now correct for all ten questions, on two scales** | Seven SWEMWBS answers on `rev_likertresponse` (frequency), three "last year" answers on `rev_agreementresponse` (agreement), both `1`–`6` with the same direction, **one shared `LikertPointMap` keyed by numeric option value**. The rebind was verified in the `Entity.xml` `<attribute>` blocks, not by the option-set file merely existing. **D-009's SDD half is still open** — A-01 is PROPOSED |
> | **FR-022** | ✅ **PASS — and the gate is now stronger than the requirement asks** | The withhold gate fires on *absent* **or** *not a key of the configuration map*, on all eleven scored answers, with both maps parsed ahead of it. Membership of the map rather than a hardcoded range, so it stays correct when the board changes configuration (FR-017). The withhold branch still writes status 5, no `rev_circumstancescore`, and names which answers were unusable without naming a value |
> | **FR-014** | ◐ **PASS on ordering, FAIL on the boundary arithmetic — D-015** | The knockout-first ordering is unchanged and still correct, and `Derive_status` now reads the **rounded** score in all three comparisons, so the outcome and the stored score cannot disagree. That half is a real fix, and the pre-fix form was demonstrably harmful (unrounded `20.5` is neither `≤ 20` nor `≥ 21`, so it fell through to Auto-pass). **But the rounded number itself is wrong at a midpoint** — `formatNumber(…,'F0')` rounds half to even, not half up, so `20.5` becomes `20` and is **Auto-rejected** where the approved rule sends it to Borderline review. Every boundary is still a configured value; the defect is in the rounding, not the thresholds. **§4.2** |
>
> **The one row that moved the wrong way is FR-014, and the reason is worth stating plainly.** The
> option-set work, the float accumulation, the widened gate and the bounds are all correct and all
> verified. The rounding is the single action in the chain whose behaviour was reasoned about rather
> than executed, and it is the one that is wrong.

### 2.4 Deferred requirements — FR-023 to FR-055 (33 FRs)

The Dev Summary §7.3 deferral list was **not** taken on trust; absence was verified by searching
`src/solutions/RevitaliseGrantAutomation/` for every named component.

Every deferred FR is listed individually so any ID can be traced without expanding a range.

| FR ID | Requirement (abbreviated) | Automation / deferral basis | Absence verified |
|---|---|---|---|
| FR-023 | Check each new application against QuickBooks grant history | #7 — Phase 4 | ✅ Only the `DEFERRED_call_duplicate_grant_check` `Compose` marker exists; it writes nothing. No QBO connector |
| FR-024 | Flag possible duplicate + prior grant ref/date/amount | #7 | ✅ `rev_duplicateflag` appears **once**, inside that marker's own description. `rev_priorgrantref` → zero hits |
| FR-025 | Record "no prior grants found" when the check completes | #7 | ✅ No `rev_duplicatecheckedon` write path exists |
| FR-026 | Redact free-text narrative to category labels | #5 — blocked on AI Builder credits + DPO sign-off on ADR-002 | ✅ `rev_narrativeredacted` → zero hits. `rev_narrativeraw` **does** exist and is secured — correct, it is the source the Phase 3 flow will read |
| FR-027 | Generalise ages to bands and locations to regions | #5 — **partly built already** | ◐ The *derivation* is built and verified in the intake flow (`Derive_age_range`, `Derive_location_area`, with Not-known fallbacks). The *narrative* generalisation is deferred |
| FR-028 | Retain region, dates, score, preferences, condition info for trustees | #5 | ✅ No trustee-visible surface exists. The columns it will read (`rev_locationarea`, `rev_breakstart/end`, `rev_circumstancescore`, `rev_conditionprofile`) exist and are correctly **not** secured |
| FR-029 | Flag and withhold redactions below the confidence threshold | #5 | ✅ `rev_redactionconfidence`, `rev_redactionreviewrequired` → zero hits. `RedactionConfidenceThreshold` is not among the ten seeded `rev_setting` rows — consistent with deferral |
| FR-030 | Allow the process owner to review, correct and release a flagged redaction | #5 | ✅ `rev_redactionreleased` → zero hits |
| FR-031 | Original unredacted narrative readable only to Admin + service identity | #5 — **the control is built ahead of the flow** | ✅ `rev_narrativeraw` and `rev_otherconditionraw` are `IsSecured=1` and released only by `REV_TrusteeRestricted`. The *enforcement* is in place; the redaction that depends on it is not |
| FR-032 | Per-application anonymised document pack | #5 (derived flow, TAD §5.6) | ✅ No Word Online connector; no pack flow |
| FR-033 | Pack preparation on demand and on a schedule | #5 | ✅ Absent |
| FR-034 | Sortable/filterable trustee summary list | #6 — blocked behind #5 | ✅ No Code App artifact declared in `build.yml`; no Code App source |
| FR-035 | Per-application trustee detail view | #6 | ✅ Absent |
| FR-036 | Withhold identifying information from every trustee view | #6 | ✅ No trustee view exists. `REV Trustee` role → zero hits, so no persona can reach the data at all |
| FR-037 | Trustee records Approve / Defer / Reject with notes | #6 | ✅ `rev_review` table → zero hits |
| FR-038 | Restrict trustee access to the current review round | #6 | ✅ `rev_eligibleforround` → zero hits |
| FR-039 | Print / offline export of trustee views | #6 | ✅ Absent |
| FR-040 | Apply verdicts and initiate acceptance on "Finalise decisions" | #6 | ✅ `REV \| Portal \| Finalise Decisions` absent |
| FR-041 | Pre-populated acceptance document routed via DocuSign | #3 — blocked on DocuSign account, template, UK residency evidence | ✅ No DocuSign connector reference in any flow (only Dataverse, Teams, Outlook) |
| FR-042 | Two signatures in sequence — applicant, then referee/GP | #3 | ✅ Absent. Note the referee columns exist and are secured, awaiting the post-approval form |
| FR-043 | Automatic reminders at 3 and 7 days | #3 | ✅ Absent. `ReminderDays` is not among the ten seeded settings |
| FR-044 | Escalate to the process owner at 14 days unsigned | #3 | ✅ Absent. `EscalationDays` not seeded |
| FR-045 | Set "Acceptance Signed" and link the signed document | #3 | ✅ `rev_grant` table absent — the only `rev_grant*` hits are the **app** `rev_grantadministration` |
| FR-046 | Manual print-sign-scan acceptance route | #3 | ✅ `rev_manualacceptancerecorded` absent (it is a `rev_grant` column) |
| FR-047 | Issue acceptance documents for a batch in one run | #3 | ✅ Absent |
| FR-048 | Automated deletion by outcome and trigger date | Cross-cutting — **partly built** | ◐ **Three of four rules implemented**: 12 months from `rev_decisiondate` (rejected), 6 months from `rev_lastcontactdate` (withdrawn/incomplete), orphaned-applicant sweep, plus the 90-day error-log job. The **6-year paid-grant rule is not implementable** — it needs `rev_grant.rev_finalpaymentdate`. Verified that **no record class is left unprotected**: `rev_applicationstatus` option 11 `Grant Paid` exists but nothing in Phase 1 can set it |
| FR-049 | Delete every linked copy outside the system of record | Cross-cutting — Phase 4 | ✅ Helper flow absent. Cascade to child rows **is** in place and verified in the package (`CascadeDelete = Cascade`) |
| FR-050 | Retain the financial record when the personal record is deleted | Cross-cutting | ✅ Absent — depends on QuickBooks and `rev_payment`, both Phase 2+ |
| FR-051 | Locate and delete all data about a named individual on demand | Cross-cutting | ◐ The **cascade the erasure path depends on is built and verified**; the on-demand locate-and-delete flow is absent |
| FR-052 | Report what cannot be deleted under legal hold | Cross-cutting | ✅ Absent |
| FR-053 | Produce a complete extract for a SAR | Cross-cutting — **no agreed mechanism at all** | ❌ Absent, and unlike the others this is not merely deferred: **no mechanism is designed or agreed** (C-DOM-005, TAD risk A-R22, accepted open item). No SAR SLA exists either (OQ-023), so there is nothing to test against even once one exists |
| FR-054 | Log every retention deletion and erasure action, no personal data in the log | Cross-cutting | ◐ The **evidence-log principle is implemented** for operational failures (`rev_errorlog`, verified to hold no personal-data-capable column). The retention/erasure evidence log itself awaits the helper flow; native bulk-delete system jobs will supply part of it |
| FR-055 | Retain irreversibly anonymised statistics indefinitely | Cross-cutting | ✅ `rev_anonymisedstatistic` → zero hits. Correctly absent: TAD §5.13 assigns its write to `REV \| Portal \| Finalise Decisions`, which is Phase 3 |

**Verdict on the deferral list: accurate.** No component the Dev Summary claims is deferred was found
present, and no component it claims is built was found absent. Five deferred FRs (FR-027, FR-031,
FR-048, FR-051, FR-054) are **partly** served already because their enforcing control was built ahead
of the flow that will use it — which is the right order, and is recorded above rather than being
counted as either done or missing.

**Verdict on the deferral list: accurate.** No component the Dev Summary claims is deferred was found
present, and no component it claims is built was found absent. The FR-055 anonymised-statistic table
and the FR-053 SAR mechanism (TAD risk A-R22, accepted open item) are genuinely unbuilt, as declared.

### 2.5 Non-functional requirement coverage

| NFR | Result | Evidence |
|---|---|---|
| NFR-001 | **PASS (design), live BLOCKED** | 34 secured columns, all released only by `REV_TrusteeRestricted`; `ensure-column-security-profile-members.ps1` adds **group teams**, never users. Live API masking test in §8 |
| NFR-002 | **PASS (vacuously, correctly)** | Neither role holds any `rev_bankaccount` / `rev_payment` privilege; both tables are Phase 2+. Both role files record that Admin must still hold none when they arrive |
| NFR-003 | **N/A Phase 1** | No trustee-facing view exists; `REV Trustee` role not built |
| NFR-004 | ⛔ **BLOCKED — and the WBS 0.3 gap is real** | MFA is tenant configuration. The service account's **unattended** sign-in Conditional Access exception is unconfirmed (SDD OQ-018, TAD A-R13). Interactive sign-in confirmed working 2026-08-10; device-code/public-client is CA-blocked |
| NFR-005 | **PASS (design), live BLOCKED** | Per-environment Entra groups in `ensure-groups.ps1` + settings files |
| NFR-006 | **PASS (design)** | All three connection references bound to service-account connections; no personal login and no connection ID in the artifact |
| NFR-007 | **PASS (design)** | Exactly three connectors referenced, all in the TAD §6.4 business group |
| NFR-008 | ~~❌ FAIL~~ → **PASS (provisioned, owned and asserted), live enforcement BLOCKED — D-001 closed** | Re-verified at retest. The primary control now has all four things D-001 found missing: a named owner (**Wanstor**, tenant administration, with the maker supplying the value), an exact specified value (*"Specific users in my tenant"* + the intake service principal **object** id, distinct from the application id that goes into `rev_IntakeAllowedClientId`), a provisioning script that produces that value (`ensure-intake-client.ps1` — parses clean, check-before-create, CREATED/EXISTS/FAILED, reports credential posture by count only), and an executable smoke test on **both** TST/ACC and PRD (`verify-intake-endpoint-auth.ps1`) whose second check asserts the rejection came from the platform and **not** from the flow's own 401 body — the exact D-001 condition. Both `intake.*` settings keys the script reads exist in both settings files. **The live 401 has still never been observed** (§8), and one residual is untestable by design: leaving *Allowed users* blank silently widens scope to the whole tenant, which the pipeline calls out and instructs reading back, and which no test can detect |
| NFR-009 | ⛔ **BLOCKED** | UK residency is an `APPROVE TENANT` evidence item; no environment to verify |
| NFR-010 | **PASS (design), partly deferred** | Four monthly bulk-delete jobs scripted; 6-year rule deferred with sound justification (§2.4) |
| NFR-011 | ⛔ **BLOCKED** | Platform restore window; no environment |
| NFR-012 | ✅ **PASS — verified** | `rev_errorlog` has no column able to hold personal data (9 attributes, all verified). Daily-summary queries select `rev_applicationid` **only** — enforced by the query, not the message. Failure-alert callers pass `submission_id` or a reference |
| NFR-013 | **PASS (design)** | `rev_agerange` / `rev_locationarea` derived at intake; ethnic group deliberately not collected |
| NFR-014 | **PASS with count defect (D-007)** | 118 of 120 attributes across the four tables carry `IsAuditEnabled=1`; the two exclusions are the calculated columns `rev_fullname` and `rev_costs`, correctly excluded because Dataverse audits stored values. `ensure-auditing.ps1` sets `auditretentionperiodv2 = 2192` days (6 years) |
| NFR-015 | **N/A Phase 1** | No trustee app |
| NFR-016 | **PASS (design)** | Evidence log holds reference/type/date/rule only |
| NFR-017 | **N/A Phase 1** | Redaction is Automation #5 |
| NFR-018 | ✅ **PASS — verified** | Both human-review paths are *pushed*, not merely filed: FR-019 Borderline → Teams, FR-022 incomplete → Teams. Fail-closed: a missing setting row leaves the application unscored rather than scored wrongly |
| NFR-019 | ✅ **PASS — verified, re-counted at retest** | **Eleven** `rev_setting` rows in both settings files (`AgeRangeLabelMap` added for D-003), and the new row is byte-identical between them, which is correct — it is a reference map, not a board criterion. Eight read at run time by the scoring flow; **three** now read by the intake flow (`AgeBandMap`, `PostcodeRegionMap`, `AgeRangeLabelMap`). `no-hardcoded-thresholds` gate passes (see D-013 for the gate's narrowness). ⚠️ Note the intake now fails closed on a missing `AgeRangeLabelMap` row, consistent with the two rows it already depended on — correct behaviour, but one more seeded row the intake cannot run without |
| NFR-020 | **PASS (spec)** | Operationalised as a measurable threshold: Flesch-Kincaid Grade ≤ 6.0 / Reading Ease ≥ 60 per page, **including error messages**. Stronger than the SDD asked for. But the applicant read-through is simultaneously required by the sign-off checklist and left undecided in §10.3 |
| NFR-021 | **PASS (design)** | ~200/yr is far inside platform limits; the constraint is licensing |
| NFR-022 | ⚪ **UNTESTABLE — no threshold exists** | SDD OQ-020 open. Recorded, not invented |
| NFR-023 | ⚪ **UNTESTABLE — no target exists** | SDD OQ-021 open |
| NFR-024 | ◐ **PARTIAL — see D-004, still PARTIAL after the 2026-08-13 cycle** | Standard derived as WCAG 2.1 AA baseline + 2.2 AA for the form (ADR-020, still unconfirmed — SDD OQ-022). **Updated basis:** the live form has now been inspected directly. **Two confirmed failures** — 1.3.5 Identify Input Purpose (no valid `autocomplete` token on any of 251 inputs) and 3.3.7 Redundant entry (two confirm-email boxes). **Four confirmed passes** — 3.1.1 (`lang="en-GB"`), 2.4.1 (skip link), 1.3.1/3.3.2 label association (132 `label for=`), 3.3.8 (no CAPTCHA, honeypot only). **Everything else is unaudited**: contrast, keyboard operation, focus order and visibility, zoom and reflow, screen-reader behaviour, target size. No conformance claim is made in either direction beyond those six rows. **Spec OPEN-26** raises the audit itself |
| NFR-025 | ⚪ **UNTESTABLE — no SLA exists** | SDD OQ-023 open; and no SAR mechanism exists to test (C-DOM-005, A-R22) |

---

## 3. Failed Tests

| Test ID | Layer | Description | Expected | Actual | Severity |
|---|---|---|---|---|---|
| TC-103 | E2E (spec) | FR-003 conditional reveal — financial detail gated on income band | Financial detail questions shown only after an income band is selected | Gate deliberately removed; the eight financial questions are shown together and asked *before* the band. No SDD change request records the deviation, and a contradictory revision-0.1 instruction survives in the same document | **P2** |
| TC-401 | Security | Platform-level authentication on the one public endpoint (NFR-008, C-TECH-006) | A control that rejects an unauthenticated caller, provisioned by a named owner and asserted by a test | Not in the solution source (`operationOptions` absent), not in any provisioning script, not a TAD §12 item, not a `post_deploy` step, and not asserted by any smoke test. Residual protection is a non-secret client-ID header | ~~**P2**~~ · ✅ **RESOLVED 2026-08-13 (retest, rev 3)** — the control now has a named owner, an exact value, a provisioning script, three TAD §12 rows and an executable smoke test on both environments, all re-verified from source. **The live 401 is still unobserved** and moves to §8 as the highest-priority deferred case |
| TC-501 | Accessibility | WCAG 2.1 AA acceptance is complete for the applicant-facing form | Every 2.1 AA criterion evidenced at sign-off | Sign-off is scoped to spec §10.1/§10.2 only. **1.3.5 Identify Input Purpose (`autocomplete`) is absent entirely**, plus 1.1.1, 1.3.4, 1.4.12, 1.4.13, 2.4.1, 2.5.3, 3.1.2, 4.1.2 | **P2** · ◐ **PARTIAL 2026-08-13** — 1.3.5 confirmed FAIL on the live form (0 valid `autocomplete` tokens across 251 inputs), 3.3.7 confirmed FAIL (two confirm-email boxes), 2.4.1 and 3.1.2 confirmed PASS; the remaining criteria need axe-core + a manual pass (spec OPEN-26) |
| TC-207 | Integration (contract) | The intake payload contract is unambiguous to the external integrator | One authoritative required-field list | Two contradictory lists: 6 fields in the banner vs 11 further "never null" scored answers mandated by §11.1 rule 3 and the sign-off checklist. True minimum is 17 | **P2** · ✅ **RESOLVED 2026-08-13** — and the six-field list itself was wrong against the live form. Required is now the four fields the live form always collects; the eleven scored answers are accepted-not-required by design |
| TC-901 | Compliance | C-TECH-014 (HARD) unit-test coverage meets the defined threshold | A coverage report against a defined threshold | No threshold is defined anywhere (`coding-standards.md` sets none) and **no automated test of any kind exists** in the repository | ~~**P2**~~ · ✅ **RESOLVED 2026-08-13 (retest, rev 3)** — threshold defined (`coding-standards.md` § Test Coverage: 80% line coverage over `provisioning/{common,entra,dataverse}`, build-failing), step wired into `build.yml`, suite **re-run: 537 passed / 0 failed / 1 skipped at 92.60%**, and **the gate was proven to bite** — re-run at `-CoverageThreshold 99` it exits **1** |
| TC-402 | Security | `secret-scan` build gate covers the delivered source | Gate scans the solution source, scripts and configs | `gitleaks detect --source .` scans **git history**; all 47 files under `src/solutions/` are untracked, so the recorded build's scan covered none of them. Closed by re-running with `--no-git` (clean, 1.84 MB) | **P3** · ⚠️ **STILL OPEN at retest** — `manifest.json` records the executed step as `secret-scan (--no-git)`, but `build.yml` line 77 still has no `--no-git`. Re-ran `--no-git` manually: clean, **2.89 MB** (larger because `src/tests/` now exists). The pass is real; **it is not reproducible from the config** · 🔧 **FIX DELIVERED rev 0.8** — the config now reads `gitleaks detect --source . --no-git --no-banner --redact --exit-code 1`. Executed **as the config specifies it**: ≈3.06 MB scanned, **no leaks found, exit 0** (the byte figure drifts by a few KB between runs because these documents are themselves inside the scan scope; the load-bearing part is *no leaks* and *exit 0*). The pass is now reproducible from the repository |
| TC-316 | Unit | Every value the live form can send for a scored answer can be stored and mapped | The eleven scored answers are storable in their columns and every value has a `LikertPointMap` / `FeelingScaleInversion` key | Live-form field 134 offers **six** columns for wellbeing answers 8–10, the sixth being **"Not sure"**; `rev_likertresponse` has five options and `LikertPointMap` five keys. A "Not sure" answer cannot be stored and cannot be mapped | **P2** — D-014 · 🔧 **FIX DELIVERED rev 0.8** — value 6 "Not sure" exists on both option sets, `LikertPointMap` has key `"6":0.5`, and a test asserts the map covers **both** option sets' value sets. Verified present inside both packed zips |
| TC-317 | Unit | The FR-022 withhold gate covers unmappable answers as well as absent ones | A value the score cannot use routes to a human, as a missing one does | `Find_missing_wellbeing_answers` filters on `empty(coalesce(string(response), ''))` — **emptiness only**. A present-but-unmappable value passes the gate and reaches `int(string(map?[key]))`, where a null lookup makes `int('')` throw | **P2** — D-014 · 🔧 **FIX DELIVERED rev 0.8** — the filter is now `@or(empty(response), empty(map?[response]))`, and a **third** gate condition does the same for the life-satisfaction answer against `FeelingScaleInversion`. Both configuration maps are parsed ahead of the gate; the scoring chain is asserted to remain downstream of it |
| TC-315 | Unit | Dev Summary §10's audit-coverage count is accurate | "122 IsAuditEnabled columns (88 / 18 / 10 / 6)" | Actual: 118 audit-enabled of 120 attributes (88 / 18 / **9** / **5**). The figure counts attributes, not audit-enabled attributes, and two table counts are each one too high | **P3** |

**Added at the second retest, 2026-08-13 (report revision 4).** TC-316, TC-317 and TC-402 above are
now **✅ RESOLVED and independently verified** — the annotations on those rows were written by
development-agent; the verification behind them is recorded in the revision 4 block at the head of
this report. Three new failures were found:

| Test ID | Layer | Description | Expected | Actual | Severity |
|---|---|---|---|---|---|
| **TC-318** | Unit | `Round_the_circumstance_score` implements the rounding rule the reviewer approved | Round **half up** — `20.5 → 21`, `30.5 → 31`, `0.5 → 1` — as stated in the Dev Summary, in `LikertPointMap`'s own description, and in the trustee-facing `rev_scorebreakdown` text | The expression is `@int(formatNumber(outputs('Calculate_circumstance_score'), 'F0'))`. `formatNumber` is .NET numeric formatting, and .NET rounds a midpoint **to even**. Executed on .NET 10.0.10: `0.5 → 0`, `2.5 → 2`, `20.5 → 20`, `30.5 → 30`, `35.5 → 36`. It coincides with half-up only when the integer part is odd. **With TST/ACC values in force (knockout ≤ 20, band 21–30) an exact 20.5 is stored as 20 and Auto-rejected, where the approved rule stores 21 and routes to Borderline human review** | **P2** — D-015 |
| **TC-319** | Unit | The rounding mode is asserted somewhere, so it cannot silently drift | A test that pins the midpoint behaviour | **Nothing asserts it, and nothing in the suite can.** 560 Pester assertions cover the map contents, the 0.5 derivation, the option-set bindings, and the fact that `Derive_status` *reads* `Round_the_circumstance_score` — none of them what that action *computes*. The Dev Summary makes no claim to have executed it either; it states the mode and, separately, the mechanism, with no link between them. The 25-row reconstruction cannot cover it, because the document itself notes no ground-truth row produces a fractional total | **P2** — D-015 (same defect, the reason it survived) |
| **TC-320** | Unit | Dev Summary §9 (Test Guidance) describes the build under test | §9's invariants match what shipped | **§9 has no revision-0.8 content at all**, and three of its invariant rows now describe the pre-0.8 build: `minimum reachable score is 10` (actually 5 — the shipped suite asserts 5 and says so), the FR-022 invariant still described as emptiness-only, and the `LikertPointMap` invariant still scoped to `rev_likertresponse` alone with no mention of `rev_agreementresponse` or value 6. §9.3's scoring table has **no case at all** for a fractional total, a midpoint, or `Derive_status` reading the rounded value — i.e. no guidance for the one change the document itself flags as most needing attention. Also stale elsewhere in the same document: "35 root components" in three places (now 36), "fifteen global option sets" (now 16), and `LikertPointMap`'s "Value unchanged in revision 0.3" (key `"6"` was added) | **P3** — D-017 |

**Resolved at the THIRD retest, 2026-08-13 (report revision 5).** **TC-318, TC-319 and TC-320 are all
✅ RESOLVED and independently verified** — see §4.000 and the verification annotation at the end of
§4.2. TC-318 was re-tested by **executing** the formatter over all 121 reachable totals under both .NET
numeric types (0 mismatches, where the pre-fix expression fails 30). TC-319 is closed by 17 new
assertions that were **mutation-tested at this gate**, not accepted on report — 7 assertion groups fail
against the pre-fix expression, and the ones that pass are exactly the odd-whole-part cases that hid
the defect originally. TC-320 is closed by a rewritten §9.

**No new failing test was found at this retest — the first time that has been true for this feature.**
The rows above are left with their original wording as the record of what was found at revision 4.

---

## 4. Defects Raised

### 4.000 Status as at the THIRD retest, 2026-08-13 (report revision 5) — authoritative

**This block supersedes §4.00 and everything below it for current status.** Every status here was set
by re-derivation or re-execution against the revision 0.9 source and the stored build #4 zips. Where a
status is unchanged it is because revision 0.9 did not touch it — not because it was not looked at.

| Defect | Severity | Status now | Basis |
|---|---|---|---|
| **D-015** | P2 | ✅ **RESOLVED — verified by execution** | The expression is `@int(formatNumber(add(outputs('Calculate_circumstance_score'), 0.25), 'F0'))` in the source and inside **both** stored zips. **Re-executed independently: 0 mismatches against round-half-up across all 121 reachable totals, under both `double` and `decimal`**; the pre-fix form fails 30 of them under `double`. `20.5 → 21`, `30.5 → 31`, `37.5 → 38`; unfixed gives `20`, `30`, `38`. The offset is exact in binary floating point, and `0.0` / `0.5` / `0.75` were each confirmed to produce wrong answers where `0.25` produces none. **17 new assertions exist, are substantive, and were mutation-tested here rather than taken on report** — driven against the pre-0.9 expression, 7 assertion groups fail and the survivors are exactly the odd-whole-part cases. `Get-RoundingOffset` parses the offset out of the shipped expression and **throws** on a reimplementation, so the suite cannot pass vacuously. `Derive_status` and `rev_circumstancescore` both still read the rounded output, and `formatNumber` appears exactly once. **The fix removes the runtime dependency rather than betting on it, which is materially better than the minimum required** |
| **D-016a** *(was the register's D-016)* | P4 | ⚠️ **OPEN — renamed, not closed** | **The live-form contradiction is unresolved.** Revision 3 counted field 132 (the seven SWEMWBS statements) as 7 × 5 = 35 radio inputs — **no "Not sure" column** — while CSV row 25 answers "Not sure" to **all ten** questions and is a real scored application. One observation is stale. **Needs the live form, not a developer** — §8 case 8, and it belongs to the D-008 mapping work. Revision 0.9 states plainly that it did *not* close this, which is correct and is credited. Renamed **D-016a** because two different items were travelling under one label |
| **D-016b** *(was the "disjoint" wording)* | P4 | ✅ **RESOLVED — verified** | `Other/Solution.xml` lines 87–93 now state the two label sets "share exactly ONE value and are otherwise disjoint", **and explain that the shared value is the argument *for* one shared `LikertPointMap`** rather than against it. Both option sets confirmed to carry six labels with `Not sure` shared. The two option-set XML descriptions and the Pester suite were already accurate and are unchanged. **`manifest.json` never contained the word** — revision 4 attributed it there in error, and revision 0.9 is right to say so |
| **D-017** | P3 | ✅ **RESOLVED — verified** | §9 Test Guidance now describes the shipped build: floor **5** not 10, the FR-022 gate as absent-**or**-unmappable on all eleven answers, `LikertPointMap` scoped to **both** option sets including value 6, and §9.3 carrying the fractional/midpoint cases led by `20.5 → 21 → Borderline`. Stale counts corrected: 15 → **16** option sets, ten → **eleven** `rev_setting` rows, six → **seven** policy rows, 20 → **22** scripts. §9.6 gained a standing rule that a scoring change *includes* updating this list. **The three "35 root components" instances were deliberately left, and that judgement is correct** — all three are historical evidence blocks where 35 was true at the time; rewriting them would falsify the record rather than correct it |
| **D-002** | P2 | ⚠️ **OPEN — unchanged, and now one of only two** | Not touched by revision 0.9. The live form gates the financial questions on **benefit status**, not income band; whether that is intended is Emily's decision (**M-04**, spec **OPEN-10**). FR-003 still not met as written. **Open and unmoved since report revision 1** |
| **D-004** | P2 | ◐ **PARTIAL — OPEN, unchanged, and not softened** | Revision 0.9 touched no accessibility surface. **1.3.5 stands as a confirmed FAIL** (251 `<input>` elements, five `autocomplete` attributes, none a valid purpose token) and **3.3.7 stands as a confirmed FAIL** (two confirm-email pairs). **The other nine criteria have still been assessed by nothing.** The audit has still never been run and is still **not blocked on anything** — the form is live and auditable today. **This is now the highest-human-consequence open item in the release by a clear margin, and the fourth consecutive report to say so** |
| **D-001, D-003, D-005, D-006, D-014** | P2 / P3 | ✅ **RESOLVED** | All closed and verified at earlier revisions. Re-confirmed not regressed by revision 0.9: the intake `required` array is still exactly the four fields with 82 properties and **zero** unbounded scored answers, `gitleaks` still runs clean **from the config** (3.19 MB, exit 0), the coverage gate still runs, and the suite grew 560 → **577** with 0 failures |
| **D-007** | P3 | ⚠️ **OPEN — unchanged, re-verified this pass** | The "122 `IsAuditEnabled` columns" figure still appears in **four** places in the Dev Summary, which separately records in two more places that D-007 stands uncorrected. Correct figure remains **118 audit-enabled of 120 attributes**. Coverage itself is complete and correct; the false-assurance checklist item is what remains |
| **D-008** | P3 | ⚠️ **OPEN — before-go-live** | Unchanged. Three mismatched option sets remain — applicant type, break type, exceptional circumstance — plus helper relationship and the ten-vs-eight condition profile. **M-01, M-05, M-07.** **D-016a belongs to this work** |
| **D-009** | P3 | 🔧 **SUBSTANCE CLOSED — formal closure still needs plan-agent** | Unchanged. **SDD FR-013's approved text is still wrong**, and Amendment **A-01 is PROPOSED, not approved** — see §4.3. Revision 0.9 correctly did not touch the SDD. **Approving this test report does not approve A-01** |
| **D-010** | P3 | ⛔ **SUPERSEDED** | Unchanged |
| **D-011** | P4 | ⚠️ **OPEN** | Re-confirmed in `prd-settings.json`: `{{PENDING_OQ_002}}` on **both** band bounds. The deliberate `-Skip` carrying the defect id is still the right pattern, and is the 1 skipped test in the suite |
| **D-012, D-013** | P4 | ⚠️ **OPEN** | Both gates unchanged and still narrow as described |
| **D-018** | **P4 — NEW (re-homed, not newly found)** | ⚠️ **OPEN** | **The three trustee-facing breakdown P4s that revision 4 folded into D-015's remedy, given their own id so they do not vanish with D-015's closure.** (a) `Record_this_answer_in_the_breakdown` now appends `' (Not sure)'` for value 6 but **values 1–5 still emit a bare option number**, so a trustee cannot tell *"None of the time"* from *"Strongly Disagree"* — the distinction that justified splitting the option sets in the first place. (b) `string(variables('likertPoints'))` on a `float` may render a whole subtotal as `35` or `35.0`. (c) `equals(Calculate_circumstance_score, Round_the_circumstance_score)` is a raw `float`-versus-`int` comparison that decides whether the breakdown claims rounding was applied — **if Logic Apps does not coerce, a whole total is told it was rounded**, which is a wrong statement in the evidence artefact. (b) and (c) are only settleable live (§8 case 3′) |

**Open P2 count: two — D-002 and D-004.** Down from three, and the composition has changed in a way
the count alone conceals: **for the first time in this feature's history, no open P2 can be closed by
writing code.** D-002 needs Emily's decision. D-004 needs an audit nobody has commissioned. Every P2
that was a developer's to fix has been fixed and independently verified.

### 4.00 Status as at the SECOND retest, 2026-08-13 (report revision 4) — superseded by §4.000 above

**This block supersedes §4.0 and everything below it for current status.** Every status here was set
by re-derivation or re-execution. Where a status is unchanged from revision 3 it is because nothing in
revision 0.8 touched it — not because it was not looked at.

| Defect | Severity | Status now | Basis |
|---|---|---|---|
| **D-014** | P2 | ✅ **RESOLVED — verified** | Every limb of the fix was checked independently rather than accepted. The formula re-derived from `Book(Sheet1).csv` reproduces all **25 / 25** rows exactly and the point mapping is the **unique** survivor of 14 400 candidate permutations; "Not sure" = 0.5 is pinned uniquely by row 25. `rev_agreementresponse` exists with the six intended values; `rev_likertresponse` has value 6; **`rev_wellbeinganswer8/9/10`'s `<attribute>` blocks genuinely reference the new option set** and `1`–`7` still reference the old one. `LikertPointMap` is `{"1":5,…,"6":0.5}`, byte-identical in both settings files, looked up by numeric option value with **no second map anywhere** — one map, as claimed. The cast is `float(...)` and `likertPoints` initialises as `"type": "float"`; both were needed and both are present. The withhold gate covers *unmappable* as well as *absent* on all eleven answers, with both maps parsed ahead of it and the scoring chain strictly downstream. All ten `wellbeing_answer_*` bounded `1`–`6` and `feeling_scale_answer` `0`–`10`, with `required` still four fields and still 82 properties. Verified **inside both packed zips**, whose hashes match `manifest.json`. **`MaxCircumstanceScore` correctly stays 60; the floor correctly moves 10 → 5.** ⚠️ **The fix introduced D-015** (below) — that is a new defect, not a reason to hold D-014 open |
| **D-006** | P3 | ✅ **RESOLVED — verified** | `config/revitalise-grant-automation-build.yml` line **91** reads `gitleaks detect --source . --no-git --no-banner --redact --exit-code 1`. The flag is genuinely in the config this time, with a fifteen-line comment explaining why it is load-bearing. **Run exactly as the config specifies it: 3.07 MB scanned, no leaks found, exit 0.** The PASS for C-TECH-001 no longer depends on a human remembering a flag |
| **D-015** | **P2 — NEW** | ⚠️ **OPEN** | **The rounding function does not implement the rounding rule the reviewer approved.** Full entry in §4.2. Found by executing `ToString("F0")` rather than reading the expression |
| **D-016** | P4 — NEW | ⚠️ **OPEN** | **The ground truth contradicts this report's own revision-3 count of the live form.** Revision 3 counted field 132 as 7 × 5 = 35 radio inputs — no "Not sure" column on the seven SWEMWBS statements. CSV row 25 answers "Not sure" to **all ten** questions and is a real scored application. One observation is stale. Revision 0.8's choice to add value 6 to **both** option sets is correct either way, so nothing is unsafe — but this sits under the M-02 / D-008 mapping work and must not be carried silently |
| **D-017** | P3 — NEW | ⚠️ **OPEN** | **Dev Summary §9 (Test Guidance) was not updated for revision 0.8 and three of its invariants now describe the pre-0.8 build.** §9 is the section `agents/test-agent.md` directs this agent to load on activation. A future tester following it literally would assert a minimum reachable score of **10** against a build whose floor is **5**, and would test the FR-022 gate as emptiness-only. The shipped Pester suite is correct — it asserts 5 and explains the change; it is the guidance document that is behind. See TC-320 for the full list, including "35 root components" in three places and "fifteen global option sets" |
| **D-002** | P2 | ⚠️ **OPEN — unchanged** | Not touched by revision 0.8, which says so itself. The live form gates the financial questions on **benefit status**, not income band; whether that is intended is Emily's decision (**M-04**, spec **OPEN-10**). FR-003 still not met as written |
| **D-004** | P2 | ◐ **PARTIAL — OPEN, unchanged, and not softened** | Revision 0.8 touched no accessibility surface. **1.3.5 stands as a confirmed FAIL** (251 `<input>` elements, five `autocomplete` attributes, none a valid purpose token) and **3.3.7 stands as a confirmed FAIL** (two confirm-email pairs). **The other nine criteria have still been assessed by nothing.** The audit has still never been run, and it is still **not blocked on anything** — the form is live. This remains the highest-human-consequence finding in the release, and three closed defects elsewhere do not touch it |
| **D-001, D-003, D-005** | P2 | ✅ **RESOLVED** | Closed and verified at revision 3. Nothing in revision 0.8 regressed them: the intake `required` array is still exactly the four fields, still 82 properties, the coverage gate still runs and still bites, and the suite grew from 537 to 560 with 0 failures |
| **D-007** | P3 | ⚠️ **OPEN — unchanged** | The "122" figure still appears in the Dev Summary. Re-confirmed at revision 3 as 118 audit-enabled of 120 attributes. Coverage itself is complete and correct; the false-assurance checklist item is what remains. Revision 0.8 kept `IsAuditEnabled=1` on the three rebound attributes |
| **D-008** | P3 | ⚠️ **OPEN — before-go-live** | Two of the five mismatched option sets are now settled by ground truth (the two wellbeing scales). The other three — applicant type, break type, exceptional circumstance — plus helper relationship and the ten-vs-eight condition profile are untouched, as revision 0.8 states. **M-01, M-05, M-07.** **D-016 belongs to this work** |
| **D-009** | P3 | 🔧 **SUBSTANCE CLOSED — formal closure still needs plan-agent** | The substance is now settled by evidence and shipped: three questions on an agreement scale, seven on a frequency scale, a sixth response worth 0.5. **SDD FR-013's approved text is still wrong**, and Amendment **A-01 is PROPOSED, not approved** — see §4.3 on why that status is right and what must happen to it |
| **D-010** | P3 | ⛔ **SUPERSEDED** | Unchanged |
| **D-011** | P4 | ⚠️ **OPEN** | Re-confirmed in `prd-settings.json`: `{{PENDING_OQ_002}}` on **both** band bounds. The deliberate `-Skip` carrying the defect id is still the right pattern |
| **D-012, D-013** | P4 | ⚠️ **OPEN** | Both gates unchanged and still narrow as described |

**Open P2 count: three — D-002, D-004, D-015.** D-014 closed properly; D-015 took its place. The
difference between them matters: **D-014 was a mismatch between the build and the world, and closing
it required evidence nobody had. D-015 is a mismatch between the build and its own approved decision,
and closing it requires one expression.** It is the smallest open P2 in the history of this feature
and the fastest to fix.

### 4.0 Status as at the retest, 2026-08-13 (report revision 3) — superseded by §4.00 above

This block superseded the two below it for status **as at revision 3**; §4.00 now supersedes it.
**Every "RESOLVED" here was confirmed by re-derivation or re-execution, not by reading the Dev
Summary.**

| Defect | Severity | Status now | Basis |
|---|---|---|---|
| **D-001** | P2 | ✅ **RESOLVED** | All four missing pieces exist and were verified from source: named owner (Wanstor), exact specified value, `ensure-intake-client.ps1` (parses clean, check-before-create, three-state status, credential posture by count only), `verify-intake-endpoint-auth.ps1` wired as a smoke test on **both** TST/ACC and PRD, plus a named manual `post_deploy` step ordered **before** flow switch-on. The smoke test's discriminator (`"error"\s*:\s*"unauthorised"`) matches the flow's actual 401 body, and a test asserts that coupling. **C-TECH-006 moves FAIL → PASS.** The live 401 remains unobserved (§8) and one residual is undetectable by any test: a blank *Allowed users* field silently reverts to whole-tenant scope — the pipeline names it and instructs reading it back |
| **D-005** | P2 | ✅ **RESOLVED** | Threshold defined and reasoned; **537 tests pass, 0 fail, 1 deliberate skip**; coverage **92.60%** over 1283 commands; gate proven to fail below threshold (exit 1 at 99%). A regression suite now exists where none did. **C-TECH-014 moves FAIL → PASS.** ⚠️ The threshold is a **Tech Lead decision taken by development-agent in the absence of a Tech Lead** and is flagged as such in `coding-standards.md`. Confirm or override it — do not treat it as settled by having been written down |
| **D-003** | P2 | ✅ **RESOLVED** | Verified in the JSON *and* against the live page's own markup. See §2.2 |
| **D-004** | P2 | ◐ **PARTIAL — still open, and correctly not closed** | Re-verified independently: **251 `<input>` elements, five `autocomplete` attributes, none a valid purpose token** (one honeypot `new-password`, four `off`) → **1.3.5 FAIL**. Two confirm-email pairs → **3.3.7 FAIL**. Four criteria confirmed PASS. **The other nine have still not been assessed by anything.** The specification half is addressed; the audit half has not started (spec **OPEN-26**). This remains **the highest-human-consequence finding in the release** and the good news elsewhere does not touch it |
| **D-002** | P2 | ⚠️ **OPEN** | Not fixable by development-agent. The live form gates the financial questions on **benefit status**, not income band; whether that is intended is Emily's decision (mapping gap **M-04**, spec **OPEN-10**). FR-003 is still not met as written. Needs an SDD amendment or a restored gate |
| **D-014** | **P2** | 🔧 **FIX DELIVERED — dev-summary revision 0.8, 2026-08-13. Awaiting test-agent verification at retest** | *Raised at this retest as:* the live form can send three answers the schema cannot store and the score cannot map, and the fail-closed design does not cover it. Full entry in §4.1. **See the development-agent annotation appended to §4.1** — the remedy is **not** the interim reject-and-flag guard this report recommended, because ground-truth data proved "Not sure" is a **valid answer worth 0.5 points**, not malformed input. Both halves of the report's own recommendation were nevertheless implemented: schema bounds AND the widened FR-022 gate |
| **D-006** | P3 | 🔧 **FIX DELIVERED — dev-summary revision 0.8, 2026-08-13. Awaiting test-agent verification at retest** | *Raised as:* `manifest.json` says `secret-scan (--no-git)`; `build.yml` line 77 still has no `--no-git`. The scan is clean when re-run manually (2.89 MB), so **C-TECH-001 genuinely passes** — but not because of the config. **`--no-git` is now in the config.** Evidence, run as the config now specifies it: `gitleaks detect --source . --no-git --no-banner --redact --exit-code 1` → ≈3.06 MB scanned, **no leaks found, exit 0** (the byte figure drifts by a few KB between runs because these documents are themselves inside the scan scope; the load-bearing part is *no leaks* and *exit 0*). The PASS is now reproducible from the repository rather than from a human remembering to add a flag |
| **D-007** | P3 | ⚠️ **OPEN, now annotated** | Re-counted at retest from the entity XML: **118 audit-enabled of 120 attributes** — `rev_application` 87 of 88, `rev_applicant` 17 of 18, `rev_errorlog` 9 of 9, `rev_setting` 5 of 5 — the two exclusions being the calculated `rev_fullname` (on `rev_applicant`) and `rev_costs` (on `rev_application`), correctly excluded because Dataverse audits stored values. All four tables also carry entity-level `IsAuditEnabled=1` and `IsRetrieveAuditEnabled=1`, re-confirmed. The Dev Summary's "122" figure **still appears in three places**, though §10.0 now carries an explicit correction naming 118/120. Coverage itself is complete and correct; the false-assurance checklist item is what remains |
| **D-008** | P3 | ⚠️ **OPEN — before-go-live** | Basis inverted: the option lists exist now (OPEN-20 closes) but do not match what the form sends. **M-01, M-05, M-07.** Safe to change before any application exists, unsafe after |
| **D-009** | P3 | 🔧 **SUBSTANCE ADDRESSED — dev-summary revision 0.8. Formal closure needs plan-agent** | Confirmed unchanged: SDD FR-013 still names "Strongly Disagree = 5 … Strongly Agree = 1" and its acceptance criterion still says "Given a Likert answer of *Strongly Disagree*", while the build ships the frequency labels. **D-014 makes this worse than a documentation defect** — the live form uses agree/disagree wording for three questions and frequency wording for seven, so the stale SDD text is now half-true in a way that hides the mismatch. **This report's diagnosis was right and better than it knew:** ground truth (`docs/Import/Book(Sheet1).csv`) confirms the agree/disagree labels are *correct for exactly the three "last year" questions* and wrong for the seven SWEMWBS items, and that a sixth response ("Not sure") was missing from both. Revision 0.8 split the option sets accordingly and raised **SDD Amendment A-01** carrying replacement FR-013 wording and a replacement acceptance criterion. **A-01 is PROPOSED, not approved** — the SDD is an APPROVED plan-agent artefact and development-agent cannot re-issue it, so D-009 cannot be closed by this cycle. Route A-01 to plan-agent |
| **D-010** | P3 | ⛔ **SUPERSEDED** | Unchanged |
| **D-011** | P4 | ⚠️ **OPEN** | Re-confirmed: `prd-settings.json` carries `{{PENDING_OQ_002}}` on **both** `BorderlineBandLower` and `BorderlineBandUpper`. A written test is deliberately `-Skip`ped with the defect id in the skip comment, which is a good pattern — an open P4 is now visible mechanically |
| **D-012** | P4 | ⚠️ **OPEN** | Re-confirmed: the FR-016 gate still requires the `body/` access form |
| **D-013** | P4 | ⚠️ **OPEN** | Re-confirmed: the gate still matches only JSON key/value pairs |

**Open P2 count: three — D-002, D-004, D-014.** None is fixable by development-agent alone: D-002
needs Emily's decision, D-004 needs an audit nobody has run, and D-014 needs a schema-or-form
decision that revision 0.7 correctly refused to take on its own judgement.

> 🔧 **development-agent, 2026-08-13 (rev 0.8): the judgement on D-014 was that this last clause
> was right to be cautious and is now overtaken by evidence, not by opinion.** D-014 did need a
> decision about the scale — and `docs/Import/Book(Sheet1).csv` supplies it, from the charity's own
> hand-scored applications, rather than requiring anyone to choose. Both limbs are settled: the
> sixth option exists **and** the three "last year" questions keep an agreement scale, because that
> is what the live form and its export both show. **Open P2 count pending retest: two — D-002 and
> D-004**, both still needing Emily or an audit. D-014 is **fix delivered, awaiting verification**.

### 4.1 D-014 (NEW, P2) — the live form can send answers the schema cannot store and the score cannot map

**This is the finding this retest exists to have caught.** The scoring engine was verified correct in
revision 1 of this report and is still correct. What was never checked is whether its inputs are the
inputs the live form produces.

| | |
|---|---|
| **Verified fact 1** | Live-form field 134 — the three "Thinking about the last year…" questions — is a **3 × 6** Likert matrix. Counted directly: 18 radio inputs, and the sixth column header reads **`Not sure`**. Field 132, the seven SWEMWBS statements, is 7 × 5 = 35 inputs on the correct five-point frequency scale |
| **Verified fact 2** | Those three questions are **`rev_wellbeinganswer8`, `9`, `10`** — confirmed from their own `<Description>` text. All ten wellbeing columns are `picklist` bound to `rev_likertresponse`, which has **exactly five options, 1–5, and no "Not sure"** |
| **Verified fact 3** | `LikertPointMap` has keys `1`–`5` only. `Add_the_configured_points_for_this_answer` = `@int(string(outputs('Parse_likert_point_map')?[string(item()?['response'])]))` |
| **Verified fact 4** | The FR-022 withhold gate is `Find_missing_wellbeing_answers` filtering on `@empty(coalesce(string(item()?['response']), ''))` — **emptiness only** |
| **Verified fact 5** | The intake trigger schema declares `wellbeing_answer_8/9/10` and `feeling_scale_answer` as bare `integer` with **no `minimum` or `maximum`** — so the intake range-checks none of them |
| **Verified fact 6** | Live-form field 133 (life satisfaction) is `type='number' min='0' max='10' **step='any'**`, so **7.5 is a valid submission**. `rev_feelingscaleanswer` is a Whole Number 0–10, and `FeelingScaleInversion` is keyed `"0"`–`"10"` |

**The two failure modes, in order of likelihood:**

1. **Lost application (write).** An applicant ticks "Not sure" on any of the three "last year"
   questions. The website sends a sixth value. `Create_application` writes it to a picklist with no
   sixth option, Dataverse rejects the value, the intake run fails, `Respond_500_intake_failed`
   returns with **`retry: true`**, and the retry fails identically. **The application is lost, and it
   presents as a transient fault** — which is worse than the clean 400 D-003 fixed, because nothing
   distinguishes it from a network blip. This is precisely the outcome FR-010 exists to prevent.
2. **Failed scoring run (score), and the fail-closed design does not catch it.** If such a value does
   reach the column, `?['6']` is null → `string(null)` is `''` → **`int('')` throws**. The withhold
   gate tests for *absent*, not for *unmappable*, so the value sails past the one control designed to
   route a problem answer to a human. The same shape applies to `7.5` in
   `Invert_the_feeling_scale_answer` = `@int(string(outputs('Parse_feeling_scale_inversion')?[string(…)]))`.

**Why this is P2 and not P3.** It is triggered by an ordinary applicant answer on a form that is live
and taking applications today; it loses the application; and it has no monitoring that separates it
from a transient fault. That is the same severity as D-003, which it closely resembles: a contract
verified against a document rather than against the world.

**Why it is not development-agent's fault, and why it is still open.** Revision 0.7 explicitly
declined to renumber or extend any option set, on the correct grounds that doing so on its own
judgement would repeat the very error the revision existed to correct, and it recorded the mismatch
as **M-02 / V-08 / V-10**. That was the right call. But the spec records it as *"the form and the
schema disagree, Emily decides"* — it does not record that the Revitalise side **fails unsafely**
while the disagreement stands, which is what makes it a defect here rather than a mapping note.

**Remedy — the interim guard is the urgent half, and it does not need Emily:**

1. **Make the flows safe against a value they cannot use, before any decision about the scale.** Two
   small changes, both inside the existing design: bound the four answers in the trigger schema
   (`"minimum": 1, "maximum": 5` and `0`/`10`) so an unusable value is rejected cleanly at the
   boundary with a 400 rather than lost in a 500 retry loop; **and** widen the FR-022 withhold gate
   from `empty(…)` to "empty **or** not a key of the map", so an unmappable answer routes to a person
   exactly as a missing one does. The second is the one that matters, because it converts every
   future scale change from a run failure into a human review.
2. **Then the decision, which is Emily's and the board's (M-02):** either `rev_likertresponse` gains
   a sixth value with a defined point contribution and `MaxCircumstanceScore` is re-derived, or the
   form's three questions move to the five-point frequency scale. Note that today the same stored
   number means "None of the time" on seven questions and "Strongly disagree" on three — **D-009's
   stale SDD text is concealing that**, so fix D-009 in the same pass.
3. **Fold in the P4 from §2.2:** a renamed age-band label degrades `rev_agerange` to "Not known"
   silently. Same class of problem — a configuration map that fails quiet.

---

#### 🔧 development-agent annotation — 2026-08-13, dev-summary revision 0.8

> **Appended by `development-agent`, not by `test-agent`.** The status column above is
> test-agent's to change at retest; this records what was delivered and the evidence for it.
> All six verified facts are confirmed accurate. **Verified fact 6 in particular found a gap in
> the first version of this fix and is credited below.**
>
> **The remedy is NOT the interim guard this section recommended, and the reason matters.**
> Ground truth arrived after this report was written: `docs/Import/Book(Sheet1).csv`, 25 real
> applications with the hand-calculated score and the eleven answers behind each. **Row 25
> answered "Not sure" to all ten wellbeing questions and was scored 9.** Working it through —
> life-satisfaction raw 6 contributes 10−6=4, leaving 5 points across 10 answers — gives
> **0.5 points per "Not sure" answer, exactly, with no remainder.**
>
> So **"Not sure" is not malformed input. It is a valid answer that the charity already scores,
> and rejecting it would have been rejecting a person's honest answer** — from precisely the
> applicants least able to give a confident one. This section's instinct that the failure mode
> was "a lost application" was right; its assumption that the value was unusable was not, and
> that assumption came from the schema rather than from the charity's practice.
>
> **What was delivered:**
>
> | | Change | Evidence |
> |---|---|---|
> | Fact 2 fixed | `rev_likertresponse` gains value **6 "Not sure"**; new **`rev_agreementresponse`** (1–6, Strongly Disagree…Strongly Agree, Not sure) created and `rev_wellbeinganswer8/9/10` rebound to it — because the CSV shows those three use an **agreement** scale and the other seven a **frequency** scale, disjoint across all 25 rows | Both option sets verified present with all six options **inside both packed zips** |
> | Fact 3 fixed | `LikertPointMap` gains `"6":0.5` in both settings files; the cast changed from `int()` to **`float()`** and `likertPoints` from `integer` to **`float`** | The 25-row reconstruction test resolves labels, points and the inversion **from the shipped artefacts**, and reproduces every published score exactly |
> | Fact 4 fixed | The withhold gate is widened from emptiness to **"empty **or** not a key of the map"**, on all eleven scored answers | 3 new assertions |
> | Fact 5 fixed | `wellbeing_answer_1`–`10` bounded **`minimum: 1, maximum: 6`**; `feeling_scale_answer` bounded **`0`–`10`**. There were no bounds at all | 82 properties and 4 required fields unchanged — asserted |
> | **Fact 6 fixed — and it caught a gap in this fix** | The first pass widened the gate for the ten wellbeing answers only. Fact 6's note that field 133 is `step='any'` (so **7.5 is a real submission**) showed the eleventh answer had the **identical** unmappable-value hole. `Parse_feeling_scale_inversion` was moved ahead of the gate and a **third** condition added, withholding when the life-satisfaction answer is not a key of `FeelingScaleInversion` | 2 new assertions; the withhold branch's breakdown text now reports "Life-satisfaction answer scoreable: NO…" |
>
> **Both halves of remedy item 1 were implemented, not just one** — the bounds *and* the widened
> gate. They are complementary rather than alternatives: the bounds turn a value the column
> cannot store into a **clean 400 at the boundary** instead of a 500 retry loop, and the widened
> gate turns a value that *can* be stored but has no point value into a **human review** instead
> of a throw. Only the second survives a future option being added in the maker portal.
>
> **Remedy item 2 is partly overtaken and partly still open.** The decision this section framed
> as "either add a sixth value, or move the three questions to the frequency scale" is settled by
> evidence on both limbs: the sixth value exists **and** the three questions keep their agreement
> scale, because that is what the live form and the export both show. **`MaxCircumstanceScore`
> did not need re-deriving** — it stays **60**, since "Not sure" at 0.5 cannot raise the maximum.
> **But the reachable floor dropped from 10 to 5**, which the board needs for OQ-001 and which
> two updated tests now assert. **D-009's SDD half is NOT closed** — see its row above; SDD
> Amendment **A-01** is raised as *PROPOSED* and needs plan-agent.
>
> **Remedy item 3 (the age-band P4) is NOT addressed.** Out of scope for this cycle and still open.
>
> **One consequence this section could not have foreseen, flagged for the reviewer:** a total can
> now be **fractional** (an odd number of "Not sure" answers gives X.5) while
> `rev_circumstancescore` is an `int` column. Revision 0.8 **rounds half up**, in the applicant's
> favour, and writes the exact unrounded total into `rev_scorebreakdown`. **The data does not
> determine this rule** — the only "Not sure" row is whole by coincidence — so it is flagged as a
> judgement call in the Dev Summary for the reviewer to confirm or override, not presented as
> derived. Rounding also had to move **ahead of `Derive_status`**: comparing an unrounded 36.5
> against a borderline lower bound of 37 gives Auto-pass while the stored 37 is Borderline — a
> human review silently skipped on a record whose own score says it should have happened.

#### ✅ test-agent verification of the above — 2026-08-13, report revision 4

**Every one of the six "what was delivered" claims is accurate**, and each was checked against the
source and against both packed zips rather than against this annotation. D-014 is **RESOLVED**. Two
specific credits are due, because they are the kind of thing that usually gets lost:

- **The remedy really was better than the one this section recommended.** Rejecting "Not sure" with a
  400 would have rejected a valid answer that the charity already scores — from precisely the
  applicants least able to give a confident one — and this report would have signed off on it. The
  ground truth is what prevented that, and it was sought rather than waited for.
- **Verified fact 6 did catch a gap, exactly as claimed.** The life-satisfaction answer had the
  identical unmappable-value hole and the first version of the fix missed it. The third gate condition
  and the reordering of `Parse_feeling_scale_inversion` ahead of the gate are both present.

**Two corrections to the annotation, neither material to the fix:**

1. **"disjoint across all 25 rows" is not quite right — the two label sets share `Not sure`.** The
   option-set file and the Pester suite both state it correctly ("disjoint apart from 'Not sure'");
   `manifest.json`'s note and the fix commission dropped the qualifier. The precise statement is the
   one shipped in the artefacts, and it is the one that matters: a **shared** value 6 is exactly why
   one `LikertPointMap` can serve both scales.
2. **The claim that the split protects `rev_scorebreakdown` is not true of `rev_scorebreakdown`.**
   `Record_this_answer_in_the_breakdown` emits `'Wellbeing answer 8: response 1 = 5 points'` — the
   numeric option value, no label, from either scale. The evidence argument for the split holds for the
   **Dataverse form and view rendering** of those three columns, which is where it bites; the breakdown
   text neither had the problem nor gained the fix, and a trustee reading it still cannot see what the
   applicant answered. **P4, folded into D-015's remedy.**

**And the last paragraph above is where the new defect is.** The `Derive_status` reordering is correct,
real, and verified — its arithmetic checks out (with the TST/ACC values, an unrounded 20.5 is neither
`≤ 20` nor `≥ 21` and falls through to Auto-pass). But it fixed *which number* the comparison reads
without establishing *what that number is*. See §4.2.

### 4.2 D-015 (NEW, P2) — the rounding function does not implement the approved rounding rule

**The reviewer approved round half up. The build does not do round half up.**

| | |
|---|---|
| **Verified fact 1** | The expression is `@int(formatNumber(outputs('Calculate_circumstance_score'), 'F0'))`. Read from `REVScoringCalculateAndFlag-…json` **and** from the copy inside both packed zips, whose hashes match `manifest.json` |
| **Verified fact 2** | `formatNumber(number, format[, locale])` is .NET numeric formatting. `'F0'` is the fixed-point specifier with zero decimals — i.e. `value.ToString("F0")` |
| **Verified fact 3** | **Executed**, on the only runtime available here (.NET 10.0.10 — the same major family `pac 2.4.1` reports): `0.5 → "0"`, `2.5 → "2"`, `20.5 → "20"`, `30.5 → "30"`, `1.5 → "2"`, `3.5 → "4"`, `35.5 → "36"`. That is **round half to even**. It agrees with half-up only when the integer part is odd |
| **Verified fact 4** | A half-integer total is ordinary, not exotic: the fractional part is `.5` whenever an **odd** number of the ten wellbeing answers is "Not sure". 1, 3, 5, 7 or 9 "Not sure" answers all produce one. Row 25 of the ground truth is an all-"Not sure" application, so this population demonstrably exists |
| **Verified fact 5** | With the TST/ACC values in force — `KnockoutThreshold 20`, `BorderlineBandLower 21`, `BorderlineBandUpper 30` — an exact total of **20.5** rounds to **20**, and `lessOrEquals(20, 20)` is true, so `Derive_status` returns **4 = Auto-reject**. Under the approved rule it rounds to **21** and returns **3 = Borderline**, which is a human review by Emily. At the top of the band, **30.5** rounds to **30** and stays Borderline where the approved rule makes it Auto-pass |
| **Verified fact 6** | `rev_scorebreakdown` — the stored, trustee-facing evidence text — asserts the behaviour that is not implemented, in words: *"halves are rounded UP, in the applicant's favour, because a higher score means greater need."* `LikertPointMap`'s own description in both settings files says the same. So does the Dev Summary, in three places, and its approval line records round-half-up as **confirmed** |
| **Verified fact 7** | **Nothing asserts the mode, and nothing in the suite can.** Of 560 Pester assertions, those touching the rounding assert the *map contents*, the *0.5 derivation*, and that `Derive_status` *reads* `Round_the_circumstance_score` — never what that action computes. The 25-row reconstruction cannot cover it: as the Dev Summary itself notes, no ground-truth row produces a fractional total. The Dev Summary makes no claim to have executed it, and correctly does not |

**Why this is P2.** It changes an automated decision about a person, in the harmful direction, at the
one boundary the whole design exists to guard. `Derive_status`'s reordering in the same revision was
made specifically to stop "a human review silently skipped on a record whose own score says it should
have happened" — and this reintroduces exactly that, one action upstream, with the additional
aggravation that the record's own plain-English explanation tells the trustee the opposite of what
happened. FR-022's fail-closed design does not help: 20.5 is a perfectly scoreable total, so nothing
withholds and nobody is alerted. **It is silent by construction.**

**What would overturn this finding, stated so it can be checked rather than argued.** The one thing
this gate could not do is execute a Logic Apps expression — there is no environment. If Power
Automate's runtime turns out to round `'F0'` half **up** rather than half **to even**, then the stored
score is right today and D-015 downgrades to a **P3 documentation-and-test defect**: an unasserted,
runtime-dependent behaviour that a runtime upgrade could silently flip, on a rule whose stated
justification is the applicant's favour. **It does not disappear**, because .NET's midpoint formatting
behaviour has changed across runtime versions before, and nothing in this repository pins it, asserts
it, or records which behaviour was relied on. The recommended fix removes the question entirely rather
than answering it, which is why it is worth doing either way. §8 case 3′ is what settles it.

**Why it survived.** It is the only step in the scoring chain whose behaviour was *reasoned about*
rather than executed. The Dev Summary states the mode and, separately and adjacently, the mechanism
(`formatNumber(…,'F0')` "because the Logic Apps expression language has no `round()`, `ceiling()` or
`floor()`" — which is true, and is the right reason to go looking for an alternative). It never states
why `'F0'` would give half-up. Nothing links the two and nothing tests the link. **This is the same
failure shape as the six silent packaging defects and as D-003: a correct-sounding claim that nobody
executed.** In fairness, a genuine platform limitation is behind it — there is no rounding function to
call.

**Remedy — two options, both small. The first is a one-token change.**

1. **Minimal and provably correct: never present the formatter with a midpoint.**
   `@int(formatNumber(add(outputs('Calculate_circumstance_score'), 0.25), 'F0'))`.
   Because the fractional part is only ever `.0` or `.5`, adding `0.25` gives `.25` or `.75` — never a
   midpoint — so the rounding mode becomes irrelevant and the result is half-up on every runtime.
   `20.0 → 20.25 → 20`; `20.5 → 20.75 → 21`. **This is safe precisely because a test already asserts
   0.5 is the only non-integer in `LikertPointMap`** — that assertion is what makes the offset sound,
   and it should be cross-referenced in the expression's own description so the two cannot drift apart.
2. **Structural: never hold a fraction at all.** Accumulate in **half-points** as integers (the map
   doubled: `{1:10, 2:8, 3:6, 4:4, 5:2, 6:1}`), then round by integer division — `div(add(H, 1), 2)` is
   exactly round-half-up for non-negative `H`, with no float and no formatter anywhere. More robust,
   but it changes the shape of a board-editable configuration row, so it is the second-pass option
   rather than the hotfix.

**Whichever is chosen, two things must come with it:**

- **A test that pins the midpoint.** It cannot be a Logic Apps execution locally, so assert the
  *expression form* — that the value handed to `formatNumber` can never be a midpoint (option 1), or
  that no float appears in the chain at all (option 2). A static assertion that makes the reasoning
  explicit is worth far more than none, and it is what stops a later revision "tidying" the offset away.
- **Then run it live.** §8 carries the case: submit an odd number of "Not sure" answers and read back
  `rev_circumstancescore`, `rev_status` and `rev_scorebreakdown` **together**. Until that runs, the
  rounding rule is asserted by argument on both sides of this defect, and only one side is right.

**Folded in as P4 rather than raised separately:** the breakdown text emits numeric option values
rather than labels (see the verification note above), and `string(variables('likertPoints'))` on a
float variable may render a whole subtotal as `35` or `35.0` depending on runtime serialisation — both
are in the same trustee-facing sentence and should be fixed in the same pass. A third, untestable
locally: `Compose_score_breakdown` decides whether to print the "Rounded to …" sentence using
`equals(Calculate_circumstance_score, Round_the_circumstance_score)`, a float-versus-int comparison. If
Logic Apps does not coerce, a whole-number total would be told it had been rounded. Confirm it in the
same live run.

#### ✅ test-agent verification of the D-015 fix — 2026-08-13, report revision 5

**D-015 is RESOLVED.** Every one of the seven verified facts above was re-checked against the revision
0.9 source rather than assumed to have been addressed, and the fix was tested rather than read.

- **Verified fact 1 is superseded:** the expression is now
  `@int(formatNumber(add(outputs('Calculate_circumstance_score'), 0.25), 'F0'))`, in the source and in
  both stored zips.
- **Verified facts 2 and 3 stand as correct and are now written down where they belong.** `'F0'` *is*
  .NET fixed-point formatting and .NET *does* round a `double` midpoint to even — the expression's own
  description now records that as executed fact, along with the correction that what it previously
  claimed was false. Re-executed here: `0.5 → 0`, `2.5 → 2`, `20.5 → 20`, `30.5 → 30` on the raw
  values, and the correct answer on all of them once offset.
- **Verified facts 4, 5 and 6 are answered by the fix:** the half-integer total is still ordinary, but
  it now rounds up. With the TST/ACC values in force an exact **20.5** stores **21** and returns
  **3 Borderline** — the human review — instead of **4 Auto-reject**. `rev_scorebreakdown`'s
  plain-English promise that "halves are rounded UP, in the applicant's favour" is now true, and a
  test asserts that sentence is still present so it cannot be deleted away from the arithmetic.
- **Verified fact 7 — the reason it survived — is the one that has been properly closed.** Something
  now asserts the mode, and it asserts it by *executing* rather than by reading: 17 assertions, of
  which the behavioural ones run .NET's own formatter over every reachable total **through the offset
  parsed out of the shipped expression**. Mutation-tested independently at this gate: against the
  pre-0.9 expression, 7 assertion groups fail.

**The remedy chosen was option 1, and both attached conditions were met.** A test pins the midpoint —
in fact two, one behavioural and one structural, deliberately, because the structural one keeps biting
on a hypothetical future runtime that rounds half away from zero where the behavioural one would go
quiet. And the cross-reference the remedy asked for was **made mechanical rather than written as a
comment**: `'is sound only because 0.5 is the smallest point value'` asserts the dependency directly,
so introducing a point value of `0.25` breaks the suite instead of silently invalidating the offset.
That is more than was asked for.

**What still has not been done, and cannot be here.** The live case (§8 item 3′) is unchanged in
priority: **that the Power Automate runtime binds `formatNumber` to the .NET formatter tested here is
still an assumption.** The fix is now correct under *both* midpoint modes and both numeric types, so
the live run can no longer overturn the arithmetic — but it remains the only thing that proves the
expression evaluates at all in the runtime, and it settles D-018(c) in the same read.

**The P4s folded into this defect's remedy did not close with it** — see **D-018** in §4.000. One was
partially addressed; two are untouched.

### 4.3 SDD Amendment A-01 — the status is right, and it is not this report's to change

Checked as asked, because the wrong answer here would have been easy to reach. **A-01 is recorded
correctly and `PROPOSED` is the right status.**

- It is an **annotated block at the head of the SDD**, not an edit to the requirement text. FR-013, its
  acceptance criterion and §9 OQ-002 each carry a marked pointer to it, and the **original approved
  wording is left visible and intact** in all three places.
- The SDD carries `Status: APPROVED`, gated on a human `APPROVED` per `agents/plan-agent.md`. It is
  **plan-agent's artefact.** `development-agent` re-issuing it would have made an approved document say
  something nobody approved — precisely the class of error this pipeline keeps finding. The amendment
  says so in as many words and routes itself for approval.
- **A-01 also corrects the scope of its own commission**, unprompted: the cycle was requested as
  "resolve OQ-001 (exact scoring weights)", and OQ-001 is not the weights — it is the knockout cut-off
  and the band width. The CSV holds scores and answers but **no accept/reject outcomes**, so no cut-off
  can be inferred from it. **OQ-001 stays open with the board**; **OQ-002 is resolved by evidence.**

**What this means for the gate: D-009 cannot be closed by any test result.** The substance is shipped
and verified; the approved requirement text is still wrong. `lead-agent` should route A-01 to
`plan-agent` for a re-issued SDD revision and a re-gate. **Approving this test report does not approve
A-01**, and A-01 should not be left at `PROPOSED` indefinitely — an approved SDD whose FR-013
contradicts the shipped build is a live traceability defect, not a paperwork one.

### Status as at 2026-08-13 — the development-agent fix cycle for D-003 and D-004

| Defect | Status | What actually happened |
|---|---|---|
| **D-003** | ✅ **RESOLVED — in the code, not only in the document** | The defect was real but it understated itself. It described two contradictory *statements* in a document; the more serious problem was that the flow's own required list demanded two fields the live form does not reliably send. `date_of_birth` is **never** collected and `email` is collected only when the applicant chooses Email as their preferred contact method, so **the intake as delivered would have returned 400 to every real submission**. Fixed: required list is now the four fields the live form always collects, the reject guard / 400 body / log line agree, `age_range` is accepted and mapped, `group_linkage` is no longer accepted, and two expressions that would have thrown on an absent value are null-guarded. The contradictory "all eleven scored answers, never null" rule is gone — the eleven answers are accepted-not-required on purpose, because rejecting at the boundary loses the application whereas accepting it routes it to a person (FR-010, FR-022). **10 new assertions** in `src/tests/solutions/IntakeContract.Tests.ps1`; full suite **537 passed, 0 failed**. |
| **D-004** | ◐ **PARTIAL — one criterion confirmed FAIL, the rest still unaudited. Deliberately not closed.** | The defect named 1.3.5 Identify Input Purpose as the most consequential omission, and **direct inspection of the live page confirms it as a real failure**: across **251 `<input>` elements** the `autocomplete` attribute appears five times — once as `new-password` on the anti-spam honeypot and four times as `off`. **Not one field carries a valid purpose token.** A second confirmed failure was found that the defect did not name: **3.3.7 Redundant entry** — both email fields are two-box "Enter Email / Confirm Email" pairs. Four criteria are confirmed **PASS** (`lang="en-GB"`, skip link, label association, no CAPTCHA). **The other nine criteria D-004 listed cannot be assessed from static HTML and have not been assessed by anything else** — contrast, keyboard operation, focus order, focus visibility, zoom and reflow, screen-reader behaviour and target size all need axe-core plus a manual pass. So the *specification* half of D-004 is addressed (spec §10 now records exactly what was and was not checked, and makes no conformance claim beyond it) while the *audit* half is open and is raised as **spec OPEN-26**. Marking D-004 closed would assert a conformance position nobody has evidence for. |
| **D-002** | ⚠️ **Basis changed, NOT closed** | D-002 said the specification "deliberately removed" FR-003's income-band gate. There was nothing to remove: **the live form gates those questions on benefit status instead** — employment, income band, care costs and the £6,000 savings test appear only when the applicant says they receive no means-tested benefits. So FR-003 is still not met as written, but the deviation is in the live form, not in a document, and the decision needed is whether that gating is intended (it may well be — a means-tested benefit is itself evidence of low income) and how the income eligibility check should behave with no band. Recorded as mapping gap **M-04** and open item **OPEN-10**. **Still needs an SDD amendment or a restored gate; still owned by the reviewer and Emily.** |
| **D-008** | ⚠️ **Basis changed, NOT closed** | D-008 said a mandatory field could not be built because its option list was a placeholder blocked on OPEN-20. **The live form has all five option lists and they are now recorded verbatim**, so OPEN-20 closes. The problem inverts: the committed option sets do not match what the live form sends — three options where the schema has four (applicant type), five against nine (break type), four against seven (exceptional circumstance), free text against a picklist (helper relationship), and, worst, **ten functional areas against eight condition types** for the condition profile, which classify along different axes and cannot be mapped without a decision. Recorded as **M-01, M-05 and M-07**. Trimming or replacing an option set is safe before any application exists and unsafe after, so this is a before-go-live item. |
| **D-010** | ⛔ **SUPERSEDED — re-raise anything still applicable** | Every sub-item (a) to (g) was a defect in the internals of a document that no longer exists in that form: mandatory-field validation rules, per-field message text, an enumerated sanitisation list, F-number arithmetic, step counts and a cross-reference. Revision 1.0 replaced the enumerated sanitisation list with the standing rule (apply to every text field), and 3.3.7 is now recorded from the live form rather than inferred. **Nothing here is asserted as fixed** — the sub-items are moot rather than resolved, and if any still applies to revision 1.0 it should be raised against revision 1.0. |
| D-001, D-005, D-006, D-007, D-009, D-011, D-012, D-013 | Unchanged | Not touched by this cycle. |

The original defect table follows unchanged.

| Defect ID | Severity | Description | Linked Test |
|---|---|---|---|
| **D-001** | **P2** | **The primary authentication control for the solution's only public endpoint is unassigned, unprovisioned and unverified.** The Dev Summary and the flow's own description both name trigger-level platform authentication as "the primary control", with the client-ID header check as a deliberate *second* gate. That primary control exists nowhere in the delivery chain: no `operationOptions`/auth property in the flow definition, no provisioning script (verified by grep across `provisioning/`, `config/`, `.github/`, `scripts/` — zero hits), no TAD §12 row, no `post_deploy` step, and no smoke test. Meanwhile the second gate compares an HTTP header against `rev_IntakeAllowedClientId`, which the repo itself correctly documents as "a public identifier" — not a secret. **If the endpoint were stood up as the repository currently describes it, the only barrier to writing arbitrary applications into Dataverse would be knowledge of a non-secret client ID.** This is distinct from ADR-011 (which route to choose) and from WBS 0.3 (the service account): ADR-011 being open does not explain why the chosen route has no owner. Not exploitable today — no environment exists. **Remedy:** add an explicit TAD §12 / `tenant_prerequisites` item naming who configures trigger authentication and to what value, and add a smoke test that POSTs with no credential and asserts rejection *before* the definition runs | TC-401 |
| **D-002** | **P2** | **FR-003 is half-implemented and the deviation is unrecorded.** The form specification deliberately removes the income-band conditional gate that FR-003 requires, and asks the financial detail questions before the band. The reasoning is defensible (the free-text blob became eight typed questions that stand alone), but no SDD change request, ADR or open item records it — so an approved requirement is silently not met. A contradictory revision-0.1 instruction also survives ("If the applicant chooses 'Prefer not to say', still reveal F21 to F23"), and OPEN-10 perpetuates it. **Remedy:** either restore the gate or raise an SDD amendment against FR-003, and delete the stale instruction | TC-103 |
| **D-003** | **P2** | **The intake payload contract has two contradictory required-field lists.** The revision 0.2 banner states the required list as `submission_id, first_name, last_name, email, postcode, date_of_birth` (six fields, matching the flow's trigger `required` array exactly). But §11.1 rule 3 and the sign-off checklist additionally mandate that all eleven scored answers are "always present as integers… **Never null**", and that `0` must be sent rather than omitted. The true minimum payload is 17 fields, and the two statements are never reconciled. An integrator building from the banner produces a payload the spec's own checklist rejects — and, worse, one that silently routes every application to Under Review via FR-022 | TC-207 |
| **D-004** | **P2** | **WCAG 2.1 AA acceptance is narrower than the standard the specification claims to adopt.** The spec asserts `skills/accessibility-checklist.md` "applies in its entirety", but the sign-off checklist only requires evidence for criteria listed in its own §10.1/§10.2 tables. Criteria absent from those tables are therefore never evidenced — most consequentially **1.3.5 Identify Input Purpose**, i.e. no `autocomplete` attribute requirement anywhere, on a 78-question form collecting name, email, phone, address, town, postcode and date of birth from disabled applicants and unpaid carers with ~age-12 average reading level. Also missing: 1.1.1, 1.3.4, 1.4.12, 1.4.13, 2.4.1 (skip link), 2.5.3, 3.1.2, 4.1.2, and HTML validation. Two further criteria conflict internally: 2.2.1 ("no time limit causes loss of a draft") against the 30-day draft deletion rule, and 2.5.8 target size softened to "primary controls" where the checklist requires 44×44 for all. **This is the highest-human-consequence defect in the release**: the population is the one least able to absorb a non-conformant form, and the surface is out-of-palette, so the acceptance criteria are the *only* control | TC-501 |
| **D-005** | **P2** | **C-TECH-014 (HARD) cannot be satisfied as written and no test layer exists.** `knowledge/technology/coding-standards.md` defines no coverage threshold, `config/…-build.yml` has no coverage step, and the repository contains no automated test of any kind — no `src/tests/`, no Dataverse Web API tests, no Pester tests over the eleven provisioning scripts, no regression suite. `knowledge/technology/testing-tools.md` (which **is** populated) does define the unit layer for this stack and names `src/tests/dataverse/` as its home, so this is an unimplemented layer rather than an inapplicable one. **Remedy:** the Tech Lead sets a threshold appropriate to declarative Power Platform artifacts (or records C-TECH-014 as not-applicable to solution-source-only releases, with reasoning); and the eleven provisioning scripts — real PowerShell with real branching — get Pester coverage | TC-901 |
| **D-006** | **P3** | **The `secret-scan` build gate did not scan the delivered source in the recorded build.** `gitleaks detect --source .` scans git history by default; zero of the 47 files under `src/solutions/` are tracked in git, so the gate scanned 2 commits of unrelated history and reported PASS. Substantively near-vacuous — the same class of "clean log ≠ verified" defect revision 0.5 was written to prevent. **This test run closed the gap**: `gitleaks detect --no-git` over the working tree scanned 1.84 MB and found no leaks, so **C-TECH-001 genuinely passes**. In CI on a committed feature branch `detect` would cover the files, so this is a local-execution hole rather than a permanent one. **Remedy:** add `--no-git`, or run the gate after checkout of committed content only | TC-402 |
| **D-007** | **P3** | **Dev Summary §10's audit-coverage figure is wrong and a reviewer is asked to confirm it.** It states "**122** `IsAuditEnabled` columns across the four tables, counted after the pass (88 `rev_application`, 18 `rev_applicant`, 10 `rev_errorlog`, 6 `rev_setting`)". Actual, re-counted from the entity XML: `rev_errorlog` has **9** attributes and `rev_setting` **5** (which §2.1 of the same document states correctly), giving 120 attributes, of which **118** carry `IsAuditEnabled=1`. The figure is an attribute count presented as an audit-enabled count — and it necessarily includes the two calculated columns that §10 elsewhere correctly says are `IsAuditEnabled=0`. **Audit coverage itself is correct and complete**; the defect is that a revision 0.5 review checklist item ("Confirm nothing was lost… 122 audit-enabled columns") gives false assurance | TC-315 |
| **D-008** | **P3** | **A mandatory field cannot be built.** F53 (Applicant type) is marked mandatory but its option list is a flagged placeholder blocked on OPEN-20; F66 and F77 are in the same position. FR-001's completeness therefore cannot be demonstrated until Emily supplies the five real option lists. This is the known, already-tracked D-5 placeholder item — confirmed still clearly flagged in all five option-set files (`rev_title`, `rev_applicanttype`, `rev_breaktype`, `rev_helperrelationship`, `rev_exceptionalcircumstance`) — but its interaction with a *mandatory* field has not been recorded before | TC-101 |
| **D-009** | **P3** | **SDD FR-013 no longer describes what is built.** FR-013 names the response labels "Strongly Disagree = 5, Disagree = 4, Neutral = 3, Agree = 2, Strongly Agree = 1". Revision 0.3 replaced them with reviewer-confirmed frequency labels. The **point mapping by ordinal position is unchanged and correct** — this is not a scoring defect — but the SDD text for a requirement that drives an automated decision about a person has not been updated, and a stale "Strongly disagree" example also survives in the form spec's FR-006 section. **Remedy:** amend FR-013's label list | TC-303 |
| **D-010** | **P3** | **Form-specification internal defects** (grouped): (a) six fields marked mandatory whose validation rule does not require an answer, so the sign-off assertion "every field marked C blocks progress when revealed and empty" is untestable as written; (b) three consent messages ("Please tick the box to confirm this.") breach the spec's own rule that every message names its field; (c) the C-TECH-004 sanitisation list **omits F19 `other_condition_raw`** — 2000 characters of special-category free text — while including its mirror F57; (d) probable WCAG 2.2 3.3.7 redundant-entry failure between F68 and F38, two mandatory free-text destination questions the spec's own duplicate walk has not caught; (e) field-count arithmetic does not reconcile (77 stated, 78 actual) and the superseded 82 survives in OPEN-19; (f) two §3 step counts wrong; (g) wrong cross-reference (OPEN-5 cited where OPEN-7 is meant) | TC-102, TC-104 |
| **D-011** | **P4** | **`BorderlineBandLower` and `BorderlineBandUpper` carry the same placeholder token** (`{{PENDING_OQ_002}}`) in `prd-settings.json`. A single find-and-replace when OQ-002 is answered produces a degenerate one-point borderline band. `seed-settings.ps1`'s `Assert-NoPlaceholder` pre-flight prevents a half-seeded PRD, so this cannot ship silently — but it can produce a wrong band from a careless resolution. **Remedy:** distinct tokens (`{{PENDING_OQ_002_LOWER}}` / `_UPPER`) | — |
| **D-012** | **P4** | **The FR-016 build gate is narrower than described.** It greps for `body/(rev_narrativeraw\|…)` — the *trigger-row access form*. That is why the four names in the flow's description prose correctly do not trip it, but it also means a future edit reading the raw narrative via a "Get a row" action (`body('Get_row')?['rev_narrativeraw']`) would **pass the gate**. The Dev Summary already warns that "a substring gate is only as good as its list"; this is a second axis of narrowness it does not mention. FR-016 is satisfied today (verified independently, TC-307) — this is regression-protection strength only. **Remedy:** drop the `body/` prefix requirement or add a second pattern | TC-307 |
| **D-013** | **P4** | **The `no-hardcoded-thresholds` gate matches only JSON key/value pairs** (`"KnockoutThreshold": 20`). A numeric literal inside an expression — the shape an actual regression would take — would evade it. FR-017 is satisfied today (verified independently, TC-308) | TC-308 |

**Carried-forward items confirmed as accurately described, NOT re-raised as new defects:**

| Item | Confirmation |
|---|---|
| **C-TECH-013** — `DEFERRED_call_duplicate_grant_check` dead-code marker | ✅ Still exactly one `Compose` action that writes nothing; its text names the insertion point and the value to pass. Accurately described, correctly reported as a SOFT warning |
| **`auth` / `lint` deferred to CI** | ✅ Manifest's `steps_deferred` reasoning is accurate: both require an authenticated pac profile against a DEV environment that does not exist. Correctly characterised as an infrastructure gap, not a defect |
| **WBS 0.3 Conditional Access exception** | ✅ Still outstanding (SDD OQ-018, TAD A-R13). Confirmed by `logs/routing.log` 2026-08-10 22:21: interactive sign-in works, device-code/public-client is CA-blocked. A blocker for live flow execution, not a code defect |
| **Referee / Emergency Contact columns written by nothing** | ✅ Correct and intentional. Five columns present, `IsSecured=1`, released by the profile; **zero** executable references in the intake flow. Post-approval form is Automation #3 scope |
| **Five placeholder option sets** | ✅ All five still carry explicit PLACEHOLDER markers in-file. See D-008 for the one new interaction |
| **Ethnic group (SDD OQ-027)** | ✅ **Genuinely absent from the schema**, as intended. The only occurrences are three comments recording the deliberate exclusion and that export column 150 proves the live form does collect it. The intake trigger explicitly does not accept it |
| **DPIA / RoPA unsigned "Concept draft"** | ✅ Confirmed unchanged. A go-live gate (UK GDPR Art. 35, SDD OQ-030), not a test failure — recorded in §7 |
| **C-TECH-030 wording stale under ADR-007** | ✅ Accurately described. Scoped to pipeline-agent, so out of this run's formal check; flagged for the Tech Lead who owns `constraints/technology/` |

---

## 5. Constraint & Compliance Verification

Applied `skills/how-to-apply-constraints.md`. Scope filter: rows whose `Scope` column names
**test-agent**, at both severities — **3 domain HARD, 0 domain SOFT, 10 technology HARD,
1 technology SOFT** (14 rows). Scopes were extracted mechanically from the constraint files rather
than read by eye.

**Re-run in full at the retest, 2026-08-13 (report revision 3).** The scope filter was re-derived from
the constraint files, not carried over. **Result: 13 / 13 HARD pass, 1 / 1 SOFT passes, zero
warnings → Overall PASS.** The two HARD failures that made revision 1 of this gate `BLOCKED` —
C-TECH-006 and C-TECH-014 — are both now PASS, each verified by execution.

**Re-run in full again at the second retest, 2026-08-13 (report revision 4).** Scope re-extracted
mechanically from both constraint files a third time — the same **14** rows (3 domain HARD, 0 domain
SOFT, 10 technology HARD, 1 technology SOFT). Every mechanical check was re-executed against the
changed source rather than carried forward: the secret scan **as the config now specifies it**, the
`TODO`/`FIXME`/`HACK` grep across `src/tests/` as well, the connector enumeration across all four
flows, the OData-escaping walk (now five interpolated values), the FR-016 token/secured-column
intersection, the 22-script AST parse, both `verify-*.py` scripts, and the Pester coverage gate.
**Result: 13 / 13 HARD pass, 1 / 1 SOFT passes, zero warnings → Overall PASS, unchanged.**

> **Two constraints could have moved on this revision and neither did.** **C-TECH-001** improves
> materially — the `--no-git` flag is now in the config, so the PASS is reproducible from the
> repository instead of resting on a human remembering a flag (**D-006 closed**). **C-TECH-004** keeps
> its PASS: the range-validation gap it recorded as D-014 is closed on both axes (bounds *and* the
> widened gate), and D-015 does not touch it — a rounding-mode error is neither an injection nor a
> sanitisation failure, and nothing unsafe is persisted. **D-015 is a functional defect against
> FR-014, and it fails this run on the P2 rule, not on the constraint check.**

> **On why C-TECH-006 is PASS and not still FAIL, stated explicitly because it is the load-bearing
> judgement in this gate.** Revision 1 failed it for two reasons: the primary control existed nowhere
> in the delivery chain, **and** its `Verify By` needs an environment. The first reason is gone —
> owner, value, provisioning script, TAD rows and an executable smoke test on both environments, all
> re-verified from source. The second reason remains and always will at this gate. But that second
> reason is shared by **C-DOM-010, C-DOM-011, C-TECH-040, C-TECH-042 and C-TECH-045**, every one of
> which this report records as PASS (design) with live verification deferred. The rule revision 1 set
> was: a control that exists, is owned, and is asserted by a test → PASS; a control that is *claimed*
> and exists nowhere → FAIL. C-TECH-006 has moved from the second category to the first, so it is
> PASS under the report's own rule. Holding it at FAIL on the environment gap alone would apply a
> standard to it that five other HARD constraints are not held to. **What has not changed is that no
> unauthenticated request to that endpoint has ever been observed being rejected** — that is §8's
> first item, and PRD must not receive the endpoint URL before it passes.

### 5.1 In-scope constraints

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| **C-DOM-004** | Personal data must not be written to application logs | **PASS** | Verified three ways, not asserted. (1) `rev_errorlog` has 9 attributes — `rev_name`, `rev_flowname`, `rev_runid`, `rev_errormessage`, `rev_recordreference`, `rev_occurredon`, `rev_severity`, `rev_resolved`, `rev_resolvednote` — **no column able to hold personal data**. (2) Every caller of the failure-alert child flow passes `submission_id` or a platform error string; the incomplete-payload log message names *field names*, never values. (3) All four daily-summary queries select `rev_applicationid` **only**, so the flow never holds a name, reference, score or narrative to leak. Live log-output test in §8 |
| **C-DOM-010** | All create/update/delete on sensitive entities audit-logged | **PASS (design)** | `IsAuditEnabled=1` on all four tables and on 118 of 120 attributes; `IsRetrieveAuditEnabled=1`. The two exclusions are the calculated columns `rev_fullname` and `rev_costs` — correct, since Dataverse audits stored values and both source-column sets are fully audited, so no coverage is lost. `ensure-auditing.ps1` enables organisation auditing (the tenant-wide master switch, without which table auditing has no effect) plus table auditing via the metadata endpoint. **Live audit-record verification BLOCKED** (§8) |
| **C-DOM-011** | Audit records include timestamp (UTC), actor, action, entity ID, before/after | **PASS (design)** | Satisfied by **native Dataverse field-change auditing**, which supplies exactly those five fields without custom code — the correct mechanism, and the reason no bespoke audit table exists. `ensure-auditing.ps1` sets `auditretentionperiodv2 = 2192` days (6 years, the reviewer-confirmed C-DOM-013 value). Note D-007: the Dev Summary's coverage *count* is wrong; the coverage itself is not. **Live record-shape verification BLOCKED** |
| **C-TECH-001** | No hardcoded secrets, credentials, API keys or tokens in version control | **PASS** | `gitleaks detect --source .` → *no leaks found*. Because that scans git history and all 47 solution files are untracked (**D-006**), the scan was **re-run as `gitleaks detect --no-git`** over the working tree: 1.84 MB scanned, *no leaks found*. Independent pattern grep for `client_secret`/`password`/`api_key`/`bearer`/private-key headers across `src/solutions`, `provisioning`, `config`, `.github`, `scripts` returns nothing but comments recording `CLIENT_SECRET`'s removal and `<secretstore>0</secretstore>` (a definition flag, not a value). **This release uses no runtime secret at all** · **Re-run at retest:** `gitleaks detect --no-git` over the working tree — **2.89 MB scanned, no leaks** (larger than revision 1's 1.84 MB because `src/tests/` now exists). The pattern grep returns only test assertions that *forbid* secrets. Two new credentials entered the design in revision 0.6 and both are correctly handled as secrets rather than values: the intake trigger URL (a SAS-signed credential) is held as `INTAKE_ENDPOINT_URL_TEST` / `_PRD` CI secrets and the verify script prints scheme/host/path with the query string redacted, and the caller's own certificate or secret is deliberately issued out of band and never touched by any script. ⚠️ **The config still does not do this** — `build.yml` line 77 has no `--no-git`, so **D-006 stays open** and this PASS rests on a manual re-run · 🔧 **development-agent, 2026-08-13 (rev 0.8): the config now does this.** `--no-git` is in the `secret-scan` step, and the command was executed exactly as the config specifies it: ≈3.06 MB scanned, **no leaks found, exit 0** (the byte figure drifts by a few KB between runs because these documents are themselves inside the scan scope; the load-bearing part is *no leaks* and *exit 0*) (larger than the retest's 2.89 MB because revision 0.8 adds a new option set and ~250 lines of test code). **This PASS no longer rests on a human remembering a flag.** No new secret entered the release in revision 0.8 — the diff is two option sets, an entity XML, two flow definitions, two settings files, a build config, a test file and documents |
| **C-TECH-004** | All user inputs validated and sanitised before processing or persistence | **PASS — with a range-validation gap recorded as D-014** | Typed trigger schema, **82 properties**, `required` array of **four** (reduced from six in revision 0.7 — re-verified), enforced by an explicit completeness check **before any Dataverse write**. **The reduction is not a weakening:** requiring a field the source never sends is not validation, it is rejection of valid input, and the two null-guards and the two-branch applicant lookup added alongside it make the flow strictly *more* defensive. Validation is largely bought at the schema level: types are declared, `rev_feelingscaleanswer` carries `MinValue 0` / `MaxValue 10` on the column, the eight typed financial columns cannot hold a paragraph, and every value interpolated into an OData filter is escaped (C-TECH-005). **The gap:** `wellbeing_answer_8/9/10` and `feeling_scale_answer` are declared as bare `integer` with **no `minimum`/`maximum`**, so a value the column cannot store passes the schema and fails at persistence — **D-014**. 🔧 **development-agent, 2026-08-13 (rev 0.8): the gap is closed, and wider than reported.** All ten `wellbeing_answer_*` properties (not just 8–10) now carry `"minimum": 1, "maximum": 6`, and `feeling_scale_answer` carries `"minimum": 0, "maximum": 10` — each with a description stating why the bound exists and that omitting the field withholds the outcome rather than rejecting the application. The `required` array is still the same **four** fields and the property count still **82**, both asserted, so nothing became newly rejectable. Bounds are paired with a widened FR-022 gate so that a value which *is* storable but has no configured point value routes to a human instead of throwing — the two controls cover different halves and neither alone is sufficient. **Why this is recorded as PASS with a defect rather than a violation, stated so it can be overruled:** this constraint's rationale is injection prevention and its `Verify By` is a malformed-input security test; every injection-relevant control is present and independently verified, nothing unsafe is persisted, and no bypass exists — the failure is availability and data integrity, which is why it is raised as a **P2 functional defect against FR-010 / FR-022** instead. **A reviewer who reads "malformed input causes an unhandled exception" as a C-TECH-004 breach would be reasonable, and the gate consequence is identical either way: D-014 is an open P2, so this run cannot be PASS.** Second residual, unchanged, in the *specification* rather than the flow: the sanitisation list omits F19 `other_condition_raw` (**D-010c**) |
| **C-TECH-005** | Parameterised queries / no string concatenation in data-store operations | **PASS with recorded caveat** | Both OData `$filter` expressions incorporate user input and both escape single quotes by doubling — `replace(x, '''', '''''')` — which is the platform-correct OData literal escaping. The Dataverse connector exposes no parameter-binding alternative, so escaping is the available control; there is no SQL and no ORM in scope. Caveat carried forward from the Dev Summary unchanged: correctness depends on that escaping being complete, and it is applied to all four interpolated values (`email`, `first_name`, `last_name`, `submission_id`) · **Re-verified at retest across all four flows.** Revision 0.7 made `Find_existing_applicant`'s `$filter` two-branch and added a **fifth** interpolated value, `postcode`; it goes through the same `replace(x, '''', '''''')` doubling. Both Daily Summary filters interpolate `outputs('Compute_reporting_window_start')` — a computed date, not user input — so no escaping is required there. ⚠️ **Minor test gap:** `IntakeContract.Tests.ps1`'s general assertion walks *every* filter and does cover the new branch, but its companion named assertion still enumerates only four fields and was not updated to include `postcode`. Correctness is unaffected; the named list is one field behind the definition. **P4, folded into D-014's remedy** |
| **C-TECH-006** | Authentication enforced on all non-public routes and operations | ~~❌ FAIL~~ → ✅ **PASS (provisioned, owned and asserted), live enforcement BLOCKED** | **Re-verified at retest, from source, not from the Dev Summary.** The definition-level second gate is unchanged and is the **first** action, with no path from it to a write. The primary control now exists in the delivery chain, which is what revision 1 failed it for: (1) `provisioning/entra/ensure-intake-client.ps1` — AST-parses clean, check-before-create, emits CREATED/EXISTS/FAILED, takes `-Env`, asserts a pre-existing registration really carries the declared Microsoft Flow Service permission, and reports credential posture **by count only**; (2) an `intake` block in **both** settings files carrying mode, audience, the double-slash `.default` scope, required claims, accepted rejection codes `[401, 403]` and a named owner (**Wanstor**, tenant administration); (3) a named manual `post_deploy` step on **both** TST/ACC and PRD, ordered explicitly **before** the flow is turned on; (4) `provisioning/entra/verify-intake-endpoint-auth.ps1` wired into **both** environments' `smoke_tests` — the literal executable form of this constraint's `Verify By`, whose second check asserts the response is **not** the flow's own `{"error":"unauthorised"}` body, so a wide-open trigger fails the deployment. The script's regex and the flow's actual 401 body were compared directly and agree, and `IntakeContract.Tests.ps1` asserts that coupling so a future edit to either cannot silently break the detector. **Still BLOCKED:** the `Verify By` has never been executed — no environment. **One residual no test can detect:** a blank *Allowed users* field under this mode silently reverts to whole-tenant scope; the pipeline names it and instructs reading the field back. **D-001 closed; the live case is §8's first item** |
| **C-TECH-011** *(SOFT)* | No `TODO`, `FIXME` or `HACK` comments in code delivered to Test or above | **PASS** | `grep -rniE '\b(TODO\|FIXME\|HACK)\b'` across `src/solutions`, `scripts`, `provisioning`, `config` and `.github` returns **nothing**. The `DEFERRED_call_duplicate_grant_check` marker carries no such token and is correctly reported under C-TECH-013 (development-agent scope) instead · **Re-run at retest with `src/tests/` now in scope: still nothing.** The one deliberate `-Skip` in the suite carries a defect id and a one-line fix rather than a `TODO`, which is the right form |
| **C-TECH-014** | Unit test coverage must meet the threshold in `coding-standards.md` | ~~❌ FAIL~~ → ✅ **PASS — verified by re-execution, twice** | **Every element the constraint names now exists and was re-run, not read.** (1) `coding-standards.md` has a **Test Coverage** section defining **80% line coverage over `provisioning/{common,entra,dataverse}`, build-failing**, plus a stated separate obligation for declarative artefacts (asserted invariants against an enumerated list, since an `Entity.xml` has no executable lines). (2) `build.yml` has the step: `Invoke-Tests.ps1 -CodeCoverage -CoverageThreshold 80`. (3) **Re-ran it: 537 passed, 0 failed, 1 skipped; 1188 of 1283 commands executed = 92.60%**, exit 0 — matching `manifest.json` exactly. (4) **The gate was proven to bite:** re-run at `-CoverageThreshold 99` it prints FAILED and exits **1**, so it is a gate rather than a report — the script enforces the threshold itself precisely because Pester's `CoveragePercentTarget` exits 0 below target. **D-005 closed.** ⚠️ Two things the reviewer must not read past: the threshold is a **Tech Lead decision taken by development-agent with no Tech Lead available**, flagged as such in the standard itself and awaiting confirm-or-override; and **coverage of the provisioning scripts is not coverage of the solution** — no flow runtime behaviour is tested, because there is no environment to run one in |
| **C-TECH-040** | Security roles assigned only via Entra-group-backed group teams — never directly to users | **PASS (design), live BLOCKED** | Three independent confirmations. (1) Neither role file contains any user assignment — the only `systemuser` references are `prvReadSystemUser` privileges, legitimately needed to resolve the FR-018 `rev_overriddenby` lookup. (2) `bind-roles-to-groups.ps1` creates AAD-Security-Group-type group teams and binds roles **by name**, because role GUIDs differ per environment. (3) `verify-role-bindings.ps1` asserts the **absence** of direct user-role assignments via `systemuserroles_association` in test/acc/prd, skipped in dev — and `allowedDirectRoleAssignments` is `[]` in **both** settings files, so there is no carve-out. The live `systemuserroles_association` query is in §8 |
| **C-TECH-042** | All provisioning / `post_deploy` scripts idempotent — check-before-create, report CREATED/EXISTS/FAILED | **PASS (source review), live BLOCKED** | **Re-run at retest: all 22 `.ps1` files under `provisioning/` parse cleanly (pwsh 7.6.4 AST parse, 0 errors)** — 22, not 20, because revision 0.6 added `ensure-intake-client.ps1` and `verify-intake-endpoint-auth.ps1`. Both new scripts honour the contract: the mutating one is check-before-create (`Get-MgApplication` before `New-MgApplication`) and emits CREATED (2) / EXISTS (3) / FAILED (5); the verify-only one emits PASS/FAIL and mutates nothing; both take `-Env` with a `ValidateSet`. Beyond parsing, **the scripts are now genuinely exercised** — 273 contract assertions derived from the README's five numbered rules **from the AST** rather than by grepping, plus 146 more running the real scripts against mocked Graph and Dataverse with the real shared helpers executing. That is a materially stronger basis than revision 1 had. *Original evidence retained:* Every mutating script emits `CREATED`/`EXISTS`/`FAILED` and takes `-Env`; the four verify-only scripts correctly emit PASS/FAIL instead. Check-before-create confirmed by inspection in each Phase 1 script (e.g. `ensure-column-security-profile-members.ps1` reads current `teamprofiles` membership before associating; `seed-settings.ps1` is a keyed upsert with a placeholder pre-flight *before any write*). One honest caveat carried from the Dev Summary: splitting the deploy registration per environment retired the "second run proves idempotency" property, so both runs' output must be read. **A live re-run producing EXISTS is BLOCKED** |
| **C-TECH-045** | All connectors comply with target DLP policy; no mixing of business and non-business groups | **PASS (design)** | Exactly **three** connectors are referenced across all four flows — `shared_commondataserviceforapps`, `shared_teams`, `shared_office365` — plus the Request/HTTP trigger. All four sit in the TAD §6.4 business group, including the two that group had originally omitted (Request/HTTP, Word Online). No connector is referenced that this release does not use, and no non-business connector appears. **Live import validation BLOCKED** |
| **C-TECH-046** | Out-of-box security roles never modified — copy into a `[PREFIX]` role | **PASS** | Both roles are custom, `REV`-prefixed, with solution-owned GUIDs (`{b2d4e6f8-2001-…}`, `{b2d4e6f8-2002-…}`). No out-of-box role ID appears anywhere in the solution source or in either packaged zip. Privilege counts re-counted **from inside the managed package** after the revision 0.5 root-element edit: 40 and 33 |
| **C-TECH-048** | Code Apps access data only through managed connector data sources — no hand-rolled token acquisition | **PASS (vacuously — verified, not assumed)** | No Code App exists in Phase 1 (the trustee portal is Automation #6 / Phase 3). Verified rather than asserted: grep for `msal`, `acquireToken`, `power.config`, `@azure/msal`, `client_credentials` across `src/solutions` and `scripts` returns nothing. No `code-app` artifact is declared in `build.yml` |

### 5.1.1 Constraint check block — retest, 2026-08-13 (report revision 3)

```
CONSTRAINT CHECK
Domain   HARD: 3 / 3    |  violations: NONE
Domain   SOFT: 0        |  warnings:   NONE  (no domain SOFT row is scoped to test-agent)
Tech     HARD: 10 / 10  |  violations: NONE
Tech     SOFT: 1        |  warnings:   NONE
Overall: PASS
```

**Movement since report revision 1:** `Tech HARD 8 / 10 → 10 / 10`; violations
`C-TECH-006, C-TECH-014 → NONE`; `Overall: BLOCKED → PASS`.

**The constraint gate passing does not make the test run PASS.** Three P2 defects are open (D-002,
D-004, D-014) and five test layers cannot be executed. Per `agents/test-agent.md` those are
independent fail conditions from the constraint check, and they are why §Status reads PARTIAL.

### 5.1.2 Constraint check block — SECOND retest, 2026-08-13 (report revision 4) — authoritative

Every row below was re-executed against the revision 0.8 source, not carried forward.

```
CONSTRAINT CHECK
Domain   HARD: 3 / 3    |  violations: NONE
Domain   SOFT: 0        |  warnings:   NONE  (no domain SOFT row is scoped to test-agent)
Tech     HARD: 10 / 10  |  violations: NONE
Tech     SOFT: 1        |  warnings:   NONE
Overall: PASS
```

**Movement since report revision 3:** none in the counts. One row is materially stronger —
**C-TECH-001** now passes *from the committed config* rather than from a manual re-run, which closes
**D-006**. Everything else holds at the same status on re-executed evidence.

**Evidence re-executed for this block:**

| Constraint | Re-executed check | Result |
|---|---|---|
| C-TECH-001 | `gitleaks detect --source . --no-git --no-banner --redact --exit-code 1` — **the command as `build.yml` line 91 now specifies it** | ✅ 3.07 MB scanned, **no leaks found, exit 0**. Independent secret-pattern grep across `src/solutions`, `provisioning`, `config`, `.github`, `scripts` returns only test assertions that *forbid* secrets and doc prose about bearer tokens in the verify script. **No new secret entered in revision 0.8** |
| C-TECH-004 | Trigger schema re-parsed | ✅ 82 properties, `required` = the four fields, **all eleven scored answers bounded** (`wellbeing_answer_1`–`10` at `1`–`6`, `feeling_scale_answer` at `0`–`10`). Zero unbounded. D-014's recorded gap is closed on both axes |
| C-TECH-005 | Every `$filter` in all four flows walked | ✅ Five interpolated values in the intake (`submission_id`, `email`, `first_name`, `last_name`, `postcode`), each through `replace(x, '''', '''''')`. Daily Summary interpolates only a computed date. ⚠️ The P4 carried from revision 3 stands: `IntakeContract.Tests.ps1`'s *named* escaping assertion still enumerates four fields, not five |
| C-TECH-011 *(SOFT)* | `grep -rniE '\b(TODO\|FIXME\|HACK)\b'` across `src/`, `scripts/`, `provisioning/`, `config/`, `.github/` — including the ~250 new lines of test code | ✅ **Nothing.** The one deliberate `-Skip` still carries a defect id rather than a token |
| C-TECH-014 | **Re-ran** `Invoke-Tests.ps1 -CodeCoverage -CoverageThreshold 80` | ✅ **560 passed, 0 failed, 1 skipped; 1188 of 1283 commands = 92.60%**, exit 0 — matches `manifest.json`. +23 assertions since build #2. ⚠️ The 80% figure is still a Tech Lead decision taken without a Tech Lead, and coverage of the provisioning scripts is still not coverage of the solution |
| C-TECH-042 | pwsh AST parse of all 22 `.ps1` under `provisioning/` | ✅ 22 scripts, **0 parse errors**. Live re-run producing EXISTS still BLOCKED |
| C-TECH-045 | Connector enumeration across all four flow definitions | ✅ Exactly three — `shared_commondataserviceforapps`, `shared_teams`, `shared_office365`. Revision 0.8 added none |
| C-TECH-046 | `RolePrivilege` re-counted inside the fresh managed zip | ✅ `REV Admin` 40, `REV Service Automation` 33. No out-of-box role id anywhere |
| C-DOM-004 | **Independent extraction** of every `rev_*` token from the scoring definition with descriptions stripped, intersected against the 34 secured columns; plus a read of both rewritten breakdown texts | ✅ 25 tokens, **intersection empty** (this also re-confirms FR-016 after two flow edits). Both rewritten texts name *question numbers, option values and point values* — no applicant identity, and the withhold branch's new "Life-satisfaction answer scoreable: NO…" line names no value |
| C-DOM-010 / C-DOM-011 | Re-read the three rebound attributes | ✅ `rev_wellbeinganswer8/9/10` keep `IsAuditEnabled=1` through the rebind. Live verification still BLOCKED |

**The constraint gate passing does not make the test run PASS.** Three P2 defects are open — **D-002,
D-004 and D-015** — and five of nine test layers still cannot be executed. Per
`agents/test-agent.md` those are fail conditions independent of the constraint check, and they are why
§Status reads **PARTIAL**.

### 5.1.3 Constraint check block — THIRD retest, 2026-08-13 (report revision 5) — authoritative

Scope re-extracted **mechanically** from both constraint files a fourth time — the same **14** rows
(3 domain HARD, 0 domain SOFT, 10 technology HARD, 1 technology SOFT). Every mechanical check below was
re-executed against the revision 0.9 source, not carried forward.

```
CONSTRAINT CHECK
Domain   HARD: 3 / 3    |  violations: NONE
Domain   SOFT: 0        |  warnings:   NONE  (no domain SOFT row is scoped to test-agent)
Tech     HARD: 10 / 10  |  violations: NONE
Tech     SOFT: 1        |  warnings:   NONE
Overall: PASS
```

**Movement since report revision 4:** none in the counts. **One row is materially stronger:**
**C-TECH-014** now covers the scoring engine's rounding *behaviourally* rather than only structurally —
the suite executes .NET's own formatter over every reachable total instead of asserting the shape of an
expression, which is the specific gap that let D-015 through 560 passing assertions. That is a change
in the *quality* of the coverage the constraint measures, not in the percentage.

**Evidence re-executed for this block:**

| Constraint | Re-executed check | Result |
|---|---|---|
| C-TECH-001 | `gitleaks detect --source . --no-git --no-banner --redact --exit-code 1` — **the command as `build.yml` line 91 specifies it** | ✅ **3.19 MB scanned, no leaks found, exit 0.** Still passes *from the config*, not from a remembered flag. No new secret entered in revision 0.9 — the diff is one expression, one description, one XML comment, a test file, a harness module and documents |
| C-TECH-004 | Trigger schema re-parsed | ✅ 82 properties, `required` = the four fields, **zero unbounded scored answers** (`wellbeing_answer_1`–`10` at `1`–`6`, `feeling_scale_answer` at `0`–`10`). Unchanged by revision 0.9 |
| C-TECH-005 | Every `$filter` in all four flows walked | ✅ Five interpolated values in the intake, each through `replace(x, '''', '''''')`. ⚠️ **The P4 carried from revisions 3 and 4 stands, re-verified**: `IntakeContract.Tests.ps1`'s *named* escaping assertion (line 364) still enumerates exactly four fields — `email`, `first_name`, `last_name`, `submission_id` — not `postcode`. The *general* assertion (line 349) does walk every filter and does cover it, so correctness is unaffected |
| C-TECH-006 | Re-read the definition-level gate, the settings blocks and the pipeline wiring | ✅ Unchanged by revision 0.9. **PASS (provisioned, owned and asserted); live enforcement still BLOCKED** and still §8's first item. **PRD must not receive the endpoint URL before it passes** |
| C-TECH-011 *(SOFT)* | `grep -rniE '\b(TODO\|FIXME\|HACK)\b'` across `src/`, `scripts/`, `provisioning/`, `config/`, `.github/` — including the new test and harness code | ✅ **Nothing.** The one deliberate `-Skip` still carries a defect id rather than a token |
| C-TECH-014 | **Re-ran** `Invoke-Tests.ps1 -CodeCoverage -CoverageThreshold 80` | ✅ **577 passed, 0 failed, 1 skipped; 1188 of 1283 commands = 92.60%**, exit 0 — matches `manifest.json`. **+17 assertions since build #3**, and they are the first in the suite that *execute* rather than inspect. ⚠️ The 80% figure is **still a Tech Lead decision taken without a Tech Lead**, and coverage of the provisioning scripts is **still not coverage of the solution** |
| C-TECH-042 | pwsh AST parse of all 22 `.ps1` under `provisioning/` | ✅ 22 scripts, **0 parse errors**. Live re-run producing EXISTS still BLOCKED |
| C-TECH-045 | Connector enumeration across all four flow definitions | ✅ Exactly three — `shared_commondataserviceforapps`, `shared_teams`, `shared_office365`. Revision 0.9 added none |
| C-TECH-046 | `RolePrivilege` re-counted; out-of-box role id search | ✅ Unchanged; no out-of-box role id anywhere in source or either stored zip |
| C-TECH-048 | Grep for `msal` / `acquireToken` / `client_credentials` across `src/solutions` and `scripts` | ✅ Still vacuous-but-verified. No Code App exists in Phase 1 |
| C-DOM-004 | **Independent extraction** of every `rev_*` token from the scoring definition with descriptions stripped, intersected against the 34 secured columns | ✅ 25 tokens, **intersection empty**. All four special-category columns appear **0 times** in the executable definition — FR-016 re-confirmed after a third flow edit. The breakdown text names question numbers, option values and point values only |
| C-DOM-010 / C-DOM-011 | Re-read the audit flags; confirmed no `Entity.xml` changed in revision 0.9 | ✅ Unchanged. **Live verification still BLOCKED.** Note D-007: the Dev Summary's coverage *count* is still wrong in four places; the coverage itself is complete |

**The constraint gate passing does not make the test run PASS.** **Two** P2 defects are open — **D-002
and D-004** — and five of nine test layers still cannot be executed. Per `agents/test-agent.md` those
are fail conditions independent of the constraint check, and they are why §Status reads **PARTIAL**.

**One thing this block should not be read as saying.** The constraint check has now returned PASS three
revisions in a row, including the revision in which D-015 — a defect that silently Auto-rejected
applicants the approved rule sends to human review — was live in the build. **The constraint set does
not contain a row that D-015 violated**, and that is a property of the constraint set, not evidence that
the build was sound. A PASS here means the enumerated rules are satisfied; it has never meant the
release is correct.

### 5.2 Final-verifier confirmation of out-of-scope rows

`constraints/README.md` describes test-agent as the final verifier of "All HARD + SOFT" while
`agents/test-agent.md` applies a scope filter. The scope-filtered set above is the formal check; the
remaining rows are confirmed here so nothing falls between the two readings.

| Constraint ID | Owning scope | Status at this gate |
|---|---|---|
| C-DOM-001, C-DOM-002 | plan/architect | PASS — SDD §7.1 classification and §7.2 lawful basis complete; every column added in revision 0.2 classified in its own `<Description>`. `rev_gender` correctly classified as ordinary personal data, benefit status correctly at the highest tier |
| C-DOM-003 | architect/dev | PASS with a declared partial — four bulk-delete jobs scripted; the 6-year paid-grant rule is designed and deferred, with no record class left unprotected (§2.4) |
| C-DOM-005 | architect | **ACCEPTED OPEN ITEM** — no SAR mechanism exists or is agreed (TAD §4.2, risk A-R22). Accepted by the reviewer 2026-08-10 and **still unresolved**. No SAR SLA exists either (OQ-023), so there is nothing to test even once a mechanism exists |
| C-DOM-006 | architect | PASS (design) — erasure path designed; helper flow is Phase 4 |
| C-DOM-012 | architect | PASS — Dataverse audit store is append-only by construction; neither role carries an audit-deletion privilege, confirmed in both role files |
| C-DOM-013 | architect | PASS — 6 years, reviewer-confirmed; implemented as `auditretentionperiodv2 = 2192` |
| C-DOM-020 | architect/dev | PASS — two narrow roles, each with an explicit "deliberately absent" block; 34 columns behind the profile; `REV Service Automation` is *narrower* than TAD §6.2 in three ways, all toward less privilege |
| C-DOM-021 | architect/dev | PASS — bulk-delete job creation is a gated `post_deploy` step, not available to `REV Admin`; `rev_setting` changes audited |
| C-DOM-022 | architect | PASS — 6-month review cadence confirmed |
| C-DOM-030, C-DOM-031 | — | **NOT EVALUABLE** — unreplaced `[PLACEHOLDER]` rows |
| C-TECH-002 | dev/architect | PASS conditionally — no runtime secret exists. If ADR-011 selects the shared-secret route, a Key Vault-backed secret environment variable becomes mandatory and Azure Key Vault is out-of-palette with no evidenced subscription |
| C-TECH-003 | architect/dev | PASS — TLS 1.2+ is platform-enforced and not configurable downward |
| C-TECH-007 | dev/pipeline | PASS (design) — TST/ACC `pre_deploy` synthetic-data guard now actually executes (it never did before revision 0.4) |
| C-TECH-010 | build | **DEFERRED** — `pac solution check` has never run; needs an authenticated profile against DEV |
| C-TECH-012, C-TECH-022, C-TECH-023 | dev | PASS |
| C-TECH-013 *(SOFT)* | dev | **WARNING, carried** — the FR-023 placeholder `Compose`. Accurately described; see D-012 for a separate observation about the FR-016 gate |
| C-TECH-020 | dev/build | PASS — `pac` pinned to 2.4.1 and `yq` to v4.44.3 in the composite action. PowerShell module versions remain unpinned with no manifest to audit |
| C-TECH-021 | build/pipeline | **NOT APPLICABLE** — no third-party dependency manifest exists |
| C-TECH-030 | pipeline | **FLAGGED — wording stale under ADR-007.** Intent (immutable artefact, no stage bypass, traceability) is met more strongly by Power Platform Pipelines, but "the artifact produced by the build-agent" no longer describes what is deployed. Needs amendment by the Tech Lead; agents do not edit constraints |
| C-TECH-031, C-TECH-047 | dev/build/pipeline | PASS, with one control genuinely weaker — no `<defaultvalue>` on any environment variable, no connection ID anywhere, no environment URL in any flow (re-verified in both packaged zips). But `pac-import-*.json` are no longer applied by any tool, so C-TECH-047's enforcement is now a human reading a code-reviewed file |
| C-TECH-032, C-TECH-033 | pipeline | PASS forward-looking — Deployment Summary required; `rollback_artifact` empty for 1.0.0.0 with the fix-forward route documented and correctly reasoned |
| C-TECH-041 | dev/pipeline | PASS — four new tenant prerequisites added behind `APPROVE TENANT`, including the Managed Environment licence cost |
| C-TECH-043 | architect/dev | PASS — three environment-scoped deploy registrations, each an application user in its own environment only, each requesting only Dataverse `user_impersonation` |
| C-TECH-044 *(SOFT)* | dev/pipeline | **RESOLVED** — OIDC federated credential; no client secret anywhere in the delivery path |

### 5.3 Compliance checklist verification

`knowledge/domain/compliance-requirements.md` **is an unpopulated placeholder template** in this
repository — it still carries `[YOUR DOMAIN]` and `[PLACEHOLDER]` headings and defines no controls.
**Noted once, per the standing convention in this feature's document set** (SDD OQ-029, carried
through the TAD and Dev Summary). No project-specific domain control could be applied on top of the
universal set, so the SDD and TAD are treated as the authoritative compliance source.
`knowledge/technology/testing-tools.md` and `knowledge/technology/security-model.md` **are**
populated and were applied — the latter supplied the group-team verification queries used above.

| Universal control | Status at test gate |
|---|---|
| Personal data identified and classified | ✅ SDD §7.1 / TAD §3; every revision 0.2 column classified in-place |
| Lawful basis documented | ✅ SDD §7.2 per entity |
| Data minimisation | ✅ Age band and region derived at intake; ethnic group not collected; FR-016 verified independently |
| Retention defined + automated deletion | ◐ Four jobs scripted; 6-year rule deferred with no class unprotected. Health free-text retention basis is **DPO decision OQ-006, open** |
| Personal data not written to logs | ✅ Verified structurally and behaviourally (C-DOM-004) |
| Encryption in transit / at rest | ✅ Platform-enforced; TLS 1.2+ not configurable downward |
| SAR path exists | ❌ **No mechanism exists or is agreed** (C-DOM-005, A-R22) — accepted open item, still open |
| Right-to-erasure path exists | ◐ Designed; helper flow is Phase 4. Cascade verified present in the package |
| Privacy impact assessed | ❌ **DPIA is a concept draft, sign-off table empty** (Art. 35 go-live gate, OQ-030) |
| CRUD on sensitive entities logged + record content | ✅ (design) C-DOM-010 / C-DOM-011 |
| Tamper-evident audit log | ✅ Append-only by construction; audit administration separated from application administration |
| Audit retention ≥ policy minimum | ✅ 2192 days |
| Least privilege | ✅ Two narrow roles; 34 columns behind the profile |
| Role assignments documented and reviewed | ✅ TAD §6.1; 6-month cadence |
| Privileged actions require elevated authorisation | ✅ Gated `post_deploy` |
| MFA for privileged access | ⛔ **Tenant-level; the unattended-flow CA exception is unconfirmed** (WBS 0.3) |
| Session timeout | ◐ Derived at 8 hours, never confirmed |
| Change management via pipeline | ✅ ADR-007, two-hop chain |
| Dependency / supply chain | ✅ `pac` and `yq` pinned; no third-party manifest exists |

---

## 6. Provisioning Verification

Every TAD §12 item and §6.1 mapping row. **The `Verified Via` column states what was actually done.**
No Graph or Dataverse Web API query could be executed — there is no environment to query — so every
row that requires one is **BLOCKED**, not passed.

| Item (TAD §12 / §6.1) | Expected | Verified Via | Result |
|---|---|---|---|
| `rev-GrantAutomation-DEV` / `-TSTACC` / `-PROD` environment security groups | 3 Entra groups | Script + settings review — `ensure-groups.ps1` creates the environment gate group per env | ⛔ **BLOCKED** (Graph `GET /groups`) |
| `rev-Admins-*`, `rev-ServiceAccounts-*` role groups | 2 of the 4 TAD role groups | Script review — `rev-Finance-*` / `rev-Trustees-*` **deliberately not created**; no Phase 1 table is reachable by either persona. Confirmed correct: neither role exists in the solution | ⛔ **BLOCKED** |
| `svc-grantautomation` service account + **scoped Conditional Access exception** | Entra user, licences, MFA, scoped CA exception | `logs/routing.log` 2026-08-10 22:21 — interactive sign-in confirmed; device-code/public-client CA-blocked | ⛔ **OUTSTANDING AND BLOCKING** (SDD OQ-018, A-R13) |
| 3 deploy app registrations, one per environment, one federated credential each, no client secret | 3 registrations + 3 Dataverse application users | Settings-file review — subjects are `repo:…:environment:<dev\|tst_acc\|prd>`; the previously broken `ref:refs/heads/main` subject is corrected in all three files | ⛔ **BLOCKED** |
| `rev-grantautomation-provisioning` app registration + admin consent | `Group.Create`, `GroupMember.ReadWrite.All`, `Sites.Selected` | Script review — `Sites.Selected` scoped to `/sites/grants`; permission GUIDs are deliberate `{{PLACEHOLDER}}` tokens with fail-fast | ⛔ **BLOCKED** |
| **Pipelines host environment (custom, not platform host)** | Dedicated production env, UK region, Pipelines app installed | `pac admin list` — **does not exist** | ⛔ **NOT PROVISIONED** |
| **Pipeline + two stages** | Environment records + `REV Grant Automation Standard` with two chained stages; redeploy-previous-versions enabled | Config review — `PIPELINE_STAGE_ID` indirection present per GitHub Environment | ⛔ **NOT PROVISIONED** |
| **Managed Environment status on TST/ACC and PRD** | Premium use rights on both targets | Config review — declared in `tenant_prerequisites` with the cost called out | ⛔ **NOT PROVISIONED — licence cost unconfirmed with Revitalise** |
| Pipelines access assignment | `Deployment Pipeline Administrator` in the host | Config review | ⛔ **NOT PROVISIONED**; whether a service principal may *request* a promotion remains undocumented |
| DEV + TST/ACC + PRD environments, UK region, Dataverse enabled | 3 environments | `pac admin list` — **only "Default" exists** | ⛔ **NOT PROVISIONED (WBS 0.2)** |
| UK residency verification (environments, AI Builder, DocuSign, QBO) | Written evidence retained | — | ⛔ **BLOCKED** (NFR-009, DPIA A5, risk A-R19) |
| Environment DLP connector policy | Business/blocked groups per §6.4 incl. Request/HTTP and Word Online | Source review — only 3 connectors referenced, all in the business group | ⛔ **BLOCKED** (live policy check) |
| AI Builder credit assignment | Capacity on PRD | — | ⚪ **N/A Phase 1** — no AI Builder connector referenced |
| SharePoint `/sites/grants` + Signed Acceptances library | Site + library, Trustee denied | `ensure-site.ps1` present and parses | ⚪ **N/A Phase 1** — Automation #3 |
| Azure Key Vault + secret env var | Only if ADR-011 keeps the webhook | — | ⚪ **NOT REQUIRED as built** — the Entra OAuth route uses no secret. **ADR-011 still open** |
| Purview basic retention labels | Backstop labels | — | ⛔ **BLOCKED** (out-of-palette, manual) |
| Group teams `REV Admins` / `REV Service Accounts` + role bindings **by name** | 2 group teams, roles looked up by name | ✅ **Script reviewed and parsed** — `bind-roles-to-groups.ps1` uses `teamtype: 2` (AAD Security Group) and resolves roles by name because GUIDs differ per environment | ✅ **PASS (source)** / ⛔ live BLOCKED |
| Column security profile membership | Both group teams added to `REV_TrusteeRestricted` | ✅ **Script reviewed** — adds **teams**, never users; reads current membership first; probes `teamprofiles_association` then `teamprofiles` with an actionable failure if neither resolves | ✅ **PASS (source)** / ⛔ live BLOCKED |
| Environment + table auditing, retention 6 years | All four tables, 2192 days | ✅ **Script reviewed** — sets organisation `isauditenabled` **and** `auditretentionperiodv2` (correctly noting table auditing has no effect while the org switch is off), then table-level via the metadata endpoint | ✅ **PASS (source)** / ⛔ live BLOCKED |
| Recurring bulk-delete jobs ×3 + orphaned-Applicant sweep | 4 monthly jobs, status-plus-date queries | ✅ **Script reviewed** — four jobs; the withdrawn/incomplete job joins to `rev_applicant` for the accurate `rev_lastcontactdate` rule, with the `rev_submittedon` approximation recorded in-script *as an approximation* | ✅ **PASS (source)** / ⛔ live BLOCKED. `QueryExpression` serialisation remains unexercised |
| App sharing — MDA to `REV Admins` / `REV Finance` | Role association | ✅ `share-apps.ps1` associates `rev_grantadministration` with the two existing roles | ✅ **PASS (source)** / ⛔ live BLOCKED |
| Connection references bound to service-account connections | `rev_SharedDataverse`, `rev_SharedTeams`, `rev_SharedOutlook` | ✅ All three present in `Other/Customizations.xml`, **verified present in both packaged zips**, with no connection ID | ✅ **PASS (source)**. Binding is interactive OAuth — not scriptable, and blocked on WBS 0.3 |
| 🆕 **Global option sets** (revision 0.8) | `rev_agreementresponse` created; `rev_likertresponse` gains value 6 | ✅ **Re-verified at the second retest.** 16 option-set files on disk, **16 `<optionset>` and 36 `RootComponents` inside both fresh and both stored zips** (was 15 / 35). `verify-solution-root-components.py` → PASS, both directions. `rev_wellbeinganswer8/9/10`'s `<attribute>` blocks genuinely reference `rev_agreementresponse`; `1`–`7` still reference `rev_likertresponse`. The three rebound attributes keep `IsAuditEnabled=1` | ✅ **PASS (source + package)** / ⛔ live import BLOCKED |
| `rev_setting` seed rows | ~~10~~ **11 rows** | ✅ **Re-counted at retest in both settings files — 11 rows each.** **⚠️ Re-counted again at the second retest: still 11 rows each — revision 0.8 changed a row's *value*, not the count.** `LikertPointMap` is now `{"1":5,"2":4,"3":3,"4":2,"5":1,"6":0.5}`, **byte-identical between the two files** and with **no second map anywhere**, so the one-map-serves-both-scales claim holds. `MaxCircumstanceScore` correctly still 60. `AgeRangeLabelMap` added for D-003 and **byte-identical between the two files**, correctly grouped with the reference maps rather than the board criteria, so it carries no `{{PENDING}}` token. TST/ACC still carries provisional 20 / 21–30 / 25000; **PRD still carries `{{PENDING_OQ_001/002/003}}`** with `Assert-NoPlaceholder` aborting before any write | ✅ **PASS (source)** — see D-011, still open (`{{PENDING_OQ_002}}` on both band bounds) |
| 🆕 **Intake caller identity** — `rev-wordpress-intake` app registration + service principal, Microsoft Flow Service `User` permission | 1 registration, 1 service principal, the SP **object** id surfaced | ✅ **Re-verified at retest** — `ensure-intake-client.ps1` exists, AST-parses clean, check-before-create, CREATED/EXISTS/FAILED, `-Env` with `ValidateSet`, **asserts** a pre-existing registration really carries the declared permission (the failure mode that caused D-001), reports credential posture **by count only**, and is wired into `tenant_prerequisites` for both test and prd | ✅ **PASS (source)** / ⛔ live Graph BLOCKED. ⚠️ The declared-delegated / acquired-app-only combination is **flagged in both settings files** as the thing likeliest to fail on first run |
| 🆕 **Intake trigger authentication** — *"Who can trigger the flow?"* = **Specific users in my tenant**, Allowed users = the intake SP object id | Set on both TST/ACC and PRD, **before** the flow is turned on | ✅ **Re-verified at retest** — a named manual `post_deploy` step on both environments, owner **Wanstor (tenant administration)**, exact value specified, ordering made explicit, and the value recorded in the Deployment Summary per C-TECH-041. It is an authoring surface with **no workflow-definition property**, so it cannot ship in the managed solution and cannot be asserted from the flow JSON — correctly handled as specify-own-verify rather than papered over with an invented property | ⛔ **NOT APPLIED — no environment.** Whether the setting survives a solution import is **unverified**, which is why the pipeline configures *and* verifies it on every deployment |
| 🆕 **Intake endpoint auth smoke test** | Executable assertion of C-TECH-006's `Verify By` on both environments | ✅ **Re-verified at retest** — `verify-intake-endpoint-auth.ps1` exists, parses clean, is read-only, and is wired into `smoke_tests` for **both** test (line 515) and prd (line 634). Three checks: no credential → 401/403; the response body is **not** the flow's own `{"error":"unauthorised"}` (proving a platform-level rejection); a bogus bearer token is also rejected. Discriminator regex and the flow's actual 401 body compared directly — they agree, and a test asserts the coupling. Probe payload is synthetic, omits the client-id header and is incomplete against `required`, so no outcome can write a row | ⛔ **NEVER EXECUTED — §8 item 1, the highest-priority deferred case in the release** |
| DocuSign / QuickBooks / WordPress form / licences | External | — | ⚪ **N/A Phase 1** (except the WordPress form, which is Automation #1's specification — see §2.1) |
| **§6.1 persona mapping** — Process owner, Service identity | 2 of 6 rows in Phase 1 scope | ✅ Roles exist as solution components with **no user assignment inside the solution**; `verify-role-bindings.ps1` asserts no direct assignments in test/acc/prd; `allowedDirectRoleAssignments` is `[]` in both settings files | ✅ **PASS (source)** / ⛔ live `systemuserroles_association` query BLOCKED |
| **§6.1** — Finance, Trustee, Maker, Platform admin rows | 4 rows | Correctly out of Phase 1 scope | ⚪ **N/A Phase 1** |

---

## 7. Gates above this test run (not test failures — recorded so they are not lost)

None of these is a defect in what was built, and none of them can be closed by testing. All three
sit above deployment.

1. **DPO decisions OQ-004 / OQ-005 / OQ-006 remain unrecorded.** ADR-002 — field-level column
   security as the trustee anonymisation control — is `Adopted (conditional)` on OQ-004. The profile
   is built and correct; **the basis on which it was built is not signed off.** OQ-005 (does automatic
   rejection at the threshold satisfy Revitalise's DUAA 2025 position) bears directly on FR-014, which
   this run verified as working exactly as designed — if the DPO requires stronger human review, the
   *design* changes, not the code.
2. **The DPIA and RoPA are unsigned concept drafts** with an empty sign-off table (TAD risk A-R21,
   SDD OQ-030). UK GDPR Art. 35 requires the DPIA to be complete before go-live. **PRD deployment
   cannot proceed on this basis regardless of any test result.**
3. **Board criteria OQ-001 and OQ-003 are unanswered. OQ-002 is now resolved by evidence.** PRD
   `rev_setting` seeding is blocked by design and `Assert-NoPlaceholder` enforces it.
   **⚠️ Updated at revision 4.** OQ-002 — the exact scoring methodology — is settled: 25 real
   hand-scored applications reconcile exactly, and the reconciliation is asserted permanently against
   the shipped artefacts. **OQ-001 is not, and it never could have been from this data** — the CSV
   holds scores and answers but **no accept/reject outcomes**, so no cut-off can be inferred. The fix
   cycle was commissioned as "resolve OQ-001" and A-01 corrects that scoping itself. Two things the
   board now needs that it did not have: the scale is **5 to 60**, not 10 to 60, so a knockout
   threshold at or below 5 is reachable where it was not; and **whatever threshold is chosen, D-015
   makes the boundary behave differently from the approved rounding rule** — so OQ-001 should not be
   answered against the current build's arithmetic.
   **⚠️ Updated at revision 5.** The second of those two caveats is **withdrawn — D-015 is fixed and
   verified.** The build's boundary arithmetic now matches the approved rule at every midpoint, so
   **OQ-001 can now be answered against the current build.** The first caveat stands unchanged and is
   the one that still matters: **the scale is 5 to 60, not 10 to 60.** A knockout threshold at or below
   5 is reachable, and the half-point cases now round *toward* the applicant, which is a substantive
   fact for the board to know before it picks a cut-off rather than after. **OQ-001 and OQ-003 remain
   unanswered, and no data in this repository can settle them** — the CSV holds scores and answers but
   no accept/reject outcomes.

---

## 8. Deferred Test Execution — what must run once DEV/TST-ACC exists

Recorded precisely so this is a work list, not a caveat. **Nothing below has been run.** The Dev
Summary §9 guidance is a good set and is largely adopted; the additions marked ➕ are cases this run
identified that §9 does not cover.

**Prerequisite chain — in this order, or the rest is untestable:**
1. Provision DEV, TST/ACC, PRD (WBS 0.2) — UK region, Dataverse enabled, capacity confirmed (A-R18).
2. **Close WBS 0.3**: the service account's scoped Conditional Access exception for *unattended*
   sign-in. All four flows run unattended as that account; without it they cannot be relied on at all.
3. Run `pac solution check` (C-TECH-010) and the **first managed import** — expect to iterate on the
   items the packer cannot validate: the 17 platform privilege names in each role file, the two
   calculated-column `<SourceType>`/`<Formula>` forms, `rev_applicantid@odata.bind` casing, the
   `runas` numeric, and alternate-key retrieval syntax.
4. Bind the three connection references (interactive OAuth — not scriptable) and activate the flows.

**Then, by layer:**

| Layer | Cases | Notes |
|---|---|---|
| **Security — highest priority** | Read all **34** secured columns as a non-profile-member **via the Web API, not the UI** — each must return null. ➕ Read `rev_firstname` as a non-member and confirm null (proving the calculated `rev_fullname` was not secured as theatre). Confirm `rev_breaklocation` reads **successfully** for a non-member (the one reviewed exemption). Query `systemuserroles_association` for zero direct assignments. ➕ **POST to the intake endpoint with no credential at all and assert rejection before the definition runs (D-001).** ➕ POST with a *valid* client-ID header from an unauthenticated context and record what happens | The point of ADR-002 is that export and API cannot bypass column security. Only a live read proves the platform honours it |
| **Integration** | Intake happy path → 201 + `REV-2026-nnn`; replay → 200, exactly one row, original status preserved; unauthorised → 401, no write, no Teams alert, run `Cancelled`; incomplete → 400 + one `Warning` error row with no personal data; Teams-connection failure → still 201; concurrency (two simultaneous POSTs, same applicant) → **one** applicant row; `O'Neill` OData escaping; ➕ calculated `rev_costs` with `other_cost` omitted → 720.00 not null (**the one behaviour the design assumes and has not proved**); ➕ attempt to PATCH `rev_fullname` directly → platform rejects | 14 cases |
| **End-to-End** | All 10 wellbeing answers at `1` + life satisfaction `0` → **60** (the single most important scoring assertion); all at `5` + `10` → **10**; ➕ life satisfaction `0` **scores** rather than going to Under Review; all eleven inversion values 0–10 one point apart with no missing-key failure; ten distinct values mapping to the right questions in the breakdown; FR-014 boundaries at exactly knockout / lower / upper; misconfigured band; FR-022 with one wellbeing answer omitted, then with only the feeling answer omitted; FR-018 override → no write at all; FR-017 threshold change → new outcome with no redeployment, change visible in `rev_setting` audit history; FR-016 identical scores across all twelve special-category columns **including the two benefit columns**; FR-015 each band → flag 1/2/3; FR-020 view membership; missing `LikertPointMap` → fail-closed at Submitted; ➕ zero hits for `wellbeinganswer11` in run outputs *and* stored breakdown | 26 cases |
| **Provisioning** | Every §6 row marked BLOCKED, via Graph and the Dataverse Web API. Run each `post_deploy` script **twice** and confirm the second reports EXISTS and exits 0. Confirm organisation audit retention reads 2192 days. Create/update/delete a row on each of the four tables and confirm the audit record carries all five C-DOM-011 fields. Orphan sweep: applicant + one application, delete the application, run the job → applicant deleted (risk A-R10). `seed-settings.ps1 -Env prd` with a pending token → aborts before any write | 21 cases |
| **Accessibility** | ⚠️ **Rewritten 2026-08-13 — this row's premise was wrong.** There is nothing to wait for: **the form is live and can be audited today**, and it does not depend on any environment being provisioned, which makes it the one deferred layer that is not actually blocked. Required: **axe-core across all 20 pages plus an error state**; manual keyboard-only completion and submission of the whole form; **NVDA + Chrome and VoiceOver + Safari** passes covering a conditional reveal, the two Likert matrices on page 11, the error summary and the progress indicator; greyscale pass; contrast measurement of every text/background pair, control border and focus indicator; 200% zoom and 320px width on every page; a real Android and a real iOS device. **Two failures are already confirmed without any of that** — 1.3.5 (`autocomplete`) and 3.3.7 (confirm-email) — so remediation can start on those now. See spec §10 and **OPEN-26** | 8 cases; **not environment-blocked** |
| **Performance** | Nothing measurable to test. **Do not invent a threshold.** Close SDD OQ-020/OQ-021 first, then baseline intake latency, single-row scoring, and the daily summary at 250 applications/year | 4 cases, blocked on OQ-020 |
| **Regression** | ~~No suite exists.~~ **A suite exists and runs — 537 tests, 92.60% coverage, D-005 closed.** What it does **not** cover, and what must be added once an environment exists: any flow *execution*, column-security enforcement, audit-record shape, connection binding, and the live 401. Add a regression case for each P2 as it closes — D-001, D-003 and D-005 each need one that would fail if the fix were reverted (D-003's already exists and demonstrably works: it failed the moment the required list changed) | Suite green; **environment-dependent regression still absent** |

**➕ Added at the retest, 2026-08-13 (report revision 3) — in priority order:**

| # | Case | Why it is first / notes |
|---|---|---|
| **1** | **POST to the intake endpoint with no credential and assert 401/403, and assert the body is NOT `{"error":"unauthorised"}`.** Then repeat with a syntactically valid but bogus bearer token. `verify-intake-endpoint-auth.ps1 -Env test\|prd` is written, wired and ready — it has simply never run against anything | **The single most important deferred case in the release.** It is the only thing standing between "C-TECH-006 is provisioned" and "C-TECH-006 is enforced". **PRD must not receive the endpoint URL before this passes** — the pipeline says so and it is right |
| **2** | **Read the trigger's *Allowed users* field back after saving it**, on each environment | Not automatable. A blank field silently means "any user in my tenant", and no test can see it. This is the one residual in D-001's remedy that stays human forever |
| **3** | **D-014: submit "Not sure" on each of wellbeing answers 8, 9 and 10 and record what actually happens** — does Dataverse reject the picklist value, does the run 500 with `retry: true`, and does the retry loop? Then submit `7.5` for the life-satisfaction answer | Predicted from source but **unproven**. This is the case that decides whether D-014 loses applications or merely fails a run, and it can be run the moment DEV exists |
| **4** | **D-014 interim guard, once added:** confirm an out-of-range scored answer produces a clean 400 (or routes to Under Review) rather than a 500 retry loop, and that the widened FR-022 gate treats "unmappable" exactly as it treats "missing" | The regression case that keeps the fix honest |
| **5** | **Rename an age-band label in `AgeRangeLabelMap` and confirm what the process owner sees.** Expected today: every subsequent applicant silently becomes `rev_agerange` = 9 (Not known), no error, no alert | The §2.2 P4. Cheap to test, and it establishes whether a quiet configuration failure is acceptable |
| **6** | **Confirm `AgeRangeLabelMap` is actually seeded before the intake flow is turned on.** The intake now reads **three** `rev_setting` rows at run time, not two; a missing row fails every submission | Ordering hazard, not a code defect. `seed-settings.ps1` is data-driven and will seed it — but PRD seeding is itself blocked on OQ-001/002/003 |
| **7** | **Run the whole Pester suite in CI**, on a committed branch, and confirm the secret-scan step covers the solution source once `--no-git` is added (D-006) | Locally the suite passes and the scan is clean; neither has been proven in the CI context the config describes |

**➕ Added / revised at the second retest, 2026-08-13 (report revision 4).** Items 3 and 4 above are
**superseded** — D-014 is fixed, and "Not sure" is a valid answer rather than a value to reject, so the
case is no longer "does it lose the application" but "does it score correctly". Item 7's `--no-git`
half is **done and verified**; its CI half stands.

| # | Case | Why it matters / notes |
|---|---|---|
| **3′** | **Submit "Not sure" on an ODD number of wellbeing answers and read back `rev_circumstancescore`, `rev_status` and `rev_scorebreakdown` together.** The decisive case: exact total **20.5** with `KnockoutThreshold 20` / band `21–30`. Expected under the approved rule: stored **21**, status **3 Borderline**, breakdown showing `Exact total before rounding = 20.5` and `Rounded to 21`. **Predicted from the shipped expression: stored 20, status 4 Auto-reject, and a breakdown that claims halves round up.** Then repeat with an **even** number of "Not sure" answers and confirm no rounding sentence is printed | **This replaces item 3 as the highest-priority scoring case.** It is the direct live test of D-015 and it settles the rounding-mode question that no local test can. It also settles the P4 float-versus-int `equals()` question in `Compose_score_breakdown` in the same run |
| **4′** | **Confirm the widened FR-022 gate treats "unmappable" exactly as it treats "missing"** — set a wellbeing answer to a value with no `LikertPointMap` key (e.g. by removing key `"6"` from the seeded row), and separately set the life-satisfaction answer outside `0`–`10`. Both must route to status 5 with no score, not throw | The regression case that keeps D-014's fix honest. The gate is now the control that makes every *future* configuration change safe, so it is worth more than the immediate fix |
| **8** | **Submit "Not sure" on one of the seven SWEMWBS answers** and record whether the live form even offers it | **D-016.** Settles which of the two contradictory observations is stale — revision 3's 7 × 5 input count, or CSV row 25's all-ten "Not sure" application. Cheap, and it feeds the M-02 / D-008 option-set decision |
| **9** | **Read `rev_scorebreakdown` as a trustee would, on a record with a "Not sure" answer**, and confirm it is intelligible | The breakdown emits `response 1 = 5 points` — a bare option value, no label. It is the artefact the charity relies on to justify a decision about a person, and nobody has read one yet |
| **10** | **Confirm `rev_circumstancescore` accepts the new floor.** A fully answered all-"Not sure" application scores **5** (was 10). Confirm the column stores it and no view, filter or aggregation assumes a minimum of 10 | The floor moved and the board needs the figure for OQ-001. Verified statically; never stored |

**➕ Revised at the THIRD retest, 2026-08-13 (report revision 5).** Item **3′ is unchanged in priority
but changed in purpose, and its expected result has flipped.** Items 1, 2, 4′, 8, 9 and 10 stand exactly
as written. Item 7's CI half still stands; its `--no-git` half remains done.

| # | Case | Why it matters / notes |
|---|---|---|
| **3′ (revised)** | **Submit "Not sure" on an ODD number of wellbeing answers and read back `rev_circumstancescore`, `rev_status` and `rev_scorebreakdown` together.** The decisive case is still an exact total of **20.5** with `KnockoutThreshold 20` / band `21–30`. **Expected — and now predicted from a fix verified by execution: stored 21, status 3 Borderline, breakdown showing `Exact total before rounding = 20.5` and `Rounded to 21`.** Then repeat with an **even** number of "Not sure" answers and confirm **no** rounding sentence is printed | **Its purpose has changed.** At revision 4 this case existed to settle *which* rounding the runtime performs. It can no longer overturn the arithmetic — **the fix is correct under both .NET midpoint modes and both numeric types**, so there is no runtime behaviour left for it to adjudicate. What it now proves is narrower and still necessary: **that the expression evaluates at all in the Power Automate runtime**, that `formatNumber` is bound to the formatter tested here, and — in the same read — **D-018(c)**, the `float`-versus-`int` `equals()` that decides whether the breakdown claims rounding was applied. Still the highest-priority scoring case |
| **11** | **Read `rev_scorebreakdown` for a whole-number total and confirm it does NOT say "Rounded to …".** `Compose_score_breakdown` decides this with `equals(Calculate_circumstance_score, Round_the_circumstance_score)` — a `float` against an `int`. If Logic Apps does not coerce, **an unrounded total is told it was rounded**, in the artefact the charity uses to justify a decision | **D-018(c).** Covered by 3′'s even-number half; called out separately because it is the failure that would go unnoticed — the sentence is plausible either way, and only a reader who knows the total was whole would spot it |
| **12** | **Read `rev_scorebreakdown` for a total containing a `.5` and confirm the wellbeing subtotal renders sensibly.** `string(variables('likertPoints'))` on a `float` may render a whole subtotal as `35` or `35.0` | **D-018(b).** Cosmetic, in a trustee-facing document, and free to check inside case 3′ |

---

## 9. Recommendations

### 9.000 Rewritten at the THIRD retest, 2026-08-13 — read this instead of §9.00, §9.0 and §9.1 below

Items 1 and 2 of §9.00 are **done and verified**. Six remain, and **the top of the list is no longer a
development task** — for the first time in this feature's history.

| # | Do this | Owner | Why now |
|---|---|---|---|
| **1** | **Commission the accessibility audit (D-004, spec OPEN-26).** axe-core across all 20 pages plus an error state; keyboard-only completion and submission; NVDA + Chrome and VoiceOver + Safari covering a conditional reveal, both Likert matrices, the error summary and the progress indicator; greyscale; contrast measurement of every text/background pair, control border and focus indicator; 200% zoom and 320px reflow; a real Android and a real iOS device | **reviewer to commission** | **This is now the top item because everything above it has been closed.** It has been the same recommendation in **four consecutive reports** and has still not started. It is **not blocked on anything** — the form is live and taking applications from disabled people today. Two criteria are confirmed failures; **nine have been assessed by nothing at all.** The `autocomplete` remediation alone is small and bounded. It is the highest-human-consequence open item in the release and the one nobody has picked up |
| **2** | **Answer D-002 / M-04:** is gating the financial questions on benefit status intended? If yes, the scoring configuration must treat an absent income band as "qualifies on benefit status" rather than as missing data | **Emily**, then the scoring configuration | **Open and unmoved since report revision 1 — five revisions.** Left as it is, every benefit-receiving applicant routes to manual review, which inverts the purpose of the programme. **This and item 1 are now the only two open P2s, and neither is a developer's to close** |
| **3** | **Route SDD Amendment A-01 to plan-agent** for a re-issued SDD revision and a re-gate, and give it a date. It resolves **OQ-002** and explicitly does **not** resolve OQ-001 — do not let the two be conflated again | lead-agent → plan-agent | Unchanged. The substance of D-009 is shipped and verified; the approved requirement text still contradicts the build. **Approving this test report does not approve A-01** (§4.3) |
| **4** | **Take OQ-001 to the board, with the two facts it did not have.** The scale is **5 to 60**, not 10 to 60, so a knockout threshold at or below 5 is now reachable. And half-point totals now round **up, toward the applicant**, verified at every midpoint | lead-agent → board | **The blocker on doing this is gone.** Revision 4 said OQ-001 should not be answered against the current build's arithmetic because D-015 made the boundary misbehave. D-015 is fixed and verified, so **the arithmetic can now be relied on** — and PRD `rev_setting` seeding stays blocked until OQ-001 is answered |
| **5** | **Confirm or override the 80% coverage threshold** in `coding-standards.md` | Tech Lead / reviewer | Unchanged from §9.00 item 6, and **now asked for the third time**. The constraint passes against a number nobody senior has agreed. It should not become settled by having gone unchallenged three times |
| **6** | **Cheap hardening, one pass:** **D-018(a)** render **labels** rather than bare option values in `rev_scorebreakdown` for values 1–5 (value 6 already reads "Not sure"); **D-018(b)** pin the `float` subtotal's rendering; **D-018(c)** make the rounded-versus-unrounded comparison type-safe; **D-012** drop the `body/` prefix requirement; **D-013** broaden beyond JSON key/value pairs; **D-011** split `{{PENDING_OQ_002}}` into lower/upper tokens and remove the `-Skip`; **D-007** correct the four surviving "122" figures to 118/120; add `postcode` to `IntakeContract.Tests.ps1`'s named escaping assertion | development-agent | All still open, all individually trivial. **D-018 is on this list because it was previously folded into D-015's remedy and would otherwise have closed with it** — see §4.000. `--no-git` and Dev Summary §9 have both left this list, done and verified |
| **7** | **Resolve D-016a — which "Not sure" observation is stale.** Submit "Not sure" on one of the seven SWEMWBS answers and record whether the live form offers it at all | Emily / whoever can exercise the live form | Unchanged in substance, renamed for clarity. It feeds the **M-02 / D-008** option-set decision. **Note that this is *not* what revision 0.9 closed** — that was the "disjoint" wording (D-016b), a different item that shared the label |
| **8** | **Add the `verify-package-contents` build step.** | build-agent | **Fourth report in a row.** It should not depend on a reviewer remembering to open the zip — and this pass is the sharpest illustration yet of why: `pac solution pack` could not be executed here at all, so the *only* verification of package contents available was opening the stored zips by hand. A build step would have made that a recorded fact rather than a manual improvisation |

**Three observations about this pass worth recording, because a defect list will bury them.**

**Revision 0.9 fixed the defect it was given and did the harder thing underneath it.** The minimum
required was making `20.5` round to `21`. What was delivered instead **removes the dependency on .NET's
midpoint mode entirely** — verified here under both `double` and `decimal`, so the expression is correct
whichever numeric type the runtime picks and whichever midpoint mode a future runtime version adopts.
The distinction matters because the *original* defect was not "the wrong rounding mode"; it was
**depending on a rounding mode nobody had executed.** A fix that merely produced the right answers today
would have left that shape intact. This one does not.

**The test that was added is the right kind of test, and it was mutation-tested rather than asserted to
be.** The suite now *executes* .NET's formatter through the offset **parsed out of the shipped
expression**, so deleting the offset changes what the test computes; and `Get-RoundingOffset` **throws**
rather than returning zero if the rounding is ever reimplemented, so the assertions cannot go quiet by
accident. That is the difference between a regression test and a regression test that can regress — and
this gate confirmed it independently instead of taking the claim, because the claim itself is exactly the
kind that D-015 taught this repository not to accept.

**And the pattern this report has been tracking five times has finally broken in the right direction.**
Revisions 3 and 4 each closed defects and each introduced or revealed a new P2 — D-014 inside 0.7's
audit, D-015 inside 0.8's fix. **Revision 0.9 closed three defects and introduced none.** The one thing
this pass found is a bookkeeping risk, not a defect: three P4s that would have vanished with the closure
of the defect they were attached to. **What remains open is what has always remained open** — an audit
nobody has commissioned, a decision nobody has taken, and five test layers with nowhere to run. Those are
not engineering problems, and no further development revision will move them.

### 9.00 Rewritten at the SECOND retest, 2026-08-13 — superseded by §9.000 above

Items 1, 2 and the `--no-git` half of item 6 in §9.0 are **done**. Three of the seven remain, and one
new item goes to the top.

| # | Do this | Owner | Why now |
|---|---|---|---|
| **1** | **Fix D-015 — the rounding.** Change `Round_the_circumstance_score` to `@int(formatNumber(add(outputs('Calculate_circumstance_score'), 0.25), 'F0'))`, or move to integer half-points and `div(add(H, 1), 2)`. **Add a static assertion that the value reaching the formatter can never be a midpoint**, and cross-reference the existing "0.5 is the only non-integer" test in the expression's description so the two cannot drift apart | development-agent | **The only open P2 a developer can close alone, and it is a one-line change.** Today an exact 20.5 is Auto-rejected where the approved rule sends it to Emily, and `rev_scorebreakdown` tells the trustee the opposite. Nothing else in the release is both this consequential and this cheap |
| **2** | **Update Dev Summary §9 (Test Guidance) for revision 0.8 — D-017.** Three invariants describe the pre-0.8 build: "minimum reachable score is 10" (now **5**), the FR-022 gate as emptiness-only, and the `LikertPointMap` invariant scoped to `rev_likertresponse` alone. Add a §9.3 case for the fractional total and the midpoint. Also correct "35 root components" (three places, now **36**), "fifteen global option sets" (now **16**) and `LikertPointMap`'s "Value unchanged in revision 0.3" | development-agent | §9 is the section `agents/test-agent.md` loads on activation. **A future tester following it literally would assert a floor of 10 against a build whose floor is 5 — and fail a correct build.** The shipped suite is right; the guidance is behind it |
| **3** | **Schedule the accessibility audit (D-004, spec OPEN-26).** Unchanged from §9.0 item 3, and unchanged from revision 2 before that. axe-core across all 20 pages plus an error state; keyboard-only completion; NVDA + Chrome and VoiceOver + Safari; contrast measurement; 200% zoom and 320px reflow; real Android and iOS | reviewer to commission | **This has now been the same recommendation in three consecutive reports and it has still not started.** It is not blocked on anything — the form is live. Two failures are already confirmed and the `autocomplete` remediation is small and bounded. Nine criteria have been assessed by nothing at all. It is the highest-human-consequence open item in the release and it is the one nobody has picked up |
| **4** | **Answer D-002 / M-04:** is gating the financial questions on benefit status intended? If yes, the scoring configuration must treat an absent income band as "qualifies on benefit status" rather than as missing data | Emily, then the scoring configuration | **Open and unmoved since report revision 1.** Left as it is, every benefit-receiving applicant routes to manual review, which inverts the purpose of the programme |
| **5** | **Route SDD Amendment A-01 to plan-agent** for a re-issued SDD revision and a re-gate, and give it a date. It resolves **OQ-002** and explicitly does **not** resolve OQ-001 — do not let the two be conflated again | lead-agent → plan-agent | The substance of D-009 is shipped and verified; the approved requirement text still contradicts the build. **Approving this test report does not approve A-01** (§4.3) |
| **6** | **Confirm or override the 80% coverage threshold** in `coding-standards.md` | Tech Lead / reviewer | Unchanged from §9.0 item 5. The constraint passes against a number nobody senior has agreed, and it should not become settled by having gone unchallenged twice |
| **7** | **Cheap hardening, one pass:** **D-012** drop the `body/` prefix requirement; **D-013** broaden beyond JSON key/value pairs; **D-011** split `{{PENDING_OQ_002}}` into lower/upper tokens and remove the `-Skip`; **D-007** correct the three surviving "122" figures to 118/120; add `postcode` to `IntakeContract.Tests.ps1`'s named escaping assertion; render **labels** rather than bare option values in `rev_scorebreakdown` (D-015's P4); **D-016** resolve which "Not sure" observation is stale | development-agent | All still open, all individually trivial. `--no-git` has left this list — **D-006 is done and verified from the config** |
| **8** | **Add the `verify-package-contents` build step.** Unchanged from §9.0 item 7, and this pass re-derived it by hand again — the same uninformative root-component warning printed on both `pac solution pack` runs | build-agent | Third report in a row. It should not depend on a reviewer remembering to open the zip |

**Two observations about this pass worth recording, because a defect list will bury them.**

**Revision 0.8 did the hard, right thing and then tripped on the easy part.** It went and got ground
truth for a scoring methodology that three revisions of documents had only asserted; it proved the
direction of both scales against 25 real applications; it derived a point value rather than choosing
one; it found and fixed two bugs beyond its brief, one of which (`Derive_status`) would have silently
skipped human reviews; and it refused to rewrite an approved SDD it had no authority over, raising a
routed amendment instead — including a correction to the scope of its own commission. **That is the
best-evidenced change in this feature's history.** The rounding is the one step it reasoned about
instead of executing, and it is the one step that is wrong. The lesson is not "trust it less"; it is
that **reasoning and execution are not interchangeable, and this repository has now demonstrated that
five times.**

**And the qualification on §9.1's closing praise can now be lifted.** Revision 3 qualified "the
scoring engine is the strongest part of the release" with "it was never checked against the inputs the
live form actually produces". **It has now been checked, against the charity's own hand-scored
applications, and it reconciles exactly on all 25.** The engine is correct about the right inputs. What
remains is one arithmetic step at the very end of it.

### 9.0 Rewritten at the retest, 2026-08-13 — superseded by §9.00 above

Recommendations 1 and 4 are done. The list that matters now is shorter and differently ordered.

| # | Do this | Owner | Why now |
|---|---|---|---|
| **1** | **Add D-014's interim guard.** Bound the four scored answers in the trigger schema (`minimum`/`maximum`), and widen the FR-022 withhold gate from `empty(…)` to "empty **or** not a key of the map". Two small edits inside the existing design | development-agent | This is the only new P2 and the only one a developer can close alone. It converts a lost application into either a clean 400 or a human review — and it makes every *future* scale change safe, which is worth more than the immediate fix |
| **2** | **Decide the wellbeing scale (M-02).** Either `rev_likertresponse` gains a sixth value with a defined point contribution and `MaxCircumstanceScore` is re-derived, or the form's three "last year" questions move to the five-point frequency scale. Fix **D-009** in the same pass — its stale SDD text is actively concealing the mismatch | Emily + trustee board | Today the same stored number means "None of the time" on seven questions and "Strongly disagree" on three, in one column family, feeding one automated decision about a person |
| **3** | **Schedule the accessibility audit (D-004, spec OPEN-26).** axe-core across all 20 pages plus an error state; manual keyboard-only completion; NVDA + Chrome and VoiceOver + Safari; contrast measurement; 200% zoom and 320px reflow; real Android and iOS | reviewer to commission | **It is not blocked on anything.** The form is live. Two failures are already confirmed and remediation of `autocomplete` alone is small and bounded. Nine criteria have been assessed by nothing at all. Keep it separate from the §7 validation change request |
| **4** | **Answer D-002 / M-04:** is gating the financial questions on benefit status intended? If yes, the scoring configuration must treat an absent income band as "qualifies on benefit status" rather than as missing data — otherwise every benefit-receiving applicant routes to manual review, which inverts the purpose of the programme | Emily, then the scoring configuration | Still the only P2 that has been open since revision 1 without moving |
| **5** | **Confirm or override the 80% coverage threshold** in `coding-standards.md`. A development-agent took a Tech Lead decision because no Tech Lead was available, documented it, and flagged it. It should not become settled by having gone unchallenged | Tech Lead / reviewer | The constraint now passes *against a number nobody senior has agreed* |
| **6** | **Cheap hardening, one pass:** **D-006** add `--no-git` to `build.yml` line 77 (the manifest already claims it); **D-012** drop the `body/` prefix requirement; **D-013** broaden beyond JSON key/value pairs; **D-011** split `{{PENDING_OQ_002}}` into lower/upper tokens and remove the `-Skip`; **D-007** correct the three surviving "122" figures to 118/120; add `postcode` to `IntakeContract.Tests.ps1`'s named escaping assertion | development-agent | All still open, all individually trivial, and D-006 is the one where a document currently claims more than the config delivers |
| **7** | **Add the `verify-package-contents` build step.** This retest re-derived it by hand in seconds, and both `pac solution pack` runs printed a root-component warning that is uninformative in both directions — a real dropped component would print the same line | build-agent | It should not depend on a reviewer remembering to open the zip |

**Unchanged and still above this gate:** the DPIA and RoPA are unsigned concept drafts, so **PRD
cannot proceed regardless of any test result** (§7); the three DPO decisions are unrecorded; WBS 0.2
and 0.3 are unprovisioned; and C-TECH-030's wording and
`knowledge/domain/compliance-requirements.md` remain their owners' to fix.

### 9.1 Original recommendations, retained for the record

**Before this release goes anywhere near an environment:**

1. ✅ **DONE at the retest.** ~~Close D-001.~~ Add a named TAD §12 / `tenant_prerequisites` item for
   intake trigger authentication — who configures it, to what value, verified how — and add the
   no-credential smoke test. **All of that now exists and was verified from source; only the live
   execution remains (§8 item 1).**
2. ✅ **D-003 is done (2026-08-13), and it was worse than recorded.** The six-field required list was
   internally consistent and externally wrong: the live form never sends a date of birth and does not
   always send an email address, so **the intake would have rejected every real submission with a
   400**. Required is now the four fields the live form always collects; `age_range` is accepted and
   mapped through a new `AgeRangeLabelMap` configuration row; `group_linkage` is no longer accepted;
   two expressions that would have thrown on an absent value are null-guarded. **D-002 is still
   open**, on a corrected basis — the live form gates the financial questions on **benefit status**,
   not income band, and whether that is intended is Emily's decision (mapping gap M-04).
3. ◐ **D-004 is half done, and the half that is left needs an audit nobody has run.** The specification
   half is addressed: the form document now records exactly which criteria were checked, how, and what
   the result was, and makes no conformance claim beyond that. **1.3.5 is confirmed as a real failure**
   on the live form — zero valid `autocomplete` tokens across 251 inputs — and **3.3.7 is a second
   confirmed failure** (two confirm-email boxes) that D-004 did not name. **The remaining nine criteria
   have not been assessed by anything.** Schedule the axe-core and manual pass (spec **OPEN-26**); it
   is not blocked on any environment, because the form is live. Until it runs, NFR-024 stays PARTIAL.
   **Keep this separate from the validation change request** — the current ask of Alex is
   validation and completeness (spec §7), and bundling an unaudited accessibility list into it would
   dilute both.

**Governance / ownership items that are not development-agent's to fix:**

4. ✅ **DONE at the retest** — but see 9.0 item 5: the decision was taken by development-agent, not a
   Tech Lead, and needs confirming. ~~**C-TECH-014 needs a decision from the Tech Lead**~~ (D-005): set a coverage threshold appropriate to
   declarative Power Platform artifacts, or record the constraint as not applicable to
   solution-source-only releases with reasoning. Either way, the eleven provisioning scripts are real
   PowerShell with real branching and should get Pester coverage — they are the least-tested and
   most privileged code in the release.
5. **C-TECH-030's text needs amending by its owner** to name the pipelines host as an acceptable
   artefact store. Until then pipeline-agent will read a `Verify By` it cannot satisfy literally.
6. **Populate `knowledge/domain/compliance-requirements.md`**, or record explicitly that this project
   runs on the universal control set alone. Four agents have now noted the same gap (SDD OQ-029).

**Cheap hardening, worth doing in the same pass:**

7. **D-006**: add `--no-git` to the `secret-scan` gate. **D-012**: broaden the FR-016 gate beyond the
   `body/` access form. **D-013**: broaden `no-hardcoded-thresholds` beyond JSON key/value pairs.
   **D-011**: split `{{PENDING_OQ_002}}` into distinct lower/upper tokens. **D-007**: correct the
   audit count to 118/120. **D-009**: amend SDD FR-013's label list.
8. **Add the `verify-package-contents` step** the Dev Summary §8 recommends. This run reproduced it by
   hand in seconds and it is the only check that would have caught four of revision 0.5's six silent
   defects on day one. It should not depend on a reviewer remembering.

**What is genuinely good here, and worth saying because it should not be lost in a defect list:**

The scoring engine is the most safety-critical component in Phase 1 — it produces an automated
outcome about a person in vulnerable circumstances — and it is the strongest part of the release.
FR-016 holds structurally rather than by intention. FR-022's zero-versus-null discrimination is
correct in the one place where getting it wrong would make *worst possible wellbeing* look like *no
answer*. FR-018's override guard is the first action with no path to a write. FR-014 evaluates
knockout before the band so a misconfigured band cannot pass a knocked-out application. Not one
threshold is a literal. Every one of those was verified by reading the definition, not the comment,
and every one held.

**Qualified at the retest, and the qualification matters.** All of that is still true, and D-014 does
not contradict any of it: the engine is correct about the inputs it is given. What the retest
established is that **it was never checked against the inputs the live form actually produces**, and
for three of the ten wellbeing answers it does not receive what it expects. That is the same failure
shape as D-003 — a contract verified against a document instead of against the world — and it is
worth saying plainly, because "the strongest part of the release" and "verified against the wrong
scale" are both true at once, and only one of them was in this report before today.

**And two things about revision 0.6 and 0.7 that deserve saying, because a defect list will bury
them.** Revision 0.7 found a bug that would have rejected 100% of real applications, and it found it
by going and reading the live form's HTML rather than by trusting three revisions of a document that
agreed with itself — which is exactly the discipline this repository has needed. Revision 0.6's smoke
test does not settle for asserting a status code; it asserts the rejection came from the platform and
not from the application's own gate, which is a genuinely subtle distinction and the only version of
that test worth having. **And revision 0.7 refused to close D-004, refused to renumber the option
sets, and said so.** Declining to close a defect that cannot honestly be closed is the behaviour that
makes the rest of the record trustworthy.

---

## Approval

**Reviewed by:** Xander Lykopoulos  **Date:** 2026-08-14  **Response:** `APPROVED` — proceeding to Pipeline with D-002 (Emily's decision) and D-004 (accessibility audit) explicitly tracked as open, non-blocking items. Constraint gate is PASS; neither is a HARD violation.

**Retest, 2026-08-13 (report revision 3) — result: PARTIAL.** Constraint gate **PASS** (was BLOCKED).
D-001, D-003 and D-005 closed and independently verified. **Three P2 defects open: D-002 (Emily's
decision), D-004 (audit never run), D-014 (new, raised by this retest).** Five of nine test layers
remain unexecutable with no environment, and PRD is separately barred by the unsigned DPIA.
Approving this gate means accepting those three open P2s and the untestable layers — it does not mean
they have been discharged.

---

**Second retest, 2026-08-13 (report revision 4) — result: PARTIAL.** Constraint gate **PASS**,
unchanged, on fully re-executed evidence.

**Closed and independently verified: D-014 and D-006.** The scoring formula was re-derived from
`docs/Import/Book(Sheet1).csv` from scratch and reproduces all **25 / 25** real applications exactly,
with the point mapping the unique survivor of 14 400 candidate permutations and "Not sure" = 0.5 pinned
uniquely by row 25. The `int()` → `float()` cast, the single shared `LikertPointMap`, the `Derive_status`
reordering, the life-satisfaction gate, the option-set split and the trigger bounds are all real and all
present inside both packed zips. `gitleaks --no-git` is genuinely in the config and runs clean from it.
560 Pester tests pass at 92.60% coverage and both `pac solution pack` types succeed.

**Three P2 defects open: D-002** (Emily's decision, unmoved since revision 1), **D-004** (accessibility
audit still never run, still not blocked on anything, third report in a row), and **D-015 — new, and
found inside the D-014 fix.** `Round_the_circumstance_score` uses `formatNumber(…,'F0')`, which rounds
half **to even**, not half **up** as the reviewer approved and as `rev_scorebreakdown` tells the
trustee. With the TST/ACC values in force an exact 20.5 is stored as 20 and **Auto-rejected** where the
approved rule sends it to Borderline human review. Two new lower-severity defects are also recorded:
**D-016** (P4 — the ground truth contradicts revision 3's own count of which questions offer "Not
sure") and **D-017** (P3 — Dev Summary §9 test guidance was not updated for revision 0.8 and three of
its invariants now describe the pre-0.8 build).

**Still true, and not softened:** five of nine test layers cannot be executed because no Power Platform
environment exists; the accessibility audit has never been run; OQ-001 remains a board decision that
the ground truth explicitly cannot settle; SDD Amendment A-01 is `PROPOSED` and needs plan-agent, so
D-009 cannot be closed here; and **PRD is separately barred by the unsigned DPIA regardless of any test
result.**

**Approving this gate means accepting D-002, D-004 and D-015 as open, and accepting that the entire
scoring flow's runtime behaviour — including the rounding, whichever way it is fixed — has still never
been executed. It does not mean any of that has been discharged.** D-015 is one expression and a
static assertion; fixing it before promotion is a materially better outcome than approving around it.

---

**Third retest, 2026-08-13 (report revision 5) — result: PARTIAL.** Constraint gate **PASS**, unchanged,
on fully re-executed evidence: 13 / 13 HARD, 1 / 1 SOFT, scope re-derived mechanically for the fourth
time.

**Closed and independently verified: D-015, D-016b and D-017.** `Round_the_circumstance_score` is now
`@int(formatNumber(add(outputs('Calculate_circumstance_score'), 0.25), 'F0'))`, and the rounding was
**re-executed here rather than read**: across all 121 totals the flow can produce, under both `double`
and `decimal`, there are **zero mismatches against round-half-up**, where the pre-fix expression fails
30. An exact **20.5 now stores 21 and routes to Borderline human review.** The 17 new assertions were
**mutation-tested at this gate** — driven against the pre-0.9 expression, 7 assertion groups fail, and
the ones that pass are exactly the odd-whole-part cases that hid the defect. The suite is **577 passed,
0 failed, 1 skipped at 92.60% coverage**, matching `manifest.json`. The fix does not merely produce the
right answers; **it removes the dependency on .NET's midpoint mode**, so it is correct whichever numeric
type the runtime uses and whichever mode a future runtime adopts.

**No new defect was found. That is the first time in this feature's history.**

**Two P2 defects open — D-002 and D-004 — and for the first time neither is fixable by a developer.**
D-002 needs **Emily's** decision and has been open and unmoved since revision 1. D-004 needs an
accessibility audit that **nobody has commissioned in four consecutive reports**, that is **not blocked
on anything** — the form is live — and whose nine unassessed criteria have been assessed by nothing at
all. Every P2 that was a developer's to close has been closed and independently verified.

**Three corrections and one re-homing this pass recorded, none of which is a criticism of the fix:**
**D-016 was two different items under one label** — the register's (which contradictory observation
about the live form is stale) is renamed **D-016a** and is **still open**; the "disjoint" wording is
**D-016b** and is closed. Revision 0.9 stated this itself, unprompted, rather than banking the closure.
**D-018 is new only as an id** — the three trustee-facing breakdown P4s that revision 4 folded into
D-015's remedy did not close with it, and two are untouched; they are re-homed so they do not vanish.

**Still true, and not softened:** five of nine test layers cannot be executed because **no Power
Platform environment exists**; **`pac solution pack` could not be re-executed at this retest** (blocked
by session command permissions — the stored zips were opened and verified instead, and this report does
not claim otherwise); **no part of the scoring flow has ever run in the Power Automate runtime**,
including the corrected rounding; the accessibility audit has never been run; **OQ-001 and OQ-003 remain
board decisions** that no data in this repository can settle; SDD Amendment **A-01 is `PROPOSED`** and
needs plan-agent, so D-009 cannot be closed here; and **PRD is separately barred by the unsigned DPIA
regardless of any test result.**

**Approving this gate means accepting D-002 and D-004 as open, and accepting that the scoring flow's
runtime behaviour has still never been executed. It does not mean either has been discharged.** What has
changed is who can act: **no further development revision will move what is left.** The two open P2s
need a decision from Emily and an audit from the reviewer, and the release cannot be made correct by
more engineering.

---

## Retest, 2026-08-19 — report revision 8 (build #8, pre-deployment verification)

**Artifact:** `build/artifacts/revitalise-grant-automation-20260819-1/` — manifest `build_number` 8, source commit `6158243`, working tree clean across `src/`, `provisioning/` and `config/`
**WBS:** `0.4`, `0.5`, `0.9`, `0.10`, `2.1`, `2.4`, `4.2`, `4.4` — resolved from [contract/evidence-map.json](contract/evidence-map.json), every rule whose evidence resolves into the solution source
**Scope of this round:** no new development. The build was re-packed for deployment and the live DEV environment was verified against it, component type by component type.
**Result:** **FAIL** — one **P1** defect, **D-025**, and two HARD domain constraint violations that are the same defect.

### Result

**Dataverse auditing is switched off in DEV, so nothing in the application has an audit trail.** Read live from the environment: `organizations.isauditenabled = False`, `auditretentionperiodv2` empty, and `IsAuditEnabled = False` on all five tables. This is not a regression in build #8 — the provisioning step that enables it, declared at [ensure-auditing.ps1 -Env dev](config/revitalise-grant-automation-pipeline.yml#L615), has never been executed, and `logs/pipeline.log` contains zero references to it.

Everything else the artifact declares is present and correct in DEV, verified by direct query rather than inferred from an import exit code. The one functional change in this build — navigation for the Grant table — is genuinely not yet deployed.

### What was verified live, and what it showed

1. **Every declared column exists in DEV; nothing unexplained exists beside it.** Live `rev_*` attributes per table were diffed both ways against the solution source: source-not-live is **0** on all five tables, and every live-not-in-source name is platform-generated (`*name` shadow attributes, primary keys, one `_base` Money twin). This closes the class recorded when a "successful" import silently created nothing.

2. **All 21 option sets match source exactly — 137 values, zero orphans, zero label mismatches.** The stale members found on 2026-08-16 (`rev_breaktype` values 6–9 and `rev_applicanttype` value 4) are **gone**, so the cleanup that needed the maker portal has been done. That closes the live half of the orphaned-option-value problem.

3. **All three alternate keys report `EntityKeyIndexStatus = Active`.** `rev_grant_applicationid`, `rev_application_sourcesubmissionid` and `rev_setting_name` are all enforcing. The `Pending` caveat recorded against **A-G01** on 2026-08-18 is therefore discharged: one-grant-per-application is live, not merely declared.

4. **All 51 field permissions match the 51 secured columns in source, both directions, with no drift.** `REV_TrusteeRestricted` releases exactly the secured set.

5. **Component ids in source are the platform's own.** Both role ids and the field-security-profile id in source are byte-identical to the live ones, and the app module deliberately declares no id. That is [C-TECH-051](constraints/technology/technology-constraints.md#L93) satisfied by evidence.

6. **Role assignment follows the group-team pattern already in DEV.** Zero direct user-to-role assignments on either REV role; two Entra-group-backed group teams exist (`REV-PP-GrantApplications-DEV`, `REV-PP-GrantApplications-Service-DEV`, both `teamtype=2` with an AAD object id).

7. **All four cloud flows are live and activated** (`statecode=0`, `statuscode=1`), and the five custom main forms and every source-declared view are present with matching ids.

### Defects

| Id | Severity | Status | Detail |
|---|---|---|---|
| **D-025** | **P1** | **OPEN** | Auditing is off in DEV at both levels that matter. Organisation `isauditenabled=False` with no retention period; `IsAuditEnabled=False` on `rev_applicant`, `rev_application`, `rev_errorlog`, `rev_setting`, `rev_grant`. Attribute-level `IsAuditEnabled` is `1` on 135 of 137 stored `rev_` columns and does nothing while the two switches above it are off. **Entity-level `IsAuditEnabled` is absent from every `Entity.xml`**, so no solution import can fix this — it is [ensure-auditing.ps1](provisioning/dataverse/ensure-auditing.ps1#L98)'s job, and that script has never run. Fix: execute the Stage 0.5 step already declared at [pipeline config line 615](config/revitalise-grant-automation-pipeline.yml#L615), then re-verify by query |
| D-002 | P2 | OPEN, unchanged | Carried from revision 3. Not touched this round |
| D-004 | P2 | OPEN, unchanged | Carried from revision 3. Not touched this round |

**Why four report revisions called this PASS.** The audit assertion was read off the **attribute-level** flags in the solution source, which are present and which prove nothing on their own, and the row itself recorded "live audit-record verification BLOCKED" as an acceptable state. No gate and no test reads live organisation or table audit state; [domain-invariants](config/revitalise-grant-automation-build.yml#L283) asserts the source-side attribute flag and passes, which is precisely the assertion that made the gap invisible.

### Assumption register

| Assumption | Was | Now |
|---|---|---|
| **A-002** — the 164-character option label at `rev_conditionprofile` value 9 | `OPEN` | **CLOSED, premise void.** The label in source is now 63 characters and the live label matches it exactly, character for character, along with the other nine. The 164-character label no longer exists anywhere |
| **A-G01** — an alternate key on a lookup column enforces uniqueness | CLOSED with a `Pending`-index caveat | **Caveat discharged** — `EntityKeyIndexStatus=Active`, verified live |
| **A-G03** — the SharePoint library ACL denies the trustee group | `OPEN` | **Still OPEN and still not closeable.** The library does not exist and no script in this repository can create it. [C-TECH-058](constraints/technology/technology-constraints.md#L128) binds only where an environment could close the assumption, and none can, so it does not block this deploy — but it does block the acceptance flows at WBS 3.2/3.4 |

### Verification levels reached

| Component group | Level | Evidence |
|---|---|---|
| Whole solution, as source | **V2** packaged | Both pack types clean; declared component set asserted by unpacking the produced zip |
| The five tables, their forms, views, columns, option sets, field permissions, keys, roles, relationships, environment variables, app module | **V3** accepted, content confirmed | Direct Web API and FetchXML queries listed above, not import exit codes |
| Grant navigation (`rev_group_grants` and its three sub-areas) | **V2 only** | Declared at [AppModuleSiteMap.xml line 142](src/solutions/RevitaliseGrantAutomation/AppModuleSiteMaps/rev_grantadministration/AppModuleSiteMap.xml#L142); the live sitemap has no Grants group and no `rev_grant` sub-area, so it is in this artifact and not in the environment |
| Human open-and-save | **V4 NOT reached** | No named person has opened and saved the changed components since 2026-08-16. Cannot be performed by this session |
| End-to-end execution | **V5 NOT reached** | The flows are activated but no scoring or intake run was executed with real inputs this round |
| Audit trail | **Not reached at any level** | D-025 — it is off |

### Test layers

| Layer | Result |
|---|---|
| Unit / static | **PASS** — 735 passed, 0 failed, 1 skipped, 89.13% line coverage against an 80% threshold, Pester pinned 5.7.1, executed as [unit-tests](config/revitalise-grant-automation-build.yml#L401) declares it |
| Platform contract | **PASS** — every hand-authored contract has a register row; no orphan guesses; `component-shape` and `guid-syntax` clean |
| Verification level | **PARTIAL** — see the table above. V4 and V5 not reached |
| Provisioning | **FAIL** — the auditing step has never run (D-025). Schema, roles, group teams, field permissions and environment variables are all in place |
| Regression | **PASS** — nothing that previously passed now fails; the live/source diffs are clean in both directions |
| Security | **PASS on structure, incomplete on operation** — secret scan clean, no environment values or tenant UPNs in source, no direct role assignments, special-category columns barred from the scoring flow. Unauthenticated-request testing against the intake endpoint was not executed this round |
| Integration | **NOT EXECUTED** — needs a live end-to-end run |
| Accessibility | **NOT EXECUTED** — never has been, on any revision |
| Performance | **NOT EXECUTED** — no NFR threshold has been measured in a live environment |
| Cross-OS | **NOT PROVEN** — every step of build #8 ran on macOS, not on the Linux CI runner |

### Constraint verification

| Constraint | Result | Evidence |
|---|---|---|
| [C-DOM-004](constraints/domain/domain-constraints.md#L37) | PASS | `rev_errorlog` holds nine columns, none from the special-category register; asserted mechanically by `domain-invariants` |
| [C-DOM-010](constraints/domain/domain-constraints.md#L47) | **VIOLATION** | No create/update/delete is audit-logged anywhere: auditing is off at organisation and table level. D-025 |
| [C-DOM-011](constraints/domain/domain-constraints.md#L48) | **VIOLATION** | The record schema cannot be satisfied because no audit record exists to carry it. Same defect |
| [C-DOM-030](constraints/domain/domain-constraints.md#L92) | PASS | Register and the FR-016 gate in sync at 20 names; the scoring flow references none of them |
| [C-DOM-031](constraints/domain/domain-constraints.md#L93) | PASS | 16 secured, 4 exceptions each with a written reason and an owner, printed on every run |
| [C-DOM-032](constraints/domain/domain-constraints.md#L94) | PASS **in source only** | 20 of 20 registered columns carry the flag in source. Note the flag has no effect in DEV today — that is D-025, not a failure of this row |
| [C-TECH-001](constraints/technology/technology-constraints.md#L34) | PASS | `gitleaks` over the working tree, 4.44 MB, no leaks, run from the config as written |
| [C-TECH-004](constraints/technology/technology-constraints.md#L37) | PASS, carried | Intake trigger schema unchanged this round; bounds on every scored answer re-confirmed by the suite |
| [C-TECH-006](constraints/technology/technology-constraints.md#L39) | PASS on design, untested live | `rev_IntakeAllowedClientId` gates the intake endpoint. No unauthenticated request was fired this round |
| [C-TECH-014](constraints/technology/technology-constraints.md#L52) | PASS | 89.13% against the 80% threshold, enforced by a runner that exits non-zero below it |
| [C-TECH-040](constraints/technology/technology-constraints.md#L82) | PASS for what exists | Zero direct user-role assignments; two Entra-group-backed group teams. Test/Acc/Prd do not exist yet, so the environments the rule names cannot be checked |
| [C-TECH-042](constraints/technology/technology-constraints.md#L84) | PASS | Every provisioning script parses and exposes `-Env`; prior deploys proved re-run idempotency by execution |
| [C-TECH-045](constraints/technology/technology-constraints.md#L87) | PASS on design | Connectors are those the TAD lists; no DLP policy evaluation was performed, and no Test environment exists to perform it against |
| [C-TECH-046](constraints/technology/technology-constraints.md#L88) | PASS | The solution contains two roles, both `REV`-prefixed. No out-of-box role appears in it |
| [C-TECH-048](constraints/technology/technology-constraints.md#L90) | NOT APPLICABLE | No Code App component in this artifact; the trustee portal is Phase 3. Not counted as passed, and not `UNEVALUABLE` — the rule and its check are both usable, there is simply nothing here for them to bind to |
| [C-TECH-051](constraints/technology/technology-constraints.md#L93) | PASS | Role ids and the field-security-profile id in source are identical to the live ones; the app module declares no id |
| [C-TECH-052](constraints/technology/technology-constraints.md#L107) | PASS | Every hand-authored contract has a register row, and every register row maps to an artefact. `component-shape` clean over 25 files against 2 declared shapes |
| [C-TECH-053](constraints/technology/technology-constraints.md#L108) | PASS | Levels reported above are the levels executed. V4 and V5 are stated as not reached, not implied |
| [C-TECH-054](constraints/technology/technology-constraints.md#L109) | WARN — not proven | Build #8 ran entirely on macOS. The suite covers the scripts, but no step of this build executed on the Linux runner |
| [C-TECH-056](constraints/technology/technology-constraints.md#L111) | PASS | The live component inventory contains nothing beyond what source declares, so no diagnostic component survived a prior investigation |
| [C-TECH-057](constraints/technology/technology-constraints.md#L127) | PASS | Preflight: 23 steps, 18 gates, all with negative-test coverage; 4 exemptions each named with a reason |
| [C-TECH-058](constraints/technology/technology-constraints.md#L128) | PASS | A-002 closed this round by live evidence. A-G03 is OPEN but closeable in no existing environment, which is what this row conditions on |
| [C-TECH-059](constraints/technology/technology-constraints.md#L129) | PASS | Artifact directory resolved per build; digest regenerated and current |
| [C-TECH-060](constraints/technology/technology-constraints.md#L130) | PASS | 129 flow descriptions and 126 settings values within the limits their own schema declares |

```
CONSTRAINT CHECK
Domain   HARD: 4 / 6  of 6   |  violations: C-DOM-010, C-DOM-011
                             |  unevaluable: NONE
  C-DOM-010: organizations.isauditenabled=False and IsAuditEnabled=False on all five tables in
             REV-GrantApplications-DEV — no create/update/delete is audit-logged. D-025
  C-DOM-011: no audit record exists, so the required record schema cannot be satisfied. Same root cause
Domain   SOFT: 0             |  warnings:   NONE  (no domain SOFT row is scoped to test-agent)
Tech     HARD: 16 / 17 of 18 |  violations: NONE
                             |  unevaluable: NONE
                             |  not applicable: C-TECH-048 (no Code App component in this artifact)
                             |  warn: C-TECH-054 (build executed on macOS only, not the CI runner OS)
Tech     SOFT: 1             |  warnings:   NONE
Overall: BLOCKED
```

```
GATE BLOCKED
Reason: HARD constraint violation(s) — see CONSTRAINT CHECK above.
Resolve the violations listed and re-run this agent to re-check.
```

### What closing D-025 takes

One step that the pipeline config already declares, then re-verification by query. It is an environment change, not a tenant change, so it runs in Stage 0.5 without `APPROVE TENANT`. Nothing in the solution source needs to change — and nothing in the source *can* fix it, which is the part worth remembering.

Until it is closed, promoting special-category health data beyond DEV means promoting it with no audit trail, while **DPO sign-off is still outstanding** ([contract/external-dependencies.json](contract/external-dependencies.json), owner Rebecca Young, first seen 2026-07-04).


---

## Addendum, 2026-08-19 — D-025 CLOSED, report revision 8.1

**Result: FAIL → PARTIAL.** The P1 is closed. Two lesser items remain and neither is a defect
in the build.

### D-025 is closed, by evidence

The reviewer enabled organisation auditing in the admin centre and table auditing on all five
tables. Verified live by query, not from the portal's confirmation:

| Check | Before | Now |
|---|---|---|
| `organizations.isauditenabled` | `False` | **`True`** |
| `IsAuditEnabled` on `rev_applicant` | `False` | **`True`** |
| `IsAuditEnabled` on `rev_application` | `False` | **`True`** |
| `IsAuditEnabled` on `rev_grant` | `False` | **`True`** |
| `IsAuditEnabled` on `rev_setting` | `False` | **`True`** |
| `IsAuditEnabled` on `rev_errorlog` | `False` | **`True`** |
| Audit records exist | none possible | **2 records, with timestamp, operation, action, table and actor** |

The two records are the audit-configuration changes themselves, attributed to the user who made
them. That is `C-DOM-011`'s required schema satisfied by real records rather than by design
intent: `createdon`, `operation`, `action`, `objecttypecode`, `_userid_value`, and
`attributemask` / `changedata` for before-and-after.

Column-level coverage needed no work — the flags were already set, so 15 of 16, 89 of 91, 14 of
15, 4 of 5 and 7 of 8 stored `rev_` columns began auditing the moment each table switch went on.
The exclusions are each table's primary key plus the calculated `rev_costs`.

### Constraint movement

| Constraint | Was | Now |
|---|---|---|
| [C-DOM-010](constraints/domain/domain-constraints.md#L47) | **VIOLATION** | **PASS** — create/update/delete are audited on all five tables, confirmed by live query and by the existence of audit records |
| [C-DOM-011](constraints/domain/domain-constraints.md#L48) | **VIOLATION** | **PASS** — real audit records carry every required field |
| [C-TECH-064](constraints/technology/technology-constraints.md#L134) | did not exist | **PASS** — this addendum's evidence is the live comparison the row requires. It has no executable implementation yet, so it is enforced by review until one exists |

```
CONSTRAINT CHECK
Domain   HARD: 6 / 6  of 6   |  violations: NONE
                             |  unevaluable: NONE
Domain   SOFT: 0             |  warnings:   NONE
Tech     HARD: 17 / 18 of 19 |  violations: NONE
                             |  unevaluable: NONE
                             |  not applicable: C-TECH-048 (no Code App component in this artifact)
                             |  warn: C-TECH-054 (build ran on macOS; the CI runner OS is unexercised)
Tech     SOFT: 1             |  warnings:   NONE
Overall: WARN
```

### What still stands

**Audit log retention is not set.** `auditretentionperiodv2` is genuinely null — not zero, not
a default this report can name. The project's own `test-settings.json` and `prd-settings.json`
both declare 2192 days (6 years), reviewed with the DPO. This is a retention gap, not an audit
gap: changes are being recorded, and nothing states how long they are kept. Set it in the admin
centre under Audit settings, and not to "forever".

**Read auditing is off.** `isreadauditenabled` and `isuseraccessauditenabled` are both `False`.
`C-DOM-010` covers create, update and delete, so this does not affect the rows above — but "who
*saw* this, and when" is the stated rationale behind `C-DOM-032`, and it cannot be answered
today. A decision, not a defect.

**V4 and V5 are still unreached**, which is why this is `PARTIAL` and not `PASS`. No named person
has opened and saved the changed components, and no end-to-end scoring or intake run has been
executed. The Grant navigation is still at V2 — it is in the artifact and not in DEV.

### Build re-run through the real CI path

Not part of D-025, recorded because it changes what the numbers mean. The whole build was
executed through [scripts/ci/run-config-steps.sh](scripts/ci/run-config-steps.sh) — the path
`ci.yml` uses — for the first time in this project's history: **22 steps executed, 1 out of
context (`auth`, correctly), 23 declared, exit 0**, 739 tests passed, 0 failed, 89.13% coverage,
solution checker 0 at every severity. Every prior build, including build #8 earlier today, ran
the steps directly and could only claim they *would* work through the runner.

---

## Retest, 2026-08-21 — report revision 9 (build #4, WBS 4.3 IMP-0112 fix + Trustee Review Portal WBS 6.1–6.5)

**WBS:** `4.3`, `6.1`, `6.2`, `6.3`, `6.4`, `6.5`
**Artifact:** `build/artifacts/revitalise-grant-automation-20260821-4/` — manifest `build_number` 4, source commit `388291be9a10ecd657e772a5e1796ebdfeb1cf35`, `git status --porcelain` clean across `src/`, `provisioning/`, `config/`
**Handoff:** `HANDOFF | from:build-agent | to:test-agent | status:READY`, per [docs/development/revitalise-grant-automation-dev-summary.md](docs/development/revitalise-grant-automation-dev-summary.md#L4802) ("Trustee Review Portal") and [#L4931](docs/development/revitalise-grant-automation-dev-summary.md#L4931) (IMP-0112 fix)
**Result:** **FAIL** — one new **P1**, **D-026**. The 4.3 fix on its own has no defect.

### What this round covers

Two independent pieces of work landed in this one build: (1) the WBS 4.3 rework fixing
`REVIntakeWordPressToDataverse`'s six alternate-key `Get-a-row-by-id` reads (the shape
[IMP-0112](logs/improvement-log.jsonl) predicted and [flow-definition-language](config/revitalise-grant-automation-build.yml#L459) caught on this build's first run through), and (2) WBS 6.1–6.5, the Trustee Review Portal —
a Power Apps Code App plus a new `rev_review` table, four new `rev_application` columns, two
new build gates, and a security-role amendment — built ahead of the outstanding DPO sign-off
under [EX-003](contract/known-exceptions.json#L31).

**Everything below was independently re-executed or independently queried live in DEV this
session, not copied from the build manifest** (`C-TECH-053`'s own discipline applied to test-agent's
own report): the full Pester suite, the coverage-threshold calculation, ten build gates, the Code
App's typecheck/lint/test/coverage run, `gitleaks`, the provisioning identity probe, and eleven
separate live Dataverse queries against `REV-GrantApplications-DEV` using the documented
cert-based method ([IMP-0083](logs/improvement-log.jsonl)/[IMP-0022](logs/improvement-log.jsonl)).

### Regression — independently re-run, not read from the manifest

**847 / 847 Pester tests pass, 0 failed, 1 skipped** — `pwsh -NoProfile -File src/tests/Invoke-Tests.ps1`,
re-executed in this session. This is the number that matters, and it corrects a stale claim: [Dev
Summary §11](docs/development/revitalise-grant-automation-dev-summary.md#L4877) under "Trustee
Review Portal" still reads **835 passed, 5 failed, 1 skipped** and still narrates the `REV Trustee`
role id as an open blocker — both true when that section was written, both stale now (the role id
closed and the 4.3 fix landed in the same day's
[later revision](docs/development/revitalise-grant-automation-dev-summary.md#L4960), which does
carry the correct 847/0/1). Per the dispatching handoff's own instruction, this was verified independently
rather than taken on trust from either document, and the independent run agrees with the newer,
corrected figure — build-agent's manifest note to the same effect is confirmed.

**Coverage: 86.62% enforced (PASS, threshold 80%)**, re-derived with
`scripts/verify-coverage-threshold.py` against a freshly generated `coverage.xml`, exit 0, 1496 of
1727 lines, 4 named exclusions each with a substitute proof. The runner's own unenforced figure —
`Invoke-Tests.ps1 -CoverageThreshold 80` — reports **67.33%** and prints `RESULT: FAILED`; this is
not a second defect, it is [IMP-0134](logs/improvement-log.jsonl)'s documented gap between what a
tool prints and what actually gates the build: the runner measures over the whole
`provisioning/{common,entra,dataverse}` tree with no exclusions, the `coverage-threshold` step
applies the four owned exclusions and is what `C-TECH-014` is actually verified by. Both numbers
match the manifest exactly.

**Code App: 228 / 228 tests pass, 97.78% line coverage, typecheck clean, lint clean** — all four
re-run directly (`npm run coverage`, `npm run typecheck`, `npm run lint` in
`src/code-apps/trustee-review-portal/`), matching the manifest exactly.

### Live verification against DEV — new this round, not previously performed on this feature

Verified via `pac env fetch` (FetchXML, using the existing `svc_grantapplications@revitalise.org.uk`
`pac auth` profile) and via direct Dataverse Web API metadata calls (cert-based app-only auth, the
method [IMP-0083](logs/improvement-log.jsonl) documents), against `REV-GrantApplications-DEV`:

| # | Query | Result |
|---|---|---|
| 1 | `role` filtered `name eq 'REV Trustee'` | **Exists live**, `roleid = 3ab6cc7b-959d-f111-b8de-70a8a5079a1b` — byte-identical to [source](src/solutions/RevitaliseGrantAutomation/Roles/REV%20Trustee/REV%20Trustee.xml#L171) and to [Solution.xml's RootComponent](src/solutions/RevitaliseGrantAutomation/Other/Solution.xml#L174). Confirms A-TR-2 CLOSED |
| 2 | `rev_review` — all 14 source-declared columns in one query | **Every column resolves**, 0 rows. The table exists live with the exact shape source declares — **contradicts** [Dev Summary A-TR-6](docs/development/revitalise-grant-automation-dev-summary.md#L4860) ("the table is not in DEV yet") and the Entity.xml's own header comment claiming V1-only. Closes A-TR-6 (below) |
| 3 | `rev_application` — `rev_narrativeredacted`, `rev_redactionreleased`, `rev_eligibleforround`, `rev_reviewround`, each filtered `not-null` | **All four columns exist live**; **zero rows** have any of them populated, across all 14 live applications. This is the direct evidence [EX-003](contract/known-exceptions.json#L31)'s safety argument rests on — nothing is exposed because nothing is set |
| 4 | `team` filtered `name like '%Trustee%'` | **No results.** No `REV Trustees` team exists yet — the app has not been shared to anyone |
| 5 | `fieldsecurityprofile` → `teamprofiles` for `REV_TrusteeRestricted` | **Zero member teams.** Matches [Dev Summary §11](docs/development/revitalise-grant-automation-dev-summary.md#L4884)'s own statement that no positive control exists yet for A-TR-4/A-TR-5 |
| 6 | `role` (`REV Trustee`) → `systemuserroles` | **Zero direct user assignments** — `C-TECH-040` holds for what exists |
| 7 | `workflow` filtered `name like '%Anonymis%'` | **No results.** Automation #5 (`REVAnonymise`) genuinely does not exist live, matching [contract/external-dependencies.json](contract/external-dependencies.json) |
| 8 | `workflow` where `category eq 5` (all cloud flows) | All four REV flows **Activated**. The live `REV \| Intake \| WordPress to Dataverse` is the **pre-IMP-0112 definition** — the 4.3 fix is V2 (packaged) only, not yet imported. See "Open risk carried into deployment" below |
| 9 | `organizations` → `isauditenabled`, `auditretentionperiodv2` | `isauditenabled = True` (D-025's 2026-08-19 fix persists); `auditretentionperiodv2 = null` (the retention gap "Addendum, 2026-08-19 — D-025 CLOSED, report revision 8.1" already recorded, above in this document, unchanged, not this round's scope) |
| 10 | `EntityDefinitions` → `IsAuditEnabled` for all six tables | `rev_applicant`, `rev_application`, `rev_grant`, `rev_setting`, `rev_errorlog` all **True**. **`rev_review` is False.** See D-026 |
| 11 | `EntityDefinitions('rev_application')/Attributes('rev_redactionreleased')` → `IsAuditEnabled` | **True** — the four new columns inherited `rev_application`'s table-level auditing correctly; only the new *table* is affected |

Query 8's discriminator (a genuine attribute error naming the entity, versus `pac`'s
`MetadataCache` "was not found" error for a truly absent entity) was proven against two
deliberately-fake control queries before being trusted — see the session's own working notes;
the distinction matters because a silent zero-row result and a nonexistent-entity result look
identical unless you check.

### Defects raised this round

| Id | Severity | Status | Detail |
|---|---|---|---|
| **D-026** | **P1** | **OPEN** | `rev_review` — the table WBS 6.4 (decision capture) and 6.5 (access test) write to — has **entity-level `IsAuditEnabled = False`** live in DEV, while organisation auditing is on and all five pre-existing tables remain on. Same defect class as D-025 ([C-DOM-010](constraints/domain/domain-constraints.md#L47), [C-DOM-011](constraints/domain/domain-constraints.md#L48), [C-TECH-064](constraints/technology/technology-constraints.md#L134)), found this time with **zero rows written** — no create/update/delete has yet gone unaudited, but the very next authorised step (6.4/6.5's test-data access test under [EX-003](contract/known-exceptions.json#L31)) would write trustee verdicts into exactly this gap. Root cause: `rev_review` was created live via `ensure-schema.ps1` (which creates schema, not audit switches — `C-TECH-050`), and `rev_review` is absent from `auditedTables` in both [test-settings.json](provisioning/deploymentSettings/test-settings.json#L331) and [prd-settings.json](provisioning/deploymentSettings/prd-settings.json#L359) — and no `dev-*-settings.json` file declares `auditedTables` at all, meaning `ensure-auditing.ps1` has never had a DEV-runnable path; the five existing tables' auditing was turned on by the reviewer directly in the admin centre on 2026-08-19 (revision 8.1), a route this settings gap makes necessary again. **Fix, same shape as D-025:** add `rev_review` (and, while there, `rev_grant`, which is on live but is *also* absent from both settings files' `auditedTables` array — a second settings/reality drift, lower severity, not itself unaudited) to the settings files, then enable table auditing on `rev_review` — via `ensure-auditing.ps1` once DEV has a settings path, or directly in the admin centre as the reviewer did for the first five — and re-verify by the same live query. One provisioning action, not a code change |
| D-002 | P2 | OPEN, unchanged | Carried since revision 3. Not touched this round |
| D-004 | P2 | OPEN, unchanged, **scope widened** | Carried since revision 3 (public form, never audited). The Trustee Review Portal is a **second, larger** UI surface with no accessibility audit performed against it either. Static review only (below) — favourable signals, not a substitute for the audit this defect has requested for eight report revisions |

### Static accessibility review (no automated scan or manual walkthrough performed)

Per `skills/accessibility-checklist.md`, applied by static source read only — no axe-core/Lighthouse
tooling exists in this repository (`C-TECH-020`–`023` retired for the same reason: no dependency
scanner), and no human keyboard/screen-reader/contrast pass was performed this round:

- `<html lang="en-GB">` declared ([index.html](src/code-apps/trustee-review-portal/index.html#L2))
- No raw `<img>` tags in the app (no missing-`alt` risk)
- No `<div onClick>` custom-control anti-pattern (0 hits) — interactive elements are Fluent UI v9
  components, an accessible-by-default library, used across 10 files
- 7 files carry explicit `aria-label` / `aria-live` / `role` attributes

Favourable, but this is exactly the "designed, not verified" distinction
`knowledge/domain/compliance-requirements.md` §3 draws — **Accessibility layer: NOT EXECUTED**,
folded into D-004 rather than raised as a new defect.

### Assumption register (Dev Summary §10, WBS 6.1–6.5) — corrected

[Dev Summary §10](docs/development/revitalise-grant-automation-dev-summary.md#L4851) states
"Twelve rows, all OPEN." That is now stale on two rows, independently closed by this test cycle:

| Assumption | Dev Summary said | test-agent finds |
|---|---|---|
| **A-TR-2** | Listed among "all OPEN" | **Already CLOSED** — the role file's own comment ([REV Trustee.xml](src/solutions/RevitaliseGrantAutomation/Roles/REV%20Trustee/REV%20Trustee.xml#L169)) records the live roleid read-back with full evidence, dated 2026-08-21. Query #1 above reconfirms it live |
| **A-TR-6** | "The table is not in DEV yet" | **CLOSED by this report.** Query #2 above: `rev_review` exists live with all 14 columns matching source exactly |
| A-TR-1, 3, 4, 5, 7–12 | OPEN | **Genuinely still OPEN, and not closeable in DEV as it stands** — each needs either the Code App pushed (`pac code push` has never run, [TAD §9.3](docs/architecture/revitalise-grant-automation-architecture.md#L1094)) or a signed-in trustee test identity (no `REV Trustees` team exists, query #4/#5). Neither is a test-agent action; `C-TECH-058` does not fire because no environment currently holds the missing precondition. Recommend pipeline-agent close all ten in one sweep (`skills/how-to-verify-a-platform-contract.md` §6) once the app is pushed and one trustee test user is provisioned |

**Corrected count: 2 of 12 CLOSED, 10 OPEN-and-not-yet-closeable.** Dev Summary should be updated
to match — a documentation finding, not a gate.

### A second, unrelated contract-chain finding, found while regenerating WBS state for this report

`scripts/verify-wbs-chain.py` reads a cached `logs/state/wbs-state.json` that is **not**
regenerated on demand. It was last written 2026-08-20 — a full day before this session's
`rev_review` entity landed on disk. Run cold, it reported `entity rev_review: ABSENT` for task
0.4, which is false (`git ls-files` and `glob.glob` both find it instantly). Running
`python3 scripts/derive-wbs-state.py` first — done as part of producing this report — corrected
it: `rev_review` drops off task 0.4's absent list, leaving `rev_provider`, `rev_bankaccount`,
`rev_payment`, `rev_anonymisedstatistic`, exactly matching
[EX-001](contract/known-exceptions.json#L13)'s remaining scope once Review is subtracted. This is
a second instance of [IMP-0089](logs/improvement-log.jsonl)'s class ("a preflight result that
depends on files left behind by a previous run is not a result") and is logged as such below.
**Separately, `EX-001`'s prose still names five absent tables; four remain** — a one-line text
correction, not a re-scoping of the exception.

A related, larger gap found the same way: `contract/evidence-map.json`'s rules for WBS **6.1,
6.2, 6.3** (and half of 6.5) check for
`src/solutions/RevitaliseGrantAutomation/AppModules/rev_trusteereview` — a Model-Driven-App
path — even though [ADR-003](docs/architecture/revitalise-grant-automation-architecture.md#L1137)
settled on a Code App at `src/code-apps/trustee-review-portal/` on 2026-08-10, before this build
existed. Because `wbs.json`'s `claimed_status` for 6.1–6.3 is also `null`, the evidence rule and
the claim currently **agree** on "not started" — so `verify-wbs-chain.py` raises no warning at
all, and ~7.5 h of demonstrably built, independently-tested work (WBS 6.1–6.3's own hours
proposal, [Dev Summary](docs/development/revitalise-grant-automation-dev-summary.md#L4896)) is
invisible to the one gate meant to catch exactly this kind of drift. Only 6.4's rule (`entity:
rev_review`) was written against the shape actually built, and it correctly derives `complete`.
**Recommend:** point the 6.1/6.2/6.3 (and 6.5's first) evidence-map rules at
`src/code-apps/trustee-review-portal/` instead.

### Open risk carried into deployment, restated plainly

DEV's live `REV | Intake | WordPress to Dataverse` (query #8) is still the **pre-fix** definition
— the six alternate-key `Get-a-row-by-id` calls IMP-0112 predicted and this build's own
`flow-definition-language` gate caught. The fix is V2 (packaged) only; nothing has imported it.
A real WordPress submission arriving before the next DEV import will still fail exactly as
IMP-0112 describes. Not a new defect — the fix is correct and independently confirmed above —
but worth stating so "the fix landed" is not read as "the live flow is fixed."

### Verification levels reached

| Component group | Level | Evidence |
|---|---|---|
| WBS 4.3 fix (`REVIntakeWordPressToDataverse`) | **V2** packaged | Byte-diff of packed flow JSON against source, identical; live flow (query #8) is still the pre-fix version — **V3 not reached for the fix itself** |
| `REV Trustee` role | **V3** accepted, live | Query #1 — created live via `ensure-schema.ps1`, id read back and matches source exactly |
| `rev_review` table + all 14 columns | **V3** accepted, live | Query #2/#11 — **this corrects Dev Summary's own V1-only claim for this entity** |
| 4 new `rev_application` columns | **V3** accepted, live | Query #3 |
| Code App (61 files, `src/code-apps/trustee-review-portal/`) | **V2** compiled/tested | `pac code push` never run ([TAD §9.3](docs/architecture/revitalise-grant-automation-architecture.md#L1094)); no environment has served it to a browser |
| Whole solution as a managed/unmanaged package | **V2** packaged | `pack-managed`/`pack-unmanaged` both re-confirmed via the full build-config gate suite |
| Human open-and-save | **V4 NOT reached** | No named person has opened any changed component since this dispatch began |
| End-to-end execution (a trustee reviewing a case) | **V5 NOT reached** | No trustee identity exists yet to execute it |
| Audit trail on `rev_review` | **Not reached at any level — D-026** | Query #10 |

- Idempotency: **not re-run this pass.** `ensure-schema.ps1`'s idempotent design is established by
  its own contract tests (part of the 847); test-agent did not perform a second live write this
  session (out of scope — provisioning writes are pipeline-agent's remit; see
  `logs/known-failure-modes.md` → "Operating constraints of this environment")
- V4 designer/editor open + save: **NOT PERFORMED.** Named, owned pipeline step, unchanged position
- Cross-OS (`C-TECH-054`): this entire session ran on macOS. No new OS-specific provisioning code
  was introduced by either piece of work in scope (four declarative columns; JSON flow edit; Node
  toolchain), so this is not a new regression — but it is a HARD constraint genuinely unproven on
  the CI runner it names, for the fifth report revision running (`IMP-0165`: CI has never fired on
  a matching branch)
- Warnings triaged (`C-TECH-055`): the three warnings in `manifest.json` (Vite bundle size,
  packer "not defined in customizations," npm `glob` deprecation) were all triaged by build-agent
  this same build and independently re-read here — all resolved or accepted with rationale, 0
  untriaged

### Test layers

| Layer | Result |
|---|---|
| Unit | **PASS** — 847/0/1, independently re-run |
| Integration | **NOT EXECUTED** — needs a live end-to-end run with a real trustee identity |
| End-to-End | **NOT EXECUTED** — same blocker |
| Regression | **PASS** — nothing that previously passed now fails; live 5-table audit state unchanged from revision 8.1 |
| Security | **PASS on structure** — `no-secured-columns-in-code-app`, `no-trustee-in-column-security-profile`, `field-security-coverage` all independently re-run and PASS; **fail-closed logic in `visibility.ts` read directly and confirmed**; live field-security profile has zero members (query #5), so no positive-control test of the anonymisation control is possible yet |
| Accessibility | **NOT EXECUTED** — see above; folded into D-004 |
| Performance | **NOT EXECUTED** — no NFR threshold measured live |
| Provisioning | **FAIL — D-026** |
| **Platform Contract** | **PASS with two documentation corrections** — A-TR-2/A-TR-6 closed (above); no orphan hand-authored contract found |
| **Verification Level** | See table above — no overclaim found; several components are in fact **further along** than Dev Summary states |
| Cross-OS | **NOT PROVEN** — carried, unchanged, see above |
| Constraint Verification | See below |

### Constraint verification

| Constraint | Result | Evidence |
|---|---|---|
| [C-DOM-004](constraints/domain/domain-constraints.md#L37) | PASS | `domain-invariants`, independently re-run: `rev_errorlog` holds no special-category column |
| [C-DOM-010](constraints/domain/domain-constraints.md#L47) | **VIOLATION** | `rev_review`: no create/update/delete is audit-logged. D-026 |
| [C-DOM-011](constraints/domain/domain-constraints.md#L48) | **VIOLATION** | Same root cause — no audit record can exist for `rev_review` today |
| [C-DOM-030](constraints/domain/domain-constraints.md#L92) | PASS | `domain-invariants`: 20/20 in sync, register ↔ FR-016 gate |
| [C-DOM-031](constraints/domain/domain-constraints.md#L93) | PASS | 16 secured, 4 documented exceptions, all printed |
| [C-DOM-032](constraints/domain/domain-constraints.md#L94) | PASS **in source only** | 20/20 enabled in source. Live half is C-TECH-064 below — this row is not evidence for C-DOM-010/011 |
| [C-TECH-001](constraints/technology/technology-constraints.md#L34) | PASS | `gitleaks detect --no-git`, re-run: no leaks, 8.28 MB scanned |
| [C-TECH-004](constraints/technology/technology-constraints.md#L37) | PASS | No new input surface; IMP-0112's fix reuses the already-verified `ScoringCalculateAndFlag` shape |
| [C-TECH-006](constraints/technology/technology-constraints.md#L39) | PASS on design, untested live this round | Live intake flow is still pre-fix (query #8); testing auth against it would not validate this round's change |
| [C-TECH-014](constraints/technology/technology-constraints.md#L52) | PASS | 86.62% ≥ 80%, re-derived independently |
| [C-TECH-040](constraints/technology/technology-constraints.md#L82) | PASS for what exists | Query #6: 0 direct assignments for `REV Trustee` |
| [C-TECH-042](constraints/technology/technology-constraints.md#L84) | PASS | Idempotent design covered by the 847-test suite; no live write performed by test-agent this round |
| [C-TECH-045](constraints/technology/technology-constraints.md#L87) | PASS | No new connector; Code App uses the existing Dataverse connector only |
| [C-TECH-046](constraints/technology/technology-constraints.md#L88) | PASS | `REV Trustee` is `IsCustomizable=1`, a copy, not an OOB role edit |
| [C-TECH-048](constraints/technology/technology-constraints.md#L90) | PASS | `client.ts` read directly: `getClient` from `@microsoft/power-apps/data`, no MSAL/token code anywhere in the app |
| [C-TECH-051](constraints/technology/technology-constraints.md#L93) | PASS | `REV Trustee` id read back live (query #1), matches source; not fabricated |
| [C-TECH-052](constraints/technology/technology-constraints.md#L107) | PASS | 12-row register for 6.1–6.5, `component-shape` re-run OK; no orphan found |
| [C-TECH-053](constraints/technology/technology-constraints.md#L108) | PASS | No overclaim found. Several components are under-claimed (A-TR-2, A-TR-6, this section) — corrected above |
| [C-TECH-054](constraints/technology/technology-constraints.md#L109) | WARN — not proven | Whole session ran on macOS; no new OS-specific code this round |
| [C-TECH-056](constraints/technology/technology-constraints.md#L111) | PASS | This session's own live queries were reads only; no diagnostic component created |
| [C-TECH-057](constraints/technology/technology-constraints.md#L127) | PASS | `verify-build-config.py` re-run clean; all gates have registered negative tests (part of the 847) |
| [C-TECH-058](constraints/technology/technology-constraints.md#L128) | PASS | The 10 genuinely-OPEN A-TR rows are not closeable in DEV as it stands (no pushed app, no trustee identity) — this constraint does not fire on a precondition that does not yet exist anywhere |
| [C-TECH-064](constraints/technology/technology-constraints.md#L134) | **VIOLATION** | Query #10: `rev_review` entity-level `IsAuditEnabled=False` live, against declared intent. D-026 |
| [C-TECH-065](constraints/technology/technology-constraints.md#L135) | PASS | `verify-environment-access.ps1 -Env dev`, re-run: `PASS — provisioning identity recognised` |
| [C-TECH-066](constraints/technology/technology-constraints.md#L136) | PASS | `verify-tad-coverage.py`, re-run: 129 column specs, 39 owned deferrals, 15 trustee-visible columns on tables `REV Trustee` can read |

```
CONSTRAINT CHECK
Domain   HARD: 4 / 6  of 6   |  violations: C-DOM-010, C-DOM-011
                             |  unevaluable: NONE
  C-DOM-010: rev_review IsAuditEnabled=False live in REV-GrantApplications-DEV — no create/
             update/delete on this table is audit-logged. D-026
  C-DOM-011: no audit record can exist for rev_review today. Same root cause
Domain   SOFT: 0             |  warnings:   NONE  (no domain SOFT row is scoped to test-agent)
Tech     HARD: 17 / 19 of 19 |  violations: C-TECH-064
                             |  unevaluable: NONE
                             |  warn: C-TECH-054 (whole session ran on macOS, not the CI runner OS)
  C-TECH-064: rev_review entity-level IsAuditEnabled=False live, against declared intent
             (source says 1; NFR-014 requires it). D-026, same root cause as C-DOM-010/011
Tech     SOFT: 0             |  warnings:   NONE  (no tech SOFT row is scoped to test-agent)
Overall: BLOCKED
```

```
GATE BLOCKED
Reason: HARD constraint violation(s) — see CONSTRAINT CHECK above (C-DOM-010, C-DOM-011, C-TECH-064).
Resolve the violations listed and re-run this agent to re-check.
```

### What closing D-026 takes

One provisioning action, same shape as D-025: add `rev_review` to `auditedTables` in a DEV-runnable
settings location (none currently exists — this is itself the settings gap named above), enable
table auditing on `rev_review` (`ensure-auditing.ps1 -Env dev` once the settings path exists, or
directly in the admin centre as the reviewer did for the first five tables on 2026-08-19), then
re-verify with the same live query this report used (`EntityDefinitions(LogicalName='rev_review')
?$select=IsAuditEnabled`). No source code changes. Recommend doing this **before** any WBS 6.4/6.5
test-data access-test writes a single row to `rev_review` — `EX-003` authorises test data in DEV,
not test data with no audit trail.

### Recommendation

**BLOCKED — do not proceed to Pipeline.** Fix D-026 (cheap, one provisioning step, no code change),
re-run test-agent against the same artifact. The WBS 4.3 fix itself has no open defect and is
independently confirmed at V2 with the live flow correctly identified as not-yet-updated; whether
it ships decoupled from the Trustee Portal work is a `commercial-agent` / reviewer scheduling
question, not a test-agent finding. Once D-026 is closed, the two Dev Summary corrections above
(A-TR-2/A-TR-6 closed; the evidence-map.json path drift for 6.1–6.3) should also be applied so the
next reader of either document is not working from stale numbers.

### Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-0178 | `platform-state-divergence` | blocker | A table created live via `ensure-schema.ps1` (schema only) does not inherit table-level auditing — `rev_review` shipped with organisation auditing on and its own entity-level `IsAuditEnabled` off, the same defect class as D-025/IMP-0082, this time on a table with zero rows; neither DEV settings file declares an `auditedTables` list at all, so `ensure-auditing.ps1` has no DEV-runnable path and the fix for the first five tables was a manual admin-centre action outside any script |
| IMP-0179 | `evidence-rule-targets-a-superseded-implementation-path` | friction | `contract/evidence-map.json`'s rules for WBS 6.1/6.2/6.3 (and half of 6.5) check for a Model-Driven-App path (`AppModules/rev_trusteereview`) that ADR-003 replaced with a Code App eleven days before this build; because the WBS claimed_status is also null, the false-absent evidence rule and the empty claim agree, so `verify-wbs-chain.py` raises no warning at all and ~7.5h of built, tested work is currently invisible to the one gate meant to catch exactly this kind of drift |
| IMP-0180 | `gate-cannot-fail` (x24 — generalise) | friction | `verify-wbs-chain.py` reads `logs/state/wbs-state.json` without regenerating it; run cold against a cache one day stale, it reported a just-built entity (`rev_review`) as ABSENT for task 0.4. Second instance of IMP-0089's class ("a preflight result that depends on files left behind by a previous run is not a result") — the gate should regenerate state itself, or refuse to run against a file older than the newest commit it covers |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py`

---

## Addendum, 2026-08-22 — D-026 CLOSED, report revision 9.1

**Result: FAIL → PARTIAL.** The P1 is closed. Two carried P2s and the unreached verification
levels remain, and neither is new.

**Scope of this addendum:** the single blocking finding from revision 9 only, per the
dispatching request — `rev_review`'s live `IsAuditEnabled` state, re-checked independently
rather than accepted from the reviewer's report that it had been switched on. No source changed
since revision 9: `git rev-parse HEAD` is still `388291be9a10ecd657e772a5e1796ebdfeb1cf35`, the
same `source_commit` the [build #4 manifest](build/artifacts/revitalise-grant-automation-20260821-4/manifest.json)
records, and `git status --porcelain -- src/ provisioning/ config/` is still clean. Nothing else
from revision 9 was re-executed — no reason existed to, since nothing that could affect it changed.

### D-026 is closed, by evidence

Four live queries, run this session against `REV-GrantApplications-DEV` via the certificate-based
Web API method ([IMP-0083](logs/improvement-log.jsonl)), the same method and the same query text
revision 9 used — not the admin-centre confirmation, and not the reviewer's report that the switch
had been flipped:

| Check | Revision 9 (2026-08-21) | Now |
|---|---|---|
| `rev_review` entity-level `IsAuditEnabled` | `False` | **`True`** |
| `organizations.isauditenabled` | `True` (unchanged) | **`True`** — no regression |
| `IsAuditEnabled` on `rev_applicant`, `rev_application`, `rev_grant`, `rev_setting`, `rev_errorlog` | all `True` | **All five still `True`** — no regression on the tables D-025 fixed |
| `rev_review` row count | 0 | **Still 0** — no create/update/delete has reached the table in the interim, so no write ever went unaudited across the gap |

The fourth row is the one this retest could not take on trust: `EX-003` authorises 6.4/6.5's
test-data access test to write to `rev_review`, and a row landing between D-026 being raised and
the switch being flipped would have been an unaudited write surviving the fix. `rev_reviews?$select=rev_reviewid,createdon,modifiedon`
returns zero rows, so that did not happen.

`rev_review`'s `Entity.xml` [already declared `IsAuditEnabled=1`](src/solutions/RevitaliseGrantAutomation/Entities/rev_review/Entity.xml#L314)
at revision 9 and is unchanged — this closes the gap between declared intent and live state that
`C-TECH-064` names, not a source change.

### Constraint movement

| Constraint | Was | Now |
|---|---|---|
| [C-DOM-010](constraints/domain/domain-constraints.md#L47) | **VIOLATION** | **PASS** — `rev_review` create/update/delete now audited; zero unaudited writes occurred in the gap |
| [C-DOM-011](constraints/domain/domain-constraints.md#L48) | **VIOLATION** | **PASS** — an audit record can now be created for `rev_review`; none was needed retroactively |
| [C-TECH-064](constraints/technology/technology-constraints.md#L134) | **VIOLATION** | **PASS** — live matches declared intent |

```
CONSTRAINT CHECK
Domain   HARD: 6 / 6  of 6   |  violations: NONE
                             |  unevaluable: NONE
Domain   SOFT: 0             |  warnings:   NONE  (no domain SOFT row is scoped to test-agent)
Tech     HARD: 18 / 19 of 19 |  violations: NONE
                             |  unevaluable: NONE
                             |  warn: C-TECH-054 (whole session ran on macOS, not the CI runner OS — carried, unchanged)
Tech     SOFT: 0             |  warnings:   NONE  (no tech SOFT row is scoped to test-agent)
Overall: WARN
```

### What still stands

Nothing below is new; each is carried forward unchanged from revision 9 and none is this
addendum's scope to re-verify or resolve:

- **D-002, D-004 (P2, OPEN)** — unchanged. §4 above still applies in full
- **V4 and V5 not reached** for the Trustee Review Portal — no `pac code push`, no trustee test
  identity, no human open-and-save on any 6.1–6.5 component. `EX-003`'s own terms mean this stays
  test-data-only in DEV regardless
- **The WBS 4.3 fix is still V2 only** — the live intake flow (revision 9's query #8) was not
  re-queried this round; nothing in this addendum's scope could have changed it
- **`auditretentionperiodv2` is still `null`** — the retention gap recorded at revision 8.1,
  restated at revision 9, restated here for the same reason: it is a decision, not a defect,
  and it is not D-026
- **C-TECH-054 (cross-OS) is still unproven** — this session, like every prior one, ran on macOS
- **IMP-0179 and IMP-0180** (the evidence-map path drift and the stale `wbs-state.json` cache,
  both logged at revision 9) — untouched; resolving either is `pm-agent`/`improvement-agent`
  territory, not test-agent's

### Recommendation

**No longer BLOCKED.** The one HARD constraint violation this retest was scoped to close
(`C-DOM-010`, `C-DOM-011`, `C-TECH-064` — all one root cause, D-026) is closed and independently
confirmed live, including the one thing a reviewer's report could not stand in for: that no write
reached the table unaudited in the gap. Per the same rule this project applied at revision 8.1,
open P2s and unreached V4/V5 keep the result at **PARTIAL**, not PASS — the reviewer's approval
is what accepts that remaining shape, the same as it did on 2026-08-19.

```
TEST REVIEW REQUIRED — docs/tests/revitalise-grant-automation-test-report.md  |  Result: PARTIAL
Respond APPROVED to proceed to Pipeline, REQUEST RETEST to re-run, or give feedback for dev fixes.
```

⚠️ SOFT-equivalent carried warning present — `C-TECH-054` (cross-OS, HARD, genuinely unproven for
the fifth report revision running). Human reviewer must explicitly acknowledge: respond APPROVED
to accept the risk, or give feedback before approving.

### Findings Logged

None. Nothing in this addendum's four queries produced a result outside what was expected once
the reviewer's action was independently confirmed — IMP-0178 (the finding that raised D-026) is
closed by this evidence, and no new lesson resulted.

IMPROVEMENT LOG: 0 entries appended — none  |  digest regenerated: YES

---

## Retest, 2026-08-23 — report revision 10 (build #2, real Dataverse data sources wired + stale-test fix)

**WBS:** `6.1`, `6.2`, `6.3`, `6.4`, `6.5`
**Artifact:** `build/artifacts/revitalise-grant-automation-20260823-2/` — manifest `build_number` 2, source commit `388291be9a10ecd657e772a5e1796ebdfeb1cf35` with **27 uncommitted paths** at pack time (the manifest's own disclosure)
**Handoff:** `HANDOFF | from:build-agent | to:test-agent | status:READY`, per [docs/development/revitalise-grant-automation-dev-summary.md#L5072](docs/development/revitalise-grant-automation-dev-summary.md#L5072) (real data sources wired) and [#L5210](docs/development/revitalise-grant-automation-dev-summary.md#L5210) (stale-test fix)
**Result:** **FAIL** — constraint gate **BLOCKED**, one new HARD violation (`C-TECH-058`). No new P1/P2 code defect; one new **P4** data-hygiene finding (D-027).

### What this round covers

Two pieces of work landed since revision 9.1, both already-accepted WBS 6.1–6.5 rework, no new scope: (1) four real Dataverse data sources (`rev_application`, `rev_review`, `rev_applicant`, `systemuser`) wired into the trustee Code App via `pa app add data-source -u <org-url>`, replacing the placeholder `account` smoke-test binding ([dev summary #L5072](docs/development/revitalise-grant-automation-dev-summary.md#L5072)); (2) `DeploymentSettings.Tests.ps1`'s stale hardcoded audited-table count generalised to derive from source ([dev summary #L5210](docs/development/revitalise-grant-automation-dev-summary.md#L5210), `IMP-0212`).

**Independently re-executed or independently queried this session, not copied from the build manifest** (`C-TECH-053` applied to this report itself): the packaged Pester results XML (parsed directly, not the manifest's prose), `no-secured-columns-in-code-app`, `gitleaks`, `verify-domain-invariants.py`, `verify-pipeline-config.py`, `verify-improvement-log.py --check`, `pac code list`, and six live Dataverse queries against `REV-GrantApplications-DEV` using the certificate-based method ([IMP-0083](logs/improvement-log.jsonl)).

### Regression — independently checked, not read from the manifest

**849 / 850 Pester tests pass, 0 failed, 1 skipped** — parsed directly from `build/artifacts/revitalise-grant-automation-20260823-2/test-results/pester-results.xml` (`total="850" errors="0" failures="0" skipped="1"`), matching the manifest's prose exactly and confirming the `IMP-0212` fix is real, not merely claimed: `verify-improvement-log.py --check` (re-run this session) shows `IMP-0212` at `status: APPLIED`, and the earlier build (`revitalise-grant-automation-20260823-1`) that halted on it is superseded.

**`no-secured-columns-in-code-app`, `gitleaks --no-git`, `verify-domain-invariants.py` — all three re-run directly, all PASS**, matching manifest figures exactly (55 authored files / 0 of 51 secured columns referenced / 3 fail-closed columns present; 0 leaks, 9.12 MB scanned; 20/20 special-category columns audited, C-DOM-030/031/032 in sync).

**`verify-pipeline-config.py` re-run independently: PASS — 81 steps, 3 environments**, including confirmation that the `code-apps-feature` prerequisite is declared and owned (`C-TECH-065`'s third rung).

### Live verification against DEV — new this round

Via the documented cert-based Web API method, against `REV-GrantApplications-DEV`:

| # | Query | Result |
|---|---|---|
| 1 | `pac code list` | **Confirms live**: `REV Trustee Review Portal`, appId `70869c95-92e5-442f-b5b9-44b3d3e549f6` — matches [power.config.json](src/code-apps/trustee-review-portal/power.config.json#L1) exactly. This is the fact that changes this round's constraint outcome (see below) |
| 2 | `role` (`REV Trustee`) → `systemuserroles_association` | **0 direct assignments** — unchanged from revision 9.1's finding; no trustee test account has been created yet |
| 3 | `team` filtered `contains(name,'Trustee')` | **0 results** — no `REV Trustees` team exists; app sharing (`A-TR-3`) has not progressed |
| 4 | `fieldsecurityprofile` (`REV_TrusteeRestricted`) → `teamprofiles_association` | **0 member teams** — the positive-control gap [TAD's own V4 step](config/revitalise-grant-automation-pipeline.yml#L799) warns about is unchanged |
| 5 | `EntityDefinitions('rev_review')` → `IsAuditEnabled`; `rev_reviews` row count | `IsAuditEnabled = True` (no regression from revision 9.1's fix) — **but row count is 2, not 0**. See D-027 |
| 6 | `audits?$filter=_objectid_value eq <id>` for both `rev_review` rows | **Both carry a Create audit record** (`action=1`/`operation=1`), timestamps matching `createdon` exactly — so despite D-027 below, **no unaudited write occurred**; `C-DOM-010`/`C-DOM-011`/`C-TECH-064` are unaffected |

### Defects raised this round

| Id | Severity | Status | Detail |
|---|---|---|---|
| **D-027** | **P4** | **OPEN** | Two `rev_review` rows (`c11014a4-fd9d-f111-b8de-7ced8d43e1b4`, `3acf8fc9-1f9e-f111-b8de-7ced8d43e87d`, both `createdon` 2026-08-22, `rev_outcome=null`) remain live in DEV. [Dev Summary](docs/development/revitalise-grant-automation-dev-summary.md#L5014) states the `A-TR-10` verification's test row and its control's upserted row "were both deleted afterward" — query 5/6 above contradicts this. Not a compliance issue (query 6 confirms both writes were audited, and `EX-003` permits test data in DEV), so rated P4 rather than P2: it is a documentation-accuracy and data-hygiene defect, not a data-protection one. Fix: delete both rows, and re-word the dev summary's claim or re-verify before making it. Logged as [IMP-0218](logs/improvement-log.jsonl) |
| D-002 | P2 | OPEN, unchanged | Carried since revision 3. Not touched this round |
| D-004 | P2 | OPEN, unchanged | Carried since revision 9. Accessibility layer still not executed for the trustee portal (no axe-core/Lighthouse tooling exists in this repo; static review only, see revision 9 above) |

### Assumption register (Dev Summary §10, WBS 6.1–6.5) — the precondition that changes this round's outcome

At revision 9.1, ten rows were "genuinely still OPEN, and not closeable in DEV as it stands" because **the Code App itself had never been pushed** — `C-TECH-058` explicitly does not fire on a precondition that does not yet exist anywhere. Since then (dev summary revisions "Trustee Code App pushed to DEV" and "real Dataverse data sources wired", both 2026-08-22), five more rows closed by live verification, and — the fact this report adds — **the app is now genuinely live** (query 1 above), which changes whether the remaining rows are "closeable":

| Assumption | State at revision 9.1 | State now | Closeable in DEV today? |
|---|---|---|---|
| A-TR-2, A-TR-6, A-TR-7, A-TR-10, A-TR-12 | CLOSED (2) / OPEN (3) | **All 5 CLOSED** — E1 evidence per [Dev Summary §10](docs/development/revitalise-grant-automation-dev-summary.md#L4861) | n/a |
| A-TR-1, A-TR-4, A-TR-5, A-TR-8, A-TR-9, A-TR-11 | OPEN, not closeable (app not pushed) | **OPEN** | **YES — the app is live (query 1) and DEV permits direct role assignment (query 2 confirms 0 taken, not 0 available). Nothing but naming a test user blocks closure.** This is what makes `C-TECH-058` fire this round |
| A-TR-3 | OPEN, not closeable | **OPEN** | **NO** — blocked by a Windows-only `Cert:\` PSDrive dependency in `share-apps.ps1`'s code/canvas branch, confirmed failing on this Mac two independent ways ([Dev Summary](docs/development/revitalise-grant-automation-dev-summary.md#L5022)). This is a tooling gap, not a decision the reviewer can close by naming a person, so `C-TECH-058` treats it the same way revision 9.1 treated all ten — genuinely not closeable here |

Deciding *who* tests as the trustee is explicitly framed as "the reviewer's call, not this session's to make" ([Dev Summary #L5041](docs/development/revitalise-grant-automation-dev-summary.md#L5041)) — but `C-TECH-058` does not treat an undecided reviewer choice as a reason to stay open once the means to decide it exists.

Logged as [IMP-0219](logs/improvement-log.jsonl): the register's own OPEN/CLOSED column is accurate for its report date and goes stale the moment the environment moves, independent of any source change.

### Requirement coverage — what the register gap actually means for FR-034/036/038

| FR ID | Requirement | Test Case(s) | Result |
|---|---|---|---|
| [FR-034](docs/plans/revitalise-grant-automation-plan.md#L339) | Sortable/filterable summary list | Code App unit tests (228/228); live read **not yet exercised by a trustee identity** | **PARTIAL** — Dev Summary's own words: "implemented but not yet met" ([#L4910](docs/development/revitalise-grant-automation-dev-summary.md#L4910)) pending `prvReadrev_applicant` reaching a real signed-in trustee |
| [FR-035](docs/plans/revitalise-grant-automation-plan.md#L340) | Detail view: redacted narrative, score, holiday details, recommendation | Code App unit tests; static `no-secured-columns-in-code-app` PASS | **PARTIAL** — built and statically verified; live rendering unconfirmed (V4 pending) |
| [FR-036](docs/plans/revitalise-grant-automation-plan.md#L341) | Withhold identifying info from every trustee view — **the core anonymisation requirement** | `no-secured-columns-in-code-app`, `no-trustee-in-column-security-profile`, `visibility.ts` fail-closed logic (all static, all PASS) | **NOT YET PROVEN LIVE** — query 4 above: zero member teams in `REV_TrusteeRestricted`, so no positive control exists; this is precisely the V4 step [pipeline.yml names by id](config/revitalise-grant-automation-pipeline.yml#L778) and precisely what the register rows above gate |
| [FR-037](docs/plans/revitalise-grant-automation-plan.md#L342) | Decision capture (Approve/Defer/Reject + notes) | `slots.ts` unit tests; `A-TR-10` live positive/negative control on the write guard | **PARTIAL** — the write mechanism is proven live; a real trustee submitting a verdict is not (V5, explicitly deferred — [pipeline.yml #L813](config/revitalise-grant-automation-pipeline.yml#L813)) |
| [FR-038](docs/plans/revitalise-grant-automation-plan.md#L343) | Restrict to current-round-eligible applications | Depends on the same `prvReadrev_applicant` privilege reaching a live trustee as FR-034 | **PARTIAL** — same gap as FR-034 |
| [FR-039](docs/plans/revitalise-grant-automation-plan.md#L344) | Print/offline export | Print route built ([Dev Summary hours proposal](docs/development/revitalise-grant-automation-dev-summary.md#L4901): "print route done, access test not performed") | **PARTIAL** — built, not live-tested |
| FR-040 | Apply verdicts to grant records, initiate acceptance | `REV \| Portal \| Finalise Decisions` flow ([TAD §5.7](docs/architecture/revitalise-grant-automation-architecture.md#L675)) | **OUT OF SCOPE for WBS 6.1–6.5** — a later automation, not built in this slice; not a gap in this delivery |

### WBS deliverable status

[WBS 6.5](contract/wbs.json#L902)'s own contracted deliverable is **"Shared app + access test."** Neither half is complete: the app is not yet shared to a `REV Trustees` group team or any equivalent (query 3), and the access test cannot run without a named trustee identity (query 2). Per `agents/test-agent.md`'s WBS section, a task whose deliverable names a test with no test result is carried as an **open item with an owner** — the owner here is the reviewer (naming a test user is explicitly their call, not this session's, per [Dev Summary](docs/development/revitalise-grant-automation-dev-summary.md#L5038)).

### Verification levels reached

| Component group | Level | Evidence |
|---|---|---|
| Trustee Code App (`pac code push`) | **V3** accepted, live | Query 1, independently confirmed — not read from the manifest |
| Four real Dataverse data sources | **V3** for the connector binding; **V2** for the app's own use of it | `pa app add data-source` × 4 succeeded (per dev summary); no live read has been observed through the app itself |
| `REV Trustee` role, `rev_review` table + 4 new columns | **V3**, unchanged from revision 9/9.1 | Already closed (A-TR-2/6/7) |
| Anonymisation control (`REV_TrusteeRestricted`) | **Designed and statically proven; V4 NOT reached** | Query 4 — zero member teams, no positive control possible yet |
| Human open-and-save (V4) | **NOT reached** | No named person has opened the app since it was pushed |
| End-to-end execution (V5) | **NOT reached, and explicitly not claimed** | [pipeline.yml #L813](config/revitalise-grant-automation-pipeline.yml#L813): "NOT REACHABLE FOR THIS SLICE" — decision enactment is WBS 6.6, not built |

- Idempotency: not re-run this pass (same rationale as revision 9 — provisioning writes are pipeline-agent's remit)
- Cross-OS (`C-TECH-054`): session ran on macOS; no new OS-specific code introduced this round (four `pa app add data-source` calls, a test-file fix) — **carried, unchanged, unproven on the CI runner for the sixth report revision running** ([IMP-0165](logs/improvement-log.jsonl): CI has never fired on a matching branch)
- Warnings triaged (`C-TECH-055`): 5 warnings in the manifest, all previously triaged, 0 untriaged, independently spot-checked

### Test layers

| Layer | Result |
|---|---|
| Unit | **PASS** — 849/0/1, confirmed from the packaged results XML directly |
| Integration | **NOT EXECUTED** — needs a live trustee identity |
| End-to-End | **NOT EXECUTED**, and not claimed (V5 explicitly out of scope this slice) |
| Regression | **PASS** — five-table + `rev_review` audit state unchanged and reconfirmed; no prior pass now fails |
| Security | **PASS on structure, NOT PROVEN live** — all three static gates re-run and PASS; zero-member-team gap (query 4) means no positive control of the anonymisation control exists yet |
| Accessibility | **NOT EXECUTED** — carried in D-004 |
| Performance | **NOT EXECUTED** — no NFR threshold measured live |
| Provisioning | **PARTIAL** — role/table/audit/app-push all confirmed live; group-team creation and app sharing not yet done |
| **Platform Contract** | **PASS, with one correction (D-027)** — register otherwise consistent with source; no orphan hand-authored contract found |
| **Verification Level** | See table above — no overclaim found in either the manifest or the dev summary this round |
| Cross-OS | **NOT PROVEN** — carried, unchanged |
| Constraint Verification | See below |

### Constraint verification

| Constraint | Result | Evidence |
|---|---|---|
| [C-DOM-004](constraints/domain/domain-constraints.md#L37) | PASS | `domain-invariants`, re-run: `rev_errorlog` holds no special-category column |
| [C-DOM-010](constraints/domain/domain-constraints.md#L47) | PASS | Query 5/6: `rev_review` audited, both live rows carry Create audit records |
| [C-DOM-011](constraints/domain/domain-constraints.md#L48) | PASS | Same evidence — audit records carry action/operation/timestamp as required |
| [C-DOM-030](constraints/domain/domain-constraints.md#L92) | PASS | `domain-invariants`, re-run: 20/20 in sync |
| [C-DOM-031](constraints/domain/domain-constraints.md#L93) | PASS | 16 secured, 4 documented exceptions, all printed |
| [C-DOM-032](constraints/domain/domain-constraints.md#L94) | PASS in source | 20/20 enabled in source; live half is C-TECH-064 below |
| [C-TECH-001](constraints/technology/technology-constraints.md#L34) | PASS | `gitleaks --no-git`, re-run: 0 leaks, 9.12 MB scanned |
| [C-TECH-004](constraints/technology/technology-constraints.md#L37) | PASS | No new user-input surface; Dataverse connector calls parameterise by construction |
| [C-TECH-006](constraints/technology/technology-constraints.md#L39) | PASS by platform design, live negative control pending | Entra sign-in is mandatory to reach any Power Apps Code App; a non-trustee's reachability is untested live pending V4 |
| [C-TECH-014](constraints/technology/technology-constraints.md#L52) | PASS | 86.36% ≥ 80% (manifest); Code App 97.78% |
| [C-TECH-040](constraints/technology/technology-constraints.md#L82) | PASS for what exists | Query 2: 0 direct assignments; DEV permits direct assignment by design |
| [C-TECH-042](constraints/technology/technology-constraints.md#L84) | PASS | `ensure-schema.ps1` idempotency covered by the 850-test suite |
| [C-TECH-045](constraints/technology/technology-constraints.md#L87) | PASS | No new connector; Dataverse connector only |
| [C-TECH-046](constraints/technology/technology-constraints.md#L88) | PASS | `REV Trustee` is a custom role, not an OOB edit |
| [C-TECH-048](constraints/technology/technology-constraints.md#L90) | PASS | `getClient(dataSourcesInfo)` from `@microsoft/power-apps/data`; no hand-rolled auth anywhere in the four new services |
| [C-TECH-051](constraints/technology/technology-constraints.md#L93) | PASS | `REV Trustee` roleid and `rev_review`'s ids all read back live, none fabricated |
| [C-TECH-052](constraints/technology/technology-constraints.md#L107) | PASS | 12-row register, no orphan hand-authored contract found |
| [C-TECH-053](constraints/technology/technology-constraints.md#L108) | PASS | No overclaim found; V4 is a named, owned step in [pipeline.yml](config/revitalise-grant-automation-pipeline.yml#L778) |
| [C-TECH-054](constraints/technology/technology-constraints.md#L109) | WARN — not proven | Session ran on macOS; no new OS-specific code this round; carried, sixth revision running |
| [C-TECH-056](constraints/technology/technology-constraints.md#L111) | PASS | The `account` smoke-test binding was cleanly removed and recorded ([dev summary #L5110](docs/development/revitalise-grant-automation-dev-summary.md#L5110)); D-027's two rows are data, not solution components, and do not travel via export — tracked separately, not a C-TECH-056 violation |
| [C-TECH-057](constraints/technology/technology-constraints.md#L127) | PASS | 39 steps / 28 gates, all with negative-test coverage (manifest) |
| **[C-TECH-058](constraints/technology/technology-constraints.md#L128)** | **VIOLATION** | Six §10 rows (A-TR-1,4,5,8,9,11) are now closeable in DEV — the app is live (query 1) and direct role assignment is available (query 2) — but remain OPEN with no reviewer `OVERRIDE`. See "Assumption register" above |
| [C-TECH-064](constraints/technology/technology-constraints.md#L134) | PASS | Query 5/6: live matches declared intent; both `rev_review` rows audited |
| [C-TECH-065](constraints/technology/technology-constraints.md#L135) | PASS | `verify-pipeline-config.py`, re-run: `code-apps-feature` prerequisite declared and owned |
| [C-TECH-066](constraints/technology/technology-constraints.md#L136) | PASS | `tad-coverage` (manifest): 129 column specs, 39 owned deferrals, 15 trustee-visible columns confirmed readable |
| [C-TECH-067](constraints/technology/technology-constraints.md#L137) | WARN (SOFT, as designed) | `source-derived-test-counts`: 6 fragile literal counts of 7 source-coupled assertions, reported not blocking (manifest) |

```
CONSTRAINT CHECK
Domain   HARD: 6 / 6  of 6   |  violations: NONE
                             |  unevaluable: NONE
Domain   SOFT: 0             |  warnings:   NONE  (no domain SOFT row is scoped to test-agent)
Tech     HARD: 20 / 21 of 21 |  violations: C-TECH-058
                             |  unevaluable: NONE
                             |  warn: C-TECH-054 (whole session ran on macOS, not the CI runner OS — carried, sixth revision)
  C-TECH-058: A-TR-1, A-TR-4, A-TR-5, A-TR-8, A-TR-9, A-TR-11 are closeable in DEV today (app
              live, direct role assignment available) but remain OPEN with no reviewer OVERRIDE
Tech     SOFT: 1             |  warnings:   C-TECH-067 (6 fragile literal counts, SOFT by design, not blocking)
Overall: BLOCKED
```

```
GATE BLOCKED
Reason: HARD constraint violation — see CONSTRAINT CHECK above (C-TECH-058).
Resolve the violation and re-run this agent to re-check.
```

### What resolving this needs — two paths, either is sufficient

**Path A — close the rows for real.** Name a DEV test user (not an administrator, and not anyone also holding `REV Admin`), assign them `REV Trustee` directly in the maker portal (permitted in DEV, [pipeline.yml #L759](config/revitalise-grant-automation-pipeline.yml#L759)), then perform the [V4 access test](config/revitalise-grant-automation-pipeline.yml#L778) exactly as pipeline.yml specifies — including the positive control (read the same record as the process owner first, confirm the identifying columns come back populated, before trusting an empty result from the trustee). This closes A-TR-1/4/5/8/9/11 and satisfies WBS 6.5's access-test deliverable in the same step. A-TR-3 stays open regardless (tooling defect, not a naming decision) and does not block this path.

**Path B — the reviewer accepts the risk explicitly.** Send `OVERRIDE <A-nnn>` for each row (e.g. `OVERRIDE A-TR-1, OVERRIDE A-TR-4, ...`) with a reason, to be recorded in the Deployment Summary per `C-TECH-058`'s own text. This does not perform the access test — WBS 6.5 would still carry an open item — but it un-blocks the constraint gate for anything else in this build that pipeline-agent needs to move.

Either way, D-027 (the two orphaned test rows) should be cleared before Path A's access test runs, so the trustee's own review of `rev_review` rows is not confused by leftover diagnostic data.

### Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-0218 | `platform-state-divergence` | rework | A dev summary's claim that a diagnostic test row "was deleted afterward" is a claim, not a result — re-query the live table for the specific ids before accepting a stated cleanup as fact |
| IMP-0219 | `assumption-register-precondition-crossed-mid-register` | friction | When a register defers a row with "not closeable until X exists", re-check specifically whether X now exists at the start of the next test cycle, rather than re-reading the register's own OPEN/CLOSED column as still current |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py`

IMPROVEMENT LOG: 2 entries appended — IMP-0218, IMP-0219  |  digest regenerated: YES

---

## Retest, 2026-08-24 — report revision 11 (build #2, WBS 0.4 finance tables)

**WBS:** `0.4`
**Artifact:** `build/artifacts/revitalise-grant-automation-20260824-2/` — manifest `build_number` 2, source commit `a072849a0af068600170c5e96075dabf06cfe253`, 42 uncommitted paths at pack time (no solution/provisioning content changed since build #1 — only a build-gate exemption comment and the improvement log)
**Handoff:** `HANDOFF | from:lead-agent | to:test-agent | feature:revitalise-grant-automation | status:READY | doc:docs/development/revitalise-grant-automation-dev-summary.md | artifact:build/artifacts/revitalise-grant-automation-20260824-2/ | wbs:0.4`
**Result:** **FAIL** — constraint gate **BLOCKED**, 2 new **P2** live defects (D-028, D-029), 0 new source/code defects.

### What this round covers

WBS `0.4`'s four remaining tables — `rev_provider`, `rev_bankaccount`, `rev_payment`, `rev_anonymisedstatistic` — plus `REV_FinanceOnly` field security. The handoff named two live defects the reviewer had already fixed and re-run: `IMP-0254` (`rev_provider` requested impossible Assign/Share privileges — [dev summary #L5633](docs/development/revitalise-grant-automation-dev-summary.md#L5633)) and `IMP-0255`/`IMP-0259` (five lookup columns' `IsSecured` flag dropped by `ConvertTo-RevRelationshipBody` — [dev summary #L5682](docs/development/revitalise-grant-automation-dev-summary.md#L5682)). It also asked this report to confirm, by live query, that the table-level Read restriction on `rev_bankaccount`/`rev_payment` — the control the reviewer's acceptance of the `rev_provideridname` name-leak residual depends on ([dev summary #L5746](docs/development/revitalise-grant-automation-dev-summary.md#L5746)) — is actually in place.

**Independently executed this session, not read from the manifest or the handoff's prose** (`C-TECH-053` applied to this report itself): 12 live Dataverse queries against `REV-GrantApplications-DEV` using the certificate-based method ([IMP-0083](logs/improvement-log.jsonl)), the full Pester suite (`src/tests/Invoke-Tests.ps1`), `gitleaks --no-git`, and eleven source-side build gates run bare (`verify-role-privilege-ownership.py`, `verify-field-security-coverage.py`, `verify-declared-property-reaches-creation-path.py`, `verify-domain-invariants.py`, `verify-guid-syntax.py`, `verify-solution-root-components.py`, `verify-source-reader-plurality.py`, `verify-pipeline-config.py`, `verify-build-config.py`, `verify-tad-coverage.py`, `verify-audited-tables.py`, `verify-source-derived-test-counts.py`, `verify-improvement-log.py --check`).

### Regression — independently re-run, not read from the manifest

**875 / 876 Pester tests pass, 0 failed, 1 skipped**, matching the manifest exactly (74.7s). All eleven source-side gates listed above re-run bare and matched the manifest's own figures exactly (e.g. `field-security-coverage`: 67 secured columns / 1 reviewed exemption / 2 accepted platform-limit warnings; `role-privilege-ownership`: PASS; `source-reader-plurality`: 35 readers plurality-safe; `tad-coverage`: 129 column specs, 9 deferred). `gitleaks --no-git` re-run: 0 leaks, 10.11 MB scanned. No regression found anywhere in source.

### Live verification against DEV — new this round

Via the documented cert-based Web API method (`provisioning/common/provisioning-common.ps1` + `provisioning-cert.psm1`), against `REV-GrantApplications-DEV`:

| # | Query | Result |
|---|---|---|
| 1 | `EntityDefinitions(LogicalName='<t>')?$select=OwnershipType` × 4 new tables | All 4 exist live, `OwnershipType` matches source exactly (`rev_provider`/`rev_anonymisedstatistic` OrganizationOwned, `rev_bankaccount`/`rev_payment` UserOwned) |
| 2 | `Attributes(LogicalName='rev_name')?$select=IsSecured` × `rev_bankaccount`, `rev_payment` | Both `IsSecured=False` — the `IMP-0249` primary-name fix is live and holding, no regression |
| 3 | `Attributes(LogicalName='<lookup>')?$select=IsSecured,CanBeSecuredForRead` × the 5 lookups `IMP-0255` names | **All 5 still report `IsSecured=False`**, all 5 `CanBeSecuredForRead=True` — the platform accepts the flag, source declares it, and it is still not live. **This is the fact that drives this round's result** |
| 4 | `fieldsecurityprofiles?$filter=name eq 'REV_FinanceOnly'` then its `fieldpermissions` | id `93d339bc-289f-f111-b8de-7ced8d43e87d` matches source exactly (`A-FIN-03` reconfirmed) — but only **11 of the intended 16** field permissions exist live. The 5 missing are exactly the 5 lookups in query 3: Dataverse will not create a field permission against an unsecured column |
| 5 | `privileges?$filter=endswith(name,'rev_provider')` and each role's `roleprivileges_association`, resolved to names | `REV Admin` and `REV Service Automation` both bind exactly the 6 privileges that exist for an OrganizationOwned table (Create/Read/Write/Delete/Append/AppendTo) — **no Assign/Share requested, none missing.** `IMP-0254`'s fix is fully live |
| 6 | `roleprivileges_association` for `REV Admin`, `REV Trustee` on `rev_bankaccount`/`rev_payment` | **Zero privileges of any kind** — confirmed by listing every bound privilege on both roles and finding no `rev_bankaccount`/`rev_payment` privilege name among them. `REV Trustee` separately confirmed to correctly hold `prvReadrev_anonymisedstatistic` (25 bound privileges total, one of them this) |
| 7 | Same query for `REV Service Automation` | Holds Read/Create/Write/Append/AppendTo on both tables, no Delete — matches the documented design (cascade-only removal) |
| 8 | `RelationshipDefinitions(SchemaName='<n>')` × 9 declared relationships | All 9 present, `CascadeConfiguration.Delete` matching source exactly (5 Cascade, 3 Restrict, 1 RemoveLink) — `A-FIN-01`'s shape closure reconfirmed, no regression from the latest live run |
| 9 | `Attributes(LogicalName='rev_amount')/Microsoft.Dynamics.CRM.DecimalAttributeMetadata` | `Decimal`, Precision 2, Min 0, Max 100000000, `IsSecured=True` — `A-FIN-02` reconfirmed, no regression |
| 10 | `Attributes(LogicalName='rev_provideridname')?$select=CanBeSecuredForRead` × `rev_bankaccount`, `rev_payment` | Both `False` — the accepted name-leak residual is exactly as documented, nothing new |
| 11 | `organizations?$select=isauditenabled` and `EntityDefinitions(...)?$select=IsAuditEnabled` × all 10 custom tables | Org-level auditing **On**; all 6 pre-existing tables **`IsAuditEnabled=True`**; **all 4 new WBS `0.4` tables `IsAuditEnabled=False`** |
| 12 | Row counts on all 4 new tables | **0 rows in all four** — the two gaps above are live control gaps, not yet a realised data-exposure or unaudited-write incident |

### Defects raised this round

| Id | Severity | Status | Detail |
|---|---|---|---|
| **D-028** | **P2** | **OPEN** | The `IMP-0255`/`IMP-0259` fix (`ensure-schema.ps1` step 3b, [#L529](provisioning/dataverse/ensure-schema.ps1#L529)) has not reached DEV: queries 3–4 above show all 5 Tier 4 lookup columns on `rev_bankaccount`/`rev_payment` still unsecured, and `REV_FinanceOnly` still 5 permissions short of its intended 16. The handoff for this round stated the reviewer's re-run fixed this alongside `IMP-0254` — it did not. Defence in depth holds (query 6: no other role can read either table), so no data has actually leaked, but the control the design calls for is not there. Logged as [IMP-0270](logs/improvement-log.jsonl) |
| **D-029** | **P2** | **OPEN** | All 4 new WBS `0.4` tables are live in DEV with `IsAuditEnabled=False` (query 11), the same class as `D-025`/`D-026` on earlier tables ([IMP-0085](logs/known-failure-modes.md#L238), [IMP-0178](logs/known-failure-modes.md#L438)). Source already declares the intent correctly (`dev-auditing-settings.json`, `verify-audited-tables.py` PASS) — this is purely a missed live step (`ensure-auditing.ps1 -Env dev` not yet (re-)run since these tables were created). 0 rows exist on any of the four, so nothing has actually gone unaudited yet. Logged as [IMP-0271](logs/improvement-log.jsonl) |
| D-002, D-004, D-027 | P2 / P2 / P4 | unchanged | Trustee Review Portal (WBS 6.x) defects — outside this round's scope, not re-checked |

### Assumption register (Dev Summary §10, WBS 0.4) — closure checked live, not read from the narrative

| Assumption ID | Claim | Status per Dev Summary | Closing precondition | Does it exist yet? | Verified by test-agent | Result |
|---|---|---|---|---|---|---|
| A-FIN-01 | Provider→BankAccount/Grant/Payment `Restrict`-delete relationship shape accepted | VERIFIED 2026-08-24 (V3) | n/a — closed | — | Query 8: reconfirmed live, unchanged | **PASS** (V5 residual stands: a delete-while-referenced attempt has never been made) |
| A-FIN-02 | `rev_payment.rev_amount` Decimal shape accepted | CLOSED | n/a — closed | — | Query 9: reconfirmed live, unchanged | **PASS** |
| A-FIN-03 | `REV_FinanceOnly`'s real id resolves and is substituted | VERIFIED 2026-08-23 | n/a — closed | — | Query 4: id matches exactly | **PASS** |
| **A-FIN-04** | Attribute-level `IsSecured` PATCH (step 3b) is accepted and lands | **OPEN** per Dev Summary | Reviewer re-runs `ensure-schema.ps1 -Env dev`, reports `CREATED — Column security on lookup` on all 5 | **The environment exists (DEV is live) and the reviewer already has write access to it — nothing outside a shell invocation blocks closing this today** | Query 3: all 5 still `IsSecured=False` | **FAIL — still OPEN, closeable in DEV, not closed → `C-TECH-058` violation** |
| A-FIN-05 | Deep-insert `IsSecured` on a freshly-*created* relationship (not a PATCH) | OPEN, deferred to first fresh-environment run | Cannot close in DEV — all 5 relationships already exist there | No (structurally not closeable here) | Unaffected — consistent with dev summary | **OPEN, not a C-TECH-058 violation** (matches its own documented non-closeability) |

### Requirement coverage

WBS `0.4`'s deliverable is **"Dataverse solution + table schema"** ([contract/wbs.json#L224](contract/wbs.json#L224)) — not one of the seven tasks whose deliverable names a test/sign-off. Schema existence is now fully met live: all 4 tables, the `rev_grant.rev_providerid` lookup, and all 9 relationships are confirmed live (queries 1, 8). This closes the schema-existence half of [`EX-001`](contract/known-exceptions.json#L7) (task 0.4 claiming "Done" while 5 tables were absent) — whether building them under `0.4` rather than the `6.4`/`8.1` split `EX-001` and `TD-001` originally named also settles the exception is a WBS-attribution question for `pm-agent`/`commercial-agent`, not this report's to decide (dev summary already flags this at [#L5468](docs/development/revitalise-grant-automation-dev-summary.md#L5468)). No FR is written against the finance tables directly — the TAD records they exist to satisfy US-015 AC-1 and NFR-002, with no automation flow yet in scope ([TAD §3.5 conflict 2](docs/architecture/revitalise-grant-automation-architecture.md#L464)).

### Verification levels reached

| Component | Level claimed | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| 4 tables, 9 relationships, `rev_amount` shape | V3 (Dev Summary, 2026-08-24) | **V3** | Queries 1, 8, 9 | PASS |
| `REV_FinanceOnly` id substitution | V3 (Dev Summary, 2026-08-23) | **V3** | Query 4 | PASS |
| `rev_provider` role privileges (`IMP-0254` fix) | V3 (handoff claim) | **V3 — reached** | Query 5, no FAILED pattern anywhere in the bound set | PASS |
| 5 lookup columns' field security (`IMP-0255`/`IMP-0259` fix) | V3 (handoff claim: "run once successfully after both fixes") | **V1 only — NOT reached** | Query 3/4: source is correct and gate-clean, live state is not | **FAIL — claimed level not reached** |
| Table-level Read restriction on `rev_bankaccount`/`rev_payment` (the confidentiality residual's actual control) | Not previously live-verified | **V3** (role-privilege binding, live) | Queries 6, 7 | **PASS at V3.** V4/V5 (a real signed-in REV Admin or REV Trustee attempting the read and being refused) NOT performed — no test identity exists for this, and a live sign-in is outside what this session can execute |
| Table audit switch, 4 new tables | Not claimed (silent) | **Not live** | Query 11 | **FAIL — C-TECH-064 requires live parity with declared intent; not met** |

- **Idempotency:** not re-run this pass — the write itself (`ensure-schema.ps1 -Env dev`) is refused by this session's own permission classifier, same as every prior round touching live DEV writes ([IMP-0084](logs/improvement-log.jsonl), [IMP-0245](logs/improvement-log.jsonl)). The reviewer's next re-run is simultaneously the fix and the idempotency proof.
- **V4 designer/editor open + save:** not required yet — these 4 tables are schema-only by WBS `0.4`'s own description, with no form/view built (build manifest: 8 accepted `forms-and-views-reachable` warnings for exactly this reason). Not a gap in this round.
- **Cross-OS (`C-TECH-054`):** this session's verification ran on macOS, not the CI runner; no new OS-specific code introduced. Carried, unchanged, unproven on CI for the seventh report revision running ([IMP-0165](logs/improvement-log.jsonl)).
- **Warnings triaged (`C-TECH-055`):** both `field-security-coverage` warnings (Money `_base`, lookup-name companions) independently reconfirmed as previously-accepted, not new.

### Test layers

| Layer | Result |
|---|---|
| Unit | **PASS** — 875/0/1, independently re-run, matches manifest |
| Integration | **NOT APPLICABLE** — schema-only, no flow/UI touches these tables yet |
| End-to-End | **NOT APPLICABLE** — no automation built against these tables (TAD §3.5 conflict 2) |
| Regression | **PASS** — all 11 independently re-run source gates match the manifest; no prior pass now fails |
| Security | **FAIL** — D-028: 5 Tier 4 columns live-unsecured; the table-level control they were meant to back up remains sound (queries 6–7), but the column-level layer is not there |
| Accessibility | N/A — no UI in this dispatch's scope |
| Performance | N/A — no NFR threshold applies to schema-only work |
| Provisioning | **PARTIAL** — tables/relationships/one of two role fixes confirmed live; audit switches (D-029) and the lookup-security reconcile (D-028) are not |
| **Platform Contract** | **PASS, register consistent with source** — every A-FIN row has a source comment and a register row; no orphan hand-authored contract found |
| **Verification Level** | **Overclaim found** — the handoff's claimed V3 for the `IMP-0255`/`IMP-0259` fix is not reached (see table above) |
| Cross-OS | NOT PROVEN — carried, unchanged |
| Constraint Verification | See below |

### Constraint verification

| Constraint | Result | Evidence |
|---|---|---|
| [C-DOM-004](constraints/domain/domain-constraints.md#L37) | PASS | `domain-invariants`, re-run: `rev_errorlog` unaffected, holds no special-category column |
| [C-DOM-010](constraints/domain/domain-constraints.md#L47) | **VIOLATION (new tables only)** | Query 11: `IsAuditEnabled=False` on all 4 new tables — no create/update/delete on them can be audit-logged right now. The 6 pre-existing tables are unaffected and remain compliant |
| [C-DOM-011](constraints/domain/domain-constraints.md#L48) | **VIOLATION (new tables only)** | Same evidence — no audit record can exist for these 4 tables to carry the required fields |
| [C-DOM-030](constraints/domain/domain-constraints.md#L92) | PASS | `domain-invariants`, re-run: 20/20 in sync; no special-category column on any new finance table |
| [C-DOM-031](constraints/domain/domain-constraints.md#L93) | PASS | `field-security-coverage`, re-run: 16 secured (of 67 solution-wide), 4 documented exceptions, unchanged |
| [C-DOM-032](constraints/domain/domain-constraints.md#L94) | PASS in source | 20/20 enabled in source, unaffected by this dispatch — live half is `C-TECH-064` below, per this row's own text |
| [C-TECH-001](constraints/technology/technology-constraints.md#L34) | PASS | `gitleaks --no-git`, re-run: 0 leaks, 10.11 MB |
| [C-TECH-004](constraints/technology/technology-constraints.md#L37) | PASS | No new input surface; schema/security only |
| [C-TECH-006](constraints/technology/technology-constraints.md#L39) | PASS | Query 6: `REV Admin`/`REV Trustee` correctly hold zero privilege on `rev_bankaccount`/`rev_payment` |
| [C-TECH-014](constraints/technology/technology-constraints.md#L52) | PASS | 81.8% ≥ 80% (manifest; not independently recomputed with coverage tooling this round) |
| [C-TECH-040](constraints/technology/technology-constraints.md#L82) | PASS | No group-team requirement introduced; DEV direct-assignment model unaffected |
| [C-TECH-042](constraints/technology/technology-constraints.md#L84) | PASS (declaration) | `provisioning-step-convergence` (manifest): step 3b carries its `CONVERGENCE:` declaration; the live re-run that proves convergence in practice is the reviewer's next action, not performed by this session |
| [C-TECH-045](constraints/technology/technology-constraints.md#L87) | PASS | No new connector |
| [C-TECH-046](constraints/technology/technology-constraints.md#L88) | PASS | All three roles remain custom, no OOB edit |
| [C-TECH-048](constraints/technology/technology-constraints.md#L90) | PASS | No Code App change in this dispatch's scope |
| [C-TECH-051](constraints/technology/technology-constraints.md#L93) | PASS | Query 4: `REV_FinanceOnly`'s live id matches source exactly, no fabricated id |
| [C-TECH-052](constraints/technology/technology-constraints.md#L107) | PASS | 5-row register (A-FIN-01..05), each with a source `A-nnn` comment; `root-components-resolve` 64/64, no orphan found |
| [C-TECH-053](constraints/technology/technology-constraints.md#L108) | **VIOLATION** | The handoff claimed V3 for both `IMP-0254` and `IMP-0255`/`IMP-0259` fixes together; only `IMP-0254` reaches V3 (query 5). Exactly the overclaim pattern this constraint's 2026-08-23 amendment exists to catch — caught here because the live query was actually run rather than trusted |
| [C-TECH-054](constraints/technology/technology-constraints.md#L109) | PASS, carried caveat | Session ran on macOS; no new OS-specific code this round; unproven on CI runner, 7th revision running |
| [C-TECH-056](constraints/technology/technology-constraints.md#L111) | PASS | This session's two live-read probe scripts were written only to the session scratchpad, never to the repository |
| [C-TECH-057](constraints/technology/technology-constraints.md#L127) | PASS | Manifest: 43 steps/32 gates, all with negative-test coverage; 4 spot-checked gates (`role-privilege-ownership`, `field-security-coverage`, `declared-property-reaches-creation-path`, `source-reader-plurality`) all reproduce their manifest figures bare |
| **[C-TECH-058](constraints/technology/technology-constraints.md#L128)** | **VIOLATION** | `A-FIN-04` is closeable in DEV today (the reviewer already has write access; nothing external blocks it) but remains OPEN with no reviewer `OVERRIDE`. See "Assumption register" above |
| [C-TECH-059](constraints/technology/technology-constraints.md#L129) | PASS | Own artifact directory used; `IMP-0270`/`IMP-0271` appended this round; digest regenerated (268 entries) |
| [C-TECH-060](constraints/technology/technology-constraints.md#L130) | PASS | `field-length-limits` (manifest): unaffected by this dispatch |
| **[C-TECH-064](constraints/technology/technology-constraints.md#L134)** | **VIOLATION** | Query 11 (audit switches off on 4 live tables, contradicting declared intent) and queries 3–4 (5 field-permission bindings absent from a profile membership that declares them) — both are exactly what this constraint requires be checked live and both diverge from source |
| [C-TECH-065](constraints/technology/technology-constraints.md#L135) | PASS | Environment-access pattern unaffected; DEV prerequisite exercised repeatedly this session via live auth |
| [C-TECH-066](constraints/technology/technology-constraints.md#L136) | PASS | `tad-coverage`, re-run: 129 column specs, 9 deferred, unchanged |
| [C-TECH-067](constraints/technology/technology-constraints.md#L137) | WARN (SOFT, as designed) | `source-derived-test-counts`, re-run: 10 fragile literal counts of 13, unchanged, pre-existing |
| [C-TECH-068](constraints/technology/technology-constraints.md#L138) | PASS (not triggered) | No V4 finance access test is being claimed this round; the route-closure half of this constraint's own first check was applied informally via queries 6–7. `verify-access-test-identity.ps1` remains scoped to the trustee V4 test only — extending it to finance is a recommendation, not a violation here |
| [C-TECH-069](constraints/technology/technology-constraints.md#L140) | PASS | `source-reader-plurality`, re-run: 35 readers plurality-safe |
| [C-TECH-070](constraints/technology/technology-constraints.md#L141) | PASS | `field-security-coverage`, re-run: PASS, 2 accepted platform-limit warnings (Money `_base`, lookup-name companions), both previously reviewed |
| [C-TECH-071](constraints/technology/technology-constraints.md#L142) | PASS (source) | `declared-property-reaches-creation-path`, re-run: 38 pairs checked, 1 accepted known gap (lookup `IsAuditEnabled` default). The code correctly reaches the creation path — the live gap (D-028) is that the reviewer's write reaching DEV has not happened, which is `C-TECH-058`/`064`, not `071` |

```
CONSTRAINT CHECK
Domain   HARD: 4 / 6  of 6    |  violations: C-DOM-010, C-DOM-011
                              |  unevaluable: NONE
Domain   SOFT: 0              |  warnings:   NONE (no domain SOFT row is scoped to test-agent)
Tech     HARD: 22 / 25 of 25  |  violations: C-TECH-053, C-TECH-058, C-TECH-064
                              |  unevaluable: NONE
  C-DOM-010/011:  4 new tables are IsAuditEnabled=False live (query 11) — no audited create/update/
                  delete is possible on rev_provider/rev_bankaccount/rev_payment/rev_anonymisedstatistic today
  C-TECH-053:     handoff claimed V3 for both live fixes; only IMP-0254 reaches V3 (query 5) —
                  IMP-0255/IMP-0259 remains V1 (query 3/4)
  C-TECH-058:     A-FIN-04 is closeable in DEV today, remains OPEN, no reviewer OVERRIDE
  C-TECH-064:     live state (queries 3, 4, 11) diverges from declared intent (source) on both
                  field-permission membership and table auditing
Tech     SOFT: 1              |  warnings:   C-TECH-067 (10 fragile literal counts, SOFT by design, not blocking)
Overall: BLOCKED
```

```
GATE BLOCKED
Reason: HARD constraint violations — see CONSTRAINT CHECK above (C-DOM-010, C-DOM-011,
        C-TECH-053, C-TECH-058, C-TECH-064).
Resolve the violations listed and re-run this agent to re-check.
```

### What resolving this needs

**One live action closes every violation raised this round.** The reviewer re-runs:

```
pwsh -NoProfile -File provisioning/dataverse/ensure-schema.ps1 -Env dev
pwsh -NoProfile -File provisioning/dataverse/ensure-auditing.ps1 -Env dev
```

`ensure-schema.ps1`'s step 3b (already on disk, already unit-tested) is what PATCHes the 5 lookups' `IsSecured` flag and lets the 5 missing field permissions be created; `ensure-auditing.ps1` is what the four `IsAuditEnabled=False` tables still need — a separate script, since table auditing is not something a solution import or `ensure-schema.ps1` itself sets ([IMP-0086](logs/improvement-log.jsonl)). Both are idempotent and safe to run against the current DEV state (steps already correct report `EXISTS`, nothing is undone).

**After that run, confirm with a fresh live read rather than trusting the console output** — the exact trap this round exists to name:

```
EntityDefinitions(LogicalName='rev_payment')/Attributes(LogicalName='rev_grantid')?$select=IsSecured
EntityDefinitions(LogicalName='rev_bankaccount')?$select=IsAuditEnabled
```

Expect `IsSecured=true` on all 5 lookups and `IsAuditEnabled` (`Value`) `=true` on all 4 new tables. Since all 4 tables hold 0 rows (query 12), there is no cleanup needed — this closes cleanly with no data-hygiene residual, unlike `D-027` on the trustee side.

**No source change is needed.** Every source-side gate for this dispatch is green; this is the second consecutive WBS `0.4` round where the fix is entirely in the environment, not the repository.

### Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-0270 | `platform-state-divergence` | blocker | A handoff's claim that a live re-run "succeeded after both fixes" is a claim, not a result — re-query each defect's own closing condition independently, never infer that one fix landing means a sibling fix from the same dispatch did too |
| IMP-0271 | `platform-state-divergence` | blocker | A newly-created Dataverse table needs its own `ensure-auditing.ps1` pass before any row is written to it — creating the table and enabling its audit switch are two separate live actions, and the gap is invisible to every source-side gate |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py` (268 entries)

IMPROVEMENT LOG: 2 entries appended — IMP-0270, IMP-0271  |  digest regenerated: YES

---

## Retest, 2026-08-24 — report revision 12 (build #3, `ensure-auditing.ps1` PATCH→PUT fix)

**WBS:** `0.4`
**Artifact:** `build/artifacts/revitalise-grant-automation-20260824-3/` — manifest `build_number` 3, source commit `fc5fb1de590fc51225bf6c07ef7db65499086b60`, 7 uncommitted paths at pack time (the `ensure-auditing.ps1`/`ensure-schema.ps1`/`ensure-schema-helpers.psm1` fix plus its Pester fixtures and the build-config steps added the same day — no solution/schema source dirty)
**Handoff:** `HANDOFF | from:build-agent | to:test-agent | feature:revitalise-grant-automation | status:READY | wbs:0.4 | doc:docs/development/revitalise-grant-automation-dev-summary.md | artifact:build/artifacts/revitalise-grant-automation-20260824-3`
**Result:** **FAIL** — constraint gate **BLOCKED**, 1 new HARD violation ([C-TECH-052](constraints/technology/technology-constraints.md#L107)), 2 HARD rows **UNEVALUABLE** this session (a first for this feature's test history), 0 new source/code defects.

### What this round covers

The [`ensure-auditing.ps1`](provisioning/dataverse/ensure-auditing.ps1) table-level auditing write, corrected from a `PATCH`-with-partial-body (rejected live, `0x80060888`, [IMP-0276](logs/improvement-log.jsonl)) to a full-object `PUT` against the uncast `EntityDefinitions` URI ([IMP-0277](logs/improvement-log.jsonl)), per Dev Summary revision at [#L5964](docs/development/revitalise-grant-automation-dev-summary.md#L5964) and its new register row [A-FIN-07](docs/development/revitalise-grant-automation-dev-summary.md#L6021). No solution/schema source is part of this dispatch's diff — this is a provisioning-script-only fix.

**Independently executed this session, not read from the manifest** (`C-TECH-053` applied to this report itself): full read of the corrected script (`ensure-auditing.ps1` lines 1–215) against Microsoft's documented metadata-write shape; `pwsh src/tests/Invoke-Tests.ps1 -Path provisioning` (the CI path, [IMP-0026](logs/improvement-log.jsonl)); `gitleaks detect --no-git`; `python3 scripts/verify-metadata-write-verbs.py` standalone; `python3 scripts/verify-provisioning-step-convergence.py` standalone; `python3 scripts/verify-audited-tables.py` standalone; `python3 scripts/verify-improvement-log.py --check`; a grep of `ensure-auditing.ps1` for an `A-FIN-07` source comment; and an attempted live read against `REV-GrantApplications-DEV` via the cert-based method ([IMP-0083](logs/improvement-log.jsonl)).

### Regression — independently re-run, not read from the manifest

**611 / 611 Pester tests pass, 0 failed, 1 skipped** (24.1s via `src/tests/Invoke-Tests.ps1 -Path provisioning`), matching the manifest's provisioning-suite figure exactly. `gitleaks --no-git`: 0 leaks, 10.73 MB scanned. `metadata-write-verbs`: **PASS** — 66 Dataverse API calls across 33 provisioning scripts, every metadata write a `PUT` to an uncast URI — direct, standalone reconfirmation of the [C-TECH-073](constraints/technology/technology-constraints.md#L143) gate the manifest reports, not merely a re-read of its output. `provisioning-step-convergence`: **PASS** — 35 numbered steps (21 read-only, 5 reconciling, 9 create-only, all 9 carrying a `CONVERGENCE:` declaration); `ensure-auditing.ps1`'s two steps classify as **reconciling** (check-then-write-only-if-different), which is why neither needs its own declaration — confirmed by reading the script's own `# ── N.` markers, not assumed. `audited-tables`: **PASS** — all 10 tables declared in `dev-auditing-settings.json`, `test-settings.json`, `prd-settings.json`. No regression found anywhere in source.

### Live verification attempt — refused before it could run

Using the exact cert-based method that report revisions 9, 10 and 11 all used successfully against `REV-GrantApplications-DEV` ([IMP-0083](logs/improvement-log.jsonl)/[IMP-0022](logs/improvement-log.jsonl)), a **read-only** probe (one `organizations` GET plus ten `EntityDefinitions(...)?$select=IsAuditEnabled` GETs, zero writes) was attempted to establish the current live audit state ahead of judging [A-FIN-07](docs/development/revitalise-grant-automation-dev-summary.md#L6021)'s closeability. The invocation was refused outright: *"Permission for this action was denied by the Claude Code auto mode classifier. Reason: Blocked by classifier."*

This is a materially different position from every prior round on this feature: revisions 9–11 all obtained live evidence. [IMP-0084](logs/improvement-log.jsonl) recorded that "read-only queries... ran freely all session" while only a write was refused; this session's refusal fired on a pure read. Logged as [IMP-0287](logs/improvement-log.jsonl) — Auto Mode does not distinguish read from write for a cert/keychain-touching command, so **this session has zero live-Dataverse reach, not merely no-write reach**, and cannot independently confirm or contradict the Dev Summary's claim that the reviewer already closed the live gap by hand in the admin portal.

### Assumption register (Dev Summary §10) — closure checked, not read from the narrative

| Assumption ID | Claim | Status per Dev Summary | Closing precondition | Verified by test-agent | Result |
|---|---|---|---|---|---|
| [A-FIN-07](docs/development/revitalise-grant-automation-dev-summary.md#L6021) | Full-object `PUT` to uncast `EntityDefinitions(LogicalName='<t>')`, `IsAuditEnabled.Value` flipped, is accepted and persists | **OPEN** | Reviewer re-runs `ensure-auditing.ps1 -Env dev`; requires `CREATED`/`EXISTS` with zero `FAILED`, then a live read confirming `true` | Live read attempted, refused by classifier ([IMP-0287](logs/improvement-log.jsonl)) | **Still OPEN — this session could not move it either way** |
| [A-FIN-06](docs/development/revitalise-grant-automation-dev-summary.md#L5881) | Full-object `PUT` to `Attributes(...)` for lookup `IsSecured` | OPEN (unrelated to this dispatch) | Reviewer re-runs `ensure-schema.ps1 -Env dev` | Not re-checked this round — outside this dispatch's diff | Unchanged |

**A-FIN-07 has no source marker.** Per [C-TECH-052](constraints/technology/technology-constraints.md#L107) ("carries an `A-nnn` comment at the point of the guess in source") and `skills/how-to-verify-a-platform-contract.md` §4 ("mark the guess where it lives, too"), the register row names `ensure-auditing.ps1#L171` as *Where* — but grepping that file for `A-FIN` finds nothing; only `IMP-0276`/`IMP-0277` are referenced. Its sibling row A-FIN-06, added the same day for the same class of fix, **does** carry its marker in `ensure-schema.ps1`. Logged as [IMP-0286](logs/improvement-log.jsonl).

### Requirement coverage

WBS `0.4`'s deliverable is **"Dataverse solution + table schema"** ([contract/wbs.json#L224](contract/wbs.json#L224)) — not one of the seven tasks whose deliverable names a test/sign-off. This dispatch adds no schema; it corrects a provisioning script's write verb. No FR is written against table-level auditing directly — it implements [C-DOM-010](constraints/domain/domain-constraints.md#L47)/[C-DOM-011](constraints/domain/domain-constraints.md#L48)/TAD §6.5.

### Verification levels reached

| Component | Level claimed (Dev Summary §11) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| `ensure-auditing.ps1` table-level write (GET-full-object → strip `@odata.*` → PUT-uncast) | V1/V2 only, explicitly | **V1/V2 — matches claim** | Direct read of the script against Microsoft's documented shape; 611/611 Pester; `metadata-write-verbs` PASS | **PASS — no overclaim** |
| Same write, live acceptance (A-FIN-07) | Not claimed above V2 | **NOT REACHED — this session has no path to V3** | Live read refused by classifier | **Consistent with the Dev Summary's own statement, but this session adds no independent confirmation either way** |

- **Idempotency:** not assessable this round — the write itself, and even a read of current state, are both refused by this session's own permission classifier ([IMP-0287](logs/improvement-log.jsonl)), a stricter block than every prior round ([IMP-0084](logs/improvement-log.jsonl), [IMP-0245](logs/improvement-log.jsonl)).
- **Cross-OS (`C-TECH-054`):** this session ran on macOS, not the CI runner; no OS-specific code in this dispatch. Carried, unchanged, unproven on CI for the eighth report revision running ([IMP-0165](logs/improvement-log.jsonl)).

### Test layers

| Layer | Result |
|---|---|
| Unit | **PASS** — 611/0/1, independently re-run via the CI path, matches manifest |
| Integration | **PASS** — Pester suite exercises the corrected GET→mutate→PUT round-trip against a faked Web API, including the `@odata.context` strip and the full-object body assertion |
| End-to-End | **NOT APPLICABLE** — no user-facing flow or UI touches this script |
| Regression | **PASS** — all five independently re-run source/build gates match the manifest |
| Security | **NOT EVALUATED** — the control this fix exists to restore (audit logging on 4 live tables) has an unconfirmed live state this round; see Constraint verification |
| Accessibility | N/A — no UI in this dispatch's scope |
| Performance | N/A — no NFR threshold applies |
| Provisioning | **PARTIAL** — script confirmed correct at V1/V2; live acceptance (V3) blocked this session, same as the write path it corrects |
| **Platform Contract** | **VIOLATION found** — A-FIN-07 register row has no source `A-nnn` marker ([C-TECH-052](constraints/technology/technology-constraints.md#L107)) |
| **Verification Level** | **No overclaim** — Dev Summary §11 correctly states V1/V2 only; this is the first round on this feature where the developer-side claim itself is not the problem |
| Cross-OS | NOT PROVEN — carried, unchanged |
| Constraint Verification | See below |

### Constraint verification

Full scope for test-agent: 6 Domain HARD, 26 Tech HARD (`C-TECH-073` new this build), 1 Tech SOFT ([C-TECH-067](constraints/technology/technology-constraints.md#L137)). Rows unaffected by this dispatch are carried from round 11's independent verification rather than re-derived; rows touching this dispatch's actual change are re-checked live in this session.

| Constraint | Result | Evidence |
|---|---|---|
| [C-DOM-004](constraints/domain/domain-constraints.md#L37) | PASS | Unaffected by this dispatch; no new log surface |
| [C-DOM-010](constraints/domain/domain-constraints.md#L47) | **UNEVALUABLE (4 finance tables only)** | The 6 pre-existing tables' audit posture was independently confirmed live in round 11 and is unaffected here. The 4 finance tables' *current* state is exactly what this dispatch's fix concerns, and this session's live read was refused ([IMP-0287](logs/improvement-log.jsonl)) |
| [C-DOM-011](constraints/domain/domain-constraints.md#L48) | **UNEVALUABLE (4 finance tables only)** | Same evidence as C-DOM-010 |
| [C-DOM-030](constraints/domain/domain-constraints.md#L92) | PASS | Unaffected — no schema/scoring change in this dispatch |
| [C-DOM-031](constraints/domain/domain-constraints.md#L93) | PASS | Unaffected |
| [C-DOM-032](constraints/domain/domain-constraints.md#L94) | PASS in source | Unaffected; live half is C-DOM-010/011 above |
| [C-TECH-001](constraints/technology/technology-constraints.md#L34) | PASS | `gitleaks --no-git`, re-run: 0 leaks, 10.73 MB |
| [C-TECH-004](constraints/technology/technology-constraints.md#L37) | PASS | No new input surface |
| [C-TECH-006](constraints/technology/technology-constraints.md#L39) | PASS | Unaffected |
| [C-TECH-014](constraints/technology/technology-constraints.md#L52) | PASS | 81.81% ≥ 80% (manifest; code-app/solution coverage untouched by this provisioning-only dispatch) |
| [C-TECH-040](constraints/technology/technology-constraints.md#L82) | PASS | Unaffected |
| [C-TECH-042](constraints/technology/technology-constraints.md#L84) | PASS | `provisioning-step-convergence`, re-run standalone: `ensure-auditing.ps1`'s two steps correctly classify as reconciling |
| [C-TECH-045](constraints/technology/technology-constraints.md#L87) | PASS | Unaffected |
| [C-TECH-046](constraints/technology/technology-constraints.md#L88) | PASS | Unaffected |
| [C-TECH-048](constraints/technology/technology-constraints.md#L90) | PASS | No Code App change |
| [C-TECH-051](constraints/technology/technology-constraints.md#L93) | PASS | Unaffected |
| **[C-TECH-052](constraints/technology/technology-constraints.md#L107)** | **VIOLATION** | A-FIN-07 register row exists (Dev Summary §10) with no `A-FIN-07` source comment in `ensure-auditing.ps1`. [IMP-0286](logs/improvement-log.jsonl) |
| [C-TECH-053](constraints/technology/technology-constraints.md#L108) | **PASS** | Dev Summary §11 and the manifest both state V1/V2 only, explicitly declining V3 — no overclaim to catch this round |
| [C-TECH-054](constraints/technology/technology-constraints.md#L109) | PASS, carried caveat | macOS session, unproven on CI runner, unchanged |
| [C-TECH-056](constraints/technology/technology-constraints.md#L111) | PASS | This session's probe script was written only to the session scratchpad, never to the repository |
| [C-TECH-057](constraints/technology/technology-constraints.md#L127) | PASS | Manifest: 46 steps/35 gates, all negative-test covered; unaffected |
| **[C-TECH-058](constraints/technology/technology-constraints.md#L128)** | **UNEVALUABLE** | A-FIN-07 is OPEN. The Dev Summary argues DEV cannot presently close it (audit switches already converged to `true` via the reviewer's portal workaround, so a re-run would report `EXISTS` everywhere and never exercise the write) — but that premise rests on a live state this session could not read ([IMP-0287](logs/improvement-log.jsonl)). Whether DEV *could* close it today is genuinely unknown from here |
| [C-TECH-059](constraints/technology/technology-constraints.md#L129) | PASS | Own artifact directory used; `IMP-0286`/`IMP-0287` appended this round, digest regenerated (284 entries) |
| [C-TECH-060](constraints/technology/technology-constraints.md#L130) | PASS | Unaffected |
| [C-TECH-064](constraints/technology/technology-constraints.md#L134) | **UNEVALUABLE** | Requires a live read comparing declared intent to actual state; this session's only attempt was refused before it ran ([IMP-0287](logs/improvement-log.jsonl)) |
| [C-TECH-065](constraints/technology/technology-constraints.md#L135) | PASS | Unaffected |
| [C-TECH-066](constraints/technology/technology-constraints.md#L136) | PASS | Unaffected |
| [C-TECH-067](constraints/technology/technology-constraints.md#L137) | WARN (SOFT, as designed) | Unaffected, pre-existing |
| [C-TECH-068](constraints/technology/technology-constraints.md#L138) | PASS (not triggered) | No V4 access-test claim this round |
| [C-TECH-069](constraints/technology/technology-constraints.md#L140) | PASS | Unaffected |
| [C-TECH-070](constraints/technology/technology-constraints.md#L141) | PASS | Unaffected |
| [C-TECH-071](constraints/technology/technology-constraints.md#L142) | PASS | Unaffected |
| **[C-TECH-073](constraints/technology/technology-constraints.md#L143)** | **PASS** | `metadata-write-verbs`, re-run standalone (not read from the manifest): 66 API calls / 33 scripts, every metadata write a `PUT` to an uncast URI — direct mechanical reconfirmation of the `ensure-auditing.ps1` fix this dispatch packages |

```
CONSTRAINT CHECK
Domain   HARD: 4 / 4  of 6    |  violations: NONE
                              |  unevaluable: C-DOM-010, C-DOM-011 (4 finance tables' live state only)
Domain   SOFT: 0              |  warnings:   NONE
Tech     HARD: 23 / 24 of 26  |  violations: C-TECH-052
                              |  unevaluable: C-TECH-058, C-TECH-064
Tech     SOFT: 1              |  warnings:   C-TECH-067 (pre-existing, unrelated to this dispatch)
  C-DOM-010/011: 4 finance tables' current audit state unconfirmed — this session's only live-read
                 attempt was refused by the Auto Mode classifier before it ran (IMP-0287)
  C-TECH-052:    A-FIN-07 register row has no A-nnn source marker in ensure-auditing.ps1 (IMP-0286)
  C-TECH-058:    A-FIN-07 OPEN; whether DEV can close it today is unconfirmed, not established
                 either way, by this session
  C-TECH-064:    the live comparison this row requires could not be executed this session
Overall: BLOCKED
```

```
GATE BLOCKED
Reason: HARD constraint violation (C-TECH-052) and HARD constraints UNEVALUABLE this session
        (C-DOM-010, C-DOM-011, C-TECH-058, C-TECH-064) — see CONSTRAINT CHECK above.
Resolve the violation and the live-verification gap, then re-run this agent to re-check.
```

### What resolving this needs

**Two independent things, neither a source change to the script under test:**

1. **One comment line closes [C-TECH-052](constraints/technology/technology-constraints.md#L107).** Add an `A-FIN-07` marker in `ensure-auditing.ps1` near line 171 (or the PUT at line 200–202), matching how `A-FIN-06` is marked in `ensure-schema.ps1`. Trivial, additive, no behaviour change.

2. **Only the reviewer can move A-FIN-07, C-TECH-058 and C-TECH-064 off `UNEVALUABLE`** — this session's cert-based method is blocked outright under Auto Mode, for reads as well as writes ([IMP-0287](logs/improvement-log.jsonl)). Run, in a non-Auto-Mode / interactive session:

```
EntityDefinitions(LogicalName='rev_provider')?$select=IsAuditEnabled
EntityDefinitions(LogicalName='rev_bankaccount')?$select=IsAuditEnabled
EntityDefinitions(LogicalName='rev_payment')?$select=IsAuditEnabled
EntityDefinitions(LogicalName='rev_anonymisedstatistic')?$select=IsAuditEnabled
```

   If any read `false`: `pwsh -NoProfile -File provisioning/dataverse/ensure-auditing.ps1 -Env dev` — expect `CREATED` on that table, which is the V3 evidence A-FIN-07 needs, and closes D-029 ([IMP-0271](logs/improvement-log.jsonl)) at the same time. If all four already read `true`: the portal workaround holds, but note (per the Dev Summary's own trap) that re-running the script now will report `EXISTS` throughout and **still not exercise the write path** — A-FIN-07's V3 evidence for the corrected code itself then waits on the first TST/ACC or PRD run, or the next new DEV table.

**Separately, and not part of this test cycle's own gate:** the improvement log currently fails its own check (`python3 scripts/verify-improvement-log.py --check` exits 1) — two blocker-severity entries sit `NEW`/unread with no `deferred_reason`: [IMP-0285](logs/improvement-log.jsonl) (this build's own queue-processing finding, which already predicted this) and [IMP-0287](logs/improvement-log.jsonl) (logged this session). Per `agents/WORKFLOW.md`, a blocker routes to `improvement-agent` immediately — this is outside test-agent's own constraint scope ([C-TECH-061](constraints/technology/technology-constraints.md#L131) does not name test-agent), but it will fail the *next* build's `unit-tests` step exactly as it failed this build's attempt 1, so it is flagged here rather than left for someone to rediscover.

### Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-0286 | `declared-policy-not-mechanically-enforced` | rework | A Dev Summary §10 row's "Where" column naming a line number is not proof an `A-nnn` source marker exists there — grep for it before treating the row as complete |
| IMP-0287 | `harness-blocks-destructive-call` | blocker | Under Auto Mode, a cert/keychain-touching pwsh command is refused regardless of whether every call inside it is a read — a test-agent session dispatched under Auto Mode has zero live-Dataverse reach, not merely no-write reach |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py` (284 entries)

IMPROVEMENT LOG: 2 entries appended — IMP-0286, IMP-0287  |  digest regenerated: YES
