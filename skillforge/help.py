from __future__ import annotations

import re

from .output import is_coach, normalize_chattiness


WELCOME_TITLE = "Welcome to SkillForge."
WELCOME_MESSAGE = (
    "SkillForge is your tool for creating, saving, and sharing your own skills, "
    "and for searching skills created by others so useful Codex workflows do "
    "not have to be reinvented."
)
WELCOME_START = "What would you like to do?"
WELCOME_QUESTION = "What would you like to do first?"
WELCOME_EXAMPLES = [
    "SkillForge, find a skill that helps me write an email.",
    "SkillForge, help me create a skill to research a dataset.",
    "Share my skill and add it to the SkillForge catalog.",
    "Show me what SkillForge skills are installed.",
    "How do I use SkillForge?",
    "Help me decide whether a skill is safe to install.",
    "Update SkillForge.",
]
WELCOME_NEXT_STEPS = [
    "Search first; install only after reviewing a result.",
    "Treat peer catalogs as discovery sources, not trust endorsements.",
    "Ask for help when you are unsure what to do next.",
]


def _command(command: str, description: str, *, side_effects: str, examples: list[str], related: list[str]) -> dict:
    return {
        "command": command,
        "description": description,
        "side_effects": side_effects,
        "examples": examples,
        "related": related,
    }


