# Improvement Review — 2026-08-19 (third review of the day)

**Gate:** `APPROVE IMPROVEMENTS` given by the reviewer, together with `APPROVE TENANT`, after
build #8 and Test Report revision 8 returned **FAIL** on a P1.
**Findings processed:** 8 `NEW` → 5 clusters. 4 applied, 4 deferred with named owners.
**WBS:** `system` — this review changes the development system, not the product. Out of
contractual scope, non-billable (`C-COM-002`).

## Summary

One blocker drove this review: **DEV held special-category health data with no audit trail for
five days**, while four revisions of the Test Report recorded the audit constraints as PASS. The
cause was not a missed step — it was a step that **could never run**, and no gate could see that.

The durable fix is a new preflight check that fails a provisioning step whose `-Env` cannot
resolve a settings file, plus one new HARD constraint requiring live verification of state that
solution source cannot express. The environment itself is still only half-fixed, and that part is
the reviewer's and development-agent's.

## Clusters and decisions

```
CLUSTER: exit-zero-does-not-mean-created  (x2 NEW: IMP-0019, IMP-0082 — class now x7)
Altitude:  CLASS. Both are one property: the environment carries state solution source cannot
           express, in both directions — import cannot SET the audit switches, and import does
           not REMOVE option values source omits. A source-side check proves nothing either way.
Ladder row: "a tool could catch it mechanically" + "second instance → generalise"
Becomes:   scripts/verify-pipeline-config.py check 10 (settings-file resolution) +
           constraints/technology/technology-constraints.md C-TECH-064 (new, HARD) +
           constraints/domain/domain-constraints.md C-DOM-032 Verify By amended +
           config/revitalise-grant-automation-pipeline.yml — 4 dead dev steps made honest
Retires:   nothing. No gate existed for this class; it was undefended.
Cites:     IMP-0019, IMP-0082, IMP-0084
Residual:  THREE things. (1) The known-bad fixture and negative test that C-TECH-057 requires
           for check 10 live under src/tests/, outside this agent's edit scope — specified for
           development-agent below. Coverage was proven by running the check against the
           pre-fix config (4 named errors, exit 1) but that proof is not yet permanent.
           (2) C-TECH-064 declares what the verification step must READ; the step itself is
           PowerShell under provisioning/, so the constraint currently has no executable
           implementation and is enforced by review until development-agent writes one.
           (3) The DEV environment is still wrong — see "What is not fixed".

CLUSTER: harness-blocks-destructive-call  (x3: IMP-0021, IMP-0040, IMP-0084)
Altitude:  CLASS — third instance, so the altitude rule forbids another one-off note.
Ladder row: "an agent had the information and still did the wrong thing"
Becomes:   agents/pipeline-agent.md → "Reviewer-Executed Operations", with a REVIEWER ACTION
           REQUIRED output block carrying the exact operation and the query that verifies it.
Retires:   nothing.
Cites:     IMP-0084 (and the two prior instances it generalises)
Residual:  The boundary is discovered by attempting the write, not predicted. Nothing lists
           which calls the harness will refuse, so the first attempt is still the probe.

CLUSTER: live-verification-capability  (x1: IMP-0083)
Altitude:  KNOWLEDGE — one instance, cause is general, a human needs to know it.
Ladder row: "a capability was established and could be lost again"
Becomes:   knowledge/technology/testing-tools.md → "Verifying live Dataverse state"
Retires:   nothing.
Cites:     IMP-0083
Residual:  Three traps are documented because each cost a cycle this session; a fourth will
           cost another. Nothing tests the documented commands still work.

CLUSTER: test-coupled-to-absolute-counts  (x2: IMP-0005, IMP-0039)
Altitude:  CLASS, and the decision it was waiting for is now made — source-derived counts.
Ladder row: "second instance → generalise"
Becomes:   NOTHING THIS REVIEW. src/tests/ is development-agent's, not this agent's.
Deferred to: development-agent, specified below.
Cites:     IMP-0005, IMP-0039

CLUSTER: build-config has no execution context  (x2: IMP-0041, IMP-0077)
Altitude:  CLASS. Two symptoms of one gap: a CI-only STEP (`auth`) is deferred indefinitely and
           a CI-only TOOL (`yq`) is invisible to the tooling check.
Becomes:   NOTHING THIS REVIEW — deliberately. The change makes a HARD preflight FAIL on this
           Mac until `brew install yq`, which blocks every local build. Reviewer's call.
Cites:     IMP-0041, IMP-0077
```

