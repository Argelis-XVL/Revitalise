#!/usr/bin/env python3
"""Executes and inspects the five `REV | Retention | Retention & Erasure Helper` definitions (wbs:0.13, CO-011,
TAD rev 33/34 sections 4.2 and 5.12 to 5.12.4, ADR-088, ADR-089). Test-only.

WHAT THIS PROVES. The SHIPPED definitions are (a) read as values, for the properties the TAD makes checkable from
source: mode 3 and the locate child are read-only, mode 1 contains no Dataverse delete, mode 2 holds the only
Dataverse delete, the retention periods equal `dataverse.bulkDeleteJobs`, `rev_detail` is never written from a
case column, every content-carrying action is secured (C-DOM-004); and (b) RUN, action by action, by the
repository's WDL executor (`src/tests/narrative/wdl_sim.py`) against an in-memory Dataverse, SharePoint, mailbox
and Teams, with the child flows run as real definitions in place of the call.

WHAT THIS DOES NOT PROVE (V2 at most; nothing ran on the platform). The stand-ins speak the shapes the definitions
assume, so every OPEN row of the Dev Summary section 10 stays open until the DEV run of TAD section 12.11/12.12:
  A-ERA-1 the typed input on a When-a-row-is-selected trigger, read as triggerBody()?['text'];
  A-ERA-2 the parental cascades and the privileges they need (the stand-in cascades as Other/Relationships says);
  A-ERA-3 SharePoint Get file metadata / Delete file by path, and a 404 for a file already gone;
  A-ERA-4 / A-SAR-12 Outlook GetEmailsV3 from/to filters and DeleteEmail_V2 on the service mailbox;
  A-SAR-6 Get file content using path; A-SAR-7 Create HTML table (rendered here as a list of rows);
  A-SAR-8 the caller header x-ms-user-email; A-SAR-11 ListRecords on audits; A-RH-1 a child flow's Response body
  as the caller's body() and a 500 failing the caller; A-RH-2 $filter and $expand through a lookup's navigation
  property; A-SAR-4 that a message sent from rev_SarProtectedSender arrives encrypted (the tenant's mail-flow rule,
  ADR-091); A-SAR-13 SendEmailV2's From (Send as), and its failure without Send As; A-RH-3 the attachment shape;
  A-SAR-15 the create-file response's Size, Exchange's real size ceiling, and several attachments arriving intact;
  A-SAR-14 where Exchange keeps a copy of the sent message. Delivery option B's send step is always built; the
  per-environment setting turns it on (TAD rev 37), so these tests run both with the setting empty and filled.
  The email carries the extract and every signed PDF copy, or nothing (TAD rev 37 second amendment): the size gate
  is run under, at and over SarEmailMaxAttachmentMB, and with the limit or a file size missing or not a number.
The executor evaluates if() eagerly, the stricter of the two readings the platform leaves open.
"""
from __future__ import annotations

import copy
import json
import re
import sys
import unittest
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / "src" / "tests" / "narrative"))
import wdl_sim  # noqa: E402

WF = REPO / "src" / "solutions" / "RevitaliseGrantAutomation" / "Workflows"
SETTINGS = REPO / "provisioning" / "deploymentSettings"


def load(stem):
    (path,) = WF.glob(f"{stem}-*.json")
    return json.loads(path.read_text(encoding="utf-8"))


SWEEP, ERASURE, SAR = load("REVRetentionSweep"), load("REVRetentionErasure"), load("REVRetentionSarExtract")
LOCATE, SNAPSHOT = load("REVRetentionLocate"), load("REVRetentionSnapshot")
ALL = {"sweep": SWEEP, "erasure": ERASURE, "sar": SAR, "locate": LOCATE, "snapshot": SNAPSHOT}
LOCATE_ID, SNAPSHOT_ID = "8f1c2a44-1017-4b7a-9e21-0a1b2c3d4e17", "8f1c2a44-1018-4b7a-9e21-0a1b2c3d4e18"
ALERT_ID = "8f1c2a44-1004-4b7a-9e21-0a1b2c3d4e04"
NOW = datetime(2026, 11, 2, 0, 30, tzinfo=timezone.utc)   # a Monday, day 2: the first run of the month


def defn(flow):
    return flow["properties"]["definition"]


def walk(actions, path=""):
    """(name, action, path) for every action at any depth."""
    for name, a in (actions or {}).items():
        yield name, a, path + "/" + name
        yield from walk(a.get("actions"), path + "/" + name)
        yield from walk((a.get("else") or {}).get("actions"), path + "/" + name + "/else")
        for cname, case in (a.get("cases") or {}).items():
            yield from walk(case.get("actions"), path + "/" + name + "/" + cname)
        yield from walk((a.get("default") or {}).get("actions"), path + "/" + name + "/default")


def connector_actions(flow):
    for name, a, _ in walk(defn(flow)["actions"]):
        if a.get("type") == "OpenApiConnection":
            host = a["inputs"]["host"]
            yield name, host["connectionName"], host["operationId"], a["inputs"].get("parameters", {}), a


def strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for v in node.values():
            yield from strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from strings(v)


# ════════════════════════════════════ static properties ════════════════════════════════════

