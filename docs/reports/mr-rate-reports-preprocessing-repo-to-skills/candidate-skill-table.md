# Candidate Skill Table

Repo path: `<local MR-RATE checkout>/data-preprocessing/src/mr_rate_preprocessing/reports_preprocessing`

Source URL: https://github.com/forithmus/MR-RATE/tree/main/data-preprocessing/src/mr_rate_preprocessing/reports_preprocessing

Inspected commit: `e02b4ed79ff427fb3578f03242de2d9d51dc709d`

Workflow goal: Create source-grounded SkillForge skills for MR-RATE radiology report preprocessing: anonymization, translation QC, structuring, structure QC, pathology classification, and shard operations.

README chain read:

- `README.md` at repository root.
- `data-preprocessing/README.md`.
- `data-preprocessing/src/mr_rate_preprocessing/reports_preprocessing/README.md`.

No README files were present at `data-preprocessing/src/` or
`data-preprocessing/src/mr_rate_preprocessing/`.

| Candidate skill | What it does | Why it is useful | Source evidence | Sample prompt call | Proposed CLI contract | Inputs | Outputs | Deterministic entrypoints | LLM context needed | Safety/license notes | Smoke-test source | Recommendation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `mrrate-report-preprocessing` | Plans and routes the full reports_preprocessing workflow. | Prevents agents from guessing stage order, columns, or output handoffs. | Root README component table; data-preprocessing README report preprocessing section; leaf README pipeline overview. | "Plan the MR-RATE report preprocessing workflow from my current artifacts." | Planning-only; use child skills for stage commands. | Source path, current stage, artifact paths, runtime constraints. | Runbook, stage checklist, child-skill routing. | None bundled; delegates to source scripts. | Summarize README chain, ask stage questions, preserve source order. | Medium risk because it may prepare commands for PHI-sensitive GPU jobs; no clinical use claims. | Documentation-only smoke: verify README chain and child skill routing. | make-skill-now |
| `mrrate-report-anonymization` | Plans anonymization and anonymization QC. | This stage has PHI/token-mapping risk and different inputs from all later stages. | `01_anonymization/anonymize_reports_parallel.py`; `utils/validate_anonymization_parallel.py`; leaf README step 01. | "Prepare anonymization and PHI validation commands for this reports CSV." | `srun python 01_anonymization/anonymize_reports_parallel.py ...`; `srun python utils/validate_anonymization_parallel.py ...`. | Raw Turkish CSV with `AccessionNo`, `RaporText`; anonymized CSV with `Anonymized_Rapor`. | `anonymized_rank_{RANK}.csv`, `mapping_rank_{RANK}.csv`, `validation_rank_{RANK}.csv`. | Existing source scripts. | Explain token mapping, PHI gates, resume behavior. | Medium risk; raw reports and mappings may contain PHI; do not quote or publish. | No public fixture; smoke by schema/command review only. | make-skill-now |
| `mrrate-report-translation-qc` | Plans translation, translation QC, Turkish detection, and retranslation. | Translation has its own QC/retry loop and distinct columns. | `02_translation/translate_reports_parallel.py`; `03_translation_qc/*.py`; leaf README steps 02-03. | "Detect remaining Turkish translations and prepare retranslation commands." | `srun python 02_translation/...`; `srun python 03_translation_qc/...`. | `Anonymized_Rapor`; QC columns `turkish_anonymized_report`, `english_anonymized_report`; detection file. | `translated_rank`, `qc_rank`, `detect_rank`, `retranslate_rank` CSVs. | Existing source scripts. | Explain conservative QC, remaining-Turkish detection, manual review. | Medium risk; translated reports remain sensitive; model access may download/cache. | No public fixture; smoke by required-column checklist. | make-skill-now |
| `mrrate-report-structuring-qc` | Plans four-section extraction and structure QC. | Structuring has parse failures, no-think fallback, and separate verification semantics. | `04_structuring/*.py`; `05_structure_qc/*.py`; leaf README steps 04-05. | "Structure translated reports and plan no-think fallback for parse failures." | `srun python 04_structuring/...`; `srun python 05_structure_qc/...`. | `english_anonymized_report`; structured fields and `parse_status`. | `structure_rank_{RANK}.csv`; `qc_rank_{RANK}.csv`. | Existing source scripts. | Explain formatting rules, parse status, false-positive review patterns. | Medium risk; do not invent clinical content or expose report text. | No public fixture; smoke by status-column merge and command review. | make-skill-now |
| `mrrate-report-pathology-labeling` | Plans 37-label pathology classification and label JSON merge. | The label ontology and CoT/JSON/verification loop are specialized and high consequence. | `06_pathology_classification/classify_pathologies_parallel.py`; `merge_labels.py`; `data/pathologies.json`; `data/pathologies_snomed_map.json`; leaf README step 06. | "Classify structured reports and merge labels_rank JSON files." | `srun python 06_pathology_classification/classify_pathologies_parallel.py ...`; `python 06_pathology_classification/merge_labels.py ...`. | Reports directory with `batch{NN}_reports.csv`; `pathologies.json`; output directory. | `labels_rank_{rank}.json`; `labels.csv`. | Existing source scripts. | Explain research-label caveats, label provenance, verification stats. | Medium risk; labels are research artifacts, not clinical truth. | No public fixture; smoke by ontology load and merge command review. | make-skill-now |
| `mrrate-report-shard-operations` | Merges and summarizes per-rank CSV and label JSON outputs. | Every source stage writes shards; deterministic merge is low risk and reusable. | `utils/merge_shards.py`; `06_pathology_classification/merge_labels.py`; leaf README parallel execution section. | "Merge structure_rank shards and summarize parse_status." | `python utils/merge_shards.py ...`; `python 06_pathology_classification/merge_labels.py ...`. | Shard directory, output path, optional prefix/dedup column; label JSON directory. | Merged CSV, status distribution, labels CSV. | Existing source merge scripts. | Explain safe overwrite checks and downstream handoff. | Low risk, but shard content may be sensitive; do not delete shards without approval. | Can smoke-test with synthetic CSV shards in future. | make-skill-now |

## Deferred Candidates

- A runnable adapter package was deferred. The source scripts already expose
  CLIs, but the SkillForge skill family currently documents and routes those
  commands rather than wrapping them. A future adapter could add schema checks,
  dry-run validation, synthetic shard fixtures, and safe overwrite guards.
- A separate "manual review workbench" skill was deferred. The source README
  describes manual review patterns, but the repo does not include a review UI,
  sample fixtures, or deterministic review helpers.
