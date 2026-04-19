from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import xml.etree.ElementTree as ET


TEI_NAMESPACE = {"tei": "http://www.tei-c.org/ns/1.0"}


@dataclass(frozen=True)
class MetadataReferenceObservation:
    provider: str
    title: str
    abstract: str
    references: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _collapse_text(text: str) -> str:
    return " ".join(str(text or "").split()).strip()


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _itertext(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return _collapse_text("".join(element.itertext()))


def _parse_grobid_tei(path: Path) -> MetadataReferenceObservation:
    root = ET.fromstring(path.read_text(encoding="utf-8"))
    title = _itertext(root.find(".//tei:titleStmt/tei:title", TEI_NAMESPACE))
    abstract_parts = [
        _itertext(node)
        for node in root.findall(".//tei:profileDesc/tei:abstract//tei:p", TEI_NAMESPACE)
    ]
    if not abstract_parts:
        abstract_parts = [_itertext(root.find(".//tei:profileDesc/tei:abstract", TEI_NAMESPACE))]
    references = []
    for node in root.findall(".//tei:listBibl/tei:biblStruct", TEI_NAMESPACE):
        text = _itertext(node)
        if text:
            references.append(text)
    return MetadataReferenceObservation(
        provider="grobid",
        title=title,
        abstract=_collapse_text(" ".join(part for part in abstract_parts if part)),
        references=references,
    )


def _parse_generic_metadata_json(path: Path) -> MetadataReferenceObservation:
    payload = _load_json(path)
    return MetadataReferenceObservation(
        provider=str(payload.get("provider", "generic")),
        title=_collapse_text(str(payload.get("title", ""))),
        abstract=_collapse_text(str(payload.get("abstract", ""))),
        references=[
            _collapse_text(str(item))
            for item in payload.get("references", [])
            if _collapse_text(str(item))
        ],
    )


def load_metadata_reference_observation(
    provider: str,
    artifact_path: str | Path,
) -> MetadataReferenceObservation:
    resolved_path = Path(artifact_path).resolve()
    normalized_provider = provider.strip().lower()
    if normalized_provider == "grobid":
        observation = _parse_grobid_tei(resolved_path)
        return MetadataReferenceObservation(
            provider="grobid",
            title=observation.title,
            abstract=observation.abstract,
            references=observation.references,
        )
    observation = _parse_generic_metadata_json(resolved_path)
    return MetadataReferenceObservation(
        provider=normalized_provider or observation.provider,
        title=observation.title,
        abstract=observation.abstract,
        references=observation.references,
    )


__all__ = [
    "MetadataReferenceObservation",
    "load_metadata_reference_observation",
]
