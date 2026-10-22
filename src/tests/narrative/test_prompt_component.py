#!/usr/bin/env python3
"""The AI prompt components (wbs:5.3) against the repo's own documents and the flow that calls them.

REV 22 (Iteration 9, 2026-10-16). The flow called two NEW prompts (rewrite, spelling; ADR-075 items 3-4), created in
DEV by the reviewer (TAD 12.6.1 R1, A-NS-31 closed by the export of 2026-10-16). The rev 20 detector component below
is still in the solution and no longer called. Its tests stand, as a check on the component the solution ships; the
run-action test checks the rewrite action against the one designer-saved run action this tenant has
(fixtures/run-a-prompt-action.json), for host, parameter shape and answer path.

REV 30 (Iteration 14, 2026-10-21, ADR-082), finished 2026-10-22. ONE prompt rewrites and corrects spelling, so the flow
calls the rewrite prompt only. The reviewer applied the rev 30 template in DEV (R1d), the component was re-exported
from DEV (2026-10-22) and copied into Other/Customizations.xml as exported, and REV Narrative Spelling Prompt was removed
from the solution source (Customizations.xml and its root component in Solution.xml). The export is therefore compared
with the prompt document's section 1, the rev 30 template.

Run:  python3 -m unittest discover -s src/tests/narrative -p 'test_*.py' -v
Also run by NarrativeRedaction.Tests.ps1 inside the HARD `unit-tests` build step.

The component in Other/Customizations.xml was copied from a DEV export (TAD 12.6.1 R1, 2026-10-06),
never hand-authored (A-NS-9). These tests do not prove it imports or runs. They prove three things a
later edit could break silently:

1. the prompt in the solution is the template docs/development/revitalise-redaction-prompt.md fixes,
   up to the whitespace the prompt builder puts around an input token;
2. the drift between that document and the export is exactly the drift recorded in the Dev Summary
   (Iteration 4) and no more, so a new difference fails here instead of shipping unreviewed;
3. the flow's run action names this component's id and passes exactly its declared inputs, and reads
   exactly its declared outputs.
"""
from __future__ import annotations

import base64
import gzip
import html
import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SOLUTION = REPO / "src" / "solutions" / "RevitaliseGrantAutomation"
CUSTOMIZATIONS = (SOLUTION / "Other" / "Customizations.xml").read_text(encoding="utf-8")
MANIFEST = (SOLUTION / "Other" / "Solution.xml").read_text(encoding="utf-8")
PROMPT_DOC = (REPO / "docs" / "development" / "revitalise-redaction-prompt.md").read_text(encoding="utf-8")
FLOW = json.loads((SOLUTION / "Workflows" / "REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json")
                  .read_text(encoding="utf-8"))["properties"]["definition"]

INPUTS = {"Categories", "AllowedLabels", "Narrative"}


def ai_models() -> list[str]:
    block = re.search(r"<AIModels>(.*?)</AIModels>", CUSTOMIZATIONS, re.S)
    return re.findall(r"<AIModel>(.*?)</AIModel>", block.group(1), re.S) if block else []


DETECTOR = "REV Narrative Redaction Prompt"      # rev 20, no longer called; kept until the reviewer decides
REWRITE = "REV Narrative Rewrite Prompt"         # rev 30 template (R1d), exported from DEV 2026-10-22
RETIRED_SPELLING_ID = "763cff31-d653-416b-a52f-7e6f400bce21"   # REV Narrative Spelling Prompt, removed from source (ADR-082)


def model(name: str = DETECTOR) -> str:
    (m,) = [x for x in ai_models() if f"<msdyn_name>{name}</msdyn_name>" in x]
    return m


def model_id(name: str = DETECTOR) -> str:
    return re.search(r"<AIModel>\s*<msdyn_aimodelid>\{([^}]+)\}", "<AIModel>" + model(name)).group(1)


