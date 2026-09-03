# Improvement Review — 2026-09-03

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 1 unread → 1 cluster
**Trigger:** blocker escalation — [`IMP-0585`](../../logs/improvement-log.jsonl#L582), unread, appended by build-agent at 09:30
**Gate:** `APPROVE IMPROVEMENTS`
**Status:** APPLIED 2026-09-03 — see §8. Scope was **expanded** by the reviewer beyond this draft;
the deviation is recorded there and in [`IMP-0585`](../../logs/improvement-log.jsonl)'s `applied_by`.
**WBS:** 6.8 (carried from the finding; system-rule changes, not a contracted deliverable)

The 14-day re-test window did its job and the halt is correct. The defect worth fixing is that the
window has **no lead time and no visibility**: yesterday's build printed
`pipeline-config-preflight PASS` while all 11 `blocked_on` notes were within four days of expiry —
eight of them with zero days left — because
[`check_blocked_on_staleness`](../../scripts/verify-pipeline-config.py#L492) counts note freshness
into `stats` and the PASS branch never prints it. The re-test itself needs live Entra/Graph/Dataverse
access this session does not hold, so it is reviewer work, named in §5.

---

## 1. Regression check — did the last review's changes work?

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| [`2026-09-02` review](2026-09-02-improvement-review.md) — the artifact-manifest refusal at [pipeline-agent activation step 3](../../agents/pipeline-agent.md#L37) | 2026-09-02 | `artifact-cited-for-deploy-has-no-build-record` | **NO** — no entry after [`IMP-0582`](../../logs/improvement-log.jsonl#L579) carries this class | **Working.** The 2026-09-02 15:35 build produced a `manifest.json` and `verify-build-manifest-note.py` reported OK |
| Review 10 — [`scripts/verify-code-app-bundle-budget.py`](../../scripts/verify-code-app-bundle-budget.py) plus its build step | 2026-09-01 | `untriaged-tool-warning` | **NO** | **Working, and now genuinely exercised.** The prior review could only say "not yet reached"; the 2026-09-02 15:35 build reached it and recorded `code-app-bundle-budget PASS (1,206.04kB within budget)` |
| Review 16 — the 14-day window itself ([`BLOCKED_ON_MAX_AGE_DAYS`](../../scripts/verify-pipeline-config.py#L487), closing [`IMP-0222`](../../logs/improvement-log.jsonl)) | 2026-08-23 | `agent-instructions-describe-a-topology-that-changed` | **YES — and this is the finding under review** | **The gate worked exactly as designed.** This is not a `gate-cannot-fail`: the note expired, the gate fired, the build stopped. What recurred is the *stale note*, not a defect in the check |

**Classes that recurred after a prose fix:** none.
**Classes that recurred after a gate:** one — the 14-day window fired as intended. Per the
regression table in [`agents/improvement-agent.md`](../../agents/improvement-agent.md#L283), a
recurrence after a gate asks whether the gate ran. It ran and it failed the build, so the escalation
row does not apply; the gap is upstream of detection.

---

## 2. Clusters and promotion decisions

```
CLUSTER: stale-deferral-uncaught-across-sessions  (x1 unread: IMP-0585; x2 in class with IMP-0366)
Altitude:  MECHANISM, not instance. The instance (8 expired notes) is reviewer-executed live
           work and cannot be fixed from here. The general property is that a dated deferral
           goes from silent to HARD-halt with no interval in which anyone is told, and the
           halt lands on whichever unrelated feature builds next.
Ladder row: "a tool could catch it mechanically" — but the tool ALREADY catches it. The
           cheapest home is therefore ADDITIVE, inside the already-wired check, not a new gate.
Becomes:   two edits to scripts/verify-pipeline-config.py (change 1 and change 2 below).
           NO new constraint, NO new script, NO new build step, NO new gate to wire.
Retires:   nothing — see §4.
Cites:     IMP-0585, IMP-0222, IMP-0366
Residual:  The window still cannot tell a re-tested note from a re-dated one. Re-dating is a
           human assertion, and nothing here verifies the re-test happened — only that
           somebody claimed a date. That is unchanged and stated rather than fixed.
```

The altitude rule's second-instance clause is satisfied without an instance patch: `IMP-0366` and
`IMP-0585` share `stale-deferral-uncaught-across-sessions` but not a mechanism — `IMP-0366` was
`contract/tad-deferrals.json` and its fix was an *ordering* rule in
[`agents/architect-agent.md`](../../agents/architect-agent.md). The property common to both is that
**a deferral's satisfaction is nobody's scheduled job, so it is discovered by an unrelated
dispatch's gate.** Change 1 gives that property a lead time in the one place it is already measured.

---

## 3. Proposed changes

### Change 1 — print blocked_on freshness on PASS, and warn before expiry (`scripts/verify-pipeline-config.py`)

[`check_blocked_on_staleness`](../../scripts/verify-pipeline-config.py#L492) already increments
`stats["blocked_on_checked"]` at [line 498](../../scripts/verify-pipeline-config.py#L498) and
`stats["blocked_on_fresh"]` at [line 523](../../scripts/verify-pipeline-config.py#L523). Neither is
in the PASS print block, so both are discarded. The change:

- emit a non-failing `WARNING: <location>: blocked_on expires in N day(s)` for any note with
  `0 <= 14 - age <= 4`;
- add a `blocked_on notes: <fresh>/<checked> fresh, <N> expiring within 4 days` line to the PASS
  summary.

The HARD error at [line 516](../../scripts/verify-pipeline-config.py#L516) is untouched. This is
purely additive — nothing the check currently refuses becomes accepted.

**Measured against the real corpus, both directions:**

| As of | 8 notes @ 2026-08-19 | 2 notes @ 2026-08-21 | 1 note @ 2026-08-22 | Warnings the change emits |
|---|---|---|---|---|
| 2026-09-02 (build PASSED) | age 14, 0 days left | age 12, 2 days left | age 11, 3 days left | **11** — on a run that reported PASS |
| 2026-09-03 (build HALTED) | age 15, **EXPIRED** | age 13, 1 day left | age 12, 2 days left | **3**, alongside the 8 existing errors |

So the change would have produced 11 warnings on the last passing build, the day before the halt.
The 4-day threshold is read off this corpus, not invented: it is the smallest window that catches
all 11 notes from the last green run.

**The prospective half matters more than the retrospective half.** The three remaining notes —
[`dev.post_deploy` code-app-push](../../config/revitalise-grant-automation-pipeline.yml#L1048)
(2026-08-22), [the Code App share](../../config/revitalise-grant-automation-pipeline.yml#L1073)
(2026-08-21) and [the TST/ACC application user](../../config/revitalise-grant-automation-pipeline.yml#L1472)
(2026-08-21) — expire on **2026-09-05 and 2026-09-06**. A reviewer who re-tests only the eight named
in the finding will be halted again within three days. Re-test all eleven in one sitting.

**Line numbers in this section were grepped before the edit landed.** Post-edit, the
constant is at [L502](../../scripts/verify-pipeline-config.py#L502), the function at
[L507](../../scripts/verify-pipeline-config.py#L507), the warning append at
[L546](../../scripts/verify-pipeline-config.py#L546), and the PASS-summary line at
[L762](../../scripts/verify-pipeline-config.py#L762).

### Change 2 — the finding message asks for a discharge condition

The error text at [line 517](../../scripts/verify-pipeline-config.py#L517) says *"either make it
executable or re-date the note with what still blocks it"*. It does not ask the author to say **what
would discharge the note**, and one of the eight shows why that costs:
[`dev.verification[4]`](../../config/revitalise-grant-automation-pipeline.yml#L1299) reads *"The
executable form of this check is the C-TECH-064 verifier … Until it exists this is a manual step"* —
naming no filename.

I measured the trap rather than describing it. [`scripts/verify-audited-tables.py`](../../scripts/verify-audited-tables.py)
now exists and is wired at [`build.yml` line 177](../../config/revitalise-grant-automation-build.yml#L177).
Executed, not read: it exits 0 with `AUDITED TABLES: PASS — 13 declared table(s) … in all 3 settings
file(s) that declare the key`. It reads **settings JSON**, so it is the source half, and
[`C-TECH-064`](../../constraints/technology/technology-constraints.md#L134) states that *a source-only
assertion may never be recorded as evidence for this row*. A re-tester grepping for "the C-TECH-064
verifier" finds a plausibly-named, build-wired, green script and could clear the note wrongly.

Per [`agents/improvement-agent.md`](../../agents/improvement-agent.md#L484) — where only prose is
available, the safe authoring form goes in the gate's own finding message, not in a document someone
has to remember — the error text gains one clause: *state what would discharge this note, as a command
or a query. A note naming a capability but no path invites a wrong clear.* No gate reads the note's
prose; this project has measured prose gates at 48–100% false five times, and change 2 deliberately
does not become one.

### What I did NOT propose

A gate asserting that a `blocked_on` note's cited artefact now exists. Review 16 built exactly that
and **withdrew it** — 3 false positives on this same config, and it would not have caught `IMP-0222`,
because the auditing note never named the file. Re-proposing it would be re-running a measured
failure.

---

## 4. Retirement

**Checked; no candidate.** The one I considered and rejected is
[`BLOCKED_ON_MAX_AGE_DAYS`](../../scripts/verify-pipeline-config.py#L487) itself — a 14-day window
that halts unrelated features is the kind of rule that looks like a tax. It stays, and the case
against retiring it is in this review's own evidence: three of the eleven notes' stated causes had to
be re-measured today, and **four of the eight are re-testable from the repository alone** (§5), which
is precisely the work nobody does until something forces it.

Derived at draft time, not retyped: 10 retired constraint rows, 82 live rows, 57 `verify-*.py`
scripts. This review adds no constraint and no script, so all three figures are unchanged and
`scripts/derived-counts-registry.json` needs no update.

---

## 5. REVIEWER ACTION REQUIRED — the 8 notes cannot be re-tested from here

Per the Reviewer-Executed Operations protocol
([`agents/pipeline-agent.md`](../../agents/pipeline-agent.md#L99), `IMP-0170`/`IMP-0048`/`IMP-0061`/`IMP-0105`/`IMP-0528`),
and because `PROVISION_APP_ID` and `PROVISION_CERT_THUMBPRINT` are **reviewer-held by design**
([`agents/lead-agent.md`](../../agents/lead-agent.md#L190) — note the brief cited
`agents/development-agent.md`, which does not mention them), I did not attempt the live half.

**Four of the eight are repository facts, and I re-tested them now.** All four causes still hold, so
these need re-dating, not resolving:

| Note | Stated cause | Re-measured 2026-09-03 |
|---|---|---|
| [`dev.environment_prerequisites[5]`](../../config/revitalise-grant-automation-pipeline.yml#L651) | no PnP template under `provisioning/sharepoint/templates/` | **STILL HOLDS** — that directory contains `README.md` only |
| [`dev.environment_prerequisites[7]`](../../config/revitalise-grant-automation-pipeline.yml#L670) | `Get-ProvisioningSettings -Env dev` throws; no `-SettingsPath` override | **STILL HOLDS** |
| [`dev.environment_prerequisites[8]`](../../config/revitalise-grant-automation-pipeline.yml#L687) | same | **STILL HOLDS** |
| [`dev.post_deploy[2]`](../../config/revitalise-grant-automation-pipeline.yml#L1088) | same, via `bind-roles-to-groups.ps1` | **STILL HOLDS** — [line 50](../../provisioning/dataverse/bind-roles-to-groups.ps1#L50) is `Get-ProvisioningSettings -Env $Env` and the script is absent from the 12 `provisioning/dataverse/*.ps1` that accept `-SettingsPath` |

**Four need the reviewer.** The commands, in the notes' own terms:

```bash
# 1. tenant_prerequisites.operations[12] — pipeline.yml L464. DEV region code still {{REGION_VALUE_TBC}}.
#    DEV demonstrably exists (builds deploy to $ENV_URL_DEV), so the note's ASK is now recording
#    the environment id + URL, not resolving a region string. Verify and re-scope the note:
pac admin list --name "Revitalise Grant Automation (DEV)"

# 2. dev.verification[4] — pipeline.yml L1299. The LIVE audit read (C-TECH-064). NOT discharged by
#    scripts/verify-audited-tables.py, which is source-side. Per entity folder under
#    src/solutions/RevitaliseGrantAutomation/Entities/:
pwsh provisioning/dataverse/ensure-auditing.ps1 -Env dev   # then read it back by query:
#    GET organizations?$select=isauditenabled,auditretentionperiodv2      -> True, 2192 (never -1)
#    GET EntityDefinitions(LogicalName='<name>')?$select=IsAuditEnabled   -> Value=true, all 13

# 3. dev.verification[5] — pipeline.yml L1317. V3 component-by-component query, list DERIVED FROM
#    SOURCE. Blocked on the same Get-ProvisioningSettings cause; confirm whether that still binds
#    once a dedicated dev settings path exists, then re-date or make executable.

# 4. prd.environment_prerequisites[0] — pipeline.yml L1719. PRD application user for
#    $PROVISION_APP_ID. Needs System Administrator on PRD; admin centre only, no script can do it.
#    Prove it with the probe the note names before any APPROVE PRD deploy:
pwsh provisioning/dataverse/verify-environment-access.ps1 -Env prd
```

Then re-run the gate that halted the build, and expect the three imminent notes to need the same
treatment:

```bash
python3 scripts/verify-pipeline-config.py config/revitalise-grant-automation-pipeline.yml
```

**Verification level reached by this review: V1.** Change 1 and change 2 are unexecuted source edits
until the keyword arrives; the four repository re-tests above are V1 measurements; the four live
re-tests are **unexecuted** and named to the reviewer, per `C-TECH-053`.

---

## 6. Queue scope — what this review excluded, and why

The blocker trigger summons the **unread** subset only
([`IMP-0183`](../../logs/improvement-log.jsonl), [`agents/improvement-agent.md`](../../agents/improvement-agent.md#L84)).
`verify-improvement-log.py --check` reports 140 NEW: 21 unread, 0 awaiting-approval, 119
reviewer-deferred, 0 already-fixed, 0 approved-not-applied.

- **Processed: 1** — `IMP-0585`, the only unread `blocker`.
- **Excluded: 20 unread non-blockers** — `IMP-0549`, `IMP-0550`, `IMP-0551`, `IMP-0552`, `IMP-0562`,
  `IMP-0563`, `IMP-0566`, `IMP-0567`, `IMP-0570`, `IMP-0571`, `IMP-0572`, `IMP-0575`, `IMP-0576`,
  `IMP-0577`, `IMP-0578`, `IMP-0579`, `IMP-0580`, `IMP-0581`, `IMP-0583`, `IMP-0584`. Each is stamped
  `excluded_by` naming this document, per [`IMP-0557`](../../logs/improvement-log.jsonl), so the
  no-silent-caps rule does not trip a citation-stamp warning per id. None is a blocker; none carries
  `corrects` against `IMP-0585`.
- **Excluded: 119 reviewer-deferred** — left untouched, per activation step 2.

Nine of the 20 excluded ids already carry a citation-stamp warning: they are cited by review
documents dated 2026-09-01 and 2026-09-02 and carry no `reviewed_in`. That is a pre-existing
bookkeeping defect in those reviews, not something this dispatch created, and it is **not** fixed
here — stamping another review's processed entries would be a false claim about who analysed them.
Flagged for the next full queue pass.

---

## 7. Disposition of IMP-0585

`observable_at` is `n/a` and the instance is not closed: the eight notes are still stale and the
build is still halted. On the keyword, `IMP-0585` becomes **`NEW` with a `deferred_reason`**, not
`APPLIED` — the mechanism changes land, the live re-test does not.

This is deliberate and it is the schema's named second discharge. A bare `revisit_when` would leave
the blocker trigger permanently lit ([`IMP-0516`](../../logs/improvement-log.jsonl)); `classify()`
gives `deferred_reason` precedence over `awaiting-approval`, so the trigger clears while the entry
stays honestly open. Simulated on a scratch copy before parking, per activation step 8 — the result
is in the gate output below.

Until the keyword, the blocker trigger **stays lit**, because a `reviewed_in` stamp with no
`deferred_reason` classifies as `awaiting-approval` and the blocker rung fires on that too. That is
correct, not a defect to route around.

---

## 8. Applied record — 2026-09-03

`APPROVE IMPROVEMENTS` received. Re-verified before applying, per activation step 8: the log was
unchanged at 582 entries with `IMP-0585` still the maximum id, no entry carried `corrects` naming it,
and `stale-deferral-uncaught-across-sessions` still had two members.

| # | Change | File | Verified by |
|---|---|---|---|
| 1 | [`BLOCKED_ON_WARN_DAYS = 4`](../../scripts/verify-pipeline-config.py#L502) — a note within 4 days of expiry emits a non-failing `WARNING`, printed on **both** the PASS and FAIL paths and **before** the errors | `scripts/verify-pipeline-config.py` | 3 findings on the real config, **3 true positives, 0 false positives** — days-left 2/1/1 matches each note's asserted date |
| 2 | PASS summary gains `blocked_on notes: <fresh>/<checked> fresh, N expiring within 4 day(s)` — both stats were already counted and discarded | `scripts/verify-pipeline-config.py` | PASS branch exercised on an all-fresh scratch copy: `11/11 fresh, 3 expiring within 4 day(s)`, exit 0, warnings still shown |
| 3 | The HARD error text now also asks for a **discharge condition**, as a command or query, citing the `verify-audited-tables.py` trap | `scripts/verify-pipeline-config.py` | Error text re-read on the live 4 remaining failures |
| 4 | **Reviewer-expanded scope:** the 4 repository-fact notes re-dated to `2026-09-03`, each gaining a `DISCHARGE:` line naming the grep that settles it | `config/revitalise-grant-automation-pipeline.yml` L651, L670, L687, L1088 | Gate re-run: **8 errors → 4**, YAML parses, 104 steps still enumerated |

**No new constraint, no new script, no new build step.** The 57 `verify-*.py` count and the 10
retired / 82 live constraint rows are unchanged, so `scripts/derived-counts-registry.json` needed no
edit. `verify-build-config.py` exits 0.

### The deviation from this draft, stated plainly

This draft proposed **no edit** to `config/revitalise-grant-automation-pipeline.yml` and routed all
eight notes to the reviewer. The reviewer approved that and expanded it: re-date the four whose
causes this review had itself re-measured. That was the better call, and the reason is recorded as
[`IMP-0586`](../../logs/improvement-log.jsonl) — a reviewer-held credential scopes the **operation**,
not the **file**, and §5's own measurement table was the signal that the split was available. The
draft also proposed a `deferred_reason`; the reviewer directed closure.

### RESIDUAL — the build is still halted

`python3 scripts/verify-pipeline-config.py config/revitalise-grant-automation-pipeline.yml` **exits
1** with four errors: [`tenant_prerequisites.operations[12]`](../../config/revitalise-grant-automation-pipeline.yml#L464),
[`dev.verification[4]`](../../config/revitalise-grant-automation-pipeline.yml#L1299),
[`dev.verification[5]`](../../config/revitalise-grant-automation-pipeline.yml#L1317) and
[`prd.environment_prerequisites[0]`](../../config/revitalise-grant-automation-pipeline.yml#L1719).
Their re-tests need live access this session does not hold; the commands are in §5 and the reviewer
has **not** yet run them.

Closing `IMP-0585` loses nothing despite that residual, and the reason is mechanical rather than a
promise: the residual is enforced by a HARD gate at step 2 of 72, so the next build for **any**
feature sharing this config halts and re-raises it. It is not held by anyone's memory.

### Still outstanding, not created here

Three notes expire **2026-09-05 / 09-06** — the change-1 warnings now name them on every run. Nine of
the 20 excluded ids carry pre-existing citation-stamp warnings from the 09-01/09-02 reviews, and
`verify-derived-counts.py` reports 6 SOFT drifts in files this review did not touch.

---

## 9. Second application pass — 2026-09-03, reviewer-supplied live evidence

The reviewer ran two of the four residual re-tests and supplied the output. Applied directly rather
than as a new review, because **no rule changed**: nothing under `agents/`, `constraints/`,
`skills/` or `knowledge/` is touched, and this is the discharge bookkeeping §5 asked for. Verified
before applying — every claim below was checked against the repository, not taken on the report.

| Note | Reviewer evidence | What I verified | Applied |
|---|---|---|---|
| [`tenant_prerequisites.operations[12]`](../../config/revitalise-grant-automation-pipeline.yml#L462) | `pac admin list` — DEV exists, Active, Sandbox, id `2f7ce6a9…`, url `orge2b20d13.crm17.dynamics.com` | The id and url **already matched** four tracked `dev-*-settings.json` files, and the org id matched the Deployment Summary. Corroboration, no conflict | `blocked_on` **removed**, not re-dated — the note's own second branch ("create it and record the id and url") is done. `satisfied_on` / `satisfied_by` record the evidence |
| [`dev.verification[4]`](../../config/revitalise-grant-automation-pipeline.yml#L1347) | `ensure-auditing.ps1 -Env dev` — org `enabled=True`, retention 2192, `EXISTS` for 13 tables | The script GETs `organizations?$select=…` and per-table `EntityDefinitions(LogicalName=…)`, so `EXISTS` = **queried live and already correct**, not the set-call exit code the step forbids. The 13 tables match the 13 `Entities/` directories exactly, name by name | Step made **executable** (`provisioning/dataverse/ensure-auditing.ps1 -Env dev`); `blocked_on` removed; `verified_on` / `verified_by` record the evidence |

**Gate result: 8 errors → 4 → 2.** The two remaining are
[`dev.verification[5]`](../../config/revitalise-grant-automation-pipeline.yml#L1371) and
[`prd.environment_prerequisites[0]`](../../config/revitalise-grant-automation-pipeline.yml#L1773),
both left untouched as instructed — the latter pending the reviewer's scope decision on whether six
`-Env prd` provisioning steps remain in scope, since Power Platform Pipelines replaces only the
solution-import hop. Step count still 104; the newly-executable script path and its `-Env` parameter
both validate.

### A third defect found while verifying, and it is the interesting one

The note's own `draft_command` said `--name "Revitalise Grant Automation (DEV)"`. **That is not the
environment's name.** It is `REV-GrantApplications-DEV` in eight other places in this same file and
in `contract/external-dependencies.json`; the wrong name appeared only on that line. So the note's
supplied re-test could only ever return zero rows — which reads exactly like *"the environment was
never created"*, the very thing the note claimed. A re-test command is untested content, and this one
was a **false-negative generator pointing at its own conclusion.** Corrected in place, with the
withdrawn wording retained in the comment above it.

That is logged as [`IMP-0587`](../../logs/improvement-log.jsonl), together with the two closures'
shared lesson: one blocker was already **satisfied** by values the repository had tracked for weeks,
and the other was **disproved** rather than expired — `ensure-auditing.ps1` already was the
C-TECH-064 read-back the step said it was awaiting, and was already wired executably three times over
in the same file. Its proposed gate is deliberately **not built**: a name-matching check would fire
on every correction comment in a file whose documented style retains withdrawn wording, which is the
48–100%-false prose-gate shape measured five times here. It needs a corpus measurement first.

This is direct evidence for change 2 of §8, written hours earlier: the note named a capability and no
path, and the discharge-condition clause is what would have surfaced it.

---

## 10. Third application pass — the PRD note is PARKED, not closed

Reviewer decision on [`prd.environment_prerequisites[0]`](../../config/revitalise-grant-automation-pipeline.yml#L1773):
park, do not close and do not drop. The real blocker is upstream of the admin role —
`$PROVISION_APP_ID` lacks Entra ID admin consent only a tenant **Global Administrator** can grant,
so the reviewer has been performing the six `-Env prd` provisioning operations manually as an
administrator. Same class as `IMP-0105`: a successful Graph connection proves the credential, never
the permission.

### Why neither obvious disposition worked

The 14-day window is a **time**-based instrument, and it assumes every blocker is one this project
can clear by working on it. This one is somebody else's approval — not stale, *pending*.

- **Re-dating** asserts "re-tested today, still blocked", which nobody did, and then hides the note
  for 14 days. That is the silent vanish the reviewer refused by name.
- **Leaving it a hard error** halts every **DEV** build of every feature at step 2 of 72, because
  `pipeline-config-preflight` validates the whole file regardless of the environment being built.

### The home chosen, and why it needed no new mechanism

[`scripts/lib/gate_baseline.py`](../../scripts/lib/gate_baseline.py) has implemented the right
semantics since `IMP-0439` — *an exception suppresses the FAIL, never the report* — with a required
owner, clearing action and expiry, failing on an expired or unowned entry. It is explicitly opt-in,
five gates consult it, and `verify-pipeline-config.py` never had. So the one gate whose findings are
most often external-approval-shaped was the one gate with no accept-and-report route. It is now the
sixth consumer; **no new mechanism was written.**

| Change | Where |
|---|---|
| Imports `lib.gate_baseline`, declares `GATE = "pipeline-config"`, loads baselines in `main()` and FAILS on an unusable, unowned or expired file | [`scripts/verify-pipeline-config.py`](../../scripts/verify-pipeline-config.py#L110) |
| An expired-but-baselined note becomes an `ACCEPTED` report, printed on both paths and before the errors; plus an orphan `WARNING` when a baseline claims nothing, and a count in the PASS summary | [`check_blocked_on_staleness`](../../scripts/verify-pipeline-config.py#L536) |
| The owned, dated entry — `clears_when` names the Global Admin consent **and** the `verify-environment-access.ps1 -Env prd` proof; `expires` `2026-11-27` | [`config/gate-baselines.json`](../../config/gate-baselines.json) |
| `blocked_on_asserted` **left at 2026-08-19**, permanently expired, with the reviewer's own words and the six PRD scripts recorded in the note | [`pipeline.yml`](../../config/revitalise-grant-automation-pipeline.yml#L1773) |

`expires` is **not a prediction of when consent arrives** — nobody here controls that. It is the date
by which the *acceptance* must be retaken, and it is Phase 3's contractual milestone, the same date
`EX-001`, `EX-003` and `EX-005` use. The non-date trigger lives in `clears_when`, as the reviewer
asked.

### Deliberately NOT also an `EX-nnn` in `known-exceptions.json`

That file's own `_gate_scope_note` records technology entries as the anomaly — `EX-004` was the first
and `C-COM-010`'s wording was never widened — whereas `gate-baselines.json` was purpose-built for
technology gates and is read by this gate on every run. One decision must not carry two expiry dates
that can drift apart. The reviewer's requirement was that it not vanish from
`verify-pipeline-config.py`'s view, and an entry here satisfies that directly.

### Does the gate still report it? Yes — measured, not asserted

**2 errors → 1 error + 1 `ACCEPTED`.** Full output line:

```
ACCEPTED: environments.prd.environment_prerequisites[0]: blocked_on was asserted 2026-08-19,
15 days ago (limit 14) — ACCEPTED, not resolved. [BASELINED until 2026-11-27, owner Xander
Lykopoulos, IMP-0588 — clears when: ...]
```

It is **not** a silent PASS: the note prints on every run with its owner, expiry and clearing action.
The three guards were proven by running them, not by reading the module — an **expired** entry fails
(exit 1), an **unowned** entry fails (exit 1), and a baseline matching no finding raises the orphan
warning. `gate_baseline.py --selftest` still passes, and `Baseline.excuses` is exact-match by design,
so this entry cannot quiet any other note.

The surviving error is [`dev.verification[5]`](../../config/revitalise-grant-automation-pipeline.yml#L1371),
untouched — development-agent is fixing it properly under a separate dispatch. **The build therefore
still halts at step 2**, on that one note alone, and will go green when that dispatch lands rather
than needing anything further here.
