from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import shutil
from typing import Literal

from pipeline.corpus_layout import ProjectLayout, current_layout
from pipeline.output.fingerprints import CURRENT_BUILDER_VERSION


TextEngine = Literal["native", "pdftotext", "hybrid"]
_DOCLING_DEVICE_VALUES = {"auto", "cpu", "mps", "cuda", "xpu"}


def _env_value(name: str, legacy_name: str, default: str = "") -> str:
    return os.environ.get(name, os.environ.get(legacy_name, default)).strip()


def _configured_docling_device() -> str | None:
    configured = os.environ.get("STEPVIEW_DOCLING_DEVICE", "").strip().lower()
    if configured in _DOCLING_DEVICE_VALUES:
        return configured
    return None


@dataclass(frozen=True)
class PipelineConfig:
    layout: ProjectLayout
    builder_version: str
    text_engine: TextEngine
    use_external_layout: bool
    use_external_math: bool
    include_review: bool
    fail_on_missing_title: bool
    write_decision_sidecars: bool
    docling_bin: Path | None
    docling_device: str | None
    mathpix_enabled: bool
    pdftotext_enabled: bool


def build_pipeline_config(
    *,
    layout: ProjectLayout | None = None,
    text_engine: TextEngine = "native",
    use_external_layout: bool = False,
    use_external_math: bool = False,
    include_review: bool = True,
    fail_on_missing_title: bool = True,
    write_decision_sidecars: bool = True,
) -> PipelineConfig:
    active_layout = layout or current_layout()
    docling_bin = _env_value("PIPELINE_DOCLING_BIN", "PAPER_PIPELINE_DOCLING_BIN")
    return PipelineConfig(
        layout=active_layout,
        builder_version=CURRENT_BUILDER_VERSION,
        text_engine=text_engine,
        use_external_layout=bool(use_external_layout),
        use_external_math=bool(use_external_math),
        include_review=include_review,
        fail_on_missing_title=fail_on_missing_title,
        write_decision_sidecars=write_decision_sidecars,
        docling_bin=Path(docling_bin).expanduser().resolve() if docling_bin else None,
        docling_device=_configured_docling_device(),
        mathpix_enabled=bool(os.environ.get("MATHPIX_APP_ID") and os.environ.get("MATHPIX_APP_KEY")),
        pdftotext_enabled=shutil.which("pdftotext") is not None,
    )
