# Test Report — Trustee Portal: org-url-null read-path fix

**Feature Slug:** trustee-portal-org-url-fix
**Artifact:** build/artifacts/revitalise-grant-automation-20260823-3/
**Date:** 2026-08-23
**Status:** PARTIAL

---

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit | 233 | 233 | 0 | 0 |
| Integration | 233 | 233 | 0 | 0 |
| End-to-End | 0 | — | — | 5 (blocked — needs V4, see §7.2) |
| Regression | 233 | 233 | 0 | 0 |
| Security | 3 (code review) | 3 | 0 | 0 |
| Accessibility | 0 | — | — | N/A — no UI/screen changed this dispatch |
| Performance | 0 | — | — | N/A — [NFR-022](../plans/revitalise-grant-automation-plan.md#L399) states no threshold exists |
| Provisioning | 0 | — | — | N/A — no entity, role, or provisioning file changed |
| Compliance | 1 (CR-01) | 1 | 0 | 0 |
| **Total** | 233 (+4 code-review checks) | 237 | 0 | 5 |

Unit/Integration/Regression figures are one suite (Vitest, this app has no seam between them) —
independently re-run this session, not taken on trust from the manifest:
`npm test -- --run` inside `src/code-apps/trustee-review-portal` → 233/233 passing, 16 files.
`npm run typecheck` (`tsc --noEmit`) and `npm run lint` (`eslint .`) both exited clean, no output.
These three commands and their outcomes match
[manifest.json:60-63](../../build/artifacts/revitalise-grant-automation-20260823-3/manifest.json#L60)
exactly.

## 2. Requirement Coverage

| FR ID | Requirement | Test Case(s) | Result |
|---|---|---|---|
| [FR-034](../plans/revitalise-grant-automation-plan.md#L339) | Sortable/filterable trustee summary list | `client.test.ts` `listRecords` describe block (14 cases) — proves the read reaches `rev_applications` via the typed service | PASS at V2/V3-adjacent (mocked SDK); the list rendering itself unchanged and covered by `ApplicationsListPage.test.tsx` (18 cases, unaffected by this fix, re-run green) |
| [FR-035](../plans/revitalise-grant-automation-plan.md#L340) | Per-application detail view | `client.test.ts` `getRecord` describe block (6 cases) | Same basis as FR-034 |
| [FR-037](../plans/revitalise-grant-automation-plan.md#L342) | Record Approve/Defer/Reject verdict | `client.test.ts` `updateRecord` describe block (3 cases) — proves the write path is **unchanged** | PASS — this fix does not touch the write path; `VerdictSection.test.tsx` (12 cases) unaffected and re-run green |
| [FR-038](../plans/revitalise-grant-automation-plan.md#L343) | Restrict to applications eligible for the current round | Unaffected — `filter`/`select` plumbing through `listRecords` is unchanged in shape, only the transport moved | PASS at the same basis as FR-034 |
| [FR-039](../plans/revitalise-grant-automation-plan.md#L344) | Print/offline export | `print.test.ts` "declares exactly one column allow-list per read" (updated for the new call-site literal, same invariant) | PASS — re-run green, still asserts exactly 2 matches |

**All five FRs share one ceiling**: every "PASS" above is proven against a **mocked** Power Apps
SDK (Vitest), never against a live Dataverse connection or a real signed-in trustee. That is
exactly the gap this whole dispatch exists to close and has not yet closed — see §7.2. None of
these FRs can be marked verified end-to-end until the reviewer's V4 step runs.

## 3. Failed Tests

None. 0 of 233 tests failed; `tsc` and `eslint` both clean.

## 4. Defects Raised

None new. The defect this dispatch responds to
([IMP-0224](../../logs/improvement-log.jsonl), status `NEW`) is not raised again here, and is not
closed here either — see §7.1/§7.2.

## 5. Constraint & Compliance Verification

Full scope per [test-agent.md](../../agents/test-agent.md#L73) — both files, HARD + SOFT, rows
listing `test-agent`. Six domain rows and 22 tech rows are in scope; results below distinguish
what this diff itself demonstrates from what is unaffected and already evidenced by
[manifest.json](../../build/artifacts/revitalise-grant-automation-20260823-3/manifest.json) (the
whole-solution gate suite, re-confirmed unchanged for every non-Code-App gate since the last green
build today).

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| [C-DOM-004](../../constraints/domain/domain-constraints.md#L37) | No personal data in logs | PASS | Unaffected — no logging code touched; `rev_errorlog` unchanged |
| [C-DOM-010](../../constraints/domain/domain-constraints.md#L47) | CRUD on sensitive entities audit-logged | PASS | Unaffected — no entity or audit config touched |
| [C-DOM-011](../../constraints/domain/domain-constraints.md#L48) | Audit log schema | PASS | Unaffected |
| [C-DOM-030](../../constraints/domain/domain-constraints.md#L92) | No special-category column drives an automated outcome | PASS | Unaffected — no column, scoring, or select-list touched beyond transport; `no-special-category-data-in-scoring` reconfirmed PASS in this build |
| [C-DOM-031](../../constraints/domain/domain-constraints.md#L93) | Register columns carry `IsSecured` | PASS | Unaffected — no schema change |
| [C-DOM-032](../../constraints/domain/domain-constraints.md#L94) | Register columns carry `IsAuditEnabled` | PASS | Unaffected — no schema change |
| [C-TECH-001](../../constraints/technology/technology-constraints.md#L34) | No hardcoded secrets | PASS | `git diff HEAD -- src/code-apps/trustee-review-portal/` read in full — no credential, token, or secret literal; manifest secret-scan clean |
| [C-TECH-004](../../constraints/technology/technology-constraints.md#L37) | Inputs validated/sanitised | PASS | No new input surface; `$select` allow-lists stay compiler-mandatory (`readonly string[]`) at [client.ts:221](../../src/code-apps/trustee-review-portal/src/dataverse/client.ts#L221) and [client.ts:272](../../src/code-apps/trustee-review-portal/src/dataverse/client.ts#L272) |
| [C-TECH-006](../../constraints/technology/technology-constraints.md#L39) | Auth enforced on non-public operations | PASS | Unaffected — both transports still resolve identity through the Power Apps SDK's own auth (per-user OAuth for the generic connector, launch-time runtime metadata for the typed services); no route bypasses it |
| [C-TECH-014](../../constraints/technology/technology-constraints.md#L52) | Coverage threshold | PASS | 97.8% Code App line coverage (independently re-run this session), 80% threshold |
| [C-TECH-040](../../constraints/technology/technology-constraints.md#L82) | Roles via group teams only, Test/Acc/Prd | PASS | Unaffected — no role/team assignment in this diff |
| [C-TECH-042](../../constraints/technology/technology-constraints.md#L84) | Provisioning scripts idempotent | PASS | Unaffected — no provisioning script changed |
| [C-TECH-045](../../constraints/technology/technology-constraints.md#L87) | DLP-compliant connectors only | PASS | No new connector — both transports are Dataverse-family, already declared |
| [C-TECH-046](../../constraints/technology/technology-constraints.md#L88) | OOB roles never modified | PASS | Unaffected |
| [C-TECH-048](../../constraints/technology/technology-constraints.md#L90) | Code Apps read/write only via CLI-generated data source | PASS | Reads now dispatch to the four CLI-generated (`pa app add data-source --table`) typed services; write stays on the CLI-generated generic connector. No MSAL/manual token code anywhere in [client.ts](../../src/code-apps/trustee-review-portal/src/dataverse/client.ts) — read in full |
| [C-TECH-051](../../constraints/technology/technology-constraints.md#L93) | No fabricated platform-assigned ids | PASS | Unaffected — no id-bearing component touched |
| [C-TECH-052](../../constraints/technology/technology-constraints.md#L107) | Unvalidated Assumptions Register complete, no orphans | PASS | See §7.1 — register cross-checked against the diff, no orphan guess found |
| [C-TECH-053](../../constraints/technology/technology-constraints.md#L108) | Reported only at the level executed | PASS | Dev Summary §11 and the manifest both cap the claim at V2/V3-adjacent and name the reviewer as the V4 owner — no overclaim found. (This is a claim-honesty check; whether V4 itself has happened is a separate question, answered in §7.2 and reflected in this report's overall `PARTIAL` status, not in this row) |
| [C-TECH-054](../../constraints/technology/technology-constraints.md#L109) | Scripts run on the CI runner's OS | PASS | Unaffected — no new script; toolchain (npm/tsc/vitest/eslint) is already cross-platform and CI-portable |
| [C-TECH-056](../../constraints/technology/technology-constraints.md#L111) | Diagnostic components removed | PASS | The diagnostic `dataSourcesInfo.ts` regeneration described in Dev Summary §1/§11 is absent from `git status --porcelain` — confirmed reverted, not committed |
| [C-TECH-057](../../constraints/technology/technology-constraints.md#L127) | Every gate provably able to fail | PASS | Unaffected by this diff — 28 build gates, all with negative-test coverage, per manifest |
| [C-TECH-058](../../constraints/technology/technology-constraints.md#L128) | OPEN register row blocks deployment where closeable | **PASS, forward-flagged** | `A-TRM-3` is `OPEN` (see §7.1), but this build has not yet been deployed anywhere — the environment that would make it closeable (DEV running *this* build) does not exist yet. Not a violation at the Test gate; pipeline-agent must re-evaluate this row before declaring DEV deployed, per this constraint's own text |
| [C-TECH-059](../../constraints/technology/technology-constraints.md#L129) | Learning substrate never destroyed | PASS | Re-run independently this session: `verify-improvement-log.py --check` → OK, 224 entries; `generate-known-failure-modes.py --check` → current, 224 entries; artifact directory unique |
| [C-TECH-060](../../constraints/technology/technology-constraints.md#L130) | No shipped value over its length limit | PASS | Unaffected — no schema/settings value in this diff |
| [C-TECH-064](../../constraints/technology/technology-constraints.md#L134) | Live environment state verified against intent | PASS | Unaffected — no environment-state category (audit, option sets, field permissions, roles) touched by this diff |
| [C-TECH-065](../../constraints/technology/technology-constraints.md#L135) | Identity/capability prerequisites declared before use | PASS | Unaffected by this diff; `code-apps-feature` prerequisite already declared upstream, confirmed present in manifest |
| [C-TECH-066](../../constraints/technology/technology-constraints.md#L136) | TAD schema/access is a checked specification | PASS | Unaffected — no column or access-privilege change |
| [C-TECH-067](../../constraints/technology/technology-constraints.md#L137) SOFT | Counts/membership derived from source, not hand-typed | **WARN (pre-existing, unrelated)** | This diff's own new count-coupled assertions carry the required rationale comment (`client.test.ts`'s four-table dispatch test, `print.test.ts`'s "exactly 2" assertion) — compliant. The WARN is the 6 pre-existing fragile literals in the Pester suite the manifest already names, untouched by this dispatch |

**CONSTRAINT CHECK**
```
Domain   HARD: 6 / 6 of 6    |  violations: NONE
                             |  unevaluable: NONE
Domain   SOFT: 0 in scope    |  warnings:   NONE
Tech     HARD: 21 / 21 of 21 |  violations: NONE
                             |  unevaluable: NONE
Tech     SOFT: 1 in scope    |  warnings:   C-TECH-067 (pre-existing, unrelated to this fix)
Overall: WARN
```

## 6. Provisioning Verification

N/A — no entity, security role, group team, app sharing, or provisioning script changed by this
dispatch (confirmed by `git diff --stat HEAD -- src/code-apps/trustee-review-portal/` — only
`client.ts`, `client.test.ts`, `print.test.ts`, `README.md`). [TAD §12](../architecture/revitalise-grant-automation-architecture.md#L1554)
items are unaffected by this fix.

## 7. Platform Contract & Verification-Level Audit (C-TECH-052, C-TECH-053)

### 7.1 Assumption register closure

| Assumption ID | Claim | Status per Dev Summary | Closing precondition | Does it exist yet? | Verified by test-agent | Result |
|---|---|---|---|---|---|---|
| A-TRM-1 | Generated `update()` has no `If-Match` path, cannot replace `updateRecord()`'s guard | CLOSED — negative | N/A (closed) | N/A | Re-read [client.ts:332-345](../../src/code-apps/trustee-review-portal/src/dataverse/client.ts#L332) — write path confirmed unchanged, still on the generic connector | Confirmed closed |
| A-TRM-2 | Migrating reads is mechanically compatible with the app's mandatory `$select` allow-list | CLOSED by construction | N/A (closed) | N/A | Re-read [client.ts:220-221](../../src/code-apps/trustee-review-portal/src/dataverse/client.ts#L220) and [client.ts:271-272](../../src/code-apps/trustee-review-portal/src/dataverse/client.ts#L271) — `select` is still `readonly string[]`, mandatory | Confirmed closed |
| [A-TRM-3](../development/trustee-portal-org-url-fix-dev-summary.md#L142) | Whether a 404 from the typed `get()` throws or resolves has not been observed live | OPEN | A real signed-in trustee requests a known-deleted id against DEV, post-deploy | **No** — this build has not been pushed to any environment yet (verification level is V2, see §7.2) | Code inspected: both branches are handled defensively at [client.ts:300](../../src/code-apps/trustee-review-portal/src/dataverse/client.ts#L300) (thrown path) and [client.ts:308](../../src/code-apps/trustee-review-portal/src/dataverse/client.ts#L308) (resolved-failure path) | Correctly OPEN — cannot close before deploy; not an orphan, not overdue |

No orphan guesses found: every hand-authored decision in the diff (the `READ_SERVICES` dispatch
table, the dual 404 check, the mandatory `select` type) traces to a register row or to prior E1
evidence cited in the [client.ts](../../src/code-apps/trustee-review-portal/src/dataverse/client.ts#L1)
file header.

### 7.2 Verification levels achieved

| Component | Level claimed (Dev Summary §11) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| `client.ts` reads (typed-service dispatch) | V2 (packages) | **V2, confirmed** | `npm run build` independently re-run this session — succeeds, matches [manifest.json:63](../../build/artifacts/revitalise-grant-automation-20260823-3/manifest.json#L63) | PASS |
| `client.ts` reads — unit contract | V1/V2-adjacent, mocked | **Confirmed** | `npm test -- --run` independently re-run — 233/233, against a mocked SDK only | PASS at the level claimed |
| `client.ts` write path ([client.ts:322-346](../../src/code-apps/trustee-review-portal/src/dataverse/client.ts#L322)) | Unchanged from prior verification | **Confirmed unchanged** | `git diff` shows zero lines changed in `updateRecord`; its tests unchanged in substance | PASS |
| Architectural claim (typed services resolve org URL independently of the connector) | E1 (not a V-level) | Not independently re-read this session | Dev Summary cites `dataverseDataOperationExecutor.js`'s `_getDataverseDataSourceInfo` directly — E1 evidence, correctly not conflated with a V-level per [how-to-verify-a-platform-contract.md §2](../../skills/how-to-verify-a-platform-contract.md#L71) | Accepted as reported |
| **The live defect itself (IMP-0224) — a real signed-in trustee's read succeeding** | **NOT REACHED. V4 not performed** | **NOT REACHED** | No host/browser access from this session either — same ceiling the dispatch instruction and [manifest.json:22](../../build/artifacts/revitalise-grant-automation-20260823-3/manifest.json#L22) already state | **Not closed. Cannot be closed by this Test Report** |

- Idempotency: N/A — nothing deployed yet to re-run a deploy against.
- V4 designer/editor open + save, performed by `<name>` on `<date>` → **NOT PERFORMED**. Per
  [C-TECH-053](../../constraints/technology/technology-constraints.md#L108)'s 2026-08-23
  amendment, [IMP-0224](../../logs/improvement-log.jsonl) and
  [IMP-0227](../../logs/improvement-log.jsonl) may be closed only by a named person re-running
  the original three-call reproduction (systemuser lookup by Entra object id, systemuser lookup
  by domain name, `rev_applications` list) as a real signed-in trustee, post-deploy, and
  recording a `reobserved` entry — a document, a clean build, or this Test Report cannot supply
  that evidence at any confidence level.
- Cross-OS (C-TECH-054): N/A — no new script.
- Warnings triaged (C-TECH-055) and diagnostic components removed (C-TECH-056) → **PASS** — see
  §5 row C-TECH-056; all 5 build warnings triaged per manifest, none untriaged.

**This is why the Result at the top of this report is `PARTIAL`, not `PASS`.** Every layer this
session could execute — the full Vitest suite, `tsc`, `eslint`, the production build, the
constraint sweep — passed cleanly, independently re-run rather than taken on the manifest's word.
None of that reaches the level the defect itself was reported at. Per
[test-agent.md](../../agents/test-agent.md#L109), "the run is PARTIAL, never PASS" whenever a
component has not been executed end-to-end at the level its defect requires — here the component
has not even reached V3 yet, so a fortiori it cannot be PASS. It is not FAIL either: nothing this
session ran found a defect, a regression, or a constraint violation. `IMP-0224` and `IMP-0227`
stay `NEW`, exactly as they arrived.

## 8. Recommendations

1. **Approve to Pipeline for a DEV deploy** — everything static and automatable is clean, and the
   only remaining verification is inherently post-deploy.
2. **Immediately after DEV deploy**, the reviewer (named in
   [Dev Summary §11](../development/trustee-portal-org-url-fix-dev-summary.md#L172),
   XLykopoulos@revitalise.org.uk) re-runs the original three-call reproduction as a real
   signed-in trustee. Record the result as a `reobserved` entry on both `IMP-0224` and
   `IMP-0227` — success or failure both close the open question; silence does not.
3. If the reviewer's V4 step fails on any of the three calls, do not re-attempt a fourth CLI
   regeneration of the generic connector — [IMP-0226](../../logs/improvement-log.jsonl) already
   closed that direction as unfixable via CLI. Route straight back to development-agent with the
   specific call and error.
4. Once DEV deploy exists, re-evaluate `A-TRM-3` (§7.1) and `C-TECH-058` (§5) — both were
   correctly deferred here only because no environment running this build existed yet.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| none | — | — | This cycle re-confirmed existing findings ([IMP-0224](../../logs/improvement-log.jsonl), [IMP-0227](../../logs/improvement-log.jsonl)) rather than surfacing a new one; nothing this session ran contradicted a document, required a second attempt, or found a gate broken |

Digest regenerated: NO — no new entry to add; `generate-known-failure-modes.py --check` already
confirmed current at 224 entries this session.
