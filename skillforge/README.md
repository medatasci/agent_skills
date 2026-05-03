# SkillForge Python Package

This package contains the deterministic Python side of SkillForge. It is the
part agents and humans call when they need repeatable behavior instead of
improvised file copying or prompt-only workflows.

## Module Map

- `cli.py`: command-line entry point and human/JSON output formatting.
- `catalog.py`: local catalog generation, search index generation, static site
  generation, local search, and publication evaluation.
- `install.py`: Codex install, remove, list, download, and path resolution.
- `peer.py`: peer catalog loading, peer cache, provider catalog corpus search,
  peer install, peer import, and diagnostics.
- `validate.py`: structural validation for local skill folders.
- `create.py`: template-backed skill creation.
- `feedback.py`: structured feedback issue drafts.
- `filesystem.py`: cross-platform copy/remove helpers and transient artifact
  filtering.
- `help.py`: hardcoded welcome text, workflow help, and first-run guidance content.
- `output.py`: chattiness mode parsing and shared output preferences.
- `update.py`: read-only upstream update checks and Git-derived "what changed"
  summaries.

For machine-readable ownership metadata, see `modules.toml`.

## Agent Editing Guidance

Start from the command a user invoked, then follow ownership:

- CLI parsing or output wording: edit `cli.py` and, for help text, `help.py`.
- Catalog JSON, static pages, search indexes, or evaluation: edit `catalog.py`.
- Peer search, provider cache, or peer install: edit `peer.py`.
- Codex install paths or remove/list behavior: edit `install.py`.
- Skill validation rules: edit `validate.py`.
- Welcome, first-run, or help content: edit `help.py`.
- Update awareness: edit `update.py`.

Keep commands deterministic. Prefer JSON output for agent workflows and avoid
side effects in commands that are documented as read-only.

## Side-Effect Boundaries

Read-only commands include `search`, `info`, `evaluate`, `search-audit`,
`doctor`, `welcome`, `help`, `getting-started`, and `whats-new`.

Commands that may write local files include `create`, `upload`,
`build-catalog`, `install`, `download`, `remove`, `import-peer`, `feedback`
only when a future authenticated submit mode is added, and peer/cache commands.

`update-check` may run a Git fetch when cache is stale, but it must not modify
working tree files. `whats-new` is read-only.

## Output Modes

Selected commands support:

- `--chattiness coach`
- `--chattiness normal`
- `--chattiness terse`
- `--chattiness silent`

The environment variable `SKILLFORGE_CHATTINESS` sets the default for supported
commands. JSON output must remain stable regardless of chattiness.

Hardcoded welcome and help responses are intentional. They provide a stable
novice entrypoint before an LLM has inferred user intent or project context.
