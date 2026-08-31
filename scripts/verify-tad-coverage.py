#!/usr/bin/env python3
"""Verify solution source actually contains the schema and access the approved TAD specifies.

WHY THIS EXISTS. Every other schema gate in this repository compares solution source against
OTHER solution source: `IsSecured` against the field security profile, `RootComponents` against
what is on disk, form cells against the attributes they bind. **An ABSENT column is absent from
both sides of every one of those comparisons**, so it is invisible to all of them. Twelve
columns the approved TAD names went missing for eleven days and every schema gate passed the
whole time (IMP-0158). The TAD is the schema's specification and no executable check had ever
read it.

The access half is the same gap with teeth (IMP-0159). TAD §3.1 marks two `rev_applicant`
columns trustee-visible while §6.2's row for that persona lists Read on Application, Review and
Grant only. Column security **releases** a column; it never **grants** table access, so a
trustee-visible column on a table the trustee role cannot read is unreachable — the row itself
does not come back. The two statements are mutually unsatisfiable, which is why FR-034 was
unimplementable as written, and nothing compared §3.1 against `Roles/*.xml`.

WHAT IT CHECKS. Three assertions. (a) and (b) are driven from the primary TAD's §3.1 table;
(c) reads the deliverable-now PROSE of every design document in the directory:

  (a) EXISTENCE. Every column §3.1 names exists as an `<attribute PhysicalName=...>` in
      `Entities/<table>/Entity.xml`, or is covered by an entry in the declared deferral file
      (`contract/tad-deferrals.json`) carrying an owner, a reason, a clearing action and an
      unexpired date. A deferral missing any of those, or past its date, is itself a FAILURE —
      the same rule and the same reasoning as `contract/known-exceptions.json`, whose own `_why`
      says it best: a gate switched off because reality violates it is the gate-cannot-fail
      class arriving by the front door. A deferral that no longer matches anything, or names a
      column that now exists, also FAILS, so the file cannot silently become a blanket.

  (b) REACHABILITY. Every column §3.1 marks `trustee-visible` sits on a table the
      `REV Trustee` role holds a `prvRead<table>` privilege for, read from
      `Roles/REV Trustee/REV Trustee.xml`. Comments in that file are not privileges: the role
      is parsed as XML, never grepped, because the file discusses `prvReadrev_applicant` in
      prose in five places.

  (c) DELIVERABLE-NOW CLAIMS ARE CHECKABLE. In EVERY `*.md` under `--design-docs`, each item
      of a bolded "deliverable now / ships now" list names a backticked `rev_*` column, and
      every column it names exists. Added 2026-08-26 by improvement review 29 change 1, on the
      THIRD instance of `requirement-names-data-the-solution-cannot-supply` (IMP-0326, after
      IMP-0293 and IMP-0296) — the second and third of which both arrived after a *prose*
      answer, which is the regression rule's own definition of the wrong altitude. The full
      reasoning, the narrow-cue measurement and three named residuals sit above
      `check_deliverable_now_claims()`.

WHAT IT CANNOT DO. **It cannot judge whether the TAD is RIGHT** — only whether source agrees
with it. Assertion (c) is the narrow exception: it makes a claim CHECKABLE, and still cannot
say whether a resolvable column is the right column. A column the TAD should name and does not is invisible here, exactly as it is to every
other gate; a wrong classification, a wrong Tier, a wrong control, or an internal contradiction
between §3.1 and §6.2 all pass this gate silently. It also says nothing about the LIVE
environment: an attribute in `Entity.xml` is a shipped intent, not a created column
(C-TECH-064). And it reads §3.1 only — §3 names `rev_granthistory` conditionally with no §3.1
block, so that table is out of scope.

STRUCTURAL SAFETY. It parses markdown, so a reword breaks it — and the failure mode of a broken
markdown parser is finding nothing, which every `! grep ... && echo` in this repository's
history turned into a PASS (`gate-cannot-fail`, 23 recorded instances; IMP-0007). So this gate
FAILS when it parses too little to be checking anything: the minimum counts in `_MINIMUMS`
below are asserted before any comparison runs, each with the reason its number is what it is.
There is no flag to lower them.

Run:
    python3 scripts/verify-tad-coverage.py
    python3 scripts/verify-tad-coverage.py --tad PATH --solution DIR --deferrals PATH
    python3 scripts/verify-tad-coverage.py --selftest    # prove the gate can fail, and can pass

Exits 0 when clean, 1 on any violation, 2 on a usage error.

C-TECH-066.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib.gate_baseline import BaselineError, load_baselines  # noqa: E402

GATE = "tad-coverage"

# ── Minimum parse yields ─────────────────────────────────────────────────────
# Asserted BEFORE any comparison. A markdown parser that has stopped matching reports zero
# findings, which is indistinguishable from clean source. Each number is a floor with slack,
# not a transcription of today's count — a floor that equals today's count fails on the next
# legitimate TAD edit, and a gate that cries wolf gets routed around (review 6, cluster A).
_MINIMUMS = {
    # §3 names ten tables plus one conditional; §3.1 currently gives a block to all ten.
    # Eight allows two tables to be legitimately dropped before the gate stops trusting its
    # own parse.
    "table_blocks": (8, "TAD §3 names ten tables and §3.1 blocks all ten; 8 leaves slack for two"),
    # rev_applicant and rev_application are the only two blocks written as per-column markdown
    # TABLES, and they are where every `trustee-visible` mark lives. If either stops parsing,
    # assertion (b) silently checks nothing. Neither can be dropped without deleting the
    # applicant or the application from the design.
    "markdown_tables": (2, "rev_applicant and rev_application carry the per-column tables and "
                           "every trustee-visible mark; losing either blinds assertion (b)"),
    # 129 (table, column) specs parse from §3.1 on 2026-08-21. 100 is a floor low enough to
    # survive one table being legitimately removed, high enough that a broken row regex — which
    # yields a handful of specs, not a hundred — cannot slip past it.
    "specs": (100, "129 specs parsed on 2026-08-21; 100 survives one table's removal and no more"),
    # §3.1 marks rev_agerange and rev_locationarea trustee-visible (FR-027) — the two columns
    # IMP-0159 is about. Zero here means assertion (b) is inert.
    "trustee_visible": (2, "FR-027's rev_agerange and rev_locationarea are the irreducible "
                           "minimum; zero means assertion (b) is inert"),
}

# ── §3.1 markdown shapes ─────────────────────────────────────────────────────
_SECTION_START = re.compile(r"^###\s+3\.1(\s|$)")
_SECTION_END = re.compile(r"^###\s+3\.2(\s|$)")
# Every per-table block in §3.1 opens the same way: **`rev_x` — Tier N...**
_BLOCK_HEADER = re.compile(r"^\*\*`(rev_[a-z0-9_]+)`\s*[—–-]\s*Tier\b")
_CODE_SPAN = re.compile(r"`([^`]+)`")
_PLAIN_COLUMN = re.compile(r"^rev_[a-z0-9_]+$")
# "trustee-visible" only, hyphenated. NOT "trustee visibility", which appears on
# rev_redactionreviewrequired as a statement about a CONDITION, not a marking.
_TRUSTEE_VISIBLE = re.compile(r"trustee-visible", re.IGNORECASE)
# `rev_wellbeinganswer1..n` — a family of unfixed arity.
_FAMILY = re.compile(r"^(rev_[a-z0-9_]*?)(\d+)\.\.[a-z]$")

# Suffix vocabulary for the collapsed form §3.1 uses to save a row:
# `rev_helpername/email/phone` means rev_helpername, rev_helperemail, rev_helperphone.
# This is a hand-kept list, so it is the thing that can go stale (review 6, cluster A). It is
# therefore FAIL-CLOSED: a slash form this list cannot expand is reported as an unresolvable
# spec, never skipped.
_STEM_SUFFIXES = ("reason", "notes", "amount", "start", "email", "phone", "note",
                  "name", "date", "ref", "end", "id", "on", "by")


class Violation:
    def __init__(self, where: str, message: str, remedy: str = "") -> None:
        self.where, self.message, self.remedy = where, message, remedy

    def __str__(self) -> str:
        out = f"{self.where}: {self.message}"
        if self.remedy:
            out += f"\n    → {self.remedy}"
        return out


class Spec:
    """One (table, column) statement made by TAD §3.1."""

    def __init__(self, table: str, column: str, line: int, trustee_visible: bool,
                 family: bool = False) -> None:
        self.table = table
        self.column = column
        self.line = line
        self.trustee_visible = trustee_visible
        self.family = family

    @property
    def key(self) -> tuple[str, str]:
        return (self.table, self.column)


# ── Parsing the TAD ──────────────────────────────────────────────────────────

def _expand(token: str) -> list[str] | None:
    """Expand one code span into the column names it states, or None if it cannot be resolved."""
    token = token.strip()
    if _PLAIN_COLUMN.match(token):
        return [token]
    if "/" in token:
        parts = [p.strip() for p in token.split("/") if p.strip()]
        head = parts[0]
        if not _PLAIN_COLUMN.match(head):
            return None
        names = [head]
        stem = None
        for suffix in _STEM_SUFFIXES:
            # len(head) - len(suffix) > 4 keeps "rev_" plus at least one real character.
            if head.endswith(suffix) and len(head) - len(suffix) > 4:
                stem = head[: -len(suffix)]
                break
        if stem is None:
            return None
        for part in parts[1:]:
            if not part.isalnum():
                return None
            names.append(stem + part)
        return names
    return None


def parse_section_31(text: str) -> tuple[list[Spec], dict, list[Violation]]:
    """Every (table, column) statement in TAD §3.1, plus what the parse yielded."""
    lines = text.splitlines()
    start = end = None
    for index, line in enumerate(lines):
        if start is None and _SECTION_START.match(line):
            start = index
        elif start is not None and _SECTION_END.match(line):
            end = index
            break
    problems: list[Violation] = []
    if start is None:
        return [], {"table_blocks": 0, "markdown_tables": 0, "specs": 0,
                    "trustee_visible": 0, "tables": []}, problems
    body = lines[start:end if end is not None else len(lines)]
    offset = start + 1  # 1-based file line number of body[0]

    # Cut the section into per-table blocks.
    blocks: list[tuple[str, int, list[str]]] = []
    for index, line in enumerate(body):
        match = _BLOCK_HEADER.match(line)
        if match:
            blocks.append((match.group(1), offset + index, []))
        elif blocks:
            blocks[-1][2].append(line)

    specs: list[Spec] = []
    markdown_tables = 0
    for table, header_line, block_lines in blocks:
        rows = [(header_line + 1 + i, l) for i, l in enumerate(block_lines)]
        table_rows = [(n, l) for n, l in rows if l.lstrip().startswith("|")]
        if table_rows:
            markdown_tables += 1
            for number, line in table_rows:
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if not cells or set(cells[0]) <= set("- :") or cells[0].lower() == "attribute":
                    continue  # separator row or header row
                visible = bool(_TRUSTEE_VISIBLE.search(line))
                for token in _CODE_SPAN.findall(cells[0]):
                    specs += _specs_from(table, token, number, visible, problems)
        else:
            # Prose block: the header line itself carries the column list.
            prose = [(header_line, body[header_line - offset])]
            prose += [(n, l) for n, l in rows
                      if l.strip() and not l.lstrip().startswith(">")]
            first = True
            for number, line in prose:
                visible = bool(_TRUSTEE_VISIBLE.search(line))
                for token in _CODE_SPAN.findall(line):
                    if first and token == table:
                        first = False
                        continue  # the block header names its own table
                    if not token.startswith("rev_"):
                        continue  # `REV_FinanceOnly`, `GR-2026-00001`, `KnockoutThreshold`
                    specs += _specs_from(table, token, number, visible, problems)

    # De-duplicate: §3.1 states rev_name once per block, and a prose block repeats nothing else.
    seen: dict[tuple[str, str], Spec] = {}
    for spec in specs:
        if spec.key in seen:
            seen[spec.key].trustee_visible |= spec.trustee_visible
        else:
            seen[spec.key] = spec
    unique = list(seen.values())

    stats = {
        "table_blocks": len(blocks),
        "markdown_tables": markdown_tables,
        "specs": len(unique),
        "trustee_visible": sum(1 for s in unique if s.trustee_visible),
        "tables": sorted({s.table for s in unique}),
    }
    return unique, stats, problems


def _specs_from(table: str, token: str, line: int, visible: bool,
                problems: list[Violation]) -> list[Spec]:
    family = _FAMILY.match(token)
    if family:
        # `rev_wellbeinganswer1..n`: n is not fixed by the TAD, so the strongest honest check
        # is that the first member exists.
        return [Spec(table, family.group(1) + family.group(2), line, visible, family=True)]
    names = _expand(token)
    if names is None:
        problems.append(Violation(
            f"TAD §3.1:{line}",
            f"`{token}` on {table} is not a column spec this gate can resolve",
            "write it as one code span per column, or add its trailing word to "
            "_STEM_SUFFIXES in this script. It is reported rather than skipped on purpose: a "
            "spec silently dropped is a column silently unchecked (IMP-0007)"))
        return []
    return [Spec(table, name, line, visible) for name in names]


# ── Reading solution source ──────────────────────────────────────────────────

def entity_columns(solution: Path, table: str) -> set[str] | None:
    """Every attribute on a table, or None when the table itself is absent from source."""
    path = solution / "Entities" / table / "Entity.xml"
    if not path.is_file():
        return None
    root = ET.parse(path).getroot()
    found: set[str] = set()
    for attribute in root.iter("attribute"):
        name = attribute.get("PhysicalName")
        if not name:
            child = attribute.find("LogicalName")
            name = (child.text or "").strip() if child is not None else ""
        if name:
            found.add(name.strip().lower())
    return found


# ── (c) "DELIVERABLE NOW" PROSE CLAIMS, across EVERY design document ─────────────────────
#
# WHY THIS CHECK EXISTS AND WHY IT LOOKS LIKE THIS (improvement review 29 change 1, cluster A).
#
# `requirement-names-data-the-solution-cannot-supply` reached its THIRD instance on 2026-08-25
# (IMP-0326, after IMP-0293 and IMP-0296) — and the second and third both arrived AFTER a
# written answer. Review 27 built the Data Provenance guidance for the flavour where no column
# supplies an item; review 28 added a third row for the flavour where no organisation holds the
# data. Within hours a delta TAD promised "preferred dates" as deliverable "now, with no schema
# change", and no preferred, holiday or travel date column exists anywhere in the solution:
# every date column on rev_application is a consent, decision, panel, payment, snapshot,
# date-of-birth or last-contact date. A recurrence after a prose fix is evidence the fix was at
# the wrong altitude, so the third instance is a gate.
#
# TWO AXES, AND THE SECOND IS THE LOAD-BEARING ONE.
#
#   SOURCE. Assertions (a) and (b) read ONE document — the `--tad` default. A delta TAD in the
#   same directory was read by nothing at all. This check reads every `*.md` under
#   `--design-docs`.
#
#   SHAPE. An identifier-RESOLVING check alone would have passed the very sentence that
#   convened the cluster, because "preferred dates" is not an identifier — it is prose, and
#   there is nothing to resolve. So the rule is that each ITEM of a deliverable-now list must
#   NAME a backticked `rev_*` column, and every named column must exist. Requiring the
#   identifier is what makes the claim checkable at all; resolving it is the easy part.
#
# THE CUE IS DELIBERATELY NARROW: a BOLDED lead-in ENDING IN A COLON. Measured against the four
# design documents before wiring, five lines contain a "no schema change"-style phrase and only
# one is a deliverables list; the other four are a section heading, a statement about a flow
# change, a traceability row and a paragraph about ALM. A looser cue would have fired on all
# five, which is the gate-fires-on-nothing class this repository has recorded five times.
#
# RESIDUALS, all three named because none is covered:
#   1. A delta TAD that states its deliverables outside a recognisable list — in a table, or as
#      ordinary unbolded prose — is invisible here.
#   2. This proves a named column EXISTS. It cannot judge whether it is the RIGHT column.
#   3. Assertions (a) and (b) still read the primary TAD only, and that is on purpose: the
#      `_MINIMUMS` floor is calibrated to the parent §3.1's scale, so running it over a delta
#      TAD's smaller §3.1 would trip the floor and report a false failure. Widening the TABLE
#      assertions needs a per-document floor, which is not this change.

_DELIVERABLE_NOW_CUE = re.compile(
    r"^\*\*(?P<lead>[^*]*\b(?:deliverable|delivers|delivered|ships|shipping|available)\s+now\b"
    r"[^*]*):\*\*(?P<rest>.*)$",
    re.IGNORECASE)
_BACKTICKED_COLUMN = re.compile(r"`(rev_[a-z0-9_]+)")


def all_solution_columns(solution: Path) -> set[str]:
    """Every attribute PhysicalName on every table. The prose items name no table, so a
    claim is checked against the whole schema rather than against one entity."""
    found: set[str] = set()
    for entity_dir in sorted((solution / "Entities").glob("*")):
        columns = entity_columns(solution, entity_dir.name)
        if columns:
            found |= columns
    return found


def split_list_items(text: str) -> list[str]:
    """Split a prose enumeration on commas at depth 0. Parentheses, brackets and backtick
    spans GROUP, so 'total funding (`a` + `b`, with the `c` flag)' stays one item — a naive
    comma split reports three phantom items and the gate becomes noise."""
    items: list[str] = []
    buf: list[str] = []
    depth = 0
    in_ticks = False
    for ch in text:
        if ch == "`":
            in_ticks = not in_ticks
        elif not in_ticks and ch in "([":
            depth += 1
        elif not in_ticks and ch in ")]":
            depth = max(0, depth - 1)
        if ch == "," and depth == 0 and not in_ticks:
            items.append("".join(buf))
            buf = []
            continue
        buf.append(ch)
    items.append("".join(buf))

    out: list[str] = []
    for raw in items:
        cleaned = re.sub(r"^\s*(?:and|&)\s+", "", raw.strip(), flags=re.IGNORECASE)
        cleaned = cleaned.strip(" .;:")
        if cleaned:
            out.append(cleaned)
    return out


def check_deliverable_now_claims(docs_dirs: Path | list[Path],
                                 solution: Path) -> tuple[list[Violation], dict]:
    """Assertion (c). Every item of every deliverable-now list names a column that exists.

    Takes SEVERAL directories since 2026-08-28 (review 36, `IMP-0425`). It read
    `docs/architecture` only, because that was the one design-document directory when the
    default was set; `docs/plans` grew into a second one and nothing revisited the default, so
    three design documents were read by no gate at all for their deliverable-now claims.
    Measured before the change: `--design-docs docs/plans` reports **0 items in 0 claims across
    3 documents**, because the cue is a bolded "deliverable now / ships now" list and those
    documents carry none. So this is a scope repair with no measured effect today — recorded as
    such rather than as a coverage win, per the entry's own correction.
    """
    if isinstance(docs_dirs, Path):
        docs_dirs = [docs_dirs]
    stats = {"docs_read": 0, "claims": 0, "items": 0, "unnamed": 0, "unresolvable": 0}
    violations: list[Violation] = []

    missing = [d for d in docs_dirs if not d.is_dir()]
    if missing:
        return [Violation(str(d), "design-document directory not found — a gate pointed "
                                  "at a missing target does not pass (IMP-0007)")
                for d in missing], stats

    known = all_solution_columns(solution)
    if not known:
        return [Violation(str(solution), "no attributes parsed from any Entity.xml, so no "
                                         "identifier could ever resolve; refusing to report OK "
                                         "over nothing (IMP-0007)")], stats

    for doc in sorted(d for docs_dir in docs_dirs for d in docs_dir.glob("*.md")):
        stats["docs_read"] += 1
        lines = doc.read_text(encoding="utf-8").splitlines()
        for index, line in enumerate(lines):
            match = _DELIVERABLE_NOW_CUE.match(line.strip())
            if not match:
                continue
            stats["claims"] += 1
            # The claim runs to the next blank line: these lists are wrapped prose.
            body = [match.group("rest")]
            cursor = index + 1
            while cursor < len(lines) and lines[cursor].strip():
                body.append(lines[cursor])
                cursor += 1
            lead = match.group("lead").strip()
            where = f"{doc.name}:{index + 1}"

            for item in split_list_items(" ".join(body)):
                stats["items"] += 1
                named = [c.lower() for c in _BACKTICKED_COLUMN.findall(item)]
                if not named:
                    stats["unnamed"] += 1
                    violations.append(Violation(
                        where,
                        f'"{lead}" promises "{item}" and names no column. A deliverable-now '
                        f"claim written as prose is not checkable by anything, which is how "
                        f"'preferred dates' shipped as deliverable against a solution that has "
                        f"no such column (IMP-0326, third instance)",
                        "name the backticked `rev_*` column(s) that supply this item — or, if "
                        "none exists, move the item out of the deliverable-now list and say "
                        "what has to change first"))
                    continue
                missing = [c for c in named if c not in known]
                if missing:
                    stats["unresolvable"] += 1
                    violations.append(Violation(
                        where,
                        f'"{lead}" promises "{item}" naming '
                        f"{', '.join(sorted(missing))}, which "
                        f"{'does' if len(missing) == 1 else 'do'} not exist in any Entity.xml",
                        "add the attribute to solution source, or withdraw the claim. "
                        "'No schema change' is a statement about source, so source decides it"))
    return violations, stats


def trustee_read_tables(solution: Path) -> tuple[set[str] | None, Path]:
    """Tables the REV Trustee role holds prvRead for. Parsed as XML — the file's own comments
    name prvReadrev_applicant in prose five times, so grep would answer the wrong question."""
    path = solution / "Roles" / "REV Trustee" / "REV Trustee.xml"
    if not path.is_file():
        return None, path
    root = ET.parse(path).getroot()
    tables: set[str] = set()
    for privilege in root.iter("RolePrivilege"):
        name = (privilege.get("name") or "").strip()
        if name.lower().startswith("prvread"):
            tables.add(name[len("prvRead"):].lower())
    return tables, path


# ── The declared deferral file ───────────────────────────────────────────────

_REQUIRED_DEFERRAL_FIELDS = ("id", "table", "columns", "reason", "owner", "clears_when",
                             "expires")


class Deferral:
    def __init__(self, raw: dict, index: int) -> None:
        self.raw = raw
        self.index = index
        self.id = str(raw.get("id") or f"entry #{index + 1}")
        self.table = str(raw.get("table") or "").strip().lower()
        columns = raw.get("columns")
        self.all_columns = columns == "*"
        self.columns = ({str(c).strip().lower() for c in columns}
                        if isinstance(columns, list) else set())
        self.used = False

    def covers(self, spec: Spec) -> bool:
        if spec.table != self.table:
            return False
        return self.all_columns or spec.column in self.columns


def load_deferrals(path: Path, today: _dt.date) -> tuple[list[Deferral], list[Violation]]:
    problems: list[Violation] = []
    if not path.is_file():
        return [], problems  # no deferral file is a legitimate state: nothing is deferred
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [], [Violation(str(path), f"is not valid JSON: {exc}",
                              "a deferral file that does not parse defers nothing, and this "
                              "gate will not treat it as if it did")]
    entries = doc.get("deferrals")
    if not isinstance(entries, list):
        return [], [Violation(str(path), "has no `deferrals` array",
                              "give it a `deferrals` array, even an empty one")]

    deferrals: list[Deferral] = []
    for index, raw in enumerate(entries):
        if not isinstance(raw, dict):
            problems.append(Violation(f"{path}[{index}]", "is not an object"))
            continue
        deferral = Deferral(raw, index)
        missing = [f for f in _REQUIRED_DEFERRAL_FIELDS
                   if not str(raw.get(f) or "").strip() and raw.get(f) != "*"
                   and not isinstance(raw.get(f), list)]
        if missing:
            problems.append(Violation(
                f"{path} → {deferral.id}",
                f"deferral is missing {', '.join(missing)}",
                "every deferral carries an owner, a reason, a clearing action and a dated "
                "expiry. An unowned or undated deferral is indistinguishable from a column "
                "nobody has noticed is missing — same rule as contract/known-exceptions.json"))
            continue
        expires = str(raw.get("expires")).strip()
        try:
            when = _dt.date.fromisoformat(expires)
        except ValueError:
            problems.append(Violation(
                f"{path} → {deferral.id}",
                f"`expires` is `{expires}`, which is not an ISO date (YYYY-MM-DD)",
                "a date this gate cannot compare is not a date"))
            continue
        if when < today:
            problems.append(Violation(
                f"{path} → {deferral.id}",
                f"expired on {expires} — deferred column(s) on {deferral.table} are still absent",
                f"build them, or re-date the deferral with a reason. Owner: "
                f"{raw.get('owner')}"))
            continue
        deferrals.append(deferral)
    return deferrals, problems


# ── (d)(e)(f) THE RESPONSE CONTRACT ──────────────────────────────────────────
#
# WHY THESE EXIST. Assertions (a)-(c) read the TAD's §3.1 COLUMN table. A requirement can be
# fully covered at column level and still be undelivered, because the columns exist and nothing
# COMPUTES the answer from them. That is what happened: the round-statistics flow composes
# `"applicationsPerDay":null` as a literal, FR-058 is partial and FR-059/FR-060 are undelivered,
# and every source-against-source gate passed because every column they read exists. The one
# table that records it — Appendix A's requirement traceability, which is what phase acceptance
# reads — was read by nothing at any strictness (IMP-0451, IMP-0454, IMP-0455).
#
# THE POLARITY RULE THAT SHAPED THE DESIGN. Five prior candidates in this repository were
# measured as phrase gates and scored the CORRECTED file worse than the defective one, because a
# correction here RETAINS the wording it withdraws (IMP-0422, IMP-0428). So every one of these
# three assertions TRIGGERS on a VALUE read from source — a literal `null` in a composed
# document, a literal status string, a register entry's own fields — and only the ACQUITTAL
# reads prose. Measured both ways before wiring: 4 findings against the pre-correction document
# and 0 against the corrected one. A correction makes this gate greener, never redder.
#
# TWO ACQUITTAL PATHS, AND THE WEAKER ONE IS NAMED ON EVERY RUN. A null response key is excused
# either by an `undelivered_requirements` entry (owned, dated, expiring) or by a not-delivered
# marker in the Appendix A requirement row that names it. The register is preferred and the
# prose path is kept only because `ethnicGroupDistribution` is a shortfall the reviewer has
# already closed (OQ-037, benchmark withdrawn) and needs no owner. Because the prose path is an
# escape hatch, the summary line prints WHICH path acquitted each key — per
# tad-deferrals.json's own rule that a deferral suppresses the FAIL and never the report.

_NULL_KEY = re.compile(r'\\"([A-Za-z_][A-Za-z0-9_]*)\\"\s*:\s*null')
_STATUS_LITERAL = re.compile(r'\\"status\\"\s*:\s*\\"([a-z][a-z-]*)\\"')
_APP_STATUS = re.compile(r"""status\s*:\s*['"]([a-z][a-z-]*)['"]""")
_NON_OK_ACTION = re.compile(r"error|pending|fail", re.I)
_NOT_DELIVERED = re.compile(
    r"\bnull\b|\bpartial\b|\bawait\w*\b|\bwithdrawn\b|\bundelivered\b|not delivered|\bdeferred\b",
    re.I)
