# Improvement Review — 2026-11-13 (1)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 2 `NEW` → 2 clusters (scoped by the reviewer to the register entries TAD rev 39 needs)
**Trigger:** reviewer request
**Gate:** `APPROVE IMPROVEMENTS`
**Status:** APPLIED 2026-11-15 (rows 1–3) — `APPROVE IMPROVEMENTS` on revision 2 (Xander Lykopoulos, verbatim *"Approve improvements"*, 2026-11-15, relayed by lead-agent). Row 4 is approved and NOT applied: it lands in an apply-only run after development-agent writes the rev 39 Entity.xml columns. ~~DRAFT, revision 2 — parked at its gate.~~ (superseded 2026-11-15)
**WBS:** `wbs:6.8` (FR-126 feedback hours; commercial-agent attributes)

> **Revision 2 (2026-11-13).** TAD rev 39 draft 4 secures no `rev_review` column any more, and enforces FR-127 inside the app instead (TAD §6.2, *Rev 39 build correction*, item 2). So the former row 5, which added five `rev_review` columns to `pending_adjudication:`, is withdrawn. The simulation was re-run without it (states S1 to S7 below), and the gate block was recounted. Rows 1 to 4 are unchanged.

---

## Summary

The register rows TAD revision 39 needs are drafted. I ran each one against the gate before writing it here. **The gate itself cannot accept two of them yet**: it lets a column name belong to only one table, so registering ethnic group on the anonymised table as well makes it flag the applicant table's own column. That needs a one-line script fix. **The rows also cannot all land at once**: one register row applies on approval, and two must land in the same step as the columns they describe.

## What has been built

Nothing yet. This is a draft. It does three things:

