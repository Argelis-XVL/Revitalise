#!/usr/bin/env python3
"""Make two asserted properties of a privileged, row-triggered flow into checked ones.

TAD `docs/architecture/trustee-portal-visual-refresh-architecture.md` §6.3.1 and §6.3.3
(ADR-038, APPROVED 2026-08-28) each turn a sentence this project has been repeating since
Revision 2 into something a build can fail on. Both are about ONE flow —
`REV | Portal | Round Statistics` — and both exist because that flow is the only privileged
reader of `rev_applicant.rev_gender`, a column the trustee persona is denied at value level.

The two properties, and why a sentence was not enough:

  CHECK A — THE FLOW READS NOTHING FROM ITS TRIGGER BODY.
    Under the superseded ADR-030 transport the flow had a Power Apps trigger and took no
    input at all, so "no round key, no filter, no column list a caller could steer" was true
    by construction. A Dataverse row trigger HANDS the flow a trigger body containing the row
    and its modifier, so the same claim now needs teeth. §1.5 point 4: the flow re-reads what
    it needs by its own queries, and `rev_triggeredon` exists only as a change to fire on.

  CHECK B — THE RESULT DOCUMENT IS COMPOSED FROM AN ENUMERATED FIELD LIST, NEVER FROM A
  SERIALISED ROW OBJECT.
    §3.3 property 6. A wholesale serialisation is one careless expression away from putting an
    applicant row into a column a trustee reads, and NO other gate in this repository would
    see it: every column gate here is read-side, and nothing written to
    `rev_roundstatisticsresult.rev_resultjson` is a secured column on a table the app queries.

WHAT CHECK A REJECTS, over the named flow definition:

  A1. `triggerBody(`, `triggerOutputs(`, `@triggerBody`, `@triggerOutputs` in any EXPRESSION
      value. Deliberately not in `description` prose — a gate that fires on its own
      documentation gets switched off, which is the trap `verify-flow-definition-language.py`
      already calls out for `select(`/`filter(`.
  A2. any `outputs('<trigger>')` / `body('<trigger>')` / `result('<trigger>')` naming the
      flow's own trigger — the same read by another route.
  A3. the string `rev_triggeredon` ANYWHERE in the definition, prose included. §6.3.1's own
      wording: "the column name must not appear in the flow definition at all." The
      explanation of why belongs in the flow's `.notes.md`, which this gate does not read.

WHAT CHECK B REJECTS:

  B1. any reference to a ROW-BEARING action that reaches `item/rev_resultjson`, except where
      the innermost enclosing function is `length` or `empty`.

  "Row-bearing" is DERIVED, never hand-typed (the `hand-maintained-count-drifts-from-source`
  class is at x20 in logs/known-failure-modes.md). An action is row-bearing if either:
    * it is a connector read (`ListRecords` / `GetItem`) whose `entityName` is the entity SET
      of a table that has at least one `IsSecured=1` attribute in `Entities/*/Entity.xml` —
      the same derive-from-source technique `verify-code-app-column-bindings.py` uses; or
    * it carries `runtimeConfiguration.secureData` on its outputs, i.e. the flow itself
      declares that action's output as personal data (TAD §6.4.1); or
    * one of its own input expressions references a row-bearing action anywhere other than
      inside `length(` / `empty(` — so a Filter/Select over the round's rows is row-bearing
      too, transitively, to a fixpoint.

  `length` and `empty` are the whole allow-list on purpose: they are the two workflow-language
  functions that reduce a collection to a scalar. `first` is NOT on it, and that is the point —
  `first(...)` returns a row.

  ONE EXEMPTION, ADDED 2026-08-28 FOR ADR-039, AND IT IS A TEMPLATE RATHER THAN A FUNCTION NAME.
  TAD Revision 6 (ADR-039, APPROVED) computes four money averages with
  `xpath(xml(concat(… join(…) …)), 'sum(/r/v)')` — a third way of reducing a collection to a
  scalar, and one this gate rejected outright when the flow was first written against the
  approved ADR. Measured, not predicted: the B1 violation was reproduced before this exemption
  existed.

  The safety argument is one sentence: **an XPath `sum()` returns an XPath number, and a number
  cannot carry a row.** That holds whatever the feeding `Select` projects — a `Select` that
  projected whole rows would make `sum(/r/v)` return `NaN`, never a row — so the exemption does
  not depend on inspecting the projection.

  It is deliberately NOT implemented by adding `xpath`, `join` or `xml` to
  `_REDUCING_FUNCTIONS`. That would exempt every reference whose innermost enclosing function
  happened to be one of those names, including `join(body('List_applications_in_round'), ',')`,
  which serialises rows. Instead ONE anchored template matches the ENTIRE input expression of a
  `Compose`, with the same `Select` action named in both `body()` positions and the XPath
  expression pinned to the literal `sum(/r/v)`. A node-returning XPath, a different XML shape,
  two different source actions, or one extra reference anywhere in the same expression all fail
  the template and taint propagates exactly as before. Four selftest cases hold that line.

Run:
    python3 scripts/verify-flow-trigger-body-isolation.py \\
        --solution src/solutions/RevitaliseGrantAutomation \\
        src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json
    python3 scripts/verify-flow-trigger-body-isolation.py --selftest   # prove it can fail

Exits 0 when the named flow is clean, 1 on any violation or unreadable input, 2 on a usage
error. It FAILS — never passes — when the named file does not exist, when it holds no trigger,
or when its trigger is not a Dataverse row trigger, so it cannot report OK over a file that
was renamed, emptied, or reverted to the superseded Power Apps trigger (`gate-fires-on-nothing`,
x5). C-TECH-049, C-TECH-052, C-TECH-057.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

# ── Check A tokens ───────────────────────────────────────────────────────────────────
# The four §6.3.1 names, as expression calls or as raw @-references.
_TRIGGER_BODY_TOKENS = re.compile(r"@?trigger(?:Body|Outputs)\b")

# The trigger column. §6.3.1 wants this absent from the whole definition, prose included.
_TRIGGER_COLUMN = "rev_triggeredon"

# `outputs('X')` / `body('X')` / `result('X')` — the three ways one action names another.
_ACTION_REF = re.compile(r"\b(?:outputs|body|result)\s*\(\s*'([^']+)'\s*\)")

# Keys whose values are prose, never expressions. Not scanned by A1/A2/B1.
_PROSE_KEYS = {"description", "$schema", "contentVersion", "templateName"}

# The only two workflow-language functions that reduce a collection to a scalar.
_REDUCING_FUNCTIONS = {"length", "empty"}

# ADR-039's scalar reduction, anchored to the WHOLE input expression of a Compose.
#
# The one shape in which a row-bearing collection may reach an output, because what comes back
# is an XPath number and a number cannot carry a row. Pinned byte-for-byte on purpose: the
# backreference forces both `body()` calls to name the SAME Select action, and the XPath
# expression is the literal `sum(/r/v)` rather than any expression at all — a node-returning
# XPath (`'/r/v'`) is not this template and does not get the exemption.
#
# The inner `if(empty(...))` is part of the template rather than optional decoration. XPath 1.0
# `sum()` over a node set containing one EMPTY element is `NaN` for the whole sum — measured
# against libxml2, 2026-08-28 — so a bare `'<r><v>' + join(…) + '</v></r>'` yields `NaN` on an
# empty subset, `NaN` is not valid JSON, and an unparseable `rev_resultjson` takes all thirteen
# metrics off the trustee screen. Over an EMPTY node set (`<r></r>`) `sum()` is `0`, which the
# average guard withholds. Requiring the guard here means the gate rejects the unhardened form.
_SCALAR_REDUCTION = re.compile(
    r"^@xpath\(xml\(concat\('<r>',\s*"
    r"if\(empty\(body\('(?P<source>[A-Za-z0-9_]+)'\)\),\s*'',\s*"
    r"concat\('<v>',\s*join\(body\('(?P=source)'\),\s*'</v><v>'\),\s*'</v>'\)\),\s*"
    r"'</r>'\)\),\s*'sum\(/r/v\)'\)$"
)


def _is_scalar_reduction(action: dict) -> bool:
    """True for a Compose whose entire input is ADR-039's `xpath(…,'sum(/r/v)')` template."""
    if action.get("type") != "Compose":
        return False
    inputs = action.get("inputs")
    return isinstance(inputs, str) and _SCALAR_REDUCTION.match(inputs.strip()) is not None

