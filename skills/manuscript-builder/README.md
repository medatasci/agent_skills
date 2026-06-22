# Manuscript Builder

Skill ID: `manuscript-builder`

Keep research projects publication-ready with a living manuscript page,
structured evidence files, citation discipline, reproducibility notes, and
collaborator-friendly update history.

## Repo And Package

Skill repo URL:
https://github.com/medatasci/agent_skills/tree/main/skills/manuscript-builder

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
Documentation, Research, Scientific Writing, Collaboration

Collection context:
This skill belongs in SkillForge because it turns a recurring collaborator
workflow, paper authoring from active project work, into a reusable Codex
behavior with source files, helper scripts, and publication-readiness checks.

## What This Skill Does

Manuscript Builder helps Codex create and maintain a shareable
`project_publication.html` manuscript page plus structured files for claims,
experiments, figures, tables, references, and dated updates. It keeps paper
authoring close to the evidence generated during project work.

## Why You Would Call It

Call this skill when:

- A research project needs a manuscript page that collaborators can review.
- New methods, experiments, results, limitations, or references should be
  reflected in publication files.
- A manuscript needs citation discipline, reproducibility notes, or readiness
  tracking before sharing.

Use it to:

- Create the initial publication files for a project.
- Update claims, experiment records, figure captions, tables, references, and
  manuscript sections after substantive work.
- Audit inline citations in literature-bearing manuscript text.
- Add an `AGENTS.md` hook so future project work keeps manuscript files current.

Do not use it when:

- The user only wants a short status summary with no durable manuscript record.
- The task is only typo fixing or chat cleanup with no publication-relevant
  project substance.
- The user needs journal submission-system work, authorship decisions, or legal
  publication advice.

## Keywords

Manuscript, paper authoring, publication page, project publication, scientific
writing, research manuscript, claims evidence, experiment log, figure registry,
table provenance, BibTeX, citation audit, reproducibility, limitations,
collaboration.

## Search Terms

Build a manuscript from my project, update project publication page, create
project_publication.html, maintain paper claims and evidence, audit manuscript
citations, prepare research paper with collaborators, track experiments for a
paper, write reproducibility notes, keep a Nature-style manuscript current,
keep a NeurIPS-style paper record current.

## How It Works

The skill inspects the project and existing publication files, decides whether
the current work changed publication-relevant substance, creates missing files
from bundled templates when needed, and updates the manuscript plus structured
JSON or BibTeX records. It treats the HTML page as the readable manuscript and
the structured files as the evidence ledger behind the prose.

For literature-bearing edits, the skill requires inline citation discipline. It
uses `scripts/audit_inline_citations.py` to catch uncited literature paragraphs,
orphan inline citations, and references listed without corresponding in-text
callouts when the manuscript is local and auditable.

## API And Options

SkillForge CLI options:

```text
python -m skillforge install manuscript-builder --scope global
python -m skillforge install manuscript-builder --scope project --project .
python -m skillforge search "paper authoring manuscript publication" --json
python -m skillforge evaluate manuscript-builder --json
```

Skill-specific APIs, scripts, or options:

- `scripts/update_project_publication.py --project .` creates missing
  publication files and can append update-log entries.
- `scripts/audit_inline_citations.py --html project_publication.html` audits
  inline citation coverage for the HTML manuscript.
- `assets/project_publication_template.html` provides the default manuscript
  page template.

Configuration:

- No credentials are required for local manuscript maintenance.
- The project root defaults to the current workspace unless the user gives a
  different location.

## Inputs And Outputs

Inputs can include:

- Project goals, methods, experiments, results, claims, limitations, and
  collaboration context.
- Existing manuscript files or a project root where they should be created.
- References, figure evidence, table provenance, and citation requirements.

Outputs can include:

- `project_publication.html`, the shareable living manuscript page.
- `publication_claims.json`, `publication_experiments.json`,
  `publication_figures.json`, `publication_tables.json`, and
  `publication_references.bib`.
- `publication_updates.jsonl`, a dated update log for manuscript changes.

Output locations:

- Project root by default.
- A user-specified project directory when the user gives one.

## Limitations

Known limitations:

- The skill can maintain local manuscript artifacts, but it does not guarantee
  acceptance by a journal, conference, or collaborator.
- Citation audits catch structural problems; they do not prove every citation
  is the best or only source for a claim.
- The skill does not decide authorship, publication venue, or external sharing
  policy.

Choose another skill when:

- You need a project retrospective rather than a manuscript artifact.
- You need domain-specific statistical or clinical review before claims are
  publication-ready.

