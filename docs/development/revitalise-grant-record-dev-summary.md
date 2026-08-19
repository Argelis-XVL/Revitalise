# Dev Summary — Grant Record and Signed-Acceptance Store

**Feature Slug:** `revitalise-grant-record`
**Date:** 2026-08-18
**Status:** DRAFT — awaiting code review
**Approved SDD:** `docs/plans/revitalise-grant-record-plan.md`
**Approved TAD:** `docs/architecture/revitalise-grant-record-architecture.md`
**Tier:** `standard` — no `escalate_to_strategic_when` rule met (established pattern exists;
zero ADRs marked `Proposed`; the security work configures a platform control, not a custom one)
**WBS:** `0.4` (remainder). Unblocks `3.2`, `3.4`, `3.7`, `6.6`, `7.2`, `8.4`.

---

## 1. Implementation Summary

One Dataverse table, its option set, its parental relationship, one form, three views, twelve
column-security permissions, ten role privileges and one environment variable. No flows, no
connectors, no app changes — as TAD §5 specifies.

**Highest verification level executed: V2 (packaged), asserted on content.** Both packages were
built and their `customizations.xml` inspected directly for each component, because a successful
pack proves the packer accepted a layout and nothing more — a DEV deployment once shipped with 0
forms and 0 views from a green build (`IMP-0006`). **V3 has not been executed. Nothing has been
deployed.**

### 1.1 Ground truth was obtained before authoring, and it changed the design twice

`pac` was authenticated to `REV-GrantApplications-DEV`, so per
`skills/how-to-verify-a-platform-contract.md` §1 the solution was **exported and unpacked
read-only** before a line was authored. Two things came out of that comparison that
documentation would not have given:

1. **The platform emits a 1049-line `Entity.xml` where this repo commits 175.** That proves the
   minimal hand-authored shape is *sufficient* — DEV accepted it and now returns the fuller form
   — so `rev_grant` was authored minimal rather than padded to match an export. It also means the
   repo source is a **subset** of what DEV contains: the platform adds `FormXml/card/`,
   `FormXml/quick/`, `RibbonDiff.xml` and **ten** SavedQueries on `rev_errorlog` where source has
   one. Those are platform-owned; only authored views belong in source.
2. **`rev_grant` had to be `UserOwned`, not `OrganizationOwned`.** Copying the nearest neighbour
   (`rev_errorlog`, `OrganizationOwned`) would have been wrong: the parental relationship declares
   `CascadeAssign=Cascade`, and a parent can only cascade an assignment to a child that has an
   owner. `rev_applicant` and `rev_application` are both `UserOwned`. This was read off the
   existing pair, not reasoned about in the abstract.

Every element set — money, date-only, picklist, bit, lookup, autonumber, option set, field
permission, form control classid — was copied from an attribute or control **live in that
environment**. Control classids were harvested mechanically by mapping every
`datafieldname`→`classid` pair in the committed forms against each attribute's declared type, so
none was chosen by resemblance. `IMP-0014` shipped three dropdowns with no options from one
guessed classid.

---

## 2. Components Created

| Component | Path | Notes |
|---|---|---|
| Entity `rev_grant` | `Entities/rev_grant/Entity.xml` | 15 attributes, 12 secured, `UserOwned`, autonumber `GR-{yyyy}-{SEQNUM:5}` |
| Global option set | `OptionSets/rev_grantstatus.xml` | 4 values: Awarded / Acceptance Issued / Acceptance Signed / Paid |
| Parental relationship | `Other/Relationships/rev_application.xml` + stub in `Other/Relationships.xml` | Cascade on delete/assign/reparent/share |
| Main form | `Entities/rev_grant/FormXml/main/{d1000000-…-ad01}.xml` | 3 sections following the record lifecycle; 15 controls |
| Views | `Entities/rev_grant/SavedQueries/` × 3 | All Grants (default), Awaiting Acceptance, Acceptance Signed |
| Column security | `Other/FieldSecurityProfiles.xml` | 12 permissions added to `REV_TrusteeRestricted` (39 → 51) |
| Role privileges | `Roles/REV Admin`, `Roles/REV Service Automation` | 5 each; **no Delete on either** |
| Environment variable | `environmentvariabledefinitions/rev_SpoSignedAcceptanceUrl/` | Definition only; value is per-environment |
| Root components | `Other/Solution.xml` | entity (type 1), option set (9), relationship (10), env var (380) |

### 2.1 Deliberate deviation: no per-slice build or pipeline config

