# Improvement Review — 2026-10-22

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 0 `NEW` → 1 cluster (a reviewer-requested capability change, not a defect batch)
**Trigger:** reviewer request — *"Yes.. add the rows to the register. Let improvement agent do it."* (Xander Lykopoulos, 2026-10-22, relayed by lead-agent, routing 12:42)
**Status:** APPLIED 2026-10-22 12:57, rows 1 and 2, to the working tree, on the reviewer's "Approve improvements" (Xander Lykopoulos, 2026-10-22, relayed by lead-agent). The engine commit, its push and the pointer bump are the reviewer's (see *What you need to decide*). See the [applied record](#applied-record--2026-10-22).
**Serves:** `wbs:6.3`, WI-0146, `feature:trustee-portal-design-2`
**Authorising design:** portal TAD Revision 4, [ADR-085](docs/architecture/trustee-portal-design-2-architecture.md) (approved 2026-10-22), and SDD Amendment A-14 FR-114, FR-115, NFR-031 ([plan](docs/plans/revitalise-grant-automation-plan.md)), approved the same day.
**Gate:** `APPROVE IMPROVEMENTS`

---

## Summary

Two changes are drafted, run against the real tree and ready to apply: the `trustee_release` rows for the three columns in the special-category register, and the `--released-profile` flag on the engine's secured-column gate. Both are needed before the portal build can go green. Nothing is applied yet. Once you approve, the register edit lands at once, and the engine change still needs one commit and push from you, which are listed under *What you need to decide*.

## What has been built

1. **The three register rows are drafted, and the register's readers accept the new key** — [rev_receivesbenefits](constraints/domain/special-category-register.yml#L165), [rev_benefitprovider](constraints/domain/special-category-register.yml#L181), [rev_employmentstatus](constraints/domain/special-category-register.yml#L185).
   Each row gets a `trustee_release:` block with `basis` and `decided: "Xander Lykopoulos, 2026-10-22"`, in the shape ADR-085 gives. The register's existing lines are untouched, including the scoring carve-out on benefit status. The header gains a short note explaining the new key and naming its new reader.

2. **The TAD's worry that `domain-invariants` might reject the key does not hold. I ran it rather than read it.** [verify-domain-invariants.py](scripts/verify-domain-invariants.py#L55) is a wrapper. The [engine loader](.engine/scripts/verify-domain-invariants.py#L88) reads rows key by key and has no unknown-key check. Run against the proposed register, it exits 0, and its output differs from today's only in the register path it prints.

3. **The column-membership gate (G1), which development-agent is still writing, turns green with the proposed rows. Today it is red.** The in-flight [load_register_releases](scripts/verify-column-security-membership.py#L166) reads the new key. With today's register it fails on the test and prd settings files ("does not grant exactly the register's trustee_release columns"). With the proposed register it exits 0: "read only and equals the register's 3 trustee_release" rows. This result is provisional, because development-agent is editing that script now.

4. **The engine flag is written and tested: `--released-profile <name>` on the secured-column gate** — [secured_pairs](.engine/scripts/verify-code-app-column-bindings.py#L88), [main](.engine/scripts/verify-code-app-column-bindings.py#L194).
   It removes the named profile's (table, column) pairs from the forbidden set. It does this only when every permission in that profile is CanRead=4, CanUpdate=0 and CanCreate=0. A profile that is absent, duplicated, empty or writable fails the gate before anything is scanned. Without the flag, the output is byte-identical to today's.

5. **The instance wrapper half is already in the tree, and development-agent wrote it, not this review** — [wrapper main](scripts/verify-code-app-column-bindings.py#L82).
   The wrapper reads [config/trustee-release-profile.json](config/trustee-release-profile.json) and passes the profile name. If the pinned engine does not support the flag, it fails with a message naming this pending change. That is why the gate is red in the tree right now. Run against this draft's engine, the same wrapper passes.

## Elements changed

| File | Repository | Change |
|---|---|---|
| [special-category-register.yml](constraints/domain/special-category-register.yml#L165) | instance | 3 `trustee_release:` blocks, 2 header notes (full diff in §A) |
| [.engine/scripts/verify-code-app-column-bindings.py](.engine/scripts/verify-code-app-column-bindings.py#L194) | **engine** | `--released-profile`, `released_pairs()`, docstring (full diff in §B) |

## What is still open

**The `basis` and `decided` keys are written but not checked.** G1 counts a row as released whenever the block is present (`row.get("trustee_release")`, [L177](scripts/verify-column-security-membership.py#L177)). So `trustee_release: true` would also release a column. The header text says this plainly, and it does not claim the keys are enforced. Making G1 require both keys to be non-empty would be a one-line change in development-agent's file. I have routed it there and not drafted it here.

**The other gate edits in ADR-085 are development-agent's work and are not in this review.** These are G3 (`schema.test.ts`), G4 (the catalogue), the new Pester fixtures (a writable release profile, and a column the register does not release) and the `derived-counts` scoping. One measurement helps: the existing known-bad fixture for this gate still fails with the flag on, because it names `rev_narrativeraw`.

**Eleven unread findings are not in this review.** You scoped it to these two changes, and 11 is below the batch threshold of 45. They wait for the next batch. Three of them share a class with something the 2026-10-21 review applied, so the next batch should look at those first (§1).

**Three derived counts are already drifting, and none of the drift comes from this review.** `verify-derived-counts.py` (SOFT) reports three. This agent's own [verify-script count](agents/improvement-agent.md#L611) says 71 where the source now has 70, because `scripts/verify-code-app-variant-parity.py` is deleted in the working tree. The digest line-count sentence says 638 where the digest has 640. A dev-summary bundle size is also out of date. This review does not change any of them. The next batch, or the commit that keeps the deletion, should correct the first two.

## What you need to decide

**Approve this draft?**

**Problem** — The portal cannot show the three answers while the secured-column gate forbids them and G1 has no register rows to match the new profile against.
**Suggested fix** — Reply `APPROVE IMPROVEMENTS`. I then apply §A and §B to disk, re-run the gates and record the result.
**What happens if you don't** — G1 and the secured-column gate both stay red, and development-agent's portal build cannot pass.
[ADR-085](docs/architecture/trustee-portal-design-2-architecture.md)

---

**After approval, commit and push the engine change, then the pointer bump (in this order).**

**Problem** — The engine is a separate repository. I can edit the file, but publishing it takes a commit and a push there, and only then the pointer bump here.
**Suggested fix** — Run these commands. `.engine` is on branch `deploy-first-learning-and-item-closure`, clean, and its HEAD `97af189` is on `origin`. Do not push to `main`: moving engine work to `main` is a release decision.

```bash
git -C .engine add scripts/verify-code-app-column-bindings.py
git -C .engine commit -m "verify-code-app-column-bindings: --released-profile (read-only release profile subtraction; Revitalise TAD ADR-085 G2)"
git -C .engine branch -r --contains HEAD~1        # expect: origin/deploy-first-learning-and-item-closure
git -C .engine push origin HEAD:deploy-first-learning-and-item-closure
git -C .engine branch -r --contains HEAD          # MUST list origin/deploy-first-learning-and-item-closure
git add .engine constraints/domain/special-category-register.yml docs/improvements/2026-10-22-improvement-review.md
git commit -m "Improvement review 2026-10-22: trustee_release register rows + engine pointer bump (--released-profile)"
git push
```

Name these paths exactly. Do not use `git add -A`, because development-agent has a lot of uncommitted work in this tree. Its wrapper and `config/trustee-release-profile.json` go in its own commit, and the gate only goes green in a clone once both commits are there.
**What happens if you don't** — Your local tree works, because scripts run from the working copy. A fresh clone or CI still pins `97af189`, so the gate is red there. A pointer pushed before the engine commit breaks `git submodule update --init` for every clone.
[improvement-agent.md, two repositories](agents/improvement-agent.md#L504)

---

Verification: 2 gates run on the proposed register (domain-invariants 0, in-flight G1 0, against 1 for today's register). 15 cases run on the proposed engine: T1 to T7, P1 and P2 directly, and L2 to L4 through development-agent's wrapper, each with the expected exit code. **Not verified:** the Pester suite `src/tests/build/BuildGates.Tests.ps1` was not run, because its G2 and G1 blocks are being rewritten now. The full build was not run. No result here is above V1: nothing touched a live environment.

---

## 1. Regression check — did the last review's changes work?

The 2026-10-21 review was applied today. Since then, 11 findings have been logged (IMP-1206 to IMP-1216). This scoped review does not process them, so this check only asks whether any of them shares a class with an entry that review closed. The match was computed from `class_instance_of`, not from prose.

| Prior change (2026-10-21) | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|
| Row 12, lead-agent rungs (IMP-1168) | `concurrent-session-same-file-write` | YES, once — IMP-1207, in improvement-agent's own commands | **Prose fix, recurred.** The ladder says escalate. IMP-1207 itself proposes waiting for a second instance. Left for the next batch to decide |
| Row 5, work_items.py component refusal (IMP-1160) | `declared-policy-not-mechanically-enforced` | YES, once — IMP-1208, a different policy (tier override on a dispatch) | Different mechanism. Not evidence against row 5 |
| Rows 1 and 17 (IMP-1150, IMP-1158) | `stale-claim-contradicting-rechecked-source` | YES, once — IMP-1211, a different file (domain overview Non-Negotiable 1) | Different claim. Not evidence against either row |
| The other 14 rows | various | NO | No evidence against them yet |

**Recurred after a prose fix:** row 12, once. Deferred to the next batch, which carries the full check.
**Recurred after a gate:** none.

---

## 2. Clusters and promotion decisions

No finding is processed; the one cluster below is the capability change itself. The change comes from capability mode (a reviewer-requested change to a gate and a register), and its authority is ADR-085 rather than any `IMP-` ids.

**Why the design document is the TAD and not a new file under `docs/improvements/`.** Capability mode asks for a design document under `docs/improvements/`. I searched that directory for `released-profile`, `trustee_release` and `REV_TrusteeFinancialEligibility` and found 0 hits. ADR-085 is already approved by you and fully specifies both changes. A second design document would compete with it for authority, which this agent's rules forbid. So the TAD is cited, and this document records the measurements.

```
CLUSTER: (none — capability mode, ADR-085 G1 register rows + G2 engine flag)
Altitude:   CLASS for the engine flag (generic Code App knowledge: subtract one read-only profile);
            INSTANCE for the register rows (this client's three columns)
Ladder row: script beats constraint row beats paragraph — both changes are data or code, no new constraint
Becomes:    §A register rows; §B engine flag
Retires:    nothing
Cites:      ADR-085 (G1, G2), SDD FR-114, FR-115, NFR-031, OQ-062 (b)
Residual:   (1) trustee_release content (basis/decided) is not checked by any gate — G1 reads
            presence only; routed to development-agent. (2) The engine trusts the instance to name
            the right profile; the tie between that profile and the reviewed columns is G1's, an
            instance gate. An instance that wires the flag without a G1-equivalent gets the read-only
            check only. Stated in the engine docstring.
```

**Why this is not the `--exclude-profile` flag that review 7 retired.** That flag dropped a whole profile, and someone had to remember to pass it every time a new profile appeared. This flag subtracts only read-only grants from one named profile. A column that is secured elsewhere on another table stays forbidden by name, as T5c below shows. With no flag, nothing is permitted.

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | other | [special-category-register.yml L165–L188](constraints/domain/special-category-register.yml#L165) | 3 `trustee_release:` blocks (`basis`, `decided`), header reader line and a *third axis* note. Existing lines unchanged (§A) | ADR-085 G1; FR-114, FR-115, NFR-031, OQ-062 (b) | YES — `python3 scripts/verify-domain-invariants.py src/solutions/RevitaliseGrantAutomation --register constraints/domain/special-category-register.yml --build-config config/revitalise-grant-automation-build.yml` exits 0; in-flight G1 exits 0. Needle `SDD A-14 FR-115; NFR-031 exception, OQ-062 (b): shown as written` | N/A, data |
| 2 | script | [.engine/scripts/verify-code-app-column-bindings.py](.engine/scripts/verify-code-app-column-bindings.py#L194), **engine only** | `--released-profile <name>` and `released_pairs()`: subtract that profile's pairs only if every permission is 4/0/0; absent, duplicate, empty or writable FAILS; no flag is unchanged (§B) | ADR-085 G2 | YES — cases T1–T7, P1, P2, L2–L4 below. Not an unsplit duplicate: the instance file is a wrapper, and `verify-engine-instance-split.py` does not list it | already wired (`no-secured-columns-in-code-app`, HARD, [build config L802](config/revitalise-grant-automation-build.yml#L802)); the wrapper passes the flag |

**Constraint budget:** 0 of 3 used.

### Measurements, run 2026-10-22 against the real tree (scratch copies, nothing on disk changed)

Register: today's register has sha1 `a8b0cae…`. It was unchanged when this draft was written.

| Id | Case | Exit | What it proves |
|---|---|---|---|
| D1 | domain-invariants, today's register | 0 | baseline |
| D2 | domain-invariants, proposed register | 0 | the new key is tolerated; output differs only in the register path |
| G1a | in-flight G1, today's register | 1 | today it is red on test and prd: the profile grants 3 columns and the register releases none |
| G1b | in-flight G1, proposed register | 0 | the rows are what G1 is waiting for (provisional: script in flight) |
| T1 | engine, real app, no flag | 0 | output byte-identical to the pinned engine (`cmp`) |
| T2 | engine, real app, flag = release profile | 0 | 88 → 85 pairs, 83 → 80 forbidden names |
| T3 | flag = `REV_TrusteeRestricted` (writable) | 1 | a writable profile is refused |
| T4 | flag = a profile that does not exist | 1 | an absent profile is refused, not ignored |
| T5a | fixture app naming `rev_benefitprovider`, no flag | 1 | the column is forbidden without the release |
| T5b | same, flag | 0 | the release lets exactly that column through |
| T5c | same plus a `REV_FinanceOnly` column (`rev_accountholdername`), flag | 1 | nothing outside the release is let through |
| T6 | release profile emptied | 1 | an empty release is refused |
| T7 | release profile grants CanUpdate=4 on one column | 1 | one writable permission refuses the whole profile |
| P1 | the existing known-bad Pester fixture, flag on | 1 | the known-bad fixture stays red (`rev_narrativeraw`) |
| P2 | retired `--exclude-profile` | 2 | still an argparse refusal |
| L1 | live tree today (dev-agent wrapper + pinned engine) | 1 | red until this engine change lands, by design |
| L2 | dev-agent wrapper + proposed engine, real app | 0 | the two halves fit |
| L3 / L4 | the same, with fixtures T5b / T5c | 0 / 1 | the same verdicts through the wrapper |

The corpus here is one app and one profile file. It has 0 findings, and 0 is correct: `schema.ts` does not name the three columns yet (grep count 0). The positive control is T5b and the negative controls are T5a, T5c and P1.

---

## 4. Retirements

> Retirement check performed: the two constraint rows these changes sit under were reviewed.
> C-TECH-069 governs how this gate reads the solution, and its rule (read every profile as a
> collection, key by table and column) still holds. The flag keeps both. No register row is
> made redundant, because every row stays `secured: required`. Nothing is retired.

---

## 5. Findings left unprocessed

**Deferred:** IMP-1206, IMP-1207, IMP-1208, IMP-1209, IMP-1210, IMP-1211, IMP-1212, IMP-1213, IMP-1214, IMP-1215, IMP-1216

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| IMP-1206 to IMP-1216 | various (see §1) | the reviewer scoped this review to two changes; 11 is below the batch threshold (45) | the next post-deploy batch, or the threshold |
| IMP-1215 | `doc-contradicts-reality` | adjacent to this change: it asks for `knowledge/technology/dataverse.md` point 1 to be reworded once ADR-084 and ADR-085 are built. It is a knowledge edit with its own premise to grep, so it is not folded in | the next batch, after G1 to G4 land |

The 3 fixed-in-flight blockers (IMP-1095, IMP-1098, IMP-1156) are reviewer-deferred. Each waits on a designer re-open, and this review does not touch them.

---

## 6. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 1212 | 1212 |
| Distinct lessons | 1189 | 1189 |
| Digest | current (`--check`) | unchanged — no entry moves |

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-10-22-improvement-review.md

Findings processed: 0 NEW  →  1 cluster (capability mode, reviewer request, ADR-085)
Regression check:   17 prior changes audited, 1 class recurred after a prose fix (deferred to next batch)
Proposed:           0 constraints (cap 3), 1 gates/scripts, 0 skill/knowledge edits,
                    0 agent-file edits, 0 retirements  (+1 other: 3 register rows)
Altitude calls:     1 generalised from instance to class (engine flag), 0 left as notes
Digest:             will not change — 1189 lessons; no log entry moves

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. On approval

The applied record is written here **after** `APPROVE IMPROVEMENTS`, not before.

**Apply order:** (1) Re-read this file's `Status` line, and write `APPLYING <time>`. (2) Re-check that the register's three target rows match the context lines in §A. Re-check that the engine file's sha1 is still `0b8375d…`; if it has moved, merge rather than overwrite. (3) Apply §A, then run D2 and G1 on the real file. (4) Apply §B, then run T1, T2 and the live wrapper on the real tree. (5) Run `python3 scripts/verify-derived-counts.py` and `python3 scripts/verify-review-document.py` on this file. (6) Hand the commit commands above to the reviewer.

---

### Applied record — 2026-10-22

**Approval:** *"Approve improvements"*, typed by Xander Lykopoulos in reply to lead-agent's relay of this gate, relayed verbatim to this agent on 2026-10-22.

**Re-verified before applying:** this file's Status line was still DRAFT. Neither target file had changed since the draft: the register was still `a8b0cae…` and the engine file still `0b8375d…`. `verify-improvement-log.py --check` showed no new entries and no `corrects` warnings. Nothing was withheld or narrowed.

| # | Change | Applied at | Entries moved to APPLIED |
|---|---|---|---|
| 1 | §A, register: 3 `trustee_release:` blocks and 2 header notes. Matches the approved diff line for line (sha1 now `2122ff7…`) | working tree 2026-10-22 12:57; instance commit by the reviewer | none, because no finding was processed |
| 2 | §B, engine `--released-profile`. Matches the approved diff line for line (sha1 now `7ecb41c…`) | `.engine` working tree 2026-10-22 12:57; **not committed**. Engine commit, push and pointer bump by the reviewer | none |

**Post-apply gates on the real tree. All are provisional, because development-agent is live in this tree.**

| Gate | Command | Exit | Note |
|---|---|---|---|
| `domain-invariants` | the build step's command | 0 | the register with the new key is accepted |
| `no-trustee-in-column-security-profile` (G1) | the build step's command, which now carries `--profiles` and `--register` | 0 | "read only and equals the register's 3 trustee_release" rows. It was 1 against the pre-apply register |
| `no-secured-columns-in-code-app` (G2) | the build step's command (development-agent's wrapper and the applied engine) | 0 | 3 pairs subtracted, 80 forbidden names. `schema.ts`, `repository.ts` and `types.ts` now name the three columns |
| G2, engine with no flag | the engine called directly | 1 | 10 findings, all on the three columns, the same count as the pinned engine at git HEAD. Only the message wording changed, as §B approved |
| G2, leak control | fixture naming `rev_benefitprovider` plus `rev_accountholdername`, flag on | 1 | the `REV_FinanceOnly` column is still caught |
| `engine-instance-split` | `python3 scripts/verify-engine-instance-split.py` | 0 | |
| `derived-counts` (SOFT) | `python3 scripts/verify-derived-counts.py` | WARN | the same 3 drifts as at draft time. None comes from this review (see *What is still open*) |
| digest | `generate-known-failure-modes.py --check` | current | no log entry moved, so no regeneration was needed |

**Evidence needle for row 1:** `SDD A-14 FR-115; NFR-031 exception, OQ-062 (b): shown as written` appears once in the register.

**Not run:** the Pester suite and the full build. Nothing here is above V1.

## §A — register diff (proposed)

```diff
--- a/constraints/domain/special-category-register.yml
+++ b/constraints/domain/special-category-register.yml
@@ -10,6 +10,7 @@
 #   * scripts/verify-domain-invariants.py    — C-DOM-030 / C-DOM-031 / C-DOM-032
 #   * the `no-special-category-data-in-scoring` gate in config/<slug>-build.yml,
 #     whose grep alternation must match this file exactly (the script asserts it)
+#   * scripts/verify-column-security-membership.py — the `trustee_release:` rows (G1, ADR-085)
 #
 # ── WHY A FILE AND NOT A PARAGRAPH ───────────────────────────────────────────
 # This list previously existed only as a regex alternation inside a shell one-liner
@@ -113,6 +114,23 @@
 #
 # Every row without a `gate_exception:` is barred from the automated score regardless of its
 # `secured` value. That remains the default and the overwhelmingly common case.
+#
+# ── A THIRD AXIS: `trustee_release:` (ADDED 2026-10-22, portal TAD ADR-085, SDD A-14) ─────
+#   axis 3 — may a TRUSTEE read this column's value?               → `trustee_release:`
+#
+# A row carrying it stays `secured: required` and stays barred from the score; the block says
+# only that the reviewer released the value to trustees, read only, through the one profile
+# config/trustee-release-profile.json names. Write both keys. No gate reads their content today:
+# `no-trustee-in-column-security-profile` reads only whether the block is present.
+#
+#   trustee_release:
+#     basis:   the SDD requirement that releases it
+#     decided: who decided, and when
+#
+# The release profile must grant EXACTLY the rows that carry this block, read only —
+# `no-trustee-in-column-security-profile` fails otherwise. So widening what trustees read takes
+# two keys: the profile's permissions and a row here, which only the reviewer or
+# improvement-agent can write.
 columns:
 
   # ── Free-text health / disability narrative ────────────────────────────────
@@ -178,14 +196,23 @@
         Derive_income_flag ONLY. The column must not reach scoring output or the score
         calculation itself, and must appear in no other action of the scoring flow.
       gate: receivesbenefits-scoped-to-income-flag
+    trustee_release:
+      basis: "SDD A-14 FR-114; NFR-031: released to trustees as a value (NFR-001 amended)"
+      decided: "Xander Lykopoulos, 2026-10-22"
   - name: rev_benefitprovider
     entity: rev_application
     basis: "SDD §7.1 — benefit provider, same tier as benefit status"
     secured: required
+    trustee_release:
+      basis: "SDD A-14 FR-115; NFR-031 exception, OQ-062 (b): shown as written"
+      decided: "Xander Lykopoulos, 2026-10-22"
   - name: rev_employmentstatus
     entity: rev_application
     basis: "Art. 9 by TAD §3.1/§3.3 classification"
     secured: required
+    trustee_release:
+      basis: "SDD A-14 FR-114; NFR-031: released to trustees as a value (NFR-001 amended)"
+      decided: "Xander Lykopoulos, 2026-10-22"
 
   # ── Racial or ethnic origin ────────────────────────────────────────────────
   # ADDED 2026-09-04 by improvement review (IMP-0598, blocker). This column had been live and
```

## §B — engine diff (proposed; `.engine` repository)

```diff
--- a/.engine/scripts/verify-code-app-column-bindings.py
+++ b/.engine/scripts/verify-code-app-column-bindings.py
@@ -53,15 +53,31 @@
 
 Run:
     python3 verify-code-app-column-bindings.py <app-root> <path/to/FieldSecurityProfiles.xml> \
-        [--require-columns <path-to-json>]
+        [--require-columns <path-to-json>] [--released-profile <profile-name>]
 
 `--require-columns` is optional: a JSON file `[["<column>", "<why>"], ...]` naming columns the
 app must reference in authored source to prove it implements some fail-closed rule (a
 conjunction of flags, a scoping column). This is the one genuinely app-specific fact — an
 instance supplies its own; without it, only the forbidden-column check runs.
 
-Exits 0 when the app references no secured column and (if given) every required column is
-present, 1 otherwise.
+`--released-profile` is optional and names ONE field security profile whose columns the app may
+select, because every persona the app is shared with is a member of it. The (table, column)
+pairs that profile grants are removed from the forbidden derivation, and nothing else changes.
+It is accepted only when the profile is READ-ONLY: present in the file, with at least one
+FieldPermission, and every FieldPermission carrying CanRead=4, CanUpdate=0 and CanCreate=0. A
+named profile that is absent, empty, or grants update or create FAILS the gate rather than
+being ignored. Without the flag the gate behaves exactly as before.
+
+Why this is not the `--exclude-profile` deny-list removed on 2026-08-23. That flag dropped a
+whole profile from consideration and needed a human to decide, for every new profile, whether
+to pass it; forgetting was unsafe. This flag subtracts only the read-only grants of the one
+profile named, a column secured in ANY other profile on another table stays forbidden by name,
+and with no flag nothing is permitted. Forgetting it fails the build; it never opens a gap.
+Which profile may be named is an instance decision, and the instance should tie it to a
+reviewed record of the released columns (first use: Revitalise TAD ADR-085, 2026-10-22).
+
+Exits 0 when the app references no secured column outside the released profile and (if given)
+every required column is present, 1 otherwise.
 """
 
 from __future__ import annotations
@@ -105,6 +121,48 @@
     return pairs, profiles
 
 
+def released_pairs(profile_path: str, name: str) -> tuple[set[tuple[str, str]], list[str]]:
+    """The (entity, column) pairs one READ-ONLY profile grants, and every reason it is refused.
+
+    Returns (pairs, errors). Any error means the caller must FAIL: a released profile that
+    cannot be shown to be read-only is never subtracted, because subtracting it would let the
+    app select a column some persona may also write through it.
+    """
+    tree = ET.parse(profile_path)
+    matches = [p for p in tree.getroot().iter("FieldSecurityProfile") if p.get("name") == name]
+    if not matches:
+        return set(), [f"--released-profile '{name}' is not a FieldSecurityProfile in "
+                       f"{profile_path}. A release that names nothing releases nothing, and "
+                       "is a configuration error, not a no-op."]
+    if len(matches) > 1:
+        return set(), [f"--released-profile '{name}' is declared {len(matches)} times in "
+                       f"{profile_path}; it must name exactly one profile."]
+    pairs: set[tuple[str, str]] = set()
+    errors: list[str] = []
+    permissions = list(matches[0].iter("FieldPermission"))
+    if not permissions:
+        errors.append(f"--released-profile '{name}' declares no FieldPermission. An empty "
+                      "release is a configuration error, not a no-op.")
+    for permission in permissions:
+        entity = (permission.findtext("EntityName") or "").strip()
+        column = (permission.findtext("AttributeName") or "").strip()
+        rights = {key: (permission.findtext(key) or "").strip()
+                  for key in ("CanRead", "CanUpdate", "CanCreate")}
+        if not entity or not column:
+            errors.append(f"--released-profile '{name}' has a FieldPermission with no "
+                          "EntityName or AttributeName.")
+            continue
+        if rights != {"CanRead": "4", "CanUpdate": "0", "CanCreate": "0"}:
+            errors.append(f"--released-profile '{name}' grants {entity}.{column} with "
+                          f"CanRead={rights['CanRead'] or '?'}, "
+                          f"CanUpdate={rights['CanUpdate'] or '?'}, "
+                          f"CanCreate={rights['CanCreate'] or '?'}. A released profile must "
+                          "be read-only on every column (CanRead=4, CanUpdate=0, CanCreate=0).")
+            continue
+        pairs.add((entity, column))
+    return pairs, errors
+
+
 def solution_entities(entities_root: str) -> set[str]:
     """Every entity logical name the solution declares, from the directory names on disk."""
     if not os.path.isdir(entities_root):
@@ -200,6 +258,9 @@
     parser.add_argument("--generated-dir", action="append", default=None,
                         help="a path prefix to exclude from the forbidden-column scan "
                              "(repeatable; default: src/generated, .power)")
+    parser.add_argument("--released-profile", default=None,
+                        help="one READ-ONLY field security profile whose granted columns the "
+                             "app may select (see the module docstring)")
     args = parser.parse_args(argv[1:])
 
     app_root = args.app_root.rstrip("/")
@@ -238,6 +299,23 @@
               "anything. That is a broken gate, not a clean app.", file=sys.stderr)
         return 1
 
+    released: set[tuple[str, str]] = set()
+    if args.released_profile is not None:
+        released, release_errors = released_pairs(profile_path, args.released_profile)
+        if release_errors:
+            for error in release_errors:
+                print(f"ERROR: {error}", file=sys.stderr)
+            print(f"\nno-secured-columns-in-code-app: FAILED — the released profile "
+                  f"'{args.released_profile}' was refused, so nothing was subtracted and the "
+                  "gate did not scan.", file=sys.stderr)
+            return 1
+        pairs = pairs - released
+        if not pairs:
+            print(f"no-secured-columns-in-code-app: FAILED — every secured pair in "
+                  f"{profile_path} is granted by '{args.released_profile}', so the forbidden "
+                  "set is empty. That is a broken gate, not a clean app.", file=sys.stderr)
+            return 1
+
     files = scan(app_root)
     if not files:
         print(f"no-secured-columns-in-code-app: FAILED — no source files ({', '.join(sorted(SOURCE_EXT))}) "
@@ -274,8 +352,8 @@
                 line = text.count("\n", 0, match.start()) + 1
                 errors.append(
                     f"{rel}:{line}: references '{column}', which column security hides. "
-                    "This app must never name a secured column — the same code may run for a "
-                    "role for whom the column IS populated.")
+                    "This app must never name a secured column outside the released profile — "
+                    "the same code may run for a role for whom the column IS populated.")
                 break  # one report per column per file is enough to act on
 
     for column, why in required_columns:
@@ -296,11 +374,16 @@
 
     required_note = (f" All {len(required_columns)} required column(s) are present."
                       if required_columns else "")
+    released_note = (f" {len(released)} (table, column) pair(s) released read-only by "
+                     f"'{args.released_profile}' were subtracted first: "
+                     f"{', '.join(f'{e}.{c}' for e, c in sorted(released))}."
+                     if args.released_profile is not None else "")
     print(f"no-secured-columns-in-code-app: OK — {len(authored)} authored file(s) reference none "
           f"of the {len(forbidden)} forbidden column(s), derived from {len(pairs)} secured "
           f"(table, column) pair(s) across {', '.join(profiles)} and scoped to the "
           f"{len(mine)} table(s) this app names ({', '.join(sorted(mine))}); "
-          f"{len(safe)} column(s) of those tables are unsecured and therefore safe.{required_note}")
+          f"{len(safe)} column(s) of those tables are unsecured and therefore safe."
+          f"{released_note}{required_note}")
     return 0
 
 
```
