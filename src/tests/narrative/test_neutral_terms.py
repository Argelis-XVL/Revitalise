"""Rules v0.5 section 10.1: the client's Anonymisation Key as an oracle (wbs:5.6; Iteration 8, brought to SDD
Amendment A-09 in Iteration 9, 2026-10-16).

Reviewer decisions (Xander Lykopoulos): 2026-10-14 "1. follow the key file" and "2. ... auto correct that for
readability"; 2026-10-16 the A-09 answers (names become They, the client's examples win over the key, the added
words, OQ-054 to OQ-056 at their defaults), and the same day's correction of OQ-054 (c): "My husband Derek becoms
partner. not family member. the word husband is leading in this pattern."

In rev 22 the REWRITE PROMPT does this work and the flow checks it (test_scrub_flow_definition.py). These tests pin
neutral_rewrite(), which is the expected output wbs:5.7 scores the live model against. It works on labelled text,
so a name is the token [NAME].

Two kinds of test:
  * TRACKED cases, synthetic, always run (the corpus rule, rules 11.1: no real text in tracked files);
  * CLIENT cases read at run time from docs/Import/*.xlsx (committed by the reviewer in ffb42ef, 2026-10-14), which
    may hold real applicant text. They SKIP where the files are absent, and they never copy a narrative into this
    file: the pinned divergences hold only pronoun and verb tokens.
"""
from __future__ import annotations

import difflib
import re
import sys
import unittest
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
REPO = HERE.parents[2]

import redaction_reference as rr  # noqa: E402

KEY_XLSX = REPO / "docs" / "Import" / "Anonymisation Key.xlsx"
EXAMPLES_XLSX = REPO / "docs" / "Import" / "Anonymised Examples.xlsx"
_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def read_sheet(path: Path) -> dict[str, str]:
    """Cell reference -> text, for the first sheet. Standard library only (openpyxl is not installed)."""
    z = zipfile.ZipFile(path)
    shared = [''.join(t.text or '' for t in si.iter(_NS + 't'))
              for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall(_NS + 'si')]
    cells = {}
    for c in ET.fromstring(z.read('xl/worksheets/sheet1.xml')).iter(_NS + 'c'):
        v = c.find(_NS + 'v')
        if v is not None:
            cells[c.get('r')] = shared[int(v.text)] if c.get('t') == 's' else v.text
    return cells


def neut(text: str) -> str:
    return rr.neutral_rewrite(text)


def scrub(text: str, names: list[str]) -> str:
    """Each listed name labelled where it occurs, as the extractor would, then the good rewrite."""
    ents, at = [], 0
    for n in names:
        at = text.index(n, at)
        ents.append(rr.ExtractorEntity("PersonName", n, at, len(n), 0.95))
        at += len(n)
    return rr.expected_scrub(text, ents)


class KeyMapping(unittest.TestCase):
    def test_every_key_row_is_in_the_map_as_written_or_as_a_named_deviation(self):
        for src, dst in rr.KEY_ROWS:
            word = re.sub(r"[^a-z'’ ]", "", src.lower().split("/")[0]).strip()
            word = "boyfriend" if word == "boyfrind" else word
            want = dst.lower().strip()
            if word in rr.KEY_DEVIATIONS:
                continue
            self.assertIn(word, rr.NEUTRAL_TERMS, src)
            self.assertEqual(rr.NEUTRAL_TERMS[word], want, src)

    def test_the_deviations_are_exactly_six_and_each_has_a_reason(self):
        self.assertEqual(sorted(rr.KEY_DEVIATIONS), ["boyfriend", "her", "hers", "herself", "him", "himself"])
        self.assertTrue(all(len(reason) > 20 for _, reason in rr.KEY_DEVIATIONS.values()))

    @unittest.skipUnless(KEY_XLSX.exists(), "docs/Import/Anonymisation Key.xlsx is untracked and absent here")
    def test_key_rows_match_the_client_file(self):
        cells = read_sheet(KEY_XLSX)
        rows = [(cells[f"A{r}"], cells[f"B{r}"]) for r in range(2, 28)]
        self.assertEqual(rows, rr.KEY_ROWS)

    @unittest.skipUnless(KEY_XLSX.exists(), "docs/Import/Anonymisation Key.xlsx is untracked and absent here")
    def test_free_text_questions_match_the_client_file(self):
        cells = read_sheet(KEY_XLSX)
        self.assertEqual(cells["A29"], "Free text questions")
        self.assertEqual([cells[f"A{r}"] for r in range(30, 45)], [q for q, _ in rr.FREE_TEXT_QUESTIONS])