TOPICS: dict[str, dict] = {
    "overview": {
        "summary": "SkillForge helps you find, inspect, install, share, and maintain Codex skills.",
        "prompt_examples": [
            "Help me use SkillForge.",
            "Find a SkillForge skill that helps with writing status emails.",
            "Search SkillForge and peer catalogs for database access skills, but ask before installing anything.",
        ],
        "commands": [
            _command(
                "python -m skillforge corpus-search \"task or workflow\"",
                "Search local and cached peer provider catalogs by task.",
                side_effects="Reads local catalog and provider cache; may refresh provider catalogs when cache is expired.",
                examples=[
                    "python -m skillforge corpus-search \"write an email\"",
                    "python -m skillforge corpus-search \"SQL database access\" --json",
                ],
                related=["search", "peer-search", "cache catalogs"],
            ),
            _command(
                "python -m skillforge info <skill-id> --json",
                "Inspect metadata, source, checksum, warnings, and install commands for one skill.",
                side_effects="Read-only.",
                examples=["python -m skillforge info project-retrospective --json"],
                related=["install", "evaluate"],
            ),
            _command(
                "python -m skillforge install <skill-id> --scope global",
                "Install a reviewed SkillForge skill into Codex.",
                side_effects="Writes to the selected Codex skills directory after validation.",
                examples=["python -m skillforge install project-retrospective --scope global"],
                related=["info", "list", "remove"],
            ),
            _command(
                "python -m skillforge feedback <subject> --trying \"...\" --happened \"...\"",
                "Draft structured GitHub issue feedback for a skill, CLI command, helper, or documentation.",
                side_effects="Read-only; drafts issue text but does not submit it.",
                examples=[
                    "python -m skillforge feedback \"skill search\" --trying \"find a Pomodoro timer\" --happened \"no dedicated timer skill appeared\""
                ],
                related=["help", "search"],
            ),
        ],
        "next_steps": [
            "Run `python -m skillforge welcome` for a novice-friendly welcome.",
            "Run `python -m skillforge getting-started` for a practical first-run guide.",
            "Run `python -m skillforge doctor --json` if Codex paths or install state are confusing.",
            "Run `python -m skillforge help search` if you know the task but not the skill name.",
        ],
    },
    "search": {
        "summary": "Use search when you know the task or outcome but not the skill name.",
        "prompt_examples": [
            "Search for skills that will help me write an email.",
            "Search SkillForge and peer catalogs for skills that help with SQL database access. Ask before installing peer results.",
        ],
        "commands": [
            _command(
                "python -m skillforge corpus-search \"task\"",
                "Best default discovery command; searches cached provider catalog snapshots and local results.",
                side_effects="Reads local catalog and provider cache; may refresh expired provider catalog cache.",
                examples=[
                    "python -m skillforge corpus-search \"write an email\"",
                    "python -m skillforge corpus-search \"time management pomodoro timer\" --chattiness terse",
                ],
                related=["search", "peer-search", "cache catalogs"],
            ),
            _command(
                "python -m skillforge search \"task\" --json",
                "Search only the local SkillForge catalog.",
                side_effects="Read-only.",
                examples=["python -m skillforge search \"YouTube transcripts\" --json"],
                related=["corpus-search", "info"],
            ),
            _command(
                "python -m skillforge peer-search \"task\" --refresh --json",
                "Run live peer search against configured peer catalogs.",
                side_effects="May use network and update peer cache.",
                examples=["python -m skillforge peer-search \"SQL database access\" --refresh --json"],
                related=["corpus-search", "peer-diagnostics"],
            ),
        ],
        "next_steps": [
            "Use `info <skill-id> --json` before installing a local SkillForge result.",
            "Review the source URL before installing anything from a peer catalog.",
            "Send feedback if the result is weak or a missing workflow should exist.",
        ],
    },
    "install": {
        "summary": "Install only after the skill source and metadata look right for the task.",
        "prompt_examples": [
            "Install the SkillForge project-retrospective skill into Codex.",
            "Use SkillForge to install huggingface-datasets.",
        ],
        "commands": [
            _command(
                "python -m skillforge install <skill-id> --scope global",
                "Install a local SkillForge catalog skill globally for Codex.",
                side_effects="Writes a copy of the skill into the global Codex skills directory.",
                examples=["python -m skillforge install project-retrospective --scope global"],
                related=["info", "list", "remove"],
            ),
            _command(
                "python -m skillforge install <skill-id> --peer <peer-id> --scope global --yes",
                "Install a peer skill after explicit source review.",
                side_effects="Writes to Codex skills directory from peer cache; does not import into this repository.",
                examples=["python -m skillforge install email-drafter --peer github-awesome-copilot --scope global --yes"],
                related=["peer-search", "import-peer"],
            ),
        ],
        "next_steps": [
            "Run `python -m skillforge list --scope global` to confirm the installed skill.",
            "Restart Codex or start a fresh session if newly installed skills do not appear.",
        ],
    },
    "feedback": {
        "summary": "Use feedback when a skill helped, failed, confused you, or should exist.",
        "prompt_examples": [
            "Send feedback on skill search that Pomodoro timer results were weak.",
            "Please help me send feedback to SkillForge about the README install flow.",
        ],
        "commands": [
            _command(
                "python -m skillforge feedback <subject> --trying \"...\" --happened \"...\"",
                "Create a structured GitHub issue draft.",
                side_effects="Read-only; no authenticated GitHub write.",
                examples=[
                    "python -m skillforge feedback \"docs:README\" --trying \"install SkillForge\" --happened \"the install prompt was unclear\" --json"
                ],
                related=["help", "search"],
            )
        ],
        "next_steps": ["Paste the drafted issue into GitHub or ask Codex to prepare it for review."],
    },
    "create": {
        "summary": "Use create or upload when turning a repeated workflow into a reusable skill.",
        "prompt_examples": [
            "Create a SkillForge skill named pomodoro-focus-timer for guided focus sessions.",
            "Package this repeated workflow as a SkillForge skill and evaluate it for publication.",
        ],
        "commands": [
            _command(
                "python -m skillforge create <skill-id> --title \"...\" --description \"...\"",
                "Scaffold SKILL.md and README.md from SkillForge templates.",
                side_effects="Writes new files under skills/<skill-id>/.",
                examples=[
                    "python -m skillforge create pomodoro-focus-timer --title \"Pomodoro Focus Timer\" --description \"Guide timed focus sessions.\" --owner medatasci --risk-level low"
                ],
                related=["build-catalog", "evaluate"],
            ),
            _command(
                "python -m skillforge evaluate <skill-id> --json",
                "Check publication readiness after editing the skill.",
                side_effects="Read-only.",
                examples=["python -m skillforge evaluate pomodoro-focus-timer --json"],
                related=["search-audit", "build-catalog"],
            ),
        ],
        "next_steps": ["Run `build-catalog`, then `evaluate`, before opening a pull request."],
    },
    "update": {
        "summary": "Use update awareness to see whether the local SkillForge checkout is behind upstream, then update only with explicit confirmation.",
        "prompt_examples": [
            "Check whether SkillForge has updates. Show what changed and ask before changing files.",
            "Update SkillForge if a safe fast-forward update is available. Show me what changed afterward.",
        ],
        "commands": [
            _command(
                "python -m skillforge update-check --json",
                "Compare the local checkout with its upstream branch and cache the result for the periodic check window.",
                side_effects="May run a Git fetch when cached update status is older than the default check window.",
                examples=["python -m skillforge update-check --json", "python -m skillforge update-check --no-fetch --json"],
                related=["update", "whats-new"],
            ),
            _command(
                "python -m skillforge update --yes",
                "Apply a fast-forward-only SkillForge update when the checkout is clean and not diverged.",
                side_effects="May fetch upstream, then changes local repository files only through a Git fast-forward merge.",
                examples=["python -m skillforge update", "python -m skillforge update --yes --json"],
                related=["update-check", "whats-new"],
            ),
            _command(
                "python -m skillforge whats-new",
                "Summarize Git changes since the previous local revision or a supplied commit.",
                side_effects="Read-only.",
                examples=["python -m skillforge whats-new", "python -m skillforge whats-new --since HEAD~3 --json"],
                related=["update-check"],
            ),
        ],
        "next_steps": [
            "Run `python -m skillforge update` first when you want a dry-run style status with no file changes.",
            "Run `python -m skillforge update --yes` only when you are ready for a safe fast-forward update.",
        ],
    },
    "doctor": {
        "summary": "Use doctor when Codex paths, scopes, or install locations are confusing.",
        "prompt_examples": ["Check whether SkillForge is installed into my real Codex environment."],
        "commands": [
            _command(
                "python -m skillforge doctor --json",
                "Show global and project Codex skills paths.",
                side_effects="Read-only.",
                examples=["python -m skillforge doctor --json", "python -m skillforge doctor --project . --json"],
                related=["install", "list"],
            )
        ],
        "next_steps": ["Use the reported path to verify whether a skill was installed globally or for one project."],
    },
    "chattiness": {
        "summary": "Use chattiness to control how much extra guidance SkillForge prints.",
        "prompt_examples": ["Make SkillForge terse for scripted output, but keep JSON stable."],
        "commands": [
            _command(
                "python -m skillforge search \"task\" --chattiness terse",
                "Run selected commands with less extra prose.",
                side_effects="Read-only for search/help commands.",
                examples=[
                    "python -m skillforge corpus-search \"write an email\" --chattiness coach",
                    "python -m skillforge help search --chattiness silent",
                ],
                related=["help", "search"],
            )
        ],
        "next_steps": [
            "Set `SKILLFORGE_CHATTINESS=coach|normal|terse|silent` to change the default for supported commands.",
            "`--json` output remains machine-readable regardless of chattiness.",
        ],
    },
}


