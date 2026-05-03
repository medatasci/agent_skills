# SkillForge Software Development TODO

Updated: 2026-05-02

Source of truth:

- Product requirements: `requirements.md`
- User entrypoint: `README.md`
- Template guide: `docs/templates.md`
- White paper draft: `docs/skillforge-whitepaper.md`
- Peer catalog seed: `peer-catalogs.json`
- Planning/archive TODO: `skillforge-planning-todo.md`

## MVP Definition

SkillForge MVP is a Codex-only, GitHub-backed skill catalog with a package-style Python CLI:

```text
python -m skillforge search "task X" --json
python -m skillforge info <skill-id>
python -m skillforge install <skill-id> --scope global
python -m skillforge install <skill-id> --scope project --project .
python -m skillforge install <skill-id> --peer <peer-id> --yes
python -m skillforge feedback <skill-id> --trying "..." --happened "..."
```

## Now

- [x] **Define catalog schema**
  - Output: `schemas/skills.schema.json`, `schemas/skill.schema.json`
  - Include: skill ID, name, description, owner, tags, source path, source URL, checksum, updated date, Codex install metadata, files, warnings.
  - Acceptance: two pilot skills can be represented without special cases.
  - Completed: schema files added and pilot metadata generated under `catalog/`.

- [x] **Decide canonical skill storage layout**
  - Decision: canonical catalog skills live under `skills/<skill-id>/SKILL.md`.
  - Acceptance: existing pilot skills have a clear migration path from legacy plugin paths.
  - Completed: pilot skills were ingested with `python -m skillforge upload ...`, not moved manually.

- [x] **Scaffold Python package**
  - Output: `skillforge/__main__.py`, `skillforge/cli.py`, `skillforge/catalog.py`, `skillforge/validate.py`, `skillforge/install.py`
  - Acceptance: `python -m skillforge --help` runs locally.
  - Completed: CLI exposes `validate`, `upload`, `download`, `search`, `search-audit`, `evaluate`, `peer-search`, `info`, `install`, `import-peer`, `remove`, `list`, `feedback`, `doctor`, `cache`, and `build-catalog`.

## Next

- [x] **Implement `validate`**
  - Checks: `SKILL.md` exists, valid YAML frontmatter, required `name` and `description`, folder/name mismatch warning, referenced files exist, suspicious file types warned.
  - Acceptance: validates both pilot skills and returns nonzero for malformed fixtures.
  - Completed: both pilot legacy skill folders validate.

- [x] **Implement catalog generation**
  - Command: `python -m skillforge build-catalog`
  - Outputs: `catalog/skills.json`, `catalog/skills/<skill-id>.json`
  - Acceptance: generated files are deterministic and stable across repeated runs.
  - Completed: generated aggregate and per-skill metadata for both pilot skills.

- [x] **Implement `search`**
  - Scope: local catalog first; exact ID, keyword, tag, and basic task text matching.
  - Acceptance: `get-youtube-media` is found for video/transcript/research queries.
  - Completed: smoke-tested task search for YouTube/research and retrospective/project memory.

- [x] **Implement `info`**
  - Output: human-readable summary and `--json`.
  - Acceptance: shows source path, checksum, description, tags, files, and install command.
  - Completed: `info` returns human-readable and JSON metadata.

- [x] **Implement Codex install**
  - Commands: `install <skill-id> --scope global`, `install <skill-id> --scope project --project <path>`, `remove <skill-id> --scope <scope> --yes`
  - Behavior: download/copy from catalog source, validate before install, avoid executing scripts, copy or symlink into Codex skill path, remove installed skills only after explicit confirmation.
  - Acceptance: install/remove works for both pilot skills in a test Codex home and test project folder.
  - Completed: global-scope install/remove is covered with an overridden test path; project-scope install/remove smoke-tested with an ignored demo project.

- [x] **Implement `list` and `doctor`**
  - `list`: show installed Codex skills.
  - `doctor`: report detected Codex paths and missing directories.
  - Acceptance: commands work on a clean machine and return useful JSON.
  - Completed: smoke-tested `list --scope project --project . --json` and `doctor --project . --json`.

- [x] **Implement feedback drafting**
  - Command: `python -m skillforge feedback <skill-id> --trying "..." --happened "..."`
  - Behavior: draft a GitHub issue title, issue-template URL, feedback-screen fields, Markdown body, and JSON payload.
  - Acceptance: users can ask Codex to turn a short problem statement into the same fields shown by the GitHub feedback issue form.
  - Completed: feedback command and tests added.

- [x] **Implement peer search/install cache**
  - Commands: `peer-search`, `install --peer <peer-id> --yes`, `import-peer`, `cache list`, `cache refresh`, `cache clear`.
  - Behavior: cache peer repos and search results under `.skillforge/cache`; install peer skills directly from cache without modifying local catalog files; import peer skills only when explicitly requested.
  - Acceptance: peer install uses source-attributed metadata and does not rewrite unrelated catalog files.
  - Completed: local fake-peer tests cover cached search, repeated cache use, peer install, and no catalog mutation.

