from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys


EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".skillforge",
    ".test-tmp",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "site-packages",
    "test-output",
    "venv",
}


CATEGORY_GUIDANCE = {
    "readme_quickstart": {
        "label": "README and quick starts",
        "provides": "Intended use, setup path, example commands, supported workflows, advertised limits, and public language.",
        "skill_design_impact": "Use to define the top-level skill purpose, examples, user-facing claims, and scope boundaries.",
        "adapter_impact": "Use quick-start commands as candidates for check, plan, run, or setup-plan adapters.",
        "llm_context_impact": "Use as the first grounding source for how to explain the codebase to a user.",
        "safety_license_publication_impact": "Verify that public copy does not exceed the source project's own claims.",
    },
    "docs_tutorials": {
        "label": "Docs and tutorials",
        "provides": "Workflow variants, parameter meanings, edge cases, troubleshooting guidance, and domain vocabulary.",
        "skill_design_impact": "Use to decide which workflows deserve separate skills or reference files.",
        "adapter_impact": "Use documented variants to shape adapter options and error messages.",
        "llm_context_impact": "Use domain terms and troubleshooting notes for clarifying questions and explanations.",
        "safety_license_publication_impact": "Check whether limitations or intended-use notes must appear in SKILL.md and README.md.",
    },
    "scripts_apis_notebooks": {
        "label": "Scripts, APIs, notebooks, and bundles",
        "provides": "Executable entrypoints, arguments, side effects, return artifacts, and adapter opportunities.",
        "skill_design_impact": "Use to decide what the agent can actually help run, plan, or verify.",
        "adapter_impact": "Primary source for deterministic CLI wrappers, schema output, and provenance fields.",
        "llm_context_impact": "Use to keep the LLM from guessing unsupported commands or parameters.",
        "safety_license_publication_impact": "Flag commands that write files, run expensive work, call networks, or need approval.",
    },
    "configs_metadata_labels": {
        "label": "Configs, metadata, schemas, and label maps",
        "provides": "Modes, labels, defaults, supported modalities, model paths, validation rules, and structured fields.",
        "skill_design_impact": "Use to define exact input/output contracts and avoid vague skill claims.",
        "adapter_impact": "Use as deterministic lookup data for labels, modes, schemas, and validation checks.",
        "llm_context_impact": "Use to constrain LLM explanations to source-supported modes and labels.",
        "safety_license_publication_impact": "Ensure catalog metadata and examples use supported values.",
    },
    "examples_tests_data": {
        "label": "Examples, tests, sample data, and expected outputs",
        "provides": "Realistic input/output contracts, fixture candidates, expected artifacts, and skip conditions.",
        "skill_design_impact": "Use to choose smoke tests and concrete examples.",
        "adapter_impact": "Use to build deterministic tests and output verification commands.",
        "llm_context_impact": "Use examples to create realistic prompts and result explanations.",
        "safety_license_publication_impact": "Check whether sample data may be redistributed or must remain local.",
    },
    "dependencies_runtime": {
        "label": "Dependencies, runtime, Docker, Conda, and CI",
        "provides": "Runtime, OS, GPU, CUDA, Docker, package, install, and environment requirements.",
        "skill_design_impact": "Use to decide whether the skill is planning-only, guarded execution, or ready to run.",
        "adapter_impact": "Use for check commands, setup-plan output, and skip reasons.",
        "llm_context_impact": "Use to explain prerequisites without pretending they are installed.",
        "safety_license_publication_impact": "Call out expensive, platform-specific, privileged, or brittle runtime needs.",
    },
    "models_data_papers": {
        "label": "Model cards, dataset cards, papers, standards, and benchmarks",
        "provides": "Intended use, method context, citations, limitations, model/data terms, and supported claims.",
        "skill_design_impact": "Use to ground capabilities, limitations, citations, and scientific context.",
        "adapter_impact": "Use to identify model/data downloads, required assets, and provenance fields.",
        "llm_context_impact": "Use to summarize method context and limitations without overclaiming.",
        "safety_license_publication_impact": "Use to verify permitted use, restricted use, and claims safe for publication.",
    },
    "licenses_releases_security": {
        "label": "Licenses, releases, issues, and security notes",
        "provides": "Permitted use, restricted use, version pinning, known bugs, and maintenance status.",
        "skill_design_impact": "Use to set risk level, contribution guidance, and whether the skill can be published.",
        "adapter_impact": "Use to pin versions and warn about known breakage or unsupported paths.",
        "llm_context_impact": "Use to avoid unsupported trust, ownership, or maintenance claims.",
        "safety_license_publication_impact": "Primary source for license, redistribution, security, and versioning notes.",
    },
}


