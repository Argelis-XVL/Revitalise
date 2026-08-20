#!/usr/bin/env python3
"""Which window is each phase in — hypercare, warranty, or out of both?

WHY IT MATTERS
--------------
PM-R15/PM-R20. The window decides whether an incoming defect is free. Build Terms B4, as summarised
in the signed agreement: 60 calendar days from Acceptance of the phase; for the final phase until
the later of 60 days and two trustee board cycles, and in any event no later than 150 days;
hypercare is the ten business days immediately after each phase go-live. Getting this wrong costs
money in one direction and goodwill in the other.

WHEN IT REFUSES TO ANSWER — AND WHY IT NO LONGER DOES
-----------------------------------------------------
D-4. The Build & Implementation Terms are incorporated **by reference**, and while the repository
held only their URL and version this script exited 2 rather than computing from a paraphrase: a
window computed from the agreement's §4.2 covering summary would be indistinguishable from one
computed from the clause, and the first person to rely on it would not know which they had.

**Since 2026-08-19 the clause text IS here** — `docs/Import/Argelis - Terms and Conditions Build
and Implementation Services v1.0.docx`, matching the version the agreement cites — so the guard
below passes and the script answers. The guard stays: it is what makes the answer trustworthy, and
it must fire again the moment a new agreement cites a version this repository does not hold.

`IMP-0092` is the tail of this change. The capability became available and two files — this
agent's own instructions and the billable-time skill — went on telling agents it was blocked. When
a refusal is lifted, grep for every sentence that announced it.

`IMP-0029` is the same lesson one level up — a document that restates a figure it does not own goes
stale silently. Restating a *clause* would be that defect with worse consequences.

Run:
    python3 scripts/warranty-clock.py
    python3 scripts/warranty-clock.py --as-of 2026-10-01
    python3 scripts/warranty-clock.py --assume-terms-present   # dry-run the arithmetic only
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

SA = Path("contract/service-agreement.json")
ACCEPT = Path("contract/acceptance")
# Uploaded 2026-08-19 in Word format. Both .docx and .pdf are accepted: the format is irrelevant,
# the presence of the authoritative TEXT is the point (D-4).
TERMS_GLOBS = ["docs/Import/*General Terms*.doc*", "docs/Import/*Build and Implementation*.doc*"]
HYPERCARE_BUSINESS_DAYS = 10
WARRANTY_DAYS = 60
FINAL_PHASE_MAX_DAYS = 150
DEEMED_ACCEPTANCE_BUSINESS_DAYS = 10

# ── What the clause text says, now that it is in the repository (Build Terms v1.0, Aug 2026) ──
# Quoted rather than paraphrased, because two of these change how acceptance works and the
# Service Agreement's covering summary does not mention either.
CLAUSES = {
    "B4": "For each Deliverable the Warranty Period is 60 calendar days from Acceptance of the "
          "phase in which it is delivered, unless the Service Agreement states a different "
          "period. Correcting a Defect does not extend the Warranty Period; a corrected "
          "component carries the unexpired remainder of the original period.",
    "B5": "A phase is accepted when the Client confirms acceptance in writing, OR when ten "
          "business days have passed after the Consultant submits the phase for acceptance "
          "without the Client raising a specific written objection. Putting a Deliverable into "
          "live operational use ALSO constitutes acceptance of it.",
    "B6": "A Defect is a reproducible failure to conform to the Agreed Specification, reported "
          "in writing within the Warranty Period. A change of requirement, an additional field, "
          "a new automation, a different layout, or any matter listed in B8 is NOT a Defect.",
    "B10": "The warranty applies only while the Client has paid all invoices then due, maintains "
           "the licences, entitlements and credentials the solution needs, has accepted the "
           "operational runbooks, and gives reasonable access.",
    "B13": "Once the Warranty Period has expired the Consultant corrects faults on a "
           "time-and-materials basis.",
}


def terms_present() -> tuple[bool, list[str]]:
    missing = [g for g in TERMS_GLOBS if not list(Path().glob(g))]
    return (not missing), missing


def add_business_days(d: dt.date, n: int) -> dt.date:
    out = d
    while n:
        out += dt.timedelta(days=1)
        if out.weekday() < 5:
            n -= 1
    return out


def read_acceptances() -> list[dict]:
    """Acceptance records, plus the two routes B5 opens that no record may capture.

    B5 is the clause the Service Agreement's covering summary does not mention, and it matters:
    acceptance is NOT only an explicit act. A phase is also accepted by SILENCE (ten business days
    after submission with no specific written objection) and by USE (putting a Deliverable into
    live operational use). Both start a 60-day warranty window with nobody recording anything.

    So a pack may additionally declare `Submitted for acceptance:` and `In live use since:`, and
    this function reports the EARLIEST of the three routes as the operative acceptance date.
    """
    out = []
    if not ACCEPT.exists():
        return out
    for p in sorted(ACCEPT.glob("PA-*.md")):
        txt = p.read_text(encoding="utf-8")
        phase = re.search(r"(?im)^\s*[-*]?\s*Phase:\s*(.+)$", txt)
        acc = re.search(r"(?im)^\s*[-*]?\s*Accepted on:\s*(\d{4}-\d{2}-\d{2})", txt)
        by = re.search(r"(?im)^\s*[-*]?\s*Accepted by:\s*(.+)$", txt)
        golive = re.search(r"(?im)^\s*[-*]?\s*Go-live:\s*(\d{4}-\d{2}-\d{2})", txt)
        subm = re.search(r"(?im)^\s*[-*]?\s*Submitted for acceptance:\s*(\d{4}-\d{2}-\d{2})", txt)
        live = re.search(r"(?im)^\s*[-*]?\s*In live use since:\s*(\d{4}-\d{2}-\d{2})", txt)
        deemed = None
        if subm:
            deemed = add_business_days(dt.date.fromisoformat(subm.group(1)),
                                       DEEMED_ACCEPTANCE_BUSINESS_DAYS).isoformat()
        routes = {"written": acc.group(1) if acc else None,
                  "deemed_by_silence": deemed,
                  "deemed_by_use": live.group(1) if live else None}
        dates = [v for v in routes.values() if v]
        out.append({"file": str(p),
                    "phase": phase.group(1).strip() if phase else None,
                    "accepted_on": min(dates) if dates else None,
                    "acceptance_routes": routes,
                    "operative_route": (min(routes.items(), key=lambda kv: kv[1] or "9999")[0]
                                        if dates else None),
                    "accepted_by": by.group(1).strip() if by else None,
                    "go_live": golive.group(1) if golive else None,
                    "submitted_for_acceptance": subm.group(1) if subm else None,
                    "in_live_use_since": live.group(1) if live else None})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--as-of", default=None)
    ap.add_argument("--assume-terms-present", action="store_true",
                    help="run the arithmetic without the clause text — for testing ONLY; the "
                         "output is explicitly marked as not contractual")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if not SA.exists():
        print("warranty-clock: contract/service-agreement.json missing", file=sys.stderr)
        return 2
    sa = json.loads(SA.read_text(encoding="utf-8"))
    ok, missing = terms_present()

    if not ok and not args.assume_terms_present:
        print("WARRANTY CLOCK — REFUSING TO COMPUTE", file=sys.stderr)
        print("", file=sys.stderr)
        print("  Reason: the incorporated Build & Implementation Terms are not in this repository, "
              "only their URL and version (D-4).", file=sys.stderr)
        print("  The agreement's §4.2 is a paraphrase in a covering document; a warranty window "
              "computed from it would be indistinguishable from one computed from the clause.",
              file=sys.stderr)
        print("", file=sys.stderr)
        print("  Missing:", file=sys.stderr)
        for m in missing:
            print(f"    {m}", file=sys.stderr)
        print("", file=sys.stderr)
        print("  Fix (a two-minute manual step, and the reviewer's to take — see "
              "docs/Import/incorporated-terms.md):", file=sys.stderr)
        print("    save each page as PDF into docs/Import/, keeping the version in the filename:",
              file=sys.stderr)
        print("      https://argelis.nl/general-terms-and-conditions   -> "
              "Argelis-General-Terms-v1.3-2026-08.pdf", file=sys.stderr)
        print("      https://argelis.nl/build-implementation-terms/    -> "
              "Argelis-Build-Implementation-Terms-v1.0-2026-08.pdf", file=sys.stderr)
        print("", file=sys.stderr)
        print(f"  Until then: {len(read_acceptances())} acceptance record(s) exist and no window "
              f"is asserted for any phase.", file=sys.stderr)
        return 2

    today = dt.date.fromisoformat(args.as_of) if args.as_of else dt.date.today()
    rows = []
    for a in read_acceptances():
        if not a["accepted_on"]:
            rows.append(dict(a, window="INVALID",
                             note="acceptance record carries no 'Accepted on:' date — V6 cannot be "
                                  "recorded without one (PM-R18)"))
            continue
        acc = dt.date.fromisoformat(a["accepted_on"])
        golive = dt.date.fromisoformat(a["go_live"]) if a["go_live"] else acc
        hyper_end = add_business_days(golive, HYPERCARE_BUSINESS_DAYS)
        warr_end = acc + dt.timedelta(days=WARRANTY_DAYS)
        final = (a["phase"] or "").strip().lower() in {"phase 4", "completion"}
        cap_end = acc + dt.timedelta(days=FINAL_PHASE_MAX_DAYS) if final else None
        if today <= hyper_end:
            window = "HYPERCARE"
        elif today <= warr_end:
            window = "WARRANTY"
        elif final and cap_end and today <= cap_end:
            window = "WARRANTY (final phase — pending two board cycles, capped)"
        else:
            window = "OUT OF WARRANTY"
        rows.append(dict(a, hypercare_ends=hyper_end.isoformat(),
                         warranty_ends=warr_end.isoformat(),
                         final_phase_cap=cap_end.isoformat() if cap_end else None,
                         window=window))

    result = {"as_of": today.isoformat(),
              "contractual": ok,
              "caveat": None if ok else "NOT CONTRACTUAL — computed with --assume-terms-present "
                                        "while the clause text is absent (D-4). Do not rely on it.",
              "phases": rows,
              "no_acceptance_records": not rows}
    if args.json:
        print(json.dumps(result, indent=2))
        return 0
    if not ok:
        print("⚠ NOT CONTRACTUAL — clause text absent (D-4); arithmetic shown for testing only\n")
    if not rows:
        print("No acceptance records in contract/acceptance/. No warranty window has started for "
              "any phase, and none is asserted.")
        return 0
    print(f"WARRANTY CLOCK — as of {result['as_of']}\n")
    for r in rows:
        print(f"  {r['phase'] or '(phase unstated)'}: {r['window']}")
        print(f"      accepted {r['accepted_on']} by {r['accepted_by']} · hypercare ends "
              f"{r.get('hypercare_ends')} · warranty ends {r.get('warranty_ends')}")
    print("\nThird-party platforms (B8: M365, Power Platform, Dataverse, Power Automate, Power "
          "Apps, AI Builder, DocuSign, QuickBooks Online, WordPress and its form plugin) are never "
          "warranty work, whatever the window.")
    print("\nB6 — NOT a Defect, so not warranty work: a change of requirement, an additional "
          "field,\n     a new automation, or a different layout. Those are change orders.")
    print("B10 — the warranty applies only while all invoices then due are PAID, the licences and "
          "credentials\n      are maintained, and the operational runbooks have been accepted.")
    print("B5  — acceptance also happens by SILENCE (10 business days after submission) and by "
          "USE\n      (putting a Deliverable into live operational use). Neither needs anyone to "
          "record anything.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
