#!/usr/bin/env python3
"""Derive each WBS task's state from repository evidence, and compare it to the claimed Status.

WHY THIS EXISTS
---------------
`IMP-0030`. WBS v0.5 task `0.4` is marked `Status: Done`. Its own description names seven
Dataverse tables plus an Anonymised Statistic snapshot; the solution contained four. Task `1.2`
was blank while its deliverable — the form specification brief — sat in `docs/development/`. The
Status column is typed by a human into a workbook the repository has never read, so the claim and
the artefacts drift in both directions and nothing notices.

This is `exit-zero-does-not-mean-created` (x4) in a spreadsheet: *marked Done* is a claim, and
this project has learned four times that a claim of creation must be verified by looking for the
thing. So state is DERIVED here, and the hand-typed value is preserved as `claimed_status` and
compared — never overwritten, because the human's claim is evidence too and a disagreement is the
finding.

Under Build Terms B1 the WBS is part of the Agreed Specification (D-5), so a false completion
claim in it is a contractual statement, not a bookkeeping slip.

NO SILENT CAPS. Tasks with no rule in `contract/evidence-map.json` derive as `unknown` and are
counted and named. A task can never derive as `complete` from an absent rule.

Run:
    python3 scripts/derive-wbs-state.py            # write logs/state/wbs-state.json + .md
    python3 scripts/derive-wbs-state.py --check    # exit 1 if the written state is stale (CI)
    python3 scripts/derive-wbs-state.py --stdout   # print the markdown report

Exit 0 clean, 1 stale, 2 usage/missing input. Disagreements do NOT fail the run — they are the
output. Use `verify-wbs-chain.py` for the gate.
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from pathlib import Path

WBS = Path("contract/wbs.json")
MAP = Path("contract/evidence-map.json")
OUT_JSON = Path("logs/state/wbs-state.json")
OUT_MD = Path("logs/state/wbs-state.md")
SOLUTION_GLOB = "src/solutions/*"

CLAIM_COMPLETE = {"done"}
CLAIM_PARTIAL = {"partially done", "in progress"}


def check_rule(rule: dict) -> tuple[bool | None, str]:
    kind = rule.get("kind")
    if kind == "manual":
        return None, f"manual — {rule.get('reason', 'no reason given')}"
    if kind == "entity":
        hits = glob.glob(f"{SOLUTION_GLOB}/Entities/{rule['value']}")
        return bool(hits), f"entity {rule['value']}: " + ("present" if hits else "ABSENT")
    if kind == "workflow":
        hits = [p for p in glob.glob(f"{SOLUTION_GLOB}/Workflows/{rule['value']}*.json")
                if not p.endswith(".data.xml")]
        return bool(hits), f"workflow {rule['value']}: " + ("present" if hits else "ABSENT")
    if kind == "path":
        hits = glob.glob(rule["value"])
        return bool(hits), f"path {rule['value']}: " + ("present" if hits else "ABSENT")
    if kind == "grep":
        files = glob.glob(rule["file"])
        if not files:
            return False, f"grep {rule['pattern']}: target {rule['file']} ABSENT"
        pat = re.compile(rule["pattern"])
        for f in files:
            try:
                if pat.search(Path(f).read_text(encoding="utf-8", errors="replace")):
                    return True, f"grep {rule['pattern']}: matched in {f}"
            except OSError:
                continue
        return False, f"grep {rule['pattern']}: no match in {len(files)} file(s)"
    return None, f"unknown rule kind {kind!r}"


def derive() -> dict:
    for p in (WBS, MAP):
        if not p.exists():
            print(f"derive-wbs-state: missing {p} — run scripts/import-baseline.py first",
                  file=sys.stderr)
            raise SystemExit(2)
    wbs = json.loads(WBS.read_text(encoding="utf-8"))
    rules = json.loads(MAP.read_text(encoding="utf-8"))["rules"]

    tasks_out, no_rule, disagreements = [], [], []
    for t in wbs["tasks"]:
        tid = t["id"]
        rs = rules.get(tid)
        evidence, present, absent, manual = [], 0, 0, 0
        if not rs:
            no_rule.append(tid)
            derived = "unknown"
        else:
            for r in rs:
                ok, note = check_rule(r)
                evidence.append({"rule": r, "ok": ok, "note": note})
                if ok is None:
                    manual += 1
                elif ok:
                    present += 1
                else:
                    absent += 1
            checkable = present + absent
            if checkable == 0:
                derived = "manual_only"
            elif absent == 0:
                derived = "complete" if manual == 0 else "complete_pending_manual"
            elif present == 0:
                derived = "not_started"
            else:
                derived = "partial"

        claim = (t.get("claimed_status") or "").strip().lower()
        claim_norm = ("complete" if claim in CLAIM_COMPLETE
                      else "partial" if claim in CLAIM_PARTIAL
                      else "none" if not claim else claim)

        verdict = "agrees"
        if claim_norm == "complete" and derived in {"partial", "not_started"}:
            verdict = "OVERCLAIM"
        elif claim_norm == "none" and derived in {"complete", "complete_pending_manual", "partial"}:
            verdict = "UNDERCLAIM"
        elif claim_norm == "complete" and derived in {"unknown", "manual_only"}:
            verdict = "unverifiable"
        if verdict in {"OVERCLAIM", "UNDERCLAIM"}:
            disagreements.append({
                "id": tid, "task": t["task"], "phase": t["phase"],
                "claimed": t.get("claimed_status"), "derived": derived, "verdict": verdict,
                "missing": [e["note"] for e in evidence if e["ok"] is False],
                "found": [e["note"] for e in evidence if e["ok"] is True],
            })

        tasks_out.append({
            "id": tid, "phase": t["phase"], "automation": t["automation"], "task": t["task"],
            "deliverable": t["deliverable"],
            "hours_low": t["hours_low"], "hours_high": t["hours_high"],
            "depends_on": t["depends_on"],
            "claimed_status": t.get("claimed_status"), "derived_status": derived,
            "verdict": verdict,
            "evidence_present": present, "evidence_absent": absent, "evidence_manual": manual,
            "evidence": evidence,
        })

    counts: dict[str, int] = {}
    for t in tasks_out:
        counts[t["derived_status"]] = counts.get(t["derived_status"], 0) + 1

    return {
        "_generated_by": "scripts/derive-wbs-state.py — do not hand-edit",
        "_source_of_truth": "The WBS Status column is a CLAIM. derived_status is evidence.",
        "baseline": {"file": str(WBS), "version": wbs["source"]["version"],
                     "tasks": wbs["totals"]["tasks"]},
        "derived_counts": counts,
        "tasks_without_a_rule": no_rule,
        "disagreements": disagreements,
        "tasks": tasks_out,
    }


def render_md(st: dict) -> str:
    L = ["# WBS state — derived from repository evidence", "",
         "**GENERATED — do not hand-edit.** `python3 scripts/derive-wbs-state.py`", "",
         f"Baseline: `{st['baseline']['file']}` {st['baseline']['version']} · "
         f"{st['baseline']['tasks']} tasks", "",
         "The WBS `Status` column is a **claim**. `derived` is what the repository actually "
         "contains. A disagreement is the finding — see `IMP-0030`.", "",
         "## Derived counts", "", "| Derived state | Tasks |", "|---|---|"]
    for k, v in sorted(st["derived_counts"].items(), key=lambda kv: -kv[1]):
        L.append(f"| `{k}` | {v} |")
    L += ["", "## Disagreements between the claim and the evidence", ""]
    if not st["disagreements"]:
        L.append("None. Every claimed status matches the evidence.")
    else:
        L += ["| Task | Phase | Claimed | Derived | Verdict | What is missing |",
              "|---|---|---|---|---|---|"]
        for d in st["disagreements"]:
            miss = "; ".join(d["missing"]) or "—"
            L.append(f"| `{d['id']}` {d['task'][:38]} | {d['phase']} | "
                     f"{d['claimed'] or '(blank)'} | `{d['derived']}` | **{d['verdict']}** | "
                     f"{miss[:150]} |")
    if st["tasks_without_a_rule"]:
        L += ["", "## Tasks with no evidence rule", "",
              "Counted and named rather than assumed complete. Add a rule to "
              "`contract/evidence-map.json`.", "",
              "`" + "`, `".join(st["tasks_without_a_rule"]) + "`"]
    L.append("")
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--stdout", action="store_true")
    args = ap.parse_args(argv)

    st = derive()
    js = json.dumps(st, indent=2, ensure_ascii=False) + "\n"
    md = render_md(st)

    if args.stdout:
        print(md)
        return 0
    if args.check:
        stale = [p for p, txt in ((OUT_JSON, js), (OUT_MD, md))
                 if not p.exists() or p.read_text(encoding="utf-8") != txt]
        if stale:
            print("derive-wbs-state: STALE: " + ", ".join(str(s) for s in stale)
                  + "\n  Run: python3 scripts/derive-wbs-state.py", file=sys.stderr)
            return 1
        print("derive-wbs-state: state is current.")
        return 0

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(js, encoding="utf-8")
    OUT_MD.write_text(md, encoding="utf-8")
    d = st["disagreements"]
    over = sum(1 for x in d if x["verdict"] == "OVERCLAIM")
    under = sum(1 for x in d if x["verdict"] == "UNDERCLAIM")
    print(f"derive-wbs-state: wrote {OUT_JSON} and {OUT_MD} — "
          f"{st['baseline']['tasks']} tasks, {len(d)} disagreement(s) "
          f"({over} overclaim, {under} underclaim), "
          f"{len(st['tasks_without_a_rule'])} without a rule.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
