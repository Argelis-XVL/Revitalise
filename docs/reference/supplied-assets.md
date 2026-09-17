# Supplied assets: every input surface names its owning agent

**Relocated from `CLAUDE.md` by the generalisation initiative, Phase 1, 2026-09-08.** `CLAUDE.md`
auto-loads on every turn and now carries a one-line pointer here. The rule below is unchanged;
only its location is.

**Established 2026-08-28 (`IMP-0028`, `IMP-0384` — second instance of
`input-type-with-no-owning-agent`, so this is a RULE for any supplied artefact, not a row for one
directory).**

---

## The rule

A brand, design or reference artefact supplied by the client **can arrive anywhere in the tree, not
only in `docs/Import/`**. When one does, four things are established **before** anything is designed
against it, and stated where the next agent will look:

1. Is it **tracked**?
2. Does it **ship**?
3. Is it **read by any build step**?
4. **Which agent owns intake?**

**A supplied artefact's status is a measurement with a date on it.** Where the answer is a number,
register it in `scripts/derived-counts-registry.json` so a gate reports the drift; where it is a
yes/no, put the date in the column header and re-run the check rather than reading the row. Never
infer a status from the fact that the files are visible, and never inherit one from a table without
looking at when it was measured (`IMP-0549`).

---

## The measured answers for `Designsystem/`

| Question | For `Designsystem/`, re-measured 2026-09-04 |
|---|---|
| **Tracked?** | **Yes.** 131 tracked files (`git ls-files Designsystem/`), added in commit `45dee74`; the working tree is clean. Not gitignored. Previously recorded *"**No.** 0 tracked files"* as verified 2026-08-28 — true then, and it was committed without anyone revisiting this row (`IMP-0549`). The figure is registered in `scripts/derived-counts-registry.json` as `designsystem-tracked-file-count`, so it cannot drift silently again |
| **Does it ship?** | **No.** Nothing under it reaches a solution, an artifact or a bundle. Unchanged, and re-measured |
| **Read by any build step?** | **Yes.** The wired HARD step `design-source-coverage` runs `scripts/verify-design-source-coverage.py`, which reads this directory: any subdirectory whose name matches a deliverable under `src/code-apps/` must be cited by a document in `docs/architecture/`. Previously recorded *"**No.** No `config/*.yml` step, workflow or script references it"* |
| **Which agent owns intake?** | **`architect-agent`**, and its placement outside `src/` is `ADR-034` — an architecture decision, not an existing rule. Unchanged |

---

## Why this rule exists

**The failure mode it prevents is silence, not error.** `docs/Import/` accepts any document, but
`skills/how-to-intake-external-documents.md` carries exactly two checklists — SDD-shaped and
TAD-shaped — and is declared *"used by plan-agent and architect-agent"*. So a commercial or
operational source dropped there **maps to no checklist and is silently unread**: `IMP-0028` was the
WBS quoting workbook that a plan document cited as the basis of its own estimate. `IMP-0384` was the
same defect from the other direction — a design system arriving in a directory named nowhere at all,
so nothing said whether it was tracked, deployable, ignored, or read.

## The correction that went stale too — which is the real lesson

This section used to read: *"`IMP-0384` describes `Designsystem/` as 'a tracked repository
directory'. It is not tracked; that was checked when this rule was written, and the row above is the
measured answer."* That was accurate on 2026-08-28 and is now wrong in both halves: the directory
holds 131 tracked files, and `IMP-0384`'s description was simply early rather than mistaken.

So the rule this document exists to state is **not** *"measure it once and write the answer down"*.
It is that **two of the four rows above changed within seven days of being verified** (`IMP-0549`).

## Why no gate enumerates the repository layout

**No gate enumerates top-level directories against `CLAUDE.md`'s Repository Layout block, and that
is deliberate.** The corpus is 14 directories, and a gate reading a prose layout block would be
asserting against a markdown code fence. A third instance is what would justify building one.
