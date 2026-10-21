#!/usr/bin/env python3
"""Executes `REV | Finance | Capture Payment` (wbs:8.6, CO-010, ADR-081, US-026) over an in-memory
Dataverse and asserts what is true after each save. Test-only.

WHAT THIS PROVES. The SHIPPED flow definition is run action by action by the repository's WDL
executor (`src/tests/narrative/wdl_sim.py`), against stand-ins for the three tables it touches.
Every acceptance criterion of US-026 that is a statement about the flow's own decisions has a test
below, named by its AC number. The stand-in applies the connector's `$filter`, `$select`, `$orderby`
and `$top`, so a column the flow reads without selecting it, or filters on wrongly, fails here.

WHAT THIS DOES NOT PROVE (V2 at most, nothing ran on the platform). Each of these is an open row
in the Dev Summary section 10 and is closed only by the DEV session of architecture section 12.9:
  A-CP-1 the row trigger fires for Added and for Modified (this suite calls the flow directly);
  A-CP-2 `filteringattributes` naming four secured columns;
  A-CP-3 a DateOnly read as and written from a `yyyy-MM-dd` string (the stand-in speaks that shape,
         so the flow's normalising expression is exercised on it and on a timestamp);
  A-CP-4 concurrency 1 on a row trigger (this suite runs saves one after another, which is what
         concurrency 1 would give; two simultaneous runs are not simulated);
  A-CP-5 `rev_paymentstatus ne 4` returning a Pending payment (the stand-in implements it as written);
  A-CP-6 a null write CLEARS a DateOnly column (the stand-in clears it; the platform is unproven);
  A-CP-7 the flow owner reading secured finance columns and writing the grant's date through team
         membership (narrowed by amendment c: the flow no longer writes rev_payment);
  A-CP-8 WITHDRAWN (amendment c, 2026-10-20): the flow writes nothing to rev_payment, so it starts no
         run of its own making. NoTriggerLoop (src/tests/narrative/test_solution_flows.py) is the gate;
  A-CP-9 the table-scope business rule on rev_payment (date required, Pending to Issued), authored in
         the DEV designer and exported (WI-0136). It is not unit-testable here. This suite asserts only
         that the flow is indifferent to it (the same result for a Pending and an Issued read) and,
         once the exported file exists in source, that it names the three columns (SourceOfRule).
The executor evaluates if() eagerly, the stricter of the two readings the platform leaves open.
"""
from __future__ import annotations

import copy
import json
import re
import sys
import unittest
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / "src" / "tests" / "narrative"))
import wdl_sim  # noqa: E402

FLOW = (REPO / "src" / "solutions" / "RevitaliseGrantAutomation" / "Workflows"
        / "REVFinanceCapturePayment-8F1C2A44-1013-4B7A-9E21-0A1B2C3D4E13.json")
DEFINITION = json.loads(FLOW.read_text(encoding="utf-8"))["properties"]["definition"]

APPROVED, GRANT_PAID, WITHDRAWN = 7, 11, 9
PENDING, ISSUED, CLEARED, CANCELLED = 1, 2, 3, 4
G1, APP1, ZERO = "grant-1", "app-1", "00000000-0000-0000-0000-000000000000"


class Engine(wdl_sim.Engine):
    """The executor plus the one function this flow needs that the narrative flow did not."""

    def f_formatDateTime(self, value, fmt=None):
        self._need_str(value)
        if fmt != "yyyy-MM-dd":
            raise wdl_sim.Unsupported(f"formatDateTime format {fmt!r}")
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%Y-%m-%d")
        except ValueError as e:  # a null or empty string reaches here as the platform's thrown error
            raise wdl_sim.WdlError(f"formatDateTime of {value!r}") from e


