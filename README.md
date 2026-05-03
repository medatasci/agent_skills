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
6. Create or publish a skill.
7. Submit improvements through Git.
8. Uninstall skills you no longer want.
9. Evaluate skill search, SEO, and publication readiness.

## 1. Install SkillForge

### Codex Prompt

The easiest way to get started, if your permissions allow it, is to prompt
Codex to install SkillForge from the repo. Copy the following prompt and paste
it into Codex.

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

If you prefer the command line, you can also install SkillForge directly with
Git. Choose the correct commands for your machine:

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

Most users should start with the shorter install prompt above. Use this version
when Codex is confused about where to install the marketplace, which Codex home
to use, or how to verify the setup:

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

Use this when you know the kind of work you want help with, but you do not know
which skill name to use. Codex can search the local SkillForge catalog and
explain the best matches.

Codex Promptable:

```text
Find SkillForge skills that help with <task or workflow>.
```

CLI API:

Use the CLI when you want deterministic JSON output, want to script search, or
want an agent to consume search results directly.

```text
python -m skillforge search "<task or workflow>" --json
```

### Search SkillForge And Peer Catalogs

SkillForge keeps a curated list of known peer catalogs in
[peer-catalogs.json](peer-catalogs.json). Peer catalogs are discovery sources,
not trust endorsements.

Use peer search when the local SkillForge catalog does not have what you need,
or when you want to see what trusted public skill libraries are publishing.
Review the source catalog before installing anything from a peer.

Codex Promptable:

```text
Search SkillForge and its peer catalogs for skills that help with <task or workflow>.

Show the source catalog for each result and ask before installing anything from a peer catalog.
```

Use the CLI to search configured peer catalogs and cache the results:

```text
python -m skillforge peer-search "<task or workflow>" --json
python -m skillforge peer-search "<task or workflow>" --peer <peer-catalog-id> --json
python -m skillforge peer-search "<task or workflow>" --refresh --json
```

Peer results include the source catalog. A peer catalog is a discovery source,
not an endorsement.

## 3. Install A Skill

Use this after you have found a skill you want to try. Codex should install the
skill into your Codex environment and tell you what changed.

Codex Promptable:

```text
Install the SkillForge skill <skill-name> into Codex.
```

CLI API:

Use the CLI when you already know the skill ID and where you want it installed.
Use `global` for your normal Codex environment, or `project` for one repo.

```text
python -m skillforge install <skill-name> --scope global
python -m skillforge install <skill-name> --scope project --project .
```

Install from a peer catalog after reviewing the source:

```text
python -m skillforge install <skill-name> --peer <peer-catalog-id> --scope global --yes
```

Task-based install should search first, explain the match, and ask before
installing when results are ambiguous.

Peer install does not import the skill into this repository's catalog. It uses
the peer cache and installs directly into Codex.

## 4. SkillForge Skill List

Browse the current SkillForge Skill List:

[plugins/agent-skills/skills/skill_list.md](plugins/agent-skills/skills/skill_list.md)

Browse the generated static catalog search page:

[site/index.html](site/index.html)

The Skill List is the plain Markdown catalog for Codex and GitHub readers. The
static catalog page is the richer search surface for humans. Update both through
`python -m skillforge build-catalog` whenever a skill is added, renamed,
removed, or materially changed.

Use this prompt when you want to browse what is available instead of searching
for a specific task. It is also a good starting point when you are not sure how
to describe the workflow you want.

Codex Promptable:

```text
Show me the current SkillForge Skill List and recommend the best skill for <task>.
```

## 5. Send Feedback

Feedback can be about a skill, a Python helper, a CLI command, documentation, or
a missing workflow.

### Promptable Feedback

Use this quick prompt when something helped, failed, confused you, or sparked an
idea. Plain language is enough; Codex can turn it into a useful GitHub issue.

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

Use the detailed prompt when you already know what you were trying to do and
what happened. The extra context makes it easier for a maintainer or agent to
reproduce the issue and improve the workflow.

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

Use the CLI when you want to generate a structured feedback draft from a script,
agent workflow, or reproducible bug report.

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

## 6. Create Or Publish A Skill

Use this when you want to turn a repeated workflow into a reusable SkillForge
skill. A publishable skill has two source files before generated catalog files:

- `skills/<skill-name>/SKILL.md`: the agent-facing behavior contract.
- `skills/<skill-name>/README.md`: the human-facing home page.

