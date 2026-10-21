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
    # TAD rev 25, ADR-078: no reason is not a release. Every record waits for the process owner; the reasons
    # are hints. (v0.1 read: released when there was no reason.)
    return Decision(review_required=True, released=False, confidence=confidence, reasons=tuple(reasons))


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
    Any kept counterpart means the flow did not produce everything a trustee would see: the hint
    `kept-existing-counterpart` tells the process owner (who releases every record, ADR-078).
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
    return Decision(True, False, d.confidence, d.reasons + plan.reasons)     # ADR-078: never released


# ════════════════════════════════════════════════════════════════════════════════════════════════
# FLOW MODEL — TAD rev 22, ADR-075 (approved 2026-10-16), amended by rev 30, ADR-082 (2026-10-21): label, rewrite and spell, check
# ════════════════════════════════════════════════════════════════════════════════════════════════
# Everything above this line is the v0.1 SPECIFICATION, written with regular expressions. The
# functions below are `REV | Narrative | Scrub Free-Text` as rebuilt in Iteration 9, step for step:
#
#   1. the extractor labels what it finds, in one call per BATCH of columns of at most 5,000 characters
#      (rev 30, ADR-082; a column over 5,000 characters is not scrubbed, `too-long`), each entity going back
#      to its column by offset (plan_batches, map_entities);
#   2. the labelled text is rebuilt by offset, so the model never receives a value the extractor found;
#   3. the REWRITE prompt applies the client's key, turns names into They, fixes the grammar, labels
#      anything else identifying and (rev 30) corrects spelling, declaring each correction (split_answer);
#   4. a declared correction counts only as a validated near-spelling pair (valid_corrections);
#   5. check P1 (surviving_identifiers): no extractor value survives -> otherwise not written;
#   6. check P2 (validate_rewrite): the rewrite added no word -> otherwise not written;
#   7. check P3 (residue_kinds): a residue writes the column and holds the record.
#
# They are the ORACLE for the flow. test_scrub_flow_definition.py executes the SHIPPED JSON in
# wdl_sim.py with stand-in prompts and asserts it agrees with these functions. The two prompts are
# the only parts the oracle cannot be: neutral_rewrite() below is what a GOOD rewrite looks like, and
# it is the expected output wbs:5.7 scores the live model against. P1 and P2 do not trust it either.
# Nothing in this section uses `re`, because the flow has none.

# The twelve raw/redacted pairs, in rules section 2.1 order. Derived from Entity.xml (IMP-1066);
# the flow's Compose_constants holds the same list and a test compares the two.
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

# THE LABEL SET — one place. The flow's Compose_constants `labels` object must equal this map, and the
# closed list (P2) and the spelling rule read the label words FROM it (label_words()), so a label
# change after Emily's test (reviewer, 2026-10-16: "Keep the family member label for now. I am
# expecting one more itteration on the labels after Emily has tested.") is one edit here and one in
# the flow constant; a test fails until both agree. "F" is produced by no rule since the reviewer's
# 2026-10-16 correction ("my husband Derek" becomes "my partner"); it stays so P2 accepts it.
LABEL_BY_CODE = {
    "N": "[NAME]", "F": "[FAMILY MEMBER]", "G": "[GP PRACTICE]", "S": "[ADDRESS]",
    "P": "[PHONE]", "E": "[EMAIL]",
    "0": "[AGE Not known]", "1": "[AGE Under 18]", "2": "[AGE 18 to 24]", "3": "[AGE 25 to 34]",
    "4": "[AGE 35 to 44]", "5": "[AGE 45 to 54]", "6": "[AGE 55 to 64]", "7": "[AGE 65 to 74]",
    "8": "[AGE 75 and over]",
}

# Extractor `type` -> code. "O" (organisation) is a GP practice only with a practice suffix; "Y" (age)
# becomes its band; "" is retained (not an identifier); a type missing from this map is "U": unmapped,
# which sends the record to review (rules 4.2, ADR-075 item 2 "as now").
EXTRACTOR_TYPE_CODE = {
    "PersonName": "N", "Organization": "O", "PhoneNumber": "P", "StreetAddress": "S",
    "ZipCode": "S", "Email": "E", "Age": "Y",
    **{t: "" for t, cat in PREBUILT_TYPE_HANDLING.items() if cat is None},
}

EXTRACTOR_MAX_CHARS = 5000   # ADR-075 item 1: a column of more characters is not scrubbed (rev 30: E2, the per-call limit)
DIGITS = "0123456789"
LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
LOWER = "abcdefghijklmnopqrstuvwxyz"
NO_SCORE = 2.0               # "no score": sits above every real score (0..1)


def class_char(c: str) -> str:
    """digit -> 9, ASCII letter -> A, anything else itself (the residue postcode shapes)."""
    return "9" if c in DIGITS else "A" if c in LETTERS else c


def class_string(text: str) -> str:
    return "".join(class_char(c) for c in text)


# ── Normalising, as the flow's replace() chains do ─────────────────────────────────────────────
# NORM_PUNCT -> space, for P1 and the entity values: lower case, punctuation INCLUDING apostrophes and
# brackets to spaces, so "Sam's" contains the word "sam" and "[NAME]" is the word "name".
NORM_PUNCT = [",", ":", ";", ".", "(", ")", "-", "–", '"', "!", "?", "/", "[", "]", "|", "'", "’",
              "\n", "\r", "\t"]
# WORD_PUNCT -> space, for P2's words: the same list WITHOUT the apostrophes, so "they're" stays one word.
WORD_PUNCT = [p for p in NORM_PUNCT if p not in ("'", "’")]
# CORE_PUNCT -> removed, for the pair rule's "is this a closed-list word" test.
CORE_PUNCT = [p for p in WORD_PUNCT if p not in ("\n", "\r", "\t")]
COLLAPSES = 4   # double spaces collapsed four times: up to 16 in a row become one


def _collapse(s: str) -> str:
    for _ in range(COLLAPSES):
        s = s.replace("  ", " ")
    return s


def normalise(s: str) -> str:
    s = s.lower()
    for ch in NORM_PUNCT:
        s = s.replace(ch, " ")
    return _collapse(s).strip()


def remove_labels(s: str, by: str = " ") -> str:
    """Every label text, exactly as the flow's map writes it (replace() is case-sensitive)."""
    for label in LABEL_BY_CODE.values():
        s = s.replace(label, by)
    return s


def p2_words(s: str) -> list[str]:
    """P2's words: labels removed, lower case, curly apostrophe made straight, punctuation to spaces."""
    s = remove_labels(s).lower().replace("’", "'")
    for ch in WORD_PUNCT:
        s = s.replace(ch, " ")
    s = _collapse(s).strip()
    return s.split(" ") if s else []


def core(word: str) -> str:
    w = word.lower().replace("’", "'")
    for ch in CORE_PUNCT:
        w = w.replace(ch, "")
    return w


# ── Step 1-2: labels and the labelled text (ADR-075 item 2) ───────────────────────────────────
GP_SUFFIXES = ["surgery", "medical centre", "medical center", "health centre", "medical practice",
               "group practice", "family practice"]


def is_gp_practice(norm_value: str) -> bool:
    v = " " + norm_value
    return any(v.endswith(" " + s) for s in GP_SUFFIXES)


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


def age_from_value(norm_value: str) -> int:
    """-1 when no age can be read: the first number, or a tens word plus a unit, in the first 3 words."""
    words = (norm_value + "   ").split(" ")
    n = [NUMBER_WORDS.get(w, -1) for w in words[:3]]
    if n[0] >= 0:
        return _age_pair(n[0], n[1])
    if n[1] >= 0:
        return _age_pair(n[1], n[2])
    return -1


def age_code(age: int) -> str:
    if age < 0 or age > 120:
        return "0"
    for upper, code in AGE_BAND_UPPER:
        if age <= upper:
            return code
    return "0"


@dataclass
class ExtractorEntity:
    """One entity exactly as the extractor returns it."""
    type: str
    value: str
    startIndex: int
    length: int
    score: float
    crosses: bool = False   # ADR-082 item 2: the entity runs past this column into its neighbour (batched call)


@dataclass(frozen=True)
class Span:
    i: int           # position in the extractor's answer
    start: int
    length: int
    code: str
    score: float
    value: str       # normalised value: what P1 searches for
    crosses: bool = False   # ADR-082 item 2: the extractor's entity straddles a column boundary

    @property
    def end(self) -> int:
        return self.start + self.length


def entity_code(e: ExtractorEntity) -> str:
    code = EXTRACTOR_TYPE_CODE.get(e.type or "", "U")
    norm = normalise(e.value or "")
    if code == "O":
        return "G" if is_gp_practice(norm) else ""
    if code == "Y":
        return age_code(age_from_value(norm))
    return code


# ── A person's name: the Dr trim and the joined-fragment extension (Iteration 11, IMP-1139) ─────
# Measured in DEV, 2026-10-19 (TD-13): the extractor returned "Beatrix Holloway" for "Beatrix Holloway-Reed",
# so the labelled text read "[NAME]-Reed" and "-Reed" reached the trustee text ("they-Reed"). P1 searches
# only extractor values and P2 accepts "reed" because it is in the input. So a PersonName span is widened
# DETERMINISTICALLY over one directly joined fragment on each side, before labelling:
#   after:  a hyphen and one or more letters ("Holloway" + "-Reed"), or an apostrophe and TWO or more letters
#           (so the possessive "'s", and "'d" / "'m", are never swallowed: "[NAME]'s" stays a possessive);
#   before: one or more letters and a hyphen or apostrophe ("O'" + "Brien", "Mary-" + "Ann").
# Letters are ASCII letters only, as everywhere else in the flow; one fragment per side. Anything still
# joined to a label after this is caught by P3's `name-fragment` check (joined_spans, final_joint).
# And a span that STARTS with "Dr ", "Dr. " or "Doctor " (any capitals) is shrunk past the title, so the
# rewrite prompt sees "Dr [NAME]" and its Keep-[NAME]-after-Dr rule can apply (DEV 2026-10-19: "Dr [NAME]"
# came back as "they", the title gone). The P1 value stays the extractor's own value.
JOINERS = "-'’"
APOSTROPHES = "'’"
DR_PREFIXES = ["doctor ", "dr. ", "dr "]   # tested longest first; matched on the lower-cased text


