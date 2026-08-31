#!/usr/bin/env python3
"""Verify that no security role requests a privilege the platform will never create.

A Dataverse table's ``<OwnershipType>`` decides which privileges exist for it. This is not a
policy question the project gets to answer — the privilege GUIDs are created by the platform
when the table is created, and a role binding names one by id:

* **UserOwned** — Create, Read, Write, Delete, Append, AppendTo, **Assign**, **Share**.
* **OrganizationOwned** — Create, Read, Write, Delete, Append, AppendTo. **No Assign. No
  Share.** An organization-owned row has no individual owner, so there is nobody to assign it
  to and nobody to share it from, and Dataverse never creates either privilege.

Requesting an Assign or a Share on an organization-owned table is therefore not an over-grant
that the platform quietly ignores. It is a binding against a privilege that cannot be resolved,
and it fails:

    FAILED — Privilege 'prvAssignrev_provider' (Global) on Security role 'REV Admin' :
    privilege 'prvAssignrev_provider' does not exist in this environment

── WHY THIS EXISTS ──────────────────────────────────────────────────────────────────────────

On 2026-08-24 the reviewer's live ``ensure-schema.ps1 -Env dev`` run produced exactly four such
lines: ``prvAssignrev_provider`` and ``prvSharerev_provider``, on both ``REV Admin`` and ``REV
Service Automation`` (IMP-0254). ``rev_provider`` is organization-owned; the eight-privilege
block had been written from the shape the solution's UserOwned tables use.

The instructive part is that the project got this right and wrong in the same afternoon.
``rev_anonymisedstatistic`` is also organization-owned and its role blocks omit Assign and
Share correctly. A worked correct example in the same tree did not prevent the defect, because
nothing compared a privilege request against the ownership of the table it names. That is this
gate.

── GROUND TRUTH ─────────────────────────────────────────────────────────────────────────────

Read live from DEV on 2026-08-24 via ``privileges?$filter=endswith(name,'<table>')`` for every
custom table in the solution, cross-checked against each table's live
``EntityDefinitions(LogicalName='<t>')?$select=OwnershipType``. All ten tables agreed with the
sets above with no exceptions:

    rev_applicant  rev_application  rev_grant  rev_bankaccount  rev_payment  rev_review
        UserOwned          → all eight privileges exist
    rev_provider  rev_anonymisedstatistic  rev_errorlog  rev_setting
        OrganizationOwned  → Assign and Share ABSENT, the other six present

**Note the asymmetry, because it is what makes the mistake easy: DELETE DOES EXIST on an
organization-owned table.** The missing set is exactly {Assign, Share}. Withholding Delete —
which ``rev_anonymisedstatistic`` and ``rev_grant`` both do — is a separate, deliberate policy
decision about a privilege that is really there, and this gate must never conflate the two. It
therefore only ever reports a privilege the platform cannot create; it says nothing about a
privilege deliberately not requested.

── IT DERIVES, IT DOES NOT TRANSCRIBE ───────────────────────────────────────────────────────

Ownership is read from each table's own ``<OwnershipType>`` element and the requested verb is
split off the privilege name against the table names actually present under ``Entities/``.
Nothing here holds a list of which tables are organization-owned (C-TECH-060, C-TECH-067): a
table that changes ownership, or a new organization-owned table added next month, is checked
correctly for free. A transcribed list would have gone stale on exactly the change that matters.

Privileges naming something that is not a table in this solution — ``prvReadSavedQuery``,
``prvReadEnvironmentVariableValue`` and the other out-of-box bindings — are skipped and
counted. Their ownership is not knowable from this source tree, so asserting on them would be
a guess.

Run:
    python3 scripts/verify-role-privilege-ownership.py src/solutions/RevitaliseGrantAutomation
    python3 scripts/verify-role-privilege-ownership.py --selftest

Exits 0 when every requested privilege can exist, 1 otherwise. Wired into
config/<slug>-build.yml as the ``role-privilege-ownership`` step.
"""

from __future__ import annotations

import glob
import os
import re
import sys
import tempfile

