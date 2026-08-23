# Improvement Review 14 — 2026-08-23

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 3 → 3 clusters (1 unread `blocker`, 2 friction, all from one build run)
**Trigger:** blocker escalation — `IMP-0212`, processed immediately rather than batched
**Gate:** `APPROVE IMPROVEMENTS`
**WBS:** `system`. No contracted task is claimed here.

**Status:** ~~AWAITING `APPROVE IMPROVEMENTS`.~~ **APPLIED 2026-08-23** — see section 6.

---

## The judgement you asked for

**Yes. The fifth instance gets the structural fix, and the decisive evidence is that the rule
already existed.**

[coding-standards.md](../../knowledge/technology/coding-standards.md#L197) carries a full write-up
of this exact problem, produced after instances 1 and 2 and titled *"The decision `IMP-0005`/
`IMP-0039` deferred four times, now made"*. It is genuinely good: a discrimination table separating
**a total this project's own source declares** (fragile — derive it) from **a fixture's own
cardinality** (stable — leave it literal); a preference order (a count-free invariant, then a
derived count, then a literal with a stated caveat); and an escape hatch for the unavoidable case.

Then instances 3, 4 and 5 happened. And **one assertion in 234 carries the annotation that write-up
asks for.**

That is this agent's own regression rule in its purest form: *a recurrence after a prose change is
evidence the fix was at the wrong altitude.* The rule was never missing — it lives in a knowledge
file nobody opens at the moment they type a literal, and nothing checked it. So the fix moves to a
gate, and the gate is the same rule at the moment it applies.

**What I did not do, and would have been wrong to do:** build a gate over all 234 absolute-count
assertions. The large majority are legitimately literal, and a gate that fires on correct code is
how `gate-fires-on-nothing` (x3) happens.

---

## 1. Narrowing, measured rather than assumed

| Step | Count |
|---|---|
| `Should -Be <literal>` anywhere in the suite | **234** |
| …of the `.Count \| Should -Be <literal>` shape | **85** |
| …whose asserted **subject traces to solution source** | **7** |
| …neither derived nor annotated → reported | **6** |

The narrowing is `coding-standards.md`'s own tell made executable: *does the number describe
something under `src/solutions/`, or something under `src/tests/fixtures/` or a mock's own setup?*
Source means one of seven named `Get-Rev*` readers, or a deployment-settings array.

**The discrimination was tightened twice, against real false positives, and both are now fixtures:**

- `@(Get-FakeDataverseCalls -Method PATCH).Count | Should -Be 0` — flagged because its `It` block
  mentioned a settings array elsewhere. A mock's call count is a fixture's cardinality. Fixed by
  tracing the *asserted subject* rather than scanning the block.
- `$body.Attributes.Count | Should -Be 1` — flagged because `$body` chains back to
  `Get-RevEntityDefinition`. Fixed by making a mock assignment terminal in the walk.

---

## 2. Clusters and promotion decisions

```
CLUSTER A: the fifth stale count  (IMP-0212, blocker)
Altitude:  CLASS, escalated from prose to a gate. x5 (IMP-0005, IMP-0039, IMP-0120, IMP-0155,
           IMP-0212) and the second instance inside this same test file. §2 of the promotion
           skill forbids a sixth instance patch; the coordinator asked directly whether this
           finally warrants the general fix, and it does.
Ladder row: "a tool could catch it mechanically", after "an agent had the information and still
           did the wrong thing" was already tried — the information exists and was not enough.
Becomes:   scripts/verify-source-derived-test-counts.py + build step
           `source-derived-test-counts` (SOFT) + C-TECH-067 (SOFT).
Retires:   nothing. coding-standards.md's write-up is not superseded — it is now ENFORCED, and
           the gate's message points back at its preference order.
Cites:     IMP-0212, IMP-0005, IMP-0039, IMP-0120, IMP-0155, IMP-0150
Residual:  Three, all in the script's docstring. (1) It reads one `It` block textually, so a
           collection built in a distant `BeforeAll` is invisible — a floor, not a proof.
           (2) It cannot read intent: EnsureSchema.Tests.ps1's `$body.Attributes.Count` asserts
           a TRANSFORMATION's invariant reached through a source reader and is correct as a
           literal. Annotating it "count-coupled" would be a lie, so the gate tolerates being
           wrong about it. (3) It asks for derivation, not arithmetic — a wrong derived count
           passes.
```

```
CLUSTER B: a config that changed under a running build  (IMP-0213)
Altitude:  INSTANCE -> an agent-file step, which is what the finding proposed for itself.
           Not a gate: nothing in a build can prevent a concurrent session, only detect it.
Ladder row: "the ORDER of steps was wrong" — the missing thing is a re-check between preflight
           and packaging.
Becomes:   build-agent.md records BUILD_CONFIG_SHA at activation step 1 and re-hashes at a new
           step 7a before packaging; on drift, re-run preflight, run any newly-inserted earlier
           step, and record old/new sha in the manifest.
Retires:   nothing.
Cites:     IMP-0213, IMP-0080
Residual:  It closes the window between preflight and packaging. A config changing DURING a
           single long step is still invisible, and a concurrent edit to something other than
           the build config (a script a step calls, a settings file) is not covered at all.
           Naming that rather than implying the window is fully shut.
```

```
CLUSTER C: a third-party console.error  (IMP-0214)
Altitude:  INSTANCE -> a documentation line, in the list that already holds two peers.
Ladder row: "one instance, the cause is general and a human needs to know it".
Becomes:   the dev summary's C-TECH-055 triaged-warnings list, now 3.
Retires:   nothing.
Cites:     IMP-0214, IMP-0177
Residual:  The reusable half is the METHOD — grep node_modules for the exact message, check for
           a NODE_ENV guard — and a method in a dev summary reaches whoever reads that summary,
           nobody else. Left there deliberately: one warning is not evidence for a rule.
```

---

## 3. Changes applied

| # | Type | Target | Change |
|---|---|---|---|
| 1 | script | `scripts/verify-source-derived-test-counts.py` (new) + build step `source-derived-test-counts` | Reports a literal count whose subject traces to solution source and is neither derived nor annotated. 9 selftest fixtures. **SOFT** |
| 2 | constraint | [C-TECH-067](../../constraints/technology/technology-constraints.md#L135) | SOFT. Derive both sides from source, or annotate; and a test is never the sole assertion of a fact a build gate already derives |
| 3 | agent | [build-agent.md](../../agents/build-agent.md#L39) | `BUILD_CONFIG_SHA` at step 1, re-hash at step 7a before packaging, act on drift, record it in the manifest |
| 4 | doc | [dev summary](../../docs/development/revitalise-grant-automation-dev-summary.md) | Keyborg stderr triaged into the C-TECH-055 list (now 3, all accepted) with the evidence and the reusable method |

**Constraint budget: 1 of 3 used.** At x5 the class has earned a row; SOFT rather than HARD for the
reason in section 4.

### Why SOFT, stated once and clearly

**`IMP-0212`'s harm was a halted build.** A gate that blocks the build to warn that a literal
*might* go stale would reproduce that harm across a wider surface — six assertions instead of one.
It exits 0 with findings, matching [verify-derived-counts.py](../../scripts/verify-derived-counts.py)'s
convention for the same class of drift, and `coding-standards.md` already frames the retrofit as
*"scoped implementation work for whoever next touches `src/tests/`"* rather than a wholesale
rewrite. **Promote to HARD when the live count reaches zero and holds** — at that point a new
finding is a regression rather than a backlog item.

### What I deliberately did not touch

**`src/tests/provisioning/DeploymentSettings.Tests.ps1`.** development-agent holds it concurrently
for the mechanical fix. Editing a file under another live session is precisely `IMP-0213`, appended
from the same build run — repeating it inside the review that processes it would be indefensible.
The gate will confirm the fix when that lands: the file currently accounts for 3 of the 6 reported
assertions, and the audited-tables one is not among them, because that literal is the one being
replaced.

---

## 4. Retirements

**Checked, and none.** One SOFT constraint added. The standing consolidation candidate —
[C-TECH-001](../../constraints/technology/technology-constraints.md#L34),
[C-TECH-002](../../constraints/technology/technology-constraints.md#L35),
[C-TECH-044](../../constraints/technology/technology-constraints.md#L86) — is unchanged and not
taken for the fourth review running. It is now the oldest un-acted item in this system and should
be the next review's first agenda point rather than its last paragraph.

---

## 5. Findings left unprocessed

No silent caps.

| Finding(s) | Why not processed | What closes it |
|---|---|---|
| `IMP-0197`, `IMP-0205` | Untouched by standing instruction — the `power.config.json` breach-vs-exception question is still undecided | the reviewer's answer |
| `IMP-0198` | Parked at review 10's gate | the keyword against that document |
| `IMP-0112`, `IMP-0152` | Standing deferrals, reasons unchanged | as recorded on each |

**One thing found and not fixed, named rather than absorbed:**
[verify-derived-counts.py](../../scripts/verify-derived-counts.py) — the sibling gate for exactly
this class of drift — **is not wired into `build.yml` at all.** It runs only when somebody runs it
by hand. That is `IMP-0174`'s rung (present but never executed) and it is not this review's finding
to fix on the way past; wiring a gate changes what every future build reports and deserves its own
decision. Reported here so it is not discovered a third time.

---

## 6. Applied

`APPROVE IMPROVEMENTS` — blocker trigger, processed immediately per `agents/WORKFLOW.md`.

**Entries moved to APPLIED:** `IMP-0212`, `IMP-0213`, `IMP-0214`, each with an `evidence_grep`
needle.
**Entries rejected:** none.
**Findings appended:** none — every trigger this session's work hit was already recorded by the
build-agent that hit it.

**Gate state:** build preflight PASS at 39 steps / 28 gates; `verify-constraint-verifiers.py` PASS
(63 paths, 74 rows); `source-derived-test-counts` reports 6 (SOFT, non-blocking);
`assumption-register` PASS; digest current at 211 entries.
