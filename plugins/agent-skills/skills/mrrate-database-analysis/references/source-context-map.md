# MR-RATE Database Analysis Source Context Map

## Purpose

This source-context map records the evidence used to publish
`mrrate-database-analysis` as a SkillForge skill. The skill is
local-workflow-derived from the MR-RATE SQLite database, helper views,
descriptor tables, generated schema docs, and query helper created for
count-unit-aware analysis.

The database itself and source data are not included in this package.

## Source Version

MR-RATE source repository:
https://github.com/forithmus/MR-RATE

Inspected MR-RATE commit:

```text
e02b4ed79ff427fb3578f03242de2d9d51dc709d
```

SkillForge repository context:

```text
skills/mrrate-database-analysis/
```

## Source Evidence

| Source | Evidence Used | Skill Responsibility |
| --- | --- | --- |
| Local `tools/query_mr_rate_db.py` | Read-only query helper and descriptor inspection pattern. | Provide the bundled `scripts/query_mr_rate_db.py` surface. |
| Local `mr_rate_db/helper_views.sql` | LLM-oriented helper views for cohorts, pathology stats, metadata, and co-occurrence. | Prefer helper views over raw tables. |
| Local `mr_rate_db/query_descriptors.sql` | LLM query catalog, column meanings, intents, rules, and examples. | Inspect descriptor tables before natural-language SQL. |
| Local `tools/generate_mr_rate_schema_docs.py` | Markdown schema publishing workflow. | Prefer generated schema docs for Codex context when available. |
| Local `docs/mr_rate_query_cookbook.md` | Repeated query examples and count-unit patterns. | Show SQL and counting caveats in answers. |
| `mrrate-data-curator` | Builds the database that this skill reads. | Keep build/update side effects out of database analysis. |

## Safety Context

The skill treats report text, labels, metadata, patient/study identifiers,
database rows, and local paths as sensitive research artifacts. Query-only work
uses SQLite read-only connections and should report count units and SQL without
dumping raw report text.

The skill does not diagnose, treat, triage, validate clinical truth, or present
MR-RATE labels as clinical ground truth.

## Candidate Skill Table

| Candidate | Decision | Reason |
| --- | --- | --- |
| MR-RATE Database Analysis | Publish as `mrrate-database-analysis`. | Read-only SQL analysis is a separate user intent from curation. |
| MR-RATE Data Curator | Keep as `mrrate-data-curator`. | Downloads and imports official source data into SQLite. |
| MR-RATE Dataset Access | Already covered by `mrrate-dataset-access`. | General data access does not require local SQL helper views. |

## Runtime Context

The skill is Windows-friendly but generic enough for other local Python
workspaces. It expects Python and a target workspace containing a curated
MR-RATE SQLite database.

The bundled script supports read-only SQL, descriptor inspection, SQL files,
table/JSON/CSV output, and a default database path of
`research-data/mr-rate.sqlite`.
