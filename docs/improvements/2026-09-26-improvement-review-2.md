# Improvement Review — 2026-09-26 (2) — Group 4: agents read only their digest sections (WS-Z)

**Agent:** improvement-agent (tier `strategic`)
**Mode:** capability — authorised by [the deploy-first learning and item-closure design, WS-Z](docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L403), Group 4 of its [sequencing table](docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L430). Nothing else from that document is in scope here.
**Findings processed:** 1 NEW → 1 clusters
**Trigger:** reviewer request (capability mode), dispatched by lead-agent in parallel with Groups 1 and 3
**Gate:** `APPROVE IMPROVEMENTS` — **APPLIED 2026-09-26**: changes 1–4 applied; change 5 (`CLAUDE.md`) withheld. See section 8. ~~Not yet sent, deliberately. Nothing below has been applied.~~
**Scope:** `system`, non-billable, outside the contracted WBS ([`C-COM-002`](constraints/commercial/commercial-constraints.md)). No `wbs:` id.
**Branch when applied:** instance repo `deploy-first-learning-and-item-closure`; the engine copy of the generator and the three agent files go on a same-named branch in `.engine`, not engine main.

---

## Summary

Three agents currently read the whole 137 KB failure digest when they start. This review proposes that they read only the sections for their moment instead. The generator gets stable section markers and a `--for <agent>` print mode, and the per-agent section list lives in one place, the generator. Measured before and projected after: build-agent reads **137,123 → 46,085 bytes**, pipeline-agent **137,123 → 55,664**, lead-agent **137,123 → 30,557**. The six other agents that read the whole file gain a 16% smaller file, because the Unrouted section moves to the appendix.

**Two things need you.** Approve the section map, which is wider than the design's (decision Z-1): re-measurement showed the design's list drops the very sections that two agents' own start-up step cites as its reason. And confirm that moving the Unrouted section to the appendix is acceptable (decision Z-2).

---

## What has been built

Nothing yet. What is **proposed**, and was proven in a scratch prototype against the real log (the prototype is not in the tree):