_REQ_ROW_ID = re.compile(r"^(FR|NFR)-\d+")
_APPENDIX_A = re.compile(r"^##\s+Appendix\s+A\b", re.M)
_STATUS_ENUM = re.compile(r'"status":\s*"ok",\s*//\s*([a-z][a-z |\-]*)')
_REQUIRED_UR_FIELDS = ("id", "requirement", "response_fields", "reason", "owner",
                       "clears_when", "expires")


_ACTION_HEAD = re.compile(r'"([A-Za-z_][A-Za-z0-9_]*)"\s*:\s*\{')


def _action_slices(text: str):
    """Every (action name, start, end) block in a flow file, by brace matching.

    Deliberately NOT a structural walk of `properties.definition.actions`. The OK document here
    is `Compose_response_body`, nested inside a Scope inside a condition, and the first
    implementation's recursive walk did not reach it — it reported 0 null response keys against
    a corpus with 8, which is precisely the "0 findings against a corpus you know contains an
    instance" tell. Brace matching cannot miss a nesting shape it has not been taught.
    """
    for match in _ACTION_HEAD.finditer(text):
        depth, index, limit = 0, match.end() - 1, len(text)
        while index < limit:
            char = text[index]
            if char == '"':                                    # skip strings, honouring escapes
                index += 1
                while index < limit and text[index] != '"':
                    index += 2 if text[index] == "\\" else 1
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    yield match.group(1), match.end() - 1, index + 1
                    break
            index += 1


