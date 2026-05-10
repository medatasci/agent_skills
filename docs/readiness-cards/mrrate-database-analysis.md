# MR-RATE Database Analysis Readiness Card

Skill ID: `mrrate-database-analysis`

Review date: May 10, 2026

## Summary

`mrrate-database-analysis` packages the read-only MR-RATE SQLite analysis
workflow as a SkillForge skill. It helps an agent inspect helper-view
descriptors, choose the correct counting unit, run read-only SQL, show the SQL,
and summarize results without exposing raw reports or patient-level exports.

The skill is high risk because it can inspect a local database derived from
gated medical-imaging research data. Safe default behavior is read-only SQL with
concise aggregate or private local summaries.

## Source Version Status

MR-RATE source repository:
https://github.com/forithmus/MR-RATE

Pinned MR-RATE source commit:

```text
commit: e02b4ed79ff427fb3578f03242de2d9d51dc709d
```

The local query workflow is represented in this repository by:

- `skills/mrrate-database-analysis/SKILL.md`
- `skills/mrrate-database-analysis/README.md`
- `skills/mrrate-database-analysis/scripts/query_mr_rate_db.py`
- `skills/mrrate-database-analysis/references/sqlite-query-interface.md`
- `skills/mrrate-database-analysis/references/source-context-map.md`

The skill does not publish MR-RATE source data, SQLite databases, patient-level
rows, browser cookies, credentials, or local private paths.

## Source Context Map

| Source | Context | How The Skill Uses It |
| --- | --- | --- |
| Local `tools/query_mr_rate_db.py` | Read-only database helper. | Provides bundled read-only SQL command behavior. |
| Local `mr_rate_db/helper_views.sql` | Helper views for cohorts, metadata, and pathology counts. | Guides view preference and examples. |
| Local `mr_rate_db/query_descriptors.sql` | LLM-facing query descriptors. | Guides natural-language SQL routing. |
| Local `docs/schema/schema.md` | Generated schema documentation. | Preferred way to publish schema context when available. |
| `mrrate-data-curator` | Builds and refreshes the database. | Defines the upstream build/update boundary. |

## Candidate Skill Table

| Candidate Skill | Decision | Evidence | Notes |
| --- | --- | --- | --- |
| MR-RATE Database Analysis | Publish as `mrrate-database-analysis`. | Read-only query helper, helper views, descriptor tables. | Distinct from curation because it does not download or write data. |
| MR-RATE Data Curator | Keep as `mrrate-data-curator`. | Browser download and SQLite import wrapper. | Use for build/update, not analysis. |
| MR-RATE Dataset Access | Already published as `mrrate-dataset-access`. | MR-RATE Hugging Face repository and download planning. | Use for general access planning without SQL. |

## Execution Surface

Bundled executable:

```text
skills/mrrate-database-analysis/scripts/query_mr_rate_db.py
```

Supported modes:

- positional SQL
- `--describe views`
- `--describe columns`
- `--describe intents`
- `--describe rules`
- `--describe examples`
- `--format table|json|csv`

Side effects:

- Opens SQLite with `mode=ro`.
- Writes no files unless the user explicitly requests a private local export
  handled outside the default command.

## Dependencies

Runtime dependencies:

- Python 3.
- A target workspace containing `research-data/mr-rate.sqlite`.
- Helper views and descriptor tables when natural-language query routing is
  requested.

## Smoke Test Plan

Expected command for a no-network smoke test:

```text
python skills/mrrate-database-analysis/scripts/query_mr_rate_db.py --workspace . --describe views
```

Expected behavior:

- The command opens the database read-only.
- It prints descriptor rows when they exist.
- If descriptor tables are missing, it explains that the database needs a newer
  schema refresh.

Skip condition:

Skip tests that require a private local MR-RATE database in public CI.

## Safety Review

The skill must:

- Treat raw reports, labels, metadata rows, study identifiers, local paths, and
  SQLite rows as sensitive research artifacts.
- Use read-only SQLite connections.
- State counting units explicitly.
- Avoid printing raw report text or patient-level rows in public artifacts.
- Avoid clinical-use claims.

## Publication Decision

Ready to publish after:

- `python -m skillforge build-catalog --json`
- `python -m skillforge evaluate mrrate-database-analysis --json`
- syntax check for `scripts/query_mr_rate_db.py`
- privacy scan for machine-local paths, credentials, raw report text, and
  unsupported clinical-care claims
