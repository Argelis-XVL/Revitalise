#!/usr/bin/env python3
"""List every dated register entry that has expired or expires soon — before a build is approved.

WHY THIS EXISTS (IMP-1046, IMP-1157, IMP-1154, IMP-1197; improvement review 2026-10-21 row 4).
The reviewer approved an advance-warning listing on 2026-10-05 (D-3 of
docs/improvements/2026-10-05-improvement-review-2.md). It was recorded as a deferral, which the queue
reads as settled, so four reviews passed it by. TD-007 then expired and halted the 2026-10-20 build at
its last step, and three DEV placeholders expired on 2026-10-16 in a file no gate reads.

The HARD expiry checks stay where they are (verify-tad-coverage.py, verify-pipeline-config.py check
14, verify-wbs-chain.py). This is the advance warning, not a second gate: REPORT ONLY, exit 0 always.
lead-agent runs it before relaying any "Approved for build" and puts every line in front of the
reviewer.

WHAT IT READS — a fixed list. A register added later is UNSEEN until it is added to REGISTERS below:
  * config/flow-check7-exceptions.json        (list of entries with `expires`)
  * config/gate-baselines.json                (`baselines[]`)
  * contract/known-exceptions.json            (`exceptions[]`; `_closed_exceptions` are skipped)
  * contract/tad-deferrals.json               (`deferrals[]`)
  * provisioning/deploymentSettings/{dev,test,prd}-settings.json  `_unresolved` blocks
    (the *.example.json files are excluded)
  * config/revitalise-grant-automation-pipeline.yml  every `blocked_on_asserted` date + 14 days
    (verify-pipeline-config.py check 14's window). A note matched by a config/gate-baselines.json
    entry's `matches` is printed as ACCEPTED, not as due.
Any entry carrying `closed` is skipped.

USAGE:
    python3 scripts/report-expiring-registers.py              # window: today + 14 days
    python3 scripts/report-expiring-registers.py --days 30
    python3 scripts/report-expiring-registers.py --selftest
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PIPELINE = "config/revitalise-grant-automation-pipeline.yml"
BLOCKED_ON_WINDOW_DAYS = 14   # verify-pipeline-config.py check 14
JSON_REGISTERS = [
    "config/flow-check7-exceptions.json",
    "config/gate-baselines.json",
    "contract/known-exceptions.json",
    "contract/tad-deferrals.json",
    "provisioning/deploymentSettings/dev-settings.json",
    "provisioning/deploymentSettings/test-settings.json",
    "provisioning/deploymentSettings/prd-settings.json",
]
SKIP_KEYS = {"_closed_exceptions"}


def _as_date(value) -> date | None:
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value).strip()[:10])
    except ValueError:
        return None


def _ident(entry: dict, where: str) -> str:
    for key in ("id", "path", "matches"):
        if entry.get(key):
            return str(entry[key])
    if entry.get("flow_prefix"):
        return f"{entry['flow_prefix']}/{entry.get('scope_name', '')}"
    return where


def _clearing(entry: dict) -> str:
    text = str(entry.get("clearing_action") or entry.get("clears_when")
               or entry.get("revisit_when") or entry.get("why") or "—")
    text = " ".join(text.split())
    return text if len(text) <= 140 else text[:137] + "..."


def json_entries(rel: str, data) -> list[tuple[str, str, date, str, str]]:
    """(file, id, expires, owner, clearing) for every dict carrying `expires` and no `closed`."""
    out: list[tuple[str, str, date, str, str]] = []

    def walk(node, where: str) -> None:
        if isinstance(node, dict):
            if "expires" in node and "closed" not in node:
                when = _as_date(node["expires"])
                if when is not None:
                    out.append((rel, _ident(node, where), when, str(node.get("owner") or "—"),
                                _clearing(node)))
            for key, value in node.items():
                if key not in SKIP_KEYS:
                    walk(value, f"{where}.{key}" if where else key)
        elif isinstance(node, list):
            for i, value in enumerate(node):
                walk(value, f"{where}[{i}]")

    walk(data, "")
    return out


def pipeline_notes(data) -> list[tuple[str, date]]:
    """(dotted path, asserted date) for every step carrying `blocked_on_asserted`."""
    out: list[tuple[str, date]] = []

    def walk(node, where: str) -> None:
        if isinstance(node, dict):
            if "blocked_on_asserted" in node:
                when = _as_date(node["blocked_on_asserted"])
                if when is not None:
                    out.append((where, when))
            for key, value in node.items():
                walk(value, f"{where}.{key}" if where else str(key))
        elif isinstance(node, list):
            for i, value in enumerate(node):
                walk(value, f"{where}[{i}]")

    walk(data, "")
    return out


def collect(root: Path, today: date, days: int) -> tuple[list[str], list[str]]:
    """Return (due lines, accepted lines)."""
    horizon = today + timedelta(days=days)
    rows: list[tuple[date, str]] = []
    baseline_keys: dict[str, str] = {}
    for rel in JSON_REGISTERS:
        path = root / rel
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            rows.append((today, f"UNREADABLE {rel}: {exc}"))
            continue
        if rel == "config/gate-baselines.json" and isinstance(data, dict):
            for b in data.get("baselines") or []:
                if isinstance(b, dict) and b.get("matches"):
                    baseline_keys[str(b["matches"])] = str(b.get("expires") or "?")
        for f, ident, when, owner, clearing in json_entries(rel, data):
            if when <= horizon:
                state = "EXPIRED" if when < today else "DUE"
                rows.append((when, f"{state:8} {when}  {f} :: {ident} — owner {owner}; "
                                   f"clears: {clearing}"))
    accepted: list[str] = []
    pipe = root / PIPELINE
    if pipe.is_file():
        try:
            import yaml  # noqa: PLC0415 — only this half needs it
            data = yaml.safe_load(pipe.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001 — a report names what it could not read
            rows.append((today, f"UNREADABLE {PIPELINE}: {exc}"))
            data = None
        for where, asserted in pipeline_notes(data):
            due = asserted + timedelta(days=BLOCKED_ON_WINDOW_DAYS)
            if where in baseline_keys:
                accepted.append(f"ACCEPTED {PIPELINE} :: {where} — blocked_on asserted {asserted}, "
                                f"accepted by config/gate-baselines.json until "
                                f"{baseline_keys[where]}")
            elif due <= horizon:
                state = "EXPIRED" if due < today else "DUE"
                rows.append((due, f"{state:8} {due}  {PIPELINE} :: {where} — blocked_on asserted "
                                  f"{asserted}; re-test and re-date, or remove the note "
                                  f"(verify-pipeline-config.py check 14)"))
    rows.sort(key=lambda r: r[0])
    return [line for _, line in rows], accepted


def selftest() -> int:
    today = date(2026, 10, 22)
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "config").mkdir()
        (root / "contract").mkdir()
        (root / "provisioning/deploymentSettings").mkdir(parents=True)
        (root / "config/flow-check7-exceptions.json").write_text(json.dumps([
            {"flow_prefix": "F", "scope_name": "S", "owner": "o", "expires": "2026-09-30",
             "clearing_action": "fix it"}]), encoding="utf-8")
        (root / "contract/known-exceptions.json").write_text(json.dumps({
            "exceptions": [{"id": "EX-1", "owner": "o", "expires": "2026-11-27", "clears_when": "x"},
                           {"id": "EX-2", "owner": "o", "expires": "2026-10-30", "clears_when": "y"}],
            "_closed_exceptions": [{"id": "EX-0", "expires": "2026-01-01", "closed": "2026-02-01"}]}),
            encoding="utf-8")
        (root / "config/gate-baselines.json").write_text(json.dumps({"baselines": [
            {"matches": "environments.prd.pre[0]", "owner": "o", "expires": "2026-11-27"}]}),
            encoding="utf-8")
        (root / "provisioning/deploymentSettings/dev-settings.json").write_text(json.dumps(
            {"a": {"_unresolved": [{"path": "a.b", "owner": "o", "expires": "2026-10-16",
                                    "why": "w"}]}}), encoding="utf-8")
        (root / "provisioning/deploymentSettings/dev-settings.example.json").write_text(json.dumps(
            {"_unresolved": [{"path": "ex", "owner": "o", "expires": "2026-01-01"}]}),
            encoding="utf-8")
        (root / PIPELINE).write_text(
            "environments:\n  dev:\n    pre:\n      - blocked_on_asserted: 2026-10-16\n"
            "  prd:\n    pre:\n      - blocked_on_asserted: 2026-08-19\n", encoding="utf-8")
        due, accepted = collect(root, today, 14)
    text = "\n".join(due)
    checks = {
        "expired check-7 exception listed": "EXPIRED  2026-09-30  config/flow-check7" in text,
        "expired _unresolved listed": "dev-settings.json :: a.b" in text,
        "entry due inside the window listed": "EX-2" in text,
        "entry outside the window not listed": "EX-1" not in text,
        "closed entry skipped": "EX-0" not in text,
        "example settings excluded": ":: ex " not in text,
        "blocked_on + 14 days listed": "environments.dev.pre[0]" in text and "2026-10-30" in text,
        "baselined note ACCEPTED, not due": (len(accepted) == 1
                                             and "environments.prd.pre[0]" not in text),
        "exactly four due lines": len(due) == 4,
    }
    bad = 0
    for name, ok in checks.items():
        bad += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {name}")
    if bad:
        print("\n".join(due + accepted))
    print("selftest: " + ("FAILED" if bad else "passed"))
    return 1 if bad else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--days", type=int, default=14, help="look-ahead window (default 14)")
    ap.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    today = date.today()
    due, accepted = collect(a.repo_root, today, a.days)
    print(f"report-expiring-registers: {len(due)} entr(y/ies) expired or due by "
          f"{today + timedelta(days=a.days)} (today {today}); report only, exit 0.")
    for line in due + accepted:
        print(f"  {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
