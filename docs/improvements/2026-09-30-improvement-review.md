# Improvement Review — 2026-09-30 (1): the precise secure-data check

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 3 `NEW` → 1 clusters (1 reviewer-deferred, 1 unread, plus 1 logged by this review from what its measurement showed)
**Trigger:** reviewer request. Xander Lykopoulos authorised the list of personal columns that the 2026-09-28 review left undecided, and asked for the check that list makes possible.
**Gate:** `APPROVE IMPROVEMENTS`
**Status:** ~~DRAFT. Parked at the gate, nothing applied.~~ **APPROVED 2026-09-30; changes 1–6 HELD BACK by this review's own sequencing condition** (corrected 2026-09-30 07:10). `APPROVE IMPROVEMENTS` from Xander Lykopoulos, relayed by lead-agent. The other session's secured flows are still uncommitted, and decisions 1–4 are unanswered. What was and was not applied is in section 8.
**WBS:** system work, `wbs:system`. The flows it measures belong to `wbs:3.2,3.3` (the two DocuSign acceptance flows) and `wbs:4.2,4.3` (intake). No change here is billable.

---

## Summary

With your list, a check can now say exactly which flow steps must hide their data from run history. It is precise: on the last commit it flags the 4 reads that return a referee's or applicant's name or contact details, and nothing else. On the working tree it flags nothing, because another live session secured those 4 reads between 06:45 and 06:46 this morning. That work is not committed yet.

**Waiting on you:** `APPROVE IMPROVEMENTS`, plus four decisions below. The check can be switched on as a hard build step only once that other session's flow changes are committed. Before that, it would stop the build on the 4 reads.

## What this review proposes

