# Source Context Map

The source-context map is the evidence layer for repo-to-skills work. It is not
just a list of files. It explains how each source artifact should influence the
future skill.

## Source Areas

| Source area | What it provides | How to use it |
| --- | --- | --- |
| README and quick starts | Intended use, setup path, example commands, supported workflows, advertised limits, and public language. | Ground skill purpose, examples, and first adapter candidates. |
| Docs and tutorials | Workflow variants, parameter meanings, edge cases, troubleshooting, and domain vocabulary. | Decide whether workflows should be separate skills or reference sections. |
| Scripts, APIs, notebooks, bundles | Executable entrypoints, arguments, side effects, and returned artifacts. | Define deterministic adapter commands and provenance. |
| Configs, metadata, schemas, label maps | Modes, labels, defaults, model paths, supported modalities, and validation rules. | Keep inputs, outputs, and LLM explanations exact. |
| Examples, tests, sample data | Realistic input/output contracts and smoke-test fixtures. | Build smoke tests and realistic user prompts. |
| Dependencies, Docker, Conda, CI | Runtime, OS, GPU, CUDA, Docker, package, and install requirements. | Define `check`, `setup-plan`, skip reasons, and deployment notes. |
| Model cards, dataset cards, papers | Intended use, method context, citations, limitations, terms, and safe claims. | Ground public README, safety notes, and citations. |
| Licenses, releases, issues, security notes | Permitted use, restricted use, version pinning, known bugs, and maintenance status. | Set publication risk, open questions, and contribution guidance. |

## Output Shape

For every important artifact, capture:

- Source path or URL.
- What it provides.
- Skill design impact.
- Adapter or deterministic-code impact.
- LLM context impact.
- Safety, license, or publication impact.
- Open questions.

The deterministic scanner can generate a first draft, but the agent still must
read the relevant artifacts before making claims.
