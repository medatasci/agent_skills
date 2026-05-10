# MR-RATE Data Curator Source Context Map

## Purpose

This source-context map records the evidence used to publish
`mrrate-data-curator` as a SkillForge skill. The skill is source-informed by
the MR-RATE dataset layout and by local curation tooling developed for building
an MR-RATE SQLite database.

Database analysis, helper-view SQL, descriptive statistics, and patient/study
record review are split into `mrrate-database-analysis`.

## Source Version

MR-RATE source repository:
https://github.com/forithmus/MR-RATE

Inspected MR-RATE commit:

```text
e02b4ed79ff427fb3578f03242de2d9d51dc709d
```

SkillForge repository context:

```text
skills/mrrate-data-curator/
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
| Local `tools/build_mr_rate_db.py` | SQLite import behavior and database schema refresh. | Require workspace tool check and database-write approval. |
| `scripts/curate_mr_rate_data.py` | Restartable wrapper over download, import, run, and status commands. | Provide deterministic local curation command surface. |
| `references/source-layout.md` | Source file paths and database table summary. | Document expected local layout and table names. |

## Safety Context

The skill treats reports, metadata, study identifiers, source rows, local paths,
browser-authenticated access, and SQLite rows as sensitive research artifacts.
It asks before downloads, database writes, MRI archive handling, or any
patient-level inspection. Analysis-only work should be handled by
`mrrate-database-analysis`.

The skill does not diagnose, treat, triage, validate clinical truth, or present
MR-RATE labels as clinical ground truth.

## Candidate Skill Table

| Candidate | Decision | Reason |
| --- | --- | --- |
| MR-RATE Data Curator | Build and publish as `mrrate-data-curator`. | It has a distinct operational surface: browser-authenticated source downloads and SQLite import. |
| MR-RATE Database Analysis | Split and publish as `mrrate-database-analysis`. | Querying, descriptive statistics, helper views, and private record summaries are read-only analysis, not curation. |
| General MR-RATE Dataset Access | Already covered by `mrrate-dataset-access`. | General download planning does not need SQLite curation logic. |
| MR-RATE MRI Archive Indexer | Defer. | MRI archives need separate disk, extraction, and indexing policy. |

## Runtime Context

The skill is Windows-friendly but generic enough for other local Python
workspaces. It expects Python, optionally Node for browser download tooling, and
project-local curation tools in the user-selected workspace.

The bundled script supports dry-run behavior for command planning and status
inspection without writing data. The `all` batch selector targets official
MR-RATE batches `01` through `27`. Local derived analysis CSV imports are
skipped by default and require `--include-derived`.
