---
name: mrrate-database-analysis
owner: medatasci
description: Use this skill when the user wants read-only analysis of a local MR-RATE SQLite database. Use for natural-language SQL questions, helper views, descriptor tables, schema docs, descriptive statistics, cohort counts, pathology prevalence, metadata coverage, co-occurrence summaries, private patient/study record previews, and requests to show the SQL used. Do not use for downloading, importing, refreshing, or building the database; use mr-rate-data-curator for that.
title: MR-RATE Database Analysis
short_description: Analyze the local MR-RATE SQLite database with read-only SQL, helper views, descriptor tables, and count-unit-aware summaries.
expanded_description: Use this skill to answer local MR-RATE database questions after a curated SQLite database exists. It guides Codex to inspect LLM descriptor tables, choose the correct counting unit, prefer helper views, run read-only SQL, show the SQL, and summarize results without publishing raw reports, patient-level exports, local paths, or PHI-sensitive artifacts.
aliases:
  - MR-RATE database analysis
  - MR-RATE SQLite analysis
  - MR-RATE SQL query
  - MR-RATE helper views
  - MR-RATE descriptive statistics
  - MR-RATE cohort counts
categories:
  - Medical Imaging
  - Data Analysis
  - Research
tags:
  - mr-rate
  - sqlite
  - sql
  - helper-views
  - descriptive-statistics
  - cohort-analysis
  - metadata
  - pathology-labels
  - research-only
tasks:
  - query MR-RATE SQLite helper views
  - answer MR-RATE descriptive statistics with SQL
  - summarize pathology cohorts and metadata coverage
  - inspect patient and study records privately
  - publish schema guidance for Codex context
use_when:
  - The user asks natural-language questions about MR-RATE counts, cohorts, pathologies, metadata, patient summaries, study summaries, or scan metadata from the local database.
  - The user asks to show SQL, helper views, schema, descriptor tables, query examples, or count-unit guidance for MR-RATE SQLite.
  - The user asks how many patients, studies, reports, label rows, or metadata series match an MR-RATE condition.
  - The user wants a private local preview of records linked to a pathology or metadata filter.
do_not_use_when:
  - The user wants to download, import, build, refresh, or verify source files for the database; use `mr-rate-data-curator`.
  - The user wants general MR-RATE dataset access planning without SQLite analysis; use `mrrate-dataset-access`.
  - The user wants model training or inference; use the contrastive MR-RATE skills.
  - The user wants raw reports, patient-level exports, or local database extracts published in public artifacts.
inputs:
  - workspace path or SQLite database path
  - natural-language database question or SQL
  - requested counting unit, filters, or output format
outputs:
  - read-only SQL statement
  - count-unit-aware result summary
  - caveats about linkage, missing metadata, and privacy
  - optional local CSV or JSON output only when explicitly requested
examples:
  - Use mrrate-database-analysis to answer how many patients have infarction, using helper views and showing the SQL.
  - Use mrrate-database-analysis to list the helper views and tell me when to use each one.
  - Show private local study summaries for Cerebral infarction without publishing raw reports.
  - Use mrrate-database-analysis to summarize field strength coverage for infarction studies and show the join SQL.
related_skills:
  - mr-rate-data-curator
  - mrrate-dataset-access
  - mrrate-medical-workflow-reviewer
  - mrrate-report-preprocessing
authoritative_sources:
  - MR-RATE dataset: https://huggingface.co/datasets/Forithmus/MR-RATE
  - MR-RATE source repository: https://github.com/forithmus/MR-RATE
  - Local MR-RATE SQLite helper views: `mr_rate_db/helper_views.sql`
  - Local MR-RATE LLM query descriptors: `mr_rate_db/query_descriptors.sql`
  - Local query helper: `tools/query_mr_rate_db.py`
citations:
  - Forithmus MR-RATE dataset and repository.
  - Creative Commons BY-NC-SA 4.0 dataset terms where applicable.
