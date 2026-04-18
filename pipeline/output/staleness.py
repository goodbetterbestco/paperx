from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from pipeline.corpus_layout import paper_pdf_path
from pipeline.output.fingerprints import (
    CURRENT_BUILDER_VERSION,
    build_input_fingerprints,
    pipeline_fingerprint,
)


def normalize_desired_flags(document: dict[str, Any], desired_flags: dict[str, bool] | None) -> dict[str, bool]:
    if desired_flags is not None:
        return {
            "use_external_layout": bool(desired_flags.get("use_external_layout")),
            "use_external_math": bool(desired_flags.get("use_external_math")),
        }
    flags = document.get("build", {}).get("flags", {})
    return {
        "use_external_layout": bool(flags.get("use_external_layout")),
        "use_external_math": bool(flags.get("use_external_math")),
    }


def fingerprints_match(stored: dict[str, Any] | None, current: dict[str, Any]) -> bool:
    if not isinstance(stored, dict):
        return False
    return (
        bool(stored.get("exists")) == bool(current.get("exists"))
        and str(stored.get("path", "")) == str(current.get("path", ""))
        and str(stored.get("sha256", "")) == str(current.get("sha256", ""))
    )


def detect_document_staleness(
    document: dict[str, Any],
    *,
    current_builder_version: str = CURRENT_BUILDER_VERSION,
    build_input_fingerprints_impl: Callable[..., dict[str, Any]] = build_input_fingerprints,
    paper_pdf_path_impl: Callable[[str], Path] = paper_pdf_path,
    pipeline_fingerprint_impl: Callable[[], dict[str, Any]] = pipeline_fingerprint,
    desired_flags: dict[str, bool] | None = None,
    current_inputs: dict[str, Any] | None = None,
    current_pipeline: dict[str, Any] | None = None,
) -> dict[str, Any]:
    paper_id = str(document.get("paper_id", ""))
    build = document.get("build", {})
    stored_flags = {
        "use_external_layout": bool(build.get("flags", {}).get("use_external_layout")),
        "use_external_math": bool(build.get("flags", {}).get("use_external_math")),
    }
    effective_flags = normalize_desired_flags(document, desired_flags)
    inputs = current_inputs or build_input_fingerprints_impl(
        paper_id,
        pdf_path=document.get("source", {}).get("pdf_path") or paper_pdf_path_impl(paper_id),
        use_external_layout=effective_flags["use_external_layout"],
        use_external_math=effective_flags["use_external_math"],
    )
    pipeline = current_pipeline or pipeline_fingerprint_impl()

    reasons: list[str] = []
    if str(build.get("builder_version", "")) != current_builder_version:
        reasons.append("builder_version_changed")

    stored_pipeline = build.get("pipeline")
    if not isinstance(stored_pipeline, dict) or not stored_pipeline.get("fingerprint"):
        reasons.append("missing_pipeline_fingerprint")
    else:
        accepted_fingerprints = {str(pipeline.get("fingerprint", ""))}
        compatibility = pipeline.get("compatibility")
        if isinstance(compatibility, dict):
            accepted_fingerprints.update(str(value) for value in compatibility.values() if value)
        if str(stored_pipeline.get("fingerprint")) not in accepted_fingerprints:
            reasons.append("pipeline_fingerprint_changed")

    if stored_flags != effective_flags:
        reasons.append("build_flags_changed")

    stored_inputs = build.get("inputs")
    if not isinstance(stored_inputs, dict):
        reasons.append("missing_input_fingerprints")
        stored_inputs = {}

    for key, current in inputs.items():
        if key not in stored_inputs:
            reasons.append(f"missing_{key}_fingerprint")
            continue
        if not fingerprints_match(stored_inputs.get(key), current):
            reasons.append(f"{key}_input_changed")

    return {
        "paper_id": paper_id,
        "stale": bool(reasons),
        "reasons": sorted(set(reasons)),
        "builder_version": str(build.get("builder_version", "")),
        "current_builder_version": current_builder_version,
        "desired_flags": effective_flags,
    }


def detect_canonical_staleness(
    canonical_path: Path,
    *,
    current_builder_version: str = CURRENT_BUILDER_VERSION,
    detect_document_staleness_impl: Callable[..., dict[str, Any]] = detect_document_staleness,
    desired_flags: dict[str, bool] | None = None,
) -> dict[str, Any]:
    if not canonical_path.exists():
        return {
            "paper_id": canonical_path.parent.name,
            "stale": True,
            "reasons": ["canonical_missing"],
            "builder_version": "",
            "current_builder_version": current_builder_version,
            "desired_flags": desired_flags or {"use_external_layout": False, "use_external_math": False},
        }
    document = json.loads(canonical_path.read_text(encoding="utf-8"))
    return detect_document_staleness_impl(document, desired_flags=desired_flags)


__all__ = [
    "detect_canonical_staleness",
    "detect_document_staleness",
    "fingerprints_match",
    "normalize_desired_flags",
]