# The privilege verbs Dataverse will NOT create for a table, keyed by OwnershipType. Read this
# as "what the platform withholds", never as "what this project chooses not to grant" — the
# two are different questions and only the first belongs in a gate.
IMPOSSIBLE_VERBS: dict[str, frozenset[str]] = {
    "organizationowned": frozenset({"Assign", "Share"}),
    "userowned": frozenset(),
}

# Every verb the platform prefixes onto a table name to form a privilege. Used only to split a
# privilege name into (verb, table) and to recognise a name shaped like a table privilege at
# all; the decision itself comes from IMPOSSIBLE_VERBS above.
KNOWN_VERBS = ("Create", "Read", "Write", "Delete", "Append", "AppendTo", "Assign", "Share")


def table_ownership(root: str) -> dict[str, str]:
    """Every table's OwnershipType, READ from its own <OwnershipType> element.

    Lowercased for comparison. A table whose Entity.xml declares no OwnershipType is absent
    from the result and its privileges are reported as unknown rather than assumed.
    """
    found: dict[str, str] = {}
    for path in sorted(glob.glob(os.path.join(root, "Entities/*/Entity.xml"))):
        table = os.path.basename(os.path.dirname(path))
        with open(path, encoding="utf-8") as handle:
            source = handle.read()
        # Strip comments first: rev_grant/Entity.xml discusses its own OwnershipType in prose
        # in the file header, and a regex over raw XML would read the sentence instead of the
        # element (IMP-0020, the same trap that let a marker inside a comment satisfy a check).
        source = re.sub(r"<!--.*?-->", "", source, flags=re.S)
        match = re.search(r"<OwnershipType>([^<]+)</OwnershipType>", source)
        if match:
            found[table] = match.group(1).strip().lower()
    return found


def _split_privilege(name: str, tables: frozenset[str]) -> tuple[str, str] | None:
    """Split ``prv<Verb><table>`` into (verb, table), or None if it names no known table.

    Matches the LONGEST table suffix, so ``prvReadrev_application`` resolves to
    ``rev_application`` and never to a shorter table that happens to be a suffix of it.
    """
    if not name.startswith("prv"):
        return None
    candidates = sorted((t for t in tables if name.endswith(t)), key=len, reverse=True)
    for table in candidates:
        verb = name[len("prv"):-len(table)]
        if verb in KNOWN_VERBS:
            return verb, table
    return None


def role_privileges(root: str) -> list[tuple[str, str, str]]:
    """Every (role, privilege name, level) requested by any role file under Roles/."""
    found: list[tuple[str, str, str]] = []
    for path in sorted(glob.glob(os.path.join(root, "Roles/*/*.xml"))):
        with open(path, encoding="utf-8") as handle:
            source = handle.read()
        source = re.sub(r"<!--.*?-->", "", source, flags=re.S)
        role_match = re.search(r"<Role[^>]*\sname=\"([^\"]+)\"", source)
        role = role_match.group(1) if role_match else os.path.basename(os.path.dirname(path))
        for element in re.findall(r"<RolePrivilege\b[^>]*/>", source):
            name_match = re.search(r'\bname="([^"]+)"', element)
            if not name_match:
                continue
            level_match = re.search(r'\blevel="([^"]+)"', element)
            found.append((role, name_match.group(1),
                          level_match.group(1) if level_match else ""))
    return found


# ── C-TECH-042's role-privilege half: a REMOVAL is not a revocation ───────────────────────
#
# IMP-0407 (rework) and IMP-0418. `ensure-schema.ps1` grants privileges through
# `AddPrivilegesRole` and revokes none — its own step-5 convergence line at lines 747-753 says so
# in as many words: "A privilege removed from a role's source XML stays bound to the live role
# forever, which is the direction that matters for least privilege."
#
# So deleting a `<RolePrivilege>` line does not remove the grant from any environment it is
# already bound in. TAD A-R49 named ONE such privilege and there were TWO: `prvReadWorkflow` was
# removed from `REV Trustee`'s source on 2026-08-27 by a different session for a different reason,
# and was still bound at `privilegedepthmask` 8 (Global) in DEV on 2026-08-28 — withdrawn in prose
# one whole revision earlier with no revocation sequenced anywhere.
#
# WHAT THIS CHECKS, and the limit is the point. It checks the SOURCE-SIDE obligation only: a role
# file that DECLARES a privilege removed must have that removal sequenced as a named revoke step
# with an absence read-back in an architecture document. It can NEVER prove the environment
# converged — that needs a live privilege query, which is delivery work under provisioning/ and
# explicitly not this agent's to author (agents/improvement-agent.md L318). The read-back rows the
# TAD sequences are the live half, and they are expected to FAIL on their first run.
#
# It reads the removal DECLARATION from comments — that is where a removal is recorded — but
# decides whether the privilege is still granted from the COMMENT-STRIPPED element set, so a
# commented-out `<RolePrivilege>` can never read as a live grant. `REV Trustee.xml` alone carries
# four prose discussions of `prvReadWorkflow`, which is IMP-0020's trap exactly.

