#!/usr/bin/env python3
"""The AI prompt components (wbs:5.3) against the repo's own documents and the flow that calls them.

REV 22 (Iteration 9, 2026-10-16). The flow now calls two NEW prompts (rewrite, spelling; ADR-075 items 3-4) that do
not exist yet: their run actions carry placeholder ids until the reviewer creates them in DEV (TAD 12.6.1 R1,
A-NS-31). The rev 20 detector component below is still in the solution and no longer called. Its tests stand, as a
check on the component the solution ships; the run-action tests now check the TWO NEW actions against the one
designer-saved run action this tenant has (fixtures/run-a-prompt-action.json), for host, parameter shape and answer
path - the parts that are E1 for one prompt and E3 for the new ones.

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
REWRITE = "REV Narrative Rewrite Prompt"         # rev 23 template (R1b), exported 2026-10-16
SPELLING = "REV Narrative Spelling Prompt"       # rev 22 template, exported 2026-10-16


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


def run_actions() -> dict:
    """The column loop's If: every action the flow runs per column once the extractor has answered."""
    return (FLOW["actions"]["Scrub_free_text"]["actions"]["For_each_column"]["actions"]
            ["Label_rewrite_and_check_the_column"]["actions"])


NEW_PROMPTS = {  # run action -> (answer Compose, documented section, input names)
    "Run_the_rewrite_prompt": ("Compose_rewrite", r"## 1\. The rewrite prompt", {"Narrative", "NeutralTerms", "Titles", "NameRules", "Labels"}),
    "Run_the_spelling_prompt": ("Compose_spelling", r"## 2\. The spelling prompt", {"Text"}),
}


class TheComponent(unittest.TestCase):

    def test_three_ai_models_each_a_declared_root_component(self):
        self.assertEqual(len(ai_models()), 3)
        for name in (DETECTOR, REWRITE, SPELLING):
            self.assertIn(f'<RootComponent type="401" id="{{{model_id(name)}}}" behavior="0" />', MANIFEST, name)
        self.assertEqual(MANIFEST.count('<RootComponent type="401"'), 3)

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
            self.assertEqual(act["inputs"]["parameters"]["recordId"],
                             model_id(REWRITE if name == "Run_the_rewrite_prompt" else SPELLING))

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
            self.assertEqual(re.findall(r"\['([^']+)'\]", path) + ["text"], designer)

    def test_no_deploy_seeds_the_kill_switch(self):
        """ADR-074 item 7, ADR-075 item 8: no Redaction* row is seeded by a deploy, so RedactionPromptStage is the
        process owner's alone (absent: the prompts run; off: nothing is written)."""
        for folder in ("provisioning", "config"):
            for p in (REPO / folder).rglob("*"):
                if p.is_file() and p.suffix in {".json", ".yml", ".yaml", ".ps1", ".csv"}:
                    self.assertNotIn("RedactionPromptStage", p.read_text(encoding="utf-8", errors="ignore"), str(p))


class TheTwoNewComponents(unittest.TestCase):
    """A-NS-31, closed by the DEV export of 2026-10-16 (after R1b): both components copied from it exactly,
    and checked here against the prompt document and the flow that calls them."""
    PROMPTS = {REWRITE: ("Run_the_rewrite_prompt", r"## 1\. The rewrite prompt",
                         {"Narrative", "NeutralTerms", "Titles", "NameRules", "Labels"}),
               SPELLING: ("Run_the_spelling_prompt", r"## 2\. The spelling prompt", {"Text"})}

    def test_the_run_specification_declares_the_inputs_the_flow_passes_and_text_and_finish_reason(self):
        for name, (action, _, inputs) in self.PROMPTS.items():
            with self.subTest(name):
                spec = active_configuration(name)["runspec"]
                required = {k for k, v in spec["InputRootEntity"]["Attributes"].items() if not v.get("Optional")}
                self.assertEqual(required, inputs)
                self.assertEqual(set(spec["OutputRootEntity"]["Attributes"]), {"text", "finishReason"})
                passed = {k.split("/", 2)[2] for k in run_actions()[action]["inputs"]["parameters"] if k.startswith("item/requestv2/")}
                self.assertEqual(passed, inputs)

    def test_model_settings_as_the_prompt_document_asks(self):
        for name in self.PROMPTS:
            with self.subTest(name):
                custom = active_configuration(name)["custom"]
                self.assertEqual(custom["modelParameters"], {"modelType": "gpt-41-mini", "gptParameters": {"temperature": 0}})
                self.assertEqual(custom["definitions"]["output"], {"formats": ["text"]})
                self.assertEqual(custom["settings"].get("contentModerationLevel"), "Low")
                self.assertEqual(custom["version"], "GptDynamicPrompt-2")

    def test_the_exported_template_is_the_documented_one_and_the_drift_is_exactly_the_known_drift(self):
        """The reviewer typed both templates by hand (R1, R1b). The wording is identical to sections 1 and 2;
        the only differences are the prompt builder's: a space each side of every input token, and one
        newline at the end. Any other difference is new drift and must be reviewed, not absorbed."""
        for name, (_, heading, inputs) in self.PROMPTS.items():
            with self.subTest(name):
                doc = documented_template(heading)
                for t in inputs:
                    doc = doc.replace("{" + t + "}", " {" + t + "} ")
                self.assertEqual(exported_template(active_configuration(name)["custom"]), doc + "\n")

    def test_the_rewrite_prompt_has_no_extra_terms_input_any_more(self):
        custom = active_configuration(REWRITE)["custom"]
        self.assertNotIn("ExtraTerms", {i["id"] for i in custom["definitions"]["inputs"]})


if __name__ == "__main__":
    unittest.main()
