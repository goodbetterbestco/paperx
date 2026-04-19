from __future__ import annotations

from pipeline.acquisition.backfill import backfill_acquisition_sidecars
from pipeline.acquisition.benchmark import (
    load_benchmark_manifest,
    run_acquisition_benchmark,
)
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
    "backfill_acquisition_sidecars",
    "build_acquisition_route_report",
    "build_source_scorecard",
    "decide_ocr_prepass_policy",
    "inspect_pdf_signals",
    "load_benchmark_manifest",
    "load_grobid_trial_manifest",
    "load_metadata_reference_observation",
    "route_pdf_signals",
    "run_acquisition_benchmark",
    "run_grobid_trial",
    "reported_layout_provider",
    "reported_math_provider",
    "score_math_provider",
    "score_metadata_provider",
    "score_layout_provider",
]
