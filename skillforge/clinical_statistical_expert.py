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


def packaged_template_dir() -> Path:
    return REPO_ROOT / "skills" / "clinical-statistical-expert" / "references" / "templates"


def implementation_template_dir() -> Path:
    return REPO_ROOT / "skillforge" / "templates" / "clinical-statistical-expert"


def default_template_dir() -> Path:
    packaged = packaged_template_dir()
    if packaged.exists():
        return packaged
    return implementation_template_dir()


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


def canonical_heading(value: str) -> str:
    text = re.sub(r"`([^`]+)`", r"\1", value)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[^a-z0-9]+", " ", text.lower())
    return " ".join(text.split())


def markdown_headings(markdown: str) -> list[dict[str, Any]]:
    headings: list[dict[str, Any]] = []
    for line_number, line in enumerate(markdown.splitlines(), start=1):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if not match:
            continue
        text = match.group(2).strip()
        headings.append(
            {
                "level": len(match.group(1)),
                "text": text,
                "canonical": canonical_heading(text),
                "line": line_number,
            }
        )
    return headings


def headings_from_file(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return markdown_headings(path.read_text(encoding="utf-8-sig"))


def has_heading(headings: list[dict[str, Any]], expected: str) -> bool:
    canonical = canonical_heading(expected)
    return any(heading["canonical"] == canonical for heading in headings)


def has_any_heading(headings: list[dict[str, Any]], options: list[str]) -> bool:
    return any(has_heading(headings, option) for option in options)


def section_headings(
    headings: list[dict[str, Any]],
    *,
    start: str,
    end: str,
    minimum_level: int = 3,
) -> list[dict[str, Any]]:
    start_key = canonical_heading(start)
    end_key = canonical_heading(end)
    in_section = False
    collected: list[dict[str, Any]] = []
    for heading in headings:
        if heading["canonical"] == start_key:
            in_section = True
            continue
        if in_section and heading["canonical"] == end_key:
            break
        if in_section and heading["level"] >= minimum_level:
            collected.append(heading)
    return collected


def chapter_markdown_files(disease_root: Path) -> list[Path]:
    if not disease_root.exists():
        return []
    files: list[Path] = []
    for path in sorted(disease_root.glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        if "." in path.stem:
            continue
        files.append(path)
    return files


def validate_json_manifest(path: Path, key: str) -> tuple[bool, str, dict[str, Any] | None]:
    if not path.exists():
        return False, "missing", None
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        return False, f"invalid JSON: {exc}", None
    if not isinstance(payload, dict):
        return False, "manifest root must be an object", payload
    value = payload.get(key)
    if not isinstance(value, list):
        return False, f"manifest must contain a list named {key}", payload
    return True, f"{len(value)} {key} recorded", payload


def local_figure_path_status(disease_root: Path, figure_payload: dict[str, Any] | None) -> tuple[bool, str]:
    if not figure_payload:
        return False, "figure manifest unavailable"
    missing: list[str] = []
    checked = 0
    for figure in figure_payload.get("figures", []):
        if not isinstance(figure, dict):
            continue
        local_path = figure.get("local_path")
        if not local_path:
            continue
        checked += 1
        local_path_text = str(local_path)
        target = (disease_root / local_path_text).resolve()
        repo_target = (REPO_ROOT / local_path_text).resolve()
        if not target.exists() and not repo_target.exists():
            missing.append(str(local_path))
    if missing:
        return False, f"missing local figure assets: {', '.join(missing[:5])}"
    return True, f"{checked} local figure paths checked"


DISEASE_TEMPLATE_SECTION_GROUPS: list[tuple[str, list[str]]] = [
    ("Goals", ["Goals"]),
    ("Source Review Status", ["Source Review Status"]),
    ("Figure Evidence", ["Figure Evidence"]),
    ("Common Names And Aliases", ["Common Names And Aliases"]),
    ("Scope", ["Scope"]),
    ("Clinical Context", ["Clinical Context"]),
    ("Known-Diagnosis Review Frame", ["Known-Diagnosis Review Frame"]),
    ("What To Look For", ["What To Look For"]),
    ("Primary Imaging Modality", ["Primary Imaging Modality"]),
    ("Other Modalities And When They Matter", ["Other Modalities And When They Matter"]),
    ("Locations And Structural Appearance", ["Locations And Structural Appearance"]),
    ("Typical Appearance", ["Typical Appearance"]),
    ("Atypical Or Red-Flag Appearance", ["Atypical Or Red-Flag Appearance"]),
    ("Differential Diagnosis And Mimics", ["Differential Diagnosis And Mimics"]),
    ("Quick Differential Diagnosis Guide", ["Quick Differential Diagnosis Guide"]),
    ("Key Imaging Discriminators", ["Key Imaging Discriminators"]),
    ("Differential Diagnosis Matrix", ["Differential Diagnosis Matrix"]),
    ("Similar-Presentation Diseases And Mimic-Aware Comparison", ["Similar-Presentation Diseases And Mimic-Aware Comparison"]),
    (
        "Report Language That Supports Or Argues Against Each Diagnosis",
        ["Report Language That Supports Or Argues Against Each Diagnosis"],
    ),
    ("When Additional Imaging Or Clinical Context Helps", ["When Additional Imaging Or Clinical Context Helps"]),
    ("Natural History And Clinical Course", ["Natural History And Clinical Course"]),
    ("Treatment, Response, And Outcome Context", ["Treatment, Response, And Outcome Context"]),
    ("Guideline-Based Management Context", ["Guideline-Based Management Context"]),
    ("Common Treatment Pathways", ["Common Treatment Pathways"]),
    ("Imaging Appearance After Treatment", ["Imaging Appearance After Treatment"]),
    ("Evidence Of Treatment Response", ["Evidence Of Treatment Response"]),
    (
        "Evidence Of Progression, Recurrence, Or Treatment Failure",
        ["Evidence Of Progression, Recurrence, Or Treatment Failure"],
    ),
    ("Expected Outcomes And Prognostic Factors", ["Expected Outcomes And Prognostic Factors"]),
    ("Statistical Implications Of Treatment And Progression", ["Statistical Implications Of Treatment And Progression"]),
    ("Evidence Of Active Disease, Progression, Or Recurrence", ["Evidence Of Active Disease, Progression, Or Recurrence"]),
    ("Stable Or Chronic Residual Findings", ["Stable Or Chronic Residual Findings"]),
    ("Improvement, Treatment Response, Or Resolution", ["Improvement, Treatment Response, Or Resolution"]),
    ("Serial Imaging Assessment And Interval Change", ["Serial Imaging Assessment And Interval Change"]),
    ("Clinical Endpoints", ["Clinical Endpoints"]),
    ("Imaging, Biomarker, And Measurement Endpoints", ["Imaging, Biomarker, And Measurement Endpoints"]),
    ("Common Covariates And Confounders", ["Common Covariates And Confounders"]),
    ("Clinical Covariates", ["Clinical Covariates"]),
    ("Imaging Covariates", ["Imaging Covariates"]),
    ("Treatment And Temporal Confounders", ["Treatment And Temporal Confounders"]),
    ("Acquisition And Protocol Confounders", ["Acquisition And Protocol Confounders"]),
    ("Research Design Implications", ["Research Design Implications"]),
    ("Statistical Implications", ["Statistical Implications"]),
    ("Missing Information To Ask For", ["Missing Information To Ask For"]),
    ("Claim Boundaries", ["Safety And Claim Boundaries", "Expert Use And Claim Boundaries"]),
    ("Related Disease Files", ["Related Disease Files"]),
    ("Related Statistical Method Files", ["Related Statistical Method Files"]),
    ("Authoritative Sources", ["Authoritative Sources"]),
    ("Notes For Skill Authors", ["Notes For Skill Authors"]),
]


def disease_template_check(
    disease: str | None = None,
    *,
    disease_dir: str | Path | None = None,
    template_dir: str | Path | None = None,
    strict: bool = False,
) -> dict[str, Any]:
    disease_root = Path(disease_dir) if disease_dir else packaged_disease_dir()
    if disease_dir is None and not disease_root.exists():
        disease_root = default_disease_dir()
    template_root = Path(template_dir) if template_dir else default_template_dir()
    disease_template = template_root / "disease.md.tmpl"
    template_headings = headings_from_file(disease_template)
    expected_template_headings = [
        heading["text"]
        for heading in template_headings
        if heading["level"] in {2, 3} and not str(heading["text"]).strip().startswith("{{")
    ]
    expected_files = [
        "disease.md.tmpl",
        "disease-research-plan.md.tmpl",
        "disease-review-criteria.md.tmpl",
        "disease-figure-evidence.md.tmpl",
        "disease.sources.schema.json",
        "disease.figures.schema.json",
    ]
    template_missing = [name for name in expected_files if not (template_root / name).exists()]

    if disease:
        markdown_files = [disease_root / f"{slug_text(disease)}.md"]
    else:
        markdown_files = chapter_markdown_files(disease_root)

    results: list[dict[str, Any]] = []
    for markdown_path in markdown_files:
        slug = markdown_path.stem
        checks: list[dict[str, Any]] = []

        def add_check(category: str, ok: bool, message: str, *, required: bool = True) -> None:
            checks.append(
                {
                    "category": category,
                    "ok": ok,
                    "required": required,
                    "message": message,
                }
            )

        if not markdown_path.exists():
            add_check("chapter_exists", False, f"missing disease chapter {repo_relative(markdown_path)}")
            results.append(
                {
                    "disease": slug,
                    "ok": False,
                    "markdown_path": repo_relative(markdown_path),
                    "checks": checks,
                    "missing_required_sections": [],
                    "strict_missing_sections": [],
                }
            )
            continue

        markdown = markdown_path.read_text(encoding="utf-8-sig")
        headings = markdown_headings(markdown)
        missing_required = [
            label
            for label, options in DISEASE_TEMPLATE_SECTION_GROUPS
            if not has_any_heading(headings, options)
        ]
        add_check(
            "template_headings",
            not missing_required,
            "required conceptual headings present"
            if not missing_required
            else f"missing required conceptual headings: {', '.join(missing_required)}",
        )

        longitudinal_headings = section_headings(headings, start="What To Look For", end="Primary Imaging Modality")
        add_check(
            "longitudinal_what_to_look_for",
            len(longitudinal_headings) >= 4,
            f"{len(longitudinal_headings)} longitudinal or report-language subsections found between What To Look For and Primary Imaging Modality",
        )

        strict_missing = [
            expected
            for expected in expected_template_headings
            if not has_heading(headings, expected)
        ]
        add_check(
            "strict_template_heading_match",
            not strict_missing,
            "all template headings match exactly"
            if not strict_missing
            else f"missing exact template headings: {', '.join(strict_missing)}",
            required=strict,
        )

        source_ok, source_message, _source_payload = validate_json_manifest(
            disease_root / f"{slug}.sources.json",
            "sources",
        )
        add_check("source_manifest", source_ok, source_message)

        figure_ok, figure_message, figure_payload = validate_json_manifest(
            disease_root / f"{slug}.figures.json",
            "figures",
        )
        add_check("figure_manifest", figure_ok, figure_message)

        local_figure_ok, local_figure_message = local_figure_path_status(disease_root, figure_payload)
        add_check("local_figure_paths", local_figure_ok, local_figure_message, required=False)

        supporting_artifacts = [
            disease_root / f"{slug}.research-plan.md",
            disease_root / f"{slug}.research-plan.backtest.md",
            disease_root / f"{slug}.source-review.md",
            disease_root / f"{slug}.review.md",
            disease_root / f"{slug}.build-retrospective.md",
        ]
        present_artifacts = [repo_relative(path) for path in supporting_artifacts if path.exists()]
        add_check(
            "supporting_artifacts",
            bool(present_artifacts),
            f"{len(present_artifacts)} supporting artifacts found",
            required=False,
        )

        add_check(
            "template_directory",
            not template_missing,
            "clinical-statistical-expert templates are packaged with the skill"
            if not template_missing
            else f"missing packaged templates: {', '.join(template_missing)}",
        )

        required_ok = all(check["ok"] for check in checks if check["required"])
        results.append(
            {
                "disease": slug,
                "ok": required_ok,
                "markdown_path": repo_relative(markdown_path),
                "checks": checks,
                "missing_required_sections": missing_required,
                "strict_missing_sections": strict_missing,
                "supporting_artifacts": present_artifacts,
            }
        )

    return {
        "ok": bool(results) and all(result["ok"] for result in results),
        "strict": strict,
        "checked": len(results),
        "disease_dir": repo_relative(disease_root),
        "template_dir": repo_relative(template_root),
        "template_path": repo_relative(disease_template),
        "template_missing_files": template_missing,
        "results": results,
    }
