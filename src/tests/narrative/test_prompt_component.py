#!/usr/bin/env python3
"""The REV Narrative Redaction Prompt component (ADR-072, wbs:5.3) against the repo's own documents and
the flow that calls it.

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


def model_id() -> str:
    (m,) = ai_models()
    return re.search(r"<AIModel>\s*<msdyn_aimodelid>\{([^}]+)\}", "<AIModel>" + m).group(1)


def active_configuration() -> dict:
    (m,) = ai_models()
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


def documented_template() -> str:
    return re.search(r"## 1\. The template.*?```text\n(.*?)\n```", PROMPT_DOC, re.S).group(1)


def run_action() -> dict:
    use = (FLOW["actions"]["Scrub_free_text"]["actions"]["For_each_column"]["actions"]
           ["Scrub_the_column_if_it_has_text"]["actions"]["Keep_or_scrub_the_column"]["else"]["actions"]
           ["Scan_the_column_in_windows"]["actions"]["Use_the_prompt_on_the_window"]["actions"])
    return use


class TheComponent(unittest.TestCase):

    def test_exactly_one_ai_model_and_it_is_a_declared_root_component(self):
        self.assertEqual(len(ai_models()), 1)
        self.assertIn(f'<RootComponent type="401" id="{{{model_id()}}}" behavior="0" />', MANIFEST)

    def test_it_is_the_redaction_prompt_on_the_prompt_template(self):
        (m,) = ai_models()
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


class TheFlowCallsThisComponent(unittest.TestCase):

    def test_the_run_action_names_the_component_by_its_exported_id(self):
        act = run_action()["Run_the_redaction_prompt"]
        self.assertEqual(act["inputs"]["parameters"]["recordId"], model_id())
        self.assertEqual(act["inputs"]["host"]["connectionName"], "shared_commondataserviceforapps")

    def test_the_run_action_passes_exactly_the_declared_inputs(self):
        params = run_action()["Run_the_redaction_prompt"]["inputs"]["parameters"]
        passed = {k.split("/", 2)[2] for k in params if k.startswith("item/requestv2/")}
        self.assertEqual(passed, INPUTS)
        self.assertEqual(set(params) - {f"item/requestv2/{n}" for n in INPUTS}, {"recordId"})
        for n in INPUTS:
            self.assertEqual(params[f"item/requestv2/{n}"], f"@outputs('Compose_prompt_request')?['{n}']")

    def test_the_answer_is_read_from_the_declared_outputs(self):
        spec_outputs = set(active_configuration()["runspec"]["OutputRootEntity"]["Attributes"])
        ans = run_action()["Compose_prompt_answer"]["inputs"]
        self.assertEqual(set(ans), spec_outputs)
        for k in spec_outputs:
            self.assertEqual(ans[k], f"@body('Run_the_redaction_prompt')?['responsev2']?['predictionOutput']?['{k}']")

    def test_the_run_action_matches_the_designer_saved_action(self):
        """A-NS-25 input half, E1: the action a maker saved in the DEV designer on 2026-10-07
        (fixtures/run-a-prompt-action.json). Same host, same parameter names, same prompt id."""
        truth = json.loads((Path(__file__).resolve().parent / "fixtures" / "run-a-prompt-action.json")
                           .read_text(encoding="utf-8"))
        act = run_action()["Run_the_redaction_prompt"]
        self.assertEqual(act["type"], truth["type"])
        self.assertEqual(act["inputs"]["host"], truth["inputs"]["host"])
        self.assertEqual(set(act["inputs"]["parameters"]), set(truth["inputs"]["parameters"]))
        self.assertEqual(act["inputs"]["parameters"]["recordId"], truth["inputs"]["parameters"]["recordId"])

    def test_the_answer_path_is_the_one_the_designer_writes(self):
        """A-NS-25, E1 (2026-10-07): the designer's own expressions for the action's outputs put text and
        finishReason at body -> responsev2 -> predictionOutput. The flow uses body() with ?[] steps; the
        designer uses outputs() with one slash path. Same location, compared key by key."""
        truth = json.loads((Path(__file__).resolve().parent / "fixtures" / "run-a-prompt-action.json")
                           .read_text(encoding="utf-8"))["outputs_read_by_the_designer"]
        ans = run_action()["Compose_prompt_answer"]["inputs"]
        for k in ("text", "finishReason"):
            designer = re.fullmatch(r"@outputs\('Run_a_prompt'\)\?\['body/([^']+)'\]", truth[k]).group(1).split("/")
            ours = re.fullmatch(r"@body\('Run_the_redaction_prompt'\)((?:\?\['[^']+'\])+)", ans[k]).group(1)
            self.assertEqual(re.findall(r"\['([^']+)'\]", ours), designer, k)

    def test_the_call_is_secured_both_ways_and_its_failure_is_handled(self):
        use = run_action()
        self.assertEqual(use["Run_the_redaction_prompt"]["runtimeConfiguration"]["secureData"]["properties"],
                         ["inputs", "outputs"])
        self.assertEqual(use["Record_a_prompt_call_failure"]["runAfter"], {"Run_the_redaction_prompt": ["Failed", "TimedOut"]})
        self.assertEqual(use["Record_a_prompt_call_failure"]["inputs"], {"name": "promptState", "value": "error"})
        self.assertEqual(use["Join_the_prompt_call_paths"]["runAfter"],
                         {"Record_a_prompt_call_failure": ["Succeeded", "Skipped"],
                          "Check_the_prompt_answer": ["Succeeded", "Skipped"]})

    def test_no_setting_row_switches_the_stage_on_in_any_shipped_file(self):
        """ADR-074 item 7: the stage ships off. No Redaction* row is seeded anywhere a deploy reads."""
        for folder in ("provisioning", "config"):
            for p in (REPO / folder).rglob("*"):
                if p.is_file() and p.suffix in {".json", ".yml", ".yaml", ".ps1", ".csv"}:
                    self.assertNotIn("RedactionPromptStage", p.read_text(encoding="utf-8", errors="ignore"), str(p))


if __name__ == "__main__":
    unittest.main()