# THREE NARROWINGS, each compelled by measurement rather than chosen. The first form of this
# check measured 8 findings, 0 TRUE positives, over the real role files. Each narrowing removes a
# named class of false positive and none of them touches the two genuine removals:
#
#  (1) ONLY A PRIVILEGE THAT COULD EXIST NEEDS REVOKING, and this narrowing had to be REFINED
#      once. A privilege the platform never created was never bound, so demanding a revoke step
#      for it is nonsense. Two evidenced exclusions:
#        (a) the comment itself declares the privilege does not exist — `REV Admin.xml:197` and
#            `:223` say "REMOVED 2026-08-14 — prvReadSavedQuery does not exist as a privilege in
#            this environment (confirmed live)". This also removes the bogus bare token `prvRead`,
#            extracted from the same comments' "under any prvRead* variant".
#        (b) it resolves to a SOLUTION table with a verb the platform withholds — IMP-0254's
#            impossible-verb case, `prvAssignrev_provider` and `prvSharerev_provider`
#            (`REV Admin.xml:93`), decided from IMPOSSIBLE_VERBS rather than from a list.
#      The FIRST attempt at this narrowing required the privilege to resolve to a solution table
#      at all, and that threw away the FOUNDING TRUE POSITIVE: `prvReadWorkflow` names the
#      out-of-box `workflow` table, exists perfectly well, and was measured bound at Global in DEV
#      on 2026-08-28. An out-of-box privilege is in scope precisely because it is real.
#  (2) THE MARKER MUST BE NEAR THE NAME. `REV Admin.xml:93` is a prose paragraph about rev_provider
#      CRUD design containing "a provider ... can simply be removed" — about a provider ROW, not a
#      privilege. Requiring the removal marker within MARKER_WINDOW characters of the privilege
#      name removes it.
#  (3) WORD-BOUNDARY MATCHING IN THE DOCUMENTS. The bare token `prvRead` was extracted from prose
#      and then scored as SEQUENCED because "prvRead" is a substring of every line naming
#      `prvReadWorkflow` — a false NEGATIVE, the one direction that hides work. Document matching
#      is now word-boundary anchored.
#
# Re-measured after all three: 2 declared removals examined — exactly the two real ones — 0
# findings, and can-it-fail proved by removing the TAD's sequenced step for one of them.

MARKER_WINDOW = 240

REMOVAL_MARKERS = (r"\bREMOVED\b", r"\bWITHDRAWN\b", r"\bwithdrawn\b", r"\bremoved\b")

# A comment declaring the privilege never existed. Such a privilege was never bound, so there is
# nothing to revoke — narrowing (1)(a).
NONEXISTENT_MARKERS = (r"does not exist", r"do(?:es)? not exist", r"never created",
                       r"not found by exact name", r"cannot exist")
REVOKE_TOKENS = (r"\$ref\s+delete", r"\$ref`?\s*delete", r"\brevoke\b", r"\brevocation\b",
                 r"\bRevoke\b")
ABSENCE_TOKENS = (r"\bis NOT bound\b", r"\bNOT bound\b", r"\babsence read-back\b",
                  r"\babsence\b", r"\bread the live privilege set back\b")


