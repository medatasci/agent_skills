# `skillforge/update.py`

Read-only upstream update checks and Git-derived "what changed" summaries for
SkillForge itself.

Use this document when a human or agent needs to understand, modify, or review
the Python module without reverse-engineering the whole package.

## Responsibilities

This module owns:

- Comparing local checkout state to the configured upstream branch.
- Caching update-check status when the user cache is writable.
- Summarizing Git changes for `whats-new`.

This module does not own:

- Actually updating files from upstream; `update --yes` is deferred.
- CLI command registration or output wording; use `cli.py`.

## When To Edit This Module

Edit this module when:

- `update-check` fields or Git comparison behavior should change.
- `whats-new` categorization or summary logic should change.
- Update-state cache behavior should change.

Choose another module when:

- The README guidance for updates changes; edit `README.md`.
- Future persistent configuration is added; add or update the owning config module.

## Commands Or Workflows

Commands, workflows, or APIs backed by this module:

```text
python -m skillforge update-check --json
python -m skillforge update-check --no-fetch --json
python -m skillforge whats-new
```

Related commands:

- `python -m skillforge whats-new --since <commit> --json`
- Future `python -m skillforge update --yes`

## Inputs And Reads

This module reads:

- The local Git repository.
- The configured upstream branch/ref.
- Optional cached update status.

Important environment variables:

- `SKILLFORGE_CACHE_DIR`: Overrides where update-check state is cached.
- Git environment variables may affect Git behavior, but this module does not set them.

## Outputs And Writes

This module writes:

- Update-check cache state when the cache directory is writable.
- Nothing for `whats-new`.

Generated or modified files:

```text
<SkillForge cache>/state/update-status.json
```

Cache write failures are reported in JSON but should not make update status
unusable.

## Side Effects And Safety

Risk level:
medium

Network access:
`update-check` may run `git fetch` unless `--no-fetch` is used.

Filesystem writes:
Only update-check cache state.

External commands:
Git commands such as `rev-parse`, `fetch`, `rev-list`, `log`, `diff`, and
`status`.

User confirmation gates:

- This module must not change working tree files.
- Future update behavior must refuse unsafe changes when the checkout is dirty.

Safety notes:

- Treat cache writes as optional.
- Keep summaries factual and derived from Git history.

## Public Functions And Data Contracts

Important functions, classes, or data structures:

- `update_check(...)`: returns local/upstream status and cache metadata.
- `whats_new(...)`: returns commits, changed files, inferred categories, and summary lines.
- `run_git(args, ...)`: safe subprocess wrapper for Git calls.

Stable JSON fields or return payloads:

- `updates_available`, `ahead_by`, `behind_by`, `dirty`, and `fetch`.
- `summary`, `commits`, `changed_files`, and `categories`.

Compatibility notes:

- Keep update-check read-only.
- Keep `--no-fetch` useful for offline and sandboxed environments.

## Cross-Platform Notes

Windows, macOS, and Linux considerations:

- Use subprocess argument lists with `shell=False`.
- User cache paths may be unwritable in sandboxed or managed environments.
- Git may be missing, blocked, or configured differently.

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

- `update_check(..., no_fetch=True)` detects behind state from local refs.
- Cache write failure does not fail the check.
- `whats_new()` categorizes docs, skill, peer, catalog, and CLI changes.

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
- `docs/python/cli.md`
- `docs/skillforge-whitepaper.md`