## Examples

Beginner example:

```text
Use manuscript-builder to create the publication files for this project.
```

Task-specific example:

```text
Use manuscript-builder to update project_publication.html, the claims file, and
the experiment log after these benchmark results.
```

Safety-aware or bounded example:

```text
Use manuscript-builder to audit inline citations in project_publication.html.
Do not add invented references; mark missing sources visibly.
```

Troubleshooting or refinement example:

```text
Use manuscript-builder to review whether the current publication files are
complete enough to share with collaborators and list the weak areas.
```

## Help And Getting Started

Start with:

```text
Use manuscript-builder to create or update the manuscript artifacts for this
research project.
```

Provide:

- The project root if it is not the current workspace.
- Any new results, methods, limitations, figures, tables, or references that
  should change the manuscript.

Ask for help when:

- You are unsure whether a change is publication-relevant.
- A citation audit reports missing or orphaned citations.
- Collaborators need a cleaner manuscript page before review.

## How To Call From An LLM

Direct prompt:

```text
Use manuscript-builder to keep this project publication-ready.
```

Task-based prompt:

```text
Use manuscript-builder to update the manuscript, claims, experiments, figures,
tables, references, and update log for the results we just produced.
```

Guarded prompt:

```text
Use manuscript-builder, but only edit local publication files and do not submit
or send the manuscript anywhere.
```

Find or install prompt:

```text
Find and install the SkillForge skill that helps with collaborative manuscript
authoring and publication evidence files. Ask before installing anything from a
peer catalog.
```

## How To Call From The CLI

Search for the skill:

```text
python -m skillforge search "collaborative manuscript authoring" --json
```

Show skill metadata:

```text
python -m skillforge info manuscript-builder --json
```

Install the skill into Codex:

```text
python -m skillforge install manuscript-builder --scope global
```

Evaluate the skill before publishing changes:

```text
python -m skillforge evaluate manuscript-builder --json
```

Remove the installed skill:

```text
python -m skillforge remove manuscript-builder --scope global --yes
```

## Trust And Safety

Risk level:
low

Permissions:

- Read local project manuscript and evidence files.
- Write local publication files when the user requests manuscript maintenance.
- Run bundled local helper scripts for initialization and citation audits.

Data handling:
The skill is local-first. It reads and writes project files in the workspace or
user-specified project root. It does not require network access for normal use.

Writes vs read-only:
The skill writes manuscript artifacts only when the user asks for persistent
publication maintenance or when project instructions require manuscript files
to stay current.

External services:
None are required for local manuscript maintenance. External publication,
email, repository push, or submission actions are separate tasks that require a
clear user request.

Credentials:
No credentials are required for the bundled local workflow.

User approval gates:

- Ask before submitting, uploading, emailing, or otherwise externally sharing a
  manuscript.
- Ask when authorship, venue, or publication policy decisions are required.

## Feedback

Feedback URL:
https://github.com/medatasci/agent_skills/issues

Send feedback when:

- The manuscript template does not fit a common paper workflow.
- Citation auditing misses a useful pattern or produces noisy warnings.
- The structured files need additional fields for collaborator review.

Promptable feedback:

```text
Send feedback on manuscript-builder that the figure registry needs a field for
reviewer-facing figure status.
```

## Contributing

Contribution path:
Open a pull request against the SkillForge Agent Skills Marketplace with
changes to `skills/manuscript-builder/`, generated catalog files, and any tests
or documentation affected by the behavior change.

If you have a concrete fix, feature, documentation update, or skill
improvement, prepare it as a pull request instead of pushing directly to
`main`:

```text
python -m skillforge contribute "improve manuscript-builder" --type skill --changed skills/manuscript-builder --user-type non-developer --json
```

Before opening a pull request:

- Run `python -m skillforge build-catalog --json`.
- Run `python -m skillforge evaluate manuscript-builder --json`.
- Include any citation-audit or template-validation results relevant to the
  change.

## Author

medatasci

Maintainer status:
SkillForge marketplace maintained; collaborator feedback welcome through
GitHub issues and pull requests.

## Citations

No external scholarly citation is required to use the skill itself. Manuscripts
created with the skill should cite their own scientific sources inline near
literature-derived claims.

## Related Skills

- `project-retrospective`: use when the project needs durable collaboration
  memory rather than a publication manuscript.
- `clinical-statistical-expert`: use when manuscript claims need clinical or
  statistical evidence review.
- `skillforge`: use to install, evaluate, publish, or update SkillForge skills.
