from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import subprocess

from .catalog import REPO_ROOT, utc_now
from .peer import cache_root


UPDATE_STATE_VERSION = 1
DEFAULT_UPDATE_TTL_HOURS = 6


def update_state_path(cache_dir: str | Path | None = None) -> Path:
    return cache_root(cache_dir) / "state" / "update-status.json"


def run_git(args: list[str], *, repo_root: str | Path = REPO_ROOT, timeout: int = 30) -> dict:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=Path(repo_root),
            text=True,
            capture_output=True,
            timeout=timeout,
            shell=False,
        )
    except FileNotFoundError as exc:
        return {"ok": False, "returncode": 127, "stdout": "", "stderr": str(exc), "args": args}
    except subprocess.TimeoutExpired as exc:
        return {
            "ok": False,
            "returncode": None,
            "stdout": exc.stdout or "",
            "stderr": f"git command timed out after {timeout}s",
            "args": args,
        }
    return {
        "ok": completed.returncode == 0,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
        "args": args,
    }


def git_stdout(args: list[str], *, repo_root: str | Path = REPO_ROOT, required: bool = False) -> str:
    result = run_git(args, repo_root=repo_root)
    if required and not result["ok"]:
        message = result["stderr"] or result["stdout"] or f"git {' '.join(args)} failed"
        raise RuntimeError(message)
    return result["stdout"] if result["ok"] else ""


def read_state(cache_dir: str | Path | None = None) -> dict | None:
    path = update_state_path(cache_dir)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def write_state(payload: dict, cache_dir: str | Path | None = None) -> None:
    path = update_state_path(cache_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_time(value: str | None) -> datetime | None:
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


def state_is_fresh(state: dict | None, *, local_commit: str, ttl_hours: int) -> bool:
    if not state or state.get("version") != UPDATE_STATE_VERSION:
        return False
    if state.get("local_commit") != local_commit:
        return False
    checked_at = parse_time(state.get("checked_at"))
    if not checked_at:
        return False
    return datetime.now(timezone.utc) - checked_at < timedelta(hours=max(ttl_hours, 0))


def current_branch(repo_root: str | Path = REPO_ROOT) -> str:
    branch = git_stdout(["branch", "--show-current"], repo_root=repo_root)
    return branch or "HEAD"


def upstream_ref(repo_root: str | Path = REPO_ROOT) -> str:
    upstream = git_stdout(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], repo_root=repo_root)
    if upstream:
        return upstream
    branch = current_branch(repo_root)
    return f"origin/{branch}" if branch and branch != "HEAD" else ""


def split_upstream(ref: str) -> tuple[str, str]:
    if "/" not in ref:
        return "origin", ref
    remote, branch = ref.split("/", 1)
    return remote, branch


def fetch_upstream(repo_root: str | Path, remote: str, branch: str) -> dict:
    if not remote or not branch:
        return {"attempted": False, "ok": False, "error": "No upstream remote/branch is configured."}
    refspec = f"{branch}:refs/remotes/{remote}/{branch}"
    result = run_git(["fetch", "--quiet", remote, refspec], repo_root=repo_root, timeout=60)
    return {
        "attempted": True,
        "ok": result["ok"],
        "error": "" if result["ok"] else (result["stderr"] or result["stdout"]),
        "returncode": result["returncode"],
    }


def ahead_behind(repo_root: str | Path, upstream: str) -> tuple[int, int]:
    counts = git_stdout(["rev-list", "--left-right", "--count", f"HEAD...{upstream}"], repo_root=repo_root)
    if not counts:
        return 0, 0
    parts = counts.split()
    if len(parts) != 2:
        return 0, 0
    try:
        return int(parts[0]), int(parts[1])
    except ValueError:
        return 0, 0


