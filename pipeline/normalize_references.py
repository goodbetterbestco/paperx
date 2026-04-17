from __future__ import annotations

from collections import Counter

from pipeline.corpus_layout import ProjectLayout
from pipeline.text import prose as _prose
from pipeline.text import references as _references
from pipeline.text.references import *  # noqa: F401,F403


def normalize_reference_text(
    text: str,
    *,
    layout: ProjectLayout | None = None,
) -> tuple[str, Counter[str]]:
    from pipeline import normalize_prose as root_prose

    previous = _prose.zipf_frequency
    _prose.zipf_frequency = root_prose.zipf_frequency
    try:
        return _references.normalize_reference_text(text, layout=layout)
    finally:
        _prose.zipf_frequency = previous


__all__ = [name for name in dir(_references) if not name.startswith("_")]