def _letter(text: str, i: int) -> bool:
    return 0 <= i < len(text) and text[i] in LETTERS


def _letter_run(text: str, i: int, step: int) -> int:
    n = 0
    while _letter(text, i + n * step):
        n += 1
    return n


def dr_trim(text: str, start: int, length: int) -> int:
    low = (text + " " * 8)[start:start + 7].lower()
    for p in DR_PREFIXES:
        if low.startswith(p) and length > len(p):
            return len(p)
    return 0


def joined_after(text: str, end: int) -> int:
    """How many characters a fragment joined at `end` adds: the joiner plus its letters; 0 when none."""
    j = text[end] if end < len(text) else " "
    run = _letter_run(text, end + 1, 1)
    if j == "-" and run > 0:
        return 1 + run
    if j in APOSTROPHES and run > 1:
        return 1 + run
    return 0


def joined_before(text: str, start: int) -> int:
    """How many characters a fragment joined before `start` adds: its letters plus the joiner; 0 when none."""
    if start < 2 or text[start - 1] not in JOINERS or not _letter(text, start - 2):
        return 0
    return 1 + _letter_run(text, start - 2, -1)


def all_spans(text: str, entities: list[ExtractorEntity]) -> list[Span]:
    """Select_entities -> Select_entity_ages -> Select_spans: every entity with its code, clamped to the text;
    a PersonName span trimmed past a leading Dr and widened over a joined fragment on each side."""
    out = []
    for i, e in enumerate(entities):
        start = max(min(int(e.startIndex or 0), len(text)), 0)
        length = max(min(int(e.length or 0), len(text) - start), 0)
        if EXTRACTOR_TYPE_CODE.get(e.type or "", "U") == "N":
            trim, back, fwd = dr_trim(text, start, length), joined_before(text, start), joined_after(text, start + length)
            start, length = start + trim - back, length - trim + back + fwd
        out.append(Span(i, start, length, entity_code(e), float(e.score or 0), normalise(e.value or ""),
                        bool(e.crosses)))
    return out


def joined_spans(text: str, kept: list[Span]) -> list[Span]:
    """P3 `name-fragment`, on the input side: a kept span (any label) with a fragment still joined to it in
    the raw text, by the same rule as the extension. Such a fragment would sit next to the label in the
    labelled text, where P1 cannot see it and P2 accepts it."""
    return [s for s in kept if joined_after(text, s.end) or joined_before(text, s.start)]


FINAL_JOINTS = ["|-A", "|'AA", "|’AA", "A-|", "A'|", "A’|"]


def final_joint(final: str) -> bool:
    """P3 `name-fragment`, on the output side: a label in the final text directly joined to letters by a
    hyphen or apostrophe, by the same rule (after an apostrophe, two letters or more)."""
    c = class_string(remove_labels(final, "|"))
    return any(x in c for x in FINAL_JOINTS)


def _contains(t: Span, s: Span) -> bool:
    return t.start <= s.start and s.end <= t.end


# ── A GP practice the extractor missed (TAD rev 29, ADR-075 item 2 "Decided: label", IMP-1170) ─────────────
# DEV 2026-10-20: the extractor returned no Organization for "Moorside Medical Centre" in TD-13, and the name was
# written with only residual-practice-word on it. Now, on the raw column, every case-sensitive occurrence of a
# capitalised practice suffix (word boundary before: a space or the start; after: a non-letter or the end) becomes a
# [GP PRACTICE] span from the start of the name to the end of the suffix. The start: walk back word by word (split on
# single spaces) while the word is St or St., or begins with A-Z and is ASCII letters with optional internal
# apostrophes or hyphens; at most four words. Zero words: no span. These spans join the extractor's AFTER them, so
# the existing containment rule drops a span inside another (an equal one kept once, the extractor's), and a partial
# overlap holds the column. Score NO_SCORE (a rule, not the model); value "" (P1 searches extractor values only).
PRACTICE_SUFFIXES = ["Surgery", "Medical Centre", "Health Centre", "Medical Practice", "Group Practice",
                     "Family Practice"]
PRACTICE_HIT_CAP = 25          # occurrences of one suffix per column; a later one is left to residual-practice-word
PRACTICE_WALK_WORDS = 4
PRACTICE_SPAN_BASE = 1000      # practice span i = 1000 + suffix index * 25 + occurrence: never an extractor index


def capitalise_words(entry: str) -> str:
    """A RedactionPracticeWordsExtra entry (word form, single spaces) with each word's first letter upper-cased."""
    return " ".join(w[:1].upper() + w[1:] for w in entry.split(" "))


def _raw_class(text: str) -> str:
    """Compose_raw_classes without its padding: ASCII letter -> A, anything else itself."""
    return "".join("A" if c in LETTERS else c for c in text)


def practice_name_word(word: str, cls: str) -> bool:
    if word in ("St", "St."):
        return True
    return (word[:1] in LETTERS[26:] and cls[:1] == "A" and cls[-1:] == "A"
            and not cls.replace("A", "").replace("'", "").replace("’", "").replace("-", ""))


def practice_spans(text: str, suffixes=None) -> list[Span]:
    suffixes = PRACTICE_SUFFIXES if suffixes is None else list(suffixes)
    cls = _raw_class(text)
    out = []
    for k, suffix in enumerate(suffixes):
        parts = text.split(suffix)
        for j in range(PRACTICE_HIT_CAP):
            if j >= len(parts) - 1:
                continue
            pos = len(suffix.join(parts[:j + 1]))
            end = pos + len(suffix)
            if not (pos == 0 or text[pos - 1] == " ") or _letter(text, end):
                continue
            words = text[:max(pos - 1, 0)].split(" ")
            cwords = cls[:max(pos - 1, 0)].split(" ")
            taken, total = 0, 0
            for back in range(1, PRACTICE_WALK_WORDS + 1):
                w = words[-back] if len(words) >= back else ""
                cw = cwords[-back] if len(cwords) >= back else ""
                if not practice_name_word(w, cw):
                    break
                taken, total = back, total + len(w)
            if taken == 0:
                continue
            start = pos - 1 - (total + taken - 1)
            out.append(Span(PRACTICE_SPAN_BASE + k * PRACTICE_HIT_CAP + j, start, end - start, "G", NO_SCORE, ""))
    return out


def label_spans(text: str, entities: list[ExtractorEntity], suffixes=None):
    """-> (labelled spans, kept spans sorted by start, unmapped?, partial overlap?).
    Labelled: a code that is neither retained ('') nor unmapped ('U'), and a length above 0. A span inside
    another is dropped (the longer wins; equal extents: the earlier entity wins). Two spans that overlap
    without either containing the other hold the column (`overlapping-identifiers`, not written)."""
    spans = all_spans(text, entities) + practice_spans(text, suffixes)   # rev 29: practice spans after
    unmapped = any(s.code == "U" for s in spans)
    lab = [s for s in spans if s.code not in ("", "U") and s.length > 0]
    dropped, partial = set(), False
    for a, s in enumerate(lab):
        for b, t in enumerate(lab):
            if a == b:
                continue
            if _contains(t, s) and (t.length > s.length or (t.length == s.length and b < a)):
                dropped.add(s.i)
            elif t.start < s.end and s.start < t.end and not _contains(t, s) and not _contains(s, t):
                partial = True
    # ADR-082 item 2: a labelled entity that straddles two columns of a batched call is held exactly as a partial
    # overlap is, in every column it touches, whether or not another span contains it here.
    partial = partial or any(s.crosses for s in lab)
    kept = sorted([s for s in lab if s.i not in dropped], key=lambda s: s.start)
    return lab, kept, unmapped, partial


def labelled_text(text: str, kept: list[Span]) -> str:
    """One Select and a join: the text between spans copied, each span its label. Kept spans never
    nest, so their ends rise with their starts; an overlap gives an empty gap, never a negative one."""
    pieces, prev = [], 0
    for s in kept:
        pieces.append(text[prev:prev + max(s.start - prev, 0)] + LABEL_BY_CODE[s.code])
        prev = s.end
    pieces.append(text[prev:])
    return "".join(pieces)


# ── The fixed part of the closed list (P2) — rev 23, ADR-076 item 3 ──────────────────────────
# Since rev 23 the NEUTRAL words, the gendered words and the titles come from four rev_setting rows (see
# "The four rule rows" below). What stays fixed is the grammar set no rule chooses, and the words of the
# extractor's own labels, which FR-026/FR-027 fix and the deterministic labelling writes.
AGREED_FORMS = ["are", "were", "have", "do", "go", "aren't", "weren't", "haven't", "don't"]
# "my" (Mum used as a name, FR-094) and the articles a replacement can need ("an uncle" -> "a relative").
FUNCTION_WORDS = ["my", "a", "an"]


def label_words() -> list[str]:
    out = []
    for label in LABEL_BY_CODE.values():
        for w in p2_words(label.replace("[", " ").replace("]", " ")):
            if w not in out:
                out.append(w)
    return out


def closed_words() -> list[str]:
    """The flow's Compose_constants `closedWords`: the fixed grammar set and the extractor's label words.
    run_context() adds the targets of RedactionNeutralTerms and the words of RedactionLabels."""
    out = []
    for w in AGREED_FORMS + FUNCTION_WORDS + label_words():
        if w not in out:
            out.append(w)
    return out


