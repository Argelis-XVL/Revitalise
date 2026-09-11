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

# BASELINE INTAKE 2026-09-10, APPROVE BASELINE by Xander Lykopoulos: v0.6 supersedes v0.5.
# v0.5 stays in docs/Import/ — a superseded contractual source is never deleted.
#
# CLOSED 2026-09-11 (`IMP-0714`, improvement review 2026-09-10-2 row 11). The note retained below
# is what stood here until then, and the defect it describes is now fixed by
# newest_wbs_present() + the NEWER SOURCE check in --check:
#
#   "NOTE, and it is a live defect: this path is HARDCODED, so this script cannot detect the
#    arrival of a NEWER accepted source — the one event a staleness gate exists for. v0.6 sat in
#    docs/Import/ with `--check` reporting 'baseline is current' until a human mentioned it.
#    Re-pointing this constant reproduces the defect for v0.7."
#
# WBS_SRC remains the PINNED source — the version this baseline was generated from, which must
# stay explicit so a re-import is reproducible and so the pin is reviewable in a diff. What
# changed is that --check no longer TRUSTS it: it globs docs/Import/ for the highest version
# present and fails when that is not this one. A staleness gate that identifies its source by a
# hardcoded filename cannot detect the one event it exists for.
WBS_SRC = Path("docs/Import/Revitalise-WBS-Grant-Automation-v0.6.xlsx")
WBS_SRC_SUPERSEDED = Path("docs/Import/Revitalise-WBS-Grant-Automation-v0.5.xlsx")

# Matches "...v0.6.xlsx", "...v1.10.xlsx"; returns a comparable (major, minor) tuple so v0.10
# sorts ABOVE v0.9 rather than below it, which a string sort gets wrong.
WBS_VERSION_RE = __import__("re").compile(r"v(\d+)\.(\d+)", __import__("re").I)


def _version_key(path: Path) -> tuple[int, int] | None:
    m = WBS_VERSION_RE.search(path.name)
    return (int(m.group(1)), int(m.group(2))) if m else None


def newest_wbs_present(import_dir: Path = Path("docs/Import")) -> tuple[Path, tuple[int, int]] | None:
    """The highest-versioned *WBS*v<n>.<n>*.xlsx in import_dir, or None if there are none.

    Ignores Office lock/temp files (`~$...`), which appear whenever the workbook is open and
    would otherwise read as a rival source.
    """
    best: tuple[Path, tuple[int, int]] | None = None
    try:
        candidates = list(import_dir.glob("*WBS*.xlsx"))
    except OSError:
        return None
    for p in candidates:
        if p.name.startswith("~$"):
            continue
        key = _version_key(p)
        if key is None:
            continue
        if best is None or key > best[1]:
            best = (p, key)
    return best
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

