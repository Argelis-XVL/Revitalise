#!/usr/bin/env python3
"""A shipped <Description> saying a column is "written by nothing" must be TRUE. Stdlib only.

WHY THIS EXISTS
---------------
`IMP-0434`, a blocker. ADR-038 moved `rev_status`, `rev_resultjson` and `rev_computedon` from
`rev_roundstatisticsrequest` to `rev_roundstatisticsresult`, and — per TAD 3.9.2, because a live
metadata delete was out of scope — **retained the superseded columns on the request table rather
than deleting them.** Each retained column ships a `<Description>` reading:

    UNUSED FROM REVISION 5 (ADR-038). ... Written by nothing and read by nothing.

`provisioning/dataverse/seed-round-statistics-test-data.ps1` went on PATCHing all three onto the
request table for three days. **The PATCH succeeded**, the script printed `CREATED`, exited 0, and
the charts it exists to populate stayed empty. A retained column is a live write target, not a
comment: every gate in this repository passed over it because both tables and all six columns
genuinely exist.

So the sentence is a factual claim about writers that nothing checked. This gate checks it.

`IMP-0438` is the second instance, found by running this gate against the corpus **before** wiring
it — `seed-round-statistics-request.ps1` writes `rev_status` to the request table, which is a
different script from the one `IMP-0434` reports. One instance is a defect; two in one feature in
three days is the reason this is a gate and not a knowledge line.

WHAT IT CHECKS
--------------
For every `<attribute>` in `Entities/*/Entity.xml` whose `<Description>` carries
`UNUSED FROM REVISION <n>`, take the owning entity's `<EntitySetName>` and the attribute's
`<LogicalName>`. Then any `provisioning/**/*.ps1` or `Workflows/*.json` that references **both**,
outside comments, is a finding.

WHY COMMENTS ARE STRIPPED, AND WHAT IT COST TO LEARN
----------------------------------------------------
Measured before wiring, per `agents/improvement-agent.md`. The first implementation stripped only
PowerShell LINE comments (`#` to end of line) and measured **3 findings, 1 true, 2 false** across
38 files — 67% wrong on first contact. Both false positives were `rev_resultjson` and
`rev_computedon` at line 24 of `seed-round-statistics-request.ps1`, inside the `<# .SYNOPSIS #>`
header that explains why those two columns are *not* written. **Every** `.ps1` here opens with such
a header naming the very entity sets and columns this gate looks for, so handling the BLOCK comment
form is not a nicety. Re-measured with it: **1 finding, 1 true, 0 false.**

RESIDUAL, stated because every promotion leaves one
---------------------------------------------------
Co-occurrence is resolved within one FILE, not one statement. A script that legitimately references
the old entity set and, separately, a superseded column name in live code would be a false
positive. None exists in this repository today; statement-level attribution needs a PowerShell
parser, which is not a one-second gate. And the READ half of the same claim — "read by nothing" —
is NOT checked here: it has one recorded instance (`IMP-0438`) and would need the app's own select
lists, so it waits for a second instance rather than being guessed at now.

EXIT CODES: 0 clean, or every finding baselined; 1 findings, or a marker with no resolvable entity
set, or zero Entity.xml files parsed (the `IMP-0007` shape — a gate reporting OK over nothing);
2 usage error.
"""
from __future__ import annotations

import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib.gate_baseline import BaselineError, load_baselines  # noqa: E402
from lib.tracked_paths import (  # noqa: E402
    IgnoreCheckUnavailable, describe_untracked, untracked_paths,
)

GATE = "superseded-column-writers"
MARKER = re.compile(r"UNUSED FROM REVISION\s+\d+", re.I)

# GATE-INPUT-TRACKING: reads the WORKING TREE on purpose. This is an authoring-time gate and its
# only inputs today are UNTRACKED — the three markers live in an uncommitted Entity.xml — so a
# tracked-only rule would give it zero inputs and it would fail on its own no-inputs branch.
# See scripts/lib/tracked_paths.py, "TWO INPUT UNIVERSES" (IMP-0437).


def strip_ps_comments(text: str) -> list[tuple[int, str]]:
    """(lineno, code-only) per line, for PowerShell.

    Handles BOTH comment forms. The line form (`#` outside quotes, to end of line) and the BLOCK
    form (`<# ... #>`, spanning lines). Omitting the block form measured 2 false positives out of
    3 findings on this corpus — see the module docstring.
    """
    out: list[tuple[int, str]] = []
    in_block = False
    for n, line in enumerate(text.splitlines(), 1):
        code: list[str] = []
        in_s = in_d = False
        i = 0
        while i < len(line):
            two = line[i:i + 2]
            if in_block:
                if two == "#>":
                    in_block = False
                    i += 2
                    continue
                i += 1
                continue
            ch = line[i]
            if ch == "'" and not in_d:
                in_s = not in_s
            elif ch == '"' and not in_s:
                in_d = not in_d
            elif not in_s and not in_d and two == "<#":
                in_block = True
                i += 2
                continue
            elif ch == "#" and not in_s and not in_d:
                break
            code.append(ch)
            i += 1
        out.append((n, "".join(code)))
    return out


