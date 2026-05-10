# MR-RATE Data Curator

Skill ID: `mr-rate-data-curator`

Curate gated MR-RATE source reports, pathology labels, and metadata into a
local SQLite database with source provenance, explicit approval gates, and
safe handling of sensitive research artifacts. When a curated database exists,
use the same skill for read-only natural-language SQL queries through helper
views and descriptor tables.

## Repo And Package

Skill repo URL:
https://github.com/medatasci/agent_skills/tree/main/skills/mr-rate-data-curator

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
turns authenticated source files into a workspace database that other MR-RATE
review, preprocessing, and model-research skills can reason about at an
aggregate or de-identified level.

## What This Skill Does

This skill helps Codex curate MR-RATE source data from Hugging Face into a
workspace database at `research-data/mr-rate.sqlite`. It can plan and run a
bundled orchestrator for local source status, reports/labels/metadata
downloads, import into SQLite, post-import verification, and read-only SQL
queries over the local database.

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
- You want Codex to answer descriptive statistics or cohort questions using
  helper SQL views and to show the SQL it ran.
- You need to plan MRI batch handling, but only after explicit storage and
  scope approval.

Use it to:

- Normalize batch selectors such as `1`, `01`, `batch01`, `00,01`, or `all`.
- Run reports, labels, and metadata downloads through a persistent
  authenticated Chrome DevTools session.
- Import downloaded sources into SQLite with source-file tracking.
- Produce verification queries without printing raw report text.
- Inspect LLM query descriptors before translating a natural-language question
  into SQL.
- Run read-only SQL against helper views for counts, cohorts, metadata coverage,
  and private local record previews.

Do not use it when:

- You only need general MR-RATE dataset download planning without SQLite import.
- You want to bypass gated access, copy browser profiles, export cookies, or
  expose credentials.
- You want to train or run inference after data is already available.
- You want to publish raw reports, patient-level metadata, local database
  extracts, or private local paths.

## Keywords

MR-RATE, SQLite, Hugging Face, gated dataset, reports, metadata, pathology
labels, curation, source provenance, research-data, browser-authenticated
download, Chrome DevTools, local database.

## Search Terms

MR-RATE SQLite database, MR-RATE data curator, MR-RATE source import, build
MR-RATE database, download MR-RATE reports into SQLite, import MR-RATE metadata,
MR-RATE pathology labels SQLite, curate gated Hugging Face data, MR-RATE helper
views, MR-RATE natural language SQL, MR-RATE pathology counts.

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
6. For natural-language database questions, inspect descriptor tables, decide
   the counting unit, and run read-only SQL against helper views.
7. Summarize provenance, local files, database status, SQL, counting unit, and
   remaining gaps.

The default source groups are `reports`, `labels`, and `metadata`. MRI is
available only as an explicit opt-in source group because archives are large
and require separate storage, retention, extraction, and indexing decisions.

## API And Options

SkillForge catalog commands:

```text
python -m skillforge search "MR-RATE SQLite database" --json
python -m skillforge info mr-rate-data-curator --json
python -m skillforge evaluate mr-rate-data-curator --json
```

Bundled orchestrator commands:

