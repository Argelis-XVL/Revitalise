# Skill: How to Account for Billable Time

Used by `commercial-agent`. Load it at the moment you classify, not upfront.

---

## 1. The rule everything else follows from

**Evidence span is a lower bound on elapsed time, and elapsed time is no bound at all on billable
attention.** The repository can see when a build ran and when a commit landed. It cannot see the
hour you spent reading the WBS, the call with Emily, or the twenty minutes the agent worked while you
made coffee.

So: `scripts/reconstruct-worklog.py` **proposes**, you **set the number**, and nothing enters
`logs/worklog.jsonl` without `APPROVE TIMESHEET`. Never present a proposal as a measurement.

## 2. Hours only

D-3: no fee figure, rate, currency amount or bank detail in this repository — including in prose
inside a ledger line. `scripts/verify-worklog.py` fails on any. The money is applied outside the
repo from a rate held outside it.

## 3. Classify every session into exactly one of four

| Classification | Billable | Decided by |
|---|---|---|
| in-scope build against an accepted WBS task | yes | the baseline |
| **warranty rework** — a defect against the Agreed Specification, inside a phase's warranty window | **no** | **Build Terms B4** — not a policy preference |
| **change order** — work no accepted WBS task covers | yes, once the Client agrees | `APPROVE CHANGE ORDER <id>` |
| **system work** — `agents/`, `skills/`, `constraints/`, `scripts/`, `templates/` | no | it is tooling, not what they bought |

Warranty classification is **currently not computable**: D-4's clause text is absent and
`scripts/warranty-clock.py` refuses. Raise a suspected warranty item to the reviewer; do not assume
either way. A guessed warranty window is a guessed invoice.

## 4. What must never be billed

- an hour with no resolving evidence and no human confirmation (`C-COM-001`)
- an hour already on an issued invoice (`C-COM-003`)
- **anything inside the D-7 historic seed.** `WL-0001` carries 64 hours already invoiced across
  Phase 0 and the Phase 2 build, and the split between them was never recorded. Start from that
  total. Re-deriving per-phase actuals for those phases charges them twice — the exact failure the
  seed exists to prevent
- work against a task absent from the accepted baseline with no change order (`C-COM-002`)
- estimated-but-not-performed work. An actual that exactly equals the WBS estimate is almost always
  an estimate copied into the actuals column; `verify-worklog.py` warns on it (`IMP-0032`, D-6)

## 5. Off-repo work is legitimate and must be marked

Client calls, Emily's walkthroughs, maker-portal clicks, chasing Wanstor: real, billable, invisible
to the repository. Record them as `source: human-declared` with a date, an activity line and a WBS
task. The gate reports what share of an invoice is un-evidenced, so a statement that is mostly
declared reads as that rather than passing as reconstructed fact.

## 6. Splitting a session

If a session touched two tasks, give it an `allocation` whose hours sum to the session total —
`verify-worklog.py` fails if they do not. If you genuinely cannot split it, say so in the note rather
than inventing a ratio.

## 7. Never report a variance for an open phase

`IMP-0065`. 64 hours against a 68–106 estimate looked like efficient delivery; the work was simply
unfinished and not fully invoiced. A phase looks efficient right up until the remaining work is
booked. Before comparing an actual to an estimate, establish the phase is **closed** — client testing
and feedback included, because those are exactly what is outstanding when the build looks done.

## 8. Disclose the write-offs

A line reading "3.5 h — internal rework, not charged" is worth more in a client relationship than
3.5 h of margin, and it is the record that stops the same question being asked next quarter.
