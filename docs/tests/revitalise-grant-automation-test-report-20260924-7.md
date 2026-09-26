# Test Report — Revitalise Grant Automation

**Feature Slug:** revitalise-grant-automation
**Artifact:** `build/artifacts/revitalise-grant-automation-20260924-7/`
**Date:** 2026-09-24
**Status:** PASS
**WBS:** 0.4, 4.7 (primary this cycle) — also touches 6.8, 2.7, 4.5, 4.2, 6.9 per the ongoing cycle

---

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit (Pester) | Yes | 1141 | 0 | 1 |
| Integration | Yes | (within Pester total above) | 0 | 0 |
| End-to-End | Not run | — | — | — (deferred-to-pipeline, see §7.2) |
| Regression | Yes | 1141 | 0 | 1 |
| Security | Spot-checked (gitleaks, field security) | Pass | 0 | — |
| Accessibility | N/A this dispatch (no new/changed screen; the change is Dataverse FormXml, not the React app) | — | — | — |
| Performance | N/A — no NFR touched by this dispatch | — | — | — |
| Provisioning | Not applicable to this dispatch's change (no new site/team/app-reg) | — | — | — |
| **Platform Contract (§7.1)** | Yes — **the fix that failed build -6 is now independently confirmed** | — | 0 | — |
| **Total** | | 1141 | **0** | 1 |

**Bottom line: PASS.** `revitalise-grant-automation-test-report-20260924-6.md` failed this
artifact's predecessor (build -6) because `ARTIFACT-QVF-1` found the packed
`customizations.xml` still shipping `<forms type="quickview">` for all three `rev_applicant`
Quick View Forms, despite the source file's own attribute already reading `quick`. This build
renames the containing folder (`FormXml/quickview/` → `FormXml/quick/`) and adds a new HARD
gate, `component-shape-packed`, that compares the packed wrapper against source per formid.
Re-verified independently against the actual packed zip, not the gate's self-report alone —
see §7.1. All three forms now pack correctly; no other regression found.

---

## 2. Requirement Coverage

| FR ID | Requirement | Test Case(s) | Result |
|---|---|---|---|
| A-LOC-1 / A-ATYPE-1 / A-AGE-1 (wbs:4.5) | Quick View Forms embedding location area, applicant type, age range on `rev_applicant` pack with the correct `<forms type>` wrapper | `IntakeContract.Tests.ps1:723` "Quick View Forms on rev_applicant"; independent unzip-and-match against `build/artifacts/revitalise-grant-automation-20260924-7/RevitaliseGrantAutomation.zip` (this report, §7.1) | **PASS** — source, unit test, and packed artifact all agree |
| wbs:4.7 | `component-shape-packed` build gate: packed `<forms type>` wrapper matches source-declared type, per formid | `BuildGates.Tests.ps1` `Describe 'Build gate: component-shape-packed'` (5 assertions); re-run independently against fixtures this cycle (§7.1) | **PASS** |
| wbs:6.9, 0.4 | `REVPortalRoundStatistics` action split; `REVSafeguardingActionCompletion` loop guard | Carried unchanged from `revitalise-grant-automation-test-report-20260924-6.md` §2 — no source change to either this cycle | Carried PASS |
| wbs:2.7, 6.8, 4.2 | Not the subject of any revision block added since build -6's report | (unchanged) | Carried — not re-tested this cycle; this build's only source change is the folder rename + new gate |

---

## 3. Failed Tests

