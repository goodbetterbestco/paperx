from __future__ import annotations

from importlib import import_module


_EXPORTS = {
    "_build_lexicon": ("pipeline.corpus.lexicon_builder", "_build_lexicon"),
    "audit_corpus": ("pipeline.corpus.audit", "audit_corpus"),
    "audit_document": ("pipeline.corpus.audit", "audit_document"),
    "audit_missing_canonical": ("pipeline.corpus.audit", "audit_missing_canonical"),
    "build_figure_expectations": ("pipeline.corpus.metadata", "build_figure_expectations"),
    "canonical_pdf_filename": ("pipeline.corpus.metadata", "canonical_pdf_filename"),
    "configured_corpus_dir": ("pipeline.corpus.paths", "configured_corpus_dir"),
    "configured_project_dir": ("pipeline.corpus.paths", "configured_project_dir"),
    "corpus_join_terms": ("pipeline.corpus.lexicon", "corpus_join_terms"),
    "corpus_paper_id": ("pipeline.corpus.paths", "corpus_paper_id"),
    "discover_paper_pdf_paths": ("pipeline.corpus.metadata", "discover_paper_pdf_paths"),
    "display_path": ("pipeline.corpus.paths", "display_path"),
    "env_value": ("pipeline.corpus.paths", "env_value"),
    "load_corpus_lexicon": ("pipeline.corpus.lexicon", "load_corpus_lexicon"),
    "load_figure_expectations": ("pipeline.corpus.metadata", "load_figure_expectations"),
    "normalize_paper_id": ("pipeline.corpus.paths", "normalize_paper_id"),
    "paper_dir_name_from_paper_id": ("pipeline.corpus.metadata", "paper_dir_name_from_paper_id"),
    "paper_figure_metadata": ("pipeline.corpus.metadata", "paper_figure_metadata"),
    "paper_id_from_dir_name": ("pipeline.corpus.metadata", "paper_id_from_dir_name"),
    "paper_id_from_pdf_path": ("pipeline.corpus.metadata", "paper_id_from_pdf_path"),
    "prepare_project_inputs": ("pipeline.corpus.paths", "prepare_project_inputs"),
}

__all__ = list(_EXPORTS)


def __getattr__(name: str):
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attr_name = _EXPORTS[name]
    value = getattr(import_module(module_name), attr_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(list(globals()) + __all__)
