from __future__ import annotations

import argparse
import csv
import datetime as dt
import html
import importlib.util
import json
import math
from pathlib import Path
import platform
import re
import sys
from typing import Any
from zipfile import ZipFile


SCHEMA_VERSION = "0.1"
OUTPUT_MASK_NAME = "roi_mask.nii.gz"
SUMMARY_NAME = "roi_summary.json"
PROVENANCE_NAME = "provenance.json"
SCRIPT_PATH = "skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py"

MRI_BRAIN_LABELS = {
    214: "3rd-Ventricle",
    215: "4th-Ventricle",
    216: "Right-Accumbens-Area",
    217: "Left-Accumbens-Area",
    218: "Right-Amygdala",
    219: "Left-Amygdala",
    220: "Brain-Stem",
    221: "Right-Caudate",
    222: "Left-Caudate",
    223: "Right-Cerebellum-Exterior",
    224: "Left-Cerebellum-Exterior",
    225: "Right-Cerebellum-White-Matter",
    226: "Left-Cerebellum-White-Matter",
    227: "Right-Cerebral-White-Matter",
    228: "Left-Cerebral-White-Matter",
    229: "Right-Hippocampus",
    230: "Left-Hippocampus",
    231: "Right-Inf-Lat-Vent",
    232: "Left-Inf-Lat-Vent",
    233: "Right-Lateral-Ventricle",
    234: "Left-Lateral-Ventricle",
    235: "Right-Pallidum",
    236: "Left-Pallidum",
    237: "Right-Putamen",
    238: "Left-Putamen",
    239: "Right-Thalamus-Proper",
    240: "Left-Thalamus-Proper",
    241: "Right-Ventral-DC",
    242: "Left-Ventral-DC",
    243: "Cerebellar-Vermal-Lobules-I-V",
    244: "Cerebellar-Vermal-Lobules-VI-VII",
    245: "Cerebellar-Vermal-Lobules-VIII-X",
    246: "Left-Basal-Forebrain",
    247: "Right-Basal-Forebrain",
    248: "Right-ACgG--anterior-cingulate-gyrus",
    249: "Left-ACgG--anterior-cingulate-gyrus",
    250: "Right-AIns--anterior-insula",
    251: "Left-AIns--anterior-insula",
    252: "Right-AOrG--anterior-orbital-gyrus",
    253: "Left-AOrG--anterior-orbital-gyrus",
    254: "Right-AnG---angular-gyrus",
    255: "Left-AnG---angular-gyrus",
    256: "Right-Calc--calcarine-cortex",
    257: "Left-Calc--calcarine-cortex",
    258: "Right-CO----central-operculum",
    259: "Left-CO----central-operculum",
    260: "Right-Cun---cuneus",
    261: "Left-Cun---cuneus",
    262: "Right-Ent---entorhinal-area",
    263: "Left-Ent---entorhinal-area",
    264: "Right-FO----frontal-operculum",
    265: "Left-FO----frontal-operculum",
    266: "Right-FRP---frontal-pole",
    267: "Left-FRP---frontal-pole",
    268: "Right-FuG---fusiform-gyrus",
    269: "Left-FuG---fusiform-gyrus",
    270: "Right-GRe---gyrus-rectus",
    271: "Left-GRe---gyrus-rectus",
    272: "Right-IOG---inferior-occipital-gyrus",
    273: "Left-IOG---inferior-occipital-gyrus",
    274: "Right-ITG---inferior-temporal-gyrus",
    275: "Left-ITG---inferior-temporal-gyrus",
    276: "Right-LiG---lingual-gyrus",
    277: "Left-LiG---lingual-gyrus",
    278: "Right-LOrG--lateral-orbital-gyrus",
    279: "Left-LOrG--lateral-orbital-gyrus",
    280: "Right-MCgG--middle-cingulate-gyrus",
    281: "Left-MCgG--middle-cingulate-gyrus",
    282: "Right-MFC---medial-frontal-cortex",
    283: "Left-MFC---medial-frontal-cortex",
    284: "Right-MFG---middle-frontal-gyrus",
    285: "Left-MFG---middle-frontal-gyrus",
    286: "Right-MOG---middle-occipital-gyrus",
    287: "Left-MOG---middle-occipital-gyrus",
    288: "Right-MOrG--medial-orbital-gyrus",
    289: "Left-MOrG--medial-orbital-gyrus",
    290: "Right-MPoG--postcentral-gyrus",
    291: "Left-MPoG--postcentral-gyrus",
    292: "Right-MPrG--precentral-gyrus",
    293: "Left-MPrG--precentral-gyrus",
    294: "Right-MSFG--superior-frontal-gyrus",
    295: "Left-MSFG--superior-frontal-gyrus",
    296: "Right-MTG---middle-temporal-gyrus",
    297: "Left-MTG---middle-temporal-gyrus",
    298: "Right-OCP---occipital-pole",
    299: "Left-OCP---occipital-pole",
    300: "Right-OFuG--occipital-fusiform-gyrus",
    301: "Left-OFuG--occipital-fusiform-gyrus",
    302: "Right-OpIFG-opercular-part-of-the-IFG",
    303: "Left-OpIFG-opercular-part-of-the-IFG",
    304: "Right-OrIFG-orbital-part-of-the-IFG",
    305: "Left-OrIFG-orbital-part-of-the-IFG",
    306: "Right-PCgG--posterior-cingulate-gyrus",
    307: "Left-PCgG--posterior-cingulate-gyrus",
    308: "Right-PCu---precuneus",
    309: "Left-PCu---precuneus",
    310: "Right-PHG---parahippocampal-gyrus",
    311: "Left-PHG---parahippocampal-gyrus",
    312: "Right-PIns--posterior-insula",
    313: "Left-PIns--posterior-insula",
    314: "Right-PO----parietal-operculum",
    315: "Left-PO----parietal-operculum",
    316: "Right-PoG---postcentral-gyrus",
    317: "Left-PoG---postcentral-gyrus",
    318: "Right-POrG--posterior-orbital-gyrus",
    319: "Left-POrG--posterior-orbital-gyrus",
    320: "Right-PP----planum-polare",
    321: "Left-PP----planum-polare",
    322: "Right-PrG---precentral-gyrus",
    323: "Left-PrG---precentral-gyrus",
    324: "Right-PT----planum-temporale",
    325: "Left-PT----planum-temporale",
    326: "Right-SCA---subcallosal-area",
    327: "Left-SCA---subcallosal-area",
    328: "Right-SFG---superior-frontal-gyrus",
    329: "Left-SFG---superior-frontal-gyrus",
    330: "Right-SMC---supplementary-motor-cortex",
    331: "Left-SMC---supplementary-motor-cortex",
    332: "Right-SMG---supramarginal-gyrus",
    333: "Left-SMG---supramarginal-gyrus",
    334: "Right-SOG---superior-occipital-gyrus",
    335: "Left-SOG---superior-occipital-gyrus",
    336: "Right-SPL---superior-parietal-lobule",
    337: "Left-SPL---superior-parietal-lobule",
    338: "Right-STG---superior-temporal-gyrus",
    339: "Left-STG---superior-temporal-gyrus",
    340: "Right-TMP---temporal-pole",
    341: "Left-TMP---temporal-pole",
    342: "Right-TrIFG-triangular-part-of-the-IFG",
    343: "Left-TrIFG-triangular-part-of-the-IFG",
    344: "Right-TTG---transverse-temporal-gyrus",
    345: "Left-TTG---transverse-temporal-gyrus",
}

