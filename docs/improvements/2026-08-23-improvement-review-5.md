# Improvement Review 17 — 2026-08-23

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 2 → 2 clusters (2 unread, 1 of them `blocker`)
**Trigger:** blocker escalation — `IMP-0227`, appended by the development-agent dispatch that repaired `IMP-0224` while review 16 was being applied. Processed immediately rather than batched.
**Gate:** `APPROVE IMPROVEMENTS`
**WBS:** `6.1–6.5` (trustee portal). No contracted task is claimed here; the findings guard it.

**Status:** ~~AWAITING `APPROVE IMPROVEMENTS`.~~ **APPROVED and APPLIED 2026-08-23** by the
reviewer (Xander Lykopoulos). See section 9 — including one correction made during application
that turns out to matter more than the change it was part of.

---

## The headline

**The blocker is a fix, not a failure — and it stays OPEN.** `IMP-0227` records the trustee
portal's reads migrated off the broken generic connector onto the four generated typed services.
It is honest about where it stopped: 233 tests, clean `tsc`, clean `eslint`, and **V4 not
performed**. Under the rule approved an hour ago it cannot be closed on that, so it is held with a
`revisit_when` naming the live trustee sign-in that closes it. That is the third consecutive
finding in this class held open rather than declared fixed.

**Review 16's gate passed its first live test, and nobody prompted it.** A different agent, in a
different session, wrote `"observable_at": "V4"` into its own finding and stated in its own lesson
that *"a clean build here is explicitly NOT sufficient evidence per IMP-0224/C-TECH-053"*. The
field went from invented to used, correctly, by someone else, within the hour.

**The remaining question this system kept re-asking is now closed permanently.** `IMP-0226` went
and checked whether *any* CLI flag can fix the generic connector. Neither can, and the reason is
structural rather than a missing flag: a `dataSourceType: "Connector"` entry has no field that
could hold an org URL. That is worth writing down precisely because six findings across three days
kept looking for one.

