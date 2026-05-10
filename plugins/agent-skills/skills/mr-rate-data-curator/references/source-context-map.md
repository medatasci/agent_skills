# MR-RATE Data Curator Source Context Map

## Purpose

This source-context map records the evidence used to publish
`mr-rate-data-curator` as a SkillForge skill. The skill is source-informed by
the MR-RATE dataset layout and by local curation tooling developed for building
and querying an MR-RATE SQLite database.

## Source Version

MR-RATE source repository:
https://github.com/forithmus/MR-RATE

Inspected MR-RATE commit:

```text
e02b4ed79ff427fb3578f03242de2d9d51dc709d
```

SkillForge repository context:

```text
skills/mr-rate-data-curator/
```

The local curation tooling referenced by the skill is expected in the target
workspace and is checked at runtime. The skill does not publish MR-RATE data,
source CSV contents, SQLite databases, browser cookies, or credentials.

## Root-To-Leaf README Context

MR-RATE ancestor README chain used for the data curation context:

- MR-RATE root `README.md`
- `data-preprocessing/README.md`
- `data-preprocessing/docs/dataset_guide.md`

The skill also relates to the previously published MR-RATE collection context:

- `collections/MR-RATE/README.md`
- `docs/reports/mr-rate-whole-repo-to-skills/source-context-map.md`
- `docs/reports/mr-rate-whole-repo-to-skills/candidate-skill-table.md`

## Source Evidence

| Source | Evidence Used | Skill Responsibility |
| --- | --- | --- |
| MR-RATE dataset card | Gated dataset access, non-commercial research context, Hugging Face source location. | Preserve access controls and research-only framing. |
| MR-RATE root README | Dataset and repository orientation. | Keep curation in the MR-RATE family context. |
| `data-preprocessing/docs/dataset_guide.md` | Reports, metadata, pathology labels, batch structure, and join keys. | Define curation scope and source groups. |
| Local `tools/browser_download_mr_rate_batch.js` | Browser-authenticated download behavior. | Require persistent Chrome session and approval before downloads. |
| Local `tools/build_mr_rate_db.py` | SQLite import behavior, helper views, and descriptor tables. | Require workspace tool check, database-write approval, and helper-view preference for queries. |
| Local `tools/query_mr_rate_db.py` | Read-only query helper and descriptor inspection pattern. | Provide a portable read-only query surface in the bundled orchestrator. |
| `scripts/curate_mr_rate_data.py` | Restartable wrapper over download, import, run, status, and query commands. | Provide deterministic local command surface. |
| `references/source-layout.md` | Source file paths and database table summary. | Document expected local layout and table names. |
| `references/sqlite-query-interface.md` | Helper views, descriptor tables, and natural-language SQL examples. | Guide Codex toward count-unit-aware SQL without exposing raw records. |

## Safety Context

The skill treats reports, metadata, study identifiers, source rows, local paths,
browser-authenticated access, and SQLite rows as sensitive research artifacts.
It asks before downloads, database writes, MRI archive handling, or any
patient-level inspection. Query-only work uses read-only SQLite connections and
should report count units and SQL without dumping raw report text.

The skill does not diagnose, treat, triage, validate clinical truth, or present
MR-RATE labels as clinical ground truth.

## Candidate Skill Table

| Candidate | Decision | Reason |
| --- | --- | --- |
| MR-RATE Data Curator | Build and publish as `mr-rate-data-curator`. | It has a distinct operational surface: browser-authenticated source downloads and SQLite import. |
| General MR-RATE Dataset Access | Already covered by `mrrate-dataset-access`. | General download planning does not need SQLite curation logic. |
| MR-RATE SQLite Query Analyst | Fold into `mr-rate-data-curator` for now. | The current query surface is read-only, descriptor-guided, and tightly coupled to the curated database schema. Split later if the query workflow grows into a separate analysis skill. |
| MR-RATE MRI Archive Indexer | Defer. | MRI archives need separate disk, extraction, and indexing policy. |

## Runtime Context

The skill is Windows-friendly but generic enough for other local Python
workspaces. It expects Python, optionally Node for browser download tooling, and
project-local curation tools in the user-selected workspace.

The bundled script supports dry-run behavior for command planning and status
inspection without writing data. Query mode opens the local SQLite database in
read-only mode.
