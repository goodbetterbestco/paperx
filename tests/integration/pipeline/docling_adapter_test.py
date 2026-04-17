import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.docling_adapter import _resolve_docling_command, docling_json_to_external_sources, run_docling


def _docling_item(ref: str, label: str, text: str, *, page: int, left: float, top: float, right: float, bottom: float) -> dict:
    return {
        "self_ref": ref,
        "label": label,
        "text": text,
        "orig": text,
        "prov": [
            {
                "page_no": page,
                "bbox": {"l": left, "t": top, "r": right, "b": bottom},
            }
        ],
    }


class DoclingAdapterTest(unittest.TestCase):
    def test_resolve_docling_command_uses_configured_bin(self) -> None:
        with patch.dict("os.environ", {"PIPELINE_DOCLING_BIN": "/custom/docling"}):
            self.assertEqual(_resolve_docling_command(), ["/custom/docling"])

    def test_run_docling_raises_clear_error_when_cli_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            with (
                patch("pipeline.docling_adapter._paper_pdf_path", return_value=Path("/tmp/fake.pdf")),
                patch("pipeline.docling_adapter._resolve_docling_command", side_effect=FileNotFoundError("Docling CLI not found.")),
            ):
                with self.assertRaisesRegex(FileNotFoundError, "Docling CLI not found"):
                    run_docling("synthetic_test_paper", output_dir=output_dir)

    def test_page_one_abstract_and_intro_close_front_matter(self) -> None:
        docling_document = {
            "texts": [
                _docling_item("#/texts/0", "section_header", "Synthetic Test Paper", page=1, left=40, top=770, right=300, bottom=740),
                _docling_item("#/texts/1", "text", "Alice Example", page=1, left=40, top=720, right=180, bottom=700),
                _docling_item("#/texts/2", "section_header", "Abstract", page=1, left=40, top=680, right=120, bottom=665),
                _docling_item("#/texts/3", "text", "A concise abstract lives here.", page=1, left=40, top=650, right=360, bottom=620),
                _docling_item("#/texts/4", "section_header", "1. Introduction", page=1, left=40, top=590, right=180, bottom=570),
                _docling_item("#/texts/5", "text", "Body text starts here.", page=1, left=40, top=560, right=360, bottom=530),
            ]
        }
        fake_layout = {
            "pdf_path": "docs/synthetic_test_paper.pdf",
            "page_count": 1,
            "page_sizes_pt": [{"page": 1, "width": 600.0, "height": 800.0}],
            "blocks": [],
        }

        with patch("pipeline.docling_adapter.extract_layout", return_value=fake_layout):
            layout, _ = docling_json_to_external_sources(docling_document, "synthetic_test_paper")

        roles = {block["text"]: block["role"] for block in layout["blocks"]}
        self.assertEqual(roles["Synthetic Test Paper"], "front_matter")
        self.assertEqual(roles["Alice Example"], "front_matter")
        self.assertEqual(roles["Abstract"], "heading")
        self.assertEqual(roles["A concise abstract lives here."], "paragraph")
        self.assertEqual(roles["1. Introduction"], "heading")
        self.assertEqual(roles["Body text starts here."], "paragraph")


if __name__ == "__main__":
    unittest.main()
