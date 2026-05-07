# Skill README Structure Options

Archived design note for future SkillForge README template work.

These options capture README structures discussed for SkillForge skills. They
are not the active template yet. Use this file when revisiting how
`skills/<skill-name>/README.md` should balance user onboarding, source-grounded
context, SEO/discovery, and agent-friendly invocation details.

## Design Goal

A skill README should help a person quickly answer:

- What is this skill?
- What can I do with it?
- Why would I use it?
- How do I start with a prompt?
- How do I call it from the CLI?
- What does it need?
- What does it produce?
- What are the risks, limits, permissions, and safety boundaries?
- What sources, papers, repos, model cards, or dataset cards support the claims?
- What related skills or next steps should I consider?

For repo-derived skills, the README should preserve useful context from upstream
README files, docs, papers, model cards, dataset cards, examples, notebooks, and
source-code evidence. The README should not feel like a thin command wrapper.

## Option 1: Fast User Onboarding

Best for the top-level SkillForge README or a broad skill collection.

```markdown
# SkillForge Or Skill Name

One-sentence value proposition.

## What You Can Do Here
- Find skills.
- Install skills.
- Use skills with Codex prompts.
- Share skills.
- Send feedback.

## Quick Start
Promptable install.
CLI install.

## Find A Skill
Prompt example.
CLI example.
What makes search useful.

## Install A Skill
Prompt example.
CLI example.
What happens safely.

## Use A Skill
Prompt example.
CLI example.

## Share Or Improve A Skill
Prompt example.
CLI example.
PR or issue workflow.

## Get Help
Prompt examples.
CLI help commands.

## Trust And Safety
Plain-English risk model.

## Documentation
Links to deeper docs.
```

## Option 2: Skill Home Page

Best for `skills/<skill-name>/README.md`.

```markdown
# Skill Name

Short value proposition.

## What This Skill Does
Plain-English description.

## Why You Would Call It
Use cases and trigger phrases.

## What It Needs
Inputs, permissions, setup, data requirements.

## What It Produces
Outputs, files, reports, command plans, JSON.

## Examples
Promptable examples.
CLI examples.

## How It Works
Short workflow explanation.

## Trust And Safety
Risk level, permissions, data handling, writes vs read-only.

## Sources And Citations
Authoritative upstream repo, papers, model cards, docs.

## Related Skills
SkillForge links.

## Feedback
Issue or PR link.
```

## Option 3: Agent-Friendly README

Best when the README should help Codex or another agent decide whether to use a
skill.

```markdown
# Skill Name

## Use This When
Bulleted trigger conditions.

## Do Not Use This When
Boundaries and failure modes.

## Supported Tasks
Task list with examples.

## Inputs
Structured list.

## Outputs
Structured list.

## Prompt Interface
Natural-language examples.

## CLI Interface
Copyable commands.

## Safety Gates
Approval needed, side effects, network, secrets, writes.

## Source Evidence
Repo paths, docs, papers, model cards.

## Machine-Readable Surfaces
Catalog JSON, SKILL.md, CLI schema, static page.
```

## Option 4: Healthcare Or Research Skill README

Best for skills such as `nv-segment-ctmr`, `nv-generate-ctmr`, and
`radiological-report-to-roi`.

```markdown
# Skill Name

## Research Use Summary
What it helps with, and what it does not claim.

## Supported Modalities
CT, MRI, labels, masks, reports, NIfTI, DICOM, etc.

## Clinical Safety Boundary
Not diagnosis, treatment, triage, or clinical decision-making.

## Inputs
Image volume, report, segmentation, config, model source.

## Outputs
Masks, ROI summaries, reports, command plans, provenance.

## Workflow
Plan, inspect, configure, run only with approval, verify output.

## Example Prompts
Human-friendly examples.

## CLI Examples
Agent-friendly deterministic commands.

## Source Evidence
GitHub repo, papers, model cards, dataset cards.

## Trust And Safety
Data handling, PHI warning, model/license warning, GPU/download warning.
```

## Option 5: Developer Or Contributor README

Best for generated code, adapters, Python modules, and repo-to-skills internals.

```markdown
# Component Name

## Purpose
What this package, script, or module does.

## Where It Fits
Architecture context.

## Public Interfaces
CLI, functions, generated files.

## Development Workflow
Run tests, build catalog, evaluate skill.

## File Map
Important files and what they do.

## Extension Points
Where to add commands, templates, checks.

## Quality Gates
Tests, evaluation, generated file checks.

## Contribution Flow
Issue, branch, PR, review checklist.
```

## Preferred Hybrid For SkillForge Skills

Use the flow of Option 1 because it matches how users think: what is this, what
can I do, and how do I start. Add the richer context from Options 2, 3, and 4
so the README remains useful for humans, searchable by agents, and grounded in
authoritative sources.

```markdown
# Skill Name

One-sentence outcome: what this skill helps the user accomplish.

## What You Can Do With This Skill
- Practical user-facing task 1.
- Practical user-facing task 2.
- Practical user-facing task 3.

## Why You Would Use It
Explain the pain point, workflow, or opportunity.
Mention what the upstream repo, paper, model, dataset, or tool makes possible.

## Quick Start
### Use It With Codex
Prompt example.

### Use It From The CLI
Command example.

## Common Workflows
### Workflow 1
What the user is trying to do.
Prompt.
CLI command, if available.

### Workflow 2
Same pattern.

## What It Needs
Inputs, source checkout, credentials, files, models, GPU, etc.

## What It Produces
Reports, JSON, generated files, masks, plans, configs, logs, etc.

## How It Works
Short explanation of the method or source repo.
Use context from the upstream README, docs, papers, model cards, and examples.

## Trust And Safety
Risk level, permissions, data handling, writes, downloads, network, secrets,
clinical or research boundaries.

## Sources And Citations
Authoritative links.
Upstream repo.
Papers.
Model cards.
Dataset cards.
Important docs.

## Related Skills
Other SkillForge skills that pair well with this one.

## Feedback
Issue or PR link.
```

## Notes For Future Template Work

- Put user value before implementation detail.
- Preserve source-grounded context from repo-derived skills.
- Keep claims traceable to authoritative sources.
- Include both promptable and CLI usage.
- Make safety and side effects visible before any execution path.
- Keep the active template concise enough for users, but structured enough for
  agents and catalog generation.