STREET_WORDS = ["road", "street", "lane", "avenue", "close", "drive", "crescent", "terrace",
                "gardens", "grove"]
PRACTICE_WORDS = ["surgery", "medical centre", "health centre", "practice"]
AGE_PHRASES = ["9 years old", "9 year old", "9years old", "9year old", "9 yrs old", "9 yr old",
               "9yrs old", "9yr old"]
POSTCODE_SHAPES = ["A9 9AA", "A99 9AA", "AA9 9AA", "AA99 9AA", "A9A 9AA", "AA9A 9AA"]
POSTCODE_RESIDUE_SHAPES = POSTCODE_SHAPES + [s.replace(" ", "") for s in POSTCODE_SHAPES]
SHAPE_SLICE = 24
CANDIDATE_PREFIXES = ("9", "(9", "+9", "A9", "AA9")
RESIDUE_KINDS = ["digit-run", "postcode", "at-sign", "street-word", "practice-word", "age-phrase",
                 "district", "gendered-term", "title", "name-fragment"]


def shape_hits(cls: str, shapes) -> list[tuple[int, int]]:
    padded = " " + cls + " " * SHAPE_SLICE
    out = []
    for i in range(len(cls)):
        before, s = padded[i], padded[i + 1:i + 1 + SHAPE_SLICE]
        if before in "9A" or not s.startswith(CANDIDATE_PREFIXES):
            continue
        for shape in shapes:
            if s.startswith(shape) and s[len(shape)] not in "9A":
                out.append((i, len(shape)))
    return out


def word_string(text: str) -> str:
    """digit -> 9, ASCII letter -> lower case, anything else -> space; padded and collapsed 3 times."""
    w = "".join("9" if c in DIGITS else c.lower() if c in LETTERS else " " for c in text)
    w = " " + w + " "
    for _ in range(3):
        w = w.replace("  ", " ")
    return w


def digit_string(text: str) -> str:
    """digit -> 9; space, brackets, hyphen and + removed; anything else -> x."""
    return "".join("9" if c in DIGITS else "" if c in " ()-+" else "x" for c in text)


# The postcode register (ADR-073): read once per run, now only for the residual-district check.
REGISTER_SEED = (Path(__file__).resolve().parents[3] / "provisioning" / "dataverse" / "data"
                 / "city-settlement-register.csv")
REGISTER_MIN_ROWS = 3000
DISTRICT_SHAPES = ["A9", "A99", "AA9", "AA99"]
INWARD_AFTER_DISTRICT = " 9AA"


def load_register(path: Path = REGISTER_SEED) -> list[str]:
    rows = path.read_text(encoding="utf-8").splitlines()[1:]
    return [r.split(",", 1)[0] for r in rows if r.strip()]


def register_from_rows(codes) -> set | None:
    if codes is None or len(codes) < REGISTER_MIN_ROWS:
        return None
    return {(c or "").strip().upper() for c in codes}


def has_residual_district(bare: str, register) -> bool:
    if register is None:
        return False
    padded = " " + class_string(bare) + " " * SHAPE_SLICE
    for i in range(len(bare)):
        before, s = padded[i], padded[i + 1:i + 1 + SHAPE_SLICE]
        if before in "9A":
            continue
        for shape in DISTRICT_SHAPES:
            n = len(shape)
            if (s.startswith(shape) and s[n] not in "9A" and not s[n:].startswith(INWARD_AFTER_DISTRICT)
                    and bare[i:i + n].upper() in register):
                return True
    return False


# ── Settings (TAD 5.5.1 rev 23, ADR-075 item 8 as amended by ADR-076) ──────────────────────────
DEFAULT_MODIFIED = "2026-10-16T09:00:00Z"
WORD_LIST_KEYS = ["RedactionStreetWordsExtra", "RedactionPracticeWordsExtra"]     # additive, ADR-074 item 3
RULE_KEYS = ["RedactionNeutralTerms", "RedactionTitles", "RedactionNameRules", "RedactionLabels"]  # ADR-076
WORD_LIST_CHARS = "abcdefghijklmnopqrstuvwxyz -'"
RETIRED_KEYS = ["RedactionPromptCalibrated", "RedactionPromptCategory.Name", "RedactionPromptCategory.FamilyMember",
                "RedactionPromptCategory.GpPractice", "RedactionPromptCategory.Address",
                "RedactionKinshipWordsExtra", "RedactionPracticeSuffixesExtra", "RedactionNeutralTermsExtra",
                "RedactionAutoRelease"]   # ADR-078 (rev 25): the process owner releases every record; a leftover row is ignored
# ADR-078: the threshold is seeded create-only at FR-029's initial 85%; a review signal, never a release gate.
THRESHOLD_SEED = "0.85"
NONE_LINE = "none"      # ADR-076 item 5: a list meant to be empty holds the single line `none`


@dataclass(frozen=True)
class SettingRow:
    name: str
    value: str | None
    modified: str | None


def redaction_rows(settings: dict, modified: dict | None = None) -> list[SettingRow]:
    modified = modified or {}
    return [SettingRow(n, v, modified.get(n, DEFAULT_MODIFIED)) for n, v in settings.items()
            if n.lower().startswith("redaction")]


def row(rows: list[SettingRow], name: str) -> SettingRow | None:
    return next((r for r in rows if r.name.lower() == name.lower()), None)


def valid_term(t: str) -> bool:
    """2 to 40 characters of a-z, space, hyphen and apostrophe, with at least one letter."""
    return 2 <= len(t) <= 40 and all(c in WORD_LIST_CHARS for c in t) \
        and bool(t.replace(" ", "").replace("-", "").replace("'", ""))


def as_word_form(entry: str) -> str:
    """An entry as the residue word string reads text: '-' and an apostrophe to a space."""
    s = entry.replace("-", " ").replace("'", " ")
    for _ in range(3):
        s = s.replace("  ", " ")
    return s.strip()


def _has_text(value: str | None) -> bool:
    return bool((value or "").replace("\r", "").replace("\n", "").strip())


def parse_word_list(value: str | None) -> list[str] | None:
    """RedactionStreetWordsExtra / RedactionPracticeWordsExtra (ADR-074 item 4): one entry per line. The
    entries in residue form, or None when the row is invalid as a whole (incl. blank)."""
    if not _has_text(value):
        return None
    out = []
    for line in (value or "").split("\n"):
        e = line.strip().lower()
        if not e:
            continue
        if not valid_term(e):
            return None
        out.append(as_word_form(e))
    return out


def valid_neutral_side(t: str) -> bool:
    """ADR-076 item 5: 1 to 40 characters of letters, spaces, hyphens and apostrophes, with a letter."""
    return 1 <= len(t) <= 40 and all(c in WORD_LIST_CHARS for c in t) \
        and bool(t.replace(" ", "").replace("-", "").replace("'", ""))


def _lines(value: str | None) -> list[str]:
    """Every non-blank line, trimmed; a `none` line is the intended-empty marker and is dropped."""
    out = []
    for line in (value or "").split("\n"):
        e = line.strip()
        if e and e.lower() != NONE_LINE:
            out.append(e)
    return out


def neutral_targets(right: str) -> list[str]:
    """`their or them` -> ['their', 'them']: the words P2 allows (hyphens to spaces, as P2 reads text)."""
    return p2_words(right.replace(" or ", " "))


def parse_neutral_terms(value: str | None) -> list[tuple[str, list[str]]] | None:
    """RedactionNeutralTerms: one `word = neutral word` per line, or `word = first or second`. Returns
    (word, [alternatives]) pairs, or None when the row is invalid as a whole: absent or blank, a line
    without exactly one '=', a side that is not a valid term, or a right-hand word that is also a
    left-hand word (it would let the prompt write a word P3 then flags)."""
    if not _has_text(value):
        return None
    out = []
    for line in _lines(value):
        e = line.lower()
        parts = e.split("=")
        w, n = parts[0].strip(), parts[-1].strip()
        if len(parts) != 2 or not valid_neutral_side(w) or not valid_neutral_side(n):
            return None
        out.append((w, [a.strip() for a in n.split(" or ")]))
    lefts = {w for w, _ in out}
    if any(t in lefts for _, alts in out for a in alts for t in neutral_targets(a)):
        return None
    return out


def parse_titles(value: str | None) -> list[str] | None:
    """RedactionTitles: one title per line, 1 to 10 letters with an optional full stop. Returned without
    the stop and with the capitals as written: P3 matches them case-sensitively (*Ms Smith*, not *MS*)."""
    if not _has_text(value):
        return None
    out = []
    for line in _lines(value):
        t = line[:-1] if line.endswith(".") else line
        if not 1 <= len(t) <= 10 or any(c not in LETTERS for c in t):
            return None
        out.append(t)
    return out


def parse_labels(value: str | None) -> list[str] | None:
    """RedactionLabels: `[LABEL] = what it covers` per line; the label is capitals, digits and spaces in
    square brackets. Returns the label words (lower case, for P2), or None when the row is invalid."""
    if not _has_text(value):
        return None
    words = []
    for line in _lines(value):
        pieces = line.split("]")
        inner = pieces[0].replace("[", "")
        if not line.startswith("[") or len(pieces) < 2 or not inner.strip() \
                or any(c not in LETTERS[26:] + DIGITS + " " for c in inner):
            return None
        for w in p2_words(inner):
            if w not in words:
                words.append(w)
    return words


def parse_name_rules(value: str | None) -> str | None:
    """RedactionNameRules: free text up to the column's 4,000 characters; it feeds the prompt only."""
    return value if _has_text(value) else None