- [x] **Implement discovery metadata support**
  - Output: schema and catalog support for optional fields: `title`, `short_description`, `expanded_description`, `aliases`, `categories`, `tasks`, `use_when`, `do_not_use_when`, `inputs`, `outputs`, `examples`, `related_skills`, `risk_level`, `permissions`, `page_title`, and `meta_description`.
  - Acceptance: `upload` preserves discovery metadata from `SKILL.md`; `build-catalog` emits it in per-skill JSON without breaking portable minimal skills.
  - Completed: parser, schemas, catalog generation, and current skills now support discovery metadata.

- [x] **Generate search index**
  - Output: `catalog/search-index.json`, `schemas/search-index.schema.json`.
  - Behavior: index descriptions, aliases, categories, tags, tasks, trigger guidance, inputs, outputs, and prompt examples; include source, checksum, owner, updated date, and install commands.
  - Acceptance: task queries can find skills through aliases and `use_when` phrases, not only the main description.
  - Completed: `catalog/search-index.json` is generated by `build-catalog` and local search uses it.

- [x] **Implement `search-audit` command**
  - Command: `python -m skillforge search-audit <skill-id> --json`.
  - Behavior: audit human clarity, agent triggerability, alias coverage, task coverage, examples, inputs/outputs, exclusion guidance, safety/permissions, source/provenance, and web metadata readiness.
  - Acceptance: returns actionable recommendations and exact files to create or update for all current SkillForge skills without modifying files.
  - Completed: all current skills return 100/100 with no recommendations after metadata enrichment.

- [x] **Implement deterministic `evaluate` command**
  - Command: `python -m skillforge evaluate <skill-id-or-path> --json`.
  - Behavior: wrap structural validation, search audit, catalog freshness, search-index freshness, and static-page freshness into one publication-readiness report.
  - Acceptance: a contributor can run one deterministic command before PR submission and get stable human-readable and JSON output.
  - Completed: CLI and Python API return structural validation, checksum freshness, generated-file readiness, search audit, and sample search evidence.

- [x] **Create LLM-driven skill discovery evaluation skill**
  - Candidate name: `skill-discovery-evaluation`.
  - Behavior: read a skill, run deterministic SkillForge commands, infer likely human and agent search prompts, improve discovery metadata and examples, rebuild generated files, and summarize the evaluation.
  - Acceptance: Codex can respond to "Evaluate this SkillForge skill for publication" by improving search/SEO readiness without inventing unsupported behavior.
  - Completed: `skills/skill-discovery-evaluation/SKILL.md` defines the LLM side of publication evaluation.

- [x] **Add publish-time evaluation workflow**
  - Flow: author/import skill, run structural validation, run LLM-driven discovery evaluation, rebuild catalog, run deterministic evaluation, submit PR.
  - Acceptance: README and contributing docs describe evaluation as the user-facing workflow while keeping validation as a technical sub-check.
  - Completed: requirements, SEO plan, README, skill list, and SkillForge CLI now describe and support the evaluation workflow.

- [x] **Add per-skill README home pages**
  - Output: `skills/<skill-id>/README.md` beside each canonical `SKILL.md`.
  - Behavior: README acts as the human-facing skill home page with repo/package links, purpose, call reasons, keywords, search terms, method, API/options, examples, help, LLM/CLI calls, feedback, author, citations, related skills, risk, limits, and discovery terms.
  - Acceptance: `build-catalog` records `homepage_path`, search indexes README text, and `evaluate` fails when the README is missing required home-page sections.
  - Completed: all current skills have README home pages using the template sections for parent collection, inputs/outputs, trust and safety, feedback, author, citations, and related skills.

- [x] **Add skill README template**
  - Output: `skillforge/templates/skill/README.md.tmpl`.
  - Behavior: provide the canonical human-facing skill home page skeleton for future skill generation.
  - Acceptance: template includes repo/package, parent collection, purpose, call reasons, keywords, search terms, method, API/options, inputs/outputs, examples, help, LLM/CLI calls, trust and safety, feedback, author, citations, and related skills.
  - Completed: template and `docs/templates.md` added.

- [x] **Add discovery warnings to `validate`**
  - Behavior: portable skills with only `name` and `description` still pass; SkillForge-owned skills warn when recommended discovery fields are missing.
  - Acceptance: warnings are clear, non-blocking, and included in JSON output.
  - Completed: warnings are scoped to repo-owned `skills/` entries.

- [x] **Generate static skill pages**
  - Output: one page per skill, category pages, JSON-LD metadata, and links from README/catalog pages.
  - Acceptance: each page includes use cases, exclusions, examples, install command, inputs/outputs, risk/permissions, source/provenance, related skills, and feedback link.
  - Completed: `build-catalog` generates `site/`, `site/search-index.json`, `site/llms.txt`, and `.well-known/agent-skills/index.json`.