# Connector operations that return Dataverse rows.
_ROW_READ_OPERATIONS = {"ListRecords", "GetItem"}

# The column the result document is written to. Check B's sink.
_RESULT_COLUMN_PARAMETER = "item/rev_resultjson"

_ROW_TRIGGER_TYPE = "OpenApiConnectionWebhook"


class Violation:
    def __init__(self, check: str, where: str, detail: str, why: str) -> None:
        self.check = check
        self.where = where
        self.detail = detail
        self.why = why

    def render(self) -> str:
        return (f"  [{self.check}] {self.where}\n"
                f"        {self.detail}\n"
                f"        why: {self.why}")


# ── Walking a definition ─────────────────────────────────────────────────────────────

def _iter_actions(node, path: str = ""):
    """Yield (json-path, action-name, action-dict) for every action at every nesting level."""
    if not isinstance(node, dict):
        return
    for name, action in node.items():
        if not isinstance(action, dict):
            continue
        here = f"{path}/{name}" if path else name
        yield here, name, action
        for key in ("actions",):
            if isinstance(action.get(key), dict):
                yield from _iter_actions(action[key], here)
        if isinstance(action.get("else"), dict):
            yield from _iter_actions(action["else"].get("actions") or {}, f"{here}/else")
        for case_name, case in (action.get("cases") or {}).items():
            if isinstance(case, dict):
                yield from _iter_actions(case.get("actions") or {}, f"{here}/case:{case_name}")
        if isinstance(action.get("default"), dict):
            yield from _iter_actions(action["default"].get("actions") or {}, f"{here}/default")


