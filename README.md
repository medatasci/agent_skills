# SkillForge Agent Skills Marketplace

Reusable Codex workflows for people who do not want to reinvent the wheel.

SkillForge is a growing collection of practical Codex skills for accessing
information, analyzing work, preserving context, and turning useful prompts into
repeatable business workflows.

SkillForge is a GitHub-backed marketplace and catalog for turning useful agent
workflows into reusable, discoverable, version-controlled skills. The goal is
simple: preserve workflows that would otherwise get lost in chat history, make
them findable by humans and agents, and make them easy to install, improve, and
share.

## The Idea Is Simple

- **Find a useful workflow.** Search the SkillForge Skill List, local catalog,
  and peer catalogs by task, topic, or name, not just exact skill title.
- **Use it with a prompt or CLI.** Install, inspect, refresh, and remove skills
  in Codex without needing Git, Bash, PowerShell, or local Codex internals.
- **Improve it together.** If a skill helps, breaks, or inspires a better one,
  send feedback so the workflow can get clearer, safer, or more useful.
- **Share what works.** Package a repeated workflow as a reusable `SKILL.md`
  contribution with source, docs, metadata, and version history.
- **Keep skills discoverable.** Maintain skill home pages, catalog entries,
  search terms, SEO text, peer metadata, and generated indexes from one repo.

SkillForge is not meant to be just a prompt dump. It is a lightweight skill
supply chain for source files, skill home pages, metadata, catalog search,
install commands, peer catalogs, feedback, and future evaluation and trust
scoring. Humans get readable skill pages; agents get structured metadata.

## Use SkillForge

SkillForge is designed to work two ways:

- **Codex Promptable:** ask Codex in plain language.
- **CLI API:** run the deterministic Python command directly.

For product strategy and architecture context, see
`requirements.md`, `skills/skillforge/SKILL.md`,
`docs/skill-search-seo-plan.md`, `docs/skillforge-whitepaper.md`,
`docs/codebase-to-agentic-skills.md`, and
`docs/radiological-report-to-roi.md`.

## Active Design Projects

- **Codebase-To-Agentic-Skills:** turn useful algorithm repositories
  into reviewable Codex skill packages with `SKILL.md`, adapters, safety notes,
  smoke tests, and catalog metadata. See
  `docs/codebase-to-agentic-skills.md`.
- **Radiological Report to ROI:** first exemplar workflow using
  a radiology report, matching MRI volume, and NV-Segment-CTMR segmentation to
  produce evidence-grounded ROI outputs. It now includes an agent-callable
  Python CLI for local ROI extraction from image and segmentation files. See
  `docs/radiological-report-to-roi.md`.
- **Strategic Improvement Loop:** recurring, reviewable Codex automation that
  improves SkillForge itself, especially healthcare-domain
  `codebase-to-agentic-skills` work. It chooses one focus, writes a run log,
  avoids concurrent-run collisions, and keeps changes reviewable. See
  `docs/improvement-loop/README.md`.

## Workflow

1. Install SkillForge.
2. Get help, next steps, update guidance, and output-style control.
3. Search for a skill in SkillForge and known peer catalogs.
4. Install the skill into Codex.
5. Browse the SkillForge Skill List.
6. Send feedback on a skill, Python helper, CLI command, or documentation.
7. Create or publish a skill, including codebase-to-agentic-skills workflows.
8. Submit improvements as pull requests.
9. Uninstall skills you no longer want.
10. Manage peer caches and diagnostics.
11. Evaluate skill search, SEO, and publication readiness.
12. Review incoming marketplace changes.
13. Run a strategic improvement loop for SkillForge and healthcare repo-to-skills work.

## 1. Install SkillForge

### Install SkillForge With A Prompt Inside Codex

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

What this example shows: SkillForge is installed as a Git-backed Codex
marketplace, not as loose copied prompt text. The prompt asks Codex to verify the
real Codex home, plugin registration, and readable skill list because sandbox or
temporary Codex paths are easy to confuse with the user's actual environment.

### If SkillForge May Already Be Installed

