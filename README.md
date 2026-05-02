# SkillForge Agent Skills Marketplace

Reusable Codex workflows for people who do not want to reinvent the wheel.

SkillForge is a growing collection of practical Codex skills for accessing
information, analyzing work, preserving context, and turning useful prompts into
repeatable business workflows.

The idea is simple:

- **Find a useful workflow.** Search for skills by task, topic, or name.
- **Use it with a prompt.** You should not need to know Git, Bash, PowerShell,
  or local Codex internals to get value from a skill.
- **Improve it together.** If a skill helps, breaks, or inspires a better one,
  feedback is welcome.
- **Share what works.** If you build a useful skill, SkillForge should help turn
  it into a pull request so others can benefit.

## What You Can Do Here

- **Search for new skills.** Browse the SkillForge Skill List or ask Codex what
  is available.
- **Download and install a skill.** Use one prompt in Codex, or call the
  SkillForge CLI directly.
- **Refresh skills you use.** Update local copies as skills improve.
- **Provide feedback.** Report what helped, failed, confused you, or should
  exist next.
- **Share a skill you developed.** Package a repeated workflow as a reusable
  `SKILL.md` contribution.

## Use SkillForge

SkillForge is designed to work two ways:

- **Codex Promptable:** ask Codex in plain language.
- **CLI API:** run the deterministic Python command directly.

## Workflow

1. Install SkillForge.
2. Search for a skill in SkillForge and known peer catalogs.
3. Install the skill into Codex.
4. Browse the SkillForge Skill List.
5. Send feedback on a skill, Python helper, CLI command, or documentation.
6. Submit improvements through Git.
7. Uninstall skills you no longer want.

## 1. Install SkillForge

### Codex Prompt

Open Codex and paste this prompt:

```text
Please install SkillForge for my real Codex environment.

Use this repo:
https://github.com/medatasci/agent_skills

Register it as a Codex marketplace, enable the Agent Skills plugin, verify the
SkillForge Skill List is readable, and tell me whether I need to restart Codex.

Do not modify unrelated Codex settings. If anything fails or is ambiguous, stop
and ask me.
```

### Git Clone

PowerShell:

```powershell
$CodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE ".codex" }
$Marketplace = Join-Path $CodexHome "plugins\cache\agent-skills-marketplace"

git clone --depth 1 --branch main https://github.com/medatasci/agent_skills.git $Marketplace
```

macOS/Linux:

```bash
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
MARKETPLACE="$CODEX_HOME/plugins/cache/agent-skills-marketplace"

git clone --depth 1 --branch main https://github.com/medatasci/agent_skills.git "$MARKETPLACE"
```

Then add or confirm these entries in `<CODEX_HOME>/config.toml`:

```toml
[marketplaces.agent-skills-marketplace]
source_type = "git"
source = "https://github.com/medatasci/agent_skills.git"
ref = "main"

[plugins."agent-skills@agent-skills-marketplace"]
enabled = true
```

Restart Codex if needed.

### Advanced Install Prompt

Use this version when Codex is confused about where to install the marketplace,
which Codex home to use, or how to verify the setup:

```text
Please install SkillForge for my real Codex environment.

Use this repo:
https://github.com/medatasci/agent_skills

Do not ask me to open a terminal unless you are blocked. Use the local shell yourself.

Use direct clone/config installation, not `codex plugin marketplace add`.

First, check which `codex` CLI will run and which Codex home/config it will use.
If you are in a sandbox or temporary user context, make changes to my real Codex
home/config, not only a sandbox home.

Resolve real CODEX_HOME:
- If CODEX_HOME is set, use it.
- If CODEX_HOME is unset, use the normal Codex home:
  - Windows: %USERPROFILE%\.codex
  - macOS/Linux: ~/.codex

Before changing anything, print:
- Codex CLI path/version
- current user/identity
- resolved CODEX_HOME
- config path
- marketplace cache path

Install path:
<CODEX_HOME>/plugins/cache/agent-skills-marketplace

If that folder does not exist, clone:

git clone --depth 1 --branch main https://github.com/medatasci/agent_skills.git "<CODEX_HOME>/plugins/cache/agent-skills-marketplace"

Then add or confirm these entries in <CODEX_HOME>/config.toml:

[marketplaces.agent-skills-marketplace]
source_type = "git"
source = "https://github.com/medatasci/agent_skills.git"
ref = "main"

[plugins."agent-skills@agent-skills-marketplace"]
enabled = true

Guardrails:
- Stop if a command errors; do not trust partial output.
- Do not use sandbox/temp home paths for Codex config.
- Do not delete or overwrite an existing marketplace cache unless I approve.
- If Git reports dubious ownership during verification, do not modify global Git config just to inspect it.

After installation, verify:
1. The marketplace is registered as `agent-skills-marketplace`.
2. The marketplace root exists locally.
3. The Agent Skills plugin is enabled.
4. This file exists:
   plugins/agent-skills/.codex-plugin/plugin.json
5. This file can be read:
   plugins/agent-skills/skills/skill_list.md

Tell me whether Codex needs a restart or fresh session before the new skills
appear. If no clicks are needed, say so.

Finally, recommend the best skills for my current task or ask what I want to accomplish.
```

