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

WHAT IT CHECKS, per flow definition under the solution root — SEVEN checks:

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
     error-recording path (`IMP-0325`, added 2026-08-26 by improvement review 29 change 3);
  6. in a flow with MORE THAN ONE Response action, no Response accepts `Skipped` in its
     `runAfter` (`IMP-0345`, added 2026-08-28 by improvement review 33 change 1);
  7. a failure branch filtering `@result('<scope>')` for the Failed child does not leave a
     CONTAINER child of that scope undescended (`IMP-0349`, same review).

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
import datetime
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

    # ── 6. A multi-Response flow may not accept `Skipped` on a Response (IMP-0345) ───────
    errors += _check_multi_response_skipped(definition, label)

    # ── 7. result(scope) must descend into container children (IMP-0349) ────────────────
    errors += _check_result_scope_descent(definition, label)
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


# ── check 6 ────────────────────────────────────────────────────────────────────────────────
#
# `IMP-0345`. The fix for defect D-02 gave `REV | Portal | Round Statistics` a `Respond_error`
# whose runAfter was `["Succeeded","Failed","TimedOut","Skipped"]` on `Alert_on_failure`. On a
# SUCCESSFUL run the entire failure chain is Skipped — and because `Skipped` is an ACCEPTED
# status, `Respond_error` executed anyway, after `Respond_ok` had already sent a body. A
# four-Response flow replied twice on its happy path.
#
# The wiring was copied from `REV | Ops | Failure Alert`'s `Respond_to_calling_flow`, which is
# safe for exactly one reason: that flow contains exactly ONE Response action, so nothing has
# already replied. The multi-Response precedent in the same solution —
# `REVIntakeWordPressToDataverse`'s `Respond_500_intake_failed`, with the identical
# `Alert_on_failure` predecessor — deliberately omits `Skipped`, and that is the shape that
# should have been copied.
#
# So the property, independent of the instance: **an always-respond error branch is safe only in
# a flow with exactly one Response action.** Nothing static caught it — check 5 passes and says
# in its own output that it proves a failure path EXISTS, never that it works; `pac solution
# pack` and the hosted Solution Checker both accept it 0/0/0/0/0.
#
# RESIDUAL: this finds NOTHING in today's tree and is reported as a regression lock rather than
# as coverage. IMP-0345's instance was fixed before improvement review 33 opened, and the
# ADR-038 redesign then removed that flow's Response actions altogether. One raw match remains —
# `REV | Ops | Failure Alert`'s single Response, on three predecessors — and the multi-Response
# guard correctly suppresses it. The guard is therefore load-bearing and proven by a real corpus
# case rather than only by a fixture.

def _check_multi_response_skipped(definition: dict, label: str) -> list[str]:
    responses = [(path, action) for path, action in _iter_actions(definition)
                 if action.get("type") == "Response"]
    # De-duplicate by path: _iter_actions yields each action once, but a Response reached through
    # more than one container key would otherwise be counted twice.
    unique = {path for path, _ in responses}
    if len(unique) < 2:
        return []
    errors: list[str] = []
    for path, action in responses:
        run_after = action.get("runAfter")
        if not isinstance(run_after, dict):
            continue
        for predecessor, statuses in run_after.items():
            if isinstance(statuses, list) and "Skipped" in statuses:
                errors.append(
                    f"{label}{path}: a Response action accepts `Skipped` in its runAfter on "
                    f"{predecessor!r}, and this flow has {len(unique)} Response actions. A "
                    "runAfter listing Skipped FIRES when its predecessor is skipped — so on "
                    "every successful run the whole failure chain is Skipped and this Response "
                    "executes anyway, after the success Response has already replied. Safe only "
                    "in a flow with exactly ONE Response (REV | Ops | Failure Alert); in a "
                    "multi-Response flow omit Skipped, as Respond_500_intake_failed does "
                    "(IMP-0345)."
                )
    return errors


