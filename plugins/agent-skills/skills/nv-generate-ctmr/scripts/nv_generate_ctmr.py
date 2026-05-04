from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from typing import Any


SCRIPT_PATH = "skills/nv-generate-ctmr/scripts/nv_generate_ctmr.py"
SCHEMA_VERSION = "0.1"
SOURCE_REPO_URL = "https://github.com/NVIDIA-Medtech/NV-Generate-CTMR/tree/main"
SOURCE_CLONE_URL = "https://github.com/NVIDIA-Medtech/NV-Generate-CTMR.git"
PINNED_SOURCE_COMMIT = "40f5109dc77eaf01fbc5741809003f89ca3a36c7"
DEFAULT_RUNTIME_DIR = "~/.skillforge/runtime/nv-generate-ctmr"
DEFAULT_LINUX_PYTHON = "python3"


MODALITY_MAPPING = {
    "unknown": 0,
    "ct": 1,
    "ct_wo_contrast": 2,
    "ct_contrast": 3,
    "mri": 8,
    "mri_t1": 9,
    "mri_t2": 10,
    "mri_flair": 11,
    "mri_pd": 12,
    "mri_dwi": 13,
    "mri_adc": 14,
    "mri_ssfp": 15,
    "mri_mra": 16,
    "mri_t1c": 17,
    "mri_swi": 20,
    "mri_t1_skull_stripped": 29,
    "mri_t2_skull_stripped": 30,
    "mri_flair_skull_stripped": 31,
    "mri_swi_skull_stripped": 32,
    "mri_mra_skull_stripped": 33,
}