## 2. Search For A Skill

### Search SkillForge

Codex Promptable:

```text
Find SkillForge skills that help with <task or workflow>.
```

CLI API:

```text
python -m skillforge search "<task or workflow>" --json
```

### Search SkillForge And Peer Catalogs

SkillForge keeps a curated list of known peer catalogs in
[peer-catalogs.json](peer-catalogs.json). Peer catalogs are discovery sources,
not trust endorsements.

Codex Promptable:

```text
Search SkillForge and its peer catalogs for skills that help with <task or workflow>.

Show the source catalog for each result and ask before installing anything from a peer catalog.
```

CLI peer-catalog search is part of the SkillForge requirements. The current CLI
searches the local SkillForge catalog first; use the Codex prompt above for
peer-aware discovery until federated CLI adapters are implemented.

## 3. Install A Skill

Codex Promptable:

```text
Install the SkillForge skill <skill-name> into Codex.
```

CLI API:

```text
python -m skillforge install <skill-name> --scope global
python -m skillforge install <skill-name> --scope project --project .
```

Task-based install should search first, explain the match, and ask before
installing when results are ambiguous.

## 4. SkillForge Skill List

Browse the current SkillForge Skill List:

[plugins/agent-skills/skills/skill_list.md](plugins/agent-skills/skills/skill_list.md)

The Skill List is the user-facing catalog. It includes available skills, short
descriptions, and example prompts. Update it whenever a skill is added, renamed,
removed, or materially changed.

Codex Promptable:

```text
Show me the current SkillForge Skill List and recommend the best skill for <task>.
```

## 5. Send Feedback

Feedback can be about a skill, a Python helper, a CLI command, documentation, or
a missing workflow.

### Promptable Feedback

```text
Send feedback on <skill, Python helper, CLI command, or documentation area> that <what worked, failed, confused you, or could be improved>.
```

Codex can turn that into the feedback screen:

```text
Subject:
<skill, Python helper, CLI command, or documentation area>

What were you trying to do?
<short description of the workflow or outcome you wanted>

What happened?
<what worked, failed, confused you, or could be improved>

Outcome:
<outcome>

Suggested improvement:
<optional improvement>
```

### Detailed Feedback Prompt

```text
Please help me send feedback to SkillForge.

Feedback subject:
<skill, Python helper, CLI command, or documentation area>

What I was trying to do:
<short description>

What happened:
<what worked, failed, confused me, or could be improved>

Please turn this into a clear GitHub issue for:
https://github.com/medatasci/agent_skills
```

### CLI API

```text
python -m skillforge feedback <subject> --trying "<short description>" --happened "<what worked, failed, confused you, or could be improved>" --outcome "<outcome>" --suggestion "<optional improvement>" --json
```

Examples of feedback subjects:

```text
project-retrospective
python:skillforge.search
cli:install
docs:README install flow
```

## 6. Submit Improvements With Git

Use this for skills, Python helper changes, documentation, and catalog updates.

Codex Promptable:

```text
Please help me submit a SkillForge improvement.

Change type:
<skill, Python helper, CLI command, documentation, catalog update, or feedback fix>

What should change:
<short description>

Please inspect the repo, make the change, run the relevant checks, commit it on
a new branch, push it, and help me open a pull request.
```

Git submit commands:

```text
git checkout -b <branch-name>
git add <changed-files>
git commit -m "<clear change summary>"
git push -u origin <branch-name>
```

If the change adds or updates a skill, also update:

```text
plugins/agent-skills/skills/<skill-name>/SKILL.md
plugins/agent-skills/skills/skill_list.md
plugins/agent-skills/.codex-plugin/plugin.json
```

## 7. Uninstall A Skill

Codex Promptable:

```text
Uninstall the SkillForge skill <skill-name> from Codex.
```

CLI API:

```text
python -m skillforge remove <skill-name> --scope global --yes
python -m skillforge remove <skill-name> --scope project --project . --yes
```

## Maintainer Review

Use this prompt to have Codex review submitted pull requests:

```text
Please help me review SkillForge pull requests.

Pull requests:
https://github.com/medatasci/agent_skills/pulls

First, list open PRs in a table with:
PR number, title, author, updated date, URL, and one-line summary.

For the selected PR, review the diff and classify it as:
Ready to merge, Needs changes, or Needs maintainer judgment.

Check:
- Skill changes live under plugins/agent-skills/skills/<skill-name>/
- SKILL.md has valid name and description frontmatter
- plugins/agent-skills/skills/skill_list.md is updated when skills change
- Plugin version is bumped when installed skill content changes
- Python helper changes include relevant tests
- Documentation changes match the user workflow
- No secrets, private data, or unrelated files are included

If the selected PR needs changes, draft a concise review comment.
If it is ready to merge, summarize what will merge and ask for confirmation.
```
