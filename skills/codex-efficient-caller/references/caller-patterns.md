# Caller Pattern Catalog

Use this reference when updating `codex-efficient-caller` or interpreting `codex-failure-analyst` priority targets.

## Automation Prompt Snippet

Use this near the top of recurring automation prompts:

```text
Automation caller preflight: before running shell commands, local CLIs, scripts, browser/app automation, or local APIs, use $codex-efficient-caller. On Windows PowerShell, use $powershell-caller for nontrivial commands. Prefer connectors or Codex tools when available; resolve bundled Python with codex_app.load_workspace_dependencies; keep writes in allowed workspace paths or request narrow approval; preserve command/output evidence for failures.
```

## Promotion Criteria

Promote a prevention pattern when it has:

- evidence volume across repeated calls or threads
- severity from blocked tasks, destructive risk, or high rework
- generality across task types and repositories
- confidence from stable root cause and prevention
- low enough token cost for always-loaded guidance
- high `rework_turns_to_resolve` or repeated failed repair turns

Keep narrow shell syntax examples in specialized skills such as `powershell-caller` unless every caller needs them.

## Pattern Families

## Current Evidence Snapshot

Latest refreshed two-month run: April 18, 2026 through June 18, 2026.

- Shell calls: 35,123
- Failed shell calls: 3,169
- Detected events: 1,977
- Shell-call efficiency: 90.98%
- Detected-event efficiency: 94.37%
- Lost-time estimate: 10.22%
- Efficiency percent: 89.78%

Top lost-time families:

- `codex-runtime-environment`: 6.75% lost time, 2,372 repair turns.
- `filesystem-state-assumption`: 1.26% lost time, 441 repair turns.
- `codex-boundary-management`: 0.81% lost time, 283 repair turns.
- `powershell-grammar-object-model`: 0.61% lost time, 214 repair turns.
- `unmapped-diagnostic-discovery`: 0.56% lost time, 195 repair turns.

Top priority targets by weighted evidence/severity/generality/confidence/token/rework:

- `codex-boundary-management`
- `codex-sandbox-001`
- `fs-path-001`
- `codex-python-001`
- `filesystem-state-assumption`
- `powershell-grammar-object-model`

Carry forward: keep runtime resolution, path verification, boundary recognition, and PowerShell command shaping in always-loaded guidance.

### Connector First

Problem: an optional CLI or local profile is assumed when a Codex connector/tool exists.

Pattern: use the connector for GitHub, calendar, email, chat, browser, documents, or runtime discovery when available; probe CLIs before use.

### Runtime Resolution

Problem: a command assumes a runtime such as Python or Node is on `PATH`.

Pattern: resolve bundled dependencies with Codex tools or explicit probes, then invoke the resolved executable path literally.

### Sandbox And Network Boundary

Problem: retries change syntax even though the failure is a permission, filesystem, network, install, or GUI boundary.

Pattern: keep work inside writable roots; after a real sandbox/network failure, rerun only necessary commands with narrow escalation.

### Shell Dialect And Quoting

Problem: syntax from one shell is used in another, or a command contains too many quoting layers.

Pattern: translate to the active shell; for complex logic, use a temporary script or a better runtime. Use `powershell-caller` on Windows PowerShell.

### Filesystem State

Problem: the call assumes paths, files, drives, or generated artifacts exist.

Pattern: verify with a native path API before reading/writing; use absolute paths when crossing thread, cwd, or sandbox context.

### Process Lifecycle

Problem: a background server, PID file, port, or native wrapper state is stale.

Pattern: check process existence, port/listener state, logs, and native exit codes before retrying or killing processes.

### Data Driven Skill Updates

Use `codex-failure-analyst` reports to decide where guidance belongs:

- `error_class` / `rule_id`: narrow stable root cause and prevention.
- `error_family` / `solution_pattern_id`: broader rollup for reusable patterns.
- `priority_targets`: combines evidence, severity, generality, confidence, token cost, and rework.
- `unmapped_repeated_failures`: review examples before adding a new rule.
