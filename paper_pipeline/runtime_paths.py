from __future__ import annotations

import os
from pathlib import Path


ENGINE_ROOT = Path(__file__).resolve().parents[1]
ROOT = ENGINE_ROOT
TMP_DIR = ENGINE_ROOT / "tmp"


def ensure_repo_tmp_dir() -> Path:
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    return TMP_DIR


def runtime_env(*, extra: dict[str, str] | None = None) -> dict[str, str]:
    tmp_dir = ensure_repo_tmp_dir()
    env = os.environ.copy()
    env.setdefault("TMPDIR", str(tmp_dir))
    env.setdefault("TMP", str(tmp_dir))
    env.setdefault("TEMP", str(tmp_dir))
    env.setdefault("XDG_CACHE_HOME", str(tmp_dir / "xdg-cache"))
    env.setdefault("DATALAB_CACHE_DIR", str(tmp_dir / "datalab-cache"))
    if extra:
        env.update(extra)
    return env
