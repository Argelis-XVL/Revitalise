# WBS state — derived from repository evidence

**GENERATED — do not hand-edit.** `python3 scripts/derive-wbs-state.py`

Baseline: `contract/wbs.json` v0.5 · 61 tasks

The WBS `Status` column is a **claim**. `derived` is what the repository actually contains. A disagreement is the finding — see `IMP-0030`.

## Derived counts

| Derived state | Tasks |
|---|---|
| `complete` | 24 |
| `manual_only` | 20 |
| `not_started` | 12 |
| `complete_pending_manual` | 5 |

## Disagreements between the claim and the evidence

| Task | Phase | Claimed | Derived | Verdict | What is missing |
|---|---|---|---|---|---|
| `0.7` Data governance & compliance | Phase 0 | Partially done | `complete` | **UNDERCLAIM** | — |
| `0.10` Flow error-handling instrumentation | Phases 1–4 | Partially done | `complete` | **UNDERCLAIM** | — |
| `1.2` Write form specification | Phase 1 | (blank) | `complete` | **UNDERCLAIM** | — |
| `1.6` Document save-and-continue workflow | Phase 1 | (blank) | `complete` | **UNDERCLAIM** | — |
| `2.8` Test with real data + sign-off | Phase 2 | (blank) | `complete_pending_manual` | **UNDERCLAIM** | — |
| `6.1` Design the trustee Dataverse app + sec | Phase 3 | (blank) | `complete` | **UNDERCLAIM** | — |
| `6.2` Build applications list screen | Phase 3 | (blank) | `complete` | **UNDERCLAIM** | — |
| `6.3` Build application detail screen | Phase 3 | (blank) | `complete` | **UNDERCLAIM** | — |
| `6.4` Build decision capture | Phase 3 | (blank) | `complete` | **UNDERCLAIM** | — |
| `6.5` Share app to trustee role + access tes | Phase 3 | (blank) | `complete_pending_manual` | **UNDERCLAIM** | — |
| `8.1` Finalise finance tables | Phase 4 | (blank) | `complete` | **UNDERCLAIM** | — |
| `8.2` Build finance security role | Phase 4 | (blank) | `complete` | **UNDERCLAIM** | — |
| `8.4` Wire Payment to Grant + payee logic | Phase 4 | (blank) | `complete` | **UNDERCLAIM** | — |