risk_level: high
permissions:
  - read local SQLite databases and generated schema docs
  - run read-only SQL against local MR-RATE helper views and descriptor tables
  - write no files unless explicitly requested for a private local export
  - do not publish raw reports, patient-level rows, local paths, or private database contents
page_title: MR-RATE Database Analysis Skill - Read-Only SQLite SQL And Helper Views
meta_description: Use the MR-RATE Database Analysis Skill to answer local MR-RATE SQLite questions with helper views, descriptor tables, count-unit-aware SQL, and privacy safeguards.
---

# MR-RATE Database Analysis

## What This Skill Does

Use this skill to analyze an already-curated local MR-RATE SQLite database. It
answers descriptive statistics, cohort, pathology, metadata, and private record
summary questions with read-only SQL.

This skill is deliberately separate from `mr-rate-data-curator`. Curation builds
or refreshes `research-data/mr-rate.sqlite`; database analysis reads that file
and translates user questions into helper-view SQL.

## Authoritative Sources

- MR-RATE dataset: https://huggingface.co/datasets/Forithmus/MR-RATE
- MR-RATE source repository: https://github.com/forithmus/MR-RATE
- Local MR-RATE SQLite helper views: `mr_rate_db/helper_views.sql`
- Local MR-RATE LLM query descriptors: `mr_rate_db/query_descriptors.sql`
- Local query helper: `tools/query_mr_rate_db.py`

## Safe Default Behavior

1. Confirm the database path, usually `research-data/mr-rate.sqlite`.
2. Inspect descriptor tables before drafting natural-language SQL when they are
   present.
3. Choose and state the counting unit: linked patients, studies, reports,
   positive label rows, or metadata series.
4. Prefer helper views over raw tables.
5. Open SQLite in read-only mode.
6. Tell the user the SQL that was run.
7. Summarize results without publishing raw reports, full patient rows, local
   private paths, or database extracts.

## Quick Decision Guide

| User intent | Preferred path |
| --- | --- |
| How many patients/studies/reports have a pathology? | Use `v_query_pathology_stats` or a pathology-specific helper view. |
| Show records for a pathology | Start with concise patient/study helper views and preview only what is needed. |
| Summarize scan metadata coverage | Use `v_query_metadata_series` or `v_query_sequence_stats`. |
| Explain which view to use | Query `llm_query_view_catalog`, `llm_query_intent_catalog`, and `llm_query_examples`. |
| Build or refresh the DB | Use `mr-rate-data-curator`. |

## Workflow

1. Resolve the workspace and database path.
2. Run `--describe intents`, `--describe views`, or `--describe examples` if
   the user asks a natural-language question.
3. Draft SQL using helper views and an explicit count unit.
4. Execute the SQL with `scripts/query_mr_rate_db.py` in read-only mode.
5. Report the SQL, result, counting unit, and caveats.
6. For record previews, keep output concise and local/private.

## Bundled Query Command

```text
scripts/query_mr_rate_db.py
```

Useful commands:

```text
python scripts/query_mr_rate_db.py --workspace . --describe intents
python scripts/query_mr_rate_db.py --workspace . --describe views
python scripts/query_mr_rate_db.py --workspace . --describe examples
python scripts/query_mr_rate_db.py --workspace . "SELECT COUNT(*) AS patients FROM v_query_patient_summary;"
```

The command supports:

- positional SQL
- `--workspace`
- `--db`
- `--sql-file`
- `--describe views|columns|intents|rules|examples`
- `--format table|json|csv`
- `--limit`

## References

Read these only when needed:

- `references/sqlite-query-interface.md`: helper views, descriptor tables, and
  example SQL patterns.
- `references/source-context-map.md`: source context for the analysis skill and
  its relationship to curation.

## Boundaries

- Do not write to the database.
- Do not infer a count unit silently.
- Do not publish raw reports, full patient rows, source rows, local sensitive
  paths, or database exports.
- Do not claim MR-RATE labels or derived summaries are clinical truth.
- Do not use this skill to download, import, or refresh source data; route that
  to `mr-rate-data-curator`.
