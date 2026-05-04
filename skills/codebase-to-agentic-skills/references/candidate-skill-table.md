# Candidate Skill Table

Create a candidate skill table after building the source-context map and before
creating SkillForge skill files.

## Required Columns

| Column | Purpose |
| --- | --- |
| Candidate skill | Proposed skill ID or readable name. |
| What it does | Concrete capability, not a vague domain label. |
| Why it is useful | User problem it solves and why an agent helps. |
| Source evidence | README, docs, script, config, model card, paper, or other source supporting the claim. |
| Sample prompt call | High-level prompt a user would actually write. |
| Proposed CLI contract | Deterministic command if code will scan, validate, plan, run, or write outputs. |
| Inputs | Required and optional input artifacts. |
| Outputs | Files, JSON, Markdown, reports, masks, summaries, or other artifacts. |
| Deterministic entrypoints | Existing scripts/APIs/configs or planned adapter commands. |
| LLM context needed | What the LLM may infer, summarize, route, or ask. |
| Safety/license notes | Claims, restrictions, data handling, write behavior, and approval gates. |
| Smoke-test source | Example data, fixture, test, or skip reason. |
| Recommendation | `make-skill-now`, `needs-adapter-first`, `needs-docs-or-examples`, `needs-license-review`, or `not-a-good-skill-yet`. |

## Promotion Rule

Do not promote a candidate to a skill package unless its core behavior, inputs,
outputs, and safety notes are supported by source evidence or implemented
adapter behavior.

## Scope Rule

Use one skill when the codebase exposes one coherent user workflow. Use
multiple skills when functional blocks have different users, inputs, outputs,
risk profiles, dependencies, or invocation patterns. Use a workflow skill when
the value comes from composing several algorithms, datasets, reports, or
deterministic adapters.