def _iter_expression_strings(node, path: str = ""):
    """Yield (json-path, string) for every string that is an EXPRESSION, not prose."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key in _PROSE_KEYS:
                continue
            yield from _iter_expression_strings(value, f"{path}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from _iter_expression_strings(value, f"{path}[{index}]")
    elif isinstance(node, str):
        yield path, node


def _iter_all_strings(node, path: str = ""):
    """Yield (json-path, string) for EVERY string, prose included. A3 only."""
    if isinstance(node, dict):
        for key, value in node.items():
            yield from _iter_all_strings(value, f"{path}.{key}")
            if isinstance(key, str):
                yield f"{path}.<key>", key
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from _iter_all_strings(value, f"{path}[{index}]")
    elif isinstance(node, str):
        yield path, node


def _innermost_enclosing_function(expression: str, position: int) -> str | None:
    """The name of the innermost function call open at `position`, or None at top level.

    Walks the prefix once, keeping a stack of `identifier(` opens and popping on `)`. Quoted
    literals are skipped so a `'('` inside a JSON fragment cannot unbalance the stack — which
    matters here, because every composition in this solution is `concat('{\"a\":', ...)`.
    """
    stack: list[str] = []
    index = 0
    length = len(expression)
    while index < position and index < length:
        char = expression[index]
        if char == "'":
            index += 1
            while index < length and expression[index] != "'":
                index += 1
            index += 1
            continue
        if char == "(":
            match = re.search(r"([A-Za-z_][A-Za-z0-9_]*)\s*$", expression[:index])
            stack.append(match.group(1) if match else "")
            index += 1
            continue
        if char == ")":
            if stack:
                stack.pop()
            index += 1
            continue
        index += 1
    return stack[-1] if stack else None


def _references(expression: str) -> list[tuple[str, str | None]]:
    """Every (action-name, innermost-enclosing-function) referenced by an expression."""
    found: list[tuple[str, str | None]] = []
    for match in _ACTION_REF.finditer(expression):
        found.append((match.group(1), _innermost_enclosing_function(expression, match.start())))
    return found


# ── Deriving the personal-data table set from solution source ────────────────────────

def _entity_sets_with_secured_columns(solution_root: Path) -> tuple[set[str], list[str]]:
    """Entity SET names of tables carrying at least one IsSecured=1 attribute.

    Derived from Entities/*/Entity.xml on disk, never hand-typed. Returns the set plus any
    non-fatal notes about files that could not be parsed, so an unreadable Entity.xml is
    reported rather than silently narrowing the seed.
    """
    sets: set[str] = set()
    notes: list[str] = []
    entities_dir = solution_root / "Entities"
    if not entities_dir.is_dir():
        notes.append(f"{entities_dir} does not exist — check B's seed is EMPTY")
        return sets, notes
    for entity_xml in sorted(entities_dir.glob("*/Entity.xml")):
        try:
            root = ET.parse(entity_xml).getroot()
        except ET.ParseError as exc:
            notes.append(f"{entity_xml}: unparseable ({exc})")
            continue
        secured = any((node.text or "").strip() == "1"
                      for node in root.iter("IsSecured"))
        if not secured:
            continue
        entity_set = root.findtext("EntitySetName")
        if entity_set:
            sets.add(entity_set.strip())
        else:
            notes.append(f"{entity_xml}: has secured columns but declares no <EntitySetName>")
    return sets, notes


# ── Check A ──────────────────────────────────────────────────────────────────────────

