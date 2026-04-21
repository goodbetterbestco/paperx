from __future__ import annotations

import os
import socket
import sys
from urllib.parse import urlparse

from pipeline.processor.status import float_env, int_env
from pipeline.sources.mathpix import MATHPIX_PDF_ENDPOINT


def mathpix_credentials_available() -> bool:
    return bool(os.environ.get("MATHPIX_APP_ID") and os.environ.get("MATHPIX_APP_KEY"))


def assert_mathpix_dns_available(endpoint: str = MATHPIX_PDF_ENDPOINT) -> None:
    host = urlparse(endpoint).hostname or ""
    if not host:
        raise SystemExit(f"Mathpix DNS preflight failed: could not determine hostname from endpoint {endpoint!r}.")
    try:
        socket.getaddrinfo(host, 443)
    except OSError as exc:
        raise SystemExit(
            "Mathpix DNS preflight failed for "
            f"{host}: {exc}. This usually means the corpus pipeline is running inside a "
            "sandboxed environment without external DNS/network access. Rerun the corpus "
            "outside the sandbox or with escalated network access."
        ) from exc


def mathpix_submit_workers() -> int:
    return int_env("STEPVIEW_MATHPIX_SUBMIT_WORKERS", 20)


def mathpix_round_poll_seconds() -> float:
    return float_env("STEPVIEW_MATHPIX_ROUND_POLL_SECONDS", 30.0)


def docling_device() -> str | None:
    configured = os.environ.get("STEPVIEW_DOCLING_DEVICE", "").strip().lower()
    if configured in {"auto", "cpu", "mps", "cuda", "xpu"}:
        return configured
    if sys.platform == "darwin":
        return "mps"
    return None


__all__ = [
    "assert_mathpix_dns_available",
    "docling_device",
    "mathpix_credentials_available",
    "mathpix_round_poll_seconds",
    "mathpix_submit_workers",
]