def active_configuration(name: str = DETECTOR) -> dict:
    m = model(name)
    active = re.search(r"<msdyn_activerunconfigurationid>\{([^}]+)\}", m).group(1)
    for cfg in re.findall(r"<AIConfiguration>(.*?)</AIConfiguration>", m, re.S):
        if re.search(r"<msdyn_aiconfigurationid>\{" + re.escape(active) + r"\}", cfg):
            return {
                "custom": json.loads(html.unescape(re.search(r"<msdyn_customconfiguration>(.*?)</msdyn_customconfiguration>",
                                                             cfg, re.S).group(1))),
                "runspec": json.loads(gzip.decompress(base64.b64decode(
                    re.search(r"<msdyn_modelrundataspecification>(.*?)</msdyn_modelrundataspecification>",
                              cfg, re.S).group(1).strip()))),
            }
    raise AssertionError("the active run configuration is not in the component")


def exported_template(custom: dict) -> str:
    return "".join(p["text"] if p["type"] == "literal" else "{" + p["id"] + "}" for p in custom["prompt"])


def documented_template(heading: str = r"### A1\. The rev 20 detector template") -> str:
    return re.search(heading + r".*?```text\n(.*?)\n```", PROMPT_DOC, re.S).group(1)


REWRITE_REV30 = r"## 1\. The rewrite prompt"           # the template applied in DEV (R1d) and exported 2026-10-22


def run_actions() -> dict:
    """The column loop's If: every action the flow runs per column once its batch's extractor call has answered.
    Rev 30: the column loop sits inside the batch loop."""
    return (FLOW["actions"]["Scrub_free_text"]["actions"]["For_each_batch"]["actions"]["For_each_column"]["actions"]
            ["Label_rewrite_and_check_the_column"]["actions"])


NEW_PROMPTS = {  # run action -> (answer Compose, documented section, input names)
    "Run_the_rewrite_prompt": ("Compose_rewrite", REWRITE_REV30, {"Narrative", "NeutralTerms", "Titles", "NameRules", "Labels"}),
}


class TheComponent(unittest.TestCase):

    def test_two_ai_models_each_a_declared_root_component(self):
        self.assertEqual(len(ai_models()), 2)
        for name in (DETECTOR, REWRITE):
            self.assertIn(f'<RootComponent type="401" id="{{{model_id(name)}}}" behavior="0" />', MANIFEST, name)
        self.assertEqual(MANIFEST.count('<RootComponent type="401"'), 2)

    def test_it_is_the_redaction_prompt_on_the_prompt_template(self):
        m = model(DETECTOR)
        self.assertIn("<msdyn_name>REV Narrative Redaction Prompt</msdyn_name>", m)
        self.assertEqual(active_configuration()["custom"]["version"], "GptDynamicPrompt-2")

    def test_the_template_is_the_documented_one_up_to_token_whitespace(self):
        norm = lambda s: re.sub(r"\s+", " ", s).strip()  # noqa: E731
        self.assertEqual(norm(exported_template(active_configuration()["custom"])), norm(documented_template()))

    def test_the_exact_drift_from_the_document_is_the_recorded_drift(self):
        """Dev Summary Iteration 4 §4.4 drift row 1: the prompt builder pads each input token with a
        space on both sides (and the AllowedLabels line keeps the space typed before it). Any other
        difference is new drift and must be reviewed, not absorbed."""
        doc = documented_template()
        padded = (doc.replace("{Categories}", " {Categories} ").replace("{Narrative}", " {Narrative} ")
                  .replace("labels: {AllowedLabels}", "labels:  {AllowedLabels} "))
        self.assertEqual(exported_template(active_configuration()["custom"]), padded)

    def test_the_inputs_are_the_three_text_inputs_the_flow_passes(self):
        custom = active_configuration()["custom"]
        self.assertEqual({i["id"] for i in custom["definitions"]["inputs"]}, INPUTS)
        self.assertTrue(all(i["type"] == "text" for i in custom["definitions"]["inputs"]))
        tokens = {p["id"] for p in custom["prompt"] if p["type"] == "inputVariable"}
        self.assertEqual(tokens, INPUTS)

    def test_model_settings_as_exported(self):
        """GPT-4.1 mini, temperature 0 and content moderation Low, as R1 asked (moderation is in the
        export since the reviewer re-published the prompt on 2026-10-07). Output format is TEXT where
        R1 asked for JSON: the reviewer decided to keep text (D-1 = a, 2026-10-07); the template itself
        asks for JSON and the flow parses the text."""
        custom = active_configuration()["custom"]
        self.assertEqual(custom["modelParameters"], {"modelType": "gpt-41-mini", "gptParameters": {"temperature": 0}})
        self.assertEqual(custom["definitions"]["output"], {"formats": ["text"]})
        self.assertEqual(custom["settings"].get("contentModerationLevel"), "Low")

    def test_the_run_specification_declares_the_inputs_and_text_and_finish_reason(self):
        spec = active_configuration()["runspec"]
        required = {k for k, v in spec["InputRootEntity"]["Attributes"].items() if not v.get("Optional")}
        self.assertEqual(required, INPUTS)
        self.assertEqual(set(spec["OutputRootEntity"]["Attributes"]), {"text", "finishReason"})


