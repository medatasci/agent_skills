from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import shutil

from .validate import SkillValidation, iter_skill_files, validate_skill


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / "skills"
CATALOG_DIR = REPO_ROOT / "catalog"
CATALOG_SKILLS_DIR = CATALOG_DIR / "skills"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def skill_checksum(skill_dir: Path) -> str:
    digest = hashlib.sha256()
    for file_path in iter_skill_files(skill_dir):
        rel = file_path.relative_to(skill_dir).as_posix()
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_sha256(file_path).encode("ascii"))
        digest.update(b"\0")
    return digest.hexdigest()


def skill_files(skill_dir: Path) -> list[dict]:
    files: list[dict] = []
    for file_path in iter_skill_files(skill_dir):
        files.append(
            {
                "path": file_path.relative_to(skill_dir).as_posix(),
                "bytes": file_path.stat().st_size,
                "sha256": file_sha256(file_path),
            }
        )
    return files


def infer_tags(name: str, description: str) -> list[str]:
    text = f"{name} {description}".lower()
    tags: list[str] = []
    candidates = {
        "youtube": ["youtube", "video", "caption", "transcript"],
        "research": ["research", "evidence", "learning", "source"],
        "media": ["media", "mp4", "audio"],
        "project-memory": ["retrospective", "log", "memory", "after-action"],
        "documentation": ["documentation", "record", "summary"],
    }
    for tag, words in candidates.items():
        if any(word in text for word in words):
            tags.append(tag)
    return sorted(set(tags))


def metadata_from_validation(
    validation: SkillValidation,
    *,
    owner: str,
    source_path: Path | None = None,
    source_url: str | None = None,
) -> dict:
    if not validation.ok:
        raise ValueError("Cannot build metadata for invalid skill")

    skill_dir = validation.skill_dir
    name = validation.metadata["name"]
    description = validation.metadata["description"]
    catalog_path = Path("skills") / name
    source_path = source_path or skill_dir
    rel_source = source_path.resolve()
    try:
        source_path_value = rel_source.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        source_path_value = str(rel_source)

    return {
        "schema_version": "0.1",
        "id": name,
        "name": name,
        "description": description,
        "owner": owner,
        "tags": infer_tags(name, description),
        "source": {
            "type": "github-repo-path",
            "path": source_path_value,
            "url": source_url,
        },
        "catalog_path": catalog_path.as_posix(),
        "updated_at": utc_now(),
        "checksum": {
            "algorithm": "sha256-tree",
            "value": skill_checksum(skill_dir),
        },
        "codex": {
            "install_scopes": ["global", "project"],
            "global_install_command": f"python -m skillforge install {name} --scope global",
            "project_install_command": f"python -m skillforge install {name} --scope project --project .",
        },
        "files": skill_files(skill_dir),
        "warnings": validation.warnings,
    }


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_catalog() -> dict:
    catalog_path = CATALOG_DIR / "skills.json"
    if not catalog_path.exists():
        return {
            "schema_version": "0.1",
            "marketplace": "SkillForge",
            "generated_at": utc_now(),
            "skills": [],
        }
    return json.loads(catalog_path.read_text(encoding="utf-8"))


def build_catalog() -> dict:
    skills: list[dict] = []
    if SKILLS_DIR.exists():
        for skill_dir in sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir()):
            validation = validate_skill(skill_dir)
            if validation.ok:
                meta_path = CATALOG_SKILLS_DIR / f"{validation.metadata['name']}.json"
                if meta_path.exists():
                    metadata = json.loads(meta_path.read_text(encoding="utf-8"))
                    metadata["checksum"] = {
                        "algorithm": "sha256-tree",
                        "value": skill_checksum(skill_dir),
                    }
                    metadata["files"] = skill_files(skill_dir)
                    metadata["warnings"] = validation.warnings
                else:
                    metadata = metadata_from_validation(validation, owner="unknown")
                write_json(meta_path, metadata)
                skills.append(summary_from_metadata(metadata))

    generated_at = max((skill["updated_at"] for skill in skills), default=utc_now())
    catalog = {
        "schema_version": "0.1",
        "marketplace": "SkillForge",
        "generated_at": generated_at,
        "skills": sorted(skills, key=lambda item: item["id"]),
    }
    write_json(CATALOG_DIR / "skills.json", catalog)
    return catalog


def summary_from_metadata(metadata: dict) -> dict:
    return {
        "id": metadata["id"],
        "name": metadata["name"],
        "description": metadata["description"],
        "owner": metadata["owner"],
        "tags": metadata.get("tags", []),
        "source": metadata["source"],
        "catalog_path": metadata["catalog_path"],
        "updated_at": metadata["updated_at"],
        "checksum": metadata["checksum"],
        "codex": metadata["codex"],
        "warnings": metadata.get("warnings", []),
    }


def upload_skill(
    source: str | Path,
    *,
    owner: str,
    source_url: str | None = None,
    force: bool = False,
) -> dict:
    validation = validate_skill(source)
    if not validation.ok:
        raise ValueError("; ".join(validation.errors))

    name = validation.metadata["name"]
    dest = SKILLS_DIR / name
    source_dir = validation.skill_dir.resolve()

    if dest.exists():
        if not force:
            raise FileExistsError(f"Skill already exists: {dest}. Use --force to replace it.")
        shutil.rmtree(dest)

    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_dir, dest)
    copied_validation = validate_skill(dest)
    metadata = metadata_from_validation(
        copied_validation,
        owner=owner,
        source_path=source_dir,
        source_url=source_url,
    )
    write_json(CATALOG_SKILLS_DIR / f"{name}.json", metadata)
    build_catalog()
    return metadata


def load_skill_metadata(skill_id: str) -> dict:
    meta_path = CATALOG_SKILLS_DIR / f"{skill_id}.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"Skill not found in catalog: {skill_id}")
    return json.loads(meta_path.read_text(encoding="utf-8"))


def search_catalog(query: str, *, limit: int = 10) -> list[dict]:
    catalog = read_catalog()
    terms = [term for term in query.lower().replace("-", " ").split() if term]
    results: list[tuple[int, dict]] = []
    for skill in catalog.get("skills", []):
        haystack = " ".join(
            [
                skill.get("id", ""),
                skill.get("name", ""),
                skill.get("description", ""),
                " ".join(skill.get("tags", [])),
            ]
        ).lower()
        score = 0
        for term in terms:
            if term in haystack:
                score += 1
            if term == skill.get("id", "").lower():
                score += 5
        if query.lower() == skill.get("id", "").lower():
            score += 20
        if score:
            item = dict(skill)
            item["score"] = score
            results.append((score, item))
    results.sort(key=lambda pair: (-pair[0], pair[1]["id"]))
    return [item for _, item in results[:limit]]
