#!/usr/bin/env python3
"""Generate logs/known-failure-modes.md — the READ path of the self-learning loop.

Why this script exists
----------------------
This system never had a capture problem. build-agent and pipeline-agent already wrote
forensic-quality post-mortems: `logs/build.log` entries run to 300 words with confirmed
root causes, and build #6's manifest carried a structured
`defect_found_and_fixed_this_build` array with a `why_it_was_never_caught` field per
defect. Nothing ever read any of it back.

Those two agents were also the only ones in the roster whose activation loaded no
prior-experience input at all — not the deployment handover document, not their own logs,
not the assumption register. So every build re-entered the same minefield with no map, and
the map it drew on the way out went to a directory the next build overwrote.

The proof, in the reviewer's own words on 2026-08-17, about a procedure established the day
before: "yesterday you moved and got the certificate from the mac keychain. Make it so that
you can use that again."

This script turns the append-only log into something an agent can afford to read on every
activation: ONE page, deduplicated, ordered by recurrence, grouped by the moment in the
workflow where each lesson applies.

Why a generated digest and not the raw log
------------------------------------------
CLAUDE.md forbids re-reading files already in context and treats token cost as a first-class
constraint. A JSONL log that grows by ~20 entries a week cannot be read on every build. The
digest is capped, so its cost stays flat while the log behind it grows.

Usage
-----
    python3 scripts/generate-known-failure-modes.py            # writes logs/known-failure-modes.md
    python3 scripts/generate-known-failure-modes.py --check    # exit 1 if the file is stale
    python3 scripts/generate-known-failure-modes.py --stdout   # print, do not write

`--check` is what CI and the improvement-agent use: it regenerates in memory and compares,
so a log entry added without regenerating the digest is caught rather than silently ignored.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from collections import defaultdict
from pathlib import Path

LOG = Path("logs/improvement-log.jsonl")
OUT = Path("logs/known-failure-modes.md")

# Maximum lessons rendered per section. Anything beyond is COUNTED AND NAMED, never
# silently dropped — a digest that truncates in silence reads as "this is everything".
# RAISED FROM 8 TO 20 ON 2026-08-19. At 47 entries the `before-build` section held 17
# lessons and SHOWED EIGHT — in the one section build-agent reads first, on the one page it
# reads before its own config. The cap was written when the log had 26 entries and no section
# was near it; it silently became a filter on the most-used page in the system. A digest that
# drops more than half of its busiest section is not a checklist.
#
# 20 is chosen to be above the largest current section with room to grow, not as a permanent
# answer: the real fix when a section genuinely exceeds this is to SPLIT the section (a new
# moment in the workflow), not to raise the number again. The dropped-lesson note below stays,
# so hitting the cap is still visible rather than silent.
MAX_PER_SECTION = 20

# Routing table: class_instance_of -> the section (i.e. the moment in the workflow where the
# lesson applies). Deterministic and reviewable; the improvement-agent edits this table when
# it introduces a new class, so a new class cannot land in no section at all.
SECTIONS: list[tuple[str, str, tuple[str, ...]]] = [
    (
        "before-build",
        "Before you execute a build config",
        ("gate-cannot-fail", "gate-scope-mismatch", "repo-path-contains-spaces",
         "test-coupled-to-absolute-counts", "two-invocation-paths-disagree",
         # Added 2026-08-19 with IMP-0057. The mirror of gate-cannot-fail: a gate that
         # fires on nothing. Same section, because it is the same moment — you are about
         # to trust what a build gate just told you.
         "gate-fires-on-nothing"),
    ),
    (
        "before-authoring",
        "Before you hand-author a platform artefact",
        ("platform-contract-guessed-not-groundtruthed", "platform-field-length-limit-unenforced",
         # Added 2026-08-22 (improvement review 10). Both were landing in Unrouted, which by
         # that section's own words reaches nobody, while both apply at exactly this moment.
         # `platform-fact-groundtruthed` is the same question as its `-guessed-` sibling asked
         # from the other side — someone went and got the ground truth, and the next person
         # about to hand-author against that platform is who needs it (IMP-0185, IMP-0193,
         # IMP-0194, IMP-0195). `environment-feature-flag-undeclared` is a per-environment
         # product toggle that no solution source can carry and no script can read back
         # (IMP-0182).
         "platform-fact-groundtruthed", "environment-feature-flag-undeclared"),
    ),
    (
        "before-deploy",
        "Before you declare a deploy or an import successful",
        ("exit-zero-does-not-mean-created", "v3-does-not-imply-v4",
         "register-predicts-but-does-not-block"),
    ),
    (
        "before-success",
        "Before you report SUCCESS at all",
        ("no-assertion-on-shipped-content", "learning-substrate-destroyed"),
    ),
    (
        "operating",
        "Operating constraints of this environment",
        (
            "harness-blocks-destructive-call",
            "repo-path-contains-spaces",
            # Added 2026-08-24 (IMP-0253). Same shape as repo-path-contains-spaces: a local
            # fact about THIS machine that breaks a command assumed portable. It was landing in
            # Unrouted, inside an overflow of 33 lessons the digest names but does not print,
            # so the lesson reached the file and no reader.
            "instruction-untested-in-target-shell",
        ),
    ),
    # Added 2026-08-19. Three classes were landing in Unrouted — which reaches nobody at the
    # moment it applies — and all three are about the same moment: you are about to run
    # something somewhere it has never actually run. IMP-0048 (a certificate thumbprint
    # exported to a runner with an empty certificate store), IMP-0054 (a filename whose case
    # only resolves on a case-insensitive filesystem) and C-TECH-054's original incident (a
    # Windows-only PSDrive in a script bound for a Linux runner) are one question asked three
    # ways: does this work on the machine that will run it, as opposed to the one it was
    # written on?
    (
        "before-running-elsewhere",
        "Before you run something on a machine it has never run on",
        ("credential-not-on-the-machine-that-needs-it", "os-specific-assumption-untested",
         "agent-instructions-describe-a-topology-that-changed",
         # Added 2026-08-21 (improvement review 3). Both landed in the Unrouted section,
         # which reaches nobody, while their entire purpose is to be read at exactly this
         # moment — before a script is pointed at an environment it has not run against.
         # IMP-0145 (a settings placeholder known for a day and never fixed) and IMP-0146
         # (a provisioning identity with no application user in the target org).
         "config-placeholder-known-but-not-fixed",
         "provisioning-identity-not-onboarded-to-target-environment"),
    ),
    # Added 2026-08-18 (improvement review). Five lessons were landing in the Unrouted
    # section — which reaches nobody at the moment it applies — because the commercial and
    # self-change classes had no home. Section name and the first three classes are as
    # specified in docs/improvements/2026-08-18-project-management-system-redesign.md §5.2;
    # the last two are declared here ahead of the scripts that will emit them, so a finding
    # logged before that work lands still routes.
    (
        "before-commercial",
        "Before you bill an hour, accept a phase, or report status",
        ("baseline-restated-not-cited", "work-order-not-driven-by-contract",
         "instrument-exists-never-used", "billable-hour-without-resolving-evidence",
         "status-claimed-above-verification-level",
         # Added 2026-08-19 when the PM capability was built. `completion-claimed-not-verified`
         # is the spreadsheet form of exit-zero-does-not-mean-created and `invoiced-is-not-
         # completed` its commercial form; both apply at this moment, not at deploy time.
         "commercial-baseline-wrong", "completion-claimed-not-verified",
         "invoiced-is-not-completed", "double-billed-session",
         "contract-date-used-as-a-delivery-fact",
         "evidence-rule-satisfied-by-a-forward-reference"),
    ),
    # These two are about this system changing ITSELF rather than about delivery, so they
    # apply at a different moment: when a request arrives that is not a feature.
    (
        "before-extending",
        "Before you extend this system or accept a new kind of input",
        ("no-route-for-system-capability-request", "input-type-with-no-owning-agent",
         # Added 2026-08-19 with IMP-0059. Not about delivery — about the moment an agent
         # writes something a human has to act on.
         "output-shape-defeats-the-reader",
         # Added 2026-08-19 with IMP-0062.
         "test-seam-in-the-wrong-scope",
         # IMP-0034 — an agent's declared Knowledge to Load pointing at template scaffolding.
         # It sat in Unrouted from 2026-08-18 until 2026-08-19, which is exactly the failure
         # the Unrouted section exists to make visible.
         "declared-knowledge-source-is-empty"),
    ),
]

HEADER = """\
# Known Failure Modes