class TheFlowsRunActions(unittest.TestCase):

    def test_the_rev20_detector_component_is_no_longer_called(self):
        self.assertNotIn(model_id(), json.dumps(FLOW))

    def test_each_new_run_action_has_the_designer_saved_shape(self):
        """A-NS-31, the part a source test can check: same host and operation as the action a maker saved in
        the DEV designer on 2026-10-07, parameters named item/requestv2/<input>, plus recordId."""
        truth = json.loads((Path(__file__).resolve().parent / "fixtures" / "run-a-prompt-action.json")
                           .read_text(encoding="utf-8"))
        for name, (_, _, inputs) in NEW_PROMPTS.items():
            act = run_actions()[name]
            self.assertEqual(act["type"], truth["type"])
            self.assertEqual(act["inputs"]["host"], truth["inputs"]["host"])
            self.assertEqual(set(act["inputs"]["parameters"]), {"recordId"} | {f"item/requestv2/{n}" for n in inputs})
            self.assertEqual(act["inputs"]["parameters"]["recordId"], model_id(REWRITE))

    def test_the_spelling_prompt_is_gone_from_the_solution_and_not_called(self):
        """ADR-082 item 4: the component and its root-component entry are removed from source (2026-10-22)."""
        self.assertNotIn(RETIRED_SPELLING_ID, CUSTOMIZATIONS)
        self.assertNotIn(RETIRED_SPELLING_ID, MANIFEST)
        self.assertNotIn("REV Narrative Spelling Prompt", CUSTOMIZATIONS)
        self.assertNotIn(RETIRED_SPELLING_ID, json.dumps(FLOW))
        self.assertNotIn("Run_the_spelling_prompt", json.dumps(FLOW))

    def test_each_template_declares_exactly_the_inputs_its_action_passes(self):
        for name, (_, heading, inputs) in NEW_PROMPTS.items():
            tokens = set(re.findall(r"\{([A-Za-z]+)\}", documented_template(heading)))
            self.assertEqual(tokens, inputs, name)

    def test_the_answer_is_read_at_the_designer_path_and_a_failure_is_handled(self):
        truth = json.loads((Path(__file__).resolve().parent / "fixtures" / "run-a-prompt-action.json")
                           .read_text(encoding="utf-8"))["outputs_read_by_the_designer"]
        designer = re.fullmatch(r"@outputs\('Run_a_prompt'\)\?\['body/([^']+)'\]", truth["text"]).group(1).split("/")
        for name, (compose, _, _) in NEW_PROMPTS.items():
            acts = run_actions()
            self.assertEqual(acts[name]["runtimeConfiguration"]["secureData"]["properties"], ["inputs", "outputs"])
            ans = acts[compose]
            self.assertEqual(ans["runAfter"], {name: ["Succeeded", "Failed", "TimedOut"]})
            path = re.search(rf"body\('{name}'\)((?:\?\['[^']+'\])+)\?\['text'\]", ans["inputs"]["text"]).group(1)
            self.assertIn(f"body('{name}')" + path + "?['finishReason']", ans["inputs"]["usable"])
            self.assertEqual(re.findall(r"\['([^']+)'\]", path) + ["text"], designer)

    def test_no_deploy_seeds_the_kill_switch(self):
        """ADR-074 item 7, ADR-075 item 8: no Redaction* row is seeded by a deploy, so RedactionPromptStage is the
        process owner's alone (absent: the prompts run; off: nothing is written)."""
        for folder in ("provisioning", "config"):
            for p in (REPO / folder).rglob("*"):
                if p.is_file() and p.suffix in {".json", ".yml", ".yaml", ".ps1", ".csv"}:
                    self.assertNotIn("RedactionPromptStage", p.read_text(encoding="utf-8", errors="ignore"), str(p))


