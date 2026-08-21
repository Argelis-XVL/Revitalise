# Improvement Review 7 — 2026-08-21

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 2 `NEW` (both `blocker`) → 1 cluster
**Trigger:** blocker escalation, plus an explicit reviewer instruction to fix both for real in one narrow pass
**Gate:** standing `APPROVE IMPROVEMENTS`

Both blockers were the same defect wearing two names: **a gate that exists, is correct, and is not
named by any `steps:` block**, so it cannot fire. Two lines in
[config/revitalise-grant-automation-build.yml](../../config/revitalise-grant-automation-build.yml#L121)
and [#L242](../../config/revitalise-grant-automation-build.yml#L242) close both. Everything else in
this review is making the two gates go green **honestly** — with owned, dated declarations — rather
than by relaxing them.

---

## 1. Regression check — did the last review's changes work?

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| [verify-tad-coverage.py](../../scripts/verify-tad-coverage.py) + `C-TECH-066` + [tad-deferrals.json](../../contract/tad-deferrals.json) (review 6, item 4) | 2026-08-20 | `declared-policy-not-mechanically-enforced` | **YES — this review's first finding** | **The gate never ran.** Script correct, constraint correct, deferral file correct, and no config named the script. Review 6's APPLIED cell said "wired as a build gate"; nothing checked that sentence against the file it described |
| [verify-pipeline-config.py](../../scripts/verify-pipeline-config.py) check 11 — settings files are opened, not merely resolved (review 4) | 2026-08-20 | `config-placeholder-known-but-not-fixed` | **YES — this review's second finding** | **The gate ran only by hand.** It was wired into [ci.yml → validate](../../.github/workflows/ci.yml#L391) alone, and CI had never fired on a matching branch until earlier the same day, so 18 unowned placeholders survived in the two files it was built to catch |
| [ci.yml](../../.github/workflows/ci.yml#L250) trigger widened (review 6, item 2) | 2026-08-21 | `declared-policy-not-mechanically-enforced` | Contributed to the above | Working, and it exposed the next layer: CI firing is necessary, not sufficient, when the build itself never calls the gate |
| [known-exceptions.json](../../contract/known-exceptions.json#L2) widened to non-commercial gates (review 6, item 12) | **NOT APPLIED** | `config-placeholder-known-but-not-fixed` | — | **Superseded, not carried.** The settings files already have the right mechanism: each one's own `_unresolved` block takes an owner, a reason and an expiry and fails on an expired entry. Nothing needed widening |

**Recurrence after a *gate* fix, twice.** The improvement-agent activation checklist says a gate that
exists and did not fire is "either mis-scoped or not wired into the config". Both were the second
thing. That is what this review fixes, and it is why every change below is a line in an executable
file rather than a sentence in a document.

---

## 2. Cluster and promotion decision

```
CLUSTER: gate-exists-but-is-not-wired-into-any-executable-config  (x2: both blockers)
            surfacing as declared-policy-not-mechanically-enforced (x3)
            and config-placeholder-known-but-not-fixed (x3)
Altitude:   CLASS — the third instance of each class, so an instance patch is forbidden
Ladder row: "a gate whose absence a review claimed to have closed" → make the claim greppable
Becomes:    (a) two steps added to the build config, so both gates run in every build;
            (b) both constraints' Verify By now NAME the step, and instruct the reader to grep
                the steps: block instead of trusting a review's APPLIED cell;
            (c) each finding's log entry carries an evidence_grep against the build config, so
                deleting either step FAILS python3 scripts/verify-improvement-log.py --check
Retires:    nothing
Residual:   this makes the two claims self-checking; it does NOT make every future
            "wired as a build gate" claim self-checking. A generalisation — requiring an
            evidence_grep on any APPLIED entry whose applied_by mentions a build gate — is
            named in §5 and deliberately deferred out of this narrow pass
```

---

## 3. Changes applied

| # | Type | Target | Change | Verified by |
|---|---|---|---|---|
| 1 | build-gate | [build.yml#L242](../../config/revitalise-grant-automation-build.yml#L242) | `tad-coverage` step, beside `component-shape` — both compare authored source against a specification the packer knows nothing about | `python3 scripts/verify-build-config.py …` → PASS, 35 steps / 24 gates |
| 2 | build-gate | [build.yml#L121](../../config/revitalise-grant-automation-build.yml#L121) | `pipeline-config-preflight` step, right after the build preflight — the build now checks what it hands off to | same preflight; the step's ability to fail is registered at [BuildGates.Tests.ps1#L711](../../src/tests/build/BuildGates.Tests.ps1#L711) |
| 3 | config | [tad-deferrals.json#L54](../../contract/tad-deferrals.json#L54)–[#L108](../../contract/tad-deferrals.json#L108) | `TD-005`–`TD-009`: the ten absent columns on tables that exist, each owned, dated and pointing at the decision that must land before any schema work | `python3 scripts/verify-tad-coverage.py` → exit 0, 129 specs, 39 deferred |
| 4 | config | [tad-deferrals.json#L109](../../contract/tad-deferrals.json#L109) | `_not_deferred` rewritten from "ten columns left un-deferred on purpose" to "NONE — and here is the decision that changed it" | read-back; the file no longer contradicts its own `deferrals` array |
| 5 | config | [test-settings.json#L159](../../provisioning/deploymentSettings/test-settings.json#L159), [prd-settings.json#L191](../../provisioning/deploymentSettings/prd-settings.json#L191) | The GitHub OIDC subject resolved for real — `repo:Argelis-XVL/Revitalise:environment:<env>`, read from `git remote -v` | `python3 scripts/verify-pipeline-config.py config/revitalise-grant-automation-pipeline.yml` → PASS |
| 6 | config | [test-settings.json#L49](../../provisioning/deploymentSettings/test-settings.json#L49), [prd-settings.json#L48](../../provisioning/deploymentSettings/prd-settings.json#L48) | Seven Entra ids per file declared in `_unresolved` with an owner, the exact read-only Graph query, and a 2026-09-18 expiry | same gate: 20 ACCEPTED lines printed, 0 errors |
| 7 | constraint text | [technology-constraints.md#L136](../../constraints/technology/technology-constraints.md#L136) | `C-TECH-066`'s Verify By names the `tad-coverage` step and says to grep the `steps:` block, never a review's APPLIED cell | the sentence is now falsifiable by one grep |
| 8 | constraint text | [technology-constraints.md#L132](../../constraints/technology/technology-constraints.md#L132) | `C-TECH-062`'s Verify By adds the `pipeline-config-preflight` step, with why CI alone was not enough | same |
| 9 | test | [BuildGates.Tests.ps1#L730](../../src/tests/build/BuildGates.Tests.ps1#L730) | The real-config assertion inverted: was "fails with exactly 2 errors", now "passes, and every exception is still reported" | 14 of 14 tests in that block pass |
| 10 | correction | [review 6, item 4](2026-08-21-improvement-review-6.md#L561) | Dated correction: the APPLIED claim was half true — script yes, wiring no | the next reader inherits the correction, not the claim |

**Constraint budget: 0 of 3 used.** No new constraint. Two existing rows had their `Verify By`
sharpened, which is the opposite of growth: each went from a sentence that could be believed to a
sentence that can be checked.

### What the ten deferred columns are, and why none was built

Building them would be schema work with no resolved WBS task, which is a change-order decision
first ([C-COM-002](../../constraints/commercial/commercial-constraints.md#L35)) — so each deferral names
the decision instead of inventing the column.

- **[TD-005](../../contract/tad-deferrals.json#L54) — the applicant's ethnic group.** The
  architecture names it conditionally, on an open question about whether the charity captures it at
  all. Building it would create special-category data nobody has agreed to hold. Short date.
- **[TD-006](../../contract/tad-deferrals.json#L65) — a scoring input called `rev_financialanswers`.**
  Source holds the eleven other inputs the same architecture line names. Whether a twelfth column is
  needed, or the line is stale, is an architecture ruling on an automation that is already live.
  Short date.
- **[TD-007](../../contract/tad-deferrals.json#L76) — the five duplicate-grant columns.** No accepted
  task writes them: the intake tasks do no QuickBooks lookup, and the payment-side task flags the
  Payment row, not the Application. This is the one deferral with hours attached. Short date.
- **[TD-008](../../contract/tad-deferrals.json#L87) — the two redaction columns.** These are
  contracted (tasks 5.3 / 5.4, not started) and the same absence is already owned and dated as
  `EX-003`. Date **inherited** from it, deliberately, so two mechanisms cannot hold two deadlines for
  one absence.
- **[TD-009](../../contract/tad-deferrals.json#L98) — the grant's provider lookup.** It points at a
  table that does not exist in source; `TD-001` already defers that table. Date inherited.

Three short dates (2026-09-18) and two inherited (2026-11-27). The short ones are questions and a
commercial decision — things that need four weeks and a conversation, not a phase.

### What could be ground-truthed in the settings files, and what could not

**Resolved:** the GitHub organisation and repository, from `git remote -v` →
`https://github.com/Argelis-XVL/Revitalise.git`. The environment segment of each subject
(`tst_acc`, `prd`) matches the GitHub Environment names [ci.yml](../../.github/workflows/ci.yml#L99)
declares.

**Not resolved, and declared instead:** four Microsoft permission ids and two Entra group object ids
per file. Every one is a single read-only Graph call away, and this machine has no way to make it —
no Graph session, no `az` CLI, and the provisioning app id and certificate thumbprint are both
unset. The commonly published GUIDs were **not** pasted from memory: an incorrect permission id
requests a permission nobody reviewed, and a wrong group object id binds security roles to the wrong
people. Each declaration carries the exact query that resolves it, so the owner has a runnable
action rather than a chore.

One live read-only query did run, and it matters for the dates: `pac admin list` confirms
**REV-GrantApplications-ACC and -PRD already exist**. These are lookups against real environments,
not placeholders for future work, which is why they carry a four-week expiry rather than the
phase date the not-yet-created trustee group carries.

---

## 4. Retirements

> Retirement check performed: the two constraints touched here (`C-TECH-062`, `C-TECH-066`) were
> reviewed for redundancy and neither is redundant — each is now the only mechanical check over its
> own surface, and both fired real findings this session. No other constraint was examined, because
> this was a two-finding pass and a retirement argument needs the coverage proof that a full review
> assembles. Named as a deliberate omission rather than a clean record.

---

## 5. Findings left unprocessed

No silent caps.

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| The generalisation this cluster earned | `declared-policy-not-mechanically-enforced` | Requiring an `evidence_grep` on every APPLIED entry whose `applied_by` claims a build-gate wiring would close the class rather than these two instances. It is a change to [verify-improvement-log.py](../../scripts/verify-improvement-log.py) and was out of scope for an explicitly narrow pass | the next full improvement review |
| 8 other `NEW` entries | various | The reviewer scoped this pass to the two blockers. Seven of the eight already carry a recorded deferral reason and are accepted as reviewed deferrals; one is unread | the next full improvement review |

The two blockers that remain `NEW` in the log are both recorded as reviewed deferrals with reasons,
so the blocker trigger is satisfied — it fires on unread blockers, and after this review there are
none.

---

## 6. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 172 | 172 |
| Distinct lessons | 172 | 172 |
| Recurring classes (x≥2) | 23 | 23 |
| Digest lines | 433 | 433 |

Unchanged, and that is correct: this review added no findings and removed none. Both lessons were
already in [known-failure-modes.md](../../logs/known-failure-modes.md); what changed is that both are
now enforced by something that runs. Regenerated and confirmed current with
`python3 scripts/generate-known-failure-modes.py --check`.

---

## 7. Verification

| Command | Result |
|---|---|
| `python3 scripts/verify-build-config.py config/revitalise-grant-automation-build.yml` | **PASS** — 35 steps, 24 gates; also PASS under `--context ci` |
| `python3 scripts/verify-tad-coverage.py` | **exit 0** — 129 column specs, 10 table blocks, 39 deferred, 15 trustee-visible reachable |
| `python3 scripts/verify-pipeline-config.py config/revitalise-grant-automation-pipeline.yml` | **exit 0** — 78 steps, 3 environments, 20 declared exceptions all printed |
| `python3 scripts/verify-improvement-log.py --check` | **exit 0** |
| Pester — `BuildGates.Tests.ps1` + `VerifyBuildConfig.Tests.ps1` | 109 tests, 0 failures |
| Pester — `DeploymentSettings.Tests.ps1` | 37 passed, 1 skipped |

**Not verified.** No build was run — `pac solution pack`, the solution checker and the code-app
toolchain steps were untouched and unexecuted, so the two new steps are proven correct as
*configuration* (the preflight parses, orders and negative-tests them) and not yet observed inside a
complete build. The full 780-test suite and the coverage gate were not run either; the three test
files touching the changed files were.

---

## 8. Applied

| # | Change | Entries moved to APPLIED |
|---|---|---|
| 1–10 | All of §3 | IMP-0174, IMP-0175 |

Nothing rejected.
