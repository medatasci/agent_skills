# MR-RATE Data Curator

Skill ID: `mrrate-data-curator`

Curate gated MR-RATE source reports, pathology labels, and metadata into a
local SQLite database with source provenance, explicit approval gates, and
safe handling of sensitive research artifacts.

Use `mrrate-database-analysis` when the database already exists and the user
wants read-only SQL, helper views, descriptive statistics, cohort counts,
metadata coverage, or private record review.

## Repo And Package

Skill repo URL:
https://github.com/medatasci/agent_skills/tree/main/skills/mrrate-data-curator

Parent package:
SkillForge Agent Skills Marketplace

Parent package repo URL:
https://github.com/medatasci/agent_skills

Distribution or marketplace:
SkillForge local catalog and Codex skill install workflow

Version or release channel:
Repository `main` branch when published

## Parent Collection

Parent collection:
MR-RATE Skill Collection

Collection URL:
https://github.com/medatasci/agent_skills/tree/main/collections/MR-RATE

Categories:
Medical Imaging, Data Engineering, Data Access, Research

Collection context:
This skill is the local SQLite curation branch of the MR-RATE skill family. It
turns authenticated official source files into a workspace database that
analysis, review, preprocessing, and model-research skills can use later.

## What This Skill Does

This skill helps Codex curate MR-RATE source data from Hugging Face into a
workspace database at `research-data/mr-rate.sqlite`. It can plan and run a
bundled orchestrator for local source status, reports/labels/metadata
downloads, import into SQLite, and post-import verification.

It is intentionally cautious. MR-RATE is gated medical-imaging research data,
and report text, identifiers, metadata, database rows, browser-authenticated
access, and local paths should be treated as sensitive research artifacts.
By default, curation scope is the official `Forithmus/MR-RATE` Hugging Face
dataset: `reports/`, `pathology_labels/`, and `metadata/`. MRI archives and
local derived analysis CSVs are opt-in.

## Why You Would Call It

Call this skill when:

- You want to build or refresh a local MR-RATE SQLite database.
- You need authenticated MR-RATE reports, labels, or metadata downloaded from
  Hugging Face into a local workspace.
- You want to inspect source-file status, database presence, row counts, or
  provenance.
- You need to plan MRI batch handling, but only after explicit storage and
  scope approval.

Use it to:

- Normalize batch selectors such as `1`, `01`, `batch01`, `00,01`, or `all`.
- Run reports, labels, and metadata downloads through a persistent
  authenticated Chrome DevTools session.
- Import downloaded sources into SQLite with source-file tracking.
- Produce verification summaries without printing raw report text.
- Keep official-source scope separate from opt-in MRI or local derived files.

Do not use it when:

- You want read-only SQL analysis, helper views, descriptive statistics, cohort
  counts, metadata coverage, or natural-language database questions. Use
  `mrrate-database-analysis`.
- You only need general MR-RATE dataset download planning without SQLite import.
- You want to bypass gated access, copy browser profiles, export cookies, or
  expose credentials.
- You want to train or run inference after data is already available.
- You want to publish raw reports, patient-level metadata, local database
  extracts, or private local paths.

## Keywords

MR-RATE, SQLite, Hugging Face, gated dataset, reports, metadata, pathology
labels, curation, source provenance, research-data, browser-authenticated
download, Chrome DevTools, local database build.

## Search Terms

MR-RATE data curator, build MR-RATE database, MR-RATE source import, download
MR-RATE reports into SQLite, import MR-RATE metadata, MR-RATE pathology labels
SQLite, curate gated Hugging Face data, MR-RATE source provenance, refresh
MR-RATE SQLite database.

## How It Works

The skill wraps `scripts/curate_mr_rate_data.py`. The orchestrator expects a
workspace that contains the project-local tools used by the MR-RATE curation
workflow:

- `tools/browser_download_mr_rate_batch.js`
- `tools/build_mr_rate_db.py`

The workflow is:

1. Confirm the workspace path and available local tools.
2. Confirm batches and source groups.
3. Use `open-nvidia-chrome` first for browser-authenticated Hugging Face
   downloads.
4. Run `status`, `download`, `import`, or `run` through the orchestrator.
5. Verify `source_files`, `upstream_sources`, and table counts without exposing
   raw report text or patient-level rows.
