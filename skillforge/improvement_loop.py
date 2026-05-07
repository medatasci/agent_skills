from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import shutil
import subprocess
import uuid

from .catalog import REPO_ROOT, display_path


DEFAULT_LOG_DIR = Path("docs") / "improvement-loop"
DEFAULT_LOCK_PATH = Path(".skillforge") / "improvement-loop" / "active-run.json"
DEFAULT_STALE_MINUTES = 90


LANES = {
    "researcher": "Look outward for practices, repositories, papers, examples, and prior art that should improve SkillForge.",
    "planner": "Turn known gaps into requirements, plans, issue drafts, and reviewable next actions.",
    "builder": "Implement a small, reviewable SkillForge, skill, adapter, or documentation improvement.",
    "hardener": "Improve tests, failure handling, cross-platform behavior, and maintainability.",
    "safety": "Review risk, data handling, medical-use boundaries, permissions, licenses, and side effects.",
    "brainstormer": "Generate and triage new improvement ideas, especially healthcare skill opportunities.",
}


HEALTHCARE_SOURCES = [
    {
        "name": "NVIDIA-Medtech GitHub organization",
        "url": "https://github.com/NVIDIA-Medtech",
        "why": "Primary source for healthcare algorithm repositories that may become agentic skills.",
    },
    {
        "name": "NV-Segment-CTMR",
        "url": "https://github.com/NVIDIA-Medtech/NV-Segment-CTMR/tree/main/NV-Segment-CTMR",
        "why": "Current segmentation skill exemplar and source for medical image segmentation workflows.",
    },
    {
        "name": "NV-Generate-CTMR",
        "url": "https://github.com/NVIDIA-Medtech/NV-Generate-CTMR/tree/main",
        "why": "Current synthetic CT/MRI generation skill exemplar and source for generation workflow hardening.",
    },
    {
        "name": "MONAI",
        "url": "https://github.com/project-monai/monai",
        "why": "Healthcare AI framework source for future algorithm and workflow skills.",
    },
    {
        "name": "SkillForge codebase-to-agentic-skills docs",
        "path": "docs/codebase-to-agentic-skills.md",
        "why": "Local design contract for converting healthcare codebases into skills.",
    },
    {
        "name": "Codebase To Agentic Skills skill",
        "path": "skills/codebase-to-agentic-skills/SKILL.md",
        "why": "Agent-facing workflow being improved by this loop.",
    },
]