MODEL_VARIANTS: dict[str, dict[str, Any]] = {
    "rflow-mr-brain": {
        "modality_family": "MRI brain",
        "network": "rflow",
        "architecture": "MAISI-v2 rectified flow",
        "default_workflow": "image-only",
        "supported_workflows": ["image-only"],
        "default_contrast": "mri_t1",
        "supported_contrasts": [
            "mri",
            "mri_t1",
            "mri_t2",
            "mri_flair",
            "mri_swi",
            "mri_t1_skull_stripped",
            "mri_t2_skull_stripped",
            "mri_flair_skull_stripped",
            "mri_swi_skull_stripped",
        ],
        "inference_steps": 30,
        "max_volume": [512, 512, 256],
        "model_repo": "nvidia/NV-Generate-MR-Brain",
        "license": "NVIDIA Open Model License",
        "use_case": "Brain MRI image-only generation with whole-brain or skull-stripped contrasts.",
        "network_config": "./configs/config_network_rflow.json",
        "model_config": "./configs/config_maisi_diff_model_rflow-mr-brain.json",
        "environment_config": "./configs/environment_maisi_diff_model_rflow-mr-brain.json",
    },
    "rflow-mr": {
        "modality_family": "MRI",
        "network": "rflow",
        "architecture": "MAISI-v2 rectified flow",
        "default_workflow": "image-only",
        "supported_workflows": ["image-only"],
        "default_contrast": "mri_t2",
        "supported_contrasts": [
            "mri",
            "mri_t1",
            "mri_t2",
            "mri_flair",
            "mri_t1_skull_stripped",
            "mri_t2_skull_stripped",
            "mri_flair_skull_stripped",
        ],
        "inference_steps": 30,
        "max_volume": [512, 512, 128],
        "model_repo": "nvidia/NV-Generate-MR",
        "license": "NVIDIA Non-Commercial License",
        "use_case": "MRI image-only generation with user-selected contrast; upstream recommends rflow-mr-brain for brain MRI.",
        "network_config": "./configs/config_network_rflow.json",
        "model_config": "./configs/config_maisi_diff_model_rflow-mr.json",
        "environment_config": "./configs/environment_maisi_diff_model_rflow-mr.json",
    },
    "rflow-ct": {
        "modality_family": "CT",
        "network": "rflow",
        "architecture": "MAISI-v2 rectified flow",
        "default_workflow": "ct-paired",
        "supported_workflows": ["ct-paired", "image-only"],
        "default_contrast": "ct",
        "supported_contrasts": ["ct", "ct_wo_contrast", "ct_contrast"],
        "inference_steps": 30,
        "max_volume": [512, 512, 768],
        "model_repo": "nvidia/NV-Generate-CT",
        "license": "NVIDIA Open Model License",
        "use_case": "CT image/mask pair generation or CT image-only generation.",
        "network_config": "./configs/config_network_rflow.json",
        "paired_inference_config": "./configs/config_infer.json",
        "paired_environment_config": "./configs/environment_rflow-ct.json",
        "model_config": "./configs/config_maisi_diff_model_rflow-ct.json",
        "environment_config": "./configs/environment_maisi_diff_model_rflow-ct.json",
    },
    "ddpm-ct": {
        "modality_family": "CT",
        "network": "ddpm",
        "architecture": "MAISI-v1 DDPM",
        "default_workflow": "ct-paired",
        "supported_workflows": ["ct-paired", "image-only"],
        "default_contrast": "ct",
        "supported_contrasts": ["ct", "ct_wo_contrast", "ct_contrast"],
        "inference_steps": 1000,
        "max_volume": [512, 512, 768],
        "model_repo": "nvidia/NV-Generate-CT",
        "license": "NVIDIA Open Model License",
        "use_case": "Legacy CT image/mask pair generation or CT image-only generation.",
        "network_config": "./configs/config_network_ddpm.json",
        "paired_inference_config": "./configs/config_infer.json",
        "paired_environment_config": "./configs/environment_ddpm-ct.json",
        "model_config": "./configs/config_maisi_diff_model_ddpm-ct.json",
        "environment_config": "./configs/environment_maisi_diff_model_ddpm-ct.json",
    },
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def importable(module: str) -> dict[str, Any]:
    spec = importlib.util.find_spec(module)
    return {"module": module, "available": spec is not None}


def executable(name: str) -> dict[str, Any]:
    path = shutil.which(name)
    return {"name": name, "available": path is not None, "path": path}


def parse_int_triple(value: str, field_name: str) -> list[int]:
    parts = [part.strip() for part in value.split(",") if part.strip()]
    if len(parts) != 3:
        raise argparse.ArgumentTypeError(f"{field_name} must have three comma-separated integers")
    try:
        parsed = [int(part) for part in parts]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{field_name} must have integer values") from exc
    return parsed


def parse_float_triple(value: str, field_name: str) -> list[float]:
    parts = [part.strip() for part in value.split(",") if part.strip()]
    if len(parts) != 3:
        raise argparse.ArgumentTypeError(f"{field_name} must have three comma-separated numbers")
    try:
        parsed = [float(part) for part in parts]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{field_name} must have numeric values") from exc
    return parsed


def parse_anatomy_scale(values: list[str]) -> list[list[Any]]:
    parsed: list[list[Any]] = []
    for value in values:
        if ":" not in value:
            raise ValueError("Controllable anatomy size must use name:scale, for example liver:0.5")
        name, scale = value.split(":", 1)
        try:
            scale_value = float(scale)
        except ValueError as exc:
            raise ValueError(f"Invalid anatomy scale in {value!r}") from exc
        if scale_value < 0 or scale_value > 1:
            raise ValueError(f"Scale must be between 0 and 1 in {value!r}")
        parsed.append([name.strip(), scale_value])
    return parsed


def existing_path(value: str | None) -> Path | None:
    if not value:
        return None
    return Path(value).expanduser()


def resolved_output_path(value: str | None) -> Path | None:
    path = existing_path(value)
    if path is None:
        return None
    return path.resolve()


def resolve_source_dir(value: str | None) -> Path | None:
    source = existing_path(value)
    if source is None:
        return None
    candidates = [source, source / "NV-Generate-CTMR"]
    for candidate in candidates:
        if (candidate / "scripts" / "inference.py").exists() and (candidate / "configs").exists():
            return candidate
    return source


def posix(path: Path | None) -> str | None:
    if path is None:
        return None
    return path.as_posix()


def source_file(source_dir: Path | None, relative_path: str | None) -> Path | None:
    if source_dir is None or not relative_path:
        return None
    normalized = relative_path[2:] if relative_path.startswith("./") else relative_path
    return source_dir / normalized


def config_path_from_args(args: argparse.Namespace, key: str, fallback: str) -> str:
    value = getattr(args, key, None)
    return value or fallback


def choose_workflow(generate_version: str, workflow: str) -> str:
    variant = MODEL_VARIANTS[generate_version]
    if workflow == "auto":
        return variant["default_workflow"]
    if workflow not in variant["supported_workflows"]:
        supported = ", ".join(variant["supported_workflows"])
        raise ValueError(f"{generate_version} supports workflows: {supported}")
    return workflow


def source_status(source_dir: Path | None) -> dict[str, Any]:
    if source_dir is None:
        return {"provided": False, "valid": False, "path": None}
    return {
        "provided": True,
        "valid": (source_dir / "scripts" / "inference.py").exists() and (source_dir / "configs").exists(),
        "path": posix(source_dir),
        "has_inference_script": (source_dir / "scripts" / "inference.py").exists(),
        "has_diff_model_infer_script": (source_dir / "scripts" / "diff_model_infer.py").exists(),
        "has_configs": (source_dir / "configs").exists(),
    }


def build_config_preview(args: argparse.Namespace, workflow: str) -> dict[str, Any]:
    variant = MODEL_VARIANTS[args.generate_version]
    output_size = parse_int_triple(args.output_size, "output-size")
    spacing = parse_float_triple(args.spacing, "spacing")
    contrast = args.contrast or variant["default_contrast"]
    if contrast not in MODALITY_MAPPING:
        raise ValueError(f"Unknown contrast/modality: {contrast}")
    if contrast not in variant["supported_contrasts"]:
        raise ValueError(f"{contrast} is not a documented default contrast for {args.generate_version}")
    anatomy_size = parse_anatomy_scale(args.control_anatomy_size or [])

    if workflow == "ct-paired":
        return {
            "kind": "config_infer",
            "num_output_samples": args.samples,
            "body_region": args.body_region or ["chest"],
            "anatomy_list": args.anatomy or [],
            "controllable_anatomy_size": anatomy_size,
            "num_inference_steps": variant["inference_steps"],
            "mask_generation_num_inference_steps": 1000,
            "output_size": output_size,
            "image_output_ext": ".nii.gz",
            "label_output_ext": ".nii.gz",
            "spacing": spacing,
            "autoencoder_sliding_window_infer_size": parse_int_triple(
                args.autoencoder_window,
                "autoencoder-window",
            ),
            "autoencoder_sliding_window_infer_overlap": args.autoencoder_overlap,
            "modality": MODALITY_MAPPING[contrast],
            "cfg_guidance_scale": args.cfg_guidance_scale,
        }
    return {
        "kind": "diffusion_model_config_patch",
        "diffusion_unet_inference": {
            "dim": output_size,
            "spacing": spacing,
            "random_seed": args.random_seed,
            "num_inference_steps": variant["inference_steps"],
            "modality": MODALITY_MAPPING[contrast],
            "cfg_guidance_scale": args.cfg_guidance_scale or 10,
        },
        "environment_patch": {
            "output_dir": args.output_dir,
            "output_prefix": args.output_prefix,
        },
    }


def config_dir_paths(args: argparse.Namespace, workflow: str) -> dict[str, Path]:
    config_dir = resolved_output_path(args.config_dir)
    if config_dir is None:
        return {}
    stem = f"skillforge_{args.generate_version}_{workflow}".replace("-", "_")
    if workflow == "ct-paired":
        return {
            "inference_config": config_dir / f"{stem}_config_infer.json",
            "environment_config": config_dir / f"{stem}_environment.json",
        }
    return {
        "model_config": config_dir / f"{stem}_model_config.json",
        "environment_config": config_dir / f"{stem}_environment.json",
    }


def planned_config_path(args: argparse.Namespace, workflow: str, key: str, fallback: str) -> str:
    explicit = getattr(args, key, None)
    if explicit:
        return explicit
    generated = config_dir_paths(args, workflow).get(key)
    if generated is not None:
        return generated.as_posix()
    return fallback


def load_json_template(source_dir: Path | None, relative_path: str | None, fallback: dict[str, Any]) -> dict[str, Any]:
    path = source_file(source_dir, relative_path)
    if path is None or not path.exists():
        return dict(fallback)
    try:
        with path.open("r", encoding="utf-8") as handle:
            loaded = json.load(handle)
    except json.JSONDecodeError:
        return dict(fallback)
    if not isinstance(loaded, dict):
        return dict(fallback)
    return loaded


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_source_configs(args: argparse.Namespace, workflow: str) -> dict[str, Any]:
    paths = config_dir_paths(args, workflow)
    if not paths:
        raise ValueError("--config-dir is required to write source-compatible config files")

    variant = MODEL_VARIANTS[args.generate_version]
    source_dir = resolve_source_dir(args.source_dir)
    preview = build_config_preview(args, workflow)
    written: dict[str, str] = {}

    if workflow == "ct-paired":
        inference_config = dict(preview)
        inference_config.update(
            {
                "controlnet": "$@controlnet_def",
                "diffusion_unet": "$@diffusion_unet_def",
                "autoencoder": "$@autoencoder_def",
                "mask_generation_autoencoder": "$@mask_generation_autoencoder_def",
                "mask_generation_diffusion": "$@mask_generation_diffusion_def",
            }
        )
        environment_config = load_json_template(
            source_dir,
            variant["paired_environment_config"],
            {
                "output_dir": "output",
                "trained_autoencoder_path": "models/autoencoder_v1.pt",
                "trained_diffusion_path": f"models/diff_unet_3d_{args.generate_version}.pt",
                "trained_controlnet_path": f"models/controlnet_3d_{args.generate_version}.pt",
                "trained_mask_generation_autoencoder_path": "models/mask_generation_autoencoder.pt",
                "trained_mask_generation_diffusion_path": "models/mask_generation_diffusion_unet.pt",
                "label_dict_json": "./configs/label_dict.json",
                "label_dict_remap_json": "./configs/label_dict_124_to_132.json",
            },
        )
        environment_config["output_dir"] = args.output_dir
        write_json(paths["inference_config"], inference_config)
        write_json(paths["environment_config"], environment_config)
        written = {key: path.as_posix() for key, path in paths.items()}
    else:
        model_config = load_json_template(
            source_dir,
            variant["model_config"],
            {"diffusion_unet_inference": {}},
        )
        inference_block = model_config.setdefault("diffusion_unet_inference", {})
        if not isinstance(inference_block, dict):
            model_config["diffusion_unet_inference"] = {}
            inference_block = model_config["diffusion_unet_inference"]
        inference_block.update(preview["diffusion_unet_inference"])
        environment_config = load_json_template(
            source_dir,
            variant["environment_config"],
            {
                "output_dir": "./output",
                "output_prefix": "unet_3d",
                "model_dir": "./models",
                "modality_mapping_path": "./configs/modality_mapping.json",
            },
        )
        environment_config.update(preview["environment_patch"])
        write_json(paths["model_config"], model_config)
        write_json(paths["environment_config"], environment_config)
        written = {key: path.as_posix() for key, path in paths.items()}

    return {
        "config_dir": resolved_output_path(args.config_dir).as_posix() if args.config_dir else None,
        "written_files": written,
        "source_dir": source_status(source_dir),
    }


def planned_commands(args: argparse.Namespace, workflow: str) -> list[list[str]]:
    variant = MODEL_VARIANTS[args.generate_version]
    python_cmd = args.python_executable or "python"
    commands: list[list[str]] = []
    if workflow == "ct-paired":
        inference_config = planned_config_path(args, workflow, "inference_config", variant["paired_inference_config"])
        environment_config = planned_config_path(args, workflow, "environment_config", variant["paired_environment_config"])
        command = [
            python_cmd,
            "-m",
            "scripts.inference",
            "-t",
            variant["network_config"],
            "-i",
            inference_config,
            "-e",
            environment_config,
            "--random-seed",
            str(args.random_seed),
            "--version",
            args.generate_version,
        ]
        if args.use_tensorrt:
            command.extend(["-x", "./configs/config_trt.json"])
        commands.append(command)
    else:
        commands.append(
            [
                python_cmd,
                "-m",
                "scripts.download_model_data",
                "--version",
                args.generate_version,
                "--root_dir",
                "./",
                "--model_only",
            ]
        )
        model_config = planned_config_path(args, workflow, "model_config", variant["model_config"])
        environment_config = planned_config_path(args, workflow, "environment_config", variant["environment_config"])
        commands.append(
            [
                python_cmd,
                "-m",
                "scripts.diff_model_infer",
                "-t",
                variant["network_config"],
                "-e",
                environment_config,
                "-c",
                model_config,
                "-g",
                str(args.num_gpus),
            ]
        )
    return commands


def command_to_text(command: list[str]) -> str:
    return " ".join(command)


def build_plan(args: argparse.Namespace) -> dict[str, Any]:
    workflow = choose_workflow(args.generate_version, args.workflow)
    variant = MODEL_VARIANTS[args.generate_version]
    source_dir = resolve_source_dir(args.source_dir)
    source = source_status(source_dir)
    config_preview = build_config_preview(args, workflow)
    commands = planned_commands(args, workflow)
    blockers: list[str] = []
    warnings: list[str] = []
    if not source["valid"]:
        blockers.append("valid NV-Generate-CTMR source checkout was not provided")
    output_dir = existing_path(args.output_dir)
    if output_dir is None:
        blockers.append("output directory was not provided")
    if workflow == "ct-paired" and args.generate_version not in {"rflow-ct", "ddpm-ct"}:
        blockers.append("paired image/mask generation is CT-only in the documented upstream workflow")
    if workflow == "ct-paired" and not args.inference_config and not args.config_dir:
        warnings.append("Custom output_size, spacing, anatomy, and output_dir require a generated or edited inference/environment config.")
    if workflow == "image-only" and not args.model_config and not args.config_dir:
        warnings.append("Custom output_size, spacing, contrast, random_seed, and output_dir require a generated or edited model/environment config.")
    if args.config_dir:
        for key, path in config_dir_paths(args, workflow).items():
            if not path.exists():
                warnings.append(f"{key} was planned from --config-dir but does not exist yet: {path.as_posix()}")
    if args.use_tensorrt and workflow != "ct-paired":
        warnings.append("TensorRT acceleration is documented for the paired CT inference command, not the image-only command path.")

    return {
        "ok": True,
        "read_only": True,
        "command": "plan",
        "generated_at": utc_now(),
        "source_repo": SOURCE_REPO_URL,
        "pinned_source_commit": PINNED_SOURCE_COMMIT,
        "generate_version": args.generate_version,
        "workflow": workflow,
        "model_variant": variant,
        "contrast": args.contrast or variant["default_contrast"],
        "source_dir": source,
        "ready_to_execute": len(blockers) == 0,
        "blocking_reasons": blockers,
        "warnings": warnings,
        "config_preview": config_preview,
        "planned_commands": commands,
        "planned_command_text": [command_to_text(command) for command in commands],
        "expected_outputs": expected_outputs(args, workflow),
        "side_effects_if_executed": [
            "may download model weights and CT mask assets from Hugging Face",
            "uses CUDA/GPU memory and can be expensive",
            "writes generated NIfTI images, CT masks, logs, and cached model/data files",
            "uses user-provided output and source directories",
        ],
        "approval_required": [
            "--confirm-execution for any run",
            "--confirm-downloads if model/data downloads may occur",
            "license and usage-term review for the selected model weights",
        ],
        "sources": [
            SOURCE_REPO_URL,
            "https://github.com/NVIDIA-Medtech/NV-Generate-CTMR/blob/main/docs/inference.md",
            "https://github.com/NVIDIA-Medtech/NV-Generate-CTMR/blob/main/docs/setup.md",
            "https://huggingface.co/nvidia/NV-Generate-CT",
            "https://huggingface.co/nvidia/NV-Generate-MR",
            "https://huggingface.co/nvidia/NV-Generate-MR-Brain",
        ],
    }


def expected_outputs(args: argparse.Namespace, workflow: str) -> list[dict[str, str]]:
    if workflow == "ct-paired":
        return [
            {"type": "ct_image", "format": "NIfTI .nii.gz", "description": "synthetic CT volume"},
            {"type": "segmentation_mask", "format": "NIfTI .nii.gz", "description": "paired synthetic CT segmentation mask"},
        ]
    return [
        {
            "type": "image",
            "format": "NIfTI .nii.gz",
            "description": f"synthetic {MODEL_VARIANTS[args.generate_version]['modality_family']} image volume",
        }
    ]


def command_schema() -> dict[str, Any]:
    return {
        "ok": True,
        "schema_version": SCHEMA_VERSION,
        "script": SCRIPT_PATH,
        "commands": [
            {"name": "schema", "read_only": True},
            {"name": "check", "read_only": True},
            {"name": "setup-plan", "read_only": True},
            {"name": "models", "read_only": True},
            {"name": "modalities", "read_only": True},
            {"name": "config-template", "read_only": True, "can_write_with_output_file_or_config_dir": True},
            {"name": "plan", "read_only": True},
            {"name": "run", "read_only": False, "requires": ["--confirm-execution", "--confirm-downloads"]},
            {"name": "verify-output", "read_only": True},
        ],
        "generate_versions": sorted(MODEL_VARIANTS),
        "workflows": ["auto", "ct-paired", "image-only"],
        "risk_default": "planning-only",
    }


def command_check(args: argparse.Namespace) -> int:
    source_dir = resolve_source_dir(args.source_dir)
    payload = {
        "ok": True,
        "read_only": True,
        "command": "check",
        "generated_at": utc_now(),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "python": platform.python_version(),
        },
        "dependencies": [
            importable("torch"),
            importable("monai"),
            importable("nibabel"),
            importable("huggingface_hub"),
            importable("numpy"),
        ],
        "executables": [
            executable("git"),
            executable("python"),
            executable("nvidia-smi"),
            executable("torchrun"),
        ],
        "source_dir": source_status(source_dir),
        "notes": [
            "This check does not install dependencies, download weights, or run inference.",
            "Full execution requires CUDA-capable PyTorch, MONAI, model weights, and accepted model terms.",
        ],
    }
    print_json(payload) if args.json else print_human(payload)
    return 0