class World:
    """Three tables, the connector over them, and a record of everything the flow did."""

    def __init__(self, application_status=APPROVED, grant=True, grant_status=3):
        self.payments = {}
        self.grants = {G1: {"rev_grantid": G1, "rev_name": "REV-2026-001", "rev_finalpaymentdate": None, "rev_status": grant_status,
                            "_rev_applicationid_value": APP1}} if grant else {}
        self.apps = {APP1: {"rev_applicationid": APP1, "rev_status": application_status}}
        self.writes, self.messages, self.alerts, self.reads = [], [], [], []
        self.fail = set()      # operation names the stand-in refuses

    def payment(self, pid, final=False, date=None, status=PENDING, grant=G1, ref=None):
        self.payments[pid] = {"rev_paymentid": pid, "rev_name": ref or f"PAY-{pid}",
                              "_rev_grantid_value": grant, "rev_isfinalpayment": final,
                              "rev_paymentdate": date, "rev_paymentstatus": status}
        return self

    # connector ---------------------------------------------------------------------------------
    def table(self, entity):
        return {"rev_payments": self.payments, "rev_grants": self.grants, "rev_applications": self.apps}[entity]

    @staticmethod
    def matches(row, clause):
        col, op, val = clause.split(" ", 2)
        have = row.get(col)
        want = {"true": True, "false": False, "null": None}.get(val, val)
        if isinstance(want, str) and re.fullmatch(r"-?\d+", want):
            want = int(want)
        return (have == want) if op == "eq" else (have != want)

    def connector(self, name, op, params):
        if name in self.fail:
            raise wdl_sim.ConnectorFailure(f"{name} refused")
        if op == "ListRecords":
            self.reads.append((name, params))
            rows = [r for r in self.table(params["entityName"]).values()
                    if all(self.matches(r, c) for c in params["$filter"].split(" and "))]
            if "$orderby" in params:
                col, direction = params["$orderby"].split(" ")
                rows.sort(key=lambda r: r[col], reverse=direction == "desc")
            rows = rows[: params.get("$top", len(rows))]
            keep = set(params["$select"].split(","))
            return {"value": [{k: v for k, v in r.items() if k in keep} for r in rows]}
        if op == "UpdateOnlyRecord":
            row = self.table(params["entityName"]).get(params["recordId"])
            if row is None:
                raise wdl_sim.ConnectorFailure("row not found")
            items = {k[5:]: v for k, v in params.items() if k.startswith("item/")}
            assert not any(k.endswith("@odata.bind") for k in items), "no lookup is written"
            self.writes.append((name, params["entityName"], params["recordId"], items))
            row.update(items)             # A-CP-6: a null clears the column
            return dict(row)
        if op == "PostMessageToConversation":
            self.messages.append((params["body/recipient"], params["body/messageBody"]))
            return {}
        raise AssertionError(f"unexpected connector call {name} {op}")

    # a save ------------------------------------------------------------------------------------
    def save(self, pid, created_on="2026-11-18T09:00:00Z", alert_upn="finance@example.org"):
        row = self.payments[pid]
        trigger = {**row, "createdon": created_on}
        self.writes, self.messages, self.alerts = [], [], []
        eng = Engine(copy.deepcopy(DEFINITION), trigger, parameters={"rev_FinanceAlertUpn": alert_upn},
                     connector=self.connector, child_flow=lambda n, b: self.alerts.append((n, b)))
        status = eng.run()
        return Result(status, list(self.writes), list(self.messages), list(self.alerts), eng)

    def grant_date(self):
        return self.grants[G1]["rev_finalpaymentdate"]

    def grant_status(self):
        return self.grants[G1]["rev_status"]

    def app_status(self):
        return self.apps[APP1]["rev_status"]


class Result:
    def __init__(self, status, writes, messages, alerts, engine):
        self.status, self.writes, self.messages, self.alerts, self.engine = status, writes, messages, alerts, engine

    def wrote(self, entity):
        return [w for w in self.writes if w[1] == entity]

    @property
    def silent(self):
        return not self.writes and not self.messages and not self.alerts


