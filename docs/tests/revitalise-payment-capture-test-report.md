# Test Report — Payment Capture Form (Automation #8)

**Feature Slug:** `revitalise-payment-capture` (SDD and Dev Summary) — the build artifact, TAD and
build config carry the parent slug `revitalise-grant-automation`; see §8 note 1
**Artifact:** [`build/artifacts/revitalise-grant-automation-20260910-3/`](../../build/artifacts/revitalise-grant-automation-20260910-3/manifest.json)
**WBS task id:** `8.3` — "Build payment capture form"
**Date:** 2026-09-10
**Status:** **FAIL** — three P2 defects open. No P1. Nothing found that makes the packaged
solution unsafe to import into DEV; the failures are a missing register row, an unenforced
security requirement whose design is self-contradictory, and a task state that derives
`complete` on evidence two levels below what its own approved design permits.

**Verification level reached by this test cycle: V2 (packaged).** Not V3. Stated in full in §7.2.

---

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit (Pester, whole solution) | 1024 | 1023 | 0 | 1 |
| Integration | 0 | 0 | 0 | 0 — deferred-to-pipeline, no import of this build |
| End-to-End (US-030 AC-1…AC-5) | 0 | 0 | 0 | 5 — deferred, see §2 |
| Regression | 1024 | 1023 | 0 | 1 |
| Security | 9 | 7 | 2 | 0 |
| Accessibility | 3 | 3 | 0 | 0 |
| Performance | 0 | 0 | 0 | 0 — no NFR names a measurable threshold for this surface |
| Provisioning | 4 | 4 | 0 | 0 |
| Platform Contract (§7.1) | 2 | 1 | 1 | 0 |
| Verification Level (§7.2) | 6 | 6 | 0 | 0 |
| Constraint Verification (§5) | 34 | 34 | 0 | 0 |
| **Total** | **1082** | **1078** | **3** | **7** |

