from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any


SPACE_RE = re.compile(r"\s+")
NON_WORD_RE = re.compile(r"[^a-z0-9]+")


@dataclass(frozen=True)
class AcquisitionGoldRecord:
    paper_id: str
    title: str
    abstract: str
    headings: list[str]
    paragraphs: list[str]
    equations: list[str]
    references: list[str]


@dataclass(frozen=True)
class ProviderArtifacts:
    name: str
    layout_path: Path
    math_path: Path | None


@dataclass(frozen=True)
class BenchmarkPaper:
    paper_id: str
    gold_path: Path
    providers: list[ProviderArtifacts]


def _normalize_text(text: str) -> str:
    squashed = SPACE_RE.sub(" ", text.lower()).strip()
    return NON_WORD_RE.sub(" ", squashed).strip()


def _normalize_tokens(text: str) -> set[str]:
    normalized = _normalize_text(text)
    if not normalized:
        return set()
    return {token for token in normalized.split(" ") if token}


def _contains_normalized(haystack: str, needle: str) -> bool:
    normalized_haystack = _normalize_text(haystack)
    normalized_needle = _normalize_text(needle)
    return bool(normalized_needle and normalized_needle in normalized_haystack)


def _token_recall(expected: str, observed: str) -> float:
    expected_tokens = _normalize_tokens(expected)
    if not expected_tokens:
        return 1.0
    observed_tokens = _normalize_tokens(observed)
    return round(len(expected_tokens & observed_tokens) / len(expected_tokens), 3)


def _guess_title(blocks: list[dict[str, Any]]) -> str:
    for block in blocks:
        role = str(block.get("role", ""))
        text = str(block.get("text", "")).strip()
        if role == "front_matter" and text:
            return text
    for block in blocks:
        role = str(block.get("role", ""))
        text = str(block.get("text", "")).strip()
        if role == "heading" and text:
            return text
    return ""


def _guess_abstract(blocks: list[dict[str, Any]]) -> str:
    seen_abstract_marker = False
    for block in blocks:
        role = str(block.get("role", ""))
        text = str(block.get("text", "")).strip()
        if not text:
            continue
        normalized = _normalize_text(text)
        if normalized == "abstract":
            seen_abstract_marker = True
            continue
        if seen_abstract_marker and role in {"front_matter", "paragraph"}:
            return text
        if role == "front_matter" and normalized.startswith("abstract "):
            return text.split(" ", 1)[1].strip()
    return ""


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_provider_observation(layout_path: Path, math_path: Path | None) -> dict[str, Any]:
    layout_payload = _load_json(layout_path)
    math_payload = _load_json(math_path) if math_path is not None and math_path.exists() else {}
    blocks = list(layout_payload.get("blocks", []))
    headings = [str(block.get("text", "")).strip() for block in blocks if str(block.get("role", "")) == "heading"]
    paragraphs = [str(block.get("text", "")).strip() for block in blocks if str(block.get("role", "")) == "paragraph"]
    references = [str(block.get("text", "")).strip() for block in blocks if str(block.get("role", "")) == "reference"]
    full_text = "\n".join(text for text in headings + paragraphs + references if text)
    equations = [
        str(entry.get("display_latex", "") or entry.get("text", "")).strip()
        for entry in math_payload.get("entries", [])
        if str(entry.get("display_latex", "") or entry.get("text", "")).strip()
    ]
    return {
        "title": _guess_title(blocks),
        "abstract": _guess_abstract(blocks),
        "headings": headings,
        "paragraphs": paragraphs,
        "references": references,
        "equations": equations,
        "full_text": full_text,
    }


def _list_hit_rate(expected_items: list[str], observed_items: list[str], fallback_text: str) -> float:
    if not expected_items:
        return 1.0
    hits = 0
    for item in expected_items:
        if any(_contains_normalized(candidate, item) for candidate in observed_items):
            hits += 1
            continue
        if _contains_normalized(fallback_text, item):
            hits += 1
    return round(hits / len(expected_items), 3)


def _overall_score(metrics: dict[str, float]) -> float:
    weighted_total = (
        metrics["title_match"] * 0.2
        + metrics["abstract_token_recall"] * 0.2
        + metrics["heading_hit_rate"] * 0.2
        + metrics["paragraph_hit_rate"] * 0.15
        + metrics["equation_hit_rate"] * 0.15
        + metrics["reference_hit_rate"] * 0.1
    )
    return round(weighted_total, 3)