def declared_removals(root: str,
                      ownership: dict[str, str] | None = None
                      ) -> list[tuple[str, str, str, int]]:
    """Every (role, privilege, file, lineno) a role file declares REMOVED in its own source.

    A declaration counts only when ALL of these hold — see the three narrowings above:
      * the privilege is absent from that role's live (comment-stripped) `<RolePrivilege>` set;
      * a removal marker sits within MARKER_WINDOW characters of the privilege name;
      * the privilege is one the PLATFORM ACTUALLY CREATES for a solution table, so it could
        have been bound and therefore can need revoking.
    """
    if ownership is None:
        ownership = table_ownership(root)
    tables = frozenset(ownership)

    def could_exist(priv: str, body: str) -> bool:
        # (1)(a) the comment itself says it does not exist -> never bound, nothing to revoke.
        if any(re.search(p, body, re.IGNORECASE) for p in NONEXISTENT_MARKERS):
            return False
        # (1)(b) a solution-table privilege with a verb the platform withholds (IMP-0254).
        split = _split_privilege(priv, tables)
        if split is not None:
            verb, table = split
            if verb in IMPOSSIBLE_VERBS.get(ownership.get(table, ""), frozenset()):
                return False
        # Everything else — including out-of-box privileges such as prvReadWorkflow — is REAL,
        # was grantable, and is therefore in scope.
        return True

    out: list[tuple[str, str, str, int]] = []
    for path in sorted(glob.glob(os.path.join(root, "Roles/*/*.xml"))):
        with open(path, encoding="utf-8") as handle:
            source = handle.read()
        stripped = re.sub(r"<!--.*?-->", "", source, flags=re.S)
        live = set(re.findall(r'<RolePrivilege\b[^>]*\bname="([^"]+)"', stripped))
        role_match = re.search(r"<Role[^>]*\sname=\"([^\"]+)\"", stripped)
        role = role_match.group(1) if role_match else os.path.basename(os.path.dirname(path))

        for comment in re.finditer(r"<!--(.*?)-->", source, flags=re.S):
            body = comment.group(1)
            marker_spans = [m.start() for pat in REMOVAL_MARKERS
                            for m in re.finditer(pat, body)]
            if not marker_spans:
                continue
            lineno = source[:comment.start()].count("\n") + 1
            for match in re.finditer(r"\b(prv[A-Za-z_0-9]+)\b", body):
                priv = match.group(1)
                if priv in live:
                    continue          # still granted — not a removal
                if not could_exist(priv, body):
                    continue          # narrowing (1)
                if not any(abs(match.start() - s) <= MARKER_WINDOW for s in marker_spans):
                    continue          # narrowing (2)
                out.append((role, priv, path, lineno))
    return sorted(set(out))


def revoke_is_sequenced(privilege: str, role: str, docs: list[str]) -> tuple[bool, bool]:
    """(has_revoke_step, has_absence_readback) for this privilege across the given documents.

    Deliberately evidence-shaped rather than clever: the privilege NAME must appear on a line
    that also carries a revoke token, and on a line that also carries an absence/read-back
    token. Both halves are required because A-R49's own failure was a withdrawal recorded in
    prose with no sequenced step and no read-back.
    """
    has_revoke = has_absence = False
    # Word-boundary anchored — narrowing (3). A substring match let the bare token `prvRead`
    # score as sequenced off every line naming `prvReadWorkflow`, which is a false NEGATIVE.
    name_re = re.compile(rf"\b{re.escape(privilege)}\b")
    for text in docs:
        for line in text.splitlines():
            if not name_re.search(line):
                continue
            if any(re.search(t, line) for t in REVOKE_TOKENS):
                has_revoke = True
            if any(re.search(t, line) for t in ABSENCE_TOKENS):
                has_absence = True
    return has_revoke, has_absence


