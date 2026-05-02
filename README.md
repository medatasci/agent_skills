# Marc's Agent Skills

Small, reusable Codex workflows that make good work repeatable.

This is Marc Edgar's Codex skills marketplace: a place to install, refresh, and
share practical skills that teach Codex better ways to work.

Think of it a few ways:

- A **skill shelf**: install once, then pull down the workflow you need.
- A **prompt-to-practice library**: useful prompts become reusable Codex skills,
  not one-off chat tricks.
- A **sharing channel**: if you build a skill that helps your work, Marc can
  review it and publish it here for others.

If Marc sent you this link, start here. You do not need to know Git, Bash, or
PowerShell. Open Codex and paste the prompt below.

## Start Here

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

## Skill Catalog

Available today:

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

## Share Your Skill With Marc

If you built a Codex skill and want it considered for Marc's marketplace, you
can ask Codex to prepare the contribution for you.

Copy this prompt into Codex:

```text
I built a Codex skill and want to share it with Marc's Agent Skills marketplace.

Please help me package it for this repository:
https://github.com/medatasci/agent_skills.git

Find the skill folder, inspect its SKILL.md, and prepare it as a contribution.
Put it under:

plugins/agent-skills/skills/<skill-name>/

Validate that SKILL.md has the required name and description frontmatter. Keep
any references, scripts, assets, or agents/openai.yaml files inside the skill
folder. Update the README's "Skill Catalog" section with a short description
and one example prompt. Bump the plugin version in
plugins/agent-skills/.codex-plugin/plugin.json.

When the files are ready, show me the diff and help me commit the changes. If I
have GitHub access, help me open a pull request. If I do not, help me open an
issue that includes the skill description, example prompt, and files that Marc
needs to review.
```

The contribution lifecycle is:

1. Build and test your skill locally in Codex.
2. Ask Codex to package it for Marc's marketplace using the prompt above.
3. Review the diff Codex prepares.
4. Share it with Marc by opening a pull request or issue in this repository.
5. Marc reviews, edits if needed, and merges accepted skills.
6. After merge, anyone who installed the marketplace can ask Codex to refresh it:

```text
Please update Marc Edgar's Agent Skills marketplace and tell me which skills are available now.
```

A strong contribution includes:

- A skill folder with a `SKILL.md` file.
- A clear description of when someone should use the skill.
- Any required resources inside the skill folder, such as `references/`,
  `scripts/`, `assets/`, or `agents/openai.yaml`.
- A short example prompt that shows how someone would use the skill in Codex.

Use this folder shape:

```text
plugins/agent-skills/skills/<skill-name>/
  SKILL.md
  agents/openai.yaml
  references/
  scripts/
  assets/
```

Only `SKILL.md` is required. Add the other folders only when the skill needs
them.

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
refreshed cleanly. Then update `Skill Catalog` with the new skill name and
a short description written for someone deciding whether to use it.
