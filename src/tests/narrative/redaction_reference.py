#!/usr/bin/env python3
"""Reference implementation of the free-text redaction rules, v0.1 (WBS 5.1 / 5.2).

WHAT THIS IS. The executable form of docs/development/revitalise-redaction-rules.md. It is the
ORACLE the narrative-scrubbing flow (WBS 5.3) must agree with, and the scorer that turns a live
AI Builder run into detection accuracy (WBS 5.2). It is NOT production code: nothing here runs in
Power Automate. Power Automate's expression language has no regular expressions, so the
deterministic rules below cannot simply be transcribed into the flow; how they are hosted is an
open architecture decision (see the rules document, section 9, and the CASCADE in the Dev Summary).

WHAT IT GUARANTEES, and the tests in test_redaction_reference.py prove each one:
  * replacement is by OFFSET, never by searching for the detected value, so a name that is also a
    common word ("Will", "Hope") is replaced only where it was detected;
  * overlapping and nested detections are merged into one span BEFORE any replacement;
  * replacements are applied from the END of the text backwards, so no earlier offset moves;
  * text longer than the model's input limit is split into overlapping windows and detections are
    mapped back to whole-text offsets;
  * the record-level decision fails CLOSED: any error, missing threshold, low score, over-length
    output or empty detection set sends the record to manual review with released = False;
  * the decision object never contains any part of the input text.

Scope: DIRECT identifiers only (reviewer decision, Xander Lykopoulos, 2026-10-05). Indirect
identifiers - family composition, household, rare circumstances - are OUT of v0.1; the extension
point is INDIRECT_RULES at the bottom of this file.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

# ── Labels (rules doc section 3) ────────────────────────────────────────────────────────────────
LABEL = {
    "NAME": "[NAME]",
    "FAMILY MEMBER": "[FAMILY MEMBER]",
    "GP PRACTICE": "[GP PRACTICE]",
    "ADDRESS": "[ADDRESS]",
    "PHONE": "[PHONE]",
    "EMAIL": "[EMAIL]",  # not in FR-026's list; the prebuilt model returns Email (rules doc 3.2)
}
AGE_CATEGORY = "AGE"  # FR-027: rendered as "[AGE <band>]", band text from the rev_agerange option set

# When merged spans disagree on category, the earlier entry wins (rules doc section 5.2).
# A span that contains a practice name is a practice; an address that contains a name is an address.
PRECEDENCE = ["ADDRESS", "GP PRACTICE", "EMAIL", "PHONE", "FAMILY MEMBER", "NAME", AGE_CATEGORY]

# ── AI Builder prebuilt entity extraction: type string -> handling (rules doc section 4) ───────
# A-NS-1: the literal `type` strings below are GUESSED (E3/E4). Microsoft's documentation lists
# display names ("Person name", "Phone number") and gives "DateTime" and "Organization" as output
# examples, so the strings are probably the PascalCase forms used here - but no run in this tenant
# has returned them yet. One live run of corpus sample S01 settles it. Until then an unknown type
# string is treated as IN SCOPE for review (UNMAPPED_TYPE_POLICY) rather than silently retained.
PREBUILT_TYPE_HANDLING = {
    "PersonName": "NAME",          # refined to FAMILY MEMBER by kinship context (section 5.1)
    "Organization": "ORG",         # redacted only when it is a GP practice (section 5.1)
    "PhoneNumber": "PHONE",        # A-NS-4: documented as US-format only (E2) - UK rules below
    "StreetAddress": "ADDRESS",    # documented as US-format only - see UK rules below
    "ZipCode": "ADDRESS",          # documented as US-format only
    "Email": "EMAIL",
    "Age": AGE_CATEGORY,
    # Retained in v0.1: not direct identifiers, or needed by trustees (FR-028).
    "City": None, "State": None, "Country": None, "CountryRegion": None, "Continent": None,
    "DateTime": None, "Duration": None, "Money": None, "Number": None, "Ordinal": None,
    "Percentage": None, "Boolean": None, "Color": None, "Event": None, "Language": None,
    "Speed": None, "Temperature": None, "Weight": None, "URL": None,
}
UNMAPPED_TYPE_POLICY = "review"  # an unrecognised type string forces review; never silently drop it

AGE_BANDS = [  # rev_agerange option labels, verbatim (OptionSets/rev_agerange.xml)
    (0, 17, "Under 18"), (18, 24, "18 to 24"), (25, 34, "25 to 34"), (35, 44, "35 to 44"),
    (45, 54, "45 to 54"), (55, 64, "55 to 64"), (65, 74, "65 to 74"), (75, 200, "75 and over"),
]

PREBUILT_MAX_CHARS = 5000   # E2: "Documents can't exceed 5,000 characters" (A-NS-3: and what happens beyond it is unverified)
WINDOW_OVERLAP = 200        # longest entity this splitter guarantees to see whole
REDACTED_MAX_CHARS = 4000   # MaxLength of every ...redacted counterpart column (Entity.xml, E1 source)


@dataclass(frozen=True)
class Detection:
    start: int            # code-point offset into the WHOLE text (see utf16_to_codepoints)
    length: int
    category: str         # a key of LABEL, AGE_CATEGORY, or "ORG" before refinement
    score: float          # 0..1; deterministic rules use 1.0
    source: str           # "aibuilder" | "rule"

    @property
    def end(self) -> int:
        return self.start + self.length


# ── Offsets: AI Builder vs Python ──────────────────────────────────────────────────────────────
def utf16_to_codepoints(text: str, utf16_index: int) -> int:
    """Convert a UTF-16 code-unit offset into a code-point offset.

    A-NS-2: AI Builder is a .NET service and Power Automate's substring() counts UTF-16 code
    units, so its offsets are assumed to be UTF-16. Python indexes code points. The two differ
    only after a character outside the Basic Multilingual Plane (an emoji, for example) - which is
    exactly what corpus sample S16 contains. The flow itself never needs this conversion; the
    scorer does.
    """
    units = 0
    for i, ch in enumerate(text):
        if units >= utf16_index:
            return i
        units += 2 if ord(ch) > 0xFFFF else 1
    return len(text)


# ── Deterministic rules (rules doc section 6) ──────────────────────────────────────────────────
_KIN = (r"(?:husband|wife|partner|spouse|fianc[eé]e?|boyfriend|girlfriend|son|daughter|child|"
        r"children|kids|mum|mom|mother|mam|dad|father|parents?|brother|sister|siblings?|twin|"
        r"grandson|granddaughter|grandchild(?:ren)?|grandmother|grandfather|gran|grandma|nan|"
        r"nana|grandad|granddad|grandpa|aunt|auntie|uncle|niece|nephew|cousin|"
        r"step(?:son|daughter|mother|father|mum|dad)|(?:mother|father|son|daughter|sister|"
        r"brother)-in-law)")
_POSS = r"(?:my|our|his|her|their)"
_KIN_BEFORE = re.compile(
    _POSS + r"\s+(?:(?:late|elder|eldest|older|younger|youngest|little|big|twin|adult|grown-up|"
    r"disabled|only)\s+)*" + _KIN + r"\b[\s,:\-]*(?:(?:called|named|is)\s+)?$",
    re.IGNORECASE)
_KIN_AFTER = re.compile(r"^(?:['’]s)?\s*[,(\-–]\s*" + _POSS + r"\s+(?:\w+\s+)?" + _KIN + r"\b",
                        re.IGNORECASE)
_LIST_JOIN = re.compile(r"^\s*(?:,\s*(?:and\s+|&\s*)?|and\s+|&\s*)$", re.IGNORECASE)

_GP_SUFFIX = (r"(?:Surgery|Medical\s+Centre|Medical\s+Center|Health\s+Centre|Medical\s+Practice|"
              r"Group\s+Practice|Family\s+Practice|Doctors['’]?\s+Surgery)")
GP_PRACTICE_VALUE = re.compile(r"\b" + _GP_SUFFIX + r"\s*$", re.IGNORECASE)
GP_PRACTICE_RULE = re.compile(
    r"(?:\b(?:Dr|Doctor)\.?\s+)?(?:[A-Z][\w'’\-]*\s+){1,4}" + _GP_SUFFIX + r"\b")

_STREET_TYPES = (r"(?:Road|Street|Lane|Avenue|Close|Drive|Way|Crescent|Grove|Place|Terrace|Court|"
                 r"Gardens|Row|Hill|Walk|Square|Mews|Rise|Park|View|Green)")
_POSTCODE = (r"(?:GIR ?0AA|[A-PR-UWYZ][A-HK-Y]?\d[A-Z\d]? ?\d[ABD-HJLNP-UW-Z]{2})")
UK_POSTCODE_RULE = re.compile(r"\b" + _POSTCODE + r"\b", re.IGNORECASE)
UK_STREET_RULE = re.compile(
    r"\b(?:(?:Flat|Apartment)\s+\d+[A-Za-z]?,?\s+)?\d{1,4}[A-Za-z]?,?\s+(?:[A-Z][a-z'’]+\s+){1,3}"
    + _STREET_TYPES + r"\b(?:,\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)?(?:,?\s+" + _POSTCODE + r")?")
# Unnumbered streets use a narrower type list: "Park", "Hill", "Green" and "View" without a house
# number are as often a destination ("a day in Hyde Park") as an address.
UK_UNNUMBERED_STREET_RULE = re.compile(
    r"\b(?:on|in|at|off|along|near)\s+((?:[A-Z][a-z'’]+\s+){1,3}"
    r"(?:Road|Street|Lane|Avenue|Close|Drive|Crescent|Terrace|Grove|Mews))\b")
EMAIL_RULE = re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")
UK_PHONE_CANDIDATE = re.compile(
    r"(?<![\w+])(?:\+44\s?(?:\(0\)\s?)?|\(?0)\d{2,4}\)?[\s\-]?\d{3,4}[\s\-]?\d{3,4}(?!\d)")
_NUMWORD = (r"(?:(?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)(?:[\s\-]"
            r"(?:one|two|three|four|five|six|seven|eight|nine))?|one|two|three|four|five|six|seven|"
            r"eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|"
            r"nineteen)")
# "years old" is REQUIRED: "for five years" is a duration, not an age, and must be retained.
AGE_RULE = re.compile(
    r"\b(\d{1,3}|" + _NUMWORD + r")\s*-?\s*(?:years?|yrs?)\s*-?\s*old\b", re.IGNORECASE)
AGED_RULE = re.compile(r"\baged\s+(\d{1,3})\b", re.IGNORECASE)


def _uk_phone_ok(candidate: str) -> bool:
    digits = re.sub(r"\D", "", candidate)
    national = digits[2:] if digits.startswith("44") else digits[1:] if digits.startswith("0") else ""
    if national.startswith("0"):
        national = national[1:]  # "+44 (0)20 ..."
    return len(national) in (9, 10)


def rule_detections(text: str) -> list[Detection]:
    """The deterministic layer: UK formats the prebuilt model does not cover, plus GP practices."""
    found: list[Detection] = []

    def add(m: re.Match, cat: str, group: int = 0) -> None:
        found.append(Detection(m.start(group), m.end(group) - m.start(group), cat, 1.0, "rule"))

    for m in EMAIL_RULE.finditer(text):
        add(m, "EMAIL")
    for m in UK_PHONE_CANDIDATE.finditer(text):
        if _uk_phone_ok(m.group(0)):
            add(m, "PHONE")
    for rx in (UK_STREET_RULE, UK_POSTCODE_RULE):
        for m in rx.finditer(text):
            add(m, "ADDRESS")
    for m in UK_UNNUMBERED_STREET_RULE.finditer(text):
        add(m, "ADDRESS", 1)
    for m in GP_PRACTICE_RULE.finditer(text):
        add(m, "GP PRACTICE")
    for m in AGE_RULE.finditer(text):
        if age_from_text(m.group(1)) is not None:
            add(m, AGE_CATEGORY)
    for m in AGED_RULE.finditer(text):
        add(m, AGE_CATEGORY)
    return found


# ── Ages (FR-027) ──────────────────────────────────────────────────────────────────────────────
_UNITS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
    "fifteen sixteen seventeen eighteen nineteen".split())}
_TENS = {w: 10 * (i + 2) for i, w in enumerate(
    "twenty thirty forty fifty sixty seventy eighty ninety".split())}


def age_from_text(s: str) -> int | None:
    s = s.strip().lower()
    m = re.search(r"\d{1,3}", s)
    if m:
        n = int(m.group(0))
        return n if 0 <= n <= 120 else None
    parts = re.split(r"[\s\-]+", s)
    if len(parts) == 1 and parts[0] in _UNITS:
        return _UNITS[parts[0]]
    if parts and parts[0] in _TENS:
        rest = parts[1:] if len(parts) > 1 else []
        if not rest:
            return _TENS[parts[0]]
        if len(rest) == 1 and rest[0] in _UNITS and 0 < _UNITS[rest[0]] < 10:
            return _TENS[parts[0]] + _UNITS[rest[0]]
    return None


def age_band(age: int | None) -> str:
    if age is None:
        return "Not known"
    for lo, hi, label in AGE_BANDS:
        if lo <= age <= hi:
            return label
    return "Not known"


# ── Mapping, refinement, merge, replacement ────────────────────────────────────────────────────
@dataclass
class PrebuiltEntity:
    type: str
    start: int   # already converted to code points
    length: int
    score: float


@dataclass
class MapResult:
    detections: list[Detection] = field(default_factory=list)
    unmapped_types: list[str] = field(default_factory=list)


def map_prebuilt(entities: Iterable[PrebuiltEntity]) -> MapResult:
    out = MapResult()
    for e in entities:
        if e.type not in PREBUILT_TYPE_HANDLING:
            out.unmapped_types.append(e.type)
            continue
        cat = PREBUILT_TYPE_HANDLING[e.type]
        if cat is None:
            continue
        out.detections.append(Detection(e.start, e.length, cat, e.score, "aibuilder"))
    return out


def refine(text: str, dets: list[Detection]) -> list[Detection]:
    """Section 5.1: kinship context turns NAME into FAMILY MEMBER; ORG survives only as a GP practice."""
    refined: list[Detection] = []
    for d in dets:
        if d.category == "ORG":
            if GP_PRACTICE_VALUE.search(text[d.start:d.end]):
                refined.append(replace(d, category="GP PRACTICE"))
            continue  # any other organisation is retained in v0.1
        if d.category == "NAME":
            before = text[max(0, d.start - 60):d.start]
            after = text[d.end:d.end + 40]
            if _KIN_BEFORE.search(before) or _KIN_AFTER.search(after):
                d = replace(d, category="FAMILY MEMBER")
        refined.append(d)
    # A name continuing a list that began with a family member is a family member too:
    # "my children Amy, Ben and Cara".
    refined.sort(key=lambda d: d.start)
    for i in range(1, len(refined)):
        prev, cur = refined[i - 1], refined[i]
        if (cur.category == "NAME" and prev.category == "FAMILY MEMBER"
                and _LIST_JOIN.match(text[prev.end:cur.start])):
            refined[i] = replace(cur, category="FAMILY MEMBER")
    return refined


def _rank(cat: str) -> int:
    return PRECEDENCE.index(cat) if cat in PRECEDENCE else len(PRECEDENCE)


def merge(text: str, dets: list[Detection]) -> list[Detection]:
    """Union overlapping/nested spans; coalesce ADDRESS spans separated only by ', ' or spaces.

    Score of a merged span is the MINIMUM of its parts - a merge never raises confidence.
    """
    ordered = sorted(dets, key=lambda d: (d.start, -d.length))
    merged: list[Detection] = []
    for d in ordered:
        if merged:
            last = merged[-1]
            touching_address = (last.category == "ADDRESS" and d.category == "ADDRESS"
                                and re.fullmatch(r"[\s,]*", text[last.end:d.start] if d.start >= last.end else ""))
            if d.start < last.end or touching_address:
                end = max(last.end, d.end)
                cat = min((last.category, d.category), key=_rank)
                source = last.source if last.source == d.source else "mixed"
                merged[-1] = Detection(last.start, end - last.start, cat, min(last.score, d.score), source)
                continue
        merged.append(d)
    return merged


def label_for(text: str, d: Detection) -> str:
    if d.category == AGE_CATEGORY:
        span = text[d.start:d.end]
        m = AGE_RULE.search(span) or AGED_RULE.search(span)
        return f"[AGE {age_band(age_from_text(m.group(1) if m else span))}]"
    return LABEL[d.category]


def apply(text: str, merged: list[Detection]) -> str:
    """Replace from the END backwards. Spans must already be disjoint (merge() guarantees it)."""
    out = text
    for d in sorted(merged, key=lambda d: d.start, reverse=True):
        out = out[:d.start] + label_for(text, d) + out[d.end:]
    return out


# ── Windows for the 5,000-character limit ──────────────────────────────────────────────────────
def windows(text: str, max_len: int = PREBUILT_MAX_CHARS, overlap: int = WINDOW_OVERLAP) -> list[tuple[int, str]]:
    """Split into windows of at most max_len, each starting `overlap` characters before the previous
    window's end, cut at whitespace where possible. Returns (offset, window) pairs."""
    if overlap >= max_len:
        raise ValueError("overlap must be smaller than max_len")
    if len(text) <= max_len:
        return [(0, text)]
    out: list[tuple[int, str]] = []
    start = 0
    while start < len(text):
        end = min(start + max_len, len(text))
        if end < len(text):
            cut = text.rfind(" ", start + overlap + 1, end)
            if cut > start:
                end = cut
        out.append((start, text[start:end]))
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return out