def code_lines(path: Path) -> list[tuple[int, str]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix == ".ps1":
        return strip_ps_comments(text)
    return list(enumerate(text.splitlines(), 1))  # JSON has no comment syntax


def superseded_columns(sol_root: Path) -> tuple[list[tuple[str, str, str]], list[str]]:
    """([(entity_set, column, entity_dir)], errors) for every attribute carrying the marker."""
    found: list[tuple[str, str, str]] = []
    errors: list[str] = []
    for ent in sorted((sol_root / "Entities").glob("*/Entity.xml")):
        try:
            root = ET.parse(ent).getroot()
        except ET.ParseError as exc:
            errors.append(f"{ent}: unparseable ({exc})")
            continue
        marked = []
        for attr in root.iter("attribute"):
            if any(MARKER.search(d.get("description", "")) for d in attr.iter("Description")):
                ln = attr.find("LogicalName")
                name = (ln.text or "").strip() if ln is not None else (
                    attr.get("PhysicalName") or "")
                if name:
                    marked.append(name)
        if not marked:
            continue
        set_el = root.find(".//EntitySetName")
        entity_set = (set_el.text or "").strip() if set_el is not None else ""
        if not entity_set:
            # Never skip silently: a marker we cannot resolve is the one we most need to report.
            errors.append(
                f"{ent.parent.name}: {len(marked)} column(s) carry the UNUSED FROM REVISION "
                f"marker but Entity.xml declares no <EntitySetName>, so no writer can be checked "
                f"for them: {', '.join(sorted(marked))}")
            continue
        for name in sorted(marked):
            found.append((entity_set, name, ent.parent.name))
    return found, errors


def scan(repo_root: Path) -> tuple[list[tuple[str, str, str, str, list[int], list[int]]],
                                   list[str], int, int, set | None, list[str]]:
    """(findings, errors, markers_examined, files_scanned, untracked, scope_note)."""
    sol_roots = sorted(p for p in (repo_root / "src/solutions").glob("*")
                       if (p / "Entities").is_dir())
    marked: list[tuple[str, str, str]] = []
    errors: list[str] = []
    for sr in sol_roots:
        m, e = superseded_columns(sr)
        marked += m
        errors += e

    targets = sorted((repo_root / "provisioning").glob("**/*.ps1"))
    for sr in sol_roots:
        targets += sorted((sr / "Workflows").glob("*.json"))

    findings = []
    for f in targets:
        lines = code_lines(f)
        for entity_set, col, entity_dir in marked:
            set_hits = [n for n, c in lines if entity_set in c]
            if not set_hits:
                continue
            col_hits = [n for n, c in lines if re.search(rf"(?<![\w-]){re.escape(col)}(?![\w-])", c)]
            if col_hits:
                rel = f.relative_to(repo_root).as_posix()
                findings.append((rel, entity_set, col, entity_dir, set_hits[:3], col_hits[:3]))

    # ── THE SCOPE LINE (IMP-0447, second instance of the property after IMP-0445) ──
    # This gate's verdict was quoted as evidence in a blocker finding against a file that was
    # mid-edit — a deliberate 90-second mutant inside another dispatch's mutation-falsification
    # run — and the verdict said nothing about WHICH UNIVERSE it had measured. It reads the
    # working tree, and all three of its markers live in an UNTRACKED Entity.xml, so its inputs
    # are not in the commit at all.
    #
    # NO --committed-only FLAG, and that is measured, not an omission. `git ls-files` over both
    # round-statistics table directories returns ZERO tracked files, so a commit-scoped run
    # would examine 0 marked columns — and this gate correctly fails on no inputs (IMP-0007),
    # so the flag would be a switch that can only break it. Review 37 §6d measured the same
    # fact for verify-forms-and-views-reachable.py one review earlier and concluded: report the
    # split, do not narrow the inputs.
    inputs = [p for p in targets]
    for sr in sol_roots:
        inputs += sorted((sr / "Entities").glob("*/Entity.xml"))
    try:
        untracked = untracked_paths(inputs, repo_root)
        scope_note = describe_untracked(sorted(untracked), repo_root)
    except IgnoreCheckUnavailable as exc:                 # git absent, or not a work tree
        untracked, scope_note = None, [str(exc)]
    return findings, errors, len(marked), len(targets), untracked, scope_note


def main(argv: list[str]) -> int:
    if len(argv) > 2 or (len(argv) == 2 and argv[1] in ("-h", "--help")):
        print(f"Usage: {argv[0]} [repo-root]", file=sys.stderr)
        return 2
    repo_root = Path(argv[1]).resolve() if len(argv) == 2 else Path(__file__).resolve().parent.parent

    if not (repo_root / "src/solutions").is_dir():
        print(f"{GATE}: FAILED — no src/solutions under {repo_root}. A gate with no inputs must "
              "fail, never report OK (IMP-0007).", file=sys.stderr)
        return 1

    try:
        baseline = load_baselines(repo_root, GATE)
    except BaselineError as exc:
        print(f"{GATE}: FAILED — {exc}", file=sys.stderr)
        return 1

    findings, errors, markers, files_scanned, untracked, scope_note = scan(repo_root)

    if untracked is None:
        scope = ("scope: WORKING TREE — tracked/untracked split UNAVAILABLE "
                 f"({'; '.join(scope_note)}), so this verdict may differ from CI and nothing "
                 "here can say whether it does. Do not transcribe these counts.")
    elif untracked:
        scope = (f"scope: WORKING TREE — {len(untracked)} UNTRACKED input(s) read as if "
                 "delivered, so this verdict may differ from CI and describes an editable tree, "
                 "not a commit. Re-read the file before quoting this verdict as evidence: a "
                 "mutation-falsification run leaves a provisioning script deliberately broken "
                 "for the length of a test (IMP-0447). Untracked: "
                 f"{'; '.join(scope_note)}")
    else:
        scope = ("scope: WORKING TREE — every input is tracked, so this verdict matches the "
                 "commit.")

    if not markers and not errors:
        print(f"{GATE}: OK — no column in any Entity.xml carries an 'UNUSED FROM REVISION' "
              f"marker, so there is no claim to check. {files_scanned} writer candidate(s) "
              f"scanned. {scope}")
        return 0

    unbaselined = 0
    for rel, entity_set, col, entity_dir, set_hits, col_hits in findings:
        key = f"{rel}::{entity_set}.{col}"
        cite = baseline.cite(key)
        label = "BASELINED" if cite else "ERROR"
        stream = sys.stdout if cite else sys.stderr
        if not cite:
            unbaselined += 1
        print(f"{label}: {rel} references entity set '{entity_set}' (line "
              f"{', '.join(map(str, set_hits))}) and superseded column '{col}' (line "
              f"{', '.join(map(str, col_hits))}), but {entity_dir}/Entity.xml ships a "
              f"<Description> saying '{col}' is written by nothing. A RETAINED column is a live "
              f"write target: either re-point the writer at the current table, or correct the "
              f"<Description> — it is a factual claim (IMP-0434, IMP-0438).{cite}", file=stream)

    for err in errors:
        print(f"ERROR: {err}", file=sys.stderr)

    total_bad = unbaselined + len(errors)
    tail = (f"{markers} marked column(s) examined across {files_scanned} writer candidate(s); "
            f"{len(findings)} finding(s), {len(findings) - unbaselined} baselined. {scope}")
    if total_bad:
        print(f"\n{GATE}: FAILED — {tail}", file=sys.stderr)
        return 1
    print(f"{GATE}: OK — {tail}")
    return 0


def selftest() -> int:
    """Proves the gate CAN fail, on the real defect shape, and CAN be quiet when it should be."""
    import tempfile

    failed = 0

    def check(why: str, ok: bool, detail: str) -> None:
        nonlocal failed
        print(f"  {'ok  ' if ok else 'FAIL'}  {why}: {detail}")
        failed += 0 if ok else 1

    ENTITY = """<?xml version="1.0" encoding="utf-8"?>
<Entity><Name>rev_thing</Name><attributes>
  <attribute PhysicalName="rev_status">
    <Name>rev_status</Name><LogicalName>rev_status</LogicalName>
    <Descriptions><Description description="UNUSED FROM REVISION 5 (ADR-038). Written by nothing
      and read by nothing." languagecode="1033" /></Descriptions>
  </attribute>
  <attribute PhysicalName="rev_live">
    <Name>rev_live</Name><LogicalName>rev_live</LogicalName>
    <Descriptions><Description description="A normal column." languagecode="1033" /></Descriptions>
  </attribute>
</attributes><EntitySetName>rev_things</EntitySetName></Entity>
"""

    def build(root: Path, script_body: str, entity: str = ENTITY) -> None:
        ent = root / "src/solutions/Sol/Entities/rev_thing"
        ent.mkdir(parents=True, exist_ok=True)
        (ent / "Entity.xml").write_text(entity, encoding="utf-8")
        (root / "src/solutions/Sol/Workflows").mkdir(parents=True, exist_ok=True)
        prov = root / "provisioning/dataverse"
        prov.mkdir(parents=True, exist_ok=True)
        (prov / "seed.ps1").write_text(script_body, encoding="utf-8")

    REAL_DEFECT = """$keyPath = 'rev_things(rev_name=''CURRENT'')'
Invoke-DataverseApi -Method PATCH -Path $keyPath -Body @{ rev_name = 'x'; rev_status = 2 }
"""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        build(root, REAL_DEFECT)
        rc = main(["x", str(root)])
        check("the REAL defect shape FAILS the gate (can-it-fail, on IMP-0434's own shape)",
              rc == 1, f"exit={rc}")

    # The measured false-positive shape: both names present, but only inside a <# #> header.
    BLOCK_COMMENT_ONLY = """<#
.SYNOPSIS
    Seeds rev_things(rev_name='CURRENT'). rev_status is deliberately NOT written here.
#>
Invoke-DataverseApi -Method PATCH -Path 'rev_things(rev_name=''CURRENT'')' -Body @{ rev_name = 'x' }
"""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        build(root, BLOCK_COMMENT_ONLY)
        rc = main(["x", str(root)])
        check("a mention only inside a <# #> BLOCK comment is NOT a finding (the 2 measured "
              "false positives)", rc == 0, f"exit={rc}")

    LINE_COMMENT_ONLY = """# rev_status is not written to rev_things any more.
Invoke-DataverseApi -Method PATCH -Path 'rev_things(rev_name=''x'')' -Body @{ rev_name = 'x' }
"""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        build(root, LINE_COMMENT_ONLY)
        rc = main(["x", str(root)])
        check("a mention only inside a # LINE comment is NOT a finding", rc == 0, f"exit={rc}")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        build(root, "Invoke-DataverseApi -Path 'rev_things' -Body @{ rev_live = 1 }\n")
        rc = main(["x", str(root)])
        check("writing an UNMARKED column on the same table is NOT a finding", rc == 0,
              f"exit={rc}")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        build(root, "Invoke-DataverseApi -Path 'rev_others' -Body @{ rev_status = 2 }\n")
        rc = main(["x", str(root)])
        check("writing the marked column to a DIFFERENT entity set is NOT a finding "
              "(that is the fix, not the defect)", rc == 0, f"exit={rc}")

    NO_SET = ENTITY.replace("<EntitySetName>rev_things</EntitySetName>", "")
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        build(root, REAL_DEFECT, entity=NO_SET)
        rc = main(["x", str(root)])
        check("a marker whose entity set cannot be resolved FAILS rather than being skipped "
              "silently", rc == 1, f"exit={rc}")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        build(root, REAL_DEFECT)
        (root / "config").mkdir(parents=True, exist_ok=True)
        (root / "config/gate-baselines.json").write_text(json.dumps({"baselines": [{
            "gate": GATE, "matches": "provisioning/dataverse/seed.ps1::rev_things.rev_status",
            "reason": "r", "owner": "lead-agent", "clears_when": "c",
            "expires": "2099-01-01", "finding": "IMP-0438"}]}), encoding="utf-8")
        rc = main(["x", str(root)])
        check("a BASELINED finding does not fail the gate", rc == 0, f"exit={rc}")
        (root / "config/gate-baselines.json").write_text(json.dumps({"baselines": [{
            "gate": GATE, "matches": "provisioning/dataverse/seed.ps1::rev_things.rev_status",
            "reason": "r", "owner": "lead-agent", "clears_when": "c",
            "expires": "2020-01-01", "finding": "IMP-0438"}]}), encoding="utf-8")
        rc = main(["x", str(root)])
        check("an EXPIRED baseline FAILS — the suppression is dated, not permanent", rc == 1,
              f"exit={rc}")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "src/solutions/Sol/Entities").mkdir(parents=True, exist_ok=True)
        rc = main(["x", str(root)])
        check("no markers anywhere reports OK and says there was no claim to check", rc == 0,
              f"exit={rc}")

    with tempfile.TemporaryDirectory() as tmp:
        rc = main(["x", str(Path(tmp))])
        check("no src/solutions at all FAILS rather than reporting OK over nothing (IMP-0007)",
              rc == 1, f"exit={rc}")

    print(f"\nSELFTEST: {'PASS' if not failed else f'FAILED — {failed} case(s)'}")
    return 1 if failed else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv[1:]:
        sys.exit(selftest())
    sys.exit(main(sys.argv))
