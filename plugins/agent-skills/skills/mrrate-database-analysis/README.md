# MR-RATE Database Analysis

Skill ID: `mrrate-database-analysis`

Analyze a local MR-RATE SQLite database with read-only SQL, helper views,
descriptor tables, and count-unit-aware summaries. This is the skill to call
when a curated database already exists and the user asks questions like how
many patients have infarction, which helper view to use, or how scan metadata
coverage differs for a cohort.

Use `mrrate-data-curator` when the task is to download, import, build, refresh,
or verify source files for `research-data/mr-rate.sqlite`.

## Repo And Package

Skill repo URL:
https://github.com/medatasci/agent_skills/tree/main/skills/mrrate-database-analysis

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
Medical Imaging, Data Analysis, Research

Collection context:
This skill is the read-only SQLite analysis branch of the MR-RATE skill family.
It uses a database created by `mrrate-data-curator` and keeps analysis
questions separate from data curation side effects.

## What This Skill Does

This skill helps Codex translate natural-language MR-RATE database questions
into read-only SQL. It prefers LLM-oriented helper views and descriptor tables,
states the counting unit, executes SQL in read-only SQLite mode, and reports the
SQL with concise results and caveats.

## Why You Would Call It

Call this skill when:

- You want Codex to answer a local MR-RATE SQLite question and show the SQL.
- You need count-unit-aware descriptive statistics from helper views.
- You want to inspect the LLM query descriptor tables or schema docs.
- You need a concise private local preview of matching patient or study records.

Use it for:

- Patient, study, report, label-row, and metadata-series counts.
- Pathology prevalence and cohort summaries.
- Metadata coverage by field strength, sequence, scanner, or protocol.
- Co-occurring pathology summaries.
- Private local patient/study previews when explicitly requested.
- Schema and helper-view discovery for Codex context.

Do not use it for:

- Downloading or importing MR-RATE source data.
- Refreshing `research-data/mr-rate.sqlite`.
- Browser-authenticated Hugging Face workflows.
- Public export of raw reports, patient rows, local paths, or database content.
- Clinical diagnosis, treatment, triage, prognosis, or validation claims.

## Keywords

MR-RATE, SQLite, SQL, helper views, descriptor tables, descriptive statistics,
cohort counts, pathology prevalence, metadata coverage, scan metadata, database
analysis, natural-language SQL.

## Search Terms

MR-RATE database analysis, MR-RATE SQLite analysis, MR-RATE SQL query, MR-RATE
helper views, MR-RATE descriptive statistics, MR-RATE cohort counts, patients
with infarction MR-RATE, MR-RATE metadata coverage, MR-RATE schema docs.

## How It Works

The skill wraps `scripts/query_mr_rate_db.py`, which opens the selected SQLite
database with `mode=ro`. The default database path is:

```text
research-data/mr-rate.sqlite
```

The workflow is:

1. Resolve the workspace and database path.
2. Inspect descriptor tables when the question is natural language.
3. Choose a count unit explicitly.
4. Draft SQL against helper views.
5. Run the query in read-only mode.
6. Tell the user the SQL and summarize the result.
7. Keep record previews concise and private.

## API And Options

SkillForge catalog commands:

```text
python -m skillforge search "MR-RATE SQL query" --json
python -m skillforge info mrrate-database-analysis --json
python -m skillforge evaluate mrrate-database-analysis --json
```

Bundled query commands:

```text
python scripts/query_mr_rate_db.py --workspace . --describe intents
python scripts/query_mr_rate_db.py --workspace . --describe views
python scripts/query_mr_rate_db.py --workspace . --describe examples
python scripts/query_mr_rate_db.py --workspace . "SELECT COUNT(*) AS patients FROM v_query_patient_summary;"
```

Important options:

- `--workspace`: workspace root used to resolve the default database path.
- `--db`: SQLite database path, absolute or relative to `--workspace`.
- `--sql-file`: read SQL from a local file.
- `--describe`: inspect `views`, `columns`, `intents`, `rules`, or `examples`.
- `--format`: choose `table`, `json`, or `csv`.
- `--limit`: table display limit.

## Helper Views And Descriptor Tables

Prefer these helper views when present:

- `v_query_positive_labels`
- `v_query_patient_summary`
- `v_query_study_summary`
- `v_query_pathology_stats`
- `v_query_patient_pathologies`
- `v_query_infarction_cases`
- `v_query_metadata_series`
- `v_query_sequence_stats`
- `v_query_cooccurring_pathologies`