def prebuilt_over_windows(text: str, call) -> list[PrebuiltEntity]:
    """Run `call(window_text) -> [PrebuiltEntity with window-relative offsets]` over every window
    and return whole-text offsets. Duplicates from the overlap are left for merge() to union."""
    out: list[PrebuiltEntity] = []
    for offset, chunk in windows(text):
        for e in call(chunk):
            out.append(PrebuiltEntity(e.type, e.start + offset, e.length, e.score))
    return out


# ── One column end to end ──────────────────────────────────────────────────────────────────────
@dataclass
class ColumnResult:
    redacted: str | None
    detections: list[Detection]
    unmapped_types: list[str]
    error: bool = False


def redact_column(text: str, prebuilt: list[PrebuiltEntity] | None, *, error: bool = False) -> ColumnResult:
    """`prebuilt` holds whole-text, code-point offsets (windows already shifted back).
    `error=True` means the AI Builder call failed for this column."""
    if error:
        return ColumnResult(None, [], [], error=True)
    mapped = map_prebuilt(prebuilt or [])
    raw = mapped.detections + rule_detections(text)
    for indirect_rule in INDIRECT_RULES:  # empty in v0.1 - see the extension point at the end
        raw += indirect_rule(text, raw)
    dets = refine(text, raw)
    merged = merge(text, dets)
    return ColumnResult(apply(text, merged), merged, mapped.unmapped_types)


