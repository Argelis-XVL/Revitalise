# Improvement Review — 2026-10-02: WS-W part W8 — reviewer verdicts given on the work board

**Agent:** improvement-agent (tier `strategic`)
**Mode:** capability mode. This document is the authorising design for a new part **W8**, extending — not competing with — [capability design 2026-09-26, §W4 and §W5](docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L326). It changes how a verdict gets *into* the ledger; it does not reopen decisions S-1 to S-5 or D-5/D-8 of that design.
**Trigger:** capability mode — reviewer request 2026-10-02, verbatim: *"It would be nice to give my verdict in the ledger. but that option is not there now."* then *"Ok, process that change..."* ([routing.log, last line](logs/routing.log#L1236)).
**Findings processed:** 2 `NEW` (IMP-1012, IMP-1013, both logged by this dispatch while measuring) → 3 clusters
**Altitude:** ENGINE. The mechanism (CLI, board, validator) is reusable at any client; the only instance fact is the list of people allowed to give verdicts, held in `instance.yaml`.
**Commercial:** system work, non-billable, no WBS task ([C-COM-002](constraints/commercial/commercial-constraints.md#L35)).
**Gate:** `APPROVE IMPROVEMENTS` — **APPROVED 2026-10-02; applied in the working tree, uncommitted (see §12).** Authorisation record: `authorised_by` Xander Lykopoulos; `relayed_by` lead-agent; keyword quoted verbatim from the reviewer's own turn: *"D-V1 agreed, reviewers: Anna Southern, Xander Lykopoulos / D-V2 agreed / D-V3 agreed / D-V4 agreed / APPROVE IMPROVEMENTS"*. The authoriser was named in a second relay, quoting the session user's later turn verbatim: *"Xander authorised this"*; the first relay named no human and was refused (WORKFLOW, *What channel a keyword must arrive through*, condition 3). This dispatch did not see either turn itself. Read as: D-V1 = `work_items.reviewers: [Anna Southern, Xander Lykopoulos]`; D-V2, D-V3, D-V4 as recommended. The artefacts this act produces are the rows of §4. The keyword covers this review only.

---

## Summary

You will be able to open the work board, pick a verdict per item — *Verified in dev*, *Done*, or *Reopen* with your comment — and get one small verdicts file (download or copy). One command then writes every verdict into the ledger through the same checks a chat-relayed verdict goes through today, and reports each one as applied, already applied, or refused with the reason. The board still writes nothing to the repository itself.

Four decisions wait on you: where your name comes from (**D-V1**), who may sign as you (**D-V2**), what happens to the verdicts file (**D-V3**), and whether the board should offer *Done* before an item reaches production (**D-V4**). All four have a recommendation; none blocks the others.

---

## What has been built (proposed)

1. **The board offers only the verdicts the ledger would accept.** [`legal_from()`](.engine/scripts/lib/work_items.py#L280) is the one state machine; the export computes each item's options from it and embeds them, so the page never carries a second copy of the rules. An item at `deployed:dev` offers *Verified in dev* and *Reopen*; at `verified:dev` it offers *Done* and *Reopen*; below `built` it offers nothing and says why (there is nothing to record — the ledger already says "not done").

2. **A verdicts file, not a write-back.** The page opens from disk and cannot write anywhere ([D-5](docs/improvements/2026-09-26-improvement-review-5.md#L10), [Phase 11 "Read-only"](docs/improvements/IMPLEMENTATION-PLAN.md#L717)). It builds one JSON document and offers *Download*, *Copy*, and a visible text box as a fallback. Measured on this Mac in Microsoft Edge 154 from `file://`: the page is a secure context, and `Blob`, object URLs, the `download` attribute, the clipboard API and `localStorage` are all available.

3. **One new command applies the file: `work-items.py apply-verdicts <file|-> --by <reviewer|lead-agent> [--dry-run]`.** Each entry becomes an ordinary event through [`write_event()`](.engine/scripts/lib/work_items.py#L842) — same lock, same fold, same AUTHOR and evidence checks. Nothing bypasses the validator, because there is no second write path.

4. **A verdict applies only to the exact item state you looked at.** Each entry carries the ledger line of the item's latest event as the board showed it. If the item has moved since — even if it moved and came back to the same state, e.g. reopened, rebuilt and redeployed — the entry is refused as *stale* and you are asked to regenerate the board. The chat relay has no such guard today.

5. **Applying the same file twice changes nothing.** The second run reports every entry as *already applied* and leaves the ledger byte-identical; that falls out of rule 4 plus an exact match on the verdict already recorded.

6. **Two small defects found while measuring are fixed in the same change.** Reopens recorded with your verdict show on the board with no name or date, because the fold drops a reopen's evidence (4 of the 9 verdicts in the ledger are affected). And an item whose evidence has drifted since you verified it — WI-0009 today — shows as plainly verified, because the board never asks the verifier; it gets a *drifted* badge next to the *Reopen* control.

### Elements added

| Element | Where |
|---|---|
| `apply-verdicts` subcommand | [`.engine/scripts/work-items.py`](.engine/scripts/work-items.py#L342) |
| Verdicts-file parser, `verdict_options()`, per-entry applier | [`.engine/scripts/lib/work_items.py`](.engine/scripts/lib/work_items.py#L842) |
| Verdict panel (name, per-item choice + comment, Download / Copy) | [`.engine/templates/audit-viewer.html`](.engine/templates/audit-viewer.html#L192) |
| `work_items.reviewers` instance key | [`instance.yaml`](instance.yaml#L75) |

### Elements changed

| Element | Change |
|---|---|
| [lead-agent, *Work items* item 2](agents/lead-agent.md#L306) | Board route added beside the chat route; *"The work board never writes back"* ([L320](agents/lead-agent.md#L320)) becomes *"…never writes to the repository; it produces a verdicts file only `apply-verdicts` reads"* |
| [WORKFLOW hop table](agents/WORKFLOW.md#L644) | The `verified`/`done` row names both routes |
| [`export-audit-data.py`](.engine/scripts/export-audit-data.py#L153) | Bundle gains reviewers, per-item verdict options, latest event line, drift |
| [`validate-instance.py` check 8](.engine/scripts/validate-instance.py#L327) | Accepts `reviewers` |
| [`new-instance.py`](.engine/scripts/new-instance.py#L51) | `--reviewer NAME` (repeatable) |

---

## 0. Premises re-measured before drafting

| # | Brief said | Measured | Command |
|---|---|---|---|
| 1 | 103 items, none done; 5 `verified:dev`, ~60 `deployed:dev` | **105 items**, 0 done, 5 `verified:dev`, **56** `deployed:dev`, 27 `ready`, 14 `deferred`, 1 `reopened`, 2 `new`; 556 events | `python3 scripts/verify-work-items.py --check` |
| 2 | Verdicts arrive only via chat relay | True. 9 `reviewer-verdict` objects, all written `by: lead-agent`, all naming the same reviewer, dates 2026-09-25 → 09-30; **0 events `by: reviewer` ever** — the path exists in [`VERDICT_AUTHORS`](.engine/scripts/lib/work_items.py#L90) and has never been exercised | python one-liner over `logs/work-items.jsonl` |
| 3 | The ledger is clean | **It is not.** `--check` exits 1: WI-0009 (`verified:dev`) cites a line in `CasePanels.tsx` that commit `4eb731e` removed after the verdict. The build runs this step `--warn-only` ([build L160](config/revitalise-grant-automation-build.yml#L160)), so nothing surfaced it → IMP-1013 | as row 1 |
| 4 | `write_event` is the path to reuse | True, and it already enforces three of the four rules this capability needs: AUTHOR ([L575](.engine/scripts/lib/work_items.py#L575)), name-is-not-an-agent and date-not-after-the-event ([L723-L728](.engine/scripts/lib/work_items.py#L723)) | read + scratch run in review -5 |
| 5 | The reviewer's name could come from git | **No.** All 20 latest commits are authored by the same git identity, agent commits included, so `git config user.name` cannot tell the reviewer from an agent | `git log --format=%an -20` |
| 6 | Instance wrappers need parallel edits | No. `scripts/work-items.py`, `export-audit-data.py`, `validate-instance.py`, `verify-work-items.py` are thin wrappers; engine-only edits suffice | `ls -la scripts/…`; wrapper source |
| 7 | A personal-data screen on the comment is possible | **Email pattern only.** Over all 472 free-text fields in the ledger: email pattern 0 hits; a phone pattern 3 hits, **0 true** (two dates with a time, one build id). The phone screen is dropped; the email screen ships with a positive control in the self-test | python over `logs/work-items.jsonl` |
| 8 | Agent sessions can be told apart from a human terminal | An agent's shell carries `CLAUDECODE` in its environment (measured in this dispatch). **Not measured:** whether a `!` command typed by you inside Claude Code carries it too | `env` |

---

## 1. Regression check

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| W4 verdict relay — lead-agent records your words ([review -5 §3.1](docs/improvements/2026-09-26-improvement-review-5.md#L128)) | 2026-09-27 | verdicts inferred from a pipeline success or a summary | **No.** 9 verdicts over 4 sittings, each quoting you with a date at or before its event | **Working.** This review adds a second route; the relay stays |
| W5 work board ([review -5 §3.3](docs/improvements/2026-09-26-improvement-review-5.md#L162)) | 2026-09-27 | items falling out between agents unseen | **No recurrence of that class.** Two display gaps found (IMP-1012, IMP-1013) — new defects, not recurrences | **Working; extended** |
| W1 ledger closed schema + AUTHOR rule | 2026-09-26 | an agent writing `verified`/`done` | **No.** 0 refusals needed; 0 verdict events by any other agent | **Working — unchanged** |

**Recurred after a prose fix:** none. **Recurred after a gate:** none.

---

## 2. Clusters

```
CLUSTER: reviewer-verdict-entry-from-the-board  (capability — W8; extends design §W4/§W5)
Altitude:   ENGINE — CLI, library, template and validator name no client literal; the reviewer list
            is instance data in instance.yaml
Ladder row: "a tool could catch it mechanically" — every rule is enforced by write_event or the new
            file parser; the board only offers what the library computed
Becomes:    apply-verdicts (work-items.py), verdict parser/applier + verdict_options (lib), verdict
            panel (template), bundle fields (export), work_items.reviewers (validate-instance,
            new-instance, instance.yaml), lead-agent + WORKFLOW text
Retires:    nothing
Cites:      design §W4, §W5, D-8; reviewer request 2026-10-02
Residual:   a verdicts file handed to an agent cannot be proven to be the reviewer's; the comment
            screen catches email addresses only, not names or health detail; the stale guard
            protects board verdicts, not chat-relayed ones
```

```
CLUSTER: evidence-recorded-but-not-surfaced  (x2: IMP-1012, IMP-1013)
Altitude:   ENGINE — both defects are in engine code and name no client fact
Ladder row: "a tool could catch it mechanically" — a self-test assertion per defect
Becomes:    apply() copies a reopen's evidence into history; the export attaches the verifier's
            per-item drift to the bundle and the board shows it
Retires:    nothing
Cites:      IMP-1012, IMP-1013
Residual:   drift is shown only on a regenerated board; the warn-only build step is unchanged
```

```
CLUSTER: instance-reviewer-list  (capability — W8, instance scaffolding)
Altitude:   ENGINE mechanism, INSTANCE data
Ladder row: "a tool could catch it mechanically" — validate-instance check 8, already HARD
Becomes:    work_items.reviewers: list of names; validated; scaffolded by new-instance --reviewer
Retires:    nothing
Cites:      design §W6
Residual:   a name on the list is a declaration, not an identity check
```

---

## 3. Specification

### 3.1 The verdicts file

```json
{
  "schema": "work-item-verdicts/1",
  "instance": "<slug>",
  "board_generated_at": "2026-10-02T14:05",
  "name": "<one name from work_items.reviewers>",
  "verdicts": [
    {"item": "WI-0045", "as_of_line": 412, "from_state": "deployed:dev",
     "verdict": "verified", "env": "dev", "quote": "Works in dev.", "date": "2026-10-02"},
    {"item": "WI-0005", "as_of_line": 498, "from_state": "deployed:dev",
     "verdict": "reopen", "quote": "Order still differs from the PDF.", "date": "2026-10-02"}
  ]
}
```

- **Closed schema**, like the ledger: an unknown key anywhere refuses the file. No hours, rates or amounts can ride along.
- **`verdict`** ∈ `verified` · `done` · `reopen`. `env` is required for `verified`, absent otherwise.
- **`quote`**: required and non-empty for `reopen`. For `verified`/`done`, a blank comment is recorded as the label you clicked (e.g. *"Verified in dev"*) — your act, in the words on the button, and `via: board` marks it as such.
- **One name per file**, chosen once at the top of the board.
- **`date`** is the local date when you picked the verdict.

### 3.2 `apply-verdicts`: file-level first, then per entry

**Whole file refused (exit 2, nothing written)** when: it is not the schema above; `instance` is not this instance (an engine shared across clients must never apply one client's verdicts to another's ledger); `name` is not in `work_items.reviewers`, or is an agent name; two entries name the same item; or `--by reviewer` is used inside an agent session (D-V2).

**Then each entry on its own** — per item, not atomic. Each verdict concerns one item and is judged against that item's current state; making one refused verdict cancel the others would make you redo all of them for one stale row. Each entry is reported as one of:

| Outcome | When |
|---|---|
| `APPLIED` | written through `write_event` as `transition verified:<env>`, `transition done`, or `reopen --reason <quote>`, with a `reviewer-verdict` `{name, date, quote, env?, via: "board"}` |
| `ALREADY APPLIED` | the item's latest event is this exact verdict (same name, date, quote, env) — no write |
| `REFUSED [STALE]` | the item's latest event line ≠ `as_of_line`: it changed since the board was made |
| `REFUSED [FOLD]` / `[AUTHOR]` / `[EVIDENCE]` | whatever the ledger itself refuses — unchanged rules, unchanged messages |
| `REFUSED [DATE]` | `date` is before `board_generated_at` (a verdict cannot predate what it judged). A date after today is already refused by the ledger ([L726](.engine/scripts/lib/work_items.py#L726)) |
| `REFUSED [PERSONAL-DATA]` | the quote contains an email address |

Closing line: `apply-verdicts: <a> applied, <b> already applied, <r> refused of <n>`. Exit 0 when nothing was refused, 1 when anything was. `--dry-run` prints the same report and writes nothing. `-` reads the file from standard input, so a copied file can be applied without saving it anywhere.

If the file sits inside the repository and git does not ignore it, the command prints a note asking for it to be deleted: the ledger now holds the verdicts.

### 3.3 Board

- Name: a selector filled from `work_items.reviewers`; preselected when there is exactly one. With no list declared, the panel is replaced by one line saying how to declare it.
- Per item: a *Your verdict* cell with only the options the export computed, a comment box, and — for an item marked *drifted* — the verifier's message beside it.
- Choosing *Done* before the chain's last environment shows: *"Done ends this item: it will no longer be tracked through `<later envs>`."* (D-V4).
- One notice above the buttons: *"Your comments are stored in the project repository. Do not write applicants' names, contact details or health information."*
- Unsent choices are kept in the browser's local storage, keyed by the board's generation time, so a reload does not lose them; a regenerated board starts empty. Wrapped in try/catch; the page works without it.
- Kept from W5 and asserted by the self-test: no `fetch`, no `XMLHttpRequest`, no `http(s)://`, no `innerHTML`; **added:** no `<form`, no `action=`. Ledger text is still inserted only as text.

### 3.4 D-8 — does it still hold?

**Yes, and it is stronger in four specific ways and equal in one.**

- **Unchanged:** only `reviewer` or `lead-agent` can write `verified`/`done`, the evidence must carry a name that is not an agent, a date and a quote — the same [AUTHOR check](.engine/scripts/lib/work_items.py#L575), because `apply-verdicts` has no write path of its own.
- **Stronger:** (1) the words are typed by you, not transcribed by an agent; (2) the name comes from a declared list, not free text; (3) a verdict can only land on the item state you saw; (4) when you run the command yourself, `by: reviewer` is literally true for the first time.
- **Equal, not stronger:** a file handed to an agent cannot be proven to be yours — any process can write a file. That is the same limit the chat relay has ([verifier docstring](.engine/scripts/verify-work-items.py#L34)). Pasting the copied text into chat is better than a path, because it then arrives in your own turn.

### 3.5 Agent-file text

**lead-agent, *Work items* item 2** gains, after the verdict table:

> **Or the reviewer gives verdicts on the board.** When the reviewer hands you a verdicts file — a path, or the copied text pasted into the conversation — apply it unchanged with `python3 scripts/work-items.py apply-verdicts <file> --by lead-agent` (save pasted text to a scratch file first) and paste its per-entry report as printed. Never edit the file, and never re-enter a refused verdict by hand with different words; report the refusal and its reason. A `STALE` refusal means: regenerate the board and ask the reviewer to look again.

and the sentence at [L320](agents/lead-agent.md#L320) becomes *"The work board never writes to the repository; it produces a verdicts file, and only `apply-verdicts` reads it."*

**WORKFLOW hop table** ([L644](agents/WORKFLOW.md#L644)): `lead-agent, from the reviewer's words` → `the reviewer (board verdicts file, applied with apply-verdicts) or lead-agent from the reviewer's words`.

**Unchanged on purpose:** the chat relay rules, pm-agent, development-agent, and the TRACKER ADAPTER CONTRACT except one clause — its point 2 ([L52](.engine/scripts/lib/work_items.py#L51)) now names `apply-verdicts` as *the* read-back path, which makes the verdicts file the interface a future Jira or Azure Boards adapter would produce.

### 3.6 Tests

**`work-items.py --selftest`** (+16 assertions, fixture repo):

1. A file with one *verified*, one *done*, one *reopen* → 3 applied, exit 0; each event carries `via: board`.
2. The same file again → 3 already applied, exit 0, ledger byte-identical.
3. An entry with a stale `as_of_line` → that entry `STALE`, the others applied, exit 1.
4. An item that moved and returned to the same state → `STALE`.
5. *Verified* on a `built` item → `FOLD`.
6. Name not in the list → exit 2, ledger byte-identical. 7. Name is an agent → exit 2.
8. Date before `board_generated_at` → `DATE`. 9. Date after today → `EVIDENCE` (existing rule).
10. Wrong `instance` → exit 2. 11. Two entries for one item → exit 2. 12. Unknown key → exit 2.
13. Quote with an email address → `PERSONAL-DATA` (positive control for the 0-hit corpus).
14. `--by reviewer` with `CLAUDECODE=1` in the environment → exit 2; without it → accepted, events `by: reviewer`.
15. `--dry-run` → report printed, ledger byte-identical. `-` reads standard input.
16. A reopen carrying a verdict exports that verdict in its history (IMP-1012).

**`export-audit-data.py --selftest`** (+5): verdict options equal the library's for `ready`, `deployed:dev`, `verified:dev`, `done`; `reviewers` carried, and absent → empty list plus a note; a drifted item flagged and a clean one not (IMP-1013); the template has no `<form` and no `action=` and still none of the W5 words.

**`validate-instance.py --selftest`** (+3): valid list; an agent name in the list; a non-list. **`new-instance.py --selftest`** (+1): `--reviewer` writes the key and the scaffold validates.

**At apply, a browser round trip** (V2): render a fixture board in headless Edge with a `#selftest-verdicts` address that pre-selects one verdict and prints the resulting file into the page; dump the page; run `apply-verdicts --dry-run` on what it printed. This is the only check that the JavaScript's output and the Python parser agree. Headless Edge hung after each run in this dispatch and had to be killed by a timer — budget for it.

---

## 4. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | script | `.engine/scripts/lib/work_items.py` | Verdicts-file vocabulary and parser, `verdict_options()` from `legal_from()`, per-entry applier over `write_event`; `via` as an optional `reviewer-verdict` key; TRACKER contract point 2 names `apply-verdicts` (§3.1, §3.2, §3.5) | design §W4, D-8 | YES — `python3 scripts/work-items.py --selftest` | N/A — library |
| 2 | script | `.engine/scripts/lib/work_items.py` | `apply()`: a reopen's evidence goes into its history summary | IMP-1012 | YES — §3.6 case 16 | N/A — library |
| 3 | script | `.engine/scripts/work-items.py` | `apply-verdicts <file\|-> --by … [--dry-run]`, exit codes 0/1/2, agent-session guard on `--by reviewer`; +16 self-test assertions | design §W4, D-8 | YES — `python3 scripts/work-items.py --selftest` | N/A — write tool, no check mode |
| 4 | script | `.engine/scripts/export-audit-data.py` | Bundle gains `reviewers`, per-item `verdict_options` and `as_of_line`, and `drifted` from `verify-work-items.py --json`; +5 self-test assertions | design §W5, IMP-1013 | YES — `python3 scripts/export-audit-data.py --selftest` | N/A — not a gate; unwired by D-5 |
| 5 | template | `.engine/templates/audit-viewer.html` | Verdict panel (§3.3); header rules: "read-only" becomes "writes nothing except a file the viewer downloads or copies" | design §W5 | YES — row 4's template assertions, plus the browser round trip in §3.6 | N/A |
| 6 | script | `.engine/scripts/validate-instance.py` | Check 8 accepts `work_items.reviewers`: unique non-empty strings, none an agent name; +3 cases | design §W6 | YES — `python3 scripts/validate-instance.py --selftest` | already wired — HARD [`validate-instance`](config/revitalise-grant-automation-build.yml#L50) |
| 7 | script | `.engine/scripts/new-instance.py` | `--reviewer NAME` (repeatable) writes the key; +1 case | design §W6 | YES — `python3 .engine/scripts/new-instance.py --selftest` | N/A — scaffolder |
| 8 | other | `instance.yaml` | `work_items.reviewers: [<the reviewer's name>]` (D-V1) | D-V1 | YES — `python3 scripts/validate-instance.py instance.yaml` | N/A |
| 9 | agent | `agents/lead-agent.md` (engine) | Board route paragraph and the L320 sentence (§3.5) | design §W4, D-8 | Partly — the tool refuses what the paragraph forbids, except editing the file before applying | N/A |
| 10 | agent | `agents/WORKFLOW.md` (engine) | Hop-table row names both routes (§3.5) | design §W3 | N/A — instruction change | N/A |
| 11 | other | capability design, end of §W5 | One line: W8 specified in this review | — | YES — `grep -c "W8 is specified in" docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md` returns 1 | N/A |

**Constraint budget:** 0 of 3 used. [C-TECH-079](constraints/technology/technology-constraints.md#L149) (items move on evidence) and [C-COM-006](constraints/commercial/commercial-constraints.md#L44) (acceptance only from a human) already govern this; the change is mechanism under them.

**Order when applied.** Rows 1–3 first (the command must exist before the board offers anything); then 4–5; then 6–8; then 9–11. Engine files go on the engine branch `deploy-first-learning-and-item-closure`; the engine is pushed before the instance pointer bump.

---

## 5. Retirements

Nothing is retired.

> Retirement check performed: 87 live constraint rows grepped for verdict and work-item terms. Hits: C-TECH-055, C-TECH-061, C-TECH-065 (build warnings, the improvement queue, credentials) and C-TECH-079 (items move on evidence), which this change relies on rather than supersedes. The chat-relay instructions are kept, not retired: chat stays the route when you are not at the board.

---

## 6. Findings left unprocessed

**Deferred:** IMP-1010, IMP-1011

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| IMP-1010, IMP-1011 | Dataverse action mapping; ADR closed on handover | `unread`, logged today by the architect dispatch on the intake flow — not verdicts, the board or the ledger | the post-deploy batch after the intake rework deploys |

49 non-blocker entries are `awaiting-approval` in other parked reviews; named by count, not re-derived. **Processed here:** IMP-1012, IMP-1013, both `observable_at: V1`, so each closes at apply on an `evidence_grep` for its self-test assertion text.

---

## 7. Routed work — after this review is applied

| # | Agent | Work | Depends on |
|---|---|---|---|
| R1 | lead-agent | Regenerate the board and tell you WI-0009 is marked drifted, so you can reopen or re-verify it | rows 2 and 4 |
| R2 | (you) | First real use: give two or three verdicts on the board and apply them; the review's applied section records what happened | rows 1–8 |

---

## 8. What you need to decide

### Who you are, to the ledger

**D-V1. Should the names allowed to give verdicts be a declared list in `instance.yaml`?**

**Problem** — The verdict needs a name that is a person and not an agent, and git cannot supply one: every commit in this repository, the agents' included, carries the same author.
**Suggested fix** — Yes: `work_items.reviewers: [your name]`; the board offers it as a selector and the command refuses any other name. At other clients, `new-instance.py --reviewer` sets it.
**What happens if you don't** — The name is typed freely on the board, so a typo or a placeholder like "A Reviewer" becomes a recorded verdict. Your name in a tracked file is not applicant data and already appears in nine ledger lines.
[§0 row 5](docs/improvements/2026-10-02-improvement-review.md#L64) · [`instance.yaml` work_items](instance.yaml#L75)

---

**D-V2. Should only a command you run yourself be allowed to sign as `reviewer`?**

**Problem** — `--by reviewer` claims you wrote the event; if an agent may pass it, the ledger can no longer tell your act from an agent applying a file on your behalf.
**Suggested fix** — Yes: refuse `--by reviewer` when the command runs inside an agent session (detected by the `CLAUDECODE` variable); agents apply with `--by lead-agent`, which is what they are doing.
**What happens if you don't** — Every board verdict applied by an agent reads as written by you, which overstates what the ledger can prove. Not measured: whether a `!` command you type inside Claude Code carries that variable — if it does, you would run the command in an ordinary terminal or hand it to lead-agent.
[§0 row 8](docs/improvements/2026-10-02-improvement-review.md#L67) · [`VERDICT_AUTHORS`](.engine/scripts/lib/work_items.py#L90)

---

### The file

**D-V3. Should the verdicts file be throwaway transport, never tracked?**

**Problem** — The repository sits in a SharePoint library that syncs everything inside it, ignored or not, so any copy saved in the tree leaves the machine.
**Suggested fix** — Yes: the browser saves it to Downloads (outside the synced tree on this Mac) or you copy it; the command reads it from there or from the clipboard and asks you to delete any copy found inside the repository. The ledger line is the record.
**What happens if you don't** — Tracking the files duplicates every verdict in a second place that can disagree with the ledger, and every comment you ever typed is synced and kept twice.
[§3.2](docs/improvements/2026-10-02-improvement-review.md#L149) · [D-5](docs/improvements/2026-09-26-improvement-review-5.md#L10)

---

### What "done" means

**D-V4. Should the board offer *Done* as soon as an item is verified in dev?**

**Problem** — The ledger lets *Done* follow *Verified in dev* directly, and once done an item is no longer tracked through test/acceptance and production.
**Suggested fix** — Offer it wherever the ledger allows, with a one-line warning naming the environments it skips; changing the rule itself would change the chat route too and is a separate decision.
**What happens if you don't** — Hiding *Done* until production means nothing can be marked done on this project until a production deploy exists, while the chat route still allows it — two routes with two rules.
[`legal_from` done](.engine/scripts/lib/work_items.py#L303)

---

D-V1 and D-V2 change rows 1, 3, 6–8. D-V3 changes one note in row 3. D-V4 changes one warning in row 5. None blocks another.

---

## 9. Verification

**Executed for this draft:** `verify-work-items.py --check` on the real ledger (exit 1, one failure, measured above); the ledger profile and personal-data pattern measurement (472 fields); `git log` authorship; a headless Edge 154 probe from `file://` (secure context true; Blob, object URL, `download`, clipboard API, `localStorage` all present — capability present, **no actual download or clipboard write performed**, both need a user click); `verify-improvement-log.py --check` exit 0 after appending IMP-1012 and IMP-1013 (1009 entries).

**Not verified:** nothing is built. No verdict has been applied through the new path; the JavaScript↔Python round trip exists only as the apply-time check in §3.6. Level reached: V1 (design).

---

## 10. Digest impact

| | Before | After this draft |
|---|---|---|
| Log entries | 1007 | 1009 (IMP-1012, IMP-1013) |
| Entries closed by applying | — | 2 |

Regenerated with `python3 scripts/generate-known-failure-modes.py` at apply, after the validator passes.

---

## 11. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-10-02-improvement-review.md

Findings processed: 2 NEW  →  3 clusters
Regression check:   3 prior changes audited, 0 classes recurred
Proposed:           0 constraints (cap 3), 6 gates/scripts, 0 skill/knowledge edits,
                    2 agent-file edits, 0 retirements
Altitude calls:     3 generalised from instance to class, 0 left as notes
Digest:             will regenerate — 2 lessons added, closed on apply

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 12. Applied

Applied 2026-10-02 in the working tree, **uncommitted** (lead-agent: do not commit). Authorisation: the record in the header (`authorised_by` Xander Lykopoulos, `relayed_by` lead-agent); the first relay named no human and was refused before anything was touched. Before editing I re-ran `verify-improvement-log.py --check`: IMP-1014, IMP-1015 and IMP-1016 were appended after the draft; none names or `corrects` IMP-1012/1013 or touches the ledger, the board or `instance.yaml`.

| # | Change | Applied at | Entries moved to APPLIED |
|---|---|---|---|
| 1 | Verdicts-file vocabulary + parser, `verdict_options()`, `as_of_line()`, per-entry `apply_verdicts()` over `write_event` (new `dry_run` parameter), `via` on `reviewer-verdict`, `slug`/`reviewers` in the context, TRACKER contract point 2, VERDICTS FILE docstring | `.engine/scripts/lib/work_items.py` | — |
| 2 | Reopen history carries its evidence | `.engine/scripts/lib/work_items.py` | IMP-1012 |
| 3 | `apply-verdicts` + 23 self-test assertions (§3.6 cases 1–16, some cases asserting two things) | `.engine/scripts/work-items.py` | — |
| 4 | Bundle: `reviewers`, `chain`, `drifted`; items carry `verdict_options` and `as_of_line` (from row 1's export); `<form` and `action=` added to the forbidden words; +6 assertions | `.engine/scripts/export-audit-data.py` | IMP-1013 |
| 5 | Verdict panel, per-item verdict column, drifted lines, `#selftest-verdicts` hook; header rules rewritten | `.engine/templates/audit-viewer.html` | — |
| 6 | Check 8 accepts `reviewers`; +3 cases | `.engine/scripts/validate-instance.py` | — |
| 7 | `--reviewer` (repeatable); +2 scaffold assertions (written when given, absent otherwise) | `.engine/scripts/new-instance.py` | — |
| 8 | `work_items.reviewers: [Anna Southern, Xander Lykopoulos]` (D-V1 as answered) | `instance.yaml` | — |
| 9 | Board-route paragraph; L320 sentence | `agents/lead-agent.md` (engine) | — |
| 10 | Hop-table row names both routes | `agents/WORKFLOW.md` (engine) | — |
| 11 | W8 pointer at the end of §W5 | the capability design | — |

**Two deviations, both narrower than the text and neither changing what is enforced:**

- **The already-applied match compares name, date, quote and `via: board`, not `env`** (§3.2 said "same name, date, quote, env"). Measured while building the self-test: after *Done* or *Reopen*, the item's state has no environment in it, so a re-applied file derived no `env` and was falsely reported as stale instead of already applied. The env of a *Verified* verdict is still compared, through the target state `verified:<env>`.
- **Row 4's drift does not edit `verify-work-items.py`.** The export reads the verifier's existing `--json` and maps each failure to its item by the ledger line it names, so the verifier is unchanged.

**One correction this apply was obliged to make outside the table:** regenerating the digest moved its line count, so the CURRENT SIZE sentence in `scripts/generate-known-failure-modes.py` (and its byte-identical engine copy) now reads 612, which is what `verify-derived-counts.py` measures.

**IMP-1012** → `APPLIED`, `evidence_grep` `.engine/scripts/lib/work_items.py` / `IMP-1012: a reopen carries the reviewer's verdict` (1 match). **IMP-1013** → `APPLIED`, `evidence_grep` `.engine/scripts/export-audit-data.py` / `evidence failures, mapped to the item by` (1 match). Both `observable_at: V1`, so no `reobserved` is required.

**What was executed, and what it returned:**

- `work-items.py --selftest`: 53 of 53 OK, exit 0 (30 before). **Can it fail:** two mutants, both caught — dropping the stale guard fails cases 3 and 3/4; dropping the already-applied match fails case 2.
- `export-audit-data.py --selftest`: 28 of 28 OK (22 before). `validate-instance.py --selftest`: PASS, 22 cases (19 before). `new-instance.py --selftest`: PASS. `verify-work-items.py --selftest`: OK.
- **Real export of this repo:** 105 items. Verdict options: 56 items offer *Verified in dev* + *Reopen*, 5 offer *Done* + *Reopen*, 14 deferred items offer *Reopen*, 28 offer nothing (all below `built` or already reopened). Drift: 1 item, WI-0009, the verifier's one failure — 1 finding, 1 true. All 4 reopens now show their verdict's name and date.
- **Browser round trip (V2):** headless Microsoft Edge 154 opened the real board from `file://` with `#selftest-verdicts`; it rendered 75 verdict selectors (56 + 14 + 5), the notice, and a verdicts file for WI-0005 naming Anna Southern. `apply-verdicts --dry-run --by lead-agent` on that file: `WOULD APPLY WI-0005 verified:dev`, exit 0, ledger sha unchanged. The same file with `--by reviewer` from this agent session: whole file refused (D-V2), nothing written. Edge hung after the dump and was killed by a 90-second timer, as in review -5.
- `verify-work-items.py --check` on the real ledger: still exit 1 on WI-0009 — **unchanged, not caused by this apply.** It is the defect the board now shows (routed R1).
- `validate-instance.py instance.yaml`: PASS. `verify-engine-instance-split.py`: exit 0 (98 scripts; no new script, every edited instance script is a wrapper). `verify-build-config.py`: exit 0. `verify-system-consistency.py`: PASS. `verify-improvement-log.py --check`: exit 0 (1015 entries). Digest regenerated; `--check` current.
- `verify-derived-counts.py`: 7 drifted claims (8 before the digest-size fix), all pre-existing and none touched by this review: pipeline config row counts, dev-summary and role column counts, the supplied-assets file count, and this agent file's `verify-*.py` count (67 stated, 69 measured — no script was added here). SOFT.
- Engine-literal sweep over every line this review added to engine files: 0 client literals (positive control: 4 in `instance.yaml`).

**Level reached (C-TECH-053):** V1 for the scripts and rules, plus a V2 machine round trip of page → file → applier. **Not verified:** a person has not yet given a verdict on the board, no real download or clipboard write has happened (both need a click), and no verdict has been written to the real ledger through the new path (R2). Whether a `!` command typed inside Claude Code carries `CLAUDECODE` is still unmeasured.
