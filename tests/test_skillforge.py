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
    search_audit_skill,
    search_catalog,
)
from skillforge.cli import main
from skillforge.feedback import FeedbackDraft
from skillforge.install import install_skill, list_installed, remove_installed_skill
from skillforge.peer import cache_listing, install_peer_skill, peer_search
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


if __name__ == "__main__":
    unittest.main()