Unit and regression figures are read from the artifact's own
[`test-results/pester-results.xml`](../../build/artifacts/revitalise-grant-automation-20260910-3/test-results/pester-results.xml)
(`total="1024" errors="0" failures="0" skipped="1"`). They are whole-solution figures: this task
adds **no** unit-test surface, because FormXml, SavedQueries, AppModule.xml and
AppModuleSiteMap.xml are declarative artefacts, which
[coding-standards.md §Test Coverage](../../knowledge/technology/coding-standards.md#L214) classes
as not coverage-measurable and covers by asserted invariants instead. So a green 1024 says nothing
about this feature and is recorded as regression evidence only.

Line coverage measured on the artifact, not quoted from it:
`python3 scripts/verify-coverage-threshold.py build/artifacts/revitalise-grant-automation-20260910-3/test-results/coverage.xml --threshold 80 --exclusions config/coverage-exclusions.json`
exits 0 — **1774 of 2183 lines = 81.26%** against a threshold of 80%, 27 files counted and 4
excluded, each with a reason and a substitute proof. Both numbers are recorded here because the
manifest records neither (defect **D-08**).

---

## 2. Requirement Coverage

| FR ID | Requirement | Test Case(s) | Result |
|---|---|---|---|
| FR-150 | One surface over Provider, Bank Account and Payment for the finance role | TC-01, TC-02, TC-03 | **PARTIAL** — the surface exists in source and is structurally complete; "when the signed-in user holds the finance role" is unverifiable, no such role exists |
| FR-151 | Grant, payee bank account and amount required before a Payment saves | TC-04 | **PASS (V1)** — all three are `ApplicationRequired` in schema *and* present as controls on the form; the model-driven form layer enforces this. Confirmed at V4 only |
| FR-152 | QuickBooks reference optional at creation, editable thereafter | TC-05 | **PASS (V1)** — `rev_qboreference` is `RequiredLevel=None`, `IsSecured=1`, and carries a control on the Payment form |
| FR-153 | Provider contact fields hold organisational contact points only | TC-06 | **PASS, with the control named** — both columns carry a `<Description>` stating the rule; no mechanical enforcement exists and none is claimed (ADR-046) |
| FR-154 | Bank Account nickname must not identify a natural person | TC-07, TC-08 | **FAIL — D-02.** The one shipped control does not address the case FR-154 was written for |
| NFR-150 | No new unsecured column on either table; no rollup or calculated column deriving from a secured column | TC-09, TC-10 | **PASS — both halves measured, not assumed** |

### The five acceptance criteria, and why four cannot be run

| AC | Status | Why |
|---|---|---|
| AC-1 (finance user can CRUD all three) | deferred-to-`wbs:8.2` | No finance role exists |
| AC-2 (save blocked without Grant / account / amount) | deferred-to-pipeline, then V4 | Enforcement is present in source; observing it needs an imported form |
| AC-3 (QuickBooks reference addable later) | deferred-to-pipeline, then V4 | Same |
| AC-4 (non-finance holder of Read on Payment sees empty columns) | **deferred, and not to `wbs:8.2` — D-06** | See below |
| AC-5 (Provider contacts are organisational) | **deferred-to-pipeline only — D-07** | Reachable at the next import without `wbs:8.2`; see below |

**AC-4 does not become testable when `wbs:8.2` lands.** AC-4 needs a principal holding Read on
Payment who is *not* a member of `REV_FinanceOnly`. `wbs:8.2` creates the opposite: TAD §6.2.1
item 5 adds `REV Finance` to the profile's `memberTeams` in the same task that grants it Read.
Measured today, the only principal with Read on `rev_payment` is `REV Service Automation`
([`Roles/REV Service Automation/`](../../src/solutions/RevitaliseGrantAutomation/Roles/REV%20Service%20Automation/REV%20Service%20Automation.xml)),
and it *is* in the profile via `REV Service Accounts`. So no principal is ever in AC-4's state by
design, and AC-4 can only be exercised with a deliberately constructed negative-control identity.
The Dev Summary says AC-4 "cannot be exercised until `wbs:8.2` creates the role", which will leave
whoever runs `wbs:8.5` looking for a test that the role does not enable. This is the same trap as
the trustee access test, where a human satisfied a request for "one identity" with the trustee's
own account and silently converted the negative control into a false positive.

**AC-5 and the Provider form are not blocked by `wbs:8.2` at all.** `rev_provider` has **zero**
secured columns; `REV Admin` holds full Create/Read/Write/Delete/Append/AppendTo on it; and
`REV Admin` is already in the app's `securityRoles`
([`test-settings.json`](../../provisioning/deploymentSettings/test-settings.json)). The moment this
solution imports, an administrator can open the Provider form, save it, and AC-5 becomes
observable. Both the TAD's §6.2.1 level table and the Dev Summary state the V4 block as a blanket
"NO" across the task. One of the three forms is V4-reachable a whole task earlier than either
document says, and per the "could the evidence exist yet?" rule that evidence becomes **due** at
the next deploy rather than deferred to `wbs:8.2`.

---

## 3. Failed Tests

| Test ID | Layer | Description | Expected | Actual | Severity |
|---|---|---|---|---|---|
| TC-07 | Security | The Bank Account nickname control carries the labelled instruction ADR-046's Decision specifies, beside the control | A form-level instruction beside the nickname control, in addition to the column description | Only the column `<Description>`. The form's own header records the omission as authorised by ADR-046 | P2 |
| TC-08 | Security | A finance user entering an applicant reimbursement account has a stated convention to follow | A convention answering OQ-151 | OQ-151 open, past its "before build" due date. The shipped description suggests `'Sunrise Lodge - main'` or `'…4321'` — a provider-account convention. It gives no guidance for the applicant case, which is the only case FR-154 exists for | P2 |
| TC-11 | Platform Contract | Every hand-authored platform contract in the shipped solution resolves to a live register row | Each `A-nnn` marker resolves to a register row about the same subject | The Decimal control classid resolves to `A-FIN-03`, which is a **closed** row about a different subject | P2 |

---

## 4. Defects Raised

| Defect ID | Severity | Description | Owner | Linked Test |
|---|---|---|---|---|
| **D-01** | **P2** | **`C-TECH-052` orphan by identifier collision.** `{C3EBB6DA-CE32-4df0-8534-30B624E393CF}` is hand-authored onto five shipped Decimal columns and its source marker names `A-FIN-03`, which the register resolves to the REV_FinanceOnly profile GUID — closed VERIFIED 2026-08-23. The classid assumption has no live row | development-agent | TC-11 |
| **D-02** | **P2** | **FR-154 ships with no control for the case it was written for**, and the approved design contradicts itself about how many controls there should be | architect-agent (the contradiction), development-agent (the build half) | TC-07, TC-08 |
| **D-03** | **P2** | **WBS 8.3 derives `complete` from five V1-only evidence rules**, which both approved documents forbid even on V3 evidence | pm-agent | TC-12 |
| D-04 | P3 | A-PAY-1's justification contains two false statements | development-agent | TC-11 |
| D-05 | P3 | Dev Summary §6 says 15 entities; the gate and Dev Summary §11 both say 13 | development-agent | TC-13 |
| D-06 | P3 | AC-4's precondition is a state `wbs:8.2` will not create | development-agent | §2 |
| D-07 | P3 | The V4 block is stated as blanket; the Provider form is V4-reachable at the next import | architect-agent, development-agent | §2 |
| D-08 | P3 | The manifest records neither the test count nor the coverage percentage | build-agent | §1 |

### D-01 — the orphan, in full

[`rev_roundfinance`'s form header](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_roundfinance/FormXml/main/%7B94936d70-da48-49e0-8778-ede28317a6f5%7D.xml#L30)
says of its Decimal control classid: *"ONE CLASSID IS NOT GROUND-TRUTHED — marked A-FIN-03, Dev
Summary §10 OPEN."* The register row it names
([dev summary A-FIN-03](../revitalise-grant-automation-dev-summary.md#L5409)) is about
`REV_FinanceOnly`'s real `fieldsecurityprofileid`, and reads **"VERIFIED 2026-08-23 … closed"**.
Two different assumptions, one id, and the surviving one is closed.

The consequence is that a hand-authored platform contract sitting on five shipped columns is
tracked by nothing, which is exactly what `C-TECH-052` exists to prevent.
[`verify-assumption-markers.py`](../../scripts/verify-assumption-markers.py) passes over it because
it checks that an OPEN row's `Where` target contains that row's id — it has no way to notice that
the id in source and the id in the register mean different things.

### D-02 — why FR-154 has no effective control

ADR-046 says two contradictory things in one ADR. Its **Decision** is *"Carry both as column
`<Description>` text surfaced on the form, **plus a labelled instruction beside the Bank Account
nickname control**"*. Its **Consequences** paragraph then says the description *"shows … as help
text at the point of typing. **That is the entire intervention.**"*

The build followed the second sentence and dropped the first, and
[the form's own header](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_bankaccount/FormXml/main/%7Bf2000000-0000-4000-8000-00000000fa01%7D.xml#L29)
records the reduction as though ADR-046 authorised it outright — *"no additional control-level
attribute is added here beyond the field description"*. A reader of the Dev Summary would believe
ADR-046 was implemented as written.

That alone would be P3. What makes it P2 is the third fact: ADR-046 states that for this
requirement **the convention *is* the control**, and OQ-151 — the question that fixes the
convention — is still open, past the "before build" date the SDD gave it. So FR-154's total
shipped control is one column description that suggests conventions for a provider account and
says nothing about an applicant reimbursement account, which is the only case FR-154 was written
for. The requirement is High priority and the exposure it guards is real and permanent: an
applicant's name typed there is readable by every holder of Read on Bank Account or Payment,
projected onto every Payment row through a lookup companion column, and unremovable by column
security.

**This is not yet an exposure.** No principal today holds Read on either table outside
`REV_FinanceOnly`, so nothing leaks. It becomes one the moment `wbs:8.2` grants the finance role
Read, which is the next task.

### D-03 — the task state contradicts its own design

`python3 scripts/derive-wbs-state.py` derives `8.3` as **`complete`**, all five evidence rules
found. All five are source greps and a directory check
([`contract/evidence-map.json`](../../contract/evidence-map.json#L489)) — every one satisfiable by
V1 well-formed source. Both approved documents forbid this: TAD ADR-047 says *"8.3 must not be
reported complete on V3 evidence"*, and SDD §11 says AC-4 *"must not be reported as passed on V3
evidence"*. The derivation reports complete one level **below** the level both warned about.

The rules were rewritten on 2026-09-09 to fix a genuinely unsatisfiable predecessor, and they fix
that. What they do not carry is the human-verification half. This is the shape of evidence rule
this project has already recorded three times — a compound deliverable needs its rule split so the
V4 half is tracked separately and the task derives `partial` until a dated confirmation exists.

Adjacent, and pm-agent's rather than mine: `8.4` also derives `complete`, on a grep for
`rev_payee|rev_bankaccount` inside `rev_payment/Entity.xml` — a file `wbs:8.1` delivered. 8.4 earns
its state from 8.1's schema.

---

## 5. Constraint & Compliance Verification

34 rows in `test-agent` scope: 6 domain HARD, 27 technology HARD, 1 technology SOFT. Every row was
evaluated; none is unevaluable. Commands were run bare and their exit codes captured directly.

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| [C-DOM-004](../../constraints/domain/domain-constraints.md#L37) | No personal data in application logs | PASS | This feature writes no operational log; `domain-invariants` exits 0 |
| [C-DOM-010](../../constraints/domain/domain-constraints.md#L47) | CUD on sensitive entities audit-logged | PASS | All three tables are in `dataverse.auditing.auditedTables` in test and prd settings; live enablement is a post-deploy step and is pipeline-agent's to assert |
| [C-DOM-011](../../constraints/domain/domain-constraints.md#L48) | Audit record fields | PASS | Platform-supplied; unchanged by this feature, which adds no column |
| [C-DOM-030](../../constraints/domain/domain-constraints.md#L92) | No special-category column influences an automated outcome | PASS | `no-special-category-data-in-scoring` exits 0; this feature adds no scoring path |
| [C-DOM-031](../../constraints/domain/domain-constraints.md#L93) | Register columns carry `IsSecured=1` | PASS | Measured independently of the gate: all 16 register rows for these tables carry `IsSecured=1`, 0 exceptions |
| [C-DOM-032](../../constraints/domain/domain-constraints.md#L94) | Register columns carry `IsAuditEnabled=1` | PASS | Same measurement: 16 of 16 |
| [C-TECH-001](../../constraints/technology/technology-constraints.md#L34) | No hardcoded secrets | PASS | `secret-scan` step green in the build; the eight changed files contain no credential material |
| [C-TECH-004](../../constraints/technology/technology-constraints.md#L37) | Inputs validated | PASS | FR-151's three fields are `ApplicationRequired`. Noted: that is a form-layer control — a direct Web API create bypasses it, which is consistent with FR-151's own wording ("the payment capture surface SHALL require") |
| [C-TECH-006](../../constraints/technology/technology-constraints.md#L39) | Authentication enforced | PASS | Dataverse platform authentication; no anonymous route added |
| [C-TECH-014](../../constraints/technology/technology-constraints.md#L52) | Coverage threshold | PASS | 81.26% line coverage against 80%, measured on this artifact's own `coverage.xml` |
| [C-TECH-040](../../constraints/technology/technology-constraints.md#L82) | Roles via group teams only | PASS | No role and no group team touched; no settings file changed |
| [C-TECH-042](../../constraints/technology/technology-constraints.md#L84) | Provisioning scripts idempotent | PASS | No provisioning script added or changed |
| [C-TECH-045](../../constraints/technology/technology-constraints.md#L87) | DLP compliance | PASS | No connector used; model-driven app, not a Code App or flow |
| [C-TECH-046](../../constraints/technology/technology-constraints.md#L88) | No OOB role modified | PASS | No file under `Roles/` is in this change |
| [C-TECH-048](../../constraints/technology/technology-constraints.md#L90) | Code App data sources | PASS | No Code App change; `code-app-data-sources` and `no-secured-columns-in-code-app` both exit 0 |
| [C-TECH-051](../../constraints/technology/technology-constraints.md#L93) | No fabricated platform-assigned id | PASS | Form, section, cell and view ids are author-assigned in author-owned ranges, which is the sanctioned pattern; `guid-syntax` exits 0 over 522 id-bearing elements |
| [C-TECH-052](../../constraints/technology/technology-constraints.md#L107) | Every guessed contract has a register row | **VIOLATION** | **D-01** — the Decimal classid's marker resolves to a closed row about a different subject |
| [C-TECH-053](../../constraints/technology/technology-constraints.md#L108) | Report only the level executed | PASS | §7.2. Dev Summary §11 claims V1 for every component and V1 is what I confirmed; the V4 row correctly says NOT REACHED |
| [C-TECH-054](../../constraints/technology/technology-constraints.md#L109) | CI-runner OS | PASS | No script added by this change |
| [C-TECH-056](../../constraints/technology/technology-constraints.md#L111) | Diagnostic components removed | PASS | No environment write occurred; nothing to remove |
| [C-TECH-057](../../constraints/technology/technology-constraints.md#L127) | Every gate proven able to fail | PASS | Manifest records 76 steps with negative-test coverage asserted by `verify-build-config.py` and `BuildGates.Tests.ps1` |
| [C-TECH-058](../../constraints/technology/technology-constraints.md#L128) | OPEN assumption blocks deployment where closeable | **deferred-to-pipeline** | A-PAY-1 is OPEN. Re-evaluated this cycle rather than carried forward: `logs/pipeline.log` has **no entry** for build `20260910-3`, and its last DEV import is build `20260908-4`, which predates the `wbs:8.3` commit. The artifact is not in any environment, so A-PAY-1 is not closeable today. It becomes closeable **immediately after the DEV import** — see §8 |
| [C-TECH-059](../../constraints/technology/technology-constraints.md#L129) | Learning substrate never destroyed | PASS | Own artifact directory `…-20260910-3`, manifest intact |
| [C-TECH-060](../../constraints/technology/technology-constraints.md#L130) | No text value over its length limit | PASS | `field-length-limits` exits 0 |
| [C-TECH-064](../../constraints/technology/technology-constraints.md#L134) | Environment state verified live after deploy | **deferred-to-pipeline** | No deploy has occurred for this artifact |
| [C-TECH-065](../../constraints/technology/technology-constraints.md#L135) | Credential ≠ identity ≠ permitted operation | PASS | No script in this change performs a live call |
| [C-TECH-066](../../constraints/technology/technology-constraints.md#L136) | TAD tables are a checked specification | PASS | `tad-coverage` exits 0 — 177 column specs across 13 table blocks all exist in source |
| [C-TECH-068](../../constraints/technology/technology-constraints.md#L138) | Negative access result needs live-verified controls | **deferred** | AC-4 is the negative access test and cannot be run — see §2 and D-06 |
| [C-TECH-069](../../constraints/technology/technology-constraints.md#L140) | Readers survive a second instance | PASS | `source-reader-plurality` and `component-shape` both exit 0 with three new forms and three new views added |
| [C-TECH-070](../../constraints/technology/technology-constraints.md#L141) | Column security protects a stored value, never a projection | **PASS, with the residual named** | `field-security-coverage` exits 0: 69 secured columns all released or baselined, **no secured primary name**. Both tables' primary names are correctly `IsSecured=0`. Five secured lookups carry unsecurable name companions — see the security layer below |
| [C-TECH-071](../../constraints/technology/technology-constraints.md#L142) | Declared property reaches the creation path | PASS | `declared-property-reaches-creation-path` green in the build; this change declares no new attribute property |
| [C-TECH-073](../../constraints/technology/technology-constraints.md#L143) | Metadata writes are PUT | PASS | No metadata write in this change |
| [C-TECH-078](../../constraints/technology/technology-constraints.md#L148) | Geometry claims proven in a real browser | PASS | No geometry claim is made; model-driven layout is platform-rendered |
| [C-TECH-067](../../constraints/technology/technology-constraints.md#L137) *(SOFT)* | Tests derive counts from source | **WARNING** | `verify-source-derived-test-counts.py` reports 9 fragile literals of 11 source-coupled assertions. Pre-existing, unrelated to this change, and the fifth instance of a class this project has already recorded |

### Security layer — the projection residual, tested rather than restated

The five secured lookups on these tables each have a name companion Dataverse will not secure. I
checked what each companion actually projects rather than accepting the general warning:

| Companion column | Projects the primary name of | What that value is | Identity risk |
|---|---|---|---|
| `rev_bankaccount.rev_applicantidname` | `rev_applicant` | Autonumber `REV-A-{SEQNUM:5}`, described in source as *"a pseudonymised code and never contains the applicant's name"* | **None** |
| `rev_payment.rev_grantidname` | `rev_grant` | Autonumber `GR-{yyyy}-{SEQNUM:5}`, *"Pseudonymous by design"* | **None** |
| `rev_bankaccount.rev_provideridname`, `rev_payment.rev_provideridname` | `rev_provider` | An organisation name, deliberately not pseudonymised | **None** — an organisation is not a natural person |
| `rev_payment.rev_bankaccountidname` | `rev_bankaccount` | **Free text a human types** | **The one real path** — and it is FR-154's, which is D-02 |

So the projection surface reduces to exactly one column, and FR-154 targets exactly that column.
The design analysis is sound; the control that discharges it is not (D-02).

Two positive findings worth recording, because neither was required and both narrow the exposure:

- **Neither new view exposes a projection.** `AllPayments` shows `rev_name`, `rev_amount`,
  `rev_paymentdate`, `rev_paymentstatus`; `AllBankAccounts` shows `rev_name`, `rev_payeetype`,
  `rev_active`. No `…idname` column appears in either list, so the nickname is not projected onto
  a Payment **list** — only onto a record read.
- **Separation of duties holds in source today.** `REV Admin` has full CRUD on `rev_provider` and
  **no privilege of any kind** on `rev_bankaccount` or `rev_payment`; `REV Trustee` has none on
  any of the three. Parent NFR-002 is intact. `role-privilege-ownership` exits 0.

### NFR-150 — both halves measured

The TAD records risk **A-R58**: NFR-150's rollup half is *"held by review, not by a gate"*, and no
build step reads rollup or formula metadata. I executed that check rather than inheriting the
risk. Scanning every `Entity.xml` in the solution for `SourceType`, `IsCalculated`,
`FormulaDefinition` or a rollup declaration returns **no calculated or rollup column anywhere** —
the only matches are two comments recording a `SourceType`/`Formula` block *removed* on 2026-08-14.
The other half is verified by the change itself: commit `e37fad0` touches eight files and no
`Entity.xml` among them, so no column was added, secured or unsecured. **NFR-150 PASS, both
halves.** The gate gap A-R58 describes is still real for future changes.

### Compliance

`rev_provider` holds no personal data **on the condition FR-153 states**, and FR-153's control is
the column descriptions, which are present and correctly worded. The SDD flagged this as a
conditional pass and the condition holds. Provider's classification (parent OQ-026) stays open and
out of this feature's path, as designed.

---

## 6. Provisioning Verification

| Item (TAD §12 / §6.1) | Expected | Verified Via | Result |
|---|---|---|---|
| App module membership | Three `<AppModuleComponent type="1">` entries | Read of `AppModule.xml` — all three present at lines 123–125 | PASS |
| Site map SubAreas | Three SubAreas under the existing `rev_group_finance` group | Read of `AppModuleSiteMap.xml` — `rev_sub_providers`, `rev_sub_bankaccounts`, `rev_sub_payments` present | PASS |
| Audit switch | All three tables in `auditedTables` | Read of `test-settings.json` and `prd-settings.json` | PASS |
| `REV_FinanceOnly` membership | `REV Service Accounts` only; `REV Admins` excluded | Read of both settings files | PASS — and note the TAD's own correction: the profile has **one** member, the unattended service account, not "no member" as the SDD states |
| App sharing for `REV Finance` | Not in this task | `securityRoles` is `['REV Admin', 'REV Service Automation']` in both files, unchanged | PASS — correctly deferred to `wbs:8.2` |
| Live component verification | Every declared component present after import | — | **deferred-to-pipeline** — no import of this build |

Adding a table to a model-driven app is four changes, not two: the entity, a SubArea, an
`AppModuleComponent`, and the environment audit switch. All four are present for all three tables.
This is the check that, when missed, produces a table visible in the designer and absent in play
mode.

---

## 7. Platform Contract & Verification-Level Audit

### 7.1 Assumption register closure

| Assumption ID | Claim | Status per Dev Summary | Closing precondition | Does it exist yet? | Verified by test-agent | Result |
|---|---|---|---|---|---|---|
| A-PAY-1 | `{C3EBB6DA-…}` is the classid Dataverse assigns to a Decimal attribute | OPEN | A human opens the imported form in the designer and confirms `rev_amount` renders as a numeric editor | **The environment exists; the artifact is not in it.** `logs/pipeline.log` has no entry for build `20260910-3`; the last DEV import is `20260908-4`, before the `wbs:8.3` commit | Row present, marker present in source, status accurate | **deferred-to-pipeline** — correctly OPEN, and closeable on the next DEV import |
| **ORPHAN** | The same `{C3EBB6DA-…}` classid on `rev_roundfinance`'s five shipped Decimal columns | Marked `A-FIN-03` in source; that register row is a **different** assumption and is **closed** | Same human designer step | Same | **D-01** | **FAIL — `C-TECH-052` violation** |

**Re-evaluated this cycle rather than carried forward**, because the closing precondition is an
environment fact that can move with no source change: it has **not** moved. The 2026-09-08 DEV
import predates commit `e37fad0`, so none of this feature's eight artefacts is in any environment.

**A-PAY-1 is substantively right to stay OPEN and its stated reasons are wrong (D-04).** It says
*"No Decimal-typed attribute anywhere in this solution's committed, already-imported FormXml has
ever had a form before this change"* — but `rev_roundfinance`'s committed form carries five Decimal
controls with this exact classid, and that form was imported to DEV on 2026-09-08. It then defers
to `A-FIN-03` as "still open", and A-FIN-03 is closed and about something else. The claim that
survives is narrower and still sufficient: **nobody has yet observed a Decimal control render**, so
the classid remains unconfirmed against the platform.

**A-PAY-1 and the orphan are one assumption, not two.** Same classid, same closing action. A single
human opening either form once closes both. The Dev Summary deliberately gave it a fresh id to
avoid a namespace collision, which was the right instinct — the result is that the repository now
tracks one unverified contract under two ids, one of which collides with a closed row.

**No other orphan.** I checked every control classid in the three new forms against this solution's
own already-shipped forms: Text (7 prior forms), Two Options (4), Lookup (3), Picklist (6), Date
Only (7), Email (1, `rev_applicant.rev_email`). Every one is grounded in-solution. Decimal has
exactly one prior instance, which is the orphan above.

### 7.2 Verification levels achieved

| Component | Level claimed (Dev Summary §11) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| `AppModule.xml`, `AppModuleSiteMap.xml` | V1 | **V1** | `guid-syntax`, `root-components-resolve`, `shipped-content`, `component-shape` all exit 0 | PASS |
| Three new forms, three new views | V1 | **V1** | 16 of 16 source gates exit 0 via `run-source-gates.py` | PASS |
| C-TECH-077 coverage | V1, "69 secured columns across **15** entities" (§6) / "**13**" (§11) | **V1 — 69 across 13** | `forms-and-views-reachable` reports 69 and 13 | PASS on the measurement, **D-05** on §6's figure |
| Packaged solution | V2 (manifest) | **V2** | Both `.zip` files present, packed by pac 2.4.1; live Solution Checker ran against the packaged zip and reported 0 issues at every severity | PASS |
| Accepted by a live target | NOT REACHED | **NOT REACHED — confirmed** | No `logs/pipeline.log` entry for this build | PASS (the claim is honest) |
| Human open-and-save | NOT REACHED | **NOT REACHED — confirmed** | Follows from V3 | PASS (the claim is honest) |

**The level this cycle reached is V2, and it could not have reached higher.** V3 requires an
import, which is pipeline-agent's step and has not run for this artifact. That is an ordering fact,
not a missing test — the evidence is not yet due.

**What is *not* only an ordering fact:** V4 for the two secured tables is blocked a second time, by
`wbs:8.2`. Both blocks are real and independent, and I confirmed both against current source rather
than accepting the TAD's analysis:

- `share-apps.ps1` associates the app by role **name**; `REV Finance` appears in no settings file,
  so it cannot be granted app access.
- `rev_bankaccount.rev_accountholdername` and `rev_payeetype` are **both `ApplicationRequired` and
  `IsSecured=1`**. A user outside `REV_FinanceOnly` is asked by the platform for a value they may
  not write, so a Bank Account cannot be created at all. Measured in source, not quoted.

Both hold. The TAD's §6.2.1 analysis is accurate — **except** for the Provider form, which is
V4-reachable without `wbs:8.2` (D-07).

- Idempotency: deploy re-run against an already-deployed target → **N/A — not deployed**
- V4 designer/editor open + save → **NOT PERFORMED — deferred-to-pipeline** (and, for the two
  secured tables, additionally blocked on `wbs:8.2`)
- Cross-OS (C-TECH-054) → **N/A** — this change adds no script
- Warnings triaged (C-TECH-055) and diagnostics removed (C-TECH-056) → **PASS** — 3 warnings, 3
  accepted with rationale, 0 untriaged; no diagnostic component created

### Fail-safe defaults (the `IMP-0511` check)

I looked for any configuration default this TAD declares fail-safe that governs this surface, so
that a test reaching the approved outcome under the unseeded value could be named. **There is
none in `wbs:8.3`'s scope.** This feature reads no `rev_setting` row, has no threshold, no
staleness bound and no seeded value; column security is a platform control, not a configurable
default. The check is recorded as performed and empty, not skipped.

---

## 8. Recommendations

1. **The slug is split and it will cost someone a search.** The SDD and Dev Summary are
   `revitalise-payment-capture`; the TAD, build config, artifact and pipeline config are
   `revitalise-grant-automation`. This report is filed under the feature slug. Worth one decision
   from pm-agent about which is canonical, rather than each agent guessing.
2. **Give pipeline-agent the two obligations this cycle could not discharge.** A-PAY-1 becomes
   closeable the moment the DEV import completes, by one human opening one form in the designer —
   and that single action closes the D-01 orphan too. Under
   [C-TECH-058](../../constraints/technology/technology-constraints.md#L128) it must be closed or
   explicitly overridden before promotion beyond DEV.
3. **Open the Provider form first.** It is the one form that needs nothing from `wbs:8.2`, and
   opening it confirms four of the six control classids and AC-5 in a single V4 step.
4. **Carry AC-4 as needing a constructed identity, not as needing `wbs:8.2`.** Whoever scopes
   `wbs:8.5` needs a test principal with Read on Payment and no `REV_FinanceOnly` membership,
   created deliberately and confirmed on both membership axes before the comparison read.
5. Note for the improvement queue, not blocking: `verify-improvement-log.py` exits 0 but warns that
   IMP-0700 is corrected by IMP-0701 with no review processing it, and that the next build reaching
   the `unit-tests` step fails on it. It did not block this build; it will block the next one.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-0703 | `identifier-namespace-collision-across-documents` | blocker | An `A-nnn` marker in source is only a register row if the row it names is about the same subject — resolve the id to its row and read the row's CLAIM before trusting a marker, because `verify-assumption-markers.py` checks that the id appears in the file and cannot tell one subject from another. |
| IMP-0704 | `approved-document-internally-inconsistent` | rework | When an ADR's Decision names N interventions and its Consequences paragraph says one of them "is the entire intervention", the build will silently implement the smaller set — resolve the contradiction in the ADR before authoring against it, and never let a source header cite the ADR as authorising a reduction only half of it supports. |
| IMP-0705 | `evidence-rule-satisfied-by-a-forward-reference` | rework | A task whose approved design forbids reporting it complete on V3 evidence must not derive `complete` from V1-only source rules — split the rule so the human-verification half is tracked separately and the task derives `partial` until a dated V4 confirmation exists. |
| IMP-0706 | `dispatch-brief-asserts-unverified-fact` | friction | A dispatch brief's figures are claims: this brief stated "69 secured columns" for the `REV_FinanceOnly` profile, where 69 is the solution-wide C-TECH-077 count across 13 entities and the profile releases 16; it also named the parent Dev Summary when the feature has its own. |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py`