**GENERATED FILE — do not hand-edit.** Regenerate with
`python3 scripts/generate-known-failure-modes.py` after any change to
`logs/improvement-log.jsonl`. CI and the improvement-agent verify it is current with
`--check`.

Source: `logs/improvement-log.jsonl` ({n_entries} entries, {n_lessons} distinct lessons)
Generated: {generated}

## How to use this file

Read it **before** your own config or instruction set, and treat it as a checklist against
that config — not as background reading. Every line below is a defect that actually happened
on this project, with the finding ids that recorded it. A `x{{n}}` marker means that class has
now recurred {{n}} times, which is the system telling you a general gate is missing where an
instance patch was applied.

`build-agent` and `pipeline-agent` load this file on activation
(`agents/build-agent.md` step 0, `agents/pipeline-agent.md` step 0). Other agents load it
when their work touches a listed area.
"""

FOOTER = """\
---

## What this file cannot tell you

It records defects that have been **found**. The classes with the highest counts are the ones
this project has learned to look for — they are not necessarily the ones most likely to bite
next. A lesson's absence here is not evidence of safety; it is evidence that nobody has been
caught by it yet and written it down.

Full analysis of every entry, including why each was invisible to the gates that existed at
the time: `docs/improvements/2026-08-17-failure-analysis-and-self-learning-design.md`.
"""


def load(log_path: Path) -> list[dict]:
    if not log_path.exists():
        raise FileNotFoundError(f"{log_path} does not exist — nothing to generate from")
    rows = []
    for i, line in enumerate(log_path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{log_path}:{i} is not valid JSON: {exc}") from exc
    return rows


# ── Where a lesson actually renders, and by which mechanism (IMP-0198) ────────────────────
# THREE independent mechanisms decide a lesson's section, and they have a silent precedence:
#
#   1. `capability: true` on ANY finding sharing the lesson  → "Capabilities", always, whatever
#      the class says. This one is invisible from the class routing table below.
#   2. the SECTIONS routing table                            → that section
#   3. nothing matches                                       → "Unrouted"
#
# And a fourth, subtler one: a class named in TWO section tuples resolves to the LAST, because
# `section_of` is built by overwriting. `repo-path-contains-spaces` is in both `before-build`
# and `operating` today and renders only in `operating`.
#
# Improvement review 10 predicted the Unrouted section would fall 31 -> 26 by adding two classes
# to the table. Measured: 31 -> 30. Four of the five findings carried `capability: true` and had
# never been in Unrouted at all — mechanism 1 had already placed them, and nothing rendered said
# so. The recurring-classes table showed the class; it did not show where the class's lessons
# actually went. That is what these two functions exist to make visible.

CAPABILITY_SECTION = "Capabilities"
UNROUTED_SECTION = "Unrouted"


def build_section_of() -> dict[str, str]:
    """class_instance_of -> section key. Last tuple wins, which is mechanism 4 above."""
    section_of: dict[str, str] = {}
    for key, _title, classes in SECTIONS:
        for c in classes:
            section_of[c] = key
    return section_of


def duplicated_classes() -> dict[str, list[str]]:
    """Classes named in more than one section tuple, with every section that names them."""
    seen: dict[str, list[str]] = defaultdict(list)
    for key, _title, classes in SECTIONS:
        for c in classes:
            seen[c].append(key)
    return {c: keys for c, keys in seen.items() if len(keys) > 1}


def routing_of(rows: list[dict]) -> dict[str, dict[str, int]]:
    """For each class, how many of its LESSONS render in which section.

    Keyed by class, then by section key (or ``Capabilities`` / ``Unrouted``). Counts lessons,
    not findings, because a lesson is what the digest renders as a line.
    """
    live = [r for r in rows if r.get("status") in {"NEW", "APPLIED"} and r.get("lesson")]
    by_lesson: dict[str, list[dict]] = defaultdict(list)
    for r in live:
        by_lesson[r["lesson"]].append(r)

    section_of = build_section_of()
    out: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for lesson, findings in by_lesson.items():
        cls = findings[0].get("class_instance_of", "unclassified")
        if any(f.get("capability") for f in findings):
            where = CAPABILITY_SECTION
        else:
            where = section_of.get(cls) or UNROUTED_SECTION
        out[cls][where] += 1
    return {c: dict(v) for c, v in out.items()}


def renders_in(breakdown: dict[str, int]) -> str:
    """One compact cell naming every section a class's lessons render in, and how many."""
    parts = []
    for where, n in sorted(breakdown.items(), key=lambda kv: (-kv[1], kv[0])):
        parts.append(f"`{where}`" + (f" ×{n}" if n > 1 else ""))
    return ", ".join(parts)


def render(rows: list[dict], generated: str) -> str:
    # Only APPLIED and NEW entries carry lessons forward. A finding the improvement-agent
    # reviewed and explicitly rejected must not keep teaching.
    live = [r for r in rows if r.get("status") in {"NEW", "APPLIED"} and r.get("lesson")]

    # Deduplicate on the lesson text: two findings with the same lesson are one line with a
    # recurrence count, which is the signal the promotion ladder acts on.
    by_lesson: dict[str, list[dict]] = defaultdict(list)
    for r in live:
        by_lesson[r["lesson"]].append(r)

    section_of = build_section_of()

    grouped: dict[str, list[tuple[str, list[dict]]]] = defaultdict(list)
    capabilities: list[tuple[str, list[dict]]] = []
    unrouted: list[tuple[str, list[dict]]] = []

    for lesson, findings in by_lesson.items():
        if any(f.get("capability") for f in findings):
            capabilities.append((lesson, findings))
            continue
        cls = findings[0].get("class_instance_of", "")
        key = section_of.get(cls)
        if key is None:
            unrouted.append((lesson, findings))
        else:
            grouped[key].append((lesson, findings))

    def sort_key(item: tuple[str, list[dict]]) -> tuple[int, int, str]:
        _lesson, fs = item
        blockers = sum(1 for f in fs if f.get("severity") == "blocker")
        return (-len(fs), -blockers, fs[0]["id"])

    out: list[str] = [
        HEADER.format(n_entries=len(rows), n_lessons=len(by_lesson), generated=generated)
    ]

    # ── Recurring classes: the promotion-ladder signal, surfaced at the top ───────────
    # A class with n>=2 means an instance was patched where a general gate was needed. On
    # this project that is not hypothetical: the 256-char flow-description cap and the
    # 500-char setting-description cap were fixed by two separate scripts, and the "import
    # reported success but created nothing" class was rediscovered two days after its first
    # appearance because nothing generalised the first fix.
    by_class: dict[str, list[dict]] = defaultdict(list)
    for r in live:
        by_class[r.get("class_instance_of", "unclassified")].append(r)
    recurring = sorted(
        ((c, fs) for c, fs in by_class.items() if len(fs) >= 2),
        key=lambda kv: (-len(kv[1]), kv[0]),
    )
    if recurring:
        out.append("\n## Recurring classes — where a general gate is missing\n")
        out.append(
            "Each of these has happened more than once. Per "
            "`skills/how-to-promote-a-finding.md`, the second instance of a class may **not** "
            "get another instance-level patch: it must be generalised, and the instance gates "
            "retired.\n"
        )
        out.append(
            "**`Renders in` is where this class's lessons actually appear below** — not where "
            "the routing table says they should. A lesson whose finding carries "
            "`capability: true` renders under `Capabilities` whatever its class, so a class can "
            "sit in this table and have none of its lessons in the section you expect. Reading "
            "the class name alone and inferring a section is how one review predicted a digest "
            "delta of 31→26 and measured 31→30 (`IMP-0198`).\n"
        )
        routing = routing_of(rows)
        out.append("| Count | Class | Renders in | Findings |")
        out.append("|---|---|---|---|")
        for cls, fs in recurring:
            ids = ", ".join(sorted(f["id"] for f in fs))
            where = renders_in(routing.get(cls, {}))
            out.append(f"| **x{len(fs)}** | `{cls}` | {where} | {ids} |")
        out.append("")

        dupes = duplicated_classes()
        if dupes:
            listed = "; ".join(
                f"`{c}` → {', '.join(f'`{k}`' for k in keys)} (renders in `{keys[-1]}`)"
                for c, keys in sorted(dupes.items())
            )
            out.append(
                f"> **A class named in two sections renders only in the last one.** {listed}. "
                f"This is a silent precedence in the routing table, not a decision anything "
                f"records — fix it by naming the class once, in the section where the lesson "
                f"actually applies.\n"
            )

    def emit(title: str, items: list[tuple[str, list[dict]]], note: str = "") -> None:
        if not items:
            return
        items = sorted(items, key=sort_key)
        total_findings = sum(len(f) for _, f in items)
        out.append(f"\n## {title}\n")
        if note:
            out.append(f"{note}\n")
        plural = lambda n, w: f"{n} {w}" + ("" if n == 1 else "s")  # noqa: E731
        out.append(f"*{plural(len(items), 'lesson')} from {plural(total_findings, 'finding')}.*\n")
        shown = items[:MAX_PER_SECTION]
        for lesson, fs in shown:
            ids = ", ".join(sorted(f["id"] for f in fs))
            recur = f" **x{len(fs)}**" if len(fs) > 1 else ""
            out.append(f"- {lesson}{recur}  \n  <sub>{ids}</sub>")
        dropped = items[MAX_PER_SECTION:]
        if dropped:
            names = ", ".join(sorted(f["id"] for _, fs in dropped for f in fs))
            out.append(
                f"\n> **{len(dropped)} further lesson(s) in this section are not shown** "
                f"(cap: {MAX_PER_SECTION}). Findings: {names}. "
                f"Read them in `logs/improvement-log.jsonl`, or raise the cap in "
                f"`scripts/generate-known-failure-modes.py`."
            )
        out.append("")

    for key, title, _classes in SECTIONS:
        emit(title, grouped.get(key, []))

    emit(
        "Capabilities established in earlier sessions",
        capabilities,
        "These are things that WORK and were once lost. Do not ask the reviewer to re-supply "
        "them.",
    )

    if unrouted:
        emit(
            "Unrouted — no section assigned",
            unrouted,
            "> These findings' `class_instance_of` values are missing from the routing table "
            "in `scripts/generate-known-failure-modes.py`. Add them, so the lesson reaches "
            "the agent at the moment it applies.",
        )

    out.append("")
    out.append(FOOTER)
    return "\n".join(out)


