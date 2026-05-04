# `skillforge/validate.py`

Structural skill validation and safe skill-file iteration rules.

Use this document when a human or agent needs to understand, modify, or review
the Python module without reverse-engineering the whole package.

## Responsibilities

This module owns:

- Validating a local skill folder has a usable `SKILL.md`.
- Parsing frontmatter and required metadata.
- Checking SkillForge-owned skills for the readable agent-contract shape used
  by the `SKILL.md` template.
- Iterating skill files while excluding transient platform/runtime artifacts.
- Warning when SkillForge-owned guarded execution skills lack a
  runtime/deployment plan.

This module does not own:

- Publication-readiness scoring; use `catalog.py`.
- Installing or copying skill folders; use `install.py` and `filesystem.py`.

## When To Edit This Module

Edit this module when:

- Required or recommended skill metadata checks change.
- The required or recommended `SKILL.md` top-section shape changes.
- Suspicious file, URL, script, or reference warnings change.
- Runtime/deployment planning warnings for code-backed skills change.
- Transient artifact filtering should change for validation/checksums.

Choose another module when:

- Generated catalog metadata changes; use `catalog.py`.
- Peer parser tolerance changes; use `peer.py` unless it should apply locally too.

## Commands Or Workflows

Commands, workflows, or APIs backed by this module:

```text
python -m skillforge validate <skill-path>
python -m skillforge validate <skill-path> --json
validate_skill(path)
```

Related commands:

- `python -m skillforge evaluate <skill-id> --json`
- `python -m skillforge upload <path> --owner <owner>`

## Inputs And Reads

This module reads:

- `SKILL.md`
- Referenced local files inside a skill folder.
- Skill folder file names and suffixes.

Important environment variables:

- None directly.
- Test overrides may affect callers but not validation itself.

## Outputs And Writes

This module writes:

- Nothing.
- It returns validation payloads and file iteration results.

Generated or modified files:

```text
None.
```

This module is read-only.

## Side Effects And Safety

Risk level:
low

Network access:
None.

Filesystem writes:
None.

External commands:
None.

User confirmation gates:

- None inside this module.
- Callers decide whether warnings block install or publication.

Safety notes:

- Prefer warnings for portable-skill compatibility unless a malformed skill must fail.
- Do not execute scripts or import code from skill folders.

## Public Functions And Data Contracts

Important functions, classes, or data structures:

- `validate_skill(path)`: returns a `SkillValidation` object.
- `parse_frontmatter(text)`: returns metadata and parse errors.
- `iter_skill_files(skill_dir)`: yields non-transient files for checksums/copy logic.

Stable JSON fields or return payloads:

- `ok`, `metadata`, `errors`, and `warnings`.
- `SkillValidation.skill_dir` identifies the validated folder.

Compatibility notes:

- Minimal portable skills with `name` and `description` should still pass.
- SkillForge-owned skills may receive additional discovery warnings.
- SkillForge-owned skills should begin with a readable agent contract:
  frontmatter, a Markdown H1, `## What This Skill Does`, and
  `## Safe Default Behavior` before generated discovery metadata.
- SkillForge-owned skills that expose guarded execution markers such as
  `--confirm-execution` should include runtime/deployment documentation
  covering install location, OS/runtime target, dependency setup, model/data
  download policy, license review, environment checks, smoke-test data, and
  rollback/cleanup notes.

## Cross-Platform Notes

Windows, macOS, and Linux considerations:

- Ignore `.DS_Store`, `Thumbs.db`, `__pycache__`, and `*.pyc`.
- Use `pathlib.Path`.
- Do not rely on case-sensitive filesystems.

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

- Valid pilot skills pass.
- Missing or malformed `SKILL.md` fails.
- Platform artifacts are ignored.
- SkillForge-owned skills without a readable H1 or required top sections warn.
- Guarded execution skills warn without runtime/deployment planning docs.
- Guarded execution skills with complete runtime/deployment planning docs do
  not emit the runtime-planning warning.

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
- `docs/python/catalog.md`
- `docs/python/filesystem.md`
