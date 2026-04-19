import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.config import build_pipeline_config
from pipeline.corpus_layout import ProjectLayout
from pipeline.reconcile.entrypoint import reconcile_paper_state
from pipeline.text.prose import normalize_prose_text
from pipeline.text.references import normalize_reference_text


def _corpus_layout(root: Path) -> ProjectLayout:
    corpus_root = root / "corpus" / "synthetic"
    return ProjectLayout(
        engine_root=root,
        mode="corpus",
        corpus_name="synthetic",
        project_dir=None,
        corpus_root=corpus_root,
        source_root=corpus_root,
        review_root=corpus_root / "review_drafts",
        runs_root=corpus_root / "_runs",
        tmp_root=root / "tmp",
        figure_expectations_path=corpus_root / "figure_expectations.json",
    )


def _write_lexicon(layout: ProjectLayout, *, terms: list[str]) -> None:
    layout.corpus_lexicon_path.parent.mkdir(parents=True, exist_ok=True)
    layout.corpus_lexicon_path.write_text(
        json.dumps(
            {
                "terms": [
                    {
                        "canonical": term,
                        "count": 1,
                        "variants": [],
                    }
                    for term in terms
                ],
                "authors": [],
                "acronyms": [],
            }
        ),
        encoding="utf-8",
    )


def _fake_zipf_frequency(word: str, language: str) -> float:
    del language
    scores = {
        "trimmed": 5.0,
        "surface": 5.0,
        "trimmedsurface": 0.5,
    }
    return scores.get(word.lower(), 5.0)


class NormalizeLayoutTest(unittest.TestCase):
    def test_normalize_prose_text_uses_explicit_layout_join_terms(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            with_term_layout = _corpus_layout(root / "with_term")
            without_term_layout = _corpus_layout(root / "without_term")
            _write_lexicon(with_term_layout, terms=["trimmedsurface"])
            _write_lexicon(without_term_layout, terms=[])

            with patch("pipeline.text.prose.zipf_frequency", side_effect=_fake_zipf_frequency):
                normalized_with_term, with_term_counts = normalize_prose_text(
                    "trimmed surface",
                    layout=with_term_layout,
                )
                normalized_without_term, without_term_counts = normalize_prose_text(
                    "trimmed surface",
                    layout=without_term_layout,
                )

            self.assertEqual(normalized_with_term, "trimmedsurface")
            self.assertEqual(normalized_without_term, "trimmed surface")
            self.assertEqual(with_term_counts["frequency_join"], 1)
            self.assertNotIn("frequency_join", without_term_counts)

    def test_normalize_reference_text_forwards_explicit_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            layout = _corpus_layout(root)
            _write_lexicon(layout, terms=["trimmedsurface"])

            with patch("pipeline.text.prose.zipf_frequency", side_effect=_fake_zipf_frequency):
                normalized, counts = normalize_reference_text(
                    "[12] trimmed surface",
                    layout=layout,
                )

            self.assertEqual(normalized, "[12] trimmedsurface")
            self.assertEqual(counts["frequency_join"], 1)

    def test_reconcile_paper_state_binds_caption_normalizer_to_config_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            layout = _corpus_layout(root)
            _write_lexicon(layout, terms=["trimmedsurface"])
            config = build_pipeline_config(layout=layout, include_review=False)

            with (
                patch("pipeline.text.prose.zipf_frequency", side_effect=_fake_zipf_frequency),
                patch("pipeline.reconcile.entrypoint.run_paper_pipeline") as run_paper_pipeline,
            ):
                run_paper_pipeline.side_effect = (
                    lambda *args, **kwargs: kwargs["normalize_figure_caption_text"]("Fig. 1 trimmed surface")
                )
                normalized_caption = reconcile_paper_state(
                    "1990_synthetic_test_paper",
                    config=config,
                )

            self.assertEqual(normalized_caption, "trimmedsurface")


if __name__ == "__main__":
    unittest.main()
