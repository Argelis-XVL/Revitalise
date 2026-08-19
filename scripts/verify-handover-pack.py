#!/usr/bin/env python3
"""Gate: a handover pack must account for every credential the solution depends on.

WHY THE CREDENTIAL RULE IS HARD
-------------------------------
PM-R22. `logs/known-failure-modes.md` records, as an established capability, that this project's
provisioning certificate lives in one Mac's CurrentUser/My keychain, bound to an app registration
with write access to the client's Dataverse. As a capability note that is correct and useful — it
stopped the reviewer having to re-teach it (`IMP-0022`). As a handover item it is a single point of
failure the Client cannot operate, and the Service Agreement excludes support after handover, so the
day it is needed is the day nobody is contractually obliged to answer.

So the system's own memory becomes the input to its exit plan: this gate reads the capability lines
out of the digest and fails if a credential named there is not accounted for in the pack.

ALSO ENFORCED
  * required sections present
  * every credential row has a holder and a transfer action
  * the §02 exclusions are quoted — that section is what fixes the support boundary
  * open items each carry a warranty-cover-end (or an explicit "not computed — D-4")

Run:
    python3 scripts/verify-handover-pack.py contract/handover/<file>.md
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DIGEST = Path("logs/known-failure-modes.md")
REQUIRED_SECTIONS = [
    "What was built", "Ownership after handover", "Licences and renewals",
    "Monitoring and alerting", "Credentials, certificates and app registrations",
    "Escalation", "Open items at handover", "What is NOT included after handover",
]
PLACEHOLDER = re.compile(r"<[^>\n]{2,60}>")


def credentials_from_digest() -> list[str]:
    """Pull identifiers out of the digest's capability lines: thumbprints, app ids, keychain refs."""
    if not DIGEST.exists():
        return []
    txt = DIGEST.read_text(encoding="utf-8")
    m = re.search(r"## Capabilities established in earlier sessions(.*?)(\n## |\Z)", txt, re.S)
    if not m:
        return []
    block = m.group(1)
    out = []
    out += re.findall(r"\b([0-9A-F]{40})\b", block)
    out += re.findall(r"\b([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\b", block)
    if re.search(r"keychain", block, re.I):
        out.append("keychain")
    return sorted(set(out))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pack", type=Path)
    args = ap.parse_args(argv)
    if not args.pack.exists():
        print(f"verify-handover-pack: {args.pack} does not exist", file=sys.stderr)
        return 2
    txt = args.pack.read_text(encoding="utf-8")
    v: list[str] = []

    for s in REQUIRED_SECTIONS:
        if s.lower() not in txt.lower():
            v.append(f"missing section: {s}")

    creds = credentials_from_digest()
    for c in creds:
        if c.lower() not in txt.lower():
            v.append(f"credential {c!r} is recorded in {DIGEST} as an established capability and is "
                     f"not accounted for in this pack. A dependency held only in an individual's "
                     f"personal keystore is a HARD handover blocker (PM-R22)")

    # credential table rows must carry a holder and a transfer action
    m = re.search(r"Credentials, certificates and app registrations(.*?)(\n## |\Z)", txt, re.S)
    if m:
        for row in re.findall(r"^\|(?!\s*What\b)(?!\s*-)(.+)\|\s*$", m.group(1), re.M):
            cells = [c.strip() for c in row.split("|")]
            if len(cells) >= 4 and any(cells):
                if not cells[2] or PLACEHOLDER.search(cells[2]):
                    v.append(f"credential row {cells[0][:40]!r} has no holder")
                if not cells[3] or PLACEHOLDER.search(cells[3]):
                    v.append(f"credential row {cells[0][:40]!r} has no transfer action")

    for phrase in ("ongoing operation, monitoring, support or maintenance after handover",
                   "website designer"):
        if phrase.lower() not in txt.lower():
            v.append(f"the exclusions section does not quote {phrase!r} — that section is what "
                     f"fixes the support boundary")

    m = re.search(r"Open items at handover(.*?)(\n## |\Z)", txt, re.S)
    if m:
        for row in re.findall(r"^\|(?!\s*Item)(?!\s*-)(.+)\|\s*$", m.group(1), re.M):
            cells = [c.strip() for c in row.split("|")]
            if len(cells) >= 3 and cells[0] and not cells[-1]:
                v.append(f"open item {cells[0][:40]!r} has no warranty-cover-end")

    print(f"verify-handover-pack: {args.pack} · {len(creds)} credential(s) from the digest")
    for x in v:
        print(f"  FAIL  {x}", file=sys.stderr)
    if v:
        print(f"\nverify-handover-pack: {len(v)} violation(s).", file=sys.stderr)
        return 1
    print("verify-handover-pack: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
