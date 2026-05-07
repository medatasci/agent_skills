# `skillforge/improvement_loop.py`

Strategic improvement-loop planning, run-log scaffolding, healthcare source
focus, and advisory concurrency locks for recurring SkillForge automation.

Use this document when a human or agent needs to understand, modify, or review
the Python module without reverse-engineering the whole package.

## Responsibilities

This module owns:

- Selecting or continuing a strategic SkillForge improvement focus.
- Returning healthcare-focused source priorities for NVIDIA-Medtech, MONAI, and
  codebase-to-agentic-skills work.
- Writing unique Markdown run-log stubs.
- Creating and releasing advisory active-run locks for overlapping scheduled
  jobs.
- Reporting a Git snapshot so automation can work on reviewable branches or
  worktrees.

This module does not own:

- Codex automation scheduling; use the Codex app automation API.
- Implementing the improvement task itself; the agent performs the selected
  work after reading the plan.
- Publishing, merging, pushing, dependency installation, model downloads, or
  authenticated GitHub writes.

## When To Edit This Module

Edit this module when:

- The improvement-loop focus selection logic changes.
- Run-log sections, concurrency behavior, or lock semantics change.
- Healthcare source priorities or strategic lanes change.
- `improve-cycle --json` fields change.

Choose another module when:

- CLI argument registration changes; edit `skillforge/cli.py`.
- Help topic text changes; edit `skillforge/help.py`.
- Skill instructions or human-facing docs change; edit
  `skills/skillforge-strategic-improvement-loop/` or
  `docs/improvement-loop/`.

## Commands Or Workflows

Commands, workflows, or APIs backed by this module:

```text
python -m skillforge improve-cycle --json
python -m skillforge improve-cycle --write-log --claim-run --json
python -m skillforge improve-cycle --release-run <run-id> --json
```

Related commands:

- `python -m skillforge help improvement-loop`
- `python -m skillforge codebase-scan <repo-path> --workflow-goal "..."`

## Inputs And Reads

This module reads:

- `docs/improvement-loop/state.json`
- `docs/improvement-loop/backlog.md`
- Git branch, commit, remote, last commit date, and dirty status.

Important environment variables:

- None owned by this module.
- Git environment variables may affect subprocess behavior, but this module
  does not set them.

## Outputs And Writes

This module writes:

- Markdown run-log stubs when `--write-log` is used.
- An advisory active-run lock when `--claim-run` is used.
- Lock removal when `--release-run <run-id>` is used.
- An alternate advisory lock path when `--lock-path` is supplied for isolated
  tests or advanced automation.

Generated or modified files:

```text
docs/improvement-loop/runs/<timestamp>-<run-id>.md
.skillforge/improvement-loop/active-run.json
```

`python -m skillforge improve-cycle --json` is read-only when neither
`--write-log` nor `--claim-run` is supplied.

## Side Effects And Safety

Risk level:
medium

Network access:
None. The module only reports source URLs for the agent to consider.

Filesystem writes:
Run logs and advisory lock files only.

External commands:
Git status commands using subprocess argument lists with `shell=False`.

User confirmation gates:

- Writing a log requires `--write-log`.
- Claiming a lock requires `--claim-run`.
- Releasing a lock requires the matching run ID.
- Tests should use `--lock-path` under `test-output/` so they do not remove or
  replace a live automation lock.

Safety notes:

- The lock is advisory and local. It reduces accidental collisions but is not a
  security model.
- A concurrent run should avoid editing shared files when an active lock is
  present.
- The recurring agent must not merge, push, publish, install dependencies,
  download models, use credentials, or run expensive jobs without explicit
  human approval.

## Public Functions And Data Contracts

Important functions, classes, or data structures:

- `improvement_cycle(...)`: returns the stable plan/log/concurrency payload for
  the CLI.
- `claim_run_lock(...)`: creates the advisory active-run lock or reports the
  current active run.
- `release_run_lock(...)`: removes the advisory active-run lock when the run ID
  matches.
- `repo_snapshot(...)`: returns branch, commit, origin, dirty state, and changed
  files.

Stable JSON fields or return payloads:

- `run_id`, `selected_lane`, `focus`, `healthcare_sources`, `repo_snapshot`,
  `concurrency`, `suggested_actions`, `warnings`, `side_effects`, and
  `log_path`.
- Release action fields include `released`, `lock_path`, and `message`.

Compatibility notes:

- Keep JSON field names stable for calling LLMs and scheduled automations.
- Keep file writes explicit and scoped to run logs or `.skillforge/` locks.

## Cross-Platform Notes

Windows, macOS, and Linux considerations:

- Use `pathlib.Path` for all paths.
- Use subprocess argument lists with `shell=False`.
- Use `git -c safe.directory=<repo>` to tolerate managed workspaces and
  sandbox users.
- Store the advisory lock under `.skillforge/`, which is ignored by Git.

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

- `improve-cycle --json` is read-only and returns a healthcare-focused plan.
- `improve-cycle --write-log --claim-run --json` writes a unique log and lock.
- A second claimed run reports an active run instead of silently taking over.
- `improve-cycle --release-run <run-id> --json` releases the matching lock.

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
- `docs/improvement-loop/README.md`
- `skills/skillforge-strategic-improvement-loop/README.md`