def flow_null_response_keys(solution: Path) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """Response keys composed as a literal null, split by whether the document is the OK one.

    Returns ({key: ["flow → action", …]} for the OK path, {key: [...]} excluded as non-ok) —
    EVERY composing action, not the first one found.

    WHY EVERY ONE (`IMP-0461`). This returned `{key: "flow → action"}` and set it with
    `setdefault`, so a key composed as null in several actions reported one. `averageAmountRequested`
    is null in THREE — `Compose_breaktype_rows` (×5, one per break type), `Compose_breaktype_total`
    and `Compose_exceptional_funding_summary` — and those belong to two DIFFERENT requirements
    (`FR-060`'s and `FR-059`'s), carried by two different register entries. Collapsed to one key,
    one acquittal covered all seven occurrences and the summary line said so about none of them.
    The multiplicity is now carried here and printed by `main()`, because a reader who cannot see
    that one acquittal covers three actions cannot see the hole either.

    IN SCOPE IFF THE ACTION COMPOSES `"status":"ok"` — a value test, not a name test. This flow
    builds FIVE documents (`Compose_response_body`, plus the no-open-round, ambiguous-round,
    truncated and error documents), and a non-ok document legitimately carries a SUBSET of the
    key set, so nulling everything in one is correct behaviour that must never be reported
    (IMP-0454). The first implementation matched action NAMES against `error|pending|fail` and
    would have treated three of the four non-ok documents as the OK one.

    A STATUS-FREE COMPOSE IS A FRAGMENT, NOT A NON-OK DOCUMENT — and getting that wrong made
    this gate reassure wrongly (2026-08-28, `wbs:6.9`, development-agent). When FR-059/FR-060
    were built, the response document stopped being composed by one action: `Compose_response_body`
    now interpolates `outputs('Compose_breaktype_rows')`, `outputs('Compose_breaktype_total')` and
    `outputs('Compose_exceptional_funding_summary')`, each of which carries the four money-average
    `null`s that are still genuinely undelivered. Those helpers compose no `"status"` literal, so
    `statuses` was the EMPTY SET, which is `!= {"ok"}`, so every one of them was filed as non-ok
    and silently ignored — the gate reported `breakTypeProfile` as delivered while three of
    FR-060's four measures were null one action away. The fix attributes a status-free fragment to
    the document(s) that CONSUME it, transitively, and it makes this gate strictly STRICTER: it
    now sees nulls it previously could not, and it fails on an unregistered null inside a helper
    exactly as it always did on one inside the OK document. `Compose_error_document` and
    `Compose_no_open_round_document` are unaffected — they compose their own non-ok status, so
    they are still classified directly and never inherit.
    """
    ok_keys: dict[str, list[str]] = {}
    non_ok: dict[str, list[str]] = {}
    for path in sorted((solution / "Workflows").glob("*.json")):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        blocks = list(_action_slices(text))

        # ── Which actions compose an OK document, directly or by feeding one a fragment?
        # An action's own status set classifies it when it HAS one. A status-free action is
        # unclassified and inherits from its consumers, so resolve consumption first.
        own_status = {}
        for name, start, end in blocks:
            own_status[name] = set(_STATUS_LITERAL.findall(text[start:end]))

        # name -> set of action names that interpolate outputs('name')
        consumers: dict[str, set[str]] = {}
        for name, start, end in blocks:
            for ref in re.findall(r"outputs\('([A-Za-z0-9_]+)'\)", text[start:end]):
                if ref != name:
                    consumers.setdefault(ref, set()).add(name)

        def feeds_ok(name: str, seen: frozenset[str] = frozenset()) -> bool:
            """True if this action's content reaches a document composing status ok."""
            if name in seen:                      # a reference cycle must not recurse forever
                return False
            statuses = own_status.get(name) or set()
            if statuses:                          # it declares its own nature; no inheritance
                return statuses == {"ok"}
            return any(feeds_ok(c, seen | {name})
                       for c in consumers.get(name, ()))

        for match in _NULL_KEY.finditer(text):
            key, at = match.group(1), match.start()
            # The NARROWEST enclosing block is the composing action. Without this the outermost
            # `"properties": {` block encloses every key, its status set is every status the
            # flow can emit, and all ten keys are misfiled as non-ok.
            enclosing = [b for b in blocks if b[1] <= at < b[2]]
            if not enclosing:
                continue
            name, start, end = min(enclosing, key=lambda b: b[2] - b[1])
            target = ok_keys if feeds_ok(name) else non_ok
            where = f"{path.name} → {name}"
            bucket = target.setdefault(key, [])
            if where not in bucket:            # one action, not one per null occurrence in it
                bucket.append(where)
    return ({k: sorted(v) for k, v in ok_keys.items() if k not in non_ok},
            {k: sorted(v) for k, v in non_ok.items()})


