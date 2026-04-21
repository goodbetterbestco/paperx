from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import re
from statistics import mean
from typing import Any

from pipeline.native_stderr import open_pdf_with_diagnostics, run_with_stderr_label
from pipeline.acquisition.grobid_policy import grobid_product_provider_chain
from pipeline.corpus_layout import ProjectLayout, display_path, paper_pdf_path


MATH_TOKEN_RE = re.compile(r"(?:\\[A-Za-z]+|[=<>+\-^_]{1,2}|\b(?:lemma|theorem|proof|corollary)\b)")
REFERENCE_MARKER_RE = re.compile(r"(?:\[\d+\]|\(\d{4}\)|\bdoi\b)", re.IGNORECASE)


@dataclass(frozen=True)
class AcquisitionSignals:
    page_count: int
    text_page_ratio: float
    avg_text_chars_per_page: float
    avg_image_coverage: float
    max_image_coverage: float
    avg_text_block_count: float
    max_text_block_count: int
    two_column_ratio: float
    math_token_density: float
    reference_marker_density: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AcquisitionRouteDecision:
    primary_route: str
    traits: list[str]
    rationale: list[str]
    recommended_providers: list[str]
    product_plan: dict[str, list[str]]
    ocr_prepass: dict[str, Any]
    signals: AcquisitionSignals

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["signals"] = self.signals.to_dict()
        return payload


def _load_fitz() -> Any:
    try:
        import fitz  # type: ignore
    except ModuleNotFoundError as exc:
        raise RuntimeError("PyMuPDF is required for acquisition routing.") from exc
    return fitz


def _page_text_blocks(page: Any) -> list[tuple[float, float, float, float, str]]:
    raw_blocks = page.get_text("blocks") or []
    blocks: list[tuple[float, float, float, float, str]] = []
    for block in raw_blocks:
        if len(block) < 5:
            continue
        text = str(block[4] or "").strip()
        if not text:
            continue
        blocks.append((float(block[0]), float(block[1]), float(block[2]), float(block[3]), text))
    return blocks


def _page_image_coverage(page: Any) -> float:
    try:
        page_dict = page.get_text("dict") or {}
    except Exception:
        return 0.0
    page_area = max(float(page.rect.width) * float(page.rect.height), 1.0)
    coverage = 0.0
    for block in page_dict.get("blocks", []):
        if int(block.get("type", 0) or 0) != 1:
            continue
        bbox = block.get("bbox") or []
        if len(bbox) != 4:
            continue
        x0, y0, x1, y1 = (float(value) for value in bbox)
        coverage += max(x1 - x0, 0.0) * max(y1 - y0, 0.0)
    return min(coverage / page_area, 1.0)


def _is_two_column_page(page: Any, blocks: list[tuple[float, float, float, float, str]]) -> bool:
    if len(blocks) < 4:
        return False
    width = max(float(page.rect.width), 1.0)
    substantial_blocks = [block for block in blocks if len(block[4]) >= 80]
    if len(substantial_blocks) < 2:
        return False
    left_blocks = 0
    right_blocks = 0
    for x0, _y0, x1, _y1, _text in substantial_blocks:
        center_x = (x0 + x1) / 2.0
        if center_x <= width * 0.45:
            left_blocks += 1
        elif center_x >= width * 0.55:
            right_blocks += 1
    return left_blocks >= 2 and right_blocks >= 2


def _route_profile(primary_route: str) -> tuple[list[str], dict[str, list[str]]]:
    metadata_plan = grobid_product_provider_chain("metadata")
    reference_plan = grobid_product_provider_chain("references")
    if primary_route == "scan_or_image_heavy":
        return (
            ["ocrmypdf", "docling", "mathpix"],
            {
                "prepass": ["ocrmypdf"],
                "metadata": metadata_plan,
                "layout": ["docling", "llamaparse"],
                "math": ["mathpix", "docling"],
                "references": reference_plan,
            },
        )
    if primary_route == "degraded_or_garbled":
        return (
            ["ocrmypdf", "docling", "mathpix", "marker"],
            {
                "prepass": ["ocrmypdf"],
                "metadata": metadata_plan,
                "layout": ["docling", "marker"],
                "math": ["mathpix", "docling"],
                "references": reference_plan,
            },
        )
    if primary_route == "layout_complex":
        return (
            ["docling", "llamaparse", "marker", "mineru"],
            {
                "metadata": metadata_plan,
                "layout": ["docling", "llamaparse", "marker", "mineru"],
                "math": ["mathpix", "docling"],
                "references": reference_plan,
            },
        )
    if primary_route == "math_dense":
        return (
            ["docling", "mathpix", "grobid"],
            {
                "metadata": metadata_plan,
                "layout": ["docling"],
                "math": ["mathpix", "docling"],
                "references": reference_plan,
            },
        )
    return (
        ["grobid", "docling"],
        {
            "metadata": metadata_plan,
            "layout": ["docling"],
            "math": ["docling", "mathpix"],
            "references": reference_plan,
        },
    )


