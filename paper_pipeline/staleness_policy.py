from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from paper_pipeline.corpus_layout import CORPUS_DIR, paper_pdf_path
from paper_pipeline.pipeline_identity import PIPELINE_COMPONENTS
from paper_pipeline.external_sources import external_layout_path, external_math_path


ROOT = Path(__file__).resolve().parents[1]
CURRENT_BUILDER_VERSION = "0.2.0"


def _now_iso_from_timestamp(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _relative_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def _resolve_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return ROOT / candidate


def fingerprint_path(path: str | Path) -> dict[str, Any]:
    resolved = _resolve_path(path)
    payload: dict[str, Any] = {
        "path": _relative_path(resolved),
        "exists": resolved.exists(),
    }
    if not resolved.exists():
        return payload

    stat = resolved.stat()
    payload["size_bytes"] = int(stat.st_size)
    payload["modified_at"] = _now_iso_from_timestamp(stat.st_mtime)
    digest = hashlib.sha256()
    with resolved.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    payload["sha256"] = digest.hexdigest()
    return payload


def _combined_pipeline_hash(modules: dict[str, str]) -> str:
    combined = hashlib.sha256()
    for module_id, module_hash in modules.items():
        combined.update(module_id.encode("utf-8"))
        combined.update(b"\0")
        combined.update(module_hash.encode("utf-8"))
        combined.update(b"\0")
    return combined.hexdigest()


def _stable_pipeline_modules() -> dict[str, str]:
    modules: dict[str, str] = {}
    for component_id, path in PIPELINE_COMPONENTS:
        fingerprint = fingerprint_path(path)
        modules[component_id] = str(fingerprint.get("sha256", "missing"))
    return modules


def _legacy_pipeline_fingerprint() -> str:
    legacy_modules: dict[str, str] = {}
    for _, path in PIPELINE_COMPONENTS:
        fingerprint = fingerprint_path(path)
        module_path = str(fingerprint["path"])
        legacy_modules[module_path] = str(fingerprint.get("sha256", "missing"))
    return _combined_pipeline_hash(legacy_modules)


def pipeline_fingerprint() -> dict[str, Any]:
    modules = _stable_pipeline_modules()
    return {
        "builder_version": CURRENT_BUILDER_VERSION,
        "fingerprint": _combined_pipeline_hash(modules),
        "modules": modules,
        "compatibility": {
            "legacy_path_fingerprint": _legacy_pipeline_fingerprint(),
        },
    }


def build_input_fingerprints(
    paper_id: str,
    *,
    pdf_path: str | Path | None = None,
    use_external_layout: bool,
    use_external_math: bool,
) -> dict[str, Any]:
    resolved_pdf_path = pdf_path or paper_pdf_path(paper_id)
    inputs: dict[str, Any] = {
        "pdf": fingerprint_path(resolved_pdf_path),
    }
    if use_external_layout:
        inputs["external_layout"] = fingerprint_path(external_layout_path(paper_id))
    if use_external_math:
        inputs["external_math"] = fingerprint_path(external_math_path(paper_id))
    return inputs


def build_metadata_for_paper(
    paper_id: str,
    *,
    pdf_path: str | Path,
    timestamp: str,
    layout_engine: str,
    math_engine: str,
    figure_engine: str,
    text_engine: str,
    use_external_layout: bool,
    use_external_math: bool,
) -> dict[str, Any]:
    return {
        "created_at": timestamp,
        "updated_at": timestamp,
        "builder_version": CURRENT_BUILDER_VERSION,
        "sources": {
            "native_pdf": True,
            "layout_engine": layout_engine,
            "math_engine": math_engine,
            "figure_engine": figure_engine,
            "text_engine": text_engine,
        },
        "flags": {
            "use_external_layout": use_external_layout,
            "use_external_math": use_external_math,
            "rebuild": False,
        },
        "inputs": build_input_fingerprints(
            paper_id,
            pdf_path=pdf_path,
            use_external_layout=use_external_layout,
            use_external_math=use_external_math,
        ),
        "pipeline": pipeline_fingerprint(),
    }


def _normalize_desired_flags(document: dict[str, Any], desired_flags: dict[str, bool] | None) -> dict[str, bool]:
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


def _fingerprints_match(stored: dict[str, Any] | None, current: dict[str, Any]) -> bool:
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
    effective_flags = _normalize_desired_flags(document, desired_flags)
    inputs = current_inputs or build_input_fingerprints(
        paper_id,
        pdf_path=document.get("source", {}).get("pdf_path") or paper_pdf_path(paper_id),
        use_external_layout=effective_flags["use_external_layout"],
        use_external_math=effective_flags["use_external_math"],
    )
    pipeline = current_pipeline or pipeline_fingerprint()

    reasons: list[str] = []
    if str(build.get("builder_version", "")) != CURRENT_BUILDER_VERSION:
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
        if not _fingerprints_match(stored_inputs.get(key), current):
            reasons.append(f"{key}_input_changed")

    return {
        "paper_id": paper_id,
        "stale": bool(reasons),
        "reasons": sorted(set(reasons)),
        "builder_version": str(build.get("builder_version", "")),
        "current_builder_version": CURRENT_BUILDER_VERSION,
        "desired_flags": effective_flags,
    }


def detect_canonical_staleness(
    canonical_path: Path,
    *,
    desired_flags: dict[str, bool] | None = None,
) -> dict[str, Any]:
    if not canonical_path.exists():
        return {
            "paper_id": canonical_path.parent.name,
            "stale": True,
            "reasons": ["canonical_missing"],
            "builder_version": "",
            "current_builder_version": CURRENT_BUILDER_VERSION,
            "desired_flags": desired_flags or {"use_external_layout": False, "use_external_math": False},
        }
    document = json.loads(canonical_path.read_text(encoding="utf-8"))
    return detect_document_staleness(document, desired_flags=desired_flags)