class FreeTextQuestionScope(unittest.TestCase):
    def test_twelve_questions_map_to_the_twelve_scrubbed_columns_and_three_have_no_counterpart(self):
        raw_scrubbed = {raw for raw, _ in rr.SCRUB_COLUMNS}
        mapped = [c for _, c in rr.FREE_TEXT_QUESTIONS if c in raw_scrubbed]
        self.assertEqual(sorted(mapped), sorted(raw_scrubbed))   # every scrubbed column is asked, once
        unmapped = [c for _, c in rr.FREE_TEXT_QUESTIONS if c not in raw_scrubbed]
        self.assertEqual(unmapped, ["rev_benefitprovider", "rev_otherfundingsource", "rev_awaitingdecisionfrom"])

    def test_the_uncovered_columns_exist_and_have_no_redacted_counterpart_in_entity_xml(self):
        xml = (REPO / "src/solutions/RevitaliseGrantAutomation/Entities/rev_application/Entity.xml").read_text(
            encoding="utf-8")
        for col in ("rev_benefitprovider", "rev_otherfundingsource", "rev_awaitingdecisionfrom"):
            self.assertIn(f'Name="{col}"', xml)
            self.assertNotIn(f'Name="{col}redacted"', xml)


class WordBoundaries(unittest.TestCase):
    def test_a_term_inside_another_word_is_never_replaced(self):
        # column D of the key: "She[space]", "[space]she[space", "[space]she."
        for s in ["the shelter", "there and then", "another mother-figure? no: other", "help here",
                  "manage the hemp herb", "a person this season", "a chemist", "Shed", "sonar", "boycott",
                  "mandatory", "Hermann's"]:
            out = neut(s)
            for w in ["shelter", "there", "other", "here", "manage", "herb", "person", "season", "chemist",
                      "Shed", "sonar", "boycott", "mandatory"]:
                if w in s:
                    self.assertIn(w, out, s)

    def test_hyphen_and_punctuation_are_boundaries(self):
        self.assertEqual(neut("my mother-in-law"), "my parent-in-law")
        self.assertEqual(neut("my ex-husband."), "my ex-partner.")
        self.assertEqual(neut("(my son)"), "(my child)")

    def test_case_is_kept(self):
        self.assertEqual(neut("She helps. she helps. SHE HELPS"), "They help. they help. THEY HELP")

    def test_plurals_of_the_key_nouns(self):
        self.assertEqual(neut("my sons and two daughters; the men and women"),
                         "my children and two children; the people and people")


class Pronouns(unittest.TestCase):
    def test_her_as_object_is_them_and_as_possessive_is_their(self):
        cases = {
            "I help her with mobility": "I help them with mobility",
            "someone with her to help": "someone with them to help",
            "supporting her when she gets tired": "supporting them when they get tired",
            "to manage her mood changes": "to manage their mood changes",
            "who knows her needs": "who knows their needs",
            "help her navigate new places": "help them navigate new places",
            "I love her.": "I love them.",
            "her husband drives": "their partner drives",
            "Her pain is constant": "Their pain is constant",
        }
        for src, want in cases.items():
            self.assertEqual(neut(src), want, src)

    def test_him_his_hers_and_reflexives(self):
        self.assertEqual(neut("I wash him and his clothes"), "I wash them and their clothes")
        self.assertEqual(neut("the choice is hers"), "the choice is theirs")
        self.assertEqual(neut("he hurt himself; she blames herself"), "they hurt themself; they blame themself")
        self.assertEqual(neut("the car is his. his car"), "the car is theirs. their car")   # OQ-056

    def test_contractions(self):
        self.assertEqual(neut("He's tired and she's got no help"), "They're tired and they've got no help")
        self.assertEqual(neut("She’s worn out. He'll come. she'd like"), "They’re worn out. They'll come. they'd like")


