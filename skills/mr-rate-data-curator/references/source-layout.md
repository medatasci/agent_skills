# MR-RATE Source Layout

Canonical gated dataset:

- `https://huggingface.co/datasets/Forithmus/MR-RATE`

Useful source groups:

- `reports/batchNN_reports.csv`: structured report text with `study_uid`, `report`,
  `clinical_information`, `technique`, `findings`, and `impression`.
- `metadata/batchNN_metadata.csv`: per-series MRI metadata with `patient_uid`,
  `study_uid`, `series_id`, classified modality fields, shape/spacing fields,
  and many DICOM-derived metadata columns.
- `pathology_labels/mrrate_labels.csv`: global 0/1 study-level pathology label
  matrix keyed by `study_uid`.
- `mri/batchNN/`: native MRI archives. Treat as large-data and require explicit
  user approval before download.

Local workspace layout used by the curator:

```text
research-data/sources/mr-rate/
  reports/batchNN_reports.csv
  metadata/batchNN_metadata.csv
  pathology_labels/mrrate_labels.csv
  browser_download_batchNN.json
research-data/mr-rate.sqlite
```

Important database tables:

- `source_files`: registered imported local files, hashes, row counts, sizes.
- `upstream_sources`: planned/imported Hugging Face repo paths and batch status.
- `studies`, `patients`, `reports`, `report_sections`.
- `metadata_rows`: raw per-series metadata rows.
- `report_pathology_labels`: normalized positive pathology labels by default.
- `mri_files`: planned/indexed MRI archive or NIfTI file records.
- `report_search`: full-text search table for reports and positive disease text.

Common helper views for query-first workflows:

- `v_query_positive_labels`: one positive label per report/study.
- `v_query_patient_summary`: one row per linked patient.
- `v_query_study_summary`: one row per study.
- `v_query_pathology_stats`: one row per pathology with patient/study/report
  counts.
- `v_query_patient_pathologies`: one row per patient/pathology.
- `v_query_infarction_cases`: infarction-focused positive-label view.
- `v_query_metadata_series`: one metadata row/series with normalized scan
  fields.
- `v_query_sequence_stats`: one row per sequence/protocol grouping.
- `v_query_cooccurring_pathologies`: one pathology pair per study.

LLM query descriptor tables, when present:

- `llm_query_view_catalog`
- `llm_query_column_catalog`
- `llm_query_intent_catalog`
- `llm_query_rules`
- `llm_query_examples`
- `v_llm_query_guide`