## Regression check

| Prior change | Class it addressed | Recurred since? |
|---|---|---|
| `scripts/verify-build-config.py` + negative tests | `gate-cannot-fail` | **No new instance in the build config.** Build #8's preflight passed 23 steps / 18 gates. But the *pipeline* preflight had a hole of exactly this shape — a step that passes every check and still cannot run — which is what check 10 closes. A gate that was generalised for one config and not the other |
| `scripts/verify-field-length-limits.py` (`C-TECH-060`) | `platform-field-length-limit-unenforced` | No. 129 flow descriptions and 126 settings values checked clean against schema-declared limits |
| `scripts/verify-shipped-content.py` | `no-assertion-on-shipped-content` | No. It is what proved the Grant navigation gap was fixed in source |
| `scripts/generate-known-failure-modes.py` read path | `learning-substrate-destroyed` | No, and it worked: build-agent's step 0 read is why build #8 read the checker result from stdout instead of trusting `--outputDirectory` |
| `scripts/verify-improvement-log.py` (`C-TECH-061`) | `learning-loop-triggers-unenforced` | **It fired, correctly, twice this session** — once on a duplicate id and once on an unprocessed blocker. Working as designed |

**One recurrence worth naming.** `repo-path-contains-spaces` recurred a third time
(`IMP-0079`): `pac solution check --outputDirectory` again wrote an empty directory while
reporting success. That was a *knowledge* fix originally, and a third instance after a knowledge
fix is evidence the altitude was too low. It is not promoted here because the proposed change is
one line in `config/<slug>-build.yml` (tee stdout, assert non-empty) and belongs with the
`when:`-context change to that same file — deferred together, not forgotten.

## Retirement considered

**No retirement this review.** Checked all 45 technology and 15 domain rows. C-TECH-049 and
seven others were retired on 2026-08-18/19 and the table now carries eight rows. The nearest
candidate is `C-DOM-032`, which on its own asserts something that does nothing — but it is not
retired, it is **narrowed**: its `Verify By` now states plainly that it is a source check and
names `C-TECH-064` as the live half. Retiring it would lose the source-side assertion, which is
still worth having.

## What is not fixed

**DEV still has no working audit trail.** The reviewer enabled organisation auditing by hand
during this session — verified live, `isauditenabled=True`. Two things remain, and a session
cannot do either:

- `auditretentionperiodv2` is **empty** against the 2192 days (6 years) that
  `test-settings.json` and `prd-settings.json` both declare, reviewed with the DPO per that
  file's own comment. Not "forever" — that is a storage-limitation defect under UK GDPR
  Art. 5(1)(e).
- `IsAuditEnabled=False` on **all five tables**: `rev_applicant`, `rev_application`, `rev_grant`,
  `rev_setting`, `rev_errorlog`. Every one reports `CanBeChanged=True`, and the column-level
  flags are already on (15/16, 89/91, 14/15, 4/5, 7/8 — the odd one out in each is the primary
  key, plus the calculated `rev_costs`), so the table switch is the only thing standing between
  here and a complete audit trail.

## Handoff to development-agent

Three changes are needed in directories this agent may not edit. Each is specified, not merely
named:

1. **`provisioning/dataverse/ensure-auditing.ps1`** — give it the dedicated-file + `-SettingsPath`
   treatment that `ensure-schema.ps1` and `seed-settings.ps1` already have, so `-Env dev` works
   without `dev-settings.json` existing. This is the **third** script needing that pattern, so per
   the altitude rule do not hand-roll it a third time: lift the resolution into
   `provisioning/common/provisioning-common.ps1` as one new function and have all three call it.
   `Get-ProvisioningSettings`'s own semantics must not change —
   `ProvisioningCommon.Tests.ps1` asserts that `-Env dev` throws, and two other scripts rely on
   it. Add the `auditing` block (org switch, 2192 days, and `auditedTables` **derived from the
   `Entities/` folders**, not hand-listed — the list in `test-settings.json` names four tables and
   omits `rev_grant`).
2. **A live-verification script** implementing `C-TECH-064`, wired into each environment's
   `verification:` block. Without it the constraint has no executable check.
