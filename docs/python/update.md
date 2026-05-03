# `skillforge/update.py`

Periodic upstream update checks, conservative fast-forward updates, and
Git-derived "what changed" summaries for SkillForge itself.

Use this document when a human or agent needs to understand, modify, or review
the Python module without reverse-engineering the whole package.

## Responsibilities

This module owns:

- Comparing local checkout state to the configured upstream branch.
- Caching update-check status when the user cache is writable.
- Applying an explicit fast-forward-only update when the checkout is clean.
- Summarizing Git changes for `whats-new`.

This module does not own:

- CLI command registration or output wording; use `cli.py`.
- Persistent user configuration; add or update a config module when that exists.

## When To Edit This Module

Edit this module when:

- `update-check` fields or Git comparison behavior should change.
- `update --yes` safety rules or fast-forward behavior should change.
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
python -m skillforge update
python -m skillforge update --yes
python -m skillforge whats-new
python -m skillforge whats-new --details
python -m skillforge whats-new --commits
```

Related commands:

- `python -m skillforge update --yes --json`
- `python -m skillforge whats-new --since <commit> --json`

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
- Repository files through `git merge --ff-only` only when `update --yes` is
  requested and the checkout is safe to fast-forward.
- Nothing for `whats-new`.

Generated or modified files:

```text
<SkillForge cache>/state/update-status.json
SkillForge repository files, only through explicit fast-forward update
```

Cache write failures are reported in JSON but should not make update status
unusable.

## Side Effects And Safety

Risk level:
medium

Network access:
`update-check` and `update` may run `git fetch` unless `--no-fetch` is used.
The default cached check window is 6 hours, so repeated checks can be run
without forcing a network fetch every time.

Filesystem writes:
Update-check cache state, and repository files only through explicit
fast-forward update.

External commands:
Git commands such as `rev-parse`, `fetch`, `rev-list`, `log`, `diff`, `status`,
and `merge --ff-only`.

User confirmation gates:

- `update` without `--yes` reports status but does not change files.
- `update --yes` must refuse unsafe changes when the checkout is dirty.
- `update --yes` must refuse diverged branches and non-fast-forward updates.

Safety notes:

- Treat cache writes as optional.
- Keep summaries factual and derived from Git history.
- Keep update behavior boring: no background daemon and no overwrite of local work.

## Public Functions And Data Contracts

Important functions, classes, or data structures:

- `update_check(...)`: returns local/upstream status and cache metadata.
- `update_skillforge(...)`: applies a fast-forward update only after explicit confirmation.
- `whats_new(...)`: returns commits, changed files, inferred categories,
  user-facing summary lines, technical summary lines, and a detail prompt.
- `run_git(args, ...)`: safe subprocess wrapper for Git calls.

Stable JSON fields or return payloads:

- `updates_available`, `ahead_by`, `behind_by`, `dirty`, and `fetch`.
- `updated`, `refused`, `requires_confirmation`, `previous_commit`, and
  `current_commit`.
- `summary`, `technical_summary`, `detail_prompt`, `commits`,
  `changed_files`, and `categories`.

Compatibility notes:

- Keep update-check read-only.
- Keep update applying only fast-forward updates.
- Keep `--no-fetch` useful for offline and sandboxed environments.

## Cross-Platform Notes

Windows, macOS, and Linux considerations:

- Use subprocess argument lists with `shell=False`.
- User cache paths may be unwritable in sandboxed or managed environments.
- Git may be missing, blocked, or configured differently.
- Fast-forward updates should use Git refs and subprocess argument lists, not
  shell-specific `git pull` wrappers.

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
- `update_skillforge(..., yes=True, no_fetch=True)` fast-forwards a clean test repo.
- Cache write failure does not fail the check.
- `whats_new()` defaults to user-facing feature summaries.
- `whats_new()` categorizes docs, skill, peer, catalog, and CLI changes for
  JSON and `--details` output.

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