def update_check(
    *,
    repo_root: str | Path = REPO_ROOT,
    cache_dir: str | Path | None = None,
    refresh: bool = False,
    no_fetch: bool = False,
    ttl_hours: int = DEFAULT_UPDATE_TTL_HOURS,
) -> dict:
    repo = Path(repo_root).resolve()
    local_commit = git_stdout(["rev-parse", "HEAD"], repo_root=repo, required=True)
    state = read_state(cache_dir)
    state_path = update_state_path(cache_dir)
    if not refresh and not no_fetch and state_is_fresh(state, local_commit=local_commit, ttl_hours=ttl_hours):
        payload = dict(state.get("payload", {}))
        payload["cache"] = {"used": True, "path": str(state_path), "ttl_hours": ttl_hours}
        return payload

    branch = current_branch(repo)
    upstream = upstream_ref(repo)
    remote, remote_branch = split_upstream(upstream) if upstream else ("", "")
    remote_url = git_stdout(["remote", "get-url", remote], repo_root=repo) if remote else ""
    fetch = {"attempted": False, "ok": None, "error": "", "returncode": None}
    if not no_fetch:
        fetch = fetch_upstream(repo, remote, remote_branch)

    upstream_commit = git_stdout(["rev-parse", upstream], repo_root=repo) if upstream else ""
    ahead, behind = ahead_behind(repo, upstream) if upstream_commit else (0, 0)
    dirty = bool(git_stdout(["status", "--porcelain"], repo_root=repo))
    ok = bool(local_commit and upstream_commit) and (fetch["ok"] is not False or no_fetch)
    next_command = "python -m skillforge whats-new"
    if behind:
        next_command = f"python -m skillforge whats-new --since {local_commit}"
    payload = {
        "ok": ok,
        "repo_root": str(repo),
        "branch": branch,
        "remote": remote,
        "remote_url": remote_url,
        "upstream_ref": upstream,
        "local_commit": local_commit,
        "upstream_commit": upstream_commit,
        "updates_available": behind > 0,
        "ahead_by": ahead,
        "behind_by": behind,
        "diverged": ahead > 0 and behind > 0,
        "dirty": dirty,
        "checked_at": utc_now(),
        "fetch": fetch,
        "next_command": next_command,
        "cache": {"used": False, "path": str(state_path), "ttl_hours": ttl_hours},
    }
    try:
        write_state(
            {
                "version": UPDATE_STATE_VERSION,
                "checked_at": payload["checked_at"],
                "local_commit": local_commit,
                "upstream_commit": upstream_commit,
                "payload": payload,
            },
            cache_dir,
        )
        payload["cache"]["write_ok"] = True
        payload["cache"]["write_error"] = ""
    except OSError as exc:
        payload["cache"]["write_ok"] = False
        payload["cache"]["write_error"] = str(exc)
    return payload


def refuse_update(check: dict, reason: str) -> dict:
    return {
        "ok": False,
        "updated": False,
        "refused": True,
        "requires_confirmation": False,
        "reason": reason,
        "check": check,
        "repo_root": check.get("repo_root"),
        "previous_commit": check.get("local_commit"),
        "current_commit": check.get("local_commit"),
        "upstream_commit": check.get("upstream_commit"),
        "upstream_ref": check.get("upstream_ref"),
        "behind_by_before": check.get("behind_by", 0),
        "ahead_by_before": check.get("ahead_by", 0),
        "dirty_before": check.get("dirty", False),
        "merge": {"attempted": False, "ok": None, "error": "", "returncode": None},
        "whats_new": None,
        "post_check": None,
        "next_command": "python -m skillforge update-check --json",
    }