def parse_threshold_flow(value: str | None) -> float | None:
    """'0.85', '85' and '85%' all give 0.85. Anything else is None (threshold-missing-or-invalid)."""
    t = (value or "").replace("%", "").strip()
    if not t or t == "." or t.count(".") > 1 or any(c not in DIGITS + "." for c in t):
        return None
    v = float(t)
    if 1 < v <= 100:
        v = v / 100
    return v if 0 < v <= 1 else None


@dataclass(frozen=True)
class RunContext:
    """Everything the flow reads once per run, before the column loop. Built by run_context() from the
    rows; every rule-derived field comes from the SAME four rows (ADR-076 item 2)."""
    threshold: float | None = None
    stage_off: bool = False            # RedactionPromptStage = off: the kill switch
    rules_ok: bool = False             # all four rule rows valid; otherwise nothing is scrubbed
    invalid_lists: tuple = ()
    street_words: tuple = tuple(STREET_WORDS)
    practice_words: tuple = tuple(PRACTICE_WORDS)
    practice_suffixes: tuple = tuple(PRACTICE_SUFFIXES)   # rev 29: the built-ins plus the extra row, capitalised
    gendered_words: tuple = ()         # left-hand words of RedactionNeutralTerms, as typed (lower case)
    titles: tuple = ()                 # RedactionTitles, capitals as written, no full stop
    closed: tuple = tuple(closed_words())
    neutral_terms: str = ""            # the four rewrite prompt inputs: each row as written, \r removed
    titles_text: str = ""
    name_rules: str = ""
    labels_text: str = ""
    register: frozenset | None = None
    register_available: bool = False


def _union(floor, extra) -> tuple:
    out = list(floor)
    for x in extra:
        if x not in out:
            out.append(x)
    return tuple(out)


_SEED = object()


def run_context(settings: dict, modified: dict | None = None, register=_SEED) -> RunContext:
    rows = redaction_rows(settings, modified)     # ADR-078: modifiedon is no longer read
    invalid, extra = [], {}
    for key in WORD_LIST_KEYS:
        r = row(rows, key)
        if r is None:
            extra[key] = []
            continue
        parsed = parse_word_list(r.value)
        if parsed is None:
            invalid.append(key)
        extra[key] = parsed or []
    value = {k: (row(rows, k).value if row(rows, k) else None) for k in RULE_KEYS}
    parsed = {"RedactionNeutralTerms": parse_neutral_terms(value["RedactionNeutralTerms"]),
              "RedactionTitles": parse_titles(value["RedactionTitles"]),
              "RedactionNameRules": parse_name_rules(value["RedactionNameRules"]),
              "RedactionLabels": parse_labels(value["RedactionLabels"])}
    invalid += [k for k in RULE_KEYS if parsed[k] is None]
    rules_ok = all(parsed[k] is not None for k in RULE_KEYS)
    terms = parsed["RedactionNeutralTerms"] or []
    targets = [t for _, alts in terms for a in alts for t in neutral_targets(a)]
    codes = load_register() if register is _SEED else register
    reg = register_from_rows(codes)
    th = row(rows, "RedactionConfidenceThreshold")
    stage = row(rows, "RedactionPromptStage")
    text = {k: (v or "").replace("\r", "") for k, v in value.items()}
    return RunContext(
        threshold=parse_threshold_flow(th.value if th else None),
        stage_off=(stage.value or "").strip().lower() == "off" if stage else False,
        rules_ok=rules_ok,
        invalid_lists=tuple(invalid),
        street_words=_union(STREET_WORDS, extra["RedactionStreetWordsExtra"]),
        practice_words=_union(PRACTICE_WORDS, extra["RedactionPracticeWordsExtra"]),
        practice_suffixes=_union(PRACTICE_SUFFIXES, [capitalise_words(e) for e in extra["RedactionPracticeWordsExtra"]]),
        gendered_words=tuple(w for w, _ in terms),
        titles=tuple(parsed["RedactionTitles"] or ()),
        closed=_union(_union(closed_words(), targets), parsed["RedactionLabels"] or []),
        neutral_terms=text["RedactionNeutralTerms"], titles_text=text["RedactionTitles"],
        name_rules=text["RedactionNameRules"], labels_text=text["RedactionLabels"],
        register=frozenset(reg) if reg is not None else None,
        register_available=reg is not None,
    )


# ── Rev 30 (ADR-082): batches, offsets, the merged answer and the declared-pair rule ─────────────
# Items 1 and 2: the columns chosen are packed, in order, into calls of at most BATCH_LIMIT characters
# (separators included), one extractor call per batch; each entity goes back to its column by offset.
BATCH_LIMIT = 5000          # E2: "Documents can't exceed 5,000 characters" (Compose_constants.batchLimit)
BATCH_SEPARATOR = "\n\n"     # two line feeds (Compose_constants.separator)
CORRECTIONS_MARK = "###CORRECTIONS###"   # item 5 (Compose_constants.correctionsMark)


def plan_batches(lengths: list[int]) -> list[list[int]]:
    """Next fit: a column joins the open batch when batch + separator + column is at most BATCH_LIMIT, else it
    opens the next. Order kept, no column split, no look-back. No column: no batch, so no call."""
    batches: list[list[int]] = []
    used = 0
    for i, n in enumerate(lengths):
        if batches and used + len(BATCH_SEPARATOR) + n <= BATCH_LIMIT:
            batches[-1].append(i)
            used += len(BATCH_SEPARATOR) + n
        else:
            batches.append([i])
            used = n
    return batches


def batch_layout(texts: list[str]) -> list[tuple[int, int]]:
    """(start, end) of each column in the joined text. Select_batch_layout: start is the length of the
    joined earlier columns plus one separator; end is start plus the column's length."""
    out = []
    for i, t in enumerate(texts):
        start = 0 if i == 0 else len(BATCH_SEPARATOR.join(texts[:i])) + len(BATCH_SEPARATOR)
        out.append((start, start + len(t)))
    return out


def map_entities(texts: list[str], ents: list[ExtractorEntity]) -> list[list[ExtractorEntity]]:
    """Per column, the entities that TOUCH it (start < end and start + length > start of the column), rebased to
    the column and clamped to it, with `crosses` when it is not wholly inside. An entity inside the separator
    touches no column and is dropped (Filter_column_entities, Select_column_entities)."""
    out = []
    for start, end in batch_layout(texts):
        col = []
        for e in ents:
            si, ln = int(e.startIndex or 0), int(e.length or 0)
            if si < end and si + ln > start:
                col.append(ExtractorEntity(
                    e.type, e.value, max(min(si - start, end - start), 0),
                    max(min(si + ln, end) - max(si, start), 0), e.score, si < start or si + ln > end))
        out.append(col)
    return out


def split_answer(text: str) -> tuple[str, list[str]]:
    """Item 5: the answer is split at the FIRST CORRECTIONS_MARK; the text before it (white space trimmed, as
    the flow's trim()) is the rewrite, each line after it a declared correction. No mark: no corrections."""
    i = text.find(CORRECTIONS_MARK)
    if i < 0:
        return text.strip(), []
    return text[:i].strip(), [ln.replace("\r", "") for ln in text[i + len(CORRECTIONS_MARK):].split("\n")]


PAIR_MAX_LENGTH_CHANGE = 2   # the pair rule's number (Select_valid_corrections), a constant not a setting


def _word_ok(w: str) -> bool:
    """Letters, with an optional INTERNAL hyphen or apostrophe: first and last character are letters."""
    return bool(w) and w[0] in LETTERS and w[-1] in LETTERS and all(c in LETTERS or c in "-'" for c in w)


def input_case_words(labelled: str) -> set:
    """Compose_check_texts.inputCase: the labelled text with labels removed and punctuation to spaces, CASE KEPT."""
    s = remove_labels(labelled).replace("’", "'")
    for ch in WORD_PUNCT:
        s = s.replace(ch, " ")
    return set(_collapse(s).split())


def valid_corrections(labelled: str, declared: list[str], closed=None, gendered=None) -> list[str]:
    """Item 6, the pair rule: a declared `wrong=>right` is valid when `wrong` is a word of the labelled input as
    written there and starts with a lower-case letter, `right` starts with the same letter, their lengths differ by
    at most two, both are letters (an optional internal hyphen or apostrophe, no brackets), `wrong` is not a
    closed-list word and `right` is not a gendered word. Returns the valid `right` words, lower case.
    A line that is not `word=>word` is ignored."""
    closed = SEED_CONTEXT().closed if closed is None else closed
    gendered = SEED_CONTEXT().gendered_words if gendered is None else gendered
    given = input_case_words(labelled)
    out = []
    for line in declared:
        parts = line.strip().split("=>")
        if len(parts) != 2:
            continue
        w, r = parts[0].strip(), parts[1].strip()
        if not (_word_ok(w) and _word_ok(r)) or w[0] not in LOWER or r[0] != w[0]:
            continue
        if abs(len(r) - len(w)) > PAIR_MAX_LENGTH_CHANGE or w not in given:
            continue
        if core(w) in closed or core(r) in gendered:
            continue
        out.append(r.lower())
    return out


# ── Step 5-7: checks P1, P2 and P3 (ADR-075 items 5-7) ─────────────────────────────────────────
def surviving_identifiers(final: str, values) -> list[str]:
    """P1: every normalised extractor value found at word boundaries in the final text."""
    f = " " + normalise(final) + " "
    return [v for v in values if v.strip() and f" {v} " in f]


def validate_rewrite(labelled: str, rewrite: str, closed=None, corrected=()) -> list[str]:
    """P2: the words of the rewrite (labels removed) that are neither a word of the labelled input, nor on
    the closed list, nor a plural-agreement form of an input word (`rely` when `relies` is in the input).
    Empty = valid. Anything the model writes is therefore a word it was given after labelling, or a word
    the flow holds: it cannot add an identifier, only move or drop words already there.
    Rev 30 (ADR-082 item 6): a word is also allowed when it is the corrected half of a declared correction that
    passed the pair rule (`corrected`, from valid_corrections)."""
    closed = SEED_CONTEXT().closed if closed is None else closed
    given = set(p2_words(labelled))
    added = []
    for w in p2_words(rewrite):
        if w in given or w in closed or w in corrected or w + "s" in given or w + "es" in given \
                or (w.endswith("y") and w[:-1] + "ies" in given):
            continue
        added.append(w)
    return added


