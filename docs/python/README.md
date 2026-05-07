# SkillForge Python Internals

These docs help humans and agents understand where to make changes in the
SkillForge Python package.

Use this directory with:

- `skillforge/README.md` for the package overview.
- `skillforge/modules.toml` for machine-readable module ownership.
- `skillforge/templates/python/module.md.tmpl` for new module docs.
- The source files in `skillforge/`.
- The tests in `tests/test_skillforge.py`.

## Recommended Agent Workflow

1. Identify the command or behavior being changed.
2. Read the matching module doc in this directory.
3. Read the module source.
4. Update tests for the behavior.
5. Run `python -m unittest tests.test_skillforge`.

## Module Docs

- `cli.md`: command registration and output routing.
- `catalog.md`: catalog, search index, static site, template conformance, and evaluation pipeline.
- `clinical_statistical_expert.md`: clinical-statistical disease chapter HTML previews.
- `contribute.md`: read-only pull request contribution drafts and review checklists.
- `create.md`: template-backed skill scaffolding.
- `feedback.md`: structured feedback issue drafts.
- `filesystem.md`: cross-platform copy/remove helpers and transient artifact filtering.
- `figure_evidence.md`: disease-chapter figure evidence manifests and conservative local image copying.
- `help.md`: first-run guidance and workflow help API.
- `improvement_loop.md`: strategic recurring improvement-loop planning, run logs, and advisory concurrency locks.
- `install.md`: Codex install, remove, list, and download behavior.
- `output.md`: chattiness mode parsing and shared output preferences.
- `peer.md`: federated peer discovery, cache, corpus search, and peer import.
- `source_archive.md`: disease-chapter source metadata manifests and ignored local source caching.
- `update.md`: update-check and Git-derived what-changed summaries.
- `validate.md`: structural skill validation and safe file iteration.

## Template

New module docs should start from:

```text
skillforge/templates/python/module.md.tmpl
```

Fill every placeholder, remove irrelevant sections only when they truly do not
apply, and update `skillforge/modules.toml` so the source module points to the
new doc.