# ── Record-level decision (FR-029, NFR-017, NFR-018; rules doc section 7) ──────────────────────
@dataclass(frozen=True)
class Decision:
    review_required: bool
    released: bool
    confidence: float | None
    reasons: tuple[str, ...]


def parse_threshold(setting_value: str | None) -> float | None:
    """rev_setting values are TEXT. Accept "0.85" or "85" (percent). Anything else is None."""
    if setting_value is None:
        return None
    try:
        v = float(str(setting_value).strip().rstrip("%"))
    except ValueError:
        return None
    if 1 < v <= 100:
        v = v / 100
    return v if 0 < v <= 1 else None


def decide(columns: dict[str, tuple[str | None, ColumnResult | None]], threshold_setting: str | None,
           empty_detection_policy: str = "review") -> Decision:
    """columns: column key -> (source text, result). A None/blank source text is out of scope.

    Fails closed on every path. Reasons are fixed codes; no input text ever enters a Decision.
    """
    reasons: list[str] = []
    threshold = parse_threshold(threshold_setting)
    if threshold is None:
        reasons.append("threshold-missing-or-invalid")
    ai_scores: list[float] = []
    any_text = False
    for key, (text, res) in sorted(columns.items()):
        if text is None or not text.strip():
            continue
        any_text = True
        if res is None or res.error:
            reasons.append(f"ai-error:{key}")
            continue
        if res.unmapped_types:
            reasons.append(f"unmapped-entity-type:{key}")
        if res.redacted is not None and len(res.redacted) > REDACTED_MAX_CHARS:
            reasons.append(f"redacted-exceeds-{REDACTED_MAX_CHARS}:{key}")
        ai_scores += [d.score for d in res.detections if d.source in ("aibuilder", "mixed")]
    confidence = min(ai_scores) if ai_scores else None
    if any_text and confidence is None and empty_detection_policy == "review":
        reasons.append("no-model-detections")
    if confidence is not None and threshold is not None and confidence < threshold:
        reasons.append("below-threshold")
    review = bool(reasons)
    return Decision(review_required=review, released=not review, confidence=confidence,
                    reasons=tuple(reasons))


# ── Re-runs never overwrite a human (rules doc section 7a) ─────────────────────────────────────
@dataclass(frozen=True)
class WritePlan:
    skip_record: bool                 # released: the flow touches nothing on this record
    writes: dict                      # column key -> redacted text to write (only EMPTY counterparts)
    kept: tuple[str, ...]             # non-empty counterparts left exactly as they are
    reasons: tuple[str, ...]          # extra review reasons for decide()


def plan_writes(released: bool, existing_counterparts: dict[str, str | None],
                new_redactions: dict[str, str | None]) -> WritePlan:
    """THE RULE: the flow writes a redacted counterpart only when the record is NOT released AND
    that counterpart is EMPTY (null or whitespace). It never overwrites text that is already there,
    because it cannot tell its own earlier output from a grant admin's correction - so it treats
    every existing value as a correction. To have one column scrubbed again, the admin clears it.

    A released record is never touched: no counterpart, no flag, no score.
    Any kept counterpart means the flow did not produce everything a trustee would see, so it may
    not release the record itself: reason `kept-existing-counterpart` sends it to the admin.
    """
    if released:
        return WritePlan(True, {}, tuple(sorted(existing_counterparts)), ())
    writes, kept = {}, []
    for key, new in new_redactions.items():
        current = existing_counterparts.get(key)
        if current is not None and current.strip():
            kept.append(key)
        elif new is not None:
            writes[key] = new
    reasons = tuple(f"kept-existing-counterpart:{k}" for k in sorted(kept))
    return WritePlan(False, writes, tuple(sorted(kept)), reasons)


def decide_with_plan(columns, threshold_setting, plan: WritePlan, **kw) -> Decision | None:
    """decide() plus the re-run reasons. Returns None for a released record: nothing is decided."""
    if plan.skip_record:
        return None
    d = decide(columns, threshold_setting, **kw)
    reasons = d.reasons + plan.reasons
    review = bool(reasons)
    return Decision(review, not review, d.confidence, reasons)


# ════════════════════════════════════════════════════════════════════════════════════════════════
# FLOW MODEL — rules v0.2, TAD rev 19 ADR-071 (direct identifiers) and ADR-072 (prompt stage, OFF)
# ════════════════════════════════════════════════════════════════════════════════════════════════
# Everything above this line is the v0.1 SPECIFICATION, written with regular expressions. Power
# Automate has none (E2), so ADR-071 hosts the rules in the flow with only what its expression
# language offers: per-character class strings, startsWith/endsWith/contains on padded strings, a
# fixed list of shapes, and a cursor loop over spans sorted by offset. The functions below are that
# flow, step for step, in Python. They are the ORACLE for `REV | Narrative | Scrub Free-Text`:
#   * test_flow_model.py proves them against the 20-sample corpus (shape detectors, residue checks,
#     refinement, merge, rebuild, decision);
#   * test_scrub_flow_definition.py executes the SHIPPED flow JSON in a small WDL simulator
#     (wdl_sim.py) over the same corpus and asserts it agrees with these functions exactly.
# Where this model and the v0.1 regex rules differ, the difference is named in the rules document,
# section 6a, and pinned by a test. Nothing in this section uses `re`.