def distinct_removals(root: str,
                      ownership: dict[str, str] | None = None
                      ) -> list[tuple[str, str, list[str]]]:
    """Every DISTINCT (role, privilege) declared removed, with every occurrence's file:line.

    `declared_removals()` yields one tuple per removal-marker OCCURRENCE, which is the right
    granularity for reporting where a declaration lives and the wrong one for COUNTING. `REV
    Trustee`'s `prvReadWorkflow` removal is explained in two separate comments in the same file
    (lines 237 and 395), so the raw count read 3 where there are 2 real removals — and this
    script's own header at the top of this section records 2 as the truth, so the gate disagreed
    with itself in writing (IMP-0453). Miscounting privilege removals is precisely the defect
    TAD Erratum 5.1 exists to correct, which is why a cosmetic count matters here.
    """
    grouped: dict[tuple[str, str], list[str]] = {}
    for role, privilege, path, lineno in declared_removals(root, ownership):
        grouped.setdefault((role, privilege), []).append(f"{path}:{lineno}")
    return [(role, privilege, where) for (role, privilege), where in sorted(grouped.items())]


def check_removals_are_sequenced(root: str, doc_dir: str) -> list[str]:
    """C-TECH-042's role-privilege clause, source side. Returns problem strings."""
    removals = declared_removals(root)
    if not removals:
        return []
    docs = []
    for path in sorted(glob.glob(os.path.join(doc_dir, "*.md"))):
        try:
            with open(path, encoding="utf-8") as handle:
                docs.append(handle.read())
        except OSError:
            continue

    problems: list[str] = []
    for role, privilege, path, lineno in removals:
        has_revoke, has_absence = revoke_is_sequenced(privilege, role, docs)
        if has_revoke and has_absence:
            continue
        missing = []
        if not has_revoke:
            missing.append("a named revoke step")
        if not has_absence:
            missing.append("an absence read-back")
        problems.append(
            f"  REMOVAL NOT SEQUENCED - '{privilege}' is declared removed from role '{role}' "
            f"({os.path.relpath(path)}:{lineno}) and is absent from that role's live privilege "
            f"set in source, but no document under {doc_dir} sequences {' and '.join(missing)} "
            f"for it. Removing the line does NOT revoke the grant: ensure-schema.ps1 adds "
            f"privileges through AddPrivilegesRole and revokes none (its own convergence line, "
            f"provisioning/dataverse/ensure-schema.ps1:747-753), so the privilege stays bound in "
            f"every environment it already reached and the write boundary is narrower in source "
            f"than in reality. This is C-TECH-042's role-privilege clause. Sequence a named "
            f"per-environment `$ref` delete plus a live read-back asserting ABSENCE - and expect "
            f"that read-back to FAIL on its first run, which is what proves it can (IMP-0407; "
            f"A-R49 named one such privilege when there were two)."
        )
    return problems


_USAGE = "<solution-root> [<doc-dir>]"
_EXAMPLE = "src/solutions/RevitaliseGrantAutomation"


def _usage_error(got: int) -> int:
    """Print the SIGNATURE, not the whole module docstring (IMP-0470).

    A usage error answered with the entire docstring and exit 2 reads like a real finding rather
    than a mistyped command. The wbs:6.9 dispatch quoted a one-argument invocation of the
    two-argument `verify-code-app-column-bindings.py`; it printed 98 lines of prose and cost a
    re-check to establish that nothing was actually wrong. Exit code is unchanged at 2 — only the
    output is, so every caller that keys on the code behaves identically.
    """
    name = os.path.basename(__file__)
    print(f"{name}: USAGE ERROR — expected 1 argument(s), got {got}.", file=sys.stderr)
    print(f"  usage:   python3 scripts/{name} {_USAGE}", file=sys.stderr)
    print(f"  example: python3 scripts/{name} {_EXAMPLE}", file=sys.stderr)
    print("  This is a usage error, NOT a finding. The rationale is this file's module docstring.",
          file=sys.stderr)
    return 2


