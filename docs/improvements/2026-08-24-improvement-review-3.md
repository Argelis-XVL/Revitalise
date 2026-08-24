# Improvement Review 23 — 2026-08-24

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 9 `NEW` (`unread`) → 5 clusters
**Trigger:** blocker escalation — [IMP-0259](../../logs/improvement-log.jsonl#L256), unread, routed immediately per [WORKFLOW.md → Processing triggers](../../agents/WORKFLOW.md#L207)
**Status:** ~~AWAITING `APPROVE IMPROVEMENTS`.~~ **APPROVED and APPLIED 2026-08-24** by the reviewer (Xander Lykopoulos). All ten changes are in the tree. Application itself found three things the review had wrong or missing, including a correction to the blocker's own premise — see section 9.
**Scope note:** the third review dated 2026-08-24. [Review 21](./2026-08-24-improvement-review.md) is parked at its own gate on a different finding and is untouched here. [Review 22](./2026-08-24-improvement-review-2.md) was approved and applied by a concurrent session while this review was being derived — see section 1.
**WBS:** the defects behind this review serve [task 0.4](../../contract/wbs.json); the review itself is system work, not billable ([C-COM-002](../../constraints/commercial/commercial-constraints.md))

---

## Summary

Two live schema defects were fixed correctly, and the interesting thing in this batch is not either fix — it is that **the gate built the day before to catch exactly that class of defect ran, passed, and was looking in the wrong place.** It compared source against source; the bug was between source and the code that sends source to the platform. That distinction is general, it is measurable, and I found one more instance of it still latent in the tree.

Separately, one of the two constraint rows that state a fixture count is stale, and so is a second one nobody had noticed. That class has now recurred eight times and was patched again minutes before this review started.

**What needs you:** one confidentiality decision that is genuinely yours (a provider's real organisation name is readable by anyone with table Read), and approval of one new constraint, two amendments and three gate changes.

---

## 1. Regression check — did the last review's changes work?

[Review 20](./2026-08-23-improvement-review-8.md) was the last review applied before this batch; its five changes are audited below. Review 22 was applied by another session *during* this derivation, so its one change is audited too.

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| Review 20 change 1 — two new checks in [verify-field-security-coverage.py](../../scripts/verify-field-security-coverage.py#L79) | yes | a column marked confidential that the platform will not secure | **YES — the next day, [IMP-0255](../../logs/improvement-log.jsonl#L252)** | **The gate was mis-scoped, not un-wired.** It ran and passed. See below — this is the most important row in the review |
| Review 20 change 2 — [C-TECH-070](../../constraints/technology/technology-constraints.md#L141) | yes | same | same | **Its own description went stale within a day** ([IMP-0260](../../logs/improvement-log.jsonl#L257)), and its substance is now wrong in a second way. See cluster B |
| Review 20 change 3 — [pipeline-agent.md](../../agents/pipeline-agent.md) steps 3a/4 | yes | a live write the harness refuses | not in this batch | No recurrence here. The open instance is parked at Review 21's gate and is not mine to re-derive |
| Review 20 change 4 — `refusal_context` in [verify-improvement-log.py](../../scripts/verify-improvement-log.py) | yes | a refusal recorded without its session context | no | **Worked.** Nothing in this batch records a refused live operation |
| Review 20 change 5 — multi-file closure accounting | yes | a finding closed on a subset of the files it named | no | **Worked, and its premise was falsified.** The gate assumes a finding's `proposed_change` names the right files. [IMP-0258](../../logs/improvement-log.jsonl#L255) is the case where two of three named files needed no change at all — so the gate can now demand an accounting for the wrong targets. Strengthens cluster C rather than undermining the gate |
| Review 22's change — registering the two retirement-count sentences | yes, minutes ago | a hand-typed count in a rule file | **YES — immediately, [IMP-0263](../../logs/improvement-log.jsonl#L260)** | **Fixed the two sentences it registered; the class recurred elsewhere in the same hour.** Four other registered claims are drifting now. Eighth instance. See cluster E |

**The first row is the one that matters, and it answers a general question about how this project builds gates.**

The gate reads solution source and asks whether source is self-consistent. Source *was* self-consistent: all five lookup columns declare `IsSecured=1` in their own `Entity.xml`, the parser reads that flag, and the field security profile names them. The defect was one missing line in the function that builds the live API call — a **source-versus-creation-path** gap, which a source-versus-source gate cannot see however strict it is made. That is [IMP-0258](../../logs/improvement-log.jsonl#L255)'s corollary, and I verified it is not a one-off.

**I measured the residual and it is still open.** [The parser](../../provisioning/dataverse/ensure-schema-helpers.psm1#L232) produces 19 properties per attribute. [The standalone-attribute builder](../../provisioning/dataverse/ensure-schema-helpers.psm1#L309) emits `IsSecured` *and* `IsAuditEnabled`. [The lookup builder](../../provisioning/dataverse/ensure-schema-helpers.psm1#L731) now emits `IsSecured` — and still never emits `IsAuditEnabled`. No lookup in the solution currently declares `IsAuditEnabled=0`, so the gap is **latent by luck, not closed**: the first lookup that wants auditing off will be created with it on, silently, exactly as `IsSecured` was.

---

## 2. Clusters and promotion decisions

```
CLUSTER A: platform-contract-guessed-not-groundtruthed  (x2: IMP-0254, IMP-0255)
Altitude:  CLASS — instances 31 and 32 of a class at x32. Both instance fixes already
           shipped in source, so an instance patch is not even available here.
Ladder row: "a tool could catch it mechanically" + "second instance -> generalise"
Becomes:   1 new constraint + scripts/verify-declared-property-reaches-creation-path.py —
           diffs the property set ConvertFrom-RevEntityXml parses against the set each
           ConvertTo-Rev*Body emits, per attribute shape, with a declared
           not-applicable map carrying a reason per exclusion.
Retires:   the IsSecured-specific check inside verify-field-security-coverage.py
           (relationship_path_secures_lookups). Its THREE lookup fixtures move to the
           new gate and must still fail there — that is the coverage proof.
Cites:     IMP-0254, IMP-0255, IMP-0258
Residual:  The gate compares a parser's output to a builder's output textually. It cannot
           know whether a property is semantically inapplicable to a shape, so it needs a
           declared not-applicable map — and a wrong entry in that map is a silent pass.
           It also cannot see a property the parser itself never reads.
```

```
CLUSTER B: platform-fact-groundtruthed  (x3: IMP-0256, IMP-0257, IMP-0261)
Altitude:  KNOWLEDGE — three live reads closing open questions. Mechanical enforcement for
           the privilege half already shipped as verify-role-privilege-ownership.py.
Ladder row: "one instance, but the cause is general and a human needs to know it"
Becomes:   knowledge edits + one amendment to C-TECH-070.
           IMP-0257's proposed target is CORRECTED: it asked for security-model.md, but its
           sibling fact (a Money column's un-securable _base twin) already lives at
           knowledge/technology/dataverse.md#L158. A fact belongs beside its sibling.
Cites:     IMP-0256, IMP-0257, IMP-0261, IMP-0047
Residual:  rev_provideridname leaks a real organisation name to anyone with table Read.
           NOT resolved here — it is a confidentiality-scope decision. See section 5.
```

```
CLUSTER C: finding-diagnosis-unverified  (x1: IMP-0258)
Altitude:  SKILL — one member in its own class, but the MECHANISM is the second instance of
           the rule established from IMP-0217, which today binds only improvement-agent via
           how-to-promote-a-finding.md#L120. The gap is audience, not absence.
Ladder row: "an agent had the information and still did the wrong thing"
Becomes:   an edit to skills/how-to-log-an-improvement.md.
Cites:     IMP-0258, IMP-0217
Residual:  DELIBERATELY DEFERRED — IMP-0258 also proposes a root_cause_verified schema
           field plus a gate. Per how-to-promote-a-finding.md §4 a one-member class waits
           for its second instance. I am not building the field. Named here so the deferral
           is not silent.
```

```
CLUSTER D: two-invocation-paths-disagree  (x1 in this batch: IMP-0259, BLOCKER)
Altitude:  CLASS — instance 10 of a class at x10. The instance patch (step 3b) already
           shipped, so per the altitude rule this may not get another one.
Ladder row: "second instance -> generalise" + "a tool could catch it mechanically"
Becomes:   amend C-TECH-042 + a gate that classifies each provisioning step as create-only
           or reconciling and requires a header declaration from the create-only ones.
Cites:     IMP-0259
Residual:  The step markers this gate keys on (# -- N. ...) exist in only 9 of 23
           provisioning scripts. The gate covers the scripts that carry them and must
           report the ones it cannot classify rather than passing over them silently.
```

```
CLUSTER E: hand-maintained-count-drifts-from-source  (x2: IMP-0260, IMP-0263)
Altitude:  CLASS — now x8, and the third consecutive review to touch it. IMP-0262 was
           patched at instance level minutes before this review began; IMP-0263 is the
           class recurring in the same hour.
Ladder row: "the system's own memory failed" + "a tool could catch it mechanically"
Becomes:   a fourth rung in verify-constraint-verifiers.py + a selftest-footer convention.
Cites:     IMP-0260, IMP-0263, IMP-0262
Residual:  Two of the four gates I sampled do not report a fixture total in any parseable
           form. Until every selftest prints one, the new rung can only check the rows
           whose scripts do — and it must say which rows it could not check.
```

**My own measurement widened cluster E beyond what the findings recorded.** [IMP-0260](../../logs/improvement-log.jsonl#L257) found one stale fixture count. I checked all three constraint rows that state one:

| Row | Claims | Actual | State |
|---|---|---|---|
| [C-TECH-067](../../constraints/technology/technology-constraints.md#L137) | 9 selftest fixtures | 11 | **stale, previously unrecorded** |
| [C-TECH-069](../../constraints/technology/technology-constraints.md#L140) | 13 selftest fixtures | 13 | correct |
| [C-TECH-070](../../constraints/technology/technology-constraints.md#L141) | 3 fixtures | 7 | **stale** |

Two of three wrong is why this is a gate and not a two-number edit.

---

## 3. Proposed changes

| # | Type | Target | What it does | Can it fail? |
|---|---|---|---|---|
| 1 | **script** | `scripts/verify-declared-property-reaches-creation-path.py` (new) | For every property [the parser](../../provisioning/dataverse/ensure-schema-helpers.psm1#L232) reads off an attribute, assert every builder that can create that attribute shape emits it — or that a declared not-applicable map excludes it *with a reason*. Catches the `IsSecured` defect before a live run, and catches the `IsAuditEnabled` gap that is open today | YES — the two retired lookup fixtures must fail here, plus a fixture for the live `IsAuditEnabled` gap and one for a not-applicable entry with no reason |
| 2 | **constraint** | `C-TECH-071` (HARD), new | **A property the solution source declares is only delivered if the code that builds the create call emits it.** A source-vs-source check can never establish this. `Verify By` is change 1 | Change 1 is its `Verify By` |
| 3 | **constraint amendment** | [C-TECH-042](../../constraints/technology/technology-constraints.md#L84) | Adds the create-only/reconciling distinction: a step that creates a component carrying properties readable from source must either reconcile them on a later run, or declare in its header which it cannot converge and name the step that does. **Also replaces a `Verify By` that is not mechanically executable** — it currently reads "Script review at code-review gate", which [anti-bloat limit 4](../../skills/how-to-promote-a-finding.md#L38) calls a comment rather than a constraint | YES — change 4 |
| 4 | **script** | `scripts/verify-provisioning-step-convergence.py` (new) | Classifies each `# ── N.` step in a provisioning script as create-only or reconciling by whether it issues `PATCH` as well as `POST`, and fails a create-only step that carries no convergence declaration. Reports, rather than skips, the scripts whose steps it cannot classify | YES — selftest fixtures both ways, plus an unclassifiable script |
| 5 | **constraint amendment** | [C-TECH-070](../../constraints/technology/technology-constraints.md#L141) | Three corrections. (a) Fixture count 3 → cite the selftest's own reported total, so extending the gate cannot falsify the row again. (b) The general property its two shapes are instances of: **column security protects a stored value, never a platform projection of that value** — a Money `_base` twin and a `<lookup>name` companion are the two known projections. (c) Stops the lookup case being absorbed as a platform limit: a lookup **is** fully securable, and that failure was a delivery gap | Change 6 for (a); changes 1–2 for (c) |
| 6 | **script** | [verify-constraint-verifiers.py](../../scripts/verify-constraint-verifiers.py#L25) | A fourth rung, beside the three its own docstring already names: where a `Verify By` states a fixture count, run that script's `--selftest` and compare. Plus a convention — every gate's selftest prints `SELFTEST OK — N fixtures` — since two of the four I sampled print no total at all | YES — C-TECH-067 and C-TECH-070 are both live fixtures today |
| 7 | **skill** | [skills/how-to-log-an-improvement.md](../../skills/how-to-log-an-improvement.md#L51) | States that `root_cause` and `proposed_change` are a hypothesis, and that the agent **acting** on a finding re-verifies both against source before building either. Two named checks: grep the "source never declares X" claim, and grep `scripts/` for a proposed gate before authoring it. Extends [an existing rule](../../skills/how-to-promote-a-finding.md#L120) that today binds only improvement-agent | Partly — the checks are mechanical, the remembering is prose |
| 8 | **knowledge** | [security-model.md](../../knowledge/technology/security-model.md#L82) | An `OrganizationOwned` table exposes exactly six privileges; `Assign` and `Share` never exist for it. `Delete` **does** — conflating the two is what made this easy to get wrong. Both live read queries recorded | The gate is [verify-role-privilege-ownership.py](../../scripts/verify-role-privilege-ownership.py), already wired at [build.yml L456](../../config/revitalise-grant-automation-build.yml#L456) |
| 9 | **knowledge** | [dataverse.md L158](../../knowledge/technology/dataverse.md#L158) and a new metadata-reading section | The lookup-companion fact beside its Money sibling, under the shared projection rule; plus the four confirmed metadata-query facts and the rule of thumb that a 400 on a metadata GET means an illegal projection, not absence | Facts are live-verified; the remembering is prose |
| 10 | **source comment** | [ensure-schema.ps1 L154](../../provisioning/dataverse/ensure-schema.ps1#L150) | Drops the "If wrong, the…" caveat on `RelationshipDefinitions(SchemaName='x')` addressing — confirmed working live, so the doubt is closed | n/a |

**One new constraint against a cap of three.** Changes 3 and 5 are amendments to existing rows, not new ones. Clusters B, C and E needed no new constraint: B is knowledge behind a gate that already ships, C is an audience fix to an existing rule, E is enforcement of claims already written.

**Change 6's ordering matters.** The convention half must land before the rung half, or the new check fails on rows whose scripts cannot yet report a total.

---

## 4. Retirements

**One instance gate retires into a general one.** [`relationship_path_secures_lookups`](../../scripts/verify-field-security-coverage.py#L79) asks whether one function sets one property. Change 1 asks the general question of every property and every builder. Per [the retirement rule](../../skills/how-to-promote-a-finding.md#L80) the instance gate's own known-bad fixtures — `secured-lookup-with-dropping-path-must-fail` and `secured-lookup-with-no-helpers-must-fail` — move to the new gate and **must still fail there**. I will report that assertion as executed, or the retirement does not happen.

**No constraint row is superseded, and I checked rather than assuming.** The nearest candidate was C-TECH-042, and the honest reading is that its *rule* is right and its *verification* was never executable — so it is amended, not retired. Change 3 says so explicitly rather than quietly rewriting the column.

**Derived, not typed:** 10 retired rows and 77 live ones (51 technology, 16 domain, 10 commercial) as of today, via `grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l`. Every retired row is in the technology file; the domain and commercial files have never retired one.

---

## 5. What you need to decide

**A provider's real organisation name is readable by anyone who can read the table. Accept it, or change the design?**

Securing a lookup column hides the GUID it stores. Dataverse also maintains a companion column beside every lookup holding the *related row's* primary name, and that companion cannot be secured — the same platform behaviour as a Money column's un-securable twin, which you accepted on 2026-08-19 for the same reason.

For most of these lookups it does not matter: the applicant, grant and bank-account tables all have autonumber or masked primary names, so their companions leak only a pseudonymous reference. **`rev_provideridname` is the exception** — it carries the provider's real organisation name, and the only control on it is the table privilege.

Two options, and I am not picking a default because the trade-off is yours: **accept it**, on the same basis as the Money twin, and record that the table privilege is the control (nothing to build; the warning already ships in the coverage gate); or **change the design** so the confidentiality claim holds at column level, which is TAD-level work against NFR-002 and therefore a change-order conversation with `commercial-agent`, not something to fold into this review.

I recommend recording the acceptance if the Finance-only table privilege is genuinely the intended boundary — but only you can say whether it is.

---

## 6. Findings left unprocessed

**States excluded, stated so the cap is not silent:** 1 `awaiting-approval`, 13 `reviewer-deferred`, and every `APPLIED`/`REJECTED` entry. Nine `unread` entries were read in full and all nine are dispositioned above.

**One blocker is parked at another review's gate and I did not re-derive it.** It has been waiting since 2026-08-24 for a keyword sent against [Review 21](./2026-08-24-improvement-review.md), not for a new session. The log gate will keep reporting `FAILED` until that keyword arrives; this review cannot clear it and does not try.

**One finding arrived after my dispatch and I included it rather than deferring it.** [IMP-0263](../../logs/improvement-log.jsonl#L260) was appended by a concurrent session mid-derivation and shares a class with [IMP-0260](../../logs/improvement-log.jsonl#L257). Splitting one class across two reviews is precisely what the clustering step exists to prevent, so it is in cluster E.

**Part of IMP-0263 is not mine and I am not taking it.** Its stale counts sit in delivery source — a role file's header and a build handover — and the finding names the owner as whoever completes the finance-table field-security work. I propose the registry half; the source edits go to `development-agent` with the count already derived (67, confirmed three independent ways).

**A concurrent session was writing the log throughout this review.** It grew from 258 to 260 entries and one entry changed state. On approval I will re-read it immediately before appending, per [IMP-0080](../../logs/known-failure-modes.md).

---

## 7. Digest impact

**I am not predicting a number.** [Review 20's own lesson](./2026-08-23-improvement-review-8.md#L133) is that a predicted delta was wrong because the generator routes a lesson by two mechanisms and one silently wins. On approval I will regenerate and report the measured before-and-after.

What I can state without measuring: the digest is **current right now** (`--check` green at 260 entries), three of the nine findings carry `capability: true` and will render under Capabilities rather than where their class sits, and one class table row moves from x6 to x8.

---

## 8. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-24-improvement-review-3.md

Findings processed: 9 unread  →  5 clusters
Regression check:   6 prior changes audited, 2 classes recurred
Proposed:           1 constraint (cap 3), 3 gates/scripts, 3 skill/knowledge edits,
                    0 agent-file edits, 1 retirement
                    (+ 2 constraint amendments, + 1 source-comment correction)
Altitude calls:     3 generalised from instance to class, 1 left as a skill edit,
                    1 deliberately deferred to a second instance
Digest:             will regenerate and report measured — currently current at 260 entries

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

**Verification executed for this review:** 4 gate selftests run (`verify-role-privilege-ownership` 5 fixtures, `verify-field-security-coverage` 7, `verify-source-derived-test-counts` 11, `verify-source-reader-plurality` 13); 3 constraint fixture-count claims checked against their scripts (2 stale); `verify-derived-counts.py` run (4 drifted claims, SOFT); the property-transmission gap measured directly against the parser and both builders; every one of the 12 lookup columns in the solution read for `IsAuditEnabled`; digest currency confirmed.

**Not verified, and it is the honest limit of this review:** every proposed script in section 3 is **unwritten** — nothing in this document exists on disk, so no selftest has been run against any of it, and per [C-TECH-053](../../constraints/technology/technology-constraints.md#L108) the level reached is V0 for changes 1, 4 and 6. The live facts in changes 8 and 9 are `development-agent`'s live reads against DEV, which I read from the findings and did **not** re-execute — I have no live environment access in this session, and re-reading them needs a signed-in identity.

---

## 9. Applied — 2026-08-24

All ten changes are on disk. **Three things this review got wrong or missed were found by applying it**, and they are the most useful part of this section.

### The corrections, first

**1. The blocker's own premise was too narrow, and the new gate said so on its first run.** [IMP-0259](../../logs/improvement-log.jsonl#L256) stated that step 2's attribute loop "already reconcile[s]", and concluded lookups were the only columns set exclusively by a create-only step. [Step 2](../../provisioning/dataverse/ensure-schema.ps1#L384) is check-then-create with no `PATCH` anywhere in it, so **no property of any already-existing attribute converges** — lookup or not. Logged as a new finding, and it makes `finding-diagnosis-unverified` a two-member class, which retroactively justifies the schema field I refused it in section 2.

**2. A second gap in the same function nobody had recorded.** [The standalone-attribute builder](../../provisioning/dataverse/ensure-schema-helpers.psm1#L309) emits `IsAuditEnabled`; [the lookup builder](../../provisioning/dataverse/ensure-schema-helpers.psm1#L731) still does not. One line of the same shape as the `IsSecured` fix. Latent only because all 12 lookup columns declare the platform default — logged, gated, and warned on every build. It is delivery's line to add, not mine.

**3. My own fixture count was wrong.** Section 4 said "two lookup fixtures" move to the general gate. Three did.

### Elements added

| Element | Where | Proven by |
|---|---|---|
| `C-TECH-071` (HARD) — a declared property is only delivered if the creating code emits it | [technology-constraints.md](../../constraints/technology/technology-constraints.md#L142) | change 1 below |
| `verify-declared-property-reaches-creation-path.py` | [scripts/](../../scripts/verify-declared-property-reaches-creation-path.py) | 9 fixtures; build step [`declared-property-reaches-creation-path`](../../config/revitalise-grant-automation-build.yml#L484) |
| `verify-provisioning-step-convergence.py` | [scripts/](../../scripts/verify-provisioning-step-convergence.py) | 13 fixtures; build step [`provisioning-step-convergence`](../../config/revitalise-grant-automation-build.yml#L505) |
| Fourth rung: a `Verify By`'s fixture-count claim is run and compared | [verify-constraint-verifiers.py](../../scripts/verify-constraint-verifiers.py#L158) | 11 fixtures, up from 6 |
| `historical` exemption for dated records, requiring a date **and** a reason | [verify-derived-counts.py](../../scripts/verify-derived-counts.py#L237) | 9 fixtures, up from 7 |
| 9 `CONVERGENCE:` declarations across three provisioning scripts | [ensure-schema.ps1](../../provisioning/dataverse/ensure-schema.ps1#L341) and two others | the gate fails without them |

### Elements changed

| Element | Change |
|---|---|
| [C-TECH-042](../../constraints/technology/technology-constraints.md#L84) | Idempotency is not convergence. Its `Verify By` was "Script review at code-review gate" — not executable, which [anti-bloat limit 4](../../skills/how-to-promote-a-finding.md#L38) calls a comment. Now names a gate |
| [C-TECH-070](../../constraints/technology/technology-constraints.md#L141) | Gains the general rule (**column security protects a stored value, never a projection of it**), its third projection, and an explicit statement that a lookup **is** securable. Property transmission handed to `C-TECH-071` |
| [C-TECH-065](../../constraints/technology/technology-constraints.md#L135), [C-TECH-067](../../constraints/technology/technology-constraints.md#L137) | Reworded to cite each selftest's own reported total instead of a literal |
| [how-to-log-an-improvement.md](../../skills/how-to-log-an-improvement.md#L110) | `root_cause` and `proposed_change` are a hypothesis; the agent **acting** on a finding re-verifies both |
| [security-model.md](../../knowledge/technology/security-model.md#L34) | The `OwnershipType`→privilege table, and that `Delete` **does** exist on an organization-owned table |
| [dataverse.md](../../knowledge/technology/dataverse.md#L158) | The projection rule above its Money sibling; a new metadata-reading section with four confirmed limits |
| [ensure-schema.ps1 header](../../provisioning/dataverse/ensure-schema.ps1#L150) | The "If wrong" caveat is closed and replaced with the confirmation plus two sibling limits |
| 3 selftest footers | `verify-source-derived-test-counts`, `verify-source-reader-plurality`, `verify-derived-counts` now report a **derived** total. The last one had itself drifted by two |

### Retirement, and its coverage proof

`relationship_path_secures_lookups` is gone from [verify-field-security-coverage.py](../../scripts/verify-field-security-coverage.py#L79), which drops from 7 fixtures to 4. Its **three** property-transmission fixtures moved to the general gate and **still fail there** — that assertion is the coverage proof [the retirement rule](../../skills/how-to-promote-a-finding.md#L80) demands, and it is executed, not asserted. The name-companion warning stayed, because it is about confidentiality rather than transmission.

**Derived, not typed:** 78 live constraint rows (52 technology, 16 domain, 10 commercial) and 10 retired, every retirement in the technology file.

### Findings: what closed, and what I refused to close

**Five closed:** the three ground-truth reads and the two process findings, each with an `evidence_grep` needle and, for the V3 entries, a `reobserved` naming the live query that produced them.

**Four left open, deliberately, and this is the important half.** Their `observable_at` is V3 and the reproduction was a **live** `ensure-schema.ps1` run against DEV. Every artefact is on disk and green, but nothing has re-run it, and I have no live environment access. Closing them on a clean source tree is precisely the [IMP-0208](../../logs/known-failure-modes.md) defect — a needle matching a sentence the closing review just wrote, with the defect still live three days later. Each carries a `deferred_reason` and a `revisit_when` naming the exact command and who can run it. **The blocker among them stays open.**

The fourth is the count-drift finding, split by ownership: the registry half is applied, the remaining stale figure is in delivery source, and closing on the half I own is the subset-closure defect review 20's own gate was built to catch.

**Two appended:** the step-2 correction and the `IsAuditEnabled` gap, both deferred to their owners rather than fixed here.

### Digest impact — measured, not predicted

262 → **264** entries and 264 distinct lessons. Two sections each grew by one (`before-authoring` 28→29, `before-extending` 58→59). One class-table row moves 6→8, and `finding-diagnosis-unverified` appears as a recurring class at x2 for the first time. `--check` green.

### The queue, and the blocked build

**The log gate now passes** — `OK (schema + triggers)`, 264 entries, 1 unread. It was `FAILED` with three triggers when this review began. That clears the [C-TECH-061](../../constraints/technology/technology-constraints.md#L131) pre-build check that had blocked WBS 0.4, and it cleared **honestly**: by deferring four findings with real reasons and named revisit conditions, not by closing them. Two blockers that were parked at other reviews' gates were resolved by a concurrent session while this one ran.

The one remaining unread entry is the finding that recorded the blocked build itself, and a new blocker arrived after approval — see the closing note.

### Verification actually executed

7 selftests (9 + 13 + 4 + 11 + 9 + 11 + 13 = 70 fixtures, 0 failures); 6 live gate runs all exit 0, plus the SOFT count gate at exit 1 on its one delivery-owned drift; the build-config preflight green at 43 steps / 32 gates; `Invoke-Pester src/tests/provisioning/ScriptContract.Tests.ps1` 375/375; the three edited PowerShell files re-parsed clean; digest `--check` green.

**Not verified, and it is the same limit as before:** nothing in the four deferred findings has been re-observed live. Per `C-TECH-053` the new gates are at V1 — they run and their selftests pass; no live Dataverse call has been made by anything in this review.
