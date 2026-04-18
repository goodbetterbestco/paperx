from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from pipeline.corpus_layout import ProjectLayout, current_layout
from pipeline.sources.docling import docling_json_to_external_sources, run_docling
from pipeline.sources.external import external_layout_path, external_math_path
from pipeline.sources.mathpix import mathpix_pages_to_external_sources, run_mathpix
from pipeline.sources.pdftotext_overlay import overlay_pdftotext_onto_layout


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


@dataclass(frozen=True)
class ExternalSourceBuildResult:
    paper_id: str
    layout: ProjectLayout
    summary: dict[str, Any]
    layout_payload: dict[str, Any]
    math_payload: dict[str, Any] | None = None

    def write(self) -> dict[str, str]:
        layout_path = external_layout_path(self.paper_id, layout=self.layout)
        _write_json(layout_path, self.layout_payload)

        outputs = {"layout_path": str(layout_path)}
        if self.math_payload is not None:
            math_path = external_math_path(self.paper_id, layout=self.layout)
            _write_json(math_path, self.math_payload)
            outputs["math_path"] = str(math_path)
        return outputs


def build_docling_external_sources(
    paper_id: str,
    *,
    docling_json: str | None = None,
    device: str | None = None,
    layout: ProjectLayout | None = None,
) -> ExternalSourceBuildResult:
    active_layout = layout or current_layout()
    docling_path = Path(docling_json) if docling_json else run_docling(paper_id, device=device, layout=active_layout)
    document = _load_json(docling_path)
    external_layout, external_math = docling_json_to_external_sources(document, paper_id, layout=active_layout)
    return ExternalSourceBuildResult(
        paper_id=paper_id,
        layout=active_layout,
        summary={
            "docling_json": str(docling_path),
            "layout_engine": external_layout.get("engine"),
            "layout_blocks": len(external_layout.get("blocks", [])),
            "math_engine": external_math.get("engine"),
            "math_entries": len(external_math.get("entries", [])),
        },
        layout_payload=external_layout,
        math_payload=external_math,
    )


def build_mathpix_external_sources(
    paper_id: str,
    *,
    pages: list[int] | None = None,
    endpoint: str = "https://api.mathpix.com/v3/pdf",
    app_id: str | None = None,
    app_key: str | None = None,
    mathpix_json: list[str] | None = None,
    layout: ProjectLayout | None = None,
) -> ExternalSourceBuildResult:
    active_layout = layout or current_layout()
    if mathpix_json:
        payloads = [_load_json(path) for path in mathpix_json]
        payloads.sort(key=lambda item: int(item.get("page", 0)))
        source = ",".join(mathpix_json)
    else:
        mathpix_result = run_mathpix(
            paper_id,
            pages=pages,
            endpoint=endpoint,
            app_id=app_id,
            app_key=app_key,
            layout=active_layout,
        )
        payloads = list(mathpix_result.get("pages") or [])
        source = "mathpix_api"

    external_layout, external_math = mathpix_pages_to_external_sources(payloads, paper_id, layout=active_layout)
    return ExternalSourceBuildResult(
        paper_id=paper_id,
        layout=active_layout,
        summary={
            "source": source,
            "layout_engine": external_layout.get("engine"),
            "layout_blocks": len(external_layout.get("blocks", [])),
            "math_engine": external_math.get("engine"),
            "math_entries": len(external_math.get("entries", [])),
        },
        layout_payload=external_layout,
        math_payload=external_math,
    )


def build_pdftotext_external_layout(
    paper_id: str,
    *,
    layout: ProjectLayout | None = None,
) -> ExternalSourceBuildResult:
    active_layout = layout or current_layout()
    payload, summary = overlay_pdftotext_onto_layout(paper_id, layout=active_layout)
    return ExternalSourceBuildResult(
        paper_id=paper_id,
        layout=active_layout,
        summary=summary,
        layout_payload=payload,
    )


def compose_external_sources(
    paper_id: str,
    *,
    layout_json: str | Path,
    math_json: str | Path,
    layout: ProjectLayout | None = None,
) -> ExternalSourceBuildResult:
    active_layout = layout or current_layout()
    external_layout = _load_json(layout_json)
    external_math = _load_json(math_json)
    return ExternalSourceBuildResult(
        paper_id=paper_id,
        layout=active_layout,
        summary={
            "layout_engine": external_layout.get("engine"),
            "layout_blocks": len(external_layout.get("blocks", [])),
            "math_engine": external_math.get("engine"),
            "math_entries": len(external_math.get("entries", [])),
        },
        layout_payload=external_layout,
        math_payload=external_math,
    )