# The twelve raw/redacted pairs, in rules section 2.1 order. Derived from Entity.xml (IMP-1066);
# the flow's Compose_scrub_columns constant holds the same list and a test compares the two.
SCRUB_COLUMNS = [
    ("rev_narrativeraw", "rev_narrativeredacted"),
    ("rev_otherconditionraw", "rev_otherconditionredacted"),
    ("rev_supportrecipientotherconditionraw", "rev_supportrecipientotherconditionredacted"),
    ("rev_disabilityimpactdescription", "rev_disabilityimpactdescriptionredacted"),
    ("rev_supportrecipientdisabilityimpactdescription", "rev_supportrecipientdisabilityimpactdescriptionredacted"),
    ("rev_unabletofundexplanation", "rev_unabletofundexplanationredacted"),
    ("rev_exceptionalfundingdetail", "rev_exceptionalfundingdetailredacted"),
    ("rev_otherexceptionalcircumstance", "rev_otherexceptionalcircumstanceredacted"),
    ("rev_caresupportdescription", "rev_caresupportdescriptionredacted"),
    ("rev_careprovidedexample", "rev_careprovidedexampleredacted"),
    ("rev_othercareprovidedtype", "rev_othercareprovidedtyperedacted"),
    ("rev_carecostsexplanation", "rev_carecostsexplanationredacted"),
]

# One-character label codes. A span variable in the flow holds offsets, a code and a score - never
# text (ADR-071 item 5). Age codes are the rev_agerange band, 0 = not known.
LABEL_BY_CODE = {
    "N": "[NAME]", "F": "[FAMILY MEMBER]", "G": "[GP PRACTICE]", "S": "[ADDRESS]",
    "P": "[PHONE]", "E": "[EMAIL]",
    "0": "[AGE Not known]", "1": "[AGE Under 18]", "2": "[AGE 18 to 24]", "3": "[AGE 25 to 34]",
    "4": "[AGE 35 to 44]", "5": "[AGE 45 to 54]", "6": "[AGE 55 to 64]", "7": "[AGE 65 to 74]",
    "8": "[AGE 75 and over]",
}
# Precedence, lowest first: a merged span takes the code that sits furthest right (rules 5.2:
# ADDRESS, GP PRACTICE, EMAIL, PHONE, FAMILY MEMBER, NAME, AGE). The flow uses indexOf() on this
# string, which is case-INSENSITIVE (E2) - so no two codes may differ only by case. They don't.
CODE_RANK = "012345678NFPEGS"
NO_SCORE = 2.0  # a shape-detector span carries no score; 2 sits above every real score (0..1)

# Extractor `type` -> code. "O" (organisation) and "Y" (age) are refined; "" is retained (not
# redacted); a type missing from this map is "U": unmapped, which forces review (rules 4.2).
EXTRACTOR_TYPE_CODE = {
    "PersonName": "N", "Organization": "O", "PhoneNumber": "P", "StreetAddress": "S",
    "ZipCode": "S", "Email": "E", "Age": "Y",
    **{t: "" for t, cat in PREBUILT_TYPE_HANDLING.items() if cat is None},
}

DIGITS = "0123456789"
LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def class_char(c: str) -> str:
    """ADR-071 item 3, the Select_referee_phone_digits pattern: digit -> 9, ASCII letter -> A."""
    return "9" if c in DIGITS else "A" if c in LETTERS else c


def class_string(text: str) -> str:
    return "".join(class_char(c) for c in text)


# ── Stage 2: UK phone and postcode shapes (ADR-071 item 3) ─────────────────────────────────────
# Derived from rules section 6's UK display forms. 9 = a digit, A = a letter, anything else is
# itself. A shape matches where the class string STARTS with it and the characters immediately
# before and after are neither a digit nor a letter. A format missing from these lists is not
# redacted - it is caught by the digit-run or postcode residue check instead, and goes to review.
PHONE_SHAPES = [
    "99999 999999", "99999999999", "99999 999 999",            # 07700 900123 · 07700900456
    "9999 999 9999", "999 9999 9999",                          # 0113 496 0000 · 020 7946 0018
    "(9999) 999 9999", "(999) 9999 9999", "(99999) 999999", "(99999) 999 999",
    "99999-999999", "9999-999-9999", "999-9999-9999",
    "+99 9999 999999", "+99 9999 999 999", "+99 99 9999 9999", "+99 999 999 9999",
    "+99 (9)9999 999999", "+99 (9)99 9999 9999", "+99 (9)999 999 9999",
    "+99 (9) 9999 999999", "+99 (9) 99 9999 9999", "+99 (9) 999 999 9999",
    "+999999999999",
]
POSTCODE_SHAPES = ["A9 9AA", "A99 9AA", "AA9 9AA", "AA99 9AA", "A9A 9AA", "AA9A 9AA"]
# The residue check is deliberately WIDER than the detector: it also catches a postcode written
# without its space, which the detector leaves alone rather than redact a product code.
POSTCODE_RESIDUE_SHAPES = POSTCODE_SHAPES + [s.replace(" ", "") for s in POSTCODE_SHAPES]
SHAPE_SLICE = 24  # the flow slices 24 class characters per candidate; every shape is shorter
SHAPE_TABLE = [{"shape": s, "code": "P"} for s in PHONE_SHAPES] + \
              [{"shape": s, "code": "S"} for s in POSTCODE_SHAPES]
CANDIDATE_PREFIXES = ("9", "(9", "+9", "A9", "AA9")  # every shape starts with one of these


def shape_hits(cls: str, shapes) -> list[tuple[int, int, str]]:
    """(start, length, code) for every shape occurrence in a class string, boundaries checked."""
    padded = " " + cls + " " * SHAPE_SLICE
    out = []
    for i in range(len(cls)):
        before, s = padded[i], padded[i + 1:i + 1 + SHAPE_SLICE]
        if before in "9A" or not s.startswith(CANDIDATE_PREFIXES):
            continue
        for row in shapes:
            shape = row["shape"]
            if s.startswith(shape) and s[len(shape)] not in "9A":
                out.append((i, len(shape), row["code"]))
    return out


def shape_spans(window: str, offset: int) -> list[dict]:
    return [{"start": offset + i, "length": n, "code": code, "score": NO_SCORE}
            for i, n, code in shape_hits(class_string(window), SHAPE_TABLE)]


# ── Stage 1 refinement: kinship, GP practice, age band (ADR-071 item 4) ────────────────────────
_NORMALISE_TO_SPACE = [",", ":", ";", ".", "(", ")", "-", "–", '"', "!", "?", "/", "\n", "\r", "\t"]


def normalise(s: str) -> str:
    """The flow's word normaliser: lower case, punctuation to spaces, double spaces collapsed three
    times (so up to 8 in a row become 1), trimmed. Mirrors a nested replace() chain exactly."""
    s = s.lower()
    for ch in _NORMALISE_TO_SPACE:
        s = s.replace(ch, " ")
    for _ in range(3):
        s = s.replace("  ", " ")
    return s.strip()


KIN_WORDS = [
    "husband", "wife", "partner", "spouse", "fiance", "fiancee", "fiancé", "fiancée",
    "boyfriend", "girlfriend", "son", "daughter", "child", "children", "kids", "mum", "mom",
    "mother", "mam", "dad", "father", "parent", "parents", "brother", "sister", "sibling",
    "siblings", "twin", "grandson", "granddaughter", "grandchild", "grandchildren", "grandmother",
    "grandfather", "gran", "grandma", "nan", "nana", "grandad", "granddad", "grandpa", "aunt",
    "auntie", "uncle", "niece", "nephew", "cousin", "stepson", "stepdaughter", "stepmother",
    "stepfather", "stepmum", "stepdad", "mother in law", "father in law", "son in law",
    "daughter in law", "sister in law", "brother in law",
]
KIN_TAILS = [k + suffix for k in KIN_WORDS for suffix in ("", " called", " named", " is")]
POSSESSIVES = ["my", "our", "his", "her", "their"]
KIN_BEFORE_CHARS = 60
KIN_AFTER_CHARS = 40


