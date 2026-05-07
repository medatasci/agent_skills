# SkillForge White Paper Draft

## Working Title

SkillForge: A GitHub-Backed Skill Sharing Layer For Humans And Agents

## Thesis

Reusable agent skills should be treated as durable software assets, not as
ephemeral prompts. SkillForge proposes a lightweight, GitHub-backed marketplace
where humans can browse, evaluate, and improve skills while agents can read
structured metadata, install skills safely, and preserve repeatable workflows.

## Why User Affordances Matter

Skill sharing only works when users can recover from uncertainty. A catalog can
contain useful skills and still fail if the user does not know what to search
for, how to inspect results, whether an update is available, or how much
explanation the tool will emit.

SkillForge should therefore make help, onboarding, update awareness, and output
style part of the product. These are not cosmetic features. They are the
interfaces that let a human or calling LLM move from "I am confused" to "I know
the next safe action."

## Proposed Affordance Model

SkillForge should expose six user affordances:

1. Documentation for humans and agents.
2. A help system for uncertain users and calling LLMs.
3. First-run guidance after installation.
4. Periodic upstream update checks.
5. A "what changed" summary after update.
6. Configurable chattiness from coaching to silent.

The first contact should be a hardcoded welcome message. This is intentional:
the welcome path should not depend on whether the calling LLM happens to infer
the right framing for a novice user.

SkillForge also needs a consistent voice, and the normal Codex-skill-compliant
place to define that behavior is `skills/skillforge/SKILL.md`. The desired
personality is helpful, practical, novice-friendly, safety-aware, transparent
about side effects, next-step aware, adjustable in chattiness, and deterministic
enough for agents. "Novice-friendly" should mean low-assumption and
recoverable, not always verbose. The product should anticipate one or two
likely next actions by default, while letting experienced users choose terse or
silent output.

## Documentation As A Product Surface

SkillForge documentation should serve two audiences at once:

- Humans need workflow-oriented docs that explain what to do next.
- Agents need stable machine-readable surfaces with examples, side effects,
  command names, JSON fields, and trust boundaries.

The public README should remain the front door. Deeper docs should live under
`docs/`, generated skill metadata should live under `catalog/`, and agent-facing
summaries should be exposed through `site/llms.txt`, JSON indexes, and CLI
`--json` output.

The important design choice is to document actions by user intent:

- "I need to find a skill."
- "I found a skill and want to inspect it."
- "I want to install it safely."
- "I am confused and need help."
- "I found a bug or want to request a feature."
- "I have a fix, feature, or skill to contribute."
- "I want to know what changed."
- "I want SkillForge to be quieter."

This framing is more useful than documenting only Python modules or command
syntax.

## Skill Packages As Product Artifacts

SkillForge skills should be understandable to humans and callable by agents at
the same time. That requires two coordinated files, not a prompt fragment.

`SKILL.md` is the agent-facing contract. It should stay portable as a normal
Codex skill, but it should also be readable enough for a human reviewer to
audit. The top of the file should explain what the skill does, the safe default
behavior, and the workflow or method an agent should follow.

`README.md` is the human-facing skill home page. It should explain why someone
would call the skill, what inputs and outputs it expects, how to use it from a
prompt or CLI, what it can and cannot do, and what trust or safety boundaries
apply.

SkillForge templates make this reviewable:

```text
skillforge/templates/skill/SKILL.md.tmpl
skillforge/templates/skill/README.md.tmpl
```

The publication flow should evaluate both files for template conformance,
unresolved placeholders, generated catalog freshness, search discoverability,
and source-supported claims. A pull request that adds or changes a skill should
include template checklist items so reviewers can see whether the agent
contract, human home page, generated catalog, and evaluation evidence are all
present.