FOCUS_AREAS = [
    {
        "id": "healthcare-repo-to-skills",
        "title": "Improve healthcare codebase-to-agentic-skills workflows",
        "lane": "builder",
        "reason": "The user explicitly wants SkillForge to improve itself, especially codebase-to-agentic-skills, with a healthcare-domain focus.",
        "suggested_actions": [
            "Review docs/codebase-to-agentic-skills.md and skills/codebase-to-agentic-skills for gaps exposed by recent NVIDIA-Medtech work.",
            "Choose one small improvement that makes repo-to-skills conversion more reliable for NVIDIA-Medtech or MONAI repositories.",
            "If code changes are made, keep them on the improvement-loop branch or a reviewable worktree.",
            "Run focused tests plus build-catalog/evaluate for changed skills when applicable.",
        ],
        "expected_artifacts": [
            "Updated requirements, skill docs, helper code, or tests.",
            "Run log describing evidence, changes, checks, what went well, and what could improve.",
        ],
    },
    {
        "id": "medical-ai-source-research",
        "title": "Research healthcare agentic-skill opportunities",
        "lane": "researcher",
        "reason": "The loop should regularly look outward for repos, papers, examples, and standards that can improve SkillForge and new skills.",
        "suggested_actions": [
            "Inspect NVIDIA-Medtech and MONAI source material relevant to one candidate capability.",
            "Record source URLs, entry points, papers, examples, and licensing or runtime caveats.",
            "Summarize one or more candidate skills with sample prompts and possible CLI contracts.",
        ],
        "expected_artifacts": [
            "A source-backed note under docs/improvement-loop/initiatives/ or docs/reports/.",
            "Backlog updates for promising candidate skills.",
        ],
    },
    {
        "id": "medical-safety-hardening",
        "title": "Harden medical AI skill safety and evidence gates",
        "lane": "safety",
        "reason": "Healthcare skills need conservative data, license, privacy, clinical-use, and provenance boundaries.",
        "suggested_actions": [
            "Review one healthcare skill for unsupported clinical, trust, citation, or license claims.",
            "Improve evaluate checks or README/SKILL guidance if a repeatable gap appears.",
            "Keep safety changes explicit and source-backed.",
        ],
        "expected_artifacts": [
            "Safety notes, requirements updates, evaluation improvements, or PR checklist additions.",
        ],
    },
    {
        "id": "skillforge-user-affordances",
        "title": "Improve SkillForge user affordances and agent APIs",
        "lane": "planner",
        "reason": "SkillForge should help novice users and calling LLMs recover when they are unsure what to do next.",
        "suggested_actions": [
            "Review README, help topics, welcome text, CLI JSON, and chattiness behavior for one rough edge.",
            "Make one user-centered improvement that also remains deterministic for agents.",
            "Document the change in requirements or the white paper if it changes product behavior.",
        ],
        "expected_artifacts": [
            "Docs, CLI, tests, or help output updates.",
        ],
    },
    {
        "id": "search-and-seo-quality",
        "title": "Improve search and SEO for healthcare skills",
        "lane": "hardener",
        "reason": "SkillForge depends on humans and agents being able to find the right skill by task, not only by exact name.",
        "suggested_actions": [
            "Run search/corpus-search for realistic healthcare prompts and inspect weak or confusing results.",
            "Improve README/SKILL discovery fields, catalog metadata, or search ranking diagnostics.",
            "Run search-audit/evaluate for changed skills.",
        ],
        "expected_artifacts": [
            "Updated discovery text, tests, or search diagnostics.",
        ],
    },
    {
        "id": "new-healthcare-skill",
        "title": "Develop a new healthcare agentic skill when justified",
        "lane": "brainstormer",
        "reason": "New skills are allowed when they are the best way to improve SkillForge and related healthcare workflows.",
        "suggested_actions": [
            "Use codebase-to-agentic-skills before packaging any new repo-derived skill.",
            "Create a source-context map and Skill Design Card before writing skill files.",
            "Keep generated skills planning-first unless runtime dependencies, data, and smoke tests are available.",
        ],
        "expected_artifacts": [
            "Candidate table, Skill Design Card, draft skill package, or explicit skip reason.",
        ],
    },
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_utc(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        normalized = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def resolve_under_repo(repo_root: Path, path_value: str | Path | None, default: Path) -> Path:
    path = Path(path_value) if path_value else default
    if path.is_absolute():
        return path
    return repo_root / path


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_git(repo_root: Path, args: list[str]) -> dict:
    git = shutil.which("git")
    if not git:
        return {"ok": False, "stdout": "", "stderr": "git not found", "returncode": 127}
    command = [
        git,
        "-c",
        f"safe.directory={repo_root.as_posix()}",
        "-C",
        str(repo_root),
        *args,
    ]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            check=False,
            shell=False,
            text=True,
            timeout=20,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {"ok": False, "stdout": "", "stderr": str(exc), "returncode": 1}
    return {
        "ok": result.returncode == 0,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "returncode": result.returncode,
    }


def repo_snapshot(repo_root: Path) -> dict:
    branch = run_git(repo_root, ["branch", "--show-current"])
    commit = run_git(repo_root, ["rev-parse", "--short=12", "HEAD"])
    commit_date = run_git(repo_root, ["log", "-1", "--format=%cI"])
    status = run_git(repo_root, ["status", "--porcelain"])
    remote = run_git(repo_root, ["remote", "get-url", "origin"])

    status_lines = status["stdout"].splitlines() if status["ok"] and status["stdout"] else []

    def status_path(line: str) -> str:
        if len(line) >= 4 and line[2] == " ":
            return line[3:].strip()
        if len(line) >= 3:
            return line[2:].strip()
        return line.strip()

    return {
        "repo_root": str(repo_root),
        "platform": platform.system(),
        "branch": branch["stdout"] if branch["ok"] else None,
        "commit": commit["stdout"] if commit["ok"] else None,
        "commit_date": commit_date["stdout"] if commit_date["ok"] else None,
        "origin": remote["stdout"] if remote["ok"] else None,
        "git_ok": all(item["ok"] for item in [branch, commit, status]),
        "git_errors": [item["stderr"] for item in [branch, commit, status, remote] if not item["ok"] and item["stderr"]],
        "dirty": bool(status_lines),
        "changed_file_count": len(status_lines),
        "changed_files": [status_path(line) for line in status_lines[:50]],
    }


def load_state(log_dir: Path) -> dict:
    state = read_json(log_dir / "state.json")
    if not state:
        state = {
            "active_initiative": None,
            "last_completed_focus": None,
            "notes": "Initial state for recurring SkillForge strategic improvement cycles.",
        }
    return state


def read_backlog(log_dir: Path, *, limit: int = 20) -> list[str]:
    backlog = log_dir / "backlog.md"
    if not backlog.exists():
        return []
    items: list[str] = []
    try:
        lines = backlog.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- [ ] "):
            items.append(stripped[6:].strip())
        elif stripped.startswith("- "):
            items.append(stripped[2:].strip())
        if len(items) >= limit:
            break
    return items


def select_focus(state: dict, backlog_items: list[str], lane: str | None, focus_override: str | None) -> dict:
    if focus_override:
        return {
            "id": "custom-focus",
            "title": focus_override,
            "lane": lane or "planner",
            "reason": "The caller supplied an explicit focus override.",
            "suggested_actions": [
                "Define the smallest useful reviewable outcome for this focus.",
                "Collect source evidence before changing behavior.",
                "Log commands, files changed, checks, and remaining gaps.",
            ],
            "expected_artifacts": ["Run log and reviewable notes or code changes."],
            "backlog_items": backlog_items[:5],
        }

    active = state.get("active_initiative")
    if isinstance(active, dict) and active.get("status") not in {"done", "blocked", "paused"}:
        selected = dict(active)
        selected.setdefault("id", "active-initiative")
        selected.setdefault("title", "Continue active SkillForge improvement initiative")
        selected.setdefault("lane", lane or selected.get("lane") or "builder")
        selected.setdefault("reason", "An active initiative is recorded in docs/improvement-loop/state.json.")
        selected.setdefault(
            "suggested_actions",
            [
                "Continue the active initiative until it reaches a reviewable outcome or a clear blocker.",
                "Avoid starting a new initiative unless the active one is blocked.",
            ],
        )
        selected.setdefault("expected_artifacts", ["Updated run log and initiative notes."])
        selected["backlog_items"] = backlog_items[:5]
        return selected

    candidates = [item for item in FOCUS_AREAS if lane is None or item["lane"] == lane]
    if not candidates:
        candidates = FOCUS_AREAS
    selected = dict(candidates[0])
    selected["backlog_items"] = backlog_items[:5]
    return selected


def claim_run_lock(
    repo_root: Path,
    run_id: str,
    *,
    stale_minutes: int = DEFAULT_STALE_MINUTES,
    lock_path: Path | None = None,
) -> dict:
    lock_path = lock_path or repo_root / DEFAULT_LOCK_PATH
    now = datetime.now(timezone.utc)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": run_id,
        "started_at": utc_now(),
        "stale_after_minutes": stale_minutes,
    }

    if lock_path.exists():
        active = read_json(lock_path)
        started = parse_utc(active.get("started_at") if isinstance(active, dict) else None)
        if started and (now - started).total_seconds() < stale_minutes * 60:
            return {
                "claimed": False,
                "lock_path": display_path(lock_path),
                "active_run": active,
                "message": "Another improvement-loop run appears active. Use read-only research or stop cleanly.",
            }
        try:
            lock_path.unlink()
        except OSError as exc:
            return {
                "claimed": False,
                "lock_path": display_path(lock_path),
                "active_run": active,
                "message": f"Existing lock looked stale, but could not be replaced: {exc}",
            }

    try:
        with lock_path.open("x", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
    except FileExistsError:
        active = read_json(lock_path)
        return {
            "claimed": False,
            "lock_path": display_path(lock_path),
            "active_run": active,
            "message": "Another run claimed the lock first.",
        }
    except OSError as exc:
        return {
            "claimed": False,
            "lock_path": display_path(lock_path),
            "active_run": None,
            "message": f"Could not create active-run lock: {exc}",
        }
    return {
        "claimed": True,
        "lock_path": display_path(lock_path),
        "active_run": payload,
        "message": "Improvement-loop run lock claimed.",
    }


def release_run_lock(repo_root: Path, run_id: str, *, lock_path: Path | None = None) -> dict:
    lock_path = lock_path or repo_root / DEFAULT_LOCK_PATH
    active = read_json(lock_path)
    if not active:
        return {
            "ok": True,
            "released": False,
            "lock_path": display_path(lock_path),
            "message": "No active improvement-loop lock was present.",
        }
    if active.get("run_id") != run_id:
        return {
            "ok": False,
            "released": False,
            "lock_path": display_path(lock_path),
            "active_run": active,
            "message": "Active improvement-loop lock belongs to another run.",
        }
    try:
        lock_path.unlink()
    except OSError as exc:
        return {
            "ok": False,
            "released": False,
            "lock_path": display_path(lock_path),
            "active_run": active,
            "message": f"Could not remove active-run lock: {exc}",
        }
    return {
        "ok": True,
        "released": True,
        "lock_path": display_path(lock_path),
        "message": "Improvement-loop run lock released.",
    }


def run_log_text(payload: dict) -> str:
    focus = payload["focus"]
    source_lines = []
    for source in payload["healthcare_sources"]:
        if source.get("url"):
            source_lines.append(f"- {source['name']}: {source['url']} - {source['why']}")
        else:
            source_lines.append(f"- {source['name']}: `{source['path']}` - {source['why']}")
    action_lines = [f"- {action}" for action in payload["suggested_actions"]]
    artifact_lines = [f"- {item}" for item in focus.get("expected_artifacts", [])]
    command_lines = [
        "- `python -m skillforge improve-cycle --write-log --claim-run --json`",
        f"- `python -m skillforge improve-cycle --release-run {payload['run_id']} --json`",
    ]
    return "\n".join(
        [
            "# SkillForge Improvement Loop Run",
            "",
            "## Run Metadata",
            "",
            f"- Run ID: `{payload['run_id']}`",
            f"- Created at: {payload['created_at']}",
            f"- Lane: `{payload['selected_lane']}`",
            f"- Repository: `{payload['repo_snapshot']['repo_root']}`",
            f"- Branch: `{payload['repo_snapshot'].get('branch') or 'unknown'}`",
            f"- Commit: `{payload['repo_snapshot'].get('commit') or 'unknown'}`",
            f"- Dirty checkout: `{payload['repo_snapshot']['dirty']}`",
            "",
            "## Selected Focus",
            "",
            f"Focus: **{focus['title']}**",
            "",
            f"Reason: {focus['reason']}",
            "",
            "## Healthcare Sources To Consider",
            "",
            *source_lines,
            "",
            "## Suggested Actions",
            "",
            *action_lines,
            "",
            "## Expected Reviewable Artifacts",
            "",
            *artifact_lines,
            "",
            "## Commands Run",
            "",
            *command_lines,
            "",
            "## Work Performed",
            "",
            "- Pending: replace this line with the actual work completed during this run.",
            "",
            "## Sources Reviewed",
            "",
            "- Pending: record URLs, local files, papers, READMEs, issues, or docs reviewed.",
            "",
            "## Files Changed",
            "",
            "- Pending: list files changed, or write `none` for read-only research.",
            "",
            "## Tests And Checks",
            "",
            "- Pending: list commands and results.",
            "",
            "## What Went Well",
            "",
            "- Pending.",
            "",
            "## What Could Be Improved",
            "",
            "- Pending.",
            "",
            "## Next Action",
            "",
            "- Pending: write the one best next action for the next run or human reviewer.",
            "",
        ]
    )


def write_run_log(log_dir: Path, payload: dict) -> Path:
    runs_dir = log_dir / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    safe_timestamp = payload["created_at"].replace(":", "").replace("-", "").replace("Z", "Z")
    path = runs_dir / f"{safe_timestamp}-{payload['run_id']}.md"
    path.write_text(run_log_text(payload), encoding="utf-8")
    return path


def improvement_cycle(
    *,
    repo_root: Path = REPO_ROOT,
    log_dir: str | Path | None = None,
    focus: str | None = None,
    lane: str | None = None,
    write_log: bool = False,
    claim_run: bool = False,
    release_run_id: str | None = None,
    stale_minutes: int = DEFAULT_STALE_MINUTES,
    lock_path: str | Path | None = None,
) -> dict:
    repo_root = repo_root.resolve()
    resolved_lock_path = resolve_under_repo(repo_root, lock_path, DEFAULT_LOCK_PATH) if lock_path else repo_root / DEFAULT_LOCK_PATH
    if release_run_id:
        release = release_run_lock(repo_root, release_run_id, lock_path=resolved_lock_path)
        return {
            "ok": release["ok"],
            "command": "improve-cycle",
            "action": "release-run",
            "read_only": False,
            **release,
        }

    normalized_lane = lane if lane in LANES else None
    log_root = resolve_under_repo(repo_root, log_dir, DEFAULT_LOG_DIR)
    run_id = uuid.uuid4().hex[:12]
    created_at = utc_now()
    state = load_state(log_root)
    backlog_items = read_backlog(log_root)
    snapshot = repo_snapshot(repo_root)
    selected_focus = select_focus(state, backlog_items, normalized_lane, focus)
    selected_lane = normalized_lane or selected_focus.get("lane") or "builder"
    suggested_actions = list(selected_focus.get("suggested_actions", []))

    warnings: list[str] = []
    if snapshot["dirty"]:
        warnings.append("Repository has uncommitted changes. Keep improvements scoped and avoid overwriting unrelated work.")
    if snapshot.get("branch") in {"main", "master"}:
        warnings.append("Current branch is a default branch. Prefer a review branch or worktree for autonomous improvement work.")
    if lane and lane not in LANES:
        warnings.append(f"Unknown lane '{lane}' ignored. Known lanes: {', '.join(sorted(LANES))}.")

    lock = {"claimed": False, "message": "No run lock requested."}
    if claim_run:
        lock = claim_run_lock(repo_root, run_id, stale_minutes=stale_minutes, lock_path=resolved_lock_path)
        if not lock.get("claimed"):
            suggested_actions = [
                "Do not modify shared files while another run is active.",
                "If useful, perform read-only research and record findings in a unique run log.",
                "If the active lock is stale, rerun with a larger stale window only after checking the active run.",
            ]
            warnings.append(lock.get("message", "Another run appears active."))

    payload = {
        "ok": True,
        "command": "improve-cycle",
        "action": "plan",
        "read_only": not write_log and not claim_run,
        "run_id": run_id,
        "created_at": created_at,
        "selected_lane": selected_lane,
        "lane_description": LANES.get(selected_lane),
        "focus": selected_focus,
        "healthcare_domain_focus": True,
        "healthcare_sources": HEALTHCARE_SOURCES,
        "repo_snapshot": snapshot,
        "state": state,
        "log_dir": display_path(log_root),
        "concurrency": {
            "lock_requested": claim_run,
            "lock": lock,
            "safe_concurrent_behavior": [
                "Use unique run logs.",
                "Avoid editing the same files as an active run.",
                "Prefer read-only research or a separate branch/worktree when another run is active.",
                "Release the run lock after work completes.",
            ],
        },
        "suggested_actions": suggested_actions,
        "warnings": warnings,
        "side_effects": [],
    }

    if write_log:
        log_path = write_run_log(log_root, payload)
        payload["log_path"] = display_path(log_path)
        payload["side_effects"].append(f"Wrote run log: {display_path(log_path)}")
    else:
        payload["log_path"] = None

    return payload


def render_improvement_cycle(payload: dict) -> str:
    if payload.get("action") == "release-run":
        return payload.get("message", "Improvement-loop run release processed.")

    lines = [
        "SkillForge Improvement Loop",
        "",
        f"Run ID: {payload['run_id']}",
        f"Lane: {payload['selected_lane']}",
        f"Focus: {payload['focus']['title']}",
        f"Reason: {payload['focus']['reason']}",
    ]
    if payload.get("log_path"):
        lines.append(f"Run log: {payload['log_path']}")
    if payload.get("warnings"):
        lines.extend(["", "Warnings:"])
        lines.extend(f"- {warning}" for warning in payload["warnings"])
    lines.extend(["", "Suggested actions:"])
    lines.extend(f"{index}. {action}" for index, action in enumerate(payload["suggested_actions"], start=1))
    if payload.get("concurrency", {}).get("lock", {}).get("claimed"):
        lines.extend(
            [
                "",
                "When the run is finished:",
                f"python -m skillforge improve-cycle --release-run {payload['run_id']} --json",
            ]
        )
    return "\n".join(lines)
