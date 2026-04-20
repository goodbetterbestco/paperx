from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from pipeline.acquisition.routing import AcquisitionSignals


@dataclass(frozen=True)
class OcrPrepassDecision:
    should_run: bool
    policy: str
    tool: str | None
    output_pdf_kind: str | None
    rationale: list[str]
    trigger_signals: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def decide_ocr_prepass_policy(
    primary_route: str,
    *,
    signals: AcquisitionSignals,
) -> OcrPrepassDecision:
    rationale: list[str] = []
    trigger_signals: list[str] = []
    severe_trigger_signals: list[str] = []

    if signals.text_page_ratio < 0.55:
        trigger_signals.append("low_text_page_ratio")
    if signals.text_page_ratio < 0.35:
        severe_trigger_signals.append("very_low_text_page_ratio")
    if signals.avg_image_coverage >= 0.2:
        trigger_signals.append("high_avg_image_coverage")
    if signals.avg_image_coverage >= 0.35:
        severe_trigger_signals.append("very_high_avg_image_coverage")
    if signals.max_image_coverage >= 0.5:
        trigger_signals.append("high_max_image_coverage")
    if signals.max_image_coverage >= 0.75:
        severe_trigger_signals.append("very_high_max_image_coverage")
    if signals.avg_text_chars_per_page < 500:
        trigger_signals.append("low_avg_text_chars_per_page")
    if signals.avg_text_chars_per_page < 180:
        severe_trigger_signals.append("very_low_avg_text_chars_per_page")

    severe_scan_evidence = bool(severe_trigger_signals) and (
        "very_low_text_page_ratio" in severe_trigger_signals
        or "very_high_avg_image_coverage" in severe_trigger_signals
        or "very_high_max_image_coverage" in severe_trigger_signals
        or (
            "very_low_avg_text_chars_per_page" in severe_trigger_signals
            and "high_avg_image_coverage" in trigger_signals
        )
    )
    multi_signal_risk = len(trigger_signals) >= 2 and (
        signals.avg_text_chars_per_page < 900 or signals.text_page_ratio < 0.75
    )

    if primary_route == "scan_or_image_heavy":
        rationale.append("scan-first routing indicates the PDF should be normalized before extraction.")
        return OcrPrepassDecision(
            should_run=True,
            policy="required",
            tool="ocrmypdf",
            output_pdf_kind="searchable_pdf",
            rationale=rationale,
            trigger_signals=trigger_signals,
        )

    if severe_scan_evidence:
        rationale.append("signal severity indicates scan-like degradation, so OCR normalization should be treated as required.")
        return OcrPrepassDecision(
            should_run=True,
            policy="required",
            tool="ocrmypdf",
            output_pdf_kind="searchable_pdf",
            rationale=rationale,
            trigger_signals=[*trigger_signals, *severe_trigger_signals],
        )

    if primary_route == "degraded_or_garbled":
        rationale.append("degraded mixed-content routing benefits from an OCR normalization pre-pass.")
        return OcrPrepassDecision(
            should_run=True,
            policy="recommended",
            tool="ocrmypdf",
            output_pdf_kind="searchable_pdf",
            rationale=rationale,
            trigger_signals=trigger_signals,
        )

    if multi_signal_risk:
        rationale.append("multiple OCR risk signals suggest normalization would improve downstream extraction.")
        return OcrPrepassDecision(
            should_run=True,
            policy="recommended",
            tool="ocrmypdf",
            output_pdf_kind="searchable_pdf",
            rationale=rationale,
            trigger_signals=trigger_signals,
        )

    rationale.append("embedded text quality is sufficient to skip OCR normalization.")
    return OcrPrepassDecision(
        should_run=False,
        policy="skip",
        tool=None,
        output_pdf_kind=None,
        rationale=rationale,
        trigger_signals=trigger_signals,
    )


__all__ = [
    "OcrPrepassDecision",
    "decide_ocr_prepass_policy",
]