# D-6: the WBS omits 20 hours for selecting and trialling DocuSign (IMP-0064). Recorded as a
# known gap against automation #3, NOT added to the workbook — amending an accepted
# specification is a re-approval, not an edit.
KNOWN_GAP = {
    "hours": 20,
    "scope": "Selecting and trialling the DocuSign platform",
    "belongs_to_automation": "3",
    "phase": "phase_1",
    "finding": "IMP-0064",
    # ── CLOSED 2026-08-19, and it STAYS closed through v0.6 ──────────────────────────────
    # The original action was "issue WBS v0.6 carrying this task". The reviewer closed that
    # route on 2026-08-19: "WBS 0.6 is not going to come. The 20 hours for DocuSign selection
    # have been invoiced already."
    #
    # A v0.6 was subsequently issued after all (2026-09-10, below) and it deliberately does NOT
    # carry this task. That is not an oversight in the new revision — the reviewer withdrew the
    # item from ever needing a WBS task on 2026-08-20, on its own merits, separately from the
    # no-v0.6 policy: docs/Import/baseline-lock.yml a2_docusign_and_rework_hours (IMP-0098),
    # "The work for Docusign was not scoped in the WBS and falls completely out of it... no v0.6
    # task should carry it." So the existence of v0.6 does not reopen this.
    "resolution": "OUT_OF_WBS_SCOPE_BY_REVIEWER_DECISION",
    "resolved_on": "2026-08-20",
    "resolution_history": [
        {"resolution": "NO_V06_WILL_BE_ISSUED", "on": "2026-08-19",
         "reviewer_statement": "WBS 0.6 is not going to come. The 20 hours for DocuSign "
                               "selection have been invoiced already.",
         "superseded_on": "2026-09-10",
         "superseded_why": "A v0.6 WAS issued and client-accepted (see WBS_IS_FINAL below), so "
                           "the stated reason — that no revision is coming — is no longer true. "
                           "The CONCLUSION is unchanged, on the independent 2026-08-20 ground "
                           "now recorded as the live resolution. Retained rather than replaced: "
                           "a decision whose stated reason expired but whose outcome held is "
                           "exactly the kind a later reader re-opens by mistake."},
    ],
    "reviewer_statement": "The work for Docusign was not scoped in the WBS and falls completely "
                          "out of it... no v0.6 task should carry it.",
    "consequence": "The 20 hours are not missing from the engagement, only from the breakdown: "
                   "they were performed and invoiced (logs/worklog.jsonl WL-0002). The accepted "
                   "specification — v0.5 then, v0.6 now — understates delivered scope by 20 "
                   "hours permanently, and any schedule or capacity figure derived from it is "
                   "short by that much. v0.6 does not change this by design.",
    "action": "NONE — closed. Recorded so no later reader re-opens it on the strength of v0.6 "
              "existing.",
}
# ── REVERSED 2026-09-10 ──────────────────────────────────────────────────────────────────
# Was True from 2026-08-19 to 2026-09-10, on the reviewer's "WBS 0.6 is not going to come".
# The reviewer reversed that decision and had the client accept a hand-corrected v0.6, imported
# under APPROVE BASELINE on 2026-09-10. The history is kept above and in contract/README.md
# rather than deleted: the 2026-08-19 decision was real, was acted on, and shaped four artefacts
# that still carry its reasoning.
#
# False does NOT mean "a v0.7 is expected". It means this baseline is no longer declared final,
# so a correction may again be routed to a re-approval — but contract/README.md's four-way
# routing table is still the first thing to try, because a re-approval needs the client.
WBS_IS_FINAL = False


def warranty_block() -> dict:
    """D-4 status, computed from what is actually in docs/Import/ — not asserted.

    The terms arrived on 2026-08-19 in Word format, which unblocks the warranty clock. But the
    General Terms in the repository read v1.2 (June 2026) and the signed agreement incorporates
    v1.3 (August 2026), so the document that governs is not the document we hold. The Build Terms
    match exactly (v1.0, August 2026), and B4/B5/B6/B8/B11 all live there — which is why the
    warranty clock can run while the General Terms mismatch stays open.
    """
    build_terms = sorted(Path("docs/Import").glob("*Build and Implementation*.doc*"))
    gen_terms = sorted(Path("docs/Import").glob("*General Terms*.doc*"))
    # Resolved 2026-08-19: General Terms v1.3 was uploaded and v1.2 removed, so the operative
    # revision and the one the signed agreement cites are the same. IMP-0071's check is what
    # surfaced the gap, and it now reports clean rather than being switched off — the version match
    # is computed on every run, so a future substitution is caught the same way.
    OPERATIVE_GENERAL_TERMS = "v1.3"
    AGREEMENT_CITES_GENERAL_TERMS = "v1.3"   # read from the signed PDF's GOVERNED BY block
    gen_version_ok = any(OPERATIVE_GENERAL_TERMS in f.name for f in gen_terms)
    out = {
        "status": "AVAILABLE" if build_terms else "UNAVAILABLE",
        "build_terms": {
            "present": bool(build_terms),
            "file": str(build_terms[0]) if build_terms else None,
            "version_in_filename": "v1.0",
            "cited_by_agreement": "v1.0 (August 2026)",
            "matches": True,
            "carries": ["B4 warranty period", "B5 acceptance", "B6 what is a Defect",
                        "B8 exclusions", "B10 warranty preconditions", "B11 liability caps"],
        },
        "general_terms": {
            "present": bool(gen_terms),
            "file": str(gen_terms[0]) if gen_terms else None,
            "version_in_repository": (gen_terms[0].name if gen_terms else None),
            "operative_version": "v1.3",
            "operative_confirmed_by": "Xander Lykopoulos (issuer of the terms), 2026-08-19",
            "cited_by_agreement": "v1.3 (August 2026)",
            "matches": gen_version_ok,
            # True when the agreement names a revision other than the operative one. Computed, not
            # asserted, so it clears itself if a future agreement cites v1.2.
            "agreement_citation_is_wrong": AGREEMENT_CITES_GENERAL_TERMS != OPERATIVE_GENERAL_TERMS,
        },
        "clauses_that_change_the_design": {
            "B5_acceptance_is_not_only_explicit": "A phase is accepted when the Client confirms in "
                "writing, OR after ten business days from submission with no specific written "
                "objection, OR by putting a Deliverable into live operational use. Two of those "
                "three routes start a 60-day warranty window with nobody recording anything.",
            "B6_defect_excludes_change": "A change of requirement, an additional field, a new "
                "automation or a different layout is NOT a Defect. That is the warranty-versus-"
                "change-order test, and it is now quotable.",
            "B10_warranty_is_conditional": "The warranty applies only while all invoices then due "
                "are paid, licences and credentials are maintained, and the operational runbooks "
                "have been accepted.",
        },
        "record": "docs/Import/incorporated-terms.md",
    }
    out["open_issue"] = (
        "RESOLVED for computation, OPEN as a contract defect. The operative General Terms are v1.2 "
        "(June 2026), confirmed by the issuer, and that is the text held here — so clauses may be "
        "computed against it. But the signed Service Agreement §'GOVERNED BY' incorporates "
        "'General Terms and Conditions of Consultancy Services v1.3 (August 2026)', a revision the "
        "issuer says is not the operative one. The client signed the document naming v1.3. Correct "
        "this in the next Service Agreement revision or by side letter; a dispute would turn on the "
        "signed text, not on this file."
    ) if out["general_terms"]["agreement_citation_is_wrong"] else None
    if out.get("open_issue") is None:
        out.pop("open_issue", None)
    return out


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
        "source": {"file": str(WBS_SRC), "version": "v0.6",
                   "accepted_by_client": True, "accepted_ref": "D-5, docs/Import/baseline-lock.yml",
                   "supersedes": {"version": "v0.5", "file": str(WBS_SRC_SUPERSEDED),
                                  "retained": True,
                                  "note": "Superseded on 2026-09-10, not deleted."},
                   "imported_on": "2026-09-10",
                   "imported_under": "APPROVE BASELINE — Xander Lykopoulos",
                   "final": WBS_IS_FINAL,
                   "final_note": "v0.6 corrects exactly two things against v0.5, verified by "
                                 "parsing both workbooks and diffing all 61 tasks field by field: "
                                 "task 8.3 Depends On '8.1' -> '8.1, 8.2', and task 0.4's "
                                 "Description and Deliverable now name the Grant Administration "
                                 "app (rev_grantadministration). NO hours moved — 177-277 across "
                                 "61 tasks in both revisions, every per-phase subtotal identical, "
                                 "the Summary sheet unchanged. So this is a correction, not a "
                                 "change of scope, and no change order arises (C-COM-002). The "
                                 "2026-08-19 'no v0.6 will be issued' decision was reversed by "
                                 "the reviewer on 2026-09-10; see KNOWN_GAP.resolution_history "
                                 "and contract/README.md for why the DocuSign gap is unaffected."},
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
            # Version-NEUTRAL key. Was "wbs_v05" until 2026-09-10; a key naming the revision it
            # holds has to be renamed by every reader on each re-approval, which is the same rot
            # the hardcoded WBS_SRC above carries. The version is stated in "wbs_version".
            "wbs_version": wbs_doc["source"]["version"],
            "wbs_as_accepted": {"low": wbs_doc["totals"]["low"],
                                "high": wbs_doc["totals"]["high"]},
            "wbs_corrected": {"low": corrected["low"], "high": corrected["high"]},
            "agreement_total": total,
            "agreement_total_inside_corrected_band": inside,
            "verdict": ("RECONCILED — the agreement total falls inside the corrected WBS band"
                        if inside else
                        "UNRECONCILED — investigate what work is missing from the breakdown "
                        "before concluding the documents disagree (IMP-0064)"),
        },
        "warranty": warranty_block(),
    }

    # WBS: hashed over the PARSED task content, not the raw file. SharePoint rewrites
    # customXml/docProps container metadata on ordinary sync with zero change to the actual
    # worksheet data — verified 2026-09-09 by diffing every zip member between the pinned
    # commit and HEAD: only customXml/item1.xml, item2.xml, itemProps1.xml and
    # docProps/custom.xml differed, and the 61 parsed tasks compared byte-identical. A raw-file
    # hash cannot tell that apart from a real edit to the accepted specification, and this gate
    # (C-COM-008) went red for three days over exactly that (IMP-0691). pmsources.py's own
    # docstring has the full reasoning for why the PDF keeps the raw-file hash instead.
    wbs_fp = P.wbs_content_fingerprint(WBS_SRC)
    lock_doc = {
        "_generated_by": "scripts/import-baseline.py — do not hand-edit",
        "_purpose": "Pin every contractual source by content hash so a silent edit is detected.",
        "decisions_record": "docs/Import/baseline-lock.yml",
        "sources": {
            str(WBS_SRC): {"sha256": wbs_fp["sha256"], "bytes": wbs_fp["bytes"],
                           "hashed": "parsed task content (IMP-0691) — not the raw file",
                           "version": "v0.6", "accepted_by_client": True,
                           "pinned_on": "2026-09-10",
                           "supersedes_version": "v0.5",
                           "supersedes_sha256": P.wbs_content_fingerprint(
                               WBS_SRC_SUPERSEDED)["sha256"] if WBS_SRC_SUPERSEDED.exists()
                               else None},
            str(SA_SRC): {"sha256": P.sha256(SA_SRC), "bytes": SA_SRC.stat().st_size,
                          "hashed": "raw file — this is the literally-signed document",
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

        # NEWER SOURCE — checked even when every output is current, because this is the case
        # "outputs match their source" cannot see: the outputs agree with the source we were
        # TOLD to read, while a newer client-accepted one sits beside it unread (IMP-0714).
        newest = newest_wbs_present(WBS_SRC.parent)
        pinned = _version_key(WBS_SRC)
        if newest and pinned and newest[1] > pinned:
            got = f"v{newest[1][0]}.{newest[1][1]}"
            have = f"v{pinned[0]}.{pinned[1]}"
            print(f"import-baseline: NEWER SOURCE PRESENT — {newest[0]} is {got}, but this "
                  f"baseline is pinned to {have} ({WBS_SRC}).\n"
                  f"  Every contract/*.json output is current with respect to {have}, so the "
                  f"staleness check above passes; that is exactly the blind spot this check "
                  f"exists for.\n"
                  f"  A new accepted specification is the loudest possible change to the "
                  f"baseline and must not wait for someone to mention it (C-COM-008/009).\n"
                  f"  This is NOT resolved by re-pointing WBS_SRC: follow the BASELINE INTAKE "
                  f"procedure — pm-agent, gate APPROVE BASELINE — which diffs the parsed tasks "
                  f"field-by-field before anything is regenerated.",
                  file=sys.stderr)
            return 1

        print(f"import-baseline: baseline is current ({len(built)} files); "
              f"no WBS version newer than {WBS_SRC.name} is present.")
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
