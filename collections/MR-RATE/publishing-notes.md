# MR-RATE Publication Notes

## Current Status

The MR-RATE collection is packaged as a publication wrapper around 16
flat SkillForge skills. The package is not a nested skill directory; it is a
collection-level review and publication artifact.

Automated SkillForge evaluation status as of May 10, 2026:

```text
16/16 ok
16/16 score 100/100
0 sample-search failures
0 evaluator recommendations
```

The row-by-row source, safety, family, generated-artifact, and evaluation
review is complete in `publication-review-matrix.md`. The collection now
includes `mr-rate-data-curator` as a high-risk local SQLite curation skill and
`mrrate-database-analysis` as the read-only SQL analysis skill. The next
publication gate is maintainer review, then optional git staging, commit, and
remote pull request creation.

## Exact Publication Set

- `mrrate-repository-guide`
- `mrrate-dataset-access`
- `mr-rate-data-curator`
- `mrrate-database-analysis`
- `mrrate-mri-preprocessing`
- `mrrate-registration-derivatives`
- `mrrate-contrastive-pretraining`
- `mrrate-contrastive-inference`
- `mrrate-report-preprocessing`
- `mrrate-report-anonymization`
- `mrrate-report-translation-qc`
- `mrrate-report-structuring-qc`
- `mrrate-report-pathology-labeling`
- `mrrate-report-shard-operations`
- `mrrate-medical-workflow-reviewer`
- `mrrate-clinical-ai-researcher`

## Publication Checklist

### 1. Source And Provenance

- [x] Confirm MR-RATE source URL:
      `https://github.com/forithmus/MR-RATE`
- [x] Confirm inspected commit:
      `e02b4ed79ff427fb3578f03242de2d9d51dc709d`
- [x] Confirm the requested source tree was `main`.
- [x] Confirm each skill has source-grounded claims only.
- [x] Confirm source caveats are preserved:
      model weights coming soon, paper/citation coming soon, research-only
      framing, gated dataset access, and non-commercial dataset terms.
- [x] Confirm public package docs do not publish local private paths, reports,
      images, labels, study IDs, patient IDs, credentials, checkpoints, or logs.

### 2. Root-To-Leaf README Context

For every source-derived skill:

- [x] Identify the leaf code directory or source surface.
- [x] Walk upward to the repository root.
- [x] Record every `README.md` found along that path.
- [x] Record missing intermediate README files explicitly.
- [x] Confirm the skill README and SKILL contract do not contradict ancestor
      README context.
- [x] Confirm the source-context reports list the README files used.

This checklist item is called **Ancestor README Chain Reviewed** in the review
matrix.

### 3. Per-Skill Review

For each of the 16 skills:

- [x] `SKILL.md` exists.
- [x] `README.md` exists.
- [x] No template placeholder values remain.
- [x] Purpose is clear in the first few lines.
- [x] `use_when` and `do_not_use_when` are specific.
- [x] Inputs and outputs are concrete.
- [x] Examples are realistic.
- [x] Related skills are correct.
- [x] Risk level is appropriate.
- [x] Permissions and side effects are explicit.
- [x] Safety boundaries are research-only and no clinical-care claims.
- [x] Source commands, if mentioned, match MR-RATE source.
- [x] No raw PHI, reports, image data, credentials, or private paths are
      included.
- [x] README follows the SkillForge home-page structure.
- [x] Skill evaluates at `100/100`.

### 4. Family Consistency

- [x] `mrrate-repository-guide` clearly routes to all relevant children.
- [x] `mrrate-report-preprocessing` correctly acts as the report-branch
      umbrella.
- [x] `mrrate-medical-workflow-reviewer` is framed as
      clinical-statistical quality control for datasets and workflows.
- [x] `mrrate-clinical-ai-researcher` is framed as clinical AI
      algorithm-development research judgment.
- [x] No skill claims to be the only orchestrator for the whole family.
- [x] Safety language is consistent across all medical skills.
- [x] Categories and tags are consistent enough for discovery.
- [x] Related-skill links make sense and do not create circular confusion.

### 5. Safety And Privacy

- [x] Search the 16 skill folders for local absolute paths.
- [x] Search the 16 skill folders for credentials, tokens, keys, or private
      identifiers.
- [x] Search examples for raw report text or PHI-like content.
- [x] Search for unsupported clinical claims such as diagnosis, treatment,
      triage, validated, clinical truth, or patient-care recommendations.
- [x] Confirm every skill that can lead to side effects asks for approval before
      downloads, uploads, GPU jobs, W&B logging, SLURM submission, model
      downloads, checkpoint writes, inference writes, or PHI-sensitive
      processing.

### 6. Generated Artifacts

- [x] Run `python -m skillforge build-catalog --json`.
- [x] Confirm `catalog/skills/<skill-id>.json` exists for all 16.
- [x] Confirm `catalog/skills.json` includes all 16.
- [x] Confirm `catalog/search-index.json` includes all 16.
- [x] Confirm plugin mirrors exist for all 16.
- [x] Confirm static site pages exist for all 16.
- [x] Confirm `site/.well-known/agent-skills/index.json` includes all 16.

### 7. Evaluation

- [x] Run `python -m skillforge evaluate <skill-id> --json` for all 16.
- [x] Confirm all pass.
- [x] Confirm all score `100/100`.
- [x] Confirm sample searches rank the intended skill.
- [x] Document any warnings, even if non-blocking.

### 8. Pull Request Package

- [x] Include all 16 MR-RATE source folders, including the legacy-ID
      `skills/mr-rate-data-curator/`.