class UsAc(unittest.TestCase):
    """US-026 acceptance criteria, one test each."""

    def test_ac1_a_dated_final_payment_sets_the_date_and_moves_the_application(self):
        w = World().payment("p1", final=True, date="2026-11-14", status=ISSUED)
        r = w.save("p1")
        self.assertEqual(r.status, "Succeeded")
        self.assertEqual((w.grant_date(), w.app_status()), ("2026-11-14", GRANT_PAID))
        self.assertTrue(r.silent is False and not r.messages and not r.alerts)

    def test_ac2_the_date_is_the_payments_own_not_the_day_it_was_entered(self):
        w = World().payment("p1", final=True, date="2026-11-14", status=ISSUED)
        w.save("p1", created_on="2026-11-18T09:00:00Z")
        self.assertEqual(w.grant_date(), "2026-11-14")

    def test_ac3_a_non_final_instalment_changes_nothing(self):
        w = World().payment("p1", date="2026-11-14").payment("p2", date="2026-11-20")
        r = w.save("p2")
        self.assertEqual((w.grant_date(), w.app_status()), (None, APPROVED))
        self.assertTrue(r.silent, r.writes)

    def test_ac3_a_non_final_instalment_leaves_a_grant_that_already_matches_alone(self):
        w = World(application_status=GRANT_PAID, grant_status=4)
        w.grants[G1]["rev_finalpaymentdate"] = "2026-11-14"
        w.payment("p1", final=True, date="2026-11-14", status=ISSUED).payment("p2", date="2026-11-20")
        self.assertTrue(w.save("p2").silent)
        self.assertEqual((w.grant_date(), w.app_status()), ("2026-11-14", GRANT_PAID))

    def test_ac4_saving_a_final_payment_again_changes_nothing(self):
        w = World().payment("p1", final=True, date="2026-11-14", status=ISSUED)
        w.save("p1")
        again = w.save("p1")
        self.assertTrue(again.silent, again.writes)
        self.assertEqual((w.grant_date(), w.app_status()), ("2026-11-14", GRANT_PAID))

    def test_ac5_two_final_payments_the_later_date_wins_in_either_save_order(self):
        for order in (("p1", "p2"), ("p2", "p1")):
            with self.subTest(order=order):
                w = (World().payment("p1", final=True, date="2026-11-14", status=ISSUED)
                     .payment("p2", final=True, date="2026-12-02", status=ISSUED))
                for p in order:
                    w.save(p)
                self.assertEqual(w.grant_date(), "2026-12-02")

    def test_ac6_unticking_the_only_final_payment_clears_the_date_and_reverts_the_application(self):
        w = World().payment("p1", final=True, date="2026-11-14")
        w.save("p1")
        w.payments["p1"]["rev_isfinalpayment"] = False
        r = w.save("p1")
        self.assertEqual((w.grant_date(), w.app_status()), (None, APPROVED))
        self.assertEqual(r.status, "Succeeded")

    def test_ac7_cancelling_the_only_final_payment_does_the_same_and_reports_it(self):
        w = World().payment("p1", final=True, date="2026-11-14")
        w.save("p1")
        w.payments["p1"]["rev_paymentstatus"] = CANCELLED
        r = w.save("p1")
        self.assertEqual((w.grant_date(), w.app_status()), (None, APPROVED))
        self.assertEqual(w.payments["p1"]["rev_paymentstatus"], CANCELLED, "a Cancelled payment is never written")
        self.assertFalse(r.wrote("rev_payments"))
        self.assertEqual(len(r.messages), 1)
        self.assertIn("Cancelled", r.messages[0][1])

    def test_ac8_correcting_the_date_re_records_it(self):
        w = World().payment("p1", final=True, date="2026-11-14")
        w.save("p1")
        w.payments["p1"]["rev_paymentdate"] = "2026-11-12"
        w.save("p1")
        self.assertEqual(w.grant_date(), "2026-11-12")
        self.assertEqual(w.app_status(), GRANT_PAID)

    def test_a_remaining_final_payment_keeps_the_grant_dated_when_another_is_unticked(self):
        w = (World().payment("p1", final=True, date="2026-11-14", status=ISSUED)
             .payment("p2", final=True, date="2026-12-02", status=ISSUED))
        w.save("p1"), w.save("p2")
        w.payments["p2"]["rev_isfinalpayment"] = False
        w.save("p2")
        self.assertEqual((w.grant_date(), w.app_status()), ("2026-11-14", GRANT_PAID))

    def test_ac9_a_final_payment_with_no_grant_is_reported_and_nothing_else_changes(self):
        w = World(grant=False).payment("p1", final=True, date="2026-11-14", grant="")
        r = w.save("p1")
        self.assertEqual(r.status, "Succeeded")
        self.assertFalse(r.writes)
        self.assertEqual((len(r.messages), len(r.alerts)), (1, 1))
        self.assertIn("not linked to a grant", r.messages[0][1])
        self.assertIn("PAY-p1", r.messages[0][1])
        self.assertEqual(r.alerts[0][1]["text_4"], "Warning")

    def test_ac9_a_payment_with_no_grant_that_is_not_final_is_not_reported(self):
        w = World(grant=False).payment("p1", grant="")
        self.assertTrue(w.save("p1").silent)

    def test_ac10_a_withdrawn_application_keeps_its_status_the_date_is_recorded_and_it_is_reported(self):
        w = World(application_status=WITHDRAWN).payment("p1", final=True, date="2026-11-14", status=ISSUED)
        r = w.save("p1")
        self.assertEqual((w.grant_date(), w.app_status()), ("2026-11-14", WITHDRAWN))
        self.assertFalse(r.wrote("rev_applications"))
        self.assertEqual((len(r.messages), len(r.alerts)), (1, 1))
        self.assertIn("Withdrawn", r.messages[0][1], "the status is named")

    def test_ac10_it_is_reported_once_when_the_date_was_written_not_on_every_later_save(self):
        w = World(application_status=WITHDRAWN).payment("p1", final=True, date="2026-11-14", status=ISSUED)
        w.save("p1")
        self.assertTrue(w.save("p1").silent)

    def test_ac10_an_unticked_payment_on_a_moved_on_application_is_reported_when_the_date_clears(self):
        w = World(application_status=WITHDRAWN).payment("p1", final=True, date="2026-11-14", status=ISSUED)
        w.save("p1")
        w.payments["p1"]["rev_isfinalpayment"] = False
        r = w.save("p1")
        self.assertEqual((w.grant_date(), w.app_status()), (None, WITHDRAWN))
        self.assertEqual(len(r.messages), 1)

    def test_ac12_an_undated_final_payment_starts_no_clock_and_is_reported(self):
        w = World().payment("p1", final=True, date=None)
        r = w.save("p1")
        self.assertEqual((w.grant_date(), w.app_status()), (None, APPROVED))
        self.assertFalse(r.writes)
        self.assertEqual(len(r.messages), 1)
        self.assertIn("no payment date", r.messages[0][1])
        self.assertIn("Add the payment date", r.messages[0][1])

    def test_ac12_an_undated_final_payment_does_not_disturb_a_clock_another_payment_started(self):
        w = (World().payment("p1", final=True, date="2026-11-14", status=ISSUED)
             .payment("p2", final=True, date=None))
        w.save("p1")
        r = w.save("p2")
        self.assertEqual((w.grant_date(), w.app_status()), ("2026-11-14", GRANT_PAID))
        self.assertFalse(r.writes)
        self.assertEqual(len(r.messages), 1)

    def test_ac13_the_issued_mark_is_not_the_flows_the_recompute_is_identical_for_pending_and_issued(self):
        """Amendment c: the payment rule sets Issued inside the save; the flow reads Pending or Issued and
        reaches the same grant, grant status and application, and writes nothing to rev_payment."""
        results = {}
        for status in (PENDING, ISSUED):
            w = World().payment("p1", final=True, date="2026-11-14", status=status)
            r = w.save("p1")
            self.assertEqual(r.status, "Succeeded")
            self.assertFalse(r.wrote("rev_payments"), "no action writes rev_payment")
            self.assertEqual(w.payments["p1"]["rev_paymentstatus"], status, "the status is left exactly as read")
            results[status] = ((w.grant_date(), w.grant_status(), w.app_status()),
                               [(n, e, items) for n, e, _, items in r.writes], len(r.messages), len(r.alerts))
        self.assertEqual(results[PENDING], results[ISSUED])
        self.assertEqual(results[PENDING][0], ("2026-11-14", 4, GRANT_PAID))
        self.assertEqual([x[0] for x in results[PENDING][1]], ["Write_the_grant_date", "Write_the_application_status"])

    def test_ac14_a_cleared_payment_stays_cleared(self):
        w = World().payment("p1", final=True, date="2026-11-14", status=CLEARED)
        r = w.save("p1")
        self.assertEqual(w.payments["p1"]["rev_paymentstatus"], CLEARED)
        self.assertFalse(r.wrote("rev_payments"))
        self.assertEqual((w.grant_date(), w.app_status()), ("2026-11-14", GRANT_PAID))

    def test_an_issued_payment_stays_issued_and_is_not_written(self):
        w = World().payment("p1", final=True, date="2026-11-14", status=ISSUED)
        self.assertFalse(w.save("p1").wrote("rev_payments"))

    def test_ac15_unticking_final_reverts_the_grant_and_the_application_and_leaves_the_payment_as_it_is(self):
        w = World().payment("p1", final=True, date="2026-11-14", status=ISSUED)
        w.save("p1")
        w.payments["p1"]["rev_isfinalpayment"] = False
        r = w.save("p1")
        self.assertEqual((w.grant_date(), w.app_status()), (None, APPROVED))
        self.assertEqual(w.payments["p1"]["rev_paymentstatus"], ISSUED, "OQ-059: never reverted to Pending, and never written")
        self.assertFalse(r.wrote("rev_payments"))