Descriptor tables guide natural-language routing:

- `llm_query_view_catalog`
- `llm_query_column_catalog`
- `llm_query_intent_catalog`
- `llm_query_rules`
- `llm_query_examples`
- `v_llm_query_guide`

For detailed examples, read `references/sqlite-query-interface.md`.

## Authoritative Sources

- MR-RATE dataset: https://huggingface.co/datasets/Forithmus/MR-RATE
- MR-RATE source repository: https://github.com/forithmus/MR-RATE
- Local MR-RATE SQLite helper views: `mr_rate_db/helper_views.sql`
- Local MR-RATE LLM query descriptors: `mr_rate_db/query_descriptors.sql`
- Local query helper: `tools/query_mr_rate_db.py`

## Inputs And Outputs

Inputs can include:

- Workspace path.
- SQLite database path.
- Natural-language question.
- SQL or SQL file.
- Desired counting unit or output format.

Outputs can include:

- SQL statement.
- Query results.
- Count-unit explanation.
- Linkage, missingness, and privacy caveats.
- Optional local private JSON or CSV output only when explicitly requested.

## Limitations

Known limitations:

- The skill requires an existing local MR-RATE SQLite database.
- Helper views and descriptor tables require a database built with the newer
  local schema.
- Natural-language SQL is only as reliable as the helper-view descriptors and
  the selected counting unit.
- Private record previews can expose sensitive research artifacts and should
  stay local.
- The skill does not validate labels as clinical truth.

Choose another skill when:

- You need to build or refresh the database: use `mrrate-data-curator`.
- You need general dataset access planning: use `mrrate-dataset-access`.
- You need training or inference: use the contrastive MR-RATE skills.

## Examples

Direct helper-view query:

```text
Use mrrate-database-analysis to list the MR-RATE pathology stats helper view.
Show me the SQL.
```

Filtered summary:

```text
How many patients have Cerebral infarction? Use helper views and tell me the SQL.
```

Join with metadata:

```text
Use mrrate-database-analysis to summarize field strength coverage for infarction studies.
Join the infarction helper view to scan metadata and show the SQL.
```

Private record preview:

```text
Show concise private local study summaries for patients with Cerebral infarction.
Do not export raw reports.
```

## Trust And Safety

Risk level:
High

Permissions:

- Reads local SQLite databases and generated schema docs.
- Runs read-only SQL against local MR-RATE helper views and descriptor tables.
- Writes no files unless explicitly requested for a private local export.
- Does not publish raw reports, patient-level rows, local paths, or private
  database contents.

Data handling:
Treat reports, pathology labels, metadata, source rows, study identifiers,
database rows, and local paths as sensitive research artifacts.

Writes vs read-only:
The bundled query command opens SQLite in read-only mode. Do not use this skill
for database writes or refreshes.

External services:
None required for analysis of an existing local database.

Credentials:
No credential access is needed. Do not inspect browser sessions or Hugging Face
tokens from this skill.

## Feedback

Feedback URL:
https://github.com/medatasci/agent_skills/issues

Send feedback when:

- A natural-language query maps to the wrong helper view.
- A useful cohort summary is missing from descriptor examples.
- Schema docs or helper-view descriptions are stale.

## Contributing

Contribution path:
Open a pull request against `medatasci/agent_skills`.

Before opening a pull request:

- Update `SKILL.md`, this `README.md`, scripts, and references together.
- Run `python -m skillforge build-catalog --json`.
- Run `python -m skillforge evaluate mrrate-database-analysis --json`.

## Author

medatasci

Maintainer status:
Local-workflow-derived SkillForge skill maintained with the MR-RATE skill
family.

## Citations

- MR-RATE source repository: https://github.com/forithmus/MR-RATE
- MR-RATE dataset: https://huggingface.co/datasets/Forithmus/MR-RATE
- Creative Commons BY-NC-SA 4.0: https://creativecommons.org/licenses/by-nc-sa/4.0/

## Related Skills

- `mrrate-data-curator`: builds and refreshes the local SQLite database.
- `mrrate-dataset-access`: plans general MR-RATE dataset downloads and layout.
- `mrrate-medical-workflow-reviewer`: reviews clinical-statistical consistency.
- `mrrate-report-preprocessing`: explains report preprocessing stages.
