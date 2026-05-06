# MR-RATE Skill Collaboration Map

This map helps `mrrate-medical-workflow-reviewer` decide which MR-RATE skill can
produce evidence for a clinical-statistical review.

The medical workflow reviewer contributes clinical-statistical interpretation:
it checks whether the data, labels, cohorts, preprocessing choices, and metrics
are medically coherent for the research question. The technical MR-RATE skills
produce source-grounded commands, artifact explanations, and workflow-specific
evidence.

## How To Use This Map

1. Start with the medical/statistical concern.
2. Identify the artifact needed to answer it.
3. Use the skill listed here to produce or explain that artifact.
4. Return to `mrrate-medical-workflow-reviewer` to interpret the artifact in
   clinical-statistical context.

Prefer aggregate summaries and de-identified artifacts. Ask before inspecting
raw reports, patient-level data, image paths, or PHI-sensitive files.

## Skill Map

| Concern | Evidence needed | Skill to use | What the reviewer evaluates afterward |
| --- | --- | --- | --- |
| The workflow spans multiple MR-RATE branches and the right source context is unclear | Whole-repo map, source README chain, child skill choice | `mrrate-repository-guide` | Whether the proposed branch and artifacts match the clinical research question. |
| Cohort availability is unclear | Dataset repository, batch, metadata, report, label, and split availability | `mrrate-dataset-access` | Whether available data can support the intended anatomy, disease, and evaluation plan. |
| Join keys or cohort unit are unclear | `patient_uid`, `study_uid`, `series_id`, report, label, and derivative relationships | `mrrate-dataset-access` | Whether patient/study/series relationships support the intended unit of analysis. |
| Native MRI preprocessing may bias the cohort | Modality filtering, metadata filtering, defacing, and preprocessing success summary | `mrrate-mri-preprocessing` | Whether preprocessing choices preserve anatomy and disease signal and whether exclusions are clinically defensible. |
| Report quality may affect labels | Anonymization, translation, structuring, QC, and shard-processing summaries | `mrrate-report-preprocessing` plus relevant report child skills | Whether report artifacts are usable as research evidence for labels or cohort definitions. |
| Pathology label meaning is uncertain | Source pathology JSON, labeling command plan, merged labels, prevalence, verification stats | `mrrate-report-pathology-labeling` | Whether labels are clinically meaningful, coherent with the disease target, and suitable for training or evaluation. |
| Image-space choice may distort the medical signal | Native/coreg/atlas derivative plan, registration outputs, backfilled study notes | `mrrate-registration-derivatives` | Whether registration or atlas-space assumptions fit the anatomy and disease question. |
| Training setup may leak targets or mismatch the cohort | Training JSONL, report inputs, split plan, objective, config, checkpoint policy | `mrrate-contrastive-pretraining` | Whether training design matches the research question and avoids patient/report/label leakage. |
| Inference metrics need medical-statistical interpretation | Scores, AUROC tables, labels CSV, prompts, split filtering, score outputs | `mrrate-contrastive-inference` | Whether metrics, thresholds, prevalence, uncertainty, and subgroup behavior support the research claim. |

## Evidence Request Pattern

When the reviewer needs another MR-RATE skill, phrase the request as a specific
artifact need:

```text
Use <MR-RATE skill> to produce or explain <artifact>. I need it so
mrrate-medical-workflow-reviewer can assess <medical/statistical concern>.
Do not run side-effecting commands unless approved.
```

Examples:

```text
Use mrrate-dataset-access to summarize patient, study, series, report, label,
and split counts for this local MR-RATE folder. I need it so
mrrate-medical-workflow-reviewer can assess cohort unit consistency and leakage
risk.
```

```text
Use mrrate-report-pathology-labeling to explain the pathology label source and
merge outputs. I need it so mrrate-medical-workflow-reviewer can assess whether
the disease labels are clinically meaningful for the planned analysis.
```

```text
Use mrrate-contrastive-inference to explain the AUROC and score artifacts for
this inference run. I need it so mrrate-medical-workflow-reviewer can assess
metric validity, prevalence effects, and interpretation limits.
```

## Review Handoff Template

Use this when handing evidence back to the medical workflow reviewer:

```text
Research question:
Evidence source skill:
Artifacts reviewed:
Counts or metrics:
Known missing data:
Known side effects:
Assumptions:
Questions for medical-statistical review:
```
