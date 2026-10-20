#!/usr/bin/env python3
"""Solution-wide checks over EVERY cloud flow definition, moved unchanged from test_scrub_flow_definition.py
in Iteration 9 (2026-10-16), when that file was rewritten for the rev 22 scrub flow. They are about the
solution, not the narrative model: the documented platform limits (C-TECH-049) and the trigger-loop proof
behind the Solution Checker triage (IMP-1090).

Run:  python3 -m unittest discover -s src/tests/narrative -p 'test_*.py' -v
Also run by NarrativeRedaction.Tests.ps1 inside the HARD `unit-tests` build step.
"""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import redaction_reference as rr  # noqa: E402

REPO = HERE.parents[2]
FLOW = (REPO / "src" / "solutions" / "RevitaliseGrantAutomation" / "Workflows"
        / "REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json")
DEFINITION = json.loads(FLOW.read_text(encoding="utf-8"))["properties"]["definition"]


class PlatformLimits(unittest.TestCase):
    """Limits the packer does not enforce (C-TECH-049), checked over EVERY flow in the solution.
    Power Automate's documented limits (E2, 'Limits of automated, scheduled, and instant flows'):
    an expression is at most 8,192 characters, actions nest at most 8 deep, a flow holds at most
    500 actions. A breach packs and imports, and fails only when the flow is saved or run.

    Rev 22 (Iteration 9): REVNarrativeScrubFreeText now nests containers 5 deep (A-NS-26 no longer applies
    to it). This test counts CONTAINERS."""

    CONTAINERS = ("If", "Foreach", "Until", "Scope", "Switch")

    def _children(self, a):
        out = dict(a.get("actions") or {})
        out.update((a.get("else") or {}).get("actions") or {})
        for c in (a.get("cases") or {}).values():
            out.update(c.get("actions") or {})
        out.update((a.get("default") or {}).get("actions") or {})
        return out

    def _walk(self, actions, depth, stats):
        for _, a in actions.items():
            stats["count"] += 1
            if a.get("type") in self.CONTAINERS:
                stats["depth"] = max(stats["depth"], depth + 1)
                self._walk(self._children(a), depth + 1, stats)

    def _strings(self, node):
        if isinstance(node, str):
            yield node
        elif isinstance(node, dict):
            for v in node.values():
                yield from self._strings(v)
        elif isinstance(node, list):
            for v in node:
                yield from self._strings(v)

    def test_every_flow_is_within_the_documented_limits(self):
        flows = sorted(FLOW.parent.glob("*.json"))
        manifest = (FLOW.parents[1] / "Other" / "Solution.xml").read_text(encoding="utf-8")
        self.assertEqual(len(flows), manifest.count('<RootComponent type="29"'),
                         "every cloud flow the solution declares is checked (C-TECH-067: both sides from source)")
        for f in flows:
            with self.subTest(f.name):
                d = json.loads(f.read_text(encoding="utf-8"))["properties"]["definition"]
                stats = {"count": 0, "depth": 0}
                self._walk(d["actions"], 0, stats)
                self.assertLessEqual(stats["count"], 500)
                self.assertLessEqual(stats["depth"], 8)
                longest = max((len(s) for s in self._strings(d) if s.startswith("@")), default=0)
                self.assertLessEqual(longest, 8192)



# --- Trigger loops (C-TECH-055 triage of Solution Checker `flow-avoid-recursive-loop`, IMP-1090) ---------
#
# The live Solution Checker flags every Dataverse write to the trigger's own table, whatever the trigger's
# filteringattributes say: it still flags REVSafeguardingActionCompletion after that trigger was filtered
# (IMP-0858, IMP-0948). Whether a flow can actually re-trigger itself, or another flow, is decided by the
# definitions: a Dataverse row-changed trigger with filteringattributes fires only when an update names one
# of those columns, and UpdateRecord sends only the `item/<column>` parameters it is given.