6. Route read-only database analysis to `mrrate-database-analysis`.
7. Summarize provenance, local files, database status, approvals, and remaining
   gaps.

The default source groups are `reports`, `labels`, and `metadata`. MRI is
available only as an explicit opt-in source group because archives are large
and require separate storage, retention, extraction, and indexing decisions.

## Authoritative Sources

- MR-RATE dataset: https://huggingface.co/datasets/Forithmus/MR-RATE
- MR-RATE source repository: https://github.com/forithmus/MR-RATE
- MR-RATE dataset guide: `data-preprocessing/docs/dataset_guide.md`
- Local browser download helper: `tools/browser_download_mr_rate_batch.js`
- Local database builder: `tools/build_mr_rate_db.py`
- Local curation orchestrator: `scripts/curate_mr_rate_data.py`

## API And Options

SkillForge catalog commands:

```text
python -m skillforge search "MR-RATE database builder" --json
python -m skillforge info mrrate-data-curator --json
python -m skillforge evaluate mrrate-data-curator --json
```

Bundled orchestrator commands:

```text
python scripts/curate_mr_rate_data.py status --workspace .
python scripts/curate_mr_rate_data.py run --workspace . --batches 01 --groups reports,labels,metadata
python scripts/curate_mr_rate_data.py run --workspace . --batches all --groups reports,labels,metadata --defer-labels
python scripts/curate_mr_rate_data.py download --workspace . --batches all --groups reports,labels,metadata
python scripts/curate_mr_rate_data.py import --workspace . --batches all --defer-labels
```

Important options:

- `--workspace`: MR-RATE curation workspace root.
- `--batches`: comma-separated batches or `all`.
- `--groups`: `reports`, `labels`, `metadata`, and explicitly approved `mri`.
- `--cdp-url`: authenticated persistent Chrome DevTools endpoint.
- `--defer-labels`: import labels once after selected batches are loaded.
- `--download-dry-run`: pass dry-run mode to the browser downloader.
- `--command-dry-run`: print commands without executing them.
- `--include-derived`: also import local derived analysis CSVs on the first
  import batch.
- `--skip-derived`: compatibility flag; local derived analysis CSVs are skipped
  unless `--include-derived` is set.

## Inputs And Outputs

Inputs can include:

- MR-RATE curation workspace path.
- Batch selector such as `01`, `00,01`, `batch01`, or `all`.
- Source group selection.
- Authenticated Chrome DevTools endpoint.
- Explicit approval for downloads, database writes, and MRI scope.

Outputs can include:

- Download/import command plan.
- Source CSVs under `research-data/sources/mr-rate/`.
- SQLite database at `research-data/mr-rate.sqlite`.
- Status JSON or verification summary.
- Source provenance table coverage.

Output locations:

- Local source root: `research-data/sources/mr-rate/`
- Local database: `research-data/mr-rate.sqlite`
- Optional generated schema guide: `docs/schema/schema.md`

## Limitations

Known limitations:

- The skill does not grant gated MR-RATE access.
- The bundled orchestrator depends on project-local curation tools that are not
  part of the MR-RATE upstream repository.
- Browser-authenticated downloads require the persistent Chrome session to be
  open and reachable.
- MRI archives are large and are never downloaded by default.
- Local derived analysis CSVs are not part of the default official dataset
  scope and require `--include-derived`.
- The skill should summarize status and counts, not publish raw source rows.

Choose another skill when:

- You need database analysis: use `mrrate-database-analysis`.
- You only need general MR-RATE dataset download planning: use
  `mrrate-dataset-access`.
- You need report preprocessing workflow guidance: use
  `mrrate-report-preprocessing`.
- You need training or inference: use the contrastive MR-RATE skills.

## Examples

Beginner example:

```text
Use mrrate-data-curator to show whether this workspace has an MR-RATE SQLite database.
Do not download or import anything yet.
```

Task-specific example:

```text
Use mrrate-data-curator to curate batch01 reports, pathology labels, and metadata into SQLite.
I approve local database writes, but do not download MRI.
```

Safety-aware or bounded example:

```text
Plan an all-batch MR-RATE metadata and reports refresh. Use command-dry-run first,
defer labels until the end, and do not print raw report text.
```

Troubleshooting or refinement example:

```text
The MR-RATE download returned a Git LFS pointer. Use mrrate-data-curator to explain the retry path.
```

## Help And Getting Started

Start with:

```text
Use mrrate-data-curator to check MR-RATE curation status in this workspace.
```

Provide:

- The workspace root.
- Desired batches and source groups.
- Whether downloads and database writes are approved.

Ask for help when:

- Hugging Face returns `401`.
- Chrome DevTools is not reachable.
- Downloaded CSVs look like Git LFS pointer files.
- Labels are slow or repeated across batches.

## How To Call From An LLM

Direct prompt:

```text
Use mrrate-data-curator to inspect MR-RATE SQLite build status.
```

Task-based prompt:

```text
Use mrrate-data-curator to download and import batch01 reports, labels, and metadata into SQLite after confirming Chrome authentication.
```

Guarded prompt:

```text
Use mrrate-data-curator, but do not download MRI, do not print raw reports, and ask before writing the database.
```

Find or install prompt:

```text
Find and install the SkillForge skill that helps build a local MR-RATE SQLite database.
Ask before installing anything from a peer catalog.
```

## How To Call From The CLI

Search for the skill:

```text
python -m skillforge search "MR-RATE database builder" --json
```

Show skill metadata:

```text
python -m skillforge info mrrate-data-curator --json
```

Install the skill into Codex:

```text
python -m skillforge install mrrate-data-curator --scope global
```

Evaluate the skill before publishing changes:

```text
python -m skillforge evaluate mrrate-data-curator --json
```

Run the bundled status command from an installed skill folder:

```text
python scripts/curate_mr_rate_data.py status --workspace .
```

## Trust And Safety

Risk level:
High

Permissions:

- Reads local workspace files and MR-RATE source status.
- Uses browser-authenticated Hugging Face access only after approval.
- Writes downloaded source files and SQLite databases after approval.
- Does not copy browser profiles, export cookies, bypass access controls, or
  publish raw medical data.

Data handling:
Treat reports, pathology labels, metadata, source rows, study identifiers,
database rows, and local paths as sensitive research artifacts.

Writes vs read-only:
Status is read-only. Downloads and imports are side-effectful and require
explicit user approval. Database analysis belongs in `mrrate-database-analysis`.

External services:
Hugging Face gated dataset access through an authenticated browser session.

Credentials:
The skill uses an existing authenticated browser session when approved. It must
not expose cookies, tokens, passwords, or browser-profile contents.

User approval gates:

- Browser-authenticated downloads.
- Database writes or refreshes.
- MRI download, extraction, indexing, or archive retention.
- Any public artifact that could include source rows, reports, identifiers, or
  local private paths.

## Feedback

Feedback URL:
https://github.com/medatasci/agent_skills/issues

Send feedback when:

- Batch handling is unclear.
- Source provenance checks miss useful evidence.
- The workflow needs safer MRI archive handling.

Promptable feedback:

```text
Send feedback on mrrate-data-curator that the status output should summarize table counts.
```

## Contributing

Contribution path:
Open a pull request against `medatasci/agent_skills`.

Before opening a pull request:

- Update `SKILL.md`, this `README.md`, scripts, and references together.
- Run `python -m skillforge build-catalog --json`.
- Run `python -m skillforge evaluate mrrate-data-curator --json`.

## Author

medatasci

Maintainer status:
Source-informed SkillForge skill maintained with the MR-RATE skill family.

## Citations

- MR-RATE source repository: https://github.com/forithmus/MR-RATE
- MR-RATE dataset: https://huggingface.co/datasets/Forithmus/MR-RATE
- Creative Commons BY-NC-SA 4.0: https://creativecommons.org/licenses/by-nc-sa/4.0/

## Related Skills

- `open-nvidia-chrome`: prepares the authenticated browser session.
- `mrrate-database-analysis`: analyzes the local SQLite database with read-only
  SQL and helper views.
- `mrrate-dataset-access`: plans general MR-RATE dataset downloads and layout.
- `mrrate-repository-guide`: routes whole-repo MR-RATE questions.
- `mrrate-report-preprocessing`: explains report preprocessing stages after
  source data is available.
- `mrrate-medical-workflow-reviewer`: reviews clinical-statistical consistency
  of curated datasets and workflows.
