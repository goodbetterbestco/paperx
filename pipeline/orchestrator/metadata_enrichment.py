from __future__ import annotations

from typing import Any

from pipeline.policies.abstract_quality import abstract_quality_flags
from pipeline.acquisition.source_ownership import canonical_provider_name
from pipeline.text.references import normalize_reference_text
from pipeline.types import default_review


def _block_text(block: dict[str, Any]) -> str:
    content = block.get("content") or {}
    spans = list(content.get("spans", []))
    if spans:
        return " ".join(str(span.get("text", "")).strip() for span in spans if str(span.get("text", "")).strip()).strip()
    return str(content.get("text", "") or "").strip()


def _find_block(blocks: list[dict[str, Any]], block_id: str | None) -> dict[str, Any] | None:
    if not block_id:
        return None
    for block in blocks:
        if str(block.get("id", "")) == str(block_id):
            return block
    return None


def _metadata_reference_entry(text: str, *, index: int, provider: str) -> dict[str, Any]:
    normalized_text, _ = normalize_reference_text(text)
    return {
        "id": f"ref-{index:03d}",
        "raw_text": text,
        "text": normalized_text,
        "source_spans": [],
        "alternates": [],
        "review": default_review(risk="medium", notes=f"sourced from {provider} metadata observation"),
    }


def _basis_allows_apply(basis: str | None) -> bool:
    normalized = str(basis or "").strip()
    return normalized != "fallback_unaccepted"


def apply_metadata_observation(state: Any) -> Any:
    observation = dict(getattr(state, "metadata_observation", None) or {})
    reference_observation = dict(getattr(state, "reference_observation", None) or {})
    if not observation and not reference_observation:
        return state

    provider = str(
        observation.get("provider") or reference_observation.get("provider") or "metadata_observation"
    )
    reference_provider = str(
        reference_observation.get("provider") or observation.get("provider", "metadata_observation") or "metadata_observation"
    )
    source_scorecard = dict(getattr(state, "source_scorecard", {}) or {})
    decision_artifacts = dict(getattr(state, "decision_artifacts", {}) or {})
    front_matter = dict(getattr(state, "front_matter", None) or {})
    blocks = list(getattr(state, "blocks", []) or [])
    references = list(getattr(state, "references", []) or [])

    metadata_decision = dict(decision_artifacts.get("metadata") or {})
    metadata_decision.setdefault("provider", provider)
    metadata_decision["reference_provider"] = reference_provider
    metadata_decision["recommended_metadata_provider"] = canonical_provider_name(
        source_scorecard.get("recommended_primary_metadata_provider")
    )
    metadata_decision["recommended_reference_provider"] = canonical_provider_name(
        source_scorecard.get("recommended_primary_reference_provider")
    )
    metadata_basis = str(source_scorecard.get("metadata_recommendation_basis", "") or "") or None
    reference_basis = str(source_scorecard.get("reference_recommendation_basis", "") or "") or None
    metadata_decision["metadata_recommendation_basis"] = metadata_basis
    metadata_decision["reference_recommendation_basis"] = reference_basis
    metadata_allowed = _basis_allows_apply(metadata_basis)
    reference_allowed = _basis_allows_apply(reference_basis)

    current_title = str(front_matter.get("title", "") or "").strip()
    observed_title = str(observation.get("title", "") or "").strip()
    if metadata_allowed and observed_title and (not current_title or len(current_title.split()) < 3):
        front_matter["title"] = observed_title
        decision_artifacts["title"] = {
            "selected_text": observed_title,
            "source": f"{provider}_metadata_observation",
            "candidate_count": 0,
            "candidates": [],
        }
        metadata_decision["title_applied"] = True
    else:
        metadata_decision.setdefault("title_applied", False)
        if observed_title and not metadata_allowed:
            metadata_decision["title_suppressed_reason"] = "metadata_provider_not_accepted"

    abstract_block = _find_block(blocks, front_matter.get("abstract_block_id"))
    current_abstract = _block_text(abstract_block or {})
    observed_abstract = str(observation.get("abstract", "") or "").strip()
    current_abstract_flags = abstract_quality_flags(current_abstract)
    observed_abstract_flags = abstract_quality_flags(observed_abstract) if observed_abstract else ["missing"]
    if (
        metadata_allowed
        and abstract_block is not None
        and observed_abstract
        and current_abstract_flags
        and not observed_abstract_flags
    ):
        abstract_block["content"] = {"spans": [{"kind": "text", "text": observed_abstract}]}
        abstract_block["source_spans"] = []
        abstract_block["review"] = default_review(risk="medium", notes=f"sourced from {provider} metadata observation")
        decision_artifacts["abstract"] = {
            "selected_text": observed_abstract,
            "source": f"{provider}_metadata_observation",
            "placeholder": False,
            "candidate_count": 0,
            "candidates": [],
        }
        metadata_decision["abstract_applied"] = True
    else:
        metadata_decision.setdefault("abstract_applied", False)
        if observed_abstract and current_abstract_flags and not metadata_allowed:
            metadata_decision["abstract_suppressed_reason"] = "metadata_provider_not_accepted"

    selected_reference_observation = reference_observation or observation
    observed_references = [
        str(item).strip()
        for item in selected_reference_observation.get("references", [])
        if str(item).strip()
    ]
    if reference_allowed and observed_references and not references:
        references = [
            _metadata_reference_entry(text, index=index, provider=reference_provider)
            for index, text in enumerate(observed_references, start=1)
        ]
        state.references = references
        metadata_decision["references_applied"] = True
    else:
        metadata_decision.setdefault("references_applied", False)
        if observed_references and not reference_allowed:
            metadata_decision["references_suppressed_reason"] = "reference_provider_not_accepted"
    metadata_decision["reference_count"] = len(observed_references)

    state.front_matter = front_matter
    state.blocks = blocks
    decision_artifacts["metadata"] = metadata_decision
    state.decision_artifacts = decision_artifacts

    document = getattr(state, "document", None)
    if isinstance(document, dict):
        document["front_matter"] = front_matter
        document["title"] = str(front_matter.get("title", document.get("title", "")))
        document["blocks"] = blocks
        document["references"] = references
        document["_decision_artifacts"] = decision_artifacts
        state.document = document

    return state


__all__ = [
    "apply_metadata_observation",
]
