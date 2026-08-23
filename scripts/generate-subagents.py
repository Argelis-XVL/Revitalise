#!/usr/bin/env python3
"""Generate `.claude/agents/*.md` — the MECHANICAL enforcement of `config/models.yml`.

WHY THIS EXISTS. Every agent file in `agents/` has always said "resolve the model ID from
`config/models.yml`, do not hardcode it" — but resolving and applying a model was a step a
human or the calling agent had to remember to do, inside one continuously-growing chat
session. It was not enforced anywhere, and on this project it was not happening: the operator
ran the whole Lead → Plan → Architect → Development → Build → Test → Pipeline → Improvement
flow in one conversation on one model (Opus) for two days running, expecting the tier
declarations in `agents/*.md` to switch it automatically. They cannot — a model cannot
redispatch itself to a cheaper model mid-conversation from a markdown instruction.

Claude Code's own subagent feature (`.claude/agents/<name>.md`, invoked via the Task tool)
*can*: each subagent definition pins a model in its frontmatter, so invoking one is what
actually changes which model runs the work — mechanically, not by request. This script
generates that layer FROM `config/models.yml`, so the tier assignment stays declared in
exactly one place. Edit `config/models.yml`, re-run this script, and every subagent's pinned
model updates with it.

WHAT IT GENERATES. One `.claude/agents/<name>.md` per entry in `config/models.yml`'s `agents:`
and `sub_agents:` blocks. Each is a short pointer file: frontmatter carries the pinned model
resolved from the entry's `tier`; the body tells the subagent to read its real instructions
from `agents/<name>.md` (roster agents) or from `agents/development-agent.md`'s Sub-Agents
table plus its named skill (spawned sub-agents) — never duplicated here, so the content stays
single-sourced the same way the digest in `logs/known-failure-modes.md` does.

ESCALATION. A pinned model cannot escalate itself mid-invocation. The `escalate_to_strategic_
when` / `de_escalate_to_mechanical_when` conditions in `config/models.yml` stay the
*dispatcher's* job: before invoking a subagent, the caller checks those conditions and, if one
is met, passes an explicit model override on the Task invocation instead of relying on the
generated file's default. Each generated file lists its own conditions so that check does not
require re-reading `config/models.yml` at dispatch time.

Usage
-----
    python3 scripts/generate-subagents.py            # writes .claude/agents/*.md
    python3 scripts/generate-subagents.py --check     # exit 1 if any file is stale or missing
    python3 scripts/generate-subagents.py --stdout    # print all, do not write

`--check` is what CI and improvement-agent use: a `config/models.yml` tier change committed
without regenerating is caught rather than silently ignored — the same discipline
`generate-known-failure-modes.py --check` already applies to the log digest.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - the CI job installs it explicitly
    print("generate-subagents: FAILED — pyyaml is not installed "
          "(`python3 -m pip install pyyaml`).", file=sys.stderr)
    raise SystemExit(1)

MODELS_YML = Path("config/models.yml")
AGENTS_DIR = Path("agents")
OUT_DIR = Path(".claude/agents")

# Claude Code subagent frontmatter accepts these model aliases; it always resolves an alias
# to the CURRENT model of that name, so this table never needs a model ID and never goes
# stale the way a hardcoded model ID would. The tier NAME is not the alias by coincidence —
# `config/models.yml` chose tier names to match, and this is the one place that fact is load
# -bearing rather than cosmetic.
TIER_TO_MODEL_ALIAS = {
    "mechanical": "haiku",
    "standard": "sonnet",
    "strategic": "opus",
}

# One-line descriptions, kept here rather than parsed out of each agent file's "## Role"
# section because a markdown heading is not a stable machine interface. improvement-agent
# updates this dict in the same change that edits an agent's Role section — the --check run
# below fails loudly if an agent exists in config/models.yml with no entry here, which is the
# backstop for that promise being kept.
ROSTER_DESCRIPTIONS = {
    "lead-agent": "Routes a request to the correct delivery or PM agent using the WBS-first "
                  "routing table; answers general project questions directly. Entry point for "
                  "this system.",
    "plan-agent": "Translates a user request into an approved Solution Design Document (SDD) "
                  "at business/functional level — no code, no technology choices.",
    "architect-agent": "Translates an approved SDD into a Technical Architecture Document "
                        "(TAD): data model, components, integrations, security, deployment "
                        "topology.",
    "development-agent": "Implements a feature per the approved TAD and SDD; produces the Dev "
                          "Summary and build/pipeline configs; fans out to sub-agents for "
                          "data, backend, frontend, automation, identity, M365 and config work.",
    "test-agent": "Validates a build artifact against SDD/TAD requirements as the final "
                  "constraint verifier; produces the Test Report.",
    "build-agent": "Packages the solution per config/<slug>-build.yml and diagnoses packer "
                    "and tool output.",
    "pipeline-agent": "Deploys the build artifact through the environment chain per "
                       "config/<slug>-pipeline.yml; produces the Deployment Summary.",
    "improvement-agent": "Processes logs/improvement-log.jsonl findings into durable changes "
                          "to agents/, constraints/, skills/, knowledge/, behind APPROVE "
                          "IMPROVEMENTS. The only agent that edits this system's own rules.",
    "pm-agent": "Owns the plan of record: the contracted baseline, WBS task state derived "
                "from evidence, the ready-to-build queue, and schedule/drift reporting.",
    "commercial-agent": "Owns billable hours, change orders and invoices, derived from "
                         "evidence. The only agent that writes logs/worklog.jsonl.",
    "acceptance-agent": "Produces phase acceptance records and handover packs; owns the "
                         "warranty clock.",
}

# Sub-agents spawned by development-agent have no `agents/<name>.md` of their own — their
# instructions live in agents/development-agent.md's Sub-Agents table plus, for most of them,
# one named skill. (skill: None) means the table entry is the whole instruction.
SUB_AGENT_DESCRIPTIONS_AND_SKILL = {
    "data-agent": (
        "Schema and migrations for one feature, following the TAD and coding standards.",
        "skills/how-to-model-a-data-schema.md",
    ),
    "backend-agent": (
        "APIs, services and business logic for one feature, within the approved TAD.",
        None,
    ),
    "frontend-agent": (
        "UI components and views for one feature.",
        "skills/accessibility-checklist.md",
    ),
    "automation-agent": (
        "Workflows, jobs and event handlers for one feature.",
        "skills/how-to-design-a-workflow.md",
    ),
    "identity-agent": (
        "App registrations, security roles, group teams and app sharing for one feature.",
        "knowledge/technology/entra-id.md and knowledge/technology/security-model.md",
    ),
    "m365-agent": (
        "SharePoint sites and Teams provisioning/app packages for one feature.",
        "knowledge/technology/sharepoint.md and knowledge/technology/teams.md",
    ),
    "config-agent": (
        "Environment config, secrets and feature flags for one feature — rule-following, no "
        "novel reasoning.",
        None,
    ),
}

ROSTER_BODY = """\
You are `{name}` in the Revitalise multi-agent delivery system.

