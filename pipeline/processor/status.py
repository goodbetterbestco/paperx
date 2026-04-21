from __future__ import annotations

from dataclasses import dataclass
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pipeline.corpus_layout import ProjectLayout, current_layout
from pipeline.corpus.metadata import discover_paper_pdf_paths, paper_id_from_pdf_path
from pipeline.runtime_paths import ENGINE_ROOT, runtime_env

ENV_LOCAL_PATH = ENGINE_ROOT / ".env.local"


@dataclass(frozen=True)
class CorpusRuntime:
    layout: ProjectLayout
    batch_dir: Path
    status_path: Path
    report_path: Path


def build_runtime(layout: ProjectLayout | None = None) -> CorpusRuntime:
    active_layout = layout or current_layout()
    return CorpusRuntime(
        layout=active_layout,
        batch_dir=active_layout.project_status_path().parent,
        status_path=active_layout.project_status_path(),
        report_path=active_layout.project_report_path(),
    )


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _env_local_disabled() -> bool:
    raw = os.environ.get("PIPELINE_SKIP_ENV_LOCAL", "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def read_env_local() -> dict[str, str]:
    if _env_local_disabled() or not ENV_LOCAL_PATH.exists():
        return {}
    loaded: dict[str, str] = {}
    for raw_line in ENV_LOCAL_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        loaded[key] = value
    return loaded


def configure_runtime_environment() -> None:
    os.environ.update(runtime_env())
    os.environ.update(read_env_local())


def int_env(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return max(1, int(raw))
    except ValueError:
        return default


def float_env(name: str, default: float) -> float:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return max(0.0, float(raw))
    except ValueError:
        return default


def paper_ids(*, layout: ProjectLayout | None = None) -> list[str]:
    return [paper_id_from_pdf_path(path, layout=layout) for path in discover_paper_pdf_paths(layout=layout)]


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_status(runtime: CorpusRuntime) -> dict[str, Any]:
    if runtime.status_path.exists():
        return json.loads(runtime.status_path.read_text(encoding="utf-8"))
    timestamp = now_iso()
    return {
        "started_at": timestamp,
        "updated_at": timestamp,
        "papers": paper_ids(layout=runtime.layout),
        "runs": [],
        "notes": [],
    }


def save_status(status: dict[str, Any], runtime: CorpusRuntime) -> None:
    status["updated_at"] = now_iso()
    write_json(runtime.status_path, status)


__all__ = [
    "CorpusRuntime",
    "ENV_LOCAL_PATH",
    "build_runtime",
    "configure_runtime_environment",
    "float_env",
    "int_env",
    "load_status",
    "now_iso",
    "paper_ids",
    "read_env_local",
    "save_status",
    "write_json",
]