# ── check 7 ────────────────────────────────────────────────────────────────────────────────
#
# `IMP-0349`. `REVPortalRoundStatistics`'s `Find_the_failed_action` filters
# `@result('Compute_statistics')` for the child whose status is Failed — correctly avoiding the
# `result(scope)[0]` trap `IMP-0109` recorded. But `result()` returns IMMEDIATE CHILDREN ONLY,
# and `Compute_statistics` wraps a Switch with eight descendants. Any failure inside that Switch
# surfaces as the Switch's own wrapper result, whose message is the platform's "An action failed.
# No dependent actions succeeded." — so the only diagnostic the trustee-facing path produces
# names the wrong action for 8 of the 10 actions that can fail.
#
# The pattern was copied from `REVScoringDailySummary`'s `Summarise` scope, whose six immediate
# children are ALL leaf actions, so filtering result() for the Failed child always reaches the
# leaf there. The two scopes differ in NESTING DEPTH — the one property the pattern depends on.
#
# So the property: **a failure branch filtering result(scope) reaches the real failure only when
# every container among that scope's immediate children is itself descended into by a further
# result() call.**
#
# WHY THE RULE CARRIES A TERMINATE-ONLY EXCLUSION, WHICH IS NOT HOW IT WAS PROPOSED.
# Measured against all five flows before wiring, the literal wording produces FIVE findings, and
# TWO of them are false. Both are `Fail_if_a_setting_row_is_missing` — an If whose only
# descendant is a `Terminate` carrying an explicit `runError` with a code and an authored
# message ("Expected 6 rev_setting rows and found …. Run provisioning/dataverse/seed-settings.ps1
# …"). A Terminate does not produce the platform's opaque wrapper text: the run's error IS the
# message the author wrote, so descending into it with a further result() call would gain
# nothing. Named, because a narrowing that cannot name what it removes is a substitution:
#
#   * REVIntakeWordPressToDataverse  /Create_the_application/Read_configuration/
#                                     Fail_if_a_setting_row_is_missing
#   * REVScoringCalculateAndFlag     /Score_and_flag/Read_configuration/
#                                     Fail_if_a_setting_row_is_missing
#
# Re-measured after the narrowing: 3 findings, 3 true, 0 false.
#
# RESIDUAL: this detects an undescended container, never that the descent produces a USEFUL
# message. And it reads the action tree only — a `result()` call assembled by string
# concatenation is invisible to it.

_CONTAINER_TYPES = {"Scope", "Switch", "If", "Foreach", "Until"}
_RESULT_CALL = re.compile(r"result\(\s*'([^']+)'\s*\)")


def _today() -> str:
    """ISO date, overridable so the self-test can prove the expiry branch fires."""
    return _TODAY_OVERRIDE or datetime.date.today().isoformat()


_TODAY_OVERRIDE: str | None = None

# Check 7 findings suppressed by a declared exception on THIS run. Reset per run() and counted
# in the OK line, because an OK that says "no undescended container" while three are printed
# above it is the `gate-reassures-wrongly` defect this review's cluster G is about.
_SUPPRESSED: list[str] = []

