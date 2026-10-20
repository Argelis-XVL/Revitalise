#!/usr/bin/env python3
"""Instance wrapper for the engine's generic verify-flow-definition-language.py (Phase 3f).

THE GENERAL GATE FOR CLASS `platform-contract-guessed-not-groundtruthed` (x16 in
logs/known-failure-modes.md). Checks 1-6's mechanism (nonexistent expression functions,
alternate-key Row IDs, the asymmetric CreateRecord/UpdateRecord connector, InitializeVariable
scoping, the multi-Response Skipped trap, and the failure-path-reaches-error-recording check)
is pure Power Automate/Dataverse platform knowledge and moved to
.engine/scripts/verify-flow-definition-language.py unchanged. Check 7's mechanism (result()
immediate-children-only descent tracking, the terminate-only narrowing) also moved; its
EXCEPTIONS -- three live, dated, owned waivers on this project's actual flows -- stayed here as
config/flow-check7-exceptions.json, since they are actively-managed governance data, not a
platform fact.

Check 5's configuration: this project's error-recording path is `REV | Ops | Failure Alert`
(workflow 8f1c2a44-1004-4b7a-9e21-0a1b2c3d4e04) and the table it writes is `rev_errorlog`.

CHECK 11 -- SECURE OUTPUTS ON A PERSONAL-DATA READ (EX-004, IMP-0951) lives HERE and not in the
engine, because its input is this project's reviewer-ruled list of personal columns
(config/personal-data-columns.json, ruling 2026-09-30) -- project data, not platform knowledge.
A ListRecords/GetItem whose $select names a listed column must carry
runtimeConfiguration.secureData.properties containing "outputs". It reads VALUES (the $select
string and the runtimeConfiguration object), never prose. KNOWN LIMITS, stated so the gate is not
mistaken for more than it is: it does not see a read with NO $select (all columns come back), nor
a column reached through $expand, and it is silent on Dataverse actions other than the two read
operations. It also fails when a listed column is absent from the solution's Entity.xml, so a
renamed column cannot quietly empty the list.

CHECK 12 -- NO REFERENCE INTO A LOOP FROM OUTSIDE IT (IMP-1098) also lives HERE, for now: it is a
platform rule, so its natural home is the engine, but the engine is not this repository's to edit
(improvement-agent proposes the move). The designer refuses to SAVE a flow in which an expression
outside a Foreach/Until calls result(), actions(), outputs() or body() on an action inside it once
more than one level of nesting is involved: "The action '<X>' is nested in a foreach scope of
multiple levels. Referencing repetition actions from outside the scope is supported only when there
are no multiple levels of nesting." (InvalidTemplate, measured on DEV 2026-10-09 against
REVNarrativeScrubFreeText). A solution import of a DRAFT flow does not template-validate, so the
shape packs, imports and passes every other gate. The platform tolerates some single-level shapes;
this check forbids EVERY crossing, which no flow in this solution needs (0 of 9 others has one), so
it cannot be argued around by counting levels. An Until's own `expression` is evaluated inside the
loop and may name its body. KNOWN LIMIT: it reads action names in literal form only -- a name
assembled by concat() is invisible to it.

CHECK 13 -- EVERY UNTIL ENDS, AND ONE THAT CALLS OUT ENDS ON A FAILURE (2026-10-09, Iteration 6 of
the narrative-scrubbing Dev Summary) also lives HERE, for the same reason as check 12. Whether the
platform starts another Until iteration after a FAILED one is not documented. Where it does, a failed
iteration that skipped the step advancing the loop re-runs the same work -- and every connector call
in it -- up to the count limit: `Scan_the_column_in_windows` could have called AI Builder 250 times for
one failed window. Two rules, read off VALUES (the limit object, variables() names, runAfter), never
prose:
  (a) every Until declares `limit.count` (a positive integer) and `limit.timeout` (an ISO 8601
      duration). Leaving either to the platform default hides the bound from the reader;
  (b) an Until whose body makes an external call (a connector, HTTP or child-flow action, at any
      depth) must have a FAILURE EXIT: its `expression` reads a variable that an action DIRECTLY in
      its body sets, and that action runs after a predecessor Failed, Skipped or TimedOut.
KNOWN LIMITS: (b) proves an exit is WIRED, not that it fires for every failure -- the narrative
suite's EveryLoopEndsAfterAFailure executes that. An Until with no external call is held to (a) only:
its cost on a stuck iteration is bounded by its own count. A variable name assembled by concat() is
invisible to it.

CHECKS 14-17 -- SHAPES THAT IMPORT BUT DO NOT SAVE OR DO NOT TURN ON (improvement review 2026-10-16
row 1) also live HERE, beside 12 and 13, and for the same reason: platform rules measured in one tenant,
kept client-specific until a second client meets them (skills/how-to-promote-a-finding.md section 6).
Each reads VALUES off the parsed definition, never prose:
  14. a Switch whose `cases` is missing or empty. The designer's flow checker refuses to save it ("add a
      valid case"); IMP-1095, ten such Switches, DEV 2026-10-08;
  15. a SetVariable whose `inputs.value` is the literal empty string. The checker reports the action as
      having no value; write `@string('')` instead (IMP-1095);
  16. a Recurrence trigger with `schedule.weekDays` set and `frequency` other than `Week`. Day plus weekDays
      imported and would not turn on; the same trigger without weekDays turned on (IMP-1107, V3, DEV
      2026-10-09). Microsoft Learn's workflow definition reference says weekDays applies only to Week;
  17. an `item/<column>` key on CreateRecord, UpdateRecord or UpdateOnlyRecord where <column> is a lookup
      in Entities/*/Entity.xml and the key is not `item/<column>@odata.bind`. A raw GUID into a lookup
      imported and the flow would not turn on (IMP-1105, second instance after IMP-1010);
  18. a Compose whose `runtimeConfiguration.secureData.properties` contains `outputs`. The designer refuses
      to save it: "InvalidSecureDataConfiguration ... These values: 'outputs' are not supported in
      'properties'" (0x80060467, DEV 2026-10-20, narrative Dev Summary Iteration 12 addendum). A Compose's
      outputs ARE its inputs, so `["inputs"]` secures both. Pack and import both accepted it.
KNOWN LIMITS: 15 sees the literal "" only, not a value computed to empty at runtime. 16 does not yet
check hours/minutes against a Month frequency (documented as Day/Week only; held at the 2026-10-16
review's decision D-1, IMP-1124). 17 knows only the lookups this solution's Entity.xml declares, so a
lookup on a table outside the solution is invisible to it. UpdateRecord (upsert) versus UpdateOnlyRecord
is deliberately NOT checked: which one a write needs is a design decision, not a shape error.

USAGE (unchanged from before the split):
    python3 scripts/verify-flow-definition-language.py src/solutions/RevitaliseGrantAutomation
    python3 scripts/verify-flow-definition-language.py --selftest

--selftest runs the engine's synthetic-fixture proof AND this wrapper's own extended proof
against the REAL corpus: that the declared check-7 exceptions leave no check-7 failure today.
The EXPIRY assertion runs against an in-memory corpus carrying the engine's undescended-container
fixture, because a clean real corpus gives an expired exception nothing to uncover (IMP-1059).
The real-corpus assertion cannot live in the engine (it has no access to this solution's actual
flows), so it stays here.

Exits 0 when every definition is clean, 1 on any violation or unreadable input, 2 on a usage
error. C-TECH-052.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import re
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE_SCRIPT = REPO_ROOT / ".engine" / "scripts" / "verify-flow-definition-language.py"

FAILURE_ALERT_WORKFLOW = "8f1c2a44-1004-4b7a-9e21-0a1b2c3d4e04"
ERRORLOG_TABLE = "rev_errorlog"
CHECK7_EXCEPTIONS_PATH = "config/flow-check7-exceptions.json"
CORPUS = REPO_ROOT / "src" / "solutions" / "RevitaliseGrantAutomation"
PERSONAL_COLUMNS_PATH = REPO_ROOT / "config" / "personal-data-columns.json"
KNOWN_BAD_CHECK11 = (REPO_ROOT / "src" / "tests" / "fixtures" / "known-bad"
                     / "flow-secure-personal-read" / "UnsecuredPersonalRead.json")
READ_OPERATIONS = ("ListRecords", "GetItem")
KNOWN_BAD_CHECK12 = (REPO_ROOT / "src" / "tests" / "fixtures" / "known-bad"
                     / "flow-cross-loop-reference" / "CrossLoopReference.json")


def _walk_actions(actions):
    """Yield (path, action) for every action, descending into scopes, conditions, switches, loops."""
    if not isinstance(actions, dict):
        return
    for name, action in actions.items():
        if not isinstance(action, dict):
            continue
        yield name, action
        for sub in _walk_actions(action.get("actions")):
            yield (name + "/" + sub[0], sub[1])
        els = action.get("else")
        if isinstance(els, dict):
            for sub in _walk_actions(els.get("actions")):
                yield (name + "/else/" + sub[0], sub[1])
        for case_name, case in (action.get("cases") or {}).items():
            if isinstance(case, dict):
                for sub in _walk_actions(case.get("actions")):
                    yield (name + "/" + case_name + "/" + sub[0], sub[1])
        default = action.get("default")
        if isinstance(default, dict):
            for sub in _walk_actions(default.get("actions")):
                yield (name + "/default/" + sub[0], sub[1])


def load_personal_columns(path: Path = PERSONAL_COLUMNS_PATH) -> dict[str, str]:
    """column -> table, from the reviewer's list. A missing or empty list is an ERROR, never a pass."""
    data = json.loads(path.read_text(encoding="utf-8"))
    cols = {e["column"]: e["table"] for e in data.get("personal", [])}
    if not cols:
        raise ValueError(f"{path}: no personal columns listed -- a check with no subject must fail")
    return cols


