#!/usr/bin/env python3
"""Fail when an existing Dataverse attribute's data type changes in source (C-TECH-080).

A Dataverse column's data type cannot change once the column exists in an environment. Solution
import rejects it ("Attribute rev_helperrelationship is a Picklist, but a String type was
specified", 2026-08-16), and Microsoft documents that a column's data type cannot be changed after
the column is saved. Every measured retype on this project needed a transitional import, a live
DELETE and a recreate (knowledge/technology/dataverse.md, "Changing a Column's Data Type After It
Has Shipped"). A design then specified eleven more as ordinary import edits (IMP-0934).

This gate compares every attribute's <Type> in Entities/*/Entity.xml against a COMMITTED lock file
recording each attribute's type. It deliberately does not read git history (CI checks out at depth
1, so a history comparison would compare nothing) and does not read build manifests (they record
no attribute types, and most were built from a dirty tree).

LOCK SHAPE (config/attribute-type-lock.json):
    {"attributes": {"<entity>.<logicalname>": "<type>", ...},
     "planned_retypes": [{"attribute": "<entity>.<logicalname>", "from": "<type>", "to": "<type>",
                          "route": "new-column" | "delete-and-recreate" | "pre-ship",
                          "live_in": ["dev", ...], "authorised_by": "<name>", "date": "YYYY-MM-DD",
                          "procedure": "knowledge/technology/dataverse.md"}],
     "applied_retypes": [ ...declarations moved here by --update once the lock records them... ]}

OUTCOMES:
    FAIL  a recorded attribute's type differs from the lock and no planned_retypes entry declares it
    FAIL  a planned_retypes entry whose `from` no longer matches the lock (a stale plan is not a plan)
    FAIL  a planned_retypes entry missing a field, or with an unknown route
    WARN  a recorded attribute's type differs and a matching declaration exists (prints the route)
    NOTE  attributes in source not yet in the lock (count + the --update command)
    NOTE  attributes in the lock no longer in source

The entity key is the Entities/<folder> name, lower-cased (the packer names each folder after the
entity's logical name).

USAGE:
    python3 scripts/verify-attribute-type-stability.py <solution-root> --lock <lock.json>
    python3 scripts/verify-attribute-type-stability.py <solution-root> --lock <lock.json> --update
    python3 scripts/verify-attribute-type-stability.py <solution-root> --lock <lock.json> --seed
    python3 scripts/verify-attribute-type-stability.py --selftest

--update records NEW attributes only. It refuses to change a recorded type, except one that a
valid planned_retypes entry declares; that declaration then moves to applied_retypes, so a landed
retype stops warning and the record of who authorised it is kept.
--seed writes a fresh lock from the given tree (refuses to overwrite an existing lock).

Exit 0 = no FAIL; exit 1 = at least one FAIL or a usage error.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROUTES = ("new-column", "delete-and-recreate", "pre-ship")
DECL_FIELDS = ("attribute", "from", "to", "route", "live_in", "authorised_by", "date", "procedure")
KNOWLEDGE = ("knowledge/technology/dataverse.md -> \"Changing a Column's Data Type After It Has "
             "Shipped\"")


def read_types(solution_root: Path) -> dict[str, str]:
    """{entity.logicalname: type} for every <attribute> carrying both <LogicalName> and <Type>."""
    out: dict[str, str] = {}
    entities = solution_root / "Entities"
    for xml_path in sorted(entities.glob("*/Entity.xml")):
        entity = xml_path.parent.name.lower()
        root = ET.parse(xml_path).getroot()
        for attr in root.iter("attribute"):
            logical = (attr.findtext("LogicalName") or "").strip().lower()
            typ = (attr.findtext("Type") or "").strip().lower()
            if logical and typ:
                out[f"{entity}.{logical}"] = typ
    return out


def load_lock(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("attributes", {})
    data.setdefault("planned_retypes", [])
    data.setdefault("applied_retypes", [])
    return data


def write_lock(path: Path, data: dict) -> None:
    data["attributes"] = dict(sorted(data["attributes"].items()))
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def validate_declarations(lock: dict) -> tuple[list[str], dict[str, dict]]:
    """Return (fail messages, {attribute: valid declaration})."""
    fails: list[str] = []
    valid: dict[str, dict] = {}
    for i, decl in enumerate(lock["planned_retypes"]):
        where = f"planned_retypes[{i}]"
        missing = [f for f in DECL_FIELDS if not decl.get(f)]
        if missing:
            fails.append(f"{where}: missing {', '.join(missing)} — a declaration without a plan "
                         f"cannot pass")
            continue
        if decl["route"] not in ROUTES:
            fails.append(f"{where}: route '{decl['route']}' is not one of {', '.join(ROUTES)}")
            continue
        if not isinstance(decl["live_in"], list):
            fails.append(f"{where}: live_in must be a list of environment keys")
            continue
        attr = str(decl["attribute"]).lower()
        recorded = lock["attributes"].get(attr)
        if recorded is None:
            fails.append(f"{where}: {attr} is not recorded in the lock, so there is no type to "
                         f"change from")
            continue
        if str(decl["from"]).lower() != recorded:
            fails.append(f"{where}: {attr} declares from '{decl['from']}' but the lock records "
                         f"'{recorded}' — a stale plan is not a plan")
            continue
        valid[attr] = decl
    return fails, valid


def check(current: dict[str, str], lock: dict) -> tuple[list[str], list[str], list[str]]:
    fails, valid = validate_declarations(lock)
    warns: list[str] = []
    notes: list[str] = []
    recorded = lock["attributes"]
    for attr, typ in sorted(current.items()):
        was = recorded.get(attr)
        if was is None or was == typ:
            continue
        decl = valid.get(attr)
        if decl and str(decl["to"]).lower() == typ:
            warns.append(f"{attr}: {was} -> {typ} DECLARED, route {decl['route']}, live in "
                         f"{', '.join(decl['live_in']) or 'none'}, authorised by "
                         f"{decl['authorised_by']} {decl['date']}")
        else:
            fails.append(
                f"{attr}: type changed {was} -> {typ} with no planned_retypes declaration. "
                f"Import rejects a type change on an existing column (C-TECH-080). Choose a "
                f"route — a NEW column under a new logical name, or the measured "
                f"delete-and-recreate sequence in each environment where it is live — and "
                f"declare it in the lock. Procedure: {KNOWLEDGE}")
    unrecorded = sorted(set(current) - set(recorded))
    if unrecorded:
        notes.append(f"{len(unrecorded)} attribute(s) in source not recorded in the lock "
                     f"(unprotected until recorded): {', '.join(unrecorded)}. Record them with "
                     f"--update once they ship")
    gone = sorted(set(recorded) - set(current))
    if gone:
        notes.append(f"{len(gone)} recorded attribute(s) no longer in source: {', '.join(gone)}")
    return fails, warns, notes


def update(current: dict[str, str], lock: dict) -> tuple[list[str], int, int]:
    """Record new attributes, and declared retypes whose new type has landed. Refuse the rest."""
    fails, valid = validate_declarations(lock)
    if fails:
        return fails, 0, 0
    added = moved = 0
    refused: list[str] = []
    for attr, typ in sorted(current.items()):
        was = lock["attributes"].get(attr)
        if was is None:
            lock["attributes"][attr] = typ
            added += 1
        elif was != typ:
            decl = valid.get(attr)
            if decl and str(decl["to"]).lower() == typ:
                lock["attributes"][attr] = typ
                lock["planned_retypes"].remove(decl)
                lock["applied_retypes"].append(decl)
                moved += 1
            else:
                refused.append(f"{attr}: refusing to change recorded type {was} -> {typ} "
                               f"without a planned_retypes declaration (C-TECH-080)")
    return refused, added, moved


def run(solution_root: Path, lock_path: Path, mode: str) -> int:
    if not (solution_root / "Entities").is_dir():
        print(f"attribute-type-stability: ERROR — no Entities/ under {solution_root}",
              file=sys.stderr)
        return 1
    current = read_types(solution_root)
    if mode == "seed":
        if lock_path.exists():
            print(f"attribute-type-stability: ERROR — {lock_path} exists; --seed never "
                  f"overwrites a lock (use --update)", file=sys.stderr)
            return 1
        write_lock(lock_path, {"attributes": current, "planned_retypes": [],
                               "applied_retypes": []})
        print(f"attribute-type-stability: seeded {lock_path} with {len(current)} attribute(s)")
        return 0
    if not lock_path.is_file():
        print(f"attribute-type-stability: ERROR — lock {lock_path} not found", file=sys.stderr)
        return 1
    lock = load_lock(lock_path)
    if mode == "update":
        refused, added, moved = update(current, lock)
        if refused:
            for r in refused:
                print(f"FAIL  {r}", file=sys.stderr)
            print(f"attribute-type-stability: --update REFUSED, lock unchanged", file=sys.stderr)
            return 1
        write_lock(lock_path, lock)
        print(f"attribute-type-stability: --update recorded {added} new attribute(s), "
              f"{moved} declared retype(s)")
        return 0
    fails, warns, notes = check(current, lock)
    for f in fails:
        print(f"FAIL  {f}", file=sys.stderr)
    for w in warns:
        print(f"WARN  {w}")
    for n in notes:
        print(f"NOTE  {n}")
    status = "FAIL" if fails else "PASS"
    print(f"attribute-type-stability: {status} — {len(current)} attribute(s) in source, "
          f"{len(lock['attributes'])} recorded, {len(fails)} fail, {len(warns)} declared retype(s)")
    return 1 if fails else 0


# ---------------------------------------------------------------------------------------------
# selftest

def _entity(attrs: dict[str, str]) -> str:
    body = "".join(f"<attribute PhysicalName=\"{n}\"><Type>{t}</Type><Name>{n}</Name>"
                   f"<LogicalName>{n}</LogicalName></attribute>" for n, t in attrs.items())
    return (f"<ImportExportXml><Entities><Entity><EntityInfo><entity Name=\"x_t\">"
            f"<attributes>{body}</attributes></entity></EntityInfo></Entity></Entities>"
            f"</ImportExportXml>")


def _tree(base: Path, attrs: dict[str, str]) -> Path:
    d = base / "Entities" / "x_t"
    d.mkdir(parents=True, exist_ok=True)
    (d / "Entity.xml").write_text(_entity(attrs), encoding="utf-8")
    return base


def _decl(**over) -> dict:
    d = {"attribute": "x_t.x_a", "from": "nvarchar", "to": "ntext", "route": "delete-and-recreate",
         "live_in": ["dev"], "authorised_by": "Reviewer", "date": "2026-10-05",
         "procedure": "knowledge/technology/dataverse.md"}
    d.update(over)
    return d


def selftest() -> int:
    cases = [
        # (name, source attrs, lock, expected exit)
        ("unchanged", {"x_a": "nvarchar"}, {"attributes": {"x_t.x_a": "nvarchar"}}, 0),
        ("undeclared retype FAILS", {"x_a": "ntext"}, {"attributes": {"x_t.x_a": "nvarchar"}}, 1),
        ("picklist->bit FAILS", {"x_a": "bit"}, {"attributes": {"x_t.x_a": "picklist"}}, 1),
        ("declared retype WARNS", {"x_a": "ntext"},
         {"attributes": {"x_t.x_a": "nvarchar"}, "planned_retypes": [_decl()]}, 0),
        ("declared to a different type FAILS", {"x_a": "int"},
         {"attributes": {"x_t.x_a": "nvarchar"}, "planned_retypes": [_decl()]}, 1),
        ("stale declaration FAILS", {"x_a": "nvarchar"},
         {"attributes": {"x_t.x_a": "nvarchar"}, "planned_retypes": [_decl(**{"from": "bit"})]}, 1),
        ("declaration without route FAILS", {"x_a": "ntext"},
         {"attributes": {"x_t.x_a": "nvarchar"}, "planned_retypes": [_decl(route="")]}, 1),
        ("unknown route FAILS", {"x_a": "ntext"},
         {"attributes": {"x_t.x_a": "nvarchar"}, "planned_retypes": [_decl(route="just-import")]}, 1),
        ("new attribute is a NOTE", {"x_a": "nvarchar", "x_b": "int"},
         {"attributes": {"x_t.x_a": "nvarchar"}}, 0),
    ]
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        for i, (name, attrs, lock, want) in enumerate(cases):
            base = _tree(Path(tmp) / f"c{i}", attrs)
            lp = base / "lock.json"
            lp.write_text(json.dumps(lock), encoding="utf-8")
            got = run(base, lp, "check")
            ok = got == want
            bad += not ok
            print(f"  {'ok  ' if ok else 'BAD '} {name}: exit {got}, want {want}")
        # --update refuses an undeclared retype and leaves the lock byte-identical
        base = _tree(Path(tmp) / "u1", {"x_a": "ntext", "x_b": "int"})
        lp = base / "lock.json"
        lp.write_text(json.dumps({"attributes": {"x_t.x_a": "nvarchar"}}), encoding="utf-8")
        before = lp.read_bytes()
        ok = run(base, lp, "update") == 1 and lp.read_bytes() == before
        bad += not ok
        print(f"  {'ok  ' if ok else 'BAD '} --update refuses an undeclared retype, lock unchanged")
        # --update records a declared retype and moves the declaration
        lp.write_text(json.dumps({"attributes": {"x_t.x_a": "nvarchar"},
                                  "planned_retypes": [_decl()]}), encoding="utf-8")
        rc = run(base, lp, "update")
        after = json.loads(lp.read_text(encoding="utf-8"))
        ok = (rc == 0 and after["attributes"] == {"x_t.x_a": "ntext", "x_t.x_b": "int"}
              and not after["planned_retypes"] and len(after["applied_retypes"]) == 1
              and run(base, lp, "check") == 0)
        bad += not ok
        print(f"  {'ok  ' if ok else 'BAD '} --update records a declared retype and moves it")
        # --seed never overwrites
        ok = run(base, lp, "seed") == 1
        bad += not ok
        print(f"  {'ok  ' if ok else 'BAD '} --seed refuses to overwrite an existing lock")
    if bad:
        print(f"verify-attribute-type-stability: SELFTEST FAILED — {bad} case(s)", file=sys.stderr)
        return 1
    print("verify-attribute-type-stability: SELFTEST OK — every known-bad case rejected")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("solution_root", nargs="?", type=Path)
    ap.add_argument("--lock", type=Path)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--update", action="store_true")
    g.add_argument("--seed", action="store_true")
    g.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.solution_root is None or args.lock is None:
        ap.error("solution_root and --lock are required")
    mode = "update" if args.update else "seed" if args.seed else "check"
    return run(args.solution_root, args.lock, mode)


if __name__ == "__main__":
    sys.exit(main())
