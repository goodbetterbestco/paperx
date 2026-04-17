#!/usr/bin/env python3

from __future__ import annotations

from pipeline.corpus.lexicon_builder import _build_lexicon, main


__all__ = ["_build_lexicon", "main"]


if __name__ == "__main__":
    raise SystemExit(main())
