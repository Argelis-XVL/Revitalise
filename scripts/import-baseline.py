#!/usr/bin/env python3
"""Generate the committed commercial baseline from the two contractual source documents.

WHY THIS EXISTS
---------------
`IMP-0029`: `docs/plans/revitalise-grant-automation-plan.md` §10 — an APPROVED document — stated
106–160 hours over 7 automations. The accepted WBS carries 177–277 over 9, and the signed
agreement 292. A figure transcribed into a repo document goes stale silently and is inherited by
everything downstream. So no document restates the baseline: this script derives it, and
everything else cites the derived file.

`IMP-0063`: the agreement's total was recorded as UNVERIFIED because no PDF extractor was
available. `scripts/lib/pmsources.py` reads it via each font's /ToUnicode CMap. This script
verifies 292 two independent ways — the sum of the five phase rows, and the stated total over the
stated rate — and fails if they disagree.

D-3 (`docs/Import/baseline-lock.yml`): HOURS ONLY. No fee figure and no hourly rate is written to
any file here. The rate is read transiently to cross-check the total and is then discarded.

D-1/D-2: the agreement groups WBS work many-to-one and *"that is not one on one"*. This script
therefore never compares an agreement phase against a WBS phase. It reconciles the TOTAL, and
maps each agreement phase to the WBS **automations** it covers, which is the join that holds.

OUTPUTS
-------
    contract/wbs.json                 the 61 tasks, hours, dependencies, deliverables
    contract/service-agreement.json   phase hours + milestone dates read from the signed PDF
    contract/source-lock.json         sha256 + size of every source, for staleness detection

Run:
    python3 scripts/import-baseline.py            # write
    python3 scripts/import-baseline.py --check    # exit 1 if any output is stale (CI)
    python3 scripts/import-baseline.py --stdout    # print, do not write

Exits 0 clean, 1 stale/inconsistent, 2 usage or missing source. Fails — never passes — when a
source is absent, so it cannot report OK over nothing (IMP-0007).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
import pmsources as P  # noqa: E402

WBS_SRC = Path("docs/Import/Revitalise-WBS-Grant-Automation-v0.5.xlsx")
SA_SRC = Path("docs/Import/Revitalise - Service Agreement - Application Process Automation - "
              "v1.3 (Signed).pdf")
OUT_WBS = Path("contract/wbs.json")
OUT_SA = Path("contract/service-agreement.json")
OUT_LOCK = Path("contract/source-lock.json")

# Agreement phase -> WBS automations. Read from the agreement's own milestone descriptions
# ("Acceptance letters and form validation live" = #3 + #1). Encoded here because it is the
# many-to-one mapping D-1/D-2 established, and it is the only legitimate join between the two
# documents. #8 sits under Completion: it is in the accepted specification (D-5) and the
# agreement's Phase 4 milestone is "final deliverables accepted".
PHASE_TO_AUTOMATIONS = {
    "phase_0": ["0"],
    "phase_1": ["3", "1"],
    "phase_2": ["4", "2"],
    "phase_3": ["5", "6"],
    "phase_4": ["7", "8"],
}

# D-6: WBS v0.5 omits 20 hours for selecting and trialling DocuSign (IMP-0064). Recorded as a
# known gap against automation #3, NOT added to v0.5 — amending an accepted specification is a
# re-approval, not an edit.
KNOWN_GAP = {
    "hours": 20,
    "scope": "Selecting and trialling the DocuSign platform",
    "belongs_to_automation": "3",
    "phase": "phase_1",
    "finding": "IMP-0064",
    "action": "Issue WBS v0.6 carrying this task; do not edit v0.5.",
}


def build() -> dict[Path, str]:
    for src in (WBS_SRC, SA_SRC):
        if not src.exists():
            print(f"import-baseline: source missing: {src}", file=sys.stderr)
            raise SystemExit(2)

    wbs = P.read_wbs(WBS_SRC)
    tasks = wbs["tasks"]
    if not tasks:
        print("import-baseline: the WBS parsed to zero tasks", file=sys.stderr)
        raise SystemExit(2)

    def agg(rows):
        return {"low": round(sum(t["hours_low"] or 0 for t in rows), 2),
                "high": round(sum(t["hours_high"] or 0 for t in rows), 2),
                "tasks": len(rows)}

    # External blockers, read from the workbook's own Summary sheet rather than hand-authored:
    # "DocuSign licence", "Alex (webhook config)", "DPO sign-off" are client-side dependencies and
    # the ready set must surface them separately from work we can simply start.
    summary_deps = {row["automation"]: row.get("dependencies", [])
                    for row in wbs["summary"] if row.get("automation")}
    summary_saved = {row["automation"]: row.get("annual_hours_saved")
                     for row in wbs["summary"] if row.get("automation")}

    by_phase, by_auto = {}, {}
    for t in tasks:
        by_phase.setdefault(t["phase"] or "(unset)", []).append(t)
        by_auto.setdefault(t["automation"] or "(unset)", []).append(t)

    wbs_doc = {
        "_generated_by": "scripts/import-baseline.py — do not hand-edit",
        "_units": "hours; D-3 forbids any fee or rate figure in this repository",
        "source": {"file": str(WBS_SRC), "version": "v0.5",
                   "accepted_by_client": True, "accepted_ref": "D-5, docs/Import/baseline-lock.yml"},
        "totals": agg(tasks),
        "per_phase": {k: agg(v) for k, v in sorted(by_phase.items())},
        "per_automation": {k: dict(agg(v), name=v[0]["automation_name"],
                                   external_dependencies=summary_deps.get(k, []),
                                   annual_hours_saved=summary_saved.get(k))
                           for k, v in sorted(by_auto.items(), key=lambda kv: (len(kv[0]), kv[0]))},
        "known_gap": KNOWN_GAP,
        "corrected_totals_with_known_gap": {
            "low": round(agg(tasks)["low"] + KNOWN_GAP["hours"], 2),
            "high": round(agg(tasks)["high"] + KNOWN_GAP["hours"], 2),
            "note": "The band the agreement's 292 must fall inside (IMP-0064).",
        },
        "tasks": tasks,
    }

    sa_text = P.read_pdf_text(SA_SRC)
    hours = P.find_hours_in_agreement(sa_text)
    miles = P.find_milestones_in_agreement(sa_text)

    if not hours["agree"]:
        print("import-baseline: the agreement's total does not reconcile two ways "
              f"(phase rows={hours['total_from_phase_rows']}, "
              f"amount/rate={hours['total_from_amount_over_rate']}). "
              "Do not publish a contracted total until this agrees.", file=sys.stderr)
        raise SystemExit(1)

    total = hours["total_from_phase_rows"]
    corrected = wbs_doc["corrected_totals_with_known_gap"]
    inside = corrected["low"] <= total <= corrected["high"]

    sa_doc = {
        "_generated_by": "scripts/import-baseline.py — do not hand-edit",
        "_units": "hours and dates only; D-3 forbids any fee or rate figure in this repository",
        "source": {"file": str(SA_SRC), "version": "v1.3", "signed": True},
        "basis": "time_and_materials",
        "invoicing": {"cadence": "monthly_in_arrears", "payment_terms_days": 14},
        "total_hours": total,
        "total_hours_verification": {
            "method_a": "sum of the five phase hour rows in §03",
            "method_b": "stated total excl. VAT divided by the stated hourly rate",
            "both_agree": True,
            "value": total,
            "closes": "IMP-0063",
            "note": "Read from the signed PDF via /ToUnicode CMap decode, not transcribed. "
                    "The rate and the amounts were read transiently and are not stored (D-3).",
        },
        "phase_hours": hours["phases"],
        "phase_to_wbs_automations": PHASE_TO_AUTOMATIONS,
        "phase_mapping_note": "Many-to-one BY DESIGN (D-1/D-2). Never compare an agreement phase "
                              "against a WBS phase of the same number — reconcile the TOTAL, and "
                              "join via automations.",
        "milestones": miles,
        "reconciliation_with_wbs": {
            "wbs_v05": {"low": wbs_doc["totals"]["low"], "high": wbs_doc["totals"]["high"]},
            "wbs_corrected": {"low": corrected["low"], "high": corrected["high"]},
            "agreement_total": total,
            "agreement_total_inside_corrected_band": inside,
            "verdict": ("RECONCILED — the agreement total falls inside the corrected WBS band"
                        if inside else
                        "UNRECONCILED — investigate what work is missing from the breakdown "
                        "before concluding the documents disagree (IMP-0064)"),
        },
        "warranty": {
            "status": "UNAVAILABLE",
            "reason": "D-4: the Build & Implementation Terms clause text is not in this "
                      "repository, only its URL and version. No gate may compute a warranty "
                      "window, an exclusion or a liability cap until the text is present.",
            "blocks": ["scripts/warranty-clock.py"],
            "record": "docs/Import/incorporated-terms.md",
        },
    }

    lock_doc = {
        "_generated_by": "scripts/import-baseline.py — do not hand-edit",
        "_purpose": "Pin every contractual source by content hash so a silent edit is detected.",
        "decisions_record": "docs/Import/baseline-lock.yml",
        "sources": {
            str(WBS_SRC): {"sha256": P.sha256(WBS_SRC), "bytes": WBS_SRC.stat().st_size,
                           "version": "v0.5", "accepted_by_client": True},
            str(SA_SRC): {"sha256": P.sha256(SA_SRC), "bytes": SA_SRC.stat().st_size,
                          "version": "v1.3", "signed": True},
        },
    }

    def dump(o):
        return json.dumps(o, indent=2, ensure_ascii=False, sort_keys=False) + "\n"

    return {OUT_WBS: dump(wbs_doc), OUT_SA: dump(sa_doc), OUT_LOCK: dump(lock_doc)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="exit 1 if any output is stale")
    ap.add_argument("--stdout", action="store_true", help="print instead of writing")
    args = ap.parse_args(argv)

    built = build()

    if args.stdout:
        for path, text in built.items():
            print(f"───── {path} " + "─" * max(0, 60 - len(str(path))))
            print(text)
        return 0

    if args.check:
        stale = []
        for path, text in built.items():
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                stale.append(path)
        if stale:
            print("import-baseline: STALE relative to the source documents: "
                  + ", ".join(str(s) for s in stale)
                  + "\n  Run: python3 scripts/import-baseline.py", file=sys.stderr)
            return 1
        print(f"import-baseline: baseline is current ({len(built)} files).")
        return 0

    for path, text in built.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    w = json.loads(built[OUT_WBS])
    s = json.loads(built[OUT_SA])
    print(f"import-baseline: wrote {len(built)} files — "
          f"{w['totals']['tasks']} tasks, {w['totals']['low']}–{w['totals']['high']} h "
          f"(corrected {w['corrected_totals_with_known_gap']['low']}–"
          f"{w['corrected_totals_with_known_gap']['high']} h), "
          f"agreement {s['total_hours']} h, "
          f"reconciliation: {s['reconciliation_with_wbs']['verdict'].split(' —')[0]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
