# Improvement Review — 2026-10-22 (2)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 2 `NEW` → 1 cluster
**Trigger:** reviewer request, as relayed by lead-agent. **Read the authority note under *What you need to decide*, because the quote relayed does not name this fix.**
**Status:** APPLIED 2026-10-22 15:24, rows 1 and 2, to the `.engine` working tree, on the reviewer's "Approve improvements" for this document (Xander Lykopoulos, 2026-10-22, relayed by lead-agent). The engine commit, its push and the pointer bump are the reviewer's. See the [applied record](#applied-record--2026-10-22).
**Serves:** `wbs:6.3`, WI-0146, WI-0147, WI-0148, `feature:trustee-portal-design-2`
**Gate:** `APPROVE IMPROVEMENTS`

---

## Summary

The work-item checker re-checks the file path on every historic `created` event. Once a file is renamed, an item can never clear that failure, even after pm-agent re-links it the correct way. The drafted engine fix checks each item's current path once and still fails when that path is missing. On the real ledger it removes exactly the three failures on WI-0146, WI-0147 and WI-0148 and adds none. Nothing is applied. It can go into the same engine commit as the release-profile flag from review (1).

## What has been built

1. **The checker now checks each item's current `source_ref`, not every superseded one** — [ref_problems](.engine/scripts/lib/work_items.py#L534), [fold](.engine/scripts/lib/work_items.py#L940).
   On replay, `fold()` no longer checks whether the files named by past events exist. It records which ledger line set each item's current `source_ref`, and after replay it checks that one path. A missing path is still a `[REF]` failure, reported at that line. The write path keeps its check, so a new event naming a missing file is still refused.

2. **It can still fail, and the new tests catch the bug.** Four tests are added to the selftest of [verify-work-items.py](.engine/scripts/verify-work-items.py#L135).
   - A superseded path whose file is later deleted passes.
   - A current path whose file is deleted fails.
   - Re-linking back onto a deleted file fails.
   - The failure is reported at the line that set the path.
   Run against today's library, the first of these fails (`got ['REF'], want []`), so the test is not vacuous.

3. **On the real ledger, the scoped check that pm-agent is stuck on goes from exit 1 to exit 0.** `verify-work-items.py --check --scope WI-0146,WI-0147,WI-0148 --at-least built` drops from 3 `[REF]` failures (ledger lines 921–923) to 0. The unscoped check drops from 329 failures to 326. A diff of the two failure lists shows exactly those three lines removed and nothing added. All three removed failures point at the deleted `trustee-review-portal-cards` folder, and each item's current path exists.

## Elements changed

| File | Repository | Change |
|---|---|---|
| [lib/work_items.py](.engine/scripts/lib/work_items.py#L534) | **engine** | `source_ref_problem()`, a `check_source` parameter on `ref_problems` and `structural_problems`, `Item.source_ref_line`, and a current-ref check at the end of `fold()` (§A) |
| [verify-work-items.py](.engine/scripts/verify-work-items.py#L135) | **engine** | 4 selftest cases (§B) |

## What is still open

**The other 326 failures in the unscoped ledger check are not touched.** They are older drift in other items. The build step runs this check as warn-only ([build config L182](config/revitalise-grant-automation-build.yml#L182)), so it blocks nothing. This review does not change how they are counted.

**The sibling finding's proposed lead-agent rule is rejected.** It said that amending a built item needs a reopen that counts against the item. The ledger shows otherwise: after pm-agent's `reopen --retrace`, all three items fold with `reopens 0`. A retrace is not counted ([apply, L914](.engine/scripts/lib/work_items.py#L914)). The actual blocker was the checker, and this fix removes it.

**Only these two findings are processed.** The other 24 unread findings wait for the next batch, which is below its threshold of 45.

## What you need to decide

**Is this fix what you said yes to?**

**Problem** — The quote relayed for this cycle, *"Yes.. add the rows to the register. Let improvement agent do it."*, is the same sentence that authorised review (1), and it names register rows, not the work-item checker. Lead-agent reads it as also saying yes to this fix. Nothing in the sentence says so.
**Suggested fix** — Treat your `APPROVE IMPROVEMENTS` on this document as the authorisation. If you did not mean to have the checker changed, say so and I will withdraw the draft.
**What happens if you don't** — Nothing is applied without the keyword, so there is no risk either way. Without it, pm-agent's scoped check on WI-0146 to WI-0148 stays red.
[IMP-1227, log L1223](logs/improvement-log.jsonl#L1223)

---

**Approve this draft?**

**Problem** — Items whose files were renamed can never pass the checker again, even after the correct amendment.
**Suggested fix** — Reply `APPROVE IMPROVEMENTS`. I then apply §A and §B, re-run the selftests and the scoped check, close the blocker and reject the sibling proposal.
**What happens if you don't** — The development gate for WI-0146 to WI-0148 cannot pass without a hand edit of the ledger, which is forbidden.
[fold](.engine/scripts/lib/work_items.py#L940)

---

**After approval: one engine commit for both reviews, then one pointer bump.**

**Problem** — `.engine` will then hold three uncommitted files: review (1)'s flag and this review's two files. All three go in one engine commit and one pointer bump.
**Suggested fix** — Run these commands. They replace the ones handed over with review (1).

```bash
git -C .engine add scripts/verify-code-app-column-bindings.py scripts/lib/work_items.py scripts/verify-work-items.py
git -C .engine commit -m "verify-code-app-column-bindings --released-profile (Revitalise ADR-085 G2); work_items: check the CURRENT source_ref on replay (IMP-1227)"
git -C .engine branch -r --contains HEAD~1        # expect origin/deploy-first-learning-and-item-closure
git -C .engine push origin HEAD:deploy-first-learning-and-item-closure
git -C .engine branch -r --contains HEAD          # MUST list origin/deploy-first-learning-and-item-closure
git add .engine constraints/domain/special-category-register.yml logs/improvement-log.jsonl logs/known-failure-modes.md logs/known-failure-modes-appendix.md docs/improvements/2026-10-22-improvement-review.md docs/improvements/2026-10-22-improvement-review-2.md
git commit -m "Improvement reviews 2026-10-22 (1) and (2): trustee_release register rows; engine pointer bump (--released-profile, current source_ref check)"
git push
```

Do not commit `__pycache__`, and never use `git add -A`. The `logs/` files in this list already hold other agents' uncommitted lines, so committing them also commits those lines. If you do not want that, commit them separately.
**What happens if you don't** — Fresh clones and CI keep pinning `97af189` and run neither fix.
[improvement-agent.md, two repositories](agents/improvement-agent.md#L504)

---

Verification: the engine selftest passes with the fix (and fails on today's library for the new case), and the `work-items.py` selftest passes. The scoped check goes from 3 failures to 0 and the unscoped check from 329 to 326, with 3 lines removed and 0 added. **Not verified:** the full build, and the effect on items other than these three beyond the diff above. Nothing here is above V1.

---

## 1. Regression check — did the last review's changes work?

The last review applied was 2026-10-22 (1), about 40 minutes ago, with a register edit and an engine flag. No finding has been logged in either class since. Two new findings touch the same work: one records that development-agent's gate depended on review (1)'s unapproved draft, and one is the class handled here. Neither is a recurrence. The 2026-10-21 review's audit is unchanged from review (1)'s §1.

| Prior change | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|
| 10-22 (1) rows 1–2, register and `--released-profile` | capability (ADR-085) | NO | Gates green after the apply; too soon to say more |
| 10-21 row 5, `work_items.py` component refusal | `declared-policy-not-mechanically-enforced` | NO, not in this file | This review changes a different function |

---

## 2. Clusters and promotion decisions

```
CLUSTER: work-item-source-ref-dangling-after-rename  (x2: IMP-1227, IMP-1226)
Altitude:   CLASS — any instance whose files are renamed after intake hits it; the fix is in the
            engine's fold, not in this ledger
Ladder row: a script beats a rule — the defect is in the checker, so the checker changes
Becomes:    §A + §B: source_ref existence checked once per item against its current folded value
Retires:    nothing
Cites:      IMP-1227, IMP-1226
Residual:   a done item whose current ref dangles still fails globally (unchanged; not this
            defect). The write path still checks at write time only, so a file deleted after a
            write is caught by the fold check, not refused.
```

**Premises re-measured at draft time.** IMP-1227's root cause was confirmed by running the scoped check: exit 1 with failures at lines 921–923, all on `created` events, and each item's current path exists. IMP-1226's premise that "an amendment after built needs a counted reopen" was disproved: the three items fold with `reopens 0`.

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | script | [.engine/scripts/lib/work_items.py](.engine/scripts/lib/work_items.py#L940), engine only | On replay, check `source_ref` existence once per item against its current folded value, reported at the line that set it; the write path is unchanged (§A) | IMP-1227, IMP-1226 | YES — `python3 .engine/scripts/verify-work-items.py --selftest`; corpus: unscoped 329 → 326 failures, 3 removed (3 of 3 superseded refs to the deleted folder), 0 added | already wired (`work-items`, SOFT `--warn-only`, [build config L182](config/revitalise-grant-automation-build.yml#L182)) |
| 2 | script | [.engine/scripts/verify-work-items.py](.engine/scripts/verify-work-items.py#L135), engine only | 4 selftest cases, one of which fails on today's library (§B) | IMP-1227 | YES — the same selftest | already wired (selftest runs with the step's suite) |

**Constraint budget:** 0 of 3 used. Neither file has an instance copy: `scripts/verify-work-items.py` is a wrapper, and there is no `scripts/lib/`.

**Dispositions, decided now from `observable_at`:**

| Entry | `observable_at` | Disposition |
|---|---|---|
| IMP-1227 (blocker) | n/a | **CLOSE** on apply: `APPLIED`, with `evidence_grep` `{"file": ".engine/scripts/lib/work_items.py", "contains": "def source_ref_problem(src: str, ctx: Context)"}` |
| IMP-1226 | n/a | **REJECTED** on apply, because its premise (a counted reopen) measures false (`reopens 0`) and the defect it names is closed by row 1 |

---

## 4. Retirements

> Retirement check performed: I reviewed the `work-items` selftest set and the `AMEND` rule
> (only `new`, `ready` and `reopened` may change `source_ref`). Neither is made redundant: the
> AMEND rule still forces a reopen to change a built item's ref, and this fix leaves that route
> intact. Nothing is retired.

---

## 5. Findings left unprocessed

**Deferred:** IMP-1206, IMP-1207, IMP-1208, IMP-1209, IMP-1210, IMP-1211, IMP-1212, IMP-1213, IMP-1214, IMP-1215, IMP-1216, IMP-1217, IMP-1218, IMP-1219, IMP-1220, IMP-1221, IMP-1222, IMP-1223, IMP-1224, IMP-1225, IMP-1228, IMP-1229

| Finding | Why deferred | Revisit when |
|---|---|---|
| all of the above | a scoped review; 24 unread, below the batch threshold of 45 | the next post-deploy batch, or the threshold |

---

## 6. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 1225 | 1225 |
| Entries closed | — | 2 (1 APPLIED, 1 REJECTED) |
| Digest | regenerated on apply | |

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-10-22-improvement-review-2.md

Findings processed: 2 NEW  →  1 cluster
Regression check:   2 prior changes audited, 0 classes recurred
Proposed:           0 constraints (cap 3), 2 gates/scripts, 0 skill/knowledge edits,
                    0 agent-file edits, 0 retirements
Altitude calls:     1 generalised from instance to class, 0 left as notes
Digest:             will regenerate — 1 blocker closed, 1 proposal rejected

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. On approval

The applied record is written here **after** `APPROVE IMPROVEMENTS`, not before. Apply order:
(1) Set the status to `APPLYING`. (2) Confirm the engine files still have sha1 `36c6799…` (lib) and `79fe7eb…` (verifier), and merge if they have moved. (3) Apply §A and §B. (4) Run both selftests, the scoped check and the unscoped diff. (5) Close IMP-1227 and reject IMP-1226, one line edit each. (6) Regenerate the digest, then run `verify-improvement-log.py --check`, `verify-derived-counts.py` and `verify-review-document.py`.

---

### Applied record — 2026-10-22

**Approval:** *"Approve improvements"*, typed by Xander Lykopoulos after he had seen this draft, and relayed verbatim by lead-agent. This keyword is the authorisation for this fix. The earlier register-rows quote was not used.

**Re-verified before applying:** the Status line was still DRAFT. Neither engine file had changed since the draft: the library was still `36c6799…` and the verifier still `79fe7eb…`. There were no `corrects` warnings. Nothing was withheld or narrowed.

| # | Change | Applied at | Entries moved |
|---|---|---|---|
| 1 | §A `lib/work_items.py`; matches the approved diff line for line | `.engine` working tree 2026-10-22 15:24; **not committed** | IMP-1227 → APPLIED (`evidence_grep` matches 1 line) |
| 2 | §B `verify-work-items.py` selftest cases; matches the approved diff line for line | `.engine` working tree 2026-10-22 15:24; **not committed** | — |

Rejected: IMP-1226 → REJECTED. Its premise was a counted reopen, but the three items fold with `reopens 0`.

**Checks after applying (development-agent is still live in this tree):**

| Check | Exit | Result |
|---|---|---|
| `python3 scripts/verify-work-items.py --selftest` | 0 | 0 FAIL lines, including the 4 new cases |
| `python3 scripts/work-items.py --selftest` | 0 | |
| `verify-work-items.py --check --scope WI-0146,WI-0147,WI-0148 --at-least built` | 0 | 0 failures. It was 3 `[REF]` before |
| `verify-work-items.py --check` (unscoped, the warn-only build step) | 1 | 326 failures, identical to the draft-time measurement. These are older drift in other items |
| `verify-improvement-log.py --check` | 0 | governance blockers open: 0 |
| digest | regenerated | 1225 entries, 1201 distinct lessons; `--check` current |
| `verify-engine-instance-split.py` | 0 | |
| `verify-derived-counts.py` (SOFT) | WARN | the same 3 drifts as before this review, none from it |

## §A — `.engine/scripts/lib/work_items.py` (proposed)

```diff
--- a/.engine/scripts/lib/work_items.py
+++ b/.engine/scripts/lib/work_items.py
@@ -410,6 +410,7 @@
     history: list[dict] = field(default_factory=list)
     evidence_since_reopen: list[tuple[int, dict]] = field(default_factory=list)
     legacy_uses: int = 0
+    source_ref_line: int | None = None   # the ledger line that set the CURRENT source_ref (IMP-1227)
 
     def to_json(self) -> dict:
         return {k: getattr(self, k) for k in (
@@ -531,8 +532,25 @@
     return it.type if it else None
 
 
+def source_ref_problem(src: str, ctx: Context) -> str | None:
+    """Why a source_ref does not resolve on disk, or None when it does."""
+    path = re.split(r"[#!]", src, maxsplit=1)[0]
+    if not path or not (ctx.root / path).exists():
+        return f"source_ref {src!r}: {path!r} does not exist"
+    return None
+
+
 def ref_problems(ev: dict, item_type: str, items: dict[str, Item], ctx: Context,
-                 self_id: str) -> list[tuple[str, str]]:
+                 self_id: str, check_source: bool = True) -> list[tuple[str, str]]:
+    """Reference problems of one event.
+
+    `check_source=False` is the REPLAY form used by fold(): a source_ref's existence is a fact
+    about the filesystem NOW, so on replay it is checked once per item against the item's
+    CURRENT source_ref (fold's last step), never against every superseded created/link event.
+    Checking history made an append-only ledger unable to clear a ref whose file was later
+    renamed, even after the amendment route succeeded (IMP-1227). The write path keeps
+    check_source=True: a new event naming a missing file is refused.
+    """
     p: list[tuple[str, str]] = []
     parent = ev.get("parent")
     if isinstance(parent, str):
@@ -565,22 +583,25 @@
     if isinstance(co, str) and CO_RE.match(co) and co not in ctx.change_orders:
         p.append(("REF", f"change_order {co} has no file under change-orders/"))
     src = ev.get("source_ref")
-    if isinstance(src, str):
-        path = re.split(r"[#!]", src, maxsplit=1)[0]
-        if not path or not (ctx.root / path).exists():
-            p.append(("REF", f"source_ref {src!r}: {path!r} does not exist"))
+    if check_source and isinstance(src, str):
+        problem = source_ref_problem(src, ctx)
+        if problem:
+            p.append(("REF", problem))
     return p
 
 
-def structural_problems(ev: dict, items: dict[str, Item], ctx: Context) -> list[tuple[str, str]]:
-    """Everything decidable from the event and the folded state — no evidence resolution."""
+def structural_problems(ev: dict, items: dict[str, Item], ctx: Context,
+                        check_source: bool = True) -> list[tuple[str, str]]:
+    """Everything decidable from the event and the folded state — no evidence resolution.
+
+    fold() passes check_source=False and checks each item's current source_ref itself."""
     e, iid = ev["event"], ev["id"]
     item = items.get(iid)
     p: list[tuple[str, str]] = []
     if e == "created":
         if item is not None:
             return [("ID", f"{iid} is already created at line {item.line}")]
-        return ref_problems(ev, ev["type"], items, ctx, iid)
+        return ref_problems(ev, ev["type"], items, ctx, iid, check_source)
     if item is None:
         return [("ID", f"{e} names {iid}, which was not created earlier in the ledger")]
 
@@ -592,7 +613,7 @@
             p.append(("AMEND", f"{iid}: a retrace is pending (back to '{item.retrace_from}'); an "
                                f"acceptance relink is a rejection, so reopen it without --retrace "
                                f"(IMP-1004)"))
-        p += ref_problems(ev, item.type, items, ctx, iid)
+        p += ref_problems(ev, item.type, items, ctx, iid, check_source)
         return p
 
     if e == "defer":
@@ -885,7 +906,8 @@
                   parent=ev.get("parent"), external_id=ev.get("external_id"),
                   source_ref=ev.get("source_ref"), acceptance=list(ev.get("acceptance", [])),
                   wbs=list(ev.get("wbs", [])), change_order=ev.get("change_order"),
-                  components=list(ev.get("components", [])))
+                  components=list(ev.get("components", [])),
+                  source_ref_line=line if ev.get("source_ref") is not None else None)
         it.history.append(summary)
         items[iid] = it
         return
@@ -894,6 +916,8 @@
         for k in ("parent", "external_id", "source_ref", "change_order", "title"):
             if k in ev:
                 setattr(it, k, ev[k])
+        if "source_ref" in ev:
+            it.source_ref_line = line
         for k in ("acceptance", "wbs", "components"):
             if k in ev:
                 setattr(it, k, list(ev[k]))
@@ -951,12 +975,20 @@
         if any(c == "SCHEMA" for c, _ in sp):
             problems += [(line, c, m) for c, m in sp]
             continue
-        st = structural_problems(ev, items, ctx)
+        st = structural_problems(ev, items, ctx, check_source=False)
         bad = sp + st
         problems += [(line, c, m) for c, m in bad]
         if any(c in ("ID", "FOLD") for c, _ in st):
             continue
         apply(ev, items, line)
+    # source_ref existence, once per item, against its CURRENT folded value (IMP-1227). Still
+    # fail-closed: an item whose current ref dangles is a REF failure at the line that set it.
+    for it in items.values():
+        if isinstance(it.source_ref, str):
+            problem = source_ref_problem(it.source_ref, ctx)
+            if problem:
+                problems.append((it.source_ref_line or it.line, "REF",
+                                 f"{it.id}: current {problem}"))
     return FoldResult(items, problems, n)
 
 
```

## §B — `.engine/scripts/verify-work-items.py` (proposed)

```diff
--- a/.engine/scripts/verify-work-items.py
+++ b/.engine/scripts/verify-work-items.py
@@ -195,6 +195,21 @@
               [ev("WI-0001", "created", type="feature", title="f"),
                ev("WI-0002", "created", type="task", title="t", parent="WI-0001")], "REF")
         fails("REF: source_ref path missing", [created | {"source_ref": "docs/nope.md#L1"}], "REF")
+        # REF on replay checks the CURRENT source_ref, not superseded events (IMP-1227)
+        gone = root / "docs" / "gone.md"
+        gone.write_text("x\n")
+        relinked = [created | {"source_ref": "docs/gone.md#L1"},
+                    ev("WI-0001", "link", source_ref="docs/feedback.md#L1")]
+        gone.unlink()
+        checks, _ = run(relinked)
+        check("REF: a superseded source_ref whose file was later deleted does not fail", checks, [])
+        fails("REF: a CURRENT source_ref whose file was later deleted still fails",
+              [created, ev("WI-0001", "link", source_ref="docs/gone.md#L1")], "REF")
+        fails("REF: relinked back onto a deleted file still fails",
+              relinked + [ev("WI-0001", "link", source_ref="docs/gone.md#L1")], "REF")
+        checks, r = run([created, ev("WI-0001", "link", source_ref="docs/gone.md#L1")])
+        check("REF: the dangling current ref is reported at the line that set it",
+              [f["line"] for f in r["failures"] if f["check"] == "REF"], [2])
         checks, _ = run([created | {"parent": "co:CO-001"}])
         check("REF: change order parent resolves", checks, [])
         # FOLD
```
