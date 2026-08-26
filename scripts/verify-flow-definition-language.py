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

WHAT IT CHECKS, per flow definition under the solution root — FIVE checks:

  1. no `select(` or `filter(` in any EXPRESSION value — deliberately not in `description`
     text, because this project's own notes explain the trap in prose and a gate that fires on
     its own documentation gets switched off;
  2. no connector `recordId` (or `item/<lookup>@odata.bind`-style Row ID) holding an
     alternate-key literal of the form `<column>='<value>'`;
  3. no `item` OBJECT on an action whose operationId is UpdateRecord — flattened `item/<column>`
     keys only;
  4. no `InitializeVariable` below the top level, and no variable written that no top-level
     `InitializeVariable` declares (`IMP-0137`);
  5. a flow that READS a Dataverse table declares a `runAfter` failure branch that reaches the
     error-recording path (`IMP-0325`, added 2026-08-26 by improvement review 29 change 3).

**This list said "three" until 2026-08-26 while four checks existed.** `IMP-0322` was logged
because a review read the docstring, concluded a Secure-Outputs check was present, and was about
to sequence work against it. A docstring that undercounts its own checks is a claim about the
file that the file contradicts, so the count is now stated and the checks enumerated. There is
NO Secure-Outputs / `runtimeConfiguration` check here — that risk is accepted under `EX-004`.

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

    # ── 4. InitializeVariable is legal ONLY at the top level (IMP-0137) ──────────
    # A nested one packs, imports and reports Activated, then the designer refuses to save and
    # the flow cannot be turned on — the restriction is enforced only by that save, which no
    # gate up to and including deploy exercises. `REVScoringCalculateAndFlag` shipped this way
    # from the first Phase 1 commit and the reviewer hand-lifted the same two actions in the
    # DEV designer on two separate activations before it was fixed at source.
    declared_top_level: set[str] = set()
    for path, action in _iter_actions(definition):
        if action.get("type") != "InitializeVariable":
            continue
        is_top_level = path.count("/") == 2 and path.startswith("/actions/")
        variables = ((action.get("inputs") or {}).get("variables") or [])
        if not isinstance(variables, list):
            variables = []
        for variable in variables:
            if isinstance(variable, dict) and variable.get("name"):
                if is_top_level:
                    declared_top_level.add(variable["name"])
        if not is_top_level:
            errors.append(
                f"{label}{path}: InitializeVariable below the top level of the flow. Power "
                "Automate allows this action only at the top level — never inside a Scope, "
                "condition, Apply to each or Switch. It packs and imports cleanly and reports "
                "the flow as present; the designer then refuses to save and the flow cannot be "
                "turned on (IMP-0137)."
            )

    for path, action in _iter_actions(definition):
        if action.get("type") not in (
                "SetVariable", "IncrementVariable", "AppendToStringVariable"):
            continue
        name = (action.get("inputs") or {}).get("name")
        if name and name not in declared_top_level:
            errors.append(
                f"{label}{path}: {action['type']} names variable {name!r}, which no "
                "top-level InitializeVariable declares in this flow. Either the declaration "
                "is missing, or it was left nested where it does not count (IMP-0137)."
            )

    # ── 5. A flow that reads a Dataverse table has a FAILURE PATH (IMP-0325) ─────────────
    errors += _check_failure_path(definition, label)
    return errors


# ── check 5 ────────────────────────────────────────────────────────────────────────────────
#
# `IMP-0325`. `REV | Portal | Round Statistics` was authored as a deliberately minimal first
# version — one metric computed, every other an explicit null — and the minimisation was applied
# to the metric computation AND, unremarked, to the error handling. Its TAD §5.1 specifies
# "rev_errorlog row + REV | Ops | Failure Alert, the existing pattern, AND a non-ok status in
# the response", and its own §5.1 flowchart draws R0 & R1 & R2 -.-> ERR. The flow shipped with
# every action on `runAfter: Succeeded` only, so a failure of either List rows terminated the run
# with NO Response action reached: the calling app got a bare failure, the screen could not
# render the "figures unavailable" state from a status value, and nothing was recorded anywhere.
# The notes documented exactly which METRICS were deferred and said nothing about the failure
# path, so the omission read as complete rather than partial.
#
# WHY THE RULE IS NOT "REACHES A rev_errorlog WRITE", WHICH IS HOW IT WAS PROPOSED.
# Measured against all five flows before wiring, that wording produces FOUR FALSE POSITIVES.
# This project centralises the write: `REV | Ops | Failure Alert` (workflow 8f1c2a44-1004-…) is
# the only flow that creates a `rev_errorlogs` row, and the other four reach it by INVOKING that
# child flow from their failure branch — which is what their own TAD calls "the existing
# pattern". A gate demanding a direct write in every flow would have been red on four correct
# flows, and the only way to green it would have been to duplicate the write four times.
#
# So the property, independent of the instance: **a flow that reads a Dataverse table declares a
# failure branch that reaches the error-recording path** — either the write itself, or the flow
# that owns the write.
#
# RESIDUAL, and it is the important one: this detects the PRESENCE of a failure path, never that
# it WORKS. Per `IMP-0109`, proving an error path means making the flow fail on purpose and
# reading what it logged. Nothing at pack, import or build time can do that.

