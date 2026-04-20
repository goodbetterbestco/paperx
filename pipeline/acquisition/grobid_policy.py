from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


GROBID_LIVE_PRODUCTS = ("metadata", "references")
GROBID_TRIAL_ONLY_PRODUCTS = ("layout", "math")
GROBID_LIVE_ROUTES = (
    "born_digital_scholarly",
    "layout_complex",
    "math_dense",
    "scan_or_image_heavy",
    "degraded_or_garbled",
)
GROBID_POLICY_STATUS = "live_metadata_reference_only"
GROBID_POLICY_SUMMARY = (
    "GROBID participates in live acquisition only for metadata and references; "
    "layout and math remain trial-only."
)


@dataclass(frozen=True)
class GrobidPolicyDecision:
    product: str
    route: str | None
    live: bool
    status: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_product(product: str | None) -> str:
    return str(product or "").strip().lower()


def _normalize_route(route: str | None) -> str | None:
    normalized = str(route or "").strip()
    return normalized or None


def is_grobid_live_product(product: str | None) -> bool:
    return _normalize_product(product) in GROBID_LIVE_PRODUCTS


def is_grobid_live_for_route(product: str | None, route: str | None) -> bool:
    normalized_product = _normalize_product(product)
    normalized_route = _normalize_route(route)
    if normalized_product not in GROBID_LIVE_PRODUCTS:
        return False
    if normalized_route is None:
        return False
    return normalized_route in GROBID_LIVE_ROUTES


def grobid_product_provider_chain(product: str | None, *, fallback_provider: str = "docling") -> list[str]:
    providers: list[str] = []
    if is_grobid_live_product(product):
        providers.append("grobid")
    fallback = str(fallback_provider or "").strip()
    if fallback and fallback not in providers:
        providers.append(fallback)
    return providers


def grobid_policy_decision(product: str | None, *, route: str | None = None) -> GrobidPolicyDecision:
    normalized_product = _normalize_product(product)
    normalized_route = _normalize_route(route)
    if normalized_product in GROBID_LIVE_PRODUCTS:
        if normalized_route and normalized_route not in GROBID_LIVE_ROUTES:
            return GrobidPolicyDecision(
                product=normalized_product,
                route=normalized_route,
                live=False,
                status="unsupported_route",
                reason="grobid_live_only_for_known_acquisition_routes",
            )
        return GrobidPolicyDecision(
            product=normalized_product,
            route=normalized_route,
            live=True,
            status="live",
            reason="grobid_live_for_metadata_reference_products",
        )
    if normalized_product in GROBID_TRIAL_ONLY_PRODUCTS:
        return GrobidPolicyDecision(
            product=normalized_product,
            route=normalized_route,
            live=False,
            status="trial_only",
            reason="grobid_not_used_for_live_layout_or_math_selection",
        )
    return GrobidPolicyDecision(
        product=normalized_product,
        route=normalized_route,
        live=False,
        status="unsupported_product",
        reason="grobid_policy_not_defined_for_product",
    )


def grobid_policy_snapshot() -> dict[str, Any]:
    return {
        "status": GROBID_POLICY_STATUS,
        "summary": GROBID_POLICY_SUMMARY,
        "live_products": list(GROBID_LIVE_PRODUCTS),
        "trial_only_products": list(GROBID_TRIAL_ONLY_PRODUCTS),
        "live_routes": list(GROBID_LIVE_ROUTES),
    }


__all__ = [
    "GROBID_LIVE_PRODUCTS",
    "GROBID_LIVE_ROUTES",
    "GROBID_POLICY_STATUS",
    "GROBID_POLICY_SUMMARY",
    "GROBID_TRIAL_ONLY_PRODUCTS",
    "GrobidPolicyDecision",
    "grobid_policy_decision",
    "grobid_policy_snapshot",
    "grobid_product_provider_chain",
    "is_grobid_live_for_route",
    "is_grobid_live_product",
]
