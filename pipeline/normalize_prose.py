from __future__ import annotations

from collections import Counter

from pipeline.corpus_layout import ProjectLayout
from pipeline.text import prose as _prose
from pipeline.text.prose import *  # noqa: F401,F403

zipf_frequency = _prose.zipf_frequency


def normalize_prose_text(
    text: str,
    *,
    layout: ProjectLayout | None = None,
) -> tuple[str, Counter[str]]:
    previous = _prose.zipf_frequency
    _prose.zipf_frequency = zipf_frequency
    try:
        return _prose.normalize_prose_text(text, layout=layout)
    finally:
        _prose.zipf_frequency = previous


__all__ = [name for name in dir(_prose) if not name.startswith("_")]
