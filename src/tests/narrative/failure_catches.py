#!/usr/bin/env python3
"""Generates the failure diagnosis of `REV | Narrative | Scrub Free-Text` (wbs:5.3, NFR-018, FR-010).

Run:  python3 src/tests/narrative/failure_catches.py           # exit 1 if the shipped JSON differs
      python3 src/tests/narrative/failure_catches.py --write   # rewrite the shipped JSON

WHY IT IS GENERATED, AND WHY IT IS SHAPED LIKE THIS (2026-10-09, notes.md "The failure descent").
The designer refused to save the flow: the top-level `Describe_the_failure` descended result() into
containers inside `For_each_column`, and "referencing repetition actions from outside the scope is
supported only when there are no multiple levels of nesting" (InvalidTemplate; check 12 of
scripts/verify-flow-definition-language.py). So the diagnosis is now done INSIDE the iteration that
failed, and carried out of the loop in the `failureTrail` array variable:

  * every container C inside For_each_column gets three LEAF siblings, in the same branch as C:
      Find_the_failed_step_inside_<C>   Query over result('<C>'), runs after C Failed/TimedOut
      Record_the_failure_inside_<C>     appends {in: C, step: <first failed child>, code} to failureTrail
      Rethrow_the_failure_inside_<C>    fails on purpose, so the iteration, the loop and the run
                                        still fail (a loop cannot Terminate; A-NS-27)
    They are leaves, never a Switch: a container among a loop's children would itself need a
    result() descent (check 7), and that descent would have to reach into the loop from outside.
  * the top level reads only result('For_each_column') (For_each_column is in no loop) and the
    trail. From the loop body's first failed child it follows the trail inwards -- entry for that
    container, its step, the entry for THAT step -- until a step has no entry: the leaf. That is the
    old descent's "first failed child at every level", relocated. Taking the first entry instead
    would be wrong: a sibling that tolerates a Skipped predecessor (Detect_shapes_in_the_window) can
    run after a failure, fail in consequence, and record before the outer catch does.
  * a container whose failure is ALREADY handled by design (a sibling runs after it on Failed --
    Validate_the_prompt_answer, whose failure means "invalid answer") gets only the Find query,
    never a record or a rethrow: re-raising it would turn a designed reason into a failed run.
  * a Find query skips children whose failure is handled by design (the extractor call, the prompt
    call, the parse), so a handled failure earlier in the same container is never named instead of
    the real one.

No container is added inside the loop, so the deepest nesting stays 8; the one container added
(`Follow_the_failure_inward`, an Until) sits at depth 2. Nothing is referenced across a loop boundary.

EVERY LOOP ENDS AFTER A FAILURE (2026-10-09, Iteration 6; notes.md "Every loop ends"). Whether the
platform starts the next iteration of a loop after a FAILED one is not documented, and under the
reading where it does, a failed window never advanced `windowStart`, so `Scan_the_column_in_windows`
could re-run the same window -- and its AI Builder calls -- up to its count limit. So:
  * in the body of For_each_column and of every Until inside it, two more LEAVES follow the body's one
    terminal action (the action nothing else in the body runs after):
      Stop_after_a_failure_in_<L>   sets `failureSeen`, runs after the terminal Failed/Skipped/TimedOut.
                                    The terminal is Skipped only when something before it failed, so
                                    this covers a leaf failure that no catch records.
      Rethrow_the_stop_in_<L>       fails on purpose: the stop leaf ran after the failure, so without
                                    it the platform could read the failure as handled.
  * the Until's own `expression` and the column guard (`Scrub_the_column_if_it_has_text`) read
    `failureSeen` and `failureTrail`. They are hand-authored and held by the tests and by check 13 of
    scripts/verify-flow-definition-language.py; this file only asserts that they are there.
  * `Follow_the_failure_inward`'s count is DERIVED: each move goes one recorded container deeper, so
    it moves at most (deepest chain of recorded containers) times and needs one more iteration to see
    there is nothing deeper. Its expression also ends the loop when a move did not happen.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
FLOW = (REPO / "src" / "solutions" / "RevitaliseGrantAutomation" / "Workflows"
        / "REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json")

CONTAINERS = ("If", "Foreach", "Until", "Scope", "Switch")
LOOP = "For_each_column"
TRAIL = "failureTrail"
CURSOR = "failureCursor"
SEEN = "failureSeen"
PREFIXES = ("Find_the_failed_step_inside_", "Record_the_failure_inside_", "Rethrow_the_failure_inside_",
            "Stop_after_a_failure_in_", "Rethrow_the_stop_in_")
FOLLOW_TIMEOUT = "PT2M"   # at most FOLLOW count x 3 in-memory actions; a timeout still holds and alerts
SECURED = {"secureData": {"properties": ["inputs", "outputs"]}}


def _branches(a):
    out = []
    if isinstance(a.get("actions"), dict):
        out.append(a["actions"])
    if isinstance(a.get("else"), dict):
        out.append(a["else"].setdefault("actions", {}))
    for c in (a.get("cases") or {}).values():
        out.append(c.setdefault("actions", {}))
    if isinstance(a.get("default"), dict):
        out.append(a["default"].setdefault("actions", {}))
    return out


def _generated(name):
    return name.startswith(PREFIXES)


def _handled_by_design(branch):
    """Names in this branch that a NON-generated sibling runs after on Failed."""
    out = set()
    for n, a in branch.items():
        if _generated(n):
            continue
        for dep, sts in (a.get("runAfter") or {}).items():
            if "Failed" in sts:
                out.add(dep)
    return out


def _find(c, handled_children):
    where = "@equals(item()?['status'], 'Failed')"
    if handled_children:
        names = ", ".join(f"'{n}'" for n in sorted(handled_children))
        where = (f"@and(equals(item()?['status'], 'Failed'), "
                 f"not(contains(createArray({names}), item()?['name'])))")
    return {
        "type": "Query",
        "runAfter": {c: ["Failed", "TimedOut"]},
        "description": ("Runs only when this container failed, inside the same iteration (a loop cannot be "
                        "read from outside it). Skips handled failures. Secured: results can carry row data."),
        "inputs": {"from": f"@result('{c}')", "where": where},
        "runtimeConfiguration": copy.deepcopy(SECURED),
    }


def _record(c):
    find = f"Find_the_failed_step_inside_{c}"
    return {
        "type": "AppendToArrayVariable",
        "runAfter": {find: ["Succeeded"]},
        "description": ("Which child of this container failed first, and its code, carried out of the loop. "
                        "Never the platform's message: an AI Builder or Dataverse error could quote the narrative."),
        "inputs": {
            "name": TRAIL,
            "value": {
                "in": c,
                "step": f"@{{coalesce(first(body('{find}'))?['name'], 'unknown')}}",
                "code": f"@{{coalesce(first(body('{find}'))?['error']?['code'], 'none')}}",
            },
        },
    }


def _rethrow(c):
    return {
        "type": "Compose",
        "runAfter": {f"Record_the_failure_inside_{c}": ["Succeeded"]},
        "description": ("Fails on purpose so the iteration, the loop and the run still fail: a loop cannot "
                        "Terminate. int() of the recorded step name always throws (A-NS-27)."),
        "inputs": f"@int(last(variables('{TRAIL}'))?['step'])",
    }


def _terminal(branch):
    """The one action in a loop body that no other non-generated action in it runs after."""
    names = [n for n in branch if not _generated(n)]
    used = {d for n in names for d in (branch[n].get("runAfter") or {})}
    ends = [n for n in names if n not in used]
    if len(ends) != 1:
        raise ValueError(f"a loop body must end in exactly one action for its stop leaf; found {ends}")
    return ends[0]


def _stop(owner, branch):
    """The two leaves that end a loop after any failure in an iteration (module docstring)."""
    end = _terminal(branch)
    return {
        f"Stop_after_a_failure_in_{owner}": {
            "type": "SetVariable",
            "runAfter": {end: ["Failed", "Skipped", "TimedOut"]},
            "description": (f"Something in this iteration failed ({end} did not succeed), so no further "
                            "iteration, column or AI Builder call runs: the loop and the column guard read this."),
            "inputs": {"name": SEEN, "value": True},
        },
        f"Rethrow_the_stop_in_{owner}": {
            "type": "Compose",
            "runAfter": {f"Stop_after_a_failure_in_{owner}": ["Succeeded"]},
            "description": ("Fails on purpose, so the failure the stop ran after is not read as handled: the "
                            "iteration, the loop and the run still fail (A-NS-27)."),
            "inputs": f"@int(string(variables('{SEEN}')))",
        },
    }


def _children_handled(a):
    out = set()
    for b in _branches(a):
        out |= _handled_by_design(b)
    return out


def _add_catches(branch, owner=None):
    """Rebuild one branch: strip old generated catches, then add them after every container, and the
    stop leaves when the branch is the body of For_each_column or of an Until inside it."""
    for n in [n for n in branch if _generated(n)]:
        del branch[n]
    handled = _handled_by_design(branch)
    rebuilt = {}
    for n, a in list(branch.items()):
        rebuilt[n] = a
        if a.get("type") not in CONTAINERS:
            continue
        for b in _branches(a):
            _add_catches(b, (n, a))
        rebuilt[f"Find_the_failed_step_inside_{n}"] = _find(n, _children_handled(a))
        if n in handled:
            rebuilt[f"Find_the_failed_step_inside_{n}"]["description"] = (
                "Diagnostic only: this container failing is a designed, handled path, so nothing is recorded "
                "or re-raised. Secured: results can carry row data.")
            continue
        rebuilt[f"Record_the_failure_inside_{n}"] = _record(n)
        rebuilt[f"Rethrow_the_failure_inside_{n}"] = _rethrow(n)
    if owner is not None and (owner[0] == LOOP or owner[1].get("type") == "Until"):
        rebuilt.update(_stop(owner[0], branch))
    branch.clear()
    branch.update(rebuilt)


def recorded_depth(branch):
    """The longest chain of RECORDED containers below this branch: the most moves the trail can make.
    A container whose failure is handled by design is never recorded, and neither is anything in it."""
    handled = _handled_by_design(branch)
    best = 0
    for n, a in branch.items():
        if a.get("type") not in CONTAINERS or n in handled:
            continue
        best = max(best, 1 + max([recorded_depth(b) for b in _branches(a)] or [0]))
    return best


def _check_exits(loop):
    """The hand-authored halves of the stop (module docstring): fail loudly if either is missing."""
    guard = json.dumps(loop["actions"]["Scrub_the_column_if_it_has_text"]["expression"])
    if f"variables('{SEEN}')" not in guard or f"variables('{TRAIL}')" not in guard:
        raise ValueError("Scrub_the_column_if_it_has_text must skip every column once a failure is seen")
    for path, a in _walk(loop["actions"]):
        if a.get("type") == "Until":
            for var in (SEEN, TRAIL):
                if f"variables('{var}')" not in a.get("expression", ""):
                    raise ValueError(f"Until {path} must end once {var} says a failure happened")


def _walk(actions):
    for n, a in actions.items():
        yield n, a
        for b in _branches(a):
            yield from _walk(b)


def _declare(actions, after, name, var, vtype, value, description):
    """Insert one InitializeVariable after `after` in the top-level chain (check 4: one per action)."""
    if name in actions:
        return
    nxt = next(n for n, a in actions.items() if (a.get("runAfter") or {}) == {after: ["Succeeded"]})
    items = list(actions.items())
    actions.clear()
    for n, a in items:
        actions[n] = a
        if n == after:
            actions[name] = {"type": "InitializeVariable", "runAfter": {after: ["Succeeded"]},
                             "description": description,
                             "inputs": {"variables": [{"name": var, "type": vtype, "value": value}]}}
    actions[nxt]["runAfter"] = {name: ["Succeeded"]}


def _top_level(actions, follow_count):
    """The top level reads result('For_each_column') (in no loop) and the trail, never into the loop.

    It follows the trail the way the old descent followed result(): from the loop body's first failed
    child, to the first entry recorded for that container, to ITS first failed child, until a step has
    no entry (a leaf). Following the chain, not taking the first entry, matters: a sibling container
    can run after a failure (a Skipped-tolerant runAfter) and fail in consequence, and its catch
    records before the outer one does."""
    _declare(actions, "Initialise_failure_detail", "Initialise_failure_trail", TRAIL, "array", [],
             "Inside For_each_column, each catch records {in, step, code}: the container, its first failed "
             "child, the code. Names and codes only. The top level cannot read into the loop (check 12).")
    _declare(actions, "Initialise_failure_trail", "Initialise_failure_cursor", CURSOR, "string", "",
             "The step the failure diagnosis has reached while following failureTrail inwards.")
    _declare(actions, "Initialise_failure_cursor", "Initialise_failure_seen", SEEN, "boolean", False,
             "Set once anything inside For_each_column fails. From then on no window, column or AI Builder "
             "call runs. Never reset: a run that saw a failure ends failed, held and alerted.")
    case = actions["Describe_the_failure"]["cases"]["Failed_in_For_each_column"]
    find, entry, leaf = ("Find_the_failed_step_inside_For_each_column", "Find_the_entry_for_the_cursor",
                         "Find_the_entry_naming_the_leaf")
    case["actions"] = {
        find: {
            "type": "Query",
            "runAfter": {},
            "description": ("The loop body's first failed child, from any iteration (A-NS-19). Where it is a "
                            "container, the trail says what failed inside it. Secured: results can carry row data."),
            "inputs": {"from": "@result('For_each_column')", "where": "@equals(item()?['status'], 'Failed')"},
            "runtimeConfiguration": copy.deepcopy(SECURED),
        },
        "Start_at_the_failed_step": {
            "type": "SetVariable",
            "runAfter": {find: ["Succeeded"]},
            "inputs": {"name": CURSOR, "value": f"@{{coalesce(first(body('{find}'))?['name'], 'unknown')}}"},
        },
        "Follow_the_failure_inward": {
            "type": "Until",
            "runAfter": {"Start_at_the_failed_step": ["Succeeded"]},
            "description": ("Moves from a container to the child that failed first inside it, as recorded in the "
                            f"iteration, until the step is a leaf. At most {follow_count - 1} moves, so {follow_count} "
                            "iterations. Ends at once if a move fails."),
            "expression": (f"@or(empty(body('{entry}')), "
                           f"not(equals(variables('{CURSOR}'), outputs('Compose_the_next_step'))))"),
            "limit": {"count": follow_count, "timeout": FOLLOW_TIMEOUT},
            "actions": {
                entry: {
                    "type": "Query",
                    "runAfter": {},
                    "inputs": {"from": f"@variables('{TRAIL}')",
                               "where": f"@equals(item()?['in'], variables('{CURSOR}'))"},
                },
                "Compose_the_next_step": {
                    "type": "Compose",
                    "runAfter": {entry: ["Succeeded"]},
                    "inputs": f"@coalesce(first(body('{entry}'))?['step'], variables('{CURSOR}'))",
                },
                "Move_to_the_next_step": {
                    "type": "SetVariable",
                    "runAfter": {"Compose_the_next_step": ["Succeeded"]},
                    "inputs": {"name": CURSOR, "value": "@outputs('Compose_the_next_step')"},
                },
            },
        },
        leaf: {
            "type": "Query",
            "runAfter": {"Follow_the_failure_inward": ["Succeeded"]},
            "inputs": {"from": f"@variables('{TRAIL}')",
                       "where": f"@equals(item()?['step'], variables('{CURSOR}'))"},
        },
        "Set_failure_detail_from_For_each_column": {
            "type": "SetVariable",
            "runAfter": {leaf: ["Succeeded"]},
            "description": ("Name and code of the leaf that failed. Never the platform's message: an AI Builder or "
                            "Dataverse error could quote the narrative."),
            "inputs": {
                "name": "failureDetail",
                "value": (f"@{{concat('Action: ', variables('{CURSOR}'), ' | Code: ', "
                          f"coalesce(first(body('{leaf}'))?['code'], first(body('{find}'))?['error']?['code'], 'none'))}}"),
            },
        },
    }


def generate(definition: dict) -> dict:
    d = copy.deepcopy(definition)
    actions = d["actions"]
    loop = actions["Scrub_free_text"]["actions"][LOOP]
    _check_exits(loop)
    _top_level(actions, recorded_depth(loop["actions"]) + 1)
    _add_catches(loop["actions"], (LOOP, loop))
    return d


def main(argv):
    doc = json.loads(FLOW.read_text(encoding="utf-8"))
    new = generate(doc["properties"]["definition"])
    if new == doc["properties"]["definition"]:
        print("failure catches: the shipped definition is the generated one.")
        return 0
    if "--write" in argv:
        doc["properties"]["definition"] = new
        FLOW.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"failure catches: rewrote {FLOW.name}.")
        return 0
    print("failure catches: the shipped definition DIFFERS from the generated one; run with --write.",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
