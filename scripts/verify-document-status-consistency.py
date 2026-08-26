#!/usr/bin/env python3
"""Compare a citation's asserted status against the cited document's own Status line.

WHY THIS EXISTS. `approved-document-internally-inconsistent` is this project's most persistent
documentation class, and one of its shapes is exactly mechanical: **one fact stated in two
fixed-format places, with nothing comparing them.** A dev summary, test report or TAD cites
another document and asserts its status in parentheses; that document carries its own `Status:`
header. Nothing in this repository has ever read the two together.

  * `IMP-0340` (FIFTH instance). `revitalise-form-field-corrections-plan.md` line 9 and its TAD
    line 11 both read `Status: DRAFT`, while the dev summary, the test report and the build
    manifest all cited them as APPROVED revision 1.4 — and the work they specify had been built,
    packaged as build #6 and deployed to DEV at V3. The DRAFT headers were the stale side.
  * `IMP-0344` (SIXTH instance), found live while measuring this gate.
    `trustee-portal-visual-refresh-dev-summary.md` line 4 cites its TAD as
    "(APPROVED, Revision 2)"; that TAD's own line 12 reads "Status: DRAFT — Revision 2". Same
    revision, contradictory status.

Five instances and a documented preference for the mechanical home
(`skills/how-to-promote-a-finding.md` §1) put this well past a prose rule. Both sides are
fixed-format lines, so it needs no prose parsing — which is what separates it from the
TAD-narrative flavour of this class that improvement review 29 measured at 48% false positives
and correctly declined to gate.

WHAT IT CHECKS

  `STATUS-DISAGREES` — a citation asserting a status for a repo-relative `.md` path, where the
                       cited file's own first `Status:` line says something different.

WHAT IT DELIBERATELY DOES NOT DO. **It cannot tell which side is stale, and it does not guess.**
`IMP-0340` and `IMP-0344` disagree on that very point: in `IMP-0340` the header was wrong, and in
`IMP-0344` it is genuinely unsettled and belongs to the document's owner. The gate reports the
contradiction and names both lines; a human decides. That is why it is wired SOFT.

EXIT CODES: 0 clean (or `--warn-only`); 1 findings, or zero citations resolved (the `IMP-0007`
shape — a gate reporting OK over nothing); 2 usage error.

RESIDUAL. Three, all measured rather than guessed:

  * A citation that asserts a status in PROSE ("the TAD was approved on Tuesday") is not read.
    Only the parenthesised form beside a path is, because that is the form both instances took and
    the only one with no prose resolution in it.
  * A cited document with no `Status:` line at all is reported as `NO-STATUS-LINE`, separately,
    because "the citation may be inventing a status" and "the two disagree" are different facts.
  * A revision number is NOT compared. `IMP-0344`'s instance agrees on revision 2 and disagrees on
    status, and a revision comparison would need to know which side increments first.
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

# The closed status vocabulary this repository actually uses in headers and citations. A closed
# list is the precision: an open "any capitalised word in parentheses" reading would fire on
# "(Revision 2)", "(see below)" and every parenthetical in the corpus.
STATUS_WORDS = {
    "APPROVED", "DRAFT", "AWAITING", "REJECTED", "SUPERSEDED", "RETIRED", "ACCEPTED",
    "FINAL", "PROPOSED", "WITHDRAWN", "DEPRECATED", "COMPLETE", "CURRENT", "STALE",
}

# The directories a cited path may live in. Anchoring the path to a known root is what stops this
# matching every inline `foo.md` mention in prose.
CITED_ROOTS = ("docs", "contract", "templates", "agents", "skills", "constraints", "config",
               "provisioning", "src", "logs")

# `**TAD Reference:** `docs/architecture/x-architecture.md` (APPROVED, Revision 2)`
# `**SDD:** [docs/plans/y-plan.md](../plans/y-plan.md) (APPROVED)`
# `**Dev Summary:** docs/development/z-dev-summary.md (APPROVED revision 1.4)`
#
# The path may be followed by a CLOSING BACKTICK, a markdown link's closing bracket, a dash or
# nothing before the parenthesised status. Anything else between them and this does not match, on
# purpose.
#
# THE BACKTICK IS NOT COSMETIC — it is the whole first measurement of this gate. Without it the
# corpus resolved 5 citations and reported a CLEAN RUN over `IMP-0344`'s own instance, which is
# written `**TAD Reference:** `docs/…-architecture.md` (APPROVED, Revision 2)`. This repository's
# house style puts every path in a code span, so a regex that does not allow one is blind to
# almost every citation it exists to read: 5 resolved before, 24 after. That is the
# `agents/improvement-agent.md` warning — "where a gate reports 0 findings against a corpus you
# know contains an instance, that is the tell" — firing exactly as written.
CITATION_RE = re.compile(
    r"(?P<path>(?:" + "|".join(CITED_ROOTS) + r")/[\w./-]+\.md)"
    r"(?P<between>[`)\]\s]*(?:\([^)]*\))?[`)\]\s]*[—–-]?\s*)"
    r"\(\s*\*{0,2}(?P<status>[A-Za-z]+)\b")

# A document's own header status. Bold-tolerant in both directions, because
# `**Status:** **APPROVED 2026-08-16**` is a real line in this repo and a regex demanding a letter
# where a `*` stands reports "no status line" on a document that plainly has one. That exact bug
# made the first measurement of this gate see 2 statusless files.
OWN_STATUS_RE = re.compile(
    r"^\s*>?\s*\*{0,2}Status\*{0,2}\s*:\s*(?P<rest>.+?)\s*$", re.MULTILINE | re.IGNORECASE)

# A struck-through value is the CORRECTED way to record history — `~~AWAITING~~ — now APPROVED` —
# so it must never be read as the current status, or this gate would punish its own remedy.
STRUCK_SPAN_RE = re.compile(r"~~.*?~~")

WORD_RE = re.compile(r"[A-Za-z]+")


@dataclass(frozen=True)
class Finding:
    kind: str
    document: str
    line: int
    detail: str

    def __str__(self) -> str:
        return f"{self.kind}: {self.document}:{self.line}: {self.detail}"


def _first_status_word(text: str) -> str | None:
    """The first recognised status word in a status line, ignoring struck-through spans."""
    cleaned = STRUCK_SPAN_RE.sub(" ", text)
    for word in WORD_RE.findall(cleaned):
        if word.upper() in STATUS_WORDS:
            return word.upper()
    return None


def own_status(path: Path) -> tuple[str | None, int]:
    """(status, line number) from the cited document's FIRST Status line.

    The first is the header, which is what both instances of this defect are about. A later
    `Status:` inside a revision table describes a past state.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None, 0
    for m in OWN_STATUS_RE.finditer(text):
        status = _first_status_word(m.group("rest"))
        if status:
            return status, text[: m.start()].count("\n") + 1
    return None, 0


