---
name: mr-rate-data-curator
owner: medatasci
description: Use this skill when the user wants to curate or query the gated MR-RATE Hugging Face dataset in a local SQLite database. Use for authenticated reports, pathology labels, metadata, and explicitly approved MRI batch downloads; browser-authenticated Hugging Face access through the persistent NVIDIA Chrome session; source provenance checks; source-file status; importing MR-RATE source batches into research-data/mr-rate.sqlite; and read-only natural-language SQL queries using helper views and descriptor tables.
title: MR-RATE Data Curator
short_description: Curate gated MR-RATE source CSVs and explicitly approved MRI batches into a local SQLite database with provenance.
expanded_description: Use this skill for the MR-RATE local curation workflow that downloads gated source reports, pathology labels, metadata, and optionally MRI batch files from Hugging Face, then imports them into a workspace SQLite database. The skill wraps a restartable local orchestrator, expects project-local MR-RATE curation tools, preserves source provenance, uses explicit approval gates for browser-authenticated downloads, large MRI data, and database writes, and supports read-only SQL queries against helper views and LLM descriptor tables when a curated database exists.
aliases:
  - MR-RATE SQLite database
  - MR-RATE data curator
  - MR-RATE source import
  - MR-RATE reports SQLite
  - MR-RATE Hugging Face curation
  - MR-RATE natural language SQL
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
  - helper-views
  - natural-language-query
  - research-only
tasks:
  - curate MR-RATE source data into SQLite
  - download MR-RATE report label and metadata CSVs
  - import MR-RATE batches into a local database
  - inspect MR-RATE local source provenance
  - query MR-RATE helper views and descriptor tables
  - answer MR-RATE descriptive statistics with SQL
  - plan explicitly approved MRI batch downloads
use_when:
  - The user wants to build or refresh a local `research-data/mr-rate.sqlite` database.
  - The user needs authenticated MR-RATE reports, labels, or metadata downloaded from Hugging Face.
  - The user asks for source provenance, local source status, batch import status, or SQLite table coverage.
  - The user asks natural-language questions about MR-RATE counts, cohorts, pathologies, metadata, or patient/study summaries from the local database.
  - The user explicitly approves MRI batch download planning and storage checks.
do_not_use_when:
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
  - verification query or table coverage summary
  - read-only SQL and natural-language query result summaries
examples:
  - Use mr-rate-data-curator to show local MR-RATE source and SQLite status without downloading anything.
  - Curate batch01 MR-RATE reports, labels, and metadata into SQLite after I confirm browser access.
  - Use mr-rate-data-curator to answer how many linked patients have infarction, using helper views and showing the SQL.
  - Plan an all-batch MR-RATE reports and metadata refresh, but defer labels until the end.
  - Check what approval and disk-space information you need before downloading MR-RATE MRI archives.
related_skills:
  - open-nvidia-chrome
  - mrrate-dataset-access
  - mrrate-repository-guide
  - mrrate-report-preprocessing
  - mrrate-medical-workflow-reviewer
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
When a curated database exists, it can also run read-only SQL queries and use
LLM descriptor tables to choose helper views for natural-language questions.

By default, curation scope is the official MR-RATE Hugging Face dataset at
`Forithmus/MR-RATE`: `reports/`, `pathology_labels/`, and `metadata/`. Local
derived analysis CSVs and MRI archives are opt-in.

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
6. Use read-only SQLite mode for query-only requests.
7. Keep raw reports, study identifiers, metadata rows, and database contents out
   of public artifacts unless the user explicitly requests a private local
   inspection.

## Quick Decision Guide

| User intent | Preferred path |
| --- | --- |
| Check local curation state | Run the bundled `status` command or inspect source paths read-only. |
| Download reports, labels, and metadata | Confirm authenticated Chrome, batches, source groups, and write approval. |
| Refresh all batches | Use `--batches all --groups reports,labels,metadata --defer-labels` after approval. |
| Import already-downloaded sources | Use the `import` command with the selected batches and label policy. |
| Answer descriptive statistics | Inspect query descriptors, choose the count unit, then use helper views. |
| Review a patient or study privately | Query concise summaries first; avoid dumping full raw report text. |
| Download MRI archives | Stop for explicit scope, disk-space, archive-retention, and extraction/indexing approval. |