def dropped_text(labelled: str, rewrite: str) -> bool:
    """A rewrite more than 10% shorter in words than its input (labels removed from both)."""
    return 10 * len(p2_words(rewrite)) < 9 * len(p2_words(labelled))


# Iteration 11: a fidelity check, like dropped_text. DEV 2026-10-19: the rewrite model dropped full stops and
# commas in several columns; nothing in the flow removes punctuation (rev 30: the prompt corrects spelling, and a
# declared pair must be letters only). Write and hold when the rewrite has at least two FEWER marks than
# its input AND more than 10% fewer: one title written "Mr." removed costs one mark and is not held.
FIDELITY_PUNCT = ".,;:!?"


def punct_count(s: str) -> int:
    return sum(s.count(ch) for ch in FIDELITY_PUNCT)


def dropped_punctuation(labelled: str, rewrite: str) -> bool:
    a, b = punct_count(labelled), punct_count(rewrite)
    return a - b >= 2 and 10 * b < 9 * a


def residue_kinds(final: str, ctx: RunContext | None = None, joined: bool = False) -> list[str]:
    """P3, on the final text with every label replaced by '|', so a label never trips a check. `joined`: the
    input side of `name-fragment` (joined_spans found a kept span with a fragment joined to it)."""
    ctx = ctx or SEED_CONTEXT()
    bare = remove_labels(final, "|")
    w = word_string(bare)
    spaced = bare
    for ch in NORM_PUNCT:                 # capitals kept: a title is matched as written (ADR-076)
        spaced = spaced.replace(ch, " ")
    spaced = " " + _collapse(spaced) + " "
    found = {
        "digit-run": "999999999" in digit_string(bare),
        "postcode": bool(shape_hits(class_string(bare), POSTCODE_RESIDUE_SHAPES)),
        "at-sign": "@" in bare,
        "street-word": any(f" {x} " in w for x in ctx.street_words),
        "practice-word": any(f" {x} " in w for x in ctx.practice_words),
        "age-phrase": any(x in w for x in AGE_PHRASES),
        "district": has_residual_district(bare, ctx.register),
        "gendered-term": any(f" {as_word_form(x)} " in w for x in ctx.gendered_words),
        "title": any(f" {t} " in spaced for t in ctx.titles),
        "name-fragment": joined or final_joint(final),
    }
    return [k for k in RESIDUE_KINDS if found[k]]


# ── One column, one record ─────────────────────────────────────────────────────────────────────
@dataclass
class ColumnOutcome:
    status: str                      # "empty" | "kept" | "too-long" | "error" | "scrubbed"
    labelled: str | None = None      # what the rewrite prompt received
    final: str | None = None         # what would be written
    score: float = NO_SCORE          # lowest score of a labelled span; NO_SCORE when none
    reasons: list = field(default_factory=list)
    write: bool = False


def _answer(call, **inputs):
    """A prompt call: (usable, rewrite, declared corrections). Any failure, a non-stop finish or an empty rewrite
    (the text before the first CORRECTIONS_MARK) is unusable (Compose_rewrite)."""
    try:
        ans = call(**inputs) or {}
    except Exception:  # noqa: BLE001 - any failure of the call is handled, by design
        return False, "", []
    text, reason = ans.get("text"), ans.get("finishReason")
    rw, declared = split_answer(text if isinstance(text, str) else "")
    usable = isinstance(reason, str) and reason.lower() == "stop" and isinstance(text, str) and bool(rw)
    return usable, rw, declared


def column_state(text: str | None, existing: str | None) -> str:
    if text is None or not text.strip():
        return "empty"
    if existing is not None and existing.strip():
        return "kept"
    if len(text) > EXTRACTOR_MAX_CHARS:
        return "too-long"
    return "scrub"


def scrub_column(key: str, text: str, ents, rewrite, ctx: RunContext) -> ColumnOutcome:
    """A column already chosen for scrubbing. `ents` is this column's entities from its batch's call, mapped by
    offset (map_entities), or None when the batch's call failed or answered at neither entity path (every column of
    the batch is then ai-error, ADR-082 item 3); `rewrite(Narrative=, NeutralTerms=, Titles=, NameRules=, Labels=)`
    returns {"text", "finishReason"}, the merged answer of ADR-082 item 5."""
    if not isinstance(ents, list):
        return ColumnOutcome("error", reasons=[f"ai-error:{key}"])
    lab, kept, unmapped, partial = label_spans(text, ents, ctx.practice_suffixes)
    labelled = labelled_text(text, kept)
    usable, rw, declared = _answer(rewrite, Narrative=labelled, NeutralTerms=ctx.neutral_terms, Titles=ctx.titles_text,
                                   NameRules=ctx.name_rules, Labels=ctx.labels_text)
    final = rw                       # Compose_final_text is an alias of the rewrite
    p1 = surviving_identifiers(final, [s.value for s in lab])
    p2 = validate_rewrite(labelled, rw, ctx.closed, valid_corrections(labelled, declared, ctx.closed, ctx.gendered_words))
    write = usable and not partial and not p1 and not p2 and len(final) <= REDACTED_MAX_CHARS
    reasons = []
    if unmapped:
        reasons.append(f"unmapped-entity-type:{key}")
    if partial:
        reasons.append(f"overlapping-identifiers:{key}")
    if not usable:
        reasons.append(f"prompt-error:{key}")
    if usable and p1:
        reasons.append(f"identifier-survived:{key}")
    if usable and p2:
        reasons.append(f"rewrite-invalid:{key}")
    if usable and len(final) > REDACTED_MAX_CHARS:
        reasons.append(f"redacted-exceeds-{REDACTED_MAX_CHARS}:{key}")
    if write:
        reasons += [f"residual-{k}:{key}" for k in residue_kinds(final, ctx, bool(joined_spans(text, kept)))]
        if dropped_text(labelled, rw):
            reasons.append(f"rewrite-dropped-text:{key}")
        if dropped_punctuation(labelled, rw):
            reasons.append(f"rewrite-dropped-punctuation:{key}")
    score = min([s.score for s in lab] + [NO_SCORE])
    return ColumnOutcome("scrubbed", labelled, final, score, reasons, write)


@dataclass(frozen=True)
class FlowDecision:
    released: bool
    review_required: bool
    confidence: float | None
    reasons: tuple[str, ...]


def flow_scrub_record(row_: dict, settings, extract, rewrite, *, modified: dict | None = None,
                      register=_SEED) -> tuple[FlowDecision | None, dict, list]:
    """The whole flow for one application row -> (decision, writes, outcomes). A released record is
    never touched: (None, {}, [])."""
    if row_.get("rev_redactionreleased") is True:
        return None, {}, []
    ctx = settings if isinstance(settings, RunContext) else run_context(settings, modified, register)
    loop_reasons, not_scrubbed, writes, outcomes, scores = [], [], {}, [], []
    any_scrubbed = False
    states = [(raw, red, column_state(row_.get(raw), row_.get(red))) for raw, red in SCRUB_COLUMNS]
    chosen = [raw for raw, _, st in states if st == "scrub" and not ctx.stage_off and ctx.rules_ok]
    # ADR-082 items 1-3: the chosen columns are packed into batches, one extractor call per batch, each entity back
    # to its column by offset; a failed or unreadable call is None for every column of its batch.
    mapped: dict = {}
    for batch in plan_batches([len(row_[raw]) for raw in chosen]):
        names = [chosen[i] for i in batch]
        texts = [row_[n] for n in names]
        try:
            ents = extract(BATCH_SEPARATOR.join(texts))
        except Exception:  # noqa: BLE001
            ents = None
        per = map_entities(texts, ents) if isinstance(ents, list) else [None] * len(names)
        mapped.update(zip(names, per))
    for raw, red, state in states:
        if state == "kept":
            not_scrubbed.append(f"kept-existing-counterpart:{raw}")
        elif state == "too-long":
            not_scrubbed.append(f"too-long:{raw}")
        if raw not in mapped:
            outcomes.append(ColumnOutcome(state if state != "scrub" else "not-run"))
            continue
        o = scrub_column(raw, row_[raw], mapped[raw], rewrite, ctx)
        outcomes.append(o)
        loop_reasons += o.reasons
        if o.status == "scrubbed":
            any_scrubbed = True
            scores.append(o.score)
        if o.write:
            writes[red] = o.final
    low = min(scores + [NO_SCORE])
    confidence = None if low >= NO_SCORE else low
    record = []
    if ctx.threshold is None:
        record.append("threshold-missing-or-invalid")
    if any_scrubbed and confidence is None:
        record.append("no-model-detections")
    if ctx.threshold is not None and confidence is not None and confidence < ctx.threshold:
        record.append("below-threshold")
    if not ctx.register_available:
        record.append("postcode-register-unavailable")
    record += [f"redaction-setting-invalid:{k}" for k in ctx.invalid_lists]
    if ctx.stage_off:
        record.append("prompt-stage-off")
    reasons = []
    for r in loop_reasons + not_scrubbed + record:
        if r and r not in reasons:
            reasons.append(r)
    # ADR-078: the flow never releases; every scrubbed record waits for the process owner, and the reasons
    # are hints on her card. `released` is what the flow leaves behind: always False (the column's default).
    return FlowDecision(False, True, confidence, tuple(reasons)), writes, outcomes