def command_setup_plan(args: argparse.Namespace) -> int:
    runtime_dir = args.runtime_dir or DEFAULT_RUNTIME_DIR
    target = args.target
    venv_python = ".venv/bin/python" if target != "windows" else ".venv\\Scripts\\python.exe"
    steps = [
        {
            "step": "clone source repository",
            "command": f"git clone {SOURCE_CLONE_URL} {runtime_dir}",
            "side_effect": "writes source checkout to runtime directory",
        },
        {
            "step": "pin source revision",
            "command": f"git checkout {PINNED_SOURCE_COMMIT}",
            "side_effect": "moves checkout to the source revision used for this skill evidence",
        },
        {
            "step": "create Python environment",
            "command": f"{python_setup_command(target)} -m venv .venv",
            "side_effect": "creates local virtual environment",
        },
        {
            "step": "install dependencies",
            "command": f"{venv_python} -m pip install -r requirements.txt",
            "side_effect": "downloads Python packages; PyTorch CUDA wheel may need a platform-specific index URL",
        },
        {
            "step": "optional model download",
            "command": f"{venv_python} -m scripts.download_model_data --version {args.generate_version} --root_dir ./ --model_only",
            "side_effect": "downloads model weights from Hugging Face",
        },
    ]
    payload = {
        "ok": True,
        "read_only": True,
        "command": "setup-plan",
        "target": target,
        "runtime_dir": runtime_dir,
        "generate_version": args.generate_version,
        "source_clone_url": SOURCE_CLONE_URL,
        "pinned_source_commit": PINNED_SOURCE_COMMIT,
        "requirements": {
            "python": "3.11+",
            "gpu": "NVIDIA GPU with at least 16GB VRAM; larger volumes can require 24GB, 40GB, or more",
            "cuda": "CUDA 11.8+ or CUDA 12.x per upstream setup guide",
            "monai": ">=1.5.0 for MR support; CT generation can work with older upstream minimums",
        },
        "commands": steps,
        "approval_required_before_execution": [
            "source clone",
            "Python environment creation",
            "dependency installation",
            "Hugging Face model/data download",
            "GPU execution",
        ],
        "platform_notes": platform_notes(target),
    }
    print_json(payload) if args.json else print_human(payload)
    return 0