def check11_findings(definitions: dict[str, dict], personal: dict[str, str]) -> list[str]:
    """Findings for check 11 over {label: parsed flow JSON}."""
    findings = []
    for label, flow in definitions.items():
        defn = (flow.get("properties") or {}).get("definition") or flow.get("definition") or {}
        for path, action in _walk_actions(defn.get("actions")):
            inputs = action.get("inputs")
            if not isinstance(inputs, dict):
                continue
            host = inputs.get("host")
            if not isinstance(host, dict) or host.get("operationId") not in READ_OPERATIONS:
                continue
            select = str((inputs.get("parameters") or {}).get("$select") or "")
            cols = {c.strip() for c in select.split(",") if c.strip()}
            hit = sorted(cols & personal.keys())
            if not hit:
                continue
            props = ((action.get("runtimeConfiguration") or {}).get("secureData") or {}).get("properties") or []
            if "outputs" not in props:
                findings.append(
                    f"{label}: action '{path}' reads personal column(s) {', '.join(hit)} but does "
                    f"not set runtimeConfiguration.secureData with 'outputs', so every row it reads "
                    f"is recorded in run history outside Dataverse's column security (check 11, "
                    f"C-DOM-004, NFR-012, EX-004). Add "
                    f'"runtimeConfiguration": {{"secureData": {{"properties": ["inputs", "outputs"]}}}}.')
    return findings