ALIASES = {
    "welcome": "overview",
    "getting-started": "overview",
    "start": "overview",
    "onboarding": "overview",
    "find": "search",
    "peer-search": "search",
    "corpus-search": "search",
    "share": "create",
    "publish": "create",
    "updates": "update",
    "what's-new": "update",
    "whats-new": "update",
    "quiet": "chattiness",
    "verbose": "chattiness",
    "config": "chattiness",
}


def normalize_topic(topic: str | None) -> str:
    if not topic:
        return "overview"
    value = topic.strip().lower()
    if value in TOPICS:
        return value
    if value in ALIASES:
        return ALIASES[value]

    words = set(re.findall(r"[a-z0-9-]+", value))
    if words & {"search", "find", "discover", "lookup", "catalog"}:
        return "search"
    if words & {"install", "download", "use"}:
        return "install"
    if words & {"feedback", "issue", "bug", "confusing", "failed"}:
        return "feedback"
    if words & {"create", "share", "publish", "package", "skill"}:
        return "create"
    if words & {"update", "upstream", "new", "changed", "version"}:
        return "update"
    if words & {"doctor", "path", "codex", "environment"}:
        return "doctor"
    if words & {"quiet", "silent", "verbose", "chatty", "chattiness", "terse"}:
        return "chattiness"
    return "overview"


def help_payload(topic: str | None = None) -> dict:
    normalized = normalize_topic(topic)
    payload = dict(TOPICS[normalized])
    payload["topic"] = normalized
    payload["requested_topic"] = topic
    payload["available_topics"] = sorted(TOPICS)
    return payload


def welcome_payload() -> dict:
    return {
        "topic": "welcome",
        "title": WELCOME_TITLE,
        "message": WELCOME_MESSAGE,
        "start": WELCOME_START,
        "question": WELCOME_QUESTION,
        "examples": list(WELCOME_EXAMPLES),
        "next_steps": list(WELCOME_NEXT_STEPS),
        "commands": [
            {
                "command": "python -m skillforge welcome",
                "description": "Show this novice-friendly welcome message.",
                "side_effects": "Read-only.",
            },
            {
                "command": "python -m skillforge getting-started",
                "description": "Show the first practical commands after install.",
                "side_effects": "Read-only.",
            },
            {
                "command": "python -m skillforge help",
                "description": "Show workflow help for SkillForge.",
                "side_effects": "Read-only.",
            },
        ],
    }