def platform_notes(target: str) -> list[str]:
    if target == "windows":
        return [
            "Prefer WSL2/Linux for CUDA-heavy execution unless the upstream stack is verified on native Windows.",
            "Use Windows paths only for planning; upstream shell examples use POSIX-style commands.",
            "Use the Python launcher or an approved Python 3.11+ installation to create the virtual environment.",
        ]
    if target == "macos":
        return [
            "The upstream workflow expects NVIDIA CUDA GPU support; macOS is suitable for planning, not full inference.",
        ]
    if target == "wsl2-linux":
        return [
            "Use WSL2 with NVIDIA GPU passthrough and CUDA-enabled PyTorch.",
            "Keep model weights and generated volumes on a filesystem with enough space.",
            "On Ubuntu, install python3-venv and pip first if `python3 -m venv` or `.venv/bin/python -m pip` is unavailable.",
        ]
    return [
        "Use a Linux host with NVIDIA CUDA and enough GPU memory for the selected volume size.",
        "Install the distro's Python venv and pip packages first if the base Python lacks ensurepip.",
    ]


def python_setup_command(target: str) -> str:
    if target == "windows":
        return "py -3"
    return DEFAULT_LINUX_PYTHON


def command_models(args: argparse.Namespace) -> int:
    payload = {
        "ok": True,
        "read_only": True,
        "command": "models",
        "models": MODEL_VARIANTS,
    }
    print_json(payload) if args.json else print_human(payload)
    return 0


