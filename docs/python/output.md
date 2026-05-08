# `skillforge/output.py`

Chattiness mode parsing and shared output preference helpers.

Use this document when a human or agent needs to understand, modify, or review
the Python module without reverse-engineering the whole package.

## Responsibilities

This module owns:

- Normalizing chattiness modes.
- Adding the shared `--chattiness` CLI argument.
- Providing small helpers for coach, normal, terse, and silent behavior.

This module does not own:

- Rendering help content; use `help.py`.
- Command-specific output text; use `cli.py` and the command owner.

## When To Edit This Module

Edit this module when:

- Chattiness modes are added, removed, or renamed.
- `SKILLFORGE_CHATTINESS` behavior changes.
- Shared output-mode helper behavior changes.

Choose another module when:

- A specific command should become more or less verbose.
- Persistent config is added; create or update a config owner.

## Commands Or Workflows

Commands, workflows, or APIs backed by this module:

```text
python -m skillforge help --chattiness coach
python -m skillforge search "task" --chattiness terse
python -m skillforge corpus-search "task" --chattiness silent
```

Related commands:

- `python -m skillforge getting-started --chattiness terse`
- `SKILLFORGE_CHATTINESS=coach`

## Inputs And Reads

This module reads:

- CLI `--chattiness` values.
- `SKILLFORGE_CHATTINESS`.
- Default chattiness constants.

Important environment variables:

- `SKILLFORGE_CHATTINESS`: Default mode when no command flag is provided. If it
  is unset, SkillForge defaults to `coach` for new-user friendliness.
- None else.

## Outputs And Writes

This module writes:

- Nothing.
- It returns normalized mode strings and parser configuration.

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

- Silent mode must not suppress required confirmations.
- Warnings and errors should still be available for risky operations.

Safety notes:

- `--json` must remain stable regardless of chattiness.
- Invalid environment values should fall back to `normal`.

## Public Functions And Data Contracts

Important functions, classes, or data structures:

- `normalize_chattiness(value)`: returns a supported mode.
- `add_chattiness_argument(parser)`: adds the shared CLI flag.
- `is_coach()`, `is_normal_or_coach()`, and `is_silent()`: helper predicates.

Stable JSON fields or return payloads:

- None.
- Supported modes are `coach`, `normal`, `terse`, and `silent`.

Compatibility notes:

- Keep `coach` as the default for users without an explicit preference.
- Additive mode changes should update docs, tests, and requirements.

## Cross-Platform Notes

Windows, macOS, and Linux considerations:

- Environment variable setting syntax differs by shell; Python only reads `os.environ`.
- Do not emit shell-specific examples from this module.
- Keep parser choices lowercase and ASCII.

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

- Supported commands accept `--chattiness`.
- Unset chattiness defaults to coach-level guidance.
- Coach mode can add next steps.
- Silent mode suppresses extra prose but not JSON.

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
- `docs/python/help.md`
