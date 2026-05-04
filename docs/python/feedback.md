# `skillforge/feedback.py`

Structured GitHub issue feedback draft module for skills, CLI commands,
helpers, documentation, and missing workflows.

Use this document when a human or agent needs to understand, modify, or review
the Python module without reverse-engineering the whole package.

## Responsibilities

This module owns:

- Turning feedback fields into a GitHub issue title and body.
- Producing a feedback-screen payload for humans and agents.
- Keeping feedback drafting read-only.

This module does not own:

- Authenticated GitHub issue creation.
- Search, install, or skill evaluation behavior.
- Pull request contribution drafting; use `contribute.py`.

## When To Edit This Module

Edit this module when:

- Feedback issue fields, body structure, or URL generation should change.
- Feedback should support new subject types.
- The feedback screen needs clearer user-facing labels.

Choose another module when:

- Feedback appears in README examples only.
- A user has a concrete bug fix, feature, docs change, catalog update, or new
  skill to submit as a pull request; use `contribute.py`.

## Commands Or Workflows

Commands, workflows, or APIs backed by this module:

```text
python -m skillforge feedback <subject> --trying "..." --happened "..."
python -m skillforge feedback <subject> --json
FeedbackDraft(...).as_dict()
```

Related commands:

- `python -m skillforge help feedback`
- `python -m skillforge contribute "<summary>" --type feature --json`
- Future authenticated issue submission command.

## Inputs And Reads

This module reads:

- Feedback subject.
- What the user was trying to do.
- What happened, outcome, suggestion, and optional title.

Important environment variables:

- None.
- GitHub authentication is not used by this module.

## Outputs And Writes

This module writes:

- Nothing directly.
- It returns JSON-ready feedback drafts to the CLI.

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

- Authenticated issue creation is out of scope.
- Users or agents should review the draft before posting.

Safety notes:

- Do not include secrets or private/internal data in generated issue text.
- Keep issue URLs clear and editable.

## Public Functions And Data Contracts

Important functions, classes, or data structures:

- `FeedbackDraft`: dataclass that stores feedback inputs.
- `FeedbackDraft.as_dict()`: returns the issue draft payload.
- Issue URL generation: points to the SkillForge GitHub issue surface.

Stable JSON fields or return payloads:

- `title`, `issue_url`, `screen`, and `body`.
- Screen fields include labels and values for human review.

Compatibility notes:

- Subject can be a skill ID, CLI command, Python helper, docs area, or missing workflow.
- Keep defaults helpful when optional outcome or suggestion is absent.
- Feedback is for issue-style reports and ideas. Contribution PR drafts belong
  to `skillforge/contribute.py`.

## Cross-Platform Notes

Windows, macOS, and Linux considerations:

- Generated Markdown should use plain text and stable newlines.
- No shell behavior is required.
- URLs should be web URLs, not local file paths.

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

- Feedback CLI JSON is parseable.
- Issue title and screen fields are present.
- Feedback drafting does not submit or write anything.

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
- `docs/python/help.md`
- `docs/python/contribute.md`
- `README.md`