def name_context(text: str, start: int, length: int) -> dict:
    """What the flow's Compose_name_context computes for one PersonName span (secured)."""
    end = start + length
    before = " " + normalise(text[max(0, start - KIN_BEFORE_CHARS):start])
    after = text[min(end, len(text)):][:KIN_AFTER_CHARS].lower()
    if after.startswith("'s") or after.startswith("’s"):
        after = (after + "  ")[2:]
    after = after.strip()
    first_ok = after[:1] in (",", "(", "-", "–")
    words = normalise((after + " ")[1:]).split(" ")
    return {"before": before, "firstOk": first_ok, "w0": words[0],
            "w1rest": " ".join(words[1:]), "w2rest": " ".join(words[2:])}


def kin_before_hits(ctx: dict, tails=None) -> list[str]:
    """KIN_TAILS items the text before the name ends with, with a possessive in the 3 words before.
    Rev 20 (ADR-074 item 3): `tails` is the effective list, the floor plus valid additions."""
    b = ctx["before"]
    hits = []
    for tail in (KIN_TAILS if tails is None else tails):
        if b.endswith(" " + tail):
            rest = b[:max(len(b) - len(tail) - 1, 0)]
            words = rest.split(" ")
            if set(words[max(len(words) - 3, 0):]) & set(POSSESSIVES):
                hits.append(tail)
    return hits


def kin_after_hits(ctx: dict, words=None) -> list[str]:
    """KIN_WORDS that follow the name as ', my grandson' / '(her late husband'."""
    if not (ctx["firstOk"] and ctx["w0"] in POSSESSIVES):
        return []
    return [k for k in (KIN_WORDS if words is None else words)
            if (ctx["w1rest"] + " ").startswith(k + " ") or (ctx["w2rest"] + " ").startswith(k + " ")]


GP_SUFFIXES = ["surgery", "medical centre", "medical center", "health centre", "medical practice",
               "group practice", "family practice"]


def is_gp_practice(value: str, suffixes=None) -> bool:
    v = " " + normalise(value)
    return any(v.endswith(" " + s) for s in (GP_SUFFIXES if suffixes is None else suffixes))


NUMBER_WORDS = {str(n): n for n in range(0, 121)}
NUMBER_WORDS.update({w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
    "fifteen sixteen seventeen eighteen nineteen".split())})
NUMBER_WORDS.update({w: 10 * (i + 2) for i, w in enumerate(
    "twenty thirty forty fifty sixty seventy eighty ninety".split())})
AGE_BAND_UPPER = [(17, "1"), (24, "2"), (34, "3"), (44, "4"), (54, "5"), (64, "6"), (74, "7"), (200, "8")]


def _age_pair(a: int, b: int) -> int:
    """'ninety one' -> 91: a tens word followed by a unit 1..9; otherwise the first number."""
    return a + b if (a >= 20 and a % 10 == 0 and a <= 90 and 1 <= b <= 9) else a


def age_from_value(value: str) -> int:
    """-1 when no age can be read. Looks at the first three words only: '72 years old',
    'ninety-one years old', 'aged 45'. Mirrors the flow's single Select expression."""
    words = normalise(value).split(" ") + ["", "", ""]
    n = [NUMBER_WORDS.get(w, -1) for w in words[:3]]
    if n[0] >= 0:
        return _age_pair(n[0], n[1])
    if n[1] >= 0:
        return _age_pair(n[1], n[2])
    return -1


def age_code(value: str) -> str:
    age = age_from_value(value)
    if age < 0 or age > 120:
        return "0"
    for upper, code in AGE_BAND_UPPER:
        if age <= upper:
            return code
    return "0"


@dataclass
class ExtractorEntity:
    """One entity exactly as the extractor returns it: offsets relative to the WINDOW."""
    type: str
    value: str
    startIndex: int
    length: int
    score: float


def extractor_spans(text: str, entities: list[ExtractorEntity], offset: int,
                    lists=None) -> tuple[list[dict], bool]:
    """Map one window's entities to spans with whole-text offsets. Returns (spans, any_unmapped).
    `lists` (rev 20, ADR-074 item 3) carries the effective kinship and practice-suffix lists."""
    lists = lists or FLOOR
    spans, unmapped = [], False
    for e in entities:
        code = EXTRACTOR_TYPE_CODE.get(e.type, "U")
        if code == "O":
            code = "G" if is_gp_practice(e.value, lists.gp_suffixes) else ""
        elif code == "Y":
            code = age_code(e.value)
        if code == "U":
            unmapped = True
            continue
        if code == "":
            continue
        start = offset + e.startIndex
        if code == "N":
            ctx = name_context(text, start, e.length)
            if kin_before_hits(ctx, lists.kin_tails) or kin_after_hits(ctx, lists.kin_words):
                code = "F"
        spans.append({"start": start, "length": e.length, "code": code, "score": float(e.score)})
    return spans, unmapped


# ── Merge (cursor loop over spans sorted by start) and rebuild (ADR-071 item 5) ────────────────
LIST_JOINS = [",", ",and", ",&", "and", "&"]


def _higher(a: str, b: str) -> str:
    return a if CODE_RANK.index(a) > CODE_RANK.index(b) else b


def flow_merge(text: str, spans: list[dict]) -> list[dict]:
    """The flow's For_each_span loop. Each merged span carries prevEnd, the end of the span merged
    before it, so the rebuild is one Select with no index arithmetic."""
    merged: list[dict] = []
    cur = None
    last_end = 0
    for d in sorted(spans, key=lambda s: s["start"]):
        d_end = d["start"] + d["length"]
        if cur is not None:
            gap = text[min(cur["end"], len(text)):][:max(d["start"] - cur["end"], 0)]
            code = "F" if (d["code"] == "N" and cur["code"] == "F"
                           and gap.lower().replace(" ", "") in LIST_JOINS) else d["code"]
            extend = d["start"] < cur["end"] or (
                cur["code"] == "S" and d["code"] == "S" and gap.replace(",", "").strip() == "")
        else:
            code, extend = d["code"], False
        if extend:
            cur = {"start": cur["start"], "end": max(cur["end"], d_end),
                   "code": _higher(cur["code"], code), "score": min(cur["score"], d["score"])}
        else:
            if cur is not None:
                merged.append({**cur, "prevEnd": last_end})
                last_end = cur["end"]
            cur = {"start": d["start"], "end": d_end, "code": code, "score": d["score"]}
    if cur is not None:
        merged.append({**cur, "prevEnd": last_end})
    return merged


def flow_rebuild(text: str, merged: list[dict]) -> tuple[str, str]:
    """(redacted, skeleton). The skeleton has '|' where each label goes, so the residue checks see
    only the applicant's words and never a label ('[GP PRACTICE]' contains 'practice')."""
    last_end = merged[-1]["end"] if merged else 0
    red = "".join(text[m["prevEnd"]:m["start"]] + LABEL_BY_CODE[m["code"]] for m in merged) + text[last_end:]
    skel = "".join(text[m["prevEnd"]:m["start"]] + "|" for m in merged) + text[last_end:]
    return red, skel


# ── Residue checks on the rebuilt text (ADR-071 item 6; rev 20 adds `district`, ADR-073) ───────
STREET_WORDS = ["road", "street", "lane", "avenue", "close", "drive", "crescent", "terrace",
                "gardens", "grove"]
PRACTICE_WORDS = ["surgery", "medical centre", "health centre", "practice"]
AGE_PHRASES = ["9 years old", "9 year old", "9years old", "9year old", "9 yrs old", "9 yr old",
               "9yrs old", "9yr old"]
