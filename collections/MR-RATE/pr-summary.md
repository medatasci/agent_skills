# MR-RATE Skill Collection Pull Request Summary

## Summary

Add a 14-skill MR-RATE SkillForge collection covering repository orientation,
dataset access, MRI preprocessing, report preprocessing, registration
derivatives, contrastive pretraining, contrastive inference, and two
domain-expert research review skills.

The skills remain in the flat SkillForge layout under `skills/<skill-id>/`.
The new `collections/MR-RATE/` folder packages them as a reviewable publication
family without changing catalog discovery behavior.

## Changed Skill Families

Whole-repository and data workflow skills:

- `mrrate-repository-guide`
- `mrrate-dataset-access`
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

## Why

MR-RATE spans data access, raw preprocessing, report preprocessing,
registration derivatives, model training, inference, medical-statistical
workflow review, and clinical AI algorithm development. One monolithic skill
would be too broad and risky. This collection keeps the skills narrow while
making the family discoverable and publishable together.

## Source Provenance

MR-RATE source repository:
https://github.com/forithmus/MR-RATE

Inspected commit:

```text
e02b4ed79ff427fb3578f03242de2d9d51dc709d
```

Source reports:

- `docs/reports/mr-rate-reports-preprocessing-repo-to-skills/`
- `docs/reports/mr-rate-whole-repo-to-skills/`

## Checks

```text
python -m skillforge build-catalog --json
python -m skillforge evaluate <each MR-RATE skill> --json
```

Evaluation result:

```text
14/14 ok
14/14 score 100/100
0 sample-search failures
0 evaluator recommendations
```

Additional review evidence:

- `collections/MR-RATE/publication-review-matrix.md`
- `collections/MR-RATE/publication-review-evidence.md`
- `collections/MR-RATE/review-state.json`

The generated aggregate catalog, search index, agent well-known index, plugin
skill list, and `llms.txt` were rebuilt so they include the 14 reviewed MR-RATE
skills and do not reference the excluded local `mr-rate-data-curator` skill.

## Safety And Privacy

This is a research-only package. It does not include MR-RATE data, patient
reports, medical images, credentials, model weights, checkpoints, W&B logs, or
PHI.

The skills preserve approval gates for downloads, uploads, GPU jobs, W&B
logging, SLURM submission, model downloads, checkpoint writes, inference
writes, and PHI-sensitive processing.

The skills must not be used for diagnosis, treatment, triage, prognosis,
clinical validation, or patient-care decisions.

## Excluded From This PR

`skills/mr-rate-data-curator/` is intentionally excluded. It was present in the
worktree but not reviewed or evaluated as part of this 14-skill package.
Generated per-skill artifacts for that excluded local skill should not be staged
with this PR.

## Review Notes

Important review points:

- Confirm the MR-RATE license and research-only wording are acceptable.
- Confirm root-to-leaf README context is sufficient for each source-derived
  skill.
- Confirm generated catalog, plugin, and static-site files should be included
  in the same PR.
- Decide whether future SkillForge work should add first-class skill-family
  metadata or nested collection support.