def appendix_a_requirement_rows(text: str) -> list[str]:
    """Every Appendix A table row whose FIRST cell is a requirement id.

    An `OQ-nnn` row is an open QUESTION, not a coverage claim, and a row naming no requirement
    is not what acceptance reads — both are excluded, and both were measured false positives.
    """
    match = _APPENDIX_A.search(text)
    if not match:
        return []
    rows = []
    for line in text[match.end():].splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if cells and _REQ_ROW_ID.search(re.sub(r"[*~`\s]", "", cells[0])):
            rows.append(line)
    return rows


def status_values_produced(solution: Path, app_src: Path) -> tuple[dict[str, str],
                                                                   dict[str, str]]:
    """Status values the FLOW composes and, separately, ones the APP synthesises.

    Test fixtures are excluded from both: they deliberately invent statuses to prove the app
    tolerates unknown ones — the naive version of this check fired on `some-new-failure-mode`,
    the fixture written to demonstrate that tolerance. 5 findings, 2 true, 3 false before this
    exclusion.

    RETURNS TWO SETS, NOT ONE (`IMP-0481`). The union used to be the only thing this returned,
    and it made assertion (e) ask one question of two populations that are not the same kind of
    thing: the response contract's enumeration describes the **response body**, which only the
    flow composes, while the app's own in-flight states never travel in one. Measured against the
    real tree, the union form scored **3 findings, 2 true, 1 false** — the false positive being
    `pending`, synthesised by `roundStatistics.ts` while polling. Splitting the return makes it
    leave BY CONSTRUCTION rather than by exemption, which is why no baseline entry excuses it.
    """
    flow_produced: dict[str, str] = {}
    app_produced: dict[str, str] = {}
    for path in sorted((solution / "Workflows").glob("*.json")):
        for value in _STATUS_LITERAL.findall(path.read_text(encoding="utf-8")):
            flow_produced.setdefault(value, path.name)
    if app_src.is_dir():
        for path in sorted(app_src.rglob("*.ts*")):
            if ".test." in path.name or "__tests__" in str(path):
                continue
            for value in _APP_STATUS.findall(path.read_text(encoding="utf-8", errors="ignore")):
                app_produced.setdefault(value, str(path.relative_to(app_src)))
    return flow_produced, app_produced


def load_undelivered_requirements(path: Path,
                                  today: _dt.date) -> tuple[list[dict], list[Violation]]:
    """The `undelivered_requirements` register, validated exactly as `deferrals` is.

    Until this gate read it, NO file under scripts/ mentioned this key — the register said so
    itself — so three owned entries carrying a dated expiry would have expired in silence
    (IMP-0455).
    """
    if not path.is_file():
        return [], []
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return [], []          # (a)'s loader already reports an unparseable file
    entries = doc.get("undelivered_requirements")
    if entries is None:
        return [], []          # an absent register is a legitimate state: nothing is undelivered
    if not isinstance(entries, list):
        return [], [Violation(f"{path} → undelivered_requirements", "is not an array",
                              "give it an array, even an empty one")]
    valid: list[dict] = []
    problems: list[Violation] = []
    for index, raw in enumerate(entries):
        if not isinstance(raw, dict):
            problems.append(Violation(f"{path} → undelivered_requirements[{index}]",
                                      "is not an object"))
            continue
        ident = raw.get("id") or f"undelivered_requirements[{index}]"
        missing = [f for f in _REQUIRED_UR_FIELDS
                   if not (raw.get(f) if isinstance(raw.get(f), list)
                           else str(raw.get(f) or "").strip())]
        if missing:
            problems.append(Violation(
                f"{path} → {ident}", f"is missing {', '.join(missing)}",
                "every entry carries an owner, a reason, a clearing action and a dated expiry. "
                "An unowned or undated entry is indistinguishable from a requirement nobody has "
                "noticed is undelivered — the same rule as `deferrals` above"))
            continue
        expires = str(raw.get("expires")).strip()
        try:
            when = _dt.date.fromisoformat(expires)
        except ValueError:
            problems.append(Violation(f"{path} → {ident}",
                                      f"`expires` is `{expires}`, not an ISO date (YYYY-MM-DD)",
                                      "a date this gate cannot compare is not a date"))
            continue
        if when < today:
            problems.append(Violation(
                f"{path} → {ident}",
                f"EXPIRED on {expires} — {raw.get('requirement')} is still undelivered",
                f"build it, withdraw the requirement, or re-date the entry with a reason. "
                f"Owner: {raw.get('owner')}. Clears when: {raw.get('clears_when')}"))
            continue
        valid.append(raw)
    return valid, problems