class ReadOnlyAndDeleteBoundaries(unittest.TestCase):
    """ADR-088 item 1 and ADR-089 items 2 and 7, checkable from source."""

    WRITE_OPS = {"CreateRecord", "UpdateRecord", "UpdateOnlyRecord", "DeleteRecord"}

    def test_mode_3_has_no_delete_and_no_business_table_write(self):
        for name, api, op, params, _ in connector_actions(SAR):
            with self.subTest(name):
                self.assertNotIn(op, {"DeleteRecord", "UpdateRecord", "DeleteFile", "DeleteEmail_V2", "MoveV2"})
                if op in ("CreateRecord", "UpdateOnlyRecord"):
                    self.assertEqual(params["entityName"], "rev_retentionlogs", "mode 3 writes only the evidence log")
                if op == "CreateFile":
                    self.assertEqual(params["folderPath"], "@parameters('rev_SpoSarFolderUrl')", "files go to the SAR folder only")

    def test_mode_3_sends_the_extract_only_from_the_protected_sender_and_never_retries(self):
        """ADR-091 items 4 and 5 (TAD rev 37): the send step is always built; it is the ONLY send, its From is the
        setting, it sits on the 'send' route only, and it is never retried. No path sends from any other address."""
        sends = [(n, p, a) for n, api, op, p, a in connector_actions(SAR) if op.startswith("SendEmail") or op.startswith("SendMail")]
        self.assertEqual([n for n, _, _ in sends], ["Send_the_extract_protected"])
        (_, p, a), = sends
        self.assertEqual(p["emailMessage/From"], "@trim(parameters('rev_SarProtectedSender'))")
        self.assertEqual(p["emailMessage/ReplyTo"], "@parameters('rev_ServiceMailbox')")
        self.assertEqual(a["inputs"]["retryPolicy"], {"type": "none"}, "a retried send could duplicate (ADR-091 item 5)")
        self.assertNotIn("emailMessage/Sensitivity", p, "Sensitivity is left empty: the label route is rejected (ADR-091 item 6)")
        self.assertEqual(p["emailMessage/Attachments"], "@variables('attachments')",
                         "one array, built per file and passed whole: the connector's multi-attachment workaround (ADR-091 item 5)")
        check = defn(SAR)["actions"]["Check_protected_delivery_is_on"]
        self.assertIn("Send_the_extract_protected", check["actions"])
        self.assertEqual(check["expression"], {"and": [{"equals": ["@outputs('Compose_delivery_route')", "send"]}]})

    def test_the_route_is_send_only_with_a_sender_an_address_and_a_set_that_fits(self):
        route = defn(SAR)["actions"]["Compose_delivery_route"]["inputs"]
        self.assertEqual(set(re.findall(r"'([^']*)'", route)) - {"rev_SarProtectedSender", "applicant", "rev_email", "Compose_case", "attachmentCheck"},
                         {"", "off", "no email", "send", "too large", "fits"}, "a fixed token, never content")
        self.assertIn("empty(trim(coalesce(parameters('rev_SarProtectedSender'), '')))", route)
        self.assertIn("if(startsWith(variables('attachmentCheck'), 'fits'), 'send', 'too large')", route,
                      "'send' needs the size check to have said fits; anything else is too large (ADR-091 item 5)")

    # ── the size gate (TAD rev 37 second amendment, ADR-091 item 5): one message or none ──
    @staticmethod
    def appends(flow, var):
        return [(n, a) for n, a, _ in walk(defn(flow)["actions"]) if a.get("type") == "AppendToArrayVariable" and a["inputs"]["name"] == var]

    def test_every_file_the_run_writes_is_attached_and_measured(self):
        """Derived from the definition: one attachment and one {Name, Size} per CreateFile, the same name, the Size from
        that very create-file response (A-SAR-15), and the content from the file that was written."""
        writes = {n: p for n, _, op, p, _ in connector_actions(SAR) if op == "CreateFile"}
        # count-coupled by design (C-TECH-067): TAD 4.2 item 6 fixes these three writes; a fourth file must fail here
        self.assertEqual(len(writes), 3, "the extract, a library copy, an envelope copy")
        att = dict(self.appends(SAR, "attachments"))
        files = dict(self.appends(SAR, "attachmentFiles"))
        self.assertEqual((len(att), len(files)), (len(writes), len(writes)))
        names_att = sorted(a["inputs"]["value"]["Name"] for a in att.values())
        names_files = sorted(a["inputs"]["value"]["Name"] for a in files.values())
        self.assertEqual(names_att, names_files)
        self.assertEqual(names_files, sorted(p["name"] for p in writes.values()))
        self.assertEqual(sorted(a["inputs"]["value"]["Size"] for a in files.values()),
                         sorted(f"@body('{n}')?['Size']" for n in writes))
        for a in att.values():
            self.assertEqual(set(a["inputs"]["value"]), {"Name", "ContentBytes"}, "the connector's attachment shape (A-RH-3)")

    def test_the_check_is_set_once_inside_the_gate_and_only_after_both_reads(self):
        sets = [(n, a, path) for n, a, path in walk(defn(SAR)["actions"]) if a.get("type") == "SetVariable" and a["inputs"]["name"] == "attachmentCheck"]
        self.assertEqual([(n, path) for n, _, path in sets], [("Set_the_attachment_check", "/Measure_the_attachments/Set_the_attachment_check")])
        (_, a, _), = sets
        self.assertEqual(a["runAfter"], {"For_each_attachment_file": ["Succeeded"], "Compose_attachment_limit_mb": ["Succeeded"]})
        value = a["inputs"]["value"]
        self.assertEqual(set(re.findall(r"(?:outputs|body|actions|variables)\('([^']+)'\)", value)),
                         {"attachments", "attachmentFiles", "attachmentBytes", "Compose_attachment_limit_mb"}, "sizes and the limit only")
        self.assertIn("lessOrEquals(variables('attachmentBytes'), mul(outputs('Compose_attachment_limit_mb'), 1048576))", value)
        init = defn(SAR)["actions"]["Initialise_attachment_check"]["inputs"]["variables"][0]["value"]
        self.assertFalse(init.startswith("fits"), "until measured, the set counts as over the limit")
        inc = defn(SAR)["actions"]["Measure_the_attachments"]["actions"]["For_each_attachment_file"]["actions"]["Add_the_file_size"]
        self.assertEqual(inc["inputs"]["value"], "@int(string(items('For_each_attachment_file')?['Size']))",
                         "a missing or non-numeric Size fails the loop: over the limit")

    def test_the_limit_is_read_by_key_and_seeded_beside_the_stale_case_setting(self):
        self.assertIn("rev_name eq 'SarEmailMaxAttachmentMB'", json.dumps(defn(SAR)))
        self.assertNotRegex(json.dumps(defn(SAR)), r"mul\(\d+, 1048576\)", "never a literal limit (FR-017)")
        for file in ("dev-scoring-settings.json", "test-settings.json", "prd-settings.json"):
            rows = {r["key"]: r for r in json.loads((SETTINGS / file).read_text(encoding="utf-8"))["dataverse"]["settingRows"]}
            row = rows["SarEmailMaxAttachmentMB"]
            with self.subTest(file=file):
                self.assertEqual((row["value"], row["dataType"], row["createOnly"]), ("15", "Whole Number", True))
                self.assertEqual(row["category"], rows["RetentionStaleCaseMonths"]["category"])

    def test_mode_3_neither_reads_nor_deletes_a_sent_copy(self):
        """ADR-091 item 7 (A-SAR-14): no new mailbox action; the only mailbox reads are the service mailbox's."""
        for name, api, op, p, _ in connector_actions(SAR):
            if api == "shared_office365":
                with self.subTest(name):
                    self.assertIn(op, {"GetEmailsV3", "SendEmailV2"})
                    if op == "GetEmailsV3":
                        self.assertEqual(p.get("mailboxAddress"), "@parameters('rev_ServiceMailbox')")
                        self.assertNotIn("rev_SarProtectedSender", json.dumps(p))

    def test_the_locate_child_only_reads(self):
        ops = {op for _, _, op, _, _ in connector_actions(LOCATE)}
        self.assertEqual(ops, {"ListRecords"})

    def test_mode_1_contains_no_dataverse_delete_and_writes_only_the_log(self):
        for name, api, op, params, _ in connector_actions(SWEEP):
            with self.subTest(name):
                self.assertNotEqual(op, "DeleteRecord", "the bulk-delete jobs delete; mode 1 never does (ADR-089 item 2)")
                if op in self.WRITE_OPS:
                    self.assertEqual(params["entityName"], "rev_retentionlogs")
        deletes = [n for n, api, op, _, _ in connector_actions(SWEEP) if "Delete" in op]
        self.assertEqual(deletes, ["Delete_the_logged_pdf"], "the signed PDF is mode 1's only delete (FR-049)")

    def test_mode_2_holds_exactly_one_dataverse_delete_on_the_applicant(self):
        deletes = [(n, p["entityName"]) for n, api, op, p, _ in connector_actions(ERASURE) if op == "DeleteRecord"]
        self.assertEqual(deletes, [("Delete_the_applicant_row", "rev_applicants")])
        for flow in (SNAPSHOT, LOCATE, SAR, SWEEP):
            self.assertFalse([1 for _, _, op, _, _ in connector_actions(flow) if op == "DeleteRecord"])

    def test_the_snapshot_child_creates_only_a_not_granted_statistic(self):
        writes = [(op, p) for _, _, op, p, _ in connector_actions(SNAPSHOT) if op in self.WRITE_OPS]
        self.assertEqual(len(writes), 1)
        op, p = writes[0]
        self.assertEqual((op, p["entityName"], p["item/rev_outcome"]), ("CreateRecord", "rev_anonymisedstatistics", 2))
        self.assertFalse([k for k in p if k.endswith("@odata.bind") or k == "item/rev_amountawarded"],
                         "a snapshot carries no lookup and no amount (TAD 3.3)")


class PeriodsMatchTheJobs(unittest.TestCase):
    """TAD 5.12.1 step 1: mode 1's rules read the same periods as dataverse.bulkDeleteJobs; a test holds them equal."""

    def jobs(self, file):
        d = json.loads((SETTINGS / file).read_text(encoding="utf-8"))
        return {j["jobKey"]: j for j in d["dataverse"]["bulkDeleteJobs"]}

    def test_mode_1_periods_equal_the_jobs_in_both_environments_that_run_them(self):
        periods = defn(SWEEP)["actions"]["Compose_retention_periods"]["inputs"]
        self.assertEqual(set(periods), {"paidGrantApplications", "rejectedApplications", "withdrawnIncompleteApplications"})
        for file in ("test-settings.json", "prd-settings.json"):
            jobs = self.jobs(file)
            for key, months in periods.items():
                with self.subTest(file=file, job=key):
                    self.assertEqual(jobs[key]["retentionUnit"], "months")
                    self.assertEqual(jobs[key]["retentionValue"], months)

    def test_mode_2_keeps_the_quickbooks_record_for_the_paid_grant_period(self):
        paid = self.jobs("prd-settings.json")["paidGrantApplications"]["retentionValue"]
        hits = [s for s in strings(defn(ERASURE)) if "rev_finalpaymentdate'], " in s and "'Month'" in s]
        self.assertTrue(hits)
        for s in hits:
            self.assertIn(f"rev_finalpaymentdate'], {paid}, 'Month'", s)

    def test_the_look_ahead_and_overdue_constants_are_the_tad_values(self):
        self.assertEqual(defn(SWEEP)["actions"]["Compose_sweep_constants"]["inputs"], {"lookAheadDays": 8, "overdueAfterDays": 35})


class DetailIsNeverCaseContent(unittest.TestCase):
    """TAD 5.12.3: rev_detail is composed from a fixed list only (the SAR file name and the stores read)."""

    ALLOWED = {"Compose_extract_file_name", "Compose_stores_read", "Compose_delivery_outcome"}

    def test_every_rev_detail_write_reads_only_the_fixed_list(self):
        found = 0
        for flow in (SWEEP, ERASURE, SAR):
            for name, api, op, params, _ in connector_actions(flow):
                if "item/rev_detail" in params:
                    found += 1
                    refs = set(re.findall(r"(?:outputs|body|actions|variables|items)\('([^']+)'\)", params["item/rev_detail"]))
                    self.assertTrue(refs and refs <= self.ALLOWED, f"{name}: {refs}")
                    self.assertNotIn("item()", params["item/rev_detail"])
        # count-coupled by design (C-TECH-067): the TAD fixes exactly these two writes; a third must fail here
        self.assertEqual(found, 2, "only mode 3 writes rev_detail: the log row, then the delivery (ADR-091 item 5)")

    def test_the_two_sources_are_themselves_fixed(self):
        a = defn(SAR)["actions"]
        self.assertEqual(set(re.findall(r"actions\('([^']+)'\)", a["Compose_stores_read"]["inputs"])),
                         {"Read_dataverse_rows", "Read_audit_history", "Read_quickbooks_section", "Read_service_mailbox", "Copy_signed_documents"})
        self.assertNotRegex(a["Compose_stores_read"]["inputs"], r"(body|outputs|variables)\(")
        refs = set(re.findall(r"(?:outputs|body)\('([^']+)'\)", a["Compose_extract_file_name"]["inputs"]))
        self.assertEqual(refs, {"Get_the_selected_applicant", "Compose_run_time"})
        self.assertIn("?['rev_name']", a["Compose_extract_file_name"]["inputs"], "the reference, never a name")
        outcome = a["Compose_delivery_outcome"]["inputs"]
        self.assertEqual(set(re.findall(r"(?:outputs|body|actions|variables)\('([^']+)'\)", outcome)),
                         {"Send_the_extract_protected", "Compose_delivery_route", "attachmentCheck"})
        self.assertNotRegex(outcome, r"body\(", "the send's status, the route token and the size check only")
        self.assertEqual(set(re.findall(r"variables\('([^']+)'\)", outcome)), {"attachmentCheck"},
                         "the size check holds sizes and the limit only (tested in ReadOnlyAndDeleteBoundaries)")

    def test_the_detail_cap_is_the_column_length(self):
        """TAD 5.12.3 (rev 37 approval amendment): rev_signedpdfpath and rev_detail are 2000 characters, and every
        rev_detail write truncates to the column's own length, read from Entity.xml."""
        entity = (REPO / "src" / "solutions" / "RevitaliseGrantAutomation" / "Entities" / "rev_retentionlog" / "Entity.xml").read_text()
        lengths = {c: int(re.search(rf'<attribute PhysicalName="{c}">.*?<MaxLength>(\d+)</MaxLength>', entity, re.S).group(1))
                   for c in ("rev_signedpdfpath", "rev_detail")}
        self.assertEqual(lengths, {"rev_signedpdfpath": 2000, "rev_detail": 2000})
        caps = [int(m) for _, _, _, p, _ in connector_actions(SAR) if "item/rev_detail" in p
                for m in re.findall(r"min\((\d+),", p["item/rev_detail"])]
        self.assertEqual(caps, [lengths["rev_detail"]] * 2)  # count-coupled by design (C-TECH-067): the two writes above