# Check 7's live instances, declared as OWNED, DATED exceptions. Originally three; the
# REVPortalRoundStatistics / Compute_statistics entry was CLEARED 2026-08-30 by descending
# result() at source rather than renewing or widening the waiver (see the removed key's comment
# below) — two remain.
#
# The reviewer confirmed on 2026-08-28 that these stay tracked exceptions rather than build
# blockers: both are pre-existing defects in shipped flows that improvement review 33 did
# not touch, and the build is already red on other gates. An exception suppresses the FAILURE,
# never the REPORT — the C-DOM-031 pattern — so both print on every run, and a THIRD
# instance fails the build immediately.
#
# Keyed on (flow-file stem prefix, scope name) -> the exact container set recorded here. When the
# containers found differ from the set recorded — one fixed, one added — the exception NO LONGER
# APPLIES and the gate fails, so a partial fix forces re-adjudication instead of inheriting a
# stale waiver.
_CHECK7_EXCEPTIONS: dict[tuple[str, str], dict] = {
    ("REVIntakeWordPressToDataverse", "Create_the_application"): {
        "containers": ("Create_or_refresh_the_applicant",
                       "Return_the_existing_reference_if_this_is_a_replay"),
        "owner": "automation-agent",
        "declared": "2026-08-28",
        "expires": "2026-09-30",
        "clearing_action": "add a Find_the_failed_step_inside_<container> Query per container, "
                           "as Describe_the_failure already does for Read_configuration",
    },
    # REVPortalRoundStatistics / Compute_statistics -- CLEARED 2026-08-30 (IMP-0349's own
    # instance, IMP-0483, wbs:6.9). Describe_the_failure now descends result() into
    # Switch_on_open_round_count and, one level deeper, into Condition_page_cap -- the exact
    # clearing action this entry used to name. Verified live: this script's own run over the
    # corpus reports NEITHER container as undescended any more, on the shape's own merits, not
    # by suppression. The reviewer's explicit instruction was to remove the exception entirely
    # rather than re-declare it at a larger hides_at_declaration (improvement review 43 change 3,
    # options (a)/(b) — both rejected). Do not re-add this key without a fresh finding.
    ("REVScoringCalculateAndFlag", "Score_and_flag"): {
        "containers": ("Route_borderline_applications_to_the_process_owner",
                       "Score_each_wellbeing_answer",
                       "Withhold_the_outcome_when_a_scored_answer_is_missing"),
        "owner": "automation-agent",
        "declared": "2026-08-28",
        "expires": "2026-09-30",
        "clearing_action": "same descent, three containers",
    },
}


def _descendant_action_count(action: dict) -> int:
    """How many actions live at ANY depth inside this container, including itself.

    This is an exception's blast radius (IMP-0477): `result()` returns immediate children only, so
    every action nested inside a container a declared result()-descent exception covers is one more
    action whose failure surfaces as the container's wrapper message — 'An action failed. No
    dependent actions succeeded.' — instead of by name.

    Counts the container itself, because it is a real action a failure can be attributed to, and
    reuses `_iter_actions` rather than re-walking the shape: the Switch/If case-and-default nesting
    that `_immediate_children` handles specially is the exact shape a hand-rolled recursion gets
    wrong.
    """
    if not isinstance(action, dict):
        return 0
    return 1 + sum(1 for _ in _iter_actions(action))


def _immediate_children(action: dict) -> dict:
    """Every action `result()` would return as an immediate child of this container."""
    children = dict(action.get("actions") or {})
    if action.get("type") == "Switch":
        for case in (action.get("cases") or {}).values():
            if isinstance(case, dict):
                children.update(case.get("actions") or {})
        default = action.get("default")
        if isinstance(default, dict):
            children.update(default.get("actions") or {})
    if action.get("type") == "If":
        alternative = action.get("else")
        if isinstance(alternative, dict):
            children.update(alternative.get("actions") or {})
    return {name: child for name, child in children.items() if isinstance(child, dict)}


def _is_terminate_only(action: dict) -> bool:
    """True when every LEAF inside this container is a Terminate with an explicit runError.

    Such a container is not a diagnostic black hole: the run's error is the message its author
    wrote, not the platform's "An action failed. No dependent actions succeeded." wrapper. This
    is the narrowing that removes check 7's two measured false positives, both named in the
    comment above.
    """
    leaves: list[dict] = []
    stack = [action]
    while stack:
        node = stack.pop()
        children = _immediate_children(node)
        if children:
            stack.extend(children.values())
        elif node is not action:
            leaves.append(node)
    if not leaves:
        return False
    return all(leaf.get("type") == "Terminate"
               and isinstance((leaf.get("inputs") or {}).get("runError"), dict)
               for leaf in leaves)


