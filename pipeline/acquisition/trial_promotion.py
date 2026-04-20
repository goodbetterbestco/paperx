from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from pipeline.corpus_layout import ProjectLayout
from pipeline.orchestrator.round_runtime import now_iso, write_json
from pipeline.sources.external import (
    acquisition_execution_report_path,
    acquisition_trial_dir,
    external_layout_path,
    external_math_path,
)


PROMOTED_FILENAMES = (
    "acquisition-route.json",
    "source-scorecard.json",
    "layout.json",
    "math.json",
    "acquisition-execution.json",
)


def _load_json_dict(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        return payload
    return {}


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _delete_path(path: Path) -> None:
    if path.exists():
        path.unlink()


def _target_paths(
    paper_id: str,
    *,
    layout: ProjectLayout | None = None,
) -> dict[str, Path]:
    sources_dir = external_layout_path(paper_id, layout=layout).parent
    return {
        "acquisition-route.json": sources_dir / "acquisition-route.json",
        "source-scorecard.json": sources_dir / "source-scorecard.json",
        "layout.json": external_layout_path(paper_id, layout=layout),
        "math.json": external_math_path(paper_id, layout=layout),
        "acquisition-execution.json": acquisition_execution_report_path(paper_id, layout=layout),
    }


def promote_acquisition_trial(
    paper_id: str,
    *,
    layout: ProjectLayout | None = None,
    label: str = "follow-up",
    load_json_dict_impl: Callable[[Path], dict[str, Any]] | None = None,
    write_json_impl: Callable[[Path, Any], None] | None = None,
    write_text_impl: Callable[[Path, str], None] | None = None,
    now_iso_impl: Callable[[], str] | None = None,
) -> dict[str, Any]:
    load_json_dict_impl = load_json_dict_impl or _load_json_dict
    write_json_impl = write_json_impl or write_json
    write_text_impl = write_text_impl or _write_text
    now_iso_impl = now_iso_impl or now_iso

    trial_dir = acquisition_trial_dir(paper_id, layout=layout, label=label)
    if not trial_dir.exists():
        raise FileNotFoundError(f"Missing acquisition trial bundle for {paper_id}: {trial_dir}")

    targets = _target_paths(paper_id, layout=layout)
    sources_dir = targets["layout.json"].parent
    for name in PROMOTED_FILENAMES:
        if not (trial_dir / name).exists():
            raise FileNotFoundError(f"Missing required trial artifact for {paper_id}: {trial_dir / name}")

    backup_dir = trial_dir / "previous-live"
    previous_live_paths: dict[str, str] = {}
    for name, target_path in targets.items():
        if target_path.exists():
            previous_live_paths[name] = str(backup_dir / name)
            write_text_impl(backup_dir / name, target_path.read_text(encoding="utf-8"))

    promotion_payload = {
        "label": label,
        "promoted_at": now_iso_impl(),
        "paper_id": paper_id,
        "trial_dir": str(trial_dir),
        "sources_dir": str(sources_dir),
        "previous_live_paths": previous_live_paths,
    }

    promoted_execution = load_json_dict_impl(trial_dir / "acquisition-execution.json")
    promoted_execution["promotion"] = promotion_payload

    for name, target_path in targets.items():
        if name == "acquisition-execution.json":
            write_json_impl(target_path, promoted_execution)
            continue
        write_text_impl(target_path, (trial_dir / name).read_text(encoding="utf-8"))

    write_json_impl(trial_dir / "promotion.json", promotion_payload)
    return {
        "paper_id": paper_id,
        "label": label,
        "promoted": True,
        "trial_dir": str(trial_dir),
        "sources_dir": str(sources_dir),
        "promotion_path": str(trial_dir / "promotion.json"),
        "previous_live_paths": previous_live_paths,
        "promoted_paths": {name: str(path) for name, path in targets.items()},
    }


def rollback_acquisition_trial(
    paper_id: str,
    *,
    layout: ProjectLayout | None = None,
    label: str = "follow-up",
    load_json_dict_impl: Callable[[Path], dict[str, Any]] | None = None,
    write_json_impl: Callable[[Path, Any], None] | None = None,
    write_text_impl: Callable[[Path, str], None] | None = None,
    delete_path_impl: Callable[[Path], None] | None = None,
    now_iso_impl: Callable[[], str] | None = None,
) -> dict[str, Any]:
    load_json_dict_impl = load_json_dict_impl or _load_json_dict
    write_json_impl = write_json_impl or write_json
    write_text_impl = write_text_impl or _write_text
    delete_path_impl = delete_path_impl or _delete_path
    now_iso_impl = now_iso_impl or now_iso

    trial_dir = acquisition_trial_dir(paper_id, layout=layout, label=label)
    promotion_path = trial_dir / "promotion.json"
    if not promotion_path.exists():
        raise FileNotFoundError(f"Missing promotion record for {paper_id}: {promotion_path}")
    promotion_payload = load_json_dict_impl(promotion_path)
    backup_dir = trial_dir / "previous-live"
    if not backup_dir.exists():
        raise FileNotFoundError(f"Missing previous-live backup for {paper_id}: {backup_dir}")

    targets = _target_paths(paper_id, layout=layout)
    previous_live_paths = {
        str(name): str(path)
        for name, path in dict(promotion_payload.get("previous_live_paths") or {}).items()
        if str(name).strip() and str(path).strip()
    }
    restored_paths: dict[str, str] = {}
    removed_paths: list[str] = []

    for name, target_path in targets.items():
        backup_path = backup_dir / name
        if name in previous_live_paths:
            if not backup_path.exists():
                raise FileNotFoundError(f"Missing backup artifact for {paper_id}: {backup_path}")
            if name == "acquisition-execution.json":
                restored_execution = load_json_dict_impl(backup_path)
                restored_execution["rollback"] = {
                    "label": label,
                    "rolled_back_at": now_iso_impl(),
                    "trial_dir": str(trial_dir),
                    "promotion_path": str(promotion_path),
                }
                write_json_impl(target_path, restored_execution)
            else:
                write_text_impl(target_path, backup_path.read_text(encoding="utf-8"))
            restored_paths[name] = str(target_path)
        else:
            delete_path_impl(target_path)
            removed_paths.append(str(target_path))

    rollback_payload = {
        "label": label,
        "rolled_back_at": now_iso_impl(),
        "paper_id": paper_id,
        "trial_dir": str(trial_dir),
        "sources_dir": str(targets["layout.json"].parent),
        "restored_paths": restored_paths,
        "removed_paths": removed_paths,
    }
    write_json_impl(trial_dir / "rollback.json", rollback_payload)
    return {
        "paper_id": paper_id,
        "label": label,
        "rolled_back": True,
        "trial_dir": str(trial_dir),
        "sources_dir": str(targets["layout.json"].parent),
        "rollback_path": str(trial_dir / "rollback.json"),
        "restored_paths": restored_paths,
        "removed_paths": removed_paths,
    }


__all__ = ["promote_acquisition_trial", "rollback_acquisition_trial"]