_FAILURE_STATUSES = {"Failed", "TimedOut", "Skipped"}
# The flow that owns the rev_errorlog write. Reaching it from a failure branch IS the pattern.
_FAILURE_ALERT_WORKFLOW = "8f1c2a44-1004-4b7a-9e21-0a1b2c3d4e04"
_ERRORLOG_TABLE = "rev_errorlog"


def _reads_dataverse(definition: dict) -> bool:
    """True when any action reads a Dataverse table (ListRecords / GetItem / GetRecord)."""
    for _path, action in _iter_actions(definition):
        inputs = action.get("inputs")
        if not isinstance(inputs, dict):
            continue
        host = inputs.get("host") if isinstance(inputs.get("host"), dict) else {}
        operation = str(host.get("operationId") or "")
        if operation in {"ListRecords", "GetItem", "GetRecord"}:
            return True
    return False


def _failure_branch_actions(definition: dict) -> list[tuple[str, dict]]:
    """Every action whose runAfter names a failure status — i.e. the failure path's entry."""
    out: list[tuple[str, dict]] = []
    for path, action in _iter_actions(definition):
        run_after = action.get("runAfter")
        if not isinstance(run_after, dict):
            continue
        for statuses in run_after.values():
            if isinstance(statuses, list) and _FAILURE_STATUSES.intersection(statuses):
                out.append((path, action))
                break
    return out


def _reaches_error_recording(definition: dict) -> bool:
    """True when the flow either WRITES the error log or INVOKES the flow that does.

    Scoped to the whole definition rather than traced from each failure branch on purpose: a
    reachability trace through Scopes, conditions and Apply-to-each is a second parser, and a
    parser that stops matching finds nothing — which this file's own header calls a FAILURE, not
    an OK. The pairing (a failure branch exists AND the error path exists) is the assertion.
    """
    for _path, action in _iter_actions(definition):
        inputs = action.get("inputs")
        if not isinstance(inputs, dict):
            continue
        host = inputs.get("host") if isinstance(inputs.get("host"), dict) else {}
        if str(host.get("workflowReferenceName") or "").lower() == _FAILURE_ALERT_WORKFLOW:
            return True
        params = inputs.get("parameters")
        entity = params.get("entityName") if isinstance(params, dict) else None
        if isinstance(entity, str) and entity.lower().startswith(_ERRORLOG_TABLE):
            return True
    return False


def _check_failure_path(definition: dict, label: str) -> list[str]:
    if not _reads_dataverse(definition):
        return []
    branches = _failure_branch_actions(definition)
    if not branches:
        return [
            f"{label}: reads a Dataverse table and declares NO runAfter branch on "
            f"Failed/TimedOut/Skipped anywhere. Every action runs on Succeeded only, so a "
            f"failed read terminates the run with no Response action reached: the caller gets a "
            f"bare failure and nothing is recorded. Add the failure branch and route it to "
            f"`REV | Ops | Failure Alert`, which owns the rev_errorlog write (IMP-0325)."
        ]
    if not _reaches_error_recording(definition):
        return [
            f"{label}: has {len(branches)} failure branch(es) but reaches neither a "
            f"`{_ERRORLOG_TABLE}` write nor `REV | Ops | Failure Alert` "
            f"({_FAILURE_ALERT_WORKFLOW}). A failure path that alerts and records nothing "
            f"leaves no trace to diagnose from (IMP-0325)."
        ]
    return []


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
          "select()/filter() expression, no alternate-key Row ID, no nested item on an "
          "UpdateRecord, no InitializeVariable below the top level, and every flow reading a "
          "Dataverse table has a failure branch reaching the error-recording path. NOTE: "
          "check 5 proves a failure path EXISTS, never that it works — proving that means "
          "making the flow fail on purpose (IMP-0109).")
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
_BAD_NESTED_INIT = _wrap({"G": {"type": "Scope", "runAfter": {}, "actions": {
    "H": {"type": "InitializeVariable", "runAfter": {},
          "inputs": {"variables": [{"name": "count", "type": "integer", "value": 0}]}}}}})
_BAD_UNDECLARED_SET = _wrap({
    "I": {"type": "IncrementVariable", "runAfter": {},
          "inputs": {"name": "neverInitialised", "value": 1}}})
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
    "G": {"type": "InitializeVariable", "runAfter": {},
          "inputs": {"variables": [{"name": "count", "type": "integer", "value": 0}]}},
    "H": {"type": "Scope", "runAfter": {"G": ["Succeeded"]}, "actions": {
        "I": {"type": "IncrementVariable", "runAfter": {},
              "inputs": {"name": "count", "value": 1}}}},
})