DATAVERSE = "shared_commondataserviceforapps"
# Every Dataverse operation the solution's flows use, classified. An unclassified one fails the test, so a
# new write operation cannot slip past the loop check by being unknown to it.
READ_OPS = {"GetItem", "ListRecords", "SubscribeWebhookTrigger",
            "aibuilderpredict_entityextraction", "aibuilderpredict_customprompt"}
WRITE_OPS = {"UpdateRecord": "update", "UpdateOnlyRecord": "update", "CreateRecord": "create"}
# subscriptionRequest/message: 1 create, 2 delete, 3 update, 4 create or update, 5 create or delete,
# 6 update or delete, 7 all three.
FIRES_ON = {"create": {1, 4, 5, 7}, "update": {3, 4, 6, 7}}

# The 14 actions the 2026-10-07 Solution Checker report (build 20261007-2) names on this flow, as triaged in
# the narrative Dev Summary §4.11. If the flow gains or loses a write to rev_applications, this set and that
# row are both out of date.
CHECKER_FLAGGED = {f"Write_{red}" for _, red in rr.SCRUB_COLUMNS} | {"Write_the_decision", "Hold_the_record_for_review"}


def _dataverse_actions(actions):
    """Every Dataverse connector action at any depth: (name, operationId, parameters)."""
    for name, a in actions.items():
        if not isinstance(a, dict):
            continue
        inputs = a.get("inputs")
        host = inputs.get("host") if isinstance(inputs, dict) else None
        if isinstance(host, dict) and host.get("connectionName") == DATAVERSE:
            yield name, host["operationId"], inputs.get("parameters", {})
        for child in (a.get("actions"), (a.get("else") or {}).get("actions"), (a.get("default") or {}).get("actions")):
            if isinstance(child, dict):
                yield from _dataverse_actions(child)
        for case in (a.get("cases") or {}).values():
            yield from _dataverse_actions(case.get("actions") or {})


def _table_of(entity_set):
    """Entity set name -> logical name, as the flows spell them (rev_applications -> rev_application)."""
    return entity_set[:-1] if entity_set.endswith("s") else entity_set


def trigger_of(definition):
    """(table, messages, filter columns or None for 'any column') for a Dataverse row trigger, else None.

    A trigger `conditions` block is accepted and NOT used to remove edges: a condition can only narrow when a
    flow fires, so ignoring it over-approximates the edges and the loop check stays sound (it may report a
    loop a condition prevents, never miss one). `trigger_conditions_of` returns them for a test to read."""
    for t in definition["triggers"].values():
        p = (t.get("inputs") or {}).get("parameters") or {}
        if "subscriptionRequest/entityname" not in p:
            return None
        cols = p.get("subscriptionRequest/filteringattributes")
        cols = {c.strip() for c in cols.split(",") if c.strip()} if cols else None
        return p["subscriptionRequest/entityname"], {p["subscriptionRequest/message"]}, cols
    return None


def trigger_conditions_of(definition):
    """The `expression` strings of the Dataverse row trigger's `conditions` block ([] when it has none)."""
    for t in definition["triggers"].values():
        if "subscriptionRequest/entityname" in ((t.get("inputs") or {}).get("parameters") or {}):
            return [c.get("expression") for c in t.get("conditions") or []]
    return []


def _column_of(key):
    """`item/<col>` -> column; a lookup is written as `item/<col>@odata.bind`, compared by its column name."""
    return key[len("item/"):].removesuffix("@odata.bind")


def writes_of(definition):
    """[(action, kind, table, columns or None for 'every column')] for every Dataverse write."""
    out = []
    for name, op, params in _dataverse_actions(definition["actions"]):
        if op in READ_OPS:
            continue
        if op not in WRITE_OPS:
            raise AssertionError(f"{name}: Dataverse operation {op} is not classified as a read or a write")
        cols = {_column_of(k) for k in params if k.startswith("item/")}
        whole_body = "item" in params
        out.append((name, WRITE_OPS[op], _table_of(params["entityName"]), None if whole_body else cols))
    return out


