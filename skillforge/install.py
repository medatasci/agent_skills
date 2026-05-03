from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import os
import subprocess
import tomllib

from .catalog import REPO_ROOT, load_skill_metadata, skill_checksum
from .filesystem import copy_tree, remove_tree
from .validate import validate_skill


MARKETPLACE_ID = "agent-skills-marketplace"
MARKETPLACE_SOURCE = "https://github.com/medatasci/agent_skills.git"
MARKETPLACE_REF = "main"
PLUGIN_ID = "agent-skills@agent-skills-marketplace"
PLUGIN_RELATIVE_PATH = "plugins/agent-skills/.codex-plugin/plugin.json"
SKILL_LIST_RELATIVE_PATH = "plugins/agent-skills/skills/skill_list.md"


def default_codex_home() -> Path:
    codex_home = os.environ.get("CODEX_HOME")
    return Path(codex_home).expanduser() if codex_home else Path.home() / ".codex"


def default_global_codex_skills_dir() -> Path:
    return default_codex_home() / "skills"


def default_marketplace_dir(codex_home: str | Path | None = None) -> Path:
    root = Path(codex_home).expanduser() if codex_home else default_codex_home()
    return root / "plugins" / "cache" / MARKETPLACE_ID


def codex_config_path(codex_home: str | Path | None = None) -> Path:
    root = Path(codex_home).expanduser() if codex_home else default_codex_home()
    return root / "config.toml"


def project_codex_skills_dir(project: str | Path) -> Path:
    return Path(project).expanduser().resolve() / ".codex" / "skills"


def resolve_install_dir(scope: str, project: str | Path | None = None) -> Path:
    if scope == "global":
        override = os.environ.get("SKILLFORGE_CODEX_SKILLS_DIR")
        return Path(override).expanduser() if override else default_global_codex_skills_dir()
    if scope == "project":
        if not project:
            raise ValueError("--project is required for project scope")
        return project_codex_skills_dir(project)
    raise ValueError("scope must be global or project")


def git_stdout(args: list[str], *, repo_root: str | Path) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=Path(repo_root),
            text=True,
            capture_output=True,
            timeout=30,
            shell=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ""
    return completed.stdout.strip() if completed.returncode == 0 else ""


def git_repo_metadata(path: Path) -> dict:
    if not path.exists() or not path.is_dir():
        return {"is_git_repo": False, "remote_url": "", "branch": "", "commit": "", "dirty": False}
    top_level = git_stdout(["rev-parse", "--show-toplevel"], repo_root=path)
    if not top_level:
        return {"is_git_repo": False, "remote_url": "", "branch": "", "commit": "", "dirty": False}
    try:
        if Path(top_level).resolve() != path.resolve():
            return {"is_git_repo": False, "remote_url": "", "branch": "", "commit": "", "dirty": False}
    except OSError:
        return {"is_git_repo": False, "remote_url": "", "branch": "", "commit": "", "dirty": False}
    commit = git_stdout(["rev-parse", "HEAD"], repo_root=path)
    branch = git_stdout(["branch", "--show-current"], repo_root=path)
    remote_url = git_stdout(["remote", "get-url", "origin"], repo_root=path)
    dirty = bool(git_stdout(["status", "--porcelain"], repo_root=path)) if commit else False
    return {
        "is_git_repo": bool(commit),
        "remote_url": remote_url,
        "branch": branch,
        "commit": commit,
        "dirty": dirty,
    }


