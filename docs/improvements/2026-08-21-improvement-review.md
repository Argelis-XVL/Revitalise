# Improvement Review — 2026-08-21

**Gate:** `APPROVE IMPROVEMENTS`, given by the reviewer after a build failed on two conditions
neither of which the change under build had caused.
**Findings processed:** 40 `NEW` → 17 clusters. 34 applied, 3 newly deferred with a named owner
and a return date, 1 existing deferral given the `revisit_when` it was missing.
**WBS:** `system` — this review changes the development system, not the product. Out of
contractual scope, non-billable (`C-COM-002`).

## Summary

One blocker drove this review, and it was not a bug in a gate — it was **a build step that
carried two gates while the record had room for one result.** `unit-tests` owned both the test
count and the C-TECH-014 coverage threshold. On 2026-08-20 three manifests recorded
`"unit-tests": "782 passed, 1 failed, 1 skipped"` and omitted the percentage. Coverage had
fallen from 89.13% to 67.78% that same day. A HARD constraint went from passing to failing and
no artifact in the repository said so, for a day and three deploys.

The durable fix is structural rather than louder: coverage is now its own named step, so two
gates can no longer hide behind one result. Alongside it, three blocker findings about cloud-flow
shapes that pack and import cleanly and then fail at run time became one gate — which
immediately found six live instances in the intake flow that nothing was going to catch before
the first real website submission.

## 1. Regression check — did the last review's changes work?

| Prior change | Class | Recurred? | Verdict |
|---|---|---|---|
| `scripts/lib/worklog.py` + verify-pm-gates section 7 | `two-invocation-paths-disagree` | One new instance (`IMP-0107`), unrelated to the ledger | Held for what it covered. |
| `verify-shipped-content.py` check 1c (SubArea Url) | `platform-contract-guessed-not-groundtruthed` | Four new instances, none of them site-map shapes | Held for site maps. The class moved to cloud-flow shapes, which is this review's main gate. |
| `reconstruct-worklog.py` per-event classification | `gate-reassures-wrongly` | No new instances | Held. |
| `how-to-report-to-the-reviewer.md` rule 8 (prose) | `output-shape-defeats-the-reader` | **Once** (`IMP-0130`) | **Wrong altitude again, and in a new direction** — see below. |
| `commercial-agent.md` topology corrections | `agent-instructions-describe-a-topology-that-changed` | No new instances | Held. |

**Two entries deserve more than a row.**

`output-shape-defeats-the-reader` recurred for the sixth time, and the recurrence is not what the
prose was written to prevent. Rules 1–8 of that skill govern **reports to the reviewer**.
`IMP-0130` is output to the **client** — two Teams notifications the process owner has to act on,
shipped as `<br/>`-separated paragraphs with no link to the record they were about. The class is
wider than the skill that owns it, and wider than the digest section it sits in. Stated here
rather than patched, because the mechanical form of "a notification offers a route to the thing
it is about" is not obvious and a bad version of that gate would be worse than none.

`C-TECH-064` still has never run. The 2026-08-20 review said so; it is still true, and `IMP-0085`
is still its consequence. It is now carrying the `revisit_when` it was missing, pinned to the next
table build rather than to a review date.

**And one thing the last review predicted about itself came true.** Its own closing line said the
Pester suite was not run. Neither was it run by the three deploys that followed. That is precisely
the window in which coverage fell 21 points unnoticed.

## 2. Clusters and promotion decisions