Installing SkillForge should be idempotent. If the marketplace is already on the
machine, Codex should verify it, repair only safe missing config entries, and
avoid recloning or overwriting anything.

Codex Promptable:

```text
Install SkillForge for my real Codex environment.

If SkillForge is already installed, do not reclone it and do not overwrite it.
Verify the existing install, show the Codex home, marketplace path, repo URL,
branch, commit, plugin status, and whether local changes exist when Git metadata
is available. Include the source repository, configured ref, plugin/code
version, and last updated date/time.

If only safe Codex config entries are missing, ask before repairing them.
If the target folder exists but is not SkillForge, stop and ask me.
```

CLI API, from an existing SkillForge checkout:

```text
python -m skillforge install-skillforge --json
python -m skillforge install-skillforge --yes
```

What this example shows: "install SkillForge" means "make sure SkillForge is
installed and usable." A healthy existing install should produce a status report
and next commands, not an error about an existing folder.

### Install SkillForge Manually With Git

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

Then either let SkillForge add the safe missing config entries:

```text
cd <marketplace-path>
python -m skillforge install-skillforge --yes
```

Or add or confirm these entries in `<CODEX_HOME>/config.toml`:

```toml
[marketplaces.agent-skills-marketplace]
source_type = "git"
source = "https://github.com/medatasci/agent_skills.git"
ref = "main"

[plugins."agent-skills@agent-skills-marketplace"]
enabled = true
```

Restart Codex if needed.

What this example shows: the install path is intentionally under the Codex
plugin marketplace cache so the repo can act as a refreshable marketplace. The
same repository also contains the Python CLI, generated catalog files, static
site, and source skills.

### Use A Safer Install Prompt When Codex Paths Are Ambiguous

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

What this example shows: the advanced prompt is a safety and diagnosability
prompt. It makes Codex prove where it is about to write, avoids
`codex plugin marketplace add` when that command is not the right interface, and
guards against partial installs.

## 2. Get Help, Updates, And Output Style

SkillForge should feel easy to approach even when you do not know the right
command or skill name yet. You can ask Codex in plain language, or use the
SkillForge help commands directly when you want deterministic output that a
human or calling LLM can parse.

### Welcome A New User

Use this when someone is brand new to SkillForge and should not be expected to
know what a skill, catalog, peer catalog, CLI, or Codex install path is.

Codex Promptable:

```text
Welcome me to SkillForge.
Assume I am a first-time user.
Show me what I can ask for and do not install anything yet.
```

CLI API:

```text
python -m skillforge welcome
python -m skillforge welcome --json
```

What this example shows: the welcome message is intentionally hardcoded so new
users get a stable, low-assumption introduction before any LLM improvises.
It includes first-step prompts for finding skills, creating skills, analyzing a
Git repo or codebase to create agentic skills, sharing skills, checking
installed skills, asking for help, reviewing safety, and updating SkillForge.

### After Installing SkillForge

Use this prompt immediately after installation when you want Codex to orient you
instead of leaving you at a terminal prompt:

```text
Help me use SkillForge.

Show me how to search for a skill, inspect a result, install a skill, list what
is installed, send feedback, and get help when I am unsure what to do next.
Keep it practical and do not install anything unless I ask.
```

Good first CLI checks:

```text
python -m skillforge doctor --json
python -m skillforge welcome
python -m skillforge getting-started
python -m skillforge help search
python -m skillforge corpus-search "write an email"
python -m skillforge list --scope global
python -m skillforge update-check --json
```

What this example shows: getting started should be a workflow, not a memory
test. The user should be able to ask for guidance, see the next useful command,
and avoid accidental installs.

### Ask SkillForge For Help

Promptable flow:

```text
SkillForge, help me figure out what to do next.
I want to find a low-risk skill for <task>, understand the options, and avoid installing anything risky.
```

CLI API:

```text
python -m skillforge help
python -m skillforge help search
python -m skillforge help "I need a skill for writing status emails"
python -m skillforge help --json
python -m skillforge welcome
python -m skillforge getting-started
```

What this example shows: help is a product surface, not only argparse output.
The JSON form returns topics, commands, examples, side effects, related
commands, and safer next steps without executing anything.

