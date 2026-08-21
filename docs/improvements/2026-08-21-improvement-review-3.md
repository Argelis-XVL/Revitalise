# Improvement Review — 2026-08-21 (third review this date)

**Trigger:** two `blocker` findings appended by `test-agent` at 14:00 and 14:05, both from
[docs/tests/acc-walkthrough-data-test-report.md](../tests/acc-walkthrough-data-test-report.md).
Routed immediately under the do-not-batch rule, not at the ten-entry threshold.

**Status:** AWAITING `APPROVE IMPROVEMENTS`. Nothing in section 3 has been applied.

**Scope note.** One change was made before the gate, and it is not a rule change: `IMP-0147` was
appended to the log and the digest regenerated, because this review produced new ground truth
(section 2, cluster A) and the log is the only place that survives the session.

---

## 1. Regression check — did the last review's changes work?

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| [scripts/verify-improvement-log.py](../../scripts/verify-improvement-log.py) — the `C-TECH-061` blocker/threshold trigger | 2026-08-17 | `gate-cannot-fail`, on the learning loop's own trigger | No | **Working — and it is why this session exists.** Run at 14:45 it printed `TRIGGER: 2 NEW entry(ies) of severity 'blocker' with no 'deferred_reason': IMP-0145, IMP-0146` and exited 1. The routing decision was made by the gate, not by anyone remembering. |
| `skills/how-to-write-a-test-plan.md` — the platform-contract-assertion rule actually written | 2026-08-21, review 2 | `test-asserts-the-defect` | No new instance | **Working, unproven.** No test has been authored since; the rule has had nothing to bite on. Carried forward. |
| [src/tests/build/BuildGates.Tests.ps1](../../src/tests/build/BuildGates.Tests.ps1) — 7 negative tests wired for `verify-shipped-content.py` checks 3–7 | 2026-08-21, review 2 | `gate-cannot-fail` | No | **Working.** The orphaned-fixture defect it fixed (`IMP-0141`) has not recurred, and the two new gates proposed below are being wired with tests in the same change specifically because of it. |
| [scripts/verify-pipeline-config.py](../../scripts/verify-pipeline-config.py) check 10 — a step's `-Env` resolves to a settings file that exists | 2026-08-19 | `exit-zero-does-not-mean-created` | **Yes — the class it created recurred today.** | **Wrong altitude.** The check asserts the settings file EXISTS and never opens it. Run at 14:45 it reported `runtime settings files resolved: 31` and `PASS` over a `tst_acc` block whose first post-deploy step is guaranteed to throw. This is the finding logged as `IMP-0147` and the substance of cluster A. |
| `knowledge/technology/entra-id.md` — the Graph-permission half of `IMP-0105` | 2026-08-20 | `credential-not-on-the-machine-that-needs-it` | **Yes — `IMP-0146`, same property, different target system** | **Wrong altitude, and half-applied.** The finding bundled a Graph permission gap (documented) with a `tenantId` placeholder (never fixed) under one `APPLIED` status. Both halves recurred within 24 hours. See clusters A and B. |

Two of five prior changes were at the wrong altitude, and both failed the same way: something was
verified by its **existence** rather than its **content**.

---

## 2. Clusters and promotion decisions

### CLUSTER A — "it exists" was accepted as "it is right" (x2 here, x5 in the wider class)

```
CLUSTER:    existence-checked, content-unchecked   (IMP-0140, IMP-0145, IMP-0147)
Wider class: evidence-rule-satisfied-by-a-forward-reference (x4: IMP-0067, IMP-0097,
             IMP-0099, IMP-0140) — the same property, already recurring
Altitude:   CLASS. IMP-0140 was deferred at the last review with revisit_when "the next
            improvement review, or the next time an APPLIED claim is found unevidenced —
            whichever comes first". Both conditions are now met, by IMP-0145, in under a day.
Ladder row: "a tool could catch it mechanically" + "second instance → generalise"
Becomes:    two mechanical checks, no new constraint — both fold under constraint rows
            that already exist (C-TECH-061 and C-TECH-062)
Retires:    nothing in this cluster
Cites:      IMP-0140, IMP-0145, IMP-0147
```