None this cycle. `ARTIFACT-QVF-1` (build -6's failing test) now passes — see §7.1.

---

## 4. Defects Raised

None this cycle. `IMP-0874` (the defect `ARTIFACT-QVF-1` raised against build -6) is `status:
APPLIED`, corrected by `IMP-0875` — both confirmed against this artifact, not merely read from
the log (§7.1).

---

## 5. Constraint & Compliance Verification

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| C-TECH-052 | Every hand-authored solution component has a register row / ground-truthed shape | **PASS** | `A-QVF-1` is `CLOSED — CONFIRMED AT V2` (dev summary L10704) on real evidence — a live `pac solution pack` whose packed wrapper matches source for all three formids — re-run and re-confirmed independently by this report against `build/artifacts/revitalise-grant-automation-20260924-7/`, not the dev summary's own claim (§7.1) |
| C-TECH-053 | Verification level claimed matches level confirmed | **PASS** | Dev summary §11 (L10786) claims V2 only for this fix and states V3/V4 as not yet performed, honestly. This report confirms V2 (§7.2) and defers V3/V4 to pipeline-agent's next dispatch per `skills/how-to-apply-constraints.md` "could the evidence exist yet?" — no live import of this rebuilt artifact has been attempted, so V3 is not yet due, not missing |
| C-TECH-057 | Every build gate is proven able to fail (known-bad fixture + negative test) | **PASS** | `component-shape-packed` re-run by this report against its own fixtures (`src/tests/fixtures/known-bad/component-shape-packed/`): `mismatched-packed.zip` and `dropped-form-packed.zip` both FAIL with exit 1 and the expected error text; `matching-packed.zip` PASSes with exit 0 — the gate genuinely discriminates, not a `gate-cannot-fail` instance |
| C-TECH-054 | Every pipeline/CI script runs on the CI runner OS | PASS | No new OS-specific script this dispatch; unchanged from build -6 |
| C-TECH-055 | Tool warnings triaged | WARN (pre-existing, not this dispatch's own change) | `IMP-0877` (friction, logged by build-agent this same build) — Dev Summary §11 L4893 still cites the code-app bundle at "558 kB (151 kB gzipped)"; the current measured figure is 1,207.50 kB / 471.91 kB gzipped (`bundle-budget.json`, `measured_on: 2026-09-01`). The MECHANICAL half (magnitude vs. budget) is green; the prose citation is stale. Not raised by this dispatch's own change (the folder rename touches no code-app file) but carried as an open item — see §8 |
| C-DOM-030 | No special-category/safeguarding column influences automated scoring | PASS | `domain-invariants` build step green per this build's manifest; unaffected by a FormXml-folder-name-only change |
| C-COM-002 | Work enters by accepted WBS task id | PASS | This dispatch's revision block carries `wbs:4.5`; the new gate is filed under 4.7 (test-results deliverable, per `contract/wbs.json`) |

All other HARD/SOFT rows in `constraints/technology/technology-constraints.md` and
`constraints/domain/domain-constraints.md` scoped to `test-agent` are unaffected by this
dispatch's change (a folder rename + one new build gate) and are carried PASS from
`revitalise-grant-automation-test-report-20260924-6.md` §5, which this report does not repeat.

---

## 6. Provisioning Verification

Not applicable — this dispatch touches no site, team, app registration, group team, role
binding, or app sharing (TAD §12 / §6.1 unaffected).

---

## 7. Platform Contract & Verification-Level Audit (C-TECH-052, C-TECH-053)

### 7.1 Assumption register closure

| Assumption ID | Claim | Status per Dev Summary | Closing precondition | Does it exist yet? | Verified by test-agent | Result |
|---|---|---|---|---|---|---|
| A-QVF-1 | `<forms type="quick">` (source) is correct **and** the packed `customizations.xml` wrapper for the same three formids also reads `quick` | **CLOSED — CONFIRMED AT V2, V3 PENDING REBUILD + RE-IMPORT** (dev summary L10704) | Direct inspection of the packed artifact this build produced, per formid | **Yes — the artifact under test exists right now** | **Independently reproduced, not trusted from the manifest or the dev summary.** Unzipped `build/artifacts/revitalise-grant-automation-20260924-7/RevitaliseGrantAutomation.zip`, parsed `customizations.xml` with `ElementTree`, matched each of the three formids (`7f145e5b…`, `8df85b1f…`, `eed29b6a…`) from the source `FormXml/quick/` files to its enclosing `<forms>` element: **all three read `type="quick"`**. Extended the check to all 15 hand-authored FormXml forms in the solution (not only the 3 previously affected): 0 mismatches, 0 forms missing from the packed zip. Also grepped the packed `customizations.xml` for the literal string `quickview`: 3 occurrences remain, all three are `<control id="quickview_…" classid="{5C5600E0-1D6E-4205-A272-BE80DA87FD42}">` — the `quickviewcontrol` embeds on the Application main form, which address forms by GUID and are unrelated to the `<forms type>` wrapper (confirmed already in `IMP-0867`; re-confirmed here by inspecting the actual matched text, not by re-reading that finding). Then ran the gate script itself, `scripts/verify-packed-form-types.py`, directly against this artifact's zip: `OK — 15 form(s)' packed <forms type> wrapper … match their own source-declared type` — matches the manual check exactly. | **PASS** |

**Root cause (unchanged from `IMP-0874`, retained for the record):** `pac solution pack`'s
SolutionPackager derives the packed `<forms type>` wrapper attribute from the
`FormXml/<foldername>/` path segment, not from the split source file's own root `type`
attribute. `IMP-0867` corrected only the file content and closed `A-QVF-1` `WRONG`; `IMP-0874`
(this report's predecessor, `revitalise-grant-automation-test-report-20260924-6.md`) caught the
folder was still named `quickview` and the packed artifact still failed. This build's fix
(`IMP-0875`) renames the folder to `FormXml/quick/`; the fix is what this report re-verifies
independently against a fresh packed artifact rather than trusting the build gate's own report.

**Why the fix is trustworthy and not another instance of the same gap.** The new gate,
`component-shape-packed`, is a genuine comparison — proven in §5/C-TECH-057 above to fail on a
mismatched or dropped form and pass only on a matching pair — and its own report on this
artifact (`OK — 15 form(s)…`) matches the independent manual unzip-and-match performed for
this report byte-for-byte. Two independent instruments agreeing is stronger evidence than either
alone; this is the check build -6's report was missing (it trusted the source-only
`formxml-type-values` gate, which structurally could not see this defect).

### 7.2 Verification levels achieved

| Component | Level claimed (Dev Summary §11) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| Quick View Forms (A-LOC-1/A-ATYPE-1/A-AGE-1) packed wrapper | V2 (packaged, packed-artifact content confirmed correct); V3/V4 explicitly stated as not yet performed | **V2 confirmed** — packs with exit 0 and the packed content is now provably correct, independently re-verified | Direct unzip + gate re-run above (§7.1) | **PASS at claimed level** |
| Same forms, live DEV import | Not claimed this cycle | Not attempted — `logs/pipeline.log`'s last entry for this feature is the 2026-09-24 11:47 FAILURE against build -4 (the original `quickview` rejection); no import of build -6 or build -7 has been attempted | `logs/pipeline.log` | **deferred-to-pipeline** — the evidence that would confirm V3 does not exist yet because the step that produces it (pipeline-agent's DEV import) has not run against this artifact; not a violation per `skills/how-to-apply-constraints.md`'s "could the evidence exist yet?" test |
| Solution Checker (managed zip) | Live network check, partial V3 signal | Confirmed — `solution-checker/pac-solution-check-stdout.log`: `Critical 0, High 0, Medium 1, Low 0, Informational 0` | Read directly from this artifact's own log file | PASS (no criticals/highs; the one Medium is pre-existing, unrelated to this fix) |
| wbs:6.9 / wbs:0.4 items | V2 (build-level), no source change this cycle | Carried from build -6's report — unaffected | `revitalise-grant-automation-test-report-20260924-6.md` §7.2 | Carried PASS |

- Idempotency: not reached — no live import of this artifact has occurred yet → `N/A — deferred-to-pipeline`
- V4 designer/editor open + save: **NOT PERFORMED** — cannot be performed until V3 (a successful import) is reached, and V3 has not been attempted against this artifact → `N/A — deferred-to-pipeline, not a violation` (unlike build -6, where V3 would have failed identically to `IMP-0866` even if attempted; that specific defect is now fixed)
- Cross-OS (C-TECH-054): PASS — no new OS-specific script this dispatch
- Warnings triaged (C-TECH-055) / diagnostic components removed (C-TECH-056): WARN on the pre-existing stale bundle-size citation (`IMP-0877`, not this dispatch's own change); no diagnostic component added this dispatch

---

## 8. Recommendations

1. **Proceed to Pipeline.** The defect that blocked build -6 (`IMP-0874`) is fixed and
   independently re-verified against this artifact's own packed zip, not inferred from the
   build gate's self-report.
2. pipeline-agent should attempt the DEV import next — this is the first opportunity to
   observe V3 for this fix. Expect the "Forms being imported are of an unsupported type
   'quickview'" error to **not** recur; if it does, that would itself be a new, distinct
   finding (the fix would have regressed between this build and the live attempt) and should
   be filed as such rather than assumed to be `IMP-0866` recurring unchanged.
3. After a successful V3 import, the reviewer's V4 open-and-save on the affected Quick View
   Forms is still owed — carry this forward until performed and named with an owner and date,
   per C-TECH-053.
4. `IMP-0877` (stale bundle-size prose in §11) is unresolved — not blocking this gate (it is a
   documentation drift, not a build-gate or import-blocking defect) but should be swept up
   before this Dev Summary is cited as evidence elsewhere.
5. `constraints/technology/component-shapes.yml`'s `entity form` shape block still carries the
   disproven "folder name is inert" claim (dev summary L10637–10649 proposes exact replacement
   text) — this is improvement-agent's file; route via `APPROVE IMPROVEMENTS`.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

None this cycle. No second attempt on unchanged input, no document/reality contradiction found
beyond what `IMP-0877` already records (logged by build-agent, not duplicated here), no
`BLOCKED`/`FAILED`/`REVISION` status, no human correction, and the one Dev Summary §11
verification-level claim checked (V2 for the Quick View Forms fix) was confirmed at exactly the
level claimed.

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| none | — | — | — |

Digest regenerated: NO — no new entry appended this cycle.
