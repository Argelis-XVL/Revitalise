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
    # flagged for its one crossing and not for its two legal look-alikes; and the real narrative
    # flow with the shape the designer refused put back in memory (a top-level result() of a
    # container inside For_each_column) IS flagged, naming that container.
    checks.append(("check 12: the real corpus has no reference into a loop from outside it",
                   check12_findings(real) == []))
    regressed = json.loads(json.dumps(real))
    planted = 0
    for n, flow in regressed.items():
        if n.startswith("REVNarrativeScrubFreeText"):
            flow["properties"]["definition"]["actions"]["Planted_cross_loop_read"] = {
                "type": "Query", "runAfter": {"Scrub_free_text": ["Failed"]},
                "inputs": {"from": "@result('Scrub_the_column_if_it_has_text')",
                           "where": "@equals(item()?['status'], 'Failed')"}}
            planted += 1
    hits = check12_findings(regressed)
    checks.append(("check 12: the refused shape, planted in the narrative flow, is flagged",
                   planted == 1 and len(hits) == 1 and "Scrub_the_column_if_it_has_text" in hits[0]))
    fixture = check12_findings({KNOWN_BAD_CHECK12.name: json.loads(KNOWN_BAD_CHECK12.read_text(encoding="utf-8"))})
    checks.append(("check 12: the known-bad fixture is flagged once, for the If inside the loop only",
                   len(fixture) == 1 and "result('Check_the_item')" in fixture[0]))

    # Check 13. Four assertions, each able to fail: the real corpus is clean; the window scan with its
    # pre-2026-10-09 expression (no failure exit) IS flagged and nothing else is; an Until with its
    # limit removed IS flagged twice (count and timeout); and an Until that makes no external call is
    # NOT held to the failure exit (Follow_the_failure_inward with its exit removed).
    checks.append(("check 13: the real corpus has no Until without a bound or a failure exit",
                   check13_findings(real) == []))

    def _mutate13(change):
        m = json.loads(json.dumps(real))
        hit = 0
        for n, flow in m.items():
            if n.startswith("REVNarrativeScrubFreeText"):
                for path, action in _walk_actions(flow["properties"]["definition"]["actions"]):
                    hit += change(path, action)
        return hit, check13_findings(m)

    def _old_exit(path, a):
        if path.split("/")[-1] == "Scan_the_column_in_windows":
            a["expression"] = "@greaterOrEquals(variables('windowStart'), length(outputs('Compose_raw_text')))"
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
    return rc or rc11 or rc12 or rc13


if __name__ == "__main__":
    sys.exit(main())