3. **`src/tests/`** — replace absolute-count assertions with counts derived from the solution
   source (`IMP-0005`, `IMP-0039`), and add the known-bad fixture plus negative test for
   `verify-pipeline-config.py` check 10 that `C-TECH-057` requires.

## Decisions the reviewer still owns

**Build-step execution context** (`IMP-0041`, `IMP-0077`) — add `when: ci|local|always` and a
`required_tools` block to the build config? It converts two indefinite deferrals into a declared,
checkable boundary, and it makes the preflight fail locally until `brew install yq`.

**Read auditing** — `isreadauditenabled` and `isuseraccessauditenabled` are both `False`. Not
required by `C-DOM-010`, which is about create/update/delete, but "who saw this, and when" is the
stated rationale behind `C-DOM-032`, and answering it needs access logging on.

---

## Addendum — the deferred build-context cluster was applied after all

The reviewer answered the open decision immediately (*"Install the yq for the preflight"*), which
removed the only reason `IMP-0041` and `IMP-0077` were held back. Both are now `APPLIED`, so this
review closed **6 of 8** findings rather than 4.

```
CLUSTER: build-config has no execution context  (x2: IMP-0041, IMP-0077)
Altitude:  CLASS — fourth instance of two-invocation-paths-disagree, so generalisation was
           mandatory: derive the tool list from what the steps and the shared runner invoke,
           and give a step a declared context instead of an indefinite deferral.
Becomes:   config/<slug>-build.yml — `when: ci` on `auth`, plus a `required_tools` block with a
           context per tool, including `yq` (needed by run-config-steps.sh; nothing declared it)
           scripts/verify-build-config.py — check_execution_context + a --context flag
           scripts/ci/run-config-steps.sh — honours `when:`, records OUT OF CONTEXT skips
           agents/build-agent.md — an out-of-context skip is not a deferral and does not count
Retires:   nothing, but it ENDS a practice: "deferred, not a defect" is no longer available for
           a step that cannot run here. It is either declared out-of-context or it is a defect.
Cites:     IMP-0041, IMP-0077
Coverage:  four known-bad fixtures, each exiting 1 — tool-missing, undeclared-tool, bad-when,
           no-required-tools. yq 4.53.4 installed at the reviewer's instruction.
Residual:  TWO. (1) The four fixtures live in the scratchpad, not under
           src/tests/fixtures/known-bad/, and the negative tests C-TECH-057 requires are not
           committed — src/tests/ is outside this agent's scope, so it joins the
           development-agent handoff. (2) SHELL_BUILTINS is a hand-kept list, which is the very
           shape this cluster set out to remove; a coreutils name missing from it produces a
           false failure rather than a false pass, so it fails safe, but it is still a list
           somebody must maintain.
```

**Proof it works, not just that it validates.** The entire build was executed through
`scripts/ci/run-config-steps.sh` — the only path `ci.yml` uses — for the first time in this
project's history: 22 steps executed, 1 out of context (`auth`), 23 declared, exit 0, 739 tests
passed, coverage 89.13%, solution checker clean. Every previous build, build #8 included, ran the
steps directly and could only assert the runner *would* work.

## Where this review ended up

| Finding | Class | Outcome |
|---|---|---|
| `IMP-0019` | `exit-zero-does-not-mean-created` | APPLIED — resolved in the environment, guarded by `C-TECH-064` |
| `IMP-0082` | `exit-zero-does-not-mean-created` | APPLIED — `C-TECH-064`, `C-DOM-032` narrowed, pipeline preflight check 10 |
| `IMP-0083` | `live-verification-capability` | APPLIED — `knowledge/technology/testing-tools.md` |
| `IMP-0084` | `harness-blocks-destructive-call` | APPLIED — `agents/pipeline-agent.md` Reviewer-Executed Operations |
| `IMP-0041` | `gate-cannot-fail` | APPLIED — execution context |
| `IMP-0077` | `two-invocation-paths-disagree` | APPLIED — tooling contract |
| `IMP-0005` | `test-coupled-to-absolute-counts` | Deferred → development-agent, approach chosen |
| `IMP-0039` | `test-coupled-to-absolute-counts` | Deferred → development-agent, approach chosen |

One new constraint against a cap of three. No retirement, and `C-DOM-032` narrowed rather than
retired so the source-side assertion survives.