def _check_trigger_isolation(definition: dict, trigger_names: list[str]) -> list[Violation]:
    violations: list[Violation] = []
    actions = definition.get("actions") or {}

    for path, value in _iter_expression_strings(actions, "actions"):
        if _TRIGGER_BODY_TOKENS.search(value):
            violations.append(Violation(
                "A1", path,
                f"reads its trigger body: {_TRIGGER_BODY_TOKENS.search(value).group(0)!r}",
                "TAD §1.5 point 4 / §6.3.1 — this flow re-reads what it needs by its own "
                "queries. A trigger-body read is a caller-supplied value reaching a "
                "privileged computation."))
        for referenced, _enclosing in _references(value):
            if referenced in trigger_names:
                violations.append(Violation(
                    "A2", path,
                    f"names its own trigger {referenced!r} — the same read by another route",
                    "TAD §6.3.1 — 'no reference to the trigger's own action name in any "
                    "action's inputs'."))

    for path, value in _iter_all_strings(definition, "definition"):
        if _TRIGGER_COLUMN in value:
            violations.append(Violation(
                "A3", path,
                f"contains {_TRIGGER_COLUMN!r}",
                f"TAD §6.3.1 — '{_TRIGGER_COLUMN} is written by the app and read by NOBODY; "
                "the column name must not appear in the flow definition at all.' Explain it "
                "in the flow's .notes.md, which this gate does not read."))
    return violations


# ── Check B ──────────────────────────────────────────────────────────────────────────

def _row_bearing_actions(definition: dict, personal_entity_sets: set[str]) -> set[str]:
    """The fixpoint of actions whose output may carry a Dataverse row."""
    catalogue: dict[str, dict] = {}
    for _path, name, action in _iter_actions(definition.get("actions") or {}):
        catalogue[name] = action

    tainted: set[str] = set()
    for name, action in catalogue.items():
        inputs = action.get("inputs")
        if not isinstance(inputs, dict):
            continue
        host = inputs.get("host")
        parameters = inputs.get("parameters")
        if (isinstance(host, dict) and host.get("operationId") in _ROW_READ_OPERATIONS
                and isinstance(parameters, dict)
                and str(parameters.get("entityName", "")) in personal_entity_sets):
            tainted.add(name)
        secure = ((action.get("runtimeConfiguration") or {}).get("secureData") or {})
        if "outputs" in (secure.get("properties") or []):
            tainted.add(name)

    changed = True
    while changed:
        changed = False
        for name, action in catalogue.items():
            if name in tainted:
                continue
            # ADR-039: an XPath sum() over the collection returns a number, and a number
            # cannot carry a row. The template is anchored to the whole expression — see
            # _SCALAR_REDUCTION — so this exempts one pinned shape, not a function name.
            if _is_scalar_reduction(action):
                continue
            for _path, value in _iter_expression_strings(action.get("inputs"), name):
                for referenced, enclosing in _references(value):
                    if referenced in tainted and enclosing not in _REDUCING_FUNCTIONS:
                        tainted.add(name)
                        changed = True
                        break
                if name in tainted:
                    break
    return tainted


def _check_no_serialised_row(definition: dict, personal_entity_sets: set[str]) -> list[Violation]:
    tainted = _row_bearing_actions(definition, personal_entity_sets)
    violations: list[Violation] = []
    for path, _name, action in _iter_actions(definition.get("actions") or {}):
        parameters = ((action.get("inputs") or {}) if isinstance(action.get("inputs"), dict)
                      else {}).get("parameters")
        if not isinstance(parameters, dict):
            continue
        for key, value in parameters.items():
            if key != _RESULT_COLUMN_PARAMETER or not isinstance(value, str):
                continue
            for referenced, enclosing in _references(value):
                if referenced in tainted and enclosing not in _REDUCING_FUNCTIONS:
                    violations.append(Violation(
                        "B1", f"{path}.parameters.{key}",
                        f"the result document references row-bearing action {referenced!r} "
                        f"{'at the top level' if enclosing is None else f'inside {enclosing}()'}",
                        "TAD §3.3 property 6 / §6.3.3 — the document is composed from an "
                        "enumerated field list, never from a serialised row object. Only "
                        f"{sorted(_REDUCING_FUNCTIONS)} may see a row collection, plus "
                        "ADR-039's exact xpath(xml(concat('<r>', if(empty(body('S')), '', "
                        "concat('<v>', join(body('S'), '</v><v>'), '</v>')), '</r>')), "
                        "'sum(/r/v)') template — same S in both positions, that XPath "
                        "expression, that empty guard, nothing else in the expression."))
    return violations


