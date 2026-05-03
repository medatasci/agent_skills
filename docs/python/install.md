# `skillforge/install.py`

Codex skill install, SkillForge marketplace install verification, remove, list,
download, and install path resolution module.

Use this document when a human or agent needs to understand, modify, or review
the Python module without reverse-engineering the whole package.

## Responsibilities

This module owns:

- Resolving global and project Codex skill directories.
- Resolving Codex home, config, and SkillForge marketplace paths.
- Verifying or safely repairing the SkillForge marketplace registration.
- Installing local SkillForge catalog skills into Codex.
- Listing, downloading, and removing installed skills.

This module does not own:

- Peer skill fetching or peer provenance; use `peer.py`.
- Catalog metadata generation; use `catalog.py`.

## When To Edit This Module

Edit this module when:

- Install scope behavior or Codex path resolution changes.
- SkillForge marketplace install verification or config repair behavior changes.
- Local catalog install, download, list, or remove behavior changes.
- `CODEX_HOME` or `SKILLFORGE_CODEX_SKILLS_DIR` handling changes.

Choose another module when:

- Installing from a peer catalog changes; use `peer.py`.
- Validation rules before install change; use `validate.py`.

## Commands Or Workflows

Commands, workflows, or APIs backed by this module:

```text
python -m skillforge install <skill-id> --scope global
python -m skillforge install-skillforge --json
python -m skillforge install-skillforge --yes
python -m skillforge remove <skill-id> --scope global --yes
python -m skillforge list --scope global
```

Related commands:

- `python -m skillforge download <skill-id>`
- `python -m skillforge doctor --json`

## Inputs And Reads

This module reads:

- `catalog/skills/<skill-id>.json`
- `skills/<skill-id>/`
- `<CODEX_HOME>/config.toml`
- `<CODEX_HOME>/plugins/cache/agent-skills-marketplace/`
- Codex skill directories.

Important environment variables:

- `CODEX_HOME`: Overrides the default global Codex home.
- `SKILLFORGE_CODEX_SKILLS_DIR`: Explicit global skills directory override for tests or advanced users.

## Outputs And Writes

This module writes:

- Installed skill folders in the selected Codex skills directory.
- Downloaded skill copies in the requested destination.
- Safe missing Codex config entries for SkillForge marketplace registration,
  only when `install-skillforge --yes` is used.

Generated or modified files:

```text
<CODEX_HOME>/skills/<skill-id>/
<CODEX_HOME>/config.toml
<project>/.codex/skills/<skill-id>/
downloads/<skill-id>/
```

`list`, `install-skillforge --json`, and path-resolution helpers are read-only.

## Side Effects And Safety

Risk level:
medium

Network access:
None.

Filesystem writes:
Install, download, remove, and `install-skillforge --yes` write or delete local
files.

External commands:
Read-only Git commands for marketplace metadata when available.

User confirmation gates:

- `remove` is confirmed by the CLI with `--yes`.
- `install-skillforge --yes` is required before Codex config entries are added.
- Peer install confirmation is owned by `cli.py` and `peer.py`.

Safety notes:

- Validate before install.
- Never execute skill scripts during install.
- Never overwrite an existing marketplace folder that is not verified as
  SkillForge.
- Marketplace verification requires the plugin manifest, skill list, and
  README. The Python CLI file is reported when present but is optional because
  some Codex marketplace caches contain plugin files without the repo-local CLI.
- Treat conflicting or malformed Codex config as manual review, not automatic
  rewrite.

## Public Functions And Data Contracts

Important functions, classes, or data structures:

- `install_skill(skill_id, scope, project, force)`: copies a local catalog skill into Codex.
- `install_skillforge_marketplace(...)`: inspects or repairs SkillForge
  marketplace registration.
- `remove_installed_skill(skill_id, scope, project)`: removes one installed copy.
- `resolve_install_dir(scope, project)`: returns the target skills directory.

Stable JSON fields or return payloads:

- CLI install JSON: `installed`, `target`, and `scope`.
- CLI install-skillforge JSON: `status`, `changed`, `codex_home`, `config`,
  `marketplace`, `version`, `actions`, `warnings`, and `next_commands`.
  `version` includes source repository, configured ref, source type, Git branch,
  Git commit, dirty state, plugin name, plugin version, code version, last
  updated timestamp, and the source for the timestamp when available.
- CLI remove JSON: `removed`, `target`, and `scope`.

Compatibility notes:

- Keep project installs under `.codex/skills` on all operating systems.
- Prefer copying over symlinks for MVP portability.
- Keep SkillForge marketplace install idempotent: healthy existing installs
  should not be treated as errors.

## Cross-Platform Notes

Windows, macOS, and Linux considerations:

- Windows may have read-only file attributes during removal.
- Environment variable syntax differs by shell; Python should read `os.environ`.
- Managed machines may restrict symlinks or long paths.
- Codex config should be appended with plain text only for missing,
  non-conflicting tables.

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

- Global install honors `SKILLFORGE_CODEX_SKILLS_DIR`.
- Global install honors `CODEX_HOME` when no explicit override is set.
- Remove deletes only the requested installed copy.
- `install_skillforge_marketplace(...)` reports healthy existing installs.
- `install_skillforge_marketplace(..., yes=True)` appends safe missing config entries.

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
- `docs/python/filesystem.md`
- `docs/python/peer.md`
