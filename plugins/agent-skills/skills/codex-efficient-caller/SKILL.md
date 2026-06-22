---
name: codex-efficient-caller
owner: medatasci
description: >-
  Use when Codex needs to call tools, shell commands, connectors, bundled
  runtimes, local CLIs, browser/app automation, or local APIs efficiently in
  Codex Desktop or CLI environments. Helps avoid repeated failed calls from
  sandbox or network boundaries, missing runtimes, optional CLI assumptions,
  shell dialect and quoting mistakes, local app/COM availability, process
  lifecycle assumptions, native exit-code handling, and environment-specific
  failures. Use before nontrivial shell/tool execution, after a tool failure, or
  when updating prevention guidance from codex-failure-analyst reports.
title: Codex Efficient Caller
short_description: Choose efficient, environment-aware Codex tool and shell calls before expensive retries.
expanded_description: Helps Codex preflight local tools, shell commands, connectors, bundled runtimes, CLIs, browser or app automation, and local APIs in Codex Desktop or CLI environments. It focuses on sandbox boundaries, runtime resolution, connector-first choices, PowerShell command shape, process lifecycle checks, and evidence-preserving failure recovery.
aliases:
  - efficient caller
  - tool call preflight
  - Codex tool caller
  - shell command preflight
  - sandbox boundary handling
  - connector first workflow
categories:
  - Developer Tools
  - Agent Workflows
  - Safety And Review
tags:
  - codex
  - tool-calling
  - shell
  - sandbox
  - connectors
  - runtime
  - automation
tasks:
  - preflight Codex shell commands and tool calls
  - choose between connectors, Codex tools, local CLIs, and shell commands
  - resolve bundled runtimes before invoking scripts
  - identify sandbox, network, profile, local app, and permission boundaries
  - preserve command evidence for failure analysis
  - reduce repeated failed tool calls in Codex Desktop or CLI sessions
use_when:
  - Codex is about to run nontrivial shell commands, local CLIs, scripts, browser automation, app automation, or local APIs.
  - A previous tool or shell call failed and the next retry needs a changed hypothesis.
  - The task may cross sandbox, network, runtime, filesystem, connector, or process-lifecycle boundaries.
  - Codex needs compact prevention guidance before updating a narrower caller skill.
do_not_use_when:
  - The task is a simple direct answer that does not need tools or environment preflight.
  - The user asks for domain-specific analysis that does not involve Codex tool execution choices.
  - A specialized caller skill fully covers the command shape and no broader Codex boundary decision is needed.
inputs:
  - intended tool, shell command, connector call, local API call, or automation step
  - current shell, cwd, sandbox, writable roots, and available Codex tools
  - observed stdout, stderr, exit code, and command text after failures
outputs:
  - narrowest capable tool choice
  - environment-aware preflight checklist
  - corrected command or connector strategy
  - failure classification and next retry hypothesis
  - escalation or fallback recommendation when a real boundary is hit
examples:
  - Use codex-efficient-caller before running this local script so the command works in Codex Desktop.
  - A shell command failed with access denied; use codex-efficient-caller to decide whether this is syntax or a sandbox boundary.
  - Choose whether to use a GitHub connector, gh, or git for this PR workflow.
related_skills:
  - powershell-caller
  - codex-failure-analyst
  - powershell-failure-analyst
risk_level: low
permissions:
  - read task context, command outputs, environment details, and local path availability
  - run shell commands, Codex tools, connectors, local CLIs, or scripts only when the active task already calls for them
  - request narrow escalation for writes outside allowed roots, network access, installs, credentials, GUI automation, or destructive actions
page_title: Codex Efficient Caller Skill - Reliable Codex Tool And Shell Calls
meta_description: Use the Codex Efficient Caller skill to choose connector-first, runtime-aware, sandbox-aware Codex tool and shell calls before expensive retries.
---

# Codex Efficient Caller

## What This Skill Does

