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
- "I want to know what changed."
- "I want SkillForge to be quieter."

This framing is more useful than documenting only Python modules or command
syntax.

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