def getting_started_payload() -> dict:
    return {
        "topic": "getting-started",
        "summary": "Start with a health check, then search by task, inspect before installing, and ask for help when unsure.",
        "steps": [
            {
                "name": "Check Codex paths",
                "why": "Confirms where global and project skills will be installed.",
                "command": "python -m skillforge doctor --json",
            },
            {
                "name": "Search by task",
                "why": "Finds skills by workflow intent, including cached peer catalog results.",
                "command": "python -m skillforge corpus-search \"write an email\"",
            },
            {
                "name": "Inspect a result",
                "why": "Shows source, checksum, warnings, and install commands before making changes.",
                "command": "python -m skillforge info <skill-id> --json",
            },
            {
                "name": "Install only after review",
                "why": "Copies a selected skill into the chosen Codex scope.",
                "command": "python -m skillforge install <skill-id> --scope global",
            },
            {
                "name": "List installed skills",
                "why": "Shows what Codex skills are currently installed.",
                "command": "python -m skillforge list --scope global",
            },
            {
                "name": "Get help or send feedback",
                "why": "Turns uncertainty or weak search results into a next action.",
                "command": "python -m skillforge help search",
            },
            {
                "name": "Check for SkillForge updates",
                "why": "Compares your checkout with upstream using a cached periodic check.",
                "command": "python -m skillforge update-check --json",
            },
            {
                "name": "Update SkillForge",
                "why": "Applies a safe fast-forward update only after explicit confirmation.",
                "command": "python -m skillforge update --yes",
            },
        ],
        "prompt_examples": [
            "Help me use SkillForge.",
            "Search for skills that help with <task>. Ask before installing anything from a peer catalog.",
            "Send feedback on skill search that <what happened>.",
            "Update SkillForge and show me what changed.",
        ],
    }


def render_welcome(payload: dict, *, chattiness: str = "normal") -> str:
    mode = normalize_chattiness(chattiness)
    if mode == "silent":
        return "\n".join(payload["examples"])

    lines = [payload["title"], "", payload["message"], "", payload["start"], "", "Examples:"]
    for example in payload["examples"]:
        lines.append(f"- {example}")
    if mode != "terse":
        lines.append("")
        lines.append("What SkillForge will do:")
        lines.append("- Search before installing.")
        lines.append("- Explain where results came from.")
        lines.append("- Ask before installing anything from a peer catalog.")
        lines.append("- Help you create and share repeatable skills.")
    if is_coach(mode):
        lines.append("")
        lines.append(payload["question"])
    return "\n".join(lines)


def render_help(payload: dict, *, chattiness: str = "normal") -> str:
    mode = normalize_chattiness(chattiness)
    lines: list[str] = [payload["summary"]]
    if mode == "silent":
        lines.extend(command["command"] for command in payload.get("commands", []))
        return "\n".join(lines)

    if payload.get("prompt_examples") and mode != "terse":
        lines.append("")
        lines.append("Prompt examples:")
        for example in payload["prompt_examples"]:
            lines.append(f"- {example}")

    lines.append("")
    lines.append("CLI commands:")
    for command in payload.get("commands", []):
        lines.append(f"- `{command['command']}`")
        if mode != "terse":
            lines.append(f"  {command['description']}")
            lines.append(f"  Side effects: {command['side_effects']}")
            for example in command["examples"][:2]:
                lines.append(f"  Example: `{example}`")

    if payload.get("next_steps") and mode != "terse":
        lines.append("")
        lines.append("Next steps:")
        for step in payload["next_steps"]:
            lines.append(f"- {step}")

    if is_coach(mode):
        lines.append("")
        lines.append("Tip: inspect before installing, and treat peer catalogs as discovery sources rather than endorsements.")
    return "\n".join(lines)


def render_getting_started(payload: dict, *, chattiness: str = "normal") -> str:
    mode = normalize_chattiness(chattiness)
    lines: list[str] = [payload["summary"]]
    if mode == "silent":
        lines.extend(step["command"] for step in payload["steps"])
        return "\n".join(lines)

    lines.append("")
    lines.append("First useful commands:")
    for index, step in enumerate(payload["steps"], start=1):
        lines.append(f"{index}. {step['name']}")
        lines.append(f"   `{step['command']}`")
        if mode not in {"terse", "silent"}:
            lines.append(f"   {step['why']}")

    if mode != "terse":
        lines.append("")
        lines.append("Promptable starts:")
        for example in payload["prompt_examples"]:
            lines.append(f"- {example}")

    if is_coach(mode):
        lines.append("")
        lines.append("Good default rhythm: search, inspect, install only after review, then send feedback when a result is weak.")
    return "\n".join(lines)
