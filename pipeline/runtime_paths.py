from __future__ import annotations

import os
from pathlib import Path
import tempfile


ENGINE_ROOT = Path(__file__).resolve().parents[1]
ROOT = ENGINE_ROOT
CORPUS_ROOT = ENGINE_ROOT / "corpus"
TMP_DIR = Path(tempfile.gettempdir()).resolve()


def ensure_repo_tmp_dir() -> Path:
    return TMP_DIR


def shared_report_root() -> Path:
    CORPUS_ROOT.mkdir(parents=True, exist_ok=True)
    return CORPUS_ROOT


def shared_report_dir(name: str) -> Path:
    return shared_report_root() / name


def runtime_env(*, extra: dict[str, str] | None = None) -> dict[str, str]:
    env = os.environ.copy()
    if extra:
        env.update(extra)
    return env