### Check For SkillForge Updates

SkillForge should periodically check whether the upstream GitHub repo has new
changes, then tell you what changed. The periodic check is cache-based: by
default, SkillForge reuses update status for a few hours instead of forcing a
network fetch every time. Updating is explicit and conservative; SkillForge only
applies a clean fast-forward update after confirmation.

Promptable flow:

```text
Check whether SkillForge has updates.
If updates are available, show me what changed. Do not update files unless I ask.
```

Update SkillForge:

```text
Update SkillForge.
Check for upstream changes, apply only a safe fast-forward update, and then show me what changed.
```

CLI API:

```text
python -m skillforge update-check --json
python -m skillforge update-check --no-fetch --json
python -m skillforge update
python -m skillforge update --yes
python -m skillforge update --yes --json
python -m skillforge whats-new
python -m skillforge whats-new --details
python -m skillforge whats-new --commits
python -m skillforge whats-new --since HEAD~3
python -m skillforge whats-new --json
```

What this example shows: update checks are safe to ask for frequently because
they are cached for a short window. `update-check` compares the local checkout
with the configured upstream branch and does not change files. `update` without
`--yes` shows status and the next command. `update --yes` refuses dirty or
diverged checkouts and only performs a Git fast-forward. `whats-new` defaults
to a user-facing feature summary and asks whether you want more detail. Use
`--details`, `--technical`, or `--commits` when you want the Git-level evidence.

### Control SkillForge Chattiness

Different users and agents want different levels of explanation. SkillForge
supports a scale from coaching to silent output on the first commands that need
it most: `welcome`, `help`, `getting-started`, `search`, and `corpus-search`.

CLI API:

```text
python -m skillforge welcome --chattiness coach
python -m skillforge help search --chattiness coach
python -m skillforge getting-started --chattiness terse
python -m skillforge search "SQL database access" --chattiness terse
python -m skillforge corpus-search "write an email" --chattiness silent
```

Environment default:

```text
SKILLFORGE_CHATTINESS=coach
```

Recommended modes:

- `coach`: explain what happened, why it matters, and useful next steps.
- `normal`: concise output with practical next steps.
- `terse`: minimal human output.
- `silent`: no extra prose beyond requested output, warnings, errors, and JSON.

Important: `--json` output should stay stable no matter how chatty the human
output is. Dangerous or ambiguous actions should still warn or require
confirmation, even in silent mode.

## 3. Search For A Skill

### Search SkillForge And Peer Catalogs For A Task

Use this as the default discovery flow when you are trying to find a skill by
task, outcome, or fuzzy human intent. SkillForge searches the local catalog and
known peer catalogs, then returns a table designed for humans and agents to take
the next step: rank, skill name, what it helps with, comments extracted from
`SKILL.md`, install command, and source URL.

Codex Promptable:

```text
Search for skills that will help me write an email.
Use the semantic-ready SkillForge corpus search so I can compare local and peer skills.
Ask before installing anything from a peer catalog.
```

CLI API:

```text
python -m skillforge corpus-search "write an email"
python -m skillforge corpus-search "write an email" --json
```

What this example shows: SkillForge search is not only exact-name lookup. The
recommended path searches normalized provider catalog snapshots that include
available `SKILL.md`, README text, aliases, tasks, examples, tags, and
descriptions. It is the semantic-search foundation because the result carries
enough text and provenance for an agent to reason about fit before asking to
install.

### Search Only The Local SkillForge Catalog

Use this when you only want skills already curated into this SkillForge
repository and do not want federated peer results. It is fast, deterministic,
and useful for CI, local testing, and known-safe marketplace browsing.

Codex Promptable:

```text
Search only the local SkillForge catalog for skills that help with YouTube transcripts.
Do not search peer catalogs.
```

CLI API:

Use the CLI when you want deterministic JSON output, want to script search, or
want an agent to consume search results directly.

```text
python -m skillforge search "YouTube transcripts" --json
```