## SkillForge Discovery Metadata

### Title

MR-RATE Data Curator

### Short Description

Curate gated MR-RATE source CSVs and explicitly approved MRI batches into a
local SQLite database with provenance.

### Expanded Description

Use this skill for the MR-RATE local curation workflow that downloads gated
source reports, pathology labels, metadata, and optionally MRI batch files from
Hugging Face, then imports them into a workspace SQLite database. The skill
wraps a restartable local orchestrator, expects project-local MR-RATE curation
tools, preserves source provenance, and uses explicit approval gates for
browser-authenticated downloads, large MRI data, and database writes.

### Aliases

- MR-RATE SQLite database
- MR-RATE data curator
- MR-RATE source import
- MR-RATE reports SQLite
- MR-RATE Hugging Face curation

### Categories

- Medical Imaging
- Data Engineering
- Data Access
- Research

### Tags

- mr-rate
- sqlite
- hugging-face
- gated-dataset
- reports
- pathology-labels
- metadata
- provenance
- research-only

### Tasks

- curate MR-RATE source data into SQLite
- download MR-RATE report label and metadata CSVs
- import MR-RATE batches into a local database
- inspect MR-RATE local source provenance
- query MR-RATE helper views and descriptor tables
- answer MR-RATE descriptive statistics with SQL
- plan explicitly approved MRI batch downloads

### Use When

- The user wants to build or refresh a local `research-data/mr-rate.sqlite`
  database.
- The user needs authenticated MR-RATE reports, labels, or metadata downloaded
  from Hugging Face.
- The user asks for source provenance, local source status, batch import status,
  or SQLite table coverage.
- The user asks natural-language questions about MR-RATE counts, cohorts,
  pathologies, metadata, or patient/study summaries from the local database.
- The user explicitly approves MRI batch download planning and storage checks.

### Do Not Use When

- The user wants general MR-RATE dataset download planning without SQLite
  import; use `mrrate-dataset-access`.
- The user wants to bypass MR-RATE gated dataset access or copy browser
  credentials.
- The user wants model training or inference; use the contrastive MR-RATE skills
  after curated data exists.
- The user wants raw report text, patient-level artifacts, or database exports
  published in public artifacts.

### Inputs

- MR-RATE curation workspace path
- batch selector such as `01`, `00,01`, `batch01`, or `all`
- source groups such as `reports`, `labels`, `metadata`, and explicitly
  approved `mri`
- browser DevTools endpoint for the persistent authenticated Chrome session
- approval for network downloads, database writes, and large-data MRI scope

### Outputs

- download and import command plan
- downloaded source CSV files under `research-data/sources/mr-rate/`
- local SQLite database at `research-data/mr-rate.sqlite`
- source provenance and status summary
- verification query or table coverage summary
- read-only SQL and natural-language query result summaries

### Examples

- Use mr-rate-data-curator to show local MR-RATE source and SQLite status
  without downloading anything.
- Curate batch01 MR-RATE reports, labels, and metadata into SQLite after I
  confirm browser access.
- Use mr-rate-data-curator to answer how many linked patients have infarction,
  using helper views and showing the SQL.
- Plan an all-batch MR-RATE reports and metadata refresh, but defer labels until
  the end.
- Check what approval and disk-space information you need before downloading
  MR-RATE MRI archives.

### Related Skills

- open-nvidia-chrome
- mrrate-dataset-access
- mrrate-repository-guide
- mrrate-report-preprocessing
- mrrate-medical-workflow-reviewer

### Authoritative Sources

