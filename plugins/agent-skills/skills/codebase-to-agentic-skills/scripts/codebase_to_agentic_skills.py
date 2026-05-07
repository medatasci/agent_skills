from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
from pprint import pformat
import re
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


@dataclass(frozen=True)
class HealthcareSignal:
    path: str
    signal_type: str
    signal: str
    evidence: str


TEXT_SAMPLE_SUFFIXES = {
    ".bib",
    ".cfg",
    ".conf",
    ".ini",
    ".ipynb",
    ".json",
    ".md",
    ".py",
    ".rst",
    ".sh",
    ".text",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}


COMMAND_STARTERS = (
    "python ",
    "python3 ",
    "py ",
    "pip ",
    "pip3 ",
    "conda ",
    "mamba ",
    "docker ",
    "git clone ",
    "curl ",
    "wget ",
    "bash ",
    "sh ",
    "pwsh ",
    "powershell ",
    "jupyter ",
    "monai ",
    "torchrun ",
)


PYTHON_CLI_PATTERNS = (
    ("argparse", "argparse.ArgumentParser"),
    ("click", "@click.command"),
    ("click", "click.group"),
    ("click", "click.command"),
    ("typer", "typer.Typer"),
    ("main", "if __name__ == \"__main__\""),
    ("main", "if __name__ == '__main__'"),
    ("main", "def main("),
)


SIDE_EFFECT_CATEGORY_ORDER = [
    "read-only-inspection",
    "install",
    "download",
    "network-access",
    "file-write",
    "gpu-or-model-execution",
    "container-runtime",
    "environment-management",
    "shell-script",
    "unknown-review-required",
]


EXECUTION_GATE_ORDER = [
    "safe-to-inspect",
    "needs-user-approval",
    "needs-runtime-plan",
    "needs-data-safety-review",
    "do-not-run-from-scanner",
]


ADAPTER_POLICY_ORDER = [
    "read-only-check",
    "setup-plan",
    "runtime-plan",
    "guarded-run",
    "no-adapter-until-review",
]


ADAPTER_POLICY_BY_GATE = {
    "safe-to-inspect": {
        "adapter_type": "read-only-check",
        "intent": "Expose schema, check, help, provenance, and source-inspection behavior only.",
        "allowed_actions": [
            "read source files",
            "print schema or help",
            "check local prerequisites without installing or writing outputs",
        ],
        "required_before_run": ["confirm-no-import-time-side-effects"],
        "blocked_actions": ["install dependencies", "download models or data", "write outputs", "run model inference"],
    },
    "needs-user-approval": {
        "adapter_type": "setup-plan",
        "intent": "Create a setup plan that explains install, download, or network steps before any side effects occur.",
        "allowed_actions": [
            "read source files",
            "summarize setup commands",
            "produce an approval-ready setup plan",
        ],
        "required_before_run": ["source-review", "runtime-plan", "human-approval"],
        "blocked_actions": ["run installs", "download resources", "access network", "modify environment"],
    },
    "needs-runtime-plan": {
        "adapter_type": "runtime-plan",
        "intent": "Create runtime checks and a launch plan before exposing a guarded run command.",
        "allowed_actions": [
            "read source files",
            "check local runtime prerequisites",
            "write a reviewed runtime plan",
        ],
        "required_before_run": ["source-review", "runtime-plan"],
        "blocked_actions": ["run containers", "run GPU jobs", "modify environments without approval"],
    },
    "needs-data-safety-review": {
        "adapter_type": "guarded-run",
        "intent": "Expose planning and verification first; require explicit approval, data-safety review, and runtime readiness before execution.",
        "allowed_actions": [
            "read source files",
            "plan input and output paths",
            "verify expected output artifacts",
            "run only behind an explicit confirmation flag after review",
        ],
        "required_before_run": ["source-review", "runtime-plan", "data-safety-review", "human-approval"],
        "blocked_actions": ["implicit execution", "writing outputs without explicit output directory", "logging sensitive inputs"],
    },
    "do-not-run-from-scanner": {
        "adapter_type": "no-adapter-until-review",
        "intent": "Do not create a runnable adapter from this command until source behavior is manually reviewed.",
        "allowed_actions": ["read source files", "record open questions", "ask for human review"],
        "required_before_run": ["source-review", "human-approval"],
        "blocked_actions": ["running the command", "wrapping shell delegation as a runnable adapter"],
    },
}


ADAPTER_PLAN_STUBS_BY_POLICY = {
    "read-only-check": {
        "title": "Read-only check adapter",
        "purpose": "Expose schema, help, provenance, and prerequisite checks without installing dependencies, downloading assets, running models, or writing workflow outputs.",
        "suggested_commands": [
            "python scripts/<adapter>.py schema --json",
            "python scripts/<adapter>.py check --source-dir <source-dir> --json",
        ],
        "required_inputs": ["source-dir"],
        "expected_outputs": ["JSON schema output", "JSON readiness or missing-prerequisite report"],
        "guardrails": [
            "read-only by default",
            "no dependency installation",
            "no network access",
            "no model execution",
            "no workflow output writes",
        ],
        "smoke_test_stub": [
            "schema command returns stable JSON",
            "check command reports missing source or dependencies without raising an exception",
        ],
    },
    "setup-plan": {
        "title": "Setup-plan adapter",
        "purpose": "Produce an approval-ready setup plan for installs, downloads, environment changes, or network steps without performing those side effects.",
        "suggested_commands": [
            "python scripts/<adapter>.py setup-plan --source-dir <source-dir> --target <runtime-target> --json",
            "python scripts/<adapter>.py check --source-dir <source-dir> --json",
        ],
        "required_inputs": ["source-dir", "runtime-target"],
        "expected_outputs": ["JSON setup plan", "approval checklist", "install/download/network side-effect list"],
        "guardrails": [
            "summarize install commands instead of running them",
            "summarize download commands instead of running them",
            "require human approval before environment changes",
            "record source references for each setup step",
        ],
        "smoke_test_stub": [
            "setup-plan command emits commands as data, not executed processes",
            "setup-plan includes approval_required=true for install, download, or network steps",
        ],
    },
    "runtime-plan": {
        "title": "Runtime-plan adapter",
        "purpose": "Plan runtime prerequisites, launch conditions, and skip reasons before any container, environment, GPU, or model workflow runs.",
        "suggested_commands": [
            "python scripts/<adapter>.py runtime-plan --source-dir <source-dir> --input <input-path> --output-dir <output-dir> --json",
            "python scripts/<adapter>.py check --source-dir <source-dir> --json",
        ],
        "required_inputs": ["source-dir", "input-path", "output-dir"],
        "expected_outputs": ["JSON runtime plan", "runtime readiness checks", "skip reasons"],
        "guardrails": [
            "do not run containers or GPU jobs from planning commands",
            "require explicit output directory before any future execution",
            "record OS, CUDA, container, and dependency assumptions",
        ],
        "smoke_test_stub": [
            "runtime-plan handles missing input path with structured JSON",
            "runtime-plan reports GPU/container prerequisites without launching them",
        ],
    },
    "guarded-run": {
        "title": "Guarded-run adapter",
        "purpose": "Expose planning and verification first, then allow execution only behind explicit confirmation after runtime and data-safety review.",
        "suggested_commands": [
            "python scripts/<adapter>.py plan --source-dir <source-dir> --input <input-path> --output-dir <output-dir> --json",
            "python scripts/<adapter>.py run --source-dir <source-dir> --input <input-path> --output-dir <output-dir> --confirm-execution --json",
            "python scripts/<adapter>.py verify-output --output-dir <output-dir> --json",
        ],
        "required_inputs": ["source-dir", "input-path", "output-dir", "confirm-execution"],
        "expected_outputs": ["JSON execution plan", "explicit output artifacts", "provenance JSON", "verification report"],
        "guardrails": [
            "require --confirm-execution for side-effecting runs",
            "require explicit output directory",
            "do not log sensitive input content",
            "write provenance for source version, command, inputs, outputs, and approvals",
            "support plan and verify-output without execution",
        ],
        "smoke_test_stub": [
            "run command refuses without --confirm-execution",
            "plan command is read-only",
            "verify-output reports missing artifacts without running inference",
        ],
    },
    "no-adapter-until-review": {
        "title": "No runnable adapter until review",
        "purpose": "Block runnable adapter generation until a human or LLM completes source review and resolves unknown side effects.",
        "suggested_commands": [
            "python scripts/<adapter>.py source-review --source-dir <source-dir> --json",
        ],
        "required_inputs": ["source-dir"],
        "expected_outputs": ["open questions", "source-review checklist", "blocked-command list"],
        "guardrails": [
            "do not wrap unknown or shell-delegated commands as runnable adapters",
            "record why execution is blocked",
            "ask for human review before proposing run commands",
        ],
        "smoke_test_stub": [
            "source-review command lists blocked commands and exits successfully",
            "no generated command includes --confirm-execution until review is complete",
        ],
    },
}


HEALTHCARE_SIGNAL_RULES = {
    "medical_imaging_format": [
        "dicom",
        "dcm2niix",
        ".dcm",
        ".nii",
        "nifti",
        "nrrd",
        ".mha",
        ".mhd",
    ],
    "monai_or_bundle": [
        "monai",
        "bundle",
        "bundle/configs",
        "metadata.json",
        "vista3d",
        "maisi",
    ],
    "model_runtime": [
        "cuda",
        "gpu",
        "torch",
        "pytorch",
        "nvidia",
        "tensorrt",
        "docker",
        "conda",
        "wsl",
    ],
    "task_or_output": [
        "segmentation",
        "mask",
        "label map",
        "inference",
        "synthesis",
        "generation",
        "registration",
        "classification",
    ],
    "model_data_paper_context": [
        "model card",
        "dataset card",
        "huggingface",
        "arxiv",
        "paper",
        "citation",
        "benchmark",
    ],
    "medical_safety": [
        "research use",
        "not for clinical",
        "not intended for diagnosis",
        "diagnosis",
        "treatment",
        "triage",
        "patient",
        "phi",
        "hipaa",
        "intended use",
    ],
}


HEALTHCARE_READING_GUIDANCE = {
    "medical_imaging_format": {
        "review_area": "Modality and file-format support",
        "why": "File-format terms help identify whether the repo may handle DICOM, NIfTI, NRRD, MHA/MHD, or conversion workflows.",
        "questions": [
            "Which image formats are accepted as inputs?",
            "Which formats are produced as outputs?",
            "Does the repo require conversion, orientation handling, spacing handling, or preprocessing before inference?",
        ],
        "claim_boundary": "Do not claim support for a modality or format until a README, config, code path, or example explicitly supports it.",
    },
    "monai_or_bundle": {
        "review_area": "MONAI, bundle, and model-family context",
        "why": "MONAI and bundle clues often define model packaging, configuration structure, labels, transforms, and inference entry points.",
        "questions": [
            "Is this a MONAI bundle, a standalone script, or a larger application?",
            "Where are bundle configs, metadata, label dictionaries, and transforms defined?",
            "Which upstream model family or workflow does the skill need to cite?",
        ],
        "claim_boundary": "Do not claim MONAI bundle compatibility or model-family behavior until configs and metadata are read.",
    },
    "model_runtime": {
        "review_area": "Runtime, installation, and execution constraints",
        "why": "Runtime clues indicate whether the skill may need GPU, CUDA, Docker, Conda, WSL, PyTorch, or NVIDIA-specific setup.",
        "questions": [
            "What operating systems and runtimes are documented?",
            "Is GPU or CUDA required, optional, or only needed for full inference?",
            "What dependency installation, model download, or container setup is required before execution?",
        ],
        "claim_boundary": "Do not run installs, downloads, containers, or GPU jobs without explicit user approval and a smoke-test plan.",
    },
    "task_or_output": {
        "review_area": "Task, workflow, and output contract",
        "why": "Task/output terms help distinguish segmentation, generation, registration, classification, masks, label maps, and inference workflows.",
        "questions": [
            "What user-level task should the skill expose?",
            "What inputs, outputs, side effects, and file naming conventions should the CLI contract use?",
            "Is this one skill, multiple functional-block skills, or a workflow skill?",
        ],
        "claim_boundary": "Do not collapse separate algorithms into one skill unless the source workflow and user goal justify that scope.",
    },
    "model_data_paper_context": {
        "review_area": "Model, dataset, paper, and citation provenance",
        "why": "Model cards, dataset cards, papers, citations, and benchmark notes are authoritative sources for claims and search metadata.",
        "questions": [
            "Which papers, model cards, dataset cards, or benchmarks must be cited?",
            "What model/data license or access constraints apply?",
            "Which claims are source-backed and which need conservative wording?",
        ],
        "claim_boundary": "Do not invent citations, benchmark claims, training data details, or model capabilities.",
    },
    "medical_safety": {
        "review_area": "Medical safety, privacy, and intended-use boundaries",
        "why": "Medical-use terms can indicate research-only boundaries, clinical disclaimers, PHI/privacy concerns, or safety constraints.",
        "questions": [
            "Is the source restricted to research use or explicitly not for clinical use?",
            "Could inputs or logs contain PHI or sensitive patient data?",
            "What warnings should the skill show before execution or publication?",
        ],
        "claim_boundary": "Do not present repo-derived skills as diagnostic, treatment, triage, or clinical decision tools.",
    },
}


HEALTHCARE_READING_SOURCE_CATEGORIES = {
    "medical_imaging_format": ["readme_quickstart", "docs_tutorials", "configs_metadata_labels", "examples_tests_data"],
    "monai_or_bundle": ["readme_quickstart", "docs_tutorials", "scripts_apis_notebooks", "configs_metadata_labels", "models_data_papers"],
    "model_runtime": ["readme_quickstart", "docs_tutorials", "dependencies_runtime", "scripts_apis_notebooks"],
    "task_or_output": ["readme_quickstart", "docs_tutorials", "scripts_apis_notebooks", "configs_metadata_labels", "examples_tests_data"],
    "model_data_paper_context": ["models_data_papers", "docs_tutorials", "licenses_releases_security"],
    "medical_safety": ["readme_quickstart", "docs_tutorials", "models_data_papers", "licenses_releases_security"],
}


TASK_HYPOTHESIS_LABELS = {
    "segmentation": {
        "name": "Research medical image segmentation workflow",
        "prompt": "Use this source repository to plan a research medical image segmentation workflow. Show source evidence before proposing commands.",
        "goal_terms": ["segmentation", "segment", "segmented", "mask", "label map"],
    },
    "mask": {
        "name": "Research medical image mask workflow",
        "prompt": "Use this source repository to plan a research medical image mask workflow. Show source evidence before proposing commands.",
        "goal_terms": ["mask", "masks", "segmentation mask", "label mask"],
    },
    "label map": {
        "name": "Research medical image label-map workflow",
        "prompt": "Use this source repository to plan a research medical image label-map workflow. Show source evidence before proposing commands.",
        "goal_terms": ["label map", "label-map", "labels", "segmentation labels"],
    },
    "generation": {
        "name": "Research medical image generation workflow",
        "prompt": "Use this source repository to plan a research medical image generation workflow. Show source evidence before proposing commands.",
        "goal_terms": ["generation", "generate", "generating", "synthetic", "synthesis"],
    },
    "synthesis": {
        "name": "Research synthetic medical image workflow",
        "prompt": "Use this source repository to plan a research synthetic medical image workflow. Show source evidence before proposing commands.",
        "goal_terms": ["synthesis", "synthetic", "generate", "generation", "image generation"],
    },
    "registration": {
        "name": "Research medical image registration workflow",
        "prompt": "Use this source repository to plan a research medical image registration workflow. Show source evidence before proposing commands.",
        "goal_terms": ["registration", "register", "alignment", "transform"],
    },
    "classification": {
        "name": "Research medical image classification workflow",
        "prompt": "Use this source repository to plan a research medical image classification workflow. Show source evidence before proposing commands.",
        "goal_terms": ["classification", "classify", "classifier", "prediction"],
    },
    "inference": {
        "name": "Research medical AI inference workflow",
        "prompt": "Use this source repository to plan a research medical AI inference workflow. Show source evidence before proposing commands.",
        "goal_terms": ["inference", "infer", "prediction", "run model"],
    },
}


HYPOTHESIS_SOURCE_CATEGORIES = [
    "readme_quickstart",
    "docs_tutorials",
    "scripts_apis_notebooks",
    "configs_metadata_labels",
    "examples_tests_data",
    "dependencies_runtime",
    "models_data_papers",
    "licenses_releases_security",
]


HYPOTHESIS_COVERAGE_AREAS = [
    {
        "id": "readme_or_quickstart",
        "label": "README or quick start",
        "categories": ["readme_quickstart"],
    },
    {
        "id": "docs_or_tutorials",
        "label": "Docs or tutorials",
        "categories": ["docs_tutorials"],
    },
    {
        "id": "entrypoints",
        "label": "Executable entrypoints",
        "categories": ["scripts_apis_notebooks"],
    },
    {
        "id": "configs_labels_metadata",
        "label": "Configs, labels, or metadata",
        "categories": ["configs_metadata_labels"],
    },
    {
        "id": "examples_tests_data",
        "label": "Examples, tests, or sample data",
        "categories": ["examples_tests_data"],
    },
    {
        "id": "runtime_requirements",
        "label": "Runtime requirements",
        "categories": ["dependencies_runtime"],
    },
    {
        "id": "model_data_or_papers",
        "label": "Model/data/paper provenance",
        "categories": ["models_data_papers"],
    },
    {
        "id": "license_security",
        "label": "License, release, or security context",
        "categories": ["licenses_releases_security"],
    },
]


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


def text_sample(path: Path, *, max_chars: int = 12000) -> str:
    if path.suffix.lower() not in TEXT_SAMPLE_SUFFIXES:
        return ""
    try:
        if path.stat().st_size > 1_000_000:
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")[:max_chars]
    except OSError:
        return ""


def normalized_command_line(line: str) -> str:
    command = line.strip()
    if not command:
        return ""
    command = re.sub(r"^(?:\$|>|PS>|PS C:[^>]*>|#)\s*", "", command, flags=re.IGNORECASE)
    command = re.sub(r"^\([^)]+\)\s*\$\s*", "", command)
    command = command.strip()
    if command.startswith(("```", "<", "|")):
        return ""
    return command


def platform_assumption_for_command(command: str) -> str:
    lowered = command.lower()
    if lowered.startswith(("pwsh ", "powershell ")) or ".ps1" in lowered:
        return "windows-powershell-or-pwsh"
    if lowered.startswith(("bash ", "sh ")) or lowered.endswith(".sh") or " ./" in lowered:
        return "posix-shell"
    if lowered.startswith("docker "):
        return "docker-runtime"
    if lowered.startswith(("conda ", "mamba ")):
        return "conda-compatible-environment"
    if lowered.startswith(("python ", "python3 ", "py ", "pip ", "pip3 ", "jupyter ", "monai ", "torchrun ")):
        return "python-environment"
    return "unknown"


def side_effect_categories_for_command(command: str) -> list[str]:
    lowered = command.lower()
    categories: set[str] = set()

    if lowered.endswith(" --help") or lowered.endswith(" -h"):
        categories.add("read-only-inspection")
    if any(term in lowered for term in ["pip install", "conda install", "mamba install", "apt install", "brew install"]):
        categories.add("install")
    if any(term in lowered for term in ["git clone", "pip install", "conda install", "mamba install", "docker pull", "curl ", "wget "]):
        categories.add("network-access")
    if any(term in lowered for term in ["download", "docker pull", "curl ", "wget "]):
        categories.add("download")
    if any(term in lowered for term in ["--output", "--out", "--save", ">", "export", "write"]):
        categories.add("file-write")
    if any(term in lowered for term in ["train", "infer", "inference", "predict", "segment", "generate", "evaluate", "torchrun"]):
        categories.add("gpu-or-model-execution")
    if any(term in lowered for term in ["gpu", "cuda", "torchrun", "nvidia-smi"]):
        categories.add("gpu-or-model-execution")
    if lowered.startswith("docker "):
        categories.add("container-runtime")
    if lowered.startswith(("conda ", "mamba ", "pip ", "pip3 ")):
        categories.add("environment-management")
    if lowered.startswith(("bash ", "sh ", "pwsh ", "powershell ")):
        categories.add("shell-script")

    if not categories:
        categories.add("unknown-review-required")
    return [category for category in SIDE_EFFECT_CATEGORY_ORDER if category in categories]


def side_effect_risk_for_command(command: str) -> tuple[str, str]:
    categories = side_effect_categories_for_command(command)
    if "install" in categories or "network-access" in categories:
        return "network-or-install", "May download code, packages, containers, or other remote resources."
    if "gpu-or-model-execution" in categories:
        return "compute-or-model-run", "May run model, GPU, or workflow code and may write outputs."
    if "file-write" in categories:
        return "possible-file-write", "May write files or create output artifacts."
    if categories == ["read-only-inspection"]:
        return "low-readonly-help", "Expected to print help, but confirm the entrypoint has no import-time side effects."
    return "unknown-review-required", "Side effects are unclear until source documentation is reviewed."


def execution_gate_for_command(categories: list[str], *, healthcare_context: bool) -> dict:
    category_set = set(categories)
    required_reviews: list[str] = []
    reasons: list[str] = []

    if "unknown-review-required" in category_set or "shell-script" in category_set:
        gate = "do-not-run-from-scanner"
        reasons.append("Command side effects are unknown or delegated through a shell script.")
        required_reviews.extend(["source-review", "human-approval"])
    elif healthcare_context and category_set.intersection({"file-write", "gpu-or-model-execution"}):
        gate = "needs-data-safety-review"
        reasons.append("Healthcare-context command may write outputs or run model/GPU workflow code.")
        required_reviews.extend(["source-review", "runtime-plan", "data-safety-review", "human-approval"])
    elif category_set.intersection({"install", "download", "network-access"}):
        gate = "needs-user-approval"
        reasons.append("Command may install packages, download resources, or access the network.")
        required_reviews.extend(["source-review", "runtime-plan", "human-approval"])
    elif category_set.intersection({"container-runtime", "environment-management", "gpu-or-model-execution"}):
        gate = "needs-runtime-plan"
        reasons.append("Command depends on runtime, environment, container, or compute setup.")
        required_reviews.extend(["source-review", "runtime-plan"])
    elif category_set == {"read-only-inspection"}:
        gate = "safe-to-inspect"
        reasons.append("Command appears limited to help or inspection output.")
        required_reviews.append("confirm-no-import-time-side-effects")
    else:
        gate = "do-not-run-from-scanner"
        reasons.append("Command does not match a known safe inspection pattern.")
        required_reviews.extend(["source-review", "human-approval"])

    return {
        "gate": gate,
        "reasons": reasons,
        "required_reviews": sorted(set(required_reviews)),
        "caveat": "Execution gates are scanner triage recommendations, not approval to run commands.",
    }


def apply_execution_gates(command_evidence: list[dict], *, healthcare_context: bool) -> list[dict]:
    gated: list[dict] = []
    for item in command_evidence:
        next_item = dict(item)
        next_item["execution_gate"] = execution_gate_for_command(
            item.get("side_effect_categories", []),
            healthcare_context=healthcare_context,
        )
        gated.append(next_item)
    return gated


def adapter_policy_for_gate(gate: str) -> dict:
    policy = ADAPTER_POLICY_BY_GATE.get(gate, ADAPTER_POLICY_BY_GATE["do-not-run-from-scanner"])
    return {
        "adapter_type": policy["adapter_type"],
        "intent": policy["intent"],
        "allowed_actions": list(policy["allowed_actions"]),
        "required_before_run": list(policy["required_before_run"]),
        "blocked_actions": list(policy["blocked_actions"]),
        "source_gate": gate,
        "caveat": "Adapter policies are design guidance for a future wrapper, not permission to execute source commands.",
    }


def adapter_policy_for_command(command: dict) -> dict:
    gate = command.get("execution_gate", {}).get("gate", "do-not-run-from-scanner")
    policy = adapter_policy_for_gate(gate)
    policy["source_command"] = command.get("command")
    policy["source_path"] = command.get("source_path")
    policy["source_line"] = command.get("line")
    policy["source_heading"] = command.get("source_heading", "")
    policy["side_effect_categories"] = list(command.get("side_effect_categories", []))
    policy["recommendation_scope"] = adapter_recommendation_scope(command)
    if command.get("candidate_relevance"):
        policy["candidate_relevance"] = dict(command["candidate_relevance"])
    return policy


def adapter_recommendation_scope(command: dict) -> str:
    source_path = str(command.get("source_path") or "").lower()
    source_command = str(command.get("command") or "").lower()
    repo_maintenance_paths = (
        ".pre-commit-config.",
        ".pre-commit-config.yaml",
        ".pre-commit-config.yml",
        "ruff.toml",
        ".ruff.toml",
    )
    if source_path in repo_maintenance_paths or any(source_path.endswith(path) for path in repo_maintenance_paths):
        return "repo-maintenance"
    maintenance_terms = (" lint", "linting", " format", "formatting", "pre-commit", "ruff", "flake8", "black ")
    if any(term in source_command for term in maintenance_terms) and not any(
        term in source_command for term in ("infer", "inference", "segment", "generate", "train", "download")
        ):
            return "repo-maintenance"
    return "workflow"


def normalized_match_terms(terms: list[str] | tuple[str, ...] | set[str] | None) -> list[str]:
    if not terms:
        return []
    normalized: list[str] = []
    seen: set[str] = set()
    for term in terms:
        value = str(term or "").strip().lower()
        if len(value) < 3 or value in seen:
            continue
        seen.add(value)
        normalized.append(value)
    return normalized


def command_match_text(command: dict) -> str:
    return " ".join(
        str(command.get(field) or "")
        for field in ("command", "source_path", "source_heading", "snippet", "source_type")
    ).lower()


def command_candidate_relevance(
    command: dict,
    *,
    candidate_terms: list[str] | tuple[str, ...] | set[str] | None = None,
    workflow_goal_terms: list[str] | tuple[str, ...] | set[str] | None = None,
) -> dict:
    candidate_terms_normalized = normalized_match_terms(candidate_terms)
    workflow_goal_terms_normalized = normalized_match_terms(workflow_goal_terms)
    text = command_match_text(command)
    candidate_matches = sorted({term for term in candidate_terms_normalized if term in text})
    workflow_goal_matches = sorted({term for term in workflow_goal_terms_normalized if term in text})
    score = (len(candidate_matches) * 10) + (len(workflow_goal_matches) * 3)
    return {
        "score": score,
        "candidate_terms": candidate_terms_normalized,
        "workflow_goal_terms": workflow_goal_terms_normalized,
        "matched_candidate_terms": candidate_matches,
        "matched_workflow_goal_terms": workflow_goal_matches,
        "scope": adapter_recommendation_scope(command),
    }


def candidate_relevant_command_evidence(
    command_evidence: list[dict],
    *,
    candidate_terms: list[str] | tuple[str, ...] | set[str] | None = None,
    workflow_goal_terms: list[str] | tuple[str, ...] | set[str] | None = None,
) -> list[dict]:
    scored_commands: list[dict] = []
    for index, item in enumerate(command_evidence):
        next_item = dict(item)
        relevance = command_candidate_relevance(
            next_item,
            candidate_terms=candidate_terms,
            workflow_goal_terms=workflow_goal_terms,
        )
        relevance["source_order"] = index
        next_item["candidate_relevance"] = relevance
        scored_commands.append(next_item)
    return sorted(
        scored_commands,
        key=lambda item: (
            1 if item["candidate_relevance"]["scope"] == "repo-maintenance" else 0,
            -item["candidate_relevance"]["score"],
            item["candidate_relevance"]["source_order"],
        ),
    )


def adapter_policy_summary(
    command_evidence: list[dict],
    *,
    candidate_terms: list[str] | tuple[str, ...] | set[str] | None = None,
    workflow_goal_terms: list[str] | tuple[str, ...] | set[str] | None = None,
) -> dict:
    policy_counts = {adapter_type: 0 for adapter_type in ADAPTER_POLICY_ORDER}
    relevant_command_evidence = candidate_relevant_command_evidence(
        command_evidence,
        candidate_terms=candidate_terms,
        workflow_goal_terms=workflow_goal_terms,
    )
    command_policies = [adapter_policy_for_command(item) for item in relevant_command_evidence]
    for policy in command_policies:
        adapter_type = policy["adapter_type"]
        policy_counts[adapter_type] = policy_counts.get(adapter_type, 0) + 1
    policies = [
        {
            "adapter_type": adapter_type,
            "count": count,
            "commands": [
                policy["source_command"]
                for policy in command_policies
                if policy["adapter_type"] == adapter_type
            ][:5],
        }
        for adapter_type, count in policy_counts.items()
        if count
    ]
    highest_policy = "none"
    for adapter_type in reversed(ADAPTER_POLICY_ORDER):
        if policy_counts.get(adapter_type, 0):
            highest_policy = adapter_type
            break
    recommendation_counts = {adapter_type: 0 for adapter_type in ADAPTER_POLICY_ORDER}
    workflow_recommendation_policies = [
        policy
        for policy in command_policies
        if policy.get("recommendation_scope") != "repo-maintenance"
    ]
    candidate_recommendation_policies = [
        policy
        for policy in workflow_recommendation_policies
        if policy.get("candidate_relevance", {}).get("matched_candidate_terms")
    ]
    workflow_goal_recommendation_policies = [
        policy
        for policy in workflow_recommendation_policies
        if policy.get("candidate_relevance", {}).get("matched_workflow_goal_terms")
    ]
    recommendation_policies = workflow_recommendation_policies
    recommendation_basis = "all-command-evidence"
    if candidate_recommendation_policies:
        recommendation_policies = candidate_recommendation_policies
        recommendation_basis = "candidate-command-evidence"
    elif workflow_goal_recommendation_policies:
        recommendation_policies = workflow_goal_recommendation_policies
        recommendation_basis = "workflow-goal-command-evidence"
    elif workflow_recommendation_policies:
        recommendation_basis = "workflow-command-evidence"
    for policy in recommendation_policies:
        adapter_type = policy["adapter_type"]
        recommendation_counts[adapter_type] = recommendation_counts.get(adapter_type, 0) + 1
    recommended_policy = highest_policy
    if recommendation_policies:
        for adapter_type in reversed(ADAPTER_POLICY_ORDER):
            if recommendation_counts.get(adapter_type, 0):
                recommended_policy = adapter_type
                break
    ignored_for_recommendation: list[dict] = []
    selected_policy_ids = {
        (policy.get("source_command"), policy.get("source_path"), policy.get("source_line"))
        for policy in recommendation_policies
    }
    for policy in command_policies:
        policy_id = (policy.get("source_command"), policy.get("source_path"), policy.get("source_line"))
        if policy_id in selected_policy_ids:
            continue
        reason = None
        if policy.get("recommendation_scope") == "repo-maintenance":
            reason = "repo-maintenance command, not candidate workflow command"
        elif candidate_recommendation_policies:
            reason = "command did not match candidate task terms"
        if reason:
            ignored_for_recommendation.append(
                {
                    "command": policy.get("source_command"),
                    "source_path": policy.get("source_path"),
                    "adapter_type": policy.get("adapter_type"),
                    "reason": reason,
                }
            )
    return {
        "highest_policy": highest_policy,
        "recommended_policy": recommended_policy,
        "recommendation_basis": recommendation_basis,
        "candidate_terms": normalized_match_terms(candidate_terms),
        "workflow_goal_terms": normalized_match_terms(workflow_goal_terms),
        "ignored_for_recommendation": ignored_for_recommendation[:5],
        "policies": policies,
        "command_policies": command_policies,
        "caveat": "Adapter policies should be reviewed against source docs, runtime requirements, data-safety needs, and user approval before implementation.",
    }


def adapter_plan_stub_for_policy(
    adapter_type: str,
    *,
    command_policies: list[dict],
    entrypoint_refs: list[str],
    config_refs: list[str],
    runtime_refs: list[str],
) -> dict:
    template = ADAPTER_PLAN_STUBS_BY_POLICY.get(adapter_type, ADAPTER_PLAN_STUBS_BY_POLICY["no-adapter-until-review"])
    matching_policies = [policy for policy in command_policies if policy.get("adapter_type") == adapter_type]
    required_reviews = sorted(
        {
            review
            for policy in matching_policies
            for review in policy.get("required_before_run", [])
        }
    )
    source_commands = [
        {
            "command": policy.get("source_command"),
            "source_path": policy.get("source_path"),
            "source_line": policy.get("source_line"),
            "source_heading": policy.get("source_heading", ""),
            "side_effect_categories": policy.get("side_effect_categories", []),
        }
        for policy in matching_policies[:5]
    ]
    confirm_required = adapter_type == "guarded-run"
    return {
        "adapter_type": adapter_type,
        "title": template["title"],
        "status": "stub-needs-source-review",
        "purpose": template["purpose"],
        "suggested_commands": list(template["suggested_commands"]),
        "required_inputs": list(template["required_inputs"]),
        "expected_outputs": list(template["expected_outputs"]),
        "guardrails": list(template["guardrails"]),
        "required_reviews": required_reviews,
        "confirm_execution_required": confirm_required,
        "source_commands": source_commands,
        "source_refs": {
            "entrypoints": entrypoint_refs[:5],
            "configs": config_refs[:3],
            "runtime": runtime_refs[:3],
        },
        "smoke_test_stub": list(template["smoke_test_stub"]),
        "caveat": "This is a scaffold for adapter design. Do not treat it as implemented behavior or approval to execute upstream code.",
    }


def adapter_plan_stubs_for_summary(
    adapter_summary: dict,
    *,
    entrypoint_refs: list[str],
    config_refs: list[str],
    runtime_refs: list[str],
) -> list[dict]:
    command_policies = adapter_summary.get("command_policies", [])
    adapter_types = [
        policy["adapter_type"]
        for policy in adapter_summary.get("policies", [])
        if policy.get("adapter_type")
    ]
    if not adapter_types and (entrypoint_refs or runtime_refs):
        adapter_types = ["no-adapter-until-review"]
    return [
        adapter_plan_stub_for_policy(
            adapter_type,
            command_policies=command_policies,
            entrypoint_refs=entrypoint_refs,
            config_refs=config_refs,
            runtime_refs=runtime_refs,
        )
        for adapter_type in ADAPTER_POLICY_ORDER
        if adapter_type in set(adapter_types)
    ]


def command_evidence_summary(command_evidence: list[dict]) -> dict:
    category_counts = {category: 0 for category in SIDE_EFFECT_CATEGORY_ORDER}
    gate_counts = {gate: 0 for gate in EXECUTION_GATE_ORDER}
    review_required_count = 0
    for item in command_evidence:
        if item.get("review_required"):
            review_required_count += 1
        for category in item.get("side_effect_categories", []):
            category_counts[category] = category_counts.get(category, 0) + 1
        gate = item.get("execution_gate", {}).get("gate")
        if gate:
            gate_counts[gate] = gate_counts.get(gate, 0) + 1
    categories = [
        {
            "category": category,
            "count": count,
            "commands": [
                item["command"]
                for item in command_evidence
                if category in item.get("side_effect_categories", [])
            ][:5],
        }
        for category, count in category_counts.items()
        if count
    ]
    highest_risk = "none"
    for category in ["install", "download", "network-access", "gpu-or-model-execution", "file-write", "unknown-review-required"]:
        if category_counts.get(category, 0):
            highest_risk = category
            break
    execution_gates = [
        {
            "gate": gate,
            "count": count,
            "commands": [
                item["command"]
                for item in command_evidence
                if item.get("execution_gate", {}).get("gate") == gate
            ][:5],
        }
        for gate, count in gate_counts.items()
        if count
    ]
    adapter_summary = adapter_policy_summary(command_evidence)
    return {
        "total_commands": len(command_evidence),
        "review_required_count": review_required_count,
        "read_only_inspection_count": category_counts.get("read-only-inspection", 0),
        "highest_risk_category": highest_risk,
        "categories": categories,
        "execution_gates": execution_gates,
        "adapter_policies": adapter_summary["policies"],
        "highest_adapter_policy": adapter_summary["highest_policy"],
        "recommended_adapter_policy": adapter_summary["recommended_policy"],
        "adapter_recommendation_basis": adapter_summary["recommendation_basis"],
        "adapter_policies_ignored_for_recommendation": adapter_summary["ignored_for_recommendation"],
        "caveat": "Side-effect categories are heuristic triage labels and must be confirmed by source review.",
    }


def markdown_heading(stripped_line: str) -> str:
    if not stripped_line.startswith("#"):
        return ""
    match = re.match(r"^(#{1,6})\s+(.+?)\s*#*$", stripped_line)
    if not match:
        return ""
    return match.group(2).strip()


def notebook_source_lines(source: object) -> list[str]:
    if isinstance(source, list):
        return [str(line).rstrip("\n") for line in source]
    if isinstance(source, str):
        return source.splitlines()
    return []


def notebook_command_evidence_for_file(path: Path, root: Path, *, limit: int = 8) -> list[dict]:
    rel = rel_posix(path, root)
    try:
        if path.stat().st_size > 1_000_000:
            return []
        notebook = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except (OSError, json.JSONDecodeError):
        return []

    cells = notebook.get("cells", [])
    if not isinstance(cells, list):
        return []

    evidence: list[dict] = []
    seen: set[tuple[str, int]] = set()
    current_heading = ""

    def add(command: str, cell_number: int, snippet: str, source_type: str, source_heading: str = "") -> None:
        clean = normalized_command_line(command)
        if not clean:
            return
        if not clean.lower().startswith(COMMAND_STARTERS):
            return
        key = (clean, cell_number)
        if key in seen:
            return
        seen.add(key)
        risk, notes = side_effect_risk_for_command(clean)
        categories = side_effect_categories_for_command(clean)
        evidence.append(
            {
                "command": clean,
                "source_path": rel,
                "line": cell_number,
                "snippet": snippet.strip()[:240],
                "source_heading": source_heading,
                "source_type": source_type,
                "platform_assumption": platform_assumption_for_command(clean),
                "side_effect_risk": risk,
                "side_effect_categories": categories,
                "side_effect_notes": notes,
                "review_required": risk != "low-readonly-help",
            }
        )

    for cell_number, cell in enumerate(cells, start=1):
        if not isinstance(cell, dict):
            continue
        cell_type = str(cell.get("cell_type", ""))
        lines = notebook_source_lines(cell.get("source"))
        if cell_type == "markdown":
            for line in lines:
                heading = markdown_heading(line.strip())
                if heading:
                    current_heading = heading
            continue
        if cell_type != "code":
            continue
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(("!", "%")):
                stripped = stripped[1:].strip()
            add(stripped, cell_number, line, f"notebook-code-cell:{cell_number}", current_heading)
            if len(evidence) >= limit:
                return evidence[:limit]

    return evidence[:limit]


def command_evidence_for_file(path: Path, root: Path, *, limit: int = 8) -> list[dict]:
    rel = rel_posix(path, root)
    if path.suffix.lower() == ".ipynb":
        return notebook_command_evidence_for_file(path, root, limit=limit)

    text = text_sample(path)
    if not text:
        return []
    evidence: list[dict] = []
    seen: set[tuple[str, int]] = set()

    def add(command: str, line_number: int, snippet: str, source_type: str, source_heading: str = "") -> None:
        clean = normalized_command_line(command)
        if not clean:
            return
        if not clean.lower().startswith(COMMAND_STARTERS):
            return
        key = (clean, line_number)
        if key in seen:
            return
        seen.add(key)
        risk, notes = side_effect_risk_for_command(clean)
        categories = side_effect_categories_for_command(clean)
        evidence.append(
            {
                "command": clean,
                "source_path": rel,
                "line": line_number,
                "snippet": snippet.strip()[:240],
                "source_heading": source_heading,
                "source_type": source_type,
                "platform_assumption": platform_assumption_for_command(clean),
                "side_effect_risk": risk,
                "side_effect_categories": categories,
                "side_effect_notes": notes,
                "review_required": risk != "low-readonly-help",
            }
        )

    in_fence = False
    fence_language = ""
    current_heading = ""
    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not in_fence:
            heading = markdown_heading(stripped)
            if heading:
                current_heading = heading
                continue
        if stripped.startswith("```"):
            in_fence = not in_fence
            fence_language = stripped[3:].strip().lower() if in_fence else ""
            continue
        source_type = "documented-command" if in_fence else "inline-command"
        if in_fence and fence_language and fence_language not in {"bash", "sh", "shell", "text", "powershell", "pwsh", "python", "console"}:
            continue
        add(stripped, line_number, line, source_type, current_heading)
        if len(evidence) >= limit:
            break

    if path.suffix.lower() == ".py" and len(evidence) < limit:
        lines = text.splitlines()
        for line_number, line in enumerate(lines, start=1):
            for framework, pattern in PYTHON_CLI_PATTERNS:
                if pattern in line:
                    command = f"python {rel} --help"
                    risk, notes = side_effect_risk_for_command(command)
                    categories = side_effect_categories_for_command(command)
                    evidence.append(
                        {
                            "command": command,
                            "source_path": rel,
                            "line": line_number,
                            "snippet": line.strip()[:240],
                            "source_heading": "",
                            "source_type": f"python-cli-framework:{framework}",
                            "platform_assumption": "python-environment",
                            "side_effect_risk": risk,
                            "side_effect_categories": categories,
                            "side_effect_notes": notes,
                            "review_required": True,
                        }
                    )
                    break
            if len(evidence) >= limit:
                break

    return evidence[:limit]


def healthcare_signals_for_file(path: Path, root: Path) -> list[HealthcareSignal]:
    rel = rel_posix(path, root)
    haystack = f"{rel}\n{text_sample(path)}".lower()
    signals: list[HealthcareSignal] = []
    for signal_type, terms in HEALTHCARE_SIGNAL_RULES.items():
        for term in terms:
            if term in haystack:
                signals.append(
                    HealthcareSignal(
                        path=rel,
                        signal_type=signal_type,
                        signal=term,
                        evidence="path-or-text-sample",
                    )
                )
    return signals


def summarize_healthcare_signals(signals: list[HealthcareSignal]) -> list[dict]:
    summary: list[dict] = []
    for signal_type in sorted({signal.signal_type for signal in signals}):
        matches = [signal for signal in signals if signal.signal_type == signal_type]
        signal_terms = sorted({signal.signal for signal in matches})
        files_to_review = sorted({signal.path for signal in matches})
        summary.append(
            {
                "signal_type": signal_type,
                "count": len(matches),
                "signals": signal_terms[:12],
                "files_to_review": files_to_review[:12],
                "review_note": "Read these files before making capability, modality, runtime, safety, model, dataset, or clinical-use claims.",
            }
        )
    return summary


def related_source_context(signal_type: str, source_context_map: list[dict]) -> list[dict]:
    related: list[dict] = []
    source_rows = {row["category"]: row for row in source_context_map}
    for category in HEALTHCARE_READING_SOURCE_CATEGORIES.get(signal_type, []):
        row = source_rows.get(category)
        if not row or not row.get("artifacts"):
            continue
        related.append(
            {
                "category": category,
                "label": row["label"],
                "why": row["what_it_provides"],
                "artifacts": [artifact["path"] for artifact in row["artifacts"][:8]],
            }
        )
    return related


def clipped_snippet(value: str, max_chars: int = 180) -> str:
    snippet = " ".join(value.strip().split())
    if len(snippet) <= max_chars:
        return snippet
    return snippet[: max_chars - 3].rstrip() + "..."


def evidence_hints_for_signals(signals: list[HealthcareSignal], root: Path, signal_type: str, max_hints: int = 6) -> list[dict]:
    hints: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for signal in signals:
        if signal.signal_type != signal_type:
            continue
        key = (signal.path, signal.signal)
        if key in seen:
            continue
        seen.add(key)
        hint = {
            "path": signal.path,
            "matched_signal": signal.signal,
            "source": "path-or-text-sample",
            "line": None,
            "snippet": "Inspect this file for the scanner-detected healthcare signal.",
            "caveat": "Snippet is a navigation aid only; read the source file before making claims.",
        }
        path = root / Path(signal.path)
        if signal.signal.lower() in signal.path.lower():
            hint["source"] = "path"
            hint["snippet"] = "Signal matched the file path; inspect this artifact directly."
        elif path.suffix.lower() in TEXT_SAMPLE_SUFFIXES:
            try:
                if path.stat().st_size <= 1_000_000:
                    for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
                        if signal.signal.lower() in line.lower():
                            hint["source"] = "text-line"
                            hint["line"] = line_number
                            hint["snippet"] = clipped_snippet(line)
                            break
            except OSError:
                hint["source"] = "unreadable"
                hint["snippet"] = "File could not be read for a line hint; inspect manually if available."
        else:
            hint["source"] = "non-text-or-large-file"
            hint["snippet"] = "Signal was detected from the file path or limited sampling; content was not line-sampled."
        hints.append(hint)
        if len(hints) >= max_hints:
            break
    return hints


def build_healthcare_reading_plan(
    summary: list[dict],
    source_context_map: list[dict],
    signals: list[HealthcareSignal],
    root: Path,
) -> list[dict]:
    plan: list[dict] = []
    for signal_type in HEALTHCARE_READING_GUIDANCE:
        row = next((item for item in summary if item["signal_type"] == signal_type), None)
        if not row:
            continue
        guidance = HEALTHCARE_READING_GUIDANCE[signal_type]
        plan.append(
            {
                "priority": len(plan) + 1,
                "signal_type": signal_type,
                "review_area": guidance["review_area"],
                "why": guidance["why"],
                "files_to_review": row["files_to_review"],
                "evidence_hints": evidence_hints_for_signals(signals, root, signal_type),
                "related_source_context": related_source_context(signal_type, source_context_map),
                "questions": guidance["questions"],
                "claim_boundary": guidance["claim_boundary"],
            }
        )
    return plan


def source_context_refs_for_hypothesis(source_context_map: list[dict]) -> list[dict]:
    rows = {row["category"]: row for row in source_context_map}
    refs: list[dict] = []
    for category in HYPOTHESIS_SOURCE_CATEGORIES:
        row = rows.get(category)
        if not row or not row.get("artifacts"):
            continue
        refs.append(
            {
                "category": category,
                "label": row["label"],
                "artifacts": [artifact["path"] for artifact in row["artifacts"][:5]],
            }
        )
    return refs


def healthcare_review_refs_for_hypothesis(reading_plan: list[dict]) -> list[dict]:
    refs: list[dict] = []
    for row in reading_plan:
        refs.append(
            {
                "signal_type": row["signal_type"],
                "review_area": row["review_area"],
                "files_to_review": row["files_to_review"][:5],
                "claim_boundary": row["claim_boundary"],
            }
        )
    return refs


def source_coverage_for_hypothesis(source_context_map: list[dict]) -> dict:
    rows = {row["category"]: row for row in source_context_map}
    areas: list[dict] = []
    for area in HYPOTHESIS_COVERAGE_AREAS:
        artifacts: list[str] = []
        for category in area["categories"]:
            row = rows.get(category)
            if not row:
                continue
            artifacts.extend(artifact["path"] for artifact in row.get("artifacts", [])[:3])
        present = bool(artifacts)
        areas.append(
            {
                "id": area["id"],
                "label": area["label"],
                "present": present,
                "artifacts": artifacts[:5],
            }
        )
    present_count = sum(1 for area in areas if area["present"])
    total = len(areas)
    if present_count >= 7:
        status = "strong-source-coverage"
    elif present_count >= 5:
        status = "moderate-source-coverage"
    else:
        status = "weak-source-coverage"
    return {
        "present_count": present_count,
        "total": total,
        "status": status,
        "present": [area["label"] for area in areas if area["present"]],
        "missing": [area["label"] for area in areas if not area["present"]],
        "areas": areas,
        "caveat": "Coverage means relevant artifact types were detected, not that the hypothesis is validated.",
    }


def artifacts_for_category(source_context_map: list[dict], category: str, limit: int = 5) -> list[dict]:
    row = next((item for item in source_context_map if item["category"] == category), None)
    if not row:
        return []
    return row.get("artifacts", [])[:limit]


def entrypoint_review_command(path: str) -> dict:
    suffix = Path(path).suffix.lower()
    if suffix == ".py":
        command = f"python {path} --help"
    elif suffix == ".ps1":
        command = f"pwsh -File {path} -Help"
    elif suffix == ".sh":
        command = f"sh {path} --help"
    elif suffix == ".ipynb":
        command = f"jupyter nbconvert --to notebook --execute {path}"
    else:
        command = f"review {path}"
    return {
        "purpose": f"Inspect whether `{path}` exposes a usable CLI or workflow entrypoint.",
        "command": command,
        "side_effects": "unknown until source review; do not run blindly",
        "adapter_policy": {
            **adapter_policy_for_gate("do-not-run-from-scanner"),
            "source_path": path,
        },
        "review_required": True,
        "source_path": path,
    }


def provisional_cli_draft_for_hypothesis(
    source_context_map: list[dict],
    command_evidence: list[dict],
    *,
    candidate_terms: list[str] | tuple[str, ...] | set[str] | None = None,
    workflow_goal_terms: list[str] | tuple[str, ...] | set[str] | None = None,
) -> dict:
    entrypoints = artifacts_for_category(source_context_map, "scripts_apis_notebooks")
    configs = artifacts_for_category(source_context_map, "configs_metadata_labels", limit=3)
    runtime = artifacts_for_category(source_context_map, "dependencies_runtime", limit=3)
    entrypoint_refs = [artifact["path"] for artifact in entrypoints]
    config_refs = [artifact["path"] for artifact in configs]
    runtime_refs = [artifact["path"] for artifact in runtime]
    if command_evidence:
        status = "source-grounded-commands-detected"
        summary = "Drafted from documented command snippets or Python CLI framework clues. Verify syntax, side effects, runtime requirements, and examples before using."
    elif entrypoints:
        status = "provisional-entrypoints-detected"
        summary = "Drafted from detected scripts, APIs, notebooks, or bundle-like files. Verify syntax, side effects, runtime requirements, and examples before using."
    else:
        status = "needs-entrypoint-discovery"
        summary = "No executable entrypoint artifacts were detected. Review README, docs, and source files before proposing a CLI."

    commands = [
        {
            "purpose": "Collect deterministic source evidence before creating or running a skill adapter.",
            "command": 'python -m skillforge codebase-scan <repo-path> --workflow-goal "<workflow goal>" --output-dir <output-dir> --json',
            "side_effects": "read-only scan plus explicit output directory writes",
            "review_required": False,
            "source_path": None,
        }
    ]
    candidate_command_evidence = candidate_relevant_command_evidence(
        command_evidence,
        candidate_terms=candidate_terms,
        workflow_goal_terms=workflow_goal_terms,
    )
    commands.extend(
        {
            "purpose": f"Review source-grounded command from `{item['source_path']}` line {item['line']}.",
            "command": item["command"],
            "side_effects": item["side_effect_notes"],
            "side_effect_risk": item["side_effect_risk"],
            "side_effect_categories": item.get("side_effect_categories", []),
            "execution_gate": item.get("execution_gate", {}),
            "adapter_policy": adapter_policy_for_command(item),
            "candidate_relevance": item.get("candidate_relevance", {}),
            "platform_assumption": item["platform_assumption"],
            "review_required": item["review_required"],
            "source_path": item["source_path"],
            "source_line": item["line"],
            "source_heading": item.get("source_heading", ""),
            "source_type": item["source_type"],
            "snippet": item["snippet"],
        }
        for item in candidate_command_evidence[:5]
    )
    if not command_evidence:
        commands.extend(entrypoint_review_command(artifact["path"]) for artifact in entrypoints[:3])
    adapter_summary = adapter_policy_summary(
        command_evidence,
        candidate_terms=candidate_terms,
        workflow_goal_terms=workflow_goal_terms,
    )
    if not command_evidence and entrypoints:
        policy = adapter_policy_for_gate("do-not-run-from-scanner")
        adapter_summary = {
            "highest_policy": policy["adapter_type"],
            "policies": [
                {
                    "adapter_type": policy["adapter_type"],
                    "count": len(entrypoints[:3]),
                    "commands": [entrypoint_review_command(artifact["path"])["command"] for artifact in entrypoints[:3]],
                }
            ],
            "command_policies": [
                {
                    **policy,
                    "source_command": entrypoint_review_command(artifact["path"])["command"],
                    "source_path": artifact["path"],
                    "source_line": None,
                    "side_effect_categories": ["unknown-review-required"],
                }
                for artifact in entrypoints[:3]
            ],
            "caveat": "Entrypoint-derived adapter policies require source review before any runnable wrapper is designed.",
        }
    adapter_plan_stubs = adapter_plan_stubs_for_summary(
        adapter_summary,
        entrypoint_refs=entrypoint_refs,
        config_refs=config_refs,
        runtime_refs=runtime_refs,
    )
    return {
        "status": status,
        "summary": summary,
        "entrypoint_refs": entrypoint_refs,
        "config_refs": config_refs,
        "runtime_refs": runtime_refs,
        "source_command_refs": candidate_command_evidence[:8],
        "adapter_policy_summary": adapter_summary,
        "recommended_adapter_policy": adapter_summary["recommended_policy"],
        "adapter_plan_stubs": adapter_plan_stubs,
        "suggested_commands": commands,
        "caveat": "These are review prompts and adapter-design hints. They are not validated run commands.",
    }


def slugify(value: str) -> str:
    slug = []
    previous_dash = False
    for char in value.lower():
        if char.isalnum():
            slug.append(char)
            previous_dash = False
        elif not previous_dash:
            slug.append("-")
            previous_dash = True
    return "".join(slug).strip("-")


def build_candidate_skill_hypotheses(
    source_context_map: list[dict],
    healthcare_signal_summary: list[dict],
    healthcare_reading_plan: list[dict],
    command_evidence: list[dict],
    workflow_goal: str = "",
    source_project_name: str = "",
) -> list[dict]:
    task_summary = next((row for row in healthcare_signal_summary if row["signal_type"] == "task_or_output"), None)
    if not task_summary:
        return []
    task_terms = set(task_summary["signals"])
    hypotheses: list[dict] = []
    source_refs = source_context_refs_for_hypothesis(source_context_map)
    review_refs = healthcare_review_refs_for_hypothesis(healthcare_reading_plan)
    source_coverage = source_coverage_for_hypothesis(source_context_map)
    workflow_goal_lower = workflow_goal.lower()
    for order, (term, details) in enumerate(TASK_HYPOTHESIS_LABELS.items()):
        if term not in task_terms:
            continue
        candidate_name = source_scoped_candidate_name(details["name"], source_project_name)
        goal_terms = [term, *details.get("goal_terms", [])]
        matched_goal_terms = sorted({goal_term for goal_term in goal_terms if goal_term and goal_term in workflow_goal_lower})
        goal_match_score = len(matched_goal_terms)
        provisional_cli_draft = provisional_cli_draft_for_hypothesis(
            source_context_map,
            command_evidence,
            candidate_terms=goal_terms,
            workflow_goal_terms=matched_goal_terms,
        )
        hypotheses.append(
            {
                "hypothesis_id": slugify(candidate_name),
                "candidate_skill": candidate_name,
                "generic_candidate_skill": details["name"],
                "source_project_name": source_project_name,
                "provisional": True,
                "workflow_goal_match_score": goal_match_score,
                "workflow_goal_match_terms": matched_goal_terms,
                "recommendation": "provisional-needs-source-review",
                "why_it_might_be_useful": "Scanner found medical-imaging task/output signals and supporting source-context artifacts that may justify a SkillForge skill after review.",
                "sample_prompt_call": details["prompt"],
                "proposed_cli_contract": "TBD after source review; start with check and plan commands, and add guarded run commands only when source entrypoints, runtime requirements, and smoke-test evidence support execution.",
                "provisional_cli_draft": provisional_cli_draft,
                "source_coverage": source_coverage,
                "source_context_refs": source_refs,
                "healthcare_review_refs": review_refs,
                "caveat": "Scanner-generated hypothesis. It is not a publishable skill recommendation until a human or LLM reads the cited source files and confirms scope, runtime, safety, license, and examples.",
                "_source_order": order,
            }
        )
    hypotheses = sorted(hypotheses, key=lambda item: (-item["workflow_goal_match_score"], item["_source_order"]))[:4]
    for hypothesis in hypotheses:
        hypothesis.pop("_source_order", None)
    return hypotheses


def source_scoped_candidate_name(generic_name: str, source_project_name: str) -> str:
    source_project_name = source_project_name.strip()
    if not source_project_name:
        return generic_name
    suffix = re.sub(r"^Research\s+", "", generic_name, flags=re.IGNORECASE).strip()
    if not suffix:
        return generic_name
    if source_project_name.lower() in suffix.lower():
        return generic_name
    return f"{source_project_name} {suffix}"


def git_result(git: str, root: Path, args: list[str], *, safe_directory: bool = False) -> subprocess.CompletedProcess[str]:
    command = [git]
    if safe_directory:
        command.extend(["-c", f"safe.directory={root.as_posix()}"])
    command.extend(["-C", str(root), *args])
    return subprocess.run(
        command,
        capture_output=True,
        check=False,
        text=True,
        timeout=10,
    )


def git_text(git: str, root: Path, args: list[str], *, safe_directory: bool) -> str | None:
    try:
        result = git_result(git, root, args, safe_directory=safe_directory)
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value or None


def git_dirty(git: str, root: Path, *, safe_directory: bool) -> bool | None:
    try:
        result = git_result(git, root, ["status", "--porcelain"], safe_directory=safe_directory)
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    return bool(result.stdout.strip())


def source_version_metadata(root: Path) -> dict[str, str | bool | None]:
    git = shutil.which("git")
    if not git:
        return {
            "commit": None,
            "branch": None,
            "remote_url": None,
            "dirty": None,
            "status": "git-not-found",
            "safe_directory_override": False,
        }
    try:
        result = git_result(git, root, ["rev-parse", "HEAD"])
    except (OSError, subprocess.SubprocessError) as exc:
        return {
            "commit": None,
            "branch": None,
            "remote_url": None,
            "dirty": None,
            "status": f"git-error:{exc}",
            "safe_directory_override": False,
        }
    safe_directory_override = False
    if result.returncode != 0:
        combined_error = f"{result.stderr}\n{result.stdout}".lower()
        if "dubious ownership" in combined_error or "safe.directory" in combined_error:
            try:
                safe_result = git_result(git, root, ["rev-parse", "HEAD"], safe_directory=True)
            except (OSError, subprocess.SubprocessError) as exc:
                return {
                    "commit": None,
                    "branch": None,
                    "remote_url": None,
                    "dirty": None,
                    "status": f"git-error:{exc}",
                    "safe_directory_override": True,
                }
            if safe_result.returncode == 0:
                result = safe_result
                safe_directory_override = True
        if result.returncode != 0:
            return {
                "commit": None,
                "branch": None,
                "remote_url": None,
                "dirty": None,
                "status": "not-a-git-repo",
                "safe_directory_override": False,
                "git_error": result.stderr.strip() or result.stdout.strip(),
            }
    branch = git_text(git, root, ["rev-parse", "--abbrev-ref", "HEAD"], safe_directory=safe_directory_override)
    remote_url = git_text(git, root, ["config", "--get", "remote.origin.url"], safe_directory=safe_directory_override)
    dirty = git_dirty(git, root, safe_directory=safe_directory_override)
    if branch == "HEAD":
        branch = None
    return {
        "commit": result.stdout.strip(),
        "branch": branch,
        "remote_url": remote_url,
        "dirty": dirty,
        "status": "ok-safe-directory-override" if safe_directory_override else "ok",
        "safe_directory_override": safe_directory_override,
    }


def git_commit(root: Path) -> dict[str, str | bool | None]:
    return source_version_metadata(root)


def scan_repo(root: Path, workflow_goal: str, max_files_per_category: int, max_total_files: int) -> dict:
    root = root.resolve()
    if not root.exists() or not root.is_dir():
        return {
            "ok": False,
            "error": f"Repo path does not exist or is not a directory: {root}",
            "repo_path": str(root),
        }

    category_artifacts: dict[str, list[Artifact]] = {category: [] for category in CATEGORY_GUIDANCE}
    healthcare_signals: list[HealthcareSignal] = []
    command_evidence: list[dict] = []
    files = iter_repo_files(root, max_total_files=max_total_files)
    files_scanned = 0
    files_matched = 0

    for path in files:
        files_scanned += 1
        categories = classify_file(path, root)
        if len(command_evidence) < max_files_per_category * 3:
            command_evidence.extend(command_evidence_for_file(path, root, limit=3))
        file_healthcare_signals = healthcare_signals_for_file(path, root)
        if file_healthcare_signals and len(healthcare_signals) < max_files_per_category * 3:
            healthcare_signals.extend(file_healthcare_signals)
        if not categories and not file_healthcare_signals:
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

    healthcare_signal_summary = summarize_healthcare_signals(healthcare_signals)
    healthcare_reading_plan = build_healthcare_reading_plan(healthcare_signal_summary, source_context_map, healthcare_signals, root)
    command_evidence = command_evidence[: max_files_per_category * 3]
    healthcare_context = bool(healthcare_signal_summary)
    command_evidence = apply_execution_gates(command_evidence, healthcare_context=healthcare_context)
    command_summary = command_evidence_summary(command_evidence)
    candidate_skill_hypotheses = build_candidate_skill_hypotheses(
        source_context_map,
        healthcare_signal_summary,
        healthcare_reading_plan,
        command_evidence,
        workflow_goal=workflow_goal,
        source_project_name=root.name,
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
        "healthcare_signals": [signal.__dict__ for signal in healthcare_signals],
        "healthcare_signal_summary": healthcare_signal_summary,
        "healthcare_reading_plan": healthcare_reading_plan,
        "command_evidence": command_evidence,
        "command_evidence_summary": command_summary,
        "candidate_skill_hypotheses": candidate_skill_hypotheses,
        "next_steps": [
            "Review the source-context map and add human notes for what each artifact contributes.",
            "If healthcare_reading_plan is present, use it before making modality, runtime, safety, model, dataset, or clinical-use claims.",
            "Review any candidate_skill_hypotheses before creating a candidate skill table.",
            "Create readiness cards before generating SkillForge skill files.",
            "Separate LLM decisions from deterministic Python checks before writing adapters.",
        ],
    }


def table_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br>")


def source_version_markdown_lines(source_version: dict) -> list[str]:
    dirty = source_version.get("dirty")
    if dirty is True:
        dirty_text = "yes"
    elif dirty is False:
        dirty_text = "no"
    else:
        dirty_text = "unknown"
    return [
        f"Source version status: `{source_version.get('status') or 'unknown'}`",
        f"Source commit: `{source_version.get('commit') or 'unknown'}`",
        f"Source branch: `{source_version.get('branch') or 'unknown'}`",
        f"Source remote: `{source_version.get('remote_url') or 'unknown'}`",
        f"Source dirty worktree: {dirty_text}",
        f"Used safe.directory override: {bool(source_version.get('safe_directory_override'))}",
    ]


def inline_code_items(items: list[str], limit: int = 3) -> str:
    selected = [item for item in items if item][:limit]
    if not selected:
        return "None"
    suffix = "" if len(items) <= limit else f" plus {len(items) - limit} more"
    return ", ".join(f"`{item}`" for item in selected) + suffix


def render_candidate_review_summary(hypothesis: dict, index: int) -> list[str]:
    coverage = hypothesis["source_coverage"]
    cli_draft = hypothesis["provisional_cli_draft"]
    source_refs = hypothesis.get("source_context_refs", [])
    healthcare_refs = hypothesis.get("healthcare_review_refs", [])
    first_source_ref = source_refs[0] if source_refs else {}
    first_healthcare_ref = healthcare_refs[0] if healthcare_refs else {}
    adapter_policy = cli_draft.get("recommended_adapter_policy", "none")
    adapter_summary = cli_draft.get("adapter_policy_summary", {})
    adapter_basis = adapter_summary.get("recommendation_basis", "all-command-evidence")
    ignored = adapter_summary.get("ignored_for_recommendation", [])
    goal_terms = ", ".join(hypothesis.get("workflow_goal_match_terms", [])) or "none"
    lines = [
        f"### {index}. {hypothesis['candidate_skill']}",
        "",
        f"- Recommendation: `{hypothesis['recommendation']}`",
        f"- Source coverage: {coverage['present_count']}/{coverage['total']} (`{coverage['status']}`)",
        f"- Missing evidence areas: {', '.join(coverage['missing']) or 'None'}",
        f"- Workflow-goal match terms: {goal_terms}",
        f"- Why it might be useful: {hypothesis['why_it_might_be_useful']}",
        f"- Sample prompt: {hypothesis['sample_prompt_call']}",
        f"- Proposed CLI contract: {hypothesis['proposed_cli_contract']}",
        f"- Recommended adapter policy: `{adapter_policy}`",
        f"- Adapter recommendation basis: `{adapter_basis}`",
        f"- First source-context review: {first_source_ref.get('label', 'None')} - "
        f"{inline_code_items(first_source_ref.get('artifacts', []))}",
        f"- First healthcare review: {first_healthcare_ref.get('review_area', 'None')} - "
        f"{inline_code_items(first_healthcare_ref.get('files_to_review', []))}",
        f"- Caveat: {hypothesis['caveat']}",
        "",
    ]
    if ignored:
        insert_at = -2
        lines.insert(
            insert_at,
            "- Ignored for candidate adapter recommendation: "
            + "; ".join(
                f"`{item.get('source_path')}` `{item.get('command')}` ({item.get('reason')})"
                for item in ignored[:3]
            ),
        )
    return lines


def render_source_context_markdown(payload: dict) -> str:
    lines = [
        "# Source Context Map",
        "",
        f"Repo path: `{payload['repo_path']}`",
        f"Workflow goal: {payload.get('workflow_goal') or 'Not provided'}",
        f"Scanned at: {payload['scanned_at']}",
        *source_version_markdown_lines(payload.get("source_version", {})),
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
    healthcare_signal_summary = payload.get("healthcare_signal_summary", [])
    if healthcare_signal_summary:
        lines.extend(
            [
                "",
                "## Healthcare Signal Summary",
                "",
                "Use this grouped summary to decide which medical-imaging evidence to read first. It is a triage aid, not a claim that the repo supports a capability.",
                "",
                "| Signal type | Count | Signals | Files to review | Review note |",
                "| --- | ---: | --- | --- | --- |",
            ]
        )
        for row in healthcare_signal_summary:
            lines.append(
                "| "
                + " | ".join(
                    [
                        table_cell(row["signal_type"]),
                        str(row["count"]),
                        table_cell(", ".join(row["signals"])),
                        table_cell("<br>".join(f"`{path}`" for path in row["files_to_review"])),
                        table_cell(row["review_note"]),
                    ]
                )
                + " |"
            )
    healthcare_reading_plan = payload.get("healthcare_reading_plan", [])
    if healthcare_reading_plan:
        lines.extend(
            [
                "",
                "## Healthcare Reading Plan",
                "",
                "Use this checklist before proposing candidate medical AI skills. Each item is scanner-generated and must be confirmed by reading the listed source files.",
            ]
        )
        for row in healthcare_reading_plan:
            lines.extend(
                [
                    "",
                    f"### {row['priority']}. {row['review_area']}",
                    "",
                    f"- Signal type: `{row['signal_type']}`",
                    f"- Why it matters: {row['why']}",
                    "- Files to review:",
                ]
            )
            for path in row["files_to_review"]:
                lines.append(f"  - `{path}`")
            if row.get("evidence_hints"):
                lines.append("- Evidence hints:")
                for hint in row["evidence_hints"]:
                    location = f"`{hint['path']}`"
                    if hint.get("line"):
                        location = f"`{hint['path']}:{hint['line']}`"
                    lines.append(f"  - {location} matched `{hint['matched_signal']}` ({hint['source']}): {hint['snippet']}")
            if row.get("related_source_context"):
                lines.append("- Related source context:")
                for context in row["related_source_context"]:
                    artifacts = ", ".join(f"`{path}`" for path in context["artifacts"])
                    lines.append(f"  - {context['label']}: {artifacts}")
            lines.append("- Questions:")
            for question in row["questions"]:
                lines.append(f"  - {question}")
            lines.append(f"- Claim boundary: {row['claim_boundary']}")
    command_evidence = payload.get("command_evidence", [])
    if command_evidence:
        summary = payload.get("command_evidence_summary", {})
        if summary:
            lines.extend(
                [
                    "",
                    "## Command Evidence Summary",
                    "",
                    f"- Total commands: {summary['total_commands']}",
                    f"- Review required: {summary['review_required_count']}",
                    f"- Read-only inspection: {summary['read_only_inspection_count']}",
                    f"- Highest risk category: `{summary['highest_risk_category']}`",
                    "- Category counts:",
                ]
            )
            for category in summary["categories"]:
                commands = ", ".join(f"`{command}`" for command in category["commands"])
                lines.append(f"  - `{category['category']}`: {category['count']} ({commands})")
            if summary.get("execution_gates"):
                lines.append("- Execution gates:")
                for gate in summary["execution_gates"]:
                    commands = ", ".join(f"`{command}`" for command in gate["commands"])
                    lines.append(f"  - `{gate['gate']}`: {gate['count']} ({commands})")
            if summary.get("adapter_policies"):
                lines.append("- Adapter policies:")
                for policy in summary["adapter_policies"]:
                    commands = ", ".join(f"`{command}`" for command in policy["commands"])
                    lines.append(f"  - `{policy['adapter_type']}`: {policy['count']} ({commands})")
                lines.append(f"- Highest adapter policy: `{summary['highest_adapter_policy']}`")
                lines.append(
                    f"- Recommended candidate adapter policy: `{summary.get('recommended_adapter_policy', summary['highest_adapter_policy'])}`"
                )
                lines.append(f"- Adapter recommendation basis: `{summary.get('adapter_recommendation_basis', 'all-command-evidence')}`")
                ignored = summary.get("adapter_policies_ignored_for_recommendation", [])
                if ignored:
                    lines.append("- Ignored for candidate recommendation:")
                    for item in ignored:
                        lines.append(
                            f"  - `{item.get('source_path')}` `{item.get('command')}` ({item.get('reason')})"
                        )
            lines.append(f"- Caveat: {summary['caveat']}")
        lines.extend(
            [
                "",
                "## Command Evidence",
                "",
                "These commands were extracted from source snippets or Python CLI framework clues. They are review targets, not approved execution steps.",
                "",
                "| Command | Source | Section | Type | Platform | Side-effect risk | Side-effect categories | Execution gate | Adapter policy | Snippet |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for command in command_evidence[:25]:
            source = f"`{command['source_path']}`"
            if command.get("line"):
                source = f"`{command['source_path']}:{command['line']}`"
            gate = command.get("execution_gate", {})
            policy = adapter_policy_for_command(command)
            lines.append(
                "| "
                + " | ".join(
                    [
                        table_cell(f"`{command['command']}`"),
                        table_cell(source),
                        table_cell(command.get("source_heading", "")),
                        table_cell(command["source_type"]),
                        table_cell(command["platform_assumption"]),
                        table_cell(command["side_effect_risk"]),
                        table_cell(", ".join(command.get("side_effect_categories", []))),
                        table_cell(gate.get("gate", "")),
                        table_cell(policy.get("adapter_type", "")),
                        table_cell(command["snippet"]),
                    ]
                )
                + " |"
            )
    healthcare_signals = payload.get("healthcare_signals", [])
    if healthcare_signals:
        lines.extend(
            [
                "",
                "## Healthcare And Medical Imaging Signals",
                "",
                "These signals are deterministic evidence candidates for medical AI repos. Read the files before making claims.",
                "",
                "| Signal type | Signal | Evidence file |",
                "| --- | --- | --- |",
            ]
        )
        for signal in healthcare_signals[:50]:
            lines.append(
                "| "
                + " | ".join(
                    [
                        table_cell(signal["signal_type"]),
                        table_cell(signal["signal"]),
                        table_cell(f"`{signal['path']}`"),
                    ]
                )
                + " |"
            )
    lines.append("")
    lines.append("Review note: this scanner finds evidence candidates. A human or LLM must still read the relevant artifacts before claiming capability, safety, license, or behavior.")
    return "\n".join(lines) + "\n"


def render_candidate_table_markdown(payload: dict) -> str:
    lines = [
        "# Candidate Skill Table",
        "",
        f"Repo path: `{payload['repo_path']}`",
        f"Workflow goal: {payload.get('workflow_goal') or 'Not provided'}",
        "",
        "## Source Provenance",
        "",
        *source_version_markdown_lines(payload.get("source_version", {})),
        "",
        "Fill this table after reviewing the source-context map. Every candidate should cite source evidence.",
        "",
    ]
    hypotheses = payload.get("candidate_skill_hypotheses", [])
    if hypotheses:
        lines.extend(
            [
                "## Candidate Review Summaries",
                "",
                "Use these compact summaries for first-pass human review. The detailed evidence table below keeps the full comparison fields for deeper review and agents.",
                "",
            ]
        )
        for index, hypothesis in enumerate(hypotheses, start=1):
            lines.extend(render_candidate_review_summary(hypothesis, index))
        lines.extend(
            [
                "## Provisional Candidate Skill Hypotheses",
                "",
                "These rows are scanner-generated hypotheses. They are not recommendations to publish a skill until the cited source files are reviewed.",
                "",
                "| Candidate skill | Source coverage | Why it might be useful | Sample prompt call | Proposed CLI contract | Adapter policy | Adapter plan stubs | Provisional CLI draft | Source context refs | Healthcare review refs | Recommendation | Caveat |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for hypothesis in hypotheses:
            coverage = hypothesis["source_coverage"]
            coverage_text = (
                f"{coverage['present_count']}/{coverage['total']} ({coverage['status']})"
                + "<br>Present: "
                + (", ".join(coverage["present"]) or "None")
                + "<br>Missing: "
                + (", ".join(coverage["missing"]) or "None")
            )
            source_refs = "<br>".join(
                f"{ref['label']}: " + ", ".join(f"`{path}`" for path in ref["artifacts"])
                for ref in hypothesis["source_context_refs"][:5]
            )
            review_refs = "<br>".join(
                f"{ref['review_area']}: " + ", ".join(f"`{path}`" for path in ref["files_to_review"][:3])
                for ref in hypothesis["healthcare_review_refs"][:5]
            )
            cli_draft = hypothesis["provisional_cli_draft"]
            cli_commands = "<br>".join(f"`{command['command']}`" for command in cli_draft["suggested_commands"][:4])
            adapter_summary = cli_draft.get("adapter_policy_summary", {})
            adapter_policy_text = (
                f"Recommended: `{cli_draft.get('recommended_adapter_policy', 'none')}`"
                + "<br>Basis: "
                + adapter_summary.get("recommendation_basis", "all-command-evidence")
                + "<br>Policies: "
                + (
                    ", ".join(
                        f"`{policy['adapter_type']}`={policy['count']}"
                        for policy in adapter_summary.get("policies", [])
                    )
                    or "None"
                )
                + "<br>Caveat: "
                + adapter_summary.get("caveat", "")
            )
            ignored = adapter_summary.get("ignored_for_recommendation", [])
            if ignored:
                adapter_policy_text += "<br>Ignored for recommendation: " + ", ".join(
                    f"`{item.get('source_path')}` `{item.get('command')}` ({item.get('reason')})"
                    for item in ignored[:3]
                )
            adapter_plan_text = "<br>".join(
                (
                    f"{stub['title']} (`{stub['adapter_type']}`)"
                    + "<br>Reviews: "
                    + (", ".join(stub.get("required_reviews", [])) or "Source review")
                    + "<br>Commands: "
                    + ", ".join(f"`{command}`" for command in stub.get("suggested_commands", [])[:2])
                )
                for stub in cli_draft.get("adapter_plan_stubs", [])[:4]
            ) or "None"
            source_commands = "<br>".join(
                f"`{command['source_path']}:{command['line']}`"
                + (f" [{command.get('source_heading')}]" if command.get("source_heading") else "")
                + f" `{command['command']}` {command['side_effect_risk']} ({', '.join(command.get('side_effect_categories', []))}; {command.get('execution_gate', {}).get('gate', 'no-gate')})"
                for command in cli_draft.get("source_command_refs", [])[:4]
            )
            cli_draft_text = (
                f"{cli_draft['status']}<br>{cli_draft['summary']}"
                + "<br>Entrypoints: "
                + (", ".join(f"`{path}`" for path in cli_draft["entrypoint_refs"][:5]) or "None detected")
                + "<br>Runtime refs: "
                + (", ".join(f"`{path}`" for path in cli_draft["runtime_refs"][:3]) or "None detected")
                + "<br>Command evidence: "
                + (source_commands or "None")
                + "<br>Draft commands: "
                + (cli_commands or "None")
            )
            lines.append(
                "| "
                + " | ".join(
                    [
                        table_cell(hypothesis["candidate_skill"]),
                        table_cell(coverage_text),
                        table_cell(hypothesis["why_it_might_be_useful"]),
                        table_cell(hypothesis["sample_prompt_call"]),
                        table_cell(hypothesis["proposed_cli_contract"]),
                        table_cell(adapter_policy_text),
                        table_cell(adapter_plan_text),
                        table_cell(cli_draft_text),
                        table_cell(source_refs),
                        table_cell(review_refs),
                        table_cell(hypothesis["recommendation"]),
                        table_cell(hypothesis["caveat"]),
                    ]
                )
                + " |"
            )
        lines.append("")
        lines.append("Copy a hypothesis into the editable table below only after source review confirms scope, examples, runtime, safety, and license boundaries.")
        lines.append("")

    lines.extend(
        [
            "| Candidate skill | What it does | Why it is useful | Source evidence | Sample prompt call | Proposed CLI contract | Inputs | Outputs | Deterministic entrypoints | LLM context needed | Safety/license notes | Smoke-test source | Recommendation |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            "|  |  |  |  |  |  |  |  |  |  |  |  |  |",
            "",
            "Recommendations: `make-skill-now`, `needs-adapter-first`, `needs-docs-or-examples`, `needs-license-review`, or `not-a-good-skill-yet`.",
            "",
        ]
    )
    return "\n".join(
        lines
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
            "## Source Provenance",
            "",
            *source_version_markdown_lines(payload.get("source_version", {})),
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
            "## Healthcare And Medical Imaging Signals",
            "",
            "Use `healthcare_reading_plan` from `scan.json` and `source-context-map.md` to review healthcare-specific evidence before proposing candidate skills. Include modalities, file formats, MONAI bundles, GPU/runtime requirements, model or dataset cards, and medical-use safety language.",
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


def normalize_adapter_name(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9_]+", "_", value.strip().lower())
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    if not normalized:
        normalized = "adapter"
    if normalized[0].isdigit():
        normalized = f"adapter_{normalized}"
    return normalized


def load_scan_payload(scan_json: Path) -> tuple[dict | None, str | None]:
    try:
        payload = json.loads(scan_json.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, f"Scan JSON not found: {scan_json}"
    except json.JSONDecodeError as exc:
        return None, f"Scan JSON is not valid JSON: {scan_json} ({exc})"
    except OSError as exc:
        return None, f"Could not read scan JSON: {scan_json} ({exc})"
    if not isinstance(payload, dict):
        return None, "Scan JSON must contain a top-level object."
    return payload, None


def candidate_matches_id(candidate: dict, candidate_id: str) -> bool:
    requested = candidate_id.strip().lower()
    requested_normalized = normalize_adapter_name(candidate_id)
    values = [
        candidate.get("candidate_skill"),
        candidate.get("hypothesis_id"),
        candidate.get("skill_id"),
        candidate.get("name"),
    ]
    for value in values:
        if not value:
            continue
        value_text = str(value).strip().lower()
        if value_text == requested or normalize_adapter_name(str(value)) == requested_normalized:
            return True
    return False


def select_candidate_from_scan(
    payload: dict,
    *,
    candidate_id: str | None = None,
    candidate_index: int = 0,
) -> tuple[dict | None, int | None, str | None]:
    candidates = payload.get("candidate_skill_hypotheses", [])
    if not isinstance(candidates, list) or not candidates:
        return None, None, "Scan JSON does not include candidate_skill_hypotheses."
    if candidate_id:
        for index, candidate in enumerate(candidates):
            if isinstance(candidate, dict) and candidate_matches_id(candidate, candidate_id):
                return candidate, index, None
        return (
            None,
            None,
            f"No candidate matched {candidate_id!r}. Available candidates: "
            + ", ".join(
                str(candidate.get("candidate_skill") or candidate.get("hypothesis_id") or index)
                for index, candidate in enumerate(candidates)
                if isinstance(candidate, dict)
            ),
        )
    if candidate_index < 0 or candidate_index >= len(candidates):
        return None, None, f"Candidate index {candidate_index} is out of range for {len(candidates)} candidate(s)."
    candidate = candidates[candidate_index]
    if not isinstance(candidate, dict):
        return None, None, f"Candidate index {candidate_index} is not an object."
    return candidate, candidate_index, None


def select_adapter_plan_stub(
    candidate: dict,
    *,
    adapter_type: str | None = None,
    stub_index: int = 0,
) -> tuple[dict | None, int | None, str | None]:
    cli_draft = candidate.get("provisional_cli_draft", {})
    if not isinstance(cli_draft, dict):
        return None, None, "Selected candidate does not include a provisional_cli_draft object."
    stubs = cli_draft.get("adapter_plan_stubs", [])
    if not isinstance(stubs, list) or not stubs:
        return None, None, "Selected candidate does not include adapter_plan_stubs."

    if adapter_type:
        matching = [
            (index, stub)
            for index, stub in enumerate(stubs)
            if isinstance(stub, dict) and stub.get("adapter_type") == adapter_type
        ]
        if not matching:
            available = sorted({str(stub.get("adapter_type")) for stub in stubs if isinstance(stub, dict) and stub.get("adapter_type")})
            return None, None, f"No adapter_plan_stub matched adapter type {adapter_type!r}. Available types: {', '.join(available)}"
        if stub_index < 0 or stub_index >= len(matching):
            return None, None, f"Stub index {stub_index} is out of range for {len(matching)} matching {adapter_type} stub(s)."
        original_index, stub = matching[stub_index]
        return dict(stub), original_index, None

    recommended = cli_draft.get("recommended_adapter_policy")
    if recommended:
        for index, stub in enumerate(stubs):
            if isinstance(stub, dict) and stub.get("adapter_type") == recommended:
                return dict(stub), index, None

    if stub_index < 0 or stub_index >= len(stubs):
        return None, None, f"Stub index {stub_index} is out of range for {len(stubs)} adapter stub(s)."
    stub = stubs[stub_index]
    if not isinstance(stub, dict):
        return None, None, f"Stub index {stub_index} is not an object."
    return dict(stub), stub_index, None


def derived_adapter_name(candidate: dict, adapter_type: str, explicit_name: str | None = None) -> str:
    if explicit_name:
        return normalize_adapter_name(explicit_name)
    for key in ("candidate_skill", "hypothesis_id", "skill_id", "name"):
        value = candidate.get(key)
        if value:
            base = normalize_adapter_name(str(value))
            if base:
                return normalize_adapter_name(f"{base}_{adapter_type}_adapter")
    return normalize_adapter_name(f"{adapter_type}_adapter")


def adapter_skeleton_source(
    adapter_name: str,
    adapter_type: str,
    plan_stub: dict,
    scaffold_metadata: dict | None = None,
) -> str:
    plan_stub_literal = pformat(plan_stub, width=100, sort_dicts=True)
    scaffold_metadata_literal = pformat(scaffold_metadata or {}, width=100, sort_dicts=True)
    return f'''from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import sys


ADAPTER_NAME = {adapter_name!r}
ADAPTER_TYPE = {adapter_type!r}
REVIEW_ONLY = True
ADAPTER_PLAN_STUB = {plan_stub_literal}
SCAFFOLD_METADATA = {scaffold_metadata_literal}


def print_json(payload: dict) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def schema_payload() -> dict:
    return {{
        "ok": True,
        "adapter_name": ADAPTER_NAME,
        "adapter_type": ADAPTER_TYPE,
        "review_only": REVIEW_ONLY,
        "commands": [
            {{
                "name": "schema",
                "description": "Describe the review-only adapter scaffold.",
                "side_effects": "Read-only.",
                "required_args": [],
                "optional_args": ["--json"],
            }},
            {{
                "name": "check",
                "description": "Check local source path availability without installing dependencies or running source code.",
                "side_effects": "Read-only.",
                "required_args": [],
                "optional_args": ["--source-dir", "--json"],
            }},
            {{
                "name": "setup-plan",
                "description": "Print setup or review steps as data without executing them.",
                "side_effects": "Read-only; no installs, downloads, network calls, model runs, or output writes.",
                "required_args": [],
                "optional_args": ["--source-dir", "--target", "--json"],
            }},
        ],
        "blocked_commands": ["run", "infer", "download", "install"],
        "adapter_plan_stub": ADAPTER_PLAN_STUB,
        "scaffold_metadata": SCAFFOLD_METADATA,
        "caveat": "This scaffold is review-only. Implement and test side-effecting commands separately after source review and approval.",
    }}


def check_payload(source_dir: str | None = None) -> dict:
    source_path = Path(source_dir).expanduser() if source_dir else None
    source_exists = bool(source_path and source_path.exists())
    return {{
        "ok": True,
        "adapter_name": ADAPTER_NAME,
        "adapter_type": ADAPTER_TYPE,
        "review_only": REVIEW_ONLY,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "source_dir": str(source_path) if source_path else None,
        "source_exists": source_exists,
        "ready_for_execution": False,
        "writes": "none",
        "network": "not-used",
        "scaffold_metadata": SCAFFOLD_METADATA,
        "blocked_side_effects": ADAPTER_PLAN_STUB.get("guardrails", []),
        "next_step": "Review source evidence and setup-plan output before implementing any side-effecting adapter command.",
    }}


def setup_plan_payload(source_dir: str | None = None, target: str | None = None) -> dict:
    return {{
        "ok": True,
        "adapter_name": ADAPTER_NAME,
        "adapter_type": ADAPTER_TYPE,
        "review_only": REVIEW_ONLY,
        "approval_required": True,
        "executed": False,
        "source_dir": source_dir,
        "target": target,
        "planned_commands": ADAPTER_PLAN_STUB.get("suggested_commands", []),
        "required_inputs": ADAPTER_PLAN_STUB.get("required_inputs", []),
        "expected_outputs": ADAPTER_PLAN_STUB.get("expected_outputs", []),
        "guardrails": ADAPTER_PLAN_STUB.get("guardrails", []),
        "required_reviews": ADAPTER_PLAN_STUB.get("required_reviews", []),
        "smoke_test_stub": ADAPTER_PLAN_STUB.get("smoke_test_stub", []),
        "source_refs": ADAPTER_PLAN_STUB.get("source_refs", {{}}),
        "scaffold_metadata": SCAFFOLD_METADATA,
        "side_effects_performed": [],
        "caveat": ADAPTER_PLAN_STUB.get("caveat"),
    }}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Review-only SkillForge adapter scaffold.")
    sub = parser.add_subparsers(dest="command", required=True)

    schema = sub.add_parser("schema", help="Describe the scaffold contract")
    schema.add_argument("--json", action="store_true")

    check = sub.add_parser("check", help="Check local source path availability")
    check.add_argument("--source-dir")
    check.add_argument("--json", action="store_true")

    setup_plan = sub.add_parser("setup-plan", help="Print setup steps as data")
    setup_plan.add_argument("--source-dir")
    setup_plan.add_argument("--target")
    setup_plan.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "schema":
        payload = schema_payload()
    elif args.command == "check":
        payload = check_payload(args.source_dir)
    else:
        payload = setup_plan_payload(args.source_dir, args.target)

    if getattr(args, "json", False):
        print_json(payload)
    else:
        print_json(payload)
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
'''


def scaffold_adapter(
    adapter_type: str | None,
    adapter_name: str | None,
    output_dir: Path,
    *,
    force: bool = False,
    from_scan_json: Path | None = None,
    candidate_id: str | None = None,
    candidate_index: int = 0,
    stub_index: int = 0,
) -> dict:
    plan_stub: dict | None = None
    scan_source: dict | None = None
    candidate: dict | None = None

    if from_scan_json:
        scan_payload, error = load_scan_payload(from_scan_json)
        if error:
            return {"ok": False, "error": error}
        assert scan_payload is not None
        candidate, selected_candidate_index, error = select_candidate_from_scan(
            scan_payload,
            candidate_id=candidate_id,
            candidate_index=candidate_index,
        )
        if error:
            return {"ok": False, "error": error}
        assert candidate is not None
        plan_stub, selected_stub_index, error = select_adapter_plan_stub(
            candidate,
            adapter_type=adapter_type,
            stub_index=stub_index,
        )
        if error:
            return {"ok": False, "error": error}
        assert plan_stub is not None
        adapter_type = str(plan_stub.get("adapter_type") or adapter_type or "")
        adapter_name = derived_adapter_name(candidate, adapter_type, adapter_name)
        scan_source = {
            "scan_json": str(from_scan_json),
            "candidate_id": candidate_id,
            "candidate_index": selected_candidate_index,
            "stub_index": selected_stub_index,
            "candidate_skill": candidate.get("candidate_skill"),
            "hypothesis_id": candidate.get("hypothesis_id"),
            "source_version": scan_payload.get("source_version", {}),
        }
    elif not adapter_name:
        return {
            "ok": False,
            "error": "--adapter-name is required when --from-scan-json is not provided.",
        }

    if not adapter_type:
        return {
            "ok": False,
            "error": "adapter_type is required unless --from-scan-json selects an adapter_plan_stub.",
            "allowed_adapter_types": list(ADAPTER_PLAN_STUBS_BY_POLICY),
        }
    if adapter_type not in ADAPTER_PLAN_STUBS_BY_POLICY:
        return {
            "ok": False,
            "error": f"Unknown adapter type: {adapter_type}",
            "allowed_adapter_types": list(ADAPTER_PLAN_STUBS_BY_POLICY),
        }
    assert adapter_name is not None
    normalized_name = normalize_adapter_name(adapter_name)
    if plan_stub is None:
        plan_stub = adapter_plan_stub_for_policy(
            adapter_type,
            command_policies=[],
            entrypoint_refs=[],
            config_refs=[],
            runtime_refs=[],
        )
    scripts_dir = output_dir / "scripts"
    script_path = scripts_dir / f"{normalized_name}.py"
    if script_path.exists() and not force:
        return {
            "ok": False,
            "error": f"Adapter scaffold already exists: {script_path}",
            "next_step": "Re-run with --force to overwrite after reviewing the existing file.",
        }
    scripts_dir.mkdir(parents=True, exist_ok=True)
    scaffold_metadata = {"scan_source": scan_source} if scan_source else {}
    script_path.write_text(
        adapter_skeleton_source(normalized_name, adapter_type, plan_stub, scaffold_metadata),
        encoding="utf-8",
    )
    payload = {
        "ok": True,
        "adapter_name": normalized_name,
        "adapter_type": adapter_type,
        "review_only": True,
        "written_files": {"adapter_script": str(script_path)},
        "supported_commands": ["schema", "check", "setup-plan"],
        "blocked_commands": ["run", "infer", "download", "install"],
        "adapter_plan_stub": plan_stub,
        "next_step": f"Review `{script_path}` and wire it into a skill package only after source evidence confirms the adapter scope.",
    }
    if scan_source:
        payload["from_scan_json"] = scan_source["scan_json"]
        payload["scan_source"] = scan_source
        payload["candidate_skill"] = scan_source.get("candidate_skill")
        payload["hypothesis_id"] = scan_source.get("hypothesis_id")
    return payload


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
            "scaffold-adapter": {
                "description": "Write a review-only Python adapter scaffold from an adapter policy type or a scan.json candidate.",
                "side_effects": "Writes scripts/<adapter-name>.py under the requested output directory. Does not run source code.",
                "required_args": ["--output-dir"],
                "optional_args": [
                    "adapter_type",
                    "--adapter-name",
                    "--from-scan-json",
                    "--candidate-id",
                    "--candidate-index",
                    "--stub-type",
                    "--stub-index",
                    "--force",
                    "--json",
                ],
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
            "healthcare_signals",
            "healthcare_signal_summary",
            "healthcare_reading_plan",
            "command_evidence",
            "command_evidence_summary",
            "candidate_skill_hypotheses",
            "written_files",
            "adapter_plan_stub",
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
    healthcare_signal_summary = payload.get("healthcare_signal_summary", [])
    if healthcare_signal_summary:
        print("Healthcare signal summary:")
        for row in healthcare_signal_summary:
            print(f"- {row['signal_type']}: {row['count']} signal(s), {len(row['files_to_review'])} file(s) to review")
    healthcare_reading_plan = payload.get("healthcare_reading_plan", [])
    if healthcare_reading_plan:
        print("Healthcare reading plan:")
        for row in healthcare_reading_plan:
            print(f"- {row['priority']}. {row['review_area']}: {len(row['files_to_review'])} file(s) to review")
    if payload.get("command_evidence"):
        summary = payload.get("command_evidence_summary", {})
        if summary:
            print(
                "Command evidence summary: "
                f"{summary['total_commands']} command(s), "
                f"{summary['review_required_count']} require review, "
                f"highest risk {summary['highest_risk_category']}"
            )
            if summary.get("execution_gates"):
                gates = ", ".join(f"{row['gate']}={row['count']}" for row in summary["execution_gates"])
                print(f"Execution gates: {gates}")
            if summary.get("adapter_policies"):
                policies = ", ".join(f"{row['adapter_type']}={row['count']}" for row in summary["adapter_policies"])
                print(f"Adapter policies: {policies}")
        print("Command evidence:")
        for row in payload["command_evidence"][:5]:
            categories = ", ".join(row.get("side_effect_categories", []))
            gate = row.get("execution_gate", {}).get("gate", "no-gate")
            adapter_policy = adapter_policy_for_command(row)["adapter_type"]
            print(f"- {row['command']} ({row['source_path']}:{row['line']}, {row['side_effect_risk']}, {categories}, {gate}, {adapter_policy})")
    if payload.get("candidate_skill_hypotheses"):
        print("Candidate skill hypotheses:")
        for row in payload["candidate_skill_hypotheses"]:
            coverage = row.get("source_coverage", {})
            coverage_text = ""
            if coverage:
                coverage_text = f", source coverage {coverage['present_count']}/{coverage['total']} ({coverage['status']})"
            cli_draft = row.get("provisional_cli_draft", {})
            cli_text = ""
            if cli_draft:
                cli_text = (
                    f", CLI draft {cli_draft['status']}, "
                    f"adapter policy {cli_draft.get('recommended_adapter_policy', 'none')}, "
                    f"adapter stubs {len(cli_draft.get('adapter_plan_stubs', []))}"
                )
            print(f"- {row['candidate_skill']} ({row['recommendation']}{coverage_text}{cli_text})")
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

    scaffold = sub.add_parser("scaffold-adapter", help="Write a review-only adapter scaffold")
    scaffold.add_argument("adapter_type", nargs="?", choices=sorted(ADAPTER_PLAN_STUBS_BY_POLICY))
    scaffold.add_argument("--adapter-name")
    scaffold.add_argument("--from-scan-json")
    scaffold.add_argument("--candidate-id")
    scaffold.add_argument("--candidate-index", type=int, default=0)
    scaffold.add_argument("--stub-type", choices=sorted(ADAPTER_PLAN_STUBS_BY_POLICY))
    scaffold.add_argument("--stub-index", type=int, default=0)
    scaffold.add_argument("--output-dir", required=True)
    scaffold.add_argument("--force", action="store_true")
    scaffold.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "check":
        payload = check_payload()
    elif args.command == "schema":
        payload = schema_payload()
    elif args.command == "scan":
        payload = scan_repo(
            Path(args.repo_path),
            workflow_goal=args.workflow_goal,
            max_files_per_category=args.max_files_per_category,
            max_total_files=args.max_total_files,
        )
        if payload.get("ok") and args.output_dir:
            payload["written_files"] = write_outputs(payload, Path(args.output_dir))
    else:
        adapter_type = args.adapter_type
        payload = None
        if args.stub_type:
            if adapter_type and adapter_type != args.stub_type:
                payload = {
                    "ok": False,
                    "error": f"adapter_type {adapter_type!r} conflicts with --stub-type {args.stub_type!r}.",
                }
            else:
                adapter_type = args.stub_type
        if payload is None:
            payload = scaffold_adapter(
                adapter_type,
                args.adapter_name,
                Path(args.output_dir),
                force=args.force,
                from_scan_json=Path(args.from_scan_json) if args.from_scan_json else None,
                candidate_id=args.candidate_id,
                candidate_index=args.candidate_index,
                stub_index=args.stub_index,
            )

    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_human(payload)
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