def _load_corpus_flows(corpus: Path) -> dict[str, dict]:
    out = {}
    for f in sorted((corpus / "Workflows").glob("*.json")):
        try:
            out[f.name] = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            out[f.name] = {"__unreadable__": str(exc)}
    return out


def _check_personal_columns_exist(corpus: Path, personal: dict[str, str]) -> list[str]:
    missing = []
    for col, table in personal.items():
        entity = corpus / "Entities" / table / "Entity.xml"
        if not entity.is_file() or f"<Name>{col}</Name>" not in entity.read_text(encoding="utf-8"):
            missing.append(f"config/personal-data-columns.json lists {table}.{col}, which is absent "
                           f"from {entity.relative_to(REPO_ROOT) if entity.is_relative_to(REPO_ROOT) else entity} "
                           f"(check 11) -- a renamed column would otherwise quietly empty the list.")
    return missing


def run_check11(corpus: Path) -> int:
    try:
        personal = load_personal_columns()
    except (OSError, ValueError, KeyError) as exc:
        print(f"ERROR: check 11 cannot read the personal-column list: {exc}", file=sys.stderr)
        return 1
    flows = _load_corpus_flows(corpus)
    errors = [f"{n}: unreadable ({d['__unreadable__']})" for n, d in flows.items() if "__unreadable__" in d]
    flows = {n: d for n, d in flows.items() if "__unreadable__" not in d}
    errors += _check_personal_columns_exist(corpus, personal)
    errors += check11_findings(flows, personal)
    for e in errors:
        print(f"ERROR: {e}", file=sys.stderr)
    if errors:
        print(f"flow-definition-language check 11 (secure outputs on personal-data reads): FAILED -- "
              f"{len(errors)} finding(s).", file=sys.stderr)
        return 1
    print(f"check 11 (secure outputs on personal-data reads): OK -- {len(flows)} flow(s), "
          f"{len(personal)} personal column(s).")
    return 0


_LOOP_TYPES = ("Foreach", "Until")
_ACTION_REF = re.compile(r"\b(result|actions|outputs|body)\s*\(\s*'((?:[^']|'')+)'\s*\)")
_CHILD_KEYS = ("actions", "else", "cases", "default")


def _branches(action: dict):
    """Every child-action dict of a container: actions, else, each case, default."""
    if isinstance(action.get("actions"), dict):
        yield action["actions"]
    if isinstance(action.get("else"), dict):
        yield action["else"].get("actions") or {}
    for case in (action.get("cases") or {}).values():
        if isinstance(case, dict):
            yield case.get("actions") or {}
    if isinstance(action.get("default"), dict):
        yield action["default"].get("actions") or {}


def _index_with_loops(actions, loops=(), out=None) -> dict:
    """name -> (tuple of enclosing loop names, outermost first, action)."""
    out = {} if out is None else out
    for name, action in (actions or {}).items():
        if not isinstance(action, dict):
            continue
        out[name] = (loops, action)
        inner = loops + ((name,) if action.get("type") in _LOOP_TYPES else ())
        for branch in _branches(action):
            _index_with_loops(branch, inner, out)
    return out


def check12_findings(definitions: dict[str, dict]) -> list[str]:
    """Findings for check 12 over {label: parsed flow JSON}: every literal action reference whose
    target sits inside a loop the referencing expression is not itself inside."""
    findings = []
    for label, flow in definitions.items():
        defn = (flow.get("properties") or {}).get("definition") or flow.get("definition") or {}
        index = _index_with_loops(defn.get("actions"))
        for name, (loops, action) in index.items():
            own = {k: v for k, v in action.items() if k not in _CHILD_KEYS}
            scopes = [(loops, {k: v for k, v in own.items() if not (action.get("type") == "Until" and k == "expression")})]
            if action.get("type") == "Until" and "expression" in own:
                scopes.append((loops + (name,), own["expression"]))   # evaluated inside the loop
            for where, node in scopes:
                text = json.dumps(node, ensure_ascii=False)
                for fn, raw in sorted(set(_ACTION_REF.findall(text))):
                    target = raw.replace("''", "'")
                    if target not in index:
                        continue
                    crossed = [loop for loop in index[target][0] if loop not in where]
                    if crossed:
                        findings.append(
                            f"{label}: action '{name}' calls {fn}('{target}'), which is inside loop(s) "
                            f"{', '.join(crossed)} that '{name}' is not inside (check 12, IMP-1098). The "
                            f"designer refuses to save this (InvalidTemplate: 'Referencing repetition "
                            f"actions from outside the scope is supported only when there are no multiple "
                            f"levels of nesting'), and a Draft import does not validate it. Read the value "
                            f"inside the same iteration and carry it out in a variable.")
    return findings


