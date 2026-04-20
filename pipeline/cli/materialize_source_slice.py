#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Callable

from pipeline.corpus.slices import (
    load_source_slice_manifest,
    materialize_source_slice,
    normalize_requested_paper_ids,
)
from pipeline.corpus_layout import current_layout


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy selected source-state corpus PDFs into a throwaway project directory for repeated validation runs."
    )
    parser.add_argument("target_project_dir", help="Project directory to materialize under tmp/ or another scratch location.")
    parser.add_argument(
        "--source-corpus-dir",
        help="Source-state corpus root. Defaults to the configured corpus root.",
    )
    parser.add_argument(
        "--paper-id",
        action="append",
        default=[],
        help="Paper id to copy. May be provided more than once.",
    )
    parser.add_argument(
        "--manifest",
        help="Optional JSON manifest with a 'papers' list.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing non-empty target project directory.",
    )
    return parser.parse_args()


def run_materialize_source_slice_cli(
    args: argparse.Namespace,
    *,
    current_layout_fn: Callable[[], object] = current_layout,
    load_source_slice_manifest_fn: Callable[[str | Path], dict[str, object]] = load_source_slice_manifest,
    materialize_source_slice_fn: Callable[..., dict[str, object]] = materialize_source_slice,
    print_fn: Callable[[str], None] = print,
) -> int:
    requested_paper_ids = list(args.paper_id or [])
    manifest_summary: dict[str, object] | None = None
    if args.manifest:
        manifest_summary = load_source_slice_manifest_fn(args.manifest)
        requested_paper_ids.extend(str(paper_id) for paper_id in manifest_summary.get("paper_ids", []))

    requested_paper_ids = normalize_requested_paper_ids(requested_paper_ids)
    if not requested_paper_ids:
        raise SystemExit("Provide at least one --paper-id or a --manifest with papers.")

    layout = current_layout_fn()
    source_corpus_dir = (
        Path(args.source_corpus_dir).expanduser().resolve()
        if args.source_corpus_dir
        else layout.corpus_root
    )
    payload = materialize_source_slice_fn(
        source_corpus_dir,
        args.target_project_dir,
        paper_ids=requested_paper_ids,
        clobber=bool(args.force),
    )
    if manifest_summary is not None:
        payload["manifest"] = {
            "path": manifest_summary["manifest_path"],
            "label": manifest_summary["label"],
            "paper_count": manifest_summary["paper_count"],
        }
    print_fn(json.dumps(payload, indent=2))
    return 0


def main() -> int:
    return run_materialize_source_slice_cli(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