# ── Runner ───────────────────────────────────────────────────────────────────────────

def run(flow_path: Path, solution_root: Path | None) -> int:
    if not flow_path.is_file():
        print(f"flow-reads-no-trigger-body: FAIL — {flow_path} does not exist.\n"
              "  A gate whose target is missing must fail, not pass "
              "(`gate-fires-on-nothing`, x5).", file=sys.stderr)
        return 1
    try:
        document = json.loads(flow_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"flow-reads-no-trigger-body: FAIL — {flow_path} unreadable: {exc}",
              file=sys.stderr)
        return 1

    definition = ((document.get("properties") or {}).get("definition")
                  if isinstance(document, dict) else None)
    if not isinstance(definition, dict):
        print(f"flow-reads-no-trigger-body: FAIL — {flow_path} carries no "
              "properties.definition.", file=sys.stderr)
        return 1

    triggers = definition.get("triggers") or {}
    if not triggers:
        print(f"flow-reads-no-trigger-body: FAIL — {flow_path} declares no trigger. This gate "
              "governs a Dataverse-row-triggered flow; an absent trigger would let every "
              "check below pass vacuously.", file=sys.stderr)
        return 1
    non_row = [name for name, trigger in triggers.items()
               if (trigger or {}).get("type") != _ROW_TRIGGER_TYPE]
    if non_row:
        print(f"flow-reads-no-trigger-body: FAIL — {flow_path} trigger(s) {non_row} are not "
              f"{_ROW_TRIGGER_TYPE}. TAD ADR-038 replaced the Power Apps trigger; a flow that "
              "has reverted to it is not the flow these checks were written for.",
              file=sys.stderr)
        return 1

    notes: list[str] = []
    personal_entity_sets: set[str] = set()
    if solution_root is not None:
        personal_entity_sets, notes = _entity_sets_with_secured_columns(solution_root)

    # An incomplete seed makes check B pass vacuously, which is exactly the
    # `gate-reassures-wrongly` class (x16). So a missing Entities/ tree, an unparseable
    # Entity.xml, or a secured table with no <EntitySetName> is a HARD failure of this gate
    # rather than a note beside a green result.
    for note in notes:
        print(f"  seed: {note}", file=sys.stderr)
    if notes:
        print(f"\nflow-reads-no-trigger-body: FAIL — check B's personal-data seed could not be "
              f"derived completely from {solution_root}. It is derived from source precisely so "
              f"it cannot drift; an incomplete seed would let a serialised row pass unnoticed.",
              file=sys.stderr)
        return 1

    violations = _check_trigger_isolation(definition, list(triggers))
    if solution_root is None:
        print("  note: --solution not given: check B (no serialised row in the result "
              "document) did NOT run", file=sys.stderr)
    else:
        violations += _check_no_serialised_row(definition, personal_entity_sets)

    if violations:
        print(f"\nflow-reads-no-trigger-body: FAIL — {len(violations)} violation(s) in "
              f"{flow_path.name}", file=sys.stderr)
        for violation in violations:
            print(violation.render(), file=sys.stderr)
        return 1

    checks = "A1, A2, A3" if solution_root is None else "A1, A2, A3, B1"
    print(f"flow-reads-no-trigger-body: OK — {flow_path.name}, trigger "
          f"{list(triggers)[0]!r} is a Dataverse row trigger, checks {checks} clean "
          f"({len(personal_entity_sets)} personal-data entity set(s) derived from source).")
    return 0


# ── Selftest fixtures ────────────────────────────────────────────────────────────────

def _wrap(actions: dict, triggers: dict | None = None) -> dict:
    return {"properties": {"definition": {
        "triggers": triggers if triggers is not None else {
            "When_a_refresh_is_requested": {
                "type": _ROW_TRIGGER_TYPE,
                "inputs": {"host": {"connectionName": "shared_commondataserviceforapps",
                                    "operationId": "SubscribeWebhookTrigger"},
                           "parameters": {"subscriptionRequest/message": 3,
                                          "subscriptionRequest/entityname":
                                              "rev_roundstatisticsrequest",
                                          "subscriptionRequest/scope": 4,
                                          "subscriptionRequest/runas": 3}}}},
        "actions": actions}}}


def _list_rows(name: str, entity_set: str, secure: bool = False) -> dict:
    action: dict = {"type": "OpenApiConnection", "runAfter": {},
                    "inputs": {"host": {"operationId": "ListRecords"},
                               "parameters": {"entityName": entity_set}}}
    if secure:
        action["runtimeConfiguration"] = {"secureData": {"properties": ["outputs"]}}
    return {name: action}


