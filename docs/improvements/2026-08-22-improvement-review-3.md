# Improvement Review 11 — 2026-08-22

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 19 unread `NEW` → 4 clusters (15 pre-existing + 4 appended by this review)
**Trigger:** reviewer keyword, dispatched by lead-agent; four unread blocker findings and a batch of 32
**Gate:** `APPROVE IMPROVEMENTS`
**WBS:** `system`. The findings guard delivery tasks 6.1–6.5 (the Trustee Review Portal). No contracted task is claimed here.

**Status:** ~~AWAITING `APPROVE IMPROVEMENTS`. Nothing in section 4 has been applied.~~
**APPROVED and APPLIED 2026-08-22 — items 1, 3, 4 and 5. Item 2 is HELD on an open reviewer decision.** See section 10.

---

## The headline

**Review 10 was approved and applied. Its own status header says the opposite, and the header is wrong.**
[Line 9](2026-08-22-improvement-review-2.md#L9) says *"Nothing in section 3 has been applied"*;
[line 460](2026-08-22-improvement-review-2.md#L460) says *"APPROVE IMPROVEMENTS received … All of section 3
applied"*. I verified the working tree rather than either claim: all four items are on disk. Do not re-approve
review 10, and do not let this review's existence suggest its work is outstanding.

**Review 10's knowledge rewrite drew five corrections within hours, because it was written from
documentation while the tool it documents sat installed on this machine.** It stated *"`pa` is not installed
on this machine"* and graded itself documentation-only. The CLI was installed 34 minutes before that file was
saved. Fifteen minutes of `--help` calls this session answered three questions review 10 had to leave open.

**That executed pass produced new information on the stuck Trustee Portal blocker, which is the most
valuable thing here.** The portal's Dataverse calls fail with *"Invalid organization URL 'null' provided"*,
and the standing conclusion across three findings was: stop guessing, raise a Microsoft ticket, and do not
re-run the data-source command because it is a confirmed no-op. The replacement CLI takes an explicit
`--org-url` flag and reaches connection metadata through a different command group. That is the "new
information" bar those findings themselves set.

**The altitude call, stated once.** A prose fix to this knowledge file has now failed twice in two days. This
review does not write a third one and stop there — it proposes the gate that makes the file's machine-state
claims checkable, and rewrites the content from executed output.

---

## 1. Scope — what this review processes, and what it must not touch

**The dispatch asked for all 32 open findings. Processing 32 would have been the wrong answer, and
[the log gate](../../scripts/verify-improvement-log.py#L116) says why.** Its state breakdown splits them:

| State | Count | What it means | This review |
|---|---|---|---|
| unread | 15 | nothing records that anyone has looked at these | **processed in full** |
| appended here | 4 | this session's own findings | **processed in full** |
| awaiting-approval | 14 | already analysed; parked at reviews 5, 6, 8 and 9 | **not touched** |
| reviewer-deferred | 3 | a recorded `deferred_reason`, accepted | **not touched** |

Re-deriving the fourteen is the exact cost [IMP-0154](../../logs/improvement-log.jsonl) recorded — a
duplicated strategic-tier dispatch five hours after the first one. The remedy for a parked review is a
keyword against the document it names, never a second review of the same finding. Section 6 names each
document.

---

## 2. Regression check — did review 10's changes work?

**Review 10 is the first review in five whose changes actually landed, so this is the first real audit in
days.** I verified each of its four items against the working tree, not against its table.

| Prior change | On disk? | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| Item 1 — [code-apps.md](../../knowledge/technology/code-apps.md#L24) rewritten for the new CLI | **YES** (+139 lines) | `platform-contract-guessed-not-groundtruthed` | **YES — five times, within hours** | **Wrong altitude.** A prose rewrite of this file has now failed twice. Escalated to a gate in item 3 |
| Item 2 — digest routing for two classes | **YES** ([line 83](../../scripts/generate-known-failure-modes.py#L83)) | `learning-substrate-destroyed` | NO | **Worked.** The environment-toggle lesson now lands in *Before you hand-author a platform artefact* instead of Unrouted |
| Item 3 — [C-TECH-048](../../constraints/technology/technology-constraints.md#L90) names the mechanism, not the tool | **YES** | `platform-fact-groundtruthed` | NO | **Worked**, and it is already load-bearing: this review's executed pass confirms both named tools exist |
| Item 4 — citation position decides meaning in the log gate | **YES** ([line 603](../../scripts/verify-improvement-log.py#L603)) | `gate-fires-on-nothing` | NO | **Worked, and proved itself on me.** It correctly rejected my own nineteen stamps this session as unresolvable until this document existed |

**The one recurrence, and what it means.** Five findings landed against the file review 10 rewrote:
the "not installed" claim was false; the superseded-tool framing was stronger than the evidence; the
vendor's own recommended dev-loop plugin was absent; the SDK's actual export surface went unrecorded; and an
advertised vendor plugin link is dead. Four of the five were answerable from this machine at the moment the
file was written.

**Per my own regression rule, a recurrence after a prose change is evidence of wrong altitude, so the fix
moves to a gate.** Item 3 is that gate.

**Reviews 8 and 9 remain unapplied.** Their items are unaffected by this review and are still the
largest block of accepted-but-absent work in the repository. This review adds five items to that pile only
if it is approved and they are not.

---

## 3. Clusters and promotion decisions

```
CLUSTER A: the toolchain knowledge file  (x7: IMP-0199, IMP-0200, IMP-0201, IMP-0202,
                                          IMP-0203, IMP-0206, IMP-0207)
Altitude:  CLASS for the read path, INSTANCE for the content — and this time the class half is
           the point. Three of the seven are `platform-contract-guessed-not-groundtruthed`
           (x25) and the file has now been prose-fixed twice in two days. skills/how-to-promote-
           a-finding.md line 44 forbids a third instance patch, and a third prose rewrite is
           exactly that.
Ladder row: "A tool could catch it mechanically" → scripts/ + a build gate. Plus "One instance,
           but the cause is general and a human needs to know it" → knowledge/, for content
           that no gate can hold (framing, a dead vendor link, a recommended plugin).
Becomes:   (1) scripts/verify-toolchain-claims.py + a build gate — the file's claims about
               locally-installed tooling are compared against the machine;
           (2) the Toolchain section rewritten from EXECUTED output (`pa <group> --help`), not
               from documentation, correcting the "not installed" line and the mislabelled
               verification grade;
           (3) one row in skills/how-to-verify-a-platform-contract.md making an npm-distributed
               CLI/SDK explicitly closable offline.
Retires:   nothing on disk. Review 10's item 1 is SUPERSEDED in part — its content stands except
           where execution contradicted it, and every correction is named in item 1 below rather
           than silently overwritten.
Cites:     IMP-0199, IMP-0200, IMP-0201, IMP-0202, IMP-0203, IMP-0206, IMP-0207
Residual:  The gate cannot check prose. It will catch a false "is/is not installed" claim, a
           stale package version and a command name the CLI does not have. It cannot catch an
           overstated framing (IMP-0202), a vendor plugin advertised but unpublished (IMP-0203),
           or a vendor-recommended package nobody surveyed (IMP-0201). Those three stay content,
           and they are the reason item 1 exists alongside item 3 rather than instead of it.
```

```
CLUSTER B: the "Invalid organization URL 'null'" chain  (x6: IMP-0187, IMP-0188, IMP-0189,
                                                         IMP-0190, IMP-0191, IMP-0192)
Altitude:  INSTANCE, deliberately, and I am saying so rather than promoting for the sake of it.
           Two classes are represented — `v3-does-not-imply-v4` (x8) and `platform-contract-
           guessed-not-groundtruthed` (x25) — but all six are one incident on one app, and five
           of the six have proposed_change type `knowledge`. IMP-0190's own proposed_change is
           type `none`: its author called it a one-off reasoning gap, and I agree.
Ladder row: "One instance, but the cause is general and a human needs to know it" → knowledge/.
           No gate in this repository can reach into the Power Apps host's connector resolution,
           which is what every one of these findings says in its own words.
Becomes:   knowledge content in item 1, plus a changed RECOMMENDATION: the next step is a retry
           through the new CLI before the Microsoft ticket, because `pa app add data-source`
           takes an explicit --org-url and `pa connection list-datasets`/`list-tables` is a
           different code path from the pac verbs that returned an empty {} here.
Retires:   nothing. It SUPERSEDES the standing "do not retry without new information" advice by
           supplying the new information, rather than contradicting it.
Cites:     IMP-0187, IMP-0188, IMP-0189, IMP-0190, IMP-0191, IMP-0192
Residual:  The retry may fail identically, in which case the Microsoft ticket is still the
           answer and nothing is lost but two commands. And it cannot be attempted at all until
           the signed-in-identity trap is settled — this machine's Enterprise SSO extension
           silently authenticates as a service account, so a retry from here would test the
           wrong user. That ordering is a decision, in section 7.
```

```
CLUSTER C: code app solution membership  (x2: IMP-0185, IMP-0193)
Altitude:  INSTANCE → knowledge, and the instance is now obsolete rather than fixed.
Ladder row: "One instance, but the cause is general and a human needs to know it" → knowledge/.
Becomes:   knowledge content. Both findings document a workaround for the old CLI — the push does
           not create the solution component, so a human adds it in the maker portal. Executed
           ground truth today supersedes the workaround outright: `pa app push --solution-id`
           takes the GUID explicitly, and `pa solution list` prints solution IDs, which is the
           lookup a current digest lesson says is only reachable through a FetchXML passthrough.
Retires:   one digest lesson's advice, by supersession — see section 5.
Cites:     IMP-0185, IMP-0193
Residual:  The pipeline config still passes a solution NAME to the old command. Correcting it is
           delivery work against a live app, not a rule change; review 10 made that altitude call
           and I am holding it. Named in section 6 rather than silently carried.
```

```
CLUSTER D: the C-TECH-047 blind spot  (x2: IMP-0197, IMP-0205)
Altitude:  CLASS. `gate-cannot-fail` is at x26 and this is the cheapest possible member: a HARD
           constraint whose gate greps one directory and whose Verify By is the word "Code
           review".
Ladder row: "A tool could catch it mechanically" → an existing gate's scope and patterns.
Becomes:   config/revitalise-grant-automation-build.yml's no-hardcoded-environment-values step
           extended to src/code-apps/**, plus a pattern for the connector-host shape the current
           three patterns do not match.
Retires:   nothing — the class was undefended over this directory, not defended badly.
Cites:     IMP-0197, IMP-0205
Residual:  There is a live breach today and the gate must not be written so as to pass over it:
           four occurrences of the DEV environment id and region in a tracked generated schema
           file. And power.config.json legitimately carries an environmentId — whether that is a
           breach or a sanctioned exception is a decision I cannot make, in section 7. A silent
           exclusion of that file would recreate gate-cannot-fail inside the fix for it.
```

**Why cluster B is one cluster and not two.** Its six findings span two class names but one
afternoon, one app and one error string. Splitting them by class would put the diagnosis and its
correction in different documents, and the decision they lead to is a single decision.

---

## 4. Proposed changes

**Five items. Zero new constraints.** Three are mechanical, one is content that no gate can hold, one is a
single row in a skill.

| # | Type | Target | Change | Cites | Mechanically verifiable? |
|---|---|---|---|---|---|
| 1 | knowledge | [code-apps.md](../../knowledge/technology/code-apps.md#L24) | Rewrite the Toolchain section from **executed** `pa <group> --help` output: correct the [*"not installed"* line](../../knowledge/technology/code-apps.md#L42), replace the [mislabelled grade](../../knowledge/technology/code-apps.md#L41), complete the command table and its flags, soften the superseded-tool framing, add the vendor's dev-loop plugin, record the SDK's real export surface and the dead plugin link, and answer the group-sharing question at flag level | IMP-0199, IMP-0200, IMP-0201, IMP-0202, IMP-0203, IMP-0206, IMP-0207, IMP-0186, IMP-0188 | YES — item 3's gate passes over the rewritten file, and fails over the current one |
| 2 | build-gate | [build.yml line 434](../../config/revitalise-grant-automation-build.yml#L434) | Extend `no-hardcoded-environment-values` ([C-TECH-047](../../constraints/technology/technology-constraints.md#L89)) from `src/solutions/` only to `src/code-apps/**` as well, and add the connector-host pattern to the [three existing patterns](../../config/revitalise-grant-automation-build.yml#L436) | IMP-0197, IMP-0205 | YES — and it must go RED on the current tree before it is accepted, on the four occurrences named in section 3 |
| 3 | script | `scripts/verify-toolchain-claims.py` (new) + a build gate | Compare a knowledge file's machine-state claims against the machine: *"X is / is not installed"* against the global npm list and the resolved binary; *"this project is on version N"* against the package's own manifest; every `pa …` / `pac …` command token in a table against that CLI's own help output when it is present | IMP-0199, IMP-0200, IMP-0206, IMP-0207 | YES — `--selftest` with a known-bad fixture per claim shape, and it must fail on [line 42](../../knowledge/technology/code-apps.md#L42) as it stands today |
| 4 | script | [verify-improvement-log.py](../../scripts/verify-improvement-log.py#L603) | Fail when a review document carries both an *Applied* section heading and a status line still claiming AWAITING. One document, two moments, and the header is always the stale half | IMP-0204, IMP-0181 | YES — [review 10](2026-08-22-improvement-review-2.md#L9) is the fixture, and it must go red until its header is corrected |
| 5 | skill | [how-to-verify-a-platform-contract.md line 61](../../skills/how-to-verify-a-platform-contract.md#L61) | State that first-party documentation is **E2 with no V-level equivalent**, and add one row: for an npm-distributed CLI or SDK, the installed package's `--help` and its own `.d.ts` files outrank the documentation, so E2 is never the resting place for a toolchain claim about a tool that installs in one command | IMP-0199, IMP-0200, IMP-0201, IMP-0207 | PARTLY — item 3 enforces the toolchain half; the grading vocabulary stays prose |

**Constraint budget: 0 of 3 used.** No new constraint is proposed and none is needed: item 2 fixes an existing
HARD rule's gate, and item 5 fixes an existing HARD rule's vocabulary. I considered and rejected a rule of the
shape *"a knowledge file must state its evidence level per section"* — item 3 enforces the part that matters
mechanically, and the rest would be a comment.

### Item 1 — what execution corrected, line by line

This is the evidence for item 1, not a summary of it. Every row was produced by running the command on this
machine today against `pa` 1.0.0.

| Current text in the applied file | Executed ground truth |
|---|---|
| [*"`pa` is not installed on this machine"*](../../knowledge/technology/code-apps.md#L42) | Installed: `@microsoft/power-apps-cli@1.0.0`, binary at `/Users/xvl/.npm-global/bin/pa`. It is a **PATH gap**, not a missing install — that directory is not on PATH, so a bare `which pa` reports nothing |
| [*"Verification level: documentation only (V2)"*](../../knowledge/technology/code-apps.md#L41) | Not a valid grade. [V2 means *"Does it package?"*](../../skills/how-to-verify-a-platform-contract.md#L127); documentation is [E2, status ASSUMED](../../skills/how-to-verify-a-platform-contract.md#L61). The command surface below is now **executed**, and the runtime behaviour remains E2 |
| *"`pac solution list` does not show solution ids; read one with `pac env fetch`"* | `pa solution list` lists solutions *"including their solution ID"*, with `--search` and `--json`. The FetchXML workaround is superseded |
| `pa app add data-source` — four flags listed | Also takes `-u, --org-url`, `-d, --dataset`, `--procedure` and `-s, --solution-id`. **The `--org-url` flag is why cluster B's recommendation changed** |
| [*"group support is unverified"*](../../knowledge/technology/code-apps.md#L166) on `pa app share` | The tool's own help: *"Comma-separated email addresses or Entra object IDs. Object IDs may identify users or service principals."* Groups are unnamed at flag level — so review 10's decision to keep group sharing as a maker-portal step is now supported by the tool, not just by silence in the docs |
| No connection-inspection commands listed | `pa connection list-datasets` / `list-tables` / `list-procedures` / `list-references` exist as a connection-scoped group — a different code path from the `pac code list-tables` that returned an empty `{}` here |
| `pa app init` — two flags listed | Also `--app-type` (CodeApp\|MobileApp), `--build-path` (default `./dist`), `--file-entry-point`, `--app-url`, `--logo-path`. The last three matter for a hand-authored Vite project like this one |
| Not mentioned | `@microsoft/power-apps-vite@1.0.2` is a real published package. The portal's [dev script](../../src/code-apps/trustee-review-portal/package.json#L8) runs two processes under `concurrently` where the vendor's own plugin needs one |
| Not mentioned | `@microsoft/power-apps@1.3.0`'s `./app` export surface is exactly `setConfig`, `getContext` and two types — read from the installed `dist/app/index.d.ts`. This closes the initialisation half of the [A-TR-12 assumption](../../src/code-apps/trustee-review-portal/src/PowerProvider.tsx#L11): there is no other initialiser to call |

---

## 5. Retirements

**I checked, and there is no clean constraint retirement — but there is one real supersession, and I am
naming it rather than letting it sit as a contradiction.**

A current digest lesson tells the next agent that a solution's real id is unreadable from `pac solution list`
and must come from a FetchXML passthrough. `pa solution list` prints it. Left alone, the digest would carry
advice the toolchain has outgrown, and the digest is generated — so the correction belongs in item 1's
knowledge content, where the reader of that lesson will meet it. Nothing is deleted.

**Two candidates I am deliberately not taking, both for the same reason.**
[C-TECH-048](../../constraints/technology/technology-constraints.md#L90)'s `Verify By` is *"Code review"*,
which by this project's own rule is a comment rather than a verification — review 9's item 4 already proposes
the grep that would flag it, and fixing it here would duplicate that at a worse altitude.
[C-TECH-001](../../constraints/technology/technology-constraints.md#L34),
[C-TECH-002](../../constraints/technology/technology-constraints.md#L35) and
[C-TECH-044](../../constraints/technology/technology-constraints.md#L86) remain the standing consolidation
candidate. The Retired table stands at 10 rows against 47 active constraints, which is a healthier ratio than
the zero this obligation was written for.

**The honest note on sweeps:** reviews 8, 9 and 10 each reviewed the active technology constraints within the
last 48 hours and found no clean candidate. A fourth pass at strategic-tier cost would return the same answer,
and I am reporting that rather than performing it.

---

## 6. Findings left unprocessed

No silent caps.

| Finding(s) | Count | Why not processed here | What closes it |
|---|---|---|---|
| IMP-0148, IMP-0178 | 2 blockers | Analysed by review 8 and parked at its gate | `APPROVE IMPROVEMENTS` against [review 8](2026-08-21-improvement-review-8.md) |
| IMP-0182 | 1 blocker | Analysed by review 9 and parked at its gate | `APPROVE IMPROVEMENTS` against [review 9](2026-08-22-improvement-review.md) |
| IMP-0162, IMP-0166, IMP-0173, IMP-0176, IMP-0177, IMP-0179, IMP-0180, IMP-0181, IMP-0183, IMP-0184, IMP-0198 | 11 | Analysed by reviews 5, 6, 8 and 9; parked at those gates. Re-deriving them is what IMP-0154 recorded the cost of | the keyword against the document each names |
| IMP-0085, IMP-0112, IMP-0152 | 3 | Reviewer-deferred with a recorded reason; the log gate accepts them as reviewed deferrals | a reviewer decision to revisit |
| IMP-0190 | 1 | **Processed and closing as a log note only.** Its own `proposed_change` type is `none` — a one-off reasoning gap, not a missing gate. The promotion ladder's top row is "Nothing. It stays a log note", and this is that row | already closed; it will move to `APPLIED` with no artefact on approval |

**Delivery work this review deliberately does not do**, holding review 10's altitude call that a config or
script edit against a live app is delivery, not a rule change: the
[pipeline's push step](../../config/revitalise-grant-automation-pipeline.yml#L677) passes a solution *name*
where the replacement command takes only a GUID; the portal's
[dev script](../../src/code-apps/trustee-review-portal/package.json#L8) is a migration candidate for the
vendor plugin; and [share-apps.ps1](../../provisioning/dataverse/share-apps.ps1#L174) needs a header note that
its code-app branch is superseded for users and service principals but not for groups. All three are named in
item 1's content so the next agent to touch them is told.

---

## 7. What you need to decide

**Which review do you actually want applied?**

Three documents are now parked at gates: review 8, review 9, and this one. That is five items here on top of
theirs, and the pile is the reason this review proposes five items instead of twelve.

My recommendation is to approve them oldest-first, because review 9's item 5 — the activation-order fix for
this very agent — is what makes each subsequent review cheap, and it has been proposed and unapplied for two
days. This review followed it manually, which is the only reason it processed nineteen findings instead of
thirty-six.

**Should the portal's data source be re-bound through the new CLI before the Microsoft support ticket?**

My recommendation is yes, and this is the item with real money behind it. Three findings concluded the
*"Invalid organization URL 'null'"* failure is a platform defect and set an explicit bar for any further local
attempt: new information. There is now new information — an explicit `--org-url` flag on the replacement
command, and a connection-inspection command group that the old CLI's equivalent could not reach on this
connection. It costs two commands and touches nothing live until a push.

The counter-argument is that this is a fourth local attempt on a defect already escalated once, and the ticket
has been deferred before.

**This is blocked by something else, and the order matters.** The retry has to be performed as the *right*
signed-in user, and on this machine an Enterprise SSO extension silently authenticates every Microsoft
sign-in — incognito included — as this project's provisioning service account. A retry from here would test
the wrong identity and produce a result nobody should trust. Settle the identity first, or run the retry from
a different device.

**Is a Code App's `power.config.json` a hardcoded-environment-values breach, or a sanctioned exception?**

This decides how item 2 is written, so I need it before that gate can be finished honestly. The file now
carries two DEV-specific values in tracked source: the environment id, and — as of the current working tree —
a real app id.

If it is a breach, the two keys are templated per environment and the gate fails on them. If it is a
sanctioned manifest, it goes in `contract/known-exceptions.json` with an owner and an expiry. What it must not
be is silently excluded from the gate's scope, which would put a gate that cannot fail inside the fix for a
gate that could not fail.

My recommendation is the exception route, with an expiry: both `pa app init` and `pa app push` take the
environment on the command line, so the file's value is a default rather than a binding, and templating it
buys little today.

---

## 8. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 200 | **204** — four appended by this review |
| Distinct lessons | 200 | **204** |
| Recurring classes (x≥2) | 24 | 24 — no new class name recurs; four existing counts rise |
| Entries in `unread` | 15 | **19**, all nineteen now stamped to this document |

Four class counts move: `gate-cannot-fail` 25 → 26, `learning-substrate-destroyed` 15 → 16,
`platform-fact-groundtruthed` 4 → 5, `gate-reassures-wrongly` 8 → 9. No new class name was invented — each of
the four appended findings reuses an existing one, because a near-duplicate class name defeats the counting
mechanism that drives the altitude rule.

**One new lesson routes to *Capabilities established in earlier sessions*** — the executed `pa` command
surface, flagged `capability: true`, because it is a thing that works and would otherwise be rediscovered by
the next session reading *"not installed on this machine"*.

Regenerated with `python3 scripts/generate-known-failure-modes.py`; `--check` confirms current at 204 entries.

### Bookkeeping done, and what it deliberately does not claim

`reviewed_in` is stamped on all nineteen entries this document owns: the fifteen that were unread, and the
four appended here. Statuses stay `NEW` — nothing is marked `APPLIED` before the keyword.

**The four blocker findings in cluster B are no longer left triggering.** Review 10 deliberately left them
unstamped so that the trigger would fetch them a dispatch; that dispatch is this document, so the accurate
encoding is now a stamp pointing at it. The log gate's blocker trigger will move them from *unread* to
*awaiting-approval*, which is what they are.

**The three pre-existing warnings are untouched and correct.** IMP-0148, IMP-0181 and IMP-0182 are cited by
later reviews than the one they are stamped to. Each is parked at a gate for a document that handles it in
full, and moving a stamp to a document that handles only part of a blocker would point the gate at the wrong
place. Review 10's reasoning on this holds and I am not overriding it.

---

## 9. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-22-improvement-review-3.md

Findings processed: 19 NEW (15 unread + 4 appended)  →  4 clusters
                    of 36 open: 19 processed, 14 parked at other gates, 3 reviewer-deferred
Regression check:   4 prior changes audited (review 10, the first applied in five reviews),
                    1 class recurred after a prose change → escalated to a gate
Proposed:           0 constraints (cap 3), 3 gates/scripts, 1 knowledge rewrite,
                    1 skill edit, 0 agent-file edits, 0 retirements (1 supersession)
Altitude calls:     1 generalised from instance to class (toolchain claims → a gate),
                    2 held at instance with reasons, 1 closed as a log note
Digest:             regenerated — 204 lessons, 24 recurring classes, 4 counts raised

IMPROVEMENT LOG: 4 entries appended — IMP-0204, IMP-0205, IMP-0206, IMP-0207
                 | digest regenerated: YES

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

**Verification performed.** `pa` 1.0.0 executed on this machine: 6 command groups and 8 individual commands
via `--help`, all quoted output taken from that run. Review 10's four applied items confirmed present in the
working tree by diff and grep, not by reading its table. The C-TECH-047 breach confirmed by
`git ls-files src/code-apps | xargs grep` — 4 occurrences of the DEV environment id and region in one tracked
file, and the gate's own command confirmed to scan only `src/solutions/`. The SDK export surface read from the
installed `dist/app/index.d.ts`. `@microsoft/power-apps-vite@1.0.2` confirmed published. Digest current at 204
entries. Every line-link in this document was grepped against the file it names.

**Not verified.** No `pa` command was executed against a live environment — only `--help`, so the command
surface is executed ground truth and every runtime behaviour claim remains E2. Whether `pa app share` accepts
a group object ID is still untested; the tool's help excludes groups from its own description, which is
stronger evidence than review 10 had but is not a test. The dead vendor plugin link was not re-checked this
session; it is taken from the finding that recorded it. And no item in section 4 has been applied.

---

## 10. Applied

`APPROVE IMPROVEMENTS` received 2026-08-22, with an explicit instruction: apply reviews 9 and 8
first, then this document's items **1, 3, 4 and 5**, and **hold item 2**.

| # | Change | Where | Entries moved to APPLIED |
|---|---|---|---|
| 1 | `code-apps.md` Toolchain rewritten from **executed** `pa --help` output: full command surface, the PATH-gap correction, the softened deprecation framing, the SDK's real export surface, `power-apps-vite`, the dead vendor plugin, and a 5-step ordered diagnostic for *"Invalid organization URL 'null'"* | [code-apps.md](../../knowledge/technology/code-apps.md#L26) | IMP-0185, IMP-0186, IMP-0187, IMP-0188, IMP-0189, IMP-0191, IMP-0192, IMP-0199, IMP-0200, IMP-0201, IMP-0202, IMP-0203, IMP-0206 |
| 1b | **A-TR-12 CLOSED** from the installed SDK's own `.d.ts` — E2 guess to E1, in the register, the summary's open-items list, and `PowerProvider.tsx`'s header. Typecheck clean, 228/228 portal tests pass | [dev summary](../../docs/development/revitalise-grant-automation-dev-summary.md#L4867) | IMP-0199 |
| 3 | `verify-toolchain-claims.py` (new) + build gate `toolchain-claims` — install, version and command-name claims in `knowledge/technology/*.md` checked against the machine. 9 selftest fixtures; **44 live claims checked, all hold** | [build.yml](../../config/revitalise-grant-automation-build.yml#L195) | IMP-0200, IMP-0206 |
| 4 | A review carrying an *Applied* section may no longer claim AWAITING. Found **four** such documents, not one | [verify-improvement-log.py](../../scripts/verify-improvement-log.py) | IMP-0204 |
| 5 | Documentation is **E2 with no V-level**; and for a tool that installs in one command, E2 is never the resting place — four offline E1 sources tabulated | [how-to-verify-a-platform-contract.md](../../skills/how-to-verify-a-platform-contract.md#L67) | IMP-0207 |
| — | Closed as a **log note only**, no artefact, per its own `proposed_change.type: none` | — | IMP-0190 |

**Item 2 HELD, and this is the reason rather than an omission.** Extending the
`no-hardcoded-environment-values` gate to `src/code-apps/**` cannot be finished honestly until
the reviewer decides whether `power.config.json`'s `environmentId` and `appId` are a
`C-TECH-047` breach or a sanctioned exception — section 7 said so before the gate was sent, and
the answer was *"not sure yet"*. Writing the gate to silently skip that file would put a
gate-that-cannot-fail inside the fix for one, which is the defect the item exists to close.

`IMP-0197` and `IMP-0205` therefore stay open, each carrying a `deferred_reason` recording that
item 2 is **drafted and blocked on that single decision**, so the next pass inherits the analysis
instead of re-deriving the cluster. **The live breach is unchanged and still invisible to the
gate:** four occurrences of the DEV environment id and region in
`src/code-apps/trustee-review-portal/.power/schemas/commondataserviceforapps/commondataserviceforapps.Schema.json`.

**Cluster B (the portal retry) was explicitly deferred by the reviewer** — *"process the
approvals first"* — and nothing here acts on it. Note what arrived while this was being applied:
a concurrent session appended **IMP-0208**, reporting that `pa app add data-source -u <org-url>`
**succeeded** against DEV and produced real per-table generated files. That is this review's
cluster-B recommendation confirmed, and it is an **unread `blocker` needing its own dispatch** —
it is not processed here.

**Entries rejected:** none.