RESIDUE_KINDS = ["digit-run", "postcode", "at-sign", "street-word", "practice-word", "age-phrase",
                 "district"]


@dataclass(frozen=True)
class Lists:
    """The four word lists the flow uses, each the tested floor plus any valid rev_setting addition
    (rev 20, ADR-074 item 3). FLOOR is the rev 19 constants alone: what an absent row gives."""
    kin_words: tuple = tuple(KIN_WORDS)
    kin_tails: tuple = tuple(KIN_TAILS)
    gp_suffixes: tuple = tuple(GP_SUFFIXES)
    street_words: tuple = tuple(STREET_WORDS)
    practice_words: tuple = tuple(PRACTICE_WORDS)


FLOOR = Lists()


def word_string(text: str) -> str:
    """digit -> 9, ASCII letter -> lower case, anything else -> space; padded and collapsed."""
    w = "".join("9" if c in DIGITS else c.lower() if c in LETTERS else " " for c in text)
    w = " " + w + " "
    for _ in range(3):
        w = w.replace("  ", " ")
    return w


def digit_string(text: str) -> str:
    """digit -> 9; space, brackets, hyphen and + removed; anything else -> x."""
    return "".join("9" if c in DIGITS else "" if c in " ()-+" else "x" for c in text)


def residue_kinds(skeleton: str, lists=None, register=None) -> list[str]:
    """`register` is the postcode register (a set of upper-case outward codes) or None when it is
    unavailable, in which case the district check is skipped (ADR-073 item 2)."""
    lists = lists or FLOOR
    w = word_string(skeleton)
    found = {
        "digit-run": "999999999" in digit_string(skeleton),
        "postcode": bool(shape_hits(class_string(skeleton),
                                    [{"shape": s, "code": "S"} for s in POSTCODE_RESIDUE_SHAPES])),
        "at-sign": "@" in skeleton,
        "street-word": any(f" {x} " in w for x in lists.street_words),
        "practice-word": any(f" {x} " in w for x in lists.practice_words),
        "age-phrase": any(x in w for x in AGE_PHRASES),
        "district": has_residual_district(skeleton, register),
    }
    return [k for k in RESIDUE_KINDS if found[k]]


# ── Rev 20: the postcode register (ADR-073) ────────────────────────────────────────────────────
# The flow reads rev_citysettlementregister once per run and joins its outward codes, upper-cased,
# into one string `|AB1|AB10|...|`; a candidate is confirmed with contains(). The register only
# ADDS detections and never removes one (ADR-073 item 3).
REGISTER_SEED = (Path(__file__).resolve().parents[3] / "provisioning" / "dataverse" / "data"
                 / "city-settlement-register.csv")
REGISTER_MIN_ROWS = 3000          # ADR-073 item 2: fewer means the seed did not run
POSTCODE_UNSPACED_SHAPES = ["A99AA", "A999AA", "AA99AA", "AA999AA", "A9A9AA", "AA9A9AA"]
DISTRICT_SHAPES = ["A9", "A99", "AA9", "AA99"]
REGISTER_SHAPE_TABLE = ([{"shape": s, "kind": "F"} for s in POSTCODE_UNSPACED_SHAPES]
                        + [{"shape": s, "kind": "D"} for s in DISTRICT_SHAPES])
INWARD_AFTER_DISTRICT = " 9AA"    # a district followed by this is part of a full postcode
CUE_CHARS = 12                    # characters read before and after a district for a cue word
CUES_BEFORE = ["postcode", "post code"]
CUES_AFTER = ["area", "district", "postcode"]


def load_register(path: Path = REGISTER_SEED) -> list[str]:
    """The seed script's own source file: the codes exactly as the register holds them."""
    rows = path.read_text(encoding="utf-8").splitlines()[1:]
    return [r.split(",", 1)[0] for r in rows if r.strip()]


def register_from_rows(codes) -> set | None:
    """What Compose_postcode_register computes. None = unavailable (a failed read, or < 3,000)."""
    if codes is None or len(codes) < REGISTER_MIN_ROWS:
        return None
    return {(c or "").strip().upper() for c in codes}


def district_cue(text: str, start: int, length: int) -> bool:
    """ADR-073 item 5: `postcode` or `post code` just before, or `area`, `district` or `postcode`
    just after. Read from the WHOLE column text, normalised as the name context is."""
    before = " " + normalise(text[max(start - CUE_CHARS, 0):start])
    after = normalise(text[start + length:start + length + CUE_CHARS]) + " "
    return (any(before.endswith(" " + c) for c in CUES_BEFORE)
            or any(after.startswith(c + " ") for c in CUES_AFTER))


def register_spans(text: str, window: str, offset: int, register) -> list[dict]:
    """Stage 2, rev 20: a postcode written without its space, and a district on its own with a cue,
    each replaced only when the register confirms the outward code. Nothing when unavailable."""
    if register is None:
        return []
    padded = " " + class_string(window) + " " * SHAPE_SLICE
    out = []
    for i in range(len(window)):
        before, s = padded[i], padded[i + 1:i + 1 + SHAPE_SLICE]
        if before in "9A" or not s.startswith(CANDIDATE_PREFIXES):
            continue
        for row in REGISTER_SHAPE_TABLE:
            shape, kind = row["shape"], row["kind"]
            n = len(shape)
            if not s.startswith(shape) or s[n] in "9A":
                continue
            if kind == "D" and s[n:].startswith(INWARD_AFTER_DISTRICT):
                continue
            token = window[i:i + n].upper()
            outward = token[:-3] if kind == "F" else token
            if outward not in register:
                continue
            if kind == "D" and not district_cue(text, offset + i, n):
                continue
            out.append({"start": offset + i, "length": n, "code": "S", "score": NO_SCORE})
    return out


def has_residual_district(skeleton: str, register) -> bool:
    """Residue, rev 20: a register-confirmed district still in the text. Read on the skeleton, so a
    district inside a replaced span never trips it. Skipped when the register is unavailable."""
    if register is None:
        return False
    padded = " " + class_string(skeleton) + " " * SHAPE_SLICE
    for i in range(len(skeleton)):
        before, s = padded[i], padded[i + 1:i + 1 + SHAPE_SLICE]
        if before in "9A":
            continue
        for shape in DISTRICT_SHAPES:
            n = len(shape)
            if (s.startswith(shape) and s[n] not in "9A" and not s[n:].startswith(INWARD_AFTER_DISTRICT)
                    and skeleton[i:i + n].upper() in register):
                return True
    return False


# ── Rev 20: the settings the flow reads (ADR-074, TAD 5.5.1) ───────────────────────────────────
DEFAULT_MODIFIED = "2026-10-06T09:00:00Z"
WORD_LIST_KEYS = ["RedactionKinshipWordsExtra", "RedactionPracticeSuffixesExtra",
                  "RedactionStreetWordsExtra", "RedactionPracticeWordsExtra"]
WORD_LIST_CHARS = "abcdefghijklmnopqrstuvwxyz -'"
PROMPT_CATEGORY_LABELS = {"redactionpromptcategory.name": "NAME",
                          "redactionpromptcategory.familymember": "FAMILY MEMBER",
                          "redactionpromptcategory.gppractice": "GP PRACTICE",
                          "redactionpromptcategory.address": "ADDRESS"}
KIN_TAIL_SUFFIXES = ["", " called", " named", " is"]


@dataclass(frozen=True)
class SettingRow:
    name: str
    value: str | None
    modified: str | None


def redaction_rows(settings: dict, modified: dict | None = None) -> list[SettingRow]:
    """Every rev_setting row whose name starts with `Redaction` (any case), as the flow's in-flow
    filter keeps them. `modified` maps a name to its modifiedon; absent names get one fixed time."""
    modified = modified or {}
    return [SettingRow(n, v, modified.get(n, DEFAULT_MODIFIED)) for n, v in settings.items()
            if n.lower().startswith("redaction")]


def row(rows: list[SettingRow], name: str) -> SettingRow | None:
    """Setting names are an alternate key and are matched without regard to case."""
    return next((r for r in rows if r.name.lower() == name.lower()), None)