def _update_result(expression: str) -> dict:
    return {"Update_the_result_row": {
        "type": "OpenApiConnection", "runAfter": {},
        "inputs": {"host": {"operationId": "UpdateRecord"},
                   "parameters": {"entityName": "rev_roundstatisticsresults",
                                  "recordId": "@{outputs('Read_the_result_row')}",
                                  "item/rev_status": 2,
                                  _RESULT_COLUMN_PARAMETER: expression}}}}


_GOOD = _wrap({
    **_list_rows("List_applications_in_round", "rev_applications", secure=True),
    "Filter_gender_1": {"type": "Query", "runAfter": {},
                        "inputs": {"from": "@outputs('List_applications_in_round')?['body/value']",
                                   "where": "@equals(item()?['rev_gender'], 1)"}},
    "Compose_response_body": {
        "type": "Compose", "runAfter": {},
        "inputs": "@{concat('{\"count\":', string(length(body('Filter_gender_1'))), "
                  "',\"population\":', string(length(outputs('List_applications_in_round')"
                  "?['body/value'])), '}')}"},
    **_update_result("@{outputs('Compose_response_body')}"),
})

_BAD_TRIGGER_BODY = _wrap({
    "Compose": {"type": "Compose", "runAfter": {},
                "inputs": "@{triggerBody()?['rev_name']}"},
})

_BAD_TRIGGER_OUTPUTS = _wrap({
    "Compose": {"type": "Compose", "runAfter": {},
                "inputs": "@triggerOutputs()?['body/rev_roundstatisticsrequestid']"},
})

_BAD_NAMES_ITS_TRIGGER = _wrap({
    "Compose": {"type": "Compose", "runAfter": {},
                "inputs": "@{outputs('When_a_refresh_is_requested')?['body/rev_name']}"},
})

_BAD_MENTIONS_TRIGGER_COLUMN = _wrap({
    "Compose": {"type": "Compose", "runAfter": {},
                "description": "Deliberately does not read rev_triggeredon.",
                "inputs": "@utcNow()"},
})

_BAD_SERIALISED_ROW = _wrap({
    **_list_rows("List_applications_in_round", "rev_applications", secure=True),
    "Compose_response_body": {
        "type": "Compose", "runAfter": {},
        "inputs": "@{string(outputs('List_applications_in_round')?['body/value'])}"},
    **_update_result("@{outputs('Compose_response_body')}"),
})

_BAD_FIRST_ROW = _wrap({
    **_list_rows("List_applications_in_round", "rev_applications", secure=True),
    **_update_result("@{concat('{\"applicant\":', "
                     "string(first(outputs('List_applications_in_round')?['body/value'])), "
                     "'}')}"),
})

_GOOD_SETTING_READ = _wrap({
    **_list_rows("Read_the_stale_after_seconds", "rev_settings"),
    **_update_result("@{concat('{\"staleAfterSeconds\":', "
                     "if(equals(length(body('Read_the_stale_after_seconds')?['value']), 0), "
                     "'null', "
                     "string(int(first(body('Read_the_stale_after_seconds')?['value'])"
                     "?['rev_value']))), '}')}"),
})

# ── ADR-039's money sums: one exempt template, and the near-misses that stay rejected ──
#
# Every case below shares this chain: a secured `List rows`, a presence `Filter array` over it,
# a `Select` projecting one money column per row, a `Compose` summing it, and a composition
# reaching `item/rev_resultjson`. Only the SUM expression differs between them, which is the
# point — it isolates the template as the only thing granting the exemption.

def _money_chain(sum_expression: str) -> dict:
    return _wrap({
        **_list_rows("List_applications_in_round", "rev_applications", secure=True),
        "Filter_cost_present": {
            "type": "Query", "runAfter": {},
            "inputs": {"from": "@outputs('List_applications_in_round')?['body/value']",
                       "where": "@not(equals(item()?['rev_costs'], null))"}},
        "Select_cost_values": {
            "type": "Select", "runAfter": {},
            "inputs": {"from": "@body('Filter_cost_present')",
                       "select": "@string(item()?['rev_costs'])"}},
        "Select_other_values": {
            "type": "Select", "runAfter": {},
            "inputs": {"from": "@body('Filter_cost_present')",
                       "select": "@string(item()?['rev_amountrequested'])"}},
        "Compose_cost_sum": {"type": "Compose", "runAfter": {}, "inputs": sum_expression},
        "Compose_response_body": {
            "type": "Compose", "runAfter": {},
            "inputs": "@{concat('{\"value\":', string(div(float(outputs('Compose_cost_sum')), "
                      "float(max(length(body('Filter_cost_present')), 1)))), '}')}"},
        **_update_result("@{outputs('Compose_response_body')}"),
    })


