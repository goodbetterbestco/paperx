from __future__ import annotations

from pipeline.acquisition.backfill import backfill_acquisition_sidecars
from pipeline.acquisition.benchmark_artifacts import (
    build_benchmark_artifact_paths,
    current_benchmark_output_dir,
    load_current_benchmark_dashboard,
    load_current_benchmark_status,
    load_current_benchmark_summary,
    write_benchmark_artifact_bundle,
)
from pipeline.acquisition.benchmark import (
    load_benchmark_manifest,
    run_acquisition_benchmark,
)
from pipeline.acquisition.benchmark_compare import compare_benchmark_reports
from pipeline.acquisition.benchmark_dashboard import summarize_benchmark_dashboard
from pipeline.acquisition.benchmark_history import list_benchmark_history
from pipeline.acquisition.benchmark_reports import (
    aggregate_provider_score_map,
    benchmark_report_label,
    family_provider_score_maps,
    list_history_reports,
    load_benchmark_report,
    provider_score_map,
    resolve_benchmark_report_path,
)
from pipeline.acquisition.benchmark_status import benchmark_status_from_dashboard, summarize_latest_benchmark_status
from pipeline.acquisition.benchmark_trend import summarize_benchmark_trend
from pipeline.acquisition.audit import audit_acquisition_quality
from pipeline.acquisition.grobid_trial import load_grobid_trial_manifest, run_grobid_trial
from pipeline.acquisition.ocr_policy import OcrPrepassDecision, decide_ocr_prepass_policy
from pipeline.acquisition.providers import MetadataReferenceObservation, load_metadata_reference_observation
from pipeline.acquisition.routing import (
    AcquisitionRouteDecision,
    AcquisitionSignals,
    build_acquisition_route_report,
    inspect_pdf_signals,
    route_pdf_signals,
)
from pipeline.acquisition.scoring import (
    build_source_scorecard,
    score_layout_provider,
    score_math_provider,
    score_metadata_provider,
)
from pipeline.acquisition.source_ownership import reported_layout_provider, reported_math_provider

__all__ = [
    "AcquisitionRouteDecision",
    "AcquisitionSignals",
    "MetadataReferenceObservation",
    "OcrPrepassDecision",
    "audit_acquisition_quality",
    "aggregate_provider_score_map",
    "backfill_acquisition_sidecars",
    "benchmark_status_from_dashboard",
    "benchmark_report_label",
    "build_benchmark_artifact_paths",
    "build_acquisition_route_report",
    "build_source_scorecard",
    "compare_benchmark_reports",
    "current_benchmark_output_dir",
    "decide_ocr_prepass_policy",
    "family_provider_score_maps",
    "inspect_pdf_signals",
    "load_benchmark_manifest",
    "load_current_benchmark_dashboard",
    "load_current_benchmark_status",
    "load_current_benchmark_summary",
    "load_benchmark_report",
    "load_grobid_trial_manifest",
    "load_metadata_reference_observation",
    "list_benchmark_history",
    "list_history_reports",
    "provider_score_map",
    "route_pdf_signals",
    "resolve_benchmark_report_path",
    "run_acquisition_benchmark",
    "run_grobid_trial",
    "summarize_benchmark_dashboard",
    "summarize_latest_benchmark_status",
    "summarize_benchmark_trend",
    "reported_layout_provider",
    "reported_math_provider",
    "score_math_provider",
    "score_metadata_provider",
    "score_layout_provider",
    "write_benchmark_artifact_bundle",
]
