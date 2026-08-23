# Improvement Review 8 — 2026-08-21

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 13 `NEW` → 6 clusters
**Trigger:** blocker escalation. `IMP-0178` (`rev_review` has no audit trail in DEV) was appended by
test-agent from a BLOCKED test cycle, alongside two friction findings.
**Gate:** `APPROVE IMPROVEMENTS`
**WBS:** `system`. The findings guard delivery tasks 6.1–6.5 and 4.3. No contracted task is claimed here.

**Status:** AWAITING `APPROVE IMPROVEMENTS`. Nothing in section 3 has been applied. Three things
*were* done, because none of them edits a rule: one new finding was appended, `reviewed_in` was
stamped on the ten entries whose disposition this review changes, and the digest was regenerated.

---

## The headline

**This system does not have a proposal problem. It has an application problem, and it now has a
complete, mechanical list of what is outstanding.**

Reviews 5, 6 and 7 produced 33 proposals. I checked every one against the working tree rather than
against any document's text: **27 are on disk, 6 are not.** That is a far better record than the last
three reviews believed — review 6's own header says *"Nothing in section 3 has been applied"* while
nine of its twelve items and its one retirement are in fact applied.

The reason nobody could tell is one field. Four findings carry an
[`evidence_grep`](../../scripts/verify-improvement-log.py#L270) — a file and a needle that proves the
fix shipped — **whose needle is absent from disk right now**, and the gate never looks, because
`evidence_grep` is evaluated for `APPLIED` entries and for the
[`already-fixed`](../../scripts/verify-improvement-log.py#L35) state only. Those four needles are
exactly the outstanding approved work:

| Finding | Approved in | The artefact that does not exist |
|---|---|---|
| `IMP-0148` | review 5, items 1–3 | `provisioning/dataverse/verify-flow-trigger.ps1` — the canary probe |
| `IMP-0161` | review 6, item 9 | the `getClient(dataSourcesInfo)` ground truth in [code-apps.md](../../knowledge/technology/code-apps.md) |
| `IMP-0162` | review 6, item 7 | escalation conditions in [models.yml](../../config/models.yml#L246) |
| `IMP-0166` | review 6, item 12 | `EX-004` in [known-exceptions.json](../../contract/known-exceptions.json) |

All four currently read as **"deferred with a recorded reason, accepted as a reviewed deferral."** The
gate is not silent about them; it is actively reassuring about them. Approved work that nobody did is
being reported as a decision somebody made.

The data to catch this is already in the log and the machinery is already 90 % built. Item 1 is a few
lines, and it produces this table automatically from then on.

---

## 1. Regression check — did the last reviews' changes work?

Verified against the working tree, not against the documents. `IMP-0154`'s lesson is that a review
document is a claim; so, it turns out, is a review document's own *status header*.

| Review | Proposals | On disk | Not on disk |
|---|---|---|---|
| 5 | 10 | 6 | 4 (items 1, 2, 3 — one cluster; item 10) |
| 6 | 12 + 1 retirement | 10 | 3 (items 7, 9, 12) |
| 7 | 10 | 10 | 0 |
| **Total** | **33** | **27** | **6** |

**Review 7's own record is clean, and it is the only review of the three that was approved and applied
in one sitting.** Both its build steps are on disk —
[`pipeline-config-preflight`](../../config/revitalise-grant-automation-build.yml#L121) and
[`tad-coverage`](../../config/revitalise-grant-automation-build.yml#L242) — which is what its two
blockers were about.

### Three prior changes worked, measurably

| Prior change | Class it targeted | Recurred? | Verdict |
|---|---|---|---|
| [verify-derived-counts.py](../../scripts/verify-derived-counts.py) + its registry (review 6, item 5) | `hand-maintained-count-drifts-from-source` | Yes — `IMP-0176`, a third instance | **Working as designed.** The gate runs and reports 8 live drifts across 6 registered claims. `IMP-0176` needs a registry row, not a script — which is precisely the outcome item 5 was built to produce |
| [verify-column-security-membership.py](../../scripts/verify-column-security-membership.py), wired at [build.yml#L350](../../config/revitalise-grant-automation-build.yml#L350) | `platform-contract-guessed-not-groundtruthed` | No | **Working.** It also *superseded* review 5 items 5, 8 and 9 with something stronger than proposed — a HARD gate instead of a skill line |
| The four-state blocker trigger in [verify-improvement-log.py](../../scripts/verify-improvement-log.py#L40) (review 5 item 7, extended by review 6 item 6) | `learning-substrate-destroyed` | **Yes — this review's headline** | **Working, and it is why this review has a real list.** It correctly separated 6 unread from 7 reasoned. The fifth state is the one it lacks |

### The recurrence that matters

**A gate fired, reported the wrong thing, and review 6 predicted it in writing.** Review 6's cluster G
said it was *"the second review in a row forced to overload one field to mean two things"* and asked
for the state to be modelled properly. The state was added for *already-fixed*; the mirror case —
*approved and not applied* — was not, because at that moment nothing had been approved. Review 7 then
approved things. One review later the predicted failure is here.

Per the regression rule, a gate that fires about the wrong thing is a finding in its own right:
appended as `IMP-0181`.

### One correction to review 6

Review 6's status header states that nothing in its section 3 was applied. **Nine of its twelve items
and its retirement of [C-TECH-023](../../constraints/technology/technology-constraints.md#L63) are on
disk.** The header was written before approval and never updated after it. A dated correction is added
to that document by item 1's companion edit, so the next reader inherits the correction rather than
the claim.

---

## 2. Clusters and promotion decisions

### CLUSTER A — the log cannot say "approved, and nobody did it"

```
CLUSTER:    a finding's disposition has five real states and the log can represent four
            (IMP-0181 new; instances IMP-0148, IMP-0161, IMP-0162, IMP-0166;
             lineage IMP-0154, IMP-0169, IMP-0033)
Class:      learning-substrate-destroyed (x15)
Altitude:   CLASS — third generation of the same substrate defect in three days. IMP-0154 was a
            REVIEW leaving no trace, IMP-0169 a DELIVERY FIX leaving no trace, this one an
            APPROVAL leaving no trace
Ladder row: "the system's own memory failed -> a read-path change"
Becomes:    item 1 — evaluate evidence_grep on NEW entries in BOTH directions, and require it
            on anything moved to APPLIED from this review forward
Retires:    nothing
Cites:      IMP-0181, IMP-0148, IMP-0161, IMP-0162, IMP-0166, IMP-0154, IMP-0169, IMP-0174
Residual:   it only catches an unapplied change whose finding carries an evidence_grep. A
            proposal approved with no needle recorded stays invisible, which is exactly why the
            second half of item 1 makes the needle mandatory going forward rather than optional.
            It also cannot verify that a needle that IS present means the change is CORRECT —
            only that something with that signature shipped
```

The direction of the error is what makes this expensive. A missing gate leaves you uncertain; this one
returned a confident answer — *accepted as a reviewed deferral* — about four items of approved,
unfinished work. Two of the four (`IMP-0161`, `IMP-0162`) were parked for eleven and five days
respectively behind a sentence that reads like a decision and was actually a to-do.

Note the honest constraint on the retrospective half: only **26 of 164** applied entries carry a
needle. Requiring one retroactively would produce 138 errors about work that is genuinely done, which
is how a gate teaches people to route around it (review 6's cluster A made exactly this call). So the
requirement binds **from this review forward**, and the 138 legacy entries are reported once as a
dated note.

### CLUSTER B — a table created live has no audit trail, and this was predicted

```
CLUSTER:    a Dataverse table created outside a deploy does not inherit table auditing, and no
            settings file or gate covers it (IMP-0178 blocker, IMP-0085)
Class:      platform-state-divergence (x4) + no-assertion-on-shipped-content (x10)
Altitude:   CLASS — and IMP-0085's own revisit condition has now fired
Ladder row: "a tool could catch it mechanically"
Becomes:    items 2, 3, 4 and one reviewer action (item 5)
Retires:    nothing
Cites:      IMP-0178, IMP-0085, IMP-0082, IMP-0086
Residual:   the gate proves a table is DECLARED for auditing in every settings file. It cannot
            prove the switch is ON in an environment — that needs a live query and it is
            C-TECH-064's job, amended here to name this gate as its source-side half. The live
            switch on rev_review remains a human action; no gate can perform it
```

This is the cluster where the system already knew the answer and had written it down. `IMP-0085` says,
in the digest today: *"Five tables … are still to be built and will each need it."* The sixth table was
built and needed it. Its deferral reason said *"revisit when the next Dataverse table is built (Phase
3, tasks 6.4 / 8.1)"* — task 6.4 is exactly what shipped, and the revisit did not happen because
nothing connected the deferral's condition to the event.

Three measurable facts, each a one-line check today:

- Tables on disk under `Entities/`: **six**. Tables in `auditedTables` in
  [test-settings.json#L331](../../provisioning/deploymentSettings/test-settings.json#L331) and
  [prd-settings.json#L359](../../provisioning/deploymentSettings/prd-settings.json#L359): **four**.
  `rev_grant` and `rev_review` are in neither.
- **No DEV settings file declares `auditedTables` at all**, so
  `ensure-auditing.ps1 -Env dev` has never had a runnable path — even though its own parameter block
  accepts `dev`. That is why the first five tables were switched on by hand in the admin centre.
- [ensure-schema.ps1#L394](../../provisioning/dataverse/ensure-schema.ps1#L394) reports `CREATED` for a
  new entity and says nothing about auditing, which is correct behaviour for a schema script and a
  silent handoff to nobody.

The general property: *every table the solution declares must be declared for auditing in every
environment's settings, and that is derivable from source.* The known-bad fixture exists on this tree
right now, which is the strongest form of coverage proof this skill asks for.

### CLUSTER C — a gate that reads a cache and calls it a result

```
CLUSTER:    verify-wbs-chain.py reads logs/state/wbs-state.json without regenerating it, and
            reported a table ABSENT that had been on disk for a day (IMP-0180)
Class:      gate-cannot-fail (x24)
Altitude:   CLASS — second instance of IMP-0089's exact shape in a different pair of scripts
Ladder row: "second instance -> generalise. Instance patches are forbidden here."
Becomes:    item 6
Retires:    nothing
Cites:      IMP-0180, IMP-0089
Residual:   the fix makes one pair of scripts honest. It does not find a THIRD pair where a gate
            reads a generated artefact it did not generate; that needs a convention (a gate
            declares its generated inputs) and one more instance to justify the cost
```

[verify-wbs-chain.py#L40](../../scripts/verify-wbs-chain.py#L40) names the state file and
[#L78](../../scripts/verify-wbs-chain.py#L78) tells you to run the generator *only when the file is
missing*. A file that is present and stale is the worse case and is handled as success. `IMP-0089`
established the principle — *a preflight result that depends on files left behind by a previous run is
not a result* — and fixed the instance it found.

### CLUSTER D — an evidence rule pointing at an architecture that was superseded

```
CLUSTER:    four evidence rules for WBS 6.1/6.2/6.3/6.5 check a Model-Driven App path for a
            deliverable ADR-003 made a Code App eleven days earlier (IMP-0179)
Class:      evidence-rule-targets-a-superseded-implementation-path (x1), and the fifth member of
            the evidence-rule-SHAPE family (IMP-0067, IMP-0097, IMP-0099, IMP-0140)
Altitude:   INSTANCE on the four paths, CLASS on the detection
Ladder row: "a tool could catch it mechanically"
Becomes:    item 7
Retires:    nothing
Cites:      IMP-0179, IMP-0067, IMP-0097, IMP-0099
Residual:   "the path has never existed in git history" catches a rule pointing at an artefact
            nobody ever built. It does NOT catch a rule pointing at a path that used to exist
            and was legitimately moved — that resolves to a real commit and looks healthy
```

The detection gap is the interesting half and `IMP-0179` states it exactly: `verify-wbs-chain.py`
reports **disagreements** between a claim and its evidence. Here the claim is null and the evidence is
false-absent, so the two agree on *"not started"* and nothing is reported. About 7.5 hours of built,
tested work is invisible to the contract chain, and the chain is content.

### CLUSTER E — a hand-narrated count, third instance, and the gate for it already exists

```
CLUSTER:    the Dev Summary's "four pre-existing pack warnings" is eight (IMP-0176)
Class:      hand-maintained-count-drifts-from-source (x3)
Altitude:   CLASS — but the class fix SHIPPED in review 6 (item 5)
Ladder row: none needed. This is a registry row in an existing gate
Becomes:    item 8
Retires:    nothing
Cites:      IMP-0176, IMP-0150, IMP-0160
Residual:   the registry only checks claims somebody registered, and there is no mechanical way
            to find an unregistered number in prose. Unchanged from review 6, and still true
```

Worth stating plainly because it is the system working: a third instance of a class arrived and cost
one registry row instead of one script. The same run also shows the gate reporting **8 uncorrected
drifts** — the secured-column count is still stated as 39 against a source figure of 51 in five places
including a review document. Item 8 corrects them, because a SOFT gate that is permanently red is a
gate people stop reading.

### CLUSTER F — two protocol and documentation notes

```
CLUSTER:    a live write refused from a background dispatch succeeded from the foreground
            (IMP-0173, capability); npm's warning stream has never been triaged (IMP-0177)
Class:      foreground-write-not-refused (x1); untriaged-tool-warning (x1)
Altitude:   INSTANCE for both -> an agent-file edit and a documentation line
Ladder row: "an agent had the information and still did the wrong thing" / "one instance, the
            cause is general and a human needs to know it"
Becomes:    items 9 and 10
Retires:    nothing
Cites:      IMP-0173, IMP-0170, IMP-0177
Residual:   IMP-0173 is one observation of a classifier's behaviour, not a documented contract.
            It is written as "try this first", never as "this will work" — the reviewer-executed
            fallback stays exactly where it is
```

`IMP-0173` is a capability worth keeping: five prior findings (`IMP-0021`, `IMP-0040`, `IMP-0084`,
`IMP-0133`, `IMP-0170`) all handed the reviewer a command, and every one of them was a background
dispatch. The variable was never isolated. It costs one step in an existing protocol at
[pipeline-agent.md#L73](../../agents/pipeline-agent.md#L73) and its binding pointer at
[development-agent.md#L89](../../agents/development-agent.md#L89).

---

## 3. Proposed changes

Ten items. **Six of them are finishing work that was already approved**, which is the point of this
review — the four outstanding needles from the headline plus the two corrections a red SOFT gate is
already reporting.

| # | Type | Target | Change | Cites | Mechanically verifiable? |
|---|---|---|---|---|---|
| 1 | script | [verify-improvement-log.py#L270](../../scripts/verify-improvement-log.py#L270) | **(a)** Evaluate `evidence_grep` on `NEW` entries in BOTH directions. Needle present → the existing `already-fixed` note. Needle **absent** on an entry whose `deferred_reason` or new `approved_in` field records an approval → a fifth state, `approved-not-applied`, reported as a **FAIL** naming the artefact that does not exist. **(b)** Require an `evidence_grep` on any entry moved to `APPLIED` whose `proposed_change.type` is not `none`, enforced for entries applied by review 8 or later; the 138 legacy entries become one dated NOTE, never an error. **(c)** A dated correction in review 6's status header | IMP-0181, IMP-0148, IMP-0161, IMP-0162, IMP-0166, IMP-0154, IMP-0169, IMP-0174 | YES — the four broken needles are the opening fixture; fixtures for all five states |
| 2 | script (new) | `scripts/verify-audited-tables.py`, wired as a build gate beside [secret-scan](../../config/revitalise-grant-automation-build.yml#L176) | HARD. Every table directory under `src/solutions/*/Entities/` must appear in `dataverse.auditing.auditedTables` in every deployment settings file that declares the key. Fails when it resolves zero tables or zero settings files (the `IMP-0007` shape) | IMP-0178, IMP-0085, IMP-0082 | YES — **currently RED**: `rev_grant` and `rev_review` are missing from both files, so the known-bad fixture is the live tree |
| 3 | config | [test-settings.json#L331](../../provisioning/deploymentSettings/test-settings.json#L331), [prd-settings.json#L359](../../provisioning/deploymentSettings/prd-settings.json#L359), plus a DEV settings path | Add `rev_grant` and `rev_review` to both `auditedTables` arrays, and add a `dataverse.auditing.auditedTables` block to a DEV settings file so `ensure-auditing.ps1 -Env dev` has a runnable path for the first time — today no DEV file declares the key, which is why the first five tables were switched on by hand | IMP-0178 | YES — item 2 goes green |
| 4 | script | [ensure-schema.ps1#L394](../../provisioning/dataverse/ensure-schema.ps1#L394) | On reporting `CREATED` for a new entity, also emit a named `ACTION REQUIRED` line: the table needs its audit switch, with the exact `ensure-auditing.ps1` invocation and the `EntityDefinitions` read-back query. A schema script must not create an unaudited table silently | IMP-0178, IMP-0085 | YES — asserted in `src/tests/provisioning/EnsureSchema.Tests.ps1` |
| 5 | **reviewer action** | live DEV metadata write | Turn table auditing on for `rev_review` (D-026). Per `IMP-0173`, attempt it from the lead-agent's own foreground session first; on refusal, hand over the exact `PATCH` with its before/after `EntityDefinitions(LogicalName='rev_review')?$select=IsAuditEnabled` query. **No gate can do this** and the test cycle stays BLOCKED until it is done | IMP-0178, IMP-0173, IMP-0084 | YES — the live read-back is the proof, and it is a read, never refused |
| 6 | script | [verify-wbs-chain.py#L40](../../scripts/verify-wbs-chain.py#L40) | Regenerate `logs/state/wbs-state.json` via `derive-wbs-state.py`'s write path before reading it — or refuse to run when the state file is older than the newest file under `contract/` or `src/solutions/`. A present-but-stale cache must not read as success | IMP-0180, IMP-0089 | YES — touch a file under `src/solutions/` and the gate must refuse or regenerate |
| 7 | config + script | [evidence-map.json#L343](../../contract/evidence-map.json#L343), [#L349](../../contract/evidence-map.json#L349), [#L356](../../contract/evidence-map.json#L356), [#L369](../../contract/evidence-map.json#L369) | Repoint all four `AppModules/rev_trusteereview` rules at `src/code-apps/trustee-review-portal/` per ADR-003. Then have `derive-wbs-state.py` report an evidence rule whose target path has **never existed in git history** — the case that produces no warning today because a false-absent rule and a null claim agree | IMP-0179, IMP-0067, IMP-0097, IMP-0099 | YES — the four rules must flip from absent to satisfied, and the staleness check must fire on a fabricated path |
| 8 | config | [derived-counts-registry.json#L4](../../scripts/derived-counts-registry.json#L4) | One registry row for the pack-warning count (`not defined in customizations`, currently 8, narrated as 4), **and** correct the 8 drifts the gate already reports — the secured-column count is stated as 39 against a source figure of 51 in five places | IMP-0176, IMP-0150, IMP-0160 | YES — `python3 scripts/verify-derived-counts.py` must exit 0 |
| 9 | agent | [pipeline-agent.md#L73](../../agents/pipeline-agent.md#L73), pointer at [development-agent.md#L89](../../agents/development-agent.md#L89) | One step before the `REVIEWER ACTION REQUIRED` fallback: on a classifier refusal from a dispatched or background agent, the lead-agent retries the identical call in its own foreground session first. Written as *try this first*, never as a guarantee | IMP-0173, IMP-0170 | N/A — instruction, but its absence is greppable |
| 10 | knowledge | `docs/development/revitalise-grant-automation-dev-summary.md` | Add the `glob@10.5.0` deprecation to the triaged-warnings list beside the Vite chunk-size warning: dev/test-only transitive dependency of `@vitest/coverage-v8`, `npm audit` reports 0 vulnerabilities, accepted. First time `code-app-install` has ever executed in a real build | IMP-0177 | N/A — but the `npm audit` figure was executed |

**Constraint budget: 0 of 3 used.** One existing row is amended:
[C-TECH-064](../../constraints/technology/technology-constraints.md#L134)'s `Verify By` gains item 2 as
its **source-side half**, so the rule names both the declaration check and the live query. The
constraint that governs cluster B already exists in both halves —
[C-DOM-010](../../constraints/domain/domain-constraints.md#L47) and
[C-DOM-011](../../constraints/domain/domain-constraints.md#L48) for the obligation,
[C-DOM-032](../../constraints/domain/domain-constraints.md#L94) for the source side. Nothing was missing
except a gate, which is the right conclusion nine times out of ten.

---

## 4. Retirements

**Review 6's one retirement landed.** [C-TECH-023](../../constraints/technology/technology-constraints.md#L63)
now reads `status: retired 2026-08-21` with its `retired_reason` on the row, so the carried-forward item
from reviews 4 and 5 is closed and the Retired table is no longer empty.

**Retirement check performed: 47 active technology constraints reviewed. No clean retirement candidate
found, and I am not proposing one.** The honest finding is a *consolidation* candidate, unchanged in
substance from review 6 and now one row better evidenced:

Three of the eight review-only `Verify By` rows —
[C-TECH-001](../../constraints/technology/technology-constraints.md#L34) (no hardcoded secrets),
[C-TECH-002](../../constraints/technology/technology-constraints.md#L35) (secrets from the approved
manager) and [C-TECH-044](../../constraints/technology/technology-constraints.md#L86) (prefer OIDC or
certificates) — govern one subject and are now backed by an executable gate that review 6 could not
cite, [secret-scan](../../config/revitalise-grant-automation-build.yml#L176). Collapsing them into one
row whose `Verify By` names that step would replace three unenforceable rows with one enforced one.

I am deliberately **not** doing it in this review. It touches three HARD rows about credentials, the
gate covers the *hardcoding* half and not the *sourcing* half, and this review's whole argument is that
the system should finish approved work before opening new fronts. It is named here so the next review
inherits the analysis rather than re-deriving it.

---

## 5. Findings left unprocessed

No silent caps. Three, each already carrying a reason that still holds, and each left pointing at
review 6 rather than re-stamped here — their disposition is unchanged and review 6's reasoning stands.

| Finding | Class | Why still deferred | Revisit when |
|---|---|---|---|
| `IMP-0085` | `no-assertion-on-shipped-content` | **Partly discharged by item 2.** The source-side half — every table declared for auditing in every settings file — becomes a gate here. The live half still needs environment credentials this session does not hold | Item 2 is applied; then the residue is only the live query, which is `C-TECH-064`'s job |
| `IMP-0112` | `platform-contract-guessed-not-groundtruthed` | Unchanged. The gate is applied and names all six alternate-key Row IDs on every build; the instance fix restructures a flow that has never run live, so there is nothing to regression-test against | Before the WordPress integration is connected to DEV |
| `IMP-0152` | `gate-cannot-fail` | Unchanged, and still correct to hold. A named-membership evidence rule flips WBS task 0.5 from complete to partial, which changes what the PM and commercial agents report | A review with pm-agent present, or immediately if task 0.5 is claimed for acceptance or an invoice |

`IMP-0148`, `IMP-0161`, `IMP-0162` and `IMP-0166` are **no longer deferrals**. They are approved work
reclassified as outstanding, stamped `reviewed_in` here, and item 1 is what keeps them visible until
they are done.

**One residual I am naming rather than fixing.** Review 5's items 8 and 9 — adding `lead-agent` to
[how-to-verify-a-platform-contract.md](../../skills/how-to-verify-a-platform-contract.md#L3)'s *Used
by* line, and having [lead-agent.md](../../agents/lead-agent.md) load it before writing a dispatch that
asserts platform behaviour — were superseded by a HARD gate that is stronger for that *instance*
(`verify-column-security-membership.py`). The general lesson behind them, *an instruction is an
artefact*, still has no home: `lead-agent.md` has zero references to that skill. Left open on purpose;
it is a read-path change and this review already carries one.

---

## 6. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 177 | 178 |
| Distinct lessons | 177 | 178 |
| `NEW` entries | 13 (6 unread, 7 reported as accepted deferrals) | 14 (0 unread, 11 awaiting-approval, 3 reviewer-deferred) |
| Recurring classes (x≥2) | 23 | 23 — `learning-substrate-destroyed` reaches x15 |
| Largest class | `gate-cannot-fail` x24 | `gate-cannot-fail` x24 |
| Technology constraints, active | 47 | 47 — 0 proposed, 0 retired, 1 `Verify By` amended |

Regenerated with `python3 scripts/generate-known-failure-modes.py` and confirmed current with
`--check` (exit 0).

The four reclassified entries land in `awaiting-approval` rather than in a state of their own,
**because the state of their own is item 1 and item 1 is not applied.** Their `deferred_reason` was
removed — they are not deferrals — and replaced with an `approved_in` field naming the review and item
that approved each one. That field is the data item 1's rule reads; until item 1 exists, the honest
representation is "this review processed them and is waiting."

`python3 scripts/verify-improvement-log.py --check` **stays red on purpose** until the keyword arrives:
`IMP-0178` is a blocker now in the `awaiting-approval` state, which review 5 item 7 deliberately kept
as a FAIL so a stalled review cannot go quiet. That behaviour is the reason this review exists rather
than being the fourth to stall unnoticed.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-21-improvement-review-8.md

Findings processed: 13 NEW  →  6 clusters (1 appended, 10 stamped, 3 carried unchanged)
Regression check:   33 prior proposals audited across reviews 5-7 — 27 on disk, 6 not.
                    1 class recurred after a gate fix (learning-substrate-destroyed x15):
                    the log gate reports 4 items of approved, unapplied work as
                    "accepted reviewed deferrals". Review 6 predicted this in writing.
Proposed:           0 constraints (cap 3), 5 gates/scripts, 3 config, 1 agent-file edit,
                    1 knowledge line, 1 reviewer action, 0 retirements
                    (1 Verify By amended; 1 consolidation candidate named, not taken)
Altitude calls:     4 generalised from instance to class, 2 left as notes
Blocker:            IMP-0178 (rev_review has no audit trail in DEV) — items 2-5.
                    Item 5 is a live write only a human can complete; the test cycle
                    stays BLOCKED until it is done.
Digest:             regenerated — 178 lessons, 23 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```