class Agreement(unittest.TestCase):
    """Decision 2: the substitution must not leave 'they is'."""

    def test_the_verb_after_a_replaced_subject_agrees(self):
        cases = {
            "she is up at night": "they are up at night",
            "He was a nurse": "They were a nurse",
            "he has dementia": "they have dementia",
            "she does all my care": "they do all my care",
            "she doesn't sleep": "they don't sleep",
            "she doesn’t overexert": "they don’t overexert",
            "he isn't able": "they aren't able",
            "she relies on me": "they rely on me",
            "she watches over me": "they watch over me",
            "he goes out": "they go out",
            "he needs help": "they need help",
            "she also helps assist": "they also help assist",
            "he really really needs": "they really really need",
        }
        for src, want in cases.items():
            self.assertEqual(neut(src), want, src)

    def test_a_verb_that_already_agrees_or_a_modal_is_left_alone(self):
        for s in ["she can help", "he will drive", "she helped", "she spend hours", "he must rest"]:
            self.assertEqual(neut(s), s.replace("she", "they").replace("he ", "they "), s)

    def test_only_a_replaced_subject_triggers_agreement(self):
        # "his needs" is a noun; "my son needs" keeps "needs" (the subject is still singular: "my child needs")
        self.assertEqual(neut("his needs are met"), "their needs are met")
        self.assertEqual(neut("my son needs help"), "my child needs help")

    def test_a_second_verb_after_and_agrees(self):
        # FR-098 (A-09): "They receive PIP and require care". The oracle's rule is a heuristic, and the live
        # model does this work; the limits are pinned below so a change is deliberate.
        self.assertEqual(neut("He receives PIP and requires care"), "They receive PIP and require care")
        self.assertEqual(neut("she cooks and cleans the house"), "they cook and clean the house")
        # not a verb at the end of a clause, and not past a full stop or a new subject
        self.assertEqual(neut("she has a cat and dogs."), "they have a cat and dogs.")
        self.assertEqual(neut("she needs help. Ann and Bob helps"), "they need help. Ann and Bob helps")


class ParentAsName(unittest.TestCase):
    def test_a_capitalised_bare_mum_or_dad_becomes_my_parent(self):
        self.assertEqual(neut("Mum helps me. Then Dad cooks."), "My parent helps me. Then my parent cooks.")
        self.assertEqual(neut("I told Mum"), "I told my parent")

    def test_after_a_determiner_it_is_just_parent(self):
        self.assertEqual(neut("My Mum helps"), "My parent helps")
        self.assertEqual(neut("my mum helps"), "my parent helps")


