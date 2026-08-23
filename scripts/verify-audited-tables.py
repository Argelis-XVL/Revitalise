#!/usr/bin/env python3
"""Every table the solution declares is declared for auditing in every environment.

WHY THIS EXISTS. `IMP-0178`, a blocker, and the system had already written down the answer.

`rev_review` shipped in Phase 3 (WBS task 6.4) and had no audit trail in DEV, which BLOCKED a
test cycle. `IMP-0085` — logged weeks earlier — says in the digest, in as many words:

    "Five tables (rev_review, rev_provider, rev_bankaccount, rev_payment,
     rev_anonymisedstatistic) are still to be built and will each need it."

The sixth table was built. It needed it. `IMP-0085`'s own deferral reason said *"revisit when the
next Dataverse table is built (Phase 3, tasks 6.4 / 8.1)"* — task 6.4 is exactly what shipped,
and the revisit never happened because nothing connected the deferral's condition to the event.
A prediction that nobody is scheduled to re-read is not a control.

WHY THIS IS THE SOURCE SIDE ONLY. Table-level auditing is entity METADATA. It is absent from
every `Entity.xml` in this repository and cannot be expressed there, so a solution import
neither sets it nor clears it (`IMP-0086` proved it survives two consecutive imports). Which
means:

  * the SWITCH lives in the environment and only a live query can read it — that is
    `C-TECH-064`'s job, and this gate is named in its `Verify By` as the source-side half;
  * the DECLARATION lives in the deployment settings and is fully derivable from source — that
    is this gate.

A table absent from `auditedTables` is a table nobody switches on, in any environment, ever. On
2026-08-22 six tables were on disk and four were declared: `rev_grant` and `rev_review` were in
neither the Test nor the Production settings file, so the known-bad fixture was the live tree.

WHAT IT DOES NOT COVER. It cannot prove the switch is ON. It cannot prove the retention period
is right. And it only checks settings files that DECLARE the key: a new environment whose
settings file omits `dataverse.auditing` entirely is invisible here, deliberately, because DEV
deliberately had no such block for months and inventing one would have broken an asserted
invariant (see `dev-auditing-settings.json`'s `_readme`). Absent-key environments are REPORTED,
never failed.

Run:
    python3 scripts/verify-audited-tables.py
    python3 scripts/verify-audited-tables.py --selftest

Exits 0 when every declared table is audited everywhere the key appears, 1 on any gap, 2 on a
usage error. Fails — never passes — when it resolves zero tables or zero declaring settings
files, because a checker with no inputs must not report PASS (`IMP-0007`).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ENTITY_GLOB = "src/solutions/*/Entities/*"
SETTINGS_GLOB = "provisioning/deploymentSettings/*.json"

# Keys under `dataverse.auditing` that carry the list, and the documentation prefix to ignore.
AUDITING_PATH = ("dataverse", "auditing")
TABLES_KEY = "auditedTables"
DOC_PREFIX = "_"


def declared_tables(repo_root: Path) -> list[str]:
    """Every table the solution source declares, from the Entities/ directories on disk.

    Derived from disk on purpose. `IMP-0038` recorded what a hand-kept list of entity names
    costs: an entity absent from it is an entity the provisioning step silently does not
    create. The same reasoning applies to a hand-kept list of tables to audit.
    """
    names = set()
    for path in repo_root.glob(ENTITY_GLOB):
        if path.is_dir() and (path / "Entity.xml").exists():
            names.add(path.name)
    return sorted(names)


def auditing_block(doc: dict) -> dict | None:
    node = doc
    for key in AUDITING_PATH:
        if not isinstance(node, dict) or key not in node:
            return None
        node = node[key]
    return node if isinstance(node, dict) else None


def scan(repo_root: Path) -> tuple[list[str], list[str], list[tuple[str, list[str]]],
                                   list[str], list[str]]:
    """Return (tables, declaring_files, gaps, absent_key_files, unreadable)."""
    tables = declared_tables(repo_root)
    declaring: list[str] = []
    absent: list[str] = []
    unreadable: list[str] = []
    gaps: list[tuple[str, list[str]]] = []

    for path in sorted(repo_root.glob(SETTINGS_GLOB)):
        rel = path.relative_to(repo_root).as_posix()
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            unreadable.append(f"{rel}: {exc}")
            continue
        if not isinstance(doc, dict):
            continue
        block = auditing_block(doc)
        if block is None or TABLES_KEY not in block:
            absent.append(rel)
            continue
        declaring.append(rel)
        listed = block.get(TABLES_KEY)
        listed = [t for t in listed if isinstance(t, str)] if isinstance(listed, list) else []
        missing = [t for t in tables if t not in listed]
        if missing:
            gaps.append((rel, missing))

    return tables, declaring, gaps, absent, unreadable


def selftest() -> int:
    import tempfile

    def build(root: Path, entities: list[str], audited: list[str] | None,
              declare_key: bool = True) -> None:
        for name in entities:
            d = root / "src" / "solutions" / "Sln" / "Entities" / name
            d.mkdir(parents=True)
            (d / "Entity.xml").write_text("<Entity />", encoding="utf-8")
        settings_dir = root / "provisioning" / "deploymentSettings"
        settings_dir.mkdir(parents=True)
        body: dict = {"dataverse": {"auditing": {"organizationAuditEnabled": True}}}
        if declare_key:
            body["dataverse"]["auditing"][TABLES_KEY] = audited or []
        (settings_dir / "test-settings.json").write_text(json.dumps(body), encoding="utf-8")

    cases = [
        ("every declared table is audited", ["rev_a", "rev_b"], ["rev_a", "rev_b"], True,
         False),
        ("a table on disk and not in the list is caught", ["rev_a", "rev_b"], ["rev_a"], True,
         True),
        ("a settings file that omits the key is reported, not failed", ["rev_a"], None, False,
         False),
        ("an extra audited table that is not on disk is not an error", ["rev_a"],
         ["rev_a", "rev_legacy"], True, False),
    ]

    failed = 0
    for why, entities, audited, declare_key, should_gap in cases:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build(root, entities, audited, declare_key)
            tables, declaring, gaps, absent, unreadable = scan(root)
            got = bool(gaps)
            ok = got == should_gap
            print(f"  {'ok  ' if ok else 'FAIL'}  {why}: {len(tables)} table(s), "
                  f"{len(declaring)} declaring file(s), {len(gaps)} gap(s), "
                  f"{len(absent)} absent-key file(s)")
            failed += 0 if ok else 1

    # The IMP-0007 controls: no tables, and no declaring files.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        build(root, [], ["rev_a"], True)
        tables, declaring, _g, _a, _u = scan(root)
        ok = tables == []
        print(f"  {'ok  ' if ok else 'FAIL'}  zero tables resolved yields an empty set "
              f"(caller must fail, not pass): tables={len(tables)}")
        failed += 0 if ok else 1

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        build(root, ["rev_a"], None, False)
        _t, declaring, _g, absent, _u = scan(root)
        ok = declaring == [] and len(absent) == 1
        print(f"  {'ok  ' if ok else 'FAIL'}  zero DECLARING files yields an empty set "
              f"(caller must fail, not pass): declaring={len(declaring)}")
        failed += 0 if ok else 1

    print(f"\nSELFTEST: {'PASS' if not failed else f'FAILED — {failed} case(s)'}")
    return 1 if failed else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Every table under src/solutions/*/Entities/ is declared for auditing in "
                    "every deployment settings file that declares auditedTables.")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--repo-root", default=None)
    args = parser.parse_args()

    if args.selftest:
        return selftest()

    repo_root = Path(args.repo_root).resolve() if args.repo_root \
        else Path(__file__).resolve().parents[1]

    tables, declaring, gaps, absent, unreadable = scan(repo_root)

    for problem in unreadable:
        print(f"ERROR: unreadable settings file — {problem}", file=sys.stderr)

    if not tables:
        print(f"ERROR: resolved ZERO tables from '{ENTITY_GLOB}'. Either the solution declares "
              f"no tables — in which case there is nothing to audit and that is the finding — "
              f"or the glob stopped matching. A checker with no inputs must fail rather than "
              f"report PASS (IMP-0007).", file=sys.stderr)
        return 1

    if not declaring:
        print(f"ERROR: no settings file under 'provisioning/deploymentSettings/' declares "
              f"'dataverse.auditing.{TABLES_KEY}', so this gate has nothing to check against "
              f"{len(tables)} declared table(s). That is the exact state that let rev_review "
              f"ship with no audit trail (IMP-0178, IMP-0007).", file=sys.stderr)
        return 1

    if gaps or unreadable:
        for rel, missing in gaps:
            print(f"ERROR: {rel}: 'dataverse.auditing.{TABLES_KEY}' omits "
                  f"{', '.join(missing)} — declared under '{ENTITY_GLOB}' but not audited in "
                  f"this environment. Table-level auditing is entity metadata that no solution "
                  f"import sets or clears (IMP-0086), so a table absent here is a table nobody "
                  f"switches on. rev_review shipped this way and blocked a test cycle "
                  f"(IMP-0178); IMP-0085 had predicted it by name.", file=sys.stderr)
        print(f"\nAUDITED TABLES: FAILED — {sum(len(m) for _, m in gaps)} undeclared "
              f"table/environment pair(s) across {len(gaps)} settings file(s).",
              file=sys.stderr)
        return 1

    print(f"AUDITED TABLES: PASS — {len(tables)} declared table(s) "
          f"({', '.join(tables)}) are audited in all {len(declaring)} settings file(s) that "
          f"declare the key.")
    for rel in declaring:
        print(f"  declares the key: {rel}")
    for rel in absent:
        print(f"  no dataverse.auditing.{TABLES_KEY} (reported, not failed): {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