def resolve(cited: str, citing: Path, repo_root: Path) -> Path | None:
    """Resolve a cited path. REPO-RELATIVE FIRST — that is how this repo writes them.

    Trying the citing file's own directory first is what made the first measurement of this gate
    resolve 0 of 17 citations and report a clean run.
    """
    candidate = repo_root / cited
    if candidate.is_file():
        return candidate
    candidate = (citing.parent / cited).resolve()
    if candidate.is_file():
        return candidate
    return None


def check_document(path: Path, repo_root: Path) -> tuple[list[Finding], int]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return [Finding("UNREADABLE", str(path), 0, f"cannot read: {exc}")], 0

    findings: list[Finding] = []
    resolved = 0
    rel = path.relative_to(repo_root).as_posix() if path.is_relative_to(repo_root) else path.name

    for line_no, line in enumerate(text.splitlines(), 1):
        for m in CITATION_RE.finditer(line):
            asserted = m.group("status").upper()
            if asserted not in STATUS_WORDS:
                continue
            cited_rel = m.group("path")
            cited = resolve(cited_rel, path, repo_root)
            if cited is None:
                continue
            # A document citing its own status is not two sources disagreeing.
            if cited.resolve() == path.resolve():
                continue
            resolved += 1
            actual, actual_line = own_status(cited)
            if actual is None:
                findings.append(Finding(
                    "NO-STATUS-LINE", rel, line_no,
                    f"asserts {asserted} for '{cited_rel}', and that file carries no "
                    f"'Status:' line at all. The assertion rests on nothing the cited "
                    f"document says about itself."))
                continue
            if actual != asserted:
                findings.append(Finding(
                    "STATUS-DISAGREES", rel, line_no,
                    f"cites '{cited_rel}' as {asserted}; that document's own Status line "
                    f"({cited_rel}:{actual_line}) says {actual}. One of the two is stale and "
                    f"this gate cannot tell which — on IMP-0340 the header was wrong, on "
                    f"IMP-0344 it needed the document's owner. Settle it in the owning "
                    f"document, not here."))
    return findings, resolved


