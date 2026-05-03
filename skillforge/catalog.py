from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import html
import json
import re

from .filesystem import copy_tree, remove_tree
from .validate import SkillValidation, iter_skill_files, validate_skill


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / "skills"
CATALOG_DIR = REPO_ROOT / "catalog"
CATALOG_SKILLS_DIR = CATALOG_DIR / "skills"
SITE_DIR = REPO_ROOT / "site"
SEARCH_INDEX_PATH = CATALOG_DIR / "search-index.json"
DISCOVERY_FIELDS = [
    "title",
    "short_description",
    "expanded_description",
    "aliases",
    "categories",
    "tasks",
    "use_when",
    "do_not_use_when",
    "inputs",
    "outputs",
    "examples",
    "related_skills",
    "risk_level",
    "permissions",
    "page_title",
    "meta_description",
]
SUMMARY_DISCOVERY_FIELDS = [
    "title",
    "short_description",
    "aliases",
    "categories",
    "tasks",
    "risk_level",
    "permissions",
    "homepage_path",
]
LIST_DISCOVERY_FIELDS = {
    "aliases",
    "categories",
    "tags",
    "tasks",
    "use_when",
    "do_not_use_when",
    "inputs",
    "outputs",
    "examples",
    "related_skills",
    "permissions",
}
GENERIC_SEARCH_TERMS = {
    "agent",
    "agents",
    "catalog",
    "catalogs",
    "find",
    "for",
    "help",
    "helping",
    "install",
    "marketplace",
    "skill",
    "skills",
    "task",
    "tasks",
    "use",
    "using",
    "workflow",
    "workflows",
}
PLACEHOLDER_PATTERN = re.compile(r"\{\{[^}\n]+\}\}")


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


def set_homepage_metadata(metadata: dict, skill_dir: Path) -> None:
    readme_path = skill_dir / "README.md"
    if readme_path.exists():
        try:
            metadata["homepage_path"] = rel(readme_path)
        except ValueError:
            metadata["homepage_path"] = str(readme_path)
    else:
        metadata.pop("homepage_path", None)


def read_repo_text(path_value: object, *, max_chars: int = 12000) -> str:
    path_text = as_text(path_value)
    if not path_text:
        return ""
    path = Path(path_text)
    if path.is_absolute():
        try:
            path.relative_to(REPO_ROOT)
        except ValueError:
            return ""
    else:
        path = REPO_ROOT / path
    if not path.exists() or not path.is_file():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:max_chars]
    except OSError:
        return ""


def has_homepage_substance(text: str) -> bool:
    lowered = text.lower()
    required_terms = [
        "repo",
        "parent package",
        "parent collection",
        "what this skill does",
        "why you would call it",
        "keywords",
        "search terms",
        "how it works",
        "api and options",
        "inputs and outputs",
        "examples",
        "help",
        "llm",
        "cli",
        "trust and safety",
        "feedback",
        "author",
        "citations",
        "related skills",
    ]
    return all(
        [
            re.search(r"^#\s+\S", text, flags=re.MULTILINE),
            all(term in lowered for term in required_terms),
        ]
    )


def slug_title(skill_id: str) -> str:
    return " ".join(part.capitalize() for part in skill_id.split("-"))


def as_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        if not value.strip():
            return []
        return [value.strip()]
    return [str(value).strip()]


def as_text(value: object) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        return "; ".join(as_list(value))
    if value is None:
        return ""
    return str(value).strip()


def source_catalog_from_metadata(metadata: dict) -> dict:
    source = metadata.get("source", {}) if isinstance(metadata.get("source"), dict) else {}
    if source.get("type") == "peer-catalog":
        peer_id = as_text(source.get("peer_id")) or as_text(source.get("repo")) or "peer-catalog"
        return {
            "id": peer_id,
            "name": peer_id,
            "type": "peer-import",
            "trust_notes": "Imported from a peer catalog. Review source provenance before trusting behavior.",
        }
    return {
        "id": "skillforge",
        "name": "SkillForge",
        "type": "local",
        "trust_notes": "Local SkillForge catalog entry.",
    }


def first_sentence(text: str) -> str:
    match = re.search(r"(.+?[.!?])(?:\s|$)", text.strip())
    return match.group(1).strip() if match else text.strip()


def normalize_tags(values: list[str]) -> list[str]:
    tags: list[str] = []
    for value in values:
        tag = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
        if tag:
            tags.append(tag)
    return sorted(set(tags))