def update_skillforge(
    *,
    repo_root: str | Path = REPO_ROOT,
    cache_dir: str | Path | None = None,
    yes: bool = False,
    no_fetch: bool = False,
    ttl_hours: int = DEFAULT_UPDATE_TTL_HOURS,
) -> dict:
    check = update_check(
        repo_root=repo_root,
        cache_dir=cache_dir,
        refresh=True,
        no_fetch=no_fetch,
        ttl_hours=ttl_hours,
    )
    if not check.get("ok"):
        return refuse_update(check, "Could not compare the local checkout with upstream.")

    if check.get("diverged"):
        return refuse_update(check, "Local branch and upstream have diverged; resolve with Git before using SkillForge update.")

    if check.get("ahead_by", 0) > 0 and check.get("behind_by", 0) == 0:
        return {
            "ok": True,
            "updated": False,
            "refused": False,
            "requires_confirmation": False,
            "reason": "Local checkout is ahead of upstream; no update is needed.",
            "check": check,
            "repo_root": check.get("repo_root"),
            "previous_commit": check.get("local_commit"),
            "current_commit": check.get("local_commit"),
            "upstream_commit": check.get("upstream_commit"),
            "upstream_ref": check.get("upstream_ref"),
            "behind_by_before": check.get("behind_by", 0),
            "ahead_by_before": check.get("ahead_by", 0),
            "dirty_before": check.get("dirty", False),
            "merge": {"attempted": False, "ok": None, "error": "", "returncode": None},
            "whats_new": None,
            "post_check": None,
            "next_command": "python -m skillforge whats-new",
        }

    if check.get("behind_by", 0) <= 0:
        return {
            "ok": True,
            "updated": False,
            "refused": False,
            "requires_confirmation": False,
            "reason": "SkillForge is already up to date with the known upstream ref.",
            "check": check,
            "repo_root": check.get("repo_root"),
            "previous_commit": check.get("local_commit"),
            "current_commit": check.get("local_commit"),
            "upstream_commit": check.get("upstream_commit"),
            "upstream_ref": check.get("upstream_ref"),
            "behind_by_before": 0,
            "ahead_by_before": check.get("ahead_by", 0),
            "dirty_before": check.get("dirty", False),
            "merge": {"attempted": False, "ok": None, "error": "", "returncode": None},
            "whats_new": None,
            "post_check": None,
            "next_command": "python -m skillforge update-check --json",
        }

    if not yes:
        return {
            "ok": True,
            "updated": False,
            "refused": False,
            "requires_confirmation": True,
            "reason": (
                "Updates are available; clean the checkout before applying with --yes."
                if check.get("dirty")
                else "Updates are available; rerun with --yes to apply a fast-forward update."
            ),
            "check": check,
            "repo_root": check.get("repo_root"),
            "previous_commit": check.get("local_commit"),
            "current_commit": check.get("local_commit"),
            "upstream_commit": check.get("upstream_commit"),
            "upstream_ref": check.get("upstream_ref"),
            "behind_by_before": check.get("behind_by", 0),
            "ahead_by_before": check.get("ahead_by", 0),
            "dirty_before": check.get("dirty", False),
            "merge": {"attempted": False, "ok": None, "error": "", "returncode": None},
            "whats_new": None,
            "post_check": None,
            "next_command": "python -m skillforge update --yes",
        }

    if check.get("dirty"):
        return refuse_update(check, "Local checkout has uncommitted changes; commit, stash, or discard them before updating.")

    repo = Path(repo_root).resolve()
    previous_commit = check.get("local_commit", "")
    upstream = check.get("upstream_ref", "")
    merge_result = run_git(["merge", "--ff-only", upstream], repo_root=repo, timeout=120)
    merge = {
        "attempted": True,
        "ok": merge_result["ok"],
        "error": "" if merge_result["ok"] else (merge_result["stderr"] or merge_result["stdout"]),
        "returncode": merge_result["returncode"],
    }
    if not merge_result["ok"]:
        payload = refuse_update(check, merge["error"] or "Fast-forward update failed.")
        payload["merge"] = merge
        return payload

    current_commit = git_stdout(["rev-parse", "HEAD"], repo_root=repo, required=True)
    changes = whats_new(repo_root=repo, cache_dir=cache_dir, since=previous_commit, until="HEAD")
    post_check = update_check(
        repo_root=repo,
        cache_dir=cache_dir,
        refresh=True,
        no_fetch=True,
        ttl_hours=ttl_hours,
    )
    return {
        "ok": True,
        "updated": current_commit != previous_commit,
        "refused": False,
        "requires_confirmation": False,
        "reason": "SkillForge updated with a fast-forward merge.",
        "check": check,
        "repo_root": str(repo),
        "previous_commit": previous_commit,
        "current_commit": current_commit,
        "upstream_commit": check.get("upstream_commit"),
        "upstream_ref": upstream,
        "behind_by_before": check.get("behind_by", 0),
        "ahead_by_before": check.get("ahead_by", 0),
        "dirty_before": False,
        "merge": merge,
        "whats_new": changes,
        "post_check": post_check,
        "next_command": f"python -m skillforge whats-new --since {previous_commit}",
    }


def short_commit(commit: str | None) -> str:
    return (commit or "")[:12]


