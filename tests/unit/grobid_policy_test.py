from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.acquisition.grobid_policy import (
    grobid_policy_decision,
    grobid_policy_snapshot,
    grobid_product_provider_chain,
    is_grobid_live_for_route,
    is_grobid_live_product,
)


class GrobidPolicyTest(unittest.TestCase):
    def test_grobid_is_live_for_metadata_and_references_only(self) -> None:
        self.assertTrue(is_grobid_live_product("metadata"))
        self.assertTrue(is_grobid_live_product("references"))
        self.assertFalse(is_grobid_live_product("layout"))
        self.assertFalse(is_grobid_live_product("math"))

    def test_grobid_metadata_policy_includes_scan_route(self) -> None:
        self.assertTrue(is_grobid_live_for_route("metadata", "scan_or_image_heavy"))
        decision = grobid_policy_decision("metadata", route="scan_or_image_heavy")
        self.assertTrue(decision.live)

    def test_grobid_layout_and_math_remain_trial_only(self) -> None:
        self.assertFalse(grobid_policy_decision("layout").live)
        self.assertFalse(grobid_policy_decision("math").live)

    def test_grobid_provider_chain_only_prepends_grobid_for_live_products(self) -> None:
        self.assertEqual(grobid_product_provider_chain("metadata"), ["grobid", "docling"])
        self.assertEqual(grobid_product_provider_chain("references"), ["grobid", "docling"])
        self.assertEqual(grobid_product_provider_chain("layout"), ["docling"])

    def test_grobid_policy_snapshot_is_operator_readable(self) -> None:
        snapshot = grobid_policy_snapshot()
        self.assertEqual(snapshot["live_products"], ["metadata", "references"])
        self.assertEqual(snapshot["trial_only_products"], ["layout", "math"])
        self.assertIn("scan_or_image_heavy", snapshot["live_routes"])


if __name__ == "__main__":
    unittest.main()