**One thing I am flagging against myself:** the correction I wrote into
[code-apps.md](../../knowledge/technology/code-apps.md#L238) sixty minutes ago is already partly
stale, because the repair landed. It is not wrong about the defect; it describes an app
architecture that has since changed. Section 3 fixes it.

---

## 1. Regression check — did review 16's changes work?

Review 16 was approved and applied roughly one hour before this review. That is too short an
interval for most of it, and I say so rather than claiming a result.

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| `observable_at` + `reobserved` in [verify-improvement-log.py](../../scripts/verify-improvement-log.py#L233) | 2026-08-23 | `v3-does-not-imply-v4` | **NO — and it was exercised** | **Working.** `IMP-0227` declared `observable_at: V4` unprompted, by another agent, and stopped at V3 deliberately |
| Three findings held open on `deferred_reason` rather than closed | 2026-08-23 | closure-on-prose | **NO** | **Working.** `IMP-0227` becomes the fourth, by the same rule |
| [code-apps.md](../../knowledge/technology/code-apps.md#L238) step 2 correction | 2026-08-23 | `code-app-connector-org-url-null` | **Partly stale within the hour** | **Right about the defect, out of date about the app.** Corrected in section 3 — see below |
| `blocked_on_asserted` expiry in [verify-pipeline-config.py](../../scripts/verify-pipeline-config.py#L462) | 2026-08-23 | `agent-instructions-describe-a-topology-that-changed` | NO | Too early to judge. The oldest note expires 2026-09-02 |
| [pipeline-agent.md](../../agents/pipeline-agent.md#L73) step 3a — native `pac` verb first | 2026-08-23 | `harness-blocks-destructive-call` | NO | Too early to judge |

**On the stale knowledge block, which is the interesting row.** It is not a recurrence and not a
wrong-altitude call. It says the trustee portal's call sites use the generic connector — true when
written, and untrue forty minutes later because `IMP-0227` moved the reads. A knowledge file that
describes *one app's current wiring* dates the moment that wiring changes. The fix in section 3
rewrites it to describe **the two data source types and how each resolves its org URL**, which is a
platform fact that does not move, and keeps the portal only as the worked example.

**No class recurred.** Both entries in scope are remediation of `code-app-connector-org-url-null`,
not new instances of it.

---

## 2. Clusters and promotion decisions

```
CLUSTER A: the generic connector cannot be fixed by a flag — it is the wrong TYPE
           (x2: IMP-0226 friction, IMP-0227 blocker; both class code-app-connector-org-url-null)
Altitude:  KNOWLEDGE, and deliberately not a rule. Two findings, one conclusion, and the
           conclusion is a platform fact rather than a process failure. The process failure
           in this class was already promoted to a gate in review 16 (IMP-0225), and that
           gate is what is holding IMP-0227 open right now — so the mechanism is defended
           and what is missing is only the fact.
Ladder row: "one instance, but the cause is general and a human needs to know it"
Becomes:   knowledge/technology/code-apps.md — the org-url diagnostic rewritten around the
           TWO DATA SOURCE TYPES and their two different resolution mechanisms, replacing
           the app-specific wiring description that is already stale.
Retires:   the standing open question "is there another flag to try?" — asked and re-asked
           across IMP-0187, IMP-0191, IMP-0192, IMP-0208, IMP-0224. Answered NO, with the
           structural reason, so it stops being asked.
Cites:     IMP-0226, IMP-0227
Residual:  The structural claim — that a per-table `"Dataverse"` source resolves its instance
           URL from launch-time app metadata rather than the shared connector's OAuth binding
           — is read from the installed SDK's own shipped source (@microsoft/power-apps@1.3.0,
           dataverseDataOperationExecutor.js). That is strong V1 evidence about the mechanism
           and it is NOT a live observation that the reads work. Only V4 supplies that, and
           this review does not claim it.
```

```
CLUSTER B: a stray `pac` process blocks whatever pac command runs next  (x3)
Altitude:  CLASS — third instance. IMP-0215 (`pac solution check`), IMP-0216 (`pac org who`),
           now IMP-0226 (`pac code add-data-source`, PID 62791, alive 34m37s).
Ladder row: "a tool could catch it mechanically" — and there is a script already at the exact
           moment of failure, currently only ADVISING the diagnostic.
Becomes:   scripts/run-with-timeout.sh RUNS the stray-process check on timeout and prints the
           result, instead of telling the reader to run it. Plus the knowledge note
           generalised from two named commands to any pac command.
           CORRECTED AT APPLY TIME — see section 9: this line said it would run
           `pgrep -fl pac`, the command all three write-ups recommended. Building it proved
           that command returns 16 non-pac processes on this Mac. What shipped matches on
           the executable BASENAME, and the knowledge note's advice was corrected too.
Retires:   nothing. The advisory text is replaced by the executed check, in place.
Cites:     IMP-0215, IMP-0216, IMP-0226
Residual:  NAMED, AND IT MATTERS. The wrapper only helps commands that run THROUGH it, and
           today that is the `lint` build step alone. IMP-0226's own hang was a bare
           `pac code add-data-source`, which the wrapper would never have seen. So the
           knowledge note is not redundant with the script — it is the only cover for
           ad-hoc pac calls, and that is why both are proposed rather than just the script.
```

---

## 3. Proposed changes

### A1 — the org-url diagnostic, rewritten around types rather than around this app

**Replaces the table and the two questions at
[code-apps.md line 243](../../knowledge/technology/code-apps.md#L243).** The current version
describes the trustee portal's wiring, which changed forty minutes after it was written. The
replacement describes the platform, and uses the portal as the example:

> **There are two kinds of Dataverse data source in `dataSourcesInfo.ts`, and they resolve their
> organisation URL by completely different mechanisms. Only one of them is broken.**
>
> | | `dataSourceType: "Dataverse"` (per-table) | `dataSourceType: "Connector"` (generic) |
> |---|---|---|
> | Key | `rev_applications`, `systemusers`, … | `commondataserviceforapps` |
> | Created by | `pa app add data-source --table <t> -u <url>` | the non-table `--connector dataverse` call |
> | Called via | the generated services in `src/generated/services/` | `getClient(dataSourcesInfo).executeAsync({connectorOperation})` |
> | Resolves the org URL from | **the app's own launch-time runtime metadata** (`metadataClient.getAppDataSourceConfigsAsync()`) | **the shared "Microsoft Dataverse" OAuth connection's org-url header** |
> | Observed null for a real signed-in user? | no | **yes, since `IMP-0187`** |
>
> **No CLI flag fixes the generic one, and this has now been checked directly rather than
> assumed** (`IMP-0226`):
>
> - `pa app add data-source --connector dataverse -u <url>` **without** `--table` exits 2 with
>   *"Missing required option --table"*. The new CLI's `-u` has no path that reaches a
>   non-table-scoped source at all.
> - `pac code add-data-source -a shared_commondataserviceforapps -env <url>` — the older CLI's
>   equivalent flag, and one this file did not previously mention — **does** run and reports
>   *"Data source added successfully"*, growing the connector's `apis` block from 1858 to 3574
>   lines. It changes which connector **schema version** is fetched. The org URL string appears
>   **nowhere** in the regenerated file, and `tableId` / `version` / `primaryKey` stay empty
>   strings, because a `"Connector"` entry has no field that could hold one.
>
> **So the fix is a different data source TYPE, not a different flag.** If an app's call sites
> use the generic connector, move them to the per-table services. That is what the trustee portal
> did (`IMP-0227`): `client.ts`'s reads now dispatch to `Rev_applicationsService`,
> `Rev_reviewsService`, `Rev_applicantsService` and `SystemusersService`, while the **write stays
> on `executeAsync`** because `UpdateOnlyRecord` + `If-Match: '*'` cannot be expressed through the
> generated `update()` (`IMP-0210`) — so a migrated app ends up deliberately using **both** types,
> reads on one and the guarded write on the other.
>
> **And none of the above is evidence the symptom is gone.** Re-open the app as a real signed-in
> user and re-run the original failing calls. Every prior closure in this class was made on a
> clean build (`IMP-0208`, `IMP-0224`).

### A2 — the stray-process note, generalised from two commands to any

**[build-and-deploy.md](../../knowledge/technology/build-and-deploy.md#L284)** currently frames the
stray process around `pac solution check` and `pac org who`. Third instance makes that scoping
wrong: it is **any** `pac` command that needs the token cache. The note becomes command-agnostic,
records `pac code add-data-source` as the third, and keeps the detail that earns its place — the
process belongs to VS Code's Power Platform extension and is a *different binary* from
`~/.dotnet/tools/pac`, so it survives anything you do to your own shell.

### B — the diagnostic runs itself

**[run-with-timeout.sh](../../scripts/run-with-timeout.sh)** already prints, on timeout, *"check
for a stray process from a previous attempt (`pgrep -fl pac`)"*. Three instances in, advice at the
moment of failure is worth less than the answer at the moment of failure. Proposed: on exit 124,
**run `pgrep -fl pac` and print what it finds**, with the elapsed lifetime if available, so the
operator sees the offending process rather than an instruction to go looking. Add a self-test case
asserting the block appears on a timeout. Six cases instead of five.

This is the ladder's *"a tool could catch it mechanically"* row, applied to a script that already
exists and already runs at exactly the right moment.

### C — no new constraints

**None proposed.** The rule that governs this class — a defect visible only at V4 is not closed on
V2/V3 evidence — became [`C-TECH-053`'s](../../constraints/technology/technology-constraints.md#L108)
amendment and a mechanical check one review ago, and it is working: it is the reason `IMP-0227` is
held open below. A second row would be duplicate coverage of a defended control.

---

## 4. Retirements

**Checked; no constraint is a retirement candidate.**
[verify-constraint-verifiers.py](../../scripts/verify-constraint-verifiers.py) passes at 64 paths
across 74 active rows, so no row names a verifier that has gone missing — the condition behind
every retirement so far.

**One knowledge retirement is proposed instead, and it is real.** The standing open question
*"is there another CLI flag to try for org-url-null?"* is answered NO with a structural reason. It
has been asked in five findings across three days and cost a Microsoft support recommendation that
review 12 had to retract. Closing a question that keeps consuming dispatches is worth as much as
retiring a rule.

**Carried forward, unchanged:** the `C-TECH-020`–`023` reinstatement — the four dependency
constraints retired on the written condition *"reinstate when the Phase 3 Code App introduces a
real manifest"*, a condition now met. Out of scope by the reviewer's explicit instruction on review
16, and still recommended as the next review's first item.

---

## 5. Findings left unprocessed

| Excluded | Count | Which | Why |
|---|---|---|---|
| `awaiting-approval` | 1 | `IMP-0198` | A review already processed it and is parked at its own gate; it needs the keyword against that document (`IMP-0154`) |
| `reviewer-deferred` | 7 | `IMP-0112`, `IMP-0152`, `IMP-0197`, `IMP-0205`, `IMP-0218`, `IMP-0221`, `IMP-0224` | Each carries an accepted `deferred_reason`. The last three are review 16's deliberate holds, waiting on live observations, not on a keyword |
| `APPLIED` / `REJECTED` | 214 | — | The digest already carries their lessons |

Both `unread` entries were read in full and both are processed. No cap was applied silently.

---

## 6. What happens to the two findings

**`IMP-0226` → APPLIED on approval.** It is `friction`, its deliverable is the knowledge it
produced, and that knowledge is the change. Nothing about it needs a live observation: the two CLI
behaviours were executed this session and the regenerated file was read and reverted per
[`C-TECH-056`](../../constraints/technology/technology-constraints.md#L111).

**`IMP-0227` → STAYS OPEN, and this is the recommendation you are approving.** The migration is
real and I verified its central claims independently rather than accepting them: `client.ts` now
dispatches reads through a `READ_SERVICES` map onto the four typed services, the only surviving
`executeAsync` call site is the guarded write, and `npx vitest run` reports **233 passed across 16
files**. All of that is V2/V3. The defect `IMP-0227` repairs was only ever observable at V4, and no
trustee has signed in since.

Closing it now would be the same act as review 12 closing `IMP-0208` — the identical class, five
weeks of rework compressed into three days, and the reason the gate exists. It gets a
`deferred_reason` and:

> **`revisit_when`:** a real trustee signs in to the live REV Trustee Review Portal after this
> build is deployed and confirms the three call sites `IMP-0224` recorded — `systemusers` by
> `azureactivedirectoryobjectid`, `systemusers` by `domainname`, and `rev_applications`
> `ListRecords` — return data with no *"Invalid organization URL 'null' provided"*. Then record
> `reobserved` on **both** `IMP-0227` and `IMP-0224`, which close together.

**Note that this build has not been deployed yet.** The migration is in the working tree; DEV still
runs build 20260823-2, the one the reviewer tested. V4 needs a push first.

---

## 7. Digest impact

`logs/improvement-log.jsonl` stays at **224 entries** — this review appends none. Both findings in
scope already exist, and nothing in processing them surprised me in a way the six capture triggers
name.

On approval the digest regenerates with 224 lessons and 25 recurring classes, unchanged in count:
`IMP-0226` and `IMP-0227` are already counted in `platform-contract-guessed-not-groundtruthed`
(x29) and `v3-does-not-imply-v4` (x10) respectively. Only their statuses move.

---

## 8. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-23-improvement-review-5.md

Findings processed: 2 NEW  →  2 clusters
Regression check:   5 prior changes audited, 0 classes recurred
Proposed:           0 constraints (cap 3), 1 gate/script, 2 knowledge edits,
                    0 agent-file edits, 0 constraint retirements (1 knowledge question closed)
Altitude calls:     1 generalised from instance to class, 1 left as knowledge
Dispositions:       1 APPLIED (IMP-0226), 1 HELD OPEN pending V4 (IMP-0227)
Digest:             will regenerate — 224 lessons, 25 recurring classes (counts unchanged)

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 9. Applied

**APPROVED and APPLIED 2026-08-23.** All three changes are on disk. `IMP-0226` is closed;
`IMP-0227` is held open pending the live V4 observation, as recommended.

| # | Change | File | Cites |
|---|---|---|---|
| 1 | Org-url diagnostic rewritten around the two data source types and their two resolution mechanisms; both CLI results recorded with the structural reason no flag can work | [code-apps.md](../../knowledge/technology/code-apps.md#L243) | IMP-0226, IMP-0227 |
| 2 | Stray-`pac` note generalised from two named commands to any `pac` command; third instance recorded; the `pgrep` advice corrected | [build-and-deploy.md](../../knowledge/technology/build-and-deploy.md#L284) | IMP-0215, IMP-0216, IMP-0226 |
| 3 | On exit 124 the wrapper RUNS the stray-process check and prints what it found; sixth self-test case asserts it | [run-with-timeout.sh](../../scripts/run-with-timeout.sh) | IMP-0226 |

### The correction that matters more than the change

**The diagnostic advice this system has been giving for three incidents does not work.** All three
write-ups said to run `pgrep -fl pac`. Building change 3 meant actually running it, and `-f`
substring-matches the entire argument list — so *"Application Support"*, *"SharePoint"* and
*"workspace"* all match. On this Mac it returns **16 processes, not one of them `pac`**: Teams
helpers, VS Code renderers, a CodeQL query server.

The first version of change 3 printed exactly that, and the output was unusable — screens of
irrelevant processes. Both the script and the knowledge note now match on the **executable
basename** instead:

```bash
ps -Ao pid=,etime=,comm= | while read -r pid etime comm; do
    [ "${comm##*/}" = "pac" ] && echo "$pid $etime $comm"
done
```

**This is worth stating plainly: for three incidents, anyone who followed the documented advice saw
a wall of unrelated processes and would reasonably have concluded there was no stray `pac`.** Two
of those three incidents escalated as far as suspecting a hosted-service outage. The advice was
never tested by the reviews that wrote it — which is the same shape as `IMP-0225`, one level down:
a remediation recorded without being executed.

### `IMP-0227` — what it is waiting for

> a real trustee signs in to the live portal **after this build is pushed to DEV** and confirms the
> three call sites return data with no *"Invalid organization URL 'null' provided"*. Then record
> `reobserved` on **both** `IMP-0227` and `IMP-0224` — they close together.

Owner: pipeline-agent for the push, then the reviewer for the sign-in. DEV currently runs
20260823-2, the build the reviewer tested; the migration is in the working tree and not yet
deployed.

### Verification

`run-with-timeout.sh --selftest`: **6 of 6**, including the new case, and a real timeout inspected
by hand to confirm the output reads usefully. `verify-improvement-log --check`: **OK — 224 entries
(9 NEW, 215 APPLIED, 0 REJECTED)**, the first fully green run of this gate today.
`generate-known-failure-modes --check`: current. `BuildGates.Tests.ps1`: **98 of 98** — the test
that was red through reviews 16 and 17 is green, because the last unprocessed blocker now carries a
recorded disposition.

**Not verified, and not verifiable from here:** that the migration fixes the live symptom. That is
what `IMP-0227` is held open for.
