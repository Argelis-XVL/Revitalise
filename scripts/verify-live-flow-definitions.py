#!/usr/bin/env python3
"""Re-read every flow's live definition from Dataverse and diff it against solution source.

WHY (IMP-0956, IMP-0959; docs/improvements/2026-09-29-improvement-review.md section 3.2):
a live read is true only when it was taken. On 2026-09-29 the intake flow read back complete after a
DEV import and had lost its `Create_application` mapping about twenty minutes later with no deploy
logged. This step is the post-import read that would have shown it, and it names the second failure
shape too: a `modifiedon` later than the import means something wrote the flow after you did.

READ-ONLY. One `pac env fetch` per query against the active auth profile. No write, no credential
beyond the profile `pac` already holds.

WHAT IT CHECKS, per flow found in <workflows-dir>/*.data.xml (WorkflowId is the join key):
  1. MISSING   the workflow row is absent from the environment.
  2. DIFFERS   live `workflow.clientdata` -> properties.definition differs from source (canonical
               JSON compare: key order and whitespace are ignored, values are not).
               `connectionReferences` is compared and reported as its own line.
  3. MODIFIED  `workflow.modifiedon` is later than the import's completion.

IMPORT COMPLETION defaults to the latest completed `importjob` row for --solution (progress 100),
overridable with --imported-at (UTC, ISO 8601).

CLOCKS. `pac env fetch` renders date-times in UTC with NO zone marker and MINUTE resolution
("9/29/2026 7:33 PM"); logs/ lines are local time (knowledge/technology/testing-tools.md). Every time
here is UTC and is printed with a "UTC" suffix. Because modifiedon is truncated to the minute, a
write in the SAME minute as the import's completion cannot be told apart from the import: the check
is `modifiedon minute > import completion minute`, and that limit is stated in the output.

EXIT CODES: 0 = every flow matches and none was modified after the import; 1 = at least one finding;
2 = the read itself failed (usage, pac missing/unauthenticated, unparseable output).

USAGE:
    python3 scripts/verify-live-flow-definitions.py --env dev
    python3 scripts/verify-live-flow-definitions.py --env dev --imported-at 2026-09-29T19:34:00
    python3 scripts/verify-live-flow-definitions.py --selftest

`--env` is a label for the report; the environment queried is pac's active profile (or --environment).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_WORKFLOWS = REPO_ROOT / "src/solutions/RevitaliseGrantAutomation/Workflows"
DEFAULT_SOLUTION = "RevitaliseGrantAutomation"
TIMEOUT = REPO_ROOT / "scripts/run-with-timeout.sh"

GUID = r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
TS = r"\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2} [AP]M"
WF_ROW = re.compile(rf"^(?P<id>{GUID})\s+(?P<name>.*?)\s+(?P<mod>{TS})\s+(?P<data>\{{.*)$")
JOB_ROW = re.compile(rf"^\S+\s+(?P<done>{TS})\s+{TS}\s+(?P<progress>[\d.]+)\s+{GUID}\s*$")


class ReadError(Exception):
    pass


def parse_ts(text: str) -> datetime:
    """pac's en-US rendering, UTC, minute resolution."""
    return datetime.strptime(text.strip(), "%m/%d/%Y %I:%M %p")


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def source_flows(workflows_dir: Path) -> dict[str, dict]:
    """workflow id (lower) -> {name, properties} from each *.data.xml and its JsonFileName."""
    out: dict[str, dict] = {}
    for meta in sorted(workflows_dir.glob("*.data.xml")):
        root = ET.parse(meta).getroot()
        wid = root.attrib["WorkflowId"].strip("{}").lower()
        jf = root.findtext("JsonFileName") or ""
        path = workflows_dir / Path(jf).name
        out[wid] = {"name": root.attrib.get("Name", wid),
                    "properties": json.loads(path.read_text(encoding="utf-8"))["properties"],
                    "file": path.name}
    return out


def parse_workflow_table(text: str) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for line in text.splitlines():
        m = WF_ROW.match(line.strip())
        if m:
            rows[m["id"].lower()] = {"name": m["name"], "modifiedon": parse_ts(m["mod"]),
                                     "clientdata": m["data"]}
    return rows