class Names(unittest.TestCase):
    """FR-095 and OQ-054 as approved on 2026-10-16, with (c) corrected the same day by the reviewer."""

    def test_the_one_person_named_becomes_they_them_or_their(self):
        self.assertEqual(scrub("Sam relies on me", ["Sam"]), "They rely on me")              # US-025 AC-3
        self.assertEqual(scrub("I help Sam every day", ["Sam"]), "I help them every day")
        self.assertEqual(scrub("I wash Sam's clothes", ["Sam"]), "I wash their clothes")
        self.assertEqual(scrub("Sam has dementia. Sam is tired.", ["Sam", "Sam"]), "They have dementia. They are tired.")

    def test_two_different_people_keep_their_labels(self):
        # OQ-054 (a), US-025 AC-4: neither name is shown, and the two are not merged into one "they"
        self.assertEqual(scrub("Sam and Ann help me", ["Sam", "Ann"]), "[NAME] and [NAME] help me")

    def test_a_name_after_dr_keeps_its_label(self):
        self.assertEqual(scrub("Dr Okafor saw me", ["Okafor"]), "Dr [NAME] saw me")          # OQ-054 (b)

    def test_the_relationship_word_leads_and_the_name_goes(self):
        # Reviewer, 2026-10-16: "My husband Derek becoms partner. not family member."
        self.assertEqual(scrub("My husband Derek Hale helps me and he drives.", ["Derek Hale"]),
                         "My partner helps me and they drive.")
        self.assertEqual(scrub("my wife Jo's car", ["Jo"]), "my partner's car")
        self.assertEqual(scrub("my late mum Joan", ["Joan"]), "my late parent")

    def test_no_rule_produces_family_member_but_the_label_is_kept(self):
        # Decision 2026-10-16: "Keep the family member label for now." P2 accepts it (closed list).
        for text, names in (("My husband Derek helps", ["Derek"]), ("my son Tom and my daughter Amy", ["Tom", "Amy"])):
            self.assertNotIn("[FAMILY MEMBER]", scrub(text, names))
        self.assertIn("[FAMILY MEMBER]", rr.LABEL_BY_CODE.values())
        self.assertEqual(rr.validate_rewrite("my son [NAME]", "my child [FAMILY MEMBER]"), [])

    def test_a_title_goes_and_the_name_after_it_is_handled_as_a_name(self):
        # FR-096, US-025 AC-5: "my grandmother and Mrs Patel" shows no gendered word and no title
        out = scrub("my grandmother and Mrs Patel", ["Patel"])
        self.assertEqual(out, "my grandparent and them")
        self.assertEqual(rr.gendered_residue(out), [])
        self.assertEqual(neut("Ms. Jones came"), "Jones came")

    def test_the_writers_own_name_keeps_its_label(self):
        # Iteration 11 (DEV 2026-10-19: "I am they"): RedactionNameRules line 1
        self.assertEqual(scrub("I am Fenella Aldous and I live alone", ["Fenella Aldous"]),
                         "I am [NAME] and I live alone")
        self.assertEqual(scrub("I'm Sam and Sam is tired", ["Sam", "Sam"]), "I'm [NAME] and they are tired")
        self.assertEqual(scrub("My name is Sam. I need help", ["Sam"]), "My name is [NAME]. I need help")

    def test_a_sentence_saying_what_the_writer_is_called_keeps_the_label(self):
        # DEV 2026-10-20, TD-15: "Fenella is the name my friends use for me" came back as "they is the name ..."
        self.assertEqual(scrub("My left side is weak and stairs are very hard. Fenella is the name my friends use for me.",
                               ["Fenella"]),
                         "My left side is weak and stairs are very hard. [NAME] is the name my friends use for me.")
        self.assertEqual(scrub("Fen is what my family call me", ["Fen"]), "[NAME] is what my family call me")
        self.assertEqual(scrub("Everyone calls me Fen", ["Fen"]), "Everyone calls me [NAME]")
        # someone else's name is still a third person
        self.assertNotIn("[NAME]", scrub("Pat is the name of my carer", ["Pat"]))
        self.assertNotIn("[NAME]", scrub("Pat helps me", ["Pat"]))

    def test_the_writers_own_name_does_not_count_as_another_person(self):
        # SDD A-11, OQ-054 (e), reviewer 2026-10-19, verbatim example
        self.assertEqual(scrub("I am Sam and Pat helps me", ["Sam", "Pat"]), "I am [NAME] and they help me")
        # two people besides the writer still keep their labels
        self.assertEqual(scrub("I am Sam and Pat and Jo help me", ["Sam", "Pat", "Jo"]),
                         "I am [NAME] and [NAME] and [NAME] help me")

    def test_the_relationship_word_leads_even_when_others_are_named(self):
        # Iteration 11 (DEV 2026-10-19: "Our child [NAME]" kept the name): line 3 applies before line 4
        self.assertEqual(scrub("My husband Cormac helps me. Our daughter Imogen, who is 40, shops.", ["Cormac", "Imogen"]),
                         "My partner helps me. Our child, who is 40, shops.")
        self.assertEqual(scrub("Sam and my son Tom help me", ["Sam", "Tom"]), "[NAME] and my child help me")

    def test_a_hyphenated_or_apostrophe_name_is_labelled_whole(self):
        # Iteration 11 (IMP-1139, DEV 2026-10-19: "they-Reed"): the extractor found only part of the name
        text = "My name is Beatrix Holloway-Reed and I need a break."
        ents = [rr.ExtractorEntity("PersonName", "Beatrix Holloway", 11, 16, 0.9)]
        _, kept, _, _ = rr.label_spans(text, ents)
        self.assertEqual(rr.labelled_text(text, kept), "My name is [NAME] and I need a break.")
        self.assertEqual(rr.expected_scrub(text, ents), "My name is [NAME] and I need a break.")
        ents = [rr.ExtractorEntity("PersonName", "Brien", 6, 5, 0.9)]
        _, kept, _, _ = rr.label_spans("Ask O'Brien now", ents)
        self.assertEqual(rr.labelled_text("Ask O'Brien now", kept), "Ask [NAME] now")
        ents = [rr.ExtractorEntity("PersonName", "Sam", 7, 3, 0.9)]
        _, kept, _, _ = rr.label_spans("I wash Sam's clothes", ents)
        self.assertEqual(rr.labelled_text("I wash Sam's clothes", kept), "I wash [NAME]'s clothes")   # possessive kept

    def test_a_name_span_that_starts_with_dr_keeps_the_title_outside(self):
        # Iteration 11 (DEV 2026-10-19: "Dr [NAME]" became "they", Dr lost)
        for title in ("Dr", "Dr.", "Doctor", "DR"):
            text = f"{title} Adeyemi reviews my tablets."
            ents = [rr.ExtractorEntity("PersonName", f"{title} Adeyemi", 0, len(title) + 8, 0.9)]
            with self.subTest(title):
                self.assertEqual(rr.expected_scrub(text, ents), f"{title} [NAME] reviews my tablets.")

    def test_a_key_word_inside_a_found_name_is_never_seen(self):
        # The extractor's span covers "Mum Smith": the rewrite receives [NAME], so "Mum" is not rewritten.
        self.assertEqual(scrub("Ask for Mum Smith at noon", ["Mum Smith"]), "Ask for them at noon")