def discovery_metadata_from_validation(validation: SkillValidation, *, fallback_tags: list[str] | None = None) -> dict:
    name = as_text(validation.metadata.get("name"))
    description = as_text(validation.metadata.get("description"))
    discovery: dict[str, object] = {
        "title": as_text(validation.metadata.get("title")) or slug_title(name),
        "short_description": as_text(validation.metadata.get("short_description")) or first_sentence(description),
    }
    expanded = as_text(validation.metadata.get("expanded_description"))
    if expanded:
        discovery["expanded_description"] = expanded

    for field_name in DISCOVERY_FIELDS:
        if field_name in {"title", "short_description", "expanded_description"}:
            continue
        raw_value = validation.metadata.get(field_name)
        if raw_value in (None, "", []):
            continue
        discovery[field_name] = as_list(raw_value) if field_name in LIST_DISCOVERY_FIELDS else as_text(raw_value)

    tags = as_list(validation.metadata.get("tags"))
    discovery["tags"] = normalize_tags(tags or fallback_tags or infer_tags(name, description))
    return discovery


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
    name = as_text(validation.metadata["name"])
    description = as_text(validation.metadata["description"])
    metadata_owner = as_text(validation.metadata.get("owner")) or owner
    catalog_path = Path("skills") / name
    source_path = source_path or skill_dir
    rel_source = source_path.resolve()
    try:
        source_path_value = rel_source.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        source_path_value = str(rel_source)

    fallback_tags = infer_tags(name, description)
    discovery = discovery_metadata_from_validation(validation, fallback_tags=fallback_tags)
    metadata = {
        "schema_version": "0.1",
        "id": name,
        "name": name,
        "description": description,
        "owner": metadata_owner,
        "tags": discovery.pop("tags", fallback_tags),
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
    metadata.update(discovery)
    set_homepage_metadata(metadata, skill_dir)
    return metadata


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
                meta_path = CATALOG_SKILLS_DIR / f"{as_text(validation.metadata['name'])}.json"
                if meta_path.exists():
                    metadata = json.loads(meta_path.read_text(encoding="utf-8"))
                    name = validation.metadata["name"]
                    description = as_text(validation.metadata["description"])
                    source = metadata.get("source", {})
                    old_checksum = metadata.get("checksum", {}).get("value")
                    new_checksum = skill_checksum(skill_dir)
                    discovery = discovery_metadata_from_validation(
                        validation,
                        fallback_tags=infer_tags(as_text(name), description),
                    )
                    for field_name in DISCOVERY_FIELDS:
                        if field_name in discovery:
                            metadata[field_name] = discovery[field_name]
                        else:
                            metadata.pop(field_name, None)
                    metadata["id"] = as_text(name)
                    metadata["name"] = as_text(name)
                    metadata["owner"] = (
                        as_text(validation.metadata.get("owner"))
                        or as_text(metadata.get("owner"))
                        or "unknown"
                    )
                    metadata["description"] = description
                    metadata["tags"] = discovery["tags"]
                    metadata["source"] = {
                        "type": as_text(source.get("type")) or "github-repo-path",
                        "path": rel(skill_dir),
                        "url": source.get("url"),
                    }
                    metadata["catalog_path"] = f"skills/{as_text(name)}"
                    if old_checksum != new_checksum:
                        metadata["updated_at"] = utc_now()
                    metadata["checksum"] = {
                        "algorithm": "sha256-tree",
                        "value": new_checksum,
                    }
                    metadata["files"] = skill_files(skill_dir)
                    metadata["warnings"] = validation.warnings
                    set_homepage_metadata(metadata, skill_dir)
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
    search_index = build_search_index(catalog)
    generate_static_catalog(catalog, search_index)
    return catalog


def summary_from_metadata(metadata: dict) -> dict:
    summary = {
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
    for field_name in SUMMARY_DISCOVERY_FIELDS:
        if field_name in metadata:
            summary[field_name] = metadata[field_name]
    return summary


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

    name = as_text(validation.metadata["name"])
    dest = SKILLS_DIR / name
    source_dir = validation.skill_dir.resolve()

    if dest.exists():
        if not force:
            raise FileExistsError(f"Skill already exists: {dest}. Use --force to replace it.")
        remove_tree(dest)

    dest.parent.mkdir(parents=True, exist_ok=True)
    copy_tree(source_dir, dest)
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


def search_terms(query: str) -> list[str]:
    return [
        term
        for term in re.findall(r"[a-z0-9]+", query.lower().replace("-", " "))
        if term and term not in GENERIC_SEARCH_TERMS
    ]


def search_text_from_metadata(metadata: dict) -> str:
    values: list[str] = []
    for field_name in [
        "id",
        "name",
        "title",
        "description",
        "short_description",
        "expanded_description",
        "risk_level",
        "page_title",
        "meta_description",
        "homepage_text",
    ]:
        values.append(as_text(metadata.get(field_name)))
    for field_name in [
        "aliases",
        "categories",
        "tags",
        "tasks",
        "use_when",
        "do_not_use_when",
        "inputs",
        "outputs",
        "examples",
        "related_skills",
        "permissions",
    ]:
        values.extend(as_list(metadata.get(field_name)))
    return " ".join(value for value in values if value).lower()


def search_document_from_metadata(metadata: dict) -> dict:
    doc = {
        "id": metadata["id"],
        "name": metadata["name"],
        "title": metadata.get("title", slug_title(metadata["id"])),
        "description": metadata["description"],
        "short_description": metadata.get("short_description", first_sentence(metadata["description"])),
        "expanded_description": metadata.get("expanded_description", metadata["description"]),
        "aliases": as_list(metadata.get("aliases")),
        "categories": as_list(metadata.get("categories")),
        "tags": as_list(metadata.get("tags")),
        "tasks": as_list(metadata.get("tasks")),
        "use_when": as_list(metadata.get("use_when")),
        "do_not_use_when": as_list(metadata.get("do_not_use_when")),
        "inputs": as_list(metadata.get("inputs")),
        "outputs": as_list(metadata.get("outputs")),
        "examples": as_list(metadata.get("examples")),
        "related_skills": as_list(metadata.get("related_skills")),
        "risk_level": metadata.get("risk_level"),
        "permissions": as_list(metadata.get("permissions")),
        "page_title": metadata.get("page_title"),
        "meta_description": metadata.get("meta_description"),
        "source": metadata["source"],
        "source_catalog": source_catalog_from_metadata(metadata),
        "owner": metadata["owner"],
        "catalog_path": metadata["catalog_path"],
        "updated_at": metadata["updated_at"],
        "checksum": metadata["checksum"],
        "codex": metadata["codex"],
        "warnings": metadata.get("warnings", []),
        "homepage_path": metadata.get("homepage_path"),
    }
    if doc.get("homepage_path"):
        doc["homepage_text"] = read_repo_text(doc["homepage_path"])
    doc["search_text"] = search_text_from_metadata(doc)
    return doc


def find_unresolved_placeholders(skill_dir: Path) -> list[dict]:
    placeholders: list[dict] = []
    for file_name in ["SKILL.md", "README.md"]:
        path = skill_dir / file_name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        matches = sorted(set(PLACEHOLDER_PATTERN.findall(text)))
        if matches:
            placeholders.append(
                {
                    "file": display_path(path),
                    "count": len(matches),
                    "placeholders": matches[:25],
                }
            )
    return placeholders


def build_search_index(catalog: dict | None = None) -> dict:
    catalog = catalog or read_catalog()
    docs: list[dict] = []
    for skill in catalog.get("skills", []):
        metadata = load_skill_metadata(skill["id"])
        docs.append(search_document_from_metadata(metadata))
    payload = {
        "schema_version": "0.1",
        "marketplace": "SkillForge",
        "generated_at": catalog.get("generated_at", utc_now()),
        "description": "Machine-readable search and SEO index for SkillForge skills.",
        "fields_indexed": [
            "name",
            "title",
            "description",
            "short_description",
            "expanded_description",
            "aliases",
            "categories",
            "tags",
            "tasks",
            "use_when",
            "do_not_use_when",
            "inputs",
            "outputs",
            "examples",
            "homepage_text",
        ],
        "skills": sorted(docs, key=lambda item: item["id"]),
    }
    write_json(SEARCH_INDEX_PATH, payload)
    return payload


def read_search_index() -> dict:
    if SEARCH_INDEX_PATH.exists():
        return json.loads(SEARCH_INDEX_PATH.read_text(encoding="utf-8"))
    return build_search_index(read_catalog())


def score_search_document(query: str, doc: dict) -> int:
    terms = search_terms(query)
    if not terms and query.strip():
        terms = re.findall(r"[a-z0-9]+", query.lower().replace("-", " "))
    if not terms:
        return 0

    score = 0
    query_lower = query.lower().strip()
    if query_lower == doc["id"].lower():
        score += 100
    if query_lower in [alias.lower() for alias in as_list(doc.get("aliases"))]:
        score += 80

    weighted_fields = [
        (["id", "name", "title"], 12),
        (["aliases", "tasks", "use_when"], 8),
        (["tags", "categories", "inputs", "outputs"], 5),
        (["description", "short_description", "expanded_description", "examples"], 3),
        (["search_text"], 1),
    ]
    for fields, weight in weighted_fields:
        haystack = " ".join(
            " ".join(as_list(doc.get(field))) if isinstance(doc.get(field), list) else as_text(doc.get(field))
            for field in fields
        ).lower()
        haystack_terms = set(re.findall(r"[a-z0-9]+", haystack.replace("-", " ")))
        for term in terms:
            if term in haystack_terms:
                score += weight
    return score



def rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def display_path(path: Path) -> str:
    try:
        return rel(path)
    except ValueError:
        return str(path)


def skill_seo_files(skill_id: str) -> list[str]:
    return [
        f"skills/{skill_id}/SKILL.md",
        f"skills/{skill_id}/README.md",
        "schemas/skill.schema.json",
        "schemas/skills.schema.json",
        f"catalog/skills/{skill_id}.json",
        "catalog/skills.json",
        "catalog/search-index.json",
        "plugins/agent-skills/skills/skill_list.md",
        "README.md",
        "docs/skill-search-seo-plan.md",
        f"site/skills/{skill_id}/index.html",
        "site/search-index.json",
        "site/llms.txt",
        "site/.well-known/agent-skills/index.json",
    ]


def search_audit_skill(skill_id: str) -> dict:
    metadata = load_skill_metadata(skill_id)
    checks: list[dict] = []
    recommendations: list[dict] = []

    def add_check(category: str, ok: bool, message: str, recommendation: str, files: list[str] | None = None) -> None:
        checks.append({"category": category, "ok": ok, "message": message})
        if not ok:
            recommendations.append(
                {
                    "category": category,
                    "recommendation": recommendation,
                    "files": files or skill_seo_files(skill_id),
                }
            )

    add_check(
        "human_clarity",
        bool(metadata.get("title") and metadata.get("short_description")),
        "Skill has a title and short description.",
        "Add `title` and `short_description` to SKILL.md frontmatter.",
    )
    add_check(
        "agent_triggerability",
        bool(as_list(metadata.get("use_when")) and as_list(metadata.get("tasks"))),
        "Skill has task phrases and use_when trigger guidance.",
        "Add `tasks` and `use_when` phrases that match how users ask for this workflow.",
    )
    add_check(
        "alias_coverage",
        len(as_list(metadata.get("aliases"))) >= 3,
        "Skill has at least three aliases or search phrases.",
        "Add common aliases, synonyms, product names, and plain-language search phrases.",
    )
    add_check(
        "example_quality",
        len(as_list(metadata.get("examples"))) >= 3,
        "Skill has at least three realistic prompt examples.",
        "Add beginner, task-specific, troubleshooting, and feedback prompt examples.",
    )
    add_check(
        "inputs_outputs",
        bool(as_list(metadata.get("inputs")) and as_list(metadata.get("outputs"))),
        "Skill lists expected inputs and outputs.",
        "Add `inputs` and `outputs` so humans and agents know what the skill consumes and produces.",
    )
    add_check(
        "exclusion_guidance",
        bool(as_list(metadata.get("do_not_use_when"))),
        "Skill says when not to use it.",
        "Add `do_not_use_when` guidance to reduce false-positive agent matches.",
    )
    add_check(
        "safety_permissions",
        bool(metadata.get("risk_level") and as_list(metadata.get("permissions"))),
        "Skill has risk level and permission notes.",
        "Add `risk_level` and `permissions` to support future trust and risk UX.",
    )
    add_check(
        "catalog_web_metadata",
        bool(metadata.get("page_title") and metadata.get("meta_description")),
        "Skill has web page title and meta description.",
        "Add `page_title` and `meta_description` for generated SEO pages.",
    )
    homepage_text = read_repo_text(metadata.get("homepage_path"))
    add_check(
        "skill_homepage",
        bool(metadata.get("homepage_path") and has_homepage_substance(homepage_text)),
        "Skill has a README home page with repo, package, purpose, examples, call patterns, feedback, author, and citation context.",
        "Add `skills/<skill-id>/README.md` as a real human-facing home page with skill name, repo URL, parent package, parent collection, purpose, keywords, search terms, method, API/options, inputs/outputs, examples, help, LLM and CLI calls, trust and safety, feedback URL, author, citations, and related skills.",
        [f"skills/{skill_id}/README.md"],
    )
    add_check(
        "source_provenance",
        bool(metadata.get("source") and metadata.get("checksum") and metadata.get("updated_at")),
        "Skill has source, checksum, and updated date.",
        "Regenerate catalog metadata with `python -m skillforge build-catalog`.",
        [f"catalog/skills/{skill_id}.json", "catalog/skills.json", "catalog/search-index.json"],
    )

    passed = sum(1 for check in checks if check["ok"])
    score = round((passed / len(checks)) * 100) if checks else 0
    return {
        "skill_id": skill_id,
        "score": score,
        "checks": checks,
        "recommendations": recommendations,
        "files": skill_seo_files(skill_id),
    }


def resolve_evaluation_target(target: str | Path) -> tuple[str, Path | None, SkillValidation | None]:
    target_path = Path(target)
    candidates = [target_path]
    if not target_path.is_absolute():
        candidates.append(REPO_ROOT / target_path)

    for candidate in candidates:
        if candidate.exists():
            validation = validate_skill(candidate)
            skill_id = as_text(validation.metadata.get("name"))
            return skill_id, validation.skill_dir, validation

    metadata = load_skill_metadata(str(target))
    canonical_dir = SKILLS_DIR / metadata["id"]
    if canonical_dir.exists():
        validation = validate_skill(canonical_dir)
        return metadata["id"], validation.skill_dir, validation
    source_path = as_text(metadata.get("source", {}).get("path"))
    if source_path:
        source_dir = Path(source_path)
        if not source_dir.is_absolute():
            source_dir = REPO_ROOT / source_dir
        if source_dir.exists():
            validation = validate_skill(source_dir)
            return metadata["id"], validation.skill_dir, validation
    return metadata["id"], None, None


def sample_search_queries(metadata: dict) -> list[str]:
    queries: list[str] = []

    def add(value: object) -> None:
        text = as_text(value)
        if text and text not in queries:
            queries.append(text)

    add(metadata.get("id"))
    add(metadata.get("title"))
    for value in as_list(metadata.get("aliases"))[:3]:
        add(value)
    for value in as_list(metadata.get("tasks"))[:3]:
        add(value)
    return queries[:8]


def evaluate_skill(target: str | Path) -> dict:
    skill_id, skill_dir, validation = resolve_evaluation_target(target)
    catalog_metadata_available = True
    try:
        metadata = load_skill_metadata(skill_id)
    except FileNotFoundError:
        catalog_metadata_available = False
        if validation is None or not validation.ok:
            metadata = {
                "id": skill_id or str(target),
                "name": skill_id or str(target),
                "description": "",
                "source": {"path": str(target)},
                "checksum": {},
            }
        else:
            metadata = metadata_from_validation(validation, owner="unknown", source_path=validation.skill_dir)
    checks: list[dict] = []

    def add_check(category: str, ok: bool, message: str, files: list[str] | None = None) -> None:
        checks.append(
            {
                "category": category,
                "ok": ok,
                "message": message,
                "files": files or [],
            }
        )

    if validation is None:
        add_check("structural_validation", False, "Skill source path was not found.", [metadata["source"].get("path", "")])
    else:
        add_check(
            "structural_validation",
            validation.ok,
            "Skill source passes structural validation." if validation.ok else "; ".join(validation.errors),
            [display_path(validation.skill_file) if validation.skill_file.exists() else str(validation.skill_file)],
        )

    placeholder_findings = find_unresolved_placeholders(skill_dir) if skill_dir and skill_dir.exists() else []
    add_check(
        "unresolved_placeholders",
        not placeholder_findings,
        "No unresolved template placeholders remain."
        if not placeholder_findings
        else "Skill source still contains template placeholders that must be replaced before publication.",
        [finding["file"] for finding in placeholder_findings],
    )

    if not catalog_metadata_available:
        add_check(
            "per_skill_catalog",
            False,
            "Per-skill catalog metadata is missing; run `python -m skillforge build-catalog`.",
            [f"catalog/skills/{skill_id}.json"],
        )
    else:
        add_check(
            "per_skill_catalog",
            True,
            "Per-skill catalog metadata exists.",
            [f"catalog/skills/{skill_id}.json"],
        )

    if catalog_metadata_available and skill_dir and skill_dir.exists():
        expected_checksum = metadata.get("checksum", {}).get("value")
        actual_checksum = skill_checksum(skill_dir)
        add_check(
            "catalog_checksum",
            expected_checksum == actual_checksum,
            "Catalog checksum matches the current skill source."
            if expected_checksum == actual_checksum
            else "Catalog checksum is stale; run `python -m skillforge build-catalog`.",
            [f"skills/{skill_id}/SKILL.md", f"catalog/skills/{skill_id}.json"],
        )
    else:
        add_check("catalog_checksum", False, "Cannot verify checksum without a local skill source.", [f"catalog/skills/{skill_id}.json"])

    if skill_dir and skill_dir.exists():
        readme_path = skill_dir / "README.md"
        readme_text = readme_path.read_text(encoding="utf-8", errors="ignore") if readme_path.exists() else ""
        add_check(
            "skill_homepage",
            readme_path.exists() and has_homepage_substance(readme_text),
            "Skill README home page exists and has the required publication sections."
            if readme_path.exists() and has_homepage_substance(readme_text)
            else "Skill README home page is missing or too thin.",
            [display_path(readme_path) if readme_path.exists() else f"skills/{skill_id}/README.md"],
        )
    else:
        add_check("skill_homepage", False, "Cannot verify README home page without a local skill source.", [f"skills/{skill_id}/README.md"])

    catalog = read_catalog()
    catalog_ids = {skill.get("id") for skill in catalog.get("skills", [])}
    add_check(
        "aggregate_catalog",
        skill_id in catalog_ids,
        "Aggregate catalog includes this skill." if skill_id in catalog_ids else "Aggregate catalog is missing this skill.",
        ["catalog/skills.json"],
    )

    search_index = read_search_index()
    index_docs = {skill.get("id"): skill for skill in search_index.get("skills", [])}
    add_check(
        "search_index",
        skill_id in index_docs,
        "Search index includes this skill." if skill_id in index_docs else "Search index is missing this skill.",
        ["catalog/search-index.json"],
    )

    page_path = SITE_DIR / "skills" / skill_id / "index.html"
    add_check(
        "static_skill_page",
        page_path.exists(),
        "Static skill page exists." if page_path.exists() else "Static skill page is missing.",
        [f"site/skills/{skill_id}/index.html"],
    )

    well_known_path = SITE_DIR / ".well-known" / "agent-skills" / "index.json"
    well_known_ok = False
    if well_known_path.exists():
        well_known = json.loads(well_known_path.read_text(encoding="utf-8"))
        well_known_ok = skill_id in {skill.get("id") for skill in well_known.get("skills", [])}
    add_check(
        "agent_index",
        well_known_ok,
        "Agent well-known index includes this skill." if well_known_ok else "Agent well-known index is missing this skill.",
        ["site/.well-known/agent-skills/index.json"],
    )

    search_audit = (
        search_audit_skill(skill_id)
        if catalog_metadata_available
        else {
            "skill_id": skill_id,
            "score": 0,
            "checks": [],
            "recommendations": [
                {
                    "category": "catalog_metadata",
                    "recommendation": "Run `python -m skillforge build-catalog` before search-audit.",
                    "files": [f"catalog/skills/{skill_id}.json", "catalog/skills.json"],
                }
            ],
            "files": skill_seo_files(skill_id),
        }
    )
    add_check(
        "search_audit",
        search_audit["score"] == 100,
        f"Search/SEO audit score is {search_audit['score']}/100.",
        search_audit["files"],
    )

    search_checks: list[dict] = []
    for query in sample_search_queries(metadata):
        results = search_catalog(query, limit=5)
        ids = [item["id"] for item in results]
        found = skill_id in ids
        search_checks.append(
            {
                "query": query,
                "ok": found,
                "rank": ids.index(skill_id) + 1 if found else None,
                "results": ids,
            }
        )
    add_check(
        "sample_searches",
        bool(search_checks) and all(check["ok"] for check in search_checks),
        "Sample search queries find this skill." if search_checks and all(check["ok"] for check in search_checks) else "One or more sample searches did not find this skill.",
        ["catalog/search-index.json"],
    )

    passed = sum(1 for check in checks if check["ok"])
    score = round((passed / len(checks)) * 100) if checks else 0
    return {
        "target": str(target),
        "skill_id": skill_id,
        "ok": all(check["ok"] for check in checks),
        "score": score,
        "checks": checks,
        "validation": None
        if validation is None
        else {
            "ok": validation.ok,
            "skill_dir": str(validation.skill_dir),
            "errors": validation.errors,
            "warnings": validation.warnings,
        },
        "search_audit": search_audit,
        "sample_searches": search_checks,
        "unresolved_placeholders": placeholder_findings,
        "files": skill_seo_files(skill_id),
    }


def e(value: object) -> str:
    return html.escape(as_text(value), quote=True)


def html_list(values: list[str]) -> str:
    if not values:
        return "<p>Not specified.</p>"
    return "<ul>" + "".join(f"<li>{html.escape(value)}</li>" for value in values) + "</ul>"


def render_skill_page(skill: dict) -> str:
    title = e(skill.get("page_title") or f"{skill.get('title', skill['name'])} Skill - SkillForge")
    meta = e(skill.get("meta_description") or skill.get("short_description") or skill["description"])
    json_ld = {
        "@context": "https://schema.org",
        "@type": "CreativeWork",
        "name": skill.get("title", skill["name"]),
        "description": skill.get("short_description", skill["description"]),
        "keywords": skill.get("tags", []) + skill.get("aliases", []),
        "isPartOf": {"@type": "SoftwareApplication", "name": "SkillForge"},
    }
    json_ld_text = json.dumps(json_ld, sort_keys=True).replace("</", "<\\/")
    homepage_path = as_text(skill.get("homepage_path"))
    homepage_html = (
        f'<p><a href="https://github.com/medatasci/agent_skills/blob/main/{e(homepage_path)}">Skill README home page</a></p>'
        if homepage_path
        else "<p>No source README home page is listed.</p>"
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{meta}">
  <script type="application/ld+json">{json_ld_text}</script>
  <style>
    body {{ font-family: system-ui, sans-serif; line-height: 1.55; max-width: 920px; margin: 0 auto; padding: 32px; }}
    code {{ background: #f3f4f6; padding: 0.1rem 0.25rem; border-radius: 4px; }}
    pre {{ background: #f3f4f6; padding: 1rem; overflow: auto; }}
    section {{ border-top: 1px solid #ddd; margin-top: 1.5rem; padding-top: 1rem; }}
  </style>
</head>
<body>
  <p><a href="../../index.html">SkillForge</a></p>
  <h1>{e(skill.get("title") or skill["name"])}</h1>
  <p>{e(skill.get("short_description") or skill["description"])}</p>
  <section><h2>Use This When</h2>{html_list(skill.get("use_when", []))}</section>
  <section><h2>Do Not Use This When</h2>{html_list(skill.get("do_not_use_when", []))}</section>
  <section><h2>Example Prompts</h2>{html_list(skill.get("examples", []))}</section>
  <section><h2>Install</h2><pre><code>{e(skill["codex"]["global_install_command"])}</code></pre></section>
  <section><h2>Inputs</h2>{html_list(skill.get("inputs", []))}</section>
  <section><h2>Outputs</h2>{html_list(skill.get("outputs", []))}</section>
  <section><h2>Trust And Safety</h2><p>Risk level: <strong>{e(skill.get("risk_level") or "Not specified")}</strong></p>{html_list(skill.get("permissions", []))}</section>
  <section><h2>Source</h2><p>{e(skill["source"].get("repo") or skill["source"].get("path") or skill["source"].get("url"))}</p><p>Updated: {e(skill.get("updated_at"))}</p></section>
  <section><h2>Related Skills</h2>{html_list(skill.get("related_skills", []))}</section>
  <section><h2>Home Page</h2>{homepage_html}</section>
  <section><h2>Feedback</h2><p><a href="https://github.com/medatasci/agent_skills/issues/new/choose">Send feedback on this skill</a>.</p></section>
</body>
</html>
"""


def render_site_index(search_index: dict) -> str:
    embedded_skills = [
        {key: value for key, value in skill.items() if key not in {"homepage_text", "search_text"}}
        for skill in search_index.get("skills", [])
    ]
    skills_json = json.dumps(embedded_skills, sort_keys=True).replace("</", "<\\/")
    generated_at = e(search_index.get("generated_at"))
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SkillForge Skill Catalog</title>
  <meta name="description" content="SkillForge catalog of reusable Codex skills for human and agent workflows.">
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f8f5;
      --surface: #ffffff;
      --ink: #17211d;
      --muted: #5b6863;
      --line: #d9ded8;
      --accent: #0f766e;
      --accent-dark: #0a4f49;
      --soft: #edf4f1;
      --warn: #8a5a00;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.5;
    }}
    a {{ color: var(--accent-dark); }}
    .shell {{
      width: min(1180px, calc(100% - 32px));
      margin: 0 auto;
      padding: 32px 0 56px;
    }}
    header {{
      display: grid;
      gap: 12px;
      padding: 18px 0 22px;
      border-bottom: 1px solid var(--line);
    }}
    h1 {{
      margin: 0;
      max-width: 860px;
      font-size: clamp(2rem, 5vw, 4.25rem);
      line-height: 0.98;
      font-weight: 760;
    }}
    .intro {{
      margin: 0;
      max-width: 720px;
      color: var(--muted);
      font-size: 1.05rem;
    }}
    .meta-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      color: var(--muted);
      font-size: 0.9rem;
    }}
    .controls {{
      display: grid;
      grid-template-columns: minmax(260px, 2fr) repeat(4, minmax(150px, 1fr));
      gap: 10px;
      align-items: end;
      padding: 18px 0;
    }}
    label {{
      display: grid;
      gap: 6px;
      color: var(--muted);
      font-size: 0.78rem;
      font-weight: 700;
      text-transform: uppercase;
    }}
    input,
    select {{
      width: 100%;
      min-height: 44px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--surface);
      color: var(--ink);
      font: inherit;
      padding: 0 12px;
    }}
    input:focus,
    select:focus {{
      outline: 3px solid rgba(15, 118, 110, 0.18);
      border-color: var(--accent);
    }}
    .result-summary {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
      margin: 4px 0 14px;
      color: var(--muted);
      font-size: 0.95rem;
    }}
    .result-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(min(100%, 330px), 1fr));
      gap: 14px;
    }}
    .result-card {{
      display: grid;
      gap: 12px;
      min-height: 100%;
      padding: 18px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--surface);
    }}
    .result-card h2 {{
      margin: 0;
      font-size: 1.2rem;
      line-height: 1.2;
    }}
    .description {{
      margin: 0;
      color: var(--muted);
    }}
    .chip-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }}
    .chip {{
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      padding: 2px 8px;
      border-radius: 999px;
      background: var(--soft);
      color: var(--accent-dark);
      font-size: 0.78rem;
      font-weight: 650;
    }}
    .risk {{
      color: var(--warn);
      background: #fff6df;
    }}
    .install {{
      margin: 0;
      overflow-x: auto;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #f3f5f2;
      padding: 10px;
      font-size: 0.82rem;
    }}
    .links {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      font-size: 0.92rem;
    }}
    .empty {{
      display: none;
      padding: 22px;
      border: 1px dashed var(--line);
      border-radius: 8px;
      background: var(--surface);
      color: var(--muted);
    }}
    .empty.visible {{ display: block; }}
    @media (max-width: 920px) {{
      .controls {{ grid-template-columns: 1fr 1fr; }}
      .controls label:first-child {{ grid-column: 1 / -1; }}
    }}
    @media (max-width: 620px) {{
      .shell {{ width: min(100% - 20px, 1180px); padding-top: 18px; }}
      .controls {{ grid-template-columns: 1fr; }}
      .result-summary {{ align-items: flex-start; flex-direction: column; }}
    }}
  </style>
</head>
<body>
  <main class="shell">
    <header>
      <h1>SkillForge Skill Catalog</h1>
      <p class="intro">Reusable Codex workflows for people who do not want to reinvent the wheel. Search by task, topic, name, category, risk level, or source catalog.</p>
      <div class="meta-row">
        <span>Generated {generated_at}</span>
        <span><a href="search-index.json">search-index.json</a></span>
        <span><a href="llms.txt">llms.txt</a></span>
        <span><a href=".well-known/agent-skills/index.json">agent index</a></span>
      </div>
    </header>

    <section class="controls" aria-label="Catalog filters">
      <label for="skill-search">Search
        <input id="skill-search" type="search" placeholder="hugging face, retrospective, YouTube transcripts">
      </label>
      <label for="category-filter">Category
        <select id="category-filter"><option value="">All categories</option></select>
      </label>
      <label for="tag-filter">Tag
        <select id="tag-filter"><option value="">All tags</option></select>
      </label>
      <label for="risk-filter">Risk
        <select id="risk-filter"><option value="">All risk levels</option></select>
      </label>
      <label for="source-filter">Source
        <select id="source-filter"><option value="">All sources</option></select>
      </label>
    </section>

    <div class="result-summary" aria-live="polite">
      <span id="result-count"></span>
      <span>Peer results must show their source catalog before install.</span>
    </div>

    <section id="results" class="result-grid" aria-label="Skill results"></section>
    <section id="empty-state" class="empty">
      No matching local skills yet. Try broader terms, search peer catalogs with <code>python -m skillforge peer-search "&lt;task&gt;" --json</code>, or send feedback requesting the missing workflow.
    </section>
  </main>

  <script id="embedded-index" type="application/json">{skills_json}</script>
  <script>
    const embeddedSkills = JSON.parse(document.getElementById("embedded-index").textContent);
    let skills = embeddedSkills;
    const controls = {{
      search: document.getElementById("skill-search"),
      category: document.getElementById("category-filter"),
      tag: document.getElementById("tag-filter"),
      risk: document.getElementById("risk-filter"),
      source: document.getElementById("source-filter"),
      results: document.getElementById("results"),
      count: document.getElementById("result-count"),
      empty: document.getElementById("empty-state"),
    }};

    function escapeHtml(value) {{
      return String(value ?? "").replace(/[&<>"']/g, (char) => ({{
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      }}[char]));
    }}

    function values(field) {{
      return [...new Set(skills.flatMap((skill) => Array.isArray(skill[field]) ? skill[field] : []))]
        .filter(Boolean)
        .sort((a, b) => a.localeCompare(b));
    }}

    function sourceCatalog(skill) {{
      const catalog = skill.source_catalog || {{}};
      return {{
        id: catalog.id || "skillforge",
        name: catalog.name || catalog.id || "SkillForge",
        type: catalog.type || "local",
      }};
    }}

    function fillSelect(select, items, label) {{
      select.innerHTML = `<option value="">${{label}}</option>` + items
        .map((item) => `<option value="${{escapeHtml(item)}}">${{escapeHtml(item)}}</option>`)
        .join("");
    }}

    function hydrateFilters() {{
      fillSelect(controls.category, values("categories"), "All categories");
      fillSelect(controls.tag, values("tags"), "All tags");
      fillSelect(controls.risk, [...new Set(skills.map((skill) => skill.risk_level).filter(Boolean))].sort(), "All risk levels");
      fillSelect(controls.source, [...new Set(skills.map((skill) => sourceCatalog(skill).id))].sort(), "All sources");
    }}

    function searchableText(skill) {{
      return [
        skill.id,
        skill.name,
        skill.title,
        skill.description,
        skill.short_description,
        skill.expanded_description,
        skill.search_text,
        ...(skill.aliases || []),
        ...(skill.categories || []),
        ...(skill.tags || []),
        ...(skill.tasks || []),
        ...(skill.use_when || []),
        ...(skill.examples || []),
      ].filter(Boolean).join(" ").toLowerCase();
    }}

    function matches(skill) {{
      const query = controls.search.value.trim().toLowerCase();
      const terms = query ? query.split(/\\s+/).filter(Boolean) : [];
      const text = searchableText(skill);
      const catalog = sourceCatalog(skill);
      return (
        terms.every((term) => text.includes(term)) &&
        (!controls.category.value || (skill.categories || []).includes(controls.category.value)) &&
        (!controls.tag.value || (skill.tags || []).includes(controls.tag.value)) &&
        (!controls.risk.value || skill.risk_level === controls.risk.value) &&
        (!controls.source.value || catalog.id === controls.source.value)
      );
    }}

    function repoUrl(skill, fileName) {{
      const sourcePath = String((skill.source && skill.source.path) || `skills/${{skill.id}}`).replace(/\\/$/, "");
      if (sourcePath.startsWith("http")) return sourcePath;
      const filePath = sourcePath.endsWith(fileName) ? sourcePath : `${{sourcePath}}/${{fileName}}`;
      return `https://github.com/medatasci/agent_skills/blob/main/${{filePath}}`;
    }}

    function chips(items, extraClass = "") {{
      return (items || []).slice(0, 8).map((item) => `<span class="chip ${{extraClass}}">${{escapeHtml(item)}}</span>`).join("");
    }}

    function renderCard(skill) {{
      const catalog = sourceCatalog(skill);
      const title = skill.title || skill.name || skill.id;
      const description = skill.short_description || skill.description || "No description provided.";
      const install = (skill.codex && skill.codex.global_install_command) || `python -m skillforge install ${{skill.id}} --scope global`;
      return `
        <article class="result-card">
          <div>
            <h2><a href="skills/${{escapeHtml(skill.id)}}/index.html">${{escapeHtml(title)}}</a></h2>
            <p class="description">${{escapeHtml(description)}}</p>
          </div>
          <div class="chip-row">
            <span class="chip">${{escapeHtml(catalog.name)}}</span>
            ${{skill.risk_level ? `<span class="chip risk">Risk: ${{escapeHtml(skill.risk_level)}}</span>` : ""}}
            ${{chips(skill.categories)}}
            ${{chips(skill.tags)}}
          </div>
          <pre class="install"><code>${{escapeHtml(install)}}</code></pre>
          <nav class="links" aria-label="${{escapeHtml(skill.id)}} links">
            <a href="skills/${{escapeHtml(skill.id)}}/index.html">Detail page</a>
            <a href="${{escapeHtml(repoUrl(skill, "SKILL.md"))}}">SKILL.md</a>
            <a href="${{escapeHtml(repoUrl(skill, "README.md"))}}">README.md</a>
          </nav>
        </article>
      `;
    }}

    function render() {{
      const filtered = skills.filter(matches);
      controls.count.textContent = `${{filtered.length}} of ${{skills.length}} skills shown`;
      controls.results.innerHTML = filtered.map(renderCard).join("");
      controls.empty.classList.toggle("visible", filtered.length === 0);
    }}

    async function loadIndex() {{
      try {{
        const response = await fetch("search-index.json", {{ cache: "no-cache" }});
        if (response.ok) {{
          const payload = await response.json();
          if (Array.isArray(payload.skills)) skills = payload.skills;
        }}
      }} catch (error) {{
        skills = embeddedSkills;
      }}
      hydrateFilters();
      render();
    }}

    Object.values(controls).forEach((element) => {{
      if (element && ["INPUT", "SELECT"].includes(element.tagName)) {{
        element.addEventListener("input", render);
        element.addEventListener("change", render);
      }}
    }});
    loadIndex();
  </script>
</body>
</html>
"""


def render_category_page(category: str, skills: list[dict]) -> str:
    items = "\n".join(
        f'<li><a href="../../skills/{e(skill["id"])}/index.html">{e(skill.get("title") or skill["name"])}</a> - {e(skill.get("short_description") or skill["description"])}</li>'
        for skill in skills
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(category)} SkillForge Skills</title>
  <meta name="description" content="SkillForge skills in the {e(category)} category.">
</head>
<body>
  <p><a href="../../index.html">SkillForge</a></p>
  <h1>{e(category)} Skills</h1>
  <ul>{items}</ul>
</body>
</html>
"""


def generate_static_catalog(catalog: dict, search_index: dict) -> None:
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    (SITE_DIR / "index.html").write_text(render_site_index(search_index), encoding="utf-8")
    write_json(SITE_DIR / "search-index.json", search_index)

    well_known = {
        "schema_version": "0.1",
        "marketplace": "SkillForge",
        "generated_at": catalog.get("generated_at", utc_now()),
        "catalog": "search-index.json",
        "skills": [
            {
                "id": skill["id"],
                "name": skill["name"],
                "title": skill.get("title"),
                "url": f"skills/{skill['id']}/index.html",
                "install": skill["codex"]["global_install_command"],
            }
            for skill in search_index.get("skills", [])
        ],
    }
    write_json(SITE_DIR / ".well-known" / "agent-skills" / "index.json", well_known)

    llms_lines = [
        "# SkillForge",
        "",
        "SkillForge is a catalog of reusable Codex skills.",
        "",
        "## Skills",
    ]
    for skill in search_index.get("skills", []):
        llms_lines.append(f"- [{skill.get('title') or skill['name']}](skills/{skill['id']}/index.html): {skill.get('short_description') or skill['description']}")
    (SITE_DIR / "llms.txt").write_text("\n".join(llms_lines) + "\n", encoding="utf-8")

    categories: dict[str, list[dict]] = {}
    for skill in search_index.get("skills", []):
        for category in skill.get("categories", []) or ["Uncategorized"]:
            categories.setdefault(category, []).append(skill)
        page_path = SITE_DIR / "skills" / skill["id"] / "index.html"
        page_path.parent.mkdir(parents=True, exist_ok=True)
        page_path.write_text(render_skill_page(skill), encoding="utf-8")

    for category, skills in sorted(categories.items()):
        category_slug = re.sub(r"[^a-z0-9]+", "-", category.lower()).strip("-") or "uncategorized"
        page_path = SITE_DIR / "categories" / category_slug / "index.html"
        page_path.parent.mkdir(parents=True, exist_ok=True)
        page_path.write_text(render_category_page(category, sorted(skills, key=lambda item: item["id"])), encoding="utf-8")


def search_catalog(query: str, *, limit: int = 10) -> list[dict]:
    index = read_search_index()
    results: list[tuple[int, dict]] = []
    for doc in index.get("skills", []):
        score = score_search_document(query, doc)
        if score >= 2:
            item = {key: value for key, value in doc.items() if key != "search_text"}
            item.pop("homepage_text", None)
            item["score"] = score
            results.append((score, item))
    results.sort(key=lambda pair: (-pair[0], pair[1]["id"]))
    return [item for _, item in results[:limit]]