def print_routing(rows: list[dict]) -> int:
    """`--routing`: the per-class breakdown IMP-0198 asked for.

    The question this answers, which nothing answered before: *if I add this class to the
    routing table, what actually moves?* The honest answer is often "nothing", because the
    lessons are already placed by the capability flag.
    """
    routing = routing_of(rows)
    section_of = build_section_of()
    dupes = duplicated_classes()

    width = max((len(c) for c in routing), default=20)
    print(f"{'CLASS'.ljust(width)}  {'IN TABLE?':<10}  RENDERS IN")
    print(f"{'-' * width}  {'-' * 10}  {'-' * 40}")

    movable: list[str] = []
    for cls in sorted(routing, key=lambda c: (-sum(routing[c].values()), c)):
        breakdown = routing[cls]
        in_table = "yes" if cls in section_of else "NO"
        cells = ", ".join(f"{w}×{n}" for w, n in
                          sorted(breakdown.items(), key=lambda kv: (-kv[1], kv[0])))
        print(f"{cls.ljust(width)}  {in_table:<10}  {cells}")
        if breakdown.get(UNROUTED_SECTION):
            movable.append(f"{cls} ({breakdown[UNROUTED_SECTION]} lesson(s))")

    print()
    if movable:
        print("Adding these classes to SECTIONS would move a lesson out of Unrouted:")
        for m in sorted(movable):
            print(f"  - {m}")
    else:
        print("Every lesson is placed. Adding any class to SECTIONS would move nothing.")

    capability_only = [c for c, b in routing.items()
                       if CAPABILITY_SECTION in b and c not in section_of]
    if capability_only:
        print()
        print("These classes are NOT in the routing table and still render nowhere near "
              "Unrouted,")
        print("because the capability flag placed their lessons first — adding them to "
              "SECTIONS moves nothing:")
        for c in sorted(capability_only):
            print(f"  - {c} → {renders_in(routing[c]).replace('`', '')}")

    if dupes:
        print()
        print("Classes named in more than one section (the LAST one wins, silently):")
        for c, keys in sorted(dupes.items()):
            print(f"  - {c}: {', '.join(keys)}  → renders in {keys[-1]}")

    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--log", type=Path, default=LOG)
    p.add_argument("--out", type=Path, default=OUT)
    p.add_argument("--check", action="store_true", help="exit 1 if the written file is stale")
    p.add_argument("--stdout", action="store_true", help="print instead of writing")
    p.add_argument("--as-of", default=None, help="YYYY-MM-DD stamp (default: today)")
    p.add_argument("--routing", action="store_true",
                   help="print where every class's lessons render, and by which mechanism, "
                        "then exit. Answers 'will adding this class to the routing table "
                        "move anything?' without reading the generator (IMP-0198)")
    args = p.parse_args(argv)

    try:
        rows = load(args.log)
    except (FileNotFoundError, ValueError) as exc:
        print(f"generate-known-failure-modes: {exc}", file=sys.stderr)
        return 2

    if args.routing:
        return print_routing(rows)

    # --check must not depend on the date, or the file would be "stale" every midnight.
    # It compares everything except the Generated: line.
    stamp = args.as_of or _dt.date.today().isoformat()
    text = render(rows, stamp)

    if args.stdout:
        print(text)
        return 0

    if args.check:
        if not args.out.exists():
            print(f"generate-known-failure-modes: {args.out} does not exist — run without "
                  f"--check to create it", file=sys.stderr)
            return 1

        def strip_stamp(s: str) -> str:
            return "\n".join(l for l in s.splitlines() if not l.startswith("Generated:"))

        if strip_stamp(args.out.read_text(encoding="utf-8")) != strip_stamp(text):
            print(
                f"generate-known-failure-modes: {args.out} is STALE relative to {args.log}.\n"
                f"  Run: python3 scripts/generate-known-failure-modes.py\n"
                f"  A log entry that never reaches the digest teaches nobody.",
                file=sys.stderr,
            )
            return 1
        print(f"generate-known-failure-modes: {args.out} is current ({len(rows)} entries).")
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    lessons = len({r["lesson"] for r in rows if r.get("lesson")})
    print(
        f"generate-known-failure-modes: wrote {args.out} — {len(rows)} entries, "
        f"{lessons} distinct lessons, {len(text.splitlines())} lines."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
