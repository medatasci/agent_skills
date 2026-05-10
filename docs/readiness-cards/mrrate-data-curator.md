# MR-RATE Data Curator Readiness Card

Skill ID: `mrrate-data-curator`

Review date: May 10, 2026

## Summary

`mrrate-data-curator` packages the local MR-RATE SQLite curation workflow as a
SkillForge skill. It helps an agent inspect curation status, plan authenticated
downloads of MR-RATE reports, labels, and metadata, import sources into
`research-data/mr-rate.sqlite`, and preserve source provenance.

The skill is high risk because it can use authenticated browser access, download
gated medical-imaging research data, and write a local SQLite database. Safe
default behavior is read-only status and command planning. Downloads, database
writes, and MRI handling require explicit user approval.

## Source Version Status

MR-RATE source repository:
https://github.com/forithmus/MR-RATE

Pinned MR-RATE source commit:

```text
commit: e02b4ed79ff427fb3578f03242de2d9d51dc709d
```

The local curation workflow was developed in the user's workspace and is
represented in this repository by:

- `skills/mrrate-data-curator/SKILL.md`
- `skills/mrrate-data-curator/README.md`
- `skills/mrrate-data-curator/scripts/curate_mr_rate_data.py`
- `skills/mrrate-data-curator/references/source-layout.md`
- `skills/mrrate-data-curator/references/source-context-map.md`

The skill does not publish MR-RATE source data, SQLite databases, patient-level
rows, browser cookies, credentials, or local private paths.

Read-only database analysis has been split into
`skills/mrrate-database-analysis/`.

## Source Context Map

| Source | Context | How The Skill Uses It |
| --- | --- | --- |
| MR-RATE root `README.md` | Repository and dataset orientation. | Keeps the curation workflow tied to MR-RATE research context. |
| `data-preprocessing/README.md` | Download, preprocessing, and dataset-use framing. | Preserves data-access and preprocessing boundaries. |
| `data-preprocessing/docs/dataset_guide.md` | Reports, metadata, pathology labels, batches, and join keys. | Defines reports/labels/metadata source groups and database curation scope. |
| Local `tools/browser_download_mr_rate_batch.js` | Browser-authenticated download helper. | Requires persistent Chrome DevTools endpoint and approval before downloads. |
| Local `tools/build_mr_rate_db.py` | SQLite import helper. | Requires database write approval and workspace tool checks. |
| `scripts/curate_mr_rate_data.py` | Skill-bundled orchestration wrapper. | Provides `status`, `download`, `import`, and `run` commands. |
| `references/source-layout.md` | Expected local source paths and table names. | Documents local file/database expectations. |

Additional preserved context:

- `skills/mrrate-data-curator/references/source-context-map.md`
- `collections/MR-RATE/README.md`
- `docs/reports/mr-rate-whole-repo-to-skills/`

## Candidate Skill Table

| Candidate Skill | Decision | Evidence | Notes |
| --- | --- | --- | --- |
| MR-RATE Data Curator | Publish as `mrrate-data-curator`. | Local curation wrapper, source layout reference, MR-RATE dataset-guide context. | Distinct from general dataset access because it writes a SQLite database. |
| MR-RATE Dataset Access | Already published as `mrrate-dataset-access`. | MR-RATE Hugging Face repository and download planning. | Use for general download planning without SQLite import. |
| MR-RATE Database Analysis | Publish as `mrrate-database-analysis`. | Read-only query helper, helper views, descriptor tables. | Separate from download/import side effects. |
| MR-RATE MRI Archive Indexer | Defer. | MRI archive handling and indexing. | Needs a separate storage, extraction, indexing, and safety design. |

## Execution Surface

Bundled executable:

```text
skills/mrrate-data-curator/scripts/curate_mr_rate_data.py
```

Supported commands:

- `status`: read local source/database state and print JSON.
- `download`: call the workspace browser download helper.
- `import`: call the workspace SQLite import helper.
- `run`: perform download and import in sequence.

Side effects:

- `status` is read-only.
- `download` can write source files under `research-data/sources/mr-rate/`.
- `import` and `run` can write or refresh `research-data/mr-rate.sqlite`.
- MRI downloads are opt-in only and require separate approval.

## Dependencies

Runtime dependencies:

- Python 3.
- Node.js when using the browser download helper.
- A target workspace containing:
  - `tools/browser_download_mr_rate_batch.js`
  - `tools/build_mr_rate_db.py`
- Authenticated browser DevTools endpoint when downloading gated sources.
- Hugging Face access to the MR-RATE gated dataset.

The bundled script checks for required workspace tools before download/import
execution and supports dry-run command planning.

## Smoke Test Plan

Expected command for a no-network, read-only smoke test:

```text
python skills/mrrate-data-curator/scripts/curate_mr_rate_data.py status --workspace .
```

Expected behavior:

- The command prints JSON.
- It does not download data.
- It does not write or modify the SQLite database.
- It reports whether `research-data/mr-rate.sqlite` and local source files
  exist.

Skip condition:

Skip download/import smoke tests in CI or public review because they require
gated Hugging Face access, an authenticated browser session, and local medical
research data. Use `--command-dry-run` for command-shape checks instead of real
downloads.

## Safety Review

The skill must:

- Treat raw reports, labels, metadata rows, study identifiers, local paths, and
  SQLite rows as sensitive research artifacts.
- Ask before browser-authenticated downloads.
- Ask before database writes or refreshes.
- Ask before MRI download, archive retention, extraction, or indexing.
- Avoid printing raw report text or patient-level rows in public artifacts.
- Avoid copying browser profiles, exporting cookies, or bypassing gated access.
- Preserve research-only framing and avoid clinical-use claims.

## Publication Decision

Ready to publish after:

- `python -m skillforge build-catalog --json`
- `python -m skillforge evaluate mrrate-data-curator --json`
- syntax check for `scripts/curate_mr_rate_data.py`
- privacy scan for machine-local paths, credentials, raw report text, and
  unsupported clinical-care claims

This skill is added to the MR-RATE family as a high-risk local data curation
skill with explicit side-effect gates.