```
CLUSTER: gate-cannot-fail  (x4 NEW: IMP-0115, IMP-0117, IMP-0129, IMP-0132 — class now x18)  ** BLOCKER **
Altitude:  CLASS. The property is not "record the coverage number too". It is: a build step may
           contain more than one gate, and a record with one slot per step can hide a failing
           gate while looking complete.
Ladder row: "a tool could catch it mechanically" + "second instance -> generalise"
Becomes:   scripts/verify-coverage-threshold.py (new) + the `coverage-threshold` build step,
           split out of `unit-tests` which now passes -CoverageThreshold 0 (measure, do not
           decide) + config/coverage-exclusions.json + the settled-metric section in
           knowledge/technology/coding-standards.md.
           AND, found while wiring it: is_gate() in verify-build-config.py was purely LEXICAL,
           so `flow-definition-language` matched no name pattern and the step count rose while
           the gate count did not — IMP-0050's hole, live again. It is now structural: anything
           invoking scripts/verify-*.py is a gate whatever it is called.
           AND: a gate whose script offers --selftest now proves itself able to fail by being
           RUN during preflight, which is a stronger assertion than a step name appearing in a
           Pester file.
Retires:   the coverage threshold's second home. `80` now appears in the coverage-threshold step
           and nowhere else in the build path.
Cites:     IMP-0132, and IMP-0115/IMP-0117/IMP-0129 as the instances already fixed in source.
Residual:  Two. (1) `[double]$CoverageThreshold = 80` is still a default inside
           src/tests/Invoke-Tests.ps1 — a second home for the number, which is IMP-0051's exact
           shape. Named as this review's retirement candidate; it is development-agent's file.
           (2) The exclusion list is judgement, and judgement can be wrong: four harness files
           are excluded on the strength of evidence that they have each been observed failing
           correctly, not on line coverage. If a fifth ever needs excluding, the cap makes that
           a decision rather than a habit.

CLUSTER: platform-contract-guessed-not-groundtruthed  (x5 NEW: IMP-0108, IMP-0112, IMP-0116,
         IMP-0124, IMP-0128 — class now x16)                                    ** 4 BLOCKERS **
Altitude:  CLASS. Three of the five are cloud-flow shapes that pack, import and report Activated,
           then fail or silently do nothing at run time. Two had already been patched as
           instances, so §2 of the promotion skill forbids a third instance patch.
Ladder row: "second instance -> generalise", and "a tool could catch it mechanically"
Becomes:   scripts/verify-flow-definition-language.py + the `flow-definition-language` build
           gate. Three checks: no select()/filter() used as an EXPRESSION; no alternate-key
           literal in a connector Row ID; no nested `item` object on an UpdateRecord.
           Proven able to fail by --selftest, 6 cases.
Retires:   nothing. Nothing validated a flow definition's connector shapes before.
Cites:     IMP-0108, IMP-0112, IMP-0116, IMP-0124
Residual:  THE GATE CURRENTLY FAILS, on six real instances in the intake flow, exactly as
           IMP-0112 predicted it would. That is the gate working. The instance fix is deferred
           with an owner — see §5 — because it restructures a runAfter chain in a flow that has
           never run live, and there is nothing to regression-test it against.
           Check 1 deliberately skips `description` values: this project's own notes explain the
           select() trap in prose, and a gate that fires on its own documentation gets switched
           off. That is a real hole — a select( hidden inside a description would pass — and it
           is the right trade.

CLUSTER: exit-zero-does-not-mean-created + v3-does-not-imply-v4  (x8 NEW: IMP-0100, IMP-0101,
         IMP-0104, IMP-0106, IMP-0113, IMP-0114, IMP-0121, and IMP-0107 — classes now x12/x5)
Altitude:  KNOWLEDGE, deliberately, and this is the one place I am choosing prose over a gate.
           Every one of these is about LIVE ENVIRONMENT STATE — a callbackregistration row, an
           environment variable value, a statecode after an import. A source-side gate cannot
           see any of it, and a gate that needs environment credentials is what C-TECH-064 has
           been unable to be since it was written.
Ladder row: "one instance, but the cause is general and a human needs to know it"
Becomes:   knowledge/technology/power-automate.md — two new sections: 'A Dataverse-Triggered Flow
           Is Not Live Until a callbackregistration Row Exists' and 'Environment variable VALUES
           do not travel'. Each carries the query to run and the shape to look for.
Retires:   nothing.
Cites:     IMP-0100, IMP-0101, IMP-0104, IMP-0106, IMP-0113, IMP-0114, IMP-0121
Residual:  Prose has failed for this class before. What makes it defensible here is that the
           post-deploy steps it describes are ALREADY named in the pipeline config as manual
           steps with owners; this gives them their reasons. If the class recurs, the escalation
           is a post-deploy smoke test with environment credentials, not a longer paragraph.

CLUSTER: no-assertion-on-shipped-content  (x3 NEW: IMP-0085, IMP-0127, IMP-0131 — class now x9)
Altitude:  CLASS for the card half, INSTANCE-ALREADY-FIXED plus a deferral for the form half.
Ladder row: "a tool could catch it mechanically"
Becomes:   verify-shipped-content.py check 4 — every readable Adaptive Card payload under
           docs/development/cards/ must parse equal to a body/messageBody string actually
           shipped in a flow definition, and no card may ship without a readable file. Fixture:
           src/tests/fixtures/known-bad/shipped-content-cards/ (exit 1). The build step now
           passes --cards.
           This is the ninth instance, so it went into the EXISTING gate for the class rather
           than becoming a tenth script.
Retires:   nothing.
Cites:     IMP-0131
Residual:  The check proves the two copies agree. It cannot prove either is correct, and it says
           nothing about the third copy of the same information — the prose in notes.md, which
           is where this drift first became visible ("THIS IS NOT AN ADAPTIVE CARD", beside a
           flow that had been posting one for a day). That paragraph was corrected by hand.

CLUSTER: gate-reassures-wrongly + two-invocation-paths-disagree  (x2 NEW: IMP-0107, IMP-0110)
Altitude:  SKILL. Both are one mistake: a confident negative drawn from an empty query result.
Ladder row: "an agent had the information and still did the wrong thing"
Becomes:   skills/how-to-verify-a-platform-contract.md §11 — 'The absence of rows is not evidence
           of the absence of events'. An empty result is one of three things and does not say
           which; pair it with a positive signal before concluding.
Retires:   nothing.
Cites:     IMP-0107, IMP-0110
Residual:  Nothing mechanical can catch a wrong inference. This is prose, at the altitude where
           prose is the only option.

CLUSTER: credential-not-on-the-machine-that-needs-it  (x1 NEW: IMP-0105 — class now x3)
Altitude:  KNOWLEDGE.
Becomes:   knowledge/technology/entra-id.md — 'Graph Auth Succeeding Is Not Graph Authorisation'.
Cites:     IMP-0105
Residual:  none.

CLUSTER: reconciliation only  (x17 NEW, no change required)
Altitude:  DIGEST. Four are capability records (IMP-0103, IMP-0118, IMP-0125, IMP-0126). Nine are
           instance defects already fixed in source and verified present during this review
           (IMP-0102, IMP-0109, IMP-0111, IMP-0115, IMP-0117, IMP-0119, IMP-0120, IMP-0122,
           IMP-0123, IMP-0129). Four are commercial findings whose artefacts exist (IMP-0096,
           IMP-0097, IMP-0098, IMP-0099).
Becomes:   the regenerated digest, plus honest statuses. IMP-0033's lesson is that an
           unreconciled log cannot tell "nothing was learned" from "nobody did the bookkeeping";
           this is the bookkeeping.
Residual:  Each was verified by checking for the artefact its proposed_change named — a presence
           check, not a correctness check.
```