def parse_latest_import(text: str) -> datetime | None:
    done = [parse_ts(m["done"]) for line in text.splitlines()
            if (m := JOB_ROW.match(line.strip())) and float(m["progress"]) >= 100.0]
    return max(done) if done else None


def compare(source: dict[str, dict], live: dict[str, dict], imported_at: datetime) -> list[str]:
    findings: list[str] = []
    imp_min = imported_at.replace(second=0, microsecond=0)
    for wid, src in sorted(source.items(), key=lambda kv: kv[1]["name"]):
        label = f"{src['name']} ({wid})"
        row = live.get(wid)
        if row is None:
            findings.append(f"MISSING   {label}: no workflow row in the environment")
            continue
        try:
            lp = json.loads(row["clientdata"])["properties"]
        except (ValueError, KeyError) as e:
            findings.append(f"DIFFERS   {label}: live clientdata is not parseable ({e})")
            continue
        sp = src["properties"]
        if canon(lp.get("definition")) != canon(sp.get("definition")):
            findings.append(f"DIFFERS   {label}: live definition differs from {src['file']}"
                            f"{_first_difference(sp.get('definition'), lp.get('definition'))}")
        if canon(lp.get("connectionReferences")) != canon(sp.get("connectionReferences")):
            findings.append(f"DIFFERS   {label}: live connectionReferences differ from {src['file']}")
        if row["modifiedon"] > imp_min:
            findings.append(f"MODIFIED  {label}: modifiedon {row['modifiedon']:%Y-%m-%d %H:%M} UTC is "
                            f"after the import's completion {imp_min:%Y-%m-%d %H:%M} UTC")
    return findings


def _first_difference(src, live, path: str = "definition") -> str:
    """Name the first path where the two differ, so a reviewer is not handed 'they differ'."""
    if isinstance(src, dict) and isinstance(live, dict):
        for k in sorted(set(src) | set(live)):
            if k not in live:
                return f" (first difference: {path}.{k} missing live)"
            if k not in src:
                return f" (first difference: {path}.{k} present live, absent in source)"
            if canon(src[k]) != canon(live[k]):
                return _first_difference(src[k], live[k], f"{path}.{k}")
        return ""
    if isinstance(src, list) and isinstance(live, list) and len(src) != len(live):
        return f" (first difference: {path} has {len(live)} items live, {len(src)} in source)"
    return f" (first difference: {path})"


def run_fetch(xml: str, environment: str | None) -> str:
    with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False) as f:
        f.write(xml)
        qfile = f.name
    cmd = ["bash", str(TIMEOUT), "90", "pac", "env", "fetch", "--xmlFile", qfile]
    if environment:
        cmd += ["--environment", environment]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True)
    except OSError as e:
        raise ReadError(f"could not run pac: {e}")
    finally:
        Path(qfile).unlink(missing_ok=True)
    # pac exits 0 on some failures; its error line starts a line. Never search the whole output:
    # clientdata is free text and can contain "Error:" (measured: it did, on the intake flow).
    err_line = any(ln.startswith("Error:") for ln in (p.stdout + "\n" + p.stderr).splitlines())
    if p.returncode != 0 or err_line:
        raise ReadError(f"pac env fetch failed (exit {p.returncode}): {(p.stdout + p.stderr).strip()[:400]}")
    return p.stdout


def workflow_query(ids: list[str]) -> str:
    vals = "".join(f"<value>{i}</value>" for i in ids)
    return ('<fetch><entity name="workflow"><attribute name="workflowid"/><attribute name="name"/>'
            '<attribute name="modifiedon"/><attribute name="clientdata"/><filter>'
            f'<condition attribute="workflowid" operator="in">{vals}</condition></filter></entity></fetch>')