IMPRESSION_ANATOMY_TERMS = [
    {
        "region": "Brainstem",
        "patterns": ["brainstem", "brain stem"],
        "labels": [220],
        "note": "Exact MRI brain segmentation label is available.",
    },
    {
        "region": "Cerebellum",
        "patterns": ["cerebellum", "cerebellar"],
        "labels": [223, 224, 225, 226, 243, 244, 245],
        "note": "Cerebellar exterior, white matter, and vermal labels are available.",
    },
    {
        "region": "Ventricles",
        "patterns": ["ventricle", "ventricles"],
        "labels": [214, 215, 231, 232, 233, 234],
        "note": "Ventricular labels are available in the MRI brain segmentation.",
    },
    {
        "region": "Cerebral parenchyma",
        "patterns": ["cerebral parenchyma"],
        "labels": [],
        "note": "The selected segmentation has many cerebral structure labels, but no single cerebral parenchyma mask.",
    },
    {
        "region": "Cerebral arterial system",
        "patterns": ["cerebral mr angiography", "cerebral mra", "mr angiography", "mra"],
        "labels": [],
        "note": "The selected MRI brain segmentation does not include arterial vessel masks.",
    },
    {
        "region": "Left sphenoidal sinus",
        "patterns": ["left sphenoidal", "left sphenoid"],
        "labels": [],
        "note": "Paranasal sinus masks are not present in the selected MRI brain segmentation.",
    },
    {
        "region": "Right ethmoidal sinus",
        "patterns": ["right ethmoidal", "right ethmoid"],
        "labels": [],
        "note": "Paranasal sinus masks are not present in the selected MRI brain segmentation.",
    },
    {
        "region": "Right vertebral artery",
        "patterns": ["right va", "right vertebral artery"],
        "labels": [],
        "note": "Vertebral artery masks are not present in the selected MRI brain segmentation.",
    },
    {
        "region": "Left P1 segment",
        "patterns": ["left p1", "p1 hypoplasia", "p1 hypoplasias"],
        "labels": [],
        "note": "Posterior cerebral artery segment masks are not present in the selected MRI brain segmentation.",
    },
    {
        "region": "Cranial MRI / brain",
        "patterns": ["cranial mri"],
        "labels": [],
        "note": "This is an exam-level statement, not a single segmentation target.",
        "context_only": True,
    },
]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def dependency_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def dependency_report() -> dict[str, Any]:
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "dependencies": {
            "numpy": dependency_available("numpy"),
            "nibabel": dependency_available("nibabel"),
            "PIL": dependency_available("PIL"),
        },
    }


def parse_labels(value: str) -> list[int]:
    labels: list[int] = []
    for part in value.split(","):
        text = part.strip()
        if not text:
            continue
        try:
            labels.append(int(text))
        except ValueError as exc:
            raise argparse.ArgumentTypeError(f"Label must be an integer: {text}") from exc
    if not labels:
        raise argparse.ArgumentTypeError("At least one label ID is required")
    return labels


def nifti_suffix_ok(path: Path) -> bool:
    name = path.name.lower()
    return name.endswith(".nii") or name.endswith(".nii.gz")


def strip_nifti_suffix(name: str) -> str:
    lowered = name.lower()
    if lowered.endswith(".nii.gz"):
        return name[:-7]
    if lowered.endswith(".nii"):
        return name[:-4]
    return name


def zip_study_uid(path: str) -> str | None:
    parts = path.replace("\\", "/").split("/")
    return parts[0] if parts else None


