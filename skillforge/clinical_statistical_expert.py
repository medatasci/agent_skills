from __future__ import annotations

from datetime import datetime, timezone
import html
import json
import os
from pathlib import Path
import re
from typing import Any

from .catalog import REPO_ROOT


def slug_text(value: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return text or "disease"


def repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def default_disease_dir() -> Path:
    return REPO_ROOT / "docs" / "clinical-statistical-expert" / "diseases"


def packaged_disease_dir() -> Path:
    return REPO_ROOT / "skills" / "clinical-statistical-expert" / "references" / "diseases"


def default_report_dir() -> Path:
    return REPO_ROOT / "docs" / "clinical-statistical-expert" / "reports"


def load_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8-sig"))


def resolve_markdown_reference(reference: str, *, markdown_dir: Path, output_dir: Path) -> str:
    if re.match(r"^[a-z]+://|^#", reference):
        return reference
    target = (markdown_dir / reference).resolve()
    try:
        return Path(os.path.relpath(target, output_dir.resolve())).as_posix()
    except ValueError:
        try:
            return target.relative_to(REPO_ROOT.resolve()).as_posix()
        except ValueError:
            return target.as_posix()


def linkify_inline(text: str, *, markdown_dir: Path, output_dir: Path) -> str:
    token = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)|(?<!!)\[([^\]]+)\]\(([^)]+)\)|`([^`]+)`")
    rendered: list[str] = []
    cursor = 0
    for match in token.finditer(text):
        rendered.append(html.escape(text[cursor : match.start()]))
        if match.group(1) is not None:
            alt = html.escape(match.group(1), quote=True)
            src = resolve_markdown_reference(match.group(2).strip(), markdown_dir=markdown_dir, output_dir=output_dir)
            rendered.append(f'<img src="{html.escape(src, quote=True)}" alt="{alt}" loading="lazy">')
        elif match.group(3) is not None:
            label = html.escape(match.group(3))
            href = resolve_markdown_reference(match.group(4).strip(), markdown_dir=markdown_dir, output_dir=output_dir)
            rendered.append(f'<a href="{html.escape(href, quote=True)}">{label}</a>')
        else:
            rendered.append(f"<code>{html.escape(match.group(5))}</code>")
        cursor = match.end()
    rendered.append(html.escape(text[cursor:]))
    return "".join(rendered)


def render_table(lines: list[str], *, markdown_dir: Path, output_dir: Path) -> str:
    rows = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in lines]
    if len(rows) < 2:
        return ""
    header = rows[0]
    body = rows[2:] if re.match(r"^[\s|:-]+$", lines[1]) else rows[1:]
    head_html = "".join(f"<th>{linkify_inline(cell, markdown_dir=markdown_dir, output_dir=output_dir)}</th>" for cell in header)
    body_rows = []
    for row in body:
        cells = "".join(f"<td>{linkify_inline(cell, markdown_dir=markdown_dir, output_dir=output_dir)}</td>" for cell in row)
        body_rows.append(f"<tr>{cells}</tr>")
    return f"<table><thead><tr>{head_html}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"


def markdown_to_html(markdown: str, *, markdown_dir: Path, output_dir: Path) -> str:
    blocks: list[str] = []
    paragraph: list[str] = []
    unordered_items: list[str] = []
    ordered_items: list[str] = []
    table_lines: list[str] = []
    code_lines: list[str] = []
    in_code_block = False

    def flush_paragraph() -> None:
        if paragraph:
            text = " ".join(line.strip() for line in paragraph).strip()
            blocks.append(f"<p>{linkify_inline(text, markdown_dir=markdown_dir, output_dir=output_dir)}</p>")
            paragraph.clear()

    def flush_list() -> None:
        if unordered_items:
            blocks.append("<ul>" + "".join(unordered_items) + "</ul>")
            unordered_items.clear()
        if ordered_items:
            blocks.append("<ol>" + "".join(ordered_items) + "</ol>")
            ordered_items.clear()

    def flush_table() -> None:
        if table_lines:
            rendered = render_table(table_lines, markdown_dir=markdown_dir, output_dir=output_dir)
            if rendered:
                blocks.append(rendered)
            table_lines.clear()

    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            flush_paragraph()
            flush_list()
            flush_table()
            if in_code_block:
                blocks.append(f"<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>")
                code_lines.clear()
                in_code_block = False
            else:
                in_code_block = True
            continue
        if in_code_block:
            code_lines.append(line)
            continue
        if not stripped:
            flush_paragraph()
            flush_list()
            flush_table()
            continue
        is_list_continuation = (
            bool(unordered_items or ordered_items)
            and (line.startswith("  ") or line.startswith("\t"))
            and not re.match(r"^\s*(- |\d+\.\s+|#{1,6}\s+|\|)", line)
            and not stripped.startswith("![")
        )
        if is_list_continuation:
            continuation = linkify_inline(stripped, markdown_dir=markdown_dir, output_dir=output_dir)
            if unordered_items:
                unordered_items[-1] = unordered_items[-1].removesuffix("</li>") + f" {continuation}</li>"
            elif ordered_items:
                ordered_items[-1] = ordered_items[-1].removesuffix("</li>") + f" {continuation}</li>"
            continue
        if stripped.startswith("|") and stripped.endswith("|"):
            flush_paragraph()
            flush_list()
            table_lines.append(stripped)
            continue
        flush_table()
        heading = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading:
            flush_paragraph()
            flush_list()
            level = min(len(heading.group(1)), 4)
            text = linkify_inline(heading.group(2), markdown_dir=markdown_dir, output_dir=output_dir)
            blocks.append(f"<h{level}>{text}</h{level}>")
            continue
        if stripped.startswith("- "):
            flush_paragraph()
            item = stripped[2:].strip()
            unordered_items.append(f"<li>{linkify_inline(item, markdown_dir=markdown_dir, output_dir=output_dir)}</li>")
            continue
        numbered = re.match(r"^\d+\.\s+(.+)$", stripped)
        if numbered:
            flush_paragraph()
            item = numbered.group(1).strip()
            ordered_items.append(f"<li>{linkify_inline(item, markdown_dir=markdown_dir, output_dir=output_dir)}</li>")
            continue
        if stripped.startswith("!["):
            flush_paragraph()
            flush_list()
            blocks.append(linkify_inline(stripped, markdown_dir=markdown_dir, output_dir=output_dir))
            continue
        paragraph.append(stripped)

    flush_paragraph()
    flush_list()
    flush_table()
    if in_code_block:
        blocks.append(f"<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>")
    return "\n".join(blocks)


def evidence_summary(disease: str, disease_dir: Path) -> dict[str, Any]:
    slug = slug_text(disease)
    source_manifest = load_json(disease_dir / f"{slug}.sources.json", {"sources": []})
    figure_manifest = load_json(disease_dir / f"{slug}.figures.json", {"figures": []})
    sources = source_manifest.get("sources", [])
    figures = figure_manifest.get("figures", [])
    source_status = {}
    for source in sources:
        status = source.get("cache_status") or "unknown"
        source_status[status] = source_status.get(status, 0) + 1
    figure_status = {}
    for figure in figures:
        status = figure.get("reuse_status") or "unknown"
        figure_status[status] = figure_status.get(status, 0) + 1
    return {
        "sources_total": len(sources),
        "source_status": source_status,
        "figures_total": len(figures),
        "figure_status": figure_status,
        "local_figures": len([figure for figure in figures if figure.get("local_path")]),
        "source_manifest": source_manifest,
        "figure_manifest": figure_manifest,
    }


def render_status_cards(summary: dict[str, Any]) -> str:
    source_items = "".join(
        f"<li>{html.escape(status)}: {count}</li>"
        for status, count in sorted(summary["source_status"].items())
    )
    figure_items = "".join(
        f"<li>{html.escape(status)}: {count}</li>"
        for status, count in sorted(summary["figure_status"].items())
    )
    return f"""
<section class="cards">
  <article><strong>{summary['sources_total']}</strong><span>Sources recorded</span><ul>{source_items}</ul></article>
  <article><strong>{summary['figures_total']}</strong><span>Image candidates</span><ul>{figure_items}</ul></article>
  <article><strong>{summary['local_figures']}</strong><span>Local embeddable figures</span><p>Other figures remain link-only until reuse is reviewed.</p></article>
</section>
"""


def disease_preview(
    disease: str,
    *,
    disease_dir: str | Path | None = None,
    output: str | Path | None = None,
) -> dict[str, Any]:
    slug = slug_text(disease)
    disease_root = Path(disease_dir) if disease_dir else default_disease_dir()
    markdown_path = disease_root / f"{slug}.md"
    if disease_dir is None and not markdown_path.exists():
        fallback_root = packaged_disease_dir()
        fallback_path = fallback_root / f"{slug}.md"
        if fallback_path.exists():
            disease_root = fallback_root
            markdown_path = fallback_path
    if not markdown_path.exists():
        raise FileNotFoundError(f"Disease chapter not found: {markdown_path}")
    output_path = Path(output) if output else default_report_dir() / f"{slug}.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    markdown = markdown_path.read_text(encoding="utf-8")
    summary = evidence_summary(slug, disease_root)
    body = markdown_to_html(markdown, markdown_dir=markdown_path.parent, output_dir=output_path.parent)
    cards = render_status_cards(summary)
    generated = datetime.now(timezone.utc).isoformat()
    title = f"{slug.replace('-', ' ').title()} Disease Chapter Preview"
    page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; line-height: 1.55; margin: 0; color: #1f2933; background: #f7f8fa; }}
    header {{ background: #102033; color: white; padding: 32px max(24px, calc((100vw - 1120px) / 2)); }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px; background: white; overflow-x: auto; }}
    h1, h2, h3 {{ line-height: 1.2; }}
    a {{ color: #0b5cab; }}
    img {{ max-width: 100%; height: auto; border: 1px solid #d7dde5; margin: 12px 0; }}
    table {{ width: 100%; min-width: 760px; border-collapse: collapse; margin: 16px 0; font-size: 0.94rem; }}
    th, td {{ border: 1px solid #d7dde5; padding: 8px; vertical-align: top; }}
    th {{ background: #edf2f7; text-align: left; }}
    code {{ background: #eef2f6; padding: 1px 4px; border-radius: 3px; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin: 20px 0; }}
    .cards article {{ border: 1px solid #d7dde5; border-radius: 6px; padding: 16px; background: #fbfcfd; }}
    .cards strong {{ display: block; font-size: 2rem; color: #102033; }}
    .cards span {{ font-weight: 700; }}
  </style>
</head>
<body>
  <header>
    <h1>{html.escape(title)}</h1>
    <p>Generated {html.escape(generated)} from {html.escape(repo_relative(markdown_path))}.</p>
  </header>
  <main>
{cards}
{body}
  </main>
</body>
</html>
"""
    output_path.write_text(page, encoding="utf-8")
    return {
        "ok": True,
        "disease": slug,
        "output_path": repo_relative(output_path),
        "markdown_path": repo_relative(markdown_path),
        "sources_total": summary["sources_total"],
        "figures_total": summary["figures_total"],
        "local_figures": summary["local_figures"],
    }
