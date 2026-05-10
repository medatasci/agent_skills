---
name: mrrate-data-curator
owner: medatasci
description: Use this skill when the user wants to curate the gated MR-RATE Hugging Face dataset into a local SQLite database. Use for authenticated reports, pathology labels, metadata, and explicitly approved MRI batch downloads; browser-authenticated Hugging Face access through the persistent NVIDIA Chrome session; source provenance checks; source-file status; importing official MR-RATE source batches into research-data/mr-rate.sqlite; and local database build/update planning. Do not use for read-only SQL analysis or natural-language database questions; use mrrate-database-analysis for that.
title: MR-RATE Data Curator
short_description: Curate gated MR-RATE source CSVs and explicitly approved MRI batches into a local SQLite database with provenance.
expanded_description: Use this skill for the MR-RATE local curation workflow that downloads gated source reports, pathology labels, metadata, and optionally MRI batch files from Hugging Face, then imports them into a workspace SQLite database. The skill wraps a restartable local orchestrator, expects project-local MR-RATE curation tools, preserves source provenance, and uses explicit approval gates for browser-authenticated downloads, large MRI data, and database writes. Use mrrate-database-analysis after a database exists when the task is descriptive statistics, helper-view SQL, cohort counts, metadata coverage, or private record review.
aliases:
  - mr-rate-data-curator
  - MR-RATE data curator
  - MR-RATE source import
  - MR-RATE reports SQLite build
  - MR-RATE Hugging Face curation
  - MR-RATE database builder
categories:
  - Medical Imaging
  - Data Engineering
  - Data Access
  - Research
tags:
  - mr-rate
  - sqlite
  - hugging-face
  - gated-dataset
  - reports
  - pathology-labels
  - metadata
  - provenance
  - data-curation
  - research-only
tasks:
  - curate MR-RATE source data into SQLite
  - download MR-RATE report label and metadata CSVs
  - import MR-RATE batches into a local database
  - inspect MR-RATE local source provenance
  - check MR-RATE source file and database build status
  - plan explicitly approved MRI batch downloads
use_when:
  - The user wants to build or refresh a local `research-data/mr-rate.sqlite` database.
  - The user needs authenticated MR-RATE reports, labels, or metadata downloaded from Hugging Face.
  - The user asks for source provenance, local source status, batch import status, or SQLite table coverage.
  - The user explicitly approves MRI batch download planning and storage checks.
do_not_use_when:
  - The user wants read-only SQL analysis, descriptive statistics, cohort counts, helper views, or natural-language questions against an existing database; use `mrrate-database-analysis`.
  - The user wants general MR-RATE dataset download planning without SQLite import; use `mrrate-dataset-access`.
  - The user wants to bypass MR-RATE gated dataset access or copy browser credentials.
  - The user wants model training or inference; use the contrastive MR-RATE skills after curated data exists.
  - The user wants raw report text, patient-level artifacts, or database exports published in public artifacts.
inputs:
  - MR-RATE curation workspace path
  - batch selector such as `01`, `00,01`, `batch01`, or `all`
  - source groups such as `reports`, `labels`, `metadata`, and explicitly approved `mri`
  - browser DevTools endpoint for the persistent authenticated Chrome session
  - approval for network downloads, database writes, and large-data MRI scope
outputs:
  - download and import command plan
  - downloaded source CSV files under `research-data/sources/mr-rate/`
  - local SQLite database at `research-data/mr-rate.sqlite`
  - source provenance and status summary
  - post-import table coverage summary
examples:
  - Use mrrate-data-curator to show local MR-RATE source and SQLite build status without downloading anything.
  - Curate batch01 MR-RATE reports, labels, and metadata into SQLite after I confirm browser access.
  - Plan an all-batch MR-RATE reports and metadata refresh, but defer labels until the end.
  - Check what approval and disk-space information you need before downloading MR-RATE MRI archives.
related_skills:
  - open-nvidia-chrome
  - mrrate-database-analysis
  - mrrate-dataset-access
  - mrrate-repository-guide
  - mrrate-report-preprocessing
  - mrrate-medical-workflow-reviewer
authoritative_sources:
  - MR-RATE dataset: https://huggingface.co/datasets/Forithmus/MR-RATE
  - MR-RATE source repository: https://github.com/forithmus/MR-RATE
  - MR-RATE dataset guide: `data-preprocessing/docs/dataset_guide.md`
  - Local browser download helper: `tools/browser_download_mr_rate_batch.js`
  - Local database builder: `tools/build_mr_rate_db.py`
citations:
  - Forithmus MR-RATE dataset and repository.
  - Creative Commons BY-NC-SA 4.0 dataset terms where applicable.
risk_level: high
permissions:
  - read local MR-RATE curation workspace files and source status
  - use the persistent authenticated browser DevTools endpoint only after approval
  - write downloaded source files and a local SQLite database after approval
  - do not copy browser profiles, export cookies, bypass gated access, or publish raw medical data
page_title: MR-RATE Data Curator Skill - Local SQLite Curation for Gated MR-RATE Sources
meta_description: Use the MR-RATE Data Curator Skill to download authenticated MR-RATE reports, labels, and metadata into a local SQLite database with provenance and approval gates.
---

# MR-RATE Data Curator

## What This Skill Does

Use this skill to curate gated MR-RATE source data from Hugging Face into a
local SQLite database. It supports source CSV downloads for reports, pathology
labels, and metadata, plus explicitly approved MRI batch planning. It then
orchestrates imports into `research-data/mr-rate.sqlite` with source provenance.

By default, curation scope is the official MR-RATE Hugging Face dataset at
`Forithmus/MR-RATE`: `reports/`, `pathology_labels/`, and `metadata/`. Local
derived analysis CSVs and MRI archives are opt-in.