def safe_write_zip_entry(zip_file: ZipFile, entry_name: str, destination: Path) -> None:
    normalized = entry_name.replace("\\", "/")
    if normalized.startswith("/") or ".." in normalized.split("/"):
        raise ValueError(f"Unsafe ZIP entry path: {entry_name}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zip_file.open(entry_name) as source, destination.open("wb") as target:
        while True:
            chunk = source.read(1024 * 1024)
            if not chunk:
                break
            target.write(chunk)


def read_csv_row(path: Path, study_uid: str) -> dict[str, str] | None:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row.get("study_uid") == study_uid:
                return dict(row)
    return None


def positive_labels(row: dict[str, str] | None) -> list[str]:
    if not row:
        return []
    positives: list[str] = []
    for key, value in row.items():
        if key == "study_uid":
            continue
        if str(value).strip() in {"1", "1.0", "true", "True", "TRUE"}:
            positives.append(key)
    return positives


def report_text(row: dict[str, str] | None) -> str:
    if not row:
        return ""
    return row.get("report") or "\n\n".join(
        part for part in [row.get("clinical_information"), row.get("technique"), row.get("findings"), row.get("impression")] if part
    )


def entry_basename(entry: str) -> str:
    return Path(entry.replace("\\", "/")).name


def image_entries(zip_file: ZipFile, study_uid: str) -> list[str]:
    prefix = f"{study_uid}/img/"
    return sorted(
        entry.filename
        for entry in zip_file.infolist()
        if not entry.is_dir() and entry.filename.startswith(prefix) and nifti_suffix_ok(Path(entry.filename))
    )


def segmentation_entries(zip_file: ZipFile, study_uid: str) -> list[str]:
    prefix = f"{study_uid}/seg/"
    return sorted(
        entry.filename
        for entry in zip_file.infolist()
        if not entry.is_dir()
        and entry.filename.startswith(prefix)
        and nifti_suffix_ok(Path(entry.filename))
        and "_nvseg-ctmr-" in entry.filename
    )


def segmentation_base(entry: str) -> tuple[str, str] | None:
    base = strip_nifti_suffix(entry_basename(entry))
    for suffix in ("_nvseg-ctmr-brain", "_nvseg-ctmr-wb"):
        if base.endswith(suffix):
            return base[: -len(suffix)], suffix.rsplit("-", 1)[-1]
    return None


def choose_pair(images: list[str], segmentations: list[str], *, prefer: str, image_entry: str | None, segmentation_entry: str | None) -> tuple[str, str, str]:
    seg_by_base: dict[str, dict[str, str]] = {}
    for entry in segmentations:
        parsed = segmentation_base(entry)
        if not parsed:
            continue
        base, kind = parsed
        seg_by_base.setdefault(base, {})[kind] = entry

    if image_entry:
        chosen_image = image_entry
    else:
        image_bases = [(entry, strip_nifti_suffix(entry_basename(entry))) for entry in images]
        candidates = [
            entry
            for entry, base in image_bases
            if (base == prefer or base.endswith(f"_{prefer}")) and base in seg_by_base
        ]
        brain_candidates = [
            entry
            for entry, base in image_bases
            if (base == prefer or base.endswith(f"_{prefer}")) and "brain" in seg_by_base.get(base, {})
        ]
        if brain_candidates:
            candidates = brain_candidates
        if not candidates:
            candidates = [
                entry
                for entry, base in image_bases
                if prefer in base and base in seg_by_base
            ]
            brain_candidates = [
                entry
                for entry, base in image_bases
                if prefer in base and "brain" in seg_by_base.get(base, {})
            ]
            if brain_candidates:
                candidates = brain_candidates
        if not candidates:
            candidates = [entry for entry, base in image_bases if "brain" in seg_by_base.get(base, {})]
        if not candidates:
            candidates = [entry for entry, base in image_bases if base in seg_by_base]
        if not candidates:
            raise ValueError("No image entry has a matching NV-Segment-CTMR segmentation entry")
        chosen_image = candidates[0]

    image_base = strip_nifti_suffix(entry_basename(chosen_image))
    if segmentation_entry:
        chosen_seg = segmentation_entry
        chosen_kind = segmentation_base(chosen_seg)[1] if segmentation_base(chosen_seg) else "unknown"
    else:
        matching = seg_by_base.get(image_base, {})
        if not matching:
            raise ValueError(f"No NV-Segment-CTMR segmentation found for image base {image_base}")
        chosen_kind = "brain" if "brain" in matching else "wb"
        chosen_seg = matching[chosen_kind]
    return chosen_image, chosen_seg, chosen_kind


def prepare_mrrate_case(args: argparse.Namespace) -> dict[str, Any]:
    image_zip_path = Path(args.image_zip).expanduser().resolve()
    segmentation_zip_path = Path(args.segmentation_zip).expanduser().resolve()
    reports_csv_path = Path(args.reports_csv).expanduser().resolve()
    labels_csv_path = Path(args.labels_csv).expanduser().resolve() if args.labels_csv else None
    output_dir = Path(args.output_dir).expanduser().resolve()
    study_uid = args.study_uid

    for label, path in (
        ("image zip", image_zip_path),
        ("segmentation zip", segmentation_zip_path),
        ("reports csv", reports_csv_path),
    ):
        if not path.exists():
            return {"ok": False, "error": f"{label} does not exist", "path": str(path)}
    if labels_csv_path and not labels_csv_path.exists():
        return {"ok": False, "error": "labels csv does not exist", "path": str(labels_csv_path)}

    report_row = read_csv_row(reports_csv_path, study_uid)
    labels_row = read_csv_row(labels_csv_path, study_uid) if labels_csv_path else None
    output_case_dir = output_dir / study_uid
    image_out_dir = output_case_dir / "image"
    segmentation_out_dir = output_case_dir / "segmentation"

    with ZipFile(image_zip_path) as image_zip, ZipFile(segmentation_zip_path) as segmentation_zip:
        images = image_entries(image_zip, study_uid)
        segmentations = segmentation_entries(segmentation_zip, study_uid)
        if not images:
            return {"ok": False, "error": "No image entries found for study_uid", "study_uid": study_uid}
        if not segmentations:
            return {"ok": False, "error": "No NV-Segment-CTMR entries found for study_uid", "study_uid": study_uid}
        chosen_image, chosen_segmentation, segmentation_kind = choose_pair(
            images,
            segmentations,
            prefer=args.prefer,
            image_entry=args.image_entry,
            segmentation_entry=args.segmentation_entry,
        )
        image_path = image_out_dir / entry_basename(chosen_image)
        segmentation_path = segmentation_out_dir / entry_basename(chosen_segmentation)
        safe_write_zip_entry(image_zip, chosen_image, image_path)
        safe_write_zip_entry(segmentation_zip, chosen_segmentation, segmentation_path)

    report_path = output_case_dir / "report.txt"
    report_json_path = output_case_dir / "report.json"
    labels_json_path = output_case_dir / "labels.json"
    manifest_path = output_case_dir / "manifest.json"
    text = report_text(report_row)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(text, encoding="utf-8")

    report_payload = {
        "study_uid": study_uid,
        "found": report_row is not None,
        "clinical_information": report_row.get("clinical_information") if report_row else None,
        "technique": report_row.get("technique") if report_row else None,
        "findings": report_row.get("findings") if report_row else None,
        "impression": report_row.get("impression") if report_row else None,
        "report_text_path": str(report_path),
    }
    labels_payload = {
        "study_uid": study_uid,
        "found": labels_row is not None,
        "positive_labels": positive_labels(labels_row),
        "label_columns": [key for key in labels_row.keys() if key != "study_uid"] if labels_row else [],
    }
    manifest = {
        "ok": True,
        "schema_version": SCHEMA_VERSION,
        "created_at": utc_now(),
        "study_uid": study_uid,
        "image_zip": str(image_zip_path),
        "segmentation_zip": str(segmentation_zip_path),
        "reports_csv": str(reports_csv_path),
        "labels_csv": str(labels_csv_path) if labels_csv_path else None,
        "available_image_entries": images,
        "available_segmentation_entries": segmentations,
        "selected_image_entry": chosen_image,
        "selected_segmentation_entry": chosen_segmentation,
        "segmentation_kind": segmentation_kind,
        "image": str(image_path),
        "segmentation": str(segmentation_path),
        "report": str(report_path),
        "report_json": str(report_json_path),
        "labels_json": str(labels_json_path),
        "positive_report_labels": labels_payload["positive_labels"],
        "next_commands": [
            (
                "python skills/radiological-report-to-roi/scripts/radiological_report_to_roi.py "
                f"extract-roi --image \"{image_path}\" --segmentation \"{segmentation_path}\" "
                "--labels <label-ids> "
                f"--output-dir \"{output_case_dir / 'roi'}\" --report \"{report_path}\" --json"
            )
        ],
    }

    write_json(report_json_path, report_payload)
    write_json(labels_json_path, labels_payload)
    write_json(manifest_path, manifest)
    return {**manifest, "manifest": str(manifest_path)}


def bounding_box(mask: Any) -> dict[str, list[int]] | None:
    import numpy as np

    coords = np.argwhere(mask)
    if coords.size == 0:
        return None
    mins = coords.min(axis=0).astype(int).tolist()
    maxs = coords.max(axis=0).astype(int).tolist()
    return {"min": mins, "max": maxs}


def affine_close(left: Any, right: Any) -> bool:
    import numpy as np

    return bool(np.allclose(left, right, rtol=1e-4, atol=1e-4))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def ensure_dependencies() -> list[str]:
    missing = [name for name in ("numpy", "nibabel") if not dependency_available(name)]
    return missing


def output_paths(output_dir: Path, name: str | None) -> dict[str, Path]:
    stem = name.strip() if name else ""
    if stem:
        return {
            "mask": output_dir / f"{stem}_mask.nii.gz",
            "summary": output_dir / f"{stem}_summary.json",
            "provenance": output_dir / f"{stem}_provenance.json",
        }
    return {
        "mask": output_dir / OUTPUT_MASK_NAME,
        "summary": output_dir / SUMMARY_NAME,
        "provenance": output_dir / PROVENANCE_NAME,
    }


def extract_roi(args: argparse.Namespace) -> dict[str, Any]:
    missing = ensure_dependencies()
    if missing:
        return {
            "ok": False,
            "error": "Missing optional dependencies required for ROI extraction.",
            "missing_dependencies": missing,
            "suggested_fix": "Activate an environment with numpy and nibabel installed.",
        }

    import nibabel as nib
    import numpy as np

    image_path = Path(args.image).expanduser().resolve()
    segmentation_path = Path(args.segmentation).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    report_path = Path(args.report).expanduser().resolve() if args.report else None
    warnings: list[str] = []

    for label, path in (("image", image_path), ("segmentation", segmentation_path)):
        if not path.exists():
            return {"ok": False, "error": f"{label} file does not exist", "path": str(path)}
        if not nifti_suffix_ok(path):
            warnings.append(f"{label} file does not have .nii or .nii.gz suffix: {path.name}")

    if report_path and not report_path.exists():
        return {"ok": False, "error": "report file does not exist", "path": str(report_path)}

    output_dir.mkdir(parents=True, exist_ok=True)
    paths = output_paths(output_dir, args.name)

    image = nib.load(str(image_path))
    segmentation = nib.load(str(segmentation_path))
    image_shape = tuple(int(value) for value in image.shape[:3])
    segmentation_shape = tuple(int(value) for value in segmentation.shape[:3])
    if image_shape != segmentation_shape:
        return {
            "ok": False,
            "error": "Image and segmentation shapes do not match.",
            "image_shape": list(image_shape),
            "segmentation_shape": list(segmentation_shape),
        }

    if not affine_close(image.affine, segmentation.affine):
        warnings.append("Image and segmentation affines differ; verify registration before using this ROI.")

    segmentation_data = segmentation.get_fdata(dtype=np.float32)
    labels = list(args.labels)
    label_data = np.rint(segmentation_data).astype(np.int64)
    mask = np.isin(label_data, labels)
    voxel_count = int(mask.sum())
    bbox = bounding_box(mask)

    roi_image = nib.Nifti1Image(mask.astype(np.uint8), image.affine, image.header)
    roi_image.set_data_dtype(np.uint8)
    nib.save(roi_image, str(paths["mask"]))

    zooms = image.header.get_zooms()[:3]
    voxel_volume_mm3 = float(math.prod(float(value) for value in zooms)) if len(zooms) == 3 else None
    volume_mm3 = float(voxel_count * voxel_volume_mm3) if voxel_volume_mm3 is not None else None

    summary = {
        "schema_version": SCHEMA_VERSION,
        "ok": True,
        "created_at": utc_now(),
        "anatomy": args.anatomy,
        "labels": labels,
        "voxel_count": voxel_count,
        "voxel_volume_mm3": voxel_volume_mm3,
        "volume_mm3": volume_mm3,
        "bounding_box": bbox,
        "image_shape": list(image_shape),
        "segmentation_shape": list(segmentation_shape),
        "image_zooms": [float(value) for value in zooms],
        "warnings": warnings,
    }
    provenance = {
        "schema_version": SCHEMA_VERSION,
        "created_at": summary["created_at"],
        "tool": "radiological-report-to-roi",
        "command": sys.argv,
        "image": str(image_path),
        "segmentation": str(segmentation_path),
        "report": str(report_path) if report_path else None,
        "output_mask": str(paths["mask"]),
        "roi_summary": str(paths["summary"]),
        "provenance": str(paths["provenance"]),
        "labels": labels,
        "anatomy": args.anatomy,
        "affine_close": not any("affines differ" in warning for warning in warnings),
        "research_only": True,
        "clinical_use": "Not for diagnosis, treatment, triage, or clinical decision-making.",
    }

    write_json(paths["summary"], summary)
    write_json(paths["provenance"], provenance)

    return {
        "ok": True,
        "roi_mask": str(paths["mask"]),
        "roi_summary": str(paths["summary"]),
        "provenance": str(paths["provenance"]),
        "summary": summary,
        "warnings": warnings,
    }


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_text_file(path: Path | None) -> str:
    if not path or not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def file_record(path: Path | None) -> dict[str, Any]:
    if not path:
        return {"path": None, "exists": False}
    exists = path.exists()
    record: dict[str, Any] = {"path": str(path), "exists": exists}
    if exists:
        stat = path.stat()
        record["size_bytes"] = stat.st_size
        record["modified_at"] = dt.datetime.fromtimestamp(stat.st_mtime, dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return record


def html_table(rows: list[tuple[str, Any]]) -> str:
    body = []
    for key, value in rows:
        if isinstance(value, (dict, list)):
            rendered = f"<pre>{html.escape(json.dumps(value, indent=2, sort_keys=True))}</pre>"
        else:
            rendered = html.escape("" if value is None else str(value))
        body.append(f"<tr><th>{html.escape(key)}</th><td>{rendered}</td></tr>")
    return "<table>" + "\n".join(body) + "</table>"


def quote_command_arg(value: Any) -> str:
    text = str(value)
    if not text:
        return '""'
    if re.search(r"\s|[\"']", text):
        return '"' + text.replace('"', '\\"') + '"'
    return text


def command_line(parts: list[Any]) -> str:
    return " ".join(quote_command_arg(part) for part in parts if part is not None and str(part) != "")


def commands_block(commands: list[dict[str, str]]) -> str:
    rows = []
    for command in commands:
        rows.append(
            "<tr>"
            f"<td>{html.escape(command['step'])}</td>"
            f"<td>{html.escape(command['purpose'])}</td>"
            f"<td><pre>{html.escape(command['command'])}</pre></td>"
            "</tr>"
        )
    return (
        "<table><thead><tr><th>Step</th><th>Purpose</th><th>Python Command</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )


def format_bytes(value: Any) -> str:
    if not isinstance(value, int):
        return ""
    units = ["bytes", "KB", "MB", "GB", "TB"]
    number = float(value)
    unit = units[0]
    for unit in units:
        if number < 1024 or unit == units[-1]:
            break
        number /= 1024
    return f"{number:.1f} {unit}" if unit != "bytes" else f"{int(number)} bytes"


def file_table(records: list[dict[str, Any]]) -> str:
    rows = []
    for record in records:
        path = record.get("path")
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(record.get('label', 'file')))}</td>"
            f"<td><code>{html.escape('' if path is None else str(path))}</code></td>"
            f"<td>{'yes' if record.get('exists') else 'no'}</td>"
            f"<td>{html.escape(format_bytes(record.get('size_bytes')))}</td>"
            f"<td>{html.escape(str(record.get('modified_at', '')))}</td>"
            "</tr>"
        )
    return (
        "<table><thead><tr><th>File</th><th>Path</th><th>Exists</th><th>Size</th><th>Modified</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )


def label_name(label_id: int) -> str:
    return MRI_BRAIN_LABELS.get(label_id, f"Label {label_id}")


def normalize_anatomy_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower().replace("-", " ")).strip()