For clinical-statistical skills, templates should preserve domain context that
future readers and agents would otherwise lose. Disease chapters should make
differential diagnosis and mimics easy to find with a quick guide, imaging
discriminators, a matrix, report-language cues, and prompts for additional
clinical or imaging context. They should also make covariates and confounders
easy to find by separating clinical, imaging, treatment/temporal,
acquisition/protocol, and research-design variables. A structured Treatment,
Response, And Outcome Context section should be used when management
guidelines, treatment pathways, response criteria, progression criteria,
posttreatment imaging effects, expected outcomes, or treatment-related
confounding affect interpretation or study design. The goal is not patient
treatment advice; it is to make differential diagnosis, guideline context,
response/progression definitions, outcome measures, confounders, and
statistical consequences visible during research planning and publication
review.

Domain-specific templates should travel with the published skill, not only with
the SkillForge implementation. For example, `clinical-statistical-expert`
packages its disease templates under `references/templates/` and includes a
template index that maps each template to its output artifact. A deterministic
checker such as `python -m skillforge disease-template-check <disease> --json`
then gives both humans and agents a repeatable way to confirm that disease
chapters still follow the intended structure before publication.

## Repo-Derived Skills

Many useful skills will come from existing repositories, model cards, datasets,
papers, and examples. Turning a codebase into agentic skills should begin with
a source-context map, not a wrapper.

For repo-derived skills, SkillForge should capture a readiness card before
publication. The card should record what each source artifact contributes:
README and quick-start behavior, scripts and APIs, configs and label maps,
examples and tests, dependency files, model or dataset cards, papers, licenses,
and known limitations.

This source-context map should inform candidate skill selection, LLM prompting,
deterministic adapter design, safety language, citations, smoke tests, and the
final publication checklist. If sources are not pinned to commits or revisions,
the skill should say that plainly and explain the reproducibility risk.

Executable repo-derived skills need a separate runtime acceptance story. It is
not enough for an agent to generate plausible commands. SkillForge should
distinguish preflight checks, such as source checkout, CUDA visibility, adapter
planning, generated config writing, and guarded refusal behavior, from runtime
acceptance, such as dependency installation, model download, GPU inference,
output verification, and cleanup. Acceptance should be per workflow rather than
blanket approval for the whole source repo. For example, a small CT paired
generation run may be accepted locally while MR brain, image-only generation,
evaluation, and training remain unaccepted. If a workstation lacks package
managers, admin permissions, model terms, or enough GPU memory, the skill
should record a clear skip reason rather than imply the model has run.

Repo-derived codebases may produce one skill or several. The default should be
one umbrella skill while the source, runtime, safety model, and user intent are
shared. Split into smaller skills only when a candidate has a distinct user
workflow, deterministic adapter surface, smoke-test evidence, and enough
search demand to justify another installable catalog item.

## Strategic Improvement Loop

SkillForge should also be able to improve itself through a recurring,
reviewable Codex automation loop. The point is not to create a background
auto-merge bot. The point is to preserve strategic momentum: a scheduled agent
can choose or continue one focus, research, plan, harden, review safety,
brainstorm, or implement a small improvement, then leave a durable log for a
human to review.

The first domain focus should be healthcare. SkillForge has already created
repo-derived skills around NVIDIA-Medtech work and is developing
`codebase-to-agentic-skills` as the general method for turning repositories
into agentic skills. A recurring loop can keep learning from NVIDIA-Medtech and
MONAI sources, improve the generator workflow, strengthen safety and evidence
gates, and identify new candidate skills.

For medical AI repositories, the generator should not leave the agent with a
flat pile of clues. It should produce raw healthcare signals, grouped signal
summaries, and a healthcare reading plan that names source files, review
questions, bounded evidence hints, related source-context artifacts, and claim
boundaries. That keeps the LLM useful while preserving the core discipline:
read the source before claiming modality support, runtime readiness, license
status, medical safety, or clinical use.

