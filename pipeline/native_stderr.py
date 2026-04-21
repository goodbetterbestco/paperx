from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path
from threading import Lock
from typing import Any, Callable, TypeVar, cast


T = TypeVar("T")

_NATIVE_STDERR_LOCK = Lock()
_MUPDF_CMS_PROFILE_ERROR = "cmsopenprofilefrommem failed"


def run_with_stderr_label(label: str, fn: Callable[[], T]) -> T:
    result, output, error = _capture_native_stderr(fn)
    _emit_labeled_output(label, output)
    if error is not None:
        raise error.with_traceback(error.__traceback__)
    return result


def open_pdf_with_diagnostics(label: str, pdf_path: str | Path, fitz_module: Any) -> Any:
    source_path = Path(pdf_path)
    result, output, error = _capture_native_stderr(lambda: fitz_module.open(source_path))
    _emit_labeled_output(label, output)
    if error is not None:
        if _is_cms_profile_open_error(error, output):
            raise RuntimeError(
                f"Failed to open source PDF for {label}: {source_path}. "
                "MuPDF reported `cmsOpenProfileFromMem failed`, which indicates malformed embedded color-profile data in the source paper. "
                "Inspect or replace the source PDF; downstream extraction cannot recover from this input."
            ) from error
        raise error.with_traceback(error.__traceback__)
    return result


def _capture_native_stderr(fn: Callable[[], T]) -> tuple[T, str, Exception | None]:
    with _NATIVE_STDERR_LOCK:
        sys.stderr.flush()
        original_stderr_fd = os.dup(2)
        error: Exception | None = None
        result: T | None = None
        with tempfile.TemporaryFile(mode="w+b") as capture:
            try:
                os.dup2(capture.fileno(), 2)
                try:
                    result = fn()
                except Exception as exc:
                    error = exc
            finally:
                sys.stderr.flush()
                os.dup2(original_stderr_fd, 2)
                os.close(original_stderr_fd)
            capture.seek(0)
            output = capture.read().decode("utf-8", errors="replace")
        return cast(T, result), output, error


def _is_cms_profile_open_error(error: Exception, output: str) -> bool:
    combined = f"{error}\n{output}".casefold()
    return _MUPDF_CMS_PROFILE_ERROR in combined


def _emit_labeled_output(label: str, output: str) -> None:
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        print(f"[native-stderr paper={label}] {line}", file=sys.stderr, flush=True)


__all__ = ["open_pdf_with_diagnostics", "run_with_stderr_label"]