class SecuredRunHistory(unittest.TestCase):
    """C-DOM-004: every action that carries row, audit, mailbox, file or extract content has secure inputs and
    outputs, so the run history holds no copy (TAD 5.12 Run history). Mechanical, so a new unsecured content
    action fails here."""

    CONTENT_OPS = {"GetEmailsV3", "GetFileContentByPath", "GetDocumentsV2", "CreateFile"}
    PERSONAL = ("rev_email", "rev_refereeemail", "rev_conditionprofile", "rev_finalpaymentdate", "internalemailaddress")
    CONTENT_SOURCES = ("Compose_case", "Compose_case_to_erase", "Create_", "variables('extract')", "Compose_reply_address",
                       "Compose_extract_document", "variables('attachments')",
                       "Get_messages", "List_the_audit_records", "Get_the_signed_pdf_content", "Get_the_envelope_document",
                       "Find_grants_without_final_payment", "Find_envelopes_to_void")

    @staticmethod
    def secured(a):
        return set(((a.get("runtimeConfiguration") or {}).get("secureData") or {}).get("properties") or [])

    def must_secure(self, name, a):
        t = a.get("type")
        if t in ("If", "Switch", "Foreach", "Scope", "Terminate", "InitializeVariable", "IncrementVariable"):
            return None
        if t == "Table":
            return {"inputs", "outputs"}
        if t == "Workflow":
            return {"inputs", "outputs"} if a["inputs"]["host"]["workflowReferenceName"] == LOCATE_ID else None
        if t == "OpenApiConnection":
            op = a["inputs"]["host"]["operationId"]
            p = a["inputs"]["parameters"]
            if op in self.CONTENT_OPS:
                return {"inputs", "outputs"}
            if op in ("ListRecords", "GetItem") and p.get("entityName") not in ("rev_retentionlogs", "rev_settings"):
                sel = p.get("$select")
                if sel is None or any(c in sel for c in self.PERSONAL) or "systemusers" == p.get("entityName"):
                    return {"inputs", "outputs"} if sel is None or p.get("entityName") != "rev_grants" or "rev_finalpaymentdate" in sel else None
            if op == "SendEmailV2" and "parameters(" not in p.get("emailMessage/To", "") and "first(body('Get_the_dpo" not in p.get("emailMessage/To", ""):
                return {"inputs"}
            return None
        # the size gate counts the attachments array (ADR-091 item 5); a length carries no content
        text = json.dumps(a.get("inputs")).replace("length(variables('attachments'))", "length(...)")
        if t in ("Select", "Query"):
            frm = json.dumps(a["inputs"]["from"])
            if any(s in frm for s in self.CONTENT_SOURCES) or any(c in frm for c in ("Get_the_applicant_row", "List_the_")):
                return {"inputs", "outputs"}
            return None
        if t in ("Compose", "AppendToStringVariable", "AppendToArrayVariable", "SetVariable", "Response"):
            if any(s in text for s in self.CONTENT_SOURCES) or any(c in text for c in self.PERSONAL):
                if t == "Compose" and re.fullmatch(r'"@\{?formatDateTime[^"]*"', text):
                    return None
                return {"inputs"}
        return None

    def test_every_content_carrying_action_is_secured(self):
        checked = 0
        for label, flow in ALL.items():
            for name, a, path in walk(defn(flow)["actions"]):
                need = self.must_secure(name, a)
                if need:
                    checked += 1
                    with self.subTest(flow=label, action=path):
                        self.assertTrue(need <= self.secured(a), f"secureData {sorted(self.secured(a))}, needs {sorted(need)}")
        self.assertGreater(checked, 40, "the rule must have subjects")

    def test_no_compose_secures_outputs(self):
        """check 18 (IMP-1156): a Compose takes ["inputs"] only."""
        for label, flow in ALL.items():
            for name, a, _ in walk(defn(flow)["actions"]):
                if a.get("type") == "Compose":
                    self.assertNotIn("outputs", self.secured(a), f"{label}/{name}")

    def test_the_rule_can_fail(self):
        d = copy.deepcopy(SAR)
        del defn(d)["actions"]["Read_dataverse_rows"]["actions"]["Create_reviews_table"]["runtimeConfiguration"]
        bad = [n for n, a, _ in walk(defn(d)["actions"]) if (need := self.must_secure(n, a)) and not need <= self.secured(a)]
        self.assertEqual(bad, ["Create_reviews_table"])


class TriggersAndSettings(unittest.TestCase):
    def test_modes_2_and_3_start_from_the_flow_menu_on_rev_applicant(self):
        for flow in (ERASURE, SAR):
            (t,) = defn(flow)["triggers"].values()
            self.assertEqual((t["inputs"]["operationId"], t["inputs"]["parameters"]["entityName"]), ("RecordSelected", "rev_applicants"))
        (t,) = defn(ERASURE)["triggers"].values()
        self.assertNotIn("splitOn", t, "an erasure reads the rows array and refuses more than one applicant")
        self.assertIn("text", t["inputs"]["schema"]["properties"])
        self.assertIn("text", t["inputs"]["schema"]["required"])

    def test_mode_1_runs_weekly_on_monday_at_00_30_utc(self):
        (t,) = defn(SWEEP)["triggers"].values()
        r = t["recurrence"]
        self.assertEqual((r["frequency"], r["interval"], r["timeZone"], r["schedule"]["weekDays"], r["schedule"]["hours"], r["schedule"]["minutes"]),
                         ("Week", 1, "UTC", ["Monday"], ["0"], [30]))

    def test_the_two_new_settings_are_seeded_in_every_environment_create_only(self):
        for file in ("dev-scoring-settings.json", "test-settings.json", "prd-settings.json"):
            rows = {r["key"]: r for r in json.loads((SETTINGS / file).read_text(encoding="utf-8"))["dataverse"]["settingRows"]}
            with self.subTest(file=file):
                self.assertEqual((rows["RetentionStaleCaseMonths"]["value"], rows["RetentionStaleCaseMonths"]["dataType"]), ("12", "Whole Number"))
                self.assertNotIn("@", rows["ErasureNotificationEmail"]["value"], "no address in the repository; the process owner sets it")
                for k in ("RetentionStaleCaseMonths", "ErasureNotificationEmail"):
                    self.assertTrue(rows[k]["createOnly"])
                    self.assertEqual(rows[k]["category"], "Data retention and erasure")

    def test_flows_read_the_settings_by_key_and_never_a_literal_period(self):
        self.assertIn("rev_name eq 'RetentionStaleCaseMonths'", json.dumps(defn(SWEEP)))
        self.assertIn("rev_name eq 'ErasureNotificationEmail'", json.dumps(defn(ERASURE)))
        self.assertNotRegex(json.dumps(defn(SWEEP)), r"le 7 and rev_applicantid/rev_lastcontactdate lt '?\d{4}-")

    def test_log_choices_match_the_option_sets(self):
        """Every integer the flows write to a rev_retentionlog choice exists in its option set."""
        os_dir = REPO / "src" / "solutions" / "RevitaliseGrantAutomation" / "OptionSets"
        sets = {"item/rev_runtype": "rev_retentionruntype", "item/rev_datatype": "rev_retentiondatatype",
                "item/rev_ruleapplied": "rev_retentionrule", "item/rev_outcome": "rev_retentionoutcome"}
        values = {k: {int(v) for v in re.findall(r'<option value="(\d+)"', (os_dir / f"{s}.xml").read_text())} for k, s in sets.items()}
        n = 0
        for flow in (SWEEP, ERASURE, SAR):
            for name, api, op, p, _ in connector_actions(flow):
                if p.get("entityName") == "rev_retentionlogs" and op in ("CreateRecord", "UpdateOnlyRecord"):
                    for k, allowed in values.items():
                        if isinstance(p.get(k), int):
                            n += 1
                            self.assertIn(p[k], allowed, f"{name} {k}")
        self.assertGreater(n, 30)


# ════════════════════════════════════ execution ════════════════════════════════════

class Http404(Exception):
    pass