The three instances are one sentence written three ways:

- `IMP-0140` — an `APPLIED` status was reconciled against a file's **existence**. The file was
  102 lines and did not contain the rule the log claimed it carried.
- `IMP-0145` — `IMP-0105` was marked `APPLIED` because a knowledge document was updated. The
  settings file the same finding named was never edited.
- `IMP-0147` — [verify-pipeline-config.py](../../scripts/verify-pipeline-config.py) check 10
  resolves the settings **file** for each step and never opens it.

**New ground truth this review produced, which changes what `IMP-0145` asks for.** The finding
describes a one-line fix in two files. Walking both files programmatically, skipping
documentation keys, that is not the state:

| File | Unresolved `{{TOKEN}}` in value positions | Reached by a declared step? |
|---|---|---|
| `test-settings.json` | **9** (`tenantId` now resolved — see below) | Yes, all 9 |
| `prd-settings.json` | **14** (`tenantId` included) | Yes |

For `tst_acc`, every one of the nine is read by a step
[config/revitalise-grant-automation-pipeline.yml](../../config/revitalise-grant-automation-pipeline.yml#L743)
declares:

- `dataverse.groupTeams[0..1].entraGroupObjectId` is read at
  [bind-roles-to-groups.ps1#L60](../../provisioning/dataverse/bind-roles-to-groups.ps1#L60),
  which is `tst_acc.post_deploy[0]` — the **first** post-deploy step.
- The seven `entra.appRegistrations[*]` tokens are read at
  [verify-entra.ps1#L80](../../provisioning/entra/verify-entra.ps1#L80) and
  [#L91](../../provisioning/entra/verify-entra.ps1#L91), which is `tst_acc.smoke_tests[3]`.

`Assert-NoPlaceholder` at
[provisioning-common.ps1#L96](../../provisioning/common/provisioning-common.ps1#L96) is the only
thing that catches these, it runs inside `Get-Setting`, and it therefore fires **one key at a
time at run time**. Each fix reveals exactly one more placeholder. Nobody ever sees the set.
That is why a finding written yesterday described the remaining work as one line.

**A concurrent session edited one of these files while this review was running.**
`test-settings.json` line [28](../../provisioning/deploymentSettings/test-settings.json#L28) read
`{{TENANT_ID}}` when this session first grepped it and held the real tenant id three minutes
later (file mtime 14:50). `prd-settings.json` line
[25](../../provisioning/deploymentSettings/prd-settings.json#L25) was not touched. So the
two-file finding has now been half-applied on two consecutive days, by two different actors,
with no gate able to say so. This is `IMP-0080`'s warning about two live sessions on a synced
path, and it is also the clearest possible argument for the check proposed below.

**Residual.** Check 11 cannot see a placeholder in a settings file no pipeline step names, and
it cannot distinguish a resolved-but-wrong value from a resolved-and-correct one. A plausible
GUID in `tenantId` passes. `evidence_grep` is opt-in, so the roughly 130 existing `APPLIED`
entries stay unverified — retrofitting them is not this review's job.

### CLUSTER B — a token is not a membership (x2 across two target systems)

```
CLUSTER:    authenticated is not authorised in the target  (IMP-0146, prior instance IMP-0105)
Altitude:   CLASS. IMP-0105 got a knowledge line — instance altitude — and the class recurred
            in 24 hours against a different target system. The altitude rule forbids a second
            instance patch.
Ladder row: "a platform law, or a third instance" → a constraint row, plus the script that
            makes its Verify By mechanically executable
Becomes:    C-TECH-065 + provisioning/dataverse/verify-environment-access.ps1 +
            verify-pipeline-config.py check 12 + environment_prerequisites for tst_acc and prd
Retires:    nothing — this class was undefended
Cites:      IMP-0146, IMP-0105
```

The two instances are the same law in different clothes:

- `IMP-0105` — `Connect-ProvisioningGraph` succeeded; `Get-MgApplication` returned
  `Authorization_RequestDenied`. Its own lesson already says *"A successful Graph connection
  proves the credential, never the permission."*
- `IMP-0146` — token acquisition against the TST/ACC org succeeded; `WhoAmI` returned
  `0x80072560 — The user is not a member of the organization`, while the identical code and
  credentials resolved a `UserId` against DEV.

The structural cause is visible in the config.
[config/revitalise-grant-automation-pipeline.yml](../../config/revitalise-grant-automation-pipeline.yml#L560)
gives `dev` an `environment_prerequisites` block for exactly this kind of first-run onboarding.
`tst_acc` at line [743](../../config/revitalise-grant-automation-pipeline.yml#L743) and `prd` at
line [944](../../config/revitalise-grant-automation-pipeline.yml#L944) have **no such block at
all**, and their post-deploy lists open straight into
`provisioning/dataverse/*.ps1 -Env test|prd`.

I am proposing a constraint row on a class with two members rather than three, which
`skills/how-to-promote-a-finding.md` [§4](../../skills/how-to-promote-a-finding.md#L103) permits
only with a stated reason. The reason: the severity is `blocker`, the mechanism is a platform
law (a Dataverse application user is created per environment and no credential implies one), and
this is a second instance, not a first.

**Residual.** Check 12 is static — it proves the probe is **declared** before the first step that
depends on it, never that it ran and passed. Only running it does that, and it cannot be run
against TST/ACC from this machine until somebody creates the application user. `C-TECH-065` will
therefore report `UNEVALUABLE` for `tst_acc` and `prd` on the day it ships. That is the true
state of those environments, not a hole in the rule.

### Not clustered — read-path defect found on the way

Both new classes land in the digest's **Unrouted** section, which the digest itself flags as a
defect: *"these findings' `class_instance_of` values are missing from the routing table … Add
them, so the lesson reaches the agent at the moment it applies."* Two lessons whose entire
purpose is to be read before running a script against a new environment currently reach nobody,
while the section named *"Before you run something on a machine it has never run on"* sits four
lines away in [scripts/generate-known-failure-modes.py#L110](../../scripts/generate-known-failure-modes.py#L110).
Routing them is a two-line change and is included below. Thirteen other classes are still
unrouted; they are named as an open item, not fixed here.

---

## 3. Proposed changes

| # | Type | Target | Change | Cites | Mechanically verifiable? |
|---|---|---|---|---|---|
| 1 | script | [scripts/verify-improvement-log.py](../../scripts/verify-improvement-log.py) | Optional `evidence_grep` field on an `APPLIED` entry naming a string its `applied_by` target must contain. `--check` fails when the pair does not match. Opt-in, so it cannot retroactively fail the ~130 existing `APPLIED` entries | IMP-0140 | YES — new known-bad fixture under `src/tests/fixtures/known-bad/improvement-log/` + negative test in the existing `Describe 'CI gate: verify-improvement-log (C-TECH-061)'` block |
| 2 | build-gate | [scripts/verify-pipeline-config.py](../../scripts/verify-pipeline-config.py) | **Check 11** — for every step whose `-Env` resolves to a settings file, open it and report each unresolved `{{TOKEN}}` in a value position, skipping `_`-prefixed documentation keys. Accepted-but-unresolved keys are declared in an `_unresolved` block **inside that settings file**, each carrying `path`, `owner`, `why`, `expires`. Reported on every run; never silently waived; FAIL when missing, unowned or expired | IMP-0145, IMP-0147 | YES — extends `settings_file_for()` at [#L146](../../scripts/verify-pipeline-config.py#L146); fixture + negative test in the existing `Describe 'CI gate: verify-pipeline-config (C-TECH-062)'` block |
| 3 | build-gate | [scripts/verify-pipeline-config.py](../../scripts/verify-pipeline-config.py) | **Check 12** — an environment block declaring any executable `provisioning/**` step must also declare an identity probe for that environment, positioned before the first such step | IMP-0146 | YES — same fixture family and Describe block |
| 4 | script (new) | `provisioning/dataverse/verify-environment-access.ps1` | The probe: resolve the auth triplet for `-Env <env>`, call `WhoAmI` against that org, print `PASS`/`FAIL` per the provisioning script contract, exit non-zero on failure. This is the call that would have turned today's four-hour diagnosis into one line | IMP-0146 | YES — Pester tests in `DataverseScripts.Tests.ps1`, mocked both ways |
| 5 | constraint | `C-TECH-065` (new, HARD) | *A credential that authenticates is not an identity that is authorised. Before any script is trusted against a target environment, a minimal identity probe against that exact environment must succeed, and the pipeline config must declare it before the first step that depends on it.* Verify By: `pwsh provisioning/dataverse/verify-environment-access.ps1 -Env <env>` exits 0, and `python3 scripts/verify-pipeline-config.py` check 12 passes | IMP-0146, IMP-0105 | YES — both halves are commands |
| 6 | config | [config/revitalise-grant-automation-pipeline.yml](../../config/revitalise-grant-automation-pipeline.yml) | Add `environment_prerequisites` to `tst_acc` and `prd`, mirroring `dev`: a `manual` step to create the Dataverse application user for `$PROVISION_APP_ID` in the Power Platform admin center, then the probe from change 4. Add the probe to `dev` too — it has no explicit one either | IMP-0146 | YES — `python3 scripts/verify-pipeline-config.py` |
| 7 | source fix | [prd-settings.json#L25](../../provisioning/deploymentSettings/prd-settings.json#L25) | `tenantId` → the real value, matching the edit a concurrent session already made to `test-settings.json` | IMP-0145 | YES — check 11 |
| 8 | source fix | `test-settings.json`, `prd-settings.json` | Add the `_unresolved` block declaring the remaining 9 and 13 keys, each with owner, reason and expiry. **This is the list in section 7 that needs your decision** | IMP-0145, IMP-0147 | YES — check 11 |
| 9 | test | [src/tests/build/BuildGates.Tests.ps1](../../src/tests/build/BuildGates.Tests.ps1) | Negative and positive tests for `evidence_grep`, check 11 and check 12, in the two existing Describe blocks at [#L604](../../src/tests/build/BuildGates.Tests.ps1#L604) and [#L654](../../src/tests/build/BuildGates.Tests.ps1#L654). Written in the same change as the checks, per `IMP-0141` | C-TECH-057, IMP-0141 | YES — each proven able to fail |
| 10 | script | [scripts/generate-known-failure-modes.py#L110](../../scripts/generate-known-failure-modes.py#L110) | Route `config-placeholder-known-but-not-fixed` and `provisioning-identity-not-onboarded-to-target-environment` into *"Before you run something on a machine it has never run on"* | IMP-0145, IMP-0146 | YES — `--check` after regeneration |

**One new constraint against a cap of three.** Clusters A's changes deliberately produce none:
`verify-improvement-log.py` is already governed by `C-TECH-061`
([constraints/technology/technology-constraints.md#L131](../../constraints/technology/technology-constraints.md#L131))
and `verify-pipeline-config.py` by `C-TECH-062`
([#L132](../../constraints/technology/technology-constraints.md#L132)). Adding checks to a gate a
constraint already owns needs no new row.

---

## 4. Retirements

**Candidate: `C-TECH-031`** —
[constraints/technology/technology-constraints.md#L72](../../constraints/technology/technology-constraints.md#L72),
*"Environment-specific values must not be embedded in the artifact — they are injected at deploy
time."*

Two reasons, and they are the two the 2026-08-19 sweep used to retire `C-TECH-011`, `012`, `013`,
`020`, `021` and `022`:

1. **Its `Verify By` is not mechanically executable.** It reads *"Code review; `build.yml`
   `required_env_vars` block documents injection points."* Anti-bloat limit 4 and
   [constraints/README.md#L122](../../constraints/README.md#L122) both forbid this shape.
2. **Its substance is already enforced twice, by gate.** `C-TECH-047`
   ([#L89](../../constraints/technology/technology-constraints.md#L89)) covers hardcoded
   environment values with a real grep over the solution tree — `IMP-0119` records that gate
   firing on an example URL in a comment. The `required_env_vars` half is enforced by
   `verify-build-config.py` and by check 8 of `verify-pipeline-config.py`.

**Coverage proof is different in kind here, and I want to be explicit about it.** The retirement
procedure asks that the retired row's known-bad fixtures still fail under the replacement.
`C-TECH-031` **has no fixture, because it has never had a gate** — which is precisely the
argument for retiring it. The coverage claim rests instead on the two enforced mechanisms above
being a superset of its text. If you would rather keep the row, nothing else in this review
depends on it.

---

## 5. Findings left unprocessed

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| `IMP-0085` | `no-assertion-on-shipped-content` | Table-level auditing has no representation in solution source, and the live half of the `C-TECH-064` verifier needs environment credentials. Carried unchanged from the 2026-08-20 and 2026-08-21 reviews. Today's cluster B makes it worse, not better: there is now no working credential for TST/ACC at all | The next Dataverse table is built (Phase 3, tasks 6.4 / 8.1) |
| `IMP-0112` | `platform-contract-guessed-not-groundtruthed` | The gate is applied and still firing; the instance fix restructures six chained actions in a flow that has never run live, with nothing to regression-test it against | Before the WordPress integration is connected to DEV |

No finding was dropped or silently capped. Six were `NEW` at the start of this review: four are
processed here, two are restated above with their conditions unchanged.

---

## 6. Digest impact

| | Before this review | After |
|---|---|---|
| Log entries | 143 | 144 (`IMP-0147` appended before the gate) |
| Distinct lessons | 143 | 144 |
| Recurring classes (x≥2) | 19 | 19 — `gate-reassures-wrongly` moves x4 → x5; neither new class recurs yet |
| `NEW` entries | 6 | 2, both deferred with a recorded reason and a revisit condition |
| Unrouted classes | 15 | 13 |
| Digest lines | 391 | 393 now, ~395 after approval |

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-21-improvement-review-3.md

Findings processed: 6 NEW  →  2 clusters (4 processed, 2 restated as deferred)
Regression check:   5 prior changes audited, 2 classes recurred (both at the wrong altitude)
Proposed:           1 constraint (cap 3), 3 gates/scripts, 0 skill/knowledge edits,
                    0 agent-file edits, 1 retirement
Altitude calls:     2 generalised from instance to class, 0 left as notes
Digest:             will regenerate — 144 lessons, 19 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

### What needs your decision before change 8 can be written

**Who owns the nine unresolved keys in `test-settings.json`, and by when?**

They are two Entra security-group object ids for the TST/ACC group teams, and seven Entra
permission and application ids. I cannot read any of them: `IMP-0105` established that this Mac's
provisioning identity cannot read Entra app registrations. They need an owner and an expiry date
in the `_unresolved` block, or check 11 fails the preflight.

**Are the three `PENDING_OQ_*` values in `prd-settings.json` still awaiting the board?**

The file says they are. If so they are a legitimate owned exception with an expiry tied to the
board date. If the board has answered, they are a source fix instead.

**Do you want `C-TECH-031` retired?**

Section 4 makes the case. It is independent of everything else here.

---

## 8. Applied

`APPROVE IMPROVEMENTS` received 2026-08-21. All ten changes applied. Reviewer's answers to
section 7: no owner named for the nine TST/ACC keys (left failing, deliberately); the three
board-pending production values confirmed as a genuine owned exception; `C-TECH-031` retired.

| # | Applied | Evidence |
|---|---|---|
| 1 | `evidence_grep` on APPLIED entries — [verify-improvement-log.py](../../scripts/verify-improvement-log.py) | Fixture `unevidenced-applied.jsonl` + tree; 3 tests green. **It caught a false claim on its first run** — this review's own `IMP-0146` entry asserted a string with the wrong capitalisation, and the gate rejected it |
| 2 | Check 11 — settings files opened, not just resolved | Fixture `unresolved-settings.yml` + `envtree/`; 3 tests green, including one asserting `_`-prefixed documentation keys are NOT reported |
| 3 | Check 12 — identity proven per environment | Fixture `no-access-probe.yml`; 3 tests green |
| 4 | [provisioning/dataverse/verify-environment-access.ps1](../../provisioning/dataverse/verify-environment-access.ps1) | **Verified live, both directions.** PASS with a UserId against DEV *and* against TST/ACC |
| 5 | `C-TECH-065` added, HARD | [technology-constraints.md#L135](../../constraints/technology/technology-constraints.md#L135) |
| 6 | `environment_prerequisites` added to `tst_acc` and `prd`; probe added to `dev` | Preflight reports 3 environment access probes |
| 7 | Production `tenantId` resolved | [prd-settings.json#L25](../../provisioning/deploymentSettings/prd-settings.json#L25) |
| 8 | `_unresolved` block declaring the four board-pending production values | Preflight prints 4 `ACCEPTED` lines naming owner and expiry |
| 9 | 6 negative/positive tests wired in the same change as the checks | `Invoke-Pester src/tests/build`: 99 passed |
| 10 | Both new classes routed out of the Unrouted bucket | Digest regenerated, 145 entries, 395 lines |
| — | `C-TECH-031` retired | [technology-constraints.md#L72](../../constraints/technology/technology-constraints.md#L72) + the Retired Constraints table |

### Two things changed under this review while it ran

**The TST/ACC application user now exists.** The probe written for change 4 returns
`PASS — provisioning identity recognised by https://org68bf3a64.crm17.dynamics.com/` with a
resolved `UserId`. `IMP-0146`'s environment half is therefore **cleared** — someone created it
between the test report at 14:05 and the probe run at 15:20. Production is still unproven and
its prerequisite step is marked not-yet-done. The finding stays `APPLIED` on the strength of the
rule and the probe, not on the environment having been fixed by someone else.

**A concurrent session resolved the TST/ACC tenant id** at 14:50, mid-review, leaving production
untouched. Recorded in cluster A; production was fixed here.

### Left deliberately failing

`python3 scripts/verify-pipeline-config.py config/revitalise-grant-automation-pipeline.yml`
**exits 1**, on exactly two errors: nine unowned unresolved keys in `test-settings.json` and nine
in `prd-settings.json`. Per the reviewer's instruction, no owner or date was invented for them.
CI's `validate` job will be red until someone names an owner, and the Pester suite asserts the
failure is *only* this — a new pipeline defect still breaks the build rather than hiding behind
a known-red gate.

### Residual, beyond the per-cluster residuals in section 2

`powershell_params()` in the preflight misses the final parameter of a **single-line** `param()`
block, because it searches up to but not including the closing parenthesis. Every real
provisioning script here declares parameters multi-line, so nothing in this repository is
affected — it surfaced only when the first draft of the new fixture was written on one line.
It is a latent false FAIL in a HARD gate. Not fixed here: changing a gate's matching behaviour
is outside what this review was approved for. Logged for the next cycle.