class AddedWords(unittest.TestCase):
    """FR-096 / OQ-055 at its default: the reviewer's words, their counterparts, plurals."""

    def test_each_added_word_and_its_counterpart(self):
        for w in rr.ADDED_WORDS:
            self.assertIn(w, rr.NEUTRAL_TERMS, w)
        cases = {"my grandmother": "my grandparent", "my grandfather": "my grandparent", "my stepson": "my stepchild",
                 "my stepdaughter": "my stepchild", "my auntie": "my relative", "my uncle": "my relative",
                 "my niece and nephew": "my relative and relative", "Mummy helps": "My parent helps",
                 "a lady": "a person", "a gentleman": "a person", "my stepmother": "my stepparent",
                 "my grandsons": "my grandchildren"}
        for src, want in cases.items():
            self.assertEqual(neut(src), want, src)

    def test_every_neutral_word_is_on_the_closed_list(self):
        targets = {w for v in rr.NEUTRAL_TERMS.values() for w in rr.p2_words(v)}
        closed = set(rr.SEED_CONTEXT().closed)
        self.assertTrue(targets <= closed, sorted(targets - closed))

    def test_every_replaced_word_is_on_the_gendered_residue_list(self):
        gendered = set(rr.SEED_CONTEXT().gendered_words)
        self.assertTrue(set(rr.NEUTRAL_TERMS) <= gendered, sorted(set(rr.NEUTRAL_TERMS) - gendered))
        self.assertEqual(rr.SEED_CONTEXT().titles, ("Mr", "Mrs", "Ms", "Miss"))   # the title check, as written

    def test_the_seed_row_says_exactly_what_the_oracle_map_says(self):
        """ADR-076 seed values: RedactionNeutralTerms is the oracle's NEUTRAL_TERMS, plus 'her', whose two
        readings the sentence decides. Every other word's first neutral word is the oracle's word."""
        seed = dict(rr.parse_neutral_terms(rr.SEED_ROWS["RedactionNeutralTerms"]))
        self.assertEqual(set(seed), set(rr.NEUTRAL_TERMS) | {"her"})
        self.assertEqual(seed["her"], ["their", "them"])
        for w, alts in seed.items():
            if w != "her":
                self.assertEqual(alts[0], rr.NEUTRAL_TERMS[w], w)


class UserStory25(unittest.TestCase):
    """US-025's acceptance criteria, as the SDD writes them, against the good rewrite."""

    def test_the_acceptance_criteria_examples(self):
        self.assertEqual(neut("My mum helps me and she is up at night"), "My parent helps me and they are up at night")
        self.assertEqual(neut("I help her with her mood"), "I help them with their mood")
        self.assertEqual(scrub("Sam relies on me", ["Sam"]), "They rely on me")
        self.assertEqual(neut("my wife and son"), "my partner and child")
        self.assertEqual(neut("He receives PIP and requires care"), "They receive PIP and require care")

    def test_no_key_term_survives_the_tracked_synthetic_examples(self):
        # One synthetic stand-in per client example: same phenomena, invented text (rules 11.1).
        samples = {
            "I care for my husband. He has a stroke and I help him with his meals; he is unable to cook.":
                "I care for my partner. They have a stroke and I help them with their meals; they are unable to cook.",
            "Mum helps me at night. She changes my bed and she soothes me when I wake.":
                "My parent helps me at night. They change my bed and they soothe me when I wake.",
            "Help from my wife. She needs someone with her to manage her anxiety and doesn't rest.":
                "Help from my partner. They need someone with them to manage their anxiety and don't rest.",
            "My son helps me with letters, he accompanies me to appointments.":
                "My child helps me with letters, they accompany me to appointments.",
        }
        for src, want in samples.items():
            out = neut(src)
            self.assertEqual(out, want, src)
            self.assertEqual(rr.gendered_residue(out), [], src)