def iso_ticks(value: str | None) -> int:
    """ticks(): 100-ns intervals since 0001-01-01. Throws on null, as the platform does (A-NS-22)."""
    if not isinstance(value, str):
        raise ValueError("ticks() of a non-string")
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return (dt - datetime(1, 1, 1, tzinfo=timezone.utc)) // timedelta(microseconds=1) * 10


def parse_word_list(value: str | None) -> list[str] | None:
    """ADR-074 item 4: one entry per line; every non-blank line, trimmed and lower-cased, must be 2 to
    40 characters of a-z, space, hyphen and apostrophe, and (a refinement, fail-closed) contain a
    letter. Returns the lines, or None when the row is invalid as a whole (incl. empty)."""
    lines = [ln.strip().lower() for ln in (value or "").split("\n")]
    entries = [ln for ln in lines if ln]
    if not entries:
        return None
    for e in entries:
        if not 2 <= len(e) <= 40 or any(c not in WORD_LIST_CHARS for c in e) \
                or not e.replace(" ", "").replace("-", "").replace("'", ""):
            return None
    return entries


def collapse(s: str) -> str:
    for _ in range(3):
        s = s.replace("  ", " ")
    return s.strip()


def as_name_form(entry: str) -> str:
    """An entry as the name context and organisation values are normalised: '-' to a space."""
    return collapse(entry.replace("-", " "))


def as_word_form(entry: str) -> str:
    """An entry as the residue word string reads text: '-' and an apostrophe to a space."""
    return collapse(entry.replace("-", " ").replace("'", " "))


def union_list(floor, extra) -> tuple:
    """union(): the floor, then each new entry once, in order."""
    out = list(floor)
    for x in extra:
        if x not in out:
            out.append(x)
    return tuple(out)


@dataclass(frozen=True)
class PromptConfig:
    stage_on: bool = False
    valid: bool = False
    labels: tuple = ()
    categories: str = ""
    calibrated: bool = False

    @property
    def runs(self) -> bool:
        return self.stage_on and self.valid

    @property
    def allowed(self) -> str:
        return ", ".join(self.labels)


@dataclass(frozen=True)
class RunContext:
    """Everything the flow reads once per run, before the column loop (TAD 5.5.1)."""
    lists: Lists = FLOOR
    register: frozenset | None = None
    register_available: bool = False
    invalid_lists: tuple = ()
    threshold: float | None = None
    auto_release: str = "off"          # "on" | "off" | "stale"
    prompt: PromptConfig = PromptConfig()
    prompt_call: object = None         # callable(request) -> {"text", "finishReason"}; None = not built


def prompt_config(rows: list[SettingRow]) -> PromptConfig:
    stage = row(rows, "RedactionPromptStage")
    stage_on = stage is not None and (stage.value or "").strip().lower() == "on"
    cats = [r for r in rows if r.name.lower().startswith("redactionpromptcategory.")]
    parsed = [(PROMPT_CATEGORY_LABELS.get(r.name.lower(), ""),
               (r.value or "").replace("\r", " ").replace("\n", " ").strip()) for r in cats]
    valid = bool(parsed) and all(label and text for label, text in parsed)
    ordered = sorted(parsed, key=lambda p: p[0])           # sort(..., 'label'), A-NS-15
    labels = tuple(label for label, _ in ordered) if valid else ()
    categories = "\n".join(f"{label}: {text}" for label, text in ordered) if valid else ""
    cal = row(rows, "RedactionPromptCalibrated")
    calibrated = False
    if valid and cal is not None:
        listed = {p.strip().upper() for p in (cal.value or "").split(",") if p.strip()}
        newer = [r for r in rows if r.name.lower().startswith("redactionprompt") and r is not cal
                 and iso_ticks(r.modified) > iso_ticks(cal.modified)]
        calibrated = listed == set(labels) and not newer
    return PromptConfig(stage_on, valid, labels, categories, calibrated)


def auto_release_state(rows: list[SettingRow]) -> str:
    """ADR-074 item 5: 'on' only when the row is `true` AND saved at or after every other Redaction*
    row; 'stale' when it is `true` but an edit came later; 'off' otherwise."""
    ar = row(rows, "RedactionAutoRelease")
    if ar is None or (ar.value or "").strip().lower() != "true":
        return "off"
    mine = iso_ticks(ar.modified)
    return "stale" if any(iso_ticks(r.modified) > mine for r in rows if r is not ar) else "on"


_SEED = object()


def run_context(settings: dict, modified: dict | None = None, register=_SEED,
                prompt_call=None) -> RunContext:
    """`register`: the codes the register read returned, None for a failed read, or the seed."""
    rows = redaction_rows(settings, modified)
    for r in rows:                       # Select_redaction_setting_times: ticks() of every row
        iso_ticks(r.modified)
    extras, invalid = {}, []
    for key in WORD_LIST_KEYS:
        r = row(rows, key)
        if r is None:
            extras[key] = []
            continue
        entries = parse_word_list(r.value)
        if entries is None:
            invalid.append(key)
            extras[key] = []
        else:
            extras[key] = entries
    kin = [as_name_form(e) for e in extras["RedactionKinshipWordsExtra"]]
    lists = Lists(
        kin_words=union_list(KIN_WORDS, kin),
        kin_tails=union_list(KIN_TAILS, [k + t for k in kin for t in KIN_TAIL_SUFFIXES]),
        gp_suffixes=union_list(GP_SUFFIXES, [as_name_form(e) for e in extras["RedactionPracticeSuffixesExtra"]]),
        street_words=union_list(STREET_WORDS, [as_word_form(e) for e in extras["RedactionStreetWordsExtra"]]),
        practice_words=union_list(PRACTICE_WORDS, [as_word_form(e) for e in extras["RedactionPracticeWordsExtra"]]),
    )
    codes = load_register() if register is _SEED else register
    reg = register_from_rows(codes)
    th = row(rows, "RedactionConfidenceThreshold")
    return RunContext(lists, frozenset(reg) if reg is not None else None, reg is not None, tuple(invalid),
                      parse_threshold_flow(th.value if th else None), auto_release_state(rows),
                      prompt_config(rows), prompt_call)


# ── Rev 20: the prompt stage, built to the TAD 12.6.1 boundary (ADR-072, ADR-074) ──────────────
PROMPT_LABEL_ALLOW = {"NAME": "N", "FAMILY MEMBER": "F", "GP PRACTICE": "G", "ADDRESS": "S"}
PROMPT_QUOTE_MIN, PROMPT_QUOTE_MAX = 2, 200


def validate_prompt_items(window: str, offset: int, items, allowed=None) -> list[dict] | None:
    """ADR-072 item 6. Turn a prompt's JSON answer into spans, or None when ANY item is invalid (the
    whole answer for that column is then discarded: prompt-output-invalid). An item is valid when its
    label is on the allow-list - rev 20: the labels of the valid category rows read in the same run -
    its quote is 2 to 200 characters, and the quote occurs VERBATIM in the window at least once at
    word boundaries. Occurrences are found left to right without overlap, as split() finds them
    (A-NS-24); each one at word boundaries becomes a span with no score, and one inside a longer word
    ('Ann' in 'annual') is skipped, not an error. The prompt never supplies text: the label comes
    from the flow's map and every other character from the source."""
    allowed = tuple(PROMPT_LABEL_ALLOW) if allowed is None else tuple(allowed)
    if not isinstance(items, list):
        return None
    spans = []
    for it in items:
        if not isinstance(it, dict):
            return None
        label, quote = it.get("label"), it.get("quote")
        if not isinstance(label, str) or label not in allowed or not isinstance(quote, str) \
                or not PROMPT_QUOTE_MIN <= len(quote) <= PROMPT_QUOTE_MAX:
            return None
        found, i = False, window.find(quote)
        while i >= 0:
            before = window[i - 1] if i > 0 else " "
            after = window[i + len(quote)] if i + len(quote) < len(window) else " "
            if class_char(before) not in "9A" and class_char(after) not in "9A":
                found = True
                spans.append({"start": offset + i, "length": len(quote),
                              "code": PROMPT_LABEL_ALLOW[label], "score": NO_SCORE})
            i = window.find(quote, i + len(quote))
        if not found:
            return None
    return spans