def main(argv: list[str]) -> int:
    if len(argv) not in (2, 3):
        return _usage_error(len(argv) - 1)
    root = argv[1].rstrip("/")
    doc_dir = argv[2].rstrip("/") if len(argv) == 3 else "docs/architecture"

    roles_dir = os.path.join(root, "Roles")
    if not os.path.isdir(roles_dir):
        print(f"FAIL - {roles_dir} is missing, so there are no role files to check. This gate "
              f"passing over an absent directory would be a gate that cannot fail (IMP-0007).")
        return 1

    ownership = table_ownership(root)
    if not ownership:
        print(f"FAIL - no <OwnershipType> was readable from any {root}/Entities/*/Entity.xml. "
              f"Without ownership there is nothing to check against, and reporting PASS here "
              f"would be a gate firing on nothing (IMP-0057).")
        return 1

    tables = frozenset(ownership)
    requests = role_privileges(root)
    if not requests:
        print(f"FAIL - no <RolePrivilege> element was found in any {roles_dir}/*/*.xml. Either "
              f"the roles ship no privileges, or this gate's reader is broken; both need a "
              f"person, not a PASS.")
        return 1

    problems: list[str] = []
    checked = 0
    skipped: list[str] = []

    for role, privilege, level in requests:
        split = _split_privilege(privilege, tables)
        if split is None:
            skipped.append(privilege)
            continue
        verb, table = split
        checked += 1
        owner = ownership[table]
        impossible = IMPOSSIBLE_VERBS.get(owner)
        if impossible is None:
            problems.append(
                f"  UNKNOWN OWNERSHIP - {table} declares OwnershipType '{owner}', which this "
                f"gate has no privilege set for. Add it to IMPOSSIBLE_VERBS with the live "
                f"privilege inventory that proves it, rather than letting the privilege "
                f"through unchecked."
            )
            continue
        if verb in impossible:
            legal = ", ".join(v for v in KNOWN_VERBS if v not in impossible)
            article = "an" if verb[0].upper() in "AEIOU" else "a"
            problems.append(
                f"  PRIVILEGE CANNOT EXIST - role '{role}' requests '{privilege}'"
                f"{f' ({level})' if level else ''}, but {table} is {owner} and Dataverse never "
                f"creates {article} {verb} privilege for an organization-owned table - there is no "
                f"individual owner to assign to or share from. The live run fails with "
                f"\"privilege '{privilege}' does not exist in this environment\". Remove this "
                f"line. The privileges that DO exist for {table} are: {legal} - note that "
                f"Delete is among them, so this is not a reason to drop Delete too."
            )

    # C-TECH-042's role-privilege clause (IMP-0407): a declared REMOVAL obliges a sequenced
    # revoke plus an absence read-back. Source side only — it can never prove the environment
    # converged.
    removal_problems = check_removals_are_sequenced(root, doc_dir)
    removals_seen = len(distinct_removals(root))

    if problems or removal_problems:
        if problems:
            print(f"FAIL - {len(problems)} role privilege(s) the platform will never create:")
            print("\n".join(problems))
        if removal_problems:
            print(f"FAIL - {len(removal_problems)} declared privilege removal(s) with no "
                  f"sequenced revocation:")
            print("\n".join(removal_problems))
        print(f"\n{checked} table privilege(s) checked across {len(set(r for r, _, _ in requests))} "
              f"role(s); {len(skipped)} non-solution privilege(s) skipped; "
              f"{removals_seen} declared removal(s) examined.")
        return 1

    org_owned = sorted(t for t, o in ownership.items() if o == "organizationowned")
    print(
        f"PASS - {checked} table privilege(s) across "
        f"{len(set(r for r, _, _ in requests))} role(s), every one a privilege the platform "
        f"actually creates for the table it names. "
        f"{len(org_owned)} organization-owned table(s) ({', '.join(org_owned)}) correctly "
        f"request no Assign and no Share. "
        f"{len(skipped)} out-of-box privilege(s) skipped as not derivable from this source tree."
    )
    print(f"  {removals_seen} distinct declared privilege removal(s) — counted by (role, "
          f"privilege), not by comment occurrence (IMP-0453) — each with a named revoke step and "
          f"an absence read-back sequenced (C-TECH-042, IMP-0407). SOURCE SIDE ONLY — this says "
          f"nothing about whether any environment has actually converged; the read-backs the "
          f"documents sequence are the live half and are expected to fail on first run.")
    return 0


# ── selftest ──────────────────────────────────────────────────────────────────────────────
# The known-bad fixture is the exact shape that failed live on 2026-08-24: an Assign and a
# Share requested on an organization-owned table. A gate with no known-bad fixture is a gate
# nobody has seen fail.