Read `agents/{name}.md` in full and follow it exactly: role, activation steps, knowledge to
load, constraints to check, and gate output format. That file is the only source of your
instructions — nothing here duplicates it, so it cannot drift out of sync with it.
{escalation}
This subagent invocation IS the session boundary described in `agents/WORKFLOW.md` →
"Session Boundaries". Produce exactly the output your gate requires, emit your `HANDOFF` line
(or `BLOCKED` / `DEPLOYMENT FAILED`, whichever applies), and stop there. Do not keep working
after your gate output — a further instruction to this agent is a new dispatch, carrying the
doc path forward, not a continued conversation with you.

Reference documents the caller gave you **by path**; read them yourself. Never ask the caller
to paste content you can read, and never paste large content back to the caller — return the
gate block and the doc path, per `agents/README.md` → "Token Efficiency Rules".
"""

SUB_AGENT_BODY = """\
You are `{name}`, a sub-agent spawned by `development-agent` in the Revitalise multi-agent
delivery system.

Read `agents/development-agent.md` → "Sub-Agents" for your responsibility{skill_clause}. You
are given the TAD, SDD, and technology constraints **by path** — read them yourself; do not
expect them pasted into your prompt, and do not paste them back.

This subagent invocation IS the session boundary described in `agents/WORKFLOW.md` →
"Session Boundaries". Build your part, report back to `development-agent` what you built and
which WBS task id(s) it serves, and stop — do not continue past that report.
"""

GENERATED_BANNER = """\
<!--
GENERATED FILE — do not hand-edit. Regenerate with `python3 scripts/generate-subagents.py`
after any change to `config/models.yml`. CI and improvement-agent verify it is current with
`--check`.