What this example shows: local `search` is deliberately narrower than
`corpus-search`. It searches the generated SkillForge catalog, including
discovery fields and README-derived text, so source `SKILL.md` and `README.md`
quality directly affects whether a curated local skill can be found.

### Refresh Peer Catalogs When You Need Live Results

SkillForge keeps a curated list of known peer catalogs in
[peer-catalogs.json](peer-catalogs.json). Peer catalogs are discovery sources,
not trust endorsements.

Use live peer search when the local provider cache may be stale, when you want
to force a fresh query against configured peer sources, or when you want to test
one peer catalog directly.

Codex Promptable:

```text
Refresh peer catalogs and search for skills that help with SQL database access.
Ask before installing anything from a peer catalog.
```

Use the CLI to refresh or narrow configured peer catalogs:

```text
python -m skillforge peer-search "SQL database access" --json
python -m skillforge peer-search "SQL database access" --peer github-awesome-copilot --json
python -m skillforge peer-search "SQL database access" --refresh --json
python -m skillforge peer-search "SQL database access" --jobs 5 --json
```

Search has three layers:

- `search` is fast local marketplace search over SkillForge-generated metadata.
- `corpus-search` is the best default for semantic-ready discovery across peer catalogs. It
  searches cached full provider snapshots, including available `SKILL.md` text,
  README text, aliases, tasks, examples, tags, and descriptions. It is not yet
  vector embedding search or LLM reranking, but it is the semantic-search
  foundation because it gives an agent the full normalized corpus to reason
  over.
- `peer-search --refresh` is for fresh live queries against configured peer
  sources when the cached provider snapshots may be stale.

The default `corpus-search` output is a Markdown table with rank, skill name,
what the skill helps with, comments extracted from the skill's `SKILL.md`, CLI
install command when one is available, and the source URL for manual review or
install. This makes the search result immediately actionable for both a human
and an agent.

Example task search:

```text
python -m skillforge corpus-search "help me draft an Outlook email"
python -m skillforge corpus-search "time management pomodoro timer"
python -m skillforge corpus-search "SQL database access" --json
```

What this example shows: `corpus-search` is the semantic-ready path. It searches
over normalized provider catalog dumps rather than only exact catalog names, and
the default table includes the install command, source URL, and comments pulled
from each result's `SKILL.md`. That lets a human or agent decide what to install
without opening every repository first. Today the ranking is deterministic
full-text/corpus scoring; future vector search or LLM reranking can use the same
cached corpus.

Peer results include the source catalog. A peer catalog is a discovery source,
not an endorsement. By default, peer search checks every enabled peer catalog in
parallel with up to 15 workers and reports each peer as matched, no_match,
error, or disabled.

Interesting detail: peer search is federated but deliberately loose. SkillForge
keeps a curated peer list, queries up to 15 peers in parallel, caches results,
and still requires source review before peer install.

## 4. Install A Skill

Use this after you have found a skill you want to try. Codex should install the
skill into your Codex environment and tell you what changed.

Codex Promptable:

```text
Install the SkillForge project-retrospective skill into Codex.
```

CLI API:

Use the CLI when you already know the skill ID and where you want it installed.
Use `global` for your normal Codex environment, or `project` for one repo.

```text
python -m skillforge install project-retrospective --scope global
python -m skillforge install project-retrospective --scope project --project .
```

Install from a peer catalog after reviewing the source:

```text
python -m skillforge install email-drafter --peer github-awesome-copilot --scope global --yes
```

Task-based install should search first, explain the match, and ask before
installing when results are ambiguous.

Peer install does not import the skill into this repository's catalog. It uses
the peer cache and installs directly into Codex.

What this example shows: installing and publishing are separate operations.
`install` changes your Codex skills directory; it does not curate, vendor, or
publish a skill in this repository. Peer installs require `--yes` so the user or
agent has an explicit source-review checkpoint.

Inspect a skill before installing when you want provenance, files, checksum,
permissions, or generated metadata:

```text
python -m skillforge info project-retrospective --json
```

Interesting detail: `info` exposes provenance, checksums, files, generated
install commands, source catalog metadata, warnings, permissions, and discovery
fields. It is the low-friction way for an agent to inspect a skill before taking
action.