def loop_edges(flows):
    """flows: {flow name: definition}. Edge (a, b, action) where action in flow a can fire flow b's trigger."""
    edges = []
    for b, db in flows.items():
        trig = trigger_of(db)
        if trig is None:
            continue
        table, messages, filt = trig
        for a, da in flows.items():
            for action, kind, wtable, cols in writes_of(da):
                if wtable != table or not (messages & FIRES_ON[kind]):
                    continue
                if kind == "update" and filt is not None and cols is not None and not (cols & filt):
                    continue
                edges.append((a, b, action))
    return edges


def cycles(edges):
    """Flows that lie on a cycle (a self-loop included)."""
    graph = {}
    for a, b, _ in edges:
        graph.setdefault(a, set()).add(b)

    def reaches(start, goal, seen):
        for n in graph.get(start, ()):
            if n == goal:
                return True
            if n not in seen:
                seen.add(n)
                if reaches(n, goal, seen):
                    return True
        return False
    return {f for f in graph if reaches(f, f, set())}


def all_flows():
    return {f.name.split("-")[0]: json.loads(f.read_text(encoding="utf-8"))["properties"]["definition"]
            for f in sorted(FLOW.parent.glob("*.json"))}


def _find(definition, action_name):
    for name, _, params in _dataverse_actions(definition["actions"]):
        if name == action_name:
            return params
    raise KeyError(action_name)


