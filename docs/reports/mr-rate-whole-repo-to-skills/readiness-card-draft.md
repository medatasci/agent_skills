# Skill Design Card Draft

Name: MR-RATE Whole-Repository Skill Family

Source: `<local MR-RATE checkout>`

Source URL: https://github.com/forithmus/MR-RATE/tree/main

Inspected commit: `e02b4ed79ff427fb3578f03242de2d9d51dc709d`

Workflow goal: Create source-grounded SkillForge skills for the full MR-RATE repository: dataset/source context, data preprocessing workflows, report preprocessing, image preprocessing, registration/backfill operations, contrastive pretraining, inference/evaluation, and safe research-use operations.

Primary users:

- Researchers using the MR-RATE dataset.
- Maintainers or collaborators rebuilding preprocessing artifacts.
- Agents planning safe commands before data, network, GPU, or upload side effects.

Recommendation: Create a skill family with one top-level router, five new whole-repo child skills, and the six existing report-preprocessing skills.

Recommendation rationale:

The repository is too broad for one skill. Dataset access, raw preprocessing,
report preprocessing, registration, training, and inference all have distinct
inputs, outputs, risks, and source commands. A family keeps user intent
discoverable while preserving narrow safety boundaries.

## Source Context Map

Use `source-context-map.md` as the evidence layer for this card. Key source
context read manually:

- Root `README.md`
- `data-preprocessing/README.md`
- `data-preprocessing/docs/dataset_guide.md`
- `data-preprocessing/docs/backfilled_reg_studies.md`
- `data-preprocessing/src/mr_rate_preprocessing/reports_preprocessing/README.md`
- `contrastive-pretraining/README.md`
- Key source entrypoints under `run/`, `scripts/hf/`, `mri_preprocessing/`,
  `registration/`, and `contrastive-pretraining/scripts/`

## Candidate Scope

Proposed skill type:

- Workflow skill family

Proposed skill IDs:

- `mrrate-repository-guide`
- `mrrate-dataset-access`
- `mrrate-mri-preprocessing`
- `mrrate-registration-derivatives`
- `mrrate-contrastive-pretraining`
- `mrrate-contrastive-inference`
- Existing report branch: `mrrate-report-preprocessing`,
  `mrrate-report-anonymization`, `mrrate-report-translation-qc`,
  `mrrate-report-structuring-qc`, `mrrate-report-pathology-labeling`,
  `mrrate-report-shard-operations`

Should this be one skill or multiple skills?

Multiple skills with a top-level router.

Why this scope:

- Dataset access has gated network and storage side effects.
- Raw MRI preprocessing has DICOM/metadata/privacy and upload side effects.
- Report preprocessing has PHI and LLM/vLLM side effects.
- Registration has ANTs CPU work and large derivative uploads.
- Contrastive training has GPU, model-download, W&B, and checkpoint side effects.
- Contrastive inference has checkpoint and medical-output interpretation risks.

## Known Blockers

- No deterministic adapters were created in this pass; skills are planning and
  source-routing first.
- The scanner did not correctly record git provenance for the whole-repo path;
  commit provenance was added manually.
- Model weights and paper are marked "coming soon" in the root README.
- Multi-label segmentation source is marked "coming soon" in this repository.
- No redistributable medical imaging or report fixtures were added.

## Open Questions

- Should future adapters expose `check`, `schema`, `plan-command`, and
  `inspect-layout` commands for dataset access and preprocessing?
- Should SkillForge add first-class family metadata before these skills are
  published broadly?
- Should a synthetic MR-RATE mini-layout be created for CI-safe smoke tests?
- Should contrastive inference get a small deterministic artifact reader for
  `scores.json`, `predicted_scores.npz`, and AUROC tables?

## Next Action

Next recommended action:

1. Validate the six new skills.
2. Rebuild the SkillForge catalog and static pages.
3. Evaluate the new skills and inspect search results.
4. If these skills become execution-oriented, add source-compatible adapters
   with read-only `check` and `schema` commands before guarded `run` commands.