1. **Add the check to the flow-definition gate the build already runs** ([engine script, check list at L47](.engine/scripts/verify-flow-definition-language.py#L47); [build step L648](config/revitalise-grant-automation-build.yml#L648)). The rule: any Dataverse list, create or update step that selects, filters on or writes a listed column must set `secureData`, for the part of the step that carries the value. The check's logic goes into the shared engine, since it holds for any client. Your list stays in this repository, following the pattern already used for check 7's exceptions ([wrapper L124](scripts/verify-flow-definition-language.py#L124)).

2. **Record your list as data, in a new file next to the special-category register** (`constraints/domain/personal-data-columns.yml`; [register L116](constraints/domain/special-category-register.yml#L116)). It holds five personal columns, the two you ruled not personal, and your decision in your own words with its date. The in-flight finding suggested adding these columns to the special-category register. This review does not, because every row in that register is recorded as Article 9 data and is barred from scoring. A referee's phone number is personal data, not special-category data.

3. **Point the personal-data-in-logs rule at the check** ([C-DOM-004 L37](constraints/domain/domain-constraints.md#L37)). Today the rule is checked against the error-log table only. Run history is a log too ([power-automate.md L317](knowledge/technology/power-automate.md#L317)), and this check covers it.

4. **Correct the knowledge line that says no such check exists** ([power-automate.md L336](knowledge/technology/power-automate.md#L336)). The line will name the check and what it does not cover: row triggers, and steps that consume a secured value later in the flow.

5. **Close the risk acceptance for the two DocuSign flows once the secured flows are committed** ([EX-004 L29](contract/known-exceptions.json#L29)). Its scope and the reasons are in the next section.

### EX-004's scope, measured

| Step EX-004 names | Returns a listed column? | Last commit | Working tree (06:50) |
|---|---|---|---|
| Create Envelope, [Get the application](src/solutions/RevitaliseGrantAutomation/Workflows/REVAcceptanceCreateEnvelope-8F1C2A44-1006-4B7A-9E21-0A1B2C3D4E06.json#L97) | yes: referee name, email, phone | not hidden | hidden |
| Create Envelope, [Get the applicant](src/solutions/RevitaliseGrantAutomation/Workflows/REVAcceptanceCreateEnvelope-8F1C2A44-1006-4B7A-9E21-0A1B2C3D4E06.json#L128) | yes: full name, email | not hidden | hidden |
| Reminders, [Get the application](src/solutions/RevitaliseGrantAutomation/Workflows/REVAcceptanceRemindersEscalation-8F1C2A44-1007-4B7A-9E21-0A1B2C3D4E07.json#L176) | yes: referee name | not hidden | hidden |
| Reminders, [Get the applicant](src/solutions/RevitaliseGrantAutomation/Workflows/REVAcceptanceRemindersEscalation-8F1C2A44-1007-4B7A-9E21-0A1B2C3D4E07.json#L207) | yes: full name | not hidden | hidden |
| Reminders, [List overdue grants](src/solutions/RevitaliseGrantAutomation/Workflows/REVAcceptanceRemindersEscalation-8F1C2A44-1007-4B7A-9E21-0A1B2C3D4E07.json#L139) | **no.** It reads the grant reference (`GR-yyyy-nnnnn`, pseudonymous by design), the envelope id and the issue date | not hidden | not hidden, correctly |

So EX-004 lists five steps, and under your list four of them are personal. Once the other session's change is committed, it covers an exposure that no longer exists in source. Three things stay true after that:

- **Environments that already ran these flows keep up to 28 days of run history with the values in it.** Nothing in source changes that. The fix takes effect in an environment only when a build carrying it is imported there.
- **Its reason carries over a claim that does not fit the new scope.** It says fixing these steps "is named by no WBS task, so it is a change-order decision". That was written for the intake and scoring flows. WBS [3.2](contract/wbs.json#L614) and [3.3](contract/wbs.json#L631) are these two DocuSign flows, and the in-flight fix is tagged to them. This review routes that question to commercial-agent and does not decide it.
- **No gate has ever observed EX-004** ([_gate_scope_note L101](contract/known-exceptions.json#L101)). Its matching text cannot fire against the gate that reads this file, so its expiry date has been its only control. When the new check lands, the gate EX-004 names exists for the first time. The proposal is to close EX-004 rather than teach the check to read it, because an exception covering nothing is a waiver waiting for the next unrelated defect.

### Elements added

| Element | What it is |
|---|---|
| Check 11 in the engine's flow-definition gate | The rule in item 1, with a synthetic self-test for each case (section 3, row 1) |
| `constraints/domain/personal-data-columns.yml` | Your list, as data the check reads |
| A real-corpus self-test in the instance wrapper | Removes `secureData` from one real read in memory and asserts that check 11 then fails |

### Elements changed

| Element | Change |
|---|---|
| [C-DOM-004](constraints/domain/domain-constraints.md#L37) `Verify By` | Adds check 11 of `flow-definition-language` |
| [power-automate.md L336](knowledge/technology/power-automate.md#L336) | "No gate checks it" becomes the check, plus what it does not cover |
| [EX-004](contract/known-exceptions.json#L29) | Moved to `_closed_exceptions`, with the measurement above as the reason |

## What is still open

**The secured flows are another session's uncommitted work.** Lead-agent's routing log records the files changing at 06:45–06:46, from a session other than its own dispatches, and holds the build for it ([routing.log L1080](logs/routing.log#L1080)). At apply time this review re-measures the tree. If the flows are not committed, changes 1, 2 and 6 are held back and the reason is reported. Changes 3–5 do not depend on it.

**Two row triggers hand over the whole application row and hide nothing.** The safeguarding-completion flow starts when an application is modified ([trigger L29](src/solutions/RevitaliseGrantAutomation/Workflows/REVSafeguardingActionCompletion-8F1C2A44-1009-4B7A-9E21-0A1B2C3D4E09.json#L29)), and the scoring flow starts when one is created ([trigger L54](src/solutions/RevitaliseGrantAutomation/Workflows/REVScoringCalculateAndFlag-8F1C2A44-1002-4B7A-9E21-0A1B2C3D4E02.json#L54)). The referee columns are on the application's main form, so a staff-edited application carries them into the safeguarding flow's run history. Your rule names list, create and update steps only, so it does not cover triggers. That is decision 3.

**Routed to commercial-agent: who pays for securing the two DocuSign flows.** WBS 3.2 and 3.3 name these flows, and EX-004 says no task does. Commercial-agent owns whether the securing work is in-task rework, warranty, or a change order.

**Two queue entries this morning are stamped about five and a half hours in the future.** One is the in-flight fix (12:00, written before 06:47) and the other a build finding (12:30). A knowledge line added yesterday asked for the clock to be used, and it did not reach two other agents within the day. Logged for the next batch as a candidate for the id allocator to stamp the time itself. This review's own second entry is stamped 07:02 against a clock reading of 06:59, which is the same defect. It is left as written, because rewriting the log was refused (see the closing line).

## What you need to decide

**1. How wide should the list be?**

**Problem** — Your list names five columns. The special-category register holds 25 more (health and care narratives), and other contact-detail columns are on neither list: helper and emergency-contact names and numbers, applicant first and last name, phone, address, date of birth, bank account holder.
**Suggested fix** — Keep your five as the list, and have the check also read the special-category register's 25. Measured: zero extra findings on either tree, and it guards the five steps that already hide those columns.
**What happens if you don't** — Nothing breaks today, because every step that reads those columns already hides them. A future step reading, say, a helper's email without hiding it would pass the check.
[register L116](constraints/domain/special-category-register.yml#L116)

---

**2. Should the check be stricter than "sets secureData" in four named ways?**

**Problem** — Taken literally, "must set secureData" passes four shapes that still expose a listed value. Each was measured on a copy of a real flow changed in memory: (a) a read that hides its inputs but not its outputs, where the returned rows are the exposure; (b) a read that filters on a listed column, where the value is in the inputs; (c) a write that hides inputs but not outputs, since the response shows the row; (d) a read with no column list, which returns every column.
**Suggested fix** — Adopt all four, plus refusing anything the check cannot read as a plain value (an expression for the table or column list, a related-table expand with no column list, an unrecognised Dataverse operation). Each costs zero findings on both trees today.
**What happens if you don't** — The check passes (a), (b) and (c) as written, and a read hiding only its inputs is the likeliest way to get this wrong. For (c), the claim that an update's response shows the whole row is not verified in this repository. Requiring outputs on writes costs nothing today, so it does not depend on that claim.
[check list L47](.engine/scripts/verify-flow-definition-language.py#L47)

---

**3. Should the check cover row triggers too?**

**Problem** — Two flows start from a trigger on the application table that returns the whole row and hides nothing, and your rule covers list, create and update steps only.
**Suggested fix** — Extend the check to Dataverse row triggers on a table holding a listed column. Wire that part as a warning until development-agent secures the two triggers and whatever reads their output, and route that work under the tasks that own those flows or as a change-order decision.
**What happens if you don't** — The safeguarding flow's run history keeps collecting referee names and contact details whenever a staff-edited application's safeguarding flag changes, and no check reports it.
[safeguarding trigger L29](src/solutions/RevitaliseGrantAutomation/Workflows/REVSafeguardingActionCompletion-8F1C2A44-1009-4B7A-9E21-0A1B2C3D4E09.json#L29)

---

**4. Close EX-004 once the secured flows are committed?**

**Problem** — Once the other session's work is committed, EX-004 accepts an exposure that no longer exists in source, and one of the five steps it names was never personal under your list.
**Suggested fix** — Close it at apply time, provided the flows are committed and the new check passes on them. Keep it with its history, and record in the closure that environments which already ran these flows keep up to 28 days of run history with the values in it.
**What happens if you don't** — It stays open, covering nothing, until 2026-10-16. On that day it fails the commercial gate that validates this file, over an exposure fixed two weeks earlier.
[EX-004 L29](contract/known-exceptions.json#L29)

---

Measured, not assumed: every Dataverse step in all 10 flows was enumerated (44 steps: 29 list, 12 update, 3 create; no get-by-id) on both the last commit and the working tree at 06:50. A prototype of the rule ran over both: 4 findings and 4 true on the commit, 0 on the working tree. Four synthetic cases each failed only under the refinement meant to catch them. **Not verified:** the check itself is not written, and no build has run it. Whether an update's response carries the whole row was not observed. Whether the two triggers have already recorded referee values in DEV was not observed, because only a session with access to that environment can read its run history. **Refused by the harness:** stamping this review's name on the findings it processed (*"[Modify Shared Resources]"*), so they still read as unlooked-at in the queue. The reviewer can run the stamp; section 5 says exactly what it is.

---

## 1. Regression check — did the last review's changes work?

The last applied review is [2026-09-29](docs/improvements/2026-09-29-improvement-review.md), applied this morning. Its predecessor on this subject is [2026-09-28](docs/improvements/2026-09-28-improvement-review.md), which withheld the table-level form of this check ([L87](docs/improvements/2026-09-28-improvement-review.md#L87)).

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| 2026-09-29 change 1: re-read a flow's live definition after an import | 2026-09-30 | `async-flow-postimport-plugin-fails-silently` | NO. The reviewer has since asked for it as a check, now built as `verify-live-flow-definitions.py` (unwired, IMP-0964) | Working; it is moving up the ladder on the reviewer's instruction |
| 2026-09-29 change 2: import takes 4–6 minutes, wrapper budget 600 s | 2026-09-30 | `client-timeout-misread-as-write-failure` | NO | Working, leave alone |
| 2026-09-29 change 3: `pac` times are UTC; take log times from `date` | 2026-09-30 | `log-timestamp-not-taken-from-the-clock` | **YES**: IMP-0963 (12:00) and IMP-0964 (12:30), both written before 07:00, and this review's own IMP-0966 (07:02 against 06:59) | **Wrong altitude.** A prose fix that recurred three times within hours across three agents. Escalate to the allocator stamping the time, logged as IMP-0965 for the next batch |
| 2026-09-28 cluster K: "Run history is a log" knowledge section | 2026-09-29 | `declared-policy-not-mechanically-enforced` | No new unhidden personal read. The 4 on the last commit are the ones already known, and the working tree has 0 | Working as a signpost. It pointed at the missing list, and this review is the result |

**Changes whose class recurred after a prose fix:** 2026-09-29 change 3 → escalation logged as IMP-0965, deferred to the next batch (section 5).
**Changes whose class recurred after a gate:** none.

---

## 2. Clusters and promotion decisions

```
CLUSTER: declared-policy-not-mechanically-enforced  (x3: IMP-0951, IMP-0963, IMP-0966)
Altitude:   CLASS — the property is "a flow step that carries a declared personal column hides it
            from run history". Strip this client's column names and the statement is still true of
            any Power Automate + Dataverse solution, so the MECHANISM is engine-level; the column
            list is client-specific and stays in constraints/domain/ (skill §6, the check-7 pattern).
            Engine text will be grepped for `rev_` before commit: fixtures use synthetic names only.
Ladder row: "a tool could catch it mechanically" + third instance of the class on this subject
            (IMP-0320 → IMP-0951 → IMP-0963)
Becomes:    check 11 in .engine/scripts/verify-flow-definition-language.py, fed by
            constraints/domain/personal-data-columns.yml through the instance wrapper; runs inside
            the existing HARD `flow-definition-language` step, so no new build step.
Retires:    nothing — no instance gate existed. EX-004 is closed, not retired (decision 4).
Cites:      IMP-0951, IMP-0963, IMP-0966
Residual:   (1) row triggers: 2 unhidden on rev_application, decision 3; (2) steps DOWNSTREAM of a
            hidden read (Compose, connector posts, Find_the_failed_action over result()): not
            covered; pinned per flow by IntakeContract.Tests.ps1 and AcceptanceEnvelopeContract.
            Tests.ps1, which is the correct home because the closure depends on each flow's data
            flow; (3) columns on neither list (decision 1); (4) the check proves source, V1 — an
            environment is protected only once a build carrying the fix is imported there.
```

**Premises of the in-flight fix, re-measured.** IMP-0963 says the intake flow has no step naming a personal column without `secureData`. Confirmed: the one create that writes the applicant's email hides both inputs and outputs, and the one read that filters on it does too. It says List overdue grants selects no personal column. Confirmed: the grant reference is an autonumber, pseudonymous by its own column description. It says the downstream consumers are secured. Confirmed for the two envelope steps and the two escalation notifications. Its suggested target, the special-category register, is not adopted, for the reason in item 2 above.

**Corpus measurement for the proposed rule.** Every step touching a listed column, per tree:

| Tree | Steps touching a listed column | Hidden correctly | Findings | True positives |
|---|---|---|---|---|
| Last commit (`9ded0a2`) | 5 | 1 | 4 | 4 |
| Working tree, 06:50 | 5 | 5 | 0 | — (0 is correct: all 5 hide the part carrying the value) |

Under decision 1's widest option (47 columns) both counts are unchanged. Hiding everything field-secured instead (80 columns) would add 6 findings on the working tree: the grant status and dates, the envelope id (one step filters on it), the signed-PDF link, the escalation stamp, and the safeguarding completed-by/on stamps. That is why this review does not propose "field-secured" as the definition of personal.

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | script | `.engine/scripts/verify-flow-definition-language.py` | Check 11 and a `--personal-columns <path>` option. For each Dataverse `ListRecords` / `CreateRecord` / `UpdateRecord` step on a table holding a listed column: a read selecting one needs `outputs`; with decision 2, also a filter on one needs `inputs`, a write needs `inputs` and `outputs`, and a non-literal table, column list, item or unknown operation fails as "cannot prove". The finding message states the fix (`runtimeConfiguration.secureData.properties`) and points at the per-flow closure tests. Synthetic self-test with one fixture per case | IMP-0951, IMP-0963 | YES — `python3 .engine/scripts/verify-flow-definition-language.py --selftest` | already wired — HARD `flow-definition-language`, [config L648](config/revitalise-grant-automation-build.yml#L648), via the wrapper |
| 2 | script | `scripts/verify-flow-definition-language.py` | Pass `--personal-columns constraints/domain/personal-data-columns.yml` by default. Add a real-corpus self-test: unchanged corpus gives 0 check-11 findings; the same corpus with `secureData` removed in memory from Create Envelope's Get the application gives 1 or more | IMP-0951, IMP-0963 | YES — `python3 scripts/verify-flow-definition-language.py --selftest` | already wired — same step |
| 3 | other | `constraints/domain/personal-data-columns.yml` (new) | Your five columns with table, your verbatim ruling, date and name; `not_personal: rev_breaktype, rev_breaklocation`; and, per decision 1, `also_read: constraints/domain/special-category-register.yml` | IMP-0951, IMP-0963 | YES — row 1's check reads it and fails on a column absent from the solution's `Entity.xml` | N/A |
| 4 | constraint-amendment | [C-DOM-004](constraints/domain/domain-constraints.md#L37) | `Verify By` adds: "and check 11 of `flow-definition-language`: no Dataverse step carries a column listed in `personal-data-columns.yml` into run history unhidden" | IMP-0951, IMP-0963 | YES — row 1 | N/A |
| 5 | knowledge | [power-automate.md L336](knowledge/technology/power-automate.md#L336) | Replace "No gate checks it for any other flow yet…" with the check, and its two gaps: triggers (decision 3) and downstream consumers (per-flow closure tests) | IMP-0963, IMP-0966 | N/A — knowledge line | N/A |
| 6 | other | [contract/known-exceptions.json EX-004](contract/known-exceptions.json#L29) | Per decision 4: move to `_closed_exceptions` with the scope table above, the WBS 3.2/3.3 note for commercial-agent, and the 28-day run-history note; update `_gate_scope_note` to say EX-004 is closed and EX-005 is the remaining technology exception. If the harness refuses the write again, as on 2026-09-29, it is handed to you as a script that changes only this entry | IMP-0951 | YES — `python3 scripts/verify-wbs-chain.py` | N/A |

**Sequencing, which the wiring depends on.** Rows 1–3 land in the same commit as the other session's secured flows, or after it. If they land first, the HARD step fails on the 4 reads. At apply time the tree is re-measured. If the flows are uncommitted, rows 1, 2, 3 and 6 are held back and reported, and rows 4 and 5 wait with them because both name the check. Row 1 is an engine change: commit and push `.engine` first, check with `git -C .engine branch -r --contains HEAD`, then bump the pointer here.

**Constraint budget:** 0 of 3 used. One amendment to an existing HARD constraint, whose new `Verify By` is executable.

---

## 4. Retirements

> Retirement check performed: 87 live constraints (10 retired), and the three that touch this subject reviewed: C-DOM-004 (amended, not redundant: its error-log half is still checked by `domain-invariants`), C-TECH-064 (live-state verification, unrelated), and the special-category register's scoring bar (a different axis). None is made redundant by check 11. No instance gate existed for this class.

---

## 5. Findings left unprocessed

**Deferred:** IMP-0961, IMP-0964, IMP-0965

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| IMP-0961 | `untriaged-tool-warning` | Unread, and fixed by IMP-0962 this morning. Not this review's subject; it belongs to the post-deploy batch | the next post-deploy batch |
| IMP-0964 | `gate-not-wired-into-build` | Unread; the new live-flow check is unwired. Development-agent's, and not this subject | the next post-deploy batch, or when development-agent wires the step |
| IMP-0965 | `log-timestamp-not-taken-from-the-clock` | Logged by this review from the regression check. A tooling change to the allocator and the log validator, unrelated to the personal-column decision; bundling it would ask for two approvals in one keyword | the next post-deploy batch |

**Excluded as parked elsewhere:** IMP-0855 (awaiting approval in its own review) and IMP-0934 (governance-lane blocker, waiting for the next batch). Neither is re-derived here.

**Stamping refused.** Step 6 stamps this review's name on every entry it processes, so that the queue reads them as awaiting approval. The harness refused the write (*"[Modify Shared Resources]"*) and it was not retried. A scratch copy with the stamps applied was run through `verify-improvement-log.py --check`: exit 0, and IMP-0963 moves from `unread` to `awaiting-approval`. The stamp to run is: IMP-0951 `reviewed_in` becomes `["docs/improvements/2026-09-28-improvement-review.md", "docs/improvements/2026-09-30-improvement-review.md"]`, and IMP-0963 and IMP-0966 get `reviewed_in: "docs/improvements/2026-09-30-improvement-review.md"`. Nothing else changes.

**Dispositions on approval** (read against each entry's `observable_at`):

| Finding | `observable_at` | Disposition |
|---|---|---|
| IMP-0951 | V1 | **CLOSE**, `evidence_grep` on check 11's finding message in the engine script. Only if rows 1–3 apply |
| IMP-0963 | V1 | **CLOSE** as `APPLIED`, naming the other session's secured flows and closure test, and recording that its suggested target (the special-category register) was not adopted. Only once those files are committed |
| IMP-0966 | V1 | **DEFER** with your decision 3 as `deferred_reason` if you choose the warning route. **CLOSE** only if the triggers are secured and the check covers them |

---

## 6. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 960 | 962 (IMP-0965, IMP-0966 appended by this review) |
| Distinct lessons | 944 | 946 |
| Recurring classes (x≥2) | 72 | 73 (`log-timestamp-not-taken-from-the-clock` reaches x2) |
| Digest lines | 605 | 606 |

Regenerated after each append, per the capture contract, and confirmed current with `--check`. Regenerating moved the digest to 606 lines, and the line count quoted in `generate-known-failure-modes.py` at L46 now reads 605. `verify-derived-counts.py` reports that as a warning, not a failure. It is corrected at apply time.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-30-improvement-review.md

Findings processed: 3 NEW  →  1 clusters
Regression check:   4 prior changes audited, 1 classes recurred
Proposed:           0 constraints (cap 3), 1 constraint amendment, 2 gates/scripts,
                    1 skill/knowledge edits, 0 agent-file edits, 2 other, 0 retirements
Altitude calls:     1 generalised from instance to class, 1 left as notes
Digest:             will regenerate — 946 lessons, 73 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```


---

## 8. Applied

**Approval.** Xander Lykopoulos, relayed by lead-agent, verbatim: *"Approve improvements… run the log stamp."* Lead-agent ran the section 5 stamp at the reviewer's instruction before this apply. Re-verified read-only: all three entries carry `reviewed_in` exactly as section 5 specifies, and `verify-improvement-log.py --check` exits 0.

**Re-verified before applying (2026-09-30 07:08).** HEAD is still `9ded0a2`. The secured acceptance flows, their notes and `AcceptanceEnvelopeContract.Tests.ps1` are still uncommitted: the prototype of the rule finds 4 on HEAD and 0 on the working tree, the same as at draft time. No entry appended since the draft carries `corrects` against IMP-0951, IMP-0963 or IMP-0966. The two row triggers are unchanged against HEAD, with no `secureData`. The reviewer's answers to decisions 1–4 have not been received.

| # | Change | Applied at | Entries moved to APPLIED |
|---|---|---|---|
| — | Digest line-count claim, 605 → 606, in `scripts/generate-known-failure-modes.py` L46 **and** `.engine/scripts/generate-known-failure-modes.py` L46. Section 6 promised this correction, and it depends on no decision. `verify-derived-counts.py` drift count 7 → 6; the 6 left predate this review. `verify-engine-instance-split.py` exit 0 | working tree, not committed. The `.engine` copy needs a submodule commit and push before the pointer bump | none |

**Held back, not applied — by the approved sequencing condition in section 3, not by re-judgement:**

| # | Change | Why held | Applies when |
|---|---|---|---|
| 1, 2 | Check 11 (engine) and wrapper | the secured flows are uncommitted; the check's exact rule also depends on decision 2 | flows committed + decision 2 answered |
| 3 | `constraints/domain/personal-data-columns.yml` | lands with rows 1–2; its `also_read` line depends on decision 1 | flows committed + decision 1 answered |
| 4 | C-DOM-004 `Verify By` | names check 11, which does not exist yet | with rows 1–3 |
| 5 | power-automate.md L336 | names check 11 and decision 3's trigger scope | with rows 1–3 + decision 3 |
| 6 | EX-004 closure | conditional on the flows being committed and the check passing; they are not | flows committed + decision 4 answered |

**Dispositions recorded** (each as `deferred_reason` + `revisit_when`, naming this approval and the hold):

| Finding | Disposition | Returns when |
|---|---|---|
| IMP-0951 | DEFERRED. Its deferral text now records that the list is decided | flows committed + decisions 1–2 answered → apply 1–3 and CLOSE with `evidence_grep` on check 11 |
| IMP-0963 | DEFERRED, not closed: its fix is the uncommitted files | those files are committed → CLOSE as APPLIED naming the commit |
| IMP-0966 | DEFERRED on decision 3 | the reviewer answers decision 3 |

After the dispositions: `verify-improvement-log.py --check` exit 0, with 0 entries of this review left awaiting approval. The digest was regenerated and is current at 962 entries and 606 lines.

Entries rejected, with reasons: none.