def _tokens(s: str) -> list[str]:
    return re.findall(r"\[[A-Z ]+\]|[A-Za-z]+(?:['’][A-Za-z]+)?", s)


def _client_examples():
    cells = read_sheet(EXAMPLES_XLSX)
    return [(cells[f"A{r}"], cells[f"B{r}"]) for r in range(3, 7)]


def _names_the_client_replaced(original: str, client: str) -> list[tuple[int, int]]:
    """Offsets of words the client turned into 'They' that are not key terms: first names. Read from the
    pair itself so no name is written into this file; stands in for the extractor's PersonName."""
    o, c = _tokens(original), _tokens(client)
    spans, pos = [], {}
    for m in re.finditer(r"[A-Za-z]+(?:['’][A-Za-z]+)?", original):
        pos.setdefault(m.group(0), []).append(m.start())
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(a=o, b=c, autojunk=False).get_opcodes():
        if tag == "replace":
            for k, w in enumerate(o[i1:i2]):
                if (w[:1].isupper() and w.lower() not in rr.NEUTRAL_TERMS and w not in ("I",)
                        and j1 + k < j2 and c[j1 + k] == "They"):
                    for p in pos[w]:
                        spans.append((p, len(w)))
    return sorted(set(spans))


# What separates the oracle from the client's own anonymised text, per example: (client token, oracle token).
# Since A-09 (2026-10-16) names become They and the -self forms "themself", as the client writes them, so no
# NAME or REFLEXIVE pair is left. Every remaining pair is one of: AGREE (the client did not fix the verb: A-09
# Finding 1, "the examples' grammar slips are not followed"), CASE (the client capitalised mid-sentence), HER
# (the client wrote "them" for a possessive "her": "them mood"), and EDIT (the client added a full stop in
# example 2, invisible to a token comparison: FR-099 says the spelling step adds no punctuation).
CLIENT_DIVERGENCES = {
    0: [("needs", "need"), ("is", "are"), ("receives", "receive")],                       # AGREE x3
    1: [("They", "they"), ("is", "are"), ("They", "they"), ("soothes", "soothe"), ("helps", "help"),
        ("does", "do"), ("They", "they")],                                                # CASE x3, AGREE x4; EDIT
    2: [("needs", "need"), ("them", "their"), ("them", "their"), ("They", "they"), ("gets", "get"),
        ("They", "they"), ("doesn’t", "don’t"), ("relies", "rely"), ("They", "they"), ("feels", "feel"),
        ("them", "their"), ("They", "they"), ("needs", "need"), ("them", "their"), ("needs", "need")],
                                                                                          # HER x4, CASE x4, AGREE x7
    3: [("accompanies", "accompany")],                                                    # AGREE x1
}


@unittest.skipUnless(EXAMPLES_XLSX.exists(), "docs/Import/Anonymised Examples.xlsx is untracked and absent here")
class ClientExamples(unittest.TestCase):
    def _run(self, i):
        original, client = _client_examples()[i]
        names = _names_the_client_replaced(original, client)
        ours = rr.expected_scrub(original, [rr.ExtractorEntity("PersonName", original[s:s + n], s, n, 0.95)
                                            for s, n in names])
        return original, client, ours

    def test_no_key_term_survives_any_client_example(self):
        for i in range(4):
            _, _, ours = self._run(i)
            self.assertEqual(rr.gendered_residue(ours), [], f"example {i + 1}")

    def test_every_difference_from_the_client_text_is_a_named_one(self):
        for i in range(4):
            _, client, ours = self._run(i)
            a, b = _tokens(client), _tokens(ours)
            with self.subTest(example=i + 1):
                self.assertEqual(len(a), len(b))     # word for word: nothing added or dropped
                pairs = [(x, y) for x, y in zip(a, b) if x != y]
                self.assertEqual(pairs, CLIENT_DIVERGENCES[i])


if __name__ == "__main__":
    unittest.main()