The README should explain what the skill is for, who should use it, examples,
related skills, collection context, inputs, outputs, risk, permissions, limits,
feedback, and natural search terms. It is part of discovery, not decoration.
Use `skillforge/templates/skill/README.md.tmpl` as the starting point.

Codex Promptable:

```text
Create a SkillForge skill named <skill-name> for <workflow>.

Put the agent instructions and metadata in:
skills/<skill-name>/SKILL.md

Put the human-facing skill home page in:
skills/<skill-name>/README.md

Use skill-discovery-evaluation to improve discovery, examples, related skills,
and search terms. Then run:
python -m skillforge build-catalog
python -m skillforge evaluate <skill-name> --json

Show me the evaluation report and any remaining publication gaps.
```

CLI API:

Start with `create` when you want SkillForge to scaffold the required source
files and leave clear placeholders for the parts you still need to fill in.

```text
python -m skillforge create <skill-name> --title "<display title>" --description "<what it helps with>" --owner "<owner>" --category "<category>" --tag "<tag>" --risk-level low
python -m skillforge validate skills/<skill-name> --json
python -m skillforge build-catalog
python -m skillforge evaluate <skill-name> --json
```

`create` does not publish, install, or import anything from a peer catalog. It
creates `skills/<skill-name>/SKILL.md` and `skills/<skill-name>/README.md`; then
you edit those files, rebuild the catalog, and evaluate the result.

## 7. Submit Improvements With Git

Use this for skills, Python helper changes, documentation, and catalog updates.
This prompt is for contributors who want Codex to make the change, run checks,
and prepare a pull request instead of just writing an issue.

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

Use these commands when you want to submit the change yourself after Codex or a
human has made edits locally.

```text
git checkout -b <branch-name>
git add <changed-files>
git commit -m "<clear change summary>"
git push -u origin <branch-name>
```

If the change adds or updates a skill, keep the skill source in `skills/` and
let the SkillForge CLI regenerate catalog and website files:

```text
skills/<skill-name>/SKILL.md
skills/<skill-name>/README.md
catalog/skills/<skill-name>.json
catalog/skills.json
catalog/search-index.json
site/
plugins/agent-skills/skills/skill_list.md
```

To turn a peer skill into a SkillForge catalog contribution, import it
explicitly:

```text
python -m skillforge import-peer <skill-name> --peer <peer-catalog-id> --owner "<owner>"
```

Importing is different from installing. Importing modifies this repository;
installing from a peer cache does not.

## 8. Uninstall A Skill

Use this when you no longer want a skill installed, or when you want to remove
an old copy before installing a cleaner version. Removing a skill from Codex does
not delete it from the SkillForge catalog.

Codex Promptable:

```text
Uninstall the SkillForge skill <skill-name> from Codex.
```

CLI API:

Use the CLI when you know exactly which installed skill should be removed.
`--yes` is required so removals are explicit.

```text
python -m skillforge remove <skill-name> --scope global --yes
python -m skillforge remove <skill-name> --scope project --project . --yes
```

## Cache Management

Peer search and peer install use a deterministic cache under `.skillforge/cache`.

```text
python -m skillforge cache list --json
python -m skillforge cache refresh --peer <peer-catalog-id> --json
python -m skillforge cache clear --peer <peer-catalog-id> --yes
python -m skillforge peer-diagnostics --json
```

Cached peer search results can be reused when the network is unavailable. Use
`--refresh` on `peer-search` when you want fresh peer results.

Use `peer-diagnostics` when you want to inspect peer catalog metadata, duplicate
IDs, adapter type, cache freshness, and missing provenance before relying on
federated discovery.

## Search And SEO Readiness

Use this when a skill is hard to find, has vague metadata, or needs better
human and agent discovery. The audit reports missing aliases, trigger phrases,
examples, inputs, outputs, safety guidance, and generated catalog files.

Codex Promptable:

```text
Use $skill-discovery-evaluation to evaluate <skill-name> for publication.

Improve its search and SEO metadata if needed, rebuild the catalog, run the
SkillForge evaluation, and show me any remaining gaps.
```

CLI API:

```text
python -m skillforge evaluate <skill-name> --json
python -m skillforge search-audit <skill-name> --json
```

Use `evaluate` before publishing a skill. It wraps structural validation,
catalog freshness, search index readiness, static page checks, the search audit,
and sample search queries. Use `search-audit` when you only want the lower-level
metadata discovery check.

## Maintainer Review

Use this prompt when you are maintaining the marketplace and want help reviewing
incoming pull requests. Codex should focus on whether the contribution is useful,
safe to merge, and consistent with the SkillForge workflow.

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
