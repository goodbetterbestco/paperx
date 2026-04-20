from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any

from pipeline.acquisition.grobid_policy import grobid_policy_snapshot
from pipeline.acquisition.providers import load_metadata_reference_observation


SPACE_RE = re.compile(r"\s+")
NON_WORD_RE = re.compile(r"[^a-z0-9]+")


@dataclass(frozen=True)
class GrobidGoldRecord:
    paper_id: str
    title: str
    abstract: str
    references: list[str]


@dataclass(frozen=True)
class GrobidTrialPaper:
    paper_id: str
    gold_path: Path
    artifact_path: Path


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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
    return bool(normalized_haystack and normalized_needle and normalized_needle in normalized_haystack)


def _token_recall(expected: str, observed: str) -> float:
    expected_tokens = _normalize_tokens(expected)
    if not expected_tokens:
        return 1.0
    observed_tokens = _normalize_tokens(observed)
    return round(len(expected_tokens & observed_tokens) / len(expected_tokens), 3)


def _list_hit_rate(expected_items: list[str], observed_items: list[str]) -> float:
    if not expected_items:
        return 1.0
    total = 0.0
    for expected in expected_items:
        best_score = max((_token_recall(expected, observed) for observed in observed_items), default=0.0)
        total += best_score
    return round(total / len(expected_items), 3)


def _overall_score(metrics: dict[str, float]) -> float:
    return round(
        metrics["title_match"] * 0.35
        + metrics["abstract_token_recall"] * 0.35
        + metrics["reference_hit_rate"] * 0.3,
        3,
    )


def _load_gold_record(paper_id: str, gold_path: Path) -> GrobidGoldRecord:
    payload = _load_json(gold_path)
    return GrobidGoldRecord(
        paper_id=paper_id,
        title=str(payload.get("title", "")),
        abstract=str(payload.get("abstract", "")),
        references=[str(item) for item in payload.get("references", [])],
    )


def load_grobid_trial_manifest(manifest_path: str | Path) -> list[GrobidTrialPaper]:
    resolved_manifest = Path(manifest_path).resolve()
    manifest_dir = resolved_manifest.parent
    payload = _load_json(resolved_manifest)
    papers: list[GrobidTrialPaper] = []
    for paper_payload in payload.get("papers", []):
        paper_id = str(paper_payload.get("paper_id", "")).strip()
        if not paper_id:
            continue
        papers.append(
            GrobidTrialPaper(
                paper_id=paper_id,
                gold_path=(manifest_dir / str(paper_payload["gold"])).resolve(),
                artifact_path=(manifest_dir / str(paper_payload["grobid_tei"])).resolve(),
            )
        )
    return papers


def run_grobid_trial(manifest_path: str | Path) -> dict[str, Any]:
    papers = load_grobid_trial_manifest(manifest_path)
    per_paper_results: list[dict[str, Any]] = []
    overall_scores: list[float] = []

    for paper in papers:
        gold = _load_gold_record(paper.paper_id, paper.gold_path)
        observed = load_metadata_reference_observation("grobid", paper.artifact_path)
        metrics = {
            "title_match": float(_contains_normalized(observed.title, gold.title)),
            "abstract_token_recall": _token_recall(gold.abstract, observed.abstract),
            "reference_hit_rate": _list_hit_rate(gold.references, observed.references),
        }
        overall_score = _overall_score(metrics)
        overall_scores.append(overall_score)
        per_paper_results.append(
            {
                "paper_id": paper.paper_id,
                "gold_path": str(paper.gold_path),
                "artifact_path": str(paper.artifact_path),
                "provider": observed.provider,
                "observation": observed.to_dict(),
                "metrics": metrics,
                "overall_score": overall_score,
            }
        )

    return {
        "manifest_path": str(Path(manifest_path).resolve()),
        "policy": grobid_policy_snapshot(),
        "paper_count": len(per_paper_results),
        "papers": per_paper_results,
        "aggregate": {
            "provider": "grobid",
            "papers": len(per_paper_results),
            "avg_overall_score": round(sum(overall_scores) / max(len(overall_scores), 1), 3),
        },
    }


__all__ = [
    "GrobidTrialPaper",
    "load_grobid_trial_manifest",
    "run_grobid_trial",
]
