# Agent Skills

Reusable agent skills published as a Codex plugin marketplace. Install this
marketplace once, then use the skills in this repository as they are added and
updated over time.

The first published skill is `project-retrospective`; more skills will be added
to the same `Agent Skills` plugin.

## Easiest Install

For most users, the easiest path is to ask Codex to install the marketplace.
Copy this whole prompt into Codex:

```text
Please install Marc Edgar's Agent Skills marketplace for me.

Do not ask me to open Bash, PowerShell, or a terminal unless something blocks you.
Use the local shell yourself to run:

codex plugin marketplace add https://github.com/medatasci/agent_skills.git --ref main

Then verify the marketplace was registered. If Codex needs a restart or if I need
to click anything in the plugin directory, tell me exactly what to click. After
the Agent Skills plugin is available, list the installed skills and show one
short example using any newly available skill.
```

That is the preferred path because users stay inside Codex instead of needing to
know which Windows shell to open.

## Manual Install

For people who are comfortable with a terminal, run:

```powershell
codex plugin marketplace add https://github.com/medatasci/agent_skills.git --ref main
```

Then restart Codex if needed. Open the Codex plugin directory, choose the
`Medatasci Agent Skills` marketplace, and install `Agent Skills` if it is not
already installed.

## Available Skills

### `project-retrospective`

Create or update a durable project retrospective log. The skill records what the
user asked, what Codex understood, what Codex did, key findings, the user's
response when available, and what went right, wrong, or was missed.

Once installed, copy this into Codex when you want a project log updated:

```text
Use $project-retrospective to update this project's retrospective.

Create or update a retrospective log for this project. Capture what I asked,
what you understood, what you did, the key findings, my response if available,
and what went right, wrong, or was missed. If there is no existing retrospective,
create one at retrospectives/interaction_log.md. Keep it concise, candid, and
useful for someone returning to this project later.
```

## Updating Skills

After the marketplace is installed, users can ask Codex to refresh it:

```text
Please update Marc Edgar's Agent Skills marketplace and tell me which skills are available now.
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
refreshed cleanly. Then update the `Available Skills` section above with the
new skill name and a short user-facing description.
