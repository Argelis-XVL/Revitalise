#!/usr/bin/env python3
"""Score a LIVE AI Builder run of the synthetic corpus against the gold spans (WBS 5.2).

Run:
  python3 src/tests/narrative/score_live_run.py --results <dir> [--offsets utf16|codepoints] [--out report.md]

A-NS-5: the model is called with language "en" for UK English text (E2 lists "English" only).

<dir> holds one file per corpus sample, named <id>.json (S01.json ...), each containing the raw
response of the prebuilt entity extraction model for that sample's PLAIN text (markup removed - use
--emit-inputs to write those texts). Accepted shapes, both taken from the platform's own run data
specification (msdyn_aitemplate EntityExtraction, read from DEV 2026-10-05, E1):
  {"result": {"entities": [{"type", "value", "startIndex", "length", "score"}, ...]}}
  [{"type", "value", "startIndex", "length", "score"}, ...]

What it reports, per category, in two layers:
  MODEL ONLY   - what the prebuilt model found on its own (mapped types, before the UK rules);
                 this is the 5.2 deliverable "detection accuracy, gaps, false positives/negatives".
  MODEL+RULES  - what the v0.1 rules produce end to end (redaction_reference.redact_column).
  MODEL+FLOW   - what the production flow produces (rules v0.2: shape detectors, in-flow refinement,
                 residue checks; redaction_reference.flow_scrub_column). This is the layer wbs:5.7
                 calibrates against.
A gold span counts as found when one final span of the SAME category covers it entirely.
It also lists every distinct `type` string the model returned - the evidence that closes A-NS-1.

Exit 0 always, unless --min-recall is given and MODEL+RULES recall for any category is below it.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import redaction_reference as rr  # noqa: E402
from test_redaction_reference import SAMPLES, parse_markup  # noqa: E402


def load_entities(path: Path, plain: str, offsets: str) -> list[rr.PrebuiltEntity]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    items = raw["result"]["entities"] if isinstance(raw, dict) else raw
    out = []
    for e in items:
        start, length = int(e["startIndex"]), int(e["length"])
        if offsets == "utf16":
            end = rr.utf16_to_codepoints(plain, start + length)
            start = rr.utf16_to_codepoints(plain, start)
            length = end - start
        out.append(rr.PrebuiltEntity(str(e["type"]), start, length, float(e["score"])))
    return out


def load_flow_entities(path: Path, plain: str, offsets: str) -> list[rr.ExtractorEntity]:
    """The same entities with their values, for the flow model (rules v0.2, ADR-071)."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    items = raw["result"]["entities"] if isinstance(raw, dict) else raw
    out = []
    for e, p in zip(items, load_entities(path, plain, offsets)):
        out.append(rr.ExtractorEntity(str(e["type"]), str(e.get("value", plain[p.start:p.start + p.length])),
                                      p.start, p.length, p.score))
    return out


FLOW_CATEGORY = {"N": "NAME", "F": "FAMILY MEMBER", "G": "GP PRACTICE", "S": "ADDRESS", "P": "PHONE",
                 "E": "EMAIL", **{str(i): rr.AGE_CATEGORY for i in range(9)}}


def flow_detections(merged) -> list[rr.Detection]:
    return [rr.Detection(m["start"], m["end"] - m["start"], FLOW_CATEGORY[m["code"]], m["score"], "flow") for m in merged]


def covered(gold, dets) -> bool:
    s, n, c = gold
    return any(d.category == c and d.start <= s and d.end >= s + n for d in dets)