def _check_result_scope_descent(definition: dict, label: str) -> list[str]:
    by_name: dict[str, dict] = {}
    for path, action in _iter_actions(definition):
        by_name[path.rsplit("/", 1)[-1]] = action

    # Every result('X') call, and whether its call site filters for the Failed child.
    call_sites: list[tuple[str, str]] = []
    descended: set[str] = set()
    for path, action in _iter_actions(definition):
        inputs = action.get("inputs")
        if inputs is None:
            continue
        text = json.dumps(inputs)
        for match in _RESULT_CALL.finditer(text):
            target = match.group(1)
            descended.add(target)
            if "'Failed'" in text or '"Failed"' in text:
                call_sites.append((path, target))

    errors: list[str] = []
    for path, target in sorted(set(call_sites)):
        scope = by_name.get(target)
        if not isinstance(scope, dict):
            continue
        containers = sorted(
            name for name, child in _immediate_children(scope).items()
            if child.get("type") in _CONTAINER_TYPES and not _is_terminate_only(child))
        undescended = tuple(name for name in containers if name not in descended)
        if not undescended:
            continue

        message = (
            f"{label}{path}: filters @result({target!r}) for the Failed child, and "
            f"{target!r} has container child(ren) {', '.join(undescended)} that no further "
            "result() call descends into. result() returns IMMEDIATE CHILDREN ONLY, so any "
            "failure inside those containers surfaces as the container's own wrapper result — "
            "'An action failed. No dependent actions succeeded.' — and the alert names the "
            "wrapper instead of the action that failed. Recurse result() into the failed child "
            "when that child is itself a container (IMP-0349)."
        )

        exception = None
        expired = None
        for (flow_prefix, scope_name), record in _CHECK7_EXCEPTIONS.items():
            if scope_name == target and flow_prefix in label:
                if tuple(sorted(record["containers"])) == tuple(sorted(undescended)):
                    if _today() > record["expires"]:
                        expired = record
                    else:
                        exception = record
                break

        if expired:
            errors.append(
                f"{message}\n    Its exception EXPIRED on {expired['expires']} "
                f"(owner {expired['owner']}). An exception with no expiry is a waiver; renew it "
                "with a new date and a reason, or clear it."
            )
            continue

        if exception:
            # HOW MUCH DOES THIS EXCEPTION HIDE? Added 2026-08-28 (IMP-0477, review 40 change 13).
            #
            # An owned, dated exception suppresses the FAIL and prints the finding — that part
            # works. What nothing measured is that the exception's BLAST RADIUS grows silently.
            # The REVPortalRoundStatistics exception was declared over a Switch and then a delivery
            # dispatch added 84 actions inside that Switch. No verdict changed, no gate went red,
            # and the "fail-loud" claim resting on the alert naming the failing action got quietly
            # weaker — because result() returns immediate children only, so every action added
            # inside the container is one more thing the wrapper message hides.
            #
            # This asserts on a VALUE and cannot fail a build, which is correct: the exception is
            # owned and dated, and the number is for the human reading the run. Growth from 20
            # hidden actions to 104 is now visible on the run that grew it, not at its expiry.
            hidden = sum(_descendant_action_count(_immediate_children(scope).get(name, {}))
                         for name in undescended)
            _SUPPRESSED.append(
                f"{label}{path} -> {', '.join(undescended)} ({hidden} action(s) hidden)")
            print(f"EXCEPTION (reported, not failed): {message}\n"
                  f"    owner={exception['owner']} declared={exception['declared']} "
                  f"expires={exception['expires']}\n"
                  f"    HIDES {hidden} descendant action(s) across "
                  f"{len(undescended)} container(s) — if this number has grown since the exception "
                  f"was declared, the fail-loud claim resting on it is weaker than it was\n"
                  f"    clearing action: {exception['clearing_action']}", file=sys.stderr)
            continue
        errors.append(message)
    return errors


def run(root: Path) -> int:
    _SUPPRESSED.clear()
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

    suppressed = (
        f" {len(_SUPPRESSED)} check-7 finding(s) are REAL and SUPPRESSED by a declared, owned, "
        f"dated exception, printed above and NOT covered by this OK: "
        f"{'; '.join(_SUPPRESSED)}." if _SUPPRESSED else
        " No check-7 exception was applied, so no undescended container exists.")
    print(f"flow-definition-language: OK — {len(definitions)} flow definition(s) carry no "
          "select()/filter() expression, no alternate-key Row ID, no nested item on an "
          "UpdateRecord, no InitializeVariable below the top level, and no Response accepting "
          "Skipped in a multi-Response flow; and every flow reading a Dataverse table has a "
          "failure branch reaching the error-recording path. NOTE: check 5 proves a failure "
          f"path EXISTS, never that it works — proving that means making the flow fail on "
          f"purpose (IMP-0109).{suppressed}")
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


