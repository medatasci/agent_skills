# Skill Discovery Evaluation

Evaluate and improve SkillForge skills before publication so humans and agents
can find them, understand them, trust them, install them, and use them.

## Repo And Package

Skill repo URL:
https://github.com/medatasci/agent_skills/tree/main/skills/skill-discovery-evaluation

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
Developer Tools, Documentation, Safety And Review

Collection context:
This skill belongs in SkillForge's Developer Tools, Documentation, and Safety
And Review categories because it helps maintain the quality of the marketplace
itself.

## What This Skill Does

Skill Discovery Evaluation makes SkillForge skills easier to find, evaluate,
trust, install, and use. It combines LLM judgment with deterministic SkillForge
CLI evidence so each skill has clear metadata, realistic examples, good trigger
language, a useful README home page, and generated catalog outputs.

## Why You Would Call It

Call this skill when:

- You are creating, importing, editing, or publishing a SkillForge skill.
- A skill is hard to find by task, topic, or natural-language search.
- You need to improve `SKILL.md`, `README.md`, examples, aliases, or trigger
  boundaries before opening a PR.

Use it to:

- Evaluate a skill for publication readiness.
- Improve `SKILL.md` metadata, aliases, tasks, examples, and trigger guidance.
- Improve `README.md` as the skill's public home page.
- Draft should-trigger and should-not-trigger queries.
- Compare a skill against nearby or related skills.
- Rebuild and review generated catalog, search, and static site outputs.

Do not use it when:

- The task is generic website SEO unrelated to SkillForge skills.
- The user wants unsupported trust, review, capability, owner, or provenance
  claims added.

## Keywords

SkillForge, skill SEO, skill discovery evaluation, skill metadata, README home
page, trigger language, publication review, search audit, agent skill catalog,
skill generation.

## Search Terms

Skill SEO, skill discovery evaluation, make skill findable, improve skill
search, evaluate skill for publication, trigger evaluation, SkillForge
publication review, README home page, agent skill metadata, generate skill
README, improve skill discoverability.

## How It Works

The skill reads the source skill, reviews how humans and agents would discover
it, drafts positive and negative trigger queries, improves `SKILL.md` and
`README.md` when the meaning is clear, rebuilds generated catalog outputs, and
runs deterministic SkillForge evaluation. Python owns checksums, catalog JSON,
search indexes, static pages, and repeatable reports.

It should ask before changing behavior, permissions, risk level, owner,
provenance, trust claims, or anything that would make a public-safe skill expose
internal information.

## API And Options

SkillForge CLI options:

```text
python -m skillforge install skill-discovery-evaluation --scope global
python -m skillforge install skill-discovery-evaluation --scope project --project .
python -m skillforge search "skill SEO evaluate skill for publication" --json
python -m skillforge evaluate skill-discovery-evaluation --json
```

Skill-specific APIs, scripts, or options:

- `python -m skillforge validate <skill-path> --json`.
- `python -m skillforge search-audit <skill-id> --json`.
- `python -m skillforge search "<query>" --json`.
- `python -m skillforge build-catalog`.
- `python -m skillforge evaluate <skill-id> --json`.

Configuration:

- No credentials are required.
- Local filesystem access to the SkillForge repo is required for edits.

## Inputs And Outputs

Inputs can include:

- SkillForge skill ID.
- Path to `SKILL.md`.
- Path to a skill folder.
- Target users.
- Publication context.
- Peer-catalog or nearby skill results.

Outputs can include:

- Improved `SKILL.md` metadata.
- Improved `README.md` home page.
- Should-trigger and should-not-trigger queries.
- Regenerated catalog outputs.
- Sample search results.
- Publication-readiness report.

Output locations:

- `skills/<skill-id>/SKILL.md`.
- `skills/<skill-id>/README.md`.
- Generated `catalog/` and `site/` outputs after `build-catalog`.

## Examples

Beginner example:

```text
Use skill-discovery-evaluation to evaluate huggingface-datasets for publication.
```

Task-specific example:

```text
Use skill-discovery-evaluation to evaluate huggingface-datasets for publication,
improve its README and search metadata if needed, rebuild the catalog, and show
the evaluation report.
```

Safety-aware or bounded example:

```text
Use skill-discovery-evaluation, but ask before changing behavior, permissions,
risk level, owner, or provenance claims.
```

Troubleshooting or refinement example:

```text
Use skill-discovery-evaluation to explain why project-retrospective is not
showing up for "after action review" searches and propose a fix.
```

## Help And Getting Started

Start with:

```text
Evaluate <skill-id> for publication. Improve SKILL.md and README.md only where
the meaning is clear, rebuild the catalog, and show me the evaluation report.
```

Provide:

- The skill ID or path.
- Any target audience or publication context that should shape the README.

Ask for help when:

- A skill is hard to find.
- Examples feel artificial.
- A README reads like a checklist instead of a home page.
- A search query returns the wrong skill.

## How To Call From An LLM

Direct prompt:

```text
Use skill-discovery-evaluation to evaluate <skill-id> for publication.
```

Task-based prompt:

```text
Use skill-discovery-evaluation to improve the skill README, search metadata,
examples, and trigger boundaries, then run SkillForge evaluation.
```

Guarded prompt:

```text
Use skill-discovery-evaluation, but ask before changing behavior, permissions,
risk level, owner, or provenance claims.
```

Find or install prompt:

```text
Find and install the SkillForge skill that helps improve skill discoverability.
Ask before installing anything from a peer catalog.
```

## How To Call From The CLI

Search for the skill:

```text
python -m skillforge search "make skill findable" --json
```

Show skill metadata:

```text
python -m skillforge info skill-discovery-evaluation --json
```

Install the skill into Codex:

```text
python -m skillforge install skill-discovery-evaluation --scope global
```

Evaluate the skill before publishing changes:

```text
python -m skillforge evaluate skill-discovery-evaluation --json
```

Remove the installed skill:

```text
python -m skillforge remove skill-discovery-evaluation --scope global --yes
```

## Trust And Safety

Risk level:
low

Permissions:

- Read and edit local SkillForge skill files when the user asks for changes.
- Run local SkillForge Python CLI commands.
- No credential access required.

Data handling:
The skill works on local SkillForge source files and generated catalog outputs.
It should not add private or internal information to public-safe skills, and it
should not invent trust, owner, permission, or provenance claims.

Writes vs read-only:
The skill can edit `SKILL.md` and `README.md` when the user requests
implementation. Python regenerates catalog JSON, search indexes, static pages,
checksums, and well-known files.

External services:
None required for local evaluation and publication checks.

Credentials:
No credentials are required.

User approval gates:

- Ask before changing behavior, risk level, permissions, owner, or provenance.
- Ask before importing or installing anything from a peer catalog.
- Ask before adding private or internal information to public-safe skills.

## Feedback

Feedback URL:
https://github.com/medatasci/agent_skills/issues/new/choose

Send feedback when:

- A skill is still hard to find.
- Examples feel artificial.
- A README reads like a checklist instead of a home page.
- The evaluation report misses an obvious discovery problem.

Promptable feedback:

```text
Send feedback on skill-discovery-evaluation that the README evaluation missed a
missing trust and safety section.
```

## Author

Marc Edgar / medatasci

Maintainer status:
SkillForge-maintained marketplace quality skill.

## Citations

No external method citation is required. The method is SkillForge-specific and
is defined by the local requirements, search plan, catalog schema, and
publication evaluation workflow.

## Related Skills

- `project-retrospective`: capture what changed, what was evaluated, and what
  remains after publication work.
- `huggingface-datasets`: data skill useful as an example for search and README
  evaluation.
- `get-youtube-media`: media skill useful as an example for risk-aware
  discovery language.
