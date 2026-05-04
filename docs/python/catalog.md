# `skillforge/catalog.py`

Local catalog, search index, static site, plugin mirror, and publication
evaluation engine for SkillForge-owned skills.

Use this document when a human or agent needs to understand, modify, or review
the Python module without reverse-engineering the whole package.

## Responsibilities

This module owns:

- Building `catalog/`, `site/`, and plugin mirror outputs from `skills/`.
- Local SkillForge search and search-index generation.
- Deterministic skill publication evaluation.
- Non-blocking repo-derived skill advisory checks for readiness cards,
  source-context maps, candidate tables, source version status, runtime plans,
  smoke tests, and authoritative-source evidence.

This module does not own:

- Peer catalog fetching or peer install; use `peer.py`.
- Codex install path resolution; use `install.py`.

## When To Edit This Module

Edit this module when:

- Generated catalog JSON, static pages, or skill list output should change.
- Local `search`, `search-audit`, or `evaluate` behavior should change.
- Skill metadata extraction or generated search text should change.

Choose another module when:

- A peer result is missing or wrong; use `peer.py`.
- A skill folder fails structural validation; use `validate.py`.

## Commands Or Workflows

Commands, workflows, or APIs backed by this module:

```text
python -m skillforge build-catalog
python -m skillforge search "<task>"
python -m skillforge evaluate <skill-id> --json
```

Related commands:

- `python -m skillforge search-audit <skill-id> --json`
- `python -m skillforge info <skill-id> --json`

## Inputs And Reads

This module reads:

- `skills/<skill-id>/SKILL.md`
- `skills/<skill-id>/README.md`
- `schemas/`

Important environment variables:

- None directly.
- `SKILLFORGE_CHATTINESS` affects search output only through `cli.py`.

## Outputs And Writes

This module writes:

- Generated catalog and search index files.
- Generated static site files and plugin skill mirror files.

Generated or modified files:

```text
catalog/skills.json
catalog/search-index.json
catalog/skills/<skill-id>.json
site/
plugins/agent-skills/skills/
```

Read-only functions such as `search_catalog()`, `load_skill_metadata()`,
`search_audit_skill()`, and `evaluate_skill()` should not write files.

## Side Effects And Safety

Risk level:
medium

Network access:
None.

Filesystem writes:
`build_catalog()` writes generated repository outputs.

External commands:
None.

User confirmation gates:

- None inside this module.
- CLI or PR workflow should make generated-file changes explicit to the user.

Safety notes:

- Generated outputs must be deterministic.
- Do not add hidden SEO or structured-data claims that are not visible in skill docs.

## Public Functions And Data Contracts

Important functions, classes, or data structures:

- `build_catalog()`: regenerates catalog, search index, static site, and plugin mirror.
- `search_catalog(query, limit=10)`: returns local SkillForge search results.
- `evaluate_skill(target)`: returns deterministic publication-readiness JSON.
- `repo_derived_advisory_checks(skill_id, skill_dir, metadata)`: returns
  warning-level checks for skills generated from upstream repositories or
  codebases.

Stable JSON fields or return payloads:

- `catalog/skills.json`: aggregate SkillForge catalog.
- `catalog/search-index.json`: local search corpus.
- `evaluate_skill()`: `ok`, `score`, `checks`, `sample_searches`,
  `advisory_checks`, `advisory_warnings`, and `repo_derived`.

Compatibility notes:

- Store repository-relative paths with POSIX separators in generated JSON.
- Keep portable skills valid even when optional discovery fields are missing.

## Cross-Platform Notes

Windows, macOS, and Linux considerations:

- Use `pathlib.Path` for local paths.
- Keep generated JSON paths platform-neutral.
- Exclude transient platform artifacts from checksums and generated file lists.

Avoid:

- Shell-specific behavior in Python module logic.
- Hard-coded path separators.
- Assuming external tools are installed or on `PATH`.

## Tests

Primary tests:

```text
python -m unittest tests.test_skillforge
tests/test_skillforge.py
```

Acceptance checks:

- `build_catalog()` is deterministic.
- `search_catalog()` finds skills by task and discovery metadata.
- `evaluate_skill()` catches stale or missing generated surfaces.
- `evaluate_skill("nv-segment-ctmr")` reports repo-derived advisory checks
  without making them hard publication failures.

## Agent Notes

Before editing:

1. Read this document.
2. Read `skillforge/modules.toml` for ownership and side-effect metadata.
3. Read the source file.
4. Search for tests that already cover the behavior.

After editing:

1. Add or update focused tests.
2. Run the relevant test subset.
3. Run `python -m unittest tests.test_skillforge` before publishing.
4. Update this document and `skillforge/modules.toml` if ownership,
   side effects, commands, or data contracts changed.

## Related Docs

- `skillforge/README.md`
- `skillforge/modules.toml`
- `docs/python/README.md`
- `docs/python/validate.md`
- `docs/skill-search-seo-plan.md`
