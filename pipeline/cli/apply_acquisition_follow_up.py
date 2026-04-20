from __future__ import annotations

import argparse
import json
from typing import Any, Callable

from pipeline.acquisition.follow_up import apply_acquisition_follow_up
from pipeline.corpus_layout import current_layout


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Materialize a non-destructive acquisition follow-up trial bundle from existing provider sidecars."
    )
    parser.add_argument("paper_id", help="Paper directory id under the configured corpus or project.")
    parser.add_argument(
        "--label",
        default="follow-up",
        help="Trial bundle label written under canonical_sources/trials/. Defaults to follow-up.",
    )
    return parser.parse_args()


def run_apply_follow_up_cli(
    args: argparse.Namespace,
    *,
    apply_follow_up_fn: Callable[..., dict[str, Any]] = apply_acquisition_follow_up,
) -> int:
    summary = apply_follow_up_fn(
        args.paper_id,
        layout=current_layout(),
        label=args.label,
    )
    print(json.dumps(summary, indent=2))
    return 0


def main() -> int:
    return run_apply_follow_up_cli(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
