from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re


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
SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]


@dataclass
class SkillValidation:
    skill_dir: Path
    skill_file: Path
    metadata: dict[str, str] = field(default_factory=dict)
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


def parse_frontmatter(text: str) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    metadata: dict[str, str] = {}
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

        if value in {"|", ">"}:
            block: list[str] = []
            index += 1
            while index < len(fm_lines):
                continuation = fm_lines[index]
                if continuation and not continuation.startswith((" ", "\t")):
                    break
                block.append(continuation.strip())
                index += 1
            metadata[key] = "\n".join(line for line in block if line)
            continue

        metadata[key] = value.strip("\"'")
        index += 1

    return metadata, errors


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

    name = metadata.get("name", "")
    description = metadata.get("description", "")
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

    for file_path in iter_skill_files(skill_dir):
        suffix = file_path.suffix.lower()
        rel = file_path.relative_to(skill_dir).as_posix()
        if suffix in SUSPICIOUS_SUFFIXES:
            result.warnings.append(f"Suspicious executable or binary-like file: {rel}")
        if suffix in ARCHIVE_SUFFIXES:
            result.warnings.append(f"Archive file should be reviewed before publishing: {rel}")
        if file_path.stat().st_size > 5_000_000:
            result.warnings.append(f"Large file should be reviewed before publishing: {rel}")
        if suffix in {".md", ".txt", ".json", ".yaml", ".yml", ".py", ".js", ".ts"}:
            scan_text_file(file_path, rel, result)

    return result


def iter_skill_files(skill_dir: Path) -> list[Path]:
    files = [path for path in skill_dir.rglob("*") if path.is_file()]
    return sorted(files, key=lambda path: path.relative_to(skill_dir).as_posix())


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
