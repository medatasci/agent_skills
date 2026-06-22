# Solution Pattern Catalog

Keep `SKILL.md` short. Put durable teaching here and executable classification in `scripts/`.

## Skill-Length Balance

Do not use a fixed pattern count. Promote as many prevention patterns as the evidence supports, but choose the storage tier deliberately:

- Put always-use guardrails in `SKILL.md`.
- Put fragile one-shot examples in a directly linked reference.
- Put deterministic classification, scoring, and report generation in scripts.
- Remove or demote patterns when new runs show they are rare, stale, or too situation-specific.

Use this scoring model when updating a prevention skill:

- Evidence: repeated count, recurrence across threads, and recent frequency.
- Severity: wasted time, repeated failed retries, destructive risk, or blocked task completion.
- Generality: applies across many user tasks, not one project.
- Confidence: root cause and prevention are stable from event evidence.
- Token cost: compact enough for `SKILL.md`; otherwise use a reference.
- Rework turns to resolve: estimated subsequent shell outputs before the next successful shell output in the same thread.

Store run data in SQLite when comparing or prioritizing:

- `events`: one row per detected diagnostic, labeled by `error_family`, `error_class`, severity, confidence, rework, and repair mode.
- `rule_summary`: grouped root-cause rules with priority score components.
- `pattern_summary`: grouped solution patterns with priority score components.
- `priority_targets`: top rule and pattern targets sorted by weighted priority.
- `v_event_classes`, `v_rule_priority`, `v_pattern_priority`, `v_repair_modes`: query-ready views.

## Category Labeling Process

Use layered labels so rollups stay stable:

1. Extract evidence signatures from output: exit code, `FullyQualifiedErrorId`, parser text, command text, path/profile/network indicators, and excerpt.
2. Assign a narrow `error_class` (`rule_id`) only when the signature has a stable root cause and prevention.
3. Assign a broader `error_family` (`solution_pattern_id`) that groups related classes into a reusable solution pattern.
4. Keep ambiguous or one-off events in `ps-unmapped-001`.
5. Promote repeated unmapped signatures only after reviewing examples and confirming the prevention behavior.
6. Preserve the raw event fields so labels can be audited and revised.

Good rollup labels should be:

- mutually distinguishable
- stable across threads and dates
- tied to a prevention behavior
- broad enough for group-by queries
- narrow enough to avoid mixing unrelated fixes

## Multi-Turn Repair Detection

`rework_turns_to_resolve` is an estimate, not a perfect conversational truth. The analyzer looks at later shell outputs in the same thread and assigns a repair mode:

- `direct_next_shell_success_similar_command`: next shell call succeeded and looks related.
- `later_similar_command_success`: a later successful shell call is strongly similar to the failed command.
- `later_related_command_success`: a later success is somewhat similar.
- `later_generic_shell_success`: a later shell call succeeded, but command similarity is weak.
- `repeated_failure_then_*`: related failures repeated before success.
- `unresolved_no_later_shell_success`: no later successful shell output was observed.

Use `repair_confidence_label` with `rework_turns_to_resolve`; do not treat low-confidence generic success as a confirmed repair.

## Promotion Rule

Promote a failure into a solution pattern only when it has:

- repeated evidence or high severity
- a stable root cause
- a prevention behavior that solves a class of problems
- a compact example suitable for a caller skill

## Pattern Shape

Each pattern should include:

- problem class
- evidence signatures
- abstraction
- safe pattern
- anti-pattern
- when to use
- when not to use
- canonical example
- target skill to update

## Current Pattern Families

### Shell Dialect Mismatch

Abstraction: Bash or generic shell habits are being used in Windows PowerShell.

Carry forward: translate the shell syntax, or move logic into Python/a script.

### Shell Complexity Overflow

Abstraction: too much quoting, JSON, brace nesting, or multi-line logic is packed into one shell command.

Carry forward: use here-strings, temporary `.ps1` files, or Python scripts for structured logic.

### PowerShell Grammar And Object Model

Abstraction: statements, variables, cmdlets, or objects are treated like Bash text streams.

Carry forward: assign block output before piping, use `${name}` near punctuation, use `-LiteralPath`, invoke quoted executables with `&`, and mutate objects deliberately.

### Codex Runtime Environment

Abstraction: the command assumes a normal interactive shell instead of Codex Desktop's bundled runtime and shell profile behavior.

Carry forward: resolve bundled dependencies through Codex tools, suppress profile noise when needed, and provide fallbacks for Codex env vars.

### Codex Boundary Management

Abstraction: the command crosses a sandbox, network, permission, local app, profile, COM, or Windows API boundary.

Carry forward: probe first, keep writes inside the workspace, and request narrow escalation only when necessary.

### Filesystem State Assumption

Abstraction: paths, directories, or files are assumed to exist in the current cwd/sandbox.

Carry forward: use absolute paths for cross-context files, `Test-Path`, `Resolve-Path`, and `-LiteralPath`.

### Unmapped Diagnostic Discovery

Abstraction: repeated diagnostics are not yet explained by the rule catalog.

Carry forward: cluster by error type and excerpt, inspect examples, then promote only stable repeated signatures.

### Optional Local Tool Availability

Abstraction: local developer CLIs or hard-coded executable paths are assumed to exist.

Carry forward: probe with `Get-Command` or `Test-Path`, then use a connector/tool, approved install, or direct API fallback.

### Process And Native Command Lifecycle

Abstraction: a process, server, PID file, or native wrapper state is assumed to still be valid.

Carry forward: check process existence, preserve logs, and distinguish native command failure from PowerShell syntax failure.

## Periodic Self-Improvement Cycle

Run this periodically, preferably monthly or after a large burst of automation work:

1. Collect: run the analyzer over the last 30-60 days.
2. Baseline: record shell calls, failed shell calls, event count, top rules, and top solution patterns.
3. Promote: review `summary.unmapped_repeated_failures` and add rules only when prevention is stable.
4. Distill: update caller skills using the skill-length balance above.
5. Validate: rerun the same window and confirm reclassification moved events out of unmapped without changing total evidence unexpectedly.
6. Compare: run against the prior period and check repeat-rule counts per 100 shell calls.
7. Install: copy updated skills only after hashes and smoke tests pass.
8. Record: save the report path and the top pattern changes.