def run_check12(corpus: Path) -> int:
    flows = {n: d for n, d in _load_corpus_flows(corpus).items() if "__unreadable__" not in d}
    errors = check12_findings(flows)
    for e in errors:
        print(f"ERROR: {e}", file=sys.stderr)
    if errors:
        print(f"flow-definition-language check 12 (no reference into a loop from outside it): FAILED -- "
              f"{len(errors)} finding(s).", file=sys.stderr)
        return 1
    print(f"check 12 (no reference into a loop from outside it): OK -- {len(flows)} flow(s).")
    return 0


_EXTERNAL_CALL_TYPES = ("OpenApiConnection", "ApiConnection", "ApiConnectionWebhook", "Http", "HttpWebhook",
                        "Workflow")
_VARIABLE_REF = re.compile(r"\bvariables\s*\(\s*'((?:[^']|'')+)'\s*\)")
_ISO_DURATION = re.compile(r"^P(?=\d|T\d)(\d+D)?(T(?=\d)(\d+H)?(\d+M)?(\d+S)?)?$")
_SETS_VARIABLE = ("SetVariable", "AppendToArrayVariable", "AppendToStringVariable", "IncrementVariable",
                  "DecrementVariable")


def check13_findings(definitions: dict[str, dict]) -> list[str]:
    """Findings for check 13 over {label: parsed flow JSON} (module docstring)."""
    findings = []
    for label, flow in definitions.items():
        defn = (flow.get("properties") or {}).get("definition") or flow.get("definition") or {}
        for path, action in _walk_actions(defn.get("actions")):
            if action.get("type") != "Until":
                continue
            limit = action.get("limit") if isinstance(action.get("limit"), dict) else {}
            count, timeout = limit.get("count"), limit.get("timeout")
            if isinstance(count, bool) or not isinstance(count, int) or count < 1:
                findings.append(f"{label}: Until '{path}' has no explicit positive limit.count ({count!r}); "
                                f"state the bound (check 13a).")
            if not isinstance(timeout, str) or not _ISO_DURATION.match(timeout):
                findings.append(f"{label}: Until '{path}' has no explicit ISO 8601 limit.timeout ({timeout!r}); "
                                f"state the bound (check 13a).")
            body = action.get("actions") if isinstance(action.get("actions"), dict) else {}
            calls = sorted(p for p, a in _walk_actions(body) if a.get("type") in _EXTERNAL_CALL_TYPES)
            if not calls:
                continue
            exits = {(a.get("inputs") or {}).get("name") for a in body.values()
                     if isinstance(a, dict) and a.get("type") in _SETS_VARIABLE
                     and any(isinstance(sts, list) and {"Failed", "Skipped", "TimedOut"} & set(sts)
                             for sts in (a.get("runAfter") or {}).values())}
            read = {v.replace("''", "'") for v in _VARIABLE_REF.findall(json.dumps(action.get("expression")))}
            if not exits & read:
                findings.append(
                    f"{label}: Until '{path}' calls out ({', '.join(calls)}) but its expression has no "
                    f"failure exit (check 13b). If an iteration fails before the step that advances the "
                    f"loop, a platform that keeps iterating re-runs the same calls up to limit.count. Set a "
                    f"variable in the body after the last step Failed/Skipped/TimedOut, and read it in the "
                    f"expression.")
    return findings


def run_check13(corpus: Path) -> int:
    flows = {n: d for n, d in _load_corpus_flows(corpus).items() if "__unreadable__" not in d}
    errors = check13_findings(flows)
    for e in errors:
        print(f"ERROR: {e}", file=sys.stderr)
    if errors:
        print(f"flow-definition-language check 13 (every Until ends, and on a failure): FAILED -- "
              f"{len(errors)} finding(s).", file=sys.stderr)
        return 1
    untils = sum(1 for d in flows.values() for _, a in _walk_actions(
        ((d.get("properties") or {}).get("definition") or {}).get("actions")) if a.get("type") == "Until")
    print(f"check 13 (every Until ends, and on a failure): OK -- {len(flows)} flow(s), {untils} Until loop(s).")
    return 0



_WRITE_OPERATIONS = ("CreateRecord", "UpdateRecord", "UpdateOnlyRecord")
_LOOKUP_ATTRIBUTE = re.compile(
    r'<attribute PhysicalName="([^"]+)">\s*<Type>(?:lookup|customer|owner)</Type>', re.IGNORECASE)


def load_lookup_columns(corpus: Path) -> set[str]:
    """Every lookup column the solution's Entity.xml files declare, lower-cased."""
    found = set()
    for entity in sorted((corpus / "Entities").glob("*/Entity.xml")):
        found |= {m.lower() for m in _LOOKUP_ATTRIBUTE.findall(entity.read_text(encoding="utf-8"))}
    return found