Download a local catalog skill source for review or editing without installing
it into Codex:

```text
python -m skillforge download project-retrospective --destination ./downloaded-skills --json
```

Interesting detail: `download` is intentionally not install. It is for source
review, editing, comparison, or packaging work where you want the files but do
not want to activate the skill in Codex.

## 5. SkillForge Skill List

Browse the current SkillForge Skill List:

[plugins/agent-skills/skills/skill_list.md](plugins/agent-skills/skills/skill_list.md)

Browse the generated static catalog search page at the published relative path:

```text
./site/
```

Avoid direct links to generated HTML files in published docs. Local README
renderers can turn them into machine-specific filesystem URLs instead of usable
published marketplace URLs.

The Skill List is the plain Markdown catalog for Codex and GitHub readers. The
static catalog page is the richer search surface for humans. Update both through
`python -m skillforge build-catalog` whenever a skill is added, renamed,
removed, or materially changed.

Use this prompt when you want to browse what is available instead of searching
for a specific task. It is also a good starting point when you are not sure how
to describe the workflow you want.

Codex Promptable:

```text
Show me the current SkillForge Skill List and recommend the best skill for inspecting Hugging Face datasets.
```

What this example shows: the Skill List is a generated, human-readable Markdown
surface for Codex and GitHub readers. It should agree with the generated catalog
JSON and static site because all of them are rebuilt from the same source
skills.

CLI API:

Use `list` to see what is installed in Codex, not merely what exists in the
SkillForge catalog:

```text
python -m skillforge list --scope global
python -m skillforge list --scope project --project . --json
```

Interesting detail: `list` answers a different question than `search`. `search`
shows what exists in the marketplace; `list` shows what is actually installed in
the active global or project Codex skill directory.

## 6. Send Feedback

Feedback can be about a skill, a Python helper, a CLI command, documentation, or
a missing workflow.

Use feedback when you want to report, request, or describe something. Use
**Submit Improvements As Pull Requests** when you have a concrete fix, feature,
documentation update, catalog update, or new skill to contribute.

### Send Feedback With A Short Prompt

Use this quick prompt when something helped, failed, confused you, or sparked an
idea. Plain language is enough; Codex can turn it into a useful GitHub issue.

```text
Send feedback on skill search that Pomodoro timer results were weak and it was hard to tell there was no dedicated timer skill.
```

What this example shows: feedback is treated as a product workflow, not an
afterthought. A user can describe the problem casually and let Codex turn it into
a structured GitHub issue.

Codex can turn that into the feedback screen:

```text
Subject:
skill search

What were you trying to do?
Find a skill for Pomodoro-style focus sessions and time management.

What happened?
The search found general planning skills, but not a dedicated Pomodoro timer skill.

Outcome:
I could use a time-management list, but not a timed focus workflow.

Suggested improvement:
Add a pomodoro-focus-timer skill or make the absence of a dedicated timer skill clearer.
```

### Send Detailed Feedback For A Reproducible Issue

Use the detailed prompt when you already know what you were trying to do and
what happened. The extra context makes it easier for a maintainer or agent to
reproduce the issue and improve the workflow.

```text
Please help me send feedback to SkillForge.

Feedback subject:
skill search

What I was trying to do:
Find a skill for Pomodoro-style focus sessions and time management.

What happened:
The search found general planning skills, but not a dedicated Pomodoro timer skill.

Please turn this into a clear GitHub issue for:
https://github.com/medatasci/agent_skills
```

### Draft Feedback From The CLI

Use the CLI when you want to generate a structured feedback draft from a script,
agent workflow, or reproducible bug report.

```text
python -m skillforge feedback "skill search" --trying "find a Pomodoro timer skill" --happened "results were weak and no dedicated timer skill appeared" --outcome "I found general planning skills, but not a timed focus workflow" --suggestion "add a pomodoro-focus-timer skill or clarify when no dedicated skill exists" --json
```

Interesting detail: the feedback CLI produces a structured draft that can be
used by humans, agents, or scripts. It keeps subjective reports reproducible by
separating intent, observed behavior, outcome, and suggested improvement.