def git_log(repo_root: str | Path, revision_range: str, *, limit: int) -> list[dict]:
    args = ["log", "--pretty=format:%H%x1f%s%x1f%ad", "--date=iso-strict", f"--max-count={limit}"]
    if revision_range:
        args.append(revision_range)
    output = git_stdout(args, repo_root=repo_root)
    commits: list[dict] = []
    for line in output.splitlines():
        parts = line.split("\x1f")
        if len(parts) != 3:
            continue
        commits.append({"commit": parts[0], "summary": parts[1], "date": parts[2]})
    return commits


def changed_files(repo_root: str | Path, revision_range: str, current: str) -> list[dict]:
    if revision_range:
        output = git_stdout(["diff", "--name-status", revision_range], repo_root=repo_root)
    else:
        output = git_stdout(["show", "--name-status", "--pretty=format:", current], repo_root=repo_root)
    files: list[dict] = []
    for line in output.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            files.append({"status": parts[0], "path": parts[-1]})
    return files


def infer_categories(files: list[dict], commits: list[dict]) -> dict:
    categories = {
        "new_skills": [],
        "skill_changes": [],
        "search_or_catalog": [],
        "python_cli": [],
        "documentation": [],
        "peer_catalogs": [],
        "tests": [],
        "breaking_or_risky": [],
    }
    for item in files:
        path = item["path"].replace("\\", "/")
        status = item["status"]
        if path.startswith("skills/"):
            categories["skill_changes"].append(path)
            if status.startswith("A") and path.count("/") >= 2:
                categories["new_skills"].append(path.split("/")[1])
        if path.startswith(("catalog/", "site/", "schemas/")) or path in {"peer-catalogs.json"}:
            categories["search_or_catalog"].append(path)
        if path.startswith("skillforge/"):
            categories["python_cli"].append(path)
        if path.startswith("docs/") or path in {"README.md", "requirements.md", "software-dev-todo.md"}:
            categories["documentation"].append(path)
        if path == "peer-catalogs.json" or "peer" in path.lower():
            categories["peer_catalogs"].append(path)
        if path.startswith("tests/"):
            categories["tests"].append(path)
    risky_terms = ("breaking", "remove", "removed", "deprecat", "risk", "unsafe", "secret", "permission")
    for commit in commits:
        if any(term in commit["summary"].lower() for term in risky_terms):
            categories["breaking_or_risky"].append(commit["summary"])
    return {key: sorted(set(value)) for key, value in categories.items()}


def technical_summary_lines(categories: dict, commits: list[dict]) -> list[str]:
    if not commits:
        return ["No Git changes found for the selected range."]
    lines = [f"Found {len(commits)} commits in the selected range."]
    if categories["new_skills"]:
        lines.append(f"New skills: {', '.join(categories['new_skills'])}.")
    if categories["skill_changes"]:
        lines.append(f"Skill files changed: {len(categories['skill_changes'])}.")
    if categories["python_cli"]:
        lines.append(f"Python/CLI changes: {', '.join(categories['python_cli'][:5])}.")
    if categories["search_or_catalog"]:
        lines.append("Catalog, search, or static site outputs changed.")
    if categories["peer_catalogs"]:
        lines.append("Peer catalog or peer-search related files changed.")
    if categories["documentation"]:
        lines.append("Documentation changed.")
    if categories["breaking_or_risky"]:
        lines.append("Potentially risky or breaking commit subjects should be reviewed.")
    return lines


def commit_subjects(commits: list[dict]) -> str:
    return " ".join(commit.get("summary", "").lower() for commit in commits)


def changed_paths(files: list[dict]) -> list[str]:
    return [item["path"].replace("\\", "/") for item in files]


def has_any_path(paths: list[str], prefixes: tuple[str, ...] = (), exact: set[str] | None = None, contains: tuple[str, ...] = ()) -> bool:
    exact = exact or set()
    return any(path in exact or path.startswith(prefixes) or any(value in path for value in contains) for path in paths)