def check14to17_findings(definitions: dict[str, dict], lookups: set[str]) -> list[str]:
    """Findings for checks 14-18 over {label: parsed flow JSON} (module docstring)."""
    findings = []
    for label, flow in definitions.items():
        defn = (flow.get("properties") or {}).get("definition") or flow.get("definition") or {}
        for path, action in _walk_actions(defn.get("actions")):
            kind = action.get("type")
            inputs = action.get("inputs") if isinstance(action.get("inputs"), dict) else {}
            if kind == "Switch" and not action.get("cases"):
                findings.append(f"{label}: Switch '{path}' has no case (check 14, IMP-1095). The designer "
                                f"refuses to save a Switch with only a default; use an If, or drop the Switch.")
            secure = ((action.get("runtimeConfiguration") or {}).get("secureData") or {}).get("properties") \
                if isinstance(action.get("runtimeConfiguration"), dict) else None
            if kind == "Compose" and isinstance(secure, list) and "outputs" in secure:
                findings.append(f"{label}: Compose '{path}' secures 'outputs' (check 18, DEV 2026-10-20). The designer refuses to "
                                f"save it (InvalidSecureDataConfiguration, 0x80060467); a Compose's outputs are its "
                                f"inputs, so secureData.properties ['inputs'] secures both.")
            if kind == "SetVariable" and inputs.get("value") == "":
                findings.append(f"{label}: SetVariable '{path}' sets the literal empty string (check 15, "
                                f"IMP-1095). The designer reports it as having no value; write \"@string('')\".")
            op = (inputs.get("host") or {}).get("operationId") if isinstance(inputs.get("host"), dict) else None
            if op in _WRITE_OPERATIONS:
                for key in (inputs.get("parameters") or {}):
                    column = key[len("item/"):] if key.startswith("item/") else None
                    if column and not column.endswith("@odata.bind") and column.lower() in lookups:
                        findings.append(
                            f"{label}: {op} '{path}' writes lookup column {column} as '{key}' (check 17, "
                            f"IMP-1105). A lookup is written as 'item/{column}@odata.bind' with the value "
                            f"'/<entity set>(<id>)'; the raw form imports and the flow will not turn on.")
        for name, trigger in (defn.get("triggers") or {}).items():
            if not isinstance(trigger, dict) or trigger.get("type") != "Recurrence":
                continue
            recurrence = trigger.get("recurrence") if isinstance(trigger.get("recurrence"), dict) else {}
            schedule = recurrence.get("schedule") if isinstance(recurrence.get("schedule"), dict) else {}
            if schedule.get("weekDays") and recurrence.get("frequency") != "Week":
                findings.append(
                    f"{label}: Recurrence trigger '{name}' sets schedule.weekDays with frequency "
                    f"{recurrence.get('frequency')!r} (check 16, IMP-1107). weekDays applies only to Week; "
                    f"with Day the flow imported and would not turn on. Remove weekDays, or use Week.")
    return findings


def run_check14to17(corpus: Path) -> int:
    flows = {n: d for n, d in _load_corpus_flows(corpus).items() if "__unreadable__" not in d}
    lookups = load_lookup_columns(corpus)
    errors = check14to17_findings(flows, lookups)
    for e in errors:
        print(f"ERROR: {e}", file=sys.stderr)
    if errors:
        print(f"flow-definition-language checks 14-18 (shapes that import but do not save or turn on): "
              f"FAILED -- {len(errors)} finding(s).", file=sys.stderr)
        return 1
    print(f"checks 14-18 (shapes that import but do not save or turn on): OK -- {len(flows)} flow(s), "
          f"{len(lookups)} lookup column(s).")
    return 0


# Checks 14-17's selftest fixture (improvement review 2026-10-16): one bad shape per check, each beside a
# look-alike that must NOT be flagged. Owned here, so a rename in a real flow cannot break the proof (IMP-1122).
_SHAPES_FIXTURE = {"properties": {"definition": {
    "triggers": {
        "Every_weekday_bad": {"type": "Recurrence", "recurrence": {
            "frequency": "Day", "interval": 1, "schedule": {"weekDays": ["Monday"], "hours": ["7"]}}},
        "Every_weekday_good": {"type": "Recurrence", "recurrence": {
            "frequency": "Week", "interval": 1, "schedule": {"weekDays": ["Monday"], "hours": ["7"]}}},
        "Every_day_good": {"type": "Recurrence", "recurrence": {
            "frequency": "Day", "interval": 1, "schedule": {"hours": ["7"], "minutes": [0]}}}},
    "actions": {
        "Switch_with_no_case": {"type": "Switch", "expression": "@variables('x')", "cases": {},
                                "default": {"actions": {}}, "runAfter": {}},
        "Switch_with_a_case": {"type": "Switch", "expression": "@variables('x')", "runAfter": {},
                               "cases": {"One": {"case": 1, "actions": {}}}, "default": {"actions": {}}},
        "Reset_bad": {"type": "SetVariable", "inputs": {"name": "x", "value": ""}, "runAfter": {}},
        "Reset_good": {"type": "SetVariable", "inputs": {"name": "x", "value": "@string('')"}, "runAfter": {}},
        "Compose_secure_bad": {"type": "Compose", "inputs": "@variables('x')", "runAfter": {},
                               "runtimeConfiguration": {"secureData": {"properties": ["inputs", "outputs"]}}},
        "Compose_secure_good": {"type": "Compose", "inputs": "@variables('x')", "runAfter": {},
                                "runtimeConfiguration": {"secureData": {"properties": ["inputs"]}}},
        "Select_secure_good": {"type": "Select", "inputs": {"from": "@createArray(1)", "select": "@item()"},
                               "runAfter": {}, "runtimeConfiguration": {"secureData": {"properties": ["inputs", "outputs"]}}},
        "Write_lookup_bad": {"type": "OpenApiConnection", "runAfter": {}, "inputs": {
            "host": {"operationId": "UpdateRecord"},
            "parameters": {"entityName": "rev_applications", "recordId": "@{guid()}",
                           "item/rev_safeguardingactioncompletedby": "@{guid()}"}}},
        "Write_lookup_good": {"type": "OpenApiConnection", "runAfter": {}, "inputs": {
            "host": {"operationId": "UpdateOnlyRecord"},
            "parameters": {"entityName": "rev_applications", "recordId": "@{guid()}",
                           "item/rev_safeguardingactioncompletedby@odata.bind": "/systemusers(@{guid()})"}}}}}}}

