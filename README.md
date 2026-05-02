# Marc's Agent Skills

Welcome. This repository is the public home for Marc Edgar's reusable Codex
skills.

Install this marketplace once in Codex, then you can use Marc's current skills
and refresh the marketplace later as new skills are published.

If Marc sent you this link, start here: copy the prompt below into Codex. Codex
should do the setup work for you.

## Install Marc's Skills

Copy this whole prompt into Codex:

```text
Please install Marc Edgar's Agent Skills marketplace for me.

Do not ask me to open Bash, PowerShell, or a terminal unless something blocks you.
Use the local shell yourself to run:

codex plugin marketplace add https://github.com/medatasci/agent_skills.git --ref main

Then verify the marketplace was registered. If Codex needs a restart or if I need
to click anything in the plugin directory, tell me exactly what to click. After
the Agent Skills plugin is available, list Marc's installed skills and show one
short example using any newly available skill.
```

This path keeps you inside Codex instead of requiring you to know which Windows
shell to open.

## What You Get Today

### `project-retrospective`

Create or update a durable project retrospective log. The skill records what you
asked, what Codex understood, what Codex did, key findings, your response when
available, and what went right, wrong, or was missed.

After installation, copy this into Codex when you want a project log updated:

```text
Use $project-retrospective to update this project's retrospective.

Create or update a retrospective log for this project. Capture what I asked,
what you understood, what you did, the key findings, my response if available,
and what went right, wrong, or was missed. If there is no existing retrospective,
create one at retrospectives/interaction_log.md. Keep it concise, candid, and
useful for someone returning to this project later.
```

## Get New Skills Later

When Marc adds new skills to this marketplace, you can ask Codex to refresh your
local copy:

```text
Please update Marc Edgar's Agent Skills marketplace and tell me which skills are available now.
```

## Manual Install

If you prefer using a terminal yourself, run:

```powershell
codex plugin marketplace add https://github.com/medatasci/agent_skills.git --ref main
```

Then restart Codex if needed. Open the Codex plugin directory, choose the
`Medatasci Agent Skills` marketplace, and install `Agent Skills` if it is not
already installed.

## For Maintainers

Add each new skill folder here:

```text
plugins/agent-skills/skills/<skill-name>/SKILL.md
```

If the skill has resources, keep them inside the skill folder:

```text
plugins/agent-skills/skills/<skill-name>/
  SKILL.md
  agents/openai.yaml
  references/
  scripts/
  assets/
```

After adding or changing skills, bump the version in
`plugins/agent-skills/.codex-plugin/plugin.json` so installed copies can be
refreshed cleanly. Then update `What You Get Today` with the new skill name and
a short description written for someone deciding whether to use it.
