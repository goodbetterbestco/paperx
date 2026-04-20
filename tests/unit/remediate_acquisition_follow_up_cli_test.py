from __future__ import annotations

import argparse
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.cli.remediate_acquisition_follow_up import run_remediate_follow_up_cli
from pipeline.corpus_layout import ProjectLayout


def _project_layout(root: Path) -> ProjectLayout:
    corpus_root = root / "corpus"
    return ProjectLayout(
        engine_root=root,
        mode="project",
        corpus_name="fixture",
        project_dir=root,
        corpus_root=corpus_root,
        source_root=root / "source",
        review_root=root,
        runs_root=corpus_root / "_runs",
        tmp_root=root / "tmp",
        figure_expectations_path=corpus_root / "figure_expectations.json",
    )


class RemediateAcquisitionFollowUpCliTest(unittest.TestCase):
    def test_cli_applies_promotes_and_builds_with_external_sources_enabled(self) -> None:
        layout = _project_layout(Path("/tmp/paperx-remediate-cli").resolve())
        printed: list[str] = []
        captured: dict[str, object] = {}
        args = argparse.Namespace(
            paper_id="1990_synthetic_test_paper",
            label="trial-mathpix",
            text_engine="native",
            include_review=False,
            dry_run=True,
        )

        exit_code = run_remediate_follow_up_cli(
            args,
            current_layout_fn=lambda: layout,
            apply_follow_up_fn=lambda paper_id, *, layout=None, label=None: {
                "paper_id": paper_id,
                "label": label,
                "applied": True,
                "trial_dir": "/tmp/trial",
            },
            promote_trial_fn=lambda paper_id, *, layout=None, label=None: {
                "paper_id": paper_id,
                "label": label,
                "promoted": True,
                "sources_dir": "/tmp/sources",
            },
            build_paper_fn=lambda paper_id, **kwargs: (
                captured.update({"paper_id": paper_id, **kwargs})
                or type(
                    "Build",
                    (),
                    {
                        "layout": layout,
                        "document": {"paper_id": paper_id, "front_matter": {}, "blocks": [], "sections": [], "references": [], "figures": []},
                    },
                )()
            ),
            validate_canonical_fn=lambda document: None,
            build_summary_fn=lambda document: {"block_count": len(document.get("blocks", []))},
            print_fn=printed.append,
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(captured["paper_id"], "1990_synthetic_test_paper")
        self.assertTrue(captured["use_external_layout"])
        self.assertTrue(captured["use_external_math"])
        payload = json.loads(printed[0])
        self.assertEqual(payload["apply"]["label"], "trial-mathpix")
        self.assertEqual(payload["promotion"]["label"], "trial-mathpix")

    def test_cli_returns_apply_status_when_no_follow_up_trial_is_available(self) -> None:
        layout = _project_layout(Path("/tmp/paperx-remediate-cli").resolve())
        printed: list[str] = []
        args = argparse.Namespace(
            paper_id="1990_synthetic_test_paper",
            label="follow-up",
            text_engine="native",
            include_review=False,
            dry_run=False,
        )

        exit_code = run_remediate_follow_up_cli(
            args,
            current_layout_fn=lambda: layout,
            apply_follow_up_fn=lambda paper_id, *, layout=None, label=None: {
                "paper_id": paper_id,
                "label": label,
                "applied": False,
                "reason": "no_trial_actions",
            },
            print_fn=printed.append,
        )

        self.assertEqual(exit_code, 3)
        payload = json.loads(printed[0])
        self.assertEqual(payload["apply"]["reason"], "no_trial_actions")


if __name__ == "__main__":
    unittest.main()
