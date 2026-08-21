#!/usr/bin/env python3
"""Reject the connector and expression shapes this project has already had rejected live.

THE GENERAL GATE FOR CLASS `platform-contract-guessed-not-groundtruthed` (x16 in
logs/known-failure-modes.md). Three of those instances are cloud-flow shapes that pack cleanly,
import cleanly, report Activated, and then fail — or silently do nothing — when the branch
containing them is first taken. Each was found by a human, in an environment, after a deploy:

  * `IMP-0124` — `select(...)` and `filter(...)` do not EXIST as expressions in the workflow
    definition language. Select and Filter array are data-operation ACTIONS, and `item()` is
    only meaningful inside one. The withheld-outcome breakdown carried a `select(` for days.
    It was the only one in the solution, in the taken branch of an `if()`, so TD-08 passed and
    TD-07 failed on the same action.
  * `IMP-0112` — the Dataverse connector's Get-a-row-by-id takes a GUID in Row ID. The Web API
    accepts `rev_settings(rev_name='LikertPointMap')` and the alternate key reports Active, so
    the shape looks verified; the CONNECTOR rejects it. The scoring flow failed on its first
    action on all eleven runs of its first live test. **The intake flow still carries six.**
  * `IMP-0116` — the Dataverse connector is ASYMMETRIC. CreateRecord accepts a nested
    `"item": {columns}`; UpdateRecord does not — its columns must be flattened to
    `"item/<column>"`. A nested item on an UpdateRecord shows as an action with NO PROPERTIES
    CONFIGURED in the designer and writes nothing WHILE SUCCEEDING. A green run and an empty
    column is the only symptom.

Two of the three were fixed as instances. Per `skills/how-to-promote-a-finding.md` §2 the third
may not get another instance patch: the property, independent of the instance, is **a flow
definition may not contain a connector or expression shape this project has already watched the
platform reject.** That is what this checks, and it is cheap enough to run on every build.

WHAT IT CHECKS, per flow definition under the solution root:

  1. no `select(` or `filter(` in any EXPRESSION value — deliberately not in `description`
     text, because this project's own notes explain the trap in prose and a gate that fires on
     its own documentation gets switched off;
  2. no connector `recordId` (or `item/<lookup>@odata.bind`-style Row ID) holding an
     alternate-key literal of the form `<column>='<value>'`;
  3. no `item` OBJECT on an action whose operationId is UpdateRecord — flattened `item/<column>`
     keys only.

Run:
    python3 scripts/verify-flow-definition-language.py src/solutions/RevitaliseGrantAutomation
    python3 scripts/verify-flow-definition-language.py --selftest   # prove it can fail

Exits 0 when every definition is clean, 1 on any violation or unreadable input, 2 on a usage
error. Fails — never passes — when it finds no flow definitions at all, so it cannot report OK
over an empty tree (IMP-0007). C-TECH-052.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

# `select(` / `filter(` as an expression call. Word-boundary anchored so `Find_missing…` and a
# column called `filterby` do not match.
_NONEXISTENT_FN = re.compile(r"(?<![A-Za-z0-9_])(select|filter)\s*\(")

# An alternate-key literal in a Row ID: rev_name='LikertPointMap'
_ALT_KEY_LITERAL = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\s*=\s*'[^']*'$")

# Keys whose VALUES are prose, not expressions. Never scanned for check 1.
_PROSE_KEYS = {"description", "$schema", "metadata"}


def _iter_actions(node, path=""):
    """Yield (json-path, action-dict) for every action/trigger in a definition."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key in ("actions", "triggers") and isinstance(value, dict):
                for name, action in value.items():
                    if isinstance(action, dict):
                        yield f"{path}/{key}/{name}", action
                        yield from _iter_actions(action, f"{path}/{key}/{name}")
            else:
                yield from _iter_actions(value, f"{path}/{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from _iter_actions(value, f"{path}/{index}")


def _iter_expression_strings(node, path="", key=None):
    """Yield (json-path, string) for every value that could be an expression."""
    if isinstance(node, dict):
        for k, v in node.items():
            if k in _PROSE_KEYS:
                continue
            yield from _iter_expression_strings(v, f"{path}/{k}", k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _iter_expression_strings(v, f"{path}/{i}", key)
    elif isinstance(node, str):
        yield path, node


def check_definition(definition: dict, label: str) -> list[str]:
    errors: list[str] = []

    # ── 1. expression functions that do not exist ────────────────────────────
    for path, text in _iter_expression_strings(definition):
        match = _NONEXISTENT_FN.search(text)
        if match:
            errors.append(
                f"{label}{path}: uses `{match.group(1)}(` as an EXPRESSION. The workflow "
                "definition language has no such function — Select and Filter array are "
                "data-operation ACTIONS, and item() is only valid inside one. This packs, "
                "imports and reports Activated, and fails when its branch is first taken "
                "(IMP-0124)."
            )

    for path, action in _iter_actions(definition):
        inputs = action.get("inputs")
        if not isinstance(inputs, dict):
            continue
        params = inputs.get("parameters")
        operation = ((inputs.get("host") or {}).get("operationId")) if isinstance(
            inputs.get("host"), dict) else None
        if not isinstance(params, dict):
            continue

        # ── 2. an alternate-key literal where the connector wants a GUID ─────
        for key, value in params.items():
            if not isinstance(value, str):
                continue
            if key != "recordId" and not key.endswith("/recordId"):
                continue
            if _ALT_KEY_LITERAL.match(value.strip()):
                errors.append(
                    f"{label}{path}: `{key}` holds the alternate-key literal {value!r}. The "
                    "Dataverse connector's Row ID takes a GUID; the Web API accepts this form "
                    "and the connector does not, which is why the scoring flow failed on its "
                    "first action on all eleven runs of its first live test. Replace with one "
                    "List rows call plus a Filter array per value, and guard the row count "
                    "(IMP-0112)."
                )

        # ── 3. the asymmetric connector: no nested item on an UpdateRecord ───
        if operation == "UpdateRecord" and isinstance(params.get("item"), dict):
            errors.append(
                f"{label}{path}: UpdateRecord carries a nested `item` object. CreateRecord "
                "accepts that shape and UpdateRecord does not — its columns must be flattened "
                "to `item/<column>`. A nested item shows as an action with NO PROPERTIES "
                "CONFIGURED in the designer and writes nothing WHILE SUCCEEDING: a green run "
                "and an empty column is the only symptom (IMP-0116)."
            )
    return errors


def run(root: Path) -> int:
    if not root.is_dir():
        print(f"flow-definition-language: FAILED — {root} is not a directory. A gate pointed at "
              "a missing target does not fail (IMP-0007).", file=sys.stderr)
        return 1

    paths = sorted(p for p in root.rglob("Workflows/*.json") if not p.name.endswith(".data.xml"))
    if not paths:
        paths = sorted(root.rglob("*.json"))
    definitions = []
    for path in paths:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        definition = (data.get("properties") or {}).get("definition") if isinstance(
            data, dict) else None
        if isinstance(definition, dict):
            definitions.append((path, definition))

    if not definitions:
        print(f"flow-definition-language: FAILED — no flow definitions found under {root}. A "
              "gate with nothing to check must not report OK (IMP-0007).", file=sys.stderr)
        return 1

    errors: list[str] = []
    for path, definition in definitions:
        try:
            rel = path.relative_to(root)
        except ValueError:
            rel = path
        errors += check_definition(definition, str(rel))

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\nflow-definition-language: FAILED — {len(errors)} shape(s) across "
              f"{len(definitions)} flow definition(s) that the platform accepts at pack and "
              "import time and rejects at run time.", file=sys.stderr)
        return 1

    print(f"flow-definition-language: OK — {len(definitions)} flow definition(s) carry no "
          "select()/filter() expression, no alternate-key Row ID, and no nested item on an "
          "UpdateRecord.")
    return 0


# ── Self-test: the gate must be able to fail (C-TECH-057) ────────────────────

def _wrap(actions: dict) -> dict:
    return {"properties": {"definition": {"actions": actions}}}


_BAD_SELECT = _wrap({"A": {"type": "Compose", "description": "mentions select( in prose only",
                           "inputs": "@join(select(body('x'), item()?['q']), ', ')"}})
_BAD_ALTKEY = _wrap({"B": {"type": "OpenApiConnection", "inputs": {
    "host": {"operationId": "GetItem"},
    "parameters": {"entityName": "rev_settings", "recordId": "rev_name='LikertPointMap'"}}}})
_BAD_NESTED = _wrap({"C": {"type": "OpenApiConnection", "inputs": {
    "host": {"operationId": "UpdateRecord"},
    "parameters": {"entityName": "rev_applications", "recordId": "@x",
                   "item": {"rev_status": 3}}}}})
_GOOD = _wrap({
    "D": {"type": "Query", "description": "A Select ACTION, not a select() expression.",
          "inputs": {"from": "@body('x')", "select": "@string(item()?['question'])"}},
    "E": {"type": "OpenApiConnection", "inputs": {
        "host": {"operationId": "UpdateRecord"},
        "parameters": {"entityName": "rev_applications", "recordId": "@triggerOutputs()",
                       "item/rev_status": 3}}},
    "F": {"type": "OpenApiConnection", "inputs": {
        "host": {"operationId": "CreateRecord"},
        "parameters": {"entityName": "rev_applications", "item": {"rev_status": 1}}}},
})


def selftest() -> int:
    cases = [("a select() expression is rejected", _BAD_SELECT, 1),
             ("an alternate-key Row ID is rejected", _BAD_ALTKEY, 1),
             ("a nested item on UpdateRecord is rejected", _BAD_NESTED, 1),
             ("a Select ACTION, a flattened UpdateRecord and a nested CreateRecord all pass",
              _GOOD, 0)]
    checks = []
    with tempfile.TemporaryDirectory() as tmp:
        for index, (label, payload, expected) in enumerate(cases):
            root = Path(tmp) / f"case{index}"
            (root / "Workflows").mkdir(parents=True)
            (root / "Workflows" / "F.json").write_text(json.dumps(payload), encoding="utf-8")
            checks.append((label, run(root) == expected))
        empty = Path(tmp) / "empty"
        empty.mkdir()
        checks.append(("a tree with no flow definitions FAILS", run(empty) == 1))
        checks.append(("a missing directory FAILS", run(Path(tmp) / "nope") == 1))

    print("\n── SELFTEST ────────────────────────────────────────────────────────────────")
    for label, passed in checks:
        print(f"  {'PASS' if passed else 'FAIL'}  {label}")
    failed = [c for c in checks if not c[1]]
    if failed:
        print(f"\nflow-definition-language selftest: FAILED — {len(failed)} check(s)",
              file=sys.stderr)
        return 1
    print(f"\nflow-definition-language selftest: OK — {len(checks)} check(s); the gate can fail.")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", help="solution source root")
    parser.add_argument("--selftest", action="store_true",
                        help="prove this gate can fail, then exit")
    args = parser.parse_args(argv[1:])
    if args.selftest:
        return selftest()
    if not args.root:
        parser.print_usage(sys.stderr)
        return 2
    return run(Path(args.root.rstrip("/")))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
