# Skill: How to Report Project Status

Used by `pm-agent`. Load it at the moment you answer, not upfront. One page by design.

---

## 1. Render, do not compose

Run `python3 scripts/collect-project-status.py --json` and answer from that. **No figure in your
answer that is absent from the snapshot.** If you want to say something the snapshot does not
contain, add it to the script — not to the prose. That is what makes a status answer cheap enough to
ask twenty times and impossible to hallucinate.

## 2. The seven things a status answer must contain

| | Why |
|---|---|
| Phase, contractual date, days remaining | The agreement fixes five dates and nobody had read one until 2026-08-19 |
| Open tasks and remaining **estimated** hours | Labelled as estimate. Never mix with actuals in one column |
| Verification level reached | In the words of the log that recorded it. See §3 |
| Blockers, each with an **owner and an age** | "Blocked" without an owner is a status; with an owner it is an action |
| Unconfirmed preconditions | Neither satisfied nor known-blocked. Someone has to ask, and nobody will unless it is on the page |
| Hours invoiced vs confirmed-unbilled | Two different numbers. D-7's 64 invoiced hours are not 64 hours worked |
| Next action, and whose it is | A status report that ends without one is a diary entry |

## 3. Never claim a level above the evidence

From `agents/WORKFLOW.md`: **V2** packaged · **V3** accepted by the target · **V4** a named person
opened and saved it · **V5** executed end-to-end with real inputs · **V6** client accepted.

Both live features stand at V3 with V4 outstanding, and `logs/pipeline.log` says so in its own
words. Writing "deployed ✅" over that is this project's most expensive recorded mistake
(`IMP-0012`: three components imported cleanly, were queryable, and no maker could open them)
committed in a new place.

Say `DEPLOYED (V3)` and name what is outstanding. Say `VERIFIED (V4)` only when someone did it, and
name them.

## 4. A document existing is not progress

`docs/development/…-form-validation-spec.md` existing means task 1.2's deliverable exists. It does
not mean the form validates anything — Alex builds the form, and the agreement excludes that work
from our scope. Report the deliverable, not the outcome you hope it implies.

## 5. The claim and the evidence are both reported

The WBS `Status` column is a claim; `derived_status` is what the repository contains. When they
disagree, report **both** and name the disagreement. That is the most valuable line in the whole
report — it is how `0.4 Done` against five absent tables became visible (`IMP-0030`).

## 6. Two numbers that must never be conflated (D-6)

- **Estimates** stay at the WBS figures. Do not re-estimate downward because AI assistance makes the
  work faster; the WBS is the customer-accepted specification.
- **Capacity** is 16 h/week, physical. Schedule risk computes against that, because a date is missed
  in wall-clock time.

Actuals are expected to come in well below estimate. That is the planned outcome, not a signal that
the estimate was wrong and not a reason to touch the baseline.

## 7. When nothing has moved

Say so, in one line, with the date of the last change. A status answer that pads a quiet week into
five paragraphs teaches the reader to stop reading them.

## 8. Never let a status failure touch delivery

If a PM script errors, report that the snapshot is stale and answer what you can. PM-R30: a
commercial or reporting failure never halts, retries or rolls back a build or a deploy.