class GrantStatus(unittest.TestCase):
    """Reviewer addition 2026-10-20: the grant itself moves Acceptance Signed (3) to Paid (4) with the date, and back."""

    def test_a_final_payment_moves_the_grant_to_paid_in_the_same_write_as_the_date(self):
        w = World().payment("p1", final=True, date="2026-11-14", status=ISSUED)
        r = w.save("p1")
        self.assertEqual((w.grant_date(), w.grant_status(), w.app_status()), ("2026-11-14", 4, GRANT_PAID))
        self.assertEqual(len(r.wrote("rev_grants")), 1)
        self.assertEqual(r.wrote("rev_grants")[0][3], {"rev_finalpaymentdate": "2026-11-14", "rev_status": 4})

    def test_removing_the_final_mark_returns_the_grant_to_acceptance_signed(self):
        w = World().payment("p1", final=True, date="2026-11-14")
        w.save("p1")
        w.payments["p1"]["rev_isfinalpayment"] = False
        w.save("p1")
        self.assertEqual((w.grant_date(), w.grant_status()), (None, 3))

    def test_a_repeat_save_does_not_write_the_grant(self):
        w = World().payment("p1", final=True, date="2026-11-14", status=ISSUED)
        w.save("p1")
        self.assertTrue(w.save("p1").silent)

    def test_a_status_left_behind_by_a_stopped_run_is_finished_by_the_next_save(self):
        w = World(grant_status=3).payment("p1", final=True, date="2026-11-14", status=ISSUED)
        w.grants[G1]["rev_finalpaymentdate"] = "2026-11-14"      # date written, status not
        w.save("p1")
        self.assertEqual(w.grant_status(), 4)

    def test_another_grant_status_is_left_alone_and_reported_while_the_date_is_still_recorded(self):
        for status in (1, 2):
            with self.subTest(status=status):
                w = World(grant_status=status).payment("p1", final=True, date="2026-11-14", status=ISSUED)
                r = w.save("p1")
                self.assertEqual((w.grant_date(), w.grant_status()), ("2026-11-14", status))
                self.assertEqual(len(r.messages), 1)
                self.assertIn("grant itself", r.messages[0][1])

    def test_a_paid_grant_with_another_final_payment_stays_paid_when_one_is_unticked(self):
        w = (World().payment("p1", final=True, date="2026-11-14", status=ISSUED)
             .payment("p2", final=True, date="2026-12-02", status=ISSUED))
        w.save("p1"), w.save("p2")
        w.payments["p2"]["rev_isfinalpayment"] = False
        w.save("p2")
        self.assertEqual((w.grant_status(), w.grant_date()), (4, "2026-11-14"))

    def test_the_grant_write_carries_the_date_as_null_and_the_status_together_on_reversal(self):
        w = World().payment("p1", final=True, date="2026-11-14", status=ISSUED)
        w.save("p1")
        w.payments["p1"]["rev_isfinalpayment"] = False
        r = w.save("p1")
        (_, _, _, items), = r.wrote("rev_grants")
        self.assertEqual(items, {"rev_finalpaymentdate": None, "rev_status": 3})

    def test_a_paid_grant_hand_set_with_no_final_payment_returns_to_signed_on_the_next_save(self):
        """A-R100 as widened by amendment b: the case the pre-PRD listing exists to find."""
        w = World(application_status=GRANT_PAID, grant_status=4).payment("p2", date="2026-11-20")
        w.save("p2")
        self.assertEqual(w.grant_status(), 3)

    def test_the_report_on_grant_status_one_or_two_fires_only_where_the_date_is_written_or_cleared(self):
        w = World(grant_status=2).payment("p1", final=True, date="2026-11-14", status=ISSUED).payment("p2", date="2026-11-20")
        self.assertEqual(len(w.save("p1").messages), 1)
        self.assertTrue(w.save("p2").silent, "an unrelated instalment later does not repeat the report")
        w.payments["p1"]["rev_isfinalpayment"] = False
        self.assertEqual(len(w.save("p1").messages), 1, "reported again where the date is cleared")

    def test_no_write_ever_moves_a_grant_to_awarded_or_acceptance_issued(self):
        for gs in (1, 2, 3, 4):
            for final in (True, False):
                w = World(grant_status=gs).payment("p1", final=final, date="2026-11-14", status=ISSUED)
                for _, e, _, items in w.save("p1").writes:
                    if e == "rev_grants" and items["rev_status"] != gs:
                        self.assertIn(items["rev_status"], (3, 4))

    def test_a_grant_never_written_to_any_status_but_three_or_four(self):
        for gs in (1, 2, 3, 4):
            for final in (True, False):
                w = World(grant_status=gs).payment("p1", final=final, date="2026-11-14", status=ISSUED)
                for _, e, _, items in w.save("p1").writes:
                    if e == "rev_grants":
                        self.assertIn(items["rev_status"], (gs, 3, 4))


