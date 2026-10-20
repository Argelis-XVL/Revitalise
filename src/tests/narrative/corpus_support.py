#!/usr/bin/env python3
"""Shared test support for the narrative suite (wbs:5.2, 5.3): the simulated extractor over the 20-sample
synthetic corpus, and stand-ins for the two prompts. Not a test module.

The simulated extractor is 'perfect' in the way the platform documents it (E2): it returns names, GP
practices (Organization), ages, emails and the STREET part of an address. It does NOT return UK phone
numbers or postcodes, which Microsoft documents as US-format only. In rev 22 nothing deterministic finds
those any more: the rewrite prompt labels them, and the residue checks hold the record when it does not.

The prompt stand-ins are what the tests feed the SHIPPED flow and the oracle alike. `good_rewrite` is the
oracle's own neutral_rewrite (what wbs:5.7 expects of the live model); the others are bad models, written
to prove P1, P2 and the spelling rule hold against them (ADR-075, "What the tests must prove").
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import redaction_reference as rr  # noqa: E402
from test_redaction_reference import SAMPLES, parse_markup  # noqa: E402

# Rev 23 (ADR-076): the four rule rows are required; absent, nothing is scrubbed. RULES is what the
# create-only seed puts in every environment.
RULES = dict(rr.SEED_ROWS)
ALL_SETTINGS = {"RedactionConfidenceThreshold": "85", **RULES}   # ADR-078: no RedactionAutoRelease
KINDS = {"NAME": "PersonName", "FAMILY MEMBER": "PersonName", "GP PRACTICE": "Organization",
         "AGE": "Age", "EMAIL": "Email"}


def simulated_entities(sample, plain, gold, score=0.93):
    """[(type, value, start, length, score)] for one text."""
    ents = []
    for start, n, cat in gold:
        value = plain[start:start + n]
        if cat in KINDS:
            ents.append((KINDS[cat], value, start, n, score))
        elif cat == "ADDRESS":
            tail = [h for h in rr.shape_hits(rr.class_string(value), rr.POSTCODE_SHAPES) if h[0] + h[1] == len(value)]
            street = (value[:tail[0][0]] if tail else value).rstrip(", ")
            if street:
                ents.append(("StreetAddress", street, start, len(street), score))
    for x in sample.get("ai_extra", []):
        idx = -1
        for _ in range(x.get("occurrence", 1)):
            idx = plain.find(x["value"], idx + 1)
        ents.append((x["type"], x["value"], idx, len(x["value"]), x.get("score", 0.9)))
    return ents


def as_entities(ents):
    return [rr.ExtractorEntity(t, v, s, n, sc) for t, v, s, n, sc in ents]


def extractor_for(texts_and_entities, calls=None):
    """The mock extractor call for a row whose columns hold different texts: the whole column is one call."""
    def call(text):
        if calls is not None:
            calls.append(len(text))
        for plain, ents in texts_and_entities:
            if plain == text:
                return as_entities(ents)
        raise AssertionError("extractor called with a text no test supplied")
    return call


def corpus():
    for s in SAMPLES:
        plain, gold = parse_markup(s["text"])
        yield s, plain, gold


# ── Prompt stand-ins: (keyword inputs) -> {"text", "finishReason"} ─────────────────────────────
def answer(text, finish="Stop"):
    return {"text": text, "finishReason": finish}


def good_rewrite(Narrative, NeutralTerms="", Titles="", NameRules="", Labels=""):  # noqa: N803 - input names
    """A good model that follows the rules it is GIVEN: the neutral terms and titles come from its inputs,
    so a test that edits a rule row sees the stand-in follow the edit (ADR-076 item 2)."""
    terms = rr.parse_neutral_terms(NeutralTerms) or []
    titles = rr.parse_titles(Titles) or []
    return answer(rr.neutral_rewrite(Narrative, 1, terms, titles))


def echo_spelling(Text):  # noqa: N803
    return answer(Text)


def spelling_from(fixes: dict):
    """A spelling model that replaces whole words by a map (and changes nothing else)."""
    def call(Text):  # noqa: N803
        return answer(" ".join(fixes.get(w, w) for w in Text.split(" ")))
    return call


def failing(**_):
    raise RuntimeError("the prompt call failed")


def rewrite_then(change):
    """A rewrite model that first does the good rewrite, then `change(text)` - the bad part."""
    def call(**inputs):
        return answer(change(good_rewrite(**inputs)["text"]))
    return call
