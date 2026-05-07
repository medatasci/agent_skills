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

## Healthcare And Medical Imaging Signals

For healthcare repositories, the deterministic scanner also returns
`healthcare_signal_summary`, `healthcare_reading_plan`, and
`healthcare_signals`. These are evidence candidates that help agents notice
medical-imaging source clues early, including:

- NIfTI, DICOM, NRRD, MHA/MHD, and conversion tool mentions.
- MONAI bundles, VISTA3D, MAISI, and healthcare model family names.
- CUDA, GPU, Docker, Conda, WSL, PyTorch, NVIDIA, and runtime clues.
- Segmentation, masks, label maps, inference, synthesis, generation,
  registration, and classification task clues.
- Model cards, dataset cards, Hugging Face, arXiv, citations, and benchmark
  clues.
- Medical-use safety language such as research use, diagnosis, treatment,
  triage, patient data, PHI, HIPAA, and intended-use terms.

`healthcare_signal_summary` groups the raw signals by signal type, count, terms,
and files to review. Use it first to decide which source files deserve attention.
The raw `healthcare_signals` list remains available for traceability.

`healthcare_reading_plan` converts the summary into a prioritized checklist of
review areas, healthcare signal files, bounded evidence hints, related
source-context artifacts, review questions, and claim boundaries. Evidence hints
are navigation aids only. Use the plan before drafting candidate skills, adapter
plans, smoke tests, or medical safety text.

`command_evidence` extracts source-grounded command candidates from documented
quick-start snippets, notebook code cells, and common Python CLI framework
clues. Use the command, source path, line or notebook cell, nearest source
heading, snippet, platform assumption, and side-effect risk to decide what to
read next. Do not treat extracted commands as approved execution steps.
`command_evidence_summary` groups likely side effects so reviewers can separate
read-only inspection from installs, downloads, network access, file writes,
GPU/model execution, container runtime, environment changes, shell scripts, and
unknown commands that need review.
`execution_gate` converts those signals into conservative review guidance:
safe to inspect, needs user approval, needs runtime planning, needs data-safety
review, or do not run from scanner output. It is a gate for review, not an
execution permission.
`adapter_policy` converts the execution gate into wrapper-design guidance:
read-only check, setup plan, runtime plan, guarded run, or no adapter until
source review. It helps the agent choose the next design artifact; it does not
approve source-command execution.

`candidate_skill_hypotheses` may appear when task/output signals are detected.
They are provisional prompts for review and must not be treated as publishable
skill recommendations until source evidence, runtime, safety, license,
examples, and smoke-test paths are confirmed. Hypothesis source coverage reports
which artifact types were detected; it is a triage signal, not validation.
Hypothesis `provisional_cli_draft` points at detected entrypoints, config files,
runtime files, source command evidence, and possible review commands for adapter
design. It may include an `adapter_policy_summary` so reviewers can see whether
the candidate is likely read-only, setup-only, runtime-planning, guarded-run, or
blocked pending review. It may also include `adapter_plan_stubs` with suggested
adapter commands, required inputs, expected outputs, guardrails, required
reviews, source references, and smoke-test ideas. For notebooks, command
relevance may use the most recent markdown heading before a code cell as
source-section context. Treat those commands as prompts for source review, not
validated execution instructions.

These signals do not prove capability, safety, license status, or runtime
readiness. They tell the agent which files to read before making those claims.