class Recompute(unittest.TestCase):
    """The flow writes the grant and the application and nothing else (amendment c; A-CP-8 withdrawn)."""

    def test_no_action_writes_rev_payment_on_any_input(self):
        statuses = (PENDING, ISSUED, CLEARED, CANCELLED)
        for status in statuses:
            for final in (True, False):
                for date in (None, "2026-11-14"):
                    for app in (APPROVED, GRANT_PAID, WITHDRAWN):
                        with self.subTest(status=status, final=final, date=date, app=app):
                            w = World(application_status=app).payment("p1", final=final, date=date, status=status)
                            r = w.save("p1")
                            self.assertEqual(r.status, "Succeeded")
                            for _, entity, _, items in r.writes:
                                self.assertNotEqual(entity, "rev_payments", "no action writes rev_payment")
                                if entity == "rev_applications":
                                    self.assertIn(items["rev_status"], (APPROVED, GRANT_PAID))
                            # and a second save of the result is always a no-op (FR-109)
                            self.assertFalse(w.save("p1").writes)

    def test_a_run_stopped_between_the_writes_is_finished_by_the_next_save(self):
        w = World().payment("p1", final=True, date="2026-11-14", status=ISSUED)
        w.fail = {"Write_the_application_status"}
        broken = w.save("p1")
        self.assertEqual(broken.status, "Failed")
        self.assertEqual((w.grant_date(), w.app_status()), ("2026-11-14", APPROVED),
                         "the application still reads Approved: the visible sign it did not finish")
        w.fail = set()
        w.save("p1")
        self.assertEqual((w.grant_date(), w.app_status()), ("2026-11-14", GRANT_PAID))

    def test_the_date_shape_is_normalised_so_a_timestamp_and_a_day_string_agree(self):
        w = World(application_status=GRANT_PAID, grant_status=4).payment("p1", final=True, date="2026-11-14T00:00:00Z", status=ISSUED)
        w.grants[G1]["rev_finalpaymentdate"] = "2026-11-14"
        self.assertTrue(w.save("p1").silent, "equal days in two shapes must not look different (FR-109)")