def evidence_for_pattern(text: str, pattern: str) -> str:
    normalized_pattern = normalize_anatomy_text(pattern)
    for line in text.splitlines():
        cleaned = line.strip(" -\t")
        if normalized_pattern in normalize_anatomy_text(cleaned):
            return cleaned
    return text.strip()


def segmentation_label_summary(segmentation_path: Path) -> dict[str, Any]:
    missing = ensure_dependencies()
    if missing:
        return {"ok": False, "missing_dependencies": missing}

    import nibabel as nib
    import numpy as np

    segmentation = nib.load(str(segmentation_path))
    data = np.rint(segmentation.get_fdata(dtype=np.float32)).astype(np.int32)
    labels, counts = np.unique(data, return_counts=True)
    records = []
    for label, count in zip(labels.tolist(), counts.tolist()):
        label_int = int(label)
        if label_int == 0:
            continue
        records.append(
            {
                "label": label_int,
                "name": label_name(label_int),
                "voxel_count": int(count),
            }
        )
    return {
        "ok": True,
        "shape": [int(value) for value in segmentation.shape[:3]],
        "label_count": len(records),
        "labels": records,
    }


def segmentation_label_lookup(segmentation_labels: dict[str, Any]) -> dict[int, dict[str, Any]]:
    lookup: dict[int, dict[str, Any]] = {}
    if not segmentation_labels.get("ok"):
        return lookup
    for record in segmentation_labels.get("labels", []):
        lookup[int(record["label"])] = record
    return lookup


def label_details(label_ids: list[int], segmentation_labels: dict[str, Any]) -> list[dict[str, Any]]:
    lookup = segmentation_label_lookup(segmentation_labels)
    details = []
    for label_id in label_ids:
        present = label_id in lookup
        details.append(
            {
                "label": label_id,
                "name": label_name(label_id),
                "present": present,
                "voxel_count": int(lookup[label_id]["voxel_count"]) if present else None,
            }
        )
    return details


def anatomy_status(details: list[dict[str, Any]], *, context_only: bool) -> str:
    if context_only:
        return "context only"
    if details and all(detail["present"] for detail in details):
        return "segmentation mask exists"
    if details and any(detail["present"] for detail in details):
        return "partial segmentation mask exists"
    if details:
        return "label map entry exists, but label is absent from selected segmentation"
    return "no segmentation mask exists"