Model is resolved from config/models.yml → {source_path}.tier = "{tier}" → Claude Code model
alias "{alias}". To change the model this subagent runs on, edit config/models.yml and
regenerate — never hand-edit the frontmatter below.
-->

"""


def load_models(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist — nothing to generate from")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "agents" not in data or "tiers" not in data:
        raise ValueError(f"{path} does not look like a models config (missing tiers/agents)")
    return data


def escalation_note(entry: dict) -> str:
    lines = []
    esc = entry.get("escalate_to_strategic_when")
    if esc:
        lines.append(
            "\nBefore YOU start work, the agent that dispatched you should have already "
            "checked these — if one is true and you were dispatched at your default tier "
            "anyway, stop and ask the caller to re-dispatch you with a `model: opus` override "
            "rather than trying to reason your way through it on this pin:\n"
        )
        lines.extend(f"- {c}" for c in esc)
    deesc = entry.get("de_escalate_to_mechanical_when")
    if deesc:
        lines.append(
            "\nThe caller may instead dispatch you with a `model: haiku` override when:\n"
        )
        lines.extend(f"- {c}" for c in deesc)
    return ("\n".join(lines) + "\n") if lines else "\n"


def render_roster(name: str, entry: dict, description: str) -> str:
    tier = entry["tier"]
    alias = TIER_TO_MODEL_ALIAS[tier]
    front = f"---\nname: {name}\ndescription: {description}\nmodel: {alias}\n---\n\n"
    banner = GENERATED_BANNER.format(source_path=f"agents.{name}", tier=tier, alias=alias)
    body = ROSTER_BODY.format(name=name, escalation=escalation_note(entry))
    return front + banner + body


def render_sub_agent(name: str, entry: dict, description: str, skill: str | None) -> str:
    tier = entry["tier"]
    alias = TIER_TO_MODEL_ALIAS[tier]
    front = f"---\nname: {name}\ndescription: {description}\nmodel: {alias}\n---\n\n"
    banner = GENERATED_BANNER.format(source_path=f"sub_agents.{name}", tier=tier, alias=alias)
    skill_clause = f", and {skill} for how to do it" if skill else ""
    body = SUB_AGENT_BODY.format(name=name, skill_clause=skill_clause)
    escalation = escalation_note(entry)
    if escalation.strip():
        body += escalation
    return front + banner + body


def build_files(data: dict) -> dict[str, str]:
    files: dict[str, str] = {}
    errors: list[str] = []

    roster = data.get("agents", {})
    for name, entry in roster.items():
        if name not in ROSTER_DESCRIPTIONS:
            errors.append(
                f"agents.{name} is in config/models.yml but has no entry in "
                f"ROSTER_DESCRIPTIONS in this script — add one before generating."
            )
            continue
        src = AGENTS_DIR / f"{name}.md"
        if not src.exists():
            errors.append(f"agents.{name} declares a tier but {src} does not exist.")
            continue
        tier = entry.get("tier")
        if tier not in TIER_TO_MODEL_ALIAS:
            errors.append(f"agents.{name}.tier is {tier!r} — not one of {list(TIER_TO_MODEL_ALIAS)}.")
            continue
        files[f"{name}.md"] = render_roster(name, entry, ROSTER_DESCRIPTIONS[name])

    for name in ROSTER_DESCRIPTIONS:
        if name not in roster:
            errors.append(
                f"{name} has a ROSTER_DESCRIPTIONS entry but no agents.{name} in "
                f"config/models.yml — remove the stale entry or add the tier."
            )

    sub_agents = data.get("sub_agents", {})
    for name, entry in sub_agents.items():
        if name not in SUB_AGENT_DESCRIPTIONS_AND_SKILL:
            errors.append(
                f"sub_agents.{name} is in config/models.yml but has no entry in "
                f"SUB_AGENT_DESCRIPTIONS_AND_SKILL in this script — add one before generating."
            )
            continue
        description, skill = SUB_AGENT_DESCRIPTIONS_AND_SKILL[name]
        tier = entry.get("tier")
        if tier not in TIER_TO_MODEL_ALIAS:
            errors.append(f"sub_agents.{name}.tier is {tier!r} — not one of {list(TIER_TO_MODEL_ALIAS)}.")
            continue
        # ── every tier is an argued tier ────────────────────────────────────────────────
        # IMP-0162, improvement review 6 item 7, applied 2026-08-22. `frontend-agent` read
        # `tier: standard` with no rationale and no escalation conditions at all, while
        # narrower sub-agents carried explicit rules — and it had just been handed the first
        # hand-authored React Code App in the repository, which is verbatim one of the
        # conditions that escalates `development-agent` itself. The override had to be
        # remembered by hand at every dispatch.
        #
        # The failure mode is what makes this a check rather than a convention: a missing
        # escalation condition fails SILENTLY. The work simply runs on a cheaper model and
        # nobody is told. So an omission must be a written decision, not an empty key.
        if not str(entry.get("rationale") or "").strip():
            errors.append(
                f"sub_agents.{name} has no 'rationale'. A tier is a cost and risk decision; "
                f"an unexplained one cannot be reviewed, and IMP-0162 is what an unexplained "
                f"`tier: standard` cost when the artefact type changed under it.")
        if not entry.get("escalate_to_strategic_when") and \
                not str(entry.get("no_escalation_because") or "").strip():
            errors.append(
                f"sub_agents.{name} declares no 'escalate_to_strategic_when' conditions and no "
                f"'no_escalation_because'. Say which — an absent escalation rule is "
                f"indistinguishable from a deliberate one, and it fails quietly in the cheap "
                f"direction (IMP-0162).")

        files[f"{name}.md"] = render_sub_agent(name, entry, description, skill)

    for name in SUB_AGENT_DESCRIPTIONS_AND_SKILL:
        if name not in sub_agents:
            errors.append(
                f"{name} has a SUB_AGENT_DESCRIPTIONS_AND_SKILL entry but no sub_agents.{name} "
                f"in config/models.yml — remove the stale entry or add the tier."
            )

    if errors:
        raise ValueError("\n".join(errors))
    return files


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--models", type=Path, default=MODELS_YML)
    p.add_argument("--out-dir", type=Path, default=OUT_DIR)
    p.add_argument("--check", action="store_true", help="exit 1 if any file is stale or missing")
    p.add_argument("--stdout", action="store_true", help="print instead of writing")
    args = p.parse_args(argv)

    try:
        data = load_models(args.models)
        files = build_files(data)
    except (FileNotFoundError, ValueError) as exc:
        print(f"generate-subagents: {exc}", file=sys.stderr)
        return 2

    if args.stdout:
        for name, text in sorted(files.items()):
            print(f"=== {args.out_dir / name} ===")
            print(text)
        return 0

    if args.check:
        stale = []
        for name, text in sorted(files.items()):
            path = args.out_dir / name
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                stale.append(str(path))
        extra = []
        if args.out_dir.exists():
            expected = {args.out_dir / n for n in files}
            extra = sorted(
                str(p) for p in args.out_dir.glob("*.md") if p not in expected
            )
        if stale or extra:
            for s in stale:
                print(f"generate-subagents: STALE or missing: {s}", file=sys.stderr)
            for e in extra:
                print(f"generate-subagents: ORPHANED (no matching config/models.yml entry): {e}",
                      file=sys.stderr)
            print(
                "generate-subagents: run `python3 scripts/generate-subagents.py` to fix.",
                file=sys.stderr,
            )
            return 1
        print(f"generate-subagents: {args.out_dir} is current ({len(files)} files).")
        return 0

    args.out_dir.mkdir(parents=True, exist_ok=True)
    for name, text in files.items():
        (args.out_dir / name).write_text(text, encoding="utf-8")
    print(f"generate-subagents: wrote {len(files)} files to {args.out_dir}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
