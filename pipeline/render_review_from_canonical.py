#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any, Literal

from pipeline.corpus_layout import CORPUS_DIR, canonical_path, review_draft_path
from pipeline.runtime_paths import ENGINE_ROOT

DOCS_DIR = CORPUS_DIR
REVIEW_DRAFTS_DIR = DOCS_DIR / "review_drafts"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a markdown review draft from canonical.json.")
    parser.add_argument("paper_id", help=f"Paper directory id under the configured corpus ({CORPUS_DIR}).")
    return parser.parse_args()


def output_path(paper_id: str) -> Path:
    return review_draft_path(paper_id)


def _span_text(
    span: dict[str, Any],
    math_map: dict[str, dict[str, Any]],
    reference_map: dict[str, dict[str, Any]],
    *,
    inline_math_mode: Literal["rendered", "plain"] = "rendered",
) -> str:
    kind = span.get("kind")
    if kind == "text":
        return str(span.get("text", ""))
    if kind == "inline_math_ref":
        math_entry = math_map.get(str(span.get("target_id")), {})
        latex = str(math_entry.get("display_latex", "")).strip()
        if not latex:
            return ""
        if inline_math_mode == "plain":
            return latex
        return f"\\({latex}\\)"
    if kind == "citation_ref":
        reference = reference_map.get(str(span.get("target_id")), {})
        return f"[{reference.get('id', span.get('target_id', 'ref'))}]"
    return ""


def _paragraph_text(
    spans: list[dict[str, Any]],
    math_map: dict[str, dict[str, Any]],
    reference_map: dict[str, dict[str, Any]],
    *,
    inline_math_mode: Literal["rendered", "plain"] = "rendered",
) -> str:
    return "".join(
        _span_text(
            span,
            math_map,
            reference_map,
            inline_math_mode=inline_math_mode,
        )
        for span in spans
    ).strip()


def _display_latex_blocks(math_entry: dict[str, Any]) -> list[str]:
    latex_blocks: list[str] = []
    if str(math_entry.get("kind", "")) == "group":
        latex_blocks.extend(
            str(item.get("display_latex", "")).strip()
            for item in math_entry.get("items", [])
            if str(item.get("display_latex", "")).strip()
        )
    if not latex_blocks:
        latex = str(math_entry.get("display_latex", "")).strip()
        if latex:
            latex_blocks.append(latex)
    return latex_blocks


CASE_LABEL_RE = re.compile(r"^\s*(\d+)\.\s*([a-z][^:]{3,160}?):\s*(.*)$")
MID_CASE_LABEL_RE = re.compile(r"^(.*?\.)\s+(\d+)\.\s*([a-z][^:]{3,160}?):\s*(.*)$")


def _render_case_label_paragraph(text: str, *, section_level: int) -> str | None:
    heading_prefix = "#" * min(section_level + 2, 6)

    match = CASE_LABEL_RE.match(text)
    if match:
        number, title, remainder = match.groups()
        lines = [f"{heading_prefix} {number}. {title.strip()}"]
        if remainder.strip():
            lines.extend(["", remainder.strip()])
        return "\n".join(lines)

    match = MID_CASE_LABEL_RE.match(text)
    if match:
        before, number, title, remainder = match.groups()
        lines = [before.strip(), "", f"{heading_prefix} {number}. {title.strip()}"]
        if remainder.strip():
            lines.extend(["", remainder.strip()])
        return "\n".join(lines)
    return None


def _looks_like_codeish_text(text: str) -> bool:
    stripped = text.strip()
    lowered = text.lower()
    if text.count("if (") >= 2 and ("push(" in text or "pop(" in text):
        return True
    if stripped.lower().startswith("struct ") and ";;" in text:
        return True
    if stripped.startswith("Q =") and ("project boundary curves" in lowered or "output " in lowered):
        return True
    if stripped.startswith("for (") or stripped.startswith("for each "):
        return True
    if stripped.startswith(("double ", "int ", "float ", "char ")) and ";;" in text:
        return True
    return False