def extract_impression_anatomy(impression: str, segmentation_labels: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_anatomy_text(impression)
    records: list[dict[str, Any]] = []
    seen_regions: set[str] = set()

    for term in IMPRESSION_ANATOMY_TERMS:
        matched_pattern = None
        for pattern in term["patterns"]:
            if normalize_anatomy_text(pattern) in normalized:
                matched_pattern = pattern
                break
        if not matched_pattern:
            continue
        labels = [int(value) for value in term.get("labels", [])]
        details = label_details(labels, segmentation_labels)
        status = anatomy_status(details, context_only=bool(term.get("context_only")))
        record = {
            "region": term["region"],
            "matched_text": matched_pattern,
            "evidence": evidence_for_pattern(impression, matched_pattern),
            "status": status,
            "labels": details,
            "note": term.get("note", ""),
            "context_only": bool(term.get("context_only")),
        }
        records.append(record)
        seen_regions.add(str(term["region"]))

    for label_id, label_value in MRI_BRAIN_LABELS.items():
        phrase = normalize_anatomy_text(label_value.replace("---", "-").replace("--", "-"))
        phrase = re.sub(r"\b(left|right)\b", lambda match: match.group(1), phrase)
        phrase = phrase.replace("proper", "").strip()
        if len(phrase) < 6 or phrase not in normalized:
            continue
        region = label_name(label_id)
        if region in seen_regions:
            continue
        details = label_details([label_id], segmentation_labels)
        records.append(
            {
                "region": region,
                "matched_text": phrase,
                "evidence": evidence_for_pattern(impression, phrase),
                "status": anatomy_status(details, context_only=False),
                "labels": details,
                "note": "Matched directly from the MRI brain segmentation label map.",
                "context_only": False,
            }
        )
        seen_regions.add(region)

    missing = [
        record
        for record in records
        if not record.get("context_only") and record["status"] != "segmentation mask exists"
    ]
    return {
        "ok": True,
        "source": "impression",
        "matched_count": len(records),
        "missing_mask_count": len(missing),
        "regions": records,
        "mentioned_without_segmentation_mask": missing,
    }


def normalize_slice(values: Any) -> Any:
    import numpy as np

    finite = values[np.isfinite(values)]
    if finite.size == 0:
        return np.zeros(values.shape, dtype=np.uint8)
    low, high = np.percentile(finite, [1, 99])
    if high <= low:
        low = float(finite.min())
        high = float(finite.max())
    if high <= low:
        return np.zeros(values.shape, dtype=np.uint8)
    normalized = (values - low) / (high - low)
    normalized = np.clip(normalized, 0, 1)
    return (normalized * 255).astype(np.uint8)


def save_overlay_png(image_slice: Any, mask_slice: Any, path: Path) -> None:
    import numpy as np
    from PIL import Image

    grayscale = normalize_slice(image_slice)
    rgb = np.stack([grayscale, grayscale, grayscale], axis=-1).astype(np.float32)
    mask = mask_slice.astype(bool)
    rgb[mask] = rgb[mask] * 0.45 + np.array([255, 32, 32], dtype=np.float32) * 0.55
    image = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))
    image.save(path)


