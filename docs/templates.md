# SkillForge Templates

SkillForge templates live with the Python package so future CLI creation
commands can reuse them directly.

Current templates:

- `skillforge/templates/skill/README.md.tmpl`

The skill README template is the human-facing home page template. It includes
repo/package links, parent collection, purpose, call reasons, keywords, search
terms, method, API/options, inputs and outputs, examples, help, LLM and CLI
calls, trust and safety, feedback, author, citations, and related skills.

The template is intentionally verbose. It is meant to guide skill generation,
review, and publication. A generated skill README should replace every
placeholder, keep the useful context, and remove template-only guidance that
would distract a normal reader.

Keep `README.md` human-facing. Keep `SKILL.md` agent-facing.
