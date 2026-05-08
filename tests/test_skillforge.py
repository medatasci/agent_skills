from __future__ import annotations

import contextlib
import io
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tomllib
import unittest
import uuid
from zipfile import ZipFile

from skillforge.catalog import (
    CLINICAL_TEMPLATE_FILES,
    CLINICAL_TEMPLATE_PACKAGE_DIR,
    CLINICAL_TEMPLATE_SOURCE_DIR,
    PLUGIN_SKILLS_DIR,
    REPO_ROOT,
    build_catalog,
    catalog_file_bytes,
    clinical_disease_chapter_paths,
    evaluate_skill,
    file_sha256,
    load_skill_metadata,
    metadata_from_validation,
    read_search_index,
    render_site_index,
    search_audit_skill,
    search_catalog,
)
from skillforge.clinical_statistical_expert import evidence_query_pack
from skillforge.cli import main
from skillforge.contribute import ContributionDraft
from skillforge.feedback import FeedbackDraft
from skillforge.filesystem import copy_tree, remove_tree
from skillforge.install import (
    MARKETPLACE_ID,
    MARKETPLACE_REF,
    MARKETPLACE_SOURCE,
    PLUGIN_ID,
    default_global_codex_skills_dir,
    install_skill,
    install_skillforge_marketplace,
    list_installed,
    remove_installed_skill,
)
from skillforge.peer import (
    cache_peer_catalogs,
    cache_listing,
    classify_peer_error,
    corpus_search,
    install_peer_skill,
    peer_diagnostics,
    peer_catalog_cache_path,
    peer_search,
    peer_search_jobs,
    search_cache_path,
    selected_peers,
)
from skillforge.update import update_check, update_skillforge, whats_new
from skillforge.validate import iter_skill_files, validate_skill