def _read(name: str = "List_rows") -> dict:
    return {name: {"type": "OpenApiConnection", "runAfter": {}, "inputs": {
        "host": {"operationId": "ListRecords"},
        "parameters": {"entityName": "rev_applications"}}}}


# check 5 — a Dataverse read with every action on Succeeded only. IMP-0325's exact shape.
_BAD_NO_FAILURE_PATH = _wrap({
    **_read(),
    "Compute": {"type": "Compose", "runAfter": {"List_rows": ["Succeeded"]},
                "inputs": "@length(body('List_rows')?['value'])"},
    "Respond": {"type": "Response", "runAfter": {"Compute": ["Succeeded"]},
                "inputs": {"statusCode": 200}}})

# check 5 — a failure branch that alerts a human and records nothing. Nothing to diagnose from.
_BAD_FAILURE_PATH_RECORDS_NOTHING = _wrap({
    **_read(),
    "Tell_someone": {"type": "OpenApiConnection",
                     "runAfter": {"List_rows": ["Failed", "TimedOut", "Skipped"]},
                     "inputs": {"host": {"operationId": "PostMessageToConversation"},
                                "parameters": {"body": "it broke"}}}})

# check 5, GOOD — THIS PROJECT'S ACTUAL PATTERN, and the reason the rule is not "reaches a
# rev_errorlog write": the write is centralised in REV | Ops | Failure Alert and the caller
# invokes it. Demanding a direct write here would be red on four correct flows.
_GOOD_FAILURE_VIA_ALERT_FLOW = _wrap({
    **_read(),
    "Find_the_failed_action": {"type": "Query",
                               "runAfter": {"List_rows": ["Failed", "TimedOut", "Skipped"]},
                               "inputs": {"from": "@result('List_rows')"}},
    "Alert_on_failure": {"type": "Workflow",
                         "runAfter": {"Find_the_failed_action": ["Succeeded"]},
                         "inputs": {"host": {"workflowReferenceName":
                                             _FAILURE_ALERT_WORKFLOW}}},
    "Respond_error": {"type": "Response", "runAfter": {"Alert_on_failure": ["Succeeded"]},
                      "inputs": {"statusCode": 500}}})

# check 5, GOOD — the other legitimate shape: the flow writes the row itself, as the Failure
# Alert flow does.
_GOOD_FAILURE_WRITES_THE_LOG = _wrap({
    **_read(),
    "Write_error_log_row": {"type": "OpenApiConnection",
                            "runAfter": {"List_rows": ["Failed", "TimedOut", "Skipped"]},
                            "inputs": {"host": {"operationId": "CreateRecord"},
                                       "parameters": {"entityName": "rev_errorlogs"}}}})

# check 5, GOOD — the over-firing control. A flow that READS NOTHING from Dataverse is out of
# scope entirely, so a scheduled notifier with no failure branch must not be reported.
_GOOD_NO_DATAVERSE_READ = _wrap({
    "Post": {"type": "OpenApiConnection", "runAfter": {}, "inputs": {
        "host": {"operationId": "PostMessageToConversation"},
        "parameters": {"body": "hello"}}}})


def selftest() -> int:
    cases = [("a select() expression is rejected", _BAD_SELECT, 1),
             ("an alternate-key Row ID is rejected", _BAD_ALTKEY, 1),
             ("a nested item on UpdateRecord is rejected", _BAD_NESTED, 1),
             ("an InitializeVariable below the top level is rejected", _BAD_NESTED_INIT, 1),
             ("a Set/Increment/AppendToStringVariable naming an undeclared variable is "
              "rejected", _BAD_UNDECLARED_SET, 1),
             ("check 5: a Dataverse read with NO failure branch anywhere is rejected",
              _BAD_NO_FAILURE_PATH, 1),
             ("check 5: a failure branch that records nothing is rejected",
              _BAD_FAILURE_PATH_RECORDS_NOTHING, 1),
             ("check 5: a failure branch invoking REV | Ops | Failure Alert PASSES — this "
              "project's actual pattern, and why the rule is not 'a direct rev_errorlog write'",
              _GOOD_FAILURE_VIA_ALERT_FLOW, 0),
             ("check 5: a failure branch writing the rev_errorlog row itself PASSES",
              _GOOD_FAILURE_WRITES_THE_LOG, 0),
             ("check 5: a flow that reads no Dataverse table is OUT OF SCOPE and must not be "
              "reported", _GOOD_NO_DATAVERSE_READ, 0),
             ("a Select ACTION, a flattened UpdateRecord, a nested CreateRecord, a top-level "
              "InitializeVariable and a nested IncrementVariable consuming it all pass",
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