`agents/development-agent.md` says to produce `config/<slug>-build.yml` and
`config/<slug>-pipeline.yml`. **Neither was created, deliberately.** This slice adds components to
the *same solution* that `config/revitalise-grant-automation-build.yml` already builds. A second
config packing the same folder would be two sources of truth for one artefact, and the class
`two-invocation-paths-disagree` (`IMP-0026`) is already in this project's digest. The existing
configs were **extended** instead:

- `revitalise-grant-automation-build.yml` — new `guid-syntax` gate (§4).
- `revitalise-grant-automation-pipeline.yml` — a **new `dev:` environment block** carrying the
  eight TAD §12.1 prerequisites and four verification steps. That block did not exist: DEV was
  imported by GitHub Actions with **no declared prerequisites at all**, which is how the first
  deployment into it cost fifteen attempts.

**pipeline-agent must confirm it consumes a `dev` entry.** If its Stage 0.5 iterates
`environments` by name and knows only `tst_acc`/`prd`, all eight steps are skipped silently —
which is the exact failure this block exists to prevent. Say so in the gate output rather than
assuming; the config now says this too.

---

## 3. Data Model Changes

Fifteen columns as TAD §3 specifies, minus `rev_providerid` (OQ-G03, closed by the reviewer as
"leave out"). Recorded as a **deliberate deferral to WBS 8.1**, not an omission: adding a lookup
later is an ordinary additive import, unlike the *type* change that cost three imports in
`IMP-0017`.

`rev_conditions` holds the **terms of the award**, not a health condition. The name collision was
flagged in the SDD and the column's own `<Description>` says so, because a future author reading
only the schema would reasonably assume otherwise.

**One grant per application is not enforced by the relationship.** Dataverse has no native 1:1.
ADR-G02 enforces it with an alternate key on `rev_applicationid` — which is assumption **A-G01**,
still `OPEN` (§10).

---

## 4. Gates Added

**`guid-syntax`** — `scripts/verify-guid-syntax.py`, with a known-bad fixture and three tests.

It exists because of a defect in this pass. The form's cell, tab, section and form ids were
authored as `{a1000000-0000-4000-8000-00000000ga01}` and fifteen siblings — **`g` is not a hex
digit** — and the formid also named the file. **`pac solution pack` accepted the folder and exited
0.** Nothing in the build noticed: the file is well-formed XML so `source-validate` passes, and
those ids are not RootComponents so `verify-solution-root-components` never reads them.

That is the same shape as every expensive defect in this project's digest — a plausible-looking
hand-authored value the packer does not validate, which fails later in an environment with an
error naming nothing useful. The gate checks every 36-character `{…}` token in every solution
`.xml` **and in every file name**, since SolutionPackager names form and view files after their
ids. 248 GUIDs across 60 files now pass. `IMP-0036`.

---

## 5. What the Existing Gates Caught In This Pass

Recorded because it is the whole point of the suite, and because a summary that only lists what
was built hides how much was nearly shipped:

| Gate / test | What it caught |
|---|---|
| `verify-solution-root-components` | The new relationship was **not declared** as a `RootComponent type="10"`, while the existing one is. It would have packed the file and deployed nothing |
| `no-hardcoded-environment-values` | A literal `https://…sharepoint.com/sites/…` URL in a **comment** inside the shipped environment-variable definition — a real `C-TECH-047` breach. Removed; the URL lives in the TAD and deployment settings, neither of which ships |
| `ConvertFrom-RevOptionSetXml` (provisioning tests) | The option set carried `<Descriptions>` **inside each option** and no optionset-level `<displaynames>`, because the shape was copied from `head -12` of a 70-line file. The two elements that matter are at the bottom. `pac solution pack` accepted the wrong shape and exited 0 (`IMP-0037`) |
| `EnsureSchema.Tests.ps1` | Two **hardcoded single-instance assumptions** in `ensure-schema-helpers.psm1`: the relationship detail path was pinned to `rev_applicant.xml`, and `Get-RevEntityLogicalNames` was a hand-kept four-name list. The second meant `ensure-schema.ps1` would **never have created `rev_grant`**, making TAD §12.1 item 1 unimplementable (`IMP-0038`) |

Three of those five would have reached an environment. Two are defects in code this slice did not
write, surfaced only because a second instance finally existed.

---

## 6. Security Controls Implemented

Twelve columns `IsSecured=1`, all released in `REV_TrusteeRestricted`. `rev_name`,
`rev_applicationid` and `rev_status` are unsecured: the reference is pseudonymous, and the other
two are needed for a view to render.

