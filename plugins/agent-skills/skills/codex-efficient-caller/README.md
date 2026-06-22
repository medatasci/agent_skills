# Codex Efficient Caller

## Repo And Package

Skill repo URL:
https://github.com/medatasci/agent_skills/tree/main/skills/codex-efficient-caller

Parent package:
Agent Skills Marketplace

Parent package repo URL:
https://github.com/medatasci/agent_skills

Distribution or marketplace:
SkillForge local catalog and Codex skill install workflow

## Parent Collection

Parent collection:
Agent Skills Marketplace

Collection URL:
https://github.com/medatasci/agent_skills

Categories:
Developer Tools, Agent Workflows, Safety And Review

## What This Skill Does

Codex Efficient Caller helps Codex choose small, environment-aware, recoverable
tool and shell calls. It covers connector-first choices, bundled runtime
resolution, shell command preflight, sandbox and network boundaries, local app
availability, process lifecycle checks, native exit-code handling, and failure
classification before retries.

## Why You Would Call It

Call this skill when:

- Codex is about to run nontrivial shell commands, scripts, local CLIs, browser
  automation, app automation, local APIs, or connector workflows.
- A tool call failed and the next retry needs a changed hypothesis.
- The workflow may cross sandbox, network, filesystem, runtime, local app,
  profile, or process-lifecycle boundaries.
- You want compact prevention guidance before updating a narrower caller skill.

## Keywords

Codex caller, tool call preflight, shell command preflight, connector first,
sandbox boundary, bundled runtime, local CLI, Codex Desktop, failure recovery,
environment-aware automation.

## Search Terms

efficient Codex tool calls, avoid repeated shell failures, choose connector or
CLI, Codex sandbox command preflight, resolve bundled Python, classify tool
failure, Codex Desktop command boundary, local app automation preflight.

## How It Works

The skill asks Codex to verify the environment before executing failure-prone
work. It recommends the narrowest capable tool, checks paths and runtimes,
probes optional CLIs, recognizes real boundaries, preserves stdout and stderr,
and retries only after classifying the failure.

## API And Options

This is an LLM-facing Codex skill. It has no standalone CLI command. It is often
paired with:

```text
$powershell-caller
$codex-failure-analyst
$powershell-failure-analyst
```

## Inputs And Outputs

Inputs:

- intended tool call, shell command, connector call, or local API step
- current shell, cwd, sandbox, writable roots, and available Codex tools
- observed stdout, stderr, exit code, and command text after failures

Outputs:

- narrowest capable tool choice
- environment-aware preflight checklist
- corrected command or connector strategy
- failure classification and retry hypothesis
- escalation or fallback recommendation when a real boundary is hit

## Limitations

- It does not grant permissions, credentials, network access, or filesystem
  access.
- It does not replace specialized domain skills or command-shaping skills.
- It should not be used to justify destructive actions without approval.

## Examples

```text
Use codex-efficient-caller before running this local script so the command works in Codex Desktop.
```

```text
A shell command failed with access denied; use codex-efficient-caller to decide whether this is syntax or a sandbox boundary.
```

```text
Choose whether to use a GitHub connector, gh, or git for this PR workflow.
```

## Help And Getting Started

Install the skill with SkillForge, then ask Codex to use
`codex-efficient-caller` before a nontrivial tool or shell workflow.

```text
python -m skillforge install codex-efficient-caller --scope global
```

## How To Call From An LLM

Use plain language:

```text
Use codex-efficient-caller to plan the next tool call and avoid repeated failed retries.
```

## How To Call From The CLI

This skill is called by Codex during a chat turn. Use SkillForge only to
install, inspect, evaluate, or update it:

```text
python -m skillforge info codex-efficient-caller --json
python -m skillforge evaluate codex-efficient-caller --json
```

## Trust And Safety

Risk level:
low

Permissions:

- read task context, command outputs, environment details, and path
  availability
- run tools, shell commands, connectors, local CLIs, or scripts only when the
  active task already calls for them
- request narrow escalation for writes outside allowed roots, network access,
  installs, credentials, GUI automation, or destructive actions

Data handling:
Do not expose secrets, private logs, or sensitive command output in public
reports or PRs.

Writes vs read-only:
The skill itself is guidance. The tool calls it shapes may read or write
depending on the user's active task and approvals.

## Feedback

Feedback URL:
https://github.com/medatasci/agent_skills/issues

## Contributing

Contributions should preserve the compact caller loop and move narrow shell
syntax examples into specialized caller skills when possible. Use pull requests
against the Agent Skills Marketplace.

## Author

Marc Edgar / medatasci

## Citations

Not applicable. This skill describes Codex workflow behavior.

## Related Skills

- `powershell-caller`: Windows PowerShell command-shaping details.
- `codex-failure-analyst`: evidence from local Codex failure history.
- `powershell-failure-analyst`: focused evidence from PowerShell failures.
