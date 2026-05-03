# SkillForge Templates

SkillForge templates live with the Python package so future CLI creation
commands can reuse them directly.

Current templates:

- `skillforge/templates/skill/README.md.tmpl`
- `skillforge/templates/skill/SKILL.md.tmpl`
- `skillforge/templates/python/module.md.tmpl`

The skill README template is the human-facing home page template. It includes
repo/package links, parent collection, purpose, call reasons, keywords, search
terms, method, API/options, inputs and outputs, examples, help, LLM and CLI
calls, trust and safety, feedback, author, citations, and related skills.

The template is intentionally verbose. It is meant to guide skill generation,
review, and publication. A generated skill README should replace every
placeholder, keep the useful context, and remove template-only guidance that
would distract a normal reader.

Keep `README.md` human-facing. Keep `SKILL.md` agent-facing.

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
