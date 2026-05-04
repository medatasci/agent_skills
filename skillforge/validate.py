from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from .filesystem import is_transient_path


NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SUSPICIOUS_SUFFIXES = {
    ".bat",
    ".cmd",
    ".dll",
    ".dylib",
    ".exe",
    ".msi",
    ".ps1",
    ".scr",
    ".sh",
    ".so",
}
ARCHIVE_SUFFIXES = {".7z", ".gz", ".rar", ".tar", ".tgz", ".zip"}
TEXT_FILE_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml", ".py", ".js", ".ts"}
SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]
RECOMMENDED_DISCOVERY_FIELDS = [
    "title",
    "short_description",
    "aliases",
    "categories",
    "tags",
    "tasks",
    "use_when",
    "do_not_use_when",
    "inputs",
    "outputs",
    "examples",
]
MARKDOWN_DISCOVERY_LABELS = {
    "title": "title",
    "short description": "short_description",
    "aliases": "aliases",
    "categories": "categories",
    "tags": "tags",
    "tasks": "tasks",
    "use when": "use_when",
    "do not use when": "do_not_use_when",
    "inputs": "inputs",
    "outputs": "outputs",
    "examples": "examples",
}
MARKDOWN_LIST_FIELDS = {
    "aliases",
    "categories",
    "tags",
    "tasks",
    "use_when",
    "do_not_use_when",
    "inputs",
    "outputs",
    "examples",
}
REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO_ROOT / "skills"
GUARDED_EXECUTION_MARKERS = ("--confirm-execution", "confirm_execution")
RUNTIME_PLAN_PATH_HINTS = (
    "requirements-and-development-plan",
    "runtime-and-deployment-plan",
    "runtime-plan",
    "deployment-plan",
    "readiness-card",
)
RUNTIME_PLAN_CHECKS = {
    "install location": ("install location", "source checkout", "runtime path", "checkout lives"),
    "OS/runtime target": ("os/runtime", "runtime target", "wsl2", "linux", "windows", "macos", "operating system"),
    "dependency setup": ("dependency", "dependencies", "requirements.txt", "conda", "pip"),
    "model/data download policy": ("model weights", "download", "dataset", "data policy"),
    "license review": ("license", "model terms", "terms"),
    "environment checks": ("environment check", "readiness", "check command", "cuda", "docker"),
    "smoke-test data": ("smoke-test", "smoke test", "test data"),
    "rollback/cleanup notes": ("rollback", "cleanup", "clean up", "temporary files"),
}


@dataclass
class SkillValidation:
    skill_dir: Path
    skill_file: Path
    metadata: dict[str, object] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def resolve_skill_dir(path: Path) -> Path:
    path = path.resolve()
    if path.is_file() and path.name == "SKILL.md":
        return path.parent
    return path


def parse_scalar(value: str) -> object:
    value = value.strip()
    if not value:
        return ""
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [item.strip().strip("\"'") for item in inner.split(",") if item.strip()]
    return value.strip("\"'")


def is_block_scalar(value: str) -> bool:
    return bool(re.fullmatch(r"[>|][+-]?", value.strip()))


def parse_block_scalar(value: str, lines: list[str]) -> str:
    content = [line.strip() for line in lines]
    if value.startswith("|"):
        return "\n".join(line for line in content if line)
    return " ".join(line for line in content if line)


