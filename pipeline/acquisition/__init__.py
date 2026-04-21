from __future__ import annotations

from pipeline.acquisition.grobid_policy import (
    GrobidPolicyDecision,
    grobid_policy_decision,
    grobid_policy_snapshot,
    grobid_product_provider_chain,
    is_grobid_live_for_route,
    is_grobid_live_product,
)
from pipeline.acquisition.ocr_policy import OcrPrepassDecision, decide_ocr_prepass_policy
from pipeline.acquisition.providers import (
    MathpixExecutionDecision,
    MetadataReferenceObservation,
    build_provider_execution_plan,
    decide_mathpix_execution,
    load_metadata_reference_observation,
)
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
    "GrobidPolicyDecision",
    "MathpixExecutionDecision",
    "MetadataReferenceObservation",
    "OcrPrepassDecision",
    "build_acquisition_route_report",
    "build_provider_execution_plan",
    "build_source_scorecard",
    "decide_mathpix_execution",
    "decide_ocr_prepass_policy",
    "grobid_policy_decision",
    "grobid_policy_snapshot",
    "grobid_product_provider_chain",
    "inspect_pdf_signals",
    "is_grobid_live_for_route",
    "is_grobid_live_product",
    "load_metadata_reference_observation",
    "reported_layout_provider",
    "reported_math_provider",
    "route_pdf_signals",
    "score_layout_provider",
    "score_math_provider",
    "score_metadata_provider",
]