- [x] **Implement template-backed skill creation**
  - Command: `python -m skillforge create <skill-id>`.
  - Behavior: generate `skills/<skill-id>/SKILL.md` and `skills/<skill-id>/README.md` from repository templates, accept common metadata flags, and leave obvious placeholders for unknown claims.
  - Acceptance: generated skills validate structurally, `evaluate` reports unresolved placeholders until they are filled, and `create` does not publish, install, or modify peer catalogs.
  - Completed: `skillforge/create.py`, `skillforge/templates/skill/SKILL.md.tmpl`, CLI wiring, and tests added.

- [x] **Implement static catalog search UI**
  - Output: generated `site/index.html`.
  - Behavior: static client-side search backed by `site/search-index.json`, with category, tag, risk, and source filters plus install commands and source links.
  - Acceptance: no backend or frontend build step is required beyond `python -m skillforge build-catalog`.
  - Completed: `render_site_index` now emits a usable static search interface with embedded fallback data.

- [x] **Expand peer catalog diagnostics and metadata**
  - Command: `python -m skillforge peer-diagnostics --json`.
  - Behavior: normalize richer peer catalog metadata, support static catalog search adapters, report cache freshness, duplicate IDs, adapter gaps, and trust notes.
  - Acceptance: peer results show source catalog metadata and cache state without weakening explicit peer install confirmation.
  - Completed: peer metadata normalization, static catalog search support, diagnostics, README updates, and tests added.

## Quality Gates

- [x] Add unit tests for validation, search ranking, metadata loading, and install path resolution.
- [ ] Add fixture skills: valid minimal, valid with references, malformed frontmatter, missing `SKILL.md`, suspicious script.
- [ ] Add CI workflow to run tests and catalog generation checks.
- [ ] Add formatting/linting for Python.
- [ ] Add a generated-files check so stale catalog output fails CI.

## Documentation

- [x] Keep `README.md` user-facing, workflow-oriented, and clear about what is implemented now versus planned.
- [ ] Keep `requirements.md` as the product contract.
- [ ] Keep `docs/skillforge-whitepaper.md` aligned with the requirements when user-affordance strategy changes.
- [ ] Add `docs/catalog-schema.md`.
- [ ] Add `docs/codex-install-paths.md`.
- [ ] Add `docs/contributing-skills.md`.
- [x] Add developer docs for the Python module architecture and command side effects.
- [x] Add a reusable Python module documentation template at `skillforge/templates/python/module.md.tmpl`.

## User Affordances

- [x] **Add a first-class help API**
  - Commands: `python -m skillforge help`, `python -m skillforge help <topic>`, and `python -m skillforge help --json`.
  - Behavior: map core workflows and common uncertain intents to safe next steps without executing actions.
  - Acceptance: a calling LLM can parse JSON help for command names, examples, side effects, and related commands.

- [x] **Add first-run guidance**
  - Command: `python -m skillforge getting-started`.
  - Behavior: show concise next steps after install or on demand: doctor, search, info, install, list, feedback, update-check.
  - Acceptance: output is useful in `normal` mode and suppressible in `silent` mode.

- [x] **Add upstream update checks**
  - Commands: `python -m skillforge update-check --json`.
  - Behavior: compare local checkout to upstream, cache last check for 24 hours, refuse unsafe updates with local changes.
  - Acceptance: offline or network-blocked environments return actionable errors and do not corrupt the checkout.
  - Completed: `update-check` is implemented. Actual `update --yes` remains deferred by product decision.

- [x] **Add what-changed summaries**
  - Command: `python -m skillforge whats-new`.
  - Behavior: use Git history between previous and current revision to summarize new skills, search changes, docs changes, peer changes, and breaking changes.
  - Acceptance: summary is factual and JSON output includes old/new commits and changed files.

- [x] **Add chattiness controls**
  - Commands/config: `--chattiness` and `SKILLFORGE_CHATTINESS`.
  - Modes: `coach`, `normal`, `terse`, `silent`.
  - Acceptance: `--json` remains stable regardless of chattiness, and risky operations still require confirmations.
  - Completed: `--chattiness` and `SKILLFORGE_CHATTINESS` are implemented for `help`, `getting-started`, `search`, and `corpus-search`. Persistent `config set` remains future work.

## Peer Catalogs

- [x] Define peer catalog adapter interface.
- [x] Implement GitHub-style `skills/<skill-id>/SKILL.md` peer repo adapter.
- [ ] Implement local/static `skills.json` adapter.
- [ ] Keep `skills.sh` disabled until source provenance and adapter behavior are verified.

## Backlog

- Trust/risk scoring.
- Human review workflow.
- NeMoClaw install target.
- Cursor install target.
- Discovery analytics for zero-result and low-confidence searches.
- `uvx` or `pipx` packaging.
- Enterprise allowlists and private catalogs.
- Trigger evals and task evals.
- Release notes or changelog authoring once Git-derived `whats-new` is not enough.
