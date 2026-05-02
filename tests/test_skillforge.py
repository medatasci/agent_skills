from __future__ import annotations

import contextlib
import io
import json
import os
import unittest
import uuid

from skillforge.catalog import REPO_ROOT, load_skill_metadata, search_catalog
from skillforge.cli import main
from skillforge.feedback import FeedbackDraft
from skillforge.install import install_skill, list_installed, remove_installed_skill
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

    def test_load_metadata(self) -> None:
        metadata = load_skill_metadata("get-youtube-media")
        self.assertEqual(metadata["id"], "get-youtube-media")
        self.assertIn("global", metadata["codex"]["install_scopes"])
        self.assertIn("project", metadata["codex"]["install_scopes"])

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


if __name__ == "__main__":
    unittest.main()