1. **Every digest section gets a stable marker, and the sections split the file losslessly.** — [the section routing table](scripts/generate-known-failure-modes.py#L344), [the renderer](scripts/generate-known-failure-modes.py#L951)
   Each `## ` heading is preceded by an invisible `<a id="kfm-<key>"></a>` line. The keys are the routing table's existing keys (`before-build`, `before-deploy`, …) plus `how-to-use`, `recurring`, `capabilities`, `unrouted` and `cannot-tell`. In the prototype, every moment section came out byte-identical to today's; only the framing changed.

2. **`--for <agent>` and `--section <key>` print only the named sections, reading the written file and never the log.** — [where `main()` currently loads the log first](scripts/generate-known-failure-modes.py#L1403)
   The generator refuses to run over a malformed log (by design, since eleven bad entries were appended in one afternoon). If the print mode sat behind that refusal, one bad append by any agent would blind build-agent's start-up read, so the print runs before the log is touched. The prototype printed correctly with `--log` pointing at a file of invalid JSON.

3. **The per-agent map lives in the generator, not in the agent files.** — a new `STEP0_READS` table beside [the routing table](scripts/generate-known-failure-modes.py#L344)
   Agent files run `--for <agent>` and name no sections. That is the lesson of the drifted batch threshold (WS-Y, in Group 1): a hand-typed copy in four files drifts. The digest's own "How to use this file" block renders the map as a table, so whoever reads the whole file sees it too.

4. **The Unrouted section moves to the appendix; a short pointer stays.** — [the Unrouted renderer](scripts/generate-known-failure-modes.py#L990)
   It holds 478 lessons at 899 entries, across 167 classes (123 of them single-instance). The digest rendered 20 of them, and no agent's moment reads it. The pointer keeps the count and the eight largest classes, so the routing debt stays visible. The appendix now carries all of them in full. Decision Z-2 explains why routing them by hand is not proposed.

5. **Three agent files and `CLAUDE.md` run the command instead of reading the file.** — [build-agent step 0](agents/build-agent.md#L64), [pipeline-agent step 0](agents/pipeline-agent.md#L56), [lead-agent Knowledge to Load](agents/lead-agent.md#L349), [`CLAUDE.md` session-start step 3](CLAUDE.md#L60)
   Each keeps a fallback. A non-zero exit means the digest is missing or predates the markers, and the agent then reads the whole file and says so. A failure opens the full read; it never leaves the agent with no read at all.

---

## Measured: bytes read at activation step 0, per agent

**"Before" is measured.** It is `wc -c logs/known-failure-modes.md` on 2026-09-26 at 899 log entries, after regeneration: **137,123 bytes, 786 lines.** All three agents read the whole file. The Read tool adds a line-number prefix of roughly 8 bytes per line (about 6 KB) on top; that is not counted on either side.

**"After" is PROJECTED.** It is the byte count of the prototype's `--for <agent>` output, run on the same log. It will be re-measured on the applied change and recorded under "8. Applied".

| Agent | Before (measured) | After, recommended map (projected) | After, design's literal map (projected) |
|---|---|---|---|
| build-agent | 137,123 | **46,085** (−66.4%) | 22,387 (−83.7%) |
| pipeline-agent | 137,123 | **55,664** (−59.4%) | 31,963 (−76.7%) |
| lead-agent | 137,123 | **30,557** (−77.7%) | 21,357 (−84.4%) |
| **Three agents, one activation each** | **411,369** | **132,306** (−67.8%) | 75,707 (−81.6%) |
| Each of the six whole-file readers (improvement, development, test, pm, commercial, acceptance) | 137,123 | **114,838** (−16.3%), from item 4 only | 114,838 |

At roughly 4 bytes per token, that is about 34k tokens before, against about 11.5k / 13.9k / 7.6k after.

What each print contains, beyond the always-printed framing (title block, *How to use this file*, *What this file cannot tell you*: 1,925 bytes together):

| Agent | Sections (recommended map) | Design's list |
|---|---|---|
| build-agent | Before you execute a build config · **Before you report SUCCESS at all** · Operating constraints · **Capabilities** | first and third only |
| pipeline-agent | Before you declare a deploy… · **Before you report SUCCESS at all** · Operating constraints · Before you run something on a machine… · **Capabilities** | without the two in bold |
| lead-agent | Recurring classes · **Before you extend this system or accept a new kind of input** | Recurring classes only |

**Growth.** Every moment section is bounded by the existing 20-lesson cap and 600-character lesson budget, so the three prints grow only through the Recurring-classes table, which is lead-agent's read. The selftest's size-envelope checks still pass on the prototype: 114,959 / 119,385 / 132,355 bytes at 700 / 1,000 / 1,500 entries (last run at 903 entries, as sibling sessions appended), against limits of 145,000 / 155,000 / 175,000.

---

## Premises re-measured before drafting

| The design said | Measured | Consequence |
|---|---|---|
| The digest is read whole at step 0 by build-agent, pipeline-agent and lead-agent | **Nine** agents read it at activation: those three, plus [development](agents/development-agent.md#L26), [test](agents/test-agent.md#L22), [pm](agents/pm-agent.md#L21), [commercial](agents/commercial-agent.md#L19), [acceptance](agents/acceptance-agent.md#L16) and [improvement](agents/improvement-agent.md#L99). The generator's own [stdout line](scripts/generate-known-failure-modes.py#L1512) names a sixth, different list | Only the three named agents are in this dispatch's file scope. The other six are an open item below; item 4 still shrinks what they read |
| The Unrouted section is 27% of the digest | 27% of **lines** (213 of 786), **17.5% of bytes** (23,990 of 137,123). Bytes are what an agent pays | Moving it removes 23.1 KB; net of the added map table and markers, the whole file shrinks by 22.3 KB |
| build-agent needs *Before you execute a build config* + *Operating constraints* | build-agent's step 0 cites two findings as its reason to read at all. One renders in *Before you report SUCCESS at all*, the other is filed under *Capabilities*. Neither section is on the design's list | Recommended map adds both (Z-1) |
| pipeline-agent needs *Before you declare a deploy…* + *Before you run something on a machine…* + *Operating constraints* | pipeline-agent's step 0 names *Capabilities established in earlier sessions* **by title** as directly about its work, and cites the same capability finding | Recommended map adds *Capabilities* and *Before you report SUCCESS at all* (Z-1) |
| lead-agent needs *Recurring classes* only | *Before you extend this system or accept a new kind of input* is, by its routing-table comment, "when a request arrives that is not a feature": capability requests with no route, input types with no owning agent, report shapes. That moment is lead-agent's | Recommended map adds it (Z-1) |
| "assigned sections by the generator, or moved to the appendix" | 167 classes, 123 with one lesson each. Routing them would put them behind section caps that already hide 92, 53 and 35 lessons in the busiest sections | Move to the appendix (item 4, Z-2) |

The premise failure is recorded as a finding ([line 899 of the log](logs/improvement-log.jsonl#L899)).

---

## 1. Regression check — did the last review's changes work?

The last changes to this read path were the per-lesson length budget (WS-N, 2026-09-01), the recency-first sort key (2026-09-01) and the `--subject` search. None of them was re-audited by a later review in this area.

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| Per-lesson 600-char budget, lessons relocated to the appendix (WS-N) | 2026-09-01 | digest size growth | NO — 69 lessons truncated at 899 entries, every one present in full in the appendix; the selftest confirms | **Working — leave alone** |
| Sort key "recurring, blocker, unfixed, newest" ([`sort_key`](scripts/generate-known-failure-modes.py#L779)) | 2026-09-01 | `digest-cap-hides-a-whole-subject-area` | **YES — a third instance, found while drafting this review.** In *Capabilities*, all 53 capped lessons are `APPLIED`, including the provisioning-certificate capability that build-agent and pipeline-agent cite as their reason to read the digest. For a defect, "applied" means fixed. For a capability it means established, so the key ranks every settled capability last | **Right key for defects, wrong key for capabilities.** Logged as a new finding ([log line 898](logs/improvement-log.jsonl#L898)). It is outside this dispatch's authority and listed as deferred in section 5 |
| `--subject <term>` search across rendered, capped and relocated lessons | 2026-08-28 | same class | not recurred as an unfindable lesson | **Working** — it is the fallback the recommended agent wording points to |

**Changes whose class recurred after a *gate*:** none. The sort key is code, but no gate asserts which lessons render, so its recurrence is a missing assertion and not a gate that failed to fire. The new finding proposes that assertion.

---

## 2. Clusters and promotion decisions

```
CLUSTER: finding-premise-fails-re-measurement — WS-Z requirement  (x1: IMP-0903)
Altitude:   ENGINE — section keys, the agent roster and the print mode are the same at every
            client; no client literal in any proposed text (grepped: no "Revitalise", "rev_",
            environment name or thumbprint in the change)
Ladder row: "the system's own memory failed → a read-path change" (activation step 0), done at
            the most mechanical home: one generator table + one command, not four prose lists
Becomes:    generate-known-failure-modes.py: section markers, STEP0_READS, --for/--section
            printed from the written file before the log is loaded; Unrouted relocated to the
            appendix; header renders the map. Three agent files + CLAUDE.md run --for <agent>
Retires:    nothing — no gate or constraint row covers what an agent reads at step 0.
            C-TECH-059 (the learning substrate is never destroyed) is unaffected: its Verify By
            is `generate-known-failure-modes.py --check`, which still checks both files
Cites:      IMP-0903 (design premises re-measured); requirement WS-Z of the authorising design
Residual:   (1) Six other agents still read the whole file — one map row + one agent-file line
            each; not in this dispatch's file scope. (2) The Capabilities ranking hides settled
            capabilities (IMP-0902, deferred). (3) A new client's CLAUDE.md is hand-written;
            the engine scaffolds no CLAUDE.md, so only lead-agent.md carries the change to
            other instances. (4) Nothing checks that an agent actually ran --for rather than
            reading the file — this is prose, like the step it replaces
```

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | script | `scripts/generate-known-failure-modes.py` **and** `.engine/scripts/generate-known-failure-modes.py`, kept byte-identical | Section markers; `STEP0_READS`; `--for AGENT` / `--section KEY` printed from the written digest **before** the log is loaded; Unrouted relocated to the appendix, with a pointer carrying the count and the largest classes; "How to use" renders the map; stdout reader list no longer hand-typed; `Usage` docstring; `CURRENT SIZE` line rewritten after regeneration. Selftest section D adds 11 checks (below) | IMP-0903 | YES — `python3 scripts/generate-known-failure-modes.py --selftest`; `--check`; `python3 scripts/verify-engine-instance-split.py` | already wired — build step at [config L113](config/revitalise-grant-automation-build.yml#L113) runs `--check` |
| 2 | agent | [`agents/build-agent.md` L64-L67](agents/build-agent.md#L64) | Step 0 runs `--for build-agent`; whole-file fallback on a non-zero exit | IMP-0903 | N/A — instruction change | N/A |
| 3 | agent | [`agents/pipeline-agent.md` L56-L60](agents/pipeline-agent.md#L56) | Step 0 runs `--for pipeline-agent`; keeps "do not ask the reviewer to re-supply", now pointing to `--subject` | IMP-0903 | N/A — instruction change | N/A |
| 4 | agent | [`agents/lead-agent.md` L349](agents/lead-agent.md#L349) | Knowledge to Load names `--for lead-agent` | IMP-0903 | N/A — instruction change | N/A |
| 5 | other | [`CLAUDE.md` L60-L62](CLAUDE.md#L60) | Session-start step 3 runs `--for lead-agent`; its last sentence is kept verbatim | IMP-0903 | N/A — instruction change | N/A |

**Constraint budget:** 0 of 3 used.

**Selftest section D, all 11 passing on the prototype against the real log:** every marker is a known key and appears once · the sections partition the digest losslessly · the framing keys are present · `STEP0_READS` names only real keys · no agent is assigned *Unrouted* · every Unrouted lesson is in the appendix in full (0 missing) · the digest renders no Unrouted lesson body · **negative:** removing one marker drops that key · `--for build-agent` prints exactly its sections plus the framing · **negative:** an unknown key exits 2 · **negative:** a digest without markers exits 1 rather than printing a partial read. The "no Unrouted body" check can fail: against today's digest it finds 20. Sections A–C of the existing selftest also pass unchanged.

**Other readers of the digest, checked so this change breaks none of them.** [`verify-handover-pack.py`](scripts/verify-handover-pack.py#L46) matches the *Capabilities* heading, and headings are unchanged. The marker line added before the next heading contains no thumbprint, GUID or "keychain", so its extraction is unaffected. [`verify-improvement-log.py`](scripts/verify-improvement-log.py#L825) falls back to the appendix when an `evidence_grep` needle is absent from the digest, so relocating Unrouted lessons cannot turn a green entry red. The one needle in the log that targets the digest itself already relies on that fallback. The nine needles that target the generator's source name strings this change does not remove.

**Proposed wording (rows 2–5).** Applied verbatim unless the reviewer changes it:

> **build-agent step 0:** 0. **Run `python3 scripts/generate-known-failure-modes.py --for build-agent` — before your config, not after.** It prints the sections of `logs/known-failure-modes.md` that apply at your moment (its first line names them), and every line is a defect that actually happened here. Treat it as a checklist against the config you are about to run, not as background reading (`IMP-0016`, `IMP-0022`). The whole file stays the reference: read it, or run `--subject <term>`, when your work reaches an area those sections do not cover. **A non-zero exit means the digest is missing or predates its section markers — read the whole file instead, and say so in your gate output.**

> **pipeline-agent step 0:** 0. **Run `python3 scripts/generate-known-failure-modes.py --for pipeline-agent` — before your config, not after.** It prints the sections of `logs/known-failure-modes.md` that apply at your moment (its first line names them). **Do not ask the reviewer to re-supply something this file records** — search it first with `--subject <term>`, which also finds lessons the section caps hide (`IMP-0022`; history → *Activation step 0*). A non-zero exit means read the whole file instead, and say so in your gate output.

> **lead-agent Knowledge to Load:** - `python3 scripts/generate-known-failure-modes.py --for lead-agent` (on activation, before routing — the digest sections a router needs; the whole `logs/known-failure-modes.md` is the reference when a question reaches beyond them)

> **CLAUDE.md step 3:** 3. Run `python3 scripts/generate-known-failure-modes.py --for lead-agent` ← the sections of the generated `logs/known-failure-modes.md` a router needs; the whole file stays the reference. Needed before routing, because a `blocker` finding routes to improvement-agent immediately.

The last sentence of step 3 is kept word for word, because Group 2 (WS-U) owns how blocker routing changes.

**No overlap with the parallel drafts.** Group 1 edits build-agent step 7b and pipeline-agent L112-L131. WS-X edits pipeline-agent's success rule. WS-W1 adds new scripts. None of them touches step 0, lead-agent's Knowledge to Load, `CLAUDE.md` step 3 or this generator. Whoever applies second re-reads the target lines first (improvement-agent step 8).

---

## 4. Retirements

> Retirement check performed: 86 live and 10 retired constraint rows (`grep -rh '^| C-' constraints/ --include='*.md' | wc -l`; `grep -rh '^| ~~C-' …`). One row names the digest, [`C-TECH-059`](constraints/technology/technology-constraints.md#L129), and it stays: this change leaves its Verify By (`--check`) intact. No other gate, script or skill governs what an agent reads at step 0, so nothing is superseded. The one thing retired in substance is a hand-typed list, the generator's stdout "Read at activation by …" line, which today names six agents and is wrong about which ones.

---

## 5. Findings left unprocessed

**Deferred:** IMP-0902

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| IMP-0902 | `digest-cap-hides-a-whole-subject-area` | Logged by this review. The Capabilities section's ranking hides every settled capability. The fix changes which lessons render, and WS-Z's authority covers which sections are read, not their contents | the next post-deploy batch, or any review of the digest's ranking |

**Excluded by mode, not deferred:** the 12 findings that were `unread` at dispatch (IMP-0862, IMP-0887, IMP-0891–IMP-0900) and the entries sibling sessions appended during this draft (IMP-0901 and IMP-0904 onward). This is a capability dispatch scoped to one workstream. None of them concerns the digest read path; checked by searching each entry for the digest, step 0 and section reads. IMP-0855 is `awaiting-approval` under another review's document.

---

## 6. Digest impact

| | Before (measured, 899 entries) | After (projected, same log) |
|---|---|---|
| Log entries | 899 | 899 |
| Distinct lessons | 890 | 890 (none removed; 476 relocated) |
| Digest bytes | 137,123 | 114,838 |
| Digest lines | 786 | 602 |
| Appendix bytes | 491,128 | 497,652 (+ the 20 Unrouted lessons the digest used to render, in full) |

The digest was regenerated by this dispatch after appending its two findings (`--check` exit 0 at 899 entries). The `CURRENT SIZE` sentence in the generator's docstring is a registered claim ([registry row](scripts/derived-counts-registry.json#L128)). The change moves it from 779 to about 602 lines, so `verify-derived-counts.py` runs on apply.

---

## What is still open

**Six agents still read the whole file.** development, test, pm, commercial, acceptance and improvement. Three of them (development, pm, commercial) already name the one section they care about in their start-up step, so each is one map row plus one line. They are outside this dispatch's file list, and `development-agent.md` is being edited by Group 1. Recommended as a small follow-on once Group 1 lands. test-agent should probably stay on the whole file: its instruction is "every line", and it uses the list as a coverage checklist.

**The Capabilities ranking hides the capability that start-up step exists for.** Logged and deferred (section 5). Until it is fixed, the recommended pipeline-agent wording points to `--subject`, which finds a capped capability (`--subject certificate` returns it).

**Nothing verifies that an agent ran the command.** It is an instruction, exactly like the "read the file" instruction it replaces. No gate can observe what an agent read.

---

## What you need to decide

**Z-1. Approve the wider section map, or keep the design's literal one?**

**Problem** — The design's list for build-agent and pipeline-agent drops the two sections holding the findings their own start-up step cites as its reason, and it leaves lead-agent without the section about the requests it routes.
**Suggested fix** — Approve the recommended map: build 46,085, pipeline 55,664, lead 30,557 bytes, still a 68% cut across the three.
**What happens if you don't** — The design's map saves another 57 KB per three activations (75,707 in total). The price is that pipeline-agent no longer sees the capabilities it is told never to ask you for again, which is the incident this read path was built for.
[Premises table](docs/improvements/2026-09-26-improvement-review-2.md#L70) · [design WS-Z](docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L403)

---

**Z-2. Is moving the Unrouted section to the appendix acceptable?**

**Problem** — 478 lessons have no section, and no agent's moment reads them. Yet the 20 the digest renders cost every whole-file reader 23 KB.
**Suggested fix** — Relocate all of them to the appendix. Keep a pointer with the count and the largest classes, and use `--routing` to decide what to route later.
**What happens if you don't** — The six whole-file readers keep the 20 rendered lessons and the 23 KB cost. The design's other option, routing them by hand, puts most of them behind section caps that already hide 35 to 92 lessons each, so they are no more visible.
[Unrouted renderer](scripts/generate-known-failure-modes.py#L990)

---

Verification reached: V1 for the proposal. A scratch prototype of change 1 passed the existing selftest (sections A–C) and all 11 new checks, printed all three maps, and printed with an invalid log. Every moment section was byte-identical to today's digest. **Not verified:** the change is not applied to the tree, the engine copy is not edited, `verify-engine-instance-split.py` and `verify-derived-counts.py` have not been run against an applied change, and no agent has yet started up on `--for`.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-26-improvement-review-2.md

Findings processed: 1 NEW  →  1 clusters
Regression check:   3 prior changes audited, 1 classes recurred
Proposed:           0 constraints (cap 3), 1 gates/scripts, 0 skill/knowledge edits,
                    3 agent-file edits, 0 retirements
Altitude calls:     1 generalised from instance to class, 0 left as notes
Digest:             will regenerate — 890 lessons, relocation only; per-agent reads 46,085 / 55,664 / 30,557 bytes (projected)

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Applied

Filled in **after** `APPROVE IMPROVEMENTS`, not before. On apply: re-measure the "after" column from the applied generator and record the measured figures here.

### Authorisation record (written before any change was made)

| Field | Value |
|---|---|
| `authorised_by` | Xander Lykopoulos (the reviewer) |
| `relayed_by` | lead-agent, quoted from Xander Lykopoulos's own conversation turn, 2026-09-26 |
| Keyword, verbatim | "Z-1 take the wider one. / Z-2 agreed, move to appendix. / Approve improvements" |
| Decisions | Z-1: the wider (recommended) section map. Z-2: move the Unrouted lessons to the appendix, with a pointer |
| Scope authorised | changes 1–4 of section 3. **Change 5 (`CLAUDE.md` step 3) is NOT applied:** a relayed message cannot authorise a `CLAUDE.md` edit, and lead-agent is putting it to the reviewer directly |
| First relay | refused 2026-09-26: it named no human (`agents/WORKFLOW.md` → "What channel a keyword must arrive through", condition 3). This record is from the corrected relay |

| # | Change | Applied at | Entries moved to APPLIED |
|---|---|---|---|
| 1 | Generator: section markers, `STEP0_READS` (the wider map, Z-1), `--for` / `--section` printed before the log is loaded, Unrouted relocated to the appendix (Z-2), header renders the map, stdout reader list derived from the map plus a per-agent byte line, `Usage` docstring, `CURRENT SIZE` set to 603 lines. Instance and engine copies byte-identical | engine `3d9aa64` (branch `deploy-first-learning-and-item-closure`, pushed); instance commit on the branch of the same name | IMP-0903 |
| 2 | build-agent step 0 runs `--for build-agent`, whole-file fallback | engine `3d9aa64` | — |
| 3 | pipeline-agent step 0 runs `--for pipeline-agent`, points to `--subject` | engine `3d9aa64` | — |
| 4 | lead-agent Knowledge to Load names `--for lead-agent` | engine `3d9aa64` | — |
| 5 | `CLAUDE.md` step 3 | **NOT APPLIED** — needs the reviewer's own instruction (see the authorisation record) | — |

**Measured after apply, at 903 log entries** (the log grew while this was drafted, so "before" was re-measured by running the pre-change generator from `HEAD` over the same log):

| Agent | Before (pre-change generator, 903 entries) | After (applied `--for`, 903 entries) |
|---|---|---|
| build-agent | 137,264 | **46,085** (−66.4%) |
| pipeline-agent | 137,264 | **55,664** (−59.4%) |
| lead-agent | 137,264 | **30,678** (−77.7%) |
| Whole-file readers | 137,264 | **114,959** (−16.3%) |

The measured figures match the projection to the byte for build-agent and pipeline-agent. lead-agent differs by 121 bytes, because its Recurring-classes table grew with the four entries appended since.

**Verification executed:**
- `generate-known-failure-modes.py --selftest`: exit 0, 28 PASS, including all 11 in section D.
- `--check`: exit 0.
- `verify-engine-instance-split.py`: exit 0, and the two copies are identical by `cmp`.
- `verify-derived-counts.py`: exit 0, all 11 registered claims match, including the new 603-line figure.
- `verify-improvement-log.py --check`: exit 0.
- `--subject certificate` still returns the capped provisioning-certificate capability.

**Rejected:** none. **Withheld:** change 5 only, for the reason in the authorisation record. **Deviations from the approved wording:** none.

**Not verified:** no agent has yet started up on `--for`. That is V1 for the instruction change; the first build-agent or pipeline-agent dispatch is the observation.