def _reduction(source: str) -> str:
    return ("@xpath(xml(concat('<r>', "
            f"if(empty(body('{source}')), '', "
            f"concat('<v>', join(body('{source}'), '</v><v>'), '</v>'))"
            ", '</r>')), 'sum(/r/v)')")


_GOOD_XPATH_SUM = _money_chain(_reduction("Select_cost_values"))

# The XPath expression returns a NODE SET rather than a number. Structurally identical to the
# template in every other respect, and the one difference is the whole safety argument.
_BAD_XPATH_NODES = _money_chain(
    _reduction("Select_cost_values").replace("'sum(/r/v)'", "'/r/v'"))

# Two DIFFERENT source actions in the two body() positions. The backreference exists so that a
# reduction cannot quietly sum one collection while claiming to guard another's emptiness.
_BAD_XPATH_MISMATCHED_SOURCE = _money_chain(
    "@xpath(xml(concat('<r>', "
    "if(empty(body('Select_other_values')), '', "
    "concat('<v>', join(body('Select_cost_values'), '</v><v>'), '</v>'))"
    ", '</r>')), 'sum(/r/v)')")

# The UNHARDENED form ADR-039's §5.1.2 writes literally — no empty guard, so an empty subset
# builds `<r><v></v></r>` and XPath 1.0 sum() returns NaN for the whole sum. Rejected here
# because the guard is part of the template, which is how this gate carries the correction.
_BAD_XPATH_UNGUARDED = _money_chain(
    "@xpath(xml(concat('<r><v>', join(body('Select_cost_values'), '</v><v>'), "
    "'</v></r>')), 'sum(/r/v)')")

# The template, followed by a second reference in the same expression. The anchors exist for
# this: a reduction is exempt because of what the WHOLE expression evaluates to.
_BAD_XPATH_PLUS_A_ROW = _money_chain(
    "@concat(" + _reduction("Select_cost_values")[1:]
    + ", string(outputs('List_applications_in_round')?['body/value']))")

_BAD_POWERAPP_TRIGGER = _wrap({"Compose": {"type": "Compose", "runAfter": {},
                                           "inputs": "@utcNow()"}},
                              triggers={"manual": {"type": "Request", "kind": "PowerApp",
                                                   "inputs": {"schema": {}}}})

_BAD_NO_TRIGGER = _wrap({"Compose": {"type": "Compose", "runAfter": {},
                                     "inputs": "@utcNow()"}}, triggers={})


_SECURED_ENTITY_XML = """<?xml version="1.0" encoding="utf-8"?>
<Entity>
  <Name>{logical}</Name>
  <EntityInfo><entity Name="{logical}"><attributes>
    <attribute PhysicalName="rev_name"><IsSecured>0</IsSecured></attribute>
    <attribute PhysicalName="rev_secret"><IsSecured>{secured}</IsSecured></attribute>
  </attributes></entity></EntityInfo>
  <EntitySetName>{entity_set}</EntitySetName>
</Entity>
"""


def _write_solution(root: Path) -> None:
    entities = root / "Entities"
    for logical, entity_set, secured in (
            ("rev_application", "rev_applications", 1),
            ("rev_applicant", "rev_applicants", 1),
            ("rev_setting", "rev_settings", 0),
            ("rev_roundstatisticsresult", "rev_roundstatisticsresults", 0)):
        directory = entities / logical
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "Entity.xml").write_text(
            _SECURED_ENTITY_XML.format(logical=logical, entity_set=entity_set,
                                       secured=secured), encoding="utf-8")