def prompt_window(window: str, offset: int, ctx: RunContext) -> tuple[str, list]:
    """One window through the prompt stage. ('', spans) | ('error', []) | ('invalid', []).
    With no run action in the build (ctx.prompt_call is None, TAD 12.6.1 R1) the answer is empty,
    which is 'error': the stage fails closed exactly as ADR-072 item 8 says a failed call does."""
    request = {"Categories": ctx.prompt.categories, "AllowedLabels": ctx.prompt.allowed, "Narrative": window}
    try:
        answer = ctx.prompt_call(request) if ctx.prompt_call else None
    except Exception:  # noqa: BLE001 - any failure of the call is prompt-error, by design
        return "error", []
    answer = answer or {}
    text, reason = answer.get("text"), answer.get("finishReason")
    if not isinstance(reason, str) or reason.lower() != "stop" or not isinstance(text, str) or not text.strip():
        return "error", []                                    # A-NS-8: only a normal stop is usable
    try:
        items = json.loads(text.strip())
    except ValueError:
        return "error", []                                    # A-NS-10: unparseable is prompt-error
    spans = validate_prompt_items(window, offset, items, ctx.prompt.labels)
    return ("invalid", []) if spans is None else ("", spans)


# ── One column, one record ─────────────────────────────────────────────────────────────────────
@dataclass
class ColumnOutcome:
    status: str                      # "empty" | "kept" | "error" | "scrubbed"
    redacted: str | None = None
    merged: list = field(default_factory=list)
    reasons: list = field(default_factory=list)   # this column's reason codes, in flow order
    write: bool = False


def flow_scrub_column(key: str, text: str | None, existing: str | None, extract,
                      ctx: RunContext | None = None) -> ColumnOutcome:
    """`extract(window_text) -> [ExtractorEntity]` (window-relative); raising = the call failed.
    `ctx` is what the flow read once per run; the default is the floor lists, no register and the
    prompt stage off - the rev 19 behaviour."""
    ctx = ctx or RunContext()
    if text is None or not text.strip():
        return ColumnOutcome("empty")
    if existing is not None and existing.strip():
        return ColumnOutcome("kept", reasons=[f"kept-existing-counterpart:{key}"])
    spans, reasons, failed = [], [], False
    prompt_state, prompt_spans = "", []
    for offset, window in windows(text):
        try:
            ents = extract(window)
        except Exception:  # noqa: BLE001 - any failure of the call is ai-error, by design
            failed = True
            ents = None
        if ents is None:
            failed = True
        else:
            more, unmapped = extractor_spans(text, ents, offset, ctx.lists)
            if unmapped and f"unmapped-entity-type:{key}" not in reasons:
                reasons.append(f"unmapped-entity-type:{key}")
            spans += more
        spans += shape_spans(window, offset)
        spans += register_spans(text, window, offset, ctx.register)
        if ctx.prompt.runs:
            state, more = prompt_window(window, offset, ctx)
            if state == "error":
                prompt_state = "error"
            elif state == "invalid" and prompt_state == "":
                prompt_state = "invalid"
            prompt_spans += more
    if failed:
        return ColumnOutcome("error", reasons=reasons + [f"ai-error:{key}"])
    if prompt_state == "":
        spans += prompt_spans
    elif prompt_state == "error":
        reasons.append(f"prompt-error:{key}")
    else:
        reasons.append(f"prompt-output-invalid:{key}")
    merged = flow_merge(text, spans)
    red, skel = flow_rebuild(text, merged)
    out = ColumnOutcome("scrubbed", redacted=red, merged=merged, reasons=reasons)
    if len(red) > REDACTED_MAX_CHARS:
        out.reasons.append(f"redacted-exceeds-{REDACTED_MAX_CHARS}:{key}")
    else:
        out.reasons += [f"residual-{k}:{key}" for k in residue_kinds(skel, ctx.lists, ctx.register)]
        out.write = True
    return out


def parse_threshold_flow(value: str | None) -> float | None:
    """What the flow can parse without float() throwing: digits and at most one '.', '%' ignored.
    "0.85", "85" and "85%" all give 0.85. Anything else is None (threshold-missing-or-invalid)."""
    t = (value or "").replace("%", "").strip()
    if not t or t == "." or t.count(".") > 1 or any(c not in DIGITS + "." for c in t):
        return None
    v = float(t)
    if 1 < v <= 100:
        v = v / 100
    return v if 0 < v <= 1 else None


def setting_is(value: str | None, expected: str) -> bool:
    return (value or "").strip().lower() == expected


@dataclass(frozen=True)
class FlowDecision:
    released: bool
    review_required: bool
    confidence: float | None
    reasons: tuple[str, ...]


def flow_decide(outcomes: list[ColumnOutcome], settings) -> FlowDecision:
    """`settings` is a RunContext, or a dict of rev_setting name -> value (every row saved at the same
    time, the seed register available, no prompt run action), turned into one."""
    ctx = settings if isinstance(settings, RunContext) else run_context(settings)
    reasons: list[str] = []
    for o in outcomes:
        for r in o.reasons:
            if r not in reasons:
                reasons.append(r)
    scores = [m["score"] for o in outcomes if o.status == "scrubbed" for m in o.merged]
    low = min(scores + [NO_SCORE])
    confidence = None if low >= NO_SCORE else low
    any_scrubbed = any(o.status == "scrubbed" for o in outcomes)
    record = []
    if ctx.threshold is None:
        record.append("threshold-missing-or-invalid")
    if any_scrubbed and confidence is None:
        record.append("no-model-detections")          # rules D-2, kept as drafted (2026-10-06)
    if ctx.threshold is not None and confidence is not None and confidence < ctx.threshold:
        record.append("below-threshold")
    if ctx.auto_release != "on":
        record.append(f"auto-release-{ctx.auto_release}")   # ADR-071 item 8, ADR-074 item 5
    if ctx.prompt.stage_on and not ctx.prompt.valid:
        record.append("prompt-config-invalid")         # ADR-074 item 4
    if ctx.prompt.stage_on and not ctx.prompt.calibrated:
        record.append("uncalibrated-stage:prompt")     # ADR-072 item 8, ADR-074 item 5
    if not ctx.register_available:
        record.append("postcode-register-unavailable")  # ADR-073 item 2
    record += [f"redaction-setting-invalid:{k}" for k in ctx.invalid_lists]   # ADR-074 item 4
    reasons += [r for r in record if r not in reasons]
    review = bool(reasons)
    return FlowDecision(not review, review, confidence, tuple(reasons))


def flow_scrub_record(row_: dict, settings: dict, extract, *, modified: dict | None = None,
                      register=_SEED, prompt_call=None) -> tuple[FlowDecision | None, dict]:
    """The whole flow for one application row. Returns (decision, writes). A released record is
    never touched: (None, {}). `register` is the codes the register read returns (default: the
    seed file), or None for a failed read."""
    if row_.get("rev_redactionreleased") is True:
        return None, {}
    ctx = run_context(settings, modified, register, prompt_call)
    outcomes, writes = [], {}
    for raw, red in SCRUB_COLUMNS:
        o = flow_scrub_column(raw, row_.get(raw), row_.get(red), extract, ctx)
        outcomes.append(o)
        if o.write:
            writes[red] = o.redacted
    return flow_decide(outcomes, ctx), writes


# ── EXTENSION POINT: indirect identifiers (OUT of v0.1) ────────────────────────────────────────
# Reviewer decision 2026-10-05: indirect identifiers (family composition such as "how many
# sisters", "living with" + postcode, household make-up, rare circumstances) are added after
# Emily's input. Each future rule is a function (text, detections) -> extra detections, appended
# here and run inside redact_column() after rule_detections(). Adding one changes no other code:
# merge(), apply() and decide() already treat every detection the same way.
INDIRECT_RULES: list = []
