from __future__ import annotations

import argparse
import json
from typing import Any, Callable

from pipeline.acquisition.trial_promotion import promote_acquisition_trial
from pipeline.corpus_layout import current_layout


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Promote a named acquisition trial bundle into the live canonical_sources sidecars."
    )
    parser.add_argument("paper_id", help="Paper directory id under the configured corpus or project.")
    parser.add_argument(
        "--label",
        default="follow-up",
        help="Trial bundle label under canonical_sources/trials/. Defaults to follow-up.",
    )
    return parser.parse_args()


def run_promote_trial_cli(
    args: argparse.Namespace,
    *,
    promote_trial_fn: Callable[..., dict[str, Any]] = promote_acquisition_trial,
) -> int:
    summary = promote_trial_fn(
        args.paper_id,
        layout=current_layout(),
        label=args.label,
    )
    print(json.dumps(summary, indent=2))
    return 0


def main() -> int:
    return run_promote_trial_cli(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
