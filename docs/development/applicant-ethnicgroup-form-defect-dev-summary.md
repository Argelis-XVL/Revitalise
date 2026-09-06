# Dev Summary Document — Applicant form: missing Ethnic Group control

**Feature Slug:** applicant-ethnicgroup-form-defect
**WBS:** [0.4](../../contract/wbs.json#L224) — Dataverse solution & table schema build (defect fix against this task's own deliverable, the Applicant table + its form; not new scope)
**TAD Reference:** `docs/architecture/trustee-portal-visual-refresh-architecture.md` (Revision 8, closes A-R24)
**Date:** 2026-09-04
**Status:** DRAFT

---

## 1. Implementation Summary

`rev_ethnicgroup` has existed live on `rev_applicant` since 2026-08-27 — `IsSecured=1`, capture
reviewer-approved (`OQ-027`, [plan.md:2023](../../docs/plans/revitalise-grant-automation-plan.md#L2023),
resolved with the reviewer's own words on record at
[known-exceptions.json:56](../../contract/known-exceptions.json#L56): *"that should be present as
this gets filled in on the website form"*) — but had no control anywhere on the applicant's main
form,
[`{5cb234cc-f4af-4e97-a024-c71b7da66399}.xml`](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_applicant/FormXml/main/%7B5cb234cc-f4af-4e97-a024-c71b7da66399%7D.xml).
This blocked the reviewer from entering test applicant data with an ethnic-group value, which in
turn blocked reviewing the ethnic-group distribution chart just shipped on the trustee portal
(FR-061,
[architecture.md:1195](../../docs/plans/revitalise-grant-automation-plan.md#L1195)).

Fixed by adding one `<cell>`/`<control>` to the `sec_identity` section, directly after Gender and
before Date of Birth
([FormXml/main/{5cb234cc...}.xml:9](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_applicant/FormXml/main/%7B5cb234cc-f4af-4e97-a024-c71b7da66399%7D.xml#L9)),
using the exact same option-set control classid (`{3EF39988-22BB-4f0b-BBBE-64B5A3748AEE}`) as
`rev_gender`/`rev_agerange` immediately either side of it. Placement confirmed against the option
set definition (`rev_ethnicgroup` is a picklist of six ONS-style categories plus "Prefer not to
say" — the same shape and purpose as Gender's option set, not a classification/reporting dimension
like `rev_applicanttype`) and against `Entity.xml`'s own comment, which already narrates Ethnic
Group as sitting "immediately below" Gender
([Entity.xml:333](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_applicant/Entity.xml#L333)).
`sec_classification` was considered and rejected: that section holds reporting dimensions with no
identity content (`rev_applicanttype`, contact/audit dates), whereas Ethnic Group is
Article-9 special-category demographic capture of the same kind as Gender and Age Range, both in
`sec_identity`.

## 2. Components Changed / Created

| Component | Type | Change Description | FR Reference |
|---|---|---|---|
| [FormXml/main/{5cb234cc-f4af-4e97-a024-c71b7da66399}.xml](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_applicant/FormXml/main/%7B5cb234cc-f4af-4e97-a024-c71b7da66399%7D.xml#L9) | Model-Driven App FormXml | Added one `<row><cell>` in `sec_identity`, between the Gender row and the Date of Birth row: label "Ethnic Group", `control id="rev_ethnicgroup" classid="{3EF39988-22BB-4f0b-BBBE-64B5A3748AEE}" datafieldname="rev_ethnicgroup" disabled="false"`. New cell id `{49468c72-4079-4547-bd56-4ad1eaf156a9}` (freshly generated GUID; the platform assigns none of its own for a hand-authored cell, so none was fabricated as if it were, `C-TECH-051`). | FR-061 |

No entity, option set, field security profile, or AppModule component changed — all four already
exist and are already correctly wired (verified below).

## 3. Data Model Changes

**None.** `rev_ethnicgroup` already exists live in DEV
([Entity.xml:336-351](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_applicant/Entity.xml#L336),
[OptionSets/rev_ethnicgroup.xml](../../src/solutions/RevitaliseGrantAutomation/OptionSets/rev_ethnicgroup.xml)) —
confirmed explicitly rather than assumed, per the dispatch instruction:
`contract/tad-deferrals.json`'s own clearing note for `TD-005` states the column "now exists live
in `Entities/rev_applicant/Entity.xml`" as of 2026-08-27
(`IMP-0363`), and `grep` against `Entity.xml` in this session confirms the attribute, its
`OptionSetName="rev_ethnicgroup"` reference, and `IsSecured="1"` are all present today, unchanged
by this dispatch. This is a **form-surface-only** change: the schema half of `IMP-0122`'s "adding
a column is two deployments" rule does not apply here because no column is being added — only the
form cell, which travels in the solution import.

## 4. Automation / Workflow Changes

None.

## 5. Configuration & Provisioning Changes

None. No provisioning script change is needed: `rev_ethnicgroup`'s attribute, option set and
field-security-profile entry were all authored generically from XML on disk in the session that
built the column (`IMP-0363`), and this dispatch touches none of those files.

## 6. Security Controls Implemented

None changed. `rev_ethnicgroup` stays `IsSecured="1"` on `Entity.xml`, secured behind
`REV_TrusteeRestricted` exactly like `rev_gender`
([Entity.xml:344,349](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_applicant/Entity.xml#L344)).
Adding a form control changes only who can *see the field on the form they already have access
to* — the field security profile, not the form, is what governs access, and it is unchanged.

## 7. Known Limitations / Deferred Items

- **DPIA sign-off (`OQ-030`) remains a separate, still-open step for Emily/DPO** — unaffected by
  this fix; this dispatch does not touch it and does not purport to close it.
- **V4 (human open-and-save) not yet performed by this dispatch** — see §11.
- **Found, not fixed, while checking constraints for this dispatch:** `rev_ethnicgroup` — a column
  its own `Entity.xml` comment self-declares as UK GDPR Article 9 special-category data — is
  absent from `constraints/domain/special-category-register.yml`,
  [C-DOM-030](../../constraints/domain/domain-constraints.md#L92)'s declared "single source of
  truth". `verify-domain-invariants.py` still reports `PASS` because it checks the register
  against the FR-016 build-gate alternation, not against source completeness. This is
  pre-existing debt from the session that built the column (`IMP-0363`), not introduced by this
  dispatch's form-only change, and is out of this dispatch's WBS scope to fix per `C-COM-002` —
  logged as `IMP-0598` for whoever owns that register next, rather than fixed silently here.

## 8. Build Instructions

No change to `config/<slug>-build.yml` is needed. This is a FormXml-only change inside the
existing `RevitaliseGrantAutomation` solution; the existing pack/import build steps already cover
it. No new artifact type, provisioning script, or platform limit was introduced.

## 9. Test Guidance

- Open the Applicant main form in the maker/app designer after import and confirm "Ethnic Group"
  renders as a picklist between Gender and Date of Birth, with the six ground-truthed categories
  plus "Prefer not to say".
- Confirm a value can be set and saved on a test applicant record, and that the value is visible
  only to a user holding (or exempt from) `REV_TrusteeRestricted`, matching Gender's existing
  behaviour.
- Confirm the trustee-portal ethnic-group distribution chart (FR-061) now reflects a non-empty
  distribution once at least one applicant carries a value — historical applications predating
  the column will correctly show no value (`Entity.xml:349`'s own "does not backfill" note).

## 10. Unvalidated Assumptions Register (C-TECH-052)

| ID | Claim | Where in source | Evidence | Why not verified | Cheapest verification | Status |
|---|---|---|---|---|---|---|
| A-AEG-1 | The `{3EF39988-22BB-4f0b-BBBE-64B5A3748AEE}` classid is the correct control for a global picklist option set on this form, matching Gender/Age Range/Applicant Type's own already-shipped controls exactly. | [FormXml/main/{5cb234cc...}.xml:9](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_applicant/FormXml/main/%7B5cb234cc-f4af-4e97-a024-c71b7da66399%7D.xml#L9) | E1 — copied verbatim from three sibling controls already live on this exact form, not inferred from documentation | N/A — this is ground truth from the same file, not a guess | N/A | **CLOSED by construction** — identical classid/shape to three already-working controls on the same form |

No `OPEN` rows. This dispatch introduced no new platform contract — it copied an existing,
already-working pattern from the same file rather than inferring one, per
`skills/how-to-verify-a-platform-contract.md` §1.

## 11. Verification Evidence (C-TECH-053, C-TECH-055, C-TECH-056)

### Verification level reached

| Component | Level reached | Environment / OS | Evidence (command + observed result) |
|---|---|---|---|
| FormXml well-formedness | **V1** | macOS, this Mac | `python3 -c "import xml.etree.ElementTree as ET; ET.parse(path)"` — parses cleanly |
| Form/option-set/entity cross-reference | **V1** | macOS, this Mac | `python3 scripts/verify-forms-and-views-reachable.py src/solutions/RevitaliseGrantAutomation` — `forms-and-views-reachable: OK` (26 checks, pre-existing warnings unrelated to this table); `python3 scripts/verify-tad-coverage.py` — `OK`, 174 §3.1 columns matched |
| Solution component manifest | **V1** | macOS, this Mac | `Invoke-Pester src/tests/provisioning/VerifySolutionComponents.Tests.ps1,src/tests/provisioning/EnsureSchema.Tests.ps1 -CI` — 50/50 passed |
| Solution pack/import (V2/V3) | **NOT PERFORMED this dispatch** | — | No `pac solution pack`/import was run in this session |
| Human open-and-save in the form designer (V4) | **NOT YET PERFORMED** | — | Requires a signed-in maker session against a real environment; not available to this dispatch |
| Live rendering / data entry for a real trustee (V5) | **NOT YET PERFORMED** | — | Depends on V3/V4 above |

**This is reported at V1 only.** The change is a small, pattern-copied FormXml edit with no new
platform contract, but per `C-TECH-053` the level claimed is the level executed, not the level
expected: V2 (pack) through V5 (live use) genuinely were not run in this session and are not
claimed as done.

### Tool warnings triaged (C-TECH-055)

| Warning | Source step | Resolved / Accepted | Rationale if accepted |
|---|---|---|---|
| `npm warn deprecated glob@10.5.0` | `code-app-install` (build `-20260905-4`) | Accepted, pre-existing | Same warning, same dev/test-only transitive dependency chain, already accepted with recorded rationale — see [parent Dev Summary, "Tool warnings" note](revitalise-grant-automation-dev-summary.md#L4893), item 2. Not introduced by this dispatch. |
| `pac solution pack`'s 14-line "not defined in customizations" notice | `pack-managed` (build `-20260905-4`) | Accepted, pre-existing | Same warning shape, already accepted with recorded rationale — see [trustee-portal-visual-refresh Dev Summary, "Tool warnings" table](trustee-portal-visual-refresh-dev-summary.md#L2631). Not introduced by this dispatch. |

### Diagnostic components created and removed (C-TECH-056)

| Component | Environment | Purpose | Removed (date / how) |
|---|---|---|---|
| None | — | — | — |

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| [IMP-0597](../../logs/improvement-log.jsonl) | `no-assertion-on-shipped-content` | blocker | When a column is added specifically to be captured by a form, add its control to that form's FormXml in the same change — nothing currently checks schema and form-surface move together. |
| [IMP-0598](../../logs/improvement-log.jsonl) | `declared-policy-not-mechanically-enforced` | blocker | A "single source of truth" register is only as complete as its own maintenance discipline unless a gate checks it against source independently — `rev_ethnicgroup` self-declares Article 9 status in its own `Entity.xml` comment and is absent from `special-category-register.yml`, and the existing gate cannot see the gap. |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py` (595 entries, 592
distinct lessons, 629 lines)

---

## Code Review Checklist

- [x] All FR IDs covered — FR-061's data-entry path fixed; no FR scope change
- [x] No hardcoded secrets
- [x] Security controls from TAD §6 implemented — n/a, none changed; `IsSecured=1` / `REV_TrusteeRestricted` preserved unchanged
- [x] Every TAD §12 item has an idempotent provisioning script wired into `config/<slug>-pipeline.yml` — n/a, no provisioning change
- [x] Role assignments via group teams only — n/a, no role change
- [x] No hardcoded environment-specific IDs/URLs (C-TECH-047) — none introduced
- [x] Every guessed platform contract is in §10 **and** commented `A-nnn` in source (C-TECH-052) — no OPEN rows; A-AEG-1 closed by construction
- [x] Where an environment existed, ground truth was used instead of a guess — pattern copied verbatim from three sibling controls already live on this form
- [x] Every platform limit the packer/compiler does not enforce has a build gate — n/a, no new platform limit introduced
- [x] Verification levels in §11 are the levels actually executed, not the levels expected (C-TECH-053) — capped at V1; V2–V5 explicitly named as not performed
- [x] Scripts run on the CI runner's OS — n/a, no new scripts
- [x] Every tool warning triaged in §11 (C-TECH-055); no diagnostic components left in the solution (C-TECH-056) — none emitted
- [ ] Accessibility requirements met — n/a, Model-Driven App standard control, no custom UI
- [x] No dead code or debug statements
- [ ] Unit tests written — n/a, no test harness exists for FormXml control presence (this dispatch's own finding, IMP-0597, proposes one)

## Hours Proposal (development-agent.md → "Propose actual hours while you still know them")

Proposed against **[WBS 0.4](../../contract/wbs.json#L224)** — defect fix against this task's own
deliverable (the Applicant table + its form), not new scope. Not billed against `wbs:6.x`
(trustee portal) even though the symptom surfaced there — the fix is entirely inside the
Applicant form the schema task already owns.

- **Evidence**: option-set/Entity.xml/tad-deferral cross-check, one FormXml edit, two gate re-runs
  (`verify-forms-and-views-reachable.py`, `verify-tad-coverage.py`), one Pester run (50 tests) —
  this session's tool-call record.
- **Proposed actual**: **0.5 h**, `system` flag: **no** (client-facing defect fix, not tooling on
  `agents/`/`skills`/`scripts/`).

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED`
