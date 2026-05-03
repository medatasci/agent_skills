from __future__ import annotations

from pathlib import Path
import os

from .catalog import REPO_ROOT, load_skill_metadata, skill_checksum
from .filesystem import copy_tree, remove_tree
from .validate import validate_skill


def default_global_codex_skills_dir() -> Path:
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        return Path(codex_home).expanduser() / "skills"
    return Path.home() / ".codex" / "skills"


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
