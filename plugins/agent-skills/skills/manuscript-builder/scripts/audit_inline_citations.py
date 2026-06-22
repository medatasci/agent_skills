#!/usr/bin/env python3
"""Audit inline citations in project_publication.html.

This is a lightweight guard for manuscript-builder. It does not replace human
reference review; it flags likely literature prose without visible inline
bracket citations.
"""

from __future__ import annotations

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

CITATION_RE = re.compile(r"\[(?:\d+(?:\s*[-,;]\s*\d+)*|citation needed:[^\]]+|[A-Za-z][A-Za-z0-9_:\-]+)\]")
LITERATURE_RE = re.compile(
    r"\b(et al\.|study|studies|paper|reported|found|showed|demonstrated|"
    r"concluded|literature|prior work|related work|trial|readers?|radiologists?|"
    r"accuracy|AUC|sensitivity|specificity|memorization|privacy|benchmark|"
    r"dataset|model card|repository|arXiv|journal|conference)\b",
    re.IGNORECASE,
)
STAT_RE = re.compile(r"\b\d+(?:\.\d+)?\s*(?:%|percent|readers?|cases?|images?|volumes?|patients?|studies?)\b", re.IGNORECASE)
DEFAULT_SECTIONS = {"background", "discussion"}


class SectionTextParser(HTMLParser):
    def __init__(self, wanted_sections: set[str]):
        super().__init__()
        self.wanted_sections = wanted_sections
        self.section_stack: list[str | None] = []
        self.current_block: list[str] = []
        self.current_tag: str | None = None
        self.blocks: list[tuple[str, str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        attrs_dict = dict(attrs)
        if tag == "section":
            self.section_stack.append(attrs_dict.get("id"))
        if tag in {"p", "li", "td", "caption"} and self._in_wanted_section():
            self.current_tag = tag
            self.current_block = []

    def handle_endtag(self, tag: str):
        if tag == "section" and self.section_stack:
            self.section_stack.pop()
        if self.current_tag == tag:
            text = " ".join(" ".join(self.current_block).split())
            if text:
                self.blocks.append((self.section_stack[-1] if self.section_stack else "", tag, text))
            self.current_tag = None
            self.current_block = []

    def handle_data(self, data: str):
        if self.current_tag:
            self.current_block.append(data)

    def _in_wanted_section(self) -> bool:
        return bool(self.section_stack and self.section_stack[-1] in self.wanted_sections)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit inline citations in manuscript HTML.")
    parser.add_argument("--html", default="project_publication.html", help="HTML manuscript path")
    parser.add_argument(
        "--sections",
        nargs="*",
        default=sorted(DEFAULT_SECTIONS),
        help="Section ids to audit, default: background discussion",
    )
    parser.add_argument("--min-words", type=int, default=12, help="Minimum block length to audit")
    args = parser.parse_args()

    html_path = Path(args.html)
    if not html_path.exists():
        print(f"ERROR: HTML file not found: {html_path}", file=sys.stderr)
        return 2

    audit = SectionTextParser(set(args.sections))
    audit.feed(html_path.read_text(encoding="utf-8"))

    warnings: list[str] = []
    cited_blocks = 0
    checked_blocks = 0
    for section, tag, text in audit.blocks:
        words = re.findall(r"\b\w+\b", text)
        if len(words) < args.min_words:
            continue
        needs_citation = LITERATURE_RE.search(text) or STAT_RE.search(text)
        has_citation = CITATION_RE.search(text)
        if has_citation:
            cited_blocks += 1
        if needs_citation:
            checked_blocks += 1
            if not has_citation:
                excerpt = text[:180] + ("..." if len(text) > 180 else "")
                warnings.append(f"{section} <{tag}> lacks inline bracket citation: {excerpt}")

    print(f"Audited {len(audit.blocks)} text blocks in sections: {', '.join(args.sections)}")
    print(f"Blocks needing citations: {checked_blocks}; blocks with bracket citations: {cited_blocks}")
    if warnings:
        print("\nCitation warnings:")
        for warning in warnings:
            print(f"- {warning}")
        return 1
    print("No likely uncited literature blocks found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