def parse_frontmatter(text: str) -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    metadata: dict[str, object] = {}
    lines = text.splitlines()

    if not lines or lines[0].strip() != "---":
        return metadata, ["SKILL.md must start with YAML frontmatter delimiter ---"]

    end_index = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = index
            break

    if end_index is None:
        return metadata, ["SKILL.md frontmatter must end with delimiter ---"]

    fm_lines = lines[1:end_index]
    index = 0
    while index < len(fm_lines):
        raw = fm_lines[index]
        if not raw.strip() or raw.lstrip().startswith("#"):
            index += 1
            continue
        if ":" not in raw:
            errors.append(f"Invalid frontmatter line: {raw}")
            index += 1
            continue

        key, value = raw.split(":", 1)
        key = key.strip()
        value = value.strip()

        if is_block_scalar(value):
            block: list[str] = []
            index += 1
            while index < len(fm_lines):
                continuation = fm_lines[index]
                if continuation and not continuation.startswith((" ", "\t")):
                    break
                block.append(continuation.strip())
                index += 1
            metadata[key] = parse_block_scalar(value, block)
            continue

        if not value:
            items: list[str] = []
            nested: dict[str, object] = {}
            index += 1
            while index < len(fm_lines):
                continuation = fm_lines[index]
                stripped = continuation.strip()
                if continuation and not continuation.startswith((" ", "\t")):
                    break
                if stripped.startswith("- "):
                    items.append(stripped[2:].strip().strip("\"'"))
                elif ":" in stripped:
                    nested_key, nested_value = stripped.split(":", 1)
                    nested[nested_key.strip()] = parse_scalar(nested_value)
                elif stripped:
                    errors.append(f"Unsupported nested frontmatter line for {key}: {continuation}")
                index += 1
            metadata[key] = nested if nested and not items else items
            continue

        metadata[key] = parse_scalar(value)
        index += 1

    return metadata, errors


def normalize_markdown_heading(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def body_after_frontmatter(text: str) -> str:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return text
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[index + 1 :])
    return text


def markdown_discovery_metadata(text: str) -> dict[str, object]:
    body = body_after_frontmatter(text)
    in_discovery = False
    current_field: str | None = None
    sections: dict[str, list[str]] = {}
    for line in body.splitlines():
        if line.startswith("## "):
            in_discovery = normalize_markdown_heading(line[3:]) == "skillforge discovery metadata"
            current_field = None
            continue
        if not in_discovery:
            continue
        if line.startswith("### "):
            current_field = MARKDOWN_DISCOVERY_LABELS.get(normalize_markdown_heading(line[4:]))
            if current_field:
                sections.setdefault(current_field, [])
            continue
        if current_field:
            sections[current_field].append(line)

    metadata: dict[str, object] = {}
    for field_name, lines in sections.items():
        if field_name in MARKDOWN_LIST_FIELDS:
            values = [line.strip()[2:].strip() for line in lines if line.strip().startswith("- ")]
            if values:
                metadata[field_name] = values
        else:
            value = " ".join(line.strip() for line in lines if line.strip() and not line.strip().startswith("- "))
            if value:
                metadata[field_name] = value
    return metadata


def metadata_text(metadata: dict[str, object], key: str) -> str:
    value = metadata.get(key, "")
    return value if isinstance(value, str) else ""


def is_skillforge_owned_skill(skill_dir: Path) -> bool:
    try:
        skill_dir.resolve().relative_to(SKILLS_ROOT.resolve())
        return True
    except ValueError:
        return False


def validate_skill(path: str | Path) -> SkillValidation:
    skill_dir = resolve_skill_dir(Path(path))
    skill_file = skill_dir / "SKILL.md"
    result = SkillValidation(skill_dir=skill_dir, skill_file=skill_file)

    if not skill_dir.exists():
        result.errors.append(f"Skill directory does not exist: {skill_dir}")
        return result
    if not skill_dir.is_dir():
        result.errors.append(f"Skill path is not a directory: {skill_dir}")
        return result
    if not skill_file.exists():
        result.errors.append(f"Missing SKILL.md: {skill_file}")
        return result

    try:
        text = skill_file.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        result.errors.append("SKILL.md must be UTF-8 text")
        return result

    metadata, parse_errors = parse_frontmatter(text)
    result.metadata = metadata
    result.errors.extend(parse_errors)

    name = metadata_text(metadata, "name")
    description = metadata_text(metadata, "description")
    if not name:
        result.errors.append("Frontmatter must include name")
    elif not NAME_PATTERN.match(name):
        result.errors.append("Skill name must be lowercase kebab-case letters, digits, and hyphens")
    elif skill_dir.name != name:
        result.warnings.append(f"Folder name '{skill_dir.name}' does not match skill name '{name}'")

    if not description:
        result.errors.append("Frontmatter must include description")
    elif len(description) > 1024:
        result.warnings.append("Description is longer than 1024 characters")

    if result.ok and is_skillforge_owned_skill(skill_dir):
        discovery_metadata = {**markdown_discovery_metadata(text), **metadata}
        for field_name in RECOMMENDED_DISCOVERY_FIELDS:
            value = discovery_metadata.get(field_name)
            if value in (None, "", []):
                result.warnings.append(f"Recommended discovery field missing: {field_name}")

    skill_files = iter_skill_files(skill_dir)
    for file_path in skill_files:
        suffix = file_path.suffix.lower()
        rel = file_path.relative_to(skill_dir).as_posix()
        if suffix in SUSPICIOUS_SUFFIXES:
            result.warnings.append(f"Suspicious executable or binary-like file: {rel}")
        if suffix in ARCHIVE_SUFFIXES:
            result.warnings.append(f"Archive file should be reviewed before publishing: {rel}")
        if file_path.stat().st_size > 5_000_000:
            result.warnings.append(f"Large file should be reviewed before publishing: {rel}")
        if suffix in TEXT_FILE_SUFFIXES:
            scan_text_file(file_path, rel, result)

    validate_runtime_deployment_plan(skill_dir, skill_files, result)

    return result