def _load_gold_record(paper_id: str, gold_path: Path) -> AcquisitionGoldRecord:
    payload = _load_json(gold_path)
    return AcquisitionGoldRecord(
        paper_id=paper_id,
        title=str(payload.get("title", "")),
        abstract=str(payload.get("abstract", "")),
        headings=[str(item) for item in payload.get("headings", [])],
        paragraphs=[str(item) for item in payload.get("paragraphs", [])],
        equations=[str(item) for item in payload.get("equations", [])],
        references=[str(item) for item in payload.get("references", [])],
    )


def load_benchmark_manifest(manifest_path: str | Path) -> list[BenchmarkPaper]:
    resolved_manifest_path = Path(manifest_path).resolve()
    manifest_dir = resolved_manifest_path.parent
    payload = _load_json(resolved_manifest_path)
    papers: list[BenchmarkPaper] = []
    for paper_payload in payload.get("papers", []):
        paper_id = str(paper_payload.get("paper_id", "")).strip()
        if not paper_id:
            continue
        gold_path = (manifest_dir / str(paper_payload["gold"])).resolve()
        providers = [
            ProviderArtifacts(
                name=str(provider_name),
                layout_path=(manifest_dir / str(provider_payload["layout"])).resolve(),
                math_path=((manifest_dir / str(provider_payload["math"])).resolve() if provider_payload.get("math") else None),
            )
            for provider_name, provider_payload in (paper_payload.get("providers", {}) or {}).items()
        ]
        papers.append(BenchmarkPaper(paper_id=paper_id, gold_path=gold_path, providers=providers))
    return papers


def run_acquisition_benchmark(manifest_path: str | Path) -> dict[str, Any]:
    papers = load_benchmark_manifest(manifest_path)
    per_paper_results: list[dict[str, Any]] = []
    aggregate_totals: dict[str, dict[str, float]] = {}

    for paper in papers:
        gold = _load_gold_record(paper.paper_id, paper.gold_path)
        provider_results: list[dict[str, Any]] = []
        for provider in paper.providers:
            observed = _extract_provider_observation(provider.layout_path, provider.math_path)
            metrics = {
                "title_match": float(_contains_normalized(observed["title"], gold.title)),
                "abstract_token_recall": _token_recall(gold.abstract, observed["abstract"]),
                "heading_hit_rate": _list_hit_rate(gold.headings, observed["headings"], observed["full_text"]),
                "paragraph_hit_rate": _list_hit_rate(gold.paragraphs, observed["paragraphs"], observed["full_text"]),
                "equation_hit_rate": _list_hit_rate(gold.equations, observed["equations"], observed["full_text"]),
                "reference_hit_rate": _list_hit_rate(gold.references, observed["references"], observed["full_text"]),
            }
            overall = _overall_score(metrics)
            result = {
                "provider": provider.name,
                "layout_path": str(provider.layout_path),
                "math_path": str(provider.math_path) if provider.math_path is not None else None,
                "metrics": metrics,
                "overall_score": overall,
            }
            provider_results.append(result)

            provider_totals = aggregate_totals.setdefault(provider.name, {"papers": 0, "overall_score_total": 0.0})
            provider_totals["papers"] += 1
            provider_totals["overall_score_total"] += overall

        provider_results.sort(key=lambda item: (-float(item["overall_score"]), str(item["provider"])))
        per_paper_results.append(
            {
                "paper_id": paper.paper_id,
                "gold_path": str(paper.gold_path),
                "providers": provider_results,
            }
        )

    aggregate = [
        {
            "provider": provider_name,
            "papers": int(values["papers"]),
            "avg_overall_score": round(values["overall_score_total"] / max(values["papers"], 1), 3),
        }
        for provider_name, values in aggregate_totals.items()
    ]
    aggregate.sort(key=lambda item: (-float(item["avg_overall_score"]), str(item["provider"])))
    return {
        "manifest_path": str(Path(manifest_path).resolve()),
        "paper_count": len(per_paper_results),
        "papers": per_paper_results,
        "aggregate": aggregate,
    }


__all__ = [
    "BenchmarkPaper",
    "ProviderArtifacts",
    "load_benchmark_manifest",
    "run_acquisition_benchmark",
]