@dataclass
class Engine(wdl_sim.Engine):
    """The executor plus what the helper flows use that the narrative and payment flows did not."""

    headers: dict = None

    def f_triggerBody(self):
        return copy.deepcopy(self.trigger_body)

    def f_triggerOutputs(self):
        return {"body": copy.deepcopy(self.trigger_body), "headers": dict(self.headers or {})}

    def f_utcNow(self, fmt=None):
        return NOW.strftime("%Y-%m-%dT%H:%M:%S.0000000Z") if fmt is None else self.f_formatDateTime(NOW.isoformat(), fmt)

    @staticmethod
    def _dt(v):
        if not isinstance(v, str):
            raise wdl_sim.WdlError(f"date of {v!r}")
        d = datetime.fromisoformat(v.replace("Z", "+00:00").replace(".0000000+00:00", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)

    def _fmt(self, d, fmt):
        if fmt is None:
            return d.strftime("%Y-%m-%dT%H:%M:%S.0000000Z")
        table = {"yyyy-MM-dd": "%Y-%m-%d", "yyyy-MM-01": "%Y-%m-01", "yyyy-MM": "%Y-%m",
                 "yyyy-MM-ddTHH-mm-ssZ": "%Y-%m-%dT%H-%M-%SZ", "d MMMM yyyy": "%-d %B %Y"}
        if fmt not in table:
            raise wdl_sim.Unsupported(f"date format {fmt!r}")
        return d.strftime(table[fmt])

    def f_formatDateTime(self, v, fmt=None):
        return self._fmt(self._dt(v), fmt)

    def f_addDays(self, v, n, fmt=None):
        self._need_num(n)
        return self._fmt(self._dt(v) + timedelta(days=n), fmt)

    def f_addToTime(self, v, n, unit, fmt=None):
        self._need_num(n)
        d = self._dt(v)
        if unit == "Month":
            m = d.month - 1 + n
            y, m = d.year + m // 12, m % 12 + 1
            d = d.replace(year=y, month=m, day=min(d.day, [31, 29 if y % 4 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]))
        elif unit == "Year":
            d = d.replace(year=d.year + n)
        elif unit == "Day":
            d = d + timedelta(days=n)
        else:
            raise wdl_sim.Unsupported(unit)
        return self._fmt(d, fmt)

    def f_base64(self, v):
        import base64
        return base64.b64encode(wdl_sim.to_str(v).encode("utf-8")).decode("ascii")

    def f_dayOfMonth(self, v):
        return self._dt(v).day

    def f_removeProperty(self, obj, prop):
        if not isinstance(obj, dict):
            raise wdl_sim.WdlError("removeProperty() of a non-object")
        out = dict(obj)
        out.pop(prop, None)
        return out

    def f_actions(self, name):
        return {"status": self.results.get(name, {}).get("status", "Skipped")}

    def a_Table(self, name, a, rec):
        rows = self.value(a["inputs"]["from"])
        if not isinstance(rows, list):
            raise wdl_sim.WdlError("Create HTML table from a non-array")
        html = "<table>" + "".join("<tr>" + "".join(f"<td>{k}={wdl_sim.to_str(v)}</td>" for k, v in r.items()) + "</tr>" for r in rows) + "</table>"
        rec.inputs = rows
        self._store(name, {"body": html}, html, rec)
        return "Succeeded"

    def a_AppendToStringVariable(self, name, a, rec):
        var = a["inputs"]["name"]
        val = self.value(a["inputs"]["value"])
        rec.inputs = val
        if not isinstance(self.variables.get(var), str):
            raise wdl_sim.WdlError(f"{var} is not a string")
        self.variables[var] += wdl_sim.to_str(val)
        self.assignments.append((var, val))
        self._store(name, None)
        return "Succeeded"

    def a_IncrementVariable(self, name, a, rec):
        var = a["inputs"]["name"]
        self.variables[var] += self.value(a["inputs"].get("value", 1))
        self._store(name, None)
        return "Succeeded"

    def a_Response(self, name, a, rec):
        self.response = (a["inputs"]["statusCode"], self.value(a["inputs"]["body"]))
        self._store(name, None)
        return "Succeeded"

    def a_Workflow(self, name, a, rec):
        body = self.value(a["inputs"]["body"])
        rec.inputs = body
        out = self.child_flow(a["inputs"]["host"]["workflowReferenceName"], body)
        self._store(name, {"body": out}, out, rec)
        return "Succeeded"

    def a_OpenApiConnection(self, name, a, rec):
        try:
            return super().a_OpenApiConnection(name, a, rec)
        except Http404:
            self.results[name] = {"status": "Failed", "outputs": {"statusCode": 404}, "error": {"code": "NotFound"}}
            rec.status = "Failed"
            return "Failed"


# ── an in-memory Dataverse with the connector's OData subset ──────────────────────────────────

NAV = {"rev_applicationid": ("rev_applications", "_rev_applicationid_value"),
       "rev_applicantid": ("rev_applicants", "_rev_applicantid_value")}
PK = {"rev_applicants": "rev_applicantid", "rev_applications": "rev_applicationid", "rev_reviews": "rev_reviewid",
      "rev_grants": "rev_grantid", "rev_payments": "rev_paymentid", "rev_bankaccounts": "rev_bankaccountid",
      "rev_retentionlogs": "rev_retentionlogid", "rev_anonymisedstatistics": "rev_anonymisedstatisticid",
      "rev_settings": "rev_settingid", "systemusers": "systemuserid", "audits": "auditid"}
CASCADE = {"rev_applicants": [("rev_applications", "_rev_applicantid_value"), ("rev_bankaccounts", "_rev_applicantid_value")],
           "rev_applications": [("rev_reviews", "_rev_applicationid_value"), ("rev_grants", "_rev_applicationid_value")],
           "rev_grants": [("rev_payments", "_rev_grantid_value")]}
TOKEN = re.compile(r"\s*(\(|\)|'(?:[^']|'')*'|[A-Za-z_][A-Za-z0-9_/.]*|-?\d[\d\-:TZ.]*)")


class ODataFilter:
    def __init__(self, world, text):
        self.world, self.toks, self.i = world, [t for t in TOKEN.findall(text) if t.strip()], 0
        rebuilt = "".join(TOKEN.findall(text)).replace(" ", "")
        assert rebuilt == text.replace(" ", ""), f"unparsed $filter text: {text!r}"

    def peek(self):
        return self.toks[self.i] if self.i < len(self.toks) else None

    def take(self):
        self.i += 1
        return self.toks[self.i - 1]

    def parse(self):
        node = self.or_()
        assert self.peek() is None, f"trailing tokens {self.toks[self.i:]}"
        return node

    def or_(self):
        parts = [self.and_()]
        while self.peek() == "or":
            self.take()
            parts.append(self.and_())
        return ("or", parts)

    def and_(self):
        parts = [self.atom()]
        while self.peek() == "and":
            self.take()
            parts.append(self.atom())
        return ("and", parts)

    def atom(self):
        if self.peek() == "(":
            self.take()
            n = self.or_()
            assert self.take() == ")"
            return n
        path, op, val = self.take(), self.take(), self.take()
        assert op in ("eq", "ne", "lt", "le", "gt", "ge"), op
        if val.startswith("'"):
            val = val[1:-1].replace("''", "'")
        elif val == "null":
            val = None
        elif re.fullmatch(r"-?\d+", val):
            val = int(val)
        return ("cmp", path, op, val)

    def value_of(self, row, path):
        if "/" in path:
            nav, col = path.split("/", 1)
            table, fk = NAV[nav]
            related = self.world.tables[table].get(row.get(fk))
            return None if related is None else related.get(col)
        return row.get(path)

    def match(self, node, row):
        kind = node[0]
        if kind == "or":
            return any(self.match(n, row) for n in node[1])
        if kind == "and":
            return all(self.match(n, row) for n in node[1])
        _, path, op, val = node
        have = self.value_of(row, path)
        if op == "eq":
            return have == val
        if op == "ne":
            return have != val
        if have is None or val is None:
            return False
        return {"lt": have < val, "le": have <= val, "gt": have > val, "ge": have >= val}[op]


class World:
    def __init__(self):
        self.tables = {k: {} for k in PK}
        self.files = {}          # SharePoint path -> bytes
        self.created_files = []  # (folder, name, body)
        self.mail = []           # {id, folder, from, to, subject, body}
        self.calls, self.messages, self.alerts, self.sent = [], [], [], []
        self.fail = set()
        self.seq = 0
        self.sender = ""         # rev_SarProtectedSender: empty, as every environment ships (ADR-091 item 4)
        self.sizes = {}          # file-name suffix -> the Size CreateFile reports, or "missing"; default the real length
        self.add("systemusers", systemuserid="u-emily", internalemailaddress="emily@example.org")
        self.setting("SarEmailMaxAttachmentMB", "15")   # seeded create-only in every environment (ADR-091 item 5)

    @staticmethod
    def file_body(data: bytes):
        """A file's content as the connectors hand it to a later action: {$content-type, $content (base64)} (A-RH-3)."""
        import base64
        return {"$content-type": "application/pdf", "$content": base64.b64encode(data).decode("ascii")}

    @staticmethod
    def raw(body):
        import base64
        if isinstance(body, dict):
            return base64.b64decode(body["$content"])
        return wdl_sim.to_str(body).encode("utf-8")

    def next_id(self, prefix):
        """A GUID-shaped id, as the platform assigns them, so ids parse in a $filter as they would live."""
        self.seq += 1
        return f"10000000-0000-4000-8000-{self.seq:012d}"

    def add(self, table, **row):
        pk = PK[table]
        row.setdefault(pk, self.next_id(table))
        self.tables[table][row[pk]] = row
        return row[pk]

    def setting(self, key, value):
        self.add("rev_settings", rev_name=key, rev_value=value)
        return self

    # the connectors -------------------------------------------------------------------------
    def connector(self, name, op, params):
        self.calls.append((name, op, copy.deepcopy(params)))
        if name in self.fail or op in self.fail:
            raise wdl_sim.ConnectorFailure(f"{name} refused")
        if op in ("ListRecords", "GetItem", "CreateRecord", "UpdateOnlyRecord", "DeleteRecord"):
            return getattr(self, "dv_" + op)(params)
        if op == "GetFileMetadataByPath":
            if params["path"] not in self.files:
                raise Http404(params["path"])
            return {"Id": "id:" + params["path"]}
        if op == "DeleteFile":
            self.files.pop(params["id"][3:])
            return {}
        if op == "GetFileContentByPath":
            if params["path"] not in self.files:
                raise Http404(params["path"])
            return self.file_body(self.files[params["path"]])
        if op == "GetDocumentsV2":
            return self.file_body(f"envelope-pdf:{params['envelopeId']}".encode())
        if op == "CreateFile":
            self.created_files.append((params["folderPath"], params["name"], params["body"]))
            out = {"Path": params["folderPath"] + "/" + params["name"], "Name": params["name"]}
            size = next((s for suffix, s in self.sizes.items() if params["name"].endswith(suffix)), None)
            if size != "missing":  # A-SAR-15 (a): the create-file response carries Size in bytes
                out["Size"] = size if size is not None else len(self.raw(params["body"]))
            return out
        if op == "GetEmailsV3":
            key, folder = ("from", "Inbox") if "from" in params else ("to", "SentItems")
            want = params.get("from") or params.get("to")
            return {"value": [dict(m) for m in self.mail if m["folder"] == folder and m[key].lower() == want.lower()]}
        if op == "DeleteEmail_V2":
            before = len(self.mail)
            self.mail = [m for m in self.mail if m["id"] != params["messageId"]]
            if len(self.mail) == before:
                raise Http404(params["messageId"])
            return {}
        if op == "SendEmailV2":
            self.sent.append(params)
            return {}
        if op == "PostMessageToConversation":
            self.messages.append(params["body/messageBody"])
            return {}
        raise AssertionError(f"unexpected connector call {name} {op}")

    def select(self, table, row, sel):
        out = dict(row) if not sel else {k: row.get(k) for k in sel.split(",")}
        out[PK[table]] = row[PK[table]]
        return out

    def dv_ListRecords(self, p):
        table = p["entityName"]
        rows = list(self.tables[table].values())
        if "$filter" in p:
            f = ODataFilter(self, p["$filter"]).parse()
            rows = [r for r in rows if ODataFilter(self, p["$filter"]).match(f, r)]
        if "$orderby" in p:
            col, direction = p["$orderby"].split(" ")
            rows.sort(key=lambda r: r.get(col) or "", reverse=direction == "desc")
        rows = rows[: p.get("$top", 5000)]
        out = [self.select(table, r, p.get("$select")) for r in rows]
        if "$expand" in p:
            m = re.fullmatch(r"(\w+)\(\$select=([\w,]+)\)", p["$expand"])
            nav, cols = m.group(1), m.group(2)
            rtable, fk = NAV[nav]
            for o, r in zip(out, rows):
                rel = self.tables[rtable].get(r.get(fk))
                o[nav] = None if rel is None else {c: rel.get(c) for c in cols.split(",")}
        return {"value": out}

    def dv_GetItem(self, p):
        row = self.tables[p["entityName"]].get(p["recordId"])
        if row is None:
            raise wdl_sim.ConnectorFailure("not found")
        return self.select(p["entityName"], row, p.get("$select"))

    def dv_CreateRecord(self, p):
        row = {}
        for k, v in p.items():
            if k.startswith("item/"):
                col = k[5:]
                if col.endswith("@odata.bind"):
                    row["_" + col[:-11] + "_value"] = re.fullmatch(r"/\w+\((.+)\)", v).group(1)
                else:
                    row[col] = v
        rid = self.add(p["entityName"], **row)
        return dict(self.tables[p["entityName"]][rid])

    def dv_UpdateOnlyRecord(self, p):
        row = self.tables[p["entityName"]].get(p["recordId"])
        if row is None:
            raise wdl_sim.ConnectorFailure("row not found")
        row.update({k[5:]: v for k, v in p.items() if k.startswith("item/")})
        return dict(row)

    def dv_DeleteRecord(self, p):
        def cascade(table, rid):
            for child, fk in CASCADE.get(table, []):
                for cid in [k for k, r in self.tables[child].items() if r.get(fk) == rid]:
                    cascade(child, cid)
            self.tables[table].pop(rid)
        if p["recordId"] not in self.tables[p["entityName"]]:
            raise wdl_sim.ConnectorFailure("row not found")
        cascade(p["entityName"], p["recordId"])
        return {}

    # running a flow, with the two children run as real definitions -----------------------------
    def child(self, workflow_id, body):
        if workflow_id == ALERT_ID:
            self.alerts.append(body)
            return {}
        flow = {LOCATE_ID: LOCATE, SNAPSHOT_ID: SNAPSHOT}[workflow_id]
        eng = self.engine(flow, body)
        status = eng.run()
        code, out = getattr(eng, "response", (None, None))
        if status != "Succeeded" or code != 200:
            raise wdl_sim.ConnectorFailure(f"child {workflow_id} answered {code}")  # A-RH-1
        return out

    def engine(self, flow, trigger, headers=None, params=None):
        return Engine(copy.deepcopy(defn(flow)), copy.deepcopy(trigger),
                      parameters=params or {"rev_ProcessOwnerUpn": "po@example.org", "rev_ServiceMailbox": "grants@example.org",
                                            "rev_SpoSiteUrl": "https://site", "rev_SpoSarFolderUrl": "/SAR",
                                            "rev_DocuSignAccountId": "acct", "rev_SarProtectedSender": self.sender},
                      connector=self.connector, child_flow=self.child, headers=headers or {})

    def run(self, flow, trigger, headers=None):
        eng = self.engine(flow, trigger, headers)
        status = eng.run()
        return status, eng

    def log(self, **match):
        return [r for r in self.tables["rev_retentionlogs"].values() if all(r.get(k) == v for k, v in match.items())]


def case(world, paid=True, deferred=False, status=11, signed=True, with_grant=True):
    """One applicant with one application (and its review, grant, payment and bank account)."""
    a = world.add("rev_applicants", rev_name="REV-A-00042", rev_email="pat@example.org", rev_fullname="Pat Example",
                  rev_lastcontactdate="2026-01-10", rev_agerange=3, rev_locationarea=2)
    app = world.add("rev_applications", rev_name="REV-2026-007", _rev_applicantid_value=a, rev_status=status,
                    rev_refereeemail="ref@example.org", rev_sourcesubmissionid="1895", rev_conditionprofile="1,5",
                    rev_narrativeraw="I care for my mother.", rev_decisiondate="2025-10-01")
    world.add("rev_reviews", rev_name="REV-R-00001", _rev_applicationid_value=app, rev_outcome=2 if deferred else 1,
              rev_paneldate="2026-03-05", createdon="2026-03-01T10:00:00Z", rev_notes1="Strong case",
              _rev_trustee1_value="u-trustee", **{"_rev_trustee1_value@OData.Community.Display.V1.FormattedValue": "Tess Trustee",
                                                  "_createdby_value": "u-trustee"})
    g = None
    if with_grant:
        g = world.add("rev_grants", rev_name="GR-2026-00003", _rev_applicationid_value=app, rev_status=4,
                      rev_finalpaymentdate="2020-05-10" if paid else None,
                      rev_signedpdfurl="/Signed/GR-2026-00003-signed-acceptance.pdf" if signed else None,
                      rev_docusignenvelopeid="env-1")
        if signed:
            world.files["/Signed/GR-2026-00003-signed-acceptance.pdf"] = b"%PDF signed"
        bank = world.add("rev_bankaccounts", rev_name="BA-1", _rev_applicantid_value=a, rev_accountnumber="12345678")
        world.add("rev_payments", rev_name="PAY-2026-00001", _rev_grantid_value=g, _rev_bankaccountid_value=bank,
                  rev_amount=450.0, rev_paymentdate="2020-05-10", rev_qboreference="QB-77")
    world.mail += [
        {"id": "m1", "folder": "Inbox", "from": "pat@example.org", "to": "grants@example.org", "subject": "My application", "body": "Hello"},
        {"id": "m2", "folder": "SentItems", "from": "grants@example.org", "to": "pat@example.org", "subject": "Re: My application", "body": "Thanks"},
        {"id": "m3", "folder": "Inbox", "from": "ref@example.org", "to": "grants@example.org", "subject": "Reference REV-2026-007", "body": "I support"},
        {"id": "m4", "folder": "Inbox", "from": "ref@example.org", "to": "grants@example.org", "subject": "Another applicant", "body": "Other"},
    ]
    return a, app, g


def erasure_trigger(a, typed, rows=None):
    return {"rows": rows if rows is not None else [{"entity": {"rev_applicantid": a, "rev_name": "REV-A-00042"}}], "text": typed}


STARTER = {"x-ms-user-email": "emily@example.org"}


class ErasureMode2(unittest.TestCase):
    """TAD 5.12.2, run against the in-memory stores."""

    def test_a_wrong_typed_reference_stops_before_anything_is_read(self):
        w = World()
        a, _, _ = case(w)
        status, _ = w.run(ERASURE, erasure_trigger(a, "REV-A-00043"), STARTER)
        self.assertEqual(status, "Failed")
        self.assertEqual(w.calls, [], "nothing read, nothing changed (A-ERA-1)")

    def test_an_empty_typed_reference_never_matches(self):
        w = World()
        a, _, _ = case(w)
        rows = [{"entity": {"rev_applicantid": a, "rev_name": ""}}]
        self.assertEqual(w.run(ERASURE, erasure_trigger(a, "", rows), STARTER)[0], "Failed")
        self.assertEqual(w.calls, [])

    def test_two_selected_applicants_stop_the_run(self):
        w = World()
        a, _, _ = case(w)
        rows = [{"entity": {"rev_applicantid": a, "rev_name": "REV-A-00042"}}] * 2
        self.assertEqual(w.run(ERASURE, erasure_trigger(a, "REV-A-00042", rows), STARTER)[0], "Failed")
        self.assertEqual(w.calls, [])

    def test_an_unidentified_starter_stops_before_the_case_is_read(self):
        w = World()
        a, _, _ = case(w)
        status, _ = w.run(ERASURE, erasure_trigger(a, "rev-a-00042 "), {})
        self.assertEqual(status, "Failed")
        self.assertFalse([c for c in w.calls if c[1] in ("DeleteRecord", "CreateRecord")])
        self.assertFalse([c for c in w.calls if c[2].get("entityName") == "rev_applications"])

    def test_the_hold_rule_stops_on_a_grant_without_a_final_payment(self):
        w = World()
        a, app, g = case(w, paid=False)
        status, _ = w.run(ERASURE, erasure_trigger(a, "REV-A-00042"), STARTER)
        self.assertEqual(status, "Succeeded")
        self.assertIn(a, w.tables["rev_applicants"], "nothing deleted")
        self.assertFalse([c for c in w.calls if "Delete" in c[1]])
        (row,) = w.log()
        self.assertEqual((row["rev_runtype"], row["rev_ruleapplied"], row["rev_outcome"], row["rev_recordreference"], row["_rev_startedby_value"]),
                         (2, 6, 5, "REV-A-00042", "u-emily"))
        (mail,) = w.sent
        self.assertEqual(mail["emailMessage/To"], "pat@example.org")
        self.assertIn("final payment", mail["emailMessage/Body"])
        self.assertIn("GR-2026-00003", w.messages[0])
        self.assertNotIn("Pat", w.messages[0])

    def test_a_case_with_no_grant_is_not_held(self):
        w = World()
        a, _, _ = case(w, with_grant=False)
        self.assertEqual(w.run(ERASURE, erasure_trigger(a, "REV-A-00042"), STARTER)[0], "Succeeded")
        self.assertNotIn(a, w.tables["rev_applicants"])

    def test_a_paid_case_is_erased_everywhere_and_the_evidence_says_so(self):
        w = World().setting("ErasureNotificationEmail", "dpo@example.org")
        a, app, g = case(w, deferred=True, status=9)
        status, eng = w.run(ERASURE, erasure_trigger(a, "REV-A-00042"), STARTER)
        self.assertEqual(status, "Succeeded", [(r.name, r.status, r.error) for r in eng.records if r.status == "Failed"])
        for table in ("rev_applicants", "rev_applications", "rev_reviews", "rev_grants", "rev_payments", "rev_bankaccounts"):
            self.assertEqual(w.tables[table], {}, f"{table} not emptied by the one delete and its cascade (A-ERA-2)")
        self.assertEqual(len([c for c in w.calls if c[1] == "DeleteRecord"]), 1)
        self.assertEqual(w.files, {}, "signed PDF deleted (FR-049, A-ERA-3)")
        self.assertEqual([m["id"] for m in w.mail], ["m4"], "every applicant message, and only the referee's that name the reference (A-ERA-4)")
        # snapshot before the delete, Scheduled rows before the delete
        order = [c[1] + ":" + c[2].get("entityName", "") for c in w.calls]
        self.assertLess(order.index("CreateRecord:rev_anonymisedstatistics"), order.index("DeleteRecord:rev_applicants"))
        self.assertLess(order.index("CreateRecord:rev_retentionlogs"), order.index("DeleteRecord:rev_applicants"))
        (stat,) = w.tables["rev_anonymisedstatistics"].values()
        self.assertEqual((stat["rev_outcome"], stat["rev_decisionmonth"]), (2, "2026-03-01"))
        kinds = sorted((r["rev_datatype"], r["rev_outcome"]) for r in w.log())
        self.assertEqual(kinds, [(1, 2), (2, 2), (3, 2), (4, 2), (5, 6), (6, 8)])
        (audit,) = w.log(rev_datatype=6)
        self.assertEqual((audit["rev_outcome"], audit["rev_scheduledon"], audit["rev_retaineduntil"]), (8, "2026-11-02", "2032-11-02"),
                         "Retained (audit), kept until the erasure date + 6 years (TAD 5.12.2 step 8, D3)")
        self.assertTrue(all(r["_rev_startedby_value"] == "u-emily" and r["rev_runtype"] == 2 for r in w.log()))
        (qbo,) = w.log(rev_datatype=5)
        self.assertEqual((qbo["rev_recordreference"], qbo["rev_retaineduntil"]), ("GR-2026-00003", "2026-05-10"))
        self.assertFalse([r for r in w.log() if r.get("rev_signedpdfpath")], "the path is cleared once deleted")
        requester, dpo = w.sent
        self.assertEqual(requester["emailMessage/To"], "pat@example.org")
        self.assertIn("REV-2026-007", requester["emailMessage/Body"])
        self.assertIn("10 May 2026", requester["emailMessage/Body"])
        self.assertNotIn("mother", requester["emailMessage/Body"])
        self.assertEqual(dpo["emailMessage/To"], "dpo@example.org")
        self.assertNotIn("pat@example.org", dpo["emailMessage/Body"])
        self.assertIn("DPO has been emailed", w.messages[-1])

    def test_without_a_dpo_address_no_dpo_email_is_sent_and_teams_says_so(self):
        w = World().setting("ErasureNotificationEmail", "not set")
        a, _, _ = case(w)
        self.assertEqual(w.run(ERASURE, erasure_trigger(a, "REV-A-00042"), STARTER)[0], "Succeeded")
        self.assertEqual([m["emailMessage/To"] for m in w.sent], ["pat@example.org"])
        self.assertIn("DPO was NOT emailed", w.messages[-1])

    def test_a_pdf_already_gone_is_not_an_error_and_a_rerun_after_a_failure_completes(self):
        w = World()
        a, _, _ = case(w)
        w.fail.add("Delete_the_applicant_row")
        status, _ = w.run(ERASURE, erasure_trigger(a, "REV-A-00042"), STARTER)
        self.assertEqual(status, "Failed")
        self.assertIn(a, w.tables["rev_applicants"])
        self.assertTrue(w.alerts)
        self.assertTrue(w.log(rev_outcome=1), "Scheduled rows are the evidence of the stopped run")
        w.fail.clear()
        self.assertEqual(w.run(ERASURE, erasure_trigger(a, "REV-A-00042"), STARTER)[0], "Succeeded")
        self.assertNotIn(a, w.tables["rev_applicants"])
        self.assertFalse(w.log(rev_outcome=1), "the re-run leaves no Scheduled row behind, its own or the stopped run's")


class SarExtractMode3(unittest.TestCase):
    """TAD 4.2 and 5.12 mode 3."""

    def run_sar(self, w, a):
        trig = {"entity": {"rev_applicantid": a, "rev_name": "REV-A-00042"}}
        return w.run(SAR, trig, STARTER)

    def test_one_extract_in_the_sar_folder_one_log_row_one_message_and_nothing_changed(self):
        w = World()
        a, app, g = case(w)
        w.add("audits", _objectid_value=app, createdon="2026-02-01T09:00:00Z", operation=2, action=2, changedata='{"rev_status":[5,6]}')
        before = copy.deepcopy(w.tables)
        status, eng = self.run_sar(w, a)
        self.assertEqual(status, "Succeeded", [(r.name, r.error) for r in eng.records if r.status == "Failed"])
        self.assertFalse([c for c in w.calls if c[1] in ("UpdateRecord", "DeleteRecord", "DeleteFile", "DeleteEmail_V2", "SendEmailV2")])
        self.assertEqual({c[2]["entityName"] for c in w.calls if c[1] == "UpdateOnlyRecord"}, {"rev_retentionlogs"})
        after = copy.deepcopy(w.tables)
        log_rows = after.pop("rev_retentionlogs")
        before.pop("rev_retentionlogs")
        self.assertEqual(after, before, "no business table changed (ADR-088 item 1)")
        (row,) = log_rows.values()
        self.assertEqual((row["rev_runtype"], row["rev_datatype"], row["rev_ruleapplied"], row["rev_outcome"], row["_rev_startedby_value"]),
                         (3, 7, 7, 7, "u-emily"))
        files = {name: body for folder, name, body in w.created_files if folder == "/SAR"}
        self.assertEqual(len(w.created_files), len(files), "every file goes to the SAR folder")
        (extract_name,) = [n for n in files if n.endswith(".html")]
        self.assertTrue(extract_name.startswith("REV-A-00042-SAR-2026-11-02T00-30-00Z"))
        self.assertIn(extract_name, row["rev_detail"])
        self.assertNotIn("pat@", row["rev_detail"])
        doc = files[extract_name]
        for text in ("pat@example.org", "I care for my mother.", "QB-77", "12345678", "My application", "rev_status", "Strong case",
                     "QuickBooks copy itself was not read", "1895"):
            self.assertIn(text, doc)
        for text in ("Tess Trustee", "u-trustee"):
            self.assertNotIn(text, doc, "trustee identities are removed (TAD 4.2 item 7)")
        self.assertTrue(any(n.endswith("-signed-acceptance.pdf") for n in files))
        ready, option_a = w.messages
        self.assertIn(extract_name, ready)
        self.assertIn("not switched on in this environment", option_a, "the setting ships empty: option A (ADR-091 item 4)")
        self.assertIn("delivery: option A, protected sending off in this environment", row["rev_detail"])
        for msg in (ready, option_a):
            self.assertIn(extract_name, msg)
            for text in ("pat@", "Pat", "mother"):
                self.assertNotIn(text, msg, "the Teams messages carry the reference and file name only")

    # ── delivery option B (TAD rev 37, ADR-091 item 5) ──
    def test_with_the_sender_set_the_extract_is_emailed_from_it_once_and_no_option_a_message(self):
        w = World()
        w.sender = " sar@example.org "
        a, _, _ = case(w)
        status, eng = self.run_sar(w, a)
        self.assertEqual(status, "Succeeded", [(r.name, r.error) for r in eng.records if r.status == "Failed"])
        (sent,) = w.sent
        self.assertEqual((sent["emailMessage/From"], sent["emailMessage/To"], sent["emailMessage/ReplyTo"]),
                         ("sar@example.org", "pat@example.org", "grants@example.org"))
        import base64
        attached = {a["Name"]: base64.b64decode(a["ContentBytes"]) for a in sent["emailMessage/Attachments"]}
        written = {n: World.raw(b) for f, n, b in w.created_files}
        self.assertEqual(attached, written, "every file the run wrote, the extract and the signed PDF copy, each identical to its SAR folder copy")
        self.assertEqual(len(attached), 2)
        self.assertTrue(any(n.endswith("-signed-acceptance.pdf") for n in attached), "reviewer: 'Also attach the signed pdf's'")
        self.assertNotIn("mother", sent["emailMessage/Body"])
        (ready,) = w.messages
        self.assertIn("extract ready", ready)
        (row,) = w.log()
        self.assertIn("delivery: option B, emailed from the protected sender, fits: 0.1 MB of files against a limit of 15 MB", row["rev_detail"])
        self.assertNotIn("pat@", row["rev_detail"])
        rec = next(r for r in eng.records if r.name == "Send_the_extract_protected")
        self.assertEqual(set(rec.secure), {"inputs", "outputs"}, "the send carries the extract: secured both ways")

    def test_an_envelope_copy_is_attached_too(self):
        w = World()
        w.sender = "sar@example.org"
        a, _, _ = case(w, signed=False)
        self.assertEqual(self.run_sar(w, a)[0], "Succeeded")
        (sent,) = w.sent
        import base64
        env = [base64.b64decode(x["ContentBytes"]) for x in sent["emailMessage/Attachments"] if x["Name"].endswith("-envelope.pdf")]
        self.assertEqual(env, [b"envelope-pdf:env-1"])

    def sized(self, limit="15", sizes=None, sender="sar@example.org", signed=True):
        w = World()
        w.sender = sender
        if limit is None:
            w.tables["rev_settings"] = {}
        else:
            next(iter(w.tables["rev_settings"].values()))["rev_value"] = limit
        w.sizes = sizes or {}
        a, _, _ = case(w, signed=signed)
        status, eng = self.run_sar(w, a)
        self.assertEqual(status, "Succeeded", [(r.name, r.error) for r in eng.records if r.status == "Failed"])
        return w

    def assert_nothing_sent_option_a(self, w, detail):
        self.assertFalse([c for c in w.calls if c[1] == "SendEmailV2"], "no send action runs at all: no part of the set leaves")
        msg = w.messages[-1]
        self.assertIn("NOT emailed: use option A", msg)
        self.assertIn("Nothing is ever emailed in part", msg)
        for n in [n for _, n, _ in w.created_files]:
            self.assertIn(n, msg, "references and file names only")
        for text in ("pat@", "Pat", "mother"):
            self.assertNotIn(text, msg)
        (row,) = w.log()
        self.assertIn("delivery: option A, not emailed, " + detail, row["rev_detail"])

    def test_a_set_over_the_limit_is_not_emailed_at_all(self):
        """ADR-091 Consequence 5 traced: 16 MB against the default 15 -> no SendEmailV2 -> Teams -> rev_detail too large."""
        w = self.sized(sizes={"-signed-acceptance.pdf": 16 * 1048576})
        self.assert_nothing_sent_option_a(w, "too large: 16.1 MB of files against a limit of 15 MB")

    def test_a_set_exactly_at_the_limit_is_sent_and_one_byte_more_is_not(self):
        w = self.sized(sizes={"-signed-acceptance.pdf": 15 * 1048576 - 1000, ".html": 1000})
        self.assertEqual(len(w.sent), 1)
        self.assertEqual(len(w.sent[0]["emailMessage/Attachments"]), 2)
        w = self.sized(sizes={"-signed-acceptance.pdf": 15 * 1048576 - 1000, ".html": 1001})
        self.assert_nothing_sent_option_a(w, "too large: 15.1 MB of files against a limit of 15 MB")

    def test_fail_closed_an_empty_non_numeric_or_missing_limit_counts_as_over(self):
        for limit in ("", "  ", "fifteen", "15.5", None):
            with self.subTest(limit=limit):
                w = self.sized(limit=limit)
                self.assert_nothing_sent_option_a(w, "not measured: a file size or the SarEmailMaxAttachmentMB setting could not be read")

    def test_fail_closed_a_missing_or_non_numeric_file_size_counts_as_over(self):
        for sizes in ({"-signed-acceptance.pdf": "missing"}, {".html": "missing"}, {"-signed-acceptance.pdf": "big"}):
            with self.subTest(sizes=sizes):
                w = self.sized(sizes=sizes)
                self.assert_nothing_sent_option_a(w, "not measured: a file size or the SarEmailMaxAttachmentMB setting could not be read")

    def test_with_the_setting_empty_the_size_check_does_not_matter(self):
        w = self.sized(sender="", sizes={"-signed-acceptance.pdf": 16 * 1048576})
        self.assertFalse([c for c in w.calls if c[1] == "SendEmailV2"])
        self.assertIn("not switched on in this environment", w.messages[-1])
        self.assertIn("delivery: option A, protected sending off in this environment", w.log()[0]["rev_detail"])

    def test_the_size_gate_mutations_fail(self):
        """Mutation check: removing a per-file append, or letting 'send' through without 'fits', must be caught."""
        global SAR
        saved = SAR
        try:
            # (1) the signed PDF is written but not added to the measured list: the static derivation fails
            SAR = copy.deepcopy(saved)
            lib = defn(SAR)["actions"]["Copy_signed_documents"]["actions"]["For_each_grant_document"]["actions"]["Check_the_grant_has_a_library_copy"]["actions"]
            del lib["Add_the_signed_pdf_file"]
            with self.assertRaises(AssertionError):
                ReadOnlyAndDeleteBoundaries("test_every_file_the_run_writes_is_attached_and_measured").test_every_file_the_run_writes_is_attached_and_measured()
            # and executed, the length check refuses the send rather than under-measuring the set
            w = self.sized(sizes={"-signed-acceptance.pdf": 16 * 1048576})
            self.assertFalse([c for c in w.calls if c[1] == "SendEmailV2"])
            # (2) the route ignores the check: the over-limit run would send, so the executed test above must fail
            SAR = copy.deepcopy(saved)
            r = defn(SAR)["actions"]["Compose_delivery_route"]
            r["inputs"] = r["inputs"].replace("if(startsWith(variables('attachmentCheck'), 'fits'), 'send', 'too large')", "'send'")
            w = self.sized(sizes={"-signed-acceptance.pdf": 16 * 1048576})
            self.assertTrue([c for c in w.calls if c[1] == "SendEmailV2"], "the mutation is live: without the gate the set would be sent")
            with self.assertRaises(AssertionError):
                self.assert_nothing_sent_option_a(w, "too large")
        finally:
            SAR = saved

    def test_a_failed_send_sends_nothing_else_and_tells_the_process_owner_option_a(self):
        w = World()
        w.sender = "sar@example.org"
        a, _, _ = case(w)
        w.fail.add("Send_the_extract_protected")
        status, _ = self.run_sar(w, a)
        self.assertEqual(status, "Succeeded", "the failure is handled: option A")
        self.assertEqual(w.sent, [])
        self.assertEqual(len([c for c in w.calls if c[1] == "SendEmailV2"]), 1, "no retry and no other sender (ADR-091 item 5)")
        self.assertIn("protected send failed", w.messages[-1])
        self.assertIn("delivery: option A, the protected send failed and nothing was sent", w.log()[0]["rev_detail"])

    def test_an_applicant_with_no_email_on_record_is_never_sent_to(self):
        w = World()
        w.sender = "sar@example.org"
        a, _, _ = case(w)
        w.tables["rev_applicants"][a]["rev_email"] = "  "
        status, _ = self.run_sar(w, a)
        self.assertEqual(status, "Succeeded")
        self.assertFalse([c for c in w.calls if c[1] == "SendEmailV2"])
        self.assertIn("no email address on record", w.messages[-1])
        self.assertIn("delivery: option A, no email on record", w.log()[0]["rev_detail"])

    def test_a_failed_delivery_record_alerts(self):
        w = World()
        a, _, _ = case(w)
        w.fail.add("Record_the_delivery")
        self.run_sar(w, a)
        self.assertTrue([al for al in w.alerts if "how it was delivered" in al["text_2"]])

    def test_an_unreadable_store_writes_not_read_and_the_rest_is_still_extracted(self):
        w = World()
        a, _, _ = case(w)
        w.fail.add("List_the_audit_records")
        status, _ = self.run_sar(w, a)
        self.assertEqual(status, "Succeeded")
        (doc,) = [b for f, n, b in w.created_files if n.endswith(".html")]
        self.assertIn("<h2>7. Audit history</h2><p><b>Not read.</b>", doc)
        self.assertIn("I care for my mother.", doc)
        self.assertIn("audit NOT read", w.log()[0]["rev_detail"])

    def test_an_envelope_with_no_library_copy_is_copied_from_docusign(self):
        w = World()
        a, _, _ = case(w, signed=False)
        self.assertEqual(self.run_sar(w, a)[0], "Succeeded")
        self.assertTrue(any(n.endswith("-envelope.pdf") and World.raw(b) == b"envelope-pdf:env-1" for f, n, b in w.created_files))

    def test_a_failed_extract_write_sends_no_ready_message_and_logs_nothing(self):
        w = World()
        a, _, _ = case(w)
        w.fail.add("Write_the_extract_file")
        status, _ = self.run_sar(w, a)
        self.assertEqual(status, "Failed")
        self.assertEqual(w.messages, [])
        self.assertEqual(w.log(), [])
        self.assertTrue(w.alerts)


class SweepMode1(unittest.TestCase):
    """TAD 5.12.1, against an in-memory Dataverse on Monday 2 November 2026 (first run of the month)."""

    def world(self):
        w = World().setting("RetentionStaleCaseMonths", "12")
        # due: rejected 2025-11-05 + 12 months = 2026-11-05, inside the 8-day look-ahead
        p = w.add("rev_applicants", rev_name="REV-A-00001", rev_lastcontactdate="2025-11-05")
        self.rejected = w.add("rev_applications", rev_name="REV-2025-001", _rev_applicantid_value=p, rev_status=8, rev_decisiondate="2025-11-05")
        # not due: rejected 2025-12-20 + 12 months is beyond the look-ahead
        q = w.add("rev_applicants", rev_name="REV-A-00002", rev_lastcontactdate="2026-10-01")
        w.add("rev_applications", rev_name="REV-2025-002", _rev_applicantid_value=q, rev_status=8, rev_decisiondate="2025-12-20")
        # due: paid grant, final payment 2020-11-06, plus an open application for the same applicant (not orphaned)
        r = w.add("rev_applicants", rev_name="REV-A-00003", rev_lastcontactdate="2026-10-01")
        paid = w.add("rev_applications", rev_name="REV-2020-009", _rev_applicantid_value=r, rev_status=11)
        w.add("rev_grants", rev_name="GR-2020-00001", _rev_applicationid_value=paid, rev_finalpaymentdate="2020-11-06",
              rev_signedpdfurl="/Signed/GR-2020-00001-signed-acceptance.pdf")
        w.files["/Signed/GR-2020-00001-signed-acceptance.pdf"] = b"pdf"
        w.add("rev_applications", rev_name="REV-2026-050", _rev_applicantid_value=r, rev_status=3)
        # due: withdrawn, applicant last contact 2026-05-08, deferred review (snapshot owed)
        s = w.add("rev_applicants", rev_name="REV-A-00004", rev_lastcontactdate="2026-05-08", rev_agerange=2, rev_locationarea=1)
        self.withdrawn = w.add("rev_applications", rev_name="REV-2026-004", _rev_applicantid_value=s, rev_status=9, rev_conditionprofile="3")
        w.add("rev_reviews", _rev_applicationid_value=self.withdrawn, rev_outcome=2, rev_paneldate="2026-04-15", createdon="2026-04-10T00:00:00Z")
        # stale: an open case whose applicant has had no contact for 13 months
        t = w.add("rev_applicants", rev_name="REV-A-00005", rev_lastcontactdate="2025-09-01")
        w.add("rev_applications", rev_name="REV-2025-077", _rev_applicantid_value=t, rev_status=5)
        return w

    def test_the_pre_pass_logs_each_application_coming_due_once_with_its_rule_and_date(self):
        w = self.world()
        status, eng = w.run(SWEEP, {})
        self.assertEqual(status, "Succeeded", [(r.name, r.error) for r in eng.records if r.status == "Failed"])
        apps = {r["rev_recordreference"]: (r["rev_ruleapplied"], r["rev_scheduledon"], r.get("rev_signedpdfpath")) for r in w.log(rev_datatype=2)}
        self.assertEqual(apps, {"REV-2025-001": (2, "2026-11-05", None),
                                "REV-2020-009": (1, "2026-11-06", "/Signed/GR-2020-00001-signed-acceptance.pdf"),
                                "REV-2026-004": (3, "2026-11-08", None)})
        applicants = {r["rev_recordreference"]: r["rev_scheduledon"] for r in w.log(rev_datatype=1)}
        self.assertEqual(applicants, {"REV-A-00001": "2026-11-05", "REV-A-00004": "2026-11-08"},
                         "REV-A-00003 keeps an open application, so it is not orphaned")
        self.assertTrue(all(r["rev_outcome"] == 1 and r["rev_runtype"] == 1 and "_rev_startedby_value" not in r for r in w.log()))
        self.assertEqual(len(w.tables["rev_anonymisedstatistics"]), 1, "only the deferred, never re-decided case gets a snapshot")
        self.assertIn("Coming due and logged: 5", w.messages[0])
        self.assertIn("REV-2025-077", w.messages[0], "the stale open case is listed on the first run of the month (D4)")

    def test_a_second_run_writes_nothing_twice(self):
        w = self.world()
        w.run(SWEEP, {})
        n = len(w.log())
        stats = len(w.tables["rev_anonymisedstatistics"])
        w.run(SWEEP, {})
        self.assertEqual((len(w.log()), len(w.tables["rev_anonymisedstatistics"])), (n, stats))
        self.assertIn("Coming due and logged: 0", w.messages[-1])

    def test_reconcile_records_a_deletion_removes_the_pdf_flags_overdue_and_not_due(self):
        w = self.world()
        gone = w.add("rev_retentionlogs", rev_runtype=1, rev_recordreference="REV-2019-001", rev_datatype=2, rev_outcome=1,
                     rev_scheduledon="2026-10-10", rev_signedpdfpath="/Signed/GR-2019-00001-signed-acceptance.pdf")
        w.files["/Signed/GR-2019-00001-signed-acceptance.pdf"] = b"pdf"
        late = w.add("rev_retentionlogs", rev_runtype=1, rev_recordreference="REV-2025-002", rev_datatype=2, rev_outcome=1, rev_scheduledon="2026-09-01")
        recent = w.add("rev_retentionlogs", rev_runtype=1, rev_recordreference="REV-2026-050", rev_datatype=2, rev_outcome=1, rev_scheduledon="2026-10-20")
        new_app = w.add("rev_retentionlogs", rev_runtype=1, rev_recordreference="REV-A-00003", rev_datatype=1, rev_outcome=1, rev_scheduledon="2026-08-01")
        nopdf = w.add("rev_retentionlogs", rev_runtype=1, rev_recordreference="REV-A-09999", rev_datatype=1, rev_outcome=1, rev_scheduledon="2026-10-30")
        gonepdf = w.add("rev_retentionlogs", rev_runtype=1, rev_recordreference="REV-2019-002", rev_datatype=2, rev_outcome=1,
                        rev_scheduledon="2026-10-10", rev_signedpdfpath="/Signed/already-gone.pdf")
        status, eng = w.run(SWEEP, {})
        self.assertEqual(status, "Succeeded", [(r.name, r.error) for r in eng.records if r.status == "Failed"])
        t = w.tables["rev_retentionlogs"]
        self.assertEqual((t[gone]["rev_outcome"], t[gone]["rev_signedpdfpath"]), (2, None))
        self.assertNotIn("/Signed/GR-2019-00001-signed-acceptance.pdf", w.files)
        self.assertEqual(t[gonepdf]["rev_outcome"], 2, "a PDF already gone is not an error (A-ERA-3)")
        self.assertEqual(t[late]["rev_outcome"], 4, "still there 35 days after its date: Overdue (NFR-010)")
        self.assertEqual(t[recent]["rev_outcome"], 1, "still there, inside 35 days: unchanged")
        self.assertEqual(t[new_app]["rev_outcome"], 3, "applicant kept by a new application: Not due, not Overdue")
        self.assertEqual(t[nopdf]["rev_outcome"], 2, "applicant gone: Deleted")
        self.assertIn("Overdue (still there 35 days after their date): 1 - REV-2025-002", w.messages[-1])
        self.assertFalse([c for c in w.calls if c[1] == "DeleteRecord"])

    def test_the_stale_list_is_monthly_and_a_missing_setting_is_said(self):
        global NOW
        saved = NOW
        try:
            NOW = datetime(2026, 11, 9, 0, 30, tzinfo=timezone.utc)
            w = self.world()
            w.run(SWEEP, {})
            self.assertIn("listed on the first run of each month", w.messages[-1])
            NOW = saved
            w = self.world()
            w.tables["rev_settings"] = {}
            self.assertEqual(w.run(SWEEP, {})[0], "Succeeded")
            self.assertIn("setting is missing or is not a whole number", w.messages[-1])
        finally:
            NOW = saved


class SnapshotChild(unittest.TestCase):
    def run_snapshot(self, outcome, status):
        w = World()
        a = w.add("rev_applicants", rev_agerange=1, rev_locationarea=4)
        app = w.add("rev_applications", _rev_applicantid_value=a, rev_status=status, rev_conditionprofile="1,7")
        w.add("rev_reviews", _rev_applicationid_value=app, rev_outcome=outcome, rev_paneldate="2026-06-20", createdon="2026-06-01T00:00:00Z")
        eng = w.engine(SNAPSHOT, {"text": app})
        self.assertEqual(eng.run(), "Succeeded")
        return w, eng

    def test_a_deferred_case_that_was_never_re_decided_gets_one_not_granted_row(self):
        for status in (6, 9, 10):
            with self.subTest(status=status):
                w, eng = self.run_snapshot(2, status)
                (row,) = w.tables["rev_anonymisedstatistics"].values()
                self.assertEqual((row["rev_outcome"], row["rev_agerange"], row["rev_conditionareas"], row["rev_decisionmonth"]), (2, 1, "1,4", "2026-06-01"))
                self.assertEqual(eng.response, (200, {"written": True}))

    def test_a_decided_or_not_deferred_case_gets_nothing(self):
        for outcome, status in ((2, 7), (2, 8), (2, 11), (1, 9), (3, 9)):
            with self.subTest(outcome=outcome, status=status):
                w, eng = self.run_snapshot(outcome, status)
                self.assertEqual(w.tables["rev_anonymisedstatistics"], {})
                self.assertEqual(eng.response, (200, {"written": False}))


class LocateChild(unittest.TestCase):
    def test_it_returns_the_whole_case_and_nothing_of_anyone_else(self):
        w = World()
        a, app, g = case(w)
        other = w.add("rev_applicants", rev_name="REV-A-00099")
        w.add("rev_applications", rev_name="REV-2026-099", _rev_applicantid_value=other)
        eng = w.engine(LOCATE, {"text": a})
        self.assertEqual(eng.run(), "Succeeded")
        code, body = eng.response
        self.assertEqual(code, 200)
        self.assertTrue(body["found"])
        self.assertEqual([x["rev_name"] for x in body["applications"]], ["REV-2026-007"])
        self.assertEqual([len(body[k]) for k in ("reviews", "grants", "payments", "bankaccounts")], [1, 1, 1, 1])
        self.assertEqual(w.calls and {c[1] for c in w.calls}, {"ListRecords"})

    def test_an_applicant_with_no_application_returns_empty_lists(self):
        w = World()
        a = w.add("rev_applicants", rev_name="REV-A-00100")
        eng = w.engine(LOCATE, {"text": a})
        self.assertEqual(eng.run(), "Succeeded")
        self.assertEqual([eng.response[1][k] for k in ("applications", "reviews", "grants", "payments")], [[], [], [], []])


if __name__ == "__main__":
    unittest.main()
