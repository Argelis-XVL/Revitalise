# Test data for the deployed flows

Synthetic data for exercising the four Power Automate flows in
`src/solutions/RevitaliseGrantAutomation/Workflows/`. **No real person is described
anywhere in this folder.** Names are invented, emails use the reserved
`example.invalid` domain, phone numbers come from the Ofcom drama range, and
postcodes are real districts with nobody attached to them.

Serves WBS tasks `2.8` (scoring: test with real data + sign-off), `4.5` (intake:
end-to-end test) and `0.9` (error log + failure alert).

---

## Before anything will happen

Two things are true of `REV-GrantApplications-DEV` as at 2026-08-20, and both stop
this data doing anything:

**1. All four flows are in Draft.** They imported cleanly, but a solution import
does not turn a flow on. `provisioning/dataverse/seed-test-data.ps1` refuses to
load while any of them is off, because the scoring flow triggers on row *created* —
a row inserted now would never be scored, and no amount of re-saving it later
would help.

**2. `rev_ProcessOwnerUpn` has no value.** Every Teams message in every flow sends
to `@parameters('rev_ProcessOwnerUpn')`. The environment variable is declared
`isrequired=1` with no default and has no value row in DEV, so those actions fail,
which fails the scope around them, which fires the failure alert — whose own Teams
action fails for the same reason, and whose fallback email needs
`rev_ServiceMailbox`, also unset.

So, in order:

| # | Do this | Where |
|---|---|---|
| 1 | Set `rev_ProcessOwnerUpn` to the tester's UPN | Solution → Environment variables |
| 2 | Set `rev_ServiceMailbox` to a monitored mailbox | same |
| 3 | Set `rev_IntakeAllowedClientId` — only needed for the intake flow | same |
| 4 | Turn all four flows on | Power Automate → Solutions |
| 5 | Confirm the connections behind `rev_SharedDataverse`, `rev_SharedTeams` and `rev_SharedOutlook` still work | Power Automate → Connections |
| 6 | Load the data | `pwsh provisioning/dataverse/seed-test-data.ps1 -Env dev` |

Steps 1–5 are all maker-portal work and none of them is scripted in this repo.

---

## The three scripts

```bash
export PROVISION_APP_ID=<provisioning app registration client id>
export PROVISION_CERT_THUMBPRINT=<thumbprint of the provisioning certificate>

pwsh provisioning/dataverse/seed-test-data.ps1   -Env dev          # load
pwsh provisioning/dataverse/verify-test-data.ps1 -Env dev          # check
pwsh provisioning/dataverse/remove-test-data.ps1 -Env dev          # dry run
pwsh provisioning/dataverse/remove-test-data.ps1 -Env dev -Force   # delete
```

`-Env` accepts `dev` and `test` only. `prd` is not a permitted value and fails at
parameter binding — a synthetic grant application in a live charity's records is a
data-quality incident, not a test.

**`seed-test-data.ps1`** creates one `rev_applicant` and one `rev_application` per
case. Creating the application is what fires the scoring flow. It validates every
case before writing anything, and it skips a case whose submission id already
exists rather than updating it: an update does not fire a create trigger, so
updating would leave the flow untested while reporting success. Use
`-Case TD-06,TD-09` to load a subset, and `-DelaySeconds` to control the pause
between cases (default 3, which keeps the run history in case order).

**`verify-test-data.ps1`** is the half that makes this a test rather than a pile of
rows. It reads each row back and compares status, score, income flag, whether
`rev_scoredon` was stamped, and specific phrases in `rev_scorebreakdown`. It then
does two things no single row can: it compares TD-10 against TD-11, and it computes
the daily-summary counters the same way the summary flow computes them. A row that
has not been scored is reported FAIL with that as the reason — "the flow has not
run" and "the flow ran and got it wrong" are different findings and neither is a
pass.

**`remove-test-data.ps1`** is a dry run unless you pass `-Force`. Error-log rows are
kept unless you also pass `-IncludeErrorLogs`, because that table is an audit trail.

### How the teardown finds the rows

| Table | Marker |
|---|---|
| `rev_application` | `rev_sourcesubmissionid` starts with `TESTDATA-` |
| `rev_applicant` | `rev_lastcontactdate` equals `1900-01-01` |

`rev_applicant` has no alternate key, and its name, email and postcode are all
secured columns, so there is nothing else reliable to filter on. A last-contact date
in 1900 is also obviously wrong on screen, which is the point. Both markers are
defined once, in `provisioning/dataverse/test-data-common.ps1`, so the loader and
the remover cannot drift apart.

---

## `scoring-test-data.json` — 12 cases

Tests `REV | Scoring | Calculate & Flag`. Every expected score is derived from the
scoring configuration **as it actually stands in DEV**, read live on 2026-08-20 and
recorded in the file's `_configurationTheseExpectationsAssume` block:

```
LikertPointMap          1→5  2→4  3→3  4→2  5→1  6→0    ("Not sure")
FeelingScaleInversion   n → 10 − n
KnockoutThreshold       20        (at or below → Auto-reject)
BorderlineBandLower     21        (21–30 inclusive → Borderline)
BorderlineBandUpper     30        (above → Auto-pass)
IncomeCeiling           25000
MaxCircumstanceScore    60
```

**If any of those change, every expected value below is wrong.** Re-derive them from
the new configuration. Do not adjust them to match whatever the flow produced — that
turns the test into a recording of current behaviour.

