#!/usr/bin/env python3
"""An `A-nnn` assumption id introduced as NEW in a TAD must not already be allocated in the
paired Dev Summary's §10 register.

WHY THIS EXISTS
---------------
`IMP-0792`. TAD Revision 9 (ADR-049) introduced the `range()`/`addToTime()`/bare-component
`formatDateTime()` platform-contract question as **`A-FLOW-13`, NEW, OPEN**, four times.
`A-FLOW-13` was already allocated — and still OPEN — in
`docs/development/trustee-portal-visual-refresh-dev-summary.md` §10, for an entirely unrelated
question: whether `result()` called with a `Switch`/`If` action's own name resolves the way
Microsoft documents it for `Scope`/`For_each`/`Until`.

The structural cause is an ordering one, and it will recur without a gate. The register is
`development-agent`'s file and is written **after** the TAD names a marker, so it is the
higher-frequency writer — one row per dev dispatch — while the TAD is revised far less often.
`architect-agent` allocates the next id **it can see in the TAD itself** and cannot see that a
later dev dispatch has already taken it. Neither desk is ever in a position to notice.

Had it not been caught by hand, two independently-closing assumptions would have merged under one
id: the register row would have been corrupted, and closing either would have read as closing both.

WHAT IT CHECKS, AND WHY THIS SHAPE
----------------------------------
For each `docs/architecture/<slug>-architecture.md` with a paired
`docs/development/<slug>-dev-summary.md`:

    an id the TAD marks NEW, which already has a definition ROW in the paired register,
    is a collision.

Both halves are **values**, not prose semantics: a `NEW` marker next to an id, and a markdown
table row whose first cell is that id. Nothing here reads what either row *means*.

THE DESIGN WAS CHOSEN BY MEASUREMENT, NOT BY TASTE
--------------------------------------------------
The obvious alternative — *"an id with a definition row in BOTH documents"* — was measured over
the same corpus first and is **100% false**. It finds exactly one id, `A-FLOW-08`, whose TAD row
reads *"RESOLVED. Replaced by A-FLOW-11"*: a resolution cross-reference, which is the register
working exactly as intended. A TAD legitimately carries rows about ids the register owns; what it
must not do is hand a **new** question an id that is already taken.

    Design A ("def row in both documents")  : 1 finding, 0 true positives
    Design B ("marked NEW, already has a row"): 1 finding, 1 true positive   <- shipped

WHAT IT DOES NOT COVER
----------------------
This depends on the `NEW` marker being written. An architect who allocates a taken id and does not
mark it NEW is invisible here, and that is an honest limit rather than an oversight: without the
marker there is no value to compare, and the only remaining signal is whether two prose
descriptions mean the same thing — the instrument this project has measured at 48-100% false five
times (`IMP-0422`). The authoring-side grep in `agents/architect-agent.md` is what covers that
half; this gate covers the half a machine can settle.

It also cannot fire before both documents exist. A collision is created at TAD-authoring time and
detected at build time, so this gate shortens the feedback loop — it does not close it.

Run:
    python3 scripts/verify-assumption-id-collisions.py
    python3 scripts/verify-assumption-id-collisions.py --selftest
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lib.gate_baseline import BaselineError, load_baselines  # noqa: E402

GATE = "assumption-id-collisions"
ARCH_DIR = "docs/architecture"
DEV_DIR = "docs/development"
ARCH_SUFFIX = "-architecture.md"
DEV_SUFFIX = "-dev-summary.md"

# A markdown table row whose FIRST cell is the id: `| A-FLOW-13 |`, `| **A-FLOW-13** |`,
# `| `A-FLOW-13` |`. That is a DEFINITION of the id, as opposed to a mention in prose.
DEF_ROW = re.compile(r"^\|\s*\**\s*`?(A-[A-Z0-9]+-\d+)`?\s*\**\s*\|")

# The id introduced as NEW: "`A-FLOW-13`, NEW", "**A-FLOW-13**, NEW", "A-FLOW-13 NEW".
NEW_MARK = re.compile(r"`?\**(A-[A-Z0-9]+-\d+)\**`?[^A-Za-z0-9]{0,4}\bNEW\b")


def definition_rows(text: str) -> set[str]:
    """Ids this document DEFINES — first cell of a markdown table row."""
    return {m.group(1) for m in (DEF_ROW.match(line) for line in text.splitlines()) if m}


def introduced_as_new(text: str) -> set[str]:
    """Ids this document introduces as NEW."""
    return {m.group(1) for m in NEW_MARK.finditer(text)}


def pairs(repo: pathlib.Path) -> list[tuple[str, pathlib.Path, pathlib.Path]]:
    """Every (slug, TAD, dev-summary) where BOTH documents exist."""
    out = []
    arch_dir = repo / ARCH_DIR
    if not arch_dir.is_dir():
        return out
    for tad in sorted(arch_dir.glob(f"*{ARCH_SUFFIX}")):
        slug = tad.name[: -len(ARCH_SUFFIX)]
        dev = repo / DEV_DIR / f"{slug}{DEV_SUFFIX}"
        if dev.exists():
            out.append((slug, tad, dev))
    return out


def run(repo: pathlib.Path) -> tuple[list[str], list[str], int]:
    """Returns (findings, baselined, pairs_examined). Raises BaselineError on a bad baseline."""
    baseline = load_baselines(repo, GATE)
    findings: list[str] = []
    baselined: list[str] = []
    claimed: set[str] = set()
    examined = 0

    for slug, tad, dev in pairs(repo):
        examined += 1
        tad_text = tad.read_text(encoding="utf-8", errors="replace")
        dev_text = dev.read_text(encoding="utf-8", errors="replace")
        allocated = definition_rows(dev_text)
        for aid in sorted(introduced_as_new(tad_text) & allocated):
            key = f"{slug}:{aid}"
            msg = (
                f"{tad.relative_to(repo)}: introduces `{aid}` as NEW, but that id already has a "
                f"register row in {dev.relative_to(repo)} §10. Two independently-closing "
                f"assumptions under one id corrupt the register — closing either reads as closing "
                f"both. Allocate the next id free across BOTH documents (IMP-0792)."
            )
            if baseline.excuses(key):
                claimed.add(key)
                baselined.append(msg + baseline.cite(key))
            else:
                findings.append(msg)

    baseline.note_claimed(claimed)
    for stale in baseline.unused:
        baselined.append(
            f"STALE BASELINE: '{stale}' matches no finding this run. The debt was paid and the "
            f"baseline not removed — delete the entry from config/gate-baselines.json."
        )
    return findings, baselined, examined


def selftest() -> int:
    import tempfile

    ok = True

    def check(why: str, cond: bool, detail: str = "") -> None:
        nonlocal ok
        ok &= cond
        print(f"  {'PASS' if cond else 'FAIL'}  {why}" + (f" — {detail}" if detail else ""))

    def build(root: pathlib.Path, tad: str, dev: str, baselines: list | None = None) -> None:
        (root / ARCH_DIR).mkdir(parents=True, exist_ok=True)
        (root / DEV_DIR).mkdir(parents=True, exist_ok=True)
        (root / "config").mkdir(parents=True, exist_ok=True)
        (root / ARCH_DIR / f"demo{ARCH_SUFFIX}").write_text(tad)
        (root / DEV_DIR / f"demo{DEV_SUFFIX}").write_text(dev)
        if baselines is not None:
            (root / "config" / "gate-baselines.json").write_text(
                json.dumps({"baselines": baselines})
            )

    print("assumption-id-collisions selftest")

    with tempfile.TemporaryDirectory() as td:
        root = pathlib.Path(td)
        build(root, "The mechanism (`A-FLOW-13`, NEW, OPEN) is unverified.\n",
              "| A-FLOW-13 | result() over a Switch | OPEN |\n")
        f, b, n = run(root)
        check("a NEW id that already has a register row FAILS", len(f) == 1 and n == 1,
              f"{len(f)} finding(s)")

    with tempfile.TemporaryDirectory() as td:
        root = pathlib.Path(td)
        build(root, "The mechanism (`A-FLOW-99`, NEW, OPEN) is unverified.\n",
              "| A-FLOW-13 | result() over a Switch | OPEN |\n")
        f, _, _ = run(root)
        check("a NEW id that is genuinely free PASSES", not f, f"{len(f)} finding(s)")

    with tempfile.TemporaryDirectory() as td:
        root = pathlib.Path(td)
        # The Design A false positive: a TAD row ABOUT an id the register owns, not marked NEW.
        build(root, "| **A-FLOW-08** | **RESOLVED.** Replaced by A-FLOW-11 |\n",
              "| A-FLOW-08 | the negative platform fact | OPEN |\n")
        f, _, _ = run(root)
        check("a RESOLVED cross-reference row is NOT a collision", not f,
              "this is the case that made Design A 100% false")

    with tempfile.TemporaryDirectory() as td:
        root = pathlib.Path(td)
        build(root, "The mechanism (`A-FLOW-13`, NEW) is unverified.\n",
              "| A-FLOW-13 | result() over a Switch |\n",
              baselines=[{"gate": GATE, "matches": "demo:A-FLOW-13", "reason": "pre-existing",
                          "owner": "architect-agent", "clears_when": "the TAD is revised",
                          "expires": "2099-01-01", "finding": "IMP-0792"}])
        f, b, _ = run(root)
        check("a baselined collision is SUPPRESSED but still REPORTED",
              not f and len(b) == 1, f"{len(f)} finding(s), {len(b)} baselined")

    with tempfile.TemporaryDirectory() as td:
        root = pathlib.Path(td)
        build(root, "The mechanism (`A-FLOW-13`, NEW) is unverified.\n",
              "| A-FLOW-13 | result() over a Switch |\n",
              baselines=[{"gate": GATE, "matches": "demo:A-FLOW-13", "reason": "pre-existing",
                          "owner": "architect-agent", "clears_when": "the TAD is revised",
                          "expires": "2020-01-01", "finding": "IMP-0792"}])
        try:
            run(root)
            check("an EXPIRED baseline FAILS", False)
        except BaselineError:
            check("an EXPIRED baseline FAILS", True, "suppression is dated, not permanent")

    with tempfile.TemporaryDirectory() as td:
        root = pathlib.Path(td)
        (root / ARCH_DIR).mkdir(parents=True)
        (root / ARCH_DIR / f"orphan{ARCH_SUFFIX}").write_text("(`A-FLOW-13`, NEW)\n")
        f, _, n = run(root)
        check("a TAD with no paired Dev Summary is skipped", not f and n == 0,
              "nothing to compare against")

    print(f"\nassumption-id-collisions selftest: {'OK' if ok else 'FAILED'} — 6 check(s); "
          f"the gate can fail.")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--repo", default=".")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    repo = pathlib.Path(args.repo).resolve()
    try:
        findings, baselined, examined = run(repo)
    except BaselineError as exc:
        print(f"assumption-id-collisions: FAILED — {exc}", file=sys.stderr)
        return 1

    for b in baselined:
        print("BASELINED: " + b)
    for f in findings:
        print("ID COLLISION: " + f, file=sys.stderr)

    if findings:
        print(
            f"\nassumption-id-collisions: FAILED — {len(findings)} collision(s) across "
            f"{examined} document pair(s).",
            file=sys.stderr,
        )
        return 1
    print(
        f"assumption-id-collisions: OK — {examined} document pair(s); every id introduced as NEW "
        f"in a TAD is free in the paired Dev Summary register"
        + (f" ({len(baselined)} baselined)." if baselined else ".")
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
