#!/usr/bin/env python3
"""Enumerate every disagreement between the contractual baseline and this repository.

WHY THIS EXISTS
---------------
PM-R04. Four separate documents are jointly the Agreed Specification under Build Terms B1 — the
Automation Solution Design, the Solution Architecture, the WBS, and the phase acceptance record —
and *"where these conflict, the most recently accepted version prevails"*. A conflict between
them is therefore a live ambiguity about what was bought, not a filing error. Unresolved drift is
reported at every PM gate rather than silently carried.

WHAT IT REPORTS
---------------
  1. total reconciliation      agreement hours against the corrected WBS band
  2. the known WBS gap         20 h DocuSign selection/trial, and whether v0.6 has landed
  3. stale restated figures    any hour figure in docs/ that disagrees with the baseline
  4. D-3 compliance            any fee or rate figure anywhere in the repository
  5. claim vs evidence         overclaims and underclaims from logs/state/wbs-state.json
  6. blocked computations      what D-4's missing clause text stops any gate from computing

This script REPORTS. It does not gate — `verify-wbs-chain.py` does. Exit 0 unless an input is
missing, so drift is always visible rather than blocking work that has to continue anyway.

Run:
    python3 scripts/report-baseline-drift.py            # write logs/state/baseline-drift.md
    python3 scripts/report-baseline-drift.py --stdout
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SA = Path("contract/service-agreement.json")
WBS = Path("contract/wbs.json")
STATE = Path("logs/state/wbs-state.json")
OUT = Path("logs/state/baseline-drift.md")
PLAN = Path("docs/plans/revitalise-grant-automation-plan.md")


def _grep(pattern: str, *paths: str) -> list[tuple[str, str]]:
    """Ripgrep-free recursive grep returning (file:line, text)."""
    try:
        r = subprocess.run(["grep", "-rnoE", pattern, *paths],
                           capture_output=True, text=True, check=False)
    except OSError:
        return []
    out = []
    for line in r.stdout.splitlines():
        parts = line.split(":", 2)
        if len(parts) == 3:
            out.append((f"{parts[0]}:{parts[1]}", parts[2]))
    return out


def build() -> tuple[str, dict]:
    for p in (SA, WBS):
        if not p.exists():
            print(f"report-baseline-drift: missing {p} — run scripts/import-baseline.py",
                  file=sys.stderr)
            raise SystemExit(2)
    sa = json.loads(SA.read_text(encoding="utf-8"))
    wbs = json.loads(WBS.read_text(encoding="utf-8"))
    state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else None

    rec = sa["reconciliation_with_wbs"]
    gap = wbs["known_gap"]
    # Which WBS revisions are physically present in docs/Import/, and which one the committed
    # baseline is actually pinned to. These are two different questions and the gap between them
    # is the thing worth reporting: a newer accepted source sitting unimported beside an older
    # pinned one is invisible to import-baseline.py --check, which knows only the filename it was
    # given (IMP-0714).
    present = sorted(p.name for p in Path("docs/Import").glob("*WBS*v?.?*.xlsx")
                     if not p.name.startswith("~$"))
    pinned_version = wbs.get("source", {}).get("version")
    newest_present = present[-1] if present else None
    baseline_is_newest = bool(newest_present and pinned_version
                              and pinned_version in newest_present)

    # 3. hour figures restated in docs that disagree with the baseline
    stale = []
    if PLAN.exists():
        txt = PLAN.read_text(encoding="utf-8")
        for m in re.finditer(r"(\d{2,3})\s*[–-]\s*(\d{2,3})\s*(?:build\s+)?hours", txt):
            lo, hi = int(m.group(1)), int(m.group(2))
            if (lo, hi) not in {(int(wbs["totals"]["low"]), int(wbs["totals"]["high"])),
                                (int(wbs["corrected_totals_with_known_gap"]["low"]),
                                 int(wbs["corrected_totals_with_known_gap"]["high"]))}:
                line = txt[:m.start()].count("\n") + 1
                stale.append((f"{PLAN}:{line}", f"{lo}–{hi} hours"))

    # 4. D-3: any fee or rate figure in the repository
    money = [(loc, t) for loc, t in _grep(r"€ ?[0-9][0-9,\.]*", "docs", "contract", "agents",
                                          "skills", "constraints", "templates", "config")
             if "redacted" not in t]

    # 5. claim vs evidence
    over = [d for d in (state or {}).get("disagreements", []) if d["verdict"] == "OVERCLAIM"]
    under = [d for d in (state or {}).get("disagreements", []) if d["verdict"] == "UNDERCLAIM"]

    L = ["# Baseline drift", "",
         "**GENERATED — do not hand-edit.** `python3 scripts/report-baseline-drift.py`", "",
         "Build Terms B1 makes the Solution Design, the Solution Architecture, the WBS and the "
         "phase acceptance record jointly the Agreed Specification, and the most recently accepted "
         "version prevails. A disagreement between them is an open question about scope.", "",
         "## 1. Total reconciliation", "",
         f"| | Hours |", "|---|---|",
         f"| Agreement (read from the signed PDF, verified two ways) | **{sa['total_hours']}** |",
         f"| WBS v0.5 as accepted | {wbs['totals']['low']:.0f}–{wbs['totals']['high']:.0f} |",
         f"| WBS corrected for the known gap | {rec['wbs_corrected']['low']:.0f}–"
         f"{rec['wbs_corrected']['high']:.0f} |",
         f"| Verdict | **{rec['verdict']}** |", "",
         "The agreement groups WBS work many-to-one by design (D-1/D-2), so a per-phase comparison "
         "is meaningless and is deliberately not made here.", "",
         "## 2. Which WBS revision this baseline is pinned to", "",
         # Rendered UNCONDITIONALLY. This used to sit in the else-branch of a ternary whose
         # condition was gap['resolution'] — so setting that field on 2026-08-19 (an unrelated
         # decision about DocuSign hours) silently stopped this line being emitted for 22 days,
         # during which a client-accepted v0.6 arrived and the report said nothing (IMP-0714).
         # Two independent facts must never share one conditional.
         f"- Baseline is pinned to: **{pinned_version or 'UNKNOWN'}**",
         f"- Present in `docs/Import/`: {', '.join(f'`{p}`' for p in present) or 'none found'}",
         (f"- **The pinned revision is the newest present.**" if baseline_is_newest else
          f"- **⚠ A NEWER WBS REVISION IS PRESENT AND NOT IMPORTED — `{newest_present}` against a "
          f"baseline pinned to {pinned_version}.** This is a BASELINE INTAKE, gated on "
          f"`APPROVE BASELINE` (agents/pm-agent.md). Note that "
          f"`scripts/import-baseline.py --check` will keep reporting the baseline as current "
          f"regardless: it reads the one filename it is given and cannot see a newer source "
          f"arrive (IMP-0714)."), "",
         "## 2b. The known WBS gap", "",
         f"- **{gap['hours']} h — {gap['scope']}** (automation #{gap['belongs_to_automation']}, "
         f"{gap['phase']}, `{gap['finding']}`)",
         f"- Action: {gap['action']}",
         f"- **Resolution: {gap['resolution']}** — {gap.get('consequence','')[:200]}", "",
         "## 3. Hour figures restated in documents", ""]
    if stale:
        L += ["A document that restates a baseline figure goes stale silently and is inherited "
              "downstream (`IMP-0029`). These disagree with the baseline:", "",
              "| Where | Says |", "|---|---|"]
        L += [f"| `{loc}` | {t} |" for loc, t in stale]
    else:
        L.append("None. No document restates a total that disagrees with the baseline.")
    L += ["", "## 4. D-3 compliance — fee and rate figures", ""]
    if money:
        L += ["D-3: *\"Hours for the baseline is perfect\"* — no fee figure or hourly rate in this "
              "repository. These remain:", "", "| Where | Figure |", "|---|---|"]
        L += [f"| `{loc}` | {t} |" for loc, t in money[:40]]
        if len(money) > 40:
            L.append(f"| … | {len(money) - 40} more |")
    else:
        L.append("Clean. No fee or rate figure appears in the checked paths.")
    L += ["", "## 5. Claimed status against evidence", ""]
    if state is None:
        L.append("`logs/state/wbs-state.json` absent — run `scripts/derive-wbs-state.py`.")
    else:
        L += [f"- **{len(over)} overclaim(s)** — a task marked complete whose deliverable is "
              f"partly or wholly absent",
              f"- **{len(under)} underclaim(s)** — a deliverable that exists against a blank status",
              f"- {len(state['tasks_without_a_rule'])} task(s) with no evidence rule", ""]
        for d in over:
            L.append(f"  - **OVERCLAIM `{d['id']}`** {d['task']} — missing: "
                     + "; ".join(d["missing"]))
        for d in under:
            L.append(f"  - UNDERCLAIM `{d['id']}` {d['task']}")
    w = sa["warranty"]
    L += ["", "## 6. Computations blocked by missing inputs", "",
          f"- **Warranty / hypercare / liability caps: {w['status']}**"
          + (f" — {w['reason']}" if w.get("reason") else
             " — clause text present; acceptance has three routes (written · ten business days' "
             "silence after submission · live operational use) and the earliest wins (B5)"), ""]
    if w.get("open_issue"):
        L += [f"- **Open:** {w['open_issue']}", ""]
    return "\n".join(L) + "\n", {
        "reconciled": rec["agreement_total_inside_corrected_band"],
        "pinned_version": pinned_version, "sources_present": present,
        "baseline_is_newest": baseline_is_newest,
        "stale_figures": len(stale), "money_figures": len(money),
        "overclaims": len(over), "underclaims": len(under),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stdout", action="store_true")
    args = ap.parse_args(argv)
    md, summary = build()
    if args.stdout:
        print(md)
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(md, encoding="utf-8")
    print(f"report-baseline-drift: wrote {OUT} — "
          f"reconciled={summary['reconciled']}, "
          f"WBS pinned={summary['pinned_version']}"
          f"{'' if summary['baseline_is_newest'] else ' (STALE — NEWER SOURCE PRESENT)'}, "
          f"stale figures={summary['stale_figures']}, fee/rate figures={summary['money_figures']}, "
          f"overclaims={summary['overclaims']}, underclaims={summary['underclaims']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