- [x] Include generated `catalog/skills/mrrate-*.json` files.
- [x] Include generated aggregate catalog, search, plugin, and site files.
- [x] Include `docs/reports/mr-rate-reports-preprocessing-repo-to-skills/`.
- [x] Include `docs/reports/mr-rate-whole-repo-to-skills/`.
- [x] Include this `collections/MR-RATE/` package.
- [x] Include a PR summary with evaluation evidence and safety/privacy notes.

## Root-To-Leaf README Chains To Verify

| Skill | Leaf/source surface | README chain to verify | Missing README notes |
| --- | --- | --- | --- |
| `mrrate-repository-guide` | Whole repository | Root `README.md`; `data-preprocessing/README.md`; reports preprocessing README; `contrastive-pretraining/README.md` | Not a single leaf; it spans multiple branches. |
| `mrrate-dataset-access` | `data-preprocessing/scripts/hf/` | Root `README.md`; `data-preprocessing/README.md` | No README observed in `scripts/` or `scripts/hf/`. |
| `mr-rate-data-curator` | Local SQLite curation workflow plus MR-RATE dataset guide | Root `README.md`; `data-preprocessing/README.md` | Local workflow-derived skill; see `docs/readiness-cards/mr-rate-data-curator.md` and `skills/mr-rate-data-curator/references/source-context-map.md`. |
| `mrrate-database-analysis` | Local SQLite helper views, descriptor tables, and query helper | Root `README.md`; `data-preprocessing/README.md` | Local workflow-derived skill; see `docs/readiness-cards/mrrate-database-analysis.md` and `skills/mrrate-database-analysis/references/source-context-map.md`. |
| `mrrate-mri-preprocessing` | `data-preprocessing/run/` and `src/mr_rate_preprocessing/mri_preprocessing/` | Root `README.md`; `data-preprocessing/README.md` | No README observed in `run/`, `src/`, or MRI preprocessing package path. |
| `mrrate-registration-derivatives` | `data-preprocessing/src/mr_rate_preprocessing/registration/` | Root `README.md`; `data-preprocessing/README.md` | No README observed in registration package path; backfilled docs are supplemental. |
| `mrrate-contrastive-pretraining` | `contrastive-pretraining/` | Root `README.md`; `contrastive-pretraining/README.md` | Leaf README exists. |
| `mrrate-contrastive-inference` | `contrastive-pretraining/scripts/` | Root `README.md`; `contrastive-pretraining/README.md` | No README observed in `scripts/`; leaf branch README covers inference. |
| `mrrate-report-preprocessing` | `data-preprocessing/src/mr_rate_preprocessing/reports_preprocessing/` | Root `README.md`; `data-preprocessing/README.md`; reports preprocessing README | No README observed at `data-preprocessing/src/` or `src/mr_rate_preprocessing/`. |
| `mrrate-report-anonymization` | Reports preprocessing `01_anonymization/` and `utils/` | Root `README.md`; `data-preprocessing/README.md`; reports preprocessing README | No README observed in stage subdirectory. |
| `mrrate-report-translation-qc` | Reports preprocessing `02_translation/` and `03_translation_qc/` | Root `README.md`; `data-preprocessing/README.md`; reports preprocessing README | No README observed in stage subdirectories. |
| `mrrate-report-structuring-qc` | Reports preprocessing `04_structuring/` and `05_structure_qc/` | Root `README.md`; `data-preprocessing/README.md`; reports preprocessing README | No README observed in stage subdirectories. |
| `mrrate-report-pathology-labeling` | Reports preprocessing `06_pathology_classification/` | Root `README.md`; `data-preprocessing/README.md`; reports preprocessing README | No README observed in stage subdirectory. |
| `mrrate-report-shard-operations` | Reports preprocessing `utils/` and label merge script | Root `README.md`; `data-preprocessing/README.md`; reports preprocessing README | No README observed in utility subdirectory. |
| `mrrate-medical-workflow-reviewer` | Domain-expert skill, source-informed by full MR-RATE family | Root `README.md`; data preprocessing README; reports preprocessing README; contrastive README | Discussion-derived expert; verify against full family source context. |
| `mrrate-clinical-ai-researcher` | Domain-expert skill, source-informed by contrastive pretraining | Root `README.md`; `contrastive-pretraining/README.md` | Discussion-derived expert; verify against contrastive source context. |

## Commands

Use the active Python environment where SkillForge is installed:

```text
$python = 'python'
```

Rebuild:

```text
& $python -m skillforge build-catalog --json
```

Evaluate all 16:

```text
$skills = @(
  'mrrate-repository-guide',
  'mrrate-dataset-access',
  'mr-rate-data-curator',
  'mrrate-database-analysis',
  'mrrate-mri-preprocessing',
  'mrrate-registration-derivatives',
  'mrrate-contrastive-pretraining',
  'mrrate-contrastive-inference',
  'mrrate-report-preprocessing',
  'mrrate-report-anonymization',
  'mrrate-report-translation-qc',
  'mrrate-report-structuring-qc',
  'mrrate-report-pathology-labeling',
  'mrrate-report-shard-operations',
  'mrrate-medical-workflow-reviewer',
  'mrrate-clinical-ai-researcher'
)
foreach ($skill in $skills) {
  & $python -m skillforge evaluate $skill --json
}
```

## Known Open Questions

- Should SkillForge add first-class skill-family metadata so the MR-RATE
  package does not need a separate collection wrapper?
- Should SkillForge support nested skill directories in the future?
- Should source-derived MR-RATE skills get deterministic read-only adapters for
  layout checks, schema checks, and artifact summaries?
- Should synthetic MR-RATE mini-fixtures be created for CI-safe smoke tests?
- Should contrastive inference get deterministic readers for `scores.json`,
  `predicted_scores.npz`, and AUROC tables?
