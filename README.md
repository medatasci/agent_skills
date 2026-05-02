# Agent Skills

Reusable agent skills published as a Codex plugin marketplace.

## Easiest Install

Copy this whole prompt into Codex:

```text
Please install Marc Edgar's Agent Skills marketplace for me.

Do not ask me to open Bash, PowerShell, or a terminal unless something blocks you.
Use the local shell yourself to run:

codex plugin marketplace add https://github.com/medatasci/agent_skills.git --ref main

Then verify the marketplace was registered. If Codex needs a restart or if I need
to click anything in the plugin directory, tell me exactly what to click. After
the Agent Skills plugin is available, show me one short example of using
$project-retrospective.
```

That is the preferred path for most users because they stay inside Codex.

## Manual Install

For people who are comfortable with a terminal, run:

```powershell
codex plugin marketplace add https://github.com/medatasci/agent_skills.git --ref main
```

Then restart Codex if needed. Open the Codex plugin directory, choose the
`Medatasci Agent Skills` marketplace, and install `Agent Skills` if it is not
already installed.

## Use Project Retrospective

Once installed, copy this into Codex when you want a project log updated:

```text
Use $project-retrospective to update this project's retrospective.

Create or update a retrospective log for this project. Capture what I asked,
what you understood, what you did, the key findings, my response if available,
and what went right, wrong, or was missed. If there is no existing retrospective,
create one at retrospectives/interaction_log.md. Keep it concise, candid, and
useful for someone returning to this project later.
```

## Add Another Skill

Add the skill folder here:

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
refreshed cleanly.