def run(root: Path, repo_root: Path) -> tuple[int, list[Finding], int, int]:
    if not root.is_dir():
        return 1, [Finding("NO-SOURCE", str(root), 0,
                           "directory does not exist, so this gate cannot see what it checks "
                           "(IMP-0007).")], 0, 0

    docs = sorted(root.rglob("*.md"))
    findings: list[Finding] = []
    resolved = 0
    for d in docs:
        f, n = check_document(d, repo_root)
        findings.extend(f)
        resolved += n

    if resolved == 0:
        return 1, [Finding("NO-SOURCE", str(root), 0,
                           f"{len(docs)} document(s) scanned and NOT ONE status citation "
                           f"resolved, so this gate would be reporting OK over nothing "
                           f"(IMP-0007). The first build of this gate did exactly that, by "
                           f"resolving cited paths relative to the citing file instead of the "
                           f"repository root.")], len(docs), 0

    return (1 if findings else 0), findings, len(docs), resolved


# ---------------------------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------------------------

_TAD_DRAFT = """# Trustee Portal Architecture

**Status:** DRAFT — **Revision 2**
"""

_TAD_APPROVED = """# Trustee Portal Architecture

**Status:** **APPROVED 2026-08-16** — **Revision 2**
"""

_TAD_STRUCK = """# Trustee Portal Architecture

**Status:** ~~DRAFT~~ — corrected 2026-08-26: **APPROVED**, Revision 2
"""

_TAD_NO_STATUS = """# Trustee Portal Architecture

Revision 2. Nothing here states a status.
"""

# IMP-0344's real shape.
_SUMMARY = ("# Dev Summary\n\n**TAD Reference:** docs/architecture/tad.md "
            "(APPROVED, Revision 2)\n")

# A markdown-linked citation, which is how several documents in this repo write it.
_SUMMARY_LINKED = ("# Dev Summary\n\n**TAD:** [docs/architecture/tad.md]"
                   "(../architecture/tad.md) (APPROVED)\n")

# The parenthetical is not a status, so there is nothing to compare.
_SUMMARY_NO_CLAIM = "# Dev Summary\n\n**TAD:** docs/architecture/tad.md (Revision 2)\n"