def import_query(solution: str) -> str:
    return ('<fetch><entity name="importjob"><attribute name="solutionname"/>'
            '<attribute name="completedon"/><attribute name="createdon"/><attribute name="progress"/>'
            f'<filter><condition attribute="solutionname" operator="eq" value="{solution}"/></filter>'
            '</entity></fetch>')


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--env", help="environment label for the report (dev, tst_acc, prd)")
    ap.add_argument("--environment", help="pac --environment value; default is the active profile")
    ap.add_argument("--solution", default=DEFAULT_SOLUTION)
    ap.add_argument("--workflows-dir", type=Path, default=DEFAULT_WORKFLOWS)
    ap.add_argument("--imported-at", help="import completion, UTC ISO 8601 (default: latest importjob)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.env:
        ap.error("--env is required")
    try:
        source = source_flows(a.workflows_dir)
        if not source:
            raise ReadError(f"no *.data.xml under {a.workflows_dir}")
        if a.imported_at:
            imported_at = datetime.fromisoformat(a.imported_at)
        else:
            imported_at = parse_latest_import(run_fetch(import_query(a.solution), a.environment))
            if imported_at is None:
                raise ReadError(f"no completed importjob for {a.solution}; pass --imported-at")
        live = parse_workflow_table(run_fetch(workflow_query(sorted(source)), a.environment))
    except (ReadError, OSError, ValueError, KeyError, ET.ParseError) as e:
        print(f"verify-live-flow-definitions: READ FAILED ({e})", file=sys.stderr)
        return 2
    findings = compare(source, live, imported_at)
    print(f"verify-live-flow-definitions [{a.env}]: {len(source)} flows in source, {len(live)} read live; "
          f"import completed {imported_at:%Y-%m-%d %H:%M} UTC (modifiedon has minute resolution; "
          f"a write within the import's own minute is not detectable)")
    for f in findings:
        print(f"  {f}")
    if findings:
        print(f"FAIL: {len(findings)} finding(s)")
        return 1
    print("PASS: every flow's live definition matches source and none was modified after the import")
    return 0


def selftest() -> int:
    d_ok = {"actions": {"A": {"inputs": {"item": {"x": 1}}}}}
    d_bad = {"actions": {"A": {"inputs": {}}}}
    cr = {"c": {"api": {"name": "n"}}}
    wid = "8f1c2a44-1001-4b7a-9e21-0a1b2c3d4e01"
    src = {wid: {"name": "F", "file": "F.json", "properties": {"connectionReferences": cr, "definition": d_ok}}}

    def table(defn, mod, refs=cr):
        cd = json.dumps({"properties": {"connectionReferences": refs, "definition": defn}}, indent=None)
        return f"h\n\n{wid} F | Intake {mod} {cd}\n"

    imp = datetime(2026, 9, 29, 19, 34)
    cases = [
        ("clean", table(d_ok, "9/29/2026 7:34 PM"), 0),
        ("clean, key order differs", table({"actions": {"A": {"inputs": {"item": {"x": 1}}}}}, "9/29/2026 7:20 PM"), 0),
        ("content differs", table(d_bad, "9/29/2026 7:34 PM"), 1),
        ("modified after import", table(d_ok, "9/29/2026 7:35 PM"), 1),
        ("connectionReferences differ", table(d_ok, "9/29/2026 7:34 PM", {"c": {}}), 1),
        ("row missing", "h\n\n", 1),
    ]
    bad = 0
    for name, text, want in cases:
        got = 1 if compare(src, parse_workflow_table(text), imp) else 0
        ok = got == want
        bad += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {name} (want {want}, got {got})")
    jobs = ("solutionname completedon createdon progress importjobid\n"
            "S 9/25/2026 2:10 PM  9/25/2026 2:06 PM  100.00 7f88444c-00d3-4501-8e53-da4804ef5564\n"
            "S 9/29/2026 7:34 PM  9/29/2026 7:30 PM  100.00 4814235d-ef64-42f2-9e1a-3e878c5a4fa3\n"
            "S 9/30/2026 9:00 AM  9/30/2026 8:59 AM  84.88  578f74a4-a41f-438c-a177-7daf5ae683d9\n")
    ok = parse_latest_import(jobs) == datetime(2026, 9, 29, 19, 34)
    bad += not ok
    print(f"  {'ok  ' if ok else 'FAIL'} latest import ignores incomplete jobs")
    ok = parse_ts("9/29/2026 12:05 AM") == datetime(2026, 9, 29, 0, 5)
    bad += not ok
    print(f"  {'ok  ' if ok else 'FAIL'} 12 AM parses as 00:xx")
    print("selftest: " + ("FAILED" if bad else "passed"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