class SkillForgeTests(unittest.TestCase):
    def test_validate_pilot_skill(self) -> None:
        result = validate_skill(REPO_ROOT / "skills" / "project-retrospective")
        self.assertTrue(result.ok)
        self.assertEqual(result.metadata["name"], "project-retrospective")

    def test_validate_warns_when_skillforge_skill_lacks_readable_agent_contract(self) -> None:
        skill_id = f"agent-contract-{uuid.uuid4().hex}"
        skill_dir = REPO_ROOT / "skills" / skill_id
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(
            "\n".join(
                [
                    "---",
                    f"name: {skill_id}",
                    "description: Test readable agent-contract warnings.",
                    "---",
                    "",
                    "Overview text before any heading.",
                    "",
                    "## SkillForge Discovery Metadata",
                ]
            ),
            encoding="utf-8",
        )
        try:
            result = validate_skill(skill_dir)
            self.assertTrue(result.ok)
            self.assertTrue(any("human-readable H1" in warning for warning in result.warnings), result.warnings)
            self.assertTrue(any("What This Skill Does" in warning for warning in result.warnings), result.warnings)
            self.assertTrue(any("Safe Default Behavior" in warning for warning in result.warnings), result.warnings)
        finally:
            remove_tree(skill_dir)

    def test_validate_warns_when_guarded_skill_lacks_runtime_plan(self) -> None:
        skill_id = f"runtime-gate-{uuid.uuid4().hex}"
        skill_dir = REPO_ROOT / "skills" / skill_id
        (skill_dir / "scripts").mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(
            "\n".join(
                [
                    "---",
                    f"name: {skill_id}",
                    "description: Test guarded execution runtime planning warnings.",
                    "---",
                    "",
                    "# Runtime Gate",
                    "",
                    "Run only after `--confirm-execution` is present.",
                ]
            ),
            encoding="utf-8",
        )
        (skill_dir / "scripts" / "runner.py").write_text(
            "CONFIRM_FLAG = '--confirm-execution'\n",
            encoding="utf-8",
        )
        try:
            result = validate_skill(skill_dir)
            self.assertTrue(result.ok)
            self.assertTrue(
                any("missing runtime/deployment plan documentation" in warning for warning in result.warnings)
            )
        finally:
            remove_tree(skill_dir)

    def test_validate_accepts_guarded_skill_with_runtime_plan(self) -> None:
        skill_id = f"runtime-plan-{uuid.uuid4().hex}"
        skill_dir = REPO_ROOT / "skills" / skill_id
        (skill_dir / "scripts").mkdir(parents=True, exist_ok=True)
        (skill_dir / "references").mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(
            "\n".join(
                [
                    "---",
                    f"name: {skill_id}",
                    "description: Test guarded execution runtime planning acceptance.",
                    "---",
                    "",
                    "# Runtime Plan",
                    "",
                    "Run only after `--confirm-execution` is present.",
                ]
            ),
            encoding="utf-8",
        )
        (skill_dir / "scripts" / "runner.py").write_text(
            "CONFIRM_FLAG = '--confirm-execution'\n",
            encoding="utf-8",
        )
        (skill_dir / "references" / "requirements-and-development-plan.md").write_text(
            "\n".join(
                [
                    "# Runtime And Deployment Plan",
                    "",
                    "Install location: source checkout under a runtime path.",
                    "OS/runtime target: Windows, macOS, Linux, or WSL2 as documented.",
                    "Dependency setup: install dependencies with pip, conda, or requirements.txt.",
                    "Model/data download policy: document model weights, dataset, and download approval.",
                    "License review: record license and model terms.",
                    "Environment checks: run the check command and inspect CUDA or Docker readiness.",
                    "Smoke-test data: use approved test data only.",
                    "Rollback/cleanup notes: clean up temporary files and document rollback.",
                ]
            ),
            encoding="utf-8",
        )
        try:
            result = validate_skill(skill_dir)
            self.assertTrue(result.ok)
            self.assertFalse(
                any("runtime/deployment plan" in warning for warning in result.warnings),
                result.warnings,
            )
        finally:
            remove_tree(skill_dir)

    def test_search_finds_youtube_skill(self) -> None:
        results = search_catalog("youtube transcripts research")
        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "get-youtube-media")
        self.assertIn("description", results[0])
        self.assertIn("short_description", results[0])
        self.assertIn("expanded_description", results[0])
        self.assertIn("summary", results[0])
        self.assertTrue(results[0]["description"])
        self.assertTrue(results[0]["summary"])

    def test_search_uses_discovery_metadata(self) -> None:
        results = search_catalog("after action review")
        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "project-retrospective")

        index = read_search_index()
        self.assertIn("aliases", index["fields_indexed"])
        self.assertIn("homepage_text", index["fields_indexed"])
        self.assertIn("search_text", index["skills"][0])
        self.assertIn("homepage_path", index["skills"][0])

    def test_build_catalog_syncs_plugin_skill_bundle(self) -> None:
        catalog = build_catalog()
        skill_ids = {skill["id"] for skill in catalog["skills"]}
        self.assertIn("huggingface-datasets", skill_ids)
        for skill_id in skill_ids:
            self.assertTrue((PLUGIN_SKILLS_DIR / skill_id / "SKILL.md").exists())
            self.assertTrue((PLUGIN_SKILLS_DIR / skill_id / "README.md").exists())
        skill_list = (PLUGIN_SKILLS_DIR / "skill_list.md").read_text(encoding="utf-8")
        self.assertIn("huggingface-datasets", skill_list)
        self.assertIn("project-retrospective", skill_list)

    def test_clinical_templates_match_canonical_sources(self) -> None:
        build_catalog()
        plugin_template_dir = PLUGIN_SKILLS_DIR / "clinical-statistical-expert" / "references" / "templates"
        for name in CLINICAL_TEMPLATE_FILES:
            expected = (CLINICAL_TEMPLATE_SOURCE_DIR / name).read_text(encoding="utf-8-sig").splitlines()
            packaged = (CLINICAL_TEMPLATE_PACKAGE_DIR / name).read_text(encoding="utf-8-sig").splitlines()
            plugin = (plugin_template_dir / name).read_text(encoding="utf-8-sig").splitlines()
            self.assertEqual(expected, packaged, name)
            self.assertEqual(expected, plugin, name)

    def test_evidence_query_pack_generates_radiology_mri_prompts(self) -> None:
        payload = evidence_query_pack("gliosis", modality="MRI")
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["target_concept"], "gliosis")
        self.assertEqual(payload["expert_role"], "neuroradiologist")
        self.assertIn("sequence-specific MRI signal characteristics", payload["advanced_prompt"])
        self.assertIn("lesion morphology", payload["advanced_prompt"])
        self.assertIn("anatomic distribution", payload["advanced_prompt"])
        self.assertIn("volume-loss patterns", payload["advanced_prompt"])
        self.assertTrue(any("T1 T2 FLAIR DWI ADC SWI" in query for query in payload["search_variants"]))
        self.assertTrue(any("Use confirm" in note for note in payload["capture_notes"]))

    def test_evidence_query_pack_cli_json(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            status = main(["evidence-query-pack", "gliosis", "--modality", "MRI", "--json"])
        self.assertEqual(status, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["target_concept"], "gliosis")
        self.assertEqual(payload["section"], "Expert-Framed Source Discovery Questions")
        self.assertIn("sequence-specific MRI signal characteristics", payload["advanced_prompt"])

    def test_skill_text_checksums_are_line_ending_stable(self) -> None:
        root = REPO_ROOT / "test-output" / f"checksum-{uuid.uuid4().hex}"
        try:
            root.mkdir(parents=True, exist_ok=True)
            lf = root / "skill.md"
            crlf = root / "skill-crlf.md"
            binary_lf = root / "payload.bin"
            binary_crlf = root / "payload-crlf.bin"
            lf.write_bytes(b"# Skill\n\nBody\n")
            crlf.write_bytes(b"# Skill\r\n\r\nBody\r\n")
            binary_lf.write_bytes(b"payload\n\0")
            binary_crlf.write_bytes(b"payload\r\n\0")

            self.assertEqual(file_sha256(lf), file_sha256(crlf))
            self.assertEqual(len(catalog_file_bytes(lf)), len(catalog_file_bytes(crlf)))
            self.assertNotEqual(file_sha256(binary_lf), file_sha256(binary_crlf))
            self.assertNotEqual(len(catalog_file_bytes(binary_lf)), len(catalog_file_bytes(binary_crlf)))
        finally:
            remove_tree(root)

    def test_search_audit_reports_ready_skill(self) -> None:
        payload = search_audit_skill("huggingface-datasets")
        self.assertEqual(payload["score"], 100)
        self.assertEqual(payload["recommendations"], [])
        self.assertTrue(any(check["category"] == "skill_homepage" and check["ok"] for check in payload["checks"]))
        self.assertIn("catalog/search-index.json", payload["files"])

    def test_evaluate_reports_ready_skill(self) -> None:
        payload = evaluate_skill("huggingface-datasets")
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["skill_id"], "huggingface-datasets")
        self.assertEqual(payload["score"], 100)
        self.assertGreaterEqual(len(payload["sample_searches"]), 3)
        self.assertTrue(any(check["category"] == "skill_homepage" and check["ok"] for check in payload["checks"]))
        self.assertTrue(any(check["category"] == "skill_md_agent_contract" and check["ok"] for check in payload["checks"]))
        self.assertTrue(any(check["category"] == "skill_template_conformance" and check["ok"] for check in payload["checks"]))
        self.assertTrue(any(check["category"] == "readme_template_conformance" and check["ok"] for check in payload["checks"]))
        self.assertTrue(payload["template_conformance"]["ok"])

    def test_evaluate_reports_repo_derived_advisories(self) -> None:
        payload = evaluate_skill("nv-segment-ctmr")
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["repo_derived"]["detected"])
        categories = {check["category"]: check for check in payload["advisory_checks"]}
        for category in [
            "repo_derived_readiness_card",
            "repo_derived_source_context_map",
            "repo_derived_candidate_table",
            "repo_derived_source_version",
            "repo_derived_runtime_plan",
            "repo_derived_smoke_test",
            "repo_derived_authoritative_sources",
        ]:
            self.assertIn(category, categories)
            self.assertTrue(categories[category]["ok"], category)
            self.assertEqual(categories[category]["severity"], "warning")

    def test_evaluate_reports_clinical_disease_advisories(self) -> None:
        build_catalog()
        payload = evaluate_skill("clinical-statistical-expert")
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["clinical_disease"]["detected"])
        categories = {check["category"]: check for check in payload["advisory_checks"]}
        for category in [
            "clinical_disease_chapters_present",
            "clinical_disease_differential_diagnosis",
            "clinical_disease_covariates_confounders",
            "clinical_disease_review_criteria",
        ]:
            self.assertIn(category, categories)
            self.assertTrue(categories[category]["ok"], category)
            self.assertEqual(categories[category]["severity"], "warning")

    def test_clinical_disease_chapter_paths_excludes_support_artifacts(self) -> None:
        skill_dir = REPO_ROOT / "skills" / "clinical-statistical-expert"
        paths = clinical_disease_chapter_paths(skill_dir)
        path_names = {path.name for path in paths}
        self.assertIn("gliosis.md", path_names)
        self.assertNotIn("gliosis.review.md", path_names)
        self.assertNotIn("gliosis.source-review.md", path_names)
        self.assertNotIn("gliosis.research-plan.backtest.md", path_names)
        self.assertNotIn("gliosis.build-retrospective.md", path_names)
        self.assertNotIn("chronic-infarct-encephalomalacia.research-plan.md", path_names)

    def test_evaluate_prefers_catalog_skill_id_over_same_name_directory(self) -> None:
        build_catalog()
        payload = evaluate_skill("skillforge")
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["skill_id"], "skillforge")

    def test_radiological_report_to_roi_cli_contract(self) -> None:
        script = REPO_ROOT / "skills" / "radiological-report-to-roi" / "scripts" / "radiological_report_to_roi.py"

        check = subprocess.run(
            [sys.executable, str(script), "check", "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(check.returncode, 0, check.stderr)
        check_payload = json.loads(check.stdout)
        self.assertTrue(check_payload["ok"])
        self.assertIn("numpy", check_payload["dependencies"])
        self.assertIn("nibabel", check_payload["dependencies"])

        schema = subprocess.run(
            [sys.executable, str(script), "schema", "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(schema.returncode, 0, schema.stderr)
        schema_payload = json.loads(schema.stdout)
        self.assertIn("extract-roi", schema_payload["commands"])
        self.assertIn("--image", schema_payload["commands"]["extract-roi"]["required_args"])
        self.assertIn("report-html", schema_payload["commands"])
        self.assertIn("--manifest", schema_payload["commands"]["report-html"]["required_args"])

        extract = subprocess.run(
            [
                sys.executable,
                str(script),
                "extract-roi",
                "--image",
                "missing-image.nii.gz",
                "--segmentation",
                "missing-segmentation.nii.gz",
                "--labels",
                "1,2",
                "--output-dir",
                "test-output/radiological-report-to-roi-missing-inputs",
                "--json",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(extract.returncode, 0)
        extract_payload = json.loads(extract.stdout)
        self.assertFalse(extract_payload["ok"])
        self.assertIn("error", extract_payload)

    def test_nv_segment_ctmr_cli_read_only_contract(self) -> None:
        script = REPO_ROOT / "skills" / "nv-segment-ctmr" / "scripts" / "nv_segment_ctmr.py"

        schema = subprocess.run(
            [sys.executable, str(script), "schema", "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(schema.returncode, 0, schema.stderr)
        schema_payload = json.loads(schema.stdout)
        self.assertTrue(schema_payload["ok"])
        self.assertIn("MRI_BODY", schema_payload["modes"])
        self.assertIn("plan", [command["name"] for command in schema_payload["commands"]])
        self.assertIn("verify-output", [command["name"] for command in schema_payload["commands"]])
        self.assertIn("setup-plan", [command["name"] for command in schema_payload["commands"]])
        self.assertIn("brain-plan", [command["name"] for command in schema_payload["commands"]])
        self.assertIn("batch-plan", [command["name"] for command in schema_payload["commands"]])
        self.assertIn("run", [command["name"] for command in schema_payload["commands"]])
        self.assertIn("brain-run", [command["name"] for command in schema_payload["commands"]])
        self.assertIn("batch-run", [command["name"] for command in schema_payload["commands"]])
        self.assertIn("segment-test-mri", [command["name"] for command in schema_payload["commands"]])

        check = subprocess.run(
            [sys.executable, str(script), "check", "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(check.returncode, 0, check.stderr)
        check_payload = json.loads(check.stdout)
        self.assertTrue(check_payload["ok"])
        self.assertTrue(check_payload["read_only"])
        self.assertIn("dependencies", check_payload)

        setup_plan = subprocess.run(
            [
                sys.executable,
                str(script),
                "setup-plan",
                "--target",
                "wsl2-linux",
                "--runtime-dir",
                "~/.skillforge/runtime/nv-segment-ctmr",
                "--json",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(setup_plan.returncode, 0, setup_plan.stderr)
        setup_payload = json.loads(setup_plan.stdout)
        self.assertTrue(setup_payload["ok"])
        self.assertTrue(setup_payload["read_only"])
        self.assertEqual(setup_payload["command"], "setup-plan")
        self.assertEqual(setup_payload["target"], "wsl2-linux")
        self.assertEqual(setup_payload["source_clone_url"], "https://github.com/NVIDIA-Medtech/NV-Segment-CTMR.git")
        self.assertTrue(any(step["step"] == "download model weights" for step in setup_payload["commands"]))
        self.assertIn("side_effects_if_executed", setup_payload)

        labels = subprocess.run(
            [sys.executable, str(script), "labels", "--query", "brain stem", "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(labels.returncode, 0, labels.stderr)
        labels_payload = json.loads(labels.stdout)
        self.assertTrue(labels_payload["ok"])
        self.assertEqual(labels_payload["results"][0]["label_id"], 220)
        self.assertEqual(labels_payload["results"][0]["name"], "Brain-Stem")

        plan = subprocess.run(
            [
                sys.executable,
                str(script),
                "plan",
                "--image",
                "scan.nii.gz",
                "--mode",
                "MRI_BODY",
                "--output-dir",
                "results",
                "--json",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(plan.returncode, 0, plan.stderr)
        plan_payload = json.loads(plan.stdout)
        self.assertTrue(plan_payload["ok"])
        self.assertTrue(plan_payload["read_only"])
        self.assertFalse(plan_payload["ready_to_execute"])
        self.assertIn("blocking_reasons", plan_payload)
        self.assertEqual(plan_payload["route"], "segment-everything")
        self.assertIn("monai.bundle", plan_payload["planned_command"])

        brain_plan = subprocess.run(
            [
                sys.executable,
                str(script),
                "brain-plan",
                "--image",
                "brain_t1.nii.gz",
                "--output-dir",
                "results",
                "--json",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(brain_plan.returncode, 0, brain_plan.stderr)
        brain_plan_payload = json.loads(brain_plan.stdout)
        self.assertTrue(brain_plan_payload["ok"])
        self.assertTrue(brain_plan_payload["read_only"])
        self.assertEqual(brain_plan_payload["command"], "brain-plan")
        self.assertEqual(brain_plan_payload["mode"], "MRI_BRAIN")

        ready_root = REPO_ROOT / "test-output" / f"nv-segment-ctmr-ready-{uuid.uuid4().hex}"
        try:
            ready_source = ready_root / "source"
            ready_output = ready_root / "output"
            ready_source.joinpath("configs").mkdir(parents=True, exist_ok=True)
            ready_source.joinpath("models").mkdir(parents=True, exist_ok=True)
            ready_output.mkdir(parents=True, exist_ok=True)
            ready_source.joinpath("configs", "inference.json").write_text("{}", encoding="utf-8")
            ready_source.joinpath("models", "model.pt").write_bytes(b"model")
            ready_image = ready_root / "scan.nii.gz"
            ready_image.write_bytes(b"nifti")
            ready_plan = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "plan",
                    "--image",
                    str(ready_image),
                    "--mode",
                    "MRI_BODY",
                    "--output-dir",
                    str(ready_output),
                    "--source-dir",
                    str(ready_source),
                    "--json",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(ready_plan.returncode, 0, ready_plan.stderr)
            ready_payload = json.loads(ready_plan.stdout)
            self.assertTrue(ready_payload["ready_to_execute"])
            self.assertEqual(ready_payload["blocking_reasons"], [])
        finally:
            remove_tree(ready_root)

        batch_root = REPO_ROOT / "test-output" / f"nv-segment-ctmr-batch-{uuid.uuid4().hex}"
        try:
            input_dir = batch_root / "input"
            output_dir = batch_root / "output"
            input_dir.mkdir(parents=True, exist_ok=True)
            output_dir.mkdir(parents=True, exist_ok=True)
            (input_dir / "case1.nii.gz").write_bytes(b"placeholder")
            batch_plan = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "batch-plan",
                    "--input-dir",
                    str(input_dir),
                    "--mode",
                    "MRI_BODY",
                    "--output-dir",
                    str(output_dir),
                    "--json",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(batch_plan.returncode, 0, batch_plan.stderr)
            batch_plan_payload = json.loads(batch_plan.stdout)
            self.assertTrue(batch_plan_payload["ok"])
            self.assertTrue(batch_plan_payload["read_only"])
            self.assertEqual(batch_plan_payload["discovered_count"], 1)
            self.assertEqual(batch_plan_payload["queued_count"], 1)
        finally:
            remove_tree(batch_root)

        run = subprocess.run(
            [
                sys.executable,
                str(script),
                "run",
                "--image",
                "scan.nii.gz",
                "--mode",
                "MRI_BODY",
                "--output-dir",
                "results",
                "--json",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(run.returncode, 0)
        run_payload = json.loads(run.stdout)
        self.assertFalse(run_payload["ok"])
        self.assertEqual(run_payload["error"]["kind"], "execution_not_confirmed")
        self.assertIn("planned_run", run_payload)

        brain_run = subprocess.run(
            [
                sys.executable,
                str(script),
                "brain-run",
                "--image",
                "brain_t1.nii.gz",
                "--output-dir",
                "results",
                "--json",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(brain_run.returncode, 0)
        brain_run_payload = json.loads(brain_run.stdout)
        self.assertFalse(brain_run_payload["ok"])
        self.assertEqual(brain_run_payload["error"]["kind"], "execution_not_confirmed")

        workflow_root = REPO_ROOT / "test-output" / f"nv-segment-ctmr-agent-workflow-{uuid.uuid4().hex}"
        try:
            workflow_output = workflow_root / "output"
            workflow_output.mkdir(parents=True, exist_ok=True)
            workflow_image = workflow_root / "brain.nii.gz"
            workflow_image.write_bytes(b"placeholder")
            missing_workflow = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "segment-test-mri",
                    "--image",
                    str(workflow_image),
                    "--output-dir",
                    str(workflow_output),
                    "--json",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(missing_workflow.returncode, 0)
            missing_payload = json.loads(missing_workflow.stdout)
            self.assertFalse(missing_payload["ok"])
            self.assertTrue(missing_payload["read_only"])
            self.assertEqual(missing_payload["status"], "missing_output")
            self.assertTrue(missing_payload["segmentation_path"].endswith("brain_trans.nii.gz"))
            self.assertEqual(missing_payload["error"]["kind"], "missing_segmentation")
        finally:
            remove_tree(workflow_root)

        batch_run = subprocess.run(
            [
                sys.executable,
                str(script),
                "batch-run",
                "--input-dir",
                "test-data/radiological-report-to-roi/22B7CXEZ6T/image",
                "--mode",
                "MRI_BODY",
                "--output-dir",
                "results",
                "--json",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(batch_run.returncode, 0)
        batch_run_payload = json.loads(batch_run.stdout)
        self.assertFalse(batch_run_payload["ok"])
        self.assertEqual(batch_run_payload["error"]["kind"], "execution_not_confirmed")

        if importlib.util.find_spec("nibabel") is None or importlib.util.find_spec("numpy") is None:
            self.skipTest("nibabel and numpy are required for synthetic NIfTI output verification")
        import nibabel as nib
        import numpy as np

        root = REPO_ROOT / "test-output" / f"nv-segment-ctmr-verify-{uuid.uuid4().hex}"
        workflow_root = REPO_ROOT / "test-output" / f"nv-segment-ctmr-agent-workflow-{uuid.uuid4().hex}"
        try:
            root.mkdir(parents=True, exist_ok=True)
            segmentation = root / "segmentation.nii.gz"
            data = np.zeros((2, 3, 4), dtype=np.int16)
            data[0, 0, 0] = 3
            data[1, 1, 1] = 220
            nib.save(nib.Nifti1Image(data, np.eye(4)), str(segmentation))

            verify = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "verify-output",
                    "--segmentation",
                    str(segmentation),
                    "--json",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(verify.returncode, 0, verify.stderr)
            verify_payload = json.loads(verify.stdout)
            self.assertTrue(verify_payload["ok"])
            self.assertTrue(verify_payload["read_only"])
            self.assertTrue(verify_payload["nifti_readable"])
            self.assertEqual(verify_payload["shape"], [2, 3, 4])
            labels_seen = {item["label"] for item in verify_payload["label_summary"]["values"]}
            self.assertEqual(labels_seen, {0, 3, 220})

            workflow_output = workflow_root / "output"
            workflow_output.mkdir(parents=True, exist_ok=True)
            workflow_image = workflow_root / "brain.nii.gz"
            workflow_image.write_bytes(b"placeholder")
            workflow_segmentation = workflow_output / "brain_trans.nii.gz"
            nib.save(nib.Nifti1Image(data, np.eye(4)), str(workflow_segmentation))

            existing_workflow = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "segment-test-mri",
                    "--image",
                    str(workflow_image),
                    "--output-dir",
                    str(workflow_output),
                    "--json",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(existing_workflow.returncode, 0, existing_workflow.stderr)
            existing_payload = json.loads(existing_workflow.stdout)
            self.assertTrue(existing_payload["ok"])
            self.assertTrue(existing_payload["read_only"])
            self.assertEqual(existing_payload["status"], "existing_output_verified")
            self.assertEqual(existing_payload["segmentation_path"], str(workflow_segmentation).replace("\\", "/"))
        finally:
            remove_tree(root)
            remove_tree(workflow_root)

    def test_nv_generate_ctmr_cli_read_only_contract(self) -> None:
        script = REPO_ROOT / "skills" / "nv-generate-ctmr" / "scripts" / "nv_generate_ctmr.py"

        schema = subprocess.run(
            [sys.executable, str(script), "schema", "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(schema.returncode, 0, schema.stderr)
        schema_payload = json.loads(schema.stdout)
        self.assertTrue(schema_payload["ok"])
        self.assertIn("rflow-mr-brain", schema_payload["generate_versions"])
        self.assertIn("run", [command["name"] for command in schema_payload["commands"]])

        check = subprocess.run(
            [sys.executable, str(script), "check", "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(check.returncode, 0, check.stderr)
        check_payload = json.loads(check.stdout)
        self.assertTrue(check_payload["ok"])
        self.assertTrue(check_payload["read_only"])
        self.assertIn("dependencies", check_payload)

        models = subprocess.run(
            [sys.executable, str(script), "models", "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(models.returncode, 0, models.stderr)
        models_payload = json.loads(models.stdout)
        self.assertEqual(models_payload["models"]["rflow-ct"]["default_workflow"], "ct-paired")
        self.assertEqual(models_payload["models"]["rflow-mr"]["license"], "NVIDIA Non-Commercial License")

        modalities = subprocess.run(
            [sys.executable, str(script), "modalities", "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(modalities.returncode, 0, modalities.stderr)
        modalities_payload = json.loads(modalities.stdout)
        modality_ids = {item["name"]: item["id"] for item in modalities_payload["modalities"]}
        self.assertEqual(modality_ids["mri_t1"], 9)
        self.assertEqual(modality_ids["mri_swi_skull_stripped"], 32)

        setup_plan = subprocess.run(
            [
                sys.executable,
                str(script),
                "setup-plan",
                "--target",
                "wsl2-linux",
                "--generate-version",
                "rflow-ct",
                "--json",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(setup_plan.returncode, 0, setup_plan.stderr)
        setup_payload = json.loads(setup_plan.stdout)
        self.assertTrue(setup_payload["read_only"])
        self.assertTrue(any(step["step"] == "optional model download" for step in setup_payload["commands"]))

        ct_plan = subprocess.run(
            [
                sys.executable,
                str(script),
                "plan",
                "--generate-version",
                "rflow-ct",
                "--workflow",
                "ct-paired",
                "--body-region",
                "chest",
                "--anatomy",
                "lung tumor",
                "--output-size",
                "256,256,256",
                "--spacing",
                "1.5,1.5,2.0",
                "--json",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(ct_plan.returncode, 0, ct_plan.stderr)
        ct_payload = json.loads(ct_plan.stdout)
        self.assertTrue(ct_payload["read_only"])
        self.assertEqual(ct_payload["workflow"], "ct-paired")
        self.assertIn("lung tumor", ct_payload["config_preview"]["anatomy_list"])
        self.assertEqual(ct_payload["planned_commands"][0][2], "scripts.inference")
        self.assertFalse(ct_payload["ready_to_execute"])

        mr_plan = subprocess.run(
            [
                sys.executable,
                str(script),
                "plan",
                "--generate-version",
                "rflow-mr-brain",
                "--workflow",
                "image-only",
                "--contrast",
                "mri_flair",
                "--output-dir",
                "results",
                "--json",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(mr_plan.returncode, 0, mr_plan.stderr)
        mr_payload = json.loads(mr_plan.stdout)
        self.assertEqual(mr_payload["workflow"], "image-only")
        self.assertEqual(mr_payload["config_preview"]["diffusion_unet_inference"]["modality"], 11)
        self.assertEqual(mr_payload["planned_commands"][0][2], "scripts.download_model_data")

        root = REPO_ROOT / "test-output" / f"nv-generate-ctmr-config-{uuid.uuid4().hex}"
        try:
            config_path = root / "preview.json"
            source_config_dir = root / "source-configs"
            config_template = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "config-template",
                    "--generate-version",
                    "rflow-ct",
                    "--workflow",
                    "ct-paired",
                    "--output-file",
                    str(config_path),
                    "--json",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(config_template.returncode, 0, config_template.stderr)
            config_payload = json.loads(config_template.stdout)
            self.assertFalse(config_payload["read_only"])
            self.assertTrue(config_path.exists())
            written_config = json.loads(config_path.read_text(encoding="utf-8"))
            self.assertEqual(written_config["kind"], "config_infer")

            source_configs = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "config-template",
                    "--generate-version",
                    "rflow-ct",
                    "--workflow",
                    "ct-paired",
                    "--output-size",
                    "256,256,128",
                    "--spacing",
                    "1.5,1.5,2.0",
                    "--body-region",
                    "chest",
                    "--anatomy",
                    "lung tumor",
                    "--config-dir",
                    str(source_config_dir),
                    "--output-dir",
                    str(root / "output"),
                    "--json",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(source_configs.returncode, 0, source_configs.stderr)
            source_payload = json.loads(source_configs.stdout)
            self.assertFalse(source_payload["read_only"])
            written_files = source_payload["source_configs"]["written_files"]
            inference_config = Path(written_files["inference_config"])
            environment_config = Path(written_files["environment_config"])
            self.assertTrue(inference_config.exists())
            self.assertTrue(environment_config.exists())
            inference_payload = json.loads(inference_config.read_text(encoding="utf-8"))
            self.assertEqual(inference_payload["controlnet"], "$@controlnet_def")
            self.assertEqual(inference_payload["output_size"], [256, 256, 128])
            environment_payload = json.loads(environment_config.read_text(encoding="utf-8"))
            self.assertEqual(environment_payload["output_dir"], str(root / "output"))

            source_config_plan = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "plan",
                    "--generate-version",
                    "rflow-ct",
                    "--workflow",
                    "ct-paired",
                    "--config-dir",
                    str(source_config_dir),
                    "--output-dir",
                    str(root / "output"),
                    "--json",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(source_config_plan.returncode, 0, source_config_plan.stderr)
            source_plan_payload = json.loads(source_config_plan.stdout)
            self.assertIn(str(inference_config).replace("\\", "/"), source_plan_payload["planned_command_text"][0])
            self.assertIn(str(environment_config).replace("\\", "/"), source_plan_payload["planned_command_text"][0])
        finally:
            remove_tree(root)

        if importlib.util.find_spec("nibabel") is not None and importlib.util.find_spec("numpy") is not None:
            import nibabel as nib
            import numpy as np

            verify_root = REPO_ROOT / "test-output" / f"nv-generate-ctmr-verify-{uuid.uuid4().hex}"
            try:
                verify_root.mkdir(parents=True, exist_ok=True)
                image = verify_root / "generated.nii.gz"
                nib.save(nib.Nifti1Image(np.zeros((2, 3, 4), dtype=np.float32), np.eye(4)), str(image))
                verify = subprocess.run(
                    [
                        sys.executable,
                        str(script),
                        "verify-output",
                        "--image",
                        str(image),
                        "--json",
                    ],
                    cwd=REPO_ROOT,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(verify.returncode, 0, verify.stderr)
                verify_payload = json.loads(verify.stdout)
                self.assertTrue(verify_payload["nifti_readable"])
                self.assertEqual(verify_payload["shape"], [2, 3, 4])
                self.assertTrue(all(isinstance(value, float) for value in verify_payload["zooms"]))
            finally:
                remove_tree(verify_root)

        run = subprocess.run(
            [
                sys.executable,
                str(script),
                "run",
                "--generate-version",
                "rflow-ct",
                "--workflow",
                "ct-paired",
                "--json",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(run.returncode, 0)
        run_payload = json.loads(run.stdout)
        self.assertFalse(run_payload["ok"])
        self.assertEqual(run_payload["error"]["kind"], "execution_not_confirmed")

    def test_radiological_report_to_roi_impression_anatomy_audit(self) -> None:
        script = REPO_ROOT / "skills" / "radiological-report-to-roi" / "scripts" / "radiological_report_to_roi.py"
        spec = importlib.util.spec_from_file_location("radiological_report_to_roi", script)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

        segmentation_labels = {
            "ok": True,
            "labels": [
                {"label": 220, "name": "Brain-Stem", "voxel_count": 100},
            ],
        }
        impression = (
            "Cranial MRI within normal limits; left sphenoidal and right ethmoidal sinusitis.\n"
            "Normal cerebral MR Angiography findings except for congenital right VA and left P1 hypoplasias."
        )
        payload = module.extract_impression_anatomy(impression, segmentation_labels)
        missing_regions = {record["region"] for record in payload["mentioned_without_segmentation_mask"]}
        self.assertIn("Left sphenoidal sinus", missing_regions)
        self.assertIn("Right ethmoidal sinus", missing_regions)
        self.assertIn("Right vertebral artery", missing_regions)
        self.assertIn("Left P1 segment", missing_regions)

    def test_radiological_report_to_roi_prepare_mrrate_case(self) -> None:
        unique = uuid.uuid4().hex
        fixture_root = REPO_ROOT / "test-output" / f"roi-prepare-{unique}"
        fixture_root.mkdir(parents=True, exist_ok=True)
        image_zip = fixture_root / "study.zip"
        segmentation_zip = fixture_root / "study_nvseg.zip"
        reports_csv = fixture_root / "reports.csv"
        labels_csv = fixture_root / "labels.csv"
        output_dir = fixture_root / "prepared"
        script = REPO_ROOT / "skills" / "radiological-report-to-roi" / "scripts" / "radiological_report_to_roi.py"

        try:
            with ZipFile(image_zip, "w") as archive:
                archive.writestr("CASE123/img/CASE123_t1w-raw-axi-2.nii.gz", b"image-2")
                archive.writestr("CASE123/img/CASE123_t1w-raw-axi.nii.gz", b"image-main")
            with ZipFile(segmentation_zip, "w") as archive:
                archive.writestr("CASE123/seg/CASE123_t1w-raw-axi-2_nvseg-ctmr-wb.nii.gz", b"seg-2")
                archive.writestr("CASE123/seg/CASE123_t1w-raw-axi_nvseg-ctmr-brain.nii.gz", b"seg-main")
            reports_csv.write_text(
                "study_uid,report,clinical_information,technique,findings,impression\n"
                "CASE123,Brainstem mentioned.,Numbness,T1,Brainstem normal,Normal\n",
                encoding="utf-8",
            )
            labels_csv.write_text("study_uid,Foo,Bar\nCASE123,0,1\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "prepare-mrrate-case",
                    "--study-uid",
                    "CASE123",
                    "--image-zip",
                    str(image_zip),
                    "--segmentation-zip",
                    str(segmentation_zip),
                    "--reports-csv",
                    str(reports_csv),
                    "--labels-csv",
                    str(labels_csv),
                    "--output-dir",
                    str(output_dir),
                    "--json",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["selected_image_entry"], "CASE123/img/CASE123_t1w-raw-axi.nii.gz")
            self.assertEqual(payload["selected_segmentation_entry"], "CASE123/seg/CASE123_t1w-raw-axi_nvseg-ctmr-brain.nii.gz")
            self.assertEqual(payload["positive_report_labels"], ["Bar"])
            self.assertTrue(Path(payload["image"]).exists())
            self.assertTrue(Path(payload["segmentation"]).exists())
            self.assertTrue(Path(payload["manifest"]).exists())
        finally:
            remove_tree(fixture_root)

    def test_evaluate_cli_json(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(["evaluate", "huggingface-datasets", "--json"])
        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["skill_id"], "huggingface-datasets")

    def test_help_and_getting_started_cli_json(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(["welcome", "--json"])
        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["topic"], "welcome")
        self.assertEqual(payload["title"], "Hi there, welcome to SkillForge!")
        self.assertEqual(payload["question"], "What would you like to do with SkillForge?")
        self.assertTrue(any("write an email" in example for example in payload["examples"]))
        self.assertIn("whole repositories into agentic skills", payload["message"])
        self.assertTrue(any("Git repo or codebase" in example for example in payload["examples"]))

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(["help", "search", "--json"])
        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["topic"], "search")
        self.assertTrue(any("corpus-search" in command["command"] for command in payload["commands"]))

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(["help", "install SkillForge", "--json"])
        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["topic"], "setup")
        self.assertTrue(any("install-skillforge" in command["command"] for command in payload["commands"]))

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(["help", "repo to skills", "--json"])
        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["topic"], "codebase")
        self.assertTrue(any("codebase-scan" in command["command"] for command in payload["commands"]))

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(["help", "pull request", "--json"])
        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["topic"], "contribute")
        self.assertTrue(any("contribute" in command["command"] for command in payload["commands"]))

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(["help", "improvement loop", "--json"])
        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["topic"], "improvement-loop")
        self.assertTrue(any("improve-cycle" in command["command"] for command in payload["commands"]))

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(["getting-started", "--json"])
        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["topic"], "getting-started")
        self.assertTrue(any("doctor" in step["command"] for step in payload["steps"]))

    def test_codebase_to_agentic_skills_scanner_generates_source_context_outputs(self) -> None:
        root = REPO_ROOT / "test-output" / f"repo-scan-{uuid.uuid4().hex}"
        repo = root / "demo-repo"
        output_dir = root / "scan-output"
        script = REPO_ROOT / "skills" / "codebase-to-agentic-skills" / "scripts" / "codebase_to_agentic_skills.py"
        try:
            (repo / "docs").mkdir(parents=True, exist_ok=True)
            (repo / "src").mkdir(parents=True, exist_ok=True)
            (repo / "configs").mkdir(parents=True, exist_ok=True)
            (repo / "examples").mkdir(parents=True, exist_ok=True)
            (repo / "notebooks").mkdir(parents=True, exist_ok=True)
            (repo / "data").mkdir(parents=True, exist_ok=True)
            (repo / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
            (repo / "README.md").write_text(
                "# Demo Repo\n\nQuick start: run the CLI.\n\nThis repo can segment medical images and also describes synthetic image generation and synthesis workflows.\n\n## Segmentation\n\n```bash\npip install monai\npython src/cli.py segment --input data/sample.nii.gz --output outputs\n```\n\n## Synthetic Image Generation\n\n```bash\npython src/cli.py run --config configs/mr.yaml --output outputs/mr\n```\n",
                encoding="utf-8",
            )
            (repo / "docs" / "tutorial.md").write_text(
                "# Tutorial\n\nParameter notes for MONAI NIfTI segmentation. Research use only; not for clinical diagnosis.\n",
                encoding="utf-8",
            )
            (repo / "notebooks" / "generation_tutorial.ipynb").write_text(
                json.dumps(
                    {
                        "cells": [
                            {
                                "cell_type": "markdown",
                                "metadata": {},
                                "source": ["# Notebook Synthetic MRI Generation\n"],
                            },
                            {
                                "cell_type": "code",
                                "execution_count": None,
                                "metadata": {},
                                "outputs": [],
                                "source": [
                                    "!python src/cli.py run --config configs/notebook.yaml --output outputs/notebook\n"
                                ],
                            },
                        ],
                        "metadata": {},
                        "nbformat": 4,
                        "nbformat_minor": 5,
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            (repo / "src" / "cli.py").write_text("def main():\n    return 0\n", encoding="utf-8")
            (repo / "configs" / "label_map.json").write_text('{"labels": []}\n', encoding="utf-8")
            (repo / "examples" / "demo.py").write_text("print('demo')\n", encoding="utf-8")
            (repo / "data" / "sample.nii.gz").write_bytes(b"")
            (repo / ".github" / "workflows" / "ci.yml").write_text("name: ci\n", encoding="utf-8")
            (repo / ".pre-commit-config.yaml").write_text(
                "Python linting and formatting (ruff) - fixes applied locally\n",
                encoding="utf-8",
            )
            (repo / "requirements.txt").write_text("numpy\n", encoding="utf-8")
            (repo / "LICENSE").write_text("Apache-2.0\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "scan",
                    str(repo),
                    "--workflow-goal",
                    "turn demo repo into skills",
                    "--output-dir",
                    str(output_dir),
                    "--json",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            self.assertGreaterEqual(payload["files_matched"], 6)
            categories = {row["category"]: row for row in payload["source_context_map"]}
            self.assertTrue(categories["readme_quickstart"]["artifacts"])
            self.assertTrue(categories["scripts_apis_notebooks"]["artifacts"])
            self.assertTrue(categories["configs_metadata_labels"]["artifacts"])
            self.assertTrue(categories["dependencies_runtime"]["artifacts"])
            signal_types = {signal["signal_type"] for signal in payload["healthcare_signals"]}
            self.assertIn("medical_imaging_format", signal_types)
            self.assertIn("monai_or_bundle", signal_types)
            self.assertIn("medical_safety", signal_types)
            summary_types = {row["signal_type"] for row in payload["healthcare_signal_summary"]}
            self.assertIn("medical_imaging_format", summary_types)
            self.assertIn("medical_safety", summary_types)
            self.assertTrue(any("docs/tutorial.md" in row["files_to_review"] for row in payload["healthcare_signal_summary"]))
            reading_plan_areas = {row["review_area"] for row in payload["healthcare_reading_plan"]}
            self.assertIn("Modality and file-format support", reading_plan_areas)
            self.assertIn("Medical safety, privacy, and intended-use boundaries", reading_plan_areas)
            self.assertTrue(all(row["claim_boundary"] for row in payload["healthcare_reading_plan"]))
            modality_plan = next(row for row in payload["healthcare_reading_plan"] if row["signal_type"] == "medical_imaging_format")
            self.assertTrue(modality_plan["evidence_hints"])
            self.assertTrue(all("caveat" in hint for hint in modality_plan["evidence_hints"]))
            safety_plan = next(row for row in payload["healthcare_reading_plan"] if row["signal_type"] == "medical_safety")
            self.assertTrue(any(hint["line"] and "Research use only" in hint["snippet"] for hint in safety_plan["evidence_hints"]))
            related_categories = {row["category"] for row in modality_plan["related_source_context"]}
            self.assertIn("readme_quickstart", related_categories)
            self.assertIn("docs_tutorials", related_categories)
            self.assertTrue(any("README.md" in row["artifacts"] for row in modality_plan["related_source_context"]))
            self.assertTrue(payload["candidate_skill_hypotheses"])
            self.assertTrue(payload["command_evidence"])
            commands_by_source = {(item["command"], item["source_path"]) for item in payload["command_evidence"]}
            self.assertIn(("pip install monai", "README.md"), commands_by_source)
            self.assertIn(("python src/cli.py segment --input data/sample.nii.gz --output outputs", "README.md"), commands_by_source)
            self.assertIn(("python src/cli.py run --config configs/mr.yaml --output outputs/mr", "README.md"), commands_by_source)
            self.assertIn(("python src/cli.py run --config configs/notebook.yaml --output outputs/notebook", "notebooks/generation_tutorial.ipynb"), commands_by_source)
            self.assertIn(("python src/cli.py --help", "src/cli.py"), commands_by_source)
            generation_command = next(
                item
                for item in payload["command_evidence"]
                if item["command"] == "python src/cli.py run --config configs/mr.yaml --output outputs/mr"
            )
            self.assertEqual(generation_command["source_heading"], "Synthetic Image Generation")
            notebook_command = next(
                item
                for item in payload["command_evidence"]
                if item["command"] == "python src/cli.py run --config configs/notebook.yaml --output outputs/notebook"
            )
            self.assertEqual(notebook_command["source_heading"], "Notebook Synthetic MRI Generation")
            self.assertEqual(notebook_command["source_type"], "notebook-code-cell:2")
            install_command = next(item for item in payload["command_evidence"] if item["command"] == "pip install monai")
            self.assertEqual(install_command["side_effect_risk"], "network-or-install")
            self.assertIn("install", install_command["side_effect_categories"])
            self.assertIn("network-access", install_command["side_effect_categories"])
            self.assertIn("environment-management", install_command["side_effect_categories"])
            self.assertEqual(install_command["execution_gate"]["gate"], "needs-user-approval")
            self.assertIn("runtime-plan", install_command["execution_gate"]["required_reviews"])
            readme_command = next(
                item
                for item in payload["command_evidence"]
                if item["command"] == "python src/cli.py segment --input data/sample.nii.gz --output outputs"
            )
            self.assertEqual(readme_command["source_type"], "documented-command")
            self.assertEqual(readme_command["platform_assumption"], "python-environment")
            self.assertEqual(readme_command["side_effect_risk"], "compute-or-model-run")
            self.assertIn("file-write", readme_command["side_effect_categories"])
            self.assertIn("gpu-or-model-execution", readme_command["side_effect_categories"])
            self.assertEqual(readme_command["execution_gate"]["gate"], "needs-data-safety-review")
            self.assertIn("data-safety-review", readme_command["execution_gate"]["required_reviews"])
            help_command = next(item for item in payload["command_evidence"] if item["command"] == "python src/cli.py --help")
            self.assertEqual(help_command["execution_gate"]["gate"], "safe-to-inspect")
            self.assertEqual(payload["command_evidence_summary"]["highest_risk_category"], "install")
            summary_categories = {row["category"]: row["count"] for row in payload["command_evidence_summary"]["categories"]}
            self.assertGreaterEqual(summary_categories["install"], 1)
            self.assertGreaterEqual(summary_categories["network-access"], 1)
            self.assertGreaterEqual(summary_categories["file-write"], 1)
            self.assertGreaterEqual(summary_categories["gpu-or-model-execution"], 1)
            summary_gates = {row["gate"]: row["count"] for row in payload["command_evidence_summary"]["execution_gates"]}
            self.assertGreaterEqual(summary_gates["needs-user-approval"], 1)
            self.assertGreaterEqual(summary_gates["needs-data-safety-review"], 1)
            self.assertGreaterEqual(summary_gates["safe-to-inspect"], 1)
            summary_policies = {
                row["adapter_type"]: row["count"] for row in payload["command_evidence_summary"]["adapter_policies"]
            }
            self.assertGreaterEqual(summary_policies["setup-plan"], 1)
            self.assertGreaterEqual(summary_policies["guarded-run"], 1)
            self.assertGreaterEqual(summary_policies["read-only-check"], 1)
            self.assertGreaterEqual(summary_policies["no-adapter-until-review"], 1)
            self.assertEqual(payload["command_evidence_summary"]["highest_adapter_policy"], "no-adapter-until-review")
            self.assertEqual(payload["command_evidence_summary"]["recommended_adapter_policy"], "guarded-run")
            self.assertEqual(payload["command_evidence_summary"]["adapter_recommendation_basis"], "workflow-command-evidence")
            self.assertTrue(payload["command_evidence_summary"]["adapter_policies_ignored_for_recommendation"])
            hypothesis = payload["candidate_skill_hypotheses"][0]
            self.assertTrue(hypothesis["provisional"])
            self.assertEqual(hypothesis["recommendation"], "provisional-needs-source-review")
            self.assertIn("segmentation", hypothesis["candidate_skill"].lower())
            self.assertTrue(hypothesis["candidate_skill"].startswith("demo-repo "))
            self.assertEqual(hypothesis["generic_candidate_skill"], "Research medical image segmentation workflow")
            self.assertEqual(hypothesis["source_project_name"], "demo-repo")
            self.assertEqual(hypothesis["workflow_goal_match_score"], 0)
            self.assertEqual(hypothesis["source_coverage"]["present_count"], 7)
            self.assertEqual(hypothesis["source_coverage"]["total"], 8)
            self.assertEqual(hypothesis["source_coverage"]["status"], "strong-source-coverage")
            self.assertIn("Model/data/paper provenance", hypothesis["source_coverage"]["missing"])
            self.assertIn("Executable entrypoints", hypothesis["source_coverage"]["present"])
            self.assertEqual(hypothesis["provisional_cli_draft"]["status"], "source-grounded-commands-detected")
            self.assertEqual(hypothesis["provisional_cli_draft"]["recommended_adapter_policy"], "guarded-run")
            draft_policy_types = {
                row["adapter_type"]: row["count"]
                for row in hypothesis["provisional_cli_draft"]["adapter_policy_summary"]["policies"]
            }
            self.assertGreaterEqual(draft_policy_types["guarded-run"], 1)
            self.assertGreaterEqual(draft_policy_types["no-adapter-until-review"], 1)
            self.assertEqual(hypothesis["provisional_cli_draft"]["adapter_policy_summary"]["highest_policy"], "no-adapter-until-review")
            self.assertEqual(hypothesis["provisional_cli_draft"]["adapter_policy_summary"]["recommended_policy"], "guarded-run")
            self.assertEqual(hypothesis["provisional_cli_draft"]["adapter_policy_summary"]["recommendation_basis"], "candidate-command-evidence")
            self.assertIn("segmentation", hypothesis["provisional_cli_draft"]["adapter_policy_summary"]["candidate_terms"])
            ignored = hypothesis["provisional_cli_draft"]["adapter_policy_summary"]["ignored_for_recommendation"]
            self.assertTrue(any(item["source_path"] == ".pre-commit-config.yaml" for item in ignored))
            adapter_stubs = {
                row["adapter_type"]: row
                for row in hypothesis["provisional_cli_draft"]["adapter_plan_stubs"]
            }
            self.assertIn("read-only-check", adapter_stubs)
            self.assertIn("setup-plan", adapter_stubs)
            self.assertIn("guarded-run", adapter_stubs)
            self.assertFalse(adapter_stubs["read-only-check"]["confirm_execution_required"])
            self.assertTrue(adapter_stubs["guarded-run"]["confirm_execution_required"])
            self.assertIn("--confirm-execution", " ".join(adapter_stubs["guarded-run"]["suggested_commands"]))
            self.assertIn("data-safety-review", adapter_stubs["guarded-run"]["required_reviews"])
            self.assertIn("summarize install commands instead of running them", adapter_stubs["setup-plan"]["guardrails"])
            self.assertTrue(
                any(
                    command.get("adapter_policy", {}).get("adapter_type") == "guarded-run"
                    for command in hypothesis["provisional_cli_draft"]["suggested_commands"]
                )
            )
            self.assertIn("src/cli.py", hypothesis["provisional_cli_draft"]["entrypoint_refs"])
            self.assertIn("requirements.txt", hypothesis["provisional_cli_draft"]["runtime_refs"])
            draft_commands = [command["command"] for command in hypothesis["provisional_cli_draft"]["suggested_commands"]]
            self.assertIn("python src/cli.py segment --input data/sample.nii.gz --output outputs", draft_commands)
            self.assertIn("python src/cli.py run --config configs/mr.yaml --output outputs/mr", draft_commands)
            self.assertLess(
                draft_commands.index("python src/cli.py segment --input data/sample.nii.gz --output outputs"),
                draft_commands.index("python src/cli.py run --config configs/mr.yaml --output outputs/mr"),
            )
            self.assertIn("python src/cli.py --help", draft_commands)
            self.assertTrue(hypothesis["provisional_cli_draft"]["source_command_refs"])
            self.assertTrue(all(command["side_effects"] for command in hypothesis["provisional_cli_draft"]["suggested_commands"]))
            self.assertTrue(hypothesis["source_context_refs"])
            self.assertTrue(hypothesis["healthcare_review_refs"])
            self.assertTrue((output_dir / "source-context-map.md").exists())
            self.assertTrue((output_dir / "candidate-skill-table.md").exists())
            self.assertTrue((output_dir / "readiness-card-draft.md").exists())
            self.assertTrue((output_dir / "scan.json").exists())
            source_context_markdown = (output_dir / "source-context-map.md").read_text(encoding="utf-8")
            self.assertIn("Healthcare Signal Summary", source_context_markdown)
            self.assertIn("Healthcare Reading Plan", source_context_markdown)
            self.assertIn("Evidence hints", source_context_markdown)
            self.assertIn("Related source context", source_context_markdown)
            self.assertIn("Command Evidence Summary", source_context_markdown)
            self.assertIn("Command Evidence", source_context_markdown)
            self.assertIn("Execution gates", source_context_markdown)
            self.assertIn("Adapter policies", source_context_markdown)
            self.assertIn("needs-data-safety-review", source_context_markdown)
            self.assertIn("needs-user-approval", source_context_markdown)
            self.assertIn("guarded-run", source_context_markdown)
            self.assertIn("setup-plan", source_context_markdown)
            self.assertIn("network-access", source_context_markdown)
            self.assertIn("gpu-or-model-execution", source_context_markdown)
            self.assertIn("compute-or-model-run", source_context_markdown)
            self.assertIn("Healthcare And Medical Imaging Signals", source_context_markdown)
            candidate_markdown = (output_dir / "candidate-skill-table.md").read_text(encoding="utf-8")
            self.assertIn("## Source Provenance", candidate_markdown)
            self.assertIn("Source version status", candidate_markdown)
            self.assertIn("Source commit", candidate_markdown)
            self.assertIn("Source branch", candidate_markdown)
            self.assertIn("Source remote", candidate_markdown)
            self.assertIn("Source dirty worktree", candidate_markdown)
            self.assertIn("Used safe.directory override", candidate_markdown)
            self.assertIn("Candidate Review Summaries", candidate_markdown)
            self.assertIn("Use these compact summaries for first-pass human review", candidate_markdown)
            self.assertIn("Workflow-goal match terms", candidate_markdown)
            self.assertIn("First source-context review", candidate_markdown)
            self.assertIn("First healthcare review", candidate_markdown)
            self.assertIn("Adapter recommendation basis", candidate_markdown)
            self.assertIn("Ignored for candidate adapter recommendation", candidate_markdown)
            self.assertIn("Provisional Candidate Skill Hypotheses", candidate_markdown)
            self.assertIn("provisional-needs-source-review", candidate_markdown)
            self.assertIn("Source coverage", candidate_markdown)
            self.assertIn("7/8", candidate_markdown)
            self.assertIn("Adapter policy", candidate_markdown)
            self.assertIn("Adapter plan stubs", candidate_markdown)
            self.assertIn("--confirm-execution", candidate_markdown)
            self.assertIn("Provisional CLI draft", candidate_markdown)
            self.assertIn("python src/cli.py segment --input data/sample.nii.gz --output outputs", candidate_markdown)
            self.assertIn("python src/cli.py --help", candidate_markdown)

            goal_order_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "scan",
                    str(repo),
                    "--workflow-goal",
                    "create a synthetic medical image generation skill",
                    "--max-total-files",
                    "50",
                    "--json",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(goal_order_result.returncode, 0, goal_order_result.stderr)
            goal_order_payload = json.loads(goal_order_result.stdout)
            first_goal_hypothesis = goal_order_payload["candidate_skill_hypotheses"][0]
            self.assertGreater(first_goal_hypothesis["workflow_goal_match_score"], 0)
            self.assertTrue(
                "generation" in first_goal_hypothesis["candidate_skill"].lower()
                or "synthetic" in first_goal_hypothesis["candidate_skill"].lower()
            )
            self.assertTrue(first_goal_hypothesis["candidate_skill"].startswith("demo-repo "))
            self.assertTrue(
                {"generation", "synthetic"}.intersection(first_goal_hypothesis["workflow_goal_match_terms"])
            )
            goal_draft_commands = [
                command["command"]
                for command in first_goal_hypothesis["provisional_cli_draft"]["suggested_commands"]
            ]
            self.assertIn("python src/cli.py run --config configs/mr.yaml --output outputs/mr", goal_draft_commands)
            self.assertIn("python src/cli.py segment --input data/sample.nii.gz --output outputs", goal_draft_commands)
            self.assertLess(
                goal_draft_commands.index("python src/cli.py run --config configs/mr.yaml --output outputs/mr"),
                goal_draft_commands.index("python src/cli.py segment --input data/sample.nii.gz --output outputs"),
            )
            self.assertEqual(
                first_goal_hypothesis["provisional_cli_draft"]["adapter_policy_summary"]["recommendation_basis"],
                "candidate-command-evidence",
            )
            self.assertIn(
                "generate",
                first_goal_hypothesis["provisional_cli_draft"]["adapter_policy_summary"]["candidate_terms"],
            )
            goal_run_command = next(
                command
                for command in first_goal_hypothesis["provisional_cli_draft"]["suggested_commands"]
                if command["command"] == "python src/cli.py run --config configs/mr.yaml --output outputs/mr"
            )
            self.assertEqual(goal_run_command["source_heading"], "Synthetic Image Generation")
            self.assertIn("generation", goal_run_command["candidate_relevance"]["matched_candidate_terms"])

            cli_output_dir = root / "cli-scan-output"
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main(
                    [
                        "codebase-scan",
                        str(repo),
                        "--workflow-goal",
                        "turn demo repo into skills",
                        "--output-dir",
                        str(cli_output_dir),
                        "--max-total-files",
                        "4",
                        "--json",
                    ]
                )
            self.assertEqual(exit_code, 0)
            cli_payload = json.loads(stdout.getvalue())
            self.assertTrue(cli_payload["ok"])
            cli_categories = {row["category"]: row for row in cli_payload["source_context_map"]}
            self.assertTrue(any(item["path"] == "README.md" for item in cli_categories["readme_quickstart"]["artifacts"]))
            self.assertIn("healthcare_signals", cli_payload)
            self.assertIn("healthcare_signal_summary", cli_payload)
            self.assertIn("healthcare_reading_plan", cli_payload)
            self.assertIn("command_evidence", cli_payload)
            self.assertIn("candidate_skill_hypotheses", cli_payload)
            self.assertTrue((cli_output_dir / "source-context-map.md").exists())
        finally:
            remove_tree(root)

    def test_codebase_to_agentic_skills_git_commit_handles_safe_directory(self) -> None:
        script = REPO_ROOT / "skills" / "codebase-to-agentic-skills" / "scripts" / "codebase_to_agentic_skills.py"
        spec = importlib.util.spec_from_file_location("codebase_to_agentic_skills_safe_directory_test", script)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

        calls = []

        class FakeResult:
            def __init__(self, returncode: int, stdout: str = "", stderr: str = "") -> None:
                self.returncode = returncode
                self.stdout = stdout
                self.stderr = stderr

        def fake_run(command, **kwargs):
            calls.append(command)
            if command[-2:] == ["rev-parse", "HEAD"] and "-c" not in command:
                return FakeResult(
                    128,
                    stderr="fatal: detected dubious ownership in repository\nTo add an exception, call git config --global --add safe.directory <path>",
                )
            if command[-2:] == ["rev-parse", "HEAD"]:
                return FakeResult(0, stdout="abc123\n")
            if command[-3:] == ["rev-parse", "--abbrev-ref", "HEAD"]:
                return FakeResult(0, stdout="main\n")
            if command[-3:] == ["config", "--get", "remote.origin.url"]:
                return FakeResult(0, stdout="https://github.com/example/source.git\n")
            if command[-2:] == ["status", "--porcelain"]:
                return FakeResult(0, stdout=" M README.md\n")
            return FakeResult(1, stderr="unexpected git command")

        original_which = module.shutil.which
        original_run = module.subprocess.run
        try:
            module.shutil.which = lambda value: "git" if value == "git" else original_which(value)
            module.subprocess.run = fake_run
            payload = module.git_commit(Path("C:/source/NV-Generate-CTMR"))
        finally:
            module.shutil.which = original_which
            module.subprocess.run = original_run

        self.assertEqual(payload["commit"], "abc123")
        self.assertEqual(payload["branch"], "main")
        self.assertEqual(payload["remote_url"], "https://github.com/example/source.git")
        self.assertTrue(payload["dirty"])
        self.assertEqual(payload["status"], "ok-safe-directory-override")
        self.assertTrue(payload["safe_directory_override"])
        self.assertEqual(calls[1][1], "-c")
        self.assertTrue(str(calls[1][2]).startswith("safe.directory="))
        self.assertTrue(all("-c" in command for command in calls[1:]))

    def test_codebase_to_agentic_skills_scaffolds_review_only_adapter(self) -> None:
        script = REPO_ROOT / "skills" / "codebase-to-agentic-skills" / "scripts" / "codebase_to_agentic_skills.py"
        root = REPO_ROOT / "test-output" / f"adapter-scaffold-{uuid.uuid4().hex}"
        output_dir = root / "skill"
        try:
            helper_schema = subprocess.run(
                [sys.executable, str(script), "schema", "--json"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(helper_schema.returncode, 0, helper_schema.stderr)
            helper_schema_payload = json.loads(helper_schema.stdout)
            self.assertIn("scaffold-adapter", helper_schema_payload["commands"])

            result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "scaffold-adapter",
                    "setup-plan",
                    "--adapter-name",
                    "Demo Adapter",
                    "--output-dir",
                    str(output_dir),
                    "--json",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["review_only"])
            self.assertEqual(payload["adapter_name"], "demo_adapter")
            self.assertEqual(payload["adapter_type"], "setup-plan")
            self.assertEqual(payload["supported_commands"], ["schema", "check", "setup-plan"])
            self.assertIn("run", payload["blocked_commands"])

            adapter_script = Path(payload["written_files"]["adapter_script"])
            self.assertTrue(adapter_script.exists())
            script_text = adapter_script.read_text(encoding="utf-8")
            self.assertIn("REVIEW_ONLY = True", script_text)
            self.assertIn("setup-plan", script_text)
            self.assertNotIn("confirm-execution", script_text)

            schema = subprocess.run(
                [sys.executable, str(adapter_script), "schema", "--json"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(schema.returncode, 0, schema.stderr)
            schema_payload = json.loads(schema.stdout)
            self.assertTrue(schema_payload["review_only"])
            command_names = [command["name"] for command in schema_payload["commands"]]
            self.assertEqual(command_names, ["schema", "check", "setup-plan"])
            self.assertIn("run", schema_payload["blocked_commands"])

            check = subprocess.run(
                [sys.executable, str(adapter_script), "check", "--source-dir", str(root / "missing"), "--json"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(check.returncode, 0, check.stderr)
            check_payload = json.loads(check.stdout)
            self.assertTrue(check_payload["ok"])
            self.assertFalse(check_payload["source_exists"])
            self.assertFalse(check_payload["ready_for_execution"])
            self.assertEqual(check_payload["writes"], "none")
            self.assertEqual(check_payload["network"], "not-used")

            setup_plan = subprocess.run(
                [
                    sys.executable,
                    str(adapter_script),
                    "setup-plan",
                    "--source-dir",
                    str(root),
                    "--target",
                    "wsl2-linux",
                    "--json",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(setup_plan.returncode, 0, setup_plan.stderr)
            setup_payload = json.loads(setup_plan.stdout)
            self.assertTrue(setup_payload["approval_required"])
            self.assertFalse(setup_payload["executed"])
            self.assertEqual(setup_payload["side_effects_performed"], [])
            self.assertTrue(setup_payload["planned_commands"])
            self.assertIn("summarize install commands instead of running them", setup_payload["guardrails"])

            top_level_output = root / "top-level"
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main(
                    [
                        "codebase-scaffold-adapter",
                        "read-only-check",
                        "--adapter-name",
                        "Top Level Adapter",
                        "--output-dir",
                        str(top_level_output),
                        "--json",
                    ]
                )
            top_payload = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertTrue(top_payload["ok"])
            self.assertTrue(Path(top_payload["written_files"]["adapter_script"]).exists())

            scan_json = root / "scan.json"
            scan_json.write_text(
                json.dumps(
                    {
                        "ok": True,
                        "source_version": {
                            "commit": "abc123",
                            "branch": "main",
                            "remote_url": "https://github.com/example/demo.git",
                            "dirty": False,
                            "status": "ok",
                            "safe_directory_override": False,
                        },
                        "candidate_skill_hypotheses": [
                            {
                                "candidate_skill": "Demo Segmentation",
                                "hypothesis_id": "demo-segmentation",
                                "provisional_cli_draft": {
                                    "recommended_adapter_policy": "guarded-run",
                                    "adapter_plan_stubs": [
                                        {
                                            "adapter_type": "guarded-run",
                                            "title": "Guarded-run adapter",
                                            "status": "stub-needs-source-review",
                                            "purpose": "Plan and optionally run a reviewed segmentation command.",
                                            "suggested_commands": [
                                                "python scripts/demo_adapter.py plan --source-dir <source-dir> --input <input-path> --output-dir <output-dir> --json",
                                                "python scripts/demo_adapter.py run --source-dir <source-dir> --input <input-path> --output-dir <output-dir> --confirm-execution --json",
                                            ],
                                            "required_inputs": ["source-dir", "input-path", "output-dir", "confirm-execution"],
                                            "expected_outputs": ["JSON plan", "segmentation output path"],
                                            "guardrails": [
                                                "require --confirm-execution for side-effecting runs",
                                                "do not log sensitive input content",
                                            ],
                                            "required_reviews": ["source-review", "runtime-plan", "data-safety-review"],
                                            "confirm_execution_required": True,
                                            "source_commands": [
                                                {
                                                    "command": "python segment.py --input sample.nii.gz --output out",
                                                    "source_path": "README.md",
                                                    "source_line": 42,
                                                    "side_effect_categories": ["file-write", "gpu-or-model-execution"],
                                                }
                                            ],
                                            "source_refs": {
                                                "entrypoints": ["scripts/segment.py"],
                                                "configs": ["configs/demo.yaml"],
                                                "runtime": ["requirements.txt"],
                                            },
                                            "smoke_test_stub": ["plan command is read-only"],
                                            "caveat": "Review source evidence before implementing execution.",
                                        }
                                    ],
                                },
                            }
                        ],
                    },
                    indent=2,
                    sort_keys=True,
                ),
                encoding="utf-8",
            )

            scan_output = root / "from-scan"
            scan_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "scaffold-adapter",
                    "--from-scan-json",
                    str(scan_json),
                    "--candidate-id",
                    "demo-segmentation",
                    "--stub-type",
                    "guarded-run",
                    "--output-dir",
                    str(scan_output),
                    "--json",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(scan_result.returncode, 0, scan_result.stderr)
            scan_payload = json.loads(scan_result.stdout)
            self.assertTrue(scan_payload["ok"])
            self.assertEqual(scan_payload["adapter_name"], "demo_segmentation_guarded_run_adapter")
            self.assertEqual(scan_payload["adapter_type"], "guarded-run")
            self.assertEqual(scan_payload["candidate_skill"], "Demo Segmentation")
            self.assertEqual(scan_payload["scan_source"]["candidate_index"], 0)
            self.assertEqual(scan_payload["scan_source"]["stub_index"], 0)
            self.assertEqual(scan_payload["scan_source"]["source_version"]["commit"], "abc123")
            self.assertEqual(scan_payload["adapter_plan_stub"]["source_refs"]["entrypoints"], ["scripts/segment.py"])

            scan_adapter_script = Path(scan_payload["written_files"]["adapter_script"])
            self.assertTrue(scan_adapter_script.exists())
            scan_schema = subprocess.run(
                [sys.executable, str(scan_adapter_script), "schema", "--json"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(scan_schema.returncode, 0, scan_schema.stderr)
            scan_schema_payload = json.loads(scan_schema.stdout)
            self.assertTrue(scan_schema_payload["review_only"])
            self.assertEqual(scan_schema_payload["adapter_plan_stub"]["confirm_execution_required"], True)
            self.assertEqual(scan_schema_payload["adapter_plan_stub"]["source_refs"]["runtime"], ["requirements.txt"])
            self.assertEqual(
                scan_schema_payload["scaffold_metadata"]["scan_source"]["source_version"]["remote_url"],
                "https://github.com/example/demo.git",
            )
            self.assertNotIn("run", [command["name"] for command in scan_schema_payload["commands"]])

            top_level_scan_output = root / "top-level-from-scan"
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main(
                    [
                        "codebase-scaffold-adapter",
                        "--from-scan-json",
                        str(scan_json),
                        "--stub-type",
                        "guarded-run",
                        "--output-dir",
                        str(top_level_scan_output),
                        "--json",
                    ]
                )
            top_scan_payload = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertTrue(top_scan_payload["ok"])
            self.assertEqual(top_scan_payload["adapter_type"], "guarded-run")
            self.assertTrue(Path(top_scan_payload["written_files"]["adapter_script"]).exists())
        finally:
            remove_tree(root)

    def test_codebase_to_agentic_skills_scan_scaffold_reports_selection_errors(self) -> None:
        script = REPO_ROOT / "skills" / "codebase-to-agentic-skills" / "scripts" / "codebase_to_agentic_skills.py"
        root = REPO_ROOT / "test-output" / f"adapter-scaffold-errors-{uuid.uuid4().hex}"
        scan_json = root / "scan.json"
        output_dir = root / "skill"
        try:
            root.mkdir(parents=True, exist_ok=True)
            scan_json.write_text(
                json.dumps(
                    {
                        "ok": True,
                        "candidate_skill_hypotheses": [
                            {
                                "candidate_skill": "Demo Segmentation",
                                "hypothesis_id": "demo-segmentation",
                                "provisional_cli_draft": {
                                    "recommended_adapter_policy": "setup-plan",
                                    "adapter_plan_stubs": [
                                        {
                                            "adapter_type": "setup-plan",
                                            "title": "Setup-plan adapter",
                                            "status": "stub-needs-source-review",
                                            "purpose": "Plan setup without installing dependencies.",
                                            "suggested_commands": [
                                                "python scripts/demo_adapter.py setup-plan --source-dir <source-dir> --target <target> --json"
                                            ],
                                            "required_inputs": ["source-dir", "runtime-target"],
                                            "expected_outputs": ["JSON setup plan"],
                                            "guardrails": ["summarize install commands instead of running them"],
                                            "required_reviews": ["source-review", "human-approval"],
                                            "confirm_execution_required": False,
                                            "source_commands": [],
                                            "source_refs": {
                                                "entrypoints": ["README.md"],
                                                "configs": [],
                                                "runtime": ["requirements.txt"],
                                            },
                                            "smoke_test_stub": ["setup-plan emits commands as data"],
                                            "caveat": "Review source evidence before implementation.",
                                        }
                                    ],
                                },
                            }
                        ],
                    },
                    indent=2,
                    sort_keys=True,
                ),
                encoding="utf-8",
            )

            missing_candidate = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "scaffold-adapter",
                    "--from-scan-json",
                    str(scan_json),
                    "--candidate-id",
                    "not-a-candidate",
                    "--output-dir",
                    str(output_dir),
                    "--json",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(missing_candidate.returncode, 1)
            missing_candidate_payload = json.loads(missing_candidate.stdout)
            self.assertFalse(missing_candidate_payload["ok"])
            self.assertIn("No candidate matched", missing_candidate_payload["error"])
            self.assertIn("Demo Segmentation", missing_candidate_payload["error"])

            missing_stub = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "scaffold-adapter",
                    "--from-scan-json",
                    str(scan_json),
                    "--stub-type",
                    "guarded-run",
                    "--output-dir",
                    str(output_dir),
                    "--json",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(missing_stub.returncode, 1)
            missing_stub_payload = json.loads(missing_stub.stdout)
            self.assertFalse(missing_stub_payload["ok"])
            self.assertIn("No adapter_plan_stub matched", missing_stub_payload["error"])
            self.assertIn("setup-plan", missing_stub_payload["error"])

            conflict = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "scaffold-adapter",
                    "setup-plan",
                    "--from-scan-json",
                    str(scan_json),
                    "--stub-type",
                    "guarded-run",
                    "--output-dir",
                    str(output_dir),
                    "--json",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(conflict.returncode, 1)
            conflict_payload = json.loads(conflict.stdout)
            self.assertFalse(conflict_payload["ok"])
            self.assertIn("conflicts with --stub-type", conflict_payload["error"])

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main(
                    [
                        "codebase-scaffold-adapter",
                        "--from-scan-json",
                        str(scan_json),
                        "--stub-type",
                        "guarded-run",
                        "--output-dir",
                        str(root / "top-level"),
                        "--json",
                    ]
                )
            top_level_payload = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 1)
            self.assertFalse(top_level_payload["ok"])
            self.assertIn("Available types: setup-plan", top_level_payload["error"])
        finally:
            remove_tree(root)

    def test_improve_cycle_cli_writes_log_and_coordinates_lock(self) -> None:
        root = REPO_ROOT / "test-output" / f"improve-cycle-{uuid.uuid4().hex}"
        log_dir = root / "improvement-loop"
        lock_dir = root / ".skillforge" / "improvement-loop"
        lock_path = lock_dir / "active-run.json"
        remove_tree(lock_dir)
        try:
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main(
                    [
                        "improve-cycle",
                        "--write-log",
                        "--claim-run",
                        "--log-dir",
                        str(log_dir),
                        "--lock-path",
                        str(lock_path),
                        "--stale-minutes",
                        "120",
                        "--json",
                    ]
                )
            payload = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["read_only"])
            self.assertEqual(payload["selected_lane"], "builder")
            self.assertTrue(payload["healthcare_domain_focus"])
            self.assertTrue(any("NVIDIA-Medtech" in source["name"] for source in payload["healthcare_sources"]))
            self.assertTrue(payload["concurrency"]["lock"]["claimed"])
            self.assertTrue(Path(payload["log_path"]).exists())
            self.assertTrue(lock_path.exists())
            run_id = payload["run_id"]

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main(
                    [
                        "improve-cycle",
                        "--claim-run",
                        "--log-dir",
                        str(log_dir),
                        "--lock-path",
                        str(lock_path),
                        "--json",
                    ]
                )
            second_payload = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertFalse(second_payload["concurrency"]["lock"]["claimed"])
            self.assertTrue(any("Another" in warning or "active" in warning for warning in second_payload["warnings"]))

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main(["improve-cycle", "--release-run", run_id, "--lock-path", str(lock_path), "--json"])
            release_payload = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertTrue(release_payload["released"])
            self.assertFalse(lock_path.exists())
        finally:
            remove_tree(root)
            remove_tree(lock_dir)

    def test_chattiness_coach_adds_search_next_steps(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(["search", "youtube", "--chattiness", "coach"])
        self.assertEqual(exit_code, 0)
        output = stdout.getvalue()
        self.assertIn("Next steps:", output)
        self.assertIn("python -m skillforge info", output)

    def test_chattiness_defaults_to_coach_until_user_overrides(self) -> None:
        previous = os.environ.pop("SKILLFORGE_CHATTINESS", None)
        try:
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main(["welcome"])
            self.assertEqual(exit_code, 0)
            self.assertIn("What SkillForge will do:", stdout.getvalue())

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main(["welcome", "--chattiness", "normal"])
            self.assertEqual(exit_code, 0)
            self.assertNotIn("What SkillForge will do:", stdout.getvalue())
        finally:
            if previous is not None:
                os.environ["SKILLFORGE_CHATTINESS"] = previous

    def test_modules_manifest_documents_python_package(self) -> None:
        manifest_path = REPO_ROOT / "skillforge" / "modules.toml"
        manifest = manifest_path.read_text(encoding="utf-8")
        self.assertIn('path = "skillforge/cli.py"', manifest)
        self.assertIn('path = "skillforge/update.py"', manifest)
        template = (REPO_ROOT / "skillforge" / "templates" / "python" / "module.md.tmpl").read_text(encoding="utf-8")
        self.assertIn("## Responsibilities", template)
        self.assertIn("## Side Effects And Safety", template)
        self.assertIn("skillforge/modules.toml", template)
        payload = tomllib.loads(manifest)
        for module in payload["module"]:
            self.assertTrue((REPO_ROOT / module["path"]).exists(), module["path"])
            for doc_path in module["docs"]:
                self.assertTrue((REPO_ROOT / doc_path).exists(), doc_path)

    def test_update_check_and_whats_new_use_git_history(self) -> None:
        unique = uuid.uuid4().hex
        repo = REPO_ROOT / "test-output" / f"update-repo-{unique}"
        cache_dir = REPO_ROOT / "test-output" / f"update-cache-{unique}"

        def git(args: list[str], cwd) -> str:
            result = subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True, shell=False)
            if result.returncode != 0:
                self.fail(f"git {' '.join(args)} failed: {result.stderr or result.stdout}")
            return result.stdout.strip()

        try:
            repo.mkdir(parents=True)
            git(["init"], repo)
            (repo / "README.md").write_text("one\n", encoding="utf-8")
            git(["add", "README.md"], repo)
            git(["-c", "user.name=SkillForge Test", "-c", "user.email=test@example.com", "commit", "-m", "Initial docs"], repo)
            first_commit = git(["rev-parse", "HEAD"], repo)

            (repo / "README.md").write_text("one\ntwo\n", encoding="utf-8")
            (repo / "docs").mkdir()
            (repo / "docs" / "skill-search-seo-plan.md").write_text("# SEO\n", encoding="utf-8")
            (repo / "site" / "skills" / "demo-skill").mkdir(parents=True)
            (repo / "site" / "skills" / "demo-skill" / "index.html").write_text("<h1>Demo</h1>\n", encoding="utf-8")
            (repo / "skills" / "demo-skill").mkdir(parents=True)
            (repo / "skills" / "demo-skill" / "README.md").write_text("# Demo Skill\n", encoding="utf-8")
            git(["add", "README.md", "docs/skill-search-seo-plan.md", "site/skills/demo-skill/index.html", "skills/demo-skill/README.md"], repo)
            git(["-c", "user.name=SkillForge Test", "-c", "user.email=test@example.com", "commit", "-m", "Improve SEO discovery"], repo)
            second_commit = git(["rev-parse", "HEAD"], repo)
            git(["remote", "add", "origin", "https://example.invalid/skillforge-test.git"], repo)
            git(["update-ref", "refs/remotes/origin/main", second_commit], repo)
            git(["checkout", "-b", "local-main", first_commit], repo)
            git(["branch", "--set-upstream-to=origin/main", "local-main"], repo)

            payload = update_check(repo_root=repo, cache_dir=cache_dir, no_fetch=True, ttl_hours=0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["updates_available"])
            self.assertEqual(payload["behind_by"], 1)
            self.assertTrue(payload["cache"]["write_ok"])

            changes = whats_new(repo_root=repo, cache_dir=cache_dir, since=first_commit, until="origin/main")
            self.assertEqual(changes["commit_count"], 1)
            self.assertIn("README.md", changes["categories"]["documentation"])
            self.assertIn("demo-skill", changes["categories"]["new_skills"])
            self.assertTrue(any("Improve SEO discovery" in commit["summary"] for commit in changes["commits"]))
            self.assertTrue(any("discovery and SEO" in line for line in changes["summary"]))
            self.assertTrue(any("Found 1 commits" in line for line in changes["technical_summary"]))
            self.assertTrue(changes["detail_prompt"].startswith("Would you like more detail"))

            dry_run = update_skillforge(repo_root=repo, cache_dir=cache_dir, no_fetch=True)
            self.assertTrue(dry_run["ok"])
            self.assertFalse(dry_run["updated"])
            self.assertTrue(dry_run["requires_confirmation"])
            self.assertEqual(git(["rev-parse", "HEAD"], repo), first_commit)

            applied = update_skillforge(repo_root=repo, cache_dir=cache_dir, yes=True, no_fetch=True)
            self.assertTrue(applied["ok"])
            self.assertTrue(applied["updated"])
            self.assertEqual(applied["previous_commit"], first_commit)
            self.assertEqual(applied["current_commit"], second_commit)
            self.assertEqual(git(["rev-parse", "HEAD"], repo), second_commit)
            self.assertEqual(applied["whats_new"]["commit_count"], 1)
            self.assertTrue(any("discovery and SEO" in line for line in applied["whats_new"]["summary"]))
            self.assertEqual(applied["post_check"]["behind_by"], 0)
        finally:
            remove_tree(repo)
            remove_tree(cache_dir)

    def test_create_scaffolds_skill_and_evaluate_flags_placeholders(self) -> None:
        skill_id = f"test-create-{uuid.uuid4().hex[:8]}"
        skill_dir = REPO_ROOT / "skills" / skill_id
        stdout = io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout):
                exit_code = main(
                    [
                        "create",
                        skill_id,
                        "--title",
                        "Test Create Skill",
                        "--description",
                        "Help verify the SkillForge create workflow.",
                        "--owner",
                        "test-owner",
                        "--category",
                        "Developer Tools",
                        "--tag",
                        "testing",
                        "--risk-level",
                        "low",
                        "--json",
                    ]
                )
            payload = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertTrue((skill_dir / "SKILL.md").exists())
            self.assertTrue((skill_dir / "README.md").exists())
            self.assertIn("README.md", payload["placeholders_remaining"])

            evaluation = evaluate_skill(skill_dir)
            self.assertFalse(evaluation["ok"])
            self.assertTrue(
                any(check["category"] == "unresolved_placeholders" and not check["ok"] for check in evaluation["checks"])
            )
        finally:
            remove_tree(skill_dir)

    def test_static_site_renderer_has_search_ui(self) -> None:
        html = render_site_index(
            {
                "generated_at": "2026-05-02T00:00:00Z",
                "skills": [
                    {
                        "id": "demo-skill",
                        "name": "demo-skill",
                        "title": "Demo Skill",
                        "description": "Demo description.",
                        "short_description": "Demo description.",
                        "categories": ["Research"],
                        "tags": ["demo"],
                        "risk_level": "low",
                        "source": {"path": "skills/demo-skill"},
                        "source_catalog": {"id": "skillforge", "name": "SkillForge", "type": "local"},
                        "codex": {"global_install_command": "python -m skillforge install demo-skill --scope global"},
                    }
                ],
            }
        )
        self.assertIn('id="skill-search"', html)
        self.assertIn("search-index.json", html)
        self.assertIn('id="source-filter"', html)

    def test_load_metadata(self) -> None:
        metadata = load_skill_metadata("get-youtube-media")
        self.assertEqual(metadata["id"], "get-youtube-media")
        self.assertIn("global", metadata["codex"]["install_scopes"])
        self.assertIn("project", metadata["codex"]["install_scopes"])
        self.assertEqual(metadata["homepage_path"], "skills/get-youtube-media/README.md")

    def test_install_uses_overridden_global_scope(self) -> None:
        old_value = os.environ.get("SKILLFORGE_CODEX_SKILLS_DIR")
        os.environ["SKILLFORGE_CODEX_SKILLS_DIR"] = str(
            REPO_ROOT / "test-output" / f"codex-skills-{uuid.uuid4().hex}"
        )
        try:
            target = install_skill("project-retrospective", scope="global")
            self.assertTrue((target / "SKILL.md").exists())
            self.assertIn("codex-skills", target.as_posix())
            installed = list_installed("global")
            self.assertEqual(installed[0]["id"], "project-retrospective")
            removed = remove_installed_skill("project-retrospective", scope="global")
            self.assertEqual(removed, target)
            self.assertFalse(target.exists())
        finally:
            if old_value is None:
                os.environ.pop("SKILLFORGE_CODEX_SKILLS_DIR", None)
            else:
                os.environ["SKILLFORGE_CODEX_SKILLS_DIR"] = old_value

    def test_install_skillforge_is_idempotent_for_existing_install(self) -> None:
        unique = uuid.uuid4().hex
        codex_home = REPO_ROOT / "test-output" / f"codex-marketplace-home-{unique}"
        marketplace = codex_home / "plugins" / "cache" / MARKETPLACE_ID
        (marketplace / "skillforge").mkdir(parents=True, exist_ok=True)
        (marketplace / "plugins" / "agent-skills" / ".codex-plugin").mkdir(parents=True, exist_ok=True)
        (marketplace / "plugins" / "agent-skills" / "skills").mkdir(parents=True, exist_ok=True)
        (marketplace / "skillforge" / "cli.py").write_text("cli", encoding="utf-8")
        (marketplace / "plugins" / "agent-skills" / ".codex-plugin" / "plugin.json").write_text(
            json.dumps({"name": "agent-skills", "version": "0.1.5", "repository": MARKETPLACE_SOURCE}),
            encoding="utf-8",
        )
        (marketplace / "plugins" / "agent-skills" / "skills" / "skill_list.md").write_text("skills", encoding="utf-8")
        (marketplace / "README.md").write_text("SkillForge", encoding="utf-8")
        config = codex_home / "config.toml"
        config.write_text(
            "\n".join(
                [
                    f"[marketplaces.{MARKETPLACE_ID}]",
                    'source_type = "git"',
                    f'source = "{MARKETPLACE_SOURCE}"',
                    f'ref = "{MARKETPLACE_REF}"',
                    "",
                    f'[plugins."{PLUGIN_ID}"]',
                    "enabled = true",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        try:
            payload = install_skillforge_marketplace(codex_home=codex_home, marketplace_path=marketplace)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["status"], "healthy")
            self.assertFalse(payload["changed"])
            self.assertTrue(payload["marketplace"]["is_skillforge"])
            self.assertTrue(payload["config"]["plugin_enabled"])
            self.assertEqual(payload["version"]["source_repo"], MARKETPLACE_SOURCE)
            self.assertEqual(payload["version"]["configured_ref"], MARKETPLACE_REF)
            self.assertEqual(payload["version"]["plugin_version"], "0.1.5")
            self.assertEqual(payload["version"]["code_version"], "0.1.5")
            self.assertEqual(payload["version"]["last_updated_source"], "plugin_json_mtime")

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main(
                    [
                        "install-skillforge",
                        "--codex-home",
                        str(codex_home),
                        "--marketplace-path",
                        str(marketplace),
                        "--json",
                    ]
                )
            cli_payload = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(cli_payload["status"], "healthy")
            self.assertEqual(cli_payload["version"]["plugin_version"], "0.1.5")
        finally:
            remove_tree(codex_home)

    def test_install_skillforge_repairs_missing_config_entries(self) -> None:
        unique = uuid.uuid4().hex
        codex_home = REPO_ROOT / "test-output" / f"codex-repair-home-{unique}"
        marketplace = codex_home / "plugins" / "cache" / MARKETPLACE_ID
        (marketplace / "skillforge").mkdir(parents=True, exist_ok=True)
        (marketplace / "plugins" / "agent-skills" / ".codex-plugin").mkdir(parents=True, exist_ok=True)
        (marketplace / "plugins" / "agent-skills" / "skills").mkdir(parents=True, exist_ok=True)
        (marketplace / "skillforge" / "cli.py").write_text("cli", encoding="utf-8")
        (marketplace / "plugins" / "agent-skills" / ".codex-plugin" / "plugin.json").write_text(
            json.dumps({"name": "agent-skills", "version": "0.1.5", "repository": MARKETPLACE_SOURCE}),
            encoding="utf-8",
        )
        (marketplace / "plugins" / "agent-skills" / "skills" / "skill_list.md").write_text("skills", encoding="utf-8")
        (marketplace / "README.md").write_text("SkillForge", encoding="utf-8")
        try:
            dry_run = install_skillforge_marketplace(codex_home=codex_home, marketplace_path=marketplace)
            self.assertTrue(dry_run["ok"])
            self.assertEqual(dry_run["status"], "repair_available")
            self.assertFalse((codex_home / "config.toml").exists())

            repaired = install_skillforge_marketplace(codex_home=codex_home, marketplace_path=marketplace, yes=True)
            self.assertTrue(repaired["ok"])
            self.assertEqual(repaired["status"], "repaired")
            self.assertTrue(repaired["changed"])
            self.assertTrue(repaired["config"]["marketplace_registered"])
            self.assertTrue(repaired["config"]["plugin_enabled"])
            self.assertEqual(repaired["version"]["source_repo"], MARKETPLACE_SOURCE)
            self.assertEqual(repaired["version"]["plugin_version"], "0.1.5")
            config_text = (codex_home / "config.toml").read_text(encoding="utf-8")
            self.assertIn(f"[marketplaces.{MARKETPLACE_ID}]", config_text)
            self.assertIn(f'[plugins."{PLUGIN_ID}"]', config_text)
        finally:
            remove_tree(codex_home)

    def test_global_scope_honors_codex_home(self) -> None:
        old_codex_home = os.environ.get("CODEX_HOME")
        old_override = os.environ.get("SKILLFORGE_CODEX_SKILLS_DIR")
        codex_home = REPO_ROOT / "test-output" / f"codex-home-{uuid.uuid4().hex}"
        os.environ.pop("SKILLFORGE_CODEX_SKILLS_DIR", None)
        os.environ["CODEX_HOME"] = str(codex_home)
        try:
            self.assertEqual(default_global_codex_skills_dir(), codex_home / "skills")
        finally:
            if old_codex_home is None:
                os.environ.pop("CODEX_HOME", None)
            else:
                os.environ["CODEX_HOME"] = old_codex_home
            if old_override is None:
                os.environ.pop("SKILLFORGE_CODEX_SKILLS_DIR", None)
            else:
                os.environ["SKILLFORGE_CODEX_SKILLS_DIR"] = old_override

    def test_remove_tree_handles_readonly_files(self) -> None:
        target = REPO_ROOT / "test-output" / f"readonly-remove-{uuid.uuid4().hex}"
        target.mkdir(parents=True, exist_ok=True)
        file_path = target / "readonly.txt"
        file_path.write_text("readonly", encoding="utf-8")
        file_path.chmod(0o400)
        try:
            remove_tree(target)
            self.assertFalse(target.exists())
        finally:
            if file_path.exists():
                file_path.chmod(0o600)
            remove_tree(target)

    def test_skill_file_iteration_ignores_platform_artifacts(self) -> None:
        skill_dir = REPO_ROOT / "test-output" / f"artifact-skill-{uuid.uuid4().hex}"
        cache_dir = skill_dir / "__pycache__"
        cache_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(
            "\n".join(
                [
                    "---",
                    "name: artifact-skill",
                    "description: Verify ignored generated files.",
                    "---",
                    "",
                    "# Artifact Skill",
                ]
            ),
            encoding="utf-8",
        )
        (skill_dir / ".DS_Store").write_text("mac artifact", encoding="utf-8")
        (skill_dir / "Thumbs.db").write_bytes(b"windows artifact")
        (cache_dir / "skill.cpython-312.pyc").write_bytes(b"python cache")
        try:
            files = [path.relative_to(skill_dir).as_posix() for path in iter_skill_files(skill_dir)]
            self.assertEqual(files, ["SKILL.md"])
        finally:
            remove_tree(skill_dir)

    def test_copy_tree_ignores_platform_artifacts(self) -> None:
        source = REPO_ROOT / "test-output" / f"copy-source-{uuid.uuid4().hex}"
        target = REPO_ROOT / "test-output" / f"copy-target-{uuid.uuid4().hex}"
        (source / "__pycache__").mkdir(parents=True, exist_ok=True)
        (source / "SKILL.md").write_text("skill", encoding="utf-8")
        (source / ".DS_Store").write_text("mac artifact", encoding="utf-8")
        (source / "Thumbs.db").write_bytes(b"windows artifact")
        (source / "__pycache__" / "skill.cpython-312.pyc").write_bytes(b"python cache")
        try:
            copy_tree(source, target)
            self.assertTrue((target / "SKILL.md").exists())
            self.assertFalse((target / ".DS_Store").exists())
            self.assertFalse((target / "Thumbs.db").exists())
            self.assertFalse((target / "__pycache__").exists())
        finally:
            remove_tree(source)
            remove_tree(target)

    def test_validate_accepts_nested_frontmatter_metadata(self) -> None:
        skill_dir = REPO_ROOT / "test-output" / f"nested-frontmatter-{uuid.uuid4().hex}"
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(
            "\n".join(
                [
                    "---",
                    "name: nested-frontmatter",
                    "description: Verify nested metadata frontmatter parses.",
                    "metadata:",
                    "  author: test-author",
                    "  version: \"0.1.0\"",
                    "---",
                    "",
                    "# Nested Frontmatter",
                ]
            ),
            encoding="utf-8",
        )
        try:
            result = validate_skill(skill_dir)
            self.assertTrue(result.ok)
            self.assertEqual(result.metadata["metadata"]["author"], "test-author")
            self.assertEqual(result.metadata["metadata"]["version"], "0.1.0")
        finally:
            remove_tree(skill_dir)

    def test_validate_accepts_chomped_block_frontmatter_description(self) -> None:
        skill_dir = REPO_ROOT / "test-output" / f"block-frontmatter-{uuid.uuid4().hex}"
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(
            "\n".join(
                [
                    "---",
                    "name: block-frontmatter",
                    "description: >-",
                    "  Search peer catalogs and explain relevant skills.",
                    "  Use this when a user asks for workflow discovery.",
                    "---",
                    "",
                    "# Block Frontmatter",
                ]
            ),
            encoding="utf-8",
        )
        try:
            result = validate_skill(skill_dir)
            self.assertTrue(result.ok)
            self.assertEqual(
                result.metadata["description"],
                "Search peer catalogs and explain relevant skills. Use this when a user asks for workflow discovery.",
            )
        finally:
            remove_tree(skill_dir)

    def test_markdown_discovery_metadata_can_supplement_minimal_frontmatter(self) -> None:
        skill_dir = REPO_ROOT / "test-output" / f"markdown-discovery-{uuid.uuid4().hex}"
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(
            "\n".join(
                [
                    "---",
                    "name: markdown-discovery",
                    "description: Verify readable markdown discovery metadata.",
                    "---",
                    "",
                    "# Markdown Discovery",
                    "",
                    "## SkillForge Discovery Metadata",
                    "",
                    "### Title",
                    "",
                    "Readable Discovery Skill",
                    "",
                    "### Aliases",
                    "",
                    "- readable discovery",
                    "- markdown metadata",
                    "",
                    "### Tags",
                    "",
                    "- testing",
                    "- discovery",
                    "",
                    "### Use When",
                    "",
                    "- The user wants a readable SKILL.md body.",
                    "",
                    "### Risk Level",
                    "",
                    "low",
                ]
            ),
            encoding="utf-8",
        )
        try:
            validation = validate_skill(skill_dir)
            self.assertTrue(validation.ok)
            metadata = metadata_from_validation(validation, owner="test-owner", source_path=skill_dir)
            self.assertEqual(metadata["title"], "Readable Discovery Skill")
            self.assertEqual(metadata["aliases"], ["readable discovery", "markdown metadata"])
            self.assertEqual(metadata["tags"], ["discovery", "testing"])
            self.assertEqual(metadata["use_when"], ["The user wants a readable SKILL.md body."])
            self.assertEqual(metadata["risk_level"], "low")
        finally:
            remove_tree(skill_dir)

    def test_feedback_draft(self) -> None:
        draft = FeedbackDraft(
            skill_id="project-retrospective",
            trying="Keep a project memory log",
            happened="It created a log but missed the user's exact wording",
            outcome="Partially helped",
            suggestion="Add a required original-ask quote block.",
        )
        payload = draft.as_dict()
        self.assertIn("project-retrospective", payload["title"])
        self.assertIn("skill-feedback.yml", payload["issue_url"])
        self.assertIn("Keep a project memory log", payload["body"])
        self.assertEqual(payload["screen"][0]["label"], "Subject")

    def test_figure_evidence_cli_copies_only_allowed_images(self) -> None:
        root = REPO_ROOT / "test-output" / f"figure-evidence-{uuid.uuid4().hex}"
        manifest = root / "gliosis.figures.json"
        assets = root / "assets"
        image = root / "source.png"
        root.mkdir(parents=True, exist_ok=True)
        image.write_bytes(b"fake image bytes")
        try:
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main(
                    [
                        "figure-evidence",
                        "gliosis",
                        "--figure-id",
                        "gliosis-fig-001",
                        "--source-title",
                        "Teaching Source",
                        "--source-url",
                        "https://example.test/source",
                        "--figure-label",
                        "Figure 31",
                        "--license",
                        "CC BY 4.0",
                        "--reuse-status",
                        "ok-to-embed",
                        "--image-path",
                        str(image),
                        "--clinical-point",
                        "FLAIR-bright gliosis adjacent to encephalomalacia.",
                        "--section",
                        "Primary Imaging Modality",
                        "--manifest",
                        str(manifest),
                        "--assets-dir",
                        str(assets),
                        "--json",
                    ]
                )
            payload = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertTrue(payload["copied"])
            copied_path = Path(payload["asset_path"])
            if not copied_path.is_absolute():
                copied_path = REPO_ROOT / copied_path
            self.assertTrue(copied_path.exists())
            self.assertIn("![", payload["markdown_snippet"])

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main(
                    [
                        "figure-evidence",
                        "gliosis",
                        "--figure-id",
                        "gliosis-fig-002",
                        "--source-title",
                        "Copyrighted Teaching Source",
                        "--source-url",
                        "https://example.test/restricted",
                        "--figure-label",
                        "Figure 32",
                        "--license",
                        "Copyrighted; link only",
                        "--reuse-status",
                        "link-only",
                        "--image-path",
                        str(image),
                        "--clinical-point",
                        "Example requiring external source review.",
                        "--manifest",
                        str(manifest),
                        "--assets-dir",
                        str(assets),
                        "--json",
                    ]
                )
            payload = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertFalse(payload["copied"])
            self.assertIsNone(payload["entry"]["local_path"])
            self.assertTrue(payload["warnings"])
            manifest_payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(len(manifest_payload["figures"]), 2)
        finally:
            remove_tree(root)

    def test_source_archive_cli_records_url_only_and_download_cache(self) -> None:
        root = REPO_ROOT / "test-output" / f"source-archive-{uuid.uuid4().hex}"
        manifest = root / "gliosis.sources.json"
        cache_root = root / "cache"
        source_file = root / "source.html"
        root.mkdir(parents=True, exist_ok=True)
        source_file.write_text("<html><body>Authoritative source text.</body></html>", encoding="utf-8")
        try:
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main(
                    [
                        "source-archive",
                        "gliosis",
                        "--source-id",
                        "teaching-source",
                        "--title",
                        "Teaching Source",
                        "--url",
                        "https://example.test/source",
                        "--source-type",
                        "radiology teaching",
                        "--claim-breadth",
                        "broad",
                        "--section",
                        "What To Look For",
                        "--manifest",
                        str(manifest),
                        "--json",
                    ]
                )
            payload = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["entry"]["cache_status"], "url-only")
            self.assertIsNone(payload["entry"]["local_cache_path"])

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main(
                    [
                        "source-archive",
                        "gliosis",
                        "--source-id",
                        "local-source",
                        "--title",
                        "Local Source",
                        "--url",
                        source_file.resolve().as_uri(),
                        "--source-type",
                        "textbook chapter",
                        "--claim-breadth",
                        "broad",
                        "--section",
                        "Primary Imaging Modality",
                        "--manifest",
                        str(manifest),
                        "--cache-root",
                        str(cache_root),
                        "--download",
                        "--json",
                    ]
                )
            payload = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["entry"]["cache_status"], "cached-local-only")
            self.assertTrue(payload["entry"]["checksum_sha256"])
            cached_path = Path(payload["entry"]["local_cache_path"])
            if not cached_path.is_absolute():
                cached_path = REPO_ROOT / cached_path
            self.assertTrue(cached_path.exists())
            manifest_payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(len(manifest_payload["sources"]), 2)
        finally:
            remove_tree(root)

    def test_disease_preview_cli_renders_html_summary(self) -> None:
        root = REPO_ROOT / "test-output" / f"disease-preview-{uuid.uuid4().hex}"
        disease_dir = root / "diseases"
        output = root / "reports" / "gliosis.html"
        disease_dir.mkdir(parents=True, exist_ok=True)
        (disease_dir / "gliosis.md").write_text(
            "\n".join(
                [
                    "# Gliosis In The Brain",
                    "",
                    "## Goals",
                    "",
                    "1. Describe MRI appearance.",
                    "2. Support mimic-aware review.",
                    "",
                    "![Local figure](../assets/gliosis.png)",
                    "",
                    "| Field | Value |",
                    "| --- | --- |",
                    "| Modality | MRI |",
                    "",
                    "- first wrapped list item",
                    "  with continuation text",
                    "- second item",
                ]
            ),
            encoding="utf-8",
        )
        (disease_dir / "gliosis.sources.json").write_text(
            json.dumps({"sources": [{"id": "source-1", "cache_status": "url-only"}]}),
            encoding="utf-8",
        )
        (disease_dir / "gliosis.figures.json").write_text(
            json.dumps(
                {
                    "figures": [
                        {
                            "id": "figure-1",
                            "reuse_status": "ok-to-embed",
                            "local_path": "../assets/gliosis.png",
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        try:
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main(
                    [
                        "disease-preview",
                        "gliosis",
                        "--disease-dir",
                        str(disease_dir),
                        "--output",
                        str(output),
                        "--json",
                    ]
                )
            payload = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["sources_total"], 1)
            self.assertEqual(payload["figures_total"], 1)
            self.assertEqual(payload["local_figures"], 1)
            self.assertTrue(output.exists())
            html_text = output.read_text(encoding="utf-8")
            self.assertIn("<ol>", html_text)
            self.assertIn("<table>", html_text)
            self.assertIn("Sources recorded", html_text)
            self.assertIn("gliosis.png", html_text)
            self.assertIn('src="../assets/gliosis.png"', html_text)
            self.assertIn("first wrapped list item with continuation text", html_text)
            self.assertNotIn("<p>with continuation text</p>", html_text)
        finally:
            remove_tree(root)

    def test_disease_template_check_cli_passes_packaged_chapters(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(["disease-template-check", "--json"])
        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertTrue(payload["ok"])
        self.assertGreaterEqual(payload["checked"], 2)
        checked_diseases = {result["disease"] for result in payload["results"]}
        self.assertIn("cerebral-infarction", checked_diseases)
        self.assertIn("gliosis", checked_diseases)

    def test_disease_template_check_cli_reports_missing_required_sections(self) -> None:
        root = REPO_ROOT / "test-output" / f"disease-template-check-{uuid.uuid4().hex}"
        disease_dir = root / "diseases"
        disease_dir.mkdir(parents=True, exist_ok=True)
        (disease_dir / "incomplete.md").write_text(
            "# Incomplete\n\n## Goals\n\nDraft only.\n",
            encoding="utf-8",
        )
        (disease_dir / "incomplete.sources.json").write_text(json.dumps({"sources": []}), encoding="utf-8")
        (disease_dir / "incomplete.figures.json").write_text(json.dumps({"figures": []}), encoding="utf-8")
        try:
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main(
                    [
                        "disease-template-check",
                        "incomplete",
                        "--disease-dir",
                        str(disease_dir),
                        "--json",
                    ]
                )
            payload = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 1)
            self.assertFalse(payload["ok"])
            result = payload["results"][0]
            self.assertIn("Source Review Status", result["missing_required_sections"])
            failed = {check["category"] for check in result["checks"] if not check["ok"] and check["required"]}
            self.assertIn("template_headings", failed)
            self.assertIn("longitudinal_what_to_look_for", failed)
        finally:
            remove_tree(root)

    def test_feedback_cli_json(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "feedback",
                    "project-retrospective",
                    "--trying",
                    "Keep a project memory log",
                    "--happened",
                    "It created a log but missed the user's exact wording",
                    "--outcome",
                    "Partially helped",
                    "--suggestion",
                    "Add a required original-ask quote block.",
                    "--json",
                ]
            )
        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["fields"]["subject"], "project-retrospective")
        self.assertEqual(payload["fields"]["outcome"], "Partially helped")

    def test_contribution_draft_is_pr_first(self) -> None:
        draft = ContributionDraft(
            summary="clarify semantic search examples",
            change_type="docs",
            why="Help novice users understand what search does by default.",
            changed_files=["README.md"],
            checks=["python -m unittest tests.test_skillforge"],
            safety_notes="Docs-only change.",
            user_type="non-developer",
        )
        payload = draft.as_dict()
        self.assertEqual(payload["intent"], "pull_request")
        self.assertFalse(payload["direct_push_to_main"])
        self.assertEqual(payload["contributor_profile"], "non-developer")
        self.assertEqual(payload["branch"], "contrib/docs-clarify-semantic-search-examples")
        self.assertIn("README.md", payload["body"])
        self.assertIn("step by step", "\n".join(payload["next_steps"]))
        self.assertIn("gh pr create", "\n".join(payload["commands"]))

        skill_draft = ContributionDraft(
            summary="add a reusable workflow skill",
            change_type="skill",
            changed_files=["skills/example-skill/SKILL.md", "skills/example-skill/README.md"],
            user_type="developer",
        )
        skill_payload = skill_draft.as_dict()
        checklist = "\n".join(skill_payload["review_checklist"])
        self.assertIn("SKILL.md.tmpl", checklist)
        self.assertIn("README.md.tmpl", checklist)
        self.assertIn("build-catalog", checklist)
        self.assertIn("evaluate <skill-id>", checklist)
        self.assertIn("Review Checklist", skill_payload["body"])

    def test_contribution_cli_json(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "contribute",
                    "add a time management skill",
                    "--type",
                    "feature",
                    "--why",
                    "Users searched for Pomodoro help and found no dedicated workflow.",
                    "--changed",
                    "skills/pomodoro-focus-timer/SKILL.md",
                    "--check",
                    "python -m skillforge evaluate pomodoro-focus-timer --json",
                    "--safety-note",
                    "Skill is prompt-only and low risk.",
                    "--user-type",
                    "developer",
                    "--json",
                ]
            )
        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["fields"]["change_type"], "feature")
        self.assertEqual(payload["fields"]["user_type"], "developer")
        self.assertEqual(payload["intent"], "pull_request")
        self.assertIn("manual_pr_url", payload)

    def test_peer_search_cache_and_install_do_not_modify_catalog(self) -> None:
        unique = uuid.uuid4().hex
        fixture_root = REPO_ROOT / "test-output" / f"peer-source-{unique}"
        cache_dir = REPO_ROOT / "test-output" / f"peer-cache-{unique}"
        install_dir = REPO_ROOT / "test-output" / f"peer-install-{unique}"
        skill_dir = fixture_root / "skills" / "huggingface-datasets"
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(
            "\n".join(
                [
                    "---",
                    "name: huggingface-datasets",
                    "description: Explore Hugging Face datasets, splits, rows, filters, and parquet files.",
                    "---",
                    "",
                    "# Hugging Face Datasets",
                    "",
                    "Use for read-only Hugging Face Dataset Viewer work.",
                ]
            ),
            encoding="utf-8",
        )
        peers = [
            {
                "id": "fake-huggingface",
                "name": "Fake Hugging Face Skills",
                "publisher": "Hugging Face",
                "kind": "github_skill_repo",
                "source_url": str(fixture_root),
                "repo": "fake/huggingface-skills",
                "default_enabled": True,
                "reliability": "test",
            }
        ]
        catalog_before = (REPO_ROOT / "catalog" / "skills.json").read_text(encoding="utf-8")
        generic_payload = peer_search("skills", peers=peers, cache_dir=cache_dir)
        self.assertEqual(generic_payload["results"], [])

        search_payload = peer_search("hugging face datasets", peers=peers, cache_dir=cache_dir)
        self.assertEqual(search_payload["results"][0]["id"], "huggingface-datasets")
        self.assertEqual(search_payload["results"][0]["source_catalog"]["id"], "fake-huggingface")

        cached_payload = peer_search("hugging face datasets", peers=peers, cache_dir=cache_dir)
        self.assertEqual(cached_payload["cache"]["status"], "hit")
        cached_peer_payload = peer_search("rows parquet", peers=peers, cache_dir=cache_dir)
        self.assertEqual(cached_peer_payload["results"][0]["id"], "huggingface-datasets")

        old_install = os.environ.get("SKILLFORGE_CODEX_SKILLS_DIR")
        os.environ["SKILLFORGE_CODEX_SKILLS_DIR"] = str(install_dir)
        try:
            install_payload = install_peer_skill(
                "huggingface-datasets",
                peer_id="fake-huggingface",
                peers=peers,
                cache_dir=cache_dir,
                scope="global",
            )
            self.assertTrue((install_dir / "huggingface-datasets" / "SKILL.md").exists())
            self.assertEqual(install_payload["source_catalog"]["id"], "fake-huggingface")
        finally:
            if old_install is None:
                os.environ.pop("SKILLFORGE_CODEX_SKILLS_DIR", None)
            else:
                os.environ["SKILLFORGE_CODEX_SKILLS_DIR"] = old_install

        catalog_after = (REPO_ROOT / "catalog" / "skills.json").read_text(encoding="utf-8")
        self.assertEqual(catalog_before, catalog_after)
        listing = cache_listing(cache_dir=cache_dir)
        self.assertEqual(listing["peers"][0]["peer_id"], "fake-huggingface")
        remove_tree(fixture_root)
        remove_tree(cache_dir)
        remove_tree(install_dir)

    def test_peer_search_filters_weak_peer_results(self) -> None:
        unique = uuid.uuid4().hex
        fixture_root = REPO_ROOT / "test-output" / f"weak-peer-source-{unique}"
        cache_dir = REPO_ROOT / "test-output" / f"weak-peer-cache-{unique}"
        skill_dir = fixture_root / "skills" / "huggingface-trackio"
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(
            "\n".join(
                [
                    "---",
                    "name: huggingface-trackio",
                    "description: Track real-time ML training dashboards and experiment metrics.",
                    "---",
                    "",
                    "# Hugging Face Trackio",
                ]
            ),
            encoding="utf-8",
        )
        peers = [
            {
                "id": "time-management-catalog",
                "name": "Time Management Catalog",
                "publisher": "Test",
                "kind": "github_skill_repo",
                "source_url": str(fixture_root),
                "repo": "test/time-management-catalog",
                "default_enabled": True,
            }
        ]
        try:
            payload = peer_search("time management motivation", peers=peers, cache_dir=cache_dir)
            self.assertEqual(payload["results"], [])
        finally:
            remove_tree(fixture_root)
            remove_tree(cache_dir)

    def test_selected_peers_returns_all_enabled_peers(self) -> None:
        unique = uuid.uuid4().hex
        fixture_root = REPO_ROOT / "test-output" / f"all-enabled-peer-source-{unique}"
        cache_dir = REPO_ROOT / "test-output" / f"all-enabled-peer-cache-{unique}"
        (fixture_root / "skills").mkdir(parents=True, exist_ok=True)
        peers = [
            {
                "id": "supabase-agent-skills",
                "name": "Supabase Agent Skills",
                "publisher": "Supabase",
                "kind": "github_skill_repo",
                "source_url": str(fixture_root),
                "repo": "supabase/agent-skills",
                "default_enabled": True,
            },
            {
                "id": "disabled-aggregator",
                "name": "Disabled Aggregator",
                "publisher": "Test",
                "kind": "public_aggregator",
                "source_url": "https://example.com/",
                "default_enabled": False,
            }
        ]
        try:
            selected = selected_peers("time management motivation", peers=peers, cache_dir=cache_dir)
            self.assertEqual([peer["id"] for peer in selected], ["supabase-agent-skills"])
        finally:
            remove_tree(fixture_root)
            remove_tree(cache_dir)

    def test_peer_search_reports_disabled_peers(self) -> None:
        unique = uuid.uuid4().hex
        fixture_root = REPO_ROOT / "test-output" / f"disabled-peer-source-{unique}"
        cache_dir = REPO_ROOT / "test-output" / f"disabled-peer-cache-{unique}"
        (fixture_root / "skills").mkdir(parents=True, exist_ok=True)
        peers = [
            {
                "id": "enabled-empty-peer",
                "name": "Enabled Empty Peer",
                "publisher": "Test",
                "kind": "github_skill_repo",
                "source_url": str(fixture_root),
                "default_enabled": True,
            },
            {
                "id": "disabled-peer",
                "name": "Disabled Peer",
                "publisher": "Test",
                "kind": "github_skill_repo",
                "source_url": str(fixture_root),
                "default_enabled": False,
            },
        ]
        try:
            payload = peer_search("sql", peers=peers, cache_dir=cache_dir)
            statuses = {status["peer_id"]: status["status"] for status in payload["peer_statuses"]}
            self.assertEqual(statuses["enabled-empty-peer"], "no_match")
            self.assertEqual(statuses["disabled-peer"], "disabled")
        finally:
            remove_tree(fixture_root)
            remove_tree(cache_dir)

    def test_peer_search_jobs_are_capped_at_fifteen(self) -> None:
        self.assertEqual(peer_search_jobs(99, 20), 15)
        self.assertEqual(peer_search_jobs(0, 20), 1)
        self.assertEqual(peer_search_jobs(None, 2), 2)
        self.assertEqual(peer_search_jobs(15, 0), 0)

    def test_peer_search_ignores_old_cache_payloads(self) -> None:
        unique = uuid.uuid4().hex
        cache_dir = REPO_ROOT / "test-output" / f"old-search-cache-{unique}"
        query = f"time management motivation {unique}"
        cache_path = search_cache_path(query, peer_id=None, cache_dir=cache_dir)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(
            json.dumps(
                {
                    "query": query,
                    "results": [{"id": "stale-false-positive"}],
                    "errors": [],
                    "generated_at": "2026-05-02T00:00:00Z",
                }
            ),
            encoding="utf-8",
        )
        try:
            payload = peer_search(query, peers=[], cache_dir=cache_dir)
            self.assertEqual(payload["cache"]["status"], "miss")
            self.assertEqual(payload["results"], [])
        finally:
            remove_tree(cache_dir)

    def test_peer_search_cache_applies_requested_limit(self) -> None:
        unique = uuid.uuid4().hex
        fixture_root = REPO_ROOT / "test-output" / f"limit-peer-source-{unique}"
        cache_dir = REPO_ROOT / "test-output" / f"limit-peer-cache-{unique}"
        for skill_id, database in [("postgres-access", "Postgres"), ("sqlite-access", "SQLite")]:
            skill_dir = fixture_root / "skills" / skill_id
            skill_dir.mkdir(parents=True, exist_ok=True)
            (skill_dir / "SKILL.md").write_text(
                "\n".join(
                    [
                        "---",
                        f"name: {skill_id}",
                        f"description: Database access helper for {database} SQL workflows.",
                        "---",
                        "",
                        f"# {skill_id}",
                    ]
                ),
                encoding="utf-8",
            )
        peers = [
            {
                "id": "database-access-catalog",
                "name": "Database Access Catalog",
                "publisher": "Test",
                "kind": "github_skill_repo",
                "source_url": str(fixture_root),
                "repo": "test/database-access-catalog",
                "default_enabled": True,
            }
        ]
        try:
            first = peer_search("database access", peers=peers, cache_dir=cache_dir, limit=1)
            self.assertEqual(first["cache"]["status"], "miss")
            self.assertEqual(len(first["results"]), 1)

            second = peer_search("database access", peers=peers, cache_dir=cache_dir, limit=10)
            self.assertEqual(second["cache"]["status"], "hit")
            self.assertEqual(len(second["results"]), 2)
        finally:
            remove_tree(fixture_root)
            remove_tree(cache_dir)

    def test_peer_search_finds_supabase_database_access_skill(self) -> None:
        unique = uuid.uuid4().hex
        fixture_root = REPO_ROOT / "test-output" / f"supabase-peer-source-{unique}"
        cache_dir = REPO_ROOT / "test-output" / f"supabase-peer-cache-{unique}"
        skill_dir = fixture_root / "skills" / "supabase"
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(
            "\n".join(
                [
                    "---",
                    "name: supabase",
                    "description: \"Use when doing ANY task involving Supabase Database, SQL, MCP server, schema changes, migrations, and Postgres access.\"",
                    "metadata:",
                    "  author: supabase",
                    "  version: \"0.1.2\"",
                    "---",
                    "",
                    "# Supabase",
                ]
            ),
            encoding="utf-8",
        )
        peers = [
            {
                "id": "supabase-agent-skills",
                "name": "Supabase Agent Skills",
                "publisher": "Supabase",
                "kind": "github_skill_repo",
                "source_url": str(fixture_root),
                "repo": "supabase/agent-skills",
                "default_enabled": True,
            }
        ]
        try:
            payload = peer_search("access databases", peers=peers, cache_dir=cache_dir)
            self.assertEqual(payload["results"][0]["id"], "supabase")
            self.assertEqual(payload["peer_statuses"][0]["status"], "matched")
        finally:
            remove_tree(fixture_root)
            remove_tree(cache_dir)

    def test_peer_error_classification(self) -> None:
        network = classify_peer_error("fatal: unable to access 'https://github.com/example/repo': Failed to connect to github.com port 443: Could not connect to server")
        self.assertEqual(network["kind"], "network_blocked")

        path_length = classify_peer_error("error: unable to create file deeply/nested/file.md: Filename too long")
        self.assertEqual(path_length["kind"], "path_too_long")
        self.assertIn("platform", path_length)

    def test_static_peer_catalog_search_and_diagnostics(self) -> None:
        unique = uuid.uuid4().hex
        fixture_root = REPO_ROOT / "test-output" / f"static-peer-{unique}"
        cache_dir = REPO_ROOT / "test-output" / f"static-cache-{unique}"
        fixture_root.mkdir(parents=True, exist_ok=True)
        catalog_path = fixture_root / "skills.json"
        catalog_path.write_text(
            json.dumps(
                {
                    "schema_version": "0.1",
                    "generated_at": "2026-05-02T00:00:00Z",
                    "skills": [
                        {
                            "id": "static-huggingface-helper",
                            "name": "static-huggingface-helper",
                            "title": "Static Hugging Face Helper",
                            "description": "Find Hugging Face datasets and model workflow skills.",
                            "source": {"path": "skills/static-huggingface-helper"},
                            "checksum": {"algorithm": "sha256-tree", "value": "abc123"},
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        peers = [
            {
                "id": "fake-static-hf",
                "name": "Fake Static Hugging Face Catalog",
                "publisher": "Test",
                "kind": "static_catalog",
                "adapter": "static-catalog",
                "catalog_url": catalog_path.resolve().as_uri(),
                "default_enabled": True,
                "trust_notes": "Test catalog only.",
                "supported_formats": ["skills.json"],
            },
            {
                "id": "fake-static-hf",
                "name": "Duplicate Fake Static Catalog",
                "publisher": "Test",
                "kind": "static_catalog",
                "adapter": "static-catalog",
                "catalog_url": str(catalog_path),
                "default_enabled": False,
            },
        ]
        try:
            payload = peer_search("hugging face datasets", peers=peers[:1], cache_dir=cache_dir)
            self.assertEqual(payload["results"][0]["id"], "static-huggingface-helper")
            self.assertEqual(payload["results"][0]["source_catalog"]["id"], "fake-static-hf")
            self.assertEqual(payload["results"][0]["source"]["cache_status"], "local")

            diagnostics = peer_diagnostics(peers=peers, cache_dir=cache_dir)
            self.assertFalse(diagnostics["ok"])
            self.assertEqual(diagnostics["duplicate_peer_ids"], ["fake-static-hf"])
            self.assertIn("trust_notes", diagnostics["peers"][0])
        finally:
            remove_tree(fixture_root)
            remove_tree(cache_dir)

    def test_static_peer_catalog_accepts_aggregator_list_payload(self) -> None:
        unique = uuid.uuid4().hex
        fixture_root = REPO_ROOT / "test-output" / f"static-list-peer-{unique}"
        cache_dir = REPO_ROOT / "test-output" / f"static-list-cache-{unique}"
        fixture_root.mkdir(parents=True, exist_ok=True)
        catalog_path = fixture_root / "skills-data.json"
        catalog_path.write_text(
            json.dumps(
                [
                    {
                        "name": "sql-review",
                        "summary": "Review SQL code for access control, injection risk, and maintainability.",
                        "repo": "example/sql-skills",
                        "url": "https://github.com/example/sql-skills/blob/main/skills/sql-review/SKILL.md",
                        "category": ["security", "database"],
                        "tags": ["sql"],
                    }
                ]
            ),
            encoding="utf-8",
        )
        peers = [
            {
                "id": "fake-aggregator",
                "name": "Fake Aggregator",
                "publisher": "Test",
                "kind": "static_catalog",
                "adapter": "static-catalog",
                "catalog_url": catalog_path.resolve().as_uri(),
                "default_enabled": True,
            }
        ]
        try:
            payload = peer_search("SQL access", peers=peers, cache_dir=cache_dir)
            self.assertEqual(payload["results"][0]["id"], "sql-review")
            self.assertEqual(payload["results"][0]["source"]["repo"], "example/sql-skills")
            self.assertEqual(payload["results"][0]["source_catalog"]["id"], "fake-aggregator")
            self.assertEqual(payload["results"][0]["summary"], "Review SQL code for access control, injection risk, and maintainability.")
            self.assertEqual(payload["results"][0]["short_description"], "Review SQL code for access control, injection risk, and maintainability.")
            self.assertTrue(payload["results"][0]["expanded_description"])
        finally:
            remove_tree(fixture_root)
            remove_tree(cache_dir)

    def test_cache_peer_catalogs_writes_full_provider_json(self) -> None:
        unique = uuid.uuid4().hex
        fixture_root = REPO_ROOT / "test-output" / f"provider-catalog-{unique}"
        static_root = REPO_ROOT / "test-output" / f"provider-static-{unique}"
        cache_dir = REPO_ROOT / "test-output" / f"provider-cache-{unique}"
        skill_dir = fixture_root / "skills" / "repo-sql-helper"
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(
            "\n".join(
                [
                    "---",
                    "name: repo-sql-helper",
                    "description: Help inspect SQL database schemas and queries.",
                    "tags:",
                    "  - sql",
                    "  - database",
                    "---",
                    "",
                    "# Repo SQL Helper",
                    "",
                    "Use for SQL database inspection.",
                ]
            ),
            encoding="utf-8",
        )
        static_root.mkdir(parents=True, exist_ok=True)
        static_catalog = static_root / "skills.json"
        static_catalog.write_text(
            json.dumps(
                {
                    "skills": [
                        {
                            "id": "static-coaching",
                            "description": "Help with coaching, motivation, and planning.",
                            "tags": ["coaching", "motivation"],
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        peers = [
            {
                "id": "repo-provider",
                "name": "Repo Provider",
                "kind": "github_skill_repo",
                "source_url": str(fixture_root),
                "repo": "test/repo-provider",
                "default_enabled": True,
            },
            {
                "id": "static-provider",
                "name": "Static Provider",
                "kind": "static_catalog",
                "adapter": "static-catalog",
                "catalog_url": static_catalog.resolve().as_uri(),
                "default_enabled": True,
            },
        ]
        try:
            payload = cache_peer_catalogs(peers=peers, cache_dir=cache_dir, ttl_hours=24)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["provider_count"], 2)
            statuses = {provider["peer_id"]: provider["status"] for provider in payload["providers"]}
            self.assertIn(statuses["repo-provider"], {"miss", "refresh"})
            self.assertIn(statuses["static-provider"], {"local", "miss", "refresh"})

            repo_cache = peer_catalog_cache_path(peers[0], cache_dir=cache_dir)
            static_cache = peer_catalog_cache_path(peers[1], cache_dir=cache_dir)
            self.assertTrue(repo_cache.exists())
            self.assertTrue(static_cache.exists())

            repo_payload = json.loads(repo_cache.read_text(encoding="utf-8"))
            static_payload = json.loads(static_cache.read_text(encoding="utf-8"))
            self.assertEqual(repo_payload["skills"][0]["id"], "repo-sql-helper")
            self.assertIn("Use for SQL database inspection.", repo_payload["skills"][0]["skill_text"])
            self.assertEqual(static_payload["skills"][0]["id"], "static-coaching")
            self.assertTrue((cache_dir / "catalogs" / "static-provider" / "raw.json").exists())

            cached = cache_peer_catalogs(peers=peers, cache_dir=cache_dir, ttl_hours=24)
            cached_statuses = {provider["peer_id"]: provider["status"] for provider in cached["providers"]}
            self.assertEqual(cached_statuses["repo-provider"], "hit")
            self.assertEqual(cached_statuses["static-provider"], "hit")
        finally:
            remove_tree(fixture_root)
            remove_tree(static_root)
            remove_tree(cache_dir)

    def test_corpus_search_returns_install_next_steps(self) -> None:
        unique = uuid.uuid4().hex
        fixture_root = REPO_ROOT / "test-output" / f"corpus-source-{unique}"
        static_root = REPO_ROOT / "test-output" / f"corpus-static-{unique}"
        cache_dir = REPO_ROOT / "test-output" / f"corpus-cache-{unique}"
        skill_dir = fixture_root / "skills" / "time-planner"
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(
            "\n".join(
                [
                    "---",
                    "name: time-planner",
                    "description: Help with time management, daily planning, priorities, focus, and task scheduling.",
                    "tags:",
                    "  - time-management",
                    "  - productivity",
                    "---",
                    "",
                    "# Time Planner",
                    "",
                    "Use for time management and prioritizing tasks.",
                ]
            ),
            encoding="utf-8",
        )
        static_root.mkdir(parents=True, exist_ok=True)
        static_catalog = static_root / "skills.json"
        static_catalog.write_text(
            json.dumps(
                {
                    "skills": [
                        {
                            "id": "time-planner",
                            "description": "Detailed time management planner for daily priorities, focus, scheduling, and productivity.",
                            "repo": "test/time-provider",
                            "url": "https://github.com/test/time-provider/blob/main/skills/time-planner/SKILL.md",
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        peers = [
            {
                "id": "time-provider",
                "name": "Time Provider",
                "kind": "github_skill_repo",
                "source_url": str(fixture_root),
                "repo": "test/time-provider",
                "default_enabled": True,
            },
            {
                "id": "time-static-provider",
                "name": "Time Static Provider",
                "kind": "static_catalog",
                "adapter": "static-catalog",
                "catalog_url": static_catalog.resolve().as_uri(),
                "default_enabled": True,
            }
        ]
        try:
            payload = corpus_search("time management", peers=peers, cache_dir=cache_dir)
            self.assertEqual(payload["results"][0]["id"], "time-planner")
            self.assertTrue(payload["results"][0]["installable"])
            self.assertEqual(
                payload["results"][0]["install_command"],
                "python -m skillforge install time-planner --peer time-provider --scope global --yes",
            )
            self.assertIn("Review source", payload["results"][0]["next_step"])
        finally:
            remove_tree(fixture_root)
            remove_tree(static_root)
            remove_tree(cache_dir)

    def test_corpus_search_cli_default_table(self) -> None:
        unique = uuid.uuid4().hex
        fixture_root = REPO_ROOT / "test-output" / f"corpus-cli-{unique}"
        cache_dir = REPO_ROOT / "test-output" / f"corpus-cli-cache-{unique}"
        skill_dir = fixture_root / "skills" / "daily-planning"
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(
            "\n".join(
                [
                    "---",
                    "name: daily-planning",
                    "description: Help with daily planning, time management, priorities, and task scheduling.",
                    "---",
                    "",
                    "# Daily Planning",
                    "",
                    "## Requirements",
                    "",
                    "- Ask before changing calendar or task data.",
                ]
            ),
            encoding="utf-8",
        )
        peer_catalog_file = fixture_root / "peer-catalogs.json"
        peer_catalog_file.write_text(
            json.dumps(
                {
                    "peers": [
                        {
                            "id": "daily-provider",
                            "name": "Daily Provider",
                            "kind": "github_skill_repo",
                            "source_url": str(fixture_root),
                            "repo": "test/daily-provider",
                            "default_enabled": True,
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        old_cache_dir = os.environ.get("SKILLFORGE_CACHE_DIR")
        old_peer_catalog = os.environ.get("SKILLFORGE_PEER_CATALOGS")
        os.environ["SKILLFORGE_CACHE_DIR"] = str(cache_dir)
        os.environ["SKILLFORGE_PEER_CATALOGS"] = str(peer_catalog_file)
        try:
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main(["corpus-search", "time management"])
            output = stdout.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("| Rank | Skill Name | Helps With | Comments | Install Command | Source URL |", output)
            self.assertIn("daily-planning", output)
            self.assertIn("Ask before changing calendar or task data.", output)
            self.assertIn("python -m skillforge install daily-planning --peer daily-provider --scope global --yes", output)
        finally:
            if old_cache_dir is None:
                os.environ.pop("SKILLFORGE_CACHE_DIR", None)
            else:
                os.environ["SKILLFORGE_CACHE_DIR"] = old_cache_dir
            if old_peer_catalog is None:
                os.environ.pop("SKILLFORGE_PEER_CATALOGS", None)
            else:
                os.environ["SKILLFORGE_PEER_CATALOGS"] = old_peer_catalog
            remove_tree(fixture_root)
            remove_tree(cache_dir)

    def test_search_table_comments_use_before_you_start_section(self) -> None:
        unique = uuid.uuid4().hex
        fixture_root = REPO_ROOT / "test-output" / f"before-start-cli-{unique}"
        cache_dir = REPO_ROOT / "test-output" / f"before-start-cache-{unique}"
        skill_dir = fixture_root / "skills" / "briefing-writer"
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(
            "\n".join(
                [
                    "---",
                    "name: briefing-writer",
                    "description: Generate status briefings from configured sources.",
                    "---",
                    "",
                    "# Briefing Writer",
                    "",
                    "Generate audience-specific briefings.",
                    "",
                    "## Before You Start",
                    "",
                    "Look for the briefing config before drafting.",
                    "",
                    "If the config file does not exist, ask the user to run setup first.",
                ]
            ),
            encoding="utf-8",
        )
        peer_catalog_file = fixture_root / "peer-catalogs.json"
        peer_catalog_file.write_text(
            json.dumps(
                {
                    "peers": [
                        {
                            "id": "briefing-provider",
                            "name": "Briefing Provider",
                            "kind": "github_skill_repo",
                            "source_url": str(fixture_root),
                            "repo": "test/briefing-provider",
                            "default_enabled": True,
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        old_cache_dir = os.environ.get("SKILLFORGE_CACHE_DIR")
        old_peer_catalog = os.environ.get("SKILLFORGE_PEER_CATALOGS")
        os.environ["SKILLFORGE_CACHE_DIR"] = str(cache_dir)
        os.environ["SKILLFORGE_PEER_CATALOGS"] = str(peer_catalog_file)
        try:
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main(["corpus-search", "briefings"])
            output = stdout.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("Look for the briefing config before drafting.", output)
        finally:
            if old_cache_dir is None:
                os.environ.pop("SKILLFORGE_CACHE_DIR", None)
            else:
                os.environ["SKILLFORGE_CACHE_DIR"] = old_cache_dir
            if old_peer_catalog is None:
                os.environ.pop("SKILLFORGE_PEER_CATALOGS", None)
            else:
                os.environ["SKILLFORGE_PEER_CATALOGS"] = old_peer_catalog
            remove_tree(fixture_root)
            remove_tree(cache_dir)

    def test_cache_catalogs_cli_json(self) -> None:
        unique = uuid.uuid4().hex
        fixture_root = REPO_ROOT / "test-output" / f"provider-cli-{unique}"
        cache_dir = REPO_ROOT / "test-output" / f"provider-cli-cache-{unique}"
        catalog_path = fixture_root / "skills.json"
        fixture_root.mkdir(parents=True, exist_ok=True)
        catalog_path.write_text(
            json.dumps({"skills": [{"id": "cli-cached-skill", "description": "CLI cached skill."}]}),
            encoding="utf-8",
        )
        peers = [
            {
                "id": "cli-static-provider",
                "name": "CLI Static Provider",
                "kind": "static_catalog",
                "adapter": "static-catalog",
                "catalog_url": catalog_path.resolve().as_uri(),
                "default_enabled": True,
            }
        ]
        old_cache_dir = os.environ.get("SKILLFORGE_CACHE_DIR")
        old_peer_catalog = os.environ.get("SKILLFORGE_PEER_CATALOGS")
        peer_catalog_file = fixture_root / "peer-catalogs.json"
        peer_catalog_file.write_text(json.dumps({"peers": peers}), encoding="utf-8")
        os.environ["SKILLFORGE_CACHE_DIR"] = str(cache_dir)
        os.environ["SKILLFORGE_PEER_CATALOGS"] = str(peer_catalog_file)
        try:
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main(["cache", "catalogs", "--json"])
            payload = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["providers"][0]["peer_id"], "cli-static-provider")

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main(["cache", "list", "--json"])
            listing = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(len(listing["provider_catalog_files"]), 1)
        finally:
            if old_cache_dir is None:
                os.environ.pop("SKILLFORGE_CACHE_DIR", None)
            else:
                os.environ["SKILLFORGE_CACHE_DIR"] = old_cache_dir
            if old_peer_catalog is None:
                os.environ.pop("SKILLFORGE_PEER_CATALOGS", None)
            else:
                os.environ["SKILLFORGE_PEER_CATALOGS"] = old_peer_catalog
            remove_tree(fixture_root)
            remove_tree(cache_dir)


if __name__ == "__main__":
    unittest.main()
