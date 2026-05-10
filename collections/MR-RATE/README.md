# MR-RATE Skill Collection

## Most Important Context

This collection packages the 16 MR-RATE SkillForge skills created from the
MR-RATE repository and the follow-on domain-expert skill design work. The skills
remain in the flat SkillForge layout under `skills/<skill-id>/` so catalog
discovery, installation, peer scanning, generated plugin mirrors, and static
site pages continue to work.

This folder is the publication wrapper for the family. It explains what belongs
to the MR-RATE package, how the skills relate to one another, what source
context grounded the work, and the completed review evidence for maintainer
review.

The package is research-only. It does not include MR-RATE data, patient reports,
medical images, credentials, model weights, checkpoints, W&B logs, or PHI. It
does not claim clinical validation and must not be used for diagnosis,
treatment, triage, prognosis, or patient-care decisions.

## Package Contents

Collection files:

- `README.md`: human-facing package overview.
- `manifest.json`: machine-readable list of the 16 skills, source context, and
  package status.
- `publishing-notes.md`: publication checklist, root-to-leaf README context
  requirements, safety notes, and PR preparation notes.
- `publication-review-matrix.md`: restartable per-skill review matrix.
- `review-state.json`: machine-readable review checkpoint for interrupted work.
- `publication-review-evidence.md`: completed source, safety, family, and
  evaluation evidence.
- `pr-summary.md`: draft pull request summary and reviewer notes.

Skill source folders remain under:

```text
skills/<skill-id>/
```

Generated distribution surfaces remain under:

```text
catalog/skills/<skill-id>.json
plugins/agent-skills/skills/<skill-id>/
site/skills/<skill-id>/
```

## Publication Set

The MR-RATE publication set contains exactly 16 skills.

Whole-repository and data workflow skills:

- `mrrate-repository-guide`
- `mrrate-dataset-access`
- `mrrate-data-curator`
- `mrrate-database-analysis`
- `mrrate-mri-preprocessing`
- `mrrate-registration-derivatives`
- `mrrate-contrastive-pretraining`
- `mrrate-contrastive-inference`

Report-preprocessing skills:

- `mrrate-report-preprocessing`
- `mrrate-report-anonymization`
- `mrrate-report-translation-qc`
- `mrrate-report-structuring-qc`
- `mrrate-report-pathology-labeling`
- `mrrate-report-shard-operations`

Domain-expert skills:

- `mrrate-medical-workflow-reviewer`
- `mrrate-clinical-ai-researcher`

## Skill Family Map

| Skill | Role In The Collection |
| --- | --- |
| `mrrate-repository-guide` | Top-level source-grounded guide for choosing the right MR-RATE child skill. |
| `mrrate-dataset-access` | Plans dataset downloads, merges, local layout checks, metadata, reports, labels, and splits. |
| `mrrate-data-curator` | Curates gated MR-RATE reports, labels, metadata, and explicitly approved MRI source batches into local SQLite with provenance. |
| `mrrate-database-analysis` | Analyzes the local MR-RATE SQLite database with read-only SQL, helper views, descriptor tables, and count-unit-aware summaries. |
| `mrrate-mri-preprocessing` | Plans raw DICOM/PACS to defaced native-space NIfTI and metadata workflows. |
| `mrrate-registration-derivatives` | Plans coregistered and atlas derivative workflows and backfilled study recovery. |
| `mrrate-contrastive-pretraining` | Plans source-supported MR-RATE contrastive MRI-report training commands and data contracts. |
| `mrrate-contrastive-inference` | Plans zero-shot pathology scoring and AUROC evaluation from trained checkpoints. |
| `mrrate-report-preprocessing` | Umbrella skill for report anonymization, translation, structuring, QC, labeling, and shard operations. |
| `mrrate-report-anonymization` | Plans report anonymization and anonymization validation with PHI-sensitive safeguards. |
| `mrrate-report-translation-qc` | Plans translation, translation QC, remaining-Turkish detection, and retranslation. |
| `mrrate-report-structuring-qc` | Plans structured report extraction, parse-failure handling, and structure QC. |
| `mrrate-report-pathology-labeling` | Plans source-defined pathology labeling and merged labels output. |
| `mrrate-report-shard-operations` | Plans deterministic shard merge and status-summary operations. |
| `mrrate-medical-workflow-reviewer` | Reviews MR-RATE datasets and workflows for clinical-statistical consistency. |
| `mrrate-clinical-ai-researcher` | Designs and critiques MR-RATE clinical AI algorithms, experiments, ablations, and reproducibility evidence. |

## Source Provenance

MR-RATE source repository:
https://github.com/forithmus/MR-RATE

Source tree requested by the user:
https://github.com/forithmus/MR-RATE/tree/main

Inspected commit:
`e02b4ed79ff427fb3578f03242de2d9d51dc709d`

Important source context reports:

- `docs/reports/mr-rate-reports-preprocessing-repo-to-skills/`
- `docs/reports/mr-rate-whole-repo-to-skills/`

Important README and documentation context included during skill creation:

- MR-RATE root `README.md`
- `data-preprocessing/README.md`
- `data-preprocessing/docs/dataset_guide.md`
- `data-preprocessing/docs/backfilled_reg_studies.md`
- `data-preprocessing/src/mr_rate_preprocessing/reports_preprocessing/README.md`
- `contrastive-pretraining/README.md`

## Root-To-Leaf README Context

Publication review must confirm the ancestor README chain for each
source-derived skill. The review should start from the source leaf where the
relevant code lives, then walk upward through parent directories to the root
README, recording every README found and explicitly noting parent directories
without README files.

This is tracked in:

- `publishing-notes.md`
- `publication-review-matrix.md`
- `manifest.json`

## Safety Boundaries

All MR-RATE skills should preserve these boundaries:

- Treat reports, image paths, study IDs, patient IDs, labels, derived artifacts,
  checkpoints, predictions, logs, and metrics as sensitive research artifacts.
- Prefer aggregate and de-identified summaries for review.
- Ask before inspecting raw reports, patient-level records, image paths,
  private checkpoints, or PHI-sensitive artifacts.
- Ask before downloads, uploads, unzipping/deleting archives, GPU jobs, W&B
  logging, SLURM submissions, model downloads, checkpoint writes, or inference
  writes.
- Do not diagnose, treat, triage, certify clinical validity, or present model
  outputs or report-derived labels as clinical truth.
- Preserve MR-RATE source caveats, including research-only framing, gated data,
  model weights marked as coming soon, and paper/citation marked as coming soon
  where relevant.

## Evaluation Status

As of May 10, 2026, all 16 skills evaluated successfully with SkillForge:

```text
16/16 ok
16/16 score 100/100
0 sample-search failures
0 evaluator recommendations
```

The restartable publication review matrix is complete. The deterministic
evaluator confirms SkillForge structure and search readiness; the matrix records
source, privacy/safety, family-consistency, and publication judgment.

## Rebuild And Evaluation Commands

Use the active Python environment where SkillForge is installed:

```text
python -m skillforge build-catalog --json
```

Evaluate one skill:

```text
python -m skillforge evaluate mrrate-repository-guide --json
```

Evaluate all package skills by reading `manifest.json` or by using the explicit
skill list in `publishing-notes.md`.

## Next Publication Step

The local package is ready for maintainer review. The next operational step is
to stage the intended 16-skill package, commit, and open a SkillForge
contribution pull request.