# ════════════════════════════════════════════════════════════════════════════════════════════════
# THE FOUR RULE ROWS — seed values (TAD rev 23, ADR-076 "Seed values"; SDD A-09; reviewer 2026-10-16)
# ════════════════════════════════════════════════════════════════════════════════════════════════
# These are what seed-settings.ps1 creates, once, in each environment (createOnly; A-NS-36). After that
# only the process owner changes them. The three deploymentSettings files carry the same text and
# test_scrub_flow_definition.py asserts it; test_neutral_terms.py proves the neutral-terms row says
# exactly what NEUTRAL_TERMS (the oracle's expected map) says.
_PRONOUN_LINES = [
    "he = they", "she = they", "him = them", "her = their or them", "his = their or theirs", "hers = theirs",
    "himself = themself", "herself = themself", "he's = they're or they've", "she's = they're or they've",
    "he'd = they'd", "she'd = they'd", "he'll = they'll", "she'll = they'll",
]
_NOUN_GROUPS = [
    (["mum", "mummy", "mother", "dad", "daddy", "father"], "parent",
     ["mums", "mummies", "mothers", "dads", "daddies", "fathers"], "parents"),
    (["brother", "sister"], "sibling", ["brothers", "sisters"], "siblings"),
    (["son", "daughter"], "child", ["sons", "daughters"], "children"),
    (["husband", "wife", "boyfriend", "girlfriend"], "partner",
     ["husbands", "wives", "boyfriends", "girlfriends"], "partners"),
    (["man", "woman", "boy", "girl", "lady", "gentleman"], "person",
     ["men", "women", "boys", "girls", "ladies", "gentlemen"], "people"),
    (["grandmother", "grandfather"], "grandparent", ["grandmothers", "grandfathers"], "grandparents"),
    (["grandson", "granddaughter"], "grandchild", ["grandsons", "granddaughters"], "grandchildren"),
    (["stepson", "stepdaughter"], "stepchild", ["stepsons", "stepdaughters"], "stepchildren"),
    (["stepmother", "stepfather"], "stepparent", ["stepmothers", "stepfathers"], "stepparents"),
    (["aunt", "auntie", "uncle", "niece", "nephew"], "relative",
     ["aunts", "aunties", "uncles", "nieces", "nephews"], "relatives"),
]
SEED_ROWS = {
    "RedactionNeutralTerms": "\n".join(
        _PRONOUN_LINES
        + [f"{w} = {n}" for ws, n, _, _ in _NOUN_GROUPS for w in ws]
        + [f"{w} = {n}" for _, _, ws, n in _NOUN_GROUPS for w in ws]),
    "RedactionTitles": "\n".join(["Mr", "Mrs", "Ms", "Miss"]),
    # Iteration 11 (reviewer, 2026-10-19, "Yes please, process the suggested changes"): the writer's own name
    # keeps [NAME] ("I am they" in DEV); the relationship word leads even when others are named ("Our child
    # [NAME]" in DEV); worked examples, label-only. The rules are in the order they apply.
    "RedactionNameRules": "\n".join([
        "When [NAME] is the writer's own name, keep [NAME]. This includes \"I am [NAME]\", \"I'm [NAME]\", "
        "\"my name is [NAME]\" and any sentence where the writer says [NAME] is what they are called, such as "
        "\"[NAME] is the name my friends use for me\".",
        "Keep [NAME] after Dr: \"Dr [NAME] reviews my medication\" stays as it is.",
        "When [NAME] comes straight after a relationship word, remove it and keep the neutral word, even when the "
        "text names other people: \"my husband [NAME]\" becomes \"my partner\", and \"our son [NAME], who is "
        "[AGE 35 to 44],\" becomes \"our child, who is [AGE 35 to 44],\".",
        "Otherwise, keep [NAME] when the text names two or more different people other than the writer.",
        "If the text is about one named person, write they, them or their in place of [NAME], as the sentence needs, "
        "and make the verb agree: \"[NAME] visits me.\" becomes \"They visit me.\"",
        "A name inside the name of a GP practice is part of [GP PRACTICE].",
        "Mum or Dad used as a name, as in \"Mum helps me\", becomes \"my parent\".",
    ]),
    "RedactionLabels": "\n".join([
        "[NAME] = a person's name",
        "[ADDRESS] = a street, a house name or number, a town in an address, or a postcode",
        "[PHONE] = a phone number",
        "[EMAIL] = an email address",
        "[GP PRACTICE] = the name of a GP practice or surgery",
    ]),
}
SEED_DESCRIPTIONS = {
    "RedactionNeutralTerms": "Narrative scrubbing (TAD ADR-076): the client's Anonymisation Key. One 'word = neutral word' per line ('word = first or second' where the sentence decides). Feeds the rewrite prompt, check P2 (right side) and the gendered residue check (left side). Synthetic examples only: never paste text from an application into this row.",
    "RedactionTitles": "Narrative scrubbing (TAD ADR-076): titles the rewrite prompt removes, one per line, 1 to 10 letters with an optional full stop. Also the title residue check, matched with the capitals as written. Write 'none' for no titles. Synthetic examples only: never paste text from an application into this row.",
    "RedactionNameRules": "Narrative scrubbing (TAD ADR-076): how the rewrite prompt handles [NAME], one rule per line in plain words. Feeds the prompt only. Synthetic examples only: never paste text from an application into this row.",
    "RedactionLabels": "Narrative scrubbing (TAD ADR-076): the labels the rewrite prompt may write, '[LABEL] = what it covers', one per line, the label in capitals in square brackets. Feeds the prompt and check P2. Synthetic examples only: never paste text from an application into this row.",
}


def SEED_CONTEXT() -> RunContext:  # noqa: N802 - reads like the constant it stands for
    """The run context the seed rows give, with no other row and the seed register."""
    global _SEED_CONTEXT
    if _SEED_CONTEXT is None:
        _SEED_CONTEXT = run_context(dict(SEED_ROWS))
    return _SEED_CONTEXT


_SEED_CONTEXT = None


# ════════════════════════════════════════════════════════════════════════════════════════════════
# NEUTRAL TERMS — rules v0.5 section 10.1 (client Anonymisation Key; SDD Amendment A-09; wbs:5.6)
# ════════════════════════════════════════════════════════════════════════════════════════════════
# Reviewer decisions, Xander Lykopoulos, verbatim (relayed by lead-agent):
#   2026-10-14 "1. follow the key file"; "2. Yes also add spell checking and auto correct that for readability"
#   2026-10-16 him/hers: "Use the clients own examples"; first names: "Change to the clients key and examples";
#              "Yes, add words for these: grandmother, stepson, auntie, niece, nephew, mummy, lady, and the
#              titles Mr, Mrs, Ms and Miss."; and: "if the second word that belongs to end is identifyable
#              information than it also needs to change."
#   2026-10-16 (correcting the OQ-054 default, after A-09's approval): "My husband Derek becoms partner. not
#              family member. the word husband is leading in this pattern."
#   SDD A-09 approved 2026-10-16 with OQ-054 to OQ-056 at their defaults, OQ-054 (c) since corrected as above.
#
# THIS IS WHAT A GOOD REWRITE LOOKS LIKE, NOT WHAT THE FLOW DOES. In rev 22 the rewrite prompt does this
# work and the flow only checks it (P1, P2, P3). neutral_rewrite() is the expected output `wbs:5.7` scores
# the live model against, and the specification the tests pin. It works on LABELLED text - the text the
# prompt receives - so a name is the token "[NAME]".

# The client's key, rows 2-27, as written (column A -> column B), so a test can show every departure.
KEY_ROWS = [
    ("He", "they"), ("She", "they"), ("Him/ him.", "their"), ("Her/ her.", "Them/ their"),
    ("His", "their"), ("Hers", "their"), ("Mother.", "parent"), ("Father.", "parent"),
    ("Mum", "parent"), ("Dad", "parent"), ("Brother", "sibling"), ("Sister", "sibling"),
    ("Daughter", "child"), ("Son", "child"), ("Wife", "partner"), ("Husband", "partner"),
    ("Girlfriend", "partner"), ("Boyfrind", "partner"), ("Himself", "themselves"),
    ("herself", "themselves"), ("Man", "person"), ("Woman", "person"), ("Girl ", "person"),
    ("Boy", "person"), ("He's", "they're"), ("She's", "they're"),
]

# Where the map departs from KEY_ROWS, and why. Where the key and the client's examples differ, the
# examples win (A-09 Finding 1); OQ-056 settles the three forms neither shows.
KEY_DEVIATIONS = {
    "him": ("them", "object pronoun; the key's 'their' is a possessive, and the client's own examples write 'them'"),
    "hers": ("theirs", "OQ-056: an independent possessive, 'the choice is hers' -> 'theirs'; 'their' cannot stand alone"),
    "her": ("them|their", "the key gives both; the examples choose by the word after it (see _her_form)"),
    "boyfriend": ("partner", "key row 19 is spelt 'Boyfrind'"),
    "himself": ("themself", "OQ-056: the client's examples write 'themself' where the key says 'themselves'"),
    "herself": ("themself", "OQ-056: as 'himself', the client's own examples write 'themself'"),
}

# word (lower case) -> neutral word.
NEUTRAL_TERMS = {
    "he": "they", "she": "they", "him": "them", "his": "their", "hers": "theirs",
    "mother": "parent", "father": "parent", "mum": "parent", "dad": "parent",
    "brother": "sibling", "sister": "sibling", "daughter": "child", "son": "child",
    "wife": "partner", "husband": "partner", "girlfriend": "partner", "boyfriend": "partner",
    "himself": "themself", "herself": "themself",
    "man": "person", "woman": "person", "girl": "person", "boy": "person",
    "he's": "they're", "she's": "they're",
    # forced by "he"/"she": the contraction is one word, so "he" alone would leave "he'd"
    "he'd": "they'd", "she'd": "they'd", "he'll": "they'll", "she'll": "they'll",
    # plurals of the key's nouns
    "mothers": "parents", "fathers": "parents", "mums": "parents", "dads": "parents",
    "brothers": "siblings", "sisters": "siblings", "daughters": "children", "sons": "children",
    "wives": "partners", "husbands": "partners", "girlfriends": "partners",
    "boyfriends": "partners", "men": "people", "women": "people", "girls": "people",
    "boys": "people",
    # A-09 FR-096 / OQ-055 (defaults adopted): the reviewer's added words and their counterparts
    "grandmother": "grandparent", "grandfather": "grandparent", "grandmothers": "grandparents",
    "grandfathers": "grandparents", "grandson": "grandchild", "granddaughter": "grandchild",
    "grandsons": "grandchildren", "granddaughters": "grandchildren",
    "stepson": "stepchild", "stepdaughter": "stepchild", "stepsons": "stepchildren",
    "stepdaughters": "stepchildren", "stepmother": "stepparent", "stepfather": "stepparent",
    "stepmothers": "stepparents", "stepfathers": "stepparents",
    "auntie": "relative", "aunt": "relative", "uncle": "relative", "niece": "relative", "nephew": "relative",
    "aunties": "relatives", "aunts": "relatives", "uncles": "relatives", "nieces": "relatives",
    "nephews": "relatives",
    "mummy": "parent", "daddy": "parent", "mummies": "parents", "daddies": "parents",
    "lady": "person", "gentleman": "person",
    "ladies": "people", "gentlemen": "people",
}
ADDED_WORDS = ["grandmother", "stepson", "auntie", "niece", "nephew", "mummy", "lady"]   # FR-096, verbatim
TITLES = ["mr", "mrs", "ms", "miss"]          # FR-096: removed; the name after is handled under FR-095
KEEP_NAME_AFTER = ["dr", "doctor"]            # OQ-054 (b): "Dr [NAME]"
SUBJECT_PRONOUNS = {"he", "she"}
PARENT_NAMES = {"mum", "dad", "mother", "father", "mummy", "daddy"}   # "Mum helps me" uses the word as a name
# A relationship word directly before a name: the relationship leads and the name goes (reviewer, 2026-10-16:
# "My husband Derek becoms partner ... the word husband is leading in this pattern").
RELATIONSHIP_WORDS = {w for w, n in NEUTRAL_TERMS.items()
                      if n in ("parent", "parents", "sibling", "siblings", "child", "children", "partner",
                               "partners", "grandparent", "grandparents", "grandchild", "grandchildren",
                               "stepchild", "stepchildren", "stepparent", "stepparents", "relative",
                               "relatives")} | {"partner", "parent", "child", "carer", "friend", "neighbour",
                                                "cousin", "sibling", "relative", "spouse"}
_DETERMINERS = {"my", "our", "your", "his", "her", "their", "the", "a", "an", "this", "that",
                "whose", "every", "each", "no", "one's"}
_HAVE_PARTICIPLES = {"got", "been", "gone", "had", "done", "taken", "given", "seen", "made",
                     "become", "lost", "left", "started", "stopped", "always", "never", "just",
                     "already", "recently"}
_OBJECT_FOLLOWERS = {
    "to", "with", "for", "at", "in", "on", "up", "out", "off", "from", "into", "onto", "about",
    "and", "but", "or", "nor", "so", "when", "while", "whilst", "because", "if", "as", "than",
    "that", "this", "these", "those", "the", "a", "an", "every", "each", "some", "any", "all",
    "back", "down", "over", "around", "through", "again", "too", "very", "home", "there",
    "here", "now", "then", "until", "before", "after", "by", "like", "since", "during",
    "regularly", "daily", "often", "always", "safe", "calm", "settled", "feel",
    "know", "get", "go", "be", "is", "was", "are", "were", "can", "will", "would", "could",
    "should", "may", "might", "must", "do", "does", "did", "has", "have", "had", "i", "we",
    "you", "they", "he", "she", "it", "me", "us", "them", "him", "her", "my", "our", "your",
}
_CAUSATIVE = {"help", "helps", "helped", "helping", "let", "lets", "letting", "make", "makes",
              "made", "making", "watch", "watches", "watched", "watching", "see", "sees", "saw",
              "seeing", "hear", "hears", "heard", "hearing"}
_ADVERBS = {"also", "always", "never", "often", "really", "still", "just", "usually",
            "sometimes", "regularly", "only", "even", "already", "then", "now", "constantly",
            "frequently", "rarely", "generally", "normally", "actually", "simply", "mostly",
            "completely", "totally", "hardly", "barely", "gradually", "quickly", "easily",
            "occasionally", "currently", "increasingly", "particularly", "especially"}
_IRREGULAR_3SG = {"is": "are", "was": "were", "has": "have", "does": "do", "goes": "go",
                  "isn't": "aren't", "wasn't": "weren't", "hasn't": "haven't",
                  "doesn't": "don't", "isn’t": "aren’t", "wasn’t": "weren’t",
                  "hasn’t": "haven’t", "doesn’t": "don’t"}
_NOT_VERBS_ENDING_S = {"this", "its", "his", "hers", "us", "yes", "less", "unless", "always",
                       "perhaps", "sometimes", "towards", "afterwards", "besides", "thus"}
NAME_TOKEN = "[NAME]"
_WORD = re.compile(r"\[NAME\]|[A-Za-z]+(?:['’][A-Za-z]+)?")
_CLAUSE_END = ".!?;:\n"
AND_LOOKAHEAD = 8   # FR-098: a second verb after "and" is agreed within this many words of the first


def _with_case(src: str, word: str, at_start: bool) -> str:
    """ALL CAPS stays all caps. Otherwise capitalised only where the replaced word was capitalised AND
    starts a sentence: "I told Mum" -> "I told my parent", "My Mum" -> "My parent"."""
    if src.isupper() and len(src) > 1 and src != NAME_TOKEN:
        return word.upper()
    if at_start and (src[:1].isupper() or src == NAME_TOKEN):
        return word[:1].upper() + word[1:]
    return word


def _sentence_start(text: str, start: int) -> bool:
    before = text[:start].rstrip(" \t\"'“‘(")
    return before == "" or before[-1] in ".!?\n:"


def _her_form(words: list, i: int, text: str) -> str:
    """'her' is 'them' (object) or 'their' (possessive), read from the words around it."""
    nxt = words[i + 1] if i + 1 < len(words) else None
    gap = "" if nxt is None else text[words[i][1]:nxt[0]]
    if nxt is None or gap.strip(" ") != "":
        return "them"
    nw = nxt[2].lower()
    if nw in NEUTRAL_TERMS and nw not in SUBJECT_PRONOUNS | {"him", "his", "hers"}:
        return "their"
    prev = words[i - 1][2].lower() if i > 0 else ""
    if prev in _CAUSATIVE:
        return "them"
    return "them" if nw in _OBJECT_FOLLOWERS else "their"


def _agree(verb: str) -> str | None:
    """Third person singular -> plural, or None when the word is not a 3sg verb form."""
    low = verb.lower()
    if low in _IRREGULAR_3SG:
        return _with_case(verb, _IRREGULAR_3SG[low], verb[:1].isupper())
    if low in _NOT_VERBS_ENDING_S or not low.endswith("s") or low.endswith(("ss", "us", "is")) \
            or "'" in low or "’" in low or len(low) < 3 or verb == NAME_TOKEN:
        return None
    if low.endswith("ies") and len(low) > 4 and low[-4] not in "aeiou":
        return verb[:-3] + "y"
    if low.endswith(("sses", "shes", "ches", "xes", "zes", "oes")):
        return verb[:-2]
    return verb[:-1]


def _same_clause(text: str, a: int, b: int) -> bool:
    return not any(c in _CLAUSE_END for c in text[a:b])


def _adjacent(text, words, j) -> bool:
    return text[words[j - 1][1]:words[j][0]].strip() == ""


def _agreements(text: str, words: list, i: int, agreed: set) -> list[tuple[int, str]]:
    """The verb after subject word i, and (FR-098) a second verb after 'and' in the same clause."""
    out = []
    j = i + 1
    while j < len(words) and words[j][2].lower() in _ADVERBS and _adjacent(text, words, j):
        j += 1
    if j >= len(words) or j in agreed or not _adjacent(text, words, j):
        return out
    base = _agree(words[j][2])
    if base is None or base == words[j][2]:
        return out
    out.append((j, base))
    for k in range(j + 1, min(j + 1 + AND_LOOKAHEAD, len(words) - 1)):
        if not _same_clause(text, words[j][1], words[k][0]):
            break
        if words[k][2].lower() in ("he", "she", "they", "i", "we", "you", "it", NAME_TOKEN.lower()):
            break
        if words[k][2].lower() == "and":
            m = k + 1
            while m < len(words) and words[m][2].lower() in _ADVERBS and _adjacent(text, words, m):
                m += 1
            # the word must be followed by more of the same clause: "and requires care", not "and dogs."
            if m + 1 < len(words) and _adjacent(text, words, m) and _same_clause(text, words[m][1], words[m + 1][0]):
                b2 = _agree(words[m][2])
                if b2 is not None and b2 != words[m][2] and m not in agreed:
                    out.append((m, b2))
            break
    return out