Examples of feedback subjects:

```text
project-retrospective
python:skillforge.search
cli:install
docs:README install flow
```

## 7. Create Or Publish A Skill

Use this when you want to turn a repeated workflow into a reusable SkillForge
skill. A publishable skill has two source files before generated catalog files:

- `skills/<skill-name>/SKILL.md`: the agent-facing behavior contract.
- `skills/<skill-name>/README.md`: the human-facing home page.

The README should explain what the skill is for, who should use it, examples,
related skills, collection context, inputs, outputs, risk, permissions, limits,
feedback, and natural search terms. It is part of discovery, not decoration.
Use `skillforge/templates/skill/README.md.tmpl` as the starting point.

### Turn A Codebase Into Agentic Skills

Use this when the starting point is a repository, model package, algorithm, or
research codebase instead of an already-written skill. SkillForge should first
build a source-context map and candidate skill table, then ask you what to
package.

Codex Promptable:

```text
SkillForge, analyze Git repo or codebase and help me create a set of agentic skills from it:
<repo-url-or-local-path>

Workflow goal:
<what users should be able to do>

Start with a source-context map, candidate skill table, and readiness-card
drafts. Do not run the source code, install dependencies, download assets, or
generate publishable skill files until I review the candidates.
```

CLI API:

```text
python -m skillforge codebase-scan <repo-path> --workflow-goal "<what users should be able to do>" --json
python -m skillforge codebase-scan <repo-path> --workflow-goal "<what users should be able to do>" --output-dir docs/reports/<repo>-repo-to-skills --json
python -m skillforge codebase-scaffold-adapter setup-plan --adapter-name <adapter-name> --output-dir skills/<skill-id> --json
```

What this example shows: repo-to-skills work starts with evidence, not a blind
wrapper. The scanner identifies likely source artifacts and drafts review files.
The adapter scaffold command can create a review-only Python skeleton with
`schema`, `check`, and `setup-plan`, but it still does not run source code,
install dependencies, download assets, or create a runnable `run` command.

Codex Promptable:

```text
Create a SkillForge skill named pomodoro-focus-timer for guided Pomodoro-style focus sessions.

Put the agent instructions and metadata in:
skills/pomodoro-focus-timer/SKILL.md

Put the human-facing skill home page in:
skills/pomodoro-focus-timer/README.md

Use skill-discovery-evaluation to improve discovery, examples, related skills,
and search terms. Then run:
python -m skillforge build-catalog
python -m skillforge evaluate pomodoro-focus-timer --json

Show me the evaluation report and any remaining publication gaps.
```

CLI API:

Start with `create` when you want SkillForge to scaffold the required source
files and leave clear placeholders for the parts you still need to fill in.

```text
python -m skillforge create pomodoro-focus-timer --title "Pomodoro Focus Timer" --description "Guide timed focus sessions and breaks." --owner "medatasci" --category "Productivity" --tag "pomodoro" --risk-level low
python -m skillforge validate skills/pomodoro-focus-timer --json
python -m skillforge build-catalog
python -m skillforge evaluate pomodoro-focus-timer --json
```

`create` does not publish, install, or import anything from a peer catalog. It
creates `skills/<skill-name>/SKILL.md` and `skills/<skill-name>/README.md`; then
you edit those files, rebuild the catalog, and evaluate the result.

What this example shows: SkillForge treats a skill as both an agent artifact and
a human-facing product page. `SKILL.md` tells agents how to behave; `README.md`
helps humans discover, evaluate, trust, and use the skill.

Use `upload` when you already have a skill folder and want to add or update it
in this repository's local catalog:

```text
python -m skillforge upload ./external-skills/pomodoro-focus-timer --owner "medatasci" --source-url "https://github.com/medatasci/pomodoro-focus-timer" --json
python -m skillforge build-catalog --json
python -m skillforge evaluate pomodoro-focus-timer --json
```

`upload` copies an existing skill folder into `skills/<skill-name>/`. `create`
starts a new folder from templates. `import-peer` pulls a skill from a configured
peer catalog into this repository. `install` only installs a skill into Codex.

Interesting detail: this distinction is one of SkillForge's core safety rails.
Users can try a peer skill locally without publishing it, download a skill
without installing it, or explicitly import a peer skill when they want it to
become a reviewed SkillForge contribution.

## 8. Submit Improvements As Pull Requests

Use this for skills, Python helper changes, documentation, catalog updates, and
bug fixes when you have a concrete change to submit. If you only found a
problem, got confused, or want to request a feature, use **Send Feedback**
instead.

The normal user path is a pull request. Direct pushes to `main` are a
maintainer path, not the default way a user or agent should contribute.

SkillForge can also pay attention to the contributor's comfort level. A
developer may want the exact Git commands. A non-developer may want Codex to
handle the branch, checks, commit, push, and PR mechanics step by step. Both
paths should end in a pull request.

### Submit A Pull Request With A Prompt

Ask Codex to make or package the change, run checks, and prepare a pull request
for review.

```text
Please help me submit a SkillForge improvement as a pull request.

I am not a developer, so please handle the Git and pull request mechanics step
by step. Explain before running commands that change files, create commits, or
push a branch.

Change type:
documentation

What should change:
Update the README search examples so users see semantic-ready corpus search, SKILL.md comments, source URLs, and install commands.

Please inspect the repo, make the change, run the relevant checks, create a new
branch, commit the change on that branch, and help me open a pull request.

Do not push directly to main.
```

What this example shows: SkillForge separates issue feedback from reviewed
code contributions. A user can describe the improvement in plain language while
Codex keeps the contribution on a branch and prepares it for PR review.

### Draft Pull Request Metadata From The CLI

Use `contribute` when you want a deterministic PR draft that another agent,
script, or human can inspect before any Git commands run.

```text
python -m skillforge contribute "clarify semantic search examples" --type docs --changed README.md --check "python -m unittest tests.test_skillforge" --json
```

For a non-developer contributor, include the profile so the output emphasizes a
promptable path:

```text
python -m skillforge contribute "clarify semantic search examples" --type docs --changed README.md --user-type non-developer --json
```

Interesting detail: `contribute` is read-only. It drafts the PR title, branch
name, body, compare URL, suggested commands, checks, and safety notes; it does
not run Git, push a branch, or create the PR.

### Prepare The Branch Yourself

Use these commands only after you or Codex have made the local edits and you
are ready to create a pull request.

```text
git checkout -b docs/semantic-search-examples
git add README.md
git commit -m "Docs: clarify semantic search examples"
git push -u origin docs/semantic-search-examples
```

Then open a pull request from the branch to `main`.

What this example shows: SkillForge is Git-native. Skills, generated catalogs,
static pages, and CLI changes all move through normal reviewable source control
instead of a hidden marketplace database.

If the change adds or updates a skill, keep the skill source in `skills/` and
let the SkillForge CLI regenerate catalog and website files. For example, a
`pomodoro-focus-timer` contribution would update source files and generated
surfaces like these:

```text
skills/pomodoro-focus-timer/SKILL.md
skills/pomodoro-focus-timer/README.md
catalog/skills/pomodoro-focus-timer.json
catalog/skills.json
catalog/search-index.json
site/
plugins/agent-skills/skills/skill_list.md
```

Draft the PR package after those files are ready:

```text
python -m skillforge contribute "add pomodoro focus timer skill" --type skill --changed skills/pomodoro-focus-timer --changed catalog/skills/pomodoro-focus-timer.json --check "python -m skillforge evaluate pomodoro-focus-timer --json" --json
```

For skill pull requests, reviewers should see that:

- `SKILL.md` follows the agent-facing template in `skillforge/templates/skill/SKILL.md.tmpl`.
- `README.md` follows the human-facing home page template in `skillforge/templates/skill/README.md.tmpl`.
- No `{{placeholder}}` values remain.
- `python -m skillforge build-catalog` was run after skill changes.
- `python -m skillforge evaluate <skill-id> --json` passes or clearly reports remaining advisory gaps.

