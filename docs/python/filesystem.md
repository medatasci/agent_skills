# `skillforge/filesystem.py`

Cross-platform copy, remove, and transient artifact filtering helpers.

Use this document when a human or agent needs to understand, modify, or review
the Python module without reverse-engineering the whole package.

## Responsibilities

This module owns:

- Removing directory trees while handling Windows read-only attributes.
- Copying skill trees while ignoring transient artifacts.
- Defining transient file, directory, and suffix rules.

This module does not own:

- Deciding whether a command should remove or copy files.
- Catalog metadata, validation warnings, or peer provenance.

## When To Edit This Module

Edit this module when:

- Cross-platform deletion or copy behavior fails.
- More transient artifacts should be ignored consistently.
- Python-version compatibility for `shutil.rmtree` changes.

Choose another module when:

- Install scope or destination logic changes; use `install.py`.
- Checksum file iteration logic changes; use `validate.py` if validation-specific.

## Commands Or Workflows

Commands, workflows, or APIs backed by this module:

```text
copy_tree(source, destination)
remove_tree(path)
is_transient_path(path, root)
```

Related commands:

- `python -m skillforge install <skill-id>`
- `python -m skillforge remove <skill-id> --yes`

## Inputs And Reads

This module reads:

- Local filesystem paths.
- Directory entries during copy/remove operations.
- File metadata during read-only removal retry.

Important environment variables:

- None.
- Callers may use environment variables to choose paths before calling this module.

## Outputs And Writes

This module writes:

- Copied directory trees.
- Removed directory trees.

Generated or modified files:

```text
Destination tree supplied to copy_tree()
Target tree supplied to remove_tree()
```

This module is intentionally small and side-effectful only when callers request
copy or removal.

## Side Effects And Safety

Risk level:
medium

Network access:
None.

Filesystem writes:
Copies and deletes local files/directories.

External commands:
None.

User confirmation gates:

- Confirmation is owned by CLI/domain callers, not this helper module.
- Do not call removal helpers on unverified computed paths.

Safety notes:

- Callers must validate target paths before removal.
- Keep transient artifact rules aligned with validation, catalog, install, and peer behavior.

## Public Functions And Data Contracts

Important functions, classes, or data structures:

- `remove_tree(path)`: removes a directory tree if it exists.
- `copy_tree(source, destination)`: copies a directory while ignoring transient artifacts.
- `is_transient_path(path, root)`: identifies transient files for file iteration.

Stable JSON fields or return payloads:

- None.
- Functions return `None` or booleans/sets as plain Python helpers.

Compatibility notes:

- Supports both `shutil.rmtree(onexc=...)` and older `onerror=...`.
- Transient rules should remain conservative.

## Cross-Platform Notes

Windows, macOS, and Linux considerations:

- Windows read-only files may need chmod before removal.
- macOS `.DS_Store` and Windows `Thumbs.db` should be ignored.
- Python cache directories should be ignored everywhere.

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

- Read-only files can be removed on Windows.
- `.DS_Store`, `Thumbs.db`, `__pycache__`, and `*.pyc` are ignored.
- Copy behavior does not carry transient artifacts.

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
- `docs/python/install.md`
- `docs/python/validate.md`