## 3. Changes applied

**Two new gates, both proven able to fail.**
`scripts/verify-coverage-threshold.py` (9 selftest cases) and
`scripts/verify-flow-definition-language.py` (6 selftest cases). Both wired into
`config/revitalise-grant-automation-build.yml`; the preflight now reports 25 steps and 20 gates,
up from 23 and 18, and the gate count rose with the step count — which is the check `IMP-0050`
demanded after a gate was once added that the preflight did not recognise as one.

**One existing gate extended, at the right altitude.**
`verify-shipped-content.py` check 4, with a known-bad fixture. Ninth instance of its class, so it
went into the gate that already owns the class.

**Two structural improvements to the gate-over-the-gates.**
`is_gate()` is no longer purely lexical: anything invoking `scripts/verify-*.py` is a gate
whatever the step is called. And a gate whose script offers `--selftest` now proves it can fail by
being **executed** during preflight — verified both ways, including that a deliberately broken
selftest is rejected with the reason.

**No new constraints. The cap is three and this review used zero.** Every cluster found a more
mechanical home, or an honest knowledge line. `C-TECH-014`, `C-TECH-052` and `C-TECH-057` already
said what needed saying; what two of them lacked was an executable implementation.

## 4. Retirements

**One retired in place:** the coverage threshold's second home in the build path. `80` now lives
in the `coverage-threshold` step and nowhere else in `config/`.

