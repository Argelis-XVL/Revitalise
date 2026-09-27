# Improvement Review — 2026-09-26 (5): WS-W parts W4–W7 — intake, the work board, instance keys, tracker stub

**Agent:** improvement-agent (tier `strategic`)
**Mode:** capability mode. Authorising artefact: [capability design, WS-W parts W4–W7](docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L310). The reviewer settled S-1 to S-5 in that document's §6 (S-4: local ledger, the client neither views nor edits it; S-5: an engine standard reusable at other clients). This review does not reopen them.
**Trigger:** capability mode
**Findings processed:** 1 `NEW` (IMP-0908, logged by this dispatch) → 4 clusters (W4, W5, W6, W7)
**Scope:** W4–W7 only. W1 is applied ([review 2026-09-26](docs/improvements/2026-09-26-improvement-review.md#L313)); W2+W3 and Group 2 are being drafted in parallel; Group 1 (review -4) is being applied now, uncommitted.
**Commercial:** system work, non-billable, no WBS task ([C-COM-002](constraints/commercial/commercial-constraints.md#L35)).
**Git:** working tree only when applied. Reviewer, verbatim: *"Wait until group 1 has landed. And all items of the plan are processed. Then we do 1 big commit."*
**Gate:** `APPROVE IMPROVEMENTS` — **APPROVED 2026-09-26; APPLIED 2026-09-27 in the working tree (uncommitted, awaiting the reviewer's single commit), see §13.** Authorisation record: Xander Lykopoulos (the reviewer; git user Xander Lykopoulos), in his own conversation turn, relayed_by lead-agent to this dispatch and quoted verbatim: *"D5 agreed / D6 ok / D8 agreed / Approve improvements"*. This dispatch did not see the reviewer's turn itself; the quote is lead-agent's relay. Read as: D-5 = generated board kept out of git (a `.gitignore` containing `*` inside `docs/audit/`); D-6 = backfill in the two tiers of §8 (follow-on work R1–R3, not part of this apply); D-8 = only the reviewer's verdict makes an item verified or done, recorded by lead-agent from his words. The keyword covers this review only.

---

## Summary

This review specifies the last four parts of the work-item ledger: who fills it (pm-agent, before any development starts), how your verdicts get into it (lead-agent, quoting you), a local work board you open by double-clicking a file, the two new `instance.yaml` keys and their validation, and a deliberately empty tracker interface. It proposes 13 changes, no new constraint, and changes no rule another draft owns.

Three decisions wait on you: **D-5** (keep the generated board out of git — recommended), **D-6** (backfill the 2026-09-20/25 feedback sheet as the first real test — recommended, in two tiers, and here is what it costs), and **D-8** (only you mark an item verified — recommended; already how W1's code behaves).

---

## 0. Where this review departs from the design text, and why

I re-measured every premise of §W4–§W7 against the tree before writing this. Eight places differ. Each keeps the design's intent.

| # | Design says | This review specifies | Measured |
|---|---|---|---|
| 1 | The closing report uses `work-items.py export --table --scope …` ([design L318](docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L318)) | `work-items.py export --format table --scope …`, and the global options `--ledger`/`--instance` go **before** the subcommand | Run on a scratch ledger: `--ledger` after the subcommand exits 2 with *"unrecognized arguments"*. The flag is `--format`, per [`cmd_export`](.engine/scripts/work-items.py#L151) |
| 2 | lead-agent records a reviewer's "still open" as `reopen` and "done" as `transition verified` ([design L315](docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L315)) | Only where the state machine allows it: `reopen` needs the item at `built` or above; `verified:<env>` needs `deployed:<env>`. **Below `built` there is nothing to record** — the ledger already says "not done" — and a "done" verdict on an item with no deploy record is reported as a disagreement, never forced | Scratch ledger: `reopen` from `ready` → *"REFUSED [FOLD] cannot reopen from 'ready'"*; `ready → verified:dev` → *"illegal (legal from: ['deployed:dev'])"* |
| 3 | A static viewer *"loads the JSON bundle"* and opens from disk ([Phase 11 L711](docs/improvements/IMPLEMENTATION-PLAN.md#L711), [11b L732](docs/improvements/IMPLEMENTATION-PLAN.md#L732)) | The export **embeds the bundle inside the generated page** and also writes the JSON file for machines | Headless Microsoft Edge on this Mac, page opened as `file://`: `fetch('data.json')` → *"TypeError: Failed to fetch"*; the same data as a `<script src>` file → loaded; inline → loaded. Logged as IMP-0908 |
| 4 | Board highlights *"`deferred` without reason"* ([design L328](docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L328)) | **Dropped.** The board shows deferred items and their reasons; it has no "missing reason" highlight | The ledger refuses a `defer` with no reason (schema check in [`lib/work_items.py`](.engine/scripts/lib/work_items.py#L311)); scratch run confirmed. The highlight could never fire |
| 5 | *"Stuck: `packaged` with no `deployed:<env>` after the next pipeline run"* | Same rule, reading the last deploy from [`collect-project-status.py --json` → `latest_deploy`](.engine/scripts/collect-project-status.py#L217), an existing generator — the board never parses `logs/pipeline.log` itself | Phase 11's own rule ("never re-implement a number a generator already computes"). Today it returns `{"env": "DEV", "result": "SUCCESS", "date": "2026-09-25 20:06"}` in 0.25 s |
| 6 | `new-instance.py` *"prompts for `deploy_paths`"*; the engine ships an empty default ([design L342](docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L342)) | A `--deploy-paths` flag (and `deploy_paths` in an answers file). When it is not given, the key is **omitted** and a note is printed | `new-instance.py` has no interactive prompt anywhere — it takes flags or an answers file. And Group 1 changed the default: an absent or empty `deploy_paths` means every blocker halts a build (fail-safe), [review -4 L28](docs/improvements/2026-09-26-improvement-review-4.md#L28) |
| 7 | pm-agent ingests "any list of work … before development is dispatched" | Ingestion happens **after** the list has stable row ids (for review feedback: after plan-agent's triage plan is approved) and **before** the first development dispatch. `acceptance` is the client's ask, verbatim — never our proposed solution | The feedback sheet's own columns separate *"What Emily asked for"* from *"Proposed solution"*; the intake skill already requires that split ([L208](skills/how-to-intake-external-documents.md#L208)) |
| 8 | W5 implements Phase 11 steps 11a/11b | Minimal 11a/11b: **two** generators (`work-items.py export --format json`, `collect-project-status.py --json`), one view. The other generators, the shared log parser, 11c's build step and 11e's redaction list stay not-started | Phase 11 lists four generators and a log parser for views this review does not build ([L724](docs/improvements/IMPLEMENTATION-PLAN.md#L724)) |

---

## 1. Regression check — the prior changes W4–W7 inherit

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| W1: the ledger, write tool and verifier | 2026-09-26 | items have no state of their own | **Not exercised yet.** `verify-work-items.py --check` today: 0 events, 0 items — no ledger exists until intake | **Untested in use.** W4 is the first thing that writes to it; D-6 is its first real test |
| Review Feedback Intake Checklist ([skill L164](skills/how-to-intake-external-documents.md#L164)) | 2026-09-17 (IMP-0739) | `input-type-with-no-owning-agent` — a list of feedback with no owner and no deliverable shape | **Yes, one step later.** The checklist gave feedback an owner and a triage table; the items then fell out between agents anyway. The reviewer, 2026-09-25: *"Not one single item of the feedback from the 20th has been processed"* ([design L70](docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L70)); IMP-0879 | **Prose fix, class recurred → escalate to a mechanism.** That escalation is WS-W: the ledger (W1), the close-out gate (W2), items in every handoff (W3) and intake into the ledger (this review) |
| `verify-import-manifest-intake.py` (SOFT) | 2026-09-17 | a source in `docs/Import/` that no agent reads | **The gate fired and nobody acted.** It reports the feedback sheet this review backfills from as unregistered, among 8 files; SOFT by design at [build L351](config/revitalise-grant-automation-build.yml#L351) | **Working as designed**; the gap is that nobody reads a SOFT line. W4's intake step 1 registers the source, so the owning agent now acts on it |

**Changes whose class recurred after a *prose* fix:** the feedback checklist — escalated, as above.
**Changes whose class recurred after a *gate*:** none (the SOFT gate fired correctly).

---

## 2. Clusters

```
CLUSTER: work-item-intake-and-reporting  (capability — design WS-W §W4)
Altitude:   ENGINE — pm-agent, lead-agent and the intake skill are engine files; the text names no
            client literal (sheet names, item ids and people stay in this review and in the ledger)
Ladder row: "an agent must do this at a moment" — agent-file steps, backed by the W1 tool that
            refuses what the steps forbid (AUTHOR, FOLD, schema checks)
Becomes:    pm-agent ITEM INTAKE mode; lead-agent verdict + closing-report section; an ingestion
            checklist in the intake skill; a "short of verified" line computed by export_table()
Retires:    nothing
Cites:      design §W4, D-8
Residual:   intake completeness (every source row became an item) is a counted reconciliation in
            pm-agent's output, not a gate; a verdict below `built` has no place in the ledger and
            is quoted in the report instead; no check can spot applicant personal data in a clause
```

```
CLUSTER: work-board  (capability — design WS-W §W5; IMP-0908)
Altitude:   ENGINE — export script and template are generic; the only instance fact is the
            output path, derived from instance.yaml slug
Ladder row: "a tool could catch it mechanically" — a generated view over generator output
Becomes:    .engine/scripts/export-audit-data.py (board view only), .engine/templates/audit-viewer.html,
            scripts/export-audit-data.py wrapper, Phase 11 plan text corrected
Retires:    nothing
Cites:      design §W5, IMPLEMENTATION-PLAN Phase 11, IMP-0908
Residual:   the "stuck" rule knows only the latest deploy, not every deploy; the board is a
            snapshot until re-exported; redaction for an external auditor is not built
```

```
CLUSTER: instance-scaffolding  (capability — design WS-W §W6)
Altitude:   ENGINE mechanism (validate-instance.py, new-instance.py), INSTANCE data (instance.yaml)
Ladder row: "a tool could catch it mechanically" — the instance validator, already a HARD build step
Becomes:    work_items keys in instance.yaml; validate-instance checks 8 and 9; new-instance
            scaffolds the keys, an empty ledger, three wrappers and one SOFT build step
Retires:    nothing
Cites:      design §W6, IMPLEMENTATION-PLAN Phase 8
Residual:   deploy_paths is validated for shape only — whether the listed paths are the ones that
            really ship is the instance owner's judgement
```

```
CLUSTER: tracker-interface  (capability — design WS-W §W7)
Altitude:   ENGINE
Ladder row: "a tool could catch it mechanically" — a one-value vocabulary the validator enforces
Becomes:    TRACKERS = ("none",) in lib/work_items.py plus a written adapter contract; validate-instance
            rejects any other value
Retires:    nothing
Cites:      design §W7, S-4
Residual:   none worth naming — nothing syncs, by the reviewer's decision
```

---

## 3. Specification

### 3.1 W4 — pm-agent owns intake; lead-agent records verdicts and closes with the item table

**pm-agent gains a fourth mode, `ITEM INTAKE`.** No gate keyword: the list it ingests has already been approved (a triage plan behind `APPROVED`, a change order behind its own gate), and adding a keyword would add to the approval load the design exists to reduce.

| When | What pm-agent does |
|---|---|
| A list of work exists in a tracked file with stable row ids, and development has not started on it | Ingest it. For review feedback that means after plan-agent's triage plan is approved |
| Step 1 | Register the source in `docs/Import/MANIFEST.yml` if `verify-import-manifest-intake.py` names it as unregistered |
| Step 2 | One intake `epic` per source list, titled with the source and its date |
| Step 3 | One `pbi` per row (`bug` when the row reports delivered work misbehaving), per the field mapping in §3.2 |
| Step 4 | `ready` for every item carrying `acceptance` and `source_ref`. Rows the triage resolved as answer-only or external-dependency: `defer` with the resolution and where it was answered as the reason |
| Step 5 | Reconcile and print both numbers: source rows = items created + rows not ingested (each with its reason, e.g. a section header row). `verify-work-items.py --check` must exit 0 |
| Never | Move an item above `ready` at intake, or write `verified`/`done` (the AUTHOR check refuses pm-agent anyway) |

**Backfill** (items that predate the ledger) follows the same steps. States above `ready` need the evidence the chain requires, and tracing source lines is development-agent's close-out work (W2), not pm-agent's. So a backfilled item sits at `ready` until someone evidences it: **the ledger understates, never overstates.**

**lead-agent** gains one routing row and one section:

- **Routing:** a list of work with no ledger items → pm-agent (item intake), before any development dispatch. Development is then dispatched by item ids (W3's `items:` field — this clause is dropped if W3 is not approved).
- **Verdicts** — the reviewer's words, quoted, never paraphrased, never inferred from a pipeline success, a Dev Summary or silence ([C-COM-006](constraints/commercial/commercial-constraints.md#L44)'s rule applied to items):

  | Reviewer says | Item state | lead-agent does |
  |---|---|---|
  | done / works | `deployed:<env>` | `transition <id> verified:<env>` with a `reviewer-verdict` object: name, date, quote, env |
  | done / works | `verified:<env>` | `transition <id> done`, same evidence |
  | not done / partly | `built` or above, `done`, `deferred` | `reopen <id> --reason "<quote>"`, same evidence |
  | not done | below `built` | nothing to write — the ledger already says so. Quote it in the report |
  | done | below `deployed:<env>` | nothing to write. Report the disagreement: *"the reviewer says done; the ledger has no deploy record for it"* |

  The evidence object goes in a scratch file, passed with `--evidence`. The board never writes back.
- **Closing report:** every delivery run ends with `work-items.py export --format table --scope <the run's items>`, pasted as printed, then the board regenerated and its path given.

**One small code change carries the "anything short of verified is named" rule.** [`export_table()`](.engine/scripts/lib/work_items.py#L836) gains a closing line — `Short of verified: <k> of <n> — <ids>` (items not at `verified:<env>` or `done`, deferred items listed separately) — so lead-agent pastes a count computed in one place instead of counting by hand. `work-items.py --selftest` gains one assertion for it.

### 3.2 The ingestion checklist (new section in the intake skill)

| Item field | Taken from | Rule |
|---|---|---|
| `external_id` | the row's own id in the source | the id every later document cites |
| `source_ref` | the row itself — `path#L<n>`, `path!<Sheet>:R<n>` or `path#p<n>` | the source, never a plan's paraphrase of it |
| `acceptance` | the client's ask, verbatim | one clause per separately stated requirement. **Never** the proposed solution — that is our design |
| `type` | `pbi`; `bug` when the row reports delivered work misbehaving | — |
| `parent` | the intake epic for this source | one epic per source list |
| `wbs`, `change_order` | the triage plan's Resolution column | a change order only once its document exists |
| state at intake | `ready`, or `deferred` with a reason for answer-only and external-dependency rows | nothing above `ready` |

Two rules beside the table:

1. **No personal data of the people the service is for.** If an ask quotes a person's name, contact details or health or disability detail, write that clause as `see source_ref — contains personal data`, and the source row stays the only copy. Measured on the backfill source: 0 of 50 asks contain an email address, a phone number or a person's name other than the client's own staff member who made the request.
2. **Reconcile the counts** (step 5 above). An item that never entered the ledger is exactly the failure this design exists to remove, and nothing downstream can see a row that was never ingested.

The `requirements` row of the skill's machine-read mapping table ([L229](skills/how-to-intake-external-documents.md#L229)) gains this checklist, so `verify-import-manifest-intake.py` checks the heading exists. The Review Feedback checklist gains one line: after the triage plan is approved, pm-agent ingests its rows.

### 3.3 W5 — the work board

**Command:** `python3 scripts/export-audit-data.py [--view board] [--out-dir docs/audit] [--selftest]`. It writes two files:

- `docs/audit/<slug>-audit.html` — the engine template with the bundle **inside** it, in a `<script type="application/json">` block. Opens by double-click.
- `docs/audit/<slug>-audit-data.json` — the same bundle, for machines (Phase 11's path).

**The bundle** carries `schema_version`, `generated_at`, `instance`, `views: ["board"]`, `source_hashes` (sha256 of the ledger, `instance.yaml`, `logs/pipeline.log` and `contract/wbs.json`, so staleness can be checked instead of assumed), and `board`:

| Key | Comes from | Never |
|---|---|---|
| `items` | `work-items.py export --format json`, unchanged | re-folded or re-counted |
| `latest_deploy` | `collect-project-status.py --json` → `latest_deploy` only | any other field of that output — it carries hours, which the board must not |
| `stuck` | derived here, per item, with the reason in words | — |
| `root_href` | the relative path from the output directory to the repository root | — |

**Stuck rules** (a board-only view, both in the export script's docstring):

1. `packaged` whose last `packaged` transition is older than `latest_deploy`, when that deploy succeeded (SUCCESS or PARTIAL) to the chain's first environment. Env names are compared lower-cased with `/` turned into `_`. If the status generator fails, `latest_deploy` is `null`, rule 1 is off, the board says so, and the export still exits 0.
2. Reopened two or more times — the same threshold W2 uses for escalation.

**The viewer** (`.engine/templates/audit-viewer.html`), one view:

- Tree: contract phase → WBS task (or change order) → items, or intake epic → items where there is no contract parent; tasks nested under their item.
- Each item: id, external id, title, state, the chain stages (Built, Packaged, Deployed to *env*, Verified in *env*) as reached/not reached, reopen count, stuck reasons. Expanding it shows the history and every evidence link, pointing at the file relative to `root_href`.
- Filters: state, feature (contract task, change order or epic), external id text, reopened only, stuck only.
- Empty ledger: a plain message saying so and naming the intake command.
- **Safety, all mechanically checkable in the template itself:** no `fetch`, no `XMLHttpRequest`, no `http://` or `https://` anywhere, and no `innerHTML` — all item text is inserted as text, never as HTML, so a title containing markup or a URL stays inert; no form, no write-back. **A Content-Security-Policy tag is deliberately not specified:** in headless Edge runs from `file://`, a page carrying `default-src 'none'; script-src 'unsafe-inline'` never ran its inline script, but the matching control page without the tag also returned unrendered in that batch (after the hung processes were killed), so the measurement is inconclusive either way. The tag is unproven. Adding one is an apply-time option only if a headless render with it shows the rows.

**Generated-output handling (D-5).** If you approve "gitignored", the export writes `docs/audit/.gitignore` containing `*` when that file is absent. The folder then ignores itself: the root `.gitignore` is untouched and its *"docs/ intentionally NOT ignored"* note ([L43](.gitignore#L43)) stays true everywhere else, and every other instance gets the same behaviour with no `.gitignore` edit.

**Not wired into the build.** Phase 11c's SOFT freshness step reports whether a *committed* viewer is current; with a gitignored output there is nothing committed to be stale. lead-agent regenerates the board at the end of each delivery run instead. The export has no `verify-` prefix and no check mode, so the suite-gate rule does not apply to it.

**Self-test** (a fixture repo from the existing `build_fixture_repo()`, with `latest_deploy` injected):

1. The HTML and JSON are written, and the embedded bundle's items equal `work-items.py export --format json` item for item (ids, states, reopen counts).
2. A title containing `</script><script>` cannot close the data block (the export writes `<` as `<`).
3. The template contains no `fetch`, `XMLHttpRequest`, `http://`, `https://` or `innerHTML`.
4. No key named `hours`, `rate` or `amount` anywhere in the bundle.
5. Stuck rule 1 flags an item packaged before the deploy and not one packaged after it; rule 2 flags two reopens and not one.
6. `latest_deploy` unavailable → `null`, a note in the bundle, exit 0.
7. Nothing is written outside `--out-dir` (tree listing before and after).

### 3.4 W6 — instance keys, validation, scaffolding

**`instance.yaml`** gains, directly after Group 1's `improvement:` block ([L63-L69](instance.yaml#L63)) and before the `# Phase 3f instance configs` comment ([L71](instance.yaml#L71)):

```yaml
# Work-item ledger (improvement review 2026-09-26-5, capability design 2026-09-26 WS-W §W6).
# The ledger is logs/work-items.jsonl, written only through scripts/work-items.py; ids are
# <id_prefix>-nnnn. `tracker: none` is the only accepted value until a tracker adapter exists
# (W7; reviewer decision S-4: the ledger stays local, the client neither views nor edits it).
work_items:
  id_prefix: WI
  tracker: none
```

**`validate-instance.py`** gains two checks, both skipped when their key is absent (an older instance must not suddenly fail):

| Check | Fails when |
|---|---|
| 8. WORK ITEMS | `work_items` is not a mapping; a key other than `id_prefix` or `tracker` is present (closed — a later key is added in the same change that introduces it); `id_prefix` does not match the ledger's own [`PREFIX_RE`](.engine/scripts/lib/work_items.py#L102); `tracker` is not in `TRACKERS` |
| 9. IMPROVEMENT LANES | `improvement.deploy_paths` is present and is not a list of non-empty, unique, relative strings (no leading `/`, no `..`). Shape only; the rest of the `improvement` block is left open for the siblings |

Both vocabularies are imported from `lib/work_items.py`, so the validator and the ledger cannot disagree about a valid prefix — today the ledger silently falls back to `WI` on a bad prefix ([L168](.engine/scripts/lib/work_items.py#L168)), and check 8 turns that into a loud failure at the HARD [`validate-instance` build step](config/revitalise-grant-automation-build.yml#L50). Self-test: +6 cases (valid keys; lowercase prefix; `tracker: jira`; an unknown `work_items` key; `deploy_paths` not a list; an absolute path).

**`new-instance.py`** ([template L86](.engine/scripts/new-instance.py#L86), [wrappers L337](.engine/scripts/new-instance.py#L337)):

- The template writes `work_items: {id_prefix, tracker: none}`. `--work-item-prefix` (default `WI`) sets the prefix.
- `--deploy-paths a/,b/` writes `improvement.deploy_paths`; without it, a comment explains that the key is absent on purpose and every blocker halts a build until it is set. The same names work in an `--answers` file.
- An empty `logs/work-items.jsonl` is scaffolded.
- Three more generated wrappers: `work-items.py` (its usage text must not contain the characters `--check`, the W1 trap), `verify-work-items.py`, `export-audit-data.py`.
- The placeholder build config ([L326](.engine/scripts/new-instance.py#L326)) gets one SOFT step, `work-items`, instead of `steps: []`, so a fresh instance's own verifier is wired from the start.
- Self-test: the scaffold carries both keys and no `improvement` key by default, the empty ledger, the three wrappers, a `work-items.py` wrapper without `--check` text, and `verify-work-items.py --check` exits 0 inside the scaffold; a second scaffold with `--deploy-paths src/,build/ --work-item-prefix ACME` validates.

### 3.5 W7 — tracker interface only

`lib/work_items.py` gains `TRACKERS = ("none",)` beside [`VERDICT_AUTHORS`](.engine/scripts/lib/work_items.py#L72), and a *TRACKER ADAPTER CONTRACT* section in its module docstring:

- The ledger is canonical. An adapter pushes one way, from `export`.
- The only thing ever read back is a reviewer verdict, written **through** `work-items.py` as `reviewer-verdict` evidence under the D-8 authorship rule — never a direct ledger write.
- No gate reads the tracker.
- Adding a value to `TRACKERS` is the change that introduces an adapter, and it gets its own review.
- Until then, `export --format csv` (W1, Azure Boards import shape) is the manual bridge.

Nothing reads `tracker` at run time, so no `Context` field is added — the validator is the only consumer.

---

## 4. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | agent | `agents/pm-agent.md` (engine) | Role names the ledger; `ITEM INTAKE` row in Modes; new `### ITEM INTAKE` subsection (§3.1); an `ITEM INTAKE` gate-output block; `ITEMS` in the Logging mode list | design §W4 | Partly — the tool refuses pm-agent a verdict (AUTHOR) and any illegal transition (FOLD); intake completeness is a printed reconciliation | N/A |
| 2 | agent | `agents/lead-agent.md` (engine) | One routing row; new section *Work items — intake, reviewer verdicts, closing report* (§3.1) | design §W4, D-8 | Partly — FOLD refuses a verdict the chain does not allow; the quote itself cannot be checked against chat | N/A |
| 3 | skill | `skills/how-to-intake-external-documents.md` (engine) | New `## Work-Item Ingestion Checklist (pm-agent)` (§3.2); one line in the Review Feedback checklist; the `requirements` mapping row gains the new checklist | design §W4 | YES — `python3 scripts/verify-import-manifest-intake.py` checks the mapped heading exists | N/A |
| 4 | script | `.engine/scripts/lib/work_items.py` + `.engine/scripts/work-items.py` | `export_table()` closing line `Short of verified: k of n — ids`; one `--selftest` assertion | design §W4 | YES — `python3 scripts/work-items.py --selftest` | N/A — library and write tool, no check mode |
| 5 | script | `.engine/scripts/export-audit-data.py` (new) | The board export (§3.3) | design §W5, IMP-0908 | YES — `python3 .engine/scripts/export-audit-data.py --selftest` (7 cases) | N/A — not a gate: no `verify-` prefix, no check mode; Phase 11c's SOFT step deliberately not wired (§3.3) |
| 6 | template | `.engine/templates/audit-viewer.html` (new) | The static board view (§3.3) | design §W5 | YES — self-test cases 2–3 of row 5, plus a headless-browser render at apply time | N/A |
| 7 | script | `scripts/export-audit-data.py` (instance) | Thin wrapper; no redaction list yet (auditor view not built) | design §W5 | YES — `verify-engine-instance-split.py` reports it `WRAPPER` | N/A — not a gate |
| 8 | other | `docs/improvements/IMPLEMENTATION-PLAN.md` | Phase 11: 11a/11b marked partial (board view), the file:// measurement added with the withdrawn "loads the JSON bundle" wording kept visible, Checkpoint 11 (1) answered, 11c/11e status; Phase 8: one "extended by W6" line | design §W5, §W6, IMP-0908 | YES — `grep -c "file:// page cannot fetch" docs/improvements/IMPLEMENTATION-PLAN.md` returns 1 | N/A |
| 9 | other | `instance.yaml` | `work_items:` block after Group 1's `improvement:` block (§3.4) | design §W6 | YES — `python3 scripts/validate-instance.py instance.yaml` | N/A |
| 10 | script | `.engine/scripts/validate-instance.py` | Checks 8 and 9, importing `PREFIX_RE` and `TRACKERS` from the lib; +6 self-test cases | design §W6, §W7 | YES — `python3 scripts/validate-instance.py --selftest` | already wired — HARD [`validate-instance`](config/revitalise-grant-automation-build.yml#L50) and CI |
| 11 | script | `.engine/scripts/new-instance.py` | Keys, `--work-item-prefix`, `--deploy-paths`, empty ledger, three wrappers, SOFT `work-items` step in the placeholder build config; self-test cases (§3.4) | design §W6 | YES — `python3 .engine/scripts/new-instance.py --selftest` | N/A — a scaffolder, not a gate |
| 12 | script | `.engine/scripts/lib/work_items.py` | `TRACKERS = ("none",)` and the adapter contract docstring (§3.5) | design §W7, S-4 | YES — exercised by row 10's `tracker: jira` case | N/A — library |
| 13 | other | the capability design, end of §W7 (before *Mechanical verification (WS-W as a whole)*) | One line: W4–W7 specified in this review, which corrects the `--table` flag, the file:// transport, the "deferred without reason" highlight and the `deploy_paths` prompt | — | N/A | N/A |

**Constraint budget:** 0 of 3 used. W4–W7 add no rule that a script does not already enforce or that the reviewer's decisions did not settle.

---

## 5. Shared files — exactly which sections this review edits

So the applies can be serialised against Group 1 (applying now), Group 2 and W2+W3 (drafting in parallel):

| File | This review edits | This review does **not** touch |
|---|---|---|
| `agents/pm-agent.md` | Role paragraph ([L10](agents/pm-agent.md#L10)); one row after `BASELINE INTAKE` in Modes ([L46](agents/pm-agent.md#L46)); new `### ITEM INTAKE` after the BASELINE INTAKE subsection, before its closing `---`; a second block in *Gate output*; the mode list in *Logging* | everything else. No sibling draft names this file |
| `agents/lead-agent.md` | One row after the baseline-intake row of the Routing table ([L33](agents/lead-agent.md#L33)); one new H2 section inserted immediately before `## Improvement Capture` ([L287](agents/lead-agent.md#L287)) | *Routing to improvement-agent* and its exit-code paragraphs (Group 1, applied in the working tree; Group 2); the "Carry the WBS task id(s)" sentence under *How Delegation Happens* and any `items:` dispatch rule (W3) |
| `instance.yaml` | New `work_items:` block after the `improvement:` block's last line (`    - build/`) | the `improvement:` block (Group 1) |
| `.engine/scripts/lib/work_items.py` | `export_table()` body; `TRACKERS` constant beside `VERDICT_AUTHORS`; one new docstring section | anything W2/W3 add (the scoped development-gate check, manifest `items[]`) |
| `skills/how-to-intake-external-documents.md` | New H2 before *Which checklist a source class maps to* ([L218](skills/how-to-intake-external-documents.md#L218)); one line in the Review Feedback checklist; the `requirements` mapping row | — |
| capability design | One line at the end of §W7 | W2/W3 and Group 2 pointer lines in their own sections |
| `docs/improvements/IMPLEMENTATION-PLAN.md` | Phase 11; one line in Phase 8 | all other phases |

**Order when applied.** After Group 1 has landed (it owns the `instance.yaml` anchor and has edited `lead-agent.md`). Rows 4 and 12 edit the same library as review -6 (W2+W3), whose findings show it changing the evidence resolvers there, so apply after -6 and re-read the file first; this review touches only `export_table()`, one constant and one docstring section. Row 2's `items:` clause waits for W3's approval, or is dropped. Engine files (rows 1–6, 10–12) go on the engine branch `deploy-first-learning-and-item-closure`, instance files on the instance branch, **uncommitted** until the reviewer's single commit.

---

## 6. Retirements

Nothing is retired.

> Retirement check performed: 86 live constraint rows reviewed by grep for intake, triage, verdict and closing-report terms. The only hits (C-TECH-055, C-TECH-061, C-TECH-065) govern build warnings, the improvement queue and credentials; none is superseded by W4–W7. The design's two retirement candidates belong to WS-U and WS-T.

---

## 7. Findings left unprocessed

**Deferred:** IMP-0862, IMP-0887, IMP-0891, IMP-0892, IMP-0893, IMP-0894, IMP-0895, IMP-0896, IMP-0897, IMP-0898, IMP-0899, IMP-0900, IMP-0901, IMP-0902

When this draft started, the queue gate reported 14 `unread`, 1 `awaiting-approval` (IMP-0855, parked on its own document) and 215 `reviewer-deferred`. Sibling drafts have appended more since; each is stamped by, or belongs to, the draft that logged it. None of the 14 concerns intake, the board, instance keys or trackers: they are gate-scope, TAD, requirements-wording, pipeline-hygiene and digest findings, for the post-deploy batch (WS-U) or the next defect review. IMP-0901's fix sits in `WORKFLOW.md`, Group 1's file. I did not stamp `excluded_by` on them: that means rewriting log lines while Group 1 and two sibling drafts append to the same file, and this line already declares their scope.

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| the 14 above | various | outside W4–W7 | the post-deploy batch or the next defect review |

**Processed here:** IMP-0908 (this dispatch's finding, `reviewed_in` stamped at draft). `observable_at: n/a` — the defect is in plan text and nothing was ever built on it — so at apply it closes on an `evidence_grep` for row 8's needle.

---

## 8. Routed work — for other agents, after this review is applied

Not changes this review makes. Each depends on a decision below.

| # | Agent | Work | Depends on |
|---|---|---|---|
| R1 | pm-agent | `ITEM INTAKE` of [the feedback sheet](docs/Import/FeedbackDeployment_20-09-2026.xlsx): register it in `docs/Import/MANIFEST.yml`; one epic; 50 items (EF-01 to EF-49 plus EF-28b; row 55 is a stray header row and is reported as not ingested); answer-only rows deferred with their reason | D-6 |
| R2 | development-agent | The first W2 close-out run, over the acceptance-test sample: EF-43 and the rows whose surface is the trustee portal — trace each clause to source lines, record the test run, the legacy manifest and the deploy records, as far as the evidence reaches | D-6, W2 applied, and review -6's deploy-record resolver fixes if you approve them (it measured the resolver missing two of the log's three success-line spellings, and not comparing a record's component with the line) |
| R3 | lead-agent | Record the sheet's 2026-09-25 verdicts on the R2 items, quoting the sheet, under the §3.1 table; then regenerate the board and check it against the sheet | D-6, D-8 |

---

## 9. What you need to decide

### The board

**D-5. Should the generated board stay out of git and be regenerated on demand?**

**Problem** — The board is regenerated after every change to the ledger, so a committed copy would change on every item transition and collide between concurrent sessions, and it duplicates what the ledger already records.
**Suggested fix** — Keep it out of git: the export writes a one-line `.gitignore` inside `docs/audit/`, and lead-agent regenerates the board at the end of each delivery run with one command. The engine template is committed either way.
**What happens if you don't** — A committed board goes stale the moment an item moves, which is the "second place a number goes stale" failure Phase 11 was written to avoid, and every concurrent session produces a merge conflict on it.
[design D-5](docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L493) · [Checkpoint 11](docs/improvements/IMPLEMENTATION-PLAN.md#L757)

---

### The first real test

**D-6. Should the 2026-09-20 and 2026-09-25 feedback sheet be backfilled as the first real corpus?**

**Problem** — The ledger is empty, so nothing yet proves the board tells the truth, and the sheet is the one source where your own verdicts sit next to each item.
**Suggested fix** — Yes, in two tiers. **Tier 1** (pm-agent, cheap and mechanical): all 50 rows become items at `ready` or `deferred`, so every row is visible and none shows as done. **Tier 2** (development-agent's first close-out run): full evidence only for EF-43 and the trustee-portal rows, the sample the design's acceptance test names, followed by your recorded verdicts.
**What happens if you don't** — The ledger stays empty, W2's gate has nothing to check, and the first real use happens during live delivery. With tier 1 only, the 19 rows your 2026-09-25 check calls "Done" show as `ready`: understated, never overstated, which the design accepts. A full-evidence trace of all 50 rows is roughly one development dispatch per surface and is not what I recommend.
[design D-6](docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L497) · [acceptance test](docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L356)

---

### Authority

**D-8. Should only you mark an item verified or done, recorded by lead-agent from your own words?**

**Problem** — A "verified" written by any agent would be a claim about your acceptance that you never made, which is how items were reported delivered twice while the live screen said otherwise.
**Suggested fix** — Yes. This is already how W1's code behaves: only `reviewer` or `lead-agent` may write `verified` or `done`, the verifier refuses anyone else, and the evidence must carry your name, a date and your quote. This review adds the lead-agent instructions that use it and nothing else.
**What happens if you don't** — Choosing "you only, typed by you" means you run the command yourself for every verdict. Widening it to other agents removes the one check that separates "tested" from "accepted".
[design D-8](docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L504) · [`VERDICT_AUTHORS`](.engine/scripts/lib/work_items.py#L72)

---

D-5 changes one behaviour of row 5. D-6 blocks only the routed work in §8. D-8 blocks nothing in the change table.

---

## 10. Verification

**Executed for this draft:**

- `verify-improvement-log.py --check`: exit 0 before and after appending IMP-0908 (904 entries).
- Headless Microsoft Edge 154, pages opened as `file://`: `fetch` of a sibling JSON file fails; `<script src>` loads; inline JSON loads. With a CSP meta tag the inline script did not run, but the no-tag control in the same batch also came back unrendered, so that batch is inconclusive and the CSP result is recorded as unproven, not as a platform fact. Headless Edge on this Mac is slow and sometimes hangs — budget for that at apply.
- Scratch ledger with two real sheet rows: `add` with no parent, `EF-28b` as an external id, `ready`, a reasoned `defer`, and three refusals (reopen from `ready`; `ready → verified:dev` by lead-agent; the same by pm-agent). `verify-work-items.py --check` over it: 4 events, 0 failures.
- The backfill source profiled: 51 rows carry an `EF-` id (50 items plus one stray header row); 0 email addresses and 0 phone numbers in the asks and verdict columns.
- `collect-project-status.py --json`: exit 0 in 0.25 s; `latest_deploy` present.

**To run at apply, before anything is wired or reported:** each new or edited script's `--selftest`; `export-audit-data.py` against this repo (0 items today — the empty-state page must render) and against a scratch ledger of three real sheet items, both opened in headless Edge with the rendered row count compared to the item count; `validate-instance.py instance.yaml`; `verify-import-manifest-intake.py`; `verify-engine-instance-split.py`; `verify-build-config.py` on the build config; `verify-derived-counts.py` (the `verify-*.py` count is unchanged at 67 — this review adds none); `verify-doc-line-links.py`; `verify-review-document.py`; an engine-literal sweep of every engine file this review writes.

**Not verified:** nothing has been applied; no board has been rendered from real ledger data; the CSV bridge is still document-verified only (W1). Level reached: V1 (design).

---

## 11. Digest impact

| | Before | After this draft |
|---|---|---|
| Log entries | 903 when this draft started | 904 after IMP-0908; 911 now, the other seven appended by sibling drafts |
| Entries closed by applying | — | 1 (IMP-0908) |

Regenerated with `python3 scripts/generate-known-failure-modes.py` after the validator passed.

---

## 12. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-26-improvement-review-5.md

Findings processed: 1 NEW  →  4 clusters
Regression check:   3 prior changes audited, 1 classes recurred
Proposed:           0 constraints (cap 3), 6 gates/scripts, 1 skill/knowledge edits,
                    2 agent-file edits, 0 retirements
Altitude calls:     4 generalised from instance to class, 0 left as notes
Digest:             will regenerate — 1 lesson added, closed on apply

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 13. Applied

Applied 2026-09-26 → 2026-09-27 in the working tree, **uncommitted** (reviewer: one commit at the end). The apply was cut off once by the account's session limit and resumed; the resumed pass re-read every target and found rows 4, 10, 12 and 9 and the new engine files for rows 5 and 6 already on disk, and redid nothing. Before editing I re-ran `verify-improvement-log.py --check`: nothing appended since the draft names or corrects IMP-0908 or anything in W4–W7. Review -6 (W2+W3) is approved in substance but not applied, so this apply went first; in `lib/work_items.py` it touched only `export_table()`, the `TRACKERS` constant and one docstring section (three diff hunks, all this review's).

| # | Change | Applied at | Entries moved to APPLIED |
|---|---|---|---|
| 1 | pm-agent: Role, Modes row, `### ITEM INTAKE`, gate block, `ITEMS` log mode | `agents/pm-agent.md` (engine) | — |
| 2 | lead-agent: routing row; *Work items — intake, reviewer verdicts, closing report* before *Improvement Capture* (the `items:` clause kept — W3 approved in substance) | `agents/lead-agent.md` (engine) | — |
| 3 | Work-Item Ingestion Checklist; Review Feedback line; `requirements` mapping row | `skills/how-to-intake-external-documents.md` (engine) | — |
| 4 | `export_table()` closing `Short of verified` / `Deferred` lines; one selftest assertion | `.engine/scripts/lib/work_items.py`, `.engine/scripts/work-items.py` | — |
| 5 | Board export | `.engine/scripts/export-audit-data.py` (new) | IMP-0908 (with row 8) |
| 6 | Viewer template | `.engine/templates/audit-viewer.html` (new) | — |
| 7 | Wrapper (no check-flag text, no redaction list) | `scripts/export-audit-data.py` (new, instance) | — |
| 8 | Phase 11 status, file:// measurement with withdrawn wording retained, 11a/11b/11c/11e, Checkpoint 11 (1) answered; Phase 8 "extended" line | `docs/improvements/IMPLEMENTATION-PLAN.md` | IMP-0908 |
| 9 | `work_items:` block after `improvement:` | `instance.yaml` | — |
| 10 | Checks 8 and 9, +6 self-test cases | `.engine/scripts/validate-instance.py` | — |
| 11 | Keys, `--work-item-prefix`, `--deploy-paths`, empty ledger, three wrappers, SOFT step, self-test | `.engine/scripts/new-instance.py` | — |
| 12 | `TRACKERS = ("none",)` + TRACKER ADAPTER CONTRACT | `.engine/scripts/lib/work_items.py` | — |
| 13 | APPLIED pointer at the end of §W7 | the capability design | — |

**IMP-0908** → `APPLIED`, `evidence_grep` = `docs/improvements/IMPLEMENTATION-PLAN.md` / `file:// page cannot fetch` (1 match). `observable_at: n/a`, so no `reobserved` is required.

**What was executed, and what it returned:**

- `work-items.py --selftest`: 30 of 30 OK, exit 0 (the new short-of-verified assertion included). `export --format table` on a three-item scratch ledger closes with `Short of verified: 2 of 3 — WI-0001, WI-0003` and `Deferred: 1 — WI-0002`.
- `verify-work-items.py --selftest`: exit 0; `--check` on this repo: 0 events, 0 items, exit 0 (no ledger yet — R1 creates it).
- `export-audit-data.py --selftest` (engine and wrapper): 22 of 22 OK, exit 0. **Can it fail:** two mutants, both killed — removing the `<` escape (the hostile title then closes the data block and the self-test fails), and dropping the date comparison from stuck rule 1 (fails *"packaged after the deploy is not"*).
- Template checks: no `fetch`, `XMLHttpRequest`, `http://`, `https://` or `innerHTML` (asserted by self-test case 3).
- **Rendered in headless Microsoft Edge 154 from `file://`:** the scratch board (three real sheet rows) shows 1 header + 3 item rows and *"3 of 3 shown"*, with its title and meta line written by the page's script — so the embedded data loaded and the script ran. This repo's real board (0 items) renders the empty-state message. That is a machine render, not a person using it.
- Real export on this repo: `docs/audit/revitalise-grant-automation-audit.html` and `-audit-data.json` written, plus `docs/audit/.gitignore` (`*`); `git status` shows nothing under `docs/audit/`, and `git check-ignore` confirms the page is ignored by that file (D-5).
- `validate-instance.py --selftest`: PASS, 19 cases (13 before + 6); `validate-instance.py instance.yaml`: PASS.
- `new-instance.py --selftest`: PASS, including both keys, no `improvement` key by default, the empty ledger, the three wrappers, a `work-items.py` wrapper without check-flag text, the wired SOFT step, `verify-work-items.py --check` exit 0 inside the scaffold, and a second scaffold with `--deploy-paths src/,build/ --work-item-prefix ACME` that validates.
- `verify-import-manifest-intake.py`: 0 unmapped or dangling classes (the new checklist heading resolves). It still exits 1 on the 8 unregistered `docs/Import/` files it reported before this review; SOFT at build time. R1 registers the feedback sheet.
- `verify-engine-instance-split.py`: exit 0 — 96 scripts, 27 split/wrapper (the new wrapper), 2 engine-only.
- `verify-build-config.py` on the build config: exit 0. `verify-system-consistency.py`: PASS. `verify-gate-input-tracking.py`: exit 0.
- `verify-improvement-log.py --check`: exit 0. Digest regenerated; `generate-known-failure-modes.py --check`: current. `verify-derived-counts.py`: 11 of 11 match (`verify-*.py` count unchanged at 67).
- Engine literal sweep of every engine file this review wrote: 0 hits in the template, the library, the new agent/skill text and the export script — after one fix: the export's self-test used this client's env key and item-id prefix as fixture values, now replaced by generic ones. `validate-instance.py` and `new-instance.py` carry 4 hits each, all pre-existing prose at HEAD. Positive control: 4 hits in `scripts/kb.py`.
- `verify-doc-line-links.py docs/improvements`: no dangling link in this review. One dangling link points into the capability design — the W1 review's `design §4` at `#L437` — and was already off before this apply (earlier sibling edits moved §4); the §W7 pointer line moves it one line further. Not fixed here: that link belongs to another review.

**Level reached (C-TECH-053):** V1 for the scripts and rules, plus a headless-browser render of the board (above). No person has opened the board, and no real ledger data exists yet. Nothing in any environment was touched.

**Not done here, by scope:** the D-6 backfill (§8 R1–R3), review -6, and any commit.