The scanner can also seed provisional candidate skill hypotheses when it sees
task or output signals. Those hypotheses should help reviewers start the
candidate table, but they are not product decisions. Source coverage can show
whether core artifact types were detected, but coverage is not confidence or
validation. A provisional CLI draft can point reviewers toward likely
entrypoints and adapter commands. The draft should be grounded in command
evidence that records source path, line, snippet, platform assumptions, and
side-effect risk. A summary should group likely read-only inspection, installs,
downloads, network access, file writes, GPU/model execution, container use,
environment changes, shell scripts, and unknown commands needing review. An
execution gate can then convert those signals into conservative guidance such
as safe to inspect, needs user approval, needs runtime planning, needs
data-safety review, or do not run from scanner output. Even then, it is still a
prompt for source review, not proof that a command is supported, safe,
cross-platform, or ready to run. Adapter policies can map those gates to
wrapper-design paths such as read-only checks, setup plans, runtime plans,
guarded run adapters, or no adapter until review. Adapter-plan stubs can then
turn the policy into a concrete implementation and smoke-test outline while
remaining explicit that the adapter has not been built yet. A deterministic
scaffolder can create the first review-only Python adapter skeleton with
`schema`, `check`, and `setup-plan`, while deliberately omitting any runnable
`run` command. When a scanner output already exists, the scaffolder should be
able to read `scan.json`, select a particular candidate and adapter-plan stub,
and carry the source references, guardrails, required reviews, and planned
commands into the generated skeleton. A skill only becomes publishable after
source evidence, runtime feasibility, safety boundaries, license constraints,
examples, and smoke tests are reviewed.

Because the loop may run frequently, it needs operational humility. A run every
20 minutes may overlap with a previous run. SkillForge should therefore use
unique run logs and an advisory active-run lock so concurrent jobs avoid
editing the same files blindly. If another run is active, the safe behavior is
to perform read-only research, use a separate worktree, or stop cleanly.

Each run should record:

- selected focus and strategic lane
- sources reviewed
- commands run
- files changed
- tests and checks
- what went well
- what could be improved
- the one next action

This loop makes agent work more auditable. It also gives SkillForge a practical
way to combine research, planning, implementation, hardening, safety review,
and new skill development without losing context between sessions.

## Contribution Model

SkillForge should treat feedback and contributions as related but distinct
product paths.

Feedback is for a user who found a bug, got confused, wants a feature, or
noticed a missing workflow but does not have a change ready. The product should
draft a GitHub issue from plain language.

Contributions are for users or agents who have a concrete fix, feature,
documentation update, catalog update, or new skill package ready for review.
The product should steer those changes through pull requests. Direct pushes to
`main` are a maintainer workflow, not the default user workflow.

SkillForge should also distinguish contributor comfort. A developer may want
clear Git commands. A non-developer may need Codex to handle branch, commit,
push, and PR mechanics step by step. This should be treated as a user-experience
signal, not as a permission model or trust claim. The safest default when the
profile is unknown is to ask one short question about whether the user wants
Codex to handle the PR mechanics.

The CLI support should be conservative:

```text
python -m skillforge feedback <subject> --trying "..." --happened "..."
python -m skillforge contribute "<summary>" --type feature --user-type non-developer --json
```

`feedback` drafts an issue. `contribute` drafts a pull request package with a
title, branch name, body, suggested commands, checks, safety notes, and review
checklist. Neither command should perform authenticated GitHub writes in the
MVP.

## Help System

A SkillForge help system should be both promptable and deterministic.

Promptable examples:

```text
Welcome me to SkillForge.
```

```text
SkillForge, help me figure out what to do next.
```

```text
Find a low-risk skill for writing status emails and explain the options before installing anything.
```

CLI examples:

```text
python -m skillforge welcome
python -m skillforge welcome --json
python -m skillforge help
python -m skillforge help search
python -m skillforge help "I need a skill for writing status emails"
python -m skillforge help --json
```

The human output should be concise and practical. The JSON output should expose
commands, example prompts, risk or side-effect notes, related commands, and next
steps so another agent can reason over the help API.

Hardcoded welcome/help content should live in source control and be covered by
tests. That makes first-run behavior reviewable instead of leaving it as an
untracked prompt convention.

## First-Run Guidance

After installation, SkillForge should avoid leaving the user with a blank slate.
The first-run guidance should suggest:

- Run a health check.
- Search for a skill by task.
- Inspect a skill before installing it.
- List installed skills.
- Send feedback if the result is bad.
- Ask SkillForge for help.
- Check for updates later.

This guidance should be short by default and available on demand through a
command such as:

```text
python -m skillforge getting-started
```

Installation itself should be idempotent. When a user or calling LLM says
"install SkillForge," the system should first verify whether SkillForge is
already installed and usable. A healthy existing install should produce a status
report, not a failed clone. Repair should be narrow: add missing non-conflicting
Codex config entries only after confirmation, and stop on non-SkillForge folders
or conflicting config.

```text
python -m skillforge install-skillforge --json
python -m skillforge install-skillforge --yes
```

## Update Awareness

A skill marketplace becomes stale if users do not know when the marketplace
itself has improved. SkillForge should periodically compare the local checkout
to the configured upstream repo and report whether updates are available.
The practical MVP cadence is a cached check every few hours, with a 6-hour
default window so a human or calling LLM can ask often without creating a
network fetch on every command.

The update model should be conservative:

- No background daemon in MVP.
- No automatic file changes without explicit approval.
- No surprise network call on every command.
- No overwrite of local changes.
- Clear behavior when offline or blocked by corporate network policy.

Possible commands:

```text
python -m skillforge update-check --json
python -m skillforge update
python -m skillforge update --yes
python -m skillforge whats-new
```

`python -m skillforge update` should behave like a safe status flow unless
`--yes` is supplied. `python -m skillforge update --yes` should only perform a
clean fast-forward update and should refuse dirty or diverged checkouts.
Background auto-update and policy-controlled update channels remain later
enterprise concerns.

## What Changed

After an update, SkillForge should highlight changes in terms users care about:

- New skills.
- Better search or peer catalog behavior.
- Safer install or update behavior.
- Documentation improvements.
- Breaking changes or changed defaults.
- New commands or deprecations.

The first implementation can use Git history:

```text
git log <old-commit>..<new-commit>
git diff --name-only <old-commit>..<new-commit>
```

Later versions can add release notes or human-authored changelog entries. Git
history should remain the factual fallback.

## Chattiness Control

SkillForge should support multiple output styles because humans and agents have
different needs.

Recommended modes:

- `coach`: extra context, teaching, and next-step suggestions.
- `normal`: concise output with practical next steps.
- `terse`: minimal human output.
- `silent`: no extra prose beyond requested output, warnings, errors, and JSON.

Possible configuration:

```text
python -m skillforge search "SQL database access" --chattiness terse
python -m skillforge search "write an email" --chattiness silent --json
```

Persistent configuration can come later through a command such as
`python -m skillforge config set chattiness coach`.

Safety rule: dangerous or ambiguous actions should still warn or require
confirmation, even in silent mode.

## Design Options

Small MVP option:

- Add README guidance.
- Add `help` and `getting-started` commands.
- Add cached `update-check`.
- Add `--quiet` and `--verbose` only.

Balanced option:

- Add `help`, `getting-started`, `update-check`, `update`, `whats-new`, and
  `config`.
- Add four chattiness modes.
- Store update-check state and last-seen commit in the SkillForge user cache.
- Keep JSON output stable for agents.

Enterprise-ready option:

- Add policy-controlled update channels.
- Add internal/private catalog update checks.
- Add signed release metadata.
- Add audit logs for update and install actions.
- Add organization defaults for chattiness and peer catalogs.

## Recommended Path

Use the balanced option as the product target, implemented incrementally.

First, document the user affordances and add the help/onboarding commands.
Second, add conservative update checks, explicit fast-forward update, and
`whats-new`. Third, add persistent configuration and chattiness modes.
Enterprise controls can remain a later layer because the public-safe GitHub
implementation should stay small and inspectable.

Backlog: add an LLM capability evaluation that checks whether a calling LLM can
welcome a novice user, choose the right SkillForge command, keep local and peer
install boundaries clear, avoid unsupported commands, and ask before risky
installs.