def read_json_file(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def file_mtime(path: Path) -> str:
    try:
        timestamp = path.stat().st_mtime
    except OSError:
        return ""
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def marketplace_files_status(path: Path) -> dict:
    exists = path.exists()
    is_dir = path.is_dir()
    plugin_json = path / PLUGIN_RELATIVE_PATH
    skill_list = path / SKILL_LIST_RELATIVE_PATH
    python_cli = path / "skillforge" / "cli.py"
    readme = path / "README.md"
    expected = {
        "python_cli": str(python_cli),
        "plugin_json": str(plugin_json),
        "skill_list": str(skill_list),
        "readme": str(readme),
    }
    present = {key: Path(value).exists() for key, value in expected.items()}
    mtimes = {key: file_mtime(Path(value)) if present[key] else "" for key, value in expected.items()}
    plugin_metadata = read_json_file(plugin_json) if present["plugin_json"] else {}
    required = ["plugin_json", "skill_list", "readme"]
    return {
        "path": str(path),
        "exists": exists,
        "is_dir": is_dir,
        "expected_files": expected,
        "present": present,
        "file_updated_at": mtimes,
        "plugin_metadata": plugin_metadata,
        "required_files": required,
        "is_skillforge": exists and is_dir and all(present[key] for key in required),
    }


def read_codex_config(path: Path) -> dict:
    if not path.exists():
        return {"exists": False, "parse_ok": True, "data": {}, "error": ""}
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return {"exists": True, "parse_ok": False, "data": {}, "error": str(exc)}
    return {"exists": True, "parse_ok": True, "data": data, "error": ""}


def codex_config_status(path: Path) -> dict:
    parsed = read_codex_config(path)
    data = parsed["data"]
    marketplaces = data.get("marketplaces", {}) if isinstance(data, dict) else {}
    plugins = data.get("plugins", {}) if isinstance(data, dict) else {}
    marketplace = marketplaces.get(MARKETPLACE_ID, {}) if isinstance(marketplaces, dict) else {}
    plugin = plugins.get(PLUGIN_ID, {}) if isinstance(plugins, dict) else {}

    marketplace_exists = isinstance(marketplace, dict) and bool(marketplace)
    plugin_exists = isinstance(plugin, dict) and bool(plugin)
    desired_marketplace = {
        "source_type": "git",
        "source": MARKETPLACE_SOURCE,
        "ref": MARKETPLACE_REF,
    }
    marketplace_conflicts = []
    if marketplace_exists:
        for key, expected in desired_marketplace.items():
            actual = marketplace.get(key)
            if actual not in {None, expected}:
                marketplace_conflicts.append({"field": key, "expected": expected, "actual": actual})
    plugin_conflicts = []
    if plugin_exists and plugin.get("enabled") is not True:
        plugin_conflicts.append({"field": "enabled", "expected": True, "actual": plugin.get("enabled")})

    missing_entries = []
    if parsed["parse_ok"]:
        if not marketplace_exists:
            missing_entries.append("marketplace")
        if not plugin_exists:
            missing_entries.append("plugin")

    marketplace_registered = (
        parsed["parse_ok"]
        and marketplace_exists
        and not marketplace_conflicts
        and marketplace.get("source_type") == "git"
        and marketplace.get("source") == MARKETPLACE_SOURCE
        and marketplace.get("ref") == MARKETPLACE_REF
    )
    plugin_enabled = parsed["parse_ok"] and plugin_exists and plugin.get("enabled") is True
    return {
        "path": str(path),
        "exists": parsed["exists"],
        "parse_ok": parsed["parse_ok"],
        "parse_error": parsed["error"],
        "marketplace_registered": marketplace_registered,
        "marketplace_table_exists": marketplace_exists,
        "marketplace": marketplace if isinstance(marketplace, dict) else {},
        "plugin_enabled": plugin_enabled,
        "plugin_table_exists": plugin_exists,
        "plugin": plugin if isinstance(plugin, dict) else {},
        "missing_entries": missing_entries,
        "conflicts": {
            "marketplace": marketplace_conflicts,
            "plugin": plugin_conflicts,
        },
        "repairable": parsed["parse_ok"] and bool(missing_entries) and not marketplace_conflicts and not plugin_conflicts,
    }


def desired_config_block(entries: list[str]) -> str:
    blocks: list[str] = []
    if "marketplace" in entries:
        blocks.append(
            "\n".join(
                [
                    f"[marketplaces.{MARKETPLACE_ID}]",
                    'source_type = "git"',
                    f'source = "{MARKETPLACE_SOURCE}"',
                    f'ref = "{MARKETPLACE_REF}"',
                ]
            )
        )
    if "plugin" in entries:
        blocks.append(
            "\n".join(
                [
                    f'[plugins."{PLUGIN_ID}"]',
                    "enabled = true",
                ]
            )
        )
    return "\n\n".join(blocks)


def append_codex_config(path: Path, entries: list[str]) -> None:
    if not entries:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    separator = "\n\n" if existing and not existing.endswith("\n\n") else ""
    path.write_text(existing + separator + desired_config_block(entries) + "\n", encoding="utf-8")


def marketplace_version_status(files: dict, git: dict, config: dict) -> dict:
    marketplace_config = config.get("marketplace", {}) if isinstance(config.get("marketplace"), dict) else {}
    plugin = files.get("plugin_metadata", {}) if isinstance(files.get("plugin_metadata"), dict) else {}
    file_updated_at = files.get("file_updated_at", {}) if isinstance(files.get("file_updated_at"), dict) else {}

    source_repo = git.get("remote_url") or marketplace_config.get("source") or plugin.get("repository") or MARKETPLACE_SOURCE
    code_version = git.get("commit") or plugin.get("version") or ""
    code_version_source = "git_commit" if git.get("commit") else ("plugin_version" if plugin.get("version") else "")
    last_updated = marketplace_config.get("last_updated") or file_updated_at.get("plugin_json") or file_updated_at.get("readme") or ""
    if marketplace_config.get("last_updated"):
        last_updated_source = "codex_config.marketplace.last_updated"
    elif file_updated_at.get("plugin_json"):
        last_updated_source = "plugin_json_mtime"
    elif file_updated_at.get("readme"):
        last_updated_source = "readme_mtime"
    else:
        last_updated_source = ""

    return {
        "source_repo": source_repo,
        "configured_ref": marketplace_config.get("ref") or MARKETPLACE_REF,
        "configured_source_type": marketplace_config.get("source_type") or "git",
        "git_branch": git.get("branch", ""),
        "git_commit": git.get("commit", ""),
        "git_dirty": git.get("dirty", False),
        "plugin_name": plugin.get("name", ""),
        "plugin_version": plugin.get("version", ""),
        "plugin_repository": plugin.get("repository", ""),
        "code_version": code_version,
        "code_version_source": code_version_source,
        "last_updated": last_updated,
        "last_updated_source": last_updated_source,
    }


def install_skillforge_marketplace(
    *,
    codex_home: str | Path | None = None,
    marketplace_path: str | Path | None = None,
    yes: bool = False,
) -> dict:
    root = Path(codex_home).expanduser() if codex_home else default_codex_home()
    marketplace = Path(marketplace_path).expanduser() if marketplace_path else default_marketplace_dir(root)
    config_path = codex_config_path(root)
    files = marketplace_files_status(marketplace)
    git = git_repo_metadata(marketplace)
    config = codex_config_status(config_path)
    actions: list[str] = []
    warnings: list[str] = []

    if not files["exists"]:
        actions.append("clone_required")
    elif not files["is_dir"]:
        actions.append("path_conflict")
    elif not files["is_skillforge"]:
        actions.append("not_skillforge_path")

    config_conflicts = bool(config["conflicts"]["marketplace"] or config["conflicts"]["plugin"])
    if not config["parse_ok"]:
        actions.append("manual_config_repair_required")
    elif config_conflicts:
        actions.append("manual_config_repair_required")
    elif config["marketplace_table_exists"] and not config["marketplace_registered"]:
        actions.append("manual_config_repair_required")
    elif config["plugin_table_exists"] and not config["plugin_enabled"]:
        actions.append("manual_config_repair_required")
    elif config["repairable"] and files["is_skillforge"]:
        actions.append("config_repair_available")

    if git["is_git_repo"] and git["remote_url"] and git["remote_url"] != MARKETPLACE_SOURCE:
        warnings.append("Marketplace checkout uses a different origin remote; review before updating.")
    if git["dirty"]:
        warnings.append("Marketplace checkout has local changes; update should refuse until clean.")

    changed = False
    if yes and files["is_skillforge"] and config["repairable"]:
        append_codex_config(config_path, config["missing_entries"])
        changed = True
        config = codex_config_status(config_path)
        actions = [action for action in actions if action != "config_repair_available"]

    healthy = files["is_skillforge"] and config["marketplace_registered"] and config["plugin_enabled"]
    if healthy:
        status = "repaired" if changed else "healthy"
    elif "clone_required" in actions:
        status = "missing"
    elif "path_conflict" in actions or "not_skillforge_path" in actions:
        status = "conflict"
    elif "manual_config_repair_required" in actions:
        status = "manual_attention"
    elif "config_repair_available" in actions:
        status = "repair_available"
    else:
        status = "unknown"

    clone_command = f'git clone --depth 1 --branch {MARKETPLACE_REF} {MARKETPLACE_SOURCE} "{marketplace}"'
    next_commands = []
    if status == "repair_available":
        next_commands.append("python -m skillforge install-skillforge --yes")
    if healthy:
        next_commands.extend(
            [
                "python -m skillforge welcome",
                "python -m skillforge update-check --json",
                "python -m skillforge update --yes",
            ]
        )
    elif status == "missing":
        next_commands.append(clone_command)

    return {
        "ok": healthy or status == "repair_available",
        "status": status,
        "changed": changed,
        "codex_home": str(root),
        "version": marketplace_version_status(files, git, config),
        "config": config,
        "marketplace": {
            **files,
            "git": git,
            "expected_source": MARKETPLACE_SOURCE,
            "expected_ref": MARKETPLACE_REF,
        },
        "actions": actions,
        "warnings": warnings,
        "clone_command": clone_command,
        "next_commands": next_commands,
    }


def install_skill(skill_id: str, *, scope: str, project: str | Path | None = None, force: bool = False) -> Path:
    metadata = load_skill_metadata(skill_id)
    source = REPO_ROOT / metadata["catalog_path"]
    validation = validate_skill(source)
    if not validation.ok:
        raise ValueError("; ".join(validation.errors))
    expected_checksum = metadata["checksum"]["value"]
    actual_checksum = skill_checksum(source)
    if actual_checksum != expected_checksum:
        raise ValueError(f"Checksum mismatch for {skill_id}: expected {expected_checksum}, got {actual_checksum}")

    install_root = resolve_install_dir(scope, project)
    target = install_root / skill_id
    if target.exists():
        if not force:
            raise FileExistsError(f"Skill already installed: {target}. Use --force to replace it.")
        remove_tree(target)

    install_root.mkdir(parents=True, exist_ok=True)
    copy_tree(source, target)
    return target


def download_skill(skill_id: str, *, destination: str | Path, force: bool = False) -> Path:
    metadata = load_skill_metadata(skill_id)
    source = REPO_ROOT / metadata["catalog_path"]
    validation = validate_skill(source)
    if not validation.ok:
        raise ValueError("; ".join(validation.errors))
    expected_checksum = metadata["checksum"]["value"]
    actual_checksum = skill_checksum(source)
    if actual_checksum != expected_checksum:
        raise ValueError(f"Checksum mismatch for {skill_id}: expected {expected_checksum}, got {actual_checksum}")

    destination = Path(destination).expanduser().resolve()
    target = destination / skill_id if destination.is_dir() or destination.suffix == "" else destination
    if target.exists():
        if not force:
            raise FileExistsError(f"Download target already exists: {target}. Use --force to replace it.")
        remove_tree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    copy_tree(source, target)
    return target


def list_installed(scope: str, project: str | Path | None = None) -> list[dict]:
    install_root = resolve_install_dir(scope, project)
    if not install_root.exists():
        return []
    results: list[dict] = []
    for skill_dir in sorted(path for path in install_root.iterdir() if path.is_dir()):
        validation = validate_skill(skill_dir)
        results.append(
            {
                "id": validation.metadata.get("name", skill_dir.name),
                "path": str(skill_dir),
                "ok": validation.ok,
                "errors": validation.errors,
                "warnings": validation.warnings,
            }
        )
    return results


def remove_installed_skill(skill_id: str, *, scope: str, project: str | Path | None = None) -> Path:
    install_root = resolve_install_dir(scope, project)
    target = install_root / skill_id
    if not target.exists():
        raise FileNotFoundError(f"Skill is not installed: {target}")
    if not target.is_dir():
        raise ValueError(f"Installed skill path is not a directory: {target}")
    remove_tree(target)
    return target
