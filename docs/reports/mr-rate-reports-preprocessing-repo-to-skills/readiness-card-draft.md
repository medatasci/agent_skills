# Skill Design Card Draft

Name: MR-RATE Report Preprocessing Skill Family

Source: `<local MR-RATE checkout>/data-preprocessing/src/mr_rate_preprocessing/reports_preprocessing`

Source URL: https://github.com/forithmus/MR-RATE/tree/main/data-preprocessing/src/mr_rate_preprocessing/reports_preprocessing

Inspected commit: `e02b4ed79ff427fb3578f03242de2d9d51dc709d`

Workflow goal: Create source-grounded SkillForge skills for MR-RATE radiology report preprocessing: anonymization, translation QC, structuring, structure QC, pathology classification, and shard operations.

Primary users:

- Research engineers operating the MR-RATE report preprocessing pipeline.
- Data scientists auditing intermediate report preprocessing artifacts.
- Agents that need safe, source-supported command planning for MR-RATE reports.

Recommendation:

Build a six-skill family now: one umbrella workflow skill and five child skills.

Recommendation rationale:

The source tree is a staged pipeline, but each stage has different inputs,
outputs, risks, and failure loops. A single giant skill would be harder to
trigger precisely and would load too much context. The selected family keeps
the umbrella overview small while letting agents invoke stage-specific guidance.

## Source Context Map

Use `source-context-map.md` as the evidence layer for this card.

Key source facts:

- Root README positions reports preprocessing inside the MR-RATE dataset and
  vision-language workflow.
- `data-preprocessing/README.md` documents `environment_reports.yml`, report
  preprocessing stages, and the research dataset context.
- Leaf README documents the run-QC-retry-manual-review loop, SLURM rank model,
  expected outputs, and stage details.
- Source scripts provide concrete CLIs and write per-rank CSV/JSON outputs.

## Candidate Scope

Proposed skill type:

- Workflow skill family.
- Stage-specific procedural skills.
- Low-risk deterministic utility skill for shard operations.

Proposed skill IDs:

- `mrrate-report-preprocessing`
- `mrrate-report-anonymization`
- `mrrate-report-translation-qc`
- `mrrate-report-structuring-qc`
- `mrrate-report-pathology-labeling`
- `mrrate-report-shard-operations`

Should this be one skill or multiple skills?

Multiple skills.

Why this scope:

- Anonymization has PHI and token-mapping risk.
- Translation QC has language and clinical meaning checks.
- Structuring QC has parse-state and section-placement rules.
- Pathology labeling has a distinct ontology and research-label caveat.
- Shard operations are deterministic and useful across stages.

## Known Blockers

- No public sample fixtures are available in the inspected tree, so smoke tests
  are limited to validation, catalog generation, and future synthetic fixtures.
- The generated skills are planning/routing skills; they do not yet provide a
  bundled adapter that validates columns, blocks overwrites, or runs source
  scripts with a normalized interface.
- Running the source scripts requires a suitable GPU/vLLM/Hugging Face runtime.

## Open Questions

- Should SkillForge include synthetic CSV fixtures for shard-merge smoke tests?
- Should a future adapter expose `check`, `schema`, and `plan-command`
  subcommands for all MR-RATE report stages?
- Should manual-review workflows become a separate skill after a review
  artifact format is defined?

## Next Action

Run SkillForge catalog build and evaluation for all six skills, then address
publication-readiness gaps.
