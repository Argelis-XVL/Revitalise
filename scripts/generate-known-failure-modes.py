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
MAX_PER_SECTION = 8

# Routing table: class_instance_of -> the section (i.e. the moment in the workflow where the
# lesson applies). Deterministic and reviewable; the improvement-agent edits this table when
# it introduces a new class, so a new class cannot land in no section at all.
SECTIONS: list[tuple[str, str, tuple[str, ...]]] = [
    (
        "before-build",
        "Before you execute a build config",
        ("gate-cannot-fail", "gate-scope-mismatch", "repo-path-contains-spaces",
         "test-coupled-to-absolute-counts", "two-invocation-paths-disagree"),
    ),
    (
        "before-authoring",
        "Before you hand-author a platform artefact",
        ("platform-contract-guessed-not-groundtruthed", "platform-field-length-limit-unenforced"),
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
        ("harness-blocks-destructive-call",),
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
         "status-claimed-above-verification-level"),
    ),
    # These two are about this system changing ITSELF rather than about delivery, so they
    # apply at a different moment: when a request arrives that is not a feature.
    (
        "before-extending",
        "Before you extend this system or accept a new kind of input",
        ("no-route-for-system-capability-request", "input-type-with-no-owning-agent"),
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


def render(rows: list[dict], generated: str) -> str:
    # Only APPLIED and NEW entries carry lessons forward. A finding the improvement-agent
    # reviewed and explicitly rejected must not keep teaching.
    live = [r for r in rows if r.get("status") in {"NEW", "APPLIED"} and r.get("lesson")]

    # Deduplicate on the lesson text: two findings with the same lesson are one line with a
    # recurrence count, which is the signal the promotion ladder acts on.
    by_lesson: dict[str, list[dict]] = defaultdict(list)
    for r in live:
        by_lesson[r["lesson"]].append(r)

    section_of: dict[str, str] = {}
    for key, _title, classes in SECTIONS:
        for c in classes:
            section_of[c] = key

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
        out.append("| Count | Class | Findings |")
        out.append("|---|---|---|")
        for cls, fs in recurring:
            ids = ", ".join(sorted(f["id"] for f in fs))
            out.append(f"| **x{len(fs)}** | `{cls}` | {ids} |")
        out.append("")

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


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--log", type=Path, default=LOG)
    p.add_argument("--out", type=Path, default=OUT)
    p.add_argument("--check", action="store_true", help="exit 1 if the written file is stale")
    p.add_argument("--stdout", action="store_true", help="print instead of writing")
    p.add_argument("--as-of", default=None, help="YYYY-MM-DD stamp (default: today)")
    args = p.parse_args(argv)

    try:
        rows = load(args.log)
    except (FileNotFoundError, ValueError) as exc:
        print(f"generate-known-failure-modes: {exc}", file=sys.stderr)
        return 2

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
