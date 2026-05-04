# `codebase_to_agentic_skills.py`

Deterministic source-context scanner for the `codebase-to-agentic-skills`
SkillForge skill.

Use this document when a human or agent needs to understand, modify, or review
the helper without reading the full skill package.

## Responsibilities

This helper owns:

- Scanning a local repository without running its code.
- Classifying source artifacts into evidence categories such as README files,
  docs, scripts, configs, examples, dependencies, model/data/paper sources, and
  license/security files.
- Returning stable JSON for agents.
- Optionally writing draft Markdown artifacts when `--output-dir` is supplied.

This helper does not own:

- Deciding which candidate skills are safe to publish.
- Reading full source files deeply enough to make unsupported claims.
- Cloning repositories, downloading assets, installing dependencies, or running
  upstream code.
- Submitting pull requests or modifying SkillForge catalog files.

## Commands

```text
python skills/codebase-to-agentic-skills/scripts/codebase_to_agentic_skills.py check --json
python skills/codebase-to-agentic-skills/scripts/codebase_to_agentic_skills.py schema --json
python skills/codebase-to-agentic-skills/scripts/codebase_to_agentic_skills.py scan <repo-path> --workflow-goal "<goal>" --json
python skills/codebase-to-agentic-skills/scripts/codebase_to_agentic_skills.py scan <repo-path> --workflow-goal "<goal>" --output-dir docs/reports/<repo>-repo-to-skills --json
```

The same scan workflow is also exposed through the top-level SkillForge CLI:

```text
python -m skillforge codebase-scan <repo-path> --workflow-goal "<goal>" --json
```

## Inputs And Outputs

Inputs:

- `repo_path`: local repository or codebase directory.
- `--workflow-goal`: user-facing reason for the scan.
- `--max-files-per-category`: cap on evidence samples per category.
- `--max-total-files`: cap on files inspected.
- `--output-dir`: optional directory for generated drafts.

Outputs:

- JSON payload with `source_context_map`, file counts, source version, and next
  steps.
- Optional `scan.json`.
- Optional `source-context-map.md`.
- Optional `candidate-skill-table.md`.
- Optional `readiness-card-draft.md`.

## Side Effects And Safety

Risk level:
low

Network access:
none

Filesystem writes:
only when `scan --output-dir` is provided

External commands:
`git rev-parse HEAD` when Git is available, used only to record local source
version. The helper does not fetch, pull, clone, install, or run upstream code.

## Tests

Primary test:

```text
python -m unittest tests.test_skillforge.SkillForgeTests.test_codebase_to_agentic_skills_scanner_generates_source_context_outputs
```

Acceptance checks:

- The direct script command returns parseable JSON.
- The top-level `python -m skillforge codebase-scan` command delegates to the
  same scanner.
- Output files are written only when `--output-dir` is provided.

