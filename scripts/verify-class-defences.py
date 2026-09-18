#!/usr/bin/env python3
"""Assert that every recorded class defence in logs/class-defences.json still exists.

    python3 scripts/verify-class-defences.py
    python3 scripts/verify-class-defences.py --selftest

WHY THIS EXISTS (IMP-0766). `logs/class-defences.json` records which recurring failure classes
already have a general gate, and `scripts/generate-known-failure-modes.py` renders it into the
digest's recurring-class table as a `Defended by` column. Agents read that column at activation
and skip proposing a gate because one is named there.

Nothing validated that record. The generator is deliberately forgiving — a malformed or missing
file yields `{}` rather than failing, so an optional annotation can never block a digest
regeneration. **That forgiveness is correct for MALFORMED input and is the wrong answer for STALE
input.** A well-formed row naming a script that was since renamed, retired or deleted parses
perfectly and renders confidently, and the digest goes on telling every agent the class is
defended. A read path that says a control exists when it does not is worse than no column at all:
the empty cell at least sends the reader to grep.

So the rule this gate enforces is the one the record's own README states — *"'proves_green' is a
command, not a description. Anyone can run it to check the claim is still true"* — mechanised, so
that "anyone" does not have to be someone who happened to be suspicious.

WHAT IT DOES **NOT** DO, deliberately:

  * **It does not RUN `proves_green`.** That command is a full build gate over the real corpus;
    running it here would make this cheap check as slow as the thing it annotates, and a red
    `proves_green` is a finding about that gate's corpus, not about this record. It asserts the
    command's script exists and is invocable — that the recorded defence has not evaporated.
  * **It does not check that the defence is ADEQUATE.** Whether `property` truly describes what
    the gate defends is a judgement no parser makes. This gate checks existence, not truth.
  * **It does not require every recurring class to have a row.** The record is opt-in and
    under-claims by construction; that asymmetry is the safe direction and is not a defect.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

DEFENCES = Path("logs/class-defences.json")

# Every key a row must carry. Each one is load-bearing in the rendered cell or in the audit trail
# behind it, so a row missing one renders a defence nobody can check.
REQUIRED = ("class", "property", "defended_by", "proves_green", "wired_at", "since",
            "imp_ids", "recorded_by")

# A path to a repository script, wherever it appears in prose: `scripts/verify-thing.py`.
SCRIPT_REF = re.compile(r"\bscripts/([A-Za-z0-9_.-]+\.py)\b")

# A function name quoted in `defended_by`, in either of the two forms the existing rows use:
# "check 11 (check_settings_content)" and "check_blocked_on_staleness, BLOCKED_ON_MAX_AGE_DAYS".
# Restricted to snake_case identifiers of two or more parts so ordinary prose words never match.
SYMBOL = re.compile(r"\b([a-z][a-z0-9]*(?:_[a-z0-9]+)+|[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+)\b")

# A build-step name in `wired_at`: "config/x-build.yml (pipeline-config-preflight)".
WIRED = re.compile(r"^(?P<file>[^\s(]+)(?:\s*\((?P<step>[^)]+)\))?\s*$")

IMP_ID = re.compile(r"^IMP-\d{4}$")


def known_imp_ids(log: Path) -> set[str]:
    """Every id in the improvement log. An unreadable log yields an empty set, which disables
    the imp_ids check rather than failing every row on an unrelated problem."""
    out: set[str] = set()
    try:
        for line in log.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                out.add(json.loads(line)["id"])
            except (ValueError, KeyError, TypeError):
                continue
    except OSError:
        return set()
    return out


def check(root: Path) -> tuple[int, list[str], list[str]]:
    errors: list[str] = []
    notes: list[str] = []
    path = root / DEFENCES

    if not path.exists():
        notes.append(f"  {DEFENCES} is absent — nothing recorded, nothing to verify. The record "
                     f"is opt-in; its absence is not a defect.")
        return 0, errors, notes

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        errors.append(
            f"  MALFORMED - {DEFENCES} is not valid JSON ({exc}). The digest generator swallows "
            f"this and renders an EMPTY 'Defended by' column for every class, which reads as "
            f"'no defence recorded' — so a syntax error here silently withdraws every recorded "
            f"defence at once. Fix the JSON.")
        return 1, errors, notes

    rows = data.get("defences")
    if not isinstance(rows, list):
        errors.append(f"  MALFORMED - {DEFENCES} has no 'defences' list. The generator reads that "
                      f"key and nothing else; without it every recorded defence is invisible.")
        return 1, errors, notes

    imp_ids = known_imp_ids(root / "logs" / "improvement-log.jsonl")
    seen: dict[str, int] = {}
    checked_refs = 0

    for n, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            errors.append(f"  ROW {n} is not an object.")
            continue
        label = row.get("class") if isinstance(row.get("class"), str) else f"row {n}"

        missing = [k for k in REQUIRED if not row.get(k)]
        if missing:
            errors.append(
                f"  INCOMPLETE ROW - '{label}' is missing {', '.join(missing)}. Every one of "
                f"{', '.join(REQUIRED)} is load-bearing: 'property' is what stops a class name "
                f"being read as fully defended when only one of its mechanisms is, and "
                f"'proves_green' is what lets the next reader check the claim instead of "
                f"trusting it.")

        # ── a class may be recorded once. Two rows for one class means the generator renders
        #    whichever it read last, silently discarding the other. ──
        if isinstance(row.get("class"), str):
            if row["class"] in seen:
                errors.append(
                    f"  RECORDED TWICE - class '{row['class']}' has rows {seen[row['class']]} "
                    f"and {n}. load_class_defences() builds a dict keyed by class, so the later "
                    f"row wins and the earlier one is discarded WITHOUT WARNING — including its "
                    f"'not_covered' clause, which is the half that stops over-claiming.")
            else:
                seen[row["class"]] = n

        # ── every script named anywhere in the row must exist ──
        for field in ("defended_by", "proves_green", "wired_at"):
            value = row.get(field)
            if not isinstance(value, str):
                continue
            for script in SCRIPT_REF.findall(value):
                checked_refs += 1
                if not (root / "scripts" / script).exists():
                    errors.append(
                        f"  DEFENCE NAMES A MISSING SCRIPT - '{label}'.{field} names "
                        f"scripts/{script}, which does not exist. The digest is telling every "
                        f"agent that reads it at activation that this class is defended by a "
                        f"gate that is not there. Either restore the gate, or remove the row so "
                        f"the cell goes back to honestly empty.")

        # ── a symbol quoted in defended_by must still appear in the script it names ──
        defended_by = row.get("defended_by")
        if isinstance(defended_by, str):
            scripts = [s for s in SCRIPT_REF.findall(defended_by)
                       if (root / "scripts" / s).exists()]
            if scripts:
                blob = "\n".join((root / "scripts" / s).read_text(encoding="utf-8", errors="replace")
                                 for s in scripts)
                for sym in set(SYMBOL.findall(defended_by)):
                    # Only assert on symbols that look like code, not prose compounds. A symbol
                    # this gate cannot find anywhere in the named scripts AND that appears in no
                    # other field is the renamed-function case IMP-0766 describes.
                    if sym.endswith(".py") or sym in {"not_covered", "proves_green", "wired_at"}:
                        continue
                    checked_refs += 1
                    if sym not in blob:
                        errors.append(
                            f"  DEFENCE NAMES A MISSING SYMBOL - '{label}'.defended_by names "
                            f"`{sym}`, which appears in none of {', '.join(scripts)}. A gate "
                            f"whose named check was renamed still exists as a FILE, so the "
                            f"file-existence check above passes while the specific defence "
                            f"recorded here is gone. Re-read the script and re-word the row.")

        # ── wired_at must name a real config, and the step it claims must be in it ──
        wired_at = row.get("wired_at")
        if isinstance(wired_at, str):
            m = WIRED.match(wired_at.strip())
            if m:
                cfg = root / m.group("file")
                if not cfg.exists():
                    errors.append(
                        f"  WIRED-AT NAMES A MISSING FILE - '{label}'.wired_at names "
                        f"{m.group('file')}, which does not exist. 'Wired' is the claim that the "
                        f"gate RUNS; a config that is gone cannot be running anything.")
                elif m.group("step"):
                    checked_refs += 1
                    if m.group("step") not in cfg.read_text(encoding="utf-8"):
                        errors.append(
                            f"  STEP NOT IN CONFIG - '{label}'.wired_at claims step "
                            f"'{m.group('step')}' in {m.group('file')}, and that config does not "
                            f"contain it. An unwired gate is one nobody runs, so the recorded "
                            f"defence is a gate that exists and never fires — which is the "
                            f"'gate-cannot-fail' shape, dressed as reassurance.")

        # ── the ids justifying the row must be real findings ──
        ids = row.get("imp_ids")
        if isinstance(ids, list) and imp_ids:
            for i in ids:
                if not (isinstance(i, str) and IMP_ID.match(i)):
                    errors.append(f"  MALFORMED IMP ID - '{label}'.imp_ids contains {i!r}.")
                elif i not in imp_ids:
                    errors.append(
                        f"  DEFENCE CITES AN UNKNOWN FINDING - '{label}'.imp_ids names {i}, "
                        f"which is in no entry of logs/improvement-log.jsonl. A defence with no "
                        f"finding behind it is somebody's opinion.")

        # ── the documents that recorded it must exist ──
        for field in ("since", "recorded_by"):
            value = row.get(field)
            if isinstance(value, str) and value.startswith("docs/"):
                checked_refs += 1
                if not (root / value).exists():
                    errors.append(
                        f"  DEFENCE CITES A MISSING DOCUMENT - '{label}'.{field} names {value}, "
                        f"which does not exist. That document is the audit trail for why the "
                        f"class is considered defended.")

    notes.append(f"  {len(rows)} recorded defence(s), {checked_refs} reference(s) resolved "
                 f"(scripts, symbols, build steps, review documents)")
    return (1 if errors else 0), errors, notes


# ── selftest ──────────────────────────────────────────────────────────────────────────────
#
# Each fixture is a whole fake repository root, because every check in this gate is a claim that
# something ELSEWHERE in the tree exists. A fixture that only supplied the JSON would test the
# parser and nothing else — and the parser is not where IMP-0766's failure lives.

_GATE = "def check_settings_content():\n    MAX_AGE = 1\n"
_CFG = "steps:\n  - name: pipeline-config-preflight\n    command: true\n"
_LOG = '{"id": "IMP-0145"}\n{"id": "IMP-0147"}\n'


def _row(**over) -> dict:
    base = {
        "class": "config-placeholder-known-but-not-fixed",
        "property": "an unresolved token",
        "defended_by": "scripts/verify-pipeline-config.py check 11 (check_settings_content)",
        "proves_green": "python3 scripts/verify-pipeline-config.py config/x-build.yml",
        "wired_at": "config/x-build.yml (pipeline-config-preflight)",
        "since": "docs/improvements/r.md",
        "imp_ids": ["IMP-0145"],
        "recorded_by": "docs/improvements/r.md",
    }
    base.update(over)
    return base


_TREE = {
    "scripts/verify-pipeline-config.py": _GATE,
    "config/x-build.yml": _CFG,
    "docs/improvements/r.md": "# r\n",
    "logs/improvement-log.jsonl": _LOG,
}

_CASES: dict[str, tuple[dict, list, bool, str]] = {
    "a-complete-row-passes": (_TREE, [_row()], False, "1 recorded defence"),
    "absent-file-is-not-a-defect": ({}, None, False, "is absent"),
    "malformed-json-fails-loudly": ({}, "NOT JSON", True, "MALFORMED"),
    "missing-script-is-caught": (
        {k: v for k, v in _TREE.items() if k != "scripts/verify-pipeline-config.py"},
        [_row()], True, "DEFENCE NAMES A MISSING SCRIPT"),
    "renamed-function-is-caught": (
        {**_TREE, "scripts/verify-pipeline-config.py": "def check_renamed():\n    pass\n"},
        [_row()], True, "DEFENCE NAMES A MISSING SYMBOL"),
    "unwired-step-is-caught": (
        {**_TREE, "config/x-build.yml": "steps:\n  - name: something-else\n"},
        [_row()], True, "STEP NOT IN CONFIG"),
    "missing-config-is-caught": (
        {k: v for k, v in _TREE.items() if k != "config/x-build.yml"},
        [_row()], True, "WIRED-AT NAMES A MISSING FILE"),
    "unknown-finding-is-caught": (
        _TREE, [_row(imp_ids=["IMP-9999"])], True, "DEFENCE CITES AN UNKNOWN FINDING"),
    "missing-document-is-caught": (
        _TREE, [_row(recorded_by="docs/improvements/gone.md")], True,
        "DEFENCE CITES A MISSING DOCUMENT"),
    "incomplete-row-is-caught": (
        _TREE, [_row(property="")], True, "INCOMPLETE ROW"),
    "duplicate-class-is-caught": (
        _TREE, [_row(), _row(property="a different mechanism entirely")], True,
        "RECORDED TWICE"),
}


def selftest() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        for name, (files, defences, expect_fail, want) in _CASES.items():
            root = Path(tmp) / name
            for rel, body in files.items():
                p = root / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(body, encoding="utf-8")
            if defences is not None:
                p = root / DEFENCES
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(defences if isinstance(defences, str)
                             else json.dumps({"defences": defences}), encoding="utf-8")
            root.mkdir(parents=True, exist_ok=True)
            rc, errors, notes = check(root)
            text = "\n".join(errors + notes)
            ok = ((rc != 0) if expect_fail else (rc == 0)) and want in text
            print(f"  {'OK' if ok else 'DID NOT BEHAVE':16} {name} → exit {rc}, "
                  f"{len(errors)} error(s)")
            if not ok:
                for line in errors + notes:
                    print(f"                   {line}")
                failures.append(name)
    if failures:
        print(f"\nverify-class-defences: SELFTEST FAILED — {', '.join(failures)}", file=sys.stderr)
        return 1
    print(f"\nverify-class-defences: SELFTEST OK — {len(_CASES)} fixtures, including the two "
          f"that exist BECAUSE the file-exists check alone would pass them: a renamed function "
          f"inside a surviving gate, and a step removed from a surviving config.")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--warn-only", action="store_true",
                   help="report and exit 0 — what would make the build step SOFT")
    p.add_argument("--selftest", action="store_true")
    try:
        args = p.parse_args(argv)
    except SystemExit:
        return 2

    if args.selftest:
        return selftest()

    rc, errors, notes = check(args.root)
    if rc:
        label = "WARN" if args.warn_only else "FAILED"
        print(f"class-defences: {label}\n" + "\n".join(errors + notes), file=sys.stderr)
        return 0 if args.warn_only else rc
    print("class-defences: OK\n" + "\n".join(notes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
