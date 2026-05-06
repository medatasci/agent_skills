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