**The reviewer's OQ-G06 answer was implemented as ADR-G03 interpreted it, and that interpretation
is load-bearing.** "Don't give access now so that later on we can give access" is honoured for the
personas it concerned — **trustees and finance get nothing** — while the process owner and service
identity keep the access they already hold on `rev_applicant`. Taken literally as *release to
nobody*, the build fails: with no System Administrator among the application personas (ADR-019),
an unreleased secured column is readable by nobody at all, and FR-041 needs the service identity
to read the grant amount. Approving the architecture adopted this reading; it is restated here
because it is the one place a reasonable person could still disagree.

**`REV_FinanceOnly` is not created** — it covers `rev_bankaccount` and `rev_payment`, neither of
which exists. **No Delete privilege** is granted on `rev_grant` to either role (`C-DOM-021`).

---

## 7. Known Limitations / Deferred Items

| Item | Status |
|---|---|
| **Nothing has been deployed.** V2 is the ceiling reached | The whole of §12.1 is unexecuted, including the alternate key that closes A-G01 |
| **`A-G01` is `OPEN`** — alternate key on a lookup column | `C-TECH-058` blocks the DEV deploy until it closes or the reviewer overrides with `OVERRIDE A-G01` |
| Deleting a Grant deletes the record but **not its signed PDF** | The purge needs the deferred Retention & Erasure helper flow (TAD §4.1) |
| The retention job keyed on `rev_finalpaymentdate` is not built | The column ships; the enforcement does not |
| `rev_docusignenvelopeid` ships **empty and unexercised** | ADR-G04. Unexercised is a different claim from working |
| `rev_providerid` absent | WBS `8.1`, and #8 still has no FR behind it |
| V5 is **not reachable** | No automation writes to this table yet. It must not be claimed |
| `A-G02` — `Format=url` and its control | Cosmetic only; fallback is `Format=text`. §10 |

---

## 8. Build Instructions

```bash
python3 scripts/verify-build-config.py config/revitalise-grant-automation-build.yml
pwsh -File src/tests/Invoke-Tests.ps1
pac solution pack --zipfile <artifact>/managed.zip \
  --folder src/solutions/RevitaliseGrantAutomation --packagetype Managed
```

Artifact directory comes from `scripts/resolve-artifact-dir.py` — never a literal path
(`IMP-0016`, `C-TECH-059`).

---

## 9. Test Guidance

`test-agent` cannot reach V5 on this slice. What is testable:

- **Structural** — the invariant suites, all updated for the new counts (§11).
- **V3, after deploy** — every declared component type queried by name from a source-derived list;
  the live option-set members compared against the four in source (`IMP-0019`).
- **V4** — a named human opens and saves a `rev_grant` record and opens all three views, checking
  labels against each attribute's authored wording (`IMP-0015`).
- **Not testable** — anything about acceptance behaviour. There is none.

---

## 10. Unvalidated Assumptions Register (C-TECH-052)

| ID | Assumption | Severity | Status | How it closes |
|---|---|---|---|---|
| ~~**A-G01**~~ | An alternate key can be created on a **lookup** column (`rev_applicationid`), enforcing one grant per application (ADR-G02) | **E2** | ✅ **CLOSED CORRECT 2026-08-18, live in DEV** — key created on `rev_applicationid`. **Caveat: `EntityKeyIndexStatus=Pending`, and while Pending it does NOT enforce uniqueness** (IMP-0044). Closing it also exposed a step-order defect: keys ran before relationships, so the first attempt failed with `0x80040203` (IMP-0043) | Create it via the Web API in DEV and observe. String alternate keys are proven here (`rev_sourcesubmissionid`); lookup keys are not. **Fallback:** duplicate-detection rule + a guard in the future finalise flow — weaker, and must be recorded as such |
| ~~**A-G02**~~ | `<Format>url</Format>` is a valid SolutionPackager format value | E4 | ✅ **CLOSED WRONG 2026-08-18** — the live column the Web API created reports `Format=text`, and a DEV export writes `text`. Source now says `text`, taken from the environment. The fallback was the answer | **The guessed part has been removed.** The form now uses the PLAIN single-line-text control (proven on 32 committed columns) instead of the formatted control used by `rev_email`/`rev_phone`, which was a guess about link rendering — and a guessed control classid is precisely what shipped three empty dropdowns (`IMP-0014`). What remains is a schema enum the import either accepts or rejects loudly, not a silent UI failure. **Fallback:** `Format=text`, cosmetic only |
| **A-G03** | The library ACL, with inheritance broken, denies the trustee group in practice | E2 | ⛔ **OPEN AND NOT CLOSEABLE TODAY** | The library does not exist and cannot be created by any script in this repo: `provisioning/sharepoint/templates/` holds only a README, there is no dev SharePoint settings block, and the provisioning app's permission on the site is unverified (`IMP-0046`). Nothing writes `rev_signedpdfurl` until WBS 3.2/3.4, so this blocks the acceptance flows, not this slice |
| ~~A-G04~~ | `pipeline-agent` consumes a `dev` entry under `environments` | E3 | ✅ **CLOSED 2026-08-18** | Closed by inspection, not assumption: `agents/pipeline-agent.md` → *Stage 0.5* reads *"the target environment's block declares `environment_prerequisites`"* and *"Executing an Environment Block (applies to every stage)"* — it iterates the block it is given rather than a fixed list of environment names, so a `dev` block is consumed like any other |