def check_response_contract(design_docs: list[Path], solution: Path, app_src: Path,
                            register_path: Path, today: _dt.date,
                            baseline) -> tuple[list[Violation], dict]:
    """(d) null response keys are declared, (e) status values are enumerated, (f) the register
    is valid and not stale."""
    violations: list[Violation] = []
    ok_nulls, non_ok = flow_null_response_keys(solution)
    register, register_problems = load_undelivered_requirements(register_path, today)
    violations += register_problems

    registered: dict[str, str] = {}
    for entry in register:
        for field in entry.get("response_fields") or []:
            registered[str(field)] = str(entry.get("id"))

    rows: list[str] = []
    docs_with_appendix = 0
    declared_status: list[str] = []
    status_doc: Path | None = None
    for directory in design_docs:
        for path in sorted(directory.rglob("*.md")) if directory.is_dir() else []:
            text = path.read_text(encoding="utf-8", errors="ignore")
            found = appendix_a_requirement_rows(text)
            if found:
                docs_with_appendix += 1
                rows += found
            enum = _STATUS_ENUM.search(text)
            if enum and status_doc is None:
                status_doc = path
                declared_status = [s.strip() for s in enum.group(1).split("|") if s.strip()]

    # ── Structural floor. A parser that stops matching finds nothing, and nothing must never
    # read as clean (IMP-0007). Only asserted when there is something to check.
    if ok_nulls and not rows:
        violations.append(Violation(
            "Appendix A requirement traceability",
            f"{len(ok_nulls)} response key(s) are composed as a literal null and NO design "
            f"document yielded a single Appendix A requirement row",
            "assertion (d) has no input, and a missing input is a FAILURE, not a pass. Either "
            "the Appendix A heading or its row shape changed — fix the parser, not this floor"))

    # ── (d) EVERY NULL RESPONSE KEY IS DECLARED SOMEWHERE ──
    acquitted: dict[str, str] = {}
    unaccounted: dict[str, str] = {}
    for key in sorted(ok_nulls):
        if key in registered:
            acquitted[key] = f"register {registered[key]}"
            continue
        hosts = [r for r in rows if re.search(r"\b" + re.escape(key) + r"\b", r)]
        if not hosts:
            # ── NOT A FAILURE, AND NOT SILENT EITHER (`IMP-0461`) ─────────────────────────
            # `IMP-0461` asked for this branch to FAIL: a null key that neither the register nor
            # any Appendix A row names is, on the face of it, a null nobody has written down.
            # MEASURED AGAINST THIS CORPUS IT IS WRONG — 3 findings, 0 true positives.
            # `highHoursCareProportion`, `lowLifeSatisfactionProportion` and
            # `unableToTakeBreakProportion` are all three declared, COLLECTIVELY, by FR-062's own
            # Appendix A row ("the three proportions await OQ-039") and again in the TAD's response
            # -contract block, which annotates them "null until its rev_setting threshold is
            # seeded". None is named individually, which is the only reason this matcher misses
            # them — and detecting a collective declaration means matching a PHRASE, the instrument
            # this repository has now measured at 48%-100% false five times over
            # (`agents/improvement-agent.md`, "And run it against the REAL CORPUS").
            #
            # So the intent survives and the enforcement does not: the bucket is REPORTED BY NAME
            # on every verdict instead. A classifier's third branch that prints nothing is exactly
            # how assertion (d) came to read `breakTypeProfile` as delivered
            # (`gate-reassures-wrongly`, x23) — the fix for that shape is to make the ignored set
            # visible, not to guess at it.
            unaccounted[key] = ", ".join(ok_nulls[key])
            continue
        if all(_NOT_DELIVERED.search(host) for host in hosts):
            acquitted[key] = "Appendix A marker"
            continue
        violations.append(Violation(
            f"response contract → {key}",
            f"composed as a literal `null` by {', '.join(ok_nulls[key])}, and the Appendix A "
            f"requirement "
            f"row naming it reads as DELIVERED",
            f"either mark it in that row the way FR-061 marks `ethnicGroupDistribution` "
            f"(\"always `null`\"), or — better, because it carries an owner and a date — add an "
            f"`undelivered_requirements` entry naming `{key}` in `response_fields` in "
            f"{register_path}. A traceability row reading as covered is what puts a phase "
            f"acceptance above its evidence (C-COM-006)"))

    # ── (e) THE PRODUCED AND ENUMERATED STATUS SETS AGREE, BY MEMBERSHIP, BOTH WAYS ──
    #
    # `IMP-0481`. This compared the two populations by MEMBERSHIP in one direction only, so an
    # enumerated value that NOTHING produces — a dead diagnostic — read as clean. The TAD
    # enumerates `threshold-unset`; no flow and no app file emits it, and the V5 key-set
    # assertion written against that enumeration therefore waits forever for a value that cannot
    # arrive. Both directions are now asked, and reported SEPARATELY, because the two are
    # different defects with different owners:
    #
    #   * a FLOW-produced value absent from the enumeration  → the enumeration is short (breach)
    #   * an ENUMERATED value nothing produces at all        → the enumeration is dead (debt)
    #
    # The first question is asked of the FLOW set alone and the second of the UNION, and that
    # asymmetry is the measurement's doing, not a preference: the enumeration describes the
    # response BODY, which only the flow composes, while an app-synthesised state such as
    # `pending` is real, correct and never travels in one. See `status_values_produced`.
    flow_produced, app_produced = status_values_produced(solution, app_src)
    produced = {**app_produced, **flow_produced}
    missing_status: dict[str, str] = {}
    dead_status: dict[str, str] = {}
    if declared_status:
        # ── (e1) a value the FLOW composes must be enumerated ──
        for value in sorted(flow_produced):
            if value in declared_status:
                continue
            key = f"status:{value}"
            if baseline is not None and baseline.excuses(key):
                missing_status[value] = (f"composed by {flow_produced[value]}, not enumerated"
                                         f"{baseline.cite(key)}")
                continue
            violations.append(Violation(
                f"response contract → status `{value}`",
                f"composed by {flow_produced[value]} and absent from the response contract's "
                f"enumeration ({', '.join(declared_status)})",
                f"add `{value}` to that enumeration in "
                f"{status_doc.name if status_doc else 'the response contract'}, marking whether "
                f"it is flow-authored or app-synthesised. An enumeration short of what the "
                f"system emits makes a key-set assertion read a legitimate divergence as a "
                f"failure (IMP-0454)"))
        # ── (e2) an enumerated value NOTHING produces is a dead diagnostic ──
        #
        # GUARDED ON A NON-EMPTY FLOW SET, and this is the structural floor above read in the
        # other direction. That floor says a parser that has stopped matching finds nothing, and
        # nothing must never read as CLEAN. Its converse binds here: when no flow composes a
        # single status literal, the producing side was not found, and "nothing produces this"
        # is then a statement about the gate's input rather than about the system. Unguarded,
        # (e2) reports EVERY enumerated value the moment the Workflows/ glob comes back empty —
        # measured, on the fixture with no flow at all, as a finding against `ok` itself.
        if flow_produced:
            for value in sorted(declared_status):
                if value in produced:
                    continue
                key = f"status-unproduced:{value}"
                if baseline is not None and baseline.excuses(key):
                    dead_status[value] = (f"enumerated, produced by nothing"
                                          f"{baseline.cite(key)}")
                    continue
                violations.append(Violation(
                    f"response contract → status `{value}`",
                    f"is enumerated in "
                    f"{status_doc.name if status_doc else 'the response contract'} and is "
                    f"composed by NO flow and synthesised by NO app file — nothing in this "
                    f"repository can ever emit it",
                    f"either build the path that emits `{value}`, or strike it from the "
                    f"enumeration. A status a consumer is told to handle and that nothing "
                    f"produces is a diagnostic that can only ever mislead: a V5 key-set "
                    f"assertion written against this enumeration waits for a value that cannot "
                    f"arrive (IMP-0481)"))

    # ── (f) THE REGISTER IS NOT A DEAD PROMISE ──
    for entry in register:
        for field in entry.get("response_fields") or []:
            if str(field) not in ok_nulls:
                violations.append(Violation(
                    f"{register_path} → {entry.get('id')}",
                    f"names response field `{field}`, which is NOT composed as a literal null "
                    f"in any flow's OK document",
                    "it shipped, or it was renamed, or the requirement changed. Delete the "
                    "entry — a register that accumulates satisfied entries becomes a blanket "
                    "nobody reads, which is `deferrals`' own rule one key above"))

    return violations, {
        "response_nulls": len(ok_nulls),
        "response_nulls_non_ok": len(non_ok),
        "response_acquitted": acquitted,
        "response_unaccounted": unaccounted,
        "response_null_actions": {k: len(v) for k, v in ok_nulls.items() if len(v) > 1},
        "register_entries": len(register),
        "status_produced": len(produced),
        "status_produced_flow": len(flow_produced),
        "status_produced_app": len(app_produced),
        "status_declared": len(declared_status),
        "status_baselined": len(missing_status),
        "status_dead_baselined": len(dead_status),
        # BY NAME, not just counted. `config/gate-baselines.json` promises that an entry
        # "suppresses the FAIL, never the report" — and until this key existed, this gate broke
        # that promise: a baselined status was silently dropped and the summary line said only
        # how many values were produced against how many enumerated. A suppression nobody can
        # see is the `gate-reassures-wrongly` shape the register exists to avoid (IMP-0481).
        "status_suppressed": {**missing_status, **dead_status},
        "appendix_a_rows": len(rows),
        "appendix_a_docs": docs_with_appendix,
    }


# ── The assertions ───────────────────────────────────────────────────────────

def run(tad: Path, solution: Path, deferrals_path: Path,
        today: _dt.date | None = None,
        design_docs: Path | list[Path] | None = None,
        app_src: Path | None = None,
        baseline=None) -> tuple[int, list[Violation], dict]:
    today = today or _dt.date.today()
    violations: list[Violation] = []
    stats: dict = {}

    if not tad.is_file():
        return 1, [Violation(str(tad), "TAD not found — a gate pointed at a missing target "
                                       "does not pass (IMP-0007)")], stats
    if not (solution / "Entities").is_dir():
        return 1, [Violation(str(solution), "no Entities/ directory under the solution root")], stats

    specs, stats, parse_problems = parse_section_31(tad.read_text(encoding="utf-8"))
    violations += parse_problems

    # ── Structural floor, asserted before any comparison ──
    floor_failed = False
    for key, (minimum, why) in _MINIMUMS.items():
        actual = stats.get(key, 0)
        if actual < minimum:
            floor_failed = True
            violations.append(Violation(
                f"TAD §3.1 parse ({tad})",
                f"yielded {key}={actual}, below the minimum of {minimum} — {why}",
                "this gate reads a markdown table, and a parser that has stopped matching "
                "finds nothing to report. Finding nothing is a FAILURE here, never an OK "
                "(gate-cannot-fail, x23). Fix the parser or the section, not this floor"))
    if floor_failed:
        return 1, violations, stats

    deferrals, deferral_problems = load_deferrals(deferrals_path, today)
    violations += deferral_problems

    # ── (a) EXISTENCE ──
    columns_by_table: dict[str, set[str] | None] = {}
    for table in stats["tables"]:
        columns_by_table[table] = entity_columns(solution, table)

    absent: list[Spec] = []
    deferred: list[Spec] = []
    for spec in sorted(specs, key=lambda s: (s.table, s.column)):
        present = columns_by_table.get(spec.table)
        if present is not None and spec.column in present:
            continue
        cover = next((d for d in deferrals if d.covers(spec)), None)
        if cover is not None:
            cover.used = True
            deferred.append(spec)
            continue
        absent.append(spec)
        table_state = ("the table itself is absent from source"
                       if present is None else "the table exists; the column does not")
        violations.append(Violation(
            f"{spec.table}.{spec.column}",
            f"named by TAD §3.1 (line {spec.line}) but absent from source — {table_state}",
            f"add the attribute to src/solutions/RevitaliseGrantAutomation/Entities/"
            f"{spec.table}/Entity.xml, or declare an owned, dated deferral in "
            f"{deferrals_path}"))

    # A deferral that covers nothing, or covers a column that now exists, is a dead promise.
    for deferral in deferrals:
        if deferral.used:
            continue
        violations.append(Violation(
            f"{deferrals_path} → {deferral.id}",
            f"defers nothing: no absent TAD §3.1 column on `{deferral.table}` matches it",
            "the columns shipped, or the TAD changed. Delete the entry — a deferral file "
            "that accumulates satisfied entries becomes a blanket nobody reads"))

    # ── (b) REACHABILITY ──
    read_tables, role_path = trustee_read_tables(solution)
    visible = [s for s in specs if s.trustee_visible]
    if read_tables is None:
        violations.append(Violation(
            str(role_path),
            "REV Trustee role not found, so no trustee-visible column can be shown reachable",
            "assertion (b) has no input; a missing input is a FAILURE, not a pass (IMP-0007)"))
    else:
        unreachable_tables: dict[str, list[Spec]] = {}
        for spec in visible:
            if spec.table in read_tables:
                continue
            if any(d.covers(spec) and d.all_columns for d in deferrals):
                continue  # whole table deferred; there is no table to grant a privilege on
            unreachable_tables.setdefault(spec.table, []).append(spec)
        for table, members in sorted(unreachable_tables.items()):
            names = ", ".join(sorted(s.column for s in members))
            violations.append(Violation(
                f"{role_path}",
                f"REV Trustee holds no `prvRead{table}`, but TAD §3.1 marks "
                f"{len(members)} column(s) on it trustee-visible: {names}",
                f"add <RolePrivilege name=\"prvRead{table}\" level=\"Global\" /> to the role, "
                f"or drop the trustee-visible marking in the TAD. Column security RELEASES a "
                f"column; it never GRANTS table access, so without the table privilege the "
                f"row does not come back at all and the marking is unimplementable (IMP-0159)"))
    # ── (c) DELIVERABLE-NOW PROSE CLAIMS, across every design document ──
    # Deliberately AFTER (a) and (b): those two read one document's §3.1 table, this one reads
    # every document's prose, and keeping them separate is what lets the floor above stay
    # calibrated to the parent TAD (residual 3 in the block above).
    claim_violations, claim_stats = check_deliverable_now_claims(
        design_docs if design_docs is not None else tad.parent, solution)
    violations += claim_violations

    # ── (d)(e)(f) THE RESPONSE CONTRACT ──
    # Last, and reading a different table of the same documents: (a)/(b) read §3.1's columns,
    # (c) reads deliverable-now prose, these read Appendix A's requirement rows, §3.3's status
    # enumeration and the undelivered_requirements register. Keeping them separate is what lets
    # the §3.1 floor above stay calibrated to the parent TAD.
    docs = design_docs if isinstance(design_docs, list) else [design_docs or tad.parent]
    contract_violations, contract_stats = check_response_contract(
        docs, solution,
        app_src or Path("src/code-apps/trustee-review-portal/src"),
        deferrals_path, today, baseline)
    violations += contract_violations

    stats.update({
        "absent": len(absent),
        "deferred": len(deferred),
        "checked_tables": len(stats["tables"]),
        "role_read_tables": sorted(read_tables) if read_tables else [],
        "visible": len(visible),
        "absent_list": [f"{s.table}.{s.column}" for s in absent],
        **claim_stats,
        **contract_stats,
    })
    return (1 if violations else 0), violations, stats