class Reports(unittest.TestCase):
    """FR-111 and FR-112: who is told, what the message carries, and what it never carries."""

    def test_finance_gets_one_teams_message_and_the_process_owner_one_warning_alert(self):
        w = World(application_status=WITHDRAWN).payment("p1", final=True, date="2026-11-14", status=ISSUED)
        r = w.save("p1", alert_upn="finance@example.org")
        self.assertEqual([m[0] for m in r.messages], ["finance@example.org"])
        (name, body), = r.alerts
        self.assertEqual((body["text"], body["text_4"]), ("REV | Finance | Capture Payment", "Warning"))
        self.assertIn("PAY-p1", body["text_3"])
        self.assertIn("REV-2026-001", body["text_3"])

    def test_the_message_carries_references_and_words_but_never_an_amount_a_date_or_a_name(self):
        w = World(application_status=WITHDRAWN).payment("p1", final=True, date="2026-11-14", status=ISSUED)
        w.payments["p1"].update({"rev_amount": 1234.5, "rev_payeename": "A Person"})
        r = w.save("p1")
        text = r.messages[0][1] + json.dumps(r.alerts)
        for forbidden in ("1234", "2026-11-14", "14 November", "A Person", "finance@example.org"):
            self.assertNotIn(forbidden, text)

    def test_a_cancelled_final_payment_is_reported_as_information_and_never_written(self):
        w = World().payment("p1", final=True, date="2026-11-14", status=CANCELLED)
        r = w.save("p1")
        self.assertFalse(r.writes)
        self.assertEqual(len(r.messages), 1)
        self.assertIn("For information only", r.messages[0][1])

    def test_the_reasons_add_up_when_more_than_one_applies(self):
        w = World(grant=False).payment("p1", final=True, date=None, grant="")
        r = w.save("p1")
        self.assertIn("not linked to a grant", r.messages[0][1])
        self.assertIn("no payment date", r.messages[0][1])

    def test_a_blank_finance_address_fails_the_run_after_the_writes_and_alerts_the_process_owner(self):
        w = World(application_status=WITHDRAWN).payment("p1", final=True, date="2026-11-14", status=ISSUED)
        w.fail = {"Tell_finance_in_Teams"}      # a blank recipient makes the post fail
        r = w.save("p1", alert_upn="")
        self.assertEqual(r.status, "Failed")
        self.assertEqual(w.grant_date(), "2026-11-14", "the writes were made before the report")
        self.assertEqual([a[1]["text_4"] for a in r.alerts], ["Warning", "Error"])
        self.assertEqual(r.messages, [])

    def test_a_platform_failure_takes_the_failure_path_without_a_retry(self):
        w = World().payment("p1", final=True, date="2026-11-14")
        w.fail = {"Write_the_grant_date"}
        r = w.save("p1")
        self.assertEqual(r.status, "Failed")
        (name, body), = r.alerts
        self.assertEqual(body["text_4"], "Error")
        self.assertEqual(body["text_3"], "PAY-p1")
        self.assertEqual(sum(1 for x in r.engine.records if x.name == "Write_the_grant_date"), 1, "no loop, no re-run")
        self.assertEqual(w.app_status(), APPROVED)