- MR-RATE dataset: https://huggingface.co/datasets/Forithmus/MR-RATE
- MR-RATE source repository: https://github.com/forithmus/MR-RATE
- Local curation orchestrator: `scripts/curate_mr_rate_data.py`
- Local source layout reference: `references/source-layout.md`
- SQLite query interface reference: `references/sqlite-query-interface.md`

### Citations

- Forithmus MR-RATE dataset and repository.
- Creative Commons BY-NC-SA 4.0 dataset terms where applicable.

### Risk Level

high

### Permissions

- read local MR-RATE curation workspace files and source status
- use the persistent authenticated browser DevTools endpoint only after approval
- write downloaded source files and a local SQLite database after approval
- do not copy browser profiles, export cookies, bypass gated access, or publish
  raw medical data

### Page Title

MR-RATE Data Curator Skill - Local SQLite Curation for Gated MR-RATE Sources

### Meta Description

Use the MR-RATE Data Curator Skill to download authenticated MR-RATE reports,
labels, and metadata into a local SQLite database with provenance and approval
gates.

## Workflow

1. Confirm the MR-RATE curation workspace and available project-local tools.
2. Confirm source scope: batches, source groups, and whether MRI is excluded or
   explicitly approved.
3. For authenticated downloads, use `open-nvidia-chrome` first and keep the
   persistent Chrome session open.
4. Use the bundled orchestrator for `status`, `download`, `import`, or `run`.
5. After import, verify `source_files`, `upstream_sources`, and relevant table
   counts without printing raw report text.
6. For natural-language questions, inspect the LLM query dictionary, decide the
   counting unit, and run read-only SQL against helper views.
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

For read-only database questions, use the bundled `query` command. If the
database contains LLM descriptor tables, inspect `--describe intents`,
`--describe views`, and `--describe examples` before drafting SQL. Read
`references/sqlite-query-interface.md` for the expected helper views and
natural-language query ritual.

## Inputs

- Workspace root containing the MR-RATE curation tools.
- Batch selector: `01`, `00,01`, `batch01`, or `all`.
- Source groups: `reports`, `labels`, `metadata`, and explicitly approved
  `mri`.
- Optional Python, Node, CDP endpoint, wait seconds, dry-run, and defer-labels
  settings.
- Optional `--include-derived` when the user explicitly wants local derived
  analysis CSVs added to the database.
- Optional read-only SQL, SQL file, descriptor kind, output format, and display
  limit for query-only work.

## Outputs

- Local source files under `research-data/sources/mr-rate/`.
- Local SQLite database at `research-data/mr-rate.sqlite`.
- Status JSON and verification summaries.
- Command plan with approval gates.
- SQL text and summarized query results for local read-only analysis.

## Boundaries

- Do not bypass Hugging Face gated access.
- Do not copy browser profiles, export cookies, or expose tokens.
- Do not download MRI data by default.
- Do not import local derived analysis CSVs by default.
- Do not publish raw reports, patient-level metadata, source rows, SQLite
  extracts, or local sensitive paths.
- Do not infer a count unit silently; state whether a result counts linked
  patients, studies, reports, label rows, or metadata series.
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
python scripts/curate_mr_rate_data.py query --workspace . --describe examples
python scripts/curate_mr_rate_data.py run --workspace . --batches 01 --groups reports,labels,metadata
python scripts/curate_mr_rate_data.py run --workspace . --batches all --groups reports,labels,metadata --defer-labels
```

When installed into Codex, resolve the script from the installed skill folder
rather than hard-coding a machine-specific path.

## Examples

```text
Use mr-rate-data-curator to show MR-RATE curation status for this workspace.
Do not download or import anything yet.
```

```text
Use mr-rate-data-curator to curate batch01 reports, labels, and metadata into
SQLite after I confirm the authenticated Chrome session is ready.
```

```text
Use mr-rate-data-curator to plan an all-batch metadata and reports refresh.
Defer labels until the end and do not include MRI.
```

```text
Use mr-rate-data-curator to answer how many linked patients have infarction.
Inspect helper-view descriptors first, run read-only SQL, and tell me the SQL.
```
