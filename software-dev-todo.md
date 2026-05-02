# SkillForge Software Development TODO

Updated: 2026-05-02

Source of truth:

- Product requirements: `requirements.md`
- User entrypoint: `README.md`
- Peer catalog seed: `peer-catalogs.json`
- Planning/archive TODO: `skillforge-planning-todo.md`

## MVP Definition

SkillForge MVP is a Codex-only, GitHub-backed skill catalog with a package-style Python CLI:

```text
python -m skillforge search "task X" --json
python -m skillforge info <skill-id>
python -m skillforge install <skill-id> --scope global
python -m skillforge install <skill-id> --scope project --project .
```

## Now

- [x] **Define catalog schema**
  - Output: `schemas/skills.schema.json`, `schemas/skill.schema.json`
  - Include: skill ID, name, description, owner, tags, source path, source URL, checksum, updated date, Codex install metadata, files, warnings.
  - Acceptance: two pilot skills can be represented without special cases.
  - Completed: schema files added and pilot metadata generated under `catalog/`.

- [x] **Decide canonical skill storage layout**
  - Decision: canonical catalog skills live under `skills/<skill-id>/SKILL.md`.
  - Acceptance: existing pilot skills have a clear migration path from legacy plugin paths.
  - Completed: pilot skills were ingested with `python -m skillforge upload ...`, not moved manually.

- [x] **Scaffold Python package**
  - Output: `skillforge/__main__.py`, `skillforge/cli.py`, `skillforge/catalog.py`, `skillforge/validate.py`, `skillforge/install.py`
  - Acceptance: `python -m skillforge --help` runs locally.
  - Completed: CLI exposes `validate`, `upload`, `download`, `search`, `info`, `install`, `remove`, `list`, `doctor`, and `build-catalog`.

## Next

- [x] **Implement `validate`**
  - Checks: `SKILL.md` exists, valid YAML frontmatter, required `name` and `description`, folder/name mismatch warning, referenced files exist, suspicious file types warned.
  - Acceptance: validates both pilot skills and returns nonzero for malformed fixtures.
  - Completed: both pilot legacy skill folders validate.

- [x] **Implement catalog generation**
  - Command: `python -m skillforge build-catalog`
  - Outputs: `catalog/skills.json`, `catalog/skills/<skill-id>.json`
  - Acceptance: generated files are deterministic and stable across repeated runs.
  - Completed: generated aggregate and per-skill metadata for both pilot skills.

- [x] **Implement `search`**
  - Scope: local catalog first; exact ID, keyword, tag, and basic task text matching.
  - Acceptance: `get-youtube-media` is found for video/transcript/research queries.
  - Completed: smoke-tested task search for YouTube/research and retrospective/project memory.

- [x] **Implement `info`**
  - Output: human-readable summary and `--json`.
  - Acceptance: shows source path, checksum, description, tags, files, and install command.
  - Completed: `info` returns human-readable and JSON metadata.

- [x] **Implement Codex install**
  - Commands: `install <skill-id> --scope global`, `install <skill-id> --scope project --project <path>`, `remove <skill-id> --scope <scope> --yes`
  - Behavior: download/copy from catalog source, validate before install, avoid executing scripts, copy or symlink into Codex skill path, remove installed skills only after explicit confirmation.
  - Acceptance: install/remove works for both pilot skills in a test Codex home and test project folder.
  - Completed: global-scope install/remove is covered with an overridden test path; project-scope install/remove smoke-tested with an ignored demo project.

- [x] **Implement `list` and `doctor`**
  - `list`: show installed Codex skills.
  - `doctor`: report detected Codex paths and missing directories.
  - Acceptance: commands work on a clean machine and return useful JSON.
  - Completed: smoke-tested `list --scope project --project . --json` and `doctor --project . --json`.

## Quality Gates

- [x] Add unit tests for validation, search ranking, metadata loading, and install path resolution.
- [ ] Add fixture skills: valid minimal, valid with references, malformed frontmatter, missing `SKILL.md`, suspicious script.
- [ ] Add CI workflow to run tests and catalog generation checks.
- [ ] Add formatting/linting for Python.
- [ ] Add a generated-files check so stale catalog output fails CI.

## Documentation

- [ ] Keep `README.md` user-facing and terse.
- [ ] Keep `requirements.md` as the product contract.
- [ ] Add `docs/catalog-schema.md`.
- [ ] Add `docs/codex-install-paths.md`.
- [ ] Add `docs/contributing-skills.md`.

## Peer Catalogs

- [ ] Define peer catalog adapter interface.
- [ ] Implement local/static `skills.json` adapter first.
- [ ] Implement GitHub skill repo adapter later.
- [ ] Keep `skills.sh` disabled until source provenance and adapter behavior are verified.

## Backlog

- Trust/risk scoring.
- Human review workflow.
- NeMoClaw install target.
- Cursor install target.
- HTML catalog generator.
- `uvx` or `pipx` packaging.
- Enterprise allowlists and private catalogs.
- Trigger evals and task evals.