_ENTITY = """<?xml version="1.0" encoding="utf-8"?>
<Entity>
  <Name LocalizedName="T">{table}</Name>
  <EntityInfo><entity Name="{table}"><attributes /></entity></EntityInfo>
  <OwnershipType>{ownership}</OwnershipType>
  <PrimaryNameAttribute>rev_name</PrimaryNameAttribute>
</Entity>
"""

_ROLE = """<?xml version="1.0" encoding="utf-8"?>
<Role name="{role}">
  <RolePrivileges>
{privileges}  </RolePrivileges>
</Role>
"""


def _tree(base: str, *, ownership: str, verbs: tuple[str, ...],
          extra: str = "", removal: str = "", doc: str = "") -> tuple[str, str]:
    """Build a throwaway solution tree. Returns (solution_root, doc_dir).

    `removal` is injected as a COMMENT inside the role file, which is where a real removal
    declaration lives. `doc` is written into the fixture's own docs dir, so a removal-sequencing
    case never reads the repository's real architecture documents.
    """
    table = "rev_thing"
    root = os.path.join(base, "sol")
    doc_dir = os.path.join(base, "docs")
    os.makedirs(os.path.join(root, "Entities", table), exist_ok=True)
    os.makedirs(os.path.join(root, "Roles", "R One"), exist_ok=True)
    os.makedirs(doc_dir, exist_ok=True)
    if doc:
        with open(os.path.join(doc_dir, "tad.md"), "w", encoding="utf-8") as handle:
            handle.write(doc)
    with open(os.path.join(root, "Entities", table, "Entity.xml"), "w",
              encoding="utf-8") as handle:
        handle.write(_ENTITY.format(table=table, ownership=ownership))
    lines = "".join(
        f'    <RolePrivilege name="prv{verb}{table}" level="Global" />\n' for verb in verbs
    ) + extra
    if removal:
        lines = f"    <!-- {removal} -->\n" + lines
    with open(os.path.join(root, "Roles", "R One", "R One.xml"), "w",
              encoding="utf-8") as handle:
        handle.write(_ROLE.format(role="R One", privileges=lines))
    return root, doc_dir


_ALL_EIGHT = KNOWN_VERBS
_SIX = tuple(v for v in KNOWN_VERBS if v not in ("Assign", "Share"))
# Delete withheld as well, so a fixture can declare prvDeleterev_thing REMOVED and have that
# privilege genuinely ABSENT from the live set — which is what a removal means.
_FIVE_NO_DELETE = tuple(v for v in _SIX if v != "Delete")

