from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import unittest
import uuid

from skillforge.catalog import (
    REPO_ROOT,
    evaluate_skill,
    load_skill_metadata,
    read_search_index,
    render_site_index,
    search_audit_skill,
    search_catalog,
)
from skillforge.cli import main
from skillforge.feedback import FeedbackDraft
from skillforge.install import install_skill, list_installed, remove_installed_skill
from skillforge.peer import cache_listing, install_peer_skill, peer_diagnostics, peer_search
from skillforge.validate import validate_skill


class SkillForgeTests(unittest.TestCase):
    def test_validate_pilot_skill(self) -> None:
        result = validate_skill(REPO_ROOT / "skills" / "project-retrospective")
        self.assertTrue(result.ok)
        self.assertEqual(result.metadata["name"], "project-retrospective")

    def test_search_finds_youtube_skill(self) -> None:
        results = search_catalog("youtube transcripts research")
        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "get-youtube-media")

    def test_search_uses_discovery_metadata(self) -> None:
        results = search_catalog("after action review")
        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "project-retrospective")

        index = read_search_index()
        self.assertIn("aliases", index["fields_indexed"])
        self.assertIn("homepage_text", index["fields_indexed"])
        self.assertIn("search_text", index["skills"][0])
        self.assertIn("homepage_path", index["skills"][0])

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

    def test_evaluate_cli_json(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(["evaluate", "huggingface-datasets", "--json"])
        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["skill_id"], "huggingface-datasets")

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
            shutil.rmtree(skill_dir, ignore_errors=True)

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
        shutil.rmtree(fixture_root, ignore_errors=True)
        shutil.rmtree(cache_dir, ignore_errors=True)
        shutil.rmtree(install_dir, ignore_errors=True)

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
                "catalog_url": str(catalog_path),
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
            shutil.rmtree(fixture_root, ignore_errors=True)
            shutil.rmtree(cache_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