# ── Self-test ────────────────────────────────────────────────────────────────
# Fixtures are ASSEMBLED AT RUNTIME, never committed: a known-bad TAD or a known-bad deferral
# file at rest in the repository would be picked up by the real gate and break the thing it
# exists to protect (IMP-0024). The synthetic TAD is generated LARGE ENOUGH to clear the real
# _MINIMUMS, so the self-test exercises the shipped floor rather than a relaxed copy.

_FIXTURE_TABLES = [f"rev_t{i:02d}" for i in range(10)]


def _fixture_tad(*, include_section: bool = True, absent_column: bool = False,
                 visible_on_unread_table: bool = False) -> str:
    out = ["# Fixture TAD", "", "## 3. Data Model", ""]
    if include_section:
        out += ["### 3.1 Key attributes and the controls each carries", ""]
        for index, table in enumerate(_FIXTURE_TABLES):
            out += [f"**`{table}` — Tier 4**", "",
                    "| Attribute | Type | Classification | Control |",
                    "|---|---|---|---|"]
            for column in range(12):
                mark = ""
                if index == 0 and column < 3:
                    mark = "trustee-visible (FR-027)"
                if visible_on_unread_table and index == 9 and column == 0:
                    mark = "trustee-visible (FR-027)"
                out.append(f"| `{table}_c{column:02d}` | Text | Tier 3 | {mark} |")
            if absent_column and index == 0:
                out.append(f"| `{table}_gone` | Text | Tier 3 | never built |")
            out.append("")
    out += ["### 3.2 Provider classification", "", "prose", ""]
    return "\n".join(out)


def _fixture_solution(root: Path, *, read_tables: list[str]) -> Path:
    solution = root / "src" / "solutions" / "RevitaliseGrantAutomation"
    for table in _FIXTURE_TABLES:
        directory = solution / "Entities" / table
        directory.mkdir(parents=True, exist_ok=True)
        attributes = "".join(
            f'<attribute PhysicalName="{table}_c{c:02d}"><Type>nvarchar</Type></attribute>'
            for c in range(12))
        (directory / "Entity.xml").write_text(
            f'<?xml version="1.0" encoding="utf-8"?><Entity><Name>{table}</Name>'
            f"<EntityInfo><entity Name=\"{table}\"><attributes>{attributes}</attributes>"
            "</entity></EntityInfo></Entity>", encoding="utf-8")
    role = solution / "Roles" / "REV Trustee"
    role.mkdir(parents=True, exist_ok=True)
    privileges = "".join(f'<RolePrivilege name="prvRead{t}" level="Global" />'
                         for t in read_tables)
    (role / "REV Trustee.xml").write_text(
        '<?xml version="1.0" encoding="utf-8"?>'
        '<!-- a comment naming prvReadrev_applicant, which is not a privilege -->'
        f'<Role id="{{00000000-0000-4000-8000-000000000001}}" name="REV Trustee">'
        f"<RolePrivileges>{privileges}</RolePrivileges></Role>", encoding="utf-8")
    return solution


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _deferral_doc(entry: dict, undelivered: list[dict] | None = None) -> str:
    doc: dict = {"_purpose": "fixture", "deferrals": [entry]}
    if undelivered is not None:
        doc["undelivered_requirements"] = undelivered
    return json.dumps(doc, indent=2)


# ── (d)(e)(f) fixtures ───────────────────────────────────────────────────────
# The flow is built as REAL escaped-JSON-in-an-expression, because that is the only shape these
# keys ever appear in: the shipped flow composes its response document as a string expression,
# so `"applicationsPerDay":null` is `\"applicationsPerDay\":null` inside a Compose action. A
# fixture using plain JSON nulls would test a shape that does not occur.

def _fixture_flow(ok_nulls: list[str] = (), non_ok_nulls: list[str] = (),
                  fragment_nulls: list[str] = (), cyclic: bool = False) -> str:
    """A flow file with ONE level of escaping, exactly as the shipped flow has it.

    Written as raw text rather than through `json.dumps`, which escapes the backslashes a
    second time and yields `\\\\"key\\\\":null` — a shape that occurs nowhere and that the
    gate's regex correctly refuses to match. The first version of this fixture did that, and
    three cases reported 0 findings against a fixture built to contain one. That is the same
    "0 findings against a corpus you know contains an instance" tell the real corpus run is
    checked for, caught here by the fixtures themselves.

    `fragment_nulls` puts its keys in a STATUS-FREE helper Compose that the OK document
    interpolates — the shape that made this gate go blind (`IMP-0461`). A status-free action's
    status set is empty, which is `!= {"ok"}`, so before the fragment-attribution fix every
    such null was filed as a non-ok document and silently dropped. Any case using this
    parameter FAILS TO FAIL on the pre-fix implementation, which is what makes it a real
    negative test for that fix and not a restatement of it.

    `cyclic` additionally makes two fragments interpolate each other, so the transitive walk
    is exercised against a reference cycle. A cycle cannot occur in a valid definition, but a
    gate that hangs on a malformed one has stopped being a gate.
    """
    def body(status: str, keys) -> str:
        pairs = "".join(f',\\"{k}\\":null' for k in keys)
        return f"concat('{{\\\"status\\\":\\\"{status}\\\"{pairs}}}')"

    def fragment_body(keys, extra_ref: str = "") -> str:
        pairs = "".join(f'\\"{k}\\":null,' for k in keys)
        ref = f",outputs('{extra_ref}')" if extra_ref else ""
        return f"concat('{{{pairs}\\\"end\\\":0}}'{ref})"

    ok_body = body("ok", ok_nulls)
    if fragment_nulls or cyclic:
        # The OK document interpolates the fragment by name, which is the edge the walk follows.
        ok_body = ok_body[:-1] + ",outputs('Compose_fragment')" + ")"

    fragment = ""
    if fragment_nulls or cyclic:
        fragment = (
            f'      "Compose_fragment": {{ "type": "Compose", "inputs": '
            f'"{fragment_body(fragment_nulls, "Compose_fragment_two" if cyclic else "")}" }},\n')
        if cyclic:
            fragment += (
                '      "Compose_fragment_two": { "type": "Compose", "inputs": '
                f'"{fragment_body([], "Compose_fragment")}" }},\n')

    return (
        '{\n'
        '  "properties": { "definition": { "actions": {\n'
        '    "Compute_statistics": { "type": "Scope", "actions": {\n'
        f'{fragment}'
        f'      "Compose_response_body": {{ "type": "Compose", "inputs": "{ok_body}" }}\n'
        '    } },\n'
        f'    "Compose_error_document": {{ "type": "Compose", "inputs": "{body("error", non_ok_nulls)}" }}\n'
        '  } } }\n'
        '}\n')


def _contract_doc(rows: list[str], enum_values: list[str]) -> str:
    enum = " | ".join(enum_values)
    row_text = "\n".join(rows)
    return f"""# Response contract fixture

### 3.3 The response document

```jsonc
{{
  "status": "ok",            // {enum}
}}
```

## Appendix A — Requirement traceability

| SDD requirement | Element | WBS |
|---|---|---|
{row_text}
"""


_UR_ENTRY = {
    "id": "UR-FIX", "requirement": "FR-999 — PARTIAL", "response_fields": ["fixtureMetric"],
    "reason": "fixture", "owner": "Fixture Owner", "clears_when": "the fixture computes it",
    "expires": "2026-12-31",
}


# A DELTA design document — the file type that, before improvement review 29 change 1, no gate
# read at all. `{items}` is the deliverable-now list under test.
_DELTA_DOC = """# Delta TAD fixture

## 3. Data Model

### 3.2 What ships, and the mechanism that closes the gap

**Deliverable now, with no schema change and no security change:** {items}

Some following prose that is not part of the claim.
"""

_GOOD_DEFERRAL = {
    "id": "TD-FIX", "table": _FIXTURE_TABLES[0], "columns": [f"{_FIXTURE_TABLES[0]}_gone"],
    "reason": "fixture", "owner": "Fixture Owner", "clears_when": "the fixture is built",
    "expires": "2099-01-01",
}