def _errorlog_write(name: str = "Write_error_log_row", after: str = "List_rows") -> dict:
    """The check-5-satisfying failure branch, so checks 6/7 fixtures are not red on check 5."""
    return {name: {"type": "OpenApiConnection",
                   "runAfter": {after: ["Failed", "TimedOut", "Skipped"]},
                   "inputs": {"host": {"operationId": "CreateRecord"},
                              "parameters": {"entityName": "rev_errorlogs"}}}}


# check 6 — IMP-0345's exact shape: two Responses, and the error Response accepts Skipped, so on
# a successful run the skipped failure chain fires it after the success Response has replied.
_BAD_MULTI_RESPONSE_SKIPPED = _wrap({
    **_read(),
    **_errorlog_write(),
    "Respond_ok": {"type": "Response", "runAfter": {"List_rows": ["Succeeded"]},
                   "inputs": {"statusCode": 200}},
    "Respond_error": {"type": "Response",
                      "runAfter": {"Write_error_log_row": ["Succeeded", "Failed", "TimedOut",
                                                          "Skipped"]},
                      "inputs": {"statusCode": 500}}})

# check 6, GOOD — the SINGLE-Response case, which is REV | Ops | Failure Alert's real shape and
# the one raw corpus match. Accepting Skipped is correct here: nothing has already replied.
_GOOD_SINGLE_RESPONSE_SKIPPED = _wrap({
    **_read(),
    **_errorlog_write(),
    "Respond_to_calling_flow": {
        "type": "Response",
        "runAfter": {"Write_error_log_row": ["Succeeded", "Failed", "TimedOut", "Skipped"]},
        "inputs": {"statusCode": 200}}})

# check 6, GOOD — two Responses, neither accepting Skipped. Respond_500_intake_failed's shape.
_GOOD_MULTI_RESPONSE_NO_SKIPPED = _wrap({
    **_read(),
    **_errorlog_write(),
    "Respond_ok": {"type": "Response", "runAfter": {"List_rows": ["Succeeded"]},
                   "inputs": {"statusCode": 200}},
    "Respond_error": {"type": "Response",
                      "runAfter": {"Write_error_log_row": ["Succeeded", "Failed", "TimedOut"]},
                      "inputs": {"statusCode": 500}}})


def _catch_scope(children: dict, scope: str = "Compute_statistics") -> dict:
    """A catch scope plus the failure branch that filters result() for the Failed child."""
    return {
        scope: {"type": "Scope", "runAfter": {}, "actions": children},
        "Find_the_failed_action": {
            "type": "Query", "runAfter": {scope: ["Failed", "TimedOut", "Skipped"]},
            "inputs": {"from": f"@result('{scope}')",
                       "where": "@equals(item()?['status'], 'Failed')"}},
        **_errorlog_write(after="Find_the_failed_action"),
    }


# check 7 — IMP-0349's exact shape: the catch scope wraps a Switch that no result() descends
# into, so every failure inside it surfaces as the Switch's opaque wrapper result.
_BAD_UNDESCENDED_CONTAINER = _wrap(_catch_scope({
    **_read(),
    "Switch_on_open_round_count": {
        "type": "Switch", "runAfter": {"List_rows": ["Succeeded"]},
        "expression": "@length(body('List_rows')?['value'])",
        "cases": {"None": {"case": 0, "actions": {
            "Compose_nulls": {"type": "Compose", "runAfter": {}, "inputs": None}}}},
        "default": {"actions": {
            "Read_the_round": {"type": "OpenApiConnection", "runAfter": {}, "inputs": {
                "host": {"operationId": "ListRecords"},
                "parameters": {"entityName": "rev_rounds"}}}}}},
}))