def _format_code_lines(raw_text: str) -> list[str]:
    working = raw_text.strip()
    if working.lower().startswith("struct ") and " f " in working:
        prefix, remainder = working.split(" f ", 1)
        working = f"{prefix} {{;; {remainder}"

    segments = [segment.strip() for segment in working.split(";;")]
    lines: list[str] = []
    for segment in segments:
        if not segment:
            continue
        line = re.sub(r"\s+", " ", segment).strip()
        if not line:
            continue
        if line == "g":
            lines.append("}")
            continue
        if line.startswith("*"):
            comment_match = re.match(r"^\*\s*(.*?)\s*\*\s*(.*)$", line)
            if comment_match:
                comment, remainder = comment_match.groups()
                if comment.strip():
                    lines.append(f"/* {comment.strip()} */")
                if remainder.strip():
                    remainder_line = remainder.strip()
                    if remainder_line == "g":
                        lines.append("}")
                    else:
                        lines.append(remainder_line)
                continue
            lines.append(f"/* {line.lstrip('*').strip()} */")
            continue
        lines.append(line)

    repaired: list[str] = []
    for line in lines:
        updated = line
        updated = updated.replace("= =", "==")
        updated = updated.replace(" + +", "++")
        updated = updated.replace("semi-infinite ra y", "semi-infinite ray")
        updated = updated.replace("some poin t", "some point")
        updated = re.sub(r"\brst\b", "first", updated)
        if updated.startswith("/*"):
            repaired.append(updated)
            continue

        updated = updated.replace("dom point ", "dom_point_")
        updated = updated.replace("index of ", "index_of_")
        updated = updated.replace("start point", "start_point")
        updated = re.sub(r"\bdom_point_(\d)\s+([uv])\b", r"dom_point_\1_\2", updated)
        updated = re.sub(r"\bindex_of_(first|second)\s+point\b", r"index_of_\1_point", updated)
        updated = re.sub(r"\bindex_of_first_point\b", "index_of_first_point", updated)
        updated = re.sub(r"\bindex_of_second_point\b", "index_of_second_point", updated)
        updated = re.sub(r"\bindex_of_first\s+point\b", "index_of_first_point", updated)
        updated = re.sub(r"\bindex_of_second\s+point\b", "index_of_second_point", updated)
        if re.match(r"^(?:double|int|float|char)\b", updated) and not updated.endswith((";", "{", "}")):
            updated = f"{updated};"
        repaired.append(updated)
    return repaired


def _render_codeish_paragraph(text: str) -> str | None:
    if not _looks_like_codeish_text(text):
        return None

    code_prefix = text
    prose = ""
    if text.count("if (") >= 2 and ("push(" in text or "pop(" in text):
        prefix, separator, remainder = text.partition(" If ")
        if separator:
            code_prefix = prefix
            prose = f"If {remainder.strip()}".strip()

    code_lines = _format_code_lines(code_prefix)
    if len(code_lines) < 2:
        return None

    rendered = ["```text", *code_lines, "```"]
    if prose:
        rendered.extend(["", prose])
    return "\n".join(rendered)


def _render_imperative_list_paragraph(text: str) -> str | None:
    first_sentence_match = re.match(r"^(.*?\.)\s+(.*)$", text)
    sentence = first_sentence_match.group(1).strip() if first_sentence_match else text.strip()
    remainder = first_sentence_match.group(2).strip() if first_sentence_match else ""
    if sentence.endswith("."):
        sentence = sentence[:-1].strip()

    normalized = re.sub(r",\s+and\s+", ", ", sentence, flags=re.IGNORECASE)
    clauses = [re.sub(r"^and\s+", "", clause.strip(), flags=re.IGNORECASE) for clause in normalized.split(",") if clause.strip()]
    if len(clauses) < 3:
        return None

    lead_verbs = {
        "build",
        "classify",
        "compute",
        "construct",
        "create",
        "decompose",
        "determine",
        "evaluate",
        "extract",
        "find",
        "form",
        "initialize",
        "insert",
        "project",
        "remove",
        "select",
        "set",
        "sort",
        "split",
        "subdivide",
        "trace",
        "triangulate",
    }
    if any(not clause.split() or clause.split()[0].lower() not in lead_verbs for clause in clauses[:3]):
        return None
    if any(len(clause.split()) > 20 for clause in clauses[:3]):
        return None

    rendered = [f"- {clause}" for clause in clauses]
    if remainder:
        rendered.extend(["", remainder])
    return "\n".join(rendered)


def _render_paragraph(
    spans: list[dict[str, Any]],
    math_map: dict[str, dict[str, Any]],
    reference_map: dict[str, dict[str, Any]],
    *,
    section_level: int,
) -> str:
    raw_text = _paragraph_text(spans, math_map, reference_map, inline_math_mode="plain")
    rendered_text = _paragraph_text(spans, math_map, reference_map, inline_math_mode="rendered")
    return (
        _render_codeish_paragraph(raw_text)
        or _render_case_label_paragraph(rendered_text, section_level=section_level)
        or _render_imperative_list_paragraph(rendered_text)
        or rendered_text
    )