def overlaps_gold(d, golds) -> bool:
    return any(d.category == c and d.start < s + n and s < d.end for s, n, c in golds)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", type=Path)
    ap.add_argument("--offsets", choices=["utf16", "codepoints"], default="utf16")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--min-recall", type=float)
    ap.add_argument("--emit-inputs", type=Path, help="write <id>.txt plain inputs here and exit")
    a = ap.parse_args()

    if a.emit_inputs:
        a.emit_inputs.mkdir(parents=True, exist_ok=True)
        for s in SAMPLES:
            (a.emit_inputs / f"{s['id']}.txt").write_text(parse_markup(s["text"])[0], encoding="utf-8")
        print(f"wrote {len(SAMPLES)} inputs to {a.emit_inputs}")
        return 0
    if not a.results:
        ap.error("--results is required unless --emit-inputs is given")

    tally = {layer: defaultdict(Counter) for layer in ("model", "full", "flow")}
    types_seen: Counter = Counter()
    lines, missing = [], []
    # Rev 20: what production runs - the seed postcode register and the floor word lists (ADR-073, ADR-074)
    FLOW_CONTEXT = rr.run_context({})
    for s in SAMPLES:
        plain, gold = parse_markup(s["text"])
        f = a.results / f"{s['id']}.json"
        if not f.exists():
            missing.append(s["id"])
            continue
        ents = load_entities(f, plain, a.offsets)
        types_seen.update(e.type for e in ents)
        model_only = rr.merge(plain, rr.refine(plain, rr.map_prebuilt(ents).detections))
        full = rr.redact_column(plain, ents)
        flow_ents = load_flow_entities(f, plain, a.offsets)
        flow = rr.flow_scrub_column("c", plain, None, lambda _w, fe=flow_ents: fe, FLOW_CONTEXT)
        flow_dets = flow_detections(flow.merged)
        for layer, dets in (("model", model_only), ("full", full.detections), ("flow", flow_dets)):
            for g in gold:
                tally[layer][g[2]]["tp" if covered(g, dets) else "fn"] += 1
            for d in dets:
                if not overlaps_gold(d, gold):
                    tally[layer][d.category]["fp"] += 1
        ok = full.redacted == s["expected"]
        fok = flow.redacted == s["expected"]
        lines.append(f"| {s['id']} | {'match' if ok else 'DIFFERS'} | {'match' if fok else 'DIFFERS'} | "
                     f"{', '.join(r.split(':')[0] for r in flow.reasons) or '-'} | "
                     f"{flow.redacted if not fok else ''} |")

    out = ["# Live AI Builder run - scored against the v0.1 corpus", ""]
    if missing:
        out += [f"**Samples with no result file:** {', '.join(missing)}", ""]
    out += ["## Type strings returned by the model (closes A-NS-1)", ""]
    out += [f"- `{t}` x{n}" + ("" if t in rr.PREBUILT_TYPE_HANDLING else "  **UNMAPPED**")
            for t, n in sorted(types_seen.items())] or ["- none"]
    worst = 1.0
    for layer, title in (("model", "Model only"), ("full", "Model + v0.1 rules"),
                         ("flow", "Model + flow (rules v0.2, ADR-071) - what production runs")):
        out += ["", f"## {title}", "", "| Category | Found | Missed | False positives | Recall |", "|---|---|---|---|---|"]
        for cat in sorted(set(tally[layer]) | {c for c in rr.LABEL} | {rr.AGE_CATEGORY}):
            c = tally[layer][cat]
            total = c["tp"] + c["fn"]
            recall = c["tp"] / total if total else None
            if layer in ("full", "flow") and recall is not None:
                worst = min(worst, recall)
            out.append(f"| {cat} | {c['tp']} | {c['fn']} | {c['fp']} | "
                       f"{'n/a' if recall is None else f'{recall:.0%}'} |")
    out += ["", "## Per sample (end to end)", "",
            "| Sample | v0.1 rules | Flow | Flow reasons | Flow text when it differs |",
            "|---|---|---|---|---|"] + lines
    report = "\n".join(out) + "\n"
    if a.out:
        a.out.write_text(report, encoding="utf-8")
    print(report)
    if a.min_recall is not None and worst < a.min_recall:
        print(f"FAIL: lowest category recall {worst:.0%} < {a.min_recall:.0%}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