# Check 13's selftest fixture (2026-10-16): two Until loops in the shape the rev 20 narrative scrub flow had
# them - one that calls a connector and has a failure exit, one that calls nothing - so the check's three
# mutation assertions keep a subject now that no real flow has an Until.
_UNTIL_FIXTURE = {"properties": {"definition": {"actions": {
    "Initialise_window_start": {"type": "InitializeVariable", "runAfter": {},
                                "inputs": {"variables": [{"name": "windowStart", "type": "integer", "value": 0}]}},
    "Initialise_failure_seen": {"type": "InitializeVariable", "runAfter": {"Initialise_window_start": ["Succeeded"]},
                                "inputs": {"variables": [{"name": "failureSeen", "type": "boolean", "value": False}]}},
    "Scan_the_column_in_windows": {
        "type": "Until", "runAfter": {"Initialise_failure_seen": ["Succeeded"]},
        "expression": "@or(variables('failureSeen'), greaterOrEquals(variables('windowStart'), 5000))",
        "limit": {"count": 250, "timeout": "PT1H"},
        "actions": {
            "Extract_entities_from_the_window": {"type": "OpenApiConnection", "runAfter": {},
                                                 "inputs": {"host": {"operationId": "aibuilderpredict_entityextraction"}}},
            "Set_window_start": {"type": "SetVariable", "runAfter": {"Extract_entities_from_the_window": ["Succeeded"]},
                                 "inputs": {"name": "windowStart", "value": 5000}},
            "Stop_after_a_failure_in_Scan_the_column_in_windows": {
                "type": "SetVariable", "runAfter": {"Set_window_start": ["Failed", "Skipped", "TimedOut"]},
                "inputs": {"name": "failureSeen", "value": True}}}},
    "Follow_the_failure_inward": {
        "type": "Until", "runAfter": {"Scan_the_column_in_windows": ["Succeeded"]},
        "expression": "@variables('failureSeen')", "limit": {"count": 6, "timeout": "PT2M"},
        "actions": {"Move_to_the_next_step": {"type": "SetVariable", "runAfter": {},
                                              "inputs": {"name": "failureSeen", "value": True}}}}}}}}

