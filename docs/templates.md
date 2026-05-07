# SkillForge Templates

SkillForge templates live with the Python package so future CLI creation
commands can reuse them directly.

Current templates:

- `skillforge/templates/skill/README.md.tmpl`
- `skillforge/templates/skill/SKILL.md.tmpl`
- `skillforge/templates/python/module.md.tmpl`

Archived design options:

- `docs/templates/skill-readme-structure-options.md`

Clinical-statistical expert draft template:

- `skillforge/templates/clinical-statistical-expert/disease.md.tmpl`
- `skillforge/templates/clinical-statistical-expert/disease-research-plan.md.tmpl`
- `skillforge/templates/clinical-statistical-expert/disease-review-criteria.md.tmpl`
- `skillforge/templates/clinical-statistical-expert/disease-figure-evidence.md.tmpl`
- `skillforge/templates/clinical-statistical-expert/disease.figures.schema.json`
- `skillforge/templates/clinical-statistical-expert/disease.sources.schema.json`

The packaged `clinical-statistical-expert` skill also carries a copy under:

```text
skills/clinical-statistical-expert/references/templates/
```

That folder includes `README.md`, which maps each template or schema to the
disease artifact it creates.

Clinical-statistical disease chapters also use deterministic helper commands:

- `python -m skillforge source-archive <disease> ...`
- `python -m skillforge figure-evidence <disease> ...`
- `python -m skillforge disease-preview <disease> --json`
- `python -m skillforge disease-template-check <disease> --json`

The skill `SKILL.md` template is the human-readable agent contract template. It
keeps portable Codex frontmatter first, then puts a readable H1, `## What This
Skill Does`, and `## Safe Default Behavior` near the top. That top section is
deliberately readable by humans, but its purpose is still agent execution: when
to use the skill, what the safe default is, what side effects need approval,
and which workflow path to choose.

The skill README template is the human-facing home page template. It includes
repo/package links, parent collection, purpose, call reasons, keywords, search
terms, method, API/options, inputs and outputs, examples, help, LLM and CLI
calls, trust and safety, feedback, author, citations, and related skills.

The template is intentionally verbose. It is meant to guide skill generation,
review, and publication. A generated skill README should replace every
placeholder, keep the useful context, and remove template-only guidance that
would distract a normal reader.

`python -m skillforge evaluate <skill-id> --json` checks template conformance
for both files. The check reports missing required sections and suggested fixes
for the agent-facing `SKILL.md` and the human-facing skill `README.md`.

Keep `README.md` public and user-facing. Keep `SKILL.md` agent-facing, concise,
and auditable. If a `SKILL.md` needs long background, move that background into
`references/`; if it needs deterministic behavior, put the code in `scripts/`.

The Python module documentation template is for docs under `docs/python/`. Use
it when adding or rewriting documentation for a Python source module such as
`skillforge/peer.py` or `skillforge/update.py`. It should explain ownership,
when to edit the module, commands and workflows, inputs, outputs, side effects,
public functions, cross-platform notes, tests, and agent editing guidance.

Do not create one README beside every `.py` file. Prefer:

- `skillforge/README.md` for the package overview.
- `skillforge/modules.toml` for machine-readable module ownership.
- `docs/python/<module>.md` for human and agent-facing module docs.
- `skillforge/templates/python/module.md.tmpl` as the starting point for new
  module docs.