def user_feature_summary_lines(categories: dict, commits: list[dict], files: list[dict]) -> list[str]:
    if not commits:
        return ["No user-facing SkillForge changes were found in the selected range."]

    paths = changed_paths(files)
    subjects = commit_subjects(commits)
    lines: list[str] = []

    if categories["new_skills"]:
        lines.append(f"New skills are available: {', '.join(categories['new_skills'])}.")

    seo_changed = (
        "seo" in subjects
        or "discovery" in subjects
        or "search index" in subjects
        or has_any_path(
            paths,
            prefixes=("site/",),
            exact={"docs/skill-search-seo-plan.md", "catalog/search-index.json", "schemas/search-index.schema.json"},
            contains=("/README.md", "skill-discovery-evaluation"),
        )
    )
    if seo_changed:
        lines.append(
            "Better skill discovery and SEO: skills are easier to find through README home pages, richer metadata, search indexes, generated catalog pages, and agent-readable discovery files."
        )

    search_changed = (
        "search" in subjects
        or "peer" in subjects
        or has_any_path(paths, prefixes=("catalog/",), exact={"peer-catalogs.json"}, contains=("peer", "search"))
    )
    if search_changed:
        lines.append(
            "Search is more useful: SkillForge can surface richer local and peer-catalog results with source-aware context, comments, install commands, and review links."
        )

    install_update_changed = (
        "install" in subjects
        or "update" in subjects
        or has_any_path(paths, exact={"skillforge/install.py", "skillforge/update.py"}, contains=("install", "update"))
    )
    if install_update_changed:
        lines.append(
            "Install and update flows are safer: SkillForge can verify existing installs, report source/version status, check upstream changes, and apply only safe fast-forward updates."
        )

    help_changed = (
        "welcome" in subjects
        or "help" in subjects
        or "onboarding" in subjects
        or "chattiness" in subjects
        or has_any_path(paths, exact={"skillforge/help.py", "skillforge/output.py"}, contains=("help", "welcome", "output"))
    )
    if help_changed:
        lines.append(
            "Onboarding and help improved: users and agents have clearer welcome, getting-started, help, and output-style guidance."
        )

    creation_changed = (
        "create" in subjects
        or "publication" in subjects
        or "evaluate" in subjects
        or has_any_path(paths, exact={"skillforge/create.py"}, contains=("templates/skill", "skill-discovery-evaluation", "validate"))
    )
    if creation_changed:
        lines.append(
            "Skill creation and publishing improved: new templates, evaluation checks, and publication guidance make reusable skills easier to package."
        )

    cross_platform_changed = "cross-platform" in subjects or has_any_path(paths, exact={"skillforge/filesystem.py"})
    if cross_platform_changed:
        lines.append("Cross-platform behavior improved for Windows, macOS, and Linux workflows.")

    docs_changed = categories["documentation"] and not seo_changed and not help_changed
    if docs_changed:
        lines.append("Documentation changed to make SkillForge workflows easier to understand.")

    if categories["breaking_or_risky"]:
        lines.append("Potentially risky or breaking changes were detected and should be reviewed before relying on the update.")

    if not lines:
        lines.append("SkillForge changed internally, but no major user-facing feature category was detected.")
    return lines


def default_since(repo_root: str | Path, current: str, cache_dir: str | Path | None = None) -> str:
    state = read_state(cache_dir)
    cached_local = (state or {}).get("local_commit")
    if cached_local and cached_local != current:
        return cached_local
    commits = git_stdout(["rev-list", "--max-count=6", current], repo_root=repo_root).splitlines()
    return commits[-1] if len(commits) > 1 else ""


def whats_new(
    *,
    repo_root: str | Path = REPO_ROOT,
    cache_dir: str | Path | None = None,
    since: str | None = None,
    until: str = "HEAD",
    limit: int = 50,
) -> dict:
    repo = Path(repo_root).resolve()
    current_commit = git_stdout(["rev-parse", until], repo_root=repo, required=True)
    since_commit = git_stdout(["rev-parse", since], repo_root=repo) if since else default_since(repo, current_commit, cache_dir)
    revision_range = f"{since_commit}..{current_commit}" if since_commit and since_commit != current_commit else ""
    commits = git_log(repo, revision_range, limit=limit)
    files = changed_files(repo, revision_range, current_commit)
    categories = infer_categories(files, commits)
    feature_lines = user_feature_summary_lines(categories, commits, files)
    technical_lines = technical_summary_lines(categories, commits)
    return {
        "ok": True,
        "repo_root": str(repo),
        "since_commit": since_commit,
        "current_commit": current_commit,
        "revision_range": revision_range,
        "commit_count": len(commits),
        "commits": commits,
        "changed_files": files,
        "categories": categories,
        "summary": feature_lines,
        "technical_summary": technical_lines,
        "detail_prompt": "Would you like more detail, such as commits, changed files, or command examples?",
    }
