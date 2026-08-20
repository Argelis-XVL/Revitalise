#!/usr/bin/env python3
"""The single definition of what `logs/worklog.jsonl` MEANS.

WHY THIS MODULE EXISTS
----------------------
`IMP-0093` (blocker). Three scripts read the ledger and two of them independently
re-implemented the rule that a `correction` entry supersedes the session it names:

    scripts/verify-worklog.py    had it  -> reported 64 h invoiced to date
    scripts/compute-invoice.py   had it  -> reported 64 h invoiced to date
    scripts/verify-wbs-chain.py  had NOT -> reported 64 h + 20 h = 84 h

84 is the exact over-count `WL-0003` was written to prevent, and both gates exited 0, so
CI was green with the two numbers twenty hours apart. A rule implemented twice is a rule
that will be implemented once somewhere else.

So: **no script may compute the superseded set itself.** Call `superseded_ids()` here.

WHAT A CORRECTION MEANS
-----------------------
An issued invoice is never edited (`C-COM-003`); it is corrected by a new entry that
references it. The superseded entry STAYS in the file — deleting it would hide the
over-count from anyone reading the ledger — and is excluded from every total.
"""
from __future__ import annotations

import json
from pathlib import Path

DEFAULT_LEDGER = Path("logs/worklog.jsonl")


def load(path: Path | str = DEFAULT_LEDGER) -> tuple[list[dict], list[str]]:
    """Return (sessions, parse_errors). Every session carries `_superseded`.

    Parse errors are RETURNED, not raised: a gate reports a malformed ledger line by
    number rather than dying on it (IMP-0007 — a gate that cannot run must fail loudly,
    not silently pass).
    """
    path = Path(path)
    rows: list[dict] = []
    errors: list[str] = []
    if not path.exists():
        return rows, [f"{path}: missing"]
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            errors.append(f"{path}:{i} is not valid JSON: {exc}")
    dead = superseded_ids(rows)
    for s in rows:
        s["_superseded"] = s.get("id") in dead
    return rows, errors


def superseded_ids(rows: list[dict]) -> set[str]:
    """Ids superseded by a later `kind: correction` entry naming them."""
    return {s["corrects"] for s in rows
            if s.get("kind") == "correction" and s.get("corrects")}


def live(rows: list[dict]) -> list[dict]:
    """Sessions that still count. Everything else is history kept for readability."""
    dead = superseded_ids(rows)
    return [s for s in rows if s.get("id") not in dead]


def invoiced_to_date(rows: list[dict]) -> float:
    """Billable hours already carrying an invoice reference. Never re-billed (C-COM-003)."""
    return round(sum(float(s.get("hours") or 0) for s in live(rows)
                     if s.get("billable") and s.get("invoice")), 2)


def unbilled_billable(rows: list[dict]) -> list[dict]:
    """Confirmed billable sessions not yet on an invoice — what an invoice may draw from."""
    return [s for s in live(rows) if s.get("billable") and not s.get("invoice")]