def iter_skill_files(skill_dir: Path) -> list[Path]:
    files = [
        path
        for path in skill_dir.rglob("*")
        if path.is_file() and not is_transient_path(path, skill_dir)
    ]
    return sorted(files, key=lambda path: path.relative_to(skill_dir).as_posix())


def read_text_corpus(skill_dir: Path, files: list[Path]) -> dict[str, str]:
    corpus: dict[str, str] = {}
    for file_path in files:
        if file_path.suffix.lower() not in TEXT_FILE_SUFFIXES:
            continue
        rel = file_path.relative_to(skill_dir).as_posix()
        try:
            corpus[rel] = file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
    return corpus


def has_guarded_execution_surface(corpus: dict[str, str]) -> bool:
    lowered = "\n".join(corpus.values()).lower()
    return any(marker in lowered for marker in GUARDED_EXECUTION_MARKERS)


def runtime_plan_candidate_text(corpus: dict[str, str]) -> str:
    candidates: list[str] = []
    for rel, text in corpus.items():
        normalized_rel = rel.lower()
        if any(hint in normalized_rel for hint in RUNTIME_PLAN_PATH_HINTS):
            candidates.append(text)
            continue
        if normalized_rel in {"skill.md", "readme.md"}:
            lowered = text.lower()
            if "runtime" in lowered and "deployment" in lowered:
                candidates.append(text)
    return "\n".join(candidates)


def missing_runtime_plan_topics(plan_text: str) -> list[str]:
    lowered = plan_text.lower()
    missing: list[str] = []
    for label, terms in RUNTIME_PLAN_CHECKS.items():
        if not any(term in lowered for term in terms):
            missing.append(label)
    return missing


def validate_runtime_deployment_plan(skill_dir: Path, files: list[Path], result: SkillValidation) -> None:
    if not is_skillforge_owned_skill(skill_dir):
        return

    corpus = read_text_corpus(skill_dir, files)
    if not has_guarded_execution_surface(corpus):
        return

    plan_text = runtime_plan_candidate_text(corpus)
    if not plan_text.strip():
        result.warnings.append(
            "Code-backed guarded execution skill is missing runtime/deployment plan documentation: "
            "document install location, OS/runtime target, dependency setup, model/data download policy, "
            "license review, environment checks, smoke-test data, and rollback/cleanup notes."
        )
        return

    missing = missing_runtime_plan_topics(plan_text)
    if missing:
        result.warnings.append(
            "Code-backed guarded execution skill runtime/deployment plan is missing: "
            + ", ".join(missing)
        )


def scan_text_file(file_path: Path, rel: str, result: SkillValidation) -> None:
    try:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
    except OSError as exc:
        result.warnings.append(f"Could not read {rel}: {exc}")
        return

    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            result.warnings.append(f"Possible secret-like text in {rel}")
            break

    lowered = text.lower()
    if any(term in lowered for term in ["rm -rf", "remove-item -recurse", "delete all", "exfiltrat"]):
        result.warnings.append(f"Potentially destructive or exfiltration-like instruction in {rel}")
    if any(term in lowered for term in ["http://", "https://"]):
        result.warnings.append(f"External URL reference found in {rel}")
