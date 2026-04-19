from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess

from pipeline.runtime_paths import runtime_env


ENGINE_ROOT = Path(__file__).resolve().parents[2]


def _resolve_ocrmypdf_command() -> list[str]:
    configured_bin = os.environ.get("PIPELINE_OCRMYPDF_BIN", "").strip()
    if configured_bin:
        return [configured_bin]

    repo_venv_bin = ENGINE_ROOT / ".venv-paperx" / "bin" / "ocrmypdf"
    if repo_venv_bin.exists():
        return [str(repo_venv_bin)]

    path_bin = shutil.which("ocrmypdf")
    if path_bin:
        return [path_bin]

    raise FileNotFoundError(
        "ocrmypdf CLI not found. Install `ocrmypdf`, add it to PATH, or set PIPELINE_OCRMYPDF_BIN."
    )


def run_ocrmypdf(
    input_pdf_path: str | Path,
    output_pdf_path: str | Path,
    *,
    deskew: bool = True,
    force_ocr: bool = False,
    skip_text: bool = True,
    optimize: int = 1,
    resolve_ocrmypdf_command_fn=None,
    subprocess_run=subprocess.run,
    runtime_env_fn=runtime_env,
) -> Path:
    active_resolve_ocrmypdf_command = resolve_ocrmypdf_command_fn or _resolve_ocrmypdf_command
    input_path = Path(input_pdf_path).resolve()
    output_path = Path(output_pdf_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    command = [
        *active_resolve_ocrmypdf_command(),
        "--optimize",
        str(optimize),
    ]
    if deskew:
        command.append("--deskew")
    if force_ocr:
        command.append("--force-ocr")
    elif skip_text:
        command.append("--skip-text")
    command.extend([str(input_path), str(output_path)])
    subprocess_run(command, check=True, env=runtime_env_fn(), capture_output=True, text=True)
    return output_path


__all__ = [
    "run_ocrmypdf",
]