def selftest() -> int:
    cases = [
        ("A1: a triggerBody() read is rejected", _BAD_TRIGGER_BODY, 1),
        ("A1: a triggerOutputs() read is rejected", _BAD_TRIGGER_OUTPUTS, 1),
        ("A2: naming the flow's own trigger in outputs() is rejected",
         _BAD_NAMES_ITS_TRIGGER, 1),
        ("A3: rev_triggeredon in a DESCRIPTION is rejected — §6.3.1 says the column name must "
         "not appear at all, and .notes.md is where the explanation belongs",
         _BAD_MENTIONS_TRIGGER_COLUMN, 1),
        ("B1: string()-ing a personal-data List rows body into rev_resultjson is rejected",
         _BAD_SERIALISED_ROW, 1),
        ("B1: first() on a personal-data List rows body reaching rev_resultjson is rejected — "
         "first() returns a ROW and is deliberately not in the reducing allow-list",
         _BAD_FIRST_ROW, 1),
        ("a reverted Power Apps trigger is rejected", _BAD_POWERAPP_TRIGGER, 1),
        ("a definition with no trigger at all is rejected, not passed vacuously",
         _BAD_NO_TRIGGER, 1),
        ("the real shape PASSES: a secured List rows, a Filter over it, and a composition "
         "that only ever takes length() of either", _GOOD, 0),
        ("a rev_setting read PASSES even though it uses first() — rev_settings carries no "
         "IsSecured=1 column, so it is not row-bearing", _GOOD_SETTING_READ, 0),
        ("B1: ADR-039's xpath(…,'sum(/r/v)') template PASSES — an XPath sum() returns a "
         "number, and a number cannot carry a row", _GOOD_XPATH_SUM, 0),
        ("B1: the same shape with a NODE-returning xpath ('/r/v') is rejected — the exemption "
         "is for a number, not for the function name", _BAD_XPATH_NODES, 1),
        ("B1: the template with two DIFFERENT source actions in its two body() positions is "
         "rejected — the backreference is load-bearing", _BAD_XPATH_MISMATCHED_SOURCE, 1),
        ("B1: the UNGUARDED xpath sum ('<r><v>' + join + '</v></r>') is rejected — an empty "
         "subset makes it NaN, and NaN is not valid JSON", _BAD_XPATH_UNGUARDED, 1),
        ("B1: the template PLUS a second row reference in the same expression is rejected — "
         "the exemption is anchored to the whole expression", _BAD_XPATH_PLUS_A_ROW, 1),
    ]
    checks: list[tuple[str, bool]] = []
    with tempfile.TemporaryDirectory() as tmp:
        solution = Path(tmp) / "solution"
        _write_solution(solution)
        for index, (label, payload, expected) in enumerate(cases):
            flow = Path(tmp) / f"case{index}.json"
            flow.write_text(json.dumps(payload), encoding="utf-8")
            checks.append((label, run(flow, solution) == expected))
        checks.append(("a missing target file FAILS",
                       run(Path(tmp) / "nope.json", solution) == 1))
        malformed = Path(tmp) / "malformed.json"
        malformed.write_text("{not json", encoding="utf-8")
        checks.append(("an unparseable target FAILS", run(malformed, solution) == 1))
        empty = Path(tmp) / "empty.json"
        empty.write_text("{}", encoding="utf-8")
        checks.append(("a target with no properties.definition FAILS", run(empty, solution) == 1))
        # The seed is what makes check B correct. An incomplete one must fail the gate, not
        # produce a green result with a note beside it (`gate-reassures-wrongly`, x16).
        broken_solution = Path(tmp) / "broken-solution"
        _write_solution(broken_solution)
        (broken_solution / "Entities" / "rev_application" / "Entity.xml").write_text(
            "<Entity><unclosed>", encoding="utf-8")
        good = Path(tmp) / "case8.json"
        checks.append(("an UNPARSEABLE Entity.xml FAILS the gate rather than silently "
                       "narrowing check B's seed", run(good, broken_solution) == 1))
        checks.append(("a solution root with no Entities/ tree FAILS for the same reason",
                       run(good, Path(tmp) / "no-such-solution") == 1))

    print("\n── SELFTEST ────────────────────────────────────────────────────────────────")
    for label, passed in checks:
        print(f"  {'PASS' if passed else 'FAIL'}  {label}")
    failed = [check for check in checks if not check[1]]
    if failed:
        print(f"\nflow-reads-no-trigger-body selftest: FAILED — {len(failed)} check(s)",
              file=sys.stderr)
        return 1
    print(f"\nflow-reads-no-trigger-body selftest: OK — {len(checks)} check(s); "
          "the gate can fail.")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("flow", nargs="?", help="path to the flow definition JSON")
    parser.add_argument("--solution", help="solution source root, for check B's derived "
                                          "personal-data entity-set list")
    parser.add_argument("--selftest", action="store_true",
                        help="prove this gate can fail, then exit")
    args = parser.parse_args(argv[1:])
    if args.selftest:
        return selftest()
    if not args.flow:
        parser.print_usage(sys.stderr)
        return 2
    solution = Path(args.solution.rstrip("/")) if args.solution else None
    return run(Path(args.flow), solution)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