**One candidate named, not actioned:** `[double]$CoverageThreshold = 80` in
`src/tests/Invoke-Tests.ps1`. It is the default of a parameter the build always passes
explicitly, which is `IMP-0051`'s exact shape — the branch nothing exercises. It should read the
number from the build config or be made mandatory. It is a `src/tests/` file and therefore
development-agent's.

**No constraint row retired.** I checked the twelve rows in build-agent's scope; none is
superseded by this review's changes, and the redundant rows in `GATE_NAME_PATTERNS` were left in
place deliberately — removing a whitelist row that the new structural rule happens to cover would
create exactly the silent hole the structural rule was added to close.

## 5. Findings left unprocessed

Three, each with a named owner and a return date. No silent caps.

**`IMP-0112` — the intake flow's six alternate-key Row IDs. `development-agent`, before the
WordPress integration is connected.** The gate is applied and names all six on every build; the
instance fix is not. Replacing six chained Get-a-row-by-id actions with one List rows call plus
six Filter arrays restructures the `runAfter` chain through four `Derive_*` actions, and the
intake flow has never executed once, so there is nothing to regression-test it against. The recipe
is exact and already proven in `REVScoringCalculateAndFlag`: one List rows filtered for all six
names, `first(body('Setting_<Key>'))?['rev_value']` per value, plus a row-count guard because List
rows returns a short array where Get-a-row-by-id returned 404. **Consequence, stated plainly: the
release build is red on `flow-definition-language` until this is done, and the first live
submission from the website will fail if it is not.**

**`IMP-0127` and `IMP-0128` — the form-format gate. `improvement-agent`, next review.** Both
instances are fixed and ground-truthed in DEV. The gate they propose is one check over two
surfaces — a column holding prose declares `Format textarea`, and every form cell bound to a
multi-line control carries `auto="true"` — and it was cut to keep this review finishable in one
session. Writing it twice, once per finding, is what the altitude rule forbids.

**`IMP-0005`, `IMP-0039`, `IMP-0085` — carried forward.** The first two are the count-coupled
assertions, deferred for the fifth time, with the discrimination rule and the 13-site inventory
already written down in the 2026-08-20 review. `IMP-0085` now has the `revisit_when` it was
missing.

## 6. Digest impact

129 entries, 129 distinct lessons. `gate-cannot-fail` reaches **x18** and
`platform-contract-guessed-not-groundtruthed` holds at **x16** — both now have a general gate
where the recurrence was happening, which is the first time that has been true of the flow-shape
half of the second class.

`no-assertion-on-shipped-content` reaches **x9** and `output-shape-defeats-the-reader` **x6**. The
second of those is the one to watch: six instances, and the only home it has ever had is prose.

## 7. Verification

Executed, all green: `verify-coverage-threshold.py --selftest` (9 checks) ·
`verify-flow-definition-language.py --selftest` (6 checks) · `verify-build-config.py` (25 steps,
20 gates, negative-test coverage OK) · `verify-shipped-content.py` with `--cards` on real source
(4 card payloads match) and **exit 1** on the drifted fixture · `verify-improvement-log.py
--check` (was exit 1 with 14 unprocessed blockers, now exit 0 with 6 reviewed deferrals) ·
`generate-known-failure-modes.py --check` (current, 129 entries).

Also executed and **failing, correctly**: `verify-flow-definition-language.py` on real solution
source, exit 1, naming six alternate-key Row IDs in the intake flow.

**Not verified.** The Pester suite was not re-run by this review — every change here is Python,
YAML, Markdown or JSON, and no `.Tests.ps1` was touched. That is the same sentence the last review
closed with, and it is the sentence that preceded a 21-point coverage drop going unnoticed, so it
is worth saying twice: **the next full build is what proves the new `coverage-threshold` step
green in the runner rather than in my hands.** Nothing in this review was verified against a live
environment.
