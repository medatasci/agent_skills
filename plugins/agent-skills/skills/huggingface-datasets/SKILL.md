---
name: huggingface-datasets
description: Use this skill for Hugging Face Dataset Viewer API workflows that fetch subset/split metadata, paginate rows, search text, apply filters, download parquet URLs, and read size or statistics.
title: Hugging Face Dataset Viewer
short_description: Inspect Hugging Face datasets with read-only Dataset Viewer API calls for splits, rows, search, filters, parquet URLs, sizes, and statistics.
expanded_description: Use this skill when a user wants to inspect public or authorized Hugging Face dataset metadata without changing the dataset. It supports validation, config and split discovery, first-row previews, row pagination, text search, filter predicates, parquet URL discovery, dataset sizes, and column statistics.
aliases:
  - hf datasets
  - hugging face dataset viewer
  - huggingface dataset rows
  - dataset parquet URLs
  - hugging face splits
categories:
  - Data
  - AI/ML
  - Research
tags:
  - hugging-face
  - datasets
  - dataset-viewer
  - parquet
  - metadata
  - rows
tasks:
  - inspect Hugging Face dataset metadata
  - list dataset configs and splits
  - preview first rows from a dataset
  - paginate dataset rows
  - search or filter dataset rows
  - retrieve parquet URLs
  - get dataset size and statistics
use_when:
  - The user asks to inspect Hugging Face dataset metadata, splits, rows, filters, parquet files, or statistics.
  - The user needs read-only Dataset Viewer API calls for public or authorized datasets.
do_not_use_when:
  - The user wants to train a model, upload a dataset, edit a Hub repository, or run non-read-only Hugging Face operations.
  - The user needs private or gated dataset access but has not provided an appropriate token.
inputs:
  - Hugging Face dataset ID
  - optional config name
  - optional split name
  - optional row offset and length
  - optional search query or filter predicate
outputs:
  - dataset validity result
  - configs and splits
  - first rows or paginated rows
  - search or filter results
  - parquet URLs
  - size and statistics metadata
examples:
  - Use huggingface-datasets to list the configs and splits for stanfordnlp/imdb.
  - Use huggingface-datasets to preview rows from a Hugging Face dataset and summarize the columns.
  - Use huggingface-datasets to find parquet URLs for a dataset and explain what each split contains.
related_skills:
  - get-youtube-media
risk_level: low
permissions:
  - network access to datasets-server.huggingface.co
  - optional HF_TOKEN for private or gated datasets
page_title: Hugging Face Dataset Viewer Skill - Inspect Dataset Rows, Splits, Parquet URLs, and Metadata
meta_description: Install the Hugging Face Dataset Viewer Skill for Codex to inspect dataset splits, rows, filters, parquet URLs, sizes, and statistics with read-only API calls.
---

# Hugging Face Dataset Viewer

Use this skill to execute read-only Dataset Viewer API calls for dataset exploration and extraction.

## Core workflow

1. Optionally validate dataset availability with `/is-valid`.
2. Resolve `config` + `split` with `/splits`.
3. Preview with `/first-rows`.
4. Paginate content with `/rows` using `offset` and `length` (max 100).
5. Use `/search` for text matching and `/filter` for row predicates.
6. Retrieve parquet links via `/parquet` and totals/metadata via `/size` and `/statistics`.

## Defaults

- Base URL: `https://datasets-server.huggingface.co`
- Default API method: `GET`
- Query params should be URL-encoded.
- `offset` is 0-based.
- `length` max is usually `100` for row-like endpoints.
- Gated/private datasets require `Authorization: Bearer <HF_TOKEN>`.

## Dataset Viewer

- `Validate dataset`: `/is-valid?dataset=<namespace/repo>`
- `List subsets and splits`: `/splits?dataset=<namespace/repo>`
- `Preview first rows`: `/first-rows?dataset=<namespace/repo>&config=<config>&split=<split>`
- `Paginate rows`: `/rows?dataset=<namespace/repo>&config=<config>&split=<split>&offset=<int>&length=<int>`
- `Search text`: `/search?dataset=<namespace/repo>&config=<config>&split=<split>&query=<text>&offset=<int>&length=<int>`
- `Filter with predicates`: `/filter?dataset=<namespace/repo>&config=<config>&split=<split>&where=<predicate>&orderby=<sort>&offset=<int>&length=<int>`
- `List parquet shards`: `/parquet?dataset=<namespace/repo>`
- `Get size totals`: `/size?dataset=<namespace/repo>`
- `Get column statistics`: `/statistics?dataset=<namespace/repo>&config=<config>&split=<split>`
- `Get Croissant metadata (if available)`: `/croissant?dataset=<namespace/repo>`

Pagination pattern:

```bash
curl "https://datasets-server.huggingface.co/rows?dataset=stanfordnlp/imdb&config=plain_text&split=train&offset=0&length=100"
curl "https://datasets-server.huggingface.co/rows?dataset=stanfordnlp/imdb&config=plain_text&split=train&offset=100&length=100"
```

When pagination is partial, use response fields such as `num_rows_total`, `num_rows_per_page`, and `partial` to drive continuation logic.

Search/filter notes:

- `/search` matches string columns (full-text style behavior is internal to the API).
- `/filter` requires predicate syntax in `where` and optional sort in `orderby`.
- Keep filtering and searches read-only and side-effect free.

For CLI-based parquet URL discovery or SQL, use the `hf-cli` skill with `hf datasets parquet` and `hf datasets sql`.

## Creating and Uploading Datasets

Use one of these flows depending on dependency constraints.

Zero local dependencies (Hub UI):

- Create dataset repo in browser: `https://huggingface.co/new-dataset`
- Upload parquet files in the repo "Files and versions" page.
- Verify shards appear in Dataset Viewer:

```bash
curl -s "https://datasets-server.huggingface.co/parquet?dataset=<namespace>/<repo>"
```

Low dependency CLI flow (`npx @huggingface/hub` / `hfjs`):

- Set auth token:

```bash
export HF_TOKEN=<your_hf_token>
```

- Upload parquet folder to a dataset repo (auto-creates repo if missing):

```bash
npx -y @huggingface/hub upload datasets/<namespace>/<repo> ./local/parquet-folder data
```

- Upload as private repo on creation:

```bash
npx -y @huggingface/hub upload datasets/<namespace>/<repo> ./local/parquet-folder data --private
```

After upload, call `/parquet` to discover `<config>/<split>/<shard>` values for querying with `@~parquet`.

## Agent Traces

The Hub supports raw agent session traces from Claude Code, Codex, and Pi Agent. Upload them to Hugging Face Datasets as original JSONL files and the Hub can auto-detect the trace format, tag the dataset as `Traces`, and enable the trace viewer for browsing sessions, turns, tool calls, and model responses. Common local session directories:

- Claude Code: `~/.claude/projects`
- Codex: `~/.codex/sessions`
- Pi: `~/.pi/agent/sessions`

Default to private dataset repos because traces can contain prompts, file paths, tool outputs, secrets, or PII. Preserve the raw `.jsonl` files and nest them by project/cwd instead of uploading every session at the dataset root.

```bash
hf repos create <namespace>/<repo> --type dataset --private --exist-ok
hf upload <namespace>/<repo> ~/.codex/sessions codex/<project-or-cwd> --type dataset
```
