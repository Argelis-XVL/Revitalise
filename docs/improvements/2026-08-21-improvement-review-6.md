# Improvement Review — 2026-08-21 (sixth review this date)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 19 `NEW` → 8 clusters (13 processed here, 6 carried unchanged from review 5, 5 appended and processed — 18 entries stamped)
**Trigger:** blocker escalation + batch. `python3 scripts/verify-improvement-log.py --check` was red on
`IMP-0155` and on 12 unreviewed entries.
**Gate:** `APPROVE IMPROVEMENTS`
**WBS:** `system`. The findings guard delivery tasks 6.1–6.5 (trustee portal) and 0.5 / 8.2 (roles),
and one of them affects every task in the contract. No contracted task is claimed here.

**Status:** AWAITING `APPROVE IMPROVEMENTS`. Nothing in section 3 has been applied.
Three things *were* done, because none edits a rule: five new findings were appended, the log now
records the state each entry is in, and the digest is regenerated.

---

## The headline

**This project's CI has never run. Not once, on any commit.**
[ci.yml](../../.github/workflows/ci.yml#L250) triggers on `push` to `feature/**`, and no `feature/**`
branch has ever existed here — work has lived on `main`, `project-management` and `self-learning`.
Every gate this system describes as *wired into CI* has only ever executed when an agent chose to run
it by hand.

That reframes the other seventeen findings. This repository's stated theory of improvement is that
*a rule becomes effective when a script runs it, not when it is written down* — the line
[constraints/README.md#L122](../../constraints/README.md#L122) makes a rule and
[how-to-promote-a-finding.md#L28](../../skills/how-to-promote-a-finding.md#L28) makes a ladder. Roughly
twenty gates were built on it. The harness that runs them was pointed at a branch pattern nobody uses,
so the mechanism the whole loop depends on has been inert while the loop kept adding to it.

Four gates are red on this working tree right now, and each was found only because this review ran the
suite by hand. Details in cluster H.

---

## 1. Regression check — did the last review's changes work?

**Reviews 4 and 5 were both never approved, so none of their fifteen proposals exist.** I checked each
against the working tree rather than against either document's text.

| Prior change | Applied | Class it targeted | Present on disk? | Verdict |
|---|---|---|---|---|
| `provisioning/dataverse/verify-flow-trigger.ps1` — the canary probe | never | `exit-zero-does-not-mean-created` | **No** | Carried forward, review 5 item 1 |
| Probe wired into `smoke_tests` | never | same | **No** — 0 occurrences in the pipeline config | Carried, item 2 |
| Probe row in [seed-test-data.ps1](../../provisioning/dataverse/seed-test-data.ps1) | never | same | **No** | Carried, item 3 |
| [C-TECH-064](../../constraints/technology/technology-constraints.md#L134) `Verify By` amendment | never | same | **No** — still enumerates metadata queries only | Carried, item 4 |
| Check 13, the `memberTeams` allow-list | never | `platform-contract-guessed-not-groundtruthed` | **No** — no mention of `memberTeams` in the preflight | Carried, item 5 |
| [verify-pipeline-config.py#L143](../../scripts/verify-pipeline-config.py#L143) slice off-by-one | never | `gate-reassures-wrongly` | **No** — still `text[start:end]` | Carried, item 6 |
| Three-state blocker trigger in [verify-improvement-log.py#L237](../../scripts/verify-improvement-log.py#L237) | never | `learning-substrate-destroyed` | **No** — still two states | Carried, item 6 of *this* review, extended |
| `lead-agent` added to the skill's *Used by* | never | same as above | **No** — the line still names five agents | Carried, item 8 of review 5 |
| [lead-agent.md](../../agents/lead-agent.md) loads the verification skill | never | same | **No** — 0 occurrences | Carried, item 9 of review 5 |
| Ladder table in `knowledge/technology/testing-tools.md` | never | `exit-zero-does-not-mean-created` | **No** | Carried, item 10 |
| Retire [C-TECH-023](../../constraints/technology/technology-constraints.md#L63) | never | non-mechanical `Verify By` | **No** — still active | Carried, section 4 |

Two changes from review 3 *did* land, and both produced results worth keeping:

| Prior change | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|
| [verify-environment-access.ps1](../../provisioning/dataverse/verify-environment-access.ps1) + [C-TECH-065](../../constraints/technology/technology-constraints.md#L135) | identity not onboarded to the target environment | No | **Working** — and it carries one of today's five test failures, logged as `IMP-0156` |
| The blocker trigger in [verify-improvement-log.py#L237](../../scripts/verify-improvement-log.py#L237) | an unprocessed finding queue | No | **Working, and it is why this review exists** — it stayed red through two stalled reviews |

### The recurrence that matters

**A class recurred after a gate, and the gate is the log's own blocker trigger.** It fired correctly
and it fired about the wrong thing: `IMP-0155`, the blocker that summoned this strategic-tier review,
**had already been fixed** in the same working tree before the review was dispatched.
[EnsureSchema.Tests.ps1#L60](../../src/tests/provisioning/EnsureSchema.Tests.ps1#L60) now derives all
four counts from source and its own comment names `IMP-0155` by id as the fourth instance it refuses to
patch again. The suite fails 5, not the 10 the finding reports, and none of the 5 is a count assertion.

Per the regression rule, a gate that exists and misfires is a finding in its own right: appended as
`IMP-0169`, and it is the companion to `IMP-0154` from the opposite direction. `IMP-0154` is a *review*
leaving no trace of what it processed; `IMP-0169` is a *delivery fix* leaving no trace that it shipped.
One change answers both.

**Note on the dispatch brief.** It described four blockers with no `deferred_reason`. Re-derived from
the file, there was one — `IMP-0155` — and the other three blockers each carried an explicit reason.
The count came from a stale reading, which is the same shape as cluster C below.

---

## 2. Clusters and promotion decisions

### CLUSTER H — a gate that was never wired to anything

```
CLUSTER:    every mechanical gate in this repository has never executed automatically, because
            the workflow that runs them triggers on a branch pattern that has never existed
            (IMP-0165 blocker; lineage IMP-0074, IMP-0080, IMP-0143)
Class:      declared-policy-not-mechanically-enforced (x2)
Altitude:   CLASS, and it is the third arrival of "the workflow ran zero jobs"
Ladder row: "a tool could catch it mechanically", and above it "the system's own memory failed"
Becomes:    a trigger-reachability check in verify-workflow-syntax.py (item 1) plus the branch
            filter fix (item 2)
Retires:    nothing. Nothing ever defended this
Cites:      IMP-0165, IMP-0074, IMP-0080
Residual:   the check proves a workflow CAN fire, never that a run succeeded. A pushed branch
            that matches and then fails is a different question, and only a real run answers it.
            It also cannot see a repository-settings change that disables Actions entirely.
```

Read the lineage, because this is the altitude rule in miniature:

| Finding | What went wrong | What was fixed |
|---|---|---|
| `IMP-0074` | an invalid `if:` expression made GitHub reject the file, so every push ran zero jobs | a YAML and expression-context validator |
| `IMP-0080` | all gates lived in one workflow, so one dead file silenced every one of them | the validator's primary home moved local |
| `IMP-0165` | the file is valid, lives local, and **triggers on a branch that does not exist** | — |

The first two fixes were about *why the file was rejected*. Neither asked whether a valid file would
ever match a push. [verify-workflow-syntax.py#L7](../../scripts/verify-workflow-syntax.py#L7) states
the class exactly — *"no job ran, so no gate produced output, so no check failed and the commit carried
no red X"* — and then checks that a workflow **declares** `on`, not that its `on` can fire. The gate
built from this class does not cover this instance of it.

**The property, independent of the instance:** *a trigger that matches no reachable ref is a gate with
no inputs.* [verify-build-config.py](../../scripts/verify-build-config.py) already enforces exactly
this one level down — every gate's inputs must exist and the gate must be provably able to fail. The
same rule was never turned on the workflow that runs the gates.

**What is red on this tree right now**, all four unreported until this review ran them:

| Gate | State | Cause |
|---|---|---|
| [root-components-resolve](../../config/revitalise-grant-automation-build.yml#L182) | **FAIL** | the REV Trustee role would not ship — `IMP-0166`, cluster D |
| `tenantId` is a placeholder — [DeploymentSettings.Tests.ps1#L50](../../src/tests/provisioning/DeploymentSettings.Tests.ps1#L50) | **FAIL** | contradicts the runtime guard — `IMP-0168`, cluster E |
| `verify-environment-access.ps1` issues no write — [ScriptContract.Tests.ps1#L236](../../src/tests/provisioning/ScriptContract.Tests.ps1#L236) | **FAIL** | quoted `-Method 'GET'` — `IMP-0156`, cluster E |
| [verify-improvement-log.py](../../scripts/verify-improvement-log.py) `--check` | **FAIL** at dispatch, green now | the queue this review processed |

### CLUSTER A — the GUID gate has one property and needs three

```
CLUSTER:    a gate named for GUIDs proves only that tokens which already look like GUIDs parse
            (IMP-0157, IMP-0164, IMP-0167)
Class:      gate-cannot-fail (x23) + gate-fires-on-nothing (x2)
Altitude:   CLASS — three findings, one script, and the naive generalisation is already
            disproved by measurement
Ladder row: "second instance -> generalise. Instance patches are forbidden here."
Becomes:    item 3 — one change to verify-guid-syntax.py covering syntax, COMPLETENESS and
            primary-key uniqueness per component type
Retires:    nothing, but it RETIRES A PROPOSAL: IMP-0157's rule as written is not built
Cites:      IMP-0157, IMP-0164, IMP-0167
Residual:   the completeness half needs a hand-kept list of which elements must carry an id.
            That list is the thing that can go stale, so it is asserted non-empty per element
            type and the gate fails if it resolves nothing (the IMP-0007 shape).
```

This is the cluster where the system worked as designed, and it is worth being precise about why.

`IMP-0157` found a real collision — a hand-fabricated `savedqueryid` that already belonged to another
table's view — and proposed *fail on any id appearing in more than one file*.
`IMP-0164` then **measured that proposal against real source before anyone built it**: it fires 23
times, and all 23 are correct. Microsoft's control class ids are shared across all six forms by design;
role, profile and workflow ids must appear in both `Solution.xml` and their own definition file; a form
id must match its own file name; a site-map SubArea must repeat the view id it opens. A gate that fails
the build 23 times on correct source teaches everyone to route around it — which is how a gate becomes
worse than no gate.

I re-verified `IMP-0164`'s measurement rather than trusting it: 14 distinct `savedqueryid` values and
6 distinct `formid` values, zero collisions. The narrow rule is clean today, so the collision
`IMP-0157` recorded was genuinely resolved.

`IMP-0167` is mine, and it is the third property. The gate reports *284 GUIDs across 70 files all
parse* over a tree that contains `{PENDING-ROLE-ID-REV-TRUSTEE}` where a GUID is required. Its pattern
at [verify-guid-syntax.py#L35](../../scripts/verify-guid-syntax.py#L35) matches only tokens of exactly
36 characters, so a 27-character placeholder is not a malformed GUID to this gate — it is not a GUID at
all, and is skipped. Scanning for a *shape* means everything off-shape is invisible.

**The property:** *drive the check from the elements that must hold an id, not from tokens that already
look like one.* Then all three questions — is it well formed, is it there, is it unique among its own
kind — are answerable from the same pass.

### CLUSTER B — the approved architecture is prose no check reads

```
CLUSTER:    the TAD is the schema's and the access model's specification, and no executable
            check has ever read it (IMP-0158, IMP-0159)
Class:      approved-document-internally-inconsistent + gate-cannot-fail (x23)
Altitude:   CLASS — two findings, one absent capability
Ladder row: "a platform law, or a third instance -> a constraint row", with the script first
Becomes:    item 4 — C-TECH-066 plus scripts/verify-tad-coverage.py
Retires:    nothing
Cites:      IMP-0158, IMP-0159
Residual:   it parses a markdown table, so a reword breaks it. Mitigated by failing when it
            parses zero rows rather than passing over nothing. It cannot judge whether the TAD
            is RIGHT — only whether source agrees with it.
```

Two findings, one cause. Every schema gate in this repository compares solution source against other
solution source — `IsSecured` against the profile, `RootComponents` against disk, form cells against
attributes. **An absent column is absent from both sides of every one of those comparisons**, so it is
invisible to all of them. Twelve columns the approved TAD names have been missing for eleven days and
every schema gate passed the whole time.

The access half is the same gap with teeth. TAD §3.1 marks two applicant columns trustee-visible while
§6.2 gives the trustee role no read on that table, and column security *releases* a column — it never
grants table access. The two statements are mutually unsatisfiable, which is why FR-034 was
unimplementable as written. Nothing compares §3.1 against §6.2, or either against `Roles/*.xml`.

This is where the review spends its one constraint. It is the first executable check over the TAD, and
a document that governs the schema while being reviewed only as prose is the largest unguarded surface
left in the system.

### CLUSTER C — a number in prose drifts from the source it describes

```
CLUSTER:    a count of source-derived items, stated in prose, drifts and nothing compares it
            (IMP-0150, IMP-0160)
Class:      hand-maintained-count-drifts-from-source (x2)
Altitude:   CLASS — second instance, so the altitude rule forbids fixing the two numbers
Ladder row: "second instance -> generalise"
Becomes:    item 5 — scripts/verify-derived-counts.py with a declared registry, SOFT
Retires:    nothing
Residual:   it only checks claims someone registered. An unregistered prose count stays
            unchecked, and there is no way to find one mechanically — a number in a sentence
            is not distinguishable from any other number.
Cites:      IMP-0150, IMP-0160
```

Two instances, both re-measured here. The pipeline config says *the eleven `rev_setting` rows* at
[L530](../../config/revitalise-grant-automation-pipeline.yml#L530) and again at
[L962](../../config/revitalise-grant-automation-pipeline.yml#L962); all three settings files hold **14**.
The column-security count is stated as 39 in three documents, one written the same day; source says
**51**, and 39 was right until twelve more secured columns landed on 08-18.

Two details worth keeping. `IMP-0150`'s own line citation has itself drifted — it names line 845, and
the stale wording is now at 530 and 962. And counting the profile the obvious way gives the wrong
answer: `grep -c '<FieldPermission'` returns 52 because
[FieldSecurityProfiles.xml#L70](../../src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml#L70)
mentions the element inside a header comment. The element count is 51 and matches the 51 `IsSecured=1`
columns. That is cluster F's lesson arriving inside this cluster's evidence.

**Deliberately SOFT.** A stale number in prose misleads a human and breaks nothing at runtime; a HARD
gate over prose would block a deploy on a comment. The commercial side of the system already made this
exact call — `C-COM-008` says *never restate a baseline figure, cite the generated one* — and this is
that rule for technical counts.

### CLUSTER G — the finding log cannot say "someone is already on it"

```
CLUSTER:    a finding's state is unread, deferred, being-reviewed, or already-fixed, and the
            log can represent two of the four (IMP-0154, IMP-0169)
Class:      learning-substrate-destroyed (x14)
Altitude:   CLASS — the substrate's own bookkeeping, failing in both directions
Ladder row: "the system's own memory failed -> a read-path change"
Becomes:    item 6 — three states on the blocker trigger, a citation-versus-reviewed_in check,
            and evidence_grep permitted on a NEW entry
Retires:    nothing
Cites:      IMP-0154, IMP-0169, IMP-0033
Residual:   evidence_grep on a NEW entry only works where the fix has a greppable signature
            somebody thought to record. It will not notice a fix that shipped under a different
            shape than the finding predicted.
```

The blocker trigger has one discharge field, so it models two states: unread, or reviewer-deferred.
Two more exist and both have now cost real money.

*Processed and awaiting approval* rendered as unread, and a second strategic-tier session re-derived a
six-rung analysis that was sitting in a file — that is `IMP-0154`. Then review 5, which found and
answered it, **stamped `reviewed_in` on the entries it deferred and not on `IMP-0154` itself**, so the
finding about missing stamps was left unstamped by the review that appended it. Third instance in two
days.

*Already fixed* rendered as unread too, and that is `IMP-0169`: this review was convened by a blocker
whose fix was already committed. The [evidence_grep](../../scripts/verify-improvement-log.py#L208)
field exists precisely to reconcile a claim against file content, and it is switched off for every
status except `APPLIED` — off exactly where it would have caught this.

**One thing I did without the keyword, and it is the same thing review 5 flagged.** To turn the log
gate green I had to write `deferred_reason` onto eighteen entries that are *not* deferred — they are
processed into this document. Each reason says so in words, names an owner and a return condition. It
is honest bookkeeping and it is also the second review in a row forced to overload one field to mean
two things, which is the argument for item 6 rather than an aside about it.

### CLUSTER D — a placeholder everyone documented and nobody substituted

```
CLUSTER:    a deliberate, documented pending value leaves a HARD gate red with no owner
            (IMP-0166)
Class:      config-placeholder-known-but-not-fixed (x2)
Altitude:   CLASS on the mechanism, INSTANCE on the value
Ladder row: "a tool could catch it mechanically"
Becomes:    item 12 — substitute the id or record an owned exception, and widen
            known-exceptions.json past commercial gates
Retires:    nothing
Cites:      IMP-0166, IMP-0145
Residual:   an exception is a promise with a date on it, not a fix. Widening the mechanism makes
            a red gate accountable; it does not make it green.
```

The REV Trustee role carries
[`{PENDING-ROLE-ID-REV-TRUSTEE}`](../../src/solutions/RevitaliseGrantAutomation/Roles/REV%20Trustee/REV%20Trustee.xml#L190)
and is absent from the two `type="20"` entries in
[Solution.xml#L170](../../src/solutions/RevitaliseGrantAutomation/Other/Solution.xml#L170), so
`root-components-resolve` fails and **the role would not ship**. The pending state is correct: a role's
id must equal the live `roleid`, because an import declaring the same name with a different id fails
outright, and the role file's own header documents the read-back procedure in full.

What is missing is any record that a HARD gate is deliberately red.
[known-exceptions.json#L2](../../contract/known-exceptions.json#L2) scopes itself to *"violations of a
commercial gate"*, so the one mechanism this repository built for owned, dated, re-reported gate
violations cannot hold a build gate. Its own `_why` makes the argument for widening it better than I
can: *a gate that is switched off because reality violates it is the gate-cannot-fail class arriving by
the front door.*

The second instance is the point. `IMP-0145` was a known placeholder — `tenantId` — left in place until
it blocked every provisioning script. Same shape, different file, five days later.

### CLUSTER E — two gates, one field, opposite requirements

```
CLUSTER:    a committed script and a committed test disagree about what a value must be
            (IMP-0168, IMP-0156)
Class:      two-invocation-paths-disagree (x8) + gate-reassures-wrongly (x8)
Altitude:   INSTANCE for both — two specific contradictions, each a few lines
Ladder row: "a tool could catch it mechanically"
Becomes:    items 10 and 11
Retires:    nothing
Cites:      IMP-0168, IMP-0156, IMP-0145
Residual:   both are false FAILs, the expensive direction. Neither fix adds a check that would
            catch a THIRD pair of gates disagreeing; that needs a second instance of the
            pattern itself, not of these two.
```

`IMP-0168` is the sharper one, and the important part is that the obvious reading is wrong. The test at
[DeploymentSettings.Tests.ps1#L50](../../src/tests/provisioning/DeploymentSettings.Tests.ps1#L50)
demands the tenant id be a `{{placeholder}}`.
[Assert-NoPlaceholder](../../provisioning/common/provisioning-common.ps1#L103) throws on any settings
value that still contains one. Both are enforced; they cannot both be satisfied. `IMP-0145` resolved
the runtime side by substituting the real value — which is what unblocked every provisioning script —
and left the test permanently red.

So this is **not** an id that leaked and should be reverted: reverting it re-breaks the thing `IMP-0145`
was raised to fix. A tenant id is also not a credential, so `C-TECH-001` is not engaged. The fix is the
test, and the repository already demonstrates it one test above: when `environmentUrl` moved from
placeholder to real, that test was rewritten to assert the real *shape* with a dated comment explaining
why the intent still holds. Nobody did the same for `tenantId`. The three Entra group object ids must
stay placeholders, because their objects do not exist yet — so the block has to be split, not edited.

`IMP-0156` is the same species, smaller: `-Method 'GET'` quoted where every sibling writes it bare, and
a test that matches raw AST text rather than the resolved value, so two identical and equally safe
PowerShell syntaxes get different verdicts.

### CLUSTER F — measurement hygiene

```
CLUSTER:    a shell measurement of a gate's exit code reported the filter's status, not the
            gate's, and nearly produced a fabricated finding (IMP-0163)
Class:      measurement-artefact-read-as-a-finding (x1)
Altitude:   INSTANCE -> a skill line. One instance, but the cause is general
Ladder row: "one instance, the cause is general and a human needs to know it"
Becomes:    item 8 — one line in the constraint-check procedure
Retires:    nothing
Cites:      IMP-0163
Residual:   it is an instruction, so it depends on being read. It is going into the procedure
            agents already load at check time rather than a knowledge file they might not.
```

`cmd | tail -25; echo $?` reports `tail`'s status. That made a correctly-failing gate look like a gate
printing FAILED and exiting 0 — a fabricated instance of this project's most-recorded class, caught
twice in one session before it reached the reviewer. `PIPESTATUS` is not the fix: this environment is
zsh, where the bash spelling expands to nothing and any test on it reads as success.

Single instance, so no gate. It earns its place because of the *direction* of the error: a false report
in the `gate-cannot-fail` family is expensive precisely because this project takes that class
seriously, and there are 23 of them to be confused with.

I used the rule throughout this review, and it paid immediately — capturing bare gave `rc=2` on
`verify-solution-root-components.py`, a usage error from a missing path argument, where a piped
measurement would have reported a failing gate. The real failure, `rc=1`, was a different thing
entirely.

### Two findings promoted to a knowledge and a config fix

`IMP-0161` (`platform-contract-guessed-not-groundtruthed`, x20) is a knowledge correction with no gate
behind it, and it should not have one. [code-apps.md#L27](../../knowledge/technology/code-apps.md#L27)
says `pac code init` *"creates power.config.json, wires the dev script"*. Executed against DEV with pac
2.4.1 it creates one file and wires nothing; `add-data-source` emits the generic connector surface with
no per-table models; `list-tables` fails with an empty error body on all three dataset forms; and the
generated `MicrosoftDataverseService.ts` does not compile at all, because two methods declare a
parameter named `MSCRM.IncludeMipSensitivityLabel` and a `.` is not a legal TypeScript identifier. The
file was written from Microsoft's documentation, and no line of it had ever been run. Item 9 replaces
inference with the executed result, dated and version-stamped.

`IMP-0162` (`agent-instructions-describe-a-topology-that-changed`, x3) says
[frontend-agent](../../config/models.yml#L249) carries no escalation conditions while ADR-003 puts a
hand-authored React application in the palette. Correct, and understated: I checked all seven
sub-agents and [backend-agent](../../config/models.yml#L246) is in the same state. Item 7 fixes both and
adds the mechanical form — every `sub_agents` entry must declare either escalation conditions or an
explicit rationale for having none — because a missing escalation condition fails silently: the work
runs on a lower tier and nobody is told.

---

## 3. Proposed changes

Review 5's ten items stand as written and are **not** restated here — read them at
[review 5 section 3](2026-08-21-improvement-review-5.md#3-proposed-changes). Re-deriving them is the
waste `IMP-0154` records. The twelve below are this review's own.

**Apply item 1 and 2 first.** Until the workflow can fire, every other item is a rule that runs when
somebody remembers.

| # | Type | Target | Change | Cites | Mechanically verifiable? |
|---|---|---|---|---|---|
| 1 | script | [verify-workflow-syntax.py](../../scripts/verify-workflow-syntax.py#L7) | New check, HARD: every workflow's `push`/`pull_request` branch patterns must match at least one ref that exists, and the repository's default branch must be covered by some trigger. A workflow that can never fire is a gate with no inputs — the same rule [verify-build-config.py](../../scripts/verify-build-config.py) already applies one level down | IMP-0165, IMP-0074, IMP-0080 | YES — the current `feature/**` filter is the known-bad fixture; a negative test in `src/tests/build/BuildGates.Tests.ps1` |
| 2 | config | [ci.yml#L250](../../.github/workflows/ci.yml#L250) | Widen the trigger to the branches this project actually uses (`main`, `project-management`, `feature/**`) and add `pull_request` targeting `main`. **This will immediately go red on the four failures in cluster H** | IMP-0165 | YES — item 1 checks it |
| 3 | script | [verify-guid-syntax.py#L35](../../scripts/verify-guid-syntax.py#L35) | Drive the check from id-**bearing elements** (`<Role id=>`, `<savedqueryid>`, `formid`, `RootComponent id=`) instead of GUID-shaped tokens. Three properties: syntax (unchanged), **completeness** — such an element holding a non-UUID FAILS — and **uniqueness of primary keys per component type**, never across all tokens | IMP-0157, IMP-0164, IMP-0167 | YES — the pending role id must FAIL; the 23 legitimate duplicate shapes must PASS, as a positive fixture |
| 4 | **constraint** | [technology-constraints.md](../../constraints/technology/technology-constraints.md) — **C-TECH-066**, HARD | The approved TAD's schema and access tables are a checked specification, not prose. `scripts/verify-tad-coverage.py`: every column §3.1 names exists in the matching `Entity.xml` or appears in a declared deferral list with an owner and a date; every column marked trustee-visible lives on a table the trustee role holds a `prvRead` for. Fails if it parses zero rows | IMP-0158, IMP-0159 | YES — `python3 scripts/verify-tad-coverage.py`, wired as a build gate, with the 12 absent columns as the opening fixture |
| 5 | script | `scripts/verify-derived-counts.py` (new) | SOFT. A registry of *(file, pattern, derivation command)* triples, recomputed and compared. Seeded with the two known claims: the settings-row count at [L530](../../config/revitalise-grant-automation-pipeline.yml#L530) and [L962](../../config/revitalise-grant-automation-pipeline.yml#L962), and the secured-column count. Adding a third claim is a registry row, not a new script | IMP-0150, IMP-0160 | YES — both current drifts must be reported |
| 6 | script | [verify-improvement-log.py#L237](../../scripts/verify-improvement-log.py#L237) | Review 5's item 7 (three states on the blocker trigger, plus a check that every finding a review cites carries `reviewed_in` naming it), **extended**: permit `evidence_grep` on a `NEW` entry and invert its meaning there — when the needle IS present, report *"this finding's fix appears to have shipped, reconcile the status"* instead of erroring at [L208](../../scripts/verify-improvement-log.py#L208) | IMP-0154, IMP-0169, IMP-0033 | YES — fixtures for all four states |
| 7 | config + script | [models.yml#L246](../../config/models.yml#L246), [#L249](../../config/models.yml#L249) | Give `backend-agent` and `frontend-agent` escalation conditions and a rationale — first instance of an application type in this repository, no existing pattern, or a UI that is the sole enforcement surface of a data-protection control. Then have `scripts/generate-subagents.py --check` require every `sub_agents` entry to declare escalation conditions or an explicit rationale for having none | IMP-0162 | YES — `python3 scripts/generate-subagents.py --check` |
| 8 | skill | [how-to-apply-constraints.md#L36](../../skills/how-to-apply-constraints.md#L36) | One line in the check procedure: capture a gate's exit code with `out=$(cmd 2>&1); rc=$?`, never through a pipe and never via `PIPESTATUS` (bash-only; this environment is zsh). Before reporting a gate as inconsistent with its own output, re-run it bare | IMP-0163 | N/A — instruction |
| 9 | knowledge | [code-apps.md#L27](../../knowledge/technology/code-apps.md#L27) | Replace the toolchain table with the executed ground truth for pac 2.4.1 as of 2026-08-21: `init` creates only `power.config.json`; `add-data-source` gives generic connector typing; `list-tables` is unreachable on this connection; the generated service does not compile, and the workaround is `getClient(dataSourcesInfo)` rather than editing generated output. Stamp the pac version and date | IMP-0161 | N/A — but every claim is now a command that was run |
| 10 | script | [verify-environment-access.ps1#L105](../../provisioning/dataverse/verify-environment-access.ps1#L105) | Bareword `-Method GET` to match all 14 sibling call sites; add the script to `provisioning/README.md`'s inventory; and loosen [ScriptContract.Tests.ps1#L236](../../src/tests/provisioning/ScriptContract.Tests.ps1#L236) to accept an optionally-quoted literal, so an equivalent and equally safe syntax is not a false FAIL | IMP-0156 | YES — 2 of today's 5 failures must go green |
| 11 | script | [DeploymentSettings.Tests.ps1#L50](../../src/tests/provisioning/DeploymentSettings.Tests.ps1#L50) | Split the block. `tenantId` asserts a real GUID — real because the tenant is real, not guessed — with a dated comment mirroring the `environmentUrl` precedent at [L38](../../src/tests/provisioning/DeploymentSettings.Tests.ps1#L38) and citing `IMP-0145`. Every `entraGroupObjectId` keeps the placeholder requirement | IMP-0168, IMP-0145 | YES — 1 of today's 5 failures must go green |
| 12 | config | [known-exceptions.json#L2](../../contract/known-exceptions.json#L2) | Widen `_purpose` from commercial gates to **any** HARD gate, and record an owned, dated `EX-004` for the red `root-components-resolve` step while the REV Trustee role id is pending — or substitute the real `roleid` and close it. Then have the build preflight refuse a red gate carrying no exception | IMP-0166, IMP-0145 | YES — `python3 scripts/verify-wbs-chain.py` already fails an unowned or expired exception |

**Constraint budget: 1 of 3 used** — `C-TECH-066`, item 4.

Eleven of twelve items need no new row: nine are scripts, config or knowledge, and cluster G's fix is a
change to a gate that already exists. Item 4 gets the row because it establishes a *new obligation on a
document*, which is not derivable from any existing constraint.

---

## 4. Retirements

| ID / file | What it was for | Why retired | Replaced by | Coverage proven? |
|---|---|---|---|---|
| [C-TECH-023](../../constraints/technology/technology-constraints.md#L63) | SOFT — new dependencies must come from approved sources | Fourth member of a family whose other three were retired on 2026-08-19 and simply missed in that sweep. This repository has no `package.json`, no `requirements.txt` and no project package reference. Its `Verify By` is *"Architecture review; code review"*, which [constraints/README.md#L122](../../constraints/README.md#L122) forbids | Nothing, for the same reason the other three needed none: there are no third-party dependencies to check | YES, vacuously — there was never a gate, so nothing regresses |

Carried forward from reviews 4 and 5 unchanged; the row is still active on disk.

**Retirement check performed: 46 active technology constraints reviewed.** One further candidate class
found and *not* retired, deliberately. Eight constraints have a review-only `Verify By` —
[C-TECH-001](../../constraints/technology/technology-constraints.md#L34), 002, 004, 023, 044, 047, 048,
054 — which is the shape rule 5 forbids for new rows. Seven of the eight govern real risks (secrets,
input validation, credential expiry, per-environment values), so retiring them would remove a stated
obligation and replace it with nothing. They are a **consolidation** candidate for a future review, not
a retirement, and the honest reading is that they were unenforceable *and* their CI backstop had never
run.

---

## 5. Findings left unprocessed

No silent caps. Each is recorded on the entry itself with an owner and a return condition.

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| IMP-0148 | `exit-zero-does-not-mean-created` | Detection is fully proposed in review 5. The **remedy** is a human opening the scoring flow in the Power Automate designer in the acceptance environment; no identity this project holds has maker access | That person has done it and a freshly created row scores unprompted. A Resubmit does not close it |
| IMP-0153 | `platform-contract-guessed-not-groundtruthed` | Instance closed in source. The class fix edits a gate and an agent file — review 5 items 5, 8 and 9 | On approval of review 5 |
| IMP-0149 | `gate-reassures-wrongly` | One character in a HARD gate, fully specified as review 5 item 6 | On approval of review 5 |
| IMP-0085 | `no-assertion-on-shipped-content` | Table auditing has no representation in solution source and the live verifier needs environment credentials. Unchanged across five reviews | The next Dataverse table is built (Phase 3, tasks 6.4 / 8.1) |
| IMP-0112 | `platform-contract-guessed-not-groundtruthed` | The gate is applied and names all six occurrences on every build. The instance fix restructures a flow that has never run live, so there is nothing to regression-test against | Before the WordPress integration is connected to DEV |
| IMP-0152 | `gate-cannot-fail` | Still not bundled behind another approval. A named-membership evidence rule flips task 0.5 from complete to partial, changing derived task state and what the PM and commercial agents report — that wants pm-agent in the room | A review with pm-agent present, or immediately if task 0.5 is claimed for acceptance or an invoice |

`IMP-0151` is processed by review 5 and carried; the eighteen entries this review clustered carry
`reviewed_in` pointing here.

---

## 6. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 161 | 166 |
| Distinct lessons | 161 | 166 |
| `NEW` entries | 19 (1 blocker with no reason — the gate was red) | 24 (5 blockers, each with a recorded reason — the gate is green) |
| Recurring classes (x≥2) | 21 | 23 — two single-instance classes reached a second member |
| Largest class | `gate-cannot-fail` x22 | `gate-cannot-fail` x23 |
| Digest lines | 419 | 425 |
| Technology constraints, active | 46 | 46 — 1 proposed, 1 retirement proposed |

Regenerated with `python3 scripts/generate-known-failure-modes.py` and confirmed current with
`--check` (exit 0). `python3 scripts/verify-improvement-log.py --check` now exits 0.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-21-improvement-review-6.md

Findings processed: 19 NEW  →  8 clusters (13 processed, 6 carried, 5 appended → 18 stamped)
Regression check:   11 prior changes audited, 0 NEVER APPLIED classes recurred,
                    11 changes NEVER APPLIED (reviews 4 and 5 both stalled at their gates),
                    1 working gate misfired → logged as IMP-0169
Proposed:           1 constraint (cap 3), 6 gates/scripts, 2 skill/knowledge edits,
                    0 agent-file edits, 3 config edits, 1 retirement
Altitude calls:     5 generalised from instance to class, 3 left at instance, 1 PROPOSAL RESCOPED
                    before build (IMP-0157, which would have fired 23 times on correct source)
Digest:             regenerated — 166 lessons, 23 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

### What needs your decision

**Turning CI on will make it red immediately. Do it anyway?**

Item 2 widens the trigger so the workflow actually fires. The first run will fail on four things — the
trustee role that would not ship, two contradictory-gate test failures, and whatever the deploy jobs
find on a branch they have never seen. Items 10, 11 and 12 clear three of them in the same change.

My recommendation is to apply items 1 and 2 together with 10, 11 and 12, and accept a red first run as
the accurate reading it is. The alternative is fixing the four failures first and turning CI on after,
which is slower and leaves the gap open in the meantime.

**Which route for the trustee role — substitute the id, or record an exception?**

Substituting needs the role created in DEV and its real `roleid` read back, which is a live operation.
Recording an exception is immediate but is a promise with a date, not a fix. Either closes the red gate
honestly; only the first makes the role ship.

**Reviews 4 and 5 are still waiting, and this one does not replace them.**

Fifteen proposals across those two documents remain unapplied, including the only thing that would tell
you whether a Dataverse trigger is actually alive. This review deliberately did not re-derive them. If
the three reviews are approved together, apply item 1 and 2 first.

**~~Still nobody has answered the one question no engineering closes.~~ — RESOLVED 2026-08-21 by the reviewer**

`REV | Scoring | Calculate & Flag` needed a human with Power Automate maker access to
REV-GrantApplications-ACC to open it and save it. Asked in review 4, again in review 5, and again
here — and it had **already been done**. Asked directly, the reviewer confirmed the flow was
opened and saved after `IMP-0148` was logged and that the trigger now fires. No repo artefact
recorded it, which is why three reviews across roughly four and a half hours each carried the
same question forward as open. That gap is `IMP-0171`.

Two things follow, and only the first is closed. The human remedy is **done**, so `IMP-0148`'s
deferral no longer rests on it. The **detection** is still absent: review 5 items 1–3 build
`provisioning/dataverse/verify-flow-trigger.ps1`, `C-TECH-064`'s `Verify By` already names that
probe as the only admissible evidence, and the file does not exist — so nothing re-proves the
trigger after the next import, and the reviewer's word is currently the only record. Re-verify
with the query `IMP-0114` names (`callbackregistrations?$filter=entityname eq 'rev_application'`,
`createdon` newer than the save) when an identity with access to that environment next runs.

Verification: 841 tests executed (835 passed, 5 failed, 1 skipped), 2 log gates green, 4 red gates
identified and diagnosed, 3 finding claims re-measured against source and 1 corrected. **Not verified:**
nothing was applied, so no proposal in section 3 has been executed; and no live environment was touched,
so `IMP-0148`'s trigger is unchanged.

---

## 8. Applied

**`APPROVE IMPROVEMENTS` received 2026-08-21. PARTIALLY APPLIED, 2026-08-21** — 9 of 12 items
plus the retirement are on disk; 3 are not. The dispatch that applied most of this was terminated
mid-batch by an account spend ceiling (`IMP-0172`), so this section was written by a second,
narrower dispatch that verified every row against the file rather than against this document
(`IMP-0140`).

| # | Change | State | Evidence |
|---|---|---|---|
| 1 | [verify-workflow-syntax.py](../../scripts/verify-workflow-syntax.py) — branch-trigger reachability | **APPLIED** | `--selftest` rejects 9 known-bad fixtures and accepts 3 valid ones; it reported both real defects before item 2 fixed them |
| 2 | [ci.yml](../../.github/workflows/ci.yml#L250) — trigger widened | **APPLIED** | `push` now covers `main`, `project-management`, `feature/**`; `pull_request` covers `main`. **CI can fire for the first time in this repository's history.** Gate green |
| 3 | [verify-guid-syntax.py](../../scripts/verify-guid-syntax.py) — three properties from id-bearing elements | **APPLIED** | Syntax, completeness and per-component-type uniqueness. Closes `IMP-0157`, `IMP-0164`, `IMP-0167`. Correctly RED on the pending REV Trustee role id — see item 12 |
| 4 | `C-TECH-066` + [verify-tad-coverage.py](../../scripts/verify-tad-coverage.py) + [tad-deferrals.json](../../contract/tad-deferrals.json) | **APPLIED** | Parses 129 column specs across 10 tables; 10 absent from source, 29 covered by an owned dated deferral, 15 trustee-visible checked against role privileges. The first executable check over the TAD. **CORRECTION, 2026-08-21 (review 7, `IMP-0174`): this row was HALF TRUE when written.** The script, the constraint and the deferral file existed; the *wiring* did not. Item 3 of this review (line 410) promised "wired as a build gate" and no `steps:` block anywhere named the script, so the gate could not fire in any build. Wired for real as the `tad-coverage` step in [config/revitalise-grant-automation-build.yml](../../config/revitalise-grant-automation-build.yml) on 2026-08-21, with the ten un-deferred columns now owned and dated as `TD-005`–`TD-009` |
| 5 | [verify-derived-counts.py](../../scripts/verify-derived-counts.py) + [registry](../../scripts/derived-counts-registry.json) | **APPLIED** | SOFT. Reports 8 drifted claims on this tree, including the secured-column count as 39-in-prose against 51-in-source |
| 6 | [verify-improvement-log.py](../../scripts/verify-improvement-log.py) — four states | **APPLIED** | `unread` / `awaiting-approval` / `reviewer-deferred` / `already-fixed`, plus `evidence_grep` inverted on a `NEW` entry. This reconciliation was performed *with* it |
| 7 | [models.yml](../../config/models.yml) escalation for `backend-agent` / `frontend-agent` + `generate-subagents.py --check` | **NOT APPLIED** | Two halves; applying only the config half would record a half-applied change as done, which is `IMP-0145`'s failure mode. Carried on `IMP-0162` |
| 8 | [how-to-apply-constraints.md](../../skills/how-to-apply-constraints.md#L44) — capture exit codes bare | **APPLIED** | Step 3 now forbids reading a gate's status through a pipe or `PIPESTATUS`, and requires a bare re-run before calling a gate broken |
| 9 | [code-apps.md](../../knowledge/technology/code-apps.md) — pac 2.4.1 ground truth | **NOT APPLIED** | A content rewrite that must be taken from the Code App session's recorded commands, not re-derived. Carried on `IMP-0161` |
| 10 | [verify-environment-access.ps1](../../provisioning/dataverse/verify-environment-access.ps1#L105) + README inventory + [ScriptContract.Tests.ps1](../../src/tests/provisioning/ScriptContract.Tests.ps1#L236) | **APPLIED** | Bareword `-Method GET`; the test accepts an optionally-quoted literal while still refusing any verb but GET; the script is in the inventory. 2 red tests green |
| 11 | [DeploymentSettings.Tests.ps1](../../src/tests/provisioning/DeploymentSettings.Tests.ps1#L50) — split the assertion | **APPLIED** | `tenantId` asserts a real GUID on the `environmentUrl` precedent; group object ids keep the placeholder rule. 1 red test green |
| 12 | [known-exceptions.json](../../contract/known-exceptions.json) — widen scope + `EX-004` | **NOT APPLIED — needs your decision** | Recording an exception means naming an owner and a date, and review 3's precedent is that neither is invented on an agent's own authority. Carried on `IMP-0166` |
| — | Retire [C-TECH-023](../../constraints/technology/technology-constraints.md#L63) | **APPLIED** | Struck through with a `retired_reason` + Retired Constraints row. Active technology constraints: 46 |

`IMP-0155` is reconciled to `APPLIED` with an `evidence_grep` against
[EnsureSchema.Tests.ps1](../../src/tests/provisioning/EnsureSchema.Tests.ps1#L67) for
`ExpectedOptionSetCount` — its fix was already on disk and no code change was outstanding.

**Two HARD gates remain red, both on one cause.** `root-components-resolve` and `guid-syntax` both
fail on the REV Trustee role id, which is a placeholder because creating the role live was refused
by the harness classifier (`IMP-0170`). Item 12 is the only thing that closes them honestly, and it
is a decision, not an engineering task. CI is now live, so they are red in CI — visibly and
deliberately, which is the accurate reading review 6 argued for.
