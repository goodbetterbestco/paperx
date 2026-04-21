from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pipeline.corpus_layout import ProjectLayout, current_layout, paper_pdf_path
from pipeline.output.identity import PIPELINE_COMPONENTS


ROOT = Path(__file__).resolve().parents[2]
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


def _component_modules(components: tuple[tuple[str, Path], ...]) -> dict[str, str]:
    modules: dict[str, str] = {}
    for component_id, path in components:
        fingerprint = fingerprint_path(path)
        modules[component_id] = str(fingerprint.get("sha256", "missing"))
    return modules


def _stable_pipeline_modules() -> dict[str, str]:
    return _component_modules(PIPELINE_COMPONENTS)


def pipeline_fingerprint() -> dict[str, Any]:
    modules = _stable_pipeline_modules()
    return {
        "builder_version": CURRENT_BUILDER_VERSION,
        "fingerprint": _combined_pipeline_hash(modules),
        "modules": modules,
    }


def build_input_fingerprints(
    paper_id: str,
    *,
    pdf_path: str | Path | None = None,
    layout: ProjectLayout | None = None,
) -> dict[str, Any]:
    resolved_pdf_path = pdf_path or paper_pdf_path(paper_id)
    return {
        "pdf": fingerprint_path(resolved_pdf_path),
    }


def build_metadata_for_paper(
    paper_id: str,
    *,
    pdf_path: str | Path,
    timestamp: str,
    layout_engine: str,
    math_engine: str,
    figure_engine: str,
    text_engine: str,
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
        "inputs": build_input_fingerprints(
            paper_id,
            pdf_path=pdf_path,
        ),
        "pipeline": pipeline_fingerprint(),
    }