def roi_center(summary: dict[str, Any], fallback_shape: tuple[int, int, int]) -> list[int]:
    bbox = summary.get("bounding_box")
    if isinstance(bbox, dict) and bbox.get("min") and bbox.get("max"):
        return [int((int(lo) + int(hi)) // 2) for lo, hi in zip(bbox["min"], bbox["max"])]
    return [int(value // 2) for value in fallback_shape]


def generate_preview_images(image_path: Path, roi_mask_path: Path, roi_summary: dict[str, Any], assets_dir: Path) -> dict[str, Any]:
    missing = ensure_dependencies()
    if missing:
        return {"ok": False, "missing_dependencies": missing, "images": []}
    if not dependency_available("PIL"):
        return {"ok": False, "missing_dependencies": ["PIL"], "images": []}

    import nibabel as nib
    import numpy as np

    assets_dir.mkdir(parents=True, exist_ok=True)
    image = nib.load(str(image_path))
    mask = nib.load(str(roi_mask_path))
    image_shape = tuple(int(value) for value in image.shape[:3])
    mask_shape = tuple(int(value) for value in mask.shape[:3])
    if image_shape != mask_shape:
        return {"ok": False, "error": "Image and ROI mask shapes do not match.", "images": []}

    image_data = image.get_fdata(dtype=np.float32)
    mask_data = mask.get_fdata(dtype=np.float32) > 0
    center = roi_center(roi_summary, image_shape)
    specs = [
        ("sagittal", 0, center[0], image_data[center[0], :, :], mask_data[center[0], :, :]),
        ("coronal", 1, center[1], image_data[:, center[1], :], mask_data[:, center[1], :]),
        ("axial", 2, center[2], image_data[:, :, center[2]], mask_data[:, :, center[2]]),
    ]
    previews = []
    for name, axis, index, image_slice, mask_slice in specs:
        output = assets_dir / f"{name}_roi_overlay.png"
        save_overlay_png(np.rot90(image_slice), np.rot90(mask_slice), output)
        previews.append(
            {
                "name": name,
                "axis": axis,
                "index": int(index),
                "path": str(output),
                "file": f"{assets_dir.name}/{output.name}",
            }
        )
    return {"ok": True, "center_voxel": center, "images": previews}


def labels_table(labels_summary: dict[str, Any]) -> str:
    if not labels_summary.get("ok"):
        return f"<p class=\"muted\">Label summary unavailable: {html.escape(json.dumps(labels_summary, sort_keys=True))}</p>"
    rows = []
    for record in labels_summary.get("labels", []):
        rows.append(
            "<tr>"
            f"<td>{int(record['label'])}</td>"
            f"<td>{html.escape(record['name'])}</td>"
            f"<td>{int(record['voxel_count']):,}</td>"
            "</tr>"
        )
    return (
        "<table><thead><tr><th>Label</th><th>Name</th><th>Voxels</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )


def format_label_details(details: list[dict[str, Any]]) -> str:
    if not details:
        return "<span class=\"muted\">None</span>"
    parts = []
    for detail in details:
        voxel_text = ""
        if detail.get("voxel_count") is not None:
            voxel_text = f" ({int(detail['voxel_count']):,} voxels)"
        present = "present" if detail.get("present") else "absent"
        parts.append(f"{int(detail['label'])}: {html.escape(detail['name'])} - {present}{voxel_text}")
    return "<br>".join(parts)


def impression_anatomy_table(impression_anatomy: dict[str, Any]) -> str:
    records = impression_anatomy.get("regions", [])
    if not records:
        return "<p class=\"muted\">No supported anatomy terms were detected in the impression.</p>"
    rows = []
    for record in records:
        rows.append(
            "<tr>"
            f"<td>{html.escape(record['region'])}</td>"
            f"<td>{html.escape(record['matched_text'])}</td>"
            f"<td>{html.escape(record['evidence'])}</td>"
            f"<td>{html.escape(record['status'])}</td>"
            f"<td>{format_label_details(record.get('labels', []))}</td>"
            f"<td>{html.escape(record.get('note', ''))}</td>"
            "</tr>"
        )
    return (
        "<table><thead><tr><th>Region</th><th>Matched Text</th><th>Evidence From Impression</th>"
        "<th>Segmentation Status</th><th>Mask Details</th><th>Notes</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )


def missing_impression_anatomy_table(impression_anatomy: dict[str, Any]) -> str:
    records = impression_anatomy.get("mentioned_without_segmentation_mask", [])
    if not records:
        return "<p class=\"muted\">Every detected impression anatomy term has a corresponding segmentation mask in the selected segmentation.</p>"
    rows = []
    for record in records:
        rows.append(
            "<tr>"
            f"<td>{html.escape(record['region'])}</td>"
            f"<td>{html.escape(record['evidence'])}</td>"
            f"<td>{html.escape(record['status'])}</td>"
            f"<td>{html.escape(record.get('note', ''))}</td>"
            "</tr>"
        )
    return (
        "<table><thead><tr><th>Region</th><th>Evidence From Impression</th><th>Status</th><th>Notes</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )


def build_reproducibility_commands(
    *,
    manifest_path: Path,
    manifest: dict[str, Any],
    roi_summary_path: Path,
    roi_summary: dict[str, Any],
    provenance_path: Path,
    provenance: dict[str, Any],
    output_html: Path,
    title: str,
) -> list[dict[str, str]]:
    study_uid = str(manifest.get("study_uid") or "")
    labels = ",".join(str(label) for label in roi_summary.get("labels", []))
    prepare_output_dir = manifest_path.parent.parent
    extract_output_dir = Path(str(provenance.get("roi_summary", roi_summary_path))).expanduser().resolve().parent
    commands = [
        {
            "step": "1",
            "purpose": "Check that the local Python environment has the optional medical-image dependencies.",
            "command": command_line(["python", SCRIPT_PATH, "check", "--json"]),
        },
        {
            "step": "2",
            "purpose": "Prepare the MR-RATE case from local image, segmentation, report, and label files.",
            "command": command_line(
                [
                    "python",
                    SCRIPT_PATH,
                    "prepare-mrrate-case",
                    "--study-uid",
                    study_uid,
                    "--image-zip",
                    manifest.get("image_zip"),
                    "--segmentation-zip",
                    manifest.get("segmentation_zip"),
                    "--reports-csv",
                    manifest.get("reports_csv"),
                    "--labels-csv",
                    manifest.get("labels_csv"),
                    "--output-dir",
                    prepare_output_dir,
                    "--image-entry",
                    manifest.get("selected_image_entry"),
                    "--segmentation-entry",
                    manifest.get("selected_segmentation_entry"),
                    "--json",
                ]
            ),
        },
        {
            "step": "3",
            "purpose": "Extract the selected segmentation labels into a binary ROI mask and JSON outputs.",
            "command": command_line(
                [
                    "python",
                    SCRIPT_PATH,
                    "extract-roi",
                    "--image",
                    manifest.get("image"),
                    "--segmentation",
                    manifest.get("segmentation"),
                    "--labels",
                    labels,
                    "--output-dir",
                    extract_output_dir,
                    "--anatomy",
                    roi_summary.get("anatomy") or provenance.get("anatomy"),
                    "--report",
                    manifest.get("report"),
                    "--json",
                ]
            ),
        },
        {
            "step": "4",
            "purpose": "Generate this HTML audit report from the prepared case and ROI outputs.",
            "command": command_line(
                [
                    "python",
                    SCRIPT_PATH,
                    "report-html",
                    "--manifest",
                    manifest_path,
                    "--roi-summary",
                    roi_summary_path,
                    "--provenance",
                    provenance_path,
                    "--output-html",
                    output_html,
                    "--title",
                    title,
                    "--json",
                ]
            ),
        },
    ]
    return commands


def image_gallery(previews: dict[str, Any]) -> str:
    if not previews.get("ok"):
        return f"<p class=\"muted\">Preview images unavailable: {html.escape(json.dumps(previews, sort_keys=True))}</p>"
    cards = []
    for preview in previews.get("images", []):
        cards.append(
            "<figure>"
            f"<img src=\"{html.escape(preview['file'])}\" alt=\"{html.escape(preview['name'])} ROI overlay\">"
            f"<figcaption>{html.escape(preview['name'].title())} slice, axis {preview['axis']}, index {preview['index']}</figcaption>"
            "</figure>"
        )
    return f"<div class=\"gallery\">{''.join(cards)}</div>"


def render_html_report(
    *,
    title: str,
    manifest: dict[str, Any],
    report_payload: dict[str, Any],
    labels_payload: dict[str, Any],
    roi_summary: dict[str, Any],
    provenance: dict[str, Any],
    report_text_value: str,
    file_records: list[dict[str, Any]],
    segmentation_labels: dict[str, Any],
    impression_anatomy: dict[str, Any],
    reproducibility_commands: list[dict[str, str]],
    previews: dict[str, Any],
    output_html: Path,
) -> None:
    study_uid = manifest.get("study_uid", "unknown study")
    positive_labels_value = labels_payload.get("positive_labels") or []
    report_sections = [
        ("Clinical Information", report_payload.get("clinical_information")),
        ("Technique", report_payload.get("technique")),
        ("Findings", report_payload.get("findings")),
        ("Impression", report_payload.get("impression")),
    ]
    report_section_rows = [(name, value) for name, value in report_sections if value]
    selected_labels = roi_summary.get("labels", [])
    selected_label_rows = []
    for label in selected_labels:
        label_id = int(label)
        selected_label_rows.append(
            "<tr>"
            f"<td>{label_id}</td>"
            f"<td>{html.escape(label_name(label_id))}</td>"
            "</tr>"
        )
    selected_labels_table = (
        "<table><thead><tr><th>Label</th><th>Name</th></tr></thead>"
        f"<tbody>{''.join(selected_label_rows)}</tbody></table>"
    )
    created_at = utc_now()
    css = """
    :root {
      color-scheme: light;
      --ink: #17202a;
      --muted: #5f6b7a;
      --line: #d9e0e8;
      --panel: #f7f9fc;
      --accent: #0b6f6a;
      --accent-soft: #e6f4f2;
      --warn: #7a4d00;
      --warn-bg: #fff6df;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      color: var(--ink);
      background: #ffffff;
      line-height: 1.5;
    }
    header {
      padding: 36px 42px 28px;
      border-bottom: 1px solid var(--line);
      background: linear-gradient(180deg, #f7fbfb, #ffffff);
    }
    main { max-width: 1180px; margin: 0 auto; padding: 28px 32px 48px; }
    h1 { margin: 0 0 8px; font-size: 30px; letter-spacing: 0; }
    h2 { margin: 34px 0 12px; font-size: 22px; border-bottom: 1px solid var(--line); padding-bottom: 8px; }
    h3 { margin: 22px 0 8px; font-size: 17px; }
    p { max-width: 900px; }
    code {
      font-family: Consolas, "Liberation Mono", monospace;
      font-size: 0.92em;
      overflow-wrap: anywhere;
    }
    pre {
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      padding: 12px;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 6px;
      max-height: 360px;
      overflow: auto;
    }
    .subtitle { color: var(--muted); margin: 0; }
    .badge {
      display: inline-block;
      margin: 14px 8px 0 0;
      padding: 4px 9px;
      border-radius: 999px;
      background: var(--accent-soft);
      color: var(--accent);
      font-weight: 700;
      font-size: 13px;
    }
    .notice {
      padding: 12px 14px;
      background: var(--warn-bg);
      border: 1px solid #f0d58a;
      border-radius: 6px;
      color: var(--warn);
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin: 10px 0 18px;
      font-size: 14px;
    }
    th, td {
      border: 1px solid var(--line);
      padding: 8px 10px;
      text-align: left;
      vertical-align: top;
    }
    th { background: var(--panel); width: 220px; }
    thead th { width: auto; }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 14px;
    }
    .panel {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #ffffff;
      padding: 14px;
    }
    .metric {
      font-size: 24px;
      font-weight: 700;
      color: var(--accent);
    }
    .metric-label { color: var(--muted); font-size: 13px; }
    .gallery {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 18px;
    }
    figure {
      margin: 0;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px;
      background: #fff;
    }
    figure img {
      width: 100%;
      height: auto;
      display: block;
      image-rendering: auto;
      background: #111;
    }
    figcaption { margin-top: 8px; color: var(--muted); font-size: 13px; }
    details {
      margin: 12px 0;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px 12px;
      background: #fff;
    }
    summary { cursor: pointer; font-weight: 700; }
    .muted { color: var(--muted); }
    """
    html_doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>{css}</style>
</head>
<body>
  <header>
    <h1>{html.escape(title)}</h1>
    <p class="subtitle">Study <code>{html.escape(str(study_uid))}</code> | Generated {html.escape(created_at)}</p>
    <span class="badge">Research workflow</span>
    <span class="badge">MR-RATE</span>
    <span class="badge">NV-Segment-CTMR</span>
    <span class="badge">ROI extraction</span>
  </header>
  <main>
    <p class="notice">Research use only. This report is not for diagnosis, treatment, triage, or clinical decision-making. Keep medical images and reports local unless the governing data terms allow transfer.</p>

    <h2>Executive Summary</h2>
    <div class="grid">
      <div class="panel"><div class="metric">{html.escape(str(roi_summary.get('anatomy') or 'ROI'))}</div><div class="metric-label">Target anatomy</div></div>
      <div class="panel"><div class="metric">{int(roi_summary.get('voxel_count') or 0):,}</div><div class="metric-label">ROI voxels</div></div>
      <div class="panel"><div class="metric">{float(roi_summary.get('volume_mm3') or 0):,.1f}</div><div class="metric-label">ROI volume mm3</div></div>
      <div class="panel"><div class="metric">{html.escape(str(segmentation_labels.get('label_count', 'n/a')))}</div><div class="metric-label">Nonzero labels in selected segmentation</div></div>
    </div>

    <h2>Raw Data</h2>
    <p>These are the source downloads, prepared files, and final output artifacts used to generate this report.</p>
    {file_table(file_records)}

    <h2>Reproducibility Commands</h2>
    <p>Run these Python commands from the SkillForge repository root to reproduce the processing pipeline and regenerate this report.</p>
    {commands_block(reproducibility_commands)}

    <h3>Available Image Entries</h3>
    <pre>{html.escape(json.dumps(manifest.get('available_image_entries', []), indent=2))}</pre>

    <h3>Available Segmentation Entries</h3>
    <pre>{html.escape(json.dumps(manifest.get('available_segmentation_entries', []), indent=2))}</pre>

    <h3>Radiology Report</h3>
    {html_table(report_section_rows) if report_section_rows else ''}
    <details open>
      <summary>Raw report text</summary>
      <pre>{html.escape(report_text_value)}</pre>
    </details>

    <h3>Anatomy Mentioned In The Impression</h3>
    <p>This section audits anatomy terms found in the impression and checks whether the selected NV-Segment-CTMR brain segmentation has a corresponding mask.</p>
    {impression_anatomy_table(impression_anatomy)}

    <h3>Mentioned In Radiology Report But No Segmentation Mask Exists</h3>
    <p class="muted">These regions were mentioned in the impression, but the selected MRI brain segmentation does not provide a direct mask for them.</p>
    {missing_impression_anatomy_table(impression_anatomy)}

    <h3>MR-RATE Pathology Labels</h3>
    <p>Positive labels from the supplied MR-RATE labels CSV: <strong>{html.escape(', '.join(positive_labels_value) if positive_labels_value else 'none recorded in the provided CSV row')}</strong>.</p>
    <details>
      <summary>Raw labels JSON</summary>
      <pre>{html.escape(json.dumps(labels_payload, indent=2, sort_keys=True))}</pre>
    </details>

    <h2>Intermediate Results</h2>
    <h3>Selected Pairing</h3>
    {html_table([
        ('Selected image entry', manifest.get('selected_image_entry')),
        ('Selected segmentation entry', manifest.get('selected_segmentation_entry')),
        ('Segmentation kind', manifest.get('segmentation_kind')),
        ('ROI labels selected', selected_labels),
        ('Bounding box', roi_summary.get('bounding_box')),
        ('Image shape', roi_summary.get('image_shape')),
        ('Image voxel spacing', roi_summary.get('image_zooms')),
        ('Warnings', roi_summary.get('warnings')),
    ])}

    <h3>Selected ROI Labels</h3>
    {selected_labels_table}

    <h3>Labels Present In Selected Segmentation</h3>
    <p class="muted">Label names are resolved from the built-in NV-Segment-CTMR MRI brain label map when available.</p>
    {labels_table(segmentation_labels)}

    <h2>Image Previews</h2>
    <p>The red overlay shows the extracted ROI mask on representative sagittal, coronal, and axial slices through the ROI center.</p>
    {image_gallery(previews)}

    <h2>Final Output</h2>
    {html_table([
        ('ROI mask', provenance.get('output_mask')),
        ('ROI summary', provenance.get('roi_summary')),
        ('Provenance', provenance.get('provenance')),
        ('Voxel count', roi_summary.get('voxel_count')),
        ('Voxel volume mm3', roi_summary.get('voxel_volume_mm3')),
        ('Volume mm3', roi_summary.get('volume_mm3')),
        ('Affine close', provenance.get('affine_close')),
        ('Clinical use', provenance.get('clinical_use')),
    ])}

    <h2>3D Data Viewing</h2>
    <p>This report embeds static slices so it works without a local web server or custom viewer code. For interactive 3D review, use an existing NIfTI-capable web viewer rather than writing a new one.</p>
    <ul>
      <li><strong><a href="https://niivue.com/docs/loading">NiiVue</a></strong>: good future fit for an embedded WebGL NIfTI viewer with image and mask overlays.</li>
      <li><strong><a href="https://rii-mango.github.io/Papaya/">Papaya</a></strong>: lightweight browser-based NIfTI viewer that can be embedded in static pages.</li>
      <li><strong>VolView or OHIF</strong>: heavier options when the workflow needs richer medical-imaging review features.</li>
    </ul>
    <p class="muted">Practical note: browser security rules often make local NIfTI loading easier when the report folder is served with <code>python -m http.server</code>. Do not upload restricted medical data to external hosted viewers unless the data terms explicitly allow it.</p>

    <details>
      <summary>Raw manifest JSON</summary>
      <pre>{html.escape(json.dumps(manifest, indent=2, sort_keys=True))}</pre>
    </details>
    <details>
      <summary>Raw ROI summary JSON</summary>
      <pre>{html.escape(json.dumps(roi_summary, indent=2, sort_keys=True))}</pre>
    </details>
    <details>
      <summary>Raw provenance JSON</summary>
      <pre>{html.escape(json.dumps(provenance, indent=2, sort_keys=True))}</pre>
    </details>
  </main>
</body>
</html>
"""
    output_html.parent.mkdir(parents=True, exist_ok=True)
    output_html.write_text(html_doc, encoding="utf-8")


def report_html(args: argparse.Namespace) -> dict[str, Any]:
    manifest_path = Path(args.manifest).expanduser().resolve()
    roi_summary_path = Path(args.roi_summary).expanduser().resolve()
    provenance_path = Path(args.provenance).expanduser().resolve()
    output_html = Path(args.output_html).expanduser().resolve()

    for label, path in (
        ("manifest", manifest_path),
        ("roi summary", roi_summary_path),
        ("provenance", provenance_path),
    ):
        if not path.exists():
            return {"ok": False, "error": f"{label} file does not exist", "path": str(path)}

    manifest = read_json(manifest_path)
    roi_summary = read_json(roi_summary_path)
    provenance = read_json(provenance_path)
    image_path = Path(manifest.get("image", "")).expanduser().resolve()
    segmentation_path = Path(manifest.get("segmentation", "")).expanduser().resolve()
    report_path = Path(manifest.get("report", "")).expanduser().resolve()
    report_json_path = Path(manifest.get("report_json", "")).expanduser().resolve()
    labels_json_path = Path(manifest.get("labels_json", "")).expanduser().resolve()
    roi_mask_path = Path(args.roi_mask or provenance.get("output_mask", "")).expanduser().resolve()

    for label, path in (
        ("image", image_path),
        ("segmentation", segmentation_path),
        ("ROI mask", roi_mask_path),
    ):
        if not path.exists():
            return {"ok": False, "error": f"{label} file does not exist", "path": str(path)}

    report_payload = read_json(report_json_path) if report_json_path.exists() else {}
    labels_payload = read_json(labels_json_path) if labels_json_path.exists() else {}
    assets_dir = output_html.with_name(f"{output_html.stem}_assets")
    segmentation_labels = segmentation_label_summary(segmentation_path)
    impression_anatomy = extract_impression_anatomy(str(report_payload.get("impression") or ""), segmentation_labels)
    previews = generate_preview_images(image_path, roi_mask_path, roi_summary, assets_dir)
    title = args.title or f"Radiological Report to ROI: {manifest.get('study_uid', 'study')}"
    reproducibility_commands = build_reproducibility_commands(
        manifest_path=manifest_path,
        manifest=manifest,
        roi_summary_path=roi_summary_path,
        roi_summary=roi_summary,
        provenance_path=provenance_path,
        provenance=provenance,
        output_html=output_html,
        title=title,
    )

    raw_paths = [
        ("Image ZIP", manifest.get("image_zip")),
        ("Segmentation ZIP", manifest.get("segmentation_zip")),
        ("Reports CSV", manifest.get("reports_csv")),
        ("Labels CSV", manifest.get("labels_csv")),
        ("Prepared image", manifest.get("image")),
        ("Prepared segmentation", manifest.get("segmentation")),
        ("Prepared report text", manifest.get("report")),
        ("Prepared report JSON", manifest.get("report_json")),
        ("Prepared labels JSON", manifest.get("labels_json")),
        ("ROI mask", provenance.get("output_mask")),
        ("ROI summary", provenance.get("roi_summary")),
        ("Provenance", provenance.get("provenance")),
    ]
    file_records = []
    for label, value in raw_paths:
        path = Path(value).expanduser().resolve() if value else None
        record = file_record(path)
        record["label"] = label
        file_records.append(record)

    render_html_report(
        title=title,
        manifest=manifest,
        report_payload=report_payload,
        labels_payload=labels_payload,
        roi_summary=roi_summary,
        provenance=provenance,
        report_text_value=read_text_file(report_path),
        file_records=file_records,
        segmentation_labels=segmentation_labels,
        impression_anatomy=impression_anatomy,
        reproducibility_commands=reproducibility_commands,
        previews=previews,
        output_html=output_html,
    )
    return {
        "ok": True,
        "html_report": str(output_html),
        "assets_dir": str(assets_dir),
        "preview_images": previews.get("images", []),
        "segmentation_label_count": segmentation_labels.get("label_count"),
        "impression_anatomy": impression_anatomy,
        "reproducibility_commands": reproducibility_commands,
        "viewer_note": "Static slice previews were embedded. For interactive 3D, use an existing NIfTI viewer such as NiiVue or Papaya served from a local HTTP server.",
    }


def schema_payload() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "commands": {
            "check": {
                "description": "Report Python and optional dependency availability.",
                "side_effects": "Read-only.",
                "example": "python radiological_report_to_roi.py check --json",
            },
            "schema": {
                "description": "Return the agent-facing CLI command contract.",
                "side_effects": "Read-only.",
                "example": "python radiological_report_to_roi.py schema --json",
            },
            "prepare-mrrate-case": {
                "description": "Prepare a local MR-RATE study case from image and NV-Segment-CTMR ZIP files plus report/label CSVs.",
                "side_effects": "Reads local ZIP and CSV files; writes selected image, segmentation, report text, labels JSON, and manifest.",
                "required_args": ["--study-uid", "--image-zip", "--segmentation-zip", "--reports-csv", "--output-dir"],
                "optional_args": ["--labels-csv", "--prefer", "--image-entry", "--segmentation-entry", "--json"],
                "example": (
                    "python radiological_report_to_roi.py prepare-mrrate-case --study-uid 22B7CXEZ6T "
                    "--image-zip 22B7CXEZ6T.zip --segmentation-zip 22B7CXEZ6T_nvseg-ctmr.zip "
                    "--reports-csv batch00_reports.csv --labels-csv mrrate_labels.csv --output-dir test-data/radiological-report-to-roi --json"
                ),
            },
            "extract-roi": {
                "description": "Extract selected label IDs from a local NIfTI segmentation as a binary ROI mask.",
                "side_effects": "Reads local image/segmentation files and writes ROI mask plus JSON summaries.",
                "required_args": ["--image", "--segmentation", "--labels", "--output-dir"],
                "optional_args": ["--name", "--anatomy", "--report", "--json"],
                "example": (
                    "python radiological_report_to_roi.py extract-roi --image image.nii.gz "
                    "--segmentation segmentation.nii.gz --labels 10,11 --output-dir output --json"
                ),
            },
            "report-html": {
                "description": "Create a human-readable HTML report from a prepared MR-RATE case and ROI extraction outputs.",
                "side_effects": "Reads local manifest, image, segmentation, ROI mask, and JSON summaries; writes an HTML report and PNG preview slices.",
                "required_args": ["--manifest", "--roi-summary", "--provenance", "--output-html"],
                "optional_args": ["--roi-mask", "--title", "--json"],
                "example": (
                    "python radiological_report_to_roi.py report-html --manifest manifest.json "
                    "--roi-summary roi_summary.json --provenance provenance.json "
                    "--output-html 22B7CXEZ6T_roi_report.html --json"
                ),
            },
        },
        "outputs": {
            "roi_mask": "Binary uint8 NIfTI mask.",
            "roi_summary": "JSON summary with labels, voxel count, volume, bounding box, and warnings.",
            "provenance": "JSON provenance with inputs, outputs, command, and research-only note.",
            "html_report": "Human-readable HTML report with raw data, intermediate results, final outputs, and slice previews.",
        },
    }


def print_payload(payload: dict[str, Any], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    if payload.get("ok") is False:
        print(f"Error: {payload.get('error', 'unknown error')}")
        if payload.get("suggested_fix"):
            print(f"Suggested fix: {payload['suggested_fix']}")
        return
    if "dependencies" in payload:
        print("Radiological Report to ROI")
        for name, available in payload["dependencies"].items():
            print(f"- {name}: {'available' if available else 'missing'}")
        return
    if payload.get("roi_mask"):
        print(f"ROI mask: {payload['roi_mask']}")
        print(f"ROI summary: {payload['roi_summary']}")
        print(f"Provenance: {payload['provenance']}")
        return
    if payload.get("html_report"):
        print(f"HTML report: {payload['html_report']}")
        print(f"Assets: {payload['assets_dir']}")
        return
    print(json.dumps(payload, indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Agent CLI for Radiological Report to ROI workflows.")
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check", help="Check optional ROI extraction dependencies")
    check.add_argument("--json", action="store_true")

    schema = sub.add_parser("schema", help="Print the agent-facing CLI schema")
    schema.add_argument("--json", action="store_true")

    extract = sub.add_parser("extract-roi", help="Extract a binary ROI mask from a segmentation")
    extract.add_argument("--image", required=True)
    extract.add_argument("--segmentation", required=True)
    extract.add_argument("--labels", required=True, type=parse_labels)
    extract.add_argument("--output-dir", required=True)
    extract.add_argument("--name")
    extract.add_argument("--anatomy")
    extract.add_argument("--report")
    extract.add_argument("--json", action="store_true")

    prepare = sub.add_parser("prepare-mrrate-case", help="Prepare local MR-RATE image/segmentation/report files")
    prepare.add_argument("--study-uid", required=True)
    prepare.add_argument("--image-zip", required=True)
    prepare.add_argument("--segmentation-zip", required=True)
    prepare.add_argument("--reports-csv", required=True)
    prepare.add_argument("--labels-csv")
    prepare.add_argument("--output-dir", required=True)
    prepare.add_argument("--prefer", default="t1w-raw-axi")
    prepare.add_argument("--image-entry")
    prepare.add_argument("--segmentation-entry")
    prepare.add_argument("--json", action="store_true")

    report = sub.add_parser("report-html", help="Create an HTML report from prepared case and ROI outputs")
    report.add_argument("--manifest", required=True)
    report.add_argument("--roi-summary", required=True)
    report.add_argument("--provenance", required=True)
    report.add_argument("--output-html", required=True)
    report.add_argument("--roi-mask")
    report.add_argument("--title")
    report.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "check":
        payload = {"ok": True, "schema_version": SCHEMA_VERSION, **dependency_report()}
    elif args.command == "schema":
        payload = schema_payload()
    elif args.command == "prepare-mrrate-case":
        payload = prepare_mrrate_case(args)
    elif args.command == "extract-roi":
        payload = extract_roi(args)
    elif args.command == "report-html":
        payload = report_html(args)
    else:
        parser.error(f"Unsupported command: {args.command}")
        return 2
    print_payload(payload, as_json=getattr(args, "json", False))
    return 0 if payload.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