class TheRewriteComponent(unittest.TestCase):
    """A-NS-31, closed by the DEV export of 2026-10-16 and refreshed from the DEV export of 2026-10-22 (after R1d):
    the component is copied from the export exactly, and checked here against the prompt document and the flow."""
    ACTION, INPUTS_ = "Run_the_rewrite_prompt", {"Narrative", "NeutralTerms", "Titles", "NameRules", "Labels"}

    def test_the_run_specification_declares_the_inputs_the_flow_passes_and_text_and_finish_reason(self):
        spec = active_configuration(REWRITE)["runspec"]
        required = {k for k, v in spec["InputRootEntity"]["Attributes"].items() if not v.get("Optional")}
        self.assertEqual(required, self.INPUTS_)
        self.assertEqual(set(spec["OutputRootEntity"]["Attributes"]), {"text", "finishReason"})
        passed = {k.split("/", 2)[2] for k in run_actions()[self.ACTION]["inputs"]["parameters"] if k.startswith("item/requestv2/")}
        self.assertEqual(passed, self.INPUTS_)

    def test_model_settings_as_the_prompt_document_asks(self):
        custom = active_configuration(REWRITE)["custom"]
        self.assertEqual(custom["modelParameters"], {"modelType": "gpt-41-mini", "gptParameters": {"temperature": 0}})
        self.assertEqual(custom["definitions"]["output"], {"formats": ["text"]})
        self.assertEqual(custom["settings"].get("contentModerationLevel"), "Low")
        self.assertEqual(custom["version"], "GptDynamicPrompt-2")

    def test_the_exported_template_is_the_documented_rev30_one_and_the_drift_is_exactly_the_known_drift(self):
        """The reviewer typed the template by hand (R1d). The wording is identical to section 1; the only differences are
        whitespace: the prompt builder's space each side of every input token, line breaks the maker editor does not keep
        where the document wraps, and one newline at the end. Any change of a word is new drift and must be reviewed."""
        doc = documented_template(REWRITE_REV30)
        norm = lambda t: re.sub(r"\s+", " ", t).strip()  # noqa: E731
        self.assertEqual(norm(exported_template(active_configuration(REWRITE)["custom"])), norm(doc))

    def test_the_rev30_template_has_the_spelling_changes_and_every_closing_clause(self):
        """ADR-082 item 5 and IMP-1202, in the template DEV holds. The label-protection clause was missing from the first
        R1d paste (IMP-1209); it is pinned here so a truncated paste fails instead of shipping."""
        new = exported_template(active_configuration(REWRITE)["custom"])
        norm = lambda t: re.sub(r"\s+", " ", t).strip()  # noqa: E731
        n = norm(new)
        self.assertNotIn("do not correct spelling", n)
        self.assertIn("###CORRECTIONS###", n)
        self.assertIn("apart from the spelling corrections you list", n)
        self.assertIn("including the full stop at the end of every sentence and after a label", n)
        self.assertIn("and do not change any label in square brackets except as the name rules say.", n)
        self.assertEqual(set(re.findall(r"\{([A-Za-z]+)\}", new)), self.INPUTS_)

    def test_the_rewrite_prompt_has_no_extra_terms_input_any_more(self):
        custom = active_configuration(REWRITE)["custom"]
        self.assertNotIn("ExtraTerms", {i["id"] for i in custom["definitions"]["inputs"]})


if __name__ == "__main__":
    unittest.main()