```text
python scripts/curate_mr_rate_data.py status --workspace .
python scripts/curate_mr_rate_data.py run --workspace . --batches 01 --groups reports,labels,metadata
python scripts/curate_mr_rate_data.py run --workspace . --batches all --groups reports,labels,metadata --defer-labels
python scripts/curate_mr_rate_data.py download --workspace . --batches all --groups reports,labels,metadata
python scripts/curate_mr_rate_data.py import --workspace . --batches all --defer-labels
python scripts/curate_mr_rate_data.py query --workspace . --describe intents
python scripts/curate_mr_rate_data.py query --workspace . --describe examples
python scripts/curate_mr_rate_data.py query --workspace . "SELECT COUNT(*) AS patients FROM v_query_patient_summary;"
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
- `query`: read-only SQLite query mode.
- `--db`: database path relative to the workspace or absolute.
- `--describe`: inspect `views`, `columns`, `intents`, `rules`, or `examples`
  from the LLM query descriptor tables.
- `--sql-file`: read query SQL from a file.
- `--format`: choose `table`, `json`, or `csv` output.
- `--limit`: table display limit for large query results.

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
- SQL statements and summarized read-only query results.

Output locations:

- Local source root: `research-data/sources/mr-rate/`
- Local database: `research-data/mr-rate.sqlite`
- Optional generated schema guide: `docs/schema/schema.md`

## Natural-Language Query Workflow

For query-only requests, use the `query` command and keep the database open in
read-only mode. Start by inspecting the query dictionary if the database has
the descriptor tables:

```text
python scripts/curate_mr_rate_data.py query --workspace . --describe intents
python scripts/curate_mr_rate_data.py query --workspace . --describe views
python scripts/curate_mr_rate_data.py query --workspace . --describe examples
```

Then choose the counting unit explicitly:

- linked patients
- studies
- reports
- positive label rows
- metadata series rows

Prefer helper views such as `v_query_pathology_stats`,
`v_query_patient_summary`, `v_query_study_summary`,
`v_query_infarction_cases`, and `v_query_metadata_series` before raw tables.
Tell the user the SQL and any linkage caveat.

Example:

```sql
SELECT COUNT(DISTINCT patient_id) AS patients_with_infarction
FROM v_query_infarction_cases
WHERE patient_id IS NOT NULL;
```

For richer examples, read
`references/sqlite-query-interface.md`.

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
- Helper views and descriptor tables require a workspace database built with
  the newer project schema.
- The skill should summarize status and counts, not publish raw source rows.

Choose another skill when:

- You only need general MR-RATE dataset download planning: use
  `mrrate-dataset-access`.
- You need report preprocessing workflow guidance: use
  `mrrate-report-preprocessing`.
- You need training or inference: use the contrastive MR-RATE skills.

## Examples

Beginner example:

```text
Use mr-rate-data-curator to show whether this workspace has an MR-RATE SQLite database.
Do not download or import anything yet.
```

Task-specific example:

```text
Use mr-rate-data-curator to curate batch01 reports, pathology labels, and metadata into SQLite.
I approve local database writes, but do not download MRI.
```

Safety-aware or bounded example:

```text
Plan an all-batch MR-RATE metadata and reports refresh. Use command-dry-run first,
defer labels until the end, and do not print raw report text.
```

Natural-language query example:

```text
How many linked patients have infarction? Use the MR-RATE helper views and tell
me the SQL.
```

Troubleshooting or refinement example:

```text
The MR-RATE download returned a Git LFS pointer. Use mr-rate-data-curator to explain the retry path.
```

## Help And Getting Started

Start with:

```text
Use mr-rate-data-curator to check MR-RATE curation status in this workspace.
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
Use mr-rate-data-curator to inspect MR-RATE SQLite curation status.
```

Task-based prompt:

```text
Use mr-rate-data-curator to download and import batch01 reports, labels, and metadata into SQLite after confirming Chrome authentication.
```

Guarded prompt:

```text
Use mr-rate-data-curator, but do not download MRI, do not print raw reports, and ask before writing the database.
```

Find or install prompt:

```text
Find and install the SkillForge skill that helps build a local MR-RATE SQLite database.
Ask before installing anything from a peer catalog.
```

## How To Call From The CLI

Search for the skill:

```text
python -m skillforge search "MR-RATE SQLite database" --json
```

Show skill metadata:

```text
python -m skillforge info mr-rate-data-curator --json
```

Install the skill into Codex:

```text
python -m skillforge install mr-rate-data-curator --scope global
```

Evaluate the skill before publishing changes:

```text
python -m skillforge evaluate mr-rate-data-curator --json
```

Run the bundled status command from an installed skill folder:

```text
python scripts/curate_mr_rate_data.py status --workspace .
```

Run a read-only query:

```text
python scripts/curate_mr_rate_data.py query --workspace . --describe views
python scripts/curate_mr_rate_data.py query --workspace . "SELECT pathology_name, linked_patients FROM v_query_pathology_stats ORDER BY linked_patients DESC LIMIT 10;"
```

## Trust And Safety

Risk level:
High

Permissions:

- Reads local workspace files and MR-RATE source status.
- Reads the local SQLite database in read-only mode for query-only requests.
- Uses browser-authenticated Hugging Face access only after approval.
- Writes downloaded source files and SQLite databases after approval.
- Does not copy browser profiles, export cookies, bypass access controls, or
  publish raw medical data.

Data handling:
Treat reports, pathology labels, metadata, source rows, study identifiers,
database rows, and local paths as sensitive research artifacts.

Writes vs read-only:
Read-only by default. Query mode uses SQLite read-only connections. Downloads
and imports are side-effectful and require explicit user approval.

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
Send feedback on mr-rate-data-curator that the status output should summarize table counts.
```

## Contributing

Contribution path:
Open a pull request against `medatasci/agent_skills`.

Before opening a pull request:

- Update `SKILL.md`, this `README.md`, scripts, and references together.
- Run `python -m skillforge build-catalog --json`.
- Run `python -m skillforge evaluate mr-rate-data-curator --json`.

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
- `mrrate-dataset-access`: plans general MR-RATE dataset downloads and layout.
- `mrrate-repository-guide`: routes whole-repo MR-RATE questions.
- `mrrate-report-preprocessing`: explains report preprocessing stages after
  source data is available.
- `mrrate-medical-workflow-reviewer`: reviews clinical-statistical consistency
  of curated datasets and workflows.
