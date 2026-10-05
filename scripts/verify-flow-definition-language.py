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
    return rc or run_check11(corpus)


if __name__ == "__main__":
    sys.exit(main())
