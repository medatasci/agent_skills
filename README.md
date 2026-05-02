# Agent Skills

Reusable agent skills published as a Codex plugin marketplace.

## Install in Codex

Add this repository as a plugin marketplace:

```bash
codex plugin marketplace add https://github.com/medatasci/agent_skills.git --ref main
```

Then open the Codex plugin directory, choose the `Medatasci Agent Skills`
marketplace, and install `Agent Skills`.

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
