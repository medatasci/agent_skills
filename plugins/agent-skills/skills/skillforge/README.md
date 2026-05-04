# SkillForge

Skill ID: `skillforge`

Use SkillForge to find, inspect, install, remove, share, update, evaluate, and
manage reusable Codex skills.

## Repo And Package

Skill repo URL:
https://github.com/medatasci/agent_skills/tree/main/skills/skillforge

Parent package:
SkillForge Agent Skills Marketplace

Parent package repo URL:
https://github.com/medatasci/agent_skills

Distribution or marketplace:
SkillForge local catalog and Codex skill install workflow

## Parent Collection

Parent collection:
SkillForge Agent Skills Marketplace

Collection URL:
https://github.com/medatasci/agent_skills

Categories:
Developer Tools, Skill Management, Agent Workflows

## What This Skill Does

This skill tells Codex how to use SkillForge itself. It covers onboarding,
search, peer catalogs, skill inspection, install, removal, feedback,
pull-request contribution drafting, skill creation, catalog rebuilds,
publication evaluation, update checks, and user-facing "what changed"
summaries.

It also defines SkillForge's agent-facing behavior: helpful, practical,
novice-friendly, safety-aware, transparent about side effects, next-step aware,
adjustable in chattiness, and deterministic enough for agents.

For contribution requests, it should distinguish whether the user is a
developer, non-developer, or unknown. That profile changes the amount of Git/PR
guidance, not the safety rule: normal contributions should go through pull
requests.

## Why You Would Call It

Call this skill when:

- You ask what SkillForge is or how to use it.
- You want to search local SkillForge skills or peer catalogs.
- You want to inspect or install a skill.
- You want to list or remove installed skills.
- You want to create, share, or evaluate a SkillForge skill.
- You want to submit a bug fix, feature, docs change, or new skill as a pull
  request.
- You want to check whether SkillForge has updates.
- You want feedback turned into a GitHub issue draft.

## Keywords

SkillForge, Agent Skills Marketplace, Codex skills, skill search, peer catalogs,
install skills, remove skills, share skills, skill feedback, SkillForge pull
request, skill evaluation, SkillForge update.

## Search Terms

Use SkillForge, how do I use SkillForge, find Codex skills, install a Codex
skill, search peer catalogs, SkillForge help, SkillForge welcome, update
SkillForge, create a SkillForge skill, share my skill, contribute a SkillForge
pull request.

## How It Works

The skill routes SkillForge requests to deterministic CLI commands when stateful
work is needed. It keeps the conversation practical by answering the immediate
request, surfacing important side effects, and offering one or two likely next
steps.

Peer catalog results are treated as discovery results, not endorsements. Install
actions should include source awareness and appropriate user confirmation.

## API And Options

Common CLI commands:

```text
python -m skillforge welcome
python -m skillforge getting-started
python -m skillforge help
python -m skillforge corpus-search "task"
python -m skillforge info <skill-id> --json
python -m skillforge install <skill-id> --scope global
python -m skillforge list --scope global
python -m skillforge remove <skill-id> --scope global
python -m skillforge feedback <subject> --trying "..." --happened "..."
python -m skillforge contribute "summary" --type docs --changed README.md --user-type non-developer --json
python -m skillforge build-catalog
python -m skillforge evaluate <skill-id> --json
python -m skillforge update-check --json
python -m skillforge whats-new
```

Output style can be adjusted with:

```text
--chattiness coach|normal|terse|silent
```

or:

```text
SKILLFORGE_CHATTINESS=coach
```

## Inputs And Outputs

Inputs:

- User intent or task description.
- Optional skill name.
- Optional peer catalog source.
- Optional Codex scope or project path.
- Optional chattiness preference.

Outputs:

- Promptable guidance.
- Deterministic CLI command.
- Source-aware search or install guidance.
- Side-effect and safety notes.
- One or two likely next steps.

## Examples

Promptable:

```text
SkillForge, help me find a skill that helps write an email.
```

```text
Search SkillForge and peer catalogs for SQL database access skills, but ask before installing peer results.
```

CLI:

```text
python -m skillforge corpus-search "write an email"
python -m skillforge info project-retrospective --json
```

## Help

Start here:

```text
python -m skillforge welcome
python -m skillforge getting-started
python -m skillforge help
python -m skillforge help search
```

For troubleshooting:

```text
python -m skillforge doctor --json
```

## How To Call From An LLM

Use plain language:

```text
SkillForge, find a skill that helps me write an email.
```

```text
SkillForge, show me what is installed and help me decide what to try next.
```

When an action may write files, install skills, update Codex config, fetch peer
catalogs, or update SkillForge itself, ask the user before taking the action
unless they already gave explicit approval.

## How To Call From The CLI

Use `python -m skillforge <command>` from a SkillForge checkout.

Use `--json` when another agent or script needs stable machine-readable output.
Use `--chattiness terse` or `--chattiness silent` when the user wants less
explanation.

## Trust And Safety

Risk level:
Low by default, but individual commands can have higher impact.

Permissions:

- Read local SkillForge docs, catalog metadata, and skill files.
- Run local SkillForge Python commands.
- Write only for commands such as install, remove, create, build-catalog,
  import-peer, or update with explicit confirmation.
- Use network only for peer refresh, update checks, source retrieval, or Git
  operations when needed and allowed.

Data handling:
Do not add NVIDIA-internal data, secrets, private process knowledge, or
privileged automation to public SkillForge content.

Writes vs read-only:
Search, info, help, welcome, getting-started, doctor, evaluate, update-check,
and whats-new are intended to be read-only. Install, remove, create,
build-catalog, import-peer, and update --yes can write files.

## Limitations

- SkillForge search results are discovery aids, not trust guarantees.
- Peer catalog metadata may be incomplete or stale.
- Network operations can fail in restricted environments.
- The skill should not invent capabilities, owners, review status, citations,
  permissions, or trust claims.

## Feedback

Feedback URL:
https://github.com/medatasci/agent_skills/issues

CLI feedback draft:

```text
python -m skillforge feedback "SkillForge help" --trying "find a skill" --happened "the next step was unclear"
```

## Contributing

Feedback and contributions are intentionally separate. Use `feedback` when you
want to report a bug, describe confusion, request a feature, or suggest a
missing workflow. Use `contribute` when you have a bug fix, feature,
documentation change, catalog update, or new skill ready for review as a pull
request.

Contributions are welcome through GitHub pull requests. For normal users and
agents, the default is to prepare a branch and PR, not to push directly to
`main`. For new or changed skills, update `SKILL.md`, update the skill
`README.md` when needed, run `python -m skillforge build-catalog`, and run
`python -m skillforge evaluate <skill-id> --json`.

If the contributor is not a developer, Codex should offer to handle the branch,
checks, commit, push, and PR preparation step by step. If the contributor is a
developer, Codex can show the exact commands, but should still default to a PR.

## Author

Marc Edgar / medatasci

## Citations

Not applicable. This skill describes the SkillForge workflow and repository
behavior.

## Related Skills

- `skill-discovery-evaluation`: evaluate and improve skill discoverability and
  publication readiness.
- `project-retrospective`: preserve lessons from a SkillForge development or
  usage session.