def _load_engine():
    name = "_engine_verify_flow_definition_language"
    spec = importlib.util.spec_from_file_location(name, ENGINE_SCRIPT)
    if spec is None or spec.loader is None:
        print(f"ERROR: could not load engine script at {ENGINE_SCRIPT} — is the .engine "
              f"submodule initialized? (git submodule update --init)", file=sys.stderr)
        sys.exit(1)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _extended_selftest(engine) -> int:
    """The real-corpus proof the original script's own selftest carried: the two declared
    check-7 exceptions suppress today, and an artificially future date expires them."""
    if not CORPUS.is_dir():
        print("flow-definition-language wrapper selftest: SKIPPED — no solution tree at "
              f"{CORPUS} (run from the repository root).", file=sys.stderr)
        return 1

    exceptions = engine.load_check7_exceptions(CHECK7_EXCEPTIONS_PATH)
    checks = []

    # These two assertions are about CHECK 7 — that a live exception suppresses its failure and
    # an expired one does not. They must therefore read check 7's own output, NOT the process
    # exit code. Until 2026-09-23 they read `rc == 0`, which asserts the entire corpus is green
    # across all nine checks, and that is a different and much stronger claim than the labels
    # make. It broke the moment check 4 gained its one-variable-per-InitializeVariable assertion
    # (IMP-0820/IMP-0821): that check correctly fails the real corpus on a defect that is still
    # in source and is delivery-agent's to fix, and an unrelated true positive must not be able
    # to falsify check 7's selftest.
    _CHECK7_MARKER = "result() returns IMMEDIATE CHILDREN ONLY"

    def _check7_failures(today: str | None = None, corpus: Path = CORPUS,
                         check7_exceptions: dict | None = None, **run_args) -> int:
        """How many check-7 findings surface as ERRORs (not as suppressed EXCEPTIONs)."""
        # The engine prints ERROR: lines to STDERR, not stdout. Redirecting the wrong stream
        # yields an empty buffer, a count of 0, and a PASS that asserts nothing.
        buffer = io.StringIO()
        with contextlib.redirect_stderr(buffer), contextlib.redirect_stdout(io.StringIO()):
            engine.run(
                corpus,
                failure_alert_workflow=run_args.get("failure_alert_workflow",
                                                    FAILURE_ALERT_WORKFLOW),
                errorlog_table=run_args.get("errorlog_table", ERRORLOG_TABLE),
                check7_exceptions=exceptions if check7_exceptions is None else check7_exceptions,
                today=today,
            )
        return sum(
            1 for line in buffer.getvalue().splitlines()
            if line.startswith("ERROR:") and _CHECK7_MARKER in line
        )

    checks.append(("the declared exceptions suppress the check-7 FAILURE today",
                   _check7_failures() == 0))

    # The EXPIRY assertion runs against a corpus that CONTAINS a check-7 shape, never against
    # the real flows (IMP-1059, review 2026-10-05-3 row 3). Once the real flows were fixed they
    # held nothing for an exception to cover, so an expired exception changed nothing and the
    # assertion failed on a clean corpus. It now uses the engine's own undescended-container
    # fixture and its matching exception, so it fails only if expiry stops working.
    with tempfile.TemporaryDirectory() as tmp:
        shaped = Path(tmp)
        (shaped / "Workflows").mkdir()
        (shaped / "Workflows" / "case.json").write_text(
            json.dumps(engine._BAD_UNDESCENDED_CONTAINER), encoding="utf-8")
        fixture_args = dict(corpus=shaped, check7_exceptions=engine._FX_CHECK7_EXCEPTIONS,
                            failure_alert_workflow=engine._FX_FAILURE_ALERT_WORKFLOW,
                            errorlog_table=engine._FX_ERRORLOG_TABLE)
        live = _check7_failures(today="2026-01-01", **fixture_args)
        lapsed = _check7_failures(today="2099-06-01", **fixture_args)
    checks.append(("a LIVE exception suppresses a check-7 shape (in-memory corpus)", live == 0))
    checks.append(("an EXPIRED exception fails the build (in-memory corpus)", lapsed > 0))

    # Check 11. Three assertions, each able to fail: the real corpus is clean; the known-bad
    # fixture IS flagged (and only its personal-column action); and the real corpus with
    # secureData removed in memory from Create Envelope's Get_the_application IS flagged.
    personal = load_personal_columns()
    real = {n: d for n, d in _load_corpus_flows(CORPUS).items() if "__unreadable__" not in d}
    checks.append(("check 11: the real corpus has no unsecured personal-data read",
                   check11_findings(real, personal) == []))
    bad = {KNOWN_BAD_CHECK11.name: json.loads(KNOWN_BAD_CHECK11.read_text(encoding="utf-8"))}
    bad_findings = check11_findings(bad, personal)
    checks.append(("check 11: the known-bad fixture is flagged, and only for its personal-column action",
                   len(bad_findings) == 1 and "Get_the_application" in bad_findings[0]
                   and "Get_a_setting" not in bad_findings[0]))
    mutated = json.loads(json.dumps(real))
    stripped = 0
    for n, flow in mutated.items():
        if n.startswith("REVAcceptanceCreateEnvelope"):
            for path, action in _walk_actions(flow["properties"]["definition"]["actions"]):
                if path.endswith("Get_the_application"):
                    action.pop("runtimeConfiguration", None)
                    stripped += 1
    checks.append(("check 11: removing secureData from Create Envelope's Get_the_application is flagged",
                   stripped == 1 and len(check11_findings(mutated, personal)) >= 1))
    checks.append(("check 11: every listed personal column exists in Entity.xml",
                   _check_personal_columns_exist(CORPUS, personal) == []))

    # Check 12. Three assertions, each able to fail: the real corpus is clean; the known-bad fixture is
    # flagged for its one crossing and not for its two legal look-alikes; and the same fixture with that
    # one crossing removed in memory is clean, so the finding is caused by the refused shape and nothing
    # else. Improvement review 2026-10-16 (IMP-1122): until then the third assertion planted a read into
    # the live narrative flow by one of its container names, and the rev 22 rebuild's renames broke it
    # although the check was unchanged. Every check-12 assertion now uses a fixture this file owns.
    checks.append(("check 12: the real corpus has no reference into a loop from outside it",
                   check12_findings(real) == []))
    bad12 = json.loads(KNOWN_BAD_CHECK12.read_text(encoding="utf-8"))
    fixture = check12_findings({KNOWN_BAD_CHECK12.name: bad12})
    checks.append(("check 12: the known-bad fixture is flagged once, for the If inside the loop only",
                   len(fixture) == 1 and "result('Check_the_item')" in fixture[0]))
    cleaned = json.loads(json.dumps(bad12))
    removed = cleaned["properties"]["definition"]["actions"].pop("Describe_the_failure", None) is not None
    checks.append(("check 12: the fixture without its one crossing is clean",
                   removed and check12_findings({KNOWN_BAD_CHECK12.name: cleaned}) == []))

    # Checks 14-17. The real corpus is clean; the owned fixture gives exactly one finding per check, each
    # naming its bad action and none naming a look-alike; and the lookup list is read from Entity.xml,
    # not typed, so a check with no lookups to know would fail here rather than pass.
    lookups = load_lookup_columns(CORPUS)
    checks.append(("checks 14-17: Entity.xml declares the lookup the fixture writes",
                   "rev_safeguardingactioncompletedby" in lookups))
    checks.append(("checks 14-18: the real corpus has none of the five shapes",
                   check14to17_findings(real, lookups) == []))
    shapes = check14to17_findings({"ShapesFixture.json": _SHAPES_FIXTURE}, lookups)
    for number, bad_name in (("14", "Switch_with_no_case"), ("15", "Reset_bad"),
                             ("16", "Every_weekday_bad"), ("17", "Write_lookup_bad"), ("18", "Compose_secure_bad")):
        mine = [f for f in shapes if f"(check {number}," in f]
        checks.append((f"check {number}: the fixture's bad shape is flagged once, by name",
                       len(mine) == 1 and bad_name in mine[0]))
    checks.append(("checks 14-18: no look-alike is flagged (five findings in all, none naming a _good action)",
                   len(shapes) == 5 and not any("_good" in f or "Switch_with_a_case" in f for f in shapes)))

    # Check 13. Four assertions, each able to fail: the real corpus is clean; an Until that calls out
    # with its failure exit removed IS flagged and nothing else is; an Until with its limit removed IS
    # flagged twice (count and timeout); and an Until that makes no external call is NOT held to the
    # failure exit. 2026-10-16 (narrative Dev Summary Iteration 9): the rev 22 scrub flow has no Until,
    # so no flow in the real corpus has one, and the three mutations run on the in-memory fixture
    # _UNTIL_FIXTURE below (the rev 20 window scan and failure descent, reduced to their loop shape),
    # added to the real corpus. Before this date they mutated the narrative flow in place. The check is
    # unchanged.
    checks.append(("check 13: the real corpus has no Until without a bound or a failure exit",
                   check13_findings(real) == []))

    def _mutate13(change):
        m = json.loads(json.dumps(real))
        m["UntilFixture.json"] = json.loads(json.dumps(_UNTIL_FIXTURE))
        hit = 0
        for path, action in _walk_actions(m["UntilFixture.json"]["properties"]["definition"]["actions"]):
            hit += change(path, action)
        return hit, check13_findings(m)

    checks.append(("check 13: the fixture as written is clean", _mutate13(lambda p, a: 0) == (0, [])))

    def _old_exit(path, a):
        if path.split("/")[-1] == "Scan_the_column_in_windows":
            a["expression"] = "@greaterOrEquals(variables('windowStart'), 5000)"
            return 1
        return 0
    hit, found = _mutate13(_old_exit)
    checks.append(("check 13: the window scan without its failure exit is flagged, alone",
                   hit == 1 and len(found) == 1 and "Scan_the_column_in_windows" in found[0] and "13b" in found[0]))

    def _no_limit(path, a):
        if path.split("/")[-1] == "Scan_the_column_in_windows":
            a.pop("limit")
            return 1
        return 0
    hit, found = _mutate13(_no_limit)
    checks.append(("check 13: an Until with no limit is flagged for count and timeout",
                   hit == 1 and len(found) == 2 and all("13a" in f for f in found)))

    def _follow_no_exit(path, a):
        if path.split("/")[-1] == "Follow_the_failure_inward":
            a["expression"] = "@equals(1, 1)"
            return 1
        return 0
    hit, found = _mutate13(_follow_no_exit)
    checks.append(("check 13: an Until with no external call is held to its bound only", hit == 1 and found == []))

    print("\n── WRAPPER SELFTEST (real corpus) ─────────────────────────────────────────")
    for label, passed in checks:
        print(f"  {'PASS' if passed else 'FAIL'}  {label}")
    failed = [c for c in checks if not c[1]]
    if failed:
        print(f"\nflow-definition-language wrapper selftest: FAILED — {len(failed)} check(s)",
              file=sys.stderr)
        return 1
    print(f"\nflow-definition-language wrapper selftest: OK — {len(checks)} check(s) against "
          "the real corpus.")
    return 0