Choose small, environment-aware, recoverable Codex tool and shell calls. Use it
to decide whether a connector, Codex tool, bundled runtime, local CLI, browser
automation, app automation, local API, or shell command is the right next move.

It is especially useful before a failure-prone command, after a failed tool
call, or when a workflow may cross sandbox, runtime, filesystem, network,
profile, local app, or process-lifecycle boundaries.

## Safe Default Behavior

Prefer the narrowest capable tool and verify assumptions before acting. Keep
writes inside allowed workspace paths, use connectors when they fit, resolve
bundled runtimes instead of assuming `python` or `node`, and retry only after
classifying the failure and changing the hypothesis.

Do not use this skill to bypass user approvals, hide destructive actions, or
turn real permission, network, credential, or local-app boundaries into repeated
syntax retries.

Make the next tool call small, environment-aware, and recoverable.

## Environment Info

Know the active Codex boundary before choosing a command shape.

- `functions.shell_command` runs under the current `cwd`, shell, and sandbox policy.
- Writable locations are limited; writes outside the workspace usually need `sandbox_permissions:"require_escalated"`.
- Network, installs, GUI apps, local profiles, COM, and OS APIs are availability boundaries.
- `codex_app.load_workspace_dependencies` is a Codex tool that returns bundled runtime paths; it is not a filesystem path.

## Workflow

Use this loop for calls that are nontrivial, failure-prone, or expensive to retry.

1. Choose the narrowest capable tool: connector or Codex tool first, shell only when it adds value.
2. Preflight the environment: verify paths, optional CLIs, local apps, runtimes, permissions, and network assumptions.
3. Shape the command for the actual shell/runtime. On Windows PowerShell, use `$powershell-caller` for syntax and quoting details.
4. Execute one failure-sensitive operation per call; preserve stdout/stderr, exit code, working directory, and command text.
5. On failure, classify before retrying: syntax, missing dependency, missing path, sandbox/network boundary, local app/API boundary, process lifecycle, or tool-domain error.
6. Retry only with a changed hypothesis. If the failure is a real boundary, request narrow escalation or switch to an available connector/API.

## Default Patterns

Apply these guardrails unless the current repo or connector gives a safer local pattern.

- Resolve bundled Python through `codex_app.load_workspace_dependencies`; do not assume `python` resolves.
- Probe optional CLIs with `Get-Command`, `Test-Path`, `command -v`, or the platform equivalent before invoking them.
- Use absolute paths for cross-context files and literal path APIs where the shell supports them.
- Keep shell logic shallow; move complex parsing, JSON, or multiline logic into a script/runtime better suited to it.
- Check native command exit codes explicitly when chaining commands or wrapping tools.
- Verify background processes and PID files before waiting on, killing, or reading them.
- Prefer local workspace outputs for reports and generated artifacts; install or modify global state only with approval.

## Priority Guardrails

Current history shows runtime, path, sandbox, and PowerShell-shape mistakes consume the most repair turns.

- Resolve bundled runtimes before use; after profile or execution-policy noise, change shell/session settings instead of changing command logic.
- Verify target files, directories, cwd, and generated artifacts before acting; use absolute paths when crossing thread or sandbox context.
- Treat access denied, network, local app, COM, and OS API errors as boundaries; switch to a connector/workspace fallback or request narrow escalation.
- Use `$powershell-caller` for nontrivial Windows PowerShell commands: quoted executables, here-strings, object pipelines, JSON mutation, variables near punctuation, and native exit handling.
- Preserve exact command/output evidence for repeated unknown diagnostics, then run `$codex-failure-analyst` before adding new rules.

## Failure Analyst Feedback

Let observed failures decide which rules deserve always-loaded skill text.

Use `$codex-failure-analyst` when failures repeat or when updating this skill. Promote a prevention rule only when evidence shows stable root cause and reusable prevention.

Read `references/caller-patterns.md` when adding examples, reviewing priority targets, writing automation prompts, or deciding whether a rule belongs in this compact skill versus a specialized caller skill.
