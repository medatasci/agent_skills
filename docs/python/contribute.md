# `skillforge/contribute.py`

Read-only pull request draft module for SkillForge contributions.

Use this document when a human or agent needs to understand, modify, or review
the Python module without reverse-engineering the whole package.

## Responsibilities

This module owns:

- Turning a proposed bug fix, feature, docs change, catalog change, or skill
  contribution into pull request draft metadata.
- Generating a branch name, pull request title, pull request body, compare URL,
  and suggested GitHub CLI command.
- Recording contributor profile so the output can distinguish developer and
  non-developer guidance.
- Making the PR-first contribution boundary explicit for non-maintainer users.

This module does not own:

- Running `git` commands.
- Pushing branches or creating authenticated GitHub pull requests.
- Feedback issue drafting; that belongs to `skillforge/feedback.py`.

## When To Edit This Module

Edit this module when:

- Pull request draft fields or wording should change.
- Contribution types, branch naming, or review checklist behavior changes.
- SkillForge adds authenticated PR creation in a separate, confirmation-gated
  workflow and this draft payload needs to support it.

Choose another module when:

- A user is only reporting a bug or requesting a feature without a local change;
  use `feedback.py`.
- CLI parser wiring or human output formatting changes; use `cli.py`.

## Commands Or Workflows

Commands, workflows, or APIs backed by this module:

```text
python -m skillforge contribute "<summary>" --type docs --json
python -m skillforge contribute "<summary>" --changed README.md --check "python -m unittest tests.test_skillforge"
ContributionDraft(...).as_dict()
```

Related commands:

- `python -m skillforge feedback <subject> --trying "..." --happened "..."`
- `python -m skillforge help contribute`

## Inputs And Reads

This module reads:

- Contribution summary.
- Contribution type.
- Optional why, changed files, checks, safety note, title, branch, and base
  branch.
- Optional contributor profile: `unknown`, `non-developer`, or `developer`.

Important environment variables:

- None.
- GitHub authentication is not used by this module.

## Outputs And Writes

This module writes:

- Nothing directly.
- It returns JSON-ready pull request draft data to the CLI.

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

- Authenticated branch push is out of scope.
- Authenticated pull request creation is out of scope.

Safety notes:

- Do not imply that draft commands have already run.
- Do not encourage pushing directly to `main` for non-maintainer users.
- Generated PR bodies should remind reviewers to check for secrets, private
  data, and unintended generated-file churn.

## Public Functions And Data Contracts

Important functions, classes, or data structures:

- `ContributionDraft`: dataclass that stores proposed contribution inputs.
- `ContributionDraft.as_dict()`: returns the pull request draft payload.
- `slugify(...)`: creates stable branch-name fragments.

Stable JSON fields or return payloads:

- `intent`, `title`, `branch`, `base`, `contributor_profile`,
  `manual_pr_url`, `body`, `promptable_request`, `commands`,
  `direct_push_to_main`, `side_effects`, `next_steps`, `fields`, and
  `review_checklist`.
- `direct_push_to_main` must remain `false` for normal contribution drafts.

Compatibility notes:

- Summary can describe a skill, Python helper, CLI command, docs update, or
  generated catalog update.
- Contributor profile changes guidance only; it is not a permission check,
  identity assertion, or trust score.
- The module should stay deterministic and should not inspect local Git state.

## Cross-Platform Notes

Windows, macOS, and Linux considerations:

- Branch names use forward slashes because Git branch names are platform
  independent.
- Generated commands are examples for humans and agents; the module does not
  execute shell commands.
- Changed files should be provided as repository-relative paths.

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

- PR draft JSON is parseable.
- Branch, title, PR body, commands, and manual PR URL are present.
- Contributor profile and next steps are present.
- Contribution drafting remains read-only and PR-first.

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
- `docs/python/feedback.md`
- `README.md`