def main(argv: list[str] | None = None) -> int:
    engine = _load_engine()
    argv = list(argv if argv is not None else sys.argv[1:])

    if "--selftest" in argv:
        engine_rc = engine.main(["verify-flow-definition-language.py", "--selftest"])
        wrapper_rc = _extended_selftest(engine)
        return engine_rc or wrapper_rc

    if "--failure-alert-workflow" not in argv:
        argv = argv + ["--failure-alert-workflow", FAILURE_ALERT_WORKFLOW]
    if "--errorlog-table" not in argv:
        argv = argv + ["--errorlog-table", ERRORLOG_TABLE]
    if "--check7-exceptions" not in argv:
        argv = argv + ["--check7-exceptions", CHECK7_EXCEPTIONS_PATH]

    rc = engine.main(["verify-flow-definition-language.py", *argv])
    # Check 11 runs on a normal invocation (the first positional argument is the solution root).
    positional = [a for a in argv if not a.startswith("--")]
    corpus = Path(positional[0]) if positional else CORPUS
    if not corpus.is_absolute():
        corpus = REPO_ROOT / corpus
    rc11 = run_check11(corpus)
    rc12 = run_check12(corpus)
    rc13 = run_check13(corpus)
    rc14 = run_check14to17(corpus)
    return rc or rc11 or rc12 or rc13 or rc14


if __name__ == "__main__":
    sys.exit(main())