# check 7, GOOD — the same shape WITH the descent: a second Query calls result() on the inner
# container, which is the second half of IMP-0109's lesson.
_GOOD_DESCENDED_CONTAINER = _wrap({
    **_catch_scope({
        **_read(),
        "Switch_on_open_round_count": {
            "type": "Switch", "runAfter": {"List_rows": ["Succeeded"]},
            "expression": "@length(body('List_rows')?['value'])",
            "default": {"actions": {
                "Read_the_round": {"type": "OpenApiConnection", "runAfter": {}, "inputs": {
                    "host": {"operationId": "ListRecords"},
                    "parameters": {"entityName": "rev_rounds"}}}}}},
    }),
    "Find_the_failed_step_inside_the_Switch": {
        "type": "Query", "runAfter": {"Find_the_failed_action": ["Succeeded"]},
        "inputs": {"from": "@result('Switch_on_open_round_count')",
                   "where": "@equals(item()?['status'], 'Failed')"}}})

# check 7, GOOD — the TERMINATE-ONLY narrowing, and the reason it exists. This is the corpus's
# two measured false positives in fixture form: an If whose only descendant is a Terminate with
# an authored runError. The run's error is that message, not the platform's opaque wrapper, so
# descending into it would gain nothing.
_GOOD_TERMINATE_ONLY_CONTAINER = _wrap(_catch_scope({
    **_read(),
    "Fail_if_a_setting_row_is_missing": {
        "type": "If", "runAfter": {"List_rows": ["Succeeded"]},
        "expression": {"and": [{"less": ["@length(body('List_rows')?['value'])", 6]}]},
        "actions": {"Stop_run_configuration_incomplete": {
            "type": "Terminate", "runAfter": {},
            "inputs": {"runStatus": "Failed",
                       "runError": {"code": "ConfigurationIncomplete",
                                    "message": "Expected 6 rev_setting rows and found 4."}}}},
        "else": {"actions": {}}},
}))

# check 7, GOOD — the over-firing control. All-leaf children, REVScoringDailySummary's Summarise
# scope, which is the flow the broken pattern was copied FROM and must stay green.
_GOOD_ALL_LEAF_CHILDREN = _wrap(_catch_scope({
    **_read(),
    "Compose_total": {"type": "Compose", "runAfter": {"List_rows": ["Succeeded"]},
                      "inputs": "@length(body('List_rows')?['value'])"},
}, scope="Summarise"))


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
             ("check 6: a multi-Response flow whose error Response accepts Skipped is rejected",
              _BAD_MULTI_RESPONSE_SKIPPED, 1),
             ("check 6: a SINGLE-Response flow accepting Skipped PASSES — REV | Ops | Failure "
              "Alert's real shape, and the one raw corpus match",
              _GOOD_SINGLE_RESPONSE_SKIPPED, 0),
             ("check 6: two Responses, neither accepting Skipped, PASSES",
              _GOOD_MULTI_RESPONSE_NO_SKIPPED, 0),
             ("check 7: a result(scope) failure filter over an undescended Switch is rejected",
              _BAD_UNDESCENDED_CONTAINER, 1),
             ("check 7: the same shape WITH a second result() descending into the Switch PASSES",
              _GOOD_DESCENDED_CONTAINER, 0),
             ("check 7: a container whose only descendant is a Terminate with an authored "
              "runError PASSES — the narrowing that removes the corpus's two false positives",
              _GOOD_TERMINATE_ONLY_CONTAINER, 0),
             ("check 7: a catch scope whose children are ALL leaves PASSES — Summarise, the "
              "flow the broken pattern was copied from", _GOOD_ALL_LEAF_CHILDREN, 0),
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

        # check 7's exception mechanism, both directions, against the REAL corpus paths. An
        # exception that cannot expire is a waiver, so the expiry branch is proven, not asserted.
        corpus = Path("src/solutions/RevitaliseGrantAutomation")
        if corpus.is_dir():
            global _TODAY_OVERRIDE
            checks.append(("check 7: the two declared exceptions suppress the FAILURE today",
                           run(corpus) == 0))
            _TODAY_OVERRIDE = "2099-01-01"
            checks.append(("check 7: an EXPIRED exception fails the build",
                           run(corpus) == 1))
            _TODAY_OVERRIDE = None

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
