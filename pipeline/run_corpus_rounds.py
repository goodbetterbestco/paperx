#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json

from pipeline.corpus_layout import CORPUS_DIR, ProjectLayout
from pipeline.orchestrator.round_reporting import render_final_report as _render_final_report
from pipeline.orchestrator.round_runtime import (
    RoundRuntime,
    TMP_DIR,
    build_round_runtime as _build_round_runtime,
    configure_runtime_environment as _configure_runtime_environment,
    load_status as _load_status_impl,
    paper_ids as _paper_ids,
    rebuild_lexicon as _rebuild_lexicon_impl,
    save_status as _save_status_impl,
)
from pipeline.orchestrator.round_settings import (
    assert_mathpix_dns_available as _assert_mathpix_dns_available,
    mathpix_credentials_available as _mathpix_credentials_available,
)
from pipeline.orchestrator.round_execution import process_round as _process_round, run_paper_job as _run_paper_job
from pipeline.orchestrator.round_sources import build_extraction_sources_for_paper as _build_extraction_sources_for_paper
from pipeline.runtime_paths import ENGINE_ROOT


DEFAULT_RUNTIME = _build_round_runtime()
BATCH_DIR = DEFAULT_RUNTIME.batch_dir
STATUS_PATH = DEFAULT_RUNTIME.status_path
REPORT_PATH = DEFAULT_RUNTIME.report_path
DOCS_DIR = CORPUS_DIR
LEXICON_PATH = DEFAULT_RUNTIME.lexicon_path


def _load_status(runtime: RoundRuntime | None = None) -> dict[str, Any]:
    return _load_status_impl(runtime or DEFAULT_RUNTIME)


def _save_status(status: dict[str, Any], runtime: RoundRuntime | None = None) -> None:
    _save_status_impl(status, runtime or DEFAULT_RUNTIME)


def _rebuild_lexicon(runtime: RoundRuntime | None = None) -> dict[str, Any]:
    return _rebuild_lexicon_impl(runtime or DEFAULT_RUNTIME)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run canonical extraction across the corpus. By default this runs one round; round 2 is opt-in."
    )
    parser.add_argument(
        "--start-round",
        type=int,
        choices=(1, 2),
        default=1,
        help="Round number to start from. Defaults to 1.",
    )
    parser.add_argument(
        "--end-round",
        type=int,
        choices=(1, 2),
        default=1,
        help="Round number to end on. Defaults to 1.",
    )
    parser.add_argument(
        "--stop-after-round",
        type=int,
        choices=(1, 2),
        default=None,
        help="Optional round number after which execution should stop even if later rounds are configured.",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=1,
        help="Maximum number of papers to process concurrently within a round. Defaults to 1.",
    )
    parser.add_argument(
        "--force-rebuild",
        action="store_true",
        help="Rebuild every targeted paper even when the canonical is already fresh.",
    )
    return parser.parse_args()


def run_rounds(
    *,
    start_round: int = 1,
    end_round: int = 1,
    stop_after_round: int | None = None,
    max_workers: int = 1,
    force_rebuild: bool = False,
    layout: ProjectLayout | None = None,
) -> dict[str, Any]:
    if start_round > end_round:
        raise SystemExit("--start-round cannot be greater than --end-round")
    if max_workers < 1:
        raise SystemExit("--max-workers must be at least 1")

    _configure_runtime_environment()
    if _mathpix_credentials_available():
        _assert_mathpix_dns_available()
    runtime = _build_round_runtime(layout)
    runtime.batch_dir.mkdir(parents=True, exist_ok=True)

    status = _load_status(runtime)
    status["papers"] = _paper_ids(layout=runtime.layout)
    status["notes"] = [
        "Round processing uses Docling for layout, Mathpix for math when credentials are available, and lexicon refresh at round boundaries.",
        f"Corpus temp paths are redirected into {TMP_DIR}.",
        f"Configured worker concurrency: {max_workers}.",
        "Fresh canonicals are skipped when source inputs, build flags, and pipeline fingerprints still match.",
        "Mathpix defaults to whole-PDF round coordination when multiple papers are pending and credentials are available.",
    ]
    if runtime.layout.project_mode:
        status["notes"].append(f"Project reports are written into {runtime.batch_dir}.")
    if force_rebuild:
        status["notes"].append("Fresh canonicals are still rebuilt because --force-rebuild was enabled.")
    _save_status(status, runtime)

    _rebuild_lexicon(runtime)
    for round_index in range(start_round, end_round + 1):
        _process_round(
            status,
            round_index,
            max_workers=max_workers,
            force_rebuild=bool(force_rebuild),
            layout=runtime.layout,
            runtime=runtime,
            run_paper_job_impl=lambda paper_id, **kwargs: _run_paper_job(
                paper_id,
                build_extraction_sources_for_paper_impl=_build_extraction_sources_for_paper,
                **kwargs,
            ),
        )
        _rebuild_lexicon(runtime)
        if stop_after_round == round_index:
            break

    report = _render_final_report(status)
    runtime.report_path.write_text(report, encoding="utf-8")
    return {
        "status_path": str(runtime.status_path),
        "report_path": str(runtime.report_path),
        "rounds": list(status.get("rounds", {}).keys()),
        "papers": len(status.get("papers", [])),
    }


def main() -> int:
    args = _parse_args()
    result = run_rounds(
        start_round=args.start_round,
        end_round=args.end_round,
        stop_after_round=args.stop_after_round,
        max_workers=args.max_workers,
        force_rebuild=bool(args.force_rebuild),
    )
    print(
        json.dumps(
            result,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
