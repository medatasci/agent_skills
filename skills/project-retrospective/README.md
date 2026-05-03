# Project Retrospective

Preserve project memory in a durable retrospective log that captures the user's
ask, Codex's interpretation, work performed, findings, response, and lessons.

## Repo And Package

Skill repo URL:
https://github.com/medatasci/agent_skills/tree/main/skills/project-retrospective

Parent package:
SkillForge Agent Skills Marketplace

Parent package repo URL:
https://github.com/medatasci/agent_skills

Distribution or marketplace:
SkillForge local catalog and Codex skill install workflow

Version or release channel:
Repository `main` branch when published

## Parent Collection

Parent collection:
SkillForge Agent Skills Marketplace

Collection URL:
https://github.com/medatasci/agent_skills

Categories:
Documentation, Project Memory, Business Workflows

Collection context:
This skill belongs in SkillForge's Documentation, Project Memory, and Business
Workflows categories because it turns collaboration context into durable
project knowledge.

## What This Skill Does

Project Retrospective helps Codex create or update an interaction log that
records what the user asked, what Codex understood, what work was done, what was
found, how the user responded, and what went right, wrong, or was missed.

## Why You Would Call It

Call this skill when:

- A project needs a durable record that is more useful than a final summary.
- A long-running task needs memory across sessions.
- You want to preserve both what the user asked and what Codex inferred.

Use it to:

- Create a new project retrospective or interaction log.
- Update an existing retrospective after a meaningful work session.
- Capture decisions, blockers, validation results, and lessons learned.
- Preserve the difference between the user's exact ask and Codex's
  interpretation.
- Make it easier to resume a project later.

Do not use it when:

- The user only wants a brief final answer.
- The log would capture secrets, private data, or sensitive details that should
  not be stored in the repository.

## Keywords

Project retrospective, project memory, interaction log, after-action review,
collaboration memory, project journal, lessons learned, Codex session log,
durable context.

## Search Terms

Project retrospective, project memory, interaction log, after action review,
collaboration memory, project journal, lessons learned, Codex session log,
durable project context, update retrospective log, preserve project decisions.

## How It Works

The skill separates the user's exact ask from Codex's interpretation, then
records actions, findings, validation, user response when available, and lessons
learned. The output should be concise enough to be useful later and candid
enough to preserve what went wrong or was missed.

The skill normally writes or updates a local Markdown log. It should avoid
unrelated code or configuration changes.

## API And Options

SkillForge CLI options:

```text
python -m skillforge install project-retrospective --scope global
python -m skillforge install project-retrospective --scope project --project .
python -m skillforge search "project memory after action review interaction log" --json
python -m skillforge evaluate project-retrospective --json
```

Skill-specific APIs, scripts, or options:

- Target retrospective path, typically `retrospectives/interaction_log.md`.
- Optional existing retrospective log to update.
- Optional project milestone or session boundary.
- Optional instruction to omit sensitive details.

Configuration:

- No credentials are required.
- No external service is required.

## Inputs And Outputs

Inputs can include:

- User request.
- Codex interpretation.
- Actions taken.
- Important files changed.
- Command results.
- Key findings.
- User response.
- Open questions.

Outputs can include:

- `retrospectives/interaction_log.md`.
- Concise after-action review entries.
- Optional interaction templates.

Output locations:

- `retrospectives/interaction_log.md` by default when no existing project
  convention is present.
- Existing project retrospective path when one is already established.

## Examples

Beginner example:

```text
Use project-retrospective to create a concise retrospective for this session.
```

Task-specific example:

```text
Use project-retrospective to update this project's interaction log with what
happened in this session.
```

Safety-aware or bounded example:

```text
Use project-retrospective, but do not include secrets, private data, or internal
details that should not be written to this repo.
```

Troubleshooting or refinement example:

```text
Use project-retrospective to revise the last retrospective entry so it captures
what Codex got wrong without adding unnecessary detail.
```

## Help And Getting Started

Start with:

```text
Create or update a concise retrospective for this project. Capture what I asked,
what you understood, what you did, what changed, what worked, what failed, and
what should happen next.
```

Provide:

- The project milestone, session, or task to summarize.
- Any sensitivity limits, such as details that should not be written.

Ask for help when:

- The log is too verbose.
- The log misses the user's original ask.
- The log stores sensitive details.
- The project needs a better retrospective structure.

## How To Call From An LLM

Direct prompt:

```text
Use project-retrospective to update this project's retrospective.
```

Task-based prompt:

```text
Use project-retrospective to create an after-action review for this milestone,
including what I asked, what Codex did, what changed, validation results, and
what remains open.
```

Guarded prompt:

```text
Use project-retrospective, but do not include secrets, private data, or internal
details that should not be written to this repo.
```

Find or install prompt:

```text
Find and install the SkillForge skill that helps preserve project memory and
interaction logs. Ask before installing anything from a peer catalog.
```

## How To Call From The CLI

Search for the skill:

```text
python -m skillforge search "after action review project memory" --json
```

Show skill metadata:

```text
python -m skillforge info project-retrospective --json
```

Install the skill into Codex:

```text
python -m skillforge install project-retrospective --scope global
```

Evaluate the skill before publishing changes:

```text
python -m skillforge evaluate project-retrospective --json
```

Remove the installed skill:

```text
python -m skillforge remove project-retrospective --scope global --yes
```

## Trust And Safety

Risk level:
low

Permissions:

- Local project file read access for project context.
- Local Markdown file writes for retrospective outputs.
- No network or credential access required.

Data handling:
The skill writes project memory into local Markdown files. It should avoid
recording secrets, private data, sensitive business details, or unsupported
claims unless the user explicitly approves that content for the repository.

Writes vs read-only:
The skill writes local retrospective files. It should not modify code,
configuration, or external systems.

External services:
None required.

Credentials:
No credentials are required.

User approval gates:

- Ask before writing sensitive or private details.
- Ask before changing the retrospective location if the project already has a
  convention.

## Feedback

Feedback URL:
https://github.com/medatasci/agent_skills/issues/new/choose

Send feedback when:

- The retrospective misses the user's exact ask.
- The entry overstates what Codex did.
- The log stores too much detail.
- The skill fails to capture a useful lesson.

Promptable feedback:

```text
Send feedback on project-retrospective that the log missed the difference
between what I asked and what Codex inferred.
```

## Author

Marc Edgar / medatasci

Maintainer status:
SkillForge-maintained example skill.

## Citations

No external method citation is required. The skill uses a practical project
retrospective and after-action review structure adapted for Codex interaction
logs.

## Related Skills

- `get-youtube-media`: use before a retrospective when the project involved
  YouTube research or transcript retrieval.
- `huggingface-datasets`: use before a retrospective when the project involved
  dataset inspection.
- `skill-discovery-evaluation`: improve this skill's README, examples,
  metadata, and catalog discoverability.
