from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlencode


REPO_ISSUES_URL = "https://github.com/medatasci/agent_skills/issues/new"
FEEDBACK_TEMPLATE = "skill-feedback.yml"


@dataclass
class FeedbackDraft:
    skill_id: str
    trying: str
    happened: str
    outcome: str
    suggestion: str | None = None
    title: str | None = None

    def issue_title(self) -> str:
        if self.title:
            return self.title
        summary = " ".join(self.happened.split())
        if len(summary) > 72:
            summary = summary[:69].rstrip() + "..."
        return f"[Feedback] {self.skill_id}: {summary}"

    def issue_url(self) -> str:
        query = urlencode({"template": FEEDBACK_TEMPLATE, "title": self.issue_title()})
        return f"{REPO_ISSUES_URL}?{query}"

    def body(self) -> str:
        suggestion = self.suggestion or "N/A"
        return "\n".join(
            [
                "## Skill",
                self.skill_id,
                "",
                "## What were you trying to do?",
                self.trying,
                "",
                "## What happened?",
                self.happened,
                "",
                "## Outcome",
                self.outcome,
                "",
                "## Suggested improvement",
                suggestion,
            ]
        )

    def screen(self) -> list[dict[str, str]]:
        return [
            {"label": "Skill", "value": self.skill_id},
            {"label": "What were you trying to do?", "value": self.trying},
            {"label": "What happened?", "value": self.happened},
            {"label": "Outcome", "value": self.outcome},
            {"label": "Suggested improvement", "value": self.suggestion or "N/A"},
        ]

    def as_dict(self) -> dict:
        return {
            "skill_id": self.skill_id,
            "title": self.issue_title(),
            "issue_url": self.issue_url(),
            "body": self.body(),
            "screen": self.screen(),
            "fields": {
                "skill": self.skill_id,
                "goal": self.trying,
                "result": self.happened,
                "outcome": self.outcome,
                "suggestion": self.suggestion or "",
            },
        }
