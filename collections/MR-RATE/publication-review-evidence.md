# MR-RATE Publication Review Evidence

Review date: May 10, 2026

Collection: `MR-RATE`

Publication set: 16 skills

## Summary

This evidence file records the post-package publication-readiness pass for the
16 MR-RATE skills. It complements `publication-review-matrix.md` and
`review-state.json`.

Outcome:

```text
16/16 skills present
16/16 catalog entries present
16/16 plugin mirrors present
16/16 static site pages present
16/16 SkillForge evaluations ok
16/16 SkillForge scores 100/100
0 sample-search failures
0 evaluator recommendations
```

Update note:

`skills/mrrate-data-curator/` remains the high-risk curation skill for
authenticated downloads, database writes, and MRI source handling.
`skills/mrrate-database-analysis/` has been split out as the read-only SQL
analysis skill for helper views, descriptor tables, descriptive statistics, and
private local record previews.

## Evaluated Skills

- `mrrate-repository-guide`
- `mrrate-dataset-access`
- `mrrate-data-curator`
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

## Automated Evaluation

Command pattern:

```text
python -m skillforge evaluate <skill-id> --json
```

Result summary:

| Skill | OK | Score | Sample-search failures | Evaluator recommendations |
| --- | --- | --- | --- | --- |
| `mrrate-repository-guide` | yes | 100 | 0 | 0 |
| `mrrate-dataset-access` | yes | 100 | 0 | 0 |
| `mrrate-data-curator` | yes | 100 | 0 | 0 |
| `mrrate-database-analysis` | yes | 100 | 0 | 0 |
| `mrrate-mri-preprocessing` | yes | 100 | 0 | 0 |
| `mrrate-registration-derivatives` | yes | 100 | 0 | 0 |
| `mrrate-contrastive-pretraining` | yes | 100 | 0 | 0 |
| `mrrate-contrastive-inference` | yes | 100 | 0 | 0 |
| `mrrate-report-preprocessing` | yes | 100 | 0 | 0 |
| `mrrate-report-anonymization` | yes | 100 | 0 | 0 |
| `mrrate-report-translation-qc` | yes | 100 | 0 | 0 |
| `mrrate-report-structuring-qc` | yes | 100 | 0 | 0 |
| `mrrate-report-pathology-labeling` | yes | 100 | 0 | 0 |
| `mrrate-report-shard-operations` | yes | 100 | 0 | 0 |
| `mrrate-medical-workflow-reviewer` | yes | 100 | 0 | 0 |
| `mrrate-clinical-ai-researcher` | yes | 100 | 0 | 0 |

## Source Path Evidence

All source paths listed in `manifest.json` were checked for existence against
the local MR-RATE checkout or the local SkillForge package, depending on the
path type.

Result:

```text
0 missing source paths
```

The source-derived skills are grounded in MR-RATE source repository commit:

```text
e02b4ed79ff427fb3578f03242de2d9d51dc709d
```

## Ancestor README Evidence

All ancestor README paths listed in `manifest.json` were checked for existence
against the local MR-RATE checkout.

Result:

```text
0 missing ancestor README files
```

The collection records root-to-leaf README context in:

- `manifest.json`
- `publishing-notes.md`
- `publication-review-matrix.md`

## Safety And Privacy Search Evidence

Search scope:

- the 16 reviewed MR-RATE skill folders, including `skills/mrrate-data-curator/`
  and `skills/mrrate-database-analysis/`
- `collections/MR-RATE/`
- MR-RATE report artifacts under `docs/reports/`

Search result summary:

| Check | Result | Notes |
| --- | --- | --- |
| Local absolute paths in 16 skill folders | no matches | No machine-local paths found in reviewed skill folders. |
| Local absolute paths in collection/report docs | sanitized | Machine-specific paths were replaced with `<local MR-RATE checkout>` or generic `python` command examples. |
| Credentials, tokens, or secrets | benign documentation matches only | Matches describe that credentials may be needed externally or should not be exposed. No actual secrets found. |
| Raw report text or patient examples | no PHI examples found | Matches are generic schema fields such as `study_uid`, `patient_uid`, `AccessionNo`, and `RaporText`. |
| Clinical-care claims | guardrail matches only | Matches are do-not-use and research-only safety language. |
| Side-effecting commands | approval language present | Skills consistently state approval gates for downloads, uploads, GPU jobs, W&B, SLURM, model downloads, checkpoint writes, inference writes, and PHI-sensitive processing. |

## Family Consistency Evidence

Family role review:

- `mrrate-repository-guide` is the top-level guide and router.
- `mrrate-report-preprocessing` is the report-branch umbrella.
- `mrrate-data-curator` is the local SQLite curation skill for authenticated
  MR-RATE source downloads and imports.
- `mrrate-database-analysis` is the read-only SQLite analysis skill for helper
  views, descriptor tables, count-unit-aware SQL, and private local previews.
- Report child skills cover anonymization, translation QC, structuring QC,
  pathology labeling, and shard operations.
- Whole-repo child skills cover dataset access, MRI preprocessing,
  registration derivatives, contrastive pretraining, and contrastive inference.
- `mrrate-medical-workflow-reviewer` is the clinical-statistical dataset and
  workflow quality-control expert.
- `mrrate-clinical-ai-researcher` is the clinical AI algorithm-development
  research expert.

No skill in the collection is presented as the sole orchestrator for all work.
The family uses routing, collaboration, evidence requests, and explicit
side-effect gates.

## Exclusions

No MR-RATE skill folders are excluded from the current publication set.

## Remaining Human Review

The collection is ready for maintainer review as a pull request package. The
remaining action is not another local validation step; it is maintainer review
of scope, safety posture, public wording, and whether to publish all 16 skills
as one MR-RATE collection.