1. **Measured the premises against source and the gate**: [special-category-register.yml L134](constraints/domain/special-category-register.yml#L134), [verify-domain-invariants.py L308](.engine/scripts/verify-domain-invariants.py#L308). The architect's report holds: the register has no row for the anonymised table, and `rev_conditionareas` has been on that table, unsecured and audited, since v0.2. One premise was partly wrong. The gate does see the two new copies: its duplicate check fails the build as soon as they are built (S3 below). So the finding's claim that the gate "passes because it reads only columns the register lists" is true only for condition areas.
2. **Drafted the register rows and the one script fix they need** (§3 below). I checked them in seven register and source states plus one negative test, all on scratch copies. No tracked file was touched.
3. **Decided the wellbeing answers from the register's own rules**: no row. The reason, and the one decision it leaves you, are in "What you need to decide".

## Elements changed (on approval)

| Element | Change | When |
|---|---|---|
| [special-category-register.yml](constraints/domain/special-category-register.yml#L134) `columns:` | `rev_anonymisedstatistic.rev_conditionareas`, `secured: exception` | on approval |
| [build config L665](config/revitalise-grant-automation-build.yml#L665) | `rev_conditionareas` added to the scoring-bar list | on approval |
| [verify-domain-invariants.py L308](.engine/scripts/verify-domain-invariants.py#L308) (engine) + one test in [BuildGates.Tests.ps1 L665](src/tests/build/BuildGates.Tests.ps1#L665) | a column name may have more than one declared table | on approval |
| register `columns:` | `rev_anonymisedstatistic.rev_ethnicgroup`, `.rev_exceptionalcircumstance`, `secured: exception` | **with the build** that adds the columns |

## What is still open

**The exception count in the constraint text is already stale.** [C-DOM-031](constraints/domain/domain-constraints.md#L93) says "four exceptions exist today". The gate prints six today and will print nine after this review. I left it alone because it is outside this review's scope. The gate prints the true figure on every run.

**Two TAD points this review raised are already settled in draft 4** (re-measured 2026-11-13). The trustee profile that failed the membership gate is withdrawn: §6.2 item 2 now secures no `rev_review` column. The anonymised table gains nineteen new columns, not twenty, because the eleventh wellbeing answer no longer exists in source. Neither is routed any more (§5).

## What you need to decide

**1. Do the wellbeing answers on the anonymised table need register rows? Recommended: (a) no.**

**Problem** — The SDD calls the wellbeing answers "health-related", but only ethnic group and the exceptional category are called Article 9. The application-table answers they are copied from are not in the register, are not secured, and the scoring flow reads them 11 times by design.
**Suggested fix** — (a) No rows. Record the decision in the register's "considered and not added" block, with gender and applicant type, so nobody rediscovers it. (b) Treat them as Article 9 health data. That is a decision about the application-table columns first, and it is a scoring redesign: the scoring bar works by column name, so one register row would block the scoring flow from reading its own inputs.
**What happens if you don't** — Nothing breaks. The anonymised copies get built as the TAD describes, unregistered, the same as their source columns.
[Register, "Considered and NOT added" block L483](constraints/domain/special-category-register.yml#L483)

---

**2. Confirm the three anonymised columns stay unsecured, as `secured: exception`.**

**Problem** — Your ruling said the fields may be stored. Leaving them unsecured is the TAD's design, and the register records an exception only with a named owner.
**Suggested fix** — Approving this review is that confirmation. Each row's owner line names your 2026-11-13 ruling and this review's approval. Each row's reason says the exception lapses if any identifier, lookup or reference is ever added to the table. The rows do not depend on hiding small groups. You rejected that rule (PD-3, *"No, remove that rule for all statistics."*). The exception concerns the stored rows, which carry no identifier. Trustees see only the one-attribute totals in the result document, never the rows.
**What happens if you don't** — The rows cannot be written, and the rev 39 build fails on the duplicate check as soon as the two copied columns exist.
[TAD ADR-096, "Data protection and constraints"](docs/architecture/revitalise-grant-automation-architecture.md)

---

Verification: 7 simulated states and 1 negative test run on scratch copies (§3), all re-run for revision 2. The patched script's output on the real tree is byte-identical to the current script's. **Not verified:** no Pester run, because the test is not written until apply. Nothing live.

---

## 1. Regression check — did the last review's changes work?

The last review applied was [2026-10-23 (2)](docs/improvements/2026-10-23-improvement-review-2.md). This review is scoped to the register, so I checked only whether its classes recurred. The altitude audit belongs to the batch review that processes those entries.

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| Rows 1–6 of 2026-10-23 (2) | 2026-10-23 | ten classes, among them `platform-contract-guessed-not-groundtruthed` | **YES** — six later entries in that class, all unread | Not audited here; it belongs to the batch of unread entries |
| Rows 1–6 of 2026-10-23 (2) | 2026-10-23 | the other nine classes | NO | Working, as far as recurrence shows |

**Changes whose class recurred after a *prose* fix:** not determined in this scoped review. The batch review owns it.
**Changes whose class recurred after a *gate*:** none found.

---

## 2. Clusters and promotion decisions

```
CLUSTER: register-gap-anonymised-table  (x1: IMP-1286)
Altitude:   INSTANCE — the register is a hand-adjudicated list by design (its header, and C-DOM-033's
            measured rejection of every automatic signal); the fix for a missing row is the row
Ladder row: data/knowledge row in the file that owns the decision
Becomes:    three `secured: exception` rows for rev_anonymisedstatistic (§3 rows 1 and 4); the
            scoring-bar list in the build config gains rev_conditionareas (row 2)
Retires:    nothing
Cites:      IMP-1286
Residual:   whether a column is Article 9 is still a human call. Nothing finds an Article 9 copy
            that is neither secured nor named the same as a registered column. The duplicate check
            catches a copy only when the name matches.
```

```
CLUSTER: gate-remedy-cannot-be-followed  (x1: IMP-1288)
Altitude:   CLASS within the script — the defect is in the generic engine check, and every client
            whose register declares an anonymised or archive copy hits it
Ladder row: fix the existing gate; no new gate
Becomes:    .engine/scripts/verify-domain-invariants.py maps each registered name to the SET of
            its declared tables; a table outside the set still fails (§3 row 3), plus one Pester
            case that fails on today's script and passes on the fix
Retires:    nothing
Cites:      IMP-1288
Residual:   none new. The check still cannot tell a declared copy that is wrong from one that is
            right; that is the register owner's judgement, as before.
```

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | constraint-amendment | [special-category-register.yml L316](constraints/domain/special-category-register.yml#L316), end of `columns:` | `rev_anonymisedstatistic.rev_conditionareas`, `secured: exception`, text in §3.A; and the "considered and not added" note in §3.D (on decision 1 (a)) | IMP-1286 | YES — S1: exit 0, 26 columns, 7 exceptions, alternation in sync (25 names) | N/A |
| 2 | other | [build config L665](config/revitalise-grant-automation-build.yml#L665), step `no-special-category-data-in-scoring` | Insert `rev_conditionareas` into the `body/(…)` list. Needed because the gate requires the list and the register to name the same columns. The scoring flow names it 0 times today | IMP-1286 | YES — same run as row 1 | already wired |
| 3 | script | [.engine/scripts/verify-domain-invariants.py L308](.engine/scripts/verify-domain-invariants.py#L308) + [BuildGates.Tests.ps1 L665](src/tests/build/BuildGates.Tests.ps1#L665) + new fixture `register-two-homes.yml` | DUPLICATE-ENTITY keys on name → set of declared tables (§3.C) | IMP-1288 | YES — S4 fails, S5 passes; a third undeclared table fails (C2); real-tree output byte-identical (C1) | already wired — `domain-invariants`, HARD, [build config L621](config/revitalise-grant-automation-build.yml#L621) |
| 4 | constraint-amendment | register `columns:`, after row 1 | `rev_anonymisedstatistic.rev_ethnicgroup` and `.rev_exceptionalcircumstance`, `secured: exception`, text in §3.A. **Applied in the same change as the Entity.xml columns, after row 3** | IMP-1286 | YES — S5: exit 0; S7 shows it fails if applied before the columns exist | N/A |

**Constraint budget:** 0 of 3 used. No new constraint. Rows 1 and 4 are data under C-DOM-030 and C-DOM-031 as written.

### Why row 4 cannot land on approval

The gate checks both directions, so either order breaks the build for a while:

| State | Gate result |
|---|---|
| Row 4 in the register, columns not built (S7) | FAIL — the register names 2 columns that do not exist |
| Columns built, row 4 absent (S3, either script) | FAIL — 2 duplicate-table errors |
| Both, with row 3's script fix (S5) | PASS |
| Both, without row 3 (S4) | FAIL — the gate flags the applicant and application tables' own columns as the duplicates |

**So, in this order:** rows 1–3 on approval. Then development-agent writes the rev 39 Entity.xml changes, then an apply-only improvement-agent dispatch adds row 4 with the approved text, and only then does the build run. development-agent cannot write the register: the protection hook refuses it ([register header L30](constraints/domain/special-category-register.yml#L30)). TAD §12.1 already orders the live schema step after the register entries.

**Nothing has to remember row 4.** If the columns are built without it, the HARD `domain-invariants` step fails and names both columns (S3). I did not record row 4 as `approved_in`. I simulated that form on a scratch log: `verify-improvement-log.py --check` exits 1 with an approved-not-applied trigger, and that is a HARD build step. Every build of every feature would halt between approval and the rev 39 Entity.xml change. The gate that owns the register is already the reminder here, and a halt on unrelated work would add nothing.

### §3.A — `columns:` rows (rows 1 and 4)

Inserted after `rev_supportrecipientdisabilityimpactdescription`, the last row of `columns:`. Row 1 is the comment block plus the first entry; row 4 is the second and third entries.

```yaml

  # ── Anonymised statistics: Article 9 content held without identifiers ──────
  # ADDED <apply date> by improvement review 2026-11-13 (IMP-1286). rev_anonymisedstatistic was
  # classed "not personal data" (SDD §7.1) and so never reached this file, although it has held
  # grouped condition areas since v0.2. An anonymised copy of an Article 9 field is still an
  # Article 9 field for this register: it is adjudicated where it is stored. The source columns
  # keep their own rows (rev_applicant.rev_ethnicgroup stays secured; rev_application's
  # rev_exceptionalcircumstance stays a panel-visible exception).
  #
  # WHY `secured: exception` AND NOT `required`: the row carries no name, address, reference or
  # lookup, so column security would protect no identifiable person. The exception holds ONLY
  # while that stays true. TAD rev 39 ADR-096 item 9 (PD-4) also limits reading the rows to the
  # process owner and the service identity, because the rows hold combinations of attributes;
  # until that role change is built, REV Trustee and REV Finance still hold Read on the table.
  # WHAT WOULD REVERSE IT: an identifier, lookup or reference number added to the table. Then
  # make these rows `secured: required` and tell the reviewer.
  - name: rev_conditionareas
    entity: rev_anonymisedstatistic
    basis: "Art. 9 — health: grouped condition areas, held anonymised (FR-055, FR-126; SDD §7.1 Anonymised row)"
    secured: exception
    reason: >
      anonymised; no identifier on the row. Retained indefinitely as a statistic (FR-055); the
      exception lapses if any identifier, lookup or reference is added to rev_anonymisedstatistic.
    owner: "Reviewer (Xander Lykopoulos): storage ruled 2026-11-13 (SDD §7.1, FR-126); unsecured posture confirmed by APPROVE IMPROVEMENTS on docs/improvements/2026-11-13-improvement-review.md"
  - name: rev_ethnicgroup
    entity: rev_anonymisedstatistic
    basis: "Art. 9 — racial or ethnic origin (coded), held anonymised on Received rows (FR-126, TAD ADR-096 item 3)"
    secured: exception
    reason: >
      anonymised; no identifier on the row. Copied once at intake from rev_applicant.rev_ethnicgroup
      (which stays secured); the exception lapses if any identifier is added to the table.
    owner: "Reviewer (Xander Lykopoulos): storage ruled 2026-11-13 (SDD §7.1, FR-126); unsecured posture confirmed by APPROVE IMPROVEMENTS on docs/improvements/2026-11-13-improvement-review.md"
  - name: rev_exceptionalcircumstance
    entity: rev_anonymisedstatistic
    basis: "Art. 9 — exceptional circumstance (coded), held anonymised on Received rows (FR-126, TAD ADR-096 item 3)"
    secured: exception
    reason: >
      anonymised; no identifier on the row. Copied once at intake from
      rev_application.rev_exceptionalcircumstance; the exception lapses if any identifier is added.
    owner: "Reviewer (Xander Lykopoulos): storage ruled 2026-11-13 (SDD §7.1, FR-126); unsecured posture confirmed by APPROVE IMPROVEMENTS on docs/improvements/2026-11-13-improvement-review.md"
```

The two new columns must carry `<IsAuditEnabled>1</IsAuditEnabled>` in Entity.xml, because C-DOM-032 has no exception route. The TAD says "audited at table level", but the gate reads the column flag, so development-agent sets both. `rev_conditionareas` already carries it.

### §3.B — withdrawn in revision 2

Revision 1 added `rev_review.rev_verdict1`, `rev_verdict2`, `rev_notes1`, `rev_notes2` and `rev_finalisedon` to `pending_adjudication:`, because TAD draft 3 column-secured them. Draft 4 secures none of them, and C-DOM-033 asks for a row only for a secured column. A `pending_adjudication` row would also claim a security setting the column does not have. Re-measured 2026-11-13: all five are `IsSecured` 0 in source, and S5 passes without them.

### §3.C — the script fix (row 3)

In `.engine/scripts/verify-domain-invariants.py`, the DUPLICATE-ENTITY loop:

```python
    registered_names: dict[str, set[str]] = {}
    for e in columns:
        registered_names.setdefault(str(e.get("name") or "").strip().lower(), set()).add(
            str(e.get("entity") or "").strip())
    for (entity, name), meta in sorted(attributes.items()):
        declared_entities = registered_names.get(name)
        if declared_entities and entity not in declared_entities:
            declared_entity = ", ".join(sorted(declared_entities))
```

The error message below it is unchanged and still reads `declared_entity`. The docstring line for DUPLICATE-ENTITY gains "on an entity the register does not declare it on, **in any of its rows**".

A new fixture, `src/tests/fixtures/known-bad/domain-invariants/register-two-homes.yml`, declares `rev_fixturecondition` on both fixture tables. A new `It` after the C-DOM-004 case asserts the output does **not** match `DUPLICATE-ENTITY`. I ran both scripts against it: the current one prints 1 such error and the fix prints 0. The existing case, with the copy undeclared, still prints 1 under both.

**Publishing:** `scripts/verify-domain-invariants.py` is a wrapper, so the change is in the `.engine` submodule only, which is on branch `retention-automation`. It takes an engine commit, then a push to the branch containing its parent, then the pointer bump here, in that order.

### §3.D — "considered and not added" (row 1, on decision 1 (a))

Appended to the existing block at [register L483](constraints/domain/special-category-register.yml#L483):

```yaml
  # Considered and NOT added, <apply date> (TAD rev 39 ADR-096, improvement review 2026-11-13):
  # rev_anonymisedstatistic's rev_wellbeinganswer1..10 and rev_feelingscaleanswer, rev_gender,
  # rev_applicanttype. SDD §7.1 calls the wellbeing answers health-related, not Article 9, and
  # their rev_application sources are unregistered scored inputs of FR-016 — registering a copy
  # by name would bar the scoring flow from its own inputs. rev_gender is ordinary personal data
  # (its own Entity.xml says so); applicant type is a reporting dimension. Reverse only by
  # adjudicating the rev_application source columns first.
```

### Simulation record (scratch copies only; re-run for revision 2)

"rev 39 built" means two audited, unsecured picklist columns added to the anonymised table. No `rev_review` column is changed, per draft 4.

| # | Register | Source | Script | Exit | What it showed |
|---|---|---|---|---|---|
| S1 | + row 1 | today | current, and fixed | 0, 0 | Rows 1 and 2 can land on approval: 26 columns, 7 exceptions, 88 secured = 19 + 69 pending |
| S2 | + rows 1, 4 | today | current | 1 | Row 4 before the columns exist: 2 missing-column and 2 duplicate errors |
| S3 | + row 1 | rev 39 built | current, and fixed | 1, 1 | 2 duplicate errors: row 4 is forced by the gate |
| S4 | + rows 1, 4 | rev 39 built | current | 1 | The script defect: it flags the source tables' own columns |
| S5 | + rows 1, 4 | rev 39 built | fixed | 0 | 28 columns, 9 exceptions, 88 secured = 19 + 69 pending |
| S7 | + rows 1, 4 | today | fixed | 1 | Order matters: 2 missing-column errors |
| C1 | today | today | both | 0, 0 | Output byte-identical (`diff`) |
| C2 | + rows 1, 4 | built + a third copy on `rev_review` | fixed | 1 | An undeclared third table still fails |

S6 from revision 1, which tested the Finalised On row, no longer applies and was dropped.

---

## 4. Retirements

> Retirement check performed: C-DOM-030, C-DOM-031, C-DOM-032 and C-DOM-033 reviewed, none redundant. Each fails a distinct simulated state above. C-DOM-031's Verify By count ("four exceptions") is stale, but that is a wording fix, not a retirement, and it is outside this review's scope.

---

## 5. Findings left unprocessed

**Deferred:** IMP-1252, IMP-1253, IMP-1254, IMP-1255, IMP-1256, IMP-1257, IMP-1258, IMP-1259, IMP-1260, IMP-1261, IMP-1262, IMP-1263, IMP-1264, IMP-1265, IMP-1266, IMP-1267, IMP-1268, IMP-1269, IMP-1270, IMP-1271, IMP-1272, IMP-1273, IMP-1274, IMP-1275, IMP-1276, IMP-1277, IMP-1278, IMP-1279, IMP-1280, IMP-1281, IMP-1282, IMP-1283, IMP-1284, IMP-1285, IMP-1287, IMP-1289, IMP-1290

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| IMP-1252 … IMP-1284 | various | Out of scope by the reviewer's brief | the separate batch review |
| IMP-1285 | `agent-output-corrected-by-reviewer-fidelity` | Named in the brief, but it is about credit sizing, not the register | the batch review |
| IMP-1287 | `locked-on-form-not-locked-on-server` | Its register consequence disappeared with draft 4. Its proposal is a rule for architect-agent, which belongs to the batch | the batch review |
| IMP-1289 | `design-contradicts-existing-gate` | Logged by this review. **Addressed by architect-agent in TAD draft 4**: the trustee profile is withdrawn (§6.2 item 2). No longer routed | the batch review, to close against draft 4 |
| IMP-1290 | `downstream-assertion-not-updated-with-source-change` | Logged by this review. **Addressed in TAD draft 4**, which now says nineteen columns. No longer routed | the batch review, to close against draft 4 |

**Routed work (re-measured 2026-11-13 for revision 2):**

| To | Item | Measured |
|---|---|---|
| lead-agent | Sequence row 4 between development-agent's Entity.xml change and the build | §3, order table |
| ~~architect-agent~~ | ~~Make REV_ReviewTrustee fit the membership gate~~ | **Withheld:** done in draft 4 |
| ~~architect-agent~~ | ~~Drop `rev_wellbeinganswer11` from ADR-096~~ | **Withheld:** draft 4 says nineteen |

---

## 6. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 1286 | 1286 (no new entries at apply) |
| Status moves at apply | — | IMP-1286 and IMP-1288 → APPLIED |

Regenerated with `python3 scripts/generate-known-failure-modes.py` at apply; confirmed with `--check`.

### Dispositions (decided from `observable_at`)

| Finding | `observable_at` | Disposition |
|---|---|---|
| IMP-1286 | n/a | **CLOSE** at apply, on row 1. `evidence_grep` on the register: `exception lapses if any identifier, lookup or reference is added`. Row 4 is enforced by `domain-invariants` (S3), not by this entry |
| IMP-1288 | n/a | **CLOSE** at apply. `evidence_grep` on `.engine/scripts/verify-domain-invariants.py`: `declared_entities = registered_names.get(name)` |

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-11-13-improvement-review.md

Findings processed: 2 NEW  →  2 clusters
Regression check:   1 prior review audited (class recurrence only), 1 class recurred
Proposed:           0 constraints (cap 3), 2 constraint amendment, 1 gates/scripts,
                    0 skill/knowledge edits, 0 agent-file edits, 0 retirements
                    (+ 1 other: the build config's scoring-bar list)
Altitude calls:     1 generalised from instance to class, 1 left as notes
Digest:             will regenerate — 0 new lessons at apply, 0 recurring classes added

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Applied

Applied 2026-11-15, rows 1–3, against the tree re-verified first: targets unchanged since the draft, no later finding `corrects` either entry, and the scoring flow still names `rev_conditionareas` 0 times.

**Decisions recorded.** The reviewer did not answer decisions 1 and 2 separately. Lead-agent relayed them as the recommended answer, "agree": (1) (a), so wellbeing answers, gender and applicant type get no register rows, and the "considered and not added" note (§3.D) is applied; (2) the three anonymised columns stay unsecured as `secured: exception`. TAD D5 was answered *"Protection in the admin app."* That changes no data model, so row 5 stays withdrawn.

| # | Change | Applied at | Entries moved to APPLIED |
|---|---|---|---|
| 1 | [special-category-register.yml](constraints/domain/special-category-register.yml#L341), the §3.A block and `rev_conditionareas` row, plus the §3.D note at the end of the "Considered and NOT added" block | uncommitted working tree, 2026-11-15 | IMP-1286 |
| 2 | [build config L665](config/revitalise-grant-automation-build.yml#L665): `rev_conditionareas` in the `no-special-category-data-in-scoring` list | uncommitted working tree | IMP-1286 |
| 3 | [.engine/scripts/verify-domain-invariants.py](.engine/scripts/verify-domain-invariants.py#L308), name → set of declared entities, plus the docstring line; fixture `src/tests/fixtures/known-bad/domain-invariants/register-two-homes.yml`; one `It` in [BuildGates.Tests.ps1](src/tests/build/BuildGates.Tests.ps1#L676) | `.engine` working tree, **not committed, not pushed, pointer not bumped** | IMP-1288 |

**One addition to the approved text, comment only.** Row 1's block carries one extra paragraph. It is headed PENDING and says that row 4's two rows join it, with the same reason, when the columns are built, and that `domain-invariants` enforces the order. It changes no rule and no row. It is there so a reader of the register sees the approved-but-unapplied rows.

**One correction caused by this apply.** Regenerating the digest drifted the registered `CURRENT SIZE` sentence in `scripts/generate-known-failure-modes.py` from 645 to 647 lines. It now reads 647, and `verify-derived-counts.py` exits 0.

**Gates run after applying:**

| Gate | Result |
|---|---|
| `domain-invariants` (real tree, build-step arguments) | exit 0 — 26 columns, 7 exceptions, alternation in sync (25 names), 88 secured = 19 + 69 pending |
| `no-special-category-data-in-scoring` (the step's own command) | exit 0 |
| Pester, `BuildGates.Tests.ps1` filtered to `domain-invariants` | 10 passed, 0 failed (the new case included) |
| `no-trustee-in-column-security-profile` | exit 0 |
| `verify-build-config.py` | exit 0 |
| `verify-improvement-log.py --check` | exit 0; IMP-1286 and IMP-1288 APPLIED, needles 1 each |
| `generate-known-failure-modes.py --check` | current (1288 entries) |
| `verify-derived-counts.py` | exit 0 after the correction above |
| `verify-engine-instance-split.py`, `verify-class-defences.py` | exit 0, exit 0 |

**TAD rev 39 constraint check.** Run with the rev 39 columns added to a scratch copy of the solution, against the register as applied: exit 1. It fails on exactly 2 violations, both DUPLICATE-ENTITY: `rev_anonymisedstatistic.rev_ethnicgroup` and `rev_anonymisedstatistic.rev_exceptionalcircumstance`. Those are row 4's two columns, and row 4 clears them (S5).

**The engine change is not yet published.** The wrapper loads `.engine/scripts/verify-domain-invariants.py` from the working tree, so every local run uses the fix now. A fresh clone or CI runs the pinned engine commit `657f56a`, which does not have it. Publishing takes three steps: an engine commit, a push to `origin/retention-automation` (the branch containing its parent), then the pointer bump committed here. **Row 4 must not land before that**, or a clean checkout fails S4's duplicate errors. No commit was made, because none was asked for.