def selftest() -> int:
    today = _dt.date(2026, 8, 21)
    cases: list[tuple[str, bool]] = []
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)

        def case(name: str, *, tad: str, read_tables: list[str],
                 deferral: str | None, expect_fail: bool,
                 delta_doc: str | None = None,
                 flow: str | None = None, contract_doc: str | None = None,
                 app_status: str | None = None) -> None:
            root = base / name
            solution = _fixture_solution(root, read_tables=read_tables)
            # Design documents live in their own directory so assertion (c)'s corpus is
            # explicit: `tad.md` plus, when a case supplies one, a sibling DELTA document.
            docs = root / "docs"
            tad_path = _write(docs / "tad.md", tad)
            if delta_doc is not None:
                _write(docs / "delta-architecture.md", delta_doc)
            if contract_doc is not None:
                _write(docs / "contract-architecture.md", contract_doc)
            if flow is not None:
                _write(solution / "Workflows" / "REVFixtureFlow.json", flow)
            deferrals_path = root / "tad-deferrals.json"
            if deferral is not None:
                _write(deferrals_path, deferral)
            # app_src MUST point inside the fixture. Left at its production default the
            # selftest reads the REAL code app's status values, and a fixture contaminated by
            # live source is not a fixture (IMP-0024).
            app_src = root / "app"
            if app_status is not None:
                _write(app_src / "fixture.ts", app_status)
            code, violations, _ = run(tad_path, solution, deferrals_path, today=today,
                                      design_docs=docs, app_src=app_src)
            ok = (code != 0) if expect_fail else (code == 0)
            print(f"  {'OK' if ok else 'DID NOT BEHAVE':16} {name} → exit {code}, "
                  f"{len(violations)} violation(s)")
            if not ok:
                for violation in violations:
                    print(f"                   {violation}")
            cases.append((name, ok))

        every = list(_FIXTURE_TABLES)

        case("zero-rows-section-3.1-removed",
             tad=_fixture_tad(include_section=False), read_tables=every,
             deferral=None, expect_fail=True)
        case("column-named-by-the-TAD-is-absent",
             tad=_fixture_tad(absent_column=True), read_tables=every,
             deferral=None, expect_fail=True)
        case("deferral-with-no-owner",
             tad=_fixture_tad(absent_column=True), read_tables=every,
             deferral=_deferral_doc({**_GOOD_DEFERRAL, "owner": ""}), expect_fail=True)
        case("deferral-with-no-date",
             tad=_fixture_tad(absent_column=True), read_tables=every,
             deferral=_deferral_doc({**_GOOD_DEFERRAL, "expires": ""}), expect_fail=True)
        case("deferral-with-an-expired-date",
             tad=_fixture_tad(absent_column=True), read_tables=every,
             deferral=_deferral_doc({**_GOOD_DEFERRAL, "expires": "2026-08-20"}),
             expect_fail=True)
        case("deferral-that-defers-nothing",
             tad=_fixture_tad(), read_tables=every,
             deferral=_deferral_doc(dict(_GOOD_DEFERRAL)), expect_fail=True)
        case("trustee-visible-column-on-a-table-the-role-cannot-read",
             tad=_fixture_tad(visible_on_unread_table=True),
             read_tables=every[:-1], deferral=None, expect_fail=True)
        case("trustee-role-file-missing",
             tad=_fixture_tad(), read_tables=[], deferral=None, expect_fail=True)
        # ── (c) DELIVERABLE-NOW PROSE CLAIMS. Each fixture lives in a DELTA document beside
        # the parent, which is the source axis: before this change nothing read that file.
        good_col = f"{_FIXTURE_TABLES[0]}_c00"

        case("delta-doc-promises-an-item-naming-no-column",
             tad=_fixture_tad(), read_tables=every, deferral=None, expect_fail=True,
             delta_doc=_DELTA_DOC.format(items="preferred dates"))
        case("delta-doc-promises-an-item-naming-a-column-that-does-not-exist",
             tad=_fixture_tad(), read_tables=every, deferral=None, expect_fail=True,
             delta_doc=_DELTA_DOC.format(items="holiday window (`rev_t00_never_built`)"))
        # THE ONE THAT MATTERS MOST: a list where SOME items resolve. An identifier-resolving
        # check alone passes this, because the only identifier present is real — and the
        # unnamed item beside it is the actual defect (IMP-0326).
        case("delta-doc-mixes-a-resolvable-item-with-an-unnamed-one",
             tad=_fixture_tad(), read_tables=every, deferral=None, expect_fail=True,
             delta_doc=_DELTA_DOC.format(
                 items=f"total funding (`{good_col}`), and preferred dates")),
        # ── (d)(e)(f) THE RESPONSE CONTRACT ──
        # Every case below fails against the CORPUS nowhere, because the corpus is now clean on
        # (d) and (f) — the concurrent dispatch declared the shortfall in two places while this
        # review was being measured. So these fixtures are the ONLY can-it-fail proof those two
        # assertions have, which is exactly why they are here (review 38, §6a).
        _ROW_UNDECLARED = "| FR-999 | Response `fixtureMetric` | 6.9 |"
        _ROW_DECLARED = "| FR-999 | Response `fixtureMetric` — **always `null`** | 6.9 |"
        # Includes `error`, because _fixture_flow ALWAYS builds a Compose_error_document — a
        # contract fixture must enumerate what its own flow fixture produces, or every case
        # using it fails on assertion (e) for a reason unrelated to what it is testing.
        # EXACTLY what `_fixture_flow` composes — `ok` and `error`, and nothing else. It used to
        # read ["ok", "no-open-round", "truncated", "error"], two of which no fixture flow has
        # ever emitted, and assertion (e2) is what surfaced that: the shared contract fixture was
        # itself an internally inconsistent document of precisely the kind (e2) exists to catch.
        # Adding the missing statuses to the fixture FLOW was the alternative and was rejected —
        # it would have made every unrelated case carry two more status literals to keep one
        # assertion quiet (IMP-0481).
        _FIVE = ["ok", "error"]

        case("null-response-key-whose-Appendix-A-row-reads-as-DELIVERED",
             tad=_fixture_tad(), read_tables=every, deferral=None, expect_fail=True,
             flow=_fixture_flow(ok_nulls=["fixtureMetric"]),
             contract_doc=_contract_doc([_ROW_UNDECLARED], _FIVE))

        # ── (d) THE STATUS-FREE FRAGMENT. `IMP-0461`: when the OK document stopped being one
        # action and started interpolating helper Composes, every null inside those helpers
        # became invisible — their status set is empty, which is `!= {"ok"}`, so they were
        # filed as non-ok documents and dropped. All three cases below FAIL TO FAIL on the
        # pre-fix implementation, which is the only thing that makes them a negative test for
        # the fix rather than a description of it (`C-TECH-057`).
        case("null-in-a-status-free-fragment-the-OK-document-consumes",
             tad=_fixture_tad(), read_tables=every, deferral=None, expect_fail=True,
             flow=_fixture_flow(fragment_nulls=["fixtureMetric"]),
             contract_doc=_contract_doc([_ROW_UNDECLARED], _FIVE))
        case("VALID-a-fragment-null-whose-Appendix-A-row-declares-it-must-not-fire",
             tad=_fixture_tad(), read_tables=every, deferral=None, expect_fail=False,
             flow=_fixture_flow(fragment_nulls=["fixtureMetric"]),
             contract_doc=_contract_doc([_ROW_DECLARED], _FIVE))
        case("VALID-a-reference-cycle-between-fragments-must-terminate-not-hang",
             tad=_fixture_tad(), read_tables=every, deferral=None, expect_fail=False,
             flow=_fixture_flow(cyclic=True),
             contract_doc=_contract_doc([_ROW_DECLARED], _FIVE))
        # (e1) The flow composes `error`; the enumeration lists only `ok`. Enumerating just the
        # one value keeps this case single-caused — with the old ["ok", "no-open-round"] it
        # would now fail for TWO reasons and still print one green line.
        case("status-value-the-flow-composes-and-the-contract-does-not-enumerate",
             tad=_fixture_tad(), read_tables=every, deferral=None, expect_fail=True,
             flow=_fixture_flow(ok_nulls=[]),
             contract_doc=_contract_doc([_ROW_DECLARED], ["ok"]))
        # (e2) THE NEGATIVE FIXTURE FOR THE DEAD-DIAGNOSTIC DIRECTION. The flow composes `ok`
        # and `error`, the enumeration adds `threshold-unset`, and nothing anywhere emits it —
        # the real corpus's own finding, reduced to a fixture.
        case("status-value-ENUMERATED-that-nothing-produces-is-a-dead-diagnostic",
             tad=_fixture_tad(), read_tables=every, deferral=None, expect_fail=True,
             flow=_fixture_flow(ok_nulls=[]),
             contract_doc=_contract_doc([_ROW_DECLARED], ["ok", "error", "threshold-unset"]))
        # INVERTED BY CHANGE 2, and it was passing for the WRONG REASON before that. An
        # app-synthesised status is a real in-flight state that never travels in a response
        # body, so it is NOT required to appear in the response contract's enumeration — that
        # is the `pending` false positive the corpus measurement removed. The case previously
        # asserted the opposite and still went green only because, with `flow=None`, (e2) fired
        # on `ok` instead. A fixture that passes for a reason other than the one it names is how
        # a plausible design hides a real defect (IMP-0319).
        case("VALID-a-status-the-APP-synthesises-need-not-be-enumerated",
             tad=_fixture_tad(), read_tables=every, deferral=None, expect_fail=False,
             flow=_fixture_flow(ok_nulls=[]), contract_doc=_contract_doc([_ROW_DECLARED], _FIVE),
             app_status="const PENDING = { status: 'pending' };")
        case("register-entry-with-no-owner",
             tad=_fixture_tad(absent_column=True), read_tables=every, expect_fail=True,
             deferral=_deferral_doc(dict(_GOOD_DEFERRAL),
                                    [{**_UR_ENTRY, "owner": ""}]),
             flow=_fixture_flow(ok_nulls=["fixtureMetric"]),
             contract_doc=_contract_doc([_ROW_UNDECLARED], _FIVE))
        case("register-entry-with-an-expired-date",
             tad=_fixture_tad(absent_column=True), read_tables=every, expect_fail=True,
             deferral=_deferral_doc(dict(_GOOD_DEFERRAL),
                                    [{**_UR_ENTRY, "expires": "2026-08-20"}]),
             flow=_fixture_flow(ok_nulls=["fixtureMetric"]),
             contract_doc=_contract_doc([_ROW_UNDECLARED], _FIVE))
        case("register-entry-that-is-a-DEAD-PROMISE-its-field-is-no-longer-null",
             tad=_fixture_tad(absent_column=True), read_tables=every, expect_fail=True,
             deferral=_deferral_doc(dict(_GOOD_DEFERRAL), [dict(_UR_ENTRY)]),
             flow=_fixture_flow(ok_nulls=[]),
             contract_doc=_contract_doc([_ROW_DECLARED], _FIVE))
        # THE FLOOR: nulls exist and NO Appendix A row parsed. A markdown parser that has
        # stopped matching finds nothing, and nothing must never read as clean (IMP-0007).
        case("nulls-exist-but-no-Appendix-A-row-parses-at-all",
             tad=_fixture_tad(), read_tables=every, deferral=None, expect_fail=True,
             flow=_fixture_flow(ok_nulls=["fixtureMetric"]),
             contract_doc="# No appendix here\n\nJust prose.\n")
        # ── (d)(e)(f) VALID controls. Each is the same fixture with the defect declared. ──
        case("VALID-null-key-acquitted-by-an-Appendix-A-marker-must-pass",
             tad=_fixture_tad(), read_tables=every, deferral=None, expect_fail=False,
             flow=_fixture_flow(ok_nulls=["fixtureMetric"]),
             contract_doc=_contract_doc([_ROW_DECLARED], _FIVE))
        case("VALID-null-key-acquitted-by-an-owned-dated-register-entry-must-pass",
             tad=_fixture_tad(absent_column=True), read_tables=every, expect_fail=False,
             deferral=_deferral_doc(dict(_GOOD_DEFERRAL), [dict(_UR_ENTRY)]),
             flow=_fixture_flow(ok_nulls=["fixtureMetric"]),
             contract_doc=_contract_doc([_ROW_UNDECLARED], _FIVE))
        # A non-ok document nulling EVERYTHING is correct behaviour, never a finding: it
        # carries a subset of the key set by design (IMP-0454).
        case("VALID-a-non-ok-document-nulling-everything-must-pass",
             tad=_fixture_tad(), read_tables=every, deferral=None, expect_fail=False,
             flow=_fixture_flow(ok_nulls=[], non_ok_nulls=["fixtureMetric", "metrics"]),
             contract_doc=_contract_doc([_ROW_UNDECLARED], ["ok", "error"]))
        # A test file inventing a status must NOT fire — it is the fixture that proves the app
        # tolerates unknown values. Measured 3 false positives before this exclusion.
        case("VALID-a-status-invented-only-in-a-TEST-file-must-pass",
             tad=_fixture_tad(), read_tables=every, deferral=None, expect_fail=False,
             flow=None, contract_doc=_contract_doc([], ["ok"]),
             app_status=None)

        case("VALID-must-pass",
             tad=_fixture_tad(), read_tables=every, deferral=None, expect_fail=False)
        case("VALID-with-an-owned-dated-deferral-must-pass",
             tad=_fixture_tad(absent_column=True), read_tables=every,
             deferral=_deferral_doc(dict(_GOOD_DEFERRAL)), expect_fail=False)
        # Every item names a real column: the claim is checkable and checks out.
        case("VALID-delta-doc-where-every-item-names-a-real-column-must-pass",
             tad=_fixture_tad(), read_tables=every, deferral=None, expect_fail=False,
             delta_doc=_DELTA_DOC.format(
                 items=f"break type (`{good_col}`), and the care pair "
                       f"(`{_FIXTURE_TABLES[0]}_c01` + `{_FIXTURE_TABLES[0]}_c02`)"))
        # THE OVER-FIRING CONTROLS, and they are why the cue is a bolded lead-in ending in a
        # colon. All four of these phrasings exist in the real corpus and NONE is a
        # deliverables list; a looser cue fires on every one of them (gate-fires-on-nothing).
        case("VALID-a-heading-mentioning-no-schema-change-must-not-fire",
             tad=_fixture_tad(), read_tables=every, deferral=None, expect_fail=False,
             delta_doc="# Delta\n\n### 3.1 Existing columns this binds — no schema change\n\n"
                       "| Attribute | Type |\n|---|---|\n| `x` | Text |\n")
        case("VALID-prose-about-a-flow-change-must-not-fire",
             tad=_fixture_tad(), read_tables=every, deferral=None, expect_fail=False,
             delta_doc="# Delta\n\nThe extension is a change to one flow and to nothing else — "
                       "no schema change, no app change, no code-app change.\n")
        case("VALID-a-traceability-table-row-must-not-fire",
             tad=_fixture_tad(), read_tables=every, deferral=None, expect_fail=False,
             delta_doc="# Delta\n\n| Req | Where | WBS |\n|---|---|---|\n"
                       "| NFR-026 | §7 — full-width half deliverable now; brand half awaits "
                       "the ramp | 6.1 |\n")
        # NOT a virtue — RESIDUAL 1, pinned so it is a known limit rather than a surprise. The
        # same claim written without the bold lead-in is invisible to this check. Asserted
        # here so that if someone later widens the cue, this case tells them what they changed.
        case("VALID-RESIDUAL-an-unbolded-claim-is-invisible-and-that-is-documented",
             tad=_fixture_tad(), read_tables=every, deferral=None, expect_fail=False,
             delta_doc="# Delta\n\nDeliverable now, with no schema change: preferred dates.\n")

    failed = [name for name, ok in cases if not ok]
    if failed:
        print(f"\nverify-tad-coverage: SELFTEST FAILED — {', '.join(failed)}", file=sys.stderr)
        return 1
    bad = sum(1 for name, _ in cases if not name.startswith("VALID"))
    good = len(cases) - bad
    print(f"\nverify-tad-coverage: SELFTEST OK — {len(cases)} case(s): {bad} known-bad "
          f"fixtures rejected, {good} valid fixtures accepted (4 of them over-firing controls "
          f"for assertion (c), read off the real corpus).")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tad", type=Path,
                        default=Path("docs/architecture/"
                                     "revitalise-grant-automation-architecture.md"))
    parser.add_argument("--solution", type=Path,
                        default=Path("src/solutions/RevitaliseGrantAutomation"))
    parser.add_argument("--deferrals", type=Path,
                        default=Path("contract/tad-deferrals.json"))
    parser.add_argument("--design-docs", type=Path, nargs="+",
                        default=[Path("docs/architecture"), Path("docs/plans")],
                        help="directories of design documents whose deliverable-now prose claims "
                             "are checked — EVERY *.md in each, not only --tad (IMP-0326). "
                             "Defaults to BOTH design-document directories: docs/plans grew into "
                             "one and the old single default read none of it (IMP-0425)")
    parser.add_argument("--app-src", type=Path,
                        default=Path("src/code-apps/trustee-review-portal/src"),
                        help="the code app's source root, read by assertion (e) for the status "
                             "values the APP synthesises. Test files are excluded: a fixture "
                             "inventing a status proves the app tolerates unknown ones")
    parser.add_argument("--selftest", action="store_true",
                        help="assemble fixtures at runtime and prove the gate can fail AND pass")
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        return 2

    if args.selftest:
        return selftest()

    try:
        baseline = load_baselines(Path.cwd(), GATE)
    except BaselineError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        print(f"\nverify-tad-coverage: FAILED — config/gate-baselines.json is unusable. An "
              f"invalid or expired baseline FAILS; it is a waiver with a date on it, and the "
              f"date is the control.", file=sys.stderr)
        return 1

    code, violations, stats = run(args.tad, args.solution, args.deferrals,
                                  design_docs=args.design_docs, app_src=args.app_src,
                                  baseline=baseline)
    acquitted = stats.get("response_acquitted") or {}
    contract = (f"{stats.get('response_nulls', 0)} null response key(s) across "
                f"{stats.get('appendix_a_rows', 0)} Appendix A requirement row(s) in "
                f"{stats.get('appendix_a_docs', 0)} document(s) "
                f"({stats.get('response_nulls_non_ok', 0)} more nulled only in a non-ok "
                f"document, correctly ignored); {stats.get('status_produced', 0)} status "
                f"value(s) produced against {stats.get('status_declared', 0)} enumerated; "
                f"{stats.get('register_entries', 0)} undelivered-requirement entry(ies)")
    if acquitted:
        contract += (". ACQUITTED, never suppressed silently: "
                     + "; ".join(f"{k} ← {v}" for k, v in sorted(acquitted.items())))
    suppressed = stats.get("status_suppressed") or {}
    if suppressed:
        contract += (". STATUS FINDINGS SUPPRESSED BY config/gate-baselines.json — the FAIL is "
                     "suppressed, the finding is NOT: "
                     + "; ".join(f"`{k}` {v}" for k, v in sorted(suppressed.items())))
    spread = stats.get("response_null_actions") or {}
    if spread:
        contract += (". COMPOSED AS NULL IN MORE THAN ONE ACTION, so one acquittal covers all of "
                     "them: "
                     + "; ".join(f"{k} ×{n} actions" for k, n in sorted(spread.items())))
    unaccounted = stats.get("response_unaccounted") or {}
    if unaccounted:
        contract += (". NOT CHECKED — no register entry and no Appendix A row NAMES these, so "
                     "assertion (d) has nothing to compare and does not fail on them; a "
                     "collective declaration in prose is not machine-readable: "
                     + "; ".join(f"{k} ({v})" for k, v in sorted(unaccounted.items())))
    claims = (f"{stats.get('items', 0)} deliverable-now item(s) in "
              f"{stats.get('claims', 0)} claim(s) across {stats.get('docs_read', 0)} design "
              f"document(s)")
    if violations:
        for violation in violations:
            print(f"ERROR: {violation}", file=sys.stderr)
        print(f"\nverify-tad-coverage: FAILED — {len(violations)} violation(s). "
              f"TAD §3.1 parsed {stats.get('specs', 0)} column spec(s) across "
              f"{stats.get('table_blocks', 0)} table block(s); "
              f"{stats.get('absent', 0)} named column(s) absent from source, "
              f"{stats.get('deferred', 0)} covered by an owned, dated deferral, "
              f"{stats.get('visible', 0)} marked trustee-visible. "
              f"{claims}: {stats.get('unnamed', 0)} name no column, "
              f"{stats.get('unresolvable', 0)} name one that does not exist. "
              f"{contract}.", file=sys.stderr)
        return code
    print(f"verify-tad-coverage: OK — TAD §3.1's {stats['specs']} column spec(s) across "
          f"{stats['table_blocks']} table block(s) all exist in source or carry an owned, "
          f"dated deferral ({stats['deferred']} deferred); "
          f"{stats['visible']} trustee-visible column(s) sit on tables REV Trustee can read; "
          f"{claims} all name a column that exists; {contract}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
