from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import tomllib
import unittest
import uuid

from skillforge.catalog import (
    PLUGIN_SKILLS_DIR,
    REPO_ROOT,
    build_catalog,
    evaluate_skill,
    load_skill_metadata,
    read_search_index,
    render_site_index,
    search_audit_skill,
    search_catalog,
)
from skillforge.cli import main
from skillforge.feedback import FeedbackDraft
from skillforge.filesystem import copy_tree, remove_tree
from skillforge.install import default_global_codex_skills_dir, install_skill, list_installed, remove_installed_skill
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
from skillforge.update import update_check, whats_new
from skillforge.validate import iter_skill_files, validate_skill


class SkillForgeTests(unittest.TestCase):
    def test_validate_pilot_skill(self) -> None:
        result = validate_skill(REPO_ROOT / "skills" / "project-retrospective")
        self.assertTrue(result.ok)
        self.assertEqual(result.metadata["name"], "project-retrospective")

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

    def test_help_and_getting_started_cli_json(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(["help", "search", "--json"])
        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["topic"], "search")
        self.assertTrue(any("corpus-search" in command["command"] for command in payload["commands"]))

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(["getting-started", "--json"])
        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["topic"], "getting-started")
        self.assertTrue(any("doctor" in step["command"] for step in payload["steps"]))

    def test_chattiness_coach_adds_search_next_steps(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(["search", "youtube", "--chattiness", "coach"])
        self.assertEqual(exit_code, 0)
        output = stdout.getvalue()
        self.assertIn("Next steps:", output)
        self.assertIn("python -m skillforge info", output)

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
            git(["add", "README.md"], repo)
            git(["-c", "user.name=SkillForge Test", "-c", "user.email=test@example.com", "commit", "-m", "Improve docs"], repo)
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
            self.assertTrue(any("Improve docs" in commit["summary"] for commit in changes["commits"]))
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