def inspect_pdf_signals(
    pdf_path: str | Path,
    *,
    paper_id: str | None = None,
    load_fitz: Any | None = None,
) -> AcquisitionSignals:
    fitz = load_fitz() if load_fitz is not None else _load_fitz()
    resolved_path = Path(pdf_path).resolve()
    label = paper_id or resolved_path.stem
    document = open_pdf_with_diagnostics(
        f"{label} stage=acquisition-routing-open",
        resolved_path,
        fitz_module=fitz,
    )

    def _inspect() -> AcquisitionSignals:
        with document:
            page_count = len(document)
            if page_count <= 0:
                return AcquisitionSignals(
                    page_count=0,
                    text_page_ratio=0.0,
                    avg_text_chars_per_page=0.0,
                    avg_image_coverage=0.0,
                    max_image_coverage=0.0,
                    avg_text_block_count=0.0,
                    max_text_block_count=0,
                    two_column_ratio=0.0,
                    math_token_density=0.0,
                    reference_marker_density=0.0,
                )

            text_lengths: list[int] = []
            image_coverages: list[float] = []
            text_block_counts: list[int] = []
            two_column_pages = 0
            text_pages = 0
            full_text_parts: list[str] = []

            for page in document:
                text = str(page.get_text("text") or "")
                blocks = _page_text_blocks(page)
                image_coverage = _page_image_coverage(page)
                text_length = len(text.strip())
                if text_length >= 80:
                    text_pages += 1
                text_lengths.append(text_length)
                text_block_counts.append(len(blocks))
                image_coverages.append(image_coverage)
                if _is_two_column_page(page, blocks):
                    two_column_pages += 1
                full_text_parts.append(text)

        full_text = "\n".join(full_text_parts)
        text_chars = sum(text_lengths)
        text_length_denominator = max(text_chars, 1)
        return AcquisitionSignals(
            page_count=page_count,
            text_page_ratio=round(text_pages / max(page_count, 1), 3),
            avg_text_chars_per_page=round(mean(text_lengths), 2),
            avg_image_coverage=round(mean(image_coverages), 3),
            max_image_coverage=round(max(image_coverages, default=0.0), 3),
            avg_text_block_count=round(mean(text_block_counts), 2),
            max_text_block_count=max(text_block_counts, default=0),
            two_column_ratio=round(two_column_pages / max(page_count, 1), 3),
            math_token_density=round(len(MATH_TOKEN_RE.findall(full_text)) / text_length_denominator, 5),
            reference_marker_density=round(len(REFERENCE_MARKER_RE.findall(full_text)) / text_length_denominator, 5),
        )

    return run_with_stderr_label(f"{label} stage=acquisition-routing", _inspect)


def route_pdf_signals(signals: AcquisitionSignals) -> AcquisitionRouteDecision:
    from pipeline.acquisition.ocr_policy import decide_ocr_prepass_policy

    rationale: list[str] = []
    traits: list[str] = []

    if signals.reference_marker_density >= 0.0005:
        traits.append("scholarly_references")
    if signals.two_column_ratio >= 0.4:
        traits.append("two_column")
    if signals.math_token_density >= 0.018:
        traits.append("math_heavy")
    if signals.avg_image_coverage >= 0.2 or signals.max_image_coverage >= 0.5:
        traits.append("image_heavy")

    primary_route = "born_digital_scholarly"
    if signals.text_page_ratio < 0.55 or (
        signals.avg_text_chars_per_page < 250 and signals.avg_image_coverage >= 0.35
    ):
        primary_route = "scan_or_image_heavy"
        rationale.append("low embedded text coverage with high image coverage suggests a scan-first route")
    elif signals.avg_text_chars_per_page < 500 and signals.avg_image_coverage >= 0.15:
        primary_route = "degraded_or_garbled"
        rationale.append("mixed text and image signals suggest a degraded born-digital PDF")
    elif signals.math_token_density >= 0.018:
        primary_route = "math_dense"
        rationale.append("math token density is high enough to justify a math-specialist route")
    elif signals.two_column_ratio >= 0.4 or signals.max_text_block_count >= 12:
        primary_route = "layout_complex"
        rationale.append("layout block distribution suggests a multi-column or structurally complex document")
    else:
        rationale.append("strong embedded text coverage and low image dominance suggest a born-digital paper")

    if not rationale:
        rationale.append("defaulted to born-digital scholarly route")

    recommended_providers, product_plan = _route_profile(primary_route)
    ocr_prepass = decide_ocr_prepass_policy(primary_route, signals=signals)
    return AcquisitionRouteDecision(
        primary_route=primary_route,
        traits=traits,
        rationale=rationale,
        recommended_providers=recommended_providers,
        product_plan=product_plan,
        ocr_prepass=ocr_prepass.to_dict(),
        signals=signals,
    )


def build_acquisition_route_report(
    paper_id: str,
    *,
    layout: ProjectLayout | None = None,
    inspect_pdf_signals_fn: Any | None = None,
) -> dict[str, Any]:
    active_layout = layout or ProjectLayout.from_environment()
    pdf_path = paper_pdf_path(paper_id, layout=active_layout)
    active_inspect_pdf_signals = inspect_pdf_signals_fn or inspect_pdf_signals
    signals = active_inspect_pdf_signals(pdf_path, paper_id=paper_id)
    decision = route_pdf_signals(signals)
    return {
        "paper_id": paper_id,
        "pdf_path": display_path(pdf_path, layout=active_layout),
        **decision.to_dict(),
    }


__all__ = [
    "AcquisitionRouteDecision",
    "AcquisitionSignals",
    "build_acquisition_route_report",
    "inspect_pdf_signals",
    "route_pdf_signals",
]