def _self_name(words: list, i: int, text: str) -> bool:
    """The writer's own name (Iteration 11): "I am [NAME]", "I'm [NAME]", "my name is [NAME]"; and (DEV 2026-10-20,
    TD-15 "they is the name my friends use for me") a sentence where the writer says [NAME] is what they are called:
    "[NAME] is the name …", "[NAME] is what … call me", "… call me [NAME]"."""
    def w(k):
        j = i - k
        return words[j][2].lower().replace("’", "'") if 0 <= j < len(words) else ""
    if ((w(-1), w(-2), w(-3)) == ("is", "the", "name") and w(-4) != "of") or (w(-1), w(-2)) == ("is", "what"):
        return True
    if w(2) in ("call", "calls") and w(1) == "me":
        return True

    def tight(k):     # word i-k and the next one are separated by spaces only
        return text[words[i - k][1]:words[i - k + 1][0]].strip(" ") == ""
    if w(1) == "i'm" and tight(1):
        return True
    if (w(2), w(1)) == ("i", "am") and tight(1) and tight(2):
        return True
    return (w(3), w(2), w(1)) == ("my", "name", "is") and tight(1) and tight(2) and tight(3)


def _name_pass(text: str, people: int, titles=None) -> str:
    """FR-095 as corrected on 2026-10-16, and the RedactionNameRules seed row of Iteration 11, in its order:
    the writer's own name keeps [NAME]; after Dr it keeps [NAME] (OQ-054 b); after a relationship word it
    goes and the relationship word leads, even when others are named (reviewer's correction of c); otherwise
    with two or more different people named it keeps [NAME] (OQ-054 a); a title before it goes (FR-096);
    "[NAME]'s" becomes "their"; as a subject it becomes "They" with its verb agreed; anywhere else "them"."""
    titles = TITLES if titles is None else titles
    if NAME_TOKEN not in text:
        return text
    words = [(m.start(), m.end(), m.group(0)) for m in _WORD.finditer(text)]
    # SDD A-11, OQ-054 (e), reviewer 2026-10-19: the writer's own name does not count toward "two or more
    # different people" ("I am Sam and Pat helps me" -> "I am [NAME] and they help me").
    if any(w == NAME_TOKEN and _self_name(words, i, text) for i, (_, _, w) in enumerate(words)):
        people -= 1
    edits, agreed = [], set()
    for i, (s, e, w) in enumerate(words):
        if w != NAME_TOKEN:
            continue
        prev = words[i - 1] if i > 0 else None
        gap = text[prev[1]:s] if prev else ""
        pw = prev[2].lower() if prev else ""
        if prev and pw in KEEP_NAME_AFTER and gap.strip(" .") == "":
            continue
        if _self_name(words, i, text):
            continue
        cut = s
        if prev and pw in titles and gap.strip(" .") == "":
            cut = prev[0]
            prev2 = words[i - 2] if i > 1 else None
            pw, prev = (prev2[2].lower(), prev2) if prev2 else ("", None)
            gap = text[prev[1]:cut] if prev else ""
        tail = text[e:e + 2]
        if prev and pw in RELATIONSHIP_WORDS and gap.strip(" ") == "":
            edits.append((prev[1], e, ""))                        # "my husband [NAME]" -> "my husband"
            continue
        if people >= 2:
            continue
        if tail in ("'s", "’s"):
            edits.append((cut, e + 2, _with_case("[NAME]", "their", _sentence_start(text, cut))))
            continue
        nxt = i + 1
        while nxt < len(words) and words[nxt][2].lower() in _ADVERBS and _adjacent(text, words, nxt):
            nxt += 1
        subject = _sentence_start(text, cut) or (
            nxt < len(words) and _adjacent(text, words, nxt) and _agree(words[nxt][2]) is not None)
        if subject:
            edits.append((cut, e, _with_case(NAME_TOKEN, "they", _sentence_start(text, cut))))
            for j, base in _agreements(text, words, i, agreed):
                agreed.add(j)
                edits.append((words[j][0], words[j][1], base))
        else:
            edits.append((cut, e, "them"))
    out = text
    for a, b, new in sorted(edits, key=lambda x: x[0], reverse=True):
        out = out[:a] + new + out[b:]
    return out


def _term_pass(text: str, terms: dict, titles) -> str:
    """FR-094, FR-096, FR-097 and the agreement FR-098 needs after a replaced 'he' or 'she'. `terms` maps a
    word to its first neutral word; 'her', 'his' and "he's" keep their reading rules when they are in it."""
    words = [(m.start(), m.end(), m.group(0)) for m in _WORD.finditer(text)]
    edits, agreed = [], set()
    for i, (s, e, w) in enumerate(words):
        low = w.lower().replace("’", "'")
        if w == NAME_TOKEN:
            continue
        if low in titles:
            nxt = text[e:e + 2]
            cut_end = e + (1 if nxt[:1] == "." else 0)
            cut_end += 1 if text[cut_end:cut_end + 1] == " " else 0
            edits.append((s, cut_end, ""))                        # "Mrs Patel" -> "Patel" (the name goes to FR-095)
            continue
        poss = ""
        if low not in terms and low.endswith("'s") and low[:-2] in terms and low[:-2] not in SUBJECT_PRONOUNS:
            poss, low, w = w[-2:], low[:-2], w[:-2]                # "my wife's car" -> "my partner's car"
        if low == "her" and "her" in terms:
            new = _her_form(words, i, text)
        elif low not in terms:
            continue
        elif low in ("he's", "she's"):
            nxt = words[i + 1][2].lower() if i + 1 < len(words) else ""
            new = "they've" if nxt in _HAVE_PARTICIPLES else "they're"
            if "’" in w:
                new = new.replace("'", "’")
        elif low == "his" and (i + 1 >= len(words) or text[e:words[i + 1][0]].strip(" ") != ""):
            new = "theirs"                                         # OQ-056: "the car is his."
        elif low in PARENT_NAMES and w[:1].isupper() and \
                (i == 0 or words[i - 1][2].lower() not in _DETERMINERS):
            new = "my parent"
        else:
            new = terms[low]
            if "’" in w:
                new = new.replace("'", "’")
        edits.append((s, e, _with_case(w, new, _sentence_start(text, s)) + poss))
        if low in SUBJECT_PRONOUNS:
            for j, base in _agreements(text, words, i, agreed):
                agreed.add(j)
                edits.append((words[j][0], words[j][1], base))
    out = text
    for a, b, new in sorted(edits, key=lambda x: x[0], reverse=True):
        out = out[:a] + new + out[b:]
    return out


def neutral_rewrite(labelled: str, people: int = 1, terms=None, titles=None) -> str:
    """What a good rewrite of a labelled text looks like (A-09). `people` is how many different people the
    extractor named in the column. `terms` is a parsed RedactionNeutralTerms row and `titles` a parsed
    RedactionTitles row (default: the seed rows, which test_neutral_terms.py proves equal NEUTRAL_TERMS)."""
    if terms is None:
        terms = parse_neutral_terms(SEED_ROWS["RedactionNeutralTerms"])
    tmap = {w: alts[0] for w, alts in terms}
    tset = {t.lower() for t in (parse_titles(SEED_ROWS["RedactionTitles"]) if titles is None else titles)}
    return _term_pass(_name_pass(labelled, people, tset), tmap, tset)


def people_named(entities: list[ExtractorEntity]) -> int:
    return len({normalise(e.value) for e in entities if EXTRACTOR_TYPE_CODE.get(e.type) == "N"})


def expected_scrub(text: str, entities: list[ExtractorEntity], terms=None, titles=None) -> str:
    """Labels (step 2) then the good rewrite: the expected trustee text for one column."""
    _, kept, _, _ = label_spans(text, entities)
    return neutral_rewrite(labelled_text(text, kept), people_named(entities), terms, titles)


def gendered_residue(text: str) -> list[str]:
    """Seeded key words and titles still present: what P3's gendered and title checks see."""
    ctx = SEED_CONTEXT()
    w = word_string(remove_labels(text, "|"))
    spaced = remove_labels(text, "|")
    for ch in NORM_PUNCT:
        spaced = spaced.replace(ch, " ")
    spaced = " " + _collapse(spaced) + " "
    return [g for g in ctx.gendered_words if f" {as_word_form(g)} " in w] + [t for t in ctx.titles if f" {t} " in spaced]


# Rows 30-44 of the key ("Free text questions") -> the raw column the intake writes (TAD Appendix C
# intake map). Three have no counterpart and get none (reviewer, 2026-10-16: "All fields in the trustee
# portal right now is what the trustees use to make their decisions on.").
FREE_TEXT_QUESTIONS = [
    ("Other conditions or illnesses affect you", "rev_otherconditionraw"),
    ("Brief confirmation", "rev_disabilityimpactdescription"),
    ("Brief description", "rev_caresupportdescription"),
    ("Other conditions or illnesses", "rev_supportrecipientotherconditionraw"),
    ("Brief confirmation13", "rev_supportrecipientdisabilityimpactdescription"),  # A-NS-28, E3 (TAD rev 22)
    ("Other types of care and support personally provided", "rev_othercareprovidedtype"),
    ("Please provide one brief example of the level of care required", "rev_careprovidedexample"),
    ("Benefit provider", "rev_benefitprovider"),
    ("Please briefly explain the significant care costs or medical expenses", "rev_carecostsexplanation"),
    ("Please briefly explain why you're unable to fund this break yourself", "rev_unabletofundexplanation"),
    ("Please specify source of additional funding", "rev_otherfundingsource"),
    ("Awaiting decision from", "rev_awaitingdecisionfrom"),
    ("Other exceptional circumstance", "rev_otherexceptionalcircumstance"),
    ("Briefly explain exceptional circumstance", "rev_exceptionalfundingdetail"),
    ("Please briefly explain how this break would benefit you", "rev_narrativeraw"),
]


# ── EXTENSION POINT: indirect identifiers (OUT of v0.1) ────────────────────────────────────────
# Reviewer decision 2026-10-05: indirect identifiers (family composition such as "how many
# sisters", "living with" + postcode, household make-up, rare circumstances) are added after
# Emily's input. Each future rule is a function (text, detections) -> extra detections, appended
# here and run inside redact_column() after rule_detections(). Adding one changes no other code:
# merge(), apply() and decide() already treat every detection the same way.
INDIRECT_RULES: list = []