@dataclass(frozen=True)
class Artifact:
    path: str
    bytes: int
    suffix: str
    signals: list[str]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rel_posix(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def should_skip_dir(path: Path) -> bool:
    return path.name in EXCLUDED_DIRS


def file_priority(path: Path, root: Path) -> tuple[int, str]:
    rel = rel_posix(path, root).lower()
    parts = rel.split("/")
    name = parts[-1]
    top = parts[0] if parts else name
    score = 100

    if len(parts) == 1:
        score -= 45
    if name.startswith("readme"):
        score -= 35
    if name in {"license", "licence", "notice", "security.md", "citation.cff"}:
        score -= 25
    if top in {"docs", "documentation"}:
        score -= 20
    if top in {"src", "scripts", "configs", "config", "examples", "tests", "notebooks"}:
        score -= 15
    if name in {"pyproject.toml", "requirements.txt", "environment.yml", "environment.yaml", "setup.py"}:
        score -= 15
    if top in {"catalog", "site", "plugins", "downloads"}:
        score += 20

    return score, rel


def iter_repo_files(root: Path, max_total_files: int) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob("*"), key=lambda item: file_priority(item, root)):
        if path.is_dir() and should_skip_dir(path):
            continue
        if not path.is_file():
            continue
        relative_parts = path.relative_to(root).parts[:-1]
        if any(part in EXCLUDED_DIRS for part in relative_parts):
            continue
        files.append(path)
        if len(files) >= max_total_files:
            break
    return files


