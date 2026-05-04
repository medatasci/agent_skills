# Codebase Readiness Card Template

Use this template before creating a SkillForge skill from an algorithm
repository. The card should be short enough to review quickly, but specific
enough that a future generator can turn it into a skill package, adapter plan,
and smoke test.

## Summary

Name:

Source:

Workflow goal:

Primary users:

Recommendation:

Recommendation rationale:

## Candidate Scope

Proposed skill type:

- Algorithm skill
- Workflow skill
- Generator skill
- Other:

Proposed skill ID:

Should this be one skill or multiple skills?

Why this scope:

## Source Inventory

Repository or codebase URL:

Model card URL:

Documentation URLs:

Example or quick-start URLs:

License URLs:

Relevant files or commands:

Version, commit, tag, or release to pin:

## Workflow Fit

User problem:

What the codebase does:

What the codebase does not do:

Where an agent adds value:

What should remain deterministic:

## Input Contract

Required inputs:

Optional inputs:

Accepted file formats:

Required metadata:

Credentials or access requirements:

Expected input size:

Validation checks:

## Output Contract

Primary outputs:

Optional outputs:

Output file formats:

Expected output locations:

Machine-readable summary:

Provenance fields:

Validation checks:

## Execution Surface

Execution type:

- Python API
- CLI command
- MONAI Bundle
- Docker command
- Notebook
- Script
- Other:

Setup commands:

Run commands:

Batch commands:

Resume or cache behavior:

Expected runtime:

## Dependencies

Python version:

Core packages:

External binaries:

GPU required:

CUDA or driver requirements:

Docker required:

Conda required:

Network required:

Large downloads:

Storage requirements:

## Safety, License, And Data Use

Code license:

Model weights license:

Dataset terms:

Permitted use:

Restricted use:

Privacy concerns:

Clinical-use constraints:

Redistribution constraints:

Required user confirmations:

## Agent Decisions

The LLM should decide:

The LLM should not decide:

Clarifying questions to ask:

Failure modes the agent should recognize:

## Deterministic Adapter Plan

Adapter files to create:

Adapter command shape:

Read-only operations:

Write operations:

Network operations:

Error handling:

JSON output fields:

## Smoke Test Plan

Minimal test input:

Expected command:

Expected outputs:

Skip conditions:

How to verify output:

Test data license:

## Skill Package Plan

Suggested files:

```text
skills/<skill-id>/
  SKILL.md
  README.md
  references/
  scripts/
```

References to include:

Scripts to include:

Catalog/search terms:

Related skills:

## Known Blockers

- 

## Open Questions

- 

## Next Action

Next recommended action:
