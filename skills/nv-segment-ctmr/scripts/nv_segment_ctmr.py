from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
from typing import Any


SCRIPT_PATH = "skills/nv-segment-ctmr/scripts/nv_segment_ctmr.py"
SCHEMA_VERSION = "0.1"
VALID_MODES = {"CT_BODY", "MRI_BODY", "MRI_BRAIN"}
SOURCE_REPO_URL = "https://github.com/NVIDIA-Medtech/NV-Segment-CTMR/tree/main/NV-Segment-CTMR"
SOURCE_CLONE_URL = "https://github.com/NVIDIA-Medtech/NV-Segment-CTMR.git"
MODEL_CARD_URL = "https://huggingface.co/nvidia/NV-Segment-CTMR"
MODEL_REPO_ID = "nvidia/NV-Segment-CTMR"
DEFAULT_RUNTIME_DIR = "~/.skillforge/runtime/nv-segment-ctmr"
DEFAULT_CONDA_ENV = "nvseg-ctmr"
DEFAULT_PYTHON_VERSION = "3.11"
VISTA3D_PAPER_URL = (
    "https://openaccess.thecvf.com/content/CVPR2025/html/"
    "He_VISTA3D_A_Unified_Segmentation_Foundation_Model_For_3D_Medical_Imaging_CVPR_2025_paper.html"
)


BUILTIN_LABELS: list[dict[str, Any]] = [
    {
        "label_id": 1,
        "name": "liver",
        "modalities": ["CT_BODY"],
        "source": "NV-Segment-CTMR model card available anatomical classes",
    },
    {
        "label_id": 2,
        "name": "kidney",
        "modalities": ["CT_BODY"],
        "source": "NV-Segment-CTMR model card available anatomical classes",
    },
    {
        "label_id": 3,
        "name": "spleen",
        "modalities": ["CT_BODY"],
        "source": "NV-Segment-CTMR model card available anatomical classes",
    },
    {
        "label_id": 4,
        "name": "pancreas",
        "modalities": ["CT_BODY"],
        "source": "NV-Segment-CTMR model card available anatomical classes",
    },
    {
        "label_id": 6,
        "name": "aorta",
        "modalities": ["CT_BODY"],
        "source": "NV-Segment-CTMR model card available anatomical classes",
    },
    {
        "label_id": 7,
        "name": "inferior vena cava",
        "modalities": ["CT_BODY"],
        "source": "NV-Segment-CTMR model card available anatomical classes",
    },
    {
        "label_id": 10,
        "name": "gallbladder",
        "modalities": ["CT_BODY"],
        "source": "NV-Segment-CTMR model card available anatomical classes",
    },
    {
        "label_id": 12,
        "name": "stomach",
        "modalities": ["CT_BODY"],
        "source": "NV-Segment-CTMR model card available anatomical classes",
    },
    {
        "label_id": 15,
        "name": "bladder",
        "modalities": ["CT_BODY"],
        "source": "NV-Segment-CTMR model card available anatomical classes",
    },
    {
        "label_id": 20,
        "name": "lung",
        "modalities": ["CT_BODY"],
        "source": "NV-Segment-CTMR model card available anatomical classes",
    },
    {
        "label_id": 22,
        "name": "brain",
        "modalities": ["CT_BODY", "MRI_BRAIN"],
        "source": "NV-Segment-CTMR model card available anatomical classes",
    },
    {
        "label_id": 57,
        "name": "trachea",
        "modalities": ["CT_BODY"],
        "source": "NV-Segment-CTMR model card available anatomical classes",
    },
    {
        "label_id": 62,
        "name": "colon",
        "modalities": ["CT_BODY"],
        "source": "NV-Segment-CTMR model card available anatomical classes",
    },
    {
        "label_id": 115,
        "name": "heart",
        "modalities": ["CT_BODY"],
        "source": "NV-Segment-CTMR model card available anatomical classes",
    },
    {
        "label_id": 121,
        "name": "spinal cord",
        "modalities": ["CT_BODY"],
        "source": "NV-Segment-CTMR model card available anatomical classes",
    },
    {
        "label_id": 132,
        "name": "airway",
        "modalities": ["CT_BODY"],
        "source": "NV-Segment-CTMR model card available anatomical classes",
    },
    {
        "label_id": 176,
        "name": "brain tumor",
        "modalities": ["MRI_BRAIN"],
        "source": "NV-Segment-CTMR model card pathological structures",
        "warning": "Model card recommends NV-Segment-CT for better tumor performance.",
    },
    {
        "label_id": 214,
        "name": "3rd-Ventricle",
        "modalities": ["MRI_BRAIN"],
        "source": "NV-Segment-CTMR model card / metadata MRI_BRAIN class range",
    },
    {
        "label_id": 215,
        "name": "4th-Ventricle",
        "modalities": ["MRI_BRAIN"],
        "source": "NV-Segment-CTMR model card / metadata MRI_BRAIN class range",
    },
    {
        "label_id": 220,
        "name": "Brain-Stem",
        "aliases": ["brainstem", "brain stem"],
        "modalities": ["MRI_BRAIN"],
        "source": "NV-Segment-CTMR metadata MRI_BRAIN labels",
    },
    {
        "label_id": 223,
        "name": "Right-Cerebellum-Exterior",
        "aliases": ["right cerebellum"],
        "modalities": ["MRI_BRAIN"],
        "source": "NV-Segment-CTMR metadata MRI_BRAIN labels",
    },
    {
        "label_id": 224,
        "name": "Left-Cerebellum-Exterior",
        "aliases": ["left cerebellum"],
        "modalities": ["MRI_BRAIN"],
        "source": "NV-Segment-CTMR metadata MRI_BRAIN labels",
    },
    {
        "label_id": 229,
        "name": "Right-Hippocampus",
        "aliases": ["right hippocampus"],
        "modalities": ["MRI_BRAIN"],
        "source": "NV-Segment-CTMR metadata MRI_BRAIN labels",
    },
    {
        "label_id": 230,
        "name": "Left-Hippocampus",
        "aliases": ["left hippocampus"],
        "modalities": ["MRI_BRAIN"],
        "source": "NV-Segment-CTMR metadata MRI_BRAIN labels",
    },
    {
        "label_id": 233,
        "name": "Right-Lateral-Ventricle",
        "aliases": ["right lateral ventricle"],
        "modalities": ["MRI_BRAIN"],
        "source": "NV-Segment-CTMR metadata MRI_BRAIN labels",
    },
    {
        "label_id": 234,
        "name": "Left-Lateral-Ventricle",
        "aliases": ["left lateral ventricle"],
        "modalities": ["MRI_BRAIN"],
        "source": "NV-Segment-CTMR metadata MRI_BRAIN labels",
    },
    {
        "label_id": 239,
        "name": "Right-Thalamus-Proper",
        "aliases": ["right thalamus"],
        "modalities": ["MRI_BRAIN"],
        "source": "NV-Segment-CTMR metadata MRI_BRAIN labels",
    },
    {
        "label_id": 240,
        "name": "Left-Thalamus-Proper",
        "aliases": ["left thalamus"],
        "modalities": ["MRI_BRAIN"],
        "source": "NV-Segment-CTMR metadata MRI_BRAIN labels",
    },
]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def normalize_text(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.lower().replace("-", " ")))


def token_set(value: str) -> set[str]:
    return set(normalize_text(value).split())


def importable(module: str) -> dict[str, Any]:
    spec = importlib.util.find_spec(module)
    return {"module": module, "available": spec is not None}


def executable(name: str) -> dict[str, Any]:
    path = shutil.which(name)
    return {"name": name, "available": path is not None, "path": path}


def posix(path: Path | None) -> str | None:
    if path is None:
        return None
    return path.as_posix()


def existing_path(value: str | None) -> Path | None:
    if not value:
        return None
    return Path(value).expanduser()


def resolve_source_dir(value: str | None) -> Path | None:
    source = existing_path(value)
    if source is None:
        return None
    candidates = [
        source,
        source / "NV-Segment-CTMR",
        source / "NV-Segment-CTMR" / "NV-Segment-CTMR",
    ]
    for candidate in candidates:
        if (candidate / "configs").exists():
            return candidate.resolve()
    return source.resolve()


def config_paths(source_dir: Path | None) -> dict[str, str | None]:
    if source_dir is None:
        return {"inference": None, "batch_inference": None, "mgpu_inference": None, "metadata": None, "label_dict": None}
    configs = source_dir / "configs"
    paths = {
        "inference": configs / "inference.json",
        "batch_inference": configs / "batch_inference.json",
        "mgpu_inference": configs / "mgpu_inference.json",
        "metadata": configs / "metadata.json",
        "label_dict": configs / "label_dict.json",
        "label_mappings": configs / "label_mappings.json",
    }
    return {key: posix(path) if path.exists() else None for key, path in paths.items()}


def read_json_file(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def recursive_label_entries(data: Any, *, source_file: str, context: list[str] | None = None) -> list[dict[str, Any]]:
    context = context or []
    entries: list[dict[str, Any]] = []
    if isinstance(data, dict):
        numeric_string_items = [
            (key, value)
            for key, value in data.items()
            if isinstance(key, str) and key.isdigit() and isinstance(value, str)
        ]
        for key, value in numeric_string_items:
            modality_context = [part for part in context if part in VALID_MODES]
            entries.append(
                {
                    "label_id": int(key),
                    "name": value,
                    "modalities": modality_context,
                    "source": "local NV-Segment-CTMR source checkout",
                    "source_file": source_file,
                    "source_context": "/".join(context) if context else None,
                }
            )
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                entries.extend(recursive_label_entries(value, source_file=source_file, context=[*context, str(key)]))
    elif isinstance(data, list):
        for index, value in enumerate(data):
            if isinstance(value, (dict, list)):
                entries.extend(recursive_label_entries(value, source_file=source_file, context=[*context, str(index)]))
    return entries


def dedupe_labels(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[tuple[int, str], dict[str, Any]] = {}
    for entry in entries:
        key = (int(entry["label_id"]), str(entry["name"]))
        existing = merged.get(key)
        if existing is None:
            merged[key] = dict(entry)
            continue
        existing_modalities = set(existing.get("modalities") or [])
        existing_modalities.update(entry.get("modalities") or [])
        existing["modalities"] = sorted(existing_modalities)
        for field in ["source_file", "source_context"]:
            if not existing.get(field) and entry.get(field):
                existing[field] = entry[field]
    return sorted(merged.values(), key=lambda item: (int(item["label_id"]), str(item["name"]).lower()))


def labels_from_source(source_dir: Path | None) -> tuple[list[dict[str, Any]], list[str]]:
    if source_dir is None:
        return [], ["No --source-dir or NV_SEGMENT_CTMR_DIR was provided; using built-in label snapshot."]
    warnings: list[str] = []
    paths = [
        source_dir / "configs" / "metadata.json",
        source_dir / "configs" / "label_dict.json",
        source_dir / "configs" / "label_mappings.json",
    ]
    entries: list[dict[str, Any]] = []
    for path in paths:
        if not path.exists():
            warnings.append(f"Label source file not found: {path}")
            continue
        try:
            entries.extend(recursive_label_entries(read_json_file(path), source_file=posix(path) or str(path)))
        except (OSError, json.JSONDecodeError) as exc:
            warnings.append(f"Could not parse label source file {path}: {exc}")
    return dedupe_labels(entries), warnings


def all_labels(source_dir: Path | None) -> tuple[list[dict[str, Any]], list[str]]:
    source_entries, warnings = labels_from_source(source_dir)
    if source_entries:
        return source_entries, warnings
    return dedupe_labels(BUILTIN_LABELS), warnings


def score_label(query: str, entry: dict[str, Any]) -> int:
    query_norm = normalize_text(query)
    query_tokens = token_set(query)
    names = [str(entry.get("name", "")), *[str(alias) for alias in entry.get("aliases", [])]]
    best = 0
    for name in names:
        name_norm = normalize_text(name)
        name_tokens = token_set(name)
        score = 0
        if query_norm == name_norm:
            score += 100
        if query_norm and query_norm in name_norm:
            score += 45
        if name_norm and name_norm in query_norm:
            score += 35
        score += 12 * len(query_tokens & name_tokens)
        if str(entry.get("label_id")) == query_norm:
            score += 120
        best = max(best, score)
    return best


def selected_model_path(source_dir: Path | None, model_path: str | None) -> Path | None:
    if model_path:
        return Path(model_path).expanduser()
    if source_dir is not None:
        return source_dir / "models" / "model.pt"
    return None


def is_nifti_path(path: Path) -> bool:
    return path.suffix == ".nii" or path.name.endswith(".nii.gz")


def json_scalar(value: Any) -> int | float | str:
    if hasattr(value, "item"):
        value = value.item()
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return int(value)
    if isinstance(value, float):
        if value.is_integer():
            return int(value)
        return float(value)
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return str(value)
    if numeric.is_integer():
        return int(numeric)
    return numeric


def shape_size(shape: list[int]) -> int:
    total = 1
    for value in shape:
        total *= int(value)
    return total


def error_payload(
    command: str,
    kind: str,
    message: str,
    suggested_fix: str,
    *,
    read_only: bool,
    outputs_written: bool = False,
    warnings: list[str] | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "ok": False,
        "command": command,
        "read_only": read_only,
        "outputs_written": outputs_written,
        "error": {"kind": kind, "message": message, "suggested_fix": suggested_fix},
        "errors": [{"kind": kind, "message": message, "suggested_fix": suggested_fix}],
        "warnings": warnings or [],
        "research_only": True,
    }
    if extra:
        payload.update(extra)
    return payload


def source_commit(source_dir: Path | None) -> str | None:
    if source_dir is None or not source_dir.exists():
        return None
    try:
        result = subprocess.run(
            ["git", "-C", str(source_dir), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def source_ready(source_dir: Path | None) -> bool:
    return bool(source_dir and (source_dir / "configs" / "inference.json").exists())


def path_writable(path: Path) -> bool:
    return path.exists() and path.is_dir() and os.access(path, os.W_OK)


def command_tail(value: str, limit: int = 4000) -> str:
    if len(value) <= limit:
        return value
    return value[-limit:]


def iter_nifti_files(input_dir: Path, recursive: bool) -> list[Path]:
    if not input_dir.exists() or not input_dir.is_dir():
        return []
    iterator = input_dir.rglob("*") if recursive else input_dir.iterdir()
    return sorted(path for path in iterator if path.is_file() and is_nifti_path(path))


def expected_output_for_image(output_dir: Path, image: Path) -> Path:
    stem = image_stem(image)
    return output_dir / stem / f"{stem}_trans.nii.gz"


def command_schema() -> dict[str, Any]:
    return {
        "ok": True,
        "schema_version": SCHEMA_VERSION,
        "skill": "nv-segment-ctmr",
        "script": SCRIPT_PATH,
        "commands": [
            {
                "name": "schema",
                "side_effects": [],
                "example": f"python {SCRIPT_PATH} schema --json",
            },
            {
                "name": "check",
                "side_effects": ["read local environment and optional source paths"],
                "example": f"python {SCRIPT_PATH} check --source-dir NV-Segment-CTMR/NV-Segment-CTMR --json",
            },
            {
                "name": "setup-plan",
                "side_effects": ["read local tool availability only; no clone, download, environment creation, or writes"],
                "example": f"python {SCRIPT_PATH} setup-plan --target wsl2-linux --json",
            },
            {
                "name": "labels",
                "side_effects": ["read local label metadata when --source-dir is supplied"],
                "example": f"python {SCRIPT_PATH} labels --query \"brain stem\" --json",
            },
            {
                "name": "plan",
                "side_effects": ["read local path metadata only; no model execution"],
                "example": f"python {SCRIPT_PATH} plan --image scan.nii.gz --mode MRI_BODY --output-dir results --json",
            },
            {
                "name": "brain-plan",
                "side_effects": ["read local path metadata only; no model execution"],
                "example": f"python {SCRIPT_PATH} brain-plan --image brain_t1.nii.gz --output-dir results --json",
            },
            {
                "name": "batch-plan",
                "side_effects": ["read input directory metadata only; no model execution"],
                "example": f"python {SCRIPT_PATH} batch-plan --input-dir cohort --mode MRI_BODY --output-dir results --json",
            },
            {
                "name": "verify-output",
                "side_effects": ["read an existing segmentation NIfTI and summarize metadata"],
                "example": f"python {SCRIPT_PATH} verify-output --segmentation results/scan_trans.nii.gz --json",
            },
            {
                "name": "run",
                "side_effects": ["requires --confirm-execution; may run model inference and write outputs"],
                "example": f"python {SCRIPT_PATH} run --image scan.nii.gz --mode MRI_BODY --output-dir results --confirm-execution --json",
            },
            {
                "name": "brain-run",
                "side_effects": ["requires --confirm-execution; may run skull stripping, preprocessing, model inference, and writes"],
                "example": f"python {SCRIPT_PATH} brain-run --image brain_t1.nii.gz --output-dir results --confirm-execution --json",
            },
            {
                "name": "batch-run",
                "side_effects": ["requires --confirm-execution; may run model inference for many volumes and write outputs"],
                "example": f"python {SCRIPT_PATH} batch-run --input-dir cohort --mode MRI_BODY --output-dir results --confirm-execution --json",
            },
        ],
        "modes": sorted(VALID_MODES),
        "research_only": True,
        "safety": [
            "Do not use for diagnosis, treatment, triage, or clinical decision-making.",
            "Do not run downloads, Docker, GPU jobs, or writes without explicit approval.",
            "Label IDs must come from source label maps or the built-in cited snapshot.",
        ],
        "sources": {
            "source_repo": SOURCE_REPO_URL,
            "model_card": MODEL_CARD_URL,
            "paper": VISTA3D_PAPER_URL,
        },
    }


def join_posix_path(*parts: str) -> str:
    clean_parts = [part.strip("/\\") for part in parts if part]
    if not clean_parts:
        return ""
    first = clean_parts[0]
    if parts[0].startswith("~"):
        return "/".join([first, *clean_parts[1:]])
    if parts[0].startswith("/"):
        return "/" + "/".join(clean_parts)
    return "/".join(clean_parts)


def setup_plan_command(args: argparse.Namespace) -> dict[str, Any]:
    runtime_dir = str(args.runtime_dir).rstrip("/\\") or DEFAULT_RUNTIME_DIR
    repo_dir = join_posix_path(runtime_dir, "repo")
    source_dir = join_posix_path(repo_dir, "NV-Segment-CTMR")
    model_dir = join_posix_path(source_dir, "models")
    model_path = join_posix_path(model_dir, "model.pt")
    env_name = args.env_name
    python_version = args.python_version

    commands = [
        {
            "step": "create runtime directory",
            "command": ["mkdir", "-p", runtime_dir],
            "writes": [runtime_dir],
        },
        {
            "step": "clone upstream source",
            "command": ["git", "clone", SOURCE_CLONE_URL, repo_dir],
            "writes": [repo_dir],
            "network": True,
        },
        {
            "step": "create conda environment",
            "command": ["conda", "create", "-n", env_name, f"python={python_version}", "-y"],
            "writes": [f"conda environment {env_name}"],
        },
        {
            "step": "install upstream Python dependencies",
            "command": ["conda", "run", "-n", env_name, "pip", "install", "-r", join_posix_path(source_dir, "requirements.txt")],
            "network": True,
            "writes": [f"conda environment {env_name}"],
        },
        {
            "step": "download model weights",
            "command": ["conda", "run", "-n", env_name, "hf", "download", MODEL_REPO_ID, "--local-dir", model_dir],
            "network": True,
            "writes": [model_dir],
        },
        {
            "step": "check runtime readiness from the SkillForge repo",
            "command": [
                "conda",
                "run",
                "-n",
                env_name,
                "python",
                SCRIPT_PATH,
                "check",
                "--source-dir",
                source_dir,
                "--model-path",
                model_path,
                "--json",
            ],
        },
    ]

    warnings: list[str] = []
    if args.target == "wsl2-linux":
        warnings.append("Run these commands inside WSL2 Ubuntu, not from PowerShell, unless the agent explicitly wraps them with wsl.exe.")
    if platform.system().lower() == "windows" and shutil.which("wsl") is None:
        warnings.append("This Windows host does not expose wsl on PATH; WSL2 setup cannot be checked from this process.")
    if shutil.which("conda") is None:
        warnings.append("conda is not on PATH for this process; install Miniforge or run from an activated conda shell before executing the plan.")
    if shutil.which("git") is None:
        warnings.append("git is not on PATH for this process; source clone will fail until git is available.")
    if shutil.which("docker") is None:
        warnings.append("Docker is not on PATH for this process; MRI_BRAIN skull stripping needs separate Docker/SynthStrip readiness or --no-skullstrip.")

    return {
        "ok": True,
        "command": "setup-plan",
        "read_only": True,
        "target": args.target,
        "runtime_dir": runtime_dir,
        "source_clone_url": SOURCE_CLONE_URL,
        "source_dir": source_dir,
        "model_repo": MODEL_REPO_ID,
        "model_path": model_path,
        "conda_env": env_name,
        "python_version": python_version,
        "commands": commands,
        "detected_tools": {
            "git": bool(shutil.which("git")),
            "conda": bool(shutil.which("conda")),
            "hf": bool(shutil.which("hf")),
            "docker": bool(shutil.which("docker")),
            "wsl": bool(shutil.which("wsl")),
        },
        "side_effects_if_executed": [
            "create runtime directories",
            "clone upstream source from GitHub",
            "create or modify a conda environment",
            "download Python packages",
            "download model weights from Hugging Face",
        ],
        "approvals_needed": [
            "Approve cloning the upstream NV-Segment-CTMR repository.",
            "Approve creating or modifying the conda environment.",
            "Approve downloading model weights and accepting applicable model terms.",
            "Approve processing any medical image data before running inference.",
        ],
        "warnings": warnings,
        "research_only": True,
        "sources": {"source_repo": SOURCE_REPO_URL, "clone_url": SOURCE_CLONE_URL, "model_card": MODEL_CARD_URL},
    }


def check_environment(args: argparse.Namespace) -> dict[str, Any]:
    env_source = args.source_dir or None
    if env_source is None:
        env_source = None
    source_dir = resolve_source_dir(env_source)
    model_path = selected_model_path(source_dir, args.model_path)
    output_dir = existing_path(args.output_dir)
    configs = config_paths(source_dir)
    dependencies = [importable(name) for name in ["monai", "torch", "nibabel", "numpy"]]
    executables = [executable(name) for name in ["git", "hf", "conda", "torchrun", "docker"]]
    warnings: list[str] = []
    if source_dir is None:
        warnings.append("No source directory supplied. Set --source-dir or NV_SEGMENT_CTMR_DIR for full readiness checks.")
    elif not (source_dir / "configs" / "inference.json").exists():
        warnings.append("Source directory does not look like the inner NV-Segment-CTMR directory with configs/inference.json.")
    if model_path is None:
        warnings.append("No model path could be inferred. Use --model-path or place weights under <source-dir>/models/model.pt.")
    elif not model_path.exists():
        warnings.append(f"Model weights not found: {model_path}")
    if output_dir is not None and output_dir.exists() and not output_dir.is_dir():
        warnings.append(f"Output path exists but is not a directory: {output_dir}")

    return {
        "ok": True,
        "command": "check",
        "read_only": True,
        "timestamp": utc_now(),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "python": sys.version.split()[0],
            "executable": sys.executable,
        },
        "source_dir": posix(source_dir),
        "source_dir_exists": bool(source_dir and source_dir.exists()),
        "configs": configs,
        "model_path": posix(model_path),
        "model_exists": bool(model_path and model_path.exists()),
        "output_dir": posix(output_dir),
        "output_dir_exists": bool(output_dir and output_dir.exists()),
        "dependencies": dependencies,
        "executables": executables,
        "warnings": warnings,
        "side_effects": ["read environment and filesystem metadata"],
        "research_only": True,
    }


def labels_command(args: argparse.Namespace) -> dict[str, Any]:
    source_dir = resolve_source_dir(args.source_dir)
    labels, warnings = all_labels(source_dir)
    scored = []
    for entry in labels:
        score = score_label(args.query, entry)
        if score > 0:
            item = dict(entry)
            item["score"] = score
            scored.append(item)
    scored.sort(key=lambda item: (-int(item["score"]), int(item["label_id"]), str(item["name"]).lower()))
    limited = scored[: args.limit]
    if not limited:
        warnings.append("No label candidates matched. Use --source-dir with the upstream checkout for full label coverage.")
    return {
        "ok": True,
        "command": "labels",
        "read_only": True,
        "query": args.query,
        "source_dir": posix(source_dir),
        "label_source": "local_source" if source_dir else "built_in_snapshot",
        "result_count": len(limited),
        "results": limited,
        "warnings": warnings,
        "sources": {
            "model_card": MODEL_CARD_URL,
            "source_repo": SOURCE_REPO_URL,
        },
    }


def verify_output_command(args: argparse.Namespace) -> dict[str, Any]:
    segmentation = Path(args.segmentation).expanduser()
    warnings: list[str] = []
    errors: list[dict[str, str]] = []
    payload: dict[str, Any] = {
        "ok": False,
        "command": "verify-output",
        "read_only": True,
        "timestamp": utc_now(),
        "segmentation": posix(segmentation),
        "exists": segmentation.exists(),
        "is_file": segmentation.is_file(),
        "suffix_ok": is_nifti_path(segmentation),
        "bytes": None,
        "nibabel_available": importable("nibabel")["available"],
        "numpy_available": importable("numpy")["available"],
        "nifti_readable": False,
        "shape": None,
        "ndim": None,
        "dtype": None,
        "zooms": None,
        "voxel_count": None,
        "label_summary": None,
        "warnings": warnings,
        "errors": errors,
        "side_effects": ["read segmentation file metadata", "optionally read segmentation label values"],
        "research_only": True,
    }

    if not payload["suffix_ok"]:
        warnings.append("Segmentation path does not end in .nii or .nii.gz.")
    if not segmentation.exists():
        errors.append(
            {
                "kind": "missing_segmentation",
                "message": f"Segmentation file not found: {segmentation}",
                "suggested_fix": "Check the path or run the plan command to review expected output locations.",
            }
        )
        payload["error"] = errors[0]
        return payload
    if not segmentation.is_file():
        errors.append(
            {
                "kind": "not_a_file",
                "message": f"Segmentation path is not a file: {segmentation}",
                "suggested_fix": "Provide a path to a .nii or .nii.gz segmentation file.",
            }
        )
        payload["error"] = errors[0]
        return payload
    try:
        payload["bytes"] = int(segmentation.stat().st_size)
    except OSError as exc:
        errors.append({"kind": "stat_failed", "message": str(exc), "suggested_fix": "Check file permissions."})
        payload["error"] = errors[0]
        return payload
    if payload["bytes"] == 0:
        errors.append(
            {
                "kind": "empty_file",
                "message": f"Segmentation file is empty: {segmentation}",
                "suggested_fix": "Regenerate the segmentation output and verify the upstream command completed successfully.",
            }
        )
        payload["error"] = errors[0]
        return payload
    if not payload["nibabel_available"]:
        errors.append(
            {
                "kind": "missing_optional_dependency",
                "message": "nibabel is required to verify that the segmentation is a readable NIfTI file.",
                "suggested_fix": "Install nibabel in the Python environment used to run this adapter.",
            }
        )
        payload["error"] = errors[0]
        return payload

    try:
        import nibabel as nib  # type: ignore[import-not-found]

        image = nib.load(str(segmentation))
        shape = [int(value) for value in image.shape]
        payload.update(
            {
                "nifti_readable": True,
                "shape": shape,
                "ndim": len(shape),
                "dtype": str(image.get_data_dtype()),
                "zooms": [float(value) for value in image.header.get_zooms()],
                "voxel_count": shape_size(shape),
                "affine": [[float(value) for value in row] for row in image.affine.tolist()],
            }
        )
        if args.no_label_summary:
            warnings.append("Label summary was skipped because --no-label-summary was supplied.")
        elif not payload["numpy_available"]:
            warnings.append("numpy is not available; label value summary was skipped.")
        else:
            import numpy as np  # type: ignore[import-not-found]

            data = np.asanyarray(image.dataobj)
            unique_values, counts = np.unique(data, return_counts=True)
            max_values = max(0, int(args.max_label_values))
            values = [
                {"label": json_scalar(value), "voxel_count": int(count)}
                for value, count in zip(unique_values[:max_values], counts[:max_values])
            ]
            truncated = len(unique_values) > max_values
            if truncated:
                warnings.append(
                    f"Label summary contains {len(unique_values)} unique values; showing first {max_values} sorted values."
                )
            payload["label_summary"] = {
                "unique_value_count": int(len(unique_values)),
                "nonzero_voxel_count": int(np.count_nonzero(data)),
                "truncated": truncated,
                "values": values,
            }
    except Exception as exc:
        errors.append(
            {
                "kind": "nifti_read_failed",
                "message": str(exc),
                "suggested_fix": "Confirm the file is a valid NIfTI image and not a compressed archive or partial output.",
            }
        )

    payload["ok"] = not errors
    if errors:
        payload["error"] = errors[0]
    return payload


def parse_labels(values: list[str] | None) -> list[int]:
    labels: list[int] = []
    for value in values or []:
        for part in value.split(","):
            part = part.strip()
            if not part:
                continue
            labels.append(int(part))
    return labels


def image_stem(path: Path) -> str:
    name = path.name
    if name.endswith(".nii.gz"):
        return name[:-7]
    return path.stem


def plan_command(args: argparse.Namespace) -> dict[str, Any]:
    mode = args.mode.upper()
    if mode not in VALID_MODES:
        return {
            "ok": False,
            "command": "plan",
            "error": {"kind": "unsupported_mode", "message": f"Mode must be one of {sorted(VALID_MODES)}"},
            "read_only": True,
        }
    source_dir = resolve_source_dir(args.source_dir)
    model_path = selected_model_path(source_dir, args.model_path)
    image = Path(args.image).expanduser()
    output_dir = Path(args.output_dir).expanduser()
    labels = parse_labels(args.label_id)
    warnings: list[str] = []
    blocking_reasons: list[str] = []
    approvals_needed = ["Confirm local medical image processing is allowed.", "Confirm output directory before execution."]
    required_files: list[str] = [posix(image) or str(image)]
    if source_dir is None:
        warnings.append("No source directory supplied; command is a template until --source-dir or NV_SEGMENT_CTMR_DIR is set.")
        blocking_reasons.append("missing_source_dir")
    elif not source_ready(source_dir):
        warnings.append("Source directory does not look like the inner NV-Segment-CTMR directory with configs/inference.json.")
        blocking_reasons.append("source_not_ready")
    if not image.exists():
        warnings.append(f"Input image does not exist yet: {image}")
        blocking_reasons.append("missing_input_image")
    if image.suffix != ".nii" and not image.name.endswith(".nii.gz"):
        warnings.append("Input path does not end in .nii or .nii.gz.")
        blocking_reasons.append("input_not_nifti")
    if model_path is None or not model_path.exists():
        warnings.append("Model weights are not available at the planned path.")
        blocking_reasons.append("missing_model_weights")
    else:
        required_files.append(posix(model_path) or str(model_path))
    if not output_dir.exists():
        warnings.append("Output directory does not exist yet. Planning is read-only and will not create it.")
        blocking_reasons.append("missing_output_dir")
    if mode == "MRI_BRAIN":
        approvals_needed.append("Confirm whether Docker/SynthStrip may be used for skull stripping.")
        if args.no_skullstrip:
            warnings.append("MRI_BRAIN preprocessing will skip skull stripping; confirm the input is suitable for no-skullstrip execution.")
        else:
            warnings.append("MRI_BRAIN requires brain MRI preprocessing; skull stripping may require Docker/SynthStrip unless --no-skullstrip is used.")
            if shutil.which("docker") is None:
                blocking_reasons.append("missing_docker_for_skullstrip")

    stem = image_stem(image)
    source_prefix = [] if source_dir is None else ["--source-dir", posix(source_dir) or str(source_dir)]
    if mode == "MRI_BRAIN" and args.brain_script:
        command = [
            str((source_dir / "brain_t1_preprocess" / "run_brain_segmentation.sh") if source_dir else "brain_t1_preprocess/run_brain_segmentation.sh"),
            "--input",
            str(image),
            "--output_dir",
            str(output_dir),
        ]
        if args.no_skullstrip:
            command.append("--no-skullstrip")
        if args.keep_temp:
            command.append("--keep-temp")
        expected_outputs = [posix(output_dir / f"{stem}_trans.nii.gz")]
        route = "brain-mri-segmentation-script"
    else:
        input_dict: dict[str, Any] = {"image": str(image)}
        if labels:
            input_dict["label_prompt"] = labels
        else:
            input_dict["modality"] = mode
        command = [
            sys.executable,
            "-m",
            "monai.bundle",
            "run",
            "--config_file",
            "configs/inference.json",
            "--input_dict",
            repr(input_dict),
        ]
        if not labels:
            command.extend(["--modality", mode])
        command.extend(["--output_dir", str(output_dir)])
        expected_outputs = [
            posix(output_dir / stem / f"{stem}_trans.nii.gz"),
            "Actual MONAI SaveImaged path may vary with upstream config.",
        ]
        route = "label-prompt-segmentation" if labels else "segment-everything"

    return {
        "ok": True,
        "command": "plan",
        "read_only": True,
        "ready_to_execute": not blocking_reasons,
        "blocking_reasons": blocking_reasons,
        "route": route,
        "mode": mode,
        "label_ids": labels,
        "image": posix(image),
        "output_dir": posix(output_dir),
        "source_dir": posix(source_dir),
        "model_path": posix(model_path),
        "source_options": source_prefix,
        "planned_command": command,
        "required_files": required_files,
        "expected_outputs": expected_outputs,
        "side_effects_if_executed": ["read medical image volume", "run model inference", "write segmentation outputs", "write logs/provenance"],
        "approvals_needed": approvals_needed,
        "warnings": warnings,
        "provenance_template": {
            "source_repo": SOURCE_REPO_URL,
            "model_card": MODEL_CARD_URL,
            "mode": mode,
            "label_ids": labels,
            "input_image": posix(image),
            "output_dir": posix(output_dir),
            "planned_at": utc_now(),
        },
        "research_only": True,
    }


def brain_plan_command(args: argparse.Namespace) -> dict[str, Any]:
    source_dir = resolve_source_dir(args.source_dir)
    plan_args = argparse.Namespace(
        image=args.image,
        mode="MRI_BRAIN",
        output_dir=args.output_dir,
        source_dir=args.source_dir,
        model_path=args.model_path,
        label_id=None,
        brain_script=True,
        no_skullstrip=args.no_skullstrip,
        keep_temp=args.keep_temp,
    )
    payload = plan_command(plan_args)
    payload["command"] = "brain-plan"
    payload["route"] = "brain-mri-segmentation-script"
    payload["brain_workflow"] = {
        "skullstrip": not args.no_skullstrip,
        "keep_temp": bool(args.keep_temp),
        "docker_may_be_required": not args.no_skullstrip,
        "native_space_reversion_expected": True,
    }
    script = (source_dir / "brain_t1_preprocess" / "run_brain_segmentation.sh") if source_dir else Path("brain_t1_preprocess/run_brain_segmentation.sh")
    command = [
        posix(script) or str(script),
        "--input",
        posix(Path(args.image).expanduser()) or str(Path(args.image).expanduser()),
        "--output_dir",
        posix(Path(args.output_dir).expanduser()) or str(Path(args.output_dir).expanduser()),
    ]
    if platform.system() == "Windows":
        command = ["bash", *command]
        if shutil.which("bash") is None:
            payload.setdefault("warnings", []).append("Windows brain execution requires bash; bash was not found on PATH.")
            payload.setdefault("blocking_reasons", []).append("missing_bash")
            payload["ready_to_execute"] = False
    if args.no_skullstrip:
        command.append("--no-skullstrip")
    if args.keep_temp:
        command.append("--keep-temp")
    payload["planned_command"] = command
    payload.setdefault("side_effects_if_executed", []).extend(
        ["may write temporary preprocessing files", "may run skull stripping", "may revert segmentation to native space"]
    )
    return payload


def batch_plan_command(args: argparse.Namespace) -> dict[str, Any]:
    mode = args.mode.upper()
    if mode not in VALID_MODES:
        return error_payload(
            "batch-plan",
            "unsupported_mode",
            f"Mode must be one of {sorted(VALID_MODES)}",
            "Choose CT_BODY, MRI_BODY, or MRI_BRAIN.",
            read_only=True,
        )
    source_dir = resolve_source_dir(args.source_dir)
    model_path = selected_model_path(source_dir, args.model_path)
    input_dir = Path(args.input_dir).expanduser()
    output_dir = Path(args.output_dir).expanduser()
    files = iter_nifti_files(input_dir, args.recursive)
    warnings: list[str] = []
    if source_dir is None:
        warnings.append("No source directory supplied; command is a template until --source-dir or NV_SEGMENT_CTMR_DIR is set.")
    elif not source_ready(source_dir):
        warnings.append("Source directory does not look like the inner NV-Segment-CTMR directory with configs/inference.json.")
    if not input_dir.exists():
        warnings.append(f"Input directory does not exist: {input_dir}")
    elif not input_dir.is_dir():
        warnings.append(f"Input path is not a directory: {input_dir}")
    if not files:
        warnings.append("No .nii or .nii.gz files were discovered.")
    if model_path is None or not model_path.exists():
        warnings.append("Model weights are not available at the planned path.")
    if not output_dir.exists():
        warnings.append("Output directory does not exist yet. Planning is read-only and will not create it.")
    if mode == "MRI_BRAIN":
        warnings.append("MRI_BRAIN batch workflows should be reviewed carefully because brain preprocessing may be per-volume.")

    expected = [
        {
            "image": posix(path),
            "expected_output": posix(expected_output_for_image(output_dir, path)),
            "skip_if_exists": bool(args.skip_existing and expected_output_for_image(output_dir, path).exists()),
        }
        for path in files[: args.max_items]
    ]
    skipped = sum(1 for item in expected if item["skip_if_exists"])
    queued = max(0, len(files) - skipped)
    base_command = [
        sys.executable,
        "-m",
        "monai.bundle",
        "run",
        "--config_file",
        "configs/batch_inference.json",
        "--input_dir",
        str(input_dir),
        "--output_dir",
        str(output_dir),
        "--modality",
        mode,
    ]
    multi_gpu_command = [
        "torchrun",
        "--nproc_per_node",
        str(max(1, int(args.gpus))),
        "-m",
        "monai.bundle",
        "run",
        "--config_file",
        "configs/mgpu_inference.json",
        "--input_dir",
        str(input_dir),
        "--output_dir",
        str(output_dir),
        "--modality",
        mode,
    ]
    return {
        "ok": True,
        "command": "batch-plan",
        "read_only": True,
        "ready_to_execute": not warnings,
        "mode": mode,
        "input_dir": posix(input_dir),
        "output_dir": posix(output_dir),
        "source_dir": posix(source_dir),
        "model_path": posix(model_path),
        "recursive": bool(args.recursive),
        "skip_existing": bool(args.skip_existing),
        "discovered_count": len(files),
        "queued_count": queued,
        "skipped_count": skipped,
        "shown_count": len(expected),
        "expected_outputs": expected,
        "planned_command": base_command,
        "multi_gpu_command": multi_gpu_command if int(args.gpus) > 1 else None,
        "side_effects_if_executed": ["read medical image volumes", "run model inference", "write segmentation outputs", "write logs/provenance"],
        "approvals_needed": ["Confirm local medical image processing is allowed.", "Confirm batch output directory before execution."],
        "warnings": warnings,
        "provenance_template": {
            "source_repo": SOURCE_REPO_URL,
            "source_commit": source_commit(source_dir),
            "model_card": MODEL_CARD_URL,
            "mode": mode,
            "input_dir": posix(input_dir),
            "output_dir": posix(output_dir),
            "planned_at": utc_now(),
        },
        "research_only": True,
    }


def run_command(args: argparse.Namespace) -> dict[str, Any]:
    plan_args = argparse.Namespace(
        image=args.image,
        mode=args.mode,
        output_dir=args.output_dir,
        source_dir=args.source_dir,
        model_path=args.model_path,
        label_id=args.label_id,
        brain_script=False,
        no_skullstrip=False,
        keep_temp=False,
    )
    plan = plan_command(plan_args)
    plan["command"] = "run"
    if not args.confirm_execution:
        return error_payload(
            "run",
            "execution_not_confirmed",
            "Refusing to run NV-Segment-CTMR without --confirm-execution.",
            "After the user has explicitly approved model execution and writes, rerun with --confirm-execution.",
            read_only=True,
            extra={"planned_run": plan, "required_flag": "--confirm-execution"},
        )

    mode = args.mode.upper()
    source_dir = resolve_source_dir(args.source_dir)
    model_path = selected_model_path(source_dir, args.model_path)
    image = Path(args.image).expanduser()
    output_dir = Path(args.output_dir).expanduser()
    errors: list[dict[str, str]] = []
    warnings = list(plan.get("warnings", []))
    if mode not in VALID_MODES:
        errors.append({"kind": "unsupported_mode", "message": f"Mode must be one of {sorted(VALID_MODES)}", "suggested_fix": "Choose CT_BODY, MRI_BODY, or MRI_BRAIN."})
    if not source_ready(source_dir):
        errors.append(
            {
                "kind": "missing_source_checkout",
                "message": "A local NV-Segment-CTMR source checkout with configs/inference.json is required.",
                "suggested_fix": "Pass --source-dir or set NV_SEGMENT_CTMR_DIR to the inner NV-Segment-CTMR directory.",
            }
        )
    if model_path is None or not model_path.exists():
        errors.append(
            {
                "kind": "missing_model_weights",
                "message": "Model weights are required before execution.",
                "suggested_fix": "Pass --model-path or place model.pt under <source-dir>/models/model.pt after reviewing model terms.",
            }
        )
    if not image.exists() or not image.is_file() or not is_nifti_path(image):
        errors.append(
            {
                "kind": "invalid_input_image",
                "message": f"Input image must be an existing .nii or .nii.gz file: {image}",
                "suggested_fix": "Provide a local CT or MRI NIfTI file path.",
            }
        )
    if not path_writable(output_dir):
        errors.append(
            {
                "kind": "output_dir_not_writable",
                "message": f"Output directory must already exist and be writable: {output_dir}",
                "suggested_fix": "Create the output directory, confirm it is writable, then rerun.",
            }
        )
    missing_dependencies = [name for name in ["monai", "torch"] if not importable(name)["available"]]
    if missing_dependencies:
        errors.append(
            {
                "kind": "missing_runtime_dependency",
                "message": f"Missing Python dependencies: {', '.join(missing_dependencies)}",
                "suggested_fix": "Run from the NV-Segment-CTMR Python environment with MONAI and PyTorch installed.",
            }
        )
    if errors:
        return {
            "ok": False,
            "command": "run",
            "read_only": False,
            "outputs_written": False,
            "errors": errors,
            "error": errors[0],
            "warnings": warnings,
            "planned_run": plan,
            "research_only": True,
        }

    command = plan["planned_command"]
    started_at = utc_now()
    try:
        result = subprocess.run(
            command,
            cwd=source_dir,
            capture_output=True,
            text=True,
            check=False,
            timeout=int(args.timeout_seconds),
        )
    except subprocess.TimeoutExpired as exc:
        return error_payload(
            "run",
            "execution_timeout",
            f"NV-Segment-CTMR execution exceeded {args.timeout_seconds} seconds.",
            "Increase --timeout-seconds or inspect partial outputs before rerunning.",
            read_only=False,
            outputs_written=True,
            warnings=warnings,
            extra={"stdout_tail": command_tail(exc.stdout or ""), "stderr_tail": command_tail(exc.stderr or ""), "planned_run": plan},
        )
    except OSError as exc:
        return error_payload(
            "run",
            "execution_launch_failed",
            str(exc),
            "Confirm the Python executable and NV-Segment-CTMR environment are usable.",
            read_only=False,
            outputs_written=False,
            warnings=warnings,
            extra={"planned_run": plan},
        )

    logs_dir = output_dir / "_nv_segment_ctmr_logs"
    logs_dir.mkdir(exist_ok=True)
    stem = image_stem(image)
    stdout_path = logs_dir / f"{stem}_stdout.txt"
    stderr_path = logs_dir / f"{stem}_stderr.txt"
    provenance_path = logs_dir / f"{stem}_provenance.json"
    stdout_path.write_text(result.stdout, encoding="utf-8")
    stderr_path.write_text(result.stderr, encoding="utf-8")
    expected_output = expected_output_for_image(output_dir, image)
    verification = None
    if expected_output.exists():
        verification = verify_output_command(
            argparse.Namespace(segmentation=str(expected_output), max_label_values=args.max_label_values, no_label_summary=False)
        )
    else:
        warnings.append(f"Expected output was not found after execution: {expected_output}")
    provenance = {
        "source_repo": SOURCE_REPO_URL,
        "source_commit": source_commit(source_dir),
        "model_card": MODEL_CARD_URL,
        "model_path": posix(model_path),
        "command": command,
        "working_dir": posix(source_dir),
        "mode": mode,
        "label_ids": parse_labels(args.label_id),
        "input_image": posix(image),
        "output_dir": posix(output_dir),
        "expected_output": posix(expected_output),
        "started_at": started_at,
        "finished_at": utc_now(),
        "returncode": result.returncode,
        "warnings": warnings,
        "research_only": True,
    }
    provenance_path.write_text(json.dumps(provenance, indent=2, sort_keys=True), encoding="utf-8")
    return {
        "ok": result.returncode == 0 and (verification is None or verification.get("ok", False)),
        "command": "run",
        "read_only": False,
        "outputs_written": True,
        "returncode": result.returncode,
        "planned_run": plan,
        "log_paths": {
            "stdout": posix(stdout_path),
            "stderr": posix(stderr_path),
            "provenance": posix(provenance_path),
        },
        "stdout_tail": command_tail(result.stdout),
        "stderr_tail": command_tail(result.stderr),
        "expected_output": posix(expected_output),
        "output_verification": verification,
        "provenance": provenance,
        "warnings": warnings,
        "error": None
        if result.returncode == 0
        else {
            "kind": "upstream_execution_failed",
            "message": f"NV-Segment-CTMR command exited with code {result.returncode}.",
            "suggested_fix": "Inspect stderr/stdout logs and confirm source checkout, model weights, input modality, and runtime environment.",
        },
        "research_only": True,
    }


def brain_run_command(args: argparse.Namespace) -> dict[str, Any]:
    plan = brain_plan_command(args)
    plan["command"] = "brain-run"
    if not args.confirm_execution:
        return error_payload(
            "brain-run",
            "execution_not_confirmed",
            "Refusing to run brain MRI preprocessing/segmentation without --confirm-execution.",
            "After the user has explicitly approved model execution, preprocessing, and writes, rerun with --confirm-execution.",
            read_only=True,
            extra={"planned_run": plan, "required_flag": "--confirm-execution"},
        )

    source_dir = resolve_source_dir(args.source_dir)
    image = Path(args.image).expanduser()
    output_dir = Path(args.output_dir).expanduser()
    errors: list[dict[str, str]] = []
    warnings = list(plan.get("warnings", []))
    script = (source_dir / "brain_t1_preprocess" / "run_brain_segmentation.sh") if source_dir else None
    if not source_ready(source_dir) or script is None or not script.exists():
        errors.append(
            {
                "kind": "missing_brain_source",
                "message": "A local NV-Segment-CTMR checkout with brain_t1_preprocess/run_brain_segmentation.sh is required.",
                "suggested_fix": "Pass --source-dir or set NV_SEGMENT_CTMR_DIR to the inner NV-Segment-CTMR directory.",
            }
        )
    if platform.system() == "Windows" and shutil.which("bash") is None:
        errors.append(
            {
                "kind": "missing_bash",
                "message": "brain-run uses the upstream shell script and requires bash on Windows.",
                "suggested_fix": "Run from WSL/Git Bash or use --no-skullstrip only after confirming the upstream script can run.",
            }
        )
    if not args.no_skullstrip and shutil.which("docker") is None:
        errors.append(
            {
                "kind": "missing_docker",
                "message": "Skull stripping may require Docker/SynthStrip and docker was not found.",
                "suggested_fix": "Install/enable Docker or rerun with --no-skullstrip if the input is already skull-stripped.",
            }
        )
    if not image.exists() or not image.is_file() or not is_nifti_path(image):
        errors.append(
            {
                "kind": "invalid_input_image",
                "message": f"Input image must be an existing .nii or .nii.gz file: {image}",
                "suggested_fix": "Provide a local brain MRI NIfTI file path.",
            }
        )
    if not path_writable(output_dir):
        errors.append(
            {
                "kind": "output_dir_not_writable",
                "message": f"Output directory must already exist and be writable: {output_dir}",
                "suggested_fix": "Create the output directory, confirm it is writable, then rerun.",
            }
        )
    if errors:
        return {
            "ok": False,
            "command": "brain-run",
            "read_only": False,
            "outputs_written": False,
            "errors": errors,
            "error": errors[0],
            "warnings": warnings,
            "planned_run": plan,
            "research_only": True,
        }

    command = plan["planned_command"]
    started_at = utc_now()
    try:
        result = subprocess.run(
            command,
            cwd=source_dir,
            capture_output=True,
            text=True,
            check=False,
            timeout=int(args.timeout_seconds),
        )
    except subprocess.TimeoutExpired as exc:
        return error_payload(
            "brain-run",
            "execution_timeout",
            f"Brain MRI segmentation exceeded {args.timeout_seconds} seconds.",
            "Increase --timeout-seconds or inspect partial outputs before rerunning.",
            read_only=False,
            outputs_written=True,
            warnings=warnings,
            extra={"stdout_tail": command_tail(exc.stdout or ""), "stderr_tail": command_tail(exc.stderr or ""), "planned_run": plan},
        )
    logs_dir = output_dir / "_nv_segment_ctmr_logs"
    logs_dir.mkdir(exist_ok=True)
    stem = image_stem(image)
    stdout_path = logs_dir / f"{stem}_brain_stdout.txt"
    stderr_path = logs_dir / f"{stem}_brain_stderr.txt"
    provenance_path = logs_dir / f"{stem}_brain_provenance.json"
    stdout_path.write_text(result.stdout, encoding="utf-8")
    stderr_path.write_text(result.stderr, encoding="utf-8")
    expected_output = output_dir / f"{stem}_trans.nii.gz"
    verification = None
    if expected_output.exists():
        verification = verify_output_command(
            argparse.Namespace(segmentation=str(expected_output), max_label_values=args.max_label_values, no_label_summary=False)
        )
    else:
        warnings.append(f"Expected brain output was not found after execution: {expected_output}")
    provenance = {
        "source_repo": SOURCE_REPO_URL,
        "source_commit": source_commit(source_dir),
        "model_card": MODEL_CARD_URL,
        "command": command,
        "working_dir": posix(source_dir),
        "mode": "MRI_BRAIN",
        "input_image": posix(image),
        "output_dir": posix(output_dir),
        "expected_output": posix(expected_output),
        "skullstrip": not args.no_skullstrip,
        "keep_temp": bool(args.keep_temp),
        "started_at": started_at,
        "finished_at": utc_now(),
        "returncode": result.returncode,
        "warnings": warnings,
        "research_only": True,
    }
    provenance_path.write_text(json.dumps(provenance, indent=2, sort_keys=True), encoding="utf-8")
    return {
        "ok": result.returncode == 0 and (verification is None or verification.get("ok", False)),
        "command": "brain-run",
        "read_only": False,
        "outputs_written": True,
        "returncode": result.returncode,
        "planned_run": plan,
        "log_paths": {"stdout": posix(stdout_path), "stderr": posix(stderr_path), "provenance": posix(provenance_path)},
        "stdout_tail": command_tail(result.stdout),
        "stderr_tail": command_tail(result.stderr),
        "expected_output": posix(expected_output),
        "output_verification": verification,
        "provenance": provenance,
        "warnings": warnings,
        "error": None
        if result.returncode == 0
        else {
            "kind": "upstream_execution_failed",
            "message": f"Brain MRI command exited with code {result.returncode}.",
            "suggested_fix": "Inspect stderr/stdout logs and confirm bash, Docker/skull-strip choice, source checkout, and input image.",
        },
        "research_only": True,
    }


def batch_run_command(args: argparse.Namespace) -> dict[str, Any]:
    plan = batch_plan_command(args)
    plan["command"] = "batch-run"
    if not args.confirm_execution:
        return error_payload(
            "batch-run",
            "execution_not_confirmed",
            "Refusing to run batch NV-Segment-CTMR inference without --confirm-execution.",
            "After the user has explicitly approved batch model execution and writes, rerun with --confirm-execution.",
            read_only=True,
            extra={"planned_run": plan, "required_flag": "--confirm-execution"},
        )

    source_dir = resolve_source_dir(args.source_dir)
    model_path = selected_model_path(source_dir, args.model_path)
    input_dir = Path(args.input_dir).expanduser()
    output_dir = Path(args.output_dir).expanduser()
    errors: list[dict[str, str]] = []
    warnings = list(plan.get("warnings", []))
    files = iter_nifti_files(input_dir, args.recursive)
    if not source_ready(source_dir):
        errors.append(
            {
                "kind": "missing_source_checkout",
                "message": "A local NV-Segment-CTMR source checkout with configs/inference.json is required.",
                "suggested_fix": "Pass --source-dir or set NV_SEGMENT_CTMR_DIR to the inner NV-Segment-CTMR directory.",
            }
        )
    if model_path is None or not model_path.exists():
        errors.append(
            {
                "kind": "missing_model_weights",
                "message": "Model weights are required before batch execution.",
                "suggested_fix": "Pass --model-path or place model.pt under <source-dir>/models/model.pt after reviewing model terms.",
            }
        )
    if not files:
        errors.append(
            {
                "kind": "no_inputs",
                "message": f"No .nii or .nii.gz files were found under {input_dir}.",
                "suggested_fix": "Provide an input directory containing local NIfTI volumes.",
            }
        )
    if not path_writable(output_dir):
        errors.append(
            {
                "kind": "output_dir_not_writable",
                "message": f"Output directory must already exist and be writable: {output_dir}",
                "suggested_fix": "Create the output directory, confirm it is writable, then rerun.",
            }
        )
    missing_dependencies = [name for name in ["monai", "torch"] if not importable(name)["available"]]
    if missing_dependencies:
        errors.append(
            {
                "kind": "missing_runtime_dependency",
                "message": f"Missing Python dependencies: {', '.join(missing_dependencies)}",
                "suggested_fix": "Run from the NV-Segment-CTMR Python environment with MONAI and PyTorch installed.",
            }
        )
    if errors:
        return {
            "ok": False,
            "command": "batch-run",
            "read_only": False,
            "outputs_written": False,
            "errors": errors,
            "error": errors[0],
            "warnings": warnings,
            "planned_run": plan,
            "research_only": True,
        }

    command = plan["multi_gpu_command"] if args.gpus > 1 and plan.get("multi_gpu_command") else plan["planned_command"]
    started_at = utc_now()
    try:
        result = subprocess.run(
            command,
            cwd=source_dir,
            capture_output=True,
            text=True,
            check=False,
            timeout=int(args.timeout_seconds),
        )
    except subprocess.TimeoutExpired as exc:
        return error_payload(
            "batch-run",
            "execution_timeout",
            f"Batch segmentation exceeded {args.timeout_seconds} seconds.",
            "Increase --timeout-seconds or inspect partial outputs before rerunning.",
            read_only=False,
            outputs_written=True,
            warnings=warnings,
            extra={"stdout_tail": command_tail(exc.stdout or ""), "stderr_tail": command_tail(exc.stderr or ""), "planned_run": plan},
        )
    logs_dir = output_dir / "_nv_segment_ctmr_logs"
    logs_dir.mkdir(exist_ok=True)
    stdout_path = logs_dir / "batch_stdout.txt"
    stderr_path = logs_dir / "batch_stderr.txt"
    provenance_path = logs_dir / "batch_provenance.json"
    stdout_path.write_text(result.stdout, encoding="utf-8")
    stderr_path.write_text(result.stderr, encoding="utf-8")
    verifications = []
    for path in files[: args.max_verify_outputs]:
        expected = expected_output_for_image(output_dir, path)
        if expected.exists():
            verifications.append(
                verify_output_command(
                    argparse.Namespace(segmentation=str(expected), max_label_values=args.max_label_values, no_label_summary=False)
                )
            )
    provenance = {
        "source_repo": SOURCE_REPO_URL,
        "source_commit": source_commit(source_dir),
        "model_card": MODEL_CARD_URL,
        "model_path": posix(model_path),
        "command": command,
        "working_dir": posix(source_dir),
        "mode": args.mode.upper(),
        "input_dir": posix(input_dir),
        "output_dir": posix(output_dir),
        "input_count": len(files),
        "started_at": started_at,
        "finished_at": utc_now(),
        "returncode": result.returncode,
        "warnings": warnings,
        "research_only": True,
    }
    provenance_path.write_text(json.dumps(provenance, indent=2, sort_keys=True), encoding="utf-8")
    return {
        "ok": result.returncode == 0,
        "command": "batch-run",
        "read_only": False,
        "outputs_written": True,
        "returncode": result.returncode,
        "planned_run": plan,
        "log_paths": {"stdout": posix(stdout_path), "stderr": posix(stderr_path), "provenance": posix(provenance_path)},
        "stdout_tail": command_tail(result.stdout),
        "stderr_tail": command_tail(result.stderr),
        "output_verifications": verifications,
        "provenance": provenance,
        "warnings": warnings,
        "error": None
        if result.returncode == 0
        else {
            "kind": "upstream_execution_failed",
            "message": f"Batch NV-Segment-CTMR command exited with code {result.returncode}.",
            "suggested_fix": "Inspect stderr/stdout logs and confirm source checkout, model weights, input modality, and runtime environment.",
        },
        "research_only": True,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read-only agent CLI for NV-Segment-CTMR planning workflows.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    sub = parser.add_subparsers(dest="command", required=True)

    schema = sub.add_parser("schema", help="Show the agent-facing command schema.")
    schema.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    schema.set_defaults(func=lambda args: command_schema())

    check = sub.add_parser("check", help="Inspect local readiness without running inference.")
    check.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    check.add_argument("--source-dir", default=None, help="Path to the inner NV-Segment-CTMR source directory.")
    check.add_argument("--model-path", default=None, help="Path to model.pt.")
    check.add_argument("--output-dir", default=None, help="Optional output directory to inspect.")
    check.set_defaults(func=check_environment)

    setup_plan = sub.add_parser("setup-plan", help="Build a read-only WSL2/Linux runtime setup plan.")
    setup_plan.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    setup_plan.add_argument("--target", choices=["wsl2-linux", "linux"], default="wsl2-linux")
    setup_plan.add_argument("--runtime-dir", default=DEFAULT_RUNTIME_DIR)
    setup_plan.add_argument("--env-name", default=DEFAULT_CONDA_ENV)
    setup_plan.add_argument("--python-version", default=DEFAULT_PYTHON_VERSION)
    setup_plan.set_defaults(func=setup_plan_command)

    labels = sub.add_parser("labels", help="Search label candidates.")
    labels.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    labels.add_argument("--query", required=True)
    labels.add_argument("--source-dir", default=None, help="Path to local NV-Segment-CTMR source for full label metadata.")
    labels.add_argument("--limit", type=int, default=10)
    labels.set_defaults(func=labels_command)

    plan = sub.add_parser("plan", help="Build a read-only segmentation command plan.")
    plan.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    plan.add_argument("--image", required=True)
    plan.add_argument("--mode", required=True, choices=sorted(VALID_MODES))
    plan.add_argument("--output-dir", required=True)
    plan.add_argument("--source-dir", default=None)
    plan.add_argument("--model-path", default=None)
    plan.add_argument("--label-id", action="append", help="Label ID or comma-separated label IDs for label-prompt segmentation.")
    plan.add_argument("--brain-script", action="store_true", help="Plan the upstream brain MRI shell script for MRI_BRAIN.")
    plan.add_argument("--no-skullstrip", action="store_true")
    plan.add_argument("--keep-temp", action="store_true")
    plan.set_defaults(func=plan_command)

    brain_plan = sub.add_parser("brain-plan", help="Build a read-only brain MRI segmentation plan.")
    brain_plan.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    brain_plan.add_argument("--image", required=True)
    brain_plan.add_argument("--output-dir", required=True)
    brain_plan.add_argument("--source-dir", default=None)
    brain_plan.add_argument("--model-path", default=None)
    brain_plan.add_argument("--no-skullstrip", action="store_true")
    brain_plan.add_argument("--keep-temp", action="store_true")
    brain_plan.set_defaults(func=brain_plan_command)

    batch_plan = sub.add_parser("batch-plan", help="Build a read-only batch segmentation plan.")
    batch_plan.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    batch_plan.add_argument("--input-dir", required=True)
    batch_plan.add_argument("--mode", required=True, choices=sorted(VALID_MODES))
    batch_plan.add_argument("--output-dir", required=True)
    batch_plan.add_argument("--source-dir", default=None)
    batch_plan.add_argument("--model-path", default=None)
    batch_plan.add_argument("--recursive", action="store_true")
    batch_plan.add_argument("--skip-existing", action="store_true")
    batch_plan.add_argument("--gpus", type=int, default=1)
    batch_plan.add_argument("--max-items", type=int, default=50)
    batch_plan.set_defaults(func=batch_plan_command)

    verify = sub.add_parser("verify-output", help="Verify an output segmentation NIfTI without modifying it.")
    verify.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    verify.add_argument("--segmentation", required=True, help="Path to the output segmentation NIfTI file.")
    verify.add_argument(
        "--max-label-values",
        type=int,
        default=50,
        help="Maximum sorted label values to include in the JSON summary.",
    )
    verify.add_argument("--no-label-summary", action="store_true", help="Skip reading label values from the file.")
    verify.set_defaults(func=verify_output_command)

    run = sub.add_parser("run", help="Run a guarded single-volume segmentation command after explicit approval.")
    run.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    run.add_argument("--image", required=True)
    run.add_argument("--mode", required=True, choices=sorted(VALID_MODES))
    run.add_argument("--output-dir", required=True)
    run.add_argument("--source-dir", default=None)
    run.add_argument("--model-path", default=None)
    run.add_argument("--label-id", action="append", help="Label ID or comma-separated label IDs for label-prompt segmentation.")
    run.add_argument("--confirm-execution", action="store_true", help="Required explicit approval gate for model execution and writes.")
    run.add_argument("--timeout-seconds", type=int, default=7200)
    run.add_argument("--max-label-values", type=int, default=50)
    run.set_defaults(func=run_command)

    brain_run = sub.add_parser("brain-run", help="Run guarded brain MRI preprocessing and segmentation after explicit approval.")
    brain_run.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    brain_run.add_argument("--image", required=True)
    brain_run.add_argument("--output-dir", required=True)
    brain_run.add_argument("--source-dir", default=None)
    brain_run.add_argument("--model-path", default=None)
    brain_run.add_argument("--no-skullstrip", action="store_true")
    brain_run.add_argument("--keep-temp", action="store_true")
    brain_run.add_argument("--confirm-execution", action="store_true", help="Required explicit approval gate for preprocessing, model execution, and writes.")
    brain_run.add_argument("--timeout-seconds", type=int, default=7200)
    brain_run.add_argument("--max-label-values", type=int, default=50)
    brain_run.set_defaults(func=brain_run_command)

    batch_run = sub.add_parser("batch-run", help="Run guarded batch segmentation after explicit approval.")
    batch_run.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    batch_run.add_argument("--input-dir", required=True)
    batch_run.add_argument("--mode", required=True, choices=sorted(VALID_MODES))
    batch_run.add_argument("--output-dir", required=True)
    batch_run.add_argument("--source-dir", default=None)
    batch_run.add_argument("--model-path", default=None)
    batch_run.add_argument("--recursive", action="store_true")
    batch_run.add_argument("--skip-existing", action="store_true")
    batch_run.add_argument("--gpus", type=int, default=1)
    batch_run.add_argument("--max-items", type=int, default=50)
    batch_run.add_argument("--max-verify-outputs", type=int, default=10)
    batch_run.add_argument("--max-label-values", type=int, default=50)
    batch_run.add_argument("--confirm-execution", action="store_true", help="Required explicit approval gate for batch model execution and writes.")
    batch_run.add_argument("--timeout-seconds", type=int, default=14400)
    batch_run.set_defaults(func=batch_run_command)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if getattr(args, "source_dir", None) is None:
        import os

        args.source_dir = os.environ.get("NV_SEGMENT_CTMR_DIR")
    try:
        payload = args.func(args)
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        payload = {
            "ok": False,
            "command": getattr(args, "command", None),
            "error": {"kind": exc.__class__.__name__, "message": str(exc)},
        }
    if args.json:
        print_json(payload)
    else:
        if payload.get("ok"):
            print(f"{payload.get('command', 'command')}: ok")
            for warning in payload.get("warnings", []):
                print(f"warning: {warning}")
        else:
            error = payload.get("error", {})
            print(f"{payload.get('command', 'command')}: failed: {error.get('message', 'unknown error')}", file=sys.stderr)
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