def selftest() -> int:
    failures: list[str] = []

    def kinds(summary: str, tad: str) -> list[str]:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "docs" / "architecture").mkdir(parents=True)
            (root / "docs" / "development").mkdir(parents=True)
            (root / "docs" / "architecture" / "tad.md").write_text(tad, encoding="utf-8")
            p = root / "docs" / "development" / "summary.md"
            p.write_text(summary, encoding="utf-8")
            found, _ = check_document(p, root)
            return sorted(f.kind for f in found)

    if "STATUS-DISAGREES" not in kinds(_SUMMARY, _TAD_DRAFT):
        failures.append("a citation asserting APPROVED over a DRAFT header was not reported "
                        "(IMP-0344's exact instance)")
    if "STATUS-DISAGREES" in kinds(_SUMMARY, _TAD_APPROVED):
        failures.append("a citation agreeing with the cited header was reported anyway — and "
                        "note the header is BOLD, the shape that made the first measurement of "
                        "this gate see a statusless file")
    if "STATUS-DISAGREES" in kinds(_SUMMARY, _TAD_STRUCK):
        failures.append("a struck-through previous status was read as current, so the gate "
                        "forbids the documented way of recording a correction")
    if "NO-STATUS-LINE" not in kinds(_SUMMARY, _TAD_NO_STATUS):
        failures.append("a citation asserting a status for a document that states none was not "
                        "reported")
    if "STATUS-DISAGREES" not in kinds(_SUMMARY_LINKED, _TAD_DRAFT):
        failures.append("a markdown-linked citation was not read, so the gate is blind to the "
                        "form several documents in this repo use")
    if kinds(_SUMMARY_NO_CLAIM, _TAD_DRAFT):
        failures.append("'(Revision 2)' was read as a status claim — the closed status "
                        "vocabulary is what keeps this gate off every parenthetical in the tree")

    with tempfile.TemporaryDirectory() as td:
        code, found, _n, _r = run(Path(td) / "absent", Path(td))
        if code != 1 or not any(f.kind == "NO-SOURCE" for f in found):
            failures.append("a missing directory did not report NO-SOURCE")
        empty = Path(td) / "empty"
        empty.mkdir()
        code, found, _n, _r = run(empty, Path(td))
        if code != 1 or not any(f.kind == "NO-SOURCE" for f in found):
            failures.append("a corpus resolving zero citations did not report NO-SOURCE — the "
                            "'0 findings is the tell' case this gate's first measurement hit")

    if failures:
        for f in failures:
            print(f"SELFTEST FAILURE: {f}", file=sys.stderr)
        print(f"\nverify-document-status-consistency --selftest: FAILED "
              f"({len(failures)} failure(s)).", file=sys.stderr)
        return 1

    print("verify-document-status-consistency --selftest: OK — 8 fixture(s): IMP-0344's exact "
          "instance reports; an agreeing BOLD header does not; a struck-through previous status "
          "does not, so the gate does not forbid its own remedy; a cited document stating no "
          "status reports separately as NO-STATUS-LINE; a markdown-linked citation is read; "
          "'(Revision 2)' is not read as a status; and a missing directory and a corpus "
          "resolving zero citations both report rather than passing over nothing.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path("docs"),
                        help="directory to scan for citing documents (default: docs)")
    parser.add_argument("--repo-root", type=Path, default=Path("."),
                        help="repository root that cited paths are relative to")
    parser.add_argument("--warn-only", action="store_true", help="print findings and exit 0")
    parser.add_argument("--selftest", action="store_true",
                        help="assemble fixtures at runtime and prove this gate can fail")
    args = parser.parse_args(argv)

    if args.selftest:
        return selftest()

    repo_root = args.repo_root.resolve()
    code, findings, n_docs, n_cites = run(args.root, repo_root)

    if findings:
        label = "WARNING" if args.warn_only else "ERROR"
        for f in findings:
            print(f"{label}: {f}", file=sys.stderr)
        by_kind: dict[str, int] = {}
        for f in findings:
            by_kind[f.kind] = by_kind.get(f.kind, 0) + 1
        print(f"\nverify-document-status-consistency: FAILED — "
              + ", ".join(f"{v} {k.lower()}" for k, v in sorted(by_kind.items()))
              + f", across {n_cites} resolved citation(s) in {n_docs} document(s)."
              + (" Exiting 0: --warn-only." if args.warn_only else ""), file=sys.stderr)
        return 0 if args.warn_only else code

    print(f"verify-document-status-consistency: OK — {n_cites} resolved status citation(s) "
          f"across {n_docs} document(s): every one agrees with the cited document's own Status "
          f"line.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
