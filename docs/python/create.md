# `skillforge/create.py`

Template-backed skill scaffolding module for new local SkillForge skills.

Use this document when a human or agent needs to understand, modify, or review
the Python module without reverse-engineering the whole package.

## Responsibilities

This module owns:

- Creating `skills/<skill-id>/SKILL.md` from the skill template.
- Creating `skills/<skill-id>/README.md` from the skill README template.
- Returning placeholder and next-command metadata for new skills.

This module does not own:

- Publishing or installing the generated skill.
- Deterministic publication evaluation; use `catalog.py`.

## When To Edit This Module

Edit this module when:

- `python -m skillforge create` should scaffold different files.
- Template placeholder replacement behavior changes.
- New create flags need to flow into generated source files.

Choose another module when:

- The template content itself changes; edit `skillforge/templates/skill/`.
- Validation rules for generated skills change; edit `validate.py`.

## Commands Or Workflows

Commands, workflows, or APIs backed by this module:

```text
python -m skillforge create <skill-id>
python -m skillforge create <skill-id> --title "..." --description "..."
python -m skillforge create <skill-id> --json
```

Related commands:

- `python -m skillforge build-catalog`
- `python -m skillforge evaluate <skill-id> --json`

## Inputs And Reads

This module reads:

- `skillforge/templates/skill/SKILL.md.tmpl`
- `skillforge/templates/skill/README.md.tmpl`
- CLI metadata values such as title, description, owner, tags, and risk level.

Important environment variables:

- None directly.
- `SKILLFORGE_CHATTINESS` affects command output only through `cli.py`.

## Outputs And Writes

This module writes:

- New skill source folders under `skills/<skill-id>/`.
- `SKILL.md` and `README.md` files from templates.

Generated or modified files:

```text
skills/<skill-id>/SKILL.md
skills/<skill-id>/README.md
```

This module does not build catalog outputs or install the skill.

## Side Effects And Safety

Risk level:
medium

Network access:
None.

Filesystem writes:
Creates local skill source files.

External commands:
None.

User confirmation gates:

- Existing folders require explicit force behavior from the CLI.
- Generated placeholder claims must be reviewed before publication.

Safety notes:

- Do not invent trust, permission, owner, or capability claims.
- Leave visible placeholders when information is unknown.

## Public Functions And Data Contracts

Important functions, classes, or data structures:

- `create_skill(...)`: creates the skill folder and returns a JSON-ready payload.
- Template placeholder maps: convert CLI metadata into template substitutions.
- Placeholder detection: reports unresolved placeholders.

Stable JSON fields or return payloads:

- `skill_id`, `skill_dir`, `files`, `placeholders_remaining`, and `next_commands`.
- `validation`: structural validation result for the generated skill.

Compatibility notes:

- Generated skills should validate structurally even before placeholder cleanup.
- Generated skills should remain portable `SKILL.md` folders.

## Cross-Platform Notes

Windows, macOS, and Linux considerations:

- Use `pathlib.Path` for skill paths.
- Keep generated text UTF-8.
- Avoid platform-specific line endings in generated templates where possible.

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

- `create` writes both `SKILL.md` and `README.md`.
- `evaluate` flags unresolved placeholders.
- `create` does not publish, install, or modify peer catalogs.

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
- `docs/templates.md`
- `docs/python/validate.md`
