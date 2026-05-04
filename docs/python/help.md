# `skillforge/help.py`

Workflow help, natural-language topic routing, and first-run guidance content
for SkillForge.

Use this document when a human or agent needs to understand, modify, or review
the Python module without reverse-engineering the whole package.

## Responsibilities

This module owns:

- Hardcoded novice welcome text.
- Topic-based help payloads for humans and calling LLMs.
- Deterministic natural-language routing to help topics.
- Human rendering for help and getting-started content.

This module does not own:

- Argparse command registration; use `cli.py`.
- Persistent user configuration; future work outside this module.

## When To Edit This Module

Edit this module when:

- A new command should appear in help.
- First-run guidance or prompt examples should change.
- Natural-language help routing should map a user phrase to a different topic.

Choose another module when:

- A command's actual behavior changes; edit the command owner too.
- Chattiness parsing changes; use `output.py`.

## Commands Or Workflows

Commands, workflows, or APIs backed by this module:

```text
python -m skillforge welcome
python -m skillforge help
python -m skillforge help search
python -m skillforge help codebase
python -m skillforge help contribute
python -m skillforge getting-started
```

Related commands:

- `python -m skillforge help --json`
- `python -m skillforge help "I need a skill for writing status emails"`

## Inputs And Reads

This module reads:

- Hardcoded welcome hints in `skillforge/help.py`.
- Help topic strings.
- Natural-language help requests.
- Chattiness mode passed from the CLI.

Important environment variables:

- `SKILLFORGE_CHATTINESS`: Parsed by `output.py`, then passed into render helpers.
- None directly.

## Outputs And Writes

This module writes:

- Nothing directly.
- It returns strings and JSON-ready payloads to `cli.py`.

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

- Help should recommend review before peer install.
- Help should distinguish issue feedback from pull request contributions.
- Help should not execute commands or imply install approval.

Safety notes:

- Keep help practical and truthful about side effects.
- Make `--json` useful for calling LLMs.

## Public Functions And Data Contracts

Important functions, classes, or data structures:

- `help_payload(topic)`: returns a JSON-ready topic payload.
- `welcome_payload()`: returns the hardcoded first-time user welcome.
- `render_welcome(payload, chattiness)`: renders novice-facing welcome text.
- `getting_started_payload()`: returns first-run guidance steps.
- `render_help(payload, chattiness)`: renders human text.

Stable JSON fields or return payloads:

- Welcome payloads include `topic`, `title`, `message`, `start`, `examples`,
  `question`, `next_steps`, and `commands`.
- `topic`, `summary`, `commands`, `prompt_examples`, and `next_steps`.
- Command entries include `command`, `description`, `side_effects`, `examples`, and `related`.

Compatibility notes:

- Help payloads should remain additive when possible.
- Avoid removing topics without updating README and tests.

## Cross-Platform Notes

Windows, macOS, and Linux considerations:

- Keep command examples using `python -m skillforge`.
- Avoid shell-specific environment syntax in generated help.
- Keep paths repository-relative when possible.

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

- `welcome --json` returns novice prompt examples.
- `help search --json` returns topic `search`.
- `help "repo to skills" --json` returns topic `codebase`.
- `help contribute --json` returns a PR-first, read-only contribution workflow.
- `getting-started --json` returns doctor/search/info/install/list steps.
- Human terse output remains short.

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
- `docs/python/contribute.md`
- `docs/python/output.md`
