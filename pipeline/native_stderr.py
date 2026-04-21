from __future__ import annotations

import os
import sys
import tempfile
from threading import Lock
from typing import Callable, TypeVar


T = TypeVar("T")

_NATIVE_STDERR_LOCK = Lock()


def run_with_stderr_label(label: str, fn: Callable[[], T]) -> T:
    with _NATIVE_STDERR_LOCK:
        sys.stderr.flush()
        original_stderr_fd = os.dup(2)
        with tempfile.TemporaryFile(mode="w+b") as capture:
            try:
                os.dup2(capture.fileno(), 2)
                result = fn()
            except Exception:
                sys.stderr.flush()
                os.dup2(original_stderr_fd, 2)
                os.close(original_stderr_fd)
                capture.seek(0)
                _emit_labeled_output(label, capture.read().decode("utf-8", errors="replace"))
                raise
            sys.stderr.flush()
            os.dup2(original_stderr_fd, 2)
            os.close(original_stderr_fd)
            capture.seek(0)
            _emit_labeled_output(label, capture.read().decode("utf-8", errors="replace"))
            return result


def _emit_labeled_output(label: str, output: str) -> None:
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        print(f"[native-stderr paper={label}] {line}", file=sys.stderr, flush=True)


__all__ = ["run_with_stderr_label"]