class SourceOfRule(unittest.TestCase):
    """A-CP-9 / WI-0136: the table-scope payment rule is a designer artefact, authored in the DEV maker designer,
    exported and copied in UNEDITED (ADR-081 item 8). Present since 2026-10-20 (Rev-Payment-Issued). This suite
    asserts what a source read can show: the file is present, is a business rule (category 2) on rev_payment at
    Entity scope (ProcessTriggerScope 2) and activated, and carries both branches and nothing else. The behaviour
    on the platform is A-CP-9 checks 1 to 6 and stays OPEN until they are run."""

    WORKFLOWS = REPO / "src" / "solutions" / "RevitaliseGrantAutomation" / "Workflows"
    SOLUTION = REPO / "src" / "solutions" / "RevitaliseGrantAutomation" / "Other" / "Solution.xml"
    RULE_ID = "02ac658e-9bcc-f111-a05c-7ced8d43e1b4"

    def rule(self):
        xaml = [f for f in self.WORKFLOWS.glob("Rev-Payment-Issued-*.xaml")]
        self.assertEqual(len(xaml), 1, "the exported rule file is not present in source exactly once (WI-0136)")
        data = Path(str(xaml[0]) + ".data.xml")
        self.assertTrue(data.exists(), "the rule's .xaml.data.xml is missing")
        return xaml[0].read_text(encoding="utf-8-sig"), data.read_text(encoding="utf-8-sig")

    def test_the_exported_rule_is_present_and_registered_in_the_solution(self):
        self.rule()
        self.assertIn(f'<RootComponent type="29" id="{{{self.RULE_ID}}}"', self.SOLUTION.read_text(encoding="utf-8"))

    def test_the_rule_is_an_active_entity_scope_business_rule_on_the_payment(self):
        _, data = self.rule()
        for needle in ("<Category>2</Category>", "<ProcessTriggerScope>2</ProcessTriggerScope>",
                       "<PrimaryEntity>rev_payment</PrimaryEntity>", "<StateCode>1</StateCode>",
                       "<StatusCode>2</StatusCode>"):
            self.assertIn(needle, data)

    def test_branch_a_final_yes_and_no_date_shows_an_error_on_the_payment_date(self):
        xaml, _ = self.rule()
        self.assertIn('Attribute="rev_isfinalpayment"', xaml)
        self.assertIn('Attribute="rev_paymentdate"', xaml)
        self.assertIn("WorkflowPropertyType.Boolean, \"1\"", xaml)           # Final = Yes
        self.assertIn('<InArgument x:TypeArguments="mxsq:ConditionOperator" x:Key="ConditionOperator">Null<', xaml)
        self.assertRegex(xaml, r'<mcwc:SetMessage ControlId="rev_paymentdate"[^>]*Level="\[Nothing\]"')

    def test_branch_b_final_yes_and_pending_sets_issued_and_nothing_else(self):
        xaml, _ = self.rule()
        self.assertIn('WorkflowPropertyType.OptionSetValue, "1", "Picklist"', xaml)    # status = Pending
        self.assertIn('WorkflowPropertyType.OptionSetValue, "2", "Picklist"', xaml)    # set to Issued
        sets = re.findall(r'<mxswa:SetEntityProperty Attribute="([a-z_]+)"', xaml)
        self.assertEqual(sets, ["rev_paymentstatus"], "the rule must write only the payment status")
        for forbidden in ('"3", "Picklist"', '"4", "Picklist"'):
            self.assertNotIn(forbidden, xaml, "the rule must never write Cleared or Cancelled")

    def test_the_rule_sets_no_requirement_level_and_is_not_form_scoped(self):
        xaml, data = self.rule()
        self.assertNotIn("SetRequirementLevel", xaml)
        self.assertNotIn("<ProcessTriggerFormId>", data)

    def test_the_flow_does_not_depend_on_the_rule_being_present(self):
        """The build passes without the rule: the flow carries no reference to it."""
        raw = FLOW.read_text(encoding="utf-8")
        self.assertNotIn("Write_the_payment_issued", raw)
        self.assertNotIn('"rev_paymentstatus": 2', raw)