class NoTriggerLoop(unittest.TestCase):
    """The Solution Checker's 14 `flow-avoid-recursive-loop` results on this flow are false positives,
    proven here from the definition; each mutation below turns one into a real loop and must fail."""

    def test_the_trigger_is_filtered_to_rev_status_with_no_conditions(self):
        self.assertEqual(trigger_of(DEFINITION), ("rev_application", {3}, {"rev_status"}))

    def test_written_columns_are_disjoint_from_the_trigger_filter(self):
        table, _, filt = trigger_of(DEFINITION)
        own = [(n, cols) for n, _, t, cols in writes_of(DEFINITION) if t == table]
        self.assertTrue(own)
        for name, cols in own:
            with self.subTest(name):
                self.assertIsNotNone(cols, "a whole-row write can name any column")
                self.assertFalse(cols & filt, f"{name} writes {sorted(cols & filt)}, which the trigger listens on")

    def test_the_writes_are_exactly_the_ones_the_checker_flagged(self):
        """The triage row names 14 actions. A new write to rev_applications must be re-triaged."""
        self.assertEqual({n for n, _, t, _ in writes_of(DEFINITION) if t == "rev_application"}, CHECKER_FLAGGED)
        self.assertEqual(len(CHECKER_FLAGGED), 14)

    def test_no_flow_in_the_solution_is_on_a_trigger_loop(self):
        """Self-loops and loops through another flow (this flow and REVSafeguardingActionCompletion both
        trigger on rev_application updates)."""
        flows = all_flows()
        self.assertIn("REVNarrativeScrubFreeText", flows)
        self.assertEqual(cycles(loop_edges(flows)), set())

    # --- mutations: each one makes a real loop, and the checks above must see it ---

    def _mutated(self, change):
        flows = all_flows()
        d = copy.deepcopy(flows["REVNarrativeScrubFreeText"])
        change(d)
        flows["REVNarrativeScrubFreeText"] = d
        return d, flows

    def test_mutation_a_write_that_names_rev_status_is_a_loop(self):
        d, flows = self._mutated(lambda d: _find(d, "Write_the_decision").__setitem__("item/rev_status", 6))
        self.assertIn("REVNarrativeScrubFreeText", cycles(loop_edges(flows)))
        _, _, filt = trigger_of(d)
        self.assertTrue(any(cols & filt for n, _, _, cols in writes_of(d) if n == "Write_the_decision"))

    def test_mutation_an_unfiltered_trigger_is_a_loop(self):
        def drop(d):
            (t,) = d["triggers"].values()
            del t["inputs"]["parameters"]["subscriptionRequest/filteringattributes"]
        _, flows = self._mutated(drop)
        self.assertIn("REVNarrativeScrubFreeText", cycles(loop_edges(flows)))

    def test_mutation_a_whole_row_write_is_a_loop(self):
        _, flows = self._mutated(lambda d: _find(d, "Hold_the_record_for_review").__setitem__("item", {}))
        self.assertIn("REVNarrativeScrubFreeText", cycles(loop_edges(flows)))

    def test_mutation_a_cross_flow_loop_is_found(self):
        """This flow writes the column the safeguarding flow listens on, and that flow writes rev_status."""
        flows = all_flows()
        d = copy.deepcopy(flows["REVNarrativeScrubFreeText"])
        _find(d, "Write_the_decision")["item/rev_safeguardingactioncompleted"] = True
        sg = copy.deepcopy(flows["REVSafeguardingActionCompletion"])
        (params,) = [p for _, op, p in _dataverse_actions(sg["actions"]) if op == "UpdateRecord"]
        params["item/rev_status"] = 6
        flows.update({"REVNarrativeScrubFreeText": d, "REVSafeguardingActionCompletion": sg})
        self.assertEqual(cycles(loop_edges(flows)), {"REVNarrativeScrubFreeText", "REVSafeguardingActionCompletion"})

    def test_mutation_an_unclassified_dataverse_operation_fails(self):
        d, _ = self._mutated(lambda d: None)
        hold = d["actions"]["Hold_the_record_for_review"]
        hold["inputs"]["host"]["operationId"] = "PerformBoundAction"
        with self.assertRaises(AssertionError):
            writes_of(d)

    def test_a_trigger_condition_no_longer_crashes_the_check_and_removes_no_edge(self):
        d, flows = self._mutated(lambda d: next(iter(d["triggers"].values())).__setitem__(
            "conditions", [{"expression": "@true"}]))
        self.assertEqual(trigger_of(d), ("rev_application", {3}, {"rev_status"}))
        self.assertEqual(trigger_conditions_of(d), ["@true"])
        self.assertEqual(cycles(loop_edges(flows)), set())

    def test_a_condition_does_not_hide_a_real_loop(self):
        """Conditions only narrow, so a loop the column filter allows is still reported with one present."""
        def loop(d):
            next(iter(d["triggers"].values())).__setitem__("conditions", [{"expression": "@false"}])
            _find(d, "Write_the_decision")["item/rev_status"] = 6
        _, flows = self._mutated(loop)
        self.assertIn("REVNarrativeScrubFreeText", cycles(loop_edges(flows)))

    def test_safeguarding_flow_has_a_condition_and_is_not_on_a_cycle(self):
        sg = all_flows()["REVSafeguardingActionCompletion"]
        self.assertTrue(trigger_conditions_of(sg))
        self.assertEqual(trigger_of(sg), ("rev_application", {3}, {"rev_safeguardingactioncompleted"}))
        own = [cols for _, _, t, cols in writes_of(sg) if t == "rev_application"]
        self.assertTrue(own)
        for cols in own:
            self.assertFalse(cols & {"rev_safeguardingactioncompleted"})
        self.assertNotIn("REVSafeguardingActionCompletion", cycles(loop_edges(all_flows())))

    def test_a_lookup_write_is_compared_by_column_name_not_odata_bind_key(self):
        sg = all_flows()["REVSafeguardingActionCompletion"]
        cols = {c for _, _, t, cs in writes_of(sg) if t == "rev_application" for c in cs}
        self.assertIn("rev_safeguardingactioncompletedby", cols)
        self.assertFalse([c for c in cols if "@odata" in c])

    def test_mutation_a_lookup_bind_of_a_filtered_column_is_a_loop(self):
        """If the bound lookup IS the column the trigger listens on, stripping the suffix must expose it."""
        flows = all_flows()
        sg = copy.deepcopy(flows["REVSafeguardingActionCompletion"])
        (params,) = [p for _, op, p in _dataverse_actions(sg["actions"]) if op == "UpdateRecord"]
        params["item/rev_safeguardingactioncompleted@odata.bind"] = "/systemusers(x)"
        (t,) = sg["triggers"].values()
        t["conditions"] = []
        flows["REVSafeguardingActionCompletion"] = sg
        self.assertIn("REVSafeguardingActionCompletion", cycles(loop_edges(flows)))



if __name__ == "__main__":
    unittest.main()
