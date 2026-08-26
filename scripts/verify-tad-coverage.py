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
import re
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

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


def check_deliverable_now_claims(docs_dir: Path, solution: Path) -> tuple[list[Violation], dict]:
    """Assertion (c). Every item of every deliverable-now list names a column that exists."""
    stats = {"docs_read": 0, "claims": 0, "items": 0, "unnamed": 0, "unresolvable": 0}
    violations: list[Violation] = []

    if not docs_dir.is_dir():
        return [Violation(str(docs_dir), "design-document directory not found — a gate pointed "
                                         "at a missing target does not pass (IMP-0007)")], stats

    known = all_solution_columns(solution)
    if not known:
        return [Violation(str(solution), "no attributes parsed from any Entity.xml, so no "
                                         "identifier could ever resolve; refusing to report OK "
                                         "over nothing (IMP-0007)")], stats

    for doc in sorted(docs_dir.glob("*.md")):
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


# ── The two assertions ───────────────────────────────────────────────────────

def run(tad: Path, solution: Path, deferrals_path: Path,
        today: _dt.date | None = None,
        design_docs: Path | None = None) -> tuple[int, list[Violation], dict]:
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

    stats.update({
        "absent": len(absent),
        "deferred": len(deferred),
        "checked_tables": len(stats["tables"]),
        "role_read_tables": sorted(read_tables) if read_tables else [],
        "visible": len(visible),
        "absent_list": [f"{s.table}.{s.column}" for s in absent],
        **claim_stats,
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


def _deferral_doc(entry: dict) -> str:
    return json.dumps({"_purpose": "fixture", "deferrals": [entry]}, indent=2)


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
                 delta_doc: str | None = None) -> None:
            root = base / name
            solution = _fixture_solution(root, read_tables=read_tables)
            # Design documents live in their own directory so assertion (c)'s corpus is
            # explicit: `tad.md` plus, when a case supplies one, a sibling DELTA document.
            docs = root / "docs"
            tad_path = _write(docs / "tad.md", tad)
            if delta_doc is not None:
                _write(docs / "delta-architecture.md", delta_doc)
            deferrals_path = root / "tad-deferrals.json"
            if deferral is not None:
                _write(deferrals_path, deferral)
            code, violations, _ = run(tad_path, solution, deferrals_path, today=today,
                                      design_docs=docs)
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
    parser.add_argument("--design-docs", type=Path, default=Path("docs/architecture"),
                        help="directory of design documents whose deliverable-now prose claims "
                             "are checked — EVERY *.md in it, not only --tad (IMP-0326)")
    parser.add_argument("--selftest", action="store_true",
                        help="assemble fixtures at runtime and prove the gate can fail AND pass")
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        return 2

    if args.selftest:
        return selftest()

    code, violations, stats = run(args.tad, args.solution, args.deferrals,
                                  design_docs=args.design_docs)
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
              f"{stats.get('unresolvable', 0)} name one that does not exist.", file=sys.stderr)
        return code
    print(f"verify-tad-coverage: OK — TAD §3.1's {stats['specs']} column spec(s) across "
          f"{stats['table_blocks']} table block(s) all exist in source or carry an owned, "
          f"dated deferral ({stats['deferred']} deferred); "
          f"{stats['visible']} trustee-visible column(s) sit on tables REV Trustee can read; "
          f"{claims} all name a column that exists.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
