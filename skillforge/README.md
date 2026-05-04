# SkillForge Python Package

This package contains the deterministic Python side of SkillForge. It is the
part agents and humans call when they need repeatable behavior instead of
improvised file copying or prompt-only workflows.

## Module Map

- `cli.py`: command-line entry point and human/JSON output formatting.
- `catalog.py`: local catalog generation, search index generation, static site
  generation, local search, and publication evaluation.
- `install.py`: Codex skill install, SkillForge marketplace verification,
  remove, list, download, and path resolution.
- `peer.py`: peer catalog loading, peer cache, provider catalog corpus search,
  peer install, peer import, and diagnostics.
- `validate.py`: structural validation for local skill folders.
- `create.py`: template-backed skill creation.
- `feedback.py`: structured feedback issue drafts.
- `contribute.py`: read-only pull request contribution drafts.
- `filesystem.py`: cross-platform copy/remove helpers and transient artifact
  filtering.
- `help.py`: hardcoded welcome text, workflow help, and first-run guidance content.
- `output.py`: chattiness mode parsing and shared output preferences.
- `update.py`: periodic upstream update checks, conservative fast-forward
  updates, and Git-derived "what changed" summaries.

For machine-readable ownership metadata, see `modules.toml`.

## Agent Editing Guidance

Start from the command a user invoked, then follow ownership:

- CLI parsing or output wording: edit `cli.py` and, for help text, `help.py`.
- Catalog JSON, static pages, search indexes, or evaluation: edit `catalog.py`.
- Peer search, provider cache, or peer install: edit `peer.py`.
- Codex install paths, SkillForge marketplace install checks, or remove/list
  behavior: edit `install.py`.
- Skill validation rules: edit `validate.py`.
- Welcome, first-run, or help content: edit `help.py`.
- Update awareness: edit `update.py`.

Keep commands deterministic. Prefer JSON output for agent workflows and avoid
side effects in commands that are documented as read-only.

## Side-Effect Boundaries

Read-only commands include `search`, `info`, `evaluate`, `search-audit`,
`doctor`, `welcome`, `help`, `getting-started`, `update-check`, and
`whats-new`.

Commands that may write local files include `create`, `upload`,
`build-catalog`, `install`, `download`, `remove`, `import-peer`, `update --yes`,
`install-skillforge --yes`, `feedback` only when a future authenticated submit
mode is added, and peer/cache commands.

`contribute` is read-only. It drafts pull request metadata, suggested Git
commands, and review notes, but it does not run Git, push a branch, or create a
pull request.

`install-skillforge --json` is read-only and should be safe to run repeatedly.
It verifies the marketplace checkout and Codex config. `install-skillforge
--yes` may append missing non-conflicting config entries, but it must not
overwrite an existing non-SkillForge folder or conflicting config.

`update-check` may run a Git fetch when cache is stale, but it must not modify
working tree files. `update --yes` may modify repository files only through a
clean fast-forward Git update. `whats-new` is read-only.

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