def render_block(
    block: dict[str, Any],
    math_map: dict[str, dict[str, Any]],
    figure_map: dict[str, dict[str, Any]],
    reference_map: dict[str, dict[str, Any]],
    *,
    section_level: int,
) -> str:
    block_type = str(block.get("type", ""))
    content = block.get("content", {})

    if block_type == "paragraph":
        spans = content.get("spans", [])
        return _render_paragraph(
            spans,
            math_map,
            reference_map,
            section_level=section_level,
        )

    if block_type == "list_item":
        spans = content.get("spans", [])
        text = _paragraph_text(spans, math_map, reference_map, inline_math_mode="rendered")
        marker = str(content.get("marker", "") or "")
        ordered = bool(content.get("ordered", False))
        prefix = marker if marker else ("1." if ordered else "-")
        return f"{prefix} {text}".strip()

    if block_type == "code":
        lines = content.get("lines", [])
        language = str(content.get("language", "text") or "text")
        return f"```{language}\n" + "\n".join(str(line) for line in lines) + "\n```"

    if block_type in {"display_equation_ref", "equation_group_ref"}:
        math_entry = math_map.get(str(content.get("math_id")), {})
        lines: list[str] = []

        latex_blocks = _display_latex_blocks(math_entry)
        for latex in latex_blocks:
            lines.append("$$")
            lines.append(latex)
            lines.append("$$")
            lines.append("")
        return "\n".join(lines).strip()

    if block_type == "figure_ref":
        figure = figure_map.get(str(content.get("figure_id")), {})
        image_path = figure.get("image_path")
        label = figure.get("label", "Figure")
        caption = figure.get("caption", "")
        if image_path:
            image_abs = Path(image_path)
            if not image_abs.is_absolute():
                image_abs = ENGINE_ROOT / image_abs
            return f"![{label}]({image_abs})\n\n*{label}: {caption}*"
        return f"*{label}: {caption}*"

    if block_type == "algorithm":
        lines = content.get("lines", [])
        raw_text = "\n".join(str(line) for line in lines if str(line).strip())
        return _render_codeish_paragraph(raw_text) or ("```text\n" + raw_text + "\n```")

    if block_type == "reference":
        reference = reference_map.get(str(content.get("reference_id")), {})
        return f"- {reference.get('text', '')}".strip()

    if block_type == "footnote":
        return str(content.get("text", ""))

    return ""


def render_section(
    section: dict[str, Any],
    sections_by_id: dict[str, dict[str, Any]],
    blocks_by_id: dict[str, dict[str, Any]],
    math_map: dict[str, dict[str, Any]],
    figure_map: dict[str, dict[str, Any]],
    reference_map: dict[str, dict[str, Any]],
) -> list[str]:
    lines: list[str] = []
    level = max(1, int(section.get("level", 1)))
    lines.append(f"{'#' * min(level + 1, 6)} {section.get('title', '')}".strip())
    lines.append("")

    for block_id in section.get("block_ids", []):
        block = blocks_by_id.get(str(block_id))
        if block is None:
            continue
        rendered = render_block(
            block,
            math_map,
            figure_map,
            reference_map,
            section_level=level,
        )
        if rendered:
            lines.append(rendered)
            lines.append("")

    for child_id in section.get("children", []):
        child = sections_by_id.get(str(child_id))
        if child is not None:
            lines.extend(render_section(child, sections_by_id, blocks_by_id, math_map, figure_map, reference_map))
    return lines


def render_document(document: dict[str, Any]) -> str:
    blocks_by_id = {block["id"]: block for block in document.get("blocks", [])}
    math_map = {entry["id"]: entry for entry in document.get("math", [])}
    figure_map = {figure["id"]: figure for figure in document.get("figures", [])}
    reference_map = {reference["id"]: reference for reference in document.get("references", [])}
    sections_by_id = {section["id"]: section for section in document.get("sections", [])}

    child_ids = {child_id for section in document.get("sections", []) for child_id in section.get("children", [])}
    root_sections = [section for section in document.get("sections", []) if section["id"] not in child_ids]

    lines: list[str] = [f"# {document.get('title', '')}", ""]
    front_matter = document.get("front_matter", {})
    authors = [author.get("name", "") for author in front_matter.get("authors", []) if author.get("name")]
    if authors:
        lines.append(", ".join(authors))
        lines.append("")
    for affiliation in front_matter.get("affiliations", []):
        for key in ("department", "institution", "address"):
            value = str(affiliation.get(key, "")).strip()
            if value:
                lines.append(value)
        if any(str(affiliation.get(key, "")).strip() for key in ("department", "institution", "address")):
            lines.append("")

    abstract_id = front_matter.get("abstract_block_id")
    if abstract_id and abstract_id in blocks_by_id:
        lines.append("## Abstract")
        lines.append("")
        lines.append(
            render_block(
                blocks_by_id[abstract_id],
                math_map,
                figure_map,
                reference_map,
                section_level=1,
            )
        )
        lines.append("")

    funding_id = front_matter.get("funding_block_id")
    if funding_id and funding_id in blocks_by_id:
        lines.append("## Funding Note")
        lines.append("")
        lines.append(
            render_block(
                blocks_by_id[funding_id],
                math_map,
                figure_map,
                reference_map,
                section_level=1,
            )
        )
        lines.append("")

    for section in root_sections:
        if section["id"] in {"sec-references"}:
            continue
        lines.extend(render_section(section, sections_by_id, blocks_by_id, math_map, figure_map, reference_map))

    references_section = sections_by_id.get("sec-references")
    if references_section is not None:
        lines.extend(render_section(references_section, sections_by_id, blocks_by_id, math_map, figure_map, reference_map))

    return "\n".join(lines).strip() + "\n"


def main() -> int:
    args = parse_args()
    document = json.loads(canonical_path(args.paper_id).read_text(encoding="utf-8"))
    destination = output_path(args.paper_id)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_document(document), encoding="utf-8")
    print(json.dumps({"path": str(destination)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
