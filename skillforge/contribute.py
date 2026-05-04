from __future__ import annotations

from dataclasses import dataclass, field
import re
from urllib.parse import quote


REPO_PULLS_URL = "https://github.com/medatasci/agent_skills/pulls"
REPO_COMPARE_URL = "https://github.com/medatasci/agent_skills/compare"
DEFAULT_BASE_BRANCH = "main"
DEFAULT_CHECKS = [
    "python -m unittest tests.test_skillforge",
    "python -m skillforge build-catalog",
]


def clean_text(value: str | None) -> str:
    return " ".join((value or "").split())


def slugify(value: str, *, max_length: int = 56) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    slug = re.sub(r"-{2,}", "-", slug)
    if not slug:
        slug = "skillforge-contribution"
    return slug[:max_length].rstrip("-")


def shell_quote(value: str) -> str:
    return '"' + value.replace('"', '\\"') + '"'


def type_label(change_type: str) -> str:
    labels = {
        "bugfix": "Bugfix",
        "feature": "Feature",
        "docs": "Docs",
        "skill": "Skill",
        "catalog": "Catalog",
        "improvement": "Improvement",
    }
    return labels.get(change_type, "Improvement")


@dataclass
class ContributionDraft:
    summary: str
    change_type: str = "improvement"
    why: str | None = None
    changed_files: list[str] = field(default_factory=list)
    checks: list[str] = field(default_factory=list)
    safety_notes: str | None = None
    user_type: str = "unknown"
    title: str | None = None
    branch: str | None = None
    base: str = DEFAULT_BASE_BRANCH

    def pr_title(self) -> str:
        if self.title:
            return clean_text(self.title)
        summary = clean_text(self.summary)
        label = type_label(self.change_type)
        if summary.lower().startswith(label.lower() + ":"):
            return summary
        return f"{label}: {summary}"

    def branch_name(self) -> str:
        if self.branch:
            return clean_text(self.branch).replace(" ", "-")
        return f"contrib/{slugify(self.change_type)}-{slugify(self.summary)}"

    def check_list(self) -> list[str]:
        checks = [clean_text(item) for item in self.checks if clean_text(item)]
        return checks or list(DEFAULT_CHECKS)

    def file_list(self) -> list[str]:
        return [clean_text(item) for item in self.changed_files if clean_text(item)]

    def body(self) -> str:
        files = self.file_list()
        checks = self.check_list()
        safety = clean_text(self.safety_notes) or (
            "No secrets, private data, or unsafe side effects are intentionally included."
        )
        why = clean_text(self.why) or "Describe the user problem or workflow this pull request improves."
        file_lines = [f"- `{item}`" for item in files] if files else ["- To be filled in after local edits are complete."]
        check_lines = [f"- [ ] `{item}`" for item in checks]
        return "\n".join(
            [
                "## Summary",
                clean_text(self.summary),
                "",
                "## Change Type",
                type_label(self.change_type),
                "",
                "## Why",
                why,
                "",
                "## Changed Files",
                *file_lines,
                "",
                "## Checks",
                *check_lines,
                "",
                "## Safety And Privacy",
                safety,
                "",
                "## Review Notes",
                "- This is intended to be reviewed as a pull request.",
                "- Do not push this change directly to `main` unless you are acting as a maintainer.",
            ]
        )

    def commands(self) -> list[str]:
        branch = self.branch_name()
        title = self.pr_title()
        files = self.file_list()
        add_target = " ".join(files) if files else "<changed-files>"
        return [
            f"git checkout -b {branch}",
            f"git add {add_target}",
            f"git commit -m {shell_quote(title)}",
            f"git push -u origin {branch}",
            f"gh pr create --base {self.base} --head {branch} --title {shell_quote(title)} --body-file pr-body.md",
        ]

    def manual_pr_url(self) -> str:
        return f"{REPO_COMPARE_URL}/{quote(self.base)}...{quote(self.branch_name(), safe='')}?quick_pull=1"

    def promptable_request(self) -> str:
        return "\n".join(
            [
                "Please help me submit this SkillForge contribution as a pull request.",
                "",
                f"Contributor profile: {self.user_type}",
                f"Change type: {type_label(self.change_type)}",
                f"Summary: {clean_text(self.summary)}",
                "",
                "Please keep the change on a branch, run the relevant checks, draft the PR body,",
                "and do not push directly to main.",
            ]
        )

    def next_steps(self) -> list[str]:
        if self.user_type == "non-developer":
            return [
                "Ask Codex to handle the branch, checks, commit, and pull request mechanics step by step.",
                "Review the PR title and body for accuracy before submitting.",
                "Do not run direct Git commands unless you understand and approve their side effects.",
            ]
        if self.user_type == "developer":
            return [
                "Review the generated branch name, PR body, and checks.",
                "Run the suggested Git commands only after confirming the working tree contains the intended changes.",
                "Open a pull request for review instead of pushing directly to main.",
            ]
        return [
            "Decide whether this is feedback only or a concrete change for a pull request.",
            "If the contributor is not comfortable with Git, ask Codex to handle the PR mechanics step by step.",
            "If the contributor is comfortable with Git, use the suggested commands after reviewing local changes.",
        ]

    def as_dict(self) -> dict:
        return {
            "intent": "pull_request",
            "title": self.pr_title(),
            "branch": self.branch_name(),
            "base": self.base,
            "contributor_profile": self.user_type,
            "pull_requests_url": REPO_PULLS_URL,
            "manual_pr_url": self.manual_pr_url(),
            "body": self.body(),
            "promptable_request": self.promptable_request(),
            "commands": self.commands(),
            "direct_push_to_main": False,
            "side_effects": "Read-only. Drafts a pull request plan and text; does not run git, push, or create a PR.",
            "next_steps": self.next_steps(),
            "fields": {
                "summary": clean_text(self.summary),
                "change_type": self.change_type,
                "user_type": self.user_type,
                "why": clean_text(self.why),
                "changed_files": self.file_list(),
                "checks": self.check_list(),
                "safety_notes": clean_text(self.safety_notes),
            },
            "review_checklist": [
                "Confirm the branch is not main.",
                "Review changed files for secrets, private data, and unintended generated-file churn.",
                "Run relevant tests and SkillForge evaluation commands.",
                "Open a pull request for maintainer review.",
            ],
        }