| Case | Score | Status | Income flag | What it is for |
|---|---|---|---|---|
| TD-01 | 60 | Auto-pass | Within ceiling | Top of the scale |
| TD-02 | 31 | Auto-pass | Within ceiling | One point above the band — proves 30 is inclusive |
| TD-03 | 30 | Borderline | Above ceiling | Band upper bound exactly |
| TD-04 | 21 | Borderline | Not stated | Band lower bound exactly — proves 20 is inclusive |
| TD-05 | 20 | Auto-reject | Above ceiling | Knockout threshold exactly |
| TD-06 | 20 | Auto-reject | Above ceiling | One "Not sure" answer, worth 0 |
| TD-07 | — | Under Review | — | Wellbeing answer 7 missing → no outcome guessed |
| TD-08 | — | Under Review | — | Life-satisfaction answer missing → same |
| TD-09 | — | Eligible for Panel | — | Override guard: the flow must not touch this row |
| TD-10 | 48 | Auto-pass | Not stated | No income band supplied |
| TD-11 | 48 | Auto-pass | Not stated | Same answers **plus** safeguarding and health data |
| TD-12 | 10 | Auto-reject | Above ceiling | Bottom of the scale |

Three of these carry more weight than the rest:

**No case exercises the rounding rule any more, and none can.** TD-06 was that case:
until 2026-08-20 "Not sure" was worth 0.5, so it totalled 20.5, and the half rounded
**up** to 21 and lifted the application out of Auto-reject. The process owner then set
"Not sure" to 0, confirmed with Emily. No answer can now produce a fractional total, so
`Round_the_circumstance_score` is unreachable — it stays as a guard. TD-06 now asserts
that the breakdown shows `response 6 (Not sure) = 0`, so a silent revert to 0.5 is
visible.

**TD-09 proves a person's decision cannot be overwritten.** Its answers would score
60 and become Auto-pass, but `rev_statusoverridden` is already true. If it comes
back scored, the override guard is broken.

**TD-10 and TD-11 are a pair, and must be read together.** Every scored answer is
identical. TD-11 additionally carries a safeguarding flag, safeguarding notes, a
condition profile, a benefits declaration and free-text narrative. Equal scores are
what "special-category data does not influence an automated outcome" looks like when
observed rather than asserted. `verify-test-data.ps1` compares them explicitly.

**TD-07's empty income flag is correct.** The withheld-outcome path stops before
deriving the flag, so an empty `rev_incomeflag` there is the specified behaviour,
not a defect.

### Two branches this data cannot reach

*An unscoreable life-satisfaction answer.* `rev_feelingscaleanswer` has
`MaxValue=10` in the table definition, so Dataverse rejects 11 before the flow sees
it. The branch is only reachable by removing a key from `FeelingScaleInversion` —
change the setting row, create a row using the removed value, then put the setting
back. Worth doing once, deliberately, not as part of a normal run.

*A wellbeing answer outside the point map.* `rev_wellbeinganswer1..10` are choice
columns bound to `rev_likertresponse`, whose only values are 1–6, all of which the
map covers. Unreachable without changing either the option set or the map.

---

## `intake-payloads.json` — 6 cases, blocked

HTTP bodies for `REV | Intake | WordPress to Dataverse`. **Not runnable yet**, and
the blocker is not only the WordPress plugin: `rev_IntakeAllowedClientId` has no
value in DEV, so the header check the flow performs cannot pass and every request
would take the 401 branch. Set that variable and turn the flow on, and five of the
six become runnable with `curl` — no plugin needed.

| Case | Expect | What it is for |
|---|---|---|
| IN-01 | 201 | Complete submission; applicant + application created, then scored to 49 / Auto-pass |
| IN-02 | 200 | Byte-identical replay of IN-01 — the alternate key must prevent a second row |
| IN-03 | 400 | No postcode — rejected *and* written to the error log |
| IN-04 | 401 | Wrong client id — rejected before anything is written or logged |
| IN-05 | 201 | Three unrecognised label values — columns left empty and recorded, never guessed |
| IN-06 | 201 | Age band label disagrees with date of birth — the label wins |

IN-04 is testable the moment the flow is on, because it asserts that a *wrong*
client id is rejected.

---

## `failure-alert-inputs.json` — 6 cases

Manual run inputs for `REV | Ops | Failure Alert`. It is a child flow with a button
trigger, so it can be run straight from the Power Automate portal by pasting five
values — this is the cheapest of the four flows to test and the one that has to work
for any of the others to report a problem.

Covers all four severity words, one severity word the mapping does not know (falls
through to Error rather than failing), and a 3,240-character error message that must
be cut to 2,000 plus a marker.

Every case expects a new `rev_errorlog` row with `rev_resolved` false, a Teams
message, and a 200 response carrying `errorLogReference`, `logged` and `alerted`.

`rev_recordreference` is a reference only — never a name, an email address or
narrative text. Every value in the file obeys that, and so must every calling flow.

---

## `REV | Scoring | Daily Summary`

Recurrence trigger, 07:00 UTC on weekdays. Run it by hand from the portal after
loading the scoring data. Expected additions on top of whatever the environment
already holds:

| Counter | From this data | Window |
|---|---|---|
| Scored | 11 | since the previous run |
| Auto-rejected | 2 | since the previous run |
| Borderline awaiting review | 3 | **all time** |
| Under review, no score | 2 | **all time** |

The bottom two are all-time counts in the flow itself, so pre-existing rows are
included. `verify-test-data.ps1` prints all four computed the same way, so the
figures in the Teams message can be checked against something derived rather than
remembered.

Teams messages this data should produce in total: **3** borderline notices (TD-03,
TD-04, TD-06) and **2** incomplete-scoring notices (TD-07, TD-08).

---

## What is not here

No `rev_grant` data. Nothing deployed writes to that table yet — the DocuSign and
finance automations are not built — so there is nothing to test against it.
