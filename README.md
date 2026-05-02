# Agent Skills Marketplace

Reusable Codex workflows for people who do not want to reinvent the wheel.

Agent Skills Marketplace is a growing collection of practical Codex skills for
accessing information, analyzing work, preserving context, and turning useful
prompts into repeatable business workflows.

The idea is simple:

- **Find a useful workflow.** Install the marketplace once and refresh it as new
  skills are added.
- **Use it with a prompt.** You should not need to know Git, Bash, PowerShell,
  or plugin internals to get value from a skill.
- **Improve it together.** If a skill helps, breaks, or inspires a better one,
  feedback is welcome.
- **Share what works.** If you build a useful skill, Codex can help package it
  as a pull request so others can benefit.

## What You Can Do Here

- **Search for new skills.** Browse the Skill Catalog or ask Codex what is
  available after you install the marketplace.
- **Download and install a skill.** Paste one prompt into Codex and let Codex
  add the marketplace for you.
- **Refresh skills you use.** Ask Codex to update the marketplace when new
  skills or improvements are published.
- **Provide feedback.** Report what helped, what failed, what was confusing, or
  what workflow you wish existed.
- **Share a skill you developed.** Ask Codex to package your skill as a
  marketplace contribution and help open a pull request or issue.

## Start Here

Open Codex and paste this prompt:

```text
Please install the Agent Skills Marketplace for me.

Do not ask me to open Bash, PowerShell, or a terminal unless something blocks you.
Use the local shell yourself to run:

codex plugin marketplace add https://github.com/medatasci/agent_skills.git --ref main

Then verify the marketplace was registered. If Codex needs a restart or if I need
to click anything in the plugin directory, tell me exactly what to click. After
the Agent Skills plugin is available, list the installed skills and show one
short example using any newly available skill.
```

This is the preferred path: stay in Codex, paste one prompt, and let Codex do
the setup work.

## Skill Catalog

Available today:

### `get-youtube-media`

Search YouTube for learning or research topics, collect captions/transcripts,
save restartable retrieval queues, and optionally download MP4 or audio files
for videos the user is authorized to save.

Use it when you want to turn YouTube videos or search results into reusable
local transcript artifacts.

```text
Use $get-youtube-media to search YouTube for "how to read an MRI for brain lesions",
save a restartable queue for the top 10 results, and transcribe the top 3 videos.
```

### `project-retrospective`

Create or update a durable project retrospective log. The skill records what you
asked, what Codex understood, what Codex did, key findings, your response when
available, and what went right, wrong, or was missed.

Use it when you want a project to remember more than the final code diff.

```text
Use $project-retrospective to update this project's retrospective.

Create or update a retrospective log for this project. Capture what I asked,
what you understood, what you did, the key findings, my response if available,
and what went right, wrong, or was missed. If there is no existing retrospective,
create one at retrospectives/interaction_log.md. Keep it concise, candid, and
useful for someone returning to this project later.
```

## Skill Refresh

After the marketplace is installed, you can ask Codex to refresh your local
copy:

```text
Please update the Agent Skills Marketplace and tell me which skills are available now.
```

## Send Feedback on a Skill

Feedback is part of the product. If a skill helped, failed, confused you, or
gave you an idea for a better workflow, open an issue in this repo.

You can also ask Codex to prepare the feedback:

```text
Please help me send feedback to the Agent Skills Marketplace.

I used this skill:
<skill-name>

What I was trying to do:
<short description>

What happened:
<what worked, failed, confused me, or could be improved>

Please turn this into a clear GitHub issue for:
https://github.com/medatasci/agent_skills
```

### Usage Signals

Automatic usage metering is not built into this repository yet. For now, usage
signals can be reported through GitHub issues. Over time, those reports can help
answer practical questions:

- Which skills are actually being used?
- Which workflows save the most time?
- Which skills need better prompts, examples, or documentation?
- What new skills should be built next?

## Share A Skill

If you built a Codex skill that helps you access, analyze, summarize, or manage
information, Codex can help package it for this marketplace.

Copy this prompt into Codex:

```text
I built a Codex skill and want to submit it to the Agent Skills Marketplace.

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

When the files are ready, show me the diff and help me commit the changes on a
new branch. If I have GitHub access, help me open a pull request. If I do not,
help me open an issue that includes the skill description, example prompt, and
files needed for review.
```

The contribution lifecycle is:

1. Build and test your skill locally in Codex.
2. Ask Codex to package it using the prompt above.
3. Review the diff Codex prepares.
4. Open a pull request or issue in this repository.
5. Maintainers review, edit if needed, and merge accepted skills.
6. After merge, anyone who installed the marketplace can ask Codex to refresh it.

A strong contribution includes:

- A skill folder with a `SKILL.md` file.
- A clear description of when someone should use the skill.
- Any required resources inside the skill folder, such as `references/`,
  `scripts/`, `assets/`, or `agents/openai.yaml`.
- A short example prompt that shows how someone would use the skill in Codex.

Only `SKILL.md` is required. Add the other folders only when the skill needs
them.

## Manual Install

If you prefer using a terminal yourself, run:

```powershell
codex plugin marketplace add https://github.com/medatasci/agent_skills.git --ref main
```

Then restart Codex if needed. Open the Codex plugin directory, choose the
`Agent Skills Marketplace`, and install `Agent Skills` if it is not already
installed.

## For Maintainers: Add a New Submitted Skill from a User

Use this prompt to have Codex review a submitted skill pull request and merge it
when it is ready:

```text
Please help me review Agent Skills Marketplace pull requests.

Pull requests:
https://github.com/medatasci/agent_skills/pulls

First, list open PRs in a table with:
PR number, title, author, updated date, URL, and one-line summary.

If there are no open PRs, say there are no marketplace PRs to review and stop.
If there is exactly one open PR, summarize that PR and ask whether I want to
review it now. If there are multiple open PRs, ask me which PR to review.

For the selected PR, review the diff and classify it as:
Ready to merge, Needs changes, or Needs maintainer judgment.

Check:
- Skill is under plugins/agent-skills/skills/<skill-name>/
- SKILL.md has valid name and description frontmatter
- README.md Skill Catalog is updated with a user-facing description and example prompt
- Plugin version is bumped
- JSON manifests parse
- No secrets, private data, or unrelated files are included

If the selected PR adds or changes a skill, README.md's Skill Catalog must be
updated before merge. If the Skill Catalog entry is missing or stale, classify
the selected PR as Needs changes and draft the exact catalog entry to add or
update.

If the selected PR needs changes, draft a concise review comment.
If the selected PR is ready to merge, summarize what will merge and ask for my
confirmation before merging. After merge, draft a short release note telling
users how to refresh the marketplace.
```

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
refreshed cleanly. Then update `Skill Catalog` with the new skill name and a
short description written for someone deciding whether to use it.
