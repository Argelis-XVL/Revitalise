# Improvement Review — 2026-09-01 (9)

**Status:** APPLIED 2026-09-01 — `APPROVE IMPROVEMENTS` received. Previously recorded AWAITING; both changes are on disk and both findings are closed. See §8.
**Trigger:** unread `blocker` — [`IMP-0569`](../../logs/improvement-log.jsonl#L566), processed alone, not batched
**Findings processed:** 2 NEW (unread) → 1 cluster
**wbs:** 6.9 (the halted build), though the defect itself is system-level and belongs to no WBS task

---

## 0. Conclusion first

**Wire the gate; do not exempt it.** [`scripts/verify-models-yml-comments.py`](../../scripts/verify-models-yml-comments.py#L2) checks `config/models.yml`, which is a repository file present at build time and already an input to the wired [`subagents-current`](../../config/revitalise-grant-automation-build.yml#L91) step. Every entry in [`SUITE_GATE_EXEMPT`](../../scripts/verify-build-config.py#L691) is exempt because it runs at a *different* gate than the build, and that list's own header states the rule the other way round: *"Anything that checks a build input belongs in the config, not in this dict"* ([line 690](../../scripts/verify-build-config.py#L690)).

Two changes are proposed: the missing step, and the agent-file line whose absence produced it. No new constraints.

**One correction to the finding's own `proposed_change`, flagged now rather than at apply time.** Both [`IMP-0568`](../../logs/improvement-log.jsonl#L565) and [`IMP-0569`](../../logs/improvement-log.jsonl#L566) — and the dispatch brief — propose the step as `--warn-only`. The script has no such flag: its parser accepts `path` and `--selftest` only ([line 125](../../scripts/verify-models-yml-comments.py#L125)). `--warn-only` would exit 2 on an argparse error, and [`scripts/ci/run-config-steps.sh`](../../scripts/ci/run-config-steps.sh) halts on the first non-zero exit — so applying the finding's literal wording would replace one build-blocking defect with another. The script is already SOFT by construction: `main()` returns 0 on a finding, proven by its own selftest.

---

## 1. Verification executed, before anything was drafted

Per `agents/improvement-agent.md` step 8's behavioural-assertion clause — the findings assert *"this script is not a build step"* and *"the preflight fails"*, which are claims about behaviour, so they were **run**, not read.

| Command | Result |
|---|---|
| `python3 scripts/verify-build-config.py config/revitalise-grant-automation-build.yml` | **exit 1** — 1 violation, `suite-gate-is-not-a-step` on `verify-models-yml-comments.py`. Both findings reproduce exactly. |
| `python3 scripts/verify-models-yml-comments.py` | **exit 0**, 0 findings against the real `config/models.yml` |
| `python3 scripts/verify-models-yml-comments.py --selftest` | **exit 0**, 8 checks green, including `main() returns 0 on a finding (SOFT never blocks)` |
| `python3 scripts/verify-models-yml-comments.py --warn-only` | not run — the flag does not exist in the parser; see §0 |
| `python3 scripts/verify-improvement-log.py --check` | 10 `unread`, 0 `awaiting-approval`, 118 `reviewer-deferred`; `TRIGGER` names `IMP-0569` alone |
| `python3 scripts/verify-derived-counts.py` | 5 pre-existing drifts, **none** touching the build config or the verify-script count (`ls scripts/verify-*.py \| wc -l` = 55, matching [`agents/improvement-agent.md`](../../agents/improvement-agent.md#L371)) |

**Level reached: V1** — every assertion in this review was executed against the real tree.

---

## 2. The cluster

```
CLUSTER: gate-cannot-fail  (x2 this batch: IMP-0568, IMP-0569; x43 lifetime)
Altitude:  INSTANCE for the wiring, CLASS for the cause. The missing step is one config
           line. The reason it is missing is that agents/improvement-agent.md tells this
           agent where to PUT a gate it writes, how to selftest it, how to measure it
           against the corpus, and how to update its derived count — and never tells it to
           WIRE it. Review 7 followed that checklist completely and still shipped an
           unrunnable gate.
Ladder row: "a tool could catch it mechanically" (already true — verify-build-config.py DID
           catch it, at build time) + "an agent had the information and still did the wrong
           thing" → agent-file edit.
Becomes:   change 1 — one step in config/revitalise-grant-automation-build.yml
           change 2 — one paragraph + one command in agents/improvement-agent.md
Retires:   nothing. See §4.
Cites:     IMP-0568, IMP-0569
Residual:  The agent-file line is PROSE, and prose is what failed here. It is mitigated by
           naming an executable command rather than an obligation, but nothing forces an
           improvement-agent dispatch to run that command before parking at its gate. The
           mechanical backstop stays where it is — the build preflight — which means the
           cost of a future omission is again one halted build, not a silent hole. That is
           the honest bound on this fix and it is deliberately not escalated further: a
           gate over improvement-agent's own draft-time behaviour would be a gate reading a
           markdown document for semantics, the shape this project has measured at 48–100%
           false, five times.
```

---

## 3. Regression check

| Question | Answer |
|---|---|
| Has any finding in this class appeared since the previous review's changes? | **Yes** — and the recurrence is the subject of this review. [`2026-09-01-improvement-review-7.md`](2026-09-01-improvement-review-7.md#L41) change A1 created `verify-models-yml-comments.py`, ran its selftest (8 checks) and measured it against the real corpus (0 findings, correctly reported as a regression guard). It did not wire it. `IMP-0568` was logged ~4 hours later, `IMP-0569` 20 minutes after that. |
| Was the change prose or a mechanical gate? | Review 7's change was a **gate**. The *instruction* governing where that gate goes is prose, and it is the prose that is incomplete — hence change 2. |
| The gate that should have caught it — did it run? | **Yes, and it worked.** `verify-build-config.py`'s `suite-gate-is-not-a-step` check fired on the first build that reached it. This is not a `gate-cannot-fail` finding against the preflight; it is the preflight doing its job at the only moment it is invoked. The defect is that the moment is 4+ hours and one dispatch downstream of the change. |
| Did the closure evidence match the level the defect was visible at? | Both findings are `observable_at: V1`, and both are closable by running the preflight — which change 1 makes green. No V4 claim is involved. |
| Review 8's own changes | [`2026-09-01-improvement-review-8.md`](2026-09-01-improvement-review-8.md#L26) applied a WORKFLOW.md fixture, rejected `IMP-0561`, and fixed the appendix marker helper. No finding in any of those classes has appeared since. |

---

## 4. Retirement

**Checked; no candidate.** The obvious candidate would be `SUITE_GATE_EXEMPT` itself — an exemption list is a standing licence not to run a check — but all ten entries were re-read and each names a gate whose inputs genuinely do not exist at build time (a phase acceptance record, a handover pack, a provisioning report, the manifest that build-agent writes *after* the config's last step). Removing any of them would create the "gate that cannot run" the file exists to catch. Retired constraint rows stand at the figure registered as `improvement-agent-retired-constraint-count`; this review adds and retires none.

---

## 5. The two proposed changes

### Change 1 — [`config/revitalise-grant-automation-build.yml`](../../config/revitalise-grant-automation-build.yml#L121)

Add, immediately after the `document-status-consistency` step (line 121), at the end of the SOFT document-consistency group:

```yaml
  # SOFT. A comment above `tier:` / `escalate_to_strategic_when:` / `de_escalate_to_mechanical_when:`
  # in config/models.yml is discarded by the YAML loader generate-subagents.py uses, so a rule
  # written there never reaches the dispatched agent (IMP-0310).
  # NO `--warn-only` HERE, AND THAT IS NOT AN OMISSION: this script has no such flag and exits 0
  # on a finding by construction, proven by its own --selftest. Adding the flag would exit 2 on an
  # argparse error and halt the build.
  # UNLIKE THE FOUR GATES ABOVE, this one is green on the tree today — it is a regression guard for
  # a defect already repaired, not a report of a live one. Read its first finding as new, not as
  # the known condition (IMP-0568, IMP-0569).
  - name: models-yml-comments
    command: python3 scripts/verify-models-yml-comments.py
```

Why this position: the SOFT group is where a report-never-block gate belongs, and the script's only input is a tracked file, so no earlier step produces it and no ordering constraint applies. Placing it after `document-status-consistency` keeps the group contiguous. It carries no `# History:` pointer, matching the other members of this group, which hold their reasoning inline.

Verified against the preflight's own checks before proposing: the script exposes `--selftest` and passes, satisfying `check_negative_tests`'s second path; its docstring's opening clause ([line 2](../../scripts/verify-models-yml-comments.py#L2)) makes no wiring claim, so `check_wired_scripts_do_not_deny_wiring` is clear; and the comment above avoids every phrase in `ASSERTS_CURRENTLY_FAILS` ([line 882](../../scripts/verify-build-config.py#L882)).

### Change 2 — [`agents/improvement-agent.md`](../../agents/improvement-agent.md#L368)

In *"Where your executable output goes — and what you must run before closing"*, after the derived-count paragraph, add:

> **A gate you write is not finished until a build config invokes it.** `scripts/verify-build-config.py`'s `suite-gate-is-not-a-step` check treats any unwired `verify-*.py` in `scripts/` as a violation, and it is the *build* that discovers it — so the cost of forgetting is a halted delivery dispatch hours later, paid by another agent. Add the step in the same change, and prove it:
>
> ```bash
> python3 scripts/verify-build-config.py config/revitalise-grant-automation-build.yml
> ```
>
> Where the gate genuinely cannot run at build time — its input is a phase acceptance record, a handover pack, a post-deploy report — add it to `SUITE_GATE_EXEMPT` with a stated reason instead. That list's test is whether the input exists when a build runs, not whether wiring it feels useful. `IMP-0568` and `IMP-0569` are one gate that failed this in both directions: authored, selftested, corpus-measured, derived-count-updated, and unrunnable.

This sits in the checklist the drafting agent is already reading at close, beside the selftest and corpus-measurement commands it did run.

---

## 6. Queue scope — what this review did NOT process

This is a **blocker** dispatch, and `agents/improvement-agent.md`'s activation rule is that an unread blocker is processed on its own and does not pull a review of everything around it (`IMP-0183`). Eight further `unread` entries exist and are **out of scope**, none of them blockers:

| Entry | Severity | Class |
|---|---|---|
| `IMP-0549` | friction | `hand-maintained-count-drifts-from-source` |
| `IMP-0550`, `IMP-0551`, `IMP-0562` | friction | `finding-diagnosis-unverified` |
| `IMP-0552` | friction | `wrong-artefact-cited-as-evidence` |
| `IMP-0563` | friction | `no-assertion-on-shipped-content` — already cited by review 8 and carrying no `reviewed_in`; the gate reports this as a WARNING |
| `IMP-0566` | rework | `no-assertion-on-shipped-content` |
| `IMP-0567` | rework | `declared-policy-not-mechanically-enforced` |

None is stamped `reviewed_in` by this review. Each carries `excluded_by` naming this document instead, so that naming them here does not make eight findings read as processed (`IMP-0557`).

**One finding appended.** `IMP-0570` records the `--warn-only` defect described in §0 — a `proposed_change` naming a flag that does not exist on the script it names, written by analogy with the four neighbouring steps that all carry it. It is stamped `appended_by`, **not** `reviewed_in` (`IMP-0456`), and joins the unread queue as `friction`. No rule change is proposed for it; this review applies the corrected invocation and puts the pattern on the record for a second instance.

---

## 7. What you need to decide

Nothing is blocked on an open decision. The one judgement call worth your eye is §0's deviation from both findings' literal `proposed_change`: they say `--warn-only`, the script has no such flag, and this review proposes the bare invocation instead. If you would rather the flag existed, that is a change to the script and a different review.

---

## 8. Applied record — 2026-09-01

Both changes landed. Re-verification was executed before anything was written, per step 8's
behavioural-assertion clause, and every premise of the draft held.

| Re-verified at apply time | Result |
|---|---|
| `python3 scripts/verify-build-config.py config/revitalise-grant-automation-build.yml` (before) | exit 1, `suite-gate-is-not-a-step` — the draft's premise still true |
| `python3 scripts/verify-models-yml-comments.py --warn-only` | **exit 2**, `unrecognized arguments: --warn-only` — the flag still does not exist; §0's deviation is still compelled |
| `python3 scripts/verify-models-yml-comments.py` | exit 0, 0 findings |
| `python3 scripts/verify-models-yml-comments.py --selftest` | exit 0, 8 checks green |
| `python3 scripts/verify-build-config.py …` (after change 1) | **exit 0 — PASS, 71 steps, 56 gates** |
| `python3 scripts/verify-improvement-log.py --check` | **exit 0**; blocker trigger cleared, 0 `awaiting-approval` |

**Change 1** — `config/revitalise-grant-automation-build.yml`, `models-yml-comments` step added
after `document-status-consistency`, with the comment block as drafted.

**Change 2** — `agents/improvement-agent.md`, the *"A gate you write is not finished until a build
config invokes it"* paragraph added after the derived-count paragraph in *"Where your executable
output goes"*.

**NARROW-AND-REPORT, recorded in all three required places** (entry `applied_by`, here, and the
gate output): both findings' literal `proposed_change` said `--warn-only`; that flag measures as
non-existent and would exit 2 into a halt-on-first-failure runner. The narrowest form preserving
the intent — the bare invocation — was applied. The specific false outcome this removes is
nameable, which is what separates a narrowing from a substitution: applying the literal wording
replaces a build-blocking preflight failure with a build-blocking step failure.

**One correction to the draft.** §5 says the step *"carries no `# History:` pointer, matching the
other members of this group, which hold their reasoning inline."* That rationale is wrong — the
neighbouring SOFT steps **do** carry `# History:` pointers. The decision it justified is
nonetheless safe and was kept: the preflight's `history pointers resolve` check only validates
pointers that are present (55 across 76 steps), and requires none. No pointer was added because no
history section exists for this step.

**Both entries closed** `APPLIED` with `evidence_grep` and a `reobserved` object recording the
re-run preflight. Nothing was withheld.

**Two further findings appended at apply time**, both `friction`, both stamped `appended_by` and
**not** `reviewed_in` (`IMP-0456`), so neither reads as processed:

- `IMP-0571` — the false `# History:` rationale corrected above. Same class as `IMP-0570`
  (`finding-diagnosis-unverified`) from the adjacent direction. No rule change on two instances;
  a third would justify extending step 8's *"execute a behavioural assertion"* clause to
  *"grep an assertion about the current state of a tracked file"*.
- `IMP-0572` — `agents/improvement-agent.md` instructs the closing agent to record `reobserved`
  in prose that reads as free text, while `scripts/verify-improvement-log.py` requires a five-key
  object; `evidence_grep`'s object shape is not stated at all. Both were first written as strings
  and rejected by the gate. Enforcement is correct and precise; the gap is discoverability at
  write time.

The digest was regenerated last and once — 569 entries, `--check` green.