_CASES = {
    # IMP-0254: the shape that produced four FAILED lines on the live DEV run.
    "assign-share-on-org-owned-must-fail": (
        {"ownership": "OrganizationOwned", "verbs": _ALL_EIGHT}, 1,
        "PRIVILEGE CANNOT EXIST"),
    # The fix: the same table, the six privileges that exist. Delete stays.
    "six-on-org-owned-must-pass": (
        {"ownership": "OrganizationOwned", "verbs": _SIX}, 0, "PASS"),
    # All eight on a user-owned table is correct and must not be flagged.
    "all-eight-on-user-owned-must-pass": (
        {"ownership": "UserOwned", "verbs": _ALL_EIGHT}, 0, "PASS"),
    # An out-of-box privilege names no table here; it must be skipped, not guessed at.
    "out-of-box-privilege-must-be-skipped": (
        {"ownership": "OrganizationOwned", "verbs": _SIX,
         "extra": '    <RolePrivilege name="prvReadSavedQuery" level="Global" />\n'}, 0,
        "1 out-of-box privilege(s) skipped"),
    # An ownership value this gate has no inventory for must be reported, never waved through.
    "unknown-ownership-must-fail": (
        {"ownership": "BusinessOwned", "verbs": _SIX}, 1, "UNKNOWN OWNERSHIP"),

    # ── C-TECH-042's role-privilege clause (IMP-0407) ─────────────────────────────────────
    # The founding shape: a privilege declared REMOVED, absent from the live set, with NOTHING
    # sequencing its revocation. This is prvReadWorkflow-on-REV-Trustee reduced to a fixture.
    "declared-removal-with-no-revoke-must-fail": (
        {"ownership": "UserOwned", "verbs": _FIVE_NO_DELETE,
         "removal": "prvDeleterev_thing REMOVED 2026-08-27 - the transport it existed for was "
                    "abandoned",
         "doc": "# TAD\nNothing here sequences anything.\n"}, 1, "REMOVAL NOT SEQUENCED"),
    # Both halves present -> clean. A revoke step with no absence read-back is NOT enough.
    "declared-removal-fully-sequenced-must-pass": (
        {"ownership": "UserOwned", "verbs": _FIVE_NO_DELETE,
         "removal": "prvDeleterev_thing REMOVED 2026-08-27",
         "doc": "# TAD\n| 8 | One `$ref` delete removing `prvDeleterev_thing` from the role |\n"
                "| `prvDeleterev_thing` is NOT bound after the change | read the live privilege "
                "set back |\n"}, 0, "1 distinct declared privilege removal(s)"),
    "declared-removal-revoke-without-readback-must-fail": (
        {"ownership": "UserOwned", "verbs": _FIVE_NO_DELETE,
         "removal": "prvDeleterev_thing REMOVED 2026-08-27",
         "doc": "# TAD\n| 8 | A revoke removing `prvDeleterev_thing` |\n"}, 1,
        "an absence read-back"),
    # Narrowing (1)(a): a privilege the comment says NEVER EXISTED needs no revoke.
    "removal-of-a-nonexistent-privilege-must-pass": (
        {"ownership": "UserOwned", "verbs": _SIX,
         "removal": "REMOVED 2026-08-14 - prvReadSavedQuery does not exist as a privilege in "
                    "this environment (confirmed live)",
         "doc": "# TAD\n"}, 0, "PASS"),
    # Narrowing (1)(b): IMP-0254's impossible verb was never bound either.
    "removal-of-an-impossible-verb-must-pass": (
        {"ownership": "OrganizationOwned", "verbs": _SIX,
         "removal": "prvAssignrev_thing REMOVED - organization-owned, so it never existed",
         "doc": "# TAD\n"}, 0, "PASS"),
    # Narrowing (2): prose about a RECORD being removed is not a privilege removal.
    "prose-about-removing-a-record-must-not-count": (
        {"ownership": "UserOwned", "verbs": _FIVE_NO_DELETE,
         "removal": "Reusable reference data, so unlike rev_grant there is no design reason to "
                    "withhold Delete - a provider that has never been referenced can simply be "
                    "removed. " + ("Padding to push the name well outside the window. " * 12)
                    + "See prvDeleterev_thing above.",
         "doc": "# TAD\n"}, 0, "PASS"),
}

# Delete must never be reported as impossible on an organization-owned table — that is the
# asymmetry this gate exists to keep straight, and an exit code cannot prove its absence.
_MUST_NOT_CONTAIN = {
    "assign-share-on-org-owned-must-fail": "requests 'prvDeleterev_thing'",
    "six-on-org-owned-must-pass": "PRIVILEGE CANNOT EXIST",
}


def selftest() -> int:
    import contextlib
    import io

    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        for name, (kwargs, want_rc, want_text) in _CASES.items():
            root, doc_dir = _tree(os.path.join(tmp, name), **kwargs)
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                rc = main(["verify-role-privilege-ownership.py", root, doc_dir])
            text = buffer.getvalue()
            banned = _MUST_NOT_CONTAIN.get(name)
            ok = (rc == want_rc and want_text in text
                  and (not banned or banned not in text))
            print(f"  {'OK' if ok else 'DID NOT BEHAVE':16} {name} → exit {rc} "
                  f"(expected {want_rc})")
            if not ok:
                failures.append(name)
                for line in text.splitlines():
                    print(f"                   {line}")

    if failures:
        print(f"\nverify-role-privilege-ownership: SELFTEST FAILED — {', '.join(failures)}",
              file=sys.stderr)
        return 1
    print(f"\nverify-role-privilege-ownership: SELFTEST OK — {len(_CASES)} fixtures. The shape "
          f"that failed live fails here, Delete on an organization-owned table is never "
          f"flagged, and an ownership value with no known inventory is reported rather than "
          f"waved through.")
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv[1:]:
        sys.exit(selftest())
    sys.exit(main(sys.argv))
