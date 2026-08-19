# WBS state — derived from repository evidence

**GENERATED — do not hand-edit.** `python3 scripts/derive-wbs-state.py`

Baseline: `contract/wbs.json` v0.5 · 61 tasks

The WBS `Status` column is a **claim**. `derived` is what the repository actually contains. A disagreement is the finding — see `IMP-0030`.

## Derived counts

| Derived state | Tasks |
|---|---|
| `manual_only` | 20 |
| `complete` | 18 |
| `not_started` | 18 |
| `partial` | 3 |
| `complete_pending_manual` | 2 |

## Disagreements between the claim and the evidence

| Task | Phase | Claimed | Derived | Verdict | What is missing |
|---|---|---|---|---|---|
| `0.4` Dataverse solution & table schema buil | Phase 0 | Done | `partial` | **OVERCLAIM** | entity rev_review: ABSENT; entity rev_provider: ABSENT; entity rev_bankaccount: ABSENT; entity rev_payment: ABSENT; entity rev_anonymisedstatistic: AB |
| `1.2` Write form specification | Phase 1 | (blank) | `complete` | **UNDERCLAIM** | — |
| `1.6` Document save-and-continue workflow | Phase 1 | (blank) | `complete` | **UNDERCLAIM** | — |
| `2.8` Test with real data + sign-off | Phase 2 | (blank) | `complete` | **UNDERCLAIM** | — |
| `6.5` Share app to trustee role + access tes | Phase 3 | (blank) | `partial` | **UNDERCLAIM** | path src/solutions/RevitaliseGrantAutomation/AppModules/rev_trusteereview: ABSENT |
| `8.2` Build finance security role | Phase 4 | (blank) | `partial` | **UNDERCLAIM** | entity rev_bankaccount: ABSENT |
