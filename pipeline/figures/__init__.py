from __future__ import annotations

from pipeline.figures.labels import caption_label

__all__ = [
    "build_manifest_from_pdf_path",
    "caption_label",
    "discover_manifests",
    "load_or_generate_ocr_records",
    "main",
    "process_paper",
    "render_crop",
    "render_crop_if_missing",
]


def __getattr__(name: str) -> object:
    if name == "caption_label":
        return caption_label
    if name in __all__:
        from pipeline.figures import linking

        return getattr(linking, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
