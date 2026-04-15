from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def default_review(risk: str = "medium", status: str = "unreviewed", notes: str = "") -> dict[str, str]:
    return {
        "status": status,
        "risk": risk,
        "notes": notes,
    }


def default_formula_conversion(status: str = "unconverted", notes: str = "") -> dict[str, Any]:
    return {
        "status": status,
        "notes": notes,
    }


def default_formula_classification(
    category: str = "unknown",
    semantic_policy: str = "graphic_only",
    role: str = "unknown",
    confidence: str = "low",
    signals: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "category": category,
        "semantic_policy": semantic_policy,
        "role": role,
        "confidence": confidence,
        "signals": list(signals or []),
    }


@dataclass(frozen=True)
class SourceSpan:
    page: int
    bbox: dict[str, float]
    engine: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "page": self.page,
            "bbox": self.bbox,
            "engine": self.engine,
        }


@dataclass(frozen=True)
class LayoutBlock:
    id: str
    page: int
    order: int
    text: str
    role: str
    bbox: dict[str, float]
    engine: str = "native_pdf"
    meta: dict[str, Any] = field(default_factory=dict)

    def source_span(self) -> SourceSpan:
        return SourceSpan(page=self.page, bbox=self.bbox, engine=self.engine)

    def as_record(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "page": self.page,
            "group_index": self.order,
            "split_index": 1,
            "type": self.role,
            "text": self.text,
            "source_spans": [self.source_span().as_dict()],
            "meta": self.meta,
        }