def classify_file(path: Path, root: Path) -> dict[str, list[str]]:
    rel = rel_posix(path, root)
    lowered = rel.lower()
    name = path.name.lower()
    suffix = path.suffix.lower()
    categories: dict[str, list[str]] = {}

    def add(category: str, signal: str) -> None:
        categories.setdefault(category, []).append(signal)

    if name.startswith("readme") or "quickstart" in lowered or "getting-started" in lowered or "getting_started" in lowered:
        add("readme_quickstart", "readme-or-quickstart")
    if lowered.startswith("docs/") or "/docs/" in lowered or any(term in lowered for term in ["tutorial", "guide", "manual", "documentation"]):
        add("docs_tutorials", "documentation-path-or-name")
    if suffix in {".py", ".sh", ".ps1", ".ipynb", ".js", ".ts", ".r", ".jl", ".java", ".cpp", ".c", ".cu"}:
        add("scripts_apis_notebooks", f"code-or-notebook:{suffix or name}")
    if any(term in lowered for term in ["cli", "command", "infer", "train", "evaluate", "predict", "pipeline", "bundle"]):
        add("scripts_apis_notebooks", "entrypoint-like-name")
    if suffix in {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf", ".xml"}:
        add("configs_metadata_labels", f"structured-config:{suffix}")
    if any(term in lowered for term in ["config", "metadata", "schema", "manifest", "label", "mapping"]):
        add("configs_metadata_labels", "metadata-or-label-name")
    if any(term in lowered for term in ["example", "demo", "sample", "test", "fixture", "expected"]):
        add("examples_tests_data", "example-test-or-sample")
    if name in {"requirements.txt", "pyproject.toml", "environment.yml", "environment.yaml", "setup.py", "setup.cfg", "package.json", "dockerfile", "makefile"}:
        add("dependencies_runtime", "runtime-dependency-file")
    if lowered.startswith(".github/") or "docker" in lowered or "conda" in lowered or "cuda" in lowered:
        add("dependencies_runtime", "runtime-or-ci-path")
    if any(term in lowered for term in ["model_card", "model-card", "dataset_card", "dataset-card", "paper", "benchmark", "citation", "citations", "bibtex"]):
        add("models_data_papers", "model-data-paper-source")
    if suffix in {".bib"}:
        add("models_data_papers", "citation-file")
    if name.startswith(("license", "licence", "notice", "security", "changelog", "release")) or any(term in lowered for term in ["license", "licence", "notice", "security", "changelog", "release-notes"]):
        add("licenses_releases_security", "license-release-or-security")

    return categories


def git_commit(root: Path) -> dict[str, str | None]:
    git = shutil.which("git")
    if not git:
        return {"commit": None, "status": "git-not-found"}
    try:
        result = subprocess.run(
            [git, "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True,
            check=False,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {"commit": None, "status": f"git-error:{exc}"}
    if result.returncode != 0:
        return {"commit": None, "status": "not-a-git-repo"}
    return {"commit": result.stdout.strip(), "status": "ok"}


def scan_repo(root: Path, workflow_goal: str, max_files_per_category: int, max_total_files: int) -> dict:
    root = root.resolve()
    if not root.exists() or not root.is_dir():
        return {
            "ok": False,
            "error": f"Repo path does not exist or is not a directory: {root}",
            "repo_path": str(root),
        }

    category_artifacts: dict[str, list[Artifact]] = {category: [] for category in CATEGORY_GUIDANCE}
    files = iter_repo_files(root, max_total_files=max_total_files)
    files_scanned = 0
    files_matched = 0

    for path in files:
        files_scanned += 1
        categories = classify_file(path, root)
        if not categories:
            continue
        files_matched += 1
        for category, signals in categories.items():
            artifacts = category_artifacts[category]
            if len(artifacts) >= max_files_per_category:
                continue
            artifacts.append(
                Artifact(
                    path=rel_posix(path, root),
                    bytes=path.stat().st_size,
                    suffix=path.suffix.lower(),
                    signals=sorted(set(signals)),
                )
            )

    source_context_map = []
    for category, guidance in CATEGORY_GUIDANCE.items():
        artifacts = category_artifacts[category]
        source_context_map.append(
            {
                "category": category,
                "label": guidance["label"],
                "what_it_provides": guidance["provides"],
                "skill_design_impact": guidance["skill_design_impact"],
                "adapter_or_deterministic_code_impact": guidance["adapter_impact"],
                "llm_context_impact": guidance["llm_context_impact"],
                "safety_license_publication_impact": guidance["safety_license_publication_impact"],
                "artifacts": [artifact.__dict__ for artifact in artifacts],
                "open_questions": [] if artifacts else [f"No {guidance['label'].lower()} artifacts detected by the scanner."],
            }
        )

    return {
        "ok": True,
        "scanned_at": utc_now(),
        "repo_path": str(root),
        "workflow_goal": workflow_goal,
        "source_version": git_commit(root),
        "files_scanned": files_scanned,
        "files_matched": files_matched,
        "max_total_files": max_total_files,
        "max_files_per_category": max_files_per_category,
        "source_context_map": source_context_map,
        "next_steps": [
            "Review the source-context map and add human notes for what each artifact contributes.",
            "Create a candidate skill table with source evidence for each candidate.",
            "Create readiness cards before generating SkillForge skill files.",
            "Separate LLM decisions from deterministic Python checks before writing adapters.",
        ],
    }


def table_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br>")


def render_source_context_markdown(payload: dict) -> str:
    lines = [
        "# Source Context Map",
        "",
        f"Repo path: `{payload['repo_path']}`",
        f"Workflow goal: {payload.get('workflow_goal') or 'Not provided'}",
        f"Scanned at: {payload['scanned_at']}",
        f"Source version: {payload['source_version'].get('commit') or payload['source_version'].get('status')}",
        "",
        "| Source area | What it provides | Skill design impact | Adapter/code impact | LLM context impact | Safety/license/publication impact | Detected artifacts | Open questions |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload["source_context_map"]:
        artifacts = "<br>".join(f"`{item['path']}`" for item in row["artifacts"][:10]) or "None detected"
        questions = "<br>".join(row["open_questions"]) or ""
        lines.append(
            "| "
            + " | ".join(
                [
                    table_cell(row["label"]),
                    table_cell(row["what_it_provides"]),
                    table_cell(row["skill_design_impact"]),
                    table_cell(row["adapter_or_deterministic_code_impact"]),
                    table_cell(row["llm_context_impact"]),
                    table_cell(row["safety_license_publication_impact"]),
                    table_cell(artifacts),
                    table_cell(questions),
                ]
            )
            + " |"
        )
    lines.append("")
    lines.append("Review note: this scanner finds evidence candidates. A human or LLM must still read the relevant artifacts before claiming capability, safety, license, or behavior.")
    return "\n".join(lines) + "\n"


def render_candidate_table_markdown(payload: dict) -> str:
    return "\n".join(
        [
            "# Candidate Skill Table",
            "",
            f"Repo path: `{payload['repo_path']}`",
            f"Workflow goal: {payload.get('workflow_goal') or 'Not provided'}",
            "",
            "Fill this table after reviewing the source-context map. Every candidate should cite source evidence.",
            "",
            "| Candidate skill | What it does | Why it is useful | Source evidence | Sample prompt call | Proposed CLI contract | Inputs | Outputs | Deterministic entrypoints | LLM context needed | Safety/license notes | Smoke-test source | Recommendation |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            "|  |  |  |  |  |  |  |  |  |  |  |  |  |",
            "",
            "Recommendations: `make-skill-now`, `needs-adapter-first`, `needs-docs-or-examples`, `needs-license-review`, or `not-a-good-skill-yet`.",
            "",
        ]
    )


def render_readiness_card_markdown(payload: dict) -> str:
    return "\n".join(
        [
            "# Codebase Readiness Card Draft",
            "",
            "Name:",
            "",
            f"Source: `{payload['repo_path']}`",
            "",
            f"Workflow goal: {payload.get('workflow_goal') or ''}",
            "",
            "Primary users:",
            "",
            "Recommendation:",
            "",
            "Recommendation rationale:",
            "",
            "## Source Context Map",
            "",
            "Use `source-context-map.md` as the evidence layer for this card.",
            "",
            "## Candidate Scope",
            "",
            "Proposed skill type:",
            "",
            "- Algorithm skill",
            "- Workflow skill",
            "- Generator skill",
            "- Other:",
            "",
            "Proposed skill ID:",
            "",
            "Should this be one skill or multiple skills?",
            "",
            "Why this scope:",
            "",
            "## Known Blockers",
            "",
            "- ",
            "",
            "## Open Questions",
            "",
            "- ",
            "",
            "## Next Action",
            "",
            "Next recommended action:",
            "",
        ]
    )


def write_outputs(payload: dict, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "scan_json": output_dir / "scan.json",
        "source_context_map": output_dir / "source-context-map.md",
        "candidate_skill_table": output_dir / "candidate-skill-table.md",
        "readiness_card_draft": output_dir / "readiness-card-draft.md",
    }
    files["scan_json"].write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    files["source_context_map"].write_text(render_source_context_markdown(payload), encoding="utf-8")
    files["candidate_skill_table"].write_text(render_candidate_table_markdown(payload), encoding="utf-8")
    files["readiness_card_draft"].write_text(render_readiness_card_markdown(payload), encoding="utf-8")
    return {key: str(path) for key, path in files.items()}


def schema_payload() -> dict:
    return {
        "ok": True,
        "commands": {
            "check": {
                "description": "Report local helper readiness without scanning or writing files.",
                "side_effects": "Read-only.",
                "required_args": [],
                "optional_args": ["--json"],
            },
            "schema": {
                "description": "Describe supported commands and JSON fields.",
                "side_effects": "Read-only.",
                "required_args": [],
                "optional_args": ["--json"],
            },
            "scan": {
                "description": "Scan a local repository for source-context evidence candidates.",
                "side_effects": "Reads repo files. Writes Markdown/JSON only when --output-dir is provided.",
                "required_args": ["repo_path"],
                "optional_args": ["--workflow-goal", "--output-dir", "--max-files-per-category", "--max-total-files", "--json"],
            },
        },
        "stable_json_fields": [
            "ok",
            "repo_path",
            "workflow_goal",
            "source_version",
            "files_scanned",
            "files_matched",
            "source_context_map",
            "written_files",
            "next_steps",
        ],
    }


def check_payload() -> dict:
    return {
        "ok": True,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "network": "not-used",
        "writes": "only when scan --output-dir is provided",
    }


def print_human(payload: dict) -> None:
    if not payload.get("ok"):
        print(f"Error: {payload.get('error', 'unknown error')}")
        return
    if "source_context_map" not in payload:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print(f"Scanned: {payload['repo_path']}")
    print(f"Matched files: {payload['files_matched']} of {payload['files_scanned']}")
    for row in payload["source_context_map"]:
        print(f"- {row['label']}: {len(row['artifacts'])} artifact(s)")
    if payload.get("written_files"):
        print("Written files:")
        for path in payload["written_files"].values():
            print(f"- {path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scan a local codebase for codebase-to-agentic-skills evidence.")
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check", help="Report helper readiness")
    check.add_argument("--json", action="store_true")

    schema = sub.add_parser("schema", help="Report command schema")
    schema.add_argument("--json", action="store_true")

    scan = sub.add_parser("scan", help="Scan a local repo or codebase path")
    scan.add_argument("repo_path")
    scan.add_argument("--workflow-goal", default="")
    scan.add_argument("--output-dir")
    scan.add_argument("--max-files-per-category", type=int, default=25)
    scan.add_argument("--max-total-files", type=int, default=5000)
    scan.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "check":
        payload = check_payload()
    elif args.command == "schema":
        payload = schema_payload()
    else:
        payload = scan_repo(
            Path(args.repo_path),
            workflow_goal=args.workflow_goal,
            max_files_per_category=args.max_files_per_category,
            max_total_files=args.max_total_files,
        )
        if payload.get("ok") and args.output_dir:
            payload["written_files"] = write_outputs(payload, Path(args.output_dir))

    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_human(payload)
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