**Status after the 2026-08-18 narrowing: A-G01 and A-G03 OPEN (both closeable in DEV by Stage 0.5), A-G02 narrowed to a schema enum, A-G04 closed by inspection.** Two of these are E2 and `C-TECH-058` makes A-G01 blocking. `IMP-0014` is why: A-001 was recorded
correctly, marked OPEN, shipped anyway, and reached the reviewer as three empty dropdowns.

---

## 11. Verification Evidence (C-TECH-053)

Executed in this session, with the command's own output as the evidence:

| Check | Result |
|---|---|
| `verify-build-config.py` (preflight) | **PASS** — 20 steps, 15 gates, all with negative-test coverage |
| `verify-source-parses.py` | **exit 0** — 60 XML files well-formed, 4 flow definitions parse (V1) |
| `verify-solution-root-components.py` | **exit 0** — 41 root components, every one has a definition on disk and nothing on disk is undeclared |
| `verify-forms-and-views-reachable.py` | **exit 0** — 10 entity/element checks across 5 entities |
| `verify-guid-syntax.py` | **exit 0** — 248 GUIDs across 60 files all parse |
| `verify-field-security-coverage.py` | **exit 0** — 51 secured columns, every one released, no permission for an unsecured column |
| `verify-field-length-limits.py` | **exit 0** — 129 flow descriptions, 126 settings values, 62 declared limits read |
| `no-hardcoded-environment-values` | **exit 0** after the URL was removed |
| `pac solution pack --packagetype Managed` | **exit 0** |
| `pac solution pack --packagetype Unmanaged` | **exit 0** |
| **Content assertion inside both zips** | entity, option set, main form, all three views, the parental relationship, **12** `rev_grant` field permissions and the role privileges all **PRESENT** |
| Environment-variable packaging | Ships as `environmentvariabledefinitions/rev_SpoSignedAcceptanceUrl/…xml` and is declared in `solution.xml` — **exactly as the platform's own export packages the other three**, which appear in `customizations.xml` only inside a comment |
| `src/tests/Invoke-Tests.ps1` | **695 passed, 0 failed, 1 skipped** — through the path CI uses (`IMP-0026`), not `Invoke-Pester` alone |

**Level reached: V2 packaged, with content asserted.** V3, V4 and V5 are not claimed. Exit codes
were re-measured without a pipeline after an early check reported `exit=0` through `| tail -1` —
the same masking that made a HARD compliance gate pass for weeks (`IMP-0007`).

### Tool warnings triaged (C-TECH-055)

`pac solution pack` reports *"Following root components are not defined in customizations"* for
6 components: 2 EntityRelationships and 4 EnvironmentVariableDefinitions. **Accepted, with
evidence:** 4 of the 6 predate this change and imported into DEV successfully, and the 2 new ones
were confirmed present in the packed `customizations.xml` by direct inspection. The platform's own
export packages both types the same way. 0 warnings left untriaged.

---

## 12. Improvement Log

| ID | Severity | What |
|---|---|---|
| `IMP-0036` | rework | `pac solution pack` accepts a malformed GUID and exits 0 → `guid-syntax` gate written and wired |
| `IMP-0037` | rework | A truncated read of a source of truth is not ground truth — `head -12` of an option set hides the two elements that matter |
| `IMP-0038` | **blocker** | Two hardcoded single-instance assumptions in `ensure-schema-helpers.psm1`; one meant `rev_grant` would never be created |
| `IMP-0039` | friction | Adding one table broke 11 absolute-count assertions. **Second instance** of `test-coupled-to-absolute-counts`, so it is now due for generalisation, not another hand-edit |

---

## Approval

**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED`