def command_modalities(args: argparse.Namespace) -> int:
    payload = {
        "ok": True,
        "read_only": True,
        "command": "modalities",
        "modalities": [{"name": name, "id": value} for name, value in MODALITY_MAPPING.items()],
    }
    print_json(payload) if args.json else print_human(payload)
    return 0


def command_config_template(args: argparse.Namespace) -> int:
    try:
        workflow = choose_workflow(args.generate_version, args.workflow)
        preview = build_config_preview(args, workflow)
    except ValueError as exc:
        payload = {"ok": False, "error": str(exc), "command": "config-template"}
        print_json(payload) if args.json else print_human(payload)
        return 2
    payload = {
        "ok": True,
        "read_only": args.output_file is None and args.config_dir is None,
        "command": "config-template",
        "generate_version": args.generate_version,
        "workflow": workflow,
        "config": preview,
        "written_file": None,
        "source_configs": None,
    }
    if args.output_file:
        path = Path(args.output_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(preview, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        payload["written_file"] = path.as_posix()
    if args.config_dir:
        try:
            payload["source_configs"] = write_source_configs(args, workflow)
        except ValueError as exc:
            payload = {"ok": False, "error": str(exc), "command": "config-template"}
            print_json(payload) if args.json else print_human(payload)
            return 2
    print_json(payload) if args.json else print_human(payload)
    return 0


def command_plan(args: argparse.Namespace) -> int:
    try:
        payload = build_plan(args)
    except ValueError as exc:
        payload = {"ok": False, "error": str(exc), "command": "plan"}
        print_json(payload) if args.json else print_human(payload)
        return 2
    print_json(payload) if args.json else print_human(payload)
    return 0


def command_run(args: argparse.Namespace) -> int:
    try:
        plan = build_plan(args)
    except ValueError as exc:
        payload = {"ok": False, "error": {"kind": "invalid_plan", "message": str(exc)}, "command": "run"}
        print_json(payload) if args.json else print_human(payload)
        return 2
    if not args.confirm_execution:
        payload = {
            "ok": False,
            "error": {
                "kind": "execution_not_confirmed",
                "message": "Refusing to run NV-Generate-CTMR without --confirm-execution.",
            },
            "planned_run": plan,
        }
        print_json(payload) if args.json else print_human(payload)
        return 2
    if not args.confirm_downloads:
        payload = {
            "ok": False,
            "error": {
                "kind": "downloads_not_confirmed",
                "message": "Refusing because upstream commands may download model/data assets without --confirm-downloads.",
            },
            "planned_run": plan,
        }
        print_json(payload) if args.json else print_human(payload)
        return 2
    if not plan["ready_to_execute"]:
        payload = {
            "ok": False,
            "error": {"kind": "not_ready", "message": "; ".join(plan["blocking_reasons"])},
            "planned_run": plan,
        }
        print_json(payload) if args.json else print_human(payload)
        return 2

    source_dir = Path(plan["source_dir"]["path"])
    completed = []
    for command in plan["planned_commands"]:
        result = subprocess.run(
            command,
            cwd=source_dir,
            capture_output=True,
            text=True,
            check=False,
            timeout=args.timeout_seconds,
        )
        completed.append(
            {
                "command": command,
                "returncode": result.returncode,
                "stdout_tail": result.stdout[-4000:],
                "stderr_tail": result.stderr[-4000:],
            }
        )
        if result.returncode != 0:
            payload = {"ok": False, "command": "run", "failed_step": completed[-1], "completed_steps": completed}
            print_json(payload) if args.json else print_human(payload)
            return result.returncode or 1

    payload = {
        "ok": True,
        "command": "run",
        "planned_run": plan,
        "completed_steps": completed,
        "provenance": {
            "source_repo": SOURCE_REPO_URL,
            "pinned_source_commit": PINNED_SOURCE_COMMIT,
            "generated_at": utc_now(),
            "generate_version": args.generate_version,
        },
    }
    print_json(payload) if args.json else print_human(payload)
    return 0


def command_verify_output(args: argparse.Namespace) -> int:
    image = Path(args.image)
    payload: dict[str, Any] = {
        "ok": image.exists(),
        "read_only": True,
        "command": "verify-output",
        "image": image.as_posix(),
        "exists": image.exists(),
        "bytes": image.stat().st_size if image.exists() else None,
        "nifti_readable": False,
    }
    if image.exists():
        try:
            import nibabel as nib  # type: ignore

            nii = nib.load(str(image))
            payload.update(
                {
                    "nifti_readable": True,
                    "shape": [int(value) for value in nii.shape],
                    "zooms": [float(value) for value in nii.header.get_zooms()],
                    "dtype": str(nii.get_data_dtype()),
                }
            )
        except Exception as exc:  # pragma: no cover - depends on optional local files
            payload["nifti_error"] = str(exc)
    print_json(payload) if args.json else print_human(payload)
    return 0 if payload["ok"] else 2


def print_human(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def add_generation_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--generate-version", choices=sorted(MODEL_VARIANTS), default="rflow-ct")
    parser.add_argument("--workflow", choices=["auto", "ct-paired", "image-only"], default="auto")
    parser.add_argument("--contrast", choices=sorted(MODALITY_MAPPING), default=None)
    parser.add_argument("--source-dir", default=None)
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--output-prefix", default="unet_3d")
    parser.add_argument("--config-dir", default=None)
    parser.add_argument("--output-size", default="256,256,256")
    parser.add_argument("--spacing", default="1.5,1.5,2.0")
    parser.add_argument("--body-region", action="append", default=[])
    parser.add_argument("--anatomy", action="append", default=[])
    parser.add_argument("--control-anatomy-size", action="append", default=[])
    parser.add_argument("--samples", type=int, default=1)
    parser.add_argument("--random-seed", type=int, default=0)
    parser.add_argument("--num-gpus", type=int, default=1)
    parser.add_argument("--cfg-guidance-scale", type=float, default=0)
    parser.add_argument("--autoencoder-window", default="48,48,48")
    parser.add_argument("--autoencoder-overlap", type=float, default=0.6666)
    parser.add_argument("--inference-config", default=None)
    parser.add_argument("--model-config", default=None)
    parser.add_argument("--environment-config", default=None)
    parser.add_argument("--python-executable", default=None)
    parser.add_argument("--use-tensorrt", action="store_true")
    parser.add_argument("--json", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SkillForge adapter for NV-Generate-CTMR")
    subparsers = parser.add_subparsers(dest="command", required=True)

    schema_parser = subparsers.add_parser("schema")
    schema_parser.add_argument("--json", action="store_true")
    schema_parser.set_defaults(func=lambda args: (print_json(command_schema()) if args.json else print_human(command_schema())) or 0)

    check_parser = subparsers.add_parser("check")
    check_parser.add_argument("--source-dir", default=None)
    check_parser.add_argument("--json", action="store_true")
    check_parser.set_defaults(func=command_check)

    setup_parser = subparsers.add_parser("setup-plan")
    setup_parser.add_argument("--target", choices=["wsl2-linux", "linux", "windows", "macos"], default="wsl2-linux")
    setup_parser.add_argument("--runtime-dir", default=DEFAULT_RUNTIME_DIR)
    setup_parser.add_argument("--generate-version", choices=sorted(MODEL_VARIANTS), default="rflow-ct")
    setup_parser.add_argument("--json", action="store_true")
    setup_parser.set_defaults(func=command_setup_plan)

    models_parser = subparsers.add_parser("models")
    models_parser.add_argument("--json", action="store_true")
    models_parser.set_defaults(func=command_models)

    modalities_parser = subparsers.add_parser("modalities")
    modalities_parser.add_argument("--json", action="store_true")
    modalities_parser.set_defaults(func=command_modalities)

    config_parser = subparsers.add_parser("config-template")
    add_generation_args(config_parser)
    config_parser.add_argument("--output-file", default=None)
    config_parser.set_defaults(func=command_config_template)

    plan_parser = subparsers.add_parser("plan")
    add_generation_args(plan_parser)
    plan_parser.set_defaults(func=command_plan)

    run_parser = subparsers.add_parser("run")
    add_generation_args(run_parser)
    run_parser.add_argument("--confirm-execution", action="store_true")
    run_parser.add_argument("--confirm-downloads", action="store_true")
    run_parser.add_argument("--timeout-seconds", type=int, default=3600)
    run_parser.set_defaults(func=command_run)

    verify_parser = subparsers.add_parser("verify-output")
    verify_parser.add_argument("--image", required=True)
    verify_parser.add_argument("--json", action="store_true")
    verify_parser.set_defaults(func=command_verify_output)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