class Reads(unittest.TestCase):
    def test_the_flow_reads_the_payment_the_grant_the_latest_final_and_the_application_and_nothing_else(self):
        w = World().payment("p1", final=True, date="2026-11-14")
        r = w.save("p1")
        tables = [p["entityName"] for _, p in w.reads]
        self.assertEqual(tables, ["rev_payments", "rev_grants", "rev_payments", "rev_applications"])
        selected = {c for _, p in w.reads for c in p["$select"].split(",")}
        for never in ("rev_amount", "rev_bankaccountid", "rev_qboreference", "rev_method", "rev_note"):
            self.assertNotIn(never, selected)

    def test_a_cancelled_or_undated_or_non_final_payment_is_never_the_latest_final(self):
        w = (World().payment("p1", final=True, date="2026-12-02", status=CANCELLED)
             .payment("p2", final=True, date=None)
             .payment("p3", final=False, date="2026-12-09")
             .payment("p4", final=True, date="2026-11-14", status=ISSUED))
        w.save("p4")
        self.assertEqual(w.grant_date(), "2026-11-14")

    def test_the_run_reads_the_saved_payment_again_not_the_trigger_body(self):
        """ADR-081 item 2: a stale trigger body must not decide. Trigger says not final; the table says final."""
        w = World().payment("p1", final=True, date="2026-11-14", status=ISSUED)
        eng = Engine(copy.deepcopy(DEFINITION),
                     {"rev_paymentid": "p1", "rev_name": "PAY-p1", "rev_isfinalpayment": False},
                     parameters={"rev_FinanceAlertUpn": "x"}, connector=w.connector, child_flow=lambda n, b: None)
        eng.run()
        self.assertEqual(w.grant_date(), "2026-11-14")

    def test_every_description_is_within_256_characters(self):
        def walk(actions):
            for name, a in actions.items():
                self.assertLessEqual(len(a.get("description", "")), 256, name)
                walk(a.get("actions", {}))
                walk((a.get("else") or {}).get("actions", {}))
        walk(DEFINITION["actions"])
        for t in DEFINITION["triggers"].values():
            self.assertLessEqual(len(t.get("description", "")), 256)


if __name__ == "__main__":
    unittest.main()