To turn a peer skill into a SkillForge catalog contribution, import it
explicitly:

```text
python -m skillforge import-peer email-drafter --peer github-awesome-copilot --owner "medatasci"
```

Importing is different from installing. Importing modifies this repository;
installing from a peer cache does not.

Interesting detail: `import-peer` preserves peer provenance while moving the
skill into the SkillForge source tree for curation. It is the bridge between
loose federation and local governance.

## 9. Uninstall A Skill

Use this when you no longer want a skill installed, or when you want to remove
an old copy before installing a cleaner version. Removing a skill from Codex does
not delete it from the SkillForge catalog.

Codex Promptable:

```text
Uninstall the SkillForge project-retrospective skill from Codex.
```

CLI API:

Use the CLI when you know exactly which installed skill should be removed.
`--yes` is required so removals are explicit.

```text
python -m skillforge remove project-retrospective --scope global --yes
python -m skillforge remove project-retrospective --scope project --project . --yes
```

What this example shows: uninstalling is scoped. Removing a global install does
not remove project installs, and removing an installed copy never deletes the
source catalog entry.

## 10. Cache Management

Peer search and peer install use a deterministic cache under `.skillforge/cache`.
Provider catalog snapshots are also cached so future semantic or LLM-assisted
search can work from a full provider corpus instead of querying every provider
for every search term.

```text
python -m skillforge doctor --json
python -m skillforge cache catalogs --json
python -m skillforge cache catalogs --refresh --ttl-hours 24 --json
python -m skillforge cache list --json
python -m skillforge cache refresh --peer github-awesome-copilot --json
python -m skillforge cache clear --peer github-awesome-copilot --yes
python -m skillforge peer-diagnostics --json
```

`cache catalogs` writes one normalized JSON catalog per configured provider to
the SkillForge user cache at `catalogs/<peer-id>/catalog.json`. Static providers
also keep the raw provider response at `catalogs/<peer-id>/raw.json`. The
default expiration is 24 hours.

What this example shows: SkillForge is moving toward agent-readable federation.
Provider catalog caching creates a full local corpus that can be searched
quickly, inspected offline, and reused later by semantic search, LLM reranking,
or trust/risk evaluation.

Cached peer search results can be reused when the network is unavailable. Use
`--refresh` on `peer-search` when you want fresh peer results.

Use `doctor` when SkillForge or Codex appears to be installed in the wrong
place, when global/project skill paths are confusing, or before asking Codex to
modify your real Codex environment.

Use `peer-diagnostics` when you want to inspect peer catalog metadata, duplicate
IDs, adapter type, cache freshness, and missing provenance before relying on
federated discovery.

Interesting detail: diagnostics are part of the product because federated
catalogs fail in messy ways: stale caches, broken URLs, duplicate IDs, parser
skips, platform path issues, and missing provenance should be visible instead of
silently degrading search.

## 11. Search And SEO Readiness

Use this when a skill is hard to find, has vague metadata, or needs better
human and agent discovery. The audit reports missing aliases, trigger phrases,
examples, inputs, outputs, safety guidance, and generated catalog files.

Codex Promptable:

```text
Use $skill-discovery-evaluation to evaluate project-retrospective for publication.

Improve its search and SEO metadata if needed, rebuild the catalog, run the
SkillForge evaluation, and show me any remaining gaps.
```

CLI API:

```text
python -m skillforge evaluate project-retrospective --json
python -m skillforge search-audit project-retrospective --json
```

Use `evaluate` before publishing a skill. It wraps structural validation,
catalog freshness, search index readiness, static page checks, the search audit,
and sample search queries. Use `search-audit` when you only want the lower-level
metadata discovery check.

What this example shows: publishing is not just syntax validation. SkillForge
checks whether a skill can be found by humans and agents, whether generated
surfaces are fresh, and whether the skill's README and metadata support search
and safe use.

## 12. Maintainer Review

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

What this example shows: maintainer review is itself a reusable workflow. The
review prompt makes generated artifacts, plugin mirrors, skill metadata, tests,
and secret/private-data checks explicit so contributions can be reviewed
consistently.
