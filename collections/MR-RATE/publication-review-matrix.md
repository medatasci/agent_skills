# MR-RATE Publication Review Matrix

This matrix makes the publication process restartable and auditable. Every row
is one skill in the 16-skill MR-RATE publication set. All rows are complete as
of May 10, 2026.

Automated SkillForge checks have passed for all 16 skills. The source, safety,
ancestor README, family-fit, and publication-judgment checkboxes are complete.

Legend:

- Auto: deterministic SkillForge checks.
- Ancestor README: root-to-leaf README chain reviewed.
- Source claims: source-specific commands, caveats, and claims checked against
  MR-RATE source context.
- Safety: PHI, research-only, side effects, and clinical-care boundaries.
- Family: related-skill links, role, and collection fit.

## Automated Review Snapshot

| Skill | SKILL.md | README.md | No placeholders | Catalog | Plugin | Site | Eval 100 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `mrrate-repository-guide` | [x] | [x] | [x] | [x] | [x] | [x] | [x] |
| `mrrate-dataset-access` | [x] | [x] | [x] | [x] | [x] | [x] | [x] |
| `mrrate-data-curator` | [x] | [x] | [x] | [x] | [x] | [x] | [x] |
| `mrrate-database-analysis` | [x] | [x] | [x] | [x] | [x] | [x] | [x] |
| `mrrate-mri-preprocessing` | [x] | [x] | [x] | [x] | [x] | [x] | [x] |
| `mrrate-registration-derivatives` | [x] | [x] | [x] | [x] | [x] | [x] | [x] |
| `mrrate-contrastive-pretraining` | [x] | [x] | [x] | [x] | [x] | [x] | [x] |
| `mrrate-contrastive-inference` | [x] | [x] | [x] | [x] | [x] | [x] | [x] |
| `mrrate-report-preprocessing` | [x] | [x] | [x] | [x] | [x] | [x] | [x] |
| `mrrate-report-anonymization` | [x] | [x] | [x] | [x] | [x] | [x] | [x] |
| `mrrate-report-translation-qc` | [x] | [x] | [x] | [x] | [x] | [x] | [x] |
| `mrrate-report-structuring-qc` | [x] | [x] | [x] | [x] | [x] | [x] | [x] |
| `mrrate-report-pathology-labeling` | [x] | [x] | [x] | [x] | [x] | [x] | [x] |
| `mrrate-report-shard-operations` | [x] | [x] | [x] | [x] | [x] | [x] | [x] |
| `mrrate-medical-workflow-reviewer` | [x] | [x] | [x] | [x] | [x] | [x] | [x] |
| `mrrate-clinical-ai-researcher` | [x] | [x] | [x] | [x] | [x] | [x] | [x] |

## Per-Skill Publication Review

| Skill | Purpose clear | Use/do-not-use | Inputs/outputs | Examples | Related skills | Risk/permissions | Safety | Source claims | Ancestor README | No PHI/private paths | Family fit | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `mrrate-repository-guide` | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | Reviewed as top-level guide and family router. |
| `mrrate-dataset-access` | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | Reviewed for gated data, storage, download, merge, and layout boundaries. |
| `mrrate-data-curator` | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | Reviewed for authenticated downloads, SQLite writes, source provenance, browser credential boundaries, and MRI opt-in gates. |
| `mrrate-database-analysis` | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | Reviewed for read-only SQLite analysis, helper views, descriptor tables, count units, and private local record previews. |
| `mrrate-mri-preprocessing` | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | Reviewed for raw DICOM/PACS, defacing, uploads, GPU, and write side effects. |
| `mrrate-registration-derivatives` | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | Reviewed for ANTs, derivative writes, zips, uploads, and research-only interpretation. |
| `mrrate-contrastive-pretraining` | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | Reviewed for training, model downloads, W&B, SLURM, checkpoints, and source-supported options. |
| `mrrate-contrastive-inference` | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | Reviewed for checkpoint loading, inference writes, score artifacts, AUROC, and research-score limits. |
| `mrrate-report-preprocessing` | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | Reviewed as report-branch umbrella with PHI-sensitive staged workflow boundaries. |
| `mrrate-report-anonymization` | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | Reviewed for PHI, token mappings, raw report columns, vLLM, and validation outputs. |
| `mrrate-report-translation-qc` | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | Reviewed for translation sensitivity, QC/retry workflow, remaining-Turkish checks, and model runtime gates. |
| `mrrate-report-structuring-qc` | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | Reviewed for structured fields, parse status, QC, and no clinical-content invention. |
| `mrrate-report-pathology-labeling` | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | Reviewed for 37-label source ontology, label merge, research-label caveats, and no clinical-truth claims. |
| `mrrate-report-shard-operations` | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | Reviewed for deterministic merges, shard sensitivity, and safe overwrite/delete boundaries. |
| `mrrate-medical-workflow-reviewer` | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | Reviewed as clinical-statistical workflow QC expert, not a command runner or clinical validator. |
| `mrrate-clinical-ai-researcher` | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | [x] | Reviewed as algorithm-development research expert, not training/inference executor or clinical validator. |

## Safety Search Checklist

Run these checks across the 16 reviewed skill folders before marking the package
ready for PR:

- [x] Search for local absolute paths that should not be public.
- [x] Search for secrets, credentials, tokens, or keys.
- [x] Search examples for raw reports, patient identifiers, or PHI-like text.
- [x] Search for unsupported clinical-care claims.
- [x] Search for side-effecting commands that do not ask for approval.

Suggested search scope:

```text
skills/mrrate-repository-guide
skills/mrrate-dataset-access
skills/mrrate-data-curator
skills/mrrate-database-analysis
skills/mrrate-mri-preprocessing
skills/mrrate-registration-derivatives
skills/mrrate-contrastive-pretraining
skills/mrrate-contrastive-inference
skills/mrrate-report-preprocessing
skills/mrrate-report-anonymization
skills/mrrate-report-translation-qc
skills/mrrate-report-structuring-qc
skills/mrrate-report-pathology-labeling
skills/mrrate-report-shard-operations
skills/mrrate-medical-workflow-reviewer
skills/mrrate-clinical-ai-researcher
```

## Review Completion Summary

```text
Reviewer: Codex / SkillForge
Date: May 10, 2026
Rows completed: 16/16
Remaining risks: Maintainer review should confirm publication scope, MR-RATE license wording, and whether to publish all 16 skills together.
Evaluation evidence: 16/16 SkillForge evaluations ok, 16/16 score 100/100, 0 sample-search failures, 0 evaluator recommendations.
Recommendation: Ready for maintainer review as a pull request package, including `skills/mrrate-data-curator/` for local SQLite curation and `skills/mrrate-database-analysis/` for read-only SQL analysis.
```
