# Dev Summary Document — Location Column for the Grant Admin

**Feature Slug:** grant-admin-app
**TAD Reference:** `docs/architecture/grant-admin-app-architecture.md` (APPROVED, reviewer Anna Southern)
**Date:** 2026-09-23
**Status:** DRAFT
**WBS task:** `0.11` (`contract/change-orders/CO-003.md`)

---

## 1. Implementation Summary

Two new columns on `rev_applicant` — `rev_localauthority` (text, the resolved local authority
name) and `rev_localauthoritystatus` (choice: Resolved / Multi-Authority / Not Known) — populated
at intake by a new step in the existing `REVIntakeWordPressToDataverse` flow, inserted immediately
after `Compute_outward_code` per the TAD. The step looks up the sibling `wbs:4.6` register
(`rev_localauthorityregister`) by the same outward code `rev_locationarea`'s own derivation already
computes, and writes both new columns alongside the existing `rev_agerange`/`rev_locationarea`
write. Both columns are secured the same way as their sibling `rev_locationarea`: released to the
Grant Administrator role and `REV Service Automation` via `REV_TrusteeRestricted`, excluded from
trustees by non-membership (FR-256). A new global option set (`rev_localauthoritystatus`) and two
new controls on the Applicant main form complete the change. No new persona, role, group, or
relationship — additive only, per FR-255.

**wbs:4.6 (the register itself) is a parallel, separately-evidenced dispatch and was not touched.**
Per the dispatch instruction and the TAD's own §5/§8/§9, this flow step runs correctly whether or
not the register is yet seeded in a given environment — a miss and an unseeded register are
indistinguishable, and both resolve to `Not Known`, not a flow error.

## 2. Components Changed / Created

| Component | Type | Change Description | FR Reference |
|---|---|---|---|
| `Entities/rev_applicant/Entity.xml` | Schema | Two new attributes: `rev_localauthority` (nvarchar 100, secured), `rev_localauthoritystatus` (picklist, secured) | FR-250, FR-256 |
| `OptionSets/rev_localauthoritystatus.xml` | New global option set | 100001 Resolved / 100002 Multi-Authority / 100003 Not Known | FR-252, FR-253, NFR-251 |
| `Other/Solution.xml` | Root component | Added `RootComponent type="9"` for the new option set (the entity's existing `type="1" behavior="0"` root component already covers the two new attributes) | — |
| `Other/FieldSecurityProfiles.xml` | Field permission | Two new `FieldPermission` rows on `REV_TrusteeRestricted`, same shape as the existing `rev_locationarea` row | FR-256, TAD §6 |
| `Entities/rev_applicant/FormXml/main/{5cb234cc-...}.xml` | Form | Two new controls added to the Contact Details section, immediately after `rev_locationarea` | FR-254, C-TECH-077 |
| `Workflows/REVIntakeWordPressToDataverse-...json` | Flow | Three new actions (`Find_local_authority_register_row`, `Derive_local_authority_status`, `Derive_local_authority`) inserted after `Compute_outward_code`; both new columns wired into `Create_new_applicant` and `Refresh_existing_applicant` | FR-251, FR-252, FR-253 |
| `Workflows/REVIntakeWordPressToDataverse-...notes.md` | Documentation | Full reasoning for the three new actions' condensed (≤256 char) in-JSON descriptions | — |

## 3. Data Model Changes

Two new columns on the existing `rev_applicant` table (TAD §3):

| Column | Type | Notes |
|---|---|---|
| `rev_localauthority` | Single line of text, max 100, `IsSecured=1`, `IsAuditEnabled=1` | Null unless `rev_localauthoritystatus = Resolved`. Frozen at intake, never re-derived (ADR-001) |
| `rev_localauthoritystatus` | Choice (new global option set `rev_localauthoritystatus`), `IsSecured=1`, `IsAuditEnabled=1` | `Resolved` (100001) / `Multi-Authority` (100002) / `Not Known` (100003) |

No relationships, no new tables. The register (`rev_localauthorityregister`, wbs:4.6) is read by
value at intake, never joined (TAD §3 Relationships, ADR-001).

## 4. Automation / Workflow Changes

In `REVIntakeWordPressToDataverse`, three new actions inserted between `Compute_outward_code` and
`Compute_postcode_prefixes` (chain re-wired so `Compute_postcode_prefixes` now runs after the new
`Derive_local_authority` instead of directly after `Compute_outward_code` — no other action's
`runAfter` changed):

1. `Find_local_authority_register_row` — `ListRecords` (never Get-by-id on an alternate key,
   IMP-0112) against the register, `$filter=rev_name eq '<outward code>'`, `$top=1`.
2. `Derive_local_authority_status` — Compose mapping the register's own status (or no row) onto
   this column's three-value set, per TAD §5's decision table.
3. `Derive_local_authority` — Compose, null unless status resolved to `Resolved`.

Both outputs are written into `item/rev_localauthority` / `item/rev_localauthoritystatus` (update
branch) and `rev_localauthority` / `rev_localauthoritystatus` (create branch), alongside the
existing `rev_agerange`/`rev_locationarea` writes.

**Sequencing note for pipeline-agent, restated from the TAD (§8, §9):** the register
(`wbs:4.6`) should be deployed and its first refresh run **before** this flow change goes live in
the same environment, independently per environment (DEV / TST-ACC / PRD each need their own
seeded register — data does not travel with a managed solution import). This is a recommendation,
not a build gate: neither task's build is blocked on the other, and every applicant intake before
the register is seeded reads `Not Known`, which is honest, not silently wrong. `wbs:4.6` was not
built or touched by this dispatch.

## 5. Configuration & Provisioning Changes

**None required.** `provisioning/dataverse/ensure-schema.ps1` is schema-source-driven — its entity
loop (`Get-RevEntityLogicalNames`), option-set loop (`Get-RevOptionSetDefinitions`) and field
security loop (`Get-RevFieldSecurityProfileDefinition`) all read the repository source directly, so
the two new attributes, the new option set, and the two new `FieldPermission` rows are picked up by
the **existing**, already-wired script with no code change. This is also the TAD §12.1 mitigation
for the `FieldPermission`-on-existing-profile risk (IMP-0637/IMP-0649): the script's step 6 already
creates each `fieldpermissions` row via a direct Web API `POST`, never via solution import.

No new provisioning script; no new `config/<slug>-pipeline.yml` `post_deploy` or
`environment_prerequisites` entries beyond what already exists generically for this solution (see
§8, Build Instructions, for why no new build/pipeline config file was produced either).

### Provisioning Scripts

| Script | Purpose | Pipeline Block | Idempotency Check |
|---|---|---|---|
| `provisioning/dataverse/ensure-schema.ps1` (unchanged) | Creates the two new attributes, the new global option set, and the two new field permissions, per environment | `environment_prerequisites` (already wired in `config/revitalise-grant-automation-pipeline.yml` for dev/tst_acc/prd) | Existing EXISTS/CREATED/FAILED reporting, unchanged |

## 6. Security Controls Implemented

| TAD §6 Control | Implementation |
|---|---|
| Authorisation — `REV_TrusteeRestricted` releases both columns to Grant Administrator + `REV Service Automation`, trustees excluded by non-membership | Two new `FieldPermission` rows added (§2 above); membership itself unchanged (ADR-G03 pattern, `IMP-0153`) |
| Data at rest — `IsSecured=1`, `IsAuditEnabled=1` | Set on both attributes in `Entity.xml` |
| Data in transit | Unchanged — existing Dataverse connector, TLS 1.2+ |
| Authentication | Unchanged — existing intake flow service principal |
| No new persona/role/group | Confirmed — no changes to `Roles/`, no new group team, no new Entra group |

**C-DOM-033 (special-category register) — proposed, not applied by this agent; confirmed blocked,
not merely anticipated.** OQ-252 is resolved (local authority is not Article 9 data), but that
does not exempt either column from adjudication. This agent **attempted** the edit to
`constraints/domain/special-category-register.yml` and was refused:

```
BLOCKED by .claude/hooks/protect-system-rules.py: this is a dispatched development-agent
subagent attempting Edit against constraints/, which only improvement-agent may write
(agents/improvement-agent.md#L12). Do not retry, do not route around this, and do not edit
the rule file yourself. Record the change you wanted as a finding in
logs/improvement-log.jsonl per skills/how-to-log-an-improvement.md and let an improvement
review apply it behind APPROVE IMPROVEMENTS.
```

Logged as **`IMP-0838`** (`blocker` — it currently fails a HARD build gate, `domain-invariants`,
confirmed below), per the hook's own instruction. The following two entries are proposed for
`pending_adjudication:`, for improvement-agent/the reviewer to apply:

```yaml
pending_adjudication:
  - entity: rev_applicant
    name: rev_localauthority
    reason: "IsSecured=1, not Article 9 data (OQ-252) — geographic administrative fact derived
      from postcode. Same posture as rev_locationarea, narrower audience (FR-256)."
  - entity: rev_applicant
    name: rev_localauthoritystatus
    reason: "IsSecured=1, same posture as rev_localauthority — adjudicated together."
```

**This was not silently skipped** — see the CONSTRAINT CHECK block below and this note. Build-agent's
`domain-invariants` step will fail (correctly) against `config/revitalise-grant-automation-build.yml`
until these two entries are applied — that must happen behind `APPROVE IMPROVEMENTS` before this
feature's next real build, not worked around.

## 7. Known Limitations / Deferred Items

- **Form control disabled state deviates from the TAD's stated assumption, matching the sibling's
  actual source instead.** TAD §8 describes the two new controls as "read-only-by-default...
  mirroring `rev_locationarea`'s own read-only treatment". Reading the actual FormXml,
  `rev_locationarea`'s own control is `disabled="false"` (editable), not read-only. Both new
  controls were built `disabled="false"` to genuinely mirror the sibling's real treatment rather
  than the TAD's stated (and, on inspection, incorrect) description of it. Low impact — both
  values are system-derived and nothing in this dispatch's scope depends on the distinction — but
  flagged rather than silently resolved either way.
- `wbs:4.6`'s register does not exist in source yet (parallel dispatch, not built by this session).
  Two assumptions in §10 below follow directly from that.
- `scripts/verify-tad-coverage.py`'s `C-TECH-066` gate does not scan this sibling TAD by default —
  same known, already-flagged gap as the sibling TAD's own §11 risk row. Not resolved here.
- **No `config/grant-admin-app-build.yml` / `-pipeline.yml` produced** — see §8 below. Logged as
  `IMP-0836` for a reviewer/architect decision.
- Historic backfill (SDD §8, out of scope) and OQ-251 (re-price question, commercial-agent) both
  carried forward unresolved, exactly as the SDD states.

## 8. Build Instructions

**No `config/grant-admin-app-build.yml` or `config/grant-admin-app-pipeline.yml` was produced,**
which is a deliberate, flagged deviation from the default per-feature template, not an omission:

- `.github/workflows/ci.yml`'s `SLUG` mechanism requires a file at exactly that path to run CI for
  a given feature slug.
- `scripts/verify-build-config.py`'s `suite-gate-is-not-a-step` check requires **every**
  `verify-*.py` / `--check`-exposing script under `scripts/` (~70 of them) to be wired as a step in
  **whichever** build config is being preflighted, with no per-config exemption mechanism. A new
  slug's build.yml cannot be a small, feature-scoped file — it would have to replicate nearly all
  of the existing ~1,000-line `revitalise-grant-automation-build.yml` and ~2,000-line
  `-pipeline.yml` to pass its own preflight.
- Git history confirms this has never been done: no feature slug other than the original
  `revitalise-grant-automation` has ever had its own build/pipeline config, across multiple prior
  change orders (CO-003 through CO-007) and WBS tasks landing in this same `RevitaliseGrantAutomation`
  solution.

Rather than silently duplicate ~3,000 lines (high drift risk, disproportionate to a two-column
change, and unprecedented) or silently skip config generation, **this is logged as `IMP-0836`** —
a `friction`-severity finding proposing a decision step in `agents/development-agent.md`: when a
feature lands in a solution that already has a working build/pipeline config, decide explicitly
whether it shares that config's CI slug or gets its own (budgeted for full gate-wiring), rather
than defaulting silently either way.

**In the meantime, this change is built and deployed as an addition to the existing
`revitalise-grant-automation` feature build** — `config/revitalise-grant-automation-build.yml` and
`config/revitalise-grant-automation-pipeline.yml`, unchanged, since:

- Both are already wired with every generic gate class this change touches (schema field-length,
  solution root components, flow-definition-language, forms-and-views-reachable,
  field-security-coverage, role-privilege-ownership) — all confirmed green against this exact
  change in §11 below.
- `provisioning/dataverse/ensure-schema.ps1`'s `environment_prerequisites` entry is already wired
  per environment and is schema-source-driven (§5) — it needs no new step to pick up these two
  columns.
- No new platform-limit class was introduced by this change, so no new build gate is needed.

## 9. Test Guidance

- **Happy path:** an applicant whose postcode's outward code resolves in the register to
  `Resolved` → `rev_localauthority` holds the register's name, `rev_localauthoritystatus = Resolved`.
- **Multi-authority:** outward code flagged `Multi-Authority` in the register →
  `rev_localauthority` null, `rev_localauthoritystatus = Multi-Authority`.
- **Miss / unseeded register:** outward code absent from the register (including "register table
  has zero rows because wbs:4.6 has not seeded it yet") → `rev_localauthority` null,
  `rev_localauthoritystatus = Not Known`. **This is the case to test FIRST in DEV**, since the
  register will likely not exist there yet when this flow is first tested.
- **NI Pending Licence:** once the register exists and has `BT`-prefixed rows, confirm those also
  collapse to `Not Known` here (TAD §3), not a fourth value.
- **Trustee non-visibility (FR-256):** confirm a trustee-authenticated read of `rev_applicant`
  cannot read either new column (same test shape as the existing `rev_locationarea` trustee-
  exclusion test, `IMP-0221`'s access-test caveat about confirming a real `REV_TrusteeRestricted`
  member exists before trusting a "null for everyone" result as a pass).
- **Regression:** `rev_agerange`, `rev_locationarea`, and every other existing intake-flow write
  must be unaffected — confirmed by the unchanged `runAfter` chain and unchanged outputs elsewhere
  in the flow (§4).

## 10. Unvalidated Assumptions Register (C-TECH-052)

| ID | Claim | Where in source | Evidence | Why not verified | Cheapest verification | Status |
|---|---|---|---|---|---|---|
| A-GAA-01 | The register's Dataverse entity set (collection) name is `rev_localauthorityregisters` (regular English pluralisation of `rev_localauthorityregister`, matching every other entity in this solution — `rev_applicant`→`rev_applicants`). If wrong, `Find_local_authority_register_row` fails loudly (404/`EntityNotFound`) on first run against an environment where the register exists, never silently. | [`src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json), action `Find_local_authority_register_row`; full reasoning in [the flow's `.notes.md`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.notes.md) | E4 (inference by analogy) | `rev_localauthorityregister` does not exist in source yet — `wbs:4.6` is a parallel, separately-evidenced dispatch this session was told not to touch, so there is no exported/live table to ground-truth the plural name against | Once `wbs:4.6` lands and is created in any environment, `GET EntityDefinitions(LogicalName='rev_localauthorityregister')?$select=EntitySetName` and compare | OPEN |
| A-GAA-02 | The register's own `rev_resolutionstatus` option values are exactly `Resolved`=100001, `Multi-Authority`=100002, `NI Pending Licence`=100003, as stated in `docs/architecture/postcode-lookup-architecture.md` §3 — `Derive_local_authority_status`'s branching logic depends on these exact numbers | [`src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json), action `Derive_local_authority_status`; full reasoning in [the flow's `.notes.md`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.notes.md) | E2 (first-party design doc for this solution, not yet built) | The register table and its option set do not exist in source or any environment yet | Once `wbs:4.6`'s option set is built, read `GlobalOptionSetDefinitions(Name='rev_localauthorityresolutionstatus')` and confirm the three values match | OPEN |

## 11. Verification Evidence (C-TECH-053, C-TECH-055, C-TECH-056)

### Verification level reached

| Component | Level reached | Environment / OS | Evidence (command + observed result) |
|---|---|---|---|
| `Entity.xml`, `OptionSets/rev_localauthoritystatus.xml`, `Solution.xml`, `FieldSecurityProfiles.xml`, `FormXml` | V2 — packages | macOS (dev workstation), `pac` 2.4.1 | `pac solution pack --folder src/solutions/RevitaliseGrantAutomation --zipfile /tmp/gaa-pack-check/RevitaliseGrantAutomation.zip --packagetype Unmanaged` → "Unmanaged Pack complete." Pre-existing "not defined in customizations" warnings for 9 EntityRelationships/EnvironmentVariableDefinitions are unrelated to this change (present before it) |
| `REVIntakeWordPressToDataverse-...json` | V1 — well-formed (JSON parse) + statically checked | macOS | `python3 -c "import json; json.load(...)"` → OK; `python3 scripts/verify-flow-definition-language.py src/solutions/RevitaliseGrantAutomation` → OK, no new findings |
| All schema/security/form changes | V1/V2 — statically checked against every applicable generic gate | macOS | See gate list below — all green |
| No environment exists for this feature yet | V3/V4/V5 not reached | — | Deferred to pipeline-agent; DEV import is the first opportunity to ground-truth A-GAA-01/A-GAA-02 if `wbs:4.6` has landed by then |

**Local gates run (all against the working tree, all green, zero new findings introduced by this
change):**

```
python3 scripts/verify-field-length-limits.py src/solutions/RevitaliseGrantAutomation provisioning/deploymentSettings
  → OK — 514 flow descriptions within 256 chars (was checked BEFORE the notes.md fix found 2 over-limit
    descriptions, which were shortened; this is the post-fix, passing run)
python3 scripts/verify-solution-root-components.py src/solutions/RevitaliseGrantAutomation
  → PASS - 79 root components declared, every one has a definition on disk, nothing undeclared
python3 scripts/verify-flow-definition-language.py src/solutions/RevitaliseGrantAutomation
  → OK - 9 flows, no new findings (3 pre-existing dated exceptions, unrelated to this change)
python3 scripts/verify-forms-and-views-reachable.py src/solutions/RevitaliseGrantAutomation
  → OK - 77 secured columns with a main-form control (was 75; +2 for this change), 6 pre-existing warnings
python3 scripts/verify-field-security-coverage.py src/solutions/RevitaliseGrantAutomation
  → PASS - 77 secured columns, every one released by a field security profile
python3 scripts/verify-role-privilege-ownership.py src/solutions/RevitaliseGrantAutomation
  → PASS - 113 table privileges, no change from this dispatch (no new table, no new privilege)
python3 scripts/verify-assumption-markers.py
  → PASS - 33 OPEN rows checked, every one (including A-GAA-01, A-GAA-02) carrying its marker in source
python3 scripts/verify-assumption-register.py
  → PASS - 94 rows across 33 registers, none contradicted by its own document
```

**`python3 scripts/run-source-gates.py config/revitalise-grant-automation-build.yml`** (this
feature has no `config/grant-admin-app-build.yml` — §8 explains why — so it is built via the
existing `revitalise-grant-automation` config; this is the derived gate set for that config,
16 of 84 steps): **2 of 16 red on first run, both fixed or tracked, not silently left red:**

- `shipped-content` — FAILED on first run: this dispatch's own new `<Description>` prose named
  `rev_localauthorityregister` and `rev_localauthorityresolutionstatus` as if they were columns in
  THIS solution (IMP-0008's exact class) — they are the sibling `wbs:4.6` dispatch's identifiers
  and do not exist here yet. **Fixed** by rewording both descriptions to refer to "a separate
  local-authority reference table" / "a separate resolution-status option set" without naming the
  not-yet-built identifiers. Re-run confirms zero dangling references from this change; the
  remaining `shipped-content` output (3 pre-existing `rev_application.rev_applicantid` form-label
  mismatches) predates this dispatch and is unrelated (present in the working tree before this
  session started).
- `domain-invariants` — FAILED, and **stays failed** until improvement-agent applies the
  `pending_adjudication:` entries above (`IMP-0838`) — this is the expected, TAD-anticipated
  handoff (§6), not a defect in this change.

### Tool warnings triaged (C-TECH-055)

| Warning | Source step | Resolved / Accepted | Rationale if accepted |
|---|---|---|---|
| `pac solution pack`: 9 "not defined in customizations" (EntityRelationships, EnvironmentVariableDefinitions) | `pac solution pack` (manual local run, V2 check) | Accepted, pre-existing | Present before this dispatch's changes; not caused by or related to the two new columns, the new option set, or the flow change. Not this feature's warning to resolve |
| `Find_local_authority_register_row` / `Derive_local_authority_status` action descriptions initially exceeded 256 chars (778 / 458 chars) | Authoring, caught by manual length check before running `verify-field-length-limits.py` | Resolved | Condensed to ≤256 chars in-JSON, full reasoning moved to the flow's `.notes.md`, per this project's own established pattern (see file header) |

### Diagnostic components created and removed (C-TECH-056)

| Component | Environment | Purpose | Removed (date / how) |
|---|---|---|---|
| None | — | No environment exists for this feature; no diagnostic component was created in any live environment | n/a |

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-0836 | `per-feature-build-config-vs-solution-scoped-gate-wiring` | friction | Before creating a new `config/<slug>-build.yml` for a feature landing in an already-provisioned solution, check whether the project shares the existing CI slug or budgets for full gate-wiring — do not silently duplicate or silently skip. |
| IMP-0838 | `pending-adjudication-entry-needed` | blocker | Add `rev_applicant.rev_localauthority` / `rev_localauthoritystatus` to `pending_adjudication:` in `constraints/domain/special-category-register.yml` (basis: geographic fact, not Article 9, per OQ-252) — confirmed BLOCKED for development-agent by the protection hook, as designed; apply behind `APPROVE IMPROVEMENTS` before the next real build. |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py` (834 entries, 826 distinct lessons)

---

## Code Review Checklist
- [x] All FR IDs covered (FR-250 through FR-256, NFR-250, NFR-251 — US-250's three acceptance criteria all traced in §9)
- [x] No hardcoded secrets
- [x] Security controls from TAD §6 implemented
- [x] Every TAD §12 item has an idempotent provisioning script wired into the pipeline config (§5 — reuses the existing, already-wired `ensure-schema.ps1` step; no new script needed)
- [x] Role assignments via group teams only — no direct user assignments (unchanged; no role/group change in this dispatch)
- [x] No hardcoded environment-specific IDs/URLs
- [x] Every guessed platform contract is in §10 **and** commented `A-nnn` in source (A-GAA-01, A-GAA-02, both present in the flow JSON description and the `.notes.md`)
- [x] Where an environment existed, ground truth was used instead of a guess — no environment exists for this feature; both open assumptions are correctly OPEN, not guessed-and-hidden
- [x] Every platform limit the packer/compiler does not enforce has a build gate — no new platform-limit class introduced; all existing generic gates re-run green
- [x] Verification levels in §11 are the levels actually executed (V1/V2 only — no environment exists)
- [x] Scripts run on the CI runner's OS — no new script written
- [x] Every tool warning triaged in §11; no diagnostic components left anywhere
- [ ] Accessibility requirements met (if UI) — form controls follow the existing MDA shell pattern (TAD §8); not independently re-verified this dispatch, consistent with "no new form/tab" scope
- [x] No dead code or debug statements
- [ ] Unit tests written — no new Pester/unit test added for the new flow branch this dispatch; flagged as a gap for test-agent, not silently skipped (see note below)

**Regression-test note (`skills/how-to-write-a-test-plan.md` line 80 applies to a defect fix, not
new-feature construction — this is new construction).** No existing automated test in
`src/tests/solutions/` exercises `REVIntakeWordPressToDataverse`'s per-action logic directly (the
existing suite targets contract/invariant shape, per `IntakeContract.Tests.ps1` and
`ScoringInvariants.Tests.ps1`); this dispatch did not add a new one for the three new actions,
consistent with that existing coverage boundary, but test-agent should confirm this is an accepted
gap rather than an oversight before sign-off.

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED`
