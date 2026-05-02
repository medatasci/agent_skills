# SkillForge

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

- **Search for new skills.** Browse the catalog or ask Codex what is available.
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

Search finds candidate skills. Install validates the selected skill, verifies
its source metadata, and copies or symlinks it into the requested Codex scope.

### Find A Skill

Codex Promptable:

```text
Find SkillForge skills that help with project retrospectives.
```

CLI API:

```text
python -m skillforge search "project retrospectives" --json
```

### Inspect A Skill

Codex Promptable:

```text
Show me the SkillForge metadata for project-retrospective.
```

CLI API:

```text
python -m skillforge info project-retrospective --json
```

### Install A Skill

Codex Promptable:

```text
Install the SkillForge skill project-retrospective into Codex.
```

CLI API:

```text
python -m skillforge install project-retrospective --scope global
python -m skillforge install project-retrospective --scope project --project .
```

### Remove A Skill

Codex Promptable:

```text
Remove the SkillForge skill project-retrospective from my Codex skills.
```

CLI API:

```text
python -m skillforge remove project-retrospective --scope global --yes
python -m skillforge remove project-retrospective --scope project --project . --yes
```

### List Installed Skills

Codex Promptable:

```text
List my installed SkillForge skills.
```

CLI API:

```text
python -m skillforge list --scope global --json
python -m skillforge list --scope project --project . --json
```

### Check Local Setup

Codex Promptable:

```text
Check whether SkillForge can find my Codex skill install paths.
```

CLI API:

```text
python -m skillforge doctor --project . --json
```

### Validate A Skill

Codex Promptable:

```text
Validate this skill folder before I submit it to SkillForge.
```

CLI API:

```text
python -m skillforge validate <skill-folder> --json
```

### Upload A Skill To The Catalog

Upload means "ingest this local skill folder into the local SkillForge catalog
layout and regenerate metadata." It does not create a pull request by itself.

Codex Promptable:

```text
Add this local skill folder to the SkillForge catalog for owner <owner>.
```

CLI API:

```text
python -m skillforge upload <skill-folder> --owner <owner>
```

### Share A Skill

Share means "prepare a contribution for other people." It usually includes
validation, upload, review of generated files, a branch, a commit, and a pull
request.

Codex Promptable:

```text
Share my local skill folder with SkillForge.

Validate the skill, upload it into the SkillForge catalog for owner <owner>,
show me the generated files, commit the changes on a branch, and help me open a
pull request.
```

CLI API:

```text
python -m skillforge validate <skill-folder> --json
python -m skillforge upload <skill-folder> --owner <owner>
git checkout -b add-<skill-id>
git add skills catalog
git commit -m "Add <skill-id> skill"
git push -u origin add-<skill-id>
```

### Download A Skill Without Installing

Codex Promptable:

```text
Download the SkillForge skill project-retrospective without installing it.
```

CLI API:

```text
python -m skillforge download project-retrospective --destination downloads
```

### Rebuild The Catalog

Codex Promptable:

```text
Rebuild the SkillForge catalog indexes.
```

CLI API:

```text
python -m skillforge build-catalog
```

## Example Skills

### `get-youtube-media`

Search YouTube for learning or research topics, collect captions and
transcripts, save restartable retrieval queues, and optionally download media
that the user is authorized to save.

Use it when you want to turn videos or YouTube search results into reusable
local transcript artifacts.

```text
Find and install the SkillForge skill for YouTube transcripts and research queues.
```

CLI API:

```text
python -m skillforge search "YouTube transcripts research queues" --json
python -m skillforge info get-youtube-media --json
python -m skillforge install get-youtube-media --scope global
```

### `project-retrospective`

Create or update a durable project retrospective log. The skill records what you
asked, what Codex understood, what Codex did, key findings, your response when
available, and what went right, wrong, or was missed.

Use it when you want a project to remember more than the final code diff.

```text
Find and install the SkillForge skill for project retrospectives.
```

CLI API:

```text
python -m skillforge search "project retrospectives" --json
python -m skillforge info project-retrospective --json
python -m skillforge install project-retrospective --scope global
```

## Peer Catalogs

SkillForge can search known peer catalogs listed in
[peer-catalogs.json](peer-catalogs.json). Peer catalogs are discovery sources,
not trust endorsements.

The current peer list includes high-signal sources such as OpenAI, Anthropic,
GitHub, Vercel, Microsoft, Sentry, Trail of Bits, Addy Osmani, Supabase,
Cloudflare, WordPress, Hugging Face, and the Agent Skills specification project.

## Send Feedback On A Skill

Feedback is part of the product. If a skill helped, failed, confused you, or
gave you an idea for a better workflow, open an issue in this repo.

Codex Promptable:

```text
Send feedback on skill <skill-name> that <what worked, failed, confused you, or could be improved>.
```

Codex can turn a short note into the existing feedback screen:

```text
Skill:
<skill-name>

What were you trying to do?
<short description of the workflow or outcome you wanted>

What happened?
<what worked, failed, confused you, or could be improved>

Outcome:
<outcome>

Suggested improvement:
<optional improvement>
```

CLI API:

```text
python -m skillforge feedback <skill-name> --trying "<short description>" --happened "<what worked, failed, confused you, or could be improved>" --outcome "<outcome>" --suggestion "<optional improvement>" --json
```

You can also ask Codex to prepare longer feedback:

```text
Please help me send feedback to SkillForge.

I used this skill:
<skill-name>

What I was trying to do:
<short description>

What happened:
<what worked, failed, confused me, or could be improved>

Please turn this into a clear GitHub issue for:
https://github.com/medatasci/agent_skills
```

## Contribution Notes

Uploading and sharing are related, but not the same:

- **Upload a skill** updates the local SkillForge catalog files.
- **Share a skill** prepares and submits those changes for others, usually by
  opening a pull request.

A strong contribution includes:

- A skill folder with a `SKILL.md` file.
- A clear description of what the skill does and when someone should use it.
- Any required resources inside the skill folder, such as `references/`,
  `scripts/`, `assets/`, or `agents/openai.yaml`.
- A short example prompt that shows how someone would use the skill in Codex.

MVP contribution flow:

```text
python -m skillforge validate <skill-folder>
python -m skillforge upload <skill-folder> --owner <owner>
```

Then open a pull request with the skill and generated catalog updates.

## Project Docs

- [Requirements](requirements.md)
- [Software development TODO](software-dev-todo.md)
- [Planning/archive TODO](skillforge-planning-todo.md)
- [Peer catalogs](peer-catalogs.json)
- [Catalog HTML draft](docs/skillforge-catalog-draft.html)
- [GitHub skill repo research](research/github-skill-repo-best-practices.md)