Use `mrrate-database-analysis` after the database exists when the user wants
descriptive statistics, helper-view SQL, cohort counts, metadata coverage, or
private patient/study record review.

This is a local research-data workflow. It is not a clinical tool, does not
grant MR-RATE access, and must not publish raw reports, patient-level metadata,
browser credentials, model outputs, or PHI-sensitive artifacts.

## Safe Default Behavior

Default to read-only status and planning:

1. Inspect the workspace and source/database status when possible.
2. Ask before browser-authenticated downloads.
3. Ask before writing or refreshing `research-data/mr-rate.sqlite`.
4. Ask before any MRI download, archive retention, extraction, or indexing.
5. Skip local derived analysis CSVs unless the user explicitly requests them.
6. Keep raw reports, study identifiers, metadata rows, and database contents out
   of public artifacts unless the user explicitly requests a private local
   inspection through `mrrate-database-analysis`.

## Quick Decision Guide

| User intent | Preferred path |
| --- | --- |
| Check local curation state | Run the bundled `status` command or inspect source paths read-only. |
| Download reports, labels, and metadata | Confirm authenticated Chrome, batches, source groups, and write approval. |
| Refresh all batches | Use `--batches all --groups reports,labels,metadata --defer-labels` after approval. |
| Import already-downloaded sources | Use the `import` command with the selected batches and label policy. |
| Answer descriptive statistics | Use `mrrate-database-analysis`. |
| Review a patient or study privately | Use `mrrate-database-analysis`. |
| Download MRI archives | Stop for explicit scope, disk-space, archive-retention, and extraction/indexing approval. |

## Authoritative Sources

- MR-RATE dataset: https://huggingface.co/datasets/Forithmus/MR-RATE
- MR-RATE source repository: https://github.com/forithmus/MR-RATE
- MR-RATE dataset guide: `data-preprocessing/docs/dataset_guide.md`
- Local browser download helper: `tools/browser_download_mr_rate_batch.js`
- Local database builder: `tools/build_mr_rate_db.py`
- Local curation orchestrator: `scripts/curate_mr_rate_data.py`
- Local source layout reference: `references/source-layout.md`
- Curation source context map: `references/source-context-map.md`

## Workflow

1. Confirm the MR-RATE curation workspace and available project-local tools.
2. Confirm source scope: batches, source groups, and whether MRI is excluded or
   explicitly approved.
3. For authenticated downloads, use `open-nvidia-chrome` first and keep the
   persistent Chrome session open.
4. Use the bundled orchestrator for `status`, `download`, `import`, or `run`.
5. After import, verify `source_files`, `upstream_sources`, and relevant table
   counts without printing raw report text.
6. Hand off database analysis questions to `mrrate-database-analysis`.
7. Summarize downloaded paths, row counts, database location, approvals used,
   and remaining gaps.

## Method

The bundled orchestrator is:

```text
scripts/curate_mr_rate_data.py
```

It expects the target workspace to contain project-local MR-RATE curation tools:

- `tools/browser_download_mr_rate_batch.js`
- `tools/build_mr_rate_db.py`

The orchestrator normalizes batch names, supports `all` for official batches
`01` through `27`, uses reports/labels/metadata by default, and treats MRI and
local derived analysis CSVs as explicit opt-in source groups.

## Inputs

- Workspace root containing the MR-RATE curation tools.
- Batch selector: `01`, `00,01`, `batch01`, or `all`.
- Source groups: `reports`, `labels`, `metadata`, and explicitly approved
  `mri`.
- Optional Python, Node, CDP endpoint, wait seconds, dry-run, and defer-labels
  settings.
- Optional `--include-derived` when the user explicitly wants local derived
  analysis CSVs added to the database.

## Outputs

- Local source files under `research-data/sources/mr-rate/`.
- Local SQLite database at `research-data/mr-rate.sqlite`.
- Status JSON and verification summaries.
- Command plan with approval gates.
- Post-import table coverage summary.

## Boundaries

- Do not bypass Hugging Face gated access.
- Do not copy browser profiles, export cookies, or expose tokens.
- Do not download MRI data by default.
- Do not import local derived analysis CSVs by default.
- Do not publish raw reports, patient-level metadata, source rows, SQLite
  extracts, or local sensitive paths.
- Do not answer database analysis questions from this skill; route those to
  `mrrate-database-analysis`.
- Do not claim the curated database is clinically validated or suitable for
  diagnosis, treatment, triage, prognosis, or patient-care decisions.

## Runtime And Deployment Notes

The skill is a local Windows-friendly research workflow. It can run read-only
status checks without network access. Download commands require authenticated
Hugging Face access, a persistent Chrome DevTools endpoint, and explicit user
approval. Import commands write to the selected workspace.

Use generic runtime commands in public docs:

```text
python scripts/curate_mr_rate_data.py status --workspace .
python scripts/curate_mr_rate_data.py run --workspace . --batches 01 --groups reports,labels,metadata
python scripts/curate_mr_rate_data.py run --workspace . --batches all --groups reports,labels,metadata --defer-labels
```

When installed into Codex, resolve the script from the installed skill folder
rather than hard-coding a machine-specific path.

## Examples

```text
Use mrrate-data-curator to show MR-RATE curation status for this workspace.
Do not download or import anything yet.
```

```text
Use mrrate-data-curator to curate batch01 reports, labels, and metadata into
SQLite after I confirm the authenticated Chrome session is ready.
```

```text
Use mrrate-data-curator to plan an all-batch metadata and reports refresh.
Defer labels until the end and do not include MRI.
```
